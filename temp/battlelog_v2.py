from datetime import datetime
import statistics 
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../utils'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../data'))

from connection import open_connection, close_connection
from classifier import get_player_profile

BATTLE_ID_IDX = 0
GAME_MODE_IDX = 2
TIMESTAMP_IDX = 3
WIN_IDX = 4
LEVEL_DIFF_IDX = 5
MATCHUP_IDX = 6
TROPHY_CHANGE_IDX = 7
OPPONENT_TAG_IDX = 8
PLAYER_CROWNS_IDX = 9
OPPONENT_CROWNS_IDX = 10
PLAYER_DECK_ID_IDX = 11
ARCHETYPE_ID_IDX = 12
    
# Soglie in secondi
SHORT_STOP = 20 * 60      # 20 minuti
LONG_STOP = 2 * 60 * 60   # 2 ore
QUIT = 20 * 60 * 60       # 20 ore


def define_trophies_history(battles, current_trophies):
    """
    Ricostruisce lo storico dei trofei per le battaglie Ladder.
    Restituisce una lista di dizionari con id, trofei prima, dopo e variazione.
    """
    # Filtra solo le battaglie Ladder
    ladder_battles = [b for b in battles if b[GAME_MODE_IDX] == 'Ladder']

    if not ladder_battles:
        return []

    # Inizializza la lista dei trofei DOPO ogni battaglia
    trophies_after_list = [0] * len(ladder_battles)
    trophies_after_list[-1] = current_trophies

    # Calcolo a ritroso
    for i in range(len(ladder_battles) - 1, 0, -1):
        battle = ladder_battles[i]
        change = battle[TROPHY_CHANGE_IDX]
        win = battle[WIN_IDX]

        if change is None:
            change = 0
        
        # Fix per dati sporchi (Arena Gate): se sconfitta e change > 0, assumiamo 0
        if win == 0 and change > 0:
            change = 0
        
        # Trofei dopo la battaglia precedente = Trofei dopo attuale - variazione attuale
        trophies_after_list[i-1] = trophies_after_list[i] - change

    history = []
    for i, battle in enumerate(ladder_battles):
        t_after = trophies_after_list[i]
        change = battle[TROPHY_CHANGE_IDX]
        win = battle[WIN_IDX]

        if change is None:
            change = 0
        if win == 0 and change > 0:
            change = 0

        history.append({
            'id': battle[BATTLE_ID_IDX],
            'trophies_after': t_after,
            'variation': change
        })

    return history

def define_sessions(battles, trophies_history, mode_filter='all'):
    if not battles:
        return []

    sessions = []
    current_session_battles = []

    # Helper per creare l'oggetto battaglia formattato
    def create_battle_dict(battle_row):
        b_id = battle_row[BATTLE_ID_IDX]
        b_dict = {
            'id': b_id,
            'game_mode': battle_row[GAME_MODE_IDX],
            'win': battle_row[WIN_IDX],
            'opponent': battle_row[OPPONENT_TAG_IDX],
            'opponent_crowns': battle_row[OPPONENT_CROWNS_IDX],
            'player_crowns': battle_row[PLAYER_CROWNS_IDX],
            'level_diff': battle_row[LEVEL_DIFF_IDX],
            'matchup': battle_row[MATCHUP_IDX] * 100 if battle_row[MATCHUP_IDX] is not None else None,
            'timestamp': datetime.fromtimestamp(battle_row[TIMESTAMP_IDX]).strftime('%Y-%m-%d %H:%M:%S'),
            'deck_id': battle_row[PLAYER_DECK_ID_IDX],
            'archetype_id': battle_row[ARCHETYPE_ID_IDX] if len(battle_row) > ARCHETYPE_ID_IDX else None
        }
        
        # Integrazione dati Ladder
        if b_dict['game_mode'] == 'Ladder':
            t_data = next((t for t in trophies_history if t['id'] == b_id), None)
            if t_data:
                b_dict.update({
                    'trophies_after': t_data['trophies_after'],
                    'trophies_before': t_data['trophies_after'] - t_data['variation'],
                    'variation': t_data['variation']
                })
        return b_dict

    # Gestione primo elemento
    if battles:
        current_session_battles.append(create_battle_dict(battles[0]))

    # Filtro preliminare delle battaglie in base al flag
    if mode_filter == 'Ladder':
        battles = [b for b in battles if b[GAME_MODE_IDX] == 'Ladder']
    elif mode_filter == 'Ranked':
        battles = [b for b in battles if b[GAME_MODE_IDX] == 'Ranked']
    elif mode_filter == 'Ladder_Ranked':
        battles = [b for b in battles if b[GAME_MODE_IDX] in ['Ladder', 'Ranked']]
    # Se 'all', nessuna modifica

    for i in range(1, len(battles)):
        time_diff = battles[i][TIMESTAMP_IDX] - battles[i-1][TIMESTAMP_IDX]
        battle_obj = create_battle_dict(battles[i])

        if time_diff < SHORT_STOP:
            current_session_battles.append(battle_obj)
        else:
            stop_type = 'Quit' if time_diff >= QUIT else ('Long' if time_diff >= LONG_STOP else 'Short')
            
            analysis_results = analyze_session(current_session_battles)
            
            sessions.append({
                'battles': current_session_battles,
                'stop_type': stop_type,
                'duration': format_duration(time_diff),
                'analysis': analysis_results
            })
            current_session_battles = [battle_obj]

    if current_session_battles:
        analysis_results = analyze_session(current_session_battles)
        sessions.append({
            'battles': current_session_battles,
            'stop_type': 'End',
            'duration': '',
            'analysis': analysis_results
        })

    return sessions

