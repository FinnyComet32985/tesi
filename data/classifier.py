import os
from datetime import datetime

def classifier(cursor, tags):
    query = """
        SELECT battle_id, battle_type, game_mode, timestamp, win, level_diff, matchup_win_rate
        FROM battles
        WHERE player_tag = ? -- AND game_mode not like '%Draft%' and battle_type not like 'riverRace%'
        ORDER BY timestamp ASC;
    """

    # Preparazione cartella e file di output
    results_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(results_dir, exist_ok=True)
    output_path = os.path.join(results_dir, 'classifier_results.txt')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"Analisi Classificatore eseguita il: {datetime.now()}\n")

        for tag in tags:
            cursor.execute(query, (tag,))
            battles = cursor.fetchall()
            profile = get_player_profile(battles)
            
            if profile:
                print_profile(profile, tag, f)

    print(f"\nI risultati sono stati salvati in: {output_path}")


def get_player_profile(battles):
    """
    Calcola il profilo comportamentale completo del giocatore, 
    inclusa la durata delle sessioni e i pattern di abbandono.
    """
    WIN_IDX = 4
    TIMESTAMP_IDX = 3
    MATCHUP_IDX = 6
    
    # Soglia per definire la fine di una sessione (es. 30 minuti di inattività)
    SESSION_THRESHOLD = 30 * 60 
    
    total_matches = len(battles)
    if total_matches == 0: 
        return None

    l_streak_count = 0
    w_streak_count = 0
    quits_after_L = 0
    total_L = 0
    
    # Variabili per le sessioni
    sessions = []
    current_session_matches = [battles[0]]
    
    for i in range(1, total_matches):
        time_diff = battles[i][TIMESTAMP_IDX] - battles[i-1][TIMESTAMP_IDX]
        
        # Gestione Sessioni
        if time_diff > SESSION_THRESHOLD:
            # La sessione precedente è finita
            sessions.append(current_session_matches)
            current_session_matches = [battles[i]]
        else:
            current_session_matches.append(battles[i])
            
        # Conteggio Ragequit (Smette di giocare dopo una L per più della soglia)
        if battles[i-1][WIN_IDX] == 0:
            total_L += 1
            if time_diff > SESSION_THRESHOLD:
                quits_after_L += 1
        
        # Conteggio Streak (su blocchi di 3)
        if i >= 3:
            last_3_wins = [battles[i-j][WIN_IDX] for j in range(1, 4)]
            if all(w == 0 for w in last_3_wins):
                l_streak_count += 1
            if all(w == 1 for w in last_3_wins): 
                w_streak_count += 1

    # Aggiungi l'ultima sessione rimasta aperta
    if current_session_matches:
        sessions.append(current_session_matches)

    # Calcolo metriche medie
    durations = []
    for s in sessions:
        if len(s) > 1:
            dur = s[-1][TIMESTAMP_IDX] - s[0][TIMESTAMP_IDX]
            durations.append(dur / 60) # Convertito in minuti
    
    avg_session_min = sum(durations) / len(durations) if durations else 0
    matches_per_session = total_matches / len(sessions)
    ragequit_rate = (quits_after_L / total_L * 100) if total_L > 0 else 0
    
    # Calcolo Matchup Medio (per vedere se il player è "overpowered")
    valid_matchups = [b[MATCHUP_IDX] for b in battles if b[MATCHUP_IDX] is not None]
    avg_matchup = (sum(valid_matchups) / len(valid_matchups) * 100) if valid_matchups else 50

    return {
        'total_matches': total_matches,
        'num_sessions': len(sessions),
        'avg_session_min': round(avg_session_min, 2),
        'matches_per_session': round(matches_per_session, 2),
        'l_streak_count': l_streak_count,
        'w_streak_count': w_streak_count,
        'ragequit_rate': round(ragequit_rate, 2),
        'avg_matchup_pct': round(avg_matchup, 2)
    }

def print_profile(profile, tag, file):
    """Stampa il profilo del giocatore in formato tabellare su console e file."""
    def log(msg):
        print(msg)
        file.write(msg + "\n")

    labels = {
        'total_matches': 'Totale Partite',
        'num_sessions': 'Numero Sessioni',
        'avg_session_min': 'Durata Media Sess. (min)',
        'matches_per_session': 'Partite per Sessione',
        'l_streak_count': 'Losing Streaks (>=3L)',
        'w_streak_count': 'Winning Streaks (>=3W)',
        'ragequit_rate': 'Ragequit Rate (%)',
        'avg_matchup_pct': 'Matchup Medio (%)'
    }

    log("\n" + "="*45)
    log(f" PLAYER: {tag}")
    log("="*45)
    log(f"{'METRICA':<30} | {'VALORE':<10}")
    log("-" * 45)
    
    for key, label in labels.items():
        val = profile.get(key, "N/A")
        log(f"{label:<30} | {str(val):<10}")
    
    log("-" * 45)