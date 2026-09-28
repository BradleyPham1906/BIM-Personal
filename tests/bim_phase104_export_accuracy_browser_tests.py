"""
bim_phase104_export_accuracy_browser_tests.py

Regression suite for __acad3dV104 in canvas_v10.html: every export writes objects where they ARE,
with north up.

WHY EACH CHECK IS THE ONE THAT WOULD CATCH A REGRESSION:

  1. THE OBJECT IS MOVED WITH THE MOUSE (the gizmo's X arm) and the export is compared with where
     it IS -- points plus offset -- in all three sinks: DXF, plan SVG, sheet viewport.
  2. NORTH UP is asserted in each sink against an independent rule, not against the app: in DXF a
     line running up the plan must have increasing Y; in SVG (y down) it must have decreasing y.
  3. ARC DIRECTION is checked with AutoCAD's own bulge rule, computed here: the apex of a DXF
     bulge B from P1 to P2 lies at the chord midpoint plus B*c/2 along the RIGHT normal. The
     model apex, mapped north-up, must land there. A missing sign flip passes every straight check.
  4. IMPORT is checked on a hand-written AutoCAD-style DXF (north up, CCW arc), not on this app's
     own output -- a round trip alone passes when export and import are wrong the same way.
  5. THE ROUND TRIP is exact for a moved, curved polyline.
  6. A SHEET VIEWPORT OF SKETCHES ONLY frames them: every point it draws lies inside its rectangle.
  7. A survey bearing N 45 E exports north-east.
  8. Zero uncaught page errors.

Run:  python3 bim_phase104_export_accuracy_browser_tests.py [path/to/canvas_v10.html]
"""
import asyncio, math, pathlib, re, sys

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


def dxf_entities(text):
    """Minimal DXF ENTITIES reader: LWPOLYLINE pts/bulges, LINE ends, TEXT point+string."""
    if not isinstance(text, str):
        return []
    lines = text.replace('\r\n', '\n').split('\n')
    pairs = [(lines[i].strip(), lines[i + 1] if i + 1 < len(lines) else '') for i in range(0, len(lines) - 1, 2)]
    out, cur, inent = [], None, False
    for c, v in pairs:
        if c == '2' and v == 'ENTITIES':
            inent = True
            continue
        if not inent:
            continue
        if c == '0':
            if cur:
                out.append(cur)
            cur = {'type': v, 'pts': [], 'bul': [], 'p': {}} if v in ('LWPOLYLINE', 'LINE', 'TEXT') else None
            continue
        if cur is None:
            continue
        if cur['type'] == 'LWPOLYLINE':
            if c == '10':
                cur['pts'].append([float(v), None]); cur['bul'].append(0.0)
            elif c == '20':
                cur['pts'][-1][1] = float(v)
            elif c == '42':
                cur['bul'][-1] = float(v)
        else:
            if c in ('10', '20', '11', '21'):
                cur['p'][c] = float(v)
            elif c == '1':
                cur['s'] = v
    return out


