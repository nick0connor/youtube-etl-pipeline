# YouTube Performance Tool

### Pitch
    A data ingestion pipeline that pulls live trending video data from the YouTube API and cross-references it against a historical Kaggle dataset of US trending videos. It validates and cleans both sources, loads them into PostgreSQL staging tables, and captures any rejected records with reasons for auditing. The goal is to give a media analytics team a reliable, scheduled feed of what's trending — with enough historical context to distinguish a genuine trend from a one-day spike.

**Every decision you make: what tables to build, what validation rules to write, 
what the AI summary says, should serve that sentence.** 

**If a feature doesn't serve it, cut it.**

## The Workflow, End to End
### Phase 1 — Define your sources

- Register for a YouTube Data API v3 key (free, takes 10 minutes)
- Download the Kaggle YouTube Trending dataset (static CSV, no account needed with the right link)
- Decide what you're actually tracking: a handful of channels, a category (gaming, tech, etc.), or a country's trending list

### Phase 2 — Build the reader layer

- One reader for the API (JSON responses → DataFrame)
- One reader for the CSV (pandas, straightforward)
- Both should normalize into the same column shape before validation touches them

### Phase 3 — Validate and clean

- This is where your spec's rules kick in: null checks, type casting, domain rules (view counts can't be negative, dates must parse, etc.)
- Rejects go to `stg_rejects` with reasons

### Phase 4 — Load into Postgres

- `stg_videos` — one row per video per ingestion run (this is what builds your time series)
- `stg_channels` — channel-level metadata
- `stg_trending` — from the Kaggle CSV, historical trending records by region
- UPSERT pattern for the live data, straight insert for the historical CSV (it's static)

### Phase 5 — Schedule it

- Even a simple loop with a time.sleep() or APScheduler running every 24 hours turns this into a live system
- This is the detail that makes it feel real

### Phase 6 — Analytics + AI layer

- A few SQL queries or views: top growing videos this week, channels with declining engagement, videos trending in multiple regions
- Pipe a summary to an LLM (Claude or Gemini) → plain English report generated after each run

### Phase 7 — Polish

- Docker Compose file so it runs in one command
- README with screenshots of logs, test results, DB schema, and a sample AI summary
- Pytest coverage at 80%+

## How to Get Started Tomorrow
The biggest mistake would be trying to build everything at once. The order matters:

1) Get your YouTube API key and make one raw API call manually — just print the JSON response. Understand what you're actually getting before building around it.
2) Download the Kaggle dataset and open it in pandas. Look at the columns, find the nulls, understand the shape.
3) Sketch your DB schema on paper (or a diagram tool) before writing any Python. What tables, what columns, what's the primary key for the time-series table?
4) Build the simplest possible version first — one reader, one table, one validation rule, one test. Get that working end to end before adding complexity.

## Why "US Trending + Categories" works so well
The YouTube API lets you pull the current trending list filtered by region and optionally by category in a single call. The Kaggle dataset happens to use the same category_id field and covers the US region with daily historical snapshots. That means your join key between live and historical data already exists — you don't have to engineer a bridge between them.

The question you can now answer that neither data source alone could answer is:
    
    "Is this video trending in a category that historically sustains trending status, or is it a flash in the pan?"

That's a real analytical insight. It's also a great demo moment.

### What this means for your schema
You'd have roughly five tables:

- `stg_trending_snapshots` — the heart of the project. One row per video per pipeline run. This is what builds your time series: video_id, snapshot_at, view_count, like_count, comment_count, rank_position
- `stg_videos` — video metadata that doesn't change run to run: video_id, title, channel_title, published_at, category_id
- `stg_categories` — a simple lookup table mapping category_id to a name like "Gaming" or "Music." Both the API and the Kaggle CSV use the same IDs, so this table serves both sources
- `stg_trending_historical` — loaded once from the Kaggle CSV: historical daily trending records with video_id, trending_date, category_id, view_count, region
- `stg_rejects` — standard from your spec


### The natural story arc for your demo

1) Historical CSV loads once, establishing baseline category behavior over years of data
2) Live API runs on a schedule, capturing today's trending list as a snapshot
3) A simple query joins them: "Of today's trending videos, which categories have the strongest historical trending track record in the US?"
4) The AI summary layer reads that query result and writes a plain-English brief

That arc — ingest, compare, surface insight — is exactly what a Cognizant data engineering team would build for a media client.

## Clarification on project scope

    So this project would mostly be looking at and analyzing daily trending videos to generate data about what's popular right now?

    Or are we going to tighten this down to analyze a current video to what we expect the performance would be like to better prepare?

    OR is this going to be for a future "potential video" where we say "If I make a video in the Gaming category playing X game for Y minutes, I expect it to perform like Z"?

These are actually three distinct products, not three versions of the same project:

- Option 1 is a *monitoring dashboard* — you're watching what's happening in real time
- Option 2 is a *diagnostic tool* — you're evaluating a specific video that already exists
- Option 3 is a *predictive planning tool* — you're forecasting before anything is created

Each one has a different primary user, different schema needs, and a different analytical core. The good news is that **Option 1** is the right choice for this project, and here's why: your spec explicitly calls for an ingestion and staging pipeline, not a predictive model. Options 2 and 3 are machine learning problems — they need training data, model fitting, and evaluation frameworks that are well outside the scope of what's being asked of you here.

Option 1 also naturally enables Options 2 and 3 down the road, which is actually a great thing to say in a demo: *"This pipeline is the foundation. Once you have 6 months of snapshots, you have a training dataset for a performance prediction model."* That shows systems thinking without overcommitting to scope.

### Potential User Stories
Framing it as a media analytics team using this internally:

1) As a content analyst, I want to see which videos are currently trending in the US so I can report on what's capturing audience attention this week.
2) As a content analyst, I want to know which categories appear most frequently in today's trending list so I can advise our production team on what content to prioritize.
3) As a content strategist, I want to compare today's trending categories against historical patterns so I can distinguish sustained trends from short-term spikes.
4) As a data engineer, I want all ingestion runs logged with row counts, rejects, and duration so I can audit the pipeline's reliability.
5) As a data engineer, I want invalid or malformed records captured in a rejects table with reasons so nothing is silently dropped.
6) As a content analyst, I want a plain-English summary generated after each pipeline run so I don't have to write SQL to understand what changed.

That last one is your AI layer, and it earns its place because it has a real user with a real need — not just "we added AI because it's cool."

## APIs and Datasets

[Kaggle CSV](https://www.kaggle.com/datasets/datasnaek/youtube-new?select=US_category_id.json)

[YouTube API](https://developers.google.com/youtube/v3)

## A few tips for the conversation:

- Lead with the problem, not the technology. Don't open with "I used psycopg and pandas" — open with "the goal was to build something that answers what's actually trending right now and whether it's likely to last."
- The two-source angle is your strongest talking point. Most student projects use one static dataset. Having a live API feeding into the same pipeline as a historical CSV, with a shared category lookup table joining them, shows you thought about real data engineering problems.
- Be ready for "why YouTube?" Your answer is that content performance analytics is a real and growing vertical, YouTube's API is production-grade, and the data is rich enough to demonstrate every layer of the pipeline — validation, cleaning, UPSERT loading, and reject tracking.