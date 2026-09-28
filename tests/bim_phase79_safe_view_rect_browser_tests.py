"""
bim_phase79_safe_view_rect_browser_tests.py

Regression suite for __acad3dV79 in canvas_v10.html: framing that respects the floating chrome,
Zoom to Selection, and an honest notice when a handle really is behind the dock.

THE PROBLEM, found while writing the V75 suite rather than by using the app. A grip low on screen
sits behind the tool dock. The dock's container is already pointer-events:none, so most of that
strip passes clicks through -- but the dock BODY, the rounded panel, is solid, and has to be: its
buttons live there. A pointer aimed at a handle beneath it never reached the canvas, nothing
happened, and the app said nothing. The V75 suite had to assert its own drag targets were reachable
to avoid passing for the wrong reason, which is a test working around a product fault.

Making the dock transparent is not the fix -- a click on a toolbar is a click on a toolbar. The fix
is to stop putting the user's work underneath it.

WHY EACH CHECK IS THE ONE THAT WOULD CATCH A REGRESSION:

  1. The safe rectangle is asserted to be MEASURED, not declared: hiding the dock body must remove
     its inset. A hardcoded 133px would pass a "there is an inset" check and then be wrong in every
     workspace, at every window size, and the moment anyone restyles the dock.
  2. Fit is asserted by PROJECTING all eight corners of the model's bounding box and requiring every
     one inside the safe rectangle -- not by checking the camera numbers. The camera is the
     mechanism; where the model lands is the promise.
  3. The centre lands on the safe rectangle's centre to within a pixel. That is what separates the
     projection-derived offset from an approximation: the pan handler's 0.0018 factor is tuned for
     feel and would leave the model a few percent off, which no "is it inside" check would catch.
  4. Asserted in PLAN as well as 3D, because toScreen has a separate flat-mode branch and the aim
     maths has to mirror it. A single-view check would miss half the implementation.
  5. Fit is asserted to include SKETCHES. The old loop read meshOf and skipped anything without a
     mesh, so a drawing made only of sketches fit to nothing at all -- a bug this phase found by
     rewriting the bounds rather than by anyone reporting it.
  6. The occlusion notice is asserted to fire ONLY when a handle is genuinely under the press. A
     generic "something may be hidden" warning on every dock click would be noise, and noise is
     what gets ignored on the one occasion it matters.
  7. The 40% guard degrades to the old behaviour rather than to an unusable sliver, with a console
     warning -- the project's fail-safe rule.

Run:  python3 bim_phase79_safe_view_rect_browser_tests.py [path/to/canvas_v10.html]
"""

import asyncio, pathlib, sys

from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'

# Project all eight corners of a bounding box and report the screen rectangle they span.
BBOX_ON_SCREEN = """(ids)=>{
  const bb=window.__a3dWorldBounds(ids);
  if(!bb)return null;
  const xs=[],ys=[];
  for(let i=0;i<8;i++){
    const q=window.__a3dProject([i&1?bb.mx[0]:bb.mn[0],
                                 i&2?bb.mx[1]:bb.mn[1],
                                 i&4?bb.mx[2]:bb.mn[2]]);
    xs.push(q.x); ys.push(q.y);
  }
  const c=window.__a3dProject([(bb.mn[0]+bb.mx[0])/2,(bb.mn[1]+bb.mx[1])/2,
                               (bb.mn[2]+bb.mx[2])/2]);
  return {l:Math.min(...xs),t:Math.min(...ys),r:Math.max(...xs),b:Math.max(...ys),
          cx:c.x,cy:c.y};}"""


class Checks:
    def __init__(self):
        self.n = 0
        self.failed = []

    def __call__(self, cond, msg):
        self.n += 1
        ok = bool(cond)
        print(("  PASS  " if ok else "  FAIL  ") + msg)
        if not ok:
            self.failed.append(msg)


def inside(box, safe, pad=1.0):
    return (box['l'] >= safe['x'] - pad and box['t'] >= safe['y'] - pad
            and box['r'] <= safe['x'] + safe['w'] + pad
            and box['b'] <= safe['y'] + safe['h'] + pad)


