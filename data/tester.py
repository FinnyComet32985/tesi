import sys
import os

from classifier import get_player_profiles

sys.path.append(os.path.join(os.path.dirname(__file__), '../utils'))

from connection import open_connection, close_connection

from test_extreme_matchup import get_extreme_matchup_stats
from test_odds_and_quitrate_correlation import calculate_correlation_pity_ragequit
from ragequit_and_odds import ragequit_and_odds_correlation
from reporter import generate_report


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
    profiles = get_player_profiles(cursor, tags)

    # raccolta statistiche matchup
    matchup_stats = get_extreme_matchup_stats(cursor, tags)

    # calcolo correlazione tra odds ratio e ragequit
    correlation_results = calculate_correlation_pity_ragequit(profiles, matchup_stats)

    # generazione report e salvataggio
    generate_report(profiles, matchup_stats, correlation_results)

    ragequit_and_odds_correlation(profiles, matchup_stats) 


    print("Processo di report completato.")

    close_connection(connection)

if __name__ == "__main__":
    main()
