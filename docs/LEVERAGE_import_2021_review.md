# LEVERAGE - Preview, review e commit import 2021

Data preview: 25 giugno 2026  
Data commit database locale: 25 giugno 2026

File sorgente: `import_files/Results 2021.xlsx`

Stato: import 2021 committato nel database locale e verificato

## 1. Obiettivo

Il file Gymternet 2021 e stato importato sul database locale gia popolato con 2018, 2019 e 2020.

Il processo e stato svolto in modo controllato:

- preview iniziale senza scrittura sul database;
- generazione dei CSV operativi per review admin;
- compilazione admin dei due file Numbers;
- trasferimento controllato delle sole colonne decisionali nei CSV operativi;
- aggiunta di 5 correzioni nome atleta verificate dall'admin;
- generazione del payload decisionale;
- preview con decisioni applicate;
- risoluzione dei conflitti post-decisione;
- backup del database;
- commit reale del 2021;
- controlli post-import.

## 2. File generati

| File | Scopo |
|---|---|
| `docs/import_reports/gymternet_2021_preview_summary.json` | Sintesi tecnica della preview iniziale 2021. |
| `docs/import_reports/gymternet_2021_duplicates.csv` | Audit dei duplicati identici interni al file; vuoto. |
| `docs/import_reports/gymternet_2021_conflicts.csv` | Audit dei conflitti bloccanti iniziali; vuoto. |
| `docs/import_reports/gymternet_2021_orphan_dscores.csv` | D-score orfani non agganciati a un final score. |
| `docs/import_reports/gymternet_2021_athlete_review.csv` | Review atleta/country completa e tecnica. |
| `docs/import_reports/gymternet_2021_existing_athlete_match_review.csv` | CSV operativo per match con atleti gia presenti nel DB. |
| `docs/import_reports/gymternet_2021_new_athlete_country_conflicts.csv` | CSV operativo per nuovi atleti con conflitti country nel file 2021. |
| `docs/import_reports/gymternet_2021_athlete_name_corrections.csv` | Correzioni nome atleta esistente verificate dall'admin. |
| `docs/import_reports/gymternet_2021_athlete_match_decisions.json` | Payload tecnico delle decisioni admin 2021. |
| `docs/import_reports/gymternet_2021_preview_with_decisions_summary.json` | Preview 2021 con decisioni admin applicate, senza commit. |
| `docs/import_reports/gymternet_2021_post_decision_conflicts.csv` | Audit dei conflitti dopo le decisioni; rigenerato vuoto dopo la correzione finale. |
| `docs/import_reports/gymternet_2021_post_decision_duplicates.csv` | Audit dei duplicati identici residui dopo le decisioni; vuoto. |
| `docs/import_reports/gymternet_2021_commit_summary.json` | Report tecnico del commit reale 2021. |

## 3. Sintesi preview iniziale

| Voce | Conteggio |
|---|---:|
| Righe parse | 77.423 |
| Result importabili | 77.423 |
| Athlete che verrebbero creati senza decisioni admin | 3.013 |
| Event che verrebbero creati | 196 |
| Duplicati identici interni al file | 0 |
| Conflitti bloccanti iniziali | 0 |
| Warning | 2 |

Warning:

- 1.341 D-score non agganciati a final score;
- assegnazione automatica `day` applicata a 7 chiavi multi-day, con 14 righe valorizzate fino a `day=2`.

## 4. Duplicati e D-score orfani

La preview 2021 non ha rilevato duplicati identici interni al file.

Totale D-score orfani: 1.341.

Distribuzione per tipo problema:

| Tipo problema | Conteggio |
|---|---:|
| `athlete_missing_in_score_sheet` | 706 |
| `possible_athlete_name_typo` | 397 |
| `missing_final_score_for_context` | 116 |
| `possible_context_mismatch` | 103 |
| `possible_event_name_mismatch` | 15 |
| `missing_score_sheet_context` | 4 |

Decisione metodologica: come per 2018, 2019 e 2020, questi D-score restano fuori dal database operativo salvo review mirata futura. Non vengono creati result autonomi con solo D-score.

## 5. Review atleta/country

Totale review atleta/country: 329.

Distribuzione iniziale:

| Tipo review | Conteggio |
|---|---:|
| `possible_existing_athlete_match` | 280 |
| `possible_athlete_identity_collision` | 31 |
| `possible_athlete_country_change` | 18 |

Per la review admin sono stati usati due CSV operativi, compilati dall'admin tramite file Numbers:

| File | Righe controllate |
|---|---:|
| `gymternet_2021_existing_athlete_match_review.csv` | 326 |
| `gymternet_2021_new_athlete_country_conflicts.csv` | 3 |

Il trasferimento dai file Numbers ai CSV operativi ha preservato i campi tecnici e ha aggiornato soltanto:

- `decision`;
- `action`;
- `country`;
- `notes`.

## 6. Correzioni nome atleta

