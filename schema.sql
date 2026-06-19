-- NOTES: 
-- _loaded_at is a pipeline audit column (use snapshot_at if timestamp needed)
-- 
-- stg_videos.channel_id will only be NULL IFF video is sourced from the historical CSV data
-- Modern API calls include the channel_id and thus stg_videos.channel_id IS NOT NULL = true
-- I use this split to denote modern/historical in the database. Sloppy, but efficient

CREATE TABLE IF NOT EXISTS stg_categories (
    category_id     TEXT PRIMARY KEY,
    category_name   TEXT NOT NULL,
    assignable      BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS stg_channels (
    channel_id      TEXT PRIMARY KEY,
    channel_title   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS stg_videos (
    video_id        TEXT PRIMARY KEY,
    channel_id      TEXT REFERENCES stg_channels(channel_id), -- NULL for CSV-sourced videos
    category_id     TEXT NOT NULL REFERENCES stg_categories(category_id),
    title           TEXT NOT NULL,
    published_at    TIMESTAMPTZ,
    tags            TEXT,
    _loaded_at      TIMESTAMPTZ NOT NULL DEFAULT NOW() 
);

CREATE TABLE IF NOT EXISTS stg_trending_snapshots (
    id              BIGSERIAL PRIMARY KEY, 
    video_id        TEXT NOT NULL REFERENCES stg_videos(video_id),
    snapshot_at     TIMESTAMPTZ NOT NULL,
    view_count      BIGINT NOT NULL,
    like_count      BIGINT NOT NULL,
    comment_count   BIGINT NOT NULL,
    _loaded_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS stg_rejects (
    id              BIGSERIAL PRIMARY KEY,
    source_name     TEXT NOT NULL,
    raw_payload     JSONB NOT NULL,
    reason          TEXT NOT NULL,
    rejected_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS daily_summaries (
    id              BIGSERIAL PRIMARY KEY,
    generated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    summary_text    TEXT NOT NULL
);