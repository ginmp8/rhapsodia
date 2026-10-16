#!/usr/bin/env python3
"""Bounded, consent-gated Playwright UI investigation for trusted websites/HTML fixtures.

Does not bypass site protections, log headers/body/token values, execute unknown
uploads, install browser packages, or assert code/runtime causal equivalence.
Fixture navigation uses page.set_content (no network); it is NOT real HTTP.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import sys
import time
from urllib.parse import urljoin, urlsplit, unquote

from behavior_lab import DataError, strict_json
from interface_traces import origin_url
from json_writer import write_exclusive

MAX_ACTIONS = 100
MAX_EVENTS = 2000
MAX_PAGES = 20
MAX_HTML = 1024 * 1024
MUTATIONS = frozenset({'click', 'fill', 'press', 'hover', 'drag', 'select', 'scroll'})
KINDS = MUTATIONS | {'goto', 'text-hash'}
HEADERS = ('content-security-policy', 'x-content-type-options', 'referrer-policy',
           'strict-transport-security', 'access-control-allow-origin')


def digest(value: bytes | str) -> str:
    if isinstance(value, str):
        value = value.encode('utf-8')
    return hashlib.sha256(value).hexdigest()


def clean_path(path: str) -> str:
    """Drop query, fragment and suspicious dynamic segments; never store credentials."""
    segments = []
    for raw in urlsplit(path).path.split('/'):
        s = unquote(raw)
        if not s:
            segments.append('')
        elif (len(s) > 64 or re.fullmatch(r'\d{5,}|[0-9a-fA-F-]{20,}', s)
              or re.search(r'(?:token|secret|password|key)=', s, re.I)):
            segments.append('[redacted-segment]')
        else:
            segments.append(s)
    return '/'.join(segments)[:512] or '/'


def safe_route(route: str) -> str:
    if (not isinstance(route, str) or not route.startswith('/') or route.startswith('//')
            or '\\' in route or '?' in route or '#' in route or len(route) > 512
            or any(ord(c) < 32 for c in route)
            or any(part in ('.', '..') for part in route.split('/'))):
        raise DataError('browser path must be an absolute same-origin path without query, dot segments or fragment')
    return route


def json_input(path: Path, max_bytes: int = 256*1024):
    if path.is_symlink() or not path.is_file() or path.stat().st_size > max_bytes:
        raise DataError('bounded regular JSON file required')
    return strict_json(path.read_text('utf-8'))


def validate_actions(raw: list[dict]) -> list[dict]:
    if not isinstance(raw, list) or len(raw) > MAX_ACTIONS:
        raise DataError('actions must be an array of at most 100 items')
    for i, a in enumerate(raw):
        if not isinstance(a, dict) or a.get('type') not in KINDS:
            raise DataError(f'unknown action at index {i}')
        k = a['type']
        keys = {'type', 'path'} if k == 'goto' else {'type', 'selector'}
        if k in ('fill', 'press', 'select'):
            keys.add('value')
        if k == 'drag':
            keys.add('target')
        if k == 'scroll':
            keys.add('pixels')
        if set(a) != keys:
            raise DataError(f'action {i} has missing or unsupported fields')
        if k == 'goto':
            safe_route(a['path'])
            continue
        if not isinstance(a['selector'], str) or not 1 <= len(a['selector']) <= 512:
            raise DataError('bounded nonempty CSS selector required')
        if k in ('fill', 'press', 'select') and (not isinstance(a['value'], str) or len(a['value']) > 1024):
            raise DataError('bounded action value required')
        if k == 'drag' and (not isinstance(a['target'], str) or not 1 <= len(a['target']) <= 512):
            raise DataError('bounded target selector required')
        if k == 'scroll' and (type(a['pixels']) is not int or abs(a['pixels']) > 10000):
            raise DataError('scroll pixels must be integer in +/-10000')
    return raw


def checked_actions(path: Path) -> list[dict]:
    return validate_actions(json_input(path))


def browser_capabilities() -> dict:
    candidates = [x for x in ('chromium', 'chromium-browser', 'google-chrome', 'msedge') if shutil.which(x)]
    return {'python_playwright': importlib.util.find_spec('playwright') is not None,
            'browser_candidates': candidates,
            'supports': ['detect', 'capture', 'explore', 'offline-fixture', 'network-metadata',
                         'dom-hashes', 'viewport-overflow', 'local-timing'],
            'note': 'Detection does not prove browser launch, HTTP access or host security.'}


def checked_fixture(root: Path, route: str) -> str:
    """Resolve only regular pre-reviewed .html beneath explicit root; do not follow links."""
    safe_route(route)
    if root.is_symlink() or not root.is_dir():
        raise DataError('trusted fixture root must be an existing nonsymlink directory')
    relative = (route.strip('/') or 'index.html')
    if relative.endswith('/'):
        relative += 'index.html'
    if not relative.endswith('.html'):
        raise DataError('fixtures must be .html files')
    candidate = root / relative
    if any(p.is_symlink() for p in (candidate, *candidate.parents) if p != root.parent):
        raise DataError('fixture symlink forbidden')
    if not candidate.resolve().is_relative_to(root.resolve()):
        raise DataError('fixture escaped approved root')
    if not candidate.is_file() or candidate.stat().st_size > MAX_HTML:
        raise DataError('fixture missing, oversized, or not regular file')
    return candidate.read_text('utf-8')


def snapshot(page, current_path: str, *, include_text: bool = False) -> dict:
    # This is a fixed script owned by the tool, not JavaScript from task inputs.
    dom = page.evaluate('''() => {
      const b=document.body;
      const t=b ? (b.innerText || '').slice(0,100000) : '';
      const w=document.documentElement;
      const p=performance.getEntriesByType('navigation')[0];
      return {text:t, heading_count:document.querySelectorAll('h1,h2,h3').length,
        form_count:document.querySelectorAll('form').length,
        link_count:document.querySelectorAll('a[href]').length,
        input_count:document.querySelectorAll('input,select,textarea').length,
        interactive_count:document.querySelectorAll('button,a[href],input,select,textarea').length,
        scroll_width:w ? w.scrollWidth:0, client_width:w ? w.clientWidth:0,
        navigation_duration_ms:p?Math.round(p.duration*100)/100:null,
        resource_count:performance.getEntriesByType('resource').length};
    }''')
    t = dom.pop('text')
    out = {'path': clean_path(current_path), 'text_sha256': digest(t),
           'text_characters': len(t), 'text_truncated': len(t) == 100000,
           **dom, 'horizontal_overflow': dom['scroll_width'] > dom['client_width']}
    if include_text:
        out['text'] = t[:4000]
    return out


def links_from_page(page, origin: str) -> list[str]:
    hrefs = page.locator('a[href]').evaluate_all('(nodes) => nodes.slice(0,200).map(a => a.getAttribute("href"))')
    out = set()
    base = urlsplit(origin)
    for href in hrefs:
        if not isinstance(href, str) or len(href) > 512:
            continue
        url = urlsplit(urljoin(origin + '/', href))
        if (url.scheme, url.netloc) != (base.scheme, base.netloc):
            continue
        if url.query:
            continue  # Never replay token-bearing query URLs automatically.
        try:
            path = safe_route(url.path or '/')
        except DataError:
            continue
        out.add(path)
    return sorted(out)[:200]


def inspect_browser(*, mode: str, origin: str, actions: list[dict] | None = None,
                    fixture_root: Path | None = None, authorized: bool = False,
                    mutations_approved: bool = False, allow_nonlocal: bool = False,
                    max_pages: int = 5, viewport_width: int = 1280,
                    viewport_height: int = 720, screenshot: Path | None = None,
                    include_text: bool = False, browser_executable: Path | None = None) -> dict:
    if not authorized:
        raise DataError('explicit trusted-target execution authorization required')
    base = origin_url(origin, allow_nonlocal=allow_nonlocal)
    if viewport_width < 320 or viewport_width > 3840 or viewport_height < 240 or viewport_height > 2160:
        raise DataError('invalid viewport bounds')
    if type(max_pages) is not int or not 1 <= max_pages <= MAX_PAGES:
        raise DataError('max-pages outside 1..20')
    if mode not in ('capture', 'explore'):
        raise DataError('unknown investigation mode')
    if mode == 'capture' and actions is None:
        raise DataError('capture requires actions')
    if mode == 'capture':
        validate_actions(actions)
    if mode == 'capture' and any(a['type'] in MUTATIONS for a in (actions or [])) and not mutations_approved:
        raise DataError('UI interactions require separate --mutations-approved authorization')
    if fixture_root and (fixture_root.is_symlink() or not fixture_root.is_dir()):
        raise DataError('fixture root must be a nonsymlink existing directory')
    if browser_executable and (browser_executable.is_symlink() or not browser_executable.is_absolute()
                               or not browser_executable.is_file()):
        raise DataError('browser path must be an absolute existing nonsymlink executable')
    if screenshot and screenshot.exists():
        raise DataError('screenshot output already exists')
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise DataError('Playwright is not installed in this runtime') from exc
    events: list[dict] = []
    dropped_events = [0]
    steps: list[dict] = []
    pages: list[dict] = []
    links: list[dict] = []
    errors = {'console_errors': 0, 'page_errors': 0, 'blocked_requests': 0}
    current_path = '/'
    base_parts = urlsplit(base)
    def on_request(req):
        if len(events) >= MAX_EVENTS:
            dropped_events[0] += 1
            return
        url = urlsplit(req.url)
        permitted = (url.scheme, url.netloc) == (base_parts.scheme, base_parts.netloc)
        events.append({'kind': 'request', 'method': req.method[:12],
                       'path': clean_path(req.url) if permitted else '[off-origin]',
                       'resource_type': req.resource_type[:32], 'observed': fixture_root is None})
    def on_response(res):
        if len(events) >= MAX_EVENTS:
            dropped_events[0] += 1
            return
        url = urlsplit(res.url)
        permitted = (url.scheme, url.netloc) == (base_parts.scheme, base_parts.netloc)
        hdrs = res.headers
        events.append({'kind': 'response', 'status': res.status,
                       'path': clean_path(res.url) if permitted else '[off-origin]',
                       'security_headers_present': {h: h in hdrs for h in HEADERS},
                       'observed': fixture_root is None})

    try:
        with sync_playwright() as pw:
            launch = {'headless': True}
            if browser_executable:
                launch['executable_path'] = str(browser_executable)
            browser = pw.chromium.launch(**launch)
            try:
                context = browser.new_context(viewport={'width': viewport_width, 'height': viewport_height},
                                              service_workers='block', accept_downloads=False)
                try:
                    def handle_route(route):
                        url = urlsplit(route.request.url)
                        ok = (url.scheme, url.netloc) == (base_parts.scheme, base_parts.netloc)
                        if fixture_root or not ok:
                            errors['blocked_requests'] += 1
                            route.abort('blockedbyclient')
                        else:
                            route.continue_()
                    context.route('**/*', handle_route)
                    page = context.new_page()
                    page.on('request', on_request)
                    page.on('response', on_response)
                    page.on('pageerror', lambda _: errors.__setitem__('page_errors', errors['page_errors'] + 1))
                    page.on('console', lambda msg: errors.__setitem__('console_errors',errors['console_errors'] + 1) if msg.type == 'error' else None)

                    def navigate(path):
                        nonlocal current_path
                        path = safe_route(path)
                        if fixture_root:
                            html = checked_fixture(fixture_root, path)
                            page.set_content(html, wait_until='domcontentloaded', timeout=10000)
                        else:
                            page.goto(base + path, wait_until='domcontentloaded', timeout=10000)
                        current_path = path

                    if mode == 'capture':
                        for index, action in enumerate(actions or []):
                            typ = action['type']
                            start_events = len(events)
                            before = time.monotonic()
                            additional = {}
                            if typ == 'goto':
                                navigate(action['path'])
                            elif typ == 'click':
                                page.locator(action['selector']).click(timeout=5000)
                            elif typ == 'fill':
                                page.locator(action['selector']).fill(action['value'], timeout=5000)
                            elif typ == 'press':
                                page.locator(action['selector']).press(action['value'], timeout=5000)
                            elif typ == 'hover':
                                page.locator(action['selector']).hover(timeout=5000)
                            elif typ == 'drag':
                                page.locator(action['selector']).drag_to(page.locator(action['target']),timeout=5000)
                            elif typ == 'select':
                                page.locator(action['selector']).select_option(action['value'],timeout=5000)
                            elif typ == 'scroll':
                                # Fixed scroll implementation without an arbitrary JS expression supplied by input.
                                page.locator(action['selector']).evaluate('(el,pixels)=>el.scrollBy(0,pixels)',action['pixels'])
                            elif typ == 'text-hash':
                                t = page.locator(action['selector']).inner_text(timeout=5000)
                                additional['selected_text_sha256'] = digest(t)
                                additional['selected_text_characters'] = len(t)
                                if include_text:
                                    additional['selected_text'] = t[:4096]
                            elapsed = round((time.monotonic() - before)*1000, 2)
                            steps.append({'index': index, 'type': typ, 'duration_ms': elapsed,
                                          'events_from': start_events, 'events_to': len(events),
                                          'dom': snapshot(page, current_path, include_text=include_text),
                                          **additional})
                    else:
                        # Only same-origin GET navigations. Not authenticated browser crawling.
                        queue = ['/index.html' if fixture_root else '/']
                        visited = set()
                        while queue and len(pages) < max_pages:
                            path = queue.pop(0)
                            if path in visited:
                                continue
                            visited.add(path)
                            navigate(path)
                            found = links_from_page(page, base)
                            pages.append({'path': clean_path(path), 'dom': snapshot(page,path,include_text=include_text),
                                          'link_count_recorded': len(found)})
                            for dest in found:
                                links.append({'from': clean_path(path), 'to': clean_path(dest),
                                              'level': 'declared-browser-link'})
                                if dest not in visited and dest not in queue:
                                    queue.append(dest)
                    if screenshot:
                        screenshot.parent.mkdir(parents=True, exist_ok=True)
                        page.screenshot(path=str(screenshot), full_page=False)
                finally:
                    context.close()
            finally:
                browser.close()
    except DataError:
        raise
    except Exception as exc:
        # Avoid potentially sensitive exception messages from sites/browsers.
        raise DataError(f'Browser capture failed ({type(exc).__name__}); no partial trace promoted') from exc
    result = {'schema_version':'1.0','mode':'web-investigation','investigation':mode,
              'evidence_type':'trusted-offline-html-fixture' if fixture_root else 'authorized-live-browser',
              'network_evidence': fixture_root is None,
              'origin_sha256':digest(base), 'fixture_root_sha256':digest(str(fixture_root.resolve())) if fixture_root else None,
              'actions_sha256':digest(json.dumps(actions,sort_keys=True,ensure_ascii=False)) if actions is not None else None,
              'viewport': {'width':viewport_width,'height':viewport_height}, 'steps':steps,
              'pages':pages,'links':links,'events':events, 'counters':errors,
              'events_truncated':dropped_events[0]>0,
              'events_dropped':dropped_events[0],
              'limitations': ('Fixture executes approved local HTML scripts; no HTTP/network or real app behavior validated.'
                              if fixture_root else 'Captured only allowed browser metadata; no backend logic or OS-level network isolation.'),
              'privacy':'No cookies, headers values, HTTP bodies, search params, form input values or console messages recorded.'}
    if screenshot:
        result['screenshot'] = {'sha256':digest(screenshot.read_bytes()),'file_name':screenshot.name,
                                'warning':'Image may contain sensitive visual content'}
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command',required=True)
    sub.add_parser('detect')
    for name in ('capture','explore'):
        p = sub.add_parser(name)
        p.add_argument('--origin',required=True)
        if name == 'capture':
            p.add_argument('--actions',type=Path,required=True)
            p.add_argument('--mutations-approved',action='store_true')
        else:
            p.add_argument('--max-pages',type=int,default=5)
        p.add_argument('--fixture-root',type=Path)
        p.add_argument('--execute-authorized',action='store_true')
        p.add_argument('--allow-nonlocal',action='store_true')
        p.add_argument('--viewport-width',type=int,default=1280)
        p.add_argument('--viewport-height',type=int,default=720)
        p.add_argument('--browser-executable',type=Path)
        p.add_argument('--screenshot',type=Path)
        p.add_argument('--include-text',action='store_true')
        p.add_argument('-o','--output',required=True,type=Path)
    a=parser.parse_args(argv)
    try:
        if a.command == 'detect':
            print(json.dumps(browser_capabilities(),sort_keys=True))
            return 0
        actions = checked_actions(a.actions) if a.command == 'capture' else None
        protected = ([a.actions] if a.command == 'capture' else [])
        if a.screenshot:
            if a.output.resolve() == a.screenshot.resolve():
                raise DataError('output aliases screenshot')
            protected.append(a.screenshot)
        if any(a.output.resolve() == x.resolve() for x in protected):
            raise DataError('output aliases input')
        result = inspect_browser(mode=a.command,origin=a.origin,actions=actions,
                                 fixture_root=a.fixture_root,authorized=a.execute_authorized,
                                 mutations_approved=getattr(a,'mutations_approved',False),
                                 allow_nonlocal=a.allow_nonlocal,
                                 max_pages=getattr(a,'max_pages',5), viewport_width=a.viewport_width,
                                 viewport_height=a.viewport_height, screenshot=a.screenshot,
                                 include_text=a.include_text,browser_executable=a.browser_executable)
        write_exclusive(a.output,json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n',protected)
        return 0
    except (ValueError,OSError) as exc:
        print(json.dumps({'error':str(exc)}),file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
