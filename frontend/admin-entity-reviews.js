const COPY = {
  athlete: ['Possible duplicate athletes', 'Possibili atleti duplicati', 'Posibles atletas duplicados', 'Athlètes potentiellement en double'],
  event: ['Possible duplicate events', 'Possibili eventi duplicati', 'Posibles eventos duplicados', 'Événements potentiellement en double'],
  note: ['Name similarity is an indicator, not identity verification. No automatic merges.', 'La somiglianza dei nomi è un indicatore, non una verifica d’identità. Nessuna unione automatica.', 'La similitud de nombres es un indicador, no una verificación de identidad. Sin uniones automáticas.', 'La similitude des noms est un indice, pas une vérification d’identité. Aucune fusion automatique.'],
  empty: ['No items.', 'Nessun elemento.', 'Ningún elemento.', 'Aucun élément.'],
  compare: ['Compare details', 'Confronta dettagli', 'Comparar detalles', 'Comparer les détails'],
  separate: ['Keep separate', 'Mantieni separati', 'Mantener separados', 'Conserver séparés'],
  merge: ['Review merge', 'Valuta unione', 'Revisar unión', 'Examiner la fusion'],
  more: ['Load more pairs', 'Carica altre coppie', 'Cargar más pares', 'Charger plus de paires'],
  compatibility: ['Name compatibility', 'Compatibilità dei nomi', 'Compatibilidad de nombres', 'Compatibilité des noms'],
  same_name: ['Matching normalized names', 'Nomi normalizzati coincidenti', 'Nombres normalizados coincidentes', 'Noms normalisés identiques'],
  similar_name: ['Similar names', 'Nomi simili', 'Nombres similares', 'Noms similaires'],
  same_year: ['Same year', 'Stesso anno', 'Mismo año', 'Même année'],
  prior_merge: ['Previously recommended merge', 'Unione già indicata nella review storica', 'Unión indicada en revisión previa', 'Fusion indiquée lors d’une révision précédente'],
  shared_wg: ['Same World Gymnastics ID', 'Stesso ID World Gymnastics', 'Mismo ID World Gymnastics', 'Même identifiant World Gymnastics'],
  different_wg: ['Different World Gymnastics IDs', 'ID World Gymnastics diversi', 'ID World Gymnastics diferentes', 'Identifiants World Gymnastics différents'],
  different_country: ['Different current countries', 'Nazionalità attuali diverse', 'Nacionalidades actuales diferentes', 'Nationalités actuelles différentes'],
  different_birth_year: ['Different birth years', 'Anni di nascita diversi', 'Años de nacimiento diferentes', 'Années de naissance différentes'],
  different_dates: ['Different event dates', 'Date evento diverse', 'Fechas diferentes', 'Dates différentes'],
  conflict: ['Different scores in the same competition context: keep separate unless official evidence resolves the conflict.', 'Punteggi diversi nello stesso contesto di gara: mantenere separati salvo riscontro ufficiale che risolva il conflitto.', 'Puntuaciones distintas en el mismo contexto: mantener separados salvo evidencia oficial.', 'Scores différents dans le même contexte : conserver séparés sauf preuve officielle.'],
  results: ['Results', 'Risultati', 'Resultados', 'Résultats'],
  history: ['Country history', 'Storico nazionalità', 'Historial de nacionalidad', 'Historique des nationalités'],
  events: ['Competitions and rounds', 'Gare e round', 'Competiciones y rondas', 'Compétitions et tours'],
  birth: ['Birth year', 'Anno di nascita', 'Año de nacimiento', 'Année de naissance'],
};

