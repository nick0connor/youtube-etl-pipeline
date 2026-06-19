import json
import pandas as pd
import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch, call
from src.load import load_categories, load_channels, load_videos, load_snapshots, load_rejects, load_summary

MOCK_CATEGORIES = pd.DataFrame({
    "category_id": ["20", "24"],
    "category_name": ["Gaming", "Entertainment"],
    "assignable": [True, True]
})

MOCK_CHANNELS = pd.DataFrame({
    "channel_id": ["chan1", "chan2"],
    "channel_title": ["The Nintendo Guy", "Marvel Maniacs"]
})

MOCK_VIDEOS = pd.DataFrame({
    "video_id": ["vid1", "vid2"],
    "channel_id": ["chan1", "chan2"],
    "category_id": ["20", "24"],
    "title": ["Nintendo Direct Reaction: BEST ONE YET????", "How It Would Really Go: Dr. Strange Meets Spiderman"],
    "published_at": [datetime(2026, 6, 9, tzinfo=timezone.utc)] * 2,
    "tags": ["nintendo|switch|direct|reaction", "marvel|drstrange|spiderman"]
})

MOCK_SNAPSHOTS = pd.DataFrame({
    "video_id": ["vid1", "vid2"],
    "snapshot_at": [datetime(2026, 6, 10, tzinfo=timezone.utc)] * 2,
    "view_count": [4500000, 1600000],
    "like_count": [130000, 74000],
    "comment_count": [3000, 6000]
})

MOCK_REJECTS = pd.DataFrame({
    "video_id": ["bad1"],
    "trending_date": ["not-a-date"],
    "reject_reason": ["unparseable trending_date"]
})

# How to test SQL calls:
# - Mock the connection
# - Run the function
# - Assert that execute was called once per row
#
# Also need to check an empty reject df will not
# touch the database at all

@patch("src.load.get_connection")
def test_load_categories_executes_for_each_row(mock_conn):
    mock_cursor = MagicMock()
    mock_conn.return_value.__enter__ = MagicMock(return_value=MagicMock(
        cursor = MagicMock(return_value=MagicMock(
            __enter__ = MagicMock(return_value=mock_cursor),
            __exit__ = MagicMock(return_value=False)
        ))
    ))
    mock_conn.return_value.__exit__ = MagicMock(return_value=False)
    load_categories(MOCK_CATEGORIES)
    assert mock_cursor.execute.call_count == len(MOCK_CATEGORIES)
    
@patch("src.load.get_connection")
def test_load_channels_executes_for_each_row(mock_conn):
    mock_cursor = MagicMock()
    mock_conn.return_value.__enter__ = MagicMock(return_value=MagicMock(
        cursor = MagicMock(return_value=MagicMock(
            __enter__ = MagicMock(return_value=mock_cursor),
            __exit__ = MagicMock(return_value=False)
        ))
    ))
    mock_conn.return_value.__exit__ = MagicMock(return_value=False)
    load_channels(MOCK_CHANNELS)
    assert mock_cursor.execute.call_count == len(MOCK_CHANNELS)
    
@patch("src.load.get_connection")
def test_load_videos_executes_for_each_row(mock_conn):
    mock_cursor = MagicMock()
    mock_conn.return_value.__enter__ = MagicMock(return_value=MagicMock(
        cursor=MagicMock(return_value=MagicMock(
            __enter__=MagicMock(return_value=mock_cursor),
            __exit__=MagicMock(return_value=False)
        ))
    ))
    mock_conn.return_value.__exit__ = MagicMock(return_value=False)
    load_videos(MOCK_VIDEOS)
    assert mock_cursor.execute.call_count == len(MOCK_VIDEOS)
    
@patch("src.load.get_connection")
def test_load_snapshots_executes_for_each_row(mock_conn):
    mock_cursor = MagicMock()
    mock_conn.return_value.__enter__ = MagicMock(return_value=MagicMock(
        cursor=MagicMock(return_value=MagicMock(
            __enter__=MagicMock(return_value=mock_cursor),
            __exit__=MagicMock(return_value=False)
        ))
    ))
    mock_conn.return_value.__exit__ = MagicMock(return_value=False)
    load_snapshots(MOCK_SNAPSHOTS)
    assert mock_cursor.execute.call_count == len(MOCK_SNAPSHOTS)
    
@patch("src.load.get_connection")
def test_load_rejects_executes_for_each_row(mock_conn):
    mock_cursor = MagicMock()
    mock_conn.return_value.__enter__ = MagicMock(return_value=MagicMock(
        cursor=MagicMock(return_value=MagicMock(
            __enter__=MagicMock(return_value=mock_cursor),
            __exit__=MagicMock(return_value=False)
        ))
    ))
    mock_conn.return_value.__exit__ = MagicMock(return_value=False)
    load_rejects(MOCK_REJECTS, source_name="test_source")
    assert mock_cursor.execute.call_count == len(MOCK_REJECTS)
     
def test_load_rejects_skips_empty_dataframe():
    empty = pd.DataFrame(columns=["video_id", "reject_reason"])
    with patch("src.load.get_connection") as mock_conn:
        load_rejects(empty, source_name="test_source")
        mock_conn.assert_not_called()
        
        
@patch("src.load.get_connection")
def test_load_summary_executes_insert(mock_conn):
    mock_cursor = MagicMock()
    mock_conn.return_value.__enter__ = MagicMock(return_value=MagicMock(
        cursor=MagicMock(return_value=MagicMock(
            __enter__=MagicMock(return_value=mock_cursor),
            __exit__=MagicMock(return_value=False)
        ))
    ))
    mock_conn.return_value.__exit__ = MagicMock(return_value=False)
    load_summary("This is a test summary.")
    mock_cursor.execute.assert_called_once()