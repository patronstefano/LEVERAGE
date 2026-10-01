const COPY = {
  start: ['Start full scan', 'Avvia scansione completa', 'Iniciar escaneo completo', 'Lancer la recherche complète'],
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
  note: ['Compatibility is a matching score, not identity verification. No profile data is imported by this scan.', 'La compatibilità è un indice di corrispondenza, non una verifica d’identità. La scansione non importa dati nelle schede.', 'La compatibilidad es un índice de coincidencia, no una verificación de identidad. El escaneo no importa datos en las fichas.', 'La compatibilité est un indice de correspondance, pas une vérification d’identité. La recherche n’importe aucune donnée dans les fiches.'],
  open: ['Review profile', 'Esamina scheda', 'Revisar ficha', 'Examiner la fiche'],
  reject: ['Reject', 'Rifiuta', 'Rechazar', 'Refuser'],
  more: ['Load more matches', 'Carica altri riscontri', 'Cargar más coincidencias', 'Charger plus de correspondances'],
  refresh: ['Refresh', 'Aggiorna', 'Actualizar', 'Actualiser'],
};

export async function mountWorldGymnasticsScan({root, api, esc, language, active, feedback, route}) {
  const index = Math.max(0, ['en', 'it', 'es', 'fr'].indexOf(language));
  const t = (key) => COPY[key][index];
  let limit = 30, signature = '', busy = false;
  const button = (key, attr = '') => `<button type="button" class="quiet-button outline-command-button" ${attr}>${esc(t(key))}</button>`;
  root.innerHTML = `<div class="admin-center-actions" data-scan-controls></div><dl class="admin-stats-metrics" data-scan-status></dl><p class="admin-stats-note">${esc(t('note'))}</p><div data-scan-matches></div>${button('more', 'data-scan-more hidden')}`;
  const refresh = async () => {
    if (!active() || !root.isConnected || busy) return;
    busy = true;
    try {
      const status = await api('/world-gymnastics/scan/status');
      const matches = {items: [], total: 0};
      do {
        const page = await api('/world-gymnastics/scan/matches', {params: {limit: Math.min(100, limit - matches.items.length), offset: matches.items.length}});
        matches.total = page.total;
        matches.items.push(...page.items);
        if (!page.items.length) break;
      } while (matches.items.length < limit && matches.items.length < matches.total);
      if (!active() || !root.isConnected) return;
      root.querySelector('[data-scan-controls]').innerHTML =
        button(status.started_at ? status.enabled ? 'pause' : 'resume' : 'start', `data-scan-action="${status.started_at ? status.enabled ? 'pause' : 'resume' : 'start'}"`)
        + (status.counts.error ? button('retry', 'data-scan-action="retry_errors"') : '')
        + button('refresh', 'data-scan-refresh');
      root.querySelector('[data-scan-status]').innerHTML = `<div><dt>World Gymnastics</dt><dd>${esc(t(status.enabled ? 'active' : 'paused'))}</dd></div>`
        + ['pending', 'running', 'matched', 'no_match', 'error', 'skipped', 'dismissed'].map((key) => `<div><dt>${esc(t(key))}</dt><dd>${status.counts[key] || 0}</dd></div>`).join('');
      const next = JSON.stringify(matches.items);
      if (next !== signature) {
        signature = next;
        const opened = new Set([...root.querySelectorAll('[data-scan-job][open]')].map((el) => el.dataset.scanJob));
        root.querySelector('[data-scan-matches]').innerHTML = matches.items.map((job) => {
          const href = `#/${job.entity_type === 'athlete' ? 'athletes' : 'events'}/${job.entity_id}?from=admin&admin_tools=1&wg_scan_job=${job.id}&return_to=${encodeURIComponent(route)}`;
          return `<details class="admin-revision-group" data-scan-job="${job.id}" ${opened.has(String(job.id)) ? 'open' : ''}><summary>${esc(job.entity_name)} <span class="admin-revision-count">${Math.round(Math.max(...job.candidates.map((c) => c.match_score)) * 100)}%</span></summary>
            <div class="admin-center-actions"><a class="quiet-button outline-command-button" href="${esc(href)}">${esc(t('open'))}</a></div>
            ${job.candidates.map((c) => `<article class="account-notification"><div class="account-notification-copy"><p><strong>${esc(c.title || [c.last_name,c.first_name].filter(Boolean).join(' '))}</strong></p><p>${esc([c.country,c.discipline,(c.disciplines || []).join(' / ')].filter(Boolean).join(' · '))}</p><a href="${esc(c.profile_url || c.event_url)}" target="_blank" rel="noopener noreferrer">World Gymnastics · ${esc(c.fig_id || c.event_id)}</a></div><div class="account-notification-actions"><span>${esc(t('compatibility'))} ${Math.round(c.match_score * 100)}%</span>${button('reject', `data-scan-reject="${job.id}" data-candidate="${esc(c.fig_id || c.event_id)}"`)}</div></article>`).join('')}</details>`;
        }).join('');
      }
      root.querySelector('[data-scan-more]').hidden = matches.items.length >= matches.total;
      root.querySelector('[data-scan-refresh]').onclick = refresh;
      root.querySelectorAll('[data-scan-action]').forEach((button) => { button.onclick = async () => {
        button.disabled = true;
        try { await api('/world-gymnastics/scan/control', {method:'POST',body:{action:button.dataset.scanAction}}); await refresh(); }
        catch (error) { feedback(error.message,true); button.disabled=false; }
      }; });
      root.querySelectorAll('[data-scan-reject]').forEach((button) => {
        button.classList.add('filter-clear-button');
        button.onclick = async () => {
          button.disabled = true;
          try { await api(`/world-gymnastics/scan/matches/${button.dataset.scanReject}/reject`, {method:'POST',body:{candidate_id:button.dataset.candidate}}); await refresh(); }
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
