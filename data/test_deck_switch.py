import os
import statistics
import sys
from collections import defaultdict
from scipy.stats import mannwhitneyu, spearmanr

# Add parent directory to path to import api_client
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api_client import fetch_matchup

# --- Helper functions ---

def get_deck_cards_batch(cursor, deck_hashes):
    """Recupera le carte per un set di deck hashes."""
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

def _calculate_avg_level(deck_cards):
    """Calcola il livello medio di un mazzo."""
    if not deck_cards:
        return 0
    levels = [c['level'] for c in deck_cards if c.get('level') is not None]
    return statistics.mean(levels) if levels else 0

def _analyze_deck_winrate_vs_opponent_levels(players_sessions, f):
    """
    Analisi Correlazione Spearman: Winrate globale di un archetipo vs. il Level Diff medio degli avversari affrontati.
    """
    archetype_stats = defaultdict(lambda: {'wins': 0, 'total': 0, 'level_diffs': []})

    for p in players_sessions:
        for s in p['sessions']:
            for b in s['battles']:
                arch = b.get('archetype_id')
                lvl_diff = b.get('level_diff')
                if arch and lvl_diff is not None:
                    archetype_stats[arch]['total'] += 1
                    archetype_stats[arch]['level_diffs'].append(lvl_diff)
                    if b['win'] == 1:
                        archetype_stats[arch]['wins'] += 1
    
    winrates = []
    avg_lvl_diffs = []

    for arch, data in archetype_stats.items():
        if data['total'] >= 50: # Min sample size for an archetype
            winrate = (data['wins'] / data['total']) * 100
            avg_ld = statistics.mean(data['level_diffs'])
            
            winrates.append(winrate)
            avg_lvl_diffs.append(avg_ld)

    f.write("\n" + "="*80 + "\n")
    f.write("ANALISI 4: CORRELAZIONE WINRATE MAZZO vs LIVELLI AVVERSARI\n")
    f.write("Ipotesi: I mazzi con Win Rate più alto (meta) affrontano avversari con livelli più alti (Level Diff più negativo)?\n")
    f.write("-" * 80 + "\n")

    if len(winrates) < 5:
        f.write("Dati insufficienti (meno di 5 archetipi con abbastanza partite).\n")
        return

    corr, p_val = spearmanr(winrates, avg_lvl_diffs)
    f.write(f"Campione: {len(winrates)} archetipi\n")
    f.write(f"Correlazione Spearman: {corr:.4f}\n")
    f.write(f"P-value: {p_val:.4f}\n")
    
    if p_val < 0.05:
        if corr < 0:
            f.write("RISULTATO: SIGNIFICATIVO E NEGATIVO. I mazzi più vincenti affrontano avversari con livelli mediamente più alti.\n")
        else:
            f.write("RISULTATO: SIGNIFICATIVO E POSITIVO. I mazzi più vincenti affrontano avversari con livelli mediamente più bassi.\n")
    else:
        f.write("RISULTATO: NON SIGNIFICATIVO. Nessuna correlazione trovata.\n")


