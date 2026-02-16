import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency, chi2

def get_streak_category(streak_count: int, threshold: int = 3) -> str:
    """Categorizza una streak numerica."""
    if streak_count >= threshold:
        return 'Winning Streak'
    elif streak_count <= -threshold:
        return 'Losing Streak'
    else:
        return 'No Streak'

def get_matchup_category(win_rate: float) -> str:
    """Categorizza la difficoltà di un matchup."""
    if win_rate is None:
        return 'Unknown'
    if win_rate > 0.55:
        return 'Favorable'
    elif win_rate < 0.45:
        return 'Unfavorable'
    else:
        return 'Even'

def get_chi2_independence_stats(players_sessions):
    """
    Calcola le statistiche del Chi-Quadro per l'indipendenza tra streak e matchup
    per una lista di giocatori.
    """
    results = {}
    for p in players_sessions:
        tag = p['tag']
        sessions = p['sessions']
        data = _get_player_data(sessions)
        if not data:
            continue
        
        stats = _calculate_chi2(data)
        if stats:
            results[tag] = stats
    return results

def _get_player_data(sessions):
    """Recupera e formatta i dati per il test (logica importata da data_formatter)."""
    formatted_data = []
    
    for session in sessions:
        battles = session['battles']
        current_streak = 0
        
        for battle in battles:
            matchup_val = battle['matchup']
            matchup_win_rate = matchup_val / 100.0 if matchup_val is not None else None
            
            streak_category = get_streak_category(current_streak)
            matchup_category = get_matchup_category(matchup_win_rate)
            
            if matchup_category != 'Unknown':
                formatted_data.append((streak_category, matchup_category))
            
            # Update streak for next battle
            win = battle['win']
            if win == 1:
                current_streak = max(1, current_streak + 1)
            else:
                current_streak = min(-1, current_streak - 1)


    return formatted_data

def _calculate_chi2(data):
    """Esegue il calcolo del Chi-Quadro sui dati formattati (logica importata da test1)."""
    if not data:
        return None

    df = pd.DataFrame(data, columns=['Streak', 'Matchup'])
    
    # Crea tabella di contingenza
    contingency_table = pd.crosstab(df['Streak'], df['Matchup'])

    # Verifica dimensioni minime
    if contingency_table.empty or contingency_table.size == 0:
        return None

    try:
        chi2_stat, p_value, dof, expected = chi2_contingency(contingency_table)
        
        # Valore critico al 95%
        prob = 0.95
        critical_value = chi2.ppf(prob, dof)
        
        expected_df = pd.DataFrame(expected, index=contingency_table.index, columns=contingency_table.columns)

                # --- Analisi Robustezza (Monte Carlo) ---
        low_expected = (expected < 5).any()
        method = "Asymptotic"
        
        # Se ci sono celle con pochi dati o il p-value è interessante (< 0.10), usiamo Monte Carlo
        if low_expected or p_value < 0.10:
            method = "Monte Carlo (10k)"
            n_sims = 10000
            
            # Preparazione dati per numpy (più veloce di pandas nel loop)
            s_vals = df['Streak'].values
            m_vals = df['Matchup'].values
            
            # Mappatura categorie -> interi (ordinati come in crosstab/unique)
            s_cats = np.sort(df['Streak'].unique())
            m_cats = np.sort(df['Matchup'].unique())
            s_map = {cat: i for i, cat in enumerate(s_cats)}
            m_map = {cat: i for i, cat in enumerate(m_cats)}
            
            s_int = np.array([s_map[x] for x in s_vals])
            m_int = np.array([m_map[x] for x in m_vals])
            
            # Calcolo Monte Carlo
            # La matrice Expected è costante sotto permutazione di una colonna
            valid_mask = expected > 0
            E_valid = expected[valid_mask]
            better_count = 0
            
            for _ in range(n_sims):
                np.random.shuffle(m_int)
                O_sim, _, _ = np.histogram2d(s_int, m_int, bins=[len(s_cats), len(m_cats)], range=[[0, len(s_cats)], [0, len(m_cats)]])
                chi2_sim = np.sum((O_sim[valid_mask] - E_valid)**2 / E_valid)
                if chi2_sim >= chi2_stat:
                    better_count += 1
            
            p_value = (better_count + 1) / (n_sims + 1)


        return {
            "chi2_stat": chi2_stat,
            "p_value": p_value,
            "dof": dof,
            "critical_value": critical_value,
            "observed": contingency_table,
            "expected": expected_df,
            "significant": p_value < 0.05,
            "method": method,
            "low_expected": low_expected
        }
    except ValueError:
        return None
