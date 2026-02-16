import os
import statistics
import sys
from scipy.stats import spearmanr, kruskal
from collections import defaultdict

# Add parent directory to path to import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from test_deck_analysis import get_deck_cards_batch, get_deck_archetypes_batch, get_local_hour

def _get_deck_and_tower_levels(cards, tower_names):
    """Estrae il livello medio del mazzo (8 carte) e il livello della torre."""
    if not cards:
        return 0, 0
    
    deck_cards = [c for c in cards if c.get('name') not in tower_names]
    tower_card = next((c for c in cards if c.get('name') in tower_names), None)

    deck_levels = [c['level'] for c in deck_cards if c.get('level') is not None]
    avg_deck_level = statistics.mean(deck_levels) if deck_levels else 0
    
    tower_level = tower_card['level'] if tower_card and tower_card.get('level') is not None else 0
    
    return avg_deck_level, tower_level

def analyze_confounding_variables(players_sessions, cursor, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'confounding_variables_results.txt')

    print(f"\nGenerazione report Variabili Confondenti (Livelli Opponent & Matchup) in: {output_file}")

    # 1. Data Collection
    data_points = []
    deck_ids_to_fetch = set()
    p_deck_ids_to_fetch = set()

    for p in players_sessions:
        nationality = p.get('nationality')
        for s in p['sessions']:
            for b in s['battles']:
                if b['game_mode'] != 'Ladder': continue
                
                t = b.get('trophies_before')
                o_id = b.get('opponent_deck_id')
                p_id = b.get('deck_id')
                mu_nolvl = b.get('matchup_no_lvl')
                ts = b.get('timestamp')

                if t and o_id and p_id and ts:
                    data_points.append({
                        'trophies': t,
                        'o_deck_id': o_id,
                        'p_deck_id': p_id,
                        'mu_nolvl': mu_nolvl,
                        'hour': get_local_hour(ts, nationality)
                    })
                    deck_ids_to_fetch.add(o_id)
                    p_deck_ids_to_fetch.add(p_id)

    if not data_points:
        print("Nessun dato trovato per l'analisi.")
        return

    # 2. Fetch Data
    print(f"Recupero dati per {len(deck_ids_to_fetch)} mazzi avversari e {len(p_deck_ids_to_fetch)} mazzi player...")
    
    # Recupera i nomi delle torri dal DB
    tower_names = set()
    try:
        cursor.execute("SELECT card_name FROM cards WHERE type='Tower'")
        tower_names = {row[0] for row in cursor.fetchall()}
    except Exception as e:
        print(f"Warning: Impossibile recuperare nomi torri ({e}). Uso default.")
        tower_names = {'King Tower', 'Princess Tower', 'Cannoneer', 'Dagger Duchess'}

    # Opponent Cards (for Levels)
    o_deck_stats = {}
    all_o_ids = list(deck_ids_to_fetch)
    CHUNK = 900
    for i in range(0, len(all_o_ids), CHUNK):
        batch = get_deck_cards_batch(cursor, all_o_ids[i:i+CHUNK])
        for d_id, cards in batch.items():
            o_deck_stats[d_id] = _get_deck_and_tower_levels(cards, tower_names)

    # Player Cards (for Levels)
    p_deck_stats = {}
    all_p_ids_list = list(p_deck_ids_to_fetch)
    for i in range(0, len(all_p_ids_list), CHUNK):
        batch = get_deck_cards_batch(cursor, all_p_ids_list[i:i+CHUNK])
        for d_id, cards in batch.items():
            p_deck_stats[d_id] = _get_deck_and_tower_levels(cards, tower_names)

    # Player Archetypes
    p_deck_archs = {}
    all_p_ids = list(p_deck_ids_to_fetch)
    for i in range(0, len(all_p_ids), CHUNK):
        batch = get_deck_archetypes_batch(cursor, all_p_ids[i:i+CHUNK])
        p_deck_archs.update(batch)

    # Enrich Data
    valid_data = []
    for d in data_points:
        if d['o_deck_id'] in o_deck_stats and d['p_deck_id'] in p_deck_archs and d['p_deck_id'] in p_deck_stats:
            d['o_avg_lvl'], d['o_tower_lvl'] = o_deck_stats[d['o_deck_id']]
            d['p_avg_lvl'], d['p_tower_lvl'] = p_deck_stats[d['p_deck_id']]
            d['p_arch'] = p_deck_archs[d['p_deck_id']]
            valid_data.append(d)

    if not valid_data:
        print("Dati insufficienti dopo il fetch.")
        return

    # 3. Analysis
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI VARIABILI CONFONDENTI: LIVELLI AVVERSARI E MATCHUP\n")
        f.write("Obiettivo: Isolare la dipendenza di Livelli Avversari e Matchup da Trofei, Orario e Mazzo.\n")
        f.write("Nota: Analizziamo i LIVELLI CARTE (Avg) perché riflettono la forza reale del mazzo.\n")
        f.write("      Il matchmaking usa il Livello Torre, che correla con le carte ma non è identico.\n")
        f.write("="*100 + "\n\n")

        # A. TROPHY DEPENDENCY (Global Correlation)
        trophies = [d['trophies'] for d in valid_data]
        o_levels = [d['o_avg_lvl'] for d in valid_data]
        p_levels = [d['p_avg_lvl'] for d in valid_data]
        mus = [d['mu_nolvl'] for d in valid_data if d['mu_nolvl'] is not None]
        trophies_mu = [d['trophies'] for d in valid_data if d['mu_nolvl'] is not None]

        f.write("1. DIPENDENZA DAI TROFEI E MATCHMAKING (Correlazione Globale)\n")
        f.write("-" * 80 + "\n")
        
        # Levels vs Trophies
        if len(trophies) > 10:
            corr_l, p_l = spearmanr(trophies, o_levels)
            f.write(f"Opponent Avg Deck Level vs Trophies:      Corr={corr_l:.4f}, p={p_l:.4f}\n")
            
            corr_pl, p_pl = spearmanr(trophies, p_levels)
            f.write(f"Player Avg Deck Level vs Trophies:        Corr={corr_pl:.4f}, p={p_pl:.4f}\n")

            corr_po, p_po = spearmanr(p_levels, o_levels)
            f.write(f"Player Deck Level vs Opponent Deck Level: Corr={corr_po:.4f}, p={p_po:.4f}\n")
            
            # --- NEW CORRELATIONS ---
            # Player Tower Level vs Player Deck Level
            p_tower_lvls_data = [(d['p_tower_lvl'], d['p_avg_lvl']) for d in valid_data if d['p_tower_lvl'] > 0]
            if len(p_tower_lvls_data) > 10:
                p_tower_lvls = [d[0] for d in p_tower_lvls_data]
                p_deck_lvls_for_tower = [d[1] for d in p_tower_lvls_data]
                corr_pt_pd, p_pt_pd = spearmanr(p_tower_lvls, p_deck_lvls_for_tower)
                f.write(f"Player Tower Level vs Player Deck Level:  Corr={corr_pt_pd:.4f}, p={p_pt_pd:.4f}\n")

            # Player Tower Level vs Opponent Tower Level
            tower_pairs = [(d['p_tower_lvl'], d['o_tower_lvl']) for d in valid_data if d['p_tower_lvl'] > 0 and d['o_tower_lvl'] > 0]
            if len(tower_pairs) > 10:
                p_towers = [p[0] for p in tower_pairs]
                o_towers = [p[1] for p in tower_pairs]
                corr_pt_ot, p_pt_ot = spearmanr(p_towers, o_towers)
                f.write(f"Player Tower Level vs Opponent Tower Level: Corr={corr_pt_ot:.4f}, p={p_pt_ot:.4f}\n")
            
            if corr_po > 0.6:
                f.write("-> MATCHMAKING EQUILIBRATO: I livelli carte player/opponent sono fortemente legati.\n")
                f.write("   (Probabilmente mediato dal Livello Torre, usato dal matchmaking).\n")
        
        # Matchup vs Trophies
        if len(mus) > 10:
            corr_m, p_m = spearmanr(trophies_mu, mus)
            f.write(f"Matchup No-Lvl vs Trophies:         Corr={corr_m:.4f}, p={p_m:.4f}\n")
        if len(trophies) > 10:
            f.write("\n")

        # B. CONTROLLED ANALYSIS (Within Trophy Buckets)
        f.write("2. ANALISI CONTROLLATA PER FASCIA TROFEI (Bucket 500)\n")
        f.write("Verifica dipendenza da ORARIO e MAZZO PLAYER a parità di trofei.\n")
        f.write("-" * 100 + "\n")
        f.write(f"{'BUCKET':<12} | {'VAR':<10} | {'FACTOR':<10} | {'P-VALUE':<10} | {'RESULT'}\n")
        f.write("-" * 100 + "\n")

        BUCKET_SIZE = 500
        buckets = defaultdict(list)
        for d in valid_data:
            b_idx = (d['trophies'] // BUCKET_SIZE) * BUCKET_SIZE
            buckets[b_idx].append(d)

        for b_idx in sorted(buckets.keys()):
            subset = buckets[b_idx]
            if len(subset) < 50: continue
            
            label = f"{b_idx}-{b_idx+BUCKET_SIZE}"

            # --- TIME DEPENDENCY ---
            # Group by Time Slot (4 slots)
            slots = defaultdict(list)
            for d in subset:
                slot = d['hour'] // 6 # 0-3
                slots[slot].append(d)
            
            # Test Levels vs Time
            groups_l = [[d['o_avg_lvl'] for d in s_data] for s_data in slots.values() if len(s_data) > 5]
            if len(groups_l) > 1:
                try:
                    stat, p = kruskal(*groups_l)
                    sig = "SIGNIFICATIVO" if p < 0.05 else "NO"
                    f.write(f"{label:<12} | {'Opp Lvl':<10} | {'Time':<10} | {p:<10.4f} | {sig}\n")
                except ValueError: pass

            # Test Matchup vs Time
            groups_m = [[d['mu_nolvl'] for d in s_data if d['mu_nolvl'] is not None] for s_data in slots.values()]
            groups_m = [g for g in groups_m if len(g) > 5]
            if len(groups_m) > 1:
                try:
                    stat, p = kruskal(*groups_m)
                    sig = "SIGNIFICATIVO" if p < 0.05 else "NO"
                    f.write(f"{label:<12} | {'Mu No-lvl':<10} | {'Time':<10} | {p:<10.4f} | {sig}\n")
                except ValueError: pass

            # --- DECK DEPENDENCY ---
            # Group by Player Archetype
            archs = defaultdict(list)
            for d in subset:
                archs[d['p_arch']].append(d)
            
            # Filter top archetypes
            top_archs = [k for k, v in archs.items() if len(v) >= 10]
            if len(top_archs) < 2: continue

            # Test Levels vs Player Deck
            groups_l = [[d['o_avg_lvl'] for d in archs[a]] for a in top_archs]
            if len(groups_l) > 1:
                try:
                    stat, p = kruskal(*groups_l)
                    sig = "SIGNIFICATIVO" if p < 0.05 else "NO"
                    f.write(f"{label:<12} | {'Opp Lvl':<10} | {'Deck':<10} | {p:<10.4f} | {sig}\n")
                except ValueError: pass
            
            # Test Matchup vs Player Deck
            groups_m = [[d['mu_nolvl'] for d in archs[a] if d['mu_nolvl'] is not None] for a in top_archs]
            groups_m = [g for g in groups_m if len(g) >= 10]
            if len(groups_m) > 1:
                try:
                    stat, p = kruskal(*groups_m)
                    sig = "SIGNIFICATIVO" if p < 0.05 else "NO"
                    f.write(f"{label:<12} | {'Mu No-lvl':<10} | {'Deck':<10} | {p:<10.4f} | {sig}\n")
                except ValueError: pass
            
            # Test Player Levels vs Player Deck (Controllo Ipotesi Demografica)
            groups_pl = [[d['p_avg_lvl'] for d in archs[a]] for a in top_archs]
            if len(groups_pl) > 1:
                try:
                    stat, p = kruskal(*groups_pl)
                    sig = "SIGNIFICATIVO" if p < 0.05 else "NO"
                    f.write(f"{label:<12} | {'Player Lvl':<10} | {'Deck':<10} | {p:<10.4f} | {sig}\n")
                except ValueError: pass

            f.write("-" * 100 + "\n")
