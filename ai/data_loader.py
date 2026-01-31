import sys
import os
import pandas as pd
from datetime import datetime, timedelta, date
import pytz
import statistics

# Add parent directory to path to import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils')))

from connection import open_connection, close_connection

# Constants from battlelog_v2
BATTLE_ID_IDX = 0
GAME_MODE_IDX = 2
TIMESTAMP_IDX = 3
WIN_IDX = 4
LEVEL_DIFF_IDX = 5
MATCHUP_IDX = 6
TROPHY_CHANGE_IDX = 7
ARCHETYPE_IDX = 12
MATCHUP_NO_LVL_IDX = 13
PLAYER_DECK_ID_IDX = 11
ELIXIR_LEAKED_IDX = 14
OPPONENT_DECK_ID_IDX = 15
OPPONENT_ARCHETYPE_IDX = 16
PLAYER_CROWNS_IDX = 9
OPPONENT_CROWNS_IDX = 10
KING_TOWER_IDX = 17

SHORT_STOP = 20 * 60

COUNTRY_TZ_MAP = {
    'Italy': 'Europe/Rome', 'IT': 'Europe/Rome',
    'United States': 'America/New_York', 'US': 'America/New_York',
    'Germany': 'Europe/Berlin', 'DE': 'Europe/Berlin',
    'France': 'Europe/Paris', 'FR': 'Europe/Paris',
    'Spain': 'Europe/Madrid', 'ES': 'Europe/Madrid',
    'United Kingdom': 'Europe/London', 'GB': 'Europe/London', 'UK': 'Europe/London',
    'Russia': 'Europe/Moscow', 'RU': 'Europe/Moscow',
    'Japan': 'Asia/Tokyo', 'JP': 'Asia/Tokyo',
    'China': 'Asia/Shanghai', 'CN': 'Asia/Shanghai',
    'Brazil': 'America/Sao_Paulo', 'BR': 'America/Sao_Paulo',
    'Canada': 'America/Toronto', 'CA': 'America/Toronto',
    'Mexico': 'America/Mexico_City', 'MX': 'America/Mexico_City',
    'Korea, Republic of': 'Asia/Seoul', 'KR': 'Asia/Seoul',
    'Netherlands': 'Europe/Amsterdam', 'NL': 'Europe/Amsterdam'
}

def get_local_hour(ts, nationality):
    """Converte il timestamp UTC nell'ora locale del giocatore."""
    try:
        utc_dt = datetime.fromtimestamp(ts, pytz.utc)
        tz_name = COUNTRY_TZ_MAP.get(nationality, 'Europe/Rome')
        target_tz = pytz.timezone(tz_name)
        player_dt = utc_dt.astimezone(target_tz)
        return player_dt.hour
    except Exception:
        # Fallback su ora locale sistema se fallisce conversione
        return datetime.fromtimestamp(ts).hour

def get_first_monday(year, month):
    d = date(year, month, 1)
    days_ahead = (0 - d.weekday() + 7) % 7
    return d + timedelta(days=days_ahead)

def get_days_since_season_start(ts):
    dt = datetime.fromtimestamp(ts)
    battle_date = dt.date()
    
    start_current = get_first_monday(battle_date.year, battle_date.month)
    
    if battle_date >= start_current:
        season_start = start_current
    else:
        prev_month = 12 if battle_date.month == 1 else battle_date.month - 1
        prev_year = battle_date.year - 1 if battle_date.month == 1 else battle_date.year
        season_start = get_first_monday(prev_year, prev_month)
        
    return (battle_date - season_start).days

def get_arenas(cursor):
    cursor.execute("SELECT trophy_limit FROM arenas ORDER BY trophy_limit ASC")
    return [r[0] for r in cursor.fetchall()]

def get_next_goal(trophies, arenas):
    for limit in arenas:
        if limit > trophies:
            return limit
    return arenas[-1] if arenas else 9000

