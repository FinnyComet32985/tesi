# Analisi EOMM

1. Test $\chi^2$ indipendenza

IPOTESI: il matchup della partita successiva dipende dalle streak

TEST: il test utilizzato è il $\chi^2$ che analizza il matchup della partita successiva (EVEN, FAV, UNFAV) per cercare una qualche tipo di dipendenza con la situazione precedente in termini di streak (NO STREAK, WINNING, LOSING)

RISULTATO 
ci sono **alcuni casi isolati** con dipendenza significativa, ma non abbastanza consistenti tra i player da suggerire un effetto sistematico ❌

1. EXACT FISCER SU MATCHUP ESTREMI

IPOTESI dopo una streak di vittorie/sconfitte la probabilità di trovare un martchup estremamente negativo/positivo cambia, significativamente?

TEST il test controlla la distribuzione dei matchup estremi e normali, comparandolo con la loro distribuzione dopo le streak

RISULTATO nessun risultato significativo ma varianza tra gli odds molto amplia ❌

1. CATENE DI MARKOV

IPOTESI il matchup della partita successiva è indipendente dal matchup della partita precedente

TEST modella una catena di MARKOV per vedere se il marchup precedente influenza quello successivo

RISULTATO  tutti i test eseguiti (matchup, levels, marchup no LVL) hanno risultare significativo ma nessuno sull'outcome della partita precedente

IMPLICAZIONE 
Le deviazioni rispetto all’indipendenza indicano che **la distribuzione dei matchup non è completamente memoryless**

POSSIBILI SPIEGAZIONI: META, TROFEI, POOL PLAYER ONLINE X FASCIA ORARIA

1. COSTRUZIONE FSI, IMPULSIVITÀ, ERS

IPOTESI      //

TEST la correlazione sperman cerca una correlazione tra due dati. in questo caso gli odds e le metriche

RISULTATO nessuna correlazione significativa

> nessuna correlazione tra i pity odds e il numero di partite del player
> 
> 
> correlazione tra pity odds e Trofei
> 

1. RITORNO DOPO UNA BAD STREAK

IPOTESI in un sistema EOMM like se un giocatore quitta dopo una streak di matchup sfavorevoli al ritorno dovrebbe avere un matchup favorevole

TEST se l'ultima sessione del player è finita con % matchup sfavorevoli, la prima partita della nuova sessione sarà ancora sfavorevole?

RISULTATO indipendentemente dal tempo passato il matchup al ritorno è peggiore di quando il player finisce la sessione non in una streak di matchup sfavorevoli ❌

1. SESSION PITY

IPOTESI in un matchmaking EOMM like se una sessione ha avuto un matchup medio sfavorevole quella successiva dovrebbe averne uno favorevole

TEST verificare se la sessione successiva ad una con un matchup mediamente sfavorevole diventa favorevole

RISULTATO nessuno dei test ha raggiunto la significatività ❌

1. ANALISI SEQUENZE KILLER

IPOTESI in un sistema di matchmaking basato sulla retention le sequenze che fanno quittare maggiormente i player dovrebbero apparire messo di quando ci aspetteremo

TEST cercare una correlazione spearman tra il rateo di apparizione di queste frequenze ( OSSERVATE / IPOTIZZATE) e la % quit rate (in che % dopo aver incontrato tale sequenza il player quitta)

RISULTATO la correlazione generale non è significativa ❌. Tuttavia, si nota un'anomalia nella sequenza **C-C-C** (3 Counter di fila), che appare con una frequenza doppia rispetto all'atteso (**Ratio 2.05x**).
> Questo fenomeno supporta l'ipotesi delle "Meta Windows": i counter non sono distribuiti uniformemente, ma arrivano a "ondate", rendendo più probabile incontrarne 3 di fila una volta entrati in una fascia ostile.

1. ANALISI EFFICIENZA POTENZIALE SISTEMA

IPOTESI la concessione dei pity match dovrebbe aumentare il coinvolgimento dei player

