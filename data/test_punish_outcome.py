import os
import statistics
from scipy.stats import mannwhitneyu

def analyze_punish_outcome_worsening(players_sessions, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'punish_outcome_worsening_results.txt')

    print(f"\nGenerazione report Peggioramento Post-Punish in: {output_file}")

    UNFAVORABLE_THRESH = 45.0
    
    # Deltas: Next Matchup - Current Matchup
    deltas_win = []  # Quando vinci il punish match
    deltas_loss = [] # Quando perdi il punish match
    
    # Deltas Levels: Next Level Diff - Current Level Diff
    deltas_lvl_win = []
    deltas_lvl_loss = []
    
    for p in players_sessions:
        for s in p['sessions']:
            battles = s['battles']
            for i in range(len(battles) - 1):
                curr = battles[i]
                next_b = battles[i+1]
                
                if curr['matchup'] is None or next_b['matchup'] is None:
                    continue
                
                # Condizione: Matchup Sfavorevole (Punish Match)
                if curr['matchup'] < UNFAVORABLE_THRESH:
                    delta = next_b['matchup'] - curr['matchup']
                    
                    # Level Diff Delta
                    delta_lvl = None
                    if curr.get('level_diff') is not None and next_b.get('level_diff') is not None:
                        delta_lvl = next_b['level_diff'] - curr['level_diff']
                    
                    if curr['win'] == 1:
                        deltas_win.append(delta)
                        if delta_lvl is not None: deltas_lvl_win.append(delta_lvl)
                    else:
                        deltas_loss.append(delta)
                        if delta_lvl is not None: deltas_lvl_loss.append(delta_lvl)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI PEGGIORAMENTO POST-PUNISH (WIN vs LOSS)\n")
        f.write("Domanda: Se vinco un match sfavorevole (<45%), il successivo è ANCORA PEGGIORE rispetto a quello appena giocato?\n")
        f.write("Metrica: Delta = Matchup Successivo - Matchup Corrente.\n")
        f.write("         Delta < 0: Il matchup è peggiorato (Accanimento).\n")
        f.write("         Delta > 0: Il matchup è migliorato (Sollievo).\n")
        f.write("="*80 + "\n\n")
        
        if len(deltas_win) < 10 or len(deltas_loss) < 10:
            f.write("Dati insufficienti.\n")
            return

        avg_delta_win = statistics.mean(deltas_win)
        avg_delta_loss = statistics.mean(deltas_loss)
        
        # Count worsening
        worsening_win = sum(1 for d in deltas_win if d < 0)
        worsening_loss = sum(1 for d in deltas_loss if d < 0)
        
        rate_worsening_win = (worsening_win / len(deltas_win)) * 100
        rate_worsening_loss = (worsening_loss / len(deltas_loss)) * 100

        f.write(f"{'ESITO PUNISH MATCH':<25} | {'N':<6} | {'AVG DELTA MU':<15} | {'% PEGGIORAMENTO':<20}\n")
        f.write("-" * 75 + "\n")
        f.write(f"{'WIN (Vittoria Eroica)':<25} | {len(deltas_win):<6} | {avg_delta_win:<+15.2f} | {rate_worsening_win:<20.2f}%\n")
        f.write(f"{'LOSS (Sconfitta Attesa)':<25} | {len(deltas_loss):<6} | {avg_delta_loss:<+15.2f} | {rate_worsening_loss:<20.2f}%\n")
        
        f.write("-" * 75 + "\n")
        
        # Mann-Whitney U Test
        # H1: Delta(Win) < Delta(Loss) -> Chi vince vede il matchup peggiorare di più (o migliorare di meno)
        stat, p_val = mannwhitneyu(deltas_win, deltas_loss, alternative='less')
        
        f.write(f"Test Mann-Whitney U (Delta Win < Delta Loss): p-value = {p_val:.4f}\n")
        
        if p_val < 0.05:
            f.write("RISULTATO: SIGNIFICATIVO. Vincere un punish match porta a una variazione di matchup peggiore rispetto a perderlo.\n")
            if avg_delta_win < 0:
                f.write("           In media, dopo una vittoria eroica, il matchup PEGGIORA ulteriormente.\n")
            else:
                f.write("           In media, il matchup migliora meno rispetto a quando si perde.\n")
        else:
            f.write("RISULTATO: NON SIGNIFICATIVO. Non c'è evidenza di accanimento specifico sul Delta.\n")

        # --- LEVEL DIFF ANALYSIS ---
        f.write("\n" + "="*80 + "\n")
        f.write("ANALISI PEGGIORAMENTO LIVELLI (WIN vs LOSS)\n")
        f.write("Metrica: Delta Level = Level Diff Successivo - Level Diff Corrente.\n")
        f.write("         Delta < 0: I livelli sono peggiorati (Avversario più forte).\n")
        f.write("-" * 80 + "\n")
        
        if len(deltas_lvl_win) < 10 or len(deltas_lvl_loss) < 10:
             f.write("Dati insufficienti per i livelli.\n")
        else:
             avg_dl_win = statistics.mean(deltas_lvl_win)
             avg_dl_loss = statistics.mean(deltas_lvl_loss)
             
             f.write(f"{'ESITO':<25} | {'N':<6} | {'AVG DELTA LVL':<15}\n")
             f.write("-" * 55 + "\n")
             f.write(f"{'WIN':<25} | {len(deltas_lvl_win):<6} | {avg_dl_win:<+15.4f}\n")
             f.write(f"{'LOSS':<25} | {len(deltas_lvl_loss):<6} | {avg_dl_loss:<+15.4f}\n")
             
             stat_l, p_val_l = mannwhitneyu(deltas_lvl_win, deltas_lvl_loss, alternative='less')
             f.write("-" * 55 + "\n")
             f.write(f"Test Mann-Whitney U (Delta Win < Delta Loss): p-value = {p_val_l:.4f}\n")
             
             if p_val_l < 0.05:
                 f.write("RISULTATO: SIGNIFICATIVO. Vincere porta a un peggioramento dei livelli maggiore rispetto a perdere.\n")
                 f.write("           (Conferma che la 'punizione' passa anche attraverso i livelli).\n")
             else:
                 f.write("RISULTATO: NON SIGNIFICATIVO. I livelli variano in modo simile.\n")
            
        f.write("\n" + "="*80 + "\n")