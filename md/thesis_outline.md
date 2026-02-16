# Matchmaking nei videogiochi multiplayer: analisi statistica tramite reverse engineering e confronto con le dichiarazioni dei publisher

## **Introduzione**

### Contesto generale

- crescente rilevanza dei giochi multiplayer competitivi nel settore videoludico
- ruolo del matchmaking nel garantire:
    - equità percepita tra i giocatori
    - retention dei player
    - sostenibilità dei modelli economici free-to-play

### Problema

- Le aziende descrivono il matchmaking come un sistema basato principalmente su indicatori di progressione (es. trofei, livello)
- Una parte della community percepisce comportamenti più complessi o non pienamente spiegabili con i soli criteri dichiarati

### Obiettivo

- Analizzare empiricamente il funzionamento del matchmaking attraverso metodi statistici
- Verificare se il comportamento osservabile del sistema sia coerente con le dichiarazioni ufficiali dei publisher
- Individuare eventuali discrepanze tra modello dichiarato e dinamiche effettivamente riscontrabili nei dati di gioco

---

## Stato dell’Arte

### Cos’è il matchmaking

*(definizione formale)*

### Tipologie di matchmaking

*(in breve vista la grandezza della letteratura a riguardo)*

### Ping Based Matchmaking

Accoppia i giocatori principalmente in base alla qualità della connessione (latenza).

È tipico dei giochi dove la reattività è prioritaria (es. FPS competitivi).

### RBMM (Rank Based Matchmaking)

Utilizza un indicatore di progressione **visibile** (es. trofei, rank, lega) per abbinare i giocatori.

La skill è considerata solo indirettamente, assumendo che il livello di progressione rifletta l’abilità del giocatore.

*(Questo è il modello che, secondo le dichiarazioni ufficiali, dovrebbe essere predominante nel caso studio analizzato.)*

### SBMM (Skill Based Matchmaking)

Lo **Skill Based Matchmaking (SBMM)** è un **modello teorico** in cui i giocatori vengono accoppiati in base a una stima numerica della loro abilità (MMR).

Alcune sue implementazioni spesso utilizzate sono:

- **Elo** – aggiorna il rating solo in base a vittoria/sconfitta
- **Glicko / Glicko-2** – introduce RD e volatilità
- **TrueSkill** – modello probabilistico usato in alcuni giochi multiplayer

In particolare il gliko *(quello che risulta compatibile con i risultati delle nostre analisi)* utilizza:

- **Rating (MMR)** → stima numerica della skill
- **Rating Deviation (RD)**
    
    *misura quanto il sistema è incerto su quella stima: RD alto = sistema poco sicuro della tua skill*
    
- **Volatilità**
    
    *misura quanto le prestazioni del giocatore sono variabili e imprevedibili nel tempo*
    

Questi parametri rendono il matchmaking **reattivo alla performance recente**.

### EOMM (Engagement Optimized Matchmaking) *(ipotesi teorica)*

Ottimizza il coinvolgimento stimando la probabilità di abbandono del giocatore.

---

### Letteratura esistente

1. **Progettazione di algoritmi** (Elo, TrueSkill, EOMM…)
2. **Esperienza del giocatore**
    
    Studi che analizzano come diversi sistemi di matchmaking influenzano:
    
    - fairness percepita
    - frustrazione
    - abbandono del gioco (churn)
    
    *Questi lavori confrontano diversi modelli di matchmaking e misurano come i giocatori percepiscono l’equità delle partite e quanto questo incida sulla loro permanenza nel gioco.*
    
3. **Discussioni non accademiche** su possibili manipolazioni

**Gap:**

Nessuna ricerca verifica empiricamente la coerenza tra dichiarazioni ufficiali dei publisher e comportamento reale del sistema.

---

## Metodologia di Reverse Engineering Statistico

### Difficoltà

- Codice server non accessibile
- Variabili nascoste
- Presenza di rumore elevato

### Strategia

- Raccolta dati da match reali
- Controllo variabili osservabili:
    - trofei
    - livelli carte
    - composizione mazzo
- Confronto tra:
    - modello dichiarato
    - pattern osservati nei dati

---

## Caso Studio: Clash Royale

### Perché Clash Royale?

- Gioco PvP molto diffuso
- Strategico, basato su mazzi di carte scelti **prima** del matchmaking
- Presenza di dichiarazioni ufficiali dettagliate sul matchmaking
- Accesso a:
    - storico partite
    - trofei
    - livelli carte
    - mazzi utilizzati

---

## Raccolta dei dati

L'analisi si basa su un dataset costruito monitorando un campione di giocatori reali attraverso portali pubblici di statistiche (RoyaleAPI).

