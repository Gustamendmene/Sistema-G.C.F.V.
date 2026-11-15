"""Validação dos campos do formulário de produto, antes de ir ao banco."""
from decimal import Decimal, InvalidOperation

from utils.datas import converter_data
from utils.erros import ErroValidacao

QUANTIDADE_MINIMA_PADRAO = 5


def _preco(texto, rotulo, obrigatorio):
    if not texto:
        if obrigatorio:
            raise ErroValidacao(f"Informe o {rotulo}.")
        return Decimal("0")
    texto = texto.replace(" ", "")
    if "," in texto:  # 1.234,56 -> 1234.56
        texto = texto.replace(".", "").replace(",", ".")
    try:
        valor = Decimal(texto)
    except InvalidOperation:
        raise ErroValidacao(f"{rotulo.capitalize()} inválido. Exemplo: 25,90.")
    if not valor.is_finite():
        raise ErroValidacao(f"{rotulo.capitalize()} inválido. Exemplo: 25,90.")
    if valor < 0:
        raise ErroValidacao(f"{rotulo.capitalize()} não pode ser negativo.")
    return valor


def _inteiro(texto, rotulo, obrigatorio, padrao=None):
    if not texto:
        if obrigatorio:
            raise ErroValidacao(f"Informe a {rotulo}.")
        return padrao
    try:
        valor = int(texto)
    except ValueError:
        raise ErroValidacao(f"{rotulo.capitalize()} deve ser um número inteiro.")
    if valor < 0:
        raise ErroValidacao(f"{rotulo.capitalize()} não pode ser negativa.")
    return valor


def _data(texto, rotulo):
    if not texto:
        raise ErroValidacao(f"Informe a data de {rotulo}.")
    try:
        return converter_data(texto)
    except ValueError:
        raise ErroValidacao(
            f"Data de {rotulo} inválida. Use o formato dd/mm/aaaa.")


def validar_produto(valores):
    """Recebe os textos dos campos (dict) e devolve os dados prontos para o banco.

    As chaves do dicionário devolvido têm o mesmo nome dos parâmetros de
    inserir_produto() / atualizar_produto(), então dá para usar `**dados`.
    Levanta ErroValidacao com uma mensagem clara se algo estiver errado.
    """
    if not valores["nome"]:
        raise ErroValidacao("Informe o nome do produto.")

    entrega = _data(valores["data_entrega"], "entrega")
    validade = _data(valores["data_validade"], "validade")
    if validade < entrega:
        raise ErroValidacao(
            "A validade não pode ser anterior à data de entrega.")

    return {
        "nome": valores["nome"],
        "categoria": valores["categoria"],
        "marca": valores["marca"],
        "codigo_barras": valores["codigo_barras"] or None,  # vazio vira NULL
        "fornecedor": valores["fornecedor"],
        "preco_custo": _preco(valores["preco_custo"], "preço de custo", False),
        "preco_venda": _preco(valores["preco_venda"], "preço de venda", True),
        "data_entrega": entrega,
        "data_validade": validade,
        "quantidade": _inteiro(valores["quantidade"], "quantidade", True),
        "quantidade_minima": _inteiro(
            valores["quantidade_minima"], "quantidade mínima", False,
            QUANTIDADE_MINIMA_PADRAO),
        "lote": valores["lote"],
        "localizacao": valores["localizacao"],
    }
