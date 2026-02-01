import os
import sys
import sqlite3
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from collections import defaultdict

# Add parent directory to path to import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data.test_deck_analysis import get_deck_cards_batch, get_deck_archetypes_batch, get_local_hour

DB_PATH = os.path.join(os.path.dirname(__file__), '../db/clash.db')

def analyze_card_regression(players_sessions, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'results/ranked')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'card_regression_results.txt')
    
    print(f"\nGenerazione report Regressione Lineare Carte in: {output_file}")
    
    # 1. Preparazione Dataset
    print("Preparazione dati per regressione...")
    data_rows = []
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Cache per deck
    deck_cards_cache = {}
    deck_arch_cache = {}
    all_deck_ids = set()
    
    # Prima passata: raccogli ID
    for p in players_sessions:
        for s in p['sessions']:
            for b in s['battles']:
                if b['game_mode'] == 'Ranked' and b.get('deck_id') and b.get('opponent_deck_id'):
                    all_deck_ids.add(b['deck_id'])
                    all_deck_ids.add(b['opponent_deck_id'])

    # Fetch in batch
    all_ids_list = list(all_deck_ids)
    CHUNK_SIZE = 900
    for i in range(0, len(all_ids_list), CHUNK_SIZE):
        chunk = all_ids_list[i:i+CHUNK_SIZE]
        # Cards
        batch_cards = get_deck_cards_batch(cursor, chunk)
        for d_id, cards in batch_cards.items():
            deck_cards_cache[d_id] = {c['name'] for c in cards}
        # Archetypes
        batch_arch = get_deck_archetypes_batch(cursor, chunk)
        deck_arch_cache.update(batch_arch)
        
    conn.close()
    
    # Seconda passata: costruisci righe
    for p in players_sessions:
        nationality = p.get('nationality', 'Unknown')
        # Calcolo Winrate Recente (rolling window 5)
        outcomes = []
        
        for s in p['sessions']:
            for b in s['battles']:
                if b['game_mode'] != 'Ranked': continue
                
                p_deck = b.get('deck_id')
                o_deck = b.get('opponent_deck_id')
                
                if not p_deck or not o_deck: continue
                if p_deck not in deck_arch_cache or o_deck not in deck_cards_cache: continue
                
                # Recent Winrate
                recent_wr = sum(outcomes[-5:]) / len(outcomes[-5:]) if outcomes else 0.5
                outcomes.append(b['win'])
                
                # Hour
                ts = b.get('timestamp')
                hour = get_local_hour(ts, nationality) if ts else 12
                
                row = {
                    'archetype': deck_arch_cache[p_deck],
                    'recent_wr': recent_wr,
                    'trophies': b.get('trophies_before', 0), # In ranked questo è il rating
                    'hour': hour,
                    'region': nationality,
                    'opp_cards': deck_cards_cache[o_deck]
                }
                data_rows.append(row)
                
    df = pd.DataFrame(data_rows)
    if df.empty:
        print("Nessun dato per la regressione.")
        return

    # Filtra archetipi rari (top 10)
    top_archetypes = df['archetype'].value_counts().nlargest(10).index.tolist()
    df = df[df['archetype'].isin(top_archetypes)]
    
    # Carte avversarie da testare (Top 5 più comuni)
    all_opp_cards = [c for cards in df['opp_cards'] for c in cards]
    top_opp_cards = pd.Series(all_opp_cards).value_counts().nlargest(5).index.tolist()
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("REGRESSIONE LINEARE (Linear Probability Model)\n")
        f.write("Formula: Has_Card ~ Archetype + Recent_Winrate + Trophies + Hour + Region\n")
        f.write("Obiettivo: Vedere se l'Archetype è un predittore significativo della carta avversaria, al netto di altri fattori.\n")
        f.write("="*100 + "\n\n")
        
        for target_card in top_opp_cards:
            f.write(f"--- TARGET: {target_card} ---\n")
            
            # Crea colonna target binaria
            df['target'] = df['opp_cards'].apply(lambda x: 1 if target_card in x else 0)
            
            # Formula statsmodels
            # C(archetype) crea dummy variables automaticamente
            formula = "target ~ C(archetype) + recent_wr + trophies + C(region)"
            
            try:
                model = smf.ols(formula=formula, data=df).fit()
                
                # Estrai coefficienti significativi per gli archetipi
                f.write(f"R-squared: {model.rsquared:.4f}\n")
                f.write("Coefficienti Significativi (p < 0.05) per Archetipi:\n")
                
                params = model.params
                pvalues = model.pvalues
                
                found_sig = False
                for name, p_val in pvalues.items():
                    if "C(archetype)" in name and p_val < 0.05:
                        f.write(f"  {name:<50} | Coeff: {params[name]:+.4f} | p={p_val:.4f}\n")
                        found_sig = True
                
                if not found_sig:
                    f.write("  Nessun archetipo influenza significativamente questa carta.\n")
                    
            except Exception as e:
                f.write(f"Errore regressione: {e}\n")
            
            f.write("\n" + "-"*100 + "\n")