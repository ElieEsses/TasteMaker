import os
import pandas as pd
from StreamingClients.SpotifyClient import SpotifyClient
from Modules.DBUtils import DBUtils

from dotenv import load_dotenv
load_dotenv()

db_utils = DBUtils()
sqlite_conn = db_utils.create_sqlite_conn("Project/Data/taste-maker.db")
features_df = db_utils.table_to_df(sqlite_conn, "audio_features")

def main():
    spotify_client = SpotifyClient(
        os.getenv("SPOTIFY_CLIENT_ID"), 
        os.getenv("SPOTIFY_CLIENT_SECRET"),
        os.getenv("SPOTIFY_REDIRECT_URI")
    )

    top_tracks = spotify_client.get_top_tracks(50, time_range="medium_term")
    
    for key, value in top_tracks[0].items():
        print(f"{key}: {value}")




if __name__ == "__main__":
    main()