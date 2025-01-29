from sqlalchemy import create_engine
from sqlalchemy import text  # Import text
import sqlite3
import pandas as pd
import requests
from datetime import datetime, timedelta
import subprocess

def backup_table():
    query = "SELECT * FROM ETL_PUBLIC.MY_PLAYED_TRACKS"
    with engine.connect() as conn:
        df = pd.read_sql_query(query, conn)
        df.to_csv("my_played_tracks_backup.csv", index=False)
        print("Backup completed: my_played_tracks_backup.csv")



# Snowflake connection details
SNOWFLAKE_USER = "RAKPA"  # Use your Snowflake username
SNOWFLAKE_PASSWORD = "Chimichanga123"  # Use your Snowflake password
SNOWFLAKE_ACCOUNT = "zdfoloi-au82040"  # Snowflake account (without `.snowflakecomputing.com`)
SNOWFLAKE_WAREHOUSE = "SPOTIFY_WH"  # Replace with your warehouse name
SNOWFLAKE_DATABASE = "SPOTIFY_ETL_DATA"  # Replace with your database name
SNOWFLAKE_SCHEMA = "ETL_PUBLIC"  # Replace with your schema name


# Connection string
engine = create_engine(
    f"snowflake://{SNOWFLAKE_USER}:{SNOWFLAKE_PASSWORD}@{SNOWFLAKE_ACCOUNT}/{SNOWFLAKE_DATABASE}/{SNOWFLAKE_SCHEMA}?warehouse={SNOWFLAKE_WAREHOUSE}",
    echo=True
)




def create_table():
    """Create the Snowflake table in the ETL_PUBLIC schema."""
    create_table_query = text("""
    CREATE TABLE IF NOT EXISTS ETL_PUBLIC.MY_PLAYED_TRACKS (
        song_name TEXT,
        artist_name TEXT,
        played_at TEXT PRIMARY KEY,
        timestamp TEXT
    )
    """)
    with engine.connect() as conn:
        conn.execute(create_table_query)  # Use text() to make the query executable
        print("Table created or already exists.")


#Fetch Data from Spotify API
TOKEN_URL = "https://accounts.spotify.com/api/token"


def refresh_access_token():
    """Refresh the access token using the refresh token."""
    try:
        with open("refresh_token.txt", "r") as refresh_file:
            refresh_token = refresh_file.read().strip()
    except FileNotFoundError:
        raise Exception("Refresh token file not found. Please run the authorization script.")


    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": "your_client_id",  # Replace with your Spotify Client ID
        "client_secret": "your_client_secret",  # Replace with your Spotify Client Secret
    }


    response = requests.post(TOKEN_URL, headers=headers, data=data)
    token_data = response.json()


    if "access_token" in token_data:
        # Save the new access token to file
        access_token = token_data["access_token"]
        with open("access_token.txt", "w") as token_file:
            token_file.write(access_token)
        print("Access token refreshed successfully.")
        return access_token
    else:
        raise Exception(f"Failed to refresh access token: {token_data}")




def read_access_token():
    """Read the access token and refresh if expired."""
    try:
        with open("access_token.txt", "r") as token_file:
            token = token_file.read().strip()


        # Test the token to see if it works
        headers = {"Authorization": f"Bearer {token}"}
        test_response = requests.get("https://api.spotify.com/v1/me", headers=headers)


        if test_response.status_code == 401:  # Token expired
            print("Access token expired. Refreshing...")
            return refresh_access_token()
        elif test_response.status_code != 200:
            raise Exception(f"Error validating access token: {test_response.json()}")


        return token
    except FileNotFoundError:
        raise Exception("Access token file not found. Please run the authorization script.")




def fetch_recently_played_tracks(token):
    """Fetch recently played tracks from Spotify."""
    headers = {"Authorization": f"Bearer {token}"}
    yesterday = datetime.now() - timedelta(days=1)
    yesterday_unix_timestamp = int(yesterday.timestamp()) * 1000


    try:
        response = requests.get(
            f"https://api.spotify.com/v1/me/player/recently-played?after={yesterday_unix_timestamp}",
            headers=headers,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Spotify API: {e}")
        return None
   


def check_if_valid_data(df: pd.DataFrame) -> bool:
    """Validate the DataFrame."""
    if df.empty:
        print("No songs downloaded. Finishing execution.")
        return False


    # Check for unique played_at values (Primary Key)
    if not pd.Series(df['played_at']).is_unique:
        raise Exception("Primary Key check is violated!")


    # Check for null values
    if df.isnull().values.any():
        raise Exception("Null values found!")


    return True


def load_new_data_to_snowflake(df: pd.DataFrame):
    """Load only new data into the Snowflake database."""
    with engine.connect() as conn:
        # Fetch existing played_at timestamps from Snowflake
        existing_played_at = pd.read_sql_query(
            "SELECT played_at FROM ETL_PUBLIC.MY_PLAYED_TRACKS",
            conn,
        )
        existing_played_at_set = set(existing_played_at["played_at"])

        # Filter out rows that already exist
        new_data = df[~df["played_at"].isin(existing_played_at_set)]

        if not new_data.empty:
            # Write new data
            new_data.to_sql(
                name="MY_PLAYED_TRACKS",
                con=conn,
                schema="ETL_PUBLIC",
                if_exists="append",
                index=False,
                method="multi",
                dtype={
                    "song_name": "TEXT",
                    "artist_name": "TEXT",
                    "played_at": "TEXT",
                    "timestamp": "TEXT",
                },
            )
            print(f"Loaded {len(new_data)} new rows into Snowflake.")
            conn.commit()  # Explicitly commit
        else:
            print("No new data to load.")


# def run_dbt_models(): - running dbt model by default
#     """Run DBT models for transformation."""
#     try:
#         subprocess.run(["dbt", "run"], cwd="dbt_project", check=True)
#         print("DBT models executed successfully.")
#     except subprocess.CalledProcessError as e:
#         print(f"Error running DBT models: {e}")

def run_dbt_models():
    """Run DBT models for transformation."""
    confirm = input("Do you want to run DBT models now? (yes/no): ")
    if confirm.lower() in ["yes", "y"]:
        try:
            subprocess.run(["dbt", "run"], cwd="dbt_project", check=True)
            print("DBT models executed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error running DBT models: {e}")
    else:
        print("Skipping DBT model execution.")


# Test the connection
if __name__ == "__main__":
    try:
        with engine.connect() as conn:
            print("Connection to Snowflake successful!")


            # Step 1: Ensure the table exists
            create_table()


            # Step 2: Read the access token
            TOKEN = read_access_token()


            # Step 3: Fetch data from Spotify API
            data = fetch_recently_played_tracks(TOKEN)
            if not data or "items" not in data:
                print("No data found or error in API response. Exiting.")
                exit()


            # Step 4: Extract relevant data into a DataFrame
            song_names = []
            artist_names = []
            played_at_list = []
            timestamps = []


            for song in data["items"]:
                song_names.append(song["track"]["name"])
                artist_names.append(song["track"]["artists"][0]["name"])
                played_at_list.append(song["played_at"])
                timestamps.append(song["played_at"][0:10])

            song_dict = {
                "song_name": song_names,
                "artist_name": artist_names,
                "played_at": played_at_list,
                "timestamp": timestamps,
            }
            song_df = pd.DataFrame(song_dict)

            # Step 5: Validate the data
            if check_if_valid_data(song_df):
                print("Data is valid. Proceeding to load...")

            # Step 6: Load only new data into Snowflake
            load_new_data_to_snowflake(song_df)

            run_dbt_models()  # Run DBT transformations

    except Exception as e:
        print(f"Error: {e}")



