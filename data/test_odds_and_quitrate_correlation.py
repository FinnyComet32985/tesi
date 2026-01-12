import scipy.stats as stats
import math
import random

def calculate_correlation_pity_ragequit(profiles, matchup_stats):
    """
    Calcola la correlazione di Spearman tra il Pity Odds Ratio (dai matchup) 
    e il Ragequit Rate (dai profili).
    """
    pity_odds_ratios = []
    fsi_ratios = []
    ers_ratios = []
    details = []

    for tag, stats_data in matchup_stats.items():
        if tag in profiles:
            profile = profiles[tag]
            fsi = profile.get('avg_fsi', 0)
            ers = profile.get('ers', 0)
            
            # stats_data ha la struttura {'pity': {...}, 'punish': {...}}
            pity_stats = stats_data.get('pity', {})
            or_pity = pity_stats.get('odds_ratio')
            
            if or_pity is not None and not math.isinf(or_pity) and not math.isnan(or_pity):
                pity_odds_ratios.append(or_pity)
                fsi_ratios.append(fsi)
                ers_ratios.append(ers)
                details.append({'tag': tag, 'odds_ratio': or_pity, 'fsi': fsi, 'ers': ers})

    if len(pity_odds_ratios) > 2:
        corr_fsi, p_val_fsi = stats.spearmanr(pity_odds_ratios, fsi_ratios)
        corr_ers, p_val_ers = stats.spearmanr(pity_odds_ratios, ers_ratios)
        
        # Esecuzione Shuffle Test per ERS (10.000 permutazioni)
        print(f"   > Esecuzione Shuffle Test su ERS (10.000 permutazioni)...")
        perm_p_val_ers = _perform_permutation_test(pity_odds_ratios, ers_ratios, corr_ers)
        
        return {
            "fsi": {"correlation": corr_fsi, "p_value": p_val_fsi},
            "ers": {"correlation": corr_ers, "p_value": p_val_ers, "perm_p_value": perm_p_val_ers},
            "sample_size": len(pity_odds_ratios),
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