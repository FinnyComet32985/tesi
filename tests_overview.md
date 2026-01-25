# Panoramica e Metodologia dei Test Eseguiti

Questo documento descrive la suite di test statistici sviluppati per analizzare il matchmaking di Clash Royale, con l'obiettivo di identificare tracce di manipolazione (Rigged Matchmaking) o ottimizzazione dell'engagement (EOMM).

I test sono organizzati secondo un flusso logico che parte dalla verifica della fairness di base fino ad arrivare ad analisi comportamentali complesse.

---

## 1. Analisi di Fairness e Indipendenza di Base
*Obiettivo: Verificare se il matchmaking rispetta le regole dichiarate (casuale entro fasce di trofei).*

### 1.1 Test di Indipendenza Oraria
- **File**: `data/test_deck_analysis.py` (`analyze_nolvl_time_independence`)
- **Descrizione**: Verifica se la difficoltà dei matchup (calcolata oggettivamente senza livelli) varia in base all'orario di gioco (Notte vs Giorno).
- **Ipotesi Rigging**: Se un giocatore trova matchup peggiori in certe fasce orarie, potrebbe essere dovuto a pool di giocatori ridotti o pattern di "fasce orarie protette".
- **Risultato**: File `matchup_nolvl_time_results.txt`.

### 1.2 Analisi Saturazione Livelli
- **File**: `data/test_deck_analysis.py` (`analyze_level_saturation`)
- **Descrizione**: Analizza la varianza della differenza livelli al crescere dei trofei.
- **Obiettivo**: Confermare che a trofei alti la competizione sia "ad armi pari" (tutti maxati) e che eventuali discrepanze a trofei bassi siano naturali.
- **Risultato**: File `level_saturation_results.txt`.

### 1.3 Gatekeeping Analysis (Soglie Arena)
- **File**: `data/test_gatekeeping.py`
- **Descrizione**: Test di Mann-Whitney U per confrontare la difficoltà delle partite (Matchup e Livelli) quando un giocatore è vicino a salire di Arena (Danger Zone) rispetto a quando è "al sicuro".
- **Ipotesi Rigging**: Il "Gatekeeping" è una tecnica dove il sistema blocca artificialmente la progressione prima di un traguardo psicologico.
- **Risultato**: File `gatekeeping_results.txt`.

---

## 2. Analisi Deck-Based Matchmaking (Il Mazzo influenza l'Avversario?)
*Obiettivo: Verificare l'ipotesi centrale del "Rigged Matchmaking", ovvero che il mazzo utilizzato determini gli avversari incontrati.*

### 2.1 Fairness del Matchmaking (Chi-Quadro)
- **File**: `data/test_deck_analysis.py` (`analyze_matchmaking_fairness`)
- **Descrizione**: Test Chi-Quadro su tabelle di contingenza (Mazzo Giocatore vs Mazzo Avversario) per ogni fascia di trofei.
- **Ipotesi Rigging**: Se l'uso di un certo mazzo è statisticamente correlato a specifici archetipi avversari (p < 0.05), il matchmaking non è casuale ma condizionato dal mazzo.
- **Risultato**: File `matchmaking_fairness_results.txt`.

### 2.2 Analisi Deck Switch (Ipotetico vs Reale)
- **File**: `data/test_deck_analysis.py` (`analyze_deck_switch_hypothetical`)
- **Descrizione**: Quando un giocatore cambia mazzo, il test confronta:
    1. **Matchup Ipotetico**: Come il *nuovo* mazzo avrebbe performato contro i *vecchi* avversari.
    2. **Matchup Reale**: Come il *nuovo* mazzo performa contro i *nuovi* avversari.
- **Metrica Chiave**: "GAP". Se il Gap è negativo e ampio, significa che il sistema ha cambiato gli avversari per neutralizzare il vantaggio teorico del cambio mazzo.
- **Risultato**: File `deck_switch_hypothetical_results.txt`.

### 2.3 Analisi Matchup "Puri" (No-Level) vs Livelli
- **File**: `data/test_matchup_no_lvl.py`
- **Descrizione**: Isola l'impatto dei livelli delle carte dal vantaggio tattico (Counter). Verifica se esistono "Losing Streaks" anche eliminando il fattore livelli.
- **Ipotesi Rigging**: Se le serie di sconfitte persistono anche "ad armi pari", suggerisce un countering intenzionale algoritmico basato sulla composizione del mazzo.
- **Risultato**: File `matchup_no_lvl_results.txt`.

---

## 3. Analisi Targeting Specifico e "Sniping"
*Obiettivo: Rilevare casi specifici in cui mazzi vulnerabili vengono deliberatamente accoppiati contro i loro Hard Counter.*

