# LEVERAGE - Diario di bordo del popolamento massivo database

Data apertura documento: 24 giugno 2026  
Stato: import storico 2018 committato e verificato; prossimo passo preview 2019
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

## 8. Prossimo passo

Il prossimo passo e ripetere il flusso sul file 2019:

1. backup dello stato post-2018;
2. preview import 2019 senza commit;
3. analisi collisioni atleta/country e possibili name-order automatici;
4. verifica duplicati e D-score orfani;
5. decisioni admin documentate;
6. commit controllato 2019;
7. controlli post-import 2019;
8. aggiornamento del presente diario.
