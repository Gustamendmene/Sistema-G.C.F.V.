"""Tela de estoque (somente consulta)."""
from componentes.listagem import tela_lista
from componentes.ui import etiqueta
from funcoes.estoque import listar_estoque
from tema import LARANJA, VERDE
from utils.datas import formatar_data


def _linhas():
    linhas = []
    for nome, qtd, minimo, atualizado in listar_estoque():
        if qtd <= minimo:
            situacao = etiqueta("ESTOQUE BAIXO", LARANJA)
        else:
            situacao = etiqueta("OK", VERDE)
        linhas.append((nome, qtd, minimo, situacao, formatar_data(atualizado)))
    return linhas


def criar_tela(page, navegar):
    return tela_lista(
        page, navegar,
        "Estoque", "Quantidade atual de cada produto e o mínimo desejado.",
        ["Produto", "Quantidade", "Mínimo", "Situação", "Atualizado em"],
        _linhas,
        "O estoque está vazio. Cadastre um produto na tela Produtos.",
    )
