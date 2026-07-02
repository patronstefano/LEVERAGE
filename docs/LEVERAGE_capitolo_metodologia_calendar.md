# Capitolo X - Metodologia di riconciliazione Calendar/Event in LEVERAGE

Documento aggiornato al 2 luglio 2026
Repository: `patronstefano/LEVERAGE`
Stato operativo: riconciliazione Calendar 2018-2025 completata, verificata e versionata; Calendar 2026 in standby in attesa dei Result 2026

---

## 1. Obiettivo del capitolo

Questo capitolo descrive la metodologia adottata per integrare in LEVERAGE il calendario eventi fornito da Gymternet e riconciliarlo con gli `Event` gia creati durante il popolamento storico dei `Result`.

Dopo l'importazione dei risultati 2018-2025, il database conteneva competizioni e performance, ma non sempre disponeva di date affidabili per ogni evento. Il file `Calendar.xlsx` ha quindi permesso di completare il livello temporale del database, necessario per costruire in futuro:

- calendario pubblico degli eventi;
- calendario admin di controllo;
- distinzione tra eventi futuri, in corso e conclusi;
- reminder admin per eventi conclusi senza risultati;
- schede evento con datazione affidabile;
- analisi temporali e dashboard basate su periodi di gara.

L'obiettivo non era semplicemente copiare date nel database, ma costruire un processo controllato, verificabile e semanticamente corretto. Il calendario contiene infatti eventi MAG, WAG, misti, eventi di stagione a cavallo d'anno, competizioni non svolte o prive di risultati Gymternet, e casi in cui piu righe calendario possono riferirsi alla stessa scheda `Event`.

---

## 2. Contesto dati

La fonte utilizzata e il file `Calendar.xlsx`, fornito da Gymternet, contenente un foglio per ogni anno dal 2018 al 2026.

Ogni foglio contiene principalmente:

| Campo sorgente | Significato |
|---|---|
| `DATE` | Intervallo temporale della competizione nel formato testuale Gymternet. |
| `EVENT` | Nome dell'evento nel calendario Gymternet. |

Prima dell'integrazione, le date sono state normalizzate nel formato:

| Caso | Formato standard |
|---|---|
| Giorno singolo | `Jan 11` |
| Piu giorni nello stesso mese | `Jan 11-15` |
| Piu giorni tra mesi diversi | `Jan 11-Feb 3` |

Il file normalizzato usato dal backend e:

```text
docs/import_reports/Calendar_date_normalized.xlsx
```

---

## 3. Entita coinvolte

La riconciliazione Calendar/Event coinvolge principalmente due entita del database.

### 3.1 Event

`Event` rappresenta la scheda principale della competizione. Contiene nome, anno, disciplina, categoria, livello, date canoniche e metadati.

Campi rilevanti:

| Campo | Ruolo nel Calendar |
|---|---|
| `name` | Nome della competizione creata dal popolamento dei Result. |
| `year` | Anno evento usato dal database e dai Result. |
| `discipline` | `MAG`, `WAG` oppure `MAG and WAG`. |
| `category` | `junior`, `senior` oppure `junior and senior`. |
| `start_date` | Data canonica di inizio evento. |
| `end_date` | Data canonica di fine evento. |

### 3.2 EventCalendarEntry

Durante la review e emerso che una singola scheda `Event` puo essere rappresentata da piu righe calendario. Questo accade, ad esempio, quando:

- MAG e WAG si svolgono in giorni diversi;
- una competizione ha piu giornate o serie;
- un evento di stagione cade nel calendario dell'anno precedente;
- una riga Calendar aggiuntiva deve puntare alla stessa scheda evento senza sovrascrivere la data canonica.

Per questo e stata introdotta l'entita `EventCalendarEntry`.

`EventCalendarEntry` consente di salvare voci calendario separate, eventualmente collegate allo stesso `Event`, senza comprimere piu date dentro un unico intervallo artificiale.

Campi rilevanti:

