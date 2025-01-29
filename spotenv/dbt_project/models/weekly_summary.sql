SELECT
    EXTRACT(WEEKOFYEAR FROM TO_DATE(timestamp)) AS play_week,
    COUNT(played_at) AS total_plays
FROM {{ source('etl_public', 'MY_PLAYED_TRACKS') }}
GROUP BY play_week
ORDER BY play_week DESC

