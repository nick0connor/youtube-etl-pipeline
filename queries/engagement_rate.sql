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