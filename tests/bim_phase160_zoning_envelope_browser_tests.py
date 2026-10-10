#!/usr/bin/env python3
"""bim_phase160_zoning_envelope_browser_tests.py -- V160: Site analysis SA3, regulation: the zoning
record, the envelope by side, the yield, the design against them, and the Zoning and yield board.

Every number the app works out is worked out again here, a different way: on a rectangular lot the
plate at a height is (width - the two side setbacks) x (depth - the front and rear setbacks), each
setback the rule's (steps and planes) at that height, integrated exactly piece by piece; an L-shaped
lot's volume is worked out by hand; the envelope's mesh is checked as a closed surface (its faces'
vector areas sum to nothing, every face flat) and its volume by the divergence theorem.

  1. THE RECORD: fields, ranges, blanks; each change one undo step; the property's sides and roles.
  2. THE WORKING: plates, volume, storeys, capacity, FAR, what governs, net, units, parking; steps,
     angular planes, the sky plane with no height limit, coverage, storeys; a corner lot; an L-shaped
     lot; a trapezoid whose corners come and go; refusals said in words.
  3. THE ENVELOPE: one undo step, its layer, locked, a closed solid of whole flat faces whose volume
     is the working's; rebuilt with each change.
  4. THE DESIGN AGAINST IT: GFA, height, coverage, elements outside in plan or height; a basement
     exempt; the findings and their classes.
  5. FROM THE LAYERS: a council layer's district, FAR (MapPLUTO's residential or commercial) and
     height (feet turned into metres); one undo step; credited.
  6. THE PANEL: the form, steps added and removed, the sides' roles, the layer button, the shell
     audit, touch sizes.
  7. THE BOARD: indicators, seven figures, the zoning analysis table, true-scale sections with their
     numbers, the rules by side, tooltips, tables, Esc, the theme, print, the phone; the climate
     board still itself; a reload keeps it all.

The harness never waits without a bound (V123).
"""
import asyncio, json, math, pathlib, re, sys, traceback

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from bim_phase133_site_context_browser_tests import Checks, Stalled, within, near   # noqa: E402
from playwright.async_api import async_playwright   # noqa: E402

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'
CK = Checks()
SC = 0.35   # a primitive's parameters are multiplied by it (V131)
LAT0, LON0 = 39.9656683, -75.1687892
WA, WE2 = 6378137.0, 0.00669437999014


# ---------------- the reference, worked out here ----------------
def rule(base, steps=(), plane=None):
    return {'base': base, 'steps': list(steps), 'plane': plane}


def inset(R, h, side):
    """The setback a rule asks for at height h; side < 0 is the limit from below (a step at h not yet taken)."""
    s = R['base']
    for hk, sk in R['steps']:
        if (hk <= h + 1e-9) if side > 0 else (hk < h - 1e-9):
            s = max(s, sk)
    if R['plane']:
        s = max(s, (h - R['plane'][0]) / R['plane'][1])
    return s


def rect_area(W, D, F, S, B, h, side=0):
    return max(0.0, W - 2 * inset(S, h, side)) * max(0.0, D - inset(F, h, side) - inset(B, h, side))


def rect_top(W, D, F, S, B, maxH):
    """Where the plate closes, or the height limit."""
    def a(h):
        return rect_area(W, D, F, S, B, h, -1)
    if maxH is not None and a(maxH) > 1e-6:
        return maxH
    lo, hi = 0.0, maxH if maxH is not None else 10.0
    while maxH is None and a(hi) > 1e-6:
        hi *= 2
    for _ in range(80):
        m = (lo + hi) / 2
        if a(m) > 1e-6:
            lo = m
        else:
            hi = m
    return lo


def rect_volume(W, D, F, S, B, top):
    """Exactly: split at every height where a rule changes or a width closes, Simpson on each piece."""
    Z = {0.0, top}
    for R in (F, S, B):
        for hk, sk in R['steps']:
            Z.add(hk)
        if R['plane']:
            h0, r = R['plane']
            for s in [R['base']] + [sk for _, sk in R['steps']]:
                Z.add(h0 + r * s)
    Z = sorted(z for z in Z if 0 <= z <= top)
    vol = 0.0
    for a, b in zip(Z, Z[1:]):
        if b - a < 1e-12:
            continue
        # the widths close inside a piece where an inset crosses its limit: split there too
        pts = [a, b]
        for k in range(1, 400):
            pts.append(a + (b - a) * k / 400)
        pts.sort()
        for u, w in zip(pts, pts[1:]):
            fu, fm, fw = rect_area(W, D, F, S, B, u, 1 if u == a else 0), rect_area(W, D, F, S, B, (u + w) / 2), rect_area(W, D, F, S, B, w, -1 if w == b else 0)
            vol += (w - u) / 6 * (fu + 4 * fm + fw)
    return vol


def rect_plates(W, D, F, S, B, top, f2f, cover_area, max_storeys=None):
    n = int(math.floor(top / f2f + 1e-9))
    if max_storeys:
        n = min(n, max_storeys)
    out = []
    for i in range(n):
        a = min(cover_area, rect_area(W, D, F, S, B, (i + 1) * f2f, -1))
        if a < 0.01:
            break
        out.append(round(a * 100) / 100)
    return out


def yield_of(plates, cap, far_gfa, eff, res, unit, park, park_non):
    ach = min(far_gfa, cap) if far_gfa is not None else cap
    gov = 'envelope' if far_gfa is None else ('FAR' if far_gfa <= cap + 1e-6 else 'envelope')
    used, acc = 0, 0.0
    for p in plates:
        if acc >= ach - 1e-6:
            break
        acc += p
        used += 1
    nsa = ach * eff / 100
    units = int(math.floor(nsa * res / 100 / unit + 1e-9))
    non = ach * (100 - res) / 100
    parking = int(math.ceil(units * park + non / 100 * park_non - 1e-9))
    return {'achievable': ach, 'governs': gov, 'storeysUsed': used, 'nsa': nsa, 'units': units, 'parking': parking}


def radii(lat):
    s = math.sin(math.radians(lat))
    w = 1 - WE2 * s * s
    return WA * (1 - WE2) / w ** 1.5, WA / math.sqrt(w)


def m2g(x, z):
    E, N = x, -z
    M, Nr = radii(LAT0)
    return [LON0 + math.degrees(E / (Nr * math.cos(math.radians(LAT0)))), LAT0 + math.degrees(N / M)]


def gring(pts):
    return [m2g(*p) for p in pts + [pts[0]]]


def zoning_layers():
    """Two council layers over the lot: a zoning district, and NSW-style FSR and height."""
    big = [(-100, -100), (200, -100), (200, 200), (-100, 200)]
    return {
        'zone': {'type': 'FeatureCollection', 'features': [
            {'type': 'Feature', 'properties': {'ZONE_CODE': 'B4', 'ZONE_NAME_LONG': 'Mixed Use'}, 'geometry': {'type': 'Polygon', 'coordinates': [gring(big)]}}]},
        'nsw': {'type': 'FeatureCollection', 'features': [
            {'type': 'Feature', 'properties': {'FSR': '2.5', 'MAX_B_H': 21, 'LEP_NAME': 'Test LEP 2012'}, 'geometry': {'type': 'Polygon', 'coordinates': [gring(big)]}}]},
        'pluto': {'type': 'FeatureCollection', 'features': [
            {'type': 'Feature', 'properties': {'ZoneDist1': 'R7-2', 'ResidFAR': 3.44, 'CommFAR': 2, 'FacilFAR': 6.5, 'MAX_HEIGHT_FT': 100},
             'geometry': {'type': 'Polygon', 'coordinates': [gring(big)]}},
            {'type': 'Feature', 'properties': {'ZoneDist1': 'M1-1', 'ResidFAR': 0, 'CommFAR': 1},
             'geometry': {'type': 'Polygon', 'coordinates': [gring([(500, 500), (600, 500), (600, 600), (500, 600)])]}}]},
    }


