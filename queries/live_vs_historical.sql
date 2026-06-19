-- LIVE VS HISTORICAL CATEGORY COMPARISON
-- Is current trending category distribution consistent
-- with historical patterns, or is something unusual happening?
-- Category | # Trending Today | # Historical Appearances | Today's Category % | Historical Category %
WITH historical AS (
    SELECT
        c.category_name,
        COUNT(*) AS historical_count
    FROM stg_trending_snapshots s
    JOIN stg_videos v ON s.video_id = v.video_id
    JOIN stg_categories c ON v.category_id = c.category_id
    WHERE v.channel_id IS NULL
    GROUP BY c.category_name
),
live AS (
    SELECT
        c.category_name,
        COUNT(*) AS live_count
    FROM stg_trending_snapshots s
    JOIN stg_videos v ON s.video_id = v.video_id
    JOIN stg_categories c ON v.category_id = c.category_id
    WHERE v.channel_id IS NOT NULL
      AND s.snapshot_at = (SELECT MAX(snapshot_at) FROM stg_trending_snapshots WHERE video_id IN (
          SELECT video_id FROM stg_videos WHERE channel_id IS NOT NULL
      ))
    GROUP BY c.category_name
)
SELECT
    COALESCE(l.category_name, h.category_name) AS category_name,
    COALESCE(l.live_count, 0) AS live_trending_today,
    COALESCE(h.historical_count, 0) AS historical_appearances,
    ROUND(
        COALESCE(l.live_count, 0) * 100.0 /
        NULLIF(SUM(COALESCE(l.live_count, 0)) OVER (), 0), 1
    ) AS live_pct,
    ROUND(
        COALESCE(h.historical_count, 0) * 100.0 /
        NULLIF(SUM(COALESCE(h.historical_count, 0)) OVER (), 0), 1
    ) AS historical_pct
FROM live l
FULL OUTER JOIN historical h ON l.category_name = h.category_name
ORDER BY live_trending_today DESC;