from scipy.stats import spearmanr
import math

def analyze_pity_odds_vs_total_matches(profiles, matchup_stats):
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
                
    if len(tmp_matches) > 2:
        corr_tmp, p_tmp = spearmanr(tmp_matches, tmp_odds)
        print(f"\n[TEST VELOCE] Correlazione Pity Odds vs N. Partite: {corr_tmp:.4f} (p-value: {p_tmp:.4f})")

def analyze_pity_odds_vs_current_trophies(profiles, matchup_stats, cursor):
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
                
    if len(tmp_trophies) > 2:
        corr_t, p_t = spearmanr(tmp_trophies, tmp_odds_t)
        print(f"\n[TEST VELOCE] Correlazione Pity Odds vs Trofei Attuali: {corr_t:.4f} (p-value: {p_t:.4f})")