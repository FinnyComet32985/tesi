import sys
import os
from tkinter import N
import pandas as pd
import plotly.graph_objects as go
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
            SELECT battle_id, battle_type, game_mode, timestamp, win, level_diff, matchup_win_rate, trophy_change, opponent_tag, player_crowns, opponent_crowns
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
            print_battlelog(battles, trophy, tag, output_file=f, output_dir=output_dir)
            print(f"\nLog salvato in: {os.path.abspath(output_filename)}")

    close_connection(connection)



# --- NUOVA FUNZIONE 1: ANALISI DIFFERENZA MATCHUP ---
def analyze_matchup_diffs(battles, log_func):
    """Calcola e stampa la variazione del matchup rispetto alla partita precedente."""
    MATCHUP_IDX = 6
    log_func("\n--- ANALISI VARIAZIONE MATCHUP (Delta) ---")
    
    for i in range(1, len(battles)):
        m_curr = battles[i][MATCHUP_IDX]
        m_prev = battles[i-1][MATCHUP_IDX]
        
        if m_curr is not None and m_prev is not None:
            delta = (m_curr - m_prev) * 100
            trend = "📈 Migliorato" if delta > 0 else "📉 Peggiorato"
            log_func(f"Match {i}: {trend} di {abs(delta):.1f}% (da {m_prev*100:.1f}% a {m_curr*100:.1f}%)")

