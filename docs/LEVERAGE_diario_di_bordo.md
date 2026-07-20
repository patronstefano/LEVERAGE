# LEVERAGE - Diario di bordo tecnico e progettuale

Data documento: 24 giugno 2026  
Stato del progetto: backend locale avanzato, audit pre-Git completato, pre-popolamento massivo definitivo, pre-deploy online  
Ambiente di lavoro: workspace LEVERAGE in VS Code; percorso operativo rilevato durante l'audit: `/Users/patronstefano/Sviluppo/LEVERAGE`  
Scopo del documento: ricostruire ordinatamente il lavoro svolto dall'inizio del progetto LEVERAGE fino allo stato attuale, come diario di bordo utile per sviluppo, tesi magistrale e futura messa online.

---

## 1. Sintesi generale

LEVERAGE e una piattaforma backend API dedicata alla ginnastica artistica elite, con focus su MAG e WAG. Il progetto nasce per raccogliere, strutturare, validare, importare, consultare e analizzare dati relativi ad atleti, eventi e risultati.

La visione di lungo periodo e costruire una piattaforma web pubblica in cui chiunque possa consultare risultati ufficiali, cercare atleti, filtrare eventi, confrontare performance, visualizzare classifiche e usare grafici interattivi. In parallelo, gli utenti registrati potranno salvare preferenze personali, mentre gli admin avranno strumenti per data entry, import massivi, verifica dati, gestione suggerimenti e governo del database.

Il principio guida definito durante lo sviluppo e questo:

- LEVERAGE deve mostrare agli utenti dati ufficiali, approvati e semanticamente coerenti.
- Gli automatismi aiutano l'admin, ma non sostituiscono mai la convalida umana.
- I dati mancanti devono essere tracciati come `not available`, non inventati.
- Le regole sportive e i vincoli del modello devono essere espliciti nel backend.
- La UI futura dovra ricevere API gia pronte per filtri, classifiche, grafici, dashboard e suggerimenti.

Stack attuale:

- Python 3.10+
- FastAPI
- SQLAlchemy
- SQLite in locale/MVP
- Alembic per migrazioni
- Pydantic per schemi API
- JWT authentication
- autenticazione email/password con verifica email e MFA per admin
- Pytest per test automatici

Stato operativo attuale:

- backend funzionante in locale;
- Alembic configurato;
- 28 migrazioni presenti;
- 106 endpoint router rilevati;
- suite test passata nell'ultima verifica pre-Git: `99 passed`;
- file import storici 2018-2025 presenti in `import_files/`;
- cartella locale non ancora trasformata in repository Git;
- frontend non ancora implementato, ma backend gia orientato a supportarlo.

---

## 2. Visione del prodotto

La piattaforma finale e pensata come sito consultabile da chiunque. Un visitatore pubblico potra leggere e filtrare i dati senza obbligo di login. Un utente registrato potra personalizzare l'esperienza. Un admin potra gestire la qualita del dato.

Obiettivi principali:

- creare un archivio strutturato di ginnastica artistica elite;
- distinguere MAG e WAG in modo rigoroso;
- gestire atleti junior e senior;
- gestire eventi singola disciplina o doppia disciplina;
- gestire eventi singola categoria o doppia categoria;
- gestire risultati per evento, round, format, discipline, category e apparatus;
- generare classifiche evento coerenti;
- supportare analisi storiche dal 2018 in poi;
- supportare import massivi da file Gymternet;
- supportare in futuro file standardizzati dal 2026 in poi;
- aiutare gli admin nel completamento dei dati tramite suggerimenti;
- mantenere tracciabile cio che e stato creato, modificato, importato o suggerito.

La futura UI dovra essere pulita, intuitiva, orientata ai dati e non puramente descrittiva. Il backend e stato modellato proprio per fornire endpoint gia utilizzabili per:

- schede atleta;
- schede evento;
- dashboard utente;
- classifiche evento;
- confronti fra atleti;
- trend temporali;
- grafici per apparatus;
- grafici eta/country;
- notifiche;
- data entry manuale admin;
- import e revisione dati.

---

## 3. Diario di bordo ordinato

### Fase 1 - Fondazione del progetto

Il progetto e iniziato come backend API per ginnastica artistica. Sono state definite le prime entita centrali:

- `User`
- `Athlete`
- `Event`
- `Result`
- `FollowedAthlete`
- `SavedEvent`

La prima architettura prevedeva gia:

- lettura pubblica dei dati;
- scrittura riservata agli admin;
- login tramite email/password con verifica email;
- MFA obbligatoria per admin e super admin;
- token JWT;
- CRUD di base per atleti, eventi e risultati;
- preferenze utente.

In questa fase `Result` rappresentava gia il nucleo della piattaforma, cioe la performance sportiva collegata a un atleta e a un evento.

Decisione importante: mantenere il nome `Result`, non rinominarlo in `Performance`, per coerenza con il linguaggio usato nel database e nelle richieste successive.

### Fase 2 - Hardening infrastrutturale e Alembic

Dopo la prima implementazione, e stato deciso di consolidare l'infrastruttura prima di sviluppare analytics avanzate.

Sono stati introdotti:

- Alembic;
- migrazioni versionate;
- vincoli di database;
- test piu robusti;
- configurazione piu ordinata;
- separazione piu chiara fra modelli, schemi, router e logiche di servizio.

Questa fase e stata fondamentale per evitare che l'evoluzione del modello dati diventasse fragile. Ogni modifica successiva a entita e campi e stata poi accompagnata da migrazioni.

### Fase 3 - Ridefinizione semantica di Athlete, Event e Result

Sono state analizzate le entita principali e i relativi campi.

Per `Athlete`:

- e stato rimosso inizialmente il campo `status`;
- e stata mantenuta la distinzione `MAG` / `WAG`;
- e stata resa chiara la differenza fra dati anagrafici obbligatori e dati completabili in seguito.

Per `Event`:

- `discipline` puo essere `MAG`, `WAG`, oppure `MAG and WAG`;
- `category` puo essere `junior`, `senior`, oppure `junior and senior`;
- `MAG and WAG` e `junior and senior` non sono pensati come bottoni separati nella UI, ma come risultato della doppia selezione dei filtri;
- e stato chiarito che un evento puo ammettere una o piu discipline/categorie, mentre un singolo risultato deve sempre avere una sola disciplina e una sola categoria.

Per `Result`:

- `discipline` deve coincidere con la disciplina dell'atleta;
- la disciplina del risultato deve essere ammessa dall'evento;
- `category` puo essere solo `junior` o `senior`;
- la category del risultato deve essere ammessa dall'evento;
- e stato aggiunto `category` a `Result`;
- e stato aggiunto `day` per gestire gare su piu giornate;
- `rank` resta opzionale;
- se `rank` manca, la classifica viene ordinata per metrica, di default `score` decrescente.

Questa fase ha sistemato il cuore semantico del dominio.

### Fase 4 - Filtri e classifiche evento

E stata sviluppata la logica per permettere all'utente di selezionare un evento e filtrare i risultati associati.

Filtri supportati per le classifiche evento:

- `format`
- `round`
- `discipline`
- `category`
- `apparatus`
- `athlete`
- `data_quality`

La classifica risultante rappresenta i `Result` di quell'evento nel contesto selezionato.

Regola ordinamento:

- se `rank` e disponibile, puo essere usato come riferimento;
- se `rank` non e disponibile, si ordina per `score` dal maggiore al minore;
- in seguito sono state aggiunte anche metriche alternative: `D_score`, `E_score`, `Penalty`, `Bonus`, `execution_estimate`.

La UI futura dovra mostrare solo filtri realmente cliccabili. Per questo e stato creato un endpoint che restituisce solo i valori effettivamente presenti nei risultati dell'evento.

### Fase 5 - Apparatus e valori speciali

Sono stati definiti gli apparatus ammessi per MAG e WAG.

MAG:

- `FX`
- `PH`
- `SR`
- `VT`
- `PB`
- `HB`
- `AA`
- `VT AVG`

WAG:

- `VT`
- `UB`
- `BB`
- `FX`
- `AA`
- `VT AVG`

`AA` e `VT AVG` sono stati aggiunti esplicitamente per entrambe le discipline.

`VT AVG` rappresenta la media dei salti nel contesto vault, mentre `VT` rappresenta il singolo salto. Il campo `vt_attempt` puo indicare `1` o `2`, oppure essere `NULL`.

### Fase 6 - Data quality, score opzionali e `not available`

In origine i risultati avevano punteggi piu rigidi. Durante l'analisi dei file Gymternet e emerso che non sempre tutti i campi sono disponibili.

Sono quindi state prese queste decisioni:

- `D_score`, `E_score`, `Penalty`, `Bonus` sono opzionali;
- `score` e normalmente richiesto, ma oggi e nullable a database per gestire casi storici controllati;
- lato UI i valori `NULL` devono apparire come `not available`;
- i dati incompleti devono essere segnalati e filtrabili;
- i dati con `D_score` ma senza `score` sono generalmente poco utili e non devono popolare il database, salvo eccezioni controllate;
- i dati con `score` ma senza `D_score` possono essere utili e conservabili;
- `execution_estimate = score - D_score` puo essere calcolato quando entrambi i valori esistono;
- `execution_estimate` non e un E-score ufficiale e non viene salvato come dato ufficiale nel database.

Questa fase ha reso il backend adatto a distinguere dati completi, incompleti e parziali, senza falsificare la qualita del dato.

### Fase 7 - Regole Bonus

Sono state definite le regole relative al campo `Bonus`.

Dal 2018 al 2024:

- il bonus non era usato nel regolamento mondiale MAG/WAG;
- il campo `Bonus` deve restare `NULL`.

Dal 2025:

- WAG: `Bonus` esiste solo per `VT AVG` e puo assumere valore `0.2`;
- MAG: `Bonus` esiste solo per `FX`, `SR`, `VT`, `PB`, `HB` e puo assumere valore `0.1`;
- negli altri casi `Bonus` resta `NULL`;
- `NULL` significa non previsto o non applicato, non zero.

Il campo viene mantenuto perche le regole future potrebbero cambiare.

### Fase 8 - Regole Vault e problema VT1/VT2

Durante l'analisi dei file storici e emerso un problema importante sui vault.

Nei file Gymternet storici:

- `VT` indica un risultato di vault singolo;
- `VT AVG` indica la media dei due vault;
- `VT SUM` o `VT1+VT2` e una colonna sorgente relativa alla somma dei D-score dei due vault;
- l'ordine reale dei vault non e sempre certo;
- in alcune classifiche ufficiali `VT` puo riferirsi a quello che tecnicamente e il secondo vault e non il primo.

La regola attuale di import legacy e:

- per 2018-2024, si ricava un VT attempt 2 da `VT AVG` per final score e da `VT SUM` per D-score;
- per 2025 MAG, si procede nello stesso modo;
- per 2025 WAG, si ricava solo il D-score del VT attempt 2 da `VT SUM`, ma il final score resta `NULL` / `not available`, perche il bonus WAG 0.2 su `VT AVG` rende impossibile risalire con certezza al singolo score di VT2;
- `VT SUM` resta una colonna sorgente di import, non un valore salvato come apparatus nel database;
- i risultati vault derivati sono marcati con `vault_attempt_order_uncertain = true`;
- la UI futura dovra mostrare un piccolo avviso accanto a questi dati;
- messaggio previsto: "Si noti che Vault 1 puo riferirsi a Vault 2 e viceversa."

Questa scelta conserva informazione utile, ma segnala onestamente l'incertezza del dato.

### Fase 9 - Data entry manuale admin

E stato progettato un flusso di inserimento manuale pensato per una UI semplice.

Ordine desiderato:

1. creazione o selezione di un nuovo `Event`;
2. inserimento o completamento dei dati dell'evento;
3. scelta del contesto risultati: `format`, `round`, opzionalmente `apparatus` e `day`;
4. inserimento rapido dei risultati di quella classifica;
5. suggerimento atleta durante digitazione;
6. creazione automatica di un nuovo `Athlete` se non esiste;
7. notifica di riepilogo all'admin se sono stati creati atleti da completare.

Sono stati aggiunti endpoint specifici:

- opzioni per creazione evento manuale;
- opzioni per inserimento risultati in un evento;
- contesto di inserimento risultati per admin/evento;
- suggerimenti atleta durante data entry;
- risoluzione atleta esistente o creazione nuovo atleta;
- inserimento bulk dei risultati.

Quando l'admin inserisce un atleta non presente:

- il sistema puo creare una nuova entita `Athlete`;
- il `Result` salva solo `athlete_id`, non il nome copiato;
- l'admin riceve una notifica `data_entry_summary`;
- la sezione entita da completare puo mostrare atleti/eventi con campi opzionali ancora vuoti.

