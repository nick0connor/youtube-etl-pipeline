import pytest
import pandas as pd
from src.readers.json_reader import load_categories

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