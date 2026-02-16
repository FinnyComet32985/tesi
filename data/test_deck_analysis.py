import os
import statistics
import sqlite3
import sys
from datetime import datetime
from scipy.stats import chi2_contingency, kruskal, levene
import pytz
from collections import defaultdict

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

def _calculate_avg_level(deck_cards):
    if not deck_cards: return 0
    levels = [c['level'] for c in deck_cards if c.get('level') is not None]
    return statistics.mean(levels) if levels else 0

def analyze_matchmaking_fairness(players_sessions, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'matchmaking_fairness_results.txt')

    print(f"\nGenerazione report Matchmaking Fairness (Deck vs Opponent Distribution) in: {output_file}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Configuration
    TIME_SLOT_HOURS = 8         
    TROPHY_BUCKET_SIZE = 1500   
    MIN_BATTLES_PER_BUCKET = 20 
    MIN_BATTLES_PER_DECK = 3    

    # Data Structure: buckets[(time_slot, trophy_bucket)] = list of (player_tag, player_deck, opp_deck)
    buckets = {}
    
    # Set per raccogliere tutti i deck ID da risolvere
    all_deck_ids = set()
    temp_battles = [] # (time_slot, trophy_bucket, player_tag, p_deck_id, o_deck_id)

    for p in players_sessions:
        nationality = p.get('nationality')
        player_tag = p['tag']
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
                
                # Rimosso region, aggiunto player_tag per tracciamento
                temp_battles.append((time_slot, trophy_bucket, player_tag, p_deck, o_deck))

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
    for time_slot, trophy_bucket, p_tag, p_id, o_id in temp_battles:
        p_arch = deck_to_archetype.get(p_id, p_id) # Fallback su ID se manca archetipo
        o_arch = deck_to_archetype.get(o_id, o_id)
        
        key = (time_slot, trophy_bucket)
        if key not in buckets: buckets[key] = []
        buckets[key].append((p_tag, p_arch, o_arch))

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI FAIRNESS MATCHMAKING (DIPENDENZA DECK AVVERSARIO DAL PROPRIO DECK)\n")
        f.write("Obiettivo: Verificare se, a parità di condizioni (Orario e Trofei), il mazzo che usi influenza il MAZZO (Archetipo) che trovi contro.\n")
        f.write("Nota: Analisi aggregata su TUTTI i player nel bucket (Inter-Player Comparison) per superare il limite dei One-Trick Ponies.\n")
        f.write("Metodo: Test Chi-Quadro su tabella di contingenza (Player Archetype vs Opponent Archetype).\n")
        f.write("Ipotesi Nulla (H0 - Fair): La distribuzione degli avversari è INDIPENDENTE dal tuo mazzo.\n")
        f.write("Ipotesi Alternativa (H1 - Rigged): La distribuzione degli avversari DIPENDE dal tuo mazzo.\n")
        f.write("Interpretazione: P-value < 0.05 => Rifiuto H0 (Sospetto Rigging). P-value >= 0.05 => Mantengo H0 (Fair).\n")
        f.write("="*100 + "\n\n")

        f.write(f"Totale Battaglie Analizzate: {len(temp_battles)}\n")
        significant_buckets = 0
        total_tested_buckets = 0
        skipped_buckets = 0
        skipped_one_trick = 0
        
        sorted_keys = sorted(buckets.keys(), key=lambda x: (x[1], x[0])) # Sort by Trophies then Time
        
        for key in sorted_keys:
            battles = buckets[key]
            
            time_slot, trophy_bucket = key
            time_label = f"{time_slot*TIME_SLOT_HOURS:02d}:00-{(time_slot+1)*TIME_SLOT_HOURS:02d}:00"
            range_label = f"{trophy_bucket}-{trophy_bucket+TROPHY_BUCKET_SIZE}"
            
            # Conta giocatori unici nel bucket
            unique_players = set(b[0] for b in battles)
            bucket_desc = f"{range_label} | {time_label} | Players: {len(unique_players)}"

            if len(battles) < MIN_BATTLES_PER_BUCKET: 
                skipped_buckets += 1
                f.write(f"SKIP {bucket_desc}: {len(battles)} battles < {MIN_BATTLES_PER_BUCKET} (Min richiesto)\n")
                continue
            
            # 1. Identifica i Top Archetipi del Giocatore in questo bucket
            p_counts = {}
            for tag, p_d, o_d in battles:
                p_counts[p_d] = p_counts.get(p_d, 0) + 1
            
            top_p_decks = [d for d, c in p_counts.items() if c >= MIN_BATTLES_PER_DECK]
            if len(top_p_decks) < 2: 
                skipped_one_trick += 1
                f.write(f"SKIP {bucket_desc}: Solo {len(top_p_decks)} deck usati >= {MIN_BATTLES_PER_DECK} volte. (Richiesti >= 2 deck per confronto). Counts: {p_counts}\n")
                continue # Servono almeno 2 mazzi diversi per confrontare
            
            # Filtra le battaglie rilevanti (dove il giocatore usava uno dei top deck)
            relevant_battles = [b for b in battles if b[1] in top_p_decks]
            
            # 2. Identifica i Top Archetipi Avversari in questo bucket
            o_counts = {}
            for tag, p_d, o_d in relevant_battles:
                o_counts[o_d] = o_counts.get(o_d, 0) + 1
            
            top_o_decks = [d for d, c in o_counts.items() if c >= 3] # Almeno 3 apparizioni per essere rilevante
            if len(top_o_decks) < 2: continue
            
            # 3. Costruisci Tabella di Contingenza (Player Arch vs Opponent Arch)
            matrix = []
            valid_p_decks = []
            
            for p_d in top_p_decks:
                row = []
                # Prendi tutti gli avversari incontrati da questo archetipo
                opps_for_p = [b[2] for b in relevant_battles if b[1] == p_d]
                
                for o_d in top_o_decks:
                    count = opps_for_p.count(o_d)
                    row.append(count)
                
                if sum(row) > 0:
                    matrix.append(row)
                    valid_p_decks.append(p_d)
            
            if len(matrix) < 2: continue
            
            total_tested_buckets += 1
            
            try:
                chi2, p, dof, ex = chi2_contingency(matrix)
                
                if p < 0.05:
                    significant_buckets += 1
                
                sig_label = "SIGNIFICATIVO -> SOSPETTO (Dipendenza rilevata)" if p < 0.05 else "NON SIGNIFICATIVO -> FAIR (Indipendenza)"
                f.write(f"Bucket: {range_label} | Orario: {time_label} | Players: {len(unique_players)} | Battles: {len(relevant_battles)}\n")
                f.write(f"Matrice: [Righe = {len(valid_p_decks)} (Tuoi Archetipi)] x [Colonne = {len(top_o_decks)} (Archetipi Avversari)]\n")
                f.write(f"P-value: {p:.6f} -> {sig_label}\n")
                f.write("-" * 80 + "\n")
            
            except Exception as e:
                f.write(f"Bucket: {range_label} | Error: {e}\n")

        f.write("\n" + "="*100 + "\n")
        f.write(f"Totale Bucket Testati: {total_tested_buckets}\n")
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

def analyze_arena_progression_curve(players_sessions, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'arena_progression_curve.txt')

    print(f"\nGenerazione report Arena Progression Curve in: {output_file}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Collect opponent deck IDs and trophies
    battles_data = [] # (trophies, opponent_deck_id)
    deck_ids = set()
    
    for p in players_sessions:
        for s in p['sessions']:
            for b in s['battles']:
                if b['game_mode'] == 'Ladder' and b.get('trophies_before') and b.get('opponent_deck_id'):
                    battles_data.append((b['trophies_before'], b['opponent_deck_id']))
                    deck_ids.add(b['opponent_deck_id'])
    
    # Fetch cards
    print(f"Recupero carte per {len(deck_ids)} mazzi avversari...")
    deck_cards_map = {}
    all_ids = list(deck_ids)
    CHUNK = 900
    for i in range(0, len(all_ids), CHUNK):
        batch = get_deck_cards_batch(cursor, all_ids[i:i+CHUNK])
        deck_cards_map.update(batch)
    
    conn.close()
    
    # Calculate avg levels
    bucket_stats = defaultdict(list)
    BUCKET_SIZE = 100
    
    for t, d_id in battles_data:
        cards = deck_cards_map.get(d_id)
        if cards:
            avg_lvl = _calculate_avg_level(cards)
            if avg_lvl > 0:
                b_idx = (t // BUCKET_SIZE) * BUCKET_SIZE
                bucket_stats[b_idx].append(avg_lvl)
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI CURVA PROGRESSIONE ARENA (LIVELLI AVVERSARI)\n")
        f.write("Obiettivo: Verificare se la crescita dei livelli avversari è lineare o esponenziale (Gatekeeping).\n")
        f.write("Metodo: Media Livello Carte Avversario per fascia di 100 trofei.\n")
        f.write("="*80 + "\n")
        f.write(f"{'RANGE':<15} | {'N':<6} | {'AVG OPP LEVEL':<15} | {'DELTA':<10}\n")
        f.write("-" * 80 + "\n")
        
        sorted_keys = sorted(bucket_stats.keys())
        prev_avg = None
        deltas = []
        
        for k in sorted_keys:
            vals = bucket_stats[k]
            if len(vals) < 10: continue
            
            avg = statistics.mean(vals)
            delta_str = ""
            if prev_avg is not None:
                delta = avg - prev_avg
                deltas.append(delta)
                delta_str = f"{delta:+.3f}"
            
            f.write(f"{k}-{k+BUCKET_SIZE:<15} | {len(vals):<6} | {avg:<15.3f} | {delta_str:<10}\n")
            prev_avg = avg
            
        f.write("-" * 80 + "\n")
        if deltas:
            avg_increase = statistics.mean(deltas)
            f.write(f"Aumento Medio Livelli per fascia ({BUCKET_SIZE} trofei): {avg_increase:+.4f}\n")
        f.write("="*80 + "\n")