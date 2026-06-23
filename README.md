# YouTube ETL Pipeline

An ETL and analytics pipeline that consolidates live YouTube trending data with hitorical trending records, enabling the monitoring of what's currently trending in the United States, category anomolies, and distinguishing short-term spikes from new trends. 


## Overview

The pipeline ingests data from two sources:

- **Historical Data**: [Trending YouTube Video Statistics (Kaggle)](https://www.kaggle.com/datasets/datasnaek/youtube-new), a one-time load of ~41,000 daily trending records spanning 2017–2018.
- **Live Data**:  [YouTube Data API v3](https://developers.google.com/youtube/v3), pulled daily via a scheduled cron job, capturing the current US trending list as a timestamped snapshot on each run.

Both sources are validated, cleaned, and loaded into the same staging tables for analysis.

After each daily API run, a selection of queries are fed to Google Gemini, which generates a plain-English summary of the day's trends. These summaries are then saved to the database for future use.

## Analytic Queries

All queries live in `queries/` as standalone `.sql` files. They are also executable from Python via `src/queries.py`:

```python
from src.queries import run_query
columns, rows = run_query("query_filename") # Do not include '.sql'
```

A quick summary of all the query files are as followed. Additional information can be found commented within each individial file. 
| Filename | Description |
|---|---|
| `trending_now.sql` | All information on the most recent trending snapshot. Ordered by view count. |
| `category_breakdown.sql` | Category information from most recent snapshot. Shows category, number of videos, and views information |
| `live_vs_historical.sql` | Today's category distribution vs the historical baseline |
| `engagement_rate.sql` | All information on the top 20 videos with the highest engagement. Ordered by 'Engagements per View' |
| `total_video_delta.sql` | Total engagement growth for each video on record since it first entered trending |
| `video_velocity.sql` | Fastest-growing videos between the two most recent snapshots (requires 2+ API runs) |
| `historical_category_dominance.sql` | Category infomation for the historical data. Categories ordered by # appearances in trending |
| `trending_channels.sql` | Returns all channels currently in trending, and what categories they post in |
| `new_to_trending.sql` | Videos appearing in today's snapshot for the first time (requires 2+ API runs) |
| `rejects_summary.sql` | All rejected columns, grouped by source and reason |

## AI Summary Layer

After each daily API run, analytic queries are passed to Gemini, who provides a plain-English summary of the trending data. This response is then saved to `daily_summaries`.

The default queries used in each summary:

- `live_vs_historical` — is today's category mix expected
- `new_to_trending` — what videos are newly trending today
- `video_velocity` — what videos are growing the fastest
- `engagement_rate` — what videos do audiences like the most


> **Note:** The Gemini API is frequently unavailable when using the free tier, which results in getting a `503` response. The script `daily.py` will retry up to 3 times, waiting 2 minutes in between runs, before marking the summary as a failure. In the event of a failure, it will be logged to `stg_rejects` and the pipeline exits cleanly. No loss of snapshot data will occur.

To view recent summaries:

```sql
SELECT summary_text, generated_at
FROM daily_summaries
ORDER BY generated_at DESC;
```


## Testing

To run tests on the entire system (for validation or for any additional features), run the following script:
```bash
pytest tests/ -v --cov=src --cov-report=term-missing
```

The code as it is now has **100% coverage** across all functions. These tests are all located in the `tests/` directory. All database and API calls are mocked using the `MagicMock` library to keep tests working while offline and limit API calls.


```bash
===================== tests coverage =====================
____ coverage: platform win32, python 3.14.0-final-0 ____

Name                         Stmts   Miss  Cover   Missing
----------------------------------------------------------
src\__init__.py                  0      0   100%
src\clean.py                    32      0   100%
src\config.py                   10      0   100%
src\load.py                     47      0   100%
src\main.py                     52      0   100%
src\queries.py                  16      0   100%
src\readers\__init__.py          0      0   100%
src\readers\api_reader.py       33      0   100%
src\readers\csv_reader.py        6      0   100%
src\readers\json_reader.py       9      0   100%
src\summarize.py                37      0   100%
----------------------------------------------------------
TOTAL                          242      0   100%
```

## Getting Started (Docker)

**You will need:** 
1) Docker
2) YouTube Data API v3 key
3) Gemini API key.

**1. Clone the repository**

```bash
git clone https://github.com/nick0connor/youtube-etl-pipeline.git
cd youtube-etl-pipeline/
```


**2. Create a `.env` file at the project root**

```env
DB_NAME = <Name to use for DB>
DB_USERNAME = <Username to use for DB>
DB_PASSWORD = <Password to use for DB>
YOUTUBE_API_KEY = <YOUR API KEY>
GEMINI_API_KEY = <YOUR API KEY>
```

**3. Start the pipeline**

```bash
docker compose up --build
```

On first boot, docker automatically runs the one-time CSV pipeline, then hands off to a cron job that calls `daily.py` every day at `06:00 UTC`.

**4. [OPTIONAL] Trigger a manual API run**

To immediately populate live data without waiting for the `06:00 UTC` cron trigger:

```bash
docker compose exec app python daily.py
```

**5. Connect to the database**

The Postgres container exposes port `5432` on `localhost`. Connect from any SQL client using the credentials from your `.env` file and `host=localhost`.


## Getting Started (PM2 / Manual)

> Docker is the recommended way to set up this pipeline. The following describes a secondary option which was personally used prior to setting up Docker in development. It may not be the most efficient, but it's just something I know works. 

**You will need:** 
- Python
- PostgreSQL
- Node.js (OPTIONAL: only needed for PM2 use),
- YouTube Data API v3 key,
- Gemini API key.

**1. Clone, create a virtual environment, and install dependencies**

```bash
git clone https://github.com/nick0connor/youtube-etl-pipeline.git
cd youtube-etl-pipeline
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**2. Create a `.env` file**

```env
DB_HOST = localhost 
DB_PORT = 5432
DB_NAME = <Name to use for DB>
DB_USERNAME = <Username to use for DB>
DB_PASSWORD = <Password to use for DB>
YOUTUBE_API_KEY = <YOUR API KEY>
GEMINI_API_KEY = <YOUR API KEY>
```

**3. Initialize the database**

```bash
psql -U DB_USERNAME -d DB_NAME -h localhost -f schema.sql
```

**4. Run both the one-time historical pipeline AND the live API pipeline**

```bash
python -m src.main
```

**5. [OPTIONAL] Schedule daily runs with PM2**

```bash
pm2 start daily.py --interpreter python --cron "0 6 * * *" --no-autorestart
pm2 save
```
You can adjust the time of the cron job by modifying `"0 6 * * * "`. The current configuration is for `06:00 UTC`.

If you choose to not set up with PM2, you can automatically trigger an API call by running
```bash
python daily.py
```