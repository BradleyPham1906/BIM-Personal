"""p171.py -- what V171's patch scripts share, since the source is src/ (CLAUDE.md, "The source").

begin(base): the build src/ makes now must be canvas_v10.html, and its sha256 the script's base, or nothing is touched.
rep(path, old, new, count): a replacement in a file under src/, asserting the exact number of occurrences.
write(path, text): a new file under src/ (refused if it is there already, unless replace=True).
done(): the files written, canvas_v10.html built again from src/, its bytes before and after and its sha256 printed."""
import hashlib, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
import build_app  # noqa: E402

SRC = ROOT / 'src'
_files = {}
_new = {}
_before = [0]


def begin(base):
    data = build_app.one_file().encode('utf-8')
    sha = hashlib.sha256(data).hexdigest()
    app = build_app.APP.read_bytes()
    if app != data:
        sys.exit('canvas_v10.html is not what src/ builds: run tools/build_app.py first')
    if sha != base:
        sys.exit('BASE mismatch: %s (expected %s)' % (sha, base))
    _before[0] = len(data)


def _text(path):
    if path not in _files:
        p = SRC / path
        if not p.exists():
            sys.exit('no src/%s' % path)
        _files[path] = p.read_text(encoding='utf-8')
    return _files[path]


def rep(path, old, new, count=1):
    s = _text(path)
    n = s.count(old)
    if n != count:
        sys.exit('src/%s: expected %d of %r, found %d' % (path, count, old[:100], n))
    _files[path] = s.replace(old, new)


def write(path, text, replace=False):
    p = SRC / path
    if p.exists() and not replace:
        sys.exit('src/%s is there already' % path)
    if not text.endswith('\n'):
        sys.exit('src/%s: a file ends with a newline' % path)
    try:
        text.encode('ascii')
    except UnicodeEncodeError as e:
        sys.exit('src/%s: non-ASCII at %d: write it as an escape' % (path, e.start))
    _new[path] = text


def done():
    for path, text in _files.items():
        (SRC / path).write_text(text, encoding='utf-8')
    for path, text in _new.items():
        q = SRC / path
        q.parent.mkdir(parents=True, exist_ok=True)
        q.write_text(text, encoding='utf-8')
    data = build_app.one_file().encode('utf-8')
    build_app.APP.write_bytes(data)
    print('%d bytes before, %d after, sha256 %s' % (_before[0], len(data), hashlib.sha256(data).hexdigest()))
