"""patch_phase117d.py -- V117 the rest of the 2D wire shell, part 4: the BIM engine stops managing
chrome that no longer exists. On entry it closed the whiteboard dock's panel and hid the 2D
workspace's status bar; neither element is built by anything any more."""
NAME = 'patch_phase117d.py'
BASE = '0178f6c0186830c994a95db25a2fae1f986323686668eb40c935dbc52c7aa468'
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
span("    /* The Figma rail's Props/Layers/Blocks pop-out (#acad-dockpanel) shows plain 2D\n", "    /* __acad3dV68: Properties moves to the right inspector.",
     r'''    /* __acad3dV117: this used to close the whiteboard dock's properties pop-out on entry, and to
       explain why two Properties panels must not show at once. That dock is deleted; the class
       below is what the rest of the stylesheet keys this workspace on. */
    try{
      document.body.classList.add('a3d-mode');
    }catch(eDp){console.warn('[BIM] Could not mark the page as the BIM workspace.',eDp);}
''', 13)
span("  var BIM_2D_CHROME_IDS=['acad-status'];", "  function enter3d(){\n",
     r'''  /* __acad3dV117: the 2D-chrome hider is gone. It hid the 2D workspace's status bar on entry and
     restored it on exit; nothing has built that bar since the whiteboard shell went, so it hid and
     restored nothing. */
''', 19)
rep("    bimHide2DChrome();\n", "")
rep("    bimRestore2DChrome();\n", "")
# scripts only, comments out: the stylesheet's rules for the dock go in 117d, by derivation
import re
code = re.sub(r'<style\b[^>]*>.*?</style>', '', t, flags=re.S | re.I)
code = re.sub(r'/\*.*?\*/', '', code, flags=re.S)
for dead in ('acad-dockpanel', 'BIM_2D_CHROME_IDS', '2DChrome'):
    if dead in code:
        sys.exit('ABORT: the engine still refers to ' + dead)
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
