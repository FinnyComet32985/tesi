import os
import sys
import sqlite3
from collections import defaultdict
from scipy.stats import chi2_contingency

# Add parent directory to path to import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from battlelog_v2 import get_players_sessions
from test_deck_analysis import get_deck_cards_batch, get_deck_archetypes_batch, get_local_hour

DB_PATH = os.path.join(os.path.dirname(__file__), '../db/clash.db')

def analyze_ranked_card_fairness():
    output_dir = os.path.join(os.path.dirname(__file__), 'results/ranked')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'ranked_card_fairness_results.txt')
    
    print(f"\nEsecuzione Analisi Fairness per Carte in RANKED...")
    print(f"Output: {output_file}")
    
    # 1. Carica sessioni SOLO RANKED
    # Nota: In Ranked il meta è più stabile (tutte le carte sbloccate), quindi aggreghiamo tutto.
    players_sessions = get_players_sessions(mode_filter='Ranked', exclude_unreliable=False)
    
    # 2. Raccolta Dati in BUCKET (Time Slot, Region)
    # buckets[(time_slot, region)] = list of (player_deck_id, opponent_deck_id)
    buckets = defaultdict(list)
    all_deck_ids = set()
    
    TIME_SLOT_HOURS = 6 # 4 fasce orarie giornaliere (0-6, 6-12, 12-18, 18-24)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Raccolta dati battaglie Ranked...")
    for p in players_sessions:
        nationality = p.get('nationality')
        for s in p['sessions']:
            for b in s['battles']:
                if b['game_mode'] != 'Ranked': continue
                
                p_deck = b.get('deck_id')
                o_deck = b.get('opponent_deck_id')
                ts = b.get('timestamp')
                
                if p_deck and o_deck and ts:
                    all_deck_ids.add(p_deck)
                    all_deck_ids.add(o_deck)
                    
                    # Calcolo Bucket
                    hour = get_local_hour(ts, nationality)
                    time_slot = hour // TIME_SLOT_HOURS
                    region = nationality if nationality else "Unknown"
                    
                    buckets[(time_slot, region)].append((p_deck, o_deck))
    
    if not buckets:
        print("Nessuna battaglia Ranked trovata.")
        return

    # 3. Risoluzione Dati (Archetipi e Carte)
    print(f"Risoluzione dati per {len(all_deck_ids)} mazzi...")
    
    # Archetipi (per raggruppare i mazzi del giocatore)
    deck_to_arch = get_deck_archetypes_batch(cursor, all_deck_ids)
    
    # Carte (per analizzare il contenuto dei mazzi avversari)
    deck_to_cards = {}
    all_ids_list = list(all_deck_ids)
    CHUNK_SIZE = 900
    for i in range(0, len(all_ids_list), CHUNK_SIZE):
        chunk = all_ids_list[i:i+CHUNK_SIZE]
        batch = get_deck_cards_batch(cursor, chunk)
        for d_id, cards in batch.items():
            deck_to_cards[d_id] = {c['name'] for c in cards}
            
    conn.close()
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI FAIRNESS RANKED (PATH OF LEGENDS): CARTE AVVERSARIE\n")
        f.write("Obiettivo: Verificare se l'uso di certi archetipi attira specifiche carte avversarie in Ranked.\n")
        f.write("Controllo: Orario (Slot 6h) e Regione (Nazionalità) per garantire pool avversari simili.\n")
        f.write("="*100 + "\n\n")
        
        total_buckets = len(buckets)
        skipped_buckets = 0
        significant_buckets = 0
        
        # Ordina bucket per regione e orario
        sorted_keys = sorted(buckets.keys(), key=lambda x: (x[1], x[0]))
        
        for key in sorted_keys:
            time_slot, region = key
            battles = buckets[key]
            
            if len(battles) < 50: # Minimo 50 battaglie per bucket per avere significatività
                skipped_buckets += 1
                continue

            # 4. Analisi nel Bucket
            p_arch_counts = defaultdict(int)
            for p_id, _ in battles:
                arch = deck_to_arch.get(p_id, p_id)
                p_arch_counts[arch] += 1
            
            # Top archetipi nel bucket (almeno 10 usi)
            top_p_archs = [arch for arch, count in p_arch_counts.items() if count >= 10]
            if len(top_p_archs) < 2:
                skipped_buckets += 1
                continue

            # Carte avversarie comuni nel bucket (>5%)
            o_card_counts = defaultdict(int)
            for _, o_id in battles:
                if o_id in deck_to_cards:
                    for card in deck_to_cards[o_id]:
                        o_card_counts[card] += 1
            
            common_o_cards = [c for c, count in o_card_counts.items() if count > len(battles) * 0.05]
            if not common_o_cards:
                continue

            bucket_sig_cards = []
            
            for card in common_o_cards:
                matrix = []
                for arch in top_p_archs:
                    matches = [pair for pair in battles if deck_to_arch.get(pair[0], pair[0]) == arch]
                    has_card = sum(1 for _, o_id in matches if o_id in deck_to_cards and card in deck_to_cards[o_id])
                    no_card = len(matches) - has_card
                    matrix.append([has_card, no_card])
                
                try:
                    chi2, p, dof, ex = chi2_contingency(matrix)
                    if p < 0.05:
                        # Calcola delta e identifica gli archetipi estremi
                        rates_info = []
                        for idx, row in enumerate(matrix):
                            total = sum(row)
                            if total > 0:
                                rate = (row[0] / total) * 100
                                rates_info.append({'arch': top_p_archs[idx], 'rate': rate, 'count': row[0], 'total': total})
                        
                        if rates_info:
                            rates_info.sort(key=lambda x: x['rate'])
                            min_info = rates_info[0]
                            max_info = rates_info[-1]
                            delta = max_info['rate'] - min_info['rate']
                            
                            bucket_sig_cards.append({'card': card, 'p': p, 'delta': delta, 'min': min_info, 'max': max_info})
                except ValueError:
                    pass
            
            if bucket_sig_cards:
                significant_buckets += 1
                time_label = f"{time_slot*TIME_SLOT_HOURS:02d}:00-{(time_slot+1)*TIME_SLOT_HOURS:02d}:00"
                f.write(f"BUCKET: {region} | {time_label} | Battles: {len(battles)}\n")
                f.write(f"Confronto tra {len(top_p_archs)} archetipi. Carte sospette: {len(bucket_sig_cards)}\n")
                
                bucket_sig_cards.sort(key=lambda x: x['p'])
                for item in bucket_sig_cards[:5]: # Top 5
                    f.write(f"  > {item['card']:<20} (p={item['p']:.4f}, Delta={item['delta']:.1f}%)\n")
                    # Tronchiamo il nome dell'archetipo se è un hash lungo per leggibilità
                    max_arch = str(item['max']['arch'])
                    min_arch = str(item['min']['arch'])
                    if len(max_arch) > 20: max_arch = max_arch[:8] + "..."
                    if len(min_arch) > 20: min_arch = min_arch[:8] + "..."
                    
                    f.write(f"    - Max Freq: {item['max']['rate']:.1f}% vs {max_arch} (n={item['max']['count']}/{item['max']['total']})\n")
                    f.write(f"    - Min Freq: {item['min']['rate']:.1f}% vs {min_arch} (n={item['min']['count']}/{item['min']['total']})\n")
                f.write("-" * 80 + "\n")

        f.write("\n" + "="*100 + "\n")
        f.write(f"Totale Bucket: {total_buckets}\n")
        f.write(f"Bucket Saltati (Dati insufficienti): {skipped_buckets}\n")
        f.write(f"Bucket con Anomalie Significative: {significant_buckets}\n")
        f.write("="*100 + "\n")
            
        print("Analisi completata.")

if __name__ == "__main__":
    analyze_ranked_card_fairness()