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

def fetch_matchup(player_deck: list, opponent_deck: list, force_equal_levels: bool = False) -> dict | None:
    """
    Esegue una richiesta POST a deckai.app per ottenere il win rate di un matchup.
    Se force_equal_levels è True, imposta tutti i livelli a 11 per un confronto ad armi pari.
    """
    url = "https://deckai.app/api/main/get-matchup"
    
    p_deck = [{"name": c["name"], "level": 11 if force_equal_levels else c["level"]} for c in player_deck]
    o_deck = [{"name": c["name"], "level": 11 if force_equal_levels else c["level"]} for c in opponent_deck]

    # Prepara i dati nel formato richiesto dall'API
    payload = [
        p_deck,
        o_deck
    ]

    try:
        response = requests.post(url, json=payload, headers=HEADERS)

        response.raise_for_status()
        return response.json()  # Restituisce {"winRate": 0.535, "probabilities": null, ...}
    except requests.RequestException as e:
        logging.error(f"Errore durante la richiesta di matchup a {url}: {e}")
        logging.error(f"Payload inviato: {payload}")
        return None