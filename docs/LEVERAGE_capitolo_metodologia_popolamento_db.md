# Capitolo X - Metodologia di popolamento e validazione del database LEVERAGE

Documento aggiornato al 30 giugno 2026  
Repository: `patronstefano/LEVERAGE`  
Stato operativo: popolamento storico Gymternet 2018-2025 completato, verificato e versionato

---

## 1. Obiettivo del capitolo

Il presente capitolo descrive la metodologia adottata per il popolamento massivo del database di LEVERAGE, piattaforma backend dedicata alla raccolta, strutturazione e analisi dei risultati internazionali di ginnastica artistica maschile e femminile.

L'obiettivo non era soltanto importare grandi quantita di dati storici, ma costruire un processo controllato, ripetibile e documentabile. Il database di LEVERAGE e infatti pensato come base informativa per classifiche, confronti, grafici, schede atleta, schede evento e analisi longitudinali delle performance. Per questo motivo la qualita del dato e stata trattata come requisito centrale del progetto.

Il popolamento storico ha riguardato i file Gymternet relativi agli anni 2018-2025. Ogni file e stato analizzato, normalizzato, verificato tramite preview, sottoposto a review admin quando necessario, importato nel database solo dopo approvazione e infine controllato con verifiche post-import.

Il principio metodologico seguito e stato il seguente:

```text
nessun dato storico viene importato alla cieca
```

Ogni import e quindi passato attraverso un ciclo di controllo composto da preview, report, review, decisioni esplicite, commit controllato, test e versionamento Git.

---

## 2. Contesto del database LEVERAGE

Il backend LEVERAGE e stato sviluppato in Python con FastAPI, SQLAlchemy, Alembic e SQLite locale. La struttura e predisposta per una futura migrazione verso PostgreSQL, ma durante la fase MVP il popolamento e stato eseguito sul database locale `leverage.db`.

Le entita centrali coinvolte nel popolamento storico sono tre:

| Entita | Ruolo nel popolamento |
|---|---|
| `Athlete` | Conserva l'identita dell'atleta, la disciplina, la country corrente/canonica, eventuali dati anagrafici e riferimenti ufficiali. |
| `Event` | Conserva la competizione: nome, anno, date, paese, disciplina, categoria, livello e altri metadati. |
| `Result` | Conserva la singola performance: atleta, evento, apparatus, round, format, categoria, punteggi, rank e country rappresentata in gara. |

Il popolamento storico non crea soltanto `Result`. Quando il file sorgente contiene atleti o competizioni non ancora presenti nel database, il tool di import puo creare nuove entita `Athlete` ed `Event`, sempre tracciando le operazioni nei report e nelle notifiche amministrative previste dal backend.

Un punto semantico rilevante e la distinzione tra:

| Campo | Significato |
|---|---|
| `Athlete.country` | Country corrente o canonica dell'atleta nella scheda atleta. |
| `Result.represented_country` | Country rappresentata dall'atleta in quella specifica gara. |

Questa distinzione e necessaria per gestire cambi di nazionalita, errori di data entry nelle fonti storiche e casi in cui uno stesso atleta abbia gareggiato per country diverse in anni o eventi differenti.

---

## 3. Fonti dati utilizzate

La fonte dati storica utilizzata per il popolamento massivo e costituita dai file Excel Gymternet standardizzati:

| File sorgente | Periodo importato |
|---|---|
| `Results 2018.xlsx` | Dati storici 2018 |
| `Results 2019.xlsx` | Dati storici 2019, con alcuni eventi 2020 presenti nel file |
| `Results 2020.xlsx` | Dati storici 2020 |
| `Results 2021.xlsx` | Dati storici 2021 |
| `Results 2022.xlsx` | Dati storici 2022, con alcuni eventi 2023 presenti nel file |
| `Results 2023.xlsx` | Dati storici 2023, con alcuni eventi 2024 presenti nel file |
| `Results 2024.xlsx` | Dati storici 2024, con alcuni eventi 2025 presenti nel file |
| `Results 2025.xlsx` | Dati storici 2025, con 108 record associati a evento 2026 |

I file contengono dati di ginnastica artistica maschile e femminile. Il formato legacy Gymternet non registra in modo completo tutte le componenti del punteggio. In particolare, per il periodo 2018-2025:

- molti result dispongono di final score ma non di `D_score`;
- i `D_score` possono comparire in fogli separati rispetto ai final score;
- `E_score`, penalty e bonus non sono registrati in modo completo;
- alcuni dati sul vault richiedono regole specifiche di interpretazione;
- alcuni eventi possono essere collocati nell'anno successivo rispetto al nome del file sorgente.

Il sistema non forza la sorgente dentro una struttura artificiale. Quando il file contiene un evento con anno diverso dall'anno nominale del file, LEVERAGE conserva l'anno reale dell'evento indicato nei dati. Questo ha generato spillover documentati, ad esempio dal file 2025 verso l'anno evento 2026.

---

## 4. Pipeline operativa di import

Il processo di popolamento e stato organizzato anno per anno. Ogni anno e stato completato prima di procedere al successivo, in modo da usare il database aggiornato come base per riconoscere atleti, eventi, duplicati e possibili collisioni negli anni seguenti.

Il flusso operativo standard e stato il seguente:

1. Verifica dello stato del repository e del database.
2. Verifica delle migrazioni Alembic.
3. Backup del database prima di modifiche rilevanti.
4. Preview dell'import senza scrivere nel database operativo.
5. Generazione dei report tecnici.
6. Separazione dei problemi in file CSV di review.
7. Revisione manuale da parte dell'admin nei file CSV/Numbers.
8. Trasferimento controllato delle sole colonne decisionali nei CSV operativi.
9. Generazione del payload tecnico delle decisioni admin.
10. Preview post-decisione su copia temporanea del database.
11. Controllo di conflitti e duplicati residui.
12. Correzione delle decisioni se la preview segnala problemi.
13. Commit reale dell'import sul database locale.
14. Controlli post-import su conteggi, qualita e duplicati semantici.
15. Esecuzione della test suite backend.
16. Aggiornamento della documentazione.
17. Commit e push su GitHub.

Questa pipeline ha permesso di trattare ogni import come una procedura verificabile, non come una semplice operazione di caricamento file.

Gli script principali del flusso sono:

| Script | Funzione |
|---|---|
| `scripts/generate_gymternet_preview_reports.py` | Genera preview e report senza modificare il database operativo. |
| `scripts/apply_gymternet_review_decisions.py` | Trasforma le decisioni admin in payload tecnico riutilizzabile dal tool. |
| `scripts/preview_gymternet_with_decisions.py` | Esegue una preview applicando le decisioni admin su copia temporanea del DB. |
| `scripts/commit_gymternet_year.py` | Esegue il commit reale dell'import dopo preview pulita e backup. |
| `scripts/generate_docx_from_markdown.py` | Genera copie Word dei documenti metodologici e dei diari di bordo. |

---

## 5. Preview e report preliminari

La preview e il punto centrale della metodologia. In questa fase il tool legge il file Excel, interpreta i dati secondo le regole Gymternet legacy e produce report senza modificare `leverage.db`.

La preview produce informazioni su:

- numero di record letti;
- numero di result importabili;
- atleti che verrebbero creati;
- eventi che verrebbero creati;
- duplicati identici;
- conflitti bloccanti;
- `D_score` orfani;
- possibili match con atleti gia presenti;
- country discordanti;
- correzioni nome suggerite;
- distribuzione per anno evento;
- result completi e parziali.

I report vengono salvati in `docs/import_reports/` e costituiscono una traccia permanente dell'import.

Per ogni anno sono stati generati, quando necessari, file come:

| Report | Scopo |
|---|---|
| `gymternet_YYYY_preview_summary.json` | Sintesi tecnica della preview iniziale. |
| `gymternet_YYYY_duplicates.csv` | Duplicati identici rilevati nel file sorgente. |
| `gymternet_YYYY_conflicts.csv` | Conflitti bloccanti prima delle decisioni admin. |
| `gymternet_YYYY_orphan_dscores.csv` | D-score non agganciati a result con final score. |
| `gymternet_YYYY_athlete_review.csv` | Review tecnica completa atleta/country. |
| `gymternet_YYYY_existing_athlete_match_review.csv` | CSV operativo per possibili match con atleti gia presenti nel DB. |
| `gymternet_YYYY_new_athlete_country_conflicts.csv` | CSV operativo per nuovi atleti con country discordanti. |
| `gymternet_YYYY_athlete_match_decisions.json` | Payload tecnico delle decisioni admin. |
| `gymternet_YYYY_preview_with_decisions_summary.json` | Preview post-decisione. |
| `gymternet_YYYY_post_decision_conflicts.csv` | Conflitti residui dopo le decisioni admin. |
| `gymternet_YYYY_post_decision_duplicates.csv` | Duplicati residui dopo le decisioni admin. |
| `gymternet_YYYY_commit_summary.json` | Report del commit reale sul database. |

