import sqlite3
import os
import sys
import numpy as np
from scipy.stats import mannwhitneyu
import statistics
from collections import defaultdict

# Percorso del database
DB_PATH = 'db/clash.db'
OUTPUT_FILE = 'data/results/symmetric_gatekeeping_results.txt'

# Aggiungi path per battlelog_v2
sys.path.append(os.path.join(os.path.dirname(__file__), 'data'))
from battlelog_v2 import get_players_sessions
from test_deck_analysis import get_deck_cards_batch

def calculate_avg_level(deck_cards):
    if not deck_cards: return 0
    levels = [c['level'] for c in deck_cards if c.get('level') is not None]
    return statistics.mean(levels) if levels else 0

def run_symmetric_test():
    if not os.path.exists(DB_PATH):
        print(f"Errore: Database non trovato in {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Recupera soglie arene dal DB
    try:
        cursor.execute("SELECT trophy_limit FROM arenas ORDER BY trophy_limit ASC")
        ARENA_THRESHOLDS = [row[0] for row in cursor.fetchall()]
    except Exception as e:
        print(f"Errore recupero soglie arene: {e}")
        return
    finally:
        conn.close()

    print("Caricamento dati e calcolo trofei...")
    players_sessions = get_players_sessions(mode_filter='Ladder', exclude_unreliable=False)
    
    # Raccogli tutti i deck ID necessari
    all_deck_ids = set()
    battles_to_process = []

    for p in players_sessions:
        for s in p['sessions']:
            for b in s['battles']:
                if b['game_mode'] != 'Ladder':
                    continue
                
                trophies = b.get('trophies_before')
                opp_deck_id = b.get('opponent_deck_id')
                
                if trophies is None or not opp_deck_id:
                    continue
                
                all_deck_ids.add(opp_deck_id)
                battles_to_process.append({
                    'trophies': trophies,
                    'opp_deck_id': opp_deck_id
                })

    # Fetch carte in batch
    print(f"Recupero carte per {len(all_deck_ids)} mazzi avversari...")
    deck_cache = {}
    all_deck_ids_list = list(all_deck_ids)
    CHUNK_SIZE = 900
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for i in range(0, len(all_deck_ids_list), CHUNK_SIZE):
        chunk = all_deck_ids_list[i:i+CHUNK_SIZE]
        batch_decks = get_deck_cards_batch(cursor, chunk)
        deck_cache.update(batch_decks)
    conn.close()

    # 1. Calcola la curva globale (Baseline) per normalizzare
    print("Calcolo baseline livelli per fascia trofei...")
    trophy_levels = defaultdict(list)
    BUCKET_SIZE = 100 # Fascia di 100 trofei per la media locale
    
    valid_battles = []
    
    for b in battles_to_process:
        trophies = b['trophies']
        deck_id = b['opp_deck_id']
        
        cards = deck_cache.get(deck_id)
        if not cards:
            continue
            
        avg_lvl = calculate_avg_level(cards)
        if avg_lvl == 0:
            continue
            
        # Store for later
        b['avg_lvl'] = avg_lvl
        valid_battles.append(b)
        
        # Add to bucket for baseline
        b_idx = (trophies // BUCKET_SIZE) * BUCKET_SIZE
        trophy_levels[b_idx].append(avg_lvl)

    # Compute means for each bucket
    bucket_means = {}
    for b_idx, levels in trophy_levels.items():
        if len(levels) >= 5: # Minimo statistico
            bucket_means[b_idx] = statistics.mean(levels)

    # Definiamo le due zone di confronto
    # DANGER ZONE: Ultimi 50 trofei prima della soglia (es. 4950-5000)
    # CONTROL ZONE: I 50 trofei precedenti alla Danger (es. 4900-4950)
    WINDOW_SIZE = 50 

    danger_residuals = []
    control_residuals = []
    
    for b in valid_battles:
        trophies = b['trophies']
        avg_lvl = b['avg_lvl']
        
        # Trova la media della fascia di appartenenza
        b_idx = (trophies // BUCKET_SIZE) * BUCKET_SIZE
        baseline = bucket_means.get(b_idx)
        
        if baseline is None:
            continue

        # Calcola residuo (quanto si discosta dalla media locale)
        residual = avg_lvl - baseline

        for threshold in ARENA_THRESHOLDS:
            # Controllo se il match cade in una delle due finestre
            
            # DANGER ZONE [Soglia - 50, Soglia)
            if (threshold - WINDOW_SIZE) <= trophies < threshold:
                danger_residuals.append(residual)
                break # Assegnato, passo al prossimo match
            
            # CONTROL ZONE [Soglia - 100, Soglia - 50)
            elif (threshold - (WINDOW_SIZE * 2)) <= trophies < (threshold - WINDOW_SIZE):
                control_residuals.append(residual)
                break

    # Analisi Statistica
    with open(OUTPUT_FILE, 'w') as f:
        f.write("ANALISI GATEKEEPING SIMMETRICA (DANGER VS CONTROL) - RESIDUI NORMALIZZATI\n")
        f.write(f"Confronto: Danger Zone [-{WINDOW_SIZE}, 0] vs Control Zone [-{WINDOW_SIZE*2}, -{WINDOW_SIZE}]\n")
        f.write("Obiettivo: Verificare se il livello avversario è anomalo rispetto alla media della fascia di trofei.\n")
        f.write("Metodo: Residuo = Livello Osservato - Media Livello Fascia (100 trofei)\n")
        f.write("============================================================\n\n")
        
        f.write(f"Campione Danger Zone:  {len(danger_residuals)}\n")
        f.write(f"Campione Control Zone: {len(control_residuals)}\n\n")
        
        if len(danger_residuals) > 0 and len(control_residuals) > 0:
            avg_danger = np.mean(danger_residuals)
            avg_control = np.mean(control_residuals)
            
            # Delta osservato (Danger - Control)
            delta = avg_danger - avg_control
            
            # Test Mann-Whitney U
            # H0: Danger <= Control
            # H1: Danger > Control (Livelli più alti nella Danger)
            stat, p_val = mannwhitneyu(danger_residuals, control_residuals, alternative='greater')
            
            f.write(f"Media Residuo (Danger):  {avg_danger:+.4f}\n")
            f.write(f"Media Residuo (Control): {avg_control:+.4f}\n")
            f.write(f"Delta Osservato:            {delta:+.4f}\n")
            f.write(f"P-value (Danger > Control): {p_val:.5f}\n")
            
            # Verifica Progressione Naturale
            # Da arena_progression_curve.txt sappiamo che i livelli salgono di ~0.097 ogni 100 trofei.
            # Quindi in 50 trofei (distanza tra i centri delle due zone) ci aspettiamo una crescita naturale.
            natural_growth_per_50 = 0.0485 
            
            excess_growth = delta - natural_growth_per_50
            
            f.write("\n--- VERIFICA PROGRESSIONE NATURALE ---\n")
            f.write(f"Crescita Naturale Attesa (+50 trofei): +{natural_growth_per_50:.4f}\n")
            f.write(f"Crescita Reale Osservata:              {delta:+.4f}\n")
            f.write(f"Eccesso (Gatekeeping Effect):          {excess_growth:+.4f}\n")
            
            if p_val < 0.05:
                if excess_growth > 0:
                    ratio = delta / natural_growth_per_50 if natural_growth_per_50 > 0 else 0
                    f.write(f"\nCONCLUSIONE: C'è un muro statisticamente significativo.\n")
                    f.write(f"Il livello avversario aumenta {ratio:.1f} volte più velocemente del normale.\n")
                else:
                    f.write("\nCONCLUSIONE: L'aumento è significativo ma in linea con la progressione naturale.\n")
            else:
                f.write("\nCONCLUSIONE: Nessuna differenza significativa tra le due zone.\n")
                
        else:
            f.write("Dati insufficienti per il confronto.\n")

    print(f"Analisi completata. Risultati in: {OUTPUT_FILE}")

if __name__ == "__main__":
    run_symmetric_test()