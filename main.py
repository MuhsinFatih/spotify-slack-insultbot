import os
import pickle
import time
import humanfriendly

import openai
import schedule
import spotipy
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from spotipy.oauth2 import SpotifyClientCredentials

# File to store the previous list of tracks
PREVIOUS_TRACKS_FILE = "previous_tracks.pickle"
PREVIOUS_RESPONSE_FILE = "previous_response.pickle"

# Set up credentials
SPOTIPY_CLIENT_ID = os.environ["SPOTIPY_CLIENT_ID"]
SPOTIPY_CLIENT_SECRET = os.environ["SPOTIPY_CLIENT_SECRET"]

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

SLACK_API_TOKEN = os.environ["SLACK_API_TOKEN"]

# Set up settings
PLAYLIST_ID = os.environ["SPOTIFY_PLAYLIST_ID"]
SLACK_CHANNEL = os.environ["SLACK_CHANNEL"]
MODEL_NAME = os.environ["MODEL_NAME"]
TIME_OF_DAY = os.environ["TIME_OF_DAY"]
# Connect to Spotify API
spotify_credentials = SpotifyClientCredentials(
    client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET
)
spotify = spotipy.Spotify(client_credentials_manager=spotify_credentials)

# Authenticate OpenAI API
openai.api_key = OPENAI_API_KEY

# Connect to Slack API
slack_client = WebClient(token=SLACK_API_TOKEN)

# Your Spotify playlist ID and Slack channel


def get_playlist_tracks(playlist_id):
    results = spotify.playlist_tracks(playlist_id)
    tracks = results["items"]
    return tracks


def get_music_recommendations(tracks):
    # Extract track names and artists to send to GPT-3
    track_list = [
        f"{track['track']['name']} - {track['track']['artists'][0]['name']}" for track in tracks
    ]
    track_list = "\n".join(track_list)

    # Generate music recommendations using GPT-3 chat-based API
    try:
        response = openai.ChatCompletion.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "You are GLaDOS from Portal. Your function is to insult the music "
                    "taste of a group of engineers at a software company. You'll be provided with "
                    "a playlist curated by these engineers. You'll make very sarcastic jokes and "
                    "recommend an alternative song that will match their taste. You're going "
                    "to keep the commentary short. You won't list the songs in the playlist.",
                },
                {
                    "role": "user",
                    "content": f"Based on the following tracks in the company spotify list, suggest "
                    "a song:\n{track_list}",
                },
            ],
            max_tokens=200,
            n=1,
            temperature=0.8,
        )

        suggestion = response.choices[0].message.content.strip()

        return suggestion

    except Exception as e:
        print(f"Error generating recommendations: {e}")
        raise e
        return None


def post_suggestion_to_slack(suggestion):
    try:
        slack_client.chat_postMessage(
            channel=SLACK_CHANNEL, text=f"Today's music suggestion: {suggestion}"
        )
    except SlackApiError as e:
        print(f"Error posting message to Slack: {e}")


def save_previous_tracks(tracks):
    with open(PREVIOUS_TRACKS_FILE, "wb") as f:
        pickle.dump(tracks, f)


def load_previous_tracks():
    if os.path.exists(PREVIOUS_TRACKS_FILE):
        with open(PREVIOUS_TRACKS_FILE, "rb") as f:
            return pickle.load(f)
    return []


def tracks_changed(prev_tracks, curr_tracks):
    if len(prev_tracks) != len(curr_tracks):
        return True

    for prev_track, curr_track in zip(prev_tracks, curr_tracks):
        if prev_track["track"]["id"] != curr_track["track"]["id"]:
            return True

    return False


def recommend():
    # Get tracks from the Spotify playlist
    tracks = get_playlist_tracks(PLAYLIST_ID)

    print("Tracks:")
    for i, item in enumerate(tracks):
        track = item["track"]
        print(" ", i, track["artists"][0]["name"], " – ", track["name"])

    # Get a music recommendation using GPT-4
    suggestion = get_music_recommendations(tracks)
    print(f"suggestion: { suggestion }")

    # if suggestion:
    #     # Post the suggestion to the Slack channel
    #     post_suggestion_to_slack(suggestion)


if __name__ == "__main__":
    print(
        f"Starting with the configuration:\n\tPlaylist ID: {PLAYLIST_ID}\n"
        f"\tSlack Channel: {SLACK_CHANNEL}\n\tModel Name: {MODEL_NAME}"
    )
    print("Scheduling job...")
    schedule.every().day.at(TIME_OF_DAY).do(recommend)
    print(f"Job scheduled. Next run in {humanfriendly.format_timespan(schedule.idle_seconds())}")
    while True:
        schedule.run_pending()
        time.sleep(1)
