import requests
from flask import Flask, request
import threading

# Spotify API credentials
CLIENT_ID = "eed160c259bd48348001e3c4a252e3a2"  # Replace with your Spotify client ID
CLIENT_SECRET = "031f13071cf14aac8a74cfe46b4dc8d1"  # Replace with your Spotify client secret
REDIRECT_URI = "http://localhost:8080/callback"
TOKEN_URL = "https://accounts.spotify.com/api/token"

# Flask app to handle Spotify's redirect
app = Flask(__name__)

# Create a global variable for shutting down the server
shutdown_event = threading.Event()

@app.route("/callback")
def callback():
    """Handle Spotify's redirect and fetch the authorization code."""
    auth_code = request.args.get("code")
    if not auth_code:
        return "Authorization failed. No code provided.", 400

    # Exchange authorization code for access and refresh tokens
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }

    response = requests.post(TOKEN_URL, headers=headers, data=data)
    token_data = response.json()

    if "access_token" in token_data and "refresh_token" in token_data:
        access_token = token_data["access_token"]
        refresh_token = token_data["refresh_token"]

        # Save tokens to files
        with open("access_token.txt", "w") as token_file:
            token_file.write(access_token)
        with open("refresh_token.txt", "w") as refresh_file:
            refresh_file.write(refresh_token)

        print(f"Access token successfully saved to access_token.txt")
        print(f"Refresh token successfully saved to refresh_token.txt")

        # Signal the server to shut down
        shutdown_event.set()
        return "Authorization successful. You can close this tab."
    else:
        return f"Authorization failed: {token_data}", 400


def generate_auth_url():
    """Generate Spotify authorization URL."""
    scopes = "user-read-recently-played"
    auth_url = (
        f"https://accounts.spotify.com/authorize"
        f"?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope={scopes}"
    )
    print(f"Go to the following URL to authorize your app:\n{auth_url}")


def run_server():
    """Run the Flask server in a separate thread."""
    app.run(port=8080)


if __name__ == "__main__":
    # Generate authorization URL and start Flask server in a thread
    generate_auth_url()
    server_thread = threading.Thread(target=run_server, daemon=True)  # Use daemon thread
    server_thread.start()

    # Wait for the server to signal shutdown
    shutdown_event.wait()
    print("Flask server has shut down.")