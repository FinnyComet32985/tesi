import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../utils'))

from battlelog_v2 import get_players_sessions
from connection import open_connection, close_connection

from test_extreme_matchup import get_extreme_matchup_stats
from test_odds_and_quitrate_correlation import calculate_correlation_pity_ragequit
from ragequit_and_odds import ragequit_and_odds_correlation
from test_indipendenza import get_chi2_independence_stats
from test_gatekeeping import analyze_gatekeeping_all
from reporter import generate_report
from test_veloci import analyze_pity_odds_vs_total_matches, analyze_pity_odds_vs_current_trophies
from test_session_trend import analyze_session_trends
from test import (
    analyze_std_correlation,
    analyze_session_pity,
    analyze_extreme_matchup_streak,
    analyze_ers_pity_hypothesis,
    analyze_return_matchups_vs_ers,
    analyze_pity_impact_on_session_length,
    analyze_pity_impact_on_return_time,
    analyze_churn_probability_vs_pity,
    analyze_cannon_fodder,
    analyze_dangerous_sequences,
    analyze_short_session_bonus,
    analyze_markov_chains,
    analyze_return_after_bad_streak,
    analyze_defeat_quality_impact,
    analyze_punishment_tradeoff,
    analyze_extreme_level_streak,
    analyze_normalized_level_streak,
    analyze_pity_probability_lift,
    analyze_paywall_impact,
    analyze_nolvl_streaks_vs_trophies,
    analyze_meta_ranges,
    analyze_climbing_impact,
    analyze_hook_by_trophy_range,
    analyze_skill_vs_matchup_dominance,
    analyze_debt_credit_combined,
    analyze_debt_initial_progression,
    analyze_residual_level_diff_debt
) # analyze_time_stats is in test.py but it is a duplicate of a function in test_time_analysis.py
from test_confounding import analyze_confounding_variables
from test_time_analysis import analyze_time_stats
from test_matchup_no_lvl import analyze_matchup_no_lvl_stats
from test_deck_analysis import (
    analyze_card_meta_vs_counter,
    analyze_matchmaking_fairness,
    analyze_level_saturation,
    analyze_arena_progression_curve
)
from test_deck_switch import analyze_deck_switch_combined
from test_targeting import (
    analyze_all_snipers_targeting,
    analyze_sniper_confounding
)
from test_punish_outcome import analyze_punish_outcome_worsening
from test_return_breakdown import analyze_return_breakdown

from analyze_micro_meta import analyze_micro_meta
from arena_gatekeeping import analyze_arena_gatekeeping

from climbing_regression_analysis import analyze_climbing_regression
from test_climbing_speed import analyze_climbing_speed_penalty
from test_card_regression import analyze_card_regression
from test_session_swap import analyze_session_swap, analyze_session_swap_conditional
from test_level_volatility import analyze_level_volatility




