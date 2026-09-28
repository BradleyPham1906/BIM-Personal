"""patch_phase118b.py -- V118: the other panels whose own controls re-render them keep the focus too.
The class, not the instance: the dock's Discipline dropdown re-renders the dock, so its focus fell to
the page and a second ArrowDown moved the selected object (measured on V117: the dock stepped once and
the column moved a metre); the views list re-renders under its Active-level-only checkbox; and the
level rows re-render under their own fields. Each renders through bimRenderInto now. The model tree,
the Project Browser and the schedules hold no fields, so what they re-render cannot hold the caret."""
NAME = 'patch_phase118b.py'
BASE = '785b2aac10df642d3eb29d461ba7c07ddcddca845f4857b5d15e9f45472e982e'
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def esc(s):
    """Non-ASCII in inserted text becomes a \\uXXXX escape, by code rather than by care (V103)."""
    return ''.join(ch if ord(ch) < 128 else '\\u%04x' % ord(ch) for ch in s)


def rep(old, new, n=1):
    global t
    new = esc(new)
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: %d occurrences, expected %d: %r' % (c, n, old[:90]))
    t = t.replace(old, new)


def after_line(head, new):
    """Insert new text after the whole line that starts with head (head must be unique)."""
    global t
    c = t.count(head)
    if c != 1:
        sys.exit('ABORT: %d occurrences, expected 1: %r' % (c, head[:90]))
    e = t.index('\n', t.index(head)) + 1
    t = t[:e] + esc(new) + t[e:]


def span(head, tail, new, lines):
    """Replace from the start of head up to (not including) the first tail after it. The span may
    hold non-ASCII that cannot be retyped, so it is found by its ends; head must be unique, and the
    number of lines removed must be exactly what was measured, so a tail that matched somewhere
    unexpected cannot quietly take the wrong amount."""
    global t
    c = t.count(head)
    if c != 1:
        sys.exit('ABORT: span head %d occurrences, expected 1: %r' % (c, head[:90]))
    s = t.index(head)
    e = t.find(tail, s + len(head))
    if e < 0:
        sys.exit('ABORT: span tail not found after head: %r' % tail[:90])
    got = t[s:e].count('\n')
    if got != lines:
        sys.exit('ABORT: span covers %d lines, expected %d: %r' % (got, lines, head[:60]))
    t = t[:s] + esc(new) + t[e:]
rep("    host.innerHTML=h+'</div>'+pops;\n",
    "    bimRenderInto(host,h+'</div>'+pops);   /* __acad3dV118: the Discipline dropdown keeps the focus */\n")
rep("    el.viewrows.innerHTML=h;\n",
    "    bimRenderInto(el.viewrows,h);   /* __acad3dV118 */\n")
rep("    el.lvlrows.innerHTML=h;\n",
    "    bimRenderInto(el.lvlrows,h);   /* __acad3dV118 */\n")
import re
code = re.sub(r'/\*.*?\*/', '', t, flags=re.S)
for dead in ("host.innerHTML=h+'</div>'+pops", "viewrows.innerHTML", "lvlrows.innerHTML", "propsbody.innerHTML"):
    if dead in code:
        sys.exit('ABORT: a panel with fields is still rendered by replacing its elements: ' + dead)
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
