from bs4 import BeautifulSoup
from utils.tools import parse_duration_to_seconds
import logging

def parse_player_data(soup: BeautifulSoup) -> tuple | None:
    """Estrae le statistiche principali del giocatore dalla pagina del profilo."""
    try:
        name_tag = soup.select_one(".p_head_item h1")
        player_name = name_tag.get_text(strip=True) if name_tag else None

        league_blocks = soup.select(".league_info_container")

        trophies = None
        rank = None
        arena = None
        ranked_trophies = None

        # 1. Parsing Trofei Standard e Arena (Header)
        # Cerchiamo il blocco che contiene specificamente l'icona del trofeo
        for block in league_blocks:
            if block.select_one(".item_icon.trophy"):
                items = block.select(".item")
                if len(items) >= 1:
                    text = items[0].get_text(strip=True)
                    try:
                        # Es: "11068 / 11309 PB" -> prende 11068
                        trophies = int(text.split("/")[0].strip().replace(",", ""))
                    except (ValueError, IndexError):
                        pass
                if len(items) >= 2:
                    arena = items[1].get_text(strip=True)
                break # Trovato il blocco trofei, usciamo dal loop

        # 2. Parsing Ranked Stats (Tabella)
        # Cerchiamo la sezione "Ranked Stats" e poi la tabella successiva
        ranked_header = soup.find("h3", string=lambda t: t and "Ranked Stats" in t)
        if ranked_header:
            table = ranked_header.find_next("table")
            if table:
                rows = table.select("tr")
                in_current_season = False
                
                for row in rows:
                    # Controllo intestazioni di sezione (Best Season, Current Season, etc.)
                    header_cell = row.select_one("h5")
                    if header_cell:
                        if "Current Season" in header_cell.get_text(strip=True):
                            in_current_season = True
                            continue
                        elif in_current_season:
                            break # Usciamo se incontriamo un'altra intestazione (es. Last Season)
                    
                    if in_current_season:
                        cols = row.select("td")
                        if len(cols) == 2:
                            label = cols[0].get_text(strip=True).lower()
                            val_text = cols[1].get_text(strip=True)
                            
                            if label == "league":
                                rank = val_text
                            elif label == "rank" and "unranked" not in val_text.lower():
                                # Se c'è un rank specifico (es. Ultimate Champion), sovrascrive la lega
                                rank = val_text
                            elif label in ["trophies", "ratings"]:
                                try:
                                    # Es: "1625 <img...>" -> prende 1625
                                    ranked_trophies = int(val_text.split()[0].replace(",", ""))
                                except (ValueError, IndexError):
                                    pass

        clan_tag = soup.select_one(".player_aux_info .ui.header.item")
        clan_name = clan_tag.get_text(strip=True) if clan_tag else 'None'
        if clan_name.lower() == "not in clan":
            clan_name = 'None'

        # Inizializzazione delle variabili per evitare UnboundLocalError
        account_age_seconds, games_per_day = None, None
        wins, losses, total_games, three_crown_wins, time_spent_seconds = None, None, None, None, None

        rows = soup.select("table tbody tr")
        for row in rows:
            tds = row.select("td")
            if len(tds) != 2:
                continue
            label = tds[0].get_text(strip=True).lower()
            value = tds[1].get_text(strip=True)

            if label == "account age":
                account_age_seconds = parse_duration_to_seconds(value)
            elif label == "games per day":
                try:
                    games_per_day = float(value)
                except (ValueError, TypeError):
                    games_per_day = None
            elif label == "total":
                time_spent_seconds = parse_duration_to_seconds(value)

        rows_h5 = soup.select("h5.ui.header")
        for h in rows_h5:
            label = h.get_text(strip=True).lower()
            row = h.find_parent("tr")
            if not row: 
                continue
            value_td = row.select_one("td.right.aligned")
            if not value_td: 
                continue
            value = value_td.get_text(strip=True).replace(",", "")

            if label == "wins":
                wins = int(value)
            elif label == "losses":
                losses = int(value)

        stat_rows = soup.select("table tbody tr")
        for row in stat_rows:
            label_td = row.select_one("td h5")
            value_td = row.select_one("td.right.aligned")
            if not label_td or not value_td: 
                continue
            label = label_td.get_text(strip=True).lower()
            value = value_td.get_text(strip=True).replace(",", "")

            if label == "total games":
                total_games = int(value)
            elif label == "three crown wins":
                three_crown_wins = int(value)

        return (player_name, clan_name, trophies, arena, rank, ranked_trophies, wins, losses, three_crown_wins, total_games, account_age_seconds, time_spent_seconds, games_per_day)
    except (AttributeError, IndexError, ValueError) as e:
        print(f"Errore durante il parsing dei dati del giocatore: {e}")
        return None

