"""Read-only check of combined event categories and the vertical selector."""
from urllib.parse import parse_qs, urlparse
from pathlib import Path

from playwright.sync_api import sync_playwright


def main():
    errors = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        page.add_init_script("localStorage.setItem('leverage.language', 'it');")
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.route("**:8000/**", lambda route: route.continue_() if route.request.method == "GET" else route.fulfill(json={}))
        with page.expect_response(lambda response: '/events/1/ranking-view?' in response.url) as first:
            page.goto('http://127.0.0.1:5173/?v=event-category-20261001#/events/1')
        payload = first.value.json()
        assert 'category' not in parse_qs(urlparse(first.value.url).query)
        assert {row['category'] for row in payload['results']} == {'junior', 'senior'}
        control = page.locator('[data-event-classification-control=category]')
        selected = control.locator('[aria-checked=true]')
        assert selected.inner_text() == 'Junior e Senior'
        assert page.locator('.event-score-editor-link').count() == 0
        assert page.locator('.event-classification-primary-row [data-event-classification-control=category]').count() == 0
        for value in ['senior', 'junior', 'junior and senior']:
            with page.expect_response(lambda response: '/events/1/ranking-view?' in response.url) as response:
                control.locator(f'[data-event-classification-value="{value}"]').click()
            data = response.value.json()
            query = parse_qs(urlparse(response.value.url).query)
            assert query.get('category') == (None if value == 'junior and senior' else [value])
            assert data['total_results'] > 0
            page.wait_for_timeout(350)
            selected_box = selected.bounding_box()
            thumb_box = control.locator('.segmented-thumb').bounding_box()
            assert abs(selected_box['y'] - thumb_box['y']) < 1
            assert abs(selected_box['height'] - thumb_box['height']) < 1
        left = page.locator('.event-result-groups').bounding_box()
        right = control.bounding_box()
        assert right['x'] > left['x'] + left['width']
        assert abs(right['y'] - left['y']) < 1
        assert abs(right['height'] - left['height']) < 1
        page.screenshot(path='/tmp/leverage-event-category.png', full_page=True)
        page.set_viewport_size({'width': 390, 'height': 844})
        page.wait_for_timeout(500)
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.screenshot(path='/tmp/leverage-event-category-mobile.png', full_page=True)
        with page.expect_response(lambda response: '/events/1/ranking-view?' in response.url) as direct:
            page.goto('http://127.0.0.1:5173/?v=event-category-20261001#/events/1?classification_category=junior')
        assert parse_qs(urlparse(direct.value.url).query)['category'] == ['junior']
        source = (Path(__file__).resolve().parents[1] / 'frontend/app.js').read_text()
        renderer = source[source.index('function renderEventScoreEditorLink()'):source.index('function renderEventResultGroups(')]
        assert page.evaluate('''(source) => {
            const render = new Function('state', 'isAdminUser', 'selectedEventClassification', 'escapeHtml', 'adminToolsIcon', source + '; return renderEventScoreEditorLink();');
            const group = {discipline:'WAG', format:'apparatus', round:'qualification', apparatus:'VT AVG', day:2};
            for (const role of ['user', 'admin', 'super_admin', null]) {
                const html = render({language:'it', eventDetail:{eventId:1}}, () => ['admin', 'super_admin'].includes(role), () => group, String, () => '<svg></svg>');
                if (role === 'user' || role === null) { if (html) return false; continue; }
                const node = document.createElement('div'); node.innerHTML = html;
                const a = node.querySelector('a');
                const params = new URLSearchParams(a.hash.split('?')[1]);
                if (params.get('event_id') !== '1' || params.get('apparatus') !== 'VT AVG' || params.get('day') !== '2' || params.get('discipline') !== 'WAG') return false;
            }
            return true;
        }''', renderer)
        assert not errors, errors
        browser.close()
    print('Combined categories, category variants, vertical thumb and responsive layout: passed')


if __name__ == '__main__':
    main()
