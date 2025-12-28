import sys
import os
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '../utils'))

from connection import open_connection, close_connection




def main():
    connection, cursor = open_connection("db/clash.db")

    query = """
        SELECT battle_id, battle_type, game_mode, timestamp, win, level_diff, matchup_win_rate
        FROM battles
        WHERE player_tag = ? AND game_mode != 'Draft Battle' and battle_type not like 'riverRace%'
        ORDER BY timestamp ASC;
    """

    PLAYER_TAG = "20GLGG298R"

    cursor.execute(query, (PLAYER_TAG,))
    battles = cursor.fetchall()

    categorize_player(battles)



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


def print_contingency_table(data_for_df):
    """Stampa la tabella di contingenza per l'analisi degli stop."""
    if data_for_df:
        df = pd.DataFrame(data_for_df)
        
        # Crea la tabella di contingenza
        contingency_table = pd.crosstab(df['Pattern'], df['StopType'])
        
        # Riordina le colonne per leggibilità (se presenti)
        desired_order = ['Short', 'Long', 'Quit']
        existing_cols = [c for c in desired_order if c in contingency_table.columns]
        contingency_table = contingency_table[existing_cols]

        print("\n" + "="*40 + "\n")
        print("Analisi Stop dopo Sessione di Gioco:")
        print(contingency_table)
        print("\n" + "="*40 + "\n")
    else:
        print("Nessuna sessione trovata con i criteri attuali.")

def categorize_player(battles):
    # Indice del timestamp e della win nella query
    TIMESTAMP_IDX = 3
    WIN_IDX = 4
    
    # Soglie in secondi
    SHORT_STOP = 20 * 60      # 20 minuti
    LONG_STOP = 2 * 60 * 60   # 2 ore
    QUIT = 20 * 60 * 60       # 20 ore
    
    data_for_df = []

    for i in range(1, len(battles)):
        

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
            pattern = "".join(results)
            results_str = "-".join(results)

            if stop_type == 'Quit':
                print(f'Quit: {readable_time} (Ultime partite: {results_str})')
            elif stop_type == 'Long':
                print(f'Long stop: {readable_time} (Ultime partite: {results_str})')
            else:
                print(f'Short stop: {readable_time} (Ultime partite: {results_str})')
            
            data_for_df.append({'Pattern': pattern, 'StopType': stop_type})

    print_contingency_table(data_for_df)

if __name__ == "__main__":
    main()
