# LEVERAGE Import Contract

Questo documento definisce il contratto comune che ogni import automatico deve rispettare, indipendentemente dal formato sorgente.

## Importer supportati

- `manual_entry`: inserimento admin da UI, tramite `POST /events/{event_id}/results/bulk`.
- `gymternet_legacy`: import Gymternet storico/legacy, tramite `POST /imports/gymternet/preview` e `POST /imports/gymternet/commit`.
- `standard_2026_plus`: import futuro consigliato per file standardizzati con componenti di punteggio esplicite.

Gli importer possono avere parser diversi, ma devono convergere sugli stessi controlli prima del commit.

## Flusso comune

1. Parse del file o payload sorgente.
2. Normalizzazione dei valori LEVERAGE: athlete, event, discipline, category, apparatus, format, round, day, score components.
3. Preview admin con righe importabili, warning, duplicati e conflitti.
4. Review admin per problemi non risolvibili automaticamente.
5. Commit solo delle righe pulite o approvate.
6. Notifica admin cumulativa `import_summary` o `data_entry_summary`.

## Controlli comuni

Ogni importer deve rispettare:

- riconoscimento o creazione `Athlete`;
- suggerimento admin per atleta simile;
- gestione cambio country e `AthleteCountryChange`;
- creazione o aggiornamento semantico `Event`;
- coerenza `Result.discipline` con `Athlete.discipline`;
- coerenza `Result.discipline` e `Result.category` con `Event`;
- validazione apparatus MAG/WAG;
- validazione `vt_attempt` solo per `VT`;
- validazione `day >= 1`;
- validazione regole `Bonus`;
- validazione formula `score = D_score + E_score - Penalty + Bonus` quando le componenti sono esplicite;
- blocco duplicati sulla chiave `Result`: `athlete_id`, `event_id`, `discipline`, `category`, `apparatus`, `vt_attempt`, `day`, `format`, `round`;
- conflitto admin quando la stessa chiave `Result` ha `represented_country` diversa;
- preservazione di `represented_country` sul singolo `Result`.

## Regola Gymternet legacy dopo il 2025

Se il tool `gymternet_legacy` viene usato per dati successivi al 2025:

- applica le stesse regole Gymternet del 2025;
- marca `VT` come `vt_attempt=1` con `vault_attempt_order_uncertain=true`;
- per MAG ricostruisce `VT attempt 2` da `VT AVG` come final score e da `VT SUM` come D-score;
- per WAG ricostruisce solo il D-score di `VT attempt 2` da `VT SUM`, mentre il final score resta `NULL` / `not available`;
- al commit, i componenti non presenti `E_score`, `Penalty` e `Bonus` restano `NULL` / `not_available`, come nel 2025;
- il parser aggiunge un warning per segnalare che sta applicando la policy 2025 e che, se il file contiene componenti esplicite, e preferibile usare un import standard dedicato.

Questa regola rende Gymternet legacy utilizzabile come fallback anche dopo il 2025, ma il percorso consigliato per i dati futuri resta `standard_2026_plus`.

## Import standard 2026+

Un futuro import `standard_2026_plus` dovrebbe leggere direttamente:

- `score`;
- `D_score`;
- `E_score`;
- `Penalty`;
- `Bonus`;
- `vt_attempt`;
- `rank`;
- `day`;
- `represented_country`;
- `format`;
- `round`;
- `discipline`;
- `category`.

Se `Penalty` o `Bonus` sono vuoti in un file standard moderno, il backend puo interpretarli come `0.0`. Se `E_score` e vuoto, il file deve essere trattato come incompleto o bloccato.

Il nuovo importer non deve duplicare le regole Gymternet legacy: deve riusare i controlli comuni e avere parser/normalizzazione propri.
