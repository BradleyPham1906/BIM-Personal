"""patch_phase120n.py -- V120: the User Interface menu opens again.

Found by V120's own suite, which asks every attribute selector in the code to name a value some
control carries: one did not. The User Interface menu -- show or hide the Model Browser, the snap
toggles, the navigation pill and the view HUD, a V20 feature with saved preferences -- had two
openers, a toolbar button (data-a3d="uipanels") and the tool dock's View > Windows > User
Interface. The button went when the ribbon stood down in V70. The handler that closes the menu on
an outside click still named it, and nothing else, so the dock's click opened the menu and the
same click closed it: the entry did nothing, in V119 as well. It is the V120 cleanup's own subject
-- a control that survived a refactor and no longer does anything -- so it is fixed here rather
than deleted:
  - the outside-click handler knows the dock's opener;
  - the menu drops from the right end of the toolbar, where its anchor is, instead of starting
    there and running 150 px off the window."""
NAME = 'patch_phase120n.py'
BASE = '0cef69d55965f84fd1acb1577ec4c57a9c7de3796fdee580c1c195fecd5aa49e'
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
rep("""      if(ev.target&&ev.target.closest&&(ev.target.closest('#a3d-uimenu')||ev.target.closest('[data-a3d="uipanels"]')))return;""",
    """      if(ev.target&&ev.target.closest&&(ev.target.closest('#a3d-uimenu')||ev.target.closest('[data-a3dr="bim:uipanels"]')))return;   /* __acad3dV120 */""")
rep(""".a3d-uimenu{display:none;position:absolute;top:100%;left:0;margin-top:4px;""",
    """.a3d-uimenu{display:none;position:absolute;top:100%;right:0;margin-top:4px;""")
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
