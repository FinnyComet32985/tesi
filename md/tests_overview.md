# Analisi EOMM

1. ## Test $\chi^2$ indipendenza

IPOTESI: il matchup della partita successiva dipende dalle streak precedenti

TEST: il test $\chi^2$ analizza il matchup della partita successiva (EVEN, FAV, UNFAV) per cercare una qualche tipo di dipendenza con la situazione precedente in termini di streak (NO STREAK, WINNING, LOSING)

RISULTATO 
Presenti **alcuni casi isolati** ma non consistenti tra i player → nessun effetto sistematico ❌

**ESECUZIONE**
`chi_square_independence_results.txt`

1. ## EXACT FISCER SU MATCHUP ESTREMI

IPOTESI dopo una streak di vittorie/sconfitte la probabilità di trovare un matchup estremamente negativo/positivo cambia, significativamente?

TEST il test controlla la distribuzione dei matchup estremi e normali, comparandolo con la loro distribuzione dopo le streak

RISULTATO nessun risultato significativo ma varianza tra gli odds molto amplia ❌

**ESECUZIONE**
`fisher_extreme_matchup_results.txt`

1. ## CATENE DI MARKOV

IPOTESI il matchup della partita successiva è indipendente dal matchup della partita precedente

TEST modella una catena di MARKOV per vedere se il matchup precedente influenza quello successivo

RISULTATO  
Dipendenza significativa tra matchup consecutivi (matchup, livelli, no-lvl)
❗ Nessuna dipendenza dall’outcome (win/loss)

IMPLICAZIONE 
Le deviazioni rispetto all’indipendenza indicano che **la distribuzione dei matchup non è completamente memoryless**

POSSIBILI SPIEGAZIONI: META, TROFEI, POOL PLAYER ATTIVI

**ESECUZIONE**
`markov_chains_results.txt`

1. ## COSTRUZIONE FSI, IMPULSIVITÀ, ERS

IPOTESI      //

TEST la correlazione sperman cerca una correlazione tra due dati. in questo caso gli odds e le metriche

RISULTATO nessuna correlazione significativa

> nessuna correlazione tra i pity odds e il numero di partite del player
> 
> 
> correlazione tra pity odds e Trofei
> 
> L’aumento dei pity odds ai trofei alti non indica aiuto artificiale, ma:
> * Varianza livelli ↓
> * Skill media ↑
> * Dipendenza dal matchup deck ↑
> ➡️ Più polarizzazione naturale → più matchup estremi
> Compatibile con ambiente competitivo più “skill-tight”, non con EOMM.

**ESECUZIONE**
`correlation_results.txt`
`quick_tests_results.txt`

1. ## RITORNO DOPO UNA BAD STREAK

IPOTESI in un sistema EOMM like se un giocatore quitta dopo una streak di matchup sfavorevoli al ritorno dovrebbe avere un matchup favorevole

TEST se l'ultima sessione del player è finita con % matchup sfavorevoli, la prima partita della nuova sessione sarà ancora sfavorevole?

RISULTATO 
il matchup al ritorno è peggiore quando il player finisce la sessione in una streak di matchup sfavorevoli 
indipendentemente dal tempo passato ❌

**ESECUZIONE**
`return_after_bad_streak_results.txt`

1. ## SESSION PITY

IPOTESI in un matchmaking EOMM like se una sessione ha avuto un matchup medio sfavorevole quella successiva dovrebbe averne uno favorevole

TEST verificare se ad una sessione con matchup mediamente sfavorevole ne sussegue una con un matchup mediamente favorevole

RISULTATO Sessioni negative non sono seguite da sessioni favorevoli ❌ 

**ESECUZIONE**
`session_pity_test_results.txt`

1. ## ANALISI SEQUENZE KILLER

IPOTESI in un sistema di matchmaking basato sulla retention le sequenze che fanno quittare maggiormente i player dovrebbero apparire meno spesso di quando ci aspetteremo

