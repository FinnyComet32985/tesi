import logging
from api_client import fetch_page, fetch_matchup
from parsers import parse_battle_data, parse_oldest_timestamp_from_page, parse_deck_from_battle, parse_all_deck_stats_from_page
from db_manager import get_last_battle_timestamp, insert_battle_and_decks, update_player_deck_stats

def _collect_battles_from_page(soup, tag, last_db_ts, conn, cursor):
    """Funzione helper per processare le battaglie di una singola pagina."""
    battles = soup.select("div.battle")
    if not battles:
        return True, None # stop = True, oldest_ts = None

    stop = False
    for div in battles:
        battle = parse_battle_data(div, tag)

        if last_db_ts and battle["timestamp"] <= last_db_ts:
            stop = True
            break

        player_deck_cards = parse_deck_from_battle(div, is_opponent=False)
        opponent_deck_cards = parse_deck_from_battle(div, is_opponent=True) if battle["opponent_tag"] else None

        

        matchup_data = None
        if player_deck_cards and opponent_deck_cards:
            # Assicurati che entrambi i mazzi abbiano 9 carte (8 + torre)
            if len(player_deck_cards) == 9 and len(opponent_deck_cards) == 9:
                matchup_data = fetch_matchup(player_deck_cards, opponent_deck_cards)

        insert_battle_and_decks(cursor, battle, player_deck_cards, opponent_deck_cards, matchup_data)

    conn.commit()
    oldest_ts = parse_oldest_timestamp_from_page(soup)
    return stop, oldest_ts

def _collect_scroll(tag, last_db_ts, conn, cursor):
    """Scorre le pagine di battaglie 'scroll' e le inserisce nel DB."""
    path = f"/player/{tag}/battles"
    while path:
        soup = fetch_page(path)
        if not soup: 
            break

        stop, oldest_ts = _collect_battles_from_page(soup, tag, last_db_ts, conn, cursor)
        if stop or not oldest_ts:
            break
        
        path = f"/player/{tag}/battles/scroll/{oldest_ts}/type/all"

def _collect_history(tag, last_db_ts, start_ts, conn, cursor):
    """Scorre le pagine di battaglie 'history' (più vecchie) e le inserisce nel DB."""
    before_ms = start_ts * 1000
    while True:
        path = f"/player/{tag}/battles/history?before={before_ms}&&"
        soup = fetch_page(path)
        if not soup: 
            break

        stop, oldest_ts = _collect_battles_from_page(soup, tag, last_db_ts, conn, cursor)
        if stop or not oldest_ts:
            break
        
        before_ms = oldest_ts * 1000

def _update_all_deck_stats_for_player(tag: str, conn, cursor):
    """
    Recupera le statistiche (confidence) per tutti i mazzi usati da un giocatore.
    """
    logging.info(f"Inizio aggiornamento statistiche mazzi per il giocatore {tag}")
    
    # 1. Scarica la pagina /decks del giocatore
    decks_page_soup = fetch_page(f"/player/{tag}/decks")
    if not decks_page_soup:
        logging.warning(f"Impossibile recuperare la pagina delle statistiche dei mazzi per {tag}.")
        return

    # 2. Esegui il parsing di TUTTI i mazzi e le loro statistiche dalla pagina,
    #    mappandoli tramite il loro archetype_hash.
    stats_by_archetype = parse_all_deck_stats_from_page(decks_page_soup)
    if not stats_by_archetype:
        logging.info(f"Nessuna statistica di mazzo trovata sulla pagina per {tag}.")
        return

    # 3. Per ogni mazzo nel nostro DB, controlla se esiste una corrispondenza
    #    di archetipo nelle statistiche appena scaricate.
    cursor.execute("SELECT deck_hash, archetype_hash FROM decks WHERE deck_hash IN (SELECT DISTINCT player_deck_id FROM battles WHERE player_tag = ?)", (tag,))
    player_decks = cursor.fetchall()
    
    for deck_hash, archetype_hash in player_decks:
        if archetype_hash in stats_by_archetype:
            stats = stats_by_archetype[archetype_hash]
            update_player_deck_stats(cursor, tag, deck_hash, stats)
            
    conn.commit()

def fetch_all_battles(tag: str, conn, cursor):
    """
    Orchestra il recupero di tutta la cronologia battaglie di un giocatore,
    partendo da dove si era interrotto.
    """
    logging.info(f"Inizio recupero battaglie per {tag}")

    last_db_ts = get_last_battle_timestamp(cursor, tag)

    # Controlla la prima pagina per ottenere il timestamp di partenza per la cronologia
    initial_soup = fetch_page(f"/player/{tag}/battles")
    if not initial_soup:
        logging.warning(f"Impossibile recuperare la pagina iniziale delle battaglie per {tag}.")
        return

    start_history_ts = parse_oldest_timestamp_from_page(initial_soup)

    _collect_scroll(tag, last_db_ts, conn, cursor)

    if start_history_ts:
        _collect_history(tag, last_db_ts, start_history_ts, conn, cursor)
    
    # Dopo aver recuperato tutte le nuove battaglie, aggiorniamo le statistiche dei mazzi
    _update_all_deck_stats_for_player(tag, conn, cursor)

    logging.info(f"Recupero battaglie per {tag} completato.")