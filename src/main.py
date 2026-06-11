# Completed:
# - Get Kaggle Data
# - Get YouTube API keyx
# - Reader for CSV (Kaggle)
# - Reader for JSON (Kaggle)
# - Reader for API 
# - Tests for CSV functions
# - Tests for JSON functions
# - Tests for API functions
# - Get 100% Coverage for test functions
# - Get PostgreSQL database online
# - Link PostgreSQL to Python
# - Set up schema
# - Create functions to load SQL from pandas
# - Tests for load functions
# - Account for CSV having no channel_id column (removed FK constraint, allowed NULL)
# - Create script to load Kaggle + api data into DB (main.py)

# Things Left to Do:
# - Set up api script to daily refresh
# - Create queries/views for insight info (top growing vids, channels in decline)
# - Get Gemini API key (Potentially OpenAI?)
# - Establish pipeline to LLM for report summary after each run
# - Ensure pytest coverage 80%+ if not already
# - README
# - Set up docker file

import logging
import pandas as pd
from datetime import datetime, timezone

from src.readers.csv_reader import load_csv
from src.readers.json_reader import load_categories
from src.readers.api_reader import load_api
from src.clean import clean
from src.load import (
    load_categories as db_load_categories,
    load_channels,
    load_videos,
    load_snapshots,
    load_rejects
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)

def run_csv_pipeline() -> None:
    log.info("ingest.start source=kaggle_csv")
    
    df_raw = load_csv()
    df_cleaned, df_rejects = clean(df_raw)
    log.info(f"ingest.cleaned source=kaggle_csv valid={len(df_cleaned)} rejected={len(df_rejects)}")

    df_categories = load_categories()
    db_load_categories(df_categories)
    log.info(f"ingest.load source=stg_categories rows={len(df_categories)}")
    
    df_cleaned["channel_id"] = None
    df_videos = df_cleaned[[
        "video_id", "channel_id", "category_id", "title", "publish_time", "tags"
    ]].drop_duplicates(subset="video_id").copy()
    df_videos = df_videos.rename(columns={"publish_time": "published_at"})
    
    load_videos(df_videos)
    log.info(f"ingest.load source=stg_videos rows={len(df_videos)}")
    
    if len(df_rejects) > 0:
        load_rejects(df_rejects, source_name="kaggle_csv")
        log.info(f"ingest.rejects source=kaggle_csv rows={len(df_rejects)}")
        
    log.info("ingest.end source=kaggle_csv status=success")
    
    
def run_api_pipeline() -> None:
    log.info("ingest.start source=youtube_api")
    
    df = load_api()
    log.info(f"ingest.fetched source=youtube_api rows={len(df)}")
    
    df_channels = df[["channel_id", "channel_title"]].drop_duplicates(subset="channel_id").copy()
    load_channels(df_channels)
    log.info(f"ingest.load source=stg_channels rows={len(df_channels)}")
    
    df_videos = df[[
        "video_id", "channel_id", "category_id", "title", "published_at", "tags"
    ]].drop_duplicates(subset="video_id").copy()
    load_videos(df_videos)
    log.info(f"ingest.load source=stg_videos rows={len(df_videos)}")
    
    df_snapshots = df[[
        "video_id", "snapshot_at", "view_count", "like_count", "comment_count"
    ]].copy()
    load_snapshots(df_snapshots)
    log.info(f"ingest.load source=stg_trending_snapshots rows={len(df_snapshots)}")
    
    log.info("ingest.end source=youtube_api status=success")


def run() -> None:
    log.info("Pipeline Starting...")
    start = datetime.now(timezone.utc)
    
    run_csv_pipeline()
    run_api_pipeline()
    
    duration = (datetime.now(timezone.utc) - start).total_seconds()
    log.info(f"Pipeline complete duration: {duration:.2f}s")
    
if __name__ == "__main__": # pragma: no cover
    run()