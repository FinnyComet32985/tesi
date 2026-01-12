from datetime import datetime
import random
import statistics 
import sys
import os
import numpy as np
from scipy.stats import spearmanr, fisher_exact, chi2_contingency, kruskal, levene

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


def analyze_matchup_correlation(players_sessions):
    pass







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
                
                if s_prev['analysis']['tot_battles'] <2 or s_next['analysis']['tot_battles'] <2:
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
    output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'extreme_matchup_streak_results.txt')

    print(f"\nGenerazione report streak matchup estremi in: {output_file}")

    # Soglie
    HIGH_THRESH = 80.0
    LOW_THRESH = 30.0
    STREAK_LEN = 3
    NUM_SIMULATIONS = 1000

    # Accumulatori
    total_battles = 0
    count_high = 0
    count_low = 0
    
    obs_high_streaks = 0
    obs_low_streaks = 0
    total_opportunities = 0
    
    # Struttura dati per simulazioni: list of (matchups_list, session_lengths_list)
    players_data = []

    for p in players_sessions:
        p_matchups = []
        p_lengths = []
        
        for session in p['sessions']:
            mus = [b['matchup'] for b in session['battles'] if b['matchup'] is not None and (b['game_mode'] == 'Ladder' or b['game_mode'] == 'Ranked')]
            if not mus: 
                continue
            
            p_matchups.extend(mus)
            p_lengths.append(len(mus))
            
            # Stats per Teorico
            for m in mus:
                total_battles += 1
                if m > HIGH_THRESH: count_high += 1
                elif m < LOW_THRESH: count_low += 1
            
            # Osservato
            if len(mus) >= STREAK_LEN:
                for i in range(len(mus) - STREAK_LEN + 1):
                    total_opportunities += 1
                    window = mus[i : i+STREAK_LEN]
                    if all(m > HIGH_THRESH for m in window): 
                        obs_high_streaks += 1
                    if all(m < LOW_THRESH for m in window): 
                        obs_low_streaks += 1
        
        if p_matchups:
            players_data.append((p_matchups, p_lengths))

    if total_opportunities == 0:
        print("Dati insufficienti per l'analisi streak.")
        return

    # Calcolo Teorico
    p_high = count_high / total_battles if total_battles else 0
    p_low = count_low / total_battles if total_battles else 0
    
    exp_high_theory = total_opportunities * (p_high ** STREAK_LEN)
    exp_low_theory = total_opportunities * (p_low ** STREAK_LEN)

    # Simulazione 1: Global Shuffle
    sim_high_streaks_sum = 0
    sim_low_streaks_sum = 0
    
    # Simulazione 2: Intra-Session Shuffle
    sim_intra_high = 0
    sim_intra_low = 0

    print(f"Esecuzione di {NUM_SIMULATIONS} permutazioni (Global & Intra-Session)...")

    for _ in range(NUM_SIMULATIONS):
        for mus, lengths in players_data:
            # --- Global Shuffle ---
            global_shuffled = mus[:]
            random.shuffle(global_shuffled)
            
            idx = 0
            for l in lengths:
                s = global_shuffled[idx : idx+l]
                idx += l
                if len(s) >= STREAK_LEN:
                    for i in range(len(s) - STREAK_LEN + 1):
                        if all(m > HIGH_THRESH for m in s[i:i+STREAK_LEN]): sim_high_streaks_sum += 1
                        if all(m < LOW_THRESH for m in s[i:i+STREAK_LEN]): sim_low_streaks_sum += 1

            # --- Intra-Session Shuffle ---
            # Ricostruiamo le sessioni originali e mescoliamo internamente
            idx = 0
            for l in lengths:
                s_orig = mus[idx : idx+l]
                idx += l
                
                s_intra = s_orig[:]
                random.shuffle(s_intra)
                
                if len(s_intra) >= STREAK_LEN:
                    for i in range(len(s_intra) - STREAK_LEN + 1):
                        if all(m > HIGH_THRESH for m in s_intra[i:i+STREAK_LEN]): sim_intra_high += 1
                        if all(m < LOW_THRESH for m in s_intra[i:i+STREAK_LEN]): sim_intra_low += 1

    avg_global_high = sim_high_streaks_sum / NUM_SIMULATIONS
    avg_global_low = sim_low_streaks_sum / NUM_SIMULATIONS
    
    avg_intra_high = sim_intra_high / NUM_SIMULATIONS
    avg_intra_low = sim_intra_low / NUM_SIMULATIONS

    # Scrittura Report
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI STREAK MATCHUP ESTREMI (>= 3 consecutivi in sessione)\n")
        f.write("="*80 + "\n")
        f.write(f"Totale Battaglie: {total_battles}\n")
        f.write(f"Totale Finestre (Opportunità): {total_opportunities}\n")
        f.write(f"Soglie: High > {HIGH_THRESH}%, Low < {LOW_THRESH}%\n")
        f.write("-" * 80 + "\n")
        f.write("DEFINIZIONI:\n")
        f.write("1. OSSERVATO: Il numero reale di streak trovate nei dati.\n")
        f.write("2. TEORICO: Probabilità p^3 basata sulla frequenza globale dei matchup (ipotesi indipendenza).\n")
        f.write("3. GLOBAL SHUFFLE: Mescola tutte le partite del player. Verifica se i matchup si 'aggrumano' in sessioni specifiche.\n")
        f.write("4. INTRA-SESSION SHUFFLE: Mescola solo dentro la sessione. Verifica se l'ordine interno è manipolato.\n")
        f.write("="*80 + "\n\n")

        def write_section(label, obs, exp_theory, avg_global, avg_intra):
            f.write(f"--- {label} ---\n")
            f.write(f"{'Metodo':<25} | {'Count':<10} | {'Prob %':<10} | {'Ratio (Obs/Exp)':<15}\n")
            f.write("-" * 70 + "\n")
            
            prob_obs = obs / total_opportunities * 100
            f.write(f"{'Osservato':<25} | {obs:<10} | {prob_obs:<10.4f} | {'1.00x':<15}\n")
            
            prob_theory = exp_theory / total_opportunities * 100
            ratio_theory = obs / exp_theory if exp_theory > 0 else 0
            f.write(f"{'Teorico (p^3)':<25} | {exp_theory:<10.2f} | {prob_theory:<10.4f} | {ratio_theory:<15.2f}\n")
            
            prob_global = avg_global / total_opportunities * 100
            ratio_global = obs / avg_global if avg_global > 0 else 0
            f.write(f"{'Global Shuffle':<25} | {avg_global:<10.2f} | {prob_global:<10.4f} | {ratio_global:<15.2f}\n")
            
            prob_intra = avg_intra / total_opportunities * 100
            ratio_intra = obs / avg_intra if avg_intra > 0 else 0
            f.write(f"{'Intra-Session Shuffle':<25} | {avg_intra:<10.2f} | {prob_intra:<10.4f} | {ratio_intra:<15.2f}\n")
            f.write("\n")

        write_section(f"MATCHUP FAVOREVOLI (> {HIGH_THRESH}%)", obs_high_streaks, exp_high_theory, avg_global_high, avg_intra_high)
        write_section(f"MATCHUP SFAVOREVOLI (< {LOW_THRESH}%)", obs_low_streaks, exp_low_theory, avg_global_low, avg_intra_low)


