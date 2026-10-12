#!/usr/bin/env python3
"""Opt-in Playwright evidence recorder for *trusted* local or explicitly approved sites.

Playwright is optional; it is not installed or downloaded. Network requests
outside the exact approved origin are blocked at Playwright routing level (not
an OS firewall). Actions and DOM content can contain private data; output omits
values and stores hashes by default. Never browse uploaded untrusted sites.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
from urllib.parse import urlsplit
from behavior_lab import DataError, strict_json
from interface_traces import origin_url
from json_writer import write_exclusive


def safe_actions(path:Path)->list[dict]:
    if path.is_symlink() or not path.is_file() or path.stat().st_size>256*1024:
        raise DataError('bounded regular actions JSON required')
    value=strict_json(path.read_text('utf-8'))
    if not isinstance(value,list) or len(value)>100:raise DataError('actions must be bounded array')
    for a in value:
        if not isinstance(a,dict) or a.get('type') not in ('goto','click','fill','press','text-hash'):
            raise DataError('unknown browser action')
        if a['type']=='goto':
            p=a.get('path')
            if not isinstance(p,str) or not p.startswith('/') or p.startswith('//') or '?' in p or '#' in p or '\\' in p:
                raise DataError('goto must be local origin path')
        else:
            selector=a.get('selector')
            if not isinstance(selector,str) or not 1<=len(selector)<=512:
                raise DataError('bounded selector required')
        if a['type'] in ('fill','press') and (not isinstance(a.get('value'),str) or len(a['value'])>1024):
            raise DataError('fill/press requires bounded string value')
    return value


def record(origin:str,actions:list,*,authorized:bool=False,allow_nonlocal:bool=False,
           screenshot:Path|None=None,include_text:bool=False,
           browser_executable:Path|None=None)->dict:
    if not authorized:raise DataError('browser capture requires explicit authorization')
    base=origin_url(origin,allow_nonlocal=allow_nonlocal)
    try:
        from playwright.sync_api import sync_playwright, Error as PlaywrightError
    except ImportError as exc:
        raise DataError('Playwright unavailable; installed browser + Python package required externally') from exc
    events=[];observations=[]
    allowed=urlsplit(base)
    def permitted(url):
        parsed=urlsplit(url)
        return (parsed.scheme,parsed.netloc)==(allowed.scheme,allowed.netloc)
    executable_args={}
    if browser_executable:
        if browser_executable.is_symlink() or not browser_executable.is_absolute() or not browser_executable.is_file():
            raise DataError('browser executable must be an existing absolute non-symlink file')
        executable_args['executable_path']=str(browser_executable.resolve())
    try:
        manager=sync_playwright()
        pw=manager.start()
        browser=pw.chromium.launch(headless=True,**executable_args)
    except PlaywrightError as exc:
        if 'pw' in locals(): pw.stop()
        raise DataError('Browser launch failed or is denied by host policy; confirm installed browser and permissions') from exc
    try:
        context=browser.new_context(service_workers='block',accept_downloads=False)
        def handle_route(route):
            if permitted(route.request.url):route.continue_()
            else:route.abort('blockedbyclient')
        context.route('**/*',handle_route)
        page=context.new_page()
        page.on('request',lambda req:events.append({'kind':'request','method':req.method,
                                                      'path':urlsplit(req.url).path if permitted(req.url) else '[blocked-origin]'}))
        page.on('response',lambda res:events.append({'kind':'response','status':res.status,
                                                      'path':urlsplit(res.url).path if permitted(res.url) else '[blocked-origin]'}))
        try:
            for index,action in enumerate(actions):
                kind=action['type']
                if kind=='goto':
                    page.goto(base+action['path'],wait_until='domcontentloaded',timeout=10000)
                elif kind=='click':page.locator(action['selector']).click(timeout=5000)
                elif kind=='fill':page.locator(action['selector']).fill(action['value'],timeout=5000)
                elif kind=='press':page.locator(action['selector']).press(action['value'],timeout=5000)
                elif kind=='text-hash':
                    t=page.locator(action['selector']).inner_text(timeout=5000)
                    obs={'index':index,'type':kind,'sha256':hashlib.sha256(t.encode('utf-8')).hexdigest(),'characters':len(t)}
                    if include_text:obs['text']=t[:4096]
                    observations.append(obs)
            if screenshot:
                if screenshot.exists():raise DataError('screenshot already exists')
                screenshot.parent.mkdir(parents=True,exist_ok=True)
                page.screenshot(path=str(screenshot),full_page=False)
                observations.append({'type':'screenshot','sha256':hashlib.sha256(screenshot.read_bytes()).hexdigest(),
                                     'file':screenshot.name})
        finally:
            context.close()
    except PlaywrightError as exc:
        raise DataError('Browser navigation/action blocked or failed under host policy; no observation promoted') from exc
    finally:
        browser.close();pw.stop()
    return {'schema_version':'1.0','mode':'authorized-browser-capture','origin':base,
            'actions_sha256':hashlib.sha256(json.dumps(actions,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),
            'events':events[:2000],'events_truncated':len(events)>2000,
            'events_dropped':max(0,len(events)-2000),'observations':observations,
            'redaction':'network queries, bodies, headers and DOM text omitted unless text requested',
            'limits':'Playwright routing blocks off-origin requests, not OS/network-level sandbox; site scripts execute in browser'}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--origin',required=True)
    p.add_argument('--actions',type=Path,required=True)
    p.add_argument('--execute-authorized',action='store_true')
    p.add_argument('--allow-nonlocal',action='store_true')
    p.add_argument('--include-text',action='store_true')
    p.add_argument('--screenshot',type=Path)
    p.add_argument('--browser-executable',type=Path,help='Preinstalled Chromium path (no auto-download)')
    p.add_argument('-o','--output',required=True,type=Path)
    a=p.parse_args(argv)
    try:
        if a.output.resolve()==a.actions.resolve() or (a.screenshot and a.output.resolve()==a.screenshot.resolve()):
            raise DataError('output aliases input/screenshot')
        result=record(a.origin,safe_actions(a.actions),authorized=a.execute_authorized,
                      allow_nonlocal=a.allow_nonlocal,screenshot=a.screenshot,include_text=a.include_text,browser_executable=a.browser_executable)
        write_exclusive(a.output,json.dumps(result,ensure_ascii=False,indent=2)+'\n',[a.actions])
        return 0
    except (ValueError,OSError) as exc:
        print(json.dumps({'error':str(exc)}),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
