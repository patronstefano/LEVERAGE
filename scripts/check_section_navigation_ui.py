"""Regression checks using the actual frontend route-memory functions."""
from pathlib import Path

from playwright.sync_api import sync_playwright


def main():
    source = (Path(__file__).resolve().parents[1] / "frontend/app.js").read_text()
    routes = source[source.index("const SECTION_BASE_ROUTES ="):source.index("const state =")]
    navigation = source[source.index("function persistSectionRoutes("):source.index("function syncNavIndicator(")]
    event_link = source[source.index('function eventSectionProfileHref('):source.index('function syncEventSearchRoute(')]
    event_back = source[source.index('function eventDetailBackDestination('):source.index('async function renderAthleteDetail(')]
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("http://127.0.0.1:5173/athlete-field-options.js")
        page.set_content('<a class="nav-trigger" data-section-nav="athletes">Athletes</a><a class="nav-trigger" data-section-nav="events">Events</a>')
        page.add_script_tag(content='const SECTION_ROUTE_MEMORY_KEY = "test.sectionRoutes";' + routes
                            + 'const state = {route:"/",sectionRoutes:initialSectionRoutes()};' + navigation)
        page.add_script_tag(content='const t = key => key; const adminLabel = (language, key) => key;' + event_link + event_back)
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
            for (const listRoute of ['/events', '/events?search=World%20Cup%20Paris%202026', '/events?search=Junior%20%26%20Senior']) {
                state.route = listRoute;
                const href = eventSectionProfileHref(42);
                state.route = href.slice(1);
                rememberCurrentSectionRoute();
                state.route = '/athletes';
                check(sectionNavigationRoute('events') === href.slice(1), 'Preserve event detail on section switch');
                state.route = href.slice(1);
                check(eventDetailBackDestination().href === '#' + listRoute, 'Restore exact event search');
            }
            for (const [route, expected] of [
                ['/events/42', '#/events'],
                ['/events/42?from=events&return_to=%2Fathletes', '#/events'],
                ['/events/42?from=search&return_to=%2Fsearch%3Fq%3DParis', '#/search?q=Paris'],
                ['/events/42?from=admin&return_to=%2Fadmin%2Fresults', '#/admin/results']
            ]) {
                state.route = route;
                check(eventDetailBackDestination().href === expected, 'Preserve other event origins');
            }
        }""")
        browser.close()
    print('Section navigation: admin isolation, stale memory recovery and public contexts passed')


if __name__ == '__main__':
    main()
