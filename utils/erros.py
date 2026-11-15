"""Tratamento centralizado de erros.

- registrar_erro(): grava o erro completo (com traceback) em logs/erros.log
- mensagem_amigavel(): transforma qualquer erro numa frase clara para a tela
"""
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from mysql.connector import errors as erros_mysql

PASTA_LOGS = Path(__file__).resolve().parent.parent / "logs"


class ErroValidacao(Exception):
    """Erro de preenchimento de formulário (a mensagem já é para o usuário)."""


_logger = None


def _obter_logger():
    global _logger
    if _logger is None:
        _logger = logging.getLogger("gcfv")
        _logger.setLevel(logging.ERROR)
        try:
            PASTA_LOGS.mkdir(exist_ok=True)
            manipulador = RotatingFileHandler(
                PASTA_LOGS / "erros.log", maxBytes=500_000,
                backupCount=3, encoding="utf-8",
            )
            manipulador.setFormatter(
                logging.Formatter("%(asctime)s | %(message)s"))
            _logger.addHandler(manipulador)
        except OSError:
            _logger.addHandler(logging.StreamHandler())
    return _logger


def registrar_erro(erro, contexto=""):
    """Grava o erro no log. `contexto` diz onde aconteceu (ex.: 'salvar produto')."""
    _obter_logger().error(contexto, exc_info=erro)


MENSAGENS_MYSQL = {
    1045: "Usuário ou senha do MySQL incorretos. Confira o arquivo .env.",
    1049: "O banco de dados não existe. Confira o DB_NAME no arquivo .env.",
    1054: "Uma coluna esperada não existe no banco. O script SQL está atualizado?",
    1146: "Uma tabela ou view não existe no banco. Rode o script SQL de criação.",
    1451: "Não é possível excluir: há registros ligados a este item.",
    1452: "O registro depende de outro que não existe.",
    2003: "Não foi possível conectar ao MySQL. Ele está ligado? Confira o DB_HOST no .env.",
    2005: "O endereço do MySQL (DB_HOST) não foi encontrado.",
}


def mensagem_amigavel(erro):
    """Devolve um texto curto e claro para mostrar ao usuário."""
    if isinstance(erro, ErroValidacao):
        return str(erro)
    if isinstance(erro, erros_mysql.Error):
        codigo = getattr(erro, "errno", None)
        if codigo == 1062:
            if "codigo_barras" in str(erro):
                return "Já existe um produto com esse código de barras."
            return "Já existe um registro com esse valor único."
        if codigo in MENSAGENS_MYSQL:
            return MENSAGENS_MYSQL[codigo]
        return "Erro no banco de dados. Os detalhes foram gravados em logs/erros.log."
    return "Ocorreu um erro inesperado. Os detalhes foram gravados em logs/erros.log."
