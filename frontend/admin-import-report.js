export const IMPORT_COPY = {
  importEntityChecks: ['Identity checks to resolve', 'Verifiche identità da risolvere', 'Verificaciones de identidad pendientes', 'Vérifications d’identité à résoudre'],
  importDeferredChecks: ['Deferred identity checks', 'Verifiche identità rinviate', 'Verificaciones de identidad aplazadas', 'Vérifications d’identité reportées'],
  importCountryChecks: ['Countries to review', 'Nazionalità da verificare', 'Nacionalidades por verificar', 'Nationalités à vérifier'],
  importReloadDetails: ['Recalculate the preview to load the comparison details.', 'Ricalcola l’anteprima per caricare i dettagli del confronto.', 'Recalcula la vista previa para cargar los detalles de comparación.', 'Recalculez l’aperçu pour charger les détails de comparaison.'],
  gymternet_orphan_dscores: ['Unmatched D-score rows in the selected import scope: {n}. Review them before importing.', 'Righe D Score senza un Final Score associato nel perimetro da importare: {n}. Da revisionare prima dell’importazione.', 'Filas D Score sin Final Score asociado en el ámbito a importar: {n}. Revísalas antes de importar.', 'Lignes D Score sans Final Score associé dans le périmètre à importer : {n}. À vérifier avant l’importation.'],
  gymternet_automatic_days: ['The file uses automatically assigned day indices to distinguish multiple performances without an explicit Day column. These are not verified calendar dates.', 'Il file utilizza indici di giorno assegnati automaticamente per distinguere più prestazioni senza una colonna Day esplicita. Non sono date di calendario verificate.', 'El archivo usa índices de día asignados automáticamente para distinguir actuaciones sin columna Day explícita. No son fechas de calendario verificadas.', 'Le fichier utilise des indices de jour attribués automatiquement pour distinguer des performances sans colonne Day explicite. Ce ne sont pas des dates vérifiées.'],
  gymternet_post_2025_policy: ['Gymternet results from 2026 onward follow the 2025 vault and missing-component rules. Missing E, Penalty and Bonus remain unavailable.', 'I risultati Gymternet dal 2026 seguono le stesse regole del 2025 per volteggio e componenti mancanti. E, Penalty e Bonus assenti restano non disponibili.', 'Los resultados Gymternet desde 2026 siguen las reglas de 2025 para salto y componentes ausentes. E, Penalty y Bonus ausentes siguen sin estar disponibles.', 'Les résultats Gymternet à partir de 2026 suivent les règles de 2025 pour le saut et les composantes manquantes. E, Penalty et Bonus absents restent indisponibles.'],
  calendar_sheet_year: ['Sheet skipped: its name is not a year.', 'Foglio ignorato: il nome non indica un anno.', 'Hoja omitida: el nombre no indica un año.', 'Feuille ignorée : son nom ne correspond pas à une année.'],
  calendar_headers: ['Columns A and B must be named DATE and EVENT.', 'Le colonne A e B devono avere le intestazioni DATE ed EVENT.', 'Las columnas A y B deben tener los encabezados DATE y EVENT.', 'Les colonnes A et B doivent porter les en-têtes DATE et EVENT.'],
  calendar_csv_headers: ['The CSV must contain DATE, EVENT and YEAR columns.', 'Il CSV deve contenere le colonne DATE, EVENT e YEAR.', 'El CSV debe contener las columnas DATE, EVENT y YEAR.', 'Le CSV doit contenir les colonnes DATE, EVENT et YEAR.'],
  calendar_event_required: ['Event name missing.', 'Nome della gara mancante.', 'Falta el nombre de la competición.', 'Nom de la compétition manquant.'],
  calendar_date_invalid: ['Date missing or invalid. Expected format: Jan 11, Jan 11-15 or Jan 11-Feb 3.', 'Data mancante o non valida. Formato previsto: Jan 11, Jan 11-15 oppure Jan 11-Feb 3.', 'Fecha ausente o no válida. Formato esperado: Jan 11, Jan 11-15 o Jan 11-Feb 3.', 'Date manquante ou incorrecte. Format attendu : Jan 11, Jan 11-15 ou Jan 11-Feb 3.'],
  calendar_year_invalid: ['YEAR must contain a valid year.', 'La colonna YEAR deve contenere un anno valido.', 'La columna YEAR debe contener un año válido.', 'La colonne YEAR doit contenir une année valide.'],
  calendar_file_empty: ['The uploaded file is empty.', 'Il file caricato è vuoto.', 'El archivo está vacío.', 'Le fichier importé est vide.'],
  calendar_file_invalid: ['The file could not be read. Check that it is a valid XLSX, XLSM or CSV calendar.', 'Impossibile leggere il file. Verifica che sia un calendario XLSX, XLSM o CSV valido.', 'No se puede leer el archivo. Comprueba que sea un calendario XLSX, XLSM o CSV válido.', 'Impossible de lire le fichier. Vérifiez qu’il s’agit d’un calendrier XLSX, XLSM ou CSV valide.'],
  importCalendarDuplicate: ['Repeated calendar entry', 'Voce calendario ripetuta', 'Entrada de calendario repetida', 'Entrée de calendrier répétée'],
  importCalendarDateConflict: ['Different periods for the same event', 'Periodi diversi per lo stesso evento', 'Periodos distintos para el mismo evento', 'Périodes différentes pour le même événement'],
  importCalendarFixSource: ['These conflicts block the import. Correct the referenced rows in the file and run the preview again.', 'Questi conflitti bloccano l’importazione. Correggi nel file le righe indicate e ripeti l’anteprima.', 'Estos conflictos bloquean la importación. Corrige las filas indicadas y repite la vista previa.', 'Ces conflits bloquent l’import. Corrigez les lignes indiquées et relancez l’aperçu.'],
  importCalendarSourceValue: ['Source date', 'Data nel file', 'Fecha del archivo', 'Date du fichier'],
  importCalendarSources: ['Source entries', 'Voci sorgente', 'Entradas de origen', 'Entrées source'],
  importCalendarSkipped: ['Not imported: no historical match', 'Non importata: nessuna corrispondenza storica', 'No importada: sin coincidencia histórica', 'Non importée : aucune correspondance historique'],
  importCalendarYearEmpty: ['No calendar entries found for {year}.', 'Nessuna voce calendario trovata per il {year}.', 'No se encontraron eventos de calendario para {year}.', 'Aucune entrée de calendrier trouvée pour {year}.'],
  importReviewEvents: ['Event review', 'Revisione Eventi', 'Revisión de Eventos', 'Révision des Événements'],
  importReviewAthletes: ['Athlete review', 'Revisione Atleti', 'Revisión de Atletas', 'Révision des Athlètes'],
  importReviewResults: ['Result review', 'Revisione Risultati', 'Revisión de Resultados', 'Révision des Résultats'],
  importPresent: ['Already in LEVERAGE', 'Già in LEVERAGE', 'Ya en LEVERAGE', 'Déjà dans LEVERAGE'],
  importNotPresent: ['Not yet matched', 'Non ancora associati', 'Sin asociar', 'Non encore associés'],
  importWithIssues: ['With discrepancies', 'Con incongruenze', 'Con discrepancias', 'Avec incohérences'],
  importWithoutIssues: ['No discrepancies found', 'Senza incongruenze rilevate', 'Sin discrepancias detectadas', 'Sans incohérences détectées'],
  importReviewScope: ['Events and Athletes concern entity identities and fields. Scores, missing components and score warnings appear only in Results.', 'Eventi e Atleti riguardano identità e campi delle entità. Punteggi, componenti mancanti e relativi avvisi compaiono solo in Risultati.', 'Eventos y Atletas tratan identidades y campos de las entidades. Las puntuaciones, componentes ausentes y avisos asociados aparecen solo en Resultados.', 'Événements et Athlètes concernent les identités et les champs des entités. Les scores, composantes absentes et signalements associés figurent uniquement dans Résultats.'],
  importDuplicateLater: ['Review duplicates', 'Revisione Duplicati', 'Revisión de Duplicados', 'Révision des Doublons'],
  importDuplicateNote: ['Review possible duplicate identities now or defer them to Duplicate Review after import.', 'Verifica ora le possibili identità duplicate oppure rinviale a Revisione Duplicati dopo l’importazione.', 'Revisa las posibles identidades duplicadas ahora o aplázalas hasta después de la importación.', 'Vérifiez les identités potentiellement dupliquées maintenant ou reportez-les après l’import.'],
  importDeferDuplicates: ['Defer all duplicate reviews', 'Rinvia tutta la revisione duplicati', 'Aplazar toda la revisión de duplicados', 'Reporter toute la révision des doublons'],
  importDeferEventsConfirm: ['Defer only event identities. Athlete reviews remain unchanged. Existing decisions are preserved; no automatic matching.', 'Rinvia solo le identità degli eventi, senza associazioni automatiche. La revisione atleti resta invariata e le decisioni già prese vengono mantenute.', 'Aplaza solo las identidades de eventos, sin asociaciones automáticas. La revisión de atletas y las decisiones existentes no cambian.', 'Reportez uniquement les identités des événements, sans association automatique. La révision des athlètes et les décisions existantes restent inchangées.'],
  importDeferAthletesConfirm: ['Defer only athlete identities. Event reviews remain unchanged. Existing decisions are preserved; no automatic matching.', 'Rinvia solo le identità degli atleti, senza associazioni automatiche. La revisione eventi resta invariata e le decisioni già prese vengono mantenute.', 'Aplaza solo las identidades de atletas, sin asociaciones automáticas. La revisión de eventos y las decisiones existentes no cambian.', 'Reportez uniquement les identités des athlètes, sans association automatique. La révision des événements et les décisions existantes restent inchangées.'],
  importResumeDuplicates: ['Resume duplicate review', 'Riprendi revisione duplicati', 'Retomar la revisión de duplicados', 'Reprendre la révision des doublons'],
  importDeferConfirm: ['Unresolved athlete and event identities will be imported separately, without automatic matching. Possible duplicate pairs will remain in Duplicate Review. Existing decisions are preserved; score conflicts, file errors and orphan D Scores still require review.', 'Le identità di atleti ed eventi non ancora risolte saranno importate separatamente, senza associazioni automatiche. Le coppie sospette resteranno in Revisione Duplicati. Le decisioni già prese sono mantenute; punteggi discordanti, errori del file e D Score orfani restano da verificare.', 'Las identidades pendientes se importarán por separado, sin asociaciones automáticas. Las parejas se conservarán en Revisión de Duplicados. Se mantienen las decisiones previas; los conflictos de puntuación, errores y D Scores huérfanos requieren revisión.', 'Les identités non résolues seront importées séparément, sans association automatique. Les paires resteront dans Révision des Doublons. Les décisions existantes sont conservées ; les conflits de scores, erreurs et D Scores orphelins restent à vérifier.'],
  importDeferredNote: ['Unresolved identities deferred to Duplicate Review after import.', 'Identità non risolte rinviate a Revisione Duplicati dopo l’importazione.', 'Identidades pendientes aplazadas hasta después de la importación.', 'Identités non résolues reportées après l’import.'],
  importDeferredCount: ['Pairs saved for Duplicate Review: {n}.', 'Coppie salvate in Revisione Duplicati: {n}.', 'Parejas guardadas para revisar: {n}.', 'Paires enregistrées pour révision : {n}.'],
  importAthletesList: ['Athletes in this import', 'Atleti di questo import', 'Atletas de esta importación', 'Athlètes de cet import'],
  importCorrections: ['Scores to review', 'Punteggi da verificare', 'Puntuaciones por revisar', 'Scores à vérifier'],
  importNoCorrections: ['No score corrections required.', 'Nessun punteggio da correggere.', 'No hay puntuaciones que corregir.', 'Aucun score à corriger.'],
  importChangeFile: ['Change file', 'Cambia file', 'Cambiar archivo', 'Changer de fichier'],
  importHideFile: ['Close parameters', 'Chiudi parametri', 'Cerrar parámetros', 'Fermer les paramètres'],
  importBlocking: ['To resolve', 'Da risolvere', 'Por resolver', 'À résoudre'],
  importReadOnly: ['Existing scores will not be overwritten.', 'I punteggi già salvati non verranno sovrascritti.', 'Los resultados guardados no se sobrescribirán.', 'Les scores existants ne seront pas remplacés.'],
  importCalendarRows: ['Calendar entries', 'Voci calendario', 'Entradas del calendario', 'Entrées du calendrier'],
  importCalendarMatched: ['Matched events', 'Gare associate', 'Competiciones asociadas', 'Compétitions associées'],
  importCalendarExistingScope: ['Events already in LEVERAGE', 'Eventi già presenti in LEVERAGE', 'Eventos ya presentes en LEVERAGE', 'Événements déjà présents dans LEVERAGE'],
  importCalendarExcluded: ['Existing events excluded', 'Eventi già presenti esclusi', 'Eventos existentes excluidos', 'Événements existants exclus'],
  importCalendarSkipNote: ['Existing events are excluded from review and their dates will not be updated.', 'Gli eventi già presenti sono esclusi dalla revisione e le loro date non saranno aggiornate.', 'Los eventos existentes se excluyen de la revisión y sus fechas no se actualizarán.', 'Les événements existants sont exclus de la révision et leurs dates ne seront pas mises à jour.'],
  importCalendarUpdate: ['Dates to update', 'Date da aggiornare', 'Fechas por actualizar', 'Dates à actualiser'],
  importCalendarUnmatched: ['Unmatched historical entries', 'Voci storiche non associate', 'Entradas históricas sin asociar', 'Entrées historiques non associées'],
  importCalendarConflicts: ['Source conflicts', 'Conflitti sorgente', 'Conflictos de origen', 'Conflits source'],
  importCalendarUnchanged: ['Dates already aligned', 'Date già allineate', 'Fechas ya coincidentes', 'Dates déjà concordantes'],
  importCalendarUpdated: ['Dates updated', 'Date aggiornate', 'Fechas actualizadas', 'Dates actualisées'],
  importCalendarCreated: ['Event created', 'Gara creata', 'Competición creada', 'Compétition créée'],
  importCreatedAthletes: ['Athletes created', 'Atleti creati', 'Atletas creados', 'Athlètes créés'],
  importCreatedEvents: ['Events created', 'Gare create', 'Competiciones creadas', 'Compétitions créées'],
  importCreatedResults: ['Results imported', 'Risultati importati', 'Resultados importados', 'Résultats importés'],
  importUpdatedEvents: ['Events updated', 'Gare aggiornate', 'Competiciones actualizadas', 'Compétitions actualisées'],
  importSkippedDuplicates: ['Duplicates skipped', 'Duplicati tralasciati', 'Duplicados omitidos', 'Doublons exclus'],
  importSkippedConflicts: ['Conflicts skipped', 'Conflitti tralasciati', 'Conflictos omitidos', 'Conflits exclus'],
  importSourceNote: ['Edits apply only to this import, not to the original file or existing scores. Excluding a source row omits all its scores.', 'Le correzioni riguardano solo questa importazione, non il file originale o i punteggi già salvati. Tralasciare una riga esclude tutti i suoi punteggi.', 'Las correcciones afectan solo a esta importación, no al archivo original ni a los resultados guardados. Omitir una fila excluye todas sus puntuaciones.', 'Les corrections concernent uniquement cet import, pas le fichier original ni les scores existants. Exclure une ligne exclut tous ses scores.'],
  importEditRow: ['Correct row', 'Correggi riga', 'Corregir fila', 'Corriger la ligne'],
  importExcludeRow: ['Skip row', 'Tralascia riga', 'Omitir fila', 'Exclure la ligne'],
  importExcludeAllRows: ['Skip unresolved source rows', 'Tralascia tutte le righe da correggere', 'Omitir las filas pendientes', 'Exclure les lignes à corriger'],
  importExcludeRowsConfirm: ['Skip {n} source rows and all their scores in this import?', 'Tralasciare {n} righe del file e tutti i relativi punteggi in questa importazione?', '¿Omitir {n} filas y todas sus puntuaciones de esta importación?', 'Exclure {n} lignes et tous leurs scores de cet import ?'],
  importExcludeRowConfirm: ['Skip 1 source row and all its scores in this import?', 'Tralasciare 1 riga del file e tutti i relativi punteggi in questa importazione?', '¿Omitir 1 fila y todas sus puntuaciones de esta importación?', 'Exclure 1 ligne et tous ses scores de cet import ?'],
  importRowExcluded: ['Excluded', 'Tralasciata', 'Excluida', 'Exclue'],
  importRowCorrected: ['Proposed correction', 'Correzione proposta', 'Corrección propuesta', 'Correction proposée'],
  importUndoRow: ['Restore source row', 'Ripristina riga originale', 'Restaurar fila original', 'Restaurer la ligne originale'],
  importInvalidCorrection: ['Enter a valid non-negative score, or explicitly skip the source row.', 'Inserisci un punteggio numerico valido e non negativo, oppure tralascia esplicitamente la riga.', 'Introduce una puntuación válida no negativa u omite explícitamente la fila.', 'Saisissez un score valide non négatif, ou excluez explicitement la ligne.'],
  importApplyDecision: ['Done', 'Fine', 'Listo', 'Terminé'],
  importApplyAll: ['Apply decisions', 'Applica decisioni', 'Aplicar decisiones', 'Appliquer les décisions'],
  importDiscardOrphans: ['Skip all unmatched D Scores', 'Tralascia tutti i D Score orfani', 'Omitir todos los D Scores sin asociar', 'Exclure tous les D Scores non associés'],
  importDiscardOrphansConfirm: ['Skip all unmatched D Scores in this preview? No scores will be invented.', 'Tralasciare tutti i D Score orfani di questa anteprima? Non verranno inventati punteggi mancanti.', '¿Omitir todos los D Scores sin asociar? No se inventarán puntuaciones.', 'Exclure tous les D Scores non associés ? Aucun score ne sera inventé.'],
  importIssueSample: ['Review source rows below to resolve file issues.', 'Correggi le righe del file qui sotto per risolvere le segnalazioni.', 'Corrige las filas del archivo para resolver las incidencias.', 'Corrigez les lignes du fichier pour résoudre les signalements.'],
  importExistingScope: ['Previously imported competitions', 'Gare già importate', 'Competiciones ya importadas', 'Compétitions déjà importées'],
  importScopeInclude: ['Include', 'Includi', 'Incluir', 'Inclure'],
  importScopeSkip: ['Skip', 'Tralascia', 'Omitir', 'Exclure'],
  importHistorical: ['competitions already in LEVERAGE', 'gare già in LEVERAGE', 'competiciones ya en LEVERAGE', 'compétitions déjà dans LEVERAGE'],
  importHistoricalSingle: ['competition already in LEVERAGE', 'gara già in LEVERAGE', 'competición ya en LEVERAGE', 'compétition déjà dans LEVERAGE'],
  importHistoricalNote: ['These competitions are excluded. Choose “Include” in the preview to add or review their results. Validated data are never overwritten.', 'Queste gare sono escluse. Scegli “Includi” nell’anteprima per integrarne o ricontrollarne i risultati. I dati già validati non vengono sovrascritti.', 'Estas competiciones se excluyen. Elige “Incluir” en la vista previa para añadir o revisar sus resultados. Los datos validados no se sobrescriben.', 'Ces compétitions sont exclues. Choisissez « Inclure » dans l’aperçu pour compléter ou vérifier leurs résultats. Les données validées ne sont pas remplacées.'],
  importHistoricalDifferences: ['Source differences in excluded competitions', 'Differenze sorgente nelle gare escluse', 'Diferencias de origen en competiciones excluidas', 'Différences de source des compétitions exclues'],
  importHistoricalCaution: ['Differences may reflect previous corrections. They do not reopen identity reviews or change existing data.', 'Le differenze possono dipendere da correzioni già effettuate. Non riaprono le revisioni di identità e non modificano i dati esistenti.', 'Las diferencias pueden deberse a correcciones previas. No reabren revisiones ni cambian datos existentes.', 'Les différences peuvent provenir de corrections antérieures. Elles ne rouvrent pas les vérifications et ne modifient pas les données.'],
  importDifferences: ['Results to compare', 'Risultati non coincidenti', 'Resultados no coincidentes', 'Résultats non concordants'],
  importPreviousPage: ['Previous', 'Precedenti', 'Anteriores', 'Précédents'],
  importNextPage: ['Next', 'Successivi', 'Siguientes', 'Suivants'],
  importHistoricalOnly: ['No new competitions to import.', 'Nessuna nuova gara da importare.', 'No hay nuevas competiciones que importar.', 'Aucune nouvelle compétition à importer.'],
  importExcludedResults: ['Excluded results (existing competitions)', 'Risultati esclusi (gare già presenti)', 'Resultados excluidos (competiciones existentes)', 'Résultats exclus (compétitions existantes)'],
  importVtInvalid: ['The second vault cannot be reconstructed: the calculated score is outside the 0–20 range. Check VT and VT AVG in the file.', 'Il secondo salto non può essere ricostruito: il punteggio calcolato è fuori dall’intervallo 0–20. Controlla VT e VT AVG nel file.', 'No se puede reconstruir el segundo salto: la puntuación calculada está fuera del intervalo 0–20. Revisa VT y VT AVG.', 'Impossible de reconstituer le deuxième saut : le score calculé est hors de l’intervalle 0–20. Vérifiez VT et VT AVG.'],
  importVtRounding: ['The calculation gives a slightly negative score, possibly due to rounding of VT AVG. Verify the source: no second-vault score has been created.', 'Il calcolo dà un punteggio leggermente negativo, compatibile con un arrotondamento di VT AVG. Verifica la fonte: il punteggio del secondo salto non è stato creato.', 'El cálculo da una puntuación ligeramente negativa, posiblemente por redondeo de VT AVG. Verifica la fuente: no se ha creado el segundo salto.', 'Le calcul donne un score légèrement négatif, possiblement dû à l’arrondi de VT AVG. Vérifiez la source : aucun score du deuxième saut n’a été créé.'],
  importSourceSheet: ['Sheet', 'Foglio', 'Hoja', 'Feuille'],
  importSourceRow: ['Row', 'Riga', 'Fila', 'Ligne'],
  compatibility: ['Compatibility', 'Compatibilità', 'Compatibilidad', 'Compatibilité'],
  importEvents: ['Competitions to process', 'Gare da elaborare', 'Competiciones por procesar', 'Compétitions à traiter'],
  importAllEvents: ['All competitions', 'Tutte le gare', 'Todas las competiciones', 'Toutes les compétitions'],
  importExisting: ['Already imported', 'Già importati', 'Ya importados', 'Déjà importés'],
  importExistingEvents: ['Already imported', 'Già importate', 'Ya importadas', 'Déjà importées'],
  importCompleted: ['Import completed', 'Importazione completata', 'Importación completada', 'Importation terminée'],
  importIdentityNote: ['Compatibility indicates name similarity. Confirm the identity before associating entities.', 'La compatibilità indica la somiglianza dei nomi. Verifica l’identità prima di associare le entità.', 'La compatibilidad indica similitud de nombres. Verifica la identidad antes de asociar entidades.', 'La compatibilité indique une similitude des noms. Vérifiez l’identité avant d’associer les entités.'],
  importNew: ['New results', 'Nuovi risultati', 'Nuevos resultados', 'Nouveaux résultats'],
  importConflicts: ['Score conflicts', 'Punteggi in conflitto', 'Conflictos de puntuación', 'Conflits de scores'],
  importFileRows: ['Results in the file', 'Risultati nel file', 'Resultados del archivo', 'Résultats du fichier'],
  importNewAthletes: ['New athlete candidates', 'Possibili nuovi atleti', 'Posibles nuevos atletas', 'Nouveaux athlètes potentiels'],
  importNewEvents: ['New competition candidates', 'Possibili nuove gare', 'Posibles nuevas competiciones', 'Nouvelles compétitions potentielles'],
  importStatusExisting: ['File results already present', 'Risultati del file già presenti', 'Resultados ya presentes', 'Résultats du fichier déjà présents'],
  importStatusAdditional: ['New results in an existing competition', 'Nuovi risultati in una gara esistente', 'Nuevos resultados en una competición existente', 'Nouveaux résultats dans une compétition existante'],
  importStatusNew: ['New competition', 'Nuova gara', 'Nueva competición', 'Nouvelle compétition'],
  importStatusConflict: ['Requires review', 'Da verificare', 'Por revisar', 'À vérifier'],
  importNoRewrite: ['Identity and score checks apply to competitions included in this import. Existing results are never overwritten.', 'I controlli di identità e punteggio riguardano le gare incluse nell’importazione. I risultati esistenti non vengono sovrascritti.', 'Los controles de identidad y puntuación se aplican a las competiciones incluidas. Los resultados existentes no se sobrescriben.', 'Les contrôles d’identité et de score concernent les compétitions incluses. Les résultats existants ne sont pas remplacés.'],
  importCandidatesNote: ['Counts depend on identity decisions and are updated when the preview is recalculated.', 'I conteggi dipendono dalle decisioni sulle identità e si aggiornano al ricalcolo dell’anteprima.', 'Los recuentos dependen de las decisiones de identidad y se actualizan al recalcular la vista previa.', 'Les totaux dépendent des décisions sur les identités et sont actualisés lors du recalcul de l’aperçu.'],
  importFileDuplicates: ['Repeated rows in the file', 'Righe ripetute nel file', 'Filas repetidas en el archivo', 'Lignes répétées dans le fichier'],
  importGroups: ['Classifications', 'Classifiche', 'Clasificaciones', 'Classements'],
  importSample: ['New results sample (up to 20 per competition)', 'Esempio dei nuovi risultati (fino a 20 per gara)', 'Muestra de nuevos resultados (hasta 20 por competición)', 'Extrait des nouveaux résultats (20 maximum par compétition)'],
  importMoreEvents: ['Load more competitions', 'Carica altre gare', 'Cargar más competiciones', 'Charger plus de compétitions'],
  importMoreConflicts: ['Load more conflicts', 'Carica altri conflitti', 'Cargar más conflictos', 'Charger plus de conflits'],
  importAthleteReview: ['Athlete identity review', 'Revisione identità atleti', 'Revisión de identidad de atletas', 'Vérification des identités des athlètes'],
  importEventReview: ['Competition identity review', 'Revisione identità gare', 'Revisión de identidad de competiciones', 'Vérification des identités des compétitions'],
  importOrphanReview: ['Unmatched D Scores', 'D Score senza risultato associato', 'D Scores sin resultado asociado', 'D Scores sans résultat associé'],
  importCompare: ['Compare details', 'Confronta dettagli', 'Comparar detalles', 'Comparer les détails'],
  importFile: ['Uploaded file', 'File caricato', 'Archivo cargado', 'Fichier importé'],
  importDatabase: ['Already in LEVERAGE', 'Già in LEVERAGE', 'Ya en LEVERAGE', 'Déjà dans LEVERAGE'],
  importRecalculate: ['Recalculate preview', 'Ricalcola anteprima', 'Recalcular vista previa', 'Recalculer l’aperçu'],
  importNeedsPreview: ['Decisions saved in this draft. Complete your review, then recalculate the preview once before importing. Counts refer to the last analysis.', 'Decisioni memorizzate nella bozza. Completa la revisione, poi ricalcola l’anteprima una sola volta prima di importare. I conteggi si riferiscono all’ultima analisi.', 'Decisiones guardadas en este borrador. Completa la revisión y recalcula la vista previa una sola vez antes de importar. Los recuentos corresponden al último análisis.', 'Décisions enregistrées dans ce brouillon. Terminez la révision, puis recalculez l’aperçu une seule fois avant d’importer. Les totaux correspondent à la dernière analyse.'],
  importMatchEvent: ['Associate competition', 'Associa gara', 'Asociar competición', 'Associer la compétition'],
  importNewSeparate: ['Keep as a new competition', 'Conferma nuova gara distinta', 'Confirmar nueva competición distinta', 'Confirmer une nouvelle compétition distincte'],
  importPending: ['Unresolved identities', 'Identità da risolvere', 'Identidades por resolver', 'Identités à résoudre'],
  importIssueList: ['File warnings', 'Avvisi del file', 'Avisos del archivo', 'Avertissements du fichier'],
  conflict_existing: ['Different scores in an existing result', 'Punteggi diversi su un risultato esistente', 'Puntuaciones distintas en un resultado existente', 'Scores différents sur un résultat existant'],
  conflict_in_file: ['Different scores in the same file context', 'Punteggi diversi nello stesso contesto del file', 'Puntuaciones distintas en el mismo contexto', 'Scores différents dans le même contexte'],
  country_conflict_existing: ['Different represented country', 'Nazionalità rappresentata diversa', 'Nacionalidad representada distinta', 'Nationalité représentée différente'],
  country_conflict_in_file: ['Different represented countries in the file', 'Nazionalità rappresentate diverse nel file', 'Nacionalidades distintas en el archivo', 'Nationalités différentes dans le fichier'],
  same_context_different_score_after_athlete_merge: ['Athlete association produces conflicting scores', 'L’associazione dell’atleta produce punteggi in conflitto', 'La asociación del atleta produce conflictos', 'L’association de l’athlète produit des scores en conflit'],
};

