# LEVERAGE - Import reports

Questa cartella conserva report derivati dai tool di import, separati dal database operativo.

I file qui presenti servono per:

- audit del popolamento massivo;
- tracciamento dei record non importati;
- eventuale recupero manuale futuro;
- documentazione metodologica per il diario di bordo.

Le regole decisionali riutilizzabili dal tool Gymternet sono documentate in:

```text
docs/GYMTERNET_IMPORT_DECISION_MEMORY.md
```

## Report presenti

| File | Descrizione |
|---|---|
| `gymternet_2018_athlete_collision_review.csv` | Review finale semplificata delle 48 collisioni atleta/country 2018. |
| `gymternet_2018_name_order_audit.csv` | Audit dei 15 merge automatici name-order rilevati durante la review 2018. |
| `gymternet_2018_orphan_dscores.csv` | D-score del file Gymternet 2018 non agganciati automaticamente a un result con final score. Sono stati lasciati fuori dal database operativo, ma conservati per review futura. |
| `gymternet_2019_preview_summary.json` | Sintesi tecnica della preview 2019 eseguita sul DB post-2018, senza commit. |
| `gymternet_2019_athlete_match_decisions.json` | Payload tecnico generato dalle decisioni admin 2019. Aggiornato dopo la risoluzione dei conflitti post-decisione. |
| `gymternet_2019_preview_with_decisions_summary.json` | Preview 2019 eseguita con decisioni admin applicate su copia temporanea del DB, senza modificare `leverage.db`. |
| `gymternet_2019_commit_summary.json` | Report tecnico del commit reale 2019, con backup, statistiche di import e controlli post-import. |
| `gymternet_2019_post_decision_conflicts.csv` | Audit dei conflitti post-decisione 2019. Inizialmente conteneva 24 conflitti; dopo le decisioni admin `keep separate`, e stato rigenerato vuoto e non blocca piu il commit. |
| `gymternet_2019_orphan_dscores.csv` | D-score del file Gymternet 2019 non agganciati automaticamente a un result con final score. |
| `gymternet_2019_athlete_review.csv` | Review atleta/country 2019 completa e tecnica. Conservata come report aggregato di riferimento. |
| `gymternet_2019_existing_athlete_match_review.csv` | CSV operativo principale per verificare se un atleta importato nel 2019 corrisponde a un atleta gia presente nel DB 2018. Include le gare 2018 dell'atleta gia esistente. |
| `gymternet_2019_existing_athlete_repeat_audit.csv` | Audit delle righe 2019 in cui lo stesso atleta gia esistente viene suggerito piu volte per varianti di nome/country. |
| `gymternet_2019_new_athlete_country_conflicts.csv` | CSV operativo separato per nuovi atleti 2019 che presentano solo conflitti di country nel file 2019. Completato dall'admin e convertito da Numbers il 25 giugno 2026. |
| `gymternet_2020_preview_summary.json` | Sintesi tecnica della preview 2020 eseguita sul DB post-2019, senza commit. |
| `gymternet_2020_duplicates.csv` | Audit dei 5 duplicati identici interni al file 2020. |
| `gymternet_2020_conflicts.csv` | Audit dei conflitti bloccanti 2020; attualmente vuoto. |
| `gymternet_2020_orphan_dscores.csv` | D-score del file Gymternet 2020 non agganciati automaticamente a un result con final score. |
| `gymternet_2020_athlete_review.csv` | Review atleta/country 2020 completa e tecnica. |
| `gymternet_2020_existing_athlete_match_review.csv` | CSV operativo per verificare se un atleta importato nel 2020 corrisponde a un atleta gia presente nel DB post-2019. |
| `gymternet_2020_new_athlete_country_conflicts.csv` | CSV operativo separato per nuovi atleti 2020 che presentano conflitti country nel file 2020. |
| `gymternet_2020_athlete_match_decisions.json` | Payload tecnico generato dalle decisioni admin 2020. Aggiornato dopo la risoluzione del caso Nao/Kaho Kobayashi con `keep separate`. |
| `gymternet_2020_preview_with_decisions_summary.json` | Preview 2020 eseguita con decisioni admin applicate, senza commit. |
| `gymternet_2020_post_decision_conflicts.csv` | Audit dei conflitti post-decisione 2020. Rigenerato vuoto dopo l'applicazione della regola `same_context_different_score_keep_separate`. |
| `gymternet_2020_post_decision_duplicates.csv` | Audit dei 5 duplicati identici residui dopo le decisioni 2020. |
| `gymternet_2020_commit_summary.json` | Report tecnico del commit reale 2020, con backup, statistiche di import e controlli post-import. |
| `gymternet_2021_preview_summary.json` | Sintesi tecnica della preview 2021 eseguita sul DB post-2020, senza commit. |
| `gymternet_2021_duplicates.csv` | Audit dei duplicati identici interni al file 2021; attualmente vuoto. |
| `gymternet_2021_conflicts.csv` | Audit dei conflitti bloccanti 2021; attualmente vuoto. |
| `gymternet_2021_orphan_dscores.csv` | D-score del file Gymternet 2021 non agganciati automaticamente a un result con final score. |
| `gymternet_2021_athlete_review.csv` | Review atleta/country 2021 completa e tecnica. |
| `gymternet_2021_existing_athlete_match_review.csv` | CSV operativo per verificare se un atleta importato nel 2021 corrisponde a un atleta gia presente nel DB post-2020. |
| `gymternet_2021_new_athlete_country_conflicts.csv` | CSV operativo separato per nuovi atleti 2021 che presentano conflitti country nel file 2021. |
| `gymternet_2021_athlete_name_corrections.csv` | Correzioni nome atleta esistente verificate dall'admin durante la review 2021. |
| `gymternet_2021_athlete_match_decisions.json` | Payload tecnico generato dalle decisioni admin 2021, incluse 5 correzioni nome atleta. |
| `gymternet_2021_preview_with_decisions_summary.json` | Preview 2021 eseguita con decisioni admin applicate, senza commit. |
| `gymternet_2021_post_decision_conflicts.csv` | Audit dei conflitti post-decisione 2021. Inizialmente conteneva 4 conflitti; dopo le decisioni `keep separate` e stato rigenerato vuoto. |
| `gymternet_2021_post_decision_duplicates.csv` | Audit dei duplicati identici residui dopo le decisioni 2021; vuoto. |
| `gymternet_2021_commit_summary.json` | Report tecnico del commit reale 2021, con backup, statistiche di import e controlli post-import. |
| `gymternet_2022_preview_summary.json` | Sintesi tecnica della preview 2022 eseguita sul DB post-2021, senza commit. |
| `gymternet_2022_duplicates.csv` | Audit dei 3 duplicati identici interni al file 2022. |
| `gymternet_2022_conflicts.csv` | Audit dei conflitti bloccanti 2022; attualmente vuoto. |
| `gymternet_2022_orphan_dscores.csv` | D-score del file Gymternet 2022 non agganciati automaticamente a un result con final score. |
| `gymternet_2022_athlete_review.csv` | Review atleta/country 2022 completa e tecnica. |
| `gymternet_2022_existing_athlete_match_review.csv` | CSV operativo per verificare se un atleta importato nel 2022 corrisponde a un atleta gia presente nel DB post-2021. |
| `gymternet_2022_new_athlete_country_conflicts.csv` | CSV operativo separato per nuovi atleti 2022 che presentano conflitti country nel file 2022. |
| `gymternet_2022_athlete_match_decisions.json` | Payload tecnico generato dalle decisioni admin 2022. Aggiornato dopo la risoluzione del caso Liu Xuanxi/Liu Xuan con `keep separate`. |
| `gymternet_2022_preview_with_decisions_summary.json` | Preview 2022 eseguita con decisioni admin applicate su copia temporanea del DB, senza modificare `leverage.db`. |
| `gymternet_2022_post_decision_conflicts.csv` | Audit dei conflitti post-decisione 2022. Inizialmente conteneva 7 conflitti Liu Xuanxi/Liu Xuan; dopo la decisione `keep separate` e stato rigenerato vuoto. |
| `gymternet_2022_post_decision_duplicates.csv` | Audit dei 3 duplicati identici residui dopo le decisioni 2022. |
| `gymternet_2022_commit_summary.json` | Report tecnico del commit reale 2022, con backup, statistiche di import e controlli post-import. |
| `gymternet_2023_preview_summary.json` | Sintesi tecnica della preview 2023 eseguita sul DB post-2022, senza commit. |
| `gymternet_2023_duplicates.csv` | Audit dei duplicati identici interni al file 2023; attualmente vuoto. |
| `gymternet_2023_conflicts.csv` | Audit dei conflitti bloccanti 2023; attualmente vuoto. |
| `gymternet_2023_orphan_dscores.csv` | D-score del file Gymternet 2023 non agganciati automaticamente a un result con final score. |
| `gymternet_2023_athlete_review.csv` | Review atleta/country 2023 completa e tecnica. |
| `gymternet_2023_existing_athlete_match_review.csv` | CSV operativo per verificare se un atleta importato nel 2023 corrisponde a un atleta gia presente nel DB post-2022. |
| `gymternet_2023_new_athlete_country_conflicts.csv` | CSV operativo separato per nuovi atleti 2023 che presentano conflitti country nel file 2023. |
| `gymternet_2023_athlete_name_corrections.csv` | Correzioni nome atleta esistente verificate durante la review 2023, incluse correzioni `Niccolò`, `Nico Olivieri` e normalizzazioni KOR. |
| `gymternet_2023_athlete_match_decisions.json` | Payload tecnico generato dalle decisioni admin 2023, incluse 39 correzioni nome atleta. |
| `gymternet_2023_preview_with_decisions_summary.json` | Preview 2023 eseguita con decisioni admin applicate su copia temporanea del DB, senza modificare `leverage.db`. |
| `gymternet_2023_post_decision_conflicts.csv` | Audit dei conflitti post-decisione 2023. Inizialmente conteneva 9 conflitti; dopo le decisioni `keep separate` e stato rigenerato vuoto. |
| `gymternet_2023_post_decision_duplicates.csv` | Audit dei duplicati identici residui dopo le decisioni 2023; vuoto. |
| `gymternet_2023_commit_summary.json` | Report tecnico del commit reale 2023, con backup, statistiche di import e controlli post-import. |
| `gymternet_2024_preview_summary.json` | Sintesi tecnica della preview 2024 eseguita sul DB post-2023, senza commit. |
| `gymternet_2024_duplicates.csv` | Audit dei duplicati identici interni al file 2024; attualmente vuoto. |
| `gymternet_2024_conflicts.csv` | Audit dei conflitti bloccanti 2024; attualmente vuoto. |
| `gymternet_2024_orphan_dscores.csv` | D-score del file Gymternet 2024 non agganciati automaticamente a un result con final score. |
| `gymternet_2024_athlete_review.csv` | Review atleta/country 2024 completa e tecnica. |
| `gymternet_2024_existing_athlete_match_review.csv` | CSV operativo per verificare se un atleta importato nel 2024 corrisponde a un atleta gia presente nel DB post-2023. Include decisioni same-country precompilate quando la memoria storica e univoca. |
| `gymternet_2024_new_athlete_country_conflicts.csv` | CSV operativo separato per nuovi atleti 2024 che presentano conflitti country nel file 2024. |
| `gymternet_2024_athlete_match_decisions.json` | Payload tecnico delle decisioni admin 2024, rigenerato dopo la correzione post-preview dei tre merge rischiosi. |
| `gymternet_2024_preview_with_decisions_summary.json` | Sintesi tecnica della preview 2024 con decisioni admin applicate; esito finale pulito con 0 duplicati e 0 conflitti. |
| `gymternet_2024_post_decision_conflicts.csv` | Audit conflitti dopo decisioni admin; vuoto dopo la correzione finale. |
| `gymternet_2024_post_decision_duplicates.csv` | Audit duplicati dopo decisioni admin; vuoto. |
| `gymternet_2024_commit_summary.json` | Report tecnico del commit reale 2024, con backup, statistiche di import e controlli post-import. |
| `gymternet_2025_preview_summary.json` | Sintesi tecnica della preview 2025 eseguita sul DB post-2024, senza commit. |
| `gymternet_2025_duplicates.csv` | Audit dei duplicati identici interni al file 2025; attualmente vuoto. |
| `gymternet_2025_conflicts.csv` | Audit dei conflitti bloccanti 2025; attualmente vuoto. |
| `gymternet_2025_orphan_dscores.csv` | D-score del file Gymternet 2025 non agganciati automaticamente a un result con final score. |
| `gymternet_2025_athlete_review.csv` | Review atleta/country 2025 completa e tecnica. |
| `gymternet_2025_existing_athlete_match_review.csv` | CSV operativo per verificare se un atleta importato nel 2025 corrisponde a un atleta gia presente nel DB post-2024. Include decisioni same-country precompilate quando la memoria storica e univoca. |
| `gymternet_2025_new_athlete_country_conflicts.csv` | CSV operativo separato per nuovi atleti 2025 che presentano conflitti country nel file 2025. |
| `gymternet_2025_athlete_name_corrections.csv` | Correzione nome atleta esistente verificata durante la review 2025: `Niccolo Martin` -> `Niccolò Martin`. |
| `gymternet_2025_athlete_match_decisions.json` | Payload tecnico generato dalle decisioni admin 2025, inclusa 1 correzione nome atleta. |
| `gymternet_2025_preview_with_decisions_summary.json` | Preview 2025 eseguita con decisioni admin applicate; esito finale pulito con 0 duplicati e 0 conflitti. |
| `gymternet_2025_post_decision_conflicts.csv` | Audit dei conflitti post-decisione 2025. Inizialmente conteneva 33 conflitti; dopo le decisioni `keep separate` e stato rigenerato vuoto. |
| `gymternet_2025_post_decision_duplicates.csv` | Audit dei duplicati identici residui dopo le decisioni 2025; vuoto. |
| `gymternet_2025_commit_summary.json` | Report tecnico del commit reale 2025, con backup, statistiche di import e controlli post-import. |

