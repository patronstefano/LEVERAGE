const COPY = {
  classification: ['Classification', 'Classifica', 'Clasificación', 'Classement'],
  athlete: ['Athlete', 'Atleta', 'Atleta', 'Athlète'],
  save: ['Save', 'Salva', 'Guardar', 'Enregistrer'],
  cancel: ['Undo changes', 'Annulla modifiche', 'Deshacer cambios', 'Annuler les modifications'],
  saved: ['Saved', 'Salvato', 'Guardado', 'Enregistré'],
  pending: ['Unsaved changes', 'Modifiche non salvate', 'Cambios sin guardar', 'Modifications non enregistrées'],
  unavailable: ['Not available', 'Non disponibile', 'No disponible', 'Indisponible'],
  conflict: ['This result was modified by another administrator. Select the event again to load the updated scores.', 'Questo risultato è stato modificato da un altro amministratore. Seleziona nuovamente l’evento per caricare i punteggi aggiornati.', 'Otro administrador modificó este resultado. Selecciona de nuevo el evento para cargar los resultados actualizados.', 'Un autre administrateur a modifié ce résultat. Sélectionnez à nouveau l’événement pour charger les scores actualisés.'],
  estimated: ['E est. · Execution components are incomplete in this classification. Empty fields remain unknown.', 'E est. · I componenti di esecuzione non sono completi in tutta la classifica. I campi vuoti restano non disponibili.', 'E est. · Los componentes de ejecución no están completos en toda la clasificación. Los campos vacíos siguen sin estar disponibles.', 'E est. · Les composantes d’exécution sont incomplètes dans ce classement. Les champs vides restent indisponibles.'],
  derived: ['AA and VT AVG cannot be edited directly. Select an apparatus classification.', 'AA e VT AVG non sono modificabili direttamente. Seleziona una classifica per attrezzo.', 'AA y VT AVG no se pueden editar directamente. Selecciona una clasificación por aparato.', 'AA et VT AVG ne sont pas modifiables directement. Sélectionnez un classement par agrès.'],
  components: ['To record E, provide Final Score, D, P and B (0 if absent).', 'Per registrare E, indica Final Score, D, P e B (0 se assenti).', 'Para registrar E, introduce Final Score, D, P y B (0 si no se aplican).', 'Pour enregistrer E, renseignez Final Score, D, P et B (0 si absents).'],
  formula: ['Final Score must equal D + E + B − P.', 'Final Score deve essere uguale a D + E + B − P.', 'Final Score debe ser igual a D + E + B − P.', 'Final Score doit être égal à D + E + B − P.'],
  aggregate: ['The linked total cannot be recalculated safely: its components are missing, ambiguous or inconsistent. Review the source data before correcting this score.', 'Il totale collegato non può essere ricalcolato in sicurezza: i componenti sono mancanti, ambigui o incoerenti. Verifica i dati della fonte prima di correggere questo punteggio.', 'No se puede recalcular el total vinculado: sus componentes faltan, son ambiguos o incoherentes. Revisa los datos de origen.', 'Le total associé ne peut pas être recalculé : ses composantes sont manquantes, ambiguës ou incohérentes. Vérifiez les données sources.'],
};

export function classificationHasRecordedExecution(rows) {
  return rows.length > 0 && rows.every((row) =>
    ['score', 'D_score', 'E_score', 'Penalty', 'Bonus'].every((key) => Number.isFinite(row[key]))
    && row.E_score >= 0 && row.E_score <= 10
    && Math.abs(Number(row.score.toFixed(3)) - Number((row.D_score + row.E_score + row.Bonus - row.Penalty).toFixed(3))) <= 0.001);
}

export function eventEditorCategories(event) {
  return event.category === 'junior and senior' ? ['junior', 'senior']
    : ['junior', 'senior'].includes(event.category) ? [event.category] : [];
}

