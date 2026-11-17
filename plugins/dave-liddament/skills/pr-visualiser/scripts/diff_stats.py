#!/usr/bin/env python3
"""Summarise a unified diff (read from stdin) for a PR explainer page.

Usage:
    git diff -M <base> <head> | python3 diff_stats.py --summary
    git diff -M <base> <head> | python3 diff_stats.py --bars
    git diff --merge-base master | python3 diff_stats.py            # full JSON

Modes:
    (default)   JSON: per-file stats (path, status, added, removed, kind, group,
                generated) plus totals by kind and by group.
    --summary   A short human-readable digest: totals, by kind, by group, and
                every added / deleted / renamed file. Read this first.
    --bars      Ready-to-paste `.bar-row` HTML for the template's "Where the
                lines went" section: one block per kind (src, test, fixture,
                docs, ...), rows sorted largest first, widths on one shared scale.

Kinds: src, test (test code), fixture (test data: JSON/XML/text under test
dirs, snapshots), docs, ci, deps, config. Generated files (lockfiles, vendored
code, minified bundles, snapshots) are flagged and left out of --bars.
"""
import argparse
import html
import json
import re
import sys
from collections import OrderedDict

DIFF_HEADER = re.compile(r'^diff --git a/(.*?) b/(.*)$')

LOCKFILES = {
    'composer.lock', 'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
    'Gemfile.lock', 'poetry.lock', 'Cargo.lock', 'go.sum', 'uv.lock',
}
DEP_MANIFESTS = {
    'composer.json', 'package.json', 'Gemfile', 'pyproject.toml',
    'requirements.txt', 'Cargo.toml', 'go.mod',
}
CODE_EXT = re.compile(r'\.(php|py|js|jsx|ts|tsx|rb|go|rs|java|kt|cs|swift|scala|c|cc|cpp|h|hpp|m|ex|exs|sh)$', re.I)
TEST_DIR = re.compile(r'(^|/)(tests?|spec|specs|__tests__|testing)(/|$)', re.I)
FIXTURE_DIR = re.compile(r'(^|/)(fixtures?|resources|testdata|test-data|__snapshots__|snapshots|stubs|data)(/|$)', re.I)
TEST_FILE = re.compile(r'(Test|_test|\.test|\.spec|Spec)\.[A-Za-z]+$')
KIND_ORDER = ['src', 'test', 'fixture', 'docs', 'config', 'ci', 'deps']


def classify(path: str) -> str:
    name = path.rsplit('/', 1)[-1]
    lower = path.lower()
    if name in LOCKFILES or name in DEP_MANIFESTS:
        return 'deps'
    if lower.startswith(('.github/', '.gitlab', '.circleci/')) or name in {
        'Dockerfile', 'docker-compose.yml', 'docker-compose.yaml', 'compose.yaml', 'Makefile', '.travis.yml',
    }:
        return 'ci'
    in_test_tree = bool(TEST_DIR.search(path))
    if in_test_tree or TEST_FILE.search(path):
        if CODE_EXT.search(path) and not FIXTURE_DIR.search(path):
            return 'test'
        return 'fixture' if in_test_tree else 'test'
    if lower.endswith(('.md', '.rst', '.adoc')) or lower.startswith('docs/'):
        return 'docs'
    if not CODE_EXT.search(path):
        return 'config'
    return 'src'


def is_generated(path: str) -> bool:
    name = path.rsplit('/', 1)[-1]
    return (
        name in LOCKFILES
        or '/vendor/' in f'/{path}'
        or '/node_modules/' in f'/{path}'
        or name.endswith(('.min.js', '.min.css', '.map', '.snap'))
        or '/dist/' in f'/{path}'
    )


def group_of(path: str, depth: int) -> str:
    parts = path.split('/')[:-1]
    return '/'.join(parts[:depth]) if parts else '(root)'


