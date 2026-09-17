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
- merge automatico `merge name order` per nomi atleta in ordine invertito o formato equivalente nello stesso file;
- review admin solo se, dopo il merge automatico del nome, emergono country diverse o altri conflitti non risolvibili automaticamente;
- gestione cambio country e `AthleteCountryChange`;
- correzione esplicita del nome di un atleta target gia presente quando l'admin verifica che la scheda esistente contiene un errore di data entry;
- creazione o aggiornamento semantico `Event`;
- coerenza `Result.discipline` con `Athlete.discipline`;
- coerenza `Result.discipline` e `Result.category` con `Event`;
- validazione apparatus MAG/WAG;
- validazione `vt_attempt` solo per `VT`;
- validazione `day >= 1`;
- validazione regole `Bonus`;
- validazione formula `score = D_score + E_score - Penalty + Bonus` quando le componenti sono esplicite;
- validazione upper bound del final score: i result non-AA non possono superare `20.0`, mentre `AA` puo superare `20.0` perche rappresenta la somma di piu apparati;
- validazione upper bound del `D_score`: il valore salvato non puo superare `10.0`; valori sorgente Gymternet tra `10.0` e `20.0` vengono trattati come errori non affidabili e non importati come D-score;
- validazione upper bound dell'`E_score`: il valore ufficiale salvato deve essere compreso tra `0.0` e `10.0`;
- validazione della `execution_estimate`: quando `E_score` non e disponibile e il sistema usa `score - D_score` come stima, la stima deve essere compresa tra `0.0` e `10.0`; in caso contrario il `D_score` non e considerato affidabile e deve essere marcato `NULL` / `not available`;
- blocco duplicati sulla chiave `Result`: `athlete_id`, `event_id`, `discipline`, `category`, `apparatus`, `vt_attempt`, `day`, `format`, `round`;
- conflitto admin quando la stessa chiave `Result` ha `represented_country` diversa;
- preservazione di `represented_country` sul singolo `Result`.
- correzione esplicita di `represented_country` solo quando l'admin stabilisce che una country sorgente e un errore di data entry. Nei casi di reale cambio nazionalita/rappresentanza, i Result devono preservare la country storica.

## Inferenza `Event.level`

Ogni importer che crea o aggiorna eventi deve applicare le stesse regole semantiche per `Event.level`:

- `Olympic Games` viene assegnato solo a eventi contenenti `Olympic Games` o denominati esattamente `Olympics`;
- `World Championships`, `Continental Championships`, `World Cup` e `World Challenge Cup` restano associati ai rispettivi nomi ufficiali;
- `Trial`/`Trials`, `Bundesliga`, `Serie A`, `Top 12`, `NCAA`, `Spanish League` e `South African Championships` hanno precedenza nazionale e devono essere classificati come `National Event`;
- anche `National Games`, `National Sports Festival`, `National Team`, `National Qualifier`, `National League`, `National Cup`, `National Selection`, `National Review`, `National Camp` e `National Test` sono `National Event`;
- i campionati domestici con prefisso nazionale riconoscibile, ad esempio `Chinese Championships`, `All-Japan Championships`, `British Championships`, `French Championships`, `U.S. Championships`, `Australian Championships`, ecc., sono `National Event`;
- i refusi sorgente evidenti `Bundlesiga` e `National Spots Festival` devono essere trattati come `Bundesliga` e `National Sports Festival`, producendo correzione/normalizzazione del nome evento quando possibile;
- `Asian Junior Championships`, `Junior Pan Am Championships`, `Junior Pan American Championships` e `Oceania Championships` sono `Continental Championships`;
- `Olympic Hopes Cup`, `Worlds Preparation Event`, `Northern European Championships`, `COMEGYM Championships`, `Klaverblad Championships`, `Liepaja Championships` e `Platinum League Online` sono `International Event`;
- gli override espliciti hanno precedenza sulle regole generali basate su parole come `Worlds`, `European` o `African`.

## Suffissi Gymternet nel nome gara

Nei file Gymternet legacy, alcuni suffissi finali nel campo `Event` non fanno parte del nome reale della gara, ma indicano il contesto del result. Il parser deve rimuoverli dal nome evento e salvarli come `Result.round` / `Result.format`:

- `QF` -> `round=qualification`, `format=individual`;
- `TF` -> `round=final`, `format=team`;
- `AA` -> `round=final`, `format=individual`;
- `EF` -> `round=final`, `format=apparatus`;
- `MT` -> `round=final`, `format=mixed team`.

Esempio: `European Championships MT` deve essere aggregato all'evento `European Championships`, salvando i relativi result come `mixed team final`.

Per i result `MT`, il profilo attrezzi atteso e:

- MAG: `FX`, `PB`, `HB`;
- WAG: `BB`, `UB`, `FX`.

Se un import `MT` contiene attrezzi diversi da questo profilo, il parser deve generare un warning di review admin nella preview. Il warning non blocca automaticamente l'import, ma segnala che il suffisso `MT` deve essere verificato prima di procedere.

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
