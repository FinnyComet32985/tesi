import scipy.stats as stats

def get_extreme_matchup_stats(players_sessions):
    """Calcola le statistiche di Fisher per i matchup estremi per ogni giocatore."""
    results = {}
    for p in players_sessions:
        tag = p['tag']
        sessions = p['sessions']
        m_pity, m_punish = get_fisher_matrices(sessions)
        results[tag] = {
            "pity": calculate_fisher_stats(m_pity),
            "punish": calculate_fisher_stats(m_punish)
        }
    return results

def get_fisher_matrices(sessions):
    """Analizza il dataset e restituisce le matrici 2x2 per i test di Fisher."""
    
    # Matrici: [[A, B], [C, D]]
    matrix_pity = [[0, 0], [0, 0]]
    matrix_punish = [[0, 0], [0, 0]]

    for session in sessions:
        battles = session['battles']
        # Need at least 4 battles to have a streak of 3 before the current one
        if len(battles) < 4:
            continue
            
        for i in range(3, len(battles)):
            matchup = battles[i]['matchup']
            if matchup is None: 
                continue
            
            # matchup is already 0-100 in battlelog_v2
            matchup_val = matchup 
            
            # Check previous 3 results
            last_3_results = [battles[i-j]['win'] for j in range(1, 4)]
            
            is_losing_streak = all(w == 0 for w in last_3_results)
            is_winning_streak = all(w == 1 for w in last_3_results)

            # Riempimento Pity Match
            if is_losing_streak:
                if matchup_val > 60: 
                    matrix_pity[0][0] += 1
                else: 
                    matrix_pity[0][1] += 1
            else:
                if matchup_val > 60: 
                    matrix_pity[1][0] += 1
                else: 
                    matrix_pity[1][1] += 1

            # Riempimento Punitivi
            if is_winning_streak:
                if matchup_val < 40: 
                    matrix_punish[0][0] += 1
                else: 
                    matrix_punish[0][1] += 1
            else:
                if matchup_val < 40: 
                    matrix_punish[1][0] += 1
                else: 
                    matrix_punish[1][1] += 1

    return matrix_pity, matrix_punish

def calculate_fisher_stats(matrix):
    """Esegue il test di Fisher e restituisce i risultati grezzi."""
    # Calcolo statistico
    odds_ratio, p_value = stats.fisher_exact(matrix, alternative='greater')
    return {
        "matrix": matrix,
        "odds_ratio": odds_ratio,
        "p_value": p_value
    }