export async function mountEntityReviews({root, kind, api, esc, language, active, route}) {
  const index = Math.max(0, ['en', 'it', 'es', 'fr'].indexOf(language));
  const t = (key) => COPY[key]?.[index] || key;
  const alive = () => active() && root.isConnected;
  let offset = 0, total = 0;
  const button = (label, attrs) => `<button type="button" class="quiet-button outline-command-button" ${attrs}>${esc(t(label))}</button>`;
  root.innerHTML = `<div class="section-header compact-section-header"><h2>${esc(t(kind))}</h2></div><p class="admin-stats-note">${esc(t('note'))}</p><div data-pair-feedback role="status"></div><div data-pairs></div>${button('more', 'data-pairs-more hidden')}`;
  const list = root.querySelector('[data-pairs]');
  const more = root.querySelector('[data-pairs-more]');
  const failure = (error) => {
    if (alive()) root.querySelector('[data-pair-feedback]').innerHTML = `<p class="admin-center-feedback is-error">${esc(error.message)}</p>`;
  };
  const card = (entity) => `<div class="admin-identity-entity"><a href="#/${kind === 'athlete' ? 'athletes' : 'events'}/${entity.id}?from=admin&return_to=${encodeURIComponent(route)}"><strong>${esc(entity.name)}</strong></a><p class="admin-revision-meta">${esc([`ID ${entity.id}`, entity.discipline, entity.country, entity.year].filter(Boolean).join(' · '))}</p>${entity.birth_year ? `<p>${esc(t('birth'))}: ${entity.birth_year}</p>` : ''}${kind === 'event' ? `<p class="admin-revision-meta">${esc([entity.start_date, entity.end_date !== entity.start_date ? entity.end_date : null, entity.location].filter(Boolean).join(' · '))}</p>` : ''}${entity.world_gymnastics_athlete_id || entity.world_gymnastics_event_id ? `<p class="admin-revision-meta">FIG ID: ${esc(entity.world_gymnastics_athlete_id || entity.world_gymnastics_event_id)}</p>` : ''}</div>`;
  const evidence = (entity) => `<div>${card(entity)}<p>${esc(t('results'))}: ${entity.result_count}</p>${entity.country_history.length ? `<p>${esc(t('history'))}: ${esc(entity.country_history.map(h => `${h.from_country || ''} → ${h.to_country} (${h.year})`).join(' · '))}</p>` : ''}<h3>${esc(t('events'))}</h3><ul class="admin-pair-events">${entity.events.map(e => `<li><a href="#/events/${e.id}?from=admin&return_to=${encodeURIComponent(route)}">${esc(e.name)} · ${e.year}</a><span>${esc([e.start_date, e.end_date !== e.start_date ? e.end_date : null, e.country, e.format, e.round].filter(Boolean).join(' · '))}</span></li>`).join('')}</ul></div>`;
  const load = async () => {
    more.disabled = true;
    try {
      const data = await api('/admin/entity-duplicates', {params: {entity_type: kind, offset, limit: 20}});
      if (!alive()) return;
      total = data.total;
      offset += data.items.length;
      if (data.items.length) list.querySelector('.empty-state')?.remove();
      for (const pair of data.items) {
        const node = document.createElement('article');
        node.className = 'admin-identity-pair';
        node.innerHTML = `<div class="admin-identity-pair-grid">${card(pair.left)}${card(pair.right)}</div><p class="admin-revision-meta">${esc(t('compatibility'))}: ${pair.compatibility}% · ${esc(pair.reasons.map(t).join(' · '))}</p><div class="admin-center-actions">${button('compare', 'data-pair-compare')}${button('separate', 'data-pair-separate')}<a class="quiet-button outline-command-button" href="#/admin/merge?entity_type=${kind}&source=${pair.right.id}&target=${pair.left.id}">${esc(t('merge'))}</a></div><div data-pair-details hidden></div>`;
        list.append(node);
        const path = `/admin/entity-duplicates/${kind}/${pair.left.id}/${pair.right.id}`;
        const details = node.querySelector('[data-pair-details]');
        const compare = node.querySelector('[data-pair-compare]');
        compare.onclick = async () => {
          if (details.innerHTML) { details.hidden = !details.hidden; compare.setAttribute('aria-expanded', String(!details.hidden)); return; }
          compare.disabled = true;
          try {
            const data = await api(path);
            if (!alive()) return;
            details.innerHTML = `${data.conflicting_scores ? `<p class="admin-pair-warning">${esc(t('conflict'))}</p>` : ''}<div class="admin-identity-pair-grid">${evidence(data.left)}${evidence(data.right)}</div>`;
            details.hidden = false;
            compare.setAttribute('aria-expanded', 'true');
          } catch (error) { failure(error); }
          finally { compare.disabled = false; }
        };
        node.querySelector('[data-pair-separate]').onclick = async (event) => {
          const button = event.currentTarget;
          button.disabled = true;
          try {
            await api(`${path}/keep-separate`, {method: 'POST', body: {fingerprint: pair.fingerprint}});
            if (!alive()) return;
            node.remove(); offset = Math.max(0, offset - 1); total--;
            if (!list.children.length) list.innerHTML = `<div class="empty-state">${esc(t('empty'))}</div>`;
            more.hidden = offset >= total;
          } catch (error) { failure(error); button.disabled = false; }
        };
      }
      if (!list.children.length) list.innerHTML = `<div class="empty-state">${esc(t('empty'))}</div>`;
      more.hidden = offset >= total;
    } catch (error) { failure(error); }
    finally { more.disabled = false; }
  };
  more.onclick = load;
  await load();
}
