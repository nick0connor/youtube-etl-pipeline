from unittest.mock import patch
import psycopg
from src.config import get_connection

def test_get_connection_returns_connection():
    with patch("src.config.psycopg.connect") as mock_connect:
        mock_connect.return_value = psycopg.Connection
        conn = get_connection()
        assert conn is not None
        mock_connect.assert_called_once()