La presenza di questi file rende l'intero popolamento ispezionabile anche a distanza di tempo.

---

## 6. Review admin tramite CSV

Le collisioni di identita e country non sono state risolte automaticamente quando il rischio semantico era alto. Il sistema ha generato CSV semplificati per permettere all'admin di decidere caso per caso.

Le colonne operative principali sono:

| Colonna | Significato |
|---|---|
| `decision` | Decisione sull'identita atleta: `merge as same athlete` oppure `keep separate`. |
| `action` | Decisione sulla country: `canonical country` oppure `country history`. |
| `country` | Country corretta nel caso `canonical country`, oppure country finale/corrente nel caso `country history`. |
| `notes` | Annotazioni manuali utili per motivare o ricordare la scelta. |

Nel caso di possibili match con atleti gia presenti, il CSV mostra anche elementi di contesto come:

- nome atleta importato;
- nome atleta suggerito dal database;
- country importata;
- country gia presente;
- disciplina;
- gare gia presenti nel database;
- evidenze degli anni successivi;
- similarita tra nomi;
- eventuale regola automatica suggerita.

Questo ha reso possibile distinguere tre situazioni diverse:

1. stesso atleta con semplice variante di nome;
2. stesso atleta con cambio country o country storica;
3. atleta diverso con nome simile.

La review non e stata svolta direttamente sul database. L'admin ha lavorato su CSV/Numbers e poi il sistema ha trasferito solo le colonne decisionali nei CSV operativi, preservando i campi tecnici originali generati dal backend. Questa scelta evita alterazioni involontarie del formato, delle chiavi tecniche o delle colonne usate dagli script.

---

## 7. Regole decisionali principali

Durante il popolamento sono emerse regole metodologiche che sono state rese persistenti nel progetto. Non sono rimaste soltanto decisioni in chat, ma sono state formalizzate nei report, nei payload e nella memoria decisionale del tool Gymternet.

### 7.1 Merge come stesso atleta

La decisione `merge as same athlete` viene usata quando l'atleta importato e l'atleta gia presente nel database rappresentano la stessa persona.

Esempi tipici:

- inversione nome/cognome;
- refuso evidente nel nome;
- trattini o spazi differenti;
- traslitterazione leggermente diversa;
- country coerente e storico risultati compatibile.

In questi casi i nuovi result vengono collegati all'entita `Athlete` gia esistente.

### 7.2 Keep separate

La decisione `keep separate` viene usata quando due atleti simili non devono essere fusi.

La regola piu importante e:

```text
same_context_different_score_keep_separate
```

Se un merge produrrebbe due result nello stesso contesto sportivo ma con score o `D_score` diversi, il sistema deve raccomandare `keep separate`.

Per "stesso contesto sportivo" si intende una combinazione sostanzialmente uguale di:

- evento;
- anno;
- disciplina;
- categoria;
- apparatus;
- format;
- round;
- day;
- vault attempt.

Questa regola evita di fondere due persone diverse solo per somiglianza del nome. E stata applicata in piu anni, ad esempio nei casi post-decisione 2019, 2020, 2021, 2022, 2023, 2024 e 2025.

### 7.3 Country canonica

La decisione `canonical country` indica che una country presente nel file e considerata errore di data entry. In questo caso il sistema corregge la country rappresentata nei result interessati e mantiene una country canonica coerente per l'atleta.

Questa regola si applica quando:

- una country e chiaramente sbagliata;
- gli anni successivi confermano una sola country stabile;
- il contesto delle gare non supporta un reale cambio di nazionalita;
- il caso appare come errore di inserimento nel foglio sorgente.

### 7.4 Country history

La decisione `country history` indica che la differenza di country e storicamente significativa. In questo caso:

- il result conserva la country rappresentata in gara;
- la scheda atleta mantiene la country finale/corrente indicata dall'admin;
- la storia country resta semanticamente tracciabile.

Questa distinzione e importante per non cancellare il dato storico di rappresentanza sportiva.

### 7.5 Riuso delle decisioni same-country

Durante il popolamento e stata introdotta una regola di efficienza:

```text
same_country_review_reuse
```

Le decisioni admin gia verificate possono essere riusate come raccomandazione forte solo quando il country non cambia. Se il country cambia, la review manuale resta obbligatoria.

Questa regola riduce il numero di collisioni ripetitive negli anni successivi, ma mantiene controllo umano sui casi potenzialmente piu delicati.

### 7.6 Ordine nome/cognome

Quando il tool rileva che due varianti differiscono solo per ordine di nome e cognome, la regola adottata e il merge automatico come stesso atleta. La forma canonica viene scelta privilegiando l'ordine che compare piu spesso nei result e, quando necessario, verificando gli anni successivi.

Questo ha evitato di trasformare semplici inversioni in collisioni manuali inutili.

### 7.7 Correzioni del nome atleta

Dal flusso 2021 e stato introdotto il supporto a `target_name_update`. Quando l'admin conferma che un atleta importato corrisponde a un atleta gia presente ma il nome gia salvato nel database e errato, il sistema puo correggere la scheda atleta esistente.

Esempi documentati nel progetto includono:

- `Hirohito Obama` corretto in `Hirohito Kohama`;
- `Dawiel Carrion` corretto in `Daniel Carrion`;
- `Yuta Sasaki` corretto in `Yutaro Sasaki`;
- `Ai Takada` corretto in `Airi Takada`;
- varianti coreane con trattini o spazi normalizzate quando l'evidenza era sufficiente;
- `Niccolo Martin` corretto in `Niccolò Martin`.

Le correzioni non univoche non vengono applicate automaticamente.

---

## 8. Gestione dei dati incompleti

Il formato Gymternet legacy non contiene sempre tutte le componenti del punteggio. La metodologia adottata distingue tra dati mancanti, dati non disponibili e dati non importabili.

### 8.1 Result con final score ma senza D-score

I result con final score disponibile ma `D_score` mancante sono stati importati come result parziali. Questa scelta conserva l'informazione principale sulla performance, cioe il punteggio finale, marcando pero la componente mancante.

Questi result sono utili per:

- classifiche;
- andamento del final score nel tempo;
- schede atleta;
- statistiche aggregate basate sul punteggio finale.

Sono invece da usare con cautela nelle analisi specifiche sulla difficolta.

### 8.2 D-score orfani

I `D_score` senza final score agganciabile non sono stati importati come result autonomi nel database operativo.

La ragione e metodologica: un solo `D_score` non descrive la performance completa dell'atleta e potrebbe alterare medie e grafici sulla difficolta nel tempo se non collegato a un result reale.

Tuttavia, questi dati non sono stati eliminati. Sono stati conservati nei file:

```text
docs/import_reports/gymternet_YYYY_orphan_dscores.csv
```

In questo modo potranno essere recuperati in futuro, se sara possibile collegarli correttamente a result con final score.

### 8.3 E-score, penalty e bonus

Per i file legacy 2018-2025, `E_score`, penalty e bonus non sono registrati in modo completo.

La regola adottata e:

- non inventare valori;
- non trasformare un dato mancante in zero;
- distinguere tra valore realmente nullo e valore non disponibile;
- mostrare in UI un avviso quando un valore e stimato o incompleto.

Nel data entry manuale e negli import futuri non-Gymternet, invece, se l'admin lascia penalty o bonus vuoti in un contesto in cui il dato e dichiarato come disponibile, questi campi possono essere interpretati come zero secondo le regole specifiche del flusso manuale.

### 8.4 Estimated execution

Per alcuni result e possibile stimare una componente di esecuzione sottraendo il `D_score` dal final score. Questa stima non equivale sempre all'E-score ufficiale, perche puo includere penalty o bonus non registrati.

Per questo motivo i result con execution stimata sono marcati e devono essere accompagnati da un alert UI del tipo:

```text
Esecuzione stimata da D score e Final score, che comprende eventuali dati Penalties non disponibili.
```

Nel 2025 e negli anni successivi importati ancora con tool Gymternet legacy, l'alert deve considerare anche l'eventuale bonus non registrato quando previsto dal regolamento.

### 8.5 Vault, VT AVG e VT SUM

Il vault ha richiesto regole specifiche.

Nel database LEVERAGE:

- `VT` resta un apparatus valido;
- `VT AVG` resta un apparatus valido;
- `VT SUM` non e un apparatus salvato nel database, ma una colonna sorgente usata dal tool;
- il campo `vt_attempt` viene mantenuto per distinguere eventuali tentativi;
- quando l'ordine dei vault non e certo, il result viene marcato con `vault_attempt_order_uncertain=true`.

