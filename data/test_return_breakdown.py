import os
import statistics
from collections import defaultdict
from scipy.stats import mannwhitneyu, spearmanr
from datetime import datetime
import sys

# Add parent dir to path if needed
sys.path.append(os.path.dirname(__file__))

try:
    from test_time_analysis import get_local_hour
except ImportError:
    def get_local_hour(ts, nat):
        return datetime.strptime(ts, '%Y-%m-%d %H:%M:%S').hour

def analyze_return_breakdown(players_sessions, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'return_breakdown_results.txt')

    print(f"\nGenerazione report Return Breakdown (Cause Bad Streak) in: {output_file}")

    # Constants
    BAD_THRESH = 45.0
    STREAK_LEN = 3
    WINDOW_SIZE = 20 # For moving average trophies

    # Data Collection
    # List of dicts: { 'return_mu': float, 'trophy_excess': float, 'level_diff': float, 'mu_nolvl': float, 'time_improvement': float }
    bad_streak_returns = []
    
    # Pre-calculate Time Profiles per Player (Avg MU No-Lvl per Hour)
    player_time_profiles = {}
    
    for p in players_sessions:
        tag = p['tag']
        nat = p.get('nationality')
        hourly_mus = defaultdict(list)
        
        for s in p['sessions']:
            for b in s['battles']:
                if b.get('matchup_no_lvl') is not None and b.get('timestamp'):
                    h = get_local_hour(b['timestamp'], nat)
                    hourly_mus[h].append(b['matchup_no_lvl'])
        
        # Compute averages
        profile = {}
        for h, mus in hourly_mus.items():
            if len(mus) >= 3: # Min sample
                profile[h] = statistics.mean(mus)
        player_time_profiles[tag] = profile

    # Main Loop
    for p in players_sessions:
        tag = p['tag']
        nat = p.get('nationality')
        sessions = p['sessions']
        
        # Flatten battles for trophy moving average
        all_battles = []
        for s in sessions:
            all_battles.extend(s['battles'])
            
        # Map battle index to trophies for quick lookup
        trophy_history = []
        for b in all_battles:
            t = b.get('trophies_before')
            trophy_history.append(t) # Can be None

        # Iterate sessions to find returns
        global_idx = 0
        for i in range(len(sessions) - 1):
            curr_sess = sessions[i]
            next_sess = sessions[i+1]
            
            sess_len = len(curr_sess['battles'])
            
            # Check Bad Streak in current session
            if sess_len >= STREAK_LEN:
                last_n = curr_sess['battles'][-STREAK_LEN:]
                if all(b['matchup'] is not None and b['matchup'] < BAD_THRESH for b in last_n):
                    # Found Bad Streak
                    
                    # Check Return Match (First of next session)
                    if not next_sess['battles']:
                        global_idx += sess_len
                        continue
                        
                    ret_b = next_sess['battles'][0]
                    if ret_b['matchup'] is None:
                        global_idx += sess_len
                        continue
                        
                    # 1. Trophy Excess
                    # Calculate avg of [global_idx + sess_len - WINDOW : global_idx + sess_len]
                    end_idx = global_idx + sess_len
                    start_idx = max(0, end_idx - WINDOW_SIZE)
                    
                    recent_trophies = [t for t in trophy_history[start_idx:end_idx] if t is not None]
                    
                    trophy_excess = None
                    if recent_trophies and ret_b.get('trophies_before'):
                        avg_t = statistics.mean(recent_trophies)
                        trophy_excess = ret_b['trophies_before'] - avg_t
                        
                    # 2. Time Improvement
                    time_improvement = None
                    if player_time_profiles.get(tag):
                        last_b = curr_sess['battles'][-1]
                        h_quit = get_local_hour(last_b['timestamp'], nat)
                        h_ret = get_local_hour(ret_b['timestamp'], nat)
                        
                        prof = player_time_profiles[tag]
                        if h_quit in prof and h_ret in prof:
                            time_improvement = prof[h_ret] - prof[h_quit]

                    bad_streak_returns.append({
                        'return_mu': ret_b['matchup'],
                        'trophy_excess': trophy_excess,
                        'level_diff': ret_b.get('level_diff'),
                        'mu_nolvl': ret_b.get('matchup_no_lvl'),
                        'time_improvement': time_improvement
                    })

            global_idx += sess_len

    # Analysis and Writing
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI CAUSE PERSISTENZA BAD STREAK AL RITORNO\n")
        f.write("Domanda: Perché la streak negativa continua anche dopo una pausa?\n")
        f.write(f"Campione: {len(bad_streak_returns)} ritorni dopo Bad Streak (>=3 match < 45%).\n")
        f.write("="*80 + "\n\n")
        
        if len(bad_streak_returns) < 10:
            f.write("Dati insufficienti.\n")
            return

        # 1. TROPHY INFLATION
        valid_trophy = [x for x in bad_streak_returns if x['trophy_excess'] is not None]
        f.write("1. IPOTESI TROPHY INFLATION ('Sei troppo in alto')\n")
        if valid_trophy:
            avg_excess = statistics.mean([x['trophy_excess'] for x in valid_trophy])
            corr, p = spearmanr([x['trophy_excess'] for x in valid_trophy], [x['return_mu'] for x in valid_trophy])
            
            f.write(f"   Excess Trofei Medio al Ritorno: {avg_excess:+.2f}\n")
            f.write(f"   Correlazione (Excess vs Return MU): {corr:.4f} (p={p:.4f})\n")
            
            if p < 0.05 and corr < 0:
                f.write("   -> CONFERMATO: Più sei sopra la tua media, peggiore è il matchup al ritorno.\n")
            else:
                f.write("   -> NON CONFERMATO: L'eccesso di trofei non spiega il matchup negativo.\n")
        f.write("\n")

        # 2. LEVELS vs NO-LVL
        valid_comp = [x for x in bad_streak_returns if x['level_diff'] is not None and x['mu_nolvl'] is not None]
        f.write("2. IPOTESI LIVELLI vs DECK (Chi causa il dolore?)\n")
        if valid_comp:
            avg_lvl = statistics.mean([x['level_diff'] for x in valid_comp])
            avg_nolvl = statistics.mean([x['mu_nolvl'] for x in valid_comp])
            avg_real = statistics.mean([x['return_mu'] for x in valid_comp])
            
            f.write(f"   Matchup Reale Medio:   {avg_real:.2f}%\n")
            f.write(f"   Matchup No-Lvl Medio:  {avg_nolvl:.2f}%\n")
            f.write(f"   Level Diff Medio:      {avg_lvl:+.2f}\n")
        f.write("\n")

        # 3. TIME SLOT
        valid_time = [x for x in bad_streak_returns if x['time_improvement'] is not None]
        f.write("3. IPOTESI FASCIA ORARIA ('Tornare in un momento migliore aiuta?')\n")
        if valid_time:
            better_time = [x for x in valid_time if x['time_improvement'] > 2.0]
            worse_time = [x for x in valid_time if x['time_improvement'] <= 2.0]
            
            f.write(f"   Ritorni in Orario Migliore (>+2% atteso): {len(better_time)}\n")
            if len(better_time) > 5 and len(worse_time) > 5:
                stat, p_val = mannwhitneyu([x['return_mu'] for x in better_time], [x['return_mu'] for x in worse_time], alternative='greater')
                f.write(f"   Test Mann-Whitney (Better > Worse): p={p_val:.4f}\n")
                if p_val < 0.05:
                    f.write("   -> RISULTATO: SÌ. Tornare in un orario favorevole migliora il matchup.\n")
                else:
                    f.write("   -> RISULTATO: NO. La streak negativa persiste indipendentemente dall'orario.\n")
            
        f.write("="*80 + "\n")