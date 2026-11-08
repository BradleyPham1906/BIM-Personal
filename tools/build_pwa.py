#!/usr/bin/env python3
"""build_pwa.py -- V172h: what makes the Pages site installable and usable offline (__acad3dV172h).

  python3 tools/build_pwa.py <site dir>     (tools/build_site.py runs it after writing the app)

docs/research/research-local-storage.md, part 15 (option C; the owner's Q1-Q7, 2026-11-08). In the site directory:
- sw.js, from src/sw/sw.js with the build's values filled in: its id (from the page, which names every bundle by its
  hash, and the worker's own text), the page and the four bundles to precache by their exact ?v= addresses, and the
  runtime's id (runtime/MANIFEST.json's hash). A new build is a new sw.js, so it reaches every user (H46).
  With BIM_SW_REMOVE=1 in the environment, tools/sw-remove.js is published as sw.js instead: the way back (Q7).
- manifest.webmanifest: id and scope the app's path, standalone, the 192 and 512 px icons and a maskable one (H49).
- icons/: icon-192.png, icon-512.png, icon-maskable-512.png and apple-touch-icon.png (180 px, which iOS uses before the
  manifest's icons, H50), drawn here: the app's own mark, no third-party design (Q5).
- index.html gains the manifest, the icon, the theme colour and <meta name="a3d-sw">, which tells the page to register
  the worker. Only this page: the one-file canvas_v10.html never registers one."""
import hashlib, json, os, pathlib, re, struct, sys, zlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SW_SRC = ROOT / 'src' / 'sw' / 'sw.js'
SW_REMOVE = ROOT / 'tools' / 'sw-remove.js'
APP_PATH = '/BIM-Personal/'
NAME = 'BIM-Personal'
BG = (0x1d, 0x24, 0x30)          # the app's dark ground
FACES = ((0xb3, 0xa6, 0xff), (0x8f, 0x7a, 0xff), (0x6a, 0x55, 0xd9))   # the accent, lit from above
HEAD_TAGS = ('<link rel="manifest" href="manifest.webmanifest" />\n'
             '<meta name="theme-color" content="#1d2430" />\n'
             '<link rel="apple-touch-icon" href="icons/apple-touch-icon.png" />\n'
             '<meta name="a3d-sw" content="sw.js" />\n')


# ---- the icons: an isometric box, scanline-filled with exact horizontal coverage and 4 sub-rows ----
def _span(poly, y):
    xs = []
    n = len(poly)
    for i in range(n):
        (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % n]
        if (y0 <= y < y1) or (y1 <= y < y0):
            xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
    return (min(xs), max(xs)) if len(xs) >= 2 else None


def _rounded_span(size, r, y):
    if r <= 0:
        return (0.0, float(size))
    if y < r:
        d = r - y
    elif y > size - r:
        d = y - (size - r)
    else:
        return (0.0, float(size))
    w = r - (max(r * r - d * d, 0.0)) ** 0.5
    return (w, size - w)


def _cover(row, span, sub):
    """add sub-row coverage of [a, b) to each pixel of row"""
    a, b = span
    a, b = max(a, 0.0), min(b, float(len(row)))
    if b <= a:
        return
    i0, i1 = int(a), int(b - 1e-9)
    for i in range(i0, i1 + 1):
        row[i] += (min(b, i + 1) - max(a, i)) * sub


def icon_rgba(size, box, radius):
    """size px; box: the cube's half-height as a share of size; radius: corner share (0 for full-bleed)"""
    cx, cy, s = size * 0.5, size * 0.5, size * box
    k = 0.8660254
    T, C, B = (cx, cy - s), (cx, cy), (cx, cy + s)
    UL, UR = (cx - k * s, cy - s / 2), (cx + k * s, cy - s / 2)
    LL, LR = (cx - k * s, cy + s / 2), (cx + k * s, cy + s / 2)
    faces = ((T, UR, C, UL), (UL, C, B, LL), (C, UR, LR, B))
    rad = size * radius
    out = bytearray()
    subs = 4
    for py in range(size):
        bg = [0.0] * size
        fc = [[0.0] * size for _ in faces]
        for j in range(subs):
            y = py + (j + 0.5) / subs
            _cover(bg, _rounded_span(size, rad, y), 1.0 / subs)
            for f, poly in enumerate(faces):
                sp = _span(poly, y)
                if sp:
                    _cover(fc[f], sp, 1.0 / subs)
        out.append(0)   # PNG filter: none
        for px in range(size):
            r, g, b = BG
            for f in range(len(faces)):
                c = min(fc[f][px], 1.0)
                if c > 0:
                    fr, fg, fb = FACES[f]
                    r, g, b = r + (fr - r) * c, g + (fg - g) * c, b + (fb - b) * c
            a = min(bg[px], 1.0)
            out += bytes((int(round(r)), int(round(g)), int(round(b)), int(round(255 * a))))
    return bytes(out)