Per i dati Gymternet legacy fino al 2024, il tool puo ricostruire alcuni valori di vault secondo le regole storiche. Dal 2025 in poi, se si usa ancora il tool Gymternet legacy, si applicano le regole 2025, piu caute per WAG e per bonus non registrati.

L'interfaccia dovra mostrare un alert sui vault derivati, ad esempio:

```text
Si noti che Vault 1 puo riferirsi a Vault 2 e viceversa.
```

---

## 9. Controlli di qualita e sicurezza dell'import

Ogni anno e stato validato con piu livelli di controllo.

### 9.1 Controllo duplicati identici

I duplicati identici interni al file sorgente vengono rilevati e saltati. Questo impedisce di importare due volte la stessa riga.

### 9.2 Controllo conflitti bloccanti

I conflitti bloccanti impediscono il commit reale finche non vengono risolti. Esempi:

- stesso contesto sportivo con valori incompatibili;
- collisione atleta non risolta;
- country incongruente senza decisione admin;
- decisioni mancanti o non valide.

### 9.3 Preview post-decisione

Dopo la review admin, il sistema non procede direttamente al commit. Esegue prima una nuova preview applicando le decisioni su una copia temporanea del database.

Questa fase ha spesso intercettato merge che sembravano plausibili ma avrebbero prodotto conflitti. In questi casi le decisioni sono state corrette prima del commit reale.

### 9.4 Controllo duplicati semantici

Dopo il commit viene controllata la presenza di duplicati semantici, cioe gruppi di result che condividono lo stesso contesto sportivo e potrebbero indicare un errore di import.

Al termine del popolamento 2018-2025, ogni commit annuale e stato chiuso con:

```text
semantic_duplicate_groups = 0
```

### 9.5 Backup

Prima dei commit reali sono stati creati backup del database. Questa scelta consente di tornare allo stato precedente in caso di import errato o comportamento inatteso.

### 9.6 Test backend

Dopo il completamento del popolamento storico 2018-2025 e stata eseguita la test suite backend.

Esito finale registrato:

```text
108 passed
```

---

## 10. Risultati quantitativi dell'import storico

La tabella seguente riassume i principali risultati dei commit annuali. I valori indicano cio che e stato creato dal commit di ciascun file sorgente, non necessariamente la distribuzione finale per anno evento, perche alcuni file contengono eventi dell'anno successivo.

| File importato | Athlete creati | Event creati | Result creati | Result completi | Result parziali | D-score orfani non importati | Duplicati semantici post-import |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2018 | 7.134 | 211 | 89.988 | 62.105 | 27.883 | 1.202 | 0 |
| 2019 | 4.211 | 234 | 106.633 | 73.802 | 32.831 | 958 | 0 |
| 2020 | 885 | 76 | 33.777 | 20.887 | 12.890 | 696 | 0 |
| 2021 | 2.727 | 196 | 77.423 | 50.565 | 26.858 | 1.341 | 0 |
| 2022 | 2.472 | 219 | 97.934 | 74.032 | 23.902 | 1.426 | 0 |
| 2023 | 3.384 | 241 | 117.489 | 86.900 | 30.589 | 1.454 | 0 |
| 2024 | 2.535 | 206 | 106.449 | 78.334 | 28.115 | 1.113 | 0 |
| 2025 | 2.911 | 222 | 124.030 | 95.229 | 28.801 | 630 | 0 |

Al termine del commit 2025, lo stato complessivo del database locale era:

| Entita | Conteggio |
|---|---:|
| Athlete | 26.259 |
| Event | 1.605 |
| Result | 753.723 |
| Notification | 0 |

La distribuzione finale dei result per anno evento era:

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

La presenza di 108 result nel 2026 deriva dal file `Results 2025.xlsx`, che contiene il caso `Top 12 Series 3 (2026)`. Quando sara importato il file 2026, questi record dovranno essere considerati dal preflight come gia presenti o potenzialmente duplicati.

---

## 11. Tracciabilita e riproducibilita

Il popolamento e stato reso tracciabile con tre livelli di documentazione.

### 11.1 Documentazione narrativa

Il documento principale e:

```text
docs/LEVERAGE_popolamento_massivo_diario.md
```

