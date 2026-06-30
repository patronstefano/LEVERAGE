# LEVERAGE - Preview e review import 2025

Data preview iniziale: 30 giugno 2026

File sorgente: `import_files/Results 2025.xlsx`

Stato: preview 2025 generata sul database locale popolato fino al commit reale 2024; database operativo non modificato.

## 1. Obiettivo

Questa preview controlla il file Gymternet 2025 sul database locale gia popolato con 2018, 2019, 2020, 2021, 2022, 2023 e 2024.

L'obiettivo e:

- verificare quanti result 2025 sono importabili;
- individuare duplicati, conflitti e warning;
- generare CSV di review admin per atleti/country e D-score orfani;
- applicare la regola `same_country_review_reuse` sui casi gia verificati in anni precedenti;
- mantenere il database operativo invariato fino alla review admin.

## 2. File generati

| File | Scopo |
|---|---|
| `docs/import_reports/gymternet_2025_preview_summary.json` | Sintesi tecnica completa della preview 2025. |
| `docs/import_reports/gymternet_2025_duplicates.csv` | Audit dei duplicati identici interni al file; vuoto in questa preview. |
| `docs/import_reports/gymternet_2025_conflicts.csv` | Audit dei conflitti bloccanti; vuoto in questa preview. |
| `docs/import_reports/gymternet_2025_orphan_dscores.csv` | D-score orfani non agganciati a final score. |
| `docs/import_reports/gymternet_2025_athlete_review.csv` | Review atleta/country completa e tecnica. |
| `docs/import_reports/gymternet_2025_existing_athlete_match_review.csv` | CSV operativo per verificare match con atleti gia presenti nel DB. |
| `docs/import_reports/gymternet_2025_new_athlete_country_conflicts.csv` | CSV operativo per nuovi atleti con conflitti country nel file 2025. |

## 3. Sintesi preview

| Voce | Conteggio |
|---|---:|
| Righe parse | 124.030 |
| Result importabili | 124.030 |
| Athlete che verrebbero creati senza decisioni admin | 3.448 |
| Event che verrebbero creati | 222 |
| Duplicati identici interni al file | 0 |
| Conflitti bloccanti | 0 |
| Warning | 3 |

Warning:

- 630 D-score non agganciati a final score;
- assegnazione automatica `day` applicata a 29 chiavi multi-day, con 58 righe valorizzate fino a `day=2`;
- il legacy Gymternet import ha rilevato result successivi al 2025 e applica le regole 2025 su vault e componenti mancanti. E_score, Penalty e Bonus mancanti restano `not available`. Per dati futuri con componenti esplicite sara preferibile usare il nuovo standard import dedicato.

## 4. Distribuzione anni nel file 2025

Il file `Results 2025.xlsx` contiene anche alcuni eventi marcati come anno evento 2026.

| Anno evento nel file | Result parse | Event distinti |
|---|---:|---:|
| 2025 | 123.922 | 221 |
| 2026 | 108 | 1 |

Eventi 2026 presenti nel file 2025:

| Event | Result parse |
|---|---:|
| `Top 12 Series 3 (2026)` | 108 |

Decisione metodologica: come per gli spillover gia rilevati nei file precedenti, questi record non sono considerati errore tecnico. Il sistema usa l'anno evento presente nel file sorgente.

## 5. Duplicati e conflitti

La preview 2025 non segnala duplicati identici interni al file e non segnala conflitti bloccanti.

| Controllo | Esito |
|---|---:|
| Duplicati identici | 0 |
| Conflitti bloccanti | 0 |

## 6. D-score orfani

Totale D-score orfani: 630.

Distribuzione per tipo problema:

| Tipo problema | Conteggio |
|---|---:|
| `athlete_missing_in_score_sheet` | 309 |
| `missing_final_score_for_context` | 140 |
| `possible_context_mismatch` | 111 |
| `possible_athlete_name_typo` | 64 |
| `possible_event_name_mismatch` | 6 |

Decisione metodologica provvisoria: come per gli anni precedenti, questi D-score restano fuori dal database operativo salvo review mirata futura. Non vengono creati result autonomi con solo D-score.

## 7. Review atleta/country

Totale review atleta/country: 636.

Distribuzione:

| Tipo review | Conteggio |
|---|---:|
| `possible_existing_athlete_match` | 535 |
| `possible_athlete_identity_collision` | 69 |
| `possible_athlete_country_change` | 32 |

CSV operativi:

| File | Righe | Stato decisioni |
|---|---:|---|
| `gymternet_2025_existing_athlete_match_review.csv` | 628 | 227 decisioni precompilate da `same_country_review_reuse`; 401 righe ancora da controllare. |
| `gymternet_2025_new_athlete_country_conflicts.csv` | 8 | 8 righe ancora da controllare. |

Distribuzione delle 401 decisioni mancanti nel CSV existing athlete:

| Tipo review | Righe da controllare |
|---|---:|
| `possible_existing_athlete_match` | 308 |
| `possible_athlete_identity_collision` | 61 |
| `possible_athlete_country_change` | 32 |

Le 227 decisioni precompilate sono tutte `merge as same athlete` su casi same-country gia verificati in anni precedenti. Queste celle possono comunque essere corrette dall'admin se durante la review emergono nuove evidenze.

## 8. Conflitti country tra nuovi atleti

Il CSV `gymternet_2025_new_athlete_country_conflicts.csv` contiene 8 casi:

| Atleta | Disciplina | Country in conflitto | Evidenza futura |
|---|---|---|---|
| Kiichi Kaneta | MAG | JAM, JPN | non disponibile: set storico fermo al 2025 |
| Victor Verwimp | MAG | BEL, NED | non disponibile: set storico fermo al 2025 |
| Adina Kubickova | WAG | AUT, CZE | non disponibile: set storico fermo al 2025 |
| Lilou Gustin | WAG | BEL, SLO | non disponibile: set storico fermo al 2025 |
| Andreea Mihai | WAG | GER, ROU | non disponibile: set storico fermo al 2025 |
| Terri Grandry | WAG | BEL, FRA | non disponibile: set storico fermo al 2025 |
| Lucie Selvais | WAG | BEL, SLO | non disponibile: set storico fermo al 2025 |
| Céleste Mordenti | WAG | LUX, NED | non disponibile: set storico fermo al 2025 |

Questi casi richiedono decisione admin esplicita. Poiche cambia il country, la regola `same_country_review_reuse` non viene applicata.

## 9. Stato operativo

Il database locale non e stato modificato.

Prossimo passo: l'admin deve completare i due CSV operativi 2025:

- `docs/import_reports/gymternet_2025_existing_athlete_match_review.csv`;
- `docs/import_reports/gymternet_2025_new_athlete_country_conflicts.csv`.

Dopo la review admin, verranno generati il payload decisionale 2025, la preview post-decisione e, solo se pulita, il commit reale del 2025.
