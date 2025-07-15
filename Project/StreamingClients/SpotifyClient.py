from __future__ import annotations
from typing import Any, Dict, List, Optional
import spotipy
from spotipy.oauth2 import SpotifyOAuth

class SpotifyClient():

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,) -> None:

        self.spotipy_client = spotipy.Spotify(auth_manager=SpotifyOAuth(
            scope = "user-read-private user-read-email user-top-read",
            redirect_uri=redirect_uri,
            client_id=client_id,
            client_secret=client_secret,
        ))

    def get_user_profile(self) -> dict:
        return self.spotipy_client.current_user()

    def get_top_tracks(self,
                       limit: int = 20,
                       time_range: str = "short_term") -> list[dict]:
        return self.spotipy_client.current_user_top_tracks(
            limit=limit, time_range=time_range)["items"]

    def get_top_artists(self,
                        limit: int = 20,
                        time_range: str = "short_term") -> list[dict]:
        return self.spotipy_client.current_user_top_artists(
            limit=limit, time_range=time_range)["items"]
    
    def get_all_playlists(self, limit:int = 50):
        playlists = []
        offset = 0

        while True:
            response = self.spotipy_client.current_user_playlists(limit=limit, offset=offset)
            playlists.extend(response["items"])
            if response["next"] is None:
                break
            offset += 50

        return playlists
    
    def get_playlist(self, playlist_name:str, limit:int = 1) -> list[dict]:
        return self.spotipy_client.search(q=playlist_name, type="playlist", limit=limit)
    
    def get_playlist_tracks(self, playlist_id: str) -> list[dict]:
        tracks = []
        offset = 0

        while True:
            response = self.spotipy_client.playlist_items(playlist_id, limit=100, offset=offset)

            for item in response["items"]:
                track = item.get("track")
                if track is None:
                    continue

                # Grab only what you need
                tracks.append({
                    "id": track["id"],
                    "name": track["name"],
                    "artists": [artist["name"] for artist in track["artists"]],
                    "album": track["album"]["name"],
                    "duration_ms": track["duration_ms"]
                })

            if response["next"] is None:
                break

            offset += 100

        return tracks

    
    def get_audio_features(self, track_ids: list[str]) -> list[dict]:
        return self.spotipy_client.audio_features(track_ids)
    
    def remove_duplicates(self, tracks):
        seen = set()
        out  = []
        for t in tracks:
            key = (t['artist'].lower(), t['title'].lower())
            if key in seen:
                continue
            seen.add(key)
            out.append(t)
        return out
    
    def get_user_tracks_list(self):
        ranges = ["short_term", "long_term", "medium_term"]

        top_tracks_list = []

        for time_range in ranges:
            top_tracks = self.get_top_tracks(50, time_range=time_range)
            for track in top_tracks:
                top_tracks_list.append({"artist": track["artists"][0]["name"], "title": track["name"]})

        top_tracks_list = self.remove_duplicates(top_tracks_list)

        return top_tracks_list