## Report calendario eventi

I report calendario vengono generati anno per anno a partire dal file `Calendar.xlsx` fornito da Gymternet. Lo scopo e allineare le date degli `Event` gia creati durante il popolamento storico dei `Result`, senza creare automaticamente righe storiche dubbie.

Per ogni anno possono essere prodotti:

- `calendar_<anno>_event_match_review.csv`: righe calendario storiche che non trovano una corrispondenza diretta nel DB, con suggerimenti di possibili `Event` da associare;
- `calendar_<anno>_event_match_review_slim.csv`: versione operativa semplificata del file precedente, pensata per la review admin;
- `calendar_<anno>_db_unmatched_events.csv`: eventi gia presenti nel DB per quell'anno che non risultano coperti da alcuna riga calendario;
- `calendar_<anno>_source_conflicts.csv`: casi in cui piu righe calendario puntano allo stesso `Event` DB con date diverse;
- `calendar_<anno>_source_conflicts_slim.csv`: versione operativa semplificata dei conflitti stesso Event/date diverse;
- `calendar_<anno>_match_summary.csv`: riepilogo numerico bidirezionale dei match/mismatch.
- `calendar_<anno>_dry_run_summary.json`: simulazione del commit calendario per l'anno;
- `calendar_<anno>_commit_summary.json`: report del commit reale delle date applicate agli `Event`.

