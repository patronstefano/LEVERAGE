const LABELS = {
  field: ['Field', 'Campo', 'Campo', 'Champ'],
  changes: ['Changed fields', 'Campi modificati', 'Campos modificados', 'Champs modifiés'],
  unchanged: ['Unchanged fields', 'Campi invariati', 'Campos sin cambios', 'Champs inchangés'],
  inserted: ['Inserted data', 'Dati inseriti', 'Datos insertados', 'Données créées'],
  previous: ['Previous data', 'Dati precedenti', 'Datos anteriores', 'Données précédentes'],
  missing: ['Not set', 'Non impostato', 'Sin establecer', 'Non renseigné'],
  yes: ['Yes', 'Sì', 'Sí', 'Oui'], no: ['No', 'No', 'No', 'Non'],
  item: ['Item', 'Elemento', 'Elemento', 'Élément'],
  source_athlete: ['Source athlete', 'Atleta da unire', 'Atleta de origen', 'Athlète source'],
  target_athlete: ['Destination athlete', 'Atleta da mantenere', 'Atleta de destino', 'Athlète cible'],
  source_event: ['Source event', 'Evento da unire', 'Evento de origen', 'Événement source'],
  target_event: ['Destination event', 'Evento da mantenere', 'Evento de destino', 'Événement cible'],
  can_merge: ['Merge allowed', 'Unione consentita', 'Unión permitida', 'Fusion autorisée'],
  blockers: ['Blocking issues', 'Problemi bloccanti', 'Problemas bloqueantes', 'Problèmes bloquants'],
  warnings: ['Warnings', 'Avvisi', 'Avisos', 'Avertissements'],
  rows: ['Source rows', 'Righe sorgente', 'Filas de origen', 'Lignes source'],
  id: ['Leverage ID', 'Leverage ID', 'Leverage ID', 'Leverage ID'],
  athlete_id: ['Athlete ID', 'ID atleta', 'ID atleta', 'ID athlète'],
  event_id: ['Event ID', 'ID evento', 'ID evento', 'ID événement'],
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
    if (Array.isArray(value)) return value.length ? `<ol class="admin-report-list">${value.map((entry, i) => `<li>${entry && typeof entry === 'object' ? disclosure([entry.name || [entry.last_name, entry.first_name].filter(Boolean).join(' ') || label('item'), entry.id != null ? `#${entry.id}` : i + 1].join(' · '), report(entry)) : report(entry, key)}</li>`).join('')}</ol>` : `<span class="admin-report-muted">${esc(text('empty'))}</span>`;
    return `<dl class="admin-report">${Object.entries(value).map(([field, entry]) => `<div${entry && typeof entry === 'object' ? ' class="admin-report-group"' : ''}>${entry && typeof entry === 'object' ? `<dt>${esc(label(field))}</dt><dd>${disclosure(label(field), report(entry, field), Array.isArray(entry) ? entry.length : null)}</dd>` : `<dt>${esc(label(field))}</dt><dd>${report(entry, field)}</dd>`}</div>`).join('')}</dl>`;
  };
  const comparison = (before, after) => {
    if (!before || !after) return `<section class="admin-report-section"><h3>${esc(label(before ? 'previous' : 'inserted'))}</h3>${report(before || after || {})}</section>`;
    const keys = [...new Set([...Object.keys(before), ...Object.keys(after)])];
    const equal = (a, b) => JSON.stringify(a) === JSON.stringify(b);
    const changed = keys.filter(key => !equal(before[key], after[key]));
    const unchanged = keys.filter(key => equal(before[key], after[key]));
    const table = changed.length ? `<div class="admin-comparison" role="table" aria-label="${esc(label('changes'))}"><div class="admin-comparison-row admin-comparison-head" role="row"><span role="columnheader">${esc(label('field'))}</span><span role="columnheader">${esc(text('before'))}</span><span role="columnheader">${esc(text('after'))}</span></div>${changed.map(key => `<div class="admin-comparison-row" role="row"><strong role="rowheader">${esc(label(key))}</strong><div role="cell"><span class="admin-comparison-mobile">${esc(text('before'))}</span>${report(before[key], key)}</div><div role="cell"><span class="admin-comparison-mobile">${esc(text('after'))}</span>${report(after[key], key)}</div></div>`).join('')}</div>` : `<p class="admin-report-muted">${esc(label('unchanged'))}</p>`;
    return table + (unchanged.length ? disclosure(label('unchanged'), report(Object.fromEntries(unchanged.map(key => [key, after[key]]))), unchanged.length) : '');
  };
  return report;
}
