"""Ponto de entrada do sistema. Rode sempre este arquivo: python main.py"""
from pathlib import Path

import flet as ft

from componentes.alertas_ui import avisar_alertas_urgentes
from telas import estoque, inicio, lotes, produtos, validade
from tema import AZUL, AZUL_ESCURO, BRANCO, CINZA, TEXTO_SUAVE, VERMELHO
from utils.erros import registrar_erro

PASTA_ASSETS = Path(__file__).resolve().parent / "assets"

# destino -> função que monta a tela. Para criar uma tela nova, crie o arquivo
# em telas/ com `criar_tela(page, navegar)` e registre aqui e no menu.
TELAS = {
    "inicio": inicio.criar_tela,
    "produtos": produtos.criar_tela,
    "lotes": lotes.criar_tela,
    "estoque": estoque.criar_tela,
    "validade": validade.criar_tela,
}


def main(page: ft.Page):
    page.title = "Mercadinho São José"
    page.bgcolor = CINZA
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.min_width = 800
    page.window.min_height = 600

    area = ft.Container(expand=True, padding=28)
    botoes_menu = {}

    def tela_de_erro(destino):
        return ft.Column(
            controls=[
                ft.Text("Não foi possível abrir esta tela.", size=18,
                        weight=ft.FontWeight.BOLD, color=VERMELHO),
                ft.Text("O erro foi gravado em logs/erros.log. Tente voltar "
                        "ao Início ou reiniciar o sistema.",
                        color=TEXTO_SUAVE, size=13),
            ],
            spacing=8,
        )

    def mostrar(destino):
        """Troca a tela mostrada à direita e destaca o item do menu."""
        for chave, caixa in botoes_menu.items():
            caixa.bgcolor = AZUL if chave == destino else None
        try:
            area.content = TELAS[destino](page, mostrar)
        except Exception as erro:  # uma tela com defeito não derruba o app
            registrar_erro(erro, f"abrir tela '{destino}'")
            area.content = tela_de_erro(destino)
        page.update()

    def item_menu(chave, icone, titulo):
        caixa = ft.Container(
            content=ft.ListTile(
                leading=ft.Icon(icone, color=BRANCO),
                title=ft.Text(titulo, color=BRANCO, size=14),
                on_click=lambda e: mostrar(chave),
            ),
            border_radius=8,
        )
        botoes_menu[chave] = caixa
        return caixa

    menu = ft.Container(
        width=235,
        bgcolor=AZUL_ESCURO,
        padding=18,
        content=ft.Column(
            controls=[
                ft.Container(
                    content=ft.Image(
                        src="logo_sao_jose.png",
                        width=165,
                        height=165,
                        fit=ft.BoxFit.CONTAIN,
                    ),
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Text(
                    "MERCADINHO SÃO JOSÉ",
                    color=BRANCO,
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Divider(color="#52749A"),
                ft.Text("MENU PRINCIPAL", color="#BBD8F5", size=11,
                        weight=ft.FontWeight.BOLD),
                item_menu("inicio", ft.Icons.DASHBOARD_OUTLINED, "Início"),
                item_menu("produtos", ft.Icons.INVENTORY_2_OUTLINED,
                          "Produtos"),
                item_menu("lotes", ft.Icons.LAYERS_OUTLINED, "Lotes"),
                item_menu("estoque", ft.Icons.WAREHOUSE_OUTLINED, "Estoque"),
                item_menu("validade", ft.Icons.CALENDAR_MONTH_OUTLINED,
                          "Validade"),
                ft.Container(expand=True),
                ft.Text("Sistema de Controle de Estoque",
                        color="#BBD8F5", size=10),
            ],
            spacing=10,
            expand=True,
        ),
    )

    page.add(ft.Row(controls=[menu, area], spacing=0, expand=True))
    mostrar("inicio")
    avisar_alertas_urgentes(page, mostrar)


if __name__ == "__main__":
    ft.run(main, assets_dir=str(PASTA_ASSETS))
