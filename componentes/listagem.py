"""Tela padrão de consulta (cabeçalho + tabela), usada por Lotes e Estoque."""
import flet as ft

from componentes.alertas_ui import Sino
from componentes.ui import cabecalho, montar_tabela, painel
from tema import LINHA, TEXTO_SUAVE, VERMELHO
from utils.erros import mensagem_amigavel, registrar_erro


def tela_lista(page, navegar, titulo, subtitulo, titulos, buscar,
               texto_vazio):
    """`buscar` é uma função que devolve as linhas já prontas para a tabela."""
    erro_banco = ""
    linhas = []
    try:
        linhas = buscar()
    except Exception as erro:
        registrar_erro(erro, f"carregar tela '{titulo}'")
        erro_banco = mensagem_amigavel(erro)

    controles = [
        cabecalho(titulo, subtitulo, Sino(page, navegar)),
        ft.Divider(color=LINHA),
    ]
    if erro_banco:
        controles.append(ft.Text(erro_banco, color=VERMELHO, size=13))
    elif not linhas:
        controles.append(ft.Text(texto_vazio, color=TEXTO_SUAVE, size=13))
    else:
        controles.append(painel(montar_tabela(titulos, linhas)))

    return ft.Column(controls=controles, spacing=16,
                     scroll=ft.ScrollMode.AUTO, expand=True)
