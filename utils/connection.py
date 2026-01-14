from json import load
import sqlite3
import logging

CONNECTION = None
CURSOR = None



def open_connection(db_path):
    global CONNECTION, CURSOR
    try: 
        CONNECTION = sqlite3.connect(db_path)
        CURSOR = CONNECTION.cursor()
        logging.info(f"Connessione al database {db_path} aperta con successo.")
        return CONNECTION, CURSOR, load_tags
    except Exception as e:
        logging.error(f"Errore di connessione al database: {e}")
        return None, None, None

def close_connection(connection):
    if connection:
        connection.close()
        logging.info("Connessione al database chiusa.")

def load_tags() -> list:
    """Carica i TAG dei giocatori dal database."""
    try:
        CURSOR.execute("SELECT player_tag FROM players -- WHERE player_name IS NULL")
        rows = CURSOR.fetchall()
        return [row[0] for row in rows]
    except Exception as e:
        print(f"Errore durante il caricamento dei tag: {e}")
        return []