async def run():
    ck = Checks()
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1600, 'height': 950},
                                        device_scale_factor=2)
        page = await ctx.new_page()
        errs, warns = [], []
        page.on('pageerror', lambda e: errs.append(str(e)))
        page.on('console', lambda m: warns.append(m.text) if m.type == 'warning' else None)
        await page.goto('file://' + str(HTML))
        await page.wait_for_timeout(1800)

        has79 = await page.evaluate("()=>!!window.__acad3dV79")
        ck(has79, "__acad3dV79 marker is present")
        if not has79:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.failed), ck.n))
            await browser.close()
            return 1

        print("\n-- 1. the safe rectangle is MEASURED from the live DOM")
        safe = await page.evaluate("()=>window.__a3dSafeViewRect()")
        print("     " + str(safe))
        ck(safe['insets']['bottom'] > 40,
           "the tool dock costs a real bottom inset (%d px)" % safe['insets']['bottom'])
        ck('#a3d-dock .a3d-dockbody' in safe['chrome'],
           "and the dock BODY is what is measured (%s) -- the dock's own container is already "
           "pointer-events:none, so it blocks nothing" % safe['chrome'])
        hidden = await page.evaluate("""()=>{
          const b=document.querySelector('#a3d-dock .a3d-dockbody');
          b.style.display='none';
          const s=window.__a3dSafeViewRect();
          b.style.display='';
          return s;}""")
        ck(hidden['insets']['bottom'] < safe['insets']['bottom'],
           "hiding it SHRINKS the inset (%d -> %d) -- a hardcoded figure would pass a 'there is an "
           "inset' check and then be wrong in every workspace and at every window size"
           % (safe['insets']['bottom'], hidden['insets']['bottom']))
        back = await page.evaluate("()=>window.__a3dSafeViewRect()")
        ck(back['insets']['bottom'] == safe['insets']['bottom'],
           "and showing it again restores it")

        print("\n-- 2. Fit puts the whole model inside that rectangle")
        await page.evaluate("""()=>{
          window.__a3dTestSetObjs([]);
          window.__a3dWall([[0,0],[16,0],[16,11],[0,11]],0.3,3.2,'center',true);
          window.__a3dSet3DView();}""")
        await page.wait_for_timeout(550)
        await page.evaluate("()=>window.__a3dFit()")
        await page.wait_for_timeout(500)
        safe = await page.evaluate("()=>window.__a3dSafeViewRect()")
        box = await page.evaluate(BBOX_ON_SCREEN, None)
        print("     bbox %s in safe %s"
              % ([round(box[k]) for k in 'ltrb'],
                 [round(safe[k]) for k in ('x', 'y', 'w', 'h')]))
        ck(inside(box, safe),
           "every one of the model's eight projected bbox corners lands inside the safe "
           "rectangle -- asserted by projection, not by reading the camera, because the camera is "
           "the mechanism and where the model lands is the promise")
        ck(abs(box['cy'] - (safe['y'] + safe['h'] / 2)) < 1.0
           and abs(box['cx'] - (safe['x'] + safe['w'] / 2)) < 1.0,
           "and its centre is on the safe rectangle's centre to within a pixel (%.2f, %.2f vs "
           "%.1f, %.1f) -- the pan handler's empirical factor would leave it a few percent off, "
           "which no 'is it inside' check would catch"
           % (box['cx'], box['cy'], safe['x'] + safe['w'] / 2, safe['y'] + safe['h'] / 2))
        cvh = await page.evaluate("()=>window.__a3dCanvasMetrics().units[1]")
        ck(box['b'] < cvh - safe['insets']['bottom'] + 1,
           "nothing reaches into the dock strip (bottom of model %d, strip starts at %d)"
           % (round(box['b']), round(cvh - safe['insets']['bottom'])))

        print("\n-- 3. the same holds in PLAN, which has its own projection branch")
        await page.evaluate("()=>window.__a3dSetPlanView()")
        await page.wait_for_timeout(500)
        await page.evaluate("()=>window.__a3dFit()")
        await page.wait_for_timeout(500)
        safeP = await page.evaluate("()=>window.__a3dSafeViewRect()")
        boxP = await page.evaluate(BBOX_ON_SCREEN, None)
        ck(inside(boxP, safeP), "the plan fit lands inside the safe rectangle too")
        ck(abs(boxP['cy'] - (safeP['y'] + safeP['h'] / 2)) < 1.0,
           "and on its centre (%.2f vs %.1f) -- toScreen has a separate flat-mode branch and the "
           "aim maths has to mirror it, so a 3D-only check would miss half the implementation"
           % (boxP['cy'], safeP['y'] + safeP['h'] / 2))
        await page.evaluate("()=>window.__a3dSet3DView()")
        await page.wait_for_timeout(450)

        print("\n-- 4. Fit now includes objects with no mesh")
        await page.evaluate("""()=>{
          window.__a3dTestSetObjs([]);
          window.__a3dSketch('poly',[[20,20],[34,20],[34,31],[20,31]]);
          window.__a3dSetPlanView();}""")
        await page.wait_for_timeout(550)
        await page.evaluate("()=>window.__a3dFit()")
        await page.wait_for_timeout(500)
        sbb = await page.evaluate("()=>window.__a3dWorldBounds(null)")
        ck(sbb is not None and abs(sbb['mn'][0] - 20) < 1e-6 and abs(sbb['mx'][0] - 34) < 1e-6,
           "a sketch contributes to the bounds (%s) -- the old loop read meshOf and skipped "
           "anything without a mesh, so a drawing made only of sketches fit to nothing at all"
           % (sbb and [round(v, 2) for v in sbb['mx']]))
        sSafe = await page.evaluate("()=>window.__a3dSafeViewRect()")
        sBox = await page.evaluate(BBOX_ON_SCREEN, None)
        ck(inside(sBox, sSafe), "and it is framed into the safe rectangle like anything else")
        await page.evaluate("()=>window.__a3dSet3DView()")
        await page.wait_for_timeout(400)

        print("\n-- 5. Zoom to Selection frames just the selection")
        ids = await page.evaluate("""()=>{
          window.__a3dTestSetObjs([]);
          const a=window.__a3dWall([[0,0],[6,0],[6,4],[0,4]],0.3,3,'center',true);
          const b=window.__a3dWall([[60,60],[64,60]],0.3,3,'center',false);
          window.__a3dSet3DView();
          window.__a3dSelectFor([]);
          return {a:a,b:b};}""")
        await page.wait_for_timeout(600)
        await page.evaluate("()=>window.__a3dFit()")
        await page.wait_for_timeout(450)
        wideBox = await page.evaluate(BBOX_ON_SCREEN, None)
        await page.evaluate("(id)=>window.__a3dSelectFor([id])", ids['a'])
        ck(await page.evaluate("()=>window.__a3dZoomToSelection()") is True,
           "Zoom to Selection runs on a selection")
        await page.wait_for_timeout(500)
        zSafe = await page.evaluate("()=>window.__a3dSafeViewRect()")
        zBox = await page.evaluate(BBOX_ON_SCREEN, [ids['a']])
        ck(inside(zBox, zSafe),
           "the selected wall lands inside the safe rectangle")
        ck((zBox['r'] - zBox['l']) > (wideBox['r'] - wideBox['l']) * 0.3,
           "and fills far more of it than when both walls were framed (%d px wide vs %d for the "
           "whole model) -- it zoomed TO the selection, it did not just re-fit everything"
           % (round(zBox['r'] - zBox['l']), round(wideBox['r'] - wideBox['l'])))
        await page.evaluate("()=>window.__a3dSelectFor([])")
        ck(await page.evaluate("()=>window.__a3dZoomToSelection()") is False,
           "with nothing selected it declines rather than doing something arbitrary")

        print("\n-- 6. the occlusion notice fires only when a handle really is under the press")
        # The projection is perspective, so pixels-per-world-unit is not constant across the
        # viewport: one linear solve lands in the right direction but not on the target. Iterating
        # the same solve converges in a few passes, which is all this positioning needs to be.
        placed = None
        for _ in range(8):
            placed = await page.evaluate("""(id)=>{
              window.__a3dSelectFor([id]);
              window.__a3dTestPaint();
              const g=window.__a3dGizmo();
              if(!g)return null;
              const ax=g.arms.filter(a=>a.axis==='x')[0], az=g.arms.filter(a=>a.axis==='z')[0];
              if(!ax||!az)return null;
              const body=document.querySelector('#a3d-dock .a3d-dockbody').getBoundingClientRect();
              const cr=window.__a3dCanvasRect();
              const tx=body.left+body.width/2-cr.left, ty=body.top+body.height/2-cr.top;
              const grip=window.__a3dGrips()[0];
              const dx=tx-grip.x, dy=ty-grip.y;
              const det=ax.sx*az.sy-ax.sy*az.sx;
              if(Math.abs(det)<1e-9)return null;
              const wx=(dx*az.sy-dy*az.sx)/det, wz=(ax.sx*dy-ax.sy*dx)/det;
              // V110: the arms publish their world direction; the Y arm points north (-z)
              window.__a3dMoveObjects([id],ax.dir[0]*wx+az.dir[0]*wz,0,ax.dir[2]*wx+az.dir[2]*wz);
              window.__a3dTestPaint();
              const g2=window.__a3dGrips()[0];
              return {want:[tx,ty],got:[g2.x,g2.y],
                      err:Math.max(Math.abs(g2.x-tx),Math.abs(g2.y-ty)),
                      client:[cr.left+g2.x,cr.top+g2.y],
                      body:[body.left,body.top,body.width,body.height]};}""", ids['a'])
            if placed and placed['err'] < 2:
                break
            await page.wait_for_timeout(80)
        print("     " + str(placed))
        ck(placed and placed['err'] < 2,
           "a grip was manoeuvred under the dock body (%s vs %s)"
           % (placed and [round(v) for v in placed['got']],
              placed and [round(v) for v in placed['want']]))
        covered = await page.evaluate("""(c)=>{
          const e=document.elementFromPoint(c[0],c[1]);
          if(!e)return null;
          // What matters is whether the press lands INSIDE the dock body, not on the body element
          // itself -- it lands on whichever child is there, and the notice listens in the capture
          // phase on the body precisely so any child still reports it.
          return {tag:(e.id||e.className||e.tagName),
                  inDock:!!e.closest('#a3d-dock .a3d-dockbody'),
                  isCanvas:e.id==='a3d-canvas'};}""", placed['client'])
        ck(covered and covered['inDock'] and not covered['isCanvas'],
           "and the pointer lands inside the dock body there, on a child of it rather than the "
           "canvas (%s) -- which is why the notice listens in the capture phase on the body"
           % covered)
        named = await page.evaluate("(c)=>window.__a3dHandleUnderPoint(c[0],c[1])",
                                    placed['client'])
        ck(named is not None and 'handle' in named,
           "the app can name the handle underneath (%s)" % named)
        elsewhere = await page.evaluate("""(b)=>window.__a3dHandleUnderPoint(b[0]+6,b[1]+6)""",
                                        placed['body'])
        ck(elsewhere is None,
           "while a press on another part of the same dock names nothing (%s) -- a generic "
           "'something may be hidden' warning on every dock click would be noise, and noise is "
           "what gets ignored on the one occasion it matters" % elsewhere)
        toasted = await page.evaluate("""(c)=>{
          const t0=document.getElementById('a3d-toast');
          if(t0)t0.textContent='';
          const body=document.querySelector('#a3d-dock .a3d-dockbody');
          body.dispatchEvent(new PointerEvent('pointerdown',
            {clientX:c[0],clientY:c[1],bubbles:true}));
          const t=document.getElementById('a3d-toast');
          return t?t.textContent.trim():null;}""", placed['client'])
        ck(toasted and 'dock' in toasted.lower(),
           "and a real press there tells the user (%r)" % toasted)

        print("\n-- 7. absurd chrome degrades to the old behaviour, loudly")
        warns[:] = []
        guard = await page.evaluate("""()=>{
          const b=document.querySelector('#a3d-dock .a3d-dockbody');
          const old=b.style.height;
          b.style.height='620px';
          const s=window.__a3dSafeViewRect();
          b.style.height=old;
          return s;}""")
        ck(guard['insets']['bottom'] == 0,
           "chrome claiming more than 40%% of the viewport is ignored (inset %d), so the app "
           "frames as it did before rather than into an unusable sliver"
           % guard['insets']['bottom'])
        ck(any('40%' in w or 'chrome' in w.lower() for w in warns),
           "with an explicit console warning (%s)" % (warns[:2] or 'none'))

        print("")
        ck(not errs, "zero uncaught page errors across every probe (%s)" % (errs or 'none'))
        await browser.close()

    print("\n%d/%d checks passed" % (ck.n - len(ck.failed), ck.n))
    if ck.failed:
        print("RESULT: FAIL")
        for m in ck.failed:
            print("   - " + m)
        return 1
    print("RESULT: PASS")
    return 0


sys.exit(asyncio.run(run()))