Regola semantica calendario aggiunta il 1 luglio 2026: nei nomi evento, `MAG` viene trattato come indizio di gara maschile e puo corrispondere a varianti DB con `Men's`/`Mens`; analogamente `WAG` puo corrispondere a varianti con `Women's`/`Womens`.

Per il 2018, dopo questa normalizzazione, il riepilogo e:

| Controllo | Conteggio |
|---|---:|
| Righe calendar 2018 | 214 |
| Righe calendar matchate | 205 |
| Righe calendar senza match diretto | 9 |
| Event DB 2018 | 211 |
| Event DB matchati | 197 |
| Event DB senza match calendar | 14 |
| Event DB senza match calendar con result | 14 |
| Event DB matchati da piu righe calendar | 8 |
| Conflitti stesso Event DB / date diverse | 8 |

Interpretazione: i due lati del mismatch non devono necessariamente essere identici, perche una riga calendario puo rappresentare una gara combinata MAG/WAG oppure piu righe calendario possono puntare allo stesso evento DB, specialmente quando nel DB storico l'evento era stato creato come `MAG and WAG`.

Il commit calendario anno-per-anno e supportato dallo script:

```text
scripts/commit_calendar_year.py
```

Lo script applica automaticamente solo i match sicuri e aggiorna i campi `start_date` / `end_date` degli `Event` associati. I mismatch e i conflitti MAG/WAG restano in review finche l'admin non compila i CSV.

