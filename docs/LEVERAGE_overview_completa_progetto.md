# LEVERAGE - Panoramica completa del progetto

Documento aggiornato al 15 settembre 2026.

## 1. Executive summary

LEVERAGE e una piattaforma web e backend API per la ginnastica artistica maschile e femminile, progettata per raccogliere, normalizzare, validare, consultare e analizzare risultati elite internazionali e nazionali.

Il progetto nasce da una necessita molto precisa: trasformare dati storici dispersi in file, classifiche, archivi e fonti eterogenee in un sistema strutturato, interrogabile e confrontabile. In LEVERAGE, atleti, eventi e risultati non sono semplici record isolati, ma parti di un modello dati coerente con la logica sportiva della ginnastica artistica:

- distinzione tra MAG e WAG;
- distinzione tra Junior e Senior;
- classificazione degli eventi per livello;
- gestione di round, format, apparatus, AA, VT AVG, VT attempt e Mixed Team;
- tracciamento della qualita del dato;
- separazione tra classifiche ufficiali di un evento e ranking analitici costruiti dall'utente;
- controllo umano admin prima della pubblicazione o modifica dei dati.

Dal punto di vista di prodotto, LEVERAGE si colloca tra tre mondi oggi separati:

- archivi ufficiali federali, molto autorevoli ma spesso poco orientati ad analisi comparative;
- siti e database informativi sulla ginnastica, ricchi di dati ma non sempre modellati come piattaforme analytics;
- strumenti di live scoring o gestione gara, utili durante l'evento ma non pensati come archivio storico analitico globale.

L'idea innovativa di LEVERAGE e proprio questa: non limitarsi a mostrare risultati, ma rendere i risultati ginnici confrontabili, filtrabili, contestualizzati e metodologicamente trasparenti.

## 2. Che cos'e LEVERAGE

LEVERAGE e una piattaforma di Artistic Gymnastics Analytics.

In termini pratici, e un sistema che permette a visitatori, utenti registrati, admin e super admin di:

- consultare atleti;
- consultare eventi;
- consultare classifiche ufficiali associate a un evento;
- creare ranking personalizzati;
- filtrare e confrontare performance nel tempo;
- osservare trend, profili attrezzo e distribuzioni statistiche;
- salvare preferenze personali;
- inserire e correggere dati con strumenti admin;
- importare dataset storici da file Gymternet;
- mantenere il dataset sotto controllo tramite audit, review e soft delete.

LEVERAGE non nasce come semplice sito editoriale e non nasce come pagina statica di risultati. La sua natura principale e quella di piattaforma dati: un database relazionale, un backend API, un sistema di regole semantiche e una UI pubblica che rendono leggibile il dato a utenti non tecnici.

## 3. Problema affrontato

La ginnastica artistica produce un volume enorme di dati:

- risultati per atleta;
- risultati per attrezzo;
- risultati all-around;
- qualifiche;
- finali;
- finali di specialita;
- team final;
- mixed team;
- categorie Junior e Senior;
- discipline MAG e WAG;
- differenze tra cicli olimpici;
- variazioni regolamentari sui punteggi;
- bonus, penalita e componenti tecniche non sempre pubblicate.

Questi dati sono spesso disponibili, ma raramente sono:

- centralizzati;
- normalizzati;
- comparabili;
- consultabili con filtri avanzati;
- accompagnati da avvisi metodologici;
- riconciliati con calendari e date;
- collegati a profili atleta;
- salvabili in configurazioni personali;
- controllati tramite workflow admin strutturato.

Il problema non e soltanto "avere i dati". Il problema e trasformare dati grezzi e fonti storiche in informazione sportiva affidabile, interrogabile e utile.

LEVERAGE risponde a questo problema costruendo una catena completa:

1. acquisizione del dato;
2. normalizzazione;
3. validazione;
4. controllo umano;
5. salvataggio strutturato;
6. esposizione tramite API;
7. visualizzazione tramite UI;
8. analisi e confronto;
9. tracciabilita delle modifiche.

## 4. Posizionamento nel mercato

### 4.1 Fonti ufficiali federali

Le fonti ufficiali, come World Gymnastics, sono centrali per l'autorevolezza del dato. Offrono pagine atleta, calendari, eventi e risultati ufficiali. Sono indispensabili come riferimento, ma il loro obiettivo principale e istituzionale: pubblicare informazioni ufficiali, non necessariamente costruire un ambiente di analisi flessibile per esplorare trend, ranking personalizzati, filtri multi-dimensione e confronti storici.

LEVERAGE non sostituisce queste fonti. Le usa come riferimento di verifica e come fonte ufficiale da collegare alle schede atleta/evento. Il principio progettuale e: dato pubblico e approvato da admin; suggerimento automatico solo come supporto, mai come pubblicazione autonoma.

### 4.2 Archivi e siti specializzati

The Gymternet e una fonte preziosa per risultati, top scores e raccolte storiche. Nel progetto LEVERAGE, i file Gymternet 2018-2026 sono stati usati come sorgente per il popolamento massivo iniziale, previa normalizzazione, revisione e import controllato.

La differenza e che LEVERAGE non vuole essere soltanto un archivio leggibile. Vuole trasformare quelle informazioni in un database applicativo, con relazioni tra entita, regole di coerenza, warning di qualita, endpoint API e visualizzazioni interattive.

### 4.3 Live scoring e piattaforme gara

Esistono strumenti che gestiscono risultati durante competizioni o pubblicano punteggi live. Questi sistemi sono utili per il momento gara, ma spesso non sono pensati come piattaforme di analisi storica globale. LEVERAGE invece ragiona sul lungo periodo: cicli olimpici, progressione atleta, confronti fra nazioni, andamento per apparatus, differenze tra MAG e WAG e ranking storici.

### 4.4 Spazio di mercato di LEVERAGE

LEVERAGE si colloca come piattaforma analytics verticale per la ginnastica artistica.

Il suo spazio e quello di uno strumento utile a:

- appassionati evoluti;
- tecnici;
- analisti;
- giornalisti sportivi;
- federazioni;
- società sportive;
- ricercatori;
- studenti;
- utenti che vogliono esplorare dati ginnici senza dover manipolare file manualmente.

In una prospettiva futura, LEVERAGE potrebbe diventare:

- un portale pubblico di consultazione;
- una dashboard tecnica;
- un archivio storico validato;
- uno strumento di scouting e benchmark;
- una piattaforma di confronto tra atleti e nazioni;
- una base dati per ricerca accademica e sport analytics.

## 5. Perche e un'idea innovativa

L'innovazione di LEVERAGE non sta in un singolo grafico o in una singola API. Sta nell'insieme coerente di prodotto, modello dati, workflow e metodologia.

### 5.1 Dato sportivo strutturato

Molti archivi mostrano tabelle. LEVERAGE costruisce un modello semantico:

- Athlete;
- Event;
- Result;
- EventCalendarEntry;
- AthleteCountryChange;
- preferenze utente;
- notifiche;
- audit log;
- suggerimenti admin;
- viste ranking salvate.

Questo consente di interrogare il dato in modo sportivamente sensato.

### 5.2 Separazione tra classifica e ranking

Una scelta fondamentale e distinguere:

- `Classifica`: graduatoria ufficiale di un evento, con round, format, discipline, category e apparatus gia determinati dai risultati caricati;
- `Ranking`: graduatoria analitica costruita dall'utente attraverso filtri, metriche e periodo.

Questa distinzione evita confusione semantica. Una classifica evento e un documento sportivo ufficiale; un ranking LEVERAGE e una vista analitica generata dalla piattaforma.

### 5.3 Consapevolezza dei cicli olimpici

La ginnastica cambia Codice dei Punteggi per cicli olimpici. Confrontare risultati di cicli diversi puo essere utile, ma deve essere segnalato.

LEVERAGE integra questa logica:

- ciclo 2017-2021;
- ciclo 2022-2024;
- ciclo 2025-2028;
- cicli futuri predisposti.

I ranking e le analytics atleta segnalano quando la selezione attraversa piu cicli, perche i punteggi possono riflettere Codici dei Punteggi diversi.

### 5.4 Data quality visibile all'utente

LEVERAGE non nasconde i limiti del dato. Quando un valore e stimato o non disponibile, lo segnala.

Esempi:

- E Score stimato da Final Score e D Score;
- Penalty non disponibile;
- Bonus non registrato in contesti in cui potrebbe esistere;
- vault attempt order uncertain;
- Final Score non disponibile in casi particolari;
- D Score mancante.

Questo rende la piattaforma metodologicamente piu onesta e piu utile.

### 5.5 Import assistito e controllato

Il tool di import non inserisce dati alla cieca. Produce preview, segnala conflitti, suggerisce match, salva report, crea notifiche e richiede decisioni admin nei casi ambigui.

Questo e un tratto distintivo: LEVERAGE non automatizza sacrificando la qualita; automatizza mantenendo il controllo umano.

### 5.6 Collegamento a fonti ufficiali

Il motore World Gymnastics non pubblica dati automaticamente. Aiuta l'admin a trovare profili ufficiali atleta/evento e a generare suggerimenti. La convalida resta sempre umana.

Questa architettura e pensata per ridurre tempo di data completion senza abbassare il livello di affidabilita.

### 5.7 UI minimal ma orientata all'analisi

La UI e stata costruita con logica Apple-like/minimal:

- topbar pulita;
- controlli app-style;
- slider coerenti;
- popup leggeri;
- ricerca live;
- sezioni pubbliche semplici;
- progressivo accesso alla complessita;
- grafici interattivi nelle schede atleta;
- classifiche e ranking in forma compatta.

L'obiettivo e rendere l'analisi avanzata accessibile senza trasformare la pagina in un pannello tecnico pesante.

## 6. Stack tecnologico

Il progetto usa:

- Python 3.10+;
- FastAPI come framework API;
- SQLAlchemy come ORM;
- SQLite in sviluppo locale;
- Alembic per migrazioni database;
- Pydantic per schemi e validazioni;
- JWT per autenticazione;
- Argon2 per hashing password;
- PyOTP per MFA admin/super admin;
- OpenPyXL per lettura file Excel;
- frontend statico HTML/CSS/JavaScript senza framework pesanti.

La scelta di un frontend statico e stata inizialmente pragmatica: evitare dipendenze Node/npm e costruire velocemente un MVP visuale controllabile. La struttura resta comunque compatibile con una futura migrazione a React/Vite o altro framework, preservando contratti API e direzione visiva.

## 7. Architettura generale

La struttura principale del repository include:

- `app/`: backend FastAPI;
- `app/models.py`: modelli SQLAlchemy;
- `app/schemas.py`: schemi Pydantic;
- `app/routers/`: router API per auth, atleti, eventi, risultati, analytics, preferenze, import, admin, search;
- `app/gymternet_import.py`: logica import Gymternet;
- `app/calendar_import.py`: logica import calendario;
- `app/world_gymnastics.py`: integrazione World Gymnastics;
- `app/result_ranking.py`: logica ranking risultati;
- `app/event_levels.py`: classificazione semantica degli eventi;
- `app/scoring_cycles.py`: cicli olimpici / Code of Points;
- `app/country_aliases.py`: alias paesi e nazioni;
- `migrations/versions/`: migrazioni Alembic;
- `frontend/`: UI MVP;
- `frontend/assets/`: logo e wordmark LEVERAGE;
- `docs/`: diario di bordo, capitoli metodologici, report di import;
- `docs/import_reports/`: CSV/JSON di review, audit, preview e commit;
- `scripts/`: strumenti operativi per import, calendar, repair, docx.

## 8. Entita principali del database

### 8.1 User

L'entita `User` rappresenta gli utenti registrati.

Campi principali:

- `id`;
- `email`;
- `password_hash`;
- token di verifica email;
- token reset password;
- `is_verified`;
- `failed_login_attempts`;
- `login_locked_until`;
- `auth_version`;
- `mfa_secret`;
- `mfa_enabled`;
- `mfa_recovery_codes`;
- `role`;
- `preferred_language`;
- `is_active`;
- `created_at`.

Ruoli:

- `user`;
- `admin`;
- `super_admin`.

Lingue supportate:

- inglese;
- italiano;
- spagnolo;
- francese.

### 8.2 Athlete

L'entita `Athlete` rappresenta il ginnasta.

Campi principali:

