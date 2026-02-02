# Spiegazione Tecnica: Il Paradosso del Matchmaking e l'Hidden MMR

## 1. La Contraddizione Apparente

**Dichiarazione Ufficiale Supercell:**
> *"Il sistema di matchmaking ti abbinerà con avversari che hanno un numero di trofei simile al tuo e non prenderà in considerazione né le carte che possiedi né il loro livello."*

**Risultato dei Nostri Test (Fenomeno "Debito"):**
> Quando un giocatore vince una partita "impossibile" (Matchup Sfavorevole), la partita successiva presenta avversari con **livelli delle carte significativamente più alti**, anche a parità di trofei.

**La Domanda:**
Come fa il sistema ad assegnarti avversari con livelli più alti se "non guarda i livelli"? Sembra impossibile senza violare la dichiarazione.

## 2. La Soluzione: L'Hidden MMR (Matchmaking Rating)

La risposta risiede probabilmente nell'utilizzo di un **MMR Nascosto (Hidden MMR)** o ELO, che agisce parallelamente ai Trofei visibili. Questo permette al sistema di manipolare la difficoltà senza dover esplicitamente interrogare il database sui livelli delle carte.

### Come funziona il meccanismo (Ipotesi Tecnica):

1.  **Due Valori di Ranking:**
    *   **Trofei (Visibili):** Determinano la fascia generale (es. 5000-5100).
    *   **MMR/ELO (Nascosto):** Misura la "forza reale" o la "performance recente" del giocatore.

2.  **Il Calcolo della Performance:**
    *   Quando vinci una partita "normale", il tuo MMR sale leggermente.
    *   Quando vinci una partita in **"Debito"** (ovvero contro pronostico, dove il sistema stimava una tua sconfitta), il tuo MMR subisce un **picco verso l'alto** (il sistema pensa: *"Questo giocatore è molto più forte del previsto"*).

3.  **Il Matchmaking:**
    *   La query di abbinamento non è `SELECT * WHERE trophies ≈ 5000 AND card_levels > X`.
    *   La query è `SELECT * WHERE trophies ≈ 5000 AND hidden_mmr ≈ TUO_MMR_ALTO`.

## 3. Perché l'MMR alto porta a Livelli Alti? (La Correlazione Indiretta)

Qui sta il trucco legale/tecnico. Il sistema non cerca i livelli, cerca l'MMR. Ma in una specifica fascia di trofei, chi sono i giocatori con MMR alto?

Immaginiamo la fascia 5000 Trofei. I giocatori con **MMR Alto** (quindi che vincono spesso o sono difficili da battere) appartengono a due categorie:

1.  **Smurf / Pro Player:** Giocatori bravissimi con livelli bassi (Rari).
2.  **Gatekeepers (Guardiani):** Giocatori mediocri ma con **Carte Maxate** (Molto comuni).

Poiché i Gatekeepers sono statisticamente molto più numerosi degli Smurf, quando il sistema ti abbina a qualcuno con il tuo stesso "MMR Alto" (appena guadagnato dopo la vittoria eroica), **statisticamente ti abbinerà quasi sempre a un Gatekeeper (Livelli Alti).**

## 4. Conclusione: È Rigged o No?

**Tecnicamente (Legalmente):**
Supercell dice la verità. L'algoritmo di selezione guarda solo Trofei e MMR (Skill/Performance). Non c'è una riga di codice che dice `if player_won_debt then find_opponent_with_level_14`.

**Di Fatto (Empiricamente):**
Il risultato è indistinguibile da un sistema che guarda i livelli. Poiché i livelli delle carte sono il fattore principale che alza l'MMR di un giocatore scarso (permettendogli di rimanere a galla), **matchare per MMR equivale a matchare per Livelli.**

### Il "Debito" spiegato
Il fenomeno del "Debito" che abbiamo osservato è quindi la correzione dell'MMR.
1.  Sei in svantaggio (Debito).
2.  Vinci (Evento anomalo).
3.  Il sistema aggiorna il tuo MMR verso l'alto ("Sei troppo forte per questi avversari").
4.  Il prossimo avversario ha MMR più alto.
5.  A quei trofei, MMR più alto significa quasi sempre **Livelli più alti**.

In sintesi: **Il sistema non ti punisce perché hai vinto, ti promuove in una fascia di MMR dove gli unici abitanti sono giocatori con carte più forti delle tue.**

## 5. L'Illusione dei Counter (Stesso principio dei Livelli)

Lo stesso meccanismo spiega perché spesso si ha la sensazione di incontrare dei **Counter** quando si sale.

Se il tuo MMR è alto, il sistema ti abbina ad altri giocatori con MMR alto nella tua fascia. Chi sono questi giocatori?
1.  Giocatori con carte maxate (Gatekeepers).
2.  Giocatori che usano **Mazzi Meta** o **Mazzi molto forti** (es. Log Bait, Hog Cycle, Mega Knight).

Se tu stai usando un mazzo "fatto in casa" (Homebrew) e vinci, il tuo MMR sale. Verrai abbinato a giocatori che usano mazzi ottimizzati (Meta). Questi mazzi sono strutturalmente superiori al tuo e ti sembreranno dei **Counter specifici**.

**Realtà:** Non sei stato abbinato contro un counter specifico per te. Sei stato abbinato contro un "Mazzo Vincente". E i mazzi vincenti tendono a counterare i mazzi amatoriali.

## 6. Il Fenomeno "Grax" (3 Pro e 1 Nabbo)

Un commento ricorrente (spesso citato sotto i video di youtuber come Grax) descrive questa esperienza: *"Trovo 3-4 player fortissimi di fila e poi uno che sembra aver scaricato il gioco ieri"*.

Questo è l'effetto della **Correzione Elastica dell'MMR** e dei meccanismi di **Retention**:

1.  **I "Player Fortissimi" (High MMR):** Sei arrivato al tuo picco di MMR. Il sistema ti abbina contro Gatekeepers o giocatori molto skillati. Perdi 3 o 4 partite di fila.
2.  **Il Crollo dell'MMR:** Con ogni sconfitta, il tuo MMR nascosto scende drasticamente (spesso più velocemente dei trofei visibili).
3.  **Il "Nabbo" (Low MMR / Pity Match):**
    *   Dopo la serie di sconfitte, il tuo MMR è crollato a un livello dove risiedono i giocatori realmente scarsi o casual.
    *   Inoltre, dopo una Losing Streak (es. 3 sconfitte), molti sistemi attivano un **"Pity Match"** (Partita di Pietà), abbinandoti intenzionalmente a un avversario con un Win Rate terribile (o un Bot sotto i 4000 trofei) per farti vincere, rilasciare dopamina ed evitare che tu chiuda il gioco per frustrazione.