def newell(P):
    nx = ny = nz = 0.0
    for i in range(len(P)):
        a, b = P[i], P[(i + 1) % len(P)]
        nx += (a[1] - b[1]) * (a[2] + b[2])
        ny += (a[2] - b[2]) * (a[0] + b[0])
        nz += (a[0] - b[0]) * (a[1] + b[1])
    return [nx / 2, ny / 2, nz / 2]


def mesh_report(env):
    """A closed surface: its faces' vector areas sum to nothing; each face flat and convex; its volume."""
    V, F = env['v'], env['f']
    tot = [0.0, 0.0, 0.0]
    vol = 0.0
    worst_flat = 0.0
    concave = 0
    area = 0.0
    for f in F:
        P = [V[i] for i in f]
        n = newell(P)
        L = math.sqrt(sum(c * c for c in n))
        area += L
        for k in range(3):
            tot[k] += n[k]
        if L > 1e-12:
            u = [c / L for c in n]
            d0 = sum(u[k] * P[0][k] for k in range(3))
            worst_flat = max(worst_flat, max(abs(sum(u[k] * p[k] for k in range(3)) - d0) for p in P))
            # convex: every turn the same way about the normal
            sg = 0
            for i in range(len(P)):
                a, b, c = P[i], P[(i + 1) % len(P)], P[(i + 2) % len(P)]
                e1 = [b[k] - a[k] for k in range(3)]
                e2 = [c[k] - b[k] for k in range(3)]
                cr = [e1[1] * e2[2] - e1[2] * e2[1], e1[2] * e2[0] - e1[0] * e2[2], e1[0] * e2[1] - e1[1] * e2[0]]
                t = sum(cr[k] * u[k] for k in range(3))
                if abs(t) < 1e-9:
                    continue
                if sg == 0:
                    sg = 1 if t > 0 else -1
                elif (1 if t > 0 else -1) != sg:
                    concave += 1
                    break
        for j in range(2, len(P)):
            a, b, c = P[0], P[j - 1], P[j]
            vol += (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0]) + a[2] * (b[0] * c[1] - b[1] * c[0])) / 6
    return {'open': math.sqrt(sum(c * c for c in tot)) / max(1e-9, area), 'flat': worst_flat, 'concave': concave, 'vol': vol, 'faces': len(F)}