- `id`;
- `first_name`;
- `last_name`;
- `birth_year`;
- `country`;
- `discipline`;
- `image_url`;
- `is_profile_verified`;
- `world_gymnastics_athlete_id`;
- `world_gymnastics_profile_url`;
- `world_gymnastics_status`;
- `world_gymnastics_verified_at`;
- `world_gymnastics_verified_by_admin_id`;
- campi soft delete;
- `created_at`.

Valori discipline:

- `MAG`;
- `WAG`.

Scelte importanti:

- il vecchio `birth_date` e stato rimosso completamente e sostituito da `birth_year`;
- il vecchio campo status dell'atleta era stato eliminato, poi e stato reintrodotto solo come `world_gymnastics_status`, cioe informazione opzionale proveniente/verificata attraverso World Gymnastics;
- nella UI gli atleti sono mostrati come `Cognome Nome`;
- il DB mantiene separati `first_name` e `last_name`;
- il Result salva solo `athlete_id`, non copia nome e cognome.
- `is_profile_verified` mostra il badge pubblico blu LEVERAGE nella Scheda Atleta. La ricerca di candidati World Gymnastics non modifica il campo; l'assegnazione avviene automaticamente e con audit soltanto quando un Admin/Super Admin seleziona un profilo riscontrato e conferma `Importa dati`. Nella stessa transazione vengono registrati timestamp e Admin verificatore. Il normale endpoint di modifica anagrafica non puo alterarlo e la successiva approvazione dei singoli suggerimenti non ridefinisce i metadati della certificazione.
- `world_gymnastics_verified_by_admin_id` e un metadato riservato: non compare nelle risposte Athlete pubbliche e viene esposto soltanto nella vista amministrativa protetta della scheda.

### 8.3 AthleteCountryChange

Questa entita registra cambi di nazionalita.

Campi:

- `id`;
- `athlete_id`;
- `from_country`;
- `to_country`;
- `change_year`;
- `created_at`.

Scelta semantica:

- `Athlete.country` rappresenta la nazionalita corrente/canonica;
- `Result.represented_country` conserva la nazione rappresentata in quella specifica gara;
- in caso di cambio reale di nazionalita, non si correggono retroattivamente i result storici;
- in caso di errore di data entry, invece, la country sbagliata puo essere corretta nei result collegati.

### 8.4 Event

L'entita `Event` rappresenta una competizione.

Campi principali:

- `id`;
- `name`;
- `location`;
- `venue`;
- `start_date`;
- `end_date`;
- `year`;
- `discipline`;
- `category`;
- `level`;
- `image_url`;
- `world_gymnastics_event_id`;
- `world_gymnastics_event_url`;
- `world_gymnastics_status`;
- `world_gymnastics_verified_at`;
- `world_gymnastics_verified_by_admin_id`;
- campi soft delete;
- `created_at`.

Valori `discipline`:

- `MAG`;
- `WAG`;
- `MAG and WAG`.

Valori `category`:

- `junior`;
- `senior`;
- `junior and senior`.

Valori `level`:

- `Olympic Games`;
- `World Championships`;
- `Continental Championships`;
- `World Cup`;
- `World Challenge Cup`;
- `International Event`;
- `National Event`.

Scelta semantica:

- `MAG and WAG` non e un bottone separato in UI: un evento di quel tipo compare sia filtrando MAG sia filtrando WAG;
- `junior and senior` segue la stessa logica: compare sia filtrando Junior sia filtrando Senior;
- eventi futuri senza result possono esistere nel calendario;
- eventi `calendar only` possono comparire nel calendario anche senza scheda risultati collegata.

### 8.5 EventCalendarEntry

`EventCalendarEntry` serve a rappresentare il calendario, anche quando una riga calendar:

- non coincide perfettamente con un singolo Event;
- rappresenta un evento futuro;
- rappresenta una ricorrenza multi-data;
- ha date calendario ma non risultati importati.

Campi:

- `id`;
- `event_id`;
- `name`;
- `start_date`;
- `end_date`;
- `year`;
- `discipline`;
- `source`;
- `source_row`;
- `source_note`;
- campi soft delete;
- `created_at`.

Stati calendar esposti nella UI/API:

- `upcoming`;
- `ongoing`;
- `completed_no_results`;
- `completed_with_results`.

### 8.6 Result

L'entita `Result` e il cuore analitico del progetto. Il nome e stato mantenuto come `Result`, come richiesto, senza rinominarlo in performance.

Campi principali:

- `id`;
- `athlete_id`;
- `event_id`;
- `represented_country`;
- `discipline`;
- `category`;
- `apparatus`;
- `vt_attempt`;
- `day`;
- `format`;
- `round`;
- `D_score`;
- `E_score`;
- `Penalty`;
- `Bonus`;
- `score`;
- `rank`;
- `vault_attempt_order_uncertain`;
- campi soft delete;
- `created_at`.

Valori `discipline`:

- `MAG`;
- `WAG`.

Valori `category`:

- `junior`;
- `senior`.

Valori MAG apparatus:

- `AA`;
- `FX`;
- `PH`;
- `SR`;
- `VT`;
- `PB`;
- `HB`;
- `VT AVG`.

Valori WAG apparatus:

- `AA`;
- `VT`;
- `UB`;
- `BB`;
- `FX`;
- `VT AVG`.

Valori `format`:

- `team`;
- `individual`;
- `apparatus`;
- `mixed team`.

Valori `round`:

- `qualification`;
- `final`.

Regole chiave:

- `Result.discipline` deve essere uguale alla discipline dell'atleta;
- l'evento deve ammettere la discipline del result;
- il result ha una sola category, mai `junior and senior`;
- l'evento deve ammettere la category del result;
- `vt_attempt` ha senso solo per `VT`;
- `day` serve per gare distribuite su piu giornate;
- score non-AA sopra 20 viene trattato come sospetto/errore;
- D Score sopra 10 viene trattato come non valido;
- E Score deve essere tra 0 e 10.

## 9. Autenticazione e ruoli

Inizialmente LEVERAGE aveva un flusso OTP via email. Questo e stato poi sostituito con una modalita piu adatta a Internet:

- registrazione email/password;
- hashing password con Argon2;
- verifica email;
- login con JWT;
- reset password;
- cambio password;
- lock temporaneo dopo troppi tentativi falliti;
- `auth_version` per invalidare token dopo eventi sensibili;
- MFA per admin e super admin;
- ruoli persistenti nel DB.