| Campo | Significato |
|---|---|
| `event_id` | Event collegato; puo essere nullo per voci solo calendario. |
| `name` | Nome della riga calendario. |
| `start_date` / `end_date` | Date specifiche della riga calendario. |
| `year` | Anno del foglio Calendar sorgente. |
| `discipline` | Disciplina inferita dalla riga Calendar. |
| `source` | Fonte della riga, ad esempio `gymternet_calendar`. |
| `source_row` | Numero riga nel foglio Calendar. |
| `source_note` | Nota metodologica, ad esempio `season_year_spillover`. |

---

## 4. Pipeline operativa

La riconciliazione e stata eseguita anno per anno, dal 2018 al 2025, seguendo una procedura prudente e ripetibile.

Il flusso standard e stato:

1. generazione dei report di matching Calendar/Event;
2. applicazione automatica solo dei match sicuri;
3. creazione di backup del database;
4. generazione dei CSV snelli per la review admin;
5. compilazione manuale dei CSV/Numbers da parte dell'admin;
6. trasferimento controllato delle decisioni nei CSV operativi;
7. applicazione in dry-run delle decisioni;
8. commit reale solo in assenza di decisioni invalide;
9. rigenerazione della coverage corrente;
10. aggiornamento del diario e dei report;
11. commit e push su GitHub.

Gli script principali usati sono:

| Script | Funzione |
|---|---|
| `scripts/generate_calendar_review_reports.py` | Produce i report iniziali di match e mismatch. |
| `scripts/commit_calendar_year.py` | Applica le date sicure e risolve i conflitti source/date approvati. |
| `scripts/generate_calendar_current_coverage_reports.py` | Fotografa la copertura corrente dopo le decisioni. |
| `scripts/apply_calendar_current_review_decisions.py` | Applica le decisioni sui CSV current. |
| `scripts/apply_calendar_numbers_decisions.py` | Trasferisce le decisioni dai file Numbers ai CSV operativi. |
| `scripts/link_calendar_spillover_entry.py` | Collega righe Calendar cross-year a Event di stagione diversa. |

---

## 5. Principi metodologici

### 5.1 Same-year strict matching

Una delle prime regole rafforzate e stata il matching same-year strict: quando si riconcilia il foglio Calendar di un anno, i suggerimenti automatici devono riferirsi prima di tutto a `Event.year` dello stesso anno.

Questa regola evita falsi match cross-year, come una riga Calendar 2018 collegata a un Event DB 2019 con nome simile.

Eccezione: i casi di stagione a cavallo d'anno non vengono forzati nel matching automatico, ma gestiti esplicitamente come `season_year_spillover` dopo review admin.

### 5.2 Normalizzazione semantica MAG/WAG

Nel calendario, `MAG` indica eventi maschili e `WAG` eventi femminili. Nei nomi evento, pero, possono comparire varianti come:

- `Men's`;
- `Mens`;
- `Women`;
- `Women's`;
- `Womens`.

Il sistema tratta queste varianti come semanticamente compatibili.

Inoltre, un `Event` con disciplina `MAG and WAG` puo essere collegato a righe Calendar MAG e WAG separate, se rappresentano lo stesso evento storico.

### 5.3 Event misto e filtri utente separati

Un punto importante per la futura UI e la distinzione tra contenitore evento e risultati.

Un `Event` puo rimanere `MAG and WAG` come contenitore semantico della competizione, ma l'utente non deve necessariamente vedere un filtro autonomo `MAG and WAG`.

Nelle classifiche, nei grafici e nei confronti, i pulsanti realmente cliccabili devono essere `MAG` e/o `WAG` quando esistono `Result` con quei valori.

La selezione dell'utente deve quindi filtrare sul campo:

```text
Result.discipline
```

e non sul valore aggregato:

```text
Event.discipline
```

Questa scelta garantisce che, in una competizione mista, l'utente possa visualizzare separatamente risultati maschili e femminili.

### 5.4 Calendar only

Non tutte le righe Calendar devono avere una scheda `Event` collegata.

Alcune competizioni presenti nel calendario possono:

- non essersi svolte;
- non avere risultati Gymternet disponibili;
- non essere state incluse nei file Results importati;
- rimanere utili come informazione calendario.

In questi casi la riga viene mantenuta come `calendar_only`: sara visibile nel calendario, ma non rimandera a una scheda evento con risultati.

