# Centro Admin unificato

Data: 22 settembre 2026. Perimetro: MVP privato locale.

## Aggiornamento Importazione file - 6 ottobre 2026

Eccezione aggiornata: la scelta Gare gia importate ricalcola automaticamente
l'anteprima di risultati e calendario. Le altre decisioni rimangono cumulative;
il cambio di perimetro riconcilia anche le scelte in bozza ancora applicabili.

Le decisioni sono ora accumulate nella bozza locale: selezioni identita,
correzioni ed esclusioni di righe, scarto orfani e rinvio duplicati.
Queste decisioni non attivano ricalcoli automatici.
Al termine, Ricalcola anteprima valida tutte le scelte; il commit resta
disabilitato fino alla validazione senza conflitti bloccanti. I conteggi prima
del ricalcolo descrivono l'ultima analisi, come indicato nell'avviso.
La bozza e mantenuta nella navigazione interna, non dopo un refresh del browser.
Restano i passaggi interni di riconciliazione delle decisioni quando varia il
perimetro o una riga sorgente, eseguiti nella stessa operazione di ricalcolo.

Le Gare da elaborare usano la stessa gerarchia della revisione atleti: nome
da 14 px, metadati/stato in grigio e comandi a destra. ID e Confronta dettagli
sono separati dal nome; i conteggi per classifica e i campioni di punteggio
restano nel dettaglio espandibile.

Per Results e disponibile "Tralascia tutte le revisioni duplicati": dopo
conferma, il parametro `defer_duplicate_reviews` rinvia le identita ancora
senza decisione di atleti ed eventi. Le decisioni esplicite restano valide.
Non equivale a confermare che due entita siano diverse: senza nuove unioni
automatiche, le identita non associate sono importate separatamente con i
rispettivi risultati. Le regole automatiche di identita gia validate non
vengono cambiate. L'opzione si annulla con "Riprendi revisione duplicati"
prima dell'importazione. Non rinvia conflitti di punteggio, errori del file
o D Score orfani, che mantengono i controlli precedenti.

Al commit le coppie effettive sono salvate come `deferred` nella tabella
EntityReviewDecision e rese disponibili in Revisione Duplicati, anche se
il confronto fuzzy ordinario non le ripropone. Il salvataggio avviene nella
stessa transazione dell'import: l'anteprima non scrive. Le coppie rinviate
possono essere confrontate, unite con gli strumenti esistenti o confermate
distinte successivamente. La coda non perde i casi oltre il limite di righe
della risposta di anteprima. Audit dell'import e delle coppie conserva la
scelta; il riepilogo finale indica quante coppie sono state salvate.

Caricamento e ricalcoli condividono la barra di avanzamento: upload percentuale
reale, analisi server indeterminata, completamento animato al 100% solo dopo
la risposta valida. Correzioni e decisioni mantengono la vecchia anteprima
non interagibile fino alla sostituzione. La transizione rispetta il movimento
ridotto; un errore di rete non viene mostrato come completamento. Il 100%
indica analisi conclusa, non assenza di conflitti o avvenuta importazione.
Durante esclusioni e revisioni la barra compare nel popup: viene riutilizzata
la conferma gia aperta oppure mostrato un popup di avanzamento per i ricalcoli
diretti. Non compare una seconda barra dietro la conferma. I pulsanti e la
chiusura con Escape sono sospesi durante l'operazione; dopo il completamento
il popup si chiude. In caso di errore la conferma resta disponibile con il
messaggio, consentendo di riprovare o annullare. Corretti singolare/plurale
della conferma di esclusione nelle quattro lingue.

Il selettore Anno e disponibile anche per Calendar, nello stesso punto del
form Risultati. Se valorizzato, limita preview e commit al foglio XLSX o alle
righe CSV di quell'anno; vuoto mantiene l'intero file. La scelta resta nella
bozza durante la navigazione. Non cambia la soglia separata di creazione degli
eventi mancanti. Il campo "Crea eventi calendario dall'anno" non e piu esposto
nel modulo: il backend mantiene come soglia predefinita l'anno corrente.
Un anno assente dal file viene segnalato e non e importabile.

