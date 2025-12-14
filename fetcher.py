from math import exp
import sqlite3
import requests
import time
from datetime import datetime
import os
from bs4 import BeautifulSoup
from utils import connection
from utils.tools import parse_duration_to_seconds
from utils.connection import open_connection



HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# set the BASE URL for the http request
BASE_URL = "https://royaleapi.com"

DB_PATH = "db/clash.db"

CONNECTION = None
CURSOR = None



def load_tags():
    try:
        CURSOR.execute("SELECT player_tag FROM players")
        rows = CURSOR.fetchall()

        return [row[0] for row in rows]
    except Exception as e:
        print(f"Error Message: {e}")
        CONNECTION.close()
        return None

def fetch_player(tag: str):
    print(f"[+] Fetch player data for {tag}")
    url = f"{BASE_URL}/player/{tag}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")

        player_data = get_player_data(soup)

        CURSOR.execute("SELECT player_name, clan_name, trophies, arena, rank, wins, losses, three_crown_wins, total_games, account_age_seconds, time_spent_seconds, games_per_day FROM players WHERE player_tag = ?", (tag,))
        row = CURSOR.fetchone()

        column =  ['player_name', 'clan_name', 'trophies', 'arena', 'rank', 'wins', 'losses', 'three_crown_wins', 'total_games', 'account_age_seconds', 'time_spent_seconds', 'games_per_day']
        
        if row is not None:
            for i in range(len(row)):
                if row[i] != player_data[i]: 
                    CURSOR.execute(f"UPDATE players SET {column[i]} = ? WHERE player_tag = ?", (player_data[i], tag))

        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        CURSOR.execute("UPDATE players SET last_updated = ? WHERE player_tag = ?", (current_time, tag))

        CONNECTION.commit()     


        towers, heroes = parse_towers_and_heroes(soup)
        evolutions = parse_evolutions(soup)

        for tower in towers:
            CURSOR.execute("INSERT OR REPLACE INTO player_card(player_tag, card_name, level, found, has_evolution, has_hero) VALUES(?, ?, ?, ?, 0, 0)", (tag, tower["name"], tower["level"], 1 if tower["level"] > 0 else 0))
        
        CONNECTION.commit()  
        


        for hero in heroes:
            CURSOR.execute("SELECT * FROM player_card WHERE player_tag = ? AND card_name = ?", (tag, hero["name"]))
            row = CURSOR.fetchone()

            if row is None:
                CURSOR.execute("INSERT INTO player_card(player_tag, card_name, has_hero) VALUES(?, ?, ?)", (tag, hero["name"], 1 if hero["found"] else 0))
            else:
                CURSOR.execute("UPDATE player_card SET has_hero = ? WHERE player_tag = ? AND card_name = ?", (1 if hero["found"] else 0, tag, hero["name"]))

        CONNECTION.commit()

        for evolution in evolutions:
            CURSOR.execute("SELECT * FROM player_card WHERE player_tag = ? AND card_name = ?", (tag, evolution["name"]))
            row = CURSOR.fetchone()

            if row is None:
                CURSOR.execute("INSERT INTO player_card(player_tag, card_name, has_evolution) VALUES(?, ?, ?)", (tag, evolution["name"], 1 if evolution["found"] else 0))
            else:
                CURSOR.execute("UPDATE player_card SET has_evolution = ? WHERE player_tag = ? AND card_name = ?", (1 if evolution["found"] else 0, tag, evolution["name"]))

        CONNECTION.commit()

        cards = get_cards(tag)

        for card in cards:
            CURSOR.execute("SELECT * FROM player_card WHERE player_tag = ? AND card_name = ?", (tag, card["name"]))
            row = CURSOR.fetchone()
            if row is None:
                CURSOR.execute("INSERT INTO player_card(player_tag, card_name, level, found, has_evolution, has_hero) VALUES(?, ?, ?, ?, 0, 0)", (tag, card["name"], card["level"], 1 if card["level"] > 0 else 0))
            else:
                CURSOR.execute("UPDATE player_card SET level = ?, found = ? WHERE player_tag = ? AND card_name = ?", (card["level"], card["found"], tag, card["name"]))

        CONNECTION.commit()
        
    else:
        print(f"Error Code: {response.status_code}")

