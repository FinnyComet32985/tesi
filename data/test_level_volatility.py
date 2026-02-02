import os
import statistics
import sqlite3
from collections import defaultdict
from scipy.stats import ttest_ind

DB_PATH = os.path.join(os.path.dirname(__file__), '../db/clash.db')

def get_deck_cards_batch(cursor, deck_hashes):
    """Recupera le carte per un set di deck hashes (copiato da test_deck_analysis)."""
    if not deck_hashes:
        return {}
    
    placeholders = ','.join(['?'] * len(deck_hashes))
    query = f"SELECT deck_hash, card_name, card_level FROM deck_cards WHERE deck_hash IN ({placeholders})"
    
    cursor.execute(query, list(deck_hashes))
    rows = cursor.fetchall()
    
    decks = {}
    for d_hash, name, level in rows:
        if d_hash not in decks:
            decks[d_hash] = []
        decks[d_hash].append({"name": name, "level": level})
    return decks

def calculate_avg_level(deck_cards):
    if not deck_cards: return 0
    levels = [c['level'] for c in deck_cards if c.get('level') is not None]
    return statistics.mean(levels) if levels else 0

def analyze_level_volatility(players_sessions, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'level_volatility_results.txt')
    
    print(f"\nGenerazione report Level Volatility in: {output_file}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Costruisci la Curva Globale (Trophies -> Avg Level)
    # Serve per calcolare i residui e il delta atteso
    print("Calcolo curva globale dei livelli...")
    trophy_levels = defaultdict(list)
    BUCKET_SIZE = 100
    
    # Raccogli tutti i deck ID e trofei per la curva globale
    global_deck_ids = set()
    global_battles = [] # (trophies, deck_id)
    
    for p in players_sessions:
        for s in p['sessions']:
            for b in s['battles']:
                if b['game_mode'] == 'Ladder' and b.get('trophies_before') and b.get('opponent_deck_id'):
                    global_battles.append((b['trophies_before'], b['opponent_deck_id']))
                    global_deck_ids.add(b['opponent_deck_id'])
    
    # Fetch batch globale (chunked)
    deck_cache = {}
    all_ids_list = list(global_deck_ids)
    CHUNK = 1000
    for i in range(0, len(all_ids_list), CHUNK):
        batch = get_deck_cards_batch(cursor, all_ids_list[i:i+CHUNK])
        deck_cache.update(batch)
        
    # Popola bucket
    for t, d_id in global_battles:
        cards = deck_cache.get(d_id)
        if cards:
            lvl = calculate_avg_level(cards)
            if lvl > 0:
                b_idx = (t // BUCKET_SIZE) * BUCKET_SIZE
                trophy_levels[b_idx].append(lvl)
                
    # Calcola medie per bucket e pendenza
    bucket_means = {}
    sorted_buckets = sorted(trophy_levels.keys())
    for b in sorted_buckets:
        bucket_means[b] = statistics.mean(trophy_levels[b])
        
    # Calcola aumento medio per 100 trofei (slope)
    deltas = []
    for i in range(1, len(sorted_buckets)):
        b_curr = sorted_buckets[i]
        b_prev = sorted_buckets[i-1]
        if b_curr - b_prev == BUCKET_SIZE: # Solo bucket adiacenti
            diff = bucket_means[b_curr] - bucket_means[b_prev]
            deltas.append(diff)
            
    avg_increase_per_100 = statistics.mean(deltas) if deltas else 0
    print(f"Aumento medio livello per 100 trofei: {avg_increase_per_100:.4f}")
    
    # 2. Analisi Sequenziale: Debt Win vs Debt Lose
    print("Analisi sequenze Debt -> Next Match...")
    
    sequences = [] # (type, next_deck_id, next_trophies) type='win' or 'lose'
    
    # Debug counters
    debug_stats = {
        'total': 0, 
        'no_ladder': 0, 
        'no_matchup': 0, 
        'no_debt': 0, 
        'deck_change': 0, 
        'no_outcome': 0,
        'b2_incomplete': 0,
        'valid': 0
    }
    
    for p in players_sessions:
        for s in p['sessions']:
            battles = s['battles']
            for i in range(len(battles) - 1):
                debug_stats['total'] += 1
                b1 = battles[i]
                b2 = battles[i+1]
                
                if b1['game_mode'] != 'Ladder' or b2['game_mode'] != 'Ladder': 
                    debug_stats['no_ladder'] += 1
                    continue
                
                # Verifica Debt in b1 (Matchup < 45%)
                mu = b1.get('matchup')
                if mu is None:
                    debug_stats['no_matchup'] += 1
                    continue
                if mu >= 45.0: 
                    debug_stats['no_debt'] += 1
                    continue 
                
                # Verifica Player Deck Invariato
                if b1.get('deck_id') != b2.get('deck_id'): 
                    debug_stats['deck_change'] += 1
                    continue
                
                # Determina esito b1
                is_win = False
                is_loss = False
                if b1.get('trophies_change') is not None:
                    if b1['trophies_change'] > 0: is_win = True
                    elif b1['trophies_change'] < 0: is_loss = True
                elif b1.get('win') is not None:
                    if b1['win']: is_win = True
                    else: is_loss = True
                elif b1.get('winner'):
                    if b1['winner'] == p['tag']: is_win = True
                    else: is_loss = True
                
                if not is_win and not is_loss: 
                    debug_stats['no_outcome'] += 1
                    if debug_stats['no_outcome'] == 1:
                        print(f"DEBUG SAMPLE NO_OUTCOME: keys={list(b1.keys())}, trophies_change={b1.get('trophies_change')}, winner={b1.get('winner')}")
                    continue
                if not b2.get('opponent_deck_id') or not b2.get('trophies_before'): 
                    debug_stats['b2_incomplete'] += 1
                    if debug_stats['b2_incomplete'] == 1:
                        print(f"DEBUG SAMPLE B2_INCOMPLETE: keys={list(b2.keys())}")
                    continue
                
                seq_type = 'win' if is_win else 'lose'
                sequences.append((seq_type, b2['opponent_deck_id'], b2['trophies_before']))
                debug_stats['valid'] += 1

    print(f"Debug Stats: {debug_stats}")
    print(f"Sequenze trovate: {len(sequences)} (Win: {len([s for s in sequences if s[0]=='win'])}, Lose: {len([s for s in sequences if s[0]=='lose'])})")

    # Fetch deck mancanti per le sequenze
    needed_ids = set(s[1] for s in sequences) - set(deck_cache.keys())
    if needed_ids:
        needed_list = list(needed_ids)
        for i in range(0, len(needed_list), CHUNK):
            batch = get_deck_cards_batch(cursor, needed_list[i:i+CHUNK])
            deck_cache.update(batch)
            
    conn.close()
    
    # Calcola metriche
    raw_levels_win = []
    raw_levels_lose = []
    residuals_win = []
    residuals_lose = []
    
    for stype, d_id, trophies in sequences:
        cards = deck_cache.get(d_id)
        if not cards: continue
        lvl = calculate_avg_level(cards)
        if lvl == 0: continue
        
        # Trova livello atteso per questi trofei (bucket più vicino)
        b_idx = (trophies // BUCKET_SIZE) * BUCKET_SIZE
        expected = bucket_means.get(b_idx)
        if expected is None: continue
        
        residual = lvl - expected
        
        if stype == 'win':
            raw_levels_win.append(lvl)
            residuals_win.append(residual)
        else:
            raw_levels_lose.append(lvl)
            residuals_lose.append(residual)
            
    # Scrittura Report
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI VOLATILITÀ LIVELLI POST-DEBT (WIN vs LOSE)\n")
        f.write("Obiettivo: Verificare se il livello dell'avversario cambia coerentemente con i trofei dopo una vittoria 'Heroic' o una sconfitta in Debt.\n")
        f.write("Condizione Debt: Matchup < 45%.\n")
        f.write("Condizione Controllo: Il mazzo del giocatore deve rimanere invariato tra i due match.\n")
        f.write("="*80 + "\n\n")
        
        f.write(f"BASELINE GLOBALE:\n")
        f.write(f"Aumento medio livello avversario per 100 trofei: {avg_increase_per_100:.4f}\n")
        expected_delta_60 = (avg_increase_per_100 / 100) * 60
        f.write(f"Variazione attesa per swing di ~60 trofei (+30 vs -30): {expected_delta_60:.4f} livelli\n")
        f.write("-" * 80 + "\n\n")
        
        f.write("TEST 1: LIVELLI ASSOLUTI (Raw Opponent Level)\n")
        n_win = len(raw_levels_win)
        n_lose = len(raw_levels_lose)
        
        if n_win > 10 and n_lose > 10:
            avg_win = statistics.mean(raw_levels_win)
            avg_lose = statistics.mean(raw_levels_lose)
            delta_raw = avg_win - avg_lose
            
            t_stat, p_val = ttest_ind(raw_levels_win, raw_levels_lose, equal_var=False)
            
            f.write(f"Dopo Heroic Win (N={n_win}): {avg_win:.4f}\n")
            f.write(f"Dopo Debt Lose  (N={n_lose}): {avg_lose:.4f}\n")
            f.write(f"Delta Rilevato: {delta_raw:+.4f}\n")
            f.write(f"Delta Atteso (~60 trofei): {expected_delta_60:+.4f}\n")
            f.write(f"Differenza dal modello naturale: {delta_raw - expected_delta_60:+.4f}\n")
            f.write(f"Significatività statistica (T-test): p={p_val:.5f}\n")
            
            if abs(delta_raw - expected_delta_60) > 0.1:
                f.write(">> ANOMALIA: La variazione di livello è ECCESSIVA rispetto alla sola differenza di trofei.\n")
            else:
                f.write(">> COERENTE: La variazione sembra spiegata dai trofei.\n")
        else:
            f.write("Dati insufficienti per Test 1.\n")
            
        f.write("\n" + "-" * 80 + "\n\n")
        
        f.write("TEST 2: ANALISI RESIDUI (Opp Level - Avg Level @ Trophies)\n")
        f.write("Questo test rimuove l'effetto 'trofei' per vedere se il matchmaking 'punisce' o 'aiuta' relativamente alla fascia.\n")
        
        if n_win > 10 and n_lose > 10:
            res_win = statistics.mean(residuals_win)
            res_lose = statistics.mean(residuals_lose)
            delta_res = res_win - res_lose
            
            t_stat_res, p_val_res = ttest_ind(residuals_win, residuals_lose, equal_var=False)
            
            f.write(f"Residuo Medio dopo Heroic Win: {res_win:+.4f}\n")
            f.write(f"Residuo Medio dopo Debt Lose:  {res_lose:+.4f}\n")
            f.write(f"Delta Residui: {delta_res:+.4f}\n")
            f.write(f"Significatività (T-test): p={p_val_res:.5f}\n")
            
            if p_val_res < 0.05:
                if delta_res > 0:
                    f.write(">> RISULTATO: Dopo una vittoria, affronti avversari RELATIVAMENTE più forti rispetto alla media della fascia (Punizione/Challenge).\n")
                else:
                    f.write(">> RISULTATO: Dopo una vittoria, affronti avversari RELATIVAMENTE più deboli (improbabile).\n")
            else:
                f.write(">> RISULTATO: Nessuna differenza significativa nei residui. Il matchmaking sembra rispettare la media della fascia.\n")
        else:
            f.write("Dati insufficienti per Test 2.\n")
            
        f.write("="*80 + "\n")