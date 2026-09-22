"""Account UI checks with mocked API: never writes to the live database."""
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright


def main():
    errors, writes = [], []
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
        assert page.locator(".account-notification").count() == 30
        assert page.locator("html").get_attribute("lang") == "it"
        page.locator("#accountMoreNotifications").click()
        page.wait_for_timeout(150)
        assert page.locator(".account-notification").count() == 31
        page.locator("[data-read]").first.click()
        page.wait_for_timeout(150)
        assert "30" in page.locator("#accountUnreadCount").inner_text()
        page.locator("#accountReadAll").click()
        page.locator("#accountUnreadOnly").check()
        page.wait_for_timeout(200)
        assert page.locator(".account-notification").count() == 0
        page.locator('[data-account-view="settings"]').click()
        page.locator('#accountSettings summary').click()
        page.locator('[data-admin-select-value="fr"]').click()
        page.wait_for_timeout(300)
        assert user["preferred_language"] == "fr"
        assert page.locator("html").get_attribute("lang") == "fr"
        page.screenshot(path="/tmp/leverage-account-desktop.png", full_page=True)
        page.set_viewport_size({"width": 390, "height": 844})
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
        assert not errors, errors
        browser.close()
    print("Account UI passed: notifications, pagination, language, password flows, mobile; API fully mocked.")


if __name__ == "__main__":
    main()
