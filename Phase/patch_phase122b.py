"""patch_phase122b.py -- V122: a sheet is drawn in the appearance it prints in.

The Appearance setting (Technical or Presentation, the status bar's Tech/Pres) reached the model view,
the SVG exports and the vector print, and not a sheet's raster: a viewport's render had the
presentation graphics switched off outright ("capMode already has its own fixed print styling"). So a
sheet printed in its presentation colours, fills and patterns and showed on screen, in its PNG and in
its raster print as a technical drawing -- and a presentation for a client, which is made of those
rasters, would have shown the one thing the owner uses Photoshop to get away from.

One question now answers it everywhere, bimPresentGraphics: a plot is drawn in the appearance it is
plotted in, and anything else in the Appearance setting. A viewport's faces keep the dark outline of
a technical sheet only when they have no presentation line colour to take. The drop shadow is sized in
the drawing's pixels, not the canvas's: a canvas does not scale a shadow with its transform, and on a
high-density screen or a page drawn at twice its pixels the shadow came out at half its size."""
NAME = 'patch_phase122b.py'
BASE = '99b407545fe0ed55200518c3fbd018013e61a8e664df0b18a8f1d91c46deb9f7'
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

# ---- the one question
rep("""  function bimWithPlotPass(pres,fn){
""", """  /* __acad3dV122: whether the drawing is drawn with its presentation graphics -- in a plot, the
     appearance it is plotted in; otherwise the Appearance setting. A sheet's viewports are drawn by
     the same paint() as the model and ask the same question, so a sheet on screen, its PNG, its
     raster print, its pages and its vector print are all one appearance. */
  function bimPresentGraphics(){return A3D_PLOT.on?!!A3D_PLOT.pres:!!A3D.presentMode;}
  function bimWithPlotPass(pres,fn){
""")

# ---- the three places that asked "presentation, and not a sheet"
rep("""      var rrg=(A3D.presentMode&&!A3D.sheetCapture)?bimResolveGraphics(o,'presentation'):null;
""", """      var rrg=bimPresentGraphics()?bimResolveGraphics(o,'presentation'):null;   /* __acad3dV122 */
""")
rep("""    var glOn=(capMode||A3D.presentMode)?false:bimGlRender(V,W,H);
""", """    var glOn=(capMode||A3D.presentMode||bimPresentGraphics())?false:bimGlRender(V,W,H);   /* __acad3dV122 */
""")
rep("""       presentation mode is on, which forces glOn false (see the glOn line above), so it can never
       double-draw against the GPU path. */
""", """       presentation graphics are on, which forces glOn false (see the glOn line above), so it can
       never double-draw against the GPU path. __acad3dV122: on a sheet too. */
""")
rep("""    var presentRooms=!!A3D.presentMode&&!capMode;
""", """    var presentRooms=bimPresentGraphics();   /* __acad3dV122 */
""")
rep("""       OFF by default (A3D.presentMode starts false) and a no-op in sheet-capture mode (capMode
       already has its own fixed print styling) -- when off, this whole block is skipped and the
       loop is BYTE-IDENTICAL to before this phase, so nobody sees any change unless they opt in.
""", """       OFF by default (A3D.presentMode starts false) -- when off, this whole block is skipped and the
       loop is BYTE-IDENTICAL to before this phase, so nobody sees any change unless they opt in.
       __acad3dV122: a sheet's viewports take it too, in the appearance the sheet is plotted in;
       they were left technical, and a sheet printed in one appearance showed in the other.
""")
rep("""    var presentOn=!!A3D.presentMode&&!capMode;
""", """    var presentOn=bimPresentGraphics();   /* __acad3dV122 */
""")

# ---- the shadow in the drawing's pixels, and the outline a presentation face has
rep("""      if(rg&&rg.shadow){ctx.shadowColor='rgba(0,0,0,0.45)';ctx.shadowBlur=10;ctx.shadowOffsetX=3;ctx.shadowOffsetY=4;}
""", """      /* __acad3dV122: a canvas does not scale a shadow with its transform, so it is given in the
         canvas's own pixels -- the drawing's times its scale (pxs) */
      if(rg&&rg.shadow){ctx.shadowColor='rgba(0,0,0,0.45)';ctx.shadowBlur=10*pxs;ctx.shadowOffsetX=3*pxs;ctx.shadowOffsetY=4*pxs;}
""")
rep("""      var baseStroke=capMode?'rgba(0,0,0,0.55)':((A3D.sel===pl.o.id)?'#4ea1ff':((A3D.sel2===pl.o.id)?'#ffb454':(rg?rg.lineColor:'rgba(0,0,0,0.35)')));
""", """      var baseStroke=capMode?(rg?rg.lineColor:'rgba(0,0,0,0.55)'):((A3D.sel===pl.o.id)?'#4ea1ff':((A3D.sel2===pl.o.id)?'#ffb454':(rg?rg.lineColor:'rgba(0,0,0,0.35)')));   /* __acad3dV122 */
""")
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
