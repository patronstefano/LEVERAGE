# LEVERAGE - Diario di bordo del popolamento massivo database

Data apertura documento: 24 giugno 2026  
Stato: import storico 2018, 2019, 2020, 2021, 2022, 2023, 2024 e 2025 committati e verificati
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

Decisione presa il 24 giugno 2026: revisionare manualmente tutti i 48 casi, uno a uno, prima del commit definitivo del file 2018.

Documento operativo creato:

```text
docs/LEVERAGE_import_2018_collisioni_atleti.md
```

La tabella di revisione riporta per ogni caso:

- nome atleta;
- disciplina;
- country rilevate e conteggi;
- country canonica suggerita solo come aiuto operativo;
- livello di rischio;
- evidenze sintetiche dagli eventi sorgente;
- evidenza post-2018 ricavata dai file 2019-2025, usando stesso nome e stessa disciplina;
- `review_id` tecnico;
- colonne `Decision` e `Notes` da compilare durante la revisione admin.

Regola metodologica: nessuna fusione automatica generale viene applicata senza validazione admin. Le decisioni possibili sono `merge_as_same_athlete`, `keep_separate`, `manual_target` o `postpone`.

Aggiornamento tecnico del 24 giugno 2026: il flusso `merge_as_same_athlete` e stato raffinato per distinguere due casi:

- `country_history`: stesso atleta con reale cambio country/rappresentanza; LEVERAGE crea o usa una sola scheda Athlete, ma preserva la country sorgente su ogni `Result.represented_country`;
- `country_correction`: stesso atleta e country errata nel file sorgente; LEVERAGE crea o usa una sola scheda Athlete e importa i Result interessati con `represented_country` corretto, senza modificare il file Excel sorgente.

Questa distinzione evita sia la perdita della storia sportiva, sia la propagazione di errori di data entry nelle classifiche e negli analytics.

Aggiornamento metodo revisione del 24 giugno 2026: per ogni collisione 2018 viene usata anche la presenza dell'atleta nei file `Results 2019.xlsx` - `Results 2025.xlsx` come evidenza di supporto. Se dopo il 2018 l'atleta compare con una sola country, questo dato puo aiutare a distinguere country finale/canonica, cambio reale o probabile errore nel 2018. Questa evidenza non decide automaticamente il caso: la decisione resta admin e va annotata nella checklist.

---

## 6. Decisioni aperte prima del commit 2018

### Decisione 1 - Collisioni identita atleta

Stato: revisione manuale completata; aggiornata dopo introduzione del merge automatico nome/cognome.

Esito revisione admin prima della rettifica name-order:

- 48 decisioni compilate;
- 47 `merge_as_same_athlete`;
- 1 `keep_separate`;
- 46 `country_correction`;
- 1 `country_history`;
- 0 decisioni mancanti;
- 0 decisioni invalide;
- 0 collisioni irrisolte nella simulazione tecnica;
- 0 conflitti generati dalla simulazione tecnica.

Rettifica tecnica del 24 giugno 2026:

- il tool applica ora automaticamente `merge name order` per nomi/cognomi invertiti o formati equivalenti;
- sulla preview 2018 vengono rilevati 15 merge automatici name-order;
- 17 chiavi atleta/country vengono ricondotte a una chiave canonica;
- 116 righe risultato vengono normalizzate sul nome canonico;
- la preview 2018 resta a 48 collisioni country, ma due vecchie review (`Takumi Onoshima` e `Onoshima Takumi`) vengono fuse in una sola review `Takumi Onoshima` con country `BEL`, `ITA`, `JPN`;
- emerge una nuova review country su `Henji Mboyo` (`FRA`, `SUI`), derivata dalla fusione automatica `Henji M'Boyo` / `Henji Mboyo`, poi risolta dall'admin come `country_correction -cc:SUI`.

Stato operativo aggiornato:

- 48 collisioni country risolte;
- 47 `merge_as_same_athlete`;
- 1 `keep_separate`;
- 46 `country_correction`;
- 1 `country_history`;
- `Onoshima Takumi` / `Takumi Onoshima` non richiede piu una verifica name-order: il nome canonico e `Takumi Onoshima`, mentre resta applicata la correzione country verso `BEL`.
- `Henji Mboyo` viene confermato come atleta `SUI`; la variante `FRA` viene trattata come errore di data entry e corretta verso `SUI`.

### Decisione 1b - Inversioni nome/cognome e formati equivalenti

Stato: risolta come regola automatica di sistema dopo osservazione admin sul caso `Takumi Onoshima` / `Onoshima Takumi`.

Esito controllo tecnico:

- la preview 2018 rileva 15 casi di nome invertito o formato equivalente;
- questi casi non bloccano piu il commit come review autonome;
- il backend normalizza automaticamente i record sul nome canonico;
- il nome canonico viene scelto dando priorita all'atleta gia presente nel database; in assenza di un atleta esistente, viene usata la variante piu ricorrente nel file importato;
- se dopo la normalizzazione rimangono country diverse, la review admin resta obbligatoria solo sulla country.

Da completare:

- rigenerare il payload `athlete_match_decisions` aggiornato per il commit controllato 2018.

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

## 7. Import 2018 - Commit controllato e controlli post-import

Data esecuzione: 24 giugno 2026
File sorgente: `import_files/Results 2018.xlsx`
Backup pre-import: `backups/leverage_pre_import_2018_2026-06-24.db`
Backup post-import verificato: `backups/leverage_post_import_2018_2026-06-24.db`

### 7.1 Stato database prima del commit 2018

Prima del commit il database locale era vuoto per i dati sportivi:

| Entita | Conteggio |
|---|---:|
| User | 0 |
| Athlete | 0 |
| Event | 0 |
| Result | 0 |
| Notification | 0 |

Nota metodologica: l'import e stato eseguito senza `notification_user_id`, perche il database locale non conteneva ancora utenti/admin. Di conseguenza non sono state create notifiche admin nel database locale durante questo commit.

### 7.2 Decisioni admin applicate

Dal documento `docs/LEVERAGE_import_2018_collisioni_atleti.md` sono state lette e applicate 48 decisioni:

| Decisione | Conteggio |
|---|---:|
| `merge_as_same_athlete` | 47 |
| `keep_separate` | 1 |
| `country_correction` | 46 |
| `country_history` | 1 |
| Decisioni mancanti | 0 |
| Decisioni invalide | 0 |

Il tool ha inoltre applicato la regola automatica `merge name order`:

| Controllo automatico | Conteggio |
|---|---:|
| Merge automatici name-order | 15 |
| Chiavi atleta/country ricondotte a nome canonico | 17 |
| Righe risultato normalizzate sul nome canonico | 116 |
| Review manuali name-order generate | 0 |

Decisioni sensibili confermate:

- `Takumi Onoshima` e `Onoshima Takumi` sono trattati come lo stesso atleta; nome canonico finale: `Takumi Onoshima`.
- `Henji Mboyo` e sempre `SUI`; la variante `FRA` e stata trattata come errore di data entry e corretta a `SUI`.
- `Deborah Salmina` conserva lo storico country/representation: atleta con country corrente `VEN`, result 2018 con `represented_country=ITA` quando coerente con la decisione di cambio/storico country.

### 7.3 Esito simulazione immediatamente prima del commit

| Voce preview | Conteggio |
|---|---:|
| Righe parse | 89.994 |
| Result importabili | 89.988 |
| Athlete da creare | 7.134 |
| Event da creare | 211 |
| Duplicati saltabili | 6 |
| Conflitti bloccanti | 0 |
| D-score orfani da review, non importati | 1.202 |
| Warning | 2 |

Statistiche decisioni atleta in simulazione:

| Voce | Conteggio |
|---|---:|
| Identity merge | 47 |
| Identity keep separate | 1 |
| Correzioni represented country | 47 |
| Decisioni invalide | 0 |
| Review irrisolte | 0 |

### 7.4 Commit effettivo 2018

Il commit controllato e stato eseguito con successo.

| Voce commit | Conteggio |
|---|---:|
| Athlete creati | 7.134 |
| Event creati | 211 |
| Result creati | 89.988 |
| Result completi creati | 62.105 |
| Result parziali creati | 27.883 |
| Athlete con nuovi result | 7.134 |
| Event con nuovi result | 211 |
| Duplicati saltati | 6 |
| D-score orfani non committati | 1.202 |
| Result con represented country corretta | 293 |
| Aggiornamenti country corrente Athlete | 0 |
| Notifiche admin create | 0 |

### 7.4.1 Report D-score orfani non importati

I 1.202 D-score orfani non sono stati importati nel database come result autonomi, coerentemente con la decisione metodologica presa prima del commit.

Per evitare perdita informativa, e stato generato un report CSV dedicato:

```text
docs/import_reports/gymternet_2018_orphan_dscores.csv
```

Il report contiene 1.202 righe dati piu intestazione e conserva per ogni D-score orfano:

- `review_id`;
- tipo di problema rilevato;
- sheet e riga sorgente nel file Gymternet;
- evento, anno, atleta, country, disciplina, categoria, apparatus, format, round, day e `D_score`;
- eventuale incertezza su vault attempt;
- numero di suggerimenti automatici disponibili;
- miglior suggerimento automatico di aggancio, quando presente;
- payload completo dei suggerimenti in formato JSON.

Statistiche del report:

| Voce | Conteggio |
|---|---:|
| D-score orfani salvati nel CSV | 1.202 |
| D-score orfani con almeno un suggerimento automatico | 269 |
| D-score orfani senza suggerimento automatico | 933 |

Interpretazione: questi record restano fuori dal database operativo, ma vengono conservati come materiale di audit e recupero. In futuro potranno essere revisionati manualmente, agganciati a result esistenti oppure scartati definitivamente.

### 7.5 Stato database dopo il commit 2018

| Entita | Conteggio |
|---|---:|
| User | 0 |
| Athlete | 7.134 |
| Event | 211 |
| Result | 89.988 |
| Notification | 0 |

Distribuzione Result per disciplina:

| Discipline | Result |
|---|---:|
| MAG | 43.182 |
| WAG | 46.806 |

Distribuzione Result per categoria:

| Category | Result |
|---|---:|
| junior | 40.767 |
| senior | 49.221 |

Distribuzione Event per disciplina:

| Discipline Event | Event |
|---|---:|
| MAG | 24 |
| WAG | 74 |
| MAG and WAG | 113 |

Distribuzione Event per categoria:

| Category Event | Event |
|---|---:|
| junior | 25 |
| senior | 56 |
| junior and senior | 130 |

Distribuzione Result per apparatus:

| Apparatus | Result |
|---|---:|
| AA | 10.000 |
| BB | 9.357 |
| FX | 15.443 |
| HB | 6.093 |
| PB | 6.173 |
| PH | 6.364 |
| SR | 6.075 |
| UB | 9.146 |
| VT | 17.891 |
| VT AVG | 3.446 |

Distribuzione Result per round:

| Round | Result |
|---|---:|
| final | 72.459 |
| qualification | 17.529 |

Distribuzione Result per format:

| Format | Result |
|---|---:|
| apparatus | 10.881 |
| individual | 77.905 |
| team | 1.202 |

### 7.6 Controlli semantici post-import

| Controllo | Esito |
|---|---:|
| Gruppi duplicati semantici Result post-import | 0 |
| Result con `score` nullo | 0 |
| Result con `d_score` nullo | 27.883 |
| Result con `score` e `d_score` presenti | 62.105 |
| Result con `score` presente e `d_score` assente | 27.883 |
| Result con `d_score` presente e `score` assente | 0 |
| Result con execution estimate disponibile | 62.105 |
| Result con `day` valorizzato | 756 |
| Massimo valore `day` rilevato | 2 |
| Result VT con alert incertezza attempt | 17.891 |
| Result con `represented_country` diverso da country corrente Athlete | 15 |
| Country rappresentate distinte nei Result | 106 |
| Country correnti distinte negli Athlete | 106 |

Interpretazione:

- i result con final score ma senza `d_score` sono importati come result parziali, perche mantengono informazione sportiva utile;
- i result con solo `d_score` e senza final score non sono stati importati come result autonomi;
- l'execution estimate e disponibile solo quando `score` e `d_score` sono entrambi presenti;
- i result VT importati dal legacy Gymternet mantengono l'alert di incertezza attempt, perche `VT` puo indicare in alcuni casi Vault 1 o Vault 2;
- la differenza residua tra country corrente Athlete e `represented_country` e attesa nel caso di storico country validato.

### 7.7 Controllo eventi multi-day

Controlli a campione richiesti prima del commit e verificati dopo il commit:

| Event | Totale Result | Day nullo | Day 1 | Day 2 |
|---|---:|---:|---:|---:|
| Russian Championships | 2.294 | 1.692 | 301 | 301 |
| Mexican Championships | 1.040 | 974 | 33 | 33 |
| All-Japan Team Championships | 503 | 501 | 1 | 1 |

Esito: il sistema rimuove correttamente `day 1` / `day 2` dal nome evento e valorizza il campo `day` del Result.

### 7.8 Controllo casi sensibili

| Caso | Esito |
|---|---|
| `Takumi Onoshima` | 1 Athlete creato, country `BEL`, disciplina `MAG`, 40 result; nessun Athlete `Onoshima Takumi` separato. |
| `Henji Mboyo` | 1 Athlete creato, country `SUI`, disciplina `MAG`, 37 result; tutti i result importati con `represented_country=SUI`. |
| `Deborah Salmina` | 1 Athlete con country corrente `VEN`; 15 result 2018 conservano `represented_country=ITA` come storico country validato. |

### 7.9 Top country rappresentate 2018

| Country | Result |
|---|---:|
| GBR | 8.229 |
| USA | 6.879 |
| RUS | 5.677 |
| GER | 5.185 |
| ITA | 4.771 |
| CHN | 3.355 |
| JPN | 3.350 |
| FRA | 3.113 |
| ESP | 2.907 |
| CAN | 2.528 |

### 7.10 Eventi con piu result nel 2018

| Event | Result |
|---|---:|
| European Championships | 3.033 |
| World Championships | 2.970 |
| British Championships | 2.910 |
| English Championships | 2.336 |
| Russian Championships | 2.294 |
| U.S. Championships | 1.399 |
| Chinese Championships | 1.360 |
| Russian Junior Championships | 1.336 |
| All-Japan Championships | 1.148 |
| Pan American Championships | 1.052 |

### 7.11 Esito finale import 2018

L'import 2018 e considerato committato e verificato.

Punti ancora da ricordare:

- i 1.202 D-score orfani restano fuori dal database e sono conservati nel report `docs/import_reports/gymternet_2018_orphan_dscores.csv` per eventuale review di recupero mirata;
- i 27.883 result senza `d_score` sono presenti come result parziali e devono essere trattati lato UI come dati incompleti/not available;
- i result VT legacy mantengono alert di incertezza attempt;
- il database locale non contiene ancora utenti, quindi le notifiche admin di import summary non sono state create in questa esecuzione locale.

## 8. Import 2019 - Preview senza commit

Data esecuzione preview: 25 giugno 2026
File sorgente: `import_files/Results 2019.xlsx`
Stato: preview eseguita, nessun commit 2019 eseguito

Backup pre-import:

```text
backups/leverage_pre_import_2019_2026-06-25.db
```

Documento operativo dedicato:

```text
docs/LEVERAGE_import_2019_review.md
```

Report generati:

| File | Scopo |
|---|---|
| `docs/import_reports/gymternet_2019_preview_summary.json` | Sintesi tecnica della preview 2019. |
| `docs/import_reports/gymternet_2019_orphan_dscores.csv` | D-score orfani 2019 conservati fuori dal database. |
| `docs/import_reports/gymternet_2019_athlete_review.csv` | Review atleta/country 2019 completa e tecnica, conservata come report aggregato. |
| `docs/import_reports/gymternet_2019_existing_athlete_match_review.csv` | CSV operativo per verificare se un atleta importato nel 2019 corrisponde a un atleta gia presente nel DB 2018. |
| `docs/import_reports/gymternet_2019_new_athlete_country_conflicts.csv` | CSV operativo per i soli nuovi atleti 2019 con conflitti di country. |

Nota di standardizzazione: a partire dalla preview 2019, le review operative da compilare vengono gestite in CSV. Per coerenza, anche la review collisioni atleta/country 2018 e stata convertita in `docs/import_reports/gymternet_2018_athlete_collision_review.csv`; l'audit automatico name-order 2018 e stato convertito in `docs/import_reports/gymternet_2018_name_order_audit.csv`. I Word operativi di review import sono stati rimossi; resta il Word del diario generale per uso documentale/tesi.

Formato operativo semplificato:

| Colonna | Uso |
|---|---|
| `athlete_name` / `imported_athlete_2019` | Nome e cognome atleta da verificare. |
| `suggested_existing_athlete` | Atleta gia presente nel DB 2018 suggerito dal sistema, quando esiste. |
| `collision_countries` / `collision_or_change_countries` | Country coinvolte nella review. |
| `results_2019_by_country` / `imported_2019_results_by_country` | Gare 2019 associate alle diverse country. |
| `existing_athlete_2018_results_by_country` | Gare 2018 dell'atleta gia esistente nel DB. Serve per capire se il nuovo record 2019 e davvero la stessa persona. |
| `future_country_evidence` | Country rappresentata negli anni successivi. Per il 2019 copre 2020-2025; per il 2018 copre 2019-2025. |
| `decision` | Inserire `merge as same athlete` oppure `keep separate`. |
| `action` | Usare `canonical country` oppure `country history` quando serve una decisione country. |
| `country` | Country corretta, oppure country finale/corrente in caso di storico country. |

### 8.1 Sintesi preview 2019

| Voce | Conteggio |
|---|---:|
| Result parse dal file | 106.633 |
| Result potenzialmente importabili | 106.633 |
| Athlete che verrebbero creati senza decisioni admin | 4.576 |
| Event che verrebbero creati | 234 |
| Duplicati rilevati | 0 |
| Conflitti bloccanti | 0 |
| Warning | 2 |

Warning:

| Warning | Esito |
|---|---:|
| D-score non agganciati a final-score | 958 |
| Multi-day automatici | 77 chiavi, 154 righe con `day` valorizzato |

Interpretazione: la preview 2019 e tecnicamente positiva perche non presenta duplicati o conflitti bloccanti. Il blocco prima del commit riguarda la review atleta/country.

### 8.2 D-score orfani 2019

| Problem type | Conteggio |
|---|---:|
| `athlete_missing_in_score_sheet` | 322 |
| `missing_final_score_for_context` | 228 |
| `possible_context_mismatch` | 201 |
| `possible_event_name_mismatch` | 147 |
| `possible_athlete_name_typo` | 53 |
| `missing_score_sheet_context` | 7 |

Totale D-score orfani: 958.

D-score orfani con almeno un suggerimento automatico: 401.

Decisione provvisoria: come per il 2018, non importarli come result autonomi. Conservarli nel CSV dedicato per eventuale review futura.

### 8.3 Merge automatico name-order 2019

Il tool ha applicato la regola automatica `merge name order` anche alla preview 2019.

| Controllo automatico | Conteggio |
|---|---:|
| Merge automatici name-order | 15 |
| Chiavi atleta/country ricondotte a nome canonico | 16 |
| Righe result normalizzate sul nome canonico | 118 |

Questi casi non generano review manuale autonoma, salvo quando dopo la normalizzazione rimane una questione country/identity.

### 8.4 Review atleta/country 2019

Totale review atleta/country: 393.

| Problem type | Conteggio |
|---|---:|
| `possible_existing_athlete_match` | 309 |
| `possible_athlete_identity_collision` | 64 |
| `possible_athlete_country_change` | 20 |

