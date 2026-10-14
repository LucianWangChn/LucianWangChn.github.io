"""Browser acceptance checks. Run with a local HTTP server on port 8765.

Requires Python Playwright and an installed Chromium browser. Artifacts are
written to ignored .qa/; these tools are not required by the website itself.
"""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.qa'
OUT.mkdir(exist_ok=True)
URL = os.environ.get('HOMEPAGE_URL', 'http://127.0.0.1:8765/').rstrip('/') + '/'
results = []


def check(name, condition):
    if not condition:
        raise AssertionError(name)
    results.append(name)


def no_overflow(page):
    return page.evaluate('document.documentElement.scrollWidth <= innerWidth')


def settle(page):
    page.wait_for_timeout(900)


with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context(viewport={'width': 1440, 'height': 1000}, device_scale_factor=1)
    page = context.new_page()
    errors = []
    failures = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('response', lambda response: failures.append(response.url) if response.status >= 400 else None)
    page.goto(URL, wait_until='networkidle')
    settle(page)
    check('desktop fits viewport', no_overflow(page))
    check('five existing projects preserved', page.locator('.project').count() == 5)
    check('academic metrics preserved', '2/230' in page.locator('#education').inner_text() and '613' in page.locator('#education').inner_text())
    check('motion starts enabled', page.locator('.motion-toggle').get_attribute('aria-pressed') == 'true')
    page.screenshot(path=str(OUT / 'desktop-hero.png'))
    page.mouse.move(1000, 300)
    page.wait_for_timeout(100)
    check('portrait follows mouse', bool(page.locator('.portrait').evaluate("e => e.style.getPropertyValue('--portrait-x')")))
    page.locator('.site-header a[href="#research"]').click()
    settle(page)
    check('navigation follows section', page.locator('.site-header a[aria-current]').get_attribute('href') == '#research')
    check('header changes after hero', 'is-light' in page.locator('.site-header').get_attribute('class'))
    check('reading progress updates', page.locator('.reading-progress').evaluate("e => e.style.transform !== 'scaleX(0)'"))
    card = page.locator('.research-grid article').first
    card.hover(position={'x': 35, 'y': 50})
    page.wait_for_timeout(100)
    check('research card reacts to mouse', card.evaluate("e => getComputedStyle(e).transform.startsWith('matrix3d')"))
    page.screenshot(path=str(OUT / 'desktop-research.png'))
    page.locator('.site-header a[href="#projects"]').click()
    settle(page)
    page.locator('.project').first.locator('summary').click()
    check('project details expand', page.locator('.project').first.locator('details').get_attribute('open') is not None)
    page.screenshot(path=str(OUT / 'desktop-projects.png'))
    page.locator('.motion-toggle').click()
    check('motion can be disabled', page.locator('.motion-toggle').get_attribute('aria-pressed') == 'false')
    page.reload(wait_until='networkidle')
    check('motion preference survives reload', page.locator('.motion-toggle').get_attribute('aria-pressed') == 'false')
    check('disabled motion keeps content visible', page.locator('#honors .section-heading').evaluate("e => getComputedStyle(e).opacity === '1'"))
    page.locator('.motion-toggle').click()
    page.emulate_media(reduced_motion='reduce')
    settle(page)
    check('system reduced motion honored live', page.locator('.motion-toggle').get_attribute('aria-pressed') == 'false')
    check('system reduced motion control explains preference', page.locator('.motion-toggle').is_disabled())
    page.emulate_media(reduced_motion='no-preference')
    settle(page)
    check('motion responds to system preference change', page.locator('.motion-toggle').get_attribute('aria-pressed') == 'true')
    anchors = page.locator('a[href^="#"]').evaluate_all('els => els.map(e => e.hash.slice(1))')
    check('all local anchors resolve', all(page.locator(f'[id="{anchor}"]').count() == 1 for anchor in anchors))
    for target in ('Chenxu_Wang_Academic_CV.pdf?v=20261014', 'projects/dexterity.html', 'projects/signspeak.html', 'projects/xingju.html'):
        response = context.request.get(URL + target)
        check(f'local download/page reachable: {target}', response.status == 200 and len(response.body()) > 100)
        if target.startswith('Chenxu_Wang_Academic_CV.pdf'):
            check('served resume exactly matches selected PDF', response.body() == (ROOT / 'Chenxu_Wang_Academic_CV.pdf').read_bytes())
    check('homepage does not offer the old Word resume', page.locator('a[href*="Academic_CV.docx"]').count() == 0)
    with page.expect_download() as download:
        page.locator('.nav-cv').click()
    check('PDF download filename matches selected resume', download.value.suggested_filename == '王晨旭简历_北京理工大学.pdf')
    for section in ('about', 'research', 'education', 'projects', 'honors', 'contact'):
        page.locator(f'#{section}').scroll_into_view_if_needed()
        settle(page)
        check(f'{section} scrolling does not cause overflow', no_overflow(page))
    check('scrolled content and images visible', page.locator('img').evaluate_all('els => els.every(e => e.complete && e.naturalWidth > 0)'))
    check('scroll reveals all observed content', page.locator('[data-reveal]:not(.is-visible)').count() == 0)
    page.screenshot(path=str(OUT / 'desktop-full.png'), full_page=True)
    page.goto(URL)
    page.keyboard.press('Tab')
    check('keyboard skip link is first focus target', page.evaluate("document.activeElement.classList.contains('skip-link')"))
    page.keyboard.press('Enter')
    check('keyboard skip link reaches main', page.evaluate("document.activeElement.id === 'main'"))
    check('no JS exceptions or failed assets', not errors and not failures)

    for width in (320, 390, 600, 768, 1024):
        mobile = browser.new_context(viewport={'width': width, 'height': 844}, is_mobile=width < 768, has_touch=width < 768)
        mp = mobile.new_page()
        mp.goto(URL, wait_until='networkidle')
        check(f'{width}px layout fits viewport', no_overflow(mp))
        mp.locator('.site-header a[href="#projects"]').click()
        settle(mp)
        check(f'{width}px navigation reaches projects', mp.locator('.site-header a[aria-current]').get_attribute('href') == '#projects')
        if width == 390:
            mp.screenshot(path=str(OUT / 'mobile-projects.png'))
            mp.locator('.motion-toggle').click()
            mp.goto(URL, wait_until='networkidle')
            mp.screenshot(path=str(OUT / 'mobile-hero.png'))
            mp.screenshot(path=str(OUT / 'mobile-full.png'), full_page=True)
        mobile.close()

    fallback = browser.new_context(java_script_enabled=False, viewport={'width': 390, 'height': 844})
    fp = fallback.new_page()
    fp.goto(URL, wait_until='networkidle')
    check('no JS: layout fits viewport', no_overflow(fp))
    check('no JS: all content remains readable', fp.locator('#honors h2').evaluate("e => getComputedStyle(e).opacity === '1'"))
    check('no JS: inert controls hidden', not fp.locator('.motion-toggle').is_visible())
    fp.locator('.site-header a[href="#projects"]').click()
    settle(fp)
    check('no JS: anchor navigation works', fp.evaluate('location.hash') == '#projects')
    fallback.close()

    notes = context.new_page()
    notes.goto(URL + 'projects/dexterity.html', wait_until='networkidle')
    check('technical note style preserved', notes.locator('body').get_attribute('class') == 'technical-page' and notes.locator('script[src*="motion"]').count() == 0)
    check('technical note fits viewport', no_overflow(notes))
    browser.close()

(OUT / 'validation.json').write_text(json.dumps({'passed': len(results), 'checks': results, 'js_errors': errors, 'http_failures': failures}, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'passed': len(results), 'artifacts': str(OUT)}, ensure_ascii=False))