def parse(stream, depth: int):
    files = []
    cur = None
    for line in stream:
        line = line.rstrip('\n')
        m = DIFF_HEADER.match(line)
        if m:
            cur = {'path': m.group(2), 'old_path': m.group(1), 'status': 'modified',
                   'added': 0, 'removed': 0, 'binary': False}
            files.append(cur)
            continue
        if cur is None:
            continue
        if line.startswith('new file mode'):
            cur['status'] = 'added'
        elif line.startswith('deleted file mode'):
            cur['status'] = 'deleted'
        elif line.startswith('rename from'):
            cur['status'] = 'renamed'
        elif line.startswith('Binary files'):
            cur['binary'] = True
        elif line.startswith('+++') or line.startswith('---'):
            continue
        elif line.startswith('+'):
            cur['added'] += 1
        elif line.startswith('-'):
            cur['removed'] += 1

    for f in files:
        if f['status'] != 'renamed' or f['old_path'] == f['path']:
            f.pop('old_path')
        f['kind'] = classify(f['path'])
        f['group'] = group_of(f['path'], depth)
        f['generated'] = is_generated(f['path'])

    def totals(key, rows):
        out = OrderedDict()
        for f in sorted(rows, key=lambda x: x[key]):
            t = out.setdefault(f[key], {'files': 0, 'added': 0, 'removed': 0})
            t['files'] += 1
            t['added'] += f['added']
            t['removed'] += f['removed']
        return out

    return {
        'files': files,
        'totals': {
            'files': len(files),
            'added': sum(f['added'] for f in files),
            'removed': sum(f['removed'] for f in files),
        },
        'by_kind': totals('kind', files),
        'by_group': totals('group', files),
    }


def summary(d) -> str:
    t = d['totals']
    out = [f"{t['files']} files, +{t['added']} -{t['removed']}", '', 'By kind:']
    for k in sorted(d['by_kind'], key=lambda k: KIND_ORDER.index(k) if k in KIND_ORDER else 99):
        v = d['by_kind'][k]
        out.append(f"  {k:<8} {v['files']:>4} files  +{v['added']} -{v['removed']}")
    out += ['', 'By group:']
    for k, v in sorted(d['by_group'].items(), key=lambda kv: -(kv[1]['added'] + kv[1]['removed'])):
        out.append(f"  {k:<50} {v['files']:>3} files  +{v['added']} -{v['removed']}")
    notable = [f for f in d['files'] if f['status'] != 'modified' or f['generated']]
    if notable:
        out += ['', 'Added / deleted / renamed / generated:']
        for f in notable:
            extra = f" (from {f['old_path']})" if 'old_path' in f else ''
            gen = ' [generated]' if f['generated'] else ''
            out.append(f"  {f['status']:<8} {f['kind']:<8} +{f['added']} -{f['removed']}  {f['path']}{extra}{gen}")
    return '\n'.join(out) + '\n'


def bars(d, depth: int) -> str:
    """One block per kind, rows per group, all widths on one shared scale."""
    rows_by_kind = OrderedDict()
    for f in d['files']:
        if f['generated']:
            continue
        g = rows_by_kind.setdefault(f['kind'], OrderedDict()).setdefault(f['group'], {'added': 0, 'removed': 0})
        g['added'] += f['added']
        g['removed'] += f['removed']
    all_rows = [v for groups in rows_by_kind.values() for v in groups.values()]
    if not all_rows:
        return '<!-- no non-generated changes -->\n'
    scale = max(r['added'] + r['removed'] for r in all_rows) or 1
    names = {'src': 'Source', 'test': 'Tests', 'fixture': 'Test fixtures', 'docs': 'Docs',
             'config': 'Config', 'ci': 'CI', 'deps': 'Dependencies'}
    out = ['<div class="bars">']
    for kind in sorted(rows_by_kind, key=lambda k: KIND_ORDER.index(k) if k in KIND_ORDER else 99):
        groups = rows_by_kind[kind]
        ta = sum(g['added'] for g in groups.values())
        tr = sum(g['removed'] for g in groups.values())
        out.append(f'  <h3>{names.get(kind, kind)} · +{ta} −{tr}</h3>')
        for name, g in sorted(groups.items(), key=lambda kv: -(kv[1]['added'] + kv[1]['removed'])):
            a = g['added'] / scale * 100
            r = g['removed'] / scale * 100
            out.append(
                f'  <div class="bar-row"><span class="label">{html.escape(name)}</span>'
                f'<span class="track"><span class="a" style="width:{a:.1f}%"></span>'
                f'<span class="r" style="width:{r:.1f}%"></span></span>'
                f'<span class="n">+{g["added"]} −{g["removed"]}</span></div>'
            )
    out.append('</div>')
    return '\n'.join(out) + '\n'


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--depth', type=int, default=2, help='directory segments used for grouping (default 2)')
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument('--summary', action='store_true', help='short human-readable digest')
    mode.add_argument('--bars', action='store_true', help='ready-to-paste .bar-row HTML')
    args = ap.parse_args()
    d = parse(sys.stdin, args.depth)
    if args.summary:
        sys.stdout.write(summary(d))
    elif args.bars:
        sys.stdout.write(bars(d, args.depth))
    else:
        json.dump(d, sys.stdout, indent=2)
        sys.stdout.write('\n')


if __name__ == '__main__':
    main()