TEST sono stati testati gli eventi (lose, lose streak ≥ 2, lose streak ≥ 3, counter, counter streak ≥ 2 e counter streak ≥3) per vedere se quando ricevano un pity match hanno un allungamento della sessione, un ritorno medio più rapido o un minore rischio di quit > 3 giorni

RISULTATO nessun test ha raggiunto la significatività, ad eccezione del test  losing streak ≥3 e avg remaining matches. questo mostra che dopo una serie di lose ≥ 3, i player che ricevano un pity tendono a giocare una portata in più

# Analisi lamentele player

1. ANALISI COUNTER DI FILA

IPOTESI un sistema di matchmaking basato unicamente sui Trofei produrrebbe delle streak di matchup no lvl svantaggiosi/vantaggiosi più alta di un sistema deck-aware ma più bassa di matchup compresi di livelli

TEST abbiamo calcolato la probabilità di incontrare una streak, confrontandolo con un sistema indipendente, uno shuffle globale e uno intra-session

RISULTATI

> MATCHUP
> 
> 1.  MATCHUP STREAK >> TEORICO (INDIPENDENZA)
> 2.  //  > GLOBAL SHUFFLE
> 3. // $\approx$ INTRA SESSION SHUFFLE
> 
> (le streak si raggruppano in determinate sessioni)
> 
> LEVELS
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
> > 

1. DECK SWITCH

IPOTESI avendo un determinato pool di mazzi che ci countera, cambiando mazzo il pool di avversari dovrebbe rimanere uguale

TEST

- calcoliamo la variazione tra le varie possibilità per capire se la probabilità cambia drasticamente
- calcolando il matchup no LVL con il nuovo mazzo ma su quelli vecchi questo migliora? 
se si le nuove partite migliorano ugualmente?

RISULTATO analizzando tutti i deck switch sembra che la probabilità di permanenza in un matchup negativo si abbassi notevolmente, riportando il giocatore su matchup più neutrali.

⚠️ **Anomalia Livelli Post-Switch (Il "Costo di Cambio")**
Subito dopo il cambio mazzo (Match +1), il Level Diff crolla drasticamente a **-0.24** (svantaggio netto) contro una baseline di **+0.07**. L'effetto svanisce gradualmente nei match successivi (+2, +3).

> **PERCHÉ È SOSPETTO?**
> Supercell dichiara che il matchmaking considera **solo Trofei e Livello Torre del Re**, ignorando i livelli delle carte. Questo pattern contraddice le aspettative in due modi:
> 1. **Ipotesi "Innocente" (Livelli Bassi)**: Se il nuovo deck ha livelli più bassi del main, è normale partire con una diff negativa. Tuttavia, **senza un sistema che bilancia attivamente le carte**, non si spiega perché lo svantaggio sparisca progressivamente tornando verso lo zero nei match successivi.
> 2. **Ipotesi "Manipolazione"**: Il picco negativo immediato potrebbe essere una penalità intenzionale ("cooldown" allo switch) inserita dal sistema, che poi normalizza il matchup.

⚠️ Calcolando i matchup che il giocatore avrebbe avuto ipoteticamente con il nuovo mazzo sui player precedenti e confrontandolo con quelli che ha dopo rimane generalmente neutrale. se però prendiamo solo i cambi in cui i matchup ipotetici sono maggiori di quelli reali precedenti vediamo come i matchup successivi ritornano più equi. Tuttavia c’è una differenza del -2,6% con quelli ipotetici

IMPLICAZIONE

1. al contrario delle dichiarazioni i livelli sono in qualche modo presi in considerazione
2. anche se una volta cambiato il giocatore ottiene un vantaggio, questo è inferiore a quello ipotizzato. dopo il cambio deck il giocatore potrebbe essere messo in un pool di giocatori diversi?

1. GATEKEEPING

IPOTESI in un matchmaking non aware del deck o dei livelli i matchup che troviamo vicino alle nuove arene dovrebbero essere in linea con quelli precedenti

TEST abbiamo diviso i marchi in due gruppi: 

