# LEVERAGE - Preview e review import 2024

Data preview iniziale: 30 giugno 2026

Data preview post-review admin: 30 giugno 2026

File sorgente: `import_files/Results 2024.xlsx`

Stato: review admin completata e preview post-decisione pulita sul database locale popolato fino al commit reale 2023; database operativo non modificato.

## 1. Obiettivo

Questa preview controlla il file Gymternet 2024 sul database locale gia popolato con 2018, 2019, 2020, 2021, 2022 e 2023.

L'obiettivo e:

- verificare quanti result 2024 sono importabili;
- individuare duplicati, conflitti e warning;
- generare CSV di review admin per atleti/country e D-score orfani;
- applicare la nuova regola `same_country_review_reuse` sui casi gia verificati in anni precedenti;
- mantenere il database operativo invariato fino alla review admin.

## 2. File generati

| File | Scopo |
|---|---|
| `docs/import_reports/gymternet_2024_preview_summary.json` | Sintesi tecnica completa della preview 2024. |
| `docs/import_reports/gymternet_2024_duplicates.csv` | Audit dei duplicati identici interni al file; vuoto in questa preview. |
| `docs/import_reports/gymternet_2024_conflicts.csv` | Audit dei conflitti bloccanti; vuoto in questa preview. |
| `docs/import_reports/gymternet_2024_orphan_dscores.csv` | D-score orfani non agganciati a final score. |
| `docs/import_reports/gymternet_2024_athlete_review.csv` | Review atleta/country completa e tecnica. |
| `docs/import_reports/gymternet_2024_existing_athlete_match_review.csv` | CSV operativo per verificare match con atleti gia presenti nel DB. |
| `docs/import_reports/gymternet_2024_new_athlete_country_conflicts.csv` | CSV operativo per nuovi atleti con conflitti country nel file 2024. |
| `docs/import_reports/gymternet_2024_athlete_match_decisions.json` | Payload tecnico delle decisioni admin 2024. |
| `docs/import_reports/gymternet_2024_preview_with_decisions_summary.json` | Sintesi tecnica della preview 2024 con decisioni admin applicate. |
| `docs/import_reports/gymternet_2024_post_decision_conflicts.csv` | Audit conflitti dopo decisioni admin; vuoto dopo correzione finale. |
| `docs/import_reports/gymternet_2024_post_decision_duplicates.csv` | Audit duplicati dopo decisioni admin; vuoto. |

## 3. Sintesi preview

| Voce | Conteggio |
|---|---:|
| Righe parse | 106.449 |
| Result importabili | 106.449 |
| Athlete che verrebbero creati senza decisioni admin | 3.051 |
| Event che verrebbero creati | 206 |
| Duplicati identici interni al file | 0 |
| Conflitti bloccanti | 0 |
| Warning | 2 |

Warning:

- 1.113 D-score non agganciati a final score;
- assegnazione automatica `day` applicata a 5 chiavi multi-day, con 10 righe valorizzate fino a `day=2`.

## 4. Distribuzione anni nel file 2024

Il file `Results 2024.xlsx` contiene anche alcuni eventi marcati come anno evento 2025.

| Anno evento nel file | Result parse | Event distinti |
|---|---:|---:|
| 2024 | 105.954 | 203 |
| 2025 | 495 | 3 |

Eventi 2025 presenti nel file 2024:

| Event | Result parse |
|---|---:|
| `Top 12 Series 1 (2025)` | 203 |
| `Top 12 Series 2 (2025)` | 196 |
| `Top 12 Series 3 (2025)` | 96 |

Decisione metodologica: come per gli spillover gia rilevati nei file precedenti, questi record non sono considerati errore tecnico. Il sistema usa l'anno evento presente nel file sorgente.

## 5. Duplicati e conflitti

La preview 2024 non segnala duplicati identici interni al file e non segnala conflitti bloccanti.

| Controllo | Esito |
|---|---:|
| Duplicati identici | 0 |
| Conflitti bloccanti | 0 |

## 6. D-score orfani

Totale D-score orfani: 1.113.

Distribuzione per tipo problema:

| Tipo problema | Conteggio |
|---|---:|
| `athlete_missing_in_score_sheet` | 815 |
| `possible_athlete_name_typo` | 109 |
| `missing_final_score_for_context` | 95 |
| `possible_context_mismatch` | 64 |
| `possible_event_name_mismatch` | 24 |
| `missing_score_sheet_context` | 6 |

Decisione metodologica provvisoria: come per gli anni precedenti, questi D-score restano fuori dal database operativo salvo review mirata futura. Non vengono creati result autonomi con solo D-score.

## 7. Review atleta/country

Totale review atleta/country: 562.

Distribuzione:

| Tipo review | Conteggio |
|---|---:|
| `possible_existing_athlete_match` | 498 |
| `possible_athlete_identity_collision` | 41 |
| `possible_athlete_country_change` | 23 |

CSV operativi:

| File | Righe | Stato decisioni |
|---|---:|---|
| `gymternet_2024_existing_athlete_match_review.csv` | 552 | 211 decisioni precompilate da `same_country_review_reuse`; 341 righe ancora da controllare. |
| `gymternet_2024_new_athlete_country_conflicts.csv` | 10 | 10 righe ancora da controllare. |

Distribuzione delle 341 decisioni mancanti nel CSV existing athlete:

