import pytest
import pandas as pd
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
from src.main import run_csv_pipeline, run_api_pipeline, run


MOCK_CLEANED = pd.DataFrame({
    "video_id": ["vid1", "vid2"],
    "category_id": ["20", "24"],
    "title": ["Nintendo Direct", "Cyclops Reveal"],
    "publish_time": [datetime(2026, 6, 9, tzinfo=timezone.utc)] * 2,
    "tags": ["nintendo|switch", "marvel|cyclops"],
    "description": ["A description", "Another description"],
    "comments_disabled": [False, False],
    "ratings_disabled": [False, False],
    "video_error_or_removed": [False, False],
    "trending_date": [datetime(2026, 6, 9, tzinfo=timezone.utc)] * 2,
    "channel_title": ["Nintendo", "Marvel"],
    "views": [100000, 200000],
    "likes": [5000, 8000],
    "comment_count": [300, 450]
})

MOCK_CATEGORIES = pd.DataFrame({
    "category_id": ["20", "24"],
    "category_name": ["Gaming", "Entertainment"],
    "assignable": [True, True]
})

MOCK_API_DF = pd.DataFrame({
    "video_id": ["vid3"],
    "snapshot_at": [datetime(2026, 6, 10, tzinfo=timezone.utc)],
    "title": ["Some API Video"],
    "channel_id": ["chan1"],
    "channel_title": ["Some Channel"],
    "category_id": ["20"],
    "published_at": [datetime(2026, 6, 9, tzinfo=timezone.utc)],
    "tags": ["tag1|tag2"],
    "view_count": [100000],
    "like_count": [5000],
    "comment_count": [300]
})


@patch("src.main.load_rejects")
@patch("src.main.load_videos")
@patch("src.main.db_load_categories")
@patch("src.main.load_snapshots")
@patch("src.main.load_categories", return_value=MOCK_CATEGORIES)
@patch("src.main.clean", return_value=(MOCK_CLEANED, pd.DataFrame()))
@patch("src.main.load_csv", return_value=MOCK_CLEANED)
def test_run_csv_pipeline(
    mock_csv, mock_clean, mock_cats, mock_snapshots,
    mock_db_cats, mock_videos, mock_rejects
):
    run_csv_pipeline()
    mock_csv.assert_called_once()
    mock_clean.assert_called_once()
    mock_db_cats.assert_called_once()
    mock_videos.assert_called_once()
    mock_rejects.assert_not_called()


@patch("src.main.load_rejects")
@patch("src.main.load_videos")
@patch("src.main.db_load_categories")
@patch("src.main.load_snapshots")
@patch("src.main.load_categories", return_value=MOCK_CATEGORIES)
@patch("src.main.clean", return_value=(MOCK_CLEANED, pd.DataFrame({"reject_reason": ["bad date"]})))
@patch("src.main.load_csv", return_value=MOCK_CLEANED)
def test_run_csv_pipeline_with_rejects(
    mock_csv, mock_clean, mock_cats, mock_snapshots,
    mock_db_cats, mock_videos, mock_rejects
):
    run_csv_pipeline()
    mock_rejects.assert_called_once()


@patch("src.main.load_snapshots")
@patch("src.main.load_videos")
@patch("src.main.load_channels")
@patch("src.main.load_api", return_value=MOCK_API_DF)
def test_run_api_pipeline(
    mock_api, mock_channels, mock_videos, mock_snapshots
):
    run_api_pipeline()
    mock_api.assert_called_once()
    mock_channels.assert_called_once()
    mock_videos.assert_called_once()
    mock_snapshots.assert_called_once()


@patch("src.main.run_api_pipeline")
@patch("src.main.run_csv_pipeline")
def test_run_calls_both_pipelines(mock_csv, mock_api):
    run()
    mock_csv.assert_called_once()
    mock_api.assert_called_once()