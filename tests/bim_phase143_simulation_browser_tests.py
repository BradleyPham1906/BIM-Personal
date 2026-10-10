#!/usr/bin/env python3
"""bim_phase143_simulation_browser_tests.py -- V143: Simulation -- sun hours, solar, rain on terrain.

Each simulation is held to a second, independent calculation here in Python, from the same sun
positions (the app's NOAA routine, read through its hook):

  1. SUN HOURS: an empty site is lit all day; around a 20 m tower, every cell's hours equal a ray
     cast to the sun past the tower's box, step by step; the tower's own footprint is left out.
  2. SOLAR: an open roof's year equals Meinel's clear-sky beam plus sky, summed by hand; a south and a
     north facade each equal theirs; a roof under a tall neighbour loses exactly the beam the
     neighbour's box blocks; Colour By and the LOD group show it; it is saved.
  3. RAIN: a tilted plane has no pond and drains downhill; a bowl holds one pond of the volume the
     same fill gives in Python; two bowls hold two; a valley gathers its flow along its floor.
  4. THE ANALYZE TAB: a Simulation section, cards that run, clear, colour, and say when the model has
     moved on; the commands; the overlay on the plan; refusals without a site or a terrain.

The harness never waits without a bound (V123).
"""
import asyncio, heapq, math, pathlib, sys, traceback
from playwright.async_api import async_playwright

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import bim_phase139_lod_cityjson_browser_tests as M139

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
STALL = 90


class Stalled(Exception):
    pass


async def within(aw, what):
    try:
        return await asyncio.wait_for(aw, STALL)
    except asyncio.TimeoutError:
        raise Stalled(what)


LAT, LON, TZ, DATE = 40.0, -75.0, -5.0, '2026-12-21'


def sunvec(el, az):
    a, e = math.radians(az), math.radians(el)
    return (math.cos(e) * math.sin(a), math.sin(e), -math.cos(e) * math.cos(a))


def ray_box(o, d, b):
    t0, t1 = 0.0, float('inf')
    for k in range(3):
        if abs(d[k]) < 1e-12:
            if o[k] < b[k] or o[k] > b[k + 3]:
                return False
            continue
        a, c = (b[k] - o[k]) / d[k], (b[k + 3] - o[k]) / d[k]
        if a > c:
            a, c = c, a
        t0, t1 = max(t0, a), min(t1, c)
        if t0 > t1:
            return False
    return t1 > 1e-9


def dni(el):
    z = 90 - el
    am = 1 / (math.cos(math.radians(z)) + 0.50572 * (96.07995 - z) ** -1.6364)
    return 1361 * 0.7 ** (am ** 0.678) if el > 0 else 0


def py_fill(H, ok, nx, nz):
    """Priority-Flood (plain): the filled surface, for the expected pond volume."""
    F = list(H)
    done = [False] * len(H)
    q = []
    for j in range(nz):
        for i in range(nx):
            k = j * nx + i
            if not ok[k]:
                continue
            edge = i in (0, nx - 1) or j in (0, nz - 1) or any(not ok[(j + dz) * nx + i + dx] for dx, dz in
                                                                 ((1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)))
            if edge:
                done[k] = True
                heapq.heappush(q, (F[k], k))
    while q:
        f, c = heapq.heappop(q)
        ci, cj = c % nx, c // nx
        for dx, dz in ((1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)):
            a, b = ci + dx, cj + dz
            if 0 <= a < nx and 0 <= b < nz:
                n = b * nx + a
                if ok[n] and not done[n]:
                    done[n] = True
                    F[n] = max(H[n], f)
                    heapq.heappush(q, (F[n], n))
    return F


