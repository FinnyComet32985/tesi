import os
import sqlite3
import statistics
from datetime import datetime
from collections import defaultdict
import pytz

# Import helper from sibling module
try:
    from test_deck_analysis import get_deck_cards_batch
except ImportError:
    # Fallback if running standalone or path issues
    def get_deck_cards_batch(cursor, deck_hashes):
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

DB_PATH = os.path.join(os.path.dirname(__file__), '../db/clash.db')

SNIPER_DEFS = {
    'Graveyard': {
        'hard': {'Poison', 'Mother Witch'},
        'soft': {'Archers', 'Dart Goblin', 'Valkyrie', 'Dark Prince', 'Bomb Tower', 'Executioner', 'Wizard', 'Electro Wizard', 'Baby Dragon', 'Minions', 'Bats', 'Skeleton King', 'Golden Knight'}
    },
    'Electro Giant': {
        'hard': {'P.E.K.K.A', 'Mini P.E.K.K.A', 'Inferno Tower', 'Inferno Dragon', 'Elite Barbarians'},
        'soft': {'Cannon', 'Tesla', 'Barbarians', 'Hunter', 'Fisherman', 'Zappies', 'Ice Wizard', 'Tornado', 'Mortar', 'X-Bow'}
    },
    'Sparky': {
        'hard': {'Rocket', 'Lightning', 'Electro Wizard', 'Electro Dragon', 'Zappies'},
        'soft': {'Zap', 'Guards', 'Dark Prince', 'Skeleton Army', 'Barbarians', 'Mini P.E.K.K.A', 'Freeze'}
    },
    'Balloon': {
        'hard': {'Rocket', 'Inferno Tower', 'Mega Minion', 'Minion Horde', 'Hunter', 'Ram Rider'},
        'soft': {'Musketeer', 'Electro Wizard', 'Wizard', 'Bats', 'Minions', 'Tesla', 'Cannon', 'Tornado', 'Snowball', 'Fireball', 'Inferno Dragon'}
    },
    'Lava Hound': {
        'hard': {'Inferno Tower', 'Inferno Dragon', 'Executioner'},
        'soft': {'Musketeer', 'Wizard', 'Minion Horde', 'Tesla', 'Arrows', 'Zap', 'Poison', 'Hunter', 'Flying Machine'}
    },
    'Golem': {
        'hard': {'Inferno Tower', 'Inferno Dragon', 'P.E.K.K.A', 'Mini P.E.K.K.A', 'Elite Barbarians'},
        'soft': {'Barbarians', 'Hunter', 'Lumberjack', 'Night Witch', 'Cannon', 'Tesla', 'Bomb Tower'}
    }
}

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

