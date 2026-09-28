"""patch_phase119g.py -- V119: one test for a plan.

V84 recorded the lesson -- "an elevation is flat too" -- and fixed three places that read "flat" as
"plan". Grepping for A3D.flat while the record learned to name every view found the same mistake in
six more, each written after or beside that lesson:

  - bimEnterDraftingMode, which every drawing tool starts through, and startSectionTool: both drop a
    3D view to the plan with "if(!A3D.flat)toggleFlat()", and an elevation is already flat. Measured
    on the V119 build before this patch: in the Front Elevation, LINE started, stayed in the
    elevation, and both clicks were refused -- groundPoint declines a ground point through a
    sideways camera -- with nothing on screen to say why. It is the "nothing happens" V18 fixed for
    sections.
  - drawTerrain, drawNorthArrow, drawSunShadows, drawSunPath, each commented "plan only" and each
    testing "flat and not a section": the north arrow was drawn in the Front Elevation, pointing up.
  - bimToggleSun, which tells the user the study is drawn in plan only when the camera is not flat.

All of them now ask bimCameraIsPlan. A drawing tool started in an elevation opens the floor plan of
the active level first, as one started in 3D does.

The north arrow's test hook kept the last arrow it drew, so it could not say that none was drawn; it
is cleared at the start of each frame, as the terrain's, the shadows' and the sun path's are."""
NAME = 'patch_phase119g.py'
BASE = '2ed62054f63a77963e1f8159ef759a64df3d7deda22f5f8e52a4556844e2e78c'
import re
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
# ---- 1. the drawing tools and the section tool: an elevation opens the plan, as 3D does
rep("    if(!A3D.flat)toggleFlat();\n",
    "    if(!A3D.flat)toggleFlat();\n"
    "    else if(!bimCameraIsPlan())bimActivateView('plan',null,{anim:false});   /* __acad3dV119: an elevation is flat too */\n", 2)

# ---- 2. what is drawn in plan only is drawn in plan only
rep("    if(!A3D.flat||A3D.section)return;\n",
    "    if(!bimCameraIsPlan())return;   /* __acad3dV119: flat is not plan -- an elevation is flat */\n", 2)
rep("    if(!A3D.showSun||!A3D.flat||A3D.section)return;\n",
    "    if(!A3D.showSun||!bimCameraIsPlan())return;   /* __acad3dV119 */\n")
rep("    if(!A3D.showSun||!A3D.flat||A3D.section||A3D.sheetCapture)return;\n",
    "    if(!A3D.showSun||!bimCameraIsPlan()||A3D.sheetCapture)return;   /* __acad3dV119 */\n")
rep("    else if(!A3D.flat)a3dToast('Sun study on: shadows and the sun path are drawn in plan');\n",
    "    else if(!bimCameraIsPlan())a3dToast('Sun study on: shadows and the sun path are drawn in plan');   /* __acad3dV119 */\n")

# ---- the north arrow's hook reports this frame, as the terrain's, the shadows' and the sun path's do
rep("  function drawNorthArrow(ctx,V,W,H){\n",
    "  function drawNorthArrow(ctx,V,W,H){\n    A3D.lastNorth=null;   /* __acad3dV119: what the hook reports is what this frame drew */\n")

# ---- nothing is left that reads "flat and not a section" as "plan"
code = re.sub(r'/\*.*?\*/', '', t, flags=re.S)
if re.search(r'!A3D\.flat\|\|A3D\.section', code):
    sys.exit('ABORT: a "plan only" test still reads flat as plan')
if len(re.findall(r'bimCameraIsPlan\(\)', code)) != 9:
    sys.exit('ABORT: bimCameraIsPlan is used %d times, expected 9' % len(re.findall(r'bimCameraIsPlan\(\)', code)))
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
