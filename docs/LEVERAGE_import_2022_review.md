# LEVERAGE - Preview e review import 2022

Data preview iniziale: 25 giugno 2026
Data review/commit: 30 giugno 2026

File sorgente: `import_files/Results 2022.xlsx`

Stato: review admin completata, preview post-decisione pulita, commit reale 2022 eseguito sul DB locale

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
| `docs/import_reports/gymternet_2022_athlete_match_decisions.json` | Payload tecnico prodotto dalle decisioni admin atleta/country 2022. |
| `docs/import_reports/gymternet_2022_preview_with_decisions_summary.json` | Preview post-decisione eseguita su copia temporanea del DB. |
| `docs/import_reports/gymternet_2022_post_decision_conflicts.csv` | Audit dei conflitti post-decisione; rigenerato vuoto dopo la correzione Liu Xuanxi/Liu Xuan. |
| `docs/import_reports/gymternet_2022_post_decision_duplicates.csv` | Audit dei duplicati identici residui dopo le decisioni. |
| `docs/import_reports/gymternet_2022_commit_summary.json` | Report tecnico del commit reale 2022, con backup, statistiche di import e controlli post-import. |

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

## 9. Review admin e payload decisionale

Il 30 giugno 2026 sono stati letti i file Numbers compilati dall'admin:

| File Numbers | Righe trasferite nel CSV operativo |
|---|---:|
| `gymternet_2022_existing_athlete_match_review.numbers` | 386 |
| `gymternet_2022_new_athlete_country_conflicts.numbers` | 3 |

Le decisioni sono state normalizzate nei valori tecnici usati dal backend.

| Azione payload | Conteggio finale |
|---|---:|
| `merge_as_same_athlete` | 44 |
| `accept_suggestion` | 305 |
| `create_new` | 15 |
| `update_country` | 17 |
| `keep_existing_country` | 8 |

Il payload finale contiene 389 decisioni e si trova in:

```text
docs/import_reports/gymternet_2022_athlete_match_decisions.json
```

## 10. Conflitto post-decisione risolto

La prima preview post-decisione ha prodotto 7 conflitti, tutti relativi allo stesso caso:

| Atleta importato | Atleta suggerito | Evento | Tipo conflitto |
|---|---|---|---|
| Liu Xuanxi | Liu Xuan | Chinese Youth Championships 2022 | stesso contesto sportivo ma score/D-score diversi su FX, HB, PB, PH, SR, VT e AA |

Decisione metodologica applicata: usare la regola gia consolidata `same_context_different_score_keep_separate`.

La riga `athlete_match_beec068c68fc0008` e stata quindi corretta nel CSV operativo come `keep separate`, con nota esplicita. Dopo questa correzione la preview post-decisione e risultata pulita.

| Controllo preview post-decisione finale | Esito |
|---|---:|
| Conflitti | 0 |
| Decisioni invalide | 0 |
| Decisioni mancanti | 0 |
| Duplicati identici residui | 3 |

I 3 duplicati identici residui sono gli stessi duplicati interni di Lee Junho gia rilevati in preview iniziale e vengono saltati automaticamente in commit.

## 11. Commit reale 2022

Prima del commit reale e stato creato il backup:

```text
backups/leverage_pre_import_2022_20260630_094008.db
```

Statistiche commit:

| Voce | Conteggio |
|---|---:|
| Athlete creati | 2.472 |
| Event creati | 219 |
| Result creati | 97.934 |
| Result completi creati | 74.032 |
| Result parziali creati | 23.902 |
| Event aggiornati | 249 |
| Country atleta aggiornate | 19 |
| Nomi atleta aggiornati | 0 |
| `represented_country` corretti sui result | 261 |
| Atleti con nuovi result | 7.265 |
| Event con nuovi result | 219 |
| Duplicati saltati | 3 |
| D-score orfani lasciati fuori dal DB | 1.426 |

Stato DB dopo il commit:

| Entita | Conteggio |
|---|---:|
| Athlete | 17.429 |
| Event | 936 |
| Result | 405.755 |
| Notification | 0 |

## 12. Controlli post-import 2022

Distribuzione result per anno evento dopo il commit:

| Anno evento | Result |
|---|---:|
| 2018 | 89.988 |
| 2019 | 106.084 |
| 2020 | 34.326 |
| 2021 | 77.423 |
| 2022 | 97.075 |
| 2023 | 859 |

Nota metodologica: il file sorgente `Results 2022.xlsx` contiene anche alcuni eventi marcati come anno evento 2023. Per questo il commit 2022 ha creato 97.075 result associati a eventi 2022 e 859 result associati a eventi 2023.

Qualita dati dei result creati dal commit 2022:

| Anno evento | Completi | Final score senza D-score | Senza final score |
|---|---:|---:|---:|
| 2022 | 73.237 | 23.838 | 0 |
| 2023 | 795 | 64 | 0 |

Controllo duplicati semantici:

| Controllo | Esito |
|---|---:|
| Gruppi duplicati semantici | 0 |

## 13. Stato operativo finale

Il 2022 e stato importato nel database locale.

Il commit reale ha creato 97.934 result nuovi e non ha introdotto duplicati semantici.

I 1.426 D-score orfani sono stati conservati in `docs/import_reports/gymternet_2022_orphan_dscores.csv` per eventuale recupero futuro, ma non sono stati importati nel database operativo.