def analyze_deck_switch_patterns(players_sessions, f):
    """Analisi 1: Impatto del cambio deck sui pattern di matchup (No-Lvl)."""
    print("Esecuzione Analisi 1: Pattern Matchup...")
    BAD_THRESH, GOOD_THRESH, LOOKAHEAD = 45.0, 55.0, 4
    transitions = {True: defaultdict(lambda: defaultdict(int)), False: defaultdict(lambda: defaultdict(int))}
    total_switches, total_noswitches = 0, 0
    trajectories_mu = {True: defaultdict(list), False: defaultdict(list)}
    trajectories_lvl = {True: defaultdict(list), False: defaultdict(list)}

    for p in players_sessions:
        all_battles = []
        for s in p['sessions']:
            all_battles.extend(s['battles'])

        for i in range(len(all_battles) - 1):
            b_curr = all_battles[i]
            b_next = all_battles[i+1]
            
            mu_curr_nolvl = b_curr.get('matchup_no_lvl')
            mu_next_nolvl = b_next.get('matchup_no_lvl')
            
            if mu_curr_nolvl is None or mu_next_nolvl is None: continue
            
            id_curr = b_curr.get('archetype_id') or b_curr.get('deck_id')
            id_next = b_next.get('archetype_id') or b_next.get('deck_id')
            
            if not id_curr or not id_next: continue

            is_switch = (id_curr != id_next)
            
            zone_curr = 'Mid'
            if mu_curr_nolvl < BAD_THRESH: zone_curr = 'Bad'
            elif mu_curr_nolvl > GOOD_THRESH: zone_curr = 'Good'
            
            zone_next = 'Mid'
            if mu_next_nolvl < BAD_THRESH: zone_next = 'Bad'
            elif mu_next_nolvl > GOOD_THRESH: zone_next = 'Good'
            
            transitions[is_switch][zone_curr][zone_next] += 1
            if is_switch: total_switches += 1
            else: total_noswitches += 1
            
            if zone_curr == 'Bad':
                target_deck_id = id_next
                for k in range(1, LOOKAHEAD + 1):
                    if i + k >= len(all_battles): break
                    b_future = all_battles[i + k]
                    id_future = b_future.get('archetype_id') or b_future.get('deck_id')
                    if id_future != target_deck_id: break
                    
                    if b_future.get('matchup_no_lvl') is not None:
                        trajectories_mu[is_switch][k].append(b_future['matchup_no_lvl'])
                    if b_future.get('level_diff') is not None:
                        trajectories_lvl[is_switch][k].append(b_future['level_diff'])

    # --- Writing Report Part 1 ---
    f.write("ANALISI 1: IMPATTO CAMBIO DECK SUL PATTERN MATCHUP (NO-LVL)\n")
    f.write("="*80 + "\n")
    f.write(f"Totale Transizioni: {total_switches + total_noswitches} (Switch: {total_switches}, No-Switch: {total_noswitches})\n")
    f.write("-" * 80 + "\n")
    f.write(f"{'PATTERN':<25} | {'NO SWITCH':<15} | {'SWITCH':<15} | {'DELTA':<10}\n")
    f.write("-" * 80 + "\n")
    patterns = [('Bad', 'Bad', 'Persistenza Negativa'), ('Good', 'Good', 'Persistenza Positiva'), ('Bad', 'Good', 'Recupero'), ('Good', 'Bad', 'Punizione')]
    for from_z, to_z, label in patterns:
        total_from_noswitch = sum(transitions[False][from_z].values())
        p_noswitch = (transitions[False][from_z][to_z] / total_from_noswitch * 100) if total_from_noswitch > 0 else 0
        total_from_switch = sum(transitions[True][from_z].values())
        p_switch = (transitions[True][from_z][to_z] / total_from_switch * 100) if total_from_switch > 0 else 0
        f.write(f"{label:<25} | {p_noswitch:<15.2f}% | {p_switch:<15.2f}% | {p_switch - p_noswitch:<+10.2f}%\n")
    
    f.write("\n--- Traiettoria Post-Switch (Partendo da Matchup 'Bad') ---\n")
    f.write(f"{'Step':<10} | {'NO SWITCH (Avg MU)':<20} | {'SWITCH (Avg MU)':<20} | {'NO SWITCH (Avg Lvl)':<20} | {'SWITCH (Avg Lvl)':<20}\n")
    f.write("-" * 95 + "\n")
    for k in range(1, LOOKAHEAD + 1):
        avg_mu_no = statistics.mean(trajectories_mu[False][k]) if trajectories_mu[False][k] else 0
        avg_mu_sw = statistics.mean(trajectories_mu[True][k]) if trajectories_mu[True][k] else 0
        avg_lvl_no = statistics.mean(trajectories_lvl[False][k]) if trajectories_lvl[False][k] else 0
        avg_lvl_sw = statistics.mean(trajectories_lvl[True][k]) if trajectories_lvl[True][k] else 0
        f.write(f"+{k} Match  | {avg_mu_no:<20.2f}% | {avg_mu_sw:<20.2f}% | {avg_lvl_no:<+20.2f} | {avg_lvl_sw:<+20.2f}\n")


