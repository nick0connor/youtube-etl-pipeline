import pytest
import pandas as pd
from src.readers.json_reader import load_categories
from src.readers.csv_reader import load_csv

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