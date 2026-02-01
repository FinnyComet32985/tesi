import os
import sys
import sqlite3
import statistics
import random
from datetime import datetime
from collections import defaultdict
from scipy.stats import ttest_rel

# Add parent directory to path to import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api_client import fetch_matchup
from data.test_deck_analysis import get_deck_cards_batch, get_local_hour

DB_PATH = os.path.join(os.path.dirname(__file__), '../db/clash.db')

WIN_CONDITIONS = {
    'Hog Rider', 'Giant', 'Golem', 'P.E.K.K.A', 'Miner', 'Goblin Barrel',
    'Balloon', 'X-Bow', 'Mortar', 'Royal Giant', 'Lava Hound', 'Graveyard',
    'Sparky', 'Mega Knight', 'Electro Giant', 'Ram Rider', 'Elixir Golem',
    'Skeleton Barrel', 'Wall Breakers', 'Three Musketeers', 'Goblin Giant',
    'Battle Ram', 'Goblin Drill', 'Royal Hogs'
}

def analyze_session_swap(players_sessions, cursor, output_dir=None, game_mode='Ladder'):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f'session_swap_{game_mode.lower()}_results.txt')
    
    print(f"\nGenerazione report Session Swap ({game_mode}) in: {output_file}")
    
    # 1. Raggruppa Sessioni in Bucket (Region, TimeSlot, TrophyRange)
    # Bucket Key: (Region, Hour//4, Trophy//500)
    # Value: List of { 'player_tag': tag, 'deck_id': deck_id, 'opp_deck_ids': [list], 'real_avg_mu': val }
    buckets = defaultdict(list)
    
    # Cache deck cards
    deck_cards_cache = {}
    needed_decks = set()
    
    print("Raggruppamento sessioni...")
    for p in players_sessions:
        tag = p['tag']
        region = p.get('nationality', 'Unknown')
        
        for s in p['sessions']:
            battles = [b for b in s['battles'] if b['game_mode'] == game_mode and b.get('matchup_no_lvl') is not None]
            if len(battles) < 3: continue
            
            # Verifica consistenza deck (Player deve usare lo stesso deck nella sessione)
            decks = {b['deck_id'] for b in battles if b.get('deck_id')}
            if len(decks) != 1: continue
            main_deck = list(decks)[0]
            
            # Dati Bucket
            first_b = battles[0]
            ts = first_b.get('timestamp')
            trophies = first_b.get('trophies_before')
            if not ts: continue
            if game_mode == 'Ladder' and trophies is None: continue
            
            hour = get_local_hour(ts, region)
            time_slot = hour // 4 # 6 fasce orarie
            
            if game_mode == 'Ranked':
                trophy_bucket = 'Ranked'
            else:
                bucket_size = 500
                trophy_bucket = trophies // bucket_size
            
            key = (region, time_slot, trophy_bucket)
            
            opp_decks = [b['opponent_deck_id'] for b in battles if b.get('opponent_deck_id')]
            if not opp_decks: continue
            
            avg_mu = statistics.mean([b['matchup_no_lvl'] for b in battles])
            
            buckets[key].append({
                'tag': tag,
                'deck_id': main_deck,
                'opp_deck_ids': opp_decks,
                'real_avg_mu': avg_mu
            })
            
            needed_decks.add(main_deck)
            for od in opp_decks: needed_decks.add(od)

    # Fetch Cards
    print(f"Recupero carte per {len(needed_decks)} mazzi...")
    all_ids = list(needed_decks)
    CHUNK = 900
    for i in range(0, len(all_ids), CHUNK):
        batch = get_deck_cards_batch(cursor, all_ids[i:i+CHUNK])
        deck_cards_cache.update(batch)

    # 2. Esegui Swap Test
    # Per ogni bucket con almeno 2 sessioni di player DIVERSI
    results = [] # (real_mu, hypo_mu)
    
    MAX_TESTS = 200 # Limite per evitare troppe chiamate API (fetch_matchup è lento)
    tests_done = 0
    
    print("Esecuzione Swap Test (questo potrebbe richiedere tempo)...")
    
    sorted_keys = sorted(buckets.keys())
    random.shuffle(sorted_keys) # Randomizza per avere varietà
    
    for key in sorted_keys:
        sessions = buckets[key]
        if len(sessions) < 2: continue
        
        # Trova coppie di player diversi
        for i in range(len(sessions)):
            if tests_done >= MAX_TESTS: break
            
            sess_A = sessions[i]
            
            # Cerca un partner B diverso
            candidates_B = [s for s in sessions if s['tag'] != sess_A['tag']]
            if not candidates_B: continue
            
            sess_B = random.choice(candidates_B)
            
            # Calcola Matchup Ipotetico: Deck A vs Opponents B
            deck_A_cards = deck_cards_cache.get(sess_A['deck_id'])
            if not deck_A_cards: continue
            
            hypo_mus = []
            for opp_id in sess_B['opp_deck_ids']:
                opp_cards = deck_cards_cache.get(opp_id)
                if opp_cards:
                    # API Call
                    mu_data = fetch_matchup(deck_A_cards, opp_cards, force_equal_levels=True)
                    if mu_data and 'winRate' in mu_data:
                        hypo_mus.append(mu_data['winRate'] * 100)
            
            if hypo_mus:
                avg_hypo = statistics.mean(hypo_mus)
                results.append((sess_A['real_avg_mu'], avg_hypo))
                tests_done += 1
                print(f"Test {tests_done}/{MAX_TESTS} completato.", end='\r')

    # 3. Report
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"ANALISI SESSION SWAP ({game_mode.upper()}) - A/B TESTING RETROATTIVO\n")
        f.write("Obiettivo: Verificare se gli avversari incontrati sono specifici per il mazzo del giocatore.\n")
        f.write("Metodo: Prendiamo il Deck A e calcoliamo come avrebbe performato contro gli avversari del Player B\n")
        if game_mode == 'Ladder':
            f.write("        (che giocava nella stessa regione, stessa settimana, orario e fascia trofei).\n")
        else:
            f.write("        (che giocava nella stessa regione, stessa settimana e orario).\n")
        f.write("="*80 + "\n\n")
        
        if not results:
            f.write("Nessun test eseguito (dati insufficienti o limite API).\n")
            return
            
        real_vals = [r[0] for r in results]
        hypo_vals = [r[1] for r in results]
        
        avg_real = statistics.mean(real_vals)
        avg_hypo = statistics.mean(hypo_vals)
        
        f.write(f"Campione: {len(results)} sessioni scambiate.\n")
        f.write(f"Matchup Medio REALE (Deck A vs Opp A):      {avg_real:.2f}%\n")
        f.write(f"Matchup Medio IPOTETICO (Deck A vs Opp B):  {avg_hypo:.2f}%\n")
        f.write(f"Delta (Reale - Ipotetico):                  {avg_real - avg_hypo:+.2f}%\n")
        
        # T-Test Paired
        stat, p_val = ttest_rel(real_vals, hypo_vals)
        f.write(f"P-value (T-Test Paired): {p_val:.4f}\n")
        
        if p_val < 0.05:
            f.write("RISULTATO: SIGNIFICATIVO. Gli avversari del Player A sono statisticamente diversi da quelli del Player B.\n")
            if avg_real < avg_hypo:
                f.write("-> RIGGED? Il matchup reale è PEGGIORE di quello che avrebbe avuto contro gli avversari di B.\n")
            else:
                f.write("-> FAVOREVOLE? Il matchup reale è MIGLIORE.\n")
        else:
            f.write("RISULTATO: NON SIGNIFICATIVO. Gli avversari sembrano pescati dallo stesso pool casuale.\n")
            
        f.write("="*80 + "\n")

