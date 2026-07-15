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
- collegamento agli endpoint pubblici per mostrare preview Calendar e Ranking;
- pagine iniziali per `Athletes`, `Events`, `Rankings`, `Analytics` e `Login`;
- footer con configurazione locale dell'API base;
- gestione lingua `EN / IT / ES / FR` tramite local storage;
- menu di navigazione a tendina per `Athletes`, `Events`, `Rankings`, `Analytics`, con azioni principali visibili al passaggio del mouse;
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
| `4e89b71` | Rifinitura styling dei controlli frontend |
| `535c42e` | Sostituzione del selettore lingua nativo con controllo custom |
| `1546cba` | Rimozione outline blu/focus non coerente |
| `e96c938` | Aggiunta dropdown di navigazione frontend |
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

## 19. Conclusione

LEVERAGE oggi non e piu solo un backend CRUD: e diventato un sistema dati strutturato per ginnastica artistica, con modello semantico forte, import assistito, validazioni sportive, gestione qualita dato, preferenze utente, notifiche, analytics, strumenti admin e una base storica consistente.

La fase di trasformazione del backend in piattaforma web utilizzabile e ora iniziata con una prima UI pubblica minimal. I prossimi sviluppi dovranno consolidare frontend pubblico, area utente, area admin, calendario interattivo, schede atleta, schede evento, grafici, deploy online e gestione produzione.
