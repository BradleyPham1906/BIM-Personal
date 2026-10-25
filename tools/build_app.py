#!/usr/bin/env python3
"""build_app.py -- join the app's source in src/ into the app.

  python3 tools/build_app.py              write canvas_v10.html (the one-file build every suite tests)
  python3 tools/build_app.py --check      exit 1 when canvas_v10.html is not what src/ builds
  python3 tools/build_app.py --site DIR   write the multi-file app Pages serves: DIR/index.html, and
                                          its stylesheet and scripts in DIR/app/

src/index.html is the page. Inside it, each block (the stylesheet, and the three scripts) is written

  <!-- @bundle engine.js -->
  <script>
  <!-- @include js/engine/_begin.js -->
  ...
  </script>
  <!-- @end -->

The one-file build puts each included file's bytes between the tags, in order, and drops the
@bundle and @end lines. The site build writes the same bytes to app/<bundle> and puts a <link> or
a <script src> in the page in their place, its address carrying the bundle's hash so a browser
never runs an old copy. The order of the files, and why the engine's are never loaded one by one,
is in tools/app_layout.py."""
import hashlib, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / 'src'
APP = ROOT / 'canvas_v10.html'

BUNDLE = re.compile(r'<!-- @bundle (\S+) -->\n$')
INCLUDE = re.compile(r'<!-- @include (\S+) -->\n$')
END = '<!-- @end -->\n'


def parse(src=SRC):
    """The page as a list: plain lines (str), and blocks (dict: bundle, open, close, files)."""
    lines = (src / 'index.html').read_text(encoding='utf-8').splitlines(keepends=True)
    out, i = [], 0
    while i < len(lines):
        m = BUNDLE.match(lines[i])
        if not m:
            out.append(lines[i])
            i += 1
            continue
        blk = {'bundle': m.group(1), 'open': lines[i + 1], 'files': []}
        i += 2
        while INCLUDE.match(lines[i]):
            blk['files'].append(INCLUDE.match(lines[i]).group(1))
            i += 1
        blk['close'] = lines[i]
        if lines[i + 1] != END:
            sys.exit('src/index.html: the block %s does not end with %r' % (blk['bundle'], END.strip()))
        i += 2
        out.append(blk)
    return out


def body(blk, src=SRC):
    """A block's content: its files' bytes, in order. Each must end with a newline, or two files'
    lines would run together."""
    parts = []
    for f in blk['files']:
        t = (src / f).read_text(encoding='utf-8')
        if not t.endswith('\n'):
            sys.exit('src/%s: does not end with a newline' % f)
        parts.append(t)
    return ''.join(parts)


def one_file(src=SRC):
    out = []
    for x in parse(src):
        out.append(x if isinstance(x, str) else x['open'] + body(x, src) + x['close'])
    return ''.join(out)


def write_site(out_dir, src=SRC):
    """The multi-file app: out_dir/index.html, out_dir/app/<bundle>. Returns the bundles' names."""
    out_dir = pathlib.Path(out_dir)
    (out_dir / 'app').mkdir(parents=True, exist_ok=True)
    page, names = [], []
    for x in parse(src):
        if isinstance(x, str):
            page.append(x)
            continue
        data = body(x, src).encode('utf-8')
        (out_dir / 'app' / x['bundle']).write_bytes(data)
        href = 'app/%s?v=%s' % (x['bundle'], hashlib.sha256(data).hexdigest()[:12])
        if x['open'].startswith('<style'):
            page.append('<link rel="stylesheet" href="%s" />\n' % href)
        else:
            page.append('<script src="%s"></script>\n' % href)
        names.append(x['bundle'])
    (out_dir / 'index.html').write_text(''.join(page), encoding='utf-8')
    return names


def main(argv):
    if '--site' in argv:
        d = argv[argv.index('--site') + 1]
        names = write_site(d)
        print('%s: index.html, and %s in app/' % (d, ', '.join(names)))
        return 0
    text = one_file()
    data = text.encode('utf-8')
    sha = hashlib.sha256(data).hexdigest()
    if '--check' in argv:
        if not APP.exists() or APP.read_bytes() != data:
            print('canvas_v10.html is not what src/ builds (src/ builds %d bytes, sha256 %s).\n'
                  'Edit src/ and run tools/build_app.py; after a change made to canvas_v10.html itself, '
                  'run tools/split_app.py to carry it into src/.' % (len(data), sha))
            return 1
        print('canvas_v10.html is what src/ builds: %d bytes, sha256 %s' % (len(data), sha))
        return 0
    APP.write_bytes(data)
    print('canvas_v10.html: %d bytes, sha256 %s' % (len(data), sha))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
