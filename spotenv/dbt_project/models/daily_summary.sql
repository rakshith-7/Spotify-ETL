SELECT
    DATE(timestamp) AS play_date,
    COUNT(played_at) AS total_plays
FROM {{ source('etl_public', 'MY_PLAYED_TRACKS') }}
GROUP BY play_date
ORDER BY play_date DESC

