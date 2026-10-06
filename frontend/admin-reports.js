const LABELS = {
  reversal_state: ['Recovery snapshot', 'Dati di ripristino', 'Datos de recuperación', 'Données de restauration'],
  field: ['Field', 'Campo', 'Campo', 'Champ'],
  changes: ['Changed fields', 'Campi modificati', 'Campos modificados', 'Champs modifiés'],
  unchanged: ['Unchanged fields', 'Campi invariati', 'Campos sin cambios', 'Champs inchangés'],
  inserted: ['Inserted data', 'Dati inseriti', 'Datos insertados', 'Données créées'],
  previous: ['Previous data', 'Dati precedenti', 'Datos anteriores', 'Données précédentes'],
  missing: ['Not set', 'Non impostato', 'Sin establecer', 'Non renseigné'],
  absent: ['Not present', 'Non presente', 'No presente', 'Absent'],
  results_count: ['Results', 'Risultati', 'Resultados', 'Résultats'],
  yes: ['Yes', 'Sì', 'Sí', 'Oui'], no: ['No', 'No', 'No', 'Non'],
  item: ['Item', 'Elemento', 'Elemento', 'Élément'],
  source_athlete: ['Source athlete', 'Atleta da unire', 'Atleta de origen', 'Athlète source'],
  target_athlete: ['Destination athlete', 'Atleta da mantenere', 'Atleta de destino', 'Athlète cible'],
  source_event: ['Source event', 'Evento da unire', 'Evento de origen', 'Événement source'],
  target_event: ['Destination event', 'Evento da mantenere', 'Evento de destino', 'Événement cible'],
  can_merge: ['Merge allowed', 'Unione consentita', 'Unión permitida', 'Fusion autorisée'],
  blockers: ['Blocking issues', 'Problemi bloccanti', 'Problemas bloqueantes', 'Problèmes bloquants'],
  warnings: ['Warnings', 'Avvisi', 'Avisos', 'Avertissements'],
  blocking_reasons: ['Blocking issues', 'Problemi bloccanti', 'Problemas bloqueantes', 'Problèmes bloquants'],
  result_conflicts: ['Conflicting results', 'Risultati in conflitto', 'Resultados en conflicto', 'Résultats en conflit'],
  merge_effects: ['Merge details', 'Effetti dell’unione', 'Detalles de la unión', 'Détails de la fusion'],
  metadata_to_copy: ['Data to copy', 'Dati da trasferire', 'Datos que transferir', 'Données à transférer'],
  metadata_differences: ['Different data', 'Dati differenti', 'Datos diferentes', 'Données différentes'],
  verification_requires_reconfirmation: ['Verification must be reconfirmed', 'Verifica da riconfermare', 'Verificación por confirmar', 'Vérification à reconfirmer'],
  rows: ['Source rows', 'Righe sorgente', 'Filas de origen', 'Lignes source'],
  id: ['Leverage ID', 'Leverage ID', 'Leverage ID', 'Leverage ID'],
  athlete_id: ['Athlete ID', 'ID atleta', 'ID atleta', 'ID athlète'],
  event_id: ['Event ID', 'ID evento', 'ID evento', 'ID événement'],
  event_name: ['Competition', 'Gara', 'Competición', 'Compétition'],
  source_sheet: ['Source sheet', 'Foglio sorgente', 'Hoja de origen', 'Feuille source'],
  source_row: ['Source row', 'Riga sorgente', 'Fila de origen', 'Ligne source'],
  created_at: ['Created on', 'Data di creazione', 'Fecha de creación', 'Date de création'],
  deleted_at: ['Deleted on', 'Data di eliminazione', 'Fecha de eliminación', 'Date de suppression'],
  deleted_by_admin_id: ['Deleted by admin ID', 'Eliminato da admin ID', 'Eliminado por admin ID', 'Supprimé par admin ID'],
  is_deleted: ['Deleted', 'Eliminato', 'Eliminado', 'Supprimé'],
  is_profile_verified: ['Verified profile', 'Profilo verificato', 'Perfil verificado', 'Profil vérifié'],
  score: ['Final Score', 'Final Score', 'Final Score', 'Final Score'],
  D_score: ['D Score', 'D Score', 'D Score', 'D Score'],
  E_score: ['E Score', 'E Score', 'E Score', 'E Score'],
  world_gymnastics_athlete_id: ['FIG ID', 'FIG ID', 'FIG ID', 'FIG ID'],
  world_gymnastics_event_id: ['FIG ID', 'FIG ID', 'FIG ID', 'FIG ID'],
  world_gymnastics_profile_url: ['World Gymnastics profile', 'Profilo World Gymnastics', 'Perfil World Gymnastics', 'Profil World Gymnastics'],
  world_gymnastics_event_url: ['World Gymnastics event', 'Evento World Gymnastics', 'Evento World Gymnastics', 'Événement World Gymnastics'],
  world_gymnastics_status: ['World Gymnastics status', 'Status World Gymnastics', 'Estado World Gymnastics', 'Statut World Gymnastics'],
  world_gymnastics_verified_at: ['Verification date', 'Data di verifica', 'Fecha de verificación', 'Date de vérification'],
  world_gymnastics_verified_by_admin_id: ['Verified by admin ID', 'Verificato da admin ID', 'Verificado por admin ID', 'Vérifié par admin ID'],
};

