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

def get_player_deck_hashes(cursor, player_tag: str) -> list:
    """Recupera tutti gli hash dei mazzi unici usati da un giocatore."""
    cursor.execute("SELECT DISTINCT player_deck_id FROM battles WHERE player_tag = ? AND player_deck_id IS NOT NULL", (player_tag,))
    rows = cursor.fetchall()
    return [row[0] for row in rows]

def get_card_keys_for_deck(cursor, deck_hash: str) -> list:
    """Recupera i nomi delle carte (con suffisso -ev1/-hero) per un dato deck_hash."""
    cursor.execute("SELECT card_name, has_evolution, has_hero FROM deck_cards WHERE deck_hash = ?", (deck_hash,))
    rows = cursor.fetchall()
    card_keys = []
    for name, has_evo, has_hero in rows:
        key = name.lower().replace(' ', '-')
        if has_evo:
            key += '-ev1'
        # Nota: l'HTML non sembra usare un suffisso per gli eroi nel deck identifier,
        # ma lo aggiungiamo per coerenza se dovesse servire.
        # if has_hero:
        #     key += '-hero'
        card_keys.append(key)
    return sorted(card_keys)

def update_player_deck_stats(cursor, player_tag: str, deck_hash: str, stats: dict):
    """Inserisce o aggiorna le statistiche di un mazzo per un giocatore."""
    confidence = stats['wins'] / stats['battles'] if stats['battles'] > 0 else 0
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("""
        INSERT INTO player_deck_stats (player_tag, deck_hash, battles_last_30d, wins_last_30d, confidence, last_updated) VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(player_tag, deck_hash) DO UPDATE SET battles_last_30d=excluded.battles_last_30d, wins_last_30d=excluded.wins_last_30d, confidence=excluded.confidence, last_updated=excluded.last_updated
    """, (player_tag, deck_hash, stats['battles'], stats['wins'], confidence, current_time))

def _generate_deck_hashes(cards: list) -> tuple[str, str]:
    """Genera due hash SHA256 per un mazzo: uno con livelli (deck_hash) e uno senza (archetype_hash)."""
    # Normalizza i nomi delle carte PRIMA di ordinarli per garantire consistenza.
    # La chiave di ordinamento è la forma normalizzata del nome.
    sorted_cards = sorted(cards, key=lambda c: c['name'].lower().replace(' ', '-'))
    
    # Hash con i livelli (per unicità della battaglia)
    level_dependent_string = ",".join([
        f"{c['name']}:{c.get('level', '')}:{c.get('has_evolution', 0)}:{c.get('has_hero', 0)}"
        for c in sorted_cards
    ])
    deck_hash = hashlib.sha256(level_dependent_string.encode()).hexdigest()

    # Hash senza i livelli (per l'archetipo)
    level_independent_string = ",".join([
        f"{c['name'].lower().replace(' ', '-')}:{c.get('has_evolution', 0)}:{c.get('has_hero', 0)}"
        for c in sorted_cards
    ])
    archetype_hash = hashlib.sha256(level_independent_string.encode()).hexdigest()

    return deck_hash, archetype_hash

def _insert_deck(cursor, cards: list) -> str | None:
    """Inserisce un mazzo e le sue carte nel DB, se non presenti, e restituisce il deck_hash (con livelli)."""
    if not cards:
        return None
    
    deck_hash, archetype_hash = _generate_deck_hashes(cards)
    cursor.execute("INSERT OR IGNORE INTO decks (deck_hash, archetype_hash) VALUES (?, ?)", (deck_hash, archetype_hash))
    
    for card in cards:
        cursor.execute("""
            INSERT OR IGNORE INTO deck_cards 
            (deck_hash, card_name, card_level, has_evolution, has_hero) 
            VALUES (?, ?, ?, ?, ?)
        """, (deck_hash, card['name'], card['level'], card['has_evolution'], card['has_hero']))
    
    return deck_hash

def insert_battle_and_decks(cursor, battle_data: dict, player_deck: list, opponent_deck: list | None, matchup_data: dict | None):
    """
    Inserisce i mazzi e la battaglia nel database.
    """
    player_deck_id = _insert_deck(cursor, player_deck)
    opponent_deck_id = _insert_deck(cursor, opponent_deck) if opponent_deck else None
    
    win_rate = matchup_data.get("winRate") if matchup_data else None
    probabilities = str(matchup_data.get("probabilities")) if matchup_data and matchup_data.get("probabilities") is not None else None

    cursor.execute("""
        INSERT OR IGNORE INTO battles (
            battle_id, battle_type, game_mode, timestamp, player_tag, player_deck_id,
            opponent_tag, opponent_deck_id, player_crowns, opponent_crowns, win,
            trophy_change, elixir_leaked_player, elixir_leaked_opponent, level_diff,
            matchup_win_rate, matchup_probabilities
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        battle_data["battle_id"], battle_data["battle_type"], battle_data["game_mode"],
        battle_data["timestamp"], battle_data["player_tag"], player_deck_id,
        battle_data["opponent_tag"], opponent_deck_id, battle_data["player_crowns"],
        battle_data["opponent_crowns"], battle_data["win"], battle_data["trophy_change"],
        battle_data["elixir_leaked_player"], battle_data["elixir_leaked_opponent"],
        battle_data["level_diff"], win_rate, probabilities
    ))