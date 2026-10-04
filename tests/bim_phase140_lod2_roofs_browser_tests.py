#!/usr/bin/env python3
"""bim_phase140_lod2_roofs_browser_tests.py -- V140 (LOD-B): LOD2 roofs from OSM's roof tags.

The owner: no surfaces "too smooth" -- every roof here is planes, and each is checked against the
volume worked out by hand:

  1. EACH SHAPE: gabled, hipped (also on an L), pyramidal, skillion, half-hipped, gambrel, mansard,
     flat -- a valid solid, the exact volume, the ridge at the top, the planes counted; ridges along
     the longest side or across it, by roof:direction; a skillion's low side where it faces.
  2. HEIGHTS: height is the whole building, levels the walls; roof:height, roof:levels, roof:angle,
     an assumed 30 degrees, in that order; a roof too tall for its height cut down to leave walls.
  3. NOT FAKED: a dome, a gabled L, a shape nobody knows -- the block kept, the reason given.
  4. CONTEXT: houses fetched with their roofs (LOD2.0), a roofed part on its base, standing on the
     ground, the LOD group and its Roof row, the toast and the last fetch.
  5. CITYJSON: roofs exported as LOD2.0 with typed roof faces facing up, valid (cjval and an
     independent closure check), and back again.

The harness never waits without a bound (V123).
"""
import asyncio, json, math, pathlib, re, sys, tempfile, traceback
from playwright.async_api import async_playwright

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import bim_phase133_site_context_browser_tests as M133
import bim_phase139_lod_cityjson_browser_tests as M139   # the parts fixture, the closure check, cjval

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'


class Checks:
    def __init__(self):
        self.n, self.bad = 0, []

    def __call__(self, cond, msg):
        self.n += 1
        if not cond:
            self.bad.append(msg)
        print(('  ok    ' if cond else '  FAIL  ') + msg)


CK = Checks()
STALL = 60


class Stalled(Exception):
    pass


async def within(aw, what):
    try:
        return await asyncio.wait_for(aw, STALL)
    except asyncio.TimeoutError:
        raise Stalled(what)


LAT0, LON0 = M133.LAT0, M133.LON0
G, ring = M133.G, M133.ring


def rect(x, z, w, d):
    return [(x, z), (x + w, z), (x + w, z + d), (x, z + d)]


def L_at(x, z):
    return [(x, z), (x + 20, z), (x + 20, z + 10), (x + 10, z + 10), (x + 10, z + 20), (x, z + 20)]


# the houses, by model metres
H = {
    1001: (rect(-60, -145, 10, 6), {'building': 'house', 'height': '8', 'roof:shape': 'gabled', 'roof:height': '3', 'name': 'Gable House'}),
    1002: (rect(-40, -145, 12, 8), {'building': 'house', 'height': '9', 'roof:shape': 'hipped', 'roof:height': '3'}),
    1003: (rect(-20, -145, 8, 8), {'building': 'house', 'building:levels': '2', 'roof:shape': 'pyramidal', 'roof:height': '4'}),
    1004: (rect(0, -145, 10, 6), {'building': 'house', 'height': '7', 'roof:shape': 'skillion', 'roof:height': '2', 'roof:direction': 'S'}),
    1005: (rect(20, -145, 12, 10), {'building': 'yes', 'height': '10', 'roof:shape': 'mansard', 'roof:height': '4'}),
    1006: (rect(40, -145, 10, 6), {'building': 'church', 'height': '12', 'roof:shape': 'dome'}),
    1007: (L_at(60, -145), {'building': 'house', 'height': '8', 'roof:shape': 'gabled'}),
    1010: (rect(-60, -125, 20, 10), {'building': 'yes', 'height': '10'}),
    1011: (rect(-60, -125, 20, 10), {'building:part': 'yes', 'min_height': '4', 'height': '10', 'roof:shape': 'gabled', 'roof:height': '3'}),
}
VOL = {1001: 390, 1002: 688, 1003: 384 + 64 * 4 / 3, 1004: 360, 1005: 1000, 1011: 20 * 10 * 3 + 20 * 10 * 3 / 2}


def fixture():
    js = M139.fixture()
    for i, (fp, tg) in H.items():
        js['elements'].append({'type': 'way', 'id': i, 'tags': tg, 'geometry': G(ring(fp))})
    return js


