import logging
from utils.connection import open_connection, close_connection
from db_manager import load_tags
from player_updater import update_player_profile
from battle_updater import fetch_all_battles
import time

DB_PATH = "db/clash.db"

def main():
    """
    Ciclo principale che inizializza la connessione al DB,
    carica i tag dei giocatori e avvia il processo di aggiornamento
    per profili e battaglie.
    """
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    conn, cursor = open_connection(DB_PATH)
    if not conn:
        logging.critical("Impossibile connettersi al database. Uscita.")
        return

    tags = load_tags(cursor)
    if not tags:
        logging.warning("Nessun tag giocatore trovato nel database.")
    else:
        for tag in tags:
            update_player_profile(tag, conn, cursor)
            fetch_all_battles(tag, conn, cursor)

    close_connection(conn)
    logging.info("Processo di fetching completato.")
    time.sleep(20 * 60)


if __name__ == "__main__":
    while True:
        main()