Quando una riga calendar o un conflitto indica piu opzioni valide, per esempio `choice = 1 and 2`, lo script non forza una data unica nel record `Event`. In questi casi crea invece record `EventCalendarEntry`, cioe voci calendario separate che possono puntare alla stessa scheda Event.

Per la review manuale si usano preferibilmente i file `_slim.csv`.

Nel file `calendar_<anno>_event_match_review_slim.csv`:

- `choice = 1`, `2` o `3`: associa la riga calendario alla relativa opzione suggerita e aggiorna `start_date` / `end_date` dell'Event;
- `manual_event_id`: permette di indicare manualmente un Event non presente tra le opzioni;
- `choice = calendar_only`: mantiene la riga come voce calendario non collegata a una scheda Event;
- `notes`: motivazione o dettaglio della decisione.

Nel file `calendar_<anno>_source_conflicts_slim.csv`:

- `choice = 1`, `2`, ecc.: sceglie quale data calendario usare per l'Event DB indicato;
- `choice = calendar_only` o `ignore`: non aggiorna l'Event DB e lascia il caso fuori dal collegamento alla scheda evento;
- `notes`: motivazione, soprattutto quando MAG/WAG sono righe distinte ma l'Event DB e `MAG and WAG`.

Primo commit calendario 2018:

| Controllo | Conteggio |
|---|---:|
| Match sicuri applicati | 189 |
| Decisioni admin slim applicate | 10 |
| Conflitti stesso Event/date risolti | 8 |
| Event 2018 con date dopo commit | 196 |
| Event 2018 ancora senza date | 15 |
| Calendar entries 2018 create | 26 |
| Elementi review aperti | 0 |

Report:

- `calendar_2018_dry_run_summary.json`
- `calendar_2018_commit_summary.json`

Secondo controllo calendario 2018:

Il primo giro aveva correttamente gestito i casi MAG/WAG multi-data, ma il controllo successivo ha imposto una regola piu stretta: per un foglio Calendar di un anno, i suggerimenti devono riferirsi solo a `Event.year` dello stesso anno. Questo evita collegamenti cross-year come una riga Calendar 2018 associata a un Event DB 2019.

Script introdotti:

```text
scripts/generate_calendar_current_coverage_reports.py
scripts/apply_calendar_current_review_decisions.py
```

Report 2018 generati:

- `calendar_2018_calendar_unmatched_current.csv`
- `calendar_2018_db_unmatched_current.csv`
- `calendar_2018_cross_year_calendar_entries.csv`
- `calendar_2018_current_review_dry_run_summary.json`
- `calendar_2018_current_review_commit_summary.json`

Esito finale 2018 dopo review corrente:

| Controllo | Conteggio |
|---|---:|
| Righe Calendar 2018 | 214 |
| Event DB 2018 | 211 |
| Calendar 2018 senza match finale | 0 |
| Event DB 2018 senza match finale | 0 |
| Collegamenti cross-year finali | 0 |
| Event 2018 aggiornati nel secondo giro | 6 |
| Calendar entries create nel secondo giro | 5 |
| Calendar entries rilinkate da anno errato | 1 |

Primo checkpoint calendario 2019:

| Controllo | Conteggio |
|---|---:|
| Righe Calendar 2019 | 244 |
| Event DB 2019 | 233 |
| Match diretti sicuri applicati | 215 |
| Event 2019 aggiornati con date | 214 |
| Elementi review aperti dopo commit sicuro | 21 |
| Calendar 2019 senza match corrente | 13 |
| Event DB 2019 senza match corrente | 11 |
| Conflitti stesso Event/date diverse | 8 |
| Collegamenti cross-year rilevati | 0 |

Per la review 2019 si usano:

- `calendar_2019_calendar_unmatched_current.csv`
- `calendar_2019_db_unmatched_current.csv`
- `calendar_2019_source_conflicts_slim.csv`

Il principio resta identico al controllo finale 2018: ogni review del Calendar di un anno deve proporre e applicare soltanto Event DB dello stesso anno.

Esito review corrente calendario 2019:

