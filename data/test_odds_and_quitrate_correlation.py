import scipy.stats as stats
import math

def calculate_correlation_pity_ragequit(profiles, matchup_stats):
    """
    Calcola la correlazione di Spearman tra il Pity Odds Ratio (dai matchup) 
    e il Ragequit Rate (dai profili).
    """
    pity_odds_ratios = []
    ragequit_ratios = []

    for tag, stats_data in matchup_stats.items():
        if tag in profiles:
            rq_rate = profiles[tag].get('ragequit_rate', 0)
            
            # stats_data ha la struttura {'pity': {...}, 'punish': {...}}
            pity_stats = stats_data.get('pity', {})
            or_pity = pity_stats.get('odds_ratio')
            
            if or_pity is not None and not math.isinf(or_pity) and not math.isnan(or_pity):
                pity_odds_ratios.append(or_pity)
                ragequit_ratios.append(rq_rate)

    if len(pity_odds_ratios) > 2:
        corr, p_val = stats.spearmanr(pity_odds_ratios, ragequit_ratios)
        return {"correlation": corr, "p_value": p_val, "sample_size": len(pity_odds_ratios)}
    
    return None