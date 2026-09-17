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
- salvare eventi come preferiti;
- salvare anche eventi futuri;
- vedere dettagli degli atleti seguiti;
- vedere dettagli degli eventi preferiti;
- salvare viste dashboard personali con filtri e configurazioni.

Entita introdotte:

- `FollowedAthlete`
- `SavedEvent`
- `SavedDashboardView`

La dashboard personale futura potra usare questi dati per mostrare:

- atleti seguiti;
- ultimi risultati;
- eventi preferiti;
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
- `preferences.py`: lingua, atleti seguiti, eventi preferiti, dashboard views.
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
- eventi preferiti;
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
- salvare eventi come preferiti;
- salvare eventi futuri;
- consultare dettagli degli atleti seguiti;
- consultare dettagli degli eventi preferiti;
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

Aggiornamento del 23 luglio 2026: controllo outlier `score > 20` sui result non-AA

Problema emerso:

- nella UI e stato notato un punteggio VT impossibile: Giuseppe Bertoli, `Champion's Cup` 2026, `VT`, `score = 24.5`;
- il nome corretto nel database e nella sorgente risulta `Giuseppe Bertoli`;
- il result derivava dal file `Results 2026.xlsx`, sheet `MAG`, row `2969`.

Analisi effettuata:

- il database conteneva `VT attempt 1 = 1.2` e `VT AVG = 12.85`;
- il tool Gymternet legacy aveva calcolato automaticamente `VT attempt 2 = (2 * VT AVG) - VT1 = 24.5`;
- il problema non era quindi una classifica sbagliata, ma una derivazione matematica basata su un typo sorgente: `VT 1.2` doveva essere interpretato come `13.2`;
- con `VT1 = 13.2`, il valore coerente di `VT attempt 2` diventa `12.5`;
- il `D_score` resta coerente con `VT SUM D = 7.6`, cioe `VT1 D = 4.4` e `VT2 D = 3.2`.

Correzioni applicate:

| Result ID | Campo | Da | A | Fonte |
|---:|---|---:|---:|---|
| `765954` | `score` | `1.2` | `13.2` | `Results 2026.xlsx`, MAG row 2969 |
| `765956` | `score` | `24.5` | `12.5` | `Results 2026.xlsx`, MAG row 2969 |

Tracciabilita:

- lo script `scripts/repair_known_result_score_outliers.py` e stato esteso con le due correzioni note;
- prima della modifica e stato creato il backup locale `backups/leverage_before_score_outlier_repair_20260723_123228.db`;
- il report di riparazione e stato salvato in `docs/import_reports/result_score_outlier_repair_20260723.csv`;
- il report di audit residuo e stato salvato in `docs/import_reports/result_score_outlier_audit_20260723.csv`.

Protezione futura:

- il parser Gymternet legacy ora blocca i `VT attempt 2` derivati quando il calcolo produce un final score non-AA superiore a `20.0`;
- in questi casi il dato derivato non viene importato e viene registrato un errore nel report import, cosi l'admin puo verificarlo;
- gli endpoint admin di creazione e bulk manuale result ora rifiutano final score non-AA superiori a `20.0`;
- la migration Alembic `0030_add_result_score_upper_bounds` aggiunge vincoli DB per bloccare score non-AA sopra `20.0` e `D_score` sopra `10.0`;
- `AA` resta escluso dal limite perche e un totale all-around.

Verifiche:

- dopo la correzione: result non-AA con `score > 20` = `0`;
- dopo la seconda correzione: result con `D_score > 10` = `0`;
- aggiunti test automatici `test_gymternet_pivot_vault_skips_derived_attempt_two_score_outlier` e `test_result_entry_rejects_non_aa_scores_above_twenty_but_allows_aa_totals`.

Seconda correzione collegata:

I quattro casi residui di `D_score > 10` sono stati confermati come errori, perche il D-score salvato nel modello LEVERAGE non puo superare `10.0`.

| Result ID | Athlete | Event | Campo | Da | A |
|---:|---|---|---|---:|---|
| `186011` | Ruby van Dijk | `2nd Bundesliga` 2019 | `D_score` | `12.8` | `NULL` |
| `241232` | Ham Chaewoo | `South Korean Championships` 2021 | `D_score` | `11.5` | `NULL` |
| `260730` | Son Euidam | `South Korean Championships` 2021 | `D_score` | `11.6` | `NULL` |
| `298429` | Petra Fanesi | `Italian Gold Championships` 2021 | `D_score` | `13.0` | `NULL` |

La scelta e stata di non inventare valori alternativi: quando un D-score sopra `10.0` non ha una correzione certa, il campo diventa `not available`.

Tracciabilita aggiuntiva:

- backup: `backups/leverage_before_score_outlier_repair_20260723_125046.db`;
- report riparazione: `docs/import_reports/result_dscore_outlier_repair_20260723.csv`;
- audit post-riparazione: `docs/import_reports/result_dscore_outlier_audit_post_repair_20260723.csv`.

Aggiornamento del 29 luglio 2026: controllo `E_score` e `execution_estimate` nel range `0-10`

Problema emerso:

- durante il controllo UI dei `Rankings` e stata individuata la possibilita di visualizzare valori di `E Score` fuori scala;
- semanticamente `E_score` ufficiale deve essere sempre compreso tra `0` e `10`;
- nei dati LEVERAGE va distinta l'esecuzione ufficiale salvata nel campo `E_score` dalla stima `execution_estimate = score - D_score`, usata per i dati Gymternet legacy quando `E_score` non e disponibile.

Audit effettuato:

- `E_score` ufficiali fuori scala nel database: `0`;
- `execution_estimate` fuori scala nel database: `527`;
- i casi fuori scala derivavano da `D_score` incoerenti rispetto al final score: alcuni producevano una stima negativa, altri una stima superiore a `10`;
- la scelta conservativa e stata di non inventare correzioni automatiche del tipo `0.52 -> 5.2`, perche senza controllo della fonte sarebbe una deduzione non sufficientemente robusta.

Correzione applicata:

- per i 527 result coinvolti e stato mantenuto il final score;
- il campo `D_score` e stato impostato a `NULL` / `not available`, cosi il result resta consultabile ma non alimenta piu medie D-score, ranking D-score o ranking `execution_estimate`;
- `execution_estimate` non viene salvata come valore ufficiale e ora viene restituita solo se il calcolo `score - D_score` produce un valore tra `0` e `10`.

Tracciabilita:

- creato lo script `scripts/repair_result_e_score_outliers.py`, con modalita dry-run/apply, backup automatico e report CSV;
- dry-run: `docs/import_reports/result_e_score_outlier_repair_dry_run_20260729.csv`;
- backup prima dell'applicazione: `backups/leverage_before_e_score_outlier_repair_20260729_183835.db`;
- report riparazione: `docs/import_reports/result_e_score_outlier_repair_20260729.csv`;
- audit post-riparazione: `docs/import_reports/result_e_score_outlier_audit_post_repair_20260729.csv`.

Protezione futura:

- aggiunto in `schemas.py` il vincolo `E_score <= 10`;
- aggiunto nel modello SQLAlchemy il check `ck_results_e_score_upper_bound`;
- aggiunta la migration Alembic `0031_add_result_e_score_upper_bound`;
- aggiornato il parser Gymternet legacy: se un D-score importato insieme al final score produrrebbe una `execution_estimate` fuori range `0-10`, il D-score viene scartato e il caso viene notificato negli issues dell'import;
- aggiunti test automatici per bloccare `E_score > 10`, stime di esecuzione impossibili e D-score Gymternet che produrrebbero una stima non valida.

Verifiche:

- dopo la correzione: `E_score` fuori scala = `0`;
- dopo la correzione: `execution_estimate` fuori scala = `0`;
- il database locale e stato migrato fino a `0031_add_result_e_score_upper_bound`.

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
- uniformata la barra di ricerca della sezione `Athletes` allo stile delle altre sezioni, separando la search bar dai filtri e rendendo stabile il campo durante la digitazione live;
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
- in UI i livelli competizione restano presentati con le stesse etichette del backend, senza rinominare `World Cup` o `World Challenge Cup`;
- il backend `/events/` e `/events/calendar` accetta ora piu livelli selezionati insieme, sia come parametri ripetuti sia come valori separati da virgola;
- nella UI `Events`, i filtri per livello competizione sono stati raccolti in un menu compatto `Level` a selezione multipla, per ridurre rumore visivo e rendere piu ordinata la fascia filtri senza perdere la possibilita di combinare piu livelli;
- aggiunta copertura test per filtri livello su lista eventi e calendario, incluse le righe calendar-only.
- resa piu smart la ricerca gare in `Events` e nella ricerca globale: il matching degli eventi non dipende piu solo dall'ordine esatto delle parole salvate nel database;
- introdotto token matching order-insensitive per i nomi gara, sede, venue e livello evento: query come `World Cup Cottbus` trovano correttamente eventi salvati come `Cottbus World Cup`, anche con anno esplicito;
- aggiunti alias semantici per query utente come `FIG Cup Paris`, ricondotte al contesto `World Cup`, cosi l'utente non deve conoscere la nomenclatura esatta con cui l'evento e registrato in LEVERAGE.

Aggiornamento UI/semantica sezione Rankings del 20 luglio 2026:

- aggiunti filtri attrezzo nella sezione `Rankings`, dinamici in base alla disciplina selezionata;
- con disciplina `MAG` vengono mostrati `AA`, `FX`, `PH`, `SR`, `VT`, `PB`, `HB`, con `VT AVG` collocato dopo l'ultimo attrezzo specifico;
- con disciplina `WAG` vengono mostrati `AA`, `VT`, `UB`, `BB`, `FX`, con `VT AVG` collocato dopo l'ultimo attrezzo specifico;
- i filtri attrezzo possono essere combinati tra loro, cosi l'utente puo confrontare ranking limitati a uno o piu apparatus senza mischiare attrezzi non desiderati;
- i cicli olimpici/scoring cycles sono ora selezionabili in combinazione multipla, mantenendo il warning quando la classifica include punteggi appartenenti a codici di punteggio diversi;
- il filtro `All cycles` mantiene il significato di confronto trasversale intenzionale: quando e attivo, la UI mostra tutti i pulsanti ciclo come selezionati e il backend riceve `include_all_scoring_cycles=true`;
- nella UI `Rankings`, i cicli olimpici/scoring cycles sono stati raccolti in un menu compatto analogo al filtro `Level` della sezione `Events`, rinominato user-facing in `Olympic cycle`/`Ciclo olimpico` e mantenendo la selezione multipla con la logica speciale di `All cycles`;
- il backend `/analytics/rankings` e l'endpoint parallelo `/results/analytics/rankings` accettano ora piu valori `apparatus` e piu valori `scoring_cycle`, sia come parametri ripetuti sia come valori separati da virgola;
- aggiunti test automatici per ranking su piu cicli e su piu attrezzi.
- le card della sezione `Rankings` mostrano ora la composizione del punteggio per i risultati non-AA: `D`, `E est.`, `P`, `B`, con valori `not available` o `not applicable` quando coerente con lo stato del dato;
- per i ranking `AA`, il backend espone `apparatus_scores`, cioe i punteggi sui singoli attrezzi collegati allo stesso atleta/evento/format/round/categoria/giorno che compongono il totale all-around, e la UI li mostra direttamente nella card.
- ogni record visualizzato nella sezione `Rankings` espone ora anche l'anno della gara e, quando disponibile, la data dell'evento, cosi l'utente puo contestualizzare immediatamente il punteggio;
- introdotto nella UI un filtro `Period`/`Periodo` per le classifiche: l'utente puo selezionare un anno intero, un intervallo di anni o un intervallo preciso tra due date;
- quando viene selezionato un intervallo temporale specifico, la UI svuota il filtro ciclo olimpico per evitare sovrapposizioni implicite tra filtri; il backend continua comunque a segnalare quando il ranking include piu scoring cycles;
- l'endpoint `/analytics/rankings` valida ora gli intervalli temporali incoerenti, rifiutando `end_year < start_year` o `end_date < start_date`.
- aggiunta gestione semantica specifica per Vault nei ranking: `VT` e `VT AVG` sono filtri distinti, cosi il salto singolo non viene mescolato con la media dei due salti;
- il backend espone ora `vt_attempt` anche nei record di ranking; nella UI `VT 1` resta visualizzato come semplice `VT` fuori dal contesto Vault, mentre `VT 1` e `VT 2` vengono mostrati quando l'utente filtra esclusivamente il ranking su `VT`;
- nella composizione dei punteggi `AA`, un componente Vault attempt 1 viene mostrato come `VT`, mentre un eventuale attempt 2 resta distinguibile come `VT 2`.
- quando l'utente visualizza un ranking `VT AVG`, la scheda punteggio mostra ora anche i dettagli dei due salti collegati (`VT 1` e `VT 2`), includendo per ciascuno score e componenti `D`, `E est.`, `P`, `B` quando disponibili.
- alleggerita l'anteprima `Ranking` in homepage: le card mostrano solo il final score, senza composizione dettagliata del punteggio, mantenendo i dettagli completi nella sezione `Rankings`.
- aggiornata la frase principale della homepage in inglese, sostituendo `rankings` con `results` e rimuovendo il termine `curated`; la nuova copy enfatizza una base dati strutturata per analisi, confronto e contesto.

Aggiornamento navigazione pubblica del 20 luglio 2026:

- aggiunta la voce `Home` nella topbar principale, prima di `Athletes`, `Events`, `Rankings` e `Analytics`;
- la voce `Home` risulta attiva sia nella homepage sia nella pagina di ricerca globale `#/search`, rendendo piu chiaro all'utente che la ricerca globale appartiene all'area generale di ingresso alla piattaforma.
- nella topbar principale la voce `Rankings` resta invariata in tutte le lingue, analogamente ad `Analytics`, per mantenere coerenza terminologica nella navigazione principale.
- estesa la stessa scelta terminologica anche alla sezione `Rankings`: il nome della sezione non viene tradotto in `Classifiche`/`Classements`, mentre il termine classifica resta riservato alle classifiche evento.

Aggiornamento area utente e preferenze del 21 luglio 2026:

- collegato il frontend al sistema di autenticazione gia implementato nel backend tramite login email/password, eventuale secondo step MFA per account admin gia configurati e salvataggio locale del token JWT;
- la topbar distingue ora utente non loggato e utente loggato: `Sign in` rimanda al login, mentre un utente autenticato vede `My LEVERAGE`;
- creata una prima area privata `My LEVERAGE`, dedicata a preferenze personali e scorciatoie utente;
- l'area privata mostra gli atleti preferiti derivati dalla tabella `FollowedAthlete` e gli eventi preferiti derivati dalla tabella tecnica `SavedEvent`, senza introdurre duplicazioni nel modello dati;
- aggiunto logout frontend con pulizia token, utente corrente e cache dei preferiti;
- nelle sezioni `Athletes` ed `Events`, se l'utente e loggato, compare ora il filtro locale `Favorites`/`Preferiti`, che mostra direttamente nella sezione corrente solo atleti o eventi preferiti senza rimandare all'area personale;
- il filtro `Favorites`/`Preferiti` e posizionato come ultimo controllo nelle sezioni `Athletes` ed `Events`, separandolo visivamente dai filtri sportivi; in `Events` resta vicino agli altri controlli per evitare un allineamento eccessivamente distante;
- il filtro `Favorites`/`Preferiti` aggiorna direttamente la lista della sezione corrente; in `Events` aggiorna insieme lista e calendario, senza forzare il ritorno all'area personale;
- per maggiore robustezza in anteprima locale, il filtro `Favorites`/`Preferiti` restringe lato frontend i risultati agli ID preferiti gia caricati, evitando di dipendere dal riavvio immediato del backend per il parametro `favorite_only`;
- aggiunto pulsante a stellina sulle card atleta e sulle card evento: stellina vuota per salvare, stellina piena per rimuovere dai preferiti;
- create schede minime reali per atleta ed evento (`#/athletes/:id`, `#/events/:id`) collegate agli endpoint pubblici esistenti, con stellina visibile nella scheda quando l'utente e autenticato;
- mantenuta la semantica corretta del backend: i risultati continuano a salvare solo `athlete_id` ed `event_id`, mentre le preferenze personali restano relazioni utente-entita separate;
- la UI dei preferiti usa lo stesso linguaggio visuale minimal gia adottato per topbar, card e controlli principali.
- aggiunta la possibilita per l'utente loggato di salvare configurazioni personalizzate della sezione `Rankings`: dopo aver selezionato disciplina, categoria, attrezzi, scoring cycle o intervallo temporale, l'utente puo nominare e salvare quella configurazione;
- le configurazioni `Rankings` salvate vengono archiviate nel modello esistente `SavedDashboardView` con `view_type = "ranking"` e contengono solo il JSON dei filtri attivi, senza duplicare risultati o dati sportivi;
- nell'area privata `My LEVERAGE` compare ora una sezione `Saved Rankings`, da cui l'utente puo riaprire una configurazione salvata; il frontend torna automaticamente a `Rankings` e riapplica i filtri memorizzati.
- rifinita la UX del salvataggio Ranking: nella sezione `Rankings` il comando compare solo per utenti loggati e inizialmente viene mostrato solo il pulsante `Save this Ranking`; il riquadro con nome configurazione e riepilogo filtri appare soltanto dopo il click dell'utente.
- aggiunto nella sezione privata `Saved Rankings` un pulsante cestino per ogni configurazione salvata, collegato all'endpoint `DELETE /preferences/dashboard-views/{id}`, cosi l'utente puo rimuovere autonomamente configurazioni non piu utili.
- corretta la resa grafica del pulsante cestino, sostituendo il disegno CSS con una piccola icona SVG proporzionata e stabile.
- uniformata la UI del cestino alla stellina dei preferiti: stesso componente base, stessa dimensione, stesso hover/focus/disabled e stessa micro-interazione al click, cambiando soltanto l'icona interna.
- aggiunto nella sezione `Rankings` il pulsante `Clear filters`/`Pulisci filtri`, che rimuove in un solo click categoria, attrezzi, scoring cycle e intervalli temporali, riportando la classifica al default tecnico MAG.
- riorganizzata la sezione `Rankings` separando visivamente i filtri che modificano la classifica dalle azioni personali: disciplina/categoria, apparatus, cicli e periodo restano in un blocco filtri compatto, mentre `Save this Ranking` e `Clear filters` sono raccolti in una riga azioni distinta.
- reso `Save this Ranking` un comando toggle: il primo click apre il riquadro di salvataggio, il secondo click lo richiude, mantenendo il pulsante sempre visibile e accessibile.
- aggiunti temporaneamente nella pagina `Sign in` i pulsanti di sviluppo `DEMO USER`, `DEMO ADMIN` e `DEMO SUPER ADMIN`, collegati a un endpoint backend abilitato solo in ambiente `development`; servono per testare rapidamente area privata, preferiti, funzioni admin e funzioni super-admin di sicurezza/review durante la costruzione frontend.
- decisione da ricordare: i pulsanti `DEMO USER`, `DEMO ADMIN` e `DEMO SUPER ADMIN`, insieme all'endpoint demo, dovranno essere rimossi prima della pubblicazione dell'MVP online.

