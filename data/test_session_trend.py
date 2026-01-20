
import os
import statistics
from scipy.stats import wilcoxon, spearmanr

def analyze_session_trends(players_sessions, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'session_trend_results.txt')

    print(f"\nGenerazione report trend intra-sessione in: {output_file}")

    # Accumulatori per i test statistici (dati appaiati per sessione)
    # Ogni elemento è una tupla (valore_inizio, valore_fine)
    win_pairs = []
    matchup_pairs = []
    level_pairs = []
    matchup_nolvl_pairs = []
    
    # Accumulatori per statistiche descrittive
    start_winrates = []
    end_winrates = []
    start_matchups = []
    end_matchups = []
    start_matchups_nolvl = []
    end_matchups_nolvl = []
    start_levels = []
    end_levels = []

    # --- TEST 2: First 3 vs Remaining (Asymmetric) ---
    win_pairs_rem = []
    matchup_pairs_rem = []
    head_winrates = []
    tail_winrates = []
    head_matchups = []
    tail_matchups = []
    matchup_nolvl_pairs_rem = []
    head_matchups_nolvl = []
    tail_matchups_nolvl = []
    level_pairs_rem = []
    head_levels = []
    tail_levels = []

    # Accumulatori per correlazione (Lunghezza Sessione vs Delta)
    corr_win = []
    corr_mu = []
    corr_munl = []
    corr_lvl = []

    MIN_SESSION_LEN = 4
    HOOK_SIZE = 3
    
    count_sessions = 0
    count_sessions_rem = 0

    for p in players_sessions:
        for session in p['sessions']:
            battles = session['battles']
            n = len(battles)
            
            if n < MIN_SESSION_LEN:
                continue
            
            # Definiamo la finestra di analisi
            # Per sessioni corte (4-7), k=2 (Primi 2 vs Ultimi 2).
            # Per sessioni lunghe (8+), k=3 (Primi 3 vs Ultimi 3).
            k = 2 if n < 8 else 3
            
            start_slice = battles[:k]
            end_slice = battles[-k:]
            
            # --- Calcolo Win Rate ---
            w_start = sum(1 for b in start_slice if b['win']) / k
            w_end = sum(1 for b in end_slice if b['win']) / k
            
            win_pairs.append((w_start, w_end))
            start_winrates.append(w_start)
            end_winrates.append(w_end)
            
            # --- Calcolo Matchup (solo se disponibile) ---
            mus_start = [b['matchup'] for b in start_slice if b['matchup'] is not None]
            mus_end = [b['matchup'] for b in end_slice if b['matchup'] is not None]
            
            # Consideriamo valido il confronto matchup solo se abbiamo dati per entrambi i lati
            if len(mus_start) == k and len(mus_end) == k:
                m_start = statistics.mean(mus_start)
                m_end = statistics.mean(mus_end)
                matchup_pairs.append((m_start, m_end))
                start_matchups.append(m_start)
                end_matchups.append(m_end)

            # --- Calcolo Matchup No-Lvl ---
            mus_nolvl_start = [b.get('matchup_no_lvl') for b in start_slice if b.get('matchup_no_lvl') is not None]
            mus_nolvl_end = [b.get('matchup_no_lvl') for b in end_slice if b.get('matchup_no_lvl') is not None]
            
            if len(mus_nolvl_start) == k and len(mus_nolvl_end) == k:
                m_start = statistics.mean(mus_nolvl_start)
                m_end = statistics.mean(mus_nolvl_end)
                matchup_nolvl_pairs.append((m_start, m_end))
                start_matchups_nolvl.append(m_start)
                end_matchups_nolvl.append(m_end)

            # --- Calcolo Level Diff ---
            levs_start = [b['level_diff'] for b in start_slice if b['level_diff'] is not None]
            levs_end = [b['level_diff'] for b in end_slice if b['level_diff'] is not None]
            
            if len(levs_start) == k and len(levs_end) == k:
                l_start = statistics.mean(levs_start)
                l_end = statistics.mean(levs_end)
                level_pairs.append((l_start, l_end))
                start_levels.append(l_start)
                end_levels.append(l_end)
            
            count_sessions += 1
            
            # --- LOGICA TEST 2 (First 3 vs Remaining) ---
            if n > HOOK_SIZE:
                head_slice = battles[:HOOK_SIZE]
                tail_slice = battles[HOOK_SIZE:]
                
                w_head = sum(1 for b in head_slice if b['win']) / len(head_slice)
                w_tail = sum(1 for b in tail_slice if b['win']) / len(tail_slice)
                
                win_pairs_rem.append((w_head, w_tail))
                head_winrates.append(w_head)
                tail_winrates.append(w_tail)
                
                # Add for correlation
                corr_win.append((n, w_tail - w_head))
                
                mus_head = [b['matchup'] for b in head_slice if b['matchup'] is not None]
                mus_tail = [b['matchup'] for b in tail_slice if b['matchup'] is not None]
                
                # Richiediamo dati validi per il confronto (almeno 2/3 validi in testa e 1 in coda)
                if len(mus_head) >= (HOOK_SIZE - 1) and len(mus_tail) > 0:
                    m_head = statistics.mean(mus_head)
                    m_tail = statistics.mean(mus_tail)
                    matchup_pairs_rem.append((m_head, m_tail))
                    head_matchups.append(m_head)
                    tail_matchups.append(m_tail)
                    # Add for correlation
                    corr_mu.append((n, m_tail - m_head))

                mus_nolvl_head = [b.get('matchup_no_lvl') for b in head_slice if b.get('matchup_no_lvl') is not None]
                mus_nolvl_tail = [b.get('matchup_no_lvl') for b in tail_slice if b.get('matchup_no_lvl') is not None]
                
                if len(mus_nolvl_head) >= (HOOK_SIZE - 1) and len(mus_nolvl_tail) > 0:
                    m_head = statistics.mean(mus_nolvl_head)
                    m_tail = statistics.mean(mus_nolvl_tail)
                    matchup_nolvl_pairs_rem.append((m_head, m_tail))
                    head_matchups_nolvl.append(m_head)
                    tail_matchups_nolvl.append(m_tail)
                    # Add for correlation
                    corr_munl.append((n, m_tail - m_head))

                levs_head = [b['level_diff'] for b in head_slice if b['level_diff'] is not None]
                levs_tail = [b['level_diff'] for b in tail_slice if b['level_diff'] is not None]
                
                if len(levs_head) >= (HOOK_SIZE - 1) and len(levs_tail) > 0:
                    l_head = statistics.mean(levs_head)
                    l_tail = statistics.mean(levs_tail)
                    level_pairs_rem.append((l_head, l_tail))
                    head_levels.append(l_head)
                    tail_levels.append(l_tail)
                    # Add for correlation
                    corr_lvl.append((n, l_tail - l_head))
                
                count_sessions_rem += 1

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI TREND INTRA-SESSIONE (HOOK & FRUSTRATION)\n")
        f.write("Obiettivo: Verificare se le sessioni iniziano con vittorie/matchup facili (Hook) e finiscono con sconfitte/matchup difficili (Frustration/Churn).\n")
        f.write(f"Criteri: Sessioni con almeno {MIN_SESSION_LEN} partite. Confronto Primi k vs Ultimi k match.\n")
        f.write("="*80 + "\n\n")
        
        f.write(f"Totale Sessioni Analizzate: {count_sessions}\n")
        f.write("-" * 80 + "\n")
        
        # --- ANALISI WIN RATE ---
        avg_w_start = statistics.mean(start_winrates) if start_winrates else 0
        avg_w_end = statistics.mean(end_winrates) if end_winrates else 0
        
        f.write("1. WIN RATE (Inizio vs Fine)\n")
        f.write(f"   Media Win Rate INIZIO: {avg_w_start*100:.2f}%\n")
        f.write(f"   Media Win Rate FINE:   {avg_w_end*100:.2f}%\n")
        f.write(f"   Delta:                 {(avg_w_end - avg_w_start)*100:+.2f}%\n")
        
        if len(win_pairs) > 10:
            # Wilcoxon Signed-Rank Test (Paired)
            # Alternative 'greater': Start > End
            try:
                stat_w, p_w = wilcoxon([x[0] for x in win_pairs], [x[1] for x in win_pairs], alternative='greater')
                f.write(f"   Test Wilcoxon (Inizio > Fine): p-value = {p_w:.4f}\n")
                if p_w < 0.05:
                    f.write("   RISULTATO: SIGNIFICATIVO. I giocatori vincono significativamente di più all'inizio della sessione.\n")
                else:
                    f.write("   RISULTATO: NON SIGNIFICATIVO. Non c'è evidenza di un calo sistematico di vittorie.\n")
            except Exception as e:
                f.write(f"   Errore Test Statistico (possibili dati costanti): {e}\n")
        else:
            f.write("   Dati insufficienti per il test statistico.\n")
        f.write("\n")

        # --- ANALISI MATCHUP ---
        avg_m_start = statistics.mean(start_matchups) if start_matchups else 0
        avg_m_end = statistics.mean(end_matchups) if end_matchups else 0
        
        f.write("2. MATCHUP QUALITY (Inizio vs Fine)\n")
        f.write(f"   Media Matchup INIZIO: {avg_m_start:.2f}%\n")
        f.write(f"   Media Matchup FINE:   {avg_m_end:.2f}%\n")
        f.write(f"   Delta:                {avg_m_end - avg_m_start:+.2f}%\n")
        
        if len(matchup_pairs) > 10:
            # Wilcoxon Signed-Rank Test (Paired)
            # Alternative 'greater': Start > End
            try:
                stat_m, p_m = wilcoxon([x[0] for x in matchup_pairs], [x[1] for x in matchup_pairs], alternative='greater')
                f.write(f"   Test Wilcoxon (Inizio > Fine): p-value = {p_m:.4f}\n")
                if p_m < 0.05:
                    f.write("   RISULTATO: SIGNIFICATIVO. I matchup sono significativamente migliori all'inizio della sessione.\n")
                else:
                    f.write("   RISULTATO: NON SIGNIFICATIVO. La difficoltà del matchup sembra costante.\n")
            except Exception as e:
                f.write(f"   Errore Test Statistico (possibili dati costanti): {e}\n")
        else:
            f.write("   Dati insufficienti per il test statistico.\n")
            
        f.write("\n")

        # --- ANALISI MATCHUP NO-LVL ---
        avg_mnl_start = statistics.mean(start_matchups_nolvl) if start_matchups_nolvl else 0
        avg_mnl_end = statistics.mean(end_matchups_nolvl) if end_matchups_nolvl else 0
        
        f.write("3. MATCHUP NO-LVL (Fair Play) (Inizio vs Fine)\n")
        f.write(f"   Media Matchup No-Lvl INIZIO: {avg_mnl_start:.2f}%\n")
        f.write(f"   Media Matchup No-Lvl FINE:   {avg_mnl_end:.2f}%\n")
        f.write(f"   Delta:                       {avg_mnl_end - avg_mnl_start:+.2f}%\n")
        
        if len(matchup_nolvl_pairs) > 10:
            try:
                stat_mnl, p_mnl = wilcoxon([x[0] for x in matchup_nolvl_pairs], [x[1] for x in matchup_nolvl_pairs], alternative='greater')
                f.write(f"   Test Wilcoxon (Inizio > Fine): p-value = {p_mnl:.4f}\n")
                if p_mnl < 0.05:
                    f.write("   RISULTATO: SIGNIFICATIVO. I matchup 'puri' sono migliori all'inizio.\n")
                else:
                    f.write("   RISULTATO: NON SIGNIFICATIVO.\n")
            except Exception as e:
                f.write(f"   Errore Test: {e}\n")
        
        f.write("\n")

        # --- ANALISI LEVEL DIFF ---
        avg_l_start = statistics.mean(start_levels) if start_levels else 0
        avg_l_end = statistics.mean(end_levels) if end_levels else 0
        
        f.write("4. LEVEL DIFFERENCE (Inizio vs Fine)\n")
        f.write(f"   Media Level Diff INIZIO: {avg_l_start:+.2f}\n")
        f.write(f"   Media Level Diff FINE:   {avg_l_end:+.2f}\n")
        f.write(f"   Delta:                   {avg_l_end - avg_l_start:+.2f}\n")
        
        if len(level_pairs) > 10:
            try:
                stat_l, p_l = wilcoxon([x[0] for x in level_pairs], [x[1] for x in level_pairs], alternative='greater')
                f.write(f"   Test Wilcoxon (Inizio > Fine): p-value = {p_l:.4f}\n")
                f.write(f"   RISULTATO: {'SIGNIFICATIVO (Livelli peggiori alla fine)' if p_l < 0.05 else 'NON SIGNIFICATIVO'}\n")
            except Exception as e:
                f.write(f"   Errore Test: {e}\n")

        # --- REPORT TEST 2 ---
        f.write("\n" + "="*80 + "\n")
        f.write("ANALISI 2: HOOK PHASE (Primi 3) vs RESTO DELLA SESSIONE\n")
        f.write("Obiettivo: Verificare se le prime partite sono sistematicamente più facili del resto della sessione.\n")
        f.write(f"Criteri: Sessioni con > {HOOK_SIZE} partite. Confronto Primi {HOOK_SIZE} vs Rimanenti.\n")
        f.write(f"Sessioni valide per questo test: {count_sessions_rem}\n")
        f.write("-" * 80 + "\n")
        
        avg_w_head = statistics.mean(head_winrates) if head_winrates else 0
        avg_w_tail = statistics.mean(tail_winrates) if tail_winrates else 0
        
        f.write("1. WIN RATE (Hook vs Resto)\n")
        f.write(f"   Media Win Rate HOOK (Primi {HOOK_SIZE}): {avg_w_head*100:.2f}%\n")
        f.write(f"   Media Win Rate RESTO:          {avg_w_tail*100:.2f}%\n")
        f.write(f"   Delta:                         {(avg_w_tail - avg_w_head)*100:+.2f}%\n")
        
        if len(win_pairs_rem) > 10:
            try:
                stat_w2, p_w2 = wilcoxon([x[0] for x in win_pairs_rem], [x[1] for x in win_pairs_rem], alternative='greater')
                f.write(f"   Test Wilcoxon (Hook > Resto): p-value = {p_w2:.4f}\n")
                f.write(f"   RISULTATO: {'SIGNIFICATIVO' if p_w2 < 0.05 else 'NON SIGNIFICATIVO'}\n")
            except Exception as e:
                f.write(f"   Errore Test: {e}\n")
        
        f.write("\n")
        
        avg_m_head = statistics.mean(head_matchups) if head_matchups else 0
        avg_m_tail = statistics.mean(tail_matchups) if tail_matchups else 0
        
        f.write("2. MATCHUP QUALITY (Hook vs Resto)\n")
        f.write(f"   Media Matchup HOOK:  {avg_m_head:.2f}%\n")
        f.write(f"   Media Matchup RESTO: {avg_m_tail:.2f}%\n")
        f.write(f"   Delta:               {avg_m_tail - avg_m_head:+.2f}%\n")
        
        if len(matchup_pairs_rem) > 10:
            try:
                stat_m2, p_m2 = wilcoxon([x[0] for x in matchup_pairs_rem], [x[1] for x in matchup_pairs_rem], alternative='greater')
                f.write(f"   Test Wilcoxon (Hook > Resto): p-value = {p_m2:.4f}\n")
                f.write(f"   RISULTATO: {'SIGNIFICATIVO' if p_m2 < 0.05 else 'NON SIGNIFICATIVO'}\n")
            except Exception as e:
                f.write(f"   Errore Test: {e}\n")
                
        f.write("\n")

        avg_mnl_head = statistics.mean(head_matchups_nolvl) if head_matchups_nolvl else 0
        avg_mnl_tail = statistics.mean(tail_matchups_nolvl) if tail_matchups_nolvl else 0
        
        f.write("3. MATCHUP NO-LVL (Hook vs Resto)\n")
        f.write(f"   Media Matchup No-Lvl HOOK:  {avg_mnl_head:.2f}%\n")
        f.write(f"   Media Matchup No-Lvl RESTO: {avg_mnl_tail:.2f}%\n")
        f.write(f"   Delta:                      {avg_mnl_tail - avg_mnl_head:+.2f}%\n")
        
        if len(matchup_nolvl_pairs_rem) > 10:
            try:
                stat_mnl2, p_mnl2 = wilcoxon([x[0] for x in matchup_nolvl_pairs_rem], [x[1] for x in matchup_nolvl_pairs_rem], alternative='greater')
                f.write(f"   Test Wilcoxon (Hook > Resto): p-value = {p_mnl2:.4f}\n")
                f.write(f"   RISULTATO: {'SIGNIFICATIVO' if p_mnl2 < 0.05 else 'NON SIGNIFICATIVO'}\n")
            except Exception as e:
                f.write(f"   Errore Test: {e}\n")
        
        f.write("\n")

        avg_l_head = statistics.mean(head_levels) if head_levels else 0
        avg_l_tail = statistics.mean(tail_levels) if tail_levels else 0
        
        f.write("4. LEVEL DIFFERENCE (Hook vs Resto)\n")
        f.write(f"   Media Level Diff HOOK:  {avg_l_head:+.2f}\n")
        f.write(f"   Media Level Diff RESTO: {avg_l_tail:+.2f}\n")
        f.write(f"   Delta:                  {avg_l_tail - avg_l_head:+.2f}\n")
        
        if len(level_pairs_rem) > 10:
            try:
                stat_l2, p_l2 = wilcoxon([x[0] for x in level_pairs_rem], [x[1] for x in level_pairs_rem], alternative='greater')
                f.write(f"   Test Wilcoxon (Hook > Resto): p-value = {p_l2:.4f}\n")
                f.write(f"   RISULTATO: {'SIGNIFICATIVO (Livelli peggiori nel resto)' if p_l2 < 0.05 else 'NON SIGNIFICATIVO'}\n")
            except Exception as e:
                f.write(f"   Errore Test: {e}\n")

        # --- ANALISI CORRELAZIONE ---
        f.write("\n" + "="*80 + "\n")
        f.write("ANALISI 3: CORRELAZIONE LUNGHEZZA SESSIONE vs DELTA (Resto - Hook)\n")
        f.write("Obiettivo: Capire se il peggioramento (Delta negativo) aumenta con la durata della sessione.\n")
        f.write("-" * 80 + "\n")

        def write_corr_section(title, data):
            f.write(f"{title}\n")
            if len(data) < 5:
                f.write("   Dati insufficienti.\n\n")
                return
            
            lens = [x[0] for x in data]
            deltas = [x[1] for x in data]
            
            corr, p = spearmanr(lens, deltas)
            f.write(f"   Correlazione (Spearman): {corr:.4f}\n")
            f.write(f"   P-value:                 {p:.4f}\n")
            
            if p < 0.05:
                if corr < 0:
                    f.write("   RISULTATO: SIGNIFICATIVO NEGATIVO. Sessioni più lunghe -> Delta peggiore (più negativo).\n")
                    f.write("              (Il vantaggio iniziale svanisce di più o lo svantaggio aumenta nelle sessioni lunghe)\n")
                else:
                    f.write("   RISULTATO: SIGNIFICATIVO POSITIVO. Sessioni più lunghe -> Delta migliore.\n")
            else:
                f.write("   RISULTATO: NON SIGNIFICATIVO.\n")
            f.write("\n")

        write_corr_section("1. Lunghezza vs Delta Win Rate", corr_win)
        write_corr_section("2. Lunghezza vs Delta Matchup", corr_mu)
        write_corr_section("3. Lunghezza vs Delta Matchup No-Lvl", corr_munl)
        write_corr_section("4. Lunghezza vs Delta Level Diff", corr_lvl)

        f.write("="*80 + "\n")
