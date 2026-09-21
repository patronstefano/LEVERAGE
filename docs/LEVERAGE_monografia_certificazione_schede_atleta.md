# LEVERAGE - Certificazione controllata delle Schede Atleta

## 1. Finalita della funzionalita

LEVERAGE introduce un meccanismo di certificazione pubblica delle Schede Atleta fondato sul riscontro controllato con una fonte istituzionale, World Gymnastics. La funzionalita e rappresentata nella UI da un badge blu LEVERAGE con spunta bianca, mostrato nel sottotitolo dell'atleta immediatamente a destra della disciplina MAG/WAG.

Il badge non e un semplice elemento estetico. Esprime uno stato persistente dell'entita `Athlete` e comunica che un utente con ruolo `admin` o `super_admin` ha:

1. avviato la ricerca di un profilo ufficiale World Gymnastics;
2. individuato e valutato un profilo compatibile con la scheda LEVERAGE;
3. selezionato esplicitamente quel riscontro;
4. confermato l'azione `Importa dati`.

La certificazione collega quindi identita digitale, fonte ufficiale, decisione umana e tracciabilita amministrativa.

## 2. Significato semantico e limiti

Il badge certifica il matching controllato tra la Scheda Atleta LEVERAGE e un profilo atleta ufficiale World Gymnastics. Non deve essere interpretato come:

- certificazione automatica di ogni singolo dato anagrafico;
- certificazione di tutti i risultati sportivi associati all'atleta;
- approvazione, partnership o endorsement di LEVERAGE da parte di World Gymnastics;
- sostituzione della revisione umana dei dati suggeriti.

I valori importati dal profilo ufficiale continuano infatti a essere trattati come suggerimenti in attesa di approvazione. L'Admin puo accettarli, modificarli o rifiutarli separatamente. Il badge attesta il riscontro dell'identita e l'avvio consapevole del flusso di importazione, mentre la pubblicazione dei singoli valori resta soggetta alla governance ordinaria di LEVERAGE.

Questa distinzione evita di confondere tre livelli differenti:

- `ricerca`: individua candidati ma non modifica lo stato di certificazione;
- `importazione`: conferma il profilo scelto, assegna il badge e genera i suggerimenti;
- `approvazione dati`: decide quali valori suggeriti entrano effettivamente nella scheda pubblica.

## 3. Flusso operativo

### 3.1 Ricerca automatica

L'Admin apre gli strumenti della Scheda Atleta e avvia `Ricerca automatica`. LEVERAGE usa i dati gia disponibili, come nome, country e disciplina, per proporre candidati World Gymnastics e mostrare compatibilita ed eventuali warning.

La sola visualizzazione dei candidati non assegna il badge.

### 3.2 Ricerca manuale

L'Admin puo inserire un FIG ID oppure l'URL di un profilo ufficiale. `Ricerca manuale` recupera e mostra il profilo trovato, ma mantiene invariato `is_profile_verified`.

Anche questo percorso richiede la conferma successiva `Importa dati`.

### 3.3 Importazione e certificazione

Quando l'Admin seleziona il profilo e preme `Importa dati`, il backend:

- verifica nuovamente il profilo World Gymnastics indicato;
- crea i suggerimenti disponibili con stato pending;
- imposta `Athlete.is_profile_verified = true`;
- imposta contestualmente `world_gymnastics_verified_at` e `world_gymnastics_verified_by_admin_id`;
- registra l'operazione nell'audit amministrativo;
- aggiorna la Scheda Atleta senza ricaricare l'intera pagina;
- mostra pubblicamente il badge blu LEVERAGE nel sottotitolo della Scheda Atleta, accanto alla disciplina MAG/WAG.

Questa e la transizione che certifica il matching dell'identita. La successiva accettazione, modifica o esclusione dei singoli suggerimenti decide soltanto quali valori entrano nella Scheda Atleta e non ridefinisce ne la data ne l'Admin della certificazione.

Il normale endpoint di modifica anagrafica non accetta il campo di certificazione. Il badge non puo quindi essere attribuito liberamente dal form di editing o da un pulsante indipendente dal riscontro ufficiale.

## 4. Modello dati e implementazione