def parse_player_cards(soup: BeautifulSoup) -> list:
    """Estrae i dati delle carte dalla pagina delle carte di un giocatore."""
    player_cards = []
    cards = soup.select("a.player_card_link.player_card_item")

    for card in cards:
        img = card.select_one("img.deck_card")
        name = img["alt"].strip() if img else None

        level = None
        level_tag = card.select_one(".player_cards__card_level")
        if level_tag:
            level_text = level_tag.get_text(strip=True)
            level = int(level_text.replace("Lvl", "").strip())
    
        player_cards.append({
            "name": name,
            "level": level,
            "found": True
        })
    return player_cards

def parse_towers_and_heroes(soup: BeautifulSoup) -> tuple[list, list]:
    """Estrae i dati di torri ed eroi dalla pagina del profilo."""
    towers = []
    heroes = []
    tower_cards = soup.select(".player_profile__tower_card_collection .player_card")

    for card in tower_cards:
        img = card.find("img", class_="mini_card")
        name = img["alt"].strip() if img else None
        if not name: 
            continue

        level_tag = card.find("div", class_="level")
        if level_tag: # È una torre
            level_text = level_tag.get_text(strip=True)
            level = 0 if "not_found" in card.get("class", []) or level_text == "_" else int(level_text)
            towers.append({"name": name, "level": level})
        else: # È un eroe
            found = "not_found" not in card.get("class", [])
            heroes.append({"name": name, "found": found})

    return towers, heroes

def parse_evolutions(soup: BeautifulSoup) -> list:
    """Estrae i dati delle evoluzioni sbloccate dalla pagina del profilo."""
    evolutions = []
    evo_cards = soup.select(".player_profile__evo_card_collection .player_card")

    for card in evo_cards:
        img = card.find("img", class_="mini_card")
        name = img["alt"].strip() if img else None
        if not name: 
            continue

        found = "not_found" not in card.get("class", [])
        evolutions.append({"name": name, "found": found})

    return evolutions

def parse_oldest_timestamp_from_page(soup: BeautifulSoup) -> int | None:
    """Estrae il timestamp della battaglia più vecchia presente nella pagina."""
    battles = soup.select("div.battle")
    if not battles:
        return None
    return int(float(battles[-1]["data-timestamp"]))

def parse_battle_data(div: BeautifulSoup, player_tag: str) -> dict:
    """Estrae i dati di una singola battaglia da un div."""
    battle_id = div["id"].replace("battle_", "")
    timestamp = int(float(div["data-timestamp"]))
    battle_type = div.get("data-battle-type")

    gm = div.select_one(".game_mode_header")
    game_mode = gm.get_text(strip=True) if gm else None

    ribbon = div.select_one(".win_loss .label")
    win = 1 if ribbon and "Victory" in ribbon.get_text() else 0

    result = div.select_one(".result_header")
    player_crowns, opponent_crowns = None, None
    if result:
        nums = result.get_text(strip=True).replace(" ", "").split("-")
        player_crowns = int(nums[0])
        opponent_crowns = int(nums[1])

    trophy_change = None
    labels = div.select(".trophy_container .ui.basic.label")
    if labels:
        tc_text = labels[0].contents[0].strip().replace("+", "")
        try:
            trophy_change = int(tc_text)
        except ValueError:
            trophy_change = None

    opponent_link = div.select_one(".team-segment:last-child a.player_name_header")
    opponent_tag = None
    if opponent_link and '/player/' in opponent_link.get("href", ""):
        opponent_tag = opponent_link["href"].split("/player/")[-1].split('/')[0]

    elixir_leaked_player, elixir_leaked_opponent = None, None
    for stat in div.select(".battle_stats .stats .item"):
        label_tag = stat.select_one(".name")
        value_tag = stat.select_one(".value")
        if not label_tag or not value_tag: 
            continue
        label = label_tag.get_text(strip=True).lower()
        val = value_tag.get_text(strip=True)
    
        if label == "elixir leaked":
            if elixir_leaked_player is None:
                elixir_leaked_player = float(val.removeprefix("Elixir Leaked"))
            else:
                elixir_leaked_opponent = float(val.removeprefix("Elixir Leaked"))

    level_diff = None
    lvl = div.select_one(".battle_level_diff")
    if lvl and "Δ Lvl:" in lvl.get_text():
        level_diff_text = lvl.get_text(strip=True).replace("Δ Lvl:", "").strip()
        try:
            level_diff = float(level_diff_text)
        except ValueError:
            level_diff = None

    return {
        "battle_id": battle_id, "battle_type": battle_type, "game_mode": game_mode,
        "timestamp": timestamp, "player_tag": player_tag, "opponent_tag": opponent_tag,
        "player_crowns": player_crowns, "opponent_crowns": opponent_crowns, "win": win,
        "trophy_change": trophy_change, "elixir_leaked_player": elixir_leaked_player,
        "elixir_leaked_opponent": elixir_leaked_opponent, "level_diff": level_diff
    }