# --- NUOVA FUNZIONE 2: GRAFICO TEMPORALE MATCHUP ---
def plot_matchup_trend(battles, tag, output_dir, current_trophies):
    """Genera un grafico interattivo del matchup (HTML)."""
    GAME_MODE_IDX = 2
    TIMESTAMP_IDX = 3
    WIN_IDX = 4
    MATCHUP_IDX = 6
    TROPHY_CHANGE_IDX = 7
    OPPONENT_TAG_IDX = 8
    PLAYER_CROWNS_IDX = 9
    OPPONENT_CROWNS_IDX = 10
    
    # Soglie in secondi (coerenti con print_battlelog)
    SHORT_STOP = 2 * 60 * 60
    LONG_STOP = 10 * 60 * 60
    QUIT = 20 * 60 * 60

    # Calcolo storico trofei (copia logica da print_battlelog)
    trophies_history = [0] * len(battles)
    trophies_history[-1] = current_trophies

    for i in range(len(battles) - 1, 0, -1):
        change = battles[i][TROPHY_CHANGE_IDX]
        win = battles[i][WIN_IDX]
        if change is None: 
            change = 0
        if win == 0 and change > 0: 
            change = 0
        trophies_history[i-1] = trophies_history[i] - change

    # Filtriamo i dati validi
    data = []
    for i, b in enumerate(battles):
        if b[MATCHUP_IDX] is not None:
            # Dati per tooltip
            trophies_after = trophies_history[i]
            change = b[TROPHY_CHANGE_IDX] if b[TROPHY_CHANGE_IDX] is not None else 0
            if b[WIN_IDX] == 0 and change > 0: 
                change = 0
            trophies_before = trophies_after - change
            
            ladder_info = ""
            if b[GAME_MODE_IDX] == 'Ladder':
                ladder_info = f"Trofei: {trophies_before} -> {trophies_after} ({change:+})"
            
            p_crowns = b[PLAYER_CROWNS_IDX] if b[PLAYER_CROWNS_IDX] is not None else "?"
            o_crowns = b[OPPONENT_CROWNS_IDX] if b[OPPONENT_CROWNS_IDX] is not None else "?"
            crowns_res = f"{p_crowns}-{o_crowns}"

            data.append({
                'seq_id': i + 1,
                'timestamp': datetime.fromtimestamp(b[TIMESTAMP_IDX]),
                'timestamp_str': datetime.fromtimestamp(b[TIMESTAMP_IDX]).strftime('%Y-%m-%d %H:%M:%S'),
                'matchup': b[MATCHUP_IDX] * 100,
                'game_mode': b[GAME_MODE_IDX],
                'crowns_result': crowns_res,
                'opponent': b[OPPONENT_TAG_IDX] if b[OPPONENT_TAG_IDX] else "N/A",
                'ladder_info': ladder_info,
                'color': 'green' if b[WIN_IDX] else 'red'
            })

    if not data:
        return

    df = pd.DataFrame(data)

    fig = go.Figure()

    # 1. Linea di tendenza generale (Sfondo)
    fig.add_trace(go.Scatter(
        x=df['seq_id'],
        y=df['matchup'],
        mode='lines',
        name='Trend Generale',
        line=dict(color='lightgray', width=1),
        hoverinfo='skip'
    ))

    # 2. Punti raggruppati per Game Mode (per permettere filtro in legenda)
    modes = df['game_mode'].unique()
    for mode in modes:
        df_mode = df[df['game_mode'] == mode]
        
        fig.add_trace(go.Scatter(
            x=df_mode['seq_id'],
            y=df_mode['matchup'],
            mode='markers',
            name=mode,
            customdata=df_mode[['game_mode', 'crowns_result', 'opponent', 'ladder_info', 'timestamp_str']].values,
            hovertemplate=(
                "<b>Partita %{x}</b><br>" +
                "Matchup: %{y:.1f}%<br>" +
                "Modalità: %{customdata[0]}<br>" +
                "Risultato: %{customdata[1]}<br>" +
                "Avversario: %{customdata[2]}<br>" +
                "%{customdata[3]}<br>" +
                "Data: %{customdata[4]}<extra></extra>"
            ),
            marker=dict(size=8, color=df_mode['color'], line=dict(width=1, color='black'))
        ))

    # Preparazione dati per le linee di stop (Sessioni)
    # Usiamo tracce reali invece di add_vline per permettere il toggle dalla legenda
    stops_data = {
        'Quit (> 20h)': {'x': [], 'y': [], 'color': 'blue'},
        'Long Stop (> 10h)': {'x': [], 'y': [], 'color': 'purple'},
        'Short Stop (> 2h)': {'x': [], 'y': [], 'color': 'skyblue'}
    }

    for k in range(len(df) - 1):
        curr_row = df.iloc[k]
        next_row = df.iloc[k+1]
        
        t1 = curr_row['timestamp']
        t2 = next_row['timestamp']
        diff = (t2 - t1).total_seconds()
        
        cat = None
        if diff >= QUIT:
            cat = 'Quit (> 20h)'
        elif diff >= LONG_STOP:
            cat = 'Long Stop (> 10h)'
        elif diff >= SHORT_STOP:
            cat = 'Short Stop (> 2h)'
            
        if cat:
            x_pos = (curr_row['seq_id'] + next_row['seq_id']) / 2
            # Aggiungiamo coordinate per disegnare il segmento verticale (0-100%)
            stops_data[cat]['x'].extend([x_pos, x_pos, None])
            stops_data[cat]['y'].extend([0, 100, None])

    # Aggiunta delle tracce per gli stop
    for label, s_data in stops_data.items():
        if s_data['x']:
            fig.add_trace(go.Scatter(
                x=s_data['x'],
                y=s_data['y'],
                mode='lines',
                line=dict(color=s_data['color'], dash='dash', width=1),
                name=label,
                hoverinfo='skip'
            ))

    # Linea di equilibrio (50%)
    fig.add_hline(y=50, line_dash="dash", line_color="red", annotation_text="Equilibrio (50%)")

    fig.update_layout(
        title=f"Trend Matchup - Player: {tag}",
        xaxis_title="Sequenza Partite",
        yaxis_title="Matchup Win Rate (%)",
        template="plotly_white",
        hovermode="x unified"
    )

    # Salvataggio HTML
    graph_path = os.path.join(output_dir, f"matchup_graph_{tag}.html")
    fig.write_html(graph_path)
    print(f"Grafico salvato in: {graph_path}")


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

def print_battlelog(battles, thropy, tag, output_file=None, output_dir=None):
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
    
    analyze_matchup_diffs(battles, log)

    if output_dir:
        plot_matchup_trend(battles, tag, output_dir, thropy)

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