def dxf_apex(p1, p2, b):
    """AutoCAD: bulge b>0 is counter-clockwise; the apex is off the chord to the RIGHT of travel."""
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    c = math.hypot(dx, dy)
    s = b * c / 2
    return [(p1[0] + p2[0]) / 2 + s * dy / c, (p1[1] + p2[1]) / 2 - s * dx / c]


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

        has = await page.evaluate("()=>!!window.__acad3dV104")
        ck(has, "__acad3dV104 marker is present")
        if not has:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.failed), ck.n))
            await browser.close()
            return 1

        async def ev(js, arg=None):
            return await page.evaluate(js, arg)

        async def dxf():
            return dxf_entities((await ev("()=>window.__a3dBuildDXF()") or {}).get('text'))

        # ------------------------------------------------ 1. moved with the mouse
        print("\n-- 1. an object moved with the gizmo exports where it is")
        await ev("""()=>{window.__a3dTestSetObjs([{id:'S',t:'sketch',name:'S',col:'#5ec4b8',pos:[0,0,0],
            pts:[[0,0],[4,-3]],y:0,closed:false}]);window.__a3dFlat(true);window.__a3dSelectFor(['S']);
            window.__a3dFit();window.__a3dTestPaint();}""")
        gz = await ev("()=>window.__a3dGizmo()")
        xa = [a for a in (gz or {}).get('arms', []) if a.get('axis') == 'x']
        if xa:
            r = await ev("()=>window.__a3dCanvasRect()")
            mx, my = (xa[0]['x0'] + xa[0]['x1']) / 2, (xa[0]['y0'] + xa[0]['y1']) / 2
            await page.mouse.move(r['left'] + mx, r['top'] + my); await page.mouse.down()
            await page.mouse.move(r['left'] + mx + 120, r['top'] + my, steps=10); await page.mouse.up()
            await page.wait_for_timeout(300)
        s = await ev("()=>window.__a3dObjSnapshot('S')")
        ox, oz = s['pos'][0], s['pos'][2]
        ck(abs(ox) > 1, "the line was moved by the gizmo (pos x %.3f)" % ox)
        want = [[0 + ox, -(0 + oz)], [4 + ox, -(-3 + oz)]]
        ents = [e for e in await dxf() if e['type'] == 'LWPOLYLINE']
        got = ents[0]['pts'] if ents else None
        ck(got and all(near(got[i][0], want[i][0], 1e-5) and near(got[i][1], want[i][1], 1e-5) for i in range(2)),
           "DXF: at its world position, north up: %s (want %s)" % (got, want))
        svg = (await ev("()=>window.__a3dBuildSVG('technical')") or {}).get('text', '')
        m = re.search(r'data-obj="S" d="M([-\d.]+),([-\d.]+) L([-\d.]+),([-\d.]+)', svg)
        sp = [float(x) for x in m.groups()] if m else None
        ck(sp and near(sp[0], ox, 1e-5) and near(sp[1], oz, 1e-5) and near(sp[2], 4 + ox, 1e-5) and near(sp[3], -3 + oz, 1e-5),
           "SVG: at its world position with y down like the plan (%s)" % sp)
        ck(sp and sp[3] < sp[1], "SVG: the end that is further NORTH has the SMALLER y (up the page)")
        vb = re.search(r'viewBox="([-\d.]+) ([-\d.]+) ([-\d.]+) ([-\d.]+)"', svg)
        vbv = [float(x) for x in vb.groups()] if vb else None
        ck(vbv and vbv[1] <= min(sp[1], sp[3]) and vbv[1] + vbv[3] >= max(sp[1], sp[3]),
           "SVG: the viewBox contains the drawing (%s)" % vbv)

        # ------------------------------------------------ 2. north up in DXF
        print("\n-- 2. DXF is north up")
        await ev("""()=>window.__a3dTestSetObjs([{id:'N',t:'sketch',name:'N',col:'#5ec4b8',pos:[0,0,0],
            pts:[[0,0],[0,-10]],y:0,closed:false}])""")
        e = [x for x in await dxf() if x['type'] == 'LWPOLYLINE']
        ck(e and near(e[0]['pts'][0][1], 0) and near(e[0]['pts'][1][1], 10),
           "a line running up the plan runs +Y in the DXF (%s)" % (e and e[0]['pts']))

        # ------------------------------------------------ 3. arcs
        print("\n-- 3. arcs turn the right way")
        for bul in (1.0, -0.4142135623730951, 0.25):
            await ev("""(b)=>window.__a3dTestSetObjs([{id:'A',t:'sketch',name:'A',col:'#5ec4b8',pos:[3,0,2],
                pts:[[0,0],[4,1]],bulges:[b,0],y:0,closed:false}])""", bul)
            apex = await ev("""()=>{var o=window.__a3dObjSnapshot('A');var a=window.__a3dBulgeArc(o.pts[0],o.pts[1],o.bulges[0]);
                var p=window.__a3dArcPointAt(a,0.5);return [p[0]+o.pos[0],p[1]+o.pos[2]];}""")
            e = [x for x in await dxf() if x['type'] == 'LWPOLYLINE']
            if e:
                dap = dxf_apex(e[0]['pts'][0], e[0]['pts'][1], e[0]['bul'][0])
                ck(near(dap[0], apex[0], 1e-5) and near(dap[1], -apex[1], 1e-5),
                   "bulge %+.3f: the DXF arc's apex by AutoCAD's rule %s is the model apex north-up %s"
                   % (bul, [round(v, 4) for v in dap], [round(apex[0], 4), round(-apex[1], 4)]))
            else:
                ck(False, "bulge %+.3f exported" % bul)

        # ------------------------------------------------ 4. import, hand-written
        print("\n-- 4. an AutoCAD-style DXF imports the right way up")
        src = "\n".join(["0", "SECTION", "2", "ENTITIES",
                         "0", "LINE", "8", "0", "10", "0", "20", "0", "30", "0", "11", "0", "21", "10", "31", "0",
                         "0", "ARC", "8", "0", "10", "0", "20", "0", "30", "0", "40", "5", "50", "0", "51", "90",
                         "0", "ENDSEC", "0", "EOF", ""])
        await ev("()=>window.__a3dTestSetObjs([])")
        await ev("(t)=>window.__a3dImportDXF(t)", src)
        im = await ev("()=>window.__a3dState().objs")
        ln = [o for o in im if o.get('pts') and len(o['pts']) == 2 and not o.get('bulges')]
        ck(ln and near(ln[0]['pts'][1][1], -10, 1e-9) and near(ln[0]['pts'][1][0], 0, 1e-9),
           "a DXF line to (0,10) -- north -- runs UP the plan to model (0,-10) (%s)" % (ln and ln[0]['pts']))
        ar = [o for o in im if o.get('bulges')]
        if ar:
            a = ar[0]
            ap = await ev("(o)=>{var a=window.__a3dBulgeArc(o.pts[0],o.pts[1],o.bulges[0]);return window.__a3dArcPointAt(a,0.5);}", a)
            r45 = 5 * math.cos(math.radians(45))
            ck(near(ap[0], r45, 1e-6) and near(ap[1], -r45, 1e-6),
               "a DXF arc from east to north bulges north-east: model apex (%.3f, %.3f) (%s)" % (r45, -r45, ap))
        else:
            ck(False, "the ARC was imported as an arc")

        # ------------------------------------------------ 5. round trip
        print("\n-- 5. round trip")
        await ev("""()=>window.__a3dTestSetObjs([{id:'R',t:'sketch',name:'R',col:'#5ec4b8',pos:[7,0,-5],
            pts:[[0,0],[6,0],[6,4],[0,4]],bulges:[0,0.5,0,-0.3],y:0}])""")
        txt = (await ev("()=>window.__a3dBuildDXF()") or {}).get('text')
        await ev("()=>window.__a3dTestSetObjs([])")
        await ev("(t)=>window.__a3dImportDXF(t)", txt)
        rt = [o for o in await ev("()=>window.__a3dState().objs") if o.get('pts')]
        wantp = [[7, -5], [13, -5], [13, -1], [7, -1]]
        ck(rt and all(near(rt[0]['pts'][i][0], wantp[i][0], 1e-6) and near(rt[0]['pts'][i][1], wantp[i][1], 1e-6) for i in range(4))
           and all(near((rt[0].get('bulges') or [0] * 4)[i], [0, 0.5, 0, -0.3][i], 1e-8) for i in range(4)),
           "a moved, curved closed polyline comes back at the same world points with the same bulges")

        # ------------------------------------------------ 6. viewport framing
        print("\n-- 6. a sheet viewport of sketches frames them")
        res = await ev("""()=>{window.__a3dTestSetObjs([{id:'V',t:'sketch',name:'V',col:'#5ec4b8',pos:[40,0,30],
            pts:[[0,0],[10,0],[10,6]],y:0,closed:false}]);
            var lvl=window.__a3dActiveLevel();var sh=window.__a3dAddSheet('A-9','V','A3');
            var vp=window.__a3dAddViewport(sh,'plan',lvl.id,'fit',100);
            var v=window.__a3dSheets().find(x=>x.id===sh).viewports.find(x=>x.id===vp);
            return {pv:window.__a3dBuildPlanViewportSVG(sh,vp),r:[v.x,v.y,v.w,v.h]};}""")
        d = re.search(r'data-obj="V"[^>]* d="([^"]+)"', (res.get('pv') or {}).get('svg', ''))
        nums = [float(x) for x in re.findall(r'[-\d.]+', d.group(1))] if d else []
        pts = list(zip(nums[0::2], nums[1::2]))
        x0, y0, w, h = res['r']
        ck(len(pts) == 3 and all(x0 <= p[0] <= x0 + w and y0 <= p[1] <= y0 + h for p in pts),
           "all 3 points are inside the viewport %s (%s)" % (res['r'], pts))
        ck(len(pts) == 3 and pts[2][1] > pts[1][1] and pts[1][0] > pts[0][0],
           "and it is not mirrored: +x right, the point further SOUTH lower on the sheet")

        # ------------------------------------------------ 7. a survey bearing
        print("\n-- 7. a bearing N 45 E exports north-east")
        await ev("()=>{window.__a3dTestSetObjs([]);window.__a3dSetTrueNorth(0);}")
        # moved (pos 5,0,3): its derived corners are world already, so the offset applies ONCE
        await ev("""()=>{var o={id:'P',t:'property',name:'P',col:'#d8a657',pos:[5,0,3],start:[0,0],y:0,
            legs:[{b:'N 45 00 00 E',az:45,d:10},{b:'S 45 00 00 E',az:135,d:10},{b:'S 45 00 00 W',az:225,d:10},{b:'N 45 00 00 W',az:315,d:10}],
            setbacks:[0,0,0,0]};window.__a3dTestSetObjs([o]);}""")
        e = [x for x in await dxf() if x['type'] == 'LWPOLYLINE']
        if e:
            p0, p1 = e[0]['pts'][0], e[0]['pts'][1]
            ck(near(p1[0] - p0[0], 10 / math.sqrt(2), 1e-6) and near(p1[1] - p0[1], 10 / math.sqrt(2), 1e-6),
               "its first leg runs +X and +Y in the DXF (%s -> %s)" % (p0, p1))
            ck(near(p0[0], 5, 1e-6) and near(p0[1], -3, 1e-6),
               "and a moved parcel starts where it is, offset once, not twice (%s)" % p0)
        else:
            ck(False, "the property exported")

        ck(not errs, "no uncaught page errors (%s)" % errs[:3])
        await browser.close()
    print("\n%d/%d checks passed" % (ck.n - len(ck.failed), ck.n))
    print("RESULT: " + ("PASS" if not ck.failed else "FAIL"))
    return 0 if not ck.failed else 1


if __name__ == '__main__':
    sys.exit(asyncio.run(run()))
