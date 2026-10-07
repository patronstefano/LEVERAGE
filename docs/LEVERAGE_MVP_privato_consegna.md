# LEVERAGE - Consegna MVP privato

Data: 7 ottobre 2026. Versione di consegna: `v1.0.0-mvp-private`.

## Perimetro

Versione locale privata per dimostrazione e tesi, non un rilascio pubblico.
Home, Atleti, Eventi, Rankings, Analytics, Area Personale, Centro Admin e
Centro Super Admin sono inclusi. L'utente ha confermato il collaudo degli
import incrementali Results/Calendar, di Audit e Ripristino e dei tre ruoli.

I pulsanti DEMO USER/ADMIN/SUPER ADMIN e i generatori notifiche DEMO restano
disponibili per scelta esplicita. Gli accessi demo possono modificare il
database: usare una copia ripristinata per dimostrazioni distruttive.
Le notifiche dei generatori sono fittizie e non sostituiscono quelle
persistenti prodotte dalle operazioni reali. Email reali e codice di accesso
via email restano rinviati. Non esporre questa configurazione su Internet.

## Avvio sulla macchina attuale

Aprire due terminali nella cartella del progetto:
`/Users/patronstefano/Sviluppo/LEVERAGE`.

Terminale backend:

```bash
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Terminale frontend:

```bash
.venv/bin/python -m http.server 5173 --bind 127.0.0.1 --directory frontend
```

Aprire <http://127.0.0.1:5173/>. Documentazione API:
<http://127.0.0.1:8000/docs>. I processi devono rimanere attivi; `Ctrl+C`
arresta il processo del rispettivo terminale. Se la preview e gia funzionante,
non avviare una seconda copia. Se la porta frontend e occupata da un altro
servizio, usare 5174, gia ammessa dal CORS locale.

La configurazione privata richiede `APP_ENV=development`. Il file `.env`
non e versionato e non deve essere pubblicato. Per il database corrente:
`DATABASE_URL=sqlite:///./leverage.db`. La versione congelata usa la
migrazione `0043_entity_reviews`; non serve ricreare il database o eseguire
importazioni per avviare la copia consegnata.

Le scansioni World Gymnastics possono riprendere all'avvio se erano attive
nel database. Per una dimostrazione senza scansioni, sospenderle dalla
sezione World Gymnastics prima di chiudere l'applicazione. Il completamento
della scansione massiva non e un requisito per consultare il MVP.

## Materiale della consegna locale

Cartella riservata, esclusa da Git: `private_releases/mvp-private-20261007/`.

- `backup/leverage.db`: snapshot consistente, incluse le scritture WAL confermate.
- `backup/uploads/`: immagini e altri caricamenti locali.
- `backup/import_files/`: file sorgente Gymternet e Calendar disponibili.
- `backup/manifest.json`: SHA-256 di ciascun file, dimensioni, schema e conteggi.
- `restore-check/`: copia ripristinata identica, verificata prima dell'avvio.
- `runtime-check/`: copia di prova usata per accessi DEMO e letture API.
- `runtime-check/smoke-report.json`: risultati delle prove sulla copia.
- `code-v1.0.0-mvp-private.tar.gz`: codice versionato al tag finale.
- `requirements.snapshot.txt`: versioni installate nella macchina di consegna.
- `release-manifest.json`: tag/commit e checksum degli artefatti di consegna.

Il database include account, preferiti, audit e dati di autenticazione: non
condividerlo pubblicamente. La cartella non include `.env`, segreti esterni,
ambienti virtuali, cache browser o vecchi backup. GitHub conserva codice e
documentazione, NON questo backup. La copia sullo stesso disco non protegge
dal guasto del computer: trasferire l'intera cartella anche su un supporto
esterno protetto.

## Verifica e ripristino non distruttivo

```bash
.venv/bin/python scripts/private_mvp_backup.py verify private_releases/mvp-private-20261007/backup
.venv/bin/python scripts/private_mvp_backup.py restore private_releases/mvp-private-20261007/backup --output private_releases/nuova-copia
```

Il ripristino rifiuta cartelle gia esistenti e non sovrascrive il database
attuale. Verifica inventario, checksum, `integrity_check`, chiavi esterne,
migrazione e conteggi di tutte le tabelle. I checksum rilevano corruzioni
accidentali: non costituiscono una firma crittografica di autenticita.

