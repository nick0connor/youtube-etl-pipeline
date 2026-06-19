# The single place in the project that can connect to db

import os
import psycopg
from google import genai
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

def get_gemini_client() -> genai.Client:
    """
    Returns:
        genai.Client: Configured Gemini client using the API key from .env
    """
    api_key = os.getenv("GEMINI_API_KEY")
    return genai.Client(api_key=api_key)
    
if __name__ == "__main__":  # pragma: no cover
    conn = get_connection()
    print("Connection successful:", conn)
    conn.close()
    print()
    client = get_gemini_client()
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Explain how AI works in a few words",
    )
    print(response.text)
