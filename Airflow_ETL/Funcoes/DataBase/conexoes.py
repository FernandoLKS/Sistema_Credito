import psycopg2

DB_CONFIG = {
    "dbname": "credito_data",
    "user": "postgres",
    "password": "postgres",
    "host": "host.docker.internal",
    "port": "5433"
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def executar_sql(query, params=None, fetch=True, many=False):
    conn = None
    resultado = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        if many and params:
            cursor.executemany(query, params)
        elif params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        if fetch:
            resultado = cursor.fetchall()
        else:
            conn.commit()

        cursor.close()
    except Exception as e:
        print(f"Erro ao executar SQL: {e}")
    finally:
        if conn:
            conn.close()
    return resultado