Anche Calendar offre "Eventi gia presenti in LEVERAGE" con Includi/Tralascia.
Tralascia esclude gli eventi riconosciuti dal matching nome/anno dalla revisione
e dal commit: nessun aggiornamento delle loro date. Un conteggio compatto
riporta gli eventi esclusi; le voci totali del file restano indicate. Tornando
a Includi si ricalcola l'intera anteprima. La scelta passa anche al commit,
che ripete il matching sul database corrente. Eventuali duplicati o periodi
discordanti delle sole righe escluse non bloccano i nuovi eventi; errori di
lettura del file e conflitti dei nuovi eventi rimangono bloccanti. Se tutte
le righe sono escluse, la conferma UI e disabilitata. L'opzione non modifica
la soglia di creazione degli eventi storici mancanti.

L'anteprima Calendar non usa piu report tecnici annidati: duplicati e periodi
discordanti sono righe compatte paginate a sei elementi con nome gara,
foglio/riga, date e link Leverage ID. Il numero dei conflitti e distinto dalle
righe sorgente consultabili. Avvisi del file e diagnostiche localizzate nelle
quattro lingue chiudono l'anteprima. Le date sorgente non interpretabili restano
visibili per riconoscere l'errore. I conflitti bloccano ancora il commit e
richiedono correzione nel file e nuova analisi; nessuna risoluzione automatica.
Il riepilogo Calendar usa tre colonne su desktop e due su schermi ridotti,
con etichette da 13 px e valori da 18 px separati da uno spazio stabile.
Nomi gara da 14 px, metadati da 13 px e interlinea 1,5 rendono uniforme la
lettura delle voci e dei conflitti. I link evento occupano un'area limitata
a destra e passano sotto ai dati su tablet/mobile; testi e nomi file lunghi
vanno a capo senza sovrapporsi ai comandi.

L'anteprima e stata compattata usando gli stessi caratteri, controlli e
separazioni di Revisione Duplicati. Dopo l'analisi il form file/parametri
si chiude ed e riapribile con Cambia file; il file e le opzioni restano in
memoria anche tornando alla sezione. Gymternet presenta tre parti selezionabili:
Revisione Eventi, Revisione Atleti e Revisione Risultati. Ogni parte ha
un recap dedicato su quattro colonne desktop e due mobile. Il numero delle
verifiche pendenti e visibile sui relativi pulsanti; cambiare parte non
sblocca la conferma. I comandi Applica decisioni e
Conferma importazione sono raccolti in un'unica riga finale.

Il ricalcolo conserva pagina, filtro e apertura delle liste gara, oltre
alle scelte delle review. Eliminati i paragrafi ripetitivi; i chiarimenti
sull'identita rimangono nella relativa sezione aperta. Anche Calendar
ha un recap dedicato e una lista di sei gare per pagina con date, azione
prevista e ID associati, invece dell'elenco esteso di campi tecnici.
I conflitti Calendar bloccano il pulsante di conferma come gia previsto
dal backend. Dopo il commit rimane il riepilogo degli esiti; i controlli
di risoluzione non sono piu modificabili. Nessuna regola di parsing,
associazione, scrittura o notifica e cambiata con questa rifinitura UI.

Il primo caricamento Gymternet mostra l'anteprima dell'intero file. Solo dopo
l'analisi, il selettore "Gare gia importate" permette di scegliere Includi o
Tralascia, con ricalcolo automatico del report prima della conferma.
Non e piu presente una spunta nel form di caricamento.

Tralascia esclude le gare gia popolate: corrispondenza univoca nome/anno e
almeno un risultato attivo. Mostra "N gare gia in LEVERAGE", con differenze e
avvisi sorgente sintetizzati in un riepilogo apribile, senza riaprire le vecchie
revisioni. Le gare presenti solo nel calendario restano da importare.
Includi permette di integrare altri round o attrezzi e mantiene tutti i controlli.
Esclusione non significa completezza. La UI usa `skip_existing_events=false`
inizialmente, e true dopo la scelta Tralascia; il commit rivaluta sempre il DB.
Rimosso il banner generico sui dati incoerenti, non le diagnostiche specifiche
ne i blocchi sui dati invalidi inclusi. Le decisioni pertinenti sono conservate
al cambio di perimetro; la conferma resta disabilitata durante il ricalcolo.

