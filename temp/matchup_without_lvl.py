import sqlite3
import logging
import sys
import os
import time

# Aggiunge la directory padre al path per importare i moduli del progetto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api_client import fetch_matchup

DB_PATH = "../db/clash.db"

def get_deck_cards(cursor, deck_hash):
    """Recupera le carte di un mazzo dato il suo hash."""
    cursor.execute("SELECT card_name, card_level FROM deck_cards WHERE deck_hash = ?", (deck_hash,))
    rows = cursor.fetchall()
    cards = []
    for name, level in rows:
        cards.append({"name": name, "level": level})
    return cards

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    if not os.path.exists(DB_PATH):
        logging.error(f"Database non trovato in {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Seleziona tutte le battaglie che hanno i mazzi ma non hanno ancora il matchup_no_lvl calcolato
    # Rimuovere "AND matchup_no_lvl IS NULL" se si vuole forzare il ricalcolo su tutto
    query = """
        SELECT battle_id, player_deck_id, opponent_deck_id 
        FROM battles 
        WHERE player_deck_id IS NOT NULL 
          AND opponent_deck_id IS NOT NULL
          AND matchup_no_lvl IS NULL
    """
    
    cursor.execute(query)
    battles = cursor.fetchall()
    
    total = len(battles)
    logging.info(f"Trovate {total} battaglie da aggiornare.")

    updated_count = 0
    
    for i, (battle_id, p_deck_id, o_deck_id) in enumerate(battles):
        print(f"{i}/{total}\n")
        try:
            p_cards = get_deck_cards(cursor, p_deck_id)
            o_cards = get_deck_cards(cursor, o_deck_id)

            # Verifica che i mazzi siano validi (9 carte inclusa la torre)
            if len(p_cards) != 9 or len(o_cards) != 9:
                continue

            # Chiamata API con livelli normalizzati
            matchup_data = fetch_matchup(p_cards, o_cards, force_equal_levels=True)
            
            if matchup_data and "winRate" in matchup_data:
                matchup_no_lvl = matchup_data["winRate"]
                
                cursor.execute(
                    "UPDATE battles SET matchup_no_lvl = ? WHERE battle_id = ?", 
                    (matchup_no_lvl, battle_id)
                )
                updated_count += 1
            
            # Commit ogni 50 aggiornamenti per sicurezza
            if updated_count % 50 == 0:
                conn.commit()
                print(f"Progress: {i+1}/{total} - Updated: {updated_count}", end='\r')

        except Exception as e:
            logging.error(f"Errore processando battle_id {battle_id}: {e}")
            continue

    conn.commit()
    conn.close()
    logging.info(f"\nAggiornamento completato. {updated_count} battaglie aggiornate su {total}.")

if __name__ == "__main__":
    main()