| Controllo | Conteggio |
|---|---:|
| Righe Calendar 2019 | 244 |
| Event DB 2019 | 233 |
| Event DB 2019 coperti dal Calendar | 233 |
| Event DB 2019 senza copertura Calendar | 0 |
| Righe Calendar 2019 ancora da risolvere | 0 |
| Righe Calendar 2019 `calendar_only` senza scheda Event | 2 |
| Collegamenti cross-year finali | 0 |
| Conflitti stesso Event/date risolti | 8 |
| Calendar entries 2019 complessive create/aggiornate in review | 32 |

Le due righe Calendar 2019 senza Event DB collegato sono state chiuse come `calendar_only`: `Zelena Jama Open` e `Brazilian Junior Championships`. Il file `Results 2019.xlsx` e stato controllato direttamente e non contiene risultati sorgente riconducibili a questi due eventi; potrebbero quindi essere gare non svolte oppure gare senza result sorgente disponibile.

Regola metodologica aggiunta durante la chiusura 2019: la riuscita del matching Calendar non richiede che ogni riga Calendar abbia una scheda Event collegata. La metrica critica e che tutti gli Event DB ricavati dai Result abbiano copertura Calendar oppure una review esplicita admin se il Calendar sorgente non contiene la gara. Le righe Calendar senza Result possono restare come `calendar_only` e comparire in UI come voci non cliccabili verso una scheda evento.

Regola tecnica rafforzata durante la chiusura 2019: se una decisione manuale collega una riga Calendar aggiuntiva a un Event che ha gia date canoniche valide, il sistema non sovrascrive `Event.start_date` / `Event.end_date`; conserva la data principale dell'Event e rappresenta la riga aggiuntiva con `EventCalendarEntry`.

Regola tecnica aggiunta durante la chiusura 2020: `season_year_spillover` indica una eccezione controllata in cui l'Event DB appartiene a una stagione/anno diverso dal foglio Calendar in cui cade la data reale. Il caso guida e `1st Spanish League (2020 season)`: `Event.year=2020`, ma data reale Dec 7-8 2019 nel Calendar 2019.

Primo checkpoint calendario 2020:

| Controllo | Conteggio |
|---|---:|
| Righe Calendar 2020 | 90 |
| Event DB 2020 | 77 |
| Match diretti sicuri applicati | 68 |
| Event 2020 aggiornati con date | 68 |
| Elementi review aperti dopo commit sicuro | 19 |
| Calendar 2020 senza match corrente | 16 |
| Event DB 2020 senza match corrente | 6 |
| Conflitti stesso Event/date diverse | 3 |
| Collegamenti cross-year rilevati | 0 |

Per la review 2020 si usano:

- `calendar_2020_calendar_unmatched_current.csv`
- `calendar_2020_db_unmatched_current.csv`
- `calendar_2020_source_conflicts_slim.csv`

Il criterio resta quello definito a fine 2019: l'obiettivo essenziale e coprire tutti gli Event DB ricavati dai Result oppure marcarli con review esplicita admin se il Calendar sorgente non contiene la gara. Le righe Calendar senza Result possono essere chiuse come `calendar_only`.

Esito finale calendario 2020:

| Controllo | Conteggio |
|---|---:|
| Righe Calendar 2020 | 90 |
| Event DB 2020 | 77 |
| Event DB 2020 coperti dal Calendar | 77 |
| Event DB 2020 senza copertura Calendar | 0 |
| Righe Calendar 2020 ancora da risolvere | 0 |
| Righe Calendar 2020 `calendar_only` senza scheda Event | 2 |
| Collegamenti `season_year_spillover` | 1 |
| Collegamenti cross-year non controllati | 0 |
| Conflitti stesso Event/date risolti | 3 |

Le due righe Calendar 2020 chiuse come `calendar_only` sono `Stella Zakharova Cup` e `Hungarian Master Championships`.

## Calendar 2021 - checkpoint review

Il flusso 2021 e stato avviato con la stessa procedura usata per gli anni precedenti: match automatici solo quando sicuri, backup locale del DB prima della scrittura, poi review admin dei casi rimasti aperti.

| Controllo | Conteggio |
|---|---:|
| Righe Calendar 2021 | 210 |
| Event DB 2021 | 196 |
| Match diretti sicuri applicati | 163 |
| Event DB 2021 gia coperti | 172 |
| Calendar 2021 senza match corrente | 29 |
| Event DB 2021 senza match corrente | 24 |
| Conflitti stesso Event/date da rivedere | 9 |
| Righe Calendar 2021 `calendar_only` | 0 |
| Collegamenti `season_year_spillover` | 1 |
| Collegamenti cross-year non controllati | 0 |

Backup del primo commit sicuro 2021:

```text
backups/leverage_calendar_2021_20260701_232721.db
```

File operativi da compilare:

- `calendar_2021_calendar_unmatched_current.csv`
- `calendar_2021_db_unmatched_current.csv`
- `calendar_2021_source_conflicts_slim.csv`

La review 2021 deve continuare a seguire la regola metodologica gia fissata: ogni Event DB derivato dai Result deve avere copertura Calendar oppure review esplicita admin come `db_only`; una riga Calendar senza Event DB puo invece restare solo calendario tramite `calendar_only` se non esiste un Result sorgente collegabile.

