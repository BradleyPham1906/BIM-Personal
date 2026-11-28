"""e03's colour comparison: how many of each file's elements That Open colours as cc-ifc does, within 2 steps (of 255)
per channel, every pairing used (a colour that rounding splits in two is paired with both). Run on run.mjs's output
made with E03_COLS=1: python3 -I colours.py e03-colours-http.jsonl"""
import json, sys
def rgb(h): return [int(h[i:i + 2], 16) for i in (1, 3, 5)]
for line in open(sys.argv[1]):
    if not line.startswith('{'): continue
    d = json.loads(line)
    if not d.get('cols'): continue
    a, b = dict(d['cols'][0]), dict(d['cols'][1])
    n = sum(a.values())
    for c in list(a):
        for c2 in list(b):
            if a[c] and b[c2] and max(abs(x - y) for x, y in zip(rgb(c), rgb(c2))) <= 2:
                m = min(a[c], b[c2]); a[c] -= m; b[c2] -= m
    left = sum(v for v in a.values() if v > 0)
    print('%-22s %5d elements, %5.1f%% coloured as cc-ifc; left: %s' % (d['file'], n, 100.0 * (n - left) / max(1, n),
        sorted([(k, v) for k, v in a.items() if v > 0], key=lambda x: -x[1])[:4]))
