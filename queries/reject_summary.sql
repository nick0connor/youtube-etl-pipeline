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