Eventi e Atleti distinguono entita gia associate al DB, non ancora associate,
con o senza incongruenze nei punteggi/avvisi sorgente. Le verifiche di identita
sono elencate separatamente; assenza di incongruenze numeriche non certifica
l'identita. Conteggi provvisori fino alle decisioni e al ricalcolo; gli atleti
sono contati una sola volta per identita risolta, anche su piu gare/attrezzi,
non a partire dal campione di risultati. I conteggi atleti riguardano il
perimetro incluso, quelli eventi mostrano anche le gare storiche tralasciate.
Righe non convertibili in risultati e D-score orfani restano nelle rispettive
diagnostiche, non sono inventati come nuove entita.

Il collegamento Revisione Duplicati apre direttamente Atleti o Eventi e
consente di rimandare l'eventuale unione di entita gia presenti; non elude
le decisioni necessarie per assegnare i risultati dell'import corrente.
L'anteprima rimane in memoria tornando a Importazione file, non dopo refresh.

Revisione Risultati contiene una sola lista di punteggi da verificare, con
confronto file/DB e correzioni nello stesso dettaglio. Non esistono piu due
elenchi paralleli per righe del file e punteggi in conflitto. Seguono D-score
orfani e Avvisi del file. Gare, atleti, correzioni e avvisi hanno sei elementi
per pagina. Confronta dettagli apre classifiche, conteggi e un campione di
massimo 20 nuovi risultati per gara. Gli errori sorgente sicuramente riferiti
alle gare escluse non bloccano le nuove importazioni; quelli delle gare incluse
o non attribuibili rimangono bloccanti.

Le possibili corrispondenze di gare nello stesso anno richiedono una decisione
esplicita: associazione alla gara proposta o conferma di gara distinta. Si
affiancano alla review atleta/nazionalita e ai D-score orfani.

La revisione avviene direttamente nell'anteprima: rimosso Scarica report e
l'export automatico in caso di errore. Correggi riga apre i punteggi sorgente
modificabili; Tralascia riga esclude, con conferma, tutti i punteggi di quella
riga, non soltanto l'attrezzo segnalato. Sono disponibili Ripristina riga
originale, Applica decisione, Applica tutte le decisioni selezionate ed
esclusioni cumulative esplicite di righe problematiche o D-score orfani.
Le liste restano paginate; nessuna unione cumulativa implicita di identita.

Ogni correzione viene applicata in memoria prima del parsing, ricalcolando
anche i salti VT derivati. L'impronta della riga originale impedisce di
riapplicare una decisione su una sorgente cambiata. Le righe D-score collegate
sono esposte insieme alle righe Final Score interessate. Nessuna modifica al
file originale o sovrascrittura di risultati gia salvati: per questi ultimi
resta l'Editor Risultati. Le decisioni sono registrate nell'audit del commit.

Conferma importazione si abilita solo dopo il ricalcolo, senza errori,
conflitti o review irrisolte nel perimetro scelto. Rimossa dalla UI l'opzione
import parziale: il frontend invia `require_resolved_reviews=true` e
`allow_partial=false`; gli script legacy conservano il contratto API precedente.
Gli avvisi non bloccanti non diventano automaticamente errori.

Le notifiche degli import Gymternet e Calendar raggiungono l'autore e tutti
i SUPER ADMIN attivi. Indicano ruolo/ID autore e riepilogo; ogni destinatario
riceve il testo nella propria lingua, senza doppia notifica quando l'autore
e SUPER ADMIN. Preview e tentativi bloccati non generano notifiche di successo.
La correzione diretta delle righe descritta qui riguarda i risultati Gymternet;
non introduce un editor delle righe Calendar.

Questo aggiornamento riguarda il flusso di import. La tabella seguente conserva
la descrizione della prima integrazione del Centro Admin del 22 settembre.

## Accesso

