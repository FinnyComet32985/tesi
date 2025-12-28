import sys
import os
import pandas as pd
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '../utils'))

from connection import open_connection, close_connection




def main():
    connection, cursor = open_connection("db/clash.db")

    query = """
        SELECT battle_id, battle_type, game_mode, timestamp, win, level_diff, matchup_win_rate
        FROM battles
        WHERE player_tag = ? AND game_mode not like '%Draft%' and battle_type not like 'riverRace%'
        ORDER BY timestamp ASC;
    """

    PLAYER_TAG = "20GLGG298R"

    cursor.execute(query, (PLAYER_TAG,))
    battles = cursor.fetchall()

    print_battlelog(battles)



    close_connection(connection)


def format_duration(seconds):
    """Converte i secondi in una stringa leggibile (giorni, ore, minuti)."""
    seconds = int(seconds)
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    parts = []
    if days > 0:
        parts.append(f"{days} giorni")
    if hours > 0:
        parts.append(f"{hours} ore")
    if minutes > 0:
        parts.append(f"{minutes} minuti")
    
    return ", ".join(parts) if parts else "< 1 minuto"

def print_battlelog(battles):
    # Indice del timestamp e della win nella query
    TIMESTAMP_IDX = 3
    WIN_IDX = 4
    
    # Soglie in secondi
    SHORT_STOP = 20 * 60      # 20 minuti
    LONG_STOP = 2 * 60 * 60   # 2 ore
    QUIT = 20 * 60 * 60       # 20 ore

    for i in range(1, len(battles)):
        readable_date = datetime.fromtimestamp(battles[i][TIMESTAMP_IDX]).strftime('%Y-%m-%d %H:%M:%S')
        
        matchup = battles[i-1][6]
        matchup_str = f"{matchup * 100:.1f}" if matchup is not None else "N/A"
        print(f"id: {battles[i-1][0]}, gamemode: {battles[i-1][2]}, win: {battles[i-1][4]}, diff: {battles[i-1][5]}, matchup: {matchup_str}, timestamp: {readable_date}")
        

        time_passed = battles[i][TIMESTAMP_IDX] - battles[i-1][TIMESTAMP_IDX]

        if time_passed >= SHORT_STOP:
            readable_time = format_duration(time_passed)
            # 1. Determina il tipo di stop
            if time_passed >= QUIT:
                stop_type = 'Quit'
            elif time_passed >= LONG_STOP:
                stop_type = 'Long'
            else:
                stop_type = 'Short'

            # 2. Recupera le ultime 3 partite (o meno) appartenenti alla STESSA sessione
            # L'ultima partita giocata è sicuramente battles[i-1]
            session_battles = [battles[i-1]]
            
            # Controlliamo indietro: i-2
            if i - 2 >= 0:
                gap_prev = battles[i-1][TIMESTAMP_IDX] - battles[i-2][TIMESTAMP_IDX]
                if gap_prev < SHORT_STOP:
                    session_battles.insert(0, battles[i-2]) # Aggiungi in testa per mantenere ordine cronologico
                    
                    # Controlliamo indietro: i-3 (solo se i-2 era valido)
                    if i - 3 >= 0:
                        gap_prev_2 = battles[i-2][TIMESTAMP_IDX] - battles[i-3][TIMESTAMP_IDX]
                        if gap_prev_2 < SHORT_STOP:
                            session_battles.insert(0, battles[i-3])

            # 3. Crea la stringa del pattern (es. "WLL")
            results = ["W" if b[WIN_IDX] else "L" for b in session_battles]
            results_str = "-".join(results)

            print("\n" + "="*40 + "\n")

            if stop_type == 'Quit':
                print(f'Quit: {readable_time} (Ultime partite: {results_str})')
            elif stop_type == 'Long':
                print(f'Long stop: {readable_time} (Ultime partite: {results_str})')
            else:
                print(f'Short stop: {readable_time} (Ultime partite: {results_str})')

            print("\n" + "="*40 + "\n")

if __name__ == "__main__":
    main()