### 5.5 DB only

Simmetricamente, un `Event` ricavato dai `Result` puo non comparire nel Calendar sorgente.

In questi casi non si forza un match artificiale. Dopo review admin, l'Event puo essere marcato come `db_only`.

La regola finale adottata e:

```text
ogni Event DB derivato dai Result deve avere copertura Calendar oppure review esplicita come db_only
```

Non e invece obbligatorio che ogni riga Calendar abbia una scheda Event collegata.

### 5.6 EventCalendarEntry per date multiple

Quando piu righe Calendar sono corrette per lo stesso `Event`, il sistema non sovrascrive ripetutamente `Event.start_date` / `Event.end_date`.

La data canonica dell'Event viene preservata, mentre le righe aggiuntive sono salvate come `EventCalendarEntry`.

Questa scelta evita di perdere informazione nei casi MAG/WAG, Top 12, Bundesliga, test nazionali, giornate separate o gare con sotto-eventi.

### 5.7 Season year spillover

Alcuni eventi appartengono a una stagione indicata nell'anno successivo, ma si svolgono nel calendario dell'anno precedente.

Questi casi sono stati gestiti come:

```text
season_year_spillover
```

Non si tratta di errori cross-year, ma di eccezioni controllate e documentate.

Esempi:

| Caso | Interpretazione |
|---|---|
| `1st Spanish League (2020 season)` | Event DB 2020 con data reale nel Calendar 2019. |
| `Top 12 Series 3 (2025)` | Event DB 2025 collegato alla riga Calendar 2024 `Top 12 Series 3 (MAG)`. |

---

## 6. Review admin

Per ogni anno sono stati generati CSV semplificati per rendere la review piu rapida e leggibile.

I tre file principali sono:

| File | Scopo |
|---|---|
| `calendar_YYYY_calendar_unmatched_current.csv` | Righe Calendar senza match corrente. |
| `calendar_YYYY_db_unmatched_current.csv` | Event DB senza copertura Calendar. |
| `calendar_YYYY_source_conflicts_slim.csv` | Casi in cui piu righe Calendar puntano allo stesso Event con date diverse. |

La review admin usa valori operativi semplici:

| Valore | Significato |
|---|---|
| `1`, `2`, `3`, ... | Sceglie una delle opzioni suggerite. |
| `1 and 2` | Conferma piu righe/date per lo stesso Event. |
| `calendar_only` | Mantiene una riga Calendar senza scheda Event collegata. |
| `db_only` | Marca un Event DB come assente dal Calendar sorgente. |
| `manual_event_id` | Permette di indicare manualmente un Event ID non suggerito. |

La compilazione e avvenuta spesso tramite Numbers. Per evitare alterazioni dei campi tecnici, e stato introdotto uno script dedicato che trasferisce nei CSV operativi soltanto le colonne decisionali.

---

## 7. Regole persistenti emerse

Durante la riconciliazione sono state formalizzate alcune regole riutilizzabili.

### 7.1 EYOF

`EYOF` significa sempre:

```text
European Youth Olympic Festival
```

Quindi nei futuri match Calendar/Event e negli import, il sistema deve espandere semanticamente questa abbreviazione prima di considerarla un mismatch.

Esempio:

| Valore abbreviato | Valore esteso |
|---|---|
| `EYOF Mixed Pairs` | `European Youth Olympic Festival` |

### 7.2 Top 12

Gli eventi `Top 12` possono cadere a cavallo tra due calendari annuali della stessa stagione.

Questo non deve essere interpretato automaticamente come errore. Il sistema deve:

- verificare la stagione;
- controllare i Result gia presenti;
- evitare duplicati;
- usare `EventCalendarEntry`;
- annotare `season_year_spillover` quando la data reale cade in un foglio Calendar diverso dall'anno dell'Event DB.

### 7.3 Event senza risultati

Alcune righe Calendar possono non corrispondere ad alcun Event DB perche non esistono Results importati.

Questi casi possono essere mantenuti come `calendar_only`, soprattutto in vista di un calendario pubblico o admin che includa eventi futuri, eventi non svolti o competizioni senza risultati sorgente.

