def get_player_profiles(cursor, tags):
    """Recupera i profili comportamentali per una lista di giocatori."""
    query = """
        SELECT battle_id, battle_type, game_mode, timestamp, win, level_diff, matchup_win_rate
        FROM battles
        WHERE player_tag = ?  AND game_mode not like '%Draft%' and battle_type not like 'riverRace%' AND game_mode != '2v2 League'
        ORDER BY timestamp ASC;
    """
    profiles = {}
    for tag in tags:
        cursor.execute(query, (tag,))
        battles = cursor.fetchall()
        profile = get_player_profile(battles)
        if profile:
            profiles[tag] = profile
    return profiles

def get_player_profile(battles):
    """
    Versione avanzata con calcolo FSI e gestione robusta delle sessioni.
    """
    if not battles:
        return None

    # Indici colonne (basati sulla tua query SQL)
    TIMESTAMP_IDX = 3
    WIN_IDX = 4
    MATCHUP_IDX = 6
    
    SESSION_THRESHOLD = 30 * 60 
    total_matches = len(battles)
    
    sessions_data = []
    current_session = [battles[0]]

    l_streak_count = 0
    w_streak_count = 0
    
    # 1. Suddivisione in sessioni
    for i in range(1, total_matches):
        time_diff = battles[i][TIMESTAMP_IDX] - battles[i-1][TIMESTAMP_IDX]
        
        if time_diff > SESSION_THRESHOLD:
            # Analizziamo la sessione appena conclusa
            sessions_data.append(analyze_session_context(current_session))
            current_session = [battles[i]]
        else:
            current_session.append(battles[i])
        
        # Conteggio Streak (su blocchi di 3)
        if i >= 3:
            last_3_results = [battles[i-j][WIN_IDX] for j in range(1, 4)]
            if all(w == 0 for w in last_3_results):
                l_streak_count += 1
            if all(w == 1 for w in last_3_results): 
                w_streak_count += 1
    
    # Aggiungiamo l'ultima sessione
    sessions_data.append(analyze_session_context(current_session))

    # 2. Aggregazione Metriche
    total_fsi = sum(s['session_fsi'] for s in sessions_data)
    avg_fsi = total_fsi / len(sessions_data) if sessions_data else 0
    
    # Calcolo durata media e matches per sessione
    durations = [s['duration_min'] for s in sessions_data if s['duration_min'] > 0]
    avg_dur = sum(durations) / len(durations) if durations else 0
    avg_mps = total_matches / len(sessions_data)

    # Calcolo Matchup Medio (per vedere se il player è "overpowered")
    valid_matchups = [b[MATCHUP_IDX] for b in battles if b[MATCHUP_IDX] is not None]
    avg_matchup = (sum(valid_matchups) / len(valid_matchups) * 100) if valid_matchups else 50

    # 3. Marcatore di Affidabilità (Filtro Rumore Statistico)
    # Identifica se il player ha abbastanza dati e sessioni lunghe per l'EOMM
    is_reliable = total_matches > 100 and avg_mps > 3

    return {
        'total_matches': total_matches,
        'num_sessions': len(sessions_data),
        'avg_fsi': round(avg_fsi, 3),
        'avg_session_min': round(avg_dur, 2),
        'matches_per_session': round(avg_mps, 2),
        'l_streak_count': l_streak_count,
        'w_streak_count': w_streak_count,
        'avg_matchup_pct': round(avg_matchup, 2),
        'is_reliable': is_reliable
    }

def analyze_session_context(session_matches):
    """
    Analizza una singola sessione per estrarre l'indice di frustrazione.
    """
    if not session_matches:
        return {'session_fsi': 0, 'duration_min': 0}

    last_match = session_matches[-1]
    is_loss = last_match[4] == 0
    # Matchup: se None assumiamo 0.5 (neutro)
    matchup = last_match[6] if last_match[6] is not None else 0.5
    
    # Calcolo durata sessione
    duration_min = (session_matches[-1][3] - session_matches[0][3]) / 60
    
    # Calcolo streak negativa finale (quanti match ha perso prima di chiudere)
    neg_streak = 0
    for m in reversed(session_matches):
        if m[4] == 0: 
            neg_streak += 1
        else: 
            break
            
    # LOGICA FSI:
    # Se la sessione finisce con una vittoria, FSI = 0 (Engagement positivo)
    # Se finisce con sconfitta, FSI cresce con la streak e l'ingiustizia del matchup
    fsi = 0
    if is_loss:
        fsi = 1.0 + (neg_streak * 0.5) 
        if matchup < 0.45: # Sotto il 45% lo consideriamo un "hard counter"
            fsi *= 1.4
            
    return {
        'session_fsi': fsi, 
        'duration_min': duration_min,
        'matches_in_session': len(session_matches)
    }