Esiste anche una copia Word:

```text
docs/LEVERAGE_popolamento_massivo_diario.docx
```

Questo diario registra anno per anno:

- file sorgente;
- preview;
- collisioni;
- decisioni admin;
- correzioni;
- commit;
- backup;
- controlli post-import;
- osservazioni metodologiche.

### 11.2 Report tecnici

La cartella:

```text
docs/import_reports/
```

contiene CSV e JSON prodotti dagli script di import. Questi file permettono di ricostruire il processo tecnico in modo piu granulare rispetto alla documentazione narrativa.

### 11.3 Versionamento Git

Ogni fase rilevante e stata salvata su Git e poi pubblicata su GitHub. Al termine del popolamento storico e stato creato e pushato il tag:

```text
v0.2.0-historical-import-2018-2025
```

Questo tag rappresenta la fotografia stabile del progetto dopo l'import storico 2018-2025.

---

## 12. Valore metodologico del processo

La metodologia adottata ha prodotto benefici su quattro dimensioni.

### 12.1 Qualita del dato

Il sistema non si limita a importare righe. Valuta coerenza sportiva, identita atleta, country, duplicati, incompletezza e possibili errori di data entry.

### 12.2 Controllo umano

L'admin resta responsabile delle decisioni ambigue. Il sistema suggerisce, segnala e precompila quando possibile, ma non sostituisce la validazione umana nei casi critici.

### 12.3 Auditabilita

Ogni decisione importante e documentata. In futuro sara possibile sapere perche un atleta e stato fuso, separato, corretto o collegato a una specifica country.

### 12.4 Scalabilita del processo

Il metodo e riutilizzabile per nuovi anni o nuovi tool di import. Le regole apprese durante il popolamento 2018-2025 riducono la fatica manuale negli import successivi senza compromettere la sicurezza semantica.

---

## 13. Limiti del popolamento storico

Il popolamento 2018-2025 presenta limiti legati alla natura della fonte legacy.

I principali sono:

- assenza completa o parziale di `E_score`, penalty e bonus;
- presenza di `D_score` orfani non agganciabili automaticamente;
- necessita di interpretazioni specifiche per il vault;
- alcuni result 2025 senza final score quando il dato non e ricostruibile in modo affidabile;
- necessita di review manuale per collisioni atleta/country;
- possibili variazioni di naming dovute a traslitterazioni, refusi o inversioni nome/cognome.

Questi limiti non sono stati nascosti. Sono stati modellati nel backend tramite campi, flag, alert e report, in modo che l'interfaccia futura possa mostrare all'utente quando un dato e completo, parziale, stimato o non disponibile.

---

## 14. Prospettive future

Il popolamento storico 2018-2025 costituisce la base dati iniziale di LEVERAGE. I prossimi sviluppi previsti riguardano:

- import del primo semestre 2026 fino al 01/07/2026;
- eventuale nuovo standard Gymternet dal 2026 in poi con componenti complete del punteggio;
- import parallelo non-Gymternet con controllo obbligatorio `D + E + B - P = final score`;
- interfaccia admin per review guidata dei problemi di import;
- dashboard utente con classifiche, filtri, grafici e confronti;
- schede atleta con trend, diagrammi per apparatus e link World Gymnastics;
- schede evento con classifiche filtrabili e statistiche aggregate;
- indicatori visivi per dati incompleti, stimati o soggetti a cautela interpretativa.

Il modello attuale e gia predisposto per mantenere piu tool di import in parallelo. Il tool Gymternet legacy puo continuare a essere usato per dati in formato storico, mentre un futuro tool standardizzato potra applicare regole piu severe sui dati completi.

---

## 15. Conclusione

Il popolamento massivo del database LEVERAGE e stato condotto come un processo controllato di ingegneria del dato. La fase non si e limitata alla conversione di file Excel in record SQL, ma ha richiesto progettazione di regole, gestione delle ambiguita, controllo umano, validazione automatica e documentazione.

Il risultato e un database locale contenente 753.723 result, 26.259 atleti e 1.605 eventi, costruito a partire dai dati storici Gymternet 2018-2025 e chiuso senza duplicati semantici rilevati nei controlli finali.

La metodologia adottata rende il dataset iniziale di LEVERAGE non soltanto ampio, ma anche verificabile, versionato e pronto per supportare lo sviluppo dell'interfaccia utente, delle analisi statistiche e della piattaforma web finale.
