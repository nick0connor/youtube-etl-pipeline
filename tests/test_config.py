from unittest.mock import MagicMock, patch
import psycopg
from src.config import get_connection, get_gemini_client

def test_get_connection_returns_connection():
    with patch("src.config.psycopg.connect") as mock_connect:
        mock_connect.return_value = psycopg.Connection
        conn = get_connection()
        assert conn is not None
        mock_connect.assert_called_once()
        
@patch("src.config.genai.Client")       
def test_get_gemini_client_returns_client(mock_client):
    mock_client.return_value = MagicMock()
    client = get_gemini_client()
    assert client is not None
    mock_client.assert_called_once()