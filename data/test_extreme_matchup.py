import scipy.stats as stats

def get_extreme_matchup_stats(cursor, tags):
    """Calcola le statistiche di Fisher per i matchup estremi per ogni giocatore."""
    query = """
        SELECT battle_id, battle_type, game_mode, timestamp, win, level_diff, matchup_win_rate
        FROM battles
        WHERE player_tag = ? -- AND game_mode not like '%Draft%' and battle_type not like 'riverRace%'
        ORDER BY timestamp ASC;
    """
    results = {}
    for tag in tags:
        cursor.execute(query, (tag,))
        battles = cursor.fetchall()
        m_pity, m_punish = get_fisher_matrices(battles)
        results[tag] = {
            "pity": calculate_fisher_stats(m_pity),
            "punish": calculate_fisher_stats(m_punish)
        }
    return results

def get_fisher_matrices(battles):
    """Analizza il dataset e restituisce le matrici 2x2 per i test di Fisher."""
    WIN_IDX = 4
    MATCHUP_IDX = 6
    
    # Matrici: [[A, B], [C, D]]
    matrix_pity = [[0, 0], [0, 0]]
    matrix_punish = [[0, 0], [0, 0]]

    for i in range(3, len(battles)):
        matchup = battles[i][MATCHUP_IDX]
        if matchup is None: 
            continue
        
        matchup_val = matchup * 100
        last_3_results = [battles[i-j][WIN_IDX] for j in range(1, 4)]
        
        is_losing_streak = all(w == 0 for w in last_3_results)
        is_winning_streak = all(w == 1 for w in last_3_results)

        # Riempimento Pity Match
        if is_losing_streak:
            if matchup_val > 80: 
                matrix_pity[0][0] += 1
            else: 
                matrix_pity[0][1] += 1
        else:
            if matchup_val > 80: 
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
