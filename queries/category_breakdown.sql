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