Triage operativa:

| Review priority | Conteggio | Interpretazione |
|---|---:|---|
| `high` | 100 | Richiede verifica admin puntuale. |
| `bulk_candidate` | 92 | Possibile accettazione piu rapida dopo controllo a campione. |
| `medium` | 201 | Match potenziali da controllare prima del commit. |

Distribuzione confidence del miglior suggerimento:

| Confidence | Conteggio |
|---|---:|
| `>=0.95` | 145 |
| `0.90-0.949` | 176 |
| `<0.90/no suggestion` | 72 |

Flag country del miglior suggerimento:

| Flag | Conteggio |
|---|---:|
| Stessa country, senza decisione country richiesta | 293 |
| Country diversa, decisione country richiesta | 16 |
| Non applicabile a identity collision con suggerimento | 48 |

### 8.5 Separazione operativa della review 2019

Durante la preparazione della review admin e emersa una necessita pratica: per gli atleti gia esistenti nel database non basta vedere il dato 2019, perche l'admin deve poter confrontare anche le gare 2018 dell'atleta gia salvato in LEVERAGE.

Decisione metodologica del 25 giugno 2026:

- separare la review 2019 in due CSV operativi;
- mostrare nel CSV dei match con atleta esistente anche le gare 2018 dell'atleta gia presente nel DB;
- lasciare in un secondo CSV solo i nuovi atleti 2019 con conflitti di country;
- mantenere `gymternet_2019_athlete_review.csv` come report tecnico aggregato.

File operativi prodotti:

| File | Righe dati | Scopo |
|---|---:|---|
| `docs/import_reports/gymternet_2019_existing_athlete_match_review.csv` | 377 | Verificare se atleta 2019 e atleta gia presente nel DB 2018 sono la stessa persona. |
| `docs/import_reports/gymternet_2019_new_athlete_country_conflicts.csv` | 16 | Risolvere conflitti country interni ai nuovi atleti 2019. |

Nel file `gymternet_2019_existing_athlete_match_review.csv` la colonna `existing_athlete_2018_results_by_country` riporta le gare 2018 dell'atleta gia presente, raggruppate per country. Questo rende piu rapida la decisione admin tra:

- `merge as same athlete`;
- `keep separate`;
- `canonical country`;
- `country history`.

Aggiornamento operativo del 25 giugno 2026:

- l'admin ha completato la review dei nuovi atleti 2019 con conflitti country nel file Numbers `gymternet_2019_new_athlete_country_conflicts.numbers`;
- il file Numbers e stato convertito nel CSV operativo `docs/import_reports/gymternet_2019_new_athlete_country_conflicts.csv`;
- l'ordine colonne e stato reso coerente nei due CSV operativi 2019, posizionando le colonne decisionali `decision`, `action`, `country`, `notes` prima delle colonne di evidenza;
- i valori inseriti in Numbers sono stati normalizzati per il backend: `Merge` diventa `merge as same athlete`, `Correct` diventa `canonical country`;
- esito: 16/16 nuovi conflitti country 2019 risultano compilati come `merge as same athlete` con `canonical country`.

Aggiornamento operativo successivo del 25 giugno 2026:

- l'admin ha completato anche il file Numbers `gymternet_2019_existing_athlete_match_review.numbers`;
- il file e stato analizzato e trasferito nel CSV operativo `docs/import_reports/gymternet_2019_existing_athlete_match_review.csv`;
- per evitare alterazioni dei dati tecnici causate dalla lettura del formato Numbers, sono state importate dal Numbers solo le colonne decisionali `decision`, `action`, `country` e `notes`;
- i valori sono stati normalizzati per il backend: `Merge` diventa `merge as same athlete`, `Separate` diventa `keep separate`, `Correct` diventa `canonical country`, `History` e il refuso `Histroy` diventano `country history`;
- esito: 377/377 righe compilate, 365 `merge as same athlete`, 12 `keep separate`, 67 `canonical country`, 9 `country history`, 0 decisioni invalide;
- sono stati rilevati 9 casi in cui lo stesso atleta gia esistente era suggerito su piu righe per varianti di nome o country. Non sono emersi duplicati tecnici di `review_id`; l'audit e stato salvato in `docs/import_reports/gymternet_2019_existing_athlete_repeat_audit.csv`.

Indicazione metodologica aggiunta per gli import futuri: se due record hanno stessa country, nome molto simile e l'evidenza degli anni successivi mostra che una delle due varianti non compare piu (`not found`), il tool puo trattare il caso come merge automatico/candidato diretto, evitando di sottoporlo ogni volta alla review manuale admin.

### 8.6 Esito preview 2019

Il 2019 non e stato committato nel database.

Prima del commit occorre:

1. eseguire il commit controllato 2019;
2. fare controlli post-import e backup post-2019;
3. aggiornare il diario con l'esito finale del commit.

### 8.7 Payload decisionale e preview applicata 2019

Data esecuzione: 25 giugno 2026

File generati:

| File | Scopo |
|---|---|
| `docs/import_reports/gymternet_2019_athlete_match_decisions.json` | Payload tecnico prodotto dalle decisioni admin atleta/country 2019. |
| `docs/import_reports/gymternet_2019_preview_with_decisions_summary.json` | Esito preview 2019 con decisioni applicate, eseguita su copia temporanea del database. |
| `docs/import_reports/gymternet_2019_post_decision_conflicts.csv` | Audit dei conflitti emersi dopo le fusioni atleta/country. |

Prima della preview applicata e stata effettuata una rifinitura backend: `canonical country` ora puo correggere `Result.represented_country` anche nei match con atleta gia esistente e nei country-change, non solo nelle identity collision. Questo rende coerente il comportamento con la semantica decisa durante la review admin.

La prima versione del payload decisionale conteneva 393 decisioni:

| Decisione tecnica | Conteggio |
|---|---:|
| `merge_as_same_athlete` | 64 |
| `accept_suggestion` | 297 |
| `update_country` | 10 |
| `keep_existing_country` | 10 |
| `create_new` | 12 |

Esito decisioni:

| Controllo | Conteggio |
|---|---:|
| Decisioni invalide | 0 |
| Review irrisolte | 0 |
| Correzioni represented country da decisioni | 76 |
| Override represented country generati | 143 |

Prima preview applicata:

| Voce | Conteggio |
|---|---:|
| Righe parse | 106.633 |
| Result importabili dopo decisioni | 106.609 |
| Athlete che verrebbero creati | 4.204 |
| Event che verrebbero creati | 234 |
| Conflitti residui | 24 |
| Duplicati residui | 0 |
| D-score orfani lasciati fuori | 958 |

Prima simulazione commit su database temporaneo:

| Voce simulata | Conteggio |
|---|---:|
| Athlete creati | 4.204 |
| Event creati | 234 |
| Result creati | 106.609 |
| Result completi creati | 73.782 |
| Result parziali creati | 32.827 |
| Event aggiornati | 268 |
| Country corrente Athlete aggiornate | 11 |
| `represented_country` corretti | 521 |
| Athlete con nuovi result | 8.571 |
| Event con nuovi result | 234 |

La simulazione e stata eseguita su:

```text
/private/tmp/leverage_preview_2019.db
```

Il database operativo `leverage.db` non e stato modificato.

Controllo rollback della copia temporanea:

| Stato DB temporaneo | Athlete | Event | Result | Notification |
|---|---:|---:|---:|---:|
| Prima della simulazione | 7.134 | 211 | 89.988 | 0 |
| Durante la simulazione | 11.338 | 445 | 196.597 | 0 |
| Dopo rollback | 7.134 | 211 | 89.988 | 0 |

### 8.8 Conflitti post-decisione 2019

La preview con decisioni applicate ha fatto emergere 24 conflitti post-decisione. Questi casi non erano visibili nella preview precedente perche diventano conflitti solo dopo avere fuso varianti nome/country sullo stesso atleta.

Distribuzione:

| Atleta risolto | Conflitti |
|---|---:|
| Jack Stanley | 7 |
| Lee Jun-ho | 5 |
| Siddhi Hattekar | 5 |
| Chen Yu | 3 |
| Sofia Bertoli | 2 |
| Carla Martin | 1 |
| Kaja Skalska | 1 |

Interpretazione: due righe sorgente diventano lo stesso `Result` sportivo dopo le decisioni admin, ma hanno score o D-score diversi. Non possono essere trattate come duplicati innocui.

Decisione metodologica iniziale: il commit standard 2019 restava bloccato finche questi conflitti non fossero stati risolti. Il file operativo da controllare era:

```text
docs/import_reports/gymternet_2019_post_decision_conflicts.csv
```

Aggiornamento successivo del 25 giugno 2026: l'admin ha confermato che i 7 gruppi coinvolti nei 24 conflitti sono atleti diversi. Le relative decisioni sono state modificate da `merge as same athlete` a `keep separate`.

Decisioni aggiornate:

| Imported athlete | Suggested existing athlete |
|---|---|
| Carolina Martin | Carla Martin |
| Cen Yu | Chen Yu |
| Jake Stanley | Jack Stanley |
| Lee Jung-hyo | Lee Jun-ho |
| Maja Skalska | Kaja Skalska |
| Riddhi Hattekar | Siddhi Hattekar |
| Sonia Bertoli | Sofia Bertoli |

Payload rigenerato:

| Decisione tecnica | Conteggio aggiornato |
|---|---:|
| `merge_as_same_athlete` | 64 |
| `accept_suggestion` | 290 |
| `update_country` | 10 |
| `keep_existing_country` | 10 |
| `create_new` | 19 |

Nuova preview applicata:

| Voce | Conteggio |
|---|---:|
| Righe parse | 106.633 |
| Result importabili dopo decisioni | 106.633 |
| Athlete che verrebbero creati | 4.211 |
| Event che verrebbero creati | 234 |
| Conflitti residui | 0 |
| Duplicati residui | 0 |
| D-score orfani lasciati fuori | 958 |

Nuova simulazione commit su database temporaneo:

| Voce simulata | Conteggio |
|---|---:|
| Athlete creati | 4.211 |
| Event creati | 234 |
| Result creati | 106.633 |
| Result completi creati | 73.802 |
| Result parziali creati | 32.831 |
| Event aggiornati | 268 |
| Country corrente Athlete aggiornate | 11 |
| `represented_country` corretti | 521 |
| Athlete con nuovi result | 8.578 |
| Event con nuovi result | 234 |

Controllo rollback della copia temporanea:

| Stato DB temporaneo | Athlete | Event | Result | Notification |
|---|---:|---:|---:|---:|
| Prima della simulazione | 7.134 | 211 | 89.988 | 0 |
| Durante la simulazione | 11.345 | 445 | 196.621 | 0 |
| Dopo rollback | 7.134 | 211 | 89.988 | 0 |

Esito: la preview 2019 con decisioni applicate e ora pulita. Il commit controllato 2019 puo essere eseguito nel prossimo passo, mantenendo i 958 D-score orfani fuori dal database operativo.

### 8.9 Memoria decisionale del tool Gymternet

Decisione metodologica del 25 giugno 2026: i problemi e le collisioni risolti durante il popolamento massivo non devono restare solo nel diario o nella chat di lavoro. Quando una decisione e riutilizzabile, deve diventare una regola persistente del tool Gymternet.

Questo principio serve a:

- ridurre review admin ripetitive negli import futuri;
- mantenere coerenza semantica tra anni diversi;
- rendere il processo di import piu controllabile e documentabile;
- permettere alla futura UI admin di mostrare suggerimenti gia motivati.

La prima regola formalizzata e:

```text
same_context_different_score_keep_separate
```

Significato: se una proposta di fusione tra atleti con nome simile produce lo stesso result sportivo ma con score o D-score diversi, il tool deve raccomandare di tenere separati gli atleti. Per le review `possible_existing_athlete_match`, l'azione tecnica equivalente e `create_new`; per i conflitti post-decisione, il payload segnala `recommended_action=keep_separate`.

Il documento operativo della memoria decisionale e:

```text
docs/GYMTERNET_IMPORT_DECISION_MEMORY.md
```

### 8.10 Commit controllato 2019

Data commit reale: 25 giugno 2026

Prima del commit reale e stato creato un backup fisico del database:

```text
backups/leverage_pre_import_2019_20260625_182243.db
```

Il commit reale e stato eseguito usando:

```text
import_files/Results 2019.xlsx
docs/import_reports/gymternet_2019_athlete_match_decisions.json
```

Il report tecnico del commit e stato salvato in:

```text
docs/import_reports/gymternet_2019_commit_summary.json
```

Esito commit:

| Voce | Conteggio |
|---|---:|
| Result creati | 106.633 |
| Result completi creati | 73.802 |
| Result parziali creati | 32.831 |
| Athlete creati | 4.211 |
| Event creati | 234 |
| Event aggiornati | 268 |
| Country corrente Athlete aggiornate | 11 |
| `represented_country` corretti | 521 |
| D-score orfani lasciati fuori dal DB | 958 |
| Duplicati saltati | 0 |

Stato DB dopo il commit:

| Entita | Conteggio |
|---|---:|
| Athlete | 11.345 |
| Event | 445 |
| Result | 196.621 |
| Notification | 0 |

Controlli post-import:

| Controllo | Esito |
|---|---:|
| Gruppi duplicati semantici Result | 0 |
| Result 2019 | 106.084 |
| Result 2020 contenuti nel file 2019 | 549 |
| Result 2019 completi | 73.802 |
| Result 2019 con final score ma senza D-score | 32.282 |
| Result 2019 senza final score | 0 |
| Result 2020 con final score ma senza D-score | 549 |
| Result 2019 con `represented_country` diverso dalla country corrente Athlete | 73 |

Nota importante: il file `Results 2019.xlsx` contiene anche 549 result riferiti all'evento `1st Spanish League (2020 season)`, correttamente registrato con `Event.year=2020`. Il DB segue l'anno reale dell'evento, non l'anno nominale del file sorgente.

I 73 result 2019 con `represented_country` diverso dalla country corrente dell'atleta sono coerenti con la logica di storico country/rappresentanza: il singolo result conserva la country rappresentata in gara, mentre la scheda Athlete conserva la country corrente dopo le decisioni admin.

## 9. Import 2020 - Preview, review e commit

Data preview: 25 giugno 2026
Data commit database locale: 25 giugno 2026

File sorgente: `import_files/Results 2020.xlsx`

Stato: import 2020 committato e verificato

La preview 2020 e stata eseguita dopo il commit reale 2019. Il database di partenza conteneva:

| Entita | Conteggio |
|---|---:|
| Athlete | 11.345 |
| Event | 445 |
| Result | 196.621 |
| Notification | 0 |

### 9.1 Sintesi preview iniziale 2020

| Voce | Conteggio |
|---|---:|
| Righe parse | 33.782 |
| Result importabili | 33.777 |
| Athlete che verrebbero creati senza decisioni admin | 1.042 |
| Event che verrebbero creati | 76 |
| Duplicati identici interni al file | 5 |
| Conflitti bloccanti | 0 |
| Warning | 2 |

Warning prodotti:

- 696 D-score non agganciati a final score;
- assegnazione automatica `day` applicata a 207 chiavi multi-day, con 431 righe valorizzate fino a `day=4`.

### 9.2 File generati

| File | Scopo |
|---|---|
| `docs/import_reports/gymternet_2020_preview_summary.json` | Sintesi tecnica completa della preview 2020. |
| `docs/import_reports/gymternet_2020_duplicates.csv` | Audit dei duplicati identici interni al file. |
| `docs/import_reports/gymternet_2020_conflicts.csv` | Audit dei conflitti bloccanti; vuoto in questa preview. |
| `docs/import_reports/gymternet_2020_orphan_dscores.csv` | D-score orfani non agganciati a final score. |
| `docs/import_reports/gymternet_2020_athlete_review.csv` | Review atleta/country completa e tecnica. |
| `docs/import_reports/gymternet_2020_existing_athlete_match_review.csv` | CSV operativo per match con atleti gia presenti nel DB. |
| `docs/import_reports/gymternet_2020_new_athlete_country_conflicts.csv` | CSV operativo per nuovi atleti con conflitti country. |
| `docs/import_reports/gymternet_2020_athlete_match_decisions.json` | Payload tecnico delle decisioni admin 2020. |
| `docs/import_reports/gymternet_2020_preview_with_decisions_summary.json` | Preview 2020 con decisioni applicate, senza commit. |
| `docs/import_reports/gymternet_2020_post_decision_conflicts.csv` | Audit dei conflitti post-decisione; rigenerato vuoto dopo la correzione finale. |
| `docs/import_reports/gymternet_2020_post_decision_duplicates.csv` | Audit dei duplicati identici residui dopo le decisioni. |
| `docs/import_reports/gymternet_2020_commit_summary.json` | Report tecnico del commit reale 2020. |

### 9.3 Duplicati interni 2020

La preview ha segnalato 5 duplicati identici interni al file. Sono duplicati innocui e sono stati saltati automaticamente in fase di commit.

| Atleta | Evento | Apparatus | Score | D-score |
|---|---|---|---:|---:|
| Adam Dobrovitz | Hungarian Championships | PH | 12.000 | 4.000 |
| Kazuma Kaya | Friendship & Solidarity Meet | HB | 14.300 |  |
| Soma Laszlo Csorvasi | Hungarian Championships | HB | 11.900 | 4.300 |
| Liu Sijia | Chinese Individual Championships | VT attempt 1 day 2 | 11.950 | 3.700 |
| Meng Shangrong | Chinese Individual Championships | UB | 12.850 | 4.600 |

### 9.4 D-score orfani 2020

Totale D-score orfani: 696.

| Tipo problema | Conteggio |
|---|---:|
| `athlete_missing_in_score_sheet` | 482 |
| `possible_context_mismatch` | 107 |
| `missing_final_score_for_context` | 62 |
| `possible_athlete_name_typo` | 40 |
| `possible_event_name_mismatch` | 4 |
| `missing_score_sheet_context` | 1 |

Decisione provvisoria: come per 2018 e 2019, questi D-score restano fuori dal database operativo salvo review mirata futura.

### 9.5 Review atleta/country 2020

Totale review atleta/country: 165.

| Tipo review | Conteggio |
|---|---:|
| `possible_existing_athlete_match` | 141 |
| `possible_athlete_country_change` | 15 |
| `possible_athlete_identity_collision` | 9 |

CSV operativi:

| File | Righe da controllare |
|---|---:|
| `gymternet_2020_existing_athlete_match_review.csv` | 164 |
| `gymternet_2020_new_athlete_country_conflicts.csv` | 1 |

L'unico conflitto country tra nuovi atleti riguarda `Cathalina Matamala` (WAG), con country `GER` e `NED`. L'evidenza futura nei file successivi mostra `2021: NED`.

I due CSV sono stati compilati dall'admin tramite file Numbers. Il trasferimento nel CSV operativo ha preservato i campi tecnici e ha aggiornato soltanto:

- `decision`;
- `action`;
- `country`;
- `notes`.

Sono stati normalizzati anche shorthand e refusi:

- `Merge` -> `merge as same athlete`;
- `Separate` -> `keep separate`;
- `Correct` / `Corrrect` -> `canonical country`;
- `History` -> `country history`.

### 9.6 Decisioni applicate 2020

Dopo il trasferimento delle decisioni admin, il payload tecnico 2020 ha prodotto:

| Decisione/azione | Conteggio |
|---|---:|
| Suggerimenti accettati | 135 |
| Nuovi atleti confermati | 6 |
| Merge di identita atleta | 9 |
| Aggiornamenti country atleta | 8 |
| Country atleta mantenute | 11 |
| Correzioni `represented_country` sui result | 19 chiavi decisionali / 96 result corretti nel commit |
| Decisioni invalide | 0 |
| Decisioni mancanti | 0 |

