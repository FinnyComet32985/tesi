import sys
import os
import pandas as pd
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '../utils'))

from connection import open_connection, close_connection


def load_tags(cursor) -> list:
    """Carica i TAG dei giocatori dal database."""
    try:
        cursor.execute("SELECT player_tag FROM players")
        rows = cursor.fetchall()
        return [row[0] for row in rows]
    except Exception as e:
        print(f"Errore durante il caricamento dei tag: {e}")
        return []

def main():
    connection, cursor = open_connection("db/clash.db")

    tags = load_tags(cursor)

    for tag in tags:
        query = """
            SELECT battle_id, battle_type, game_mode, timestamp, win, level_diff, matchup_win_rate, trophy_change
            FROM battles
            WHERE player_tag = ? -- AND game_mode not like '%Draft%' and battle_type not like 'riverRace%'
            ORDER BY timestamp ASC;
        """
        cursor.execute(query, (tag,))
        battles = cursor.fetchall()

        query = """
            SELECT trophies
            FROM players
            WHERE player_tag = ?
        """
        cursor.execute(query, (tag,))
        trophy = cursor.fetchone()[0]

        

        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs')
        os.makedirs(output_dir, exist_ok=True)
        output_filename = os.path.join(output_dir, f"battlelog_{tag}.txt")
        with open(output_filename, "w", encoding="utf-8") as f:
            print_battlelog(battles, trophy, output_file=f)
            print(f"\nLog salvato in: {os.path.abspath(output_filename)}")

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

def print_battlelog(battles, thropy, output_file=None):
    def log(msg):
        #print(msg)
        if output_file:
            output_file.write(msg + "\n")

    # Indice del timestamp e della win nella query
    TIMESTAMP_IDX = 3
    WIN_IDX = 4
    MATCHUP_IDX = 6
    TROPHY_CHANGE_IDX = 7
    
    # Soglie in secondi
    SHORT_STOP = 20 * 60      # 20 minuti
    LONG_STOP = 2 * 60 * 60   # 2 ore
    QUIT = 20 * 60 * 60       # 20 ore

    if not battles:
        log("Nessuna battaglia da mostrare.")
        return

    # trophies_history[i] = Trofei posseduti DOPO la battaglia i
    trophies_history = [0] * len(battles)
    trophies_history[-1] = thropy # L'ultimo valore è quello attuale (passato come argomento)

    # Iteriamo dall'ultima battaglia indietro fino alla seconda (indice 1)
    for i in range(len(battles) - 1, 0, -1):
        change = battles[i][TROPHY_CHANGE_IDX]
        win = battles[i][WIN_IDX]

        if change is None:
            change = 0
        
        # Fix per dati sporchi (Arena Gate): se sconfitta e change > 0, assumiamo 0
        if win == 0 and change > 0:
            change = 0
            
        # Trofei dopo la battaglia (i-1) = Trofei dopo (i) - Change(i)
        trophies_history[i-1] = trophies_history[i] - change

    # 2. Stampa Log
    for i in range(len(battles)):
        battle = battles[i]
        
        readable_date = datetime.fromtimestamp(battle[TIMESTAMP_IDX]).strftime('%Y-%m-%d %H:%M:%S')
        
        matchup = battle[MATCHUP_IDX]
        matchup_str = f"{matchup * 100:.1f}" if matchup is not None else "N/A"
        
        # Trofei posseduti dopo questa battaglia
        current_val = trophies_history[i]
        
        # Ricalcolo change sanificato per visualizzazione e calcolo 'before'
        change = battle[TROPHY_CHANGE_IDX]
        win = battle[WIN_IDX]
        if change is None: 
            change = 0
        if win == 0 and change > 0: 
            change = 0
        
        before_val = current_val - change
        change_str = f"{change:+}"
        
        log(f"id: {battle[0]}, gamemode: {battle[2]}, win: {battle[WIN_IDX]}, trophies: {before_val} -> {current_val} ({change_str}), leveldiff: {battle[5]}, matchup: {matchup_str}, timestamp: {readable_date}")

        # Gestione Stop/Sessioni (guardando alla PROSSIMA battaglia)
        if i < len(battles) - 1:
            next_battle = battles[i+1]
            time_passed = next_battle[TIMESTAMP_IDX] - battle[TIMESTAMP_IDX]

            if time_passed >= SHORT_STOP:
                readable_time = format_duration(time_passed)
                
                if time_passed >= QUIT:
                    stop_type = 'Quit'
                elif time_passed >= LONG_STOP:
                    stop_type = 'Long'
                else:
                    stop_type = 'Short'

                # Recupera contesto sessione (ultime 3 incluso questa)
                session_battles = [battle]
                # Guarda indietro per aggiungere contesto alla sessione appena conclusa
                if i - 1 >= 0:
                    gap_prev = battle[TIMESTAMP_IDX] - battles[i-1][TIMESTAMP_IDX]
                    if gap_prev < SHORT_STOP:
                        session_battles.insert(0, battles[i-1])
                        if i - 2 >= 0:
                            gap_prev_2 = battles[i-1][TIMESTAMP_IDX] - battles[i-2][TIMESTAMP_IDX]
                            if gap_prev_2 < SHORT_STOP:
                                session_battles.insert(0, battles[i-2])

                results = ["W" if b[WIN_IDX] else "L" for b in session_battles]
                results_str = "-".join(results)

                log("\n" + "="*40 + "\n")
                if stop_type == 'Quit':
                    log(f'Quit: {readable_time} (Ultime partite: {results_str})')
                elif stop_type == 'Long':
                    log(f'Long stop: {readable_time} (Ultime partite: {results_str})')
                else:
                    log(f'Short stop: {readable_time} (Ultime partite: {results_str})')
                log("\n" + "="*40 + "\n")

if __name__ == "__main__":
    main()
