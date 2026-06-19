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