Questa modifica ha risolto il problema bloccante di sicurezza legato alla precedente autenticazione passwordless non ancora adatta a esposizione pubblica.

### 9.1 Visitatore pubblico

Un visitatore non loggato puo:

- visualizzare home;
- cambiare lingua;
- cercare globalmente atleti, eventi e risultati;
- consultare atleti;
- consultare eventi;
- aprire schede atleta;
- aprire schede evento;
- visualizzare classifiche evento;
- usare ranking pubblici;
- usare filtri;
- consultare calendario;
- consultare analytics pubbliche disponibili.

Non puo:

- salvare preferiti;
- salvare ranking;
- modificare dati;
- accedere a pannelli admin.

### 9.2 User registrato

Un user registrato puo fare tutto cio che fa un visitatore, in piu:

- seguire atleti tramite stellina;
- salvare eventi preferiti;
- salvare configurazioni ranking;
- rinominare ranking salvati;
- eliminare ranking salvati;
- vedere area personale `My LEVERAGE`;
- ricevere notifiche nella lingua preferita.

### 9.3 Admin

Un admin puo:

- creare/modificare/eliminare atleti;
- creare/modificare/eliminare eventi;
- creare/modificare/eliminare result;
- caricare immagini atleta/evento;
- importare file Gymternet;
- importare calendar;
- usare data entry manuale;
- vedere preview import;
- vedere suggerimenti del sistema;
- approvare/rifiutare/modificare suggerimenti;
- collegare profili World Gymnastics;
- ricevere notifiche `import_summary`;
- ricevere reminder su entita da completare;
- ricevere reminder su eventi futuri da completare con risultati.

### 9.4 Super admin

Un super admin ha funzioni di governance:

- promuovere/declassare admin;
- controllare audit log;
- approvare modifiche admin;
- ripristinare snapshot precedenti;
- ripristinare entita soft-deleted;
- supervisionare rischi di manomissione dati.

## 10. Sicurezza dati e governance

LEVERAGE include protezioni importanti:

- admin-only write access;
- super-admin review;
- soft delete;
- audit log;
- snapshot before/after per modifiche;
- restore di Athlete, Event e Result;
- notifiche per promozione/declassamento;
- password hashing;
- MFA;
- blocco tentativi login;
- separazione tra dati pubblicati e suggerimenti non approvati.

Scelta metodologica centrale:

> LEVERAGE deve mostrare solo dati ufficiali o approvati da admin.

Il motore automatico puo aiutare, ma non deve mai diventare fonte autonoma di verita.

## 11. Import Gymternet

Il tool Gymternet e stato sviluppato per la popolazione massiva storica 2018-2026.

### 11.1 Obiettivo

Importare file Excel/CSV standardizzati contenenti risultati MAG e WAG, creando o aggiornando:

- Athlete;
- Event;
- Result;
- notifiche admin;
- report di qualita;
- file di review.

### 11.2 Flusso operativo

Il flusso usato per ogni anno e:

1. preview senza scrittura;
2. generazione report;
3. CSV per nuovi atleti con conflitti country;
4. CSV per possibili match con atleti gia esistenti;
5. review manuale admin;
6. applicazione decisioni;
7. preview post-decisione;
8. verifica duplicati/conflitti residui;
9. commit reale sul DB;
10. backup;
11. report finale;
12. aggiornamento diario;
13. commit Git.

### 11.3 Problemi gestiti

Il tool gestisce:

- nomi atleta simili;
- nome/cognome invertiti;
- refusi in nomi atleta;
- country diverse per stesso atleta;
- cambi di nazionalita;
- represented_country diverso dalla country corrente;
- nuovi atleti;
- nuovi eventi;
- duplicati result;
- result multipli nello stesso evento;
- day 1/day 2;
- suffissi evento Gymternet;
- Mixed Team;
- D-score orfani;
- final score senza D-score;
- D-score senza final score;
- VT AVG;
- VT SUM;
- dati non disponibili;
- warning metodologici.

### 11.4 Regole Gymternet storiche

Per i file Gymternet 2018-2024:

- E Score non e registrato;
- Penalty non e registrata;
- Bonus non esisteva nel regolamento e resta `NULL`;
- quando Final Score e D Score sono disponibili, LEVERAGE stima l'esecuzione come `score - D_score`;
- result con solo D Score e senza Final Score non vengono importati nel DB;
- D-score orfani vengono salvati in CSV per futura utilita;
- VT attempt 2 puo essere ricostruito da VT AVG e VT SUM, con warning di incertezza sull'ordine.

Per Gymternet 2025 e successivi, se si usa ancora il tool legacy:

- valgono le stesse regole Gymternet del 2025;
- E/P/B non sono registrati nei file;
- Bonus puo esistere nel regolamento ma non essere disponibile;
- per MAG, VT attempt 2 viene ricostruito da VT AVG e VT SUM;
- per WAG, VT attempt 2 final score resta non disponibile per possibile bonus 0.2 sul VT AVG;
- viene mantenuto warning specifico;
- il percorso consigliato futuro resta un importer standard 2026+ con componenti esplicite.

### 11.5 Regole Bonus

2018-2024:

- Bonus non previsto dal Codice dei Punteggi;
- si mantiene `NULL`, non `not available`.

Dal 2025:

- WAG: Bonus possibile solo su `VT AVG`, valore 0.2 in casi specifici;
- MAG: Bonus possibile solo su `FX`, `SR`, `VT`, `PB`, `HB`, valore 0.1;
- se il file Gymternet non lo registra ma il contesto lo ammette, la UI segnala dato non disponibile;
- se il bonus non e previsto/applicabile, resta `NULL`.

### 11.6 Vault

Il vault e stato uno dei punti piu delicati.

Regole emerse:

- nei file Gymternet storici, `VT` e considerato il salto singolo disponibile;
- `VT AVG` rappresenta media/valore aggregato su due salti;
- `VT SUM` non e salvato come apparatus nel DB, ma puo essere letto per ricavare D Score complessivi;
- per 2018-2024 si puo ricostruire VT attempt 2 da VT AVG/VT SUM;
- per 2025+ MAG si mantiene la stessa regola legacy;
- per 2025+ WAG il Final Score VT2 non e ricostruibile con certezza per il bonus 0.2;
- `vault_attempt_order_uncertain` segnala che VT1 e VT2 potrebbero essere invertiti.

