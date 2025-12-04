import sqlite3
import os

DB_PATH = "./storage/database.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Cria a tabela de colaboradores se ainda não existir.
    """
    if not os.path.exists("storage"):
        os.makedirs("storage")
    if not os.path.exists(DB_PATH):
        print("Criando novo banco em storage/database.db...")
    else:
        print("Banco já existe, usando normalmente.")

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS colaboradores (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            saldo_folgas_dias REAL NOT NULL DEFAULT 0,
            cargo TEXT NOT NULL,
            endereco TEXT NOT NULL,
            folgas_solicitadas_dias INTEGER NOT NULL DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()