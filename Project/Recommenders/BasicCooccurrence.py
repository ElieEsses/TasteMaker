from typing import List, Dict
import sqlite3 as sq3
from Recommenders.Recommender import Recommender

class BasicCooccurrence(Recommender):
    def __init__(self, db_conn: sq3.Connection):
        self.db_conn = db_conn

    def recommend(self, song_id, limit:int = 10, filter_same_artirst = False, filter_popular = False, popularity_cutoff = 10000, offset = 300) -> List[Dict]:
        artist_filter = "AND s.artist != seed.artist" if filter_same_artirst else ""
        popularity_filer = f"AND oc.overall_freq <= {popularity_cutoff}" if filter_popular else ""
        query = f"""
        WITH seed_song AS (
            SELECT artist
            FROM spotify_songs
            WHERE id = ?
        ),
        target_playlists AS (
            SELECT playlist_id
            FROM spotify_playlist_tracks
            WHERE song_id = ?
        ),
        co_occurrence AS (
            SELECT pt.song_id,
                COUNT(*) AS freq
            FROM spotify_playlist_tracks pt
            JOIN target_playlists tp ON tp.playlist_id = pt.playlist_id
            WHERE pt.song_id != ?
            GROUP BY pt.song_id
        ),
        overall_counts AS (
            SELECT song_id,
            COUNT(DISTINCT playlist_id) AS overall_freq
            FROM spotify_playlist_tracks
            GROUP BY song_id
        )
        SELECT
            s.id,
            s.title,
            s.artist,
            co.freq AS cooccurrence_freq,
            oc.overall_freq,
            (1.0 * co.freq) / (oc.overall_freq + {offset}) AS rec_strength
        FROM co_occurrence co
        JOIN overall_counts oc ON co.song_id = oc.song_id
        JOIN spotify_songs s    ON s.id = co.song_id
        JOIN seed_song seed     ON 1=1
        WHERE 1=1
            {artist_filter}
            {popularity_filer}
        ORDER BY rec_strength DESC
        LIMIT ?;
        """

        cursor = self.db_conn.cursor()
        cursor.execute(query, (song_id, song_id, song_id, limit))
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return results