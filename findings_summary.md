# Sintesi dei Risultati e Scoperte

## 1. EOMM (Engagement Optimized Matchmaking)
- **Smentito**: I test di indipendenza (Chi-Quadro, Markov su Win/Loss) non mostrano pattern sistematici di manipolazione dell'esito (es. forzare una vittoria dopo una sconfitta per retention). Il sistema non sembra "aggiustare" le partite basandosi sulla storia recente di vittorie/sconfitte per massimizzare il tempo di gioco nel breve termine.
**File Report**: `chi_square_independence_results.txt`, `markov_chains_results.txt`

## 2. Analisi Lamentele Giocatori
- **"Incontro troppi counter di fila"**: 
  - **Corretto** rispetto a un modello teorico di indipendenza pura, ma **coerente** con simulazioni di shuffle (Global e Intra-Session). Le sequenze di counter (es. 3 di fila) accadono, ma sembrano dovute alla varianza naturale e alla concentrazione di certi mazzi in specifiche fasce di trofei (Meta Ranges), non a un targeting intenzionale del giocatore.
  **File Report**: `extreme_matchup_streak_results.txt`
  
- **"Gatekeeping (Il gioco mi blocca prima dell'arena successiva)"**:
  - **Vero per i Livelli**: Nella "Danger Zone" (vicino alla promozione) i livelli avversari sono significativamente più alti.
  - **Falso per il Matchup**: Non c'è evidenza consistente che il sistema assegni counter specifici alle soglie delle arene.
  - **Conclusione**: Probabilmente un effetto strutturale (i giocatori bloccati alle soglie sono quelli con livelli alti ma skill bassa) piuttosto che un sistema intenzionale.
  **File Report**: `arena_gatekeeping_results.txt`, `level_saturation_results.txt`

- **"Il sistema guarda il mio mazzo (Deck Aware)"**:
  - **Smentito** dal test Matchmaking Fairness: La distribuzione degli archetipi avversari risulta statisticamente indipendente dal mazzo usato dal giocatore (a parità di trofei e orario).
  - *Nota*: Il test "Session Swap" ha mostrato anomalie in casi specifici, ma su un campione troppo ristretto per ribaltare il risultato generale.
  **File Report**: `matchmaking_fairness_results.txt`, `session_swap_ladder_results.txt`

- **"Il gioco decide quando devo vincere"**:
  - **No**, questo bias è spiegabile con fattori esterni. Il meta cambia drasticamente in base all'**Orario** (pool giocatori diversi) e ai **Trofei** (Meta Ranges). Salendo di trofei, le condizioni peggiorano naturalmente (Climbing Impact), creando l'illusione di un sistema che "chiude i rubinetti".
  **File Report**: `meta_ranges_results.txt`, `climbing_impact_results.txt`

- **"La Skill conta meno dei Livelli/Matchup"**:
  - **Vero**: L'analisi mostra che i livelli e il matchup hanno un peso preponderante sull'esito.
  - **Dati**: Giocare meglio dell'avversario (efficienza elisir) in un matchup sfavorevole porta a un Win Rate basso (~46%). Al contrario, avere un matchup favorevole garantisce un Win Rate alto (~64%) anche giocando peggio.
  - **Conclusione**: La skill mitiga lo svantaggio ma spesso non è sufficiente a ribaltare un gap strutturale (Counter o Livelli).
  **File Report**: `skill_vs_matchup_dominance.txt`

## 3. Scoperta Principale: Il "Debito" (Hidden MMR)
L'evidenza più forte trovata suggerisce che il matchmaking **non si basa solo su Trofei e Livello Torre** (come dichiarato ufficialmente), ma utilizza un parametro nascosto (MMR latente o "Debito") per bilanciare le partite.

**La Prova (Test Debt/Credit):**
Quando un giocatore si trova in una situazione di "Debito" (Matchup Sfavorevole < 45%):
- Se **VINCE** (esito inatteso / "contro pronostico"):
  - La partita successiva presenta avversari con **Livelli Carte significativamente più alti**.
  - Il sistema sembra "punire" la vittoria inattesa o "alzare l'asticella" immediatamente.
- Se **PERDE** (esito atteso):
  - La partita successiva presenta livelli normali o più bassi (il debito è "pagato").
**File Report**: `debt_credit_combined_results.txt`

## 4. Validazione della Scoperta (Esclusione Fattori Confondenti)
Per confermare che il fenomeno del "Debito" sia una manipolazione attiva e non un effetto collaterale, abbiamo escluso le altre cause possibili:

