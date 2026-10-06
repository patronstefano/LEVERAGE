"""Read-only browser smoke checks; all write requests are blocked."""
import json
from pathlib import Path
from urllib.request import urlopen
from urllib.parse import parse_qs, urlparse

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
    event_days = [None]
    full_classification_size = [0]
    dismissed_scan_jobs = set()
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
                    "athletes": {"total": 1250, "verified": 50, "scanned_world_gymnastics": 300, "possible_duplicates": 12, "incomplete": 1200, "missing_birth_year": 1000, "mag": 650, "wag": 600},
                    "events": {"total": 500, "verified": 20, "scanned_world_gymnastics": 100, "possible_duplicates": 3, "incomplete": 480, "missing_dates": 10, "with_results": 400, "without_results": 100},
                    "results": {"total": 40000, "with_final_score": 39000, "without_final_score": 1000, "with_d_score": 20000, "with_e_score": 100, "with_penalty": 100, "with_bonus": 100},
                }
            elif path == "/admin/activity-overview":
                payload = {"total": 3, "pending": 1, "approved": 2, "reverted": 0,
                    "by_action": [{"key": "create", "count": 3}], "by_entity": [{"key": "Athlete", "count": 3}],
                    "actors": [{"admin_id": 7, "email": "actor@example.test", "count": 3, "pending": 1, "last_activity": "2026-09-28T10:00:00"}],
                    "recent": [{"id": 15, "admin_id": 7, "email": "actor@example.test", "action": "create", "entity_type": "Athlete", "entity_id": 2, "review_status": "pending", "created_at": "2026-09-28T10:00:00"}],
                }
            elif path == "/world-gymnastics/scan/status":
                payload = {"enabled": False, "started_at": None, "counts": {"matched": 1}, "total": 1}
                if parse_qs(urlparse(route.request.url).query).get('entity_type') == ['event']:
                    payload['counts']['matched'] = 7
                    payload['total'] = 7
            elif path == '/admin/entity-duplicates':
                kind = parse_qs(urlparse(route.request.url).query).get('entity_type', ['athlete'])[0]
                entity = {**athlete, 'name': 'Test Ada'} if kind == 'athlete' else event
                payload = {'total': 1, 'items': [{'left': entity, 'right': {**entity, 'id': 2},
                    'compatibility': 98, 'reasons': ['similar_name'], 'fingerprint': 'a' * 64}]}
            elif path in ['/admin/entity-duplicates/athlete/1/2', '/admin/entity-duplicates/event/1/2']:
                entity = {**athlete, 'name': 'Test Ada', 'result_count': 2, 'country_history': [], 'events': []}
                payload = {'left': entity, 'right': {**entity, 'id': 2}, 'conflicting_scores': 1}
            elif path == "/world-gymnastics/scan/matches":
                payload = {"total": 1, "items": [{"id": 51, "entity_type": "athlete", "entity_id": 1, "entity_name": "Test Ada", "candidates": [{"fig_id": "123", "first_name": "Ada", "last_name": "Test", "country": "ITA", "discipline": "WAG", "match_score": .95, "profile_url": "https://www.gymnastics.sport/site/athletes/bio_detail.php?id=123"}]}]}
                if parse_qs(urlparse(route.request.url).query).get('entity_type') == ['event']:
                    payload = {"total": 1, "items": [{"id": 52, "entity_type": "event", "entity_id": 1, "entity_name": "Admin test event", "candidates": [{"event_id": "456", "title": "Event candidate", "match_score": .9, "event_url": "https://www.gymnastics.sport/site/events/detail.php?id=456"}]}]}
                payload['items'] = [item for item in payload['items'] if item['id'] not in dismissed_scan_jobs]
                payload['total'] = len(payload['items'])
            elif path == "/admin/entities-to-complete":
                payload = {"athletes": [{**athlete, "missing_fields": ["birth_year"]}], "events": [], "total_athletes": 1, "total_events": 0}
            elif path == "/admin/users":
                payload = [{"id": 77, "email": "review@example.test", "role": "admin"}, {"id": 78, "email": "last@example.test", "role": "super_admin", "is_active": True, "is_last_active_super_admin": True}]
                query = parse_qs(urlparse(route.request.url).query).get('search', [''])[0].strip().lower()
                payload = [user for user in payload if query in user['email'].lower()]
            elif path == "/admin/audit-logs":
                payload = [{"id": 91, "entity_type": "Athlete", "entity_id": 1, "action": "update", "created_at": "2026-09-30T10:00:00", "review_status": "pending", "admin_id": 77, "before_json": '{"country":"ITA"}', "after_json": '{"country":"FRA"}'}]
                payload.append({**payload[0], 'id': 92, 'action': 'create', 'before_json': None})
                payload.append({**payload[0], 'id': 93, 'action': 'merge'})
                payload[0].update(admin_email='review@example.test', admin_current_role='admin')
                payload[1].update(admin_email='super@example.test', admin_current_role='super_admin')
            elif path == "/data-suggestions/":
                payload = [
                    {"id": 12, "entity_type": "athlete", "entity_id": 1, "field_name": "birth_year", "suggested_value": "2001", "evidence": "Official profile", "status": "pending", "source_title": "World Gymnastics Athlete Profile", "source_url": "https://www.gymnastics.sport/site/athletes/bio_detail.php?id=1"},
                    {"id": 13, "entity_type": "athlete", "entity_id": 1, "field_name": "country", "suggested_value": "ITA", "status": "pending", "source_title": "Generic suggestion", "source_url": "https://example.org/profile"},
                    {"id": 14, "entity_type": "athlete", "entity_id": 1, "field_name": "country", "suggested_value": "ITA", "status": "pending", "source_title": "World Gymnastics Athlete Profile", "source_url": "https://gymnastics.sport.example.org/profile"},
                ]
            elif path == "/admin/calendar":
                payload = {"events": [], "summary": {"total_events": 0}, "reminders": []}
            elif path == "/site-analytics/admin/summary":
                payload = {"start_date": "2026-09-01", "end_date": "2026-09-30", "visitors": 42,
                           "sessions": 50, "page_views": 100, "searches": 20, "athlete_views": 30,
                           "event_views": 0, "dashboard_views": 0, "total_events": 170,
                           "average_session_seconds": None,
                           "users": {"registered_users": 10, "verified_users": 8, "unverified_users": 2,
                                     "active_users": 6, "inactive_users": 4, "active_window_days": 30},
                           "top_searches": [{"label": "European Championships", "count": 4}],
                           "top_athletes": [], "top_events": []}
            elif path == "/events/":
                payload = [event]
            elif path == "/events/1":
                payload = event
            elif path == "/events/1/result-groups":
                payload = [{"discipline": discipline, "category": category, "format": "individual", "round": "final", "apparatus": apparatus, "day": day, "count": 1} for discipline, apparatuses in [('MAG', ['AA', 'VT AVG', 'FX', 'HB', 'PB', 'SR', 'VT', 'PH']), ('WAG', ['FX', 'BB', 'VT', 'UB'])] for category in ["senior", "junior"] for apparatus in apparatuses for day in event_days]
            elif path == "/results/":
                payload = [{"id": 1, "event_id": 1, "athlete_id": 1, "discipline": "MAG", "category": "senior", "format": "individual", "round": "final", "apparatus": "FX", "day": None, "D_score": 5, "score": 13, "E_score": None, "Penalty": None, "Bonus": None}]
                payload.append({**payload[0], "id": 2, "category": "junior"})
                payload = [{**row, "day": day, "id": row['id'] + index * 10} for index, day in enumerate(event_days) for row in payload]
                if full_classification_size[0]:
                    params = parse_qs(urlparse(route.request.url).query)
                    offset = int(params.get('offset', ['0'])[0])
                    limit = int(params.get('limit', ['500'])[0])
                    payload = [{**payload[0], 'id': 1000 + index} for index in range(offset, min(offset + limit, full_classification_size[0]))]
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
                if path in ["/results/1/scores", "/results/2/scores"]:
                    route.fulfill(json={"id": int(path.split('/')[2]), **json.loads(route.request.post_data)["values"]}, headers={"Access-Control-Allow-Origin": "*"})
                elif path == "/imports/gymternet/preview":
                    route.fulfill(json=preview, headers={"Access-Control-Allow-Origin": "*"})
                elif path == "/data-suggestions/12/accept":
                    route.fulfill(json={"id": 12}, headers={"Access-Control-Allow-Origin": "*"})
                elif path.startswith('/world-gymnastics/scan/matches/') and path.endswith('/dismiss'):
                    dismissed_scan_jobs.add(int(path.split('/')[4]))
                    route.fulfill(json={"status": "dismissed"}, headers={"Access-Control-Allow-Origin": "*"})
                elif path in ["/events/1/merge-preview", "/athletes/1/merge-preview"]:
                    kind = 'event' if path.startswith('/events/') else 'athlete'
                    route.fulfill(json={
                        "can_merge": True, "preview_token": "a" * 64,
                        f"source_{kind}": {"id": 1, "name": "Test Cup", "discipline": "MAG", "country": "ITA"},
                        f"target_{kind}": {"id": 2, "name": "Test Cup", "discipline": "MAG", "country": "ITA"},
                        "source_result_count": 12, "target_result_count": 24,
                    }, headers={"Access-Control-Allow-Origin": "*"})
                elif path in ['/events/1/merge', '/athletes/1/merge']:
                    key = 'target_event' if path.startswith('/events/') else 'target_athlete'
                    route.fulfill(json={"merged": True, key: {"id": 2}}, headers={"Access-Control-Allow-Origin": "*"})
                elif path.startswith('/admin/entity-duplicates/') and path.endswith('/keep-separate'):
                    route.fulfill(json={"decision": "keep_separate"}, headers={"Access-Control-Allow-Origin": "*"})
                elif path in ['/athletes/', '/events/']:
                    route.fulfill(status=201, json={"id": 1, **json.loads(route.request.post_data)}, headers={"Access-Control-Allow-Origin": "*"})
                elif path == '/admin/audit-logs/91/approve':
                    route.fulfill(json={"id": 91, "review_status": "approved"}, headers={"Access-Control-Allow-Origin": "*"})
                elif path == '/admin/users/77' and route.request.method == 'DELETE':
                    route.fulfill(json={"id": 77, "is_active": False}, headers={"Access-Control-Allow-Origin": "*"})
                else:
                    route.fulfill(status=403, json={"detail": "Write blocked by UI test"})
            else:
                route.fulfill(json=payload, headers={"Access-Control-Allow-Origin": "*"})

        page.route("**:8000/**", api)
        page.goto("http://127.0.0.1:5173/#/admin")
        page.locator(".admin-center").wait_for()
        assert page.locator('[data-admin-tab]').evaluate_all('tabs => tabs.map(tab => tab.dataset.adminTab)') == ['overview', 'world-gymnastics', 'review', 'merge', 'entry', 'results', 'imports']
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
        assert page.locator('[data-admin-tab="entities"]').count() == 0
        page.evaluate("location.hash = '/admin/entities'")
        page.wait_for_timeout(500)
        assert page.locator('[data-admin-tab="overview"]').get_attribute('aria-current') == 'page'
        assert page.locator('#adminRecordLookup').count() == 0
        for tab in ["overview", "entry", "results", "imports", "review", "merge", "statistics", "users", "audit"]:
            base = '/super-admin/' if tab in ['users', 'audit', 'statistics'] else '/admin/'
            page.evaluate("(route) => location.hash = route", base + tab)
            page.wait_for_timeout(500)
            assert page.locator("#adminWorkspace").count(), tab
            assert abs(page.locator('.detail-back-button').bounding_box()['y'] - admin_back_top) < 1
            assert page.locator('#adminWorkspace').evaluate('node => { const s = getComputedStyle(node); return [s.backgroundColor, s.borderRadius, s.padding]; }') == panel_style
            assert page.locator('#adminWorkspace > .compact-section-header h2').evaluate('node => { const s = getComputedStyle(node); return [s.fontSize, s.fontWeight, s.lineHeight]; }') == title_style
            assert page.locator('#adminWorkspace > .compact-section-header h2').inner_text()
            renamed = {'entry': 'Nuova Entità', 'results': 'Editor Risultati', 'merge': 'Unione Entità', 'statistics': 'Statistiche Sito'}
            if tab in renamed:
                assert page.locator('#adminWorkspace > .compact-section-header h2').inner_text() == renamed[tab]
                assert page.locator(f'[data-admin-tab="{tab}"]').inner_text() == renamed[tab]
            for control in page.locator('#adminWorkspace input:not([type=hidden]):not([type=checkbox]):not(#adminImportFile):visible, #adminWorkspace .admin-custom-select > summary:visible, #adminChooseFile').all():
                expected_height = 34 if control.get_attribute('id') == 'adminEventSearch' else 36
                assert abs(control.bounding_box()['height'] - expected_height) < 1
            assert page.locator('.admin-view-toggle .segmented-option').first.evaluate('node => { const s = getComputedStyle(node); return [s.height, s.fontSize, s.fontWeight, s.padding]; }') == account_option_style
            assert page.locator('.admin-view-toggle #adminNotificationsToggle').count() == 0
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
                assert page.evaluate('''async () => {
                    const {athleteFieldOptions: options, athleteCountryCodes: codes} = await import('/athlete-field-options.js?v=country-names-20261001');
                    for (const language of ['en', 'it', 'es', 'fr']) {
                        const rows = options('country', '', language);
                        if (!codes.every(code => rows.some(row => row.value === code && row.label.startsWith(code + ' (')))) return false;
                    }
                    return options('country', '', 'it').find(row => row.value === 'ITA').label === 'ITA (Italia)'
                        && options('country', '', 'en').find(row => row.value === 'ITA').label === 'ITA (Italy)'
                        && options('country', 'ZZZ', 'it').some(row => row.value === 'ZZZ' && row.label === 'ZZZ')
                        && options('birth_year', '2001', 'it').find(row => row.value === '2001').label === '2001';
                }''')
                page.locator('#adminCreateForm input[name=last_name]').wait_for()
                previous_writes = len(writes)
                page.locator('#adminCreateForm button[type=submit]').click()
                assert page.locator('#adminCreateForm').evaluate('el => el.noValidate')
                assert page.locator('#adminCreateFormValidation').inner_text() == 'Completa i campi obbligatori.'
                assert page.locator('#adminCreateForm input[aria-invalid=true]').count() > 0
                for invalid in page.locator('#adminCreateForm input[aria-invalid=true]').all():
                    invalid.focus()
                    invalid.hover()
                    page.wait_for_timeout(180)
                    colors = invalid.evaluate('el => { const s = getComputedStyle(el); return [s.borderTopColor, s.boxShadow]; }')
                    assert colors == ['rgba(184, 52, 52, 0.76)', 'rgba(184, 52, 52, 0.08) 0px 0px 0px 3px'], colors
                assert page.locator('#adminCreateForm').evaluate('el => getComputedStyle(el).animationName') == 'savedRankingInvalidShake'
                assert len(writes) == previous_writes
                page.locator('#adminCreateForm input[name=last_name]').fill('Test')
                assert page.locator('#adminCreateFormValidation').inner_text() == ''
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
                    bounds = control.locator('.admin-custom-select-menu').evaluate('menu => { const m = menu.getBoundingClientRect(); const b = menu.querySelector("button").getBoundingClientRect(); return {left: b.left - m.left, right: m.right - b.right, top: b.top - m.top}; }')
                    assert bounds['left'] >= 6 and bounds['right'] >= 6 and bounds['top'] >= 6, bounds
                    assert abs(bounds['left'] - bounds['right']) < 2, bounds
                    control.locator(f'[data-admin-select-value="{value}"]').click()
                    assert page.locator(f'#adminCreateForm [name={name}]').input_value() == value
                    if name == 'country':
                        assert control.locator('[data-admin-select-label]').inner_text() == 'ITA (Italia)'
                assert page.locator('#adminNewAthlete').bounding_box()['x'] < page.locator('#adminNewEvent').bounding_box()['x']
                page.locator("#adminNewEvent").click()
                page.locator("#adminCreateForm input[name=name]").wait_for()
                category_label = page.locator('#adminCreateForm [data-admin-select-value="junior and senior"]').text_content().strip()
                assert category_label == 'Junior e Senior', repr(category_label)
                event_start = page.locator('#adminCreateForm [data-admin-date=start_date] input')
                event_start.fill('29/02/2024')
                assert event_start.evaluate('el => el.checkValidity()')
                assert page.locator('#adminCreateForm [name=start_date]').input_value() == '2024-02-29'
                page.locator('#adminCreateForm [name=start_date]').evaluate('el => { el.value = "2026-07-01"; el.dispatchEvent(new Event("admin-date-sync")); }')
                assert event_start.input_value() == '01/07/2026'
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
                for kind, values, message, label in [
                    ('athletes', {'first_name': 'Ada', 'last_name': 'Test'}, 'Nuovo atleta salvato', 'Vai all’atleta'),
                    ('events', {'name': 'Test Cup', 'year': '2026'}, 'Nuovo evento salvato', 'Vai all’evento'),
                ]:
                    if kind == 'events':
                        page.locator('#adminNewEvent').click()
                        page.locator('#adminCreateForm [name=name]').wait_for()
                    assert page.locator('#adminCreate .is-success').count() == 0
                    for name, value in values.items():
                        page.locator(f'#adminCreateForm [name={name}]').fill(value)
                    for control in page.locator('#adminCreateForm [data-admin-select]').all():
                        control.locator('summary').click()
                        control.locator('[data-admin-select-value]:not([disabled])').first.click()
                    page.locator('#adminCreateForm button[type=submit]').click()
                    page.locator('#adminCreate [role=status]').wait_for()
                    assert page.locator('#adminCreate [role=status]').inner_text() == message
                    assert page.locator('#adminCreate .is-success').count() == 1
                    link = page.locator('#adminCreate a')
                    assert link.inner_text() == label
                    notice = page.locator('#adminCreate [role=status]')
                    assert notice.evaluate('el => getComputedStyle(el).fontSize') == link.evaluate('el => getComputedStyle(el).fontSize')
                    assert notice.bounding_box()['height'] == 36
                    assert link.get_attribute('href').startswith(f'#/{kind}/1?from=admin&')
                    assert 'return_to=%2Fadmin%2Fentry' in link.get_attribute('href')
                    assert page.locator('#adminFeedback').inner_text() == ''
            if tab == "merge":
                previous_writes = len(writes)
                page.locator('#adminMergeForm button[type=submit]').click()
                assert page.locator('#adminMergeFormValidation').inner_text() == 'Completa i campi obbligatori.'
                assert len(writes) == previous_writes
                assert page.locator('#adminMergeAthlete').get_attribute('aria-pressed') == 'true'
                page.locator('#adminMergeEvent').click()
                assert page.locator('#adminMergeEvent').get_attribute('aria-pressed') == 'true'
                assert page.locator('.admin-create-toggle').evaluate('el => el.style.getPropertyValue("--selected-index")') == '1'
                for name, value in [('source', '1'), ('target', '2')]:
                    page.locator(f'#adminMergeForm [name={name}]').fill(value)
                page.locator('#adminMergeForm button[type=submit]').click()
                page.locator('#adminMergeCommit').wait_for()
                assert writes[-1]['path'] == '/events/1/merge-preview'
                assert json.loads(writes[-1]['body'])['target_event_id'] == 2
                assert 'preview_token' not in page.locator('#adminMergePreview').inner_text()
                assert page.locator('#adminMergePreview .admin-audit-side h3').all_text_contents() == ['Evento da unire', 'Evento da mantenere']
                sides = page.locator('#adminMergePreview .admin-audit-side')
                assert sides.nth(0).bounding_box()['x'] < sides.nth(1).bounding_box()['x']
                assert '12' in sides.nth(0).inner_text() and '24' in sides.nth(1).inner_text()
                page.screenshot(path='/tmp/leverage-merge-comparison.png', full_page=True)
                page.set_viewport_size({"width": 390, "height": 844})
                assert sides.nth(1).bounding_box()['y'] > sides.nth(0).bounding_box()['y']
                page.set_viewport_size({"width": 1440, "height": 1000})
                page.locator('#adminMergeForm [name=target]').fill('3')
                assert page.locator('#adminMergeCommit').count() == 0
                page.locator('#adminMergeAthlete').click()
                assert page.locator('#adminMergeAthlete').get_attribute('aria-pressed') == 'true'
                assert page.locator('#adminMergeForm [name=source]').input_value() == ''
                for kind, toggle, message, label in [
                    ('athletes', '#adminMergeAthlete', 'Atleti uniti', 'Vai all’atleta'),
                    ('events', '#adminMergeEvent', 'Eventi uniti', 'Vai all’evento'),
                ]:
                    page.locator(toggle).click()
                    for name, value in [('source', '1'), ('target', '2')]:
                        page.locator(f'#adminMergeForm [name={name}]').fill(value)
                    page.locator('#adminMergeForm button[type=submit]').click()
                    page.locator('#adminMergePreview .admin-audit-comparison').wait_for()
                    assert page.locator('#adminMergePreview .admin-audit-side').count() == 2
                    previous_writes = len(writes)
                    page.locator('#adminMergeSwap').click()
                    assert page.locator('#adminMergeForm [name=source]').input_value() == '2'
                    assert page.locator('#adminMergeForm [name=target]').input_value() == '1'
                    assert page.locator('#adminMergeCommit').count() == 0
                    assert page.locator('#adminMergePreview').inner_text() == ''
                    assert len(writes) == previous_writes
                    page.locator('#adminMergeSwap').click()
                    page.locator('#adminMergeForm button[type=submit]').click()
                    page.locator('#adminMergeCommit').wait_for()
                    preview_box = page.locator('#adminMergeForm button[type=submit]').bounding_box()
                    commit_box = page.locator('#adminMergeCommit').bounding_box()
                    assert commit_box['x'] > preview_box['x'] + preview_box['width']
                    assert abs(commit_box['y'] - preview_box['y']) < 1
                    page.locator('#adminMergeCommit').click()
                    page.locator('dialog[open] [data-confirm]').click()
                    notice = page.locator('#adminMergeContent [role=status]')
                    notice.wait_for()
                    assert notice.inner_text() == message
                    assert notice.bounding_box()['height'] == 36
                    assert notice.evaluate('el => getComputedStyle(el).fontSize') == '14px'
                    assert page.locator('#adminMergeForm').count() == 0
                    link = page.locator('#adminMergeContent a')
                    assert link.inner_text() == label
                    assert link.get_attribute('href').startswith(f'#/{kind}/2?from=admin&')
                    assert 'return_to=%2Fadmin%2Fmerge' in link.get_attribute('href')
                    assert page.locator('#adminFeedback').inner_text() == ''
            if tab == "results":
                assert page.evaluate('''async () => {
                    const {classificationHasRecordedExecution: valid} = await import('/admin-result-editor.js?v=execution-validation-20261001');
                    const row = {score: 13, D_score: 5, E_score: 8, Penalty: 0, Bonus: 0};
                    return valid([row, row]) && !valid([]) && !valid([row, {...row, Bonus: null}])
                        && !valid([row, {...row, E_score: null}]) && !valid([row, {...row, score: 14}]);
                }''')
                assert page.locator('#adminNewAthlete').count() == 0
                assert page.locator('#adminNewEvent').count() == 0
                page.locator('[name="event_search"]').fill("Admin")
                page.locator('#adminEventOptions button').first.wait_for()
                assert page.locator('[name=event_search]').get_attribute('placeholder') == 'Cerca eventi per competizione, anno o luogo...'
                assert page.locator('[name=event_search]').evaluate('el => getComputedStyle(el, "::placeholder").fontWeight') == '400'
                assert page.locator('#adminEventSearchForm').bounding_box()['width'] == 520
                assert page.locator('#adminEventSearchForm').bounding_box()['height'] == 36
                assert page.locator('[name=event_search]').evaluate('el => getComputedStyle(el).fontSize') == '15px'
                assert page.locator('#adminEventOptions').bounding_box()['width'] >= 518
                assert page.locator('#adminEventOptions .search-suggestion').count() == 1
                assert page.locator('#adminEventOptions .search-suggestion').first.bounding_box()['height'] == 54
                assert page.locator('#adminEventOptions strong').first.evaluate('el => getComputedStyle(el).fontSize') == '15px'
                assert page.locator('#adminEventOptions span').first.evaluate('el => getComputedStyle(el).fontSize') == '12px'
                assert page.locator('#adminEventOptions').evaluate('el => getComputedStyle(el).borderRadius') == page.locator('#adminEventSearchForm').evaluate('el => getComputedStyle(el).borderRadius')
                assert page.locator('.admin-editor-search-row').evaluate('el => getComputedStyle(el, "::before").content') == 'none'
                assert page.locator('.admin-editor-search-row').evaluate('el => getComputedStyle(el).backgroundColor') == 'rgba(0, 0, 0, 0)'
                assert page.locator('#adminEventOptions').evaluate('el => getComputedStyle(el).backgroundColor') == 'rgb(255, 255, 255)'
                page.screenshot(path='/tmp/leverage-editor-search-background.png')
                assert 'Caricamento' not in page.locator('#adminEventOptions').inner_text()
                page.locator('[name=event_search]').press('Escape')
                assert page.locator('#adminEventOptions').is_hidden()
                page.locator('#adminEventSearchForm .search-clear-button').click()
                assert page.locator('[name=event_search]').input_value() == ''
                assert page.locator('#adminEventOptions').is_hidden()
                page.locator('[name=event_search]').fill('Admin')
                choice = page.locator('#adminEventOptions button').first
                choice.wait_for()
                # Reproduce browsers that do not focus a clicked button before input blur.
                choice.evaluate('el => el.addEventListener("mousedown", event => { event.preventDefault(); document.querySelector("#adminEventSearch").blur(); }, {once: true})')
                choice.hover()
                page.mouse.down()
                page.wait_for_timeout(200)
                assert page.locator('#adminEventOptions').is_visible(), 'Suggestions closed before the event click completed'
                page.mouse.up()
                page.locator('#adminScoreRows tbody tr').first.wait_for()
                page.locator('.admin-score-table').wait_for()
                assert page.locator('.admin-score-table [data-reset]').evaluate_all('buttons => buttons.every(button => button.getBoundingClientRect().right <= button.closest("td").getBoundingClientRect().right - 5)')
                page.set_viewport_size({'width': 390, 'height': 844})
                page.locator('.admin-score-table-scroll').evaluate('el => el.scrollLeft = el.scrollWidth')
                assert page.locator('.admin-score-table [data-reset]').evaluate_all('buttons => buttons.every(button => button.getBoundingClientRect().right <= button.closest(".admin-score-table-scroll").getBoundingClientRect().right - 5)')
                page.set_viewport_size({'width': 1440, 'height': 1000})
                page.locator('.admin-score-table-scroll').evaluate('el => el.scrollLeft = 0')
                page.screenshot(path='/tmp/leverage-editor-action-border.png', full_page=True)
                assert page.locator('#adminReloadClassification').count() == 0
                assert page.locator('#adminClassificationSelectors [name^=classification_]').count() == 4
                assert page.locator('#adminClassificationSelectors').evaluate('el => { const tops = [...el.children].map(child => child.getBoundingClientRect().top); return Math.max(...tops) - Math.min(...tops) < 1; }')
                page.locator('#adminClassificationSelectors').evaluate('el => { const extra = el.firstElementChild.cloneNode(true); extra.dataset.layoutTest = "day"; el.append(extra); }')
                assert page.locator('#adminClassificationSelectors').evaluate('el => { const tops = [...el.children].map(child => child.getBoundingClientRect().top); return Math.max(...tops) - Math.min(...tops) < 1; }')
                page.locator('[data-layout-test="day"]').evaluate('el => el.remove()')
                assert page.locator('[name=classification_day]').count() == 0
                assert page.locator('[name=classification_category]').count() == 0
                apparatus = page.locator('[name=classification_apparatus]')
                assert apparatus.input_value() == 'FX'
                assert apparatus.locator('..').locator('[data-admin-select-value]').evaluate_all('options => options.map(o => o.dataset.adminSelectValue)') == ['FX', 'PH', 'SR', 'VT', 'PB', 'HB']
                assert apparatus.locator('..').locator('[data-admin-select-value="AA"]').count() == 0
                assert apparatus.locator('..').locator('[data-admin-select-value="VT AVG"]').count() == 0
                assert page.locator('[data-execution-notice]').is_visible()
                execution_input = page.locator('.admin-score-table [name=E_score]')
                assert execution_input.input_value() == ''
                assert execution_input.get_attribute('placeholder') == 'E est. 8,000'
                assert execution_input.evaluate('el => getComputedStyle(el, "::placeholder").color') == 'rgb(142, 142, 147)'
                execution_input.fill('8')
                assert execution_input.get_attribute('placeholder') == '—'
                execution_input.fill('')
                assert execution_input.get_attribute('placeholder') == 'E est. 8,000'
                assert page.locator('#adminResultForm').count() == 0
                assert page.locator('[data-save]').is_disabled()
                previous_writes = len(writes)
                page.locator('.admin-score-table [name=D_score]').fill('-1')
                page.locator('[data-save]').click()
                assert page.locator('.admin-score-table [name=D_score]').get_attribute('aria-invalid') == 'true'
                assert page.locator('.admin-score-table [role=status]').inner_text() == 'Alcuni dati non sono validi. Controlla i campi evidenziati.'
                assert len(writes) == previous_writes
                page.locator('[data-reset]').click()
                for key in ['D_score', 'Penalty', 'Bonus']:
                    score_input = page.locator(f'.admin-score-table [name={key}]')
                    assert score_input.get_attribute('step') == '0.1'
                    score_input.fill('1.0')
                    score_input.press('ArrowUp')
                    assert score_input.input_value() == '1.1'
                    score_input.press('ArrowDown')
                    score_input.blur()
                    assert score_input.input_value() == '1.0'
                page.locator('[data-reset]').click()
                assert page.locator('.admin-score-table [name=D_score]').input_value() == '5.0'
                assert page.locator('.admin-score-table [name=Penalty]').input_value() == ''
                assert page.locator('.admin-score-table [name=E_score]').get_attribute('step') == '0.001'
                assert page.locator('.admin-score-table [name=score]').get_attribute('step') == '0.001'
                page.locator('.admin-score-table [name=score]').fill('13.2')
                for value in ['PH', 'FX']:
                    control = page.locator('[name=classification_apparatus]').locator('..')
                    control.locator('summary').click()
                    control.locator(f'[data-admin-select-value="{value}"]').click()
                    if value == 'PH':
                        page.locator('#adminScoreRows .empty-state').wait_for()
                    else:
                        page.locator('.admin-score-table').wait_for()
                assert page.locator('.admin-score-table [name=score]').input_value() == '13.2'
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
                assert saved['values']['E_score'] is None
                assert execution_input.get_attribute('placeholder') == 'E est. 8,200'
                assert page.locator('[data-save]').is_disabled()
                page.screenshot(path="/tmp/leverage-admin-result-editor.png", full_page=True)
                page.set_viewport_size({"width": 390, "height": 844})
                page.wait_for_timeout(100)
                assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
                assert page.locator('.admin-score-table-scroll').evaluate('el => el.scrollWidth > el.clientWidth')
                page.screenshot(path="/tmp/leverage-admin-result-editor-mobile.png", full_page=True)
                page.set_viewport_size({"width": 1440, "height": 1000})
                for category, expected_ids in [('junior and senior', ['1', '2']), ('junior', ['2']), ('senior', ['1'])]:
                    event['category'] = category
                    page.locator('[name=event_search]').fill('Admin ' + category)
                    with page.expect_response(lambda response: ':8000/results/?' in response.url) as loaded:
                        page.locator('#adminEventOptions button').first.click()
                    page.locator('.admin-score-table').wait_for()
                    query = parse_qs(urlparse(loaded.value.url).query)
                    assert query.get('category') == (None if category == 'junior and senior' else [category])
                    assert page.locator('[name=classification_category]').count() == 0
                    assert sorted(page.locator('[data-result-id]').evaluate_all('rows => rows.map(r => r.dataset.resultId)')) == expected_ids
                    if category == 'junior and senior':
                        junior_row = page.locator('[data-result-id="2"]')
                        junior_row.locator('[name=score]').fill('13.1')
                        junior_row.locator('[data-save]').click()
                        page.wait_for_timeout(200)
                        assert writes[-1]['path'] == '/results/2/scores'
                        assert set(json.loads(writes[-1]['body'])) == {'expected', 'values'}
                for days in [[1], [1, 2]]:
                    event_days[:] = days
                    page.locator('[name=event_search]').fill('Admin days ' + str(days))
                    with page.expect_response(lambda response: ':8000/results/?' in response.url):
                        page.locator('#adminEventOptions button').first.click()
                    page.locator('.admin-score-table').wait_for()
                    assert page.locator('[name=classification_day]').count() == (1 if len(days) > 1 else 0)
                day_control = page.locator('[name=classification_day]').locator('..')
                day_control.locator('summary').click()
                with page.expect_response(lambda response: ':8000/results/?' in response.url) as day_response:
                    day_control.locator('[data-admin-select-value="2"]').click()
                page.locator('[data-result-id="11"]').wait_for()
                assert parse_qs(urlparse(day_response.value.url).query)['day'] == ['2']
                assert page.locator('[data-result-id="1"]').count() == 0
                event_days[:] = [None]
                discipline_control = page.locator('[name=classification_discipline]').locator('..')
                discipline_control.locator('summary').click()
                discipline_control.locator('[data-admin-select-value="WAG"]').click()
                page.locator('#adminScoreRows .empty-state').wait_for()
                assert page.locator('[name=classification_apparatus]').locator('..').locator('[data-admin-select-value]').evaluate_all('options => options.map(o => o.dataset.adminSelectValue)') == ['VT', 'UB', 'BB', 'FX']
                full_classification_size[0] = 501
                page.locator('[name=event_search]').fill('Admin full classification')
                page.locator('#adminEventOptions button').first.click()
                page.wait_for_function("document.querySelectorAll('.admin-score-table tbody tr').length === 501")
                assert page.locator('[data-result-id="1500"]').count() == 1
                assert page.locator('#adminReloadClassification').count() == 0
                full_classification_size[0] = 0
                for apparatus, expected in [('PH', 'PH'), ('AA', 'FX'), ('VT AVG', 'VT')]:
                    page.evaluate('(apparatus) => { location.hash = "/admin/results?event_id=1&discipline=MAG&round=final&format=individual&day=&apparatus=" + encodeURIComponent(apparatus); }', apparatus)
                    page.wait_for_function('(expected) => document.querySelector("[name=classification_apparatus]")?.value === expected', arg=expected)
                    assert page.locator('[name=event_search]').input_value() == ''
                    assert page.locator('#adminSelectedEvent strong').inner_text() == 'Admin test event'
                    assert page.locator('[name=classification_round]').input_value() == 'final'
                    assert page.locator('[name=classification_format]').input_value() == 'individual'
                page.screenshot(path='/tmp/leverage-editor-selected-event.png', full_page=True)
                page.locator('#adminSelectedEvent button').click()
                assert page.locator('#adminClassificationEditor').inner_text() == ''
                assert page.locator('#adminSelectedEvent').inner_text() == ''
                assert page.locator('[name=event_search]').input_value() == ''
                page.locator('[name=event_search]').fill('Admin')
                page.locator('#adminEventOptions button').first.click()
                page.locator('#adminScoreRows tbody tr').first.wait_for()
                assert page.locator('#adminSelectedEvent strong').inner_text() == 'Admin test event'
            if tab == "users":
                assert page.locator('#adminUsersForm + #adminUsers').evaluate("el => getComputedStyle(el).borderTopWidth === '1px' && getComputedStyle(el).paddingTop === '4px'")
                assert page.locator('#adminUsers > .account-notification').first.evaluate("el => getComputedStyle(el).paddingTop === '6px'")
                search = page.locator('#adminUsersForm [name=search]')
                search.fill('REVI')
                page.wait_for_function("document.querySelectorAll('#adminUsers .account-notification').length === 1 && document.querySelector('#adminUsers').textContent.includes('review@example.test')")
                assert search.evaluate('el => el.checkValidity()')
                search.fill('not-found')
                page.locator('#adminUsers .empty-state').wait_for()
                search.fill('')
                page.wait_for_function("document.querySelectorAll('#adminUsers .account-notification').length === 2")
                assert page.locator('#adminUsersForm button[type=submit]').count() == 0
                search.press('Enter')
                page.locator('#adminUsers .account-notification').first.wait_for()
                assert 'review@example.test' in page.locator('#adminUsers').inner_text()
                assert page.locator('.admin-user-role-actions').first.is_visible()
                assert page.locator('[name=role_78], [data-role="78"], [data-delete-user="78"]').count() == 0
                assert 'Ultimo SUPER ADMIN attivo: ruolo non modificabile.' in page.locator('#adminUsers').inner_text()
                assert page.locator('#adminUsers .admin-user-role-actions > .admin-revision-meta').evaluate('el => { const s = getComputedStyle(el); const reference = getComputedStyle(document.querySelector("#adminUsers .account-notification-copy .admin-revision-meta")); return s.fontSize === "13px" && s.fontWeight === "400" && s.color === reference.color && s.lineHeight === "19.5px"; }')
                page.locator('[data-delete-user="77"]').click()
                assert 'review@example.test' in page.locator('dialog[open]').inner_text()
                assert 'sarà disabilitato' in page.locator('dialog[open]').inner_text()
                page.locator('dialog[open] [data-cancel]').click()
                assert page.locator('[data-delete-user="77"]').is_visible()
                page.locator('[data-delete-user="77"]').click()
                page.locator('dialog[open] [data-confirm]').click()
                page.locator('#adminUsers .is-success').wait_for()
                assert page.locator('#adminUsers .is-success').inner_text() == 'Utente eliminato'
                assert page.locator('[data-role="77"], [data-delete-user="77"]').count() == 0
            if tab == "audit":
                assert page.locator('#adminAuditForm + #adminAudit').evaluate("el => getComputedStyle(el).borderTopWidth === '1px' && getComputedStyle(el).paddingTop === '4px'")
                assert page.locator('#adminAudit > .admin-audit-record').first.evaluate("el => getComputedStyle(el).paddingTop === '6px'")
                assert page.locator('#adminAuditForm [name=entity_id]').locator('..').inner_text() == 'Leverage ID'
                assert page.evaluate('''async () => {
                    const { createAdminReport } = await import('/admin-reports.js?v=20261006');
                    const escape = value => String(value).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');
                    for (const language of ['en', 'it', 'es', 'fr']) {
                        const render = createAdminReport({language, esc: escape, text: key => key});
                        const node = document.createElement('div');
                        node.innerHTML = render({before: {id: 1, country: 'ITA', value: null}, after: {id: 1, country: 'FRA', value: '<script>bad</script>'}});
                        if (node.querySelectorAll('.admin-audit-side').length !== 2) return false;
                        if (node.querySelector('script') || node.querySelector('.admin-report-disclosure')) return false;
                        node.innerHTML = render({before: null, after: {id: 1, is_deleted: false, D_score: 5.3}});
                        if (node.querySelectorAll('.admin-audit-side').length !== 2) return false;
                        node.innerHTML = render({before: {source_athlete: {id: 1, first_name: 'Ada', last_name: 'Test'}, target_athlete: {id: 2, first_name: 'Ada', last_name: 'Test'}, source_result_ids: [10], target_result_ids_before: [11], reversal_state: {results: [{id: 10, athlete_id: 1}, {id: 11, athlete_id: 2}]}}, after: {source_athlete: {id: 1, first_name: 'Ada', last_name: 'Test', is_deleted: true}, target_athlete: {id: 2, first_name: 'Ada', last_name: 'Test'}, moved_results: 1, reversal_state: {results: [{id: 10, athlete_id: 2}, {id: 11, athlete_id: 2}]}}});
                        if (node.querySelectorAll('.admin-audit-entity').length !== 4 || node.textContent.includes('reversal') || node.querySelector('details')) return false;
                        node.innerHTML = render({warnings: ['Test'], source_athlete: {id: 1, last_name: 'Test'}});
                        if (node.querySelectorAll('.admin-report-disclosure').length !== 2) return false;
                        node.innerHTML = render({can_merge: false, source_athlete: {id: 1, first_name: 'Ada', last_name: 'Test'}, target_athlete: {id: 2, first_name: 'Ada', last_name: 'Test'}, source_result_count: 12, target_result_count: 24, blocking_reasons: ['Cannot merge <script>bad</script>'], result_conflicts: [{source_result_id: 10, target_result_id: 11}], preview_token: 'SECRET'});
                        if (node.querySelectorAll('.admin-audit-side').length !== 2 || node.querySelector('script') || node.textContent.includes('SECRET')) return false;
                        if (node.querySelector('.is-error').closest('details') || !node.querySelector('.is-error').textContent.includes('Cannot merge')) return false;
                        if (node.querySelector('.admin-audit-entity strong').textContent !== 'Test Ada') return false;
                    }
                    return true;
                }''')
                assert page.locator('#adminAuditForm button[type=submit]').count() == 0
                with page.expect_response(lambda response: '/admin/audit-logs?' in response.url and 'entity_id=123' in response.url):
                    page.locator('#adminAuditForm [name=entity_id]').fill('123')
                with page.expect_response(lambda response: '/admin/audit-logs?' in response.url and 'review_status=pending' in response.url):
                    page.locator('#adminAuditForm [name=review_status]').evaluate("el => { el.value = 'pending'; el.dispatchEvent(new Event('change', {bubbles: true})); }")
                page.locator('#adminAudit .account-notification').first.wait_for()
                authors = page.locator('[data-audit-author]').all_text_contents()
                assert authors[0] == 'Autore: review@example.test · ID 77 · Ruolo attuale: ADMIN'
                assert 'super@example.test' in authors[1] and 'SUPER ADMIN' in authors[1]
                assert authors[2] == 'Autore: ID 77'
                compare_button = page.locator('#adminAudit [data-audit-compare]').first
                assert compare_button.get_attribute('aria-expanded') == 'false'
                title_box = page.locator('#adminAudit .admin-audit-record .account-notification-copy').first.bounding_box()
                button_box = compare_button.bounding_box()
                assert button_box['x'] > title_box['x'] + title_box['width']
                compare_button.click()
                assert compare_button.get_attribute('aria-expanded') == 'true'
                assert page.locator('#auditDetails_91 [name=note_91]').is_visible()
                comparison = page.locator('#adminAudit .admin-audit-comparison').first
                assert comparison.is_visible()
                assert comparison.locator('dd').all_inner_texts() == ['ITA', 'FRA']
                assert comparison.locator('h3').all_inner_texts() == ['Prima', 'Dopo']
                before_box = comparison.locator('.admin-audit-side').nth(0).bounding_box()
                after_box = comparison.locator('.admin-audit-side').nth(1).bounding_box()
                assert before_box['x'] < after_box['x'] and abs(before_box['y'] - after_box['y']) < 1
                assert page.locator('[data-action=approve].admin-accept-button').count() == 3
                assert page.locator('[data-action=revert].filter-clear-button').count() == 3
                undo_merge = page.locator('[data-audit="93"][data-action=revert]')
                assert undo_merge.inner_text() == 'Annulla unione'
                undo_merge.click()
                assert page.locator('dialog[open] h2').inner_text() == 'Annulla unione'
                page.locator('dialog[open] [data-cancel]').click()
                undo = page.locator('[data-audit="92"][data-action=revert]')
                assert undo.inner_text() == 'Annulla inserimento'
                undo.click()
                assert page.locator('dialog[open] h2').inner_text() == 'Annulla inserimento'
                page.locator('dialog[open] [data-cancel]').click()
                assert page.locator('#adminRestoreForm').count() == 0
                page.set_viewport_size({"width": 390, "height": 844})
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                page.screenshot(path='/tmp/leverage-super-audit-mobile.png', full_page=True)
                page.set_viewport_size({"width": 1440, "height": 1000})
                page.screenshot(path='/tmp/leverage-super-audit-details.png', full_page=True)
                page.locator('[data-audit="91"][data-action=approve]').click()
                page.locator('dialog[open] [data-confirm]').click()
                notice = page.locator('#adminAudit > article').first.locator('.account-notification-actions .is-success')
                notice.wait_for()
                assert notice.bounding_box()['height'] == 36
                assert notice.evaluate('el => getComputedStyle(el).fontSize') == '14px'
                assert notice.evaluate('el => getComputedStyle(el).backgroundColor') == 'rgba(0, 0, 0, 0)'
                assert notice.evaluate('el => getComputedStyle(el).color === getComputedStyle(el).borderTopColor')
                assert page.locator('[data-audit="91"]').count() == 0
                assert page.locator('#adminFeedback').inner_text() == ''
                assert page.locator('#adminAudit > article').count() == 3
                assert page.locator('#adminAudit [name=note_91]').is_disabled()
            if tab == "statistics":
                assert page.locator('[data-admin-tab]').evaluate_all('tabs => tabs.map(tab => tab.dataset.adminTab)') == ['overview', 'statistics', 'users', 'audit']
                assert page.locator('[data-admin-tab=statistics]').inner_text() == 'Statistiche Sito'
                assert page.locator('#adminStats .admin-data-group').count() == 2
                assert page.locator('#adminStats .admin-data-group dl > div').count() == 13
                assert page.locator('#adminStats .admin-data-group').first.locator('dt').all_inner_texts()[-1] == 'Altre attività'
                assert 'Attività negli ultimi 30 giorni' not in page.locator('#adminStats').inner_text()
                assert '42' in page.locator('#adminStats').inner_text()
                assert page.locator('#adminStats .empty-state, #adminStats .admin-stats-top').count() == 0
                assert page.locator('#adminStatsForm [name=start_date], #adminStatsForm [name=end_date]').count() == 0
                assert page.locator('#adminStatsForm [name=days]').input_value() == '30'
                assert page.locator('#adminStatsForm button[type=submit]').count() == 0
                for days in ['7', '90', '0', '30']:
                    with page.expect_response(lambda response: '/site-analytics/admin/summary?' in response.url and f'days={days}' in response.url):
                        page.locator('#adminStatsForm [name=days]').evaluate('(el, value) => { el.value = value; el.dispatchEvent(new Event("change", {bubbles: true})); }', days)
                    page.wait_for_timeout(100)
                    assert page.locator('#adminStatsForm [name=days]').input_value() == days
                page.screenshot(path='/tmp/leverage-admin-statistics-desktop.png', full_page=True)
                page.set_viewport_size({"width": 390, "height": 844})
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                page.screenshot(path='/tmp/leverage-admin-statistics-mobile.png', full_page=True)
                page.set_viewport_size({"width": 1440, "height": 1000})
            if tab == "review":
                assert page.locator('[data-admin-tab="review"]').inner_text() == 'Revisione Duplicati'
                assert page.locator('#adminWorldGymnasticsScan').count() == 0
                assert page.locator('.admin-revisions > .admin-tool-block').count() == 2
                page.locator('#adminEntityReviews .admin-identity-pair').wait_for()
                first_pair = page.locator('[data-pair-recap]').bounding_box()
                review_toggle = page.locator('.admin-review-toggle').bounding_box()
                assert abs(first_pair['y'] - review_toggle['y'] - review_toggle['height'] - 16) < 1, (first_pair, review_toggle)
                assert page.locator('#adminEntityReviews [data-pair-feedback]').is_hidden()
                assert page.locator('[data-pair-recap] dd').all_text_contents() == ['1', '1', '0']
                assert page.locator('[data-pair-recap]').evaluate('el => getComputedStyle(el).borderBottomWidth') == '1px'
                assert page.locator('[data-pairs-more]').evaluate('''button => {
                    button.hidden = false;
                    const box = button.getBoundingClientRect();
                    const parent = button.parentElement.getBoundingClientRect();
                    button.hidden = true;
                    return box.width <= 240 && Math.abs(box.left + box.width / 2 - (parent.left + parent.width / 2)) < 1;
                }''')
                assert page.locator('#adminEntityReviews h2').count() == 0
                assert page.locator('[data-pair-note]').evaluate('el => el === el.parentElement.lastElementChild')
                assert page.locator('#adminEntityReviews .admin-review-compatibility').inner_text() == 'Compatibilità: 98%'
                assert 'Nomi simili' not in page.locator('#adminEntityReviews [data-pairs]').inner_text()
                assert page.locator('#adminEntityReviews .admin-review-compatibility').bounding_box()['x'] < page.locator('[data-pair-compare]').bounding_box()['x']
                page.locator('[data-pair-compare]').click()
                page.locator('.admin-pair-warning').wait_for()
                assert 'Nomi simili' in page.locator('[data-pair-details]').inner_text()
                compare = page.locator('[data-pair-compare]')
                assert compare.get_attribute('aria-expanded') == 'true'
                compare.hover()
                page.wait_for_timeout(200)
                assert compare.evaluate('el => getComputedStyle(el).backgroundColor') == 'rgb(25, 23, 71)'
                compare.click()
                assert compare.get_attribute('aria-expanded') == 'false'
                assert page.locator('[data-pair-details]').is_hidden()
                page.wait_for_timeout(200)
                assert compare.evaluate('el => getComputedStyle(el).backgroundColor') != 'rgb(25, 23, 71)'
                compare.click()
                assert compare.get_attribute('aria-expanded') == 'true'
                assert 'Valuta unione' in page.locator('#adminEntityReviews').inner_text()
                page.locator('[data-review-entity="event"]').click()
                page.locator('#adminEntityReviews[data-review-kind="event"] .admin-identity-pair').wait_for()
                assert page.locator('#adminEntityReviews h2').count() == 0
                assert page.locator('[data-review-entity]').all_text_contents() == ['Atleti', 'Eventi', 'Risultati']
                page.locator('[data-review-entity="result"]').click()
                assert page.locator('#adminResultReviews').is_visible()
                assert page.locator('[data-result-recap] dd').all_text_contents() == ['0', '0']
                assert page.locator('[data-result-recap]').evaluate('el => getComputedStyle(el).borderBottomWidth') == '1px'
                assert page.locator('#adminResultReviews h2').count() == 0
                assert page.locator('#adminEntityReviews').is_hidden()
                page.wait_for_timeout(700)
                thumb = page.locator('.admin-review-toggle .segmented-thumb').bounding_box()
                selected = page.locator('[data-review-entity="result"]').bounding_box()
                assert abs(thumb['x'] - selected['x']) < 1
                assert abs(thumb['width'] - selected['width']) < 1
                page.screenshot(path='/tmp/leverage-result-reviews.png', full_page=True)
                page.locator('[data-admin-tab="world-gymnastics"]').click()
                page.locator('[data-scan-job="51"]').wait_for()
                wg_recap = page.locator('[data-scan-status]').bounding_box()
                wg_toggle = page.locator('[data-review-entity="athlete"]').locator('..').bounding_box()
                assert abs(wg_recap['y'] - wg_toggle['y'] - wg_toggle['height'] - 16) < 1, (wg_recap, wg_toggle)
                assert page.locator('[data-scan-more]').evaluate('''button => {
                    button.hidden = false;
                    const box = button.getBoundingClientRect();
                    const parent = button.parentElement.getBoundingClientRect();
                    button.hidden = true;
                    return box.width <= 240 && Math.abs(box.left + box.width / 2 - (parent.left + parent.width / 2)) < 1;
                }''')
                assert page.locator('[data-review-entity]').all_text_contents() == ['Atleti', 'Eventi']
                assert page.locator('#adminEntityReviews, #adminResultReviews').count() == 0
                assert page.locator('.admin-revisions > .admin-tool-block > .section-header').count() == 0
                assert page.locator('[data-scan-action="start"]').inner_text() == 'Avvia scansione atleti'
                assert page.locator('[data-scan-refresh]').count() == 0
                assert page.locator('[data-scan-job="51"] .admin-review-compatibility').inner_text() == 'Compatibilità: 95%'
                assert page.locator('[data-scan-job="51"] .admin-identity-pair-grid .admin-identity-entity').count() == 2
                assert page.locator('[data-scan-job="51"] .admin-wg-actions').inner_text() == 'Compatibilità: 95%\nRifiuta\nVai all’atleta'
                assert page.locator('[data-scan-job="51"] .admin-review-compatibility').bounding_box()['x'] < page.locator('[data-scan-job="51"] [data-scan-dismiss]').bounding_box()['x']
                assert 'wg_scan_job=51' in page.locator('[data-scan-job="51"] .admin-wg-actions a').get_attribute('href')
                page.locator('[data-wg-review-group] > summary').click()
                assert page.locator('.admin-revisions .account-notification').count() == 1
                assert page.locator('[data-accept="13"], [data-accept="14"]').count() == 0
                assert page.locator('[data-accept]').evaluate('el => el.classList.contains("admin-accept-button")')
                page.locator('[data-accept]').click()
                page.locator('#adminRevisionSuggestions').wait_for(state='hidden')
                assert page.locator('#adminRevisionSuggestions .empty-state').count() == 0
                assert page.locator('[data-scan-job="51"]').is_visible()
                assert json.loads(writes[-1]['body']) == {'value': '2001'}
                page.locator('[data-review-entity="event"]').click()
                page.locator('[data-scan-job="52"]').wait_for()
                assert page.locator('[data-scan-action="start"]').inner_text() == 'Avvia scansione eventi'
                assert page.locator('[data-scan-job="52"] .admin-wg-actions').inner_text() == 'Compatibilità: 90%\nRifiuta\nVai all’evento'
                assert '7' in page.locator('[data-scan-status]').inner_text()
                assert page.locator('[data-scan-note]').evaluate('el => el === el.parentElement.lastElementChild && el.previousElementSibling.id === "adminRevisionSuggestions"')
                assert page.locator('[data-review-entity="event"]').get_attribute('aria-pressed') == 'true'
                assert page.locator('[data-scan-job="51"]').count() == 0
                assert page.locator('#adminRevisionSuggestions').is_hidden()
                assert page.locator('#adminRevisionSuggestions .empty-state').count() == 0
                page.locator('[data-review-entity="athlete"]').click()
                page.locator('[data-scan-job="51"]').wait_for()
                assert page.locator('[data-scan-job="52"]').count() == 0
                assert not any(write['path'] == '/world-gymnastics/scan/control' for write in writes)
                assert page.locator('[data-scan-status]').evaluate('el => getComputedStyle(el).gridTemplateColumns.split(" ").length') == 4
                assert page.locator('[data-scan-status]').evaluate("el => getComputedStyle(el).borderTopWidth === '0px' && getComputedStyle(el).borderBottomWidth === '1px'")
                controls = page.locator('[data-scan-controls]').bounding_box()
                toggle = page.locator('[data-review-entity="athlete"]').locator('..').bounding_box()
                assert controls['x'] >= toggle['x'] + toggle['width']
                assert abs(controls['y'] + controls['height'] / 2 - toggle['y'] - toggle['height'] / 2) < 2
                counters = page.locator('[data-scan-status]').bounding_box()
                note = page.locator('[data-scan-note]').bounding_box()
                assert abs(counters['y'] - controls['y'] - controls['height'] - 16) < 1
                assert note['y'] - counters['y'] - counters['height'] >= 17
                page.screenshot(path="/tmp/leverage-admin-revisions.png", full_page=True)
                page.set_viewport_size({"width": 390, "height": 844})
                page.wait_for_timeout(100)
                assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
                assert page.locator('[data-scan-status]').evaluate('el => getComputedStyle(el).gridTemplateColumns.split(" ").length') == 2
                actions = page.locator('[data-scan-job="51"] .admin-wg-actions').bounding_box()
                assert actions['x'] + actions['width'] <= 390
                page.screenshot(path="/tmp/leverage-wg-scan-mobile.png", full_page=True)
                page.set_viewport_size({"width": 1440, "height": 1000})
                page.locator('[data-scan-action="start"]').click()
                page.wait_for_timeout(200)
                assert json.loads(writes[-1]['body']) == {'action': 'start', 'entity_type': 'athlete'}
                page.locator('[data-review-entity="event"]').click()
                page.locator('[data-scan-job="52"]').wait_for()
                page.locator('[data-scan-action="start"]').click()
                page.wait_for_timeout(200)
                assert json.loads(writes[-1]['body']) == {'action': 'start', 'entity_type': 'event'}
                page.locator('[data-scan-job="52"] [data-scan-dismiss]').click()
                page.locator('[data-scan-job="52"]').wait_for(state='detached')
                assert writes[-1]['path'] == '/world-gymnastics/scan/matches/52/dismiss'
                page.locator('[data-admin-tab="review"]').click()
                page.locator('#adminEntityReviews .admin-identity-pair').wait_for()
                page.locator('[data-review-entity="event"]').click()
                page.locator('#adminEntityReviews[data-review-kind="event"] .admin-identity-pair').wait_for()
                page.locator('[data-pair-separate]').click()
                page.locator('#adminEntityReviews .empty-state').wait_for()
                assert page.locator('[data-pair-recap] dd').all_text_contents() == ['0', '0', '0']
                assert writes[-1]['path'] == '/admin/entity-duplicates/event/1/2/keep-separate'
                page.evaluate("location.hash = '/admin/merge?entity_type=event&source=2&target=1'")
                page.locator('#adminMergeForm').wait_for()
                assert page.locator('#adminMergeForm [name=source]').input_value() == '2'
                assert page.locator('#adminMergeForm [name=target]').input_value() == '1'
            if tab == "imports":
                previous_writes = len(writes)
                page.locator('#adminImportForm button[type=submit]').click()
                assert page.locator('#adminImportFormValidation').inner_text() == 'Completa i campi obbligatori.'
                assert page.locator('#adminImportFile').get_attribute('aria-invalid') == 'true'
                assert len(writes) == previous_writes
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
        athlete_overview = page.locator('.admin-data-group').first
        assert athlete_overview.locator('dt').all_inner_texts()[:4] == ['Totali', 'Verificati World Gymnastics', 'Scansionati World Gymnastics', 'Possibili duplicati']
        assert 'Da completare' not in page.locator('.admin-data-overview').inner_text()
        assert athlete_overview.locator('[data-overview-count="athletes.possible_duplicates"]').inner_text() == '12'
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
        assert page.locator('.admin-activity-details').count() == 0
        assert page.locator('#adminWorkspace a[href="#/super-admin/audit"]').count() == 0
        assert page.locator('.admin-data-total').count() == 1
        assert page.locator('#adminActivityPeriod button[type=submit]').count() == 0
        assert page.locator('#adminActivityPeriod').bounding_box()['y'] < page.locator('.admin-data-overview').bounding_box()['y']
        assert page.locator('#adminActivityPeriod + .admin-data-overview').evaluate("el => getComputedStyle(el).borderTopWidth === '1px' && getComputedStyle(el).paddingTop === '16px'")
        assert page.locator('.admin-activity-overview .admin-data-total').count() == 1
        assert page.locator('.admin-activity-overview').inner_text().count('Totali') == 0
        assert "il ruolo SUPER ADMIN dell'autore non approva automaticamente" in page.locator('.admin-data-note').inner_text()
        page.locator('#adminActivityPeriod input[name="days"]').evaluate("node => { node.value = '7'; node.dispatchEvent(new Event('change', {bubbles: true})); }")
        page.wait_for_timeout(300)
        assert page.locator('#adminActivityPeriod input[name="days"]').input_value() == '7'
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
        assert page.locator('#adminNotificationsToggle').count() == 0
        page.evaluate("location.hash = '#/super-admin/notifications'")
        page.wait_for_url('**/#/account?section=notifications')
        assert page.locator('#accountNotifications').is_visible()
        page.screenshot(path="/tmp/leverage-admin-mobile.png", full_page=True)
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), "Horizontal overflow"
        page.evaluate("location.hash = '#/super-admin/audit'")
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
