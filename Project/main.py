import os
from StreamingClients.SpotifyClient import SpotifyClient

from dotenv import load_dotenv
load_dotenv()

def main():

    spotify_client = SpotifyClient(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
    )

    # print(spotify_client.get_user_profile())
    # print(spotify_client.get_top_tracks())
    top_tracks = spotify_client.get_top_tracks(limit=50, time_range="long_term")
    for track in top_tracks:
        print(track['name'], "by", ", ".join(artist['name'] for artist in track['artists']))
    # print(spotify_client.get_top_artists())


if __name__ == "__main__":
    main()