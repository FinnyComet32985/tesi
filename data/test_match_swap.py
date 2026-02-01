import os
import sys
import sqlite3
import statistics
import random
from collections import defaultdict
from scipy.stats import ttest_rel

# Add parent directory to path to import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api_client import fetch_matchup
from data.test_deck_analysis import get_deck_cards_batch, get_local_hour
from battlelog_v2 import get_players_sessions # To run standalone

DB_PATH = os.path.join(os.path.dirname(__file__), '../db/clash.db')

def _calculate_avg_level(deck_cards):
    if not deck_cards: return 0
    levels = [c['level'] for c in deck_cards if c.get('level') is not None]
    return statistics.mean(levels) if levels else 0

def analyze_match_swap(players_sessions, cursor, output_dir=None, game_mode='Ladder'):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f'match_swap_{game_mode.lower()}_results.txt')
    
    print(f"\nGenerazione report Match Swap ({game_mode}) in: {output_file}")

    # Config
    NEG_THRESH = 45.0
    POS_THRESH = 55.0
    MAX_TESTS = 500
    
    # 1. Data Preparation
    print("Preparazione dati per Match Swap...")
    all_matches = []
    needed_decks = set()
    
    for p in players_sessions:
        tag = p['tag']
        region = p.get('nationality', 'Unknown')
        
        # Rolling window for recent winrate
        outcomes = []
        
        for s in p['sessions']:
            # Determine session type
            session_mus = [b.get('matchup_no_lvl') for b in s['battles'] if b.get('matchup_no_lvl') is not None and b['game_mode'] == game_mode]
            if not session_mus: continue
            
            avg_session_mu = statistics.mean(session_mus)
            session_type = None
            if avg_session_mu < NEG_THRESH: session_type = 'Neg'
            elif avg_session_mu > POS_THRESH: session_type = 'Pos'
            
            if not session_type: continue

            for b in s['battles']:
                if b['game_mode'] != game_mode: continue
                
                p_deck = b.get('deck_id')
                o_deck = b.get('opponent_deck_id')
                ts = b.get('timestamp')
                trophies = b.get('trophies_before')
                mu_nolvl = b.get('matchup_no_lvl')
                
                if not all([p_deck, o_deck, ts, mu_nolvl]): continue
                if game_mode == 'Ladder' and trophies is None: continue
                
                needed_decks.add(p_deck)
                needed_decks.add(o_deck)
                
                recent_wr = sum(outcomes[-5:]) / len(outcomes[-5:]) if outcomes else 0.5
                outcomes.append(b['win'])
                
                all_matches.append({
                    'session_type': session_type,
                    'p_deck': p_deck,
                    'o_deck': o_deck,
                    'mu_nolvl': mu_nolvl,
                    'region': region,
                    'hour': get_local_hour(ts, region),
                    'trophies': trophies,
                    'recent_wr': recent_wr
                })

    # Fetch Cards and calculate avg levels
    print(f"Recupero carte e calcolo livelli medi per {len(needed_decks)} mazzi...")
    deck_cards_cache = {}
    deck_levels_cache = {}
    all_ids = list(needed_decks)
    CHUNK = 900
    for i in range(0, len(all_ids), CHUNK):
        batch = get_deck_cards_batch(cursor, all_ids[i:i+CHUNK])
        deck_cards_cache.update(batch)
        for d_id, cards in batch.items():
            deck_levels_cache[d_id] = _calculate_avg_level(cards)

    # Add avg_deck_level to matches
    for match in all_matches:
        match['avg_deck_level'] = deck_levels_cache.get(match['p_deck'], 0)

    # 2. Bucketing & Matching
    print("Esecuzione Pseudo-Swap (questo potrebbe richiedere tempo)...")
    
    neg_matches = [m for m in all_matches if m['session_type'] == 'Neg']
    pos_matches_buckets = defaultdict(list)
    for m in all_matches:
        if m['session_type'] == 'Pos':
            key = (m['region'], m['hour'], m['trophies'] // 50 if m['trophies'] is not None else 'Ranked')
            pos_matches_buckets[key].append(m)
            
    results = [] # (real_mu, hypo_mu)
    tests_done = 0
    
    random.shuffle(neg_matches) # Process in random order
    
    for neg_match in neg_matches:
        if tests_done >= MAX_TESTS: break
        
        key = (neg_match['region'], neg_match['hour'], neg_match['trophies'] // 50 if neg_match['trophies'] is not None else 'Ranked')
        
        candidates = pos_matches_buckets.get(key, [])
        if not candidates: continue
        
        # Find a good match
        best_candidate = None
        min_dist = float('inf')
        
        for pos_match in candidates:
            # Calculate distance based on winrate and level
            dist = (abs(neg_match['recent_wr'] - pos_match['recent_wr']) + 
                    abs(neg_match['avg_deck_level'] - pos_match['avg_deck_level']) / 14.0) # Normalize level diff
            
            if dist < min_dist:
                min_dist = dist
                best_candidate = pos_match
        
        if best_candidate and min_dist < 0.3: # Threshold for a "good enough" match
            # Perform Swap
            deck_A_cards = deck_cards_cache.get(neg_match['p_deck'])
            opp_B_cards = deck_cards_cache.get(best_candidate['o_deck'])
            
            if deck_A_cards and opp_B_cards:
                mu_data = fetch_matchup(deck_A_cards, opp_B_cards, force_equal_levels=True)
                if mu_data and 'winRate' in mu_data:
                    hypo_mu = mu_data['winRate'] * 100
                    results.append((neg_match['mu_nolvl'], hypo_mu))
                    tests_done += 1
                    print(f"Test {tests_done}/{MAX_TESTS} completato.", end='\r')

    # 3. Report
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"ANALISI MATCH SWAP (PSEUDO A/B TESTING) - {game_mode.upper()}\n")
        f.write("Obiettivo: Verificare se gli avversari di una sessione 'Positiva' sono più facili per un mazzo che era in una sessione 'Negativa'.\n")
        f.write("Metodo: Per ogni match in sessione Negativa, si trova un match 'gemello' in una sessione Positiva (stessi trofei, ora, regione, wr, livelli).\n")
        f.write("        Si calcola il matchup ipotetico del mazzo 'sfortunato' contro l'avversario 'fortunato'.\n")
        f.write("="*80 + "\n\n")
        
        if not results:
            f.write("Nessun test eseguito (dati insufficienti o limite API).\n")
            return
            
        real_vals = [r[0] for r in results]
        hypo_vals = [r[1] for r in results]
        
        avg_real = statistics.mean(real_vals)
        avg_hypo = statistics.mean(hypo_vals)
        
        f.write(f"Campione: {len(results)} coppie di match.\n")
        f.write(f"Matchup Medio REALE (in Sessione Negativa):      {avg_real:.2f}%\n")
        f.write(f"Matchup Medio IPOTETICO (vs Opponent Fortunato): {avg_hypo:.2f}%\n")
        f.write(f"Delta (Ipotetico - Reale):                       {avg_hypo - avg_real:+.2f}%\n")
        
        stat, p_val = ttest_rel(hypo_vals, real_vals)
        f.write(f"P-value (T-Test Paired): {p_val:.4f}\n")
        
        if p_val < 0.05 and (avg_hypo - avg_real) > 1.0:
            f.write("RISULTATO: SIGNIFICATIVO. Gli avversari delle sessioni positive sono più facili.\n")
            f.write("-> EVIDENZA DI TARGETING: Il pool di avversari non è uniforme, ma dipende dallo stato (Neg/Pos) del giocatore.\n")
        else:
            f.write("RISULTATO: NON SIGNIFICATIVO. Gli avversari sembrano pescati dallo stesso pool casuale.\n")
            
        f.write("="*80 + "\n")

if __name__ == "__main__":
    # Standalone execution example
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    players_sessions = get_players_sessions(mode_filter='Ladder', exclude_unreliable=True)
    analyze_match_swap(players_sessions, cursor)
    conn.close()