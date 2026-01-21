from datetime import datetime
import math
import random
import statistics 
import os
import numpy as np
from scipy.stats import spearmanr, fisher_exact, chi2_contingency, kruskal, levene, mannwhitneyu, ttest_1samp

# Import data loader from battlelog_v2
from battlelog_v2 import get_players_sessions


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


def analyze_extreme_matchup_streak(players_sessions, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'extreme_matchup_streak_results.txt')

    print(f"\nGenerazione report streak matchup estremi in: {output_file}")

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
            mus = [b['matchup'] for b in session['battles'] if b['matchup'] is not None and (b['game_mode'] == 'Ladder' or b['game_mode'] == 'Ranked')]
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


def analyze_confounding_factors(players_sessions, output_dir=None):
    if output_dir is None:
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


def analyze_time_matchup_stats(players_sessions, output_dir=None):
    if output_dir is None:
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

    # Soglia Churn: 7 giorni (in secondi)
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
        f.write(f"Definizione Churn: Assenza > 7 giorni rispetto all'ultimo dato globale ({datetime.fromtimestamp(max_ts)}).\n")
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

def analyze_matchup_markov_chain(players_sessions, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'matchup_markov_chain_results.txt')

    print(f"\nGenerazione report Catene di Markov (Transizioni Matchup) in: {output_file}")

    # Definizioni Stati
    # 0: Unfavorable (<45%), 1: Even (45-55%), 2: Favorable (>55%)
    states = ['Unfavorable', 'Even', 'Favorable']
    
    # Matrice di Transizione (Conteggi): transitions[FROM][TO]
    transitions = [[0]*3 for _ in range(3)]
    
    total_transitions = 0

    for p in players_sessions:
        for session in p['sessions']:
            battles = session['battles']
            if len(battles) < 2: 
                continue
            
            # Convertiamo la sessione in una sequenza di stati
            session_states = []
            for b in battles:
                m = b['matchup']
                if m is None:
                    session_states.append(None)
                    continue
                
                if m > 55.0: s = 2   # Favorable
                elif m < 45.0: s = 0 # Unfavorable
                else: s = 1          # Even
                session_states.append(s)
            
            # Contiamo le transizioni i -> i+1
            for i in range(len(session_states) - 1):
                curr_s = session_states[i]
                next_s = session_states[i+1]
                
                if curr_s is not None and next_s is not None:
                    transitions[curr_s][next_s] += 1
                    total_transitions += 1

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI CATENE DI MARKOV: TRANSIZIONI MATCHUP\n")
        f.write("Obiettivo: Verificare se il matchup attuale influenza il prossimo (es. 'Bad' chiama 'Bad').\n")
        f.write("Ipotesi Nera (Random): La probabilità del prossimo stato dipende solo dalla frequenza globale, non dallo stato precedente.\n")
        f.write("="*80 + "\n\n")
        
        f.write(f"Totale Transizioni Analizzate: {total_transitions}\n")
        f.write("-" * 80 + "\n")

        # Calcolo Totali per Riga (From) e Colonna (To)
        row_totals = [sum(transitions[i]) for i in range(3)]
        col_totals = [sum(transitions[i][j] for i in range(3)) for j in range(3)]
        grand_total = sum(row_totals)

        if grand_total == 0:
            f.write("Dati insufficienti.\n")
            return

        # Probabilità Globali (Attese se il sistema fosse senza memoria)
        global_probs = [c / grand_total for c in col_totals]

        f.write(f"{'STATO PRECEDENTE':<20} | {'SUCCESSIVO: Unfavorable':<25} | {'SUCCESSIVO: Even':<20} | {'SUCCESSIVO: Favorable':<20}\n")
        f.write("-" * 95 + "\n")

        for i, from_state in enumerate(states):
            row_str = f"{from_state:<20} | "
            for j, to_state in enumerate(states):
                count = transitions[i][j]
                total_from = row_totals[i] if row_totals[i] > 0 else 1
                
                obs_prob = count / total_from
                exp_prob = global_probs[j] # Se indipendente, dovrebbe essere uguale alla media globale
                
                diff = obs_prob - exp_prob
                marker = ""
                if abs(diff) > 0.05: marker = "(!)" # Evidenzia scostamenti > 5%
                
                cell_str = f"{obs_prob*100:.1f}% (Exp {exp_prob*100:.1f}%) {marker}"
                row_str += f"{cell_str:<25} | "
            f.write(row_str + "\n")

        f.write("-" * 95 + "\n")
        
        # Test Chi-Quadro sulla matrice di transizione
        chi2, p, dof, ex = chi2_contingency(transitions)
        f.write(f"Test Chi-Quadro (Indipendenza Transizioni):\n")
        f.write(f"P-value: {p:.6f}\n")
        
        if p < 0.05:
            f.write("RISULTATO: DIPENDENZA SIGNIFICATIVA. Il sistema ha 'memoria' (il matchup precedente influenza il successivo).\n")
        else:
            f.write("RISULTATO: INDIPENDENZA. Le transizioni sembrano casuali rispetto alla distribuzione globale.\n")
        
        f.write("="*80 + "\n")

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

def main():
    # Filter options: 'all', 'Ladder', 'Ranked', 'Ladder_Ranked'
    mode_filter = 'all' 
    print(f"Esecuzione test con filtro modalità: {mode_filter}")
    
    players_sessions = get_players_sessions(mode_filter=mode_filter, exclude_unreliable=True)

    analyze_std_correlation(players_sessions)
    analyze_session_pity(players_sessions)
    analyze_extreme_matchup_streak(players_sessions)
    analyze_confounding_factors(players_sessions)
    analyze_time_matchup_stats(players_sessions)
    analyze_deck_switch_impact(players_sessions)
    analyze_return_matchups_vs_ers(players_sessions)
    analyze_pity_impact_on_session_length(players_sessions)
    analyze_pity_impact_on_return_time(players_sessions)
    analyze_churn_probability_vs_pity(players_sessions, {}) # Placeholder per test locale
    analyze_cannon_fodder(players_sessions)
    analyze_dangerous_sequences(players_sessions)
    analyze_matchup_markov_chain(players_sessions)
    analyze_return_after_bad_streak(players_sessions)
    analyze_debt_extinction(players_sessions)

if __name__ == "__main__":
    main()