### Fase 10 - Preferenze utente e dashboard personale

E stato introdotto un livello di personalizzazione per utenti registrati.

Un `USER` registrato puo:

- seguire atleti;
- salvare eventi;
- salvare anche eventi futuri;
- vedere dettagli degli atleti seguiti;
- vedere dettagli degli eventi salvati;
- salvare viste dashboard personali con filtri e configurazioni.

Entita introdotte:

- `FollowedAthlete`
- `SavedEvent`
- `SavedDashboardView`

La dashboard personale futura potra usare questi dati per mostrare:

- atleti seguiti;
- ultimi risultati;
- eventi salvati;
- eventi futuri;
- dashboard views preferite;
- filtri ricorrenti.

### Fase 11 - Calendario eventi ed eventi futuri

E stata chiarita la natura del database eventi: non deve contenere solo gare concluse, ma anche eventi futuri.

Gli admin possono creare eventi futuri senza risultati associati.

Sono stati introdotti:

- endpoint calendario pubblico;
- stato calcolato dell'evento;
- reminder admin per eventi conclusi senza risultati.

Stati calendario:

- `upcoming`: evento futuro;
- `ongoing`: evento in corso;
- `completed_no_results`: evento concluso senza risultati;
- `completed_with_results`: evento concluso con risultati.

Gli eventi futuri possono essere salvati dagli user registrati.

### Fase 12 - Analytics, ranking, trend e grafici futuri

Sono stati creati endpoint pubblici per analytics, pensati come base della futura UI grafica.

Funzionalita supportate:

- filtri globali realmente disponibili;
- ranking globali;
- ranking evento;
- confronto fra atleti;
- trend nel tempo;
- dashboard atleta;
- profilo apparatus atleta;
- age-by-country;
- dati pronti per grafici sovrapponibili;
- distinzione fra metriche disponibili e non disponibili.

Metriche principali:

- `score`
- `D_score`
- `E_score`
- `Penalty`
- `Bonus`
- `execution_estimate`

Per la scheda atleta futura sono stati preparati endpoint utili a visualizzare:

- dati anagrafici;
- risultati recenti;
- statistiche;
- trend;
- breakdown per anno;
- breakdown per apparatus;
- profilo apparatus.

Per MAG il profilo apparatus e pensato come esagono.  
Per WAG il profilo apparatus e pensato come rombo.

Questi grafici potranno poi essere modificati lato UI senza dover stravolgere il backend, perche le API espongono dati filtrabili e aggregabili.

### Fase 13 - Site analytics leggere

E stata introdotta una prima versione minima e leggera delle statistiche sito, visibile solo da admin.

Obiettivo:

- registrare eventi d'uso senza introdurre una piattaforma pesante;
- restare privacy-friendly;
- fornire dati minimi per capire utilizzo e interesse.

Eventi tracciabili:

- `page_view`
- `search`
- `athlete_view`
- `event_view`
- `dashboard_view`
- `session_end`

Statistiche admin:

- numero visitatori stimati;
- sessioni;
- utenti registrati;
- utenti attivi/inattivi;
- atleti piu visualizzati;
- eventi piu visualizzati;
- ricerche frequenti;
- durata media quando disponibile.

Questa versione e intenzionalmente piccola: non sostituisce strumenti professionali di analytics, ma offre un primo nucleo interno.

### Fase 14 - Notifiche

Il sistema notifiche e stato progressivamente pulito.

Tipi attuali:

- `new_event`
- `new_result`
- `import_summary`
- `data_entry_summary`
- `event_results_reminder`
- `security_alert`
- `admin_promotion`
- `admin_demotion`

Decisioni importanti:

- le notifiche `new_result` sono cumulative per atleta, evento, round e format;
- l'import Gymternet non genera notifiche separate confuse per nuovi atleti/eventi;
- l'import produce una unica notifica `import_summary`;
- la notifica `import_summary` deve riassumere cosa e stato fatto automaticamente;
- promozione e declassamento ruolo producono notifiche personali;
- reminder risultati evento produce notifiche admin.

Esempio concettuale di `import_summary`:

"Import completato: il file Results 2024 ha creato 38 nuovi atleti, 12 nuovi eventi, 1460 nuovi risultati. Sono stati rilevati 21 atleti da verificare, 4 possibili cambi di country e 16 risultati con dati parziali."

### Fase 15 - Import Gymternet legacy 2018-2025

Questa e una delle aree piu importanti del progetto.

L'obiettivo e popolare il database storico usando file Gymternet standardizzati relativi agli anni 2018-2025.

I file sono presenti in:

- `import_files/Results 2018.xlsx`
- `import_files/Results 2019.xlsx`
- `import_files/Results 2020.xlsx`
- `import_files/Results 2021.xlsx`
- `import_files/Results 2022.xlsx`
- `import_files/Results 2023.xlsx`
- `import_files/Results 2024.xlsx`
- `import_files/Results 2025.xlsx`

Durante la conversazione sono stati analizzati diversi problemi:

- nomi colonna inizialmente non standard;
- rinomina e normalizzazione dei fogli Excel;
- distinzione fra top scores e D-scores;
- D-score orfani;
- final score orfani;
- atleti junior riconoscibili da asterisco;
- eventi con `Day 1` / `Day 2`;
- duplicati evento;
- typo nei nomi atleta;
- atleta simile gia presente nel database;
- cambio nazionalita atleta;
- dati mancanti;
- regole VT;
- bonus dal 2025;
- import 2018, poi verifica 2019, 2020 e file successivi;
- validazione generale sui file 2018-2025.

Il tool di import oggi segue un flusso admin:

1. upload/preview del file;
2. parsing;
3. normalizzazione;
4. deduplicazione;
5. rilevazione nuovi atleti;
6. rilevazione nuovi eventi;
7. suggerimenti per match atleta;
8. suggerimenti per cambio country;
9. rilevazione dati parziali;
10. review admin;
11. commit nel database;
12. notifica unica `import_summary`.

Endpoint principali:

- `POST /imports/gymternet/preview`
- `POST /imports/gymternet/review-target-suggestions`
- `POST /imports/gymternet/commit`

### Fase 16 - Suggerimenti durante import

E stata introdotta una logica per assistere l'admin quando l'import trova problemi.

Esempi:

- se nel file appare `Hasimoto` ma in LEVERAGE esiste `Hashimoto`, il sistema propone un possibile match;
- se un atleta ha lo stesso nome ma country diverso, il sistema chiede se aggiornare la country e registrare un cambio;
- se un evento contiene `Day 1`, il sistema rimuove `Day 1` dal nome evento e valorizza `day = 1`;
- se il dato e incompleto, il sistema lo segnala nel report.

L'admin deve poter:

- accettare il suggerimento;
- rifiutare il suggerimento;
- correggere manualmente;
- scartare il dato.

Questo approccio riduce errori di data entry senza automatizzare in modo cieco.

### Fase 17 - Storico cambi country atleta

E stata aggiunta la possibilita di registrare cambi di nazionalita dell'atleta.

Entita:

- `AthleteCountryChange`

Campi:

- `athlete_id`
- `from_country`
- `to_country`
- `change_year`

Questa funzionalita serve sia durante import sia nella scheda atleta admin. Se durante import viene rilevato un country diverso per atleta gia presente, l'admin puo decidere se aggiornare la country corrente e registrare il cambio.

### Fase 18 - `birth_date` sostituito da `birth_year`

E stata presa una decisione strutturale: sostituire `birth_date` con `birth_year` in tutto il progetto.

Motivazione:

- nelle fonti sportive spesso e disponibile l'anno di nascita, non la data completa;
- per le analytics eta/gara e sufficiente l'anno;
- riduce il rischio di salvare date non verificate;
- migliora coerenza con i dati World Gymnastics e Gymternet.

Risultato:

- `birth_date` e stato rimosso;
- `birth_year` e presente in `Athlete`;
- il backend valida l'anno;
- le analytics eta usano `event.year - athlete.birth_year`.

### Fase 19 - Motore World Gymnastics per Athlete

E stato sviluppato un motore leggero World Gymnastics per assistere l'admin nel completamento della scheda atleta.

Principio:

- il motore cerca candidati compatibili;
- l'admin sceglie il profilo ufficiale;
- il sistema crea suggerimenti pending;
- solo l'admin puo approvare, modificare o rifiutare;
- i dati ufficiali dell'atleta non cambiano automaticamente.

Campi Athlete collegati:

- `world_gymnastics_athlete_id`
- `world_gymnastics_profile_url`
- `world_gymnastics_status`
- `world_gymnastics_verified_at`
- `world_gymnastics_verified_by_admin_id`

E stato deciso di reintrodurre il concetto di status atleta, ma in modo diverso rispetto all'inizio:

- non come generico campo manuale primario;
- come `world_gymnastics_status`;
- opzionale;
- nullo alla creazione;
- valorizzabile tramite verifica admin da fonte ufficiale.

Endpoint principali:

- `GET /world-gymnastics/athletes/{athlete_id}/candidates`
- `POST /world-gymnastics/athletes/{athlete_id}/suggestions`

### Fase 20 - Motore World Gymnastics per Event

E stato sviluppato un approccio analogo per Event.

Campi Event collegati:

- `world_gymnastics_event_id`
- `world_gymnastics_event_url`
- `world_gymnastics_status`
- `world_gymnastics_verified_at`
- `world_gymnastics_verified_by_admin_id`
- `venue`

La scelta su `venue` e stata di renderlo coerente con `world_gymnastics_status`:

- campo opzionale;
- nullo alla creazione;
- completabile tramite suggerimento World Gymnastics;
- approvabile/modificabile/rifiutabile dall'admin.

Per `image_url` evento e stato deciso di mantenerlo opzionale per sviluppi futuri, senza rimuoverlo. In futuro si potra decidere se:

- assegnare immagini prefissate a eventi specifici;
- usare immagini ufficiali;
- eliminare il campo se non serve.

Endpoint principali:

- `GET /world-gymnastics/events/{event_id}/candidates`
- `POST /world-gymnastics/events/{event_id}/suggestions`

### Fase 21 - Motore AI/web nascosto

E stato discusso un motore AI/web per suggerire campi mancanti di `Athlete` ed `Event`.

Decisione:

- il motore resta integrato ma disabilitato di default;
- non deve generare costi se non usato;
- non deve modificare dati ufficiali senza admin;
- puo essere utile per sviluppi futuri;
- il provider e configurabile tramite variabili d'ambiente.

Entita centrale:

- `DataSuggestion`

Stati:

- `pending`
- `accepted`
- `edited`
- `rejected`

Endpoint:

- `GET /data-suggestions`
- `POST /data-suggestions`
- `POST /data-suggestions/generate`
- `POST /data-suggestions/{suggestion_id}/accept`
- `POST /data-suggestions/{suggestion_id}/reject`

### Fase 22 - Ruoli, super admin, audit e soft delete

Per proteggere il database da cancellazioni o manomissioni, e stato introdotto un hardening ulteriore.

Ruoli attuali:

- `super_admin`
- `admin`
- `user`

Il primo utente registrato diventa `super_admin`.

Operazioni di governo riservate al super admin:

- consultare audit log;
- ripristinare entita soft-deleted;
- gestire ruoli critici;
- proteggere l'ultimo super admin.

Sono stati introdotti:

- `AuditLog`;
- soft delete su `Athlete`;
- soft delete su `Event`;
- soft delete su `Result`;
- restore super-admin-only;
- `security_alert`.

Il soft delete non sostituisce i backup, ma riduce il rischio operativo di cancellazioni accidentali o malevole.

### Fase 23 - Import nuovo standard 2026

Sono stati analizzati file separati MAG/WAG 2026 in un nuovo standard potenzialmente fornito da Gymternet.

Decisione attuale:

- non implementare subito il nuovo standard;
- prima completare la popolazione storica 2018-2025;
- in futuro valutare un import parallelo o sostitutivo;
- mantenere un contratto comune tra data entry manuale, import Gymternet legacy e futuri importer paralleli;
- il nuovo standard potrebbe ridurre o eliminare calcoli derivati come VT2 ed execution estimate;
- dopo la popolazione storica si potra valutare se rendere nuovamente `score` obbligatorio per i dati futuri.

Questa scelta mantiene stabile il lavoro storico e rimanda la nuova pipeline a una fase successiva.

Per rendere coerente un futuro importer parallelo, e stato aggiunto un contratto tecnico in `docs/import_contract.md`. Il principio e che ogni importer puo avere parser e normalizzazioni proprie, ma deve rispettare gli stessi controlli comuni: preview admin, verifica atleta simile, cambio country, creazione controllata di eventi e atleti, coerenza discipline/category, regole Bonus, duplicati Result, country storica su `represented_country` e notifica cumulativa.

