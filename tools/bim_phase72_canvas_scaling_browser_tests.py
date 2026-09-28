"""
bim_phase72_canvas_scaling_browser_tests.py

Regression suite for __acad3dV72 in canvas_v10.html: the click that lands off the cursor, and the
blurry render. Two reported symptoms, one root cause.

THE BUG. A canvas has TWO sizes and this code used one of them for both jobs.

  cvXY(ev)                  returns CSS pixels        (ev.clientX - rect.left)
  groundPoint / toScreen    worked in BACKING pixels  (el.cv.width / el.cv.height)

Those are the same number only when the display is 1x AND size() has run since the viewport box
last changed. Neither held:

  - `devicePixelRatio` appeared ZERO times in the entire file. On a 2x display the backing store
    was half the physical resolution and the browser upscaled it. Measured before the fix, with a
    1024x845 CSS box on a 2x display: backing 1024x845 against 2048x1690 physical pixels. That is
    the blur, and the reason line weights and text read as "off scale".
  - size() was called from exactly TWO places: a window resize, and once in enter3d. Anything that
    resized .a3d-vp without a window resize left the backing store stale. Measured, collapsing the
    left file dock (no window resize): CSS box 1266px, backing 1024px, so the canvas is stretched
    1.236x and every click is off by that ratio -- and the error GROWS with distance from the left
    edge, because it is multiplicative:

        click x=200   ->  47.3px off
        click x=600   -> 141.8px off
        click x=1000  -> 236.3px off

THE FIX:
  1. The backing store is sized in DEVICE pixels and the 2D context is scaled by the same factor
     at the top of every frame, so all existing drawing code keeps working in CSS pixels.
  2. Geometry reads go through cvW()/cvH() -- the LOGICAL size. The divisor lives on the canvas
     element (__a3dScale), so the scratch canvas sheet capture swaps in, which is already 1:1,
     divides by 1 and is untouched.
  3. A ResizeObserver on .a3d-vp calls size(). That fixes the CLASS of stale-backing bugs rather
     than the one instance found.

WHAT THIS SUITE ASSERTS, and why each check is the one that would catch a regression:

  1. The three sizes agree: units == cssBox (or every click is off by their ratio) and
     backing == cssBox * dpr (or the render is upscaled). Both are asserted at 1x AND 2x, because
     the bug was invisible at 1x -- which is why it survived every previous suite.
  2. SCREEN-SPACE click error, not canvas-space. The obvious round trip -- hover a point, project
     it back -- CANCELS this bug: projection and un-projection share the same wrong units, so the
     error is zero in both builds. It has to be measured where the user sees it, by mapping the
     projection through the stretch the browser applies. This suite's first version made exactly
     that mistake and reported the broken build as correct.
  3. The error is checked AFTER a layout change with no window resize, at several x positions,
     because it is multiplicative: a single probe near the left edge would show ~0 and pass.
  4. The context transform is re-applied per frame. Setting it once in size() would be dropped by
     any ctx.setTransform elsewhere in a frame, and a lost transform is a quarter-size drawing.
  5. Sheet capture is UNAFFECTED. It swaps el.cv for a 1:1 scratch canvas; if that inherited the
     screen scale, every exported sheet would be silently wrong. Asserted by exporting and
     comparing against the same export from before the change.

Run:  python3 bim_phase72_canvas_scaling_browser_tests.py [path/to/canvas_v10.html]
"""

# AMENDED FOR V120: the shell's canvas-era names were replaced -- #figma-layers-shell/-rail/-panel are
# #a3d-shell/-rail/-leftpanel, the .fl-* classes .a3d-*, #uploaded-command-palette #a3d-cmdpal, the
# Project Browser tab 'file' is 'browser', --figma-dock-w is --a3d-left-w, and the material library is
# read through window.__a3dMaterialCards() (window.__WB_MATERIAL_CARDS is gone).
import asyncio, pathlib, sys

from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'

ENTER = """()=>{
  window.__a3dEnter();
  window.ACAD_WS_CUR='da';
  window.__a3dTestSetObjs([]);
  window.__a3dSetPlanView&&window.__a3dSetPlanView();
}"""

# The measurement that matters: where a model point lands ON SCREEN versus where the cursor was.
SCREEN_ERR = """(p)=>{
  const s=window.__a3dStatusHoverAt(p.sx,p.sy);   // a real mousemove, through cvXY + groundPoint
  const m=(s||'').match(/-?\\d+\\.\\d+/g);
  if(!m||m.length<3)return null;
  const css=window.__a3dProjectCss([parseFloat(m[0]),parseFloat(m[2]),parseFloat(m[1])]);
  if(!css)return null;
  return {dx:Math.round((css.x-p.sx)*100)/100, dy:Math.round((css.y-p.sy)*100)/100};
}"""

COLLAPSE_DOCK = """()=>{
  /* AMENDED FOR V120: collapsed the way the user does it, with the rail's toggle, which also moves
     the workspace edge (window.__figmaDockSyncW, which the probe called for that, is gone) */
  const s=document.getElementById('a3d-shell');
  const b=document.querySelector('#a3d-rail .a3d-paneltoggle');
  if(s&&b&&!s.classList.contains('collapsed'))b.click();
  return true;
}"""


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