def analyze_deck_switch_hypothetical(players_sessions, cursor, f):
    """Analisi 2: Deck Switch Ipotetico vs Reale (Richiede API)."""
    print("Esecuzione Analisi 2: Deck Switch Ipotetico (Richiede tempo)...")
    hypothetical_results = []
    WINDOW_HYPO, MAX_SWITCHES_TO_TEST, switches_tested_hypo = 3, 500, 0

    for p in players_sessions:
        all_battles = []
        for s in p['sessions']:
            all_battles.extend(s['battles'])

        # Pre-fetch all deck cards for the player to reduce DB calls
        player_deck_ids = {b.get('deck_id') for b in all_battles if b.get('deck_id')}
        player_deck_ids.update({b.get('opponent_deck_id') for b in all_battles if b.get('opponent_deck_id')})
        deck_cards_map = get_deck_cards_batch(cursor, player_deck_ids)

        for i in range(len(all_battles) - 1):
            if switches_tested_hypo >= MAX_SWITCHES_TO_TEST: break

            b_curr = all_battles[i]
            b_next = all_battles[i+1]
            
            id_curr = b_curr.get('archetype_id') or b_curr.get('deck_id')
            id_next = b_next.get('archetype_id') or b_next.get('deck_id')
            
            if not id_curr or not id_next: continue
            is_switch = (id_curr != id_next)

            if is_switch:
                if i >= WINDOW_HYPO and i < len(all_battles) - WINDOW_HYPO:
                    prev_window = all_battles[i-WINDOW_HYPO : i]
                    next_window = all_battles[i : i+WINDOW_HYPO]
                    
                    if any(not b.get('opponent_deck_id') for b in prev_window): continue
                    
                    new_deck_cards = deck_cards_map.get(b_next.get('deck_id'))
                    hypothetical_mus = []
                    if new_deck_cards:
                        for b_prev in prev_window:
                            opp_deck_cards = deck_cards_map.get(b_prev['opponent_deck_id'])
                            if opp_deck_cards:
                                mu_data = fetch_matchup(new_deck_cards, opp_deck_cards, force_equal_levels=True)
                                if mu_data and 'winRate' in mu_data:
                                    hypothetical_mus.append(mu_data['winRate'] * 100)
                    
                    if hypothetical_mus:
                        actual_prev_mus = [b['matchup_no_lvl'] for b in prev_window if b.get('matchup_no_lvl') is not None]
                        actual_next_mus = [b['matchup_no_lvl'] for b in next_window if b.get('matchup_no_lvl') is not None]
                        
                        if actual_prev_mus and actual_next_mus:
                            hypothetical_results.append({
                                'avg_prev': statistics.mean(actual_prev_mus),
                                'avg_hypo': statistics.mean(hypothetical_mus),
                                'avg_next': statistics.mean(actual_next_mus)
                            })
                            switches_tested_hypo += 1
                            print(f"Switch ipotetici analizzati: {switches_tested_hypo}/{MAX_SWITCHES_TO_TEST}", end='\r')

    # --- Writing Report Part 2 ---
    f.write("\n\n" + "="*80 + "\n")
    f.write("ANALISI 2: DECK SWITCH IPOTETICO vs REALE\n")
    f.write("="*80 + "\n")
    if hypothetical_results:
        avg_prev_all = statistics.mean([r['avg_prev'] for r in hypothetical_results])
        avg_hypo_all = statistics.mean([r['avg_hypo'] for r in hypothetical_results])
        avg_next_all = statistics.mean([r['avg_next'] for r in hypothetical_results])
        gap = avg_next_all - avg_hypo_all
        f.write(f"Campione: {len(hypothetical_results)} cambi mazzo.\n")
        f.write(f"1. Matchup PRE-SWITCH (Vecchio Deck vs Vecchi Opp): {avg_prev_all:.2f}%\n")
        f.write(f"2. Matchup IPOTETICO  (Nuovo Deck vs Vecchi Opp):   {avg_hypo_all:.2f}%\n")
        f.write(f"3. Matchup REALE      (Nuovo Deck vs Nuovi Opp):    {avg_next_all:.2f}%\n")
        f.write(f"GAP (Reale - Ipotetico): {gap:+.2f}%\n")
        if gap < -2.0: f.write("-> SOSPETTO: Il sistema sembra assegnare avversari più difficili del previsto.\n")
        else: f.write("-> NEUTRO/FAVOREVOLE: Il cambio di avversari è coerente o vantaggioso.\n")
    else:
        f.write("Nessun dato per l'analisi ipotetica.\n")


