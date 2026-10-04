#!/usr/bin/env python3
"""build_site.py -- what GitHub Pages serves, in _site/ (the workflow runs it on every push to main).

  python3 tools/build_site.py [_site]

- index.html and canvas_v10.html: the newest app;
- docs/: the user guide (built HTML, committed; tools/build_docs.py --check proves it current);
- v/<version>/index.html: every older build kept in Phase/ before a phase, named as on the guide's
  Versions page, so an older version stays reachable at a fixed address."""
import pathlib, shutil, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
import build_docs  # noqa: E402

OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / '_site'


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / 'docs').mkdir(parents=True)
    shutil.copy(ROOT / 'canvas_v10.html', OUT / 'index.html')
    shutil.copy(ROOT / 'canvas_v10.html', OUT / 'canvas_v10.html')
    for p in (ROOT / 'docs').glob('*.html'):
        shutil.copy(p, OUT / 'docs' / p.name)
    n = 0
    for lab, src in build_docs.kept_versions():
        d = OUT / 'v' / lab.lower()
        d.mkdir(parents=True)
        shutil.copy(src, d / 'index.html')
        n += 1
    (OUT / '.nojekyll').touch()
    print('%s: the app, %d guide pages, %d older versions' % (OUT, len(list((OUT / 'docs').glob('*.html'))), n))


if __name__ == '__main__':
    main()
