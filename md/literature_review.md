# Riferimenti Bibliografici e Stato dell'Arte

Questa è una raccolta di riferimenti utili per inquadrare lo stato dell'arte nell'analisi dei sistemi di matchmaking.

---

### 1. Brevetti Fondamentali (La Prova Industriale)

**Titolo:** Engagement-Optimized Matchmaking (EOMM)
**Autori/Fonte:** Electronic Arts Inc. (Brevetto US20170259177A1)
**Descrizione:** Questo è il brevetto che ha dato il via al dibattito moderno. Descrive un sistema che non mira a creare partite "eque" (con 50% di win rate), ma a massimizzare il tempo di gioco (engagement). Lo fa analizzando il profilo del giocatore (es. tendenza al churn, spesa) e manipolando dinamicamente la difficoltà delle partite per ottimizzare la retention. È la prova che l'industria ha sviluppato e brevettato queste tecniche.
**Link:** [Google Patents](https://patents.google.com/patent/US20170259177A1/en)

**Titolo:** System and method for driving microtransactions in multiplayer video games
**Autori/Fonte:** Activision Publishing, Inc. (Brevetto US20160005270A1)
**Descrizione:** Un altro brevetto chiave che va oltre l'engagement. Ipotizza di abbinare giocatori con item premium (es. skin, armi) a giocatori che non li possiedono per incentivare l'acquisto. Se un giocatore "junior" viene abbinato a un "senior" con un'arma potente e viene sconfitto, potrebbe essere più propenso ad acquistare quell'arma. Questo dimostra che il matchmaking può essere usato come leva di monetizzazione.
**Link:** [Google Patents](https://patents.google.com/patent/US20160005270A1/en)

---

### 2. Ricerca Accademica e Analisi Dati

**Titolo:** TrueSkill(TM): A Bayesian Skill Rating System
**Autori:** Herbrich, R., Minka, T., & Graepel, T. (Microsoft Research)
**Descrizione:** Un paper fondamentale che descrive il sistema di rating usato da Xbox Live. A differenza dell'ELO (che funziona 1v1), TrueSkill modella la skill di ogni giocatore in un team e gestisce partite con più partecipanti. È un ottimo riferimento per spiegare come funzionano i sistemi di rating moderni e "onesti". Serve come baseline teorica da cui i sistemi EOMM si discostano.
**Link:** [Microsoft Research](https://www.microsoft.com/en-us/research/project/trueskill-ranking-system/)

**Titolo:** The rich get richer: a large-scale study of player skill and progression in online games
**Autori:** A. Drachen, C. M. Hall, M. C. Miller, A. N. T. Normoyle (Proceedings of the FDG 2014 Conference)
**Descrizione:** Sebbene non si concentri sul "rigging", questo studio analizza i dati di progressione di migliaia di giocatori in giochi come *Battlefield 3*. Mostra come la skill e il tempo di gioco si correlano e come i giocatori progrediscono. È un eccellente esempio di analisi di dati su larga scala per comprendere le dinamiche di gioco, molto simile al nostro approccio metodologico.
**Link:** [ResearchGate](https://www.researchgate.net/publication/262470068_The_rich_get_richer_a_large-scale_study_of_player_skill_and_progression_in_online_games)

**Titolo:** Churn Prediction in a Free-to-Play Game: A Case Study
**Autori:** A. Runge, J. Gao, R. Garcin, F. Faltings (IEEE Conference on Computational Intelligence and Games, 2014)
**Descrizione:** Questo paper si concentra sulla predizione del "churn" (abbandono del gioco). È rilevante perché l'obiettivo principale dell'EOMM è proprio ridurre il churn. Comprendere quali fattori portano un giocatore ad abbandonare (es. losing streak, frustrazione) aiuta a capire perché un publisher potrebbe essere tentato di implementare un matchmaking manipolativo.
**Link:** [IEEE Xplore](https://ieeexplore.ieee.org/document/6932866)

---

### 3. Fonti Industriali e Divulgative (GDC Talks)

**Titolo:** Player-Centric Matchmaking
**Autori/Fonte:** Josh Menke (GDC - Game Developers Conference)
**Descrizione:** Josh Menke è stato il principale designer del matchmaking per giochi come *Halo 5* e *Call of Duty*. In questo talk, spiega come un matchmaking "buono" debba bilanciare tre fattori: equità (skill), latenza (connessione) e tempi di attesa. Critica i sistemi puramente basati su ELO e introduce il concetto di "matchmaking percepito" (la sensazione di equità del giocatore). È una visione dall'interno dell'industria che contrasta con i brevetti più aggressivi.
**Link:** [GDC Vault](https://www.gdcvault.com/play/1024 matchmaking) (il link diretto può variare, ma la ricerca per titolo/autore è efficace)