def analyze_confounding_factors(players_sessions):
    output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'confounding_factors_results.txt')

    print(f"\nGenerazione report fattori confondenti (Orario/Deck) in: {output_file}")

    # Soglie
    HIGH_THRESH = 80.0
    LOW_THRESH = 40.0
    STREAK_LEN = 3

    # --- 1. ANALISI ORARIA (Globale) ---
    # Fasce: 0=Notte(0-6), 1=Mattina(6-12), 2=Pom(12-18), 3=Sera(18-24)
    time_slots = {0: "Notte (00-06)", 1: "Mattina (06-12)", 2: "Pomeriggio (12-18)", 3: "Sera (18-24)"}
    
    # [Slot] -> {'total_windows': 0, 'streak_windows': 0}
    time_stats = {k: {'total': 0, 'streak': 0} for k in time_slots}

    # --- 2. ANALISI DECK (Per Player) ---
    deck_independence_count = 0
    deck_total_tested = 0

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI FATTORI CONFONDENTI: ORARIO E DECK\n")
        f.write("Obiettivo: Dimostrare che le streak sono indipendenti da orario e mazzo usato.\n")
        f.write("="*80 + "\n\n")

        for p in players_sessions:
            # Per analisi Deck del singolo player
            # DeckID -> {'total': 0, 'streak': 0}
            player_deck_stats = {}

            for session in p['sessions']:
                battles = [b for b in session['battles'] if b['game_mode'] == 'Ladder' or b['game_mode'] == 'Ranked']
                if len(battles) < STREAK_LEN: continue

                for i in range(len(battles) - STREAK_LEN + 1):
                    window = battles[i : i+STREAK_LEN]
                    matchups = [b['matchup'] for b in window if b['matchup'] is not None]
                    
                    if len(matchups) < STREAK_LEN: continue

                    # Dati finestra
                    first_b = window[0]
                    ts = datetime.strptime(first_b['timestamp'], '%Y-%m-%d %H:%M:%S')
                    hour = ts.hour
                    deck_id = first_b.get('deck_id')

                    # Determina Fascia Oraria
                    slot = 0
                    if 6 <= hour < 12: slot = 1
                    elif 12 <= hour < 18: slot = 2
                    elif 18 <= hour < 24: slot = 3
                    
                    # Determina se è Streak (High o Low)
                    is_streak = all(m > HIGH_THRESH for m in matchups) or all(m < LOW_THRESH for m in matchups)

                    # Aggiorna Time Stats (Globale)
                    time_stats[slot]['total'] += 1
                    if is_streak:
                        time_stats[slot]['streak'] += 1

                    # Aggiorna Deck Stats (Player)
                    if deck_id:
                        if deck_id not in player_deck_stats:
                            player_deck_stats[deck_id] = {'total': 0, 'streak': 0}
                        player_deck_stats[deck_id]['total'] += 1
                        if is_streak:
                            player_deck_stats[deck_id]['streak'] += 1

            # Test Chi-Quadro Deck per il player corrente
            # Consideriamo solo i top 3 mazzi per avere dati significativi
            sorted_decks = sorted(player_deck_stats.items(), key=lambda x: x[1]['total'], reverse=True)[:3]
            if len(sorted_decks) >= 2:
                # Costruiamo tabella contingenza: [[Streak_D1, NoStreak_D1], [Streak_D2, NoStreak_D2], ...]
                obs = []
                valid_decks = 0
                for d_id, stats in sorted_decks:
                    if stats['total'] > 10: # Minimo 10 finestre per validità
                        obs.append([stats['streak'], stats['total'] - stats['streak']])
                        valid_decks += 1
                
                if valid_decks >= 2:
                    deck_total_tested += 1
                    try:
                        chi2, p, dof, ex = chi2_contingency(obs)
                        if p > 0.05:
                            deck_independence_count += 1
                    except ValueError:
                        # Se fallisce (es. 0 streak totali), assumiamo indipendenza
                        deck_independence_count += 1

        # --- SCRITTURA RISULTATI TIME ---
        f.write("1. ANALISI ORARIA (Globale)\n")
        f.write(f"{'Fascia Oraria':<25} | {'Tot Finestre':<15} | {'Streak Trovate':<15} | {'Streak Rate %':<15}\n")
        f.write("-" * 80 + "\n")
        
        time_obs = []
        for slot in sorted(time_stats.keys()):
            s = time_stats[slot]
            rate = (s['streak'] / s['total'] * 100) if s['total'] > 0 else 0
            f.write(f"{time_slots[slot]:<25} | {s['total']:<15} | {s['streak']:<15} | {rate:<15.2f}%\n")
            if s['total'] > 0:
                time_obs.append([s['streak'], s['total'] - s['streak']])
        
        p_time = 1.0
        res_time = "Dati insufficienti"

        if len(time_obs) >= 2:
            # Verifica che ci siano sia streak che non-streak nel totale per evitare expected=0
            total_streaks = sum(row[0] for row in time_obs)
            total_non_streaks = sum(row[1] for row in time_obs)
            
            if total_streaks > 0 and total_non_streaks > 0:
                try:
                    chi2_time, p_time, _, _ = chi2_contingency(time_obs)
                    res_time = "INDIPENDENTE (L'orario NON influisce)" if p_time > 0.05 else "DIPENDENTE (L'orario influisce)"
                except ValueError:
                    res_time = "Errore calcolo (Freq attesa 0)"
            else:
                res_time = "INDIPENDENTE (Dati costanti/0 eventi)"
        
        f.write("-" * 80 + "\n")
        f.write(f"Test Chi-Quadro Indipendenza Oraria:\n")
        f.write(f"P-value: {p_time:.4f}\n")
        f.write(f"Risultato: {res_time}\n\n")

        # --- SCRITTURA RISULTATI DECK ---
        f.write("2. ANALISI DECK (Aggregata per Player)\n")
        f.write("Verifica se la probabilità di streak cambia cambiando mazzo (tra i mazzi più usati).\n")
        f.write("-" * 80 + "\n")
        f.write(f"Player analizzati (con almeno 2 mazzi usati >10 volte): {deck_total_tested}\n")
        f.write(f"Player con streak INDIPENDENTI dal mazzo (p > 0.05):    {deck_independence_count}\n")
        perc = (deck_independence_count / deck_total_tested * 100) if deck_total_tested > 0 else 0
        f.write(f"Percentuale Indipendenza: {perc:.2f}%\n")
        f.write("="*80 + "\n")


