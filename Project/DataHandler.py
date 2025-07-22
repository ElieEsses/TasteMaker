import sqlite3 as sq3
from typing import Optional
from operator import itemgetter
from tqdm import tqdm

class DataHandler:
    def __init__(self, db_conn: sq3.Connection):
        self.db_conn = db_conn
        self.cursor = self.db_conn.cursor()

    def get_id_from_song(self, title: str, artist: str) -> Optional[int]:
        cursor = self.db_conn.cursor()

        # try exact match (case-insensitive)
        exact_query = """
        SELECT id
        FROM spotify_songs
        WHERE LOWER(title) = LOWER(?) AND LOWER(artist) = LOWER(?)
        LIMIT 1;
        """
        cursor.execute(exact_query, (title, artist))
        result = cursor.fetchone()
        if result:
            return result[0]

        # try fuzzy match using LIKE
        fuzzy_query = """
        SELECT id
        FROM spotify_songs
        WHERE LOWER(title) LIKE '%' || LOWER(?) || '%'
          AND LOWER(artist) LIKE '%' || LOWER(?) || '%'
        LIMIT 1;
        """
        cursor.execute(fuzzy_query, (title, artist))
        result = cursor.fetchone()
        if result:
            return result[0]

        # if nothing found
        return None
    
    def get_distinct_top_songs(self, *rec_lists, limit:int = 5):
        combined = []
        seen_artists = set()
        top_recs = []

        # Step 1: Guarantee at least one from each list
        for rec_list in rec_lists:
            sorted_list = sorted(rec_list, key=itemgetter("rec_strength"), reverse=True)
            for song in sorted_list:
                if song["artist"] not in seen_artists:
                    top_recs.append(song)
                    seen_artists.add(song["artist"])
                    break  # stop after finding 1 from this list

        # Step 2: Fill in the rest from all lists combined
        combined = [song for rec_list in rec_lists for song in rec_list]
        combined_sorted = sorted(combined, key=itemgetter("rec_strength"), reverse=True)

        for song in combined_sorted:
            if song["artist"] not in seen_artists:
                top_recs.append(song)
                seen_artists.add(song["artist"])
            if len(top_recs) == limit:
                break

        return top_recs
    
    def playlist_exists(self, playlist_uri):
        self.cursor.execute("SELECT 1 FROM spotify_playlists WHERE playlist_uri = ?", (playlist_uri,))
        return self.cursor.fetchone() is not None

    def song_exists(self, spotify_uri):
        self.cursor.execute("SELECT 1 FROM spotify_songs WHERE spotify_uri = ?", (spotify_uri,))
        return self.cursor.fetchone() is not None

    def insert_playlist(self, playlist):
        self.cursor.execute("""
            INSERT INTO spotify_playlists (playlist_uri, name, num_tracks)
            VALUES (?, ?, ?)
        """, (playlist["uri"], playlist["name"], playlist["tracks"]["total"]))
        return self.cursor.lastrowid

    def insert_song(self, track):
        self.cursor.execute("""
            INSERT INTO spotify_songs (spotify_uri, title, artist, album)
            VALUES (?, ?, ?, ?)
        """, (
            track["uri"],
            track["name"],
            ', '.join([a["name"] for a in track["artists"]]),
            track["album"]["name"]
        ))
        return self.cursor.lastrowid

    def get_playlist_id_from_uri(self, playlist_uri):
        self.cursor.execute("SELECT playlist_id FROM spotify_playlists WHERE playlist_uri = ?", (playlist_uri,))
        return self.cursor.fetchone()[0]

    def get_song_id_from_uri(self, spotify_uri):
        self.cursor.execute("SELECT id FROM spotify_songs WHERE spotify_uri = ?", (spotify_uri,))
        return self.cursor.fetchone()[0]
    
    def ingest_user_playlists(self, spotify_client, limit: int = 50):
        playlists = spotify_client.get_all_playlists(limit=limit)

        for playlist in tqdm(playlists, desc="📝 Processing playlists"):
            playlist_uri = playlist["uri"]
            playlist_name = playlist["name"]
            playlist_total = playlist["tracks"]["total"]

            # Insert or get playlist ID
            if self.playlist_exists(playlist_uri):
                playlist_id = self.get_playlist_id(playlist_uri)
            else:
                playlist_id = self.insert_playlist(playlist)

            # Fetch cleaned tracks
            track_items = spotify_client.get_playlist_tracks(playlist["id"])

            for track in track_items:
                if not track or not track.get("id") or not track.get("name"):
                    continue

                # Construct song info
                song_uri = f"spotify:track:{track['id']}"
                title = track["name"]
                artist = ', '.join(track["artists"])
                album = track["album"]

                # Insert or get song ID
                if self.song_exists(song_uri):
                    song_id = self.get_song_id(song_uri)
                else:
                    self.cursor.execute("""
                        INSERT INTO spotify_songs (spotify_uri, title, artist, album)
                        VALUES (?, ?, ?, ?)
                    """, (song_uri, title, artist, album))
                    song_id = self.cursor.lastrowid

                # Insert playlist-song mapping
                self.cursor.execute("""
                    INSERT OR IGNORE INTO spotify_playlist_tracks (playlist_id, song_id)
                    VALUES (?, ?)
                """, (playlist_id, song_id))

        self.db_conn.commit()