Esito finale calendario 2021:

| Controllo | Conteggio |
|---|---:|
| Righe Calendar 2021 | 210 |
| Event DB 2021 | 196 |
| Event DB 2021 coperti o verificati | 196 |
| Event DB 2021 senza copertura/review Calendar | 0 |
| Righe Calendar 2021 ancora da risolvere | 0 |
| Righe Calendar 2021 `calendar_only` senza scheda Event | 1 |
| Event DB 2021 `db_only` assenti dal Calendar sorgente | 1 |
| Collegamenti `season_year_spillover` | 0 |
| Collegamenti cross-year non controllati | 0 |
| Conflitti stesso Event/date risolti | 9 |

La riga `calendar_only` 2021 e `Oceania Championships`. L'Event `db_only` 2021 e `RomGym Trophy`, ricavato dai Result ma non presente nel Calendar sorgente.

Regola metodologica aggiunta durante la chiusura 2021: un Event DB ricavato dai Result puo non comparire nel Calendar sorgente. In questo caso non si forza un'associazione artificiale; dopo verifica admin viene registrato come `db_only`, resta consultabile come scheda Event/Result, ma non viene usato come voce del calendario interattivo finche non esiste una data sorgente affidabile.

## Calendar 2022 - checkpoint review

Il flusso 2022 e stato avviato dopo l'introduzione della regola `db_only`. I match diretti sicuri sono stati applicati, mentre i casi non certi sono stati lasciati nei CSV di review admin.

| Controllo | Conteggio |
|---|---:|
| Righe Calendar 2022 | 228 |
| Event DB 2022 | 215 |
| Match diretti sicuri applicati | 202 |
| Event DB 2022 gia coperti | 209 |
| Calendar 2022 senza match corrente | 12 |
| Event DB 2022 senza match corrente | 6 |
| Event DB 2022 `db_only` gia verificati | 0 |
| Righe Calendar 2022 `calendar_only` | 0 |
| Conflitti stesso Event/date da rivedere | 7 |
| Collegamenti `season_year_spillover` | 0 |
| Collegamenti cross-year non controllati | 0 |

Backup del primo commit sicuro 2022:

```text
backups/leverage_calendar_2022_20260702_001613.db
```

File operativi da compilare:

- `calendar_2022_calendar_unmatched_current.csv`
- `calendar_2022_db_unmatched_current.csv`
- `calendar_2022_source_conflicts_slim.csv`

La review 2022 deve usare gli stessi valori operativi del 2021: scelta numerica o `manual_event_id` quando esiste un collegamento Calendar/Event, `calendar_only` per righe Calendar senza Event DB, `db_only` per Event DB ricavati dai Result ma assenti dal Calendar sorgente.

Esito finale calendario 2022:

| Controllo | Conteggio |
|---|---:|
| Righe Calendar 2022 | 228 |
| Event DB 2022 | 215 |
| Event DB 2022 coperti o verificati | 215 |
| Event DB 2022 senza copertura/review Calendar | 0 |
| Righe Calendar 2022 ancora da risolvere | 0 |
| Righe Calendar 2022 `calendar_only` senza scheda Event | 0 |
| Event DB 2022 `db_only` assenti dal Calendar sorgente | 0 |
| Collegamenti `season_year_spillover` | 0 |
| Collegamenti cross-year non controllati | 0 |
| Conflitti stesso Event/date risolti | 7 |

Nota di review: `EYOF Mixed Pairs` e stato collegato alla riga Calendar 142, `European Youth Olympic Festival`. Il 2022 si chiude senza eccezioni `calendar_only` o `db_only`. Durante la review 2023, la riga Calendar 2022 n. 205, `1st Spanish League – 2023 season`, e stata rilinkata all'Event 2023 `1st Spanish League 2023` come `season_year_spillover`; la copertura 2022 resta completa.

## Calendar 2023 - checkpoint review

Il flusso 2023 e stato avviato applicando solo i match diretti sicuri. I casi ambigui, inclusi quelli con etichetta `2024 season` ma data nel 2023, sono lasciati alla review admin.

| Controllo | Conteggio |
|---|---:|
| Righe Calendar 2023 | 265 |
| Event DB 2023 | 241 |
| Match diretti sicuri applicati | 211 |
| Event DB 2023 gia coperti | 223 |
| Calendar 2023 senza match corrente | 39 |
| Event DB 2023 senza match corrente | 18 |
| Event DB 2023 `db_only` gia verificati | 0 |
| Righe Calendar 2023 `calendar_only` | 0 |
| Conflitti stesso Event/date da rivedere | 6 |
| Righe saltate per piu match possibili | 3 |
| Collegamenti `season_year_spillover` | 0 |
| Collegamenti cross-year non controllati | 0 |

Backup del primo commit sicuro 2023:

```text
backups/leverage_calendar_2023_20260702_003617.db
```

File operativi da compilare:

- `calendar_2023_calendar_unmatched_current.csv`
- `calendar_2023_db_unmatched_current.csv`
- `calendar_2023_source_conflicts_slim.csv`

La review 2023 usa gli stessi valori operativi: scelta numerica o `manual_event_id` quando esiste un collegamento Calendar/Event, `calendar_only` per righe Calendar senza Event DB, `db_only` per Event DB ricavati dai Result ma assenti dal Calendar sorgente.

