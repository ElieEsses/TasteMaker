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

    def get_audio_features(self, track_ids: list[str]) -> list[dict]:
        return self.spotipy_client.audio_features(track_ids)
    