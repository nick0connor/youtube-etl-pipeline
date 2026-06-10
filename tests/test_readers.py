import pytest
import pandas as pd
from src.readers.json_reader import load_categories
from src.readers.csv_reader import load_csv
from datetime import datetime, timezone
from src.readers.api_reader import fetch_trending, parse_items, load_api

# load_categories

def test_load_categories_returns_dataframe():
    df = load_categories()
    assert isinstance(df, pd.DataFrame)
    
def test_load_categories_has_correct_columns():
    df = load_categories()
    assert list(df.columns) == ["category_id", "category_name", "assignable"]
    
def test_load_categories_has_expected_row_count():
    df = load_categories()
    assert len(df) == 32
    
def test_load_categories_assignable_is_bool():
    df = load_categories()
    assert df['assignable'].dtype == bool
    
def test_load_categories_known_entry():
    df = load_categories()
    comedy = df[df["category_id"] == "34"]
    assert comedy.iloc[0]["category_name"] == "Comedy"
    
# load_csv

def test_load_csv_returns_dataframe():
    df = load_csv()
    assert isinstance(df, pd.DataFrame)
    
def test_load_csv_has_correct_columns():
    df = load_csv()
    expected_cols = [
        "video_id", "trending_date", "title", "channel_title",
        "category_id", "publish_time", "tags", "views", "likes",
        "dislikes", "comment_count", "thumbnail_link",
        "comments_disabled", "ratings_disabled",
        "video_error_or_removed", "description"
    ]
    assert list(df.columns) == expected_cols
    
def test_load_csv_category_id_is_string():
    df = load_csv()
    assert pd.api.types.is_string_dtype(df["category_id"])
   
# Fake YouTube API data to test functions without making direct calls every time 
MOCK_ITEMS = [
    {
        "id": "abc123",
        "snippet": {
            "title": "Test Video",
            "channelId": "chan1",
            "channelTitle": "Test Channel",
            "categoryId": "20",
            "publishedAt": "2026-06-09T16:00:00Z",
            "tags": ["gaming", "test"],
            "description": "A test video"
        },
        "statistics": {
            "viewCount": "1000",
            "likeCount": "500",
            "commentCount": "100"
        }
    },
    {
        "id": "def456",
        "snippet": {
            "title": "Test Video 2",
            "channelId": "chan2",
            "channelTitle": "Test Channel 2",
            "categoryId": "24",
            "publishedAt": "2026-06-09T10:00:00Z",
            "tags": [],
            "description": "Another test video"
        },
        "statistics": {
            "viewCount": "2000",
            "likeCount": "800",
            "commentCount": "200"
        }
    }
]

# --- parse_items ---

def test_parse_items_returns_dataframe():
    df = parse_items(MOCK_ITEMS)
    assert isinstance(df, pd.DataFrame)
    
def test_parse_items_row_count():
    df = parse_items(MOCK_ITEMS)
    assert len(df) == 2
    
def test_parse_items_columns():
    df = parse_items(MOCK_ITEMS)
    expected = [
        "video_id", "snapshot_at", "title", "channel_id",
        "channel_title", "category_id", "published_at",
        "tags", "view_count", "like_count", "comment_count"
    ]
    assert list(df.columns) == expected
    
def test_parse_items_casts_counts_to_int():
    df = parse_items(MOCK_ITEMS)
    assert df["view_count"].dtype == "int64"
    assert df["like_count"].dtype == "int64"
    assert df["comment_count"].dtype == "int64"
    
def test_parse_items_joins_tags_as_pipe_string():
    df = parse_items(MOCK_ITEMS)
    assert df.iloc[0]["tags"] == "gaming|test"
    
def test_parse_items_empty_tags_become_empty_string():
    df = parse_items(MOCK_ITEMS)
    assert df.iloc[1]["tags"] == ""
    
def test_parse_items_snapshot_at_injected():
    time = datetime(2011, 3, 12, 7, 0, 0, tzinfo=timezone.utc)
    df = parse_items(MOCK_ITEMS, time)
    assert df.iloc[0]["snapshot_at"] == time

def test_parse_items_published_at_is_datetime():
    df = parse_items(MOCK_ITEMS)
    assert pd.api.types.is_datetime64_any_dtype(df["published_at"])