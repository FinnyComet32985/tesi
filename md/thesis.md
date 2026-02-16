\chapter*{Introduzione}
Nel contesto attuale, dove la tecnologia ha fatto passi da gigante, non basta più una bella grafica o un \textit{gameplay} moderno per decretare il successo di un videogioco.

La ragione principale risiede nell'eccessiva saturazione del mercato.

L'introduzione di abbonamenti che mettono a disposizione un parco titoli molto ampio, a un prezzo tutto sommato “conveniente”, ha fatto crollare quell'equilibrio già precario che si era venuto a creare.

I giocatori sono alla ricerca di esperienze ben curate e non del solito “copia e incolla” adottato dalle multinazionali per ridurre al minimo i costi di sviluppo.

Ciò che conta veramente è far sentire all'utente di avere un grande peso nel processo decisionale alla base dello sviluppo del videogioco.

Un classico esempio è rappresentato dalla corretta impostazione della difficoltà. Bisogna trovare un compromesso che non provochi noia per un'eccessiva semplicità o frustrazione per una sfida troppo ardua. In questi casi, il bilanciamento non è solo una scelta creativa, ma una necessità commerciale: se l'utente smette di giocare a causa di un'esperienza percepita come eccessivamente punitiva, il modello di business basato sulle microtransazioni crolla inevitabilmente.

A differenza dei titoli \textit{single-player} o \textit{cooperative}, dove abbiamo a disposizione diversi strumenti per correggere il tiro (come i selettori di difficoltà o la progressione delle statistiche del personaggio), nei \textit{multiplayer} la questione si fa più spinosa. Il giocatore non affronta più nemici controllati dal computer, ma si trova di fronte ad altre persone in carne e ossa.

Questo ci porta a una questione che resta, per molti versi, ancora aperta: come si può intervenire sulla difficoltà percepita in un ambiente competitivo senza dare l'impressione di manipolare il match? Il rischio, infatti, è quello di rompere il patto di equità che è alla base di ogni competizione, finendo per allontanare proprio quei giocatori che si volevano trattenere.

L'elemento fondante del funzionamento dei \textit{multiplayer} è il \textit{matchmaking}: quella funzione invisibile necessaria per decidere quali saranno i giocatori che si affronteranno in partita.

In un mondo ideale, il suo unico scopo è garantire una sfida equa, accoppiando utenti con livelli di progressione simili affinché il risultato finale dipenda unicamente dalla loro abilità e dalle strategie adottate.

Recentemente questo componente è finito al centro di un acceso dibattito. Le aziende descrivono pubblicamente i propri sistemi come basati principalmente su metriche semplici che rispecchiano la progressione e, indirettamente, la bravura. Tuttavia, una parte crescente della community percepisce comportamenti più complessi, schemi che si ripresentano con una certa regolarità e dinamiche che sembrano andare oltre le spiegazioni ufficiali.

Le voci si moltiplicano nei forum e sui social. Sospetti di algoritmi nascosti, ipotesi di manipolazione mirata, accuse di sistemi progettati non per garantire equità, ma per massimizzare il coinvolgimento. I publisher, dal canto loro, negano categoricamente l'uso di tecniche di questo tipo, richiamando il segreto industriale quando vengono richiesti dettagli più precisi.

È davvero tutto frutto di una suggestione collettiva o c'è qualcosa in più?

L'obiettivo di questo elaborato è proprio superare le sensazioni e le lamentele soggettive.

Attraverso un processo di \textit{reverse engineering}, supportato da analisi statistiche, cercheremo di verificare se il comportamento osservabile del sistema sia effettivamente coerente con le dichiarazioni ufficiali dei publisher o se emergano discrepanze che suggeriscano l'esistenza di meccanismi più complessi di quelli dichiarati.

Non si tratta di dimostrare presunte manipolazioni, ma di mettere alla prova le comunicazioni pubbliche con l'unico strumento che abbiamo a disposizione: i dati. Dati reali, raccolti sistematicamente e analizzati con metodi rigorosi.

Perché, se un sistema funziona davvero come viene descritto, i numeri devono confermarlo. E se i numeri raccontano un'altra storia, allora è il caso di chiedere spiegazioni più complete.

\chapter{Matchmaking}

Nel tempo, il modo di vivere le esperienze \textit{multiplayer} si è trasformato sensibilmente, e il \textit{matchmaking} ha giocato un ruolo centrale in questo cambiamento.

Inizialmente, i giocatori dovevano scorrere lunghe liste di server, cercando manualmente una partita che si adattasse alle proprie esigenze. Il \textit{matchmaking} nasce proprio per risolvere questo problema: niente più ricerche interminabili o attese prolungate, ma un sistema in grado di creare automaticamente una partita in pochi secondi.

Con la diffusione dei giochi \textit{free-to-play}, il ruolo del \textit{matchmaking} ha progressivamente assunto una funzione più ampia. Quello che era nato come uno strumento per facilitare l'accesso alle partite è diventato un elemento centrale anche per la gestione dell'esperienza di gioco nel lungo periodo. Di conseguenza, questi sistemi sono diventati sempre più complessi, adattandosi ad un pubblico sempre più competitivo.