def define_trophies_history(battles, current_trophies):
    """
    Ricostruisce lo storico dei trofei per le battaglie Ladder.
    Restituisce una mappa {battle_id: trophies_after_battle}.
    """
    ladder_battles = [b for b in battles if b[GAME_MODE_IDX] == 'Ladder']
    if not ladder_battles: return {}
    
    trophies_map = {}
    t_after = current_trophies
    
    # Reverse calculation (from newest to oldest)
    # battles are usually ordered ASC (oldest first) in the query, 
    # so we iterate backwards from the end of the list.
    for i in range(len(ladder_battles) - 1, -1, -1):
        battle = ladder_battles[i]
        b_id = battle[BATTLE_ID_IDX]
        change = battle[TROPHY_CHANGE_IDX] if battle[TROPHY_CHANGE_IDX] is not None else 0
        win = battle[WIN_IDX]
        
        # Fix per dati sporchi (Arena Gate)
        if win == 0 and change > 0: change = 0
        
        trophies_map[b_id] = t_after
        t_after = t_after - change
        
    return trophies_map

def load_data_for_ai():
    """
    Carica i dati dal DB e li formatta per l'addestramento AI.
    Restituisce un DataFrame Pandas.
    """
    db_path = os.path.join(os.path.dirname(__file__), '../db/clash.db')
    connection, cursor, load_tags = open_connection(db_path)
    tags = load_tags()
    arenas = get_arenas(cursor)
    
    dataset = []
    
    for tag in tags:
        # Load player details
        cursor.execute("SELECT trophies, nationality FROM players WHERE player_tag = ?", (tag,))
        p_row = cursor.fetchone()
        if not p_row: continue
        current_trophies, nationality = p_row
        
        # Load battles (Only Ladder for consistency)
        query = """
            SELECT b.battle_id, b.battle_type, b.game_mode, b.timestamp, b.win, b.level_diff, b.matchup_win_rate, b.trophy_change, b.opponent_tag, b.player_crowns, b.opponent_crowns, b.player_deck_id, d.archetype_hash, b.matchup_no_lvl, b.elixir_leaked_player, b.opponent_deck_id, od.archetype_hash,
            (SELECT MAX(card_level) FROM deck_cards WHERE deck_hash = b.player_deck_id AND card_name IN (SELECT card_name FROM cards WHERE type = 'Tower'))
            FROM battles b
            LEFT JOIN decks d ON b.player_deck_id = d.deck_hash
            LEFT JOIN decks od ON b.opponent_deck_id = od.deck_hash
            WHERE b.player_tag = ? AND  b.game_mode = 'Ladder'
            ORDER BY b.timestamp ASC;
        """
        cursor.execute(query, (tag,))
        battles = cursor.fetchall()
        
        if not battles: continue
        
        trophies_map = define_trophies_history(battles, current_trophies)
        
        current_streak = 0
        session_start_ts = battles[0][TIMESTAMP_IDX]
        battles_in_session = 0
        
        running_pb = 0
        trophy_history_100 = []
        opp_archetype_history_10 = []
        matchup_history = []
        win_history = []
        career_matchup_sum = 0.0
        career_matchup_count = 0
        cumulative_matchup_error = 0.0
        player_deck_history = {} # deck_hash -> list of (timestamp, win, elixir_leaked)
        
        for i in range(len(battles) - 1):
            curr = battles[i]
            next_b = battles[i+1]
            
            # Features for Current Battle
            b_id = curr[BATTLE_ID_IDX]
            ts = curr[TIMESTAMP_IDX]
            win = curr[WIN_IDX]
            matchup = curr[MATCHUP_IDX]
            matchup_no_lvl = curr[MATCHUP_NO_LVL_IDX]
            level_diff = curr[LEVEL_DIFF_IDX]
            archetype = curr[ARCHETYPE_IDX]
            elixir_leaked = curr[ELIXIR_LEAKED_IDX]
            opp_archetype = curr[OPPONENT_ARCHETYPE_IDX]
            king_tower = curr[KING_TOWER_IDX]
            
            # Update Deck History with Current Battle
            c_archetype = curr[ARCHETYPE_IDX]
            if c_archetype:
                if c_archetype not in player_deck_history:
                    player_deck_history[c_archetype] = []
                e_leak = elixir_leaked if elixir_leaked is not None else 0.0
                player_deck_history[c_archetype].append((ts, win, e_leak))
            
            # Calculate Stats for NEXT Battle's Deck (Target)
            n_archetype = next_b[ARCHETYPE_IDX]
            n_ts = next_b[TIMESTAMP_IDX]
            
            history = player_deck_history.get(n_archetype, [])
            deck_matches_played = len(history)
            
            cutoff_7d = n_ts - (7 * 24 * 3600)
            recent_wins = [w for t, w, e in history if t >= cutoff_7d]
            deck_win_rate_7d = (sum(recent_wins) / len(recent_wins) * 100) if recent_wins else 50.0
            
            # Avg Elixir Leaked for this deck
            all_leaks = [e for t, w, e in history]
            deck_avg_elixir_leaked = (sum(all_leaks) / len(all_leaks)) if all_leaks else 0.0
            
            # Session Logic
            if i > 0:
                prev_ts = battles[i-1][TIMESTAMP_IDX]
                if (ts - prev_ts) > SHORT_STOP:
                    session_start_ts = ts
                    battles_in_session = 0
            
            battles_in_session += 1
            session_duration = ts - session_start_ts
            
            # Streak Logic (State entering next match)
            if win == 1:
                current_streak = current_streak + 1 if current_streak > 0 else 1
            else:
                current_streak = current_streak - 1 if current_streak < 0 else -1
            
            # Deck Switch Logic
            deck_changed = 0
            if i > 0:
                prev_archetype = battles[i-1][ARCHETYPE_IDX]
                if prev_archetype != archetype:
                    deck_changed = 1
                
            # Time since last match
            time_since_last = 0
            if i > 0:
                time_since_last = ts - battles[i-1][TIMESTAMP_IDX]

            # Trophies (After current match)
            trophies = trophies_map.get(b_id, 0)
            
            # PB & Goal
            if trophies > running_pb:
                running_pb = trophies
            dist_pb = trophies - running_pb
            dist_goal = get_next_goal(trophies, arenas) - trophies
            
            # Rolling Avg Trophies
            avg_trophies_100 = sum(trophy_history_100) / len(trophy_history_100) if trophy_history_100 else trophies
            dist_avg_trophies = trophies - avg_trophies_100
            trophy_history_100.append(trophies)
            if len(trophy_history_100) > 100: trophy_history_100.pop(0)
            
            # Opponent Archetype Frequency
            freq_opp_arch_10 = 0.0
            if opp_archetype:
                freq_opp_arch_10 = opp_archetype_history_10.count(opp_archetype) / len(opp_archetype_history_10) if opp_archetype_history_10 else 0.0
                opp_archetype_history_10.append(opp_archetype)
                if len(opp_archetype_history_10) > 10: opp_archetype_history_10.pop(0)
                
            # Rolling Avg Matchup
            if matchup is not None:
                matchup_val = matchup * 100
                matchup_history.append(matchup_val)
                if len(matchup_history) > 150: matchup_history.pop(0)
                
                career_matchup_sum += matchup_val
                career_matchup_count += 1

            def get_rolling_avg(hist, n):
                if not hist: return 50.0
                subset = hist[-n:]
                return sum(subset) / len(subset)

            avg_matchup_20 = get_rolling_avg(matchup_history, 20)
            avg_matchup_30 = get_rolling_avg(matchup_history, 30)
            avg_matchup_40 = get_rolling_avg(matchup_history, 40)
            avg_matchup_50 = get_rolling_avg(matchup_history, 50)
            avg_matchup_60 = get_rolling_avg(matchup_history, 60)
            avg_matchup_80 = get_rolling_avg(matchup_history, 80)
            avg_matchup_100 = get_rolling_avg(matchup_history, 100)
            avg_matchup_120 = get_rolling_avg(matchup_history, 120)
            avg_matchup_150 = get_rolling_avg(matchup_history, 150)

            # Cumulative Matchup Error (Sum of deviations from avg_150)
            if matchup is not None:
                cumulative_matchup_error += (matchup * 100) - avg_matchup_150

            # Matchup Trend (Drift): Avg(Last 5) - Avg(Prev 20)
            matchup_trend_5 = 0.0
            if len(matchup_history) >= 25:
                avg_last_5 = sum(matchup_history[-5:]) / 5
                avg_prev_20 = sum(matchup_history[-25:-5]) / 20
                matchup_trend_5 = avg_last_5 - avg_prev_20

            # Matchup Volatility (Std Dev Last 10)
            matchup_volatility_10 = 0.0
            if len(matchup_history) >= 10:
                matchup_volatility_10 = statistics.stdev(matchup_history[-10:])

            # Delta Equilibrium (Current - Career Avg)
            equilibrium_matchup = (career_matchup_sum / career_matchup_count) if career_matchup_count > 0 else 50.0
            delta_equilibrium = ((matchup * 100) - equilibrium_matchup) if matchup is not None else 0.0

            # Streak Violation (Interaction Feature)
            streak_violation = current_streak * delta_equilibrium

            # Matchup Quality Decay
            matchup_quality_decay = ((matchup * 100) / (battles_in_session + 1)) if matchup is not None else 0.0

            # Rolling Global Win Rate (Last 100)
            win_history.append(win)
            if len(win_history) > 100: win_history.pop(0)
            global_win_rate = (sum(win_history) / len(win_history) * 100) if win_history else 50.0

            # Crowns
            crown_diff = (curr[PLAYER_CROWNS_IDX] - curr[OPPONENT_CROWNS_IDX]) if curr[PLAYER_CROWNS_IDX] is not None and curr[OPPONENT_CROWNS_IDX] is not None else 0
            
            # Target for Next Battle
            target_win = next_b[WIN_IDX]
            target_matchup = next_b[MATCHUP_IDX]
            
            # Filter invalid data
            if matchup is None or target_matchup is None:
                continue
                
            # Time Calculation
            local_h = get_local_hour(ts, nationality)
            days_since_season = get_days_since_season_start(ts)

            # Lagged Matchups (1 to 30)
            lags = {}
            for k in range(1, 31):
                idx = -(k + 1)
                lags[f'prev_matchup_{k}'] = matchup_history[idx] if len(matchup_history) >= (k + 1) else 50.0
                lags[f'prev_win_{k}'] = win_history[idx] if len(win_history) >= (k + 1) else 0.5

            row = {
                'player_tag': tag,
                'nationality': nationality,
                'timestamp': ts,
                'hour': local_h,
                'days_since_season': days_since_season,
                'trophies': trophies,
                'current_win': win,
                'current_matchup': matchup * 100,
                'current_matchup_no_lvl': (matchup_no_lvl * 100) if matchup_no_lvl else 50.0,
                'current_level_diff': level_diff if level_diff else 0.0,
                'streak': current_streak,
                'session_duration': session_duration,
                'battles_in_session': battles_in_session,
                'deck_changed': deck_changed,
                'elixir_leaked': elixir_leaked if elixir_leaked is not None else 0.0,
                'archetype': archetype,
                'dist_goal': dist_goal,
                'dist_pb': dist_pb,
                'dist_avg_trophies': dist_avg_trophies,
                'freq_opp_arch_10': freq_opp_arch_10,
                'time_since_last': time_since_last,
                'crown_diff': crown_diff,
                'king_tower_level': king_tower if king_tower else 0,
                'avg_matchup_20': avg_matchup_20,
                'avg_matchup_30': avg_matchup_30,
                'avg_matchup_40': avg_matchup_40,
                'avg_matchup_50': avg_matchup_50,
                'avg_matchup_60': avg_matchup_60,
                'avg_matchup_80': avg_matchup_80,
                'avg_matchup_100': avg_matchup_100,
                'avg_matchup_120': avg_matchup_120,
                'avg_matchup_150': avg_matchup_150,
                'deck_matches_played': deck_matches_played,
                'deck_win_rate_7d': deck_win_rate_7d,
                'deck_avg_elixir_leaked': deck_avg_elixir_leaked,
                'global_win_rate': global_win_rate,
                'matchup_trend_5': matchup_trend_5,
                'matchup_volatility_10': matchup_volatility_10,
                'delta_equilibrium': delta_equilibrium,
                'streak_violation': streak_violation,
                'matchup_quality_decay': matchup_quality_decay,
                'cumulative_matchup_error': cumulative_matchup_error,
                # Targets
                'target_win': target_win,
                'target_matchup': target_matchup * 100
            }
            row.update(lags)
            dataset.append(row)
            
    close_connection(connection)
    return pd.DataFrame(dataset)

if __name__ == "__main__":
    df = load_data_for_ai()
    print(f"Dataset loaded: {len(df)} rows")
    if not df.empty:
        print(df.head())