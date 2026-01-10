from datetime import datetime
import statistics 
import sys
import os
import numpy as np
from scipy.stats import spearmanr, fisher_exact

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

def define_sessions(battles, trophies_history):
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
    def calculate_matchup_drift(battles):
        if len(battles) < 3: 
            return 0
    
        # X = indice della partita (0, 1, 2...), Y = valore matchup
        x = np.arange(len(battles))
        y = np.array([b['matchup'] for b in battles])
    
        # Calcola la pendenza (slope) della retta
        slope, intercept = np.polyfit(x, y, 1)
    
        return slope

    # Filtra battaglie con matchup valido per statistiche matchup
    valid_matchups = [b for b in battles if b['matchup'] is not None]
    
    # tot_battles, avg_matchup, avg_level_diff, n_extreme_matchup,  winrate,
    tot_battles = len(battles)
    avg_matchup = sum(b['matchup'] for b in valid_matchups) / len(valid_matchups) if valid_matchups else 0
    avg_level_diff = sum(b['level_diff'] for b in battles) / tot_battles if tot_battles > 0 else 0
    n_extreme_matchup = sum(1 for b in valid_matchups if b['matchup'] > 80 or b['matchup'] < 40)
    winrate = sum(1 for b in battles if b['win']) / tot_battles if tot_battles > 0 else 0
    wins = sum(1 for b in battles if b['win']) / tot_battles if tot_battles > 0 else 0
    loses = sum(1 for b in battles if not b['win']) / tot_battles
    perc_win_negative_matchup = sum(1 for b in valid_matchups if b['win'] and b['matchup'] < 40) / sum(1 for b in valid_matchups if b['matchup'] < 40) if sum(1 for b in valid_matchups if b['matchup'] < 40) > 0 else 0
    perc_lose_positive_matchup = sum(1 for b in valid_matchups if not b['win'] and b['matchup'] > 80) / sum(1 for b in valid_matchups if b['matchup'] > 80) if sum(1 for b in valid_matchups if b['matchup'] > 80) > 0 else 0


    matchups = [b['matchup'] for b in valid_matchups]
    stdev = statistics.stdev(matchups) if len(matchups) > 1 else 0

    drift = calculate_matchup_drift(valid_matchups)


    return {
        'tot_battles': tot_battles,
        'avg_matchup': avg_matchup,
        'stdev_matchup': stdev,
        'matchup_drift': drift,
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
        'matchup_drift': [],
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
            log(f"   Matchup Drift: {analysis['matchup_drift']:.4f}")
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
        avg_drift = safe_avg(global_metrics['matchup_drift'])
        avg_level = safe_avg(global_metrics['avg_level_diff'])
        avg_extreme = safe_avg(global_metrics['n_extreme_matchup'])
        avg_win_neg = safe_avg(global_metrics['perc_win_negative_matchup'])
        avg_lose_pos = safe_avg(global_metrics['perc_lose_positive_matchup'])

        log(f"   Avg Battaglie/Sessione: {avg_battles:.2f}")
        log(f"   Avg Win Rate: {avg_winrate*100:.1f}%")
        log(f"   Avg Matchup: {avg_matchup:.1f}% (Avg StdDev: {avg_stdev:.1f}%)")
        log(f"   Avg Matchup Drift: {avg_drift:.4f}")
        log(f"   Avg Level Diff: {avg_level:.2f}")
        log(f"   Avg Extreme Matchups: {avg_extreme:.2f}")
        log(f"   Avg Win % (Negative MU): {avg_win_neg*100:.1f}%")
        log(f"   Avg Lose % (Positive MU): {avg_lose_pos*100:.1f}%")
    else:
        log("   Nessun dato disponibile per le medie.")
    log("="*40)


def calculate_variance_ratio(data):
    low_fsi_variances = []
    high_fsi_variances = []

    print("\n" + "="*60)
    print(" ANALISI VARIANZA SESSIONI vs FSI")
    print("="*60)

    for p in data:
        variance = p['std_dev'] ** 2
        fsi = p['fsi']
        
        print(f"Player: {p['tag']:<10} | FSI: {fsi:.2f} | StdDev: {p['std_dev']:.2f} | Var: {variance:.2f}")

        if fsi < 0.81:
            low_fsi_variances.append(variance)
        elif fsi > 1.20:
            high_fsi_variances.append(variance)

    avg_var_low = statistics.mean(low_fsi_variances) if low_fsi_variances else 0
    avg_var_high = statistics.mean(high_fsi_variances) if high_fsi_variances else 0

    print("\n" + "-"*60)
    print(f"Gruppo Low FSI (<0.81)  [n={len(low_fsi_variances)}]: Avg Varianza = {avg_var_low:.2f}")
    print(f"Gruppo High FSI (>1.20) [n={len(high_fsi_variances)}]: Avg Varianza = {avg_var_high:.2f}")
    
    if avg_var_low > 0:
        ratio = avg_var_high / avg_var_low
        print(f"RAPPORTO (High/Low): {ratio:.2f}")
    else:
        print("RAPPORTO: N/A (Varianza Low = 0)")
    print("="*60 + "\n")


def calculate_fsi_variance_correlation(data):
    print("\n" + "="*60)
    print(" CORRELAZIONE SPEARMAN: FSI vs VARIANZA")
    print("="*60)

    if len(data) < 3:
        print("Campione insufficiente per il calcolo della correlazione.")
        print("="*60 + "\n")
        return

    fsi_values = [d['fsi'] for d in data]
    variances = [d['std_dev'] ** 2 for d in data]

    corr, p_value = spearmanr(fsi_values, variances)

    print(f"Campione:     {len(data)} giocatori")
    print(f"Coefficiente: {corr:.4f}")
    print(f"P-value:      {p_value:.4f}")
    print("="*60 + "\n")


def analyze_session_pity(players_sessions):
    output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'session_pity_test_results.txt')

    print(f"\nGenerazione report test sessioni per player in: {output_file}")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI FISHER: SESSION PITY (Low Avg MU -> High Avg MU) PER PLAYER\n")
        f.write("Ipotesi: Una sessione con Avg Matchup < 45% è seguita da una con Avg Matchup > 55%?\n")
        f.write("="*80 + "\n")

        LOW_THRESH = 45.0
        HIGH_THRESH = 55.0
        
        global_significant = 0
        total_tested = 0

        for p in players_sessions:
            tag = p['tag']
            sessions = p['sessions']
            
            # Matrix per player: [[A, B], [C, D]]
            matrix = [[0, 0], [0, 0]]
            count = 0

            for i in range(len(sessions) - 1):
                s_prev = sessions[i]
                s_next = sessions[i+1]
                
                if 'analysis' not in s_prev or 'analysis' not in s_next:
                    continue
                
                if s_prev['analysis']['tot_battles'] == 0 or s_next['analysis']['tot_battles'] == 0:
                    continue

                mu_prev = s_prev['analysis']['avg_matchup']
                mu_next = s_next['analysis']['avg_matchup']
                
                is_prev_low = mu_prev < LOW_THRESH
                is_next_high = mu_next > HIGH_THRESH
                
                if is_prev_low:
                    if is_next_high:
                        matrix[0][0] += 1
                    else:
                        matrix[0][1] += 1
                else:
                    if is_next_high:
                        matrix[1][0] += 1
                    else:
                        matrix[1][1] += 1
                count += 1
            
            if count < 2: # Skip se dati insufficienti
                continue

            total_tested += 1
            odds_ratio, p_value = fisher_exact(matrix, alternative='greater')
            
            is_sig = p_value < 0.05
            if is_sig:
                global_significant += 1

            f.write(f"\nPLAYER: {tag}\n")
            f.write(f"Coppie di sessioni: {count}\n")
            f.write(f"Matrice: {matrix}\n")
            f.write(f"Odds Ratio: {odds_ratio:.4f}\n")
            f.write(f"P-value:    {p_value:.4f}\n")
            f.write(f"Risultato:  {'SIGNIFICATIVO' if is_sig else 'Non significativo'}\n")
            f.write("-" * 40 + "\n")

        f.write("\n" + "="*80 + "\n")
        f.write(f"RIEPILOGO:\n")
        f.write(f"Totale Player Analizzati: {total_tested}\n")
        f.write(f"Player con P-value < 0.05: {global_significant}\n")
        if total_tested > 0:
            f.write(f"Percentuale Significativi: {(global_significant/total_tested)*100:.2f}%\n")
        f.write("="*80 + "\n")


