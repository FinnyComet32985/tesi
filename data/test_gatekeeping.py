import scipy.stats as stats
import pandas as pd

def get_gatekeeping_stats(cursor, tags, danger_range=150):
    """
    Analizza se i giocatori affrontano matchup più difficili quando sono vicini
    a salire di arena (Gatekeeping).
    """
    # 1. Carica le soglie delle arene
    cursor.execute("SELECT trophy_limit FROM arenas ORDER BY trophy_limit ASC")
    arena_thresholds = [row[0] for row in cursor.fetchall()]
    
    results = {}

    for tag in tags:
        # 2. Recupera dati giocatore e battaglie
        cursor.execute("SELECT trophies FROM players WHERE player_tag = ?", (tag,))
        row = cursor.fetchone()
        if not row: 
            continue
        current_trophies = row[0]

        # Recuperiamo le battaglie dalla più recente alla più vecchia per ricostruire i trofei
        query = """
            SELECT win, trophy_change, matchup_win_rate
            FROM battles
            WHERE player_tag = ? 
              AND trophy_change IS NOT NULL 
              AND matchup_win_rate IS NOT NULL
              AND game_mode = 'Ladder'
            ORDER BY timestamp DESC
        """
        cursor.execute(query, (tag,))
        battles = cursor.fetchall()

        if not battles:
            continue

        # 3. Costruzione Matrice di Contingenza
        # [Danger Zone, Safe Zone] x [Hard Counter, Normal Match]
        # Matrix: [[a, b], [c, d]]
        # a: Danger & Hard | b: Danger & Normal
        # c: Safe & Hard   | d: Safe & Normal
        matrix = [[0, 0], [0, 0]]
        
        # Simulazione trofei a ritroso
        simulated_trophies = current_trophies

        for win, trophy_change, matchup_win_rate in battles:
            # Fix per Arena Gate: se sconfitta (win=0) ma variazione positiva,
            # significa che siamo al limite dell'arena (perdita 0) e il parser
            # ha letto erroneamente i trofei vinti dall'avversario.
            if win == 0 and trophy_change > 0:
                trophy_change = 0

            # Calcoliamo i trofei che il player aveva PRIMA di questa partita
            # Se la battaglia è finita, i trofei attuali sono post-change.
            # Quindi pre-match = post-match - change
            trophies_before_match = simulated_trophies - trophy_change
            
            # Aggiorniamo il simulatore per la prossima iterazione (che è la partita precedente)
            simulated_trophies = trophies_before_match

            # Identifica la prossima arena target
            next_arena_limit = None
            for limit in arena_thresholds:
                if limit > trophies_before_match:
                    next_arena_limit = limit
                    break
            
            if not next_arena_limit:
                continue # Player sopra l'ultima arena registrata

            distance = next_arena_limit - trophies_before_match
            
            # Definizione Zone
            is_danger_zone = 0 < distance <= danger_range
            
            # Definizione Hard Counter (es. win rate < 45%)
            is_hard_counter = matchup_win_rate < 0.45

            if is_danger_zone:
                if is_hard_counter:
                    matrix[0][0] += 1 # a
                else:
                    matrix[0][1] += 1 # b
            else:
                if is_hard_counter:
                    matrix[1][0] += 1 # c
                else:
                    matrix[1][1] += 1 # d

        # 4. Calcolo Fisher Exact Test
        if sum(matrix[0]) > 0 and sum(matrix[1]) > 0:
            odds_ratio, p_value = stats.fisher_exact(matrix, alternative='greater')
            
            results[tag] = {
                "matrix": matrix,
                "odds_ratio": odds_ratio,
                "p_value": p_value,
                "total_danger_matches": sum(matrix[0]),
                "total_safe_matches": sum(matrix[1])
            }

    return results

def format_gatekeeping_matrix(matrix):
    """Formatta la matrice per la stampa."""
    a, b = matrix[0]
    c, d = matrix[1]
    
    df = pd.DataFrame(
        [[a, b], [c, d]],
        columns=["Hard Counter (<45%)", "Normal Match (>=45%)"],
        index=["Danger Zone (Close to Arena)", "Safe Zone"]
    )
    return df

def get_gatekeeping_summary(results):
    """Calcola quanti giocatori mostrano segni di gatekeeping."""
    significant = 0
    total = 0
    for res in results.values():
        total += 1
        if res['p_value'] < 0.05 and res['odds_ratio'] > 1:
            significant += 1
    return significant, total