TEST cercare una correlazione spearman tra il rateo di apparizione di queste frequenze ( OSSERVATE / IPOTIZZATE) e la % quit rate (in che % dopo aver incontrato tale sequenza il player quitta)

RISULTATO 
la correlazione generale non è significativa ❌. 
Tuttavia, si nota un'anomalia nella sequenza **C-C-C** (3 Counter di fila), che appare con una frequenza doppia rispetto all'atteso (**Ratio 2.05x**).
> Questo fenomeno supporta l'ipotesi delle "Meta Windows": i counter non sono distribuiti uniformemente, ma arrivano a "ondate", rendendo più probabile incontrarne 3 di fila una volta entrati in una fascia ostile.

**ESECUZIONE**
`dangerous_sequences_results.txt`

1. ## ANALISI EFFICIENZA POTENZIALE SISTEMA

IPOTESI la concessione dei pity match dovrebbe aumentare il coinvolgimento dei player

TEST sono stati testati gli eventi (lose, lose streak ≥ 2, lose streak ≥ 3, counter, counter streak ≥ 2 e counter streak ≥3) per vedere se le sessioni che contengono uno di questi eventi susseguiti da un pity match sono più lunghe, favoriscono un ritorno medio più rapido o un minore rischio di quit > 3 giorni

RISULTATO nessun test ha raggiunto la significatività, ad eccezione del test losing streak ≥3 e avg remaining matches. 
dopo una serie di lose ≥ 3, i player che ricevono un pity tendono a giocare una partata in più

**ESECUZIONE**
`pity_impact_on_session_length.txt`
`pity_impact_on_return_time.txt`
`churn_probability_vs_pity_results.txt`

# Analisi lamentele player

1. ## ANALISI COUNTER STREAK

IPOTESI 
Se il matchmaking fosse basato unicamente sui Trofei, senza considerare direttamente mazzo o livelli carte, allora dovremmo osservare un comportamento intermedio tra:
* un sistema totalmente casuale (indipendenza statistica)
* un sistema fortemente deck-aware

In particolare:
| Tipo di streak |	Atteso in sistema solo-Trofei |
| --- | --- |
| Matchup (con livelli) | Più frequenti del modello teorico indipendente |
| Level Diff | Più frequenti del teorico |
| Matchup No-Lvl (solo deck) | Presenti ma meno eclatanti rispetto ai matchup completi |

TEST
Per ciascuna metrica abbiamo confrontato la frequenza osservata di streak (≥ 3 consecutivi) con tre modelli di riferimento:
* Modello Teorico Indipendente
  Eventi mescolati in modo completamente casuale.

* Global Shuffle
  Stessi valori globali ma ordine completamente rimescolato.

* Intra-Session Shuffle
  Mescolamento solo all’interno delle singole sessioni di gioco.


RISULTATI