Pulizia sorgente 2023: dopo il checkpoint iniziale, il file `Calendar.xlsx` e stato corretto per rimuovere URL rimasti nel testo visibile di alcune righe `Finnish National Team Test`. Solo il foglio 2023 presenta differenze rispetto alla versione precedente; i conteggi di matching sono rimasti invariati e i CSV 2023 sono stati rigenerati con nomi gara puliti.

Esito finale calendario 2023:

| Controllo | Conteggio |
|---|---:|
| Righe Calendar 2023 | 265 |
| Event DB 2023 | 241 |
| Event DB 2023 coperti o verificati | 241 |
| Event DB 2023 senza copertura/review Calendar | 0 |
| Righe Calendar 2023 ancora da risolvere | 0 |
| Righe Calendar 2023 `calendar_only` senza scheda Event | 13 |
| Event DB 2023 `db_only` assenti dal Calendar sorgente | 1 |
| Collegamenti `season_year_spillover` | 7 |
| Collegamenti cross-year non controllati | 0 |
| Conflitti stesso Event/date risolti | 6 |

Note di review 2023:

- `EYOF Mixed Pairs` e stato collegato alla riga Calendar 151, `European Youth Olympic Festival`;
- `1st Spanish League 2023` e stato collegato alla riga Calendar 2022 n. 205 come `season_year_spillover`;
- sei righe Calendar 2023 riferite alla stagione 2024 sono state collegate agli Event DB 2024 corrispondenti come `season_year_spillover`;
- `German Worlds Trials 2` e stato chiuso come `db_only`;
- `Top 12 Series 3 (MAG) (2024 season)` e stata chiusa come `calendar_only`.

## Calendar 2024 - checkpoint review

Il flusso 2024 e stato avviato considerando gia validi i sei collegamenti `season_year_spillover` provenienti dalla review 2023. I match diretti sicuri sono stati applicati, mentre i casi ambigui sono stati lasciati nei CSV di review admin.

| Controllo | Conteggio |
|---|---:|
| Righe Calendar 2024 | 222 |
| Event DB 2024 | 207 |
| Match diretti sicuri applicati | 192 |
| Event DB 2024 gia coperti | 198 |
| Calendar 2024 senza match corrente | 18 |
| Event DB 2024 senza match corrente | 9 |
| Event DB 2024 `db_only` gia verificati | 0 |
| Righe Calendar 2024 `calendar_only` | 0 |
| Conflitti stesso Event/date da rivedere | 6 |
| Collegamenti `season_year_spillover` | 6 |
| Collegamenti cross-year non controllati | 0 |

Backup del primo commit sicuro 2024:

```text
backups/leverage_calendar_2024_20260702_012421.db
```

File operativi da compilare:

- `calendar_2024_calendar_unmatched_current.csv`
- `calendar_2024_db_unmatched_current.csv`
- `calendar_2024_source_conflicts_slim.csv`

La review 2024 usa gli stessi valori operativi: scelta numerica o `manual_event_id` quando esiste un collegamento Calendar/Event, `calendar_only` per righe Calendar senza Event DB, `db_only` per Event DB ricavati dai Result ma assenti dal Calendar sorgente.

Esito finale calendario 2024:

| Controllo | Conteggio |
|---|---:|
| Righe Calendar 2024 | 222 |
| Event DB 2024 | 207 |
| Event DB 2024 coperti o verificati | 207 |
| Event DB 2024 senza copertura/review Calendar | 0 |
| Righe Calendar 2024 ancora da risolvere | 0 |
| Righe Calendar 2024 `calendar_only` senza scheda Event | 2 |
| Event DB 2024 `db_only` assenti dal Calendar sorgente | 0 |
| Collegamenti `season_year_spillover` | 6 |
| Collegamenti cross-year non controllati | 0 |
| Conflitti stesso Event/date risolti | 6 |

Le due righe `calendar_only` 2024 sono `Israeli Championships` e `Japanese National Sports Festival`. Il 2024 si chiude senza Event DB `db_only`.

## Convenzione review atleta/country

Nei CSV semplificati:

- `decision`: usare `merge as same athlete` oppure `keep separate`;
- `action`: usare `canonical country` se una country e un errore da correggere, oppure `country history` se si tratta di storico/cambio country;
- `country`: country corretta nel caso `canonical country`, oppure country finale/corrente nel caso `country history`.
- `future_country_evidence`: mostra la country rappresentata negli anni successivi. Nel CSV 2019 copre 2020-2025; nel CSV 2018 copre 2019-2025.

Per la review manuale 2019 si usano preferibilmente i due CSV separati:

- `gymternet_2019_existing_athlete_match_review.csv`: casi in cui il sistema suggerisce un possibile collegamento tra atleta importato 2019 e atleta gia presente dal 2018;
- `gymternet_2019_new_athlete_country_conflicts.csv`: casi in cui il nuovo atleta 2019 ha country discordanti all'interno del file 2019.

Nel primo CSV la colonna `existing_athlete_2018_results_by_country` mostra le gare 2018 dell'atleta gia salvato nel DB, cosi l'admin puo valutare se si tratta dello stesso atleta o di due atleti diversi.