Comprendere il funzionamento attuale del \textit{matchmaking} rappresenta quindi il punto di partenza per analizzarne l'evoluzione storica e le principali tipologie sviluppate nel tempo, dalle prime forme di valutazione dell'abilità fino ai modelli moderni descritti nella letteratura.

\section{Funzionamento del matchmaking}

Per comprendere le necessità che hanno portato alla creazione del \textit{matchmaking}, è innanzitutto utile analizzare come i giocatori riuscivano a giocare insieme nelle prime esperienze \textit{multiplayer}.

In una prima fase, il compito di ospitare le partite era affidato ai giocatori stessi, che tramite un'apposita funzione potevano creare un server di gioco. A seconda delle impostazioni, questo server poteva essere accessibile solo agli amici oppure visibile nelle liste pubbliche.

Questo tipo di architettura portava con sé una serie di problematiche rilevanti. Non si trattava soltanto di difficoltà legate alla stabilità della connessione: il giocatore che ospitava la partita godeva infatti di un vantaggio strutturale sugli altri partecipanti. Poiché il server veniva eseguito localmente sulla sua macchina, le sue azioni venivano elaborate senza i ritardi di trasmissione che invece influenzavano gli altri giocatori collegati da remoto, con una conseguente disparità nella reattività del gioco.

A questo si aggiungeva la possibilità, per utenti con competenze tecniche avanzate e dispositivi modificati, di accedere ai cosiddetti \textit{mod menu}, strumenti che permettevano di alterare il comportamento del gioco. Tra gli esempi più comuni si trovavano l'invincibilità, la possibilità di eliminare gli avversari con un solo colpo o di ottenere armi e munizioni illimitate.

Questi erano solo alcuni dei motivi che hanno spinto le case di sviluppo a spostare progressivamente l'\textit{hosting} delle partite su server proprietari.

Nonostante questo importante cambiamento infrastrutturale, rimaneva comunque il problema delle lunghe liste di server tra cui scegliere e della difficoltà nel trovare rapidamente partite equilibrate.

È in questo contesto che inizia a delinearsi il concetto moderno di \textit{matchmaking}.

Una volta chiarito il funzionamento dei primi sistemi \textit{multiplayer}, è possibile introdurre una definizione più precisa.

Il \textit{matchmaking} è un sistema integrato nei giochi \textit{multiplayer} che si occupa di selezionare, tra le richieste di accesso alla partita da parte dei giocatori, quelle più adatte a formare un'esperienza di gioco equilibrata e coinvolgente. Il sistema decide inoltre su quale server ospitare la partita e quali giocatori accoppiare, basandosi su diversi criteri, tra cui la progressione, la qualità della connessione e, in alcuni casi, l'abilità stimata o le preferenze espresse dagli utenti.

\section{Tipologie di matchmaking}

Definito il concetto di \textit{matchmaking}, è ora possibile esplorare le principali tipologie impiegate nei sistemi competitivi moderni. 
La classificazione avviene in base all'obiettivo perseguito dal sistema e, di conseguenza, ai parametri utilizzati per effettuare l'accoppiamento dei giocatori. 
Di seguito vengono presentate brevemente le categorie più rilevanti.

\subsection{Ping Based Matchmaking}

La prima tipologia sviluppata, nonché la più semplice, prende in considerazione esclusivamente la qualità della connessione dei giocatori. 
Questo tipo di accoppiamento mira a garantire a ogni partecipante un'esperienza di gioco più fluida possibile, riducendo il vantaggio competitivo che possiederebbero i giocatori dotati di una connessione superiore.

Prima di procedere, è necessaria una breve precisazione terminologica. In ambito videoludico, con il termine \textit{ping}, si fa riferimento al ritardo della comunicazione tra il client e il server, ossia al tempo necessario affinché un'azione eseguita dal giocatore venga inviata al server, processata e la risposta torni al client. 
In realtà, questa denominazione deriva dall'omonima \textit{utility} di rete, che utilizza il protocollo ICMP (\textit{Internet Control Message Protocol}) per misurare il \textit{Round Trip Time} (RTT), ovvero il tempo totale necessario a un pacchetto di rete per raggiungere un dispositivo destinatario e tornare al mittente. 

Sebbene il termine tecnicamente più corretto per indicare questo ritardo sia latenza (o RTT), l'uso di \textit{ping} si è consolidato nel linguaggio comune e nelle stesse interfacce di gioco. Per questo motivo, nel presente elaborato i due termini verranno utilizzati in modo intercambiabile.

Questa tipologia di \textit{matchmaking} è particolarmente indicata per i titoli in cui il tempo di reazione è critico per l'esito della sfida, come negli \textit{First-Person Shooter} (FPS), \textit{Third-Person Shooter} (TPS) o \textit{Real-Time Strategy} (RTS). 
In genere viene implementata in modalità di gioco definite “casual”, dove l'obiettivo primario è il divertimento dei giocatori e un eventuale esito negativo della partita non comporta penalità significative in termini di progressione o punteggio.

