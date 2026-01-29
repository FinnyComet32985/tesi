import os
import statistics
import sqlite3
import sys
from datetime import datetime
from scipy.stats import chi2_contingency, kruskal, levene
import pytz

# Add parent directory to path to import api_client
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api_client import fetch_matchup

DB_PATH = os.path.join(os.path.dirname(__file__), '../db/clash.db')

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

def get_deck_archetypes_batch(cursor, deck_hashes):
    """Recupera l'archetype_hash per un set di deck hashes."""
    if not deck_hashes: return {}
    placeholders = ','.join(['?'] * len(deck_hashes))
    query = f"SELECT deck_hash, archetype_hash FROM decks WHERE deck_hash IN ({placeholders})"
    cursor.execute(query, list(deck_hashes))
    return {row[0]: row[1] for row in cursor.fetchall()}

COUNTRY_TZ_MAP = {
    'Italy': 'Europe/Rome', 'IT': 'Europe/Rome',
    'United States': 'America/New_York', 'US': 'America/New_York',
    'Germany': 'Europe/Berlin', 'DE': 'Europe/Berlin',
    'France': 'Europe/Paris', 'FR': 'Europe/Paris',
    'Spain': 'Europe/Madrid', 'ES': 'Europe/Madrid',
    'United Kingdom': 'Europe/London', 'GB': 'Europe/London', 'UK': 'Europe/London',
    'Russia': 'Europe/Moscow', 'RU': 'Europe/Moscow',
    'Japan': 'Asia/Tokyo', 'JP': 'Asia/Tokyo',
    'China': 'Asia/Shanghai', 'CN': 'Asia/Shanghai',
    'Brazil': 'America/Sao_Paulo', 'BR': 'America/Sao_Paulo',
    'Canada': 'America/Toronto', 'CA': 'America/Toronto',
    'Mexico': 'America/Mexico_City', 'MX': 'America/Mexico_City',
    'Korea, Republic of': 'Asia/Seoul', 'KR': 'Asia/Seoul',
    'Netherlands': 'Europe/Amsterdam', 'NL': 'Europe/Amsterdam'
}

def get_local_hour(timestamp_str, nationality):
    try:
        # Timestamp string is in Italian local time (from battlelog_v2)
        italy_tz = pytz.timezone('Europe/Rome')
        naive_dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        italy_dt = italy_tz.localize(naive_dt)
        
        target_tz_name = COUNTRY_TZ_MAP.get(nationality, 'Europe/Rome')
        target_tz = pytz.timezone(target_tz_name)
        player_dt = italy_dt.astimezone(target_tz)
        return player_dt.hour
    except Exception:
        return datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S').hour

