import os
from datetime import datetime

def generate_report(profiles, matchup_stats, correlation_results=None, chi2_results=None):
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

    # 4. Report Chi-Square Independence
    if chi2_results:
        _save_chi2_report(chi2_results, results_dir)

def _save_classifier_report(profiles, results_dir):
    output_path = os.path.join(results_dir, 'classifier_results.txt')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"Analisi Classificatore eseguita il: {datetime.now()}\n")
        
        for tag, profile in profiles.items():
            _print_profile_advanced(profile, tag, f)
            
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

        for metric_type in ['pity', 'punish']:
            res_data = correlation_results.get(metric_type)
            if not res_data:
                continue
                
            res_fsi = res_data.get('fsi', {})
            res_ers = res_data.get('ers', {})
            sample_size = res_data['sample_size']
            details = res_data.get('details', [])
            
            label = "PITY ODDS" if metric_type == 'pity' else "PUNISH ODDS"
            
            log_msg = "\n" + "="*60 + "\n"
            log_msg += f" ANALISI CORRELAZIONE SPEARMAN ({label})\n"
            log_msg += "="*60 + "\n"
            
            log_msg += f"1. {label} vs FSI (Frustration Sensitivity)\n"
            log_msg += f"   Correlazione: {res_fsi.get('correlation', 0):.4f}\n"
            log_msg += f"   P-value:      {res_fsi.get('p_value', 1):.4f}\n\n"
            
            log_msg += f"2. {label} vs ERS (Impulsività * exp(-FSI))\n"
            log_msg += f"   Correlazione: {res_ers.get('correlation', 0):.4f}\n"
            log_msg += f"   P-value:      {res_ers.get('p_value', 1):.4f}\n"

            perm_p = res_ers.get('perm_p_value')
            if perm_p is not None:
                log_msg += f"   P-value (Shuffle 10k): {perm_p:.4f}\n"
                if perm_p < 0.05:
                    log_msg += "   -> RISULTATO ROBUSTO (Molto improbabile sia casuale)\n"
                else:
                    log_msg += "   -> RISULTATO NON ROBUSTO (Potrebbe essere frutto del caso)\n"

            log_msg += f"Campione: {sample_size} giocatori\n" + "="*60
            
            print(log_msg)
            f.write(log_msg + "\n")

            if details:
                # Ordina per Odds Ratio decrescente per evidenziare i casi più estremi
                details.sort(key=lambda x: x['odds_ratio'], reverse=True)

                table_header = f"\n{'='*75}\n DETTAGLIO GIOCATORI ({label})\n{'='*75}\n"
                table_header += f"{'PLAYER TAG':<20} | {'ODDS RATIO':<15} | {'FSI':<15} | {'ERS':<15}\n"
                table_header += f"{'-'*75}"
                
                print(table_header)
                f.write(table_header + "\n")
                
                for d in details:
                    ers_val = d.get('ers', 0)
                    line = f"{d['tag']:<20} | {d['odds_ratio']:<15.2f} | {d['fsi']:<15.2f} | {ers_val:<15.2f}"
                    print(line)
                    f.write(line + "\n")
    
    print(f"\nI risultati della correlazione sono stati salvati in: {output_path}")

def _save_chi2_report(chi2_results, results_dir):
    output_path = os.path.join(results_dir, 'chi_square_independence_results.txt')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"Analisi Chi-Quadro Indipendenza (Streak vs Matchup) eseguita il: {datetime.now()}\n")
        
        significant_count = 0
        total_count = len(chi2_results)

        for tag, res in chi2_results.items():
            if res['significant']:
                significant_count += 1
            
            f.write(f"\n\n{'#'*60}\n# PLAYER: {tag}\n{'#'*60}\n")
            f.write(f"Statistica Chi-Quadro: {res['chi2_stat']:.4f}\n")
            f.write(f"Valore Critico (95%):  {res['critical_value']:.4f}\n")
            f.write(f"P-value:               {res['p_value']:.4f} ({res.get('method', 'Asymptotic')})\n")
            if res.get('low_expected', False):
                f.write("WARNING: Celle con frequenza attesa < 5. (Monte Carlo applicato per robustezza)\n")
            f.write(f"Risultato:             {'DIPENDENZA SIGNIFICATIVA' if res['significant'] else 'Indipendenza (Nulla non rifiutata)'}\n")
            
            f.write("\n")
            f.write(_format_dataframe_table(res['observed'], "TABELLA OSSERVATA (Conteggi Reali)"))
            f.write("\n")
            f.write(_format_dataframe_table(res['expected'], "TABELLA ATTESA (Teorica)"))

        if total_count > 0:
            summary = f"\n\n{'='*60}\n RIEPILOGO GENERALE\n{'='*60}\n"
            summary += f"Totale Giocatori Analizzati: {total_count}\n"
            summary += f"Giocatori con Dipendenza Significativa: {significant_count} ({(significant_count/total_count*100):.2f}%)\n"
            f.write(summary)
            print(f"\nI risultati del test Chi-Quadro sono stati salvati in: {output_path}")

