import os
import statistics
from scipy.stats import spearmanr, wilcoxon
import random

def analyze_matchup_no_lvl_stats(players_sessions, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'matchup_no_lvl_results.txt')

    print(f"\nGenerazione report Matchup No-Level (Fair Play) in: {output_file}")

    # Accumulatori
    real_matchups = []
    nolvl_matchups = []
    deltas = [] # Real - NoLvl (Positivo = Livelli aiutano, Negativo = Livelli svantaggiano)
    
    for p in players_sessions:
        for session in p['sessions']:
            battles = [b for b in session['battles'] if b['game_mode'] in ['Ladder', 'Ranked']]
            
            # Raccolta dati confronto
            for b in battles:
                if b['matchup'] is not None and b['matchup_no_lvl'] is not None:
                    real = b['matchup']
                    nolvl = b['matchup_no_lvl']
                    
                    real_matchups.append(real)
                    nolvl_matchups.append(nolvl)
                    deltas.append(real - nolvl)
            
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI MATCHUP INDIPENDENTE DAI LIVELLI (NO-LVL)\n")
        f.write("Obiettivo 1: Capire quanto i livelli influenzano il matchup reale.\n")
        f.write("="*80 + "\n\n")
        
        if not real_matchups:
            f.write("Nessun dato disponibile (matchup_no_lvl mancante nel DB?).\n")
            return

        # --- 1. CONFRONTO REALE vs NO-LVL ---
        avg_real = statistics.mean(real_matchups)
        avg_nolvl = statistics.mean(nolvl_matchups)
        avg_delta = statistics.mean(deltas)
        
        f.write("1. IMPATTO DEI LIVELLI\n")
        f.write(f"   Media Matchup REALE:   {avg_real:.2f}%\n")
        f.write(f"   Media Matchup NO-LVL:  {avg_nolvl:.2f}%\n")
        f.write(f"   Delta Medio (Real-No): {avg_delta:+.2f}% (Positivo = Vantaggio Livelli)\n")
        
        # Correlazione
        corr, p_corr = spearmanr(real_matchups, nolvl_matchups)
        f.write(f"   Correlazione (Real vs NoLvl): {corr:.4f} (p={p_corr:.4f})\n")
        f.write("   (Alta correlazione = I livelli contano poco; Bassa = I livelli stravolgono il matchup)\n\n")
        
        # Test Wilcoxon (Real vs NoLvl)
        # Se significativo, i livelli spostano significativamente l'ago della bilancia
        try:
            stat, p_wilc = wilcoxon(real_matchups, nolvl_matchups)
            f.write(f"   Test Wilcoxon (Differenza Significativa): p-value = {p_wilc:.4f}\n")
            f.write(f"   RISULTATO: {'SIGNIFICATIVO' if p_wilc < 0.05 else 'NON SIGNIFICATIVO'}\n")
        except Exception as e:
            f.write(f"   Errore Wilcoxon: {e}\n")
            
        f.write("="*80 + "\n")