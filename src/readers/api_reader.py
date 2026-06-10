import os
import pandas as pd
from datetime import datetime, timezone
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()

def get_youtube_client():
    api_key = os.getenv("YOUTUBE_API_KEY")
    return build("youtube", "v3", developerKey=api_key)

def fetch_trending(youtube, region_code: str = "US", max_results: int = 200, page_size: int = 50) -> list[dict]:
    """
    Fetch trending videos from the YouTube API with pagination

    Args:
        youtube: API object
        region_code (str, optional): Country code for trending page. Defaults to "US".
        max_results (int, optional): Defaults to 200.
        page_size (int, optional): Defaults to 50.

    Returns:
        list[dict]: Raw item dicts from API
    """
    items = []
    next_page_token = None
    
    while len(items) < max_results:
        batch_size = min(page_size, max_results - len(items))
        
        response = youtube.videos().list(
            part="snippet,statistics",
            chart="mostPopular",
            regionCode=region_code,
            maxResults=batch_size,
            pageToken=next_page_token
        ).execute()
        
        items.extend(response.get("items", []))
        next_page_token = response.get("nextPageToken")
        
        if not next_page_token:
            break
        
    return items

def parse_items(items: list[dict], snapshot_at: datetime = None) -> pd.DataFrame:
    """
    Parse raw API response items into a flat DataFrame

    Args:
        items (list[dict]): Raw API data
        snapshot_at (datetime, optional): When data was collected. Defaults to datetime.now().

    Returns:
        pd.DataFrame: DataFrame version of API response data
    """
    if snapshot_at is None:
        snapshot_at = datetime.now(timezone.utc)
        
    records = []
    for item in items:
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        
        records.append({
            "video_id":      item["id"],
            "snapshot_at":   snapshot_at,
            "title":         snippet.get("title"),
            "channel_id":    snippet.get("channelId"),
            "channel_title": snippet.get("channelTitle"),
            "category_id":   snippet.get("categoryId"),
            "published_at":  pd.to_datetime(snippet.get("publishedAt"), utc=True, errors="coerce"),
            "tags":          "|".join(snippet.get("tags") or []),
            "view_count":    int(stats.get("viewCount", 0)),
            "like_count":    int(stats.get("likeCount", 0)),
            "comment_count": int(stats.get("commentCount", 0)),
        })
    
    return pd.DataFrame(records)

def load_api(region_code: str = "US") -> pd.DataFrame:
    """
    Main entry point.

    Args:
        region_code (str, optional): Country code for search. Defaults to "US".

    Returns:
        pd.DataFrame: DataFrame of trending videos
    """
    youtube = get_youtube_client()
    items = fetch_trending(youtube, region_code=region_code)
    return parse_items(items)

if __name__ == "__main__":
    df = load_api()
    print(df.shape)
    print(df.dtypes)    
    print()
    print(f"Fetched {len(df)} trending videos")
    print(df[["video_id", "title", "category_id", "view_count"]].head(5))

# Output:
#
# (199, 11) < NOT 200?
# video_id                         str
# snapshot_at      datetime64[us, UTC]
# title                            str
# channel_id                       str
# channel_title                    str
# category_id                      str < json holds string data as well, no need to convert
# published_at     datetime64[us, UTC]
# tags                             str
# view_count                     int64
# like_count                     int64
# comment_count                  int64
# dtype: object

# Fetched 199 trending videos
#       video_id                                              title category_id  view_count
# 0  UxA1nJEZRUs     Santa Fe Klan, Zimple - Gu3rr4 (Video Oficial)          10      419940
# 1  Kf3c53eX7Lg  Cyclops: The Fearless Leader | Character Revea...          20     1685489
# 2  PvUPDSDZg1k  Nintendo Direct 6.9.2026 + Nintendo Treehouse:...          20     4517707
# 3  N7JOI12o_NI                                  C-Kan - Toma Todo          10     1623672
# 4  gM4LkaXwGuY  THE SOCIAL RECKONING – Official Teaser Trailer...          24      252325