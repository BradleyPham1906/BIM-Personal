#!/usr/bin/env python3
"""check_runtime.py -- the Ladybug analyses' runtime is exactly what runtime/MANIFEST.json pins (V172b).

  python3 tools/check_runtime.py

runtime/ holds Pyodide 0.29.5's core files and the four Ladybug wheels, committed so that the site and the suites
never depend on npm or PyPI (the owner, 2026-10-31; reference/research-ladybug-weather-comfort.md). Each file must
be in the manifest with its size and SHA-256, and nothing else may be in the folder: the bytes the suites ran are
the bytes Pages serves. Exits 1, naming each fault, otherwise prints the count and the total. build_site.py runs it
before it copies the folder, and the Pages workflow refuses to publish a runtime that does not match."""
import hashlib, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
RT = ROOT / 'runtime'


def check():
    faults = []
    try:
        m = json.loads((RT / 'MANIFEST.json').read_text(encoding='utf-8'))
    except (OSError, ValueError) as e:
        return ['runtime/MANIFEST.json cannot be read: %s' % e], 0, 0
    want = {f['path']: f for f in m.get('files', [])}
    have = {p.relative_to(RT).as_posix() for p in RT.rglob('*') if p.is_file()} - {'MANIFEST.json'}
    for rel in sorted(have - set(want)):
        faults.append('runtime/%s is not in the manifest' % rel)
    total = 0
    for rel, f in sorted(want.items()):
        p = RT / rel
        if not p.is_file():
            faults.append('runtime/%s is missing' % rel)
            continue
        b = p.read_bytes()
        total += len(b)
        if len(b) != f['bytes']:
            faults.append('runtime/%s is %d bytes, the manifest says %d' % (rel, len(b), f['bytes']))
        h = hashlib.sha256(b).hexdigest()
        if h != f['sha256']:
            faults.append('runtime/%s has SHA-256 %s, the manifest says %s' % (rel, h, f['sha256']))
    return faults, len(want), total


def main():
    faults, n, total = check()
    if faults:
        print('\n'.join(faults))
        sys.exit(1)
    print('runtime/ is what its manifest pins: %d files, %d bytes' % (n, total))


if __name__ == '__main__':
    main()