### 9.7 Conflitto post-decisione risolto

La prima preview con decisioni applicate ha generato 5 conflitti, tutti collegati allo stesso caso:

- `Nao Kobayashi` suggerita come merge con `Kaho Kobayashi`;
- stesso evento: `All-Japan Student Championships`;
- stessa disciplina/category/format/round;
- stessi apparatus `BB`, `FX`, `UB`, `VT`, `AA`;
- score diversi nello stesso contesto sportivo.

Decisione metodologica: quando un possibile merge atleta produce lo stesso contesto sportivo di result ma con score o D-score diversi, il tool deve trattare i due record come atleti diversi e applicare `keep separate`.

La regola e coerente con quanto gia deciso durante il 2019 ed e tracciata come:

```text
same_context_different_score_keep_separate
```

Dopo questa correzione, la preview post-decisione e risultata pulita:

| Voce | Conteggio |
|---|---:|
| Conflitti post-decisione | 0 |
| Decisioni invalide | 0 |
| Decisioni mancanti | 0 |
| Duplicati identici residui | 5 |

### 9.8 Commit database 2020

Prima del commit e stato creato il backup:

```text
backups/leverage_pre_import_2020_20260625_191629.db
```

Statistiche commit:

| Voce | Conteggio |
|---|---:|
| Athlete creati | 885 |
| Event creati | 76 |
| Result creati | 33.777 |
| Result completi creati | 20.887 |
| Result parziali creati | 12.890 |
| Event aggiornati | 94 |
| Country atleta aggiornate | 8 |
| `represented_country` corretti sui result | 96 |
| Atleti con nuovi result | 3.906 |
| Event con nuovi result | 76 |
| Duplicati saltati | 5 |
| D-score orfani lasciati fuori dal DB | 696 |

Stato DB dopo il commit:

| Entita | Conteggio |
|---|---:|
| Athlete | 12.230 |
| Event | 521 |
| Result | 230.398 |
| Notification | 0 |

### 9.9 Controlli post-import 2020

Distribuzione result per anno dopo il commit:

| Anno evento | Result |
|---|---:|
| 2018 | 89.988 |
| 2019 | 106.084 |
| 2020 | 34.326 |

Qualita dati 2020:

| Indicatore | Conteggio |
|---|---:|
| Result completi 2020 | 20.887 |
| Result 2020 con final score ma senza D-score | 13.439 |
| Result 2020 senza final score | 0 |

Controllo duplicati semantici:

| Controllo | Esito |
|---|---:|
| Gruppi duplicati semantici | 0 |

Nota: i result 2020 sono 34.326 perche il file 2019 conteneva gia 549 result riferiti all'evento `1st Spanish League (2020 season)`, registrati correttamente con `Event.year=2020`.

### 9.10 Strumenti riutilizzabili

Per evitare comandi manuali fragili e rendere coerenti gli anni successivi, e stato aggiunto lo script:

```text
scripts/generate_gymternet_preview_reports.py
```

Lo script genera automaticamente preview summary, CSV duplicati/conflitti, CSV D-score orfani e CSV review atleta/country per l'anno indicato.

Durante il flusso 2020 sono stati aggiunti anche:

- `scripts/apply_gymternet_review_decisions.py`: trasferisce le decisioni dai CSV/Numbers al payload tecnico;
- `scripts/preview_gymternet_with_decisions.py`: riesegue una preview con decisioni applicate;
- `scripts/commit_gymternet_year.py`: esegue il commit controllato di un anno dopo preflight e backup.

### 9.11 Stato operativo finale 2020

Il 2020 e stato importato nel database locale.

Il commit reale ha creato 33.777 result nuovi e non ha introdotto duplicati semantici.

I 696 D-score orfani sono stati conservati in `docs/import_reports/gymternet_2020_orphan_dscores.csv` per eventuale recupero futuro, ma non sono stati importati nel database operativo.

## 10. Import 2021 - Preview, review e commit

Data preview: 25 giugno 2026  
Data commit database locale: 25 giugno 2026

File sorgente: `import_files/Results 2021.xlsx`

Stato: import 2021 committato e verificato

La preview 2021 e stata eseguita dopo il commit reale 2020. Il database di partenza conteneva:

| Entita | Conteggio |
|---|---:|
| Athlete | 12.230 |
| Event | 521 |
| Result | 230.398 |
| Notification | 0 |

### 10.1 Sintesi preview iniziale 2021

| Voce | Conteggio |
|---|---:|
| Righe parse | 77.423 |
| Result importabili | 77.423 |
| Athlete che verrebbero creati senza decisioni admin | 3.013 |
| Event che verrebbero creati | 196 |
| Duplicati identici interni al file | 0 |
| Conflitti bloccanti iniziali | 0 |
| Warning | 2 |

Warning prodotti:

- 1.341 D-score non agganciati a final score;
- assegnazione automatica `day` applicata a 7 chiavi multi-day, con 14 righe valorizzate fino a `day=2`.

### 10.2 File generati

| File | Scopo |
|---|---|
| `docs/import_reports/gymternet_2021_preview_summary.json` | Sintesi tecnica completa della preview 2021. |
| `docs/import_reports/gymternet_2021_duplicates.csv` | Audit dei duplicati identici interni al file; vuoto. |
| `docs/import_reports/gymternet_2021_conflicts.csv` | Audit dei conflitti bloccanti; vuoto. |
| `docs/import_reports/gymternet_2021_orphan_dscores.csv` | D-score orfani non agganciati a final score. |
| `docs/import_reports/gymternet_2021_athlete_review.csv` | Review atleta/country completa e tecnica. |
| `docs/import_reports/gymternet_2021_existing_athlete_match_review.csv` | CSV operativo per match con atleti gia presenti nel DB. |
| `docs/import_reports/gymternet_2021_new_athlete_country_conflicts.csv` | CSV operativo per nuovi atleti con conflitti country. |
| `docs/import_reports/gymternet_2021_athlete_name_corrections.csv` | Correzioni nome atleta esistente verificate dall'admin. |
| `docs/import_reports/gymternet_2021_athlete_match_decisions.json` | Payload tecnico delle decisioni admin. |
| `docs/import_reports/gymternet_2021_preview_with_decisions_summary.json` | Preview con decisioni admin applicate, senza commit. |
| `docs/import_reports/gymternet_2021_post_decision_conflicts.csv` | Audit dei conflitti post-decisione; rigenerato vuoto dopo la correzione finale. |
| `docs/import_reports/gymternet_2021_post_decision_duplicates.csv` | Audit dei duplicati identici residui dopo le decisioni; vuoto. |
| `docs/import_reports/gymternet_2021_commit_summary.json` | Report tecnico del commit reale 2021. |

### 10.3 D-score orfani 2021

Totale D-score orfani: 1.341.

| Tipo problema | Conteggio |
|---|---:|
| `athlete_missing_in_score_sheet` | 706 |
| `possible_athlete_name_typo` | 397 |
| `missing_final_score_for_context` | 116 |
| `possible_context_mismatch` | 103 |
| `possible_event_name_mismatch` | 15 |
| `missing_score_sheet_context` | 4 |

Decisione: come per 2018, 2019 e 2020, questi D-score restano fuori dal database operativo salvo review mirata futura.

### 10.4 Review atleta/country 2021

Totale review atleta/country: 329.

| Tipo review | Conteggio |
|---|---:|
| `possible_existing_athlete_match` | 280 |
| `possible_athlete_identity_collision` | 31 |
| `possible_athlete_country_change` | 18 |

CSV operativi compilati dall'admin:

| File | Righe controllate |
|---|---:|
| `gymternet_2021_existing_athlete_match_review.csv` | 326 |
| `gymternet_2021_new_athlete_country_conflicts.csv` | 3 |

### 10.5 Correzioni nome atleta

Durante la review 2021 l'admin ha identificato 5 nomi errati gia presenti nel database. E stato aggiunto il supporto backend a `target_name_update`, cosi il commit Gymternet puo correggere il nome della scheda atleta esistente senza creare una nuova entita.

| ID atleta | Nome precedente | Nome corretto | Country | Discipline |
|---:|---|---|---|---|
| 1147 | Hirohito Obama | Hirohito Kohama | JPN | MAG |
| 676 | Dawiel Carrion | Daniel Carrion | ESP | MAG |
| 8849 | Yuta Sasaki | Yutaro Sasaki | JPN | MAG |
| 8915 | Ai Takada | Airi Takada | JPN | WAG |
| 1180 | Hung Yuang-His | Hung Yuan-Hsi | TPE | MAG |

### 10.6 Decisioni applicate 2021

Dopo il trasferimento delle decisioni admin e l'aggiunta delle correzioni nome, il payload tecnico 2021 ha prodotto:

| Decisione/azione | Conteggio |
|---|---:|
| Suggerimenti accettati | 242 |
| Nuovi atleti confermati | 38 |
| Merge di identita atleta | 31 |
| Aggiornamenti country atleta | 11 |
| Country atleta mantenute | 10 |
| Correzioni nome atleta | 5 |
| Correzioni `represented_country` | 35 chiavi decisionali / 174 result corretti nel commit |
| Decisioni invalide | 0 |
| Decisioni mancanti | 0 |

### 10.7 Conflitti post-decisione risolti

La prima preview con decisioni applicate ha generato 4 conflitti, collegati a 2 proposte di merge:

- `Ona Garcia` con `Ana Garcia`;
- `Ariadna Sanchez` con `Aitana Sanchez`.

In entrambi i casi il merge avrebbe creato result nello stesso evento, round, format e apparatus con score o D-score diversi.

Decisione metodologica: applicare la regola gia consolidata:

```text
same_context_different_score_keep_separate
```

Dopo questa correzione, la preview post-decisione e risultata pulita:

| Voce | Conteggio |
|---|---:|
| Conflitti post-decisione | 0 |
| Decisioni invalide | 0 |
| Decisioni mancanti | 0 |
| Duplicati identici residui | 0 |

### 10.8 Name-order automatico

Durante la preview 2021 il tool ha applicato automaticamente la regola name-order:

| Voce | Conteggio |
|---|---:|
| Merge automatici name-order | 4 |
| Chiavi variante normalizzate | 4 |
| Record normalizzati | 20 |

### 10.9 Commit database 2021

Prima del commit e stato creato il backup:

```text
backups/leverage_pre_import_2021_20260625_204252.db
```

Statistiche commit:

| Voce | Conteggio |
|---|---:|
| Athlete creati | 2.727 |
| Event creati | 196 |
| Result creati | 77.423 |
| Result completi creati | 50.565 |
| Result parziali creati | 26.858 |
| Event aggiornati | 189 |
| Country atleta aggiornate | 11 |
| Nomi atleta aggiornati | 5 |
| `represented_country` corretti sui result | 174 |
| Atleti con nuovi result | 6.782 |
| Event con nuovi result | 196 |
| Duplicati saltati | 0 |
| D-score orfani lasciati fuori dal DB | 1.341 |

Stato DB dopo il commit:

| Entita | Conteggio |
|---|---:|
| Athlete | 14.957 |
| Event | 717 |
| Result | 307.821 |
| Notification | 0 |

### 10.10 Controlli post-import 2021

Distribuzione result per anno dopo il commit:

| Anno evento | Result |
|---|---:|
| 2018 | 89.988 |
| 2019 | 106.084 |
| 2020 | 34.326 |
| 2021 | 77.423 |

Qualita dati 2021:

| Indicatore | Conteggio |
|---|---:|
| Result completi 2021 | 50.565 |
| Result 2021 con final score ma senza D-score | 26.858 |
| Result 2021 senza final score | 0 |

Controllo duplicati semantici:

| Controllo | Esito |
|---|---:|
| Gruppi duplicati semantici | 0 |

### 10.11 Stato operativo finale 2021

Il 2021 e stato importato nel database locale.

Il commit reale ha creato 77.423 result nuovi e non ha introdotto duplicati semantici.

I 1.341 D-score orfani sono stati conservati in `docs/import_reports/gymternet_2021_orphan_dscores.csv` per eventuale recupero futuro, ma non sono stati importati nel database operativo.

## 11. Import 2022 - Preview senza commit

Data preview: 25 giugno 2026

File sorgente: `import_files/Results 2022.xlsx`

Stato: preview eseguita, nessun commit 2022 eseguito

La preview 2022 e stata eseguita dopo il commit reale 2021. Il database di partenza contiene:

| Entita | Conteggio |
|---|---:|
| Athlete | 14.957 |
| Event | 717 |
| Result | 307.821 |
| Notification | 0 |

### 11.1 Sintesi preview 2022

| Voce | Conteggio |
|---|---:|
| Righe parse | 97.937 |
| Result importabili | 97.934 |
| Athlete che verrebbero creati senza decisioni admin | 2.840 |
| Event che verrebbero creati | 219 |
| Duplicati identici interni al file | 3 |
| Conflitti bloccanti | 0 |
| Warning | 2 |

Warning prodotti:

- 1.426 D-score non agganciati a final score;
- assegnazione automatica `day` applicata a 16 chiavi multi-day, con 32 righe valorizzate fino a `day=2`.

### 11.2 File generati

| File | Scopo |
|---|---|
| `docs/import_reports/gymternet_2022_preview_summary.json` | Sintesi tecnica completa della preview 2022. |
| `docs/import_reports/gymternet_2022_duplicates.csv` | Audit dei duplicati identici interni al file. |
| `docs/import_reports/gymternet_2022_conflicts.csv` | Audit dei conflitti bloccanti; vuoto in questa preview. |
| `docs/import_reports/gymternet_2022_orphan_dscores.csv` | D-score orfani non agganciati a final score. |
| `docs/import_reports/gymternet_2022_athlete_review.csv` | Review atleta/country completa e tecnica. |
| `docs/import_reports/gymternet_2022_existing_athlete_match_review.csv` | CSV operativo per match con atleti gia presenti nel DB. |
| `docs/import_reports/gymternet_2022_new_athlete_country_conflicts.csv` | CSV operativo per nuovi atleti con conflitti country. |

### 11.3 Duplicati interni 2022

La preview segnala 3 duplicati identici interni al file. Sono duplicati innocui e verranno saltati automaticamente in fase di commit.

| Atleta | Evento | Apparatus | Score | D-score |
|---|---|---|---:|---:|
| Lee Junho | World Championships | HB | 12.233 | 5.600 |
| Lee Junho | World Championships | PB | 13.266 | 5.600 |
| Lee Junho | World Championships | SR | 13.433 | 5.000 |

### 11.4 D-score orfani 2022

Totale D-score orfani: 1.426.

| Tipo problema | Conteggio |
|---|---:|
| `athlete_missing_in_score_sheet` | 966 |
| `possible_athlete_name_typo` | 195 |
| `possible_context_mismatch` | 130 |
| `missing_final_score_for_context` | 118 |
| `possible_event_name_mismatch` | 14 |
| `missing_score_sheet_context` | 3 |

Decisione provvisoria: come per 2018, 2019, 2020 e 2021, questi D-score restano fuori dal database operativo salvo review mirata futura.

### 11.5 Review atleta/country 2022

Totale review atleta/country: 389.

| Tipo review | Conteggio |
|---|---:|
| `possible_existing_athlete_match` | 320 |
| `possible_athlete_identity_collision` | 44 |
| `possible_athlete_country_change` | 25 |

CSV operativi:

| File | Righe da controllare |
|---|---:|
| `gymternet_2022_existing_athlete_match_review.csv` | 386 |
| `gymternet_2022_new_athlete_country_conflicts.csv` | 3 |

Priorita del CSV `existing_athlete_match_review`:

| Priorita | Righe |
|---|---:|
| high | 81 |
| medium | 305 |

### 11.6 Conflitti country tra nuovi atleti

| Atleta | Discipline | Country coinvolte | Evidenza futura |
|---|---|---|---|
| Viggo Altarac | MAG | SGP, SWE | 2023: SWE; 2024: SWE; 2025: SGP/SWE |
| Andres Yustiz | MAG | USA, VEN | not found 2023-2025 |
| Kyle Millar | MAG | GBR, ISL | 2023: GBR; 2024: GBR; 2025: GBR |

Questi casi dovranno essere verificati dall'admin nel CSV dedicato.

### 11.7 Name-order automatico

Durante la preview 2022 il tool ha applicato automaticamente la regola name-order:

| Voce | Conteggio |
|---|---:|
| Merge automatici name-order | 6 |
| Chiavi variante normalizzate | 6 |
| Record normalizzati | 66 |

### 11.8 Review admin e payload decisionale 2022

Data review/commit: 30 giugno 2026

L'admin ha completato i file Numbers relativi alle collisioni atleta/country 2022. Le decisioni sono state trasferite nei CSV operativi preservando i campi tecnici originali.

| File Numbers | Righe trasferite |
|---|---:|
| `gymternet_2022_existing_athlete_match_review.numbers` | 386 |
| `gymternet_2022_new_athlete_country_conflicts.numbers` | 3 |

Il payload tecnico finale e stato generato in:

```text
docs/import_reports/gymternet_2022_athlete_match_decisions.json
```

Distribuzione finale delle azioni nel payload:

| Azione payload | Conteggio |
|---|---:|
| `merge_as_same_athlete` | 44 |
| `accept_suggestion` | 305 |
| `create_new` | 15 |
| `update_country` | 17 |
| `keep_existing_country` | 8 |

### 11.9 Conflitto post-decisione e correzione Liu Xuanxi/Liu Xuan

La prima preview post-decisione ha prodotto 7 conflitti, tutti relativi allo stesso merge suggerito:

| Atleta importato | Atleta suggerito | Evento | Motivo |
|---|---|---|---|
| Liu Xuanxi | Liu Xuan | Chinese Youth Championships 2022 | stesso contesto sportivo ma score/D-score diversi su FX, HB, PB, PH, SR, VT e AA |

Il sistema ha riconosciuto la regola decisionale persistente:

```text
same_context_different_score_keep_separate
```

Decisione applicata: la riga `athlete_match_beec068c68fc0008` e stata corretta in `keep separate`, con nota nel CSV operativo.

Dopo questa correzione la preview post-decisione e risultata pulita:

| Voce | Conteggio |
|---|---:|
| Conflitti post-decisione | 0 |
| Decisioni invalide | 0 |
| Decisioni mancanti | 0 |
| Duplicati identici residui | 3 |

I 3 duplicati identici residui sono duplicati interni gia noti di Lee Junho al World Championships 2022 e vengono saltati automaticamente dal commit.

### 11.10 Commit database 2022

Prima del commit e stato creato il backup:

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

### 11.11 Controlli post-import 2022

Distribuzione result per anno dopo il commit:

| Anno evento | Result |
|---|---:|
| 2018 | 89.988 |
| 2019 | 106.084 |
| 2020 | 34.326 |
| 2021 | 77.423 |
| 2022 | 97.075 |
| 2023 | 859 |

Nota metodologica: il file `Results 2022.xlsx` contiene anche alcuni eventi marcati come anno evento 2023. Per questo il commit del file 2022 ha creato 97.075 result su eventi 2022 e 859 result su eventi 2023.

Qualita dati importati dal commit 2022:

| Anno evento | Result completi | Final score senza D-score | Senza final score |
|---|---:|---:|---:|
| 2022 | 73.237 | 23.838 | 0 |
| 2023 | 795 | 64 | 0 |

Controllo duplicati semantici:

| Controllo | Esito |
|---|---:|
| Gruppi duplicati semantici | 0 |

### 11.12 Stato operativo finale 2022

Il 2022 e stato importato nel database locale.

Il commit reale ha creato 97.934 result nuovi e non ha introdotto duplicati semantici.