1. **Crawler e Parsing**:
    - Sviluppo di un software dedicato per l'estrazione periodica e incrementale dei battle log.
    - Parsing delle pagine HTML per estrarre in modo strutturato le informazioni rilevanti
2. **Arricchimento tramite API Esterne**:
    - Integrazione con un servizio esterno di simulazione (**DeckAI**) per stimare l’esito teorico di ogni singolo scontro.
    - Generazione delle probabilità di vittoria ex-ante per ogni coppia di mazzi registrata.

Il dataset finale, salvato in un db sqlite, comprende:

- **40 giocatori**
- **~8700 partite totali**

### Dati raccolti

- Trofei giocatore
- Mazzo utilizzato
- Livelli carte di entrambi i giocatori
- **lvl diff**
    
    *differenza tra il livello medio delle carte dell’avversario e quello del giocatore.*
    
    *Valore positivo = avversario con carte mediamente più forti.*
    
    *Questa misura **non include** il livello delle torri, che è stato analizzato separatamente.*
    
- Matchup (probabilità teorica di vittoria considerando carte + livelli)
- Matchup no-lvl (probabilità basata solo sulle carte)
- **Elisir sprecato**
    
    *unico indicatore usato per stimare la qualità della gestione della partita: meno elisir sprecato → gioco più efficiente*
    

---

# Analisi statistiche

## 1️⃣ Il matchmaking considera i mazzi?

Dichiarazione ufficiale: le carte non vengono considerate.

### Test 1 — Dipendenza temporale

Analisi catene di Markov sul **matchup no-lvl**

→ Il matchup no-lvl successivo dipende da quello precedente

### Possibili cause strutturali

- **Meta**
    
    *insieme di carte/strategie statisticamente più forti e quindi molto usate in un certo periodo o fascia trofei*
    
- Cambi di meta tra fasce di trofei
- Dipendenza dall’orario
    
    *in orari diversi giocano gruppi di utenti diversi con preferenze di mazzo differenti*
    

### Test 2 — Controllo per fattori esterni

Per verificare che la dipendenza fosse effettivamente spiegabile da questi fattori abbiamo segmentato i matchup no lvl per:

- fascia trofei
- fascia oraria

risultati: 

- in diverse fasce di trofei troviamo carte utilizzate generalmente molto diverse
- il matchup no lvl nella maggior parte delle fasce di trofei varia significativamente in base all’orario

### Test dipendenza mazzi

Confronto tra partite:

- nella stessa fascia trofei
- in orari simili

Se il sistema scegliesse attivamente i mazzi avversari in base al nostro, dovremmo osservare un’associazione diretta tra i due.

**Risultato:** questa associazione non è stata trovata in modo significativo.

➡ Il sistema **non sembra manipolare direttamente i mazzi avversari**.

---

## 2️⃣ Il matchmaking considera i livelli delle carte?

Analisi della dipendenza tra **lvl diff** consecutivi.

Risultato: esiste correlazione.

### Controlli

- Correlazione trofei ↔ livelli: molto forte
- Dipendenza livelli ↔ orario: non significativa
- Livello torri ↔ livello carte: forte correlazione

➡ La dipendenza osservata risulta **in larga parte spiegabile** con la progressione naturale dei trofei

---

## 3️⃣ Effetti legati alla performance recente (debito / credito)

Per verificare se il sistema reagisca anche alla performance recente, e non esclusivamente ai trofei, è stata analizzata la presenza di effetti di “debito/credito” tra partite consecutive.

### Test

Confronto tra matchup dopo:

- vittoria molto sfavorevole
- sconfitta molto sfavorevole

Risultato:

- Dopo **vittoria eroica** → il giocatore **rimane in un contesto di matchup sfavorevoli**
    
    *(persistenza della difficoltà, non peggioramento rispetto al match appena giocato)*
    
- Dopo **sconfitta** → il giocatore tende a tornare verso matchup **più equilibrati**

Effetto medio osservato ≈ ±3%

### Origine dell’effetto

Ripetendo l’analisi separatamente su:

- carte (matchup no-lvl) → nessuna variazione significativa
- livelli (lvl diff) → variazione significativa

➡ Il peggioramento riguarda **i livelli**, non la composizione dei mazzi.

### L’effetto è spiegabile solo con i trofei?

Aumento medio livelli avversari per +100 trofei: **+0.097**

Aumento atteso per ±60 trofei: **~+0.050**

Aumento osservato dopo vittoria eroica: **+0.228**

➡ L’effetto è troppo grande per essere spiegato solo dalla variazione trofei

➡ Rimane significativo anche dopo aver sottratto l’aumento della specifica fascia di trofei

**Compatibile con un sistema SBMM con rating nascosto**

---

## 4️⃣ Persistenza tra sessioni (memoria del sistema)

