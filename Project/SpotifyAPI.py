import requests
import base64
import time

class SpotifyAPI:
    AUTH_URL = "https://accounts.spotify.com/api/token"
    API_URL = "https://api.spotify.com/v1"

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self._access_token = None
        self._expires_at = 0  
    
    def get_song_data(self, song_name: str, limit: int = 1) -> dict:
        token = self._token()

        params = {"q": song_name, "type": "track", "limit": limit}

        res = requests.get(f"{self.API_URL}/search", params=params,
                           headers={"Authorization": f"Bearer {token}"})
        
        res.raise_for_status()

        return res.json()

    def _token(self) -> str:
        now = time.time()
        if self._access_token and now < self._expires_at - 30:
            return self._access_token

        auth_b64 = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()

        res = requests.post(
            self.AUTH_URL,
            data={"grant_type": "client_credentials"},
            headers={"Authorization": f"Basic {auth_b64}"}
        )
        res.raise_for_status()
        data = res.json()

        self._access_token = data["access_token"]
        self._expires_at = now + data["expires_in"]  # usually 3600 seconds

        return self._access_token

    def refresh_token(self) -> None:
        self._access_token = None
        self._expires_at   = 0