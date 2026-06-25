# LEVERAGE - Preview e review import 2020

Data preview: 25 giugno 2026

File sorgente: `import_files/Results 2020.xlsx`

Stato: preview eseguita, nessun commit 2020 eseguito

## 1. Obiettivo

Questa preview controlla il file Gymternet 2020 sul database locale gia popolato con 2018 e 2019.

L'obiettivo e:

- verificare quanti result 2020 sono importabili;
- individuare duplicati, conflitti e warning;
- generare CSV di review admin per atleti/country e D-score orfani;
- mantenere il database operativo invariato fino alla review admin.

## 2. File generati

| File | Scopo |
|---|---|
| `docs/import_reports/gymternet_2020_preview_summary.json` | Sintesi tecnica completa della preview 2020. |
| `docs/import_reports/gymternet_2020_duplicates.csv` | Audit dei duplicati identici interni al file. |
| `docs/import_reports/gymternet_2020_conflicts.csv` | Audit dei conflitti bloccanti; vuoto in questa preview. |
| `docs/import_reports/gymternet_2020_orphan_dscores.csv` | D-score orfani non agganciati a un final score. |
| `docs/import_reports/gymternet_2020_athlete_review.csv` | Review atleta/country completa e tecnica. |
| `docs/import_reports/gymternet_2020_existing_athlete_match_review.csv` | CSV operativo per verificare match con atleti gia presenti nel DB. |
| `docs/import_reports/gymternet_2020_new_athlete_country_conflicts.csv` | CSV operativo per nuovi atleti con conflitti country nel file 2020. |

## 3. Sintesi preview

| Voce | Conteggio |
|---|---:|
| Righe parse | 33.782 |
| Result importabili | 33.777 |
| Athlete che verrebbero creati senza decisioni admin | 1.042 |
| Event che verrebbero creati | 76 |
| Duplicati identici interni al file | 5 |
| Conflitti bloccanti | 0 |
| Warning | 2 |

Warning:

- 696 D-score non agganciati a final score;
- assegnazione automatica `day` applicata a 207 chiavi multi-day, con 431 righe valorizzate fino a `day=4`.

## 4. Duplicati interni

La preview segnala 5 duplicati identici interni al file. Sono duplicati innocui: stesso contesto sportivo e stesso score/D-score. Il tool li saltera automaticamente in fase di commit.

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

Decisione metodologica provvisoria: come per 2018 e 2019, questi D-score restano fuori dal database operativo salvo review mirata futura. Non vengono creati result autonomi con solo D-score.

## 6. Review atleta/country

Totale review atleta/country: 165.

Distribuzione:

| Tipo review | Conteggio |
|---|---:|
| `possible_existing_athlete_match` | 141 |
| `possible_athlete_country_change` | 15 |
| `possible_athlete_identity_collision` | 9 |

Per rendere piu rapida la review admin, sono stati generati due CSV operativi:

| File | Righe da controllare | Scopo |
|---|---:|---|
| `gymternet_2020_existing_athlete_match_review.csv` | 164 | Verificare se atleta 2020 e atleta gia presente nel DB sono la stessa persona, oppure se c'e cambio/correzione country. |
| `gymternet_2020_new_athlete_country_conflicts.csv` | 1 | Risolvere conflitto country interno a un nuovo atleta 2020. |

Nel CSV degli atleti gia esistenti sono incluse:

- gare 2020 dell'atleta importato;
- risultati precedenti dell'atleta gia presente nel DB;
- evidenza futura dai file 2021-2025;
- eventuali raccomandazioni della memoria decisionale del tool Gymternet.

## 7. Unico conflitto country tra nuovi atleti

| Atleta | Discipline | Country coinvolte | Evidenza 2020 | Evidenza futura |
|---|---|---|---|---|
| Cathalina Matamala | WAG | GER, NED | GER: Pre-Olympic Youth Cup; NED: Create Team Cup | 2021: NED |

Questo caso dovra essere verificato dall'admin nel CSV dedicato.

## 8. Stato operativo

Il 2020 non e stato importato nel database.

Prima del commit 2020 occorre:

1. completare `gymternet_2020_existing_athlete_match_review.csv`;
2. completare `gymternet_2020_new_athlete_country_conflicts.csv`;
3. generare il payload decisionale 2020;
4. rieseguire preview con decisioni applicate;
5. controllare eventuali conflitti post-decisione;
6. solo dopo preview pulita, eseguire commit controllato 2020.