Aggiornamento UX search bar del 21 luglio 2026:

- nelle sezioni dedicate `Athletes` ed `Events`, i filtri sono stati riallineati a destra della rispettiva barra di ricerca su desktop, lasciando la ricerca a sinistra e i controlli contestuali a destra;
- nella sezione `Events`, i filtri sportivi/semantici e quelli di stato calendario restano raccolti in una colonna compatta a destra della search bar, cosi la pagina conserva ordine anche con molti controlli attivi;
- su viewport stretti e mobile, la struttura torna automaticamente verticale per evitare compressione o sovrapposizione tra input, pulsante Search e filtri;
- tutte le search bar principali ora includono una piccola crocetta interna al campo di testo per cancellare l'intera query in un click: ricerca globale home, pagina ricerca globale, ricerca Athletes e ricerca Events;
- la crocetta resta nascosta quando il campo e vuoto, compare solo durante la digitazione e scatena lo stesso flusso live della ricerca manuale, cosi i risultati si aggiornano immediatamente nelle sezioni dedicate.

Correzione preferiti del 21 luglio 2026:

- corretto un problema UX per cui, dopo aver cambiato schermata e rientrando in `Athletes` o `Events`, il filtro `Favorites`/`Preferiti` poteva mostrare `No results` anche in presenza di preferiti salvati;
- causa individuata: il frontend scaricava una lista pubblica limitata e poi applicava il filtro preferiti localmente; se il preferito non rientrava nella finestra caricata, il risultato veniva escluso;
- soluzione adottata: quando il filtro `Preferiti` e attivo, la UI passa `favorite_only=true` agli endpoint pubblici autenticati gia esistenti (`/athletes/` e `/events/calendar`) e invia il token JWT;
- regola definitiva: il filtro `Preferiti` non usa piu le liste pubbliche per costruire la vista filtrata. Quando l'utente attiva `Preferiti` in `Athletes` o `Events`, il frontend legge direttamente gli stessi endpoint dell'area personale (`/preferences/athletes/followed/details` e `/preferences/events/saved/details`) e mostra quelle schede nella sezione corrente, facendo sparire temporaneamente tutte le altre. Quando il filtro viene tolto, la sezione torna alla lista pubblica normale.

Aggiornamento UI search/filter del 23 luglio 2026:

- ridotta esclusivamente l'altezza di input e pulsante `Search` nelle barre di ricerca delle sezioni `Athletes` ed `Events`, mantenendo invariati i pulsanti filtro;
- il tasto `Search` delle sezioni dedicate usa ora la stessa altezza dei filter button esistenti, cosi i controlli associati risultano piu coerenti senza modificare la ricerca globale della home.
- mantenuta la dimensione ridotta ma corretto il raggio dei bordi della search bar e del pulsante `Search` delle sezioni dedicate, evitando l'effetto pillola e riportando i controlli allo stile app con radius coerente ai filtri.
- rifinito il filtro `Level` nella sezione `Events`: la selezione resta multipla e il popup non si chiude dopo ogni click sui livelli. L'utente puo selezionare piu livelli consecutivamente e chiudere il menu solo ricliccando il pulsante `Level` o aprendo un altro popup filtro.
- resa piu compatta la preview del filtro `Level`: nel pulsante vengono mostrate sigle (`OG`, `WCh`, `CCh`, `WC`, `WCC`, `INT`, `NAT`) mentre il popup conserva i nomi completi e il tooltip del pulsante mostra la selezione estesa.
- rifinito il filtro `Periodo` nelle sezioni `Events` e `Rankings`: quando e attivo, il pulsante mostra direttamente una preview sintetica del periodo selezionato, per esempio `Periodo: 2021 - 2023` o `Periodo: 01/2021 - 12/2023`; se il testo e troppo lungo, viene troncato nel pulsante e mostrato completo tramite tooltip al passaggio del mouse.
- trasformata la sezione `Events` in una vista unica selezionabile: la lista gare non e piu seguita automaticamente dal calendario, ma puo essere convertita in calendario tramite controllo slider `List/Calendar`, coerente con il selettore `MAG/WAG` della sezione `Rankings`. Gli stessi filtri `discipline`, `category`, `Level`, `Periodo` e `Preferiti` agiscono in tempo reale sia sulla lista sia sulla vista calendario.
- aggiunto il filtro `Level` anche nella sezione `Rankings`, collegato al parametro backend `/analytics/rankings?level=...` e salvato nelle configurazioni ranking dell'utente. La prima riga dei filtri `Rankings` ora raccoglie disciplina, categoria, `Level`, `Periodo`, `Ciclo olimpico` e `Pulisci filtri`, mentre gli attrezzi restano separati nella riga successiva.
- ripulito il riquadro principale della sezione `Events`: rimane il titolo `Competitions`/`Competizioni` con il controllo `List/Calendar`, mentre e stata rimossa la frase descrittiva ridondante sotto al titolo per rendere il pannello piu coerente e minimale rispetto alle altre sezioni.
- aggiunto il comando `Pulisci filtri` anche nella sezione `Athletes`: il pulsante resetta disciplina, categoria e filtro `Preferiti`, mantenendo invece il testo digitato nella search bar, che resta gestito dalla crocetta interna al campo.
- rimossi i popup/dropdown informativi dalla topbar principale: le voci `Home`, `Athletes`, `Events`, `Rankings` e `Analytics` sono ora link diretti senza pannelli hover, rendendo la barra superiore piu pulita e coerente con una UI minimal.
- rese piu compatte le liste `Events` e `Rankings`: le card evento e ranking usano padding, gap, chip e titoli leggermente ridotti, cosi le liste risultano piu consultabili e coerenti con la densita visiva della sezione `Athletes`.
- rimosso il titolo ridondante `Competitions`/`Competizioni` dal riquadro principale della sezione `Events`; il controllo `List/Calendar` viene ora mostrato a sinistra come primo elemento funzionale del pannello.
- rimosso il riquadro/panel esterno che incorniciava lista e calendario nella sezione `Events`; le schede evento sono state rese leggermente piu leggibili e la data non viene piu duplicata nella riga meta e nei chip, restando visibile una sola volta come chip principale.
- rese piu compatte anche le schede atleta e rimossa la dicitura tecnica `Official profile pending` quando non esiste ancora uno status ufficiale da mostrare; le card atleta vuote nella riga meta vengono nascoste per restare coerenti con la pulizia visiva di `Events` e `Rankings`.
- uniformata la tipografia delle card tra home, `Athletes`, `Events` e `Rankings`: titoli, meta text, pill/chip, padding e gap usano una scala comune, riducendo differenze locali e rendendo piu omogenea la lettura delle liste.
- allineata la dimensione del controllo `List/Calendar` nella sezione `Events` ai filter button: altezza, padding, corpo testo e proporzioni interne sono ora coerenti con gli altri pulsanti dell'interfaccia.
- rifinita anche la tipografia interna del controllo `List/Calendar`: il testo eredita la stessa dimensione dei filter button e usa colore, peso, allineamento e spaziatura coerenti con gli altri comandi.
- collegato il filtro `Preferiti` della sezione `Events` alla vista calendario: quando l'utente attiva i preferiti, il calendario si posiziona automaticamente sul mese/anno del primo evento preferito datato mostrato nella lista; nella toolbar del calendario compare inoltre una piccola navigazione precedente/successivo per saltare tra gli eventi preferiti, mantenendo gli stessi filtri di ricerca attivi.
- resi sticky i controlli principali delle sezioni consultabili: durante lo scroll, la topbar resta visibile e, subito sotto, restano agganciati search bar e filtri di `Athletes`/`Events` oppure il blocco filtri di `Rankings`; il frontend misura dinamicamente l'altezza reale della topbar, cosi il punto di aggancio resta corretto anche su viewport stretti o con topbar su due righe.
- aggiunti nella sezione `Rankings` i filtri di metrica `Final Score`, `D Score`, `E Score`, `Penalty` e `Bonus`, collegati al parametro backend `sort_by`; le card ranking mostrano come pill principale il valore effettivamente usato per ordinare la classifica e le configurazioni Ranking salvate memorizzano anche questa scelta.
- corretto il comportamento dei filtri sticky: quando l'utente scorre una lista e clicca un filtro, il frontend aggiorna i risultati preservando la posizione di scroll corrente, evitando il ritorno automatico all'inizio pagina in `Athletes`, `Events` e `Rankings`.
- trasformato il filtro metrica dei `Rankings` in un unico segmented slider largo, coerente con il controllo `MAG/WAG`; il pulsante `E Score` ora usa la metrica backend `execution_estimate` e, quando attivo, mostra una nota informativa sopra la lista per chiarire che l'esecuzione e stimata da Final Score e D Score e puo incorporare Penalty/Bonus non disponibili.
- rivista la scelta UX sui filtri sticky: su indicazione di test, il click su un filtro torna nuovamente all'inizio della lista aggiornata, per dare all'utente un riferimento chiaro dopo il cambio dei criteri; lo sfondo del menu filtri sticky e stato reso coerente con la superficie grigio-vetro della UI, evitando l'effetto fascia bianca separata.
- rimossa successivamente la resa opaca/vetro da topbar e menu filtri sticky: restano fissi durante lo scroll, ma usano superfici piatte e pulite senza `backdrop-filter`, blur o gradienti semi-trasparenti.
- rifinito lo sfondo dei menu filtri sticky: non usano piu bianco pieno, ma il grigio pagina `#f5f5f7`, mantenendo una separazione sottile tramite bordo inferiore.
- allineata la dimensione del testo nel filtro metrica dei `Rankings` (`Final Score`, `D Score`, `E Score`, `Penalty`, `Bonus`) agli altri controlli filtro, evitando che lo slider score sembrasse un componente separato.
- resa esplicita la coerenza tra sfondo pagina e sticky menu: introdotta una variabile unica `--page-bg`, usata sia dal body sia dai menu filtri sticky, evitando discrepanze visive tra fascia filtri e superficie della pagina.
- rimosso il grassetto dai pulsanti filtro slider (`MAG/WAG`, `List/Calendar`, metriche score), mantenendo selezione e contrasto tramite colore e thumb invece che tramite peso tipografico.
- migliorata la leggibilita delle card `Rankings`: quando l'utente ordina per `D Score`, `E Score`, `Penalty` o `Bonus`, la metrica selezionata compare solo nella pill principale e viene rimossa dalla composizione D/E/P/B sottostante, evitando duplicazioni nella stessa scheda.
- corretto lo stato vuoto dei `Rankings` quando vengono selezionate le metriche `Penalty` o `Bonus`: se non esistono valori ordinabili per i filtri attivi, la UI non mostra piu un generico `No results`, ma segnala che quei dati non sono disponibili per la selezione corrente e suggerisce di usare `Final Score`, `D Score`, `E Score` o modificare i filtri.
- reso piu compatto lo slider delle metriche score nei `Rankings`: il controllo non occupa piu quasi tutta la larghezza della sezione, ma mantiene una dimensione massima coerente con gli altri filtri e un'altezza allineata ai pulsanti della UI.
- aggiornata la lettura delle card `Rankings`: quando il ranking viene ordinato per `D Score`, `E Score`, `Penalty` o `Bonus`, la pill principale mostra la metrica scelta per l'ordinamento e una seconda pill mostra sempre il `Final Score` associato al result, cosi l'utente mantiene il riferimento complessivo della performance.
- ripristinato il comportamento UX iniziale dei filtri: dopo l'attivazione o modifica di un filtro, la pagina torna in cima (`top: 0`) invece di posizionarsi soltanto all'inizio della lista risultati, cosi il cambio filtro viene percepito come refresh completo della vista.
- eliminata la trasparenza residua dalle sticky bar dei filtri: i contenitori sticky di `Athletes`, `Events` e `Rankings` usano ora uno sfondo pieno coerente con il grigio pagina, esteso anche fuori dalla colonna contenuto, mentre search form, filter button e segmented control hanno sfondo bianco pieno.
- rifiniti titoli e didascalie delle sezioni principali `Athletes`, `Events`, `Rankings` e `Analytics`: i testi ora spiegano in modo piu operativo cosa l'utente puo fare in ciascuna area e la gerarchia tipografica dei page heading e stata ridotta per restare coerente con una UI minimal, distinguendosi dalla hero della home.
- rifinita la composizione delle card `Rankings`: quando l'utente ordina per `D Score`, `E Score`, `Penalty` o `Bonus`, la metrica selezionata resta in evidenza nella pill superiore, mentre il `Final Score` viene mostrato nella griglia inferiore allineato agli altri componenti disponibili del punteggio, con etichetta esplicita `Final Score`.
- corretto lo stato vuoto dei `Rankings` per `VT AVG` ordinato tramite `D Score` o `E Score`: se il backend non restituisce risultati ordinabili, la UI non mostra piu `No results`, ma segnala che i dati componenti di `VT AVG` non sono disponibili per la metrica selezionata, suggerendo `Final Score` o un cambio attrezzo.
- introdotto il `D Score total` derivato per i result `AA`: il valore non viene salvato nel database come campo ufficiale del result AA, ma viene calcolato nelle risposte ranking sommando i `D_score` dei singoli attrezzi che compongono quell'AA quando tutti gli attrezzi previsti sono disponibili. Il backend puo usare questo dato anche per ordinare ranking filtrati su `apparatus=AA&sort_by=D_score`, mentre la UI lo mostra nelle card AA accanto al `Final Score`.
- corretto il layering dei popup filtro (`Level`, `Periodo`, `Ciclo olimpico`) nelle barre sticky: rimosso il clipping verticale che faceva finire i pannelli sotto il contenuto della pagina e riallineato lo z-index dei dropdown, mantenendo lo sfondo sticky pieno e coerente con il grigio pagina.
- rifinita la chiusura dei popup filtro: i pannelli aperti da `Level`, `Periodo`, `Ciclo olimpico` e menu analoghi si chiudono ora anche cliccando fuori dal popup in un punto qualsiasi della pagina, senza cancellare i filtri gia selezionati.
- rifinita la visualizzazione dei result `AA` nelle card `Rankings`: quando l'ordinamento e per `Final Score`, il `D Score AA` derivato viene mostrato subito accanto al final score; quando l'ordinamento e per `D Score`, il `Final Score` associato viene mostrato subito accanto al D-score. Questo affiancamento resta limitato ai soli casi `AA`, evitando duplicazioni nella composizione per attrezzo sottostante.
- corretto un problema visivo causato dallo sfondo full-width delle barre filtri sticky: il precedente `box-shadow` esteso, dopo la rimozione del clipping necessaria ai popup, copriva visivamente liste e card sotto i filtri. Lo sfondo pieno delle sticky bar e ora gestito con pseudo-elementi posti dietro ai controlli, mentre i contenuti delle sezioni restano visibili e i popup possono uscire correttamente.
- ottimizzato il ranking `AA` ordinato per `D Score`: il `D Score AA` resta un dato derivato, ma non viene piu calcolato caricando tutti gli AA in Python. Il backend ora usa una subquery SQL aggregata che somma i `D_score` dei componenti AA e ordina gia nel database, restituendo solo i record richiesti dalla UI. Aggiunta anche la migration Alembic `0032_add_result_apparatus_metric_index` con indice `ix_results_apparatus_metric_scope`, applicata al DB locale; nelle prove live, `MAG/WAG + AA + D Score + limit=60` risponde in circa 0.9-1.25 secondi.
- rifinito il pannello `Salva questo Ranking`: quando l'utente apre il form, il pulsante di conferma non e piu separato ma integrato direttamente nella barra di inserimento del nome, come controllo interno `Salva`, mantenendo il messaggio di conferma sotto la barra.
- aumentata leggermente la larghezza del pannello `Salva questo Ranking`, rendendo piu comoda la digitazione del nome della configurazione senza alterare il comportamento responsivo su viewport stretti.
- risolto il rallentamento nel caricamento iniziale della sezione `Rankings`: il problema non era la query dei record finali, ma due query `DISTINCT` usate per ricostruire anni e discipline del contesto ranking, che sul dataset reale richiedevano circa 10-11 secondi. Quando disciplina e ciclo olimpico sono gia noti dai filtri/applicazione dello scope, il backend usa ora direttamente quel contesto invece di scansionare tutto il dataset; il caricamento live di `MAG + Final Score + limit=60` e sceso a circa 0.21 secondi, `WAG + Final Score + limit=60` a circa 0.22 secondi e `MAG + AA + D Score + limit=60` a circa 0.39 secondi.
- riallineata la riga grigia di separazione nella sezione `Athletes`: la sticky bar dei filtri atleta usa ora uno spacing inferiore leggermente ridotto, cosi il divider risulta piu coerente con la posizione percepita nella sezione `Events`.
- riordinati i filtri della sezione `Rankings`: il filtro metrica (`Final Score`, `D Score`, `E Score`, `Penalty`, `Bonus`) viene ora mostrato sotto i filtri apparatus, cosi l'utente sceglie prima il dominio tecnico del ranking e poi la metrica con cui ordinarlo.
- spostato il controllo `Lista/Calendario` della sezione `Events` dentro la barra sticky dei filtri, eliminando l'header separato sotto i filtri. La scelta rende il cambio vista parte dei controlli principali della sezione, mantenendo invariata la logica di aggiornamento lista/calendario.
- aggiunto nella sezione `Athletes` un controllo slider `Nome/Nazione`, coerente con il controllo `Lista/Calendario` della sezione `Events`: l'ordinamento per nome mostra le schede in ordine alfabetico per cognome/nome, mentre l'ordinamento per nazione usa `country` come primo criterio e poi cognome/nome. Il backend espone il parametro `sort_by=name|country`, cosi l'ordinamento viene applicato all'intero dataset filtrato prima della paginazione e non solo alle schede gia caricate in UI; lo stesso criterio viene applicato anche alla lista `Preferiti`, che usa un endpoint personale dedicato.
- rifinita la posizione del controllo `Lista/Calendario` nella sezione `Events`: il toggle resta dentro la sticky bar dei filtri, ma viene mostrato in una seconda riga sotto i filtri semantici principali, distinguendo meglio la scelta di visualizzazione dai criteri di filtraggio.
- rifinita allo stesso modo la posizione del controllo `Nome/Nazione` nella sezione `Athletes`: il toggle resta nella sticky bar, ma viene spostato in una seconda riga sotto i filtri principali, separando l'ordinamento della lista dai filtri semantici.
- corretto l'ordinamento iniziale della sezione `Athletes`: gli atleti con `last_name` vuoto, frequenti nei dati importati per nomi singoli, e quelli con `last_name` tecnico tra parentesi non vengono piu mostrati prima di tutti gli altri solo per effetto dell'ordinamento SQL sulle stringhe non alfabetiche. L'ordinamento `Nome` ora mostra prima gli atleti con cognome reale valorizzato, poi quelli con cognome tecnico tra parentesi e infine quelli con cognome mancante; lo stesso criterio e applicato anche dentro l'ordinamento per `Nazione` e alla lista dei preferiti.
- allineata la linea grigia di separazione tra menu filtri e lista record nelle sezioni `Athletes`, `Events` e `Rankings`: senza modificare dimensione di pulsanti, font o slider, le search bar dedicate di `Athletes` ed `Events` sono state portate a un'altezza coerente con l'altezza complessiva del menu `Rankings`, rendendo uniforme la quota del divider nelle tre sezioni.
- corretto il feedback visivo del controllo `Nome/Nazione` nella sezione `Athletes`: il cambio ordinamento aggiorna ora anche `aria-checked` e la posizione del thumb dello slider, cosi l'animazione segue immediatamente la scelta dell'utente senza dover ridisegnare l'intera pagina.
- aumentato il numero di schede caricate nella sezione `Athletes`: la vista pubblica passa da 40 a 300 record per richiesta, rendendo la consultazione iniziale molto piu ricca pur mantenendo un limite controllato in attesa di una futura paginazione/load-more.
- rifinita ulteriormente la quota del divider sticky tra menu filtri e liste record: l'altezza delle search bar dedicate `Athletes`/`Events` e stata ridotta di 2px, lasciando invariati font, dimensioni dei pulsanti e controlli slider, per avvicinare la linea grigia alla stessa altezza percepita nella sezione `Rankings`.
- uniformata la convenzione di visualizzazione delle schede atleta nella sezione `Athletes` e nei `Preferiti`: il titolo della card mostra ora `Cognome Nome`, coerentemente con l'ordinamento alfabetico per `last_name` e poi `first_name`; per gli atleti con cognome mancante viene mostrato il solo nome disponibile.
- abbassata leggermente la linea grigia di separazione nella sezione `Rankings`: aumentato di pochi pixel il padding inferiore della sticky bar ranking, senza modificare dimensione, font o spaziatura interna dei pulsanti filtro.
- uniformata l'animazione dei controlli segmented slider: oltre a `Nome/Nazione`, anche `Lista/Calendario`, `MAG/WAG` nei `Rankings` e il selettore metrica (`Final Score`, `D Score`, `E Score`, `Penalty`, `Bonus`) aggiornano subito thumb e `aria-checked` prima del reload dei dati, rendendo coerente il feedback visivo tra sezioni.
- abbassato leggermente l'intero gruppo filtri della sezione `Rankings`: aumentato di pochi pixel il padding superiore della sticky bar ranking per allineare meglio la quota dello slider metrica `Scores` con il toggle `Lista/Calendario` della sezione `Events`.
- uniformati UI e design dei controlli segmented slider `Nome/Nazione`, `Lista/Calendario` e `Scores`: stessa altezza complessiva, stesso padding, stesso radius, stesso peso del carattere, stessa altezza delle opzioni e stessa geometria del thumb; resta diversa solo la larghezza complessiva dove necessaria, perche `Scores` contiene cinque opzioni invece di due.
- abbassata di un ultimo micro-step la sticky bar della sezione `Rankings`: il padding superiore passa da 14px a 16px, cosi la riga apparatus (`AA`, `FX`, ecc.) si allinea meglio alla riga filtri principale della sezione `Events` (`MAG`, `WAG`, ecc.) senza modificare dimensioni dei pulsanti o caratteri.
- riallineata in modo piu sistematico la geometria sticky di `Rankings`: la sticky bar usa piu spazio sopra i filtri e meno spazio sotto, cosi la riga apparatus (`AA`, `FX`, ecc.) scende alla stessa quota visiva della riga filtri principale di `Events`, mentre la linea grigia di separazione resta coerente con quella delle altre sezioni.
- rifinito l'allineamento della terza riga `Rankings`: mantenuta ferma la riga apparatus gia corretta, lo slider `Scores` e stato portato alla quota del controllo `List/Calendar` della sezione `Events` e il padding inferiore della sticky bar e stato bilanciato per ridurre lo sfalsamento della linea grigia.
- compattata la hero della home senza toccare gli allineamenti delle sezioni interne: la search globale e leggermente piu bassa, lo spazio verticale sopra/sotto la hero e stato ridotto e le quattro card `Start with the data` sono state avvicinate e rese appena piu compatte, cosi entrano prima nel primo viewport.
- ripulita la sezione iniziale dati della home: rimossi titolo/sottotitolo `Start with the data`, tolto il link testuale `Open/Apri` dalle quattro card principali e introdotta una variante compatta delle feature card, cosi i percorsi `Athletes`, `Events`, `Rankings` e `Analytics` risultano visibili prima e con una UI piu minimale.
- riequilibrate le quattro card iniziali della home: leggermente aumentate altezza, padding e dimensione dei testi interni, mantenendo la pulizia della sezione ma occupando abbastanza spazio verticale da evitare che calendario e ranking preview si intravedano gia all'apertura della homepage.
- aggiornata l'etichetta della card `Rankings` nella home: in italiano passa da `Vai ai Rankings` a `Crea Rankings`, con traduzioni coerenti nelle altre lingue e mantenimento del termine `Rankings` non tradotto.
- riordinata la posizione delle azioni filtro: `Pulisci filtri` viene spinto a destra nelle sezioni `Athletes` ed `Events`; nella sezione `Rankings` e stata introdotta una colonna azioni a destra della sticky bar, con `Salva questo Ranking` sopra e `Pulisci filtri` sotto, mantenendo a sinistra le righe filtri gia allineate.
- rifinita ulteriormente l'area azioni dei filtri: `Pulisci filtri` viene spostato sulla riga dello slider nelle sezioni `Athletes` ed `Events`, mentre in `Rankings` viene allineato alla riga dello slider `Scores`; il bottone assume una variante rosso-leggera coerente con le azioni distruttive come il cestino. Il comando `Salva questo Ranking` resta visibile nella colonna azioni: da loggato apre il salvataggio, da non loggato rimanda al login.
- reso opaco il popup `Salva questo Ranking`: il pannello non eredita piu la superficie traslucida delle card generiche, ma usa sfondo bianco pieno, bordo leggero e ombra dedicata per garantire leggibilita.
- riportato `Pulisci filtri` a uno stato normale neutro, uguale agli altri pulsanti; il colore rosso viene usato solo in hover/focus, analogamente al cestino dei Ranking salvati, per segnalare l'azione di rimozione senza appesantire la UI a riposo.
- reso neutro anche il pulsante interno `Salva` del popup `Salva questo Ranking`: a riposo resta bianco come gli altri controlli, mentre in hover/focus diventa blu Maserati.
- aggiornata la semantica visiva dei preferiti: la stellina diventa gialla in hover/focus e resta gialla quando atleta o evento sono salvati come preferiti; il cestino dei Ranking salvati resta invece separato e mantiene hover rosso.
- rifinito il tasto preferiti mantenendo lo stile precedente del bottone pieno: il giallo sostituisce il blu Maserati negli stati hover/attivo, mentre la stellina interna resta bianca come nella versione originale.
- rifinito l'allineamento interno delle quattro card iniziali della home: titolo e descrizione sono ora trattati come un blocco verticale centrato e spaziato in modo uniforme dentro ciascuna scheda, mantenendo la UI compatta.
- spostato il filtro `Preferiti` nelle sezioni `Athletes` ed `Events`: non compare piu tra i filtri principali, ma nella seconda riga accanto a `Pulisci filtri`, dentro un gruppo azioni allineato a destra.
- allineata la semantica cromatica del filtro `Preferiti`: a riposo resta neutro come gli altri filtri, mentre in hover/focus e quando attivo diventa giallo come la stellina dei preferiti.
- aggiunto nella sezione `Rankings` il pulsante `Salvati`, visibile solo da utente loggato, accanto a `Pulisci filtri`: il link rimanda direttamente alla sezione `Rankings salvati` dell'area privata `My LEVERAGE`.
- introdotta una codifica cromatica leggera per le chip di disciplina in tutta la UI: `MAG` usa una tinta azzurra, `WAG` una tinta rosa, mentre `MAG and WAG` usa una sfumatura da azzurro a rosa. La logica e centralizzata nel frontend e viene applicata automaticamente a tutte le pill/caselline con quelle diciture, incluse schede atleta, eventi, risultati, dettagli e rankings.
- resa compatta la larghezza delle chip `MAG` e `WAG` nelle schede atleta: i badge non possono crescere oltre il contenuto testuale, mantenendo invariati altezza, colori e radius, cosi risultano coerenti con gli altri badge delle card.
- rifinito il comportamento del popup `Periodo`: quando un campo data e vuoto, la rotella giorno/mese/anno si apre su `01/01` dell'anno corrente invece che sulla data corrente. Il default viene visualizzato nella casella come placeholder leggero, non come valore nero gia selezionato, e la rotella scorre automaticamente sulla selezione attiva; il filtro resta inattivo finche l'utente non seleziona o digita una data.
- aggiunto nel popup `Periodo` il comando rapido `Oggi`, visualizzato nella colonna dell'anno sotto l'ultimo anno disponibile: il pulsante imposta il campo `Da data` o `A data` selezionato alla data corrente, mantenendo lo stesso comportamento del resto della rotella.
- aggiunta una protezione di coerenza al popup `Periodo`: il campo `A data` non puo essere impostato prima di `Da data`, ne tramite digitazione manuale ne tramite rotella o pulsante `Oggi`. Le opzioni della rotella che produrrebbero un intervallo non valido vengono disabilitate; se l'utente sposta `Da data` oltre un `A data` gia selezionato, `A data` viene svuotato per evitare uno stato incoerente.
- allineata la visibilita del comando `Salva questo Ranking` alla logica delle funzioni personali: il pulsante viene renderizzato solo quando l'utente e loggato, esattamente come `Preferiti` e `Salvati`. Da visitatore anonimo la barra filtri resta quindi pulita e non mostra call-to-action legate all'area privata.
- riallineata la posizione del comando `Pulisci filtri` nella sezione `Rankings`: anche quando il pulsante `Salva questo Ranking` non viene mostrato ai visitatori anonimi, `Pulisci filtri` resta ancorato alla stessa quota bassa della colonna azioni, coerente con le altre sezioni.
- uniformato il popup `Salva questo Ranking` al comportamento degli altri popup filtro: il pannello si chiude quando l'utente clicca fuori, quando apre un altro popup o quando preme `Escape`, senza disattivare i filtri del ranking.
- avviata la revisione semantica del campo `Event.level`: `Olympic Hopes Cup` e stato confermato come `International Event`, non `Olympic Games`. Il record 2026 importato dal Calendar e stato corretto nel DB locale e la regola di inferenza Calendar e stata ristretta: solo eventi contenenti `Olympic Games` o denominati `Olympics` vengono marcati come `Olympic Games`, evitando falsi positivi su eventi con la sola parola `Olympic`.
- estesa la revisione di `Event.level` con una regola di precedenza nazionale: tutti gli eventi contenenti `Trial`/`Trials`, `Bundesliga`, `Serie A` o `Top 12` devono essere classificati come `National Event`, anche se nel nome compaiono parole come `Worlds`, `World Cup`, `Olympic` o `Euros`. La regola e stata centralizzata in `app/event_levels.py` e viene usata sia dall'import Gymternet legacy sia dall'import/materializzazione Calendar.
- riclassificati nel DB locale 296 Event gia esistenti verso `National Event`: 250 provenivano da `International Event`, 45 da `World Championships` e 1 da `World Cup`. Le motivazioni rilevate sono: 115 `Trial/Trials`, 78 `Bundesliga`, 68 `Top 12`, 35 `Serie A`. Backup locale: `backups/leverage_before_event_level_reclassification_20260803.db`; report CSV: `docs/import_reports/event_level_reclassification_national_rules_20260803.csv`.
- aggiunti override espliciti approvati nella revisione `Event.level`: `Worlds Preparation Event` viene classificato come `International Event`, `South African Championships` come `National Event`, `Northern European Championships` come `International Event`. Sono stati corretti 13 eventi gia presenti nel DB locale e la regola e stata centralizzata per import Gymternet e Calendar. Backup locale: `backups/leverage_before_event_level_specific_overrides_20260803.db`; report CSV: `docs/import_reports/event_level_specific_overrides_20260803.csv`.
- lasciato in revisione `European Championships MT`: l'evento 2025 ha 56 risultati associati, `MAG and WAG`, categoria `senior`, format `individual`, round `final`, con risultati su `MAG FX/HB/PB` e `WAG BB/FX/VT`. In attesa di decisione admin resta classificato come `Continental Championships`.
- chiarita la semantica del suffisso Gymternet `MT`: non rappresenta un evento autonomo, ma il format `Mixed Team`. Il backend ora include il nuovo `Result.format = mixed team`; il parser Gymternet rimuove `MT` dal nome gara e salva quei result come `round=final`, `format=mixed team`. L'evento `European Championships MT` 2025 e stato aggregato dentro `European Championships` 2025: 56 result spostati sull'evento base, vecchio evento soft-deleted, nessun duplicato Result generato. Backup locale: `backups/leverage_before_mixed_team_format_20260803.db`; migration Alembic: `0033_add_mixed_team_result_format`; report CSV: `docs/import_reports/mixed_team_event_merge_20260803.csv`.
- risolto anche `Chinese Championships MT` 2026 con lo stesso trattamento di `European Championships MT`: 72 result spostati nell'evento base `Chinese Championships` 2026, salvati come `round=final`, `format=mixed team`, e vecchio evento tecnico soft-deleted. La calendar entry `Chinese Championships` e stata collegata all'evento base, mentre la calendar entry `Chinese Junior Championships` 2026 e stata lasciata senza `event_id` e marcata `left_unmatched_after_mt_merge`, perche rappresenta una gara calendario distinta senza risultati importati al momento. Report aggiornato: `docs/import_reports/mixed_team_event_merge_20260803.csv`; dettaglio result: `docs/import_reports/chinese_championships_2026_mixed_team_results_20260803.csv`.
- aggiunta una regola di controllo per i futuri import `MT`: il suffisso `MT` indica `Mixed Team` quando il profilo attrezzi e coerente con MAG `FX/PB/HB` e WAG `BB/UB/FX`. Il parser Gymternet ora genera un warning di review admin se un import `MT` contiene attrezzi diversi da questo profilo, senza bloccare automaticamente l'import.
- completata una revisione aggiuntiva dei record marcati `International Event`: l'audit iniziale contava 1.315 eventi attivi in quel livello e ha individuato un cluster molto ampio di eventi domestici/nazionali rimasti classificati come internazionali per prudenza dell'import Gymternet legacy. La regola condivisa `app/event_levels.py` e stata estesa per riconoscere campionati domestici con prefisso nazionale, `NCAA`, `Spanish League`, `National Qualifier`, `National Team`, `National Camp/Test/Review/Selection`, `National Games` e `National Sports Festival`. La migration Alembic `0034_reclassify_domestic_event_levels` ha riclassificato 659 eventi da `International Event` a `National Event`; report: `docs/import_reports/event_level_domestic_reclassification_candidates_20260804.csv`.
- completato il cleanup residuo di `Event.level`: corretti i refusi `1st/2nd Bundlesiga League 2` in `1st/2nd Bundesliga League 2`, riclassificati come `National Event`; corretto `Japanese National Spots Festival` in `Japanese National Sports Festival`, riclassificato come `National Event`; spostati `Asian Junior Championships`, `Junior Pan Am Championships` e `Oceania Championships` da `International Event` a `Continental Championships`. La migration Alembic associata e `0035_cleanup_residual_event_levels`; report: `docs/import_reports/event_level_residual_cleanup_20260804.csv`.
- dopo la revisione `Event.level`, la distribuzione attiva del DB locale e: `National Event` 976, `International Event` 647, `Continental Championships` 37, `World Challenge Cup` 44, `World Cup` 40, `World Championships` 10, `Olympic Games` 5. Il report clusterizzato degli International residui e `docs/import_reports/international_events_cluster_review_20260804.csv`. I quattro nomi domestic-looking rimasti (`COMEGYM Championships`, `Klaverblad Championships`, `Liepaja Championships`, `Platinum League Online`) sono stati confermati da review admin come `International Event`, non come `National Event`; la decisione e tracciata in `docs/import_reports/event_level_residual_domestic_review_20260804.csv` e `docs/import_reports/event_level_international_overrides_20260804.csv`.
- sviluppata la prima versione completa della scheda atleta pubblica in frontend: cliccando una card atleta, l'utente apre una pagina dedicata con hero compatta, immagine o iniziali, discipline/country/ID, campi ufficiali dell'entita `Athlete`, collegamento World Gymnastics quando approvato e storico dei cambi di nazionalita. La stellina preferiti resta visibile solo per utenti loggati, mentre i visitatori anonimi consultano gli stessi dati pubblici senza funzioni personali.
- aggiunta nella stessa pagina la variante admin-only: se l'utente loggato ha ruolo `admin` o `super_admin`, la scheda atleta mostra un pannello di modifica dei campi principali (`first_name`, `last_name`, `birth_year`, `country`, `discipline`, `image_url`, eventuale `country_change_year`), la review dei suggerimenti pendenti con possibilita di accettare, modificare o rifiutare il valore proposto, e un assistente World Gymnastics leggero che cerca candidati o accetta manualmente FIG ID/URL per generare suggerimenti ufficiali. La logica resta coerente con il principio gia fissato: il motore World Gymnastics propone, ma la pubblicazione dei dati passa sempre da conferma admin tramite `DataSuggestion`.
- predisposta una protezione dati super-admin per le modifiche effettuate dagli admin ordinari: `AuditLog` ora include uno stato di revisione (`pending`, `approved`, `reverted`), il super-admin revisore, data revisione e nota. Le operazioni compiute direttamente da un `super_admin` vengono marcate automaticamente come approvate, mentre le modifiche degli admin ordinari restano in coda `pending`.
- aggiunti endpoint super-admin per confermare o annullare una modifica registrata negli audit log: `POST /admin/audit-logs/{audit_log_id}/approve` approva la modifica; `POST /admin/audit-logs/{audit_log_id}/revert` ripristina lo snapshot precedente per `Athlete`, `Event` o `Result` e genera un nuovo audit log `revert_update`. La lista audit e filtrabile anche per `review_status`, cosi in futuro la UI potra mostrare una sezione di sicurezza dati dedicata.
- rifinita la scheda atleta frontend: il nome visualizzato nella pagina dettaglio segue ora la convenzione `Cognome Nome`, coerente con le card atleta e con l'ordinamento alfabetico; e stato aggiunto il comando app-style `Torna agli Atleti` in alto a sinistra della pagina dettaglio; nella traduzione italiana della scheda sono stati corretti gli accenti principali (`Identità`, `nazionalità`, `già`, `può`, `qualità`, `età`).
- correzione dati critica su `Illia Kovtun`: individuate tre schede attive riferite allo stesso atleta (`#1212 Illia Kovtun UKR`, `#1215 Ilya Kovtun UKR`, `#26543 Illia Kovtun CRO`). Dopo backup locale `backups/leverage_before_kovtun_duplicate_merge_20260806.db`, le schede duplicate `#1215` e `#26543` sono state fuse nella scheda canonica `#1212`, spostando 45 result e portando il totale della scheda a 740 result attivi. La scheda canonica e ora `Illia Kovtun`, country attuale `CRO`, con storico `UKR -> CRO` dal 2026. I `represented_country` dei singoli result non sono stati corretti automaticamente, per preservare il dato sorgente fino a eventuale country-correction esplicita.
- aggiunta una normalizzazione permanente nel parser Gymternet: la variante `Ilya Kovtun` viene ora convertita in `Illia Kovtun` prima del match atleta, per evitare che futuri import rigenerino lo stesso duplicato. E stato creato anche il report `docs/import_reports/athlete_duplicate_audit_20260806.csv`, che elenca i candidati duplicati residui da review admin, distinguendo duplicati esatti normalizzati e varianti nome/cognome molto simili.
- uniformata a livello globale la convenzione di visualizzazione dei nomi atleta: in tutta la UI pubblica e admin, nelle risposte `athlete_name` usate da ranking, analytics, ricerca globale, notifiche, statistiche sito e pannelli di revisione, Leverage mostra ora sempre `Cognome Nome`. I campi tecnici del database restano separati come `first_name` e `last_name`, mentre la ricerca continua ad accettare sia digitazioni `Nome Cognome` sia `Cognome Nome` per non peggiorare l'esperienza utente/admin.
- ripulite le pagine dettaglio `Athlete` ed `Event`: quando l'utente apre una scheda specifica non viene piu ripetuto il titolo/sottotitolo generale della sezione (`Athletes`/`Events`). La pagina dettaglio parte direttamente dal contenuto dell'entita, mantenendo il heading generale solo nelle viste lista.
- aggiunto nella pagina dei risultati della ricerca globale (`/search`) un pulsante app-style `Torna alla Home` in alto a sinistra, coerente con il comando `Torna agli Atleti` della scheda atleta. La scelta rende piu chiaro il percorso di ritorno per gli utenti che arrivano alla pagina partendo dalla barra di ricerca della homepage.
- aggiunto nella pagina dettaglio `Event` il pulsante app-style `Torna agli Eventi` in alto a sinistra, usando lo stesso pattern UI gia applicato alla scheda atleta e alla pagina dei risultati della ricerca globale.
- ripristinato nella pagina dei risultati della ricerca globale un heading piu preciso: il titolo e ora `Ricerca globale` e il sottotitolo chiarisce che la ricerca consente di trovare atleti, eventi e risultati in un database di ginnastica strutturato per analisi, confronto e contesto. Il pulsante `Torna alla Home` resta sopra il blocco, come via di ritorno rapida alla homepage.
- rifinito il comportamento dei filtri nelle sezioni `Athletes`, `Events` e `Rankings`: quando l'utente si trova in basso nella lista e attiva un nuovo filtro, la UI non ricostruisce l'intera pagina. Prima riavvolge con scroll morbido fino all'inizio della sezione, rendendo nuovamente visibili titolo e sottotitolo; solo dopo aggiorna localmente la lista dei record con il nuovo filtro applicato. In `Rankings`, il cambio `MAG/WAG` aggiorna localmente anche la riga degli attrezzi disponibili, mantenendo coerenti i filtri senza perdere lo stato della sezione.
- micro-taratura successiva dello stesso comportamento: il caricamento dei nuovi record parte durante l'ultimo tratto del riavvolgimento, quando la pagina e gia vicina all'inizio della sezione. In questo modo l'utente mantiene la percezione del ritorno ordinato al top, ma trova piu rapidamente la lista aggiornata al filtro scelto.
- rifinita la leggibilita del calendario mensile nella home e nella sezione `Events`: ogni settimana viene ora trattata come una banda visiva autonoma, con i giorni nella parte superiore e le barre evento nella parte inferiore dello stesso contenitore. Sono state aggiunte guide verticali leggere nell'area eventi, cosi l'utente capisce meglio a quali giorni appartiene ogni gara e non confonde le barre con la settimana successiva.
- micro-correzione di allineamento del calendario: le bande settimanali non sono piu card separate con bordi propri, ma sezioni dentro un unico frame mensile. Questo mantiene colonne e riquadri perfettamente allineati, conservando separatori orizzontali chiari tra una settimana e l'altra.
- corretta anche la griglia interna dell'area eventi del calendario: e stato rimosso il padding orizzontale che faceva partire le linee/barre evento qualche pixel piu a destra rispetto ai riquadri dei giorni. Le colonne eventi e le colonne giorni condividono ora lo stesso punto di partenza e la stessa larghezza.
- estesa la timeline delle analytics atleta: nella vista `Periodo`, il controllo temporale non ha piu un solo cursore finale, ma due cursori `Da/A` che permettono di selezionare un intervallo storico preciso. Radar/rombo, trend, medie annuali e statistiche riepilogative vengono ricalcolati live sui result compresi tra inizio e fine periodo; nella vista `Snapshot` resta invece attivo il solo cursore finale come istante di riferimento.
- estese le analytics della scheda atleta con un filtro tecnico per apparatus, separato dalla metrica numerica. Oltre a `Final Score`, `D Score`, `E Score`, `Penalty` e `Bonus`, l'utente puo ora isolare un singolo apparatus (`FX`, `PH`, `SR`, `VT`, `PB`, `HB` per MAG; `VT`, `UB`, `BB`, `FX` per WAG), oltre a `AA` e `VT AVG`. La vista completa resta lo stato iniziale ma non viene piu mostrata come pulsante `Tutto`, perche non rappresenta una metrica/attrezzo reale; ricliccando il filtro apparatus gia attivo si torna alla vista completa. Quando viene selezionato un singolo attrezzo, il diagramma esagonale/romboidale mantiene il profilo complessivo ma evidenzia solo il vertice pertinente e rende piu chiari gli altri vertici; il trend viene invece filtrato sul solo apparatus scelto. Per `AA`, l'intera area resta evidenziata e il trend principale AA viene accompagnato da curve secondarie piu leggere degli attrezzi che compongono lo stesso contesto di risultato; per `VT AVG`, la curva principale e il vault average e le curve secondarie mostrano `VT 1` e `VT 2` quando disponibili. Il backend espone ora anche `vt_attempt` nei punti analytics, cosi il frontend puo distinguere correttamente le due prove di volteggio.
- raffinato il filtro apparatus delle analytics atleta da selezione singola a multi-selezione. L'utente puo ora attivare insieme piu attrezzi e vedere l'aggiornamento live di riepilogo, radar/rombo, trend e medie annuali senza nuove chiamate API. Se non ci sono attrezzi selezionati, resta attiva la vista completa; se vengono scelti piu apparatus, il diagramma evidenzia tutti i vertici pertinenti e il trend principale aggrega i punti selezionati. Quando la multi-selezione coinvolge piu attrezzi semplici, il trend mostra anche curve secondarie leggere per i singoli attrezzi selezionati; le regole speciali di `AA` e `VT AVG` restano attive.
- allineato l'ordine dei pulsanti apparatus nelle analytics atleta alla sezione `Rankings`: `AA` viene mostrato come primo filtro, seguito dagli attrezzi della disciplina e da `VT AVG` in coda. La UI usa ora la stessa sorgente dati dei filtri ranking (`RANKING_APPARATUS_BY_DISCIPLINE`), mentre il diagramma mantiene separato l'ordine geometrico dei vertici MAG/WAG.
- corretta la semantica del pulsante temporale `Istante` nelle analytics atleta: non rappresenta piu una vista cumulativa fino alla data selezionata, ma filtra esclusivamente i result della singola data scelta. La vista `Periodo` resta invece l'unica vista a intervallo. Il trend SVG gestisce ora anche il caso di una sola data visualizzando il punto singolo, inclusi eventuali punti secondari per curve componenti.
- corretta la semantica delle statistiche totali nelle analytics atleta: quando nessun apparatus e selezionato, il dataset usato per media, best/latest, conteggi, trend e medie annuali esclude sempre `AA`. Il punteggio all-around e infatti una somma di punteggi gia rappresentati dagli attrezzi e includerlo nella media totale avrebbe prodotto una distorsione. `AA` resta comunque analizzabile quando l'utente seleziona esplicitamente il relativo pulsante apparatus.
- rifinita la visualizzazione del trend nella modalita `Istante`: sopra la timeline viene mostrata solo la data selezionata, senza prefisso `Al/At`, perche non e un intervallo. Il calcolo resta puntuale sulla singola data, ma il grafico mantiene la curva storica in secondo piano con una linea piu chiara; il momento selezionato viene evidenziato con un punto piu marcato sulla curva, preservando il contesto senza trasformare `Istante` in una statistica cumulativa.
- aggiunto alle analytics atleta il contesto dei cicli olimpici/scoring cycles, coerente con la sezione `Rankings`: sopra i grafici viene indicato a quali cicli appartengono i result selezionati e, quando la selezione attraversa piu cicli, viene mostrato un warning metodologico sui possibili diversi Codes of Points. Il grafico trend ora usa una scala temporale reale, mostra una scala del punteggio sull'asse Y, etichette dinamiche sull'asse X (anni, mesi o giorni in base al periodo visibile) e linee verticali tratteggiate per separare i diversi cicli di punteggio.
- corretta anche la semantica visiva del cursore temporale nella modalita `Istante`: la track non evidenzia piu il tratto precedente al cursore, per evitare che l'utente interpreti la selezione come un periodo cumulativo. In `Istante` resta evidenziato solo il punto del cursore relativo alla data precisa selezionata.
- aggiunta una scala indicativa anche al diagramma radar/rombo della scheda atleta: i quattro ring principali mostrano piccole etichette numeriche coerenti con la metrica selezionata (`Final Score`, `D Score`, `E Score`, `Penalty`, `Bonus`). Per `Penalty`, dove un valore piu basso e migliore, la scala viene invertita per mantenere corretta la lettura dell'area del grafico.
- separato lo stato del cursore `Istante` dallo stato dei cursori `Periodo`: la modalita snapshot ora usa un indice temporale indipendente (`snapshotIndex`) e puo muoversi liberamente su tutto l'asse temporale, senza essere vincolata da `startIndex/endIndex` del periodo e senza modificarli. La UI della timeline, in modalita `Istante`, mostra inoltre una sola data selezionata.
- rimossa dalla timeline analytics atleta l'etichetta testuale duplicata sopra il cursore: ora la timeline mostra un solo punto di lettura delle date, cioe una sola data in modalita `Istante` e la coppia `Da/A` in modalita `Periodo`.
- corretta la rigenerazione live dei box data della timeline analytics quando l'utente passa da `Periodo` a `Istante`: il blocco date viene ora ricostruito in base alla modalita attiva, evitando che resti visibile il box `Da` del periodo precedente con la stessa data dello snapshot.
- definita la semantica temporale dei result provenienti da eventi multigiorno: LEVERAGE non richiede all'admin di ricostruire manualmente le date esatte di qualifiche, finali o sessioni quando queste non sono presenti nei file Gymternet/Calendar, perche sarebbe un lavoro non sostenibile e non coerente con la granularita della fonte. Il backend espone ora, per i punti analytics, `event_start_date`, `event_end_date` e `date_precision`; quando il result non ha un `day` affidabile, il punto resta ancorato all'inizio evento solo per ordinamento cronologico, ma la UI mostra esplicitamente il `Periodo evento` e un avviso metodologico. Nei tooltip del trend vengono inoltre riportati nome evento, round, format, disciplina e apparatus, cosi piu punteggi collocati nello stesso riferimento temporale sono distinguibili per gara/tipo di gara senza inventare date non disponibili.
- rifinita la comunicazione della stessa regola nelle statistiche atleta: il chiarimento sul `Periodo evento` viene ora mostrato direttamente sotto le statistiche riepilogative quando la selezione contiene result da eventi multigiorno senza data sessione esatta, includendo i periodi e alcuni contesti gara/round/format coinvolti. Nella modalita `Istante`, il box data mostra soltanto la data o il periodo selezionato, senza piu l'etichetta `Al`, per evitare di suggerire una lettura cumulativa.
- micro-correzione successiva: il box `Fonte temporale` nella sezione statistiche atleta viene mostrato ogni volta che esistono result inclusi nella selezione analytics, non solo quando il sottoinsieme corrente contiene result multigiorno marcati come `event_period`. In assenza di eventi multigiorno specifici, il box spiega comunque che le statistiche usano date o periodi evento disponibili in LEVERAGE; nella modalita `Istante`, il box data usa ora l'etichetta `Data`, coerente con `Da data` e `A data` della modalita `Periodo`.
- ulteriore rifinitura informativa: il box `Fonte temporale` non mostra piu solo una nota metodologica, ma riepiloga anche le gare coinvolte nella selezione analytics, indicando nome evento, periodo inizio/fine e round/format disponibili. Nella modalita `Istante`, invece, il box `Data` resta volutamente piu semplice: se il punto selezionato appartiene a un evento multigiorno, mostra soltanto il periodo inizio/fine dell'evento, perche in assenza di data sessione esatta l'istante rappresenta il periodo fonte della competizione e non un singolo giorno.
- corretto il calcolo del label del box `Data` in modalita `Istante`: il testo non viene piu derivato solo dai result inclusi dalla metrica corrente, ma da un contesto temporale dedicato (`timelineLabelPoints`) che include i punti della data selezionata indipendentemente dalla disponibilita della metrica. In questo modo, anche quando l'utente osserva una metrica parziale, il box puo continuare a mostrare correttamente entrambe le date dell'evento multigiorno, senza aggiungere nome gara o round/format nel box data.
- aggiunti marker verticali sulla timeline delle analytics atleta per segnalare i cambi di ciclo olimpico / Code of Points. I marker usano la stessa logica gia applicata alle linee verticali del grafico trend, cosi il cursore temporale e il grafico condividono la stessa semantica dei cicli (`2017-2021`, `2022-2024`, `2025-2028`, ecc.).
- rifinita la leggibilita dei marker ciclo sulla timeline: sopra ogni trattino viene mostrato in modo molto leggero l'anno di inizio del nuovo ciclo, per esempio `2022` o `2025`, mantenendo il dettaglio completo del ciclo nel contesto/tooltip.
- revisione globale dei box di avviso/avvertimento della UI: gli avvisi tecnici provenienti dal backend (`data_warnings` di Result/Rankings/analytics atleta e warning World Gymnastics) non vengono piu mostrati come stringhe raw in inglese, ma passano da un livello di localizzazione frontend coerente con la lingua selezionata dall'utente (`en`, `it`, `es`, `fr`). Sono stati inoltre corretti i casi singolare/plurale nei box analytics, per esempio `Ciclo olimpico` quando la selezione contiene un solo ciclo e `Cicli olimpici` quando ne contiene piu di uno, oltre ai conteggi `1 risultato/2 risultati`, `1 punto/2 punti` e `1 suggerimento admin/2 suggerimenti admin`. La scelta mantiene invariato il contratto dati del backend ma rende la comunicazione metodologica piu pulita, comprensibile e coerente a livello UI.
- rafforzata la deduplica semantica degli avvisi `execution_estimate`: quando una vista aggrega result con warning diversi sulla stima dell'esecuzione, la UI non mostra piu messaggi quasi duplicati. Gli avvisi generici, con `Penalty` non disponibile, con `Bonus` possibile e con `Penalty + Bonus` vengono condensati in un solo messaggio, scegliendo sempre la variante piu completa necessaria per descrivere i dati selezionati.
- semplificata la homepage iniziale: sono state rimosse le preview operative di `Calendario` e `Ranking`, lasciando la prima schermata concentrata su brand, sottotitolo, ricerca globale e quattro percorsi principali verso `Athletes`, `Events`, `Rankings` e `Analytics`. Le funzionalita complete di calendario e ranking restano disponibili nelle rispettive sezioni dedicate.
- micro-rifinitura della homepage dopo la rimozione delle preview: padding verticale, altezza hero, distanza della search globale e altezza delle quattro card iniziali sono stati leggermente ridotti solo nella home, cosi l'intero contenuto principale entra nel primo viewport senza richiedere scroll nelle condizioni desktop standard.
- rimosso dal footer il box tecnico `API`, usato solo durante lo sviluppo per cambiare manualmente il backend FastAPI della preview. La scelta rende la UI piu pulita per l'utente finale; la logica interna di fallback automatico verso i backend locali resta nel frontend, cosi la preview puo continuare a funzionare senza esporre controlli tecnici.
- corretta la semantica della ricerca globale: `country` e `apparatus` restano segnali interpretati dal motore di ricerca per filtrare meglio atleti, eventi e risultati, ma non vengono piu mostrati come categorie autonome di output. Suggerimenti e pagina risultati della ricerca globale espongono quindi solo tre famiglie cliccabili: `Athletes`, `Events` e `Results`, evitando blocchi generici come "nazioni" con centinaia di atleti o "apparatus" con migliaia di punteggi.
- micro-rifinitura degli heading delle sezioni principali: le viste `Athletes`, `Events`, `Rankings` e `Analytics` usano ora una spaziatura superiore dedicata, leggermente piu compatta rispetto alle pagine generiche, cosi titolo e sottotitolo risultano piu allineati visivamente alla wordmark LEVERAGE della homepage senza alterare la posizione dei contenuti delle pagine dettaglio.
- rifinita la topbar principale con un indicatore di sezione attiva dinamico: la vecchia sottolineatura statica sul singolo link e stata sostituita da un unico indicatore animato che si sposta e ridimensiona fluidamente tra `Home`, `Athletes`, `Events`, `Rankings` e `Analytics` al cambio rotta, mantenendo una percezione piu app-like della navigazione.
- allineata la semantica delle analytics atleta ai `Rankings`: quando l'utente apre una scheda atleta, la timeline delle statistiche parte di default dall'ultimo ciclo olimpico disponibile per quell'atleta, invece che dall'intero storico. Lo storico resta comunque disponibile tramite i cursori temporali. Il box di contesto del ciclo usa lo stesso stile `context-note` dei `Rankings`, con formato `MAG/WAG · Ciclo olimpico 2025-2028`; se l'utente seleziona un periodo che attraversa piu cicli, viene mostrato l'avviso metodologico sui diversi Codes of Points.
- aggiunto un tooltip dinamico ai punti del trend nelle analytics atleta: passando con mouse o focus tastiera sui punti reali della curva, LEVERAGE mostra vicino al grafico valore, fonte temporale e contesto gara/round/format collegato al risultato. Il tooltip sostituisce la sola informazione browser nativa e mantiene uno stile coerente con le card e i box informativi della piattaforma.
- snellito il tooltip del trend atleta: ora mostra solo valore, data/periodo fonte e nome gara. Sono stati rimossi i `<title>` SVG nativi dai punti e dalle linee del trend, evitando la comparsa ritardata del popup grigio del browser sopra il tooltip custom.
- rimossi globalmente i tooltip nativi del browser dalla UI frontend: oltre ai `<title>` SVG delle analytics, sono stati eliminati gli attributi HTML `title` da calendario, pulsanti preferiti, cestino ranking salvati, crocette di cancellazione ricerca, filtri `Level/Periodo` e marker dei cicli olimpici. Nel calendario, le barre evento mantengono un'etichetta accessibile (`aria-label`) ma non generano piu popup grigi nativi al passaggio del mouse; eventuali tooltip informativi dovranno restare custom e coerenti con lo stile LEVERAGE.
- micro-rifinitura visuale del tooltip trend atleta: il box custom e stato reso leggermente piu piccolo, mantenendo comunque spazio sufficiente per visualizzare valore, data/periodo e nome gara senza appesantire il grafico.
- corretta la visualizzazione temporale degli eventi multigiorno nelle statistiche della scheda atleta: quando il backend espone `date_precision=event_period`, la UI non mostra piu il result come associato al solo primo giorno dell'evento, ma usa la label del periodo gara (`start_date-end_date`) nei box della timeline e nel tooltip del trend. La data di inizio resta solo un'ancora tecnica interna per ordinamento e posizionamento cronologico, non una data sessione dichiarata.
- precisata la semantica del tooltip trend per eventi multigiorno: anche quando il punto resta agganciato al primo giorno dell'evento per posizionamento cronologico, il tooltip dinamico mostra sempre il periodo completo `start_date-end_date` se la gara ha data di inizio e fine diverse. In questo modo l'utente vede chiaramente che il risultato appartiene al periodo gara e non necessariamente al singolo giorno iniziale.
- ulteriore correzione sul tooltip trend dopo verifica reale con `Abbadini Yumin` alle `Olympic Games` 2024: il backend aveva correttamente `start_date=2024-07-26` ed `end_date=2024-08-11`, ma il tooltip poteva ancora ricadere sulla data visuale del punto. Il tooltip ora usa direttamente `athleteAnalyticsPointEventPeriodLabel` per i punti raggruppati del trend, cosi ogni evento multigiorno mostra sempre inizio e fine evento.
- individuata e risolta la causa effettiva della mancata visualizzazione del periodo nel tooltip: i server backend di preview gia attivi su `8000/8001` stavano servendo una versione non aggiornata del payload analytics, priva di `event_start_date`, `event_end_date` e `date_precision`. E stato avviato un backend aggiornato su `8002` e il frontend locale ora lo preferisce automaticamente nelle preview `517x`, evitando che dati live vecchi facciano ricadere il tooltip sulla sola data tecnica del punto.
- riallineati i marker dei cicli olimpici sulla timeline della scheda atleta: i cursori della timeline si muovono per indici discreti dei result disponibili, mentre i marker erano calcolati su una scala temporale continua. Ora i marker vengono interpolati dentro lo step corretto della timeline, usando la stessa scala dei cursori; le linee verticali del grafico trend restano invece su scala temporale reale, coerenti con l'asse X del grafico.
- aggiunta memoria di navigazione per le sezioni principali della topbar: durante la sessione browser, LEVERAGE ricorda l'ultimo route visitato dentro `Athletes`, `Events`, `Rankings` e `Analytics`. Se l'utente apre una scheda atleta, passa temporaneamente a un'altra sezione e poi clicca di nuovo `Athletes` nella topbar, ritorna alla stessa scheda atleta invece che alla lista base. Lo stesso comportamento vale per eventi, ranking e analytics. I pulsanti interni `Torna agli Atleti/Eventi` restano invece link espliciti verso le rispettive liste.
- ripristinata la preview locale dopo il cambio porte: le origini CORS di sviluppo includono ora anche `5177`, `5178` e `5179`, cosi le preview statiche aperte su porte successive possono caricare i record dal backend aggiornato senza errore browser. Nella scheda atleta e stato inoltre rimosso il grande box `Fonte temporale`, perche la stessa informazione metodologica essenziale viene ora comunicata in modo piu leggero dal tooltip del grafico trend.
- resa piu minimale la scheda atleta pubblica: i tre riquadri separati `Identita`, `World Gymnastics` e `Storico nazionalita` sono stati accorpati in un unico pannello generale `Identita`. La hero della scheda mantiene solo immagine/iniziali, nome atleta in formato `Cognome Nome`, meta essenziale e pulsante preferito per utenti loggati; i dettagli come ID, country, discipline, birth year, stato/link World Gymnastics e storico nazionalita vengono mostrati nel pannello identita solo quando il relativo dato e realmente presente. In questo modo la UI evita righe `Non disponibile` nella vista pubblica e resta coerente con il principio di mostrare solo dati approvati e disponibili.
- rinominata nella UI la presentazione degli identificativi interni: dove prima compariva `Athlete ID` o una generica chip `ID`, ora viene mostrato `Leverage ID`, applicato alle schede atleta, ai preferiti atleta e alla scheda evento. Il backend conserva invariati i campi tecnici `id`, `athlete_id` ed `event_id`, mentre la UI rende piu chiara la differenza tra identificativo interno LEVERAGE e identificativi ufficiali esterni come `World Gymnastics ID`.
- ulteriore compattazione della scheda atleta: il pannello `Identita` usa ora padding, gap, campi e storico nazionalita piu densi, riducendo lo spazio verticale prima delle analytics. La barra filtri delle analytics atleta e stata riorganizzata in due cluster: a sinistra metrica punteggio e apparatus, a destra modalita temporale e timeline. La scelta permette di variare metrica, attrezzi e periodo mantenendo piu facilmente visibili nello stesso viewport il diagramma poligonale e il grafico trend, preservando l'aggiornamento live gia implementato.
- spostate le statistiche riepilogative delle analytics atleta (`Media`, `Migliore`, `Ultimo`, `Eventi`, `Risultati totali`) sotto ai grafici. La scheda ora privilegia prima l'osservazione visiva di diagramma poligonale, trend e barre annuali; i valori numerici sintetici diventano una lettura di conferma immediatamente successiva.
- riallineata la UI delle analytics atleta alla grammatica dei filtri principali di LEVERAGE: metriche, apparatus e modalita temporale usano ora la stessa altezza, radius, padding, peso tipografico e comportamento visivo dei `filter-button` e degli slider gia presenti nelle sezioni `Athletes`, `Events` e `Rankings`. Anche i riquadri grafici e le statistiche riepilogative usano superficie, bordo, radius e ombra coerenti con card e pannelli del resto della piattaforma.
- riorganizzata la gerarchia visiva delle analytics nella scheda atleta: i filtri `Metrica` e `Apparatus` restano a sinistra, mentre `Vista temporale` e `Timeline` vengono collocati subito sotto i filtri attrezzi. A fianco dei controlli viene mostrato il diagramma poligonale MAG/WAG, cosi l'utente puo variare filtri e periodo osservando immediatamente la forma tecnica dell'atleta. Il grafico `Trend` e stato spostato subito sotto questa fascia e reso full-width, con una base SVG piu larga e alta, per diventare il principale grafico temporale della scheda.
- corretto il comportamento di riavvolgimento delle liste nelle sezioni `Athletes`, `Events` e `Rankings`: quando l'utente digita nella ricerca o modifica un filtro, lo scroll verso l'inizio dei record calcola ora anche l'altezza reale del menu sticky della sezione, oltre alla topbar. In questo modo i primi record non restano nascosti sotto ricerca/filtri e, anche per i cambi filtro espliciti, la UI torna al primo record della lista aggiornata senza far rivedere titolo e sottotitolo della sezione. Il click sui filtri avvia subito lo scroll smooth sui record gia visibili e aggiorna i dati senza sostituire temporaneamente la lista con un box `Loading`, preservando l'effetto di riavvolgimento percepito durante la digitazione.
- micro-rifinita la centratura verticale della homepage: il contenuto principale della Home e stato abbassato leggermente aumentando solo il padding superiore della vista iniziale. La modifica non tocca le sezioni interne e serve a rendere piu bilanciata la composizione del primo viewport dopo splash logo e topbar.
- resa piu compatta la chip identificativa nelle card atleta di lista: nella sezione `Athletes` e nelle liste di atleti preferiti viene mostrato solo `ID`, perche il contesto rende implicito che si tratti dell'identificativo interno LEVERAGE. Nella scheda dettaglio atleta resta invece l'etichetta completa `Leverage ID`, cosi l'utente distingue chiaramente l'ID interno dagli eventuali identificativi ufficiali esterni.
- uniformata la capitalizzazione dei titoli delle quattro card iniziali della homepage: `Atleti`, `Eventi` e `Performance` vengono ora mostrati con iniziale maiuscola, coerentemente con `Rankings` e con la funzione di questi elementi come percorsi principali della piattaforma.
- rivista nuovamente la scheda atleta dopo review UI: la soluzione con identita e controlli analytics nello stesso rettangolo sticky e stata scartata perche risultava troppo densa. La scheda ora parte con un blocco informativo normale e pulito composto da nome atleta, immagine/iniziali, preferito e pannello `Identita`; sotto, la sezione analytics ha un menu sticky dedicato solo a bottoni e cursori, coerente con i menu filtro di `Events` e `Rankings`. I grafici principali vengono mostrati sotto il menu: diagramma poligonale MAG/WAG piu piccolo a sinistra e trend temporale piu ampio a destra.
- riordinata la gerarchia dei controlli analytics nella scheda atleta: nel menu sticky vengono mostrati prima i pulsanti degli attrezzi, poi sotto la metrica di punteggio (`Final Score`, `D Score`, `E Score`, `Penalty`, `Bonus`) e infine i controlli temporali. La scelta privilegia prima la selezione tecnica dell'apparatus e poi il criterio numerico con cui leggerlo.
- ripulito il riquadro del diagramma poligonale nelle analytics atleta: le card con i punteggi dei singoli attrezzi sotto il grafico sono state rimosse per ridurre rumore visivo. Il dettaglio del valore resta disponibile tramite un tooltip custom sui pallini del radar/rombo, coerente con il tooltip del trend e privo di tooltip nativi del browser.
- riallineata la barra dei controlli analytics della scheda atleta: dopo una prima soluzione con `Vista temporale` a destra e timeline sotto, il blocco temporale e stato reso piu compatto e semantico. Lo slider `Periodo/Istante` e ora affiancato direttamente alla timeline, con il selettore a sinistra e la linea temporale piu corta a destra; il cluster temporale resta allineato alla riga degli apparatus, mentre la metrica di punteggio viene mantenuta subito sotto agli apparatus nella colonna sinistra, coerentemente con la gerarchia dei filtri delle altre sezioni.
- rifinito l'allineamento interno del cluster temporale nelle analytics atleta: il box `Da data/A data` non resta piu immediatamente sotto la linea della timeline, ma viene abbassato sulla stessa riga visiva dei filtri metrica. La linea temporale rimane accanto allo slider `Periodo/Istante`, mentre le date diventano un elemento di lettura allineato ai controlli numerici sottostanti.
- aumentata leggermente l'altezza dei box data sotto la timeline delle analytics atleta: `Da data/A data` e il box singolo `Data` in modalita `Istante` usano ora un'altezza minima coerente con la meta selezionata dello slider verticale `Periodo/Istante`, con label e valore centrati verticalmente.
- arrotondato il box date della timeline atleta usando lo stesso `control-radius` dei filtri e degli slider vicini, eliminando l'effetto troppo squadrato del precedente `data-chip-radius` e rendendo `Da data/A data` piu coerenti con la grammatica morbida dei controlli.
- riallineata la posizione verticale del box date sotto la timeline atleta: mantenendo invariati dimensione e radius, e stato ridotto il gap interno del cluster temporale cosi il bordo inferiore di `Da data/A data` coincide con il bordo inferiore del riquadro esterno dello slider verticale `Periodo/Istante`.
- trasformato lo slider `Periodo/Istante` delle analytics atleta in un controllo verticale piu stretto e alto: `Periodo` viene mostrato sopra `Istante` e il thumb scorre dall'alto verso il basso, invece che da sinistra a destra. Dopo review visiva, l'altezza e stata ritarata sul bordo esterno reale del controllo, senza considerare il precedente margine interno del thumb blu, cosi il fondo dello slider resta piu vicino all'allineamento di metrica e box date.
- uniformata la grammatica visiva di tutti i segmented slider LEVERAGE: il thumb blu della selezione riempie ora completamente la porzione selezionata del controllo, senza lasciare il piccolo vuoto interno tra rettangolo blu e bordo dello slider. La regola vale per `MAG/WAG`, `Lista/Calendario`, `Nome/Nazione`, metriche `Rankings`, metriche analytics atleta e slider verticale `Periodo/Istante`.
- micro-rifinitura dello slider verticale `Periodo/Istante`: mantenendo fermi dimensione e posizione del riquadro esterno, il thumb blu interno e stato centrato sulle due selezioni facendo occupare esattamente meta del controllo a `Periodo` e meta a `Istante`. Il movimento verticale usa quindi la stessa semantica del controllo: prima meta superiore, seconda meta inferiore.
- semplificata ulteriormente la barra analytics della scheda atleta rimuovendo le etichette visibili `Apparatus`, `Metrica`, `Vista temporale` e `Timeline` sopra i relativi controlli. I pulsanti e gli slider restano autoesplicativi, mentre le label vengono mantenute come `aria-label` accessibili; la UI risulta cosi piu coerente con i filtri delle sezioni `Athletes`, `Events` e `Rankings`.
- uniformata la distanza orizzontale tra i pulsanti filtro delle sezioni principali alla densita compatta della scheda atleta: toolbar e gruppi azione di `Athletes`, `Events` e `Rankings` usano ora lo stesso gap visivo dei filtri apparatus nelle analytics atleta, mantenendo invariati altezza, radius e tipografia dei controlli.
- aggiunta sotto al diagramma poligonale MAG/WAG una piccola legenda coerente con quella del trend: il box mostra solo il valore collegato alla selezione apparatus corrente. Per attrezzi singoli o multi-selezione mostra esclusivamente i valori degli attrezzi selezionati; per aggregati esclusivi come `AA` e `VT AVG` mostra il valore sintetico della selezione, evitando di trasformare il radar in una lista completa di tutti gli attrezzi.
- rimpicciolito leggermente il diagramma poligonale dentro la stessa card grafica e successivamente riallineata la sua legenda: il riquadro del radar/rombo mantiene le stesse dimensioni esterne, ma organizza internamente intestazione, grafico e legenda in modo che la legenda resti nella fascia bassa della card. Dopo review visiva, la legenda e stata tarata di pochi pixel rispetto al fondo pieno e il mini-box informativo e stato uniformato alla legenda del trend per altezza, padding e tipografia, senza modificare i riquadri esterni.
- resa esclusiva la selezione degli aggregati tecnici `AA` e `VT AVG` rispetto agli attrezzi singoli, sia nella sezione `Rankings` sia nelle analytics della scheda atleta. `AA` rappresenta l'all-around e `VT AVG` la media dei due salti: nessuno dei due puo essere selezionato insieme a `FX/PH/SR/VT/PB/HB` o `VT/UB/BB/FX`. Se l'utente seleziona un attrezzo mentre `AA` o `VT AVG` sono attivi, l'aggregato viene rimosso automaticamente; se seleziona `AA` o `VT AVG` dopo uno o piu attrezzi, gli attrezzi vengono rimossi. L'endpoint backend `/analytics/rankings` rifiuta inoltre chiamate dirette con aggregati combinati ad altri apparatus, per mantenere coerente anche il contratto API.
- impostato `AA` come selezione apparatus iniziale nelle due viste di analisi principali: quando l'utente apre la sezione `Rankings` o una scheda atleta, il filtro parte da `AA` preselezionato. La scelta evita che la prima lettura mescoli automaticamente attrezzi singoli e aggregati e rende subito chiaro il contesto all-around; l'utente puo comunque deselezionare `AA` o sostituirlo con uno o piu attrezzi singoli.
- rafforzata la stessa regola apparatus lato UI: non e piu possibile lasciare la selezione apparatus vuota, ne nella sezione `Rankings` ne nelle analytics della scheda atleta. Se l'utente deseleziona l'ultimo attrezzo attivo, il frontend riattiva automaticamente `AA`, mantenendo sempre un contesto tecnico esplicito e impedendo classifiche/grafici senza filtro apparatus.
- migliorata la leggibilita dei grafici nella scheda atleta: il trend temporale usa ora una scala verticale dinamica centrata sui valori osservati, invece di partire sempre da zero, cosi le variazioni tra punteggi vicini risultano piu visibili. Il diagramma poligonale/radar mantiene la scala sportiva di riferimento, ma mostra anelli, assi, tacche e valori guida con maggiore contrasto, includendo anche un riferimento centrale coerente con la metrica selezionata.
- migliorata la lettura delle curve componenti nel trend atleta: quando l'utente seleziona `AA`, le curve degli attrezzi che compongono il contesto all-around vengono mostrate con colori distinti e intensita tenue, lasciando la curva principale in blu LEVERAGE. Lo stesso criterio viene applicato quando l'utente seleziona piu attrezzi singoli: la curva principale rappresenta l'aggregato della selezione, mentre le curve secondarie mostrano i singoli attrezzi con colori piu leggeri e stabili.
- corretta la semantica delle curve secondarie nel trend atleta dopo revisione metodologica: nel caso `AA`, mostrare le curve dei singoli attrezzi accanto al trend all-around e stato considerato poco utile per interpretare la composizione del punteggio aggregato. Il trend `AA` mantiene quindi come curva principale il `Final Score`, mentre le curve secondarie leggere mostrano `D Score`, `E Score`/esecuzione stimata e, quando presenti con valori effettivi, `Penalty` e `Bonus` riferiti allo stesso contesto di risultato. La stessa logica viene applicata quando l'utente seleziona un singolo attrezzo o `VT AVG`: la curva principale resta il `Final Score` dell'attrezzo selezionato, mentre le curve secondarie descrivono la composizione D/E/P/B di quei punteggi. La visualizzazione per-attrezzo con colori distinti resta invece attiva solo quando l'utente seleziona piu attrezzi semplici contemporaneamente. Il backend espone inoltre `score` e `D_score` dentro i punti analytics, cosi il frontend puo calcolare questi overlay senza nuove chiamate API e senza salvare campi derivati nel database.
- aggiunto lo zoom diretto sul grafico trend della scheda atleta tramite trackpad/mouse wheel e gesture pinch dove supportata dal browser. Lo zoom non crea uno stato separato dal resto della UI: nella vista `Periodo` modifica gli stessi indici temporali `Da/A` usati dalla timeline, centrando l'ingrandimento sul punto orizzontale del grafico in cui si trova il cursore. In questo modo curva del trend, diagramma poligonale, statistiche riepilogative, cursori e box data restano sempre sincronizzati.
- rifinito il feedback del cursore sul grafico trend della scheda atleta: il mouse non mostra piu sempre la lente di ingrandimento o le frecce slider solo al passaggio sopra il grafico. Il cursore speciale compare temporaneamente soltanto quando l'utente modifica davvero il trend tramite wheel/trackpad o gesture, usando `zoom-in` in modalita `Periodo` ed `ew-resize` in modalita `Istante`.
- estesa la logica delle curve secondarie del trend atleta anche quando la metrica principale selezionata non e `Final Score`, ma `D Score` o `E Score`. Se l'utente seleziona `D Score`, la curva principale diventa il D-score e vengono mostrate, con colori opachi, le altre metriche disponibili dello stesso risultato (`Final Score`, `E Score`/stima, eventuali `Penalty` e `Bonus`). Se seleziona `E Score`, la curva principale diventa l'esecuzione e le curve secondarie mostrano `Final Score`, `D Score` ed eventuali componenti P/B. Per `AA`, il backend espone nei punti analytics anche il `D Score` totale derivato dagli attrezzi, cosi la stessa lettura compositiva funziona anche sull'all-around senza salvare valori derivati come campi ufficiali del result.
- reso piu fluido il cambio metrica nelle analytics della scheda atleta: passare da `Final Score` a `D Score` o `E Score` non attiva piu una nuova chiamata backend ne un ricaricamento visibile del pannello. Il payload atleta viene usato come base dati ricca e il frontend ricalcola localmente il valore principale della curva, mantenendo invariati periodo/istante, punti temporali e filtri apparatus. La transizione e ora locale al solo contenuto grafico, evitando che lo sticky menu dei controlli diventi temporaneamente trasparente quando si trova sopra i grafici.
- riposizionati gli avvisi metodologici delle analytics atleta sotto tutti i dati principali della scheda: grafici, breakdown annuale e box riepilogativi (`Media`, `Migliore`, `Ultimo`, `Eventi`, `Risultati totali`) vengono ora mostrati prima, mentre avvisi su ciclo olimpico, E-score stimata, metriche non disponibili e warning qualita dato compaiono in fondo al pannello. La scelta mantiene gli alert accessibili ma riduce l'interferenza iniziale con la lettura dei dati.
- esteso il gesto trackpad nella vista `Istante` delle analytics atleta: quando l'utente scorre sul grafico trend, LEVERAGE non esegue uno zoom dell'intervallo, perche `Istante` resta semanticamente una singola data/periodo fonte. Lo stesso gesto sposta invece il punto snapshot avanti o indietro lungo le date che hanno dati disponibili per la metrica e l'apparatus selezionati, aggiornando in tempo reale curva, diagramma, riepiloghi e box data.

