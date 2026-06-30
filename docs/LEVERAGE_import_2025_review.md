# LEVERAGE - Preview e review import 2025

Data preview iniziale: 30 giugno 2026

Data preview post-review admin: 30 giugno 2026

File sorgente: `import_files/Results 2025.xlsx`

Stato: review admin completata, preview post-decisione pulita, commit reale 2025 eseguito sul DB locale.

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
| `docs/import_reports/gymternet_2025_athlete_name_corrections.csv` | Correzione nome atleta esistente verificata dall'admin. |
| `docs/import_reports/gymternet_2025_athlete_match_decisions.json` | Payload tecnico delle decisioni admin 2025. |
| `docs/import_reports/gymternet_2025_preview_with_decisions_summary.json` | Sintesi tecnica della preview 2025 con decisioni admin applicate. |
| `docs/import_reports/gymternet_2025_post_decision_conflicts.csv` | Audit conflitti dopo decisioni admin; vuoto dopo correzione finale. |
| `docs/import_reports/gymternet_2025_post_decision_duplicates.csv` | Audit duplicati dopo decisioni admin; vuoto. |
| `docs/import_reports/gymternet_2025_commit_summary.json` | Report tecnico del commit reale 2025, con backup, statistiche di import e controlli post-import. |

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

## 9. Review admin completata

Il 30 giugno 2026 l'admin ha completato i file Numbers relativi alle collisioni atleta/country 2025.

Le decisioni sono state trasferite nei CSV operativi preservando i campi tecnici originali.

| File Numbers | Righe trasferite nel CSV operativo |
|---|---:|
| `gymternet_2025_existing_athlete_match_review.numbers` | 628 |
| `gymternet_2025_new_athlete_country_conflicts.numbers` | 8 |

Il trasferimento ha aggiornato soltanto:

- `decision`;
- `action`;
- `country`;
- `notes`.

Inoltre e stata aggiunta una correzione nome atleta esistente:

| Review | Athlete ID | Nome precedente | Nome corretto |
|---|---:|---|---|
| `athlete_match_5181b096d32f4b0a` | 18410 | Niccolo Martin | Niccolò Martin |

Il payload tecnico generato e:

```text
docs/import_reports/gymternet_2025_athlete_match_decisions.json
```

### 9.1 Prima preview post-decisione

La prima preview con decisioni admin applicate ha prodotto:

| Voce | Conteggio |
|---|---:|
| Result importabili | 123.997 |
| Duplicati | 0 |
| Conflitti | 33 |

I 33 conflitti erano tutti del tipo:

```text
same_context_different_score_after_athlete_merge
```

Il backend ha riconosciuto la regola persistente:

```text
same_context_different_score_keep_separate
```

Significato: il merge tra due atleti avrebbe creato lo stesso identico contesto sportivo di result, ma con final score o D-score diversi. In questi casi la decisione corretta e mantenere separati gli atleti.

### 9.2 Correzioni post-preview

Sono state corrette sette decisioni nel CSV operativo `gymternet_2025_existing_athlete_match_review.csv`, portandole da `merge as same athlete` a `keep separate`:

| Atleta importato | Atleta gia presente suggerito | Motivo |
|---|---|---|
| Saya Okubo | Aya Okubo | Merge produceva 5 result nello stesso contesto della `All-Japan Junior Championships 2025` con score diversi. |
| Anna Klykova | Anna Kalmykova | Merge produceva 4 result nello stesso contesto della `Russian Championships 2025` con score/D-score diversi. |
| Mia Fujiwara | Mirea Fujiwara | Merge produceva 5 result nello stesso contesto della `All-Japan Student Championships 2025` con score/D-score diversi. |
| Marta Garcia | Maria Garcia | Merge produceva 1 result nello stesso contesto della `2nd Spanish League 2025` con score/D-score diverso. |
| Lee Sooyeon | Lee Seoyeon | Merge produceva 5 result nello stesso contesto della `South Korean Championships 2025` con score/D-score diversi. |
| Lee Jiyeon | Lee Jiseon | Merge produceva 10 result negli stessi contesti della `Korean National Sports Festival 2025` e `South Korean Championships 2025` con score/D-score diversi. |
| Zeng Yifan | Zeng Yiran | Merge produceva 3 result nello stesso contesto della `Chinese Junior Championships 2025` con score/D-score diversi. |

Queste correzioni sono coerenti con la regola gia stabilita negli anni precedenti: quando due atleti simili, anche con stessa country, generano stesso contesto sportivo ma punteggi diversi, devono restare entita separate.