La certificazione e memorizzata nel booleano persistente:

```text
Athlete.is_profile_verified
```

Il campo e stato introdotto dalla migrazione Alembic `0037_add_athlete_profile_verification` con valore predefinito `false`, preservando la compatibilita con tutti gli atleti storici gia presenti nel database.

Per le schede collegate e approvate prima dell'introduzione del booleano e stata aggiunta la migrazione dati `0038_backfill_verified_athlete_profiles`. Il riallineamento assegna il badge soltanto se la scheda contiene congiuntamente URL del profilo ufficiale, data di verifica e identificativo dell'Admin verificatore. Il solo URL non e considerato sufficiente per inferire retroattivamente una certificazione.

La migrazione correttiva `0039_repair_verified_athlete_audit` interviene esclusivamente sulle certificazioni gia attive ma prive di timestamp o Admin. I valori vengono ricostruiti soltanto quando il log storico contiene una transizione documentata `is_profile_verified: false -> true`; in assenza di tale evidenza, la migrazione non attribuisce informazioni.

Le responsabilita sono distribuite come segue:

- `app/models.py`: persistenza del booleano sull'entita `Athlete`;
- `app/schemas.py`: esposizione pubblica dello stato, esclusione dal normale payload di modifica;
- `app/routers/world_gymnastics.py`: assegnazione esclusiva durante l'importazione del profilo ufficiale;
- `app/routers/data_suggestions.py`: approvazione separata dei valori proposti, senza modifica dei metadati della certificazione atleta;
- `app/audit.py`: registrazione della variazione e supporto alla revisione Super Admin;
- `frontend/app.js`: flusso ricerca-preview-importazione e rendering condizionale del badge;
- `frontend/styles.css`: rappresentazione del contrassegno nel blu identificativo LEVERAGE;
- `tests/test_api.py`: verifica automatica dei permessi e delle transizioni di stato.

## 5. Governance, sicurezza e privacy

La funzionalita applica diversi controlli:

- ricerca e importazione World Gymnastics sono riservate ad Admin e Super Admin;
- la ricerca senza importazione lascia il badge disattivato;
- il form anagrafico ordinario non puo impostare `is_profile_verified`;
- badge, timestamp e Admin verificatore sono assegnati atomicamente da `Importa dati`;
- l'assegnazione e registrata nell'audit con stato coerente al ruolo dell'operatore;
- l'approvazione dei singoli suggerimenti non sovrascrive i metadati del matching certificato;
- una certificazione gia presente viene preservata se una scheda duplicata e incorporata nella scheda canonica tramite merge;
- `world_gymnastics_verified_by_admin_id` non e esposto nelle API pubbliche;
- l'identificativo dell'Admin verificatore e disponibile soltanto nella vista protetta `admin-view` e nel relativo box riservato ad Admin/Super Admin.

Queste regole rendono la certificazione verificabile, non arbitraria e coerente con il modello di sicurezza gia adottato per le altre modifiche amministrative.

## 6. Valore per LEVERAGE

Dal punto di vista dell'utente, il badge riduce l'ambiguita tra omonimi, traslitterazioni, errori ortografici e cambi di nazionalita. Dal punto di vista della piattaforma, introduce un segnale sintetico di data provenance: la Scheda Atleta non e soltanto presente nel database, ma e stata collegata consapevolmente a un riferimento istituzionale.

La funzionalita e particolarmente rilevante per LEVERAGE perche il progetto integra dati storici provenienti da fonti eterogenee. Il badge crea un livello ulteriore di fiducia senza eliminare il principio human-in-the-loop: l'automazione ricerca e prepara, mentre la decisione resta umana e tracciata.

L'elemento innovativo non risiede quindi nella sola icona, ma nell'architettura che la sostiene:

- fonte istituzionale;
- matching assistito;
- decisione Admin esplicita;
- separazione tra certificazione dell'identita e approvazione dei singoli campi;
- audit e supervisione Super Admin;
- comunicazione pubblica immediata e comprensibile.

## 7. Manutenzione e revoca della certificazione

### 7.1 Invariante di sicurezza