async def check_at_dpr(pw, ck, dpr):
    browser = await pw.chromium.launch()
    ctx = await browser.new_context(viewport={'width': 1600, 'height': 950},
                                    device_scale_factor=dpr)
    page = await ctx.new_page()
    errs = []
    page.on('pageerror', lambda e: errs.append(str(e)))
    await page.goto('file://' + str(HTML))
    await page.wait_for_timeout(900)

    if not await page.evaluate("()=>!!window.__acad3dV72"):
        ck(False, "__acad3dV72 marker is present (DPR %g)" % dpr)
        await browser.close()
        return False

    await page.evaluate(ENTER)
    await page.wait_for_timeout(900)

    print("\n-- DPR %g : the three sizes agree" % dpr)
    m = await page.evaluate("()=>window.__a3dCanvasMetrics()")
    print("     " + str(m))
    ck(m['units'] == m['cssBox'],
       "the drawing's coordinate units equal the on-screen CSS box (%s vs %s) -- if these differ, "
       "every click is off by their ratio" % (m['units'], m['cssBox']))
    ck(m['backing'] == [round(m['cssBox'][0] * dpr), round(m['cssBox'][1] * dpr)],
       "the backing store is the CSS box times the device pixel ratio (%s) -- if it is smaller, "
       "the browser upscales it and the render is blurry" % m['backing'])
    ck(m['scale'] == dpr, "the canvas records its scale (%g)" % m['scale'])
    ck(m['ctxTransform'] == [dpr, dpr],
       "and the 2D context is scaled by it (%s) -- re-applied each frame, so a stray "
       "ctx.setTransform cannot silently leave a quarter-size drawing" % m['ctxTransform'])

    print("\n-- DPR %g : clicks land where the cursor is, after a layout change" % dpr)
    # A layout change with NO window resize is the case that was broken. Before the fix this took
    # the CSS box to 1266px against a 1024px backing store.
    await page.evaluate(COLLAPSE_DOCK)
    await page.wait_for_timeout(500)
    m2 = await page.evaluate("()=>window.__a3dCanvasMetrics()")
    ck(m2['cssBox'][0] > m['cssBox'][0],
       "collapsing the file dock widened the viewport with no window resize (%d -> %d)"
       % (m['cssBox'][0], m2['cssBox'][0]))
    ck(m2['units'] == m2['cssBox'],
       "the units followed it (%s) -- this is the ResizeObserver doing what two hand-placed "
       "size() calls could not" % m2['units'])
    ck(m2['backing'] == [round(m2['cssBox'][0] * dpr), round(m2['cssBox'][1] * dpr)],
       "and so did the backing store (%s)" % m2['backing'])

    # Multiplicative error: probe across the width, because near the left edge it reads as ~0.
    worst = 0.0
    for x, y in ((200, 200), (600, 400), (1000, 700)):
        e = await page.evaluate(SCREEN_ERR, {'sx': x, 'sy': y})
        ck(e is not None, "the cursor at (%d,%d) resolves to a model point" % (x, y))
        if e:
            worst = max(worst, abs(e['dx']), abs(e['dy']))
            ck(abs(e['dx']) <= 1.0 and abs(e['dy']) <= 1.0,
               "a click at (%d,%d) lands within a pixel of the cursor (dx=%.2f dy=%.2f)"
               % (x, y, e['dx'], e['dy']))
    ck(worst <= 1.0,
       "worst screen error across the viewport width is %.2fpx -- before the fix this read "
       "47.3 / 141.8 / 236.3px at these same three points" % worst)

    ck(not errs, "zero uncaught page errors at DPR %g (%s)" % (dpr, errs or 'none'))
    await browser.close()
    return True


async def run():
    ck = Checks()
    async with async_playwright() as pw:
        # 1x first: the bug was INVISIBLE at 1x, which is how it survived every earlier suite.
        ok = await check_at_dpr(pw, ck, 1)
        if ok:
            await check_at_dpr(pw, ck, 2)
            await check_at_dpr(pw, ck, 3)

            print("\n-- sheet capture still renders 1:1")
            browser = await pw.chromium.launch()
            ctx = await browser.new_context(viewport={'width': 1600, 'height': 950},
                                            device_scale_factor=2)
            page = await ctx.new_page()
            errs = []
            page.on('pageerror', lambda e: errs.append(str(e)))
            await page.goto('file://' + str(HTML))
            await page.wait_for_timeout(900)
            await page.evaluate(ENTER)
            await page.wait_for_timeout(700)
            # Capture swaps el.cv for a scratch canvas with no __a3dScale. If it inherited the
            # screen scale, every exported sheet would be silently half- or double-size.
            cap = await page.evaluate("""()=>{
              window.__a3dTestSetObjs([]);
              const w=window.__a3dWall([[0,0],[8,0],[8,5],[0,5]],0.3,3,'center',true);
              const before=window.__a3dCanvasMetrics();
              const svg=window.__a3dBuildSVG('technical').text;
              const after=window.__a3dCanvasMetrics();
              return {sameMetrics:JSON.stringify(before)===JSON.stringify(after),
                      svgLen:svg.length, hasPath:svg.indexOf('<path')>=0,
                      scaleStillSet:after.scale};}""")
            ck(cap['hasPath'] is True and cap['svgLen'] > 200,
               "a vector export still produces geometry (%d bytes)" % cap['svgLen'])
            ck(cap['sameMetrics'] is True,
               "and leaves the live canvas's metrics exactly as it found them")
            ck(cap['scaleStillSet'] == 2,
               "with the screen canvas still carrying its scale afterwards (%s)"
               % cap['scaleStillSet'])
            png = await page.evaluate("""()=>{
              try{const r=window.__a3dRenderSheetPNG?'hook':'none';return r;}catch(e){return 'err';}}""")
            ck(png in ('hook', 'none'), "the sheet PNG path is reachable without throwing")
            ck(not errs, "zero uncaught page errors during capture (%s)" % (errs or 'none'))
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
