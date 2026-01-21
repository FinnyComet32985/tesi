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
from test_veloci import analyze_pity_odds_vs_total_matches, analyze_pity_odds_vs_current_trophies
from test_session_trend import analyze_session_trends
from test import (
    analyze_std_correlation,
    analyze_session_pity,
    analyze_extreme_matchup_streak,
    analyze_confounding_factors,
    analyze_time_matchup_stats,
    analyze_deck_switch_impact,
    analyze_ers_pity_hypothesis,
    analyze_return_matchups_vs_ers,
    analyze_pity_impact_on_session_length,
    analyze_pity_impact_on_return_time,
    analyze_churn_probability_vs_pity,
    analyze_cannon_fodder,
    analyze_dangerous_sequences,
    analyze_short_session_bonus,
    analyze_matchup_markov_chain,
    analyze_return_after_bad_streak,
    analyze_debt_extinction,
)
from test_matchup_no_lvl import analyze_matchup_no_lvl_stats

def main():
    connection, cursor, load_tags = open_connection("db/clash.db")
    
    tags = load_tags()

    mode_filter = 'Ladder'

    # Caricamento sessioni e profili tramite battlelog_v2
    # Questo assicura che le sessioni siano definite consistentemente
    players_sessions = get_players_sessions(mode_filter, exclude_unreliable=True)

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
    analyze_return_matchups_vs_ers(players_sessions, output_dir=results_dir)
    analyze_pity_impact_on_session_length(players_sessions, output_dir=results_dir)
    analyze_pity_impact_on_return_time(players_sessions, output_dir=results_dir)
    analyze_churn_probability_vs_pity(players_sessions, matchup_stats, output_dir=results_dir)
    analyze_session_trends(players_sessions, output_dir=results_dir)
    analyze_cannon_fodder(players_sessions, output_dir=results_dir)
    analyze_dangerous_sequences(players_sessions, output_dir=results_dir)
    analyze_matchup_no_lvl_stats(players_sessions, output_dir=results_dir)
    analyze_short_session_bonus(players_sessions, output_dir=results_dir)
    analyze_matchup_markov_chain(players_sessions, output_dir=results_dir)
    analyze_return_after_bad_streak(players_sessions, output_dir=results_dir)
    analyze_debt_extinction(players_sessions, output_dir=results_dir)

    # --- TEST VELOCI ---
    analyze_pity_odds_vs_total_matches(profiles, matchup_stats)
    if mode_filter == 'Ladder':
        analyze_pity_odds_vs_current_trophies(profiles, matchup_stats, cursor)

    print("Processo di report completato.")

    close_connection(connection)

if __name__ == "__main__":
    main()