def parse_deck_from_battle(div: BeautifulSoup, is_opponent: bool = False) -> list | None:
    """Estrae le carte di un mazzo da un div di battaglia."""
    segments = div.select(".team-segment")
    if not segments:
        return None
    
    segment = segments[-1] if is_opponent else segments[0]
    parsed_cards = []

    # Parsing delle 8 carte del mazzo
    deck_containers = segment.select(".deck_card__four_wide")
    for card_container in deck_containers:
        card_img = card_container.select_one("img.deck_card")
        if not card_img: 
            continue

        level = None
        level_tag = card_container.select_one(".card-level")
        if level_tag:
            level_text = level_tag.get_text(strip=True).replace("Lvl", "").strip()
            if level_text.isdigit():
                level = int(level_text)

        card_key = card_img.get("data-card-key", "")
        parsed_cards.append({
            "name": card_img.get("alt"),
            "level": level,
            "has_evolution": 1 if "-ev" in card_key else 0,
            "has_hero": 1 if "-hero" in card_key else 0
        })

    # Parsing della carta torre
    tower_container = segment.select_one(".deck_tower_card__container")
    if tower_container:
        tower_img = tower_container.select_one("img.deck_card")
        if tower_img:
            level = None
            # Il livello è nel secondo div dentro al div con classe "level"
            level_divs = tower_container.select(".level div")
            if len(level_divs) > 1:
                level_text = level_divs[1].get_text(strip=True).replace("Lvl", "").strip()
                if level_text.isdigit():
                    level = int(level_text)
            
            parsed_cards.append({"name": tower_img.get("alt"), "level": level, "has_evolution": 0, "has_hero": 0})

    return parsed_cards if parsed_cards else None

def parse_all_deck_stats_from_page(soup: BeautifulSoup) -> dict[str, dict]:
    """
    Estrae le statistiche per tutti i mazzi presenti nella pagina /decks di un giocatore.

    Args:
        soup: L'oggetto BeautifulSoup della pagina /player/{tag}/decks.

    Returns:
        Un dizionario dove la chiave è l'archetype_hash del mazzo e il valore
        è un dizionario con le sue statistiche (battles, wins).
    """
    from db_manager import _generate_deck_hashes # Importazione locale per evitare dipendenza circolare
    
    all_deck_stats = {}
    deck_segments = soup.select("div.deck_segment")

    for segment in deck_segments:
        try:
            # 1. Estrai le carte per calcolare l'archetype_hash
            card_elements = segment.select("img.deck_card")
            cards_for_hash = []
            for img in card_elements:
                card_key = img.get("data-card-key", "")
                cards_for_hash.append({
                    "name": img.get("alt"),
                    "has_evolution": 1 if "-ev" in card_key else 0,
                    "has_hero": 1 if "-hero" in card_key else 0 # Anche se non usato, per coerenza
                })
            
            if not cards_for_hash:
                continue

            _, archetype_hash = _generate_deck_hashes(cards_for_hash)

            # 2. Estrai le statistiche di gioco
            player_stats_row = segment.find('td', string='Player')
            
            if not player_stats_row:
                continue
            row_cells = player_stats_row.find_parent('tr').find_all('td')
            
            battles = int(row_cells[1].get_text(strip=True))
            win_rate = float(row_cells[2].get_text(strip=True).replace('%', ''))
            wins = round(battles * (win_rate / 100))

            all_deck_stats[archetype_hash] = {"battles": battles, "wins": int(wins)}
        except (AttributeError, IndexError, ValueError, TypeError) as e:
            logging.warning(f"Impossibile parsare le statistiche per un mazzo: {e}")
            continue

    return all_deck_stats