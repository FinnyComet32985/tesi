import math

def ragequit_and_odds_correlation(profiles, matchup_stats):
    """
    Calcola la correlazione di Spearman tra il Pity Odds Ratio (dai matchup) 
    e l'Indice di Frustrazione (FSI) (dai profili).
    """
    pity_odds_ratios = []
    punitive_odds_ratios = []
    fsi_ratios = []
    details = []

    for tag, stats_data in matchup_stats.items():
        if tag in profiles:
            fsi = profiles[tag].get('avg_fsi', 0)
            
            # stats_data ha la struttura {'pity': {...}, 'punish': {...}}
            pity_stats = stats_data.get('pity', {})
            punish_stats = stats_data.get('punish', {})

            or_pity = pity_stats.get('odds_ratio')
            or_punish = punish_stats.get('odds_ratio')


            if (or_pity is not None and not math.isinf(or_pity) and not math.isnan(or_pity)) or (or_punish is not None and not math.isinf(or_punish) and not math.isnan(or_punish)):
                pity_odds_ratios.append(or_pity)
                punitive_odds_ratios.append(or_punish)
                fsi_ratios.append(fsi)
                details.append({'tag': tag, 'pity_odds_ratio': or_pity, 'punish_odds_ratio': or_punish, 'fsi': fsi})

    _print_table(details)
    #return details

def _print_table(details):
    # Ordina per Ragequit Rate decrescente
    details.sort(key=lambda x: x['fsi'], reverse=True)

    print(f"\n{'='*85}")
    print(f" DETTAGLIO COMPLETO ({len(details)} giocatori)")
    print(f"{'='*85}")
    print(f"{'PLAYER TAG':<15} | {'FSI':<15} | {'PITY ODDS':<15} | {'PUNISH ODDS':<15}")
    print(f"{'-'*85}")

    for d in details:
        pity = f"{d['pity_odds_ratio']:.2f}" if _is_valid(d['pity_odds_ratio']) else "-"
        punish = f"{d['punish_odds_ratio']:.2f}" if _is_valid(d['punish_odds_ratio']) else "-"
        print(f"{d['tag']:<15} | {d['fsi']:<15.2f} | {pity:<15} | {punish:<15}")
    
    print(f"{'='*85}\n")

    # Raggruppamento per fasce di FSI
    groups = {
        "Low FSI (< 0.85)": [d for d in details if d['fsi'] < 0.85],
        "Medium FSI (0.85 - 1.30)": [d for d in details if 0.85 <= d['fsi'] <= 1.30],
        "High FSI (> 1.30)": [d for d in details if d['fsi'] > 1.30]
    }

    print(f"{'='*85}")
    print(" ANALISI PER FASCE DI FSI")
    print(f"{'='*85}")

    for label, group in groups.items():
        print(f"\n--- {label} (n={len(group)}) ---")
        if not group:
            print("Nessun giocatore in questa fascia.")
            continue

        print(f"{'PLAYER TAG':<15} | {'FSI':<15} | {'PITY ODDS':<15} | {'PUNISH ODDS':<15}")
        print(f"{'-'*85}")

        valid_pity = []
        valid_punish = []

        for d in group:
            pity_val = d['pity_odds_ratio']
            punish_val = d['punish_odds_ratio']
            
            pity_str = "-"
            if _is_valid(pity_val):
                valid_pity.append(pity_val)
                pity_str = f"{pity_val:.2f}"
            
            punish_str = "-"
            if _is_valid(punish_val):
                valid_punish.append(punish_val)
                punish_str = f"{punish_val:.2f}"

            print(f"{d['tag']:<15} | {d['fsi']:<15.2f} | {pity_str:<15} | {punish_str:<15}")

        avg_pity = sum(valid_pity) / len(valid_pity) if valid_pity else 0
        avg_punish = sum(valid_punish) / len(valid_punish) if valid_punish else 0

        print(f"{'-'*85}")
        print(f"{'MEDIA':<15} | {'':<15} | {avg_pity:<15.2f} | {avg_punish:<15.2f}")
        print(f"{'-'*85}")

def _is_valid(val):
    return val is not None and not math.isnan(val) and not math.isinf(val)