"""make_seed_survey.py -- write the seed survey datasets for V138's checks, with known faults planted.

Each dataset is a survey text file and a JSON sidecar saying how to read it and what its check must
find. tests/bim_phase138_survey_check_browser_tests.py reads every sidecar in tests/data/surveys/ and
holds the app to it, so a real survey added there with its own sidecar is checked on every change.

The ground is a smooth function, so every elevation is known exactly:
    z = 100 + 0.05 dE + 0.02 dN + 2 sin(dE / 40) cos(dN / 50)   (metres; dE, dN from 2000 E, 5000 N)

seed_site_m       PNEZD, metres, a 15 x 15 grid at 10 m, with:
                  a header line, a note (skipped silently), a mistyped line (2040.0O), a duplicate
                  (point 300 where point 12 is), a bust shot (point 88, 3 m high), six check shots
                  coded CHK, and two control points
seed_site_usft    the same ground, PENZD, in US survey feet, no faults: every check passes

Usage: python3 tools/make_seed_survey.py [out_dir]   (default tests/data/surveys)
"""
import json, math, pathlib, sys

OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parent.parent / 'tests/data/surveys'
N0, E0 = 5000.0, 2000.0
USFT = 1200 / 3937


def z_at(e, n):
    de, dn = e - E0, n - N0
    return 100 + 0.05 * de + 0.02 * dn + 2 * math.sin(de / 40) * math.cos(dn / 50)


def grid():
    pts, k = [], 1
    for i in range(15):
        for j in range(15):
            n, e = N0 + 10 * i, E0 + 10 * j
            pts.append([str(k), n, e, z_at(e, n), 'GND'])
            k += 1
    return pts


CHECKS = [(23.4, 31.7), (57.2, 88.1), (91.9, 12.6), (104.3, 66.6), (128.8, 121.4), (36.6, 133.3)]
NOISE = [0.012, -0.008, 0.005, -0.015, 0.010, -0.004]


def seed_m():
    pts = grid()
    lines = ['P,N,E,Z,D', '# crew A, total station, 2026-10-03']
    for p in pts:
        z = p[3] + (3.0 if p[0] == '88' else 0.0)
        e = '%.3f' % p[2]
        if p[0] == '57':
            e = e[:-1] + 'O'   # a mistyped easting: 2060.00O
        lines.append('%s,%.3f,%s,%.3f,%s' % (p[0], p[1], e, z, p[4]))
    dup = pts[11]
    lines.append('300,%.3f,%.3f,%.3f,GND' % (dup[1], dup[2], dup[3] + 0.02))
    for k, ((dn, de), nz) in enumerate(zip(CHECKS, NOISE)):
        n, e = N0 + dn, E0 + de
        lines.append('%d,%.3f,%.3f,%.3f,CHK' % (500 + k, n, e, z_at(e, n) + nz))
    text = '\n'.join(lines) + '\n'
    bad = [i + 1 for i, l in enumerate(lines) if l.startswith('P,') or l.startswith('57,')]
    meta = {
        'file': 'seed_site_m.txt', 'format': 'PNEZD', 'units': 'm', 'base': {'n': N0, 'e': E0, 'z': 100.0}, 'checkCode': 'CHK',
        'control': '1=%.3f, 113=%.3f' % (pts[0][3], pts[112][3]),   # point 113 is row 8, column 8: 5070 N, 2070 E
        'note': 'Seed: a 15 x 15 grid at 10 m with a header, a mistyped line, a duplicate, a bust shot and six check shots.',
        'expect': {'verdict': 'fail', 'points': 224,   # 225, less the mistyped 57; the duplicate 300 is left out too
                   'checks': 6, 'skippedLines': bad, 'duplicates': ['300'], 'busts': ['88'],
                   'fidelity': 'pass', 'triangles': 'pass', 'checkStatus': 'pass', 'checkRmseMax': 0.05, 'control': 'pass'}}
    return text, meta


def seed_usft():
    pts = grid()
    lines = []
    for p in pts:
        z, d = p[3], p[4]
        if p[0] == '140':
            z, d = z + 0.20, 'MH'   # a manhole lid 0.2 m proud of the ground: real, not a bust
        lines.append('%s %.4f %.4f %.4f %s' % (p[0], p[2] / USFT, p[1] / USFT, z / USFT, d))
    for k, ((dn, de), nz) in enumerate(zip(CHECKS, NOISE)):
        n, e = N0 + dn, E0 + de
        lines.append('%d %.4f %.4f %.4f CHK-%d' % (500 + k, e / USFT, n / USFT, (z_at(e, n) + nz) / USFT, k + 1))
    text = '\n'.join(lines) + '\n'
    meta = {
        'file': 'seed_site_usft.txt', 'format': 'PENZD', 'units': 'usft', 'base': {'n': N0 / USFT, 'e': E0 / USFT, 'z': 100.0 / USFT}, 'checkCode': 'CHK',
        'control': '1=%.4f, 113=%.4f' % (pts[0][3] / USFT, pts[112][3] / USFT),
        'note': 'Seed: the same ground in US survey feet, PENZD, space separated, a manhole lid 0.2 m proud (not a bust), no faults.',
        'expect': {'verdict': 'pass', 'points': 225, 'checks': 6, 'skippedLines': [], 'duplicates': [], 'busts': [],
                   'fidelity': 'pass', 'triangles': 'pass', 'checkStatus': 'pass', 'checkRmseMax': 0.05, 'control': 'pass'}}
    return text, meta


OUT.mkdir(parents=True, exist_ok=True)
for name, (text, meta) in (('seed_site_m', seed_m()), ('seed_site_usft', seed_usft())):
    (OUT / meta['file']).write_text(text)
    (OUT / (name + '.json')).write_text(json.dumps(meta, indent=2) + '\n')
    print('%s: %d lines' % (meta['file'], text.count('\n')))