UI warning:

> Vault 1 puo riferirsi a Vault 2 e viceversa.

## 12. Import standard 2026+ e import paralleli futuri

E stato definito un contratto comune di import in `docs/import_contract.md`.

Importer previsti:

- `manual_entry`;
- `gymternet_legacy`;
- `standard_2026_plus`;
- eventuali tool paralleli futuri.

Ogni importer deve convergere su:

- normalizzazione;
- validazione discipline/category;
- controllo athlete/event/result;
- deduplica;
- score formula;
- audit;
- preview admin;
- commit controllato.

Per import manuale e standard moderno:

- D Score obbligatorio;
- E Score obbligatorio;
- Final Score obbligatorio;
- Penalty vuota = 0;
- Bonus vuoto = 0;
- controllo `Final Score = D + E - Penalty + Bonus`;
- se il conto non torna, il result non viene importato e l'admin riceve report cumulativo.

## 13. Data entry manuale admin

Il backend e stato adattato a un data entry manuale semplice:

1. creazione evento;
2. inserimento dati evento;
3. selezione una volta sola di format e round;
4. inserimento dei result della classifica;
5. ricerca atleta assistita;
6. creazione atleta se non esiste;
7. notifica/admin reminder per completare atleta nuovo;
8. validazione finale punteggi.

L'admin non deve conoscere l'ID atleta. Il sistema offre suggerimenti durante la digitazione, riconoscendo:

- nome cognome;
- cognome nome;
- ID;
- country;
- nomi simili.

Nel `Result` viene salvato solo `athlete_id`, non una copia del nome.

## 14. Notifiche

Le notifiche sono state razionalizzate.

Notifiche user:

- nuovi result relativi ad atleta seguito, in forma cumulativa;
- promozione/declassamento ruolo;
- future notifiche preferenze/dashboard.

Notifiche admin:

- `import_summary`, unica e cumulativa;
- `data_entry_summary`;
- entita create da import da completare;
- atleti nuovi;
- eventi nuovi;
- eventi futuri svolti senza risultati;
- suggerimenti da review.

La notifica `import_summary` riassume:

- nuovi atleti;
- nuovi eventi;
- nuovi result;
- atleti con nuovi risultati;
- conflitti risolti;
- dati scartati;
- D-score orfani;
- warning generati.

## 15. Motori di suggerimento

### 15.1 DataSuggestion

Il sistema include una entita `DataSuggestion` per suggerimenti su campi mancanti.

Campi:

- entity type;
- entity id;
- field name;
- suggested value;
- confidence;
- source URL;
- evidence;
- status;
- reviewed value;
- admin creatore/revisore.

Stati:

- pending;
- accepted;
- rejected.

L'admin puo:

- accettare;
- rifiutare;
- modificare prima di accettare.

### 15.2 Motore AI/web nascosto

E stato predisposto un motore AI/web assistito, ma lasciato disattivato/config-gated.

Motivo:

- possibile utilita futura;
- nessun costo se non usato;
- nessuna chiamata esterna automatica;
- nessun dato pubblicato senza approvazione admin.

### 15.3 World Gymnastics Athlete

Il motore World Gymnastics Athlete:

- cerca profili atleta;
- propone candidati;
- confronta nome/country/discipline;
- propone `world_gymnastics_athlete_id`;
- propone link profilo ufficiale;
- propone status;
- genera warning se qualcosa non coincide;
- salva suggerimenti solo per review admin.

La scheda atleta puo mostrare il link ufficiale World Gymnastics solo quando verificato.

Il flusso comprende inoltre una certificazione controllata dell'identita: la sola ricerca di candidati non assegna alcun badge, mentre la selezione esplicita del profilo e il comando `Importa dati` impostano atomicamente `is_profile_verified`, data e Admin verificatore, registrano la decisione nell'audit e mostrano il badge pubblico blu LEVERAGE. I singoli valori proposti restano separatamente soggetti a review Admin e la loro approvazione non modifica i metadati del matching certificato. Razionale, limiti e implementazione sono descritti nel capitolo dedicato [LEVERAGE_monografia_certificazione_schede_atleta.md](LEVERAGE_monografia_certificazione_schede_atleta.md).

La manutenzione segue un invariante di sicurezza: i dati World Gymnastics sono separati dalla normale anagrafica e diventano modificabili in un blocco dedicato soltanto dopo il collegamento. Un Admin puo revocare il badge, ma non puo attribuirlo manualmente. Una variazione di FIG ID o URL revoca automaticamente la certificazione; per riattivarla e necessario selezionare nuovamente un profilo ufficiale e confermare `Importa dati`. Le operazioni che modificano certificazione o dati World Gymnastics sono auditabili e soggette alla governance Admin/Super Admin; ricerca e preview sono protette dai ruoli ma non producono log mutativi artificiali.

Una migrazione di riallineamento certifica anche i profili approvati prima dell'introduzione del badge, ma solo quando URL ufficiale, data di verifica e Admin verificatore risultano tutti gia registrati.

### 15.4 World Gymnastics Event

Il motore World Gymnastics Event e stato impostato in modo analogo:

- ricerca evento;
- collegamento a pagina ufficiale;
- suggerimenti su campi evento;
- status World Gymnastics;
- venue opzionale;
- verifica admin.

Il campo `image_url` Event e stato mantenuto opzionale per sviluppi futuri, ad esempio immagini standard per Olimpiadi o grandi eventi.

## 16. Search

LEVERAGE include ricerca globale e ricerche dedicate.

### 16.1 Ricerca globale

La ricerca globale deve restituire solo:

- Athletes;
- Events;
- Results.

Non deve mostrare output autonomi tipo:

- apparatus;
- country;
- migliaia di result generici.

Deve pero usare termini come country/apparatus per interpretare la query.

Esempi:

- `Stefano Patron, Serie A 2026, volteggio`;
- `Bundesliga 2025`;
- `World Cup Cottbus`;
- `Europei 2025`;
- `worlds`;
- `europeans`;
- `Italia`;
- `Italy`.

La ricerca e stata resa piu intelligente con:

