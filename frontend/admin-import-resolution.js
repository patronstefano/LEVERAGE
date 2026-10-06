export function mountImportResolution({root, preview, draft, text, esc, button, field, markChanged, apply, confirm, guard}) {
  const rows = preview.source_review || [];
  if (!rows.length) { root.innerHTML = ''; return {focus() {}}; }
  const keyOf = row => `${row.sheet}:${row.row}`;
  const pageSize = 6;
  let page = Math.min(draft.sourcePage || 0, Math.max(0, Math.ceil(rows.length / pageSize) - 1));
  const pending = rows.filter(row => draft.source[keyOf(row)]?.action !== 'exclude' && (
    (preview.conflicts || []).some(item => item.source_sheet === row.sheet && item.source_row === row.row) ||
    (preview.issues || []).some(item => item.severity === 'error' && item.sheet === row.sheet && item.row === row.row)));
  const exclude = row => { draft.source[keyOf(row)] = {sheet: row.sheet, row: row.row, fingerprint: row.fingerprint, action: 'exclude'}; };
  const render = () => {
    draft.sourcePage = page;
    root.innerHTML = `<details class="admin-revision-group" data-source-group ${draft.sourceOpen ? 'open' : ''}><summary>${esc(text('importResolveRows'))} · ${rows.length}</summary><p class="admin-stats-note">${esc(text('importSourceNote'))}</p>${pending.length ? `<div class="admin-center-actions">${button('importExcludeAllRows', 'data-source-exclude-all')}</div>` : ''}<div data-source-rows>${rows.slice(page * pageSize, (page + 1) * pageSize).map((row, offset) => {
      const index = page * pageSize + offset, decision = draft.source[keyOf(row)];
      const identity = Object.entries(row.values).filter(([key]) => ['athlete', 'name', 'event', 'country'].includes(key.toLowerCase())).map(([, value]) => value).join(' · ');
      return `<article class="admin-identity-pair admin-source-row" data-source-index="${index}"><div><strong>${esc(identity)}</strong><p class="admin-revision-meta">${esc(row.sheet)} · ${esc(text('importSourceRow'))} ${row.row}${decision ? ` · ${esc(text(decision.action === 'exclude' ? 'importRowExcluded' : 'importRowCorrected'))}` : ''}</p></div><div class="admin-center-actions">${button('importEditRow', 'data-source-edit aria-expanded="false"')}${button('importExcludeRow', 'data-source-exclude')}${decision ? button('importUndoRow', 'data-source-undo') : ''}</div><div data-source-fields hidden><div class="admin-form-grid">${(row.editable_fields || []).map((key, i) => field(`source_${i}`, key, 'text', decision?.values?.[key] ?? row.values[key])).join('')}</div><div class="admin-center-actions">${button('importApplyDecision', 'data-source-apply')}</div></div></article>`;
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
      article.querySelector('[data-source-apply]').onclick = guard(apply);
      article.querySelector('[data-source-exclude]').onclick = () => confirm(text('importExcludeRowsConfirm').replace('{n}', '1'), async () => { exclude(row); markChanged(); await apply(); }, false, text('importSourceNote'));
      article.querySelector('[data-source-undo]')?.addEventListener('click', guard(async () => { delete draft.source[keyOf(row)]; markChanged(); await apply(); }));
    });
    root.querySelector('[data-source-exclude-all]')?.addEventListener('click', () => confirm(text('importExcludeRowsConfirm').replace('{n}', pending.length), async () => {
      pending.forEach(exclude); markChanged(); await apply();
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
