"""
bim_phase96_hatch_browser_tests.py

Regression suite for __acad3dV96 in canvas_v10.html: HATCH as a real object, and pattern ANGLE.

WHAT THIS PHASE CLAIMS: a hatch is a closed region carrying its own pattern; it renders in
Technical mode as well as Presentation, unlike every pattern this library drew before; pattern
angle is a real parameter honoured identically by the canvas and by both SVG sinks; HATCH and
HATCHEDIT are reachable; and the two graphics sanitizers became one field validator.

WHY EACH CHECK IS THE ONE THAT WOULD CATCH A REGRESSION:

  1. ANGLE IS DRIVEN INTO BOTH SINKS, not read back from the object. An angle that is stored,
     shown in the panel and ignored by the renderer passes every model check -- the V86 fault.
     The SVG check reads the emitted patternTransform; the canvas check instruments
     CanvasPattern.setTransform and reads the matrix the renderer actually applied.
  2. TWO HATCHES AT DIFFERENT ANGLES MUST PRODUCE TWO <pattern> DEFINITIONS. The registry
     interns by identity, and before this phase the angle was not part of that identity, so the
     second hatch would have referenced the first one's definition and drawn at its angle.
  3. THE SIGN IS ASSERTED, not just the presence of a rotation. Both sinks draw with y
     downward, so a model angle applies as its negative; getting that right in one sink and
     wrong in the other is invisible until someone compares an export with the screen.
  4. RENDERING IN TECHNICAL MODE IS ASSERTED WITH presentMode OFF, because every pattern in
     this build until now was gated on presentation mode and inheriting that gate would make
     the hatch invisible exactly where a drafter works.
  5. BOTH CREATION PATHS ARE DRIVEN -- fill a selected closed sketch, and pick an internal
     point in a region bounded by lines that merely cross.
  6. THE CURVED CASE IS ASSERTED AT pi*r^2, so a hatch traced round a circle keeps the circle.
  7. Zero uncaught page errors, and the V80 shell audit stays clean.

Run:  python3 bim_phase96_hatch_browser_tests.py [path/to/canvas_v10.html]
"""
import asyncio, math, pathlib, sys

from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'


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


def near(a, b, tol=1e-6):
    try:
        return abs(a - b) <= tol
    except TypeError:
        return False


async def palette_run(page, name):
    await page.keyboard.press('Control+k')
    await page.wait_for_timeout(320)
    await page.keyboard.type(name)
    await page.wait_for_timeout(220)
    await page.keyboard.press('Enter')
    await page.wait_for_timeout(420)


async def dlg_ok(page, values=None, selects=None):
    # Guarded: when an earlier step failed there may be no dialog, and page.fill would then
    # block until timeout and end the run instead of failing the next check.
    if not await page.evaluate("()=>!!document.querySelector('.a3d-dlg')"):
        return False
    if selects:
        for sel, val in selects.items():
            await page.select_option('.a3d-dlg [data-a3dp="%s"]' % sel, val)
            await page.wait_for_timeout(70)
    if values:
        for sel, val in values.items():
            await page.fill('.a3d-dlg [data-a3dp="%s"]' % sel, str(val))
            await page.wait_for_timeout(70)
    await page.click('.a3d-dlg [data-a3dlg="ok"]')
    await page.wait_for_timeout(480)
    return True


def line_obj(i, a, b):
    return {'id': 'ck-l%d' % i, 't': 'sketch', 'name': 'L%d' % i, 'col': '#5ec4b8',
            'pos': [0, 0, 0], 'pts': [a, b], 'y': 0, 'closed': False}


async def paint_and_count_patterns(page):
    """Repaint with CanvasPattern instrumented; report the rotations actually applied."""
    return await page.evaluate("""()=>{
      const P=CanvasPattern.prototype;
      const realST=P.setTransform;
      const C=CanvasRenderingContext2D.prototype;
      const realCP=C.createPattern;
      let made=0; const rots=[];
      C.createPattern=function(){made++;return realCP.apply(this,arguments);};
      P.setTransform=function(m){
        try{ rots.push(Math.round(Math.atan2(m.b,m.a)*180/Math.PI*1000)/1000); }catch(e){}
        return realST.apply(this,arguments);
      };
      try{ window.__a3dFit(); }finally{ P.setTransform=realST; C.createPattern=realCP; }
      return {made:made,rots:rots};
    }""")


