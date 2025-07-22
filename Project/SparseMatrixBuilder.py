import sqlite3
import json
import os
from scipy.sparse import csr_matrix, save_npz, load_npz


class SparseMatrixBuilder:
    def __init__(self, db_path, table_name):
        self.db_path = db_path
        self.table_name = table_name
        self.playlist_to_idx = {}
        self.song_to_idx = {}
        self.idx_to_playlist = {}
        self.idx_to_song = {}
        self.matrix = None

    def build(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(f"SELECT playlist_id, song_id FROM {self.table_name}")
        data = cursor.fetchall()
        conn.close()

        playlists = sorted(set(row[0] for row in data))
        songs = sorted(set(row[1] for row in data))

        # Map playlists to columns, songs to rows
        self.playlist_to_idx = {pid: idx for idx, pid in enumerate(playlists)}
        self.song_to_idx = {sid: idx for idx, sid in enumerate(songs)}
        self.idx_to_playlist = {idx: pid for pid, idx in self.playlist_to_idx.items()}
        self.idx_to_song = {idx: sid for sid, idx in self.song_to_idx.items()}

        rows = [self.song_to_idx[sid] for pid, sid in data]
        cols = [self.playlist_to_idx[pid] for pid, sid in data]
        vals = [1] * len(rows)

        # Matrix is songs (rows) x playlists (columns)
        self.matrix = csr_matrix((vals, (rows, cols)),
                                shape=(len(songs), len(playlists)))
        return self.matrix

    def save_matrix(self, path):
        if self.matrix is None:
            raise ValueError("Matrix has not been built yet.")
        save_npz(path, self.matrix)

    @staticmethod
    def load_matrix(path):
        return load_npz(path)

    def save_mappings(self, path_prefix):
        mappings = {
            "playlist_to_idx": self.playlist_to_idx,
            "song_to_idx": self.song_to_idx
        }
        with open(f"{path_prefix}_mappings.json", "w") as f:
            json.dump(mappings, f)

    def load_mappings(self, path_prefix):
        with open(f"{path_prefix}_mappings.json", "r") as f:
            mappings = json.load(f)
        self.playlist_to_idx = {int(k): v for k, v in mappings["playlist_to_idx"].items()}
        self.song_to_idx = {int(k): v for k, v in mappings["song_to_idx"].items()}
        self.idx_to_playlist = {v: k for k, v in self.playlist_to_idx.items()}
        self.idx_to_song = {v: k for k, v in self.song_to_idx.items()}