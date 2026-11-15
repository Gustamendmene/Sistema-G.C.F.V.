"""Conversões entre o formato da tela (dd/mm/aaaa) e o do banco."""
from datetime import datetime


def converter_data(texto):
    """'13/11/2026' -> date(2026, 11, 13). Levanta ValueError se for inválida."""
    return datetime.strptime(texto.strip(), "%d/%m/%Y").date()


def formatar_data(valor):
    """Mostra datas vindas do banco como dd/mm/aaaa ('-' se vazio)."""
    if valor is None:
        return "-"
    try:
        return valor.strftime("%d/%m/%Y")
    except AttributeError:
        return str(valor)


def data_para_campo(valor):
    """Igual a formatar_data, mas devolve '' (campo vazio) quando não há data."""
    return "" if valor is None else formatar_data(valor)