1.  **Fattore Tempo e Regione (Escluso)**:
    - I match analizzati sono **consecutivi nella stessa sessione** (< 20 minuti di differenza).
    - L'orario e la regione sono identici, quindi il pool di giocatori non cambia drasticamente.

2.  **Fattore Meta/Deck (Escluso)**:
    - Il **Matchup No-Lvl** (basato solo sugli archetipi) **non cambia significativamente** dopo la vittoria in debito (p-value > 0.05).
    - Questo indica che il sistema non sta cambiando il tipo di mazzo avversario (non è un cambio di meta locale), ma sta agendo specificamente sui **Livelli**.
    **File Report**: `debt_credit_combined_results.txt`

3.  **Fattore Climbing/Progressione (Escluso)**:
    - **Test Paywall Impact**: Confrontando match nello stesso range di trofei, la differenza di livelli dopo una vittoria o una sconfitta è nulla (Delta ~ 0). Questo prova che la progressione naturale non punisce la vittoria.
    - **Test Climbing Impact**: Sebbene salire di trofei porti a livelli più alti, questo è un processo graduale e lineare, non spiega il picco improvviso osservato solo dopo le vittorie "in debito".
    - **Test Residual Level Diff**: Anche normalizzando per la fascia di trofei (calcolando lo scostamento dalla media locale), chi vince in debito riceve avversari con livelli significativamente peggiori rispetto a chi perde (-0.21 vs -0.11, p < 0.001). Questo conferma matematicamente che la "punizione" è attiva e non è un semplice artefatto statistico della salita in classifica.
    **File Report**: `paywall_impact_results.txt`, `climbing_impact_results.txt`, `residual_level_diff_debt_results.txt`

4.  **Fattore Saturazione (Escluso)**:
    - L'analisi della saturazione mostra che, sebbene a trofei alti la varianza diminuisca, la percentuale di match con **differenza di livello pari a 0** è relativamente bassa (~10%).
    - Questo significa che nel ~90% dei casi esiste un divario di livelli, lasciando al sistema ampio margine per manipolare la difficoltà scegliendo avversari più o meno livellati.
    **File Report**: `level_saturation_results.txt`

## 5. Rilettura delle Lamentele alla luce dell'MMR (La "Nuova Verità")
Alla luce della scoperta del meccanismo di **Debito/Credito (Hidden MMR)**, possiamo reinterpretare le lamentele iniziali (Sezione 2) che sembravano smentite o spiegate da fattori esterni.

- **"Il gioco decide quando devo vincere"**:
  - **Analisi Iniziale**: Sembrava un bias cognitivo o effetto del Meta/Orario.
  - **Nuova Interpretazione**: È l'effetto della **Correzione dell'MMR**. Se vinci troppo ("sopra le righe"), il tuo MMR sale e il sistema ti assegna avversari "impossibili" (Debito) per riportarti al tuo livello previsto. La sensazione che il gioco "chiuda i rubinetti" è reale: è il sistema che frena la tua ascesa perché il tuo MMR (Skill) ha superato i tuoi Livelli Carte.

- **"Gatekeeping"**:
  - **Analisi Iniziale**: Effetto strutturale (livelli alti si accumulano alle soglie).
  - **Nuova Interpretazione (La Trappola dell'MMR)**: Arrivando alla soglia vincendo, il tuo MMR è alto. Il sistema ti abbina ad altri con MMR alto in quella fascia. A quei trofei, gli unici con MMR alto che non sono ancora saliti sono i "Guardiani" (livelli maxati, skill bassa). Il sistema ti blocca "equamente" basandosi sulla tua skill.

- **"Incontro troppi counter"**:
  - **Analisi Iniziale**: Varianza statistica e Meta Ranges.
  - **Nuova Interpretazione**: Se il tuo MMR è alto, incontri mazzi Meta (più forti/ottimizzati). Se usi un mazzo "fatto in casa", i mazzi Meta sembrano tutti counter. Non è il sistema che sceglie il counter specifico, è il sistema che sceglie avversari forti (che usano mazzi forti).

---
**Conclusione Finale**:
Il sistema non sembra manipolare l'esito tramite counter-picking (EOMM classico sui deck), ma utilizza i **Livelli delle Carte** come leva di bilanciamento dinamico (Hidden MMR). Se performi sopra le aspettative (vinci match difficili), il sistema ti assegna avversari con livelli più alti nella partita subito successiva, indipendentemente dalla tua fascia di trofei.
