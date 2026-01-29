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

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI REGRESSIONE EFFETTO CLIMBING (Natural Level Decay)\n")
        f.write("Obiettivo: Verificare se il peggioramento del Level Diff osservato dopo una vittoria (test 'Paywall Impact')\n")
        f.write("           è spiegabile con la naturale progressione dei trofei (incontrare avversari più forti).\n")
        f.write("Metodo: Regressione lineare Level_Diff vs Trophies per calcolare il trend naturale.\n")
        f.write("        Slope = Variazione media di Level Diff per 1 Trofeo guadagnato.\n")
        f.write("        Delta 30 = Variazione attesa per una vittoria (+30 trofei).\n")
        f.write("        Delta 60 = Variazione attesa tra lo stato post-vittoria (+30) e post-sconfitta (-30).\n")
        f.write("                   Questo valore è il confronto diretto con il 'DELTA' del test 'Paywall Impact'.\n")
        f.write("="*120 + "\n")
        f.write(f"{'RANGE TROFEI':<15} | {'N. BATTLES':<10} | {'SLOPE (x1000)':<15} | {'DELTA 30 (Win)':<15} | {'DELTA 60 (W-L Gap)':<20} | {'NOTE'}\n")
        f.write("-" * 120 + "\n")
        
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
            
            delta_60 = slope * 60
            note = "In linea con Paywall Test" if -0.12 <= delta_60 <= -0.04 else ""
            
            label = f"{bid}-{bid+bucket_size}"
            f.write(f"{label:<15} | {n:<10} | {slope*1000:<15.4f} | {slope * 30:<15.4f} | {delta_60:<20.4f} | {note}\n")
            
        f.write("-" * 120 + "\n")
        
        if len(all_points) > 100:
            xs, ys = [p[0] for p in all_points], [p[1] for p in all_points]
            n = len(all_points)
            sum_x, sum_y = sum(xs), sum(ys)
            sum_xy = sum(x*y for x,y in zip(xs, ys))
            sum_xx = sum(x*x for x in xs)
            denominator = (n * sum_xx - sum_x * sum_x)
            slope = (n * sum_xy - sum_x * sum_y) / denominator if denominator != 0 else 0
            delta_60 = slope * 60
            note = "In linea con Paywall Test" if -0.12 <= delta_60 <= -0.04 else ""
            f.write(f"{'GLOBAL':<15} | {n:<10} | {slope*1000:<15.4f} | {slope * 30:<15.4f} | {delta_60:<20.4f} | {note}\n")
            
        f.write("="*120 + "\n")
        f.write("INTERPRETAZIONE:\n")
        f.write("1. La colonna 'DELTA 60 (W-L Gap)' stima la differenza 'naturale' di Level Diff tra una vittoria e una sconfitta, dovuta solo alla scalata.\n")
        f.write("2. Confronta questo valore con il 'DELTA' nel file 'paywall_impact_results.txt' per la stessa fascia di trofei.\n")
        f.write("3. Se i valori sono simili (es. DELTA 60 è -0.07 e il Delta del paywall test era -0.08), allora l'effetto è spiegato dal CLIMBING.\n")
        f.write("4. Se 'DELTA 60' è molto più piccolo del Delta del paywall test (es. -0.01 vs -0.08), allora c'è una componente PUNITIVA non spiegata dalla scalata.\n")