# LEVERAGE

Backend API per la gestione di utenti, athletes, events e risultati.

## Stack
- Python 3.10+
- FastAPI
- SQLAlchemy
- SQLite (MVP)
- JWT authentication

## Installazione

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Configura le variabili locali copiando `.env.example` in `.env`.

## Avvio

```bash
alembic upgrade head
uvicorn app.main:app --reload
```

## API principali
- `POST /auth/register`
  Registra un account con email e password; l'account resta non verificato finche l'utente non conferma il link email
- `POST /auth/verify-email`
  Conferma l'account tramite token inviato via email
- `POST /auth/resend-verification`
  Reinvia il link di verifica con rate limit
- `POST /auth/login`
  Login con email/password; per admin e super admin richiede MFA TOTP o recovery code
- `POST /auth/password/forgot`
- `POST /auth/password/reset`
- `POST /auth/password/change`
- `POST /auth/mfa/setup`
- `POST /auth/mfa/confirm`
- `GET /auth/me`
  Restituisce l'utente loggato, ruolo, lingua preferita e stato MFA
- `GET /admin/users`
  Endpoint admin-only per cercare utenti registrati per email, ruolo e stato
- `PUT /admin/users/{user_id}/role`
  Endpoint admin-only per cambiare ruolo a un utente tramite id
- `PUT /admin/users/role-by-email`
  Endpoint admin-only per promuovere o modificare ruolo a un utente tramite email registrata
- `GET /analytics/filter-options`
  Restituisce i valori realmente presenti nel database per costruire filtri globali della dashboard: anni, discipline, categorie, format, round, apparatus, country, livelli evento e metriche disponibili
- `GET /analytics/rankings`
  Ranking globale pubblico con filtri per evento, periodo, disciplina, category, apparatus, format, round, country, livello, qualita dato e metrica (`score`, `D_score`, `execution_estimate`, `E_score`, `Penalty`, `Bonus`)
- `GET /analytics/athletes/compare`
  Restituisce serie sovrapponibili per confrontare atleti su una metrica, con aggregazioni `raw`, `best_by_event`, `average_by_year`, `average_by_apparatus`
- `GET /analytics/athletes/{athlete_id}/apparatus-profile`
  Restituisce il profilo attrezzi per scheda atleta: `hexagon` MAG o `rhombus` WAG, vertici ordinati, metrica selezionata, criterio (`average`, `best`, `latest`) e valori normalizzati per disegnare il poligono
- `GET /analytics/athletes/{athlete_id}/profile-view`
  Restituisce una vista composita per scheda atleta: dati atleta, dashboard trend/statistiche, profilo attrezzi, metriche e qualità dato disponibili
- `GET /analytics/athletes/{athlete_id}/dashboard`
  Restituisce una scheda dashboard pronta per grafici: trend, riepilogo, breakdown per anno, breakdown per apparatus e risultati recenti
- `GET /analytics/age-by-country`
  Restituisce punti eta atleta-gara e media eta per country, usando `birth_year` dell'atleta e `year` dell'evento
- `POST /site-analytics/events`
  Endpoint pubblico leggero per registrare eventi d'uso privacy-friendly: page view, search, athlete view, event view, dashboard view e session end
- `GET /site-analytics/admin/summary`
  Endpoint admin-only per visualizzare statistiche aggregate del sito web
- `GET /athletes`
- `POST /athletes`
- `PUT /athletes/{athlete_id}`
  Se modifica `country` e include `country_change_year`, registra anche una riga in `country_changes`
- `DELETE /athletes/{athlete_id}`
- `POST /athletes/{athlete_id}/image`
- `POST /athletes/{athlete_id}/country-changes`
  Endpoint admin-only per registrare un cambio country con `to_country` e `change_year`
- `GET /athletes/{athlete_id}/admin-view`
  Endpoint admin-only: restituisce la scheda Athlete ufficiale e i suggerimenti pendenti visibili solo agli admin
- `POST /athletes/{source_athlete_id}/merge-preview`
  Endpoint admin-only per verificare se una scheda atleta duplicata puo essere unita a un atleta canonico indicato tramite `target_athlete_id`
- `POST /athletes/{source_athlete_id}/merge`
  Endpoint admin-only per fondere una scheda atleta duplicata nell'atleta canonico, con `confirm=true`, audit log e blocco se esistono conflitti Result
- `GET /athletes/suggestions`
- `GET /athletes/{athlete_id}/results`
- `GET /athletes/{athlete_id}/events/{event_id}/results`
- `GET /athletes/compare?ids=1,2,3`
- `GET /athletes/{athlete_id}/scores-over-time`
- `GET /athletes/compare/scores`
- `GET /athletes/{athlete_id}/stats`
- `GET /events`
- `POST /events`
- `PUT /events/{event_id}`
- `DELETE /events/{event_id}`
- `POST /events/{event_id}/image`
- `GET /events/{event_id}/admin-view`
  Endpoint admin-only: restituisce la scheda Event ufficiale e i suggerimenti pendenti visibili solo agli admin
- `GET /events/{event_id}/results`
  Supporta filtri per `format`, `round`, `discipline`, `category`, `apparatus`, `athlete`, `data_quality`
  `athlete` puo essere id, nome, cognome, `nome cognome` oppure `cognome nome`
  Supporta anche `sort_by` con `score`, `D_score`, `execution_estimate`, `E_score`, `Penalty`, `Bonus`
  La risposta costituisce la classifica dei result di quell'evento per i filtri selezionati
  Supporta `limit` e `offset` per non scaricare classifiche troppo grandi in una sola richiesta
- `GET /events/{event_id}/ranking-view`
  Restituisce in una sola risposta `event`, opzioni filtro, suggerimenti atleta, filtri applicati e classifica arricchita
- `GET /events/{event_id}/profile-view`
  Restituisce una vista composita per scheda evento: dati calendario, stato evento, filtri reali, gruppi result e classifica principale
- `GET /events/{event_id}/athlete-suggestions`
  Restituisce suggerimenti di completamento per il filtro `athlete`, limitati agli atleti che hanno result in quell'evento
- `GET /events/calendar`
  Restituisce eventi in formato calendario pubblico, anche futuri e anche senza result, con `result_count`, `has_results` e `calendar_status`
  Supporta `limit` e `offset`