async def run():
    ck = Checks()
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1600, 'height': 950})
        page = await ctx.new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        await page.goto('file://' + str(HTML))
        await page.wait_for_timeout(2300)
        await page.mouse.click(800, 500)
        await page.wait_for_timeout(250)

        has96 = await page.evaluate("()=>!!window.__acad3dV96")
        ck(has96, "__acad3dV96 marker is present")
        if not has96:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.failed), ck.n))
            await browser.close()
            return 1

        # ------------------------------------------------- 1. the rotation contract
        print("\n-- 1. one rotation function, and the sign it applies")
        ck(await page.evaluate("()=>window.__a3dPatternRotation(30,true)") == -30,
           "a y-down sink applies a model 30 degrees as -30")
        ck(await page.evaluate("()=>window.__a3dPatternRotation(30,false)") == 30,
           "and a y-up sink applies it as +30")
        ck(await page.evaluate("()=>window.__a3dPatternRotation(200,false)") == 20,
           "200 normalises to 20, because a hatch field at 200 IS the field at 20")
        ck(await page.evaluate("()=>window.__a3dPatternRotation(-30,false)") == 150,
           "and -30 normalises to 150")

        print("\n-- 2. the SVG pattern definition carries it")
        d30 = await page.evaluate(
            "()=>window.__a3dPatternSvgDef('p1','diagonal','#555555',1,1,true,30)")
        d0 = await page.evaluate(
            "()=>window.__a3dPatternSvgDef('p1','diagonal','#555555',1,1,true,0)")
        ck('patternTransform="rotate(-30' in d30,
           "angle 30 emits rotate(-30) in a flipped-y export (%s)" % ('yes' if d30 else d30))
        ck('patternTransform' not in d0,
           "angle 0 emits no transform at all, so an unrotated export is byte-identical")
        dup = await page.evaluate(
            "()=>window.__a3dPatternSvgDef('p1','diagonal','#555555',1,1,false,30)")
        ck('patternTransform="rotate(30' in dup,
           "and the same angle in a y-up sink emits +30 (%s)" % ('yes' if dup else dup))

        # ------------------------------------------------- 3. the hatch object
        print("\n-- 3. a hatch is a closed region with a pattern")
        await page.evaluate("()=>window.__a3dTestSetObjs([])")
        hid = await page.evaluate("""()=>window.__a3dAddHatch(
            [[0,0],[4,0],[4,3],[0,3]],null,0,
            {pattern:'diagonal',patternAngle:30,patternScale:2})""")
        ck(await page.evaluate("(id)=>window.__a3dIsHatch(id)", hid),
           "the engine recognises it as a hatch")
        area = await page.evaluate("(id)=>window.__a3dHatchArea(id)", hid)
        ck(near(area, 12, 1e-9), "its area is exactly 12 m2 (%.9f)" % area)
        g = await page.evaluate("(id)=>window.__a3dHatchGraphics(id)", hid)
        ck(g and g['pattern'] == 'diagonal' and near(g['patternAngle'], 30)
           and near(g['patternScale'], 2),
           "and its appearance carries pattern, angle and scale (%s)" % g)
        clamped = await page.evaluate("""()=>{
            const id=window.__a3dAddHatch([[0,0],[1,0],[1,1]],null,0,
              {pattern:'cross',patternAngle:200,patternScale:99});
            return window.__a3dHatchGraphics(id);}""")
        ck(near(clamped['patternAngle'], 20) and near(clamped['patternScale'], 8),
           "an out-of-range angle and scale are clamped by the shared validator (%s deg, %s)"
           % (clamped['patternAngle'], clamped['patternScale']))

        # ------------------------------------------------- 4. it draws in TECHNICAL mode
        print("\n-- 4. it draws in Technical mode, which no pattern in this build did before")
        await page.evaluate("()=>window.__a3dSetPresentMode(false)")
        await page.wait_for_timeout(200)
        ck(await page.evaluate("()=>window.__a3dPresentMode()") is False,
           "presentation mode is OFF for this measurement")
        await page.evaluate("()=>window.__a3dTestSetObjs([])")
        await page.evaluate("""()=>window.__a3dAddHatch([[0,0],[6,0],[6,6],[0,6]],null,0,
            {pattern:'diagonal',patternAngle:30,patternScale:1})""")
        await page.wait_for_timeout(200)
        r = await paint_and_count_patterns(page)
        ck(r['made'] >= 1,
           "painting builds a canvas pattern with presentMode off (%d)" % r['made'])
        ck(any(near(x, -30, 0.01) for x in r['rots']),
           "and rotates it by -30, the same sign the SVG sink uses (%s)" % r['rots'])
        # and an unrotated hatch must not rotate at all
        await page.evaluate("()=>window.__a3dTestSetObjs([])")
        await page.evaluate("""()=>window.__a3dAddHatch([[0,0],[6,0],[6,6],[0,6]],null,0,
            {pattern:'diagonal',patternAngle:0,patternScale:1})""")
        await page.wait_for_timeout(200)
        r0 = await paint_and_count_patterns(page)
        ck(r0['made'] >= 1 and not r0['rots'],
           "an unrotated hatch applies no transform at all (%s)" % r0['rots'])

        # ------------------------------------------------- 5. two angles, two definitions
        print("\n-- 5. the angle is part of the pattern's identity")
        await page.evaluate("()=>window.__a3dTestSetObjs([])")
        await page.evaluate("""()=>{
            window.__a3dAddHatch([[0,0],[4,0],[4,4],[0,4]],null,0,
              {pattern:'diagonal',patternAngle:0,patternScale:1});
            window.__a3dAddHatch([[6,0],[10,0],[10,4],[6,4]],null,0,
              {pattern:'diagonal',patternAngle:30,patternScale:1});}""")
        await page.wait_for_timeout(250)
        svg = await page.evaluate("()=>window.__a3dBuildSVG('technical')")
        # bimBuildSVG returns {text, stats}
        text = svg if isinstance(svg, str) else (svg or {}).get('text', '')
        ck(text.count('<pattern ') == 2,
           "two hatches at different angles emit TWO pattern definitions, not one shared (%d)"
           % text.count('<pattern '))
        ck('rotate(-30' in text,
           "and the rotated one carries its transform into the export")

        # ------------------------------------------------- 6. HATCH, both creation paths
        print("\n-- 6. HATCH from a selected closed sketch")
        await page.evaluate("()=>window.__a3dTestSetObjs([])")
        sid = await page.evaluate("()=>window.__a3dSketch('poly',[[0,0],[5,0],[5,4]])")
        await page.evaluate("(id)=>window.__a3dSelectFor([id])", sid)
        await palette_run(page, 'HATCH')
        ck(await page.evaluate("()=>!!document.querySelector('.a3d-dlg')"),
           "HATCH opens its dialog from the palette -- it was unreachable before this phase")
        await dlg_ok(page, {'ang': 45, 'sc': 1.5}, {'pat': 'cross'})
        objs = await page.evaluate("()=>window.__a3dState().objs")
        hs = [o for o in objs if o.get('t') == 'hatch']
        ck(len(hs) == 1, "one hatch created on the selected sketch (%d)" % len(hs))
        if hs:
            a = await page.evaluate("(id)=>window.__a3dHatchArea(id)", hs[0]['id'])
            ck(near(a, 10, 1e-9), "with the triangle's exact area of 10 m2 (%.9f)" % a)
            ck(hs[0]['pattern'] == 'cross' and near(hs[0]['patternAngle'], 45)
               and near(hs[0]['patternScale'], 1.5),
               "and the pattern, angle and scale the dialog was given (%s)"
               % {k: hs[0].get(k) for k in ('pattern', 'patternAngle', 'patternScale')})

        print("\n-- 7. HATCH by picking an internal point in a traced region")
        GRID = [line_obj(1, [-5, 0], [5, 0]), line_obj(2, [-5, 1], [5, 1]),
                line_obj(3, [0, -5], [0, 5]), line_obj(4, [1, -5], [1, 5])]
        await page.evaluate("(o)=>window.__a3dTestSetObjs(o)", GRID)
        await page.wait_for_timeout(150)
        await palette_run(page, 'HATCH')
        await dlg_ok(page, {'ang': 0, 'sc': 1}, {'pat': 'diagonal'})
        st = await page.evaluate("()=>window.__a3dState()")
        ck(st['sk'] and st['sk']['tool'] == 'hatch',
           "with nothing selected it enters the pick tool (%s)" % (st['sk'] and st['sk']['tool']))
        await page.evaluate("()=>window.__a3dPlacePoint(0.5,0.5)")
        await page.wait_for_timeout(420)
        objs = await page.evaluate("()=>window.__a3dState().objs")
        hs = [o for o in objs if o.get('t') == 'hatch']
        ck(len(hs) == 1, "clicking inside makes one hatch (%d)" % len(hs))
        if hs:
            a = await page.evaluate("(id)=>window.__a3dHatchArea(id)", hs[0]['id'])
            ck(near(a, 1, 1e-9),
               "bounded by four lines that merely cross, area exactly 1 m2 (%.9f)" % a)
        st = await page.evaluate("()=>window.__a3dState()")
        ck(st['sk'] and st['sk']['tool'] == 'hatch', "and the command stays live")
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(150)

        print("\n-- 8. a curved region keeps its curve")
        await page.evaluate("""()=>window.__a3dTestSetObjs([{id:'ck-c',t:'sketch',name:'C',
            col:'#5ec4b8',pos:[0,0,0],pts:[[-2,0],[2,0]],bulges:[1,1],y:0}])""")
        await page.wait_for_timeout(150)
        cid = await page.evaluate("(id)=>window.__a3dSelectFor([id])", 'ck-c')
        await palette_run(page, 'HATCH')
        await dlg_ok(page, {'ang': 0, 'sc': 1}, {'pat': 'diagonal'})
        objs = await page.evaluate("()=>window.__a3dState().objs")
        hs = [o for o in objs if o.get('t') == 'hatch']
        ck(len(hs) == 1 and hs[0].get('bulges'),
           "hatching a circle keeps the bulges (%s)"
           % (hs[0].get('bulges') if hs else None))
        if hs:
            a = await page.evaluate("(id)=>window.__a3dHatchArea(id)", hs[0]['id'])
            ck(near(a, math.pi * 4, 1e-9), "and its area is exactly pi*r^2 (%.9f)" % a)

        # ------------------------------------------------- 9. HATCHEDIT
        print("\n-- 9. HATCHEDIT changes one that already exists")
        hid = hs[0]['id'] if hs else None
        await page.evaluate("(id)=>window.__a3dSelectFor([id])", hid)
        await palette_run(page, 'HATCHEDIT')
        ck(await page.evaluate("()=>!!document.querySelector('.a3d-dlg')"),
           "HATCHEDIT opens on a selected hatch")
        hd = await page.evaluate(
            "()=>{const d=document.querySelector('.a3d-dlghd');return d?d.textContent:null;}")
        ck(hd == 'Hatch edit', "as the edit dialog, not a new one (%s)" % hd)
        await dlg_ok(page, {'ang': 135, 'sc': 3}, {'pat': 'steel'})
        snap = await page.evaluate("(id)=>window.__a3dObjSnapshot(id)", hid) if hid else None
        ck(snap and snap.get('pattern') == 'steel' and near(snap.get('patternAngle'), 135)
           and near(snap.get('patternScale'), 3),
           "and the hatch changed (%s)"
           % ({k: snap.get(k) for k in ('pattern', 'patternAngle', 'patternScale')}
              if snap else 'no hatch to edit'))
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(120)
        no_sel = await page.evaluate("()=>{window.__a3dSelectFor([]);return true;}")
        await palette_run(page, 'HATCHEDIT')
        ck(not await page.evaluate("()=>!!document.querySelector('.a3d-dlg')"),
           "with nothing selected it refuses rather than opening on nothing")

        # A selected non-hatch must come through HATCHEDIT unchanged. Asserting the dialog
        # stays shut is not enough on its own: a build that opens it anyway and writes pattern
        # fields onto a wall would leave the wall quietly altered.
        await page.evaluate("()=>window.__a3dTestSetObjs([])")
        wall0 = await page.evaluate(
            "()=>window.__a3dCurvedWall([[0,0],[4,0]],null,0.3,3,'center',false)")
        await page.wait_for_timeout(250)
        await page.evaluate("(id)=>window.__a3dSelectFor([id])", wall0)
        before_wall = await page.evaluate("(id)=>window.__a3dObjSnapshot(id)", wall0)
        await palette_run(page, 'HATCHEDIT')
        await dlg_ok(page, {'ang': 90, 'sc': 5})
        after_wall = await page.evaluate("(id)=>window.__a3dObjSnapshot(id)", wall0)
        ck(after_wall is not None and after_wall.get('pattern') is None
           and after_wall.get('patternAngle') is None,
           "HATCHEDIT on a wall leaves the wall untouched (%s)"
           % {k: after_wall.get(k) for k in ('pattern', 'patternAngle')})
        ck(before_wall is not None and after_wall is not None
           and before_wall.get('name') == after_wall.get('name'),
           "and does not rename or replace it")
        # The dialog has its own guard, so bimApplyHatchEdit's guard is reachable only through
        # the exported entry point -- which is where it has to be driven, or it is a guard
        # nothing tests sitting behind a guard everything tests.
        direct = await page.evaluate(
            "(id)=>window.__a3dApplyHatchEdit(id,{pattern:'steel',patternAngle:90,patternScale:2})",
            wall0)
        ck(direct is None, "and applying a hatch edit to a wall directly is refused (%s)" % direct)
        after2 = await page.evaluate("(id)=>window.__a3dObjSnapshot(id)", wall0)
        ck(after2 is not None and after2.get('pattern') is None,
           "leaving the wall without hatch fields (%s)" % (after2 or {}).get('pattern'))

        # ------------------------------------------------- 10. the shared field validator
        print("\n-- 10. one field validator for both sanitizers")
        await page.evaluate("()=>window.__a3dTestSetObjs([])")
        wid = await page.evaluate(
            "()=>window.__a3dCurvedWall([[0,0],[5,0]],null,0.3,3,'center',false)")
        await page.wait_for_timeout(250)
        await page.evaluate(
            "(id)=>window.__a3dSetGraphicsOverride(id,'technical','patternAngle',60)", wid)
        rgv = await page.evaluate("(id)=>window.__a3dResolveGraphics(id,'technical')", wid)
        ck(rgv and near(rgv['patternAngle'], 60),
           "an instance override carries patternAngle through resolution (%s)"
           % (rgv.get('patternAngle') if rgv else None))
        await page.evaluate(
            "(id)=>window.__a3dSetGraphicsOverride(id,'technical','patternAngle',200)", wid)
        rgv = await page.evaluate("(id)=>window.__a3dResolveGraphics(id,'technical')", wid)
        ck(rgv and near(rgv['patternAngle'], 20),
           "and it is normalised by the same rule the hatch uses (%s)"
           % (rgv.get('patternAngle') if rgv else None))

        # ------------------------------------------------- 11. DXF
        print("\n-- 11. the DXF says what it can carry")
        await page.evaluate("()=>window.__a3dTestSetObjs([])")
        d0 = await page.evaluate("()=>window.__a3dBuildDXF().stats")
        await page.evaluate("""()=>window.__a3dAddHatch([[0,0],[4,0],[4,4],[0,4]],null,0,
            {pattern:'diagonal',patternAngle:0,patternScale:1})""")
        await page.wait_for_timeout(200)
        d1 = await page.evaluate("()=>window.__a3dBuildDXF().stats")
        ck(d1.get('hatch') == 1,
           "the export counts the hatch (%s)" % d1.get('hatch'))
        # the counter is named by the entity the builder writes; read it rather than assume it
        key = 'lwpolyline' if 'lwpolyline' in d0 else 'polyline'
        ck(d1.get(key) == d0.get(key, 0) + 1,
           "and writes its BOUNDARY as one closed %s -- R12 has no HATCH entity (%s -> %s)"
           % (key.upper(), d0.get(key), d1.get(key)))

        # The sheet-SVG sink cannot be driven without building a sheet viewport, so what is
        # asserted about it is structural: that no presentation gate was left behind anywhere.
        # This is the same technique V95 used to prove a deleted tracer had not been parked.
        print("\n-- 11b. every pattern gate asks the one predicate")
        src_txt = await page.evaluate("()=>document.documentElement.outerHTML")
        ck(src_txt.count('bimPatternAlways(') == 5,
           "bimPatternAlways has one definition and four call sites (%d)"
           % src_txt.count('bimPatternAlways('))
        ck('if(!pres||!rg)' not in src_txt and 'if(!pres||!cmd.rg)' not in src_txt,
           "and no sink still decides the question for itself")

        # ------------------------------------------------- 12. hygiene
        print("\n-- 12. hygiene")
        audit = await page.evaluate("()=>window.__a3dShellAudit()")
        bad = [k for k, v in (audit or {}).items()
               if isinstance(v, list) and v] if isinstance(audit, dict) else []
        ck(not bad, "V80 shell audit is clean (%s)" % (bad or 'clean'))
        ck(not errs, "no uncaught page errors (%s)" % (errs[:3] or 'none'))

        passed = ck.n - len(ck.failed)
        print("\n%d/%d checks passed" % (passed, ck.n))
        print("RESULT: %s" % ('PASS' if not ck.failed else 'FAIL'))
        if ck.failed:
            print("FAILURES:")
            for f in ck.failed:
                print("  - " + f)
        await browser.close()
        return 1 if ck.failed else 0


if __name__ == '__main__':
    sys.exit(asyncio.run(run()))
