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