def get_streak_category(streak_count: int, threshold: int = 2) -> str:
    """
    Categorizza una streak numerica in una stringa.

    Args:
        streak_count: Numero di vittorie (positivo) o sconfitte (negativo) consecutive.
        threshold: Soglia per considerare una serie una "streak".

    Returns:
        Categoria della streak ('Winning Streak', 'Losing Streak', 'No Streak').
    """
    if streak_count >= threshold:
        return 'Winning Streak'
    elif streak_count <= -threshold:
        return 'Losing Streak'
    else:
        return 'No Streak'

def get_matchup_category(win_rate: float) -> str:
    """
    Categorizza la difficoltà di un matchup basandosi sulla win rate.

    Args:
        win_rate: La probabilità di vittoria del matchup (0.0 a 1.0).

    Returns:
        Categoria del matchup ('Favorable', 'Even', 'Unfavorable').
    """
    if win_rate is None:
        return 'Unknown'
    if win_rate > 0.55:
        return 'Favorable'
    elif win_rate < 0.45:
        return 'Unfavorable'
    else:
        return 'Even'

def data_provider(cursor, player_tag: str):
    """
    Prepara i dati per il test del chi-quadro sull'EOMM.

    Recupera le battaglie di un giocatore, calcola la streak prima di ogni match
    e categorizza sia la streak che la difficoltà del matchup.

    Args:
        cursor: Cursore del database per eseguire le query.
        player_tag: Il tag del giocatore da analizzare.

    Returns:
        Una lista di tuple, dove ogni tupla è (categoria_streak, categoria_matchup).
        Es: [('Winning Streak', 'Unfavorable'), ('No Streak', 'Even'), ...]
    """
    query = """
    SELECT timestamp, win, matchup_win_rate
    FROM battles
    WHERE player_tag = ? /* AND battle_type = 'pathOfLegend' */ AND game_mode='Ladder' -- Filtra per un tipo di battaglia consistente
    ORDER BY timestamp ASC;
    """
    cursor.execute(query, (player_tag,))
    battles = cursor.fetchall()

    if not battles:
        print(f"Nessuna battaglia trovata per il giocatore {player_tag}")
        return []

    # Calcoliamo la streak *prima* di ogni battaglia
    streaks_before_match = [0] # La prima battaglia non ha una streak precedente
    current_streak = 0
    for i in range(len(battles) - 1):
        win = battles[i][1] # risultato della battaglia i
        if win == 1:
            current_streak = max(1, current_streak + 1)
        else: # win == 0
            current_streak = min(-1, current_streak - 1)
        streaks_before_match.append(current_streak)

    # Combiniamo i dati in un formato categorico
    formatted_data = []
    for i, battle in enumerate(battles):
        matchup_win_rate = battle[2]
        streak_category = get_streak_category(streaks_before_match[i])
        matchup_category = get_matchup_category(matchup_win_rate)
        
        # Ignoriamo i dati incompleti per non falsare il test
        if matchup_category != 'Unknown':
            formatted_data.append((streak_category, matchup_category))

    return formatted_data