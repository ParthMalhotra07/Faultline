"""Actual timed silent demo recording in isolated headless Chromium."""
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import time
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright,expect

ROOT=Path(__file__).resolve().parents[1]
BASE=os.environ.get('FAULTLINE_BASE_URL','http://127.0.0.1:8765').rstrip('/')
out=ROOT/'artifacts/submission'; out.mkdir(parents=True,exist_ok=True)
report=dict(started_at=datetime.now(timezone.utc).isoformat(),label='Actual silent recording; live sandbox at capture time, recorded fallback when played',
            stages=[],console_errors=[],page_errors=[])
with sync_playwright() as pw:
    browser=pw.chromium.connect(os.environ['FAULTLINE_PLAYWRIGHT_WS'],expose_network=urlsplit(BASE).netloc,timeout=30000)
    context=browser.new_context(viewport=dict(width=1440,height=1000),record_video_dir=str(out/'video'))
    context.tracing.start(screenshots=True,snapshots=True)
    page=context.new_page();page.set_default_timeout(15000)
    page.on('console',lambda m:report['console_errors'].append(m.text) if m.type=='error' else None)
    page.on('pageerror',lambda e:report['page_errors'].append(str(e)))
    def click(id,endpoint):
        with page.expect_response(lambda r:r.url.endswith(endpoint)) as response:page.locator('#'+id).click()
        assert response.value.ok
        expect(page.locator('#learn')).to_be_enabled()
        expect(page.locator('#notice')).to_contain_text('Complete.')
    def stage(at,label):
        remaining=at-(time.monotonic()-start)
        if remaining>0:time.sleep(remaining)
        report['stages'].append(dict(target_second=at,actual_second=round(time.monotonic()-start,2),stage=label))
        print(f'{at}s: {label}',flush=True)
    try:
        page.goto(BASE+'/',wait_until='networkidle')
        expect(page.locator('#hero-title')).to_contain_text('Watch the graph learn why')
        page.screenshot(path=str(out/'landing.png'))
        page.locator('.nav-workspace').click()
        expect(page).to_have_url(BASE+'/workspace')
        click('reset','/local/reset-experiment')
        expect(page.locator('.health-card.healthy')).to_have_count(3)
        page.evaluate('scrollTo(0,0)')
        start=time.monotonic();stage(0,'Healthy executable app and missing-dependency problem')
        page.screenshot(path=str(out/'healthy.png'),full_page=True)
        stage(20,'Trigger actual checkout configuration fault')
        page.locator('#scenario').select_option('demo-currency');click('trigger','/local/trigger')
        stage(45,'Initial graph abstains honestly')
        click('diagnose','/api/diagnose');expect(page.locator('#diagnosis-status')).to_have_text('INSUFFICIENT EVIDENCE')
        stage(80,'Inspect one bounded source and commit verified HydraDB claims')
        click('learn','/api/learn');expect(page.locator('.origin')).to_have_text('config:currency')
        page.locator('#graph').scroll_into_view_if_needed()
        page.screenshot(path=str(out/'learning.png'),full_page=True)
        stage(110,'Restore real acceptance checks; graph learning persists')
        click('restore','/local/restore');expect(page.locator('.health-card.healthy')).to_have_count(3)
        stage(130,'Different refunds incident benefits without another inspection')
        page.locator('#scenario').select_option('demo-transfer');click('trigger','/local/trigger');click('diagnose','/api/diagnose')
        expect(page.locator('.origin')).to_have_text('config:currency')
        stage(155,'Show complete measured curve, fair baselines and limitations')
        page.locator('#results-section').scroll_into_view_if_needed();expect(page.locator('#chart circle')).to_have_count(28)
        page.screenshot(path=str(out/'comparison.png'),full_page=True)
        stage(174,'Buyer hypothesis and honest production boundaries')
        page.locator('footer').scroll_into_view_if_needed()
        stage(180,'End of three-minute storyboard')
        report['storyboard_elapsed_seconds']=time.monotonic()-start
        assert not report['console_errors'] and not report['page_errors']
        report['status']='PASS'
        print('PASS: timed 180-second storyboard completed with real controls and zero console/page errors.',flush=True)
    except Exception as e:
        report.update(status='FAIL',failure=str(e));raise
    finally:
        report['completed_at']=datetime.now(timezone.utc).isoformat()
        context.tracing.stop(path=str(out/'rehearsal-trace.zip'))
        video=page.video;context.close()
        if video:video.save_as(str(out/'fallback-demo.webm'))
        browser.close()
        (out/'rehearsal.json').write_text(json.dumps(report,indent=2)+'\n')