def png(size, rgba_rows):
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', size, size, 8, 6, 0, 0, 0)) +
            chunk(b'IDAT', zlib.compress(rgba_rows, 9)) + chunk(b'IEND', b''))


ICONS = (  # name, size, cube, corner radius: "any" icons rounded; maskable and iOS full-bleed (the system shapes them)
    ('icon-192.png', 192, 0.30, 0.18),
    ('icon-512.png', 512, 0.30, 0.18),
    ('icon-maskable-512.png', 512, 0.22, 0.0),   # inside the 40 % safe circle
    ('apple-touch-icon.png', 180, 0.28, 0.0),
)


def manifest():
    return {
        'id': APP_PATH,             # resolved against the origin (part 15.3)
        'name': NAME,
        'short_name': NAME,
        'description': 'A browser CAD and BIM workspace that also works offline.',
        'start_url': './',
        'scope': './',
        'display': 'standalone',
        'background_color': '#1d2430',
        'theme_color': '#1d2430',
        'icons': [
            {'src': 'icons/icon-192.png', 'sizes': '192x192', 'type': 'image/png', 'purpose': 'any'},
            {'src': 'icons/icon-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'any'},
            {'src': 'icons/icon-maskable-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'maskable'},
        ],
    }


def _replace_once(text, pattern, value):
    new, n = re.subn(pattern, lambda m: value, text, count=0, flags=re.M)
    if n != 1:
        raise SystemExit('build_pwa: %r matched %d times in src/sw/sw.js (expected 1)' % (pattern, n))
    return new


def service_worker(page, runtime_id):
    src = SW_SRC.read_text(encoding='utf-8')
    shell = ['index.html'] + re.findall(r'(?:href|src)="(app/[^"?]+\?v=[0-9a-f]+)"', page)
    if len(shell) < 2:
        raise SystemExit('build_pwa: the page names no app/ bundle')
    build = hashlib.sha256((page + '\n' + src).encode('utf-8')).hexdigest()[:16]
    src = _replace_once(src, r"^var BIM_SW_BUILD = '[^']*';$", "var BIM_SW_BUILD = '%s';" % build)
    src = _replace_once(src, r"^var BIM_SW_SHELL = \[\];$", 'var BIM_SW_SHELL = %s;' % json.dumps(shell))
    src = _replace_once(src, r"^var BIM_SW_RUNTIME = '[^']*';$", "var BIM_SW_RUNTIME = '%s';" % runtime_id)
    return src, build, shell


def write(site):
    site = pathlib.Path(site)
    idx = site / 'index.html'
    page = idx.read_text(encoding='utf-8')
    if 'name="a3d-sw"' in page:
        raise SystemExit('build_pwa: index.html already carries the offline tags')
    if page.count('</head>') != 1:
        raise SystemExit('build_pwa: index.html has no single </head>')
    page = page.replace('</head>', HEAD_TAGS + '</head>')
    idx.write_text(page, encoding='utf-8')
    man = ROOT / 'runtime' / 'MANIFEST.json'
    runtime_id = hashlib.sha256(man.read_bytes()).hexdigest()[:16] if man.exists() else 'none'
    if os.environ.get('BIM_SW_REMOVE') == '1':
        sw, build, shell = SW_REMOVE.read_text(encoding='utf-8'), 'remove', []
    else:
        sw, build, shell = service_worker(page, runtime_id)
    (site / 'sw.js').write_text(sw, encoding='utf-8')
    (site / 'manifest.webmanifest').write_text(json.dumps(manifest(), indent=2) + '\n', encoding='utf-8')
    (site / 'icons').mkdir(exist_ok=True)
    for name, size, box, radius in ICONS:
        (site / 'icons' / name).write_bytes(png(size, icon_rgba(size, box, radius)))
    return {'build': build, 'shell': shell, 'runtime': runtime_id}


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    r = write(sys.argv[1])
    print('%s: sw.js (build %s, %d files precached), manifest.webmanifest, %d icons' %
          (sys.argv[1], r['build'], len(r['shell']), len(ICONS)))