export function importIssueScope(issue) {
  if (['country_conflict_existing', 'country_conflict_in_file'].includes(issue.reason)) return 'athletes';
  return ['events', 'athletes'].includes(issue.review_scope) ? issue.review_scope : 'results';
}

export function renderImportIssues({issues, text, esc, language, sourceRows = [], page = 0}) {
  const ordered = [...issues].sort((a, b) => Number(b.severity === 'error') - Number(a.severity === 'error'));
  const score = value => new Intl.NumberFormat(language, {minimumFractionDigits: 3, maximumFractionDigits: 3}).format(value);
  page = Math.min(page, Math.max(0, Math.ceil(ordered.length / 6) - 1));
  return `<ul class="admin-import-issues">${ordered.slice(page * 6, (page + 1) * 6).map(issue => {
    const known = issue.code === 'derived_vt_outlier';
    const message = known ? text(issue.possible_rounding ? 'importVtRounding' : 'importVtInvalid') : issue.code === 'source_correction_invalid' ? text('importInvalidCorrection') : issue.code === 'calendar_year_empty' ? text('importCalendarYearEmpty').replace('{year}', issue.year) : IMPORT_COPY[issue.code] ? text(issue.code).replace('{n}', issue.count ?? '') : issue.message;
    const identity = [[issue.last_name, issue.first_name].filter(Boolean).join(' '), issue.event_name].filter(Boolean).join(' · ');
    const source = [issue.sheet ? `${text('importSourceSheet')} ${issue.sheet}` : '', issue.row != null ? `${text('importSourceRow')} ${issue.row}` : ''].filter(Boolean).join(' · ');
    return `<li><strong>${esc(identity || source)}</strong>${identity && source ? `<p class="admin-revision-meta">${esc(source)}</p>` : ''}<p class="${issue.severity === 'error' ? 'admin-import-issue-error' : ''}">${esc(message)}</p>${issue.date_label && issue.code?.startsWith("calendar_") ? `<p class="admin-revision-meta">${esc(text("importCalendarSourceValue"))}: ${esc(issue.date_label)}</p>` : ""}${known ? `<p class="admin-revision-meta">2 × VT AVG ${score(issue.source_vt_avg)} − VT ${score(issue.source_vt)} = ${score(issue.original_score)}</p>` : ''}${sourceRows.some(row => row.sheet === issue.sheet && row.row === issue.row) ? `<div class="admin-center-actions"><button type="button" class="quiet-button outline-command-button" data-correct-issue-sheet="${esc(issue.sheet)}" data-correct-issue-row="${issue.row}">${esc(text('importEditRow'))}</button></div>` : ''}</li>`;
  }).join('')}</ul>${ordered.length > 6 ? `<div class="admin-import-pagination"><button type="button" class="quiet-button outline-command-button" data-issue-page="${page - 1}" ${page === 0 ? 'disabled' : ''}>${esc(text('importPreviousPage'))}</button><span>${page * 6 + 1}–${Math.min((page + 1) * 6, ordered.length)} / ${ordered.length}</span><button type="button" class="quiet-button outline-command-button" data-issue-page="${page + 1}" ${(page + 1) * 6 >= ordered.length ? 'disabled' : ''}>${esc(text('importNextPage'))}</button></div>` : ''}`;
}