\subsection{Rank Based Matchmaking}

La situazione diventa più complessa quando, all'interno del gioco, vengono introdotti sistemi di progressione che non hanno soltanto una funzione estetica o di personalizzazione (come \textit{skin} o cosmetici), ma incidono direttamente sul \textit{gameplay}, ad esempio attraverso lo sblocco di abilità o il potenziamento dei personaggi. 

Spostando il focus da un'esperienza puramente “casual” a un contesto più competitivo, diventa necessario uno strumento in grado di bilanciare le partite, fornire obiettivi chiari ai giocatori e distinguere il loro livello di impegno e abilità. È in questo contesto che emergono i sistemi basati su trofei, leghe o gradi, comunemente definiti \textbf{Rank Based Matchmaking (RBMM)}. 

La maggior parte delle \textit{software house} dichiara di adottare proprio questa tipologia di matchmaking, in quanto percepita come la più trasparente dal giocatore. La visibilità del punteggio permette, infatti, di intuire con facilità il motivo dell'abbinamento. 

Sebbene il \textit{rank} non rappresenti in modo diretto e perfetto l'abilità reale di un giocatore, ne costituisce comunque una stima approssimativa. Non è raro osservare giocatori con livelli di progressione inferiori alla media della propria fascia che riescono comunque a ottenere buoni risultati grazie alla propria abilità. Questo comportamento è coerente con l'idea di un sistema percepito come equo, in cui la competenza del giocatore può compensare eventuali svantaggi legati alla progressione.

\subsection{Skill Based Matchmaking}

Una volta entrati in un contesto pienamente orientato alla competizione e potenzialmente propedeutico all'\textit{esport}, non è più sufficiente accoppiare i giocatori esclusivamente in base al loro livello di progressione. Diventa infatti necessario disporre di una stima quanto più accurata possibile dell'abilità effettiva del giocatore.

Si definisce \textbf{Skill Based Matchmaking (SBMM)} qualsiasi sistema di \textit{matchmaking} che utilizza una metrica numerica, comunemente chiamata \textit{MMR} (\textit{Matchmaking Rating}), per stimare la bravura di un giocatore. A differenza del \textit{rank} visibile al giocatore, l'\textit{MMR} è spesso un valore nascosto, aggiornato dinamicamente dal sistema in base ai risultati delle partite e ad altri parametri legati alle prestazioni individuali.

Questa distinzione tra \textit{rank} pubblico e valutazione interna è fondamentale: mentre il primo svolge anche una funzione motivazionale e di progressione percepita, il secondo rappresenta lo strumento tecnico utilizzato dal sistema per creare partite il più possibile equilibrate. In un sistema perfettamente calibrato, l'effetto atteso è che ciascun giocatore venga progressivamente abbinato ad avversari di livello simile, portando nel tempo a una distribuzione delle vittorie e delle sconfitte che tende ad avvicinarsi a un rapporto equilibrato, spesso prossimo al 50\% di \textit{win rate}.

Per stimare l'abilità dei giocatori molti sistemi di \textit{SBMM} si ispirano a modelli statistici sviluppati originariamente in altri contesti competitivi, successivamente adattati all'ambito videoludico. Tra i più noti si trovano i sistemi Elo, Glicko e TrueSkill, che verranno descritti nelle sezioni successive.

\subsubsection{ELO}

Il sistema Elo prende il nome dal fisico e statistico Arpad Elo, che lo sviluppò negli anni Sessanta per la Federazione Scacchistica Statunitense con l'obiettivo di valutare in modo quantitativo l'abilità relativa dei giocatori nelle competizioni ufficiali.

Si tratta di un sistema di rating probabilistico: a ciascun giocatore viene associato un punteggio numerico che rappresenta una stima della sua forza rispetto agli altri partecipanti. La differenza tra i punteggi di due giocatori consente di calcolare la probabilità attesa di vittoria per ciascuno di essi.

In termini generali, più la differenza tra i rating è ridotta, più l'incontro è considerato equilibrato. Quando due giocatori possiedono lo stesso punteggio Elo, il sistema prevede che ciascuno abbia una probabilità di vittoria del 50\%. All'aumentare della differenza di rating, la probabilità di vittoria del giocatore con punteggio più alto cresce in modo non lineare.

Dopo ogni partita, il rating dei giocatori viene aggiornato confrontando il risultato effettivo con quello atteso. Se il giocatore favorito vince, la variazione del punteggio sarà contenuta, poiché l'esito era già previsto dal sistema. Al contrario, se il giocatore sfavorito ottiene la vittoria, l'incremento del suo rating sarà maggiore, mentre il giocatore favorito subirà una riduzione più significativa.

L'entità della variazione è regolata da un parametro detto $K$\textit{-factor}, che determina quanto velocemente il punteggio di un giocatore può cambiare nel tempo. Valori elevati di $K$ rendono il sistema più reattivo ai risultati recenti, mentre valori più bassi producono una stima più stabile ma meno sensibile alle prestazioni immediate.

