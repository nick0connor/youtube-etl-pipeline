# The single place in the project that can connect to db

import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

def get_connection() -> psycopg.Connection:
    """
    Returns:
        psycopg.Connection: Live connection using credentials from .env
    """
    return psycopg.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USERNAME"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )
    
if __name__ == "__main__":  # pragma: no cover
    conn = get_connection()
    print("Connection successful:", conn)
    conn.close()