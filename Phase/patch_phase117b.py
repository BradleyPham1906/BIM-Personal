"""patch_phase117b.py -- V117 the rest of the 2D wire shell, part 2: acadWs2V1's sections 1 and 2.
Section 1 put Properties, Layers and Blocks buttons for the whiteboard dock on the left rail (hidden in
this app) and watched every change to the document with a MutationObserver to keep them there;
section 2 was a window / crossing marquee over whiteboard wires that could never start. Section 6,
the Delete key, is not here: the BIM engine's Delete rides on it, so it goes in 117c with the move."""
NAME = 'patch_phase117b.py'
BASE = '26d726ae674e37bed74520bddcc529f6ced02bbb26c93f4ad51d2858417a90f8'
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
rep("  function wsSt(){ try{return window.__wsState?window.__wsState():{};}catch(e){return {};} }\n", "")
span("  // ============ 1. DOCK IN LEFT SIDEBAR ============\n", "  /* __acad3dV116: section 3, the Start page's wire thumbnails, is gone.",
     r'''  /* __acad3dV117: sections 1 and 2 are gone. Section 1 put buttons for the whiteboard's
     Properties / Layers / Blocks dock on the left rail -- hidden in this app -- and kept them there
     with a MutationObserver on every change to the whole document. Section 2 was a window / crossing
     marquee over whiteboard wires; it only started after the whiteboard's own hit test had run on its
     viewport, which V113c deleted, so it never started. Window and crossing selection of BIM objects
     is the BIM engine's. */
''', 161)
seg = t[t.index('(function acadWs2V1(){'):]
seg = seg[:seg.index('})();')]
# code only: the phase comments that say what went (V73's, V116's) name it on purpose
import re
seg = re.sub(r'/\*.*?\*/', '', seg, flags=re.S)
seg = re.sub(r'(?m)^\s*//.*$', '', seg)
for dead in ('wirePts', 'acad-dkbtn', 'ws2-marq', '__ws2Marq', 'MutationObserver', 'toWorld', 'wsSt('):
    if dead in seg:
        sys.exit('ABORT: acadWs2V1 still has ' + dead)
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