- alias paese;
- alias eventi;
- matching ordine-insensibile;
- riconoscimento anni;
- riconoscimento apparatus;
- suggerimenti durante digitazione.

### 16.2 Ricerca Athlete

La sezione atleti:

- filtra live durante digitazione;
- accetta nome/cognome e cognome/nome;
- riconosce paesi estesi e codici;
- supporta filtri MAG/WAG;
- supporta Senior/Junior;
- supporta preferiti;
- permette ordinamento Nome/Nazione.

### 16.3 Ricerca Events

La sezione eventi:

- filtra live competizioni;
- riconosce alias;
- mostra eventi in lista o calendario;
- permette filtri MAG/WAG;
- Junior/Senior;
- Level;
- Periodo;
- Preferiti;
- Pulisci filtri.

### 16.4 Rankings

La sezione Rankings:

- costruisce ranking globali;
- non mescola MAG e WAG nello stesso ranking;
- distingue cicli olimpici;
- supporta metriche diverse;
- supporta periodo custom;
- supporta level;
- supporta category;
- supporta apparatus;
- supporta salvataggio configurazioni per utenti loggati.

## 17. Analytics

### 17.1 Ranking analytics

Ranking disponibili per:

- Final Score;
- D Score;
- E Score;
- Penalty;
- Bonus.

Filtri:

- discipline;
- category;
- level;
- apparatus;
- round;
- format;
- periodo;
- ciclo olimpico.

Regole:

- `Periodo` e `Ciclo olimpico` non possono essere attivi insieme;
- default ranking su ultimo ciclo olimpico;
- MAG/WAG non si mischiano;
- AA default se nessun apparatus e selezionato;
- AA e VT AVG sono mutuamente esclusivi con altri apparatus;
- se tutti gli apparatus vengono deselezionati, AA torna attivo.

### 17.2 Scheda atleta analytics

La scheda atleta include:

- identity box;
- link World Gymnastics;
- analytics;
- diagramma poligonale;
- trend;
- statistiche riepilogative;
- warning metodologici.

Per MAG:

- esagono a sei vertici;
- ordine vertici: FX, PH, SR, VT, PB, HB.

Per WAG:

- rombo a quattro vertici;
- ordine vertici: VT, UB, BB, FX.

Metriche:

- Final Score;
- D Score;
- E Score;
- Penalty;
- Bonus.

Apparatus:

- AA;
- apparati discipline-specific;
- VT AVG.

Timeline:

- Periodo;
- Istante;
- doppio cursore per periodo;
- cursore singolo per istante;
- marker cicli olimpici;
- tooltip su trend con valore, periodo/data, gara.

Scelte metodologiche:

- nelle statistiche totali non si include AA, per non duplicare punteggi gia composti da attrezzi;
- gli eventi multigiorno sono posizionati temporalmente sull'inizio evento ma il tooltip mostra periodo completo;
- non si inventano date di qualifica/finale non presenti nelle fonti;
- E stimata e chiaramente segnalata.

### 17.3 Age analytics

Il backend e stato predisposto anche per:

- eta atleta in gara;
- eta media per country;
- analisi per competizione;
- confronti tra nazioni.

La sostituzione `birth_date -> birth_year` rende l'eta una stima annuale, piu coerente con dati storici incompleti.

## 18. Frontend MVP

Il frontend e stato costruito come prototipo statico minimal.

### 18.1 Branding

Sono stati integrati:

- logo LEVERAGE;
- logo trasparente;
- wordmark LEVERAGE;
- colore blu Maserati come colore riconoscitivo.

La home mostra:

- splash logo iniziale;
- dissolvenza;
- comparsa wordmark;
- topbar;
- subtitle `Artistic Gymnastics Analytics`.

### 18.2 Stile UI

Principi UI:

- pulito;
- moderno;
- minimale;
- app-like;
- bordi arrotondati coerenti;
- no pillole eccessive;
- controlli coerenti;
- filtri sticky;
- popup non trasparenti;
- animazioni morbide;
- nessun elemento tecnico visibile all'utente finale.

### 18.3 Home

La home include:

- brand;
- ricerca globale;
- quattro card di accesso;
- niente preview calendario/ranking per non appesantire.

Card:

- Athletes;
- Events;
- Performance;
- Rankings.

### 18.4 Topbar

La topbar include:

- Home;
- Athletes;
- Events;
- Rankings;
- Analytics;
- lingua;
- Sign in / area utente.

E stato rimosso il popup hover superfluo della topbar.

L'indicatore della sezione corrente si muove dinamicamente.

### 18.5 Lingue

Lingue:

- EN default;
- IT;
- ES;
- FR.

Anche l'utente non loggato puo cambiare lingua.

L'utente loggato conserva la lingua preferita e riceve notifiche localizzate.

### 18.6 Area personale

Area user:

- atleti preferiti;
- eventi preferiti;
- ranking salvati;
- eliminazione ranking salvati;
- accesso rapido a configurazioni salvate.

Funzioni temporanee:

- demo user;
- demo admin;
- demo super admin.

Questi pulsanti sono solo per sviluppo frontend e devono essere rimossi prima del rilascio.

### 18.7 Scheda atleta

La scheda atleta e stata sviluppata come milestone importante.

Contiene:

- pulsante `Torna agli Atleti`;
- nome `Cognome Nome`;
- identity box compatto;
- solo campi disponibili;
- `Leverage ID`;
- country;
- discipline;
- category se disponibile;
- birth year se disponibile;
- World Gymnastics link se verificato;
- country history se disponibile;
- stellina preferiti per logged user;
- pulsante strumenti admin solo per admin/super admin;
- pannello admin nascosto finche non richiesto;
- analytics con grafici.

La scheda atleta e stata dichiarata milestone completata nella fase frontend.

### 18.8 Scheda evento

La scheda evento e stata sviluppata seguendo la stessa logica della scheda atleta.

Contiene:

- pulsante `Torna agli Eventi`;
- dettagli evento minimal;
- `Leverage ID`;
- nome;
- periodo;
- luogo;
- venue se disponibile;
- discipline;
- category;
- level;
- World Gymnastics link se verificato;
- stellina preferiti;
- pulsante strumenti admin;
- classifiche evento.

Scelta importante:

- nella scheda evento non si usano filtri liberi stile Rankings;
- si mostrano le classifiche ufficiali caricate;
- l'utente sceglie solo tra classifiche effettivamente disponibili o previste;
- le opzioni non disponibili restano visibili ma disabilitate.

Classifiche:

- raggruppate per discipline/category/round/format/apparatus/day;
- ordinate per Final Score o rank quando disponibile;
- metrica visualizzabile Final/D/E/P/B;
- righe compatte in forma graduatoria;
- AA con griglia attrezzi;
- tooltip su componenti.

### 18.9 Sezione Events

La sezione eventi include:

- ricerca live;
- card tre colonne;
- modalita lista/calendario;
- calendario interattivo;
- navigazione mese;
- tasto oggi;
- evidenza giorno corrente;
- eventi futuri;
- eventi calendar-only;
- filtri live;
- navigazione tra eventi della selezione corrente.

### 18.10 Sezione Rankings

La sezione ranking include:

- filtri sportivi;
- slider MAG/WAG;
- apparatus;
- metriche score;
- period/cycle;
- level;
- category;
- saved rankings;
- load more;
- avvisi metodologici;
- graduatoria compatta;
- AA table;
- VT AVG details.

### 18.11 Paginazione progressiva

Per non appesantire la UI:

- Athletes carica un primo blocco di record;
- Events carica card in multipli di tre;
- Rankings usa offset e load more;
- la numerazione ranking resta coerente tra pagine.

## 19. Popolamento massivo del database

Il DB locale e stato popolato con dati storici Gymternet.

### 19.1 Copertura

Risultati importati:

- 2018;
- 2019;
- 2020;
- 2021;
- 2022;
- 2023;
- 2024;
- 2025;
- 2026 primo semestre.

Calendario riconciliato:

- 2018;
- 2019;
- 2020;
- 2021;
- 2022;
- 2023;
- 2024;
- 2025;
- 2026, con parte futura materializzata.

### 19.2 Stato quantitativo locale

Alla data del controllo:

| Entita | Totale attivo |
|---|---:|
| Athlete | 27.919 |
| Event | 1.759 |
| Result | 819.739 |
| EventCalendarEntry | 308 |
| AuditLog | 1.567 |

Distribuzione Result:

| Discipline | Result |
|---|---:|
| WAG | 411.677 |
| MAG | 408.062 |

Distribuzione Category:

| Category | Result |
|---|---:|
| Senior | 449.504 |
| Junior | 370.235 |

Distribuzione Event level:

| Level | Event |
|---|---:|
| National Event | 976 |
| International Event | 647 |
| World Challenge Cup | 44 |
| World Cup | 40 |
| Continental Championships | 37 |
| World Championships | 10 |
| Olympic Games | 5 |

Risultati per anno:

| Anno | Result | Event con result |
|---:|---:|---:|
| 2018 | 89.988 | 211 |
| 2019 | 106.084 | 233 |
| 2020 | 34.326 | 77 |
| 2021 | 77.423 | 196 |
| 2022 | 97.075 | 215 |
| 2023 | 117.256 | 241 |
| 2024 | 107.046 | 207 |
| 2025 | 124.417 | 223 |
| 2026 | 66.124 | 114 |

Indicatori qualita:

| Indicatore | Valore |
|---|---:|
| Result senza Final Score | 4.787 |
| Result senza D Score | 220.133 |
| Execution estimate | 594.819 |
| Vault attempt uncertain | 164.342 |
| AA result | 92.196 |
| VT AVG result | 34.049 |

### 19.3 Report prodotti

Il progetto contiene oltre 300 file in `docs/import_reports`, inclusi:

- preview annuali;
- review atleti;
- decisioni match;
- D-score orfani;
- duplicati;
- report commit;
- audit calendario;
- riclassificazioni event level;
- repair score outliers;
- mixed team merge;
- calendar matching.

### 19.4 Capitoli metodologici prodotti

Sono stati prodotti documenti specifici:

- diario tecnico generale;
- diario popolamento massivo;
- metodologia popolamento DB;
- metodologia riconciliazione calendar/event;
- import contract;
- decision memory Gymternet;
- thesis request fields.

## 20. Regole semantiche e decisioni progettuali chiave

### 20.1 Mantenere `Result`

Il nome `Result` e stato mantenuto in tutto il progetto.

Motivo:

- coerenza con la richiesta;
- chiarezza sportiva;
- una performance puo essere concetto piu ampio, ma il DB registra risultati.

### 20.2 `birth_year` invece di `birth_date`

Si e scelto `birth_year` per:

- maggiore disponibilita storica;
- minore rischio privacy;
- maggiore coerenza con fonti incomplete;
- sufficienza per analytics eta annuale.

### 20.3 Event multi-discipline e multi-category

Un evento puo essere:

- MAG;
- WAG;
- MAG and WAG.

E puo essere:

- junior;
- senior;
- junior and senior.

La UI non mostra "MAG and WAG" come terzo pulsante: mostra MAG e WAG entrambi applicabili.

### 20.4 Result single-discipline e single-category

Un result e sempre specifico:

- una discipline;
- una category;
- un apparatus;
- un round;
- un format.

Questo evita ambiguita analitiche.

### 20.5 No mix MAG/WAG nei ranking globali

MAG e WAG non si mescolano in ranking globali perche:

- hanno attrezzi diversi;
- hanno regole diverse;
- anche gli attrezzi comuni possono avere scale e logiche diverse.

### 20.6 Classifiche evento non sono ranking liberi

La scheda evento mostra classifiche caricate, non ranking costruiti dall'utente.

Questa distinzione mantiene coerenza tra:

- ufficialita della classifica;
- flessibilita del ranking analytics.

### 20.7 AA e VT AVG mutuamente esclusivi

AA e VT AVG sono aggregati. Non devono essere selezionati insieme ad altri attrezzi.

Regola:

- se AA e attivo e clicco un attrezzo, AA si disattiva;
- se seleziono AA, gli altri attrezzi si disattivano;
- stesso per VT AVG;
- se tutto viene deselezionato, torna AA.

### 20.8 Dati incompleti non nascosti

Il sistema non inventa dati.

Se un dato manca:

- resta `NULL`;
- viene segnalato come non disponibile;
- puo essere escluso o filtrato;
- viene trattato con avvisi.

### 20.9 Admin validation

Nessun suggerimento automatico diventa dato pubblicato senza admin.

