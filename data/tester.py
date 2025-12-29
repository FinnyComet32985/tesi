import sys
import os

from classifier import classifier

sys.path.append(os.path.join(os.path.dirname(__file__), '../utils'))

from connection import open_connection, close_connection

from test_extreme_matchup import test_extreme_matchup


def load_tags(cursor) -> list:
    """Carica i TAG dei giocatori dal database."""
    try:
        cursor.execute("SELECT player_tag FROM players")
        rows = cursor.fetchall()
        return [row[0] for row in rows]
    except Exception as e:
        print(f"Errore durante il caricamento dei tag: {e}")
        return []

def main():
    connection, cursor = open_connection("db/clash.db")

    tags = load_tags(cursor)

    # raccolta dei dati utili per la classificazione del player
    classifier(cursor, tags)


    test_extreme_matchup(cursor, tags)




    close_connection(connection)

if __name__ == "__main__":
    main()