Per i dati Gymternet legacy successivi al 2025, la regola esplicita e conservativa e stata aggiornata: il tool genera un warning e applica le stesse regole Gymternet del 2025. Quindi `VT` viene marcato come `vt_attempt=1` con `vault_attempt_order_uncertain=true`; MAG ricostruisce `VT attempt 2` da `VT AVG` e `VT SUM`; WAG ricostruisce solo il D-score di `VT attempt 2` da `VT SUM`, lasciando il final score `NULL` / `not available`. I componenti mancanti `E_score`, `Penalty` e `Bonus` restano `NULL` / `not_available`, come nel 2025. Il percorso consigliato per i dati futuri resta un import standard dedicato con componenti esplicite.

### Fase 24 - Preparazione a GitHub e popolamento massivo

Prima di popolare definitivamente il database, e stato consigliato di creare un repository Git.

Motivazione:

- salvare una fotografia stabile del backend;
- evitare perdita di lavoro;
- poter tornare indietro in caso di problemi;
- documentare le modifiche;
- preparare deploy futuro;
- separare codice, database locale e file di import.

Stato attuale:

- la cartella non e ancora repository Git;
- il progetto e in locale;
- il prossimo passo consigliato e inizializzare Git, creare repo GitHub e fare primo commit;
- solo dopo conviene procedere con popolamento massivo controllato.

Il popolamento massivo storico viene tracciato in un documento operativo dedicato: `docs/LEVERAGE_popolamento_massivo_diario.md`. Questo file registra preview, statistiche, decisioni admin, commit e verifiche post-import per ogni anno 2018-2025.

### Fase 25 - Lingua, i18n e rifinitura pre-Git finale

Prima del passaggio a Git e stato fatto un controllo specifico sulla lingua supportata dal sistema.

Decisione finale:

- la lingua principale del backend e l'inglese;
- i dati sportivi, gli enum e i codici API restano stabili e non vengono tradotti;
- il sito dovra poter essere visualizzato in inglese, italiano, spagnolo e francese;
- un visitatore anonimo puo cambiare lingua nella UI senza account, con scelta conservata lato browser;
- un utente loggato salva invece `preferred_language` sul proprio profilo;
- le notifiche backend vengono generate nella lingua preferita del destinatario loggato.

Sono stati aggiunti:

- enum lingua `en`, `it`, `es`, `fr`;
- campo `User.preferred_language`;
- endpoint pubblico `GET /preferences/language-options`;
- endpoint pubblico `GET /preferences/language`, capace di risolvere lingua da utente loggato, parametro `language`, header `Accept-Language` o default `en`;
- endpoint autenticato `PUT /preferences/language`;
- traduzioni backend per notifiche principali;
- test dedicati per lingua anonima, lingua browser, lingua utente loggato e notifiche localizzate.

Durante la rifinitura finale pre-Git e stato inoltre corretto il contratto di data entry manuale: per eventi dal 2026 in poi `GET /events/{event_id}/manual-entry-options` dichiara `E_score` tra i campi obbligatori, coerentemente con la validazione effettiva e con la regola moderna `Final Score = D_score + E_score - Penalty + Bonus`.

Audit tecnico finale:

- `alembic upgrade head` verificato su database SQLite temporaneo;
- test mirati su auth, i18n, import Gymternet, policy 2026 e data entry manuale superati;
- suite completa aggiornata a `99 passed`;
- compilazione Python di `app` e `tests` completata;
- artifact locali di test/cache puliti;
- `.gitignore` verificato per escludere `.venv`, cache, database locali, log, upload e file sorgente locali in `import_files/`.

---

## 4. Architettura attuale

### 4.1 Cartelle principali

- `app/`: codice backend FastAPI.
- `app/routers/`: endpoint API divisi per area funzionale.
- `migrations/`: configurazione e versioni Alembic.
- `tests/`: test automatici.
- `docs/`: documentazione progettuale.
- `import_files/`: file storici Gymternet 2018-2025.
- `uploads/`: immagini caricate localmente.
- `leverage.db`: database SQLite locale.
- `test_leverage.db`: database test locale generato dai test, escluso dal versionamento e da eliminare prima del commit.

### 4.2 Moduli principali

- `models.py`: modelli SQLAlchemy.
- `schemas.py`: schemi Pydantic.
- `security.py`: autenticazione JWT e controlli ruolo.
- `audit.py`: registrazione audit log.
- `soft_delete.py`: funzioni di cancellazione logica.
- `result_ranking.py`: ranking, metriche e qualita dato.
- `gymternet_import.py`: import legacy Gymternet.
- `i18n.py`: lingue supportate, risoluzione lingua pubblica e traduzioni backend.
- `world_gymnastics.py`: integrazione leggera World Gymnastics.
- `ai_suggestions.py`: provider opzionale suggerimenti AI/web.
- `event_calendar.py`: stato calendario eventi.

### 4.3 Router API

- `auth.py`: registrazione, verifica email, login password, reset password, MFA admin, token, utente corrente.
- `athletes.py`: CRUD atleta, immagini, risultati atleta, stats, country changes, admin view.
- `events.py`: CRUD evento, calendario, classifiche, data entry manuale, bulk results, ranking view, profile view.
- `results.py`: CRUD result, ranking e trend storici.
- `analytics.py`: filtri globali, ranking, confronti, dashboard atleta, apparatus profile, eta per country.
- `imports.py`: preview, review e commit import Gymternet.
- `preferences.py`: lingua, atleti seguiti, eventi salvati, dashboard views.
- `notifications.py`: lettura e gestione notifiche.
- `data_suggestions.py`: suggerimenti admin.
- `world_gymnastics.py`: candidati e suggerimenti World Gymnastics.
- `site_analytics.py`: eventi d'uso e summary admin.
- `admin_users.py`: utenti, ruoli, reminder, audit, restore, entita da completare.

---

## 5. Entita e database

### 5.1 User

Rappresenta un account registrato.

Campi principali:

- `id`
- `email`
- `password_hash`
- `email_verification_token_hash`
- `email_verification_expires_at`
- `password_reset_token_hash`
- `password_reset_expires_at`
- `is_verified`
- `role`
- `is_active`
- `failed_login_attempts`
- `login_locked_until`
- `auth_version`
- `mfa_secret`
- `mfa_enabled`
- `mfa_recovery_codes`
- `preferred_language`
- `created_at`

Ruoli:

- `super_admin`
- `admin`
- `user`

Relazioni:

- atleti seguiti;
- eventi salvati;
- dashboard views salvate.

`preferred_language` accetta `en`, `it`, `es`, `fr` e ha default `en`. Serve per la lingua personale dell'utente loggato e per localizzare le notifiche generate dal backend.

### 5.2 Athlete

Rappresenta un ginnasta.

Campi principali:

- `id`
- `first_name`
- `last_name`
- `birth_year`
- `country`
- `discipline`
- `image_url`
- `world_gymnastics_athlete_id`
- `world_gymnastics_profile_url`
- `world_gymnastics_status`
- `world_gymnastics_verified_at`
- `world_gymnastics_verified_by_admin_id`
- `is_deleted`
- `deleted_at`
- `deleted_by_admin_id`
- `created_at`

Valori:

- `discipline`: `MAG`, `WAG`;
- `birth_year`: opzionale, fra 1900 e 2100;
- `country`: opzionale ma consigliato;
- `image_url`: opzionale, caricabile solo admin;
- campi World Gymnastics: opzionali e approvati da admin.

Relazioni:

- risultati;
- storico cambi country.

### 5.3 AthleteCountryChange

Registra cambi di nazionalita.

Campi:

- `id`
- `athlete_id`
- `from_country`
- `to_country`
- `change_year`
- `created_at`

Uso:

- durante import se un atleta esistente appare con country diverso;
- nella scheda atleta admin;
- come storico consultabile in futuro nella scheda atleta.

### 5.4 Event

Rappresenta una competizione.

Campi principali:

- `id`
- `name`
- `location`
- `venue`
- `start_date`
- `end_date`
- `year`
- `discipline`
- `category`
- `level`
- `image_url`
- `world_gymnastics_event_id`
- `world_gymnastics_event_url`
- `world_gymnastics_status`
- `world_gymnastics_verified_at`
- `world_gymnastics_verified_by_admin_id`
- `is_deleted`
- `deleted_at`
- `deleted_by_admin_id`
- `created_at`

Valori:

- `discipline`: `MAG`, `WAG`, `MAG and WAG`;
- `category`: `junior`, `senior`, `junior and senior`;
- `level`: `Olympic Games`, `World Championships`, `Continental Championships`, `World Cup`, `World Challenge Cup`, `International Event`, `National Event`;
- `venue`: opzionale;
- `image_url`: opzionale, caricabile solo admin;
- date opzionali ma utili per calendario;
- `year` obbligatorio.

Semantica UI:

- `MAG and WAG` corrisponde alla doppia selezione MAG + WAG;
- `junior and senior` corrisponde alla doppia selezione junior + senior;
- non sono bottoni separati.

### 5.5 Result

Rappresenta un risultato sportivo collegato a un atleta e a un evento.

Campi principali:

- `id`
- `athlete_id`
- `event_id`
- `discipline`
- `category`
- `apparatus`
- `vt_attempt`
- `day`
- `format`
- `round`
- `D_score`
- `E_score`
- `Penalty`
- `Bonus`
- `score`
- `rank`
- `vault_attempt_order_uncertain`
- `is_deleted`
- `deleted_at`
- `deleted_by_admin_id`
- `created_at`

Valori:

- `discipline`: `MAG`, `WAG`;
- `category`: `junior`, `senior`;
- `format`: `team`, `individual`, `apparatus`;
- `round`: `qualification`, `final`;
- `vt_attempt`: `1`, `2`, oppure `NULL`;
- `day`: numero positivo oppure `NULL`;
- `score`: normalmente presente, nullable per casi storici controllati;
- `D_score`, `E_score`, `Penalty`, `Bonus`: opzionali;
- `vault_attempt_order_uncertain`: boolean.

Vincoli semantici:

- l'atleta deve esistere;
- l'evento deve esistere;
- la disciplina del result deve coincidere con quella dell'atleta;
- la disciplina del result deve essere ammessa dall'evento;
- la category del result deve essere ammessa dall'evento;
- apparatus deve essere coerente con la disciplina;
- Bonus deve rispettare le regole per anno/disciplina/apparatus;
- score nullable solo nei casi ammessi dal dominio/import.

### 5.6 ResultEntryContext

Memorizza il contesto di inserimento manuale per admin/evento.

Campi:

- `event_id`
- `admin_id`
- `apparatus`
- `day`
- `format`
- `round`

Uso:

- l'admin sceglie format e round una volta;
- poi inserisce piu risultati senza ripetere ogni campo;
- rende il data entry piu agile.

### 5.7 DataSuggestion

Rappresenta un suggerimento da verificare.

Campi:

- `entity_type`
- `entity_id`
- `field_name`
- `suggested_value`
- `reviewed_value`
- `confidence`
- `source_url`
- `source_title`
- `evidence`
- `status`
- `created_by_admin_id`
- `reviewed_by_admin_id`
- `created_at`
- `reviewed_at`

Uso:

- completamento campi Athlete/Event;
- motore AI/web disabilitato;
- motore World Gymnastics;
- revisione admin.

### 5.8 Notification

Rappresenta una notifica utente/admin.

Tipi:

- `new_event`
- `new_result`
- `import_summary`
- `data_entry_summary`
- `event_results_reminder`
- `security_alert`
- `admin_promotion`
- `admin_demotion`

### 5.9 Preferences

Entita:

- `FollowedAthlete`
- `SavedEvent`
- `SavedDashboardView`

Permettono all'utente registrato di personalizzare l'esperienza.

### 5.10 SiteAnalyticsEvent

Registra eventi d'uso minimi.

Campi:

- `event_type`
- `visitor_id`
- `session_id`
- `user_id`
- `path`
- `search_query`
- `entity_type`
- `entity_id`
- `duration_seconds`
- `created_at`

### 5.11 AuditLog

Registra modifiche critiche.

Campi:

- `admin_id`
- `action`
- `entity_type`
- `entity_id`
- `before_json`
- `after_json`
- `created_at`

---

## 6. Utenti e funzioni ammesse

### 6.1 Visitatore pubblico

Un visitatore non registrato puo:

- visualizzare atleti;
- visualizzare eventi;
- visualizzare calendario eventi;
- visualizzare classifiche;
- filtrare risultati;
- usare analytics pubbliche;
- consultare schede atleta/evento pubbliche;
- cambiare lingua della futura UI senza account, con preferenza salvata lato browser;
- cercare e confrontare dati se la futura UI lo consente tramite endpoint pubblici.

Non puo:

- modificare dati;
- salvare preferenze;
- ricevere notifiche personali;
- accedere agli strumenti admin.

### 6.2 USER registrato