async def run():
    ck = CK
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1500, 'height': 950})
        page = await ctx.new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
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

        has = await safe("()=>window.__acad3dV143")
        ck(bool(has) and 'sunhours' in has and 'rainfill' in has, "__acad3dV143 marker is present (%s)" % has)
        if not has:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.bad), ck.n))
            await browser.close()
            return 1

        async def toast():
            return await safe("()=>{var t=document.getElementById('a3d-toast');return t?t.textContent:'';}") or ''

        async def set_site(date=DATE):
            await safe("""(a)=>{window.__a3dSelectFor([]);window.__a3dSetPropTab('site');window.__a3dRefreshProps();}""")
            for k, v in (('sunlat', repr(LAT)), ('sunlon', repr(LON)), ('suntz', repr(TZ)), ('sundate', date)):
                await page.fill('#a3d-propsbody [data-propmodel="%s"]' % k, v)
                await page.keyboard.press('Enter')
                await page.wait_for_timeout(60)

        async def suns(date, step, start):
            return await safe("""(a)=>{var out=[],m;for(m=a[2];m<1440;m+=a[1]){var rm=Math.round(m),hh=Math.floor(rm/60),mm=rm%60;
                var s=window.__a3dSunCalc(a[3],a[4],a[5],a[0],(hh<10?'0':'')+hh+':'+(mm<10?'0':'')+mm);if(s&&s.elevation>0)out.push([s.elevation,s.azimuth]);}return out;}""",
                              [date, step, start, LAT, LON, TZ])

        async def wbox(i):
            """an object's box in the world, from its own mesh"""
            b = await safe("""(i)=>{var o=window.__a3dState().objs.filter(function(x){return x.id===i;})[0],q=o.pos||[0,0,0],b=[1e9,1e9,1e9,-1e9,-1e9,-1e9];
              o.mesh.v.forEach(function(v){for(var k=0;k<3;k++){b[k]=Math.min(b[k],v[k]+q[k]);b[k+3]=Math.max(b[k+3],v[k]+q[k]);}});return b;}""", i)
            return tuple(b)

        async def cards():
            return await safe("""()=>{var w=document.querySelector('.a3d-analyze-wrap');if(!w)return null;
              return [].map.call(w.querySelectorAll('[data-anzcard]'),function(c){return {id:c.getAttribute('data-anzcard'),st:(c.querySelector('.a3d-anzst')||{}).textContent,
                state:(c.querySelector('.a3d-anzstate')||{textContent:''}).textContent,leg:!!c.querySelector('.a3d-anzleg'),
                btns:[].map.call(c.querySelectorAll('[data-anzact]'),function(b){return [b.getAttribute('data-anzact'),b.disabled];})};});}""") or []

        try:
            # ---------------------------------------------------------------------------------
            print("\n-- 0. refusals")
            r = await safe("()=>window.__a3dSunHours({})")
            ck(r and 'Set the site latitude' in r.get('error', ''), "no site place: sun hours say what is missing")
            r = await safe("()=>window.__a3dSolar({})")
            ck(r and 'Set the site' in r.get('error', ''), "so does solar")
            r = await safe("()=>window.__a3dRainFlow(null,{})")
            ck(r and 'There is no terrain surface' in r.get('error', ''), "and rain with no terrain")
            await set_site()

            # ---------------------------------------------------------------------------------
            print("\n-- 1. sun hours")
            S = await suns(DATE, 15, 7.5)
            day = len(S) * 0.25
            r = await safe("()=>window.__a3dSunHours({margin:10,cell:1})") or {}
            ck(r.get('day') == day and r.get('steps') == len(S) and r.get('min') == day and r.get('max') == day,
               "an empty site: every cell lit all %.2f h of the day (%s)" % (day, {k: r.get(k) for k in ('day', 'min', 'max', 'steps')}))
            tid = await safe("()=>window.__a3dColumnAt([0,0],0,4,4,20)")
            r = await safe("()=>window.__a3dSunHours({margin:30,cell:1})") or {}
            box = await wbox(tid)
            mism, roofbad, n, six = 0, 0, 0, 0
            vecs = [sunvec(e, a) for e, a in S]
            for j in range(r['nz']):
                z = r['z0'] + (j + 0.5) * r['cell']
                for i in range(r['nx']):
                    x = r['x0'] + (i + 0.5) * r['cell']
                    k = j * r['nx'] + i
                    inside = box[0] < x < box[3] and box[2] < z < box[5]
                    if r['roof'][k] != (1 if inside else 0):
                        roofbad += 1
                    if inside:
                        continue
                    n += 1
                    lit = sum(0.25 for d in vecs if not ray_box((x, 0.0, z), d, box))
                    six += 1 if lit >= 6 - 1e-9 else 0
                    if abs(lit - r['hours'][k]) > 1e-6:
                        mism += 1
            ck(roofbad == 0, "the tower's footprint is its roof, left out of the ground (%d cells wrong)" % roofbad)
            ck(abs(r['sixPlus'] - six / float(n)) < 0.001, "the share of ground with 6 h or more is the rays' share, roofs left out (%.4f, %.4f)" % (r['sixPlus'], six / float(n)))
            ck(n > 3000 and mism <= n * 0.005, "around a 20 m tower in December, %d cells: each one's hours equal a ray cast past the tower, step by step (%d differ)" % (n, mism))
            north = r['hours'][(int((-6 - r['z0']) / r['cell'])) * r['nx'] + int((0 - r['x0']) / r['cell'])]
            south = r['hours'][(int((6 - r['z0']) / r['cell'])) * r['nx'] + int((0 - r['x0']) / r['cell'])]
            ck(north < day - 2 and abs(south - day) < 1e-6, "north of the tower the ground loses hours (%.2f), south of it keeps them all (%.2f)" % (north, south))
            ck('Sun hours on %s' % DATE in await toast(), "the toast gives the range and the share with 6 h or more")

            # ---------------------------------------------------------------------------------
            print("\n-- 2. solar")
            Y = []
            for mo, days in enumerate([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]):
                for e, a in await suns('2026-%02d-21' % (mo + 1), 30, 15):
                    Y.append((sunvec(e, a), dni(e), days * 0.5))
            yy = await safe("()=>window.__a3dSolarYear()") or []
            ck(len(yy) == len(Y) and max(abs(p['dni'] - q[1]) for p, q in zip(yy, Y)) < 1e-6, "the year: %d half hours of sun, Meinel's DNI to the micro-watt" % len(Y))

            def year(nrm, block=None, origin=None):
                beam = sky = 0.0
                sv = (1 + nrm[1]) / 2
                blocks = block if isinstance(block, list) else ([block] if block else [])
                for d, dn, w in Y:
                    sky += 0.1 * dn * sv * w
                    c = sum(nrm[k] * d[k] for k in range(3))
                    if c <= 0:
                        continue
                    if any(ray_box(origin, d, bx) for bx in blocks):
                        continue
                    beam += dn * c * w
                return (beam + sky) / 1000
            res = await safe("(i)=>window.__a3dSolar({ids:[i]})", tid) or {}
            fs = (res.get('objects') or {}).get(tid, {}).get('faces', [])
            roof = [f for f in fs if f['n'][1] > 0.99]
            south = [f for f in fs if f['n'][2] > 0.99]
            northf = [f for f in fs if f['n'][2] < -0.99]
            ck(roof and abs(roof[0]['kwhm2'] - year((0, 1, 0))) < 1e-3 * year((0, 1, 0)),
               "an open roof: %.1f kWh/m2 a year, as summed by hand (%.1f)" % (roof[0]['kwhm2'] if roof else -1, year((0, 1, 0))))
            ck(south and abs(south[0]['kwhm2'] - year((0, 0, 1))) < 1e-3 * year((0, 0, 1)) and northf and abs(northf[0]['kwhm2'] - year((0, 0, -1))) < 1e-3 * year((0, 0, -1)),
               "the south facade %.1f and the north %.1f, each as summed by hand" % (south[0]['kwhm2'] if south else -1, northf[0]['kwhm2'] if northf else -1))
            ck(south and northf and south[0]['kwhm2'] > 2 * northf[0]['kwhm2'], "the south face gets more than twice the north's")
            # a low block with a tall neighbour to its south
            ids = await safe("()=>[window.__a3dColumnAt([40,0],0,10,10,5),window.__a3dColumnAt([40,12],0,10,4,30)]")
            res = await safe("(i)=>window.__a3dSolar({ids:i})", ids) or {}
            lowr = [f for f in res['objects'][ids[0]]['faces'] if f['n'][1] > 0.99][0]
            lb, tb = await wbox(ids[0]), await wbox(ids[1])
            c0 = lowr['c']   # each face is measured from its own centre: here a triangle of the roof
            exp = year((0, 1, 0), [tb, await wbox(tid)], (c0[0], c0[1] + 0.01, c0[2]))   # shaded by every solid: the neighbour, and the tower to the west
            ck(abs(lowr['kwhm2'] - exp) < 2e-3 * exp and lowr['kwhm2'] < year((0, 1, 0)) - 50,
               "a roof under a 30 m neighbour to its south loses the beam the neighbour blocks: %.1f, by hand %.1f, against %.1f open" % (lowr['kwhm2'], exp, year((0, 1, 0))))
            r2 = await safe("(i)=>window.__a3dSolar({ids:i,noShade:true})", ids) or {}
            ck(abs([f for f in r2['objects'][ids[0]]['faces'] if f['n'][1] > 0.99][0]['kwhm2'] - year((0, 1, 0))) < 1e-3 * year((0, 1, 0)), "unshaded, it gets the open roof's year")
            await safe("(i)=>window.__a3dSolar({ids:i})", ids)
            keys = await safe("()=>window.__a3dLensPropKeys&&window.__a3dLensPropKeys()") or []
            ck('Solar on roof (kWh/m2 a year)' in keys and 'Solar on facades (kWh/m2 a year)' in keys, "Colour By can show the roofs' and facades' solar (%s)" % [k for k in keys if 'Solar' in k])
            # a building that is not a box: an L, with a low block in its notch. Its bounding box covers the
            # notch, so only its real faces may shade the block, not its box
            L = M139.foreign_file()
            L['CityObjects'] = {'NL.L': L['CityObjects']['NL.L']}
            used = sorted(set(i for srf in L['CityObjects']['NL.L']['geometry'][0]['boundaries'][0] for ring in srf for i in ring))
            remap = {o_: n_ for n_, o_ in enumerate(used)}
            L['vertices'] = [L['vertices'][i] for i in used]
            g0 = L['CityObjects']['NL.L']['geometry'][0]
            g0['boundaries'] = [[[[remap[i] for i in ring] for ring in srf] for srf in shell] for shell in g0['boundaries']]
            L['CityObjects']['NL.L']['geometry'] = [g0]
            await safe("(t)=>window.__a3dCityJsonImport(t,'l.city.json')", __import__('json').dumps(L))
            nb = await safe("()=>window.__a3dColumnAt([5,-5],0,3,3,1)")
            rn = await safe("(i)=>window.__a3dSolar({ids:[i]})", nb) or {}
            nf = [f for f in rn['objects'][nb]['faces'] if f['n'][1] > 0.99][0]
            skyonly = year((0, 1, 0)) - sum(dn * d[1] * w for d, dn, w in Y) / 1000
            ck(nf['beam'] > 50 and nf['kwhm2'] < year((0, 1, 0)) - 50, "a block in an L's notch: the L's walls shade it, its empty box does not (%.0f beam, %.0f in all, %.0f open)" % (nf['beam'], nf['kwhm2'], year((0, 1, 0))))
            await safe("()=>{window.__a3dUndo();window.__a3dUndo();}")
            # a building's LOD group
            await safe("(t)=>window.__a3dCityJsonImport(t,'nl.city.json')", __import__('json').dumps(M139.foreign_file()))
            st = await safe("()=>window.__a3dState().objs.filter(function(o){return o.cityjson&&o.cityjson.id==='NL.L';})[0].id")
            await safe("(i)=>window.__a3dSolar({ids:[i]})", st)
            await safe("(i)=>{window.__a3dSelectFor([i]);window.__a3dRefreshProps();}", st)
            h = await safe("()=>document.getElementById('a3d-propsbody').innerHTML") or ''
            ck('Solar' in h and 'kWh/m² a year' in h and 'clear sky' in h, "the L block's LOD group shows its solar, clear sky")
            await page.wait_for_timeout(700)
            await within(page.reload(), 'reload')
            await page.wait_for_timeout(2300)
            sv = await safe("(i)=>{var o=window.__a3dState().objs.filter(function(o){return o.id===i;})[0];return o&&o.solar;}", st)
            ck(sv and sv.get('roof') and sv.get('computed'), "the result is saved with the project (%s)" % sv)

            # ---------------------------------------------------------------------------------
            print("\n-- 3. rain")
            plane = [[x, z, 0.1 * x, '', ''] for x in range(-20, 21, 5) for z in range(-20, 21, 5)]
            pid = await safe("(p)=>window.__a3dMakeTerrain(p)", plane)
            r = await safe("(a)=>window.__a3dRainFlow(a,{cell:1})", pid) or {}
            nx, nz = r['nx'], r['nz']
            inner = [r['dir'][j * nx + i] for j in range(2, nz - 2) for i in range(2, nx - 2)]
            ck(not r['ponds'] and all(d in (3, 4, 5) for d in inner), "a tilted plane: no pond, every cell draining downhill, west (%s)" % sorted(set(inner)))
            ck(max(r['acc']) == r['maxAcc'] and r['maxAcc'] >= nx - 4, "the flow gathers to the low edge")
            await safe("()=>window.__a3dUndo()")
            bowl = [[x, z, (x * x + z * z) / 100.0, '', ''] for x in range(-20, 21, 2) for z in range(-20, 21, 2)]
            bid = await safe("(p)=>window.__a3dMakeTerrain(p)", bowl)
            r = await safe("(a)=>window.__a3dRainFlow(a,{cell:2})", bid) or {}   # 2 m cells: each holds 4 m2 of water per metre of depth
            ck(len(r['ponds']) == 1, "a bowl holds one pond (%d)" % len(r['ponds']))
            p0 = r['ponds'][0] if r['ponds'] else {}
            # the same fill in Python, on the bowl's own formula at the same cell centres
            cx = [r['x0'] + (i + 0.5) * r['cell'] for i in range(r['nx'])]
            cz = [r['z0'] + (j + 0.5) * r['cell'] for j in range(r['nz'])]
            Hb = [(x * x + z * z) / 100.0 for z in cz for x in cx]
            Fb = py_fill(Hb, [True] * len(Hb), r['nx'], r['nz'])
            exp_v = sum(f - h for f, h in zip(Fb, Hb) if f - h >= 0.02) * r['cell'] ** 2
            rim = min(Hb[k] for k in range(len(Hb)) if k % r['nx'] in (0, r['nx'] - 1) or k // r['nx'] in (0, r['nz'] - 1))
            ck(abs(p0.get('volume', 0) - exp_v) < 0.02 * exp_v and abs(p0.get('depth', 0) - rim) < 0.05,
               "of the volume the same fill gives in Python, %.0f m3 (%.0f), as deep as its rim allows (%.3f; rim %.3f)" % (p0.get('volume', 0), exp_v, p0.get('depth', 0), rim))
            ck(p0.get('low') and abs(p0['low'][0]) < 1.01 and abs(p0['low'][1]) < 1.01, "its deepest point at the centre (%s)" % p0.get('low'))
            await safe("()=>window.__a3dUndo()")
            two = [[x, z, min(((x + 12) ** 2 + z * z), ((x - 12) ** 2 + z * z)) / 50.0, '', ''] for x in range(-24, 25, 2) for z in range(-12, 13, 2)]
            wid = await safe("(p)=>window.__a3dMakeTerrain(p)", two)
            r = await safe("(a)=>window.__a3dRainFlow(a,{cell:1})", wid) or {}
            ck(len(r['ponds']) == 2 and abs(r['ponds'][0]['volume'] - r['ponds'][1]['volume']) < 0.1 * r['ponds'][0]['volume'],
               "two bowls hold two ponds, of about the same volume (%s)" % [round(p['volume']) for p in r['ponds']])
            await safe("()=>window.__a3dUndo()")
            val = [[x, z, 0.1 * abs(x) + 0.05 * z, '', ''] for x in range(-20, 21, 2) for z in range(-20, 21, 2)]
            vid = await safe("(p)=>window.__a3dMakeTerrain(p)", val)
            r = await safe("(a)=>window.__a3dRainFlow(a,{cell:1})", vid) or {}
            nx = r['nx']
            big = max(range(len(r['acc'])), key=lambda k: r['acc'][k])
            bx = r['x0'] + (big % nx + 0.5) * r['cell']
            bz = r['z0'] + (big // nx + 0.5) * r['cell']
            ck(not r['ponds'] and abs(bx) <= 1.5 and bz < -17, "a valley: no pond, the flow gathered along its floor to its low end (%.1f, %.1f)" % (bx, bz))
            ck(r['segs'] > 10 and r['outlets'] >= 1, "flow lines along it, leaving at an outlet (%d segments)" % r['segs'])

            # ---------------------------------------------------------------------------------
            print("\n-- 4. the Analyze tab")
            await safe("()=>window.__a3dSetPlanView&&window.__a3dSetPlanView()")
            await page.click('#a3d-rail [data-tab="analyze"]')
            await page.wait_for_timeout(250)
            # AMENDED FOR V148: the cards are rows that open, every one opened so each button can be
            # clicked; the simulations are in the groups they belong to, not a section of their own
            await safe("()=>window.__a3dAnzOpenAll(true)")
            await page.wait_for_timeout(100)
            C = {c['id']: c for c in await cards()}
            hd = await safe("()=>[].map.call(document.querySelectorAll('.a3d-analyze-wrap .a3d-anzgrphd'),function(e){return e.textContent;})")
            # AMENDED FOR V162: one Analyze -- the simulations in the categories they answer (Climate,
            # Water); Model is the one group left at the end
            cat = await safe("()=>{var o={};['sunhours','solar','rain'].forEach(function(k){var r=document.querySelector('.a3d-analyze-wrap [data-anzcard=\"'+k+'\"]'),c=r&&r.closest('[data-sacat]');o[k]=c?c.getAttribute('data-sacat'):null;});return o;}") or {}
            ck(hd == ['Model'] and all(k in C for k in ('sunhours', 'solar', 'rain')) and cat == {'sunhours': 'climate', 'solar': 'climate', 'rain': 'water'},
               "the simulations among the categories: Sun hours and Solar in Climate, Rain on terrain in Water (%s, %s)" % (hd, cat))
            ck(C['rain']['state'] == 'On' and 'no pond' not in C['rain']['st'] and 'flow lines where' in C['rain']['st'], "the rain card says what it shows (%s)" % C['rain']['st'])
            await safe("()=>window.__a3dSimClear()")
            await page.wait_for_timeout(100)
            C = {c['id']: c for c in await cards()}
            ck(C['sunhours']['state'] == 'Off' and C['solar']['state'] == 'Off' and C['rain']['state'] == 'Off' and
               all(b[1] for b in C['sunhours']['btns'] if b[0].startswith('sim:clear')), "SIMCLEAR clears all three; Clear is disabled with nothing to clear")
            px0 = await safe("""()=>{var c=document.querySelector('#a3d-viewport canvas, canvas');var r=c.getBoundingClientRect();return [r.left+r.width*0.55,r.top+r.height*0.25];}""")
            shot0 = await page.screenshot(clip={'x': px0[0], 'y': px0[1], 'width': 6, 'height': 6})
            await page.click('.a3d-analyze-wrap [data-anzact="sunhours:run"]')
            await page.wait_for_timeout(300)
            C = {c['id']: c for c in await cards()}
            shot1 = await page.screenshot(clip={'x': px0[0], 'y': px0[1], 'width': 6, 'height': 6})
            ck(C['sunhours']['state'] == 'On' and C['sunhours']['leg'] and 'Ground in direct sun on %s' % DATE in C['sunhours']['st'], "Run: the sun hours, with a legend (%s)" % C['sunhours']['st'])
            ck(shot0 != shot1, "and they are drawn over the plan")
            await safe("()=>window.__a3dColumnAt([-30,0],0,3,3,6)")
            await safe("()=>window.__a3dRefreshProps()")
            await page.wait_for_timeout(100)
            C = {c['id']: c for c in await cards()}
            ck(C['sunhours']['state'] == 'Out of date' and 'changed since' in C['sunhours']['st'], "a new building: the card says the result is out of date")
            await page.click('.a3d-analyze-wrap [data-anzact="solar:run"]')
            for _ in range(60):
                if not (await safe("()=>window.__a3dSimState().busy")):
                    break
                await page.wait_for_timeout(100)
            await page.wait_for_timeout(150)
            C = {c['id']: c for c in await cards()}
            ck(C['solar']['state'] == 'On' and 'kWh/m' in C['solar']['st'] and 'clear sky' in C['solar']['st'], "Run on Solar: the roofs' average, clear sky (%s; %s)" % (C['solar']['st'], await toast()))
            await page.click('.a3d-analyze-wrap [data-anzact="solar:colour"]')
            await page.wait_for_timeout(150)
            ls = await safe("()=>window.__a3dLens()")
            ck(ls and ls.get('by') == 'prop' and ls.get('prop') == 'Solar on roof (kWh/m2 a year)', "Colour By colours the buildings by their roofs' solar (%s)" % ls)
            await page.click('.a3d-analyze-wrap [data-anzact="sim:clear:solar"]')
            await page.wait_for_timeout(150)
            ck(not await safe("()=>window.__a3dState().objs.some(function(o){return !!o.solar;})"), "Clear takes the solar results off the buildings")
            await safe("(i)=>{window.__a3dSelectFor([i]);window.__a3dRefreshProps();}", vid)
            ck(len((await safe("()=>window.__a3dSolar({})") or {}).get('objects', {})) >= 7, "with only a terrain selected, Solar takes every solid, not none")
            cat = await safe("()=>window.__a3dCommandCatalog().filter(c=>['SUNHOURS','SOLAR','RAINFLOW','SIMCLEAR'].indexOf(c.name)>=0).map(c=>c.name)") or []
            ck(sorted(cat) == ['RAINFLOW', 'SIMCLEAR', 'SOLAR', 'SUNHOURS'], "the four commands are in the catalogue")
            for q_, n_ in (('drainage', 'RAINFLOW'), ('photovoltaic', 'SOLAR'), ('overshadowing', 'SUNHOURS')):
                nm = [x['name'] for x in (await safe("(q)=>window.__a3dCommandSearch(q,5)", q_) or [])]
                ck(n_ in nm[:3], "searching %r finds %s (%s)" % (q_, n_, nm))
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
