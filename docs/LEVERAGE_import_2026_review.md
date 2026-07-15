# LEVERAGE - Preview e review import 2026

Data preview iniziale: 14 luglio 2026

File sorgente: `import_files/Results 2026.xlsx`

Stato: preview iniziale completata, nessun commit reale eseguito sul DB locale, review admin da completare.

## 1. Obiettivo

Questa preview controlla il file Gymternet 2026 sul database locale gia popolato con Results e Calendar 2018-2025.

L'obiettivo e:

- verificare quanti result 2026 sono importabili;
- controllare eventuali sovrapposizioni con i 108 result 2026 gia importati dallo spillover del file 2025;
- individuare duplicati, conflitti e warning;
- generare CSV di review admin per atleti/country e D-score orfani;
- applicare la regola `same_country_review_reuse` sui casi same-country gia verificati in anni precedenti;
- mantenere il database operativo invariato fino alla review admin.

## 2. Correzione preliminare mapping country

Durante la prima preview sono emersi warning su country non ancora mappati:

- `Togo`;
- `Mali`;
- `DR Congo`.

Prima di consegnare i CSV di review all'admin, il mapping e stato corretto nel backend/importer:

| Nome nel file sorgente | Codice salvato |
|---|---|
| `Togo` | `TOG` |
| `Mali` | `MLI` |
| `DR Congo` | `COD` |
| `Democratic Republic of Congo` | `COD` |

E stato aggiunto un test di regressione in `tests/test_api.py` per evitare che questi alias tornino a produrre warning in futuro.

## 3. File generati

| File | Scopo |
|---|---|
| `docs/import_reports/gymternet_2026_preview_summary.json` | Sintesi tecnica completa della preview 2026. |
| `docs/import_reports/gymternet_2026_duplicates.csv` | Audit dei duplicati identici interni al file. |
| `docs/import_reports/gymternet_2026_conflicts.csv` | Audit dei conflitti bloccanti; vuoto in questa preview. |
| `docs/import_reports/gymternet_2026_orphan_dscores.csv` | D-score orfani non agganciati a final score. |
| `docs/import_reports/gymternet_2026_athlete_review.csv` | Review atleta/country completa e tecnica. |
| `docs/import_reports/gymternet_2026_existing_athlete_match_review.csv` | CSV operativo per verificare match con atleti gia presenti nel DB. |
| `docs/import_reports/gymternet_2026_new_athlete_country_conflicts.csv` | CSV operativo per nuovi atleti con conflitti country nel file 2026. |

## 4. Sintesi preview

| Voce | Conteggio |
|---|---:|
| Righe parse | 66.017 |
| Result importabili | 66.016 |
| Athlete che verrebbero creati senza decisioni admin | 2.029 |
| Event che verrebbero creati | 114 |
| Duplicati identici interni al file | 1 |
| Conflitti bloccanti | 0 |
| Warning | 3 |

Warning:

- 287 D-score non agganciati a final score;
- assegnazione automatica `day` applicata a 22 chiavi multi-day, con 44 righe valorizzate fino a `day=2`;
- il legacy Gymternet import ha rilevato result successivi al 2025 e applica le regole 2025 su vault e componenti mancanti. E_score, Penalty e Bonus mancanti restano `not available`.

## 5. Controllo spillover 2025

Prima della preview era gia presente nel DB un Event 2026 generato dal file 2025:

| Event ID | Event | Result gia presenti |
|---:|---|---:|
| 1584 | `Top 12 Series 3 (2026)` | 108 |

La preview 2026 non ha rilevato duplicati contro il DB gia esistente. Il duplicato individuato e solo interno al file 2026.

## 6. Duplicati e conflitti

| Controllo | Esito |
|---|---:|
| Duplicati identici | 1 |
| Conflitti bloccanti | 0 |

Duplicato interno rilevato:

| Event | Athlete | Country | Discipline | Category | Apparatus | Format | Round | Score | Source row |
|---|---|---|---|---|---|---|---|---:|---:|
| `Fuzion National Qualifier` | `Elaina Sliney` | USA | WAG | senior | FX | individual | final | 12.600 | 1948 |

