# LEVERAGE - Preview e review import 2019

Data creazione: 25 giugno 2026
File sorgente: `import_files/Results 2019.xlsx`
Stato: preview eseguita, nessun commit 2019 eseguito

---

## 1. Scopo

Questo documento registra la preview del file Gymternet 2019 eseguita sul database locale gia popolato con il 2018.

Obiettivo:

- verificare quanti result 2019 sono importabili;
- individuare D-score orfani;
- individuare possibili collisioni atleta/country;
- individuare possibili collegamenti con athlete gia presenti dal 2018;
- preparare la review admin prima del commit controllato 2019.

Nessun dato 2019 e stato scritto nel database.

---

## 2. File generati

| File | Scopo |
|---|---|
| `docs/import_reports/gymternet_2019_preview_summary.json` | Sintesi tecnica completa della preview 2019. |
| `docs/import_reports/gymternet_2019_orphan_dscores.csv` | D-score orfani non agganciati a un final score. |
| `docs/import_reports/gymternet_2019_athlete_review.csv` | Review atleta/country completa e tecnica, conservata come report aggregato. |
| `docs/import_reports/gymternet_2019_existing_athlete_match_review.csv` | CSV operativo per verificare i possibili collegamenti tra atleti importati 2019 e atleti gia presenti nel DB 2018. Include le gare 2018 dell'atleta gia esistente. |
| `docs/import_reports/gymternet_2019_new_athlete_country_conflicts.csv` | CSV operativo per i soli nuovi atleti 2019 che presentano conflitti di country. |

Backup pre-import:

```text
backups/leverage_pre_import_2019_2026-06-25.db
```

---

## 3. Sintesi preview 2019

| Voce | Conteggio |
|---|---:|
| Result parse dal file | 106.633 |
| Result potenzialmente importabili | 106.633 |
| Athlete che verrebbero creati senza decisioni admin | 4.576 |
| Event che verrebbero creati | 234 |
| Duplicati rilevati contro DB/file | 0 |
| Conflitti bloccanti | 0 |
| Warning | 2 |

Warning rilevati:

| Warning | Conteggio |
|---|---:|
| D-score non agganciati a final-score | 958 |
| Multi-day assegnati automaticamente | 77 chiavi, 154 righe con day valorizzato |

---

## 4. D-score orfani

Il file 2019 genera 958 D-score orfani.

| Problem type | Conteggio |
|---|---:|
| `athlete_missing_in_score_sheet` | 322 |
| `missing_final_score_for_context` | 228 |
| `possible_context_mismatch` | 201 |
| `possible_event_name_mismatch` | 147 |
| `possible_athlete_name_typo` | 53 |
| `missing_score_sheet_context` | 7 |

Di questi, 401 hanno almeno un suggerimento automatico di possibile aggancio.

Decisione metodologica proposta: come per il 2018, non importare i D-score orfani come result autonomi. Conservarli nel CSV dedicato per eventuale recupero futuro.

---

## 5. Review atleta/country

La preview 2019 genera 393 review atleta/country.

| Problem type | Conteggio |
|---|---:|
| `possible_existing_athlete_match` | 309 |
| `possible_athlete_identity_collision` | 64 |
| `possible_athlete_country_change` | 20 |

Triage operativa nel CSV:

| Review priority | Conteggio | Interpretazione |
|---|---:|---|
| `high` | 100 | Richiede verifica admin puntuale. Include collisioni country, country change e match con country diversa. |
| `bulk_candidate` | 92 | Possibile accettazione piu rapida dopo controllo a campione: match con stessa country e confidence >= 0.95. |
| `medium` | 201 | Match potenziale con confidence piu bassa o maggiore incertezza; va controllato prima del commit. |

Distribuzione confidence del miglior suggerimento:

| Confidence | Conteggio |
|---|---:|
| `>=0.95` | 145 |
| `0.90-0.949` | 176 |
| `<0.90/no suggestion` | 72 |

