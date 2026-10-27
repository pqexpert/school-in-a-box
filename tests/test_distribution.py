import hashlib
import http.client
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import threading
import unittest
import zipfile

from scripts.build import ROOT, catalog, rendered_catalog
from scripts.package import package
from server import make_server


class DistributionTests(unittest.TestCase):
    def test_catalog_matches_sources_and_teaching_pairs(self):
        self.assertEqual((ROOT / 'web/catalog.json').read_text(encoding='utf-8'), rendered_catalog())
        data = catalog()
        self.assertEqual(len(data['campuses']), 4)
        lessons = [d for d in data['documents'] if d['collection'] != 'planning']
        self.assertEqual(len(lessons), 8)
        for week in (1, 2):
            for language in ('amdo', 'english'):
                self.assertEqual({d['collection'] for d in lessons if d['week'] == week and d['language'] == language}, {'student', 'teacher'})

    def test_public_material_has_no_private_recovery_identifiers(self):
        data = rendered_catalog()
        for pattern in [r'docs\.google\.com', r'drive\.google\.com', r'/home/',
                        r'AIza[0-9A-Za-z_-]{20,}', r'gh[pousr]_[0-9A-Za-z]{20,}',
                        r'-----BEGIN .*PRIVATE KEY-----', r'RBO-97', r'12120']:
            self.assertIsNone(re.search(pattern, data), pattern)
        self.assertTrue(all('review_status' in d for d in catalog()['documents']))

    def test_offline_web_assets_are_local(self):
        html = (ROOT / 'web/index.html').read_text(encoding='utf-8')
        for value in re.findall(r'(?:src|href)="([^"]+)"', html):
            if value.startswith(('#', 'https://')):
                continue
            target = value.removeprefix('./')
            if target in ('LICENSE', 'LICENSE-CONTENT.md'):
                self.assertTrue((ROOT / target).is_file())
            else:
                self.assertTrue((ROOT / 'web' / target).is_file(), value)
        self.assertNotRegex(html, r'<(?:script|link)[^>]+(?:src|href)="https?://')

    def test_static_export_is_complete_and_preserves_existing_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'site'
            result = subprocess.run([sys.executable, 'scripts/build.py', '--output', str(output)], cwd=ROOT, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((output / 'index.html').is_file())
            for doc in catalog()['documents']:
                self.assertTrue((output / doc['path']).is_file())
            self.assertEqual(json.loads((output / 'catalog.json').read_text(encoding='utf-8')), catalog())
            again = subprocess.run([sys.executable, 'scripts/build.py', '--output', str(output)], cwd=ROOT, capture_output=True)
            self.assertNotEqual(again.returncode, 0)

    def test_offline_package_is_reproducible_and_contains_only_public_paths(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            one, two = package('v0.1.0', Path(a)), package('v0.1.0', Path(b))
            self.assertEqual(one.read_bytes(), two.read_bytes())
            with zipfile.ZipFile(one) as archive:
                names = archive.namelist()
                for forbidden in ['/home/', '.env', '.git/', 'notes.json', 'recovery-receipt', '.playwright', '__pycache__']:
                    self.assertFalse(any(forbidden in name for name in names), forbidden)
                for expected in ['server.py', 'README.md', 'LICENSE', 'LICENSE-CONTENT.md', 'web/catalog.json', 'content/campuses.json']:
                    self.assertIn('school-in-a-box-v0.1.0/' + expected, names)
            digest = hashlib.sha256(one.read_bytes()).hexdigest()
            self.assertTrue((Path(a) / 'SHA256SUMS').read_text().startswith(digest))

    def test_cli_rejects_implicit_lan_sharing(self):
        result = subprocess.run([sys.executable, 'server.py', '--bind', '0.0.0.0'], cwd=ROOT, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b'--allow-host', result.stderr)


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = make_server(port=0, allowed_hosts=['school.local'])
        cls.worker = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.worker.start()
        cls.port = cls.server.server_port

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.worker.join()

    def request(self, path, method='GET', host=None):
        connection = http.client.HTTPConnection('127.0.0.1', self.port)
        connection.request(method, path, headers={'Host': host or f'localhost:{self.port}'})
        response = connection.getresponse()
        result = response.status, dict(response.getheaders()), response.read()
        connection.close()
        return result

    def test_read_public_documents_and_headers(self):
        for path in ['/', '/catalog.json', '/app.js', '/style.css', '/LICENSE', '/content/lessons/week-01-amdo-student.md']:
            status, headers, body = self.request(path)
            self.assertEqual(status, 200, path)
            self.assertTrue(body)
            self.assertEqual(headers['X-Content-Type-Options'], 'nosniff')
            self.assertIn("frame-ancestors 'none'", headers['Content-Security-Policy'])
        self.assertEqual(self.request('/', host=f'school.local:{self.port}')[0], 200)

    def test_host_boundary(self):
        for host in [f'attacker.example:{self.port}', 'localhost', f'localhost:{self.port}@attacker.example']:
            self.assertEqual(self.request('/', host=host)[0], 403)

    def test_source_and_traversal_are_not_served(self):
        for path in ['/server.py', '/.git/config', '/content/../server.py', '/%2e%2e/server.py', '//server.py', '/docs/PROVENANCE.md']:
            self.assertEqual(self.request(path)[0], 404, path)

    def test_head_and_readonly_methods(self):
        self.assertEqual(self.request('/', method='HEAD')[2], b'')
        for method in ['POST', 'PUT', 'DELETE']:
            self.assertEqual(self.request('/catalog.json', method=method)[0], 501)


if __name__ == '__main__':
    unittest.main()
