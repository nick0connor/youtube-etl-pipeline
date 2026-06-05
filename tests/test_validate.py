import pytest
import numpy as np
import pandas as pd
from datetime import datetime
from src.clean import parse_YYDDMM_date, cast_booleans, fill_missing, parse_dates

# parse_YYDDMM_date

def test_parse_YYDDMM_date_valid_1():
    result = parse_YYDDMM_date("17.14.11")
    assert result == datetime(2017, 11, 14)
    
def test_parse_YYDDMM_date_valid_2():
    result = parse_YYDDMM_date("09.12.03")
    assert result == datetime(2009, 3, 12)
    
def test_parse_YYDDMM_date_invalid():
    result = parse_YYDDMM_date("test.string")
    assert result is None
    
def test_parse_YYDDMM_date_empty_string():
    result = parse_YYDDMM_date("")
    assert result is None


# cast_booleans

def test_cast_booleans_converts_correctly():
    df = pd.DataFrame({
        "comments_disabled": ["True", "False"],
        "ratings_disabled": ["False", "True"],
        "video_error_or_removed": ["True", "True"]
    })
    bool_cols = ["comments_disabled", "ratings_disabled", "video_error_or_removed"]
    result = cast_booleans(df, bool_cols)
    assert result["comments_disabled"].to_list() == [True, False]
    assert result["ratings_disabled"].to_list() == [False, True]
    assert result["video_error_or_removed"].to_list() == [True, True]
    
def test_cast_booleans_converts_only_selected_columns():
    df = pd.DataFrame({
        "comments_disabled": ["True", "False"],
        "ratings_disabled": ["False", "True"],
        "video_error_or_removed": ["True", "True"]
    })
    bool_cols = ["comments_disabled", "video_error_or_removed"]
    result = cast_booleans(df, bool_cols)
    assert result["comments_disabled"].to_list() == [True, False]
    assert result["ratings_disabled"].to_list() == ["False", "True"]
    assert result["video_error_or_removed"].to_list() == [True, True]
    
def test_cast_booleans_returns_bool_dtype():
    df = pd.DataFrame({
        "comments_disabled": ["True"],
        "ratings_disabled": ["False"],
        "video_error_or_removed": ["True"]
    })
    bool_cols = ["comments_disabled", "ratings_disabled", "video_error_or_removed"]
    result = cast_booleans(df, bool_cols)
    assert result["comments_disabled"].dtype == bool
    assert result["ratings_disabled"].dtype == bool
    assert result["video_error_or_removed"].dtype == bool
    

# fill_missing

def test_fill_missing_replaces_null_all():
    df = pd.DataFrame({
        "description1": [None, "some text", None],
        "description2": ["more", None, None]
    })
    cols = ["description1", "description2"]
    result = fill_missing(df, cols)
    assert result["description1"].to_list() == ["", "some text", ""]
    assert result["description2"].to_list() == ["more", "", ""]
    
def test_fill_missing_replaces_null_only_selected():
    df = pd.DataFrame({
        "description1": [None, "some text", None],
        "description2": ["more", None, None]
    })
    cols = ["description1"]
    result = fill_missing(df, cols)
    assert result["description1"].to_list() == ["", "some text", ""]
    assert result["description2"].to_list() == ["more", np.nan, np.nan]
    
def test_fill_missing_leaves_valid_columns():
    df = pd.DataFrame({
        "description1": [None, "some text", None],
        "description2": ["Fully", "legitimate", "description"],
        "description3": ["more", None, None]
    })
    cols = ["description1", "description2"]
    result = fill_missing(df, cols)
    assert result["description1"].to_list() == ["", "some text", ""]
    assert result["description2"].to_list() == ["Fully", "legitimate", "description"]
    assert result["description3"].to_list() == ["more", np.nan, np.nan]
    

# parse_dates

def test_parse_dates_valid_rows_pass_through():
    df = pd.DataFrame({
        "trending_date": ["17.14.11", "17.15.11"],
        "publish_time": ["2017-11-13T17:13:01.000Z", "2017-11-14T10:00:00.000Z"]
    })
    cleaned, rejects = parse_dates(df, ["publish_time"], "trending_date")
    assert len(cleaned) == 2
    assert len(rejects) == 0
    
def test_parse_dates_invalid_rows_rejected():
    df = pd.DataFrame({
        "trending_date": ["17.14.11", "bad.data"],
        "publish_time": ["2017-11-13T17:13:01.000Z", "2017-11-14T10:00:00.000Z"]
    })
    cleaned, rejects = parse_dates(df, ["publish_time"], "trending_date")
    assert len(cleaned) == 1
    assert len(rejects) == 1
    
def test_parse_dates_invalid_rows_have_reason():
    df = pd.DataFrame({
        "trending_date": ["bad.data"],
        "publish_time": ["2017-11-13T17:13:01.000Z"]
    })
    _, rejects = parse_dates(df, ["publish_time"], "trending_date")
    assert rejects.iloc[0]["reject_reason"] == "unparseable trending_date"
    
def test_parse_dates_works_no_YYDDMM():
    df = pd.DataFrame({
        "trending_date": ["17.14.11", "17.15.11", "bad.data"],
        "publish_time": ["2017-11-13T17:13:01.000Z", "2017-11-14T10:00:00.000Z", "2018-11-13T17:13:01.000Z"]
    })
    cleaned, rejects = parse_dates(df, ["publish_time"])
    assert len(cleaned) == 3
    assert len(rejects) == 0 
    assert cleaned["trending_date"].to_list() == ["17.14.11", "17.15.11", "bad.data"]

def test_parse_dates_works_datetime_col():
    df = pd.DataFrame({
        "trending_date": ["17.14.11", "17.15.11", "bad.data"],
        "publish_time": ["2017-11-13T17:13:01.000Z", "2017-11-14T10:00:00.000Z", "should be trimmed"]
    })
    cleaned, rejects = parse_dates(df, YYMMDD_col="trending_date")
    assert len(cleaned) == 2
    assert len(rejects) == 1 
    assert cleaned["publish_time"].to_list() == ["2017-11-13T17:13:01.000Z", "2017-11-14T10:00:00.000Z"] 