"""Validate an explicitly selected local-live HTML artifact before granting access.

This validates a portable HTML contract and byte consistency, not code authorship.
It never downloads assets, executes HTML or imports a particular viewer package.
"""
from __future__ import annotations

import base64
import hashlib
from html.parser import HTMLParser
from pathlib import Path
import re

SESSION_SLOT = '<script id="local-graph-session" type="application/json">{}</script>'
MAX_VIEWER_BYTES = 64 * 1024 * 1024
REQUIRED_POLICY = {
    'default-src': ["'none'"], 'base-uri': ["'none'"],
    'script-src-attr': ["'none'"], 'style-src': ["'unsafe-inline'"],
    'img-src': ['data:', 'blob:'], 'font-src': ["'none'"],
    'connect-src': ["'self'"], 'object-src': ["'none'"],
    'frame-src': ["'none'"], 'worker-src': ["'none'"],
    'media-src': ["'none'"], 'form-action': ["'none'"],
}


class LiveViewerParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.policies = []
        self.profiles = []
        self.versions = []
        self.scripts = []
        self.sessions = []
        self.active_script = None
        self.charset = []
        self.in_head = False

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if len(values) != len(attrs):
            raise ValueError('Duplicate HTML attributes are not supported in local-live artifacts')
        if tag == 'head':
            self.in_head = True
        if not self.policies and tag not in ('html', 'head', 'meta'):
            raise ValueError('The local-live policy must precede scripts and all active content')
        if any(key.startswith('on') for key in values):
            raise ValueError('Inline HTML event handlers are not permitted in local-live artifacts')
        if tag in ('base', 'iframe', 'frame', 'object', 'embed', 'link', 'form'):
            raise ValueError(f'Unsupported active HTML element in local-live artifact: {tag}')
        for key in ('src', 'href', 'action', 'formaction', 'poster', 'data', 'srcset', 'ping'):
            value = values.get(key)
            if value and not value.startswith(('#', 'data:', 'blob:')):
                raise ValueError('External or relative resource URLs are not permitted in local-live HTML')
        if tag == 'meta':
            kind = (values.get('http-equiv') or '').lower()
            if kind == 'content-security-policy':
                if not self.in_head:
                    raise ValueError('The Content Security Policy must be in the document head')
                self.policies.append(values.get('content') or '')
            elif kind == 'refresh':
                raise ValueError('Meta refresh is not permitted in local-live HTML')
            if values.get('name') == 'local-graph-security-profile':
                self.profiles.append(values.get('content'))
            if values.get('name') == 'local-graph-runtime-version':
                self.versions.append(values.get('content'))
            if 'charset' in values:
                self.charset.append((values['charset'] or '').lower())
        if tag == 'script':
            if self.active_script is not None or 'src' in values:
                raise ValueError('Nested or external scripts are not permitted in local-live HTML')
            kind = (values.get('type') or '').lower()
            if kind not in ('', 'application/json'):
                raise ValueError('Only classic inline scripts and JSON data slots are supported')
            self.active_script = [values, []]

    def handle_endtag(self, tag):
        if tag == 'head':
            self.in_head = False
        if tag == 'script' and self.active_script is not None:
            attrs, parts = self.active_script
            body = ''.join(parts)
            if attrs.get('id') == 'local-graph-session':
                if attrs.get('type') != 'application/json' or body != '{}':
                    raise ValueError('The session slot must be empty inert JSON before serving')
                self.sessions.append(body)
            elif not attrs.get('type'):
                self.scripts.append(body)
            self.active_script = None

    def handle_data(self, data):
        if self.active_script is not None:
            self.active_script[1].append(data)


def validate_live_viewer(viewer: Path, expected_sha256: str | None = None) -> tuple[str, str, str]:
    """Return normalized page, policy and raw-byte identity; never grant authority."""
    viewer = Path(viewer)
    if viewer.is_symlink() or not viewer.is_file():
        raise ValueError('Viewer must be a regular local HTML file, not a symbolic link')
    with viewer.open('rb') as source:
        raw = source.read(MAX_VIEWER_BYTES + 1)
    if len(raw) > MAX_VIEWER_BYTES:
        raise ValueError('Viewer exceeds the 64 MiB byte budget')
    digest = hashlib.sha256(raw).hexdigest()
    if expected_sha256 is not None:
        if not re.fullmatch(r'[0-9a-fA-F]{64}', expected_sha256) or digest != expected_sha256.lower():
            raise ValueError('Viewer SHA-256 mismatch; server was not started')
    page = raw.decode('utf-8').replace('\r\n', '\n').replace('\r', '\n')
    parser = LiveViewerParser()
    parser.feed(page)
    parser.close()
    if parser.profiles != ['local-live'] or parser.versions != ['1']:
        raise ValueError('Serving requires explicit local-live HTML runtime v1; regenerate with --security-profile local-live. Offline/custom pages are not upgraded')
    if parser.charset != ['utf-8'] or len(parser.policies) != 1:
        raise ValueError('The local-live viewer must declare UTF-8 and exactly one early CSP')
    if parser.active_script is not None or len(parser.sessions) != 1 or page.count(SESSION_SLOT) != 1:
        raise ValueError('The local-live viewer must contain exactly one empty canonical session slot')
    directives = {}
    for raw_directive in parser.policies[0].split(';'):
        parts = raw_directive.split()
        if not parts:
            continue
        if parts[0] in directives:
            raise ValueError('Duplicate CSP directives are not supported')
        directives[parts[0]] = parts[1:]
    if set(directives) != set(REQUIRED_POLICY) | {'script-src'}:
        raise ValueError('Unsupported or missing local-live CSP directives')
    for name, values in REQUIRED_POLICY.items():
        if directives.get(name) != values:
            raise ValueError(f'Unsafe local-live CSP directive: {name}')
    expected_hashes = {"'sha256-" + base64.b64encode(hashlib.sha256(body.encode('utf-8')).digest()).decode('ascii') + "'" for body in parser.scripts}
    if not expected_hashes or set(directives['script-src']) != expected_hashes:
        raise ValueError('Inline script hashes do not match the local-live CSP; regenerate the viewer')
    return page, parser.policies[0], digest
