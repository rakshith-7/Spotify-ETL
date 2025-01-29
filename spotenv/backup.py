import pandas as pd
from sqlalchemy import create_engine

# Add your Snowflake credentials here
SNOWFLAKE_USER = "RAKPA"
SNOWFLAKE_PASSWORD = "Chimichanga123"
SNOWFLAKE_ACCOUNT = "zdfoloi-au82040"
SNOWFLAKE_WAREHOUSE = "SPOTIFY_WH"
SNOWFLAKE_DATABASE = "SPOTIFY_ETL_DATA"
SNOWFLAKE_SCHEMA = "ETL_PUBLIC"

engine = create_engine(
    f"snowflake://{SNOWFLAKE_USER}:{SNOWFLAKE_PASSWORD}@{SNOWFLAKE_ACCOUNT}/{SNOWFLAKE_DATABASE}/{SNOWFLAKE_SCHEMA}?warehouse={SNOWFLAKE_WAREHOUSE}"
)

def backup_table():
    """Backup the MY_PLAYED_TRACKS table to a local CSV file."""
    backup_file = "my_played_tracks_backup.csv"
    query = "SELECT * FROM ETL_PUBLIC.MY_PLAYED_TRACKS"

    with engine.connect() as conn:
        df = pd.read_sql_query(query, conn)
        if not df.empty:
            df.to_csv(backup_file, index=False)
            print(f"Backup created: {backup_file}")
        else:
            print("No data found to back up.")
    return backup_file

if __name__ == "__main__":
    backup_table()
