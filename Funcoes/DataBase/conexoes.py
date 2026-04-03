import psycopg2
from Funcoes.DataBase.configuracoes import DB_CONFIG

def get_connection():
    return psycopg2.connect(**DB_CONFIG)