- `GET /events/{event_id}/result-filter-options`
  Restituisce solo i valori realmente presenti nei result dell'evento per `format`, `round`, `discipline`, `category`, `apparatus`
  Restituisce anche `ranking_metrics` e `data_qualities` davvero disponibili, con `default_ranking_metric=score` e `default_data_quality=all`
- `GET /events/{event_id}/result-groups`
- `POST /events/{event_id}/result-context`
- `GET /events/{event_id}/result-context`
- `DELETE /events/{event_id}/result-context`
- `GET /events/{event_id}/manual-entry-options`
  Endpoint admin-only per costruire una UI di inserimento manuale: restituisce discipline, categorie, attrezzi, format, round, campi richiesti, campi opzionali, contesto corrente e suggerimenti atleta ammessi dall'evento
- `GET /events/{event_id}/result-athlete-suggestions`
  Endpoint admin-only per suggerire atleti gia presenti nel database durante la digitazione di un result, anche con `nome cognome` o `cognome nome`
- `GET /events/manual-entry-options`
  Endpoint admin-only per costruire la UI di creazione evento: restituisce discipline, categorie, livelli e campi richiesti/opzionali
- `POST /events/{event_id}/athletes/resolve`
  Endpoint admin-only per trovare un atleta esistente oppure creare una nuova entita `Athlete` compatibile con l'evento
- `POST /events/{event_id}/results/bulk`
- `GET /admin/calendar`
  Endpoint admin-only per alimentare una sezione calendario gestionale: restituisce eventi, summary per stato, conteggi result e reminder degli eventi conclusi senza risultati
- `GET /admin/entities-to-complete`
  Endpoint admin-only per alimentare una futura sezione di controllo: restituisce `Athlete` ed `Event` con campi opzionali ancora da completare dopo data entry manuale o import
- `GET /admin/event-result-reminders`
  Endpoint admin-only per vedere eventi conclusi che non hanno ancora result inseriti
- `POST /admin/event-result-reminders/notify`
  Endpoint admin-only per creare notifiche `event_results_reminder` per gli admin, senza duplicarle per lo stesso evento
- `GET /results`
  Supporta `limit` e `offset`
- `GET /results/analytics/rankings`
  Supporta `sort_by` con la stessa semantica della classifica evento
- `GET /results/analytics/trends`
- `POST /results`
- `PUT /results/{result_id}`
- `DELETE /results/{result_id}`
- `GET /admin/audit-logs`
  Endpoint super-admin-only per consultare lo storico delle modifiche critiche su `Athlete`, `Event`, `Result` e ruoli
- `PUT /admin/athletes/{athlete_id}/restore`
- `PUT /admin/events/{event_id}/restore`
- `PUT /admin/results/{result_id}/restore`
  Endpoint super-admin-only per ripristinare entita cancellate con soft delete
- `POST /preferences/athletes/follow`
- `GET /preferences/athletes/followed`
- `GET /preferences/athletes/followed/details`
  Endpoint user-only per mostrare in dashboard personale gli atleti seguiti con scheda atleta, conteggio result e ultimo result
- `DELETE /preferences/athletes/follow/{athlete_id}`
- `POST /preferences/events/save`
- `GET /preferences/events/saved`
- `GET /preferences/events/saved/details`
  Endpoint user-only per mostrare in dashboard personale gli eventi salvati con dati calendario, `calendar_status`, `result_count` e `has_results`
- `DELETE /preferences/events/save/{event_id}`
- `GET /preferences/language-options`
  Endpoint pubblico per esporre le lingue supportate dalla UI: `en`, `it`, `es`, `fr`; la lingua principale/default e `en`
- `GET /preferences/language`
  Endpoint pubblico per risolvere la lingua corrente: per utenti loggati restituisce `preferred_language`; per visitatori anonimi usa `?language=it|es|fr|en`, poi `Accept-Language`, poi default `en`
- `PUT /preferences/language`
  Endpoint user-only per aggiornare la lingua preferita salvata sull'account
- `POST /preferences/dashboard-views`
- `GET /preferences/dashboard-views`
- `GET /preferences/dashboard-views/default`
- `GET /preferences/dashboard-views/{view_id}`
- `PUT /preferences/dashboard-views/{view_id}`
- `DELETE /preferences/dashboard-views/{view_id}`
  Endpoint user-only per salvare ricerche, filtri e configurazioni dashboard personali
- `GET /notifications`
- `PUT /notifications/{notification_id}/read`
- `PUT /notifications/read-all`
  Le notifiche `new_result` sono cumulative per atleta, gara, round e format: piu punteggi dello stesso atleta nella stessa gara/round/format aggiornano una sola notifica.
  Le notifiche `data_entry_summary` ricordano all'admin quando il data entry manuale ha creato nuovi atleti da completare.
- `GET /data-suggestions`
- `POST /data-suggestions`
- `POST /data-suggestions/generate`
  Endpoint admin-only per chiedere al provider AI/web configurato di proporre suggerimenti pendenti per campi mancanti
- `POST /data-suggestions/{suggestion_id}/accept`
- `POST /data-suggestions/{suggestion_id}/reject`
  Endpoint admin-only per creare, consultare, approvare, modificare o rifiutare suggerimenti sui campi mancanti di `Athlete` e `Event`
- `GET /world-gymnastics/athletes/{athlete_id}/candidates`
  Endpoint admin-only per cercare profili atleta ufficiali World Gymnastics compatibili con la scheda Athlete
- `POST /world-gymnastics/athletes/{athlete_id}/suggestions`
  Endpoint admin-only per creare suggerimenti pending dalla scheda profilo atleta World Gymnastics scelta dall'admin
- `GET /world-gymnastics/events/{event_id}/candidates`
  Endpoint admin-only per cercare eventi ufficiali World Gymnastics compatibili con la scheda Event
- `POST /world-gymnastics/events/{event_id}/suggestions`
  Endpoint admin-only per creare suggerimenti pending dalla scheda evento World Gymnastics scelta dall'admin

## Modello dati essenziale

- `Athlete`
  Campi principali: `first_name`, `last_name`, `birth_year`, `country`, `discipline`, `image_url`, `country_changes`, `world_gymnastics_athlete_id`, `world_gymnastics_profile_url`, `world_gymnastics_status`
  `birth_year`: opzionale; anno di nascita ufficiale/confermato, validato lato API come anno non futuro
  `country` rappresenta la nazionalita corrente; `country_changes` registra eventuali cambi con `from_country`, `to_country`, `change_year`
  `discipline`: `MAG` oppure `WAG`
  `world_gymnastics_athlete_id`, `world_gymnastics_profile_url` e `world_gymnastics_status`: opzionali; vengono pensati come metadati ufficiali World Gymnastics e restano `NULL` finche un admin non verifica/approva il profilo tramite il motore World Gymnastics
  `world_gymnastics_verified_at` e `world_gymnastics_verified_by_admin_id`: valorizzati automaticamente quando un admin approva un suggerimento World Gymnastics legato al profilo ufficiale
