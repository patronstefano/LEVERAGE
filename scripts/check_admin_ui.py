"""Read-only browser smoke checks; all write requests are blocked."""
import json
from pathlib import Path
from urllib.request import urlopen

from playwright.sync_api import sync_playwright


def main():
    schema = json.load(urlopen("http://127.0.0.1:8000/openapi.json"))
    errors = []
    writes = []
    event = {"id": 1, "name": "Admin test event", "year": 2026, "discipline": "MAG and WAG", "category": "senior", "level": "National Event"}
    athlete = {"id": 1, "first_name": "Ada", "last_name": "Test", "country": "ITA", "discipline": "MAG"}
    preview = {"filename": "test.csv", "parsed_rows": 1, "importable_results": 1,
               "issues": [], "conflicts": [], "duplicates": [], "sample_results": [],
               "athlete_match_review": [{"review_id": "r1", "problem_type": "possible_existing_athlete_match",
                 "imported_athlete": athlete, "suggestions": [{"suggestion_id": "s1", "target_athlete": athlete}]}],
               "orphan_dscore_review": []}
    current_role = ["super_admin"]
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.add_init_script("localStorage.setItem('leverage.authToken', 'test-only'); localStorage.setItem('leverage.language', 'it');")

        def api(route):
            path = route.request.url.split(":8000", 1)[-1].split("?", 1)[0]
            payload = []
            if path == "/auth/me":
                payload = {"id": 999, "email": "admin@example.test", "role": current_role[0], "preferred_language": "it"}
            elif path == "/openapi.json":
                payload = schema
            elif path == "/admin/entities-to-complete":
                payload = {"athletes": [], "events": [], "total_athletes": 0, "total_events": 0}
            elif path == "/admin/calendar":
                payload = {"events": [], "summary": {"total_events": 0}, "reminders": []}
            elif path == "/site-analytics/admin/summary":
                payload = {"unique_visitors": 0, "registered_users": 0}
            elif path == "/events/":
                payload = [event]
            elif path == "/events/1/manual-entry-options":
                payload = {"event": event, "disciplines": ["MAG", "WAG"], "categories": ["senior"],
                           "formats": ["individual"], "rounds": ["final", "qualification"],
                           "apparatus_by_discipline": {"MAG": ["FX", "PH"], "WAG": ["VT", "UB"]}}
            elif path == "/events/1/result-athlete-suggestions":
                payload = [athlete]
            if route.request.method not in ("GET", "OPTIONS"):
                writes.append({"path": path, "body": route.request.post_data})
                if path == "/events/1/results/bulk":
                    route.fulfill(json=[{"id": 1}], headers={"Access-Control-Allow-Origin": "*"})
                elif path == "/imports/gymternet/preview":
                    route.fulfill(json=preview, headers={"Access-Control-Allow-Origin": "*"})
                else:
                    route.fulfill(status=403, json={"detail": "Write blocked by UI test"})
            else:
                route.fulfill(json=payload, headers={"Access-Control-Allow-Origin": "*"})

        page.route("**:8000/**", api)
        page.goto("http://127.0.0.1:5173/#/admin")
        page.locator(".admin-center").wait_for()
        back = page.locator('.detail-topbar .detail-back-button')
        assert back.inner_text() == 'Torna all’Area Personale'
        assert back.get_attribute('href') == '#/account'
        back.click()
        page.locator('.account-view-switcher').wait_for()
        admin_link = page.locator('.account-navigation-actions a[href="#/admin"]').bounding_box()
        notifications_button = page.locator('[data-account-view="notifications"]').bounding_box()
        assert admin_link['x'] + admin_link['width'] < notifications_button['x']
        page.goto("http://127.0.0.1:5173/#/admin")
        page.locator(".admin-center").wait_for()
        for tab in ["overview", "entry", "entities", "imports", "calendar", "review", "merge", "notifications", "statistics", "security", "users", "audit"]:
            page.evaluate("(tab) => location.hash = '/admin/' + tab", tab)
            page.wait_for_timeout(500)
            assert page.locator("#adminWorkspace").count(), tab
            assert page.locator('#authLink').get_attribute('aria-current') == 'page'
            assert page.locator('#authLink').get_attribute('href') == '#/account'
            assert page.locator('#authLink').evaluate('node => getComputedStyle(node).backgroundColor') == 'rgb(25, 23, 71)'
            feedback = page.locator("#adminFeedback").inner_text()
            assert not feedback, (tab, feedback)
            if tab == "entry":
                page.locator("#adminNewEvent").click()
                page.locator("#adminCreateForm").wait_for()
                assert page.locator("#adminCreateForm input[name=name]").count()
                page.locator("#adminNewAthlete").click()
                page.wait_for_timeout(200)
                assert page.locator("#adminCreateForm input[name=last_name]").count()
                page.locator('[name="event_search"]').fill("Admin")
                page.locator("#adminEventOptions button").first.click()
                page.locator("#adminResultForm").wait_for()
                page.locator('[name="athlete_search"]').fill("Test")
                page.locator("#adminAthleteOptions button").first.click()
                for key, value in {"D_score": "5", "E_score": "8", "score": "13"}.items():
                    page.locator("#adminResultForm [name=" + key + "]").fill(value)
                page.locator('#adminResultForm button[type="submit"]').click()
                assert page.locator("#adminBatch").inner_text().startswith("Test Ada")
                page.locator("#adminSubmitResults").click()
                page.wait_for_timeout(200)
                saved = json.loads(writes[-1]["body"])["results"][0]
                assert saved["athlete_id"] == 1
                assert saved["D_score"] == 5 and saved["score"] == 13
                assert saved["Penalty"] is None and saved["Bonus"] is None
                page.locator('#adminContext [data-admin-select]').first.locator("summary").click()
                page.locator('#adminContext [data-admin-select-value="WAG"]').click()
                assert page.locator('#adminResultForm [name="apparatus"]').input_value() == "VT"
                page.screenshot(path="/tmp/leverage-admin-entry.png", full_page=True)
            if tab == "imports":
                page.locator('input[name="file"]').set_input_files({"name": "test.csv", "mimeType": "text/csv", "buffer": b"test"})
                page.locator('#adminImportForm button[type="submit"]').click()
                row = page.locator("[data-review-type=athlete]")
                row.wait_for()
                row.locator("[data-admin-select]").first.locator("summary").click()
                row.locator('[data-admin-select-value="suggestion:s1"]').click()
                page.locator("#adminReviewPreview").click()
                page.wait_for_timeout(200)
                assert "accept_suggestion" in writes[-1]["body"]
                assert "s1" in writes[-1]["body"]
                page.screenshot(path="/tmp/leverage-admin-import.png", full_page=True)
        page.evaluate("location.hash = '/admin'")
        page.wait_for_timeout(300)
        page.screenshot(path="/tmp/leverage-admin-desktop.png", full_page=True)
        page.set_viewport_size({"width": 390, "height": 844})
        page.screenshot(path="/tmp/leverage-admin-mobile.png", full_page=True)
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), "Horizontal overflow"
        current_role[0] = "admin"
        page.reload()
        page.locator(".admin-center").wait_for()
        assert not page.locator('.admin-center-nav a[href="#/admin/users"]').count()
        assert not page.locator('.admin-center-nav a[href="#/admin/audit"]').count()
        current_role[0] = "user"
        page.reload()
        page.locator('[role="alert"]').wait_for()
        assert not page.locator(".admin-center").count()
        assert not errors, errors
        browser.close()
    print("Admin views, creation forms, desktop/mobile layout: passed")


if __name__ == "__main__":
    main()