export function createAdminReport({text, esc, language}) {
  const index = Math.max(0, ['en', 'it', 'es', 'fr'].indexOf(language));
  const label = key => LABELS[key]?.[index] || (text(key) !== key ? text(key) : key.replace(/_/g, ' ').replace(/^./, c => c.toUpperCase()));
  const scalar = (value, key) => {
    if (value == null || value === '') return `<span class="admin-report-muted">${esc(label('missing'))}</span>`;
    if (typeof value === 'boolean') return esc(label(value ? 'yes' : 'no'));
    if (typeof value === 'number') return esc(new Intl.NumberFormat(language, key === 'D_score' ? {minimumFractionDigits: 1, maximumFractionDigits: 1} : {maximumFractionDigits: 6}).format(value));
    if (typeof value === 'string' && /^\d{4}-\d{2}-\d{2}(T.*)?$/.test(value)) {
      const date = new Date(value.length === 10 ? `${value}T00:00:00` : /Z$|[+-]\d{2}:\d{2}$/.test(value) ? value : `${value}Z`);
      if (!Number.isNaN(date.valueOf())) return esc(new Intl.DateTimeFormat(language, {dateStyle: 'medium', ...(value.length > 10 ? {timeStyle: 'short'} : {})}).format(date));
    }
    return esc(String(value));
  };
  const disclosure = (title, body, count) => `<details class="admin-report-disclosure"><summary>${esc(title)}${count == null ? '' : `<span class="admin-revision-count">${count}</span>`}</summary>${body}</details>`;
  const report = (value, key = '') => {
    if (value == null || typeof value !== 'object') return scalar(value, key);
    if (!Array.isArray(value) && Object.keys(value).length === 2 && 'before' in value && 'after' in value) return comparison(value.before, value.after);
    if ('can_merge' in value && (value.source_athlete || value.source_event)) return mergePreview(value);
    if (Array.isArray(value)) return value.length ? `<ol class="admin-report-list">${value.map((entry, i) => `<li>${entry && typeof entry === 'object' ? disclosure([entry.name || [entry.last_name, entry.first_name].filter(Boolean).join(' ') || label('item'), entry.id != null ? `#${entry.id}` : i + 1].join(' · '), report(entry)) : report(entry, key)}</li>`).join('')}</ol>` : `<span class="admin-report-muted">${esc(text('empty'))}</span>`;
    return `<dl class="admin-report">${Object.entries(value).map(([field, entry]) => `<div${entry && typeof entry === 'object' ? ' class="admin-report-group"' : ''}>${entry && typeof entry === 'object' ? `<dt>${esc(label(field))}</dt><dd>${disclosure(label(field), report(entry, field), Array.isArray(entry) ? entry.length : null)}</dd>` : `<dt>${esc(label(field))}</dt><dd>${report(entry, field)}</dd>`}</div>`).join('')}</dl>`;
  };
  const mergePreview = preview => {
    const kind = preview.source_athlete ? 'athlete' : 'event';
    const fields = ['id', 'discipline', 'country', 'birth_date', 'birth_year', 'year', 'category', 'start_date', 'end_date', 'location', 'world_gymnastics_athlete_id', 'world_gymnastics_event_id'];
    const source = preview[`source_${kind}`], target = preview[`target_${kind}`];
    const visibleFields = fields.filter(key => [source, target].some(row => row?.[key] != null && row[key] !== ''));
    const side = (row, role) => {
      const name = [row?.last_name, row?.first_name].filter(Boolean).join(' ') || row?.name || label('missing');
      const values = Object.fromEntries(visibleFields.map(key => [key, row?.[key] ?? null]));
      values.results_count = preview[`${role}_result_count`] ?? null;
      return `<section class="admin-audit-side"><h3>${esc(label(`${role}_${kind}`))}</h3><div class="admin-audit-entity"><strong>${esc(name)}</strong>${report(values)}</div></section>`;
    };
    const omitted = new Set(['source_athlete', 'target_athlete', 'source_event', 'target_event', 'source_result_count', 'target_result_count', 'can_merge', 'preview_token', 'blocking_reasons', 'result_conflicts']);
    const effects = Object.fromEntries(Object.entries(preview).filter(([key, value]) => !omitted.has(key) && value != null && value !== false && value !== 0 && value !== '' && (typeof value !== 'object' || Object.keys(value).length)));
    const blockers = preview.blocking_reasons?.length ? `<div class="admin-center-feedback is-error"><strong>${esc(label('blocking_reasons'))}</strong>${report(preview.blocking_reasons)}</div>` : '';
    const conflicts = preview.result_conflicts?.length ? report({result_conflicts: preview.result_conflicts}) : '';
    return `<div class="admin-identity-pair-grid admin-audit-comparison">${side(source, 'source')}${side(target, 'target')}</div>${report({can_merge: preview.can_merge})}${blockers}${conflicts}${Object.keys(effects).length ? disclosure(label('merge_effects'), report(effects)) : ''}`;
  };
  const comparison = (before, after) => {
    const technical = new Set(['created_at', 'updated_at', 'deleted_at', 'deleted_by_admin_id', 'world_gymnastics_verified_by_admin_id']);
    const identity = ['id', 'last_name', 'first_name', 'name', 'discipline', 'country', 'year', 'athlete_id', 'event_id', 'apparatus', 'round', 'format', 'category'];
    const entities = snapshot => {
      if (!snapshot) return [];
      const nested = ['source_athlete', 'target_athlete', 'source_event', 'target_event'].filter(key => snapshot[key]);
      if (nested.length) return nested.map(key => ({key, row: snapshot[key]}));
      if (Array.isArray(snapshot.entities)) return snapshot.entities.map(row => ({key: String(row.id), row}));
      return [{key: 'entity', row: snapshot}];
    };
    const left = entities(before), right = entities(after);
    const keys = [...new Set([...left, ...right].map(entry => entry.key))];
    const selected = new Map(keys.map(key => {
      const a = left.find(entry => entry.key === key)?.row || {};
      const b = right.find(entry => entry.key === key)?.row || {};
      const fields = [...new Set([...Object.keys(a), ...Object.keys(b)])].filter(field => !technical.has(field)
        && (field !== 'is_deleted' || a[field] || b[field])
        && (a[field] == null || typeof a[field] !== 'object') && (b[field] == null || typeof b[field] !== 'object')
        && !field.endsWith('_count') && !field.startsWith('moved_') && !field.startsWith('removed_')
        && !['reason', 'relinked_notifications'].includes(field)
        && (identity.includes(field) || JSON.stringify(a[field]) !== JSON.stringify(b[field]))
        && (a[field] != null || b[field] != null));
      return [key, [...identity.filter(field => fields.includes(field)), ...fields.filter(field => !identity.includes(field))]];
    }));
    const resultCount = (snapshot, id) => {
      const rows = snapshot?.reversal_state?.results || snapshot?.results;
      const owner = snapshot?.source_athlete ? 'athlete_id' : snapshot?.source_event ? 'event_id' : null;
      if (Array.isArray(rows) && owner) return rows.filter(row => row[owner] === id).length;
      if (snapshot?.source_athlete?.id === id && Array.isArray(snapshot.source_result_ids)) return snapshot.source_result_ids.length;
      if (snapshot?.target_athlete?.id === id && Array.isArray(snapshot.target_result_ids_before)) return snapshot.target_result_ids_before.length;
      if (snapshot === after && typeof snapshot?.moved_results === 'number' && Array.isArray(before?.target_result_ids_before)) {
        if (snapshot.source_athlete?.id === id) return 0;
        if (snapshot.target_athlete?.id === id) return before.target_result_ids_before.length + snapshot.moved_results;
      }
      return null;
    };
    const side = (snapshot, entries, title) => `<section class="admin-audit-side"><h3>${esc(text(title))}</h3>${entries.length ? entries.map(({key, row}) => {
      const fields = selected.get(key);
      const name = [row.last_name, row.first_name].filter(Boolean).join(' ') || row.name;
      const values = Object.fromEntries(fields.filter(field => !['last_name', 'first_name', 'name'].includes(field)).map(field => [field, row[field] ?? null]));
      const count = entries.length > 1 ? resultCount(snapshot, row.id) : null;
      if (count != null) values.results_count = count;
      const hasName = fields.some(field => ['last_name', 'first_name', 'name'].includes(field));
      return `<div class="admin-audit-entity">${key.startsWith('source_') || key.startsWith('target_') ? `<p class="admin-revision-meta">${esc(label(key))}</p>` : ''}${hasName ? `<strong>${esc(name || label('missing'))}</strong>` : ''}${report(values)}</div>`;
    }).join('') : `<p class="admin-report-muted">${esc(label('absent'))}</p>`}</section>`;
    return `<div class="admin-identity-pair-grid admin-audit-comparison">${side(before, left, 'before')}${side(after, right, 'after')}</div>`;
  };
  return report;
}
