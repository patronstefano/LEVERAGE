export const IMPORT_COPY = {
  importChangeFile: ['Change file', 'Cambia file', 'Cambiar archivo', 'Changer de fichier'],
  importHideFile: ['Close parameters', 'Chiudi parametri', 'Cerrar parámetros', 'Fermer les paramètres'],
  importBlocking: ['To resolve', 'Da risolvere', 'Por resolver', 'À résoudre'],
  importReadOnly: ['Existing scores will not be overwritten.', 'I punteggi già salvati non verranno sovrascritti.', 'Los resultados guardados no se sobrescribirán.', 'Les scores existants ne seront pas remplacés.'],
  importCalendarRows: ['Calendar entries', 'Voci calendario', 'Entradas del calendario', 'Entrées du calendrier'],
  importCalendarMatched: ['Matched events', 'Gare associate', 'Competiciones asociadas', 'Compétitions associées'],
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
  importResolveRows: ['Resolve source rows', 'Correggi righe del file', 'Corregir filas del archivo', 'Corriger les lignes du fichier'],
  importSourceNote: ['Edits apply only to this import, not to the original file or existing scores. Excluding a source row omits all its scores.', 'Le correzioni riguardano solo questa importazione, non il file originale o i punteggi già salvati. Tralasciare una riga esclude tutti i suoi punteggi.', 'Las correcciones afectan solo a esta importación, no al archivo original ni a los resultados guardados. Omitir una fila excluye todas sus puntuaciones.', 'Les corrections concernent uniquement cet import, pas le fichier original ni les scores existants. Exclure une ligne exclut tous ses scores.'],
  importEditRow: ['Correct row', 'Correggi riga', 'Corregir fila', 'Corriger la ligne'],
  importExcludeRow: ['Skip row', 'Tralascia riga', 'Omitir fila', 'Exclure la ligne'],
  importExcludeAllRows: ['Skip unresolved source rows', 'Tralascia tutte le righe da correggere', 'Omitir las filas pendientes', 'Exclure les lignes à corriger'],
  importExcludeRowsConfirm: ['Skip {n} source rows and all their scores in this import?', 'Tralasciare {n} righe del file e tutti i relativi punteggi in questa importazione?', '¿Omitir {n} filas y todas sus puntuaciones de esta importación?', 'Exclure {n} lignes et tous leurs scores de cet import ?'],
  importRowExcluded: ['Excluded', 'Tralasciata', 'Excluida', 'Exclue'],
  importRowCorrected: ['Proposed correction', 'Correzione proposta', 'Corrección propuesta', 'Correction proposée'],
  importUndoRow: ['Restore source row', 'Ripristina riga originale', 'Restaurar fila original', 'Restaurer la ligne originale'],
  importInvalidCorrection: ['Enter a valid non-negative score, or explicitly skip the source row.', 'Inserisci un punteggio numerico valido e non negativo, oppure tralascia esplicitamente la riga.', 'Introduce una puntuación válida no negativa u omite explícitamente la fila.', 'Saisissez un score valide non négatif, ou excluez explicitement la ligne.'],
  importApplyDecision: ['Apply decision', 'Applica decisione', 'Aplicar decisión', 'Appliquer la décision'],
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
  importHistoricalDifferences: ['Differences in historical data', 'Incongruenze sui dati già importati', 'Diferencias en datos ya importados', 'Différences dans les données déjà importées'],
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
  importCandidatesNote: ['Counts are provisional until identity reviews are resolved and the preview is recalculated.', 'I conteggi sono provvisori fino alla risoluzione dei conflitti di identità e al ricalcolo dell’anteprima.', 'Los recuentos son provisionales hasta resolver las identidades y recalcular la vista previa.', 'Les totaux sont provisoires avant résolution des identités et recalcul de l’aperçu.'],
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
  importNeedsPreview: ['Recalculate the preview to apply your decisions before importing.', 'Ricalcola l’anteprima per applicare le decisioni prima dell’importazione.', 'Recalcula la vista previa para aplicar las decisiones antes de importar.', 'Recalculez l’aperçu pour appliquer les décisions avant l’importation.'],
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

export function renderImportIssues({issues, text, esc, language, sourceRows = []}) {
  const ordered = [...issues].sort((a, b) => Number(b.severity === 'error') - Number(a.severity === 'error'));
  const score = value => new Intl.NumberFormat(language, {minimumFractionDigits: 3, maximumFractionDigits: 3}).format(value);
  return `<ul class="admin-import-issues">${ordered.slice(0, 6).map(issue => {
    const known = issue.code === 'derived_vt_outlier';
    const message = known ? text(issue.possible_rounding ? 'importVtRounding' : 'importVtInvalid') : issue.code === 'source_correction_invalid' ? text('importInvalidCorrection') : issue.message;
    const identity = [[issue.last_name, issue.first_name].filter(Boolean).join(' '), issue.event_name].filter(Boolean).join(' · ');
    const source = [issue.sheet ? `${text('importSourceSheet')} ${issue.sheet}` : '', issue.row != null ? `${text('importSourceRow')} ${issue.row}` : ''].filter(Boolean).join(' · ');
    return `<li><strong>${esc(identity || source)}</strong>${identity && source ? `<p class="admin-revision-meta">${esc(source)}</p>` : ''}<p class="${issue.severity === 'error' ? 'admin-import-issue-error' : ''}">${esc(message)}</p>${known ? `<p class="admin-revision-meta">2 × VT AVG ${score(issue.source_vt_avg)} − VT ${score(issue.source_vt)} = ${score(issue.original_score)}</p>` : ''}${sourceRows.some(row => row.sheet === issue.sheet && row.row === issue.row) ? `<div class="admin-center-actions"><button type="button" class="quiet-button outline-command-button" data-correct-issue-sheet="${esc(issue.sheet)}" data-correct-issue-row="${issue.row}">${esc(text('importEditRow'))}</button></div>` : ''}</li>`;
  }).join('')}</ul>${ordered.length > 6 ? `<p class="admin-stats-note">${esc(text('importIssueSample'))}</p>` : ''}`;
}

export function renderImportMetrics({items, text, esc, language}) {
  const count = value => new Intl.NumberFormat(language).format(value || 0);
  return `<dl class="admin-stats-metrics admin-duplicate-recap admin-import-metrics">${items.map(([key, value]) => `<div><dt>${esc(text(key))}</dt><dd>${count(value)}</dd></div>`).join('')}</dl>`;
}

export function mountCalendarImportRows({root, preview, text, esc, language, route, viewState}) {
  const rows = preview.rows || [], pageSize = 6;
  let page = Math.min(viewState.page || 0, Math.max(0, Math.ceil(rows.length / pageSize) - 1));
  const date = value => value ? new Intl.DateTimeFormat(language, {dateStyle: 'medium'}).format(new Date(`${value}T00:00:00`)) : '';
  const render = () => {
    viewState.page = page;
    root.innerHTML = `<details class="admin-revision-group" data-calendar-details ${viewState.open ? 'open' : ''}><summary>${esc(text('importCalendarRows'))}<span class="admin-revision-count">${rows.length}</span></summary>${rows.slice(page * pageSize, (page + 1) * pageSize).map(row => {
      const period = [date(row.start_date), row.end_date !== row.start_date ? date(row.end_date) : ''].filter(Boolean).join(' – ');
      const status = {update_dates: preview.committed ? 'importCalendarUpdated' : 'importCalendarUpdate', no_change: 'importCalendarUnchanged', create_event: preview.committed ? 'importCalendarCreated' : 'importStatusNew', skip_unmatched_historical: 'importCalendarUnmatched'}[row.action];
      return `<article class="admin-identity-pair"><div class="admin-identity-entity"><strong>${esc(row.event_name)}</strong><p class="admin-revision-meta">${esc(period)} · ${esc(text(status || 'importStatusConflict'))}</p></div><div class="admin-center-actions">${(row.matched_event_ids || []).map(id => `<a class="admin-revision-source" href="#/events/${id}?from=admin&return_to=${encodeURIComponent(route)}">ID ${id}</a>`).join('')}</div></article>`;
    }).join('')}${rows.length > pageSize ? `<div class="admin-import-pagination"><button type="button" class="quiet-button outline-command-button" data-calendar-page="-1" ${page === 0 ? 'disabled' : ''}>${esc(text('importPreviousPage'))}</button><span>${page * pageSize + 1}–${Math.min((page + 1) * pageSize, rows.length)} / ${rows.length}</span><button type="button" class="quiet-button outline-command-button" data-calendar-page="1" ${(page + 1) * pageSize >= rows.length ? 'disabled' : ''}>${esc(text('importNextPage'))}</button></div>` : ''}</details>`;
    root.querySelector('[data-calendar-details]').ontoggle = event => { if (event.target.isConnected) viewState.open = event.target.open; };
    root.querySelectorAll('[data-calendar-page]').forEach(control => control.onclick = () => { page += Number(control.dataset.calendarPage); render(); });
  };
  render();
}

export function mountImportReport({root, preview: p, text, esc, report, language, route, onCorrect, viewState = {}}) {
  const count = value => new Intl.NumberFormat(language).format(value || 0);
  const score = (value, digits) => value == null ? '—' : new Intl.NumberFormat(language, {minimumFractionDigits: digits, maximumFractionDigits: digits}).format(value);
  const athlete = row => [row.last_name, row.first_name].filter(Boolean).join(' ') || row.athlete_name || '';
  const date = value => value ? new Intl.DateTimeFormat(language, {dateStyle: 'medium'}).format(new Date(`${value}T00:00:00`)) : '';
  const context = row => [row.discipline, text(row.category), text(row.format), text(row.round), row.apparatus, row.day ? `${text('day')} ${row.day}` : ''].filter(Boolean).join(' · ');
  const button = (label, attrs) => `<button type="button" class="quiet-button outline-command-button" ${attrs}>${esc(text(label))}</button>`;
  const summary = p.event_summaries || [];
  const pending = (p.athlete_match_decision_stats?.unresolved || 0) + (p.event_match_decision_stats?.unresolved || 0);
  const existing = (p.duplicates || []).filter(row => row.reason === 'duplicate_existing').length + (p.skipped_existing_results || 0);
  const skipped = p.skipped_existing_events || [];
  const historicDifferences = skipped.filter(row => row.differences || row.source_issues);
  const pagination = (key) => `<div class="admin-import-pagination" data-pagination="${key}">${button('importPreviousPage', `data-prev="${key}"`)}<span data-page-label="${key}"></span>${button('importNextPage', `data-next="${key}"`)}</div>`;
  const pageSize = 6;
  const pages = viewState.pages ||= {events: 0, conflicts: 0, historical: 0};
  const pageItems = (key, items) => {
    pages[key] = Math.min(pages[key], Math.max(0, Math.ceil(items.length / pageSize) - 1));
    const start = pages[key] * pageSize;
    const pager = root.querySelector(`[data-pagination="${key}"]`);
    pager.hidden = items.length <= pageSize;
    pager.querySelector('[data-prev]').disabled = start === 0;
    pager.querySelector('[data-next]').disabled = start + pageSize >= items.length;
    pager.querySelector('[data-page-label]').textContent = `${start + 1}–${Math.min(start + pageSize, items.length)} / ${count(items.length)}`;
    return items.slice(start, start + pageSize);
  };
  root.innerHTML = renderImportMetrics({text, esc, language, items: [
    ['importFileRows', p.parsed_rows], [skipped.length ? 'importExcludedResults' : 'importExisting', skipped.length ? p.skipped_existing_results : existing], ['importNew', p.importable_results],
    ['importNewAthletes', p.would_create_athletes], ['importNewEvents', p.would_create_events], ['importPending', pending],
  ]}) + `
    ${skipped.length ? `<p class="admin-stats-note admin-import-historical-total"><strong>${count(skipped.length)} ${esc(text(skipped.length === 1 ? 'importHistoricalSingle' : 'importHistorical'))}</strong></p>${historicDifferences.length ? `<details class="admin-revision-group" data-import-historical><summary>${esc(text('importHistoricalDifferences'))}<span class="admin-revision-count">${count(historicDifferences.length)}</span></summary><p class="admin-stats-note">${esc(text('importHistoricalCaution'))}</p><div data-historical-rows></div>${pagination('historical')}</details>` : ''}` : ''}
    <details class="admin-revision-group" data-import-event-list><summary>${esc(text('importEvents'))}<span class="admin-revision-count">${count(summary.length)}</span></summary><div class="admin-center-actions admin-import-event-filters">${['all', 'existing', 'new', 'conflicts'].map((key, i) => `<button type="button" class="filter-button" data-import-filter="${key}" aria-pressed="${i === 0}">${esc(text(['importAllEvents', 'importExistingEvents', 'importNew', 'importStatusConflict'][i]))}</button>`).join('')}</div><div data-import-events></div>${pagination('events')}</details>
    ${(p.conflicts || []).length ? `<details class="admin-revision-group" data-import-conflict-list><summary>${esc(text('importConflicts'))}<span class="admin-revision-count">${count(p.conflicts.length)}</span></summary><div data-import-conflicts></div>${pagination('conflicts')}</details>` : ''}`;
  let filter = viewState.filter || 'all';
  for (const name of ['event-list', 'conflict-list', 'historical']) {
    const group = root.querySelector(`[data-import-${name}]`);
    if (!group) continue;
    group.open = Boolean(viewState[name]);
    group.ontoggle = () => { if (group.isConnected) viewState[name] = group.open; };
  }
  const list = root.querySelector('[data-import-events]');

  const eventDetails = event => `<h3>${esc(text('importGroups'))}</h3><div class="admin-import-table-scroll"><table class="admin-import-table"><thead><tr><th>${esc(text('importGroups'))}</th>${['importExisting', 'importNew', 'importConflicts', 'importFileDuplicates'].map(key => `<th>${esc(text(key))}</th>`).join('')}</tr></thead><tbody>${event.groups.map(group => `<tr><td>${esc(context(group))}</td>${['existing_results', 'new_results', 'conflicting_results', 'duplicate_file_results'].map(key => `<td>${count(group[key])}</td>`).join('')}</tr>`).join('')}</tbody></table></div>${event.new_results_preview.length ? `<h3>${esc(text('importSample'))}</h3><div class="admin-import-table-scroll"><table class="admin-import-table"><thead><tr><th>${esc(text('Athlete'))}</th><th>${esc(text('importGroups'))}</th><th>Final Score</th><th>D Score</th></tr></thead><tbody>${event.new_results_preview.map(row => `<tr><td>${esc(athlete(row))}<span class="admin-revision-meta"> · ${esc(row.country || '')}</span></td><td>${esc(context(row))}</td><td>${score(row.score, 3)}</td><td>${score(row.D_score, 1)}</td></tr>`).join('')}</tbody></table></div>` : ''}`;
  const toggle = (button, details, html) => {
    const open = details.hidden;
    if (open && !details.innerHTML) details.innerHTML = html();
    details.hidden = !open;
    button.setAttribute('aria-expanded', String(open));
  };
  const renderEvents = () => {
    const events = summary.filter(event => filter === 'all' || (filter === 'existing' ? event.status === 'already_imported' : filter === 'new' ? event.new_results > 0 : event.conflicting_results > 0));
    list.innerHTML = pageItems('events', events).map((event, i) => {
      const title = `${esc(event.event_name)}${event.event_name.includes(String(event.year)) ? '' : ` · ${event.year}`}`;
      return `<article class="admin-identity-pair admin-import-event"><div class="admin-identity-entity"><strong>${event.event_id ? `<a href="#/events/${event.event_id}?from=admin&return_to=${encodeURIComponent(route)}">${title}</a>` : title}</strong><p class="admin-revision-meta">${event.event_id ? `ID ${event.event_id}` : esc(text('importStatusNew'))}${event.start_date ? ` · ${esc(date(event.start_date))}${event.end_date && event.end_date !== event.start_date ? ` – ${esc(date(event.end_date))}` : ''}` : ''}</p><p class="admin-revision-meta">${[['importExisting', event.existing_results], ['importNew', event.new_results], ['importConflicts', event.conflicting_results], ['importFileDuplicates', event.duplicate_file_results]].filter(([, value]) => value).map(([key, value]) => `${esc(text(key))}: ${count(value)}`).join(' · ')}</p></div><div class="admin-center-actions">${button('importCompare', `data-import-event="${i}" aria-expanded="false"`)}</div><div data-pair-details hidden></div></article>`;
    }).join('') || `<div class="empty-state">${esc(text('empty'))}</div>`;

    list.querySelectorAll('[data-import-event]').forEach(control => {
      control.onclick = () => toggle(control, control.closest('article').querySelector('[data-pair-details]'), () => eventDetails(events[pages.events * pageSize + Number(control.dataset.importEvent)]));
    });
  };
  root.querySelectorAll('[data-import-filter]').forEach(control => control.onclick = () => {
    filter = viewState.filter = control.dataset.importFilter; pages.events = 0;
    root.querySelectorAll('[data-import-filter]').forEach(item => item.setAttribute('aria-pressed', String(item === control)));
    renderEvents();
  });
  root.querySelectorAll('[data-import-filter]').forEach(control => control.setAttribute('aria-pressed', String(control.dataset.importFilter === filter)));

  renderEvents();
  const renderConflicts = () => {
    const conflicts = root.querySelector('[data-import-conflicts]');
    if (!conflicts) return;
    conflicts.innerHTML = pageItems('conflicts', p.conflicts).map((row, i) => `<article class="admin-identity-pair"><div><strong>${esc(athlete(row))}</strong><p class="admin-revision-meta">${esc(row.event_name)} · ${row.year} · ${esc(context(row))}</p><p class="admin-revision-meta">${esc(text(row.reason))}</p></div><div class="admin-center-actions">${button('importCompare', `data-import-conflict="${i}" aria-expanded="false"`)}${onCorrect ? button('importEditRow', `data-correct-conflict="${i}"`) : ''}</div><div data-pair-details hidden></div></article>`).join('');
    conflicts.querySelectorAll('[data-import-conflict]').forEach(control => control.onclick = () => {
      const row = p.conflicts[pages.conflicts * pageSize + Number(control.dataset.importConflict)];
      toggle(control, control.closest('article').querySelector('[data-pair-details]'), () => `<div class="admin-identity-pair-grid admin-audit-comparison"><section class="admin-audit-side"><h3>${esc(text(row.existing_result_id ? 'importDatabase' : 'previous'))}</h3>${report({score: row.existing_score, D_score: row.existing_D_score, country: row.existing_country})}</section><section class="admin-audit-side"><h3>${esc(text('importFile'))}</h3>${report({score: row.score, D_score: row.D_score, country: row.country, source_sheet: row.source_sheet, source_row: row.source_row})}</section></div>`);
    });
    conflicts.querySelectorAll('[data-correct-conflict]').forEach(control => control.onclick = () => {
      const row = p.conflicts[pages.conflicts * pageSize + Number(control.dataset.correctConflict)];
      onCorrect(row.source_sheet, row.source_row);
    });
  };
  renderConflicts();
  const renderHistorical = () => {
    const rows = root.querySelector('[data-historical-rows]');
    if (rows) rows.innerHTML = pageItems('historical', historicDifferences).map(row => `<article class="admin-import-historical-row"><strong>${esc(row.event_name)}</strong><p class="admin-revision-meta">${esc(text('importDifferences'))}: ${count(row.differences)} · ${esc(text('importIssueList'))}: ${count(row.source_issues)}</p></article>`).join('');
  };
  renderHistorical();
  root.querySelectorAll('[data-prev], [data-next]').forEach(control => control.onclick = () => {
    const key = control.dataset.prev || control.dataset.next;
    pages[key] += control.dataset.prev ? -1 : 1;
    ({events: renderEvents, conflicts: renderConflicts, historical: renderHistorical})[key]();
  });
}
