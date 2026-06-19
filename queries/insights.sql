-- NOTE: 
-- Due to the nature of the datasets: 
-- stg_videos.channel_id will only be NULL IFF video is sourced from the historical CSV data
-- Modern API calls include the channel_id and thus stg_videos.channel_id IS NOT NULL = true
-- I use this split to denote modern/historical. Sloppy, but efficient

-- TODAY'S TRENDING VIDEOS
-- What is currently trending and in what category?
-- ID | Title | Channel | Category | Views | Likes | Comments | Snapshot Time
SELECT
    v.video_id,
    v.title,
    ch.channel_title,
    c.category_name,
    s.view_count,
    s.like_count,
    s.comment_count,
    s.snapshot_at
FROM stg_trending_snapshots s
JOIN stg_videos v ON s.video_id = v.video_id
JOIN stg_categories c ON v.category_id = c.category_id
JOIN stg_channels ch ON v.channel_id  = ch.channel_id 
WHERE s.snapshot_at = (SELECT MAX(snapshot_at) FROM stg_trending_snapshots)
ORDER BY s.view_count DESC;


-- CATEGORY BREAKDOWN
-- Which categories appear most in today's trending?
-- Category | Count | Average Views | Total Views
SELECT
    c.category_name,
    COUNT(*) AS video_count,
    ROUND(AVG(s.view_count),2) AS avg_views,
    SUM(s.view_count) AS total_views
FROM stg_trending_snapshots s
JOIN stg_videos v ON s.video_id = v.video_id
JOIN stg_categories c ON v.category_id = c.category_id
WHERE s.snapshot_at = (SELECT MAX(snapshot_at) FROM stg_trending_snapshots)
GROUP BY c.category_name
ORDER BY video_count DESC;


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


-- TOP VIDEOS BY ENGAGEMENT RATE
-- Likes + comments relative to views: which videos are driving the most interaction?
-- Video Title | Channel | Category | Views | Likes | Comments | 'Engagement per View'
SELECT
    v.title,
    ch.channel_title,
    c.category_name,
    s.view_count,
    s.like_count,
    s.comment_count,
    ROUND(
        (s.like_count + s.comment_count) * 100.0 /
        NULLIF(s.view_count, 0), 2
    ) AS engagement_rate_pct
FROM stg_trending_snapshots s
JOIN stg_videos v ON s.video_id = v.video_id
JOIN stg_categories c ON v.category_id = c.category_id
LEFT JOIN stg_channels ch ON v.channel_id = ch.channel_id 
WHERE s.snapshot_at = (SELECT MAX(snapshot_at) FROM stg_trending_snapshots)
ORDER BY engagement_rate_pct DESC
LIMIT 20;


-- TOTAL VIDEO DELTA 
-- Which videos have grown the most after entering trending?
-- Video Title | Views Gained | Likes Gained | Comments Gained | First Snapshot | Last Snapshot
WITH first_last AS (
	SELECT
		video_id,
		MIN(snapshot_at) AS first_seen,
		MAX(snapshot_at) AS last_seen
	FROM stg_trending_snapshots
	GROUP BY video_id
)
SELECT
	v.title,
	last_seen.view_count - first_seen.view_count AS views_gained,
	last_seen.like_count - first_seen.like_count AS likes_gained,
	last_seen.comment_count - first_seen.comment_count AS comments_gained,
	first_last.first_seen,
	first_last.last_seen
FROM first_last
JOIN stg_trending_snapshots first_seen
	ON first_seen.video_id = first_last.video_id 
	AND first_seen.snapshot_at = first_last.first_seen
JOIN stg_trending_snapshots last_seen
	ON last_seen.video_id = first_last.video_id 
	AND last_seen.snapshot_at = first_last.last_seen
JOIN stg_videos v
	ON v.video_id = first_last.video_id 
WHERE first_seen.snapshot_at != last_seen.snapshot_at;


