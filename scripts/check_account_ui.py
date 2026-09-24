"""Account UI checks with mocked API: never writes to the live database."""
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright


def main():
    def check_input(locator):
        assert abs(locator.bounding_box()['height'] - 36) < 0.1
        style = locator.evaluate("node => { const s = getComputedStyle(node); return [s.fontSize, s.fontWeight, s.borderRadius]; }")
        assert style == ['14px', '400', '12px'], style

    errors, writes = [], []
    failures = {"notifications": False}
    user = {"id": 999, "email": "user@example.test", "role": "user", "preferred_language": "it"}
    notices = [{"id": n, "message": "Notifica personale " + str(n), "is_read": False,
                "created_at": "2026-09-22T12:00:00Z"} for n in range(31)]
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.add_init_script("localStorage.setItem('leverage.authToken','test-only'); localStorage.setItem('leverage.language','en');")

        def api(route):
            from urllib.parse import parse_qs
            url = urlsplit(route.request.url)
            path, params = url.path, parse_qs(url.query)
            payload = []
            if path == "/auth/me":
                payload = user
            elif path == "/notifications/unread-count":
                payload = {"count": sum(not n["is_read"] for n in notices)}
            elif path == "/notifications/":
                if failures['notifications']:
                    route.fulfill(status=503, body='Service unavailable')
                    return
                items = [n for n in notices if not n["is_read"]] if params.get("unread_only") == ["true"] else notices
                offset = int(params.get("offset", [0])[0])
                payload = items[offset:offset + 30]
            if route.request.method not in ("GET", "OPTIONS"):
                writes.append(path)
                if path == "/preferences/language":
                    user["preferred_language"] = route.request.post_data_json["preferred_language"]
                elif path == "/notifications/read-all":
                    for n in notices:
                        n["is_read"] = True
                elif path.startswith("/notifications/"):
                    next(n for n in notices if n["id"] == int(path.split("/")[2]))["is_read"] = True
                payload = {"message": "OK"}
            route.fulfill(json=payload, headers={"Access-Control-Allow-Origin": "*"})

        page.route("**:8000/**", api)
        page.goto("http://127.0.0.1:5173/#/account?section=notifications")
        page.locator(".account-notification").first.wait_for()
        assert page.locator('#accountNotifications').evaluate('node => getComputedStyle(node).borderRadius') == '12px'
        assert page.locator('#accountNotifications > .compact-section-header h2').evaluate('node => getComputedStyle(node).fontSize') == '17px'
        assert page.locator('#accountReadAll').bounding_box()['height'] == 36
        notification_top = page.locator('#accountNotifications').bounding_box()['y']
        notification_header_height = page.locator('#accountNotifications > .compact-section-header').bounding_box()['height']
        assert page.locator('#app').evaluate("node => node.classList.contains('primary-section-main-view')")
        assert page.locator('#app').evaluate("node => getComputedStyle(node).paddingTop") == '58px'
        assert 'La tua area privata dove visualizzare atleti, eventi e rankings preferiti.' in page.locator('.page-heading').inner_text()
        page.wait_for_timeout(200)
        assert page.locator('#authLink').get_attribute('aria-current') == 'page'
        assert page.locator('#authLink').evaluate('node => getComputedStyle(node).backgroundColor') == 'rgb(25, 23, 71)'
        assert page.locator('.account-view-toggle [data-account-view]').count() == 3
        assert page.locator('#demoUserNotifications').is_hidden()
        assert page.locator('.account-favorites-section .section-header').count() == 0
        assert page.locator('.account-view-switcher').evaluate("node => getComputedStyle(node, '::after').borderBottomColor") == 'rgba(25, 23, 71, 0.06)'
        assert page.locator('.account-view-switcher').evaluate("node => getComputedStyle(node, '::after').borderBottomWidth") == '1px'
        assert page.locator('.account-tool-actions button').count() == 2
        assert page.locator('.account-summary').count() == 0
        assert page.locator('.account-view-switcher .account-tool-actions button').count() == 2
        slider = page.locator('.account-view-toggle').bounding_box()
        actions = page.locator('.account-navigation-actions').bounding_box()
        assert abs((slider['y'] + slider['height'] / 2) - (actions['y'] + actions['height'] / 2)) < 1
        assert actions['x'] > slider['x'] + slider['width']
        notification_button = page.locator('.account-tool-actions button').nth(0).bounding_box()
        settings_button = page.locator('.account-tool-actions button').nth(1).bounding_box()
        logout_button = page.locator('#signOutButton').bounding_box()
        assert abs(settings_button['x'] - notification_button['x'] - notification_button['width'] - 8) < 1
        assert abs(logout_button['x'] - settings_button['x'] - settings_button['width'] - 8) < 1
        for control in page.locator('.account-tool-actions button').all():
            control.hover()
            page.wait_for_timeout(600)
            assert control.get_attribute('title') is None
            assert control.locator('[role=tooltip], .account-tool-tooltip').count() == 0
        for box in page.locator('.account-tool-actions button').all():
            rect = box.bounding_box()
            assert rect['width'] == 36 and rect['height'] == 36
        assert page.locator('[data-account-view="notifications"]').get_attribute("aria-pressed") == "true"
        assert page.locator(".account-notification").count() == 30
        assert page.locator("html").get_attribute("lang") == "it"
        page.locator('#accountReadAll').hover()
        page.wait_for_timeout(200)
        assert page.locator('#accountReadAll').evaluate('node => getComputedStyle(node).color') == 'rgb(180, 35, 24)'
        assert page.locator('#accountReadAll').evaluate('node => getComputedStyle(node).backgroundColor') == 'rgb(255, 255, 255)'
        page.screenshot(path='/tmp/leverage-notifications-desktop.png', full_page=True)
        failures['notifications'] = True
        page.locator('#accountUnreadOnly').click()
        assert page.locator('#accountUnreadOnly').get_attribute('aria-pressed') == 'true'
        page.locator('#accountNotificationRetry').wait_for(state='visible')
        assert page.locator('.account-notification').count() == 30
        assert page.locator('#accountNotificationList').get_attribute('aria-busy') == 'false'
        failures['notifications'] = False
        page.locator('#accountNotificationRetry').click()
        page.locator('#accountNotificationRetry').wait_for(state='hidden')
        page.wait_for_timeout(150)
        page.locator('#accountUnreadOnly').click()
        assert page.locator('#accountUnreadOnly').get_attribute('aria-pressed') == 'false'
        page.wait_for_timeout(150)
        page.locator("#accountMoreNotifications").click()
        page.wait_for_timeout(150)
        assert page.locator(".account-notification").count() == 31
        page.locator("[data-read]").first.click()
        page.wait_for_timeout(150)
        assert "30" in page.locator("#accountUnreadCount").inner_text()
        page.locator("#accountReadAll").click()
        page.locator("#accountUnreadOnly").click()
        page.wait_for_timeout(200)
        assert page.locator(".account-notification").count() == 0
        assert page.locator('.account-notification-empty').inner_text() == 'Nessuna notifica da leggere.'
        assert page.locator('#accountReadAll').is_disabled()
        page.locator('[data-account-view="settings"]').click()
        for field in page.locator('#accountPasswordForm input').all():
            assert field.bounding_box()['height'] == 36
            assert field.evaluate('node => getComputedStyle(node).fontSize') == '15px'
        assert page.locator('#accountSettings').evaluate('node => getComputedStyle(node).borderRadius') == '12px'
        assert page.locator('#accountPasswordForm button[type=submit]').bounding_box()['width'] < 150
        assert page.locator('[data-account-view="settings"]').get_attribute("aria-pressed") == "true"
        assert abs(page.locator('#accountSettings').bounding_box()['y'] - notification_top) < 1
        assert page.locator('#accountSettings > .compact-section-header').bounding_box()['height'] == notification_header_height
        identity = page.locator('.account-settings-identity')
        assert identity.locator('dd').first.is_visible()
        assert identity.locator('dd').all_text_contents() == ['user@example.test', 'USER']
        assert identity.locator('dt').all_text_contents() == ['Email', 'Ruolo']
        assert identity.locator('input, select, button').count() == 0
        assert page.locator('.account-view-toggle').get_attribute('data-account-content-active') == 'false'
        for content in ['athletes', 'events', 'rankings']:
            page.locator(f'[data-account-view="{content}"]').click()
            for tool in ['notifications', 'settings']:
                button = page.locator(f'[data-account-view="{tool}"]')
                button.click()
                assert button.get_attribute('aria-pressed') == 'true'
                button.click()
                assert button.get_attribute('aria-pressed') == 'false'
                assert page.locator(f'[data-account-view="{content}"]').get_attribute('aria-checked') == 'true'
                assert page.locator(f'[data-account-view-panel="{content}"]').is_visible()
        page.locator('[data-account-view="settings"]').click()
        page.locator('#accountSettings summary').click()
        page.locator('[data-admin-select-value="fr"]').click()
        page.wait_for_timeout(300)
        assert user["preferred_language"] == "fr"
        assert page.locator("html").get_attribute("lang") == "fr"
        page.screenshot(path="/tmp/leverage-account-desktop.png", full_page=True)
        page.set_viewport_size({"width": 390, "height": 844})
        assert page.locator('#app').evaluate("node => getComputedStyle(node).paddingTop") == '24px'
        page.screenshot(path="/tmp/leverage-account-mobile.png", full_page=True)
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), "Mobile overflow"
        page.locator('[name="current_password"]').fill("ExistingPassword123!")
        page.locator('[name="new_password"]').fill("ReplacementPassword123!")
        page.locator('[name="repeat_password"]').fill("DifferentPassword123!")
        page.locator('#accountPasswordForm button[type=submit]').click()
        assert "/auth/password/change" not in writes
        page.locator('[name="repeat_password"]').fill("ReplacementPassword123!")
        page.locator('#accountPasswordForm button[type=submit]').click()
        page.wait_for_timeout(200)
        assert "/auth/password/change" in writes
        assert page.evaluate("localStorage.getItem('leverage.authToken')") is None
        for mode, endpoint in [("forgot-password", "/auth/password/forgot"), ("resend-verification", "/auth/resend-verification")]:
            page.evaluate("mode => location.hash = '/' + mode", mode)
            page.locator('#accountRecoveryForm input[name=email]').fill("user@example.test")
            if mode == 'forgot-password':
                assert page.locator('.account-recovery-intro').is_visible()
                assert page.locator('.account-recovery-intro').inner_text()
                page.screenshot(path='/tmp/leverage-recovery-help.png', full_page=True)
                assert page.locator('.account-recovery a[href="#/forgot-password"]').count() == 0
                assert page.locator('.account-recovery a[href="#/login"]').count() == 0
                assert page.locator('.auth-login-links a[href="#/login"]').count() == 1
            assert page.locator('#authLink').get_attribute('aria-current') == 'page'
            check_input(page.locator('#accountRecoveryForm input[name=email]'))
            recovery_button = page.locator('#accountRecoveryForm button')
            bottom_gap = page.locator('.account-recovery').evaluate("node => node.getBoundingClientRect().bottom - node.querySelector('button[type=submit]').getBoundingClientRect().bottom")
            assert 19 <= bottom_gap <= 22, bottom_gap
            assert recovery_button.bounding_box()['width'] < page.locator('#accountRecoveryForm').bounding_box()['width']
            assert recovery_button.evaluate('node => getComputedStyle(node).justifySelf') == 'center'
            page.locator('#accountRecoveryForm button').click()
            page.wait_for_timeout(200)
            assert endpoint in writes
            assert page.locator('#accountRecoveryFeedback').inner_text()
        page.evaluate("location.hash = '/reset-password?token=abcdefghijklmnopqrstuvwxyz123456'")
        page.locator('[name="new_password"]').fill("ReplacementPassword123!")
        page.locator('[name="repeat_password"]').fill("ReplacementPassword123!")
        page.locator('#accountRecoveryForm button').click()
        page.wait_for_timeout(200)
        assert "/auth/password/reset" in writes
        assert "token=" not in page.url
        page.evaluate("location.hash = '/account'")
        prompt = page.locator('.auth-required-actions')
        prompt.wait_for()
        message = page.locator('.auth-brand-welcome p').bounding_box()
        action = prompt.locator('a').bounding_box()
        assert action['y'] - (message['y'] + message['height']) >= 18
        assert page.locator('#app').evaluate("node => node.classList.contains('auth-main-view')")
        page.screenshot(path='/tmp/leverage-account-signed-out.png', full_page=True)
        before_logo = page.locator('.auth-brand-logo').bounding_box()
        prompt.locator('a').click()
        page.locator('#loginForm').wait_for()
        assert page.locator('.auth-login-panel [data-demo-role]').count() == 0
        assert page.locator('footer [data-demo-role]').count() == 3
        assert page.locator('#footerDemoAccess').is_visible()
        page.wait_for_timeout(200)
        assert page.locator('#authLink').get_attribute('aria-current') == 'page'
        assert page.locator('#authLink').evaluate('node => getComputedStyle(node).backgroundColor') == 'rgb(25, 23, 71)'
        check_input(page.locator('#loginEmail'))
        check_input(page.locator('#loginPassword'))
        assert page.locator('.auth-login-panel a[href="#/forgot-password"]').count() == 0
        assert page.locator('.auth-login-links a[href="#/forgot-password"]').count() == 1
        assert page.locator('.auth-login-links a[href="#/register"]').count() == 1
        assert page.locator('.auth-login-panel a[href="#/resend-verification"]').count() == 0
        assert page.locator('#loginForm button[type=submit]').bounding_box()['height'] == 36
        assert not page.locator('#loginMessage').is_visible()
        bottom_gap = page.locator('.auth-login-panel').evaluate("node => node.getBoundingClientRect().bottom - node.querySelector('button[type=submit]').getBoundingClientRect().bottom")
        assert 19 <= bottom_gap <= 22, bottom_gap
        submit = page.locator('#loginForm button[type=submit]')
        assert submit.evaluate("node => getComputedStyle(node).backgroundColor") == 'rgb(255, 255, 255)'
        submit.hover()
        page.wait_for_timeout(200)
        assert submit.evaluate("node => getComputedStyle(node).backgroundColor") == 'rgb(255, 255, 255)'
        assert submit.evaluate("node => getComputedStyle(node).borderTopColor") == 'rgb(25, 23, 71)'
        assert submit.evaluate("node => getComputedStyle(node).color") == 'rgb(25, 23, 71)'
        assert page.locator('.auth-brand-form .auth-login-subtitle').count() == 1
        assert page.locator('.auth-login-panel .auth-login-subtitle').count() == 0
        page.wait_for_timeout(650)
        after_logo = page.locator('.auth-brand-logo').bounding_box()
        assert before_logo['width'] == 80 and after_logo['width'] == 28
        assert page.locator('.auth-brand-form h1').is_visible()
        assert 'sr-only' not in (page.locator('.auth-brand-form h1').get_attribute('class') or '')
        assert after_logo['y'] < before_logo['y']
        page.screenshot(path='/tmp/leverage-login-logo.png', full_page=True)
        assert not page.locator('#mfaField').is_visible()
        assert not page.locator('#loginMfaCode').evaluate('node => node.required')
        page.route('**:8000/auth/login', lambda route: route.fulfill(
            json={'mfa_required': True}, headers={'Access-Control-Allow-Origin': '*'}))
        page.locator('#loginEmail').fill('admin@example.test')
        page.locator('#loginPassword').fill('ExistingPassword123!')
        page.locator('#loginForm button[type=submit]').click()
        page.locator('#mfaField').wait_for(state='visible')
        check_input(page.locator('#loginMfaCode'))
        assert page.locator('#loginMfaCode').evaluate('node => node.required')
        assert page.locator('#loginMfaCode').evaluate('node => document.activeElement === node')
        page.set_viewport_size({'width': 1440, 'height': 1000})
        assert page.locator('.auth-login-panel').bounding_box()['width'] == 420
        page.screenshot(path='/tmp/leverage-login-compact.png', full_page=True)
        page.evaluate("location.hash = '/forgot-password'")
        page.locator('#accountRecoveryForm').wait_for()
        assert page.locator('.account-recovery').bounding_box()['width'] == 420
        page.screenshot(path='/tmp/leverage-recovery-compact.png', full_page=True)
        page.evaluate("location.hash = '/register'")
        page.locator('#registerForm').wait_for()
        assert page.locator('#registerForm > p').count() == 0
        for field_id in ['registerPassword', 'registerPasswordConfirm']:
            field = page.locator('#' + field_id)
            assert field.get_attribute('minlength') == '6'
            field.fill('Six12!')
            assert field.evaluate('node => node.checkValidity()')
        assert not page.locator('#registerMessage').is_visible()
        bottom_gap = page.locator('.auth-register-panel').evaluate("node => node.getBoundingClientRect().bottom - node.querySelector('button[type=submit]').getBoundingClientRect().bottom")
        assert 19 <= bottom_gap <= 22, bottom_gap
        assert page.locator('.auth-register-panel a[href="#/login"]').count() == 0
        assert page.locator('.auth-login-links a[href="#/login"]').count() == 1
        assert page.locator('.auth-register-panel').bounding_box()['width'] == 420
        assert page.locator('.auth-brand-logo').bounding_box()['width'] == 28
        assert page.locator('.auth-brand-form .home-body').is_visible()
        assert page.locator('#registerForm button[type=submit]').bounding_box()['height'] == 36
        for field in page.locator('#registerForm input').all():
            check_input(field)
        page.screenshot(path='/tmp/leverage-register-desktop.png', full_page=True)
        page.set_viewport_size({'width': 390, 'height': 844})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.screenshot(path='/tmp/leverage-register-mobile.png', full_page=True)
        for route in ['/login', '/forgot-password', '/register', '/account']:
            page.evaluate('route => location.hash = route', route)
            page.wait_for_timeout(100)
            logo = page.locator('.auth-brand-logo')
            assert logo.evaluate('node => getComputedStyle(node).animationName') == 'authLogoArrival'
            assert logo.evaluate('node => getComputedStyle(node).animationDuration') == '0.52s'
        page.emulate_media(reduced_motion='reduce')
        assert page.locator('.auth-brand-logo').evaluate('node => getComputedStyle(node).animationName') == 'none'
        page.emulate_media(reduced_motion='no-preference')
        page.locator('footer [data-demo-role="user"]').click()
        page.wait_for_timeout(200)
        assert '/auth/demo-login' in writes
        assert page.locator('#footerDemoMessage').inner_text()
        user['email'] = 'demo.user@leverage-demo.com'
        page.goto('http://127.0.0.1:5173/#/account')
        page.reload()
        page.locator('#demoUserNotifications').wait_for(state='visible')
        write_count = len(writes)
        page.locator('#demoUserNotifications').click()
        page.locator('.account-notification').first.wait_for()
        assert page.locator('.account-notification').count() == 30
        assert 'DEMO' in page.locator('.account-notification').first.inner_text()
        page.locator('#accountMoreNotifications').click()
        page.wait_for_timeout(100)
        assert page.locator('.account-notification').count() == 35
        page.locator('#accountReadAll').click()
        page.wait_for_timeout(100)
        assert page.locator('#accountUnreadCount').is_hidden()
        assert len(writes) == write_count
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.reload()
        page.locator('.account-notification').first.wait_for()
        assert 'DEMO' not in page.locator('.account-notification').first.inner_text()
        assert not errors, errors
        browser.close()
    print("Account UI passed: notifications, pagination, language, password flows, mobile; API fully mocked.")


if __name__ == "__main__":
    main()
