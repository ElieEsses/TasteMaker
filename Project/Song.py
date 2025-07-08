class Song:
    def __init__(self, id, name, artist, album, duration_ms, popularity):
        self.spotify_id = id
        self.isrc: str = None
        self.mdid: str = None