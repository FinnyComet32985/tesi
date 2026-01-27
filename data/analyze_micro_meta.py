import sqlite3
from collections import defaultdict, Counter
import os
import statistics

def analyze_micro_meta_150(players_sessions, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'micro_meta_150_results.txt')
    
    print(f"\nGenerazione report Micro-Meta (150 Trofei) in: {output_file}")
    
    db_path = os.path.join(os.path.dirname(__file__), '../db/clash.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    BUCKET_SIZE = 150
    
    # Data Structures
    # bucket_id -> list of opponent_deck_ids
    bucket_decks = defaultdict(list)
    
    # player -> bucket -> list of matchups (no_lvl)
    player_bucket_mus = defaultdict(lambda: defaultdict(list))
    
    # list of (trophies_start)
    streak_starts = []
    
    all_deck_ids = set()
    
    for p in players_sessions:
        tag = p['tag']
        # Flatten sessions for streak analysis
        all_battles = []
        for s in p['sessions']:
            all_battles.extend(s['battles'])
            
        # Analyze Battles
        current_loss_streak = 0
        streak_start_trophies = None
        
        for b in all_battles:
            if b['game_mode'] != 'Ladder': continue
            
            t = b.get('trophies_before')
            if not t: continue
            
            bucket_id = t // BUCKET_SIZE
            
            # Collect Deck Data
            o_deck = b.get('opponent_deck_id')
            if o_deck:
                bucket_decks[bucket_id].append(o_deck)
                all_deck_ids.add(o_deck)
            
            # Collect Matchup Data
            mu = b.get('matchup_no_lvl')
            if mu is not None:
                player_bucket_mus[tag][bucket_id].append(mu)
            
            # Streak Detection (Losses)
            if b['win'] == 0:
                if current_loss_streak == 0:
                    streak_start_trophies = t
                current_loss_streak += 1
            else:
                if current_loss_streak >= 3 and streak_start_trophies:
                    streak_starts.append(streak_start_trophies)
                current_loss_streak = 0
                streak_start_trophies = None
        
        # Check last streak
        if current_loss_streak >= 3 and streak_start_trophies:
            streak_starts.append(streak_start_trophies)

    # Resolve Decks to Cards
    print(f"Risoluzione carte per {len(all_deck_ids)} mazzi...")
    deck_cards_map = {}
    all_deck_ids_list = list(all_deck_ids)
    CHUNK_SIZE = 900
    
    for i in range(0, len(all_deck_ids_list), CHUNK_SIZE):
        chunk = all_deck_ids_list[i:i+CHUNK_SIZE]
        placeholders = ','.join(['?'] * len(chunk))
        query = f"SELECT deck_hash, card_name FROM deck_cards WHERE deck_hash IN ({placeholders})"
        cursor.execute(query, chunk)
        for dh, cn in cursor.fetchall():
            if dh not in deck_cards_map: deck_cards_map[dh] = []
            deck_cards_map[dh].append(cn)
            
    conn.close()
    
    # Calculate Card Frequencies per Bucket
    bucket_card_freqs = {}
    card_bucket_distribution = defaultdict(list)
    
    sorted_buckets = sorted(bucket_decks.keys())
    
    for bid in sorted_buckets:
        decks = bucket_decks[bid]
        total_decks = len(decks)
        if total_decks < 50: continue # Skip low sample buckets
        
        counts = Counter()
        for d_id in decks:
            if d_id in deck_cards_map:
                counts.update(deck_cards_map[d_id])
        
        freqs = {c: count/total_decks for c, count in counts.items()}
        bucket_card_freqs[bid] = freqs
        
        for c, f in freqs.items():
            card_bucket_distribution[c].append(f)
            
    # Calculate Global Mean/Std per Card (across buckets)
    card_stats = {}
    for c, freqs in card_bucket_distribution.items():
        if len(freqs) < 5: continue
        card_stats[c] = {
            'mean': statistics.mean(freqs),
            'std': statistics.stdev(freqs) if len(freqs) > 1 else 0
        }

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI MICRO-META (BUCKET 150 TROFEI)\n")
        f.write("Obiettivo: Identificare anomalie locali (Micro-Metas) e Gatekeeping.\n")
        f.write("="*80 + "\n\n")
        
        # 1. DOMINANT CARDS & TRANSITION RATE
        f.write("1. CARTE DOMINANTI & TASSO DI TRANSIZIONE\n")
        f.write("Dominant: Frequenza > Media Globale + 2*StdDev.\n")
        f.write("Transition: 1 - Jaccard Index (Top 15 Cards) rispetto al bucket precedente.\n")
        f.write("-" * 100 + "\n")
        f.write(f"{'BUCKET':<15} | {'N. DECKS':<8} | {'TRANSITION':<10} | {'DOMINANT CARDS (Anomalie)'}\n")
        f.write("-" * 100 + "\n")
        
        prev_top_cards = set()
        
        for bid in sorted_buckets:
            if bid not in bucket_card_freqs: continue
            
            freqs = bucket_card_freqs[bid]
            
            # Dominant
            dominant = []
            for c, freq in freqs.items():
                if c in card_stats:
                    stats = card_stats[c]
                    if stats['std'] > 0:
                        z = (freq - stats['mean']) / stats['std']
                        if z > 2.0:
                            dominant.append(f"{c} (+{z:.1f}σ)")
            
            # Transition
            top_cards = set(dict(sorted(freqs.items(), key=lambda x: x[1], reverse=True)[:15]).keys())
            transition_rate = 0.0
            if prev_top_cards:
                intersection = len(top_cards.intersection(prev_top_cards))
                union = len(top_cards.union(prev_top_cards))
                jaccard = intersection / union if union > 0 else 0
                transition_rate = 1.0 - jaccard
            
            prev_top_cards = top_cards
            
            dom_str = ", ".join(dominant[:5]) # Show top 5 dominant
            label = f"{bid*BUCKET_SIZE}-{(bid+1)*BUCKET_SIZE}"
            
            f.write(f"{label:<15} | {len(bucket_decks[bid]):<8} | {transition_rate:<10.2f} | {dom_str}\n")

        # 2. HOSTILITY COEFFICIENT
        f.write("\n" + "="*80 + "\n")
        f.write("2. COEFFICIENTE DI OSTILITÀ (Hostility Coefficient)\n")
        f.write("Misura quanto il meta locale è peggiore per il giocatore rispetto alla sua media globale.\n")
        f.write("Hostility = Global_Avg_MU - Local_Avg_MU (Positivo = Ostile).\n")
        f.write("-" * 80 + "\n")
        f.write(f"{'BUCKET':<15} | {'AVG HOSTILITY':<15} | {'STATUS'}\n")
        f.write("-" * 80 + "\n")
        
        bucket_hostility = defaultdict(list)
        
        for tag, buckets_data in player_bucket_mus.items():
            # Calculate Global Avg for player
            all_mus = []
            for mus in buckets_data.values(): all_mus.extend(mus)
            if not all_mus: continue
            global_avg = statistics.mean(all_mus)
            
            for bid, mus in buckets_data.items():
                local_avg = statistics.mean(mus)
                hostility = global_avg - local_avg
                bucket_hostility[bid].append(hostility)
        
        for bid in sorted_buckets:
            if bid not in bucket_hostility: continue
            vals = bucket_hostility[bid]
            if len(vals) < 5: continue
            
            avg_h = statistics.mean(vals)
            status = "NEUTRAL"
            if avg_h > 2.0: status = "HOSTILE (Gatekeeping?)"
            elif avg_h < -2.0: status = "FRIENDLY (Boost?)"
            
            label = f"{bid*BUCKET_SIZE}-{(bid+1)*BUCKET_SIZE}"
            f.write(f"{label:<15} | {avg_h:<+15.2f} | {status}\n")

        # 3. STREAK BOUNDARY ANALYSIS
        f.write("\n" + "="*80 + "\n")
        f.write("3. ANALISI POSIZIONE STREAK (Gatekeeping ai Confini)\n")
        f.write("Dove iniziano le serie di sconfitte (>=3) all'interno del bucket?\n")
        f.write("-" * 80 + "\n")
        
        offsets = [t % BUCKET_SIZE for t in streak_starts]
        if not offsets:
            f.write("Nessuna streak trovata.\n")
        else:
            # Bins: Start (0-30), Mid (30-120), End (120-150)
            c_start = sum(1 for x in offsets if x < 30)
            c_mid = sum(1 for x in offsets if 30 <= x < 120)
            c_end = sum(1 for x in offsets if x >= 120)
            total = len(offsets)
            
            # Normalize by range width
            # Start: 30 units, Mid: 90 units, End: 30 units
            # Density = Count / Width
            d_start = c_start / 30
            d_mid = c_mid / 90
            d_end = c_end / 30
            
            f.write(f"Totale Streak Analizzate: {total}\n")
            f.write(f"Early Bucket (0-30):   {c_start} (Densità: {d_start:.2f})\n")
            f.write(f"Mid Bucket   (30-120): {c_mid} (Densità: {d_mid:.2f})\n")
            f.write(f"Late Bucket  (120-150): {c_end} (Densità: {d_end:.2f})\n")
            
            if d_end > d_mid * 1.2:
                f.write("RISULTATO: GATEKEEPING RILEVATO. Le streak iniziano frequentemente alla fine del bucket (prima del salto).\n")
            elif d_start > d_mid * 1.2:
                f.write("RISULTATO: WALL INIZIALE. Le streak iniziano appena entrati nel nuovo bucket.\n")
            else:
                f.write("RISULTATO: DISTRIBUZIONE UNIFORME.\n")
        
        f.write("="*80 + "\n")
