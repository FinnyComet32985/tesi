import scipy.stats as stats
import math
import random

def calculate_correlation_pity_ragequit(profiles, matchup_stats):
    """
    Calcola la correlazione di Spearman tra Odds Ratio (Pity e Punish) 
    e le metriche comportamentali (FSI, ERS).
    """
    return {
        "pity": _calculate_single_metric_correlation(profiles, matchup_stats, 'pity'),
        "punish": _calculate_single_metric_correlation(profiles, matchup_stats, 'punish')
    }

def _calculate_single_metric_correlation(profiles, matchup_stats, metric_type):
    valid_data = []
    finite_odds = []

    for tag, stats_data in matchup_stats.items():
        if tag in profiles:
            profile = profiles[tag]
            fsi = profile.get('avg_fsi', 0)
            ers = profile.get('ers', 0)
            
            # stats_data ha la struttura {'pity': {...}, 'punish': {...}}
            type_stats = stats_data.get(metric_type, {})
            odds = type_stats.get('odds_ratio')
            
            # Escludiamo NaN (0/0: condizione mai verificata) e None.
            # MANTENIAMO inf per ora.
            if odds is not None and not math.isnan(odds):
                valid_data.append({'tag': tag, 'odds': odds, 'fsi': fsi, 'ers': ers})
                if not math.isinf(odds):
                    finite_odds.append(odds)

    # Gestione INF: Sostituiamo INF con un valore più alto del massimo finito osservato
    # per preservare il rango (Spearman) senza rompere il calcolo.
    max_finite = max(finite_odds) if finite_odds else 10.0
    inf_replacement = max_finite * 1.5

    odds_ratios = []
    fsi_ratios = []
    ers_ratios = []
    details = []

    for item in valid_data:
        val = item['odds']
        if math.isinf(val):
            val = inf_replacement

        odds_ratios.append(val)
        fsi_ratios.append(item['fsi'])
        ers_ratios.append(item['ers'])
        details.append({'tag': item['tag'], 'odds_ratio': val, 'fsi': item['fsi'], 'ers': item['ers']})

    if len(odds_ratios) > 2:
        corr_fsi, p_val_fsi = stats.spearmanr(odds_ratios, fsi_ratios)
        corr_ers, p_val_ers = stats.spearmanr(odds_ratios, ers_ratios)
        
        # Esecuzione Shuffle Test per ERS (10.000 permutazioni)
        print(f"   > Esecuzione Shuffle Test su ERS ({metric_type}) (10.000 permutazioni)...")
        perm_p_val_ers = _perform_permutation_test(odds_ratios, ers_ratios, corr_ers)
        
        return {
            "fsi": {"correlation": corr_fsi, "p_value": p_val_fsi},
            "ers": {"correlation": corr_ers, "p_value": p_val_ers, "perm_p_value": perm_p_val_ers},
            "sample_size": len(odds_ratios),
            "details": details
        }
    
    return None

def _perform_permutation_test(x, y, observed_corr, num_simulations=10000):
    """Esegue un test di permutazione per verificare la robustezza della correlazione."""
    count_extreme = 0
    y_shuffled = list(y)
    
    for _ in range(num_simulations):
        random.shuffle(y_shuffled)
        corr, _ = stats.spearmanr(x, y_shuffled)
        # Test a due code: contiamo quante volte la correlazione casuale è forte quanto quella osservata
        if abs(corr) >= abs(observed_corr):
            count_extreme += 1
            
    return count_extreme / num_simulations