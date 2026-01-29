import os
from scipy.stats import spearmanr
import math

def analyze_pity_odds_vs_total_matches(profiles, matchup_stats, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'quick_tests_results.txt')
    print(f"\nGenerazione report Test Veloci in: {output_file}")

    # --- TEST VELOCE TEMPORANEO: Pity Odds vs Total Matches ---
    tmp_matches = []
    tmp_odds = []
    
    for t, prof in profiles.items():
        if t in matchup_stats:
            o = matchup_stats[t]['pity']['odds_ratio']
            m = prof.get('total_matches', 0)
            if o is not None and not math.isnan(o) and not math.isinf(o):
                tmp_matches.append(m)
                tmp_odds.append(o)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("TEST VELOCI DI CORRELAZIONE\n")
        f.write("="*80 + "\n\n")
        if len(tmp_matches) > 2:
            corr_tmp, p_tmp = spearmanr(tmp_matches, tmp_odds)
            f.write("1. PITY ODDS vs TOTAL MATCHES\n")
            f.write(f"   Correlazione: {corr_tmp:.4f}\n")
            f.write(f"   P-value:      {p_tmp:.4f}\n")
            f.write("-" * 40 + "\n\n")

def analyze_pity_odds_vs_current_trophies(profiles, matchup_stats, cursor, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    output_file = os.path.join(output_dir, 'quick_tests_results.txt')

    # --- TEST VELOCE TEMPORANEO: Pity Odds vs Current Trophies ---
    tmp_trophies = []
    tmp_odds_t = []
    

    for t in profiles.keys():
        if t in matchup_stats:
            o = matchup_stats[t]['pity']['odds_ratio']
            
            cursor.execute("SELECT trophies FROM players WHERE player_tag = ?", (t,))
            row = cursor.fetchone()
            trophies = row[0] if row else 0
            
            if o is not None and not math.isnan(o) and not math.isinf(o):
                tmp_trophies.append(trophies)
                tmp_odds_t.append(o)

    with open(output_file, "a", encoding="utf-8") as f:
        if len(tmp_trophies) > 2:
            corr_t, p_t = spearmanr(tmp_trophies, tmp_odds_t)
            f.write("2. PITY ODDS vs CURRENT TROPHIES\n")
            f.write(f"   Correlazione: {corr_t:.4f}\n")
            f.write(f"   P-value:      {p_t:.4f}\n")
            f.write("-" * 40 + "\n\n")