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