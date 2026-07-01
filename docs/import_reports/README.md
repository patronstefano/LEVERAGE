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
- `calendar_<anno>_db_unmatched_events.csv`: eventi gia presenti nel DB per quell'anno che non risultano coperti da alcuna riga calendario;
- `calendar_<anno>_source_conflicts.csv`: casi in cui piu righe calendario puntano allo stesso `Event` DB con date diverse;
- `calendar_<anno>_match_summary.csv`: riepilogo numerico bidirezionale dei match/mismatch.

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
