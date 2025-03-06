🎵 Spotify ETL Pipeline
📌 Project Overview
This project is an ETL (Extract, Transform, Load) pipeline designed to extract recently played tracks from Spotify's API, process and clean the data, and store it in a database for analysis. 
The system includes API authentication, data validation, database storage, and a DBT project for transformations.


🚀 Setup & Usage
1️⃣ Create a Spotify Developer Account
Once the app is created, Spotify provides API credentials:

Client ID → Unique identifier for the application.
Client Secret → Used for secure authentication.
Redirect URI → The URL where Spotify redirects after user authentication.

Store this for usage in etl_script.py file

2️⃣ Set Up Virtual Environment (Why spotenv?)
Why use spotenv?
The spotenv virtual environment ensures that all dependencies specific to this project are installed in an isolated environment. 
This prevents conflicts with system-wide Python packages and ensures consistency across different machines.

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Authenticate & Fetch Access Tokens
python fetch_and_authorize.py
This step will generate the access_token.txt file needed for API requests.
The script runs a Flask server to handle Spotify OAuth authentication and automatically saves the token for further API requests.

5️⃣ Run the ETL Script
python etl_script.py
This script fetches the recently played tracks and loads them into the database.
If no new tracks are available, it will notify the user instead of reloading duplicate data.

6️⃣ View Stored Data
python db_view.py
This script allows you to inspect the SQLite database and verify the stored records.

7️⃣ Backup and Restore Data (Optional)
To backup data:
python backup.py
To restore from backup:
python restore.py


🔍 How the ETL Process Works

Extract

- Fetches recently played tracks from Spotify's API.
- Stores authentication tokens for future API requests.

Transform

- Validates data (removes duplicates and null values).
- Extracts relevant track details (song name, artist, timestamp).
- Prepares the data for loading.

Load

- Inserts new records into an SQLite database.
- Ensures data integrity with a primary key constraint to avoid duplicates.

🛠️ Technologies Used

- Python (for scripting)
- Spotify API (for extracting data)
- SQLite (for storing structured data)
- DBT (for transformations)
- Flask (for API authentication)
- Pandas (for data manipulation)

📈 Future Scope 🚀
This project is designed to be scalable, and the following improvements can be added in the future:

🔹 1. Tableau Dashboard for Analysis
The stored Spotify data can be visualized using Tableau to gain insights into listening habits, artist preferences, and peak listening times.
Potential visualizations:
Top artists and songs
Listening trends over time
Most active listening hours in a day
Genre distribution of played tracks
🔹 2. Scheduled ETL Execution
Automating the ETL script to run at regular intervals using cron jobs (Linux) or Task Scheduler (Windows).
This will ensure continuous data collection without manual execution.
🔹 3. Cloud Database Integration
Instead of storing data locally in SQLite, it can be migrated to a cloud-based data warehouse such as:
AWS RDS (PostgreSQL/MySQL)
Google BigQuery
Snowflake
🔹 4. Expanding Data Sources
Fetch additional data from Spotify API, such as:
User's liked songs
Playlist data
Audio features of tracks (tempo, danceability, energy, etc.)

🤝 Contributions
If you’d like to contribute, fork the repository, create a new branch, and submit a pull request.
Feel free to report issues or suggest improvements.
