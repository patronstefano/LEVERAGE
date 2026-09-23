"""Exercise authentication validation without real API writes."""
from playwright.sync_api import sync_playwright


def submit_with_stable_position(form):
    panel = form.locator('xpath=ancestor::section[contains(@class,"auth-panel")]')
    button = form.locator('button[type=submit]')
    before_panel, before_button = panel.bounding_box(), button.bounding_box()
    footer = form.page.locator('.footer')
    before_footer = footer.bounding_box()
    button.click()
    after_panel, after_button = panel.bounding_box(), button.bounding_box()
    assert abs(after_panel['y'] - before_panel['y']) < 1
    assert abs(after_button['y'] - before_button['y']) < 1
    assert after_panel['height'] > before_panel['height']
    assert abs(footer.bounding_box()['y'] - before_footer['y']) < 1


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 1000})
        page.add_init_script("localStorage.removeItem('leverage.authToken'); localStorage.setItem('leverage.language','it');")
        errors, requests = [], []
        response = {"status": 401, "body": {"detail": "Invalid email or password"}}
        page.on('pageerror', lambda error: errors.append(str(error)))

        def api(route):
            if route.request.method == 'POST':
                requests.append(route.request.url)
                if response.get('offline'):
                    route.abort()
                    return
                route.fulfill(status=response['status'], json=response['body'])
            else:
                route.fulfill(json=[])

        page.route('**:8000/**', api)
        page.goto('http://127.0.0.1:5173/#/login')
        form = page.locator('#loginForm')
        form.wait_for()
        assert form.evaluate('node => node.noValidate')
        page.locator('#loginEmail').focus()
        assert page.locator('#loginEmail').evaluate('node => getComputedStyle(node).outlineStyle') == 'none'
        assert page.locator('#loginEmail').evaluate('node => getComputedStyle(node).borderTopColor') == 'rgba(25, 23, 71, 0.32)'
        assert page.locator('#loginEmail').evaluate('node => getComputedStyle(node).boxShadow') == 'rgba(25, 23, 71, 0.08) 0px 0px 0px 3px'
        submit_with_stable_position(form)
        assert not requests
        assert page.locator('#loginMessage').inner_text() == 'Completa i campi obbligatori.'
        assert form.locator('[aria-invalid=true]').count() == 2
        assert page.locator('#loginEmail').evaluate('node => getComputedStyle(node).outlineStyle') == 'none'
        assert page.locator('#loginEmail').evaluate('node => getComputedStyle(node).borderTopColor') == 'rgba(184, 52, 52, 0.76)'
        assert page.locator('.auth-login-panel').evaluate('node => getComputedStyle(node).animationName') == 'savedRankingInvalidShake'
        page.locator('#loginEmail').fill('invalid')
        page.locator('#loginPassword').fill('short')
        form.locator('button[type=submit]').click()
        assert 'email valido' in page.locator('#loginMessage').inner_text()
        assert '6 a 128' in page.locator('#loginMessage').inner_text()
        assert not requests
        page.locator('#loginEmail').fill('user@example.test')
        page.locator('#loginPassword').fill('Valid6!')
        form.locator('button[type=submit]').click()
        page.wait_for_timeout(150)
        assert page.locator('#loginMessage').inner_text() == 'Email o password errate.'
        for status, detail, expected in [
            (403, 'Email verification required', 'Verifica la tua email'),
            (429, 'Account temporarily locked', 'Troppi tentativi'),
            (503, 'unavailable', 'Invio email non disponibile'),
            (422, [{'loc': ['body', 'email']}], 'Alcuni dati non sono validi'),
        ]:
            response.update(status=status, body={'detail': detail})
            form.locator('button[type=submit]').click()
            page.wait_for_timeout(150)
            assert expected in page.locator('#loginMessage').inner_text()
        response.update(status=200, body={'mfa_required': True})
        form.locator('button[type=submit]').click()
        page.locator('#mfaField').wait_for(state='visible')
        count = len(requests)
        form.locator('button[type=submit]').click()
        assert len(requests) == count
        assert page.locator('#loginMfaCode').get_attribute('aria-invalid') == 'true'
        page.locator('#loginMfaCode').fill('12')
        form.locator('button[type=submit]').click()
        assert 'Codice di Autenticazione o di recupero valido' in page.locator('#loginMessage').inner_text()
        response.update(status=401, body={'detail': 'Invalid authentication credentials'})
        page.locator('#loginMfaCode').fill('123456')
        form.locator('button[type=submit]').click()
        page.wait_for_timeout(150)
        assert 'Codice di Autenticazione errato' in page.locator('#loginMessage').inner_text()
        page.screenshot(path='/tmp/leverage-login-validation.png', full_page=True)

        page.evaluate("location.hash = '/register'")
        form = page.locator('#registerForm')
        submit_with_stable_position(form)
        assert form.locator('[aria-invalid=true]').count() == 3
        page.locator('#registerEmail').fill('user@example.test')
        page.locator('#registerPassword').fill('Valid6!')
        page.locator('#registerPasswordConfirm').fill('Other6!')
        count = len(requests)
        form.locator('button[type=submit]').click()
        assert len(requests) == count
        assert page.locator('#registerMessage').inner_text() == 'Le password non coincidono.'
        page.locator('#registerPasswordConfirm').fill('Valid6!')
        assert not form.locator('[aria-invalid=true]').count()
        response.update(status=202, body={'message': 'OK'})
        form.locator('button[type=submit]').click()
        page.wait_for_timeout(150)
        assert page.locator('#registerMessage').get_attribute('class').find('is-error') == -1

        page.evaluate("location.hash = '/forgot-password'")
        form = page.locator('#accountRecoveryForm')
        submit_with_stable_position(form)
        assert page.locator('#accountRecoveryFeedback').inner_text() == 'Completa i campi obbligatori.'
        form.locator('input').fill('bad-email')
        form.locator('button').click()
        assert page.locator('#accountRecoveryFeedback').inner_text() == 'Inserisci un indirizzo email valido.'
        form.locator('input').fill('user@example.test')
        response['offline'] = True
        form.locator('button').click()
        page.wait_for_timeout(300)
        assert 'Connessione non riuscita' in page.locator('#accountRecoveryFeedback').inner_text()
        response['offline'] = False
        response.update(status=202, body={'message': 'OK'})
        form.locator('button').click()
        page.wait_for_timeout(150)
        assert 'Se l’indirizzo soddisfa' in page.locator('#accountRecoveryFeedback').inner_text()
        page.emulate_media(reduced_motion='reduce')
        form.locator('button').click()
        assert page.locator('.account-recovery').evaluate('node => getComputedStyle(node).animationName') == 'none'
        page.set_viewport_size({'width': 390, 'height': 844})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.screenshot(path='/tmp/leverage-recovery-validation.png', full_page=True)
        for width, height in [(1280, 720), (1440, 900), (390, 844)]:
            page.set_viewport_size({'width': width, 'height': height})
            page.goto('http://127.0.0.1:5173/#/register')
            page.reload()
            form = page.locator('#registerForm')
            form.wait_for()
            submit_with_stable_position(form)
            page.locator('#registerEmail').fill('invalid')
            page.locator('#registerPassword').fill('short')
            before_footer = page.locator('.footer').bounding_box()['y'] + page.evaluate('scrollY')
            form.locator('button[type=submit]').click()
            after_footer = page.locator('.footer').bounding_box()['y'] + page.evaluate('scrollY')
            assert abs(after_footer - before_footer) < 1
        assert not errors, errors
        browser.close()
    print('Authentication validation passed: missing/invalid fields, credentials, MFA, verification, rate limits, email delivery, network, mismatch, success and reduced motion.')


if __name__ == '__main__':
    main()
