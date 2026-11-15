"""Controle de validade: todos os alertas, com filtro por tipo."""
import flet as ft

from componentes.alertas_ui import Sino, cor_do_alerta
from componentes.ui import cabecalho, etiqueta, montar_tabela, painel
from funcoes.alertas import BAIXO, DIAS_URGENTE, PROXIMO, VENCIDO, carregar_alertas
from tema import AZUL, BRANCO, LINHA, TEXTO_SUAVE, VERMELHO
from utils.datas import formatar_data

TITULOS = ["ID", "Produto", "Validade", "Prazo", "Quantidade", "Mínimo",
           "Alerta"]

# (chave do filtro, texto do botão, tipo da view; None = todos)
FILTROS = [
    ("todos", "Todos", None),
    ("vencidos", "Vencidos", VENCIDO),
    ("proximos", "Próximos do vencimento", PROXIMO),
    ("baixo", "Estoque baixo", BAIXO),
]


def _linha(a):
    prazo = ft.Text(a.prazo, color=VERMELHO if a.urgente else None,
                    weight=ft.FontWeight.BOLD if a.urgente else None)
    return (a.id_produto, a.nome, formatar_data(a.validade), prazo,
            a.quantidade, a.minimo, etiqueta(a.rotulo, cor_do_alerta(a)))


def criar_tela(page, navegar):
    sino = Sino(page, navegar)
    resultado = carregar_alertas(forcar=True)
    sino.atualizar()
    estado = {"filtro": "todos"}

    linha_filtros = ft.Row(wrap=True, spacing=8, run_spacing=8)
    area_tabela = ft.Container()

    def contagem(tipo):
        return len(resultado.alertas if tipo is None
                   else resultado.por_tipo(tipo))

    def desenhar():
        linha_filtros.controls = []
        for chave, texto, tipo in FILTROS:
            rotulo = f"{texto} ({contagem(tipo)})"
            if chave == estado["filtro"]:
                botao = ft.Button(rotulo, style=ft.ButtonStyle(
                    bgcolor=AZUL, color=BRANCO))
            else:
                botao = ft.OutlinedButton(
                    rotulo, on_click=lambda e, c=chave: escolher(c))
            linha_filtros.controls.append(botao)

        tipo = next(t for c, _, t in FILTROS if c == estado["filtro"])
        selecionados = (resultado.alertas if tipo is None
                        else resultado.por_tipo(tipo))
        if resultado.erro:
            area_tabela.content = ft.Text(resultado.erro, color=VERMELHO,
                                          size=13)
        elif not selecionados:
            area_tabela.content = ft.Text(
                "Nenhum alerta no momento. Tudo dentro da validade e do "
                "estoque mínimo." if tipo is None
                else "Nenhum alerta deste tipo.",
                color=TEXTO_SUAVE, size=13)
        else:
            area_tabela.content = painel(montar_tabela(
                TITULOS, [_linha(a) for a in selecionados]))

    def escolher(chave):
        estado["filtro"] = chave
        desenhar()
        page.update()

    desenhar()
    return ft.Column(
        controls=[
            cabecalho(
                "Controle de validade",
                "Vencidos, vencendo em até 7 dias (urgente: até "
                f"{DIAS_URGENTE} dias) e estoque baixo.", sino),
            ft.Divider(color=LINHA),
            linha_filtros,
            area_tabela,
        ],
        spacing=16, scroll=ft.ScrollMode.AUTO, expand=True,
    )