La semplicità del sistema Elo e la sua solida base statistica ne hanno favorito l'adozione come fondamento teorico per molti sistemi di \textit{Skill Based Matchmaking} nei videogiochi, spesso con modifiche e adattamenti per gestire partite a squadre, prestazioni individuali e incertezza nella stima dell'abilità.

\subsubsection{Glicko}

Il modello Glicko è stato sviluppato nel 1995 dallo statistico Mark Glickman. 
Esso rappresenta un'evoluzione del modello Elo ed è stato progettato per fornire una stima più realistica e dinamica dell'abilità dei giocatori.

Oltre al \textit{rating}, calcolato in modo analogo a quanto avviene nel sistema Elo, Glicko introduce un secondo parametro fondamentale: il \textit{Rating Deviation} (RD). Questo indicatore misura l'incertezza associata alla stima dell'abilità di un giocatore. In altre parole, mentre il punteggio indica quanto un giocatore è considerato forte, l'RD indica quanto tale valutazione sia ritenuta affidabile.

Un valore elevato di RD implica una grande incertezza: il modello dispone di poche informazioni attendibili sulle prestazioni recenti del giocatore. In queste condizioni, le variazioni del punteggio dopo una partita risultano più ampie, poiché l'obiettivo è aggiornare rapidamente una stima ancora poco solida. Al contrario, un RD basso indica che la valutazione è considerata stabile; di conseguenza, le modifiche successive sono più contenute.

Questo meccanismo consente a Glicko di incorporare anche la dimensione temporale. Quando un giocatore rimane inattivo per un periodo prolungato, il valore di RD aumenta progressivamente, riflettendo la crescente incertezza sulla sua abilità reale. In questo modo, al rientro in gioco, la valutazione diventa più sensibile ai nuovi risultati, permettendo un riallineamento più veloce della stima.

Una successiva evoluzione del modello, nota come Glicko-2, introduce un ulteriore parametro chiamato \textit{volatilità}. A differenza dell'RD, che misura l'incertezza della stima in un determinato momento, la volatilità descrive quanto l'abilità reale di un giocatore tenda a variare nel tempo. Giocatori con prestazioni molto altalenanti o in rapido miglioramento presentano una volatilità maggiore, che consente di adattare rapidamente la valutazione in presenza di risultati inaspettati. Al contrario, giocatori con rendimento stabile hanno una volatilità ridotta, rendendo la stima della loro abilità meno soggetta a oscillazioni improvvise.

\subsubsection{TrueSkill}

A differenza dei modelli Elo e Glicko, TrueSkill è un sistema sviluppato direttamente da Microsoft nei primi anni Duemila per la piattaforma \textit{Xbox Live}. Non deriva quindi da un modello preesistente, ma è stato progettato appositamente per il contesto videoludico.
L'abilità di un giocatore non viene rappresentata da un singolo valore numerico, ma da una distribuzione normale (gaussiana). Ogni utente è descritto attraverso due parametri: la media $\mu$, che rappresenta la stima corrente della sua abilità, e la deviazione standard $\sigma$, che misura l'incertezza associata a tale stima.

In modo simile al \textit{Rating Deviation} del modello Glicko, un valore elevato di $\sigma$ indica che il sistema dispone di poche informazioni affidabili sul giocatore; di conseguenza, i risultati delle partite producono variazioni più marcate nella valutazione della sua abilità. Al contrario, quando $\sigma$ è ridotto, la stima è considerata più stabile e viene aggiornata in modo più graduale.

Uno dei principali punti di forza di TrueSkill è la sua naturale applicazione alle partite con più giocatori o più squadre. Il modello utilizza infatti un approccio probabilistico per stimare il contributo relativo di ciascun partecipante al risultato finale, permettendo di aggiornare le valutazioni individuali anche in contesti in cui non esiste un semplice confronto uno contro uno.

Con il passare delle partite, l'obiettivo del sistema è ridurre progressivamente l'incertezza associata alla stima dell'abilità, ovvero diminuire il valore di $\sigma$. Un giocatore attivo e con prestazioni coerenti vedrà quindi la propria distribuzione restringersi attorno alla media, segnalando che il sistema ha individuato con maggiore precisione il suo livello di competenza.

Grazie a questa caratteristica, TrueSkill risulta più efficace dei sistemi tradizionali nella fase iniziale di valutazione dei nuovi giocatori, riuscendo a ottenere una stima più precisa in un numero inferiore di partite.

\subsection{Engagement Optimized Matchmaking}

Negli ultimi anni è stata ipotizzata una diversa filosofia di progettazione dei sistemi di \textit{matchmaking}, nota come \textbf{Engagement Optimized Matchmaking} (EOMM). A differenza dei modelli tradizionali, il cui obiettivo principale è creare partite equilibrate in base all'abilità stimata dei giocatori, questo approccio si concentra sull'ottimizzazione del coinvolgimento nel lungo periodo.

