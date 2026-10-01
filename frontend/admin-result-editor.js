const COPY = {
  classification: ['Classification', 'Classifica', 'Clasificación', 'Classement'],
  athlete: ['Athlete', 'Atleta', 'Atleta', 'Athlète'],
  save: ['Save', 'Salva', 'Guardar', 'Enregistrer'],
  cancel: ['Undo changes', 'Annulla modifiche', 'Deshacer cambios', 'Annuler les modifications'],
  saved: ['Saved', 'Salvato', 'Guardado', 'Enregistré'],
  pending: ['Unsaved changes', 'Modifiche non salvate', 'Cambios sin guardar', 'Modifications non enregistrées'],
  unavailable: ['Not available', 'Non disponibile', 'No disponible', 'Indisponible'],
  reload: ['Reload classification', 'Ricarica classifica', 'Recargar clasificación', 'Recharger le classement'],
  conflict: ['This result was modified by another administrator. Reload the classification.', 'Questo risultato è stato modificato da un altro amministratore. Ricarica la classifica.', 'Otro administrador modificó este resultado. Recarga la clasificación.', 'Un autre administrateur a modifié ce résultat. Rechargez le classement.'],
};

export function mountResultEditor({ root, api, select, field, text, esc, bind, wireLookup, active, language, nameOf, feedback, onSaved }) {
  const lang = Math.max(0, ['en', 'it', 'es', 'fr'].indexOf(language));
  const label = (key) => COPY[key]?.[lang] || text(key);
  const keys = ['score', 'D_score', 'E_score', 'Penalty', 'Bonus'];
  const titles = ['Final Score', 'D Score', 'E Score', 'P', 'B'];
  const snapshot = (row) => Object.fromEntries(keys.map((key) => [key, row[key] ?? null]));
  const drafts = new Map();
  const names = new Map();
  let revision = 0;
  root.innerHTML = `<div class="admin-lookup">${field('event_search', 'search')}<div id="adminEventOptions"></div></div><div id="adminClassificationEditor"></div>`;
  const area = root.querySelector('#adminClassificationEditor');
  const showError = (error) => { if (active()) feedback(error.message, true); };
  const loadEvent = async (event) => {
    const token = ++revision;
    try {
      const groups = await api(`/events/${event.id}/result-groups`);
      if (!active() || token !== revision) return;
      area.innerHTML = `<h3>${esc(event.name)} · ${esc(event.year)}</h3>`;
      if (!groups.length) { area.innerHTML += `<div class="empty-state">${esc(text('empty'))}</div>`; return; }
      area.innerHTML += select('classification', label('classification'), groups.map((g, i) => ({value: String(i), label: [g.discipline, g.category, g.format, g.round, g.apparatus, g.day == null ? '' : `${text('day')} ${g.day}`].filter(Boolean).map(text).join(' · ')})), '0')
        + `<div class="admin-center-actions"><button type="button" id="adminReloadClassification" class="quiet-button outline-command-button">${esc(label('reload'))}</button></div><div id="adminScoreRows"></div>`;
      bind();
      const loadGroup = async () => {
        const groupToken = ++revision;
        const group = groups[Number(area.querySelector('[name=classification]').value)];
        const out = area.querySelector('#adminScoreRows');
        out.replaceChildren();
        try {
          const params = {event_id: event.id, limit: 500};
          for (const key of ['discipline', 'category', 'format', 'round', 'apparatus', 'day']) if (group[key] != null) params[key] = group[key];
          let rows = [], batch;
          do {
            batch = await api('/results/', {params: {...params, offset: rows.length}});
            if (!active() || groupToken !== revision) return;
            rows.push(...batch);
          } while (batch.length === 500);
          rows = rows.filter((r) => ['discipline', 'category', 'format', 'round', 'apparatus', 'day'].every((key) => (r[key] ?? null) === (group[key] ?? null)));
          for (const id of new Set(rows.map((r) => r.athlete_id))) {
            if (!names.has(id)) names.set(id, nameOf(await api(`/athletes/${id}`)));
            if (!active() || groupToken !== revision) return;
          }
          rows.sort((a,b) => (b.score ?? -Infinity) - (a.score ?? -Infinity) || a.id-b.id);
          if (!rows.length) { out.innerHTML = `<div class="empty-state">${esc(text('empty'))}</div>`; return; }
          out.innerHTML = `<div class="admin-score-table-scroll"><table class="admin-score-table"><thead><tr><th>${esc(label('athlete'))}</th>${titles.map((t) => `<th>${t}</th>`).join('')}<th></th></tr></thead><tbody>${rows.map((r) => {
            const values = drafts.get(r.id) || snapshot(r);
            return `<tr data-result-id="${r.id}"><th scope="row">${esc(names.get(r.athlete_id))}<small>${esc(r.represented_country || '')} · ID ${r.id}${r.vt_attempt ? ` · VT ${r.vt_attempt}` : ''}</small></th>${keys.map((key,i) => `<td><input type="number" step="${key === 'D_score' ? '0.1' : '0.001'}" min="0" name="${key}" aria-label="${titles[i]} · ${esc(names.get(r.athlete_id))}" value="${values[key] == null ? '' : key === 'D_score' ? Number(values[key]).toFixed(1) : values[key]}" placeholder="—" title="${esc(label('unavailable'))}"></td>`).join('')}<td><div class="admin-center-actions"><button type="button" data-save class="quiet-button outline-command-button">${esc(label('save'))}</button><button type="button" data-reset class="quiet-button outline-command-button">${esc(label('cancel'))}</button></div><small role="status"></small></td></tr>`;
          }).join('')}</tbody></table></div>`;
          rows.forEach((row) => {
            const tr = out.querySelector(`[data-result-id="${row.id}"]`);
            const notice = tr.querySelector('[role=status]');
            const save = tr.querySelector('[data-save]');
            const reset = tr.querySelector('[data-reset]');
            const inputs = [...tr.querySelectorAll('input')];
            const values = () => Object.fromEntries(inputs.map((el) => [el.name,
              el.name === 'D_score' && row.D_score != null && el.value === Number(row.D_score).toFixed(1)
                ? row.D_score : el.value === '' ? null : el.valueAsNumber]));
            const update = () => {
              const dirty = keys.some((key) => values()[key] !== (row[key] ?? null));
              save.disabled = reset.disabled = !dirty;
              notice.textContent = dirty ? label('pending') : '';
              if (dirty) drafts.set(row.id, values()); else drafts.delete(row.id);
            };
            inputs.forEach((input) => input.addEventListener('input', update));
            reset.onclick = () => { inputs.forEach((el) => { el.value = row[el.name] == null ? '' : el.name === 'D_score' ? Number(row[el.name]).toFixed(1) : row[el.name]; }); update(); };
            save.onclick = async () => {
              if (inputs.some((input) => !input.reportValidity())) return;
              const body = {expected: snapshot(row), values: values()};
              save.disabled = reset.disabled = true;
              inputs.forEach((el) => { el.disabled = true; });
              try {
                const saved = await api(`/results/${row.id}/scores`, {method: 'PATCH', body});
                Object.assign(row, saved); drafts.delete(row.id); update();
                onSaved?.();
                notice.textContent = label('saved');
                rows.sort((a,b) => (b.score ?? -Infinity) - (a.score ?? -Infinity) || a.id-b.id)
                  .forEach((item) => out.querySelector('tbody').append(out.querySelector(`[data-result-id="${item.id}"]`)));
              } catch (error) {
                notice.textContent = error.message.includes('Result changed') ? label('conflict') : error.message;
                save.disabled = reset.disabled = false;
              } finally { inputs.forEach((el) => { el.disabled = false; }); }
            };
            update();
          });
        } catch (error) { if (groupToken === revision) showError(error); }
      };
      area.querySelector('[name=classification]').addEventListener('change', loadGroup);
      area.querySelector('#adminReloadClassification').onclick = loadGroup;
      await loadGroup();
    } catch (error) { if (token === revision) showError(error); }
  };
  wireLookup(root.querySelector('[name=event_search]'), root.querySelector('#adminEventOptions'), '/events/', {}, loadEvent);
}
