import { automaticImportIssueCode } from './admin-import-report.js?v=country-review-spacing-20261007';

export function cleanSourceScoreDisplay(value) {
  if (value == null || String(value).trim() === '') return value;
  const numeric = Number(String(value).replace(',', '.'));
  if (!Number.isFinite(numeric)) return value;
  const rounded = Math.round(numeric * 1000) / 1000;
  return Math.abs(numeric - rounded) < 1e-9 ? rounded : value;
}

export function mountImportResolution({root, preview, draft, text, esc, button, field, report, markChanged, confirm, guard}) {
  const resultIssues = (preview.issues || []).filter(issue => !automaticImportIssueCode(issue) && !['events', 'athletes'].includes(issue.review_scope));
  const sourceKeys = new Set([
    ...(preview.conflicts || []).map(row => `${row.source_sheet}:${row.source_row}`),
    ...resultIssues.map(row => `${row.sheet}:${row.row}`),
    ...Object.entries(draft.source || {}).filter(([, decision]) => decision.action === 'exclude' || Object.keys(decision.values || {}).some(key => key.toLowerCase().trim() !== 'country')).map(([key]) => key),
  ]);
  for (const row of preview.source_review || []) {
    if (sourceKeys.has(`${row.sheet}:${row.row}`)) {
      for (const related of row.related_rows || []) sourceKeys.add(`${related.sheet}:${related.row}`);
    }
  }
  const rows = (preview.source_review || []).filter(row => sourceKeys.has(`${row.sheet}:${row.row}`));
  if (!rows.length) {
    const pending = preview.conflicts?.length || preview.orphan_dscore_review_count || preview.orphan_dscore_review?.length ||
      resultIssues.some(issue => issue.severity === 'error' || issue.row != null || issue.code === 'gymternet_orphan_dscores');
    root.innerHTML = pending ? '' : `<div class="admin-center-feedback" data-import-empty="results" role="status">${esc(text('importNoCorrections'))}</div>`;
    return {focus() {}};
  }
  const keyOf = row => `${row.sheet}:${row.row}`;
  const pageSize = 6;
  let page = Math.min(draft.sourcePage || 0, Math.max(0, Math.ceil(rows.length / pageSize) - 1));
  const pendingRows = () => rows.filter(row => draft.source[keyOf(row)]?.action !== 'exclude' && (
    (preview.conflicts || []).some(item => item.source_sheet === row.sheet && item.source_row === row.row) ||
    resultIssues.some(item => item.severity === 'error' && item.sheet === row.sheet && item.row === row.row)));
  const exclude = row => { draft.source[keyOf(row)] = {sheet: row.sheet, row: row.row, fingerprint: row.fingerprint, action: 'exclude'}; };
  const render = () => {
    const pending = pendingRows();
    draft.sourcePage = page;
    root.innerHTML = `<details class="admin-revision-group" data-source-group ${draft.sourceOpen ? 'open' : ''}><summary>${esc(text('importCorrections'))}<span class="admin-revision-count">${rows.length}</span></summary><p class="admin-stats-note">${esc(text('importSourceNote'))}</p>${pending.length ? `<div class="admin-center-actions">${button('importExcludeAllRows', 'data-source-exclude-all')}</div>` : ''}<div data-source-rows>${rows.slice(page * pageSize, (page + 1) * pageSize).map((row, offset) => {
      const index = page * pageSize + offset, decision = draft.source[keyOf(row)];
      const identity = Object.entries(row.values).filter(([key]) => ['athlete', 'name', 'event', 'country'].includes(key.toLowerCase())).map(([, value]) => value).join(' · ');
      const conflicts = (preview.conflicts || []).filter(item => item.source_sheet === row.sheet && item.source_row === row.row);
      const comparison = conflicts.map(item => `<div class="admin-source-comparison"><p class="admin-revision-meta">${esc([item.event_name, item.year, item.apparatus, text(item.reason)].filter(Boolean).join(' · '))}</p><div class="admin-identity-pair-grid admin-audit-comparison"><section class="admin-audit-side"><h3>${esc(text(item.existing_result_id ? 'importDatabase' : 'previous'))}</h3>${report({score: item.existing_score, D_score: item.existing_D_score, country: item.existing_country})}</section><section class="admin-audit-side"><h3>${esc(text('importFile'))}</h3>${report({score: item.score, D_score: item.D_score, country: item.country})}</section></div></div>`).join('');
      return `<article class="admin-identity-pair admin-source-row" data-source-index="${index}"><div><strong>${esc(identity)}</strong><p class="admin-revision-meta">${esc(row.sheet)} · ${esc(text('importSourceRow'))} ${row.row}${decision ? ` · ${esc(text(decision.action === 'exclude' ? 'importRowExcluded' : 'importRowCorrected'))}` : ''}</p></div><div class="admin-center-actions">${button('importEditRow', 'data-source-edit aria-expanded="false"')}${button('importExcludeRow', 'data-source-exclude')}${decision ? button('importUndoRow', 'data-source-undo') : ''}</div><div data-source-fields hidden>${comparison}<div class="admin-form-grid">${(row.editable_fields || []).map((key, i) => field(`source_${i}`, key, 'text', cleanSourceScoreDisplay(decision?.values?.[key] ?? row.values[key]))).join('')}</div><div class="admin-center-actions">${button('importApplyDecision', 'data-source-apply')}</div></div></article>`;
    }).join('')}</div>${rows.length > pageSize ? `<div class="admin-import-pagination">${button('importPreviousPage', `data-source-page="-1" ${page === 0 ? 'disabled' : ''}`)}<span>${page * pageSize + 1}–${Math.min((page + 1) * pageSize, rows.length)} / ${rows.length}</span>${button('importNextPage', `data-source-page="1" ${(page + 1) * pageSize >= rows.length ? 'disabled' : ''}`)}</div>` : ''}</details>`;
    root.querySelector('[data-source-group]').ontoggle = event => { if (event.target.isConnected) draft.sourceOpen = event.target.open; };
    root.querySelectorAll('[data-source-index]').forEach(article => {
      const row = rows[Number(article.dataset.sourceIndex)];
      article.querySelector('[data-source-edit]').onclick = () => {
        const fields = article.querySelector('[data-source-fields]');
        fields.hidden = !fields.hidden;
        article.querySelector('[data-source-edit]').setAttribute('aria-expanded', String(!fields.hidden));
      };
      article.querySelectorAll('input').forEach((input, i) => {
        input.inputMode = 'decimal';
        input.oninput = () => {
          const values = {...draft.source[keyOf(row)]?.values, [row.editable_fields[i]]: input.value};
          draft.source[keyOf(row)] = {sheet: row.sheet, row: row.row, fingerprint: row.fingerprint, action: 'edit', values};
          markChanged();
        };
      });
      article.querySelector('[data-source-apply]').onclick = render;
      article.querySelector('[data-source-exclude]').onclick = () => confirm(text('importExcludeRowConfirm'), () => { exclude(row); markChanged(); render(); }, false, text('importSourceNote'));
      article.querySelector('[data-source-undo]')?.addEventListener('click', guard(() => { delete draft.source[keyOf(row)]; markChanged(); render(); }));
    });
    root.querySelector('[data-source-exclude-all]')?.addEventListener('click', () => confirm(text(pending.length === 1 ? 'importExcludeRowConfirm' : 'importExcludeRowsConfirm').replace('{n}', pending.length), () => {
      pending.forEach(exclude); markChanged(); render();
    }, false, text('importSourceNote')));
    root.querySelectorAll('[data-source-page]').forEach(control => control.onclick = () => { page += Number(control.dataset.sourcePage); render(); });
  };
  render();
  return {focus(sheet, number) {
    const index = rows.findIndex(row => row.sheet === sheet && row.row === number);
    if (index < 0) return;
    draft.sourceOpen = true; page = Math.floor(index / pageSize); render();
    const article = root.querySelector(`[data-source-index="${index}"]`);
    article.querySelector('[data-source-edit]').click();
    article.scrollIntoView({behavior: 'smooth', block: 'center'});
  }};
}