### 7.4 Event da Result assenti dal Calendar

Alcuni Event DB possono essere derivati dai Result ma non presenti nel Calendar sorgente.

Questi casi non devono essere forzati verso match deboli. Dopo review, possono essere marcati come `db_only`.

---

## 8. Sintesi annuale 2018-2025

### 2018

Il 2018 ha permesso di definire la prima metodologia Calendar/Event.

Decisioni principali:

- introduzione della review manuale per mismatch;
- gestione dei casi MAG/WAG multi-data;
- introduzione di `EventCalendarEntry`;
- correzione di un match cross-year errato;
- chiusura finale con copertura completa.

Esito:

| Metrica | Valore |
|---|---:|
| Righe Calendar | 214 |
| Event DB | 211 |
| Calendar senza match finale | 0 |
| Event DB senza copertura finale | 0 |

### 2019

Il 2019 ha consolidato il matching same-year strict.

Decisioni principali:

- il matching automatico deve proporre Event dello stesso anno;
- alcune righe Calendar possono restare `calendar_only`;
- la metrica critica diventa la copertura di tutti gli Event DB derivati dai Result.

Esito:

| Metrica | Valore |
|---|---:|
| Righe Calendar | 244 |
| Event DB | 233 |
| Calendar only | 2 |
| Event DB senza copertura | 0 |

### 2020

Il 2020 ha introdotto la gestione formale dello `season_year_spillover`.

Caso guida:

```text
1st Spanish League (2020 season)
```

L'Event appartiene al 2020, ma la data reale si trova nel Calendar 2019.

Esito:

| Metrica | Valore |
|---|---:|
| Righe Calendar | 90 |
| Event DB | 77 |
| Calendar only | 2 |
| Season year spillover | 1 |
| Event DB senza copertura | 0 |

### 2021

Il 2021 ha introdotto in modo esplicito il concetto di `db_only`.

Caso rilevante:

```text
RomGym Trophy
```

L'Event e presente nei Result, ma non nel Calendar sorgente. Non e stato forzato alcun match artificiale.

Esito:

| Metrica | Valore |
|---|---:|
| Righe Calendar | 210 |
| Calendar only | 1 |
| DB only | 1 |
| Event DB senza copertura/review | 0 |

### 2022

Il 2022 si e chiuso senza eccezioni `calendar_only` o `db_only`.

Caso metodologico:

```text
EYOF Mixed Pairs -> European Youth Olympic Festival
```

Questa decisione ha contribuito a formalizzare la regola persistente su `EYOF`.

Esito:

| Metrica | Valore |
|---|---:|
| Righe Calendar | 228 |
| Calendar only | 0 |
| DB only | 0 |
| Event DB senza copertura/review | 0 |

### 2023

Il 2023 ha richiesto una pulizia preliminare della sorgente, perche alcune righe Calendar contenevano link nel testo evento.

Decisioni principali:

- pulizia del foglio 2023 senza modificare date o numero righe;
- collegamento `EYOF Mixed Pairs` a `European Youth Olympic Festival`;
- gestione di eventi stagione 2024 presenti nel Calendar 2023;
- creazione di piu collegamenti `season_year_spillover`;
- mantenimento di alcune righe come `calendar_only`.

Esito:

| Metrica | Valore |
|---|---:|
| Righe Calendar | 265 |
| Calendar only | 13 |
| DB only | 1 |
| Season year spillover | 7 |
| Event DB senza copertura/review | 0 |

### 2024

Il 2024 e stato avviato considerando gia validi gli spillover creati durante la review 2023.

Decisioni principali:

- preservazione dei collegamenti `season_year_spillover`;
- review dei conflitti Top 12 e Bundesliga;
- uso di scelte multiple per creare `EventCalendarEntry`;
- chiusura con zero Event DB `db_only`.

Esito:

| Metrica | Valore |
|---|---:|
| Righe Calendar | 222 |
| Event DB | 207 |
| Calendar only | 2 |
| DB only | 0 |
| Season year spillover | 6 |
| Event DB senza copertura/review | 0 |

### 2025

Il 2025 ha chiuso il ciclo storico Calendar 2018-2025.

Decisioni principali:

