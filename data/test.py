from datetime import datetime
import math
import random
import statistics 
import os
import numpy as np
from scipy.stats import spearmanr, fisher_exact, chi2_contingency, kruskal, levene, mannwhitneyu, ttest_1samp, binomtest    

# Import data loader from battlelog_v2
from battlelog_v2 import get_players_sessions
from test_time_analysis import get_local_hour




def calculate_variance_ratio(data, f=None):
    def log(msg):
        if f:
            f.write(msg + "\n")
        else: 
            print(msg)

    low_fsi_variances = []
    high_fsi_variances = []

    log("\n" + "="*60)
    log(" ANALISI VARIANZA SESSIONI vs FSI")
    log("="*60)

    for p in data:
        variance = p['std_dev'] ** 2
        fsi = p['fsi']
        
        log(f"Player: {p['tag']:<10} | FSI: {fsi:.2f} | StdDev: {p['std_dev']:.2f} | Var: {variance:.2f}")

        if fsi < 0.81:
            low_fsi_variances.append(variance)
        elif fsi > 1.20:
            high_fsi_variances.append(variance)

    avg_var_low = statistics.mean(low_fsi_variances) if low_fsi_variances else 0
    avg_var_high = statistics.mean(high_fsi_variances) if high_fsi_variances else 0

    log("\n" + "-"*60)
    log(f"Gruppo Low FSI (<0.81)  [n={len(low_fsi_variances)}]: Avg Varianza = {avg_var_low:.2f}")
    log(f"Gruppo High FSI (>1.20) [n={len(high_fsi_variances)}]: Avg Varianza = {avg_var_high:.2f}")
    
    if avg_var_low > 0:
        ratio = avg_var_high / avg_var_low
        log(f"RAPPORTO (High/Low): {ratio:.2f}")
    else:
        log("RAPPORTO: N/A (Varianza Low = 0)")
    log("="*60 + "\n")

def calculate_fsi_variance_correlation(data, f=None):
    def log(msg):
        if f: 
            f.write(msg + "\n")
        else: 
            print(msg)

    log("\n" + "="*60)
    log(" CORRELAZIONE SPEARMAN: FSI vs VARIANZA")
    log("="*60)

    if len(data) < 3:
        log("Campione insufficiente per il calcolo della correlazione.")
        log("="*60 + "\n")
        return

    fsi_values = [d['fsi'] for d in data]
    variances = [d['std_dev'] ** 2 for d in data]

    corr, p_value = spearmanr(fsi_values, variances)

    log(f"Campione:     {len(data)} giocatori")
    log(f"Coefficiente: {corr:.4f}")
    log(f"P-value:      {p_value:.4f}")
    log("="*60 + "\n")



def analyze_session_pity(players_sessions, output_dir=None):
    if output_dir is None:
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
        f.write("RIEPILOGO:\n")
        f.write(f"Totale Player Analizzati: {total_tested}\n")
        f.write(f"Player con P-value < 0.05: {global_significant}\n")
        if total_tested > 0:
            f.write(f"Percentuale Significativi: {(global_significant/total_tested)*100:.2f}%\n")
        f.write("="*80 + "\n")


def analyze_std_correlation(players_sessions, output_dir=None):
    f = None
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, 'std_correlation_results.txt')
        print(f"\nGenerazione report correlazione deviazione standard in: {output_file}")
        f = open(output_file, "w", encoding="utf-8")

    try:
        data = []
        for player_sessions in players_sessions:
            long_sessions = [s for s in player_sessions['sessions'] if len(s['battles']) >= 3]

            if not long_sessions or len(long_sessions) < 3:
                continue

            avg_matchup = [s['analysis']['avg_matchup'] for s in long_sessions]
            std_matchups = statistics.stdev(avg_matchup)
            profile = player_sessions.get('profile')
            fsi = profile.get('avg_fsi', 0) if profile else 0

            msg = f"Player: {player_sessions['tag']}     -     std_dev: {std_matchups:.2f}"
            if f: 
                f.write(msg + "\n")
            else: 
                print(msg)

            data.append({
                'tag': player_sessions['tag'],
                'std_dev': std_matchups,
                'fsi': fsi
            })
            
        calculate_variance_ratio(data, f)
        calculate_fsi_variance_correlation(data, f)
    finally:
        if f: 
            f.close()


def analyze_extreme_matchup_streak(players_sessions, output_dir=None, use_no_lvl=False):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)

    if use_no_lvl:
        output_file = os.path.join(output_dir, 'extreme_matchup_streak_no_lvl_results.txt')
        report_title = "ANALISI STREAK MATCHUP ESTREMI (NO-LVL) (>= 3 consecutivi in sessione)\n"
        matchup_key = 'matchup_no_lvl'
        print(f"\nGenerazione report streak matchup estremi (NO-LVL) in: {output_file}")
    else:
        output_file = os.path.join(output_dir, 'extreme_matchup_streak_results.txt')
        report_title = "ANALISI STREAK MATCHUP ESTREMI (REALE) (>= 3 consecutivi in sessione)\n"
        matchup_key = 'matchup'
        print(f"\nGenerazione report streak matchup estremi (REALE) in: {output_file}")

    # Soglie
    HIGH_THRESH = 80.0
    LOW_THRESH = 30.0
    STREAK_LEN = 3
    NUM_SIMULATIONS = 10000

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
            mus = [b.get(matchup_key) for b in session['battles'] if b.get(matchup_key) is not None and (b['game_mode'] == 'Ladder' or b['game_mode'] == 'Ranked')]
            if not mus: 
                continue
            
            p_matchups.extend(mus)
            p_lengths.append(len(mus))
            
            # Stats per Teorico
            for m in mus:
                total_battles += 1
                if m > HIGH_THRESH: 
                    count_high += 1
                elif m < LOW_THRESH: 
                    count_low += 1
            
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
        f.write(report_title)
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