## 19. Milestone - Scheda Atleta completata

Data milestone: 11 settembre 2026

LEVERAGE ha raggiunto una milestone importante dello sviluppo frontend MVP: la `Scheda Atleta` lato utente e stata considerata completata in modo definitivo nella sua struttura principale.

Stato raggiunto:

- la scheda atleta mostra identita, dati disponibili dell'entita e collegamento ufficiale World Gymnastics quando presente;
- la visualizzazione usa in modo coerente cognome prima del nome e `Leverage ID` come identificativo interno;
- l'utente loggato puo usare la stellina per salvare l'atleta tra i preferiti;
- la sezione analytics atleta include diagramma poligonale MAG/WAG, trend temporale, metriche, filtri apparatus, timeline periodo/istante, statistiche riepilogative e avvisi metodologici;
- i controlli sono stati rifiniti fino a una grammatica UI coerente con il resto della piattaforma: pulsanti compatti, slider coerenti, thumb centrati, box date allineati, tooltip custom e nessun popup nativo browser;
- la semantica tecnica dei grafici e stata consolidata: `AA` e `VT AVG` sono aggregati esclusivi, non e possibile lasciare nessun apparatus selezionato, `AA` e default iniziale, i cicli olimpici sono segnalati e gli avvisi su stime/dati non disponibili sono mostrati in fondo alla scheda;
- il comportamento interattivo e stato chiuso: cambio metrica senza reload visibile, zoom del trend in modalita `Periodo`, scorrimento dell'istante tramite trackpad in modalita `Istante`, tooltip dinamici sui punti reali.

