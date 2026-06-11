-- TEXT is the same thing as VARCHAR with no true limit in PostgreSQL
-- TIMESTAMPTZ accounts for timezone
-- _loaded_at is a pipeline audit column: when each row entered system, separate from snapshot_at

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
    channel_id      TEXT NOT NULL REFERENCES stg_channels(channel_id),
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