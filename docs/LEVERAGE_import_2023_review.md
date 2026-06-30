# LEVERAGE - Preview e review import 2023

Data preview: 30 giugno 2026

File sorgente: `import_files/Results 2023.xlsx`

Stato: preview eseguita, nessun commit 2023 eseguito

## 1. Obiettivo

Questa preview controlla il file Gymternet 2023 sul database locale gia popolato con 2018, 2019, 2020, 2021 e 2022.

L'obiettivo e:

- verificare quanti result 2023 sono importabili;
- individuare duplicati, conflitti e warning;
- generare CSV di review admin per atleti/country e D-score orfani;
- mantenere il database operativo invariato fino alla review admin.

## 2. File generati

| File | Scopo |
|---|---|
| `docs/import_reports/gymternet_2023_preview_summary.json` | Sintesi tecnica completa della preview 2023. |
| `docs/import_reports/gymternet_2023_duplicates.csv` | Audit dei duplicati identici interni al file; vuoto in questa preview. |
| `docs/import_reports/gymternet_2023_conflicts.csv` | Audit dei conflitti bloccanti; vuoto in questa preview. |
| `docs/import_reports/gymternet_2023_orphan_dscores.csv` | D-score orfani non agganciati a final score. |
| `docs/import_reports/gymternet_2023_athlete_review.csv` | Review atleta/country completa e tecnica. |
| `docs/import_reports/gymternet_2023_existing_athlete_match_review.csv` | CSV operativo per verificare match con atleti gia presenti nel DB. |
| `docs/import_reports/gymternet_2023_new_athlete_country_conflicts.csv` | CSV operativo per nuovi atleti con conflitti country nel file 2023. |

## 3. Sintesi preview

| Voce | Conteggio |
|---|---:|
| Righe parse | 117.489 |
| Result importabili | 117.489 |
| Athlete che verrebbero creati senza decisioni admin | 3.908 |
| Event che verrebbero creati | 241 |
| Duplicati identici interni al file | 0 |
| Conflitti bloccanti | 0 |
| Warning | 2 |

Warning:

- 1.454 D-score non agganciati a final score;
- assegnazione automatica `day` applicata a 104 chiavi multi-day, con 208 righe valorizzate fino a `day=2`.

## 4. Distribuzione anni nel file 2023

Il file `Results 2023.xlsx` contiene anche alcuni eventi marcati come anno evento 2024.

| Anno evento nel file | Result parse | Event distinti |
|---|---:|---:|
| 2023 | 116.397 | 237 |
| 2024 | 1.092 | 4 |

Eventi 2024 presenti nel file 2023:

| Event | Result parse |
|---|---:|
| `1st Spanish League (2024 season)` | 586 |
| `Top 12 Series 2 (2024 Season)` | 200 |
| `Top 12 Series 1 (2024 Season)` | 199 |
| `Top 12 Series 3 (2024 Season)` | 107 |

Decisione metodologica: come per lo spillover 2023 rilevato nel file 2022, questi record non sono considerati errore tecnico. Il sistema usa l'anno evento presente nel file sorgente.

## 5. Duplicati e conflitti

La preview 2023 non segnala duplicati identici interni al file e non segnala conflitti bloccanti.

| Controllo | Esito |
|---|---:|
| Duplicati identici | 0 |
| Conflitti bloccanti | 0 |

## 6. D-score orfani

Totale D-score orfani: 1.454.

Distribuzione per tipo problema:

| Tipo problema | Conteggio |
|---|---:|
| `athlete_missing_in_score_sheet` | 1.045 |
| `possible_context_mismatch` | 126 |
| `missing_final_score_for_context` | 122 |
| `possible_athlete_name_typo` | 77 |
| `possible_event_name_mismatch` | 62 |
| `missing_score_sheet_context` | 22 |

Decisione metodologica provvisoria: come per 2018, 2019, 2020, 2021 e 2022, questi D-score restano fuori dal database operativo salvo review mirata futura. Non vengono creati result autonomi con solo D-score.

## 7. Review atleta/country

Totale review atleta/country: 577.

Distribuzione:

| Tipo review | Conteggio |
|---|---:|
| `possible_existing_athlete_match` | 490 |
| `possible_athlete_identity_collision` | 52 |
| `possible_athlete_country_change` | 35 |

Per rendere piu rapida la review admin, sono stati generati due CSV operativi:

| File | Righe da controllare | Scopo |
|---|---:|---|
| `gymternet_2023_existing_athlete_match_review.csv` | 568 | Verificare se atleta 2023 e atleta gia presente nel DB sono la stessa persona, oppure se c'e cambio/correzione country. |
| `gymternet_2023_new_athlete_country_conflicts.csv` | 9 | Risolvere conflitti country interni a nuovi atleti 2023. |

Priorita del CSV `existing_athlete_match_review`:

| Priorita | Righe |
|---|---:|
| high | 111 |
| medium | 457 |

## 8. Conflitti country tra nuovi atleti

| Atleta | Discipline | Country coinvolte | Evidenza 2023/2024 nel file | Evidenza futura |
|---|---|---|---|---|
| Lucia Gonzalez | WAG | ARG, ESP | ARG: Argentinian Championships; ESP: 1st Spanish League 2024 season | 2024: ARG; 2025: ARG |
| Phong Tage Gullbrandsson | MAG | NOR, SWE | NOR: Malar Cup; SWE: Malar Cup | 2024: NOR; 2025: NOR |
| Paloma Mintcheva | WAG | BUL, USA | BUL: European Championships; USA: WOGA Classic | not found 2024-2025 |
| Yaroslav Krutov | MAG | BLR, RUS | BLR: Belarus Open Cup; RUS: Russian Championships | 2024: BLR |
| Nicolo Mozzato | MAG | FRA, ITA | FRA: Top 12 Series 2 2024 season; ITA: Italian Championships | 2024: ITA; 2025: ITA |
| Timm Sauter | MAG | GER, SUI | GER: German Junior Championships; SUI: Swiss Team Championships | 2024: GER; 2025: GER |
| Bogdan Ilyinkov | MAG | BLR, RUS | BLR/RUS: Russian Cup and Belarus Open Cup | 2024: BLR |
| Yoan Ivanov | MAG | BUL, GBR | BUL: European Youth Olympic Festival; GBR: Scottish Championships | 2024: BUL/GBR; 2025: BUL |
| Amber Ward Wen Si | WAG | AUS, HKG | AUS: Australian Championships; HKG: Singapore Open | 2024: HKG; 2025: HKG |

Questi casi dovranno essere verificati dall'admin nel CSV dedicato.

## 9. Name-order automatico

Durante la preview 2023 il tool ha applicato automaticamente la regola name-order:

| Voce | Conteggio |
|---|---:|
| Merge automatici name-order | 8 |
| Chiavi variante normalizzate | 8 |
| Record normalizzati | 52 |

Questa logica segue la decisione gia presa: quando nome e cognome sono invertiti, il tool non deve chiedere review admin ma normalizzare automaticamente verso l'ordine piu coerente con i result.

## 10. Stato operativo

Il 2023 non e stato importato nel database.

Prima del commit 2023 occorre:

1. completare `gymternet_2023_existing_athlete_match_review.csv`;
2. completare `gymternet_2023_new_athlete_country_conflicts.csv`;
3. generare il payload decisionale 2023;
4. rieseguire preview con decisioni applicate;
5. controllare eventuali conflitti post-decisione;
6. solo dopo preview pulita, eseguire commit controllato 2023.
