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
)
order by c.category_name asc;