# Centro Admin unificato

Data: 22 settembre 2026. Perimetro: MVP privato locale.

## Aggiornamento Importazione file - 6 ottobre 2026

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

Il recap distingue risultati esclusi, nuovi candidati e identita da risolvere.
Gare, conflitti e revisioni sono raccolti in sezioni chiuse, con sei elementi
per pagina. Confronta dettagli apre classifiche, conteggi e un campione di
massimo 20 nuovi risultati per gara. Gli errori sorgente sicuramente riferiti
alle gare escluse non bloccano le nuove importazioni; quelli delle gare incluse
o non attribuibili rimangono bloccanti.

Le possibili corrispondenze di gare nello stesso anno richiedono una decisione
esplicita: associazione alla gara proposta o conferma di gara distinta. Si
affiancano alla review atleta/nazionalita e ai D-score orfani. Dopo le decisioni,
Ricalcola anteprima aggiorna il report prima della conferma. I conflitti di
identita irrisolti bloccano anche l'import parziale; i risultati gia salvati
non vengono sovrascritti. Le decisioni sono comprese nel report JSON scaricabile.

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