def analyze_time_matchup_stats(players_sessions):
    output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'time_matchup_stats.txt')

    print(f"\nGenerazione report statistiche temporali in: {output_file}")

    time_slots = {0: "Notte (00-06)", 1: "Mattina (06-12)", 2: "Pomeriggio (12-18)", 3: "Sera (18-24)"}
    # Slot -> list of matchups
    samples = {k: [] for k in time_slots}

    for p in players_sessions:
        for session in p['sessions']:
            for b in session['battles']:
                if b['matchup'] is not None:
                    ts = datetime.strptime(b['timestamp'], '%Y-%m-%d %H:%M:%S')
                    h = ts.hour
                    slot = 0
                    if 6 <= h < 12: slot = 1
                    elif 12 <= h < 18: slot = 2
                    elif 18 <= h < 24: slot = 3
                    
                    samples[slot].append(b['matchup'])

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI STATISTICA MATCHUP PER FASCIA ORARIA\n")
        f.write("Obiettivo: Verificare se Media e Varianza del matchup cambiano durante il giorno.\n")
        f.write("="*80 + "\n\n")
        
        f.write(f"{'Fascia Oraria':<20} | {'N. Partite':<12} | {'Media MU':<10} | {'StdDev':<10} | {'Varianza':<10}\n")
        f.write("-" * 75 + "\n")

        valid_samples = [] # List of arrays for statistical tests
        
        for slot in sorted(time_slots.keys()):
            data = samples[slot]
            if not data:
                f.write(f"{time_slots[slot]:<20} | {'0':<12} | {'-':<10} | {'-':<10} | {'-':<10}\n")
                continue
            
            avg = statistics.mean(data)
            stdev = statistics.stdev(data) if len(data) > 1 else 0
            var = stdev ** 2
            
            f.write(f"{time_slots[slot]:<20} | {len(data):<12} | {avg:<10.2f} | {stdev:<10.2f} | {var:<10.2f}\n")
            
            valid_samples.append(data)

        f.write("-" * 75 + "\n\n")
        f.write("TEST STATISTICI:\n")
        
        if len(valid_samples) < 2:
            f.write("Dati insufficienti per i test (servono almeno 2 fasce orarie con dati).\n")
        else:
            # 1. Kruskal-Wallis (Non-parametric ANOVA) for Location/Mean
            try:
                stat_k, p_k = kruskal(*valid_samples)
                f.write("1. Kruskal-Wallis (Confronto Medie/Distribuzione):\n")
                f.write(f"   P-value: {p_k:.4f}\n")
                res_k = "DIFFERENZA SIGNIFICATIVA (Il matchup medio cambia?)" if p_k < 0.05 else "NESSUNA DIFFERENZA (Matchup medio costante)"
                f.write(f"   Risultato: {res_k}\n\n")
            except Exception as e:
                f.write(f"   Errore Kruskal-Wallis: {e}\n\n")

            # 2. Levene Test for Variance
            try:
                stat_l, p_l = levene(*valid_samples)
                f.write("2. Levene Test (Confronto Varianze):\n")
                f.write(f"   P-value: {p_l:.4f}\n")
                res_l = "DIFFERENZA SIGNIFICATIVA (La variabilità del matchup cambia?)" if p_l < 0.05 else "NESSUNA DIFFERENZA (Variabilità costante)"
                f.write(f"   Risultato: {res_l}\n\n")
                
                if p_l < 0.05:
                    f.write("   NOTA: Una varianza diversa suggerisce che in certe fasce orarie\n")
                    f.write("   il matchmaking è più 'lasco' o la popolazione di player è diversa,\n")
                    f.write("   creando più matchup estremi (streak) anche se la media è simile.\n")
            except Exception as e:
                f.write(f"   Errore Levene Test: {e}\n\n")
        
        f.write("="*80 + "\n")


