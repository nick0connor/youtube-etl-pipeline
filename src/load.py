import json
import pandas as pd
from datetime import datetime, timezone
from src.config import get_connection

def load_categories(df: pd.DataFrame) -> None:
    # UPSERT: Account for duplicates 
    sql = """
        INSERT INTO stg_categories (category_id, category_name, assignable)
        VALUES (%s, %s, %s)
        ON CONFLICT (category_id) DO UPDATE
        SET category_name = EXCLUDED.category_name,
            assignable    = EXCLUDED.assignable;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            for _, row in df.iterrows():
                cur.execute(sql, (row["category_id"], row["category_name"], row["assignable"]))
        conn.commit()

    
def load_channels(df: pd.DataFrame) -> None:
    # UPSERT: Account for duplicates 
    sql = """
        INSERT INTO stg_channels (channel_id, channel_title)
        VALUES (%s, %s)
        ON CONFLICT (channel_id) DO UPDATE
        SET channel_title = EXCLUDED.channel_title;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            for _, row in df.iterrows():
                cur.execute(sql, (row["channel_id"], row["channel_title"]))
        conn.commit()
    
def load_videos(df: pd.DataFrame) -> None:
    # UPSERT: Account for duplicates 
    sql = """
        INSERT INTO stg_videos (video_id, channel_id, category_id, title, published_at, tags)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (video_id) DO UPDATE
        SET title = EXCLUDED.title,
            tags  = EXCLUDED.tags;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            for _, row in df.iterrows():
                cur.execute(sql, (
                    row["video_id"], 
                    row["channel_id"], 
                    row["category_id"], 
                    row["title"], 
                    row["published_at"], 
                    row["tags"]
                ))
        conn.commit()
    
def load_snapshots(df: pd.DataFrame) -> None:
    sql = """
        INSERT INTO stg_trending_snapshots (video_id, snapshot_at, view_count, like_count, comment_count)
        VALUES (%s, %s, %s, %s, %s);
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            for _, row in df.iterrows():
                cur.execute(sql, (
                    row["video_id"], 
                    row["snapshot_at"], 
                    row["view_count"], 
                    row["like_count"], 
                    row["comment_count"]
                ))
        conn.commit()
    
def load_rejects(rejects: pd.DataFrame, source_name: str) -> None:
    if len(rejects) == 0:
        return
    
    sql = """
        INSERT INTO stg_rejects (source_name, raw_payload, reason, rejected_at)
        VALUES (%s, %s, %s, %s);
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            for _, row in rejects.iterrows():
                cur.execute(sql, (
                    source_name, 
                    json.dumps(row.drop("reject_reason").to_dict(), default=str),
                    row["reject_reason"],
                    datetime.now(timezone.utc)
                ))
        conn.commit()
        
def load_summary(summary_text: str) -> None:
    sql = """
        INSERT INTO daily_summaries (generated_at, summary_text)
        VALUES (%s, %s);
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (datetime.now(timezone.utc), summary_text))
        conn.commit()
    