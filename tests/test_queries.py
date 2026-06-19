import pytest
from unittest.mock import MagicMock, patch
from src.queries import load_query, run_query

def test_load_query_reads_real_file():
    sql = load_query('video_velocity')
    assert "SELECT" in sql
    assert "FROM snapshot_deltas" in sql
    
def test_load_query_raises_on_missing_file():
    with pytest.raises(FileExistsError):
        load_query("not_real_file")

@patch("src.queries.get_connection")
def test_run_query_returns_columns_and_rows(mock_conn):
    mock_cursor = MagicMock()
    mock_cursor.description = [("category_name",), ("video_count",)]
    mock_cursor.fetchall.return_value = [("Gaming", 5), ("Music", 2)]
    mock_conn.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor # lol
    
    columns, rows = run_query("category_breakdown")
    assert columns == ["category_name", "video_count"]
    assert rows == [("Gaming", 5), ("Music", 2)]