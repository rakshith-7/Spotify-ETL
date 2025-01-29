import sqlite3

conn = sqlite3.connect("my_played_tracks.sqlite")
cursor = conn.cursor()

cursor.execute("SELECT * FROM my_played_tracks")
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()
