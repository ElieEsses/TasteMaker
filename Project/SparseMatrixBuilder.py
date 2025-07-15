import sqlite3
from scipy.sparse import csr_matrix, save_npz, load_npz
import os


class SparseMatrixBuilder:
    def __init__(self, db_conn, table_name:str = 'spotify_playlist_tracks'):
        self.db_conn = db_conn
        self.table_name = table_name
        self.playlist_to_idx = {}
        self.song_to_idx = {}
        self.matrix = None

    def build(self):
        conn = self.db_conn
        cursor = conn.cursor()

        cursor.execute(f"SELECT playlist_id, song_id FROM {self.table_name}")
        data = cursor.fetchall()
        conn.close()

        playlists = sorted(set(row[0] for row in data))
        songs = sorted(set(row[1] for row in data))

        self.playlist_to_idx = {pid: idx for idx, pid in enumerate(playlists)}
        self.song_to_idx = {sid: idx for idx, sid in enumerate(songs)}

        rows = [self.playlist_to_idx[pid] for pid, sid in data]
        cols = [self.song_to_idx[sid] for pid, sid in data]
        vals = [1] * len(rows)

        self.matrix = csr_matrix((vals, (rows, cols)),
                                 shape=(len(playlists), len(songs)))
        return self.matrix

    def save_matrix(self, path):
        if self.matrix is None:
            raise ValueError("Matrix has not been built yet.")
        save_npz(path, self.matrix)

    @staticmethod
    def load_matrix(path):
        return load_npz(path)