def analyze_std_correlation(players_sessions):
    data = []

    for player_sessions in players_sessions:
        long_sessions = [s for s in player_sessions['sessions'] if len(s['battles']) >= 3]

        if not long_sessions or len(long_sessions) < 3:
            continue

        avg_matchup = [s['analysis']['avg_matchup'] for s in long_sessions]
        std_matchups = statistics.stdev(avg_matchup)
        fsi = player_sessions.get('fsi', 0)

        print(f"Player: {player_sessions['tag']}     -     std_dev: {std_matchups:.2f}")
        data.append({
            'tag': player_sessions['tag'],
            'std_dev': std_matchups,
            'fsi': fsi
        })
        
    calculate_variance_ratio(data)
    calculate_fsi_variance_correlation(data)


def analyze_extreme_matchup_streak(players_sessions):
    print("\n" + "="*60)
    print(" ANALISI STREAK MATCHUP ESTREMI (>= 3 consecutivi in sessione)")
    print("="*60)

    # Soglie
    HIGH_THRESH = 80.0
    LOW_THRESH = 40.0
    STREAK_LEN = 3

    total_valid_battles = 0
    count_high = 0
    count_low = 0

    streak_opportunities = 0
    found_high_streaks = 0
    found_low_streaks = 0

    for p in players_sessions:
        for session in p['sessions']:
            # Estrai matchups validi della sessione
            matchups = [b['matchup'] for b in session['battles'] if b['matchup'] is not None]
            
            # Aggiorna statistiche globali per calcolo probabilità teorica
            for m in matchups:
                total_valid_battles += 1
                if m > HIGH_THRESH:
                    count_high += 1
                elif m < LOW_THRESH:
                    count_low += 1
            
            # Analisi Streak nella sessione (Sliding Window)
            if len(matchups) >= STREAK_LEN:
                for i in range(len(matchups) - STREAK_LEN + 1):
                    streak_opportunities += 1
                    window = matchups[i : i+STREAK_LEN]
                    
                    if all(m > HIGH_THRESH for m in window):
                        found_high_streaks += 1
                    
                    if all(m < LOW_THRESH for m in window):
                        found_low_streaks += 1

    if total_valid_battles == 0 or streak_opportunities == 0:
        print("Dati insufficienti per l'analisi.")
        print("="*60 + "\n")
        return

    # Calcolo Probabilità
    p_high = count_high / total_valid_battles
    p_low = count_low / total_valid_battles

    prob_theory_high = p_high ** STREAK_LEN
    prob_theory_low = p_low ** STREAK_LEN

    prob_obs_high = found_high_streaks / streak_opportunities
    prob_obs_low = found_low_streaks / streak_opportunities

    print(f"Totale Battaglie Analizzate: {total_valid_battles}")
    print(f"Finestre di {STREAK_LEN} partite analizzate: {streak_opportunities}")
    print("-" * 60)
    
    ratio_high = prob_obs_high / prob_theory_high if prob_theory_high > 0 else 0
    print(f"MATCHUP FAVOREVOLI (> {HIGH_THRESH}%)")
    print(f"  Freq. Base Osservata (p): {p_high*100:.2f}%")
    print(f"  Prob. Teorica 3-in-a-row (p^3): {prob_theory_high*100:.4f}%")
    print(f"  Prob. Reale Osservata:          {prob_obs_high*100:.4f}%")
    print(f"  Ratio (Obs/Theory):             {ratio_high:.2f}x")
    
    print("-" * 60)

    ratio_low = prob_obs_low / prob_theory_low if prob_theory_low > 0 else 0
    print(f"MATCHUP SFAVOREVOLI (< {LOW_THRESH}%)")
    print(f"  Freq. Base Osservata (p): {p_low*100:.2f}%")
    print(f"  Prob. Teorica 3-in-a-row (p^3): {prob_theory_low*100:.4f}%")
    print(f"  Prob. Reale Osservata:          {prob_obs_low*100:.4f}%")
    print(f"  Ratio (Obs/Theory):             {ratio_low:.2f}x")

    print("="*60 + "\n")



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
            SELECT battle_id, battle_type, game_mode, timestamp, win, level_diff, matchup_win_rate, trophy_change, opponent_tag, player_crowns, opponent_crowns
            FROM battles
            WHERE player_tag = ?
            ORDER BY timestamp ASC;
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


def main():
    connection, cursor = open_connection("db/clash.db")

    tags = load_tags(cursor)
    #tags = ['JJYP08']

    players_sessions = []

    for tag in tags:
        battles = load_battles(cursor, tag)
        current_trophies = load_trophies(cursor, tag)

        trophies_history = define_trophies_history(battles, current_trophies)
        
        sessions = define_sessions(battles, trophies_history)
        
        profile = get_player_profile(battles)
        fsi = profile['avg_fsi'] if profile else 0

        players_sessions.append({
            'tag': tag,
            'sessions': sessions,
            'fsi': fsi
        })
        
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, f"log_{tag}.txt"), "w", encoding="utf-8") as f:
            print_sessions(sessions, output_file=f)


        print(f"Log generato per {tag}")

    analyze_std_correlation(players_sessions)
    analyze_session_pity(players_sessions)
    analyze_extreme_matchup_streak(players_sessions)



    close_connection(connection)


if __name__ == "__main__":
    main()