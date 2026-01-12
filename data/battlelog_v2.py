from datetime import datetime
import math
import statistics 
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../utils'))
# sys.path.append(os.path.join(os.path.dirname(__file__), '../data')) # Already in data

from connection import open_connection, close_connection
from charts import plot_matchup_trend

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

    # Filtro preliminare delle battaglie in base al flag
    if mode_filter == 'Ladder':
        battles = [b for b in battles if b[GAME_MODE_IDX] == 'Ladder']
    elif mode_filter == 'Ranked':
        battles = [b for b in battles if b[GAME_MODE_IDX] == 'Ranked']
    elif mode_filter == 'Ladder_Ranked':
        battles = [b for b in battles if b[GAME_MODE_IDX] in ['Ladder', 'Ranked']]
    # Se 'all', nessuna modifica

    # Gestione primo elemento (dopo il filtro)
    if battles:
        current_session_battles.append(create_battle_dict(battles[0]))

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

def calculate_profile_from_sessions(sessions):
    """
    Calcola il profilo comportamentale avanzato del giocatore.
    L'FSI (Frustration Sensitivity Index) ora tiene conto di:
    - Intensità dello stress (Sconfitte consecutive, Counter).
    - Tolleranza (Quanto a lungo gioca sotto stress prima di quittare).
    - Tipo di Quit (Short, Long, Rage Quit).
    """
    if not sessions:
        return None
    
    total_battles = 0
    total_duration = 0
    
    # Accumulatori per FSI
    total_loss_events = 0 # Numero totale di sconfitte (opportunità di quit)
    weighted_sensitivity_sum = 0.0 # Somma della sensibilità calcolata
    weighted_quit_count = 0 # Numero di volte che ha quittato con peso (per calcolo impulsività)
    
    # Statistiche di resilienza
    max_loss_streak_tolerated = 0
    loss_streak_continuations = 0 # Quante volte ha continuato dopo una streak >= 2
    counter_streak_continuations = 0 # Quante volte ha continuato dopo counter consecutivi
    loss_continuations = 0 # Quante volte ha continuato dopo una sconfitta
    
    # Statistiche Win
    total_wins = 0
    win_continuations = 0 # Quante volte ha continuato dopo una vittoria
    
    # Dati generali
    all_matchups = []
    
    # Pesi per il tipo di stop
    STOP_WEIGHTS = {'Short': 1.0, 'Long': 2.5, 'Quit': 5.0, 'End': 0.0}
    
    for session in sessions:
        battles = session['battles']
        num_battles = len(battles)
        total_battles += num_battles
        
        # Calcolo durata
        if num_battles > 1:
            start_ts = datetime.strptime(battles[0]['timestamp'], '%Y-%m-%d %H:%M:%S')
            end_ts = datetime.strptime(battles[-1]['timestamp'], '%Y-%m-%d %H:%M:%S')
            total_duration += (end_ts - start_ts).total_seconds()
            
        # Variabili di stato per la sessione corrente
        current_loss_streak = 0
        current_win_streak = 0
        current_counter_streak = 0
        current_stress = 0.0 # Accumulatore di "pressione" (Loss + Bad Matchup)

        for i, battle in enumerate(battles):
            matchup = battle['matchup']
            if matchup is not None:
                all_matchups.append(matchup)
            
            is_win = battle['win'] == 1
            is_last_battle = (i == num_battles - 1)
            
            # --- LOGICA WIN ---
            if is_win:
                total_wins += 1
                current_loss_streak = 0
                current_counter_streak = 0
                current_win_streak += 1
                
                # Riduzione stress proporzionale alla win streak (es. 1 win -> -2.0, 2 wins -> -4.0)
                stress_reduction = 2.0 * current_win_streak
                current_stress = max(0.0, current_stress - stress_reduction)
                
                if not is_last_battle:
                    win_continuations += 1
            
            # --- LOGICA LOSS ---
            else:
                total_loss_events += 1
                current_loss_streak += 1
                current_win_streak = 0
                
                # Calcolo Stress per questa battaglia
                battle_stress = 1.0 # Base loss
                
                # Penalità Matchup (Counter)
                if matchup is not None:
                    if matchup < 45.0:
                        battle_stress += 0.5 # Counter
                        current_counter_streak += 1
                    else:
                        current_counter_streak = 0
                        
                    if matchup < 35.0:
                        battle_stress += 0.5 # Hard Counter
                
                current_stress += battle_stress
                
                # Analisi Transizione (Continua o Quitta?)
                if not is_last_battle:
                    # HA CONTINUATO A GIOCARE
                    loss_continuations += 1
                    if current_loss_streak >= 2:
                        loss_streak_continuations += 1
                    if current_counter_streak >= 2:
                        counter_streak_continuations += 1
                    
                    # Aggiorna record resilienza
                    if current_loss_streak > max_loss_streak_tolerated:
                        max_loss_streak_tolerated = current_loss_streak
                        
                else:
                    # HA SMESSO DI GIOCARE (Session End)
                    stop_type = session['stop_type']
                    weight = STOP_WEIGHTS.get(stop_type, 0.0)
                    
                    if weight > 0:
                        # Calcolo Sensibilità:
                        # Se quitta con poco stress (es. 1 sconfitta), Sensitivity è ALTA (1/1 = 1).
                        # Se quitta con molto stress (es. 10 sconfitte), Sensitivity è BASSA (1/10 = 0.1).
                        # Moltiplicato per il peso del quit (Rage Quit > Short Break).
                        sensitivity = weight * (1.0 / current_stress)
                        weighted_sensitivity_sum += sensitivity
                        weighted_quit_count += 1

    # --- CALCOLO METRICHE FINALI ---
    
    # FSI: Media della sensibilità per ogni evento di sconfitta
    # Un player che continua sempre avrà weighted_sensitivity_sum = 0 -> FSI = 0.
    # Un player che quitta subito avrà weighted_sensitivity_sum alto e pochi loss events totali -> FSI Alto.
    avg_fsi = weighted_sensitivity_sum / total_loss_events if total_loss_events > 0 else 0.0
    
    # Quit Impulsivity: Media della sensibilità calcolata SOLO quando avviene un quit.
    # Indica "Quando quitta, quanto è stato impulsivo?". Alto = Quitta dopo 1 sconfitta. Basso = Quitta dopo tante.
    quit_impulsivity = weighted_sensitivity_sum / weighted_quit_count if weighted_quit_count > 0 else 0.0
    
    # ERS = Impulsività * exp(-FSI)
    ers = quit_impulsivity * math.exp(-avg_fsi)
    
    avg_matchup = statistics.mean(all_matchups) if all_matchups else 50.0
    avg_session_min = (total_duration / 60) / len(sessions) if sessions else 0
    matches_per_session = total_battles / len(sessions) if sessions else 0
    
    win_continuation_rate = win_continuations / total_wins if total_wins > 0 else 0.0
    loss_continuation_rate = loss_continuations / total_loss_events if total_loss_events > 0 else 0.0
    
    # Conteggio Losing Streaks (>=3) per compatibilità
    l_streak_count = loss_streak_continuations # Approssimazione basata sulle continuazioni
    
    # Affidabilità statistica
    is_reliable = total_battles > 50 and matches_per_session > 2

    return {
        'total_matches': total_battles,
        'num_sessions': len(sessions),
        'avg_fsi': round(avg_fsi, 3),
        'quit_impulsivity': round(quit_impulsivity, 3),
        'ers': round(ers, 3),
        'avg_session_min': round(avg_session_min, 2),
        'matches_per_session': round(matches_per_session, 2),
        'l_streak_count': l_streak_count,
        'max_loss_streak_tolerated': max_loss_streak_tolerated,
        'win_continuation_rate': round(win_continuation_rate * 100, 1),
        'loss_continuation_rate': round(loss_continuation_rate * 100, 1),
        'avg_matchup_pct': round(avg_matchup, 2),
        'is_reliable': is_reliable,
        'counter_streak_continuations': counter_streak_continuations
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
    connection, cursor, load_tags = open_connection("db/clash.db")
    tags = load_tags()

    players_sessions = []

    for tag in tags:
        battles = load_battles(cursor, tag)
        current_trophies = load_trophies(cursor, tag)

        trophies_history = define_trophies_history(battles, current_trophies)
        sessions = define_sessions(battles, trophies_history, mode_filter=mode_filter)
        
        profile = calculate_profile_from_sessions(sessions)
        fsi = profile['avg_fsi'] if profile else 0

        players_sessions.append({
            'tag': tag,
            'sessions': sessions,
            'profile': profile,
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

        plot_matchup_trend(sessions, tag, output_dir)

if __name__ == "__main__":
    main()