### 3.1 Multi-Sniper Targeting
- **File**: `data/test_targeting.py` (`analyze_all_snipers_targeting`)
- **Descrizione**: Definisce coppie "Deck Vulnerabile" vs "Carta Sniper" (es. Golem vs Pekka). Calcola se i giocatori vulnerabili incontrano lo Sniper più spesso rispetto ai giocatori non vulnerabili.
- **Metrica**: "Lift" o Ratio (Frequenza su Vulnerabili / Frequenza su Safe). Un Ratio > 1.5x indica possibile targeting.
- **Risultato**: File `snipers_targeting_analysis.txt`.

### 3.2 Controllo Fattori Confondenti (Sniper)
- **File**: `data/test_targeting.py` (`analyze_sniper_confounding`)
- **Descrizione**: Verifica se le anomalie rilevate nel targeting sono spiegate da variabili esterne (es. giocare di notte quando il meta è diverso).
- **Risultato**: File `sniper_confounding_check.txt`.

### 3.3 Meta vs Counter (Popolarità o Targeting?)
- **File**: `data/test_deck_analysis.py` (`analyze_card_meta_vs_counter`)
- **Descrizione**: Analizza le carte che appaiono spesso nei matchup sfavorevoli. Distingue tra carte "Meta" (popolari ovunque) e carte "Killer" (iper-rappresentate solo contro chi counterano).
- **Risultato**: File `card_meta_vs_counter_results.txt`.

---

## 4. EOMM & Analisi Comportamentale
*Obiettivo: Identificare pattern di Engagement Optimized Matchmaking mirati a massimizzare la ritenzione tramite manipolazione emotiva.*

### 4.1 Session Trends (Hook & Frustration)
- **File**: `data/test_session_trend.py`
- **Descrizione**: Divide ogni sessione di gioco in due fasi: "Hook" (primi 3 match) e "Resto". Confronta Win Rate e Qualità del Matchup.
- **Ipotesi EOMM**: Le sessioni iniziano facili per ingaggiare il giocatore ("Hook") e diventano progressivamente più difficili per indurlo a spendere o a provare "ancora una partita".
- **Risultato**: File `session_trend_results.txt`.

### 4.2 Analisi Catene di Markov (Memoria del Sistema)
- **File**: `data/test_deck_analysis.py` (`analyze_nolvl_markov`)
- **Descrizione**: Modella la sequenza di matchup (Favorevole/Pari/Sfavorevole) come una catena di Markov per vedere se l'esito precedente influenza il successivo.
- **Ipotesi**: Una deviazione dalla distribuzione attesa suggerisce che il sistema "ricorda" la partita precedente per forzare una win-rate del 50%.
- **Risultato**: File `matchup_nolvl_markov_results.txt`.

### 4.3 Fisher Test su Matchup Estremi (Pity & Punish)
- **File**: `data/test_extreme_matchup.py`
- **Descrizione**: Usa il test esatto di Fisher per verificare se, dopo una streak di vittorie/sconfitte, la probabilità di un matchup "Estremo" (molto facile o molto difficile) cambia significativamente.
- **Obiettivo**: Identificare meccanismi di "Pity Match" (partita regalata per fermare l'abbandono) o "Punishment Match" (partita impossibile per frenare la salita).

### 4.4 Correlazione Odds Ratio vs Quit Rate (Behavioral Impact)
- **File**: `data/test_odds_and_quitrate_correlation.py`
- **Descrizione**: Correlazione di Spearman tra quanto un giocatore viene manipolato (Odds Ratio di Pity/Punish) e il suo comportamento di abbandono (Quit Rate, ERS - Early Return to Session).
- **Obiettivo Finale**: Dimostrare che la manipolazione (EOMM) ha un effetto reale sul comportamento del giocatore (es. "Se ti aiuto, torni prima a giocare?").

### 4.5 Indipendenza Streak vs Matchup
- **File**: `data/test_indipendenza.py`
- **Descrizione**: Test Chi-Quadro per verificare se lo stato attuale di Streak (Vincente/Perdente) è indipendente dalla difficoltà del prossimo matchup.

---

## Riepilogo Organizzazione per Tesi

In una tesi, questi test dovrebbero essere presentati nel seguente ordine logico:

1.  **Capitolo: Validazione Dataset e Fairness di Base**
    *   (Tests 1.1, 1.2, 1.3)
    *   Dimostrazione della qualità dei dati e verifica delle ipotesi nulle più semplici.

2.  **Capitolo: Analisi del Matchmaking Basato sul Mazzo**
    *   (Tests 2.1, 2.2, 3.1, 3.3)
    *   Il cuore dell'analisi tecnica sul "Rigged Matchmaking". Qui si presentano le prove forti (Chi-Quadro e Deck Switch).

3.  **Capitolo: Engagement Optimization (EOMM)**
    *   (Tests 4.1, 4.2, 4.3)
    *   Analisi temporale e sequenziale. Si passa dal "chi incontro" al "quando incontro chi".

4.  **Capitolo: Impatto Comportamentale**
    *   (Tests 4.4)
    *   Collegamento tra l'algoritmo (cause) e il giocatore (effetti), chiudendo il cerchio della tesi sulla psicologia del design.
