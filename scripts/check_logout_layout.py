"""Check signed-out layouts without contacting the application database."""

from playwright.sync_api import sync_playwright


with sync_playwright() as p:
    browser = p.chromium.launch()
    for width, height in [(1440, 900), (1280, 720), (390, 844)]:
        page = browser.new_page(viewport={"width": width, "height": height})
        page.route("**:8000/**", lambda route: route.fulfill(status=401, json={"detail": "Not authenticated"}))
        for section in ["account", "admin"]:
            page.goto(f"http://127.0.0.1:5173/#/{section}")
            page.locator(".auth-brand-welcome").wait_for()
            page.wait_for_timeout(1600)
            brand = page.locator(".auth-brand-welcome").bounding_box()
            actions = page.locator(".auth-required-actions").bounding_box()
            header = page.locator(".topbar").bounding_box()
            footer = page.locator(".footer").bounding_box()
            center = (brand["y"] + actions["y"] + actions["height"]) / 2
            available_center = (header["y"] + header["height"] + footer["y"]) / 2
            assert abs(center - available_center) < 2, (section, width, center, available_center)
            assert footer["y"] + footer["height"] <= height + 1
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
            page.screenshot(path=f"/tmp/leverage-logout-{section}-{width}.png")
        page.close()
    browser.close()
print("USER/ADMIN signed-out layouts centered on desktop and mobile")