- `Event`
  Campi principali: `name`, `location`, `venue`, `start_date`, `end_date`, `year`, `discipline`, `category`, `level`, `image_url`, `world_gymnastics_event_id`, `world_gymnastics_event_url`, `world_gymnastics_status`
  `discipline`: `MAG`, `WAG`, `MAG and WAG`
  `category`: `junior`, `senior`, `junior and senior`
  Nei filtri API, `MAG and WAG` corrisponde alla selezione contemporanea di `MAG` e `WAG`
  Nei filtri API, `junior and senior` corrisponde alla selezione contemporanea di `junior` e `senior`
  `world_gymnastics_event_id`, `world_gymnastics_event_url` e `world_gymnastics_status`: opzionali; restano `NULL` finche un admin non verifica/approva l'evento tramite il motore World Gymnastics
  `world_gymnastics_verified_at` e `world_gymnastics_verified_by_admin_id`: valorizzati automaticamente quando un admin approva un suggerimento World Gymnastics legato all'evento ufficiale
- `Result`
  Campi principali: `athlete_id`, `event_id`, `represented_country`, `discipline`, `category`, `apparatus`, `vt_attempt`, `day`, `format`, `round`, `D_score`, `E_score`, `Penalty`, `Bonus`, `score`, `rank`
  `represented_country`: country rappresentata dall'atleta in quella specifica gara; resta separata da `Athlete.country`, che indica la nazionalita corrente
  `discipline`: deve coincidere con la disciplina dell'atleta e deve essere ammessa dall'evento
  `category`: `junior` oppure `senior`, mai combinata, e deve essere ammessa dall'evento
  `day`: opzionale; `NULL` per result senza distinzione giornaliera, numero positivo per gare su piu giornate
  `score`, `D_score`, `E_score`, `Penalty`, `Bonus`: opzionali quando il dominio lo consente
  `e_score_status` e `penalty_status`: campi API calcolati per spiegare il significato di `E_score` e `Penalty`: `available` oppure `not_available`
  per i dati Gymternet legacy, `E_score` e `Penalty` restano normalmente `NULL` perche non conosciuti; la UI deve mostrarli come `non disponibile`
  dal 2026 in poi, nei flussi manuali o standard moderni, `E_score` e obbligatorio; `Penalty` e `Bonus` vuoti/nulli vengono salvati come `0.0` ed esposti con status `available`
  `Bonus`: resta numerico oppure `NULL`; non va popolato con stringhe testuali
  `bonus_status`: campo API calcolato per spiegare il significato di `Bonus`: `available`, `not_available`, `not_applicable`
  per il periodo 2018-2024 il Bonus non esisteva nel codice dei punteggi: `Bonus=NULL` viene esposto come `bonus_status=not_applicable`
  dal 2025 il Bonus esiste nel regolamento, ma nei dati Gymternet non e registrato: se il Result e in un caso in cui il Bonus potrebbe esistere e `Bonus=NULL`, viene esposto come `bonus_status=not_available`
  regole Bonus note dal 2025: `WAG` solo su `VT AVG` con valore `0.2` se conosciuto; `MAG` solo su `FX`, `SR`, `VT`, `PB`, `HB` con valore `0.1` se conosciuto
  La UI deve mostrare i campi score opzionali `NULL` come `non disponibile` solo quando il relativo status e `not_available`
  Le risposte API aggiungono `execution_estimate = score - D_score` solo quando `score` e `D_score` sono disponibili; non e un E-score ufficiale e non viene salvato nel database
  Quando `execution_estimate` e presente, le risposte API aggiungono in `data_warnings` un avviso calcolato in base agli status disponibili
  Se `penalty_status=not_available`, l'avviso cita le Penalties non disponibili; se `bonus_status=not_available`, cita anche il possibile Bonus non registrato
  Le risposte API aggiungono anche `is_complete` e `missing_fields`; un Result senza `score` o senza `D_score` e valido solo nei casi previsti e viene marcato come incompleto
  `vault_attempt_order_uncertain`: `true` quando un `VT attempt 1/2` deriva dalla logica Gymternet pre-2025 e l'ordine effettivo dei vault potrebbe essere invertito; le risposte API aggiungono `data_warnings` per permettere alla UI di mostrare un piccolo `!`
  `apparatus`:
  per `MAG`: `FX`, `PH`, `SR`, `VT`, `PB`, `HB`, `AA`, `VT AVG`
  per `WAG`: `VT`, `UB`, `BB`, `FX`, `AA`, `VT AVG`
- `DataSuggestion`
  Campi principali: `entity_type`, `entity_id`, `field_name`, `suggested_value`, `reviewed_value`, `confidence`, `source_url`, `source_title`, `evidence`, `status`, `created_by_admin_id`, `reviewed_by_admin_id`
  `entity_type`: `athlete` oppure `event`
  `status`: `pending`, `accepted`, `edited`, `rejected`
  `suggested_value` conserva il valore proposto dall'assistente; `reviewed_value` conserva il valore finale approvato o modificato dall'admin
  I suggerimenti sono visibili solo agli admin e non modificano mai i dati ufficiali finche un admin non li approva o li modifica esplicitamente

## Configurazione email
Aggiungi le variabili d'ambiente per inviare link di verifica email e reset password via SMTP:

- `DATABASE_URL` (opzionale, default `sqlite:///./leverage.db`)
- `APP_ENV` (default `development`)
- `SECRET_KEY` (opzionale in locale, consigliata in produzione)
- `FRONTEND_BASE_URL` (obbligatoria in staging/production e deve usare HTTPS)
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USER`
- `SMTP_PASSWORD`
- `EMAIL_FROM`
- `AI_SUGGESTIONS_PROVIDER` (`disabled` oppure `openai`)
- `OPENAI_API_KEY`
- `OPENAI_BASE_URL` (default `https://api.openai.com/v1`)
- `OPENAI_MODEL` (default `gpt-5`)
- `AI_SUGGESTIONS_TIMEOUT_SECONDS` (default `30`)
- `WORLD_GYMNASTICS_TIMEOUT_SECONDS` (default `10`)