I 1.426 D-score orfani sono stati conservati in `docs/import_reports/gymternet_2022_orphan_dscores.csv` per eventuale recupero futuro, ma non sono stati importati nel database operativo.

## 12. Import 2023 - Preview senza commit

Data preview: 30 giugno 2026

File sorgente: `import_files/Results 2023.xlsx`

Stato: preview eseguita, nessun commit 2023 eseguito

La preview 2023 e stata eseguita dopo il commit reale 2022. Il database di partenza contiene:

| Entita | Conteggio |
|---|---:|
| Athlete | 17.429 |
| Event | 936 |
| Result | 405.755 |
| Notification | 0 |

### 12.1 Sintesi preview 2023

| Voce | Conteggio |
|---|---:|
| Righe parse | 117.489 |
| Result importabili | 117.489 |
| Athlete che verrebbero creati senza decisioni admin | 3.908 |
| Event che verrebbero creati | 241 |
| Duplicati identici interni al file | 0 |
| Conflitti bloccanti | 0 |
| Warning | 2 |

Warning prodotti:

- 1.454 D-score non agganciati a final score;
- assegnazione automatica `day` applicata a 104 chiavi multi-day, con 208 righe valorizzate fino a `day=2`.

### 12.2 Distribuzione anni nel file 2023

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

### 12.3 File generati

| File | Scopo |
|---|---|
| `docs/import_reports/gymternet_2023_preview_summary.json` | Sintesi tecnica completa della preview 2023. |
| `docs/import_reports/gymternet_2023_duplicates.csv` | Audit dei duplicati identici interni al file; vuoto in questa preview. |
| `docs/import_reports/gymternet_2023_conflicts.csv` | Audit dei conflitti bloccanti; vuoto in questa preview. |
| `docs/import_reports/gymternet_2023_orphan_dscores.csv` | D-score orfani non agganciati a final score. |
| `docs/import_reports/gymternet_2023_athlete_review.csv` | Review atleta/country completa e tecnica. |
| `docs/import_reports/gymternet_2023_existing_athlete_match_review.csv` | CSV operativo per match con atleti gia presenti nel DB. |
| `docs/import_reports/gymternet_2023_new_athlete_country_conflicts.csv` | CSV operativo per nuovi atleti con conflitti country. |

### 12.4 D-score orfani 2023

Totale D-score orfani: 1.454.

| Tipo problema | Conteggio |
|---|---:|
| `athlete_missing_in_score_sheet` | 1.045 |
| `possible_context_mismatch` | 126 |
| `missing_final_score_for_context` | 122 |
| `possible_athlete_name_typo` | 77 |
| `possible_event_name_mismatch` | 62 |
| `missing_score_sheet_context` | 22 |

Decisione provvisoria: come per gli anni precedenti, questi D-score restano fuori dal database operativo salvo review mirata futura.

### 12.5 Review atleta/country 2023

Totale review atleta/country: 577.

| Tipo review | Conteggio |
|---|---:|
| `possible_existing_athlete_match` | 490 |
| `possible_athlete_identity_collision` | 52 |
| `possible_athlete_country_change` | 35 |

CSV operativi:

| File | Righe da controllare |
|---|---:|
| `gymternet_2023_existing_athlete_match_review.csv` | 568 |
| `gymternet_2023_new_athlete_country_conflicts.csv` | 9 |

Priorita del CSV `existing_athlete_match_review`:

| Priorita | Righe |
|---|---:|
| high | 111 |
| medium | 457 |

### 12.6 Conflitti country tra nuovi atleti

| Atleta | Discipline | Country coinvolte | Evidenza futura |
|---|---|---|---|
| Lucia Gonzalez | WAG | ARG, ESP | 2024: ARG; 2025: ARG |
| Phong Tage Gullbrandsson | MAG | NOR, SWE | 2024: NOR; 2025: NOR |
| Paloma Mintcheva | WAG | BUL, USA | not found 2024-2025 |
| Yaroslav Krutov | MAG | BLR, RUS | 2024: BLR |
| Nicolo Mozzato | MAG | FRA, ITA | 2024: ITA; 2025: ITA |
| Timm Sauter | MAG | GER, SUI | 2024: GER; 2025: GER |
| Bogdan Ilyinkov | MAG | BLR, RUS | 2024: BLR |
| Yoan Ivanov | MAG | BUL, GBR | 2024: BUL/GBR; 2025: BUL |
| Amber Ward Wen Si | WAG | AUS, HKG | 2024: HKG; 2025: HKG |

### 12.7 Name-order automatico

Durante la preview 2023 il tool ha applicato automaticamente la regola name-order:

| Voce | Conteggio |
|---|---:|
| Merge automatici name-order | 8 |
| Chiavi variante normalizzate | 8 |
| Record normalizzati | 52 |

### 12.8 Review admin e payload decisionale 2023

L'admin ha completato i file Numbers relativi alle collisioni atleta/country 2023. Le decisioni sono state trasferite nei CSV operativi preservando i campi tecnici originali.

| File Numbers | Righe trasferite |
|---|---:|
| `gymternet_2023_existing_athlete_match_review.numbers` | 568 |
| `gymternet_2023_new_athlete_country_conflicts.numbers` | 9 |

Il payload tecnico finale e stato generato in:

```text
docs/import_reports/gymternet_2023_athlete_match_decisions.json
```

Distribuzione finale delle azioni nel payload:

| Azione payload | Conteggio |
|---|---:|
| `merge_as_same_athlete` | 52 |
| `accept_suggestion` | 444 |
| `create_new` | 46 |
| `update_country` | 19 |
| `keep_existing_country` | 16 |

### 12.9 Correzioni nome atleta 2023

Durante la review sono state definite 39 correzioni nome per atleti gia presenti nel database.

| Tipo correzione | Conteggio |
|---|---:|
| Correzioni esplicite admin | 9 |
| KOR: rimozione trattino/spazio | 21 |
| KOR: evidenza futura a favore della forma importata | 9 |

Esempi:

| Prima | Dopo |
|---|---|
| `Niccolo Vannucchi` | `Niccolò Vannucchi` |
| `Niccolo Belli` | `Niccolò Belli` |
| `Nico Oliveiri` | `Nico Olivieri` |
| `Kim Han-sol` | `Kim Hansol` |
| `Lee Yun-seo` | `Lee Yunseo` |
| `Bae Ga-ram` | `Bae Garam` |
| `Hur Wo-ong` | `Hur Woong` |
| `Lee Jun-ho` | `Lee Junho` |
| `Kim Jae Ho` | `Kim Jaeho` |

Nota metodologica: per le romanizzazioni KOR e stata applicata la correzione quando la forma importata era supportata dall'evidenza futura oppure quando si trattava di semplice rimozione di trattino/spazio. Nei casi ambigui senza evidenza univoca, la correzione automatica del nome non e stata applicata. Il caso `Shin Jea-hwan/Shin Jaehwan` puntava allo stesso atleta; e stata mantenuta la forma `Shin Jeahwan`, piu supportata dai file futuri.

File tecnico:

```text
docs/import_reports/gymternet_2023_athlete_name_corrections.csv
```

### 12.10 Conflitti post-decisione e correzioni keep separate

La prima preview post-decisione ha prodotto 9 conflitti, tutti di tipo:

```text
same_context_different_score_after_athlete_merge
```

I conflitti derivavano da due merge suggeriti:

| Atleta importato | Atleta suggerito | Evento | Conflitti |
|---|---|---|---:|
| Abdelrahman Mahmoud | Ahmed Abdelrahman | Pharaoh's Cup 2023 | 4 |
| Martina Baldi | Martina Balliu | Italian Gold Championships Qualifier 2023 | 5 |

Decisione applicata: correggere le due righe in `keep separate`, seguendo la regola persistente `same_context_different_score_keep_separate`.

Dopo questa correzione la preview post-decisione e risultata pulita:

| Voce | Conteggio |
|---|---:|
| Conflitti post-decisione | 0 |
| Decisioni invalide | 0 |
| Decisioni mancanti | 0 |
| Duplicati identici residui | 0 |
| Correzioni nome atleta | 39 |

### 12.11 Commit database 2023

Prima del commit e stato creato il backup:

```text
backups/leverage_pre_import_2023_20260630_113627.db
```

Statistiche commit:

| Voce | Conteggio |
|---|---:|
| Athlete creati | 3.384 |
| Event creati | 241 |
| Result creati | 117.489 |
| Result completi creati | 86.900 |
| Result parziali creati | 30.589 |
| Event aggiornati | 276 |
| Country atleta aggiornate | 21 |
| Nomi atleta aggiornati | 39 |
| `represented_country` corretti sui result | 414 |
| Atleti con nuovi result | 8.979 |
| Event con nuovi result | 241 |
| Duplicati saltati | 0 |
| D-score orfani lasciati fuori dal DB | 1.454 |

Stato DB dopo il commit:

| Entita | Conteggio |
|---|---:|
| Athlete | 20.813 |
| Event | 1.177 |
| Result | 523.244 |
| Notification | 0 |

### 12.12 Controlli post-import 2023

Distribuzione result per anno dopo il commit:

| Anno evento | Result |
|---|---:|
| 2018 | 89.988 |
| 2019 | 106.084 |
| 2020 | 34.326 |
| 2021 | 77.423 |
| 2022 | 97.075 |
| 2023 | 117.256 |
| 2024 | 1.092 |

Nota metodologica: il file `Results 2023.xlsx` contiene anche alcuni eventi marcati come anno evento 2024. Per questo il commit del file 2023 ha creato 117.256 result su eventi 2023 e 1.092 result su eventi 2024.

Qualita dati importati dal commit 2023:

| Anno evento | Result completi | Final score senza D-score | Senza final score |
|---|---:|---:|---:|
| 2023 | 86.702 | 30.554 | 0 |
| 2024 | 993 | 99 | 0 |

Controllo duplicati semantici:

| Controllo | Esito |
|---|---:|
| Gruppi duplicati semantici | 0 |

### 12.13 Stato operativo finale 2023

Il 2023 e stato importato nel database locale.

Il commit reale ha creato 117.489 result nuovi e non ha introdotto duplicati semantici.

I 1.454 D-score orfani sono stati conservati in `docs/import_reports/gymternet_2023_orphan_dscores.csv` per eventuale recupero futuro, ma non sono stati importati nel database operativo.

### 12.14 Regola futura su review same-country gia controllate

Dopo la review 2023 e stata formalizzata una nuova regola metodologica per ridurre controlli ripetitivi negli anni successivi.

Quando un caso `possible_existing_athlete_match` riguarda due varianti nome gia controllate dall'ADMIN e il country non cambia, il tool puo riusare la decisione precedente come raccomandazione forte:

- `merge as same athlete`, se il caso era stato gia validato come errore di battitura, accento, trattino/spazio, ordine nome/cognome o romanizzazione;
- `keep separate`, se il caso era stato gia validato come due atleti distinti.

Nel CSV operativo futuro la decisione puo essere precompilata e tracciata con `same_country_review_reuse`.

La precompilazione avviene solo se le review degli anni precedenti danno una decisione univoca per quella coppia atleta/variante nome. Se la memoria storica e discordante, il caso resta manuale.

La regola vale solo per casi same-country. Se il country cambia, la review manuale admin resta obbligatoria, perche il caso puo riguardare un cambio reale di rappresentanza, un errore country del file sorgente o una fusione rischiosa tra atleti diversi.

## 13. Import 2024 - Preview iniziale

File sorgente: `import_files/Results 2024.xlsx`

Documento operativo dedicato:

```text
docs/LEVERAGE_import_2024_review.md
```

### 13.1 Stato del database prima della preview 2024

La preview 2024 e stata eseguita sul database locale gia popolato e verificato fino al commit reale 2023.

Conteggi DB prima della preview:

| Entita | Conteggio |
|---|---:|
| Athlete | 20.813 |
| Event | 1.177 |
| Result | 523.244 |
| Notification | 0 |

### 13.2 Esito tecnico preview 2024

| Voce | Conteggio |
|---|---:|
| Righe parse | 106.449 |
| Result importabili | 106.449 |
| Athlete che verrebbero creati senza decisioni admin | 3.051 |
| Event che verrebbero creati | 206 |
| Duplicati identici interni al file | 0 |
| Conflitti bloccanti | 0 |
| Warning | 2 |

Warning principali:

- 1.113 D-score non agganciati a final score;
- assegnazione automatica `day` applicata a 5 chiavi multi-day, con 10 righe valorizzate fino a `day=2`.

### 13.3 Distribuzione anni nel file 2024

Il file `Results 2024.xlsx` contiene anche 495 record associati a eventi con anno evento 2025.

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

### 13.4 File generati

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
| `docs/import_reports/gymternet_2024_commit_summary.json` | Report tecnico del commit reale 2024, con backup, statistiche di import e controlli post-import. |

### 13.5 Review atleta/country 2024

Totale review atleta/country: 562.

Distribuzione:

| Tipo review | Conteggio |
|---|---:|
| `possible_existing_athlete_match` | 498 |
| `possible_athlete_identity_collision` | 41 |
| `possible_athlete_country_change` | 23 |

CSV operativi:

| File | Righe | Stato |
|---|---:|---|
| `gymternet_2024_existing_athlete_match_review.csv` | 552 | 211 decisioni precompilate da `same_country_review_reuse`; 341 righe ancora da controllare. |
| `gymternet_2024_new_athlete_country_conflicts.csv` | 10 | 10 righe ancora da controllare. |

Distribuzione delle 341 decisioni mancanti nel CSV existing athlete:

| Tipo review | Righe da controllare |
|---|---:|
| `possible_existing_athlete_match` | 287 |
| `possible_athlete_identity_collision` | 31 |
| `possible_athlete_country_change` | 23 |

Le 211 decisioni precompilate sono tutte `merge as same athlete` su casi same-country gia verificati in anni precedenti. Restano comunque modificabili dall'admin se durante la review emergono nuove evidenze.

### 13.6 Conflitti country tra nuovi atleti

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

### 13.7 Review admin completata

Il 30 giugno 2026 l'admin ha completato i due file Numbers relativi alle collisioni atleta/country 2024. Le decisioni sono state trasferite nei CSV operativi preservando i campi tecnici originali e aggiornando soltanto:

- `decision`;
- `action`;
- `country`;
- `notes`.

| File Numbers | Righe trasferite nel CSV operativo |
|---|---:|
| `gymternet_2024_existing_athlete_match_review.numbers` | 552 |
| `gymternet_2024_new_athlete_country_conflicts.numbers` | 10 |

Payload tecnico generato:

```text
docs/import_reports/gymternet_2024_athlete_match_decisions.json
```

Statistiche decisioni generate dal payload:

| Azione | Conteggio |
|---|---:|
| Suggerimenti atleta accettati | 462 |
| Nuovi atleti confermati / create new | 36 |
| Merge identita atleta | 41 |
| Country updates | 16 |
| Country kept | 7 |

### 13.8 Preview post-decisione e correzione conflitti residui

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

La regola significa che una proposta di merge atleta deve essere annullata quando produce lo stesso identico contesto sportivo di result ma con score o D-score diversi.

Sono state quindi corrette tre decisioni nel CSV operativo `gymternet_2024_existing_athlete_match_review.csv`, portandole da `merge as same athlete` a `keep separate`:

| Atleta importato | Atleta gia presente suggerito | Motivo |
|---|---|---|
| Max Griffiths | Mac Griffiths | Merge produceva 7 result nello stesso contesto della `English Championships 2024` con score/D-score diversi. |
| Ania Fernandez | Jana Fernandez | Merge produceva 1 result nello stesso contesto della `Spanish League Final 2024` con score/D-score diverso. |
| Lee Seyeon | Lee Seoyeon | Merge produceva 5 result nello stesso contesto della `South Korean Championships 2024` con score/D-score diversi. |

Il payload decisionale e stato rigenerato senza rileggere i Numbers, usando i CSV operativi come fonte autorevole.

Statistiche decisioni finali:

| Azione | Conteggio |
|---|---:|
| Suggerimenti atleta accettati | 459 |
| Nuovi atleti confermati / create new | 39 |
| Merge identita atleta | 41 |
| Country updates | 20 |
| Country kept | 9 |
| Correzioni represented country | 39 |
| Correzioni nome atleta | 0 |
| Decisioni non valide | 0 |
| Decisioni irrisolte | 0 |

### 13.9 Preview post-decisione pulita

Esito finale preview post-decisione 2024:

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

File generati:

```text
docs/import_reports/gymternet_2024_preview_with_decisions_summary.json
docs/import_reports/gymternet_2024_post_decision_conflicts.csv
docs/import_reports/gymternet_2024_post_decision_duplicates.csv
```

I file `post_decision_conflicts` e `post_decision_duplicates` risultano vuoti.

### 13.10 Commit database 2024

Prima del commit e stato creato il backup:

```text
backups/leverage_pre_import_2024_20260630_185841.db
```

Il commit reale e stato eseguito usando:

```text
scripts/commit_gymternet_year.py
```

Report tecnico generato:

```text
docs/import_reports/gymternet_2024_commit_summary.json
```

Statistiche commit:

| Voce | Conteggio |
|---|---:|
| Athlete creati | 2.535 |
| Event creati | 206 |
| Result creati | 106.449 |
| Result completi creati | 78.334 |
| Result parziali creati | 28.115 |
| Event aggiornati | 262 |
| Country atleta aggiornate | 20 |
| Nomi atleta aggiornati | 0 |
| `represented_country` corretti sui result | 224 |
| Atleti con nuovi result | 8.672 |
| Event con nuovi result | 206 |
| Duplicati saltati | 0 |
| D-score orfani lasciati fuori dal DB | 1.113 |

Stato DB dopo il commit:

| Entita | Conteggio |
|---|---:|
| Athlete | 23.348 |
| Event | 1.383 |
| Result | 629.693 |
| Notification | 0 |

### 13.11 Controlli post-import 2024

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
| 2025 | 495 |

Nota metodologica: il file `Results 2024.xlsx` contiene anche 495 record associati a eventi con anno evento 2025. Per questo il commit del file 2024 ha portato il totale dell'anno 2024 a 107.046 result e ha creato 495 result su eventi 2025.

Qualita dati importati dal commit 2024:

| Anno evento | Result completi | Final score senza D-score | Senza final score |
|---|---:|---:|---:|
| 2024 | 78.857 | 28.189 | 0 |
| 2025 | 470 | 25 | 0 |

Controllo duplicati semantici:

| Controllo | Esito |
|---|---:|
| Gruppi duplicati semantici | 0 |

### 13.12 Stato operativo finale 2024

Il 2024 e stato importato nel database locale.

Il commit reale ha creato 106.449 result nuovi e non ha introdotto duplicati semantici.

I 1.113 D-score orfani sono stati conservati in `docs/import_reports/gymternet_2024_orphan_dscores.csv` per eventuale recupero futuro, ma non sono stati importati nel database operativo.

## 14. Import 2025 - Preview iniziale

File sorgente: `import_files/Results 2025.xlsx`

Documento operativo dedicato:

```text
docs/LEVERAGE_import_2025_review.md
```

### 14.1 Stato del database prima della preview 2025

La preview 2025 e stata eseguita sul database locale gia popolato e verificato fino al commit reale 2024.

Conteggi DB prima della preview:

| Entita | Conteggio |
|---|---:|
| Athlete | 23.348 |
| Event | 1.383 |
| Result | 629.693 |
| Notification | 0 |

### 14.2 Esito tecnico preview 2025

| Voce | Conteggio |
|---|---:|
| Righe parse | 124.030 |
| Result importabili | 124.030 |
| Athlete che verrebbero creati senza decisioni admin | 3.448 |
| Event che verrebbero creati | 222 |
| Duplicati identici interni al file | 0 |
| Conflitti bloccanti | 0 |
| Warning | 3 |

