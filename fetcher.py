from ast import Pass
from encodings import undefined
from math import exp
import requests
import time
from datetime import datetime
import os
from bs4 import BeautifulSoup
import sqlite3



HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# set the BASE URL for the http request
BASE_URL = "https://royaleapi.com"

DB_PATH = "db/clash.db"

CONNECTION = None
CURSOR = None

def open_connection():
    global CONNECTION, CURSOR
    try: 
        CONNECTION = sqlite3.connect(DB_PATH)
        CURSOR = CONNECTION.cursor()
    except Exception as e:
        print(f"Error Message: {e}")
        return None

def close_connection():
    global CONNECTION
    CONNECTION.close()

def load_tags():
    try:
        CURSOR.execute("SELECT player_tag FROM players")
        rows = CURSOR.fetchall()

        return [row[0] for row in rows]
    except Exception as e:
        print(f"Error Message: {e}")
        close_connection()
        return None


#! ERRATO
def fetch_games(tag: str):
    url = f"{BASE_URL}/player/{tag}/battles"
    response = requests.get(url)

    if response.status_code == 200:
        return response
    else:
        print(f"Error Code: {response.status_code}")
        try:
            r = response.json()
        except Exception as e:
            print(f"Error Message: {e}")
            return None

        print(f"Error Reason: {r.get('reason')}")
        print(f"Error Message: {r.get('message')}")
        return None


def fetch_player(tag: str):
    url = f"{BASE_URL}/player/{tag}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")

        player_data = get_player_data(soup)

        CURSOR.execute("SELECT name, clan, trophies, arena, rank FROM players WHERE player_tag = ?", (tag,))
        row = CURSOR.fetchone()

        column =  ['name', 'clan', 'trophies', 'arena', 'rank']
        
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


        print(evolutions)
        for evolution in evolutions:
            CURSOR.execute("SELECT * FROM player_card WHERE player_tag = ? AND card_name = ?", (tag, evolution["name"]))
            row = CURSOR.fetchone()

            if row is None:
                CURSOR.execute("INSERT INTO player_card(player_tag, card_name, has_evolution) VALUES(?, ?, ?)", (tag, evolution["name"], 1 if evolution["found"] else 0))
            else:
                CURSOR.execute("UPDATE player_card SET has_evolution = ? WHERE player_tag = ? AND card_name = ?", (1 if evolution["found"] else 0, tag, evolution["name"]))

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

    return player_name, clan_name, trophies, arena, rank


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


def main_loop():
    open_connection()
    tags = load_tags()
    for tag in tags:
        fetch_player(tag)
    #     print(profile)
        # games = fetch_games(tag)
        # print(games)


if __name__ == "__main__":
    main_loop()