export function renderImportMetrics({items, text, esc, language}) {
  const count = value => new Intl.NumberFormat(language).format(value || 0);
  return `<dl class="admin-stats-metrics admin-duplicate-recap admin-import-metrics">${items.map(([key, value]) => `<div><dt>${esc(text(key))}</dt><dd>${count(value)}</dd></div>`).join('')}</dl>`;
}

export function renderEntityImportMetrics({rows, idKey, text, esc, language, pending = 0, deferred = 0}) {
  const existing = rows.filter(row => row[idKey] != null).length;
  return renderImportMetrics({text, esc, language, items: [
    ['importPresent', existing], ['importNotPresent', rows.length - existing],
    ['importEntityChecks', pending], ['importDeferredChecks', deferred],
  ]});
}

export function mountImportAthletes({root, preview, text, esc, language}) {
  const stats = preview.athlete_match_decision_stats || {};
  root.innerHTML = renderEntityImportMetrics({
    rows: preview.athlete_summaries || [], idKey: 'athlete_id', text, esc, language,
    pending: stats.unresolved ?? (preview.athlete_match_review || []).filter(row => !row.deferred).length,
    deferred: stats.deferred || 0,
  });
}

export function mountCalendarImportRows({root, preview, text, esc, language, route, viewState}) {
  const rows = (preview.rows || []).filter(row => row.action !== 'no_change'), pageSize = 6;
  let page = Math.min(viewState.page || 0, Math.max(0, Math.ceil(rows.length / pageSize) - 1));
  const date = value => value ? new Intl.DateTimeFormat(language, {dateStyle: 'medium'}).format(new Date(`${value}T00:00:00`)) : '';
  const render = () => {
    viewState.page = page;
    root.innerHTML = `<details class="admin-revision-group" data-calendar-details ${viewState.open ? 'open' : ''}><summary>${esc(text('importCalendarRows'))}<span class="admin-revision-count">${rows.length}</span></summary>${rows.slice(page * pageSize, (page + 1) * pageSize).map(row => {
      const period = [date(row.start_date), row.end_date !== row.start_date ? date(row.end_date) : ''].filter(Boolean).join(' – ');
      const status = {update_dates: preview.committed ? 'importCalendarUpdated' : 'importCalendarUpdate', no_change: 'importCalendarUnchanged', create_event: preview.committed ? 'importCalendarCreated' : 'importStatusNew', skip_unmatched_historical: 'importCalendarSkipped'}[row.action];
      const source = [row.sheet ? `${text('importSourceSheet')} ${row.sheet}` : '', row.row ? `${text('importSourceRow')} ${row.row}` : ''].filter(Boolean).join(' · ');
      return `<article class="admin-identity-pair"><div class="admin-identity-entity"><strong>${esc(row.event_name)}</strong><p class="admin-revision-meta">${esc(period)} · ${esc(text(status || 'importStatusConflict'))}</p>${source ? `<p class="admin-revision-meta">${esc(source)}</p>` : ''}</div><div class="admin-center-actions">${(row.matched_event_ids || []).map(id => `<a class="quiet-button outline-command-button" href="#/events/${id}?from=admin&return_to=${encodeURIComponent(route)}">Leverage ID ${id}</a>`).join('')}</div></article>`;
    }).join('')}${rows.length > pageSize ? `<div class="admin-import-pagination"><button type="button" class="quiet-button outline-command-button" data-calendar-page="-1" ${page === 0 ? 'disabled' : ''}>${esc(text('importPreviousPage'))}</button><span>${page * pageSize + 1}–${Math.min((page + 1) * pageSize, rows.length)} / ${rows.length}</span><button type="button" class="quiet-button outline-command-button" data-calendar-page="1" ${(page + 1) * pageSize >= rows.length ? 'disabled' : ''}>${esc(text('importNextPage'))}</button></div>` : ''}</details>`;
    root.querySelector('[data-calendar-details]').ontoggle = event => { if (event.target.isConnected) viewState.open = event.target.open; };
    root.querySelectorAll('[data-calendar-page]').forEach(control => control.onclick = () => { page += Number(control.dataset.calendarPage); render(); });
  };
  render();
}

