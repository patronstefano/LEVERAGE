# Prompt per la chat di scrittura della monografia

Integra nella monografia di LEVERAGE una sezione specifica e tecnicamente rigorosa dedicata al ciclo di certificazione World Gymnastics delle Schede Atleta. Trattalo come un passaggio fondamentale di sicurezza e data governance, non come una semplice scelta grafica o funzionalita UI.

Devi spiegare chiaramente che LEVERAGE separa tre livelli:

1. la normale anagrafica dell'atleta;
2. il collegamento informativo al profilo ufficiale World Gymnastics;
3. la certificazione pubblica dell'identita, rappresentata dal badge blu LEVERAGE.

Il blocco World Gymnastics compare in `Modifica atleta` soltanto quando esiste gia un collegamento e permette ad Admin/Super Admin di gestire FIG ID, URL e status. Il badge dispone di una revoca esplicita, ma non puo essere attribuito o riattribuito manualmente dal form, dal normale endpoint anagrafico o inserendo semplicemente un URL. Se FIG ID o URL vengono modificati manualmente, LEVERAGE revoca automaticamente badge, data di verifica e riferimento all'Admin verificatore. La modifica del solo status non invalida invece l'identita certificata.

Dopo una revoca, il badge puo essere riattivato esclusivamente selezionando nuovamente un profilo ufficiale riscontrato e confermando `Importa dati`. Questa regola impedisce che una certificazione pubblica venga assegnata senza un nuovo controllo della fonte. `Importa dati` registra atomicamente badge, timestamp e Admin verificatore; l'approvazione successiva dei singoli suggerimenti non modifica tali metadati. Le operazioni amministrative che modificano certificazione o dati World Gymnastics sono registrate nell'audit Admin/Super Admin; ricerca e preview sono protette dai ruoli ma non producono una voce `AuditLog`.

Specifica inoltre che il badge attesta il matching controllato tra la Scheda Atleta LEVERAGE e un profilo ufficiale World Gymnastics; non certifica automaticamente ogni dato anagrafico, tutti i risultati sportivi, ne costituisce un endorsement della federazione.

Prima di scrivere la sezione, verifica l'implementazione nel repository GitHub `patronstefano/LEVERAGE`, concentrandoti sui commit:

- `39ac359` - assegnazione del badge esclusivamente tramite `Importa dati`;
- `8fd7976` - manutenzione protetta dei dati FIG, revoca esplicita, revoca automatica al cambio dell'identita ufficiale e audit;
- `452125b` - visualizzazione pubblica del badge accanto alla disciplina MAG/WAG.

Consulta inoltre `docs/LEVERAGE_monografia_certificazione_schede_atleta.md`, il diario di bordo e i relativi test API. Descrivi la scelta in termini di human-in-the-loop, provenienza del dato, separazione delle responsabilita, principio del minimo privilegio, auditabilita, reversibilita controllata e protezione dall'attribuzione arbitraria della certificazione.