R6 = [[0, 0], [10, 0], [10, 6], [0, 6]]


async def run():
    ck = CK
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1600, 'height': 950}, accept_downloads=True)
        page = await ctx.new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))

        async def ovp(route):
            await route.fulfill(status=200, body=json.dumps(fixture()), headers={'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'})
        for h in ('https://overpass-api.de/**', 'https://overpass.private.coffee/**', 'https://maps.mail.ru/**', 'https://overpass.kumi.systems/**'):
            await ctx.route(h, ovp)

        async def ter(route):
            m = re.search(r'/terrarium/(\d+)/(\d+)/(\d+)\.png$', route.request.url)
            if not m:
                return await route.abort('internetdisconnected')
            z, x, y = (int(v) for v in m.groups())
            await route.fulfill(status=200, body=M133.terrarium_png(z, x, y), headers={'Content-Type': 'image/png', 'Access-Control-Allow-Origin': '*'})
        await ctx.route('https://s3.amazonaws.com/**', ter)

        await within(page.goto('file://' + str(HTML)), 'goto')
        await page.wait_for_timeout(2300)

        async def safe(js, arg=None):
            try:
                return await within(page.evaluate(js, arg) if arg is not None else page.evaluate(js), 'evaluate ' + js[:50])
            except Stalled:
                raise
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:200])
                return None

        has = await safe("()=>window.__acad3dV140")
        ck(bool(has) and all(k in has for k in ('roofgabled', 'roofhipped', 'roofmansard', 'lod20')), "__acad3dV140 marker is present (%s)" % has)
        if not has:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.bad), ck.n))
            await browser.close()
            return 1

        async def roof(fp, tags, h, frm='height', base=0):
            return await safe("""a=>{var r=window.__a3dOsmRoof(a[0],a[1],a[4],a[2],a[3]);if(!r||!r.mesh)return r;
              var c=window.__a3dSolidCheckMesh(r.mesh);return {info:r.info,total:r.total,chk:c,v:r.mesh.v,f:r.mesh.f};}""", [fp, tags, h, frm, base])

        def top(r):
            return max(v[1] for v in r['v'])

        def at_top(r):
            t_ = top(r)
            return [v for v in r['v'] if abs(v[1] - t_) < 1e-9]

        async def toast():
            return await safe("()=>{var t=document.getElementById('a3d-toast');return t?t.textContent:'';}") or ''

        async def nosel():
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dRefreshProps();}")
            await page.wait_for_timeout(60)

        async def sel(i):
            await safe("(i)=>{window.__a3dSelectFor([i]);window.__a3dRefreshProps();}", i)
            await page.wait_for_timeout(80)

        async def props_html():
            return await safe("()=>document.getElementById('a3d-propsbody').innerHTML") or ''

        async def set_field(s, val):
            await safe("""(a)=>{var e=document.querySelector('#a3d-propsbody '+a[0]);if(!e)return false;
              e.value=a[1];e.dispatchEvent(new Event('change',{bubbles:true}));return true;}""", [s, val])
            await page.wait_for_timeout(120)

        try:
            # ---------------------------------------------------------------------------------
            print("\n-- 1. each shape")
            SH = [
                ('gabled 10 x 6, 8 m, roof 3 m', R6, {'roof:shape': 'gabled', 'roof:height': '3'}, 8, 'height', 390, 8, 2),
                ('hipped 12 x 8, 9 m, roof 3 m', [[0, 0], [12, 0], [12, 8], [0, 8]], {'roof:shape': 'hipped', 'roof:height': '3'}, 9, 'height', 688, 9, 4),
                ('pyramidal 8 x 8, 2 levels, roof 4 m', [[0, 0], [8, 0], [8, 8], [0, 8]], {'roof:shape': 'pyramidal', 'roof:height': '4'}, 6, 'levels', 384 + 64 * 4 / 3, 10, 4),
                ('skillion 10 x 6, 7 m, roof 2 m', R6, {'roof:shape': 'skillion', 'roof:height': '2', 'roof:direction': 'S'}, 7, 'height', 360, 7, 1),
                ('half-hipped 12 x 8, 10 m, roof 4 m', [[0, 0], [12, 0], [12, 8], [0, 8]], {'roof:shape': 'half-hipped', 'roof:height': '4'}, 10, 'height', 768 - 2 * 1.6 ** 3 / 3, 10, 4),
                ('gambrel 10 x 8, 10 m, roof 4 m', [[0, 0], [10, 0], [10, 8], [0, 8]], {'roof:shape': 'gambrel', 'roof:height': '4'}, 10, 'height', 704, 10, 4),
                ('mansard 12 x 10, 10 m, roof 4 m', [[0, 0], [12, 0], [12, 10], [0, 10]], {'roof:shape': 'mansard', 'roof:height': '4'}, 10, 'height', 1000, 10, 8),
                ('flat 10 x 6, 8 m', R6, {'roof:shape': 'flat'}, 8, 'height', 480, 8, 1),
            ]
            for nm, fp, tg, h, frm, vol, tp, nf in SH:
                r = await roof(fp, tg, h, frm)
                ok = bool(r and r.get('chk', {}).get('valid') and abs(r['chk']['volume'] - vol) < 0.002 and abs(top(r) - tp) < 1e-9 and r['info']['faces'] == nf)
                ck(ok, "%s: a valid solid of %.3f m3, its top at %g m, %d roof plane%s (%s)" % (
                    nm, vol, tp, nf, '' if nf == 1 else 's', r and (r.get('chk', {}).get('volume'), r.get('chk', {}).get('errors'), top(r) if r.get('v') else None, r.get('info', {}).get('faces'))))
            r = await roof([[0, 0], [20, 0], [20, 10], [10, 10], [10, 20], [0, 20]], {'roof:shape': 'hipped', 'roof:height': '4'}, 10)
            ck(r and r['chk']['valid'] and abs(top(r) - 10) < 1e-9 and r['info']['faces'] == 6 and 'straight skeleton' in r['info']['how'],
               "hipped on an L (not convex): the straight skeleton, a valid solid, six planes, the ridge at 10 m")
            # mansard: the knee
            r = await roof([[0, 0], [12, 0], [12, 10], [0, 10]], {'roof:shape': 'mansard', 'roof:height': '4'}, 10)
            kn = sorted(set(round(v[1], 6) for v in r['v']))
            ck(kn == [0, 6, 8.8, 10], "the mansard's heights: ground, eaves at 6, the knee at 8.8 (70%% of the roof), the top at 10 (%s)" % kn)
            # the ridge's direction
            r = await roof(R6, {'roof:shape': 'gabled', 'roof:height': '3'}, 8)
            rg = at_top(r)
            ck(len(rg) == 2 and all(abs(v[2] - 3) < 1e-9 for v in rg) and sorted(v[0] for v in rg) == [0, 10],
               "gabled: the ridge along the longest side, from end to end over the middle (%s)" % rg)
            r = await roof(R6, {'roof:shape': 'gabled', 'roof:height': '3', 'roof:orientation': 'across'}, 8)
            rg = at_top(r)
            ck(len(rg) == 2 and all(abs(v[0] - 5) < 1e-9 for v in rg) and sorted(v[2] for v in rg) == [0, 6], "roof:orientation=across turns it (%s)" % rg)
            r = await roof(R6, {'roof:shape': 'gabled', 'roof:height': '3', 'roof:direction': 'E'}, 8)
            rg = at_top(r)
            ck(len(rg) == 2 and all(abs(v[0] - 5) < 1e-9 for v in rg), "roof:direction=E: the roof faces east and west, the ridge runs north to south (%s)" % rg)
            r = await roof(R6, {'roof:shape': 'gabled', 'roof:height': '3', 'roof:direction': '90'}, 8)
            ck(r and all(abs(v[0] - 5) < 1e-9 for v in at_top(r)), "so does roof:direction=90")
            r = await roof(R6, {'roof:shape': 'skillion', 'roof:height': '2', 'roof:direction': 'S'}, 7)
            lo = set(round(v[1], 6) for v in r['v'] if abs(v[2] - 6) < 1e-9 and v[1] > 0)
            hi = set(round(v[1], 6) for v in r['v'] if abs(v[2]) < 1e-9 and v[1] > 0)
            ck(lo == {5} and hi == {7}, "skillion facing south: its low eave on the south side (model +z) at 5 m, the high one on the north at 7 m (%s %s)" % (lo, hi))
            r = await roof(R6, {'roof:shape': 'skillion', 'roof:height': '2', 'roof:direction': 'N'}, 7)
            ck(set(round(v[1], 6) for v in r['v'] if abs(v[2]) < 1e-9 and v[1] > 0) == {5}, "facing north, the other way round")
            d = await safe("()=>[window.__a3dRoofDir('S'),window.__a3dRoofDir('ssw'),window.__a3dRoofDir('nowhere'),window.__a3dRoofDir('')]")
            ck(d and abs(d[0][0]) < 1e-12 and abs(d[0][1] - 1) < 1e-12 and abs(d[1][0] + math.sin(math.radians(22.5))) < 1e-12 and d[2] is None and d[3] is None,
               "compass points and degrees read; nonsense does not (%s)" % d)
            # every face is planar and every roof face faces up
            r = await roof([[0, 0], [12, 0], [12, 10], [0, 10]], {'roof:shape': 'mansard', 'roof:height': '4'}, 10)
            ck(r['chk']['valid'] and not [e for e in r['chk']['errors'] if e['code'] == 203], "every face flat to val3dity's 1 cm: no smoothing anywhere")

            # ---------------------------------------------------------------------------------
            print("\n-- 2. heights")
            r = await roof(R6, {'roof:shape': 'gabled', 'roof:levels': '1'}, 8)
            ck(r['info']['from'] == 'roof:levels' and r['info']['height'] == 3 and top(r) == 8, "roof:levels=1: a 3 m roof inside an 8 m height")
            r = await roof(R6, {'roof:shape': 'gabled', 'roof:angle': '45'}, 6, 'levels')
            ck(r['info']['from'] == 'roof:angle' and abs(r['info']['height'] - 3) < 1e-9 and abs(top(r) - 9) < 1e-9 and abs(r['chk']['volume'] - 450) < 0.002,
               "roof:angle=45 over 6 m walls (2 levels): 3 m of roof on top, 9 m in all, 450 m3")
            r = await roof(R6, {'roof:shape': 'gabled'}, 6, 'levels')
            ck(r['info']['from'] == 'assumed' and abs(r['info']['height'] - math.tan(math.radians(30)) * 3) < 0.0006, "nothing said: an assumed 30 degree pitch")
            r = await roof(R6, {'roof:shape': 'gabled', 'roof:height': '3', 'roof:levels': '2', 'roof:angle': '60'}, 8)
            ck(r['info']['from'] == 'roof:height', "roof:height comes before roof:levels and roof:angle")
            r = await roof(R6, {'roof:shape': 'gabled', 'roof:height': '3 ft'}, 8)
            ck(abs(r['info']['height'] - 0.9144) < 0.0006, "roof:height in feet")
            r = await roof(R6, {'roof:shape': 'gabled', 'roof:height': '9'}, 6)
            ck(r['info']['clamped'] and r['info']['eave'] == 0.5 and abs(top(r) - 6) < 1e-9 and r['chk']['valid'], "a 9 m roof on a 6 m building: cut down, walls of 0.5 m kept")
            r = await roof(R6, {'roof:shape': 'gabled', 'roof:height': '3'}, 6, 'levels', 4)
            ys = sorted(set(round(v[1], 6) for v in r['v']))
            ck(ys == [4, 10, 13], "from a base 4 m up: walls 4 to 10, the ridge at 13 (%s)" % ys)

            # ---------------------------------------------------------------------------------
            print("\n-- 3. not faked")
            for tg, why in (({'roof:shape': 'dome'}, 'a dome roof is curved or uneven and is not built yet'),
                            ({'roof:shape': 'onion'}, 'a onion roof is curved or uneven and is not built yet'),
                            ({'roof:shape': 'spaceship'}, 'roof:shape=spaceship is not a shape this app knows')):
                r = await roof(R6, tg, 8)
                ck(r and 'mesh' not in r and r.get('why') == why, "%s: not built (%s)" % (tg['roof:shape'], r))
            r = await roof([[0, 0], [20, 0], [20, 10], [10, 10], [10, 20], [0, 20]], {'roof:shape': 'gabled'}, 8)
            ck(r and r.get('why') == 'a gabled roof needs a convex footprint (split the building into parts in OSM)', "a gabled L: not built, and why")
            ck(await roof(R6, {}, 8) is None, "no roof:shape: no roof")

            # ---------------------------------------------------------------------------------
            print("\n-- 4. context")
            await nosel()
            await set_field('[data-propmodel="sunlat"]', repr(LAT0))
            await set_field('[data-propmodel="sunlon"]', repr(LON0))
            res = await safe("()=>Promise.resolve(window.__a3dCtxFetch())") or {}
            ck(res.get('roofs') == {'gabled': 2, 'hipped': 1, 'mansard': 1, 'pyramidal': 1, 'skillion': 1} and res.get('notRoofed') == {'dome': 1, 'gabled': 1},
               "six LOD2 roofs, two not built (%s; %s)" % (res.get('roofs'), res.get('notRoofed')))
            tst = await toast()
            ck('6 LOD2 roofs (2 gabled, 1 hipped, 1 mansard, 1 pyramidal, 1 skillion)' in tst and '2 roofs not built (1 dome, 1 gabled)' in tst, "the toast says so")
            O = [o for o in (await safe("()=>window.__a3dState().objs") or []) if o.get('context') and o['context']['kind'] == 'buildings']
            by = {o['context']['id']: o for o in O}
            allv = True
            for i, vol in VOL.items():
                o = by.get(i)
                c = await safe("(i)=>window.__a3dSolidCheck(i)", o['id']) if o else None
                allv = allv and bool(c and c['valid'] and abs(c['volume'] - vol) < 0.01)
                if not (c and c['valid'] and abs(c['volume'] - vol) < 0.01):
                    print('      %s: %s' % (i, c))
            ck(allv, "each roofed house and part: a valid solid of its hand-worked volume")
            g = by.get(1001)
            ck(g and g['context'].get('lod') == '2.0' and g['context'].get('height') == 8 and g['context'].get('roof', {}).get('shape') == 'gabled',
               "the gable house: LOD2.0, 8 m to its ridge")
            L = await safe("(i)=>window.__a3dLodOf(i)", g['id'])
            ck(L == {'lod': '2.0', 'how': "a gabled roof from OpenStreetMap's roof:shape tag, 3 m high (its roof:height tag), ridge along the longest side; walls to 5 m, the top at 8 m (its height tag)"},
               "how it was made (%s)" % L)
            L = await safe("(i)=>window.__a3dLodOf(i)", by[1003]['id'])
            ck(L and L['how'].endswith('walls to 6 m (its levels at 3 m each), the top at 10 m') and by[1003]['context']['height'] == 10,
               "levels give the walls, the roof on top (%s)" % (L and L['how']))
            p = by.get(1011)
            ys = sorted(set(round(v[1], 6) for v in p['mesh']['v'])) if p else []
            ck(p and p['context']['lod'] == '2.0' and ys == [4, 7, 10] and p['context'].get('building', {}).get('id') == 1010,
               "a roofed part: from its base at 4 m, eaves at 7, ridge at 10, in its building (%s)" % ys)
            L = await safe("(i)=>window.__a3dLodOf(i)", p['id'])
            ck(L and 'walls to 7 m' in L['how'], "its walls counted from the ground (%s)" % (L and L['how']))
            dm = by.get(1006)
            ck(dm and dm['context']['lod'] == '1.2' and dm['context'].get('roofSkipped', {}).get('shape') == 'dome', "the domed church stays a LOD1.2 block")
            L = await safe("(i)=>window.__a3dLodOf(i)", dm['id'])
            ck(L and L['how'].endswith('; no LOD2 roof: a dome roof is curved or uneven and is not built yet'), "and says why")
            ck(by.get(1007) and by[1007]['context']['lod'] == '1.2', "so does the gabled L")
            sy = g['pos'][1]
            ck(abs(sy) > 0.01 and abs(sy - (min(M133.ground_xz(x, z) for x, z in H[1001][0]) - await safe("()=>window.__a3dCtxDatum()"))) < 0.03,
               "roofed houses stand on the ground like any other (%.3f)" % sy)
            await sel(g['id'])
            h = await props_html()
            ck('>LOD2.0<' in h and "the roof's shape on walls straight up from the footprint (no dormers or overhangs)" in h and
               'gabled, 3 m, 2 planes, eaves at 5 m' in h and 'a valid solid' in h, "its LOD group: LOD2.0, the Roof row, a valid solid")
            await sel(dm['id'])
            h = await props_html()
            ck('roof:shape=dome not built: a dome roof is curved' in h and 'a3d-svck-warn' in h, "the dome's group says its roof was not built")
            await nosel()
            ck('(6 LOD2 roofs)' in await props_html(), "the last fetch counts its roofs")

            # ---------------------------------------------------------------------------------
            print("\n-- 5. CityJSON")
            D = await safe("()=>window.__a3dCityJson()") or {}
            CO = D.get('CityObjects', {})
            gg = (CO.get('osm-way-1001', {}).get('geometry') or [{}])[0]
            sem = gg.get('semantics', {})
            types = [sem['surfaces'][k]['type'] for k in sem['values'][0]] if sem else []
            ck(gg.get('lod') == '2.0' and types.count('RoofSurface') == 2 and types.count('GroundSurface') == 1 and types.count('WallSurface') == 4,
               "the gable house in CityJSON: LOD2.0, two roof faces, one ground, four walls (%s)" % types)
            Vx = [[v[k] * 0.001 for k in range(3)] for v in D['vertices']]
            ups = []
            for k_, s_ in enumerate(sem['values'][0] if sem else []):
                if sem['surfaces'][s_]['type'] == 'RoofSurface':
                    rr = gg['boundaries'][0][k_][0]
                    n = [0, 0, 0]
                    for i in range(len(rr)):
                        a, b = Vx[rr[i]], Vx[rr[(i + 1) % len(rr)]]
                        n[0] += (a[1] - b[1]) * (a[2] + b[2]); n[1] += (a[2] - b[2]) * (a[0] + b[0]); n[2] += (a[0] - b[0]) * (a[1] + b[1])
                    ups.append(n[2] > 0)
            ck(ups == [True, True], "each roof face faces up")
            mn = (CO.get('osm-way-1005', {}).get('geometry') or [{}])[0]
            ms = mn.get('semantics', {})
            ck(mn.get('lod') == '2.0' and [ms['surfaces'][k]['type'] for k in ms['values'][0]].count('RoofSurface') == 8, "the mansard: eight roof faces")
            bad = []
            for k, co in CO.items():
                for g2 in co.get('geometry', []):
                    if g2['type'] == 'Solid':
                        cl, vol = M139.shell_check(g2['boundaries'][0], Vx)
                        if not cl or vol <= 0:
                            bad.append(k)
            ck(not bad, "every solid closed and outward, by the independent check (%s)" % bad[:4])
            cv = M139.cjval()
            if cv:
                tmpd = pathlib.Path(tempfile.mkdtemp())
                (tmpd / 'roofs.city.json').write_text(json.dumps(D))
                rep = cv(tmpd / 'roofs.city.json')
                ck(rep.get('valid') is True and rep.get('has_warnings') is False, "cjval finds it valid, with no warnings")
            else:
                print('      (cjval is not installed: its validation is skipped)')
            await safe("()=>window.__a3dCtxRemove()")
            r = await safe("(t)=>window.__a3dCityJsonImport(t,'roofs.city.json')", json.dumps(D)) or {}
            ck(r.get('bad') == 0 and r.get('lods', {}).get('2.0') == 6, "back in: six LOD2.0 objects, all valid (%s)" % r.get('lods'))
            O2 = {o['cityjson']['id']: o for o in (await safe("()=>window.__a3dState().objs") or []) if o.get('cityjson')}
            o2 = O2.get('osm-way-1005')
            c2 = await safe("(i)=>window.__a3dSolidCheck(i)", o2['id']) if o2 else None
            ck(c2 and c2['valid'] and abs(c2['volume'] - 1000) < 0.5, "the mansard comes back whole (%s)" % (c2 and c2['volume']))
            L = await safe("(i)=>window.__a3dLodOf(i)", O2['osm-way-1001']['id']) if 'osm-way-1001' in O2 else None
            ck(L and L['lod'] == '2.0' and L['how'].startswith('a gabled roof from'), "with its LOD and how it was made")
            ck(not errs, "no page errors (%s)" % errs[:3])
        except Stalled as e:
            ck(False, "the harness stalled at: %s" % e)
        except Exception:
            traceback.print_exc()
            ck(False, "the suite ran to its end")
        await browser.close()
    print("\n%d/%d checks passed" % (ck.n - len(ck.bad), ck.n))
    print("RESULT: " + ("PASS" if not ck.bad else "FAIL"))
    return 0 if not ck.bad else 1


if __name__ == '__main__':
    sys.exit(asyncio.run(run()))