- trasferimento delle decisioni da Numbers tramite script dedicato;
- normalizzazione `EYOF Mixed Pairs` su `European Youth Olympic Festival`;
- gestione di `Top 12 Series 3 (2025)` come spillover dal Calendar 2024;
- conferma della regola UI secondo cui gli Event `MAG and WAG` sono contenitori, mentre i filtri utente devono lavorare su `Result.discipline`;
- chiusura con zero Calendar unmatched e zero DB unmatched.

Esito:

| Metrica | Valore |
|---|---:|
| Righe Calendar | 227 |
| Event DB | 224 |
| Calendar unmatched finale | 0 |
| DB unmatched finale | 0 |
| Calendar only | 0 |
| DB only | 1 |
| Season year spillover | 1 |

L'Event `db_only` 2025 e:

```text
Dutch Worlds Trials 3
```

Il caso `season_year_spillover` 2025 e:

```text
Calendar 2024 row 219 - Top 12 Series 3 (MAG)
collegato a Event DB 2025 ID 1219 - Top 12 Series 3 (2025)
```

---

## 9. Impatto sul backend e sulla futura UI

La riconciliazione Calendar/Event ha reso possibile sviluppare una futura UI calendario coerente.

Funzionalita abilitate:

- calendario pubblico consultabile;
- calendario admin con eventi passati e futuri;
- identificazione di eventi con risultati gia importati;
- identificazione di eventi conclusi senza risultati;
- eventi futuri salvabili dagli utenti;
- reminder admin per completare Results mancanti;
- filtri per anno, periodo, disciplina, categoria e stato evento;
- collegamento tra voce calendario e scheda evento;
- supporto a voci calendario senza scheda Event (`calendar_only`);
- supporto a Event DB senza voce calendario (`db_only`).

Il backend e gia predisposto a calcolare lo stato calendario dell'evento, ad esempio:

| Stato | Significato |
|---|---|
| `upcoming` | Evento futuro. |
| `ongoing` | Evento in corso. |
| `completed_with_results` | Evento concluso con Result disponibili. |
| `completed_no_results` | Evento concluso senza Result importati. |

---

## 10. Controlli e versionamento

Ogni anno Calendar e stato chiuso con:

- backup locale del database prima del commit reale;
- report JSON di dry-run e commit;
- CSV di review conservati in `docs/import_reports`;
- aggiornamento del diario di bordo;
- generazione del documento Word;
- commit Git;
- push su GitHub.

La test suite backend e stata eseguita dopo modifiche rilevanti agli script e alla logica di supporto.

Per la chiusura Calendar 2025, la verifica finale ha prodotto:

```text
113 passed
```

---

## 11. Lavoro residuo sul 2026

Il Calendar 2026 e gia presente nel file sorgente, ma la riconciliazione completa e stata lasciata in standby perche i `Results 2026` non sono ancora disponibili.

Il flusso futuro sara:

1. import controllato dei Results 2026;
2. preview e review dei conflitti atleta/country/nome;
3. verifica duplicati rispetto ai 108 result 2026 gia creati dal file 2025;
4. riconciliazione Calendar 2026;
5. distinzione tra eventi 2026 con risultati e voci calendario future/senza risultati;
6. eventuale uso di `calendar_only`, `db_only` e `season_year_spillover`;
7. aggiornamento del diario e dei capitoli di tesi.

---

## 12. Conclusione

La fase Calendar ha trasformato il popolamento storico di LEVERAGE da semplice archivio di risultati a base dati temporalmente interrogabile.

La scelta metodologica principale e stata evitare automatismi aggressivi: ogni data e ogni collegamento ambiguo sono stati verificati, documentati e versionati. Il sistema distingue ora tra schede evento, voci calendario, risultati effettivamente disponibili e casi eccezionali come eventi non svolti, eventi assenti dal Calendar o competizioni di stagione a cavallo d'anno.

Questa struttura e essenziale per il futuro MVP online, perche permette a LEVERAGE di offrire non solo classifiche e schede atleta, ma anche una navigazione temporale degli eventi e un pannello admin capace di monitorare cosa e gia stato importato e cosa deve ancora essere completato.