> MATCHUP
> 
> 1.  MATCHUP STREAK >> TEORICO
> 2.  //  > GLOBAL SHUFFLE
> 3. // $\approx$ INTRA SESSION SHUFFLE
> 
> (le streak si raggruppano in determinate sessioni)
> 
> LEVEL DIFF
> 
> 1. LVL STREAK >> TEORICO (IND)
> 2. NORM LVL STR >> GLOBAL SHUFFLE
> 3. NORM LVL $\approx$  INTRA SESSION SHUFFLE
> 
> (le streak di NORM LVL si raggruppano nelle sessioni)
> 
> MATCHUP NO LVL
> 
> 1. MATCHUP NO LVL >> TEORICO (IND)
> 2. // < GLOBAL SHUFFLE
> 3. // < INTRA SESSION SHUFFLE
> 
> (l'ordine dei matchup puri è più casuale rispetto ad un ordine random puro)
> 
> > le streak si trovano in sessioni con caratteristiche particolari?


**ESECUZIONE**
`extreme_matchup_streak_results.txt`
`extreme_level_streak_results.txt`
`extreme_matchup_streak_no_lvl_results.txt`


1. ## DECK SWITCH

IPOTESI avendo un determinato pool di mazzi online (generalmente counter), cambiando mazzo il pool di avversari dovrebbe rimanere uguale

TEST

- calcoliamo la variazione tra le varie possibilità per capire se la probabilità cambia drasticamente
- calcolando il matchup no LVL con il nuovo mazzo ma su quelli vecchi questo migliora? 
se si le nuove partite migliorano ugualmente?

RISULTATO analizzando tutti i deck switch sembra che la probabilità di permanenza in un matchup negativo si abbassi notevolmente, riportando il giocatore su matchup più neutrali.

⚠️ **Anomalia Livelli Post-Switch (Il "Costo di Cambio")**
Subito dopo il cambio mazzo (Match +1), il Level Diff crolla drasticamente a **-0.24** (svantaggio netto) contro una baseline di **+0.07**. L'effetto svanisce gradualmente nei match successivi (+2, +3), pur rimanendo negativo.

> **PERCHÉ È SOSPETTO?**
> Supercell dichiara che il matchmaking considera **solo Trofei e Livello Torre del Re**, ignorando i livelli delle carte. Questo pattern contraddice le aspettative in due modi:
> 1. **Ipotesi "Innocente" (Livelli Bassi)**: Se il nuovo deck ha livelli più bassi del main, è normale partire con una diff negativa. Tuttavia, **senza un sistema che bilancia attivamente le carte**, non si spiega perché lo svantaggio sparisca progressivamente tornando verso lo zero nei match successivi.
> 2. **Ipotesi "Manipolazione"**: Il picco negativo immediato potrebbe essere una penalità intenzionale ("cooldown" allo switch) inserita dal sistema, che poi normalizza il matchup.

⚠️ Calcolando i matchup che il giocatore avrebbe avuto ipoteticamente con il nuovo mazzo sui player precedenti e confrontandolo con quelli che ha dopo rimane generalmente neutrale. 
se però prendiamo solo i cambi in cui i matchup ipotetici sono maggiori di quelli reali precedenti vediamo come i matchup successivi ritornano più equi. Tuttavia c’è una differenza del -2,6% con quelli ipotetici

IMPLICAZIONE

1. al contrario delle dichiarazioni i livelli sono in qualche modo presi in considerazione
2. anche se una volta cambiato il giocatore ottiene un vantaggio, questo è inferiore a quello ipotizzato. 
dopo il cambio deck il giocatore potrebbe essere messo in un pool di giocatori diversi?

**ESECUZIONE**
`deck_switch_impact.txt`
`deck_switch_hypothetical_results.txt`

1. ## GATEKEEPING

IPOTESI in un matchmaking non aware del deck o dei livelli i matchup che troviamo vicino alle nuove arene dovrebbero essere in linea con quelli precedenti

TEST abbiamo diviso i marchi in due gruppi: 

- zona safe
- zona danger (-50 Trofei all'obiettivo)

e abbiamo visto se il matchup, i livelli o i matchup no lvl sono sistematicamente più bassi

RISULTATO non sembrano esserci peggioramenti significativi (ad eccezione dei livelli)

(inizialmente solo i matchup no lvl)

**ESECUZIONE**
`gatekeeping_results.txt`

1. ## GATEKEEPING AVANZATO

**IPOTESI**

Se esiste un gatekeeping, l’ostilità del meta dovrebbe aumentare **prima o subito dopo** il superamento della soglia arena.

**TEST**

Analisi in 4 zone intorno alla soglia trofei:

- Pre-Stable
- Pre-Early (Danger Zone)
- Post-Early (Meta Shock)
- Post-Stable

Metrica: Hostility = Global Avg Matchup − Local Avg Matchup

RISULTATO

- Presenza di Meta Shock in diverse soglie (4200, 5000, 6000, 7000, 9000) (post early >> post stable)
- Pattern di Gatekeeping evidenti (6000, 7000, 10000, 11000) (pre-early con grande hostility > 1)
- Fenomeno "Relax Post-Gate" a 5500, 6500, 7000, 10000 (pre stable > post stable)
- Delta Pre-Stable vs Post-Stable varia significativamente per soglia

**ESECUZIONE**
`arena_gatekeeping_results.txt`

1. ## COUNTER STREAK MANIPOLATION

IDEA in un sistema di matchmaking puramente basato sui trofei le streak dei matchup no lvl si dovrebbero distribuire in modo casuale

TEST capire se le bad streak di matchup no lvl si concentrano proprio quando ti trovi più in alto di trofei rispetto alla media delle tue ultime 50 partite

RISULTATO entrambi i test non raggiungono la significatività

**ESECUZIONE**
`nolvl_streaks_vs_trophies_results.txt`

1. ## SESSION TREND

IPOTESI in un sistema puramente basato sulla skill ci dovrebbe essere un maggiore winrate nelle prime partite della sessione (maggiore concentrazione) ma non a causa di matchup favorevoli

TEST il winrate è maggiore? i matchup sono migliori? player con sessioni più corre hanno matchup migliori?

RISULTATI sia il winrate che il matchup e i lvl sono migliori ma sessioni più corte non portano a matchup migliori, inoltre i matchup non diventano sempre peggio più è lunga la sessione

**ESECUZIONE**
`session_trend_results.txt`

1. ## CONSISTENZA HOOK x TROFEI

IPOTESI l'hook è presente indipendentemente dai Trofei

TEST verificare se l'hook non dipende dai trofei

RISULTATI si, l'hook è quasi sempre presente ma varia abbastanza

**ESECUZIONE**
`hook_by_trophy_range_results.txt`

1. ## IL PLAYER INCONTRA PIÙ COUNTER

IPOTESI in un sistema deck aware un player dovrebbe incontrare più deck counter rispetto agli avversari

TEST 

- player che giocano nello stesso range di trofei, nella stessa fascia oraria e nella stessa nazione incontrano player con deck diversi?
- un player incontra più spesso counter rispetto a quando li incontrano gli averi player?

RISULTATO 
no, i player incontrano gli stessi deck e no, non incontrano i counter più spesso di chi non li soffre

**ESECUZIONE**
`matchmaking_fairness_results.txt`


# Analisi livelli, skill e componenti del matchup

1. ## QUANTO CONTANO I LVL E LA SKILL

IPOTESI 

- quanto influenzano i lvl il matchup?
- quanto influenzano i lvl il marchup?
- in un gioco equo la skill dovrebbe consentire al player di vincere nonostante i deficit di livelli o al matchup no LVL

TEST 
- testare la relazione tra LVL e matchup
- capire se la skill riveste un ruolo pesante nel winrate

RISULTATO 
- si, i livelli contano abbastanza nella determinazione del matchup composto
- avere una gestione dell'elisir migliore rispetto al tuo avversario ti porta generalmente a vincere di più, pur restando in svantaggio
    - winrate 46% con > skill
    - winrate 33 % con < skill
- avere un matchup migliore tende a dare un vantaggio notevole, anche giocando male
    - winrate 70% con > skill
    - winrate 64% con < skill

**ESECUZIONE**
`skill_vs_matchup_dominance.txt`

1. ## MATCHUP E STREAK DIPENDONO DALL’ORARIO

il matchup medio dipende dall’orario (probabilmente per il minor numero di player online) 
il numero di streak dipende dall’orario ma le variazioni sono molto piccole

1. ## MATCHUP E STREAK DIPENDONO DAI TROFEI

si, sia il matchup medio che il numero di streak dipendono dai trofei 

**ESECUZIONE**
`confounding_factors_results.txt`
`time_stats_results.txt`

1. META RANGES (FASCE META LOCALI)

IPOTESI Alcune fasce trofei potrebbero essere intrinsecamente più ostili a causa del meta locale.

TEST Distribuzione del matchup no-lvl per bucket da 200 trofei, Test Kruskal-Wallis tra fasce

**RISULTATO** differenze fortemente significative

**INTERPRETAZIONE**

Esistono vere e proprie **fasce meta difficili**, che possono spiegare molte bad streak senza bisogno di EOMM.

**ESECUZIONE**
`meta_ranges_results.txt`

1. ## MICRO-META E TRANSIZIONI LOCALI

**IPOTESI** Il meta non cambia solo su larga scala, ma anche localmente tra sotto-fasce.

**TEST**

- Bucket da 150 trofei
- Carte dominanti anomale (>2σ)
- Indice di transizione tra bucket
- Coefficiente di ostilità locale

**RISULTATO**

- Forti variazioni di carte dominanti tra bucket vicini
- Alcuni bucket mostrano meta temporaneamente più ostile, ma **non allineato con streak o churn**

**CONCLUSIONE**

Molte percezioni di “matchmaking contro di me” derivano da **micro-meta locali**, non da manipolazione attiva. Queste anomalie spiegano perché un mazzo che funziona a 5000 trofei smette di funzionare a 5150.

**ESECUZIONE**
`micro_meta_results.txt`

1. ## MATCHUP E STREAK DIPENDONO DAL MAZZO

no, non dipendono dal mazzo

**ESECUZIONE**
`confounding_factors_results.txt`

1. IMPATTO CLIMBING

IPOTESI più sei in alto di trofei e peggiori sono le condizioni

TEST vedere se c'è una correlazione tra queste cose

RISULTATO si, salendo trovi generalmente condizioni peggiori ma non a tal punto da non permettere di salire

> confermato dal paywall impact
> 

**ESECUZIONE**
`climbing_impact_results.txt`

1. ## PAYWALL IMPACT (Paywall Statico vs Dinamico)

**DOMANDA**
Il "muro" di livelli che impedisce di salire è una caratteristica strutturale del gioco (più sali, più trovi gente forte) o una punizione attiva che scatta dopo una vittoria?

**IPOTESI**
Se il sistema manipolasse attivamente le partite, dopo una vittoria dovrebbe assegnare un avversario con livelli significativamente più alti rispetto a dopo una sconfitta, *anche rimanendo nella stessa fascia di trofei*.

**TEST**
Questo test è cruciale per isolare la manipolazione dalla progressione naturale. Abbiamo confrontato il `Level Diff` medio dopo una vittoria e dopo una sconfitta, ma solo all'interno di **fasce di trofei ristrette (bucket)**. In questo modo, l'effetto del "climbing" viene neutralizzato.

**RISULTATO**
La differenza media di livelli tra post-vittoria e post-sconfitta è **praticamente zero** in tutte le fasce di trofei analizzate.

**CONCLUSIONE**
L'ipotesi del Paywall Dinamico è **smentita**. Il sistema non "punisce" una vittoria con un avversario di livello superiore. La difficoltà aumenta solo perché, vincendo, si sale di trofei e si accede a una fascia dove i livelli medi sono strutturalmente più alti. Il "muro" è una conseguenza della progressione (statico), non una reazione comportamentale del matchmaking (dinamico).

**ESECUZIONE**
`paywall_impact_results.txt`

1.  ## LVL SATURATION

IPOTESI a Trofei alti i giocatori tendono ad essere maxati, per cui la varianza si abbassa

TEST verificare se la varianza tende ad abbassarsi, specialmente nelle ultime arene

RISULTATO 
Non sembra esserci una relazione forte, ad eccezione delle ultime arene, come ipotizzato.

La varianza è generalmente bassa

La % di 0 diff inoltre è generalmente alta 

> ma non a tal punto da spiegare completamente la mancanza di Double Whammy
> 

**ESECUZIONE**
`level_saturation_results.txt`

1. ## PUNISHMENT TRADE-OFF (NO DOUBLE WHAMMY)

**IPOTESI**

Il sistema evita di punire contemporaneamente con matchup sfavorevole e livelli sfavorevoli.

**TEST**

- Correlazione Spearman tra matchup no-lvl e level diff
- Confronto Double Whammy osservati vs attesi

**RISULTATO**

- Correlazione negativa significativa
- Double Whammy osservati = 0.72× attesi

**CONCLUSIONE**

Il sistema tende a distribuire lo svantaggio su un solo asse → comportamento più compatibile con matchmaking bilanciato che con EOMM punitivo

**ESECUZIONE**
`punishment_tradeoff_results.txt`

# fattori nascosti

1. ## DEBT / CREDIT

**IPOTESI**
In un sistema senza memoria, l'esito di una partita (vittoria o sconfitta) in condizioni sfavorevoli non dovrebbe influenzare la difficoltà della partita successiva.

**TEST**
Confronta la difficoltà del match successivo (Matchup, Level Diff, Matchup No-Lvl) dopo aver **vinto** un matchup sfavorevole (<45%) rispetto a dopo averlo **perso**.

**RISULTATO**
- **Vincere** una partita sfavorevole porta a un **matchup successivo peggiore** rispetto a perderla.
- L'analisi delle componenti rivela che questo peggioramento è quasi interamente dovuto a un **peggioramento del Level Diff** (avversari con livelli più alti).
- Il matchup puro (No-Lvl, basato solo sui mazzi) non cambia in modo significativo.

**POSSIBILI SPIEGAZIONI E ANALISI DI ESCLUSIONE**

1. #### CAMBIO META RAPIDO
    Dai test precedenti sappiamo che:
    * META RANGES → alcune fasce di 200 trofei hanno matchup medi molto diversi (Kruskal-Wallis) significativo
    * MICRO META → anche in bucket da 150 trofei compaiono carte dominanti anomale (>2σ)
    
    L’indice di transizione mostra che il meta può cambiare anche bruscamente tra bucket adiacenti
    
    Quindi era assolutamente plausibile che:
    > Dopo una vittoria o sconfitta, lo spostamento di trofei potesse far entrare il player in un micro-meta diverso, spiegando il cambio di difficoltà.

    Perché non spiega il risultato Debt/Credit
    Nel test Debt/Credit:
    * Le partite confrontate sono consecutive
    * Delta trofei medio ≈ 30
    * Questo spostamento è molto inferiore ai bucket dove osserviamo veri cambi meta (150–200 trofei)

    Inoltre:
    * Il cambiamento osservato è forte nel Level Diff
    * Ma debole o non significativo nel Matchup No-Lvl

    Se fosse un cambio meta:

    | Variabile | Dovrebbe cambiare | Osservato |
    | :-- | :-- | :-- |
    | Matchup No-Lvl |	✔️ SÌ	| ❌ Debole |
    | Level Diff | ❌ Non necessariamente | ✔️ Forte |

    *Il pattern osservato è incoerente con un semplice cambio meta*


2. #### FATTORI TEMPORALI (ORARIO / POOL ATTIVI)
    Dai test sui fattori confondenti sappiamo che:
    * Il matchup medio varia con l’orario
    * Anche il Level Diff medio cambia a seconda della fascia oraria
    * Questo è coerente con pool di giocatori diversi (casual vs hardcore)
    
    Quindi era plausibile che:
    > Dopo una partita, il cambio orario o di pool potesse spiegare il cambiamento nel matchup.

    Perché non spiega il risultato
    Nel Debt/Credit:
    * Le partite analizzate sono intra-sessione
    * Delta time < 20 minuti
    
    In 20 minuti:
    * Il pool attivo non cambia in modo drastico
    * I test sugli orari mostrano differenze tra fasce orarie ampie, non su finestre così brevi

    Inoltre:
    * I fattori temporali influenzano matchup e livelli in modo simile
    * Nel Debt/Credit vediamo un effetto molto più forte sui livelli
    
    *L’effetto temporale è troppo lento e troppo simmetrico per spiegare il pattern osservato*

3. #### CLIMBING IMPACT (EFFETTO SALITA TROFEI)
    Dai test:
    * Il matchup medio peggiora salendo di trofei
    * Il Level Diff tende a diventare più negativo
    * Il Paywall Impact mostra che la progressione livelli crea svantaggi crescenti
    
    Quindi era logico pensare:
    > Dopo una vittoria, salendo di trofei, il sistema trovi avversari con livelli più alti.

    Perché non basta a spiegare il fenomeno
    Abbiamo confrontato:
    * Delta Level Diff osservato post-match
    * Delta atteso dalla regressione Level Diff vs Trofei

    Risultato:
    * Il climbing spiega una frazione minima dell’effetto osservato (≈ 2–3%)
    
    Inoltre:
    * La varianza livelli è bassa
    * La % di 0 diff è alta
    * Salire di 30 trofei non sposta abbastanza la distribuzione

    *Il climbing contribuisce, ma non può generare variazioni così brusche tra due partite consecutive*

4. #### LVL SATURATION (POOL PIÙ MAXATI)
    Ai trofei alti:
    * I giocatori tendono a essere più maxati
    * La distribuzione livelli è più compressa
    * Questo può cambiare la probabilità di incontrare svantaggi

    Perché non basta
    La saturazione:
    * È un fenomeno graduale
    * Non cambia drasticamente tra due partite consecutive
    * Non spiega perché il cambio avvenga subito dopo uno specifico esito


**IMPLICAZIONE FINALE**

Poiché le spiegazioni strutturali e statistiche vengono escluse dai test, l'ipotesi più plausibile è l'esistenza di un **meccanismo di matchmaking nascosto** che tiene traccia delle vittorie "contro pronostico" e le "punisce" nella partita successiva aumentando la difficoltà tramite i livelli delle carte avversarie (un "debito" di MMR/rating).

**ESECUZIONE**
`debt_credit_combined_results.txt`

2. ### QUALITÀ DELLA SCONFITTA (DEFEAT QUALITY)

**IPOTESI**
Il modo in cui si perde influenza la reazione del sistema. Una sconfitta netta e frustrante (0-3) dovrebbe attivare un meccanismo di "pity" (compassione) più forte rispetto a una sconfitta combattuta.

**TEST**
Confronta il matchup della partita successiva dopo una sconfitta "Crushing" (0-3) rispetto a una "Close" (differenza di 1 corona).

**RISULTATO**
L'ipotesi è **smentita**. Una sconfitta 0-3 porta a un **matchup successivo peggiore** (48.07%) rispetto a una sconfitta combattuta (50.66%).
Il Delta è -2.60%.

**IMPLICAZIONE**
Non esiste un meccanismo di "Pity" basato sulla gravità della sconfitta. Farsi "asfaltare" non garantisce aiuti; al contrario, il sistema sembra ignorare la frustrazione derivante dal punteggio, o addirittura penalizzare ulteriormente (forse interpretando il 0-3 come gap di skill non colmato).

**ESECUZIONE**
`defeat_quality_impact_results.txt`


---



## CONCLUSIONI GENERALI

L’insieme dei test condotti permette di distinguere in modo piuttosto netto tra:

percezioni soggettive dei giocatori

fenomeni strutturali del meta e della progressione

possibili dinamiche nascoste del sistema di matchmaking

L’analisi non supporta l’idea di un sistema EOMM classico orientato alla retention emotiva nel breve periodo, ma evidenzia comunque che il matchmaking osservato è più complesso e meno “memoryless” di quanto dichiarato ufficialmente.

❌ Assenza di prove a favore di un EOMM “classico”

I test tipici per individuare un sistema orientato alla retention (streak break, pity post-quit, compensazioni tra sessioni, riduzione delle sequenze frustranti, aumento engagement dopo pity) mostrano risultati coerenti:

Nessuna compensazione sistematica dopo losing streak

Nessun miglioramento al ritorno dopo una sessione negativa

Nessuna riduzione delle sequenze che causano più quit

Nessun effetto consistente dei pity sull’allungamento delle sessioni o sul ritorno

👉 Non emerge un sistema che “aggiusta” le partite per trattenere attivamente il giocatore nel breve periodo.

Il comportamento osservato è molto più vicino a un sistema strutturale e statistico che a un controllo dinamico dell’esperienza emotiva.

⚙️ Molti fenomeni percepiti come “rigging” sono spiegabili senza EOMM

Diversi risultati mostrano che molte lamentele dei player hanno basi reali, ma cause strutturali:

🔹 Meta Ranges e Micro-Meta

Il meta cambia in modo significativo tra fasce di trofei anche vicine.
Questo crea:

zone naturalmente più ostili a certi mazzi

ondate di counter

streak di matchup negativi senza alcuna manipolazione

🔹 Climbing Impact

Salendo di trofei:

aumentano skill media e livelli medi

aumenta la dipendenza dal matchup

peggiorano le condizioni medie

Questo genera la sensazione di “il gioco mi blocca”, ma è una conseguenza della progressione, non una punizione dinamica.

🔹 Punishment Trade-Off (No Double Whammy)

Il sistema tende a non combinare contemporaneamente matchup e livelli sfavorevoli.
Questo comportamento è più compatibile con un matchmaking bilanciato che con un sistema punitivo.

⚠️ Il sistema NON è completamente memoryless

I test sulle catene di Markov e sulle streak mostrano che:

I matchup consecutivi non sono completamente indipendenti

Le streak si concentrano in specifiche sessioni

Esistono “finestre meta” dove certe condizioni persistono

Questo indica che il matchmaking reale:

non è puro random

non è solo funzione dei trofei istantanei

risente della struttura del pool di giocatori attivi e della segmentazione del meta

👉 È un sistema strutturato e segmentato, ma non necessariamente orientato alla manipolazione emotiva.

🔍 L’anomalia principale: Debt / Credit

Il test Debt/Credit è l’unico che mostra un pattern coerente, significativo e difficile da spiegare solo con fattori noti:

Vincere un matchup sfavorevole → partita successiva con livelli peggiori

Perdere un matchup sfavorevole → partita successiva più neutra

Effetto concentrato sui livelli, non sui matchup puri

Magnitudine non spiegabile da:

climbing naturale

meta shift

orario

varianza livelli

regressione verso la media (spiega la direzione, non l’ampiezza)

Questo non prova un EOMM, ma suggerisce che il sistema:

non sia basato unicamente su trofei e livello del Re, come dichiarato.

La spiegazione più prudente è l’esistenza di una variabile di rating o segmentazione nascosta che influenza indirettamente la distribuzione dei livelli degli avversari.

🎯 Conclusione Finale

Dai dati emerge che:

✔ Il matchmaking non mostra comportamenti tipici di un EOMM orientato alla retention emotiva
✔ Molte percezioni di “gioco contro il giocatore” derivano da meta locali, progressione strutturale e segmentazione del pool
✔ Il sistema appare progettato per mantenere una certa equità strutturale (no double whammy)

MA

⚠️ Non è compatibile con un modello puramente basato su trofei e livello torre, poiché:

esiste memoria statistica tra match consecutivi

esistono variazioni nei livelli avversari non spiegabili dal solo climbing

il fenomeno Debt/Credit indica una struttura di rating o pooling non osservabile direttamente