Per ripetere anche avvio e verifiche dei tre ruoli su una nuova copia:

```bash
.venv/bin/python scripts/check_private_mvp_restore.py private_releases/mvp-private-20261007/backup --output private_releases/nuovo-collaudo
```

Il comando ripristina tutti i file in una cartella nuova, disattiva le
scansioni SOLO nella copia e prova l'applicazione tramite TestClient con
il suo ciclo di avvio/arresto. Non chiama il server della preview e non
conferma importazioni. La copia viene modificata dalle sessioni demo e dai
reminder: il suo manifest originale non descrive piu il database dopo il
collaudo; il backup di partenza rimane immutato.

Per una prova manuale separata, estrarre il codice in una nuova cartella,
ripristinare il backup in una diversa cartella vuota e aggiungervi i file
del codice, senza sovrascrivere database o asset. Avviare da quella cartella
con ambiente virtuale dedicato e `.env` locale. Non puntare la prova al
database originale.

## Nuovi backup

```bash
.venv/bin/python scripts/private_mvp_backup.py create --database leverage.db --output private_releases/nuovo-backup --include uploads --include import_files
```

Usare sempre una destinazione nuova. Durante la copia non caricare o
modificare immagini e file sorgente: il database ha uno snapshot SQLite
consistente, ma database e filesystem non costituiscono una transazione unica.
La procedura rifiuta symlink e backup con chiavi esterne non valide.

Non copiare il solo `leverage.db` mentre il backend e attivo: con WAL si
possono perdere scritture gia confermate. Per la consegna usare questo
strumento, non le funzioni di copia semplice presenti negli script storici
di importazione/riparazione. Non cancellare manualmente file `-wal`/`-shm`.

## Ambiente e riproducibilita

Il progetto dichiara Python 3.10+ in `pyproject.toml`. L'ambiente locale
storico effettivamente collaudato usa Python 3.9.6 su macOS: questa differenza
e documentata, non e una prova su tutte le versioni Python. Per una nuova
macchina usare Python 3.10+ e verificare installazione e test in un ambiente
dedicato; non copiare `.venv` tra macchine.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pytest -q
```

La suite pytest forza un database temporaneo separato e rifiuta l'uso del
database di lavoro. `alembic upgrade head` serve per un database nuovo vuoto,
non per ricreare i dati della consegna: per quelli ripristinare il backup.
`requirements.txt` ha limiti minimi, non e un lockfile;
`requirements.snapshot.txt` descrive le versioni dell'ambiente verificato.
Preparare `.env` usando `.env.example`, con una chiave segreta locale non
pubblicata; SMTP puo restare vuoto per la dimostrazione con soli utenti DEMO.

I test UI richiedono anche Playwright e Chromium, non necessari per usare
la preview. Le prove UI con API simulate non dimostrano l'invio reale di
email o l'accessibilita di World Gymnastics. La prova di ripristino usa il
backend reale con una copia del database.

## Prima di una pubblicazione futura

Disabilitare gli accessi DEMO anche lato backend, rimuovere i generatori,
configurare e collaudare autenticazione ed email reali, verificare HTTPS,
segreti, backup esterni, autorizzazioni e configurazione di produzione.
Questi passaggi NON fanno parte del MVP privato qui consegnato.

## Verifiche della consegna

Il 7 ottobre 2026 sono passati 412 test pytest e i seguenti controlli browser:
`check_admin_ui.py`, `check_account_ui.py`, `check_auth_validation_ui.py`,
`check_section_navigation_ui.py`, `check_import_progress_ui.py`.
Le verifiche comprendono viste desktop/mobile, permessi simulati, moduli,
navigazione e avanzamento import; non sono una garanzia di assenza di bug.

La prova separata `check_private_mvp_restore.py` ha usato il backend reale
e il database ripristinato, verificando accessi DEMO dei tre ruoli,
autorizzazioni e consultazione dei dati. Nessuna importazione e stata
confermata nel database di lavoro. Snapshot: 575 file, integrita SQLite
`ok`, zero violazioni delle chiavi esterne; conteggi delle tabelle sportive
invariati dopo le prove sulla copia.