Test su sessioni concluse con **bad streak** (ultimi 2 matchup <45%).

Confronto matchup al ritorno dopo pause brevi, medie e lunghe.

Risultato: il matchup al ritorno resta significativamente sfavorevole, con un effetto che si attenua progressivamente all’aumentare della durata della pausa

*Comportamento compatibile con un sistema che mantiene una memoria temporanea dello stato del giocatore tra sessioni, analogo ai meccanismi di incertezza presenti in alcuni modelli SBMM.*

---

## 5️⃣ Inizio sessione facilitato

Osservazione community: primi match più facili.

Test:

- confronto winrate inizio sessione vs resto
- confronto matchup inizio sessione vs resto

Risultato:

- winrate più alto all’inizio
- matchup più favorevole
- effetto dovuto principalmente ai livelli

*Compatibile con un sistema che, dopo una pausa, riduce temporaneamente l’incertezza sul rating per rivalutare rapidamente la stima della skill dopo un periodo di inattività..*

# Conclusioni

## Coerenza tra dichiarazioni ufficiali e comportamento osservato

L’obiettivo della tesi era verificare se il comportamento osservabile del sistema di matchmaking fosse coerente con le dichiarazioni ufficiali del publisher.

Le dichiarazioni analizzate descrivono il sistema come basato principalmente sui **trofei**, escludendo l’uso diretto delle carte possedute e dei loro livelli.

L’analisi statistica ha mostrato che:

- **Non emergono evidenze di manipolazione diretta dei mazzi**
    
    Le variazioni nel tipo di carte affrontate sono spiegabili con:
    
    - distribuzione dei mazzi nel meta
    - differenze tra fasce di trofei
    - variazioni legate all’orario
- **La distribuzione dei livelli delle carte è fortemente legata ai trofei**
    
    La maggior parte delle differenze di livello osservate tra gli avversari è coerente con la progressione naturale lungo la ladder.
    

Tuttavia, sono emersi anche effetti che **non risultano completamente spiegabili con il solo numero di trofei**:

- variazioni nei livelli degli avversari dopo performance eccezionali
- persistenza della difficoltà tra sessioni
- primi match della sessione mediamente più favorevoli

Questi fenomeni risultano compatibili con la presenza di un **sistema di valutazione della skill nascosto**, dotato di meccanismi di incertezza e adattamento alla performance recente, tipici dei moderni sistemi SBMM.

---

## Perché le dichiarazioni possono sembrare fuorvianti

Una lettura superficiale delle dichiarazioni ufficiali può portare a interpretarle come:

> “Il sistema usa **solo** i trofei e ignora completamente tutto il resto”
> 

L’analisi mostra invece che una formulazione di questo tipo è **semanticamente vera sul piano delle variabili esplicite**, ma non descrive necessariamente l’intera logica interna del sistema.

In particolare:

- I **trofei** possono essere il principale vincolo visibile e pubblico del matchmaking
- All’interno di questo vincolo possono coesistere meccanismi secondari di valutazione della skill che **non contraddicono direttamente** quanto dichiarato, ma ne ampliano il funzionamento reale

Ne risulta una comunicazione **tecnicamente corretta ma semplificata**, che può generare una discrepanza tra:

- ciò che il sistema effettivamente fa
- ciò che il giocatore medio crede che faccia

---

## Contributo della tesi

Questa ricerca introduce un approccio metodologico basato su:

- raccolta sistematica di dati reali
- reverse engineering statistico
- confronto diretto tra comportamento osservabile e comunicazione ufficiale

A differenza della maggior parte dei lavori esistenti, focalizzati su:

- progettazione di algoritmi
- percezione soggettiva dei giocatori

questa tesi si concentra sulla **verifica empirica della coerenza tra dichiarazioni e implementazione**, proponendo un modello di analisi replicabile anche su altri titoli multiplayer.

---

## Implicazioni per il settore

I risultati suggeriscono che:

- i publisher non forniscono necessariamente informazioni false
- ma adottano comunicazioni **semplificate**, pensate per essere comprensibili e rassicuranti per il pubblico generale

In un contesto in cui il matchmaking influenza:

- percezione di equità
- frustrazione
- permanenza nel gioco

una maggiore trasparenza strutturata potrebbe:

- ridurre la diffusione di teorie infondate
- aumentare la fiducia dei giocatori
- migliorare la comprensione del funzionamento reale dei sistemi competitivi

---

## Limiti e sviluppi futuri

Lo studio si basa su:

- un singolo titolo
- variabili osservabili dall’esterno
- assenza di accesso ai parametri interni del sistema

Futuri sviluppi potrebbero includere:

- analisi su più giochi e generi
- modelli statistici più avanzati per stimare rating nascosti
- collaborazione diretta con sviluppatori per validare i risultati