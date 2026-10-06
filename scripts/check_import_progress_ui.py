"""Isolated browser checks for import progress; no backend requests or writes."""
from playwright.sync_api import sync_playwright


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 900, 'height': 500})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.route('**/progress-test', lambda route: route.fulfill(content_type='text/html', body='''
            <link rel="stylesheet" href="/styles.css">
            <main class="admin-center"><div id="progress"></div></main>'''))
        page.goto('http://127.0.0.1:5173/progress-test')
        page.evaluate('''async () => {
            const {mountImportProgress, mountImportProgressDialog} = await import('/admin-import-progress.js');
            const labels = {importUploading: 'Caricamento file...', importLoading: 'Analisi del file in corso...',
                importAnalysisComplete: 'Analisi completata'};
            window.mount = uploading => mountImportProgress({root: document.querySelector('#progress'),
                text: key => labels[key], esc: value => value, uploading});
            window.mountDialog = dialog => mountImportProgressDialog({dialog,
                text: key => labels[key] || 'Ricalcola anteprima', esc: value => value});
            window.progress = mount(true);
        }''')
        page.evaluate('progress.onUploadProgress(43)')
        assert page.locator('[role=progressbar]').get_attribute('aria-valuenow') == '43'
        page.evaluate('progress.onUploaded()')
        assert page.locator('[role=progressbar]').get_attribute('aria-valuenow') is None
        assert page.locator('[data-import-progress-value]').inner_text() == ''
        assert page.locator('.is-analyzing > span').evaluate('el => getComputedStyle(el).animationName') == 'admin-import-analyzing'
        page.wait_for_timeout(180)
        page.screenshot(path='/tmp/leverage-import-progress-running.png')
        page.evaluate('() => { window.finished = false; window.completion = progress.complete().then(() => {finished = true;}); }')
        assert page.locator('[role=progressbar]').get_attribute('aria-valuenow') == '100'
        assert not page.evaluate('finished')
        assert page.locator('[data-import-progress-label]').inner_text() == 'Analisi completata'
        page.wait_for_function('finished')
        track = page.locator('[role=progressbar]').bounding_box()
        fill = page.locator('[role=progressbar] > span').bounding_box()
        assert abs(track['width'] - fill['width']) < 1
        page.screenshot(path='/tmp/leverage-import-progress-complete.png')
        page.evaluate('progress.dispose(); progress.onUploaded(); progress.onUploadProgress(75)')
        assert page.locator('[role=progressbar]').count() == 0
        # Recalculation starts indeterminate and cancellation never announces success.
        page.evaluate('window.progress = mount(false)')
        assert page.locator('[role=progressbar]').get_attribute('aria-valuenow') is None
        page.evaluate('progress.dispose()')
        assert page.locator('#progress').inner_text() == ''
        page.emulate_media(reduced_motion='reduce')
        page.evaluate('window.progress = mount(false)')
        assert page.locator('.is-analyzing > span').evaluate('el => getComputedStyle(el).animationName') == 'none'
        page.evaluate('progress.complete()')
        assert page.locator('[role=progressbar]').get_attribute('aria-valuenow') == '100'
        page.set_viewport_size({'width': 390, 'height': 500})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.evaluate('''() => {
            progress.dispose();
            const dialog = document.createElement('dialog');
            dialog.className = 'admin-confirm';
            dialog.innerHTML = '<h2>Tralasciare 1 riga del file?</h2><div class="admin-center-actions"><button>Annulla</button><button disabled>Conferma</button></div>';
            document.body.append(dialog); dialog.showModal();
            window.dialogProgress = mountDialog(dialog);
        }''')
        assert page.locator('dialog[open] [role=progressbar]').count() == 1
        assert page.locator('dialog button:disabled').count() == 2
        page.keyboard.press('Escape')
        assert page.locator('dialog[open]').count() == 1
        page.screenshot(path='/tmp/leverage-import-dialog-mobile.png')
        # Error cleanup keeps a borrowed confirmation open for retry/cancel.
        page.evaluate('dialogProgress.dispose()')
        assert page.locator('dialog[open]').count() == 1
        assert page.locator('dialog button:disabled').count() == 1
        assert page.locator('dialog [role=progressbar]').count() == 0
        page.evaluate("document.querySelector('dialog').remove(); window.dialogProgress = mountDialog()")
        assert page.locator('dialog[open]').count() == 1
        page.evaluate('dialogProgress.complete()')
        assert page.locator('dialog [role=progressbar]').get_attribute('aria-valuenow') == '100'
        page.evaluate('dialogProgress.dispose()')
        assert page.locator('dialog').count() == 0
        page.evaluate('window.dialogProgress = mountDialog(); location.hash = "away"')
        page.wait_for_function('!document.querySelector("dialog")')
        page.evaluate('dialogProgress.dispose()')
        assert not errors, errors
        browser.close()
    print('Import progress: upload, analysis, completion, cancellation, reduced motion and mobile passed')


if __name__ == '__main__':
    main()
