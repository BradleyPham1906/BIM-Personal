"""
bim_phase103_site_property_browser_tests.py

Regression suite for __acad3dV103 in canvas_v10.html: property lines from a survey, setbacks and
true north -- the first phase of the site track.

WHY EACH CHECK IS THE ONE THAT WOULD CATCH A REGRESSION:

  1. THE BEARING ARITHMETIC IS CHECKED AGAINST HAND VALUES in all four quadrants, in the notations
     a deed actually uses, and the malformed bearings a typo produces are refused, not guessed.
  2. CLOSURE is checked on a parcel that closes and on one that misses by exactly 10 mm, with the
     precision ratio computed independently here.
  3. TRUE NORTH turns a traverse: a leg due north with True North at 30 degrees must land at
     (50, -86.603), computed here, not read back from the app.
  4. THE DIALOG IS DRIVEN: opened from the ribbon, typed into, its closure read before OK, a bad
     line refused with its line number.
  5. SETBACKS are asserted on the buildable area the offsets leave, per side and all sides, and the
     VIOLATION list names exactly the element that crosses the setback line.
  6. The north arrow points where True North says, through the camera.
  7. Undo, reload, the DXF, and a mouse pick of the line.

Run:  python3 bim_phase103_site_property_browser_tests.py [path/to/canvas_v10.html]
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


SQUARE = "N 00 00 00 E 100\nN 90 00 00 E 100\nS 00 00 00 E 100\nS 90 00 00 W 100"


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

        has = await page.evaluate("()=>!!window.__acad3dV103")
        ck(has, "__acad3dV103 marker is present")
        if not has:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.failed), ck.n))
            await browser.close()
            return 1

        async def ev(js, arg=None):
            return await page.evaluate(js, arg)

        async def objs(t=None):
            os_ = await ev("()=>window.__a3dState().objs")
            return [o for o in os_ if t is None or o.get('t') == t]

        async def toast():
            return await ev("()=>{const t=document.getElementById('a3d-toast');return t?t.textContent:'';}")

        async def fill(sel, v):
            # a missing field makes the NEXT check fail; it must never end the run
            if await page.query_selector(sel) is None:
                return False
            await page.fill(sel, v, timeout=3000)
            return True

        async def dispatch(sel):
            if await page.query_selector(sel) is None:
                return False
            await page.dispatch_event(sel, 'change', timeout=3000)
            return True

        await ev("()=>{window.__a3dTestSetObjs([]);window.__a3dFlat(true);window.__a3dSetTrueNorth(0);}")

        # ------------------------------------------------ 1. bearings
        print("\n-- 1. bearings, in every quadrant and notation")
        cases = [('N 45 30 00 E', 45.5), ('S 45 30 00 E', 134.5), ('S 10 00 00 W', 190.0),
                 ('N 10 00 00 W', 350.0), ('N45-30-00E', 45.5), ('N 45d30m00s E', 45.5),
                 ('N 45.5 E', 45.5), ('S 89 59 59.5 E', 90.0 + 0.5 / 3600)]
        for s, want in cases:
            r = await ev("(s)=>window.__a3dParseBearing(s)", s)
            ck(r and near(r.get('az'), want, 1e-9), "%-16s -> azimuth %.6f (%s)" % (s, want, r))
        for s in ('N 95 E', 'N 45 61 00 E', 'X 10 E', 'N 45.5 30 E', ''):
            r = await ev("(s)=>window.__a3dParseBearing(s)", s)
            ck(r and r.get('error'), "%r is refused, not guessed (%s)" % (s, r and r.get('error')))
        f = await ev("()=>window.__a3dFormatBearing(134.5,' ')")
        ck(f == 'S 45 30\'00" E', "azimuth 134.5 formats back to S 45 30'00\" E (%r)" % f)

        # ------------------------------------------------ 2. closure
        print("\n-- 2. closure")
        pl = await ev("(t)=>window.__a3dParseLegs(t)", SQUARE)
        tr = await ev("(l)=>window.__a3dTraverse([0,0],l,0)", pl['legs'])
        ck(not pl['errors'] and near(tr['misclosure'], 0, 1e-9) and near(tr['area'], 10000, 1e-6) and near(tr['perimeter'], 400, 1e-9),
           "a 100 m square closes exactly: area 10000 m2, perimeter 400 m")
        pl2 = await ev("(t)=>window.__a3dParseLegs(t)", SQUARE.replace('W 100', 'W 99.99'))
        tr2 = await ev("(l)=>window.__a3dTraverse([0,0],l,0)", pl2['legs'])
        ck(near(tr2['misclosure'], 0.01, 1e-9) and near(tr2['precision'], 399.99 / 0.01, 1e-3),
           "a last leg 10 mm short misses by 0.010 m, precision 1:%d (%.3f, %.1f)"
           % (round(399.99 / 0.01), tr2['misclosure'], tr2['precision']))
        bad = await ev("(t)=>window.__a3dParseLegs(t)", "N 0 E 100\nN 91 E 50\nS 0 E\nN 90 E 20")
        ck(any('line 2' in e for e in bad['errors']) and any('line 3' in e for e in bad['errors']),
           "bad legs are reported by line number (%s)" % bad['errors'])

        # ------------------------------------------------ 3. true north
        print("\n-- 3. true north turns the traverse")
        tr3 = await ev("()=>window.__a3dTraverse([0,0],[{az:0,d:100}],30)")
        ck(near(tr3['end'][0], 50.0, 1e-9) and near(tr3['end'][1], -100 * math.cos(math.radians(30)), 1e-9),
           "a leg due north with True North at 30 deg ends at (50, -86.603) (%s)" % tr3['end'])

        # ------------------------------------------------ 4. the dialog
        print("\n-- 4. the Property Line dialog, from the ribbon")
        await ev("()=>{const e=document.querySelector('[data-a3dr=\"bim:property\"]');if(e)e.click();}")
        await page.wait_for_timeout(250)
        ta = await page.query_selector('.a3d-dlg [data-a3dp="legs"]')
        ck(ta is not None, "the ribbon's Property Line button opens the dialog")
        if ta:
            await fill('.a3d-dlg [data-a3dp="legs"]', SQUARE.replace('W 100', 'W 99.99'))
            await page.wait_for_timeout(150)
            cl = await ev("()=>{const e=document.querySelector('.a3d-dlg [data-a3dp=\"closure\"]');return e?e.textContent:'';}")
            ck('misclosure 0.010' in cl and '1:39999' in cl, "the closure is shown before OK (%r)" % cl)
            await fill('.a3d-dlg [data-a3dp="legs"]', "N 0 E 100\nN 91 E 50\nS 0 E 100")
            await page.wait_for_timeout(100)
            await ev("()=>{const b=document.querySelector('.a3d-dlg [data-a3dlg=\"ok\"]');if(b)b.click();}")
            er = await ev("()=>{const e=document.querySelector('.a3d-dlg #a3d-dlgerr');return e?e.textContent:null;}")
            ck(er and 'line 2' in er and not await objs('property'), "OK with a bad line is refused and says which (%r)" % er)
            await fill('.a3d-dlg [data-a3dp="legs"]', SQUARE)
            await fill('.a3d-dlg [data-a3dp="sx"]', '10')
            await fill('.a3d-dlg [data-a3dp="sy"]', '20')
            await ev("()=>{const b=document.querySelector('.a3d-dlg [data-a3dlg=\"ok\"]');if(b)b.click();}")
            await page.wait_for_timeout(200)
        props = await objs('property')
        pid = props[0]['id'] if props else None
        g = await ev("(id)=>window.__a3dPropertyGeometry(id)", pid)
        ck(g and near(g['ring'][1][0], 10, 1e-9) and near(g['ring'][1][1], -80, 1e-9) and near(g['area'], 10000, 1e-6),
           "OK makes the parcel from (10,20): first leg north to (10,-80), area 10000 (%s)" % (g and g['ring'][:2]))
        await ev("()=>window.__a3dUndo()")
        await page.wait_for_timeout(150)
        ck(not await objs('property'), "Undo removes it")

        # ------------------------------------------------ 5. from a shape; setbacks; violations
        print("\n-- 5. a parcel from a drawn shape, setbacks and violations")
        await ev("""()=>window.__a3dTestSetObjs([{id:'LOT',t:'sketch',name:'LOT',col:'#5ec4b8',pos:[0,0,0],
            pts:[[0,0],[30,0],[30,20],[0,20]],y:0}])""")
        await ev("()=>window.__a3dSelectFor(['LOT'])")
        await ev("()=>{const e=document.querySelector('[data-a3dr=\"bim:propshape\"]');if(e)e.click();}")
        await page.wait_for_timeout(200)
        props = await objs('property')
        pid = props[0]['id'] if props else None
        g = await ev("(id)=>window.__a3dPropertyGeometry(id)", pid)
        legs = props[0]['legs'] if props else []
        ck(len(legs) == 4 and near(legs[0]['az'], 90, 1e-9) and near(legs[1]['az'], 180, 1e-9) and g and near(g['misclosure'], 0, 1e-9) and near(g['area'], 600, 1e-6),
           "a 30 x 20 rectangle becomes 4 legs, first due east then due south, closing on 600 m2")
        await ev("(id)=>{window.__a3dSelectFor([id]);window.__a3dRefreshProps();}", pid)
        await fill('[data-propsetback="all"]', '3')
        await dispatch('[data-propsetback="all"]')
        await page.wait_for_timeout(150)
        g = await ev("(id)=>window.__a3dPropertyGeometry(id)", pid)
        sa = abs(sum(g['setback']['ring'][i][0] * g['setback']['ring'][(i + 1) % 4][1] - g['setback']['ring'][(i + 1) % 4][0] * g['setback']['ring'][i][1] for i in range(4))) / 2 if g and g.get('setback') and g['setback'].get('ring') else None
        ck(near(sa, 24 * 14, 1e-6), "3 m on all sides leaves a 24 x 14 = 336 m2 buildable area (%s)" % sa)
        await fill('[data-propsetback="0"]', '5')
        await dispatch('[data-propsetback="0"]')
        await page.wait_for_timeout(150)
        g = await ev("(id)=>window.__a3dPropertyGeometry(id)", pid)
        r = ((g or {}).get('setback') or {}).get('ring') or [[0, 0]] * 4
        sa = abs(sum(r[i][0] * r[(i + 1) % 4][1] - r[(i + 1) % 4][0] * r[i][1] for i in range(4))) / 2
        ck(near(sa, 24 * 12, 1e-6), "5 m on the north side alone: 24 x 12 = 288 m2 (%.3f)" % sa)
        ok_w = await ev("()=>window.__a3dWall([[10,10],[20,10]],0.3,3,'center',false)")
        bad_w = await ev("()=>window.__a3dWall([[10,3],[20,3]],0.3,3,'center',false)")
        vio = await ev("(id)=>window.__a3dSetbackViolations(id)", pid)
        names = [v['name'] for v in (vio or [])]
        bw = [o for o in await objs() if o['id'] == bad_w]
        gw = [o for o in await objs() if o['id'] == ok_w]
        ck(bw and gw and names == [bw[0]['name']],
           "only the wall 3 m from the north line is a violation (%s)" % names)
        await ev("(id)=>{window.__a3dSelectFor([id]);window.__a3dRefreshProps();}", pid)
        pv = await ev("()=>{const r=[...document.querySelectorAll('.a3d-prow')].find(e=>/Violations/.test(e.textContent));return r?r.textContent:'';}")
        ck(bw and bw[0]['name'] in pv, "and Properties names it (%r)" % pv)

        # ------------------------------------------------ 6. north arrow
        print("\n-- 6. the north arrow")
        await ev("()=>{window.__a3dSetTrueNorth(0);window.__a3dFit();window.__a3dTestPaint();}")
        n0 = await ev("()=>window.__a3dNorthArrow()")
        await ev("()=>{window.__a3dSetTrueNorth(90);window.__a3dTestPaint();}")
        n1 = await ev("()=>window.__a3dNorthArrow()")
        ck(n0 and near(n0['dx'], 0, 0.02) and n0['dy'] < -0.99, "True North 0: the arrow points up the plan (%s)" % n0)
        ck(n1 and n1['dx'] > 0.99 and near(n1['dy'], 0, 0.02), "True North 90: it points right (%s)" % n1)
        g90 = await ev("(id)=>window.__a3dPropertyGeometry(id)", pid)
        ck(g90 and near(g90['ring'][1][1], 30, 1e-6),
           "and the parcel, entered as true bearings, turns with it (%s)" % (g90 and g90['ring'][1]))
        tn_field = await ev("()=>{window.__a3dSelectFor([]);window.__a3dRefreshProps();const e=document.querySelector('[data-propmodel=\"truenorth\"]');return e?e.value:null;}")
        ck(tn_field == '90', "True North is in the site Properties (%r)" % tn_field)
        await ev("()=>window.__a3dSetTrueNorth(0)")

        # ------------------------------------------------ 7. pick, export, reload
        print("\n-- 7. pick, export, reload")
        # the shape the parcel was made from lies under it and is picked first, which is right;
        # it is removed so the click tests the property line itself
        await ev("()=>{window.__a3dTestSetObjs(window.__a3dState().objs.filter(o=>o.id!=='LOT'));window.__a3dSelectFor([]);window.__a3dFit();window.__a3dTestPaint();}")
        box = await ev("()=>{const r=document.getElementById('a3d-canvas').getBoundingClientRect();return [r.left,r.top];}")
        s = await ev("()=>window.__a3dToScreen([15,20],0)")
        await page.mouse.click(box[0] + s[0], box[1] + s[1])
        await page.wait_for_timeout(200)
        st_ = await ev("()=>window.__a3dState()")
        ck(st_.get('sel') == pid, "a click on the south property line selects the property (%s)" % st_.get('sel'))
        dxf = (await ev("()=>window.__a3dBuildDXF()") or {}).get('text', '')
        ck('N 90%%d00\'00" E 30.00' in dxf, "the DXF carries each leg's bearing with the R12 degree mark")
        await page.wait_for_timeout(600)
        await page.reload()
        await page.wait_for_timeout(2300)
        pr = [o for o in await objs('property')]
        ck(pr and pr[0]['setbacks'][0] == 5 and len(pr[0]['legs']) == 4, "the parcel and its setbacks survive a reload")

        ck(not errs, "no uncaught page errors (%s)" % errs[:3])
        await browser.close()
    print("\n%d/%d checks passed" % (ck.n - len(ck.failed), ck.n))
    print("RESULT: " + ("PASS" if not ck.failed else "FAIL"))
    return 0 if not ck.failed else 1


if __name__ == '__main__':
    sys.exit(asyncio.run(run()))
