"""Regras dos alertas de validade e estoque (sem interface).

Os dados vêm da view `alerta_estoque` do MySQL (via funcoes/estoque.py).
Aqui eles são transformados em objetos `Alerta`, ordenados por gravidade
e guardados em um cache curto para o sino não consultar o banco a cada clique.
"""
import time
from dataclasses import dataclass

from funcoes.estoque import listar_alertas
from utils.erros import mensagem_amigavel, registrar_erro

# Tipos devolvidos pela view alerta_estoque
VENCIDO = "VENCIDO"
PROXIMO = "PRÓXIMO DO VENCIMENTO"
BAIXO = "ESTOQUE BAIXO"

DIAS_URGENTE = 3          # até quantos dias o "próximo do vencimento" vira URGENTE
SEGUNDOS_EM_CACHE = 30    # validade do cache usado pelo sino do cabeçalho

_ORDEM = {VENCIDO: 0, PROXIMO: 1, BAIXO: 2}


@dataclass(frozen=True)
class Alerta:
    id_produto: int
    nome: str
    validade: object      # date
    dias: object          # int (negativo = já venceu) ou None
    quantidade: int
    minimo: int
    tipo: str

    @property
    def urgente(self):
        """Vencido, ou vencendo em até DIAS_URGENTE dias."""
        if self.tipo == VENCIDO:
            return True
        return (self.tipo == PROXIMO and self.dias is not None
                and self.dias <= DIAS_URGENTE)

    @property
    def rotulo(self):
        """Texto curto para a etiqueta colorida."""
        if self.tipo == VENCIDO:
            return "VENCIDO"
        if self.tipo == PROXIMO:
            if self.dias == 0:
                return "VENCE HOJE"
            return "URGENTE" if self.urgente else "A VENCER"
        if self.tipo == BAIXO:
            return "ESTOQUE BAIXO"
        return self.tipo or "-"

    @property
    def prazo(self):
        if self.dias is None:
            return "-"
        if self.dias < 0:
            return f"venceu há {-self.dias} dia(s)"
        if self.dias == 0:
            return "vence hoje"
        if self.dias == 1:
            return "vence amanhã"
        return f"vence em {self.dias} dias"

    @property
    def descricao(self):
        if self.tipo == BAIXO:
            return (f"{self.nome}: estoque baixo "
                    f"({self.quantidade} em estoque, mínimo {self.minimo})")
        return f"{self.nome}: {self.prazo}"


@dataclass
class ResultadoAlertas:
    alertas: list
    erro: str = ""   # mensagem amigável se o banco falhou

    def por_tipo(self, tipo):
        return [a for a in self.alertas if a.tipo == tipo]

    @property
    def urgentes(self):
        return [a for a in self.alertas if a.urgente]


def _converter(linha):
    id_p, nome, validade, dias, qtd, minimo, tipo = linha
    return Alerta(id_p, nome, validade,
                  None if dias is None else int(dias), qtd, minimo, tipo)


def obter_alertas():
    """Consulta o banco; ordena por gravidade (vencidos primeiro) e depois por prazo."""
    alertas = [_converter(linha) for linha in listar_alertas()]
    alertas.sort(key=lambda a: (_ORDEM.get(a.tipo, 9),
                                a.dias if a.dias is not None else 10**6,
                                a.nome))
    return alertas


_cache = {"quando": 0.0, "resultado": None}


def carregar_alertas(forcar=False):
    """Devolve um ResultadoAlertas (nunca levanta exceção).

    Usa o cache por 30 s, a menos que `forcar=True`. Se o banco falhar, o erro
    é gravado no log e vem em `resultado.erro` (e também fica em cache, para
    não travar cada tela esperando o MySQL desligado).
    """
    agora = time.monotonic()
    em_cache = _cache["resultado"]
    if (not forcar and em_cache is not None
            and agora - _cache["quando"] < SEGUNDOS_EM_CACHE):
        return em_cache
    try:
        resultado = ResultadoAlertas(obter_alertas())
    except Exception as erro:
        registrar_erro(erro, "carregar alertas")
        resultado = ResultadoAlertas([], mensagem_amigavel(erro))
    _cache["quando"] = time.monotonic()
    _cache["resultado"] = resultado
    return resultado


def invalidar_cache():
    """Chame depois de cadastrar, editar ou excluir produtos."""
    _cache["resultado"] = None
