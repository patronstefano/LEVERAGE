export function mountImportProgressDialog({dialog, text, esc}) {
  const owned = !dialog;
  if (owned) {
    dialog = document.createElement('dialog');
    dialog.className = 'admin-confirm';
    dialog.innerHTML = `<h2>${esc(text('importRecalculate'))}</h2>`;
    document.body.append(dialog);
    dialog.showModal();
  }
  const root = document.createElement('div');
  root.dataset.importDialogProgress = '';
  const actions = dialog.querySelector('.admin-center-actions');
  if (actions) actions.after(root);
  else dialog.append(root);
  const controls = [...dialog.querySelectorAll('button')].map(button => [button, button.disabled]);
  controls.forEach(([button]) => { button.disabled = true; });
  dialog.querySelector('[role=alert]')?.remove();
  dialog.setAttribute('aria-busy', 'true');
  const preventCancel = event => event.preventDefault();
  const close = () => { if (owned) { dialog.close(); dialog.remove(); } };
  dialog.addEventListener('cancel', preventCancel);
  window.addEventListener('hashchange', close);
  const progress = mountImportProgress({root, text, esc});
  return {
    complete: () => progress.complete(),
    dispose() {
      progress.dispose();
      root.remove();
      controls.forEach(([button, disabled]) => { button.disabled = disabled; });
      dialog.removeAttribute('aria-busy');
      dialog.removeEventListener('cancel', preventCancel);
      window.removeEventListener('hashchange', close);
      close();
    },
  };
}

export function mountImportProgress({root, text, esc, uploading = false}) {
  let disposed = false;
  let analyzing = !uploading;
  root.hidden = false;
  root.innerHTML = `<div class="admin-import-progress" role="status" aria-live="polite"><div class="admin-import-progress-heading"><span data-import-progress-label>${esc(text(uploading ? 'importUploading' : 'importLoading'))}</span><strong data-import-progress-value>${uploading ? '0%' : ''}</strong></div><div class="admin-import-progress-track ${uploading ? '' : 'is-analyzing'}" role="progressbar" aria-label="${esc(text(uploading ? 'importUploading' : 'importLoading'))}" aria-valuemin="0" aria-valuemax="100" ${uploading ? 'aria-valuenow="0"' : ''}><span></span></div></div>`;
  const label = root.querySelector('[data-import-progress-label]');
  const value = root.querySelector('[data-import-progress-value]');
  const track = root.querySelector('[role=progressbar]');
  const fill = track.firstElementChild;
  const live = () => !disposed && root.isConnected;
  return {
    onUploadProgress(percent) {
      if (!live() || analyzing) return;
      const progress = Math.max(0, Math.min(100, percent));
      value.textContent = `${progress}%`;
      track.setAttribute('aria-valuenow', String(progress));
      fill.style.width = `${progress}%`;
    },
    onUploaded() {
      if (!live()) return;
      analyzing = true;
      label.textContent = text('importLoading');
      value.textContent = '';
      track.setAttribute('aria-label', text('importLoading'));
      track.removeAttribute('aria-valuenow');
      fill.style.width = '';
      track.classList.add('is-analyzing');
    },
    async complete() {
      if (!live()) return;
      analyzing = true;
      const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
      // Preserve the moving bar's current frame before expanding it to completion.
      const frame = getComputedStyle(fill);
      fill.style.width = frame.width;
      fill.style.transform = frame.transform;
      track.classList.remove('is-analyzing');
      void fill.offsetWidth;
      track.classList.add('is-complete');
      fill.style.width = '100%';
      fill.style.transform = 'translateX(0)';
      track.setAttribute('aria-valuenow', '100');
      track.setAttribute('aria-label', text('importAnalysisComplete'));
      label.textContent = text('importAnalysisComplete');
      value.textContent = '100%';
      if (!reduced) await new Promise(resolve => setTimeout(resolve, 380));
    },
    dispose() {
      disposed = true;
      root.replaceChildren();
      root.hidden = true;
    },
  };
}