def get_player_data(soup):
    name_tag = soup.select_one(".p_head_item h1")
    player_name = name_tag.get_text(strip=True) if name_tag else None

    league_blocks = soup.select(".league_info_container")

    trophies = None
    rank = None

    if len(league_blocks) >= 1:
        items = league_blocks[0].select(".item")

        if len(items) >= 1:
            text = items[0].get_text(strip=True)
            trophies = int(text.split("/")[0].strip())

        if len(items) >= 2:
            arena = items[1].get_text(strip=True)


    if len(league_blocks) >= 2:
        items = league_blocks[1].select(".item")

        if len(items) >= 2:
            rank = items[1].get_text(strip=True)

    clan_tag = soup.select_one(".player_aux_info .ui.header.item")

    if not clan_tag:
        clan_tag = None

    clan_name = clan_tag.get_text(strip=True)

    if clan_name.lower() == "not in clan":
        clan_name = 'None'


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
            except ValueError:
                pass

    rows = soup.select("h5.ui.header")

    for h in rows:
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

    # Totali
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

    # Tempo totale
    for row in stat_rows:
        tds = row.select("td")
        if len(tds) != 2:
            continue

        label = tds[0].get_text(strip=True).lower()
        if label == "total":
            duration_text = tds[1].get_text(strip=True)
            time_spent_seconds = parse_duration_to_seconds(duration_text)

    return player_name, clan_name, trophies, arena, rank, wins, losses, three_crown_wins, total_games, account_age_seconds, time_spent_seconds, games_per_day


def get_cards(tag: str):
    print(f"[+] Fetch cards for {tag}")
    url = f"{BASE_URL}/player/{tag}/cards"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        player_cards = []


        cards = soup.select("a.player_card_link.player_card_item")

        for card in cards:
            # Nome
            img = card.select_one("img.deck_card")
            name = img["alt"].strip() if img else None

            # Livello
            level_tag = card.select_one(".player_cards__card_level")
            level = None

            if level_tag:
                # "Lvl 16" → 16
                level_text = level_tag.get_text(strip=True)
                level = int(level_text.replace("Lvl", "").strip())
        
            player_cards.append({
                "name": name,
                "level": level,
                "found": True
            })
        return(player_cards)
    else:
        print(f"Error Code: {response.status_code}")
    

def parse_towers_and_heroes(soup):
    towers = []
    heroes = []

    tower_cards = soup.select(".player_profile__tower_card_collection .player_card")

    for card in tower_cards:
        img = card.find("img", class_="mini_card")
        name = img["alt"].strip() if img else None

        # Controlliamo se è una torre (ha il div level)
        level_tag = card.find("div", class_="level")

        if level_tag:
            # Torre
            level_text = level_tag.get_text(strip=True)

            if "not_found" in card.get("class", []) or level_text == "_":
                level = 0
            else:
                level = int(level_text)

            towers.append({
                "name": name,
                "level": level
            })

        else:
            # Eroe
            found = "not_found" not in card.get("class", [])
            heroes.append({
                "name": name,
                "found": found
            })

    return towers, heroes

def parse_evolutions(soup):
    evolutions = []

    evo_cards = soup.select(".player_profile__evo_card_collection .player_card")

    for card in evo_cards:
        img = card.find("img", class_="mini_card")
        name = img["alt"].strip() if img else None

        found = "not_found" not in card.get("class", [])

        evolutions.append({
            "name": name,
            "found": found
        })

    return evolutions



#* BATTAGLIE
def get_last_battle_timestamp(player_tag):
    CURSOR.execute("""
        SELECT MAX(battle_timestamp)
        FROM battles
        WHERE player_tag = ?
    """, (player_tag,))
    row = CURSOR.fetchone()
    return row[0] if row and row[0] else None