Se le variabili SMTP non sono configurate in locale, il backend continua a funzionare in modalità development/test stampando il contenuto email in console.
In `production` e `staging`, `SECRET_KEY`, SMTP e `FRONTEND_BASE_URL` HTTPS devono essere configurati esplicitamente.

## Admin bootstrap
Il primo `super_admin` va creato da terminale, non tramite auto-promozione pubblica:

```bash
python -m app.bootstrap_admin --email owner@example.com
```

Il comando crea o aggiorna l'account come `super_admin`, imposta password e verifica email. Al primo login web l'account dovra completare il setup MFA.

Gli admin successivi vengono nominati da un `super_admin`. Il flusso consigliato per la UI admin e:

1. `GET /admin/users?search=email@example.com`
   Cerca l'utente registrato tramite email.
2. `PUT /admin/users/role-by-email`
   Promuove l'utente a `admin` con payload `{"email": "...", "role": "admin"}`.

LEVERAGE impedisce di rimuovere l'ultimo `super_admin` e impedisce a un `super_admin` di degradare se stesso. Quando un utente viene promosso ad admin/super admin, riceve una notifica personale di tipo `admin_promotion` e al login successivo deve usare/configurare MFA. Quando un admin viene declassato a user, riceve una notifica personale di tipo `admin_demotion`.

## Sicurezza dati
Le operazioni ordinarie di data entry restano disponibili agli `admin`, ma le operazioni distruttive e di governo sono riservate ai `super_admin`.

- `Athlete`, `Event` e `Result` usano soft delete: `DELETE` non rimuove fisicamente il record, ma valorizza `is_deleted`, `deleted_at` e `deleted_by_admin_id`.
- Le API pubbliche e analytics escludono i record soft-deleted.
- Il `super_admin` puo ripristinare entita cancellate tramite endpoint `/admin/.../restore`.
- Le modifiche critiche producono record in `audit_logs`, consultabili con `GET /admin/audit-logs`.
- Le operazioni distruttive o di cambio ruolo possono generare notifiche `security_alert` per gli altri super admin.

Il soft delete non sostituisce i backup: in produzione sara comunque necessario configurare backup automatici del database a livello infrastrutturale, idealmente giornalieri o piu frequenti durante import massivi.

## Calendario eventi
Gli `Event` possono essere creati anche prima che la gara si svolga e possono quindi non avere ancora `Result` associati.
`GET /events/calendar` espone una vista calendario pubblica con stato calcolato automaticamente:

- `upcoming`: evento futuro
- `ongoing`: evento in corso
- `completed_no_results`: evento concluso senza result
- `completed_with_results`: evento concluso con result

Lo stato non viene salvato manualmente nel database: deriva da `start_date`, `end_date`, data corrente e numero di `Result` associati.
Per gli admin, `GET /admin/calendar` restituisce una vista gestionale aggregata con eventi, summary per stato e reminder. `GET /admin/event-result-reminders` mostra solo gli eventi conclusi senza result; `POST /admin/event-result-reminders/notify` crea una notifica `event_results_reminder` per ricordare l'inserimento dei risultati.

## Accesso pubblico e area personale
LEVERAGE e pensato come sito pubblico consultabile senza login: atleti, eventi, risultati, classifiche e analytics sono leggibili da visitatori anonimi.

Il login serve per entrare nell'area personale o nell'area admin:

- visitatore anonimo: puo leggere e filtrare dati ufficiali
- `user`: puo leggere dati ufficiali e salvare preferenze personali
- `admin`: puo fare data entry, import, correzioni, upload immagini e approvazione suggerimenti

Per la UI il flusso consigliato e: `POST /auth/register`, verifica email tramite `POST /auth/verify-email`, poi `POST /auth/login`. Dopo il login, la UI puo chiamare `GET /auth/me` per sapere ruolo, stato account e MFA. Se un admin non ha ancora MFA attivo, `POST /auth/login` restituisce `mfa_setup_required` e un token temporaneo per completare `POST /auth/mfa/setup` e `POST /auth/mfa/confirm`.

## Lingua e i18n
La lingua principale del backend e l'inglese. I dati sportivi e i codici API (`MAG`, `WAG`, `FX`, `score`, enum tecniche) non vengono tradotti per non rompere il contratto dati.

I visitatori anonimi possono cambiare lingua nella UI senza account: il frontend deve conservarla localmente, per esempio in local storage o cookie, e puo validarla/risolverla con `GET /preferences/language?language=it`. Se non c'e scelta esplicita, il backend puo usare l'header `Accept-Language`; se non e supportato, torna `en`.

Gli utenti registrati hanno `preferred_language`, con default `en` e valori ammessi `en`, `it`, `es`, `fr`. La UI puo leggere le opzioni da `GET /preferences/language-options`, salvare la scelta persistente con `PUT /preferences/language` e recuperarla anche da `GET /auth/me`.

Le notifiche generate dal backend usano sempre la lingua preferita del destinatario loggato. Per visitatori anonimi, testi di interfaccia e label visuali restano responsabilita del frontend.

## Inserimento manuale dati
La creazione, modifica, cancellazione e upload immagini di `Athlete`, `Event` e `Result` sono operazioni riservate agli admin.

Per una interfaccia semplice di data entry, il frontend puo usare questo flusso:

1. `GET /events/manual-entry-options`
   Mostra i valori ammessi per creare una nuova gara.
2. `POST /events`
   Crea la gara.
3. `PUT /events/{event_id}`
   Completa o corregge i dati della gara.
4. `GET /events/{event_id}/manual-entry-options`
   Mostra le opzioni coerenti con quella gara.
5. `POST /events/{event_id}/result-context`
   Imposta il contesto di inserimento, soprattutto `format` e `round`, cosi non vanno ripetuti su ogni result. Per gare su piu giornate puo includere anche `day`.
6. `GET /events/{event_id}/result-athlete-suggestions`
   Durante la digitazione del result suggerisce atleti gia presenti nel database e compatibili con la gara.
7. `POST /events/{event_id}/athletes/resolve`
   Mentre l'admin digita il nome atleta, il sistema puo riusare un atleta gia presente oppure crearne uno nuovo se manca.
8. `POST /events/{event_id}/results/bulk`
   Inserisce i result usando il contesto corrente.

