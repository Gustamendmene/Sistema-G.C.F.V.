"""Peças de interface reutilizadas por várias telas."""
import inspect

import flet as ft

from tema import AZUL_ESCURO, BRANCO, TEXTO_SUAVE
from utils.erros import registrar_erro


def etiqueta(texto, cor):
    return ft.Container(
        content=ft.Text(texto, color=BRANCO, size=12,
                        weight=ft.FontWeight.BOLD),
        bgcolor=cor,
        padding=6,
        border_radius=6,
    )


def criar_cartao(titulo, valor, icone, cor):
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(icone, color=cor, size=28),
                ft.Text(titulo, size=13, color=TEXTO_SUAVE),
                ft.Text(str(valor), size=26, weight=ft.FontWeight.BOLD,
                        color=AZUL_ESCURO),
            ],
            spacing=8,
        ),
        bgcolor=BRANCO,
        padding=18,
        border_radius=12,
        expand=True,
    )


def titulo_coluna(texto):
    return ft.DataColumn(
        ft.Text(texto, weight=ft.FontWeight.BOLD, color=AZUL_ESCURO))


def celula(conteudo):
    """Célula de tabela: aceita texto ou um controle (botão, etiqueta...)."""
    if isinstance(conteudo, ft.Control):
        return ft.DataCell(conteudo)
    return ft.DataCell(ft.Text(str(conteudo)))


def montar_tabela(titulos, linhas):
    """Tabela só de leitura. Cada célula pode ser texto ou um controle."""
    return ft.DataTable(
        columns=[titulo_coluna(t) for t in titulos],
        rows=[ft.DataRow(cells=[celula(c) for c in linha])
              for linha in linhas],
        column_spacing=28,
    )


def painel(tabela):
    """Caixa branca com rolagem horizontal para tabelas largas."""
    return ft.Container(
        content=ft.Row(controls=[tabela], scroll=ft.ScrollMode.AUTO),
        bgcolor=BRANCO,
        padding=12,
        border_radius=12,
    )


def cabecalho(titulo, subtitulo, sino):
    """Título da tela + sino de alertas (veja componentes/alertas_ui.py)."""
    return ft.Row(
        controls=[
            ft.Column(
                controls=[
                    ft.Text(titulo, size=25, weight=ft.FontWeight.BOLD,
                            color=AZUL_ESCURO),
                    ft.Text(subtitulo, color=TEXTO_SUAVE, size=13),
                ],
                spacing=4,
                expand=True,
            ),
            sino.controle,
        ],
    )


def abrir_dialogo(page, dialogo):
    """Abre um diálogo (compatível com versões novas e antigas do Flet)."""
    if hasattr(page, "show_dialog"):
        page.show_dialog(dialogo)
    else:
        page.open(dialogo)


def fechar_dialogo(page, dialogo):
    if hasattr(page, "pop_dialog"):
        page.pop_dialog()
    else:
        page.close(dialogo)


def rolar_ao_topo(page, coluna):
    """Rola a coluna até o topo. Nunca derruba o app se não for possível."""
    try:
        resultado = coluna.scroll_to(offset=0, duration=300)
        if inspect.isawaitable(resultado):  # versões novas do Flet: async
            async def _aguardar():
                await resultado
            page.run_task(_aguardar)
    except Exception as erro:
        registrar_erro(erro, "rolar ao topo")