LEVERAGE separa strutturalmente i dati World Gymnastics dalla normale anagrafica. Il blocco dedicato compare nella sezione `Modifica atleta` soltanto quando esiste gia un collegamento ufficiale e consente di amministrare FIG ID, URL e status senza esporre il campo booleano della certificazione. Ne deriva il seguente invariante: **il badge non puo essere attribuito o riattribuito mediante modifica manuale, endpoint anagrafico ordinario o semplice inserimento di un URL**. Dopo una revoca o una variazione dell'identita FIG, la certificazione puo essere ripristinata esclusivamente selezionando nuovamente un profilo World Gymnastics riscontrato e confermando `Importa dati`.

Questo vincolo impedisce che un Admin possa trasformare un collegamento scritto manualmente in una certificazione pubblica senza una nuova verifica della fonte. Le operazioni amministrative che modificano lo stato della certificazione o dei dati World Gymnastics sono registrate nell'audit; le operazioni di sola ricerca e preview sono protette dai ruoli ma non producono una voce `AuditLog`.

### 7.2 Modifica e revoca controllate

La certificazione non e irreversibile. Dopo il collegamento iniziale, gli utenti Admin e Super Admin possono correggere FIG ID, URL del profilo e status World Gymnastics attraverso campi dedicati nella sezione `Modifica atleta`. La piattaforma applica tuttavia una distinzione semantica precisa: lo status descrive una condizione del profilo e puo cambiare senza alterarne l'identita; FIG ID e URL identificano invece la fonte ufficiale certificata. La modifica manuale di uno di questi ultimi campi revoca pertanto in modo automatico il badge, la data di verifica e il riferimento all'Admin verificatore.

E inoltre disponibile una revoca esplicita del solo badge, che conserva FIG ID, URL e status per non perdere il collegamento informativo. Ogni modifica o revoca genera una voce di audit. Per ripristinare il badge non e sufficiente intervenire manualmente sul booleano: l'Admin deve selezionare nuovamente un profilo ufficiale riscontrato e confermare `Importa dati`. Questo ciclo rende la certificazione correggibile nel tempo senza indebolirne il significato metodologico.

## 8. Evidenze nel repository GitHub

La versione definitiva del flusso automatico e verificabile nel repository pubblico:

- repository: `https://github.com/patronstefano/LEVERAGE`;
- commit applicativo principale: `39ac3591ca534d34d4fd56a5fce71d6192dab8a8`;
- messaggio commit: `Assign athlete badge from World Gymnastics import`.

Commit collegati:

- `9f62586`: introduzione del campo persistente, migrazione, badge UI e controlli iniziali;
- `178c531`: protezione del metadato relativo all'Admin verificatore;
- `39ac359`: rimozione dell'assegnazione manuale e collegamento definitivo del badge all'azione `Importa dati` del flusso World Gymnastics.
- `8fd7976`: separazione dei dati World Gymnastics dall'anagrafica ordinaria, manutenzione protetta, revoca esplicita e revoca automatica in caso di modifica dell'identita FIG.
- `452125b`: collocazione pubblica del badge accanto alla disciplina MAG/WAG e aggiornamento degli asset frontend.
- `c9f6fc2`: registrazione atomica e recupero da audit di data e Admin della ri-certificazione.

I commit `39ac359` e `8fd7976` rappresentano congiuntamente la decisione semantica e di sicurezza definitiva: nessun badge per la sola ricerca, nessuna assegnazione libera dal form e nessuna riattivazione manuale dopo una revoca; certificazione soltanto dopo la selezione e l'importazione esplicita di un profilo ufficiale riscontrato.

## 9. Formula sintetica utilizzabile nella monografia

LEVERAGE adotta un meccanismo di certificazione controllata delle Schede Atleta: il badge pubblico viene assegnato esclusivamente quando un amministratore seleziona e importa un profilo ufficiale World Gymnastics riscontrato. La ricerca preliminare non altera lo stato della scheda e i singoli dati importati rimangono soggetti ad approvazione separata. La certificazione attesta pertanto il matching dell'identita e la provenienza istituzionale del riferimento, non un'approvazione generalizzata di tutti i dati ne un endorsement da parte della federazione. L'intera transizione e persistente, auditabile e protetta da ruoli amministrativi.
