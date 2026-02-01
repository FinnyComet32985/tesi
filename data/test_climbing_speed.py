import os
import statistics
from scipy.stats import spearmanr, mannwhitneyu

def analyze_climbing_speed_penalty(players_sessions, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'climbing_speed_penalty_results.txt')
    
    print(f"\nGenerazione report Climbing Speed Penalty in: {output_file}")
    
    WINDOW = 5
    
    # Data: speed_score -> list of next_matchups
    # Speed Score: Net Wins in last WINDOW matches (Wins - Losses)
    # Range: -5 to +5
    speed_data_mu = {}
    speed_data_lvl = {}
    
    for i in range(-WINDOW, WINDOW + 1):
        speed_data_mu[i] = []
        speed_data_lvl[i] = []
        
    for p in players_sessions:
        for s in p['sessions']:
            battles = s['battles']
            if len(battles) <= WINDOW: continue
            
            # Sliding window
            for i in range(WINDOW, len(battles)):
                window = battles[i-WINDOW : i]
                next_b = battles[i]
                
                if next_b.get('matchup_no_lvl') is None or next_b.get('level_diff') is None:
                    continue
                
                wins = sum(1 for b in window if b['win'])
                losses = len(window) - wins
                net_score = wins - losses
                
                speed_data_mu[net_score].append(next_b['matchup_no_lvl'])
                speed_data_lvl[net_score].append(next_b['level_diff'])
                
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI PENALITÀ VELOCITÀ DI SCALATA (MOMENTUM)\n")
        f.write("Obiettivo: Verificare se salire velocemente (High Momentum) porta a matchup o livelli peggiori.\n")
        f.write(f"Metodo: Calcolo Net Wins negli ultimi {WINDOW} match (Range -{WINDOW} a +{WINDOW}).\n")
        f.write("="*100 + "\n")
        
        f.write(f"{'NET WINS':<10} | {'N':<6} | {'NEXT MU (No-Lvl)':<20} | {'NEXT LEVEL DIFF':<20}\n")
        f.write("-" * 100 + "\n")
        
        sorted_scores = sorted(speed_data_mu.keys())
        
        x_vals = []
        y_mu = []
        
        for score in sorted_scores:
            mus = speed_data_mu[score]
            lvls = speed_data_lvl[score]
            
            if len(mus) < 20: continue
            
            avg_mu = statistics.mean(mus)
            avg_lvl = statistics.mean(lvls)
            
            f.write(f"{score:<10} | {len(mus):<6} | {avg_mu:<20.2f} | {avg_lvl:<20.3f}\n")
            
            for m in mus:
                x_vals.append(score)
                y_mu.append(m)
                
        f.write("-" * 100 + "\n")
        
        # Correlation
        if len(x_vals) > 100:
            corr_mu, p_mu = spearmanr(x_vals, y_mu)
            
            f.write(f"Correlazione Momentum vs Matchup No-Lvl: {corr_mu:.4f} (p={p_mu:.4f})\n")
            
            f.write("\nINTERPRETAZIONE:\n")
            f.write("- Correlazione NEGATIVA significativa: Chi sale veloce viene frenato (Matchup peggiori).\n")
            f.write("- Correlazione POSITIVA significativa: Chi sale veloce viene aiutato (Snowball).\n")
            
        # Compare Extremes
        tilt_mus = []
        hot_mus = []
        for s in range(-WINDOW, -2): tilt_mus.extend(speed_data_mu.get(s, []))
        for s in range(3, WINDOW + 1): hot_mus.extend(speed_data_mu.get(s, []))
            
        if tilt_mus and hot_mus:
            stat, p_val = mannwhitneyu(hot_mus, tilt_mus, alternative='less')
            f.write(f"\nMann-Whitney U (Hot Streak < Tilt?): p={p_val:.4f}\n")

        f.write("="*100 + "\n")