| Tipo review | Righe da controllare |
|---|---:|
| `possible_existing_athlete_match` | 287 |
| `possible_athlete_identity_collision` | 31 |
| `possible_athlete_country_change` | 23 |

Le 211 decisioni precompilate sono tutte `merge as same athlete` su casi same-country gia verificati in anni precedenti. Queste celle possono comunque essere corrette dall'admin se durante la review emergono nuove evidenze.

## 8. Conflitti country tra nuovi atleti

Il CSV `gymternet_2024_new_athlete_country_conflicts.csv` contiene 10 casi:

| Atleta | Disciplina | Country in conflitto | Evidenza futura |
|---|---|---|---|
| William Emard | MAG | CAN, FRA | 2025: CAN |
| Clovis Dias | MAG | FRA, POR | 2025: POR |
| Eliza Barbosa de Melo | WAG | GBR, HUN | not found 2025 |
| Anujin Gomboluudev | WAG | MGL, USA | 2025: MGL |
| Magdalena Andradottir | WAG | ISL, NOR | 2025: ISL |
| Rebecca Mitchell | WAG | CAN, DEN | 2025: DEN |
| Hanna Bjartalid | WAG | DEN, ISL | not found 2025 |
| Louay Sahli | MAG | ALG, TUN | 2025: FRA/TUN |
| Hjordis Petursdottir | WAG | DEN, ISL | not found 2025 |
| Jan Kies | MAG | BEL, NED | not found 2025 |

Questi casi richiedono decisione admin esplicita. Poiche cambia il country, la regola `same_country_review_reuse` non viene applicata.

## 9. Review admin completata

Il 30 giugno 2026 l'admin ha completato i file Numbers relativi alle collisioni atleta/country 2024.

Le decisioni sono state trasferite nei CSV operativi preservando i campi tecnici originali.

| File Numbers | Righe trasferite nel CSV operativo |
|---|---:|
| `gymternet_2024_existing_athlete_match_review.numbers` | 552 |
| `gymternet_2024_new_athlete_country_conflicts.numbers` | 10 |

Il trasferimento ha aggiornato soltanto:

- `decision`;
- `action`;
- `country`;
- `notes`.

Il payload tecnico generato e:

```text
docs/import_reports/gymternet_2024_athlete_match_decisions.json
```

### 9.1 Prima preview post-decisione

La prima preview con decisioni admin applicate ha prodotto:

| Voce | Conteggio |
|---|---:|
| Result importabili | 106.436 |
| Duplicati | 0 |
| Conflitti | 13 |

I 13 conflitti erano tutti del tipo:

```text
same_context_different_score_after_athlete_merge
```

Il backend ha riconosciuto la regola persistente:

```text
same_context_different_score_keep_separate
```

Significato: il merge tra due atleti avrebbe creato lo stesso identico contesto sportivo di result, ma con final score o D-score diversi. In questi casi la decisione corretta e mantenere separati gli atleti.

### 9.2 Correzioni post-preview

Sono state corrette tre decisioni nel CSV operativo `gymternet_2024_existing_athlete_match_review.csv`, portandole da `merge as same athlete` a `keep separate`:

| Atleta importato | Atleta gia presente suggerito | Motivo |
|---|---|---|
| Max Griffiths | Mac Griffiths | Merge produceva 7 result nello stesso contesto della `English Championships 2024` con score/D-score diversi. |
| Ania Fernandez | Jana Fernandez | Merge produceva 1 result nello stesso contesto della `Spanish League Final 2024` con score/D-score diverso. |
| Lee Seyeon | Lee Seoyeon | Merge produceva 5 result nello stesso contesto della `South Korean Championships 2024` con score/D-score diversi. |

Queste correzioni sono coerenti con la regola gia stabilita negli anni precedenti: quando due atleti simili, anche con stessa country, generano stesso contesto sportivo ma punteggi diversi, devono restare entita separate.

## 10. Preview post-decisione pulita

Dopo le tre correzioni, il payload decisionale e stato rigenerato senza rileggere i Numbers, usando i CSV operativi come fonte autorevole.

Esito finale preview post-decisione:

| Voce | Conteggio |
|---|---:|
| Righe parse | 106.449 |
| Result importabili | 106.449 |
| Athlete che verrebbero creati | 2.535 |
| Event che verrebbero creati | 206 |
| Duplicati | 0 |
| Conflitti | 0 |
| Warning | 2 |
| D-score orfani mantenuti fuori dal DB | 1.113 |

Statistiche decisioni atleta/country applicate:

| Azione | Conteggio |
|---|---:|
| Suggerimenti atleta accettati | 459 |
| Nuovi atleti confermati / creati come separati | 39 |
| Merge identita atleta | 41 |
| Country updates | 20 |
| Country kept | 9 |
| Correzioni represented country | 39 |
| Correzioni nome atleta | 0 |
| Decisioni non valide | 0 |
| Decisioni irrisolte | 0 |

La preview finale ha generato:

```text
docs/import_reports/gymternet_2024_preview_with_decisions_summary.json
docs/import_reports/gymternet_2024_post_decision_conflicts.csv
docs/import_reports/gymternet_2024_post_decision_duplicates.csv
```

I file `post_decision_conflicts` e `post_decision_duplicates` risultano vuoti.

## 11. Stato operativo

Il database locale non e stato modificato.

Prossimo passo: eseguire il commit reale controllato del file 2024 sul database operativo, mantenendo backup e report tecnico di commit come gia fatto per gli anni precedenti.
