import os
from datetime import datetime
import scipy.stats as stats

def test_extreme_matchup(cursor, tags):

    query = """
        SELECT battle_id, battle_type, game_mode, timestamp, win, level_diff, matchup_win_rate
        FROM battles
        WHERE player_tag = ? -- AND game_mode not like '%Draft%' and battle_type not like 'riverRace%'
        ORDER BY timestamp ASC;
    """

    # Preparazione cartella e file di output
    results_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(results_dir, exist_ok=True)
    output_path = os.path.join(results_dir, 'fisher_extreme_matchup_results.txt')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"Analisi eseguita il: {datetime.now()}\n")

        for tag in tags:
            cursor.execute(query, (tag,))
            battles = cursor.fetchall()

            # Intestazione per separare i player nel log
            f.write(f"\n{'#'*40}\n# PLAYER: {tag}\n{'#'*40}\n")
            print(f"\n{'#'*40}\n# PLAYER: {tag}\n{'#'*40}")

            m_pity, m_punish = get_fisher_matrices(battles)
            run_fisher_analysis(m_pity, "PITY MATCH", "Dopo Losing Streak (>=3L)", "Matchup > 80%", file=f)
            run_fisher_analysis(m_punish, "MATCHUP PUNITIVI", "Dopo Win Streak (>=3W)", "Matchup < 40%", file=f)

    print(f"\nI risultati sono stati salvati in: {output_path}")

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
        last_3_wins = [battles[i-j][WIN_IDX] for j in range(1, 4)]
        
        is_losing_streak = all(w == 0 for w in last_3_wins)
        is_winning_streak = all(w == 1 for w in last_3_wins)

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

def run_fisher_analysis(matrix, label, condition_name, effect_name, file=None):
    """Esegue il test e stampa la tabella formattata come richiesto."""
    
    def log(msg):
        print(msg)
        if file:
            file.write(msg + "\n")

    # Calcolo statistico
    odds_ratio, p_value = stats.fisher_exact(matrix, alternative='greater')
    
    # Estrazione celle per chiarezza
    a, b = matrix[0]
    c, d = matrix[1]

    log("\n" + "="*60)
    log(f" ANALISI STATISTICA: {label}")
    log("="*60)
    log(f"{'CONDIZIONE':<25} | {effect_name:<15} | {'Altro/Normale':<15}")
    log("-" * 60)
    log(f"{condition_name:<25} | {a:<15} | {b:<15}")
    log(f"{'Situazione Normale':<25} | {c:<15} | {d:<15}")
    log("-" * 60)
    
    # Risultati del test
    log(f"Rapporto di probabilità (Odds Ratio): {odds_ratio:.2f}")
    log(f"Significatività (p-value): {p_value:.6f}")
    
    if p_value < 0.05:
        status = "CONFERMATA (EOMM Probabile)"
    else:
        status = "NON CONFERMATA (Casualità)"
    
    log(f"IPOTESI: {status}")
    log("="*60)
