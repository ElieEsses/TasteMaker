import os
from dotenv import load_dotenv
load_dotenv()

from SpotifyAPI import SpotifyAPI

spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID")
spotify_client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

spotify_client = SpotifyAPI(spotify_client_id, spotify_client_secret)

song_data = spotify_client.get_song_data("bad guy", limit=1)
track = song_data["tracks"]["items"][0]

print(track["name"])
print(track["artists"][0]["name"])