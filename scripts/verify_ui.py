"""User-authorized isolated headless Chromium QA; never touches desktop Chrome."""
import argparse
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import re
import time
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright,expect

ROOT=Path(__file__).resolve().parents[1]
BASE=os.environ.get('FAULTLINE_BASE_URL','http://127.0.0.1:8765').rstrip('/')
os.environ.setdefault('PLAYWRIGHT_BROWSERS_PATH',str(ROOT/'.runtime/playwright-browsers'))
p=argparse.ArgumentParser(); p.add_argument('--results',action='store_true'); a=p.parse_args()
out=ROOT/'artifacts/ui'/time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())
out.mkdir(parents=True)
report=dict(started_at=datetime.now(timezone.utc).isoformat(),browser='Isolated headless Playwright Chromium',
            user_profile=False,channel=os.environ.get('FAULTLINE_PLAYWRIGHT_CHANNEL','chromium'),
            checks=[],console_errors=[],page_errors=[],failed_requests=[],http_errors=[],screenshots=[])
with sync_playwright() as pw:
    ws=os.environ.get('FAULTLINE_PLAYWRIGHT_WS')
    browser=(pw.chromium.connect(ws,expose_network=urlsplit(BASE).netloc,timeout=30000) if ws else
             pw.chromium.launch(headless=True,channel=os.environ.get('FAULTLINE_PLAYWRIGHT_CHANNEL','chromium')))
    context=browser.new_context(viewport=dict(width=1440,height=1000),record_video_dir=str(out/'video'))
    context.tracing.start(screenshots=True,snapshots=True,sources=True)
    page=context.new_page(); page.set_default_timeout(15000)
    page.on('console',lambda m:report['console_errors'].append(m.text) if m.type=='error' else None)
    page.on('pageerror',lambda e:report['page_errors'].append(str(e)))
    page.on('requestfailed',lambda r:report['failed_requests'].append(dict(url=r.url,error=r.failure)))
    page.on('response',lambda r:report['http_errors'].append(dict(url=r.url,status=r.status)) if r.status>=400 else None)
    def screenshot(name):
        path=out/(name+'.png'); page.screenshot(path=str(path),full_page=True)
        report['screenshots'].append(str(path.relative_to(ROOT)).replace('\\','/'))
    def click(id,endpoint,message='Complete.'):
        with page.expect_response(lambda r:r.url.endswith(endpoint)) as response:
            page.locator('#'+id).click()
        assert response.value.ok, f'{endpoint}: {response.value.status}'
        expect(page.locator('#learn')).to_be_enabled()
        expect(page.locator('#notice')).to_contain_text(message)
    try:
        response=page.goto(BASE+'/workspace',wait_until='networkidle')
        assert response.status==200
        expect(page).to_have_url(BASE+'/workspace')
        expect(page.locator('#graph svg')).to_be_visible()
        report['browser_version']=browser.version
        click('reset','/local/reset-experiment')
        expect(page.locator('.health-card.healthy')).to_have_count(3)
        expect(page.locator('#graph .edge.learned')).to_have_count(0)
        report['checks'].append('Experiment reset: three healthy flows and no learned config claims')
        screenshot('01-healthy-desktop')
        page.locator('#scenario').select_option('demo-currency')
        click('trigger','/local/trigger')
        expect(page.locator('.health-card.failing')).to_have_count(1)
        click('diagnose','/api/diagnose')
        expect(page.locator('#diagnosis-status')).to_have_text('INSUFFICIENT EVIDENCE')
        report['checks'].append('Real checkout fault: initial graph diagnosis visibly abstains')
        screenshot('02-insufficient-evidence')
        click('learn','/api/learn')
        expect(page.locator('#diagnosis-status')).to_have_text('SUPPORTED')
        expect(page.locator('.origin')).to_have_text('config:currency')
        expect(page.locator('#graph .edge.learned')).to_have_count(2)
        graph=page.request.get(BASE+'/api/graph').json()
        actual_nodes=set(page.locator('#graph .node title').all_text_contents())
        assert actual_nodes=={n['id'] for n in graph['nodes']}
        assert page.locator('#graph .edge').count()==len(graph['edges'])
        report['checks'].append('Learning: supported currency hypothesis; rendered nodes/edges match real backend graph')
        screenshot('03-learned-graph')
        click('restore','/local/restore')
        expect(page.locator('.health-card.healthy')).to_have_count(3)
        expect(page.locator('#graph .edge.learned')).to_have_count(2)
        page.locator('#scenario').select_option('demo-transfer')
        click('trigger','/local/trigger'); click('diagnose','/api/diagnose')
        expect(page.locator('.origin')).to_have_text('config:currency')
        report['checks'].append('Restore preserves learning; different refunds incident is supported without inspection')
        screenshot('04-transfer')
        click('learn','/api/learn','No unseen relevant evidence sources remain.')
        report['checks'].append('Relevant-source exhaustion is explicitly visible, without another inspection')
        if a.results:
            expect(page.locator('#results-section')).to_be_visible()
            expect(page.locator('#chart circle')).to_have_count(28)
            measured=page.request.get(BASE+'/api/results').json()['rows']
            for point in page.locator('#chart circle').all():
                method=point.get_attribute('data-method'); round_no=int(point.get_attribute('data-round'))
                actual=next(r for r in measured if r['method']==method and r['round']==round_no)
                assert int(point.get_attribute('data-correct'))==actual['correct']
                assert int(point.get_attribute('data-total'))==actual['total']
            screenshot('05-results')
            page.locator('#replay').click()
            expect(page.locator('#mode')).to_contain_text('RECORDED')
            expect(page.locator('.origin')).to_have_text('config:currency')
            expect(page.locator('#manifest')).to_contain_text('Recorded')
            report['checks'].append('All 28 measured curve points render; recorded pilot replay is distinctly labeled')
            screenshot('06-replay')
        page.set_viewport_size(dict(width=390,height=844))
        expect(page.locator('#learn')).to_be_visible()
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'Horizontal mobile overflow'
        screenshot('07-mobile')
        report['checks'].append('390px mobile layout has no horizontal overflow and visible controls')
        page.set_viewport_size(dict(width=1440,height=1000))
        assert not report['page_errors'], report['page_errors']
        assert not report['console_errors'], report['console_errors']
        assert not report['failed_requests'], report['failed_requests']
        report['checks'].append('No browser console errors, uncaught page errors, or failed requests during successful workflow')
        # Explicit transport-failure UI check; it does not stand in for database integration.
        page.route('**/api/diagnose',lambda route:route.fulfill(status=503,content_type='application/json',body='{"error":"Injected test-only transport failure"}'))
        page.locator('#diagnose').click()
        expect(page.locator('#notice')).to_have_text('Injected test-only transport failure')
        expect(page.locator('#notice')).to_have_class('error')
        report['checks'].append('Injected HTTP 503 visibly shows an error rather than an empty success')
        report['expected_error']='One intentionally injected HTTP 503 after successful-workflow console checks'
        screenshot('08-explicit-error')
        page.unroute('**/api/diagnose')
        report['status']='PASS'
        print('PASS:',len(report['checks']),'rendered workflow checks; screenshots, video, trace and console saved.')
    except Exception as e:
        report['status']='FAIL'; report['failure']=str(e)
        screenshot('failure')
        raise
    finally:
        report['completed_at']=datetime.now(timezone.utc).isoformat()
        context.tracing.stop(path=str(out/'trace.zip'))
        video=page.video
        context.close()
        if video: video.save_as(str(out/'workflow.webm'))
        browser.close()
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
        (ROOT/'artifacts/ui/latest-attempt.json').write_text(json.dumps(dict(directory=str(out.relative_to(ROOT)).replace('\\','/')),indent=2)+'\n')
