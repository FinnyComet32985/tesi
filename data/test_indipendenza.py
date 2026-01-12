import pandas as pd
from scipy.stats import chi2_contingency, chi2

def get_streak_category(streak_count: int, threshold: int = 2) -> str:
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

        return {
            "chi2_stat": chi2_stat,
            "p_value": p_value,
            "dof": dof,
            "critical_value": critical_value,
            "observed": contingency_table,
            "expected": expected_df,
            "significant": chi2_stat >= critical_value
        }
    except ValueError:
        return None