def analyze_deck_switch_impact(players_sessions):
    output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'deck_switch_impact.txt')

    print(f"\nGenerazione report impatto cambio deck in: {output_file}")

    # Soglie per definire le "Zone" di Matchup
    BAD_THRESH = 45.0
    GOOD_THRESH = 55.0
    
    # Accumulatori per Transizioni: [Is_Switch][From_Zone][To_Zone]
    # Is_Switch: True (Cambio Archetipo), False (Stesso Archetipo)
    # Zones: 'Bad', 'Mid', 'Good'
    transitions = {
        True: {'Bad': {'Bad': 0, 'Mid': 0, 'Good': 0}, 'Mid': {'Bad': 0, 'Mid': 0, 'Good': 0}, 'Good': {'Bad': 0, 'Mid': 0, 'Good': 0}},
        False: {'Bad': {'Bad': 0, 'Mid': 0, 'Good': 0}, 'Mid': {'Bad': 0, 'Mid': 0, 'Good': 0}, 'Good': {'Bad': 0, 'Mid': 0, 'Good': 0}}
    }
    
    total_switches = 0
    total_noswitches = 0

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI IMPATTO CAMBIO DECK (ARCHETIPO) SUL PATTERN MATCHUP\n")
        f.write("Obiettivo: Verificare se il cambio di mazzo interrompe il pattern di matchup (es. serie negativa) o se esso persiste.\n")
        f.write("Ipotesi: Se il sistema è 'rigged' contro il giocatore, la serie negativa (Bad->Bad) dovrebbe continuare anche cambiando mazzo.\n")
        f.write("         Se il sistema è equo/basato sul mazzo, cambiare mazzo dovrebbe 'resettare' o variare il matchup.\n")
        f.write("="*80 + "\n\n")
        
        for p in players_sessions:
            # Appiattiamo le sessioni per analizzare la sequenza temporale
            all_battles = []
            for s in p['sessions']:
                all_battles.extend(s['battles'])
            
            for i in range(len(all_battles) - 1):
                b_curr = all_battles[i]
                b_next = all_battles[i+1]
                
                mu_curr = b_curr.get('matchup')
                mu_next = b_next.get('matchup')
                
                if mu_curr is None or mu_next is None: continue
                
                # Determina Zone
                if mu_curr < BAD_THRESH: zone_curr = 'Bad'
                elif mu_curr > GOOD_THRESH: zone_curr = 'Good'
                else: zone_curr = 'Mid'
                
                if mu_next < BAD_THRESH: zone_next = 'Bad'
                elif mu_next > GOOD_THRESH: zone_next = 'Good'
                else: zone_next = 'Mid'
                
                # Determina Switch (Usa Archetipo se disponibile, fallback su deck_id)
                id_curr = b_curr.get('archetype_id') or b_curr.get('deck_id')
                id_next = b_next.get('archetype_id') or b_next.get('deck_id')
                
                # Se manca l'ID, saltiamo
                if not id_curr or not id_next: continue

                is_switch = (id_curr != id_next)
                
                transitions[is_switch][zone_curr][zone_next] += 1
                
                if is_switch: total_switches += 1
                else: total_noswitches += 1

        # Calcolo Percentuali di Persistenza
        def calc_persistence(data, from_z, to_z):
            total_from = sum(data[from_z].values())
            if total_from == 0: return 0.0
            return (data[from_z][to_z] / total_from) * 100

        # --- Report ---
        f.write(f"Totale Transizioni Analizzate: {total_switches + total_noswitches}\n")
        f.write(f"  - Senza cambio mazzo: {total_noswitches}\n")
        f.write(f"  - Con cambio mazzo:   {total_switches}\n")
        f.write("-" * 80 + "\n")
        
        f.write(f"{'PATTERN':<25} | {'NO SWITCH (Baseline)':<20} | {'SWITCH (Test)':<20} | {'DELTA':<10}\n")
        f.write("-" * 80 + "\n")

        patterns = [
            ('Bad', 'Bad', 'Persistenza Matchup Negativo'),
            ('Good', 'Good', 'Persistenza Matchup Positivo'),
            ('Bad', 'Good', 'Recupero (Bad -> Good)'),
            ('Good', 'Bad', 'Punizione (Good -> Bad)')
        ]

        for from_z, to_z, label in patterns:
            p_noswitch = calc_persistence(transitions[False], from_z, to_z)
            p_switch = calc_persistence(transitions[True], from_z, to_z)
            delta = p_switch - p_noswitch
            
            f.write(f"{label:<25} | {p_noswitch:<20.2f}% | {p_switch:<20.2f}% | {delta:<+10.2f}%\n")

        f.write("-" * 80 + "\n")
        f.write("INTERPRETAZIONE:\n")
        f.write("1. Se 'Persistenza Matchup Negativo' con SWITCH è simile o superiore a NO SWITCH,\n")
        f.write("   significa che cambiare mazzo NON aiuta a uscire dalla serie negativa (il sistema forza il matchup).\n")
        f.write("2. Se 'Persistenza Matchup Negativo' crolla con SWITCH,\n")
        f.write("   significa che il cambio mazzo ha effetto reale e il matchmaking risponde al nuovo mazzo.\n")
        f.write("="*80 + "\n")


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
    analyze_confounding_factors(players_sessions)
    analyze_time_matchup_stats(players_sessions)
    analyze_deck_switch_impact(players_sessions)



    close_connection(connection)


if __name__ == "__main__":
    main()