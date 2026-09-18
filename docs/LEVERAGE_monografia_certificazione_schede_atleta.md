# LEVERAGE - Certificazione controllata delle Schede Atleta

## 1. Finalita della funzionalita

LEVERAGE introduce un meccanismo di certificazione pubblica delle Schede Atleta fondato sul riscontro controllato con una fonte istituzionale, World Gymnastics. La funzionalita e rappresentata nella UI da un badge blu LEVERAGE con spunta bianca, mostrato sotto il nome dell'atleta.

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
- registra l'operazione nell'audit amministrativo;
- aggiorna la Scheda Atleta senza ricaricare l'intera pagina;
- mostra pubblicamente il badge blu LEVERAGE sotto il nome.

Il normale endpoint di modifica anagrafica non accetta il campo di certificazione. Il badge non puo quindi essere attribuito liberamente dal form di editing o da un pulsante indipendente dal riscontro ufficiale.

## 4. Modello dati e implementazione

La certificazione e memorizzata nel booleano persistente:

```text
Athlete.is_profile_verified
```

Il campo e stato introdotto dalla migrazione Alembic `0037_add_athlete_profile_verification` con valore predefinito `false`, preservando la compatibilita con tutti gli atleti storici gia presenti nel database.

Per le schede collegate e approvate prima dell'introduzione del booleano e stata aggiunta la migrazione dati `0038_backfill_verified_athlete_profiles`. Il riallineamento assegna il badge soltanto se la scheda contiene congiuntamente URL del profilo ufficiale, data di verifica e identificativo dell'Admin verificatore. Il solo URL non e considerato sufficiente per inferire retroattivamente una certificazione.

Le responsabilita sono distribuite come segue:

- `app/models.py`: persistenza del booleano sull'entita `Athlete`;
- `app/schemas.py`: esposizione pubblica dello stato, esclusione dal normale payload di modifica;
- `app/routers/world_gymnastics.py`: assegnazione esclusiva durante l'importazione del profilo ufficiale;
- `app/audit.py`: registrazione della variazione e supporto alla revisione Super Admin;
- `frontend/app.js`: flusso ricerca-preview-importazione e rendering condizionale del badge;
- `frontend/styles.css`: rappresentazione del contrassegno nel blu identificativo LEVERAGE;
- `tests/test_api.py`: verifica automatica dei permessi e delle transizioni di stato.

## 5. Governance, sicurezza e privacy

La funzionalita applica diversi controlli:

- ricerca e importazione World Gymnastics sono riservate ad Admin e Super Admin;
- la ricerca senza importazione lascia il badge disattivato;
- il form anagrafico ordinario non puo impostare `is_profile_verified`;
- l'assegnazione e registrata nell'audit con stato coerente al ruolo dell'operatore;
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

## 7. Evidenze nel repository GitHub

La versione definitiva del flusso automatico e verificabile nel repository pubblico:

- repository: `https://github.com/patronstefano/LEVERAGE`;
- commit applicativo principale: `39ac3591ca534d34d4fd56a5fce71d6192dab8a8`;
- messaggio commit: `Assign athlete badge from World Gymnastics import`.

Commit collegati:

- `9f62586`: introduzione del campo persistente, migrazione, badge UI e controlli iniziali;
- `178c531`: protezione del metadato relativo all'Admin verificatore;
- `39ac359`: rimozione dell'assegnazione manuale e collegamento definitivo del badge all'azione `Importa dati` del flusso World Gymnastics.

Il commit `39ac359` rappresenta la decisione semantica definitiva: nessun badge per la sola ricerca e nessuna assegnazione libera dal form; certificazione soltanto dopo la selezione e l'importazione esplicita di un profilo ufficiale riscontrato.

## 8. Formula sintetica utilizzabile nella monografia

LEVERAGE adotta un meccanismo di certificazione controllata delle Schede Atleta: il badge pubblico viene assegnato esclusivamente quando un amministratore seleziona e importa un profilo ufficiale World Gymnastics riscontrato. La ricerca preliminare non altera lo stato della scheda e i singoli dati importati rimangono soggetti ad approvazione separata. La certificazione attesta pertanto il matching dell'identita e la provenienza istituzionale del riferimento, non un'approvazione generalizzata di tutti i dati ne un endorsement da parte della federazione. L'intera transizione e persistente, auditabile e protetta da ruoli amministrativi.
