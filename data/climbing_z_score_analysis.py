import os
import statistics
import math
from scipy.stats import linregress, norm

def analyze_climbing_z_score(players_sessions, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'climbing_z_score_results.txt')
    
    print(f"\nGenerazione report Z-Score Climbing in: {output_file}")
    
    # 1. Calcolo Regressione Globale
    all_trophies = []
    all_values = []
    
    # Dati per bucket
    BUCKET_SIZE = 100
    buckets = {} # bucket_start -> {'win': [], 'loss': []}

    for p in players_sessions:
        for s in p['sessions']:
            battles = s['battles']
            for i in range(len(battles) - 1):
                curr = battles[i]
                next_b = battles[i+1]
                
                if curr['game_mode'] != 'Ladder': continue
                
                t = curr.get('trophies_before')
                val_curr = curr.get('matchup_no_lvl')
                
                # Per regressione globale usiamo tutti i punti validi
                if t is not None and val_curr is not None:
                    all_trophies.append(t)
                    all_values.append(val_curr)
                
                # Per analisi Z-score (Next Match)
                # Raccogliamo il valore della PROSSIMA partita, diviso per esito della CORRENTE
                val_next = next_b.get('matchup_no_lvl')
                if t is not None and val_next is not None:
                    b_idx = (t // BUCKET_SIZE) * BUCKET_SIZE
                    if b_idx not in buckets:
                        buckets[b_idx] = {'win': [], 'loss': []}
                    
                    if curr['win']:
                        buckets[b_idx]['win'].append(val_next)
                    else:
                        buckets[b_idx]['loss'].append(val_next)

    if not all_trophies:
        with open(output_file, "w") as f: f.write("Dati insufficienti.")
        return

    # Calcolo Slope Globale
    slope, intercept, r_value, p_value, std_err = linregress(all_trophies, all_values)
    
    # Expected Delta per 60 trofei (Win vs Loss gap)
    expected_delta_60 = slope * 60
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI Z-SCORE DELTA MATCHUP NO-LVL (WIN vs LOSS)\n")
        f.write("Obiettivo: Verificare se il peggioramento del Matchup (Deck) dopo una vittoria è statisticamente diverso\n")
        f.write("           da quello atteso dalla progressione naturale (Regressione Lineare).\n")
        f.write(f"Regressione Globale: Slope = {slope*1000:.4f} (per 1000 trofei)\n")
        f.write(f"Expected Delta (60 trofei): {expected_delta_60:.4f}\n")
        f.write("="*120 + "\n")
        f.write(f"{'RANGE':<12} | {'N':<6} | {'OBS DELTA':<10} | {'EXP DELTA':<10} | {'Z-SCORE':<8} | {'P-VAL':<8} | {'INTERP'}\n")
        f.write("-" * 120 + "\n")
        
        sorted_keys = sorted(buckets.keys())
        
        anomalies = 0
        total_buckets = 0
        
        for bid in sorted_keys:
            data = buckets[bid]
            wins = data['win']
            losses = data['loss']
            
            if len(wins) < 20 or len(losses) < 20: continue
            
            mean_w = statistics.mean(wins)
            var_w = statistics.variance(wins) if len(wins) > 1 else 0
            n_w = len(wins)
            
            mean_l = statistics.mean(losses)
            var_l = statistics.variance(losses) if len(losses) > 1 else 0
            n_l = len(losses)
            
            observed_delta = mean_w - mean_l
            
            # Standard Error of the difference between means
            se_diff = math.sqrt((var_w / n_w) + (var_l / n_l))
            
            if se_diff == 0: continue
            
            # Z-Score: (Observed - Expected) / SE
            z_score = (observed_delta - expected_delta_60) / se_diff
            
            p_val = norm.sf(abs(z_score)) * 2
            
            interp = ""
            if abs(z_score) > 2:
                if z_score < 0: # Observed < Expected (More negative -> Worse than expected)
                    interp = "PUNISHMENT"
                    anomalies += 1
                else: # Observed > Expected (Less negative -> Better than expected)
                    interp = "AID/BOOST"
            
            total_buckets += 1
            
            label = f"{bid}-{bid+BUCKET_SIZE}"
            f.write(f"{label:<12} | {n_w+n_l:<6} | {observed_delta:<10.4f} | {expected_delta_60:<10.4f} | {z_score:<8.2f} | {p_val:<8.4f} | {interp}\n")
            
        f.write("-" * 120 + "\n")
        f.write(f"Totale Finestre Analizzate: {total_buckets}\n")
        f.write(f"Finestre Anomale (Punishment |Z|>2): {anomalies}\n")
        if total_buckets > 0:
            f.write(f"Percentuale Anomalie: {(anomalies/total_buckets)*100:.2f}%\n")
        f.write("="*120 + "\n")