def analyze_all_snipers_targeting(players_sessions, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'snipers_targeting_analysis.txt')

    print(f"\nGenerazione report Multi-Sniper Targeting in: {output_file}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Configurazione
    MIN_TROPHIES = 6000
    MAX_TROPHIES = 12000

    # Raccolta Deck IDs
    relevant_battles = []
    deck_ids_to_fetch = set()

    for p in players_sessions:
        for s in p['sessions']:
            for b in s['battles']:
                if b['game_mode'] == 'Ladder' and b.get('trophies_before'):
                    t = b['trophies_before']
                    if MIN_TROPHIES <= t < MAX_TROPHIES:
                        if b.get('deck_id') and b.get('opponent_deck_id'):
                            relevant_battles.append(b)
                            deck_ids_to_fetch.add(b['deck_id'])
                            deck_ids_to_fetch.add(b['opponent_deck_id'])

    if not relevant_battles:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"Nessuna battaglia trovata nella fascia {MIN_TROPHIES}-{MAX_TROPHIES} trofei.\n")
        conn.close()
        return

    # Fetch Carte
    print(f"Recupero carte per {len(deck_ids_to_fetch)} mazzi...")
    deck_cache = {}
    all_ids_list = list(deck_ids_to_fetch)
    CHUNK_SIZE = 900
    for i in range(0, len(all_ids_list), CHUNK_SIZE):
        chunk = all_ids_list[i:i+CHUNK_SIZE]
        batch = get_deck_cards_batch(cursor, chunk)
        deck_cache.update(batch)
    
    conn.close()

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"TEST INCROCIATO: TARGETING MULTI-SNIPER (Fascia {MIN_TROPHIES}-{MAX_TROPHIES})\n")
        f.write("Obiettivo: Verificare se i deck vulnerabili a specifiche carte 'Sniper' le incontrano più spesso.\n")
        f.write("Definizione Vulnerabile: 0 Hard Counters E < 2 Soft Counters nel mazzo.\n")
        f.write("="*80 + "\n")

        for sniper_card, counters in SNIPER_DEFS.items():
            hard_counters = counters['hard']
            soft_counters = counters['soft']
            
            vuln_battles = 0
            vuln_vs_sniper = 0
            
            safe_battles = 0
            safe_vs_sniper = 0

            for b in relevant_battles:
                p_deck = deck_cache.get(b['deck_id'])
                o_deck = deck_cache.get(b['opponent_deck_id'])
                
                if not p_deck or not o_deck: continue
                
                # Check Player Vulnerability
                p_cards = {c['name'] for c in p_deck}
                hard_cnt = len(p_cards.intersection(hard_counters))
                soft_cnt = len(p_cards.intersection(soft_counters))
                
                is_vulnerable = (hard_cnt == 0 and soft_cnt < 2)
                
                # Check Opponent Sniper
                o_cards = {c['name'] for c in o_deck}
                has_sniper = sniper_card in o_cards
                
                if is_vulnerable:
                    vuln_battles += 1
                    if has_sniper: vuln_vs_sniper += 1
                else:
                    safe_battles += 1
                    if has_sniper: safe_vs_sniper += 1
            
            # Scrittura Report per questa carta
            f.write(f"\n>>> ANALISI CARTA: {sniper_card.upper()}\n")
            f.write(f"    Hard Counters: {', '.join(list(hard_counters)[:4])}...\n")
            
            vuln_rate = (vuln_vs_sniper / vuln_battles * 100) if vuln_battles > 0 else 0
            safe_rate = (safe_vs_sniper / safe_battles * 100) if safe_battles > 0 else 0
            
            f.write(f"    {'GRUPPO':<20} | {'N. MATCH':<10} | {'VS SNIPER':<10} | {'RATE %':<10}\n")
            f.write(f"    {'-'*60}\n")
            f.write(f"    {'VULNERABILI':<20} | {vuln_battles:<10} | {vuln_vs_sniper:<10} | {vuln_rate:<10.2f}%\n")
            f.write(f"    {'NON-VULNERABILI':<20} | {safe_battles:<10} | {safe_vs_sniper:<10} | {safe_rate:<10.2f}%\n")
            
            if safe_rate > 0:
                ratio = vuln_rate / safe_rate
                f.write(f"    RATIO (Vuln/Safe): {ratio:.2f}x\n")
            else:
                f.write("    RATIO: N/A (Safe rate is 0)\n")
            
            if vuln_rate > safe_rate * 1.5:
                f.write("    -> EVIDENZA DI TARGETING (!)\n")
            elif safe_rate > vuln_rate:
                f.write("    -> NESSUN TARGETING (Paradosso)\n")
            else:
                f.write("    -> NEUTRO\n")
            
            f.write("-" * 80 + "\n")

        f.write("\n" + "="*80 + "\n")

