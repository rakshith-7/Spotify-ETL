SELECT
    artist_name,
    COUNT(played_at) AS play_count,
    MAX(timestamp) AS last_played
FROM {{ source('etl_public', 'MY_PLAYED_TRACKS') }}
GROUP BY artist_name
ORDER BY play_count DESC