Area personale > Centro Admin, oppure `#/admin`. Il frontend richiede
ADMIN/SUPER ADMIN; il backend autorizza separatamente ogni operazione.
Il modulo `frontend/admin-center.js` riusa autenticazione, controlli di
selezione e token CSS esistenti. I form leggono enum e tipi da OpenAPI.

| Area | Operazioni | Permesso |
| --- | --- | --- |
| Inserimento dati | Nuovo Event/Athlete; ricerca atleta; format/round condivisi; bozza e validazione bulk | ADMIN |
| Gestione record | Schede e strumenti WG; modifica Result; immagini; eliminazione con conferma | ADMIN |
| Importazioni | XLSX/CSV Gymternet e Calendar; preview; decisioni identita/nazionalita; recupero D-score; suggerimenti target; report JSON; commit | ADMIN |
| Calendario | Vista interattiva, anno/stato, conteggi, gare e promemoria | ADMIN |
| Revisioni | Dati da completare; suggerimenti modificabili con fonte/evidenza; accetta/rifiuta; Result duplicati | ADMIN |
| Unisci atleti | ID sorgente/destinazione, motivazione, preview conflitti, conferma | ADMIN |
| Notifiche | Notifiche dell'account; lettura singola/globale; paginazione | ADMIN |
| Statistiche sito | Riepilogo per periodo | ADMIN |
| Sicurezza | Cambio password e nuovo login; stato MFA | ADMIN |
| Utenti e ruoli | Ricerca email e modifica ruolo | SUPER ADMIN |
| Audit e ripristino | Prima/dopo, approvazione, annullamento update, ripristino entita eliminate | SUPER ADMIN |

Le schede aperte dal centro mostrano gli strumenti amministrativi gia
implementati e un ritorno al pannello di provenienza. Il ciclo di
certificazione World Gymnastics resta quello delle schede canoniche.

## Scelte semantiche

- Gli atleti nuovi nella bozza risultati vengono inviati nel payload bulk:
  creazione e validazione seguono la transazione del backend.
- E Score obbligatorio dal 2026 nel data entry; P/B vuoti inviati come null,
  normalizzati dal backend. Controllo D + E - P + B = Final Score server-side.
- La preview Gymternet accetta ora le decisioni del commit e ne mostra
  l'esito senza modificare il database.
- Bozze, file e decisioni persistono in memoria durante la navigazione;
  un ricaricamento completo del browser le perde. Nessun salvataggio locale
  persistente dei file caricati.
- Nazionalita: scelta tra storico e correzione dei country rappresentati.
  Associazioni irrisolte restano soggette ai blocchi dell'importatore.
- Calendar conserva i vincoli esistenti: duplicati e sorgenti discordanti
  bloccano il commit; righe storiche non associate restano nel report.
  Non vengono inventate associazioni automatiche.
- Audit e restore operano sui record previsti dal backend; non equivalgono
  al ripristino integrale di un backup del database.
- MFA configurata al login con token temporaneo mfa_setup; chiave e codici
  di recupero visualizzati prima di completare l'accesso.
- Provider IA disabilitato: il centro non lo attiva.

## Collaudo

165 test automatici superati, compresi due nuovi test per preview con
decisioni senza scritture e paginazione stabile delle notifiche.
Lo script `scripts/check_admin_ui.py` verifica le aree in Chromium,
i form, l'invio bulk simulato e il cambio attrezzi MAG/WAG. Le richieste
di scrittura sono intercettate: il DB storico non viene modificato.
Verificati screenshot desktop/mobile e assenza di overflow orizzontale.
Playwright/Chromium sono strumenti di collaudo opzionali.

Non sono stati eseguiti import massivi, ripristini o cambi ruolo reali dal
nuovo centro. Il collaudo operativo conclusivo va eseguito su una copia
del DB. I comandi principali sono localizzati EN/IT/ES/FR; le evidenze e
i messaggi tecnici conservano il testo fornito dal backend.

Questa e la prima integrazione operativa del centro: la revisione visuale
con il proprietario e il collaudo operativo precedono la chiusura definitiva.