def main():
    connection, cursor, load_tags = open_connection("db/clash.db")

    mode_filter = 'Ladder'

    # Caricamento sessioni e profili tramite battlelog_v2
    # Questo assicura che le sessioni siano definite consistentemente
    players_sessions = get_players_sessions(mode_filter, exclude_unreliable=True)

    # Definizione cartella risultati
    results_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(results_dir, exist_ok=True)

    # # raccolta dei dati utili per la classificazione del player
    # # Ricostruiamo il dizionario profiles per compatibilità con reporter.py
    #profiles = {p['tag']: p['profile'] for p in players_sessions if p['profile']}

    # raccolta statistiche matchup
    #matchup_stats = get_extreme_matchup_stats(players_sessions)

    # # calcolo correlazione tra odds ratio e ragequit
    #correlation_results = calculate_correlation_pity_ragequit(profiles, matchup_stats)

    # # calcolo chi quadro indipendenza (streak vs matchup)
    #chi2_results = get_chi2_independence_stats(players_sessions)

    # analyze_gatekeeping_all(players_sessions, cursor, output_dir=results_dir, gate_range=50)


    # # generazione report e salvataggio
    #generate_report(profiles, matchup_stats, correlation_results, chi2_results)

    # ragequit_and_odds_correlation(profiles, matchup_stats) 

    # # Esecuzione test aggiuntivi da test.py
    # print("\nEsecuzione test aggiuntivi (Sessioni, Streak, Fattori Confondenti)...")
    # analyze_std_correlation(players_sessions, output_dir=results_dir)
    # analyze_session_pity(players_sessions, output_dir=results_dir)
    # analyze_extreme_matchup_streak(players_sessions, output_dir=results_dir, use_no_lvl=False) # Con livelli (Reale)
    # analyze_extreme_matchup_streak(players_sessions, output_dir=results_dir, use_no_lvl=True)  # Senza livelli (Puro)
    #analyze_confounding_variables(players_sessions, cursor, output_dir=results_dir)
    # analyze_time_stats(players_sessions, output_dir=results_dir)
    #analyze_deck_switch_combined(players_sessions, cursor, output_dir=results_dir)
    # analyze_ers_pity_hypothesis(profiles, matchup_stats, output_dir=results_dir)
    # analyze_return_matchups_vs_ers(players_sessions, output_dir=results_dir)
    # analyze_pity_impact_on_session_length(players_sessions, output_dir=results_dir)
    # analyze_pity_impact_on_return_time(players_sessions, output_dir=results_dir)
    # analyze_churn_probability_vs_pity(players_sessions, matchup_stats, output_dir=results_dir)
    # analyze_session_trends(players_sessions, output_dir=results_dir)
    # analyze_cannon_fodder(players_sessions, output_dir=results_dir)
    # analyze_dangerous_sequences(players_sessions, output_dir=results_dir)
    # analyze_matchup_no_lvl_stats(players_sessions, output_dir=results_dir)
    # analyze_short_session_bonus(players_sessions, output_dir=results_dir)
    # analyze_markov_chains(players_sessions, output_dir=results_dir)
    analyze_return_after_bad_streak(players_sessions, output_dir=results_dir)
    # analyze_defeat_quality_impact(players_sessions, output_dir=results_dir)
    # analyze_debt_credit_combined(players_sessions, output_dir=results_dir)
    # analyze_punish_outcome_worsening(players_sessions, output_dir=results_dir)
    # analyze_return_breakdown(players_sessions, output_dir=results_dir)
    # analyze_punishment_tradeoff(players_sessions, output_dir=results_dir)
    # analyze_extreme_level_streak(players_sessions, output_dir=results_dir)
    # analyze_normalized_level_streak(players_sessions, output_dir=results_dir)
    # analyze_pity_probability_lift(players_sessions, output_dir=results_dir)
    # analyze_paywall_impact(players_sessions, output_dir=results_dir)
    # analyze_nolvl_streaks_vs_trophies(players_sessions, output_dir=results_dir)
    # analyze_meta_ranges(players_sessions, output_dir=results_dir)
    # analyze_climbing_regression(players_sessions, output_dir=results_dir)
    # analyze_arena_progression_curve(players_sessions, output_dir=results_dir)
    # analyze_climbing_speed_penalty(players_sessions, output_dir=results_dir)
    # analyze_climbing_impact(players_sessions, output_dir=results_dir)
    # analyze_hook_by_trophy_range(players_sessions, output_dir=results_dir, cursor=cursor)
    # analyze_skill_vs_matchup_dominance(players_sessions, output_dir=results_dir)
    # analyze_debt_initial_progression(players_sessions, output_dir=results_dir)
    # analyze_residual_level_diff_debt(players_sessions, output_dir=results_dir)
    # analyze_level_volatility(players_sessions, output_dir=results_dir)
    

    # analyze_card_meta_vs_counter(players_sessions, output_dir=results_dir)
    #analyze_matchmaking_fairness(players_sessions, output_dir=results_dir)
    # analyze_level_saturation(players_sessions, output_dir=results_dir)
    #analyze_all_snipers_targeting(players_sessions, output_dir=results_dir)
    # analyze_sniper_confounding(players_sessions, output_dir=results_dir)

    # analyze_micro_meta(players_sessions, output_dir=results_dir)
    # analyze_arena_gatekeeping(players_sessions, output_dir=results_dir)
    # # --- TEST VELOCI ---
    # analyze_pity_odds_vs_total_matches(profiles, matchup_stats, output_dir=results_dir)
    # if mode_filter == 'Ladder':
    #     analyze_pity_odds_vs_current_trophies(profiles, matchup_stats, cursor, output_dir=results_dir)

    # players_sessions = get_players_sessions('Ladder', exclude_unreliable=True)
    # results_dir = os.path.join(os.path.dirname(__file__), 'results/ranked')

    # analyze_session_swap(players_sessions, cursor, output_dir=results_dir, game_mode='Ladder')

    # mode='Ranked'

    # players_sessions = get_players_sessions(mode, exclude_unreliable=True)
    # results_dir = os.path.join(os.path.dirname(__file__), 'results/ranked')
    # #analyze_session_swap(players_sessions, cursor, output_dir=results_dir, game_mode='Ranked')
    # analyze_session_swap_conditional(players_sessions, cursor, output_dir=results_dir, game_mode=mode)
    # analyze_card_regression(players_sessions, output_dir=results_dir)


    print("Processo di report completato.")

    close_connection(connection)

if __name__ == "__main__":
    main()
