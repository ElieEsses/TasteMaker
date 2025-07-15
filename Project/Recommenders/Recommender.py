from abc import ABC, abstractmethod
from typing import List, Dict
import sqlite3 as sq3

class Recommender(ABC):
    def __init__(self, db_conn: sq3.Connection, top_songs: List[Dict], limit: int):
        self.top_songs = top_songs
        self.db_conn = db_conn
        self.limit = limit

    @abstractmethod
    def recommend(self) -> List[Dict]:
        """Subclasses must implement this to return a list of song recommendations."""
        pass