Decisione metodologica provvisoria: il duplicato identico interno al file puo essere ignorato/skippato dal tool durante il commit reale, salvo diversa verifica admin.

## 7. D-score orfani

Totale D-score orfani: 287.

Distribuzione per tipo problema:

| Tipo problema | Conteggio |
|---|---:|
| `possible_context_mismatch` | 159 |
| `athlete_missing_in_score_sheet` | 54 |
| `missing_final_score_for_context` | 40 |
| `possible_athlete_name_typo` | 32 |
| `possible_event_name_mismatch` | 2 |

Decisione metodologica provvisoria: come per gli anni precedenti, questi D-score restano fuori dal database operativo salvo review mirata futura. Non vengono creati result autonomi con solo D-score.

## 8. Review atleta/country

Totale review atleta/country: 414.

Distribuzione:

| Tipo review | Conteggio |
|---|---:|
| `possible_existing_athlete_match` | 327 |
| `possible_athlete_country_change` | 47 |
| `possible_athlete_identity_collision` | 40 |

CSV operativi:

| File | Righe | Stato decisioni |
|---|---:|---|
| `gymternet_2026_existing_athlete_match_review.csv` | 407 | 166 decisioni precompilate da `same_country_review_reuse`; 241 righe ancora da controllare. |
| `gymternet_2026_new_athlete_country_conflicts.csv` | 7 | 7 righe ancora da controllare. |

Distribuzione delle 241 decisioni mancanti nel CSV existing athlete:

| Tipo review | Righe da controllare |
|---|---:|
| `possible_existing_athlete_match` | 161 |
| `possible_athlete_country_change` | 47 |
| `possible_athlete_identity_collision` | 33 |

Le 166 decisioni precompilate sono tutte casi same-country gia verificati in anni precedenti. Queste celle possono comunque essere corrette dall'admin se durante la review emergono nuove evidenze.

## 9. Conflitti country tra nuovi atleti

Il CSV `gymternet_2026_new_athlete_country_conflicts.csv` contiene 7 casi:

| Atleta | Disciplina | Country in conflitto | Evidenza futura |
|---|---|---|---|
| Sam Rakita | MAG | CAN, USA | non disponibile: set storico fermo al primo semestre 2026 |
| Reece Landsperger | MAG | CAN, USA | non disponibile: set storico fermo al primo semestre 2026 |
| Jordan Carroll | MAG | CAN, USA | non disponibile: set storico fermo al primo semestre 2026 |
| Anna Alekseeva | WAG | GER, RUS | non disponibile: set storico fermo al primo semestre 2026 |
| Santiago Rojas | MAG | COL, MEX | non disponibile: set storico fermo al primo semestre 2026 |
| Fabian Benedek | MAG | GER, HUN | non disponibile: set storico fermo al primo semestre 2026 |
| Emily Moorhead | WAG | GBR, IRL | non disponibile: set storico fermo al primo semestre 2026 |

Poiche cambia il country, la regola `same_country_review_reuse` non viene applicata. Serve decisione admin esplicita.

## 10. Stato operativo

Il DB locale e rimasto invariato dopo la preview:

| Controllo DB | Valore |
|---|---:|
| Event 2026 presenti prima e dopo la preview | 1 |
| Result 2026 presenti prima e dopo la preview | 108 |

Test eseguito:

```text
.venv/bin/python -m pytest tests/test_api.py::test_gymternet_country_aliases_cover_results_files
```

Esito: passato.

## 11. Prossimi passi

1. L'admin compila i CSV operativi:
   - `docs/import_reports/gymternet_2026_existing_athlete_match_review.csv`;
   - `docs/import_reports/gymternet_2026_new_athlete_country_conflicts.csv`.
2. Le decisioni vengono trasferite dai file Numbers ai CSV operativi con lo script dedicato.
3. Viene generato il payload `gymternet_2026_athlete_match_decisions.json`.
4. Si esegue una preview post-decisione.
5. Se la preview post-decisione e pulita, si procede con backup locale e commit reale del 2026.
6. Dopo il commit Results 2026, si passa alla riconciliazione Calendar 2026.