L'idea alla base dell'EOMM è che il sistema possa analizzare il comportamento passato dell'utente (come frequenza di gioco, durata delle sessioni o reazione a vittorie e sconfitte) per stimare la probabilità che egli interrompa la sessione dopo una determinata partita. Sulla base di queste previsioni, il sistema selezionerebbe gli avversari in modo da favorire l'esito che, per quello specifico giocatore in quel momento, comporta il minor rischio di abbandono.

In questa prospettiva, l'obiettivo non è direttamente quello di garantire equilibrio competitivo, ma di massimizzare la permanenza del giocatore nel sistema. Eventuali sequenze di vittorie o sconfitte non sarebbero quindi impostate in modo esplicito, ma emergerebbero come possibile conseguenza delle scelte operate dall'algoritmo.

È importante sottolineare che l'esistenza e l'eventuale utilizzo di sistemi di questo tipo nei giochi commerciali è oggetto di dibattito. Le aziende tendono a descrivere i propri algoritmi come orientati principalmente all'equilibrio competitivo, mentre una parte della community ritiene che possano essere presenti logiche più complesse legate alla fidelizzazione dell'utenza. Questa discrepanza tra comunicazione ufficiale e percezione dei giocatori rappresenta uno degli aspetti centrali che motivano le analisi presentate in questo elaborato.

\section{Matchmaking nella letteratura scientifica}

La letteratura scientifica sul \textit{matchmaking} si è concentrata soprattutto sullo sviluppo di modelli sempre più accurati per stimare l'abilità dei giocatori.

Ne sono un esempio i sistemi di \textit{Skill Based Matchmaking} analizzati in precedenza: Elo, Glicko e TrueSkill. Grazie alla collaborazione con gli sviluppatori, non mancano studi che ne analizzano il comportamento, i punti di forza e i limiti in contesti reali.

Negli ultimi anni, però, si è iniziato a guardare al problema da un'altra prospettiva. Accanto all'obiettivo dell'equilibrio competitivo, alcuni lavori hanno proposto di considerare il \textit{matchmaking} anche come uno strumento per influenzare il coinvolgimento del giocatore nel lungo periodo.

In questo contesto si inserisce il concetto di \textit{Engagement Optimized Matchmaking} (EOMM), che punta a ottimizzare la probabilità di permanenza del giocatore più che la sola equità della sfida.

Parallelamente, diverse ricerche hanno analizzato il tema dal punto di vista dei giocatori, mettendo in relazione il funzionamento del \textit{matchmaking} con fattori come frustrazione, motivazione e percezione di correttezza delle partite.

Da questi studi emerge che la sola trasparenza non basta a garantire fiducia nel sistema: i giocatori tendono a razionalizzare le sconfitte solo quando percepiscono il meccanismo di accoppiamento come coerente e comprensibile.

Per questo motivo, non è sufficiente limitarsi alle comunicazioni ufficiali. Diventa fondamentale cercare di capire quali variabili vengano realmente prese in considerazione dai sistemi e verificare se il loro comportamento osservabile sia coerente con quanto dichiarato pubblicamente.


\chapter{Metodologia di analisi}

Affrontare un'analisi di questo tipo significa, prima di tutto, scontrarsi con un limite strutturale piuttosto evidente: le logiche che governano il \textit{matchmaking} risiedono interamente su server proprietari. Si tratta di processi eseguiti ``a porte chiuse'', lontano da qualsiasi possibilità di osservazione diretta o controllo da parte nostra.

Non potendo accedere al codice sorgente e trovandoci nell'impossibilità di applicare le classiche tecniche di \textit{reverse engineering} (come la decompilazione, che in questo contesto risulterebbe del tutto inefficace), dobbiamo necessariamente tentare una strada alternativa. L'idea è quella di trattare il sistema come una \textbf{\textit{black box}}. In sostanza, accettiamo di considerare il meccanismo come una scatola chiusa: non ne conosciamo gli ingranaggi interni, ma possiamo registrarne con precisione gli \textit{input} e studiare ciò che restituisce in \textit{output}.

Questo concetto non è certo una novità in ambito informatico, dato che il \textit{black box testing} rappresenta una pratica standard per verificare se un software faccia ciò che promette senza guardarne il codice. Nel nostro caso, però, l'obiettivo è leggermente diverso. Non ci interessa tanto scovare dei \textit{bug}, quanto piuttosto cercare di ``decodificare'' la logica di fondo del sistema. Per farlo, ci affidiamo alla \textbf{statistica inferenziale}: analizzando con cura un campione rappresentativo di giocatori, potrebbe essere possibile formulare delle ipotesi sensate su come funzioni il sistema, per poi metterle alla prova confrontando i pattern che emergono con i modelli teorici dichiarati dagli sviluppatori.