- zona safe
- zona danger (-50 Trofei all'obiettivo)

e abbiamo visto se il matchup, i livelli o i matchup no lvl sono sistematicamente più bassi

RISULTATO non sembrano esserci peggioramenti significativi (ad eccezione dei livelli)

(inizialmente solo i matchup no lvl)

1. GATEKEEPING AVANZATO

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

- Presenza di Meta Shock in diverse soglie (4200, 5000, 6000, 7000, 9000)
- Pattern di Gatekeeping evidenti a 6000, 7000, 10000, 11000
- Fenomeno "Relax Post-Gate" a 5500, 6500, 7000, 10000
- Delta Pre-Stable vs Post-Stable varia significativamente per soglia

1. COUNTER STREAK MANIPOLATION

IDEA in un sistema di matchmaking puramente basato sui trofei le streak dei matchup no lvl si dovrebbero distribuire in modo casuale

TEST capire se le bad streak di marchup no lvl si concentrano proprio quando ti trovi più in alto di trofei rispetto alla media delle tue ultime 200 portale

RISULTATO il Tempo che il giocatore passa Sopra alla media e dell' 88%. la probabilità di incappare in una serie di matchup negatavi è del 5% più grande quando sei sopra la media (circa +160 trofei)

1. SESSION TREND

IPOTESI in un sistema puramente basato sulla skill ci dovrebbe essere un maggiore winrate nelle prime partite della sessione (maggiore concentrazione) ma non a causa di matchup favorevoli

TEST il winrate è maggiore? i matchup sono migliori? player con sessioni più corre hanno matchup migliori?

RISULTATI sia il winrate che i matchup e i lvl sono migliori ma sessioni più corte non portano a matchup migliori, inoltre i matchup non diventano sempre peggio più è lunga la sessione

1. CONSISTENZA HOOK x TROFEI

IPOTESI l'hook è presente indipendentemente dai Trofei

TEST verificare se l' hook non dipende dai trofei

RISULTATI si, l' hook è quasi sempre presente ma varia abbastanza

1. DEBT/ CREDIT

IPOTESI in un gioco che non ha memoria dei matchup precedenti vincere o perdere un matchup estremo non dovrebbe influenzare il matchup successivo

TEST verificare se un matchup sfavorevole seguito da una vittoria porta ad un matchup ancora sfavorevole, confrontandolo con una sconfitta

RISULTATO vincere una partita sfavorevole porta ad un matchup ancora sfavorevole, perderla porla il matchup verso l'equità.

perdere una partita favorevole porta ad un matchup ancora favorevole, vincerla porta il matchup verso l'equità

in entrambi i casi la vittoria o la sconfitta sono dovuto all'elisir leaked dell'avversario (x la vittoria) o

del player (x la sconfitta)

POSSIBILI SPIEGAZIONI

il player è già a limite con i livelli, per cui trova il matchup sfavorevole. vincendo avrò avversari con livelli ancora maggiori e quindi un matchup peggiore

cambiano così tanto i livelli in 30 trofei? NO, LVL SATURATION e PAYWALL IMPACT 

cambio di meta? NO, META RANGE + MICRO META

1. DEBT / CREDIT ESTINOTION

IPOTESI perdere la partita sfavorevole combattendola o perdendo malamente non dovrebbe portare a differenze

TEST confrontare il matchup successivo a quello sfavorevole e capire se una sconfitta netta riporla più velocemente ad un matchup equo rispetto a una sconfitta combattuta

RISULTATO no, non sembra che perdere malamente la partita sfavorita porti a matchup più equo

rispetto a una sconfitta combattuta. anzi il contrario, sembra meglio una close loss

1. IL PLAYER INCONTRA PIÙ COUNTER

IPOTESI in un sistema deck aware un player dovrebbe incontrare più deck counter rispetto agli avversari

TEST 

- player che giocano nello stesso range di trofei, nella stessa fascia oraria e nella stessa nazione incontrano player con deck diversi?
- un player incontra più spesso counter rispetto a quando li incontrano gli averi player?

RISULTATO no, i player incontrano gli stessi deck e no, non incentrano i counter più spesso di chi non li soffre

1. QUANTO CONTANO I LVL E LA SKILL

IPOTESI 

- quanto influenzano i lvl il marchup?
- in un gioco equo la skill dovrebbe consentire al player di vincere nonostante i deficit di livelli o al matchup no LVL

TEST 

- testare la relazione tra LVL e matchup
- capire se la skill riveste un ruolo pesante nel winrate

RISULTATO 

- si, i livelli contano abbastanza nella determinazione del matchup composto
- avere una gestione dell'elisir migliore rispetto al tuo avversario ti porta generalmente vincere di più pur restando in svantaggio
    - winrate 46% con > skill
    - winrate 33 % con < skill
- avere un matchup migliore tende a dare un vantaggio notevole, anche giocando male
    - winrate 70% con > skill
    - winrate 64% con < skill

1. MATCHUP E STREAK DIPENDONO DALL’ORARIO

il matchup medio dipende dall’orario (probabilmente per il minor numero di player

il numero di streak dipende dall’orario ma le variazioni sono molto piccole

1. MATCHUP E STREAK DIPENDONO DAI TROFEI

si, sia il matchup medio che il numero di streak dipendono dai trofei 

1. META RANGES (FASCE META LOCALI)

IPOTESI Alcune fasce trofei potrebbero essere intrinsecamente più ostili a causa del meta locale.

TEST Distribuzione del matchup no-lvl per bucket da 200 trofei, Test Kruskal-Wallis tra fasce

**RISULTATO** differenze fortemente significative

**INTERPRETAZIONE**

Esistono vere e proprie **fasce meta difficili**, che possono spiegare molte bad streak senza bisogno di EOMM.

1. MICRO-META E TRANSIZIONI LOCALI

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

1. MATCHUP E STREAK DIPENDONO DAL MAZZO

no, non dipendono dal mazzo

1. IMPATTO CLIMBING

IPOTESI più sei in alto di trofei e peggiori sono le condizioni

TEST vedere se c'è una correlazione tra queste cose

RISULTATO si, salendo trovi generalmente condizioni peggiori ma non a tal punto da non permettere di salire

> confermato dal paywall impact
> 

1. PAYWALL IMPACT (Progressione Naturale vs Manipolazione)

**IPOTESI**

Se il sistema manipola i livelli in base alle vittorie, il level diff dovrebbe peggiorare dopo win e migliorare dopo loss nella stessa fascia trofei.

**TEST**

Confronto Level Diff post-win vs post-loss nello stesso bucket

**RISULTATO**

Delta ≈ 0 in quasi tutte le fasce

Solo rare anomalie non sistematiche

**CONCLUSIONE**

I livelli seguono una **progressione strutturale (paywall statico)**, non una manipolazione dinamica post-partita.

1.  LVL SATURATION

IPOTESI a Trofei alti i giocatori tendono ad essere maxati, per cui la varianza si abbassa

TEST verificare se la varianza tende ad abbassarsi, specialmente nelle ultime arene

RISULTATO non sembra esserci una relazione forte, ad eccezione delle ultime arene, come ipotizzato

inoltre  la varianza è generalmente bassa

> non spiega il debito
> 

la %  di 0 diff inoltre è generalmente alta 

> ma non a tal punto da spiegare completamente la mancanza di Double Whammy
> 

1. PUNISHMENT TRADE-OFF (NO DOUBLE WHAMMY)

**IPOTESI**

Il sistema evita di punire contemporaneamente con matchup sfavorevole *e* livelli sfavorevoli.

**TEST**

- Correlazione Spearman tra matchup no-lvl e level diff
- Confronto Double Whammy osservati vs attesi

**RISULTATO**

- Correlazione negativa significativa
- Double Whammy osservati = 0.72× attesi

**CONCLUSIONE**

Il sistema tende a distribuire lo svantaggio su un solo asse → comportamento più compatibile con matchmaking bilanciato che con EOMM punitivo

# conclusione

L’insieme dei test condotti sul matchmaking di Clash Royale non mostra evidenze compatibili con un sistema di tipo **EOMM (Engagement Optimized Matchmaking)**, ovvero un algoritmo progettato per manipolare attivamente l’esito delle partite al fine di controllare l’esperienza emotiva del giocatore (alternando vittorie e sconfitte in modo pilotato).

I risultati ottenuti indicano invece che i pattern osservati — streak, matchup estremi e variazioni nella difficoltà percepita — possono essere spiegati in modo coerente attraverso **fattori strutturali del sistema competitivo**, senza dover ricorrere a ipotesi di manipolazione dinamica.

### **1. Assenza di segnali di compensazione attiva (debito/credito)**

Se il sistema fosse EOMM, ci si aspetterebbe un chiaro effetto di **compensazione**:

- dopo una serie di sconfitte → aumento significativo di matchup favorevoli
- dopo una serie di vittorie → aumento di matchup sfavorevoli

I test sul “debito e credito” non mostrano questo comportamento.

Si osserva piuttosto una **regressione verso la media**, cioè un ritorno graduale alla distribuzione normale dei matchup, senza picchi anomali che indichino un intervento dell’algoritmo per “restituire” una vittoria o imporre una sconfitta.

Questo è compatibile con un sistema **statistico e non manipolativo**.

### **2. Aumento dei pity odds ai trofei alti: effetto strutturale, non artificiale**

La correlazione positiva tra pity odds e trofei, inizialmente controintuitiva, trova una spiegazione nella **struttura della ladder alta**:

- varianza dei livelli molto bassa
- skill dei giocatori simile
- meta stabile ma polarizzato (forti relazioni di counter tra archetipi)

In questo contesto, il risultato delle partite dipende molto più dal **matchup tra deck** che da errori o differenze di livello. Questo amplifica la probabilità di:

- matchup estremamente favorevoli
- matchup estremamente sfavorevoli
- streak naturali di vittorie o sconfitte

Si tratta quindi di un effetto **emergente dalla competitività del meta**, non di un intervento del sistema per creare difficoltà artificiali.

---

### **3. Percezione della “losing queue” e assenza di evidenze statistiche**

L’idea di una “losing queue” — una coda separata per i giocatori in losing streak — è diffusa nella community, ma:

- non esistono conferme ufficiali da parte di Supercell
- nei dati analizzati non emerge alcuna struttura compatibile con code distinte o con un algoritmo che modifica sistematicamente la difficoltà in base alle sconfitte recenti

Se una losing queue fosse attiva, si osserverebbero:

- forti dipendenze tra risultato precedente e difficoltà del matchup successivo
- distribuzioni dei matchup diverse dopo win streak e loss streak

Questi segnali non compaiono in modo statisticamente significativo.

---

### **4. Il sistema è “rigged”?**

Alla luce dei risultati, il matchmaking **non appare “rigged” nel senso di manipolare gli esiti per far perdere o vincere intenzionalmente un giocatore**.

Tuttavia, è corretto affermare che:

✔ Il sistema **decide contro chi si gioca**

✔ Ma lo fa principalmente sulla base di **trofei, disponibilità di giocatori e vincoli di matchmaking**, non sull’obiettivo di controllare l’esito emotivo delle partite

Le sensazioni di partite “impossibili” o “regalate” derivano in larga parte da:

- polarizzazione del meta
- natura ciclica dei counter tra archetipi
- riduzione della varianza ai trofei alti
- normale varianza statistica delle sequenze di eventi

---

## **Conclusione finale**

I pattern osservati nel matchmaking di Clash Royale sono compatibili con un sistema **competitivo basato su abbinamento per trofei e meta**, in cui le streak e i matchup estremi emergono come conseguenza della struttura del gioco e della distribuzione degli archetipi, non come risultato di una manipolazione dinamica dell’esperienza del giocatore.

In base alle evidenze raccolte, **non si può affermare che il sistema utilizzi un EOMM o una “losing queue” per pilotare vittorie e sconfitte**. Le fluttuazioni nella difficoltà percepita sono spiegabili attraverso dinamiche statistiche e strutturali tipiche degli ambienti competitivi ad alta ottimizzazione.

---