### 20.10 Git e tracciabilita

Il progetto e stato versionato su GitHub:

- repository `patronstefano/LEVERAGE`;
- tag intermedi;
- commit dopo fasi chiave;
- documentazione aggiornata.

## 21. Dashboard e site analytics

E stata implementata una versione iniziale leggera di analytics sito, admin-only.

Eventi tracciabili:

- page view;
- search;
- athlete view;
- event view;
- dashboard view;
- session end.

Metriche previste:

- visitatori;
- sessioni;
- tempo medio;
- atleti piu visualizzati;
- eventi piu visualizzati;
- ricerche piu frequenti;
- utenti registrati;
- utenti attivi/inattivi.

Scelta:

- versione leggera;
- nessun tracciamento invasivo;
- attenzione futura a privacy/cookie/legal.

## 22. Documentazione

La documentazione e uno dei punti forti del progetto.

Sono stati mantenuti:

- diario di bordo tecnico;
- diario popolamento massivo;
- capitoli metodologia;
- report CSV;
- report JSON;
- decision memory;
- import contract;
- README;
- documenti Word generati da Markdown.

Questo rende il progetto particolarmente adatto a una tesi magistrale, perche mostra:

- processo;
- decisioni;
- motivazioni;
- dati quantitativi;
- controllo qualita;
- iterazione prodotto;
- sviluppo tecnico;
- governance.

## 23. Stato attuale del progetto

LEVERAGE e oggi in una fase avanzata di MVP.

Completato o molto avanzato:

- backend dati;
- modello semantico;
- autenticazione;
- ruoli;
- import storico;
- popolamento 2018-2026 primo semestre;
- calendario;
- analytics backend;
- ricerca;
- preferenze;
- notifiche;
- audit;
- World Gymnastics assistant;
- frontend pubblico principale;
- scheda atleta;
- scheda evento;
- rankings;
- events calendar/list;
- documentazione.

Ancora da completare o rifinire:

- area admin completa in UI;
- area super admin completa in UI;
- data entry manuale UI completa;
- import Gymternet UI completa;
- review suggerimenti UI completa;
- dashboard personale user definitiva;
- site analytics admin UI definitiva;
- responsive QA;
- accessibilita;
- pulizia demo buttons;
- email provider reale;
- produzione PostgreSQL;
- deployment;
- privacy/cookie/legal;
- dominio e social;
- test end-to-end frontend;
- ultimo passaggio di polish UI.

Stima avanzamento:

- backend e dati: circa 90-95%;
- popolamento storico: circa 95%, in attesa di eventuale completamento 2026 fine anno;
- frontend pubblico: circa 70-75%;
- frontend admin/super admin: circa 35-45%;
- deploy produzione: non ancora completato;
- MVP online serio complessivo: circa 75-80%.

## 24. Perche LEVERAGE e rilevante per una tesi di ingegneria gestionale

LEVERAGE non e solo sviluppo software. E un caso completo di progettazione, gestione e valorizzazione di un sistema informativo sportivo.

Aspetti rilevanti:

- definizione del problema;
- analisi del mercato;
- progettazione del modello dati;
- data governance;
- gestione della qualita;
- processi di import;
- controllo umano su automazioni;
- tracciabilita;
- digitalizzazione di dataset storici;
- user experience;
- scalabilita;
- gestione ruoli;
- sicurezza;
- prodotto digitale;
- potenziale modello di business.

Il valore gestionale sta nella trasformazione di un processo manuale e frammentato in un workflow digitale controllato:

1. input dati;
2. validazione;
3. review;
4. pubblicazione;
5. consultazione;
6. analisi;
7. feedback;
8. miglioramento continuo.

## 25. Possibili modelli di sviluppo futuro

### 25.1 Prodotto pubblico free

Accesso libero a:

- atleti;
- eventi;
- risultati;
- ranking base;
- schede atleta.

### 25.2 Account user gratuito

Funzioni:

- preferiti;
- ranking salvati;
- dashboard personale;
- notifiche.

### 25.3 Funzioni premium future

Ipotesi:

- analytics avanzate;
- export;
- confronti multi-atleta;
- dashboard coach;
- dataset professionale;
- API access;
- alert personalizzati;
- report PDF.

### 25.4 Collaborazione dati

LEVERAGE puo continuare a collaborare con Gymternet o integrare futuri file standardizzati 2026+.

La piattaforma e gia predisposta per import paralleli, purche rispettino il contratto comune.

## 26. Fonti esterne consultate per il posizionamento

Fonti pubbliche consultate il 15 settembre 2026:

- World Gymnastics - homepage ed eventi: https://www.gymnastics.sport/
- World Gymnastics - athlete profiles: https://www.gymnastics.sport/site/athletes/wcg_view.php
- FIG athlete profile example: https://www.worldgymnastics.sport/site/athletes/bio_detail.php
- The Gymternet: https://thegymter.net/
- The Gymternet yearly archive / top score context: https://thegymter.net/2024/
- MeetScoresOnline example of live/event scoring context: https://meetscoresonline.com/

Queste fonti mostrano che esistono archivi ufficiali, pagine atleta, calendari, risultati e strumenti gara; LEVERAGE si differenzia per l'obiettivo di trasformare tali dati in un ambiente analitico integrato, filtrabile, confrontabile e governato da workflow admin.

## 27. Sintesi finale

LEVERAGE e un MVP avanzato di piattaforma mondiale per analytics di ginnastica artistica.

Il progetto ha gia superato la fase di semplice prototipo dati:

- possiede un database popolato;
- possiede regole sportive;
- possiede import controllato;
- possiede audit;
- possiede frontend pubblico;
- possiede schede atleta/evento;
- possiede ranking;
- possiede calendario;
- possiede documentazione metodologica.

La parte ancora da completare riguarda soprattutto la trasformazione definitiva in prodotto online:

- UI admin;
- UI super admin;
- completamento area personale;
- deploy;
- hardening produzione;
- legal/privacy;
- rimozione strumenti demo;
- test finale.

La direzione progettuale e solida: LEVERAGE non e soltanto un database di risultati, ma un sistema informativo verticale che organizza conoscenza sportiva, controlla qualita, rende visibili le incertezze e permette analisi che oggi richiederebbero lavoro manuale su fonti sparse.