def analyze_session(battles):

    # Filtra battaglie con matchup valido per statistiche matchup
    valid_matchups = [b for b in battles if b['matchup'] is not None and (b['game_mode'] == 'Ladder' or b['game_mode'] == 'Ranked')] 
    
    # tot_battles, avg_matchup, avg_level_diff, n_extreme_matchup,  winrate,
    tot_battles = len(valid_matchups)
    avg_matchup = sum(b['matchup'] for b in valid_matchups) / len(valid_matchups) if valid_matchups else 0
    avg_level_diff = sum(b['level_diff'] for b in battles) / tot_battles if tot_battles > 0 else 0
    n_extreme_matchup = sum(1 for b in valid_matchups if b['matchup'] > 80 or b['matchup'] < 40)
    if tot_battles > 0:
        winrate = sum(1 for b in valid_matchups if b['win']) / tot_battles if tot_battles > 0 else 0
        wins = sum(1 for b in valid_matchups if b['win']) / tot_battles if tot_battles > 0 else 0
        loses = sum(1 for b in valid_matchups if not b['win']) / tot_battles
        perc_win_negative_matchup = sum(1 for b in valid_matchups if b['win'] and b['matchup'] < 40) / sum(1 for b in valid_matchups if b['matchup'] < 40) if sum(1 for b in valid_matchups if b['matchup'] < 40) > 0 else 0
        perc_lose_positive_matchup = sum(1 for b in valid_matchups if not b['win'] and b['matchup'] > 80) / sum(1 for b in valid_matchups if b['matchup'] > 80) if sum(1 for b in valid_matchups if b['matchup'] > 80) > 0 else 0
    else:
        winrate = 0
        wins = 0
        loses = 0
        perc_win_negative_matchup = 0
        perc_lose_positive_matchup = 0

    matchups = [b['matchup'] for b in valid_matchups]
    stdev = statistics.stdev(matchups) if len(matchups) > 1 else 0

    return {
        'tot_battles': tot_battles,
        'avg_matchup': avg_matchup,
        'stdev_matchup': stdev,
        'avg_level_diff': avg_level_diff,
        'n_extreme_matchup': n_extreme_matchup,
        'winrate': winrate,
        'wins': wins,
        'loses': loses,
        'perc_win_negative_matchup': perc_win_negative_matchup,
        'perc_lose_positive_matchup': perc_lose_positive_matchup
    }


