import os
import pandas as pd
import musicbrainzngs as mb
import pickle
from StreamingClients.SpotifyClient import SpotifyClient
from Recommenders.BasicCooccurrence import BasicCooccurrence
from DataHandler import DataHandler
from Modules.DBUtils import DBUtils
import sqlite3 as sq3
from typing import Optional, Dict, List
from scipy.sparse import load_npz
from Factorizers.NMF_Factorizer import NMF_Factorizer
from Factorizers.SVD_Factorizer import SVD_Factorizer
from Clusterers.DBSCAN_Clusterer import DBSCAN_Clusterer
from Clusterers.KMeans_Clusterer import KMeans_Clusterer
from Recommenders.CosSim import CosSim
from Recommenders.BasicCooccurrence import BasicCooccurrence
from RefactorAndCluster import RefactorAndCluster
from SparseMatrixBuilder import SparseMatrixBuilder



from dotenv import load_dotenv
load_dotenv()

DB_PATH = "Project/Data/taste_maker.db"
EMBEDDINGS_PATH = "/Users/elieesses/Desktop/Programming/TasteMaker/Project/Data/song_SVD_embeddings_100d.pkl"
ID_INDEX = "/Users/elieesses/Desktop/Programming/TasteMaker/Project/Data/song_id_index.csv"

def main():
    db_conn = sq3.connect(DB_PATH)
    data_hander = DataHandler(db_conn)

    matrix_builder = SparseMatrixBuilder(db_conn, 'spotify_playlist_tracks')
    # matrix_builder.build()
    # matrix_builder.save_matrix('Project/Data/playlist_song_sparse_matrix.npz')

    sparse = matrix_builder.load_matrix('Project/Data/playlist_song_sparse_matrix.npz')

    factorizer = SVD_Factorizer(n_components=6000)
    embeddings = factorizer.fit_transform(sparse)
    factorizer.save('Project/Data/playlist_song_embeddings.joblib')

    # print(data_hander.get_id_from_song("dirty paws", "of monsters and men"))

    # dirty_paws = 5470

    # recommender = BasicCooccurrence(db_conn)
    # recommender.recommend(5470)

    # for rec in recs:
    #     print(rec)

    # spotify_client = SpotifyClient(os.getenv("SPOTIFY_CLIENT_ID"), os.getenv("SPOTIFY_CLIENT_SECRET"), os.getenv("SPOTIFY_REDIRECT_URI"))


   

if __name__ == "__main__":
    main()