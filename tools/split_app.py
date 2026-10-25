#!/usr/bin/env python3
"""split_app.py -- cut a canvas_v10.html into src/, by the table in tools/app_layout.py.

  python3 tools/split_app.py [path/to/canvas_v10.html]

For a build changed as one file: a branch made before the split, merged in, or a phase's script
that patched canvas_v10.html itself. It rewrites src/index.html, src/css/ and src/js/ (nothing else
in src/), then joins them again and refuses to finish unless the result is the input, byte for byte.
An anchor that is missing or no longer unique stops it before anything is written: fix the row in
app_layout.py (a changed first line, or a new file) and run it again."""
import hashlib, pathlib, shutil, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
import app_layout  # noqa: E402
import build_app  # noqa: E402

SRC = ROOT / 'src'


def starts(lines, i, anchor):
    return ''.join(lines[i:i + anchor.count('\n') + 1]).startswith(anchor)


def cut(path):
    data = pathlib.Path(path).read_bytes()
    lines = data.decode('utf-8').splitlines(keepends=True)
    tags = [i for i, l in enumerate(lines) if l in ('<style>\n', '</style>\n', '<script>\n', '</script>\n')]
    if len(tags) != 2 * len(app_layout.BLOCKS):
        sys.exit('%s: %d block tags on lines of their own, %d expected' % (path, len(tags), 2 * len(app_layout.BLOCKS)))
    page, files, prev = [], {}, 0
    for b, (tag, bundle, folder, rows) in enumerate(app_layout.BLOCKS):
        o, c = tags[2 * b], tags[2 * b + 1]
        if lines[o] != '<%s>\n' % tag or lines[c] != '</%s>\n' % tag:
            sys.exit('block %d is not a <%s>' % (b + 1, tag))
        page += lines[prev:o]
        at = []
        for name, anchor in rows:
            hits = [i for i in range(o + 1, c) if starts(lines, i, anchor)]
            if len(hits) != 1:
                sys.exit('%s/%s: its anchor is found %d times in block %d (1 expected): %r' % (folder, name, len(hits), b + 1, anchor))
            at.append(hits[0])
        if at[0] != o + 1:
            sys.exit('%s/%s: the block\'s first file starts on line %d, not at the block\'s start (%d)' % (folder, rows[0][0], at[0] + 1, o + 2))
        if at != sorted(at):
            sys.exit('block %d: the anchors are out of order' % (b + 1))
        page.append('<!-- @bundle %s -->\n' % bundle)
        page.append(lines[o])
        for k, (name, _) in enumerate(rows):
            rel = '%s/%s' % (folder, name)
            files[rel] = ''.join(lines[at[k]:at[k + 1] if k + 1 < len(at) else c])
            page.append('<!-- @include %s -->\n' % rel)
        page.append(lines[c])
        page.append(build_app.END)
        prev = c + 1
    page += lines[prev:]
    return data, ''.join(page), files


def main(argv):
    path = argv[0] if argv else str(build_app.APP)
    data, page, files = cut(path)
    for d in ('css', 'js'):
        if (SRC / d).exists():
            shutil.rmtree(SRC / d)
    SRC.mkdir(exist_ok=True)
    (SRC / 'index.html').write_text(page, encoding='utf-8')
    for rel, text in files.items():
        p = SRC / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding='utf-8')
    back = build_app.one_file().encode('utf-8')
    if back != data:
        sys.exit('src/ does not join back into %s: do not commit it' % path)
    print('%s: %d files in src/, joined back byte for byte (%d bytes, sha256 %s)'
          % (path, len(files) + 1, len(data), hashlib.sha256(data).hexdigest()))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
