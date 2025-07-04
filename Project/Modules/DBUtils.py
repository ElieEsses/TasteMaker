import sqlite3 as sq3
import sqlalchemy
from sqlalchemy import create_engine
import pandas as pd
from typing import Union

class DBUtils:
    @staticmethod
    def create_sqlite_conn(
        db_path: str, 
        init_sql_path: str = None
    ) -> sq3.Connection:
        conn = sq3.connect(db_path)
        
        if init_sql_path:
            try:
                with open(init_sql_path, 'r') as sql_file:
                    sql_script = sql_file.read()
                
                cursor = conn.cursor()
                cursor.executescript(sql_script)
                conn.commit()
            except FileNotFoundError:
                print(f"[ERROR] SQL init file not found: {init_sql_path}")
            except sq3.OperationalError as e:
                print(f"[SQL ERROR] Failed to execute SQL script: {e}")
            except Exception as e:
                print(f"[ERROR] Unexpected error during SQL init: {e}")
        
        return conn
    
    @staticmethod
    def close_sqlite_conn(
        conn: sq3.Connection, 
        commit: bool = False
    ) -> None:
        if commit:
            conn.commit()
        conn.close()
    
    @staticmethod
    def create_postgres_conn(
        user: str, 
        password: str, 
        host: str, 
        port: int, 
        db: str
    ) -> sqlalchemy.Engine:
        try:
            conn_str = f"postgresql://{user}:{password}@{host}:{port}/{db}"
            engine = create_engine(conn_str)
        except sqlalchemy.exc.SQLAlchemyError as e:
            raise RuntimeError(f"Failed to create Postgres engine: {e}") from e
        
        return engine
    
    @staticmethod
    def close_postgres_conn(conn: sqlalchemy.Engine) -> None:
        conn.dispose()

    @staticmethod
    def df_to_table(
        df: pd.DataFrame, 
        conn: Union[sq3.Connection, sqlalchemy.Engine], 
        table_name: str, 
        if_exists: str = "replace"
    ) -> None:
        df.to_sql(table_name, conn, if_exists="replace", index=False)

    @staticmethod
    def table_to_df(
        conn: Union[sq3.Connection, sqlalchemy.Engine], 
        table_name: str
    ) -> pd.DataFrame:
        try:
            return pd.read_sql(f"SELECT * FROM {table_name}", conn)
        except Exception as e:
            raise RuntimeError(f"Failed to read table '{table_name}': {e}") from e
    
    @staticmethod
    def query_db(
        conn: Union[sq3.Connection, sqlalchemy.Engine], 
        query: str, 
        params: tuple = ()
    ) -> pd.DataFrame:
        try:
            return pd.read_sql(query, conn, params=params)
        except Exception as e:
            raise RuntimeError(f"Failed to execute query: {e}") from e

    @staticmethod
    def sqlite_to_postgres(
        tables: Union[list[str], dict[str, str]],
        sqlite_conn: sq3.Connection,
        pg_conn: sqlalchemy.Engine,
        if_exists: str = "replace"
    ) -> None:
        # if tables is given as list, made into dict
        if isinstance(tables, list):
            tables = {name: name for name in tables}

        for sqlite_table, pg_table  in tables.items():
            try:
                df = DBUtils.table_to_df(sqlite_conn, sqlite_table)
                DBUtils.df_to_table(df, pg_conn, pg_table)
                print(f"[INFO] Transferred '{sqlite_table}' -> '{pg_table}'")
            except Exception as e:
                raise RuntimeError(f"Failed to transfer '{sqlite_table}' to '{pg_table}': {e}") from e
    
    @staticmethod
    def postgres_to_sqlite(
        tables: Union[list[str], dict[str, str]],
        pg_conn: sqlalchemy.Engine,
        sqlite_conn: sq3.Connection,
        if_exists: str = "replace"
    ) -> None:
        if isinstance(tables, list):
            tables = {name: name for name in tables}

        for pg_table, sqlite_table in tables.items():
            try:
                df = DBUtils.table_to_df(pg_conn, pg_table)
                DBUtils.df_to_table(df, sqlite_conn, sqlite_table)
                print(f"[INFO] Transferred '{pg_table}' -> '{sqlite_table}'")
            except Exception as e:
                raise RuntimeError(f"Failed to transfer '{pg_table}' to '{sqlite_table}': {e}") from e
    
    @staticmethod
    def get_sqlite_tables(conn: sq3.Connection) -> list[str]:
        cursor = conn.cursor()
        result = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [row[0] for row in result.fetchall()]
    
    @staticmethod
    def get_postgres_tables(
        conn: sqlalchemy.Engine, 
        schema: str = "public"
    ) -> list[str]:
        query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = %s
            AND table_type = 'BASE TABLE';
        """
        try:
            df = pd.read_sql(query, conn, params=(schema,))
            return df["table_name"].tolist()
        except Exception as e:
            raise RuntimeError(f"Failed to fetch Postgres tables from schema '{schema}': {e}") from e