## 10. Preview post-decisione pulita

Dopo le sette correzioni, il payload decisionale e stato rigenerato senza rileggere i Numbers, usando i CSV operativi come fonte autorevole.

Esito finale preview post-decisione:

| Voce | Conteggio |
|---|---:|
| Righe parse | 124.030 |
| Result importabili | 124.030 |
| Athlete che verrebbero creati | 2.911 |
| Event che verrebbero creati | 222 |
| Duplicati | 0 |
| Conflitti | 0 |
| Warning | 3 |
| D-score orfani mantenuti fuori dal DB | 630 |

Statistiche decisioni atleta/country applicate:

| Azione | Conteggio |
|---|---:|
| Suggerimenti atleta accettati | 451 |
| Nuovi atleti confermati / creati come separati | 85 |
| Merge identita atleta | 69 |
| Country updates | 15 |
| Country kept | 21 |
| Correzioni represented country | 75 |
| Correzioni nome atleta | 1 |
| Decisioni non valide | 0 |
| Decisioni irrisolte | 0 |

La preview finale ha generato:

```text
docs/import_reports/gymternet_2025_preview_with_decisions_summary.json
docs/import_reports/gymternet_2025_post_decision_conflicts.csv
docs/import_reports/gymternet_2025_post_decision_duplicates.csv
```

I file `post_decision_conflicts` e `post_decision_duplicates` risultano vuoti.

## 11. Commit reale 2025

Prima del commit reale e stato creato il backup:

```text
backups/leverage_pre_import_2025_20260630_220340.db
```

Il commit reale e stato eseguito usando:

```text
scripts/commit_gymternet_year.py
```

Report tecnico generato:

```text
docs/import_reports/gymternet_2025_commit_summary.json
```

Statistiche commit:

| Voce | Conteggio |
|---|---:|
| Athlete creati | 2.911 |
| Event creati | 222 |
| Result creati | 124.030 |
| Result completi creati | 95.229 |
| Result parziali creati | 28.801 |
| Event aggiornati | 284 |
| Country atleta aggiornate | 15 |
| Nomi atleta aggiornati | 1 |
| `represented_country` corretti sui result | 637 |
| Atleti con nuovi result | 9.442 |
| Event con nuovi result | 222 |
| Duplicati saltati | 0 |
| D-score orfani lasciati fuori dal DB | 630 |

Stato DB dopo il commit:

| Entita | Conteggio |
|---|---:|
| Athlete | 26.259 |
| Event | 1.605 |
| Result | 753.723 |
| Notification | 0 |

## 12. Controlli post-import 2025

Distribuzione result per anno dopo il commit:

| Anno evento | Result |
|---|---:|
| 2018 | 89.988 |
| 2019 | 106.084 |
| 2020 | 34.326 |
| 2021 | 77.423 |
| 2022 | 97.075 |
| 2023 | 117.256 |
| 2024 | 107.046 |
| 2025 | 124.417 |
| 2026 | 108 |

Nota metodologica: il file `Results 2025.xlsx` contiene anche 108 record associati a evento con anno evento 2026 (`Top 12 Series 3 (2026)`). Per questo il commit del file 2025 ha portato il totale dell'anno 2025 a 124.417 result e ha creato 108 result su eventi 2026.

Qualita dati importati dal commit 2025:

| Anno evento | Result completi | Final score senza D-score | Senza final score |
|---|---:|---:|---:|
| 2025 | 95.604 | 25.625 | 3.188 |
| 2026 | 95 | 13 | 0 |

Nota sui result senza final score: nel legacy Gymternet 2025 alcuni result possono essere conservati senza final score quando il dato non e ricostruibile in modo affidabile, in particolare per le regole 2025+ su componenti mancanti e vault. Questi record restano marcati come incompleti/not available e vanno trattati con cautela in UI e analisi.

Controllo duplicati semantici:

| Controllo | Esito |
|---|---:|
| Gruppi duplicati semantici | 0 |

## 13. Stato operativo finale

Il 2025 e stato importato nel database locale.

Il commit reale ha creato 124.030 result nuovi e non ha introdotto duplicati semantici.

I 630 D-score orfani sono stati conservati in `docs/import_reports/gymternet_2025_orphan_dscores.csv` per eventuale recupero futuro, ma non sono stati importati nel database operativo.

Il database contiene gia 108 result associati a evento 2026. Quando verra importato il file Gymternet 2026, questi result dovranno essere considerati nel controllo duplicati/preflight.