def _format_dataframe_table(df, title):
    """Formatta un DataFrame pandas in una tabella testuale allineata."""
    lines = []
    lines.append(f"--- {title} ---")
    
    # L'indice del DF contiene le categorie di Streak (es. Losing Streak)
    row_labels = [str(x) for x in df.index]
    col_labels = [str(x) for x in df.columns]
    
    # Calcolo larghezza prima colonna (etichette righe)
    # 'Streak' è l'intestazione fittizia per l'indice
    first_col_width = max(len("Streak"), max([len(x) for x in row_labels]) if row_labels else 0) + 5
    
    # Calcolo larghezza colonne dati
    col_widths = []
    for col in df.columns:
        w = len(str(col))
        for val in df[col]:
            if isinstance(val, float):
                w = max(w, len(f"{val:.2f}"))
            else:
                w = max(w, len(str(val)))
        col_widths.append(w + 5) # Padding abbondante
        
    # Costruzione Header
    header = f"{'Streak':<{first_col_width}} | " + " | ".join(f"{c:<{w}}" for c, w in zip(col_labels, col_widths))
    lines.append(header)
    lines.append("-" * len(header))
    
    # Costruzione Righe
    for idx in df.index:
        row_str = f"{str(idx):<{first_col_width}} | "
        vals = []
        for i, col in enumerate(df.columns):
            val = df.at[idx, col]
            if isinstance(val, float):
                val_str = f"{val:.2f}"
            else:
                val_str = str(val)
            vals.append(f"{val_str:<{col_widths[i]}}")
        row_str += " | ".join(vals)
        lines.append(row_str)
        
    return "\n".join(lines) + "\n"

def _print_profile_advanced(profile, tag, file):
    """
    Stampa il profilo comportamentale arricchito con metriche EOMM-ready.
    """
    def log(msg):
        print(msg)
        file.write(msg + "\n")

    # Mappatura etichette aggiornata con le nuove metriche
    labels = {
        'total_matches': 'Totale Partite',
        'num_sessions': 'Numero Sessioni',
        'avg_session_min': 'Durata Media Sess. (min)',
        'matches_per_session': 'Partite per Sessione',
        'avg_matchup_pct': 'Matchup Medio (%)',
        'avg_matchup_no_lvl_pct': 'Matchup No-Lvl (%)',
        'avg_level_diff': 'Level Diff Medio',
        'avg_fsi': 'Indice Frustrazione (FSI)', # Nuova
        'quit_impulsivity': 'Impulsività Quit (Avg)', # Nuova
        'ers': 'ERS (Impulsività * exp(-FSI))', # Nuova
        'is_reliable': 'Affidabilità Campione',    # Nuova
        'max_loss_streak_tolerated': 'Max Loss Streak (Toll.)',
        'win_continuation_rate': 'Win Continuation (%)',
        'loss_continuation_rate': 'Loss Continuation (%)',
        'counter_streak_continuations': 'Counter Streak Cont.',
        'l_streak_count': 'Resilienza (Partite in Loss)'
    }

    log("\n" + "="*45)
    log(f" PLAYER: {tag}")
    log("="*45)
    log(f"{'METRICA':<30} | {'VALORE':<10}")
    log("-" * 45)
    
    for key, label in labels.items():
        val = profile.get(key, "N/A")
        
        # Formattazione speciale per il booleano di affidabilità
        if key == 'is_reliable':
            val = "ALTA" if val else "BASSA (Rumore)"
        
        log(f"{label:<30} | {str(val):<10}")
    
    log("-" * 45)

    # Nota interpretativa automatica per la tesi
    fsi = profile.get('avg_fsi', 0)
    if profile.get('is_reliable'):
        if fsi > 1.8:
            log("ANALISI: Player sensibile (High FSI). Target ideale per EOMM.")
        elif fsi < 1.0:
            log("ANALISI: Player resiliente (Low FSI). Bassa probabilità di manipolazione.")
    else:
        log("ANALISI: Campione insufficiente o sessioni troppo brevi per analisi EOMM.")
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