Un user registrato puo fare tutto cio che fa un visitatore, in piu puo:

- seguire atleti;
- salvare eventi;
- salvare eventi futuri;
- consultare dettagli degli atleti seguiti;
- consultare dettagli degli eventi salvati;
- salvare dashboard views;
- impostare una dashboard view di default;
- salvare la lingua preferita sul profilo;
- ricevere notifiche personali.

Non puo:

- creare/modificare/cancellare atleti, eventi o risultati;
- importare file;
- approvare suggerimenti;
- vedere suggerimenti admin;
- vedere analytics sito admin;
- gestire ruoli.

### 6.3 ADMIN

Un admin puo:

- creare/modificare atleti;
- creare/modificare eventi;
- creare/modificare risultati;
- caricare immagini atleta/evento;
- usare data entry manuale;
- usare import Gymternet;
- vedere preview import;
- risolvere suggerimenti import;
- approvare/correggere/rifiutare suggerimenti;
- vedere entita da completare;
- vedere reminder eventi senza risultati;
- generare notifiche reminder;
- vedere statistiche sito;
- consultare admin view di Athlete/Event.

Non dovrebbe gestire operazioni distruttive critiche senza supervisione super admin.

### 6.4 SUPER_ADMIN

Un super admin puo:

- fare cio che fa un admin;
- consultare audit logs;
- ripristinare entita soft-deleted;
- gestire ruoli critici;
- proteggere governance del sistema;
- ricevere security alert.

Il primo account registrato diventa super admin.

---

## 7. Tool di import Gymternet

### 7.1 Obiettivo

Il tool di import serve a popolare in modo controllato il database LEVERAGE con dati storici Gymternet 2018-2025.

Non e pensato come import cieco, ma come procedura assistita:

- il sistema legge il file;
- rileva problemi;
- propone soluzioni;
- l'admin verifica;
- solo dopo si committa nel database.

### 7.2 Entita popolate

L'import puo creare o aggiornare:

- `Athlete`
- `Event`
- `Result`
- `AthleteCountryChange`
- `Notification`

L'import non deve solo inserire righe result: deve mantenere coerente l'intero grafo dati.

### 7.3 Problemi gestiti

Problemi gestiti o previsti:

- nuovo atleta;
- atleta simile gia presente;
- typo nel nome atleta;
- atleta junior da asterisco;
- nuovo evento;
- evento con day nel nome;
- evento multi-day;
- cambio country atleta;
- duplicati;
- duplicati `Result` con stessa identita sportiva;
- conflitti country su `Result` gia presenti o importati;
- score senza D-score;
- D-score senza score;
- dati parziali;
- VT AVG;
- VT SUM;
- VT attempt 2 derivato;
- ordine vault incerto;
- regole bonus 2018-2024 e 2025;
- report import unico.

### 7.4 Strategia dati incompleti

Scelte attuali:

- conservare result con `score` ma senza `D_score`, segnalando `D_score` come `not available`;
- evitare di popolare result con solo `D_score` e senza `score`, perche potrebbero falsare analisi;
- eccezione controllata: 2025 WAG VT attempt 2 derivato da VT SUM, dove il final score non e ricostruibile con certezza;
- calcolare `execution_estimate` solo quando possibile;
- non salvare `execution_estimate` come dato ufficiale.

### 7.5 Output admin

L'import deve restituire all'admin:

- quanti atleti sono stati creati;
- quanti eventi sono stati creati;
- quanti risultati sono stati inseriti;
- quanti dati sono stati saltati;
- quanti dati sono parziali;
- quanti match atleta sono stati suggeriti;
- quanti cambi country sono stati proposti;
- quanti vault sono marcati come ordine incerto;
- quali entita restano da completare.

Tutto confluisce nella notifica `import_summary`.

---

## 8. Tool di completamento e suggerimenti

### 8.1 Entita da completare

Endpoint admin:

- `GET /admin/entities-to-complete`

Serve per alimentare una futura sezione admin in cui vedere:

- atleti con campi opzionali mancanti;
- eventi con campi opzionali mancanti;
- entita create automaticamente da import o data entry;
- record da completare in un secondo momento.

### 8.2 Suggerimenti AI/web

Il motore AI/web:

- e presente;
- e disabilitato di default;
- non genera costi se non configurato/usato;
- non approva mai dati automaticamente;
- crea solo `DataSuggestion` pending.

Questa scelta consente sviluppi futuri senza introdurre oggi costi server o API.

### 8.3 World Gymnastics Athlete

Il motore atleta cerca profili ufficiali e permette all'admin di collegare:

- ID World Gymnastics;
- URL profilo;
- status ufficiale;
- eventuali campi mancanti.

Solo l'admin approva.

### 8.4 World Gymnastics Event

Il motore evento segue una logica analoga:

- cerca candidati evento;
- propone URL ufficiale;
- propone status;
- propone venue;
- crea suggerimenti pending.

Anche qui, solo admin approva.

---

## 9. Backend pronto per futura UI

Il backend e gia orientato a supportare:

- homepage dati pubblici;
- elenco atleti;
- scheda atleta;
- elenco eventi/calendario;
- scheda evento;
- classifiche evento;
- filtri realmente disponibili;
- dashboard utente;
- salvataggio preferenze;
- notifiche;
- cambio lingua anonimo/loggato;
- area admin;
- data entry manuale;
- import da file;
- verifica suggerimenti;
- analytics sito.

Esempi di schermate future supportate:

- scheda atleta con dati anagrafici, country changes, World Gymnastics link, trend score, profilo apparatus;
- scheda evento con dati calendario, filtri reali, gruppi result, classifica principale;
- dashboard confronto atleti con grafici sovrapponibili;
- dashboard eta media per country in eventi selezionati;
- sezione admin import con problemi e suggerimenti;
- sezione admin entita da completare;
- sezione admin site analytics.

Il frontend potra ancora cambiare molto, ma il backend espone gia contratti API adatti.

---

## 10. Stato migrazioni

Migrazioni presenti:

- `0001_initial`
- `0002_result_category_and_event_domain_updates`
- `0003_split_event_and_result_category_enums`
- `0004_add_format_to_result_entry_context`
- `0005_add_day_to_results`
- `0006_import_created_notifications`
- `0007_add_athlete_country_changes`
- `0008_add_data_suggestions`
- `0009_add_reviewed_value_to_data_suggestions`
- `0010_replace_athlete_birth_year`
- `0011_add_world_gymnastics_athlete_fields`
- `0012_add_world_gymnastics_event_fields`
- `0013_add_event_venue`
- `0014_add_saved_dashboard_views`
- `0015_add_site_analytics_events`
- `0016_add_admin_promotion_notification`
- `0017_add_admin_demotion_notification`
- `0018_add_import_summary_notification`
- `0019_cleanup_import_notification_types`
- `0020_add_data_entry_summary_notification`
- `0021_add_event_results_reminder_notification`
- `0022_security_audit_soft_delete`
- `0023_add_vault_attempt_order_uncertain`
- `0024_allow_nullable_result_score`
- `0025_add_result_represented_country`
- `0026_replace_passwordless_authentication`
- `0027_add_scalability_indexes`
- `0028_add_user_preferred_language`

Le migrazioni raccontano l'evoluzione reale del progetto: da schema iniziale a piattaforma con import, suggerimenti, analytics, notifiche, sicurezza, i18n e gestione qualita dati.

---

## 11. Stato test

Ultima verifica pre-Git:

- `99 passed`
- `alembic upgrade head` verificato su database SQLite temporaneo
- compilazione Python di `app` e `tests` completata

Aree coperte:

- auth email/password, verifica email, MFA admin/JWT;
- ruoli;
- admin/super admin;
- CRUD;
- vincoli semantici;
- classifiche evento;
- analytics;
- dashboard;
- site analytics;
- preferenze;
- lingua/i18n per visitatori anonimi e utenti loggati;
- notifiche;
- data entry manuale;
- import Gymternet;
- suggerimenti;
- World Gymnastics;
- soft delete;
- audit;
- regole vault;
- regole bonus;
- score nullable controllato.
- indici e paginazione per preparare il popolamento storico.
- opzioni data entry manuale coerenti con E-score obbligatorio dal 2026.

La suite test e uno degli asset piu importanti del progetto, perche protegge una logica di dominio ormai molto articolata.

---

## 12. Decisioni progettuali chiave

### Dati ufficiali

LEVERAGE deve mostrare dati ufficiali e approvati. I suggerimenti non diventano mai ufficiali senza admin.

### `Result` resta `Result`

Il nome `Result` e stato mantenuto per coerenza semantica e per volonta esplicita di progetto.

### `birth_year` al posto di `birth_date`

Decisione coerente con le fonti disponibili e con le analytics eta.

### Event multi-discipline e multi-category

`MAG and WAG` e `junior and senior` sono valori database utili, ma nella UI derivano da doppia selezione.

### Result single-discipline e single-category

Un risultato e sempre specifico: una disciplina e una category.

### Score mancanti

`not available` e preferibile a valori inventati. I dati incompleti devono essere visibili e filtrabili.

### Bonus

Bonus resta opzionale e `NULL` quando non previsto, non applicabile o non disponibile nei dati storici. Dal 2026, nei flussi moderni di data entry/import, `E_score` e obbligatorio; `Penalty` e `Bonus` lasciati vuoti vengono normalizzati a `0.0`.

### Vault

I vault storici derivati sono utili ma incerti. Vanno salvati con warning.

### Import assistito

L'import e uno strumento admin, non un caricamento automatico cieco.

### Git prima del popolamento massivo

Prima di importare definitivamente anni di dati, conviene versionare il codice su GitHub.

### Scalabilita prima del popolamento

Prima del popolamento storico sono stati aggiunti indici mirati su `Athlete`, `Event` e soprattutto `Result`, con attenzione a classifiche evento, schede atleta, filtri per calendario, ranking e chiave semantica anti-duplicato. Gli endpoint pubblici principali che restituiscono liste (`athletes`, `events`, `events/calendar`, `results`, result atleta e result evento) supportano ora `limit` e `offset` con massimali, cosi la UI deve lavorare per pagine invece di scaricare intere tabelle.

### Duplicati Result prima del popolamento

Prima del popolamento storico e stata consolidata la definizione di duplicato `Result`.

La chiave semantica del risultato e:

- `athlete_id`;
- `event_id`;
- `discipline`;
- `category`;
- `apparatus`;
- `vt_attempt`;
- `day`;
- `format`;
- `round`.

`represented_country` non fa parte della chiave di unicita, perche descrive la nazionalita rappresentata in quel risultato e va preservata come dato storico. Se due righe hanno la stessa chiave sportiva ma country diversa, LEVERAGE non le considera duplicati innocui: le segnala come conflitto da verificare.

Questa scelta evita due rischi opposti:

- fondere per errore due atleti diversi;
- perdere la nazionalita storica corretta di un atleta.

Sono stati consolidati tre livelli di protezione:

- blocco di duplicati in `POST /results`;
- blocco di duplicati nel bulk manuale `POST /events/{event_id}/results/bulk`;
- endpoint admin `GET /admin/result-duplicate-groups` per individuare gruppi duplicati gia presenti nel database.

### Merge amministrativo Athlete duplicati

Dopo l'import storico puo emergere che lo stesso atleta sia stato salvato come due entita diverse a causa di errori di battitura, accenti, romanizzazioni o varianti del nome.

Per questo e stato aggiunto un flusso admin-only di merge tra schede `Athlete`:

- `POST /athletes/{source_athlete_id}/merge-preview`;
- `POST /athletes/{source_athlete_id}/merge`.

L'admin indica l'ID dell'atleta corretto/canonico tramite `target_athlete_id`. La preview mostra:

- atleta sorgente/duplicato;
- atleta target/canonico;
- result che verrebbero spostati;
- preferenze utente da riallacciare;
- country history da spostare o deduplicare;
- suggerimenti dati e notifiche collegate;
- metadati che possono essere copiati nel target se mancanti;
- eventuali conflitti bloccanti.

Il commit richiede `confirm=true`. Se non ci sono conflitti, LEVERAGE sposta tutti i `Result` verso l'atleta canonico, preserva `represented_country`, riallaccia i follower, sposta country history non duplicate, sposta suggerimenti e notifiche, copia nel target solo metadati mancanti e soft-delete della scheda duplicata.

Se il merge produrrebbe due `Result` nello stesso contesto sportivo sullo stesso atleta target, l'operazione viene bloccata con errore `409`. Questo mantiene coerente la regola anti-duplicato dei Result e impedisce fusioni pericolose.

Ogni merge produce audit log e security alert, perche modifica in modo rilevante la struttura del database storico.

### Lingua principale e i18n

La lingua tecnica principale del backend e l'inglese. I codici sportivi, gli enum, i nomi campo e il contratto API non vengono tradotti, perche devono restare stabili per import, filtri, grafici e integrazioni.