Flag country del miglior suggerimento:

| Flag | Conteggio |
|---|---:|
| `country_matches=True`, `requires_country_decision=False` | 293 |
| `country_matches=False`, `requires_country_decision=True` | 16 |
| Non applicabile a identity collision con suggerimento | 48 |

---

## 6. Come compilare i CSV operativi 2019

Per rendere piu veloce e affidabile la revisione admin, la review atleta/country 2019 viene divisa in due CSV operativi:

| File | Righe dati | Quando usarlo |
|---|---:|---|
| `gymternet_2019_existing_athlete_match_review.csv` | 377 | Quando il sistema propone che un atleta del 2019 possa corrispondere a un atleta gia presente nel DB dal 2018. |
| `gymternet_2019_new_athlete_country_conflicts.csv` | 16 | Quando l'atleta non e gia presente nel DB, ma nel file 2019 compaiono country diverse per lo stesso nome/disciplina. |

Il report completo `gymternet_2019_athlete_review.csv` resta come audit tecnico aggregato, ma la compilazione manuale dovrebbe avvenire sui due CSV separati.

Aggiornamento del 25 giugno 2026: il file `gymternet_2019_new_athlete_country_conflicts.numbers` compilato dall'admin e stato convertito nel CSV operativo `gymternet_2019_new_athlete_country_conflicts.csv`. Le 16 righe sono state completate e normalizzate nei valori tecnici usati dal backend:

| Valore inserito in Numbers | Valore CSV/backend |
|---|---|
| `Merge` | `merge as same athlete` |
| `Correct` | `canonical country` |

Esito: 16/16 nuovi conflitti country 2019 risultano compilati come `merge as same athlete` con correzione country canonica.

Aggiornamento del 25 giugno 2026: il file `gymternet_2019_existing_athlete_match_review.numbers` compilato dall'admin e stato analizzato e trasferito nel CSV operativo `gymternet_2019_existing_athlete_match_review.csv`, preservando dal CSV originale i dati tecnici non decisionali. Sono state importate dal Numbers solo le colonne `decision`, `action`, `country` e `notes`.

Esito della review atleti gia esistenti:

| Voce | Conteggio |
|---|---:|
| Righe controllate | 377 |
| `merge as same athlete` | 365 |
| `keep separate` | 12 |
| `canonical country` | 67 |
| `country history` | 9 |
| Decisioni invalide | 0 |
| Action/country incoerenti | 0 |

Normalizzazioni applicate:

| Valore inserito in Numbers | Valore CSV/backend |
|---|---|
| `Merge` | `merge as same athlete` |
| `Separate` | `keep separate` |
| `Correct` | `canonical country` |
| `History` / `Histroy` | `country history` |

Durante il controllo sono stati individuati 9 casi in cui lo stesso atleta gia esistente era suggerito in piu righe per varianti di nome o country. Non sono emersi `review_id` duplicati o blocchi tecnici. L'audit e stato salvato in `docs/import_reports/gymternet_2019_existing_athlete_repeat_audit.csv`.

Indicazione metodologica aggiunta per gli anni successivi: quando due record hanno stessa country, nome molto simile e l'evidenza post-anno mostra che una delle due varianti non compare piu (`not found`), il caso puo essere trattato come merge automatico/candidato diretto, senza richiedere necessariamente una review admin manuale.

### 6.1 Match con atleti gia presenti nel DB 2018

Il file `gymternet_2019_existing_athlete_match_review.csv` contiene colonne operative:

| Colonna | Uso |
|---|---|
| `imported_athlete_2019` | Nome e cognome dell'atleta letto nel file 2019. |
| `suggested_existing_athlete_id` | ID dell'atleta gia presente nel DB 2018 suggerito dal sistema. |
| `suggested_existing_athlete` | Nome dell'atleta gia presente nel DB 2018. |
| `suggested_existing_country` | Country corrente dell'atleta gia presente nel DB. |
| `imported_2019_results_by_country` | Gare 2019 dell'atleta importato, raggruppate per country. |
| `existing_athlete_2018_results_by_country` | Gare 2018 dell'atleta gia esistente nel DB, raggruppate per country. Questa colonna serve a valutare se l'atleta 2019 e davvero la stessa persona. |
| `future_country_evidence` | Country rappresentata negli anni successivi, dal 2020 al 2025. |
| `decision` | Inserire `merge as same athlete` oppure `keep separate`. |
| `action` | Se serve una scelta country, inserire `canonical country` oppure `country history`. |
| `country` | Se `action=canonical country`, inserire la country corretta. Se `action=country history`, inserire la country finale/corrente dell'atleta. |
| `notes` | Spazio libero per motivazione admin. |

### 6.2 Nuovi atleti 2019 con conflitto country

Il file `gymternet_2019_new_athlete_country_conflicts.csv` contiene colonne operative:

| Colonna | Uso |
|---|---|
| `athlete_name` | Nome e cognome dell'atleta da verificare. |
| `collision_countries` | Nazionalita/country coinvolte nella review. |
| `results_2019_by_country` | Gare 2019 associate alle diverse country. |
| `future_country_evidence` | Country rappresentata negli anni successivi, dal 2020 al 2025. |
| `decision` | Inserire `merge as same athlete` oppure `keep separate`. La cella inizialmente e vuota. |
| `action` | Se `decision=merge as same athlete`, inserire `canonical country` oppure `country history` quando serve una scelta country. |
| `country` | Se `action=canonical country`, inserire la country corretta. Se `action=country history`, inserire la country finale/corrente dell'atleta. |
| `notes` | Spazio libero per motivazione admin. |

### 6.3 Regole operative comuni

- `decision=merge as same athlete`: i record devono essere collegati allo stesso atleta;
- `decision=keep separate`: i record devono restare riferiti ad atleti distinti;
- `action=canonical country`: una delle country e considerata errore di data entry; `country` contiene la country corretta da usare;
- `action=country history`: si tratta dello stesso atleta con storico/cambio country; `country` contiene la country finale/corrente dell'atleta;
- se non esiste una questione country, `action` e `country` possono restare vuoti.

Nota: il `review_id` resta nel CSV per consentire al backend di trasformare le decisioni admin nel payload tecnico del commit 2019.

---

## 7. Proposta operativa

Stato operativo dopo la compilazione admin dei due CSV:

1. mantenere come completato `gymternet_2019_new_athlete_country_conflicts.csv`, salvo eventuali correzioni admin mirate;
2. mantenere come completato `gymternet_2019_existing_athlete_match_review.csv`, salvo eventuali correzioni admin mirate;
3. lasciare fuori dal database i 958 D-score orfani e conservarli nel CSV;
4. generare il payload decisionale;
5. simulare il commit 2019 con le decisioni;
6. solo dopo preview pulita, eseguire commit controllato 2019.

---

## 8. Stato finale della preview

Il 2019 non e ancora importato nel database.

La preview e positiva perche:

- non ci sono conflitti bloccanti;
- non ci sono duplicati rilevati;
- le anomalie sono state isolate in report dedicati;
- il database 2018 e stato preservato tramite backup pre-2019.

Il blocco atleta/country e stato risolto nei CSV operativi.

---

## 9. Payload decisionale e preview con decisioni applicate

Data esecuzione: 25 giugno 2026

Payload generato:

```text
docs/import_reports/gymternet_2019_athlete_match_decisions.json
```

Preview con decisioni applicate:

```text
docs/import_reports/gymternet_2019_preview_with_decisions_summary.json
```

La preview e stata eseguita su copia temporanea del database:

```text
/private/tmp/leverage_preview_2019.db
```

Il database operativo `leverage.db` non e stato modificato.

### 9.1 Esito decisioni atleta/country

