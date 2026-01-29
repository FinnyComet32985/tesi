import os
import statistics

def analyze_climbing_regression(players_sessions, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'climbing_regression_results.txt')
    
    print(f"\nGenerazione report Regressione Climbing in: {output_file}")
    
    # Configurazione Bucket
    bucket_size = 1000
    buckets = {}
    all_points = []

    # Raccolta Dati: (Trofei, Level_Diff)
    for p in players_sessions:
        for s in p['sessions']:
            for b in s['battles']:
                if b['game_mode'] == 'Ladder':
                    t = b.get('trophies_before')
                    ld = b.get('level_diff')
                    
                    # Filtriamo dati validi
                    if t is not None and ld is not None:
                        bucket_id = (t // bucket_size) * bucket_size
                        if bucket_id not in buckets:
                            buckets[bucket_id] = []
                        buckets[bucket_id].append((t, ld))
                        all_points.append((t, ld))

    # Valore di riferimento dal test Debt Extinction (Delta Win - Loss)
    OBSERVED_DELTA_WIN_LOSS = -0.08

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI REGRESSIONE EFFETTO CLIMBING (Natural Level Decay)\n")
        f.write("Obiettivo: Verificare se il peggioramento del Level Diff (-0.08) osservato nel test 'Debt Extinction' (Delta Win-Loss)\n")
        f.write("           è spiegabile con la naturale progressione dei trofei (incontrare avversari più forti).\n")
        f.write("Metodo: Regressione lineare Level_Diff vs Trophies per calcolare il trend naturale.\n")
        f.write("        Confrontiamo il 'Natural Delta 60' (gap trofei tra Win e Loss) con l'Observed Delta (-0.08).\n")
        f.write("="*130 + "\n")
        f.write(f"{'RANGE TROFEI':<15} | {'N. BATTLES':<10} | {'SLOPE (x1000)':<15} | {'NATURAL DELTA 60':<20} | {'OBSERVED DELTA':<15} | {'EXPLAINED %':<15}\n")
        f.write("-" * 130 + "\n")
        
        sorted_keys = sorted(buckets.keys())
        
        for bid in sorted_keys:
            points = buckets[bid]
            if len(points) < 100: # Ignora bucket con pochi dati
                continue
            
            xs = [p[0] for p in points]
            ys = [p[1] for p in points]
            
            n = len(points)
            sum_x, sum_y = sum(xs), sum(ys)
            sum_xy = sum(x*y for x,y in zip(xs, ys))
            sum_xx = sum(x*x for x in xs)
            
            denominator = (n * sum_xx - sum_x * sum_x)
            slope = (n * sum_xy - sum_x * sum_y) / denominator if denominator != 0 else 0
            
            # Gap di 60 trofei (Win +30 vs Loss -30)
            natural_delta_60 = slope * 60
            
            # Percentuale spiegata
            explained_pct = (natural_delta_60 / OBSERVED_DELTA_WIN_LOSS) * 100 if OBSERVED_DELTA_WIN_LOSS != 0 else 0
            
            label = f"{bid}-{bid+bucket_size}"
            f.write(f"{label:<15} | {n:<10} | {slope*1000:<15.4f} | {natural_delta_60:<20.4f} | {OBSERVED_DELTA_WIN_LOSS:<15} | {explained_pct:<15.1f}%\n")
            
        f.write("-" * 120 + "\n")
        
        if len(all_points) > 100:
            xs, ys = [p[0] for p in all_points], [p[1] for p in all_points]
            n = len(all_points)
            sum_x, sum_y = sum(xs), sum(ys)
            sum_xy = sum(x*y for x,y in zip(xs, ys))
            sum_xx = sum(x*x for x in xs)
            denominator = (n * sum_xx - sum_x * sum_x)
            slope = (n * sum_xy - sum_x * sum_y) / denominator if denominator != 0 else 0
            
            natural_delta_60 = slope * 60
            explained_pct = (natural_delta_60 / OBSERVED_DELTA_WIN_LOSS) * 100 if OBSERVED_DELTA_WIN_LOSS != 0 else 0
            
            f.write(f"{'GLOBAL':<15} | {n:<10} | {slope*1000:<15.4f} | {natural_delta_60:<20.4f} | {OBSERVED_DELTA_WIN_LOSS:<15} | {explained_pct:<15.1f}%\n")
            
        f.write("="*120 + "\n")
        f.write("INTERPRETAZIONE:\n")
        f.write("1. NATURAL DELTA 60: Variazione di livello attesa per un gap di 60 trofei (differenza tra aver vinto +30 e aver perso -30).\n")
        f.write("2. OBSERVED DELTA: Il valore -0.08 misurato nel test 'Debt Extinction' (differenza reale tra post-win e post-loss).\n")
        f.write("3. EXPLAINED %: Quanta parte del fenomeno è spiegata dal climbing naturale.\n")
        f.write("   - Se vicino a 100%: Il debito è un'illusione statistica dovuta alla scalata.\n")
        f.write("   - Se vicino a 0% (o negativo): Il debito è REALE e non dovuto alla scalata. Il sistema ti punisce attivamente.\n")