def analyze_confounding_factors(players_sessions, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'confounding_factors_results.txt')

    print(f"\nGenerazione report fattori confondenti (Orario/Trofei/Deck) in: {output_file}")

    # Configurazione Metriche
    metrics_config = [
        {'name': 'Matchup (Reale)', 'key': 'matchup', 'high': 80.0, 'low': 40.0},
        {'name': 'Matchup (No-Lvl)', 'key': 'matchup_no_lvl', 'high': 80.0, 'low': 40.0},
        {'name': 'Level Diff', 'key': 'level_diff', 'high': 0.5, 'low': -0.5}
    ]
    
    STREAK_LEN = 3
    TROPHY_BUCKET = 1000
    time_slots = {0: "Notte (00-06)", 1: "Mattina (06-12)", 2: "Pomeriggio (12-18)", 3: "Sera (18-24)"}

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI FATTORI CONFONDENTI: ORARIO, TROFEI, DECK\n")
        f.write("Obiettivo: Verificare se la probabilità di STREAK (serie di matchup estremi) dipende da fattori esterni.\n")
        f.write("Ipotesi Nulla: Le streak sono distribuite uniformemente rispetto a orario, trofei e mazzo.\n")
        f.write("="*80 + "\n\n")

        for metric in metrics_config:
            m_name = metric['name']
            m_key = metric['key']
            high_thresh = metric['high']
            low_thresh = metric['low']
            
            f.write(f"{'='*80}\n")
            f.write(f"METRICA: {m_name}\n")
            f.write(f"Soglie Streak ({STREAK_LEN} match): High > {high_thresh}, Low < {low_thresh}\n")
            f.write(f"{'='*80}\n\n")

            # Reset Stats per metrica
            time_stats = {k: {'total': 0, 'streak': 0} for k in time_slots}
            trophy_stats = {} # bucket -> {'total': 0, 'streak': 0}
            
            deck_independence_count = 0
            deck_total_tested = 0

            for p in players_sessions:
                nationality = p.get('nationality')
                # Per analisi Deck del singolo player
                # DeckID -> {'total': 0, 'streak': 0}
                player_deck_stats = {}

                for session in p['sessions']:
                    battles = [b for b in session['battles'] if b['game_mode'] == 'Ladder' or b['game_mode'] == 'Ranked']
                    if len(battles) < STREAK_LEN: continue

                    for i in range(len(battles) - STREAK_LEN + 1):
                        window = battles[i : i+STREAK_LEN]
                        values = [b.get(m_key) for b in window]
                        
                        # Skip windows with missing values
                        if any(v is None for v in values): continue

                        # Dati finestra
                        first_b = window[0]
                        
                        # --- TIME ---
                        slot = None
                        if 'timestamp' in first_b:
                            h = get_local_hour(first_b['timestamp'], nationality)
                            if 6 <= h < 12: slot = 1
                            elif 12 <= h < 18: slot = 2
                            elif 18 <= h < 24: slot = 3
                            else: slot = 0

                        # --- TROPHIES ---
                        t = first_b.get('trophies_before')
                        bucket = (t // TROPHY_BUCKET) * TROPHY_BUCKET if t else None

                        # --- DECK ---
                        deck_id = first_b.get('deck_id')

                        # Determina se è Streak (High o Low)
                        is_streak = all(v > high_thresh for v in values) or all(v < low_thresh for v in values)

                        # Update Time
                        if slot is not None:
                            time_stats[slot]['total'] += 1
                            if is_streak: time_stats[slot]['streak'] += 1
                        
                        # Update Trophies
                        if bucket is not None:
                            if bucket not in trophy_stats: trophy_stats[bucket] = {'total': 0, 'streak': 0}
                            trophy_stats[bucket]['total'] += 1
                            if is_streak: trophy_stats[bucket]['streak'] += 1

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

            # --- REPORTING PER METRICA ---

            # 1. TIME
            f.write("1. ANALISI ORARIA (Globale)\n")
            f.write(f"{'Fascia Oraria':<25} | {'Tot Finestre':<15} | {'Streak':<10} | {'Rate %':<10}\n")
            f.write("-" * 70 + "\n")
            
            time_obs = []
            for slot in sorted(time_slots.keys()):
                s = time_stats[slot]
                rate = (s['streak'] / s['total'] * 100) if s['total'] > 0 else 0
                f.write(f"{time_slots[slot]:<25} | {s['total']:<15} | {s['streak']:<10} | {rate:<10.2f}%\n")
                if s['total'] > 0:
                    time_obs.append([s['streak'], s['total'] - s['streak']])
            
            if len(time_obs) >= 2:
                try:
                    chi2, p, _, _ = chi2_contingency(time_obs)
                    res = "DIPENDENTE (L'orario influisce)" if p < 0.05 else "INDIPENDENTE (L'orario NON influisce)"
                    f.write(f"\nTest Chi-Quadro: p-value = {p:.4f} -> {res}\n")
                except:
                    f.write("\nTest Chi-Quadro: Errore (Dati insufficienti)\n")
            f.write("\n")

            # 2. TROPHIES
            f.write("2. ANALISI TROFEI (Globale)\n")
            f.write(f"{'Fascia Trofei':<25} | {'Tot Finestre':<15} | {'Streak':<10} | {'Rate %':<10}\n")
            f.write("-" * 70 + "\n")
            
            trophy_obs = []
            for bucket in sorted(trophy_stats.keys()):
                s = trophy_stats[bucket]
                if s['total'] < 50: continue # Skip low sample buckets
                rate = (s['streak'] / s['total'] * 100) if s['total'] > 0 else 0
                label = f"{bucket}-{bucket+TROPHY_BUCKET}"
                f.write(f"{label:<25} | {s['total']:<15} | {s['streak']:<10} | {rate:<10.2f}%\n")
                trophy_obs.append([s['streak'], s['total'] - s['streak']])
                
            if len(trophy_obs) >= 2:
                try:
                    chi2, p, _, _ = chi2_contingency(trophy_obs)
                    res = "DIPENDENTE (I trofei influiscono)" if p < 0.05 else "INDIPENDENTE (I trofei NON influiscono)"
                    f.write(f"\nTest Chi-Quadro: p-value = {p:.4f} -> {res}\n")
                except:
                    f.write("\nTest Chi-Quadro: Errore (Dati insufficienti)\n")
            f.write("\n")

            # 3. DECK
            f.write("3. ANALISI DECK (Aggregata per Player)\n")
            f.write("Verifica se la probabilità di streak cambia cambiando mazzo (tra i mazzi più usati).\n")
            f.write("-" * 80 + "\n")
            f.write(f"Player analizzati (con almeno 2 mazzi usati >10 volte): {deck_total_tested}\n")
            f.write(f"Player con streak INDIPENDENTI dal mazzo (p > 0.05):    {deck_independence_count}\n")
            perc = (deck_independence_count / deck_total_tested * 100) if deck_total_tested > 0 else 0
            f.write(f"Percentuale Indipendenza: {perc:.2f}%\n")
            f.write("="*80 + "\n\n")

def analyze_deck_switch_impact(players_sessions, output_dir=None):
    if output_dir is None:
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

    # Traiettorie Post-Evento (per vedere se il sistema si riadatta)
    LOOKAHEAD = 4
    trajectories = {
        True: {k: [] for k in range(1, LOOKAHEAD + 1)},
        False: {k: [] for k in range(1, LOOKAHEAD + 1)}
    }
    trajectories_lvl = {
        True: {k: [] for k in range(1, LOOKAHEAD + 1)},
        False: {k: [] for k in range(1, LOOKAHEAD + 1)}
    }

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI IMPATTO CAMBIO DECK (ARCHETIPO) SUL PATTERN MATCHUP (NO-LVL)\n")
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
                
                mu_curr = b_curr.get('matchup_no_lvl')
                mu_next = b_next.get('matchup_no_lvl')
                
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
                
                # --- Analisi Traiettoria (Solo se partiamo da Bad Matchup) ---
                if zone_curr == 'Bad':
                    target_deck_id = id_next # Il mazzo usato al passo i+1
                    
                    for k in range(1, LOOKAHEAD + 1):
                        idx_future = i + k
                        if idx_future >= len(all_battles): break
                        
                        b_future = all_battles[idx_future]
                        mu_future = b_future.get('matchup_no_lvl')
                        lvl_future = b_future.get('level_diff')
                        id_future = b_future.get('archetype_id') or b_future.get('deck_id')
                        
                        if mu_future is None or id_future is None: break
                        if id_future != target_deck_id: break # Deck cambiato di nuovo
                        
                        trajectories[is_switch][k].append(mu_future)
                        if lvl_future is not None:
                            trajectories_lvl[is_switch][k].append(lvl_future)

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
        
        f.write("\n" + "="*80 + "\n")
        f.write("ANALISI ADATTAMENTO SISTEMA (TRAIETTORIA POST-SWITCH)\n")
        f.write("Domanda: Dopo aver cambiato mazzo per sfuggire a un counter, quanto dura l'effetto benefico?\n")
        f.write("         Il sistema si 'riadatta' (matchup peggiora) dopo qualche partita?\n")
        f.write("-" * 80 + "\n")
        f.write(f"{'Step':<10} | {'NO SWITCH (Avg MU)':<20} | {'SWITCH (Avg MU)':<20} | {'N. Switch':<10}\n")
        f.write("-" * 80 + "\n")
        
        for k in range(1, LOOKAHEAD + 1):
            vals_no = trajectories[False][k]
            vals_sw = trajectories[True][k]
            
            avg_no = statistics.mean(vals_no) if vals_no else 0
            avg_sw = statistics.mean(vals_sw) if vals_sw else 0
            count_sw = len(vals_sw)
            
            f.write(f"+{k} Match  | {avg_no:<20.2f}% | {avg_sw:<20.2f}% | {count_sw:<10}\n")
            
        f.write("-" * 80 + "\n")
        f.write("INTERPRETAZIONE:\n")
        f.write("1. Se SWITCH parte alto (es. >50%) e scende nei match successivi (+2, +3),\n")
        f.write("   potrebbe indicare che il sistema sta ricalibrando il matchmaking sul nuovo mazzo.\n")
        f.write("2. Se SWITCH rimane costantemente alto rispetto a NO SWITCH, il cambio è efficace a lungo termine.\n")
        f.write("="*80 + "\n")
        
        f.write("\n" + "="*80 + "\n")
        f.write("ANALISI ADATTAMENTO LIVELLI (TRAIETTORIA POST-SWITCH)\n")
        f.write("Domanda: Se cambio mazzo, il sistema mi punisce con livelli più alti (Level Diff più negativo)?\n")
        f.write("-" * 80 + "\n")
        f.write(f"{'Step':<10} | {'NO SWITCH (Avg Lvl)':<20} | {'SWITCH (Avg Lvl)':<20} | {'N. Switch':<10}\n")
        f.write("-" * 80 + "\n")
        
        for k in range(1, LOOKAHEAD + 1):
            vals_no = trajectories_lvl[False][k]
            vals_sw = trajectories_lvl[True][k]
            
            avg_no = statistics.mean(vals_no) if vals_no else 0
            avg_sw = statistics.mean(vals_sw) if vals_sw else 0
            count_sw = len(vals_sw)
            
            f.write(f"+{k} Match  | {avg_no:<20.2f} | {avg_sw:<20.2f} | {count_sw:<10}\n")
            
        f.write("-" * 80 + "\n")
        f.write("INTERPRETAZIONE:\n")
        f.write("1. Level Diff negativo = Avversario più forte (Svantaggio).\n")
        f.write("2. Se SWITCH ha valori più negativi di NO SWITCH, il sistema compensa il cambio mazzo con livelli più alti.\n")
        f.write("="*80 + "\n")


def analyze_ers_pity_hypothesis(profiles, matchup_stats, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'ers_pity_hypothesis_results.txt')

    print(f"\nGenerazione report ipotesi ERS -> Pity in: {output_file}")
    
    # Data collection
    data_points = []
    for tag, profile in profiles.items():
        if tag not in matchup_stats:
            continue
            
        ers = profile.get('ers')
        total_matches = profile.get('total_matches', 0)
        pity_stats = matchup_stats[tag].get('pity', {})
        pity_odds = pity_stats.get('odds_ratio')
        
        # Filtra valori validi
        if ers is not None and pity_odds is not None and not (isinstance(pity_odds, float) and (np.isnan(pity_odds) or np.isinf(pity_odds))):
             data_points.append({'tag': tag, 'ers': ers, 'pity_odds': pity_odds, 'total_matches': total_matches})
             
    if len(data_points) < 4:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("Dati insufficienti per l'analisi (serve un campione più ampio).")
        return

    # Sort by ERS
    data_points.sort(key=lambda x: x['ers'])
    
    mid = len(data_points) // 2
    low_ers_group = data_points[:mid]
    high_ers_group = data_points[mid:]
    
    low_pity_values = [x['pity_odds'] for x in low_ers_group]
    high_pity_values = [x['pity_odds'] for x in high_ers_group]
    
    low_matches = [x['total_matches'] for x in low_ers_group]
    high_matches = [x['total_matches'] for x in high_ers_group]

    avg_low = statistics.mean(low_pity_values) if low_pity_values else 0
    avg_high = statistics.mean(high_pity_values) if high_pity_values else 0
    
    # Mann-Whitney U Test (Non parametrico)
    # Ipotesi Alternativa 'greater': High ERS Pity > Low ERS Pity
    stat, p_value = mannwhitneyu(high_pity_values, low_pity_values, alternative='greater')
    
    # --- Analisi Correlazione Parziale (Controllo Confounding) ---
    ers_vals = [x['ers'] for x in data_points]
    pity_vals = [x['pity_odds'] for x in data_points]
    matches_vals = [x['total_matches'] for x in data_points]

    r_xy, p_xy = spearmanr(ers_vals, pity_vals)     # ERS vs Pity
    r_xz, p_xz = spearmanr(ers_vals, matches_vals)  # ERS vs Matches
    r_yz, p_yz = spearmanr(pity_vals, matches_vals) # Pity vs Matches

    # Partial Correlation: r_xy.z
    denom = math.sqrt((1 - r_xz**2) * (1 - r_yz**2))
    r_partial = (r_xy - (r_xz * r_yz)) / denom if denom != 0 else 0

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI IPOTESI: ERS ALTO -> AUMENTO PITY ODDS\n")
        f.write("Obiettivo: Verificare se i giocatori con ERS alto (Engagement Resilience Score) ricevono più 'aiuti' (Pity Match) dopo le sconfitte.\n")
        f.write("="*80 + "\n\n")
        
        f.write(f"Totale Giocatori Validi: {len(data_points)}\n")
        f.write(f"Soglia ERS (Mediana): {data_points[mid]['ers']:.3f}\n")
        f.write("-" * 80 + "\n")
        
        f.write(f"{'GRUPPO':<20} | {'N':<5} | {'AVG PITY ODDS':<15} | {'AVG MATCHES':<15} | {'RANGE ERS':<20}\n")
        f.write("-" * 80 + "\n")
        
        f.write(f"{'LOW ERS':<20} | {len(low_ers_group):<5} | {avg_low:<15.4f} | {statistics.mean(low_matches):<15.1f} | {low_ers_group[0]['ers']:.3f} - {low_ers_group[-1]['ers']:.3f}\n")
        f.write(f"{'HIGH ERS':<20} | {len(high_ers_group):<5} | {avg_high:<15.4f} | {statistics.mean(high_matches):<15.1f} | {high_ers_group[0]['ers']:.3f} - {high_ers_group[-1]['ers']:.3f}\n")
        
        f.write("-" * 80 + "\n")
        f.write("TEST STATISTICO (Mann-Whitney U):\n")
        f.write("Ipotesi Alternativa: Pity Odds (High ERS) > Pity Odds (Low ERS)\n")
        f.write(f"U-statistic: {stat}\n")
        f.write(f"P-value:     {p_value:.4f}\n\n")
        
        if p_value < 0.05:
            f.write("RISULTATO: SIGNIFICATIVO. I giocatori con ERS alto sembrano ricevere sistematicamente più Pity Match.\n")
        else:
            f.write("RISULTATO: NON SIGNIFICATIVO. Non c'è evidenza statistica sufficiente per confermare l'ipotesi.\n")
        
        f.write("-" * 80 + "\n")
        f.write("CONTROLLO VARIABILE CONFONDENTE (Numero Partite):\n")
        f.write(f"Correlazione Pity vs Matches (r_yz):   {r_yz:.4f} (p={p_yz:.4f})\n")
        f.write(f"Correlazione ERS vs Matches (r_xz):    {r_xz:.4f} (p={p_xz:.4f})\n")
        f.write(f"Correlazione Diretta (ERS vs Pity):    {r_xy:.4f}\n")
        f.write(f"Correlazione Parziale (Netta):         {r_partial:.4f}\n")
        if abs(r_partial) < abs(r_xy) * 0.5:
            f.write("WARNING: La correlazione sembra spiegata in gran parte dal numero di partite.\n")

        f.write("="*80 + "\n")


def analyze_return_matchups_vs_ers(players_sessions, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'return_matchup_ers_results.txt')

    print(f"\nGenerazione report Return Matchup vs ERS in: {output_file}")

    data_points = []

    for p in players_sessions:
        tag = p['tag']
        profile = p['profile']
        sessions = p['sessions']
        
        if not profile:
            continue
            
        ers = profile.get('ers')
        if ers is None:
            continue

        return_matchups = []
        # Itera sulle sessioni per trovare i "ritorni"
        # Se la sessione i finisce con Long o Quit, la sessione i+1 è un "ritorno"
        for i in range(len(sessions) - 1):
            stop_type = sessions[i]['stop_type']
            if stop_type in ['Long', 'Quit']:
                # Controlla la prima battaglia della sessione successiva
                next_session = sessions[i+1]
                if next_session['battles']:
                    first_b = next_session['battles'][0]
                    if first_b['matchup'] is not None:
                        return_matchups.append(first_b['matchup'])
        
        if return_matchups:
            avg_return_mu = statistics.mean(return_matchups)
            data_points.append({
                'tag': tag,
                'ers': ers,
                'avg_return_mu': avg_return_mu,
                'count': len(return_matchups)
            })

    if len(data_points) < 4:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("Dati insufficienti per l'analisi.")
        return

    # Sort by ERS
    data_points.sort(key=lambda x: x['ers'])
    
    mid = len(data_points) // 2
    low_ers = data_points[:mid]
    high_ers = data_points[mid:]
    
    vals_low = [x['avg_return_mu'] for x in low_ers]
    vals_high = [x['avg_return_mu'] for x in high_ers]
    
    avg_low = statistics.mean(vals_low) if vals_low else 0
    avg_high = statistics.mean(vals_high) if vals_high else 0
    
    # Mann-Whitney U (High ERS > Low ERS?)
    stat, p_value = mannwhitneyu(vals_high, vals_low, alternative='greater')
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI: ERS vs MATCHUP AL RITORNO (Dopo Long/Quit)\n")
        f.write("Ipotesi: I giocatori con alto ERS ricevono matchup migliori quando ritornano a giocare?\n")
        f.write("="*80 + "\n\n")
        
        f.write(f"Totale Giocatori: {len(data_points)}\n")
        f.write(f"Soglia ERS (Mediana): {data_points[mid]['ers']:.3f}\n")
        f.write("-" * 80 + "\n")
        
        f.write(f"{'GRUPPO':<20} | {'N':<5} | {'AVG RETURN MU':<15} | {'RANGE ERS':<20}\n")
        f.write("-" * 80 + "\n")
        f.write(f"{'LOW ERS':<20} | {len(low_ers):<5} | {avg_low:<15.2f}% | {low_ers[0]['ers']:.3f} - {low_ers[-1]['ers']:.3f}\n")
        f.write(f"{'HIGH ERS':<20} | {len(high_ers):<5} | {avg_high:<15.2f}% | {high_ers[0]['ers']:.3f} - {high_ers[-1]['ers']:.3f}\n")
        
        f.write("-" * 80 + "\n")
        f.write("TEST STATISTICO (Mann-Whitney U):\n")
        f.write(f"Ipotesi Alternativa: Return Matchup (High ERS) > Return Matchup (Low ERS)\n")
        f.write(f"P-value: {p_value:.4f}\n")
        f.write(f"Risultato: {'SIGNIFICATIVO (Retention EOMM Probabile)' if p_value < 0.05 else 'Non significativo'}\n")
        
        f.write("="*80 + "\n")


def analyze_pity_impact_on_session_length(players_sessions, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'pity_impact_on_session_length.txt')

    print(f"\nGenerazione report Impatto Pity su Durata Sessione in: {output_file}")

    # Struttura dati: event_type -> { 'pity': [remaining_matches], 'no_pity': [remaining_matches] }
    distributions = {
        'Loss': {'pity': [], 'no_pity': []},
        'Loss Streak (>=2)': {'pity': [], 'no_pity': []},
        'Loss Streak (>=3)': {'pity': [], 'no_pity': []},
        'Counter (Loss <40%)': {'pity': [], 'no_pity': []},
        'Counter Streak (>=2)': {'pity': [], 'no_pity': []},
        'Counter Streak (>=3)': {'pity': [], 'no_pity': []}
    }
    
    PITY_THRESH = 60.0
    BAD_MU_THRESH = 40.0

    for p in players_sessions:
        for session in p['sessions']:
            battles = session['battles']
            n_battles = len(battles)
            if n_battles < 2: 
                continue
            
            # Iteriamo fino al penultimo, perché dobbiamo guardare il "next match"
            for i in range(n_battles - 1):
                curr = battles[i]
                next_b = battles[i+1]
                
                # Se il prossimo match non ha dati matchup, saltiamo
                if next_b['matchup'] is None:
                    continue
                
                is_next_pity = next_b['matchup'] > PITY_THRESH
                group_key = 'pity' if is_next_pity else 'no_pity'
                
                # Calcolo partite rimanenti (inclusa la next_b)
                # Se siamo a i, e lunghezza è N. i va da 0 a N-2.
                # Remaining = (N - 1) - i. 
                # Es: N=10. i=8 (penultimo). Next=9 (ultimo). Remaining = 1.
                remaining = (n_battles - 1) - i
                
                # --- Identificazione Eventi di Rischio ---
                
                # 1. Loss
                if curr['win'] == 0:
                    distributions['Loss'][group_key].append(remaining)
                    
                    # Loss Streak Logic
                    # Controlliamo se anche la precedente (i-1) era loss
                    if i > 0 and battles[i-1]['win'] == 0:
                        distributions['Loss Streak (>=2)'][group_key].append(remaining)
                        
                        if i > 1 and battles[i-2]['win'] == 0:
                            distributions['Loss Streak (>=3)'][group_key].append(remaining)
                    
                    # Counter Logic (Loss + Bad Matchup)
                    if curr['matchup'] is not None and curr['matchup'] < BAD_MU_THRESH:
                        distributions['Counter (Loss <40%)'][group_key].append(remaining)
                        
                        # Counter Streak Logic
                        if i > 0 and battles[i-1]['win'] == 0 and battles[i-1]['matchup'] is not None and battles[i-1]['matchup'] < BAD_MU_THRESH:
                            distributions['Counter Streak (>=2)'][group_key].append(remaining)
                            
                            if i > 1 and battles[i-2]['win'] == 0 and battles[i-2]['matchup'] is not None and battles[i-2]['matchup'] < BAD_MU_THRESH:
                                distributions['Counter Streak (>=3)'][group_key].append(remaining)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI IMPATTO PITY MATCH SU DURATA SESSIONE (RETENTION)\n")
        f.write("Obiettivo: Capire se ricevere un Pity Match dopo un evento negativo estende la sessione.\n")
        f.write(f"Definizione Pity Match: Matchup > {PITY_THRESH}%\n")
        f.write("="*80 + "\n\n")
        
        for event_name, groups in distributions.items():
            pity_vals = groups['pity']
            nopity_vals = groups['no_pity']
            
            f.write(f"--- EVENTO: {event_name} ---\n")
            if len(pity_vals) < 10 or len(nopity_vals) < 10:
                f.write("Dati insufficienti per questo evento.\n\n")
                continue
                
            avg_pity = statistics.mean(pity_vals)
            avg_nopity = statistics.mean(nopity_vals)
            
            # Mann-Whitney U Test (Greater: Pity > NoPity)
            stat, p_val = mannwhitneyu(pity_vals, nopity_vals, alternative='greater')
            
            f.write(f"{'Gruppo':<15} | {'N':<8} | {'Avg Remaining Matches':<25}\n")
            f.write("-" * 55 + "\n")
            f.write(f"{'Con Pity':<15} | {len(pity_vals):<8} | {avg_pity:<25.2f}\n")
            f.write(f"{'Senza Pity':<15} | {len(nopity_vals):<8} | {avg_nopity:<25.2f}\n")
            f.write("-" * 55 + "\n")
            f.write(f"Test Mann-Whitney U (Pity > NoPity):\n")
            f.write(f"P-value: {p_val:.4f}\n")
            
            if p_val < 0.05:
                f.write("RISULTATO: SIGNIFICATIVO. Il Pity Match estende la sessione.\n")
            else:
                f.write("RISULTATO: NON SIGNIFICATIVO.\n")
            f.write("\n")
        f.write("="*80 + "\n")


def analyze_pity_impact_on_return_time(players_sessions, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'pity_impact_on_return_time.txt')

    print(f"\nGenerazione report Impatto Pity su Tempo di Ritorno in: {output_file}")

    # Struttura dati: event_type -> { 'pity': [return_seconds], 'no_pity': [return_seconds] }
    distributions = {
        'Loss': {'pity': [], 'no_pity': []},
        'Loss Streak (>=2)': {'pity': [], 'no_pity': []},
        'Loss Streak (>=3)': {'pity': [], 'no_pity': []},
        'Counter (Loss <40%)': {'pity': [], 'no_pity': []},
        'Counter Streak (>=2)': {'pity': [], 'no_pity': []},
        'Counter Streak (>=3)': {'pity': [], 'no_pity': []}
    }
    
    PITY_THRESH = 60.0
    BAD_MU_THRESH = 40.0

    for p in players_sessions:
        for session in p['sessions']:
            # Saltiamo l'ultima sessione che non ha un tempo di ritorno definito
            if session.get('break_duration_seconds') is None:
                continue
                
            return_time = session['break_duration_seconds']
            battles = session['battles']
            n_battles = len(battles)
            
            if n_battles < 2: 
                continue
            
            # Iteriamo fino al penultimo
            for i in range(n_battles - 1):
                curr = battles[i]
                next_b = battles[i+1]
                
                if next_b['matchup'] is None:
                    continue
                
                is_next_pity = next_b['matchup'] > PITY_THRESH
                group_key = 'pity' if is_next_pity else 'no_pity'
                
                # --- Identificazione Eventi di Rischio ---
                if curr['win'] == 0:
                    distributions['Loss'][group_key].append(return_time)
                    
                    if i > 0 and battles[i-1]['win'] == 0:
                        distributions['Loss Streak (>=2)'][group_key].append(return_time)
                        
                        if i > 1 and battles[i-2]['win'] == 0:
                            distributions['Loss Streak (>=3)'][group_key].append(return_time)
                    
                    if curr['matchup'] is not None and curr['matchup'] < BAD_MU_THRESH:
                        distributions['Counter (Loss <40%)'][group_key].append(return_time)
                        
                        if i > 0 and battles[i-1]['win'] == 0 and battles[i-1]['matchup'] is not None and battles[i-1]['matchup'] < BAD_MU_THRESH:
                            distributions['Counter Streak (>=2)'][group_key].append(return_time)
                            
                            if i > 1 and battles[i-2]['win'] == 0 and battles[i-2]['matchup'] is not None and battles[i-2]['matchup'] < BAD_MU_THRESH:
                                distributions['Counter Streak (>=3)'][group_key].append(return_time)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI IMPATTO PITY MATCH SU TEMPO DI RITORNO (PREVENZIONE RAGEQUIT)\n")
        f.write("Obiettivo: Capire se ricevere un Pity Match riduce il tempo di pausa prima della sessione successiva.\n")
        f.write(f"Definizione Pity Match: Matchup > {PITY_THRESH}%\n")
        f.write("="*80 + "\n\n")
        
        for event_name, groups in distributions.items():
            pity_vals = groups['pity']
            nopity_vals = groups['no_pity']
            
            f.write(f"--- EVENTO: {event_name} ---\n")
            if len(pity_vals) < 10 or len(nopity_vals) < 10:
                f.write("Dati insufficienti per questo evento.\n\n")
                continue
            
            # Convertiamo in ore per leggibilità
            avg_pity = (statistics.mean(pity_vals) / 3600)
            avg_nopity = (statistics.mean(nopity_vals) / 3600)
            
            # Mann-Whitney U Test (Less: Pity < NoPity -> Return Faster)
            stat, p_val = mannwhitneyu(pity_vals, nopity_vals, alternative='less')
            
            f.write(f"{'Gruppo':<15} | {'N':<8} | {'Avg Return Time (Ore)':<25}\n")
            f.write("-" * 55 + "\n")
            f.write(f"{'Con Pity':<15} | {len(pity_vals):<8} | {avg_pity:<25.2f}\n")
            f.write(f"{'Senza Pity':<15} | {len(nopity_vals):<8} | {avg_nopity:<25.2f}\n")
            f.write("-" * 55 + "\n")
            f.write(f"Test Mann-Whitney U (Pity < NoPity):\n")
            f.write(f"P-value: {p_val:.4f}\n")
            
            if p_val < 0.05:
                f.write("RISULTATO: SIGNIFICATIVO. Il Pity Match riduce il tempo di assenza (Retention).\n")
            else:
                f.write("RISULTATO: NON SIGNIFICATIVO.\n")
            f.write("\n")
        f.write("="*80 + "\n")


def analyze_churn_probability_vs_pity(players_sessions, matchup_stats, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'churn_probability_vs_pity_results.txt')

    print(f"\nGenerazione report Probabilità Churn vs Pity in: {output_file}")

    # 1. Trova l'ultimo timestamp globale (approssimazione di "Oggi" nel dataset)
    max_ts = 0
    player_last_ts = {}

    for p in players_sessions:
        tag = p['tag']
        sessions = p['sessions']
        if not sessions:
            continue
        
        # L'ultima sessione è l'ultima della lista
        last_session = sessions[-1]
        if not last_session['battles']:
            continue
            
        last_battle = last_session['battles'][-1]
        ts_str = last_battle['timestamp']
        # Converti stringa in timestamp
        dt = datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S')
        ts = dt.timestamp()
        
        if ts > max_ts:
            max_ts = ts
        
        player_last_ts[tag] = ts

    # Soglia Churn: 3 giorni (in secondi)
    CHURN_THRESHOLD = 3 * 24 * 60 * 60
    
    churned_pity = []
    active_pity = []

    for tag, last_ts in player_last_ts.items():
        if tag not in matchup_stats:
            continue
            
        pity_stats = matchup_stats[tag].get('pity', {})
        pity_odds = pity_stats.get('odds_ratio')
        
        if pity_odds is None or math.isnan(pity_odds) or math.isinf(pity_odds):
            continue
            
        is_churned = (max_ts - last_ts) > CHURN_THRESHOLD
        
        if is_churned:
            churned_pity.append(pity_odds)
        else:
            active_pity.append(pity_odds)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI PROBABILITÀ CHURN vs PITY ODDS\n")
        f.write("Obiettivo: Verificare se i giocatori con Pity Odds più alti hanno meno probabilità di abbandonare il gioco (Churn).\n")
        f.write(f"Definizione Churn: Assenza > 3 giorni rispetto all'ultimo dato globale ({datetime.fromtimestamp(max_ts)}).\n")
        f.write("="*80 + "\n\n")
        
        if len(churned_pity) < 5 or len(active_pity) < 5:
            f.write(f"numero churned pity: {len(churned_pity)}\n")
            f.write(f"numero active pity: {len(active_pity)}\n")
            f.write("Dati insufficienti per l'analisi Churn (pochi giocatori attivi o churned nel campione).\n")
            return

        avg_churned = statistics.mean(churned_pity)
        avg_active = statistics.mean(active_pity)
        
        # Mann-Whitney U Test
        # Ipotesi Alternativa 'greater': Active Pity > Churned Pity
        # Se significativo, significa che chi rimane attivo riceve più "aiuti" di chi se ne va.
        stat, p_value = mannwhitneyu(active_pity, churned_pity, alternative='greater')
        
        f.write(f"{'GRUPPO':<20} | {'N':<5} | {'AVG PITY ODDS':<15}\n")
        f.write("-" * 50 + "\n")
        f.write(f"{'CHURNED (Inactive)':<20} | {len(churned_pity):<5} | {avg_churned:<15.4f}\n")
        f.write(f"{'ACTIVE':<20} | {len(active_pity):<5} | {avg_active:<15.4f}\n")
        
        f.write("-" * 50 + "\n")
        f.write("TEST STATISTICO (Mann-Whitney U):\n")
        f.write(f"Ipotesi Alternativa: Pity Odds (Active) > Pity Odds (Churned)\n")
        f.write(f"P-value: {p_value:.4f}\n\n")
        
        if p_value < 0.05:
            f.write("RISULTATO: SIGNIFICATIVO. I giocatori attivi hanno Pity Odds significativamente più alti dei giocatori che hanno abbandonato.\n")
            f.write("INTERPRETAZIONE: Il Pity Match potrebbe essere un fattore di protezione efficace contro l'abbandono definitivo.\n")
        else:
            f.write("RISULTATO: NON SIGNIFICATIVO. Non sembra esserci evidenza che i Pity Odds influenzino la probabilità di abbandono.\n")
            
        f.write("="*80 + "\n")


def analyze_cannon_fodder(players_sessions, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'cannon_fodder_results.txt')
    
    print(f"\nGenerazione report Cannon Fodder (Dynamic Stress Analysis) in: {output_file}")
    
    # Grouped data
    low_stress_matchups = []  # Stress == 0 (Low Risk)
    high_stress_matchups = [] # Stress >= 2.0 (High Risk)
    
    all_stress = []
    all_matchups = []
    
    for p in players_sessions:
        for s in p['sessions']:
            battles = s['battles']
            
            # Initialize Session State (Replicating battlelog_v2 logic)
            current_stress = 0.0
            current_win_streak = 0
            
            for b in battles:
                # 1. Analyze State BEFORE this battle
                if b['matchup'] is not None:
                    all_stress.append(current_stress)
                    all_matchups.append(b['matchup'])
                    
                    if current_stress <= 0.1: # Essentially 0
                        low_stress_matchups.append(b['matchup'])
                    elif current_stress >= 2.0: # High pressure
                        high_stress_matchups.append(b['matchup'])
                
                # 2. Update State based on this battle outcome
                is_win = (b['win'] == 1)
                
                if is_win:
                    current_win_streak += 1
                    stress_reduction = 2.0 * current_win_streak
                    current_stress = max(0.0, current_stress - stress_reduction)
                else:
                    current_win_streak = 0
                    battle_stress = 1.0
                    
                    if b['matchup'] is not None:
                        if b['matchup'] < 45.0:
                            battle_stress += 0.5
                        if b['matchup'] < 35.0:
                            battle_stress += 0.5
                            
                    current_stress += battle_stress

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI CANNON FODDER: DYNAMIC STRESS vs MATCHUP\n")
        f.write("Ipotesi: Quando il giocatore è a 'Basso Rischio Quit' (Stress Basso), riceve matchup peggiori?\n")
        f.write("Metodo: Calcolo dello Stress cumulativo partita per partita all'interno della sessione.\n")
        f.write("="*80 + "\n\n")
        
        f.write(f"Totale Partite Analizzate: {len(all_matchups)}\n")
        f.write(f"Partite in Low Stress (<=0.1): {len(low_stress_matchups)}\n")
        f.write(f"Partite in High Stress (>=2.0): {len(high_stress_matchups)}\n")
        f.write("-" * 80 + "\n")
        
        avg_low = statistics.mean(low_stress_matchups) if low_stress_matchups else 0
        avg_high = statistics.mean(high_stress_matchups) if high_stress_matchups else 0
        
        f.write(f"{'STATO':<20} | {'AVG MATCHUP':<15}\n")
        f.write("-" * 40 + "\n")
        f.write(f"{'LOW STRESS (Safe)':<20} | {avg_low:<15.2f}%\n")
        f.write(f"{'HIGH STRESS (Risk)':<20} | {avg_high:<15.2f}%\n")
        
        # Mann-Whitney U Test
        # Alternative 'less': Low Stress < High Stress (Cannon Fodder Hypothesis)
        stat, p_val = mannwhitneyu(low_stress_matchups, high_stress_matchups, alternative='less')
        
        f.write("-" * 80 + "\n")
        f.write("TEST STATISTICO (Mann-Whitney U):\n")
        f.write("Ipotesi Alternativa: Matchup(Low Stress) < Matchup(High Stress)\n")
        f.write(f"P-value: {p_val:.4f}\n")
        
        if p_val < 0.05:
            f.write("RISULTATO: SIGNIFICATIVO. I giocatori rilassati ricevono matchup peggiori.\n")
        else:
            f.write("RISULTATO: NON SIGNIFICATIVO.\n")
            
        # Correlation
        corr, p_corr = spearmanr(all_stress, all_matchups)
        f.write(f"\nCorrelazione Spearman (Stress vs Matchup): {corr:.4f} (p={p_corr:.4f})\n")
        f.write("(Correlazione positiva indica che all'aumentare dello stress migliora il matchup)\n")
        f.write("="*80 + "\n")


def analyze_dangerous_sequences(players_sessions, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'dangerous_sequences_results.txt')
    
    print(f"\nGenerazione report Sequenze Pericolose in: {output_file}")
    
    seq_counts = {} # "WLL" -> count occurrences
    seq_quits = {}  # "WLL" -> count quits (session ends after this sequence)
    
    # Global counts for probabilities
    global_counts = {'W': 0, 'L': 0, 'C': 0}
    
    SEQ_LEN = 3
    
    for p in players_sessions:
        for s in p['sessions']:
            battles = s['battles']
            
            # Convert session to outcome string
            outcomes = []
            for b in battles:
                outcome = ''
                if b['win'] == 1:
                    outcome = 'W'
                else:
                    # Loss or Counter?
                    if b['matchup'] is not None and b['matchup'] < 40.0:
                        outcome = 'C' # Counter
                    else:
                        outcome = 'L' # Normal Loss
                
                outcomes.append(outcome)
                global_counts[outcome] += 1
            
            if len(battles) < SEQ_LEN:
                continue
            
            # Analyze triplets
            for i in range(len(outcomes) - SEQ_LEN + 1):
                triplet = "".join(outcomes[i : i+SEQ_LEN])
                
                seq_counts[triplet] = seq_counts.get(triplet, 0) + 1
                
                # Check if this is the end of the session (Quit)
                if (i + SEQ_LEN) == len(outcomes):
                    # Check stop type to be sure it's a real quit/break
                    if s['stop_type'] in ['Long', 'Quit', 'Short']:
                        seq_quits[triplet] = seq_quits.get(triplet, 0) + 1

    # Calculate Global Probabilities
    total_outcomes = sum(global_counts.values())
    probs = {k: v / total_outcomes for k, v in global_counts.items()} if total_outcomes > 0 else {'W':0, 'L':0, 'C':0}
    
    total_triplets = sum(seq_counts.values())

    # Calculate Stats per Sequence
    results = []
    for seq, count in seq_counts.items():
        quit_count = seq_quits.get(seq, 0)
        quit_rate = quit_count / count if count > 0 else 0
        
        # Expected Probability assuming independence
        p_seq = 1.0
        for char in seq:
            p_seq *= probs.get(char, 0)
            
        exp_count = p_seq * total_triplets
        ratio = count / exp_count if exp_count > 0 else 0.0
        
        results.append({
            'seq': seq, 
            'count': count, 
            'quit_count': quit_count, 
            'quit_rate': quit_rate,
            'exp_count': exp_count,
            'ratio': ratio
        })
        
    # Sort by Quit Rate
    results.sort(key=lambda x: x['quit_rate'], reverse=True)
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI SEQUENZE PERICOLOSE (OUTCOME -> QUIT)\n")
        f.write("Legenda: W=Win, L=Loss (Normal), C=Counter (Loss & Matchup < 40%)\n")
        f.write("Obiettivo: Identificare sequenze che causano quit e verificare se sono 'soppresse' (Ratio < 1) o 'frequenti' (Ratio > 1).\n")
        f.write("="*80 + "\n\n")
        
        f.write(f"Totale Triplette: {total_triplets}\n")
        f.write(f"Probabilità Globali: W={probs['W']:.2f}, L={probs['L']:.2f}, C={probs['C']:.2f}\n")
        f.write("-" * 100 + "\n")
        
        f.write(f"{'SEQ':<5} | {'COUNT':<8} | {'QUITS':<8} | {'QUIT RATE':<10} | {'EXPECTED':<10} | {'RATIO (Obs/Exp)':<15}\n")
        f.write("-" * 100 + "\n")
        
        for r in results:
            if r['count'] < 10: continue # Filter rare sequences
            f.write(f"{r['seq']:<5} | {r['count']:<8} | {r['quit_count']:<8} | {r['quit_rate']*100:.1f}%{'':<5} | {r['exp_count']:<10.1f} | {r['ratio']:<15.2f}\n")
            
        # Correlation Analysis
        ratios = [r['ratio'] for r in results if r['count'] >= 10]
        quit_rates = [r['quit_rate'] for r in results if r['count'] >= 10]
        
        if len(ratios) > 2:
            corr, p_val = spearmanr(ratios, quit_rates)
            f.write("-" * 100 + "\n")
            f.write(f"CORRELAZIONE SPEARMAN (Ratio vs Quit Rate): {corr:.4f} (p={p_val:.4f})\n")
            if corr < 0 and p_val < 0.05:
                f.write("-> Correlazione NEGATIVA SIGNIFICATIVA: Le sequenze soppresse (Ratio < 1) tendono ad avere Quit Rate più alto.\n")
                f.write("   (Possibile intervento dell'algoritmo per ridurre le sequenze tossiche)\n")
            elif corr > 0 and p_val < 0.05:
                f.write("-> Correlazione POSITIVA SIGNIFICATIVA: Le sequenze più frequenti causano più quit.\n")

        f.write("-" * 100 + "\n")
        f.write("INTERPRETAZIONE:\n")
        f.write("1. QUIT RATE ALTO: Sequenze che frustrano il giocatore.\n")
        f.write("2. RATIO < 1.0: La sequenza appare MENO del previsto (possibile intervento del sistema).\n")
        f.write("3. RATIO > 1.0: La sequenza appare PIÙ del previsto (clustering naturale o forzatura).\n")
        f.write("="*100 + "\n")


def analyze_short_session_bonus(players_sessions, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'short_session_bonus_results.txt')

    print(f"\nGenerazione report Correlazione Bonus Sessioni Brevi in: {output_file}")

    matches_per_session = []
    avg_matchups = []
    avg_level_diffs = []

    for p in players_sessions:
        profile = p.get('profile')
        if not profile:
            continue

        mps = profile.get('matches_per_session')
        avg_mu = profile.get('avg_matchup_pct')
        avg_ld = profile.get('avg_level_diff')

        if mps is not None and avg_mu is not None and avg_ld is not None:
            matches_per_session.append(mps)
            avg_matchups.append(avg_mu)
            avg_level_diffs.append(avg_ld)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI CORRELAZIONE: BONUS PER SESSIONI BREVI\n")
        f.write("Ipotesi: I giocatori con sessioni più corte (meno match/sessione) ricevono matchup mediamente migliori?\n")
        f.write("="*80 + "\n\n")

        if len(matches_per_session) < 5:
            f.write("Dati insufficienti per l'analisi (meno di 5 giocatori con profili completi).\n")
            return

        f.write(f"Campione: {len(matches_per_session)} giocatori\n")
        f.write("-" * 80 + "\n")

        # 1. Correlazione vs Matchup
        corr_mu, p_mu = spearmanr(matches_per_session, avg_matchups)
        f.write("1. Correlazione: Match/Sessione vs. Matchup Medio\n")
        f.write(f"   Coefficiente: {corr_mu:.4f}\n")
        f.write(f"   P-value:      {p_mu:.4f}\n")
        if p_mu < 0.05:
            if corr_mu < 0:
                f.write("   RISULTATO: SIGNIFICATIVO E NEGATIVO. Meno partite per sessione sono correlate a matchup MIGLIORI.\n")
            else:
                f.write("   RISULTATO: SIGNIFICATIVO E POSITIVO. Meno partite per sessione sono correlate a matchup PEGGIORI.\n")
        else:
            f.write("   RISULTATO: NON SIGNIFICATIVO. Nessuna correlazione evidente.\n")
        f.write("\n")

        # 2. Correlazione vs Level Difference
        corr_ld, p_ld = spearmanr(matches_per_session, avg_level_diffs)
        f.write("2. Correlazione: Match/Sessione vs. Delta Livello Medio\n")
        f.write("   (Delta Livello > 0 significa che il giocatore ha livelli più alti dell'avversario)\n")
        f.write(f"   Coefficiente: {corr_ld:.4f}\n")
        f.write(f"   P-value:      {p_ld:.4f}\n")
        if p_ld < 0.05:
            if corr_ld < 0:
                f.write("   RISULTATO: SIGNIFICATIVO E NEGATIVO. Meno partite per sessione sono correlate a un Delta Livello INFERIORE (avversari più forti).\n")
            else:
                f.write("   RISULTATO: SIGNIFICATIVO E POSITIVO. Meno partite per sessione sono correlate a un Delta Livello SUPERIORE (avversari più deboli).\n")
        else:
            f.write("   RISULTATO: NON SIGNIFICATIVO. Nessuna correlazione evidente.\n")
        
        f.write("="*80 + "\n")

def _compute_and_write_mixed_markov(data_pairs, from_states_labels, to_states_labels, title, f):
    n_from = len(from_states_labels)
    n_to = len(to_states_labels)
    transitions = [[0]*n_to for _ in range(n_from)]
    
    for from_s, to_s in data_pairs:
        if from_s is not None and to_s is not None:
            transitions[from_s][to_s] += 1
            
    total_transitions = sum(sum(row) for row in transitions)
    f.write(f"\n--- {title} ---\n")
    f.write(f"Totale Transizioni: {total_transitions}\n")
    
    if total_transitions == 0:
        f.write("Dati insufficienti.\n")
        return

    row_totals = [sum(transitions[i]) for i in range(n_from)]
    col_totals = [sum(transitions[i][j] for i in range(n_from)) for j in range(n_to)]
    grand_total = sum(row_totals)
    
    global_probs_to = [c / grand_total for c in col_totals]
    
    col_width = 25
    header = f"{'STATO PRECEDENTE':<20} | " + " | ".join([f"NEXT: {s:<{col_width}}" for s in to_states_labels])
    sep = "-" * len(header)
    
    f.write(sep + "\n")
    f.write(header + "\n")
    f.write(sep + "\n")
    
    for i, from_state in enumerate(from_states_labels):
        row_str = f"{from_state:<20} | "
        for j, to_state in enumerate(to_states_labels):
            count = transitions[i][j]
            total_from = row_totals[i] if row_totals[i] > 0 else 1
            obs_prob = count / total_from
            exp_prob = global_probs_to[j]
            
            marker = "(!)" if abs(obs_prob - exp_prob) > 0.05 else ""
            cell_str = f"{obs_prob*100:.1f}% (Exp {exp_prob*100:.1f}%) {marker}"
            row_str += f"{cell_str:<{col_width+6}} | "
        f.write(row_str + "\n")
    f.write(sep + "\n\n")


def _compute_and_write_markov(data_sequences, states_labels, title, f):
    n_states = len(states_labels)
    transitions = [[0]*n_states for _ in range(n_states)]
    total_transitions = 0
    
    for seq in data_sequences:
        for i in range(len(seq) - 1):
            curr_s = seq[i]
            next_s = seq[i+1]
            if curr_s is not None and next_s is not None:
                transitions[curr_s][next_s] += 1
                total_transitions += 1
                
    f.write(f"\n--- {title} ---\n")
    f.write(f"Totale Transizioni: {total_transitions}\n")
    
    if total_transitions == 0:
        f.write("Dati insufficienti.\n")
        return

    row_totals = [sum(transitions[i]) for i in range(n_states)]
    col_totals = [sum(transitions[i][j] for i in range(n_states)) for j in range(n_states)]
    grand_total = sum(row_totals)
    
    global_probs = [c / grand_total for c in col_totals]
    
    # Formatting
    col_width = 25
    header = f"{'STATO PRECEDENTE':<20} | " + " | ".join([f"NEXT: {s:<{col_width}}" for s in states_labels])
    sep = "-" * len(header)
    
    f.write(sep + "\n")
    f.write(header + "\n")
    f.write(sep + "\n")
    
    for i, from_state in enumerate(states_labels):
        row_str = f"{from_state:<20} | "
        for j, to_state in enumerate(states_labels):
            count = transitions[i][j]
            total_from = row_totals[i] if row_totals[i] > 0 else 1
            obs_prob = count / total_from
            exp_prob = global_probs[j]
            
            diff = obs_prob - exp_prob
            marker = "(!)" if abs(diff) > 0.05 else ""
            
            cell_str = f"{obs_prob*100:.1f}% (Exp {exp_prob*100:.1f}%) {marker}"
            row_str += f"{cell_str:<{col_width+6}} | "
        f.write(row_str + "\n")
        
    f.write(sep + "\n")
    
    try:
        chi2, p, dof, ex = chi2_contingency(transitions)
        f.write(f"Test Chi-Quadro: p-value = {p:.6f}\n")
        if p < 0.05:
            f.write("RISULTATO: DIPENDENZA SIGNIFICATIVA (Memoria presente).\n")
        else:
            f.write("RISULTATO: INDIPENDENZA (Processo senza memoria).\n")
    except ValueError:
        f.write("Errore calcolo Chi-Quadro.\n")
    f.write("\n")

def analyze_markov_chains(players_sessions, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'markov_chains_results.txt')

    print(f"\nGenerazione report Catene di Markov (Matchup, No-Lvl, Levels) in: {output_file}")
    
    seq_mu = []
    seq_mnl = []
    seq_lvl = []
    outcome_to_mu_pairs = []
    outcome_to_mnl_pairs = []
    outcome_to_lvl_pairs = []
    
    for p in players_sessions:
        for session in p['sessions']:
            battles = session['battles']
            if len(battles) < 2: continue
            
            s_mu = []
            s_mnl = []
            s_lvl = []

            # Analisi per Outcome -> Next Matchup
            for i in range(len(battles) - 1):
                curr_b = battles[i]
                next_b = battles[i+1]

                from_state = curr_b.get('win') # 0 for Loss, 1 for Win

                next_mu = next_b.get('matchup')
                to_state = None
                if next_mu is not None:
                    if next_mu > 55.0: to_state = 2
                    elif next_mu < 45.0: to_state = 0
                    else: to_state = 1
                
                outcome_to_mu_pairs.append((from_state, to_state))

                # Next Matchup No Lvl
                next_mnl = next_b.get('matchup_no_lvl')
                to_state_mnl = None
                if next_mnl is not None:
                    if next_mnl > 55.0: to_state_mnl = 2
                    elif next_mnl < 45.0: to_state_mnl = 0
                    else: to_state_mnl = 1
                outcome_to_mnl_pairs.append((from_state, to_state_mnl))

                # Next Level Diff
                next_lvl = next_b.get('level_diff')
                to_state_lvl = None
                if next_lvl is not None:
                    if next_lvl > 0.5: to_state_lvl = 2 # Advantage
                    elif next_lvl < -0.5: to_state_lvl = 0 # Disadvantage
                    else: to_state_lvl = 1
                outcome_to_lvl_pairs.append((from_state, to_state_lvl))
            
            for b in battles:
                # Matchup
                m = b.get('matchup')
                if m is None: s_mu.append(None)
                elif m > 55.0: s_mu.append(2)
                elif m < 45.0: s_mu.append(0)
                else: s_mu.append(1)
                
                # No Lvl
                mnl = b.get('matchup_no_lvl')
                if mnl is None: s_mnl.append(None)
                elif mnl > 55.0: s_mnl.append(2)
                elif mnl < 45.0: s_mnl.append(0)
                else: s_mnl.append(1)
                
                # Level Diff
                l = b.get('level_diff')
                if l is None: s_lvl.append(None)
                elif l > 0.5: s_lvl.append(2) # Advantage
                elif l < -0.5: s_lvl.append(0) # Disadvantage
                else: s_lvl.append(1)
            
            seq_mu.append(s_mu)
            seq_mnl.append(s_mnl)
            seq_lvl.append(s_lvl)
            
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI CATENE DI MARKOV MULTIPLE\n")
        f.write("Obiettivo: Verificare la 'memoria' del sistema su diverse metriche.\n")
        f.write("Ipotesi Nera: La probabilità dello stato successivo dipende solo dalla distribuzione globale (Indipendenza).\n")
        f.write("="*120 + "\n")
        
        _compute_and_write_markov(seq_mu, ['Unfavorable', 'Even', 'Favorable'], "1. MATCHUP REALE (Include Livelli)", f)
        _compute_and_write_markov(seq_mnl, ['Unfavorable', 'Even', 'Favorable'], "2. MATCHUP NO-LVL (Solo Deck)", f)
        _compute_and_write_markov(seq_lvl, ['Disadvantage', 'Even', 'Advantage'], "3. LEVEL DIFFERENCE", f)
        _compute_and_write_mixed_markov(
            outcome_to_mu_pairs,
            from_states_labels=['Loss', 'Win'],
            to_states_labels=['Unfavorable', 'Even', 'Favorable'],
            title="4. OUTCOME PARTITA PRECEDENTE vs MATCHUP SUCCESSIVO",
            f=f
        )
        _compute_and_write_mixed_markov(
            outcome_to_mnl_pairs,
            from_states_labels=['Loss', 'Win'],
            to_states_labels=['Unfavorable', 'Even', 'Favorable'],
            title="5. OUTCOME PARTITA PRECEDENTE vs MATCHUP NO-LVL SUCCESSIVO",
            f=f
        )
        _compute_and_write_mixed_markov(
            outcome_to_lvl_pairs,
            from_states_labels=['Loss', 'Win'],
            to_states_labels=['Disadvantage', 'Even', 'Advantage'],
            title="6. OUTCOME PARTITA PRECEDENTE vs LEVEL DIFF SUCCESSIVO",
            f=f
        )
        
        f.write("="*120 + "\n")

def analyze_return_after_bad_streak(players_sessions, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'return_after_bad_streak_results.txt')

    print(f"\nGenerazione report Return Matchup dopo Bad Streak in: {output_file}")

    # Config
    BAD_THRESH = 45.0
    STREAK_LEN = 2 
    
    # Storage: stop_type -> {'bad_streak': [], 'control': []}
    data = {
        'Short': {'bad_streak': [], 'control': []},
        'Long': {'bad_streak': [], 'control': []},
        'Quit': {'bad_streak': [], 'control': []}
    }
    
    for p in players_sessions:
        sessions = p['sessions']
        for i in range(len(sessions) - 1):
            curr_sess = sessions[i]
            next_sess = sessions[i+1]
            
            stop_type = curr_sess['stop_type']
            if stop_type not in data: continue 
            
            if not next_sess['battles']: continue
            first_b = next_sess['battles'][0]
            if first_b['matchup'] is None: continue
            return_mu = first_b['matchup']
            
            battles = curr_sess['battles']
            # Check last N matches
            if len(battles) < STREAK_LEN:
                data[stop_type]['control'].append(return_mu)
                continue
                
            last_n = battles[-STREAK_LEN:]
            if any(b['matchup'] is None for b in last_n):
                continue
                
            is_bad_streak = all(b['matchup'] < BAD_THRESH for b in last_n)
            
            if is_bad_streak:
                data[stop_type]['bad_streak'].append(return_mu)
            else:
                data[stop_type]['control'].append(return_mu)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI RETURN MATCHUP DOPO BAD STREAK\n")
        f.write("Domanda: Se un giocatore chiude la sessione dopo una serie di matchup sfavorevoli,\n")
        f.write("         al ritorno viene 'punito' ancora (memoria) o il sistema si resetta (coin flip)?\n")
        f.write(f"Definizione Bad Streak: Ultimi {STREAK_LEN} match con Matchup < {BAD_THRESH}%\n")
        f.write("="*80 + "\n\n")
        
        for stop_type in ['Short', 'Long', 'Quit']:
            bad_vals = data[stop_type]['bad_streak']
            ctrl_vals = data[stop_type]['control']
            
            f.write(f"--- STOP TYPE: {stop_type} ---\n")
            if len(bad_vals) < 5 or len(ctrl_vals) < 5:
                f.write("Dati insufficienti.\n\n")
                continue
                
            avg_bad = statistics.mean(bad_vals)
            avg_ctrl = statistics.mean(ctrl_vals)
            
            f.write(f"{'Condizione Precedente':<25} | {'N':<6} | {'Avg Return Matchup':<20}\n")
            f.write("-" * 60 + "\n")
            f.write(f"{'Bad Streak':<25} | {len(bad_vals):<6} | {avg_bad:<20.2f}%\n")
            f.write(f"{'Control (No Streak)':<25} | {len(ctrl_vals):<6} | {avg_ctrl:<20.2f}%\n")
            
            # Test Mann-Whitney U
            # H1: Bad Streak Return < Control Return (Punishment Continues)
            stat, p_val = mannwhitneyu(bad_vals, ctrl_vals, alternative='less')
            
            f.write("-" * 60 + "\n")
            f.write(f"Delta: {avg_bad - avg_ctrl:+.2f}%\n")
            f.write(f"Test Mann-Whitney U (Bad < Control): p-value = {p_val:.4f}\n")
            
            if p_val < 0.05:
                f.write("RISULTATO: SIGNIFICATIVO. La punizione sembra continuare anche dopo la pausa.\n")
                f.write("           (Il matchup al ritorno è peggiore rispetto alla norma)\n")
            else:
                f.write("RISULTATO: NON SIGNIFICATIVO. Il sistema sembra resettarsi (o non c'è memoria).\n")
            
            # Test vs 50% (Coin Flip) for Bad Streak group
            t_stat, p_50 = ttest_1samp(bad_vals, 50.0)
            
            f.write(f"Test vs 50% (Coin Flip): p-value = {p_50:.4f} (Avg: {avg_bad:.2f}%)\n")
            if p_50 < 0.05 and avg_bad < 50:
                 f.write("           (Significativamente inferiore al 50% -> Sfavorevole)\n")
            elif p_50 < 0.05 and avg_bad > 50:
                 f.write("           (Significativamente superiore al 50% -> Favorevole/Pity)\n")
            else:
                 f.write("           (Compatibile con 50% -> Coin Flip)\n")

            f.write("\n")
        f.write("="*80 + "\n")

def analyze_debt_extinction(players_sessions, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'debt_extinction_results.txt')

    print(f"\nGenerazione report Estinzione Debito (Unfavorable Win vs Loss) in: {output_file}")

    # Soglia per definire un match "Unfavorable"
    UNFAVORABLE_THRESH = 45.0
    
    # Gruppi di analisi
    # A: Unfavorable + WIN
    # B: Unfavorable + LOSS
    
    # Dati raccolti: Next Matchup
    next_mu_win = []
    next_mu_loss = []
    
    # Dati di controllo (per verificare che i gruppi siano omogenei)
    ctrl_curr_mu_win = []
    ctrl_curr_mu_loss = []
    
    ctrl_lvl_win = []
    ctrl_lvl_loss = []
    
    ctrl_elixir_diff_win = [] # (Opponent Leaked - Player Leaked) -> Positivo = Opponent ha giocato peggio

    for p in players_sessions:
        for s in p['sessions']:
            battles = s['battles']
            for i in range(len(battles) - 1):
                curr = battles[i]
                next_b = battles[i+1]
                
                if curr['matchup'] is None or next_b['matchup'] is None: continue
                
                # Identifichiamo la condizione "Debito": Matchup Sfavorevole
                if curr['matchup'] < UNFAVORABLE_THRESH:
                    
                    # Raccogliamo dati in base all'esito
                    if curr['win'] == 1:
                        next_mu_win.append(next_b['matchup'])
                        ctrl_curr_mu_win.append(curr['matchup'])
                        if curr['level_diff'] is not None: ctrl_lvl_win.append(curr['level_diff'])
                        
                        # Elixir Control
                        if curr.get('elixir_leaked_player') is not None and curr.get('elixir_leaked_opponent') is not None:
                            ctrl_elixir_diff_win.append(curr['elixir_leaked_opponent'] - curr['elixir_leaked_player'])
                            
                    else:
                        next_mu_loss.append(next_b['matchup'])
                        ctrl_curr_mu_loss.append(curr['matchup'])
                        if curr['level_diff'] is not None: ctrl_lvl_loss.append(curr['level_diff'])

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI ESTINZIONE DEBITO (MMR DEBT)\n")
        f.write("Ipotesi: Vincere un matchup sfavorevole NON estingue il debito (il sistema punisce ancora).\n")
        f.write("         Perdere un matchup sfavorevole estingue il debito (il sistema dà tregua).\n")
        f.write(f"Definizione Unfavorable: Matchup < {UNFAVORABLE_THRESH}%\n")
        f.write("="*80 + "\n\n")
        
        if len(next_mu_win) < 10 or len(next_mu_loss) < 10:
            f.write("Dati insufficienti.\n")
            return

        avg_next_win = statistics.mean(next_mu_win)
        avg_next_loss = statistics.mean(next_mu_loss)
        
        f.write(f"{'ESITO MATCH PRECEDENTE':<30} | {'N':<6} | {'NEXT MATCHUP (Avg)':<20}\n")
        f.write("-" * 65 + "\n")
        f.write(f"{'Unfavorable + WIN (Debito?)':<30} | {len(next_mu_win):<6} | {avg_next_win:<20.2f}%\n")
        f.write(f"{'Unfavorable + LOSS (Pagato?)':<30} | {len(next_mu_loss):<6} | {avg_next_loss:<20.2f}%\n")
        
        # Test Mann-Whitney U
        # H1: Next(Win) < Next(Loss) -> Chi vince viene punito con matchup peggiori
        stat, p_val = mannwhitneyu(next_mu_win, next_mu_loss, alternative='less')
        
        f.write("-" * 65 + "\n")
        f.write(f"Delta: {avg_next_win - avg_next_loss:+.2f}%\n")
        f.write(f"Test Mann-Whitney U (Win < Loss): p-value = {p_val:.4f}\n")
        
        if p_val < 0.05:
            f.write("RISULTATO: SIGNIFICATIVO. Vincere contro le probabilità porta a matchup futuri peggiori rispetto a perdere.\n")
        else:
            f.write("RISULTATO: NON SIGNIFICATIVO. Il sistema sembra trattare i due casi in modo simile.\n")
            
        f.write("\n" + "="*80 + "\n")
        f.write("CONTROLLI DI VALIDITÀ (Bias Check)\n")
        f.write("Verifichiamo che le vittorie 'impossibili' non siano dovute a fattori esterni.\n")
        f.write("-" * 80 + "\n")
        
        f.write(f"1. Matchup Iniziale (Avg): Win={statistics.mean(ctrl_curr_mu_win):.2f}% vs Loss={statistics.mean(ctrl_curr_mu_loss):.2f}%\n")
        f.write(f"2. Level Diff (Avg):       Win={statistics.mean(ctrl_lvl_win):+.2f} vs Loss={statistics.mean(ctrl_lvl_loss):+.2f}\n")
        if ctrl_elixir_diff_win:
            f.write(f"3. Elixir Advantage (Win): {statistics.mean(ctrl_elixir_diff_win):+.2f} (Positivo = Opponent ha sprecato elisir)\n")
            f.write("   (Se alto, la vittoria potrebbe essere dovuta a errori dell'avversario)\n")
        f.write("="*80 + "\n")

def analyze_favorable_outcome_impact(players_sessions, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'favorable_outcome_impact_results.txt')

    print(f"\nGenerazione report Impatto Esito Matchup Favorevole in: {output_file}")

    # Soglia per definire un match "Favorable"
    FAVORABLE_THRESH = 55.0
    
    # Gruppi di analisi
    # A: Favorable + WIN (Esito Atteso)
    # B: Favorable + LOSS (Esito Inatteso / Choke)
    
    next_mu_win = []
    next_mu_loss = []
    
    ctrl_curr_mu_win = []
    ctrl_curr_mu_loss = []
    ctrl_lvl_win = []
    ctrl_lvl_loss = []
    ctrl_elixir_diff_loss = [] 

    for p in players_sessions:
        for s in p['sessions']:
            battles = s['battles']
            for i in range(len(battles) - 1):
                curr = battles[i]
                next_b = battles[i+1]
                
                if curr['matchup'] is None or next_b['matchup'] is None: continue
                
                if curr['matchup'] > FAVORABLE_THRESH:
                    if curr['win'] == 1:
                        next_mu_win.append(next_b['matchup'])
                        ctrl_curr_mu_win.append(curr['matchup'])
                        if curr['level_diff'] is not None: ctrl_lvl_win.append(curr['level_diff'])
                    else:
                        next_mu_loss.append(next_b['matchup'])
                        ctrl_curr_mu_loss.append(curr['matchup'])
                        if curr['level_diff'] is not None: ctrl_lvl_loss.append(curr['level_diff'])
                        
                        if curr.get('elixir_leaked_player') is not None and curr.get('elixir_leaked_opponent') is not None:
                            ctrl_elixir_diff_loss.append(curr['elixir_leaked_opponent'] - curr['elixir_leaked_player'])

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI IMPATTO ESITO SU MATCHUP FAVOREVOLE\n")
        f.write("Domanda: Come reagisce il sistema quando vinci o perdi una partita che 'dovevi' vincere?\n")
        f.write(f"Definizione Favorable: Matchup > {FAVORABLE_THRESH}%\n")
        f.write("="*80 + "\n\n")
        
        if len(next_mu_win) < 10 or len(next_mu_loss) < 10:
            f.write("Dati insufficienti.\n")
            return

        avg_next_win = statistics.mean(next_mu_win)
        avg_next_loss = statistics.mean(next_mu_loss)
        
        f.write(f"{'ESITO MATCH PRECEDENTE':<30} | {'N':<6} | {'NEXT MATCHUP (Avg)':<20}\n")
        f.write("-" * 65 + "\n")
        f.write(f"{'Favorable + WIN (Atteso)':<30} | {len(next_mu_win):<6} | {avg_next_win:<20.2f}%\n")
        f.write(f"{'Favorable + LOSS (Inatteso)':<30} | {len(next_mu_loss):<6} | {avg_next_loss:<20.2f}%\n")
        
        stat, p_val = mannwhitneyu(next_mu_win, next_mu_loss)
        f.write("-" * 65 + "\n")
        f.write(f"Delta: {avg_next_win - avg_next_loss:+.2f}%\n")
        f.write(f"Test Mann-Whitney U (Differenza Significativa): p-value = {p_val:.4f}\n")
        
        f.write("\n" + "="*80 + "\n")
        f.write(f"1. Matchup Iniziale (Avg): Win={statistics.mean(ctrl_curr_mu_win):.2f}% vs Loss={statistics.mean(ctrl_curr_mu_loss):.2f}%\n")
        if ctrl_elixir_diff_loss:
            f.write(f"2. Elixir Advantage (Loss): {statistics.mean(ctrl_elixir_diff_loss):+.2f} (Se molto negativo, player ha giocato male)\n")
        f.write("="*80 + "\n")

def analyze_defeat_quality_impact(players_sessions, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'defeat_quality_impact_results.txt')

    print(f"\nGenerazione report Qualità della Sconfitta (Crushing vs Close) in: {output_file}")

    # Gruppi
    # A: Crushing Defeat (0-3). Segnale di resa/stomp.
    # B: Close Defeat (Diff 1 corona). Segnale di match combattuto.
    
    crushing_next_mu = []
    close_next_mu = []
    
    # Controllo Elixir Leaked (se disponibile) per confermare "volontarietà" o scarsa performance
    crushing_leaked = []
    close_leaked = []

    for p in players_sessions:
        for s in p['sessions']:
            battles = s['battles']
            for i in range(len(battles) - 1):
                curr = battles[i]
                next_b = battles[i+1]
                
                if curr['win'] == 0: # Solo sconfitte
                    if curr['matchup'] is None or next_b['matchup'] is None: continue
                    
                    p_crowns = curr['player_crowns']
                    o_crowns = curr['opponent_crowns']
                    
                    # Crushing Defeat: 0-3
                    if p_crowns == 0 and o_crowns == 3:
                        crushing_next_mu.append(next_b['matchup'])
                        if curr.get('elixir_leaked_player') is not None:
                            crushing_leaked.append(curr['elixir_leaked_player'])
                            
                    # Close Defeat: Differenza di 1 (es. 0-1, 1-2, 2-3)
                    elif (o_crowns - p_crowns) == 1:
                        close_next_mu.append(next_b['matchup'])
                        if curr.get('elixir_leaked_player') is not None:
                            close_leaked.append(curr['elixir_leaked_player'])

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI QUALITÀ DELLA SCONFITTA: CRUSHING (0-3) vs CLOSE (Diff 1)\n")
        f.write("Domanda: Perdere malamente (0-3) estingue il debito meglio di una sconfitta combattuta?\n")
        f.write("Ipotesi: Una sconfitta netta attiva meccanismi di protezione (Pity) più forti.\n")
        f.write("="*80 + "\n\n")
        
        if len(crushing_next_mu) < 10 or len(close_next_mu) < 10:
            f.write("Dati insufficienti.\n")
            return

        avg_crushing = statistics.mean(crushing_next_mu)
        avg_close = statistics.mean(close_next_mu)
        
        f.write(f"{'TIPO SCONFITTA':<25} | {'N':<6} | {'NEXT MATCHUP (Avg)':<20} | {'AVG LEAKED ELIXIR':<20}\n")
        f.write("-" * 80 + "\n")
        
        leak_crushing = f"{statistics.mean(crushing_leaked):.2f}" if crushing_leaked else "N/A"
        leak_close = f"{statistics.mean(close_leaked):.2f}" if close_leaked else "N/A"
        
        f.write(f"{'Crushing (0-3)':<25} | {len(crushing_next_mu):<6} | {avg_crushing:<20.2f}% | {leak_crushing:<20}\n")
        f.write(f"{'Close (Diff 1)':<25} | {len(close_next_mu):<6} | {avg_close:<20.2f}% | {leak_close:<20}\n")
        
        stat, p_val = mannwhitneyu(crushing_next_mu, close_next_mu, alternative='greater')
        f.write("-" * 80 + "\n")
        f.write(f"Delta: {avg_crushing - avg_close:+.2f}%\n")
        f.write(f"Test Mann-Whitney U (Crushing > Close): p-value = {p_val:.4f}\n")
        
        if p_val < 0.05:
            f.write("RISULTATO: SIGNIFICATIVO. Farsi 'asfaltare' (0-3) porta a matchup successivi migliori.\n")
            f.write("           (Il sistema rileva la frustrazione/incompetenza e compensa di più)\n")
        else:
            f.write("RISULTATO: NON SIGNIFICATIVO. Il margine della sconfitta non sembra influenzare il prossimo matchup.\n")
        
        f.write("="*80 + "\n")

def analyze_debt_credit_duration_and_levels(players_sessions, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'debt_credit_duration_levels.txt')

    print(f"\nGenerazione report Durata Debito/Credito e Livelli in: {output_file}")

    # Definizioni
    BAD_THRESH = 45.0  # Debito
    GOOD_THRESH = 55.0 # Credito
    
    # Storage
    # lengths: lista di lunghezze delle streak
    # levels: lista di tutti i level_diff incontrati durante quel tipo di streak
    
    # 1. Analisi Standard (Matchup Reale - include livelli)
    stats_real = {
        'Debt': {'lengths': [], 'levels': []},
        'Credit': {'lengths': [], 'levels': []},
        'Normal': {'lengths': [], 'levels': []} # 45-55%
    }
    # 2. Analisi Pura (Matchup No-Lvl - solo Deck)
    stats_pure = {
        'Debt': {'lengths': [], 'levels': []},
        'Credit': {'lengths': [], 'levels': []},
        'Normal': {'lengths': [], 'levels': []}
    }

    for p in players_sessions:
        for s in p['sessions']:
            battles = s['battles']
            
            current_type = None
            current_len = 0
            
            current_type_pure = None
            current_len_pure = 0
            
            for b in battles:
                mu = b['matchup']
                mu_pure = b.get('matchup_no_lvl')
                lvl = b['level_diff']
                
                if mu is None or lvl is None: continue
                
                # --- LOGICA STANDARD (Reale) ---
                if mu < BAD_THRESH: new_type = 'Debt'
                elif mu > GOOD_THRESH: new_type = 'Credit'
                else: new_type = 'Normal'
                
                if new_type != current_type:
                    if current_type is not None:
                        stats_real[current_type]['lengths'].append(current_len)
                    current_type = new_type
                    current_len = 1
                else:
                    current_len += 1
                
                stats_real[new_type]['levels'].append(lvl)
                
                # --- LOGICA PURA (No-Lvl) ---
                if mu_pure is not None:
                    if mu_pure < BAD_THRESH: new_type_pure = 'Debt'
                    elif mu_pure > GOOD_THRESH: new_type_pure = 'Credit'
                    else: new_type_pure = 'Normal'
                    
                    if new_type_pure != current_type_pure:
                        if current_type_pure is not None:
                            stats_pure[current_type_pure]['lengths'].append(current_len_pure)
                        current_type_pure = new_type_pure
                        current_len_pure = 1
                    else:
                        current_len_pure += 1
                    
                    # Qui verifichiamo se il livello è correlato al SOLO matchup di mazzo
                    stats_pure[new_type_pure]['levels'].append(lvl)
            
            # Salva l'ultima streak della sessione
            if current_type is not None:
                stats_real[current_type]['lengths'].append(current_len)
            
            if current_type_pure is not None:
                stats_pure[current_type_pure]['lengths'].append(current_len_pure)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI DURATA DEBITO/CREDITO E CORRELAZIONE LIVELLI (PAY-TO-WIN CHECK)\n")
        f.write("Obiettivo 1: Capire quanto durano i periodi di punizione (Debito) e gratificazione (Credito).\n")
        f.write("Obiettivo 2: Verificare se durante il Debito il giocatore affronta avversari di livello più alto (incentivo shop).\n")
        f.write(f"Soglie: Debito < {BAD_THRESH}%, Credito > {GOOD_THRESH}%\n")
        f.write("="*80 + "\n\n")
        
        f.write("--- 1. ANALISI STANDARD (Matchup Reale: include livelli) ---\n")
        f.write(f"{'TIPO FASE':<15} | {'N. STREAK':<10} | {'AVG DURATA':<12} | {'MAX DURATA':<10} | {'AVG LEVEL DIFF':<15}\n")
        f.write("-" * 80 + "\n")
        
        for phase in ['Debt', 'Normal', 'Credit']:
            lens = stats_real[phase]['lengths']
            levs = stats_real[phase]['levels']
            
            if not lens: continue
            
            avg_len = statistics.mean(lens)
            max_len = max(lens)
            avg_lvl = statistics.mean(levs) if levs else 0.0
            
            f.write(f"{phase:<15} | {len(lens):<10} | {avg_len:<12.2f} | {max_len:<10} | {avg_lvl:<15.2f}\n")

        f.write("\nNota: Una correlazione qui è attesa se il Matchup include i livelli.\n")
        f.write("-" * 80 + "\n")
        
        # --- ANALISI PURA ---
        f.write("\n--- 2. ANALISI PURA (Matchup No-Lvl: Solo Deck) ---\n")
        f.write("Domanda: Quando il sistema ti countera il MAZZO (Debt), ti dà anche livelli più alti?\n")
        f.write(f"{'TIPO FASE':<15} | {'N. STREAK':<10} | {'AVG DURATA':<12} | {'MAX DURATA':<10} | {'AVG LEVEL DIFF':<15}\n")
        f.write("-" * 80 + "\n")
        
        for phase in ['Debt', 'Normal', 'Credit']:
            lens = stats_pure[phase]['lengths']
            levs = stats_pure[phase]['levels']
            
            if not lens: continue
            
            avg_len = statistics.mean(lens)
            max_len = max(lens)
            avg_lvl = statistics.mean(levs) if levs else 0.0
            
            f.write(f"{phase:<15} | {len(lens):<10} | {avg_len:<12.2f} | {max_len:<10} | {avg_lvl:<15.2f}\n")

        f.write("-" * 80 + "\n")
        
        # Test Statistici sui Livelli (PURA)
        debt_lvls = stats_pure['Debt']['levels']
        credit_lvls = stats_pure['Credit']['levels']
        
        if len(debt_lvls) > 10 and len(credit_lvls) > 10:
            # Mann-Whitney U: Debt Level Diff < Credit Level Diff? (Più negativo = avversario più forte)
            stat, p_val = mannwhitneyu(debt_lvls, credit_lvls, alternative='less')
            
            avg_debt = statistics.mean(debt_lvls)
            avg_credit = statistics.mean(credit_lvls)
            
            f.write(f"Confronto Livelli (Pure Debt vs Pure Credit):\n")
            f.write(f"   Avg Level Diff in DEBT (Bad Deck):   {avg_debt:+.3f}\n")
            f.write(f"   Avg Level Diff in CREDIT (Good Deck): {avg_credit:+.3f}\n")
            f.write(f"   Test Mann-Whitney U (Debt < Credit): p-value = {p_val:.4f}\n\n")
            
            if p_val < 0.05:
                f.write("RISULTATO: SIGNIFICATIVO (DOPPIA PUNIZIONE).\n")
                f.write("           Quando il sistema ti dà un mazzo contro (Counter Deck), ti assegna ANCHE avversari di livello superiore.\n")
                f.write("           (Indizio molto forte di manipolazione Pay-to-Win).\n")
            else:
                f.write("RISULTATO: NON SIGNIFICATIVO.\n")
                f.write("           Il livello degli avversari sembra indipendente dal fatto che tu abbia un mazzo favorevole o sfavorevole.\n")
        
        f.write("="*80 + "\n")

def analyze_punishment_tradeoff(players_sessions, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'punishment_tradeoff_results.txt')

    print(f"\nGenerazione report Trade-off Punizione (Matchup vs Livelli) in: {output_file}")

    # Soglie
    BAD_MU_THRESH = 45.0
    BAD_LVL_THRESH = -0.5 # Player underleveled (Svantaggio livelli)

    matchups_no_lvl = []
    level_diffs = []
    
    count_bad_mu = 0
    count_bad_lvl = 0
    count_double_whammy = 0
    total_valid = 0

    for p in players_sessions:
        for s in p['sessions']:
            for b in s['battles']:
                if b['game_mode'] not in ['Ladder', 'Ranked']:
                    continue
                
                mu = b.get('matchup_no_lvl')
                lvl = b.get('level_diff')
                
                if mu is not None and lvl is not None:
                    matchups_no_lvl.append(mu)
                    level_diffs.append(lvl)
                    total_valid += 1
                    
                    is_bad_mu = mu < BAD_MU_THRESH
                    is_bad_lvl = lvl < BAD_LVL_THRESH
                    
                    if is_bad_mu: count_bad_mu += 1
                    if is_bad_lvl: count_bad_lvl += 1
                    if is_bad_mu and is_bad_lvl: count_double_whammy += 1

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI TRADE-OFF PUNIZIONE: MATCHUP PURO vs LIVELLI\n")
        f.write("Ipotesi: Il sistema usa o il Counter Deck o i Livelli per svantaggiare, ma raramente entrambi insieme (Double Whammy).\n")
        f.write(f"Soglie: Bad Matchup (No-Lvl) < {BAD_MU_THRESH}%, Bad Levels < {BAD_LVL_THRESH}\n")
        f.write("="*80 + "\n\n")
        
        if total_valid < 100:
            f.write("Dati insufficienti.\n")
            return

        # 1. Correlazione
        corr, p_val = spearmanr(matchups_no_lvl, level_diffs)
        
        f.write("1. CORRELAZIONE (Matchup No-Lvl vs Level Diff)\n")
        f.write(f"   Coefficiente Spearman: {corr:.4f}\n")
        f.write(f"   P-value:               {p_val:.4f}\n")
        
        f.write("\n   Interpretazione:\n")
        f.write("   - Correlazione NEGATIVA: Se il Matchup sale, i Livelli scendono (e viceversa). Supporta l'ipotesi di alternanza/trade-off.\n")
        f.write("   - Correlazione POSITIVA: Se il Matchup sale, i Livelli salgono. (Doppio aiuto o Doppia punizione).\n")
        f.write("   - Vicino a 0: Indipendenza.\n")
        f.write("-" * 80 + "\n")
        
        # 2. Analisi Frequenza Double Whammy
        prob_bad_mu = count_bad_mu / total_valid
        prob_bad_lvl = count_bad_lvl / total_valid
        
        exp_double_whammy = prob_bad_mu * prob_bad_lvl * total_valid
        obs_double_whammy = count_double_whammy
        
        ratio = obs_double_whammy / exp_double_whammy if exp_double_whammy > 0 else 0
        
        f.write("2. ANALISI DOUBLE WHAMMY (Doppia Punizione)\n")
        f.write(f"   Totale Battaglie: {total_valid}\n")
        f.write(f"   Bad Matchup Count: {count_bad_mu} ({prob_bad_mu*100:.2f}%)\n")
        f.write(f"   Bad Levels Count:  {count_bad_lvl} ({prob_bad_lvl*100:.2f}%)\n\n")
        
        f.write(f"   Double Whammy ATTESI (Ipotesi Indipendenza):   {exp_double_whammy:.2f}\n")
        f.write(f"   Double Whammy OSSERVATI:                       {obs_double_whammy}\n")
        f.write(f"   RATIO (Obs/Exp):                               {ratio:.2f}x\n")
        
        f.write("\n   Conclusione:\n")
        if ratio < 0.85:
            f.write("   RATIO < 1: Il sistema EVITA la doppia punizione. (Conferma l'ipotesi 'o l'uno o l'altro').\n")
        elif ratio > 1.15:
            f.write("   RATIO > 1: Il sistema FORZA la doppia punizione. (Accanimento/Pay-to-Win pressure).\n")
        else:
            f.write("   RATIO ~ 1: Eventi indipendenti. Non c'è coordinazione evidente tra deck e livelli.\n")
            
        f.write("="*80 + "\n")

def analyze_extreme_level_streak(players_sessions, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'extreme_level_streak_results.txt')

    print(f"\nGenerazione report streak livelli estremi in: {output_file}")

    # Soglie per Level Diff
    # > 0.5: Vantaggio (es. metà mazzo +1)
    # < -0.5: Svantaggio (es. metà mazzo -1)
    HIGH_THRESH = 0.5 
    LOW_THRESH = -0.5
    STREAK_LEN = 3
    NUM_SIMULATIONS = 10000

    # Accumulatori
    total_battles = 0
    count_high = 0 # Advantage
    count_low = 0  # Disadvantage
    
    obs_high_streaks = 0
    obs_low_streaks = 0
    total_opportunities = 0
    
    players_data = []

    for p in players_sessions:
        p_levels = []
        p_lengths = []
        
        for session in p['sessions']:
            # Filtriamo solo Ladder/Ranked
            levs = [b.get('level_diff') for b in session['battles'] if b.get('level_diff') is not None and (b['game_mode'] == 'Ladder' or b['game_mode'] == 'Ranked')]
            if not levs: 
                continue
            
            p_levels.extend(levs)
            p_lengths.append(len(levs))
            
            for l in levs:
                total_battles += 1
                if l > HIGH_THRESH: count_high += 1
                elif l < LOW_THRESH: count_low += 1
            
            if len(levs) >= STREAK_LEN:
                for i in range(len(levs) - STREAK_LEN + 1):
                    total_opportunities += 1
                    window = levs[i : i+STREAK_LEN]
                    if all(l > HIGH_THRESH for l in window): obs_high_streaks += 1
                    if all(l < LOW_THRESH for l in window): obs_low_streaks += 1
        
        if p_levels:
            players_data.append((p_levels, p_lengths))

    if total_opportunities == 0:
        print("Dati insufficienti per l'analisi streak livelli.")
        return

    # Calcolo Teorico
    p_high = count_high / total_battles if total_battles else 0
    p_low = count_low / total_battles if total_battles else 0
    
    exp_high_theory = total_opportunities * (p_high ** STREAK_LEN)
    exp_low_theory = total_opportunities * (p_low ** STREAK_LEN)

    # Simulazioni
    sim_global_high = 0
    sim_global_low = 0
    sim_intra_high = 0
    sim_intra_low = 0

    print(f"Esecuzione di {NUM_SIMULATIONS} permutazioni (Livelli - Global & Intra Session)...")

    for _ in range(NUM_SIMULATIONS):
        for levs, lengths in players_data:
            # --- Global Shuffle ---
            global_shuffled = levs[:]
            random.shuffle(global_shuffled)
            
            idx = 0
            for l in lengths:
                s = global_shuffled[idx : idx+l]
                idx += l
                if len(s) >= STREAK_LEN:
                    for i in range(len(s) - STREAK_LEN + 1):
                        if all(v > HIGH_THRESH for v in s[i:i+STREAK_LEN]): sim_global_high += 1
                        if all(v < LOW_THRESH for v in s[i:i+STREAK_LEN]): sim_global_low += 1

            # Intra-Session Shuffle (Unico valido per i livelli per evitare bias da climbing)
            idx = 0
            for l in lengths:
                s_orig = levs[idx : idx+l]
                idx += l
                s_intra = s_orig[:]
                random.shuffle(s_intra)
                if len(s_intra) >= STREAK_LEN:
                    for i in range(len(s_intra) - STREAK_LEN + 1):
                        if all(v > HIGH_THRESH for v in s_intra[i:i+STREAK_LEN]): sim_intra_high += 1
                        if all(v < LOW_THRESH for v in s_intra[i:i+STREAK_LEN]): sim_intra_low += 1

    avg_global_high = sim_global_high / NUM_SIMULATIONS
    avg_global_low = sim_global_low / NUM_SIMULATIONS
    avg_intra_high = sim_intra_high / NUM_SIMULATIONS
    avg_intra_low = sim_intra_low / NUM_SIMULATIONS

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI STREAK LIVELLI ESTREMI (PAY-TO-WIN PRESSURE)\n")
        f.write("Obiettivo: Verificare se il sistema genera sequenze di partite con svantaggio di livello (Underleveled) più spesso del caso.\n")
        f.write("Metodo: Confronto con Teorico, Global Shuffle e Intra-Session Shuffle.\n")
        f.write("Nota: Global Shuffle può essere distorto dalla progressione naturale (Climbing). Intra-Session è il più affidabile.\n")
        f.write("="*80 + "\n")
        f.write(f"Totale Battaglie: {total_battles}\n")
        f.write(f"Totale Finestre (Opportunità): {total_opportunities}\n")
        f.write(f"Soglie: Vantaggio > {HIGH_THRESH}, Svantaggio < {LOW_THRESH} (Delta Livello)\n")
        f.write("-" * 80 + "\n")
        
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

        write_section(f"Vantaggio Livelli (> {HIGH_THRESH})", obs_high_streaks, exp_high_theory, avg_global_high, avg_intra_high)
        write_section(f"Svantaggio Livelli (< {LOW_THRESH})", obs_low_streaks, exp_low_theory, avg_global_low, avg_intra_low)
        
        f.write("="*80 + "\n")

def analyze_normalized_level_streak(players_sessions, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'normalized_level_streak_results.txt')

    print(f"\nGenerazione report streak livelli NORMALIZZATI (Z-Score) in: {output_file}")

    # 1. Ricostruzione Trofei e Raccolta Dati per Baseline
    # Bucket size per calcolare media/std locali
    BUCKET_SIZE = 200 
    bucket_stats = {} # { bucket_index: [list_of_level_diffs] }
    global_level_diffs = [] # Fallback per chi non ha trofei

    # Struttura temporanea per salvare i dati arricchiti
    enriched_battles = [] # list of (player_tag, session_idx, battle_idx, z_score)
    
    processed_players = 0
    processed_battles = 0

    for p in players_sessions:
        current_trophies = p['profile'].get('trophies') if p['profile'] else None
        # if not current_trophies: continue # RIMOSSO: Non saltiamo chi non ha trofei

        # Iteriamo le sessioni dalla più recente alla più vecchia per ricostruire i trofei
        # Assumiamo che p['sessions'] sia ordinato cronologicamente o inversamente. 
        # Solitamente i log sono Newest -> Oldest. Verifichiamo timestamp.
        # Per semplicità, assumiamo l'ordine di lista e ricostruiamo a ritroso.
        
        # Appiattiamo tutte le battaglie del player in ordine inverso (dalla più recente)
        all_battles_rev = []
        for s_idx, s in enumerate(p['sessions']):
            for b_idx, b in enumerate(s['battles']):
                all_battles_rev.append((s_idx, b_idx, b))
        
        # Se i timestamp sono crescenti, invertiamo. Se decrescenti (log tipico), ok.
        # Controlliamo i primi due per capire l'ordine
        if len(all_battles_rev) > 1:
            t1 = all_battles_rev[0][2]['timestamp']
            t2 = all_battles_rev[-1][2]['timestamp']
            if t1 < t2: # Ordine cronologico (Old -> New), invertiamo per partire dal current
                all_battles_rev.reverse()

        simulated_trophies = current_trophies
        
        for s_idx, b_idx, b in all_battles_rev:
            if b['game_mode'] not in ['Ladder', 'Ranked']: continue
            
            lvl_diff = b.get('level_diff')
            if lvl_diff is not None:
                processed_battles += 1
                global_level_diffs.append(lvl_diff)
                
                if simulated_trophies is not None:
                    bucket_idx = simulated_trophies // BUCKET_SIZE
                    if bucket_idx not in bucket_stats: bucket_stats[bucket_idx] = []
                    bucket_stats[bucket_idx].append(lvl_diff)
                
                # Salviamo riferimento per dopo
                enriched_battles.append({
                    'tag': p['tag'],
                    's_idx': s_idx,
                    'lvl_diff': lvl_diff,
                    'trophies': simulated_trophies
                })

            # Aggiorna trofei per il prossimo passo (indietro nel tempo)
            # Se ho vinto +30, prima ne avevo 30 in meno.
            if simulated_trophies is not None:
                change = b.get('trophy_change')
                if change is not None:
                    if b['win']: simulated_trophies -= change
                    else: simulated_trophies += change 
        
        processed_players += 1

    print(f"Dati processati: {processed_players} giocatori, {processed_battles} battaglie.")

    # 2. Calcolo Statistiche per Bucket (Mean, Std)
    bucket_metrics = {}
    for idx, values in bucket_stats.items():
        if len(values) > 5: # Minimo campione
            bucket_metrics[idx] = {
                'mean': statistics.mean(values),
                'std': statistics.stdev(values) if len(values) > 1 else 1.0
            }
            
    # Statistiche Globali (Fallback)
    global_mean = statistics.mean(global_level_diffs) if global_level_diffs else 0
    global_std = statistics.stdev(global_level_diffs) if len(global_level_diffs) > 1 else 1.0
    print(f"Global Stats (Fallback): Mean={global_mean:.3f}, Std={global_std:.3f}")

    # 3. Calcolo Z-Score e Analisi Streak
    # Riorganizziamo i dati per player/sessione per l'analisi streak
    player_data_map = {} # tag -> { s_idx -> [z_scores] }

    for entry in enriched_battles:
        metrics = None
        if entry['trophies'] is not None:
            b_idx = entry['trophies'] // BUCKET_SIZE
            metrics = bucket_metrics.get(b_idx)
        
        if metrics and metrics['std'] > 0:
            z = (entry['lvl_diff'] - metrics['mean']) / metrics['std']
        else:
            # Fallback su Global Stats se mancano trofei o bucket vuoto
            z = (entry['lvl_diff'] - global_mean) / global_std
            
        tag = entry['tag']
        s_idx = entry['s_idx']
        
        if tag not in player_data_map: player_data_map[tag] = {}
        if s_idx not in player_data_map[tag]: player_data_map[tag][s_idx] = []
        
        player_data_map[tag][s_idx].append(z)

    # Analisi Streak su Z-Score
    # Z < -1.5 indica uno svantaggio ANOMALO per quella fascia di trofei
    Z_THRESH = -2
    STREAK_LEN = 3
    
    obs_streaks = 0
    total_opps = 0
    
    # Per simulazione
    players_sim_data = [] # list of (flat_z, lengths)

    for tag, sessions_map in player_data_map.items():
        sorted_s_idxs = sorted(sessions_map.keys())
        
        p_z_flat = []
        p_lengths = []
        
        for s_idx in sorted_s_idxs:
            z_list = sessions_map[s_idx]
            # z_list è popolata Newest->Oldest (perché enriched_battles è reverse)
            z_list.reverse() 
            
            # Analisi Streak Osservata (Per Sessione)
            if len(z_list) >= STREAK_LEN:
                for i in range(len(z_list) - STREAK_LEN + 1):
                    total_opps += 1
                    if all(z < Z_THRESH for z in z_list[i:i+STREAK_LEN]):
                        obs_streaks += 1
            
            p_z_flat.extend(z_list)
            p_lengths.append(len(z_list))
            
        if p_z_flat:
            players_sim_data.append((p_z_flat, p_lengths))

    # Simulazione Global Shuffle (ora valida perché detrendizzata)
    sim_streaks_global = 0
    sim_streaks_intra = 0
    NUM_SIM = 1000
    
    for _ in range(NUM_SIM):
        for z_flat, lengths in players_sim_data:
            # --- Global Shuffle ---
            shuffled = z_flat[:]
            random.shuffle(shuffled)
            
            idx = 0
            for l in lengths:
                s = shuffled[idx : idx+l]
                idx += l
                if len(s) >= STREAK_LEN:
                    for i in range(len(s) - STREAK_LEN + 1):
                        if all(z < Z_THRESH for z in s[i:i+STREAK_LEN]):
                            sim_streaks_global += 1
            
            # --- Intra-Session Shuffle ---
            idx = 0
            for l in lengths:
                s_orig = z_flat[idx : idx+l]
                idx += l
                s_intra = s_orig[:]
                random.shuffle(s_intra)
                
                if len(s_intra) >= STREAK_LEN:
                    for i in range(len(s_intra) - STREAK_LEN + 1):
                        if all(z < Z_THRESH for z in s_intra[i:i+STREAK_LEN]):
                            sim_streaks_intra += 1
    
    avg_sim_global = sim_streaks_global / NUM_SIM
    avg_sim_intra = sim_streaks_intra / NUM_SIM

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI STREAK LIVELLI NORMALIZZATI (Z-SCORE)\n")
        f.write("Metodo: Normalizzazione per fascia trofei (Bucket 200). Z = (Diff - Mean) / Std.\n")
        f.write("Obiettivo: Rilevare anomalie di matchmaking indipendenti dalla progressione naturale.\n")
        f.write("="*80 + "\n")
        f.write(f"Soglia Z-Score (Svantaggio Anomalo): < {Z_THRESH}\n")
        f.write(f"Totale Opportunità: {total_opps}\n")
        f.write("-" * 80 + "\n")
        f.write(f"{'METODO':<25} | {'STREAK COUNT':<15} | {'RATIO':<10}\n")
        f.write("-" * 80 + "\n")
        f.write(f"{'Osservato':<25} | {obs_streaks:<15} | 1.00x\n")
        f.write(f"{'Global Shuffle':<25} | {avg_sim_global:<15.2f} | {obs_streaks/avg_sim_global if avg_sim_global else 0:.2f}x\n")
        f.write(f"{'Intra-Session Shuffle':<25} | {avg_sim_intra:<15.2f} | {obs_streaks/avg_sim_intra if avg_sim_intra else 0:.2f}x\n")
        f.write("-" * 80 + "\n")
        f.write("INTERPRETAZIONE:\n")
        f.write("1. Ratio Global > 1: Le partite 'sfortunate' sono raggruppate in sessioni specifiche (Bad Sessions).\n")
        f.write("2. Ratio Intra > 1: L'ordine delle partite nella sessione è manipolato per creare filotti negativi.\n")
        f.write("="*80 + "\n")

def analyze_pity_probability_lift(players_sessions, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'pity_probability_lift_results.txt')

    print(f"\nGenerazione report Pity Probability Lift in: {output_file}")

    PITY_THRESH = 60.0
    STREAK_LEN = 3

    # Accumulatori Globali
    global_baseline_opportunities = 0
    global_baseline_successes = 0
    
    global_streak_opportunities = 0
    global_streak_successes = 0

    for p in players_sessions:
        for s in p['sessions']:
            battles = s['battles']
            n = len(battles)
            if n < STREAK_LEN + 1: continue

            # 1. Calcolo Baseline (Tutte le partite valide)
            for b in battles:
                if b['matchup'] is not None:
                    global_baseline_opportunities += 1
                    if b['matchup'] > PITY_THRESH:
                        global_baseline_successes += 1

            # 2. Calcolo Post-Streak
            for i in range(n - STREAK_LEN):
                # Finestra di 3 sconfitte
                window = battles[i : i+STREAK_LEN]
                next_b = battles[i+STREAK_LEN]
                
                if next_b['matchup'] is None: continue
                
                # Verifica Streak Sconfitte
                if all(b['win'] == 0 for b in window):
                    global_streak_opportunities += 1
                    if next_b['matchup'] > PITY_THRESH:
                        global_streak_successes += 1

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI PITY PROBABILITY LIFT (BASELINE vs STREAK)\n")
        f.write("Obiettivo: Verificare se la probabilità di ricevere un Matchup > 60% aumenta dopo 3 sconfitte rispetto alla media globale.\n")
        f.write("="*80 + "\n\n")
        
        baseline_rate = global_baseline_successes / global_baseline_opportunities if global_baseline_opportunities > 0 else 0
        streak_rate = global_streak_successes / global_streak_opportunities if global_streak_opportunities > 0 else 0
        lift = streak_rate / baseline_rate if baseline_rate > 0 else 0

        f.write(f"Baseline Pity Rate (Globale): {baseline_rate*100:.2f}% ({global_baseline_successes}/{global_baseline_opportunities})\n")
        f.write(f"Post-Streak Pity Rate (Dopo 3 Loss): {streak_rate*100:.2f}% ({global_streak_successes}/{global_streak_opportunities})\n")
        f.write(f"LIFT (Aumento Probabilità): {lift:.2f}x\n")
        f.write("-" * 80 + "\n")
        
        # Binomial Test
        # H0: La probabilità dopo streak è uguale alla baseline
        # H1: La probabilità dopo streak è MAGGIORE della baseline
        res = binomtest(k=global_streak_successes, n=global_streak_opportunities, p=baseline_rate, alternative='greater')
        
        f.write(f"Test Binomiale (Streak Rate > Baseline Rate):\n")
        f.write(f"P-value: {res.pvalue:.6f}\n")
        
        if res.pvalue < 0.05:
            f.write("RISULTATO: SIGNIFICATIVO. Il sistema aumenta artificialmente la probabilità di vittoria dopo le sconfitte.\n")
        else:
            f.write("RISULTATO: NON SIGNIFICATIVO. La frequenza di aiuti dopo le sconfitte è in linea con la media normale.\n")
        f.write("="*80 + "\n")


def analyze_paywall_impact(players_sessions, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'paywall_impact_results.txt')

    print(f"\nGenerazione report Paywall Impact in: {output_file}")

    # Bucket size per controllare la "Progressione Naturale"
    # Usiamo un range sufficientemente ampio per avere dati, ma stretto per considerare i livelli costanti
    BUCKET_SIZE = 400
    
    # Struttura: bucket -> { 'after_win': [], 'after_loss': [] }
    buckets = {}

    for p in players_sessions:
        # Appiattiamo le sessioni per avere la sequenza temporale completa
        all_battles = []
        for s in p['sessions']:
            all_battles.extend(s['battles'])
            
        for i in range(1, len(all_battles)):
            prev = all_battles[i-1]
            curr = all_battles[i]
            
            if curr['game_mode'] != 'Ladder': continue
            
            trophies = curr.get('trophies_before')
            if not trophies: continue
            
            lvl_diff = curr.get('level_diff')
            if lvl_diff is None: continue
            
            # Identifica il bucket di trofei
            bucket_idx = (trophies // BUCKET_SIZE) * BUCKET_SIZE
            bucket_label = f"{bucket_idx}-{bucket_idx + BUCKET_SIZE}"
            
            if bucket_label not in buckets:
                buckets[bucket_label] = {'after_win': [], 'after_loss': []}
            
            # Classifica in base all'esito precedente
            if prev['win']:
                buckets[bucket_label]['after_win'].append(lvl_diff)
            else:
                buckets[bucket_label]['after_loss'].append(lvl_diff)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI PAYWALL: PROGRESSIONE NATURALE vs MANIPOLAZIONE ATTIVA\n")
        f.write("Obiettivo: Rispondere alla critica 'È normale trovare livelli più alti salendo di trofei'.\n")
        f.write("Metodo: Confronto il Level Diff DOPO UNA VITTORIA vs DOPO UNA SCONFITTA all'interno della STESSA fascia di trofei.\n")
        f.write(f"Ipotesi Naturale: In un range ristretto ({BUCKET_SIZE} trofei), il livello medio degli avversari dovrebbe essere costante.\n")
        f.write("Ipotesi Paywall: Se dopo una vittoria il livello avversario sale drasticamente rispetto a dopo una sconfitta (nello stesso bucket), è manipolazione.\n")
        f.write("="*100 + "\n")
        f.write(f"{'FASCIA TROFEI':<15} | {'N. MATCH':<10} | {'AVG L.DIFF (Tot)':<18} | {'Post-Win':<12} | {'Post-Loss':<12} | {'DELTA':<10} | {'P-VALUE':<10}\n")
        f.write("-" * 100 + "\n")

        sorted_keys = sorted(buckets.keys(), key=lambda x: int(x.split('-')[0]))

        for key in sorted_keys:
            data = buckets[key]
            wins = data['after_win']
            losses = data['after_loss']
            
            n_tot = len(wins) + len(losses)
            if n_tot < 50 or len(wins) < 10 or len(losses) < 10: 
                continue 
            
            avg_win = statistics.mean(wins)
            avg_loss = statistics.mean(losses)
            avg_tot = statistics.mean(wins + losses) # Media globale del bucket
            delta = avg_win - avg_loss # Se negativo, Post-Win è peggio (avversario più forte)
            
            # Mann-Whitney U Test
            # H1: Post-Win < Post-Loss (Livelli peggiori dopo vittoria)
            try:
                stat, p_val = mannwhitneyu(wins, losses, alternative='less')
            except ValueError:
                p_val = 1.0
            
            marker = ""
            if p_val < 0.05 and delta < -0.1:
                marker = "<-- RIGGED?"
            
            f.write(f"{key:<15} | {n_tot:<10} | {avg_tot:<18.2f} | {avg_win:<12.2f} | {avg_loss:<12.2f} | {delta:<10.2f} | {p_val:<10.4f} {marker}\n")

        f.write("-" * 100 + "\n")
        f.write("INTERPRETAZIONE:\n")
        f.write("1. AVG L.DIFF (Tot): Se diventa sempre più negativo salendo di trofei, conferma il 'Paywall Statico' (Progressione Naturale).\n")
        f.write("2. DELTA ~ 0: Conferma che il sistema NON manipola i livelli in base all'esito della partita precedente.\n")
        f.write("3. RIGGED?: Solo se Delta è significativamente negativo e P-Value < 0.05 c'è sospetto di manipolazione attiva.\n")
        f.write("="*100 + "\n")

def analyze_nolvl_streaks_vs_trophies(players_sessions, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'nolvl_streaks_vs_trophies_results.txt')

    print(f"\nGenerazione report Streak No-Lvl vs Trofei in: {output_file}")

    STREAK_LEN = 3
    BAD_THRESH = 45.0
    GOOD_THRESH = 55.0
    WINDOW_SIZE = 200  # Finestra mobile per la media
    MIN_HISTORY = 10   # Minimo partite precedenti per calcolare la media
    
    # Accumulatori globali
    total_battles_above = 0
    total_battles_below = 0
    total_battles_total = 0
    
    streaks_bad_above = 0
    streaks_bad_total = 0
    streaks_good_below = 0
    streaks_good_total = 0
    
    # Per analisi distribuzione
    streak_bad_deltas = [] # (Streak Avg Trophies - Player Avg Trophies)
    streak_good_deltas = []

    for p in players_sessions:
        # 1. Preparazione Dati (Solo Ladder)
        ladder_battles = []
        for s in p['sessions']:
            for b in s['battles']:
                if b['game_mode'] == 'Ladder' and b.get('trophies_before') and b.get('matchup_no_lvl') is not None:
                    ladder_battles.append(b)
        
        if len(ladder_battles) < MIN_HISTORY:
            continue

        # 2. Calcolo Baseline (Tempo speso sopra la media mobile)
        for i in range(len(ladder_battles)):
            # Definisci finestra storica (es. ultimi 200 match prima di i)
            start_idx = max(0, i - WINDOW_SIZE)
            history = ladder_battles[start_idx : i]
            
            if len(history) < MIN_HISTORY:
                continue
            
            avg_trophies = statistics.mean([h['trophies_before'] for h in history])
            curr_trophies = ladder_battles[i]['trophies_before']
            
            total_battles_total += 1
            if curr_trophies > avg_trophies:
                total_battles_above += 1
            elif curr_trophies < avg_trophies:
                total_battles_below += 1
        
        # 3. Identificazione Streak
        if len(ladder_battles) >= STREAK_LEN:
            for i in range(len(ladder_battles) - STREAK_LEN + 1):
                # Finestra storica relativa all'inizio della streak
                start_idx = max(0, i - WINDOW_SIZE)
                history = ladder_battles[start_idx : i]
                
                if len(history) < MIN_HISTORY:
                    continue
                
                avg_trophies_hist = statistics.mean([h['trophies_before'] for h in history])
                
                window = ladder_battles[i : i+STREAK_LEN]
                
                # Verifica se è una Bad Streak No-Lvl
                if all(b['matchup_no_lvl'] < BAD_THRESH for b in window):
                    streaks_bad_total += 1
                    
                    # Calcola trofei medi durante la streak
                    avg_streak_trophies = statistics.mean([b['trophies_before'] for b in window])
                    
                    streak_bad_deltas.append(avg_streak_trophies - avg_trophies_hist)
                    
                    if avg_streak_trophies > avg_trophies_hist:
                        streaks_bad_above += 1

                # Verifica se è una Good Streak No-Lvl
                if all(b['matchup_no_lvl'] > GOOD_THRESH for b in window):
                    streaks_good_total += 1
                    avg_streak_trophies = statistics.mean([b['trophies_before'] for b in window])
                    streak_good_deltas.append(avg_streak_trophies - avg_trophies_hist)
                    
                    if avg_streak_trophies < avg_trophies_hist:
                        streaks_good_below += 1

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI STREAK NO-LVL vs POSIZIONE TROFEI (MOVING AVERAGE)\n")
        f.write("Obiettivo: Capire se le serie di matchup negativi/positivi dipendono dalla posizione in classifica.\n")
        f.write(f"Metodo: Confronto con media mobile degli ultimi {WINDOW_SIZE} match (Dynamic Baseline).\n")
        f.write("="*80 + "\n\n")
        
        if total_battles_total == 0:
            f.write("Dati insufficienti.\n")
            return

        # --- BAD STREAK ANALYSIS ---
        baseline_above_rate = total_battles_above / total_battles_total
        streak_bad_above_rate = streaks_bad_above / streaks_bad_total if streaks_bad_total > 0 else 0
        
        f.write("1. BAD STREAK (Matchup < 45%) vs HIGH TROPHIES (Sopra Media)\n")
        f.write("Ipotesi Naturale: Più sali, più trovi counter (Concentrazione in alto).\n")
        f.write("-" * 80 + "\n")
        f.write(f"Totale Bad Streak: {streaks_bad_total}\n")
        f.write(f"Baseline (Tempo speso sopra media): {baseline_above_rate*100:.2f}%\n")
        f.write(f"Bad Streak avvenute sopra media:    {streak_bad_above_rate*100:.2f}%\n")
        
        lift_bad = streak_bad_above_rate / baseline_above_rate if baseline_above_rate > 0 else 0
        f.write(f"LIFT: {lift_bad:.2f}x\n")
        
        res_bad = binomtest(k=streaks_bad_above, n=streaks_bad_total, p=baseline_above_rate, alternative='greater')
        f.write(f"P-value (Binomial): {res_bad.pvalue:.6f}\n")
        
        if res_bad.pvalue < 0.05:
            f.write("RISULTATO: SIGNIFICATIVO. Le Bad Streak si concentrano quando sei in alto (Gatekeeping).\n")
        else:
            f.write("RISULTATO: NON SIGNIFICATIVO. Le Bad Streak colpiscono ovunque (Forzatura 50%).\n")
        
        avg_delta_bad = statistics.mean(streak_bad_deltas) if streak_bad_deltas else 0
        f.write(f"Delta Medio Trofei (Bad Streak): {avg_delta_bad:+.2f}\n\n")

        # --- GOOD STREAK ANALYSIS ---
        baseline_below_rate = total_battles_below / total_battles_total
        streak_good_below_rate = streaks_good_below / streaks_good_total if streaks_good_total > 0 else 0
        
        f.write("2. GOOD STREAK (Matchup > 55%) vs LOW TROPHIES (Sotto Media)\n")
        f.write("Ipotesi Recupero: Quando scendi troppo, il sistema ti aiuta a risalire (Concentrazione in basso).\n")
        f.write("-" * 80 + "\n")
        f.write(f"Totale Good Streak: {streaks_good_total}\n")
        f.write(f"Baseline (Tempo speso sotto media): {baseline_below_rate*100:.2f}%\n")
        f.write(f"Good Streak avvenute sotto media:   {streak_good_below_rate*100:.2f}%\n")
        
        lift_good = streak_good_below_rate / baseline_below_rate if baseline_below_rate > 0 else 0
        f.write(f"LIFT: {lift_good:.2f}x\n")
        
        res_good = binomtest(k=streaks_good_below, n=streaks_good_total, p=baseline_below_rate, alternative='greater')
        f.write(f"P-value (Binomial): {res_good.pvalue:.6f}\n")
        
        if res_good.pvalue < 0.05:
            f.write("RISULTATO: SIGNIFICATIVO. Le Good Streak si concentrano quando sei in basso (Rubber Banding / Aiutino).\n")
        else:
            f.write("RISULTATO: NON SIGNIFICATIVO. Le Good Streak sono casuali.\n")
            
        avg_delta_good = statistics.mean(streak_good_deltas) if streak_good_deltas else 0
        f.write(f"Delta Medio Trofei (Good Streak): {avg_delta_good:+.2f}\n")
        
        f.write("="*80 + "\n")

def analyze_meta_ranges(players_sessions, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'meta_ranges_results.txt')

    print(f"\nGenerazione report Meta Ranges in: {output_file}")

    BUCKET_SIZE = 200
    buckets = {} # { range_start: [matchups] }

    for p in players_sessions:
        for s in p['sessions']:
            for b in s['battles']:
                if b['game_mode'] == 'Ladder' and b.get('trophies_before') and b.get('matchup_no_lvl') is not None:
                    t = b['trophies_before']
                    b_idx = (t // BUCKET_SIZE) * BUCKET_SIZE
                    if b_idx not in buckets: buckets[b_idx] = []
                    buckets[b_idx].append(b['matchup_no_lvl'])

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI META RANGES (DISTRIBUZIONE MATCHUP NO-LVL PER TROFEI)\n")
        f.write("Obiettivo: Verificare se esistono 'fasce di trofei maledette' dove il matchup medio crolla (Meta Ranges).\n")
        f.write(f"Bucket Size: {BUCKET_SIZE} trofei\n")
        f.write("="*80 + "\n\n")
        
        sorted_keys = sorted(buckets.keys())
        valid_buckets = []
        
        f.write(f"{'RANGE TROFEI':<20} | {'N. MATCH':<10} | {'AVG MATCHUP':<15} | {'STD DEV':<10}\n")
        f.write("-" * 65 + "\n")
        
        for k in sorted_keys:
            vals = buckets[k]
            if len(vals) < 50: continue # Skip low sample
            
            avg = statistics.mean(vals)
            std = statistics.stdev(vals)
            f.write(f"{k}-{k+BUCKET_SIZE:<15} | {len(vals):<10} | {avg:<15.2f}% | {std:<10.2f}\n")
            valid_buckets.append(vals)
            
        f.write("-" * 65 + "\n")
        
        if len(valid_buckets) > 1:
            stat, p_val = kruskal(*valid_buckets)
            f.write(f"Test Kruskal-Wallis (Differenza tra fasce): p-value = {p_val:.4f}\n")
            if p_val < 0.05:
                f.write("RISULTATO: SIGNIFICATIVO. Il matchup medio cambia in base alla fascia di trofei (Meta Ranges confermati).\n")
                f.write("NOTA: Questo supporta l'ipotesi che alcune 'Bad Streak' siano dovute al meta locale.\n")
            else:
                f.write("RISULTATO: NON SIGNIFICATIVO. Il matchup medio è costante attraverso i trofei.\n")
                f.write("NOTA: Questo indebolisce l'ipotesi dei Meta Ranges come causa principale.\n")
        
        f.write("="*80 + "\n")

def analyze_climbing_impact(players_sessions, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'climbing_impact_results.txt')

    print(f"\nGenerazione report Impatto Climbing in: {output_file}")
    
    correlations_mu = []
    correlations_mu_nolvl = []
    correlations_lvl = []
    
    for p in players_sessions:
        # Matchup
        t_mu, v_mu = [], [] # (trophies, matchup)
        # Matchup No Lvl
        t_mnl, v_mnl = [], []
        # Level Diff
        t_lvl, v_lvl = [], []

        for s in p['sessions']:
            for b in s['battles']:
                if b['game_mode'] == 'Ladder' and b.get('trophies_before'):
                    t = b['trophies_before']
                    
                    if b.get('matchup') is not None:
                        t_mu.append(t)
                        v_mu.append(b['matchup'])
                    
                    if b.get('matchup_no_lvl') is not None:
                        t_mnl.append(t)
                        v_mnl.append(b['matchup_no_lvl'])
                        
                    if b.get('level_diff') is not None:
                        t_lvl.append(t)
                        v_lvl.append(b['level_diff'])
        
        if len(t_mu) > 20:
            c, p_val = spearmanr(t_mu, v_mu)
            if not np.isnan(c): correlations_mu.append((c, p_val))
            
        if len(t_mnl) > 20:
            c, p_val = spearmanr(t_mnl, v_mnl)
            if not np.isnan(c): correlations_mu_nolvl.append((c, p_val))
            
        if len(t_lvl) > 20:
            c, p_val = spearmanr(t_lvl, v_lvl)
            if not np.isnan(c): correlations_lvl.append((c, p_val))

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI IMPATTO CLIMBING (TROFEI vs METRICHE)\n")
        f.write("Obiettivo: Verificare se salire di trofei porta naturalmente a condizioni peggiori (Correlazione Negativa).\n")
        f.write("="*80 + "\n\n")
        
        def write_section(title, data):
            if not data:
                f.write(f"--- {title} ---\nDati insufficienti.\n\n")
                return
            
            corrs = [x[0] for x in data]
            
            avg_corr = statistics.mean(corrs)
            
            # Significant counts (p < 0.05)
            sig_pos = len([x for x in data if x[0] > 0 and x[1] < 0.05])
            sig_neg = len([x for x in data if x[0] < 0 and x[1] < 0.05])
            
            f.write(f"--- {title} ---\n")
            f.write(f"Player Analizzati: {len(data)}\n")
            f.write(f"Correlazione Media (Spearman): {avg_corr:.4f}\n")
            f.write(f"Significativi Positivi (p<0.05): {sig_pos}\n")
            f.write(f"Significativi Negativi (p<0.05): {sig_neg}\n")
            f.write("-" * 40 + "\n")

        write_section("1. MATCHUP (Reale)", correlations_mu)
        write_section("2. MATCHUP NO-LVL (Deck)", correlations_mu_nolvl)
        write_section("3. LEVEL DIFF", correlations_lvl)
        
        f.write("INTERPRETAZIONE:\n")
        f.write("1. Correlazione Negativa su Matchup: Salendo trovi counter.\n")
        f.write("2. Correlazione Negativa su Level Diff: Salendo trovi avversari più forti (livelli più alti).\n")
        f.write("="*80 + "\n")

def analyze_hook_by_trophy_range(players_sessions, output_dir=None, cursor=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'hook_by_trophy_range_results.txt')

    print(f"\nGenerazione report Hook Consistency (Session Trend per Fascia) in: {output_file}")

    # Fetch arenas if cursor present
    arenas = []
    if cursor:
        try:
            cursor.execute("SELECT arena_id, trophy_limit FROM arenas ORDER BY trophy_limit ASC")
            arenas = cursor.fetchall() # List of (id, limit)
        except Exception as e:
            print(f"Error fetching arenas: {e}")

    # { range_start: { 'sessions': 0, 'hook': {...}, 'rest': {...} } }
    buckets = {}

    for p in players_sessions:
        for s in p['sessions']:
            if len(s['battles']) <= 3: continue
            
            # Determina fascia trofei dalla prima battaglia
            first_b = s['battles'][0]
            t = first_b.get('trophies_before')
            if not t: continue
            
            b_idx = 0
            b_label = ""
            
            if arenas:
                current_limit = 0
                next_limit = "Inf"
                for i, (aid, limit) in enumerate(arenas):
                    if t >= limit:
                        current_limit = limit
                        if i + 1 < len(arenas):
                            next_limit = arenas[i+1][1]
                        else:
                            next_limit = "Inf"
                    else:
                        break
                b_idx = current_limit
                b_label = f"{current_limit}-{next_limit}"
            else:
                # Fallback
                b_idx = (t // 1000) * 1000
                b_label = f"{b_idx}-{b_idx+1000}"

            if b_idx not in buckets:
                buckets[b_idx] = {
                    'label': b_label,
                    'sessions': 0,
                    'hook': {'wins': 0, 'tot': 0, 'mu_sum': 0, 'mu_count': 0, 'lvl_sum': 0, 'lvl_count': 0},
                    'rest': {'wins': 0, 'tot': 0, 'mu_sum': 0, 'mu_count': 0, 'lvl_sum': 0, 'lvl_count': 0}
                }
            
            buckets[b_idx]['sessions'] += 1
            
            # Helper per processare le slice
            def process_slice(slice_battles, key):
                b_data = buckets[b_idx][key]
                b_data['wins'] += sum(1 for b in slice_battles if b['win'])
                b_data['tot'] += len(slice_battles)
                
                for b in slice_battles:
                    if b.get('matchup') is not None:
                        b_data['mu_sum'] += b['matchup']
                        b_data['mu_count'] += 1
                    if b.get('level_diff') is not None:
                        b_data['lvl_sum'] += b['level_diff']
                        b_data['lvl_count'] += 1

            process_slice(s['battles'][:3], 'hook')
            process_slice(s['battles'][3:], 'rest')
            

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI CONSISTENZA HOOK PER FASCIA DI TROFEI (WIN RATE, MATCHUP, LIVELLI)\n")
        f.write("Obiettivo: Distinguere tra Skill del Giocatore (Win Rate) e Aiuto del Sistema (Matchup/Livelli).\n")
        f.write("Ipotesi: Se il Matchup/Livelli sono migliori all'inizio, è manipolazione (Hook). Se solo WR è migliore, è freschezza mentale.\n")
        f.write("="*140 + "\n")
        f.write(f"{'FASCIA':<12} | {'SESS':<5} | {'HOOK WR':<9} {'REST WR':<9} {'Δ WR':<7} | {'HOOK MU':<9} {'REST MU':<9} {'Δ MU':<7} | {'HOOK LVL':<9} {'REST LVL':<9} {'Δ LVL':<7}\n")
        f.write("-" * 140 + "\n")

        for k in sorted(buckets.keys()):
            d = buckets[k]
            if d['sessions'] < 20: continue # Filtra fasce con pochi dati
            
            # Win Rate
            h_wr = (d['hook']['wins'] / d['hook']['tot'] * 100) if d['hook']['tot'] else 0
            r_wr = (d['rest']['wins'] / d['rest']['tot'] * 100) if d['rest']['tot'] else 0
            d_wr = r_wr - h_wr
            
            # Matchup
            h_mu = (d['hook']['mu_sum'] / d['hook']['mu_count']) if d['hook']['mu_count'] else 0
            r_mu = (d['rest']['mu_sum'] / d['rest']['mu_count']) if d['rest']['mu_count'] else 0
            d_mu = r_mu - h_mu
            
            # Levels
            h_lvl = (d['hook']['lvl_sum'] / d['hook']['lvl_count']) if d['hook']['lvl_count'] else 0
            r_lvl = (d['rest']['lvl_sum'] / d['rest']['lvl_count']) if d['rest']['lvl_count'] else 0
            d_lvl = r_lvl - h_lvl
            
            f.write(f"{d['label']:<12} | {d['sessions']:<5} | "
                    f"{h_wr:<9.1f} {r_wr:<9.1f} {d_wr:<+7.1f} | "
                    f"{h_mu:<9.1f} {r_mu:<9.1f} {d_mu:<+7.1f} | "
                    f"{h_lvl:<+9.2f} {r_lvl:<+9.2f} {d_lvl:<+7.2f}\n")
            
        f.write("="*140 + "\n")

def analyze_skill_vs_matchup_dominance(players_sessions, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'skill_vs_matchup_dominance.txt')

    print(f"\nGenerazione report Skill vs Matchup Dominance in: {output_file}")

    # Definizioni
    BAD_MU = 45.0
    GOOD_MU = 55.0
    
    # Matrice Risultati: [MatchupType][SkillDiff] -> {wins, total}
    # MatchupType: 'Bad', 'Even', 'Good'
    # SkillDiff (Net Elixir): 'Better' (Player leaked less), 'Worse' (Player leaked more), 'Equal'
    matrix = {
        'Bad':   {'Better': {'w':0, 't':0}, 'Worse': {'w':0, 't':0}, 'Equal': {'w':0, 't':0}},
        'Even':  {'Better': {'w':0, 't':0}, 'Worse': {'w':0, 't':0}, 'Equal': {'w':0, 't':0}},
        'Good':  {'Better': {'w':0, 't':0}, 'Worse': {'w':0, 't':0}, 'Equal': {'w':0, 't':0}}
    }
    
    # Per Analisi Pressione: Raccogliamo quanto elisir leaka il player in base al matchup
    pressure_stats = {'Bad': [], 'Good': [], 'Even': []}

    for p in players_sessions:
        for s in p['sessions']:
            for b in s['battles']:
                mu = b.get('matchup')
                p_leak = b.get('elixir_leaked_player')
                o_leak = b.get('elixir_leaked_opponent')
                win = b['win']
                
                if mu is None or p_leak is None or o_leak is None: continue
                
                # 1. Classifica Matchup
                if mu < BAD_MU: mu_type = 'Bad'
                elif mu > GOOD_MU: mu_type = 'Good'
                else: mu_type = 'Even'
                
                # 2. Classifica Skill (Efficienza Elisir)
                # Se io leako MENO dell'avversario, ho giocato "Meglio" (Better)
                if p_leak < o_leak: skill_type = 'Better'
                elif p_leak > o_leak: skill_type = 'Worse'
                else: skill_type = 'Equal'
                
                # Aggiorna Matrice
                matrix[mu_type][skill_type]['t'] += 1
                if win: matrix[mu_type][skill_type]['w'] += 1
                
                # Aggiorna Pressione
                pressure_stats[mu_type].append(p_leak)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI SKILL vs MATCHUP DOMINANCE\n")
        f.write("Obiettivo: Capire se giocare meglio (Skill) è sufficiente a ribaltare un Matchup Sfavorevole.\n")
        f.write("Metodo: Skill misurata come 'Efficienza Elisir' (Net Elixir Leaked).\n")
        f.write("        'Better Skill' = Il giocatore ha sprecato MENO elisir dell'avversario.\n")
        f.write("="*100 + "\n")
        
        f.write(f"{'MATCHUP':<10} | {'SKILL (vs Opp)':<15} | {'N. MATCH':<10} | {'WIN RATE':<10} | {'INTERPRETAZIONE'}\n")
        f.write("-" * 100 + "\n")
        
        for mu_type in ['Bad', 'Even', 'Good']:
            for skill_type in ['Better', 'Worse']: # Ignoriamo Equal per chiarezza
                d = matrix[mu_type][skill_type]
                if d['t'] < 10: continue
                
                wr = (d['w'] / d['t']) * 100
                
                interp = ""
                if mu_type == 'Bad' and skill_type == 'Better':
                    interp = "-> SKILL UPSET? (Riesci a vincere contro i pronostici?)"
                elif mu_type == 'Good' and skill_type == 'Worse':
                    interp = "-> DECK CARRY? (Vinci anche giocando male?)"
                
                f.write(f"{mu_type:<10} | {skill_type:<15} | {d['t']:<10} | {wr:<10.2f}% | {interp}\n")
            f.write("-" * 100 + "\n")
            
        f.write("\n" + "="*100 + "\n")
        f.write("ANALISI PRESSIONE PSICOLOGICA (Il Counter fa sbagliare?)\n")
        f.write("Ipotesi: Se il giocatore spreca più elisir nei Bad Matchup, la sconfitta è parzialmente colpa della pressione.\n")
        f.write("-" * 100 + "\n")
        
        avg_leak_bad = statistics.mean(pressure_stats['Bad']) if pressure_stats['Bad'] else 0
        avg_leak_good = statistics.mean(pressure_stats['Good']) if pressure_stats['Good'] else 0
        
        f.write(f"Avg Elixir Leaked in BAD Matchup:  {avg_leak_bad:.4f}\n")
        f.write(f"Avg Elixir Leaked in GOOD Matchup: {avg_leak_good:.4f}\n")
        
        delta = avg_leak_bad - avg_leak_good
        f.write(f"Delta (Bad - Good): {delta:+.4f}\n")
        
        stat, p_val = mannwhitneyu(pressure_stats['Bad'], pressure_stats['Good'], alternative='greater')
        f.write(f"Test Mann-Whitney U (Bad > Good): p-value = {p_val:.4f}\n")
        
        if p_val < 0.05:
            f.write("RISULTATO: SIGNIFICATIVO. I giocatori giocano PEGGIO (leakano di più) quando sono counterati.\n")
            f.write("           (Conferma l'ipotesi della Pressione/Tilt indotto dal mazzo).\n")
        else:
            f.write("RISULTATO: NON SIGNIFICATIVO. La qualità di gioco (leaks) è indipendente dal matchup.\n")
        f.write("="*100 + "\n")

def analyze_time_stats(players_sessions, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'time_stats_results.txt')

    print(f"\nGenerazione report Time Stats (Matchup, No-Lvl, Levels) in: {output_file}")

    time_slots = {0: "Notte (00-06)", 1: "Mattina (06-12)", 2: "Pomeriggio (12-18)", 3: "Sera (18-24)"}
    
    # Metrics to analyze
    metrics = {
        'matchup': {'label': 'Matchup Reale', 'data': {k: [] for k in time_slots}},
        'matchup_no_lvl': {'label': 'Matchup No-Lvl', 'data': {k: [] for k in time_slots}},
        'level_diff': {'label': 'Level Diff', 'data': {k: [] for k in time_slots}}
    }

    for p in players_sessions:
        nationality = p.get('nationality')
        for session in p['sessions']:
            for b in session['battles']:
                ts = b.get('timestamp')
                if not ts: continue
                
                # Get time slot
                h = get_local_hour(ts, nationality)
                slot = 0
                if 6 <= h < 12: slot = 1
                elif 12 <= h < 18: slot = 2
                elif 18 <= h < 24: slot = 3
                
                # Collect data
                if b.get('matchup') is not None:
                    metrics['matchup']['data'][slot].append(b['matchup'])
                
                if b.get('matchup_no_lvl') is not None:
                    metrics['matchup_no_lvl']['data'][slot].append(b['matchup_no_lvl'])
                    
                if b.get('level_diff') is not None:
                    metrics['level_diff']['data'][slot].append(b['level_diff'])

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI STATISTICA PER FASCIA ORARIA (MATCHUP, NO-LVL, LIVELLI)\n")
        f.write("Obiettivo: Verificare se Media e Varianza cambiano durante il giorno per diverse metriche.\n")
        f.write("="*100 + "\n\n")
        
        for key, info in metrics.items():
            label = info['label']
            samples = info['data']
            
            f.write(f"--- {label} ---\n")
            f.write(f"{'Fascia Oraria':<20} | {'N':<10} | {'Mean':<10} | {'StdDev':<10} | {'Variance':<10}\n")
            f.write("-" * 75 + "\n")
            
            valid_samples = []
            
            for slot in sorted(time_slots.keys()):
                data = samples[slot]
                if not data:
                    f.write(f"{time_slots[slot]:<20} | {'0':<10} | {'-':<10} | {'-':<10} | {'-':<10}\n")
                    continue
                
                avg = statistics.mean(data)
                std = statistics.stdev(data) if len(data) > 1 else 0
                var = std ** 2
                
                f.write(f"{time_slots[slot]:<20} | {len(data):<10} | {avg:<10.2f} | {std:<10.2f} | {var:<10.2f}\n")
                valid_samples.append(data)
            
            f.write("-" * 75 + "\n")
            
            if len(valid_samples) > 1:
                try:
                    stat_k, p_k = kruskal(*valid_samples)
                    f.write(f"Kruskal-Wallis (Medie): p={p_k:.4f}\n")
                    if p_k < 0.05:
                        f.write("-> DIFFERENZA SIGNIFICATIVA nelle medie.\n")
                    else:
                        f.write("-> NESSUNA differenza significativa nelle medie.\n")
                except Exception as e:
                    f.write(f"Kruskal-Wallis Error: {e}\n")

                try:
                    stat_l, p_l = levene(*valid_samples)
                    f.write(f"Levene Test (Varianze): p={p_l:.4f}\n")
                    if p_l < 0.05:
                        f.write("-> DIFFERENZA SIGNIFICATIVA nelle varianze.\n")
                    else:
                        f.write("-> NESSUNA differenza significativa nelle varianze.\n")
                except Exception as e:
                    f.write(f"Levene Test Error: {e}\n")
            else:
                f.write("Dati insufficienti per i test statistici.\n")
            
            f.write("\n" + "="*100 + "\n\n")

def main():
    # Filter options: 'all', 'Ladder', 'Ranked', 'Ladder_Ranked'
    mode_filter = 'all' 
    print(f"Esecuzione test con filtro modalità: {mode_filter}")
    
    players_sessions = get_players_sessions(mode_filter=mode_filter, exclude_unreliable=True)

    analyze_std_correlation(players_sessions)
    analyze_session_pity(players_sessions)
    analyze_extreme_matchup_streak(players_sessions)
    analyze_confounding_factors(players_sessions)
    analyze_deck_switch_impact(players_sessions)
    analyze_return_matchups_vs_ers(players_sessions)
    analyze_pity_impact_on_session_length(players_sessions)
    analyze_pity_impact_on_return_time(players_sessions)
    analyze_churn_probability_vs_pity(players_sessions, {}) # Placeholder per test locale
    analyze_cannon_fodder(players_sessions)
    analyze_dangerous_sequences(players_sessions)
    analyze_markov_chains(players_sessions)
    analyze_return_after_bad_streak(players_sessions)
    analyze_debt_extinction(players_sessions)
    analyze_favorable_outcome_impact(players_sessions)
    analyze_defeat_quality_impact(players_sessions)
    analyze_debt_credit_duration_and_levels(players_sessions)
    analyze_punishment_tradeoff(players_sessions)
    analyze_paywall_impact(players_sessions)
    analyze_meta_ranges(players_sessions)
    analyze_climbing_impact(players_sessions)
    analyze_hook_by_trophy_range(players_sessions)
    analyze_skill_vs_matchup_dominance(players_sessions)
    analyze_time_stats(players_sessions)

if __name__ == "__main__":
    main()