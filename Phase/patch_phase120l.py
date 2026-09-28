"""patch_phase120l.py -- V120: two scripts, the shell and the engine.

<body> held four scripts: the top bar, the palette and project tabs, the boot, and the engine --
the first three written as separate modules injected one after another, each guarding against
being run twice. They become one <script>, in the same order, followed by the engine's. Each keeps
its own try/catch, so one failing still cannot stop the next.

Two leftovers go with the seams:
  - the palette module's run-once guard, window.__acadWorkspaceV1: the script runs once;
  - the engine's header, which still called it "a3d_engine.js v2 - 3D (Part) workspace integrated
    into the AutoCAD-style shell ... Injected as the final script block by patch_3d.py".
And one silent failure: the engine's outer catch stored a load error in window.__a3dErr, which
nothing reads, and said nothing. It warns now; the boot, finding no engine, says so on screen."""
NAME = 'patch_phase120l.py'
BASE = '815c89d32c892c87420dd07b7aebbfb4cadb13d18db4b98bc4243e8365ac5c78'
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
rep("""<body>

<script>
(function acadTopBar(){""", """<body>

<script>
/* __acad3dV120: the shell -- the top bar, the command palette and the project tabs, and the boot
   into the BIM workspace. The engine is the next script. */
(function acadTopBar(){""")
rep("""})();
</script>

<script>
(function acadWorkspaceV1(){
  if(window.__acadWorkspaceV1) return; window.__acadWorkspaceV1=true;
  try{""", """})();

(function acadWorkspaceV1(){
  try{""")
rep("""})();
</script>

<script>
(function acadBoot(){""", """})();

(function acadBoot(){""")
rep("""<script>
/* a3d_engine.js v2 - 3D (Part) workspace integrated into the AutoCAD-style shell.
   Original implementation of the parametric solid primitives (box, cylinder,
   sphere, cone, torus, tube, prism, wedge, ellipsoid) and their parameters.
   ES5 only. Injected as the final script block by patch_3d.py. */
(function(){""", """<script>
/* The BIM engine: the model and its objects, the views, the tools, documentation and persistence.
   ES5 throughout. */
(function(){""")
rep("""}catch(e){
  window.__a3dErr=String(e&&e.message||e);
}
})();""", """}catch(e){
  window.__a3dErr=String(e&&e.message||e);
  console.warn('[BIM] The engine failed to load.',e);   /* __acad3dV120 */
}
})();""")
rep("""      else console.warn('[BIM] The BIM workspace did not load; reload the page to try again.');""",
    """      else{
        console.warn('[BIM] The BIM workspace did not load; reload the page to try again.');
        document.body.insertAdjacentHTML('beforeend','<div style="position:fixed;left:50%;top:40%;transform:translateX(-50%);padding:14px 18px;background:#2a2f35;color:#e6eef6;border:1px solid #c0504d;border-radius:6px;font:13px sans-serif;z-index:99999">The workspace did not load. Reload the page to try again.</div>');
      }""")
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