def analyze_deck_switch_levels(players_sessions, cursor, f):
    """Analisi 3: Adattamento livelli avversari al cambio mazzo."""
    print("Esecuzione Analisi 3: Adattamento Livelli...")
    level_adaptation_data = {
        'level_down': {'pre': [], 'post_by_step': defaultdict(list)},
        'level_up': {'pre': [], 'post_by_step': defaultdict(list)},
        'no_change': {'pre': [], 'post_by_step': defaultdict(list)}
    }
    LOOKAHEAD = 4

    for p in players_sessions:
        all_battles = []
        for s in p['sessions']:
            all_battles.extend(s['battles'])

        player_deck_ids = {b.get('deck_id') for b in all_battles if b.get('deck_id')}
        deck_cards_map = get_deck_cards_batch(cursor, player_deck_ids)

        for i in range(len(all_battles) - 1):
            b_curr = all_battles[i]
            b_next = all_battles[i+1]
            
            id_curr = b_curr.get('archetype_id') or b_curr.get('deck_id')
            id_next = b_next.get('archetype_id') or b_next.get('deck_id')
            
            if not id_curr or not id_next: continue
            is_switch = (id_curr != id_next)

            if is_switch:
                old_deck_cards = deck_cards_map.get(b_curr.get('deck_id'))
                new_deck_cards = deck_cards_map.get(b_next.get('deck_id'))
                
                if old_deck_cards and new_deck_cards:
                    old_avg_lvl = _calculate_avg_level(old_deck_cards)
                    new_avg_lvl = _calculate_avg_level(new_deck_cards)
                    
                    category = 'no_change'
                    if new_avg_lvl < old_avg_lvl - 0.1: category = 'level_down'
                    elif new_avg_lvl > old_avg_lvl + 0.1: category = 'level_up'
                    
                    # 1. Collect PRE-SWITCH (Last 4 matches with OLD deck)
                    pre_diffs = []
                    for k in range(0, LOOKAHEAD): # i, i-1, i-2, i-3
                        idx = i - k
                        if idx < 0: break
                        b_prev = all_battles[idx]
                        id_prev = b_prev.get('archetype_id') or b_prev.get('deck_id')
                        if id_prev != id_curr: break # Stop if deck changed again backwards
                        if b_prev.get('level_diff') is not None:
                            pre_diffs.append(b_prev['level_diff'])

                    # 2. Collect POST-SWITCH (Next 4 matches with NEW deck)
                    current_post_map = {}
                    for k in range(1, LOOKAHEAD + 1):
                        if i + k >= len(all_battles): break
                        b_future = all_battles[i + k]
                        id_future = b_future.get('archetype_id') or b_future.get('deck_id')
                        if id_future != id_next: break
                        if b_future.get('level_diff') is not None:
                            current_post_map[k] = b_future['level_diff']

                    if pre_diffs and current_post_map:
                        level_adaptation_data[category]['pre'].extend(pre_diffs)
                        for k, val in current_post_map.items():
                            level_adaptation_data[category]['post_by_step'][k].append(val)

    # --- Writing Report Part 3 ---
    f.write("\n\n" + "="*80 + "\n")
    f.write("ANALISI 3: ADATTAMENTO LIVELLI AVVERSARI AL CAMBIO MAZZO\n")
    f.write("Ipotesi: Il sistema adatta i livelli avversari a quelli del nuovo mazzo del giocatore?\n")
    f.write("-" * 80 + "\n")
    for category, data in level_adaptation_data.items():
        all_post_values = []
        for k_list in data['post_by_step'].values():
            all_post_values.extend(k_list)
            
        if not all_post_values: continue
        
        avg_pre = statistics.mean(data['pre']) if data['pre'] else 0
        avg_post = statistics.mean(all_post_values)
        
        # Avg excluding first match
        post_no_first_values = []
        for k, v_list in data['post_by_step'].items():
            if k > 1:
                post_no_first_values.extend(v_list)
        
        avg_post_no_first = statistics.mean(post_no_first_values) if post_no_first_values else avg_post
        
        delta = avg_post - avg_pre
        f.write(f"Switch '{category.upper()}':\n")
        f.write(f"  - N. Match Post analizzati: {len(all_post_values)}\n")
        f.write(f"  - Avg Level Diff PRE  (Vecchio Deck): {avg_pre:+.3f}\n")
        f.write(f"  - Avg Level Diff POST (Nuovo Deck):   {avg_post:+.3f}\n")
        f.write(f"  - Avg Level Diff POST (No 1st Match): {avg_post_no_first:+.3f}\n")
        f.write(f"  - DELTA (Adattamento):                {delta:+.3f}\n")
        
        # Trend
        f.write("  - Trend Post-Switch:\n")
        sorted_steps = sorted(data['post_by_step'].keys())
        for k in sorted_steps:
            vals = data['post_by_step'][k]
            if vals:
                step_avg = statistics.mean(vals)
                f.write(f"    +{k}: {step_avg:+.3f} (n={len(vals)})\n")
        f.write("\n")
        
    f.write("\nINTERPRETAZIONE:\n")
    f.write("Se dopo uno switch 'level_down' (il giocatore usa un mazzo più debole), l'Avg Level Diff è positivo,\n")
    f.write("significa che il sistema assegna avversari con livelli più bassi (adattamento).\n")
    f.write("Se è negativo, il sistema continua ad assegnare avversari forti (nessun adattamento o punizione).\n")


def analyze_deck_switch_combined(players_sessions, cursor, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'deck_switch_analysis_results.txt')

    print(f"\nGenerazione report analisi combinata Deck Switch in: {output_file}")

    with open(output_file, "w", encoding="utf-8") as f:
        analyze_deck_switch_patterns(players_sessions, f)
        
        
        #analyze_deck_switch_hypothetical(players_sessions, cursor, f)
        
        analyze_deck_switch_levels(players_sessions, cursor, f)
        
        _analyze_deck_winrate_vs_opponent_levels(players_sessions, f)
        f.write("\n" + "="*80 + "\n")