export function mountCalendarConflicts({root, preview, text, esc, language, route, viewState}) {
  const duplicates = preview.duplicate_source_rows || [];
  const conflicts = preview.matched_event_source_conflicts || [];
  const count = duplicates.length + conflicts.length;
  if (!count) { root.innerHTML = ''; return; }
  const date = value => value ? new Intl.DateTimeFormat(language, {dateStyle: 'medium'}).format(new Date(`${value}T00:00:00`)) : '';
  const source = row => [row.sheet ? `${text('importSourceSheet')} ${row.sheet}` : '', row.row != null ? `${text('importSourceRow')} ${row.row}` : ''].filter(Boolean).join(' · ');
  const period = row => row.start_date ? [date(row.start_date), row.end_date !== row.start_date ? date(row.end_date) : ''].filter(Boolean).join(' – ') : row.date_label || '';
  const sourceRows = new Map((preview.rows || []).map(row => [`${row.sheet}:${row.row}`, row]));
  const records = [
    ...duplicates.map(row => ({...sourceRows.get(`${row.sheet}:${row.row}`), ...row, kind: 'importCalendarDuplicate', original: {
      ...sourceRows.get(`${row.duplicate_of_sheet}:${row.duplicate_of_row}`),
      sheet: row.duplicate_of_sheet, row: row.duplicate_of_row, date_label: row.duplicate_of_date_label,
    }})),
    ...conflicts.flatMap(conflict => (conflict.source_rows || []).map(row => ({...row, event_id: conflict.event_id, kind: 'importCalendarDateConflict'}))),
  ];
  const render = () => {
    const page = viewState.page = Math.min(viewState.page || 0, Math.max(0, Math.ceil(records.length / 6) - 1));
    root.innerHTML = `<details class="admin-revision-group" data-calendar-conflicts ${viewState.open ? 'open' : ''}><summary>${esc(text('importCalendarConflicts'))}<span class="admin-import-blocking">${count}</span></summary><p class="admin-stats-note">${esc(text('importCalendarFixSource'))}</p>${records.slice(page * 6, (page + 1) * 6).map(row => `<article class="admin-identity-pair admin-calendar-conflict"><div class="admin-identity-entity"><strong>${esc(row.event_name)}</strong><p class="admin-revision-meta">${esc(text(row.kind))}</p><p class="admin-calendar-source">${esc([source(row), period(row)].filter(Boolean).join(' · '))}</p>${row.original ? `<p class="admin-calendar-source">${esc([source(row.original), period(row.original)].filter(Boolean).join(' · '))}</p>` : ''}</div><div class="admin-center-actions">${row.event_id ? `<a class="quiet-button outline-command-button" href="#/events/${row.event_id}?from=admin&return_to=${encodeURIComponent(route)}">Leverage ID ${row.event_id}</a>` : ''}</div></article>`).join('')}${records.length > 6 ? `<div class="admin-import-pagination"><button type="button" class="quiet-button outline-command-button" data-calendar-conflict-page="${page - 1}" ${page === 0 ? 'disabled' : ''}>${esc(text('importPreviousPage'))}</button><span>${page * 6 + 1}–${Math.min((page + 1) * 6, records.length)} / ${records.length} · ${esc(text('importCalendarSources'))}</span><button type="button" class="quiet-button outline-command-button" data-calendar-conflict-page="${page + 1}" ${(page + 1) * 6 >= records.length ? 'disabled' : ''}>${esc(text('importNextPage'))}</button></div>` : ''}</details>`;
    root.querySelector('[data-calendar-conflicts]').ontoggle = event => { if (event.target.isConnected) viewState.open = event.target.open; };
    root.querySelectorAll('[data-calendar-conflict-page]').forEach(control => control.onclick = () => { viewState.page = Number(control.dataset.calendarConflictPage); render(); });
  };
  render();
}

export function mountImportReport({root, preview, text, esc, language}) {
  const stats = preview.event_match_decision_stats || {};
  root.innerHTML = renderEntityImportMetrics({
    rows: preview.event_summaries || [], idKey: 'event_id', text, esc, language,
    pending: stats.unresolved ?? (preview.event_match_review || []).filter(row => !row.deferred).length,
    deferred: stats.deferred || 0,
  });
  const skipped = preview.skipped_existing_events || [];
  if (skipped.length) root.insertAdjacentHTML('beforeend',
    `<p class="admin-stats-note admin-import-historical-total"><strong>${new Intl.NumberFormat(language).format(skipped.length)} ${esc(text(skipped.length === 1 ? 'importHistoricalSingle' : 'importHistorical'))}</strong></p>`);
}