def analyze_sniper_confounding(players_sessions, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'sniper_confounding_check.txt')

    print(f"\nGenerazione report Sniper Confounding in: {output_file}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    MIN_TROPHIES = 7000
    MAX_TROPHIES = 8000
    
    # 1. Identificazione Sniper (Lift Analysis on the fly)
    battles_data = [] # (trophies, opponent_deck_id, is_counter, timestamp, opponent_tag)
    deck_ids = set()
    
    for p in players_sessions:
        nationality = p.get('nationality')
        for s in p['sessions']:
            for b in s['battles']:
                if b['game_mode'] == 'Ladder' and b.get('trophies_before'):
                    t = b['trophies_before']
                    if MIN_TROPHIES <= t < MAX_TROPHIES:
                        if b.get('opponent_deck_id'):
                            mu = b.get('matchup_no_lvl')
                            is_counter = mu is not None and mu < 40.0
                            battles_data.append({
                                't': t,
                                'deck_id': b['opponent_deck_id'],
                                'is_counter': is_counter,
                                'ts': b['timestamp'],
                                'opp_tag': b['opponent'],
                                'nationality': nationality
                            })
                            deck_ids.add(b['opponent_deck_id'])

    if not battles_data:
        conn.close()
        return

    # Fetch cards
    deck_cache = {}
    all_ids = list(deck_ids)
    CHUNK_SIZE = 900
    for i in range(0, len(all_ids), CHUNK_SIZE):
        chunk = all_ids[i:i+CHUNK_SIZE]
        batch = get_deck_cards_batch(cursor, chunk)
        deck_cache.update(batch)
    conn.close()

    # Count Card Frequencies
    total_battles = len(battles_data)
    total_counters = sum(1 for b in battles_data if b['is_counter'])
    
    card_counts_global = defaultdict(int)
    card_counts_counter = defaultdict(int)
    
    # Per confounding analysis
    card_details = defaultdict(lambda: {'hours': defaultdict(int), 'buckets': defaultdict(int), 'opponents': set()})
    
    for b in battles_data:
        d_id = b['deck_id']
        if d_id not in deck_cache: continue
        
        cards = [c['name'] for c in deck_cache[d_id]]
        
        # Parse timestamp
        hour = get_local_hour(b['ts'], b['nationality'])
        bucket = (b['t'] // 250) * 250 # 7000, 7250, 7500, 7750
        
        for card in cards:
            card_counts_global[card] += 1
            if b['is_counter']:
                card_counts_counter[card] += 1
            
            # Store details
            card_details[card]['hours'][hour] += 1
            card_details[card]['buckets'][bucket] += 1
            card_details[card]['opponents'].add(b['opp_tag'])

    # Identify Snipers
    snipers = []
    for card, count in card_counts_global.items():
        if count < 5: continue # Ignore very rare
        freq_g = count / total_battles
        
        count_c = card_counts_counter[card]
        freq_c = count_c / total_counters if total_counters > 0 else 0
        
        lift = freq_c / freq_g if freq_g > 0 else 0
        
        if lift > 1.8 and freq_g < 0.15: # High lift, not ubiquitous
            snipers.append((card, lift, freq_g, count))
            
    snipers.sort(key=lambda x: x[1], reverse=True)
    top_snipers = snipers[:5] # Top 5

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("CONTROLLO FATTORI CONFONDENTI: CARTE SNIPER (7k-8k)\n")
        f.write("Obiettivo: Verificare se le carte 'Sniper' (Alto Lift nei Counter) sono artefatti statistici.\n")
        f.write("Fattori: 1. Orario (Notte?), 2. Sotto-fasce (Concentrazione?), 3. Player Specialist (Pochi avversari?).\n")
        f.write("="*80 + "\n")
        
        if not top_snipers:
            f.write("Nessuna carta Sniper identificata con i criteri attuali.\n")
            return

        for card, lift, freq, count in top_snipers:
            details = card_details[card]
            
            f.write(f"\nCARTA: {card.upper()} (Lift: {lift:.2f}x, Global Freq: {freq*100:.1f}%, N={count})\n")
            f.write("-" * 60 + "\n")
            
            # 1. Orario
            hours = details['hours']
            night = sum(hours.get(h, 0) for h in range(0, 7))
            day = sum(hours.get(h, 0) for h in range(7, 24))
            night_share = night / count * 100
            f.write(f"1. ORARIO (00-07): {night_share:.1f}% partite notturne.\n")
            if night_share > 40:
                f.write("   -> WARNING: Carta prevalentemente notturna (Meta notturno diverso?).\n")
            
            # 2. Sotto-fasce
            buckets = details['buckets']
            f.write("2. DISTRIBUZIONE SOTTO-FASCE:\n")
            for b_key in sorted(buckets.keys()):
                b_count = buckets[b_key]
                b_share = b_count / count * 100
                f.write(f"   {b_key}-{b_key+250}: {b_share:.1f}% ({b_count})\n")
            
            # Check concentration
            max_bucket_share = max(buckets.values()) / count if count > 0 else 0
            if max_bucket_share > 0.6:
                 f.write("   -> WARNING: Forte concentrazione in una sotto-fascia.\n")

            # 3. Unique Opponents
            unique_opps = len(details['opponents'])
            opp_ratio = unique_opps / count
            f.write(f"3. AVVERSARI UNICI: {unique_opps} su {count} partite ({opp_ratio*100:.1f}%)\n")
            if opp_ratio < 0.5:
                f.write("   -> WARNING: Pochi specialisti (Stessi avversari incontrati più volte).\n")
            elif opp_ratio < 0.2:
                f.write("   -> ALARM: Probabile sniping da parte di 1-2 giocatori.\n")
            else:
                f.write("   -> OK: Avversari vari.\n")
                
        f.write("="*80 + "\n")