Durante la review 2021 l'admin ha identificato 5 nomi errati gia presenti nel database. E stato aggiunto il supporto backend a `target_name_update`, cosi il commit Gymternet puo correggere il nome della scheda atleta esistente senza creare una nuova entita.

| ID atleta | Nome precedente | Nome corretto | Country | Discipline |
|---:|---|---|---|---|
| 1147 | Hirohito Obama | Hirohito Kohama | JPN | MAG |
| 676 | Dawiel Carrion | Daniel Carrion | ESP | MAG |
| 8849 | Yuta Sasaki | Yutaro Sasaki | JPN | MAG |
| 8915 | Ai Takada | Airi Takada | JPN | WAG |
| 1180 | Hung Yuang-His | Hung Yuan-Hsi | TPE | MAG |

Queste correzioni sono documentate in:

```text
docs/import_reports/gymternet_2021_athlete_name_corrections.csv
```

## 7. Decisioni applicate

Dopo il trasferimento delle decisioni admin e l'aggiunta delle correzioni nome, il payload tecnico 2021 ha prodotto:

| Decisione/azione | Conteggio |
|---|---:|
| Suggerimenti accettati | 242 |
| Nuovi atleti confermati | 38 |
| Merge di identita atleta | 31 |
| Aggiornamenti country atleta | 11 |
| Country atleta mantenute | 10 |
| Correzioni nome atleta | 5 |
| Correzioni `represented_country` | 35 chiavi decisionali / 174 result corretti nel commit |
| Decisioni invalide | 0 |
| Decisioni mancanti | 0 |

## 8. Conflitti post-decisione risolti

La prima preview con decisioni applicate ha generato 4 conflitti, collegati a 2 proposte di merge:

- `Ona Garcia` con `Ana Garcia`;
- `Ariadna Sanchez` con `Aitana Sanchez`.

In entrambi i casi il merge avrebbe creato result nello stesso evento, round, format e apparatus con score o D-score diversi.

Decisione metodologica: applicare la regola gia consolidata:

```text
same_context_different_score_keep_separate
```

Dopo questa correzione, la preview post-decisione e risultata pulita:

| Voce | Conteggio |
|---|---:|
| Conflitti post-decisione | 0 |
| Decisioni invalide | 0 |
| Decisioni mancanti | 0 |
| Duplicati identici residui | 0 |

## 9. Name-order automatico

Durante la preview 2021 il tool ha applicato automaticamente la regola name-order:

| Voce | Conteggio |
|---|---:|
| Merge automatici name-order | 4 |
| Chiavi variante normalizzate | 4 |
| Record normalizzati | 20 |

Questa logica segue la decisione gia presa: quando nome e cognome sono invertiti, il tool non deve chiedere review admin ma normalizzare automaticamente verso l'ordine piu coerente con i result.

## 10. Commit database 2021

Prima del commit e stato creato il backup:

```text
backups/leverage_pre_import_2021_20260625_204252.db
```

Stato database prima del commit:

| Entita | Conteggio |
|---|---:|
| Athlete | 12.230 |
| Event | 521 |
| Result | 230.398 |
| Notification | 0 |

Statistiche commit:

| Voce | Conteggio |
|---|---:|
| Athlete creati | 2.727 |
| Event creati | 196 |
| Result creati | 77.423 |
| Result completi creati | 50.565 |
| Result parziali creati | 26.858 |
| Event aggiornati | 189 |
| Country atleta aggiornate | 11 |
| Nomi atleta aggiornati | 5 |
| `represented_country` corretti sui result | 174 |
| Atleti con nuovi result | 6.782 |
| Event con nuovi result | 196 |
| Duplicati saltati | 0 |
| D-score orfani lasciati fuori dal DB | 1.341 |

Stato database dopo il commit:

| Entita | Conteggio |
|---|---:|
| Athlete | 14.957 |
| Event | 717 |
| Result | 307.821 |
| Notification | 0 |

## 11. Controlli post-import

Distribuzione result per anno dopo il commit 2021:

| Anno evento | Result |
|---|---:|
| 2018 | 89.988 |
| 2019 | 106.084 |
| 2020 | 34.326 |
| 2021 | 77.423 |

Qualita dati 2021:

| Indicatore | Conteggio |
|---|---:|
| Result completi 2021 | 50.565 |
| Result 2021 con final score ma senza D-score | 26.858 |
| Result 2021 senza final score | 0 |

Controllo duplicati semantici:

| Controllo | Esito |
|---|---:|
| Gruppi duplicati semantici | 0 |

## 12. Stato operativo finale

Il 2021 e stato importato nel database locale.

Il commit reale ha creato 77.423 result nuovi e non ha introdotto duplicati semantici.

I 1.341 D-score orfani sono stati conservati in `docs/import_reports/gymternet_2021_orphan_dscores.csv` per eventuale recupero futuro, ma non sono stati importati nel database operativo.
