import sqlite3
from collections import Counter, defaultdict
import os
import statistics


def analyze_arena_gatekeeping(players_sessions, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'arena_gatekeeping_results.txt')
    
    print(f"\nGenerazione report Arena Gatekeeping in: {output_file}")
    
    db_path = os.path.join(os.path.dirname(__file__), '../db/clash.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Fetch Arena Limits
    try:
        cursor.execute("SELECT trophy_limit, arena_name FROM arenas ORDER BY trophy_limit ASC")
        arenas = cursor.fetchall()
    except Exception as e:
        print(f"Errore DB Arenas: {e}")
        arenas = []
        
    # Filter arenas (ignore tutorial/low arenas if needed, here we take all > 0)
    gate_limits = [row[0] for row in arenas if row[0] > 0]
    
    # Zones configuration
    # PRE-STABLE: [-150, -75)
    # PRE-EARLY:  [-75, 0)  <-- Danger Zone
    # POST-EARLY: [0, 75)   <-- Meta Shock
    # POST-STABLE: [75, 150] <-- Settled
    
    zones = ['pre_stable', 'pre_early', 'post_early', 'post_stable']
    
    # Data structures: gate -> zone -> stats
    gate_data = {
        limit: {
            z: {'mus': [], 'opp_decks': [], 'switches': 0, 'battles': 0, 'player_mus': []}
            for z in zones
        } for limit in gate_limits
    }
    
    # Data structure for attempts analysis: gate -> attempt_num -> list of (tag, mu)
    gate_attempts = {limit: defaultdict(list) for limit in gate_limits}

    # Calculate Global Avg MU per player for Hostility calculation
    player_global_mu = {}
    for p in players_sessions:
        mus = []
        for s in p['sessions']:
            for b in s['battles']:
                if b.get('matchup_no_lvl') is not None:
                    mus.append(b['matchup_no_lvl'])
        if mus:
            player_global_mu[p['tag']] = statistics.mean(mus)
            
    # Collect Data
    all_opp_deck_ids = set()
    
    for p in players_sessions:
        tag = p['tag']
        if tag not in player_global_mu: continue
        
        all_battles = []
        for s in p['sessions']:
            all_battles.extend(s['battles'])
            
        prev_deck = None
        
        # State for attempts per gate for current player
        player_gate_state = {limit: {'in_zone': False, 'attempt': 0} for limit in gate_limits}
        
        for b in all_battles:
            if b['game_mode'] != 'Ladder': continue
            
            t = b.get('trophies_before')
            if not t: continue
            
            mu = b.get('matchup_no_lvl')
            if mu is None: continue
            
            deck = b.get('deck_id')
            opp_deck = b.get('opponent_deck_id')
            
            is_switch = False
            if deck and prev_deck and deck != prev_deck:
                is_switch = True
            prev_deck = deck
            
            for limit in gate_limits:
                diff = t - limit
                target_zone = None
                
                if -150 <= diff < -75:
                    target_zone = 'pre_stable'
                elif -75 <= diff < 0:
                    target_zone = 'pre_early'
                elif 0 <= diff < 75:
                    target_zone = 'post_early'
                elif 75 <= diff <= 150:
                    target_zone = 'post_stable'
                
                if target_zone:
                    d = gate_data[limit][target_zone]
                    d['mus'].append(mu)
                    d['player_mus'].append((tag, mu))
                    d['battles'] += 1
                    if is_switch: d['switches'] += 1
                    if opp_deck: 
                        d['opp_decks'].append(opp_deck)
                        all_opp_deck_ids.add(opp_deck)
                
                # Attempt Logic (Danger Zone: -75 to 0)
                in_danger_zone = (-75 <= diff < 0)
                state = player_gate_state[limit]
                
                if in_danger_zone:
                    if not state['in_zone']:
                        state['in_zone'] = True
                        state['attempt'] += 1
                    gate_attempts[limit][state['attempt']].append((tag, mu))
                else:
                    state['in_zone'] = False

    # Resolve Cards for Meta Transition
    print(f"Risoluzione carte per {len(all_opp_deck_ids)} mazzi (Gatekeeping)...")
    deck_cards_map = {}
    all_ids_list = list(all_opp_deck_ids)
    CHUNK_SIZE = 900
    for i in range(0, len(all_ids_list), CHUNK_SIZE):
        chunk = all_ids_list[i:i+CHUNK_SIZE]
        placeholders = ','.join(['?'] * len(chunk))
        q = f"SELECT deck_hash, card_name FROM deck_cards WHERE deck_hash IN ({placeholders})"
        cursor.execute(q, chunk)
        for dh, cn in cursor.fetchall():
            if dh not in deck_cards_map: deck_cards_map[dh] = []
            deck_cards_map[dh].append(cn)
            
    conn.close()
    
    # Generate Report
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI ARENA GATEKEEPING (4 FASI: PRE-STABLE, PRE-EARLY, POST-EARLY, POST-STABLE)\n")
        f.write("Obiettivo: Isolare l'effetto 'Meta Shock' post-soglia per verificare il Gatekeeping.\n")
        f.write("Zone:\n")
        f.write("  1. PRE-STABLE  (-150 a -75): Baseline prima del gate.\n")
        f.write("  2. PRE-EARLY   (-75 a 0):    Danger Zone (Gatekeeping?).\n")
        f.write("  3. POST-EARLY  (0 a +75):    Meta Shock / Adattamento.\n")
        f.write("  4. POST-STABLE (+75 a +150): Baseline dopo il gate (Meta assorbito).\n")
        f.write("Metrica Hostility: Global_Avg_MU - Local_Avg_MU (Positivo = Ostile).\n")
        f.write("="*140 + "\n")
        f.write(f"{'SOGLIA':<8} | {'ZONA':<12} | {'N':<5} | {'AVG MU':<8} | {'HOSTILITY':<10} | {'SWITCH %':<8} | {'META TRANS':<10} | {'INTERPRETAZIONE'}\n")
        f.write("-" * 140 + "\n")
        
        for limit in sorted(gate_limits):
            # Check data sufficiency
            if any(len(gate_data[limit][z]['mus']) < 10 for z in zones):
                continue
                
            prev_cards = None
            
            # Helper to calc metrics
            def get_metrics(z):
                d = gate_data[limit][z]
                mus = d['mus']
                if not mus: return 0, 0, 0, set()
                
                avg_mu = statistics.mean(mus)
                
                # Hostility calculated per player instance to normalize
                hostilities = []
                for tag, m in d['player_mus']:
                    if tag in player_global_mu:
                        h = player_global_mu[tag] - m
                        hostilities.append(h)
                avg_hostility = statistics.mean(hostilities) if hostilities else 0
                
                switch_rate = (d['switches'] / d['battles'] * 100) if d['battles'] else 0
                
                card_counts = Counter()
                for did in d['opp_decks']:
                    if did in deck_cards_map:
                        card_counts.update(deck_cards_map[did])
                top_cards = set([c for c, _ in card_counts.most_common(20)])
                
                return avg_mu, avg_hostility, switch_rate, top_cards

            # Calculate for all zones
            metrics = {}
            for z in zones:
                metrics[z] = get_metrics(z)
            
            # Print rows
            for i, z in enumerate(zones):
                mu, host, sw, cards = metrics[z]
                
                # Transition from previous zone
                trans_val = 0.0
                if prev_cards:
                    intersection = len(cards.intersection(prev_cards))
                    union = len(cards.union(prev_cards))
                    jaccard = intersection / union if union > 0 else 0
                    trans_val = 1.0 - jaccard
                
                prev_cards = cards
                
                # Interpretation logic
                interp = ""
                if z == 'pre_early':
                    if host > 1.0: interp = "GATEKEEPING?"
                elif z == 'post_early':
                    if trans_val > 0.4: interp = "META SHOCK"
                elif z == 'post_stable':
                    # Compare with PRE-STABLE
                    pre_s_host = metrics['pre_stable'][1]
                    if host < pre_s_host - 1.0:
                        interp = "RELAX (Post-Gate)"
                    elif host > pre_s_host + 1.0:
                        interp = "HARDER META"
                    else:
                        interp = "STABLE"

                trans_str = f"{trans_val:.2f}" if i > 0 else "-"
                f.write(f"{limit:<8} | {z:<12} | {len(gate_data[limit][z]['mus']):<5} | {mu:<8.2f} | {host:<+10.2f} | {sw:<8.2f} | {trans_str:<10} | {interp}\n")
            
            # Summary Comparison
            pre_s_host = metrics['pre_stable'][1]
            post_s_host = metrics['post_stable'][1]
            delta = pre_s_host - post_s_host # Positive if Pre is more hostile
            
            f.write(f"{'':<8} | {'DELTA (PreS-PostS)':<20} | {delta:<+10.2f} ({'PRE PIÙ OSTILE' if delta > 0.5 else 'SIMILI' if abs(delta)<0.5 else 'POST PIÙ OSTILE'})\n")
            f.write("-" * 140 + "\n")
        
        f.write("="*140 + "\n")
        f.write("\nANALISI HOSTILITY PER TENTATIVO (PRE-EARLY ZONE)\n")
        f.write("Ipotesi: L'ostilità è maggiore nei primi tentativi di superare la soglia e diminuisce successivamente?\n")
        f.write("Tentativo = Ingresso nella fascia [-75, 0) trofei prima della soglia.\n")
        f.write("-" * 140 + "\n")
        f.write(f"{'SOGLIA':<8} | {'ATT 1 (Host)':<15} | {'ATT 2 (Host)':<15} | {'ATT 3 (Host)':<15} | {'ATT 4+ (Host)':<15} | {'TREND'}\n")
        f.write("-" * 140 + "\n")
        
        for limit in sorted(gate_limits):
            attempts_data = gate_attempts[limit]
            if not attempts_data: continue
            
            # Helper to calc hostility for a list of (tag, mu)
            def calc_h(data_list):
                if not data_list: return None
                vals = []
                for t, m in data_list:
                    if t in player_global_mu:
                        vals.append(player_global_mu[t] - m)
                return statistics.mean(vals) if vals else None

            h1 = calc_h(attempts_data[1])
            h2 = calc_h(attempts_data[2])
            h3 = calc_h(attempts_data[3])
            
            # Aggregate 4+
            data_4plus = []
            for k, v in attempts_data.items():
                if k >= 4: data_4plus.extend(v)
            h4 = calc_h(data_4plus)
            
            # Formatting
            def fmt(val): return f"{val:+.2f}" if val is not None else "-"
            def count(val, k): return f"({len(attempts_data[k])})" if val is not None else ""
            def count4(val): return f"({len(data_4plus)})" if val is not None else ""

            s1 = f"{fmt(h1)} {count(h1, 1)}"
            s2 = f"{fmt(h2)} {count(h2, 2)}"
            s3 = f"{fmt(h3)} {count(h3, 3)}"
            s4 = f"{fmt(h4)} {count4(h4)}"
            
            # Trend detection
            trend = ""
            valid_h = [x for x in [h1, h2, h3, h4] if x is not None]
            if len(valid_h) >= 2:
                if valid_h[0] > valid_h[-1] + 1.0: trend = "DECRESCENTE (Easier)"
                elif valid_h[0] < valid_h[-1] - 1.0: trend = "CRESCENTE (Harder)"
                else: trend = "STABILE"
            
            if len(attempts_data[1]) < 10: continue # Skip low data
            
            f.write(f"{limit:<8} | {s1:<15} | {s2:<15} | {s3:<15} | {s4:<15} | {trend}\n")
            
        f.write("="*140 + "\n")