Nel CSV `gymternet_2019_new_athlete_country_conflicts.csv`, i valori inseriti come `Merge` e `Correct` nel file Numbers sono stati normalizzati rispettivamente in `merge as same athlete` e `canonical country`.

Nel CSV `gymternet_2019_existing_athlete_match_review.csv`, i valori inseriti come `Merge`, `Separate`, `Correct`, `History` e `Histroy` nel file Numbers sono stati normalizzati rispettivamente in `merge as same athlete`, `keep separate`, `canonical country` e `country history`.

Nel CSV `gymternet_2020_existing_athlete_match_review.csv`, i valori inseriti come `Merge`, `Separate`, `Correct` e `History` nel file Numbers sono stati normalizzati rispettivamente in `merge as same athlete`, `keep separate`, `canonical country` e `country history`.

Nel CSV `gymternet_2020_new_athlete_country_conflicts.csv`, il refuso `Corrrect` inserito nel file Numbers e stato normalizzato in `canonical country`.

Nel flusso 2021 e stato introdotto il supporto a `target_name_update`: quando l'ADMIN conferma che un atleta importato corrisponde a un atleta gia presente ma il nome salvato nel DB e errato, il commit puo correggere la scheda atleta esistente senza creare una nuova entita. I casi verificati sono documentati in `gymternet_2021_athlete_name_corrections.csv`.

Nel flusso 2022 i valori inseriti nei file Numbers sono stati trasferiti nei CSV operativi e normalizzati negli stessi valori tecnici degli anni precedenti. Dopo la preview post-decisione, il caso Liu Xuanxi/Liu Xuan e stato corretto manualmente in `keep separate` perche il merge produceva lo stesso contesto sportivo con score/D-score diversi.

La preview 2023 segnala uno spillover analogo a quello gia visto nel file 2022: `Results 2023.xlsx` contiene 1.092 record associati a eventi con anno 2024. La scelta metodologica resta usare l'anno evento dichiarato nel file sorgente.

Nel flusso 2023 sono state applicate 39 correzioni nome su atleti gia presenti nel DB. Per i nomi KOR, la normalizzazione e stata applicata quando riguardava trattino/spazio oppure quando l'evidenza futura sosteneva chiaramente la forma importata. I casi non univoci sono stati lasciati senza correzione automatica del nome.

Nel flusso 2024 i file Numbers compilati dall'admin sono stati trasferiti nei CSV operativi. La prima preview post-decisione ha rilevato 13 conflitti `same_context_different_score_after_athlete_merge`; applicando la regola persistente `same_context_different_score_keep_separate`, tre decisioni sono state corrette da `merge as same athlete` a `keep separate`: Max Griffiths/Mac Griffiths, Ania Fernandez/Jana Fernandez e Lee Seyeon/Lee Seoyeon. La preview finale 2024 e risultata pulita e il commit reale 2024 ha creato 106.449 result senza introdurre duplicati semantici.

La preview 2025 segnala uno spillover di 108 record associati a evento 2026 (`Top 12 Series 3 (2026)`). Come per gli anni precedenti, il sistema mantiene l'anno evento dichiarato nel file sorgente. Poiche il set storico disponibile termina al 2025, la colonna `future_country_evidence` non puo fornire evidenza successiva per la review 2025.

Nel flusso 2025 e stata applicata la correzione nome `Niccolo Martin` -> `Niccolò Martin`. La prima preview post-decisione ha rilevato 33 conflitti `same_context_different_score_after_athlete_merge`; applicando la regola persistente `same_context_different_score_keep_separate`, sette decisioni sono state corrette da `merge as same athlete` a `keep separate`: Saya Okubo/Aya Okubo, Anna Klykova/Anna Kalmykova, Mia Fujiwara/Mirea Fujiwara, Marta Garcia/Maria Garcia, Lee Sooyeon/Lee Seoyeon, Lee Jiyeon/Lee Jiseon e Zeng Yifan/Zeng Yiran. La preview finale 2025 e risultata pulita e il commit reale 2025 ha creato 124.030 result senza introdurre duplicati semantici.

Regola metodologica aggiunta durante la review 2019: se due atleti hanno stessa country, nome molto simile e l'evidenza degli anni successivi mostra che una variante non viene piu trovata, il sistema potra trattare il caso come merge automatico/candidato diretto, riducendo le review manuali future.

Regola metodologica aggiunta il 30 giugno 2026: le decisioni admin gia verificate sui casi `merge as same athlete` / `keep separate` possono essere riusate come raccomandazione forte solo quando il country non cambia. Nei CSV futuri il tool puo precompilare la decisione nei casi same-country gia controllati, indicando `same_country_review_reuse` come regola applicata. Se imported country e suggested/current country differiscono, la review manuale admin resta sempre obbligatoria.

Regola metodologica persistente: se una proposta di merge atleta produce lo stesso contesto sportivo di result ma con score o D-score diversi, il tool deve raccomandare `keep separate`. Nel backend questa regola e tracciata con `same_context_different_score_keep_separate`.

La generazione dei report annuali e supportata dallo script:

```text
scripts/generate_gymternet_preview_reports.py
```

Il flusso controllato post-review e supportato dagli script:

```text
scripts/apply_gymternet_review_decisions.py
scripts/preview_gymternet_with_decisions.py
scripts/commit_gymternet_year.py
```
