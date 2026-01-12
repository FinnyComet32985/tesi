import sys
import os

# from classifier import get_player_profiles # Removed, using battlelog_v2

sys.path.append(os.path.join(os.path.dirname(__file__), '../utils'))

from battlelog_v2 import get_players_sessions
from connection import open_connection, close_connection

from test_extreme_matchup import get_extreme_matchup_stats
from test_odds_and_quitrate_correlation import calculate_correlation_pity_ragequit
from ragequit_and_odds import ragequit_and_odds_correlation
from test_indipendenza import get_chi2_independence_stats
from test_gatekeeping import get_gatekeeping_stats # Importazione nuovo test
from reporter import generate_report
from test import (
    analyze_std_correlation,
    analyze_session_pity,
    analyze_extreme_matchup_streak,
    analyze_confounding_factors,
    analyze_time_matchup_stats,
    analyze_deck_switch_impact,
    analyze_ers_pity_hypothesis
)

def main():
    connection, cursor, load_tags = open_connection("db/clash.db")
    
    tags = load_tags()

    # Caricamento sessioni e profili tramite battlelog_v2
    # Questo assicura che le sessioni siano definite consistentemente
    players_sessions = get_players_sessions(mode_filter='Ladder_Ranked')

    # Definizione cartella risultati
    results_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(results_dir, exist_ok=True)

    # raccolta dei dati utili per la classificazione del player
    # Ricostruiamo il dizionario profiles per compatibilità con reporter.py
    profiles = {p['tag']: p['profile'] for p in players_sessions if p['profile']}

    # raccolta statistiche matchup
    matchup_stats = get_extreme_matchup_stats(players_sessions)

    # calcolo correlazione tra odds ratio e ragequit
    correlation_results = calculate_correlation_pity_ragequit(profiles, matchup_stats)

    # calcolo chi quadro indipendenza (streak vs matchup)
    chi2_results = get_chi2_independence_stats(players_sessions)

    # calcolo gatekeeping (danger zone vs hard counter)
    gatekeeping_results = get_gatekeeping_stats(cursor, tags, danger_range=50)

    # generazione report e salvataggio
    generate_report(profiles, matchup_stats, correlation_results, chi2_results, gatekeeping_results)

    ragequit_and_odds_correlation(profiles, matchup_stats) 

    # Esecuzione test aggiuntivi da test.py
    print("\nEsecuzione test aggiuntivi (Sessioni, Streak, Fattori Confondenti)...")
    analyze_std_correlation(players_sessions, output_dir=results_dir)
    analyze_session_pity(players_sessions, output_dir=results_dir)
    analyze_extreme_matchup_streak(players_sessions, output_dir=results_dir)
    analyze_confounding_factors(players_sessions, output_dir=results_dir)
    analyze_time_matchup_stats(players_sessions, output_dir=results_dir)
    analyze_deck_switch_impact(players_sessions, output_dir=results_dir)
    analyze_ers_pity_hypothesis(profiles, matchup_stats, output_dir=results_dir)

    print("Processo di report completato.")

    close_connection(connection)

if __name__ == "__main__":
    main()