## 12. Review admin completata

Il 14 luglio 2026 l'admin ha completato i file Numbers relativi alle collisioni atleta/country 2026.

Le decisioni sono state trasferite nei CSV operativi preservando i campi tecnici originali.

| File Numbers | Righe trasferite nel CSV operativo |
|---|---:|
| `gymternet_2026_existing_athlete_match_review.numbers` | 407 |
| `gymternet_2026_new_athlete_country_conflicts.numbers` | 7 |

Il trasferimento ha aggiornato soltanto:

- `decision`;
- `action`;
- `country`;
- `notes`.

Inoltre e stata aggiunta una correzione nome atleta esistente:

| Review | Athlete ID | Nome precedente | Nome corretto |
|---|---:|---|---|
| `athlete_match_d7eb122b7c46b2a0` | 21148 | Francesco Berarellt | Francesco Bertarelli |

Il payload tecnico generato e:

```text
docs/import_reports/gymternet_2026_athlete_match_decisions.json
```

Distribuzione iniziale delle azioni nel payload:

| Azione | Conteggio |
|---|---:|
| `accept_suggestion` | 287 |
| `create_new` | 40 |
| `merge_as_same_athlete` | 40 |
| `keep_existing_country` | 32 |
| `update_country` | 15 |

## 13. Prima preview post-decisione

La prima preview con decisioni admin applicate ha prodotto:

| Controllo | Conteggio |
|---|---:|
| Decisioni applicate | 414 |
| Decisioni irrisolte | 0 |
| Decisioni invalide | 0 |
| Duplicati identici | 1 |
| Conflitti post-decisione | 10 |

I 10 conflitti erano tutti riconducibili allo stesso caso:

| Athlete importato | Athlete suggerito | Evento | Problema |
|---|---|---|---|
| Julianne Thibault | Julia Thibault | Canadian Championships 2026 | stesso contesto Result, punteggi diversi |

Decisione metodologica applicata: secondo la regola persistente `same_context_different_score_keep_separate`, il merge e stato corretto in `keep separate`.

La riga corretta nel CSV operativo e:

```text
athlete_match_b99769b3ed6d5e29
```

La nota inserita e:

```text
Post-decision conflict review: same context with different scores; keep separate.
```

Il payload decisionale e stato quindi rigenerato dai CSV con `--skip-numbers`, per non sovrascrivere la correzione post-preview con il valore precedente presente nel file Numbers.

Distribuzione finale delle azioni nel payload:

| Azione | Conteggio |
|---|---:|
| `accept_suggestion` | 286 |
| `create_new` | 41 |
| `merge_as_same_athlete` | 40 |
| `keep_existing_country` | 32 |
| `update_country` | 15 |

## 14. Preview post-decisione finale

La seconda preview post-decisione e risultata pulita:

| Controllo | Conteggio |
|---|---:|
| Righe parse | 66.017 |
| Result importabili | 66.016 |
| Duplicati identici | 1 |
| Conflitti | 0 |
| Decisioni irrisolte | 0 |
| Decisioni invalide | 0 |
| D-score orfani lasciati fuori dal DB | 287 |

Il duplicato residuo e sempre il duplicato identico interno al file:

| Event | Athlete | Country | Discipline | Category | Apparatus | Format | Round | Score |
|---|---|---|---|---|---|---|---|---:|
| `Fuzion National Qualifier` | `Elaina Sliney` | USA | WAG | senior | FX | individual | final | 12.600 |

## 15. Commit reale 2026

Il commit reale del file `Results 2026.xlsx` e stato eseguito il 14 luglio 2026.

Report tecnico:

```text
docs/import_reports/gymternet_2026_commit_summary.json
```

Statistiche principali:

| Voce | Conteggio |
|---|---:|
| Athlete creati | 1.662 |
| Event creati | 114 |
| Result creati | 66.016 |
| Result completi creati | 53.496 |
| Result parziali creati | 12.520 |
| D-score orfani non importati | 287 |
| Event aggiornati | 138 |
| Athlete country aggiornati | 19 |
| Athlete name aggiornati | 1 |
| Represented country corretti | 421 |
| Athlete con nuovi result | 6.378 |
| Event con nuovi result | 114 |
| Duplicati skippati | 1 |

Conteggi DB dopo il commit:

| Entita | Conteggio |
|---|---:|
| Athlete | 27.921 |
| Event | 1.719 |
| Result | 819.739 |

Distribuzione Result dopo il commit:

| Anno evento | Result |
|---:|---:|
| 2018 | 89.988 |
| 2019 | 106.084 |
| 2020 | 34.326 |
| 2021 | 77.423 |
| 2022 | 97.075 |
| 2023 | 117.256 |
| 2024 | 107.046 |
| 2025 | 124.417 |
| 2026 | 66.124 |

Controllo duplicati semantici post-import:

| Controllo | Conteggio |
|---|---:|
| Gruppi duplicati semantici | 0 |

Qualita dati 2026:

| Qualita | Result |
|---|---:|
| Completi con score e D_score | 53.591 |
| Con final score ma senza D_score | 10.934 |
| Senza final score | 1.599 |

## 16. Nota backup commit 2026

Durante il commit reale lo script ha riportato `backup_path: null`, perche accettava un parametro `--backup` ma non creava un backup automatico se il parametro non veniva passato.

Subito dopo il commit e stata creata una copia post-commit del DB:

```text
backups/leverage_gymternet_2026_post_commit_20260714_202134.db
```

La procedura tecnica e stata corretta: da ora `scripts/commit_gymternet_year.py` crea automaticamente un backup pre-commit in `backups/` quando `--backup` non viene specificato.

## 17. Stato finale Results 2026

Lo stato finale della fase Results 2026 e:

- review admin completata;
- payload decisionale generato;
- correzione `Francesco Berarellt` -> `Francesco Bertarelli` applicata;
- conflitto `Julianne Thibault` / `Julia Thibault` risolto con `keep separate`;
- preview post-decisione pulita;
- commit reale eseguito;
- D-score orfani conservati nei report e non importati come result autonomi;
- duplicati semantici post-import pari a 0.

## 18. Chiusura Calendar 2026 collegata al Results 2026

La riconciliazione Calendar 2026 e stata completata il 15 luglio 2026 per il perimetro disponibile al primo semestre.

Report principali:

| Report | Contenuto |
|---|---|
| `docs/import_reports/calendar_2026_commit_summary.json` | Commit automatico sicuro e conflitti source Bundesliga |
| `docs/import_reports/calendar_2026_current_review_commit_summary.json` | Applicazione decisioni admin correnti |
| `docs/import_reports/calendar_2026_current_match_summary.csv` | Copertura finale Calendar/Event 2026 |
| `docs/import_reports/calendar_2026_db_only_events.csv` | Event DB 2026 senza riga Calendar sorgente |
| `docs/import_reports/calendar_2026_top12_commit_summary.json` | Decisioni Top 12 2026 |

Esito finale:

| Metrica | Valore |
|---|---:|
| Righe Calendar 2026 | 170 |
| Event DB 2026 | 115 |
| Event DB 2026 coperti | 115 |
| Event DB 2026 non coperti | 0 |
| Righe Calendar future/in standby | 45 |
| Event `db_only` | 2 |
| Righe `calendar_only` | 5 |
| Collegamenti `season_year_spillover` | 1 |

Decisioni specifiche:

- `Ifact Norges Cup 1/2`: `calendar_only`;
- `Colombian Championships`: `db_only`, per assenza di riscontro nel Calendar 2026 sorgente;
- `Romanian Euros Trials`: `db_only`;
- `Top 12 Series 3 (2026)` WAG: collegamento al Calendar 2025 come `season_year_spillover`;
- eventi Bundesliga: conservazione delle date multiple tramite `EventCalendarEntry`.

La fase Results + Calendar 2026 primo semestre e quindi chiusa.