| Voce | Conteggio |
|---|---:|
| Decisioni admin nel payload | 393 |
| Decisioni invalide | 0 |
| Review irrisolte | 0 |
| `accept_suggestion` | 290 |
| `merge_as_same_athlete` | 64 |
| `create_new` | 19 |
| `update_country` | 10 |
| `keep_existing_country` | 10 |
| Correzioni represented country da decisioni | 76 |
| Override represented country generati | 143 |

La semantica `canonical country` e stata resa coerente anche per i match con atleta gia esistente: quando l'admin sceglie una country canonica, il payload puo correggere anche `Result.represented_country` tramite `represented_country_override`.

### 9.2 Preview applicata

| Voce | Conteggio |
|---|---:|
| Righe parse | 106.633 |
| Result importabili dopo decisioni | 106.633 |
| Athlete che verrebbero creati | 4.211 |
| Event che verrebbero creati | 234 |
| Conflitti residui | 0 |
| Duplicati residui | 0 |
| D-score orfani lasciati fuori | 958 |
| Warning | 2 |

Warning confermati:

- 958 D-score non agganciati a final score;
- 77 chiavi multi-day automatiche, 154 righe con `day` valorizzato.

### 9.3 Simulazione commit su database temporaneo

La simulazione commit e stata eseguita solo su copia temporanea e poi rollbackata.

| Voce simulata | Conteggio |
|---|---:|
| Athlete creati | 4.211 |
| Event creati | 234 |
| Result creati | 106.633 |
| Result completi creati | 73.802 |
| Result parziali creati | 32.831 |
| Event aggiornati | 268 |
| Country corrente Athlete aggiornate | 11 |
| `represented_country` corretti | 521 |
| Athlete con nuovi result | 8.578 |
| Event con nuovi result | 234 |

Controllo rollback:

| Stato DB temporaneo | Athlete | Event | Result | Notification |
|---|---:|---:|---:|---:|
| Prima della simulazione | 7.134 | 211 | 89.988 | 0 |
| Durante la simulazione | 11.345 | 445 | 196.621 | 0 |
| Dopo rollback | 7.134 | 211 | 89.988 | 0 |

### 9.4 Conflitti post-decisione

La prima preview con decisioni applicate aveva individuato 24 conflitti post-decisione:

```text
docs/import_reports/gymternet_2019_post_decision_conflicts.csv
```

Questi conflitti emergono solo dopo avere applicato le fusioni atleta/country: due righe sorgente, prima distinte per nome o variante, diventano lo stesso `Result` sportivo, ma con score o D-score diversi. Non sono duplicati innocui.

Distribuzione dei conflitti:

| Atleta risolto | Conflitti |
|---|---:|
| Jack Stanley | 7 |
| Lee Jun-ho | 5 |
| Siddhi Hattekar | 5 |
| Chen Yu | 3 |
| Sofia Bertoli | 2 |
| Carla Martin | 1 |
| Kaja Skalska | 1 |

Decisione admin del 25 giugno 2026: tutti e 7 i gruppi sono atleti diversi e vanno quindi trattati come `keep separate`.

Righe decisione aggiornate a `keep separate`:

| Imported athlete | Suggested existing athlete |
|---|---|
| Carolina Martin | Carla Martin |
| Cen Yu | Chen Yu |
| Jake Stanley | Jack Stanley |
| Lee Jung-hyo | Lee Jun-ho |
| Maja Skalska | Kaja Skalska |
| Riddhi Hattekar | Siddhi Hattekar |
| Sonia Bertoli | Sofia Bertoli |

Dopo l'aggiornamento delle decisioni, il payload e stato rigenerato e la preview applicata e stata rieseguita. Esito:

| Controllo | Esito |
|---|---:|
| Conflitti residui | 0 |
| Decisioni invalide | 0 |
| Review irrisolte | 0 |

Il file `docs/import_reports/gymternet_2019_post_decision_conflicts.csv` e stato rigenerato come audit corrente vuoto, con sola intestazione.