La lingua dell'esperienza utente e invece gestibile:

- visitatore anonimo: scelta lingua lato frontend/browser;
- utente loggato: `preferred_language` salvata nel DB;
- notifiche: testo generato nella lingua preferita del destinatario.

Lingue supportate nel backend MVP: `en`, `it`, `es`, `fr`.

---

## 13. Rischi e punti da sistemare

### Repository Git mancante

La cartella locale non e ancora un repository Git. Va inizializzato prima della popolazione definitiva.

### Database locale

Il database attuale e SQLite locale. Per produzione servira decidere hosting e probabilmente passare a PostgreSQL.

### Backup

Soft delete e audit aiutano, ma non sostituiscono backup reali.

### Import storico

La pipeline e pronta, ma la popolazione massiva va fatta con prudenza:

- un anno alla volta;
- preview;
- review;
- commit;
- backup;
- verifica;
- eventuale correzione.

### Nuovo standard 2026

Il nuovo standard va implementato in seguito come import parallelo o nuova pipeline. Il file `docs/import_contract.md` stabilisce che il nuovo importer dovra riusare i controlli comuni gia sviluppati per Gymternet e data entry manuale, ma non dovra ereditare le regole legacy di ricostruzione VT.

### Score nullable

Oggi `score` e nullable per casi storici controllati. Dopo il popolamento 2018-2025 si potra valutare se renderlo di nuovo obbligatorio per i dati futuri.

### Frontend

Il frontend non esiste ancora. Il backend e pronto, ma servira progettare UI e UX.

### Deploy

Mancano ancora:

- scelta dominio;
- scelta hosting;
- configurazione produzione;
- database production;
- email transazionali reali per verifica account e reset password;
- backup;
- log;
- sicurezza deploy;
- CORS/frontend.

### Aspetti legali/privacy

Per site analytics e account utente serviranno:

- privacy policy;
- cookie policy se necessario;
- gestione dati personali minima;
- trasparenza sugli analytics;
- attenzione a fonti e licenze dati.

---

## 14. Prossimi passi consigliati

### Passo 1 - Salvare il progetto su Git

Azioni:

- inizializzare repository Git locale;
- creare `.gitignore` pulito;
- escludere `.venv`, cache, database locali se necessario;
- fare primo commit;
- creare repo GitHub;
- fare push.

### Passo 2 - Congelare una versione backend stabile

Azioni:

- eseguire test;
- correggere eventuali regressioni;
- aggiornare README e documentazione;
- taggare o segnare una milestone.

### Passo 3 - Preparare popolamento storico

Azioni:

- backup del database vuoto/stabile;
- import 2018 preview;
- review admin;
- commit;
- test/verifica;
- ripetere per 2019-2025;
- creare report di popolamento.

### Passo 4 - Validare il dataset importato

Azioni:

- controllare numero atleti;
- controllare numero eventi;
- controllare numero result;
- controllare dati mancanti;
- controllare vault incerti;
- controllare country changes;
- controllare duplicati.

### Passo 5 - Progettare frontend MVP

Priorita UI:

- pagina elenco atleti;
- scheda atleta;
- calendario eventi;
- scheda evento;
- classifica evento;
- login email/password con verifica email e MFA admin;
- dashboard user;
- area admin data entry/import.

### Passo 6 - Decidere infrastruttura produzione

Azioni:

- scelta hosting;
- database PostgreSQL;
- storage immagini;
- email provider;
- backup;
- dominio;
- monitoring/logging.

---

## 15. Milestone - Backend dati storico completato

Data milestone: 2 luglio 2026

LEVERAGE ha raggiunto una milestone centrale del progetto MVP: il backend e la base dati storica 2018-2025 sono stati consolidati, verificati, documentati e versionati su GitHub.

Rispetto allo stato precedente, sono stati completati:

- repository GitHub e versionamento stabile;
- popolamento storico controllato dei Results 2018-2025;
- review delle collisioni atleta/country/nome per ogni anno;
- riconciliazione Calendar/Event 2018-2025;
- introduzione e utilizzo di `EventCalendarEntry`;
- gestione delle eccezioni `calendar_only`, `db_only` e `season_year_spillover`;
- regole persistenti `EYOF = European Youth Olympic Festival` e `Top 12` a cavallo d'anno;
- documentazione di tesi per metodologia di popolamento Results;
- documentazione di tesi per metodologia di riconciliazione Calendar/Event.

Fotografia quantitativa del database locale:

| Entita / controllo | Valore |
|---|---:|
| Athlete attivi | 26.259 |
| Event attivi | 1.605 |
| Result attivi | 753.723 |
| EventCalendarEntry attive | 287 |
| Event 2026 gia presenti da spillover 2025 | 1 |
| Result 2026 gia presenti da spillover 2025 | 108 |

Valutazione di avanzamento al 2 luglio 2026:

| Area | Avanzamento stimato |
|---|---:|
| Backend core e modello dati | 90% |
| Import storico Gymternet | 95% |
| Popolamento dati 2018-2025 | 100% |
| Riconciliazione Calendar 2018-2025 | 100% |
| Documentazione tecnica/tesi della fase dati | 90% |
| Backend pronto per UI MVP | 80% |
| Frontend/UI | 0% |
| Deploy online produzione | 0% |
| MVP online complessivo | 70% |

## 16. Prossimo passo 2026

Il progetto era in attesa del file `Results 2026` del primo semestre. Il file e stato poi ricevuto, controllato e importato il 14 luglio 2026.

Il flusso previsto e stato seguito:

1. copiare il file sorgente in `import_files`;
2. eseguire preview Gymternet 2026 senza scrivere nel DB;
3. verificare i duplicati rispetto ai 108 result 2026 gia presenti da `Results 2025.xlsx`;
4. generare i CSV di review per conflitti atleta/country/nome;
5. compilare e applicare le decisioni admin;
6. rieseguire preview post-decisione;
7. eseguire backup e commit reale solo se pulito;
8. aggiornare diario, capitoli e report;
9. procedere alla riconciliazione Calendar 2026;
10. distinguere eventi Calendar 2026 con risultati, eventi futuri, eventi senza risultati e possibili `calendar_only` / `db_only` / `season_year_spillover`.

## 17. Milestone - Dati riconciliati fino al primo semestre 2026

Data milestone: 15 luglio 2026

LEVERAGE ha raggiunto una nuova milestone dati: il database locale e stato popolato con i Results Gymternet 2018-2025, con i Results 2026 del primo semestre e con il Calendar riconciliato fino agli Event 2026 disponibili.

Sintesi quantitativa:

| Metrica | Valore |
|---|---:|
| Athlete attivi | 27.921 |
| Event attivi | 1.719 |
| Result attivi | 819.739 |
| Event 2026 | 115 |
| Result 2026 | 66.124 |
| EventCalendarEntry 2026 | 18 |
| Righe `calendar_only` 2026 | 5 |

Esito Calendar 2026:

| Metrica | Valore |
|---|---:|
| Righe Calendar 2026 | 170 |
| Event DB 2026 | 115 |
| Event DB 2026 coperti | 115 |
| Event DB 2026 non coperti | 0 |
| Righe Calendar 2026 future/in standby | 45 |
| Event `db_only` | 2 |
| Collegamenti `season_year_spillover` | 1 |

Decisioni rilevanti:

- `Ifact Norges Cup 1/2` restano `calendar_only`;
- `Colombian Championships` e `Romanian Euros Trials` restano `db_only`;
- `Bundesliga` e modellata con `EventCalendarEntry` quando una scheda Event ha piu date calendario corrette;
- `Top 12 Series 3 (2026)` WAG e collegato al Calendar 2025 come `season_year_spillover`.

Valutazione di avanzamento al 15 luglio 2026:

| Area | Avanzamento stimato |
|---|---:|
| Backend core e modello dati | 92% |
| Import storico Gymternet | 97% |
| Popolamento dati 2018-2025 | 100% |
| Popolamento dati 2026 primo semestre | 100% |
| Riconciliazione Calendar 2018-2025 | 100% |
| Riconciliazione Calendar 2026 primo semestre | 100% |
| Documentazione tecnica/tesi della fase dati | 94% |
| Backend pronto per UI MVP | 82% |
| Frontend/UI | 0% |
| Deploy online produzione | 0% |
| MVP online complessivo | 74% |

## 18. Milestone - Avvio frontend pubblico e UI MVP

Data milestone: 15 luglio 2026

Dopo il completamento del popolamento storico e della riconciliazione Calendar fino al primo semestre 2026, e stata avviata la fase di trasformazione di LEVERAGE da backend/API platform a piattaforma web consultabile.

Scelta architetturale:

- il frontend viene sviluppato nella stessa repository GitHub del backend, dentro la cartella `frontend/`;
- in questa prima fase e stato scelto un frontend dependency-free in HTML, CSS e JavaScript vanilla, perche l'ambiente locale non disponeva di Node/npm e perche l'obiettivo iniziale era validare struttura, navigazione, stile e collegamento agli endpoint pubblici senza introdurre toolchain prematura;
- il backend FastAPI e stato predisposto con CORS configurabile per permettere al frontend locale di interrogare le API;
- la UI usa di default `http://localhost:8000` come API base, modificabile dal footer durante i test locali.

Scelte di prodotto e UX:

- LEVERAGE deve presentarsi come piattaforma dati, non come landing page puramente descrittiva;
- la prima schermata deve permettere subito ricerca, filtri e accesso ai dati principali;
- lo stile visivo scelto e minimale, pulito, moderno, ispirato all'esperienza Apple;
- il colore identitario e il blu del brand LEVERAGE fornito dal logo;
- logo e wordmark sono stati importati dagli asset forniti e usati nella topbar;
- l'interfaccia e in inglese di default, con supporto iniziale anche per italiano, spagnolo e francese;
- anche l'utente non loggato puo cambiare lingua, con preferenza salvata localmente nel browser.

Funzionalita frontend iniziali implementate:

- topbar con logo, wordmark, navigazione principale e azione `Sign in`;
- home pubblica con titolo LEVERAGE, sottotitolo `Artistic Gymnastics Analytics`, ricerca globale e filtri rapidi `MAG`, `WAG`, `Senior`, `Junior`;
- trasformazione della barra iniziale in vera ricerca globale LEVERAGE: la query viene instradata a `#/search?q=...` e non piu limitata alla sola pagina atleti;
- aggiunta dell'endpoint pubblico `/search`, con response strutturata per `athletes`, `events`, `countries`, `apparatuses` e `results`, pensata sia per la UI attuale sia per futuri autocomplete/filtri rapidi;
- potenziamento semantico della ricerca globale con parsing degli anni e alias dei paesi: query come `Serie A 2026` filtrano correttamente gli eventi/risultati del 2026, mentre ricerche come `Italy` o `ITA` restituiscono atleti di quel country ed eventi svolti in quel paese;
- ulteriore normalizzazione semantica della ricerca globale per query numeriche/ordinali, ad esempio `Bundesliga 2` riconduce anche a eventi denominati `2nd Bundesliga`;
- aggiunta dei suggerimenti live nella barra di ricerca globale, visibili sia mentre l'utente digita sia mentre cancella, con risultati provenienti dallo stesso endpoint `/search` e raggruppabili in atleti, eventi, nazioni, attrezzi e risultati;
- correzione della visibilita dei suggerimenti live: chiamata frontend indirizzata direttamente a `/search/` per evitare redirect, stato `Loading...` immediato durante l'attesa del backend e cache-buster su CSS/JS per forzare il caricamento della versione aggiornata in anteprima locale;
- aggiunta della pagina frontend `Search`, con risultati raggruppati per atleti, eventi, nazioni, attrezzi e risultati, mantenendo layout minimale e coerente con la home;
- rifinitura dei bordi dei componenti dati: card, pannelli, suggerimenti di ricerca e pill dei risultati sono stati allineati a raggi piu controllati, evitando l'effetto eccessivamente "a pillola" nei calendari, nelle classifiche e nelle schede risultato;
- separazione semantica delle classifiche globali: le ranking complessive richiedono una disciplina esplicita `MAG` o `WAG` e applicano un contesto di ciclo di punteggio, evitando confronti impliciti tra GAM/GAF o tra codici di punteggio diversi;
- trasformazione dell'anteprima calendario della home in una vera griglia mensile interattiva: gli eventi datati vengono visualizzati come barre multi-day sulle settimane, con corsie separate per gestire sovrapposizioni e indicatore del giorno corrente;
- aggiunta della navigazione mese precedente/successivo direttamente nell'anteprima calendario della home, con frecce accanto al nome del mese e ricarica mirata del range calendario selezionato;
- ribilanciamento della sezione home `Calendar preview` / `Ranking preview`: il calendario riceve piu spazio orizzontale, mentre la classifica resta una preview piu compatta;
- trasformazione della pagina `Events` in calendario mensile completo: la vista non e piu una lista di card, ma una griglia piu ampia con barre multi-day, legenda completa e navigazione mese precedente/successivo;
- estensione dell'endpoint pubblico `/events/calendar` alle voci `EventCalendarEntry`, incluse righe `calendar_only` senza scheda evento collegata, cosi il calendario puo mostrare anche eventi schedulati senza risultati;
- supporto a filtri calendario multi-selezione: l'utente puo selezionare contemporaneamente `MAG` e `WAG`, oppure `junior` e `senior`;
- correzione semantica dei filtri evento: gli eventi `MAG and WAG` compaiono anche filtrando solo `MAG` o solo `WAG`; gli eventi `junior and senior` compaiono anche filtrando solo `junior` o solo `senior`;
- aggiunta del pulsante `Today` / `Oggi` vicino al mese, sia nella preview home sia nel calendario completo, per tornare rapidamente al mese corrente;
- integrazione leggera con le site analytics: ogni ricerca globale invia un evento `search` non bloccante a `/site-analytics/events`, cosi la dashboard admin potra conteggiare le ricerche piu frequenti;
- introduzione iniziale della home con logo LEVERAGE mostrato brevemente, dissolvenza/dispersione leggera e comparsa della scritta `LEVERAGE` centrata in alto con sottotitolo minimale `Artistic Gymnastics Analytics`;
- rifinitura dell'introduzione iniziale: dopo la dissolvenza del logo, la topbar scende dall'alto con effetto tendina e la scritta centrale `LEVERAGE` usa il wordmark PNG ufficiale fornito;
- allineamento cromatico del sottotitolo della home al grigio secondario standard della UI, usando la variabile condivisa `--muted`;
- revisione della hero iniziale in composizione centrata, con ricerca e filtri immediatamente sotto al titolo e status API ridotto a indicatore compatto;
- collegamento agli endpoint pubblici per mostrare preview Calendar e Ranking;
- pagine iniziali per `Athletes`, `Events`, `Rankings`, `Analytics` e `Login`;
- footer con configurazione locale dell'API base;
- gestione lingua `EN / IT / ES / FR` tramite local storage;
- menu di navigazione a tendina per `Athletes`, `Events`, `Rankings`, `Analytics`, con azioni principali visibili al passaggio del mouse;
- correzione dello stato visivo della topbar: le voci di navigazione restano evidenziate solo quando realmente attive o in hover, evitando che `Analytics` rimanga grigio dopo interazioni precedenti;
- correzione ulteriore dei dropdown topbar: rimossa l'apertura tramite `focus-within`, cosi un pannello come `Analytics` non puo restare visibile/scuro dopo un click o dopo il mantenimento del focus;
- rimozione definitiva del riquadro grigio pieno dalle voci della topbar: lo stato attivo usa solo testo scuro e una linea sottile, evitando box persistenti o visivamente pesanti;
- selettore lingua custom, arrotondato e coerente con lo stile app;
- menu lingua compatto con pulsante dedicato e popover separato, mantenendo la lingua selezionata visibile e mostrando solo le opzioni non selezionate;
- micro-animazione progressiva del contorno/espansione del controllo lingua;
- rifinitura del controllo lingua per evitare il bordo sdoppiato: il contorno viene disegnato da un solo guscio animato, mentre il pulsante interno resta trasparente e gestisce solo label/freccia;
- calibrazione dimensionale del controllo lingua per mantenere il selettore compatto, alto 36px e allineato al pulsante `Sign in`;
- allineamento tipografico e verticale del selettore lingua: la lingua selezionata e le opzioni sottostanti condividono la stessa scala testuale e lo stesso asse centrale, mentre la freccia non sposta piu il testo;
- rifinitura della spaziatura del selettore lingua: il triangolino viene separato dalla sigla selezionata e le opzioni del menu vengono centrate con margini laterali coerenti rispetto al bordo espanso;
- uniformazione del bordo del selettore lingua ai pulsanti della topbar: sostituita la finta linea via `box-shadow` con un bordo reale da 1px, coerente con `Sign in` e con gli altri controlli;
- riduzione del peso visivo del selettore lingua, con pill chiusa piu stretta e menu aperto meno alto, per non competere visivamente con `Sign in`;
- revisione finale della logica del selettore lingua: la versione incastonata e stata sostituita da un popover compatto, piu simile alla funzionalita iniziale e piu proporzionato rispetto al pulsante `Sign in`;
- ulteriore riduzione del selettore lingua a pill minimale senza freccia, mantenendo la sigla selezionata visibile e il menu cliccabile ma alleggerendo definitivamente la topbar;
- variabili CSS riutilizzabili `--control-expand-motion` e `--control-fade-motion`, pensate per mantenere coerenza nelle future animazioni di pulsanti/dropdown simili;
- supporto a `prefers-reduced-motion` per rispettare utenti che disattivano le animazioni di sistema.

Commit principali della fase UI iniziale:

| Commit | Contenuto |
|---|---|
| `1df670f` | Aggiunta prima interfaccia pubblica frontend |
| `51dafe1` | Aggiunta ricerca globale backend/frontend |
| `c280ef4` | Potenziamento ricerca globale con anni e alias paese |
| `d1a186f` | Autocomplete ricerca globale e matching ordinale |
| `c908dcc` | Correzione visibilita autocomplete ricerca |
| `e71f08c` | Introduzione splash iniziale e home centrata |
| `2a4dc9f` | Rifinitura intro home con topbar a tendina e wordmark ufficiale |
| `4e89b71` | Rifinitura styling dei controlli frontend |
| `535c42e` | Sostituzione del selettore lingua nativo con controllo custom |
| `1546cba` | Rimozione outline blu/focus non coerente |
| `e96c938` | Aggiunta dropdown di navigazione frontend |
| `e3b3e09` | Correzione evidenziazione persistente topbar |
| `f6a5665` | Impedisce ai dropdown topbar di restare aperti su focus |
| `92aa850` | Rimozione del riquadro pieno dalle voci topbar |
| `950b610` | Menu lingua incastonato nel controllo |
| `bbf1dbc` | Nasconde dal menu la lingua gia selezionata |
| `0bb81c1` | Animazione progressiva del controllo lingua |
| `a00add5` | Rimozione bordo sdoppiato dal controllo lingua |
| `9a5dce5` | Calibrazione dimensionale del controllo lingua |
| `e4ddac6` | Allineamento del controllo lingua al pulsante Sign in |
| `125ddc6` | Allineamento tipografico delle opzioni lingua |
| `252d78e` | Rifinitura spaziatura del dropdown lingua |
| `41535ff` | Uniformazione bordo del selettore lingua |
| `1c05880` | Riduzione del peso visivo del selettore lingua |
| `ee3f42e` | Ritorno a selettore lingua compatto con popover |
| `69cdee4` | Riduzione del selettore lingua a pill minimale |
| `2d512ad` | Ricerca globale strutturata per intento e autocomplete ordinato |
| `d2dff49` | Aggregazione reale dei filtri nella pagina risultati |
| `a66858e` | Correzione outlier punteggi e protezione import Gymternet |
| `9ef341b` | Rifinitura raggi visivi di card e pill dati frontend |
| `fb88ea7` | Separazione ranking globali per disciplina e ciclo di punteggio |
| `7e877c5` | Warning ranking calcolati sul contesto completo anche con risultati limitati |
| `30817a3` | Calendario mensile interattivo nella home |

Aggiornamento del 16 luglio 2026: ricerca globale strutturata

Problema emerso:

La ricerca globale non deve limitarsi a sommare risultati eterogenei provenienti da atleti, eventi, paesi, attrezzi e risultati. Deve invece comportarsi come un punto di accesso unico al patrimonio dati di LEVERAGE, capace di interpretare indicazioni composte inserite dall'utente nella barra di ricerca.

Esempio funzionale:

`Stefano Patron, Serie A 2026, volteggio`

La query viene interpretata come combinazione di tre intenzioni:

- atleta: `Stefano Patron`;
- evento/anno: `Serie A 2026`;
- attrezzo: `volteggio`, normalizzato semanticamente in `VT`.

Scelta progettuale adottata:

- il backend divide la query in blocchi semantici quando l'utente usa virgole;
- ciascun blocco viene analizzato per riconoscere testo libero, anni, paesi e alias degli attrezzi in inglese/italiano;
- i risultati vengono filtrati per intersezione logica tra i blocchi riconosciuti, evitando che una ricerca composta diventi una semplice somma disordinata di risultati;
- gli alias attrezzo come `volteggio`, `balance`, `trave`, `anelli`, `sbarra`, `parallele`, `corpo libero` vengono trattati come filtri sportivi e non come testo generico;
- il frontend ordina i suggerimenti in modo piu narrativo: prima la scheda entita principale, poi i risultati collegati, poi eventuali filtri/facet.

Motivazione semantica:

Questa scelta avvicina LEVERAGE al comportamento atteso da una piattaforma dati sportiva: l'utente non deve conoscere ID interni o parametri tecnici, ma puo scrivere una richiesta naturale e progressivamente precisa. La ricerca globale diventa quindi l'unione guidata di ricerca atleti, ricerca eventi e ricerca risultati.

Impatto funzionale:

- cercando un atleta, il primo suggerimento resta la scheda atleta;
- subito sotto compaiono i punteggi collegati all'atleta;
- cercando un evento, il primo suggerimento resta la scheda evento;
- cercando query composte, i risultati vengono filtrati su atleta, evento/anno e attrezzo quando questi elementi sono riconosciuti;
- la ricerca `Bundesliga 2` continua a riconoscere correttamente `2nd Bundesliga`;
- la ricerca per anno e paese continua a restituire eventi, atleti e risultati coerenti.

Verifiche:

- aggiunto test automatico sull'esempio `Stefano Patron, Serie A 2026, volteggio`;
- il test verifica che venga restituito solo il risultato `VT` dell'atleta corretto nell'evento corretto, escludendo risultati dello stesso atleta su altri attrezzi, risultati di altri atleti nello stesso evento e risultati dello stesso atleta in altri eventi;
- suite API verificata con `114 passed`.

Correzione successiva della stessa milestone:

E emersa una distinzione importante tra autocomplete e pagina dei risultati. I suggerimenti possono continuare a mostrare scorciatoie utili, come scheda atleta, scheda evento o facet attrezzo. Tuttavia, quando l'utente conferma una query composta, la pagina risultati non deve mostrare quelle entita come blocchi separati principali: deve mostrare i `Result` che soddisfano simultaneamente tutti i filtri riconosciuti.

Esempio:

`Stefano Patron, Serie A 2026, volteggio`

Comportamento corretto:

- autocomplete: puo aiutare l'utente mostrando atleta, evento e attrezzo riconosciuti;
- pagina risultati: mostra solo i risultati compatibili con `Stefano Patron` + `Serie A 2026` + `VT`;
- se non esistono risultati compatibili con tutti i filtri, la pagina mostra un messaggio dedicato invece di ripiegare su schede o facet generici.

Implementazione:

- aggiunto al payload globale il flag `structured_result_search`;
- la UI usa questo flag per renderizzare la pagina in modalita `Filtered results`;
- le sezioni separate `Athletes`, `Events`, `Countries`, `Apparatus` restano disponibili per ricerche semplici, ma non dominano piu le ricerche strutturate sui risultati;
- aggiunta verifica automatica che distingue ricerca semplice da ricerca composta.

Aggiornamento del 16 luglio 2026: coerenza dei bordi nei dati frontend

Problema emerso:

Nelle viste pubbliche iniziali, molti dati visualizzati in calendario, classifiche e risultati di ricerca apparivano dentro bordi troppo arrotondati, con un effetto "pillola" non sempre coerente con lo stile app scelto per LEVERAGE.

Scelta progettuale adottata:

- introdotte due variabili CSS condivise: `--surface-radius` per card/pannelli e `--data-chip-radius` per piccole etichette dati;
- ridotto il raggio delle `pill` usate per score, discipline, country, apparatus, stato calendario e conteggio risultati;
- normalizzato il raggio di card, pannelli, suggerimenti di ricerca e stato API compatto;
- aggiornato il cache-buster degli asset frontend per forzare il caricamento della versione corretta in anteprima locale.

Motivazione UI:

Lo stile deve restare morbido e riconoscibile come interfaccia moderna, ma i dati sportivi non devono apparire come pulsanti primari o capsule troppo evidenti. La gerarchia visiva diventa cosi piu chiara: i controlli restano controlli, mentre i metadati dei risultati diventano etichette leggere e ordinate.

Verifiche:

- server frontend locale verificato con risposta HTTP `200`;
- controllo `git diff --check` pulito;
- modifica salvata nel commit `9ef341b`.

