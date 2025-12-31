import os
from datetime import datetime

def generate_report(profiles, matchup_stats, correlation_results=None):
    """Genera i report su file e console basandosi sui dati calcolati."""
    results_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(results_dir, exist_ok=True)
    
    # 1. Report Classifier
    _save_classifier_report(profiles, results_dir)
    
    # 2. Report Extreme Matchup
    _save_matchup_report(matchup_stats, results_dir)

    # 3. Report Correlation
    if correlation_results:
        _save_correlation_report(correlation_results, results_dir)

def _save_classifier_report(profiles, results_dir):
    output_path = os.path.join(results_dir, 'classifier_results.txt')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"Analisi Classificatore eseguita il: {datetime.now()}\n")
        
        for tag, profile in profiles.items():
            _print_profile(profile, tag, f)
            
    print(f"\nI risultati del classificatore sono stati salvati in: {output_path}")

def _save_matchup_report(matchup_stats, results_dir):
    output_path = os.path.join(results_dir, 'fisher_extreme_matchup_results.txt')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"Analisi Extreme Matchup eseguita il: {datetime.now()}\n")

        for tag, stats_data in matchup_stats.items():
            # Intestazione
            header = f"\n{'#'*40}\n# PLAYER: {tag}\n{'#'*40}"
            print(header)
            f.write(header + "\n")

            # Pity Match Analysis
            pity_stats = stats_data['pity']
            _print_fisher_table(pity_stats, "PITY MATCH", "Dopo Losing Streak (>=3L)", "Matchup > 80%", f)
            
            # Punish Match Analysis
            punish_stats = stats_data['punish']
            _print_fisher_table(punish_stats, "MATCHUP PUNITIVI", "Dopo Win Streak (>=3W)", "Matchup < 40%", f)

    print(f"\nI risultati dell'analisi matchup sono stati salvati in: {output_path}")

def _save_correlation_report(correlation_results, results_dir):
    output_path = os.path.join(results_dir, 'correlation_results.txt')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"Analisi Correlazione eseguita il: {datetime.now()}\n")

        corr = correlation_results['correlation']
        p_val = correlation_results['p_value']
        sample_size = correlation_results['sample_size']
        details = correlation_results.get('details', [])
        
        log_msg = "\n" + "="*60 + "\n"
        log_msg += " ANALISI CORRELAZIONE SPEARMAN (Pity Odds vs Ragequit)\n"
        log_msg += "="*60 + "\n"
        log_msg += f"Correlazione: {corr:.4f}\n"
        log_msg += f"P-value: {p_val:.4f}\n"
        log_msg += f"Campione: {sample_size} giocatori\n" + "="*60
        
        print(log_msg)
        f.write(log_msg + "\n")

        if details:
            # Ordina per Odds Ratio decrescente per evidenziare i casi più estremi
            details.sort(key=lambda x: x['odds_ratio'], reverse=True)

            table_header = f"\n{'='*60}\n DETTAGLIO GIOCATORI\n{'='*60}\n"
            table_header += f"{'PLAYER TAG':<20} | {'PITY ODDS':<15} | {'RAGEQUIT %':<15}\n"
            table_header += f"{'-'*60}"
            
            print(table_header)
            f.write(table_header + "\n")
            
            for d in details:
                line = f"{d['tag']:<20} | {d['odds_ratio']:<15.2f} | {d['ragequit_rate']:<15.2f}"
                print(line)
                f.write(line + "\n")
    
    print(f"\nI risultati della correlazione sono stati salvati in: {output_path}")

def _print_profile(profile, tag, file):
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

def _print_fisher_table(stats_data, label, condition_name, effect_name, file):
    def log(msg):
        print(msg)
        file.write(msg + "\n")

    matrix = stats_data['matrix']
    odds_ratio = stats_data['odds_ratio']
    p_value = stats_data['p_value']

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
    
    log(f"Rapporto di probabilità (Odds Ratio): {odds_ratio:.2f}")
    log(f"Significatività (p-value): {p_value:.6f}")
    
    if p_value < 0.05:
        status = "CONFERMATA (EOMM Probabile)"
    else:
        status = "NON CONFERMATA (Casualità)"
    
    log(f"IPOTESI: {status}")
    log("="*60)


