#!/usr/bin/env python3
"""Create a deterministic offline source distribution from explicit public paths."""
import argparse
import hashlib
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIRS = ['web', 'content', 'docs', 'scripts', 'tests', '.github']
PUBLIC_FILES = ['README.md', 'LICENSE', 'LICENSE-CONTENT.md', 'CONTRIBUTING.md',
                'CODE_OF_CONDUCT.md', 'SECURITY.md', 'server.py', '.gitignore']


def package(version, output):
    if not re.fullmatch(r'v\d+\.\d+\.\d+(?:-[a-z0-9.-]+)?', version):
        raise ValueError('Use a semantic version such as v0.1.0')
    from scripts.build import rendered_catalog
    if (ROOT / 'web/catalog.json').read_text(encoding='utf-8') != rendered_catalog():
        raise ValueError('Catalog is stale; run scripts/build.py')
    output.mkdir(parents=True, exist_ok=True)
    dest = output / f'school-in-a-box-{version}.zip'
    candidates = [ROOT / f for f in PUBLIC_FILES]
    for directory in PUBLIC_DIRS:
        candidates.extend(p for p in (ROOT / directory).rglob('*') if p.is_file()
                          and '__pycache__' not in p.parts and p.suffix not in ('.pyc', '.pyo'))
    with zipfile.ZipFile(dest, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(candidates):
            if path.is_symlink():
                raise ValueError('Symlinks are not distributable')
            relative = path.relative_to(ROOT).as_posix()
            info = zipfile.ZipInfo(f'school-in-a-box-{version}/{relative}', (2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, path.read_bytes())
    digest = hashlib.sha256(dest.read_bytes()).hexdigest()
    (output / 'SHA256SUMS').write_text(f'{digest}  {dest.name}\n', encoding='utf-8')
    return dest


if __name__ == '__main__':
    import sys
    sys.path.insert(0, str(ROOT))
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', required=True)
    parser.add_argument('--output', type=Path, default=ROOT / 'dist')
    args = parser.parse_args()
    print(package(args.version, args.output))