def analyze_deck_switch_hypothetical(players_sessions, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'deck_switch_hypothetical_results.txt')

    print(f"\nGenerazione report Deck Switch Hypothetical in: {output_file}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Configurazione
    WINDOW = 3
    MAX_SWITCHES_TO_TEST = 1000 # Limite per evitare troppe chiamate API
    switches_tested = 0

    results = []

    try:
        for p in players_sessions:
            if switches_tested >= MAX_SWITCHES_TO_TEST: break

            # Appiattiamo le sessioni
            battles = []
            for s in p['sessions']:
                battles.extend([b for b in s['battles'] if b['game_mode'] in ['Ladder', 'Ranked']])
            
            for i in range(WINDOW, len(battles) - WINDOW):
                if switches_tested >= MAX_SWITCHES_TO_TEST: break

                prev_window = battles[i-WINDOW : i]
                next_window = battles[i : i+WINDOW]
                
                curr_deck = battles[i]['deck_id']
                prev_deck = battles[i-1]['deck_id']
                
                # Rileva cambio mazzo
                if not curr_deck or not prev_deck or curr_deck == prev_deck:
                    continue
                
                # Verifica dati necessari
                if any(not b['opponent_deck_id'] for b in prev_window): continue
                
                # Recupera carte dal DB
                needed_decks = {curr_deck}
                for b in prev_window: needed_decks.add(b['opponent_deck_id'])
                
                deck_cards_map = get_deck_cards_batch(cursor, needed_decks)
                
                if curr_deck not in deck_cards_map: continue
                
                # Calcola Matchup Ipotetico: Nuovo Mazzo vs Vecchi Avversari
                hypothetical_mus = []
                new_deck_cards = deck_cards_map[curr_deck]
                
                for b in prev_window:
                    opp_deck_id = b['opponent_deck_id']
                    if opp_deck_id in deck_cards_map:
                        opp_cards = deck_cards_map[opp_deck_id]
                        # Chiamata API (o cache interna se esistesse)
                        # Nota: fetch_matchup fa una richiesta HTTP.
                        mu_data = fetch_matchup(new_deck_cards, opp_cards, force_equal_levels=True)
                        if mu_data and 'winRate' in mu_data:
                            hypothetical_mus.append(mu_data['winRate'] * 100)
                
                if not hypothetical_mus: continue
                
                # Dati Reali
                actual_prev_mus = [b['matchup_no_lvl'] for b in prev_window if b.get('matchup_no_lvl') is not None]
                actual_next_mus = [b['matchup_no_lvl'] for b in next_window if b.get('matchup_no_lvl') is not None]
                
                if not actual_prev_mus or not actual_next_mus: continue
                
                avg_hypo = statistics.mean(hypothetical_mus)
                avg_prev = statistics.mean(actual_prev_mus)
                avg_next = statistics.mean(actual_next_mus)
                
                results.append({
                    'tag': p['tag'],
                    'avg_prev': avg_prev,
                    'avg_hypo': avg_hypo,
                    'avg_next': avg_next
                })
                
                switches_tested += 1
                print(f"Switch analizzati: {switches_tested} /{MAX_SWITCHES_TO_TEST}", end='\r')

    finally:
        conn.close()

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI DECK SWITCH: IPOTETICO vs REALE\n")
        f.write("Obiettivo: Verificare se il sistema cambia gli avversari quando cambi mazzo.\n")
        f.write("Metodo: Calcoliamo come il TUO NUOVO mazzo avrebbe performato contro i TUOI VECCHI avversari (Ipotetico).\n")
        f.write("        Confrontiamo questo valore con i matchup che hai effettivamente trovato dopo il cambio (Reale).\n")
        f.write("="*80 + "\n\n")
        
        if not results:
            f.write("Nessun dato analizzato (o limite API raggiunto/nessun cambio deck trovato).\n")
            return
            
        avg_prev_all = statistics.mean([r['avg_prev'] for r in results])
        avg_hypo_all = statistics.mean([r['avg_hypo'] for r in results])
        avg_next_all = statistics.mean([r['avg_next'] for r in results])
        
        f.write(f"Campione: {len(results)} cambi mazzo analizzati.\n")
        f.write("-" * 80 + "\n")
        f.write(f"1. Matchup PRE-SWITCH (Vecchio Deck vs Vecchi Opp): {avg_prev_all:.2f}%\n")
        f.write(f"2. Matchup IPOTETICO  (Nuovo Deck vs Vecchi Opp):   {avg_hypo_all:.2f}%\n")
        f.write(f"3. Matchup REALE      (Nuovo Deck vs Nuovi Opp):    {avg_next_all:.2f}%\n")
        f.write("-" * 80 + "\n")
        
        delta_hypo = avg_hypo_all - avg_prev_all
        delta_real = avg_next_all - avg_prev_all
        gap = avg_next_all - avg_hypo_all
        
        f.write(f"Miglioramento Teorico (Se gli avversari restassero uguali): {delta_hypo:+.2f}%\n")
        f.write(f"Miglioramento Reale   (Con i nuovi avversari):              {delta_real:+.2f}%\n")
        f.write(f"GAP (Manipolazione?):                                       {gap:+.2f}%\n")
        
        f.write("\nINTERPRETAZIONE:\n")
        if gap < -5.0:
            f.write("RISULTATO: SOSPETTO. Il nuovo mazzo avrebbe dovuto performare molto meglio contro i vecchi avversari,\n")
            f.write("           ma il sistema ti ha assegnato nuovi avversari che lo counterano (Gap Negativo ampio).\n")
        elif gap > 5.0:
            f.write("RISULTATO: FAVOREVOLE. Il sistema ti ha assegnato avversari ancora più facili del previsto.\n")
        else:
            f.write("RISULTATO: NEUTRO. Il cambio di avversari è coerente con il cambio di mazzo (o casuale).\n")
        f.write("="*80 + "\n")
        
        # New section: Subset where Hypo > Prev (Improvement Expected)
        subset = [r for r in results if r['avg_hypo'] > r['avg_prev']]
        
        f.write("\n" + "="*80 + "\n")
        f.write("FOCUS: SWITCH 'INTELLIGENTI' (Dove il nuovo mazzo è teoricamente migliore)\n")
        f.write("Obiettivo: Se cambio per un mazzo migliore (Hypo > Prev), il sistema mi premia o mi punisce?\n")
        f.write("-" * 80 + "\n")
        
        if subset:
            avg_prev_sub = statistics.mean([r['avg_prev'] for r in subset])
            avg_hypo_sub = statistics.mean([r['avg_hypo'] for r in subset])
            avg_next_sub = statistics.mean([r['avg_next'] for r in subset])
            
            f.write(f"Campione Subset: {len(subset)} cambi.\n")
            f.write(f"1. Matchup PRE-SWITCH: {avg_prev_sub:.2f}%\n")
            f.write(f"2. Matchup IPOTETICO:  {avg_hypo_sub:.2f}%\n")
            f.write(f"3. Matchup REALE:      {avg_next_sub:.2f}%\n")
            
            gap_sub = avg_next_sub - avg_hypo_sub
            f.write(f"GAP (Reale - Ipotetico): {gap_sub:+.2f}%\n")
        else:
            f.write("Nessun caso trovato.\n")
        f.write("="*80 + "\n")


def analyze_nolvl_markov(players_sessions, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'matchup_nolvl_markov_results.txt')

    print(f"\nGenerazione report Markov No-Lvl in: {output_file}")

    states = ['Unfavorable', 'Even', 'Favorable']
    transitions = [[0]*3 for _ in range(3)]
    total_transitions = 0

    for p in players_sessions:
        for session in p['sessions']:
            battles = session['battles']
            if len(battles) < 2: continue
            
            session_states = []
            for b in battles:
                m = b.get('matchup_no_lvl')
                if m is None:
                    session_states.append(None)
                    continue
                
                if m > 55.0: s = 2
                elif m < 45.0: s = 0
                else: s = 1
                session_states.append(s)
            
            for i in range(len(session_states) - 1):
                curr_s = session_states[i]
                next_s = session_states[i+1]
                if curr_s is not None and next_s is not None:
                    transitions[curr_s][next_s] += 1
                    total_transitions += 1

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI CATENE DI MARKOV: MATCHUP NO-LVL\n")
        f.write("Obiettivo: Verificare la memoria del sistema sui matchup 'puri' (senza livelli).\n")
        f.write("="*80 + "\n")
        
        row_totals = [sum(transitions[i]) for i in range(3)]
        col_totals = [sum(transitions[i][j] for i in range(3)) for j in range(3)]
        grand_total = sum(row_totals)
        
        if grand_total == 0:
            f.write("Dati insufficienti.\n")
            return

        global_probs = [c / grand_total for c in col_totals]

        f.write(f"{'STATO PRECEDENTE':<20} | {'SUCCESSIVO: Unfavorable':<25} | {'SUCCESSIVO: Even':<20} | {'SUCCESSIVO: Favorable':<20}\n")
        f.write("-" * 95 + "\n")

        for i, from_state in enumerate(states):
            row_str = f"{from_state:<20} | "
            for j, to_state in enumerate(states):
                count = transitions[i][j]
                total_from = row_totals[i] if row_totals[i] > 0 else 1
                obs_prob = count / total_from
                exp_prob = global_probs[j]
                
                diff = obs_prob - exp_prob
                marker = "(!)" if abs(diff) > 0.05 else ""
                
                cell_str = f"{obs_prob*100:.1f}% (Exp {exp_prob*100:.1f}%) {marker}"
                row_str += f"{cell_str:<25} | "
            f.write(row_str + "\n")

        f.write("-" * 95 + "\n")
        chi2, p, dof, ex = chi2_contingency(transitions)
        f.write(f"Test Chi-Quadro: p-value = {p:.6f}\n")
        f.write("="*80 + "\n")

def analyze_card_meta_vs_counter(players_sessions, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'card_meta_vs_counter_results.txt')

    print(f"\nGenerazione report Card Meta vs Counter in: {output_file}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Raccogli tutti i deck ID avversari e i trofei associati
    # Struttura: arena_bucket -> { 'total_battles': 0, 'counter_battles': 0, 'cards_total': {card: count}, 'cards_counter': {card: count} }
    BUCKET_SIZE = 1000
    arena_stats = {}
    
    # Cache per deck cards per evitare query ripetute
    deck_cache = {}
    
    # Set di tutti i deck ID da fetchare
    all_deck_ids = set()
    
    # Prima passata: raccogli ID
    temp_battles = [] # (bucket, deck_id, is_counter)
    
    for p in players_sessions:
        for s in p['sessions']:
            for b in s['battles']:
                if b['game_mode'] == 'Ladder' and b.get('trophies_before') and b.get('opponent_deck_id'):
                    t = b['trophies_before']
                    bucket = (t // BUCKET_SIZE) * BUCKET_SIZE
                    
                    mu = b.get('matchup_no_lvl')
                    is_counter = mu is not None and mu < 40.0
                    
                    all_deck_ids.add(b['opponent_deck_id'])
                    temp_battles.append((bucket, b['opponent_deck_id'], is_counter))

    # Fetch carte in batch
    print(f"Recupero carte per {len(all_deck_ids)} mazzi unici...")
    # SQLite limit variable number, do in chunks
    all_deck_ids_list = list(all_deck_ids)
    CHUNK_SIZE = 900
    for i in range(0, len(all_deck_ids_list), CHUNK_SIZE):
        chunk = all_deck_ids_list[i:i+CHUNK_SIZE]
        batch_decks = get_deck_cards_batch(cursor, chunk)
        deck_cache.update(batch_decks)
    
    conn.close()

    # Processamento dati
    for bucket, deck_id, is_counter in temp_battles:
        if bucket not in arena_stats:
            arena_stats[bucket] = {'total': 0, 'counter': 0, 'cards_total': {}, 'cards_counter': {}}
        
        stats = arena_stats[bucket]
        stats['total'] += 1
        if is_counter: stats['counter'] += 1
        
        if deck_id in deck_cache:
            cards = deck_cache[deck_id]
            for card in cards:
                c_name = card['name']
                stats['cards_total'][c_name] = stats['cards_total'].get(c_name, 0) + 1
                if is_counter:
                    stats['cards_counter'][c_name] = stats['cards_counter'].get(c_name, 0) + 1

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI FREQUENZA CARTE: META vs COUNTER\n")
        f.write("Obiettivo: Identificare carte che appaiono sproporzionatamente spesso quando il giocatore è counterato.\n")
        f.write("Definizione Counter: Matchup No-Lvl < 40%.\n")
        f.write("Lift = Frequenza in Counter / Frequenza Globale.\n")
        f.write("="*80 + "\n")

        for bucket in sorted(arena_stats.keys()):
            s = arena_stats[bucket]
            if s['total'] < 50: continue
            
            f.write(f"\n--- FASCIA TROFEI {bucket}-{bucket+BUCKET_SIZE} (Battles: {s['total']}, Countered: {s['counter']}) ---\n")
            f.write(f"{'CARTA':<20} | {'GLOBAL %':<10} | {'COUNTER %':<10} | {'LIFT':<10} | {'STATUS'}\n")
            f.write("-" * 80 + "\n")
            
            card_metrics = []
            for card, count_tot in s['cards_total'].items():
                if count_tot < 10: continue # Ignora carte rare
                
                freq_global = count_tot / s['total']
                
                count_cnt = s['cards_counter'].get(card, 0)
                freq_counter = count_cnt / s['counter'] if s['counter'] > 0 else 0
                
                lift = freq_counter / freq_global if freq_global > 0 else 0
                card_metrics.append((card, freq_global, freq_counter, lift))
            
            # Ordina per Lift decrescente
            card_metrics.sort(key=lambda x: x[3], reverse=True)
            
            for card, fg, fc, lift in card_metrics[:15]: # Top 15 sospette
                status = ""
                if lift > 1.5 and fg > 0.10: status = "META KILLER (Popolare & Counter)"
                elif lift > 2.0: status = "SNIPER (Rara ma letale)"
                elif lift < 0.7: status = "SAFE (Appare meno nei counter)"
                
                f.write(f"{card:<20} | {fg*100:<9.1f}% | {fc*100:<9.1f}% | {lift:<10.2f} | {status}\n")
        
        f.write("="*80 + "\n")

def analyze_matchmaking_fairness(players_sessions, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'matchmaking_fairness_results.txt')

    print(f"\nGenerazione report Matchmaking Fairness (Deck vs Opponent Distribution) in: {output_file}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Configuration
    TIME_SLOT_HOURS = 8         # Allargato da 4
    TROPHY_BUCKET_SIZE = 1000   # Allargato da 500
    MIN_BATTLES_PER_BUCKET = 20 # Abbassato da 30
    MIN_BATTLES_PER_DECK = 3    # Abbassato da 5

    # Data Structure: buckets[(time_slot, trophy_bucket, region)] = list of (player_deck, opp_deck)
    buckets = {}
    
    # Set per raccogliere tutti i deck ID da risolvere
    all_deck_ids = set()
    temp_battles = [] # (time_slot, trophy_bucket, region, p_deck_id, o_deck_id)

    for p in players_sessions:
        nationality = p.get('nationality')
        for s in p['sessions']:
            for b in s['battles']:
                if b['game_mode'] != 'Ladder': continue
                
                t = b.get('trophies_before')
                if not t: continue
                
                ts_str = b['timestamp']
                hour = get_local_hour(ts_str, nationality)
                
                # Identifiers (Archetype preferred)
                p_deck = b.get('deck_id')
                o_deck = b.get('opponent_deck_id')
                
                if not p_deck or not o_deck: continue
                
                all_deck_ids.add(p_deck)
                all_deck_ids.add(o_deck)
                
                # Bucket Keys
                time_slot = hour // TIME_SLOT_HOURS
                trophy_bucket = (t // TROPHY_BUCKET_SIZE) * TROPHY_BUCKET_SIZE
                
                temp_battles.append((time_slot, trophy_bucket, nationality, p_deck, o_deck))

    # Risoluzione Archetipi in Batch
    print(f"Risoluzione archetipi per {len(all_deck_ids)} mazzi...")
    deck_to_archetype = {}
    all_deck_ids_list = list(all_deck_ids)
    CHUNK_SIZE = 900
    for i in range(0, len(all_deck_ids_list), CHUNK_SIZE):
        chunk = all_deck_ids_list[i:i+CHUNK_SIZE]
        batch_map = get_deck_archetypes_batch(cursor, chunk)
        deck_to_archetype.update(batch_map)
    
    conn.close()

    # Popolamento Buckets con Archetipi
    for time_slot, trophy_bucket, region, p_id, o_id in temp_battles:
        p_arch = deck_to_archetype.get(p_id, p_id) # Fallback su ID se manca archetipo
        o_arch = deck_to_archetype.get(o_id, o_id)
        
        key = (time_slot, trophy_bucket, region)
        if key not in buckets: buckets[key] = []
        buckets[key].append((p_arch, o_arch))

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI FAIRNESS MATCHMAKING (DIPENDENZA DECK AVVERSARIO DAL PROPRIO DECK)\n")
        f.write("Obiettivo: Verificare se, a parità di condizioni (Orario, Trofei e Regione), il mazzo che usi influenza gli avversari che trovi.\n")
        f.write("Metodo: Test Chi-Quadro su tabella di contingenza (PlayerDeck vs OpponentDeck) per ogni bucket.\n")
        f.write("Ipotesi Nulla (Fair): La distribuzione degli avversari è indipendente dal tuo mazzo.\n")
        f.write("="*100 + "\n\n")
        
        f.write(f"Totale Battaglie Analizzate: {len(temp_battles)}\n")
        significant_buckets = 0
        total_tested_buckets = 0
        skipped_buckets = 0
        
        sorted_keys = sorted(buckets.keys(), key=lambda x: (x[1], x[0], x[2] or "")) # Sort by Trophies then Time then Region
        
        for key in sorted_keys:
            battles = buckets[key]
            if len(battles) < MIN_BATTLES_PER_BUCKET: 
                skipped_buckets += 1
                continue
            
            time_slot, trophy_bucket, region = key
            time_label = f"{time_slot*TIME_SLOT_HOURS:02d}:00-{(time_slot+1)*TIME_SLOT_HOURS:02d}:00"
            range_label = f"{trophy_bucket}-{trophy_bucket+TROPHY_BUCKET_SIZE}"
            region_label = region if region else "Unknown"
            
            # Count frequencies
            p_counts = {}
            for p_d, o_d in battles:
                p_counts[p_d] = p_counts.get(p_d, 0) + 1
            
            # Filter top player decks
            top_p_decks = [d for d, c in p_counts.items() if c >= MIN_BATTLES_PER_DECK]
            if len(top_p_decks) < 2: continue # Need at least 2 decks to compare
            
            # Build Contingency Table
            relevant_battles = [b for b in battles if b[0] in top_p_decks]
            
            o_counts = {}
            for p_d, o_d in relevant_battles:
                o_counts[o_d] = o_counts.get(o_d, 0) + 1
            
            top_o_decks = [d for d, c in o_counts.items() if c >= 3]
            if len(top_o_decks) < 2: continue
            
            matrix = []
            valid_p_decks = []
            
            for p_d in top_p_decks:
                row = []
                opps_for_p = [b[1] for b in relevant_battles if b[0] == p_d]
                for o_d in top_o_decks:
                    count = opps_for_p.count(o_d)
                    row.append(count)
                
                if sum(row) > 0:
                    matrix.append(row)
                    valid_p_decks.append(p_d)
            
            if len(matrix) < 2: continue
            
            try:
                chi2, p, dof, ex = chi2_contingency(matrix)
                total_tested_buckets += 1
                
                is_sig = p < 0.05
                if is_sig: significant_buckets += 1
                
                sig_str = "SIGNIFICATIVO (Rigged?)" if is_sig else "Non significativo"
                
                f.write(f"Bucket: {range_label} | Orario: {time_label} | Regione: {region_label} | Battles: {len(relevant_battles)}\n")
                f.write(f"Confronto tra {len(valid_p_decks)} Archetipi Player vs {len(top_o_decks)} Archetipi Opponent\n")
                f.write(f"P-value: {p:.6f} -> {sig_str}\n")
                f.write("-" * 60 + "\n")
                
            except Exception as e:
                f.write(f"Bucket: {range_label} | Error: {e}\n")

        f.write("\n" + "="*100 + "\n")
        f.write(f"Totale Bucket Testati: {total_tested_buckets}\n")
        f.write(f"Bucket Saltati (Dati insufficienti): {skipped_buckets}\n")
        f.write(f"Bucket con Dipendenza Significativa: {significant_buckets}\n")
        if total_tested_buckets > 0:
            f.write(f"Percentuale Sospetta: {(significant_buckets/total_tested_buckets)*100:.2f}%\n")
        f.write("="*100 + "\n")

def analyze_level_saturation(players_sessions, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'level_saturation_results.txt')

    print(f"\nGenerazione report Level Saturation in: {output_file}")
    
    BUCKET_SIZE = 500
    buckets = {} # bucket -> list of level_diffs

    for p in players_sessions:
        for s in p['sessions']:
            for b in s['battles']:
                if b['game_mode'] != 'Ladder': continue
                t = b.get('trophies_before')
                l = b.get('level_diff')
                if t and l is not None:
                    b_idx = (t // BUCKET_SIZE) * BUCKET_SIZE
                    if b_idx not in buckets: buckets[b_idx] = []
                    buckets[b_idx].append(l)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI SATURAZIONE LIVELLI PER TROFEI\n")
        f.write("Obiettivo: Verificare se a trofei alti la varianza dei livelli diminuisce (tutti maxati).\n")
        f.write("="*80 + "\n")
        f.write(f"{'RANGE':<15} | {'N':<8} | {'MEAN DIFF':<10} | {'VARIANCE':<10} | {'% ZERO DIFF':<15}\n")
        f.write("-" * 80 + "\n")
        
        for k in sorted(buckets.keys()):
            vals = buckets[k]
            if len(vals) < 20: continue
            
            mean = statistics.mean(vals)
            var = statistics.variance(vals)
            zeros = len([v for v in vals if v == 0])
            zero_perc = (zeros / len(vals)) * 100
            
            f.write(f"{k}-{k+BUCKET_SIZE:<15} | {len(vals):<8} | {mean:<10.3f} | {var:<10.3f} | {zero_perc:<15.1f}%\n")
            
        f.write("="*80 + "\n")