export function mountResultEditor({ root, api, select, field, text, esc, bind, searchUi, active, language, nameOf, feedback, onSaved, initialSelection }) {
  const lang = Math.max(0, ['en', 'it', 'es', 'fr'].indexOf(language));
  const label = (key) => COPY[key]?.[lang] || text(key);
  const keys = ['score', 'D_score', 'E_score', 'Penalty', 'Bonus'];
  const apparatusOrder = {MAG: ['FX', 'PH', 'SR', 'VT', 'PB', 'HB'], WAG: ['VT', 'UB', 'BB', 'FX']};
  const oneDecimal = (key) => ['D_score', 'Penalty', 'Bonus'].includes(key);
  const inputValue = (key, value) => value == null ? '' : oneDecimal(key) ? Number(value).toFixed(1) : value;
  const titles = ['Final Score', 'D Score', 'E Score', 'P', 'B'];
  const snapshot = (row) => Object.fromEntries(keys.map((key) => [key, row[key] ?? null]));
  const drafts = new Map();
  const names = new Map();
  let revision = 0;
  root.innerHTML = `<div class="section-search-row analytics-comparison-search-row admin-editor-search-row"><div class="analytics-comparison-search-primary"><form class="search-form section-search-form analytics-comparison-search-form" id="adminEventSearchForm"><div class="search-input-shell"><input class="search-input" id="adminEventSearch" name="event_search" type="search" autocomplete="off" placeholder="${esc(searchUi.t('eventSearchPlaceholder'))}" aria-label="${esc(searchUi.t('eventSearchPlaceholder'))}" aria-controls="adminEventOptions" aria-expanded="false"><button type="button" class="search-clear-button" aria-label="${esc(searchUi.t('clearSearch'))}" hidden><span aria-hidden="true">&times;</span></button></div><div id="adminEventOptions" class="search-suggestions analytics-comparison-suggestions" role="listbox" hidden></div></form></div></div><div id="adminClassificationEditor"></div>`;
  const area = root.querySelector('#adminClassificationEditor');
  const showError = (error) => { if (active()) feedback(error.message, true); };
  const loadEvent = async (event, fromLink = false) => {
    const token = ++revision;
    try {
      const categories = eventEditorCategories(event);
      const groups = (await api(`/events/${event.id}/result-groups`)).filter((g) => categories.includes(g.category)
        && ['FX', 'PH', 'SR', 'VT', 'PB', 'HB', 'UB', 'BB'].includes(g.apparatus));
      if (!active() || token !== revision) return;
      area.innerHTML = `<h3>${esc(event.name)} · ${esc(event.year)}</h3>`;
      if (!groups.length) { area.innerHTML += `<div class="empty-state">${esc(label('derived'))}</div>`; return; }
      const dimensions = ['discipline', 'format', 'round', 'apparatus', 'day'];
      let selected = {...groups[0]};
      if (fromLink) {
        const requestedApparatus = initialSelection.get('apparatus');
        const candidates = groups.filter((group) => dimensions.every((key) => {
          if (!initialSelection.has(key)) return true;
          let requested = initialSelection.get(key);
          if (key === 'apparatus' && requested === 'AA') return true;
          if (key === 'apparatus' && requested === 'VT AVG') requested = 'VT';
          return String(group[key] ?? '') === requested;
        }));
        if (!candidates.length) { area.innerHTML += `<div class="empty-state">${esc(text('empty'))}</div>`; return; }
        candidates.sort((a, b) => (apparatusOrder[a.discipline] || []).indexOf(a.apparatus) - (apparatusOrder[b.discipline] || []).indexOf(b.apparatus));
        selected = {...candidates[0]};
        if (['AA', 'VT AVG'].includes(requestedApparatus)) area.innerHTML += `<p>${esc(label('derived'))}</p>`;
      }
      area.innerHTML += '<div id="adminClassificationSelectors" class="admin-form-grid"></div>'
        + '<div id="adminScoreRows"></div>';
      const renderSelectors = () => {
        let available = groups;
        const html = dimensions.map((key) => {
          const options = [...new Set(available.map((g) => String(g[key] ?? '')))];
          if (key === 'apparatus') {
            const order = apparatusOrder[selected.discipline] || [];
            options.sort((a, b) => order.indexOf(a) - order.indexOf(b));
          }
          if (!options.includes(String(selected[key] ?? ''))) selected[key] = available[0][key];
          const value = String(selected[key] ?? '');
          available = available.filter((g) => String(g[key] ?? '') === value);
          if (key === 'day' && options.length < 2) return '';
          return select(`classification_${key}`, text(key), options.map((v) => ({value: v, label: v ? text(v) : '—'})), value);
        }).join('');
        selected = {...available[0]};
        area.querySelector('#adminClassificationSelectors').innerHTML = html;
        bind();
        dimensions.forEach((key) => area.querySelector(`[name=classification_${key}]`)?.addEventListener('change', (event) => {
          selected[key] = event.target.value;
          renderSelectors();
          loadGroup();
        }));
      };
      const loadGroup = async () => {
        const groupToken = ++revision;
        const group = {...selected};
        const out = area.querySelector('#adminScoreRows');
        out.replaceChildren();
        try {
          const params = {event_id: event.id, limit: 500};
          for (const key of dimensions) if (group[key] != null) params[key] = group[key];
          if (categories.length === 1) params.category = categories[0];
          let rows = [], batch;
          do {
            batch = await api('/results/', {params: {...params, offset: rows.length}});
            if (!active() || groupToken !== revision) return;
            rows.push(...batch);
          } while (batch.length === 500);
          rows = rows.filter((r) => categories.includes(r.category)
            && dimensions.every((key) => (r[key] ?? null) === (group[key] ?? null)));
          for (const id of new Set(rows.map((r) => r.athlete_id))) {
            if (!names.has(id)) names.set(id, nameOf(await api(`/athletes/${id}`)));
            if (!active() || groupToken !== revision) return;
          }
          rows.sort((a,b) => (b.score ?? -Infinity) - (a.score ?? -Infinity) || a.id-b.id);
          if (!rows.length) { out.innerHTML = `<div class="empty-state">${esc(text('empty'))}</div>`; return; }
          out.innerHTML = `<p data-execution-notice role="status"></p><div class="admin-score-table-scroll"><table class="admin-score-table"><thead><tr><th>${esc(label('athlete'))}</th>${titles.map((t) => `<th>${t}</th>`).join('')}<th></th></tr></thead><tbody>${rows.map((r) => {
            const values = drafts.get(r.id) || snapshot(r);
            return `<tr data-result-id="${r.id}"><th scope="row">${esc(names.get(r.athlete_id))}<small>${esc(r.represented_country || '')} · ID ${r.id}${r.vt_attempt ? ` · VT ${r.vt_attempt}` : ''}</small></th>${keys.map((key,i) => `<td><input type="number" step="${oneDecimal(key) ? '0.1' : '0.001'}" min="0" name="${key}" aria-label="${titles[i]} · ${esc(names.get(r.athlete_id))}" value="${inputValue(key, values[key])}" placeholder="—" title="${esc(label('unavailable'))}"></td>`).join('')}<td><div class="admin-center-actions"><button type="button" data-save class="quiet-button outline-command-button">${esc(label('save'))}</button><button type="button" data-reset class="quiet-button outline-command-button">${esc(label('cancel'))}</button></div><small role="status"></small></td></tr>`;
          }).join('')}</tbody></table></div>`;
          const refreshExecutionNotice = () => {
            const incomplete = !classificationHasRecordedExecution(rows);
            const notice = out.querySelector('[data-execution-notice]');
            notice.hidden = !incomplete;
            notice.textContent = incomplete ? label('estimated') : '';
          };
          refreshExecutionNotice();
          rows.forEach((row) => {
            const tr = out.querySelector(`[data-result-id="${row.id}"]`);
            const notice = tr.querySelector('[role=status]');
            const save = tr.querySelector('[data-save]');
            const reset = tr.querySelector('[data-reset]');
            const inputs = [...tr.querySelectorAll('input')];
            const executionInput = tr.querySelector('[name=E_score]');
            const values = () => Object.fromEntries(inputs.map((el) => [el.name,
              oneDecimal(el.name) && row[el.name] != null && el.value === inputValue(el.name, row[el.name])
                ? row[el.name] : el.value === '' ? null : el.valueAsNumber]));
            const update = () => {
              const current = values();
              const dirty = keys.some((key) => current[key] !== (row[key] ?? null));
              const e = current.score != null && current.D_score != null ? current.score - current.D_score : null;
              executionInput.placeholder = current.E_score == null && e != null && e >= 0 && e <= 10
                ? `E est. ${e.toLocaleString(language, {minimumFractionDigits: 3, maximumFractionDigits: 3})}` : '—';
              save.disabled = reset.disabled = !dirty;
              notice.textContent = dirty ? label('pending') : '';
              if (dirty) drafts.set(row.id, values()); else drafts.delete(row.id);
            };
            inputs.forEach((input) => input.addEventListener('input', update));
            inputs.filter((input) => oneDecimal(input.name)).forEach((input) => input.addEventListener('change', () => {
              if (input.value !== '' && input.validity.valid) input.value = inputValue(input.name, input.valueAsNumber);
              update();
            }));
            reset.onclick = () => { inputs.forEach((el) => { el.value = inputValue(el.name, row[el.name]); }); update(); };
            save.onclick = async () => {
              if (inputs.some((input) => !input.reportValidity())) return;
              const body = {expected: snapshot(row), values: values()};
              if (body.values.E_score != null) {
                if (keys.some((key) => body.values[key] == null)) { notice.textContent = label('components'); return; }
                if (!classificationHasRecordedExecution([body.values])) { notice.textContent = label('formula'); return; }
              }
              save.disabled = reset.disabled = true;
              inputs.forEach((el) => { el.disabled = true; });
              try {
                const saved = await api(`/results/${row.id}/scores`, {method: 'PATCH', body});
                Object.assign(row, saved); drafts.delete(row.id);
                onSaved?.();
                if (!active() || groupToken !== revision) return;
                update();
                refreshExecutionNotice();
                notice.textContent = label('saved');
                rows.sort((a,b) => (b.score ?? -Infinity) - (a.score ?? -Infinity) || a.id-b.id)
                  .forEach((item) => out.querySelector('tbody').append(out.querySelector(`[data-result-id="${item.id}"]`)));
              } catch (error) {
                notice.textContent = error.message.includes('Result changed') ? label('conflict')
                  : error.message.includes('Incomplete execution components') ? label('components')
                  : error.message.includes('Final score must equal') ? label('formula')
                  : error.message.includes('Unsafe aggregate correction') ? label('aggregate') : error.message;
                save.disabled = reset.disabled = false;
              } finally { inputs.forEach((el) => { el.disabled = false; }); }
            };
            update();
          });
        } catch (error) { if (groupToken === revision) showError(error); }
      };
      renderSelectors();
      await loadGroup();
    } catch (error) { if (token === revision) showError(error); }
  };
  const input = root.querySelector('[name=event_search]');
  const suggestions = root.querySelector('#adminEventOptions');
  const clear = root.querySelector('.search-clear-button');
  const searchForm = root.querySelector('#adminEventSearchForm');
  let searchRevision = 0, timer;
  const closeSuggestions = () => {
    ++searchRevision;
    clearTimeout(timer);
    suggestions.hidden = true;
    input.setAttribute('aria-expanded', 'false');
    searchUi.setSearchSuggestionsOpen(suggestions, false);
    searchUi.setSearchSuggestionsBusy(suggestions, false);
  };
  const chooseEvent = (event) => {
    closeSuggestions();
    input.value = `${event.name} · ${event.year}`;
    clear.hidden = false;
    loadEvent(event);
  };
  const search = async (token) => {
    const query = input.value.trim();
    if (!query) { closeSuggestions(); return; }
    searchUi.setSearchSuggestionsBusy(suggestions, true);
    try {
      const events = /^\d+$/.test(query) && !/^\d{4}$/.test(query)
        ? [await api(`/events/${Number(query)}`)]
        : await api('/events/', {params: {search: query, query, limit: 12}});
      if (!active() || !input.isConnected || token !== searchRevision) return;
      suggestions.innerHTML = events.length ? events.map((event, index) => `<button type="button" class="analytics-comparison-suggestion search-suggestion" role="option" data-event-choice="${index}"><strong>${esc(event.name)}</strong><span>${esc([event.year, event.discipline, event.location, `ID ${event.id}`].filter(Boolean).join(' · '))}</span></button>`).join('') : `<div class="search-suggestion search-suggestion-status">${esc(text('empty'))}</div>`;
      suggestions.querySelectorAll('[data-event-choice]').forEach((button) => { button.onclick = () => chooseEvent(events[Number(button.dataset.eventChoice)]); });
      suggestions.hidden = false;
      input.setAttribute('aria-expanded', 'true');
      searchUi.setSearchSuggestionsOpen(suggestions, true, Math.max(1, events.length));
    } catch (error) {
      if (token === searchRevision && active()) showError(error);
    } finally {
      if (token === searchRevision) searchUi.setSearchSuggestionsBusy(suggestions, false);
    }
  };
  const scheduleSearch = () => {
    clearTimeout(timer);
    const token = ++searchRevision;
    clear.hidden = !input.value;
    if (!input.value.trim()) { closeSuggestions(); return; }
    timer = setTimeout(() => search(token), 140);
  };
  input.addEventListener('input', scheduleSearch);
  input.addEventListener('focus', scheduleSearch);
  input.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') { closeSuggestions(); input.blur(); }
    if (event.key === 'ArrowDown') { event.preventDefault(); suggestions.querySelector('button')?.focus(); }
  });
  searchForm.addEventListener('submit', (event) => { event.preventDefault(); if (!suggestions.hidden) suggestions.querySelector('button')?.click(); });
  searchForm.addEventListener('focusout', () => setTimeout(() => {
    if (!searchForm.contains(document.activeElement)) closeSuggestions();
  }, 0));
  root.addEventListener('pointerdown', (event) => { if (!searchForm.contains(event.target)) closeSuggestions(); }, true);
  clear.onclick = () => { input.value = ''; clear.hidden = true; closeSuggestions(); input.focus(); };
  const eventId = initialSelection?.get('event_id');
  if (eventId && /^\d+$/.test(eventId)) {
    api(`/events/${eventId}`).then((event) => {
      if (!active()) return;
      root.querySelector('[name=event_search]').value = `${event.name} · ${event.year}`;
      clear.hidden = false;
      return loadEvent(event, true);
    }).catch(showError);
  }
}
