import requests
import time
import logging
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
BASE_URL = "https://royaleapi.com"

def fetch_page(path: str) -> BeautifulSoup | None:
    """
    Esegue una richiesta GET a un dato percorso su royaleapi.com,
    gestisce un rate limit e restituisce un oggetto BeautifulSoup.
    """
    url = f"{BASE_URL}{path}"
    time.sleep(0.5)  # Rate limit fondamentale per non sovraccaricare il server

    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()  # Lancia un'eccezione per status code non 2xx
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        logging.error(f"Errore durante la richiesta a {url}: {e}")
        return None

def fetch_matchup(player_deck: list, opponent_deck: list) -> dict | None:
    """
    Esegue una richiesta POST a deckai.app per ottenere il win rate di un matchup.
    """
    url = "https://deckai.app/api/main/get-matchup"
    
    # Prepara i dati nel formato richiesto dall'API
    payload = [
        [{"name": card["name"], "level": card["level"]} for card in player_deck],
        [{"name": card["name"], "level": card["level"]} for card in opponent_deck]
    ]

    try:
        response = requests.post(url, json=payload, headers=HEADERS)

        response.raise_for_status()
        return response.json()  # Restituisce {"winRate": 0.535, "probabilities": null, ...}
    except requests.RequestException as e:
        logging.error(f"Errore durante la richiesta di matchup a {url}: {e}")
        return None