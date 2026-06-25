# LEVERAGE - Preview e review import 2021

Data preview: 25 giugno 2026

File sorgente: `import_files/Results 2021.xlsx`

Stato: preview eseguita, nessun commit 2021 eseguito

## 1. Obiettivo

Questa preview controlla il file Gymternet 2021 sul database locale gia popolato con 2018, 2019 e 2020.

L'obiettivo e:

- verificare quanti result 2021 sono importabili;
- individuare duplicati, conflitti e warning;
- generare CSV di review admin per atleti/country e D-score orfani;
- mantenere il database operativo invariato fino alla review admin.

## 2. File generati

| File | Scopo |
|---|---|
| `docs/import_reports/gymternet_2021_preview_summary.json` | Sintesi tecnica completa della preview 2021. |
| `docs/import_reports/gymternet_2021_duplicates.csv` | Audit dei duplicati identici interni al file; vuoto in questa preview. |
| `docs/import_reports/gymternet_2021_conflicts.csv` | Audit dei conflitti bloccanti; vuoto in questa preview. |
| `docs/import_reports/gymternet_2021_orphan_dscores.csv` | D-score orfani non agganciati a un final score. |
| `docs/import_reports/gymternet_2021_athlete_review.csv` | Review atleta/country completa e tecnica. |
| `docs/import_reports/gymternet_2021_existing_athlete_match_review.csv` | CSV operativo per verificare match con atleti gia presenti nel DB. |
| `docs/import_reports/gymternet_2021_new_athlete_country_conflicts.csv` | CSV operativo per nuovi atleti con conflitti country nel file 2021. |

## 3. Sintesi preview

| Voce | Conteggio |
|---|---:|
| Righe parse | 77.423 |
| Result importabili | 77.423 |
| Athlete che verrebbero creati senza decisioni admin | 3.013 |
| Event che verrebbero creati | 196 |
| Duplicati identici interni al file | 0 |
| Conflitti bloccanti | 0 |
| Warning | 2 |

Warning:

- 1.341 D-score non agganciati a final score;
- assegnazione automatica `day` applicata a 7 chiavi multi-day, con 14 righe valorizzate fino a `day=2`.

## 4. Duplicati e conflitti

La preview 2021 non ha rilevato duplicati identici interni al file.

La preview 2021 non ha rilevato conflitti bloccanti con il database gia popolato.

## 5. D-score orfani

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

Decisione metodologica provvisoria: come per 2018, 2019 e 2020, questi D-score restano fuori dal database operativo salvo review mirata futura. Non vengono creati result autonomi con solo D-score.

## 6. Review atleta/country

Totale review atleta/country: 329.

Distribuzione:

| Tipo review | Conteggio |
|---|---:|
| `possible_existing_athlete_match` | 280 |
| `possible_athlete_identity_collision` | 31 |
| `possible_athlete_country_change` | 18 |

Per rendere piu rapida la review admin, sono stati generati due CSV operativi:

| File | Righe da controllare | Scopo |
|---|---:|---|
| `gymternet_2021_existing_athlete_match_review.csv` | 326 | Verificare se atleta 2021 e atleta gia presente nel DB sono la stessa persona, oppure se c'e cambio/correzione country. |
| `gymternet_2021_new_athlete_country_conflicts.csv` | 3 | Risolvere conflitti country interni a nuovi atleti 2021. |

Nel CSV degli atleti gia esistenti sono incluse:

- gare 2021 dell'atleta importato;
- risultati precedenti dell'atleta gia presente nel DB;
- evidenza futura dai file 2022-2025;
- eventuali raccomandazioni della memoria decisionale del tool Gymternet.

Priorita del CSV `existing_athlete_match_review`:

| Priorita | Righe |
|---|---:|
| high | 60 |
| medium | 266 |

## 7. Conflitti country tra nuovi atleti

| Atleta | Discipline | Country coinvolte | Evidenza 2021 | Evidenza futura |
|---|---|---|---|---|
| Logan Curtis | MAG | BAN, NZL | BAN: New Zealand Championships; NZL: New Zealand Championships | 2024: NZL, 2025: NZL |
| Rory Quinn | MAG | BAN, NZL | BAN: New Zealand Championships; NZL: New Zealand Championships | 2023: NZL, 2024: NZL, 2025: NZL |
| Joshua Jack Williams | MAG | ESP, GER | ESP: 1st Bundesliga; GER: 2nd Bundesliga / 4th Bundesliga | not found 2022-2025 |

Questi casi dovranno essere verificati dall'admin nel CSV dedicato.

## 8. Name-order automatico

Durante la preview 2021 il tool ha applicato automaticamente la regola name-order:

| Voce | Conteggio |
|---|---:|
| Merge automatici name-order | 4 |
| Chiavi variante normalizzate | 4 |
| Record normalizzati | 20 |

Questa logica segue la decisione gia presa: quando nome e cognome sono invertiti, il tool non deve chiedere review admin ma normalizzare automaticamente verso l'ordine piu coerente con i result.

## 9. Stato operativo

Il 2021 non e stato importato nel database.

Prima del commit 2021 occorre:

1. completare `gymternet_2021_existing_athlete_match_review.csv`;
2. completare `gymternet_2021_new_athlete_country_conflicts.csv`;
3. generare il payload decisionale 2021;
4. rieseguire preview con decisioni applicate;
5. controllare eventuali conflitti post-decisione;
6. solo dopo preview pulita, eseguire commit controllato 2021.
