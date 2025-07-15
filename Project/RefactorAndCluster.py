import pandas as pd
import numpy as np
import sqlite3
from scipy.sparse import coo_matrix, save_npz
from tqdm import tqdm
import joblib

class RefactorAndCluster:
    def __init__(self, db_path,
                 factorizer, clusterer,
                 matrix_path="song_playlist_matrix.npz",
                 embedding_path="song_embeddings.pkl",
                 song_index_path="song_id_index.csv",
                 cluster_table="song_clusters"):
        self.db_path = db_path
        self.factorizer = factorizer
        self.clusterer = clusterer
        self.matrix_path = matrix_path
        self.embedding_path = embedding_path
        self.song_index_path = song_index_path
        self.cluster_table = cluster_table

        self.matrix = None
        self.embeddings = None
        self.labels = None
        self.song_ids = None

    def build_sparse_matrix(self):
        print("🔗 Connecting to DB...")
        conn = sqlite3.connect(self.db_path)

        print("📥 Loading playlist-track data...")
        df = pd.read_sql("SELECT playlist_id, song_id FROM spotify_playlist_tracks", conn)

        print("🎛️ Building index maps...")
        unique_song_ids = df['song_id'].unique()
        unique_playlist_ids = df['playlist_id'].unique()

        song_id_to_idx = {sid: i for i, sid in enumerate(unique_song_ids)}
        playlist_id_to_idx = {pid: i for i, pid in enumerate(unique_playlist_ids)}

        print("🧱 Building sparse matrix...")
        row_indices = df['song_id'].map(song_id_to_idx).values
        col_indices = df['playlist_id'].map(playlist_id_to_idx).values
        data = np.ones(len(df), dtype=np.int8)

        matrix = coo_matrix((data, (row_indices, col_indices)),
                            shape=(len(song_id_to_idx), len(playlist_id_to_idx)))

        self.matrix = matrix.tocsr()
        self.song_ids = pd.Series(unique_song_ids)

        # Save to disk
        save_npz(self.matrix_path, self.matrix)
        self.song_ids.to_csv(self.song_index_path, index=False)
        print("✅ Sparse matrix and song index saved.")

        conn.close()

    def factorize(self):
        print("🧠 Running factorization...")
        self.embeddings = self.factorizer.fit_transform(self.matrix)
        joblib.dump(self.embeddings, self.embedding_path)
        print("💾 Embeddings saved.")

    def cluster(self):
        print("🧬 Running clustering...")
        self.labels = self.clusterer.fit_predict(self.embeddings)

    def save_clusters_to_sqlite(self):
        print("💾 Saving clusters to DB...")
        cluster_df = pd.DataFrame({
            "song_id": self.song_ids,
            "cluster": self.labels
        })

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.cluster_table} (
                song_id INTEGER PRIMARY KEY,
                cluster INTEGER
            );
        """)

        insert_sql = f"""
            INSERT INTO {self.cluster_table} (song_id, cluster)
            VALUES (?, ?)
            ON CONFLICT(song_id) DO UPDATE SET cluster=excluded.cluster;
        """

        for _, row in tqdm(cluster_df.iterrows(), total=len(cluster_df), desc="Updating clusters"):
            cursor.execute(insert_sql, (int(row["song_id"]), int(row["cluster"])))

        conn.commit()
        conn.close()
        print("✅ Clusters saved to SQLite.")

    def run(self):
        self.build_sparse_matrix()
        self.factorize()
        self.cluster()
        self.save_clusters_to_sqlite()