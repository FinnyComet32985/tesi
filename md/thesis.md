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

\subsection{Definizione di sessione di gioco}

Per analizzare correttamente il comportamento dei giocatori e del sistema nel tempo, è stato necessario strutturare il flusso continuo delle partite in unità discrete denominate \textit{sessioni di gioco}.

Una sessione è definita come una sequenza ininterrotta di partite giocate dallo stesso utente. Per identificare i confini tra una sessione e l'altra, è stato applicato un criterio basato sull'intervallo temporale tra due match consecutivi.

Nello specifico, è stata fissata una soglia (\textit{threshold}) di 20 minuti: se il tempo trascorso tra la fine di una partita e l'inizio della successiva supera tale valore, la sequenza corrente viene considerata conclusa e la nuova partita segna l'inizio di una nuova sessione.

Questa suddivisione è fondamentale per isolare fenomeni come l'\textit{hook effect} (l'analisi delle prime partite dopo una pausa) e per valutare la persistenza di determinati stati del matchmaking tra sessioni distinte.

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


\section{Definizioni preliminari e metodologia dei test}

Prima di procedere è necessario chiarire alcuni concetti utili per comprendere la struttura delle analisi e la corretta interpretazione dei risultati.

In precedenza è stato definito \textit{counter} un avversario che possiede un mazzo in grado, per composizione e sinergia delle carte, di neutralizzare efficacemente le strategie offensive avversarie o di difendere le proprie torri con un consumo inferiore di elisir, realizzando il cosiddetto ``positive elixir trade''.

A questa definizione si affianca il concetto di \textit{meta}. Con il termine meta si identifica l’insieme delle carte o degli archetipi che, in un determinato periodo, risultano più efficaci e quindi maggiormente utilizzati rispetto agli altri.

Questi concetti assumono rilevanza metodologica poiché la progressione in \textit{Clash Royale} non avviene esclusivamente attraverso i trofei, ma è fortemente legata anche allo sblocco e al potenziamento delle carte. La modalità principale, la ladder, prevede il raggiungimento progressivo di arene che consentono l’accesso a nuove carte.

Ne consegue che il meta non è uniforme lungo tutta la scala dei trofei, ma varia in funzione delle carte disponibili e del livello medio dei giocatori presenti in ciascuna fascia.

Inoltre, i livelli delle carte modificano in modo statisticamente significativo il valore del matchup (cfr. Sezione~XXXX).

Per questo motivo risulta necessario analizzare separatamente la componente strutturale del mazzo e quella legata ai livelli, calcolando sia un matchup comprensivo dei livelli sia una versione che li esclude (matchup no-level).

Infine, la distribuzione del meta e dei livelli degli avversari potrebbe dipendere anche dalla composizione della \textit{playerbase} attiva in una determinata fascia oraria.

Diventa pertanto necessario applicare test che consentano di isolare tali fattori prima di formulare interpretazioni sul comportamento del sistema di matchmaking.

\subsection{Strumenti statistici utilizzati}
Nella nostra analisi abbiamo utilizzato diversi test statistici particolarmente rinomati in questo ambito~\cite{sheskin2020handbook}.
Di seguito ne presentiamo una panoramica.

\subsubsection{Correlazione di Spearman}
La correlazione di Spearman ($\rho$) è un test non parametrico che misura la forza e la direzione della relazione monotona tra due variabili. A differenza della correlazione di Pearson, che richiede una relazione lineare, Spearman lavora sui \textbf{ranghi} dei dati anziché sui valori assoluti.

I ranghi rappresentano semplicemente le posizioni ordinali dei dati quando vengono ordinati. Ad esempio, i valori $[10, 5, 20, 15]$ hanno ranghi $[2, 1, 4, 3]$. Questa trasformazione rende il test robusto rispetto agli \textit{outlier} e permette di rilevare qualsiasi relazione in cui le variabili crescono o decrescono insieme, anche se non in modo proporzionale.

