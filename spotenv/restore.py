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

def restore_table():
    """Restore the MY_PLAYED_TRACKS table from a local CSV backup."""
    backup_file = "my_played_tracks_backup.csv"
    if not backup_file:
        print("Backup file not found. Skipping restore.")
        return

    with engine.connect() as conn:
        df = pd.read_csv(backup_file)
        if not df.empty:
            df.to_sql(
                "MY_PLAYED_TRACKS",
                conn,
                schema="ETL_PUBLIC",
                if_exists="append",  # Append to the table
                index=False,
                method="multi",
            )
            print("Backup restored successfully.")
        else:
            print("Backup file is empty. Nothing to restore.")

if __name__ == "__main__":
    restore_table()