Gli endpoint `manual-entry-options` evitano valori hardcoded nella UI e restituiscono solo opzioni coerenti con l'evento selezionato.
Nel bulk results ogni riga puo usare `athlete_id` se l'atleta esiste gia, oppure `athlete` con `first_name`, `last_name`, `country`, `birth_year`, `image_url` se deve essere creato automaticamente. `represented_country` e facoltativo e, se omesso, viene inizializzato con la country corrente dell'atleta.
Dal 2026, nel data entry manuale `E_score` e obbligatorio. `Penalty` e `Bonus` lasciati vuoti vengono salvati come `0.0`. Prima di creare i result, il bulk verifica per ogni riga `Final Score = D_score + E_score - Penalty + Bonus`: se almeno una riga non torna, l'intero inserimento viene bloccato e l'admin riceve una notifica cumulativa `data_entry_summary` con i result da correggere.
`GET /events/{event_id}/manual-entry-options` segnala questa regola alla UI: per eventi dal 2026 in poi `E_score` viene restituito tra i `required_result_fields`, mentre per eventi storici resta tra i campi opzionali.
Il bulk manuale e il `POST /results` bloccano anche duplicati sullo stesso contesto sportivo: atleta, evento, discipline, category, apparatus, vault attempt, day, format e round.
Quando `POST /events/{event_id}/athletes/resolve` o il bulk results creano nuovi atleti, LEVERAGE genera una notifica admin `data_entry_summary` con il riepilogo degli atleti creati e il link logico all'evento.
La futura UI admin puo usare `GET /admin/entities-to-complete` per mostrare gli atleti e gli eventi con campi ancora vuoti, cosi l'admin puo completare le schede dopo aver finito la classifica in corso.
La futura UI admin puo usare anche `GET /admin/result-duplicate-groups` per controllare eventuali duplicati gia presenti nel database prima o dopo import storici: l'endpoint raggruppa i `Result` con stessa identita sportiva e mostra gli ID da verificare.

## Merge amministrativo Athlete
Se dopo un import o un controllo manuale emerge che lo stesso atleta e stato salvato come due entita diverse per un errore di battitura, LEVERAGE espone un flusso admin-only per unirle.

Flusso consigliato per la UI admin:

1. L'admin apre la scheda duplicata e inserisce l'ID dell'atleta corretto/canonico.
2. `POST /athletes/{source_athlete_id}/merge-preview` con `{"target_athlete_id": ...}`.
3. La UI mostra dati dei due atleti, result da spostare, preferenze utente coinvolte, country history, suggerimenti/notification da riallacciare e conflitti bloccanti.
4. Se `can_merge=true`, l'admin conferma con `POST /athletes/{source_athlete_id}/merge` e payload `{"target_athlete_id": ..., "confirm": true, "reason": "..."}`.

Il merge sposta i `Result` verso l'atleta canonico, mantiene `represented_country` sui result, riallaccia i follower, sposta country history non duplicate, sposta suggerimenti e notifiche collegate, copia nel target solo metadati mancanti, soft-delete della scheda duplicata e registra audit log. Se il merge creerebbe due result nello stesso contesto sportivo sullo stesso atleta target, l'operazione viene bloccata con `409` e la preview restituisce i conflitti da risolvere.

## Scalabilita pre-popolamento
Prima della popolazione storica 2018-2025, LEVERAGE include una migrazione dedicata agli indici (`0027_add_scalability_indexes`) per rendere piu efficienti classifiche evento, schede atleta, filtri calendario, ranking, ricerca duplicati e query sui country rappresentati.

Gli endpoint pubblici principali che possono crescere molto supportano `limit` e `offset`: `/athletes`, `/events`, `/events/calendar`, `/results`, `/events/{event_id}/results`, `/events/{event_id}/ranking-view`, `/athletes/{athlete_id}/results` e `/athletes/{athlete_id}/events/{event_id}/results`.

## Dashboard e analytics user
Gli endpoint `/analytics` sono pubblici in lettura e pensati come contratto stabile per una futura UI interattiva.

Filtri supportati:

- periodo: `start_year`, `end_year`, `start_date`, `end_date`
- gara: `event_id`, `level`
- result: `discipline`, `category`, `format`, `round`, `apparatus`, `day`
- atleta/country: `ids` per confronti, `country` per filtri aggregati
- metrica: `score`, `D_score`, `execution_estimate`, `E_score`, `Penalty`, `Bonus`
- qualita dato: `data_quality=all`, `data_quality=complete`, `data_quality=missing_d_score`, `data_quality=missing_score`

Le serie per confronto atleti possono essere restituite come punti grezzi (`raw`) oppure aggregate per evento, anno o apparatus. Questo permette al frontend di costruire grafici sovrapponibili senza dover ricostruire la semantica dei dati.
I punti dei grafici includono `execution_estimate`, `is_complete`, `missing_fields`, `complete_result_count` e `partial_result_count`, cosi la UI puo evidenziare quando una media o un trend contiene result con dati non disponibili.

Per i grafici sull'eta, LEVERAGE usa `birth_year` e `Event.year`, quindi l'eta e una stima annuale coerente con i dati ufficiali disponibili. La media per country usa `Result.represented_country` e viene calcolata su coppie uniche atleta-gara, cosi un atleta con piu result nella stessa gara non pesa piu volte sull'eta media.

Gli utenti loggati possono salvare viste dashboard personali tramite `/preferences/dashboard-views`. Una vista contiene `name`, `view_type`, `chart_type`, `metric`, `filters`, `is_default` e `position`; questo permette alla UI di riproporre ricerche frequenti, filtri preferiti e grafici principali senza rendere definitivo un layout specifico.

## Analitiche sito web
LEVERAGE include una prima versione leggera di analytics del sito, separata dalle analytics sportive.

Il frontend puo inviare eventi a `POST /site-analytics/events`:

- `page_view`
- `search`
- `athlete_view`
- `event_view`
- `dashboard_view`
- `session_end`

Il payload puo includere `visitor_id`, `session_id`, `path`, `search_query`, `entity_type`, `entity_id` e `duration_seconds`. Se la richiesta contiene un token valido, LEVERAGE collega l'evento allo user loggato; altrimenti resta anonimo.

Per scelta privacy-friendly questa prima versione non salva IP, user-agent completo, fingerprint del browser o dati sensibili. La dashboard admin usa solo dati aggregati.

`GET /site-analytics/admin/summary` restituisce:

