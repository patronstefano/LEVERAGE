"""Exercise the actual selector render/sync functions without database writes."""
from pathlib import Path

from playwright.sync_api import sync_playwright


def main():
    source = (Path(__file__).resolve().parents[1] / "frontend/app.js").read_text()
    render = source[source.index("function renderAdminSelectControl("):source.index("function closeAdminSelectControls(")]
    sync = source[source.index("function syncAdminFormValue("):source.index("function updateAthleteProfileSummary(")]
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("http://127.0.0.1:5173/athlete-field-options.js")
        page.set_content('<form id="testForm"></form>')
        page.add_script_tag(content="function escapeHtml(value) { const el = document.createElement('span'); el.textContent = String(value); return el.innerHTML.replaceAll('\"', '&quot;'); }" + render + sync)
        page.evaluate("""async () => {
            const { athleteFieldOptions } = await import('/athlete-field-options.js?v=20260930');
            const form = document.getElementById('testForm');
            form.innerHTML = renderAdminSelectControl('country', 'Country', 'ITA', athleteFieldOptions('country', 'ITA'))
                + renderAdminSelectControl('birth_year', 'Year', '2001', athleteFieldOptions('birth_year', 2001));
            window.applyOfficialValues = (country, year) => {
                syncAdminFormValue(form, 'country', country);
                syncAdminFormValue(form, 'birth_year', year);
            };
            window.applyOfficialValues('AIN', 1998);
        }""")
        assert page.locator('[name=country]').input_value() == 'AIN'
        assert page.locator('[data-admin-select-label]').all_text_contents() == ['AIN', '1998']
        assert page.locator('[aria-selected=true]').all_text_contents() == ['AIN', '1998']
        page.evaluate("applyOfficialValues('CRO', 2000)")
        page.locator('summary').first.click()
        page.locator('[data-admin-select-value=AIN]').click()
        assert page.locator('[name=country]').input_value() == 'AIN'
        assert page.evaluate("Object.fromEntries(new FormData(document.getElementById('testForm')))") == {'country': 'AIN', 'birth_year': '2000'}
        page.evaluate("applyOfficialValues(null, null)")
        assert page.locator('[data-admin-select-label]').all_text_contents() == ['—', '—']
        browser.close()
    print('Athlete selectors: official values, new country codes, selection and null clearing passed')


if __name__ == '__main__':
    main()
