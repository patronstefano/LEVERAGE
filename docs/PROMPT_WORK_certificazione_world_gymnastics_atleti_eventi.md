# Prompt per Work - certificazione World Gymnastics di Atleti ed Eventi

Analizza e documenta nella monografia di LEVERAGE il sistema di certificazione World Gymnastics implementato per le Schede Atleta e le Schede Evento. Il lavoro e gia stato sviluppato, verificato e pubblicato nel repository GitHub:

`https://github.com/patronstefano/LEVERAGE`

Usa come riferimento principale il tag GitHub:

`v0.5.0-world-gymnastics-certification`

Prima di scrivere, consulta direttamente il codice, i test e la documentazione associati al tag. Non limitarti a parafrasare questo prompt: verifica nel repository che ogni affermazione sia coerente con l'implementazione effettiva.

## Obiettivo della sezione

Spiega il sistema come una funzionalita di data governance, sicurezza e controllo human-in-the-loop. Non descriverlo come un semplice badge grafico. LEVERAGE separa infatti tre livelli distinti:

1. i normali dati anagrafici dell'Atleta o descrittivi dell'Evento;
2. il collegamento informativo alla corrispondente pagina ufficiale World Gymnastics;
3. la certificazione pubblica del matching tra l'entita LEVERAGE e la fonte ufficiale, rappresentata dal badge blu LEVERAGE.

## Flusso da descrivere

Descrivi in modo rigoroso il seguente ciclo, comune e coerente per Atleti ed Eventi:

- soltanto un utente `admin` o `super_admin` puo usare l'Assistente World Gymnastics;
- l'Admin puo effettuare una ricerca automatica dei candidati oppure una ricerca manuale tramite FIG ID o URL ufficiale;
- ricerca e preview sono operazioni non mutative: non certificano l'entita, non pubblicano dati e non producono da sole un badge;
- LEVERAGE mostra i candidati, la compatibilita e gli eventuali warning, lasciando sempre la decisione finale a un essere umano;
- quando l'Admin seleziona il candidato corretto e conferma `Importa dati`, LEVERAGE certifica il matching e registra atomicamente i metadati della verifica;
- i singoli valori provenienti dalla fonte ufficiale diventano suggerimenti pending: l'Admin puo approvarli, modificarli oppure rifiutarli separatamente;
- l'approvazione successiva dei singoli suggerimenti non deve sovrascrivere la data o l'autore della certificazione;
- l'identificativo dell'Admin verificatore e riservato ad Admin/Super Admin e non viene esposto negli schemi API pubblici;
- le operazioni mutative rilevanti sono registrate nell'audit amministrativo.

## Manutenzione, revoca e ri-certificazione

Evidenzia l'invariante di sicurezza principale. Dopo il primo collegamento, FIG ID, URL ufficiale e status possono essere gestiti in un blocco World Gymnastics dedicato degli strumenti Admin. Tuttavia:

- la modifica del solo status non invalida il matching dell'identita;
- la modifica manuale di FIG ID o URL cambia la fonte identificativa e revoca automaticamente certificazione, data e Admin verificatore;
- il badge puo essere rimosso esplicitamente senza cancellare necessariamente il collegamento informativo;
- il badge non puo essere attribuito o riattivato manualmente dal form ordinario;
- dopo una revoca o una variazione dell'identita FIG, la ri-certificazione richiede un nuovo riscontro ufficiale e una nuova conferma di `Importa dati`;
- la ri-certificazione registra nuovamente, nella stessa transazione, stato verificato, timestamp e Admin responsabile.

Spiega perche questa separazione impedisce che il semplice inserimento di un URL venga trasformato arbitrariamente in una certificazione pubblica.

## Modello dati e rappresentazione pubblica

Verifica e descrivi anche la differenza implementativa tra le entita:

- per `Athlete`, la certificazione pubblica e rappresentata dal booleano persistente `is_profile_verified`, accompagnato da timestamp e Admin verificatore;
- per `Event`, lo stato pubblico verificato deriva dalla presenza di `world_gymnastics_verified_at`, anch'esso associato internamente all'Admin verificatore;
- nelle Schede complete, i dati World Gymnastics approvati sono raccolti in una riga dedicata e ordinata: FIG ID, status, profilo, data di verifica e, soltanto per utenti amministrativi, Admin verificatore;
- nelle card sintetiche non vengono mostrati status, URL, FIG ID o altri dati aggiuntivi: compare soltanto il badge accanto al nome quando l'entita e verificata;
- le card Atleta continuano a mostrare soltanto disciplina, country e Leverage ID;
- le card Evento continuano a mostrare soltanto disciplina, categoria e level, con la data sempre sotto al nome.

Il badge deve essere presentato come certificazione del matching controllato con la pagina ufficiale World Gymnastics. Non certifica automaticamente ogni campo, i risultati sportivi o l'intero contenuto della scheda; non implica partnership, approvazione o endorsement di LEVERAGE da parte di World Gymnastics.

## Aspetti da valorizzare nella monografia

Collega l'implementazione ai concetti di:

- human-in-the-loop;
- provenienza e tracciabilita del dato;
- separazione delle responsabilita;
- principio del minimo privilegio;
- auditabilita;
- privacy dei metadati amministrativi;
- revocabilita e ri-certificazione controllata;
- prevenzione delle attribuzioni arbitrarie;
- coerenza semantica e visiva tra Atleti ed Eventi;
- test automatici e migrazioni conservative per la riparazione degli stati storici.

## Riferimenti Git da verificare

Oltre al tag finale, consulta almeno i seguenti commit e la loro evoluzione:

- `39ac359` - assegnazione del badge Atleta esclusivamente attraverso `Importa dati`;
- `8fd7976` - manutenzione protetta, revoca esplicita e invalidazione automatica al cambio dell'identita FIG;
- `c9f6fc2` - preservazione atomica dei metadati di audit durante la ri-certificazione;
- `e0ebbe8` - consolidamento finale del ciclo di certificazione Atleta;
- `0cf164d` - allineamento degli strumenti Admin Evento al flusso certificativo;
- `92c1bf8` - allineamento dell'identita World Gymnastics verificata tra Evento e Atleta;
- `0583bac` - visualizzazione coerente dei badge nelle card Atleta ed Evento e completamento del contratto della ricerca globale.

Consulta inoltre:

- `docs/LEVERAGE_diario_di_bordo.md`;
- `docs/LEVERAGE_monografia_certificazione_schede_atleta.md`;
- `docs/PROMPT_monografia_certificazione_world_gymnastics.md`;
- le migrazioni Alembic relative alla certificazione;
- i test API e i contratti frontend dedicati.

Produci una sezione accademica completa, tecnicamente verificabile e coerente con il resto della monografia. Distingui sempre cio che il sistema certifica da cio che non certifica, e cita tag, commit, componenti backend, frontend, audit e test come evidenze dell'implementazione.
