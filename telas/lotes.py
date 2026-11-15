"""Tela de lotes (somente consulta)."""
from componentes.listagem import tela_lista
from funcoes.estoque import listar_lotes
from utils.datas import formatar_data


def _linhas():
    return [
        (lote or "-", nome, formatar_data(validade), qtd, local or "-")
        for lote, nome, validade, qtd, local in listar_lotes()
    ]


def criar_tela(page, navegar):
    return tela_lista(
        page, navegar,
        "Lotes", "Lotes registrados, com validade e quantidade.",
        ["Lote", "Produto", "Validade", "Quantidade", "Local"],
        _linhas,
        "Nenhum lote registrado ainda. Cadastre um produto na tela Produtos.",
    )
