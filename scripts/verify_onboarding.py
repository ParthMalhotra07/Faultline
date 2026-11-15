"""Exercise public demo access, tour, navigation, and a live graph workflow."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import time
from urllib.parse import urlsplit

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
BASE = os.environ.get('FAULTLINE_BASE_URL', 'http://127.0.0.1:8765').rstrip('/')
OUT = ROOT / 'artifacts/ui' / ('t30-' + time.strftime('%Y%m%dT%H%M%SZ', time.gmtime()))
OUT.mkdir(parents=True, exist_ok=True)
report = dict(base=BASE, started_at=datetime.now(timezone.utc).isoformat(),
              status='RUNNING', checks=[], screenshots=[], console_errors=[],
              page_errors=[], failed_requests=[], navigation_aborts=[])


def capture(page, name, full_page=True):
    path = OUT / f'{name}.png'
    page.screenshot(path=str(path), full_page=full_page)
    report['screenshots'].append(str(path.relative_to(ROOT)).replace('\\', '/'))


with sync_playwright() as playwright:
    endpoint = os.environ.get('FAULTLINE_PLAYWRIGHT_WS')
    browser = (playwright.chromium.connect(endpoint, expose_network=urlsplit(BASE).netloc)
               if endpoint else playwright.chromium.launch(headless=True))
    context = browser.new_context(viewport=dict(width=1440, height=1000))
    page = context.new_page()
    page.set_default_timeout(20000)
    page.on('console', lambda message: report['console_errors'].append(message.text)
            if message.type == 'error' else None)
    page.on('pageerror', lambda error: report['page_errors'].append(str(error)))
    def request_failed(request):
        event = dict(url=request.url, error=request.failure)
        if request.failure == 'net::ERR_ABORTED' and request.url.endswith('/api/results'):
            report['navigation_aborts'].append(event)
        else:
            report['failed_requests'].append(event)

    page.on('requestfailed', request_failed)
    try:
        response = page.goto(BASE + '/', wait_until='networkidle')
        assert response.status == 200
        expect(page.locator('.header .brand-logo')).to_be_visible()
        logo = page.request.get(BASE + '/faultline-logo.png')
        assert logo.status == 200 and logo.headers['content-type'] == 'image/png'
        capture(page, '01-landing', full_page=False)
        report['checks'].append('Supplied logo loads in landing navigation and favicon route')

        page.locator('.nav-workspace').click()
        expect(page).to_have_url(BASE + '/workspace')
        expect(page.locator('#demo-gate')).to_be_visible()
        expect(page.locator('#demo-email')).to_have_value('judge@faultline.demo')
        expect(page.locator('#demo-password')).to_have_value('FaultlineDemo2026!')
        expect(page.locator('.demo-credentials-note')).to_contain_text('prefilled for hackathon testing')
        assert page.request.get(BASE + '/api/demo/session').json()['signed_in'] is False
        capture(page, '02-demo-access', full_page=False)
        report['checks'].append('Workspace presents working public demo access with labeled prefilled values')

        with page.expect_response(lambda result: result.url.endswith('/api/demo/sign-in')) as sign_in:
            page.locator('#demo-form button[type="submit"]').click()
        assert sign_in.value.status == 200
        expect(page.locator('#demo-gate')).to_be_hidden()
        expect(page.locator('#tour')).to_be_visible()
        expect(page.locator('#tour-progress')).to_contain_text('1 OF 5')
        assert page.request.get(BASE + '/api/demo/session').json()['signed_in'] is True
        capture(page, '03-first-visit-tour', full_page=False)
        report['checks'].append('Server-backed demo session starts a five-step first-visit tour')

        page.locator('#tour-next').click()
        expect(page.locator('#tour-progress')).to_contain_text('2 OF 5')
        page.locator('#tour-back').click()
        expect(page.locator('#tour-progress')).to_contain_text('1 OF 5')
        page.locator('#tour-skip').click()
        expect(page.locator('#tour')).to_be_hidden()
        assert page.evaluate("localStorage.getItem('faultline-tour-v1-complete')") == 'yes'
        report['checks'].append('Tour Next, Back, and Skip work and save completion in this browser')

        page.locator('#take-tour').click()
        expect(page.locator('#tour')).to_be_visible()
        for _ in range(4):
            page.locator('#tour-next').click()
        expect(page.locator('#tour-progress')).to_contain_text('5 OF 5')
        page.locator('#tour-next').click()
        expect(page.locator('#tour')).to_be_hidden()
        report['checks'].append('Manual replay traverses all five steps and Finish closes the tour')

        page.reload(wait_until='networkidle')
        expect(page.locator('#demo-gate')).to_be_hidden()
        expect(page.locator('#tour')).to_be_hidden()
        expect(page.locator('#graph svg')).to_be_visible()
        report['checks'].append('Demo cookie resumes the workspace; completed tour stays dismissed')

        page.locator('#reset').click()
        expect(page.locator('.health-card.healthy')).to_have_count(3)
        page.locator('#trigger').click()
        expect(page.locator('.health-card.failing')).to_have_count(1)
        page.locator('#diagnose').click()
        expect(page.locator('#diagnosis-status')).to_have_text('INSUFFICIENT EVIDENCE')
        page.locator('#learn').click()
        expect(page.locator('#diagnosis-status')).to_have_text('SUPPORTED')
        expect(page.locator('.origin')).to_have_text('config:currency')
        graph = page.request.get(BASE + '/api/graph').json()
        assert graph['source'] == 'live HydraDB traversal'
        assert any(edge['relationship_type'] == 'READS_CONFIG' for edge in graph['edges'])
        capture(page, '04-live-workspace')
        report['checks'].append('Demo controls still trigger, abstain, learn and traverse real HydraDB claims')

        page.set_viewport_size(dict(width=390, height=844))
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        expect(page.locator('#take-tour')).to_be_visible()
        page.locator('#take-tour').click()
        expect(page.locator('#tour-card')).to_be_visible()
        capture(page, '05-mobile-tour', full_page=False)
        page.locator('#tour-skip').click()
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        capture(page, '06-mobile-workspace')
        report['checks'].append('Mobile workspace and replayed tour remain usable without page overflow')

        with page.expect_response(lambda result: result.url.endswith('/api/demo/sign-out')) as sign_out:
            page.locator('#signout').click()
        assert sign_out.value.status == 200
        expect(page.locator('#demo-gate')).to_be_visible()
        assert page.request.get(BASE + '/api/demo/session').json()['signed_in'] is False
        page.locator('#demo-form button[type="submit"]').click()
        expect(page.locator('#demo-gate')).to_be_hidden()
        expect(page.locator('#tour')).to_be_hidden()
        expect(page.locator('#results-section')).to_be_visible()
        page.locator('.identity').click()
        expect(page).to_have_url(BASE + '/')
        expect(page.locator('#hero-title')).to_be_visible()
        report['checks'].append('Sign-out revokes the demo session; re-entry works and workspace logo returns home')

        assert not report['console_errors'], report['console_errors']
        assert not report['page_errors'], report['page_errors']
        assert not report['failed_requests'], report['failed_requests']
        report['checks'].append('No browser console, page, or unexpected failed-request errors')
        report['status'] = 'PASS'
        report['browser_version'] = browser.version
        print(f'PASS: {len(report["checks"])} rendered onboarding and graph checks; screenshots saved.')
    except Exception as error:
        report['status'] = 'FAIL'
        report['failure'] = str(error)
        capture(page, 'failure')
        raise
    finally:
        report['completed_at'] = datetime.now(timezone.utc).isoformat()
        context.close()
        browser.close()
        (OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        (ROOT / 'artifacts/T30-browser-report.json').write_text(
            json.dumps(dict(directory=str(OUT.relative_to(ROOT)).replace('\\', '/'),
                            status=report['status'], checks=report['checks'],
                            screenshots=report['screenshots']), indent=2) + '\n', encoding='utf-8')
