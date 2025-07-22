from typing import List, Dict
import sqlite3 as sq3
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from Recommenders.Recommender import Recommender


class CosSim(Recommender):
    def __init__(self, 
                 db_conn: sq3.Connection, 
                 embeddings_path: str, 
                 song_id_index_path: str):
        if not os.path.exists(embeddings_path):
            raise FileNotFoundError(f"Embeddings file not found at {embeddings_path}")
        if not os.path.exists(song_id_index_path):
            raise FileNotFoundError(f"Song ID index file not found at {song_id_index_path}")

        self.db_conn = db_conn

        # Load embeddings
        self.song_embeddings = joblib.load(embeddings_path)

        # Normalize embeddings for cosine similarity
        norms = np.linalg.norm(self.song_embeddings, axis=1, keepdims=True)
        self.song_embeddings = self.song_embeddings / (norms + 1e-10)

        # Load song id index mapping (embedding index → spotify_songs.id)
        self.id_mapping = pd.read_csv(song_id_index_path, header=None).squeeze().tolist()


    def recommend(self, 
                  song_id: int, 
                  limit: int = 10, 
                  filter_same_artist: bool = False, 
                  offset: int = 0) -> List[Dict]:

        # Map DB song_id → embedding index
        try:
            embedding_index = self.id_mapping.index(song_id)
        except ValueError:
            raise ValueError(f"Song ID {song_id} not found in embedding index mapping.")
        
        # Cosine similarity search
        query_vector = self.song_embeddings[embedding_index].reshape(1, -1)
        similarities = cosine_similarity(query_vector, self.song_embeddings).flatten()
        similarities[embedding_index] = -np.inf  # exclude self

        # Get top indices in embedding space
        top_indices = np.argpartition(-similarities, offset + limit)[offset:offset + limit]
        top_indices = top_indices[np.argsort(-similarities[top_indices])]

        # Map back to DB song IDs
        db_song_ids = [self.id_mapping[idx] for idx in top_indices]

        songs = self._get_song_metadata(db_song_ids)

        results = []
        for idx, song in zip(top_indices, songs):
            if filter_same_artist and song['artist'] == self._get_artist(song_id):
                continue
            results.append({
                'song_id': song['song_id'],
                'title': song['title'],
                'artist': song['artist'],
                'similarity': float(similarities[idx])
            })
            if len(results) >= limit:
                break

        return results


    def _get_song_metadata(self, song_ids: List[int]) -> List[Dict]:
        placeholders = ','.join('?' for _ in song_ids)
        query = f"""
            SELECT id, title, artist
            FROM spotify_songs
            WHERE id IN ({placeholders})
        """
        cursor = self.db_conn.execute(query, song_ids)
        rows = cursor.fetchall()
        return [{'song_id': row[0], 'title': row[1], 'artist': row[2]} for row in rows]


    def _get_artist(self, song_id: int) -> str:
        query = "SELECT artist FROM spotify_songs WHERE id = ?"
        cursor = self.db_conn.execute(query, (song_id,))
        row = cursor.fetchone()
        return row[0] if row else ""