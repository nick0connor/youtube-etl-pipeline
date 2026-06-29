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
	ch.channel_title,
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
JOIN stg_channels ch
	ON ch.channel_id = v.channel_id 
WHERE rn = 1
	AND views_gained IS NOT NULL
	AND v.channel_id IS NOT null
	AND sd.snapshot_at = (SELECT MAX(snapshot_at) FROM stg_trending_snapshots)
ORDER BY sd.views_gained DESC;