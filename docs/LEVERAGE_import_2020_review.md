# LEVERAGE - Preview, review e commit import 2020

Data preview: 25 giugno 2026  
Data commit database locale: 25 giugno 2026

File sorgente: `import_files/Results 2020.xlsx`

Stato: import 2020 committato nel database locale e verificato

## 1. Obiettivo

Il file Gymternet 2020 e stato importato sul database locale gia popolato con 2018 e 2019.

Il processo e stato svolto in modo controllato:

- preview iniziale senza scrittura sul database;
- generazione dei CSV operativi per review admin;
- compilazione admin dei due file Numbers;
- trasferimento controllato delle sole colonne decisionali nei CSV operativi;
- generazione del payload decisionale;
- preview con decisioni applicate;
- risoluzione dei conflitti post-decisione;
- backup del database;
- commit reale del 2020;
- controlli post-import.

## 2. File generati

| File | Scopo |
|---|---|
| `docs/import_reports/gymternet_2020_preview_summary.json` | Sintesi tecnica della preview iniziale 2020. |
| `docs/import_reports/gymternet_2020_duplicates.csv` | Audit dei duplicati identici interni al file. |
| `docs/import_reports/gymternet_2020_conflicts.csv` | Audit dei conflitti bloccanti iniziali; vuoto. |
| `docs/import_reports/gymternet_2020_orphan_dscores.csv` | D-score orfani non agganciati a un final score. |
| `docs/import_reports/gymternet_2020_athlete_review.csv` | Review atleta/country completa e tecnica. |
| `docs/import_reports/gymternet_2020_existing_athlete_match_review.csv` | CSV operativo per match con atleti gia presenti nel DB. |
| `docs/import_reports/gymternet_2020_new_athlete_country_conflicts.csv` | CSV operativo per nuovi atleti con conflitti country nel file 2020. |
| `docs/import_reports/gymternet_2020_athlete_match_decisions.json` | Payload tecnico delle decisioni admin 2020. |
| `docs/import_reports/gymternet_2020_preview_with_decisions_summary.json` | Preview 2020 con decisioni admin applicate, senza commit. |
| `docs/import_reports/gymternet_2020_post_decision_conflicts.csv` | Audit dei conflitti dopo le decisioni; rigenerato vuoto dopo la correzione finale. |
| `docs/import_reports/gymternet_2020_post_decision_duplicates.csv` | Audit dei duplicati identici residui dopo le decisioni. |
| `docs/import_reports/gymternet_2020_commit_summary.json` | Report tecnico del commit reale 2020. |

## 3. Sintesi preview iniziale

| Voce | Conteggio |
|---|---:|
| Righe parse | 33.782 |
| Result importabili | 33.777 |
| Athlete che verrebbero creati senza decisioni admin | 1.042 |
| Event che verrebbero creati | 76 |
| Duplicati identici interni al file | 5 |
| Conflitti bloccanti iniziali | 0 |
| Warning | 2 |

Warning:

- 696 D-score non agganciati a final score;
- assegnazione automatica `day` applicata a 207 chiavi multi-day, con 431 righe valorizzate fino a `day=4`.

## 4. Duplicati interni

La preview ha segnalato 5 duplicati identici interni al file. Sono duplicati innocui: stesso contesto sportivo e stesso score/D-score. Il tool li ha saltati automaticamente in fase di commit.

| Atleta | Evento | Apparatus | Score | D-score |
|---|---|---|---:|---:|
| Adam Dobrovitz | Hungarian Championships | PH | 12.000 | 4.000 |
| Kazuma Kaya | Friendship & Solidarity Meet | HB | 14.300 |  |
| Soma Laszlo Csorvasi | Hungarian Championships | HB | 11.900 | 4.300 |
| Liu Sijia | Chinese Individual Championships | VT attempt 1 day 2 | 11.950 | 3.700 |
| Meng Shangrong | Chinese Individual Championships | UB | 12.850 | 4.600 |

## 5. D-score orfani

Totale D-score orfani: 696.

Distribuzione per tipo problema:

| Tipo problema | Conteggio |
|---|---:|
| `athlete_missing_in_score_sheet` | 482 |
| `possible_context_mismatch` | 107 |
| `missing_final_score_for_context` | 62 |
| `possible_athlete_name_typo` | 40 |
| `possible_event_name_mismatch` | 4 |
| `missing_score_sheet_context` | 1 |

Decisione metodologica: come per 2018 e 2019, questi D-score restano fuori dal database operativo salvo review mirata futura. Non vengono creati result autonomi con solo D-score.

## 6. Review atleta/country

Totale review atleta/country: 165.

Distribuzione iniziale:

| Tipo review | Conteggio |
|---|---:|
| `possible_existing_athlete_match` | 141 |
| `possible_athlete_country_change` | 15 |
| `possible_athlete_identity_collision` | 9 |

Per la review admin sono stati usati due CSV operativi, compilati dall'admin tramite file Numbers:

| File | Righe controllate |
|---|---:|
| `gymternet_2020_existing_athlete_match_review.csv` | 164 |
| `gymternet_2020_new_athlete_country_conflicts.csv` | 1 |

Il trasferimento dai file Numbers ai CSV operativi ha preservato i campi tecnici e ha aggiornato soltanto:

- `decision`;
- `action`;
- `country`;
- `notes`.

Sono stati normalizzati anche shorthand e refusi:

- `Merge` -> `merge as same athlete`;
- `Separate` -> `keep separate`;
- `Correct` / `Corrrect` -> `canonical country`;
- `History` -> `country history`.

## 7. Decisioni applicate

Dopo il trasferimento delle decisioni admin, il payload tecnico 2020 ha prodotto:

| Decisione/azione | Conteggio |
|---|---:|
| Suggerimenti accettati | 135 |
| Nuovi atleti confermati | 6 |
| Merge di identita atleta | 9 |
| Aggiornamenti country atleta | 8 |
| Country atleta mantenute | 11 |
| Correzioni `represented_country` sui result | 19 chiavi decisionali / 96 result corretti nel commit |
| Decisioni invalide | 0 |
| Decisioni mancanti | 0 |

### 7.1 Conflitto post-decisione risolto

La prima preview con decisioni applicate ha generato 5 conflitti, tutti collegati allo stesso caso:

- `Nao Kobayashi` suggerita come merge con `Kaho Kobayashi`;
- stesso evento: `All-Japan Student Championships`;
- stessa disciplina/category/format/round;
- stessi apparatus `BB`, `FX`, `UB`, `VT`, `AA`;
- score diversi nello stesso contesto sportivo.

Decisione metodologica: quando un possibile merge atleta produce lo stesso contesto sportivo di result ma con score o D-score diversi, il tool deve trattare i due record come atleti diversi e applicare `keep separate`.

La regola e coerente con quanto gia deciso durante il 2019 ed e tracciata come:

```text
same_context_different_score_keep_separate
```

Dopo questa correzione, la preview post-decisione e risultata pulita:

| Voce | Conteggio |
|---|---:|
| Conflitti post-decisione | 0 |
| Decisioni invalide | 0 |
| Decisioni mancanti | 0 |
| Duplicati identici residui | 5 |

## 8. Commit database 2020

Prima del commit e stato creato il backup:

```text
backups/leverage_pre_import_2020_20260625_191629.db
```

Stato database prima del commit:

| Entita | Conteggio |
|---|---:|
| Athlete | 11.345 |
| Event | 445 |
| Result | 196.621 |
| Notification | 0 |

Statistiche commit:

| Voce | Conteggio |
|---|---:|
| Athlete creati | 885 |
| Event creati | 76 |
| Result creati | 33.777 |
| Result completi creati | 20.887 |
| Result parziali creati | 12.890 |
| Event aggiornati | 94 |
| Country atleta aggiornate | 8 |
| `represented_country` corretti sui result | 96 |
| Atleti con nuovi result | 3.906 |
| Event con nuovi result | 76 |
| Duplicati saltati | 5 |
| D-score orfani lasciati fuori dal DB | 696 |

Stato database dopo il commit:

| Entita | Conteggio |
|---|---:|
| Athlete | 12.230 |
| Event | 521 |
| Result | 230.398 |
| Notification | 0 |

## 9. Controlli post-import

Distribuzione result per anno dopo il commit 2020:

| Anno evento | Result |
|---|---:|
| 2018 | 89.988 |
| 2019 | 106.084 |
| 2020 | 34.326 |

Qualita dati 2020:

| Indicatore | Conteggio |
|---|---:|
| Result completi 2020 | 20.887 |
| Result 2020 con final score ma senza D-score | 13.439 |
| Result 2020 senza final score | 0 |

Controllo duplicati semantici:

| Controllo | Esito |
|---|---:|
| Gruppi duplicati semantici | 0 |

Nota: i result 2020 sono 34.326 perche il file 2019 conteneva gia 549 result riferiti all'evento `1st Spanish League (2020 season)`, registrati correttamente con `Event.year=2020`.

## 10. Stato operativo finale

Il 2020 e stato importato nel database locale.

Il commit reale ha creato 33.777 result nuovi e non ha introdotto duplicati semantici.

I 696 D-score orfani sono stati conservati in `docs/import_reports/gymternet_2020_orphan_dscores.csv` per eventuale recupero futuro, ma non sono stati importati nel database operativo.