def fetch_page(url):
    time.sleep(0.5)  # rate limit fondamentale
    r = requests.get(url, headers=HEADERS)
    if r.status_code != 200:
        return None
    return BeautifulSoup(r.text, "html.parser")

def get_oldest_timestamp(soup):
    battles = soup.select("div.battle")
    if not battles:
        return None
    return int(float(battles[-1]["data-timestamp"]))

def parse_battle(div, player_tag):
    # ID e timestamp
    battle_id = div["id"].replace("battle_", "")
    timestamp = int(float(div["data-timestamp"]))

    battle_type = div.get("data-battle-type")

    # Game mode
    gm = div.select_one(".game_mode_header")
    game_mode = gm.get_text(strip=True) if gm else None

    # Win / Loss
    ribbon = div.select_one(".win_loss .label")
    win = 1 if ribbon and "Victory" in ribbon.get_text() else 0

    # Crowns
    result = div.select_one(".result_header")
    if result:
        nums = result.get_text(strip=True).replace(" ", "").split("-")
        player_crowns = int(nums[0])
        opponent_crowns = int(nums[1])
    else:
        player_crowns = opponent_crowns = None

    # Trophy change
    trophy_change = None
    labels = div.select(".trophy_container .ui.basic.label")
    if labels:
        tc_text = labels[0].contents[0].strip().replace("+", "")
        trophy_change = int(tc_text)

    # Opponent tag
    opponent_link = div.select_one(
        ".team-segment:last-child a.player_name_header"
    )
    opponent_tag = None
    if opponent_link:
        href = opponent_link.get("href", "")
        opponent_tag = href.split("/player/")[-1].replace("/battles", "")

    # Stats
    elixir_leaked_player = elixir_leaked_opponent = None

    for stat in div.select(".battle_stats .stats .item"):
        label_tag = stat.select_one(".name")
        value_tag = stat.select_one(".value")
        if not label_tag or not value_tag:
            continue
        label = label_tag.get_text(strip=True).lower()
        val = value_tag.get_text(strip=True)
    
        if label == "elixir leaked":
        # Controllo posizione: se è la prima, player; se seconda, opponent
            if elixir_leaked_player is None:
                elixir_leaked_player = float(val.removeprefix("Elixir Leaked"))
            else:
                elixir_leaked_opponent = float(val.removeprefix("Elixir Leaked"))


    # Level diff
    level_diff = None
    lvl = div.select_one(".battle_level_diff")
    if lvl:
        level_diff = float(
            lvl.get_text(strip=True)
               .replace("Δ Lvl:", "")
               .strip()
        )

    return {
        "battle_id": battle_id,
        "battle_type": battle_type,
        "game_mode": game_mode,
        "timestamp": timestamp,
        "battle_timestamp": timestamp,
        "player_tag": player_tag,
        "opponent_tag": opponent_tag,
        "player_crowns": player_crowns,
        "opponent_crowns": opponent_crowns,
        "win": win,
        "trophy_change": trophy_change,
        "elixir_leaked_player": elixir_leaked_player,
        "elixir_leaked_opponent": elixir_leaked_opponent,
        "level_diff": level_diff
    }


