import hashlib
import logging
from datetime import datetime

def load_tags(cursor) -> list:
    """Carica i TAG dei giocatori dal database."""
    try:
        cursor.execute("SELECT player_tag FROM players")
        rows = cursor.fetchall()
        return [row[0] for row in rows]
    except Exception as e:
        logging.error(f"Errore durante il caricamento dei tag: {e}")
        return []

def update_player_stats(cursor, tag: str, player_data: tuple):
    """Aggiorna le statistiche base di un giocatore nel database."""
    columns = ['player_name', 'clan_name', 'trophies', 'arena', 'rank', 'wins', 'losses', 'three_crown_wins', 'total_games', 'account_age_seconds', 'time_spent_seconds', 'games_per_day']
    
    for i, col_name in enumerate(columns):
        cursor.execute(f"UPDATE players SET {col_name} = ? WHERE player_tag = ?", (player_data[i], tag))

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("UPDATE players SET last_updated = ? WHERE player_tag = ?", (current_time, tag))

def update_player_towers(cursor, tag: str, towers: list):
    """Aggiorna le torri di un giocatore nel database."""
    for tower in towers:
        cursor.execute("INSERT OR REPLACE INTO player_card(player_tag, card_name, level, found, has_evolution, has_hero) VALUES(?, ?, ?, ?, 0, 0)", 
                       (tag, tower["name"], tower["level"], 1 if tower["level"] > 0 else 0))

def update_player_heroes(cursor, tag: str, heroes: list):
    """Aggiorna gli eroi di un giocatore nel database."""
    for hero in heroes:
        is_found = 1 if hero["found"] else 0
        cursor.execute("INSERT INTO player_card(player_tag, card_name, has_hero) VALUES(?, ?, ?) ON CONFLICT(player_tag, card_name) DO UPDATE SET has_hero=excluded.has_hero",
                       (tag, hero["name"], is_found))

def update_player_evolutions(cursor, tag: str, evolutions: list):
    """Aggiorna le evoluzioni di un giocatore nel database."""
    for evolution in evolutions:
        is_found = 1 if evolution["found"] else 0
        cursor.execute("INSERT INTO player_card(player_tag, card_name, has_evolution) VALUES(?, ?, ?) ON CONFLICT(player_tag, card_name) DO UPDATE SET has_evolution=excluded.has_evolution",
                       (tag, evolution["name"], is_found))

def update_player_cards(cursor, tag: str, cards: list):
    """Aggiorna le carte di un giocatore nel database."""
    for card in cards:
        is_found = 1 if card["level"] and card["level"] > 0 else 0
        cursor.execute("INSERT INTO player_card(player_tag, card_name, level, found) VALUES(?, ?, ?, ?) ON CONFLICT(player_tag, card_name) DO UPDATE SET level=excluded.level, found=excluded.found",
                       (tag, card["name"], card["level"], is_found))

def get_last_battle_timestamp(cursor, player_tag: str) -> int | None:
    """Recupera il timestamp dell'ultima battaglia registrata per un giocatore."""
    cursor.execute("SELECT MAX(timestamp) FROM battles WHERE player_tag = ?", (player_tag,))
    row = cursor.fetchone()
    return row[0] if row and row[0] else None

def _generate_deck_hash(cards: list) -> str:
    """Genera un hash SHA256 per un mazzo di carte."""
    sorted_cards = sorted(cards, key=lambda x: x['name'])
    canonical_string = ",".join([
        f"{c['name']}:{c.get('level', '')}:{c['has_evolution']}:{c['has_hero']}"
        for c in sorted_cards
    ])
    return hashlib.sha256(canonical_string.encode()).hexdigest()

def _insert_deck(cursor, cards: list) -> str | None:
    """Inserisce un mazzo e le sue carte nel DB, se non presenti, e restituisce l'hash."""
    if not cards:
        return None
    
    deck_hash = _generate_deck_hash(cards)
    cursor.execute("INSERT OR IGNORE INTO decks (deck_hash) VALUES (?)", (deck_hash,))
    
    for card in cards:
        cursor.execute("""
            INSERT OR IGNORE INTO deck_cards 
            (deck_hash, card_name, card_level, has_evolution, has_hero) 
            VALUES (?, ?, ?, ?, ?)
        """, (deck_hash, card['name'], card['level'], card['has_evolution'], card['has_hero']))
    
    return deck_hash

def insert_battle_and_decks(cursor, battle_data: dict, player_deck: list, opponent_deck: list | None):
    """
    Inserisce i mazzi e la battaglia nel database.
    """
    player_deck_id = _insert_deck(cursor, player_deck)
    opponent_deck_id = _insert_deck(cursor, opponent_deck) if opponent_deck else None

    cursor.execute("""
        INSERT OR IGNORE INTO battles (
            battle_id, battle_type, game_mode, timestamp, player_tag, player_deck_id,
            opponent_tag, opponent_deck_id, player_crowns, opponent_crowns, win,
            trophy_change, elixir_leaked_player, elixir_leaked_opponent, level_diff
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        battle_data["battle_id"], battle_data["battle_type"], battle_data["game_mode"],
        battle_data["timestamp"], battle_data["player_tag"], player_deck_id,
        battle_data["opponent_tag"], opponent_deck_id, battle_data["player_crowns"],
        battle_data["opponent_crowns"], battle_data["win"], battle_data["trophy_change"],
        battle_data["elixir_leaked_player"], battle_data["elixir_leaked_opponent"],
        battle_data["level_diff"]
    ))