"""patch_phase120a.py -- V120, the canvas-era cleanup: what the whiteboard left in the shell services.

The owner, opening the file: "it look very messy and still contain some of the old canvas
configuretion in there please clean that up before we make any further progress". This phase
removes the Canvas whiteboard's leftovers: the code, styles, names and comments it left behind.
It removes nothing that still does something for the user.

This script handles the three blocks at the top of <body>:
  - an HTML comment and a <script> holding nothing but a comment, both epitaphs for the whiteboard
    deleted in V113c;
  - the material library, declared outside the engine and published a second time as
    window.__WB_MATERIAL_CARDS ("WB" for whiteboard) so that the board and BIM would share one
    array. The board is gone and the engine is the only reader, so the array moves into the engine,
    before any engine code runs, and bimMaterialCards() returns it. window.__a3dMaterialCards()
    has published it to the suites since V69;
  - window.toast, the whiteboard's name for a toast, kept since V114 as a shim over the engine's.
    The five calls that used it (the quick-access bar, the command palette, the project tabs and
    the Start page) now call the engine's published window.__a3dToast, each behind a guard, so a
    missing engine cannot turn a message into a throw. The block that is left is empty, so it goes."""
NAME = 'patch_phase120a.py'
BASE = '905371647a373c5d46a38ff0f361e853cac444ee347ef5db6948bfc227fb37bd'
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
# 1. the epitaphs and the shell-services block, from the HTML comment through the services </script>
span('<!-- __acad3dV113c: the whiteboard\'s own markup is gone',
     '\n\n<style>\n/* Figma-style Assets library', '', 48)

# 2. the library, at the top of the engine, before bimProjectRecord() first runs
after_line('  var DEFCAM={yaw:-0.7,pitch:0.42,dist:30,tx:0,ty:1,tz:0};',
"""  /* __acad3dV120: the material library. One array, read through bimMaterialCards() by the
     inspector, the schedules' mass takeoff, the plan hatches and the Assets panel. Each card carries
     its engineering data -- density in kg/m3, Young's modulus, Poisson's ratio -- and a hatch. */
  var A3D_MATERIAL_LIBRARY=[
    {name:'Steel',kind:'Metal',density:7900,youngsModulus:'210 GPa',poissonRatio:0.30,color:'#9fb6c9',hatch:{angle:45,gap:9}},
    {name:'Aluminium',kind:'Metal',density:2700,youngsModulus:'70 GPa',poissonRatio:0.35,color:'#c9cdd2',hatch:{angle:45,gap:9,cross:true}},
    {name:'Concrete',kind:'Mineral',density:2400,youngsModulus:'32 GPa',poissonRatio:0.17,color:'#b7ab98',hatch:{angle:30,gap:12,cross:true}},
    {name:'Wood',kind:'Organic',density:700,youngsModulus:'12 GPa',poissonRatio:0.05,color:'#c8a06a',hatch:{angle:0,gap:10}},
    {name:'Glass',kind:'Mineral',density:2500,youngsModulus:'72 GPa',poissonRatio:0.22,color:'#8fd0d8',hatch:{angle:60,gap:14}}
  ];
""")
rep("""  /* __acad3dV69: BIM's view of the shared material library. Cards carry real engineering data
     (density kg/m3, Young's modulus, Poisson ratio) plus a hatch definition, so assigning one
     to a solid gives BOTH a plan cut pattern and a quantity takeoff from the same act. */
  function bimMaterialCards(){
    var c=window.__WB_MATERIAL_CARDS;
    return (c&&c.length)?c:[];
  }""",
"""  /* __acad3dV69: assigning a card to a solid gives BOTH a plan cut pattern and a quantity takeoff
     from the same act. */
  function bimMaterialCards(){
    return A3D_MATERIAL_LIBRARY;   /* __acad3dV120 */
  }""")

# 3. the five toasts outside the engine go to the engine's own
rep("""    console.warn('[BIM] No command runs the act '+act);
    window.toast('That command is not available');""",
"""    console.warn('[BIM] No command runs the act '+act);
    if(window.__a3dToast)window.__a3dToast('That command is not available');   /* __acad3dV120 */""")
rep("""      if(!ok&&window.toast)try{window.toast(c.name+' is not available here');}catch(eT){}""",
"""      if(!ok&&window.__a3dToast)window.__a3dToast(c.name+' is not available here');   /* __acad3dV120 */""")
rep("""      console.warn('[BIM] The project list is not ready yet');
      window.toast('The workspace is still loading; try again in a moment');""",
"""      console.warn('[BIM] The project list is not ready yet');
      if(window.__a3dToast)window.__a3dToast('The workspace is still loading; try again in a moment');   /* __acad3dV120 */""")
rep("""      console.warn('[BIM] Project '+fn+' failed',eD);
      window.toast('That did not work: '+(eD&&eD.message?eD.message:eD));""",
"""      console.warn('[BIM] Project '+fn+' failed',eD);
      if(window.__a3dToast)window.__a3dToast('That did not work: '+(eD&&eD.message?eD.message:eD));   /* __acad3dV120 */""")
rep("""        console.warn('[BIM] The project file picker could not be opened');
        window.toast('The workspace is still loading; try Open again in a moment');""",
"""        console.warn('[BIM] The project file picker could not be opened');
        if(window.__a3dToast)window.__a3dToast('The workspace is still loading; try Open again in a moment');   /* __acad3dV120 */""")
rep("""  /* __acad3dV114: published, because the shell outside this engine had no toast of its own. It
     had been calling window.toast, which was the Canvas whiteboard's; V113c deleted that, and every
     call -- all nine guarded with window.toast&& -- went silent without an error: the palette's
     "not available here", the workspace switch confirmation, and seven more. */
  window.__a3dToast=function(m){return a3dToast(m);};""",
"""  /* __acad3dV114: published for the chrome outside this engine -- the quick-access bar, the command
     palette, the project tabs and the Start page all toast through it (V120). */
  window.__a3dToast=function(m){return a3dToast(m);};""")

for gone in ('__WB_MATERIAL_CARDS', 'window.toast=', "window.toast(", '__acad3dV113c: the Canvas whiteboard engine'):
    if gone in t.replace('window.__WB_MATERIAL_CARDS, V69', ''):
        sys.exit('ABORT: still in the file: %r' % gone)

out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
