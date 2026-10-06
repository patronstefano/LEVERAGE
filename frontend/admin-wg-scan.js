const COPY = {
  startAthletes: ['Start athlete scan', 'Avvia scansione atleti', 'Iniciar escaneo de atletas', 'Lancer la recherche des athlètes'],
  startEvents: ['Start event scan', 'Avvia scansione eventi', 'Iniciar escaneo de eventos', 'Lancer la recherche des événements'],
  pause: ['Pause', 'Sospendi', 'Pausar', 'Suspendre'],
  resume: ['Resume', 'Riprendi', 'Reanudar', 'Reprendre'],
  retry: ['Retry failed searches', 'Riprova ricerche fallite', 'Reintentar búsquedas fallidas', 'Réessayer les recherches échouées'],
  pending: ['Queued', 'In coda', 'En cola', 'En attente'],
  running: ['Searching', 'In ricerca', 'Buscando', 'Recherche en cours'],
  matched: ['With candidates', 'Con candidati', 'Con candidatos', 'Avec candidats'],
  no_match: ['No candidates', 'Senza candidati', 'Sin candidatos', 'Sans candidats'],
  error: ['Failed', 'Fallite', 'Fallidas', 'Échouées'],
  skipped: ['Skipped', 'Escluse', 'Excluidas', 'Exclues'],
  dismissed: ['Dismissed', 'Scartate', 'Descartadas', 'Écartées'],
  active: ['Active', 'Attiva', 'Activo', 'Active'],
  paused: ['Paused', 'Sospesa', 'Pausado', 'Suspendue'],
  compatibility: ['Compatibility', 'Compatibilità', 'Compatibilidad', 'Compatibilité'],
  goToAthlete: ['Go to athlete', 'Vai all’atleta', 'Ir al atleta', 'Voir l’athlète'],
  goToEvent: ['Go to event', 'Vai all’evento', 'Ir al evento', 'Voir l’événement'],
  note: ['Compatibility is a matching score, not identity verification. No profile data is imported by this scan.', 'La compatibilità è un indice di corrispondenza, non una verifica d’identità. La scansione non importa dati nelle schede.', 'La compatibilidad es un índice de coincidencia, no una verificación de identidad. El escaneo no importa datos en las fichas.', 'La compatibilité est un indice de correspondance, pas une vérification d’identité. La recherche n’importe aucune donnée dans les fiches.'],
  reject: ['Reject', 'Rifiuta', 'Rechazar', 'Refuser'],
  more: ['Load more matches', 'Carica altri riscontri', 'Cargar más coincidencias', 'Charger plus de correspondances'],
};

