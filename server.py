#!/usr/bin/env python3
"""Serve the School in a Box library without accounts or write endpoints."""
import argparse
from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import ipaddress
from pathlib import Path
from urllib.parse import urlsplit

from scripts.build import catalog, rendered_catalog

ROOT = Path(__file__).resolve().parent


def routes():
    result = {'/': ('web/index.html', 'text/html; charset=utf-8')}
    for filename, mime in [('app.js', 'text/javascript'), ('style.css', 'text/css'),
                           ('catalog.json', 'application/json'), ('favicon.svg', 'image/svg+xml')]:
        result['/' + filename] = ('web/' + filename, mime + '; charset=utf-8')
    for name in ['LICENSE', 'LICENSE-CONTENT.md']:
        result['/' + name] = (name, 'text/plain; charset=utf-8')
    for d in catalog()['documents']:
        result['/' + d['path']] = (d['path'], 'text/plain; charset=utf-8')
    return result


class Handler(BaseHTTPRequestHandler):
    def __init__(self, *args, allowed_hosts, public_routes, **kwargs):
        self.allowed_hosts = allowed_hosts
        self.public_routes = public_routes
        super().__init__(*args, **kwargs)

    def do_HEAD(self):
        self.respond(head=True)

    def do_GET(self):
        self.respond()

    def respond(self, head=False):
        hosts = self.headers.get_all('Host', [])
        allowed = {f'{host}:{self.server.server_port}' for host in self.allowed_hosts}
        if self.server.server_port == 80:
            allowed |= self.allowed_hosts
        if len(hosts) != 1 or hosts[0].lower() not in allowed:
            self.send_error(403, 'Host is not allowed')
            return
        if not self.path.startswith('/') or self.path.startswith('//'):
            self.send_error(404)
            return
        route = self.public_routes.get(urlsplit(self.path).path)
        if route is None:
            self.send_error(404)
            return
        body = (ROOT / route[0]).read_bytes()
        self.send_response(200)
        self.send_header('Content-Type', route[1])
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
        self.end_headers()
        if not head:
            self.wfile.write(body)


def make_server(bind='127.0.0.1', port=8080, allowed_hosts=()):
    handler = partial(Handler, allowed_hosts={'localhost', '127.0.0.1', *allowed_hosts}, public_routes=routes())
    return ThreadingHTTPServer((bind, port), handler)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bind', default='127.0.0.1', help='IPv4 address; defaults to loopback')
    parser.add_argument('--port', type=int, default=8080)
    parser.add_argument('--allow-host', action='append', default=[], help='Explicit LAN hostname or IPv4 address, without port; repeat as needed')
    args = parser.parse_args()
    try:
        address = ipaddress.IPv4Address(args.bind)
    except ipaddress.AddressValueError:
        parser.error('--bind must be an IPv4 address')
    if not 1 <= args.port <= 65535:
        parser.error('--port must be between 1 and 65535')
    if not address.is_loopback and not args.allow_host:
        parser.error('LAN binding requires at least one explicit --allow-host')
    import re
    if any(not re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?', h) for h in args.allow_host):
        parser.error('--allow-host expects a hostname or IPv4 address without scheme, path or port')
    if (ROOT / 'web/catalog.json').read_text(encoding='utf-8') != rendered_catalog():
        parser.error('Catalog is stale. Run python3 scripts/build.py first.')
    with make_server(args.bind, args.port, [h.lower() for h in args.allow_host]) as server:
        print(f'School in a Box: http://127.0.0.1:{args.port} — Ctrl+C to stop', flush=True)
        if not address.is_loopback:
            print('LAN sharing enabled for explicit hosts; all course content and answer keys are public.', flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()
