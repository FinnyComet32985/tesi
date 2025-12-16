import sqlite3
import logging

def open_connection(db_path):
    try: 
        CONNECTION = sqlite3.connect(db_path)
        CURSOR = CONNECTION.cursor()
        logging.info(f"Connessione al database {db_path} aperta con successo.")
        return CONNECTION, CURSOR
    except Exception as e:
        logging.error(f"Errore di connessione al database: {e}")
        return None, None

def close_connection(connection):
    if connection:
        connection.close()
        logging.info("Connessione al database chiusa.")