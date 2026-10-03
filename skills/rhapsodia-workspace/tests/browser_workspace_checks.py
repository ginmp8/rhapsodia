#!/usr/bin/env python3
"""Optional real-browser checks; needs Playwright and a local Chromium executable."""
from __future__ import annotations
import argparse, copy, json, shutil, sys, tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package-root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--browser',default=shutil.which('chromium'))
    args=parser.parse_args();args.output_dir.mkdir(parents=True,exist_ok=True)
    sys.path.insert(0,str(args.package_root/'scripts'));sys.path.insert(0,str(args.package_root/'tests'))
    from artifact_protocol import canonical_bytes,digest
    from workspace import build_catalog,render
    from test_protocol import record
    outcomes=[]
    with tempfile.TemporaryDirectory() as temporary:
        repo=Path(temporary)
        for owner,area,dimension in [('nomia','product','governance'),('mago','specs','planning'),('magia','implementation','execution')]:
            value=record(f'docs/{area}/sample/example.md')
            value.update(producer=owner,artifact_id=f'{owner}:sample:example',title=f'{owner.title()} artifact',state={'dimension':dimension,'value':'unknown'})
            if owner=='magia':value['relations']=[{'type':'implements','target':'mago:sample:example'}]
            source=repo/value['source']['path'];source.parent.mkdir(parents=True);source.write_bytes(b'# Technical design\n')
            Path(str(source)+'.artifact.json').write_bytes(canonical_bytes(value))
        catalog=build_catalog(repo);html=repo/'index.html';html.write_bytes(render(catalog))
        with sync_playwright() as playwright:
            browser=playwright.chromium.launch(headless=True,executable_path=args.browser,args=['--no-sandbox'])
            page=browser.new_page(viewport={'width':1440,'height':1080},accept_downloads=True)
            errors=[];remote=[]
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.on('request',lambda req:remote.append(req.url) if req.url.startswith(('http:','https:')) else None)
            def reset():page.set_content(html.read_text(encoding='utf-8'));page.wait_for_load_state('networkidle')
            def check(name,fn):
                try:reset();fn();outcomes.append({'name':name,'status':'pass'})
                except Exception as exc:outcomes.append({'name':name,'status':'fail','error':str(exc)[:1000]})
            def import_data(value):
                payload=json.dumps(value).encode() if not isinstance(value,bytes) else value
                page.locator('#load-file').set_input_files({'name':'catalog.json','mimeType':'application/json','buffer':payload})
                expect(page.locator('#load-file')).to_have_value('')
            def views():
                for view,title in [('portfolio','Work items'),('timeline','Artifact updates'),('relations','Declared relationships'),('skills','Producer inventory')]:
                    page.locator(f'[data-view="{view}"]').click();assert page.locator('#view-title').inner_text()==title
                    assert page.locator('#content button').count()>0
            def filters():
                page.locator('#producer').select_option('mago');assert page.locator('#results-count').inner_text()=='1 shown'
                page.locator('#search').fill('nonexistent');assert 'No matching artifacts' in page.locator('#content').inner_text()
            def details():
                page.locator('#content button.artifact').first.click();assert 'Source SHA-256' in page.locator('#details').text_content(), 'Details not opened: '+page.locator('#details').inner_text()
                first=page.locator('html').get_attribute('data-theme');page.locator('#theme').click();assert page.locator('html').get_attribute('data-theme')!=first, 'Theme unchanged: '+str(first)+' / '+str(page.locator('html').get_attribute('data-theme'))
            def roundtrip():
                with page.expect_download() as download:page.locator('#export').click()
                exported=json.loads(Path(download.value.path()).read_text());assert exported==catalog
                import_data(exported);assert 'cannot be verified' in page.locator('#snapshot-note').inner_text()
            def mobile():
                page.set_viewport_size({'width':320,'height':1000})
                assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
                page.screenshot(path=str(args.output_dir/'mobile.png'),full_page=True)
                page.set_viewport_size({'width':1440,'height':1080})
            check('four_views',views);check('search_and_producer_filters',filters);check('details_and_theme',details);check('export_import_roundtrip',roundtrip);check('mobile_no_horizontal_overflow',mobile)
            mutations={
                'unknown_record_schema':lambda v:v['entries'][0]['record'].update(schema_version='9.0.0'),
                'invalid_privacy':lambda v:v['entries'][0]['record']['privacy'].update(contains_secrets=True),
                'unauthorized_destination':lambda v:v.update(destination='public'),
                'year_zero':lambda v:v['entries'][0]['record'].update(created_at='0000-01-01T12:00:00Z'),
                'invalid_calendar_date':lambda v:v['entries'][0]['record'].update(updated_at='2026-02-30T12:00:00Z'),
                'invalid_source_hash':lambda v:v['entries'][0]['record']['source'].update(sha256='not-a-sha256'),
                'extra_record_property':lambda v:v['entries'][0]['record'].update(unknown_property=True),
                'duplicate_artifact_id':lambda v:v['entries'].append(copy.deepcopy(v['entries'][0])),
                'self_relation':lambda v:v['entries'][0]['record'].update(relations=[{'type':'depends_on','target':v['entries'][0]['record']['artifact_id']}]),
                'source_path_escape':lambda v:v['entries'][0]['record']['source'].update(path='../outside.md'),
            }
            for name,mutate in mutations.items():
                def rejection(mutate=mutate):
                    value=copy.deepcopy(catalog);mutate(value);value['entries'][0]['record']['title']='Invalid imported change'
                    import_data(value)
                    assert 'Invalid imported change' not in page.locator('#content').inner_text(),'Invalid catalog replaced the last good snapshot'
                    assert not page.locator('#message').is_hidden(),'No rejection diagnostic'
                check('reject_'+name,rejection)
            def duplicate_key():
                raw=json.dumps(catalog).replace('"destination": "local"','"destination": "public", "destination": "local"')
                import_data(raw.encode());assert not page.locator('#message').is_hidden(),'Duplicate JSON keys accepted'
            check('reject_duplicate_json_keys',duplicate_key)
            reset();page.screenshot(path=str(args.output_dir/'desktop.png'),full_page=True)
            outcomes.append({'name':'no_uncaught_browser_errors','status':'pass' if not errors else 'fail','errors':errors})
            outcomes.append({'name':'no_external_network_requests','status':'pass' if not remote else 'fail','requests':remote})
            browser.close()
    report={'status':'pass' if all(row['status']=='pass' for row in outcomes) else 'fail','checks':outcomes,'browser':args.browser,'claim':'Exact rendered HTML loaded into local Chromium with set_content; file URL navigation is blocked by sandbox policy; other host runtimes not tested.'}
    (args.output_dir/'results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
    return 0 if report['status']=='pass' else 1
if __name__=='__main__':raise SystemExit(main())