Aggiornamento del 16 luglio 2026: classifiche globali, disciplina e cicli di punteggio

Problema emerso:

Le classifiche globali non devono mescolare automaticamente risultati MAG e WAG. Anche quando alcuni attrezzi hanno lo stesso nome, le regole e le scale di punteggio possono essere diverse. Inoltre, confrontare punteggi appartenenti a quadrienni/cicli di punteggio diversi puo essere utile come analisi storica, ma non deve avvenire senza avviso metodologico.

Cicli di punteggio definiti:

- `2017-2021`, esteso di un anno a causa dello slittamento olimpico legato al Covid;
- `2022-2024`;
- `2025-2028`;
- `2029-2032` e successivi, calcolati automaticamente con la stessa logica quadriennale.

Scelta progettuale adottata:

- aggiunto il modulo `app/scoring_cycles.py`, che ricava il ciclo di punteggio dall'anno dell'evento senza aggiungere campi al database;
- aggiunto il modulo `app/ranking_context.py`, condiviso dagli endpoint ranking;
- gli endpoint globali `/analytics/rankings` e `/results/analytics/rankings` richiedono ora `discipline=MAG` o `discipline=WAG`, salvo uso esplicito di `allow_mixed_disciplines=true`;
- se l'utente non imposta un periodo o un ciclo specifico, il backend applica di default il ciclo di punteggio piu recente disponibile nel set filtrato;
- l'opzione `include_all_scoring_cycles=true` permette analisi trasversali, ma il payload restituisce warning espliciti;
- i warning vengono calcolati sull'intero set filtrato prima del `limit`, cosi restano visibili anche quando la UI mostra solo una parte della classifica;
- il payload ranking include ora `discipline`, `scoring_cycle`, `available_scoring_cycles` e `warnings`.

Impatto UI:

- la pagina `Rankings` mostra MAG come default semantico quando l'utente non ha ancora scelto una disciplina;
- WAG resta selezionabile in modo esplicito;
- sono stati aggiunti controlli per `2017-2021`, `2022-2024`, `2025-2028` e `All cycles`;
- sopra le liste ranking viene mostrata una nota compatta con disciplina e ciclo applicato;
- in caso di confronto tra cicli o discipline diverse, la UI mostra i warning ricevuti dal backend.

Motivazione semantica:

La classifica deve essere un confronto sportivo coerente, non solo un ordinamento numerico. Separare disciplina e ciclo di punteggio riduce il rischio di confronti fuorvianti e prepara la futura UI a spiegare chiaramente quando una comparazione e interna allo stesso codice o quando serve solo come lettura storica/metodologica.

Verifiche:

- aggiunto test automatico `test_global_rankings_require_discipline_and_expose_scoring_cycle_context`;
- aggiornati i test esistenti per richiedere disciplina nelle ranking globali;
- suite completa verificata con `116 passed`;
- frontend locale verificato con risposta HTTP `200`;
- modifica salvata nel commit `fb88ea7`.
- correzione successiva salvata nel commit `7e877c5`: i warning metodologici restano calcolati sul contesto completo anche con `limit` basso.

Aggiornamento del 16 luglio 2026: calendario mensile interattivo nella home

Problema emerso:

L'anteprima calendario della home era ancora una lista di eventi. Questo rendeva meno immediata la lettura temporale delle competizioni, soprattutto per eventi multi-day e per piu eventi sovrapposti nello stesso periodo.

Scelta progettuale adottata:

- la home carica il mese corrente tramite `/events/calendar`, usando `start_date`, `end_date` e `as_of`;
- l'anteprima viene renderizzata come griglia mensile con settimane da lunedi a domenica;
- gli eventi con date precise vengono visualizzati come barre che attraversano le colonne dei giorni interessati;
- gli eventi sovrapposti vengono distribuiti su corsie separate, fino a quattro corsie visibili per settimana;
- se una settimana contiene piu eventi di quelli mostrabili, viene visualizzato un indicatore compatto `+N`;
- il giorno corrente viene evidenziato direttamente nel numero del giorno;
- gli eventi senza date precise non vengono posizionati nella griglia della home, per evitare una rappresentazione giornaliera falsa;
- il mese visualizzato puo essere cambiato dalla home con frecce precedente/successivo collocate accanto al nome del mese;
- il cambio mese aggiorna lo stato locale della home e ricarica da `/events/calendar` solo il range del nuovo mese, mantenendo indipendente la preview ranking;
- il giorno corrente espone una micro-etichetta localizzata (`Today`, `Oggi`, `Hoy`, `Aujourd'hui`) al passaggio del mouse e al focus da tastiera;
- la griglia home dedicata a calendario e ranking usa una proporzione specifica, separata dalla `content-grid` generale, per dare al calendario il ruolo visivo principale senza alterare le altre pagine.

Motivazione UI:

Il calendario e una delle viste centrali di LEVERAGE: non deve sembrare una lista secondaria, ma un vero strumento di orientamento nella stagione. La home mantiene comunque una versione compatta, mentre una futura pagina `Events/Calendar` potra espandere la stessa logica con navigazione mese/anno, filtri piu ricchi e viste admin.

La navigazione mese-per-mese anticipa il comportamento della futura pagina calendario completa senza appesantire la home: l'utente puo esplorare rapidamente eventi passati e futuri, mentre la UI resta minimal e coerente con i controlli arrotondati in stile app scelti per LEVERAGE.

La micro-etichetta sul giorno corrente rende piu leggibile il significato dell'evidenziazione blu senza aggiungere testo fisso nella griglia, mantenendo la schermata pulita.

Il ribilanciamento calendario/ranking risponde alla nuova gerarchia della home: il calendario non e piu una semplice lista di eventi ma una vista interattiva, quindi richiede piu ampiezza per mostrare sovrapposizioni e barre multi-day; la ranking resta utile come anteprima sportiva, ma non deve competere visivamente con il calendario.

Aggiornamento successivo:

- la pagina `Events` usa la stessa logica calendario della home, ma in versione piu ampia, con piu corsie evento visibili per settimana;
- la legenda distingue risultati disponibili, risultati mancanti, evento in corso ed evento futuro;
- `/events/calendar` non legge piu soltanto la tabella `events`, ma integra anche `event_calendar_entries`;
- le righe `calendar_only` vengono restituite con `id = null`, `calendar_entry_id` valorizzato e `is_calendar_only = true`, cosi la UI puo mostrarle nel calendario senza rimandare a una scheda evento inesistente;
- gli `Event` senza date precise non vengono piu inseriti nei range mensili come se durassero tutto l'anno: nel calendario mensile compaiono solo eventi con date reali o voci `EventCalendarEntry`;
- la verifica sul database locale al 16 luglio 2026 ha confermato che, dopo tale data, risultava presente un solo evento futuro datato (`British Team Championships`) e nessuna riga futura `calendar_only`; quindi l'assenza di altri futuri senza risultati dipendeva dai dati effettivamente materializzati nel DB, non solo dalla UI.
- i filtri calendario `MAG`/`WAG` e `junior`/`senior` sono diventati multi-selezione;
- il backend tratta i valori aggregati in modo inclusivo: `MAG and WAG` e compatibile con il filtro `MAG` e con il filtro `WAG`, mentre `junior and senior` e compatibile con il filtro `junior` e con il filtro `senior`;
- il pulsante localizzato `Today` / `Oggi` riporta il calendario visualizzato al mese corrente, sia nella preview home sia nella vista completa `Events`.

Aggiornamento UI successivo:

- i filtri calendario includono ora anche lo stato dell'evento: con risultati, risultati mancanti, in corso, in programma;
- il filtro di stato viene passato a `/events/calendar`, quindi funziona anche per eventi futuri o in corso privi di Results;
- il pulsante `Today` / `Oggi` e stato spostato piu a destra, dopo la freccia di avanzamento mese, per renderlo meno compresso vicino al nome del mese;
- nella pagina `Rankings`, MAG/WAG non sono piu due bottoni apparentemente multi-selezionabili: sono un controllo segmentato esclusivo, coerente con la scelta semantica di non mischiare classifiche MAG e WAG.
- la `Ranking preview` della home e stata riallineata all'altezza dell'anteprima calendario: il riquadro segue la lunghezza del calendario e contiene la ranking completa in uno scroll interno, senza allungare la sezione home.
- i filtri categoria del calendario ora usano una categoria effettiva calcolata anche dal nome della voce calendario: una riga come `Chinese Junior Championships`, anche se collegata a un Event piu ampio `junior and senior`, viene filtrata e restituita come `junior` e non compare piu con filtro `senior`.
- il CORS di sviluppo accetta ora anche `http://localhost:5174` e `http://127.0.0.1:5174`, cosi la preview frontend puo usare una porta alternativa quando `5173` e occupata senza generare errori `Load failed`.
- il riquadro dei suggerimenti della ricerca globale e stato mantenuto largo quanto l'intera search form, fino al pulsante `Search`, con testi e spaziatura piu leggibili e coerenti con la dimensione della digitazione.
- l'input interno della barra di ricerca e stato reso trasparente e senza focus ring proprio: quando l'utente scrive, l'evidenza visiva resta sulla barra esterna e non compare piu un riquadro grigio interno piu alto del pulsante `Search`.
- nel calendario, il titolo del mese e stato separato in mese e anno su due righe dentro un contenitore a larghezza stabile, evitando che le frecce di navigazione si spostino quando cambia la lunghezza del nome del mese.

Correzione dati successiva:

- dal file `import_files/Calendar.xlsx` sono state lette 45 righe Calendar 2026 future dal 16 luglio 2026 in poi;
- 42 righe sono state materializzate come nuovi `Event` futuri senza Results;
- `British Team Championships` era gia presente e non e stato duplicato;
- `3rd Bundesliga` e `4th Bundesliga` avevano gia Event con risultati e date di aprile: le nuove date future sono state salvate come `EventCalendarEntry`, preservando le date originali degli Event popolati;
- dopo la correzione, il calendario pubblico restituisce eventi futuri fino a dicembre 2026, inclusi U.S. Classic, Commonwealth Games, European Championships, World Championships, Youth Olympic Games e All-Japan Team & Event Championships.

Correzione semantica successiva:

- tutti gli Event contenenti `Youth` nel nome devono essere interpretati come junior;
- la regola di inferenza dell'import Calendar e stata aggiornata: `Youth` vale come indicatore junior, analogamente a `Junior`;
- nel database locale sono stati corretti 5 Event precedentemente classificati come `junior and senior` e 191 Result collegati, ora coerenti con `category = junior`;
- l'intervento e stato registrato nel report `docs/import_reports/youth_category_correction_20260716.json`.

Verifiche:

- endpoint calendario mese corrente verificato con risposta HTTP `200`;
- frontend locale verificato con risposta HTTP `200`;
- controllo `git diff --check` pulito;
- runtime JavaScript locale non disponibile (`node`, `deno` e `bun` assenti), quindi la validazione sintattica JS e stata sostituita da ispezione del diff e verifica via preview servita;
- suite completa backend verificata con `117 passed`;
- modifica salvata nel commit `30817a3`.
- navigazione mese calendario salvata nel commit `2abbea1`;
- tooltip localizzato del giorno corrente salvato nel commit `f1166ce`;
- ribilanciamento layout calendario/ranking salvato nel commit `d7d603e`;
- calendario completo e supporto `EventCalendarEntry` salvati nel commit `2f9127e`;
- filtri calendario multi-selezione e pulsante ritorno a oggi salvati nel commit `2b9bd88`;
- materializzazione eventi futuri Calendar 2026 eseguita con report `calendar_2026_future_materialization_commit_summary.json`;
- correzione semantica `Youth = junior` verificata sui dati locali e tracciata nel report `youth_category_correction_20260716.json`;
- filtro calendario `senior` verificato sul caso `Chinese Junior Championships`: la voce non compare piu tra gli eventi senior e resta disponibile nel filtro `junior`;
- endpoint calendario verificato anche su un mese diverso con risposta HTTP `200`.

Aggiornamento del 16 luglio 2026: correzione outlier nella ranking preview

Problema emerso:

Nella `Ranking preview` della home comparivano tre punteggi impossibili per la ginnastica artistica:

- Daniel Serban, German Junior Championships 2023, PB: `1205.0`;
- Keisuke Komori, All-Japan Team Championships 2021, FX: `142.33`;
- Silas Bortt, 4th Bundesliga 2021, PB: `110.65`.

Controllo effettuato:

- i valori erano realmente presenti nel database, quindi l'errore non era nella classifica ma nel dato importato;
- le stesse anomalie erano presenti nelle celle sorgenti dei file Gymternet normalizzati;
- lo scan completo del database ha individuato solo tre `score > 100`;
- e stato individuato anche un `D_score > 20`, relativo a Elene Sanna UB (`22.0`), corretto per evitare futuri errori nelle classifiche per D-score.