def print_sessions(sessions, output_file=None):

    def log(msg=""):
        if output_file:
            output_file.write(msg + "\n")
        else:
            print(msg)

    if not sessions:
        log("Nessuna sessione da mostrare.")
        return
    
    # Accumulatori per le medie globali
    global_metrics = {
        'tot_battles': [],
        'avg_matchup': [],
        'stdev_matchup': [],
        'avg_level_diff': [],
        'n_extreme_matchup': [],
        'winrate': [],
        'perc_win_negative_matchup': [],
        'perc_lose_positive_matchup': []
    }

    for i, session in enumerate(sessions):
        log(f"\n--- SESSIONE {i+1} ---")
        
        for b in session['battles']:
            res = "WIN" if b['win'] else "LOSE"
            
            # Info extra
            trophy_info = ""
            if 'trophies_after' in b:
                trophy_info = f" | {b['trophies_before']} -> {b['trophies_after']} ({b['variation']:+})"
            
            matchup_str = f" | MU: {b['matchup']:.1f}%" if b['matchup'] is not None else " | MU: null"
            level_diff_str = f" - ΔLvl: {b['level_diff']}" if b['level_diff'] is not None else ""
            crowns = f"{b['player_crowns']}-{b['opponent_crowns']}"
            opponent = f" vs {b['opponent']}" if b['opponent'] else ""
            
            line = f"[{b['timestamp']}] {b['game_mode']}{opponent} | {res} -> {crowns}{trophy_info}{matchup_str}{level_diff_str}"
            log(line)
        
        # Stampa metriche sessione
        analysis = session.get('analysis')
        if analysis:
            log("\n   [METRICHE SESSIONE]")
            log(f"   Battaglie: {analysis['tot_battles']}")
            log(f"   Win Rate: {analysis['winrate']*100:.1f}%")
            log(f"   Avg Matchup: {analysis['avg_matchup']:.1f}% (StdDev: {analysis['stdev_matchup']:.1f}%)")
            log(f"   Avg Level Diff: {analysis['avg_level_diff']:.2f}")
            log(f"   Extreme Matchups: {analysis['n_extreme_matchup']}")
            log(f"   Win % (Negative MU <40%): {analysis['perc_win_negative_matchup']*100:.1f}%")
            log(f"   Lose % (Positive MU >80%): {analysis['perc_lose_positive_matchup']*100:.1f}%")

            # Accumulo per media globale
            for key in global_metrics:
                if key in analysis:
                    global_metrics[key].append(analysis[key])

        if session['stop_type'] != 'End':
            log(f"\n[STOP: {session['stop_type']} ({session['duration']})]")

    # Stampa Medie Globali
    log("\n" + "="*40)
    log(" MEDIA GLOBALE METRICHE (Su tutte le sessioni)")
    log("="*40)
    
    if any(global_metrics.values()):
        def safe_avg(values):
            return sum(values) / len(values) if values else 0

        avg_battles = safe_avg(global_metrics['tot_battles'])
        avg_winrate = safe_avg(global_metrics['winrate'])
        avg_matchup = safe_avg(global_metrics['avg_matchup'])
        avg_stdev = safe_avg(global_metrics['stdev_matchup'])
        avg_level = safe_avg(global_metrics['avg_level_diff'])
        avg_extreme = safe_avg(global_metrics['n_extreme_matchup'])
        avg_win_neg = safe_avg(global_metrics['perc_win_negative_matchup'])
        avg_lose_pos = safe_avg(global_metrics['perc_lose_positive_matchup'])

        log(f"   Avg Battaglie/Sessione: {avg_battles:.2f}")
        log(f"   Avg Win Rate: {avg_winrate*100:.1f}%")
        log(f"   Avg Matchup: {avg_matchup:.1f}% (Avg StdDev: {avg_stdev:.1f}%)")
        log(f"   Avg Level Diff: {avg_level:.2f}")
        log(f"   Avg Extreme Matchups: {avg_extreme:.2f}")
        log(f"   Avg Win % (Negative MU): {avg_win_neg*100:.1f}%")
        log(f"   Avg Lose % (Positive MU): {avg_lose_pos*100:.1f}%")
    else:
        log("   Nessun dato disponibile per le medie.")
    log("="*40)


def load_tags(cursor) -> list:
    """Carica i TAG dei giocatori dal database."""
    try:
        cursor.execute("SELECT player_tag FROM players")
        rows = cursor.fetchall()
        return [row[0] for row in rows]
    except Exception as e:
        print(f"Errore durante il caricamento dei tag: {e}")
        return []

def load_battles(cursor, tag):
    query = """
            SELECT b.battle_id, b.battle_type, b.game_mode, b.timestamp, b.win, b.level_diff, b.matchup_win_rate, b.trophy_change, b.opponent_tag, b.player_crowns, b.opponent_crowns, b.player_deck_id, d.archetype_hash
            FROM battles b
            LEFT JOIN decks d ON b.player_deck_id = d.deck_hash
            WHERE b.player_tag = ?
            ORDER BY b.timestamp ASC;
        """
    cursor.execute(query, (tag,))
    battles = cursor.fetchall()
    return battles

def load_trophies(cursor, tag):
    cursor.execute("SELECT trophies FROM players WHERE player_tag = ?", (tag,))
    row = cursor.fetchone()
    current_trophies = row[0] if row else 0
    return current_trophies


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


def get_players_sessions(mode_filter='all'):
    connection, cursor = open_connection("db/clash.db")
    tags = load_tags(cursor)

    players_sessions = []

    for tag in tags:
        battles = load_battles(cursor, tag)
        current_trophies = load_trophies(cursor, tag)

        trophies_history = define_trophies_history(battles, current_trophies)
        sessions = define_sessions(battles, trophies_history, mode_filter=mode_filter)
        
        profile = get_player_profile(battles)
        fsi = profile['avg_fsi'] if profile else 0

        players_sessions.append({
            'tag': tag,
            'sessions': sessions,
            'fsi': fsi
        })
    
    close_connection(connection)
    return players_sessions

def main():
    # Example usage: mode_filter can be 'all', 'Ladder', 'Ranked', 'Ladder_Ranked'
    players_sessions = get_players_sessions(mode_filter='all')
    
    output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)

    for p in players_sessions:
        tag = p['tag']
        sessions = p['sessions']
        with open(os.path.join(output_dir, f"log_{tag}.txt"), "w", encoding="utf-8") as f:
            print_sessions(sessions, output_file=f)
        print(f"Log generato per {tag}")


if __name__ == "__main__":
    main()