async def run():
    ck = CK
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1440, 'height': 900})
        LAYERS = zoning_layers()
        HITS = []

        async def gis(route):
            u = route.request.url
            HITS.append(u)
            key = 'zone' if 'zone.geojson' in u else ('nsw' if 'nsw.geojson' in u else 'pluto')
            await route.fulfill(status=200, body=json.dumps(LAYERS[key]), headers={'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'})
        await ctx.route('https://data.example.org/**', gis)
        page = await ctx.new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        ext = []
        page.on('request', lambda r: ext.append(r.url) if not r.url.startswith(('file:', 'data:', 'blob:', 'https://data.example.org/')) else None)
        await within(page.goto('file://' + str(HTML)), 'goto')
        await page.wait_for_timeout(2300)

        async def safe(js, arg=None, pg=None):
            pg = pg or page
            try:
                return await within(pg.evaluate(js, arg) if arg is not None else pg.evaluate(js), 'evaluate ' + js[:60].replace('\n', ' '))
            except Stalled:
                raise
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:200])
                return None

        async def toast(pg=None):
            return await safe("()=>{var t=document.getElementById('a3d-toast');return t?t.textContent:'';}", pg=pg) or ''

        async def zn():
            return await safe("()=>window.__a3dZn()") or {}

        async def zset(k, v, pg=None):
            return await safe("(a)=>window.__a3dZnSet(a[0],a[1])", [k, v], pg=pg)

        async def calc(pg=None):
            return await safe("()=>window.__a3dZnCalc()", pg=pg) or {}

        async def fnd(key):
            for f in ((await safe("()=>window.__a3dSa()")) or {}).get('findings', []):
                if f.get('auto') == key:
                    return f
            return None

        async def lot(pts, pg=None):
            await safe("""(a)=>{var o=window.__a3dState().objs.filter(function(x){return x.t!=='property'&&x.id!=='LOT'&&!x.envelope&&x.t!=='box';});
              o.push({id:'LOT',t:'sketch',name:'Lot',col:'#5ec4b8',pos:[0,0,0],pts:a,y:0,closed:true,layer:'layer-0'});
              window.__a3dTestSetObjs(o);window.__a3dPropertyFromSketch('LOT');}""", pts, pg=pg)

        async def box(L, W, H, x, z, y0=0.0, usage='use-res'):
            bid = await safe("(a)=>window.__a3dAdd('box',{Length:a[0],Width:a[1],Height:a[2]}).id", [L / SC, W / SC, H / SC])
            await safe("(a)=>{var L=window.__a3dState().objs;L.forEach(function(o){if(o.id===a[0])o.pos=[a[1],a[2],a[3]];});window.__a3dTestSetObjs(L);}", [bid, x, y0 + H / 2, z])
            if usage:
                await safe("(a)=>window.__a3dUsageAssign([a[0]],a[1])", [bid, usage])
            return bid

        async def clear_boxes():
            await safe("()=>{var L=window.__a3dState().objs.filter(function(o){return o.t!=='box';});window.__a3dTestSetObjs(L);}")

        async def set_site(lat, lon, pg=None):
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dSetPropTab('site');window.__a3dRefreshProps();}", pg=pg)
            for k, v in (('sunlat', lat), ('sunlon', lon)):
                await safe("""(a)=>{var L=document.querySelectorAll('#a3d-propsbody input'),e=null,i;for(i=0;i<L.length;i++)if(L[i].getAttribute('data-propmodel')===a[0])e=L[i];
                  if(!e)return false;e.value=a[1];e.dispatchEvent(new Event('change',{bubbles:true}));return true;}""", [k, v], pg=pg)
                await (pg or page).wait_for_timeout(80)

        try:
            has = await safe("()=>window.__acad3dV160")
            ck(bool(has) and 'envelope' in has and 'rolesbyside' in has and 'zoningboard' in has, "__acad3dV160 marker is present (%s)" % (has or '')[:80])
            mv = re.search(r"var BIM_APP_VERSION=\{v:'V(\d+)'", HTML.read_text(encoding='utf-8'))
            ck(mv and int(mv.group(1)) >= 160, "the app says V160 or later (%s)" % (mv and mv.group(1)))
            if not has:
                raise Stalled('no V160')
            await safe("()=>{window.__a3dEnter();window.__a3dTestSetObjs([]);}")

            # ---------------------------------------------------------------------------------
            print("\n-- 1. the record")
            ck((await calc()).get('error', '').startswith('No property line yet'), "no property: said so (%s)" % (await calc()).get('error'))
            Z0 = await zn()
            ck(Z0.get('f2f') == 3.2 and Z0.get('eff') == 82 and Z0.get('unit') == 75 and Z0.get('res') == 100 and Z0.get('park') == 1 and Z0.get('far') is None and Z0.get('maxH') is None and
               Z0.get('frontSteps') == [] and Z0.get('legRoles') == [], "the defaults: 3.2 m floors, 82% efficiency, 75 m² units, all residential, a space a unit; no controls")
            await lot([[0, 0], [30, 0], [30, 40], [0, 40]])
            ck((await calc()).get('error', '').startswith('Give a height limit'), "a lot but no height: said so (%s)" % (await calc()).get('error'))
            for k, v in (('district', '  R7-2  '), ('uses', 'Residential; community facility'), ('far', '4'), ('maxH', '30'), ('front', '3'), ('side', '2'), ('rear', '5'),
                         ('baseH', '15'), ('step', '3'), ('cover', '70'), ('source', 'Test code s.23 (2026)')):
                ck(await zset(k, v) is True, "%s set" % k) if k in ('district', 'far') else await zset(k, v)
            Z = await zn()
            ck(Z.get('district') == 'R7-2' and Z.get('far') == 4 and Z.get('maxH') == 30 and Z.get('baseH') == 15 and Z.get('step') == 3, "the controls kept, the district trimmed (%s)" % Z.get('district'))
            r = await zset('far', '60')
            ck(r is False and (await zn()).get('far') == 4 and 'out of range (0 to 50)' in await toast(), "out of range: refused, saying the range")
            ck(await zset('skyR', '0') is False and (await zn()).get('skyR') is None, "a sky plane ratio of 0: refused")
            await zset('cover', '')
            ck((await zn()).get('cover') is None, "a blank coverage is none")
            await safe("()=>window.__a3dUndo()")
            ck((await zn()).get('cover') == 70, "one undo brings it back: each change one step")
            await zset('step', '')
            ck((await zn()).get('step') == 0, "a blank stepback is 0, not none")
            await safe("()=>window.__a3dUndo()")
            ck((await zn()).get('step') == 3 and (await zn()).get('cover') == 70, "and its undo is only its own")
            ck(await zset('frontSteps.0.h', '20') is False, "a step that is not there: refused")
            ck(await safe("()=>window.__a3dZnStepAdd('front')") is True and (await zn()).get('frontSteps') == [[None, None]], "Add a step: a blank step")
            ck(await zset('frontSteps.0.h', '1200') is False, "a step's height out of range: refused")
            await safe("()=>window.__a3dUndo()")
            ck((await zn()).get('frontSteps') == [], "one undo takes the step away")
            C = await calc()
            ck(C.get('roles') == ['front', 'side', 'rear', 'side'] and C.get('convex') is True, "the sides: the chosen front, the rear facing it, the sides between (%s)" % C.get('roles'))

            # ---------------------------------------------------------------------------------
            print("\n-- 2. the working")
            W, D = 30.0, 40.0
            F, S, B = rule(3, [(15, 6)]), rule(2), rule(5)
            top = rect_top(W, D, F, S, B, 30)
            ref_v = rect_volume(W, D, F, S, B, top)
            ref_p = rect_plates(W, D, F, S, B, top, 3.2, 0.7 * W * D)
            ck(near(C.get('volume'), ref_v, 1e-6) and near(C.get('volume'), 3 * 26 * 3 * 0 + 26 * 32 * 15 + 26 * 29 * 15, 1e-6),
               "a street wall then a stepback: %.1f m³ (26 x 32 x 15 + 26 x 29 x 15)" % ref_v)
            ck(C.get('plates') == ref_p == [832.0] * 4 + [754.0] * 5, "nine storeys of 3.2 m: four of 832 m², five of 754 above the stepback (%s)" % C.get('plates'))
            Y = yield_of(ref_p, sum(ref_p), 4 * W * D, 82, 100, 75, 1, 0)
            ck(near(C.get('capacity'), sum(ref_p), 1e-6) and near(C.get('farGFA'), 4800, 1e-9) and near(C.get('achievable'), Y['achievable'], 1e-9) and C.get('governs') == 'FAR' == Y['governs'],
               "capacity %d m²; FAR 4 x 1,200 m² = 4,800 m²: the FAR governs" % sum(ref_p))
            ck(C.get('storeysUsed') == Y['storeysUsed'] == 6 and near(C.get('nsa'), 3936, 1e-6) and C.get('units') == Y['units'] == 52 and C.get('parking') == 52,
               "six storeys used; 3,936 m² net at 82%; 52 units of 75 m²; 52 spaces")
            ck(C.get('lot') == 1200 and near(C.get('fpArea'), 832, 1e-9) and near(C.get('lotD'), 40, 1e-9), "the lot 1,200 m², buildable 832 m² at the ground, 40 m deep")
            for h, sd in ((14.99, -1), (15, -1), (15, 1), (29.99, -1)):
                P = await safe("(a)=>window.__a3dZnPlate(a[0],a[1])", [h, sd]) or {}
                ck(near(P.get('area'), rect_area(W, D, F, S, B, h, sd), 1e-6), "the plate at %.2f m%s: %.0f m²" % (h, ' (from above)' if sd > 0 else '', rect_area(W, D, F, S, B, h, sd)))
            ck(await safe("()=>window.__a3dZnInset('front',15,-1)") == 3 and await safe("()=>window.__a3dZnInset('front',15,1)") == 6, "a 15 m street wall may reach 15 m: the step is taken above it")
            # steps by side and an angular plane at the rear
            await safe("()=>window.__a3dZnStepAdd('side')")
            await zset('sideSteps.0.h', '20')
            await zset('sideSteps.0.s', '4')
            await zset('rearH', '10')
            await zset('rearR', '1')
            S, B = rule(2, [(20, 4)]), rule(5, [], (10, 1))
            C = await calc()
            top = rect_top(W, D, F, S, B, 30)
            ref_v = rect_volume(W, D, F, S, B, top)
            ref_p = rect_plates(W, D, F, S, B, top, 3.2, 0.7 * W * D)
            ck(near(C.get('volume'), ref_v, 1e-6 * ref_v), "sides 4 m back above 20 m, a 45° rear plane from 10 m: %.3f m³ (%.3f)" % (ref_v, C.get('volume') or -1))
            ck(C.get('plates') == ref_p, "and each storey's plate (%s)" % ref_p)
            ck(C.get('breaks') == [0, 15, 20, 30], "worked out in pieces between the heights where a rule changes: 15 (street wall; the rear plane overtakes 5 m), 20, 30 (%s)" % C.get('breaks'))
            worst = 0
            for h in (3, 12, 15.5, 19.9, 20.1, 24, 29.5):
                P = await safe("(a)=>window.__a3dZnPlate(a[0],0)", [h]) or {}
                worst = max(worst, abs((P.get('area') or 0) - rect_area(W, D, F, S, B, h)))
            ck(worst < 1e-6, "the plate at any height is (width - 2 sides) x (depth - front - rear) (%.2g)" % worst)
            # the sky plane alone
            for k in ('maxH', 'baseH', 'step', 'rearH', 'rearR'):
                await zset(k, '')
            await safe("()=>window.__a3dZnStepDel('side',0)")
            await zset('skyH', '25')
            await zset('skyR', '2.7')
            F, S, B = rule(3, [], (25, 2.7)), rule(2), rule(5)
            C = await calc()
            top = rect_top(W, D, F, S, B, None)
            ck(near(C.get('top'), 25 + 2.7 * 35, 1e-6) and near(top, 119.5, 1e-6), "a sky exposure plane and no height limit: the plate closes at 25 + 2.7 x 35 = 119.5 m (%s)" % C.get('top'))
            ref_v = rect_volume(W, D, F, S, B, top)
            ck(near(C.get('volume'), ref_v, 1e-6 * ref_v), "volume %.2f m³" % ref_v)
            ck(C.get('maxH') is None and len(C.get('plates', [])) == int(119.5 / 3.2), "37 storeys under it")
            # the envelope governs; coverage; storeys; mixed use
            await zset('skyH', '')
            await zset('skyR', '')
            await zset('maxH', '30')
            await zset('far', '10')
            F, S, B = rule(3), rule(2), rule(5)
            C = await calc()
            ref_p = rect_plates(W, D, F, S, B, 30, 3.2, 840)
            ck(C.get('governs') == 'envelope' and near(C.get('achievable'), sum(ref_p), 1e-6), "FAR 10: the envelope governs, %d m²" % sum(ref_p))
            await zset('cover', '50')
            C = await calc()
            ck(C.get('plates') == [600.0] * 9, "coverage 50%%: no floor above 600 m² (%s)" % C.get('plates', [])[:3])
            await zset('maxH', '')
            await zset('maxStoreys', '5')
            C = await calc()
            ck(near(C.get('maxH'), 16, 1e-9) and len(C.get('plates', [])) == 5, "five storeys and no height: 5 x 3.2 = 16 m, five plates")
            await zset('maxH', '30')
            ck(len((await calc()).get('plates', [])) == 5, "five storeys under a 30 m limit: still five")
            await zset('maxStoreys', '')
            await zset('cover', '70')
            await zset('far', '4')
            await zset('res', '60')
            await zset('parkNon', '2')
            C = await calc()
            ref_p = rect_plates(W, D, F, S, B, 30, 3.2, 840)
            Y = yield_of(ref_p, sum(ref_p), 4800, 82, 60, 75, 1, 2)
            ck(C.get('units') == Y['units'] and C.get('parking') == Y['parking'], "60%% residential: %d units; %d spaces with 2 per 100 m² of the rest" % (Y['units'], Y['parking']))
            await zset('res', '100')
            await zset('parkNon', '')
            await zset('baseH', '15')
            await zset('step', '3')
            # a corner lot: side 2 another front
            await zset('legRoles.1', 'front')
            C = await calc()
            ck(C.get('roles') == ['front', 'front', 'rear', 'side'] and near(C.get('fpArea'), (30 - 3 - 2) * (40 - 3 - 5), 1e-6),
               "a corner lot: side 2 picked as a second front, its setback the front's (%s)" % C.get('roles'))
            ck(near((await safe("()=>window.__a3dZnPlate(16,-1)") or {}).get('area'), (30 - 6 - 2) * (40 - 6 - 5), 1e-6), "and its stepback above the street wall")
            await safe("()=>window.__a3dUndo()")
            ck((await calc()).get('roles') == ['front', 'side', 'rear', 'side'], "one undo: back to auto")
            ck(await zset('legRoles.9', 'front') is False, "a side the lot has not: refused")
            # an L-shaped lot
            await lot([[0, 0], [30, 0], [30, 15], [15, 15], [15, 35], [0, 35]])
            for k, v in (('maxH', '24'), ('front', '3'), ('side', '2'), ('rear', '3'), ('baseH', '12'), ('step', '2')):
                await zset(k, v)
            C = await calc()
            ck(C.get('convex') is False and C.get('roles') == ['front', 'side', 'rear', 'side', 'rear', 'side'], "an L-shaped lot: not convex; its inner sides a rear and a side (%s)" % C.get('roles'))
            ck(near(C.get('volume'), (754 - 300) * 12 + (702 - 300) * 12, 1e-6), "its volume by hand: (754 - 300) x 12 + (702 - 300) x 12 = 10,272 m³ (%s)" % C.get('volume'))
            ck(near(C.get('fpArea'), 454, 1e-9), "its footprint: an L of 454 m², the inner corner mitred as the setback line is")
            await safe("()=>window.__a3dZnBuild()")
            M = mesh_report(await safe("()=>window.__a3dZnEnvelope()") or {'v': [], 'f': []})
            ck(M['open'] < 1e-9 and M['flat'] < 1e-6 and M['concave'] == 0 and near(M['vol'], 10272, 1e-6), "its envelope: closed, flat convex faces, %.3f m³ (%s)" % (M['vol'], M))
            ck(M['faces'] <= 18, "its L-shaped floor and roofs each two convex faces, not a fan of triangles (%d faces)" % M['faces'])
            # a U-shaped lot whose base closes first: the setbacks would split it in two
            await lot([[0, 0], [40, 0], [40, 40], [25, 40], [25, 10], [15, 10], [15, 40], [0, 40]])
            for k, v in (('maxH', ''), ('front', '0'), ('side', '0'), ('rear', '0'), ('baseH', ''), ('step', ''), ('skyH', '0'), ('skyR', '1'), ('sideH', '0'), ('sideR', '1'), ('rearH', '0'), ('rearR', '1')):
                await zset(k, v)
            C = await calc()
            tU = C.get('top') or 0
            ck(near(C.get('split'), 5, 1e-6) and near(tU, 4.999, 1e-6), "a U-shaped lot, every side under a 45° plane: at 5 m its base closes and it would split; the envelope stops a millimetre short (%s)" % tU)
            ck(near(C.get('volume'), 1300 * tU - 110 * tU ** 2 + 4 * tU ** 3 / 3, 1e-6), "its volume by hand, the integral of (40 - 2h)² - 30(10 + 2h) to there: %.2f m³ (%s)" % (1300 * tU - 110 * tU ** 2 + 4 * tU ** 3 / 3, C.get('volume')))
            await safe("()=>window.__a3dZnBuild()")
            M = mesh_report(await safe("()=>window.__a3dZnEnvelope()") or {'v': [], 'f': []})
            ck(M['open'] < 1e-9 and M['concave'] == 0 and near(M['vol'], C.get('volume'), 1e-6 * C.get('volume')), "its envelope closed, its floor in convex parts (%s)" % M)
            await safe("()=>window.__a3dClbOpen('zoning')")
            ck('Above 5.0 m the setbacks would split this lot in two' in (await safe("()=>document.querySelector('.a3d-clb-notes').textContent") or ''), "the board says where the envelope stops, and why")
            await safe("()=>window.__a3dClbClose()")
            for k in ('skyH', 'skyR', 'sideH', 'sideR', 'rearH', 'rearR'):
                await zset(k, '')
            # a trapezoid whose rear side is squeezed out on the way up
            await lot([[0, 0], [40, 0], [28, 30], [8, 30]])
            for k, v in (('maxH', '40'), ('front', '4'), ('side', '3'), ('rear', '4'), ('baseH', ''), ('step', ''), ('sideH', '6'), ('sideR', '1.5')):
                await zset(k, v)
            C = await calc()
            n = 2000
            A = await safe("(a)=>{var o=[],i;for(i=0;i<=a[1];i++){var r=window.__a3dZnPlate(a[0]*i/a[1],0);o.push(r&&r.area||0);}return o;}", [C.get('top', 0), n]) or [0]
            h = C.get('top', 0) / n
            simp = h / 3 * (A[0] + A[-1] + 4 * sum(A[1:-1:2]) + 2 * sum(A[2:-1:2]))
            ck(len(C.get('pieces', [])) == 3 and near(C.get('volume'), simp, 2e-4 * simp), "a trapezoid with daylight planes on its sides: three pieces, the rear side squeezed out at %.2f m; %.2f m³ (%.2f by 2,000 slices)" %
               ((C.get('pieces') or [[0, 0], [0, 0]])[1][1], C.get('volume') or -1, simp))
            await safe("()=>window.__a3dZnBuild()")
            M = mesh_report(await safe("()=>window.__a3dZnEnvelope()") or {'v': [], 'f': []})
            ck(M['open'] < 1e-9 and M['flat'] < 1e-6 and M['concave'] == 0 and near(M['vol'], C.get('volume'), 1e-7 * C.get('volume')), "its envelope: closed, flat convex faces, the same volume (%s)" % M)
            for k, v in (('sideH', ''), ('sideR', ''), ('front', '30')):
                await zset(k, v)
            ck((await calc()).get('error') == 'The setbacks leave no buildable area', "setbacks that meet: said so")
            await zset('front', '4')

            # ---------------------------------------------------------------------------------
            print("\n-- 3. the envelope")
            await lot([[0, 0], [30, 0], [30, 40], [0, 40]])
            for k, v in (('maxH', '30'), ('front', '3'), ('side', '2'), ('rear', '5'), ('baseH', '15'), ('step', '3'), ('rearH', '10'), ('rearR', '1')):
                await zset(k, v)
            await safe("()=>window.__a3dZnStepAdd('side')")
            await zset('sideSteps.0.h', '20')
            await zset('sideSteps.0.s', '4')
            await safe("()=>window.__a3dZnBuild()")
            await safe("()=>{var L=window.__a3dState().objs.filter(function(o){return !o.envelope;});window.__a3dTestSetObjs(L);}")
            ck(await safe("()=>window.__a3dZnEnvelope()") is None, "(no envelope)")
            C = await calc()
            r = await safe("()=>window.__a3dZnBuild()")
            E = await safe("()=>window.__a3dZnEnvelope()") or {}
            ck(r is True and E.get('locked') and E.get('name') == 'Zoning envelope (R7-2)' and 'Zoning envelope: ' in await toast(), "ENVELOPE builds it, locked, named for the district")
            ly = await safe("(id)=>{var L=window.__a3dLayers?window.__a3dLayers():[];for(var i=0;i<L.length;i++)if(L[i].id===id)return L[i];return null;}", E.get('layer'))
            ck(ly and ly.get('name') == 'Zoning envelope' and ly.get('transparency') == 70, "on its own layer, Zoning envelope, 70%% transparent (%s)" % (ly and {k: ly.get(k) for k in ('name', 'transparency')}))
            M = mesh_report(E)
            ck(M['open'] < 1e-9 and M['flat'] < 1e-6 and M['concave'] == 0, "a closed solid of flat convex faces, which the renderer draws as fans (%s)" % M)
            ck(near(M['vol'], C.get('volume'), 1e-7 * C.get('volume')) and E.get('envelope', {}).get('volume') == round(C.get('volume')), "its volume is the working's, %.1f m³" % M['vol'])
            ck(M['faces'] <= 24, "whole faces, not a triangle soup: %d" % M['faces'])
            await safe("()=>window.__a3dUndo()")
            ck(await safe("()=>window.__a3dZnEnvelope()") is None and (await zn()).get('sideSteps') == [[20, 4]], "one undo takes it away, and only it: the step set before stays")
            await safe("()=>window.__a3dRedo()")
            v0 = (await safe("()=>window.__a3dZnEnvelope()") or {}).get('envelope', {}).get('volume')
            await zset('maxH', '27')
            v1 = (await safe("()=>window.__a3dZnEnvelope()") or {}).get('envelope', {}).get('volume')
            ck(v0 and v1 and v1 < v0, "a change to the record rebuilds it (%s to %s m³)" % (v0, v1))
            await safe("()=>window.__a3dUndo()")
            ck((await safe("()=>window.__a3dZnEnvelope()") or {}).get('envelope', {}).get('volume') == v0 and (await zn()).get('maxH') == 30, "and one undo puts both back")

            # ---------------------------------------------------------------------------------
            print("\n-- 4. the design against it")
            b1 = await box(20, 26, 12, 15, 20)   # x 5..25, z 7..33, 12 m: inside
            C = await calc()
            pr = C.get('proposed') or {}
            ck(pr.get('outside') == [] and near(pr.get('height'), 12, 1e-6) and near(pr.get('coverArea'), 520, 1e-6), "a 20 x 26 m, 12 m mass inside: nothing outside; 12 m; 520 m² covered")
            ck(pr.get('gfa') and pr['gfa'] > 0, "its GFA from its usage (%s m²)" % pr.get('gfa'))
            await safe("()=>window.__a3dSaFill()")
            ck(await fnd('legal.compliance') is None, "no finding against the design")
            await clear_boxes()
            await box(20, 26, 35, 15, 20)   # 35 m: over the height, and through the rear plane
            C = await calc()
            pr = C.get('proposed') or {}
            await safe("()=>window.__a3dSaFill()")
            f = await fnd('legal.compliance')
            ck(len(pr.get('outside', [])) == 1 and near(pr.get('height'), 35, 1e-6), "35 m tall: outside the envelope")
            ck(f and f.get('cls') == 'redflag' and 'height 35.0 m is over the limit of 30.0 m' in f.get('value', ''), "a red flag: over the height limit (%s)" % (f and f.get('value')))
            await clear_boxes()
            await box(20, 30, 18, 15, 19)   # front face at z = 4: within 3 m below 15 m, but not the 6 m above it
            C = await calc()
            pr = C.get('proposed') or {}
            await safe("()=>window.__a3dSaFill()")
            f = await fnd('legal.compliance')
            ck(len(pr.get('outside', [])) == 1 and f and f.get('cls') == 'constraint' and '1 element outside the envelope' in f.get('value', ''),
               "through the stepback above the street wall, under the height: a constraint, outside the envelope (%s)" % (f and f.get('value')))
            ck(await safe("()=>window.__a3dZnAllows(15,4.5,14.9)") is True and await safe("()=>window.__a3dZnAllows(15,4.5,15.5)") is False and
               await safe("()=>window.__a3dZnAllows(15,6.5,15.5)") is True, "a point 4.5 m behind the front: allowed below 15 m, not above; 6.5 m behind, allowed")
            await clear_boxes()
            await box(40, 50, 6, 15, 20, y0=-6.0)   # a basement under the whole lot and beyond
            await box(20, 26, 12, 15, 20)
            C = await calc()
            pr = C.get('proposed') or {}
            ck(pr.get('outside') == [] and near(pr.get('coverArea'), 520, 1e-6), "a basement past the lot lines: the envelope does not apply below ground, nor does coverage (%s)" % pr)
            ck(near(pr.get('height'), 12, 1e-6), "the height from the ground up")
            await clear_boxes()
            await box(30, 30, 12, 15, 20)   # 900 m² on the ground: over 70% coverage
            await safe("()=>window.__a3dSaFill()")
            f = await fnd('legal.compliance')
            ck(f and 'coverage 75% is over 70%' in f.get('value', ''), "900 m² on a 1,200 m² lot: coverage 75%% over 70%% (%s)" % (f and f.get('value')))
            await clear_boxes()
            await zset('uses', 'Offices')
            ck('Uses: Offices' in ((await fnd('legal.zoning')) or {}).get('value', ''), "a change to the record refreshes its findings at once")
            await zset('uses', 'Residential; community facility')
            await safe("()=>window.__a3dSaFill(true)")
            fz, fe, fy = await fnd('legal.zoning'), await fnd('legal.envelope'), await fnd('legal.yield')
            ck(fz and fz['cat'] == 'legal' and fz['value'].startswith('R7-2: FAR 4, height 30.0 m, coverage 70%, front 3.0 m; 6.0 m above 15.0 m') and
               'side 2.0 m; 4.0 m above 20.0 m' in fz['value'] and 'rear 5.0 m; angular plane 1.0:1 from 10.0 m' in fz['value'] and fz['source'] == 'Test code s.23 (2026)',
               "the zoning in words, each side's rule, its source (%s)" % (fz and fz['value'][:120]))
            C = await calc()
            ck(fe and fe['cls'] == 'opportunity' and ('{:,}'.format(round(C['volume'])) + ' m³') in fe['value'] and 'the FAR governs: 4,800 m²' in fe['value'], "the envelope: its volume, what governs (%s)" % (fe and fe['value']))
            ck(fy and fy['value'].startswith('4,800 m² GFA, 3,936 m² net at 82%: 52 units of 75 m²; 52 parking spaces required'), "the yield (%s)" % (fy and fy['value']))

            # ---------------------------------------------------------------------------------
            print("\n-- 5. from the layers")
            await set_site(repr(LAT0), repr(LON0))
            await safe("()=>window.__a3dSetTrueNorth(0)")
            ck(await safe("()=>window.__a3dZnFromLayer(false)") is None, "no layer under the lot: nothing found")
            r1 = await safe("()=>window.__a3dDataAdd('https://data.example.org/zone.geojson','Land zoning','#ffaa00','Test council')")
            r2 = await safe("()=>window.__a3dDataAdd('https://data.example.org/nsw.geojson','Planning controls','#00aaff','Test planning portal')")
            ck(r1 and r1.get('id') and r2 and r2.get('id'), "two council layers added (%s, %s)" % (r1 and r1.get('result'), r2 and r2.get('result')))
            found = await safe("()=>window.__a3dZnFromLayer(false)") or {}
            ck(found.get('district', {}).get('value') == 'B4' and found['district'].get('attr') == 'ZONE_CODE' and found.get('far', {}).get('value') == 2.5 and found['far'].get('attr') == 'FSR' and
               found.get('height', {}).get('value') == 21 and found['height'].get('attr') == 'MAX_B_H', "the district from one layer, the FSR and height from another (%s)" %
               {k: (v.get('value'), v.get('attr')) for k, v in found.items()})
            await zset('district', 'old')
            r = await safe("()=>window.__a3dZnFromLayer(true)")
            Z = await zn()
            ck(r and Z.get('district') == 'B4' and Z.get('far') == 2.5 and Z.get('maxH') == 21 and 'Land zoning (Test council), ZONE_CODE' in Z.get('source', '') and
               'Planning controls (Test planning portal), FSR' in Z['source'] and 'MAX_B_H' in Z['source'], "used: the three set, each credited to its layer and field (%s)" % Z.get('source'))
            ck('From the layers: B4 · FAR 2.5 · 21.0 m' in await toast(), "and said")
            await safe("()=>window.__a3dUndo()")
            Z = await zn()
            ck(Z.get('district') == 'old' and Z.get('far') == 4 and Z.get('maxH') == 30, "one undo puts the record back")
            for lid in (r1.get('id'), r2.get('id')):
                await safe("(i)=>window.__a3dDataRemove(i)", lid)
            r3 = await safe("()=>window.__a3dDataAdd('https://data.example.org/pluto.geojson','MapPLUTO','#ff00aa','NYC DCP')")
            found = await safe("()=>window.__a3dZnFromLayer(false)") or {}
            ck(found.get('district', {}).get('value') == 'R7-2' and found.get('far', {}).get('attr') == 'ResidFAR' and found['far'].get('value') == 3.44 and
               near(found.get('height', {}).get('value'), 30.48, 1e-9) and found['height'].get('feet'), "MapPLUTO: ZoneDist1, the residential FAR for a residential scheme, 100 ft as 30.48 m (%s)" %
               {k: (v.get('value'), v.get('attr')) for k, v in found.items()})
            await zset('res', '30')
            found = await safe("()=>window.__a3dZnFromLayer(false)") or {}
            ck(found.get('far', {}).get('attr') == 'CommFAR' and found['far'].get('value') == 2, "a mostly commercial scheme: the commercial FAR")
            await zset('res', '100')
            ck(not [u for u in ext], "no other server asked (%s)" % ext[:2])

            # ---------------------------------------------------------------------------------
            print("\n-- 6. the panel")
            await safe("()=>{window.__a3dZnEdit(false);window.__a3dAnzView('site');}")
            await page.wait_for_timeout(200)
            sec = await safe("()=>{var s=document.querySelector('.a3d-sa-wrap [data-znsec]');return s?{t:s.textContent,btn:[].map.call(s.querySelectorAll('[data-saact]'),function(b){return b.getAttribute('data-saact');})}:null;}") or {}
            ck('Zoning and yield' in sec.get('t', '') and 'achievable (FAR governs)' in sec['t'] and sec.get('btn') == ['znedit', 'znbuild', 'znboard'], "Site analysis has Zoning and yield: its summary, Edit, Rebuild, the board (%s)" % sec.get('btn'))
            await safe("()=>document.querySelector('[data-znsec] [data-saact=\"znedit\"]').click()")
            await page.wait_for_timeout(150)
            fields = await safe("()=>[].map.call(document.querySelectorAll('[data-znsec] [data-znf]'),function(e){return e.getAttribute('data-znf');})") or []
            want = ['district', 'uses', 'far', 'maxH', 'maxStoreys', 'cover', 'front', 'frontLeg', 'baseH', 'step', 'skyH', 'skyR', 'side', 'sideH', 'sideR', 'sideSteps.0.h', 'sideSteps.0.s',
                    'rear', 'rearH', 'rearR', 'legRoles.0', 'legRoles.1', 'legRoles.2', 'legRoles.3', 'f2f', 'eff', 'unit', 'res', 'park', 'parkNon', 'source']
            ck(fields == want, "the form: the controls, the front, the sides, the rear, the lot's sides, the yield (%s)" % [x for x in want if x not in fields])
            ck('Use R7-2 · FAR 3.44 · 30.5 m' in (await safe("()=>document.querySelector('[data-znsec] [data-saact=\"znlayer\"]').textContent") or ''), "the layer under the lot offered in one button")
            await safe("""()=>{var e=document.querySelector('[data-znsec] [data-znf="far"]');e.value='3.5';e.dispatchEvent(new Event('change',{bubbles:true}));}""")
            await page.wait_for_timeout(150)
            ck((await zn()).get('far') == 3.5, "typed in the form: kept")
            await safe("()=>document.querySelector('[data-znsec] [data-saact=\"znstepadd:rear\"]').click()")
            await page.wait_for_timeout(150)
            ck((await zn()).get('rearSteps') == [[None, None]] and await safe("()=>!!document.querySelector('[data-znsec] [data-znstep=\"rear.0\"]')"), "Add a step: a row with its two numbers and a remove button")
            await safe("()=>document.querySelector('[data-znsec] [data-saact=\"znstepdel:rear.0\"]').click()")
            await page.wait_for_timeout(150)
            ck((await zn()).get('rearSteps') == [], "× removes it")
            await safe("""()=>{var e=document.querySelector('[data-znsec] [data-znf="legRoles.3"]');e.value='rear';e.dispatchEvent(new Event('change',{bubbles:true}));}""")
            await page.wait_for_timeout(150)
            ck((await calc()).get('roles') == ['front', 'side', 'rear', 'rear'], "a side's role picked in the form")
            ck(await safe("()=>document.querySelector('[data-znsec] [data-znf=\"legRoles.0\"]').disabled") is True, "the front's own role cannot be changed there")
            await safe("()=>window.__a3dUndo()")
            au = await safe("()=>window.__a3dShellAudit()") or {}
            ck(au.get('ok'), "the shell audit is clean with the form open (%s)" % au.get('unclaimed'))
            nm = {}
            for q, want_c in (('zoning', 'ZONING'), ('yield', 'ZONINGBOARD'), ('buildable envelope', 'ENVELOPE'), ('floor space ratio', 'ZONING'), ('sky exposure plane', 'ENVELOPE')):
                nm[q] = [x['name'] for x in (await safe("(q)=>window.__a3dCommandSearch(q,6)", q) or [])]
                ck(want_c in nm[q][:3], "searching %r finds %s (%s)" % (q, want_c, nm[q][:4]))

            # ---------------------------------------------------------------------------------
            print("\n-- 7. the board")
            await zset('far', '4')
            await zset('district', 'R7-2')
            await box(20, 26, 12, 15, 20)   # inside: 21 m would cross the rear's 45° plane
            await safe("()=>document.querySelector('[data-znsec] [data-saact=\"znboard\"]').click()")
            await page.wait_for_timeout(400)
            Bd = await safe("""()=>{var b=document.querySelector('.a3d-clb');if(!b)return null;
              return {label:b.getAttribute('aria-label'),h1:b.querySelector('.a3d-clb-h1').textContent,sub:b.querySelector('.a3d-clb-sub').textContent,
                kpis:[].map.call(b.querySelectorAll('.a3d-clb-kpi'),function(k){return [k.querySelector('.a3d-clb-kl').textContent,k.querySelector('.a3d-clb-kv').textContent,!!k.querySelector('.a3d-clb-st')];}),
                figs:[].map.call(b.querySelectorAll('.a3d-clb-card'),function(c){return {no:c.getAttribute('data-fig'),t:c.querySelector('.a3d-clb-h2').textContent,svg:c.querySelectorAll('svg').length,src:!!c.querySelector('.a3d-clb-src')};}),
                bar:[].map.call(b.querySelectorAll('.a3d-clb-bar [data-clb]'),function(x){return x.getAttribute('data-clb');}),notes:b.querySelector('.a3d-clb-notes').textContent};}""") or {}
            ck(Bd.get('label') == 'Zoning and yield board' and Bd.get('h1', '').endswith(': zoning and yield') and 'District R7-2' in Bd.get('sub', '') and 'Lot 1,200 m²' in Bd['sub'],
               "the board: a dialog, its title and header")
            ck(Bd.get('bar') == ['tables', 'envelope', 'print', 'close'], "its bar: Tables, Rebuild envelope, Print, Close (%s)" % Bd.get('bar'))
            labels = [k[0] for k in Bd.get('kpis', [])]
            ck(labels == ['Lot area', 'Floor area ratio', 'Height limit', 'Lot coverage', 'Envelope capacity', 'Achievable GFA', 'Units', 'Parking', 'The design'], "nine indicators (%s)" % labels)
            dk = Bd['kpis'][-1] if Bd.get('kpis') else ['', '', False]
            ck(dk[1] == 'Complies' and dk[2], "the design: Complies, with its icon and word (%s)" % dk[:2])
            figs = Bd.get('figs', [])
            ck([f['no'] for f in figs] == [str(i) for i in range(1, 8)] and all(f['src'] for f in figs) and all(f['svg'] >= 1 for f in figs[1:]),
               "seven figures, numbered, each with its source; six drawings and the table")
            ck(all(re.search(r'\d', f['t']) for f in figs), "every title states a finding with its number (%s)" % [f['t'][:40] for f in figs])
            rows = await safe("""()=>[].map.call(document.querySelectorAll('.a3d-zn-zt tbody tr[data-znrow]'),function(r){var c=r.querySelectorAll('td');return [r.getAttribute('data-znrow'),c[1].textContent,c[2].textContent,c[3].textContent];})""") or []
            items = [r[0] for r in rows]
            ck(items == ['District', 'Permitted uses', 'Lot area', 'Floor area ratio', 'Building height', 'Lot coverage', 'Front', 'Side yards', 'Rear yard', 'Inside the envelope', 'Parking spaces'],
               "Fig. 1, the zoning analysis table: each control (%s)" % items)
            byi = {r[0]: r for r in rows}
            icons = await safe("()=>[].map.call(document.querySelectorAll('.a3d-zn-zt .a3d-clb-st'),function(e){return [e.textContent,!!e.querySelector('svg')];})") or []
            ck(icons and all(i[1] for i in icons) and [i[0] for i in icons].count('Complies') == 4, "each verdict an icon and a word, never colour alone (%s)" % icons)
            ck(byi.get('Building height', [0, 0, 0, ''])[1:] == ['30.0 m', '12.0 m', 'Complies'] and byi.get('Rear yard', ['', ''])[1] == '5.0 m; angular plane 1.0:1 from 10.0 m' and
               byi.get('Parking spaces', ['', '', '', ''])[3] == 'Not checked', "permitted, proposed, complies; what cannot be checked says so (%s)" % byi.get('Building height'))
            await safe("()=>document.querySelector('[data-clb=\"tables\"]').click()")
            tA = await safe("()=>[].map.call(document.querySelectorAll('.a3d-clb-card[data-fig=\"2\"] .a3d-clb-table tbody tr'),function(r){return [].map.call(r.querySelectorAll('td'),function(c){return c.textContent;});})") or []
            ck(tA and tA[0] == ['0.00 m', '3.00 m', '5.00 m', '32.00 m'] and tA[-1] == ['30.00 m', '6.00 m', '20.00 m', '14.00 m'],
               "Fig. 2 front to rear: 3 m and 5 m at the ground; at 30 m, 6 m behind the street and 20 m from the rear under its plane (%s, %s)" % (tA[:1], tA[-1:]))
            tB = await safe("()=>[].map.call(document.querySelectorAll('.a3d-clb-card[data-fig=\"3\"] .a3d-clb-table tbody tr'),function(r){return [].map.call(r.querySelectorAll('td'),function(c){return c.textContent;});})") or []
            ck(tB and tB[0] == ['0.00 m', '2.00 m', '2.00 m', '26.00 m'] and tB[-1] == ['30.00 m', '4.00 m', '4.00 m', '22.00 m'], "Fig. 3 side to side: 26 m wide at the ground, 22 m above the step (%s)" % tB[-1:])
            t4 = await safe("()=>[].map.call(document.querySelectorAll('.a3d-clb-card[data-fig=\"4\"] .a3d-clb-table tbody tr'),function(r){return [].map.call(r.querySelectorAll('td'),function(c){return c.textContent;});})") or []
            ck(t4 == [['Front', '3.0 m', '6.0 m above 15.0 m', '—'], ['Side', '2.0 m', '4.0 m above 20.0 m', '—'], ['Rear', '5.0 m', '—', '1.0:1 from 10.0 m']], "Fig. 4, the rules by side (%s)" % t4)
            await safe("()=>document.querySelector('[data-clb=\"tables\"]').click()")
            box2 = await safe("()=>{var e=document.querySelector('.a3d-clb-card[data-fig=\"2\"] svg polygon.mk');e.scrollIntoView({block:'center'});var r=e.getBoundingClientRect();return [r.left+r.width*0.5,r.top+r.height*0.75];}")
            await page.mouse.move(box2[0], box2[1])
            await page.wait_for_timeout(120)
            tip = await safe("()=>{var t=document.querySelector('.a3d-clb-tip');return t.hidden?null:t.textContent;}") or ''
            ck(tip.startswith('Zoning envelope') and 'Up to 30.0 m high' in tip, "hover the section: the envelope's numbers (%s)" % tip[:60])
            sv = await safe("""()=>{var s=document.querySelector('.a3d-clb-card[data-fig="2"] svg'),p=s.querySelector('polygon.mk').getAttribute('points').split(' ').map(function(q){return q.split(',').map(Number);});
              var xs=p.map(function(q){return q[0];}),ys=p.map(function(q){return q[1];});return {w:Math.max.apply(null,xs)-Math.min.apply(null,xs),h:Math.max.apply(null,ys)-Math.min.apply(null,ys)};}""") or {}
            ck(sv and near(sv['w'] / sv['h'], 32 / 30, 0.02), "the section at true scale: 32 m wide, 30 m high, drawn %.1f by %.1f" % (sv.get('w', 0), sv.get('h', 0)))
            await safe("()=>document.querySelector('[data-clb=\"envelope\"]').click()")
            await page.wait_for_timeout(200)
            ck(await safe("()=>!!window.__a3dZnEnvelope()") and await safe("()=>!!document.querySelector('.a3d-clb')"), "Rebuild envelope from the board's bar, the board staying open")
            surf = await safe("()=>getComputedStyle(document.querySelector('.a3d-clb')).getPropertyValue('--surf').trim()")
            await safe("()=>document.body.classList.add('light-theme')")
            surf2 = await safe("()=>getComputedStyle(document.querySelector('.a3d-clb')).getPropertyValue('--surf').trim()")
            await safe("()=>document.body.classList.remove('light-theme')")
            ck(surf == '#1a1a19' and surf2 == '#fcfcfb', "it follows the theme")
            await page.emulate_media(media='print')
            pr = await safe("()=>({bar:getComputedStyle(document.querySelector('.a3d-clb-bar')).display,pos:getComputedStyle(document.querySelector('.a3d-clb')).position,zt:getComputedStyle(document.querySelector('.a3d-zn-zt')).display})") or {}
            await page.emulate_media(media='screen')
            ck(pr.get('bar') == 'none' and pr.get('pos') == 'static' and pr.get('zt') == 'table', "in print: the board alone, the zoning table on it (%s)" % pr)
            await page.keyboard.press('Escape')
            await page.wait_for_timeout(100)
            ck(await safe("()=>!document.querySelector('.a3d-clb')"), "Esc closes it")
            await safe("()=>window.__a3dRunCmd('zoningboard')")
            await page.wait_for_timeout(200)
            ck(await safe("()=>document.querySelector('.a3d-clb').getAttribute('aria-label')") == 'Zoning and yield board', "ZONINGBOARD opens it")
            await safe("()=>window.__a3dClbClose()")
            await safe("()=>window.__a3dRunCmd('climate')")
            await page.wait_for_timeout(200)
            ck(await safe("()=>document.querySelector('.a3d-clb').getAttribute('aria-label')") == 'Climate and risk board' and
               (await safe("()=>document.querySelector('.a3d-clb-h1').textContent") or '').endswith('climate and risk'), "and CLIMATE still opens the climate board")
            await safe("()=>window.__a3dClbClose()")
            before = await zn()
            env0 = await safe("()=>window.__a3dZnEnvelope()") or {}
            await page.wait_for_timeout(700)
            await within(page.reload(), 'reload')
            await page.wait_for_timeout(2300)
            env1 = await safe("()=>window.__a3dZnEnvelope()") or {}
            ck(await zn() == before and env1.get('envelope') == env0.get('envelope'), "a reload keeps the record and the envelope")
            await safe("()=>window.__a3dClbOpen('zoning')")
            ck(await safe("()=>document.querySelectorAll('.a3d-clb-card').length") == 7, "and the board opens again, all seven figures")
            await safe("()=>window.__a3dClbClose()")
            ck(not errs, "no page errors (%s)" % errs[:3])
            await ctx.close()

            # a phone
            ctx2 = await browser.new_context(viewport={'width': 390, 'height': 844}, has_touch=True, is_mobile=True)
            p2 = await ctx2.new_page()
            errs2 = []
            p2.on('pageerror', lambda e: errs2.append(str(e)))
            await within(p2.goto('file://' + str(HTML)), 'goto')
            await p2.wait_for_timeout(1800)
            await safe("()=>{window.__a3dEnter();window.__a3dTestSetObjs([]);}", pg=p2)
            await lot([[0, 0], [30, 0], [30, 40], [0, 40]], pg=p2)
            for k, v in (('district', 'R7-2'), ('far', '4'), ('maxH', '30'), ('front', '3'), ('side', '2'), ('rear', '5'), ('baseH', '15'), ('step', '3')):
                await zset(k, v, pg=p2)
            await safe("()=>{window.__a3dAnzView('site');window.__a3dZnEdit(true);window.__a3dSaGoto('legal');}", pg=p2)   # AMENDED FOR V162: the zoning form is in 2. Legal
            await p2.wait_for_timeout(200)
            t = await safe("""()=>{var i=document.querySelector('[data-znsec] [data-znf="far"]'),b=document.querySelector('[data-znsec] [data-saact="znstepadd:front"]');
              return i&&b?{i:i.getBoundingClientRect().height,f:parseFloat(getComputedStyle(i).fontSize),b:b.getBoundingClientRect().height}:null;}""", pg=p2) or {}
            ck(t and t['i'] >= 36 and t['f'] >= 16 and t['b'] >= 30, "on a phone: inputs 36 px tall at 16 px (no zoom on focus), buttons touch-sized (%s)" % t)
            await safe("()=>window.__a3dClbOpen('zoning')", pg=p2)
            await p2.wait_for_timeout(300)
            g = await safe("""()=>{var b=document.querySelector('.a3d-clb'),k=document.querySelectorAll('.a3d-clb-kpi');
              return {sw:b.scrollWidth,cw:b.clientWidth,k0:k[0].getBoundingClientRect().top,k1:k[1].getBoundingClientRect().top,k2:k[2].getBoundingClientRect().top,
                vb:[].map.call(document.querySelectorAll('.a3d-clb-card svg[role="img"]'),function(s){return s.getAttribute('viewBox').split(' ')[2];}),
                btn:document.querySelector('[data-clb="close"]').getBoundingClientRect().height};}""", pg=p2) or {}
            ck(g and g['sw'] <= g['cw'] + 1, "the board on a phone: nothing scrolls sideways (%s)" % {k: g.get(k) for k in ('sw', 'cw')})
            ck(g and g['k0'] == g['k1'] and g['k2'] > g['k1'], "indicators two to a row")
            ck(g and g.get('vb') and all(v == '360' for v in g['vb']), "every drawing drawn for the phone's width (%s)" % g.get('vb'))
            ck(g and g['btn'] >= 38, "touch-sized buttons")
            ck(not errs2, "no page errors on the phone (%s)" % errs2[:3])
            await ctx2.close()
        except Stalled as e:
            ck(False, "the harness stalled: %s" % e)
        except Exception:
            traceback.print_exc()
            ck(False, "the harness raised")
        await browser.close()

    print("\n%d/%d checks passed" % (ck.n - len(ck.bad), ck.n))
    if ck.bad:
        for b in ck.bad:
            print("  FAILED: " + b)
        print("RESULT: FAIL")
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == '__main__':
    sys.exit(asyncio.run(run()))
