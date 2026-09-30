"""Regression checks using the actual frontend route-memory functions."""
from pathlib import Path

from playwright.sync_api import sync_playwright


def main():
    source = (Path(__file__).resolve().parents[1] / "frontend/app.js").read_text()
    routes = source[source.index("const SECTION_BASE_ROUTES ="):source.index("const state =")]
    navigation = source[source.index("function persistSectionRoutes("):source.index("function syncNavIndicator(")]
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("http://127.0.0.1:5173/athlete-field-options.js")
        page.set_content('<a class="nav-trigger" data-section-nav="athletes">Athletes</a><a class="nav-trigger" data-section-nav="events">Events</a>')
        page.add_script_tag(content='const SECTION_ROUTE_MEMORY_KEY = "test.sectionRoutes";' + routes
                            + 'const state = {route:"/",sectionRoutes:initialSectionRoutes()};' + navigation)
        page.evaluate("""() => {
            const check = (value, message) => { if (!value) throw new Error(message); };
            for (const section of ['athletes', 'events']) {
                const detail = `/${section}/1?from=admin&admin_tools=1&return_to=%2Fadmin%2Fentities`;
                sessionStorage.setItem(SECTION_ROUTE_MEMORY_KEY, JSON.stringify({[section]:detail}));
                state.sectionRoutes = initialSectionRoutes();
                check(state.sectionRoutes[section] === `/${section}`, 'Discard stale admin memory');
                for (const previous of [`/${section}`, `/${section}/2`]) {
                    state.sectionRoutes[section] = previous;
                    state.route = detail;
                    rememberCurrentSectionRoute();
                    syncSectionNavLinks();
                    check(activeRouteSection(detail) === '', 'Admin details are not public sections');
                    check(state.sectionRoutes[section] === previous, 'Preserve public section memory');
                    check(sectionNavigationRoute(section) === previous, 'Return to public view');
                    check(document.querySelector(`[data-section-nav=${section}]`).getAttribute('href') === '#' + previous, 'Topbar target');
                }
            }
            for (const [route, section] of [
                ['/athletes/2?from=athletes', 'athletes'],
                ['/athletes/2?from=ranking', 'rankings'],
                ['/athletes/2?from=classification', 'events'],
                ['/athletes/2?from=search', 'home'],
                ['/events/2?from=search', 'home'],
                ['/events/2', 'events']
            ]) {
                state.route = route;
                rememberCurrentSectionRoute();
                check(state.sectionRoutes[section] === route, 'Preserve contextual public details');
            }
            sessionStorage.removeItem(SECTION_ROUTE_MEMORY_KEY);
        }""")
        browser.close()
    print('Section navigation: admin isolation, stale memory recovery and public contexts passed')


if __name__ == '__main__':
    main()
