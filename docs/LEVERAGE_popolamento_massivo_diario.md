# LEVERAGE - Diario di bordo del popolamento massivo database

Data apertura documento: 24 giugno 2026  
Stato: popolamento storico non ancora committato; fase preview 2018 avviata  
Scopo: documentare in modo ordinato, verificabile e adatto alla tesi magistrale il processo di popolamento massivo del database LEVERAGE con i file storici Gymternet 2018-2025.

---

## 1. Obiettivo del documento

Questo documento affianca il Diario di bordo tecnico generale di LEVERAGE e registra nello specifico il popolamento massivo del database.

Per ogni anno importato vengono annotati:

- file sorgente utilizzato;
- stato del database prima dell'import;
- backup creati;
- esito della preview;
- statistiche aggregate;
- distribuzione dei dati;
- problemi rilevati;
- decisioni admin prese;
- dati effettivamente committati;
- controlli post-import;
- eventuali correzioni o scelte rimandate.

Il principio metodologico e che nessun dato storico viene importato "alla cieca": ogni anno passa da preview, review, decisioni esplicite e controlli post-import.

---

## 2. Metodo operativo deciso

Il popolamento storico viene eseguito un anno alla volta.

Per ogni file:

1. Verifica stato Git e stato database.
2. Backup del database prima di qualunque modifica rilevante.
3. Preview dell'import senza scrittura nel database.
4. Analisi aggregata della preview.
5. Revisione dei problemi bloccanti.
6. Decisioni admin documentate.
7. Commit solo dopo approvazione.
8. Controlli post-import.
9. Backup del database dopo l'import verificato.
10. Aggiornamento del presente diario.

La preview e il commit usano la logica backend del tool Gymternet legacy gia implementato in LEVERAGE.

---

## 3. Stato iniziale prima del popolamento

### 3.1 Repository e versione stabile

Prima del popolamento massivo e stato creato il repository GitHub:

- repository: `patronstefano/LEVERAGE`;
- tag stabile pre-import: `v0.1.0-backend-mvp`.

Questo tag rappresenta la fotografia stabile del backend MVP prima del caricamento storico dei dati.

### 3.2 Stato database locale

All'avvio del popolamento il database locale risultava vuoto per i dati sportivi:

| Entita | Conteggio iniziale |
|---|---:|
| Athlete | 0 |
| Event | 0 |
| Result | 0 |
| User | 0 |
| Notification | 0 |

### 3.3 Migrazioni

Prima della preview 2018 e stato rilevato che il database locale era fermo alla migrazione:

```text
0027_add_scalability_indexes
```

Il codice aggiornato richiedeva invece:

```text
0028_add_user_preferred_language
```

Prima di applicare la migrazione e stato creato un backup:

```text
/tmp/leverage_pre_import_2018_before_migration.db
```

Successivamente e stato eseguito:

```bash
alembic upgrade head
```

Risultato:

```text
0028_add_user_preferred_language (head)
```

Il database e quindi stato portato allo schema corrente prima di qualsiasi import.

---

## 4. Regole generali del popolamento storico Gymternet

Il tool Gymternet legacy usa le regole documentate in `docs/import_contract.md`.

Principi principali:

- il file puo creare `Athlete`, `Event` e `Result`;
- i dati mancanti non vengono inventati;
- i result con final score ma senza `D_score` sono ammessi come result parziali;
- i result con solo `D_score` e senza final score non vengono importati come result autonomi, ma restano in review;
- `represented_country` viene salvato sul singolo `Result`;
- `Athlete.country` rappresenta la country corrente o canonica dell'atleta;
- possibili cambi country o collisioni di identita vengono sottoposti a review admin;
- duplicati identici vengono saltati;
- duplicati non identici o country discordanti vengono segnalati;
- `VT SUM` e una colonna sorgente, non un apparatus salvato nel database;
- `VT AVG` resta un apparatus salvato;
- i vault derivati vengono marcati con `vault_attempt_order_uncertain=true`;
- dal 2025 in poi, se si usa ancora il tool Gymternet legacy, si applicano le regole legacy 2025.

---

## 5. Import 2018 - Preview iniziale

### 5.1 File sorgente

File analizzato:

```text
import_files/Results 2018.xlsx
```

La preview e stata eseguita senza scrivere dati nel database.

### 5.2 Stato DB prima della preview

| Entita | Conteggio |
|---|---:|
| Athlete | 0 |
| Event | 0 |
| Result | 0 |
| User | 0 |
| Notification | 0 |

### 5.3 Esito generale preview

| Indicatore | Valore |
|---|---:|
| Record letti | 89.994 |
| Result importabili | 89.988 |
| Nuovi Athlete previsti | 7.196 |
| Nuovi Event previsti | 211 |
| Duplicati identici nel file | 6 |
| Conflitti con DB | 0 |
| D-score orfani | 1.202 |
| Verifiche identita atleta | 48 |
| Issue totali preview | 2 warning |

### 5.4 Distribuzione per disciplina

| Discipline | Record |
|---|---:|
| MAG | 43.188 |
| WAG | 46.806 |

### 5.5 Distribuzione per category

| Category | Record |
|---|---:|
| senior | 49.225 |
| junior | 40.769 |

### 5.6 Distribuzione per format

| Format | Record |
|---|---:|
| individual | 77.911 |
| apparatus | 10.881 |
| team | 1.202 |

### 5.7 Distribuzione per round

| Round | Record |
|---|---:|
| final | 72.464 |
| qualification | 17.530 |

### 5.8 Distribuzione per apparatus

| Apparatus | Record |
|---|---:|
| VT | 17.891 |
| FX | 15.443 |
| AA | 10.000 |
| BB | 9.357 |
| UB | 9.146 |
| PH | 6.364 |
| PB | 6.174 |
| HB | 6.096 |
| SR | 6.077 |
| VT AVG | 3.446 |

### 5.9 Qualita dati rilevata

| Indicatore | Valore |
|---|---:|
| Result senza final score | 0 |
| Result senza D_score | 27.888 |
| Vault con ordine incerto | 17.891 |
| Result con day automatico | 756 |

I result senza `D_score` sono ammessi come dati parziali, perche dispongono comunque di final score.

### 5.10 Warning prodotti dalla preview

Warning 1:

```text
1202 D-score rows did not match a final-score row and need admin review
```

Interpretazione: esistono righe D-score che non sono state agganciate automaticamente a un result con final score. Non verranno importate come result autonomi. Potranno essere scartate o agganciate manualmente in seguito.

Warning 2:

```text
Automatic day assignment applied to 378 multi-day result keys without an explicit Day column; 756 rows received day values up to 2.
```

Interpretazione: alcuni eventi avevano risultati ripetuti compatibili con gare su piu giornate. In assenza di colonna `Day`, il sistema ha assegnato automaticamente `day=1` e `day=2`.

Eventi coinvolti dal day automatico:

- `Mexican Championships`
- `Russian Championships`
- `Top 12 Series 1`
- `Danish Championships`
- `Chinese Championships`
- `All-Japan Team Championships`

Questa logica e coerente con la decisione progettuale presa in precedenza: usare `Result.day` per distinguere gare multi-day.

### 5.11 D-score orfani

Totale:

```text
1.202
```

Distribuzione per tipo problema:

| Tipo problema | Conteggio |
|---|---:|
| athlete_missing_in_score_sheet | 481 |
| missing_score_sheet_context | 313 |
| possible_athlete_name_typo | 156 |
| missing_final_score_for_context | 139 |
| possible_context_mismatch | 100 |
| possible_event_name_mismatch | 13 |

D-score orfani con suggerimenti automatici:

```text
269
```

D-score orfani senza suggerimenti:

```text
933
```

Decisione provvisoria: non bloccare il commit 2018 per i D-score orfani. Importare i result dotati di final score e lasciare i D-score orfani nel report/review, evitando di creare result con solo D-score.

### 5.12 Duplicati identici nel file

Totale:

```text
6
```

Esempi:

| Event | Athlete | Discipline | Category | Apparatus | Round | Score | Note |
|---|---|---|---|---|---|---:|---|
| Mexican Championships | Edwin Lopez | MAG | junior | HB | final | 12.35 | duplicate_in_file |
| Danish Championships | Jacob Buus | MAG | senior | HB | final | 12.8 | duplicate_in_file |
| Russian Championships | Maksim Khodykin | MAG | senior | SR | qualification | 14.4 | duplicate_in_file |
| Russian Championships | Oleg Stepko | MAG | senior | PB | final | 14.2 | duplicate_in_file |
| Mexican Championships | Orlando Esparza | MAG | junior | SR | final | 12.0 | duplicate_in_file |
| Russian Championships | Vadim Smetanin | MAG | senior | HB | final | 12.2 | duplicate_in_file |

Decisione provvisoria: i duplicati identici possono essere saltati dal sistema.

### 5.13 Eventi principali per volume result

| Event | Result |
|---|---:|
| European Championships | 3.033 |
| World Championships | 2.970 |
| British Championships | 2.910 |
| English Championships | 2.336 |
| Russian Championships | 2.297 |
| U.S. Championships | 1.399 |
| Chinese Championships | 1.360 |
| Russian Junior Championships | 1.336 |
| All-Japan Championships | 1.148 |
| Pan American Championships | 1.052 |
| Mexican Championships | 1.042 |
| Asian Games | 1.017 |
| Italian Gold Championships | 998 |
| Voronin Cup | 960 |
| International Junior Team Cup | 931 |
| 2nd Italian Serie A | 877 |
| Pacific Rim Championships | 876 |
| 3rd Italian Serie A | 869 |
| Commonwealth Games | 864 |
| 1st Italian Serie A | 860 |

### 5.14 Blocco principale prima del commit 2018

Il vero blocco prima del commit e costituito da:

```text
48 verifiche identita atleta
```

Questi casi indicano stesso nome, stessa disciplina, ma country diverse nello stesso file.

Esempi:

| Athlete | Discipline | Country variants |
|---|---|---|
| Daniel Fox | MAG | GBR:12, IRL:10 |
| Benjamin Gischard | MAG | FRA:3, SUI:38 |
| Alexander Shatilov | MAG | ISR:33, RUS:1 |
| Andrei Muntean | MAG | FRA:5, ROU:69 |
| Sara Ricciardi | WAG | ITA:50, SRB:5 |
| Ana Palacios | WAG | ESP:8, GUA:25 |

Motivo del blocco: LEVERAGE deve evitare sia di fondere per errore atleti diversi, sia di creare doppioni quando si tratta dello stesso atleta con diversa representation/country.

Decisione da prendere: stabilire se trattare questi casi con una regola generale controllata o revisarli manualmente uno a uno.

Proposta operativa iniziale:

- default: `merge_as_same_athlete`;
- `canonical_country`: country con piu result;
- ogni singolo `Result` conserva comunque il proprio `represented_country`;
- eccezioni da valutare manualmente solo quando il nome e potenzialmente comune o la distribuzione country e sospetta.

Questa proposta non e ancora stata approvata.

---

## 6. Decisioni aperte prima del commit 2018

### Decisione 1 - Collisioni identita atleta

Da decidere:

- usare una regola generale controllata per le 48 collisioni;
- oppure revisionare manualmente tutti i 48 casi;
- oppure applicare regola generale e isolare solo alcuni casi sospetti.

### Decisione 2 - D-score orfani

Proposta attuale:

- non importarli come result autonomi;
- lasciare il numero nel report import;
- agganciare manualmente solo eventuali casi rilevanti o suggeriti;
- non bloccare il commit 2018.

### Decisione 3 - Duplicati identici

Proposta attuale:

- saltarli automaticamente;
- riportarli nel report.

### Decisione 4 - Day automatico

Proposta attuale:

- accettare `day=1` e `day=2` automatici per i 756 result coinvolti;
- verificare a campione almeno `Russian Championships`, `Mexican Championships` e `All-Japan Team Championships` dopo il commit.

---

## 7. Prossimo passo

Prima del commit 2018 occorre decidere come gestire le 48 collisioni identita atleta.

Solo dopo questa decisione si procedera con:

1. eventuale costruzione decisioni admin;
2. commit controllato 2018;
3. verifica conteggi DB;
4. verifica duplicati post-import;
5. verifica campioni evento/classifica;
6. backup post-import 2018;
7. aggiornamento del presente diario con esito definitivo.