- visitatori unici
- sessioni
- page views
- ricerche
- atleti piu visualizzati
- gare piu visualizzate
- tempo medio stimato dalle sessioni chiuse
- numero iscritti, verificati/non verificati, attivi/inattivi

## World Gymnastics Athlete
LEVERAGE espone un motore leggero admin-only per proporre dati mancanti di `Athlete` usando solo pagine pubbliche ufficiali World Gymnastics, senza AI e senza API a pagamento.

Flusso consigliato nella scheda admin Athlete:

1. `GET /athletes/{athlete_id}/admin-view`
   Mostra la scheda ufficiale LEVERAGE e i suggerimenti pendenti gia presenti.
2. `GET /world-gymnastics/athletes/{athlete_id}/candidates`
   Cerca candidati World Gymnastics usando cognome, disciplina e country quando disponibile.
3. L'admin seleziona il profilo corretto tra i candidati.
4. `POST /world-gymnastics/athletes/{athlete_id}/suggestions`
   Con `fig_athlete_id` oppure `fig_profile_url`, legge la pagina profilo ufficiale e crea suggerimenti `pending`.
5. L'admin approva, modifica o rifiuta i suggerimenti tramite gli endpoint `data-suggestions`.

Campi suggeribili attuali:

- `birth_year`, da `Year of birth`
- `country`, da codice country del profilo
- `image_url`, solo se il profilo espone una immagine chiara e riusabile
- `world_gymnastics_athlete_id`, dal profilo selezionato
- `world_gymnastics_profile_url`, link diretto al profilo ufficiale selezionato
- `world_gymnastics_status`, dallo status World Gymnastics quando disponibile

`first_name`, `last_name` e `discipline` non vengono modificati automaticamente: se differiscono dal profilo World Gymnastics, il backend restituisce warning per revisione admin.
Quando un admin approva `world_gymnastics_athlete_id`, `world_gymnastics_profile_url` o `world_gymnastics_status`, LEVERAGE registra anche `world_gymnastics_verified_at` e `world_gymnastics_verified_by_admin_id`.

## World Gymnastics Event
LEVERAGE espone anche un motore leggero admin-only per collegare una scheda `Event` a una pagina evento ufficiale World Gymnastics, usando l'endpoint pubblico `sportevents` del sito ufficiale.

Flusso consigliato nella scheda admin Event:

1. `GET /events/{event_id}/admin-view`
   Mostra la scheda ufficiale LEVERAGE e i suggerimenti pendenti gia presenti.
2. `GET /world-gymnastics/events/{event_id}/candidates`
   Cerca candidati World Gymnastics usando nome evento, anno/date, location e disciplina.
3. L'admin seleziona l'evento ufficiale corretto tra i candidati.
4. `POST /world-gymnastics/events/{event_id}/suggestions`
   Con `fig_event_id` oppure `fig_event_url`, legge il dettaglio ufficiale e crea suggerimenti `pending`.
5. L'admin approva, modifica o rifiuta i suggerimenti tramite gli endpoint `data-suggestions`.

Campi suggeribili attuali:

- `location`, da city/country ufficiali
- `venue`, dalla venue ufficiale quando disponibile
- `start_date`, da event dates
- `end_date`, da event dates
- `discipline`, mappata su `MAG`, `WAG`, `MAG and WAG`
- `category`, mappata su `junior`, `senior`, `junior and senior`
- `level`, mappato sui livelli LEVERAGE
- `world_gymnastics_event_id`, dal dettaglio selezionato
- `world_gymnastics_event_url`, link diretto al dettaglio ufficiale selezionato
- `world_gymnastics_status`, dallo status World Gymnastics quando disponibile

`image_url` per `Event` resta volutamente fuori dal motore World Gymnastics Event: in seguito si puo valutare se usare immagini prefissate per tipologia evento, per esempio cerchi olimpici per Olympic Games, oppure eliminare il campo se non serve davvero.
Quando un admin approva `world_gymnastics_event_id`, `world_gymnastics_event_url` o `world_gymnastics_status`, LEVERAGE registra anche `world_gymnastics_verified_at` e `world_gymnastics_verified_by_admin_id`.

## Suggerimenti AI/web assistiti
LEVERAGE supporta una coda admin-only di suggerimenti per completare campi mancanti di `Athlete` e `Event`.

Il motore AI/web deve essere trattato solo come assistente: puo proporre valori, fonte ed evidenza, ma il dato diventa ufficiale solo dopo una decisione esplicita di un admin. Gli utenti non-admin non vedono i suggerimenti e gli endpoint pubblici continuano a mostrare solo dati ufficiali gia approvati.

Il provider e disabilitato di default. Per usare OpenAI con web search lato server:

```bash
AI_SUGGESTIONS_PROVIDER=openai
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-5
```

Questa integrazione usa la Responses API con strumento `web_search` e output strutturato JSON. `ChatGPT Plus` e l'API sono prodotti distinti: per questa funzione serve una chiave API server-side configurata nell'ambiente del backend.

Flusso consigliato per la UI admin:

1. Aprire `GET /athletes/{athlete_id}/admin-view` oppure `GET /events/{event_id}/admin-view`.
2. Se mancano dati, usare `POST /data-suggestions/generate` con `entity_type`, `entity_id` e, opzionalmente, `fields`.
3. Mostrare i `pending_suggestions` direttamente nella scheda admin, accanto al campo interessato.
4. Usare `POST /data-suggestions/{suggestion_id}/accept` per approvare il valore suggerito.
5. Usare lo stesso endpoint con `{"value": "..."}` per approvare una versione corretta dall'admin. In questo caso `suggested_value` resta invariato e `reviewed_value` salva il valore finale.
6. Usare `POST /data-suggestions/{suggestion_id}/reject` per rifiutare il suggerimento.

Campi suggeribili attuali:

- `Athlete`: `birth_year`, `country`, `image_url`
- `Event`: `location`, `venue`, `start_date`, `end_date`, `level`, `image_url`

## Import Gymternet
Accanto al data entry manuale, LEVERAGE espone uno strumento admin-only per caricare file Gymternet standardizzati in formato `.xlsx` o `.csv`.

Il contratto comune che un import parallelo futuro dovra rispettare e documentato in [docs/import_contract.md](docs/import_contract.md). In sintesi: parser diversi sono ammessi, ma tutti gli importer devono convergere sulla stessa preview admin, sugli stessi controlli di atleta/evento/result, sulla stessa logica anti-duplicato, sulle stesse verifiche di country storica e sulle notifiche cumulative.

