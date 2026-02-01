import os
import statistics
from collections import defaultdict

def analyze_arena_progression_curve(players_sessions, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'arena_progression_curve.txt')
    
    print(f"\nGenerazione report Curva Progressione Arena in: {output_file}")
    
    # Configurazione
    ARENA_STEP = 1000 # Dimensione Arena (es. 5000-6000)
    SUB_STEP = 100    # Risoluzione analisi (es. ogni 100 trofei)
    
    # Struttura: arena_start -> { sub_step_index: [level_diffs] }
    data = defaultdict(lambda: defaultdict(list))
    
    for p in players_sessions:
        for s in p['sessions']:
            for b in s['battles']:
                if b['game_mode'] == 'Ladder' and b.get('trophies_before') and b.get('level_diff') is not None:
                    t = b['trophies_before']
                    
                    arena_start = (t // ARENA_STEP) * ARENA_STEP
                    offset = t - arena_start
                    sub_idx = offset // SUB_STEP
                    
                    data[arena_start][sub_idx].append(b['level_diff'])

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI CURVA PROGRESSIONE ARENA (GATEKEEPER EFFECT)\n")
        f.write("Obiettivo: Verificare se lo svantaggio livelli aumenta non-linearmente avvicinandosi alla fine dell'arena.\n")
        f.write("Ipotesi: All'inizio dell'arena trovi climber (livelli bassi), alla fine gatekeeper (livelli alti/maxati).\n")
        f.write(f"Arena Size: {ARENA_STEP}, Step Analisi: {SUB_STEP}\n")
        f.write("="*100 + "\n\n")
        
        sorted_arenas = sorted(data.keys())
        
        for arena in sorted_arenas:
            sub_data = data[arena]
            total_matches = sum(len(v) for v in sub_data.values())
            
            if total_matches < 100: continue # Skip arene poco popolate
            
            f.write(f"--- ARENA {arena}-{arena+ARENA_STEP} (N={total_matches}) ---\n")
            f.write(f"{'RANGE':<15} | {'N':<6} | {'AVG LEVEL DIFF':<15} | {'DELTA PREV':<12}\n")
            f.write("-" * 60 + "\n")
            
            sorted_subs = sorted(sub_data.keys())
            prev_avg = None
            
            slopes = []
            
            for sub_idx in sorted_subs:
                if sub_idx >= (ARENA_STEP // SUB_STEP): continue # Ignore out of bounds
                
                vals = sub_data[sub_idx]
                if len(vals) < 10: continue
                
                avg = statistics.mean(vals)
                
                range_label = f"{arena + sub_idx*SUB_STEP}-{arena + (sub_idx+1)*SUB_STEP}"
                
                delta_str = ""
                if prev_avg is not None:
                    delta = avg - prev_avg
                    delta_str = f"{delta:+.3f}"
                    slopes.append(delta)
                
                f.write(f"{range_label:<15} | {len(vals):<6} | {avg:<15.3f} | {delta_str:<12}\n")
                prev_avg = avg
            
            # Analisi Trend
            if len(slopes) > 2:
                # Confrontiamo la pendenza nella prima metà vs seconda metà
                mid = len(slopes) // 2
                first_half_slope = statistics.mean(slopes[:mid])
                second_half_slope = statistics.mean(slopes[mid:])
                
                f.write("-" * 60 + "\n")
                f.write(f"Avg Slope Prima Metà:   {first_half_slope:+.4f} / 100 trofei\n")
                f.write(f"Avg Slope Seconda Metà: {second_half_slope:+.4f} / 100 trofei\n")
                
                if second_half_slope < first_half_slope - 0.05:
                    f.write(">> EFFETTO GATEKEEPER RILEVATO: Il muro si alza più velocemente alla fine.\n")
                else:
                    f.write(">> PROGRESSIONE LINEARE O COSTANTE.\n")
            
            f.write("\n")