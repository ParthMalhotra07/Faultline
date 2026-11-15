"""Rendered landing-page checks in isolated headless Chromium."""
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
out=ROOT/'artifacts/ui'/time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())
out.mkdir(parents=True)
report=dict(started_at=datetime.now(timezone.utc).isoformat(),base=BASE,
            browser='Isolated headless Playwright Chromium',checks=[],console_errors=[],page_errors=[],failed_requests=[],screenshots=[])
with sync_playwright() as pw:
    ws=os.environ.get('FAULTLINE_PLAYWRIGHT_WS')
    browser=(pw.chromium.connect(ws,expose_network=urlsplit(BASE).netloc,timeout=30000) if ws else pw.chromium.launch(headless=True))
    context=browser.new_context(viewport=dict(width=1440,height=1000),record_video_dir=str(out/'video'))
    context.tracing.start(screenshots=True,snapshots=True)
    page=context.new_page();page.set_default_timeout(15000)
    page.on('console',lambda m:report['console_errors'].append(m.text) if m.type=='error' else None)
    page.on('pageerror',lambda e:report['page_errors'].append(str(e)))
    page.on('requestfailed',lambda r:report['failed_requests'].append(dict(url=r.url,error=r.failure)))
    def screenshot(name):
        path=out/(name+'.png');page.screenshot(path=str(path),full_page=True)
        report['screenshots'].append(str(path.relative_to(ROOT)).replace('\\','/'))
    try:
        response=page.goto(BASE+'/',wait_until='networkidle')
        assert response.status==200
        expect(page.locator('#hero-title')).to_contain_text('Watch the graph learn why')
        expect(page.locator('#particle-wave')).to_be_visible()
        expect(page.locator('.hero-window')).to_be_visible()
        expect(page.locator('.workflow-step')).to_have_count(3)
        expect(page.locator('.workflow-step').nth(1)).to_contain_text('Check the missing link')
        report['checks'].append('Origyn-style landing hero, animated particle canvas and product window render at root')
        expect(page.locator('html')).to_have_attribute('data-preview-loaded','true')
        graph=page.request.get(BASE+'/api/graph').json()
        observations=page.request.get(BASE+'/api/observations').json()
        sources=page.request.get(BASE+'/api/sources').json()
        measured=page.request.get(BASE+'/api/results').json()['rows']
        expect(page.locator('#preview-graph-count')).to_have_text(f"{len(graph['nodes'])} nodes · {len(graph['edges'])} claims")
        expect(page.locator('#feature-node-count')).to_have_text(str(len(graph['nodes'])))
        expect(page.locator('#feature-edge-count')).to_have_text(str(len(graph['edges'])))
        expect(page.locator('#feature-learned-count')).to_have_text(str(sum(e['relationship_type']=='READS_CONFIG' for e in graph['edges'])))
        expect(page.locator('.source-row')).to_have_count(len(sources))
        expect(page.locator('#feature-chart circle')).to_have_count(21)
        for point in page.locator('#feature-chart circle').all():
            method=point.get_attribute('data-method');round_no=int(point.get_attribute('data-round'))
            actual=next(r for r in measured if r['method']==method and r['round']==round_no)
            assert int(point.get_attribute('data-correct'))==actual['correct']
        by_id={o['endpoint_id']:o['status'] for o in observations['observations']}
        for name in ('checkout','refunds','renewals'):
            expected=by_id.get('endpoint:'+name,'unknown')
            assert page.locator('#feature-health>div').filter(has=page.locator('b',has_text=name)).get_attribute('class')==expected
        report['checks'].append('Live preview, source list and measured chart match the actual public API')
        assert page.locator('#particle-wave').get_attribute('data-motion')=='active'
        first=page.locator('#particle-wave').evaluate('(canvas)=>canvas.toDataURL()')
        page.wait_for_timeout(300)
        second=page.locator('#particle-wave').evaluate('(canvas)=>canvas.toDataURL()')
        assert first!=second,'Particle wave did not animate'
        page.locator('#planning').scroll_into_view_if_needed()
        expect(page.locator('#planning .section-head')).to_have_class(re.compile('reveal-visible'))
        expect(page.locator('#overview .statement')).to_contain_text('Checkout fails')
        report['checks'].append('Particle wave changes over time and section content reveals on scroll')
        for element in page.locator('.reveal').all():
            element.scroll_into_view_if_needed()
            expect(element).to_have_class(re.compile('reveal-visible'))
        report['checks'].append('Every landing section reveals when scrolled into view')
        page.evaluate('scrollTo(0,0)');page.wait_for_timeout(750)
        page.screenshot(path=str(out/'00-hero-desktop.png'))
        report['screenshots'].append(str((out/'00-hero-desktop.png').relative_to(ROOT)).replace('\\','/'))
        screenshot('01-landing-desktop')
        page.set_viewport_size(dict(width=390,height=844))
        page.evaluate('scrollTo(0,0)');page.wait_for_timeout(350)
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),'Landing page overflows mobile width'
        expect(page.locator('.nav-workspace')).to_be_visible()
        screenshot('02-landing-mobile')
        report['checks'].append('Mobile landing and workspace CTA render without page overflow')
        page.set_viewport_size(dict(width=1440,height=1000))
        page.locator('.nav-workspace').click()
        expect(page).to_have_url(BASE+'/workspace')
        expect(page.locator('#demo-gate')).to_be_visible()
        page.locator('#demo-form button[type="submit"]').click()
        expect(page.locator('#demo-gate')).to_be_hidden()
        expect(page.locator('#tour')).to_be_visible()
        page.locator('#tour-skip').click()
        expect(page.locator('#graph svg')).to_be_visible()
        report['checks'].append('Landing CTA opens public demo access, tour and real HydraDB-backed workspace')
        reduced=browser.new_context(viewport=dict(width=1280,height=800),reduced_motion='reduce')
        reduced_page=reduced.new_page();reduced_page.goto(BASE+'/',wait_until='networkidle')
        expect(reduced_page.locator('#particle-wave')).to_have_attribute('data-motion','reduced')
        assert reduced_page.locator('#particle-wave').evaluate('(canvas)=>canvas.width>0')
        expect(reduced_page.locator('#overview .statement')).to_be_visible()
        reduced_page.screenshot(path=str(out/'03-reduced-motion.png'),full_page=True)
        report['screenshots'].append(str((out/'03-reduced-motion.png').relative_to(ROOT)).replace('\\','/'))
        reduced.close()
        report['checks'].append('Reduced-motion preference keeps content visible and animation static')
        assert not report['console_errors'] and not report['page_errors'] and not report['failed_requests']
        report['checks'].append('No browser console errors, uncaught page errors or failed requests')
        report['browser_version']=browser.version;report['status']='PASS'
        print(f"PASS: {len(report['checks'])} landing checks; screenshots and trace saved.",flush=True)
    except Exception as exc:
        report.update(status='FAIL',failure=str(exc))
        screenshot('failure')
        raise
    finally:
        report['completed_at']=datetime.now(timezone.utc).isoformat()
        context.tracing.stop(path=str(out/'trace.zip'))
        video=page.video;context.close()
        if video:video.save_as(str(out/'workflow.webm'))
        browser.close()
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        (ROOT/'artifacts/ui/latest-landing.json').write_text(json.dumps(dict(directory=str(out.relative_to(ROOT)).replace('\\','/')),indent=2)+'\n',encoding='utf-8')
