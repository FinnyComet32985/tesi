from datetime import datetime, timezone
import re

def parse_duration_to_seconds(text):
    """
    Converte '1w 3d 5h', '9y 36w 5d', '10h 21m' in secondi
    """
    if not text:
        return None

    units = {
        "y": 365 * 24 * 3600,
        "w": 7 * 24 * 3600,
        "d": 24 * 3600,
        "h": 3600,
        "m": 60
    }

    total = 0
    matches = re.findall(r"(\d+)\s*([ywdhm])", text)

    for value, unit in matches:
        total += int(value) * units[unit]

    return total


def parse_battle_datetime(battle):
    time_div = battle.select_one(".battle-timestamp-popup")
    if not time_div:
        return None, None

    raw = time_div.get("data-content")  # "2025-12-12 22:08:43 UTC"
    dt = datetime.strptime(raw, "%Y-%m-%d %H:%M:%S UTC")
    dt = dt.replace(tzinfo=timezone.utc)

    return dt.isoformat(), int(dt.timestamp())