Warning principali:

- 630 D-score non agganciati a final score;
- assegnazione automatica `day` applicata a 29 chiavi multi-day, con 58 righe valorizzate fino a `day=2`;
- il legacy Gymternet import ha rilevato result successivi al 2025 e applica le regole 2025 su vault e componenti mancanti. E_score, Penalty e Bonus mancanti restano `not available`. Per dati futuri con componenti esplicite sara preferibile usare il nuovo standard import dedicato.

### 14.3 Distribuzione anni nel file 2025

Il file `Results 2025.xlsx` contiene anche 108 record associati a eventi con anno evento 2026.

| Anno evento nel file | Result parse | Event distinti |
|---|---:|---:|
| 2025 | 123.922 | 221 |
| 2026 | 108 | 1 |

Eventi 2026 presenti nel file 2025:

| Event | Result parse |
|---|---:|
| `Top 12 Series 3 (2026)` | 108 |

Decisione metodologica: come per gli spillover gia rilevati nei file precedenti, questi record non sono considerati errore tecnico. Il sistema usa l'anno evento presente nel file sorgente.

### 14.4 File generati

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

### 14.5 Review atleta/country 2025

Totale review atleta/country: 636.

Distribuzione:

| Tipo review | Conteggio |
|---|---:|
| `possible_existing_athlete_match` | 535 |
| `possible_athlete_identity_collision` | 69 |
| `possible_athlete_country_change` | 32 |

CSV operativi:

| File | Righe | Stato |
|---|---:|---|
| `gymternet_2025_existing_athlete_match_review.csv` | 628 | 227 decisioni precompilate da `same_country_review_reuse`; 401 righe ancora da controllare. |
| `gymternet_2025_new_athlete_country_conflicts.csv` | 8 | 8 righe ancora da controllare. |

Distribuzione delle 401 decisioni mancanti nel CSV existing athlete:

| Tipo review | Righe da controllare |
|---|---:|
| `possible_existing_athlete_match` | 308 |
| `possible_athlete_identity_collision` | 61 |
| `possible_athlete_country_change` | 32 |

Le 227 decisioni precompilate sono tutte `merge as same athlete` su casi same-country gia verificati in anni precedenti. Restano comunque modificabili dall'admin se durante la review emergono nuove evidenze.

### 14.6 Conflitti country tra nuovi atleti

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

### 14.7 Review admin completata

Il 30 giugno 2026 l'admin ha completato i due file Numbers relativi alle collisioni atleta/country 2025. Le decisioni sono state trasferite nei CSV operativi preservando i campi tecnici originali e aggiornando soltanto:

- `decision`;
- `action`;
- `country`;
- `notes`.

| File Numbers | Righe trasferite nel CSV operativo |
|---|---:|
| `gymternet_2025_existing_athlete_match_review.numbers` | 628 |
| `gymternet_2025_new_athlete_country_conflicts.numbers` | 8 |

E stata aggiunta anche una correzione nome atleta esistente:

| Review | Athlete ID | Nome precedente | Nome corretto |
|---|---:|---|---|
| `athlete_match_5181b096d32f4b0a` | 18410 | Niccolo Martin | Niccolò Martin |

Payload tecnico generato:

```text
docs/import_reports/gymternet_2025_athlete_match_decisions.json
```

### 14.8 Preview post-decisione e correzione conflitti residui

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

Sono state quindi corrette sette decisioni nel CSV operativo `gymternet_2025_existing_athlete_match_review.csv`, portandole da `merge as same athlete` a `keep separate`:

| Atleta importato | Atleta gia presente suggerito | Motivo |
|---|---|---|
| Saya Okubo | Aya Okubo | Merge produceva 5 result nello stesso contesto della `All-Japan Junior Championships 2025` con score diversi. |
| Anna Klykova | Anna Kalmykova | Merge produceva 4 result nello stesso contesto della `Russian Championships 2025` con score/D-score diversi. |
| Mia Fujiwara | Mirea Fujiwara | Merge produceva 5 result nello stesso contesto della `All-Japan Student Championships 2025` con score/D-score diversi. |
| Marta Garcia | Maria Garcia | Merge produceva 1 result nello stesso contesto della `2nd Spanish League 2025` con score/D-score diverso. |
| Lee Sooyeon | Lee Seoyeon | Merge produceva 5 result nello stesso contesto della `South Korean Championships 2025` con score/D-score diversi. |
| Lee Jiyeon | Lee Jiseon | Merge produceva 10 result negli stessi contesti della `Korean National Sports Festival 2025` e `South Korean Championships 2025` con score/D-score diversi. |
| Zeng Yifan | Zeng Yiran | Merge produceva 3 result nello stesso contesto della `Chinese Junior Championships 2025` con score/D-score diversi. |

Il payload decisionale e stato rigenerato senza rileggere i Numbers, usando i CSV operativi come fonte autorevole.

Statistiche decisioni finali:

| Azione | Conteggio |
|---|---:|
| Suggerimenti atleta accettati | 451 |
| Nuovi atleti confermati / create new | 85 |
| Merge identita atleta | 69 |
| Country updates | 15 |
| Country kept | 21 |
| Correzioni represented country | 75 |
| Correzioni nome atleta | 1 |
| Decisioni non valide | 0 |
| Decisioni irrisolte | 0 |

### 14.9 Preview post-decisione pulita

Esito finale preview post-decisione 2025:

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

File generati:

```text
docs/import_reports/gymternet_2025_preview_with_decisions_summary.json
docs/import_reports/gymternet_2025_post_decision_conflicts.csv
docs/import_reports/gymternet_2025_post_decision_duplicates.csv
```

I file `post_decision_conflicts` e `post_decision_duplicates` risultano vuoti.

### 14.10 Commit database 2025

Prima del commit e stato creato il backup:

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

### 14.11 Controlli post-import 2025

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

### 14.12 Stato operativo finale 2025

Il 2025 e stato importato nel database locale.

Il commit reale ha creato 124.030 result nuovi e non ha introdotto duplicati semantici.

I 630 D-score orfani sono stati conservati in `docs/import_reports/gymternet_2025_orphan_dscores.csv` per eventuale recupero futuro, ma non sono stati importati nel database operativo.

Il database contiene gia 108 result associati a evento 2026. Quando verra importato il file Gymternet 2026, questi result dovranno essere considerati nel controllo duplicati/preflight.

## 15. Integrazione calendario eventi Gymternet

### 15.1 Obiettivo

Dopo il popolamento storico dei Result 2018-2025, Gymternet ha fornito un file `Calendar.xlsx` con i calendari annuali 2018-2026. Il file contiene, per ogni anno, le colonne `DATE` ed `EVENT`.

L'obiettivo operativo e aggiornare le date degli Event gia presenti nel database LEVERAGE e predisporre, in seguito, una vista calendario admin che mostri:

- eventi passati con risultati gia importati;
- eventi passati senza risultati;
- eventi futuri ancora da disputare;
- promemoria admin per eventi conclusi senza Result.

### 15.2 Regole tecniche adottate

Il backend calendario e stato sviluppato con un flusso prudente:

- preview prima di qualsiasi scrittura;
- commit admin-only;
- creazione automatica solo degli eventi futuri o comunque a partire da `create_missing_from_year`;
- righe storiche non matchate lasciate in review;
- blocco del commit in presenza di duplicati sorgente;
- blocco del commit se piu righe calendario puntano allo stesso Event DB con date diverse.

Regola semantica aggiunta il 1 luglio 2026: nei nomi evento, `MAG` indica una gara maschile e puo corrispondere a varianti DB con `Men's`/`Mens`; `WAG` indica una gara femminile e puo corrispondere a varianti DB con `Women's`/`Womens`.

Questa regola ha ridotto i falsi mismatch nel calendario 2018, ma ha anche reso visibili casi in cui una gara creata nel DB come `MAG and WAG` e richiamata da piu righe calendario distinte.

### 15.3 Primo audit calendario 2018

Report generati:

```text
docs/import_reports/calendar_2018_event_match_review.csv
docs/import_reports/calendar_2018_event_match_review_slim.csv
docs/import_reports/calendar_2018_db_unmatched_events.csv
docs/import_reports/calendar_2018_source_conflicts.csv
docs/import_reports/calendar_2018_source_conflicts_slim.csv
docs/import_reports/calendar_2018_match_summary.csv
```

Riepilogo numerico 2018 dopo normalizzazione MAG/Men's e WAG/Women's:

| Controllo | Conteggio |
|---|---:|
| Righe calendar 2018 | 214 |
| Righe calendar matchate | 205 |
| Righe calendar senza match diretto | 9 |
| Event DB 2018 | 211 |
| Event DB matchati | 197 |
| Event DB senza match calendar | 14 |
| Event DB senza match calendar con result | 14 |
| Event DB matchati da piu righe calendar | 8 |
| Conflitti stesso Event DB / date diverse | 8 |
| Delta righe calendar unmatched - Event DB unmatched | -5 |

Interpretazione: la differenza tra mismatch lato calendario e mismatch lato DB non e automaticamente un errore. In particolare, alcuni Event DB rappresentano gare `MAG and WAG`, mentre il calendario puo distinguere righe MAG e WAG con date diverse. Questi casi richiedono review admin prima di aggiornare le date definitive.

Il 2026 resta momentaneamente in standby perche il file Results 2026 del primo semestre non e ancora stato ricevuto.

### 15.4 Commit sicuro date calendario 2018

Per applicare le date agli Event associati e stato creato lo script:

```text
scripts/commit_calendar_year.py
```

Lo script lavora anno per anno e separa tre categorie:

- match diretti sicuri, applicabili automaticamente;
- righe calendario senza match diretto, da compilare nel CSV `calendar_<anno>_event_match_review.csv`;
- conflitti in cui piu righe calendario puntano allo stesso Event DB con date diverse, da compilare nel CSV `calendar_<anno>_source_conflicts.csv`.

Aggiornamento operativo: per rendere la review admin piu rapida sono state aggiunte versioni semplificate dei CSV:

```text
docs/import_reports/calendar_2018_event_match_review_slim.csv
docs/import_reports/calendar_2018_source_conflicts_slim.csv
```

Questi file mostrano soltanto:

- evento calendario;
- data calendario;
- possibili Event DB associabili come opzioni numerate;
- colonna `choice` da compilare.

Se l'admin inserisce `choice = 1`, `2` o `3`, lo script associa la riga calendario alla relativa opzione. Se invece inserisce `choice = calendar_only`, la riga resta una voce calendario non collegata a una scheda Event: sara quindi visualizzabile nel calendario futuro ma non rimandera alla scheda evento.

Durante la review 2018 sono emersi casi in cui la scelta corretta e multipla, ad esempio `choice = 1 and 2`. Questo accade quando due voci calendario sono entrambe corrette per lo stesso Event DB, spesso perche un Event `MAG and WAG` contiene risultati MAG e WAG disputati in date diverse.

Decisione metodologica: in questi casi non si forza una data unica nel record `Event`, perche sarebbe semanticamente scorretto. Viene invece creata una voce `EventCalendarEntry`, cioe una riga calendario separata che puo puntare alla stessa scheda Event. In futuro, la UI calendario potra mostrare due righe distinte ma farle rimandare alla stessa scheda evento.

Il primo dry-run 2018 ha individuato:

| Controllo | Conteggio |
|---|---:|
| Righe calendar 2018 | 214 |
| Match sicuri applicabili | 189 |
| Righe saltate per conflitto stesso Event/date diverse | 16 |
| Elementi review aperti | 17 |
| Decisioni invalide | 0 |

Il commit reale 2018 e stato eseguito solo sui match sicuri.

Report generati:

```text
docs/import_reports/calendar_2018_dry_run_summary.json
docs/import_reports/calendar_2018_commit_summary.json
```

Esito del commit reale:

| Controllo | Conteggio |
|---|---:|
| Event aggiornati con `start_date` / `end_date` dal primo commit sicuro | 189 |
| Event aggiornati con `start_date` / `end_date` dopo review slim | 8 |
| Event 2018 totali nel DB | 211 |
| Event 2018 con date dopo commit review | 196 |
| Event 2018 ancora senza date | 15 |
| Calendar entries 2018 create | 26 |
| Elementi review ancora aperti | 0 |

Un backup locale del database e stato creato automaticamente prima del commit. Il backup non viene tracciato da Git perche il database locale e escluso dal repository.

Secondo controllo di copertura 2018:

Dopo il primo commit e stato effettuato un controllo piu restrittivo, imponendo che i suggerimenti di match fossero sempre interni a `Event.year = 2018`. Questo ha evidenziato un collegamento cross-year errato: la riga Calendar 2018 `Buckeye National Qualifier` era stata associata all'Event DB `Buckeye National Qualifier` del 2019, mentre il corrispettivo corretto nel DB 2018 era `Buckeye Qualifier`.

Sono stati generati file di review corrente:

```text
docs/import_reports/calendar_2018_calendar_unmatched_current.csv
docs/import_reports/calendar_2018_db_unmatched_current.csv
docs/import_reports/calendar_2018_cross_year_calendar_entries.csv
```

Le decisioni admin hanno associato:

| Event DB 2018 | Riga Calendar 2018 |
|---|---|
| `Buckeye Qualifier` | `Buckeye National Qualifier` |
| `Houston National Invite` | `Houston National Invitational` |
| `DTB Team Challenge` | `DTB Pokal Team Challenge` |
| `Junior Pan Am Championships` | `Junior Pan American Championships` |
| `Ukraine Open Cup` | `Kiev Open Cup` |
| `Swiss Duel` | `Swiss Cup` |

Esito del secondo commit corrente 2018:

| Controllo | Conteggio |
|---|---:|
| Decisioni applicate | 6 |
| Event 2018 aggiornati con date | 6 |
| Calendar entries create | 5 |
| Calendar entries rilinkate da anno errato | 1 |
| Date 2018 rimosse da Event 2019 errato | 1 |
| Decisioni invalide | 0 |
| Calendar 2018 senza match finale | 0 |
| Event DB 2018 senza match finale | 0 |
| Collegamenti cross-year finali | 0 |

Il controllo finale conferma quindi la copertura completa del 2018: tutte le 214 righe Calendar 2018 hanno almeno un match DB 2018 e tutti i 211 Event DB 2018 hanno una copertura calendario diretta o tramite `EventCalendarEntry`.

Nota metodologica: l'aggiornamento delle date serve ad alimentare la futura UI calendario cliccabile. Ogni Event datato potra comparire nella vista calendario pubblica/admin con stato calcolato (`upcoming`, `ongoing`, `completed_with_results`, `completed_no_results`) e collegamento alla scheda evento.

### Calendar 2019

Il flusso Calendar 2019 e stato avviato applicando la regola corretta emersa dal controllo finale 2018: i suggerimenti e le associazioni automatiche devono rimanere nello stesso anno del foglio Calendar. Dunque le righe Calendar 2019 vengono confrontate solo con `Event.year = 2019`.

Situazione iniziale:

| Controllo | Conteggio |
|---|---:|
| Righe Calendar 2019 | 244 |
| Event DB 2019 ricavati dai Result | 233 |
| Righe Calendar 2019 con match automatico | 231 |
| Righe Calendar 2019 senza match automatico | 13 |
| Event DB 2019 con match automatico | 222 |
| Event DB 2019 senza match automatico | 11 |
| Event DB 2019 matched da piu righe Calendar | 9 |
| Conflitti stesso Event/date diverse | 8 |
| Duplicate source rows | 0 |

Primo commit sicuro 2019:

| Controllo | Conteggio |
|---|---:|
| Righe dirette sicure applicate | 215 |
| Event aggiornati con `start_date` / `end_date` | 214 |
| Event gia coerenti/no change | 1 |
| Righe saltate per conflitto stesso Event/date diverse | 16 |
| Elementi review ancora aperti | 21 |
| Decisioni invalide | 0 |

Backup locale creato automaticamente:

```text
backups/leverage_calendar_2019_20260701_220455.db
```

Report generati per la review 2019:

```text
docs/import_reports/calendar_2019_event_match_review_slim.csv
docs/import_reports/calendar_2019_source_conflicts_slim.csv
docs/import_reports/calendar_2019_calendar_unmatched_current.csv
docs/import_reports/calendar_2019_db_unmatched_current.csv
docs/import_reports/calendar_2019_cross_year_calendar_entries.csv
```

Per la review manuale 2019 verranno usati soprattutto:

- `calendar_2019_calendar_unmatched_current.csv`: righe Calendar 2019 ancora senza match DB 2019;
- `calendar_2019_db_unmatched_current.csv`: Event DB 2019 ancora senza copertura Calendar;
- `calendar_2019_source_conflicts_slim.csv`: Event gia matchati da piu righe Calendar con date diverse, spesso casi MAG/WAG o competizioni con piu giornate/serie.

Fotografia post-commit sicuro:

| Controllo | Conteggio |
|---|---:|
| Calendar 2019 senza match corrente | 13 |
| Event DB 2019 senza match corrente | 11 |
| Event DB 2019 gia coperti | 222 |
| Collegamenti cross-year rilevati | 0 |

Nota metodologica: nel caso in cui una riga Calendar e un Event DB rappresentino lo stesso evento ma con nomi abbreviati o leggermente diversi, l'associazione viene confermata dall'admin nei CSV. Nel caso in cui un Event `MAG and WAG` abbia piu righe Calendar/date distinte, il sistema puo creare o mantenere piu `EventCalendarEntry` collegate alla stessa scheda Event, senza forzare una singola data nel record `Event`.

Review admin corrente 2019:

Le decisioni admin sono state lette dai file compilati in Numbers e riportate nei CSV operativi. Sono stati usati tre livelli di controllo:

- righe Calendar 2019 senza match DB 2019;
- Event DB 2019 senza copertura Calendar;
- conflitti in cui piu righe Calendar puntavano allo stesso Event con date diverse.

Esito dell'applicazione:

| Controllo | Conteggio |
|---|---:|
| Conflitti stesso Event/date diverse risolti | 8 |
| Calendar entries create dai conflitti MAG/WAG o multi-data | 16 |
| Coppie Calendar/Event applicate dalla review corrente | 14 |
| Calendar entries aggiornate dalla review corrente | 14 |
| Righe Calendar chiuse come `calendar_only` | 2 |
| Date canoniche Event preservate e non sovrascritte | 2 |
| Elementi review ancora aperti | 0 |
| Decisioni invalide | 0 |
| Collegamenti cross-year finali | 0 |

Durante la verifica e stata rafforzata una regola semantica: se un Event ha gia una data canonica valida e una riga Calendar aggiuntiva rappresenta un sotto-caso dello stesso evento, il sistema non sovrascrive `Event.start_date` / `Event.end_date`. In questi casi conserva la data principale dell'Event e usa `EventCalendarEntry` per la riga calendario aggiuntiva.

I due casi verificati nel 2019 sono:

| Event DB | Data canonica preservata | Riga Calendar aggiuntiva |
|---|---|---|
| `Russian Junior Championships` | May 13-18 | `Russian Junior Men's Championships`, May 6-11 |
| `1st Spanish League` | Feb 8-10 | `1st Spanish League (2020 season)`, Dec 7-8 |

Il controllo finale 2019 conferma:

| Controllo | Conteggio |
|---|---:|
| Righe Calendar 2019 | 244 |
| Event DB 2019 | 233 |
| Event DB 2019 coperti dal Calendar | 233 |
| Event DB 2019 senza copertura Calendar | 0 |
| Righe Calendar 2019 ancora da risolvere | 0 |
| Righe Calendar 2019 `calendar_only` senza scheda Event | 2 |
| Collegamenti cross-year finali | 0 |

