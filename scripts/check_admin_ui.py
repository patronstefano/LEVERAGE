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
            elif path == "/admin/data-overview":
                payload = {
                    "athletes": {"total": 1250, "verified": 50, "incomplete": 1200, "missing_birth_year": 1000, "mag": 650, "wag": 600},
                    "events": {"total": 500, "verified": 20, "incomplete": 480, "missing_dates": 10, "with_results": 400, "without_results": 100},
                    "results": {"total": 40000, "with_final_score": 39000, "without_final_score": 1000, "with_d_score": 20000, "with_e_score": 100, "with_penalty": 100, "with_bonus": 100},
                }
            elif path == "/admin/activity-overview":
                payload = {"total": 3, "pending": 1, "approved": 2, "reverted": 0,
                    "by_action": [{"key": "create", "count": 3}], "by_entity": [{"key": "Athlete", "count": 3}],
                    "actors": [{"admin_id": 7, "email": "actor@example.test", "count": 3, "pending": 1, "last_activity": "2026-09-28T10:00:00"}],
                    "recent": [{"id": 15, "admin_id": 7, "email": "actor@example.test", "action": "create", "entity_type": "Athlete", "entity_id": 2, "review_status": "pending", "created_at": "2026-09-28T10:00:00"}],
                }
            elif path == "/admin/entities-to-complete":
                payload = {"athletes": [{**athlete, "missing_fields": ["birth_year"]}], "events": [], "total_athletes": 1, "total_events": 0}
            elif path == "/admin/users":
                payload = [{"id": 77, "email": "review@example.test", "role": "admin"}]
            elif path == "/admin/audit-logs":
                payload = [{"id": 91, "entity_type": "Athlete", "entity_id": 1, "action": "update", "created_at": "2026-09-30T10:00:00", "review_status": "pending", "admin_id": 77, "before_json": '{"country":"ITA"}', "after_json": '{"country":"FRA"}'}]
            elif path == "/data-suggestions/":
                payload = [{"id": 12, "entity_type": "athlete", "entity_id": 1, "field_name": "birth_year", "suggested_value": "2001", "evidence": "Official profile", "source_url": "https://example.org/profile"}]
            elif path == "/admin/calendar":
                payload = {"events": [], "summary": {"total_events": 0}, "reminders": []}
            elif path == "/site-analytics/admin/summary":
                payload = {"start_date": "2026-09-01", "end_date": "2026-09-30", "visitors": 42,
                           "sessions": 50, "page_views": 100, "searches": 20, "athlete_views": 30,
                           "event_views": 15, "dashboard_views": 5, "total_events": 170,
                           "average_session_seconds": None,
                           "users": {"registered_users": 10, "verified_users": 8, "unverified_users": 2,
                                     "active_users": 6, "inactive_users": 4, "active_window_days": 30},
                           "top_searches": [{"label": "European Championships", "count": 4}],
                           "top_athletes": [], "top_events": []}
            elif path == "/events/":
                payload = [event]
            elif path == "/events/1/result-groups":
                payload = [{"discipline": "MAG", "category": "senior", "format": "individual", "round": "final", "apparatus": "FX", "day": None, "count": 1}]
            elif path == "/results/":
                payload = [{"id": 1, "event_id": 1, "athlete_id": 1, "discipline": "MAG", "category": "senior", "format": "individual", "round": "final", "apparatus": "FX", "day": None, "D_score": 5, "score": 13, "E_score": None, "Penalty": None, "Bonus": None}]
            elif path == "/athletes/1":
                payload = athlete
            elif path == "/events/1/manual-entry-options":
                payload = {"event": event, "disciplines": ["MAG", "WAG"], "categories": ["senior"],
                           "formats": ["individual"], "rounds": ["final", "qualification"],
                           "apparatus_by_discipline": {"MAG": ["FX", "PH"], "WAG": ["VT", "UB"]}}
            elif path == "/events/1/result-athlete-suggestions":
                payload = [athlete]
            if route.request.method not in ("GET", "OPTIONS"):
                writes.append({"path": path, "body": route.request.post_data})
                if path == "/results/1/scores":
                    route.fulfill(json={"id": 1, **json.loads(route.request.post_data)["values"]}, headers={"Access-Control-Allow-Origin": "*"})
                elif path == "/imports/gymternet/preview":
                    route.fulfill(json=preview, headers={"Access-Control-Allow-Origin": "*"})
                elif path == "/data-suggestions/12/accept":
                    route.fulfill(json={"id": 12}, headers={"Access-Control-Allow-Origin": "*"})
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
        admin_back_top = back.bounding_box()['y']
        back.click()
        page.locator('.account-view-switcher').wait_for()
        account_option_style = page.locator('.account-view-toggle .segmented-option').first.evaluate('node => { const s = getComputedStyle(node); return [s.height, s.fontSize, s.fontWeight, s.padding]; }')
        panel_style = page.locator('#accountSettings').evaluate('node => { const s = getComputedStyle(node); return [s.backgroundColor, s.borderRadius, s.padding]; }')
        title_style = page.locator('#accountSettings > .compact-section-header h2').evaluate('node => { const s = getComputedStyle(node); return [s.fontSize, s.fontWeight, s.lineHeight]; }')
        admin_link = page.locator('.account-navigation-actions a[href="#/admin"]').bounding_box()
        super_link = page.locator('.account-navigation-actions a[href="#/super-admin"]').bounding_box()
        assert super_link['x'] + super_link['width'] < admin_link['x']
        notifications_button = page.locator('[data-account-view="notifications"]').bounding_box()
        assert admin_link['x'] + admin_link['width'] < notifications_button['x']
        page.goto("http://127.0.0.1:5173/#/admin")
        page.locator(".admin-center").wait_for()
        assert page.locator('[data-admin-tab="security"]').count() == 0
        for tab in ["overview", "entry", "results", "entities", "imports", "review", "merge", "notifications", "statistics", "users", "audit"]:
            base = '/super-admin/' if tab in ['users', 'audit'] else '/admin/'
            page.evaluate("(route) => location.hash = route", base + tab)
            page.wait_for_timeout(500)
            assert page.locator("#adminWorkspace").count(), tab
            assert abs(page.locator('.detail-back-button').bounding_box()['y'] - admin_back_top) < 1
            if tab != 'notifications':
                assert page.locator('#adminWorkspace').evaluate('node => { const s = getComputedStyle(node); return [s.backgroundColor, s.borderRadius, s.padding]; }') == panel_style
                assert page.locator('#adminWorkspace > .compact-section-header h2').evaluate('node => { const s = getComputedStyle(node); return [s.fontSize, s.fontWeight, s.lineHeight]; }') == title_style
                assert page.locator('#adminWorkspace > .compact-section-header h2').inner_text()
                for control in page.locator('#adminWorkspace input:not([type=hidden]):not([type=checkbox]):not(#adminImportFile):visible, #adminWorkspace .admin-custom-select > summary:visible, #adminChooseFile').all():
                    assert abs(control.bounding_box()['height'] - 36) < 1
            else:
                assert page.locator('#adminWorkspace').is_hidden()
            assert page.locator('.admin-view-toggle .segmented-option').first.evaluate('node => { const s = getComputedStyle(node); return [s.height, s.fontSize, s.fontWeight, s.padding]; }') == account_option_style
            assert page.locator('.admin-view-toggle #adminNotificationsToggle').count() == 0
            if tab != 'notifications':
                option = page.locator('.admin-view-toggle [aria-current="page"]').bounding_box()
                thumb = page.locator('.admin-view-thumb').bounding_box()
                assert abs(option['x'] - thumb['x']) < 1 and abs(option['width'] - thumb['width']) < 1
            assert page.locator('#authLink').get_attribute('aria-current') == 'page'
            assert page.locator('#authLink').get_attribute('href') == '#' + base + tab
            assert page.locator('#authLink').evaluate('node => getComputedStyle(node).backgroundColor') == 'rgb(25, 23, 71)'
            feedback = page.locator("#adminFeedback").inner_text()
            assert not feedback, (tab, feedback)
            if tab == 'overview':
                assert page.locator('.admin-data-group').count() == 3
                assert page.locator('[data-overview-count="athletes.total"]').inner_text().replace('.', '') == '1250'
                assert page.locator('[data-overview-count="results.total"]').inner_text() == '40.000'
                assert not page.locator('.admin-overview-link').count()
            if tab == "entry":
                page.locator('#adminCreateForm input[name=last_name]').wait_for()
                page.locator('#adminCreateForm input[name=last_name]').focus()
                page.wait_for_timeout(200)
                focus_style = page.locator('#adminCreateForm input[name=last_name]').evaluate('el => { const s = getComputedStyle(el); return [s.outlineStyle, s.borderTopColor, s.boxShadow]; }')
                assert focus_style == ['none', 'rgba(25, 23, 71, 0.32)', 'rgba(25, 23, 71, 0.08) 0px 0px 0px 3px'], focus_style
                assert page.locator('#adminNewAthlete').get_attribute('aria-pressed') == 'true'
                for name, value in [('country', 'ITA'), ('birth_year', '2001')]:
                    control = page.locator(f'#adminCreateForm [name={name}]').locator('..')
                    control.locator('summary').click()
                    page.wait_for_timeout(180)
                    visible_count = control.locator('.admin-custom-select-menu').evaluate('menu => { const r = menu.getBoundingClientRect(); return [...menu.querySelectorAll("[role=option]")].filter(el => { const b = el.getBoundingClientRect(); return b.top >= r.top && b.bottom <= r.bottom; }).length; }')
                    assert visible_count == 4, visible_count
                    control.locator(f'[data-admin-select-value="{value}"]').click()
                    assert page.locator(f'#adminCreateForm [name={name}]').input_value() == value
                assert page.locator('#adminNewAthlete').bounding_box()['x'] < page.locator('#adminNewEvent').bounding_box()['x']
                page.locator("#adminNewEvent").click()
                page.locator("#adminCreateForm input[name=name]").wait_for()
                assert page.locator("#adminCreateForm input[name=name]").count()
                assert page.locator('#adminNewEvent').get_attribute('aria-pressed') == 'true'
                page.locator("#adminNewAthlete").click()
                page.wait_for_timeout(200)
                assert page.locator("#adminCreateForm input[name=last_name]").count()
                assert page.locator('#adminNewEvent').get_attribute('aria-pressed') == 'false'
                assert page.locator('#adminNewAthlete').get_attribute('aria-pressed') == 'true'
                assert page.locator('.admin-create-toggle .segmented-thumb').evaluate('el => getComputedStyle(el).backgroundColor') == 'rgb(25, 23, 71)'
                assert page.locator('.admin-create-toggle').evaluate('el => el.style.getPropertyValue("--selected-index")') == '0'
                assert page.locator('[name="event_search"]').count() == 0
                assert page.locator('#adminEntry').count() == 0
            if tab == "results":
                assert page.locator('#adminNewAthlete').count() == 0
                assert page.locator('#adminNewEvent').count() == 0
                page.locator('[name="event_search"]').fill("Admin")
                page.locator("#adminEventOptions button").first.click()
                page.locator('.admin-score-table').wait_for()
                assert page.locator('#adminResultForm').count() == 0
                assert page.locator('[data-save]').is_disabled()
                page.locator('.admin-score-table [name=score]').fill('13.2')
                page.locator('[data-reset]').click()
                assert page.locator('.admin-score-table [name=score]').input_value() == '13'
                page.locator('.admin-score-table [name=score]').fill('13.2')
                page.locator('[data-save]').click()
                page.wait_for_timeout(200)
                saved = json.loads(writes[-1]["body"])
                assert writes[-1]['path'] == '/results/1/scores'
                assert saved['expected']['score'] == 13
                assert saved['values']['score'] == 13.2
                assert saved['values']['Penalty'] is None and saved['values']['Bonus'] is None
                assert page.locator('[data-save]').is_disabled()
                page.screenshot(path="/tmp/leverage-admin-result-editor.png", full_page=True)
                page.set_viewport_size({"width": 390, "height": 844})
                page.wait_for_timeout(100)
                assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
                assert page.locator('.admin-score-table-scroll').evaluate('el => el.scrollWidth > el.clientWidth')
                page.screenshot(path="/tmp/leverage-admin-result-editor-mobile.png", full_page=True)
                page.set_viewport_size({"width": 1440, "height": 1000})
            if tab == "users":
                page.locator('#adminUsersForm button[type=submit]').click()
                page.locator('#adminUsers .account-notification').wait_for()
                assert 'review@example.test' in page.locator('#adminUsers').inner_text()
                assert page.locator('.admin-user-role-actions').is_visible()
            if tab == "audit":
                page.locator('#adminAuditForm button[type=submit]').click()
                page.locator('#adminAudit .account-notification').wait_for()
                assert page.locator('[data-action=approve].admin-accept-button').count() == 1
                assert page.locator('[data-action=revert].filter-clear-button').count() == 1
                assert page.locator('#adminRestoreForm').locator('..').get_attribute('class') == 'admin-tool-block'
                page.set_viewport_size({"width": 390, "height": 844})
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                page.screenshot(path='/tmp/leverage-super-audit-mobile.png', full_page=True)
                page.set_viewport_size({"width": 1440, "height": 1000})
            if tab == "statistics":
                assert page.locator('#adminStats > .admin-tool-block').count() == 5
                assert page.locator('.admin-stats-metrics dd').first.inner_text() == '42'
                assert page.locator('#adminStats .empty-state').count() == 2
                assert page.locator('#adminStatsForm [name=start_date]').input_value() == '2026-09-01'
                assert 'Data di inizio' in page.locator('#adminStatsForm').inner_text()
                assert 'European Championships' in page.locator('.admin-stats-top').inner_text()
                page.set_viewport_size({"width": 390, "height": 844})
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                page.screenshot(path='/tmp/leverage-admin-statistics-mobile.png', full_page=True)
                page.set_viewport_size({"width": 1440, "height": 1000})
            if tab == "review":
                assert page.locator('.admin-revisions > .admin-tool-block').count() == 3
                page.locator('.admin-revision-group summary').first.click()
                assert page.locator('.admin-revisions .account-notification').count() == 2
                assert page.locator('[data-accept]').evaluate('el => el.classList.contains("admin-accept-button")')
                page.locator('[data-accept]').click()
                page.locator('#adminRevisionSuggestions .empty-state').wait_for()
                assert json.loads(writes[-1]['body']) == {'value': '2001'}
                page.screenshot(path="/tmp/leverage-admin-revisions.png", full_page=True)
            if tab == "imports":
                year_control = page.locator('[name=year_hint]').locator('..')
                assert year_control.locator('summary').bounding_box()['x'] < page.locator('#adminChooseFile').bounding_box()['x']
                year_control.locator('summary').click()
                year_control.locator('[data-admin-select-value="2026"]').click()
                assert page.locator('[name=year_hint]').input_value() == '2026'
                assert page.locator('#adminImportFilename').inner_text() == 'Nessun file selezionato'
                assert page.locator('#adminImportForm [name=kind]').input_value() == 'gymternet'
                assert 'Risultati (The Gymternet)' in page.locator('#adminImportForm').inner_text()
                with page.expect_file_chooser() as chooser:
                    page.locator('#adminChooseFile').click()
                chooser.value.set_files({"name": "test.csv", "mimeType": "text/csv", "buffer": b"test"})
                assert page.locator('#adminImportFilename').inner_text() == 'test.csv'
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
        page.evaluate("location.hash = '/admin/review'")
        page.wait_for_timeout(300)
        page.locator('[data-section-nav="home"]').click()
        page.wait_for_timeout(300)
        assert page.locator('#authLink').get_attribute('href') == '#/admin/review'
        page.reload()
        page.wait_for_timeout(300)
        assert page.locator('#authLink').get_attribute('href') == '#/admin/review'
        page.locator('#authLink').click()
        page.locator('.admin-center').wait_for()
        assert page.url.endswith('#/admin/review')
        page.locator('.detail-back-button').click()
        page.locator('.account-view-switcher').wait_for()
        assert page.locator('#authLink').get_attribute('href') == '#/account'
        page.evaluate("location.hash = '/admin'")
        page.wait_for_timeout(300)
        page.screenshot(path="/tmp/leverage-admin-desktop.png", full_page=True)
        for width, height in [(1366, 768), (1280, 720), (1440, 900)]:
            page.set_viewport_size({'width': width, 'height': height})
            page.wait_for_timeout(100)
            assert page.locator('#adminWorkspace').bounding_box()['height'] < 450, (width, height)
            assert page.evaluate('document.documentElement.scrollHeight <= innerHeight + 180'), (width, height)
        page.set_viewport_size({"width": 390, "height": 844})
        assert page.locator('.admin-data-group').count() == 3
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.screenshot(path="/tmp/leverage-data-overview-mobile.png", full_page=True)
        page.goto("http://127.0.0.1:5173/#/super-admin")
        page.locator('.admin-view-toggle [data-admin-tab="audit"]').wait_for()
        page.locator('#adminActivityPeriod').wait_for()
        assert page.locator('.admin-activity-details .admin-revision-list').count() == 2
        assert page.locator('.admin-activity-details .account-notification').count() == 2
        assert page.locator('.admin-data-total').count() == 3
        assert not page.locator('.admin-activity-details[open]').count()
        page.locator('.admin-activity-details > summary').first.click()
        assert 'actor@example.test' in page.locator('#adminWorkspace').inner_text()
        page.locator('.admin-activity-details > summary').first.click()
        page.locator('#adminActivityPeriod input[name="days"]').evaluate("node => node.value = '7'")
        page.locator('#adminActivityPeriod button[type="submit"]').click()
        page.wait_for_timeout(300)
        assert page.locator('#adminActivityPeriod input[name="days"]').input_value() == '7'
        page.locator('.admin-activity-details > summary').first.click()
        page.locator('.admin-activity-details > summary').last.click()
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.screenshot(path="/tmp/leverage-super-activity-mobile.png", full_page=True)
        page.set_viewport_size({"width": 1440, "height": 1000})
        page.screenshot(path="/tmp/leverage-super-activity-desktop.png", full_page=True)
        page.set_viewport_size({"width": 390, "height": 844})
        assert 'Super Admin' in page.locator('.admin-center h1').inner_text()
        assert page.locator('.detail-back-button').get_attribute('href') == '#/account'
        page.locator('.admin-view-toggle [data-admin-tab="audit"]').click()
        page.wait_for_timeout(500)
        assert page.url.endswith('#/super-admin/audit')
        page.goto("http://127.0.0.1:5173/#/home")
        page.wait_for_timeout(300)
        assert page.locator('#authLink').get_attribute('href') == '#/super-admin/audit'
        page.locator('#authLink').click()
        page.locator('#adminWorkspace').wait_for()
        assert page.locator('#adminNotificationsToggle').is_visible()
        page.locator('#adminNotificationsToggle').click()
        page.wait_for_timeout(300)
        assert page.locator('.admin-view-thumb').is_hidden()
        page.screenshot(path="/tmp/leverage-admin-mobile.png", full_page=True)
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), "Horizontal overflow"
        current_role[0] = "admin"
        page.reload()
        page.locator('[role="alert"]').wait_for()
        assert not page.locator('.admin-center').count()
        page.goto("http://127.0.0.1:5173/#/account")
        page.locator('.account-navigation-actions').wait_for()
        assert not page.locator('.account-navigation-actions a[href="#/super-admin"]').count()
        page.goto("http://127.0.0.1:5173/#/admin")
        page.locator(".admin-center").wait_for()
        assert not page.locator('.admin-center-nav a[href="#/admin/users"]').count()
        assert not page.locator('.admin-center-nav a[href="#/admin/audit"]').count()
        current_role[0] = "user"
        page.reload()
        page.locator('[role="alert"]').wait_for()
        assert not page.locator(".admin-center").count()
        assert page.locator('#app').evaluate('el => el.classList.contains("auth-main-view")')
        assert page.locator('.auth-brand-welcome .auth-brand-logo').is_visible()
        assert page.locator('.auth-required-actions a').get_attribute('href') == '#/login'
        assert page.locator('#authLink').get_attribute('href') == '#/account'
        assert not errors, errors
        browser.close()
    print("Admin views, creation forms, desktop/mobile layout: passed")


if __name__ == "__main__":
    main()
