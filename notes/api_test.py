# TEST SCRIPT
# This script is being used to get data from YouTube API
# which is then pasted into api_test.json for analysis

import os
import json
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()

api_key = os.getenv("YOUTUBE_API_KEY")
youtube = build("youtube", "v3", developerKey=api_key)

response = youtube.videos().list(
    part="snippet,statistics",
    chart="mostPopular",
    regionCode="US",
    maxResults=3
).execute()

print(json.dumps(response, indent=2))