Le due righe Calendar chiuse come `calendar_only`, quindi visualizzabili nel calendario ma non cliccabili verso una scheda Event DB, sono:

| Riga Calendar | Evento | Data | Esito |
|---:|---|---|---|
| 60 | `Zelena Jama Open` | Apr 6 | Nessun match DB 2019 confermato; non trovato in `Results 2019.xlsx`; possibile evento non svolto o senza risultati sorgente |
| 211 | `Brazilian Junior Championships` | Nov 5-10 | Nessun match DB 2019 confermato; non trovato in `Results 2019.xlsx`; possibile evento non svolto o senza risultati sorgente |

Nota metodologica: da questo passaggio in poi, la chiusura di un anno calendario non richiede che ogni riga Calendar abbia un Event DB collegato. Alcune gare presenti nel calendario possono non comparire negli Event ricavati dai Result perche potrebbero non essere state svolte, oppure perche non esiste un risultato Gymternet sorgente associato. La metrica critica e quindi che tutti gli Event DB creati dai Result abbiano una copertura Calendar oppure, se il Calendar sorgente non contiene la gara, una review esplicita admin; le righe Calendar senza Result possono restare come `calendar_only`. Il file `Results 2019.xlsx` e stato controllato direttamente: contiene risultati per `Hungarian Masters`, che e stato associato all'Event DB `Hungarian Masters`, ma non contiene risultati riconducibili a `Zelena Jama Open` o `Brazilian Junior Championships`.

### Calendar 2020

Il flusso Calendar 2020 e stato avviato dopo la chiusura metodologica del 2019. La regola di successo applicata e: tutti gli Event DB creati dai Result devono avere copertura Calendar oppure una review esplicita admin se il Calendar sorgente non contiene la gara; le righe Calendar senza Result possono restare come `calendar_only`.

Situazione iniziale:

| Controllo | Conteggio |
|---|---:|
| Righe Calendar 2020 | 90 |
| Event DB 2020 ricavati dai Result | 77 |
| Righe Calendar 2020 con match automatico | 74 |
| Righe Calendar 2020 senza match automatico | 16 |
| Event DB 2020 con match automatico | 71 |
| Event DB 2020 senza match automatico | 6 |
| Event DB 2020 senza match automatico con result | 6 |
| Event DB 2020 matched da piu righe Calendar | 3 |
| Conflitti stesso Event/date diverse | 3 |
| Duplicate source rows | 0 |

Primo commit sicuro 2020:

| Controllo | Conteggio |
|---|---:|
| Righe dirette sicure applicate | 68 |
| Event aggiornati con `start_date` / `end_date` | 68 |
| Righe saltate per conflitto stesso Event/date diverse | 6 |
| Elementi review ancora aperti | 19 |
| Decisioni invalide | 0 |

Backup locale creato automaticamente:

```text
backups/leverage_calendar_2020_20260701_224922.db
```

Fotografia post-commit sicuro:

| Controllo | Conteggio |
|---|---:|
| Calendar 2020 senza match corrente | 16 |
| Event DB 2020 senza match corrente | 6 |
| Event DB 2020 gia coperti | 71 |
| Righe Calendar 2020 `calendar_only` | 0 |
| Collegamenti cross-year rilevati | 0 |

File preparati per la review admin 2020:

- `calendar_2020_calendar_unmatched_current.csv`
- `calendar_2020_db_unmatched_current.csv`
- `calendar_2020_source_conflicts_slim.csv`

Nota metodologica: le righe Calendar senza Event DB non sono automaticamente errori. Durante la review verranno collegate a un Event DB solo se rappresentano effettivamente risultati presenti in LEVERAGE; in caso contrario verranno chiuse come `calendar_only`.

Review admin corrente 2020:

Le decisioni admin sono state lette dai file Numbers e riportate nei CSV operativi. Nel file `calendar_2020_calendar_unmatched_current.csv`, la decisione `No one` e stata normalizzata in `calendar_only`. Nel file `calendar_2020_db_unmatched_current.csv`, la scelta testuale `Unisport Norges Cup` e stata interpretata come riferimento alla riga Calendar 26.

Esito dell'applicazione:

| Controllo | Conteggio |
|---|---:|
| Conflitti stesso Event/date diverse risolti | 3 |
| Calendar entries create dai conflitti multi-data | 5 |
| Coppie Calendar/Event applicate dalla review corrente | 15 |
| Calendar entries create dalla review corrente | 15 |
| Righe Calendar chiuse come `calendar_only` | 2 |
| Event aggiornati con date dalla review corrente | 5 |
| Date canoniche Event preservate e non sovrascritte | 7 |
| Elementi review ancora aperti | 0 |
| Decisioni invalide | 0 |

Durante la review 2020 e stato corretto un caso di stagione a cavallo d'anno: `1st Spanish League (2020 season)` e un Event DB con `Event.year=2020`, ma la riga Calendar corrispondente e nel foglio 2019, riga 242, con data Dec 7-8 2019. Il collegamento precedentemente associato all'Event 2019 `1st Spanish League` e stato rilinkato all'Event 2020 corretto e marcato con `season_year_spillover`.

Esito finale 2020:

| Controllo | Conteggio |
|---|---:|
| Righe Calendar 2020 | 90 |
| Event DB 2020 | 77 |
| Event DB 2020 coperti dal Calendar | 77 |
| Event DB 2020 senza copertura Calendar | 0 |
| Righe Calendar 2020 ancora da risolvere | 0 |
| Righe Calendar 2020 `calendar_only` senza scheda Event | 2 |
| Collegamenti `season_year_spillover` | 1 |
| Collegamenti cross-year non controllati | 0 |

Le due righe Calendar 2020 chiuse come `calendar_only` sono:

| Riga Calendar | Evento | Data | Esito |
|---:|---|---|---|
| 42 | `Stella Zakharova Cup` | Sep 26-27 | Nessun Result DB 2020 collegato; possibile evento non svolto o senza risultati sorgente |
| 79 | `Hungarian Master Championships` | Nov 13-15 | Nessun Result DB 2020 collegato; possibile evento non svolto o senza risultati sorgente |

Nota metodologica: `season_year_spillover` e una eccezione controllata, non un errore cross-year. Si usa quando l'Event DB appartiene a una stagione/anno dati diverso dal foglio Calendar in cui cade la data reale dell'evento.

### Calendar 2021

Il flusso Calendar 2021 e stato avviato con la stessa metodologia consolidata per 2018-2020: prima applicazione automatica solo dei match sicuri, poi preparazione di file CSV snelli per la review admin dei casi non risolti. La regola guida resta che tutti gli Event DB creati dai Result devono ottenere copertura Calendar oppure una review esplicita admin come `db_only` se il Calendar sorgente non contiene la gara, mentre le righe Calendar prive di Result possono essere chiuse come `calendar_only` se rappresentano eventi non svolti o privi di risultati sorgente.

Fotografia iniziale 2021:

| Controllo | Conteggio |
|---|---:|
| Righe Calendar 2021 | 210 |
| Event DB 2021 | 196 |
| Righe Calendar 2021 con match automatico | 181 |
| Righe Calendar 2021 senza match automatico | 29 |
| Event DB 2021 matched automaticamente | 172 |
| Event DB 2021 senza match automatico con result | 24 |
| Event DB 2021 matched da piu righe Calendar | 9 |
| Conflitti stesso Event/date diverse | 9 |
| Duplicate source rows | 0 |

Primo commit sicuro 2021:

| Controllo | Conteggio |
|---|---:|
| Righe dirette sicure applicate | 163 |
| Event aggiornati con `start_date` / `end_date` | 163 |
| Righe saltate per conflitto stesso Event/date diverse | 18 |
| Elementi review ancora aperti | 38 |
| Decisioni invalide | 0 |

Backup locale creato automaticamente:

```text
backups/leverage_calendar_2021_20260701_232721.db
```

Fotografia post-commit sicuro:

| Controllo | Conteggio |
|---|---:|
| Calendar 2021 senza match corrente | 29 |
| Event DB 2021 senza match corrente | 24 |
| Event DB 2021 gia coperti | 172 |
| Righe Calendar 2021 `calendar_only` | 0 |
| Collegamenti `season_year_spillover` | 0 |
| Collegamenti cross-year rilevati | 0 |

File preparati per la review admin 2021:

- `calendar_2021_calendar_unmatched_current.csv`
- `calendar_2021_db_unmatched_current.csv`
- `calendar_2021_source_conflicts_slim.csv`

Nota operativa: i tre file restano volutamente snelli. Nel primo si decide se una riga Calendar va collegata a un Event DB suggerito oppure chiusa come `calendar_only`; nel secondo si collega un Event DB ancora senza data alla riga Calendar corretta; nel terzo si risolve il caso in cui lo stesso Event DB puo essere rappresentato da piu righe Calendar, spesso per differenze MAG/WAG o giornate multiple.

Review admin corrente 2021:

Le decisioni admin sono state lette dai file Numbers e riportate nei CSV operativi. Durante questa review e emersa una nuova eccezione metodologica: alcuni Event DB ricavati dai Result possono non comparire nel Calendar sorgente. In questi casi non bisogna forzare un match artificiale; l'Event va marcato come `db_only` dopo verifica admin, mantenendo traccia del motivo.

Normalizzazioni applicate:

- `No one.` nel file Calendar-unmatched e stato normalizzato in `calendar_only`;
- `No one.` nel file DB-unmatched e stato normalizzato in `db_only`;
- le righe Calendar 24 e 61 dei British Olympic Trials sono state marcate come `linked_by_db_review`, perche rappresentano righe calendario aggregate collegate a piu Event DB distinti tramite il file DB-unmatched;
- le scelte multi-riga `1 and 2` e simili sono state conservate per creare `EventCalendarEntry` multipli senza comprimere date diverse dentro un solo intervallo canonico Event.

Esito dell'applicazione dei mismatch correnti:

| Controllo | Conteggio |
|---|---:|
| Coppie Calendar/Event applicate dalla review corrente | 37 |
| Event aggiornati con date dalla review corrente | 25 |
| Calendar entries create dalla review corrente | 37 |
| Righe Calendar chiuse come `calendar_only` | 1 |
| Event DB marcati come `db_only` | 1 |
| Date canoniche Event preservate e non sovrascritte | 12 |
| Elementi review ancora aperti | 0 |
| Decisioni invalide | 0 |

Backup locale creato automaticamente:

```text
backups/leverage_calendar_current_review_2021_20260701_220954.db
```

Esito dei conflitti stesso Event/date diverse:

| Controllo | Conteggio |
|---|---:|
| Conflitti stesso Event/date risolti | 9 |
| Calendar entries create dai conflitti multi-data | 18 |
| Decisioni invalide | 0 |

Backup locale creato automaticamente:

```text
backups/leverage_calendar_2021_20260702_001020.db
```

Esito finale 2021:

| Controllo | Conteggio |
|---|---:|
| Righe Calendar 2021 | 210 |
| Event DB 2021 | 196 |
| Event DB 2021 coperti o verificati | 196 |
| Event DB 2021 senza copertura/review Calendar | 0 |
| Righe Calendar 2021 ancora da risolvere | 0 |
| Righe Calendar 2021 `calendar_only` senza scheda Event | 1 |
| Event DB 2021 `db_only` assenti dal Calendar sorgente | 1 |
| Collegamenti `season_year_spillover` | 0 |
| Collegamenti cross-year non controllati | 0 |

La riga Calendar 2021 chiusa come `calendar_only` e:

| Riga Calendar | Evento | Data | Esito |
|---:|---|---|---|
| 66 | `Oceania Championships` | May 21 | Nessun Event DB 2021 collegato; voce Calendar mantenuta senza scheda Event collegata |

L'Event DB 2021 chiuso come `db_only` e:

| Event ID | Evento | Discipline | Result | Esito |
|---:|---|---|---:|---|
| 691 | `RomGym Trophy` | WAG | 16 | Event ricavato dai Result ma assente dal Calendar sorgente; non viene forzato un match Calendar artificiale |

Nota metodologica: da questo punto in avanti la qualita della riconciliazione Calendar non richiede che ogni Event DB abbia per forza una riga Calendar. Richiede invece che ogni Event DB sia o collegato a una riga Calendar, oppure marcato esplicitamente come `db_only` dopo verifica admin. Questa regola evita di creare date o collegamenti non supportati dal file Calendar sorgente.

### Calendar 2022

Il flusso Calendar 2022 e stato avviato applicando la metodologia aggiornata dopo la chiusura 2021: ogni Event DB ricavato dai Result deve essere collegato al Calendar quando esiste una riga sorgente affidabile; se invece il Calendar non contiene la gara, l'Event puo essere chiuso solo dopo review admin come `db_only`. Le righe Calendar prive di Result possono restare come `calendar_only`.

Fotografia iniziale 2022:

| Controllo | Conteggio |
|---|---:|
| Righe Calendar 2022 | 228 |
| Event DB 2022 | 215 |
| Righe Calendar 2022 con match automatico | 216 |
| Righe Calendar 2022 senza match automatico | 12 |
| Event DB 2022 matched automaticamente | 209 |
| Event DB 2022 senza match automatico con result | 6 |
| Event DB 2022 matched da piu righe Calendar | 7 |
| Conflitti stesso Event/date diverse | 7 |
| Duplicate source rows | 0 |

Primo commit sicuro 2022:

| Controllo | Conteggio |
|---|---:|
| Righe dirette sicure applicate | 202 |
| Event aggiornati con `start_date` / `end_date` | 202 |
| Righe saltate per conflitto stesso Event/date diverse | 14 |
| Elementi review ancora aperti | 19 |
| Decisioni invalide | 0 |

Backup locale creato automaticamente:

```text
backups/leverage_calendar_2022_20260702_001613.db
```

Fotografia post-commit sicuro:

| Controllo | Conteggio |
|---|---:|
| Calendar 2022 senza match corrente | 12 |
| Event DB 2022 senza match corrente | 6 |
| Event DB 2022 gia coperti | 209 |
| Event DB 2022 `db_only` gia verificati | 0 |
| Righe Calendar 2022 `calendar_only` | 0 |
| Collegamenti `season_year_spillover` | 0 |
| Collegamenti cross-year rilevati | 0 |

File preparati per la review admin 2022:

- `calendar_2022_calendar_unmatched_current.csv`
- `calendar_2022_db_unmatched_current.csv`
- `calendar_2022_source_conflicts_slim.csv`

Nota operativa: il 2022 contiene pochi casi aperti. Nel file Calendar-unmatched restano soprattutto gare MAG con denominazione maschile esplicita; nel file DB-unmatched sono presenti possibili refusi/varianti come `Bundlesiga` e gare che potrebbero richiedere associazione manuale o `db_only`; nel file source-conflicts restano casi MAG/WAG o serie Bundesliga con piu righe Calendar corrette per lo stesso Event.

Review admin corrente 2022:

Le decisioni admin sono state lette dai file Numbers e riportate nei CSV operativi. Il caso `EYOF Mixed Pairs` e stato indicato testualmente come `European Youth Olympic Festival`; la scelta e stata normalizzata manualmente sulla riga Calendar 142 (`European Youth Olympic Festival`, Jul 24-30).

Esito dell'applicazione dei mismatch correnti:

| Controllo | Conteggio |
|---|---:|
| Coppie Calendar/Event applicate dalla review corrente | 13 |
| Event aggiornati con date dalla review corrente | 9 |
| Calendar entries create dalla review corrente | 13 |
| Righe Calendar chiuse come `calendar_only` | 0 |
| Event DB marcati come `db_only` | 0 |
| Date canoniche Event preservate e non sovrascritte | 4 |
| Elementi review ancora aperti | 0 |
| Decisioni invalide | 0 |

Backup locale creato automaticamente:

```text
backups/leverage_calendar_current_review_2022_20260701_223227.db
```

Esito dei conflitti stesso Event/date diverse:

| Controllo | Conteggio |
|---|---:|
| Conflitti stesso Event/date risolti | 7 |
| Calendar entries create dai conflitti multi-data | 14 |
| Decisioni invalide | 0 |

Backup locale creato automaticamente:

```text
backups/leverage_calendar_2022_20260702_003257.db
```

Esito finale 2022:

| Controllo | Conteggio |
|---|---:|
| Righe Calendar 2022 | 228 |
| Event DB 2022 | 215 |
| Event DB 2022 coperti o verificati | 215 |
| Event DB 2022 senza copertura/review Calendar | 0 |
| Righe Calendar 2022 ancora da risolvere | 0 |
| Righe Calendar 2022 `calendar_only` senza scheda Event | 0 |
| Event DB 2022 `db_only` assenti dal Calendar sorgente | 0 |
| Collegamenti `season_year_spillover` | 1 |
| Collegamenti cross-year non controllati | 0 |

Nota metodologica: il 2022 non ha richiesto eccezioni `calendar_only` o `db_only`. Tutti gli Event DB 2022 risultano collegati a righe Calendar sorgente, con i conflitti MAG/WAG e Bundesliga preservati tramite `EventCalendarEntry` quando erano presenti piu date corrette.

Aggiornamento successivo durante la review 2023: la riga Calendar 2022 n. 205, `1st Spanish League – 2023 season`, e stata rilinkata dall'Event 2022 `1st Spanish League` all'Event 2023 `1st Spanish League 2023`. Questa correzione e marcata come `season_year_spillover`, perche la data reale e nel Calendar 2022 ma l'Event DB appartiene alla stagione/anno evento 2023. La copertura 2022 resta completa.

### Calendar 2023

Il flusso Calendar 2023 e stato avviato con la stessa metodologia consolidata: applicazione automatica dei soli match sicuri, mantenimento in review dei casi con ambiguita, e uso di `EventCalendarEntry` per piu date corrette riferite allo stesso Event. Il 2023 contiene anche alcune righe di calendario riferite alla stagione 2024 ma datate nel 2023; queste righe vengono lasciate alla review admin e non trattate automaticamente come errore.

Fotografia iniziale 2023:

| Controllo | Conteggio |
|---|---:|
| Righe Calendar 2023 | 265 |
| Event DB 2023 | 241 |
| Righe Calendar 2023 con match automatico | 226 |
| Righe Calendar 2023 senza match automatico | 39 |
| Righe Calendar 2023 con piu possibili Event DB | 3 |
| Event DB 2023 matched automaticamente | 223 |
| Event DB 2023 senza match automatico con result | 18 |
| Event DB 2023 matched da piu righe Calendar | 6 |
| Conflitti stesso Event/date diverse | 6 |
| Duplicate source rows | 0 |

Primo commit sicuro 2023:

| Controllo | Conteggio |
|---|---:|
| Righe dirette sicure applicate | 211 |
| Event aggiornati con `start_date` / `end_date` | 211 |
| Righe saltate per conflitto stesso Event/date diverse | 12 |
| Righe saltate per piu match possibili | 3 |
| Elementi review ancora aperti | 45 |
| Decisioni invalide | 0 |

Backup locale creato automaticamente:

```text
backups/leverage_calendar_2023_20260702_003617.db
```

Fotografia post-commit sicuro:

| Controllo | Conteggio |
|---|---:|
| Calendar 2023 senza match corrente | 39 |
| Event DB 2023 senza match corrente | 18 |
| Event DB 2023 gia coperti | 223 |
| Event DB 2023 `db_only` gia verificati | 0 |
| Righe Calendar 2023 `calendar_only` | 0 |
| Collegamenti `season_year_spillover` | 0 |
| Collegamenti cross-year rilevati | 0 |

File preparati per la review admin 2023:

- `calendar_2023_calendar_unmatched_current.csv`
- `calendar_2023_db_unmatched_current.csv`
- `calendar_2023_source_conflicts_slim.csv`

Nota operativa: nella review 2023 compaiono righe come `Top 12 Series 1 (2024 season)`, `Top 12 Series 2 (2024 season)`, `Top 12 Series 3 (2024 season)` e `1st Spanish League (2024 season)`. La scelta corretta deve essere verificata dall'admin come per i precedenti casi di stagione a cavallo d'anno: se la riga Calendar e la scheda Event rappresentano la stessa competizione, si collega; se invece non esiste un collegamento supportato dai dati sorgente, si usa `calendar_only` o `db_only` secondo il lato mancante.

Pulizia sorgente Calendar 2023:

Dopo il primo checkpoint 2023, e stata corretta la sorgente `Calendar.xlsx` per rimuovere URL rimasti dentro il testo visibile di alcune gare. La correzione ha riguardato solo il foglio 2023 e non ha modificato date, numero di righe o altri fogli. Le righe ripulite sono legate ai `Finnish National Team Test` / `Finnish Men's National Team Test`. I report 2023 sono stati rigenerati dopo la pulizia: i conteggi di matching sono rimasti invariati, ma i nomi gara nei CSV operativi risultano ora leggibili e privi di URL.

Review admin corrente 2023:

Le decisioni admin sono state lette dai file Numbers e riportate nei CSV operativi. Per `calendar_2023_calendar_unmatched_current` e stato usato il file compilato dopo la pulizia della sorgente, denominato `calendar_2023_calendar_unmatched_current 2.numbers`.

Normalizzazioni e decisioni applicate:

- `No one.` nelle righe Calendar e stato normalizzato in `calendar_only`;
- `No one.` negli Event DB e stato normalizzato in `db_only`;
- `EYOF Mixed Pairs` e stato collegato alla riga Calendar 151, `European Youth Olympic Festival`;
- `1st Spanish League 2023` e stato collegato alla riga Calendar 2022 n. 205 come `season_year_spillover`;
- le righe 2023 riferite alla stagione 2024 sono state collegate agli Event DB 2024 quando presenti;
- `Top 12 Series 3 (MAG) (2024 season)` e stata chiusa come `calendar_only`, perche non e stato trovato un Event DB 2024 MAG corrispondente.

Riparazione cross-year/spillover:

| Riga Calendar | Foglio Calendar | Evento Calendar | Event DB collegato | Esito |
|---:|---:|---|---|---|
| 205 | 2022 | `1st Spanish League – 2023 season` | `1st Spanish League 2023` | Entry rilinkata dall'Event 888 all'Event 887 e marcata `season_year_spillover` |

Esito dell'applicazione dei mismatch correnti:

| Controllo | Conteggio |
|---|---:|
| Coppie Calendar/Event applicate dalla review corrente | 30 |
| Event aggiornati con date dalla review corrente | 20 |
| Calendar entries create dalla review corrente | 30 |
| Righe Calendar chiuse come `calendar_only` | 13 |
| Event DB marcati come `db_only` | 1 |
| Date canoniche Event preservate e non sovrascritte | 10 |
| Elementi review ancora aperti | 0 |
| Decisioni invalide | 0 |

Backup locali creati automaticamente:

```text
backups/leverage_calendar_2023_spillover_repair_20260701_231737.db
backups/leverage_calendar_current_review_2023_20260701_231759.db
```

Esito dei conflitti stesso Event/date diverse:

| Controllo | Conteggio |
|---|---:|
| Conflitti stesso Event/date risolti | 6 |
| Calendar entries create dai conflitti multi-data | 12 |
| Decisioni invalide | 0 |

Backup locale creato automaticamente:

```text
backups/leverage_calendar_2023_20260702_011813.db
```

Collegamenti `season_year_spillover` rilevanti:

| Foglio Calendar | Riga | Evento Calendar | Event DB | Event year |
|---:|---:|---|---|---:|
| 2022 | 205 | `1st Spanish League – 2023 season` | `1st Spanish League 2023` | 2023 |
| 2023 | 239 | `Top 12 Series 1 (2024 season)` | `Top 12 Series 1 (2024 Season)` | 2024 |
| 2023 | 245 | `Top 12 Series 1 (MAG) (2024 season)` | `Top 12 Series 1 (2024 Season)` | 2024 |
| 2023 | 252 | `Top 12 Series 2 (2024 season)` | `Top 12 Series 2 (2024 Season)` | 2024 |
| 2023 | 260 | `Top 12 Series 2 (MAG) (2024 season)` | `Top 12 Series 2 (2024 Season)` | 2024 |
| 2023 | 261 | `1st Spanish League (2024 season)` | `1st Spanish League (2024 season)` | 2024 |
| 2023 | 263 | `Top 12 Series 3 (2024 season)` | `Top 12 Series 3 (2024 Season)` | 2024 |

Esito finale 2023:

| Controllo | Conteggio |
|---|---:|
| Righe Calendar 2023 | 265 |
| Event DB 2023 | 241 |
| Event DB 2023 coperti o verificati | 241 |
| Event DB 2023 senza copertura/review Calendar | 0 |
| Righe Calendar 2023 ancora da risolvere | 0 |
| Righe Calendar 2023 `calendar_only` senza scheda Event | 13 |
| Event DB 2023 `db_only` assenti dal Calendar sorgente | 1 |
| Collegamenti `season_year_spillover` | 7 |
| Collegamenti cross-year non controllati | 0 |

