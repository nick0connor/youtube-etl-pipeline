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
LEFT JOIN stg_channels ch ON v.channel_id  = ch.channel_id 
WHERE s.snapshot_at = (SELECT MAX(snapshot_at) FROM stg_trending_snapshots)
ORDER BY s.view_count DESC;