\section{Difficoltà e limiti dell'analisi}

Però diciamocelo chiaramente: questo approccio della ``scatola nera'' ha i suoi limiti. Il problema principale è che il sistema potrebbe utilizzare variabili interne che noi semplicemente non possiamo vedere. Parametri nascosti, pesi che cambiano in tempo reale o algoritmi adattivi restano, di fatto, delle congetture che possiamo solo provare a intuire dai risultati.

C'è poi la questione del ``rumore'' nei dati, che tende a sporcare le osservazioni. Le prestazioni di un giocatore in una partita non dipendono solo dall'algoritmo di accoppiamento; entrano in gioco fattori umani e tecnici impossibili da misurare con precisione, come un calo di concentrazione momentaneo o una connessione che decide di rallentare proprio sul più bello. Questi elementi rendono difficile isolare con certezza l'impatto reale del \textit{matchmaking} rispetto alla naturale variabilità di ogni \textit{match}.

Inoltre, va considerato che il nostro campione, per quanto ampio, rimane pur sempre una parte della popolazione. È probabile che alcuni meccanismi del sistema si attivino solo in circostanze specifiche (magari solo per i giocatori di alto livello o in particolari fasi della progressione) che potrebbero non emergere con chiarezza dal nostro dataset. Per questo motivo, i risultati che presentiamo non vanno letti come una verità assoluta o una ricostruzione definitiva del codice di gioco, quanto piuttosto come una serie di evidenze statistiche che suggeriscono quanto il comportamento reale del sistema sia coerente con quello dichiarato.

\section{Raccolta dei dati}

Recuperare dati affidabili è stato probabilmente l'ostacolo più noioso. Nella maggior parte dei titoli moderni, mancano strumenti ufficiali per monitorare sistematicamente la cronologia delle partite. Inizialmente si potrebbe pensare di raccogliere i dati giocando in prima persona e annotando ogni risultato, ma questa strada appare subito impraticabile: non solo il processo sarebbe lentissimo e soggetto a errori di distrazione, ma ci ritroveremmo con un campione totalmente distorto, che rifletterebbe esclusivamente la mia esperienza.

Fortunatamente, alcuni giochi si appoggiano a piattaforme web esterne che permettono di consultare lo storico dei \textit{match} (solitamente gli ultimi 30 o 50) e i progressi dei vari utenti. Queste risorse ci hanno permesso di osservare il sistema ``sul campo'', attingendo a una base utenti reale e molto variegata.

Per automatizzare il tutto, abbiamo sviluppato uno script che interroga queste pagine, estrae le informazioni che ci servono e le organizza in un database. Dato che il numero di partite visibili per ogni ricerca è limitato, il programma è stato impostato per eseguire dei fetch periodici. In questo modo, siamo riusciti a costruire il dataset un po' alla volta, mettendo in coda i nuovi dati e salvando anche quelle partite che, con il passare dei giorni, sarebbero inevitabilmente sparite dai siti di consultazione. Questo approccio ci ha permesso di ottenere un volume di dati decisamente più solido, riducendo al minimo l'intervento manuale e i pregiudizi legati all'osservatore.

\section{Caso di studio: Clash Royale}

Dopo un'analisi preliminare dei principali titoli competitivi disponibili, la scelta del caso studio è ricaduta su \textit{Clash Royale}, videogioco mobile di genere RTS (\textit{real-time strategy}), pubblicato da Supercell nel 2016 e distribuito secondo un modello \textit{free-to-play}.

Il gioco si basa su scontri \textit{PvP} in tempo reale tra due giocatori, ciascuno dotato di un mazzo composto da otto carte selezionate prima dell'ingresso in coda. Questo aspetto rappresenta un elemento metodologicamente cruciale. A differenza di molti altri titoli competitivi, nei quali la selezione dei personaggi o delle abilità avviene durante la fase di caricamento della partita o addirittura nel corso della stessa, in \textit{Clash Royale} il mazzo è determinato interamente prima dell'attivazione del \textit{matchmaking}. 

Ciò implica che l'algoritmo di accoppiamento, nel momento in cui assegna l'avversario, conosce già la composizione completa del mazzo del giocatore. Questa caratteristica rende possibile, almeno in linea teorica, un accoppiamento basato non soltanto sul livello di abilità o sui trofei, ma anche sulle interazioni strategiche tra mazzi.

In questo contesto emerge il concetto di \textit{counter}. Nel gergo competitivo, un mazzo è considerato ``counter'' di un altro quando, per composizione delle carte e sinergie interne, presenta un vantaggio strutturale statisticamente significativo. La presenza o meno di un elevato numero di \textit{counter match} è uno dei principali motivi di discussione nella community, dove spesso si ipotizza l'esistenza di un sistema in grado di assegnare avversari sfavorevoli dopo determinate sequenze di vittorie.

Dal punto di vista metodologico, il fatto che il mazzo sia scelto prima della coda elimina una variabile di ambiguità presente in altri giochi. Non è infatti necessario analizzare il comportamento storico degli avversari o la frequenza di utilizzo di determinate fazioni: l'interazione tra i mazzi può essere valutata direttamente, partita per partita, sulla base delle carte effettivamente schierate.

Oltre a questo aspetto, \textit{Clash Royale} presenta ulteriori proprietà che lo rendono particolarmente adatto a un'analisi sul \textit{matchmaking}: un sistema di progressione chiaramente osservabile (trofei, arene, livelli delle carte), la presenza di dichiarazioni ufficiali sul funzionamento del sistema di accoppiamento e la disponibilità pubblica dello storico delle partite tramite piattaforme esterne.

\section{Costruzione del dataset}

La raccolta dei dati è avvenuta attraverso la piattaforma RoyaleAPI, che consente di consultare pubblicamente lo storico recente delle partite dei giocatori.

Sebbene Supercell metta a disposizione API ufficiali, il loro utilizzo richiede un indirizzo IP pubblico statico e l'adesione a specifiche politiche di accesso. Nel contesto di questa ricerca, tali requisiti non risultavano compatibili con l'infrastruttura disponibile. Inoltre, l'uso diretto delle API ufficiali avrebbe comportato potenziali limitazioni legate a \textit{rate limiting} o alla sospensione temporanea dell'accesso in caso di richieste frequenti.

RoyaleAPI ha offerto una soluzione più flessibile, permettendo l'estrazione incrementale dei dati tramite \textit{scraping} delle pagine HTML. Un ulteriore vantaggio è rappresentato dalla presenza di alcune metriche già calcolate, come la differenza media di livello tra i mazzi, che avrebbero altrimenti richiesto un'elaborazione manuale aggiuntiva.

Il sistema di raccolta è stato implementato tramite uno script in Python organizzato in moduli distinti per il recupero delle pagine, il \textit{parsing} delle informazioni e il salvataggio strutturato in un database SQLite.

Per quanto riguarda la selezione del campione, è stata adottata una tecnica di tipo \textit{snowball sampling}. A partire da un primo giocatore noto, sono stati progressivamente inclusi gli avversari incontrati e i membri dei rispettivi clan, privilegiando quelli con accesso recente al gioco, così da massimizzare la quantità di partite osservabili. Questo approccio ha permesso di ottenere un campione eterogeneo pur mantenendo una struttura relazionale tra i profili analizzati.

Il dataset finale comprende 40 giocatori per un totale di circa 8.700 partite, filtrate includendo esclusivamente la modalità ladder e profili con almeno 50 incontri registrati.

\section{Variabili analizzate}

Le metriche raccolte costituiscono il nucleo dell'analisi statistica successiva e richiedono quindi una definizione dettagliata.

Tra le variabili più rilevanti troviamo il \textit{matchup}, ovvero la probabilità teorica di vittoria stimata tramite il simulatore esterno DeckAI. Tale valore rappresenta una stima ex-ante dell'esito dello scontro, calcolata considerando la composizione dei mazzi, i livelli delle singole carte, nonché il tipo e il livello delle torri utilizzate. Il \textit{matchup} consente di distinguere, almeno teoricamente, le partite strutturalmente equilibrate da quelle in cui uno dei due giocatori parte con un vantaggio statistico.

Accanto a questo è stato calcolato il \textit{matchup no-lvl}, che considera esclusivamente la composizione delle carte ipotizzandone livelli equivalenti. La differenza tra le due metriche permette di isolare l'impatto del progresso numerico (livelli) rispetto alla sola interazione strategica tra mazzi.

Un'altra variabile centrale è il \textit{level diff}, definito come la differenza tra il livello medio delle carte dell'avversario e quello del giocatore. Questa misura consente di valutare eventuali squilibri strutturali legati alla progressione, indipendentemente dalla sinergia tra le carte.

Infine, particolare attenzione è stata dedicata all'elisir sprecato (\textit{elixir leaked}). In \textit{Clash Royale} l'elisir rappresenta la risorsa fondamentale per giocare le carte; una gestione inefficiente comporta uno svantaggio immediato. La quantità di elisir non utilizzato quando la barra è piena costituisce un indicatore indiretto della qualità decisionale del giocatore. Valori elevati suggeriscono errori di gestione, mentre valori contenuti indicano maggiore efficienza. Questa metrica risulta particolarmente utile per distinguere le sconfitte attribuibili a errori di esecuzione da quelle potenzialmente legate a uno svantaggio strutturale del \textit{matchup}.

\chapter{Dichiarazioni ufficiali}

Ora che abbiamo tutti gli strumenti per comprendere appieno l'analisi che stiamo per condurre, vediamo quali sono le dichiarazioni da verificare.

\begin{quote}
``Il sistema di matchmaking ti abbinerà con avversari che hanno un numero di trofei simile al tuo e non prenderà in considerazione né le carte che possiedi né il loro livello.

A volte la differenza tra il numero dei tuoi trofei e quelli dell'avversario può essere molto grande, ma ricorda che riceverai più trofei sconfiggendo un giocatore che ne possiede più di te.

Inoltre, la forza delle torri dell'avversario sarà uguale alla tua, oppure maggiore o minore di un livello: ad esempio, se la tua forza è a 12, inizialmente ti saranno abbinati solo avversari che hanno una forza pari a 11, 12 o 13.

Per garantire un matchmaking veloce e senza lunghi periodi di attesa, la ricerca degli avversari si estenderà alle forze inferiori e superiori in base a certi criteri.
\begin{itemize}
    \item La ricerca si espanderà di un livello di forza maggiore e inferiore ogni cinque secondi.
    \item La ricerca può arrivare a considerare al massimo quei giocatori con tre livelli sopra o sotto il tuo, cosa che avverrà dopo 10 secondi.
\end{itemize}

Il team che si occupa di Clash Royale tiene d'occhio il sistema di matchmaking e adotterà dei cambiamenti, se il sistema attuale avrà effetti negativi sull'esperienza di gioco.''~\cite{supercell_matchmaking}
\end{quote}

In breve, il matchmaking prende in considerazione principalmente i seguenti parametri:
\begin{itemize}
    \item Trofei del giocatore e dell'avversario
    \item Livello delle torri del re
\end{itemize}

Sono invece categoricamente escluse sia le carte utilizzate sia i loro livelli.

\section{Interpretazione delle dichiarazioni}

Se le dichiarazioni corrispondono a ciò che è stato implementato, ci aspetteremmo un sistema in cui non siano presenti pattern ricorrenti, in cui il risultato delle partite precedenti non influisca sul matchup successivo e in cui le carte avversarie non siano scelte appositamente, ma la loro frequenza sia coerente tra tutti i player analizzati.

Ci troveremmo quindi di fronte a un sistema di tipo RBMM, senza alcuna stima sulla skill né manipolazione dei matchup a fini di ritenzione.

Partendo da queste deduzioni, proviamo a costruire delle ipotesi rigorose e statisticamente verificabili.

\chapter{Formalizzazione delle ipotesi e verifica empirica del matchmaking}

Nel capitolo precedente abbiamo elencato alcune caratteristiche che dovremmo osservare nel sistema in caso di conformità rispetto alle dichiarazioni.

Riprendiamo ora queste considerazioni e le formalizziamo sotto forma di ipotesi verificabili empiricamente.

\section{Ipotesi da verificare}

\subsection{H1: Indipendenza dalla composizione del mazzo}

Se il sistema non considera le carte utilizzate, il mazzo che incontriamo non dovrebbe dipendere dal nostro. 

In altre parole, a parità di trofei e orario, la distribuzione degli archetipi avversari deve essere la stessa indipendentemente dall'archetipo che stiamo usando. Se uso un mazzo Beatdown, non dovrei trovare più (o meno) mazzi Control rispetto a chi usa un mazzo Cycle.

Se invece troviamo che certi archetipi avversari compaiono con frequenza diversa a seconda del mazzo che usiamo, significa che il sistema sta facendo qualcosa in più di quanto dichiarato.

\subsection{H2: Indipendenza dal livello delle carte}

Secondo le dichiarazioni, il sistema non guarda il livello delle carte. Quindi il \textit{level diff} (la differenza di livello tra le nostre carte e quelle avversarie) non dovrebbe seguire pattern particolari.

Se il \textit{level diff} fosse davvero casuale, dovremmo trovare una distribuzione coerente con quella attesa dalla popolazione di giocatori nella nostra fascia. Inoltre, non dovrebbero esserci correlazioni sistematiche con altre variabili come l'orario o il livello delle torri.

\subsection{H3: Assenza di logiche EOMM}

Un sistema EOMM manipola i matchup in base all'esito delle partite precedenti per massimizzare il coinvolgimento. Se Clash Royale usa EOMM, dovremmo vedere pattern ricorrenti: ad esempio, una sconfitta seguita da partite più facili, o una serie di vittorie seguita da matchup sfavorevoli.

Un sistema puramente basato su trofei e livello delle torri non dovrebbe mostrare questi pattern. Le vittorie e le sconfitte dovrebbero dipendere solo dalla nostra abilità e dalla casualità del matchup, non da una logica nascosta che reagisce ai nostri risultati recenti.

\subsection{H4: Assenza di meccanismi SBMM nascosti}

Anche se le dichiarazioni parlano di un sistema RBMM puro, potrebbe esistere uno strato nascosto di SBMM che aggiusta i matchup in base alla nostra abilità stimata.

Per verificarlo, cerchiamo tre fenomeni tipici dello SBMM:

\begin{itemize}
    \item \textbf{Reazione alla performance (Debito)}: se vinciamo una partita statisticamente "impossibile" (matchup sfavorevole), un sistema SBMM dovrebbe alzare immediatamente la stima della nostra abilità, proponendoci una sfida successiva molto più ardua (spesso tramite livelli più alti), cosa che un sistema basato solo sui trofei non farebbe così bruscamente.
    \item \textbf{Persistenza tra sessioni}: se il sistema tiene traccia delle nostre prestazioni, la difficoltà della prima partita di una nuova sessione dovrebbe dipendere da come è andata l'ultima della sessione precedente.
    \item \textbf{Hook fase}: nei primi match dopo aver iniziato a giocare (o dopo una pausa lunga), il sistema potrebbe darci partite più facili per agganciare il giocatore e farlo continuare.
\end{itemize}

Se troviamo evidenze di questi meccanismi, significa che il sistema fa più di quanto dichiarato.