Decisione progettuale:

- la `Scheda Atleta` viene salvata come blocco funzionale completato per l'MVP USER;
- ulteriori modifiche future dovranno essere considerate evoluzioni successive, non parte della rifinitura base della scheda;
- il prossimo passo di sviluppo sara la `Scheda Evento`, da progettare con coerenza UI e semantica rispetto alla scheda atleta appena chiusa.

## 20. Sviluppo Scheda Evento

Data aggiornamento: 11 settembre 2026

Dopo la chiusura della `Scheda Atleta`, e stato avviato lo sviluppo della `Scheda Evento` con l'obiettivo di riutilizzare la stessa grammatica UI e la stessa logica semantica gia consolidata per gli atleti.

Scelte implementate:

- la pagina dettaglio evento parte direttamente dal contenuto dell'evento, senza ripetere il titolo generale della sezione `Events`;
- e stato mantenuto il comando app-style `Torna agli Eventi`, coerente con `Torna agli Atleti` e `Torna alla Home`;
- il blocco superiore della scheda mostra immagine/iniziali evento, nome gara, periodo, luogo, discipline, categorie, livello, stato calendario, numero risultati e identificativi ufficiali disponibili;
- l'identificativo interno viene mostrato come `Leverage ID`, per distinguere il dato tecnico LEVERAGE da eventuali ID ufficiali World Gymnastics;
- il collegamento ufficiale World Gymnastics viene mostrato come `Evento World Gymnastics`, non come profilo atleta, per mantenere corretta la semantica della scheda;
- il blocco informativo usa lo stesso principio della scheda atleta: i dati non disponibili non vengono mostrati nella vista pubblica, evitando rumore visivo;
- sotto ai dettagli evento e stata predisposta la sezione `Risultati evento`, che legge dal backend le classifiche realmente disponibili per quella gara;
- l'utente puo selezionare disciplina, categoria, format, round, apparatus, day e metrica ranking solo tra i valori effettivamente presenti per quell'evento;
- la classifica evento usa gli endpoint backend dedicati `profile-view` e `ranking-view`, mantenendo isolato lo stato dei filtri della scheda evento rispetto alle sezioni globali `Events` e `Rankings`;
- se `rank` ufficiale e disponibile, la classifica lo mantiene come riferimento; altrimenti resta coerente la logica di ordinamento per metrica selezionata;
- sotto alla classifica vengono mostrati gli avvisi metodologici relativi ai punteggi, inclusi E Score stimata, Penalty/Bonus non disponibili e warning tecnici gia previsti nel backend;
- per gli utenti loggati resta disponibile la stellina evento, coerente con il sistema di eventi preferiti;
- per admin loggati e stata predisposta la sezione strumenti evento: modifica dei campi principali, gestione immagine/link, suggerimenti pendenti e motore World Gymnastics Event leggero quando supportato dal backend;
- gli strumenti admin restano separati dalla vista utente, cosi la scheda pubblica rimane minimale e consultabile.

