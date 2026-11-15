import os

import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def conectar():
    """Abre uma conexão com o MySQL usando as variáveis do arquivo .env.

    Nenhuma senha fica escrita no código: ela vem sempre do .env
    (veja o modelo em .env.example).
    """
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "mercado"),
        connection_timeout=5,  # evita o app travar se o MySQL estiver desligado
    )