Il coefficiente varia tra $-1$ e $+1$:
\begin{itemize}
    \item $\rho = +1$: relazione monotona crescente perfetta (al crescere di una variabile, cresce anche l'altra)
    \item $\rho = -1$: relazione monotona decrescente perfetta (al crescere di una variabile, l'altra diminuisce)
    \item $\rho = 0$: assenza di relazione monotona
\end{itemize}

Questo test risulta particolarmente utile nel nostro contesto per tre motivi: è robusto rispetto agli \textit{outlier}, non assume che i dati seguano una distribuzione normale e permette di rilevare relazioni non lineari ma comunque monotone. 

Nel caso specifico, lo utilizziamo per verificare se variabili come i livelli degli avversari o il \textit{matchup} siano correlati con fattori confondenti quali i trofei, l'orario di gioco o il mazzo utilizzato.

\subsubsection{Test di Wilcoxon}
Il test di Wilcoxon per ranghi con segno è un test non parametrico utilizzato per confrontare due campioni appaiati, ovvero coppie di osservazioni sullo stesso soggetto in condizioni diverse. Il test lavora sui ranghi delle differenze tra le coppie anziché sui valori assoluti, rendendolo robusto rispetto agli \textit{outlier} e non richiedendo assunzioni di normalità.

Nel nostro contesto, lo utilizziamo per verificare se determinate condizioni (ad esempio, vittoria vs sconfitta nella partita precedente) producano cambiamenti sistematici in variabili come il \textit{matchup} o il \textit{level difference} della partita successiva, analizzando lo stesso giocatore in momenti diversi.

\subsubsection{Test $\chi^2$ (Chi-quadro)}
Il test Chi-quadro di indipendenza verifica se esiste una relazione statisticamente significativa tra due variabili categoriali. Il test confronta le frequenze osservate in una tabella di contingenza con le frequenze attese sotto l'ipotesi di indipendenza.

Un p-value inferiore a 0.05 indica che le due variabili sono dipendenti, ovvero che la distribuzione di una è influenzata dai valori dell'altra.

Nel contesto del \textit{matchmaking}, questo test è fondamentale per verificare due aspetti:
\begin{itemize}
    \item \textbf{Indipendenza tra mazzi}: se l'archetipo del mazzo utilizzato dal giocatore influenza la distribuzione degli archetipi avversari incontrati
    \item \textbf{Memoria del sistema}: se lo stato di una partita (ad esempio, \textit{matchup} favorevole/sfavorevole) influenza probabilisticamente lo stato della partita successiva nelle catene di Markov
\end{itemize}

\subsubsection{Catene di Markov}
Le catene di Markov non sono un test statistico in senso stretto, ma un framework matematico per modellare sequenze di eventi in cui la probabilità di transizione verso uno stato futuro dipende esclusivamente dallo stato corrente.

Nel nostro caso, trattiamo le partite come una sequenza di stati (ad esempio: \textit{matchup} favorevole, equilibrato, sfavorevole) e costruiamo una \textbf{matrice di transizione} che registra con quale frequenza, dopo essere stati nello stato $i$, ci si trova nello stato $j$.

L'\textbf{ipotesi nulla} che vogliamo verificare è l'indipendenza: se il sistema non ha memoria, la probabilità di trovarsi in uno stato al tempo $t+1$ dovrebbe corrispondere alla frequenza globale di quello stato, indipendentemente dallo stato al tempo $t$. Per verificarlo, applichiamo il test Chi-quadro alla matrice di transizione.

Se il test risulta significativo (p-value < 0.05), significa che il sistema possiede \textbf{memoria}: lo stato della partita precedente influenza sistematicamente quello della successiva.

\subsubsection{Probabilità $p^k$}
Questo non è un test ma un metodo per calcolare la probabilità teorica di osservare $k$ eventi consecutivi dello stesso tipo, assumendo che gli eventi siano indipendenti tra loro.

Se un determinato tipo di \textit{matchup} (ad esempio, sfavorevole) ha una probabilità globale $p$ di verificarsi, la probabilità di osservare $k$ occorrenze consecutive è semplicemente:
\[
P(\text{streak di lunghezza } k) = p^k
\]

Nel nostro contesto, lo utilizziamo come \textbf{baseline teorico} per confrontare il numero di \textit{streak} (filotti) osservate con quello atteso sotto ipotesi di indipendenza. Ad esempio, se i \textit{matchup} sfavorevoli hanno frequenza globale del 40\%, la probabilità di trovarne tre consecutivi in una sessione dovrebbe essere $0.4^3 = 6.4\%$.

Se il numero di \textit{streak} osservate supera significativamente questo valore, è un indizio che il sistema sta manipolando l'ordine delle partite.

\subsubsection{Z-score}
Lo Z-score è una trasformazione statistica che normalizza i dati esprimendoli in termini di deviazioni standard dalla media:
\[
Z = \frac{X - \mu}{\sigma}
\]
dove $X$ è il valore osservato, $\mu$ la media della popolazione e $\sigma$ la deviazione standard.

Un valore assoluto di Z-score superiore a 2 indica che l'osservazione è anomala (si trova oltre il 95\% della distribuzione normale).

Nel nostro contesto, lo utilizziamo per normalizzare il \textit{level difference} rispetto alla fascia di trofei. Poiché i livelli degli avversari crescono naturalmente con i trofei, non ha senso confrontare un \textit{level diff} di $-1$ a 5000 trofei con lo stesso valore a 10000 trofei. Normalizzando per fascia, possiamo identificare partite con livelli \textbf{anomali rispetto alla norma della fascia}, indipendentemente dalla progressione naturale.

Uno Z-score inferiore a $-2$ indica un \textit{match} in cui l'avversario ha livelli significativamente più alti del normale per quella fascia.

\subsubsection{Shuffle globale e intra-sessione}
Questi sono due metodi di permutazione che abbiamo sviluppato per creare \textbf{baseline empirici} contro cui confrontare le \textit{streak} osservate.

\textbf{Global Shuffle}: Mescoliamo tutte le partite del giocatore mantenendo però intatte le sessioni di gioco (ovvero, ogni sessione conserva lo stesso numero di partite). Questo test verifica se i \textit{matchup} estremi tendono ad ``aggrumarsi'' in determinate sessioni piuttosto che distribuirsi uniformemente nel tempo.

Se le \textit{streak} osservate superano significativamente il global shuffle, significa che esistono ``bad sessions'' o ``good sessions'' programmate dal sistema.

\textbf{Intra-Session Shuffle}: Mescoliamo le partite solo all'interno di ciascuna sessione, mantenendo invariata la composizione della sessione stessa. Questo test verifica se l'ordine delle partite dentro la sessione è manipolato.

Se le \textit{streak} osservate superano l'intra-session shuffle, significa che il sistema sta costruendo intenzionalmente sequenze favorevoli o sfavorevoli all'interno delle sessioni.

\subsubsection{Test di Mann–Whitney U}
Il test di Mann-Whitney U (equivalente al test di Wilcoxon rank-sum) è un test non parametrico utilizzato per confrontare due campioni indipendenti. Come gli altri test basati sui ranghi, non richiede che i dati seguano una distribuzione normale: ordina tutti i valori di entrambi i gruppi insieme e verifica se i ranghi di un gruppo tendono ad essere sistematicamente più alti o più bassi dell'altro.

L'ipotesi nulla è che le due popolazioni abbiano la stessa distribuzione. Un p-value < 0.05 indica che una delle due popolazioni tende ad avere valori sistematicamente più alti (o più bassi) dell'altra.

Nel nostro contesto, lo utilizziamo per confrontare il \textit{matchup} medio della partita successiva in due condizioni diverse, ad esempio:
\begin{itemize}
    \item Dopo una vittoria vs dopo una sconfitta
    \item Dopo un \textit{matchup} favorevole vs dopo uno sfavorevole
    \item Prima sessione della giornata vs sessioni successive
\end{itemize}

Questo ci permette di rilevare meccanismi di ``debito'' o ``credito'' implementati dal sistema.

\subsubsection{T-test}
Il t-test è un test parametrico utilizzato per confrontare le medie di due gruppi. A differenza dei test non parametrici, assume che i dati seguano una distribuzione normale (o che il campione sia sufficientemente grande da invocare il teorema del limite centrale).

Esistono due varianti principali:
\begin{itemize}
    \item \textbf{T-test per campioni indipendenti}: confronta le medie di due gruppi diversi che non hanno relazione tra loro
    \item \textbf{T-test per campioni appaiati}: confronta le medie dello stesso gruppo in due condizioni diverse
\end{itemize}

Nel nostro contesto, utilizziamo il \textbf{t-test per campioni indipendenti} per analizzare i \textbf{residui} del \textit{level difference}. Confrontiamo infatti due gruppi distinti di partite: quelle che seguono una vittoria ``eroica'' e quelle che seguono una sconfitta in ``debt''. Poiché le partite nei due gruppi si verificano in momenti e contesti diversi queste sono indipendenti.

Dopo aver rimosso l'effetto naturale dei trofei sulla crescita dei livelli (calcolando i residui), verifichiamo se esistono differenze sistematiche nei livelli avversari tra i due gruppi. Se il test risulta significativo, indica che il \textit{matchmaking} sta aggiustando i livelli oltre quanto spiegabile dalla sola progressione naturale, suggerendo un meccanismo di compensazione basato sulle prestazioni recenti.

\subsubsection{Indice di Jaccard}
L'indice di Jaccard è una misura di similarità tra due insiemi, definito come il rapporto tra l'intersezione e l'unione:
\[
J(A, B) = \frac{|A \cap B|}{|A \cup B|}
\]

Il valore varia tra 0 (insiemi completamente disgiunti) e 1 (insiemi identici).

Nel contesto del \textit{matchmaking}, lo utilizziamo per quantificare la similarità tra il pool di carte disponibili in diverse arene o fasce di trofei. Questo ci permette di comprendere quanto il \textit{meta} cambi tra le varie fasi di progressione e di controllare che eventuali differenze nei \textit{matchup} non siano dovute semplicemente a una diversa disponibilità di carte.

\subsubsection{Test di Kruskal-Wallis}
Il test di Kruskal-Wallis è un test non parametrico utilizzato per confrontare tre o più gruppi indipendenti. Rappresenta l'estensione del test di Mann-Whitney U al caso di gruppi multipli ed è l'alternativa non parametrica all'ANOVA a una via.

Come gli altri test basati sui ranghi, non richiede che i dati seguano una distribuzione normale: tutti i valori vengono ordinati insieme indipendentemente dal gruppo di appartenenza, e il test verifica se i ranghi medi dei diversi gruppi differiscono significativamente tra loro.

L'ipotesi nulla è che tutte le popolazioni abbiano la stessa distribuzione. Un p-value < 0.05 indica che almeno uno dei gruppi tende ad avere valori sistematicamente diversi dagli altri.

Nel nostro contesto, lo utilizziamo per confrontare il \textit{matchup} o il \textit{level difference} in diverse condizioni simultaneamente, ad esempio:
\begin{itemize}
    \item Confronto tra diverse fasce orarie (mattina, pomeriggio, sera, notte)
    \item Confronto tra diversi tipi di mazzo utilizzato (Beatdown, Control, Cycle, etc.)
    \item Confronto tra diverse fasi di progressione (arena iniziale, intermedia, avanzata)
\end{itemize}

Questo test è particolarmente utile quando vogliamo verificare l'effetto di variabili categoriali con più di due livelli, permettendoci di identificare se esiste una dipendenza generale prima di eventualmente procedere con confronti post-hoc tra coppie specifiche di gruppi.

\subsubsection{Test esatto di Fisher}
Il test esatto di Fisher è un test statistico utilizzato per verificare l'indipendenza tra due variabili categoriali in tabelle di contingenza, tipicamente 2×2. A differenza del test Chi-quadro, che si basa su approssimazioni asintotiche, il test di Fisher calcola la probabilità esatta di osservare la distribuzione dei dati (o una più estrema) sotto l'ipotesi nulla di indipendenza.

Questo test è particolarmente indicato quando:
\begin{itemize}
    \item I campioni sono di dimensioni ridotte (tipicamente con celle della tabella di contingenza < 5)
    \item Si vuole ottenere un p-value esatto senza ricorrere ad approssimazioni
    \item Le assunzioni del test Chi-quadro non sono soddisfatte
\end{itemize}

L'ipotesi nulla è che non esista associazione tra le due variabili categoriali. Un p-value < 0.05 indica che l'associazione osservata è statisticamente significativa e non è dovuta al caso.

\section{Verifica delle ipotesi}

\subsection{Test propedeutico}

è ormai risaputo nella community di Clash Royale che i livelli delle carte hanno un impatto sulle probabilità di vittoria di una partita. Com'è giusto che sia in questo contesto non si è voluto dare nulla per scontato.

Come primo test, soprattutto per prendere confidenza con i dati e i vari strumenti, si è voluto cercare di capire se questa convinzione è fondata.

Nello specifico abbiamo confrontato per ogni partita del dataset il matchup e il matchup no lvl, con l'obiettivo di osservare se e in che modo si relazionano i due parametri.

A questo scopo gli strumenti utilizzati sono due:

\begin{itemize}
    \item Correlazione di Spearman
    \item Test di Wilcoxon
\end{itemize}

Il coefficiente di Spearman ($\rho$) ha permesso di verificare la relazione presente. Un valore elevato significherebbe che i livelli hanno un basso impatto sulla probabilità di vittoria, al contrario un valore basso sta a significare un alto impatto.

Il p-value del test di Wilcoxon ci permette di verificare se tale differenza sia sistematica o casuale.

\begin{listing}[t]
\caption{Risultato dei test sull'impatto dei livelli}
\begin{minted}[
    frame=lines,
    framerule=0.8pt,
    fontsize=\footnotesize,
    breaklines
  ]{text}
IMPATTO DEI LIVELLI
Media Matchup REALE:   49.79%
Media Matchup NO-LVL:  49.33%
Delta Medio (Real-No): +0.46% (Positivo = Vantaggio Livelli)
Correlazione (Real vs NoLvl): 0.4549 (p=0.0000)
(Alta correlazione = I livelli contano poco; Bassa = I livelli stravolgono il matchup)

Test Wilcoxon (Differenza Significativa): p-value = 0.0030
RISULTATO: SIGNIFICATIVO
\end{minted}
\label{lst:test-livelli}
\end{listing}

I risultati indicano una correlazione moderata (0,45). Questo indica che l'inclusione dei livelli influisce significativamente sul matchup.

Un p-value inferiore a 0,05 indica che la differenza non è frutto di una casualità. In questo caso il valore (0,0030) è di molto inferiore, permettendo di rifiutare l'ipotesi nulla.


\subsection{H1 - Indipendenza dalla composizione del mazzo}

Nell'ipotesi H1 volevamo verificare se la composizione del mazzo non influenzasse, come da dichiarazioni, sulle logiche di matchmaking.

Per fare ciò abbiamo svolto i seguenti passaggi:
\begin{itemize}
    \item Analisi sequenziale del \textit{matchup no-level} tramite catene di Markov
    \item Test $\chi^2$ di indipendenza su matrici di transizione
    \item Analisi della probabilità di streak di matchup no lvl estremi
    \item Analisi controllata per fascia trofei (bucket) rispetto a orario e mazzo
    \item Test $\chi^2$ inter-player su archetipi player vs archetipi avversari
\end{itemize}

\subsubsection{Analisi catene di markov}

Come prima cosa abbiamo suddiviso i matchup no lvl in tre categorie:
\begin{itemize}
    \item Sfavorevole (Unfavorable): $\text{matchup no-lvl} < 45\%$
    \item Neutro (Even): $45\% \leq \text{matchup no-lvl} \leq 55\%$
    \item Favorevole (Favorable): $\text{matchup no-lvl} > 55\%$
\end{itemize}

A partire da queste categorie è stata costruita una matrice di transizione che mostra la probabilità di ottenere da un tempo $t$ a un tempo $t+1$.

Se il sistema fosse completamente privo di memoria rispetto alla composizione del mazzo, la distribuzione degli stati successivi dovrebbe essere coerente con la distribuzione globale attesa.

\begin{listing}[t]
\caption{Risultato test markov per indipendenza dei matchup no lvl}
\begin{minted}[
    frame=lines,
    framerule=0.8pt,
    fontsize=\footnotesize,
    breaklines
  ]{text}
Totale Transizioni: 5533
------------------------------------------------------------------------------
STATO PREC.  | NEXT: Unfavorable   | NEXT: Even        | NEXT: Favorable                
------------------------------------------------------------------------------
Unfavorable  | 46.9% (Exp 38.1%) ! | 27.9% (Exp 29.9%) | 25.1% (Exp 32.0%) ! | 
Even         | 36.0% (Exp 38.1%)   | 31.8% (Exp 29.9%) | 32.1% (Exp 32.0%)   | 
Favorable    | 30.0% (Exp 38.1%) ! | 30.3% (Exp 29.9%) | 39.6% (Exp 32.0%) ! | 
------------------------------------------------------------------------------
Test Chi-Quadro: p-value = 0.000000
RISULTATO: DIPENDENZA SIGNIFICATIVA (Memoria presente).
\end{minted}
\label{lst:test-markov-matchup-no-lvl}
\end{listing}

Il test $\chi^2$ eseguito sulla matrice ha evidenziato una dipendenza statisticamente significativa tra stati consecutivi.

Questo risultato suggerisce la presenza di memoria nella sequenza dei \textit{matchup} strutturali.

\subsubsection{Analisi streak di matchup no lvl estremi}

Per approfondire tale dipendenza è stata analizzata la probabilità di osservare streak di matchup no lvl estremi ($>80\%$ o $<30\%$). Confrontando gli eventi osservati rispetto alla probabilità in caso di indipendenza, con il global shuffle e l'intra-session shuffle.

\begin{listing}[t]
\caption{Analisi streak matchup estremi}
\begin{minted}[
    frame=lines,
    framerule=0.8pt,
    fontsize=\footnotesize,
    breaklines
  ]{text}
--- MATCHUP SFAVOREVOLI (< 30.0%) ---
Metodo                    | Count      | Prob %     | Ratio (Obs/Exp)
----------------------------------------------------------------------
Osservato                 | 5          | 0.1227     | 1.00x          
Teorico (p^3)             | 1.20       | 0.0296     | 4.15           
Global Shuffle            | 4.89       | 0.1201     | 1.02           
Intra-Session Shuffle     | 6.91       | 0.1695     | 0.72           
\end{minted}
\label{lst:test-no-lvl-streak}
\end{listing}

Nonostante il valore osservato risulta superiore all'ipotesi di indipendenza ($p^3$), è in linea con i valori degli shuffle.   
Di conseguenza le streak non sembrano essere organizzate in modo intenzionale ma potrebbe trattarsi di raggruppamenti dovuti alla popolazione attiva nella fascia oraria o al meta locale.

\subsubsection{Analisi fattori fasce di trofei e orario}

Prima di trarre conclusioni definitive è quindi necessario controllare che questa dipendenza non sia causata da alcuni fattori esterni, quali i trofei, l'orario, o il meta locale.

Per la prima verifica abbiamo utilizzato la correlazione di spearman tra i matchup no lvl e i trofei. Nonostante la correlazione sia significativa questa risulta molto debole ($\rho=0.07$). 

il dataset è stato suddiviso in bucket (fasce) da 500 trofei e, per ognuno di questi, è stata testata (tramite test di Kruskal-Wallis) la dipendenza tra il matchup no lvl e la fascia oraria ma anche tra il matchup no lvl e il mazzo del giocatore.

I risultati mostrano che l'effetto dell'orario è sporadico e non consistente. Mentre la dipendenza dal mazzo tende a risultare significativa soprattutto nelle fasce medio alte.

Per cui si rafforza l'ipotesi per cui la variazione è giustificabile dal meta locale.

\subsubsection{Analisi meta ranges}

Per verificare se i cambi di meta sono così repentini da poter giustificare il cambio di matchup no lvl abbiamo analizzato i vari deck utilizzati nelle varie fasce, riportando il tasso di transizione (rispetto alla fascia precedente) tramite l'indice di Jaccard e identificato le carte in meta in quella fascia (frequenza nella fascia > $\mu_{globale}+2\sigma$).

\begin{listing}[t]
\caption{Risultato analisi variazione meta}
\begin{minted}[
    frame=lines,
    framerule=0.8pt,
    fontsize=\footnotesize,
    breaklines,
    escapeinside=@@
  ]{text}
CARTE DOMINANTI & TASSO DI TRANSIZIONE
Dominant: Frequenza > Media Globale + 2*StdDev.
Transition: 1 - Jaccard Index (Top 15 Cards) rispetto al bucket precedente.
----------------------------------------------------------------------------------------------------
BUCKET     | N. DECKS | TRANSITION | DOMINANT CARDS (Anomalie)
----------------------------------------------------------------------------------------------------
5400-5550  | 142      | 0.12       | Mini P.E.K.K.A (+2.1@$\sigma$@), Tombstone (+2.4@$\sigma$@)
5550-5700  | 157      | 0.24       | Skeleton Army (+2.1@$\sigma$@)
5700-5850  | 103      | 0.24       | Goblin Curse (+2.3@$\sigma$@), Goblin Giant (+2.5@$\sigma$@), Sparky (+2.2@$\sigma$@), Skeleton King (+3.0@$\sigma$@), Goblins (+2.8@$\sigma$@)
5850-6000  | 151      | 0.42       | Bomb Tower (+2.8@$\sigma$@), Zappies (+2.2@$\sigma$@)
 ...       | ...      | ...        | ...
\end{minted}
\label{lst:test-micro-meta}
\end{listing}

I risultati mostrano variazioni nette nella composizione del meta tra le varie fasce, con valori di transizione anche superiori a 0.5 (cioè la metà delle carte utilizzate è diverso), coerente con l'ipotesi che la variazione del matchup derivi dal cambio del meta.

\subsubsection{Analisi conclusiva}

Infine, si è voluto verificare che a parità di trofei e di orario uno specifico mazzo non porti a incontrare mazzi avversari diversi.

\begin{listing}[t]
\caption{Risultato test dipendenza tra archetipi player e archetipi avversari}
\begin{minted}[
    frame=lines,
    framerule=0.8pt,
    fontsize=\footnotesize,
    breaklines
  ]{text}
Totale Battaglie Analizzate: 8093

Bucket: 4500-6000 | Orario: 00:00-08:00 | Players: 6 | Battles: 195
Matrice: [Righe = 5 (Tuoi Archetipi)] x [Colonne = 4 (Archetipi Avversari)]
P-value: 0.631797 -> NON SIGNIFICATIVO -> FAIR (Indipendenza)
--------------------------------------------------------------------------------
Bucket: 4500-6000 | Orario: 08:00-16:00 | Players: 6 | Battles: 311
Matrice: [Righe = 10 (Tuoi Archetipi)] x [Colonne = 15 (Archetipi Avversari)]
P-value: 0.603072 -> NON SIGNIFICATIVO -> FAIR (Indipendenza)
--------------------------------------------------------------------------------
Bucket: 4500-6000 | Orario: 16:00-24:00 | Players: 6 | Battles: 560
Matrice: [Righe = 16 (Tuoi Archetipi)] x [Colonne = 20 (Archetipi Avversari)]
P-value: 0.099683 -> NON SIGNIFICATIVO -> FAIR (Indipendenza)
--------------------------------------------------------------------------------
...

================================================================================
Totale Bucket Testati: 14
Bucket con Dipendenza Significativa: 1
Percentuale Sospetta: 7.14%
================================================================================
\end{minted}
\label{lst:test-fairness}
\end{listing}

Abbiamo utilizzato il test $\chi^2$ su una tabella di contingenza tra archetipi player e archetipi avversari.

Su 14 bucket analizzati:

\begin{itemize}
    \item 13 risultano non significativi
    \item 1 risulta significativo (7.14\%)
\end{itemize}

La percentuale di bucket significativi è compatibile con la probabilità di errore di tipo I attesa con soglia 0.05.

\subsubsection{Interpretazione finale}

A seguito dei test abbiamo riscontrato la presenza di dipendenza tra matchup successivi che suggerisce una memoria nella sequenza.

Memoria che tuttavia è compatibile con la variazione del meta locale osservata nelle varie fasce di trofei.

Visto anche il risultato dell'analisi della distribuzione dei mazzi avversari non abbiamo alcuna evidenza che il sistema assegni deliberatamente counter specifici in funzione del mazzo utilizzato.

\subsection{H2: Indipendenza dai livelli}

L'ipotesi H2 è speculare alla precedente ma riguarda i livelli.

Anche in questo caso l'analisi è stata condotta in tre fasi:

\begin{itemize}
    \item analisi delle transizioni tramite le catene di markov
    \item verifica della dipendenza rispetto a orario, trofei e mazzo
    \item analisi delle streak anomale tramite normalizzazione
\end{itemize}

\subsubsection{Analisi catene di markov}

Come prima il dataset è stato suddiviso in tre categorie:

\begin{itemize}
    \item Svantaggio (Disadvantage): $\text{lvl diff} < -0.5\%$
    \item Neutro (Even): $-0.5\% \leq \text{lvl diff} \leq 0.5\%$
    \item Vantaggio (Advantage): $\text{lvl diff} > 0.5\%$
\end{itemize}

E analogamente è stata costruita la matrice di transizione.

\begin{listing}[t]
\caption{Risultato test markov per indipendenza dei matchup no lvl}
\begin{minted}[
    frame=lines,
    framerule=0.8pt,
    fontsize=\footnotesize,
    breaklines
  ]{text}
--- 3. LEVEL DIFFERENCE ---
Totale Transizioni: 5534
--------------------------------------------------------------------------
PREC.  | NEXT: Disadvantage  | NEXT: Even          | NEXT: Advantage                
--------------------------------------------------------------------------
Disad. | 46.5% (Exp 16.0%) ! | 48.5% (Exp 69.6%) ! | 5.1% (Exp 14.4%) !  | 
Even   | 11.5% (Exp 16.0%)   | 75.2% (Exp 69.6%) ! | 13.4% (Exp 14.4%)   | 
Ad.    | 4.1% (Exp 16.0%) !  | 66.2% (Exp 69.6%)   | 29.7% (Exp 14.4%) ! | 
-----------------------------------------------------------------
Test Chi-Quadro: p-value = 0.000000
RISULTATO: DIPENDENZA SIGNIFICATIVA (Memoria presente).
\end{minted}
\label{lst:test-markov-lvl-diff}
\end{listing}

I risultati ottenuti sono molto simili all'ipotesi precedente, con un livello di significatività ben sotto la soglia di indipendenza.
Come prima emerge una memoria nella sequenza.

\subsubsection{Dipendenza dai treofei}

Ovviamente prima di continuare dobbiamo verificare alcune possibili correlazioni significative:

\begin{itemize}
    \item livello medio carte avversario e trofei
    \item livello medio carte giocatore e trofei
    \item livello medio carte giocatore e avversario
    \item livello torri e livello carte
\end{itemize}

\begin{listing}[t]
\caption{Analisi correlazione livelli}
\begin{minted}[
    frame=lines,
    framerule=0.8pt,
    fontsize=\footnotesize,
    breaklines
  ]{text}
Opponent Avg Deck Level vs Trophies:      Corr=0.9594, p=0.0000
Player Avg Deck Level vs Trophies:        Corr=0.9665, p=0.0000
Player Deck Level vs Opponent Deck Level: Corr=0.9370, p=0.0000
Player Tower Level vs Player Deck Level:  Corr=0.9189, p=0.0000
Player Tower Level vs Opponent Tower Level: Corr=0.9013, p=0.0000
-> MATCHMAKING EQUILIBRATO: I livelli carte player/opponent sono fortemente legati.
   (Probabilmente mediato dal Livello Torre, usato dal matchmaking).
\end{minted}
\label{lst:correlation-lvl}
\end{listing}

Tutte le correlazioni sono molto forti ($\rho>0.90$).
Per cui i livelli tendono a crescere lungo la scala dei trofei (più sali e più i livelli degli avversari sono maggiori). 
Ma non solo, le correlazioni tra livello dei giocatori e livelli degli avversari ci fa capire che il sistema è strutturalmente equilibrato, verosimilmente a causa della relazione tra livello delle torri e livello medio delle carte del mazzo.

\subsubsection{Analisi per fasce di trofei}

La dipendenza osservata può essere ulteriormente compatibile con una dipendenza a livello di orario.

Come prima segmentiamo il dataset in fasce di trofei e controlliamo un eventuale dipendenza.

Nella maggior parte dei bucket risulta non significativa.

Prima di concludere questa sezione affrontiamo un discorso un po più complesso, che comprende un ultimo tipo di dipendenza testata, quella tra il livello medio delle carte dell'avversario e il nostro mazzo.

Analizzando i dati, emerge un netto cambio di comportamento intorno ai 5000 trofei. Mentre inizialmente non vediamo alcuna relazione, dopo questa soglia i test diventano significativi.

Questo, al contrario di quanto ci aspetti, non significa necessariamente che il gioco decide il livello degli avversari in base alle mie carte. 

Il fatto che la variazione avviene dopo un certo punto è cruciale nella nostra interpretazione. Ad alti trofei troviamo generalmente due tipi di giocatori. Quelli con mazzi meta, che riescono a scalare anche avendo livelli più bassi e quelli con mazzi normali che, nonostante abbiano livelli superiori si trovano bloccati.

Il nostro mazzo diventa quindi indirettamente un buon predittore dei livelli avversari.

\subsubsection{Analisi streak di partite con svantaggio di livelli normalizzati}

Per eseguire i test con il $p^3$ e gli shuffle abbiamo bisogno di normalizzare la differenza di livelli rispetto ai trofei.

Mentre nel matchup no lvl non era necessario perchè in quel caso non esiste una correlazione tra matchup no lvl e trofei, quì risulta indispensabile.

la normalizzazione è avvenuta tramite lo z-score: 
\[
Z = \frac{Diff - \mu_{bucket}}{\sigma_{bucket}}
\]

In questo modo confrontiamo la differenza eliminando dall'equazione la crescita dovuta ai trofei.

Sono state considerate come anomalie le partite con $Z < -2$.

\begin{listing}[t]
\caption{Analisi streak matchup estremi}
\begin{minted}[
    frame=lines,
    framerule=0.8pt,
    fontsize=\footnotesize,
    breaklines
  ]{text}
ANALISI STREAK LIVELLI NORMALIZZATI (Z-SCORE)
Metodo: Normalizzazione per fascia trofei (Bucket 200). Z = (Diff - Mean) / Std.
Obiettivo: Rilevare anomalie di matchmaking indipendenti dalla progressione naturale.
================================================================================
Soglia Z-Score (Svantaggio Anomalo): < -2
Totale Opportunità: 4076
--------------------------------------------------------------------------------
METODO                    | STREAK COUNT    | RATIO     
--------------------------------------------------------------------------------
Osservato                 | 7               | 1.00x
Global Shuffle            | 2.44            | 2.86x
Intra-Session Shuffle     | 6.33            | 1.11x
--------------------------------------------------------------------------------
INTERPRETAZIONE:
1. Ratio Global > 1: Le partite 'sfortunate' sono raggruppate in sessioni specifiche (Bad Sessions).
2. Ratio Intra > 1: L'ordine delle partite nella sessione è manipolato per creare filotti negativi.
================================================================================     
\end{minted}
\label{lst:test-lvl-streak}
\end{listing}

Il numero osservato di streak (7) risulta superiore a quello ottenuto tramite global shuffle (2.44), ma molto vicino a quello ottenuto tramite intra-session shuffle (6.33).

Questi dati ci portano a pensare che le partite con svantaggi anomali tendono a concentrarsi in specifiche sessioni. L'ordine interno invece non presenta anomalie significative.

Non emergono quindi evidenze robuste di manipolazione sequenziale dell’assegnazione dei livelli.

\subsubsection{Interpretazione fionale}
Nel complesso, pur emergendo una memoria statistica nella sequenza delle differenze di livello, l’elevata correlazione con i trofei e l’assenza di anomalie interne alle sessioni suggeriscono che tale dipendenza sia compatibile con la struttura del sistema di progressione, piuttosto che con un intervento sequenziale deliberato.

\subsection{H3: presenza di un sistema EOMM}

Per verificare se il matchup della partita $t+1$ dipende dal risultato della parita $t$ o dalla situazione in cui ci troviamo abbiamo eseguito i seguenti test:

\begin{itemize}
    \item test $\chi^2$ applicato sulla matrice di transizione di markov
    \item test $\chi^2$ singoli per ogni giocatore
\end{itemize}

Analogamente alle matrici costruite nelle ipotesi precedenti dividiamo il matchup (comprensivo di livelli) in tre categorie:
\begin{itemize}
    \item Sfavorevole (Unfavorable): $\text{matchup} < 45\%$
    \item Neutro (Even): $45\% \leq \text{matchup} \leq 55\%$
    \item Favorevole (Favorable): $\text{matchup} > 55\%$
\end{itemize}

e l'outcome della partita precedente in due categorie:
\begin{itemize}
    \item sconfitta (lose)
    \item vittoria (win)
\end{itemize}

\begin{listing}[t]
\caption{Risultato test markov per indipendenza dei matchup no lvl}
\begin{minted}[
    frame=lines,
    framerule=0.8pt,
    fontsize=\footnotesize,
    breaklines
  ]{text}
Totale Transizioni: 5532
-------------------------------------------------------------------------
STATO PREC. | NEXT: Unfavorable | NEXT: Even        | NEXT: Favorable                
-------------------------------------------------------------------------
Loss        | 40.4% (Exp 41.8%) | 20.7% (Exp 20.7%) | 38.9% (Exp 37.5%) | 
Win         | 42.9% (Exp 41.8%) | 20.7% (Exp 20.7%) | 36.5% (Exp 37.5%) | 
-------------------------------------------------------------------------
\end{minted}
\label{lst:test-markov-outcome-matchup}
\end{listing}

In questo caso non riscontriamo alcuna memoria nel sistema. 
Poiché questo tipo di sistema non avrebbe gli stessi effetti su tutti i player abbiamo eseguito un test $\chi^2$ per ogni giocatore, confrontando questa volta la situazione in cui si trovava. 
Ovvero:
\begin{itemize}
    \item tre o più sconfitte consecutive (losing streak)
    \item nessuna streak (no streak)
    \item tre o più vittorie consecutive (winning streak) 
\end{itemize} 

Eseguendo i vari test abbiamo ottenuto un numero di risultati significativi pari a 4, rispetto ai 40 giocatori analizzati. 

Generalmente ci aspetteremmo un numero di falsi positivi sul totale dei giocatori pari al 5\%, ovvero 2.

Nonostante troviamo il doppio dei risultati questi sono al limite della significatività. 

Applicando la correzione per test multipli (Bonferroni) otteniamo come nuova soglia di significatività $\alpha = 0.05/40 = 0.00125$. 

Nessuno dei risultati si avvicina minimamente a questa soglia, per cui il risultato è puramente frutto del caso.

In alcune dette tabelle però erano presenti delle celle con frequenze inferiori a 5.

Poiché in tali condizioni l'approssimazione del $\chi^2$ può non essere affidabile abbiamo deciso di eseguire un ultimo test di Fischer exact come verifica di robustezza.

Anche questo test ha portato a risultati analoghi.

\subsubsection{Interpretazioni finali}

Dati i risultati ottenuti possiamo affermare con buona certezza che nel sistema di matchmaking non viene considerato in alcun modo il risultato delle partite precedenti.

\subsection{H4: SBMM}

Esclusa la possibilità di un sistema di tipo EOMM ci rimane un ultima ipotesi da verificare; la presenza, all'interno del matchmaking, di un indicatore MMR nascosto utilizzato per l'accoppiamento dei giocatori.

A tale scopo vogliamo ricercare nei nostri dati tre delle meccaniche peculiari di tale sistema, utilizzando i seguenti metodi:
\begin{itemize}
    \item presenza di meccanismi di debito/credito, verificando le differenze tramite il Test Mann-Whitney U
    \item persistenza del debito anche in sessioni successive, sempre utilizzando il Test Mann-Whitney U
    \item presenza di una fase di hook all'inizio delle sessioni, testata tramite Test Wilcoxon
\end{itemize}

\subsubsection{Meccanismi di debito/credito}

Per verificare la presenza di tali meccanismi abbaiamo calcolato il matchup medio delle partite successive ad una con matchup estremamente sfavorevole, dividendole in base al risultato di tale partita.

In un sistema di tipo SBMM la vittoria di una partita fortemente sfavorevole dovrebbe portare ad una partita ancora sfavorevole (debito). Perdendola invece la stima dovrebbe riassestarsi, riportando ad un matchup più equo.

La stessa cosa vale per il credito ma all'opposto.

\begin{listing}[t]
\caption{Risultato test debito/credito}
\begin{minted}[
    frame=lines,
    framerule=0.8pt,
    fontsize=\footnotesize,
    breaklines
  ]{text}
ANALISI COMBINATA DEBITO/CREDITO
Include: Debt Extinction, Favorable Outcome Impact.
================================================================================

PARTE 1: ESTINZIONE DEBITO (MMR DEBT)
Ipotesi: Vincere un matchup sfavorevole NON estingue il debito. Perdere lo estingue.
Definizione Unfavorable: Matchup < 45.0%
---------------------------------------------------------------
ESITO MATCH PRECEDENTE         | N      | NEXT MATCHUP (Avg)  
Unfavorable + WIN (Debito?)    | 962    | 42.71               %
Unfavorable + LOSS (Pagato?)   | 1264   | 45.86               %
Delta: -3.15%
Test Mann-Whitney U (Win < Loss): p-value = 0.0000

COMPONENTI DEL MATCHUP SUCCESSIVO:
1. Level Diff: Win=-0.22 vs Loss=-0.14 (Delta: -0.08, p=0.0004)
2. Matchup No-Lvl: Win=48.06% vs Loss=48.73% (Delta: -0.67%, p=0.1708)

CONTROLLI DI VALIDITÀ:
Matchup Iniziale (Avg): Win=33.85% vs Loss=31.27%
Elixir Advantage (Win): +2.42

====================================================================================

PARTE 2: IMPATTO ESITO SU MATCHUP FAVOREVOLE
Domanda: Come reagisce il sistema quando vinci o perdi una partita che 'dovevi' vincere?
Definizione Favorable: Matchup > 55.0%
----------------------------------------------------------------
ESITO MATCH PRECEDENTE         | N      | NEXT MATCHUP (Avg)  
Favorable + WIN (Atteso)       | 1533   | 52.93               %
Favorable + LOSS (Inatteso)    | 597    | 56.01               %
Delta: -3.08%
Test Mann-Whitney U (Diff Significativa): p-value = 0.0002

COMPONENTI DEL MATCHUP SUCCESSIVO:
1. Level Diff: Win=+0.11 vs Loss=+0.15 (Delta: -0.04, p=0.1315)
2. Matchup No-Lvl: Win=49.56% vs Loss=50.43% (Delta: -0.87%, p=0.1618)
Elixir Advantage (Loss): -0.45

======================================================================================
\end{minted}
\label{lst:test-debt}
\end{listing}

I risultati ottenuti evidenziano una variazione sistematica nei matchup.

Nel caso di matchup inizialmente sfavorevole (<45\%), la vittoria è seguita da un matchup medio del 42.71\%, mentre la sconfitta porta ad un valore medio del 45.86\%.  
La differenza (−3.15\%) risulta altamente significativa (p < 0.001).

Un comportamento analogo emerge nel caso dei matchup favorevoli (>55\%).  
Dopo una vittoria il matchup medio scende a 52.93\%, mentre dopo una sconfitta sale a 56.01\%, con una differenza significativa (p < 0.001).

A prima vista questi pattern sono compatibili con un meccanismo di compensazione:  
vincere una partita inattesa è seguito da una partita con alta difficoltà, mentre perderla porta ad un matchup più equo.


\textbf{Regressione verso la media}

A prima vista, il riavvicinamento dei valori verso una soglia più neutrale potrebbe far pensare a una semplice \textbf{regressione verso la media}. Tuttavia, un'analisi più attenta delle condizioni iniziali smentisce questa ipotesi.

Osservando i dati di partenza, notiamo che il gruppo che ha poi vinto la partita si trovava in una condizione iniziale leggermente migliore (matchup medio 33.85\%) rispetto al gruppo che ha perso (31.27\%), con un delta positivo di circa +2.58\%.

Se il fenomeno fosse governato esclusivamente dalla regressione statistica, ci aspetteremmo che questa differenza si mantenga o si riduca nel match successivo, ma senza invertire il proprio segno: chi partiva da una condizione migliore dovrebbe, in media, atterrare su una condizione migliore o uguale.

I dati mostrano invece l'opposto: nel match successivo, il gruppo dei vincitori crolla a un livello inferiore (42.71\%) rispetto a quello degli sconfitti (45.86\%), ribaltando il delta a -3.15\%.

Questa inversione di segno — dove chi partiva avvantaggiato finisce svantaggiato solo perché ha vinto — è incompatibile con la pura regressione verso la media e costituisce un forte indizio di un intervento attivo del sistema (aggiornamento della stima di skill).

\textbf{Scomposizione in componenti}

L'analisi precedente è stata eseguita considerando il matchup complessivo ma le due componenti agiscono in modo diverso?

Questa scomposizione mostra come, nel caso del debito, la variazione sia principalmente guidata dai livelli (p=0.0004), mentre la componente del mazzo risulta non significativa (p=0.170).

Nel caso del credito, nonostante si osserva una variazione complessiva significativa, entrambe le componenti non risultano significative.

Questo può essere spiegato da una possibile asimmetria strutturale della ladder: salendo di trofei è più probabile incontrare giocatori con livelli superiori, mentre scendendo la riduzione della difficoltà può manifestarsi più attraverso differenze di skill che di livelli.

\textbf{Ruolo della performance dei giocatori}

L'analisi dell'elisir leaked rafforza l'ipotesi fatta poco fa.

Mentre nel caso del debito la vittoria la differenza risulta di +2.42, nel caso del credito questa è di -0.45.

I dati suggeriscono che la vittoria nel caso del debito sia strettamente legata a gravi errori da parte dell'avversario più che a una superiorità in termini di bravura.

Un sistema che aggiorna la stima di skill principalmente sulla base dell’esito potrebbe quindi reagire in modo marcato anche a vittorie “anomale”.

% rimando al test sul peso della sconfitta? va inserito?
questo risultato è ulteriormente rafforzato dal risultato del test X presente in appendice. dove si dimostra che la qualità della sconfitta non influenza il matchup della partita successiva. Sconfitte nette (0-3) non portano a matchup più favorevoli rispetto a sconfitte combattute (p=0.9854). Inoltre la media di elisir leaked nelle sconfitte, pari a 7, dimostra che molte crushing lose sono causate da quit del giocatore. 

\textbf{Relazione con i trofei}

Prima di riportare le considerazioni finali dobbiamo fare un ultima analisi. 
Nella prima ipotesi avevamo visto come i livelli delle carte varia in modo significativo con il numero di trofei. 
Per eliminare questo fattore abbiamo calcolato il livello medio degli avversari nelle varie fasce di trofei (in bucket da 100 trofei), calcolando poi l'incremento per singola fascia e l'incremento medio totale.

Il risultato mostra un aumento medio di $+0.0971$ livelli.

Con questo dato è stato eseguito nuovamente il test precedente, confrontando il livello medio nel caso di sconfitta e nel caso di vittoria e verificando il delta rispetto all'incremento medio registrato.

Ma non solo, per avere un risultato più robusto, è stato sottratto ad ogni partita la variazione specifica della fascia di trofei in questione, ottenendo così l'effetto "pulito". 

\begin{listing}[t]
\caption{Risultato test variazione livelli rispetto alla media}
\begin{minted}[
    frame=lines,
    framerule=0.8pt,
    fontsize=\footnotesize,
    breaklines
  ]{text}
ANALISI VOLATILITÀ LIVELLI POST-DEBT (WIN vs LOSE)
Obiettivo: Verificare se il livello dell'avversario cambia coerentemente con i trofei dopo una vittoria 'Heroic' o una sconfitta in Debt.
Condizione Debt: Matchup < 45%.
Condizione Controllo: Il mazzo del giocatore deve rimanere invariato tra i due match.
================================================================================

BASELINE GLOBALE:
Aumento medio livello avversario per 100 trofei: 0.0838
Variazione attesa per swing di ~60 trofei (+30 vs -30): 0.0503 livelli
--------------------------------------------------------------------------------

TEST 1: LIVELLI ASSOLUTI (Raw Opponent Level)
Dopo Heroic Win (N=931): 13.5275
Dopo Debt Lose  (N=1144): 13.2991
Delta Rilevato: +0.2284
Delta Atteso (~60 trofei): +0.0503
Differenza dal modello naturale: +0.1781
Significatività statistica (T-test): p=0.00990
>> ANOMALIA: La variazione di livello è ECCESSIVA rispetto alla sola differenza di trofei.

--------------------------------------------------------------------------------

TEST 2: ANALISI RESIDUI (Opp Level - Avg Level @ Trophies)
Questo test rimuove l'effetto 'trofei' per vedere se il matchmaking 'punisce' o 'aiuta' relativamente alla fascia.
Residuo Medio dopo Heroic Win: +0.0387
Residuo Medio dopo Debt Lose:  -0.0087
Delta Residui: +0.0474
Significatività (T-test): p=0.00829
>> RISULTATO: Dopo una vittoria, affronti avversari RELATIVAMENTE più forti rispetto alla media della fascia (Punizione/Challenge).
================================================================================
\end{minted}
\label{lst:test-lvl-volability}
\end{listing}

In entrambi i test abbiamo ottenuto un risultato significativo, dimostrando che l'effetto rimane presente indipendentemente dall'effetto "scalata"

\textbf{Interpretazione finale}

Nel complesso, l’effetto osservato:

\begin{itemize}
    \item è significativo;
    \item presenta una direzione non coerente con la sola regressione verso la media;
    \item è mediato prevalentemente dalla componente livelli;
    \item è compatibile con un aggiornamento non simmetrico della stima di skill.
\end{itemize}

L’evidenza risulta quindi coerente con un sistema di tipo SBMM implementato indirettamente tramite modulazione dei livelli degli avversari, piuttosto che attraverso una manipolazione diretta del matchup strutturale del deck.

\subsubsection{Persistenza del debito/credito}

Un'analisi molto interessante e particolarmente correlata ai punti ache abbiamo appena affrontato riguarda la continuazione del debito (o del credito) anche in sessioni diverse.

In un sistema che calcola e tiene in considerazione l'MMR lo stato in cui si trova il giocatore dovrebbe continuare anche in sessioni diverse. 

Per verificare tale fenomeno le sessioni sono state divise in tre gruppi:
\begin{itemize}
    \item terminate con due o più matchup sfavorevoli (bad streak)
    \item terminate in uno stato neutro (control)
    \item terminate con due o più matchup favorevoli (good streak)
\end{itemize}

Infine per ognuna di queste è stata presa la media del primo matchup della sessione successiva. 
Il matchup per le sessioni good e bad sono poi state confrontate con quella control tramite test Mann-Whitney U.

Per isolare il fattore mazzo e ladder l'analisi è stata eseguita dividendo il matchup no lvl dai livelli e analizzato il residuo dopo la normalizzazione 

\begin{listing}[t]
\caption{Risultato persistenza del debito/credito}
\begin{minted}[
    frame=lines,
    framerule=0.8pt,
    fontsize=\footnotesize,
    breaklines
  ]{text}
ANALISI RETURN MATCHUP DOPO BAD/GOOD STREAK (DETTAGLIO COMPONENTI & RESIDUI)
Domanda: Se un giocatore chiude la sessione dopo una serie di matchup estremi,
         al ritorno viene 'punito'/'aiutato' (memoria) o il sistema si resetta (coin flip)?
         Analisi componenti: Matchup Reale vs No-Lvl (Deck) vs Level Diff vs RESIDUO.
         RESIDUO = Level Diff Osservato - Level Diff Atteso per la fascia trofei.
         (Serve a isolare l'effetto 'Climbing' dall'effetto 'MMR/Punizione').
Definizione Bad Streak: Ultimi 2 match con Matchup < 45.0%
Definizione Good Streak: Ultimi 2 match con Matchup > 55.0%
Definizione Control: Nessuna streak attiva (Matchup misti o neutri)
====================================================================================================

--- STOP TYPE: Short (20 min <= T < 2 ore) ---
Condizione      | N     | Matchup    | No-Lvl     | Lvl Diff   | RESIDUO (Netto)
------------------------------------------------------------------------------------------
Bad Streak      | 112   | 40.62     % | 46.33     % | -0.20      | -0.1991        
Good Streak     | 96    | 58.37     % | 52.08     % | 0.19       | 0.2013         
Control         | 568   | 51.35     % | 49.11     % | 0.05       | 0.0462         
------------------------------------------------------------------------------------------
1. Bad Streak vs Control (RESIDUO):
   Delta Residuo: -0.2453
   Test Mann-Whitney U (Bad < Control): p-value = 0.0000
   -> SIGNIFICATIVO. La punizione persiste anche normalizzando per i trofei.
      (Fortemente compatibile con MMR nascosto).

2. Good Streak vs Control (RESIDUO):
   Delta Residuo: +0.1551
   Test Mann-Whitney U (Good > Control): p-value = 0.0248
   -> SIGNIFICATIVO. Vantaggio persistente oltre i trofei.
      (Compatibile con MMR).

--- STOP TYPE: Long (2 ore <= T < 20 ore) ---
Condizione      | N     | Matchup    | No-Lvl     | Lvl Diff   | RESIDUO (Netto)
------------------------------------------------------------------------------------------
Bad Streak      | 151   | 41.77     % | 49.65     % | -0.32      | -0.2354        
Good Streak     | 132   | 58.65     % | 51.26     % | 0.21       | 0.2485         
Control         | 894   | 50.96     % | 49.49     % | 0.03       | 0.0622         
------------------------------------------------------------------------------------------
1. Bad Streak vs Control (RESIDUO):
   Delta Residuo: -0.2976
   Test Mann-Whitney U (Bad < Control): p-value = 0.0000
   -> SIGNIFICATIVO. La punizione persiste anche normalizzando per i trofei.
      (Fortemente compatibile con MMR nascosto).

2. Good Streak vs Control (RESIDUO):
   Delta Residuo: +0.1862
   Test Mann-Whitney U (Good > Control): p-value = 0.0010
   -> SIGNIFICATIVO. Vantaggio persistente oltre i trofei.
      (Compatibile con MMR).

--- STOP TYPE: Quit (T >= 20 ore) ---
Condizione      | N     | Matchup    | No-Lvl     | Lvl Diff   | RESIDUO (Netto)
------------------------------------------------------------------------------------------
Bad Streak      | 53    | 42.71     % | 52.77     % | -0.46      | -0.3493        
Good Streak     | 62    | 61.42     % | 49.45     % | 0.35       | 0.3377         
Control         | 323   | 51.39     % | 51.23     % | -0.00      | 0.0441         
------------------------------------------------------------------------------------------
1. Bad Streak vs Control (RESIDUO):
   Delta Residuo: -0.3934
   Test Mann-Whitney U (Bad < Control): p-value = 0.0000
   -> SIGNIFICATIVO. La punizione persiste anche normalizzando per i trofei.
      (Fortemente compatibile con MMR nascosto).

2. Good Streak vs Control (RESIDUO):
   Delta Residuo: +0.2936
   Test Mann-Whitney U (Good > Control): p-value = 0.0004
   -> SIGNIFICATIVO. Vantaggio persistente oltre i trofei.
      (Compatibile con MMR).

====================================================================================================
\end{minted}
\label{lst:test-debt-persistance}
\end{listing}

In tutti i test abbiamo ottenuto risultati significativi e soprattutto coerenti nel tempo. 
Non sembrerebbe quindi che il matchup al ritorno da una bad o good streak ritorni verso l'equità.

Il fenomeno è principalmente spiegato dalla differenza dei livelli e non completamente attribuibile alla scalata.

\textbf{Interpretazione dei risultati}

Anche se i risultati sono forte indizio della presenza di un MMR nascosto non è possibile escludere che il comportamento sia causato da fattori non presi in considerazione in questa analisi (ad esempio fattori di rete).

\subsubsection{Hook effect}

I sistemi di matchmaking basati sulla skill che includono nel loro funzionamento l'incertezza tendono ad avere dei dubbi sulla stima del giocatore.

Questo si traduce spesso nel cosiddetto hook effect. All'inizio della sessione l'incertezza è alta, per cui il sistema tende a dare al giocatore dei matchup più favorevoli, per poi tornare alla normalità una volta ridotta l'incertezza.

Per testarlo abbiamo usato ancora una volta il test Wilcoxon, confrontando il matchup medio delle prime partite rispetto alle ultime, e successivamente anche confrontando il matchup delle prime partite rispetto al resto della sessione.

\begin{listing}[t]
\caption{Risultato test hook effect}
\begin{minted}[
    frame=lines,
    framerule=0.8pt,
    fontsize=\footnotesize,
    breaklines
  ]{text}
ANALISI TREND INTRA-SESSIONE (HOOK & FRUSTRATION)
Obiettivo: Verificare se le sessioni iniziano con vittorie/matchup facili (Hook) e finiscono con sconfitte/matchup difficili (Frustration/Churn).
Criteri: Sessioni con almeno 4 partite. Confronto Primi k vs Ultimi k match.
================================================================================

Totale Sessioni Analizzate: 735
--------------------------------------------------------------------------------
1. WIN RATE (Inizio vs Fine)
   Media Win Rate INIZIO: 59.12%
   Media Win Rate FINE:   52.54%
   Delta:                 -6.58%
   Test Wilcoxon (Inizio > Fine): p-value = 0.0001
   RISULTATO: SIGNIFICATIVO. I giocatori vincono significativamente di più all'inizio della sessione.

2. MATCHUP QUALITY (Inizio vs Fine)
   Media Matchup INIZIO: 50.17%
   Media Matchup FINE:   48.56%
   Delta:                -1.62%
   Test Wilcoxon (Inizio > Fine): p-value = 0.0020
   RISULTATO: SIGNIFICATIVO. I matchup sono significativamente migliori all'inizio della sessione.

3. MATCHUP NO-LVL (Fair Play) (Inizio vs Fine)
   Media Matchup No-Lvl INIZIO: 49.08%
   Media Matchup No-Lvl FINE:   49.05%
   Delta:                       -0.03%
   Test Wilcoxon (Inizio > Fine): p-value = 0.4611
   RISULTATO: NON SIGNIFICATIVO.

4. LEVEL DIFFERENCE (Inizio vs Fine)
   Media Level Diff INIZIO: +0.00
   Media Level Diff FINE:   -0.05
   Delta:                   -0.05
   Test Wilcoxon (Inizio > Fine): p-value = 0.0001
   RISULTATO: SIGNIFICATIVO (Livelli peggiori alla fine)
\end{minted}
\label{lst:test-hook-effect}
\end{listing}


\begin{listing}[t]
\caption{Risultato test hook effect}
\begin{minted}[
    frame=lines,
    framerule=0.8pt,
    fontsize=\footnotesize,
    breaklines
  ]{text}
================================================================================
ANALISI 2: HOOK PHASE (Primi 3) vs RESTO DELLA SESSIONE
Obiettivo: Verificare se le prime partite sono sistematicamente più facili del resto della sessione.
Criteri: Sessioni con > 3 partite. Confronto Primi 3 vs Rimanenti.
Sessioni valide per questo test: 735
--------------------------------------------------------------------------------
1. WIN RATE (Hook vs Resto)
   Media Win Rate HOOK (Primi 3): 59.68%
   Media Win Rate RESTO:          50.20%
   Delta:                         -9.48%
   Test Wilcoxon (Hook > Resto): p-value = 0.0000
   RISULTATO: SIGNIFICATIVO

2. MATCHUP QUALITY (Hook vs Resto)
   Media Matchup HOOK:  50.01%
   Media Matchup RESTO: 48.30%
   Delta:               -1.71%
   Test Wilcoxon (Hook > Resto): p-value = 0.0010
   RISULTATO: SIGNIFICATIVO

3. MATCHUP NO-LVL (Hook vs Resto)
   Media Matchup No-Lvl HOOK:  49.18%
   Media Matchup No-Lvl RESTO: 48.87%
   Delta:                      -0.31%
   Test Wilcoxon (Hook > Resto): p-value = 0.1632
   RISULTATO: NON SIGNIFICATIVO

4. LEVEL DIFFERENCE (Hook vs Resto)
   Media Level Diff HOOK:  -0.00
   Media Level Diff RESTO: -0.05
   Delta:                  -0.05
   Test Wilcoxon (Hook > Resto): p-value = 0.0005
   RISULTATO: SIGNIFICATIVO (Livelli peggiori nel resto)
\end{minted}
\label{lst:test-hook-effect-2}
\end{listing}

I seguenti risultati mostrano come ci sia un effettivo aumento del winrate nelle prime partite della sessione. Questo però non è solo causato come ci potremmo aspettare dalla maggiore concentrazione del giocatore, anche la variazione del matchup risulta significativa e come prima principalmente dovuta ai livelli.

Compatibile ancora una volta con un sistema di tipo skill based.
