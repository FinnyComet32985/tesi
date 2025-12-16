import logging
from api_client import fetch_page
from parsers import (
    parse_player_data,
    parse_towers_and_heroes,
    parse_evolutions,
    parse_player_cards
)
from db_manager import (
    update_player_stats,
    update_player_towers,
    update_player_heroes,
    update_player_evolutions,
    update_player_cards
)

def update_player_profile(tag: str, conn, cursor):
    """
    Orchestra il recupero e l'aggiornamento completo del profilo di un giocatore.
    """
    logging.info(f"Inizio aggiornamento profilo per {tag}")
    
    # 1. Fetch e Parse dati profilo principale
    profile_soup = fetch_page(f"/player/{tag}")
    if not profile_soup: 
        return

    player_data = parse_player_data(profile_soup)
    towers, heroes = parse_towers_and_heroes(profile_soup)
    evolutions = parse_evolutions(profile_soup)

    # 2. Fetch e Parse dati carte
    cards_soup = fetch_page(f"/player/{tag}/cards")
    cards = parse_player_cards(cards_soup) if cards_soup else []

    # 3. Aggiornamento del database
    if player_data: 
        update_player_stats(cursor, tag, player_data)
    if towers: 
        update_player_towers(cursor, tag, towers)
    if heroes: 
        update_player_heroes(cursor, tag, heroes)
    if evolutions: 
        update_player_evolutions(cursor, tag, evolutions)
    if cards: 
        update_player_cards(cursor, tag, cards)
    
    conn.commit()
    logging.info(f"Profilo per {tag} aggiornato con successo.")