export async function mountWorldGymnasticsScan({root, api, esc, language, active, feedback, route, entityType, noteHost = root, controlsHost = root}) {
  const index = Math.max(0, ['en', 'it', 'es', 'fr'].indexOf(language));
  const t = (key) => COPY[key][index];
  let limit = 30, signature = '', busy = false;
  const button = (key, attr = '') => `<button type="button" class="quiet-button outline-command-button" ${attr}>${esc(t(key))}</button>`;
  root.innerHTML = `<div class="admin-center-actions" data-scan-controls></div><dl class="admin-stats-metrics" data-scan-status></dl><div data-scan-matches></div>${button('more', 'data-scan-more hidden')}<p class="admin-stats-note" data-scan-note>${esc(t('note'))}</p>`;
  const controls = root.querySelector('[data-scan-controls]');
  if (controlsHost !== root) {
    controlsHost.querySelector('[data-scan-controls]')?.remove();
    controlsHost.append(controls);
  }
  if (noteHost !== root) {
    [...noteHost.children].filter((element) => element.matches('[data-scan-note]')).forEach((element) => element.remove());
    noteHost.append(root.querySelector('[data-scan-note]'));
  }
  const refresh = async () => {
    if (!active() || !root.isConnected || busy) return;
    busy = true;
    try {
      const status = await api('/world-gymnastics/scan/status', {params: {entity_type: entityType}});
      const matches = {items: [], total: 0};
      do {
        const page = await api('/world-gymnastics/scan/matches', {params: {limit: Math.min(100, limit - matches.items.length), offset: matches.items.length, ...(entityType ? {entity_type: entityType} : {})}});
        matches.total = page.total;
        matches.items.push(...page.items);
        if (!page.items.length) break;
      } while (matches.items.length < limit && matches.items.length < matches.total);
      if (!active() || !root.isConnected) return;
      controls.innerHTML =
        button(status.started_at ? status.enabled ? 'pause' : 'resume' : entityType === 'athlete' ? 'startAthletes' : 'startEvents', `data-scan-action="${status.started_at ? status.enabled ? 'pause' : 'resume' : 'start'}"`)
        + (status.counts.error ? button('retry', 'data-scan-action="retry_errors"') : '');
      root.querySelector('[data-scan-status]').innerHTML = `<div><dt>World Gymnastics</dt><dd>${esc(t(status.enabled ? 'active' : 'paused'))}</dd></div>`
        + ['pending', 'running', 'matched', 'no_match', 'error', 'skipped', 'dismissed'].map((key) => `<div><dt>${esc(t(key))}</dt><dd>${status.counts[key] || 0}</dd></div>`).join('');
      const next = JSON.stringify(matches.items);
      if (next !== signature) {
        signature = next;
        root.querySelector('[data-scan-matches]').innerHTML = matches.items.map((job) => {
          const href = `#/${job.entity_type === 'athlete' ? 'athletes' : 'events'}/${job.entity_id}?from=admin&admin_tools=1&wg_scan_job=${job.id}&return_to=${encodeURIComponent(route)}`;
          const best = job.candidates.reduce((current, candidate) => !current || candidate.match_score > current.match_score ? candidate : current, null);
          return `<article class="admin-identity-pair admin-wg-match" data-scan-job="${job.id}">
            <div class="admin-identity-pair-grid"><div class="admin-identity-entity"><a href="${esc(href)}"><strong>${esc(job.entity_name)}</strong></a><p class="admin-revision-meta">LEVERAGE · ID ${esc(job.entity_id)}</p></div><div class="admin-identity-entity">${best ? `<a href="${esc(best.profile_url || best.event_url)}" target="_blank" rel="noopener noreferrer"><strong>${esc(best.title || [best.last_name, best.first_name].filter(Boolean).join(' '))}</strong></a><p class="admin-revision-meta">World Gymnastics · ${esc(best.fig_id || best.event_id)}</p>` : ''}</div></div>
            <p class="admin-revision-meta">${esc(t('compatibility'))}: ${best ? Math.round(best.match_score * 100) : 0}%</p>
            <div class="admin-center-actions admin-wg-actions">${button('reject', `data-scan-dismiss="${job.id}"`)}<a class="quiet-button outline-command-button" href="${esc(href)}">${esc(t(job.entity_type === 'athlete' ? 'goToAthlete' : 'goToEvent'))}</a></div></article>`;
        }).join('');
      }
      root.querySelector('[data-scan-more]').hidden = matches.items.length >= matches.total;
      controls.querySelectorAll('[data-scan-action]').forEach((button) => { button.onclick = async () => {
        button.disabled = true;
        try { await api('/world-gymnastics/scan/control', {method:'POST',body:{action:button.dataset.scanAction, entity_type: entityType}}); await refresh(); }
        catch (error) { feedback(error.message,true); button.disabled=false; }
      }; });
      root.querySelectorAll('[data-scan-dismiss]').forEach((button) => {
        button.classList.add('filter-clear-button');
        button.onclick = async () => {
          button.disabled = true;
          try { await api(`/world-gymnastics/scan/matches/${button.dataset.scanDismiss}/dismiss`, {method:'POST'}); await refresh(); }
          catch (error) { feedback(error.message,true); button.disabled=false; }
        };
      });
    } catch (error) { if (active()) feedback(error.message,true); }
    finally { busy=false; }
  };
  root.querySelector('[data-scan-more]').onclick = () => { limit += 30; refresh(); };
  await refresh();
  const poll = setInterval(() => {
    if (!active() || !root.isConnected) { clearInterval(poll); return; }
    if (!document.hidden) refresh();
  }, 10000);
}
