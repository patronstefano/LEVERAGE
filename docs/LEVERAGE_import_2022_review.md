# LEVERAGE - Preview e review import 2022

Data preview: 25 giugno 2026

File sorgente: `import_files/Results 2022.xlsx`

Stato: preview eseguita, nessun commit 2022 eseguito

## 1. Obiettivo

Questa preview controlla il file Gymternet 2022 sul database locale gia popolato con 2018, 2019, 2020 e 2021.

L'obiettivo e:

- verificare quanti result 2022 sono importabili;
- individuare duplicati, conflitti e warning;
- generare CSV di review admin per atleti/country e D-score orfani;
- mantenere il database operativo invariato fino alla review admin.

## 2. File generati

| File | Scopo |
|---|---|
| `docs/import_reports/gymternet_2022_preview_summary.json` | Sintesi tecnica completa della preview 2022. |
| `docs/import_reports/gymternet_2022_duplicates.csv` | Audit dei duplicati identici interni al file. |
| `docs/import_reports/gymternet_2022_conflicts.csv` | Audit dei conflitti bloccanti; vuoto in questa preview. |
| `docs/import_reports/gymternet_2022_orphan_dscores.csv` | D-score orfani non agganciati a un final score. |
| `docs/import_reports/gymternet_2022_athlete_review.csv` | Review atleta/country completa e tecnica. |
| `docs/import_reports/gymternet_2022_existing_athlete_match_review.csv` | CSV operativo per verificare match con atleti gia presenti nel DB. |
| `docs/import_reports/gymternet_2022_new_athlete_country_conflicts.csv` | CSV operativo per nuovi atleti con conflitti country nel file 2022. |

## 3. Sintesi preview

| Voce | Conteggio |
|---|---:|
| Righe parse | 97.937 |
| Result importabili | 97.934 |
| Athlete che verrebbero creati senza decisioni admin | 2.840 |
| Event che verrebbero creati | 219 |
| Duplicati identici interni al file | 3 |
| Conflitti bloccanti | 0 |
| Warning | 2 |

Warning:

- 1.426 D-score non agganciati a final score;
- assegnazione automatica `day` applicata a 16 chiavi multi-day, con 32 righe valorizzate fino a `day=2`.

## 4. Duplicati interni

La preview segnala 3 duplicati identici interni al file. Sono duplicati innocui: stesso contesto sportivo e stesso score/D-score. Il tool li saltera automaticamente in fase di commit.

| Atleta | Evento | Apparatus | Score | D-score |
|---|---|---|---:|---:|
| Lee Junho | World Championships | HB | 12.233 | 5.600 |
| Lee Junho | World Championships | PB | 13.266 | 5.600 |
| Lee Junho | World Championships | SR | 13.433 | 5.000 |

## 5. D-score orfani

Totale D-score orfani: 1.426.

Distribuzione per tipo problema:

| Tipo problema | Conteggio |
|---|---:|
| `athlete_missing_in_score_sheet` | 966 |
| `possible_athlete_name_typo` | 195 |
| `possible_context_mismatch` | 130 |
| `missing_final_score_for_context` | 118 |
| `possible_event_name_mismatch` | 14 |
| `missing_score_sheet_context` | 3 |

Decisione metodologica provvisoria: come per 2018, 2019, 2020 e 2021, questi D-score restano fuori dal database operativo salvo review mirata futura. Non vengono creati result autonomi con solo D-score.

## 6. Review atleta/country

Totale review atleta/country: 389.

Distribuzione:

| Tipo review | Conteggio |
|---|---:|
| `possible_existing_athlete_match` | 320 |
| `possible_athlete_identity_collision` | 44 |
| `possible_athlete_country_change` | 25 |

Per rendere piu rapida la review admin, sono stati generati due CSV operativi:

| File | Righe da controllare | Scopo |
|---|---:|---|
| `gymternet_2022_existing_athlete_match_review.csv` | 386 | Verificare se atleta 2022 e atleta gia presente nel DB sono la stessa persona, oppure se c'e cambio/correzione country. |
| `gymternet_2022_new_athlete_country_conflicts.csv` | 3 | Risolvere conflitti country interni a nuovi atleti 2022. |

Nel CSV degli atleti gia esistenti sono incluse:

- gare 2022 dell'atleta importato;
- risultati precedenti dell'atleta gia presente nel DB;
- evidenza futura dai file 2023-2025;
- eventuali raccomandazioni della memoria decisionale del tool Gymternet.

Priorita del CSV `existing_athlete_match_review`:

| Priorita | Righe |
|---|---:|
| high | 81 |
| medium | 305 |

## 7. Conflitti country tra nuovi atleti

| Atleta | Discipline | Country coinvolte | Evidenza 2022 | Evidenza futura |
|---|---|---|---|---|
| Viggo Altarac | MAG | SGP, SWE | SGP: Singapore Championships; SWE: Nordic Championships | 2023: SWE; 2024: SWE; 2025: SGP/SWE |
| Andres Yustiz | MAG | USA, VEN | USA: Houston National Invitational; VEN: Bolivarian Games | not found 2023-2025 |
| Kyle Millar | MAG | GBR, ISL | GBR: Scottish Championships; ISL: Northern European Championships | 2023: GBR; 2024: GBR; 2025: GBR |

Questi casi dovranno essere verificati dall'admin nel CSV dedicato.

## 8. Name-order automatico

Durante la preview 2022 il tool ha applicato automaticamente la regola name-order:

| Voce | Conteggio |
|---|---:|
| Merge automatici name-order | 6 |
| Chiavi variante normalizzate | 6 |
| Record normalizzati | 66 |

Questa logica segue la decisione gia presa: quando nome e cognome sono invertiti, il tool non deve chiedere review admin ma normalizzare automaticamente verso l'ordine piu coerente con i result.

## 9. Stato operativo

Il 2022 non e stato importato nel database.

Prima del commit 2022 occorre:

1. completare `gymternet_2022_existing_athlete_match_review.csv`;
2. completare `gymternet_2022_new_athlete_country_conflicts.csv`;
3. generare il payload decisionale 2022;
4. rieseguire preview con decisioni applicate;
5. controllare eventuali conflitti post-decisione;
6. solo dopo preview pulita, eseguire commit controllato 2022.
