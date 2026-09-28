"""patch_phase120d.py -- V120: the way out of a workspace that is the whole app.

The BIM engine began as a mode entered from the Canvas whiteboard, and exit3d() was the way back:
it un-nested the Project Browser from the whiteboard's file dock, returned Properties to the
palette, re-collapsed the dock if the whiteboard had it collapsed, and took a3d-mode off the body so
the board's styles came back. V67 measured that nothing reaches it -- no control emits
act === 'exit', and V85 took it out of the Escape chain -- and V113c deleted the board it returned
to. It survived as window.__a3dExit, called only by suites checking that it restored a layout no
user can leave.

It goes, with the bookkeeping that existed only for it (A3D._treeHome, _propsHome,
_dockWasCollapsed) and the toolbar branch that would have called it. __a3dShellGeom stops
reporting the board's #viewport, which V113c deleted, and a 'canvas' mode, which nothing can be in:
before the engine enters its mode is null."""
NAME = 'patch_phase120d.py'
BASE = '5bc4b8aa70a6247d2245d0a9664b0dae4ce4900e21e38bfacfdf5649c5c4ca97'
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
span('  function exit3d(){\n', '\n  window.__a3dEnter=enter3d;\n', '', 38)
rep('  window.__a3dEnter=enter3d;\n  window.__a3dExit=exit3d;\n', '  window.__a3dEnter=enter3d;\n')
rep("      else if(act==='exit')exit3d();\n", '')
rep("""      if(flPanel&&tree&&tree.parentNode!==flPanel){
        // Remember where it came from so exit3d can put it back exactly, leaving the Canvas
        // workspace's own layout untouched.
        A3D._treeHome=tree.parentNode;
        A3D._dockWasCollapsed=!!(flShell&&flShell.classList.contains('collapsed'));
        flPanel.appendChild(tree);""",
"""      if(flPanel&&tree&&tree.parentNode!==flPanel){
        flPanel.appendChild(tree);""")
rep("""      if(propsSec&&rightPane&&propsSec.parentNode!==rightPane){
        A3D._propsHome=propsSec.parentNode;
        rightPane.appendChild(propsSec);""",
"""      if(propsSec&&rightPane&&propsSec.parentNode!==rightPane){
        rightPane.appendChild(propsSec);""")
rep("""    var vp=box('viewport'),sh=box('acad3d');
    return {
      mode:(window.__a3dOn?(window.__a3dFlat&&window.__a3dFlat()?'da':'3d'):'canvas'),
      wsCur:window.ACAD_WS_CUR||null,
      a3dOn:!!window.__a3dOn,
      viewport:vp,acad3d:sh,
      dock:box('figma-layers-shell'),ribbon:box('acad-shell'),
      // Exactly one full-window work surface may be mounted at a time -- the invariant this
      // phase established, and the one worth failing a build over.
      workSurfaces:[vp,sh].filter(function(b){return b&&b.visible;}).length,
      work:(vp&&vp.visible)?vp:((sh&&sh.visible)?sh:null)
    };""",
"""    var sh=box('acad3d');
    return {
      mode:(window.__a3dOn?(window.__a3dFlat&&window.__a3dFlat()?'da':'3d'):null),   /* __acad3dV120 */
      wsCur:window.ACAD_WS_CUR||null,
      a3dOn:!!window.__a3dOn,
      acad3d:sh,
      dock:box('figma-layers-shell'),ribbon:box('acad-shell'),
      workSurfaces:[sh].filter(function(b){return b&&b.visible;}).length,
      work:(sh&&sh.visible)?sh:null
    };""")
for gone in ('exit3d', '__a3dExit=', '_treeHome', '_propsHome', '_dockWasCollapsed', "box('viewport')"):
    if gone in t.replace('toggled by enter3d/exit3d', '').replace('             exit3d();', ''):
        sys.exit('ABORT: %s is still in the code' % gone)
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
