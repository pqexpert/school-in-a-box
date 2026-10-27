#!/usr/bin/env python3
"""Validate educational sources and build a portable catalog/static site."""
import argparse
import json
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def unique(records, label):
    ids = [record['id'] for record in records]
    if len(ids) != len(set(ids)) or not all(re.fullmatch(r'[a-z0-9-]+', i) for i in ids):
        raise ValueError(f'{label}: IDs must be unique lowercase slugs')


def catalog():
    campuses = load('content/campuses.json')
    courses = load('content/courses.json')
    lessons = load('content/lessons/index.json')
    school = load('content/school/index.json')
    for records, label in [(campuses, 'campuses'), (courses, 'courses'), (lessons + school, 'documents')]:
        if not records:
            raise ValueError(f'{label}: empty collection')
        unique(records, label)
    by_course = {c['id']: c for c in courses}
    for campus in campuses:
        for key in ['name', 'context', 'rhythm']:
            if not campus.get(key):
                raise ValueError(f'Campus missing {key}')
    documents = []
    for source in lessons + school:
        d = dict(source)
        path = Path(d['path'])
        if path.is_absolute() or '..' in path.parts or path.suffix != '.md' or path.parts[:2] not in [('content', 'lessons'), ('content', 'school')]:
            raise ValueError(f'Invalid content path: {path}')
        resolved = (ROOT / path).resolve()
        if not resolved.is_relative_to(ROOT / 'content'):
            raise ValueError('Content cannot escape content directory')
        body = resolved.read_text(encoding='utf-8')
        if not body.strip() or not d.get('review_status'):
            raise ValueError(f'Empty or unreviewed content: {path}')
        if source in lessons:
            course = by_course[d['course']]
            if d['collection'] not in ('student', 'teacher') or d['language'] not in ('amdo', 'english'):
                raise ValueError(f'Invalid lesson facing: {path}')
            if d['week'] not in [w['number'] for w in course['weeks']]:
                raise ValueError(f'Unknown course week: {path}')
            levels = {level['id'] for level in course['levels']}
            if not d['levels'] or not set(d['levels']) <= levels:
                raise ValueError(f'Unknown course level: {path}')
        else:
            d['collection'] = 'planning'
        d['content'] = body
        d['license'] = 'CC-BY-4.0'
        documents.append(d)
    return {'version': '0.1.0', 'campuses': campuses, 'courses': courses,
            'documents': sorted(documents, key=lambda d: d['id'])}


def rendered_catalog():
    return json.dumps(catalog(), ensure_ascii=False, indent=2) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Fail if checked-in catalog is stale')
    parser.add_argument('--output', type=Path, help='Write a new static site directory; refuses existing paths')
    args = parser.parse_args()
    rendered = rendered_catalog()
    target = ROOT / 'web/catalog.json'
    if args.check:
        if not target.exists() or target.read_text(encoding='utf-8') != rendered:
            parser.error('Catalog is stale. Run python3 scripts/build.py')
    else:
        target.write_text(rendered, encoding='utf-8')
    if args.output:
        if args.output.exists():
            parser.error('Output already exists. Choose a new directory to preserve existing files.')
        args.output.mkdir(parents=True)
        (args.output / '.nojekyll').touch()
        for name in ['index.html', 'app.js', 'style.css', 'favicon.svg', 'catalog.json']:
            shutil.copyfile(ROOT / 'web' / name, args.output / name)
        shutil.copytree(ROOT / 'content', args.output / 'content')
        for name in ['LICENSE', 'LICENSE-CONTENT.md']:
            shutil.copyfile(ROOT / name, args.output / name)
    print('Catalog validated' + (f'; static site written to {args.output}' if args.output else ''))


if __name__ == '__main__':
    main()