L'Event DB 2023 chiuso come `db_only` e `German Worlds Trials 2`. Le righe `calendar_only` 2023 sono principalmente test nazionali finlandesi senza Event DB collegato, oltre a `Austrian Junior Championships`, `Hungarian Junior Men's Championships` e `Top 12 Series 3 (MAG) (2024 season)`.

### Calendar 2024

Il flusso Calendar 2024 e stato avviato tenendo conto dei collegamenti `season_year_spillover` gia creati durante la review 2023. Sei Event DB 2024 risultano infatti gia coperti da righe Calendar del foglio 2023, perche riferiti a competizioni di stagione 2024 disputate in date 2023.

Fotografia iniziale 2024:

| Controllo | Conteggio |
|---|---:|
| Righe Calendar 2024 | 222 |
| Event DB 2024 | 207 |
| Righe Calendar 2024 con match automatico | 204 |
| Righe Calendar 2024 senza match automatico | 18 |
| Event DB 2024 matched automaticamente | 197 |
| Event DB 2024 senza match automatico con result | 10 |
| Event DB 2024 matched da piu righe Calendar | 7 |
| Conflitti stesso Event/date diverse | 6 |
| Duplicate source rows | 0 |

Primo commit sicuro 2024:

| Controllo | Conteggio |
|---|---:|
| Righe dirette sicure applicate | 192 |
| Event aggiornati con `start_date` / `end_date` | 191 |
| Event gia coerenti con la data sorgente | 1 |
| Righe saltate per conflitto stesso Event/date diverse | 12 |
| Elementi review ancora aperti | 24 |
| Decisioni invalide | 0 |

Backup locale creato automaticamente:

```text
backups/leverage_calendar_2024_20260702_012421.db
```

Fotografia post-commit sicuro:

| Controllo | Conteggio |
|---|---:|
| Calendar 2024 senza match corrente | 18 |
| Event DB 2024 senza match corrente | 9 |
| Event DB 2024 gia coperti | 198 |
| Event DB 2024 `db_only` gia verificati | 0 |
| Righe Calendar 2024 `calendar_only` | 0 |
| Collegamenti `season_year_spillover` | 6 |
| Collegamenti cross-year rilevati | 0 |

File preparati per la review admin 2024:

- `calendar_2024_calendar_unmatched_current.csv`
- `calendar_2024_db_unmatched_current.csv`
- `calendar_2024_source_conflicts_slim.csv`

Nota operativa: nel 2024 restano da verificare alcune righe Calendar senza Event DB evidente, come `European Gymnastics Online Series`, gare MAG nazionali e amichevoli junior, oltre a 9 Event DB non ancora collegati. I conflitti source riguardano soprattutto Top 12 e Bundesliga, quindi vanno gestiti con la stessa logica multi-data gia usata negli anni precedenti.

Review admin corrente 2024:

Le decisioni admin sono state lette dai file Numbers e riportate nei CSV operativi. Per `calendar_2024_calendar_unmatched_current` e `calendar_2024_source_conflicts_slim` sono stati usati i file compilati con suffisso `2.numbers`.

Normalizzazioni applicate:

- `No one.` nelle righe Calendar e stato normalizzato in `calendar_only`;
- le righe DB-unmatched sono state tutte collegate tramite scelta numerica;
- i conflitti same Event/date sono stati risolti con scelte multiple `1 and 2`, creando `EventCalendarEntry` multipli.

Esito dell'applicazione dei mismatch correnti:

| Controllo | Conteggio |
|---|---:|
| Coppie Calendar/Event applicate dalla review corrente | 18 |
| Event aggiornati con date dalla review corrente | 9 |
| Calendar entries create dalla review corrente | 18 |
| Righe Calendar chiuse come `calendar_only` | 2 |
| Event DB marcati come `db_only` | 0 |
| Date canoniche Event preservate e non sovrascritte | 9 |
| Elementi review ancora aperti | 0 |
| Decisioni invalide | 0 |

Backup locale creato automaticamente:

```text
backups/leverage_calendar_current_review_2024_20260702_060927.db
```

Esito dei conflitti stesso Event/date diverse:

| Controllo | Conteggio |
|---|---:|
| Conflitti stesso Event/date risolti | 6 |
| Calendar entries create dai conflitti multi-data | 12 |
| Decisioni invalide | 0 |

Backup locale creato automaticamente:

```text
backups/leverage_calendar_2024_20260702_080943.db
```

Esito finale 2024:

| Controllo | Conteggio |
|---|---:|
| Righe Calendar 2024 | 222 |
| Event DB 2024 | 207 |
| Event DB 2024 coperti o verificati | 207 |
| Event DB 2024 senza copertura/review Calendar | 0 |
| Righe Calendar 2024 ancora da risolvere | 0 |
| Righe Calendar 2024 `calendar_only` senza scheda Event | 2 |
| Event DB 2024 `db_only` assenti dal Calendar sorgente | 0 |
| Collegamenti `season_year_spillover` | 6 |
| Collegamenti cross-year non controllati | 0 |

Le righe Calendar 2024 chiuse come `calendar_only` sono:

| Riga Calendar | Evento | Data | Esito |
|---:|---|---|---|
| 137 | `Israeli Championships` | Jun 28-Jul 8 | Nessun Event DB 2024 collegato; voce Calendar mantenuta senza scheda Event collegata |
| 150 | `Japanese National Sports Festival` | Sep 5-8 | Nessun Event DB 2024 collegato; voce Calendar mantenuta senza scheda Event collegata |

Nota metodologica: il 2024 si chiude senza Event DB `db_only`. Tutti gli Event DB 2024 risultano coperti da righe Calendar dello stesso foglio oppure dai collegamenti `season_year_spillover` gia creati durante la review 2023.

### Calendar 2025

Il flusso Calendar 2025 e stato avviato con la stessa metodologia applicata agli anni precedenti: matching same-year strict, normalizzazione semantica MAG/WAG, applicazione automatica solo delle date sicure e mantenimento in review delle righe ambigue o conflittuali.

Fotografia iniziale 2025:

| Controllo | Conteggio |
|---|---:|
| Righe Calendar 2025 | 227 |
| Event DB 2025 | 224 |
| Righe Calendar 2025 con match automatico | 214 |
| Righe Calendar 2025 senza match automatico | 13 |
| Event DB 2025 matched automaticamente | 211 |
| Event DB 2025 senza match automatico con result | 13 |
| Event DB 2025 matched da piu righe Calendar | 7 |
| Conflitti stesso Event/date diverse | 7 |
| Duplicate source rows | 1 |
| Delta Calendar unmatched - DB unmatched | 0 |

Primo commit sicuro 2025:

| Controllo | Conteggio |
|---|---:|
| Righe dirette sicure applicate | 200 |
| Event aggiornati con `start_date` / `end_date` | 200 |
| Event gia coerenti con la data sorgente | 0 |
| Righe saltate per conflitto stesso Event/date diverse | 12 |
| Righe saltate per match multiplo | 2 |
| Elementi review ancora aperti | 20 |
| Decisioni invalide | 0 |

Backup locale creato automaticamente:

```text
backups/leverage_calendar_2025_20260702_081522.db
```

Fotografia post-commit sicuro:

| Controllo | Conteggio |
|---|---:|
| Calendar 2025 senza match corrente | 13 |
| Event DB 2025 senza match corrente | 13 |
| Event DB 2025 gia coperti | 211 |
| Event DB 2025 `db_only` gia verificati | 0 |
| Righe Calendar 2025 `calendar_only` | 0 |
| Collegamenti `season_year_spillover` | 0 |
| Collegamenti cross-year rilevati | 0 |
| Source issues | 0 |

File preparati per la review admin 2025:

- `calendar_2025_calendar_unmatched_current.csv`
- `calendar_2025_db_unmatched_current.csv`
- `calendar_2025_source_conflicts_slim.csv`

Nota operativa: il 2025 resta in review su 13 righe Calendar senza match corrente, 13 Event DB senza match corrente e 7 conflitti stesso Event/date diverse. Il file sorgente contiene anche 1 duplicate source row da controllare nel flusso di review. Al momento non risultano righe `calendar_only`, Event DB `db_only`, collegamenti `season_year_spillover` o cross-year gia verificati.

Review admin corrente 2025:

Le decisioni admin sono state lette dai tre file Numbers e riportate nei CSV operativi tramite lo script:

```text
scripts/apply_calendar_numbers_decisions.py
```

Normalizzazioni applicate:

- le 13 righe Calendar-unmatched sono state collegate tramite scelta numerica;
- `No one.` nell'Event DB `Dutch Worlds Trials 3` e stato normalizzato in `db_only`;
- `EYOF Mixed Pairs` e stato indicato testualmente come `European Youth Olympic Festival` e normalizzato sulla riga Calendar 144 (`European Youth Olympic Festival`, Jul 20-26);
- `Top 12 Series 3 (2025)` e stato indicato con nota `See the 2024 calendar`: il caso e stato gestito come `season_year_spillover`, collegando la riga Calendar 2024 n. 219 (`Top 12 Series 3 (MAG)`, Dec 7) all'Event DB 2025 ID 1219.

Per lo spillover `Top 12 Series 3 (2025)` e stato aggiunto e usato lo script:

```text
scripts/link_calendar_spillover_entry.py
```

Backup locale creato automaticamente per lo spillover:

```text
backups/leverage_calendar_spillover_2024_1219_20260702_063816.db
```

Esito dell'applicazione dei mismatch correnti:

| Controllo | Conteggio |
|---|---:|
| Coppie Calendar/Event applicate dalla review corrente | 20 |
| Event aggiornati con date dalla review corrente | 12 |
| Calendar entries create dalla review corrente | 20 |
| Righe Calendar chiuse come `calendar_only` | 0 |
| Event DB marcati come `db_only` | 1 |
| Date canoniche Event preservate e non sovrascritte | 8 |
| Elementi review ancora aperti | 0 |
| Decisioni invalide | 0 |

Backup locale creato automaticamente:

```text
backups/leverage_calendar_current_review_2025_20260702_063831.db
```

Esito dei conflitti stesso Event/date diverse:

| Controllo | Conteggio |
|---|---:|
| Conflitti stesso Event/date risolti | 6 |
| Calendar entries create dai conflitti multi-data | 11 |
| Calendar entries aggiornate dai conflitti multi-data | 13 |
| Event aggiornati dai conflitti source/date | 9 |
| Decisioni invalide | 0 |

Backup locale creato automaticamente:

```text
backups/leverage_calendar_2025_20260702_083911.db
```

Esito finale 2025:

| Controllo | Conteggio |
|---|---:|
| Righe Calendar 2025 | 227 |
| Event DB 2025 | 224 |
| Event DB 2025 coperti o verificati | 224 |
| Event DB 2025 senza copertura/review Calendar | 0 |
| Righe Calendar 2025 ancora da risolvere | 0 |
| Righe Calendar 2025 `calendar_only` senza scheda Event | 0 |
| Event DB 2025 `db_only` assenti dal Calendar sorgente | 1 |
| Collegamenti `season_year_spillover` | 1 |
| Collegamenti cross-year non controllati | 0 |
| Source issues | 0 |

L'Event DB 2025 chiuso come `db_only` e:

| Event ID | Evento | Disciplina | Note |
|---:|---|---|---|
| 1538 | `Dutch Worlds Trials 3` | MAG | Nessuna riga Calendar 2025 corrispondente confermata dall'admin |

Regola semantica UI confermata durante la review 2025: per gli Event storici con disciplina `MAG and WAG`, l'interfaccia utente non deve mostrare un pulsante autonomo `MAG and WAG` per filtrare i Result. Deve invece mostrare i pulsanti realmente cliccabili `MAG` e/o `WAG` quando esistono Result con quei valori. La scheda Event puo restare `MAG and WAG` come contenitore semantico, ma classifiche, grafici e filtri devono lavorare sul campo `Result.discipline`, cosi l'utente puo visualizzare separatamente risultati maschili e femminili.

Regole metodologiche persistenti aggiunte dopo la chiusura Calendar 2025:

- `EYOF` significa sempre `European Youth Olympic Festival`. Nei futuri match Calendar/Event e negli import, il sistema deve espandere semanticamente questa abbreviazione prima di trattarla come mismatch.
- Gli Event `Top 12` possono appartenere alla stessa stagione sportiva pur cadendo a cavallo tra due fogli calendario/anni diversi. Questo non e automaticamente un errore: va gestito con collegamenti espliciti `EventCalendarEntry` e note `season_year_spillover`, senza forzare tutte le date dentro l'anno nominale dell'Event DB.

## 16. Milestone - Chiusura blocco storico 2018-2025

Data milestone: 2 luglio 2026

Stato raggiunto: il blocco storico iniziale di LEVERAGE e stato completato per Results e Calendar dal 2018 al 2025. Il database locale contiene ora la base dati storica consolidata, verificata, documentata e versionata su GitHub.

Sintesi quantitativa del database locale alla milestone:

| Entita / controllo | Valore |
|---|---:|
| Athlete attivi | 26.259 |
| Event attivi | 1.605 |
| Result attivi | 753.723 |
| EventCalendarEntry attive | 287 |
| Event 2026 gia presenti da spillover 2025 | 1 |
| Result 2026 gia presenti da spillover 2025 | 108 |

Distribuzione Result per anno evento:

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
| 2026 | 108 |

Stato funzionale della milestone:

- popolamento Gymternet Results 2018-2025 completato;
- collisioni atleta/country/nome 2018-2025 verificate e risolte;
- regole persistenti di import e collisione salvate nel progetto;
- D-score orfani e warning storici conservati nei report;
- Calendar 2018-2025 riconciliato con gli Event DB;
- regole `calendar_only`, `db_only`, `EventCalendarEntry` e `season_year_spillover` consolidate;
- regole persistenti `EYOF = European Youth Olympic Festival` e `Top 12` a cavallo d'anno documentate;
- capitoli di tesi dedicati a popolamento Results e riconciliazione Calendar creati in Markdown e Word;
- repository GitHub aggiornato con checkpoint e commit per ogni fase rilevante.

Valutazione di avanzamento al 2 luglio 2026:

| Area | Avanzamento stimato |
|---|---:|
| Backend core e modello dati | 90% |
| Tool import Gymternet storico | 95% |
| Popolamento storico 2018-2025 | 100% |
| Riconciliazione Calendar 2018-2025 | 100% |
| Documentazione tecnica/tesi della fase dati | 90% |
| Backend pronto per UI MVP | 80% |
| Frontend/UI pubblica e admin | 0% |
| Deploy online produzione | 0% |
| MVP online complessivo | 70% |

Passo successivo sospeso: attendere il file `Results 2026` del primo semestre. Una volta ricevuto, il lavoro riprendera con preview import 2026, review conflitti, controllo duplicati rispetto ai 108 result 2026 gia presenti da `Results 2025.xlsx`, commit controllato, e successiva riconciliazione Calendar 2026.

## 17. Avvio import Results 2026 - primo semestre

Data: 14 luglio 2026

File ricevuto:

```text
/Users/patronstefano/Downloads/RESULTS/Results 2026.xlsx
```

Il file e stato copiato nel workspace locale come:

```text
import_files/Results 2026.xlsx
```

### 17.1 Controllo preliminare DB

Prima della preview 2026 il database locale conteneva gia un evento 2026 importato come spillover dal file `Results 2025.xlsx`:

| Event ID | Event | Result gia presenti |
|---:|---|---:|
| 1584 | `Top 12 Series 3 (2026)` | 108 |

Questo controllo era necessario per evitare duplicazioni durante l'import del file 2026.

### 17.2 Preview senza scrittura nel DB

E stata eseguita la preview Gymternet 2026 senza commit reale:

```text
.venv/bin/python scripts/generate_gymternet_preview_reports.py 2026 --source-dir import_files --report-dir docs/import_reports --db-path leverage.db
```

Il DB e rimasto invariato dopo la preview:

| Controllo DB | Valore |
|---|---:|
| Event 2026 | 1 |
| Result 2026 | 108 |

### 17.3 Correzione mapping country

La prima preview ha evidenziato country non ancora mappati (`Togo`, `Mali`, `DR Congo`). Prima della review admin e stato aggiornato il mapping nel backend/importer:

| Nome sorgente | Codice LEVERAGE |
|---|---|
| `Togo` | `TOG` |
| `Mali` | `MLI` |
| `DR Congo` | `COD` |
| `Democratic Republic of Congo` | `COD` |

E stato aggiunto un test di regressione a `tests/test_api.py`.

Test eseguito:

```text
.venv/bin/python -m pytest tests/test_api.py::test_gymternet_country_aliases_cover_results_files
```

Esito: passato.

### 17.4 Esito preview 2026 rigenerata

La preview rigenerata ha prodotto:

| Voce | Conteggio |
|---|---:|
| Righe parse | 66.017 |
| Result importabili | 66.016 |
| Athlete che verrebbero creati senza decisioni admin | 2.029 |
| Event che verrebbero creati | 114 |
| Duplicati identici interni al file | 1 |
| Conflitti bloccanti | 0 |
| Warning | 3 |
| D-score orfani | 287 |
| Review atleta/country | 414 |

Warning residui:

- 287 D-score non agganciati a final score;
- assegnazione automatica `day` applicata a 22 chiavi multi-day, con 44 righe valorizzate fino a `day=2`;
- import legacy successivo al 2025: vengono applicate le regole 2025+ su vault e componenti mancanti; E_score, Penalty e Bonus mancanti restano `not available`.

### 17.5 Duplicato interno al file

La preview non segnala duplicati contro il DB gia popolato. Il solo duplicato e interno al file 2026:

| Event | Athlete | Country | Discipline | Category | Apparatus | Format | Round | Score | Source row |
|---|---|---|---|---|---|---|---|---:|---:|
| `Fuzion National Qualifier` | `Elaina Sliney` | USA | WAG | senior | FX | individual | final | 12.600 | 1948 |

Decisione provvisoria: duplicato identico skippabile in commit reale, salvo diversa verifica admin.

### 17.6 File di review generati

| File | Righe operative | Stato |
|---|---:|---|
| `docs/import_reports/gymternet_2026_existing_athlete_match_review.csv` | 407 | 166 decisioni precompilate; 241 da controllare |
| `docs/import_reports/gymternet_2026_new_athlete_country_conflicts.csv` | 7 | 7 da controllare |
| `docs/import_reports/gymternet_2026_orphan_dscores.csv` | 287 | conservazione D-score orfani fuori dal DB |

Distribuzione delle 241 decisioni ancora da controllare nel CSV existing athlete:

| Tipo review | Righe |
|---|---:|
| `possible_existing_athlete_match` | 161 |
| `possible_athlete_country_change` | 47 |
| `possible_athlete_identity_collision` | 33 |

Le 166 decisioni gia precompilate derivano dalla regola persistente `same_country_review_reuse`, applicata solo a casi same-country gia verificati negli anni precedenti. I casi con cambio country restano sempre in review admin.

### 17.7 Prossimo passo

L'admin deve ora compilare:

- `docs/import_reports/gymternet_2026_existing_athlete_match_review.csv`;
- `docs/import_reports/gymternet_2026_new_athlete_country_conflicts.csv`.

Dopo la compilazione:

1. le decisioni saranno trasferite dai file Numbers ai CSV operativi;
2. sara generato il payload `gymternet_2026_athlete_match_decisions.json`;
3. verra eseguita una preview post-decisione;
4. se pulita, si procedera con backup e commit reale Results 2026;
5. infine si passera alla riconciliazione Calendar 2026.

### 17.8 Review admin completata e payload decisionale

L'admin ha completato i due file Numbers operativi:

| File Numbers | Righe trasferite nel CSV operativo |
|---|---:|
| `gymternet_2026_existing_athlete_match_review.numbers` | 407 |
| `gymternet_2026_new_athlete_country_conflicts.numbers` | 7 |

Le decisioni sono state trasferite nei CSV operativi con lo script:

```text
.venv/bin/python scripts/apply_gymternet_review_decisions.py 2026 --source-dir import_files --report-dir docs/import_reports
```

Durante la review admin e stata segnalata una correzione nome:

| Review | Athlete ID | Nome precedente | Nome corretto |
|---|---:|---|---|
| `athlete_match_d7eb122b7c46b2a0` | 21148 | Francesco Berarellt | Francesco Bertarelli |

La correzione e stata registrata nel file:

```text
docs/import_reports/gymternet_2026_athlete_name_corrections.csv
```

Il payload decisionale generato e:

```text
docs/import_reports/gymternet_2026_athlete_match_decisions.json
```

Distribuzione iniziale delle azioni:

| Azione | Conteggio |
|---|---:|
| `accept_suggestion` | 287 |
| `create_new` | 40 |
| `merge_as_same_athlete` | 40 |
| `keep_existing_country` | 32 |
| `update_country` | 15 |

### 17.9 Prima preview post-decisione e correzione Julianne Thibault

La prima preview post-decisione ha prodotto:

| Controllo | Conteggio |
|---|---:|
| Decisioni applicate | 414 |
| Decisioni irrisolte | 0 |
| Decisioni invalide | 0 |
| Duplicati identici | 1 |
| Conflitti post-decisione | 10 |

I 10 conflitti erano tutti riconducibili a un unico merge rischioso:

| Athlete importato | Athlete suggerito | Evento | Problema |
|---|---|---|---|
| Julianne Thibault | Julia Thibault | Canadian Championships 2026 | stesso contesto Result con score/D_score diversi |

Decisione applicata: `keep separate`, secondo la regola persistente `same_context_different_score_keep_separate`.

La riga corretta e:

```text
athlete_match_b99769b3ed6d5e29
```

Nota operativa inserita:

```text
Post-decision conflict review: same context with different scores; keep separate.
```

Il payload e stato rigenerato dai CSV operativi con:

```text
.venv/bin/python scripts/apply_gymternet_review_decisions.py 2026 --source-dir import_files --report-dir docs/import_reports --skip-numbers
```

Distribuzione finale delle azioni:

| Azione | Conteggio |
|---|---:|
| `accept_suggestion` | 286 |
| `create_new` | 41 |
| `merge_as_same_athlete` | 40 |
| `keep_existing_country` | 32 |
| `update_country` | 15 |

### 17.10 Preview post-decisione finale

La seconda preview post-decisione e risultata pulita:

| Controllo | Conteggio |
|---|---:|
| Righe parse | 66.017 |
| Result importabili | 66.016 |
| Duplicati identici | 1 |
| Conflitti | 0 |
| Decisioni irrisolte | 0 |
| Decisioni invalide | 0 |
| D-score orfani | 287 |

Il duplicato residuo e il duplicato identico interno al file:

| Event | Athlete | Country | Discipline | Category | Apparatus | Format | Round | Score |
|---|---|---|---|---|---|---|---|---:|
| `Fuzion National Qualifier` | `Elaina Sliney` | USA | WAG | senior | FX | individual | final | 12.600 |

### 17.11 Commit reale Results 2026

Il commit reale del file `Results 2026.xlsx` e stato eseguito con:

```text
.venv/bin/python scripts/commit_gymternet_year.py 2026 --source-dir import_files --report-dir docs/import_reports --db-path leverage.db
```

Report tecnico:

```text
docs/import_reports/gymternet_2026_commit_summary.json
```

Statistiche commit:

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

Controlli post-import:

| Controllo | Conteggio |
|---|---:|
| Gruppi duplicati semantici | 0 |
| Result 2026 completi con score e D_score | 53.591 |
| Result 2026 con final score ma senza D_score | 10.934 |
| Result 2026 senza final score | 1.599 |

### 17.12 Nota backup e correzione procedura

Durante il commit reale lo script ha riportato `backup_path: null`, perche il backup veniva creato solo se l'argomento `--backup` era passato esplicitamente.

Subito dopo il commit e stata creata una copia post-commit:

```text
backups/leverage_gymternet_2026_post_commit_20260714_202134.db
```

La procedura tecnica e stata corretta in `scripts/commit_gymternet_year.py`: da ora lo script crea automaticamente un backup pre-commit in `backups/` anche quando `--backup` non viene specificato.

### 17.13 Stato finale Results 2026

La fase Results 2026 e completata:

- review admin completata;
- correzione nome `Francesco Berarellt` -> `Francesco Bertarelli` applicata;
- conflitto `Julianne Thibault` / `Julia Thibault` risolto con `keep separate`;
- preview post-decisione pulita;
- commit reale eseguito;
- database aggiornato fino al primo semestre 2026;
- duplicati semantici post-import pari a 0.

## 18. Riconciliazione Calendar 2026 - primo semestre

Data: 15 luglio 2026

La fase Calendar 2026 e stata eseguita dopo il commit reale dei `Results 2026` del primo semestre.

File sorgente utilizzato:

```text
import_files/Calendar.xlsx
```

### 18.1 Obiettivo

L'obiettivo era collegare gli `Event` 2026 creati dai risultati Gymternet alle righe del calendario 2026, distinguendo:

- eventi 2026 con risultati gia importati;
- righe calendario future successive al 1 luglio 2026;
- righe calendario senza Event DB collegabile;
- Event DB derivati dai Results ma non presenti nel calendario sorgente;
- casi multi-data da salvare come `EventCalendarEntry`;
- casi `Top 12` a cavallo tra calendario e stagione.

### 18.2 Applicazione automatica sicura

Il primo commit automatico ha applicato solo i match diretti non ambigui.

Report:

```text
docs/import_reports/calendar_2026_commit_summary.json
```

Backup locale:

```text
backups/leverage_calendar_2026_20260714_203147.db
```

Sintesi:

| Metrica | Valore |
|---|---:|
| Righe Calendar 2026 | 170 |
| Event DB 2026 | 115 |
| Match automatici sicuri aggiornati | 105 |
| Event gia invariati | 1 |
| Review ancora necessarie dopo automatico | 4 |

### 18.3 Review admin corrente

Dopo la review admin sono state applicate le decisioni contenute nei report correnti.

Comando operativo:

```text
.venv/bin/python scripts/apply_calendar_current_review_decisions.py import_files/Calendar.xlsx --year 2026 --db-path leverage.db --report-dir docs/import_reports --commit
```

Report:

```text
docs/import_reports/calendar_2026_current_review_commit_summary.json
```

Backup locale:

```text
backups/leverage_calendar_current_review_2026_20260715_154044.db
```

Esito:

| Metrica | Valore |
|---|---:|
| Coppie Event/Calendar applicate | 7 |
| Event aggiornati | 2 |
| `EventCalendarEntry` create | 7 |
| Righe `calendar_only` create | 5 |
| Event `db_only` registrati | 2 |
| Decisioni irrisolte | 0 |
| Decisioni invalide | 0 |

Decisioni particolari:

- `Ifact Norges Cup 1` e `Ifact Norges Cup 2` sono state mantenute come `calendar_only`, perche nel file Calendar esistono ma non e stato trovato un Event DB 2026 corrispondente nei Results importati.
- `Colombian Championships` e stato registrato come `db_only`, perche l'Event esiste nel DB con risultati, ma non e stato trovato riscontro nel Calendar 2026 sorgente. La nota admin citava la riga 76, ma la riga 76 del Calendar 2026 corrisponde a `Varna Challenge Cup`.
- `Romanian Euros Trials` e stato registrato come `db_only`, perche deriva dai Results ma non ha una riga Calendar sorgente collegabile.

### 18.4 Conflitti source Bundesliga

I conflitti in cui piu righe calendario puntavano allo stesso Event DB sono stati risolti con la logica gia usata negli anni precedenti: non si forza una data unica nel record `Event`, ma si creano voci `EventCalendarEntry`.

Comando:

```text
.venv/bin/python scripts/commit_calendar_year.py import_files/Calendar.xlsx --year 2026 --db-path leverage.db --report-dir docs/import_reports --commit
```

Report:

```text
docs/import_reports/calendar_2026_commit_summary.json
```

Backup locale:

```text
backups/leverage_calendar_2026_20260715_174222.db
```

Esito:

| Metrica | Valore |
|---|---:|
| Conflitti source risolti | 4 |
| `EventCalendarEntry` create | 5 |
| Decisioni irrisolte | 0 |
| Decisioni invalide | 0 |

### 18.5 Casi Top 12 2026

Sono stati applicati anche i due casi `Top 12` gia accettati dall'admin.

Report:

```text
docs/import_reports/calendar_2026_top12_commit_summary.json
```

Backup locali:

```text
backups/leverage_calendar_spillover_2026_1650_20260715_154341.db
backups/leverage_calendar_spillover_2025_1584_20260715_154341.db
```

Decisioni:

| Caso | Decisione |
|---|---|
| `Top 12 Series 3` MAG, Event 1650 | collegato alla riga Calendar 2026 n. 31, `Top 12 Series 3 (MAG)`, data 2026-02-28 |
| `Top 12 Series 3 (2026)` WAG, Event 1584 | collegato alla riga Calendar 2025 n. 227 come `season_year_spillover`, data 2025-12-13 |

### 18.6 Copertura finale Calendar 2026

Report finale:

```text
docs/import_reports/calendar_2026_current_match_summary.csv
```

Esito finale:

| Metrica | Valore |
|---|---:|
| Righe Calendar 2026 | 170 |
| Event DB 2026 | 115 |
| Event DB 2026 coperti | 115 |
| Event DB 2026 ancora senza copertura | 0 |
| Righe Calendar 2026 non abbinate | 45 |
| Event `db_only` | 2 |
| Righe `calendar_only` | 5 |
| Collegamenti `season_year_spillover` per Event 2026 | 1 |
| Cross-year errati | 0 |
| Issue sorgente | 0 |

Le 45 righe Calendar 2026 non abbinate sono successive al 1 luglio 2026 e, al momento della prima chiusura del calendario, erano state lasciate in standby fino al successivo import dei Results 2026 di fine anno.

Aggiornamento del 16 luglio 2026:

Per rendere visibili nel calendario pubblico anche gli eventi futuri gia schedulati ma privi di Results, le 45 righe future sono state materializzate nel database locale.

Flusso usato:

```text
.venv/bin/python scripts/materialize_future_calendar_events.py import_files/Calendar.xlsx --year 2026 --from-date 2026-07-16
.venv/bin/python scripts/materialize_future_calendar_events.py import_files/Calendar.xlsx --year 2026 --from-date 2026-07-16 --commit
```

Report prodotti:

```text
docs/import_reports/calendar_2026_future_materialization_dry_run_summary.json
docs/import_reports/calendar_2026_future_materialization_commit_summary.json
```

Backup locale creato prima del commit:

```text
backups/leverage_future_calendar_2026_20260716_120535.db
```

Esito materializzazione:

| Metrica | Valore |
|---|---:|
| Righe future Calendar 2026 processate | 45 |
| Nuovi Event futuri creati | 42 |
| Event futuro gia esistente | 1 |
| EventCalendarEntry future create | 2 |
| Righe ambigue | 0 |

Decisione metodologica:

- le righe future senza Event DB sono state create come nuovi `Event`, con `result_count = 0`, per renderle cliccabili/salvabili e predisporre il successivo inserimento Results;
- `British Team Championships` era gia presente come Event futuro e non e stato duplicato;
- `3rd Bundesliga` e `4th Bundesliga` avevano gia Event 2026 con risultati e date di aprile: le date future sono state conservate come `EventCalendarEntry`, senza sovrascrivere le date degli Event gia popolati.

### 18.7 Correzione semantica Youth

Durante il controllo dei filtri calendario e stato deciso che ogni evento contenente `Youth` nel nome deve essere trattato come evento junior.

Questa regola e stata applicata sia alla logica futura di import Calendar sia ai dati locali gia popolati.

Report prodotto:

```text
docs/import_reports/youth_category_correction_20260716.json
```

Backup locale post-correzione:

```text
backups/leverage_youth_category_correction_20260716_123000.db
```

Esito correzione:

| Metrica | Valore |
|---|---:|
| Event corretti da `junior and senior` a `junior` | 5 |
| Result collegati corretti da `senior` a `junior` | 191 |

Event corretti:

| Event ID | Year | Event | Result corretti |
|---:|---:|---|---:|
| 271 | 2019 | European Youth Olympic Festival | 5 |
| 411 | 2019 | International Youth Games | 12 |
| 508 | 2020 | Pre-Olympic Youth Cup | 41 |
| 1718 | 2026 | Pre-Olympic Youth Cup | 133 |
| 1749 | 2026 | Youth Olympic Games | 0 |

### 18.8 Stato database locale dopo Results + Calendar 2026

| Entita | Totale |
|---|---:|
| Athlete attivi | 27.921 |
| Event attivi | 1.761 |
| Result attivi | 819.739 |
| Event 2026 | 157 |
| Result 2026 | 66.124 |
| EventCalendarEntry 2026 | 20 |
| Righe `calendar_only` 2026 | 5 |
| Event futuri datati dal 16 luglio 2026 | 43 |
| EventCalendarEntry future dal 16 luglio 2026 | 2 |

Event 2026 senza `start_date` diretta:

| Event | Motivo |
|---|---|
| `1st Bundesliga` | Evento multi-data conservato tramite `EventCalendarEntry` |
| `Colombian Championships` | `db_only`, Results presenti ma Calendar sorgente senza riscontro |
| `Romanian Euros Trials` | `db_only`, Results presenti ma Calendar sorgente senza riscontro |

### 18.9 Milestone

Milestone raggiunta il 15 luglio 2026: LEVERAGE e popolato e riconciliato fino al primo semestre 2026.

La fase dati storici ora copre:

- Results 2018-2025 completi;
- Results 2026 primo semestre;
- Calendar 2018-2025 completo;
- Calendar 2026 riconciliato per gli Event con risultati disponibili e materializzato anche per gli eventi futuri schedulati dal 16 luglio 2026.

Il prossimo completamento dati avverra quando sara disponibile il file Results 2026 di fine anno o un secondo file 2026 aggiornato.