def insert_battle(b):
    CURSOR.execute("""
        INSERT OR IGNORE INTO battles (
            battle_id,
            battle_type,
            game_mode,
            timestamp,
            player_tag,
            opponent_tag,
            player_crowns,
            opponent_crowns,
            win,
            trophy_change,
            elixir_leaked_player,
            elixir_leaked_opponent,
            level_diff,
            battle_timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        b["battle_id"],
        b["battle_type"],
        b["game_mode"],
        b["timestamp"],
        b["player_tag"],
        b["opponent_tag"],
        b["player_crowns"],
        b["opponent_crowns"],
        b["win"],
        b["trophy_change"],
        b["elixir_leaked_player"],
        b["elixir_leaked_opponent"],
        b["level_diff"],
        b["battle_timestamp"]
    ))


def collect_scroll(tag, last_db_ts):
    soup = fetch_page(f"{BASE_URL}/player/{tag}/battles")
    if not soup:
        return

    while True:
        battles = soup.select("div.battle")
        if not battles:
            break

        stop = False

        for div in battles:
            battle = parse_battle(div, tag)

            if last_db_ts and battle["battle_timestamp"] <= last_db_ts:
                stop = True
                break

            insert_battle(battle)
            # Aggiunto parsing del deck anche qui
            parse_and_insert_deck(div, battle["battle_id"], tag, is_opponent=False)
            if battle["opponent_tag"]:
                parse_and_insert_deck(div, battle["battle_id"], battle["opponent_tag"], is_opponent=True)

        CONNECTION.commit()

        if stop:
            return

        oldest = get_oldest_timestamp(soup)
        if not oldest:
            break

        soup = fetch_page(
            f"{BASE_URL}/player/{tag}/battles/scroll/{oldest}/type/all"
        )

def collect_history(tag, last_db_ts, start_ts):
    before = start_ts * 1000  # ms

    while True:
        soup = fetch_page(
            f"{BASE_URL}/player/{tag}/battles/history?before={before}&&"
        )
        if not soup:
            break

        battles = soup.select("div.battle")
        if not battles:
            break

        stop = False

        for div in battles:
            battle = parse_battle(div, tag)

            if last_db_ts and battle["battle_timestamp"] <= last_db_ts:
                stop = True
                break

            insert_battle(battle)
            parse_and_insert_deck(div, battle["battle_id"], tag, is_opponent=False)
            parse_and_insert_deck(div, battle["battle_id"], battle["opponent_tag"], is_opponent=True)

        CONNECTION.commit()

        if stop:
            return

        before = int(float(battles[-1]["data-timestamp"]) * 1000)

def fetch_all_battles(tag):
    print(f"[+] Fetch battles for {tag}")

    last_db_ts = get_last_battle_timestamp(tag)

    soup = fetch_page(f"{BASE_URL}/player/{tag}/battles")
    if not soup:
        return

    newest_ts = get_oldest_timestamp(soup)

    collect_scroll(tag, last_db_ts)

    if newest_ts:
        collect_history(tag, last_db_ts, newest_ts)
        

def parse_and_insert_deck(div, battle_id, player_tag, is_opponent=False):
    segments = div.select(".team-segment")
    if not segments:
        return
    
    if is_opponent:
        segment = segments[-1]
    else:
        segment = segments[0]

    # Seleziona i contenitori delle carte per trovare più facilmente il livello associato
    deck_containers = segment.select(".deck_card__four_wide")
    if not deck_containers: # Fallback per altre strutture
        deck_containers = segment.select(".deck_card")

    for card_container in deck_containers:
        card_img = card_container.select_one("img.deck_card")
        if not card_img:
            continue

        name = card_img.get("alt")
        card_key = card_img.get("data-card-key", "")

        has_evolution = 1 if "-ev" in card_key else 0
        has_hero = 1 if "-hero" in card_key else 0

        level_tag = card_container.select_one(".card-level")
        level = None
        if level_tag:
            level_text = level_tag.get_text(strip=True).replace("Lvl", "").strip()
            if level_text.isdigit():
                level = int(level_text)

        CURSOR.execute("""
            INSERT OR IGNORE INTO battle_decks (
                battle_id,
                player_tag,
                card_name,
                card_level,
                has_evolution,
                has_hero
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (battle_id, player_tag, name, level, has_evolution, has_hero))





def main_loop():
    global CONNECTION, CURSOR
    CONNECTION, CURSOR = open_connection(DB_PATH)

    tags = load_tags()

    for tag in tags:
        fetch_player(tag)
        fetch_all_battles(tag)

    CONNECTION.close()



if __name__ == "__main__":
    main_loop()
