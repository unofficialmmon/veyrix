#!/usr/bin/env python3
"""Offline integrity/selection checks. Does not certify upstream code or host use."""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from veyrix.common import HASH, ID, SHA, Error, digest, encoded, load_json, load_yaml, require, safe_rel


def check(root: Path) -> dict:
    catalog = load_json((root/'catalog/skills.json').read_bytes())
    entries = catalog['skills']
    migration = load_json((root/'catalog/migration.json').read_bytes())
    require(catalog['schema'] == migration['schema'] == 1, 'SCHEMA', 'Unsupported catalog schema')
    require(len(migration['decisions']) == 95, 'MIGRATION', 'Migration inventory must cover the reviewed 95 IDs')
    roots = {p.name for p in (root/'skills').iterdir()}
    require(roots == set(entries), 'CATALOG', 'Catalog and source directories differ')
    count = 0
    size = 0
    for name, entry in entries.items():
        require(bool(ID.fullmatch(name)), 'ID', name)
        require(entry['path'] == 'skills/' + name, 'PATH', name)
        folder = root/entry['path']
        paths = list(folder.rglob('*'))
        require(not any(p.is_symlink() for p in paths), 'SYMLINK', name)
        actual = {p.relative_to(folder).as_posix() for p in paths if p.is_file()}
        require(actual == set(entry['files']), 'INVENTORY', name)
        require(set(entry['files']) == set(entry['original_files']) | set(entry['supplements']), 'ORIGIN', name)
        require(any(Path(p).name.lower().startswith('license') for p in actual), 'LICENSE', name)
        require(SHA.fullmatch(entry['origin']['commit']) is not None, 'ORIGIN', name)
        for rel, expected in entry['files'].items():
            safe_rel(rel)
            data = (folder/rel).read_bytes()
            require(HASH.fullmatch(expected) is not None and digest(data) == expected, 'HASH', name+'/'+rel)
            require(expected == entry['original_files'].get(rel, entry['supplements'].get(rel, {}).get('sha256')), 'ORIGIN', name+'/'+rel)
            count += 1; size += len(data)
        text = (folder/'SKILL.md').read_text()
        front = load_yaml(text.split('---',2)[1])
        require(front['name'] == name and isinstance(front['description'],str), 'FRONTMATTER', name)
        require(entry['status'] in ('available','conditional'), 'STATUS', name)
        require(entry['host_runtime'] == 'NOT_RUN', 'EVIDENCE', 'Do not invent host PASS')
    reachable = set()
    for folder in ('profiles','addons'):
        for path in sorted((root/folder).glob('*.json')):
            spec = load_json(path.read_bytes())
            require(spec['schema'] == 1 and isinstance(spec['roles'],dict), 'PROFILE', path.name)
            for role, names in spec['roles'].items():
                require(role in ('fixer','designer','oracle','librarian'), 'ROLE', role)
                require(names == sorted(set(names)), 'PROFILE', path.name+' IDs must be unique/sorted')
                require(set(names) <= set(entries), 'PROFILE', path.name+' references unknown IDs')
                if folder == 'profiles':
                    require(all(entries[n]['status'] == 'available' for n in names), 'PROFILE', 'Conditional IDs must remain opt-in add-ons')
                reachable.update(names)
    require(reachable == set(entries), 'PROFILE', 'Unreachable catalog entries')
    kept = {n for n,e in migration['decisions'].items() if e['decision'] == 'KEEP'}
    require(kept == set(entries) - {'emil-design-eng'}, 'MIGRATION', 'KEEP decisions differ from catalog')
    require(all(e['decision'] in ('KEEP','EXCLUDE','DEFER') and e.get('reason') for e in migration['decisions'].values()),
            'MIGRATION', 'Every decision needs a reason')
    for name in ('setup','sync','audit'):
        text = (root/'commands'/f'veyrix-{name}.md').read_text()
        require(text.startswith('---\n') and '$ARGUMENTS' in text, 'COMMAND', name)
    require(not (root/'.apm').exists(), 'SCOPE', 'No APM mirrors in Veyrix')
    return {'result':'PASS','skills':len(entries),'files':count,'bytes':size,
            'profiles':len(list((root/'profiles').glob('*.json'))),
            'addons':len(list((root/'addons').glob('*.json'))),
            'conditional':[n for n,e in entries.items() if e['status']=='conditional'],
            'origins':dict(Counter(e['upstream']['sourceType'] for e in entries.values())),
            'migration':dict(Counter(e['decision'] for e in migration['decisions'].values())),
            'host_runtime':'NOT_RUN'}


if __name__ == '__main__':
    try:
        print(encoded(check(Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[1])).decode(),end='')
    except (Error,KeyError,ValueError,OSError,TypeError) as exc:
        print(json.dumps({'result':'FAIL','message':str(exc)}));raise SystemExit(1)
