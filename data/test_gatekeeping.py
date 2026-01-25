import os
import statistics
from scipy.stats import mannwhitneyu

def get_arena_thresholds(cursor):
    """Aggiorna le soglie delle arene dal database."""
    if not cursor: 
        return
    try:
        cursor.execute("SELECT trophy_limit FROM arenas ORDER BY trophy_limit ASC")
        rows = cursor.fetchall()
        if rows:
            return [row[0] for row in rows]
    except Exception as e:
        print(f"Errore recupero soglie arene: {e}")
        return []

def run_gatekeeping_test(players_sessions, analysis_type, gate_range=150, ARENA_THRESHOLDS=None):
    """
    Esegue il test statistico Mann-Whitney U per il Gatekeeping (Globale).
    analysis_type: 'matchup', 'levels', 'nolvl'
    """

    if not ARENA_THRESHOLDS:
        return

    data = {
        'danger': [],
        'safe': []
    }
    
    for p in players_sessions:
        for s in p['sessions']:
            for b in s['battles']:
                if b['game_mode'] != 'Ladder': continue
                
                trophies = b.get('trophies_before')
                if not trophies: continue
                
                # Find next threshold
                next_gate = None
                for t in ARENA_THRESHOLDS:
                    if t > trophies:
                        next_gate = t
                        break
                
                if not next_gate: continue
                
                dist = next_gate - trophies
                is_danger = dist <= gate_range
                
                val = None
                if analysis_type == 'matchup':
                    val = b.get('matchup')
                elif analysis_type == 'levels':
                    val = b.get('level_diff')
                elif analysis_type == 'nolvl':
                    val = b.get('matchup_no_lvl')
                
                if val is not None:
                    if is_danger:
                        data['danger'].append(val)
                    else:
                        data['safe'].append(val)
    
    result = {'type': analysis_type, 'stats': {}, 'counts': {}}
    result['counts'] = {'danger': len(data['danger']), 'safe': len(data['safe'])}
    
    if result['counts']['danger'] < 10 or result['counts']['safe'] < 10:
        result['stats']['error'] = "Dati insufficienti"
        return result

    # Mann-Whitney U Test
    # H1: Danger < Safe (Values are worse in Danger zone)
    stat, p = mannwhitneyu(data['danger'], data['safe'], alternative='less')
    
    result['stats'] = {
        'u_stat': stat,
        'p_value': p,
        'avg_danger': statistics.mean(data['danger']),
        'avg_safe': statistics.mean(data['safe'])
    }
        
    return result

def save_gatekeeping_results(result, output_file):
    """Salva i risultati in append sul file."""
    atype = result['type']
    stats = result['stats']
    counts = result['counts']
    
    with open(output_file, 'a', encoding='utf-8') as f:
        f.write(f"\n--- ANALISI: {atype.upper()} ---\n")
        
        if 'error' in stats:
            f.write(f"Errore: {stats['error']}\n")
            f.write("-" * 40 + "\n")
            return

        f.write(f"Campione: Danger={counts['danger']}, Safe={counts['safe']}\n")
        f.write(f"Media: Danger={stats['avg_danger']:.4f}, Safe={stats['avg_safe']:.4f}\n")
        f.write(f"Delta: {stats['avg_danger'] - stats['avg_safe']:.4f}\n")
        f.write(f"P-value (Mann-Whitney U <): {stats['p_value']:.4f}\n")
        
        if stats['p_value'] < 0.05:
            f.write("RISULTATO: SIGNIFICATIVO. Valori peggiori vicino alla soglia (Gatekeeping).\n")
        else:
            f.write("RISULTATO: NON SIGNIFICATIVO.\n")
        
        f.write("-" * 40 + "\n")

def analyze_gatekeeping_all(players_sessions, cursor=None, output_dir=None, gate_range=150):
    if output_dir is None: 
        return
    
    ARENA_THRESHOLDS = get_arena_thresholds(cursor)
    
    output_file = os.path.join(output_dir, 'gatekeeping_results.txt')
    print(f"\nGenerazione report Gatekeeping (Unified Mann-Whitney) in: {output_file}")
    
    # Reset file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("ANALISI GATEKEEPING UNIFICATA (MANN-WHITNEY)\n")
        f.write(f"Range Gate: {gate_range} trofei\n")
        f.write("Ipotesi: I valori (Matchup/Livelli) sono peggiori nella Danger Zone.\n")
        f.write("============================================================\n")

    for atype in ['matchup', 'levels', 'nolvl']:
        res = run_gatekeeping_test(players_sessions, atype, gate_range, ARENA_THRESHOLDS)
        save_gatekeeping_results(res, output_file)