def analyze_session_swap_conditional(players_sessions, cursor, output_dir=None, game_mode='Ladder'):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f'session_swap_conditional_{game_mode.lower()}_results.txt')
    
    print(f"\nGenerazione report Session Swap Condizionale ({game_mode}) in: {output_file}")

    # Config
    NEG_THRESH = 45.0
    POS_THRESH = 55.0
    MAX_SHARED_CARDS = 3 # Decks are "different" if they share <= 3 cards
    MAX_TESTS_PER_CATEGORY = 200 # Limit API calls per category

    # Buckets: key -> { 'Neg': [], 'Pos': [] }
    buckets = defaultdict(lambda: {'Neg': [], 'Pos': []})
    needed_decks = set()

    print("Classificazione sessioni...")
    for p in players_sessions:
        tag = p['tag']
        region = p.get('nationality', 'Unknown')
        
        for s in p['sessions']:
            battles = [b for b in s['battles'] if b['game_mode'] == game_mode and b.get('matchup_no_lvl') is not None]
            if len(battles) < 3: continue
            
            # Consistency check
            decks = {b['deck_id'] for b in battles if b.get('deck_id')}
            if len(decks) != 1: continue
            main_deck = list(decks)[0]
            
            # Bucket info
            first_b = battles[0]
            ts = first_b.get('timestamp')
            trophies = first_b.get('trophies_before')
            if not ts: continue
            if game_mode == 'Ladder' and trophies is None: continue

            # Estrai data per vincolo temporale stretto
            try:
                dt = datetime.strptime(ts, '%Y-%m-%d %H:%M:%S')
                date_str = dt.strftime('%Y-%W')
            except ValueError:
                continue

            hour = get_local_hour(ts, region)
            time_slot = hour // 4
            
            if game_mode == 'Ranked':
                trophy_bucket = 'Ranked'
            else:
                trophy_bucket = trophies // 500
            
            # Aggiunta data alla chiave del bucket
            key = (region, date_str, time_slot, trophy_bucket)
            
            avg_mu = statistics.mean([b['matchup_no_lvl'] for b in battles])
            
            cat = None
            if avg_mu < NEG_THRESH: cat = 'Neg'
            elif avg_mu > POS_THRESH: cat = 'Pos'
            
            if cat:
                opp_decks = [b['opponent_deck_id'] for b in battles if b.get('opponent_deck_id')]
                if not opp_decks: continue
                
                buckets[key][cat].append({
                    'tag': tag,
                    'deck_id': main_deck,
                    'opp_deck_ids': opp_decks,
                    'real_avg_mu': avg_mu
                })
                needed_decks.add(main_deck)
                for od in opp_decks: needed_decks.add(od)

    # Fetch Cards
    print(f"Recupero carte per {len(needed_decks)} mazzi...")
    deck_cards_cache = {}
    all_ids = list(needed_decks)
    CHUNK = 900
    for i in range(0, len(all_ids), CHUNK):
        batch = get_deck_cards_batch(cursor, all_ids[i:i+CHUNK])
        deck_cards_cache.update(batch)

    # Helper for deck difference
    def are_decks_different(d1_id, d2_id):
        c1 = deck_cards_cache.get(d1_id)
        c2 = deck_cards_cache.get(d2_id)
        if not c1 or not c2: return False
        s1 = {c['name'] for c in c1}
        s2 = {c['name'] for c in c2}
        
        # 1. Controllo carte condivise (strutturale)
        if len(s1 & s2) > MAX_SHARED_CARDS:
            return False
            
        # 2. Controllo Win Condition condivise (archetipale)
        wc1 = s1 & WIN_CONDITIONS
        wc2 = s2 & WIN_CONDITIONS
        if not wc1.isdisjoint(wc2): # Se condividono almeno una WC
            return False
            
        return True

    # Categories to test
    comparisons = [
        ('Neg', 'Neg', 'Negative vs Negative (Diff Deck)'),
        ('Pos', 'Pos', 'Positive vs Positive (Diff Deck)'),
        ('Neg', 'Pos', 'Negative vs Positive (Diff Deck)')
    ]
    
    results = {label: [] for _, _, label in comparisons}

    print("Esecuzione Swap Condizionali...")
    
    for catA, catB, label in comparisons:
        tests_done = 0
        sorted_keys = sorted(buckets.keys())
        random.shuffle(sorted_keys)
        
        for key in sorted_keys:
            if tests_done >= MAX_TESTS_PER_CATEGORY: break
            
            groupA = buckets[key][catA]
            groupB = buckets[key][catB]
            
            if not groupA or not groupB: continue
            
            # Shuffle to randomize
            random.shuffle(groupA)
            random.shuffle(groupB)
            
            for sA in groupA:
                if tests_done >= MAX_TESTS_PER_CATEGORY: break
                
                for sB in groupB:
                    if sA['tag'] == sB['tag']: continue # Skip same player
                    
                    if are_decks_different(sA['deck_id'], sB['deck_id']):
                        # Perform Swap: Deck A vs Opponents B
                        deck_A_cards = deck_cards_cache.get(sA['deck_id'])
                        hypo_mus = []
                        
                        for opp_id in sB['opp_deck_ids']:
                            opp_cards = deck_cards_cache.get(opp_id)
                            if opp_cards:
                                mu_data = fetch_matchup(deck_A_cards, opp_cards, force_equal_levels=True)
                                if mu_data and 'winRate' in mu_data:
                                    hypo_mus.append(mu_data['winRate'] * 100)
                        
                        if hypo_mus:
                            avg_hypo = statistics.mean(hypo_mus)
                            # We record: (Real A, Hypo A on B's opps)
                            results[label].append((sA['real_avg_mu'], avg_hypo))
                            tests_done += 1
                            print(f"[{label}] Test {tests_done}/{MAX_TESTS_PER_CATEGORY}", end='\r')
                            break # Move to next sA to avoid reusing same A too much

    # Report
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"ANALISI SESSION SWAP CONDIZIONALE ({game_mode.upper()})\n")
        f.write("Obiettivo: Confrontare sessioni con esiti specifici (Neg/Pos) tra giocatori con mazzi DIVERSI.\n")
        f.write(f"Definizioni: Neg < {NEG_THRESH}%, Pos > {POS_THRESH}%.\n")
        
        constraints = "Stessa Regione, Stessa Settimana, Stesso Slot Orario (4h)"
        if game_mode == 'Ladder':
            constraints += ", Stessa Fascia Trofei (500)"
            
        f.write(f"Vincoli: {constraints}.\n")
        f.write(f"Diff Deck: Shared Cards <= {MAX_SHARED_CARDS} AND No Shared Win Conditions.\n")
        f.write("="*100 + "\n\n")
        
        for _, _, label in comparisons:
            data = results[label]
            f.write(f"--- {label} ---\n")
            if not data:
                f.write("Dati insufficienti.\n\n")
                continue
                
            real_vals = [x[0] for x in data]
            hypo_vals = [x[1] for x in data]
            
            avg_real = statistics.mean(real_vals)
            avg_hypo = statistics.mean(hypo_vals)
            delta = avg_real - avg_hypo # Real - Hypo. If Real < Hypo, Real was worse.
            
            f.write(f"Campione: {len(data)} coppie.\n")
            f.write(f"Matchup Reale (Player A):      {avg_real:.2f}%\n")
            f.write(f"Matchup Ipotetico (A vs Opp B): {avg_hypo:.2f}%\n")
            f.write(f"Delta (Reale - Ipotetico):      {delta:+.2f}%\n")
            
            stat, p_val = ttest_rel(real_vals, hypo_vals)
            f.write(f"P-value (Paired T-Test): {p_val:.4f}\n")
            
            if p_val < 0.05:
                f.write("RISULTATO: SIGNIFICATIVO.\n")
                if "Negative vs Negative" in label:
                    if delta < 0:
                        f.write("-> RIGGED? Player A ha avuto avversari peggiori di quelli che avrebbe trovato al posto di B.\n")
                        f.write("   (Anche B era in sessione negativa, ma i suoi avversari erano specifici per B e non per A).\n")
                    else:
                        f.write("-> NEUTRO/STRANO. Player A ha avuto avversari migliori di quelli di B.\n")
                elif "Negative vs Positive" in label:
                    if delta < -5.0:
                        f.write("-> RIGGED. A è stato punito con counter specifici, mentre B aveva avversari facili.\n")
            else:
                f.write("RISULTATO: NON SIGNIFICATIVO. Gli avversari sembrano intercambiabili.\n")
            f.write("\n")
        f.write("="*100 + "\n")