Verifiche effettuate:

- `GET /events/{event_id}/profile-view` restituisce correttamente evento, opzioni filtro, gruppi classifica, ranking di default e conteggio risultati;
- `GET /events/{event_id}/ranking-view` restituisce correttamente una classifica filtrata per disciplina, categoria, format, round, apparatus e metrica;
- la sintassi JavaScript del frontend risulta valida;
- il controllo `git diff --check` non segnala errori di whitespace.

Decisione progettuale:

- la `Scheda Evento` segue lo stesso modello concettuale della `Scheda Atleta`: dettaglio entita in alto, contenuto analitico/operativo sotto, avvisi metodologici in fondo, strumenti admin separati;
- la pagina evento non replica le analytics atleta, ma valorizza il suo ruolo naturale nel sistema: consultazione delle classifiche e dei risultati di gara;
- eventuali affinamenti visuali successivi saranno eseguiti partendo da questa struttura stabile.

Rifinitura successiva:

- dopo review visiva, la parte iniziale della scheda evento e stata resa piu minimale e coerente con la scheda atleta;
- sono stati rimossi i badge riepilogativi sotto la hero evento, perche duplicavano informazioni gia presenti nel titolo, nel periodo e nel pannello dettagli;
- il pannello e stato rinominato semanticamente in `Informazioni` e mostra solo i campi utili non ridondanti: `Leverage ID`, luogo, venue, disciplina, categoria, level, stato solo quando diverso da evento concluso con risultati, numero risultati e link ufficiale World Gymnastics se presente;
- anno, periodo e stato tecnico completo non vengono piu ripetuti nella griglia pubblica quando sono gia impliciti o visibili altrove;
- i campi World Gymnastics tecnici restano gestibili nella sezione admin, evitando di appesantire la vista pubblica.
- rifinita la visualizzazione delle category evento composte: il valore tecnico resta `junior and senior`, ma in UI viene mostrato come `Junior and Senior`, coerente con le altre label app-style.
- estesa la stessa logica alle lingue della piattaforma: i valori tecnici composti restano invariati nel backend (`MAG and WAG`, `junior and senior`), ma in UI la congiunzione viene localizzata in base alla lingua selezionata, per esempio `MAG e WAG` e `Junior e Senior` in italiano.
- rielaborata la semantica della sezione `Classifiche evento`: nella scheda evento non vengono piu mostrati filtri liberi componibili dall'utente, perche avrebbero trasformato la gara in un generatore di ranking simile alla sezione `Rankings` e avrebbero prodotto molte combinazioni vuote o fuorvianti;
- il backend espone ora le classifiche ufficiali realmente caricate per ciascun evento come gruppi completi di `discipline`, `category`, `format`, `round`, `apparatus`, `day` e numero risultati;
- il frontend mostra questi gruppi come classifiche selezionabili gia esistenti, per esempio `MAG · Senior · Individual · Final · AA`, e carica sempre i risultati ordinati per `Final Score`;
- eventuali analisi alternative dentro una classifica evento, come ordinare temporaneamente per `D Score` o `E Score`, sono state lasciate come possibile sviluppo successivo, senza confondere la funzione principale della scheda evento.
- la visualizzazione delle classifiche evento e stata successivamente clusterizzata per rendere piu chiara la struttura reale della gara: prima divisione per disciplina (`MAG`/`WAG`), poi per categoria (`Senior`/`Junior`), poi per round e format (`Final · Individual`, `Qualification · Apparatus`, ecc.);
- dentro ogni cluster vengono mostrati solo i pulsanti delle classifiche effettivamente presenti, come `AA`, `FX`, `VT AVG` o eventuali classifiche con `day`, con conteggio dei risultati associati;
- questa scelta rafforza la differenza tra `Classifiche evento`, che sono blocchi ufficiali caricati dall'admin, e `Rankings`, che restano invece viste analitiche costruibili dall'utente tramite filtri.
- dopo ulteriore review UX, la rappresentazione visuale a cluster e stata sostituita da uno sticky menu compatto a tendine concatenate, coerente con la barra controlli della scheda atleta;
- la logica semantica dei cluster resta invariata nei dati, ma l'interfaccia permette ora di scegliere progressivamente `Sezione` (`MAG`/`WAG`), `Categoria`, `Round`, `Format`, `Apparatus` ed eventuale `Day`;
- ogni tendina mostra solo opzioni realmente disponibili per la classifica selezionata e dipende dalle scelte precedenti, evitando combinazioni vuote e mantenendo la scheda evento distinta dalla sezione `Rankings`;
- la classifica visualizzata continua a essere sempre ordinata per `Final Score`, perche rappresenta una classifica ufficiale caricata e non un ranking analitico costruito dall'utente.
- la UI dello stesso sticky menu e stata poi riallineata alla grammatica visiva di LEVERAGE: le tendine native sono state sostituite da controlli segmentati/pill con thumb blu, coerenti con gli slider gia presenti nelle sezioni principali e nella scheda atleta. La logica resta guidata e concatenata, ma l'interazione appare piu app-like e meno simile a un form amministrativo.
- rifinito il menu `Ciclo olimpico` nella sezione `Rankings`: l'opzione autonoma `Tutti i cicli` e stata rimossa dal popup perche ridondante rispetto alla selezione contemporanea di tutti i cicli disponibili. La UI continua a sintetizzare lo stato completo come `Tutti i cicli`, ma solo come riepilogo del bottone, non come opzione separata.
- corretto il filtro `Level` nella sezione `Rankings`: ora funziona come il filtro `Level` della sezione `Events`, consentendo la selezione contemporanea di piu livelli di competizione. Il backend `/analytics/rankings` accetta piu valori `level`, la UI mostra le sigle selezionate nel bottone e le configurazioni di ranking salvate conservano il filtro come lista, mantenendo compatibilita con eventuali salvataggi precedenti a valore singolo.
- alleggerita ulteriormente la Scheda Evento: rimosso il blocco descrittivo sopra lo sticky menu delle classifiche e rimosse le etichette visibili sopra i controlli (`Classifiche caricate`, `Sezione`, `Categoria`, ecc.). La selezione resta semanticamente guidata e accessibile tramite label interne, ma la vista utente diventa piu minimale e coerente con la Scheda Atleta.
- riallineato lo sticky menu della Scheda Evento alla Scheda Atleta: font dei bottoni, altezza dei segmenti, padding interno e spaziatura sono stati uniformati ai controlli analytics atleta, cosi la selezione delle classifiche evento usa la stessa grammatica visiva del resto della piattaforma.
- separata visivamente la lista dei risultati dallo sticky menu della Scheda Evento: il menu delle classifiche resta subito dopo il blocco informazioni evento, mentre i record della classifica iniziano sotto, senza essere raccolti nello stesso pannello e senza scorrere visivamente dietro ai controlli sticky.
- uniformato il comportamento di aggiornamento delle classifiche nella Scheda Evento a quello delle liste `Athletes`, `Events` e `Rankings`: quando l'utente cambia una classificazione disponibile, la lista dei record torna morbidamente all'inizio e viene aggiornata senza ricostruire l'intera pagina, mantenendo lo stesso fade leggero e la stessa gestione anti-race gia usata nelle sezioni principali.
- aggiunto nella Scheda Evento lo slider metrica `Final Score / D Score / E Score / Penalty / Bonus`, coerente con Scheda Atleta e sezione `Rankings`. La classifica evento resta agganciata alla classificazione ufficiale selezionata, ma l'utente puo osservare la stessa classifica ordinata/visualizzata per le componenti disponibili; se una metrica non e disponibile viene mostrato il relativo stato informativo gia previsto dal sistema.
- uniformati i box riepilogo sotto gli sticky menu: nella sezione `Rankings` il box inizia con `Ranking` e riporta i filtri attivi, mentre nella Scheda Evento inizia con `Classifica` e riporta disciplina, categoria, format, round, apparatus, metrica e numero risultati. Entrambi usano la stessa struttura tipografica e la stessa UI `context-note`.
- resi piu compatti gli slider della Scheda Evento: `MAG/WAG`, category, round, format e apparatus non occupano piu larghezze sproporzionate ma usano dimensioni intrinseche coerenti con i controlli analoghi di `Rankings`; lo slider metrica mantiene invece la larghezza del controllo score gia usato nelle altre sezioni.
- rifinita la distanza tra sticky menu della Scheda Evento e box riepilogo `Classifica`: lo spazio verticale effettivo, considerando sia il `gap` del contenitore sia il margine del blocco risultati, e stato allineato a quello della sezione `Rankings` tra sticky menu filtri e box riepilogo `Ranking`, mantenendo coerenza visiva tra le due aree.
- riorganizzato lo sticky menu della Scheda Evento in tre righe semanticamente distinte: prima riga con i filtri generali della classifica caricata (`MAG/WAG`, categoria, round, format ed eventuale day), seconda riga dedicata agli attrezzi, terza riga dedicata alla metrica score (`Final Score`, `D Score`, `E Score`, `Penalty`, `Bonus`). Questa struttura rende la scheda evento coerente con la logica dei controlli gia consolidata in `Rankings` e nella Scheda Atleta.
- rifinito il box avvisi della Scheda Evento: rimossa l'intestazione visibile `Avvisi risultati` e sostituito l'avviso a pillola con un box squadrato a bordi arrotondati, coerente con i riquadri principali della UI. Il testo e il bordo mantengono il colore warning previsto dal sistema, mentre lo sfondo colorato e stato rimosso per alleggerire la pagina.
- aggiornato lo sticky menu della Scheda Evento affinche gli slider mostrino sempre la grammatica completa delle classifiche previste da LEVERAGE: `MAG/WAG`, `Senior/Junior`, `Final/Qualification`, format principali e attrezzi della disciplina selezionata. Le opzioni non presenti per quello specifico evento restano visibili ma disabilitate, cosi l'utente capisce che la piattaforma supporta quella possibilita ma che quella classifica non e stata caricata per la gara selezionata. Il campo `day` resta invece dinamico, perche viene mostrato solo quando esistono risultati realmente associati a giornate diverse.
- rifinito lo stato visuale delle opzioni non disponibili nella Scheda Evento: restano attenuate ma non mostrano piu il cursore di divieto al passaggio del mouse, evitando un segnale troppo aggressivo. Lo slider `Final/Qualification` e stato allargato per contenere correttamente la label lunga `Qualification`, mantenendo coerenza con gli altri segmented control.
- corretta la gestione dello slider metrica nella Scheda Evento: quando l'utente cambia una classifica caricata (`MAG/WAG`, categoria, round, format, attrezzo o day), la metrica scelta resta attiva. La metrica rappresenta infatti una modalita di lettura della classifica selezionata, non un attributo della classifica stessa; se la nuova combinazione non dispone della metrica richiesta, la UI mostra lo stato informativo di dato non disponibile.
- corretto il comportamento visuale degli slider della Scheda Evento: il thumb blu non si basa piu su segmenti teoricamente uguali, ma viene misurato sulla posizione e sulla larghezza reale dell'opzione selezionata. Questo evita sbordi nello slider attrezzi, mantiene centrata la selezione anche con label di lunghezza diversa e ripristina l'animazione di scorrimento quando l'utente cambia classifica o metrica.
- il menu della Scheda Evento viene ora aggiornato senza ridisegno ritardato quando le opzioni restano strutturalmente uguali, evitando il traballamento del thumb blu e mantenendo fluida l'animazione di scorrimento.
- eliminato il tremolio residuo degli slider nella Scheda Evento quando si passa da `MAG` a `WAG` o viceversa: se il cambio disciplina modifica la struttura degli attrezzi disponibili, il frontend sostituisce solo lo slider che cambia davvero e sincronizza i nuovi thumb senza transizione iniziale. Gli altri slider restano stabili e la metrica scelta dall'utente rimane selezionata.
- consolidata la gestione delle richieste asincrone nella Scheda Evento: cambi rapidi e ripetuti della metrica, ad esempio `E Score` su classifiche `AA`, annullano la richiesta precedente e mantengono valida solo l'ultima selezione. Questo evita blocchi apparenti dei controlli e preserva la fluidita dello sticky menu.
- uniformata la UI degli avvisi metodologici a fondo pagina tra Scheda Evento, sezione `Rankings` e Scheda Atleta: il riepilogo in alto resta dedicato ai filtri/contesto, mentre warning su `E Score` stimata, `Penalty`, `Bonus`, vault attempt e dati non disponibili vengono mostrati in fondo con lo stesso box arrotondato, deduplicato e localizzato.
- estesa la deduplica degli avvisi anche ai casi semanticamente equivalenti: messaggi come `E Score stimato da Final Score e D Score` e `Esecuzione stimata da D Score e Final Score` vengono riconosciuti come lo stesso avviso metodologico e condensati in un'unica frase, mantenendo la versione piu specifica quando sono presenti informazioni su `Penalty` o `Bonus` non disponibili.
- arrotondati i box di contesto `context-note` usati per riepiloghi come `MAG · Ciclo olimpico 2025-2028`, `Classifica · ...` e `Ranking · ...`: il bordo usa un raggio intermedio, piu morbido del badge tecnico ma non a pillola, rendendo questi elementi coerenti con lo stile app-like sviluppato per LEVERAGE.
- corretto il box avvisi della sezione `Rankings`: oltre ai warning generali del payload, la UI puo leggere anche i `data_warnings` dei singoli result visualizzati nella lista, come gia avviene nella Scheda Evento. Tuttavia questi avvisi vengono mostrati solo quando sono semanticamente utili alla vista attiva: warning su E Score stimata quando la metrica selezionata e `E Score`, warning sul vault attempt quando il ranking riguarda `VT` o `VT AVG`, e warning generali di comparabilita quando arrivano dal backend. Questo evita rumore informativo nei ranking in cui l'avviso non serve.
- nella Scheda Atleta, il box di contesto del ciclo olimpico/scoring cycle e stato spostato sopra i due grafici principali. Questa informazione descrive il perimetro metodologico della visualizzazione e deve quindi precedere diagramma poligonale e trend, mentre gli avvisi veri restano raccolti in fondo alla sezione analytics.
- rifinita la spaziatura del box ciclo olimpico nella Scheda Atleta: il riepilogo metodologico ora precede i grafici con lo stesso respiro visivo usato nella sezione `Rankings` tra box riepilogo e lista dei record. Il warning multi-ciclo e stato inoltre alleggerito: non esplicita piu tra parentesi tutti i cicli selezionati, gia visibili nel riepilogo sopra, ma segnala solo la presenza di piu Codes of Points.
- nella sezione `Rankings`, il warning relativo alla presenza di piu cicli olimpici e stato spostato dal box avvisi finale al box riepilogo del ranking (`Ranking · ...`). Questa informazione e infatti parte del contesto metodologico della vista, non un warning puntuale di qualita del singolo result. Il box avvisi finale resta dedicato a dati stimati, componenti non disponibili, vault attempt incerto e altri avvisi tecnici.
- uniformata la dimensione tipografica dei box riepilogo (`context-note`) a quella dei box avvisi, cosi `MAG · Ciclo olimpico...`, `Classifica · ...` e `Ranking · ...` hanno lo stesso peso visivo di base. Nella Scheda Evento e nella sezione `Rankings`, le parole funzionali `CLASSIFICA` e `RANKING` sono ora rese in maiuscolo e con peso maggiore, per distinguere chiaramente il tipo di vista senza appesantire il resto del riepilogo.
- completata la grammatica dei box riepilogo: anche nella Scheda Atleta il riepilogo del ciclo olimpico inizia ora con `ANALYTICS`, coerente con `RANKING` e `CLASSIFICA`. Tutti i box riepilogo `context-note` usano inoltre un bordo blu LEVERAGE leggero, cosi risultano riconoscibili come elementi di contesto senza confondersi con i box avvisi.
- resa esplicita la mutua esclusione tra filtro `Periodo` e filtro `Ciclo olimpico` nella sezione `Rankings`: semanticamente sono due modi alternativi per definire il perimetro temporale della classifica, quindi non possono restare attivi insieme. Se l'utente imposta un periodo viene svuotato il ciclo olimpico; se seleziona uno o piu cicli olimpici viene svuotato il periodo. La stessa regola e protetta anche dal backend, che rifiuta chiamate API con `scoring_cycle`/`include_all_scoring_cycles` e filtri temporali espliciti nello stesso ranking.
- rifinita la leggibilita del calendario nella sezione `Events`: ogni settimana viene ora visualizzata come una fascia autonoma con bordo morbido e separazione chiara dalla settimana successiva. I numeri dei giorni e le barre evento restano nello stesso blocco settimanale, cosi e immediato capire che gli eventi appartengono alla riga di giorni immediatamente sopra e non alla settimana successiva.
- estesa la navigazione evento-per-evento del calendario: il piccolo box con frecce, inizialmente disponibile solo per gli eventi preferiti degli utenti loggati, compare ora anche nella vista calendario quando un visitatore o utente applica ricerca e filtri (`MAG/WAG`, categoria, `Level`, `Periodo`). Le frecce navigano tra gli eventi realmente inclusi nella selezione corrente e mantengono evidenziato l'evento agganciato, cosi la vista calendario resta utile anche per ricerche ristrette senza richiedere login.
- dopo review UX, il comportamento di inglobamento/srotolamento del menu filtri nella sezione `Rankings` e nella `Scheda Evento` e stato scartato: rendeva la lettura meno naturale e introduceva movimento non necessario. Il menu filtri/classifiche resta quindi un blocco normale sopra i record, mentre solo il box riepilogo (`RANKING` o `CLASSIFICA`) rimane sticky durante lo scroll.
- nel box riepilogo sticky di `Rankings` e `Scheda Evento` e stata mantenuta una freccia a destra, ma con funzione piu semplice e coerente: cliccandola l'utente torna verso i filtri della vista corrente con scroll morbido, come se riavvolgesse manualmente la pagina verso l'alto.
- rimosso il riavvolgimento automatico dei record quando l'utente cambia filtro nella sezione `Rankings` o nella `Scheda Evento`: in queste due viste, la lista/graduatoria si aggiorna in posizione, lasciando all'utente la scelta esplicita di tornare ai filtri tramite la freccia del riepilogo sticky.
- alleggerita la visualizzazione dei record in `Rankings` e nella `Scheda Evento`: le vecchie card verticali sono state sostituite da una graduatoria compatta condivisa, con posizione, atleta, contesto e punteggio principale in colonne leggere. Le componenti del punteggio restano disponibili in chip piu piccoli, inclusi `Final Score` associato, `D Score AA`, dettagli `AA` e componenti `VT AVG`, ma la lettura complessiva diventa piu simile a una classifica sportiva e meno a una lista infinita di record.
- nella graduatoria della `Scheda Evento` sono stati rimossi i tag ripetitivi di contesto (`MAG`, categoria, format, round, apparatus, day), perche gia presenti nel box riepilogo `CLASSIFICA`. Ogni riga evento mostra ora solo posizione, atleta, nazionalita e punteggi, rendendo la classifica piu vicina a una graduatoria ufficiale.
- applicata la stessa logica alla sezione `Rankings`: le righe non ripetono piu tag tecnici come disciplina, categoria, apparatus o anno, gia sintetizzati nel box riepilogo `RANKING`. Ogni record mostra ora atleta, nazionalita, gara con data/anno e punteggi, separando meglio contesto della vista e dati del singolo risultato.
- ordinata ulteriormente la resa delle graduatorie in forma tabellare: i dettagli del punteggio sono ora distribuiti in celle allineate. Per `AA`, gli attrezzi vengono mostrati sempre nelle colonne tecniche della disciplina (`FX`, `PH`, `SR`, `VT`, `PB`, `HB` per MAG; `VT`, `UB`, `BB`, `FX` per WAG); per `VT AVG`, le celle restano separate tra `VT 1` e `VT 2`; per gli altri attrezzi vengono allineate le componenti `Final Score`, `D`, `E`, `P`, `B` disponibili.
- aggiunta la paginazione progressiva nelle sezioni pubbliche principali `Athletes`, `Events` e `Rankings`: il caricamento iniziale mostra un primo blocco leggero di record e, quando esistono altri dati coerenti con ricerca e filtri attivi, compare in fondo il pulsante `Load more Athletes/Events/Scores`. La scelta riduce il peso iniziale della UI senza impedire all'utente di esplorare il dataset completo.
- esteso il backend dei ranking con parametro `offset`, mantenendo invariato il default. Il builder delle graduatorie accetta ora `rank_offset`, cosi le pagine successive non ripartono da `#1` ma continuano la numerazione della classifica. La stessa coerenza e stata applicata anche agli endpoint ranking legacy/evento che gia espongono offset.
- rifinita la semantica visuale dei record `AA` in `Rankings` e nelle `Classifiche evento`: il `Final Score` resta sempre il punteggio principale mostrato subito dopo atleta e nazionalita, anche quando l'ordinamento della graduatoria e basato su `D Score`, `E Score`, `Penalty` o `Bonus`. Il `D Score AA`, inteso come somma dei D Score degli attrezzi, viene mostrato in formato piu piccolo sotto al Final Score. Questa scelta evita di confondere il punteggio complessivo ufficiale AA con la metrica analitica usata per ordinare o interpretare la vista.
- sempre nei record `AA`, ogni cella attrezzo della griglia puo ora mostrare al passaggio del mouse un dettaglio compatto a srotolo con `D Score`, `E Score` stimato/registrato ed eventuali valori `P` e `B` quando rilevanti o non disponibili. La graduatoria resta quindi leggera in lettura, ma permette all'utente di ispezionare la composizione tecnica dei singoli attrezzi senza aprire una nuova vista.
- rifinita la resa del calendario interattivo nella sezione `Events`: le linee verticali della griglia settimanale non sono piu disegnate con due sistemi separati tra riquadri dei giorni e area delle barre evento. Ora una singola maschera visiva attraversa tutta la settimana, evitando sfalsamenti progressivi verso destra dovuti ad arrotondamenti sub-pixel del browser.
- riallineata la visualizzazione dei record nella sezione `Events` alla sezione `Athletes`: in modalita lista, gli eventi vengono ora mostrati come card in griglia a tre colonne su desktop, due su tablet e una su mobile. Anche la vista degli eventi preferiti riusa la stessa struttura, mantenendo coerenza tra ricerca, filtri e preferenze utente.
- rifinita la distanza verticale nella `Scheda Evento` sotto il box riepilogo `CLASSIFICA` e prima della graduatoria: e stato rimosso il margine extra che rendeva questo passaggio piu ampio rispetto allo spazio equivalente sotto il box `RANKING` nella sezione `Rankings`. Lo spazio tra sticky menu e box `CLASSIFICA` e stato invece mantenuto come prima.
- alleggerite le card della sezione `Events`: la data non viene piu mostrata come badge blu, per evitare che sembri un filtro o uno stato della gara. Il periodo dell'evento viene ora visualizzato in piccolo e in grigio accanto al nome evento, mentre i badge restano dedicati a disciplina, categoria, level ed eventuale stato `calendar only`.
- riallineata la spaziatura della sezione `Rankings` a quella della `Scheda Evento`: il passaggio tra menu filtri, box riepilogo `RANKING` e lista dei record usa ora le stesse distanze visuali del passaggio tra menu classifiche, box `CLASSIFICA` e graduatoria evento.
- resa coerente anche la linea di separazione tra menu filtri e box riepilogo nella sezione `Rankings`: e stata rimossa la linea full-width generata dallo sfondo dello sticky menu, lasciando solo il bordo leggero del blocco come nella `Scheda Evento`.
- ripuliti i separatori sticky in `Athletes`, `Events` e nella `Scheda Atleta`: sono stati rimossi i bordi locali sovrapposti ai separatori full-width, lasciando una sola linea leggera continua tra menu/controlli e contenuto sottostante.
- corretta la paginazione visuale della sezione `Events`: il backend puo restituire record grezzi che, dopo normalizzazione calendario/deduplica, producono un numero di card non multiplo di tre. Dopo review UX sono stati eliminati gli slot invisibili: la lista visibile ora viene semplicemente fermata al multiplo di tre precedente quando comparirebbe una card eccedente, mantenendo la griglia a tre colonne pulita e coerente con la sezione `Athletes`. La stessa logica evita anche un pulsante `Load more Events` finale quando resterebbero solo 1 o 2 card residue non mostrabili come riga completa; il cache-buster frontend e stato aggiornato per impedire alla preview di mantenere la vecchia logica in memoria.
- rifinita la visualizzazione delle graduatorie `AA` in `Classifica` evento e `Ranking`: il `D Score AA` non viene piu mostrato come chip secondario fisso sotto al `Final Score`, perche appesantiva la lettura della riga. Resta disponibile come dettaglio tecnico in un popup a srotolo sul punteggio principale AA, coerente con il popup gia usato sulle celle attrezzo della composizione AA.
- rifinita la gestione degli strumenti admin nelle Schede Atleta ed Evento: per utenti `admin` e `super_admin`, i pannelli di modifica non vengono piu visualizzati automaticamente sotto la scheda. Accanto alla stellina dei preferiti compare un pulsante strumenti con icona, coerente con lo stile dei bottoni scheda; cliccandolo si apre il pannello admin relativo a quella specifica entita, mantenendo la vista pubblica piu pulita per consultazione e analisi.
- bilanciata la riga delle graduatorie `CLASSIFICA` e `RANKING`: la colonna atleta e stata leggermente ridotta e la colonna del punteggio principale e stata allargata e resa piu leggibile. In questo modo il `Final Score` occupa meglio lo spazio disponibile tra nome atleta e dettagli tecnici, riducendo il vuoto visivo senza modificare l'organizzazione tabellare dei record.
- rifinito il popup del `D Score AA`: il dettaglio a srotolo sul punteggio principale AA e stato ristretto, mantenendo comunque label e valore su una sola riga per preservare leggibilita e compattezza.
- riallineato il popup del `D Score AA` al centro del blocco `Final Score`, cosi il dettaglio tecnico appare visivamente connesso al punteggio principale AA e non al bordo della colonna.
- corretta la semantica della metrica principale nei record `AA` di `CLASSIFICA` e `RANKING`: quando l'utente passa da `Final Score` a `D Score`, `E Score`, `Penalty` o `Bonus`, anche le righe AA mostrano come valore principale la metrica selezionata, esattamente come per i singoli attrezzi. In questi casi il `Final Score` non viene piu mostrato come chip fisso ma come popup tecnico sul valore principale, mentre il popup `D Score AA` rimane riservato alla vista `Final Score`.
- estesa la stessa coerenza alle celle attrezzo delle graduatorie `AA`: se l'utente seleziona `D Score`, `E Score`, `Penalty` o `Bonus`, anche i box dei singoli attrezzi (`FX`, `PH`, `SR`, ecc.) mostrano la metrica selezionata invece del Final Score dell'attrezzo. Il popup della cella conserva le altre componenti utili, evitando duplicazioni; quando il popup primario mostra `Final Score`, il testo resta su una sola riga senza ellissi.
- allargato leggermente il popup dei punteggi delle celle attrezzo nei record `AA`, per evitare che dettagli come `Final Score` vengano troncati con ellissi quando la graduatoria e filtrata per `D Score`, `E Score`, `Penalty` o `Bonus`. La modifica resta limitata ai popup tecnici delle celle e non altera la compattezza della graduatoria.
- centrato il popup tecnico delle celle attrezzo `AA` rispetto al box del punteggio dell'apparatus, usando lo stesso principio gia adottato per il popup principale del punteggio AA. In questo modo il dettaglio a srotolo appare visivamente collegato al valore su cui l'utente passa con il mouse.
- uniformata la visualizzazione dei record `VT AVG` alla logica di composizione gia adottata per i record `AA`: le celle `VT 1` e `VT 2` mostrano ora solo il `Final Score` del singolo salto, mentre `D Score`, `E Score`, `Penalty` e `Bonus` sono disponibili nel popup tecnico della cella. Questa scelta alleggerisce la graduatoria e mantiene la distinzione tra valore principale e componenti del punteggio.
- consolidata la posizione degli avvisi tecnici nella sezione `Rankings`, compreso il caso `VT AVG`: i box warning vengono ora mostrati realmente a fondo pagina, dopo l'eventuale pulsante `Load more Scores`. Gli avvisi generali restituiti dal backend vengono inoltre conservati e deduplicati durante la paginazione progressiva, mentre i warning dei singoli risultati continuano a essere ricavati dall'intero insieme di record gia caricato. In questo modo gli avvisi relativi a ordine incerto di `VT 1/VT 2`, stime e componenti non disponibili non scompaiono caricando altri punteggi.
- milestone Git del 17 settembre 2026: risolto il blocco locale di Git causato dalla licenza Xcode non ancora accettata, rieseguito l'audit pre-pubblicazione e verificata l'assenza dal commit di database locali, file `.env`, upload, cache o segreti di produzione. Dopo il superamento di 135 test, controllo della sintassi JavaScript, compilazione Python e verifica Alembic alla migration `0036`, tutto il lavoro accumulato dal precedente checkpoint del 23 luglio e stato consolidato nel commit `9737307` (`Complete public MVP data and analytics milestone`) e pubblicato sul ramo `main` della repository GitHub. Il commit comprende backend, frontend pubblico, analytics, schede atleta/evento, ranking e classifiche, migrazioni, audit e repair dei dati, report di governance e documentazione di tesi.
- standardizzata la precisione visuale del `D Score` in tutta la UI: ogni valore D viene mostrato con una sola cifra decimale (`5.3` invece di `5.300`) in ranking, classifiche evento, composizioni AA, dettagli VT AVG, popup tecnici, tooltip e riepiloghi analytics della Scheda Atleta. La modifica riguarda esclusivamente il formato di presentazione e non altera la precisione dei valori memorizzati nel database o restituiti dalle API.
- sostituita l'interazione hover dei popup tecnici nelle graduatorie `RANKING` e `CLASSIFICA` per i record `AA` e `VT AVG`: cliccando una riga, il record si espande verticalmente e mostra inline i dettagli prima nascosti del punteggio AA, di tutti gli attrezzi oppure di `VT 1` e `VT 2`; un secondo clic richiude la riga. Il comportamento e disponibile anche da tastiera con `Invio` o `Spazio`, mentre il nome dell'atleta resta un collegamento autonomo alla Scheda Atleta. I record di singolo attrezzo conservano invece la visualizzazione compatta ordinaria.
- compattati i dettagli espansi di `AA` e `VT AVG`: quando `Penalty` e `Bonus` risultano entrambi non disponibili per uno stesso attrezzo o salto, vengono sintetizzati in un'unica riga `P / B - Not available`, evitando un'espansione verticale eccessiva. Se almeno uno dei due campi contiene un valore reale, i dettagli restano separati per preservare l'informazione.
- resa contestuale la navigazione verso la Scheda Atleta dai record di graduatoria: se l'atleta viene aperto dalla sezione `RANKING`, il pulsante in alto mostra `Torna al Ranking` e riporta alla vista con i filtri mantenuti; se viene aperto da una `CLASSIFICA` della Scheda Evento, mostra `Torna alla Classifica` e riporta allo stesso evento preservando la classificazione selezionata nello stato della sessione. Negli altri percorsi resta `Torna agli Atleti`. Le etichette sono state localizzate in inglese, italiano, spagnolo e francese.
- verificata e corretta la coerenza grafica dello switch metrica nelle analytics della Scheda Atleta. L'asse temporale del trend viene ora mantenuto sul periodo scelto indipendentemente dalla disponibilita puntuale di `Final Score`, `D Score` o `E Score`, evitando riscalature orizzontali prive di significato. Le curve vengono spezzate quando una componente non e disponibile in una data intermedia, invece di collegare artificialmente punti lontani. Per le metriche score correlate, il dominio verticale deriva dallo stesso insieme numerico e non dalla metrica attualmente evidenziata: una curva conserva quindi la propria geometria quando passa da secondaria a principale e cambia solo enfasi/colore. La legenda primaria esplicita ora sia gli attrezzi sia la metrica attiva. Il diagramma poligonale continua invece correttamente a cambiare forma tra metriche, perche rappresenta valori e scale sportive differenti.
- corretta la sezione attiva quando una Scheda Atleta viene aperta da una graduatoria: provenendo da `Rankings`, la topbar mantiene attiva la sezione `Rankings`; provenendo da una `Classifica` evento, mantiene attiva la sezione `Eventi`. Queste aperture contestuali non sovrascrivono piu la memoria della sezione `Atleti`, che conserva la propria lista, ricerca e filtri precedenti. Una Scheda Atleta aperta direttamente dalla sezione Atleti continua invece ad appartenere normalmente a quella sezione e a essere ricordata secondo il comportamento di navigazione gia stabilito.
- completata la navigazione contestuale delle Schede Atleta: mentre una scheda e aperta da `Rankings` o da una `Classifica` evento, la voce `Atleti` della topbar punta esplicitamente alla lista generale `#/athletes`. Il collegamento rimane quindi sempre utilizzabile anche se una precedente sessione aveva memorizzato una Scheda Atleta, mentre le sezioni `Rankings` ed `Eventi` continuano a conservare la vista e i filtri di provenienza.
- estesa la memoria di navigazione alle Schede Atleta contestuali: una Scheda Atleta aperta da `Rankings` diventa la schermata corrente della sezione `Rankings`, mentre una scheda aperta da una Classifica diventa la schermata corrente di `Eventi`. Dopo il passaggio temporaneo a un'altra sezione, tornando alla sezione di origine viene quindi ripristinata la stessa Scheda Atleta. La graduatoria di provenienza viene memorizzata separatamente nel parametro contestuale `return_to`, cosi i pulsanti `Torna al Ranking` e `Torna alla Classifica` continuano a riportare alla lista originaria senza creare cicli di navigazione; la voce `Atleti` resta sempre disponibile per aprire la lista generale.
- uniformato lo stesso comportamento alla sezione `Atleti`: aprendo una Scheda Atleta dalle card della lista, la scheda diventa la schermata corrente di `Atleti` e viene ripristinata tornando nella sezione dopo una navigazione temporanea altrove. Il pulsante `Torna agli Atleti` conserva separatamente la rotta della lista di provenienza, compresi gli eventuali parametri di ricerca, anziche azzerare sempre la vista alla lista generale.
- consolidato il ripristino delle schermate tramite risoluzione dinamica dei link di sezione nella topbar. Al clic su `Atleti`, `Eventi`, `Rankings` o `Analytics`, la destinazione viene ora ricalcolata dalla memoria di sessione in quello stesso istante, evitando che un collegamento rimasto obsoleto dopo un caricamento asincrono riporti alla pagina iniziale della sezione. In particolare, una Scheda Atleta aperta direttamente dalla lista Atleti viene ripristinata in modo affidabile dopo il passaggio a un'altra sezione.
- sviluppata la prima Sezione `Analytics` operativa, dedicata al confronto diretto di due atleti. L'utente puo cercare i due ginnasti per cognome, nome o Leverage ID tramite suggerimenti dinamici; dopo la prima selezione, i suggerimenti vengono limitati automaticamente alla stessa disciplina e lo stesso atleta non puo essere scelto due volte. Il vincolo `MAG con MAG` oppure `WAG con WAG` e applicato sia nella UI sia dall'endpoint backend `/analytics/athletes/compare`, che rifiuta confronti misti con risposta `422`.
- il confronto Analytics riutilizza la semantica consolidata della Scheda Atleta: selezione esclusiva di `AA` e `VT AVG`, selezione multipla degli altri attrezzi, metriche `Final Score`, `D Score`, `E Score`, `Penalty` e `Bonus`, vista temporale `Periodo` o `Istante`, timeline a due cursori e delimitazione dei cicli olimpici. Tutte le modifiche aggiornano contemporaneamente entrambi gli atleti e il periodo iniziale viene impostato sull'ultimo ciclo olimpico disponibile nell'unione dei rispettivi risultati.
- introdotte due modalita visuali per il confronto: `Affiancati`, con radar e trend separati ma dotati della stessa scala numerica e dello stesso dominio temporale; `Sovrapposti`, con entrambi gli atleti nello stesso diagramma poligonale e nello stesso trend. Colori persistenti, legenda e tooltip permettono di distinguere i ginnasti. Le scale condivise evitano confronti grafici ingannevoli dovuti ad autoscaling differente. La sezione include inoltre statistiche riepilogative separate, avvisi qualita dato localizzati e layout responsive.
- corretta l'animazione dei controlli slider nella Sezione Analytics: metriche, vista `Periodo/Istante` e layout `Affiancati/Sovrapposti` non ricreano piu l'intero sticky menu a ogni clic. I controlli restano persistenti nel DOM, aggiornano `aria-checked` e indice del thumb in tempo reale e animano quindi lo scorrimento blu in modo coerente con la Scheda Atleta; vengono ridisegnati soltanto i grafici e i riepiloghi interessati.
- uniformate le due ricerche atleta della Sezione Analytics alle barre consolidate delle sezioni Atleti ed Eventi: stessi bordi, altezza, tipografia, focus, pulsante di cancellazione e pannello suggerimenti. La ricerca reagisce dal primo carattere, supporta selezione con clic o Invio e chiusura con `Esc`; le richieste dei due campi sono ora indipendenti, evitando che la digitazione in una barra interrompa i suggerimenti dell'altra, mentre resta attivo il vincolo automatico della stessa disciplina.
- raffinato il flusso di selezione della Sezione Analytics sostituendo i due campi paralleli con una sola barra di ricerca progressiva. Il primo atleta selezionato viene aggiunto all'area di confronto e le sue analytics diventano immediatamente consultabili; la stessa barra consente poi di cercare un secondo atleta, limitando automaticamente i suggerimenti alla disciplina `MAG` o `WAG` del primo. Al secondo inserimento i grafici vengono affiancati e diventa disponibile anche la modalita sovrapposta. Gli atleti selezionati restano visibili in due schede compatte e rimovibili; raggiunto il limite di due, la barra comunica che occorre rimuoverne uno prima di una nuova scelta.
- prodotto il documento di sintesi `docs/LEVERAGE_overview_completa_progetto.md`, pensato come panoramica estesa per lavoro accademico/tesi. Il documento descrive cosa e LEVERAGE, il suo posizionamento di mercato, il valore innovativo, l'architettura, le entita, gli import, la data governance, i motori World Gymnastics, la UI, le analytics, lo stato quantitativo del DB locale e i prossimi passi verso MVP online.

## 21. Conclusione

LEVERAGE oggi non e piu solo un backend CRUD: e diventato un sistema dati strutturato per ginnastica artistica, con modello semantico forte, import assistito, validazioni sportive, gestione qualita dato, preferenze utente, notifiche, analytics, strumenti admin e una base storica consistente.

La fase di trasformazione del backend in piattaforma web utilizzabile e ora iniziata con una prima UI pubblica minimal. I prossimi sviluppi dovranno consolidare frontend pubblico, area utente, area admin, calendario interattivo, schede atleta, schede evento, grafici, deploy online e gestione produzione.