Correzioni applicate:

| Result ID | Campo | Da | A | Fonte |
|---:|---|---:|---:|---|
| `416930` | `score` | `1205.0` | `12.05` | `Results 2023.xlsx`, MAG row 2352 |
| `246431` | `score` | `142.33` | `14.233` | `Results 2021.xlsx`, MAG row 3639 |
| `260503` | `score` | `110.65` | `11.065` | `Results 2021.xlsx`, MAG row 6784 |
| `278214` | `D_score` | `22.0` | `2.2` | `Results 2021.xlsx`, WAG D row 1908 |

Scelta progettuale:

- la correzione non e stata fatta in modo opaco: e stato creato lo script `scripts/repair_known_result_score_outliers.py`;
- lo script controlla `result_id` e valore atteso prima di aggiornare il DB;
- prima dell'applicazione e stato creato il backup locale `backups/leverage_before_score_outlier_repair_20260716_101004.db`;
- il report tracciabile e stato salvato in `docs/import_reports/result_score_outlier_repair_20260716.csv`.

Protezione futura:

Il parser Gymternet ora intercetta outlier evidenti durante l'import:

- final score AA sopra `100`;
- final score non-AA sopra `20`;
- D-score sopra `20`.

Quando possibile, il parser corregge automaticamente il decimale mancante dividendo per `10`, `100` o `1000` e registra un warning nel report import. Se non trova una correzione plausibile, registra un errore.

Verifiche:

- dopo la correzione: `score > 100 = 0`;
- dopo la correzione: `D_score > 20 = 0`;
- la ranking preview torna a mostrare punteggi AA plausibili, con Zhang Boheng `89.299` come primo risultato;
- aggiunto test automatico `test_gymternet_parser_corrects_clear_score_outliers`;
- suite API verificata con `115 passed`.

Decisione metodologica per la tesi:

Da questa milestone in poi, ogni sviluppo UI/UX significativo deve essere annotato nel diario di bordo e nei file di avanzamento del progetto, includendo:

- richiesta o problema da risolvere;
- scelta progettuale adottata;
- motivazione semantica/funzionale;
- impatto su frontend, backend o modello dati;
- commit Git rilevanti;
- eventuali limiti o sviluppi successivi.

Valutazione di avanzamento aggiornata al 15 luglio 2026:

| Area | Avanzamento stimato |
|---|---:|
| Backend core e modello dati | 92% |
| Import storico Gymternet | 97% |
| Popolamento dati 2018-2025 | 100% |
| Popolamento dati 2026 primo semestre | 100% |
| Riconciliazione Calendar 2018-2025 | 100% |
| Riconciliazione Calendar 2026 primo semestre | 100% |
| Documentazione tecnica/tesi della fase dati | 94% |
| Backend pronto per UI MVP | 82% |
| Frontend/UI pubblica iniziale | 12% |
| UI admin | 0% |
| Deploy online produzione | 0% |
| MVP online complessivo | 76% |

Aggiornamento ricerca globale:

- verificato il caso reale `Stefano Patron, FX, Bundesliga 2025`: nel database locale l'atleta Stefano Patron non ha risultati associati a eventi Bundesliga 2025, quindi la combinazione completa non produce risultati esatti;
- confermata la regola semantica che `Bundesliga 2025` deve trovare eventi e risultati di tutte le gare il cui nome contiene `Bundesliga` nell'anno 2025, anche se il nome ufficiale e piu specifico (`1st Bundesliga`, `2nd Bundesliga`, `Bundesliga Finals`, ecc.);
- introdotta la distinzione tra `results` e `related_results` nella ricerca globale: `results` contiene solo i risultati che rispettano tutti i filtri della query, mentre `related_results` mostra risultati collegati alla parte evento/anno/attrezzo quando la combinazione completa e vuota;
- aggiornata la UI affinche, in caso di ricerca composta senza risultati esatti, non nasconda i match parziali utili: vengono mostrati atleta, eventi, attrezzi e risultati collegati, evitando che l'utente interpreti erroneamente la risposta come assenza totale di dati;
- aggiunta copertura di test sul caso `Bundesliga 2025` e sul fallback di ricerca strutturata senza risultati esatti.
- raffinata la home search: i filtri principali sono stati spostati sopra la barra di ricerca, cosi restano sempre visibili anche quando si apre il riquadro autocomplete; il riquadro dei suggerimenti e stato allargato fino ai bordi esterni della search form, includendo visivamente anche l'area del pulsante `Search`.
- rifinita la sequenza iniziale della home: il tempo di presenza del logo LEVERAGE e stato mantenuto sostanzialmente invariato, ma topbar e contenuto principale vengono anticipati durante la chiusura dello splash, riducendo il tempo percepito di pagina bianca prima della comparsa della home.
- semplificata la ricerca globale della home: rimane una barra unica, pulita e non filtrata, mentre i pulsanti filtro sono riservati alle sezioni dedicate (`Athletes`, `Events`, `Rankings`, `Analytics`). Le preview della home non ereditano piu filtri invisibili dallo stato delle altre pagine.
- separato lo stato dei filtri per sezione: i filtri selezionati in `Athletes`, `Events` e `Rankings` sono indipendenti e non influenzano automaticamente le altre sezioni. Esempio: selezionare `WAG` in `Athletes` non attiva `WAG` in `Events`.
- resa piu intelligente la ricerca globale sugli eventi: abbreviazioni e nomi d'uso comune come `europeans`/`euros` vengono ricondotti a `European Championships`, mentre `worlds`/`world champs` vengono ricondotti a `World Championships`, cosi l'utente non deve conoscere il nome ufficiale esatto della gara. Il backend assegna inoltre priorita ai nomi ufficiali esatti rispetto a eventi correlati ma meno pertinenti.
- rimossi dalla UI pubblica gli indicatori tecnici di sviluppo come `API status`, stato online/offline del backend e messaggi che invitavano ad avviare FastAPI. Gli errori di caricamento dati vengono ora mostrati con un messaggio neutro e contestuale, senza esporre dettagli tecnici all'utente finale.
- rifinito il riquadro autocomplete della ricerca globale: caratteri di `Loading` e suggerimenti resi piu coerenti con la dimensione del testo digitato, pannello reso meno invasivo in altezza e scrollabile quando sono disponibili piu suggerimenti.
- regolata l'altezza del riquadro autocomplete affinche mostri quattro suggerimenti completi senza tagliare visivamente il record successivo; ulteriori suggerimenti restano disponibili tramite scroll interno.
- corretto il comportamento del riquadro autocomplete nella home: quando i suggerimenti sono aperti, la sezione successiva viene spinta verso il basso con spazio riservato dinamicamente, evitando che il pannello si sovrapponga alla sezione `Start with the data`.
- rifinita la responsivita della home: logo LEVERAGE, sottotitolo, testo descrittivo e barra di ricerca seguono ora breakpoint coerenti su desktop stretto, tablet e mobile, evitando che un elemento si riduca mentre gli altri mantengono proporzioni da desktop.
- resa piu interattiva la ricerca dedicata della sezione Athletes: la digitazione filtra direttamente la griglia delle schede atleta, senza pannello suggerimenti separato, mantenendo solo gli atleti coerenti con nome, cognome o ID e rispettando i filtri di disciplina della sezione.
- verificata e stabilizzata la ricerca composta nella sezione Athletes: query come `Stefano Patron`, `Patron Stefano` o l'ID atleta mantengono la scheda corretta anche al termine della digitazione; il frontend usa inoltre l'endpoint con slash finale per evitare redirect intermedi durante il filtro live.
- aggiunti i filtri `Junior` e `Senior` nella sezione Athletes: la categoria resta semanticamente derivata dai Result dell'atleta, non da un campo fisso dell'entita Athlete, cosi un ginnasta puo essere trovato in base alle categorie in cui ha effettivamente gareggiato.
- distinto il placeholder della ricerca Athletes dalla ricerca globale: la barra dedicata agli atleti comunica ora esclusivamente ricerca per nome, ID o nazione, evitando riferimenti fuorvianti a eventi, classifiche o attrezzi.
- resa piu intelligente la ricerca per nazione nella sezione Athletes: i nomi paese e gli alias multilingua vengono normalizzati verso i codici country salvati nel database, cosi ricerche come `Italy`, `Italia`, `United States` o `Germania` restituiscono gli atleti collegati ai codici `ITA`, `USA` o `GER`.
- rifinita la home page rinominando le anteprime in `Calendar` e `Ranking` e stabilizzando il pulsante `View all`, ora centrato e contenuto correttamente nel controllo senza sbordature.

Aggiornamento UI sezione Events del 20 luglio 2026:

- aggiunta una barra di ricerca dedicata nella sezione `Events`, separata dalla ricerca globale della home e dai filtri delle altre sezioni;
- la ricerca Eventi aggiorna in tempo reale la lista delle competizioni durante la digitazione, in modo analogo alla griglia live della sezione `Athletes`;
- la lista Eventi usa l'endpoint calendario `/events/calendar`, non solo `/events/`, cosi puo mostrare sia gare collegate a una scheda evento sia righe calendar-only senza risultati o senza entita evento cliccabile;
- le gare nella lista sono visualizzate con periodo leggibile, sede/venue quando disponibili, disciplina, categoria, livello e indicazione `Calendar only` quando non esiste una scheda evento collegata;
- esteso il backend del calendario con parametro `search`, capace di leggere anno, nome competizione, sede/venue, alias paese e alias semantici di competizioni;
- introdotta la comprensione di query localizzate come `Europei 2025`, `Mondiali 2025`, `europeans`, `worlds`, ecc., ricondotte rispettivamente a `European Championships` e `World Championships`;
- i filtri `MAG`, `WAG`, `Junior`, `Senior` e stato calendario restano coerenti tra calendario visuale e lista live, senza influenzare le ricerche di `Athletes`, `Rankings` o della home;
- aggiunti test automatici per verificare che la ricerca eventi capisca alias localizzati e anni, e che la ricerca calendario trovi anche competizioni calendar-only.
- rifinita la gerarchia della pagina `Events`: i risultati della barra di ricerca sono stati spostati sopra il calendario, rendendo la ricerca competizioni il primo output visibile dopo la digitazione;
- aggiunti filtri per livello competizione nella sezione `Events`, mappati ai valori dell'entita `Event`: `Olympic Games`, `World Championships`, `Continental Championships`, `World Cup`, `World Challenge Cup`, `International Event`, `National Event`;
- in UI i livelli `World Cup` e `World Challenge Cup` sono presentati come `FIG World Cups` e `FIG Challenge`, mantenendo nel backend i valori ufficiali del modello dati;
- il backend `/events/` e `/events/calendar` accetta ora piu livelli selezionati insieme, sia come parametri ripetuti sia come valori separati da virgola;
- aggiunta copertura test per filtri livello su lista eventi e calendario, incluse le righe calendar-only.

Aggiornamento UI/semantica sezione Rankings del 20 luglio 2026:

- aggiunti filtri attrezzo nella sezione `Rankings`, dinamici in base alla disciplina selezionata;
- con disciplina `MAG` vengono mostrati solo `FX`, `PH`, `SR`, `VT`, `PB`, `HB`;
- con disciplina `WAG` vengono mostrati solo `VT`, `UB`, `BB`, `FX`;
- i filtri attrezzo possono essere combinati tra loro, cosi l'utente puo confrontare ranking limitati a uno o piu apparatus senza mischiare attrezzi non desiderati;
- i cicli olimpici/scoring cycles sono ora selezionabili in combinazione multipla, mantenendo il warning quando la classifica include punteggi appartenenti a codici di punteggio diversi;
- il filtro `All cycles` mantiene il significato di confronto trasversale intenzionale: quando e attivo, la UI mostra tutti i pulsanti ciclo come selezionati e il backend riceve `include_all_scoring_cycles=true`;
- il backend `/analytics/rankings` e l'endpoint parallelo `/results/analytics/rankings` accettano ora piu valori `apparatus` e piu valori `scoring_cycle`, sia come parametri ripetuti sia come valori separati da virgola;
- aggiunti test automatici per ranking su piu cicli e su piu attrezzi.

## 19. Conclusione

LEVERAGE oggi non e piu solo un backend CRUD: e diventato un sistema dati strutturato per ginnastica artistica, con modello semantico forte, import assistito, validazioni sportive, gestione qualita dato, preferenze utente, notifiche, analytics, strumenti admin e una base storica consistente.

La fase di trasformazione del backend in piattaforma web utilizzabile e ora iniziata con una prima UI pubblica minimal. I prossimi sviluppi dovranno consolidare frontend pubblico, area utente, area admin, calendario interattivo, schede atleta, schede evento, grafici, deploy online e gestione produzione.