-- VIDEO VELOCITY
-- Which videos are growing fastest in trending?
-- Video Title | Views Gained | Likes Gained | Comments Gained | Time Since Previous Snapshot
WITH snapshot_deltas AS (
    SELECT
    	video_id,
    	snapshot_at,
    	view_count,
    	like_count,
    	comment_count,
        view_count - LAG(view_count) OVER (
        	PARTITION BY video_id
        	ORDER BY snapshot_at
        ) AS views_gained,
        like_count - LAG(like_count) OVER (
        	PARTITION BY video_id
        	ORDER BY snapshot_at
        ) AS likes_gained,
        comment_count - LAG(comment_count) OVER (
        	PARTITION BY video_id
        	ORDER BY snapshot_at
        ) AS comments_gained,
        snapshot_at - LAG(snapshot_at) OVER (
        	PARTITION BY video_id
        	ORDER BY snapshot_at
        ) AS time_delta,
        ROW_NUMBER() OVER (
        	PARTITION BY video_id
        	ORDER BY snapshot_at DESC
        ) AS rn
    FROM stg_trending_snapshots
)
SELECT
    v.title,
    c.category_name,
    sd.views_gained,
    sd.likes_gained,
    sd.comments_gained,
    sd.time_delta,
    sd.snapshot_at AS most_recent_snapshot
FROM snapshot_deltas sd
JOIN stg_videos v
    ON v.video_id = sd.video_id
JOIN stg_categories c
	ON v.category_id = c.category_id 
WHERE rn = 1
  AND views_gained IS NOT NULL
 AND v.channel_id IS NOT NULL
ORDER BY sd.views_gained DESC;


-- HISTORICAL CATEGORY DOMINANCE
-- Which categories have trended most over time historically?
-- Category | # Trending Appearances | Unique Videos | Avg Views While Trending
SELECT
    c.category_name,
    COUNT(*) AS total_trending_appearances,
    COUNT(DISTINCT v.video_id) AS unique_videos,
    ROUND(AVG(s.view_count)) AS avg_views_when_trending
FROM stg_trending_snapshots s
JOIN stg_videos v ON s.video_id = v.video_id
JOIN stg_categories c ON v.category_id = c.category_id
WHERE v.channel_id IS NULL
GROUP BY c.category_name
ORDER BY total_trending_appearances DESC;


-- TRENDING CHANNELS NOW
-- Which channels are in trending and what categories do they post videos in?
-- Channel | Category | Number of Videos In Category
SELECT
    ch.channel_title,
    c.category_name,
    COUNT(DISTINCT v.video_id) AS unique_videos_trending
FROM stg_channels ch
JOIN stg_videos v ON ch.channel_id = v.channel_id 
JOIN stg_trending_snapshots s ON s.video_id = v.video_id 
JOIN stg_categories c ON v.category_id = c.category_id
GROUP BY ch.channel_title, c.category_name 
ORDER BY unique_videos_trending DESC;


-- REJECT SUMMARY
-- What's being rejected, and why?
-- Source | Reason | # Rejected
SELECT
    source_name,
    reason,
    COUNT(*) AS reject_count
FROM stg_rejects
GROUP BY source_name, reason
ORDER BY reject_count DESC;


-- NEW TO TRENDING
-- What videos just entered trending this snapshot?
-- Title | Channel | Category | Views | Likes | Comments | Snapshot
SELECT
    v.title,
    ch.channel_title,
    c.category_name,
    s.view_count,
    s.like_count,
    s.comment_count,
    s.snapshot_at
FROM stg_trending_snapshots s
JOIN stg_videos v ON s.video_id = v.video_id
JOIN stg_categories c ON v.category_id = c.category_id
LEFT JOIN stg_channels ch ON v.channel_id = ch.channel_id
WHERE s.snapshot_at = (SELECT MAX(snapshot_at) FROM stg_trending_snapshots WHERE video_id IN (
    SELECT video_id FROM stg_videos WHERE channel_id IS NOT NULL
))
AND v.video_id NOT IN (
    SELECT video_id FROM stg_trending_snapshots
    WHERE snapshot_at < (SELECT MAX(snapshot_at) FROM stg_trending_snapshots)
    AND video_id IN (SELECT video_id FROM stg_videos WHERE channel_id IS NOT NULL)
);