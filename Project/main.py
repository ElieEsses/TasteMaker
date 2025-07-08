import os
import pandas as pd
import musicbrainzngs as mb
from StreamingClients.SpotifyClient import SpotifyClient
from Modules.DBUtils import DBUtils
import sqlite3


from dotenv import load_dotenv
load_dotenv()

# db_utils = DBUtils()
# sqlite_conn = db_utils.create_sqlite_conn("Project/Data/taste-maker.db")
# features_df = db_utils.table_to_df(sqlite_conn, "audio_features")

con = sqlite3.connect("Project/Data/taste_maker.db")  

def main():
    spotify_client = SpotifyClient(
        os.getenv("SPOTIFY_CLIENT_ID"), 
        os.getenv("SPOTIFY_CLIENT_SECRET"),
        os.getenv("SPOTIFY_REDIRECT_URI")
    )

    top_tracks = spotify_client.get_top_tracks(50, time_range="medium_term")
    
    for track in top_tracks:
        row = fetch_track(con, track['artists'][0]['name'], track['name'])

        if not row.empty:
            print(row)
        else:
            print(f"Track not found in database: {track['name']} by {track['artists'][0]['name']}")





def get_mbid_from_isrc(isrc):
    mb.set_useragent(
        "TasteaMaker",        # app name
        "0.1",               # version
        "elieesses04@gmail.com"   # contact (can be blank but recommended)
    )

    res = mb.get_recordings_by_isrc(isrc)

    mbids = [rec["id"] for rec in res["isrc"]["recording-list"]]

    return mbids[0] if mbids else None

def fetch_track(con, artist, title):
    sql = """
    SELECT *
      FROM features_lastfm
     WHERE artist = ?  COLLATE NOCASE
       AND title  = ? COLLATE NOCASE
     LIMIT 1;
    """
    return pd.read_sql_query(sql, con, params=(artist, title))


# isrc = "USUM71800057"
# mbid = get_mbid_from_isrc(isrc)





if __name__ == "__main__":
    main()