Il popolamento storico 2018-2025 viene documentato passo passo in [docs/LEVERAGE_popolamento_massivo_diario.md](docs/LEVERAGE_popolamento_massivo_diario.md), con preview, statistiche, scelte admin, commit e controlli post-import per ogni anno.

Una sintesi metodologica in forma di capitolo da tesi e disponibile in [docs/LEVERAGE_capitolo_metodologia_popolamento_db.md](docs/LEVERAGE_capitolo_metodologia_popolamento_db.md), con copia Word in `docs/LEVERAGE_capitolo_metodologia_popolamento_db.docx`.

Flusso consigliato per la UI admin:

1. `POST /imports/gymternet/preview`
   Carica il file e mostra quanti `Athlete`, `Event` e `Result` verrebbero creati, duplicati identici da saltare, conflitti da risolvere, warning, un campione di righe importabili e la review dei D-score non agganciati.
2. `POST /imports/gymternet/review-target-suggestions`
   Usa lo stesso file della preview e restituisce target `Result` suggeriti mentre l'admin risolve manualmente un D-score non agganciato. Accetta `query`, `review_id`, `year_hint`, `csv_discipline`, `csv_score_kind` e `limit`; la UI puo usarlo come autocomplete per scegliere il `target_id` corretto.
3. `POST /imports/gymternet/commit`
   Ripete il parsing e scrive nel database solo se non ci sono errori strutturali. Di default blocca il commit se ci sono conflitti; con `allow_partial=true` importa le righe pulite e lascia i conflitti non importati nel report. I duplicati identici vengono saltati. Puo ricevere decisioni admin per applicare D-score non agganciati.
   Al termine del commit genera una singola notifica admin `import_summary` con il report generale dell'import: nuovi `Athlete`, nuovi `Event`, nuovi `Result`, atleti ed eventi con nuovi risultati, aggiornamenti applicati e duplicati saltati.
   Se un nuovo atleta importato assomiglia a un `Athlete` gia presente nel database, il commit viene bloccato finche l'admin non decide se usare l'atleta esistente, creare un nuovo atleta o indicare manualmente l'atleta corretto.

Parametri opzionali:

- `year_hint`: anno da usare quando il file o il nome gara non contengono l'anno.
- `csv_discipline`: `MAG` o `WAG`, utile per CSV pivot senza disciplina nel file.
- `csv_score_kind`: `final` o `dscore`, utile per CSV pivot.
- `allow_partial`: solo sul commit; se `true`, importa i result senza conflitti e salta quelli conflittuali.
- `orphan_review_limit`: limita quanti problemi D-score restituire nella preview.
- `orphan_dscore_decisions`: solo sul commit, come campo form JSON. Ogni decisione usa `review_id` dalla preview e una `action`: `accept_suggestion`, `discard`, oppure `manual_target`.
- `athlete_review_limit`: limita quanti possibili match atleta restituire nella preview.
- `athlete_match_decisions`: solo sul commit, come campo form JSON. Ogni decisione usa `review_id` dalla preview. Per i match ordinari sono disponibili `accept_suggestion`, `create_new` e `manual_target`; per un possibile cambio country sono disponibili anche `update_country` e `keep_existing_country`.
  Per un match con atleta gia presente, l'admin puo aggiungere `target_name_update` quando verifica che il nome salvato nella scheda atleta esistente contiene un errore di data entry. Il commit aggiorna la scheda atleta target senza creare un duplicato.
- se lo stesso nome e la stessa disciplina compaiono con country diverse nello stesso file, la preview crea una verifica bloccante `possible_athlete_identity_collision`. L'admin puo scegliere `keep_separate`, `merge_as_same_athlete` indicando `canonical_country`, `accept_suggestion` verso un atleta esistente oppure `manual_target`.
  Per `merge_as_same_athlete`, il default e `country_strategy="preserve_represented_country"`: una sola scheda Athlete, ma ogni Result conserva la country sorgente come storico di rappresentanza. Se invece una country e un errore di data entry, l'admin puo aggiungere `country_corrections`, per esempio `{"RUS": "ISR"}`, e il commit salvera i Result interessati con `represented_country` corretto.
  Quando l'admin sceglie `update_country`, il sistema aggiorna `Athlete.country` e registra una riga in `country_changes` con l'anno del file importato.
  In assenza di correzioni esplicite, ogni Result importato salva la country sorgente in `represented_country`, preservando la nazionalita storica usata da classifiche, filtri e analytics.
- se lo stesso file contiene lo stesso atleta con nome/cognome invertiti o formato equivalente, il tool applica automaticamente `merge name order`: crea una sola chiave atleta e usa come ordine canonico il nome gia presente nel database, quando disponibile, oppure la variante piu ricorrente nel file importato.
  Se dopo questo merge emergono country diverse, la preview crea comunque una verifica bloccante `possible_athlete_identity_collision`: l'admin decide solo la parte country (`country_history`, `country_correction`, `keep_separate` o target manuale), non l'inversione nome/cognome.
- `represented_country` non fa parte della chiave anti-duplicato del `Result`: se il sistema trova lo stesso contesto sportivo con paese rappresentato diverso, il record viene trattato come conflitto da review admin e non come duplicato innocuo.

## Import calendario eventi
LEVERAGE espone anche un import admin-only per file calendario Gymternet con fogli annuali e colonne `DATE` / `EVENT`.

Endpoint:

1. `POST /imports/calendar/preview`
   Legge il file `.xlsx`, `.xlsm` o `.csv`, interpreta date come `Jan 11`, `Jan 11-15`, `Jan 11-Feb 3`, confronta gli eventi con il database e restituisce cosa verrebbe aggiornato o creato.
2. `POST /imports/calendar/commit`
   Ripete il parsing, aggiorna `start_date` / `end_date` degli eventi gia presenti e crea automaticamente solo gli eventi mancanti da `create_missing_from_year` in poi. Le righe storiche non matchate restano in review e non vengono create automaticamente.

Default per nuovi eventi calendario:

- `discipline`: `MAG and WAG`, salvo suffissi espliciti come `(MAG)` o `(WAG)`;
- `category`: `junior and senior`, salvo indicazioni esplicite nel nome;
- `level`: inferito da parole chiave essenziali (`Olympic`, `World Cup`, `World Championships`, ecc.), altrimenti `International Event`.

Il commit genera una notifica admin `import_summary` con riepilogo degli eventi aggiornati, futuri creati e righe storiche rimaste in review.

Esempio decisione admin:

```json
[
  {
    "review_id": "orphan_...",
    "action": "accept_suggestion",
    "suggestion_id": "suggestion_..."
  },
  {
    "review_id": "orphan_...",
    "action": "discard"
  },
  {
    "review_id": "orphan_...",
    "action": "manual_target",
    "target": {
      "event_name": "All-Japan Team Championships",
      "year": 2018,
      "athlete_name": "Daiki Hasimoto",
      "discipline": "MAG",
      "category": "senior",
      "apparatus": "HB",
      "vt_attempt": null,
      "format": "individual",
      "round": "final",
      "day": null
    }
  }
]
```

Esempio decisione admin per possibile atleta gia esistente:

```json
[
  {
    "review_id": "athlete_match_...",
    "action": "accept_suggestion",
    "suggestion_id": "suggestion_..."
  },
  {
    "review_id": "athlete_match_...",
    "action": "create_new"
  },
  {
    "review_id": "athlete_match_...",
    "action": "manual_target",
    "target": {
      "athlete_id": 123
    }
  },
  {
    "review_id": "athlete_country_...",
    "action": "update_country"
  },
  {
    "review_id": "athlete_match_...",
    "action": "accept_suggestion",
    "suggestion_id": "suggestion_...",
    "country_action": "keep_existing_country"
  },
  {
    "review_id": "athlete_identity_collision_...",
    "action": "merge_as_same_athlete",
    "canonical_country": "ITA",
    "country_strategy": "preserve_represented_country"
  },
  {
    "review_id": "athlete_identity_collision_...",
    "action": "merge_as_same_athlete",
    "canonical_country": "ISR",
    "country_strategy": "country_correction",
    "country_corrections": {
      "RUS": "ISR"
    }
  }
]
```

Regole Gymternet attualmente applicate:

- file `.xlsx` con fogli `MAG`, `MAG D`, `WAG`, `WAG D`;
- file `.csv` flat con colonne come `discipline`, `athlete`, `country`, `event`, `apparatus`, `score`, `d_score`;
- atleta con asterisco (`*`) = `junior`; l'asterisco viene rimosso dal nome salvato;
- nazione convertita in codice ufficiale quando riconosciuta;
- `day` e opzionale su `Result`: `NULL` per result senza distinzione giornaliera, valore positivo per gare su piu giornate;
- `score`, `D_score`, `E_score`, `Penalty` e `Bonus` restano opzionali nei casi ammessi: per Gymternet legacy i valori non presenti vengono salvati come `NULL` e mostrati come `non disponibile` quando il dato e rilevante ma mancante;
- per Gymternet legacy anche i dati successivi al 2025 seguono la policy del 2025; la normalizzazione a `0.0` dei campi vuoti vale per data entry manuale e import standard moderni, non per questo importer legacy;
- la UI deve usare `bonus_status` per distinguere `not_available` da `not_applicable`;
- i record con final score ma senza `D_score` vengono importati come result parziali validi;
- i record con solo `D_score` e senza final score non creano Result: vengono tenuti nel report/review per eventuale aggancio admin a un result con final score;
- il report `import_summary` distingue nuovi punteggi completi, nuovi punteggi con dati `not available` e D-score orfani rimasti in review;
- se il file contiene una colonna `Day`, il valore viene usato direttamente;
- se il file non contiene `Day`, risultati ripetuti con stessa chiave ma score/D-score diverso ricevono automaticamente `day=1`, `day=2`, ecc.;
- event senza suffix = `format=individual`, `round=final`;
- suffix `QF` = `individual` / `qualification`, `TF` = `team` / `final`, `AA` = `individual` / `final`, `EF` = `apparatus` / `final`;
- `AA` viene salvato come apparatus `AA`;
- `VT AVG` viene salvato come apparatus `VT AVG`;
- per gli anni 2018-2024, nei fogli `MAG` e `WAG`, `VT` viene salvato come `vt_attempt=1` con `vault_attempt_order_uncertain=true`;
- per gli anni 2018-2024, `VT attempt 2` viene ricavato da `VT AVG` come final score e da `VT SUM` come D-score, sempre con `vault_attempt_order_uncertain=true`;
- dal 2025 in poi, Gymternet legacy applica sempre la policy 2025;
- per MAG dal 2025 in poi, `VT` viene salvato come `vt_attempt=1` con `vault_attempt_order_uncertain=true` e `VT attempt 2` viene ricavato da `VT AVG` come final score e da `VT SUM` come D-score;
- per WAG dal 2025 in poi, `VT` viene salvato come `vt_attempt=1` con `vault_attempt_order_uncertain=true`; `VT attempt 2` riceve solo il D-score ricavato da `VT SUM`, mentre il final score viene salvato come `NULL` e mostrato in UI come `not available`;
- se il tool Gymternet legacy viene usato per dati successivi al 2025, genera un warning per ricordare che sta applicando le regole 2025; il percorso consigliato per dati futuri completi resta un import standard dedicato;
- `VT SUM` viene riconosciuto come colonna sorgente ma non viene salvato nel database come `Result`;
- duplicate key: `athlete_id`, `event_id`, `discipline`, `category`, `apparatus`, `format`, `round`, `vt_attempt`, `day`;
- duplicato identico = skip; stessa key con score/D-score diversi = conflitto in preview, blocco del commit standard oppure skip esplicito con `allow_partial=true`;
- stessa key con score/D-score uguali ma `represented_country` diverso = conflitto `country_conflict_*`, per evitare fusioni errate di atleti o perdita della nazionalita storica.

## Test

```bash
pytest
```

I test usano `test_leverage.db` tramite `DATABASE_URL`, separato dal database locale di sviluppo.

Ultimo audit pre-Git locale:

- 28 migrazioni Alembic;
- 99 test automatici;
- 106 endpoint router;
- `alembic upgrade head` verificato su database SQLite temporaneo;
- `.gitignore` configurato per escludere `.venv`, cache, database locali, log, `uploads/` e file sorgente locali in `import_files/`.

## Migrazioni

Alembic è configurato in `alembic.ini` e nella cartella `migrations/`.
LEVERAGE non crea più le tabelle automaticamente all'avvio: lo schema va gestito tramite migrazioni.

```bash
alembic upgrade head
alembic revision --autogenerate -m "descrizione modifica"
```
