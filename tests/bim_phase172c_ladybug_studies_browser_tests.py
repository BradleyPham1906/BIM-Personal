#!/usr/bin/env python3
"""V172c: sun-hours and radiation on the model, by Ladybug. reference/research-ladybug-sun-radiation.md.

Run: python3 bim_phase172c_ladybug_studies_browser_tests.py [path/to/canvas_v10.html]

Every number the studies give is held to a reckoning of the suite's own, made in CPython from Ladybug's own code
(the committed wheels, unpacked) and from geometry with exact answers -- never to the app's own functions:
 1. THE RECORDS: the marker, the version, the registry's app.solar (Ladybug's defaults), the runtime's gendaymtx as
    the app pins it.
 2. THE ROWS before a run: both need the site's place; radiation the weather too; direct sun not.
 3. DIRECT SUN on a canyon floor: Ladybug's Sunpath (native) and the canyon's walls, exactly, on two days; the year's
    steps; nothing more of the runtime fetched until a study, then numpy and gendaymtx.
 4. RADIATION on a lone box: each face, the sky's own patches (Ladybug's, by sky_values) times the cosine with
    Ladybug's patch directions (native), the ground's hemisphere as RadiationStudy adds it; the roof the sky's
    value on open ground; the sky against the weather file's own sums.
 5. TRUE NORTH turned: the result out of date, then each face again by the same reckoning, turned.
 6. REINHART's sky: 577 patches, the faces again.
 7. KEPT: one undo step a run; out of date when the model moves or a standard is overridden, and why; an override
    used by the next run; Clear.
 8. THE SELECTION: only the selected solid's faces, every solid still casting shade.
 9. DRAWN: the faces facing the eye in the legend's colours, the legend inside the view's safe area; hidden.
10. A RUNTIME FILE NOT WHAT THE APP PINS: gendaymtx refused by its SHA-256, said.
11. A PHONE: the rows' buttons, touch-sized.
12. NO PAGE ERRORS.

The harness never waits without a bound (V123).
"""
import asyncio, json, math, pathlib, shutil, sys, tempfile, traceback, zipfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from bim_phase133_site_context_browser_tests import Checks, Stalled, within   # noqa: E402
import ladybug_fixture as F   # noqa: E402
from playwright.async_api import async_playwright   # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT / 'canvas_v10.html'
RUNTIME = HTML.parent / 'runtime' if (HTML.parent / 'runtime').is_dir() else ROOT / 'runtime'
PAGES = 'https://bradleypham1906.github.io/BIM-Personal/runtime/'
CK = Checks()
YEAR = 2017
EPWT = F.epw_text(YEAR)
LAT, LON, TZ = F.LAT, F.LON, F.TZ
TMP = []


def tmpdir(prefix):
    d = pathlib.Path(tempfile.mkdtemp(prefix=prefix))
    TMP.append(d)
    return d


# ---------------- native: Ladybug's own code, on the committed wheels ----------------
NAT = {}


def native():
    d = tmpdir('bim172c_')
    for w in sorted((RUNTIME / 'wheels').glob('ladybug_*.whl')):
        with zipfile.ZipFile(str(w)) as z:
            z.extractall(str(d / 'site'))
    sys.path[:0] = [str(d / 'site')]
    from ladybug.viewsphere import view_sphere
    from ladybug.sunpath import Sunpath
    from ladybug.analysisperiod import AnalysisPeriod
    from ladybug.epw import EPW
    (d / 'fx.epw').write_text(EPWT)
    e = EPW(str(d / 'fx.epw'))
    NAT['ghi'] = sum(e.global_horizontal_radiation.values) / 1000.0
    NAT['dhi'] = sum(e.diffuse_horizontal_radiation.values) / 1000.0
    NAT['treg'] = [list(v.to_array()) for v in view_sphere.tregenza_dome_vectors]
    NAT['rein'] = [list(v.to_array()) for v in view_sphere.reinhart_dome_vectors]
    sp = Sunpath(LAT, LON, TZ)

    def suns(p, step):
        ap = AnalysisPeriod(p[0], p[1], p[2], p[3], p[4], p[5], step)
        out = []
        for h in ap.hoys:
            s = sp.calculate_sun_from_hoy(h)
            if s.altitude > 0:
                out.append(list(s.sun_vector_reversed.to_array()))
        return out, len(ap.hoys)
    NAT['suns'] = suns


def to_app(v, tn):
    """Ladybug's frame (x east, y north, z up) to the app's (x east, y up, north at -z), turned by true north as the
    app turns its sun (V107's bimSunVector: the azimuth plus true north)"""
    x, y, z = v
    L = math.sqrt(x * x + y * y + z * z) or 1.0
    e = math.asin(max(-1.0, min(1.0, z / L)))
    a = math.atan2(x, y) + math.radians(tn)
    return [math.cos(e) * math.sin(a), math.sin(e), -math.cos(e) * math.cos(a)]


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def newell(pts):
    n = [0.0, 0.0, 0.0]
    for i in range(len(pts)):
        a, b = pts[i], pts[(i + 1) % len(pts)]
        n[0] += (a[1] - b[1]) * (a[2] + b[2])
        n[1] += (a[2] - b[2]) * (a[0] + b[0])
        n[2] += (a[0] - b[0]) * (a[1] + b[1])
    L = math.sqrt(dot(n, n))
    return [c / L for c in n]


def face_rad(n, dome, sky, gr, tn):
    """a face nothing shades: RadiationStudy's sum -- each sky patch's kWh/m2 times the cosine, and the ground's
    hemisphere (the sky's mean times the reflectance, each patch reversed) the same way"""
    V = [to_app(v, tn) for v in dome]
    g = sum(sky) / len(sky) * gr
    tot = 0.0
    for v, s in zip(V, sky):
        c = dot(n, v)
        if c > 0:
            tot += s * c
        c = -c
        if c > 0:
            tot += g * c
    return tot


def box(i, x0, z0, x1, z1, h, y0=0.0):
    return {'id': i, 't': 'solid', 'name': i, 'col': '#9db0c4', 'pos': [0, 0, 0], 'layer': 'layer-0',
            'mesh': {'v': [[x0, y0, z0], [x1, y0, z0], [x1, y0, z1], [x0, y0, z1], [x0, h, z0], [x1, h, z0], [x1, h, z1], [x0, h, z1]],
                     'f': [[0, 1, 2, 3], [4, 7, 6, 5], [0, 4, 5, 1], [1, 5, 6, 2], [2, 6, 7, 3], [3, 7, 4, 0]]}}


def normals(b):
    v = b['mesh']['v']
    return [newell([v[k] for k in f]) for f in b['mesh']['f']]


def canyon_hours(suns_app, p, W=10.0, H=10.0, L=200.0, step=4):
    """direct sun on a point between two walls along north-south (x = -W/2 and +W/2, H high, L long): exact"""
    seen = 0
    for v in suns_app:
        if v[1] <= 0:
            continue
        if abs(v[0]) < 1e-12:
            seen += 1
            continue
        x = W / 2 if v[0] > 0 else -W / 2
        t = (x - p[0]) / v[0]
        y, z = p[1] + v[1] * t, p[2] + v[2] * t
        if not (y < H and abs(z) < L / 2):
            seen += 1
    return seen / float(step)


async def run():
    ck = CK
    native()
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1500, 'height': 950})
        ST = {'rt': [], 'tamper': None}

        async def rt_route(route):
            rel = route.request.url[len(PAGES):].split('?')[0]
            ST['rt'].append(rel)
            p = RUNTIME / rel
            if not p.is_file():
                await route.fulfill(status=404, body='not found', headers={'Access-Control-Allow-Origin': '*'})
                return
            body = p.read_bytes()
            if ST.get('tamper') and rel.endswith(ST['tamper']):
                body = body[:-1] + bytes([body[-1] ^ 1])
            ct = 'application/wasm' if rel.endswith('.wasm') else ('application/javascript' if rel.endswith('.js') else 'application/octet-stream')
            await route.fulfill(status=200, body=body, headers={'Access-Control-Allow-Origin': '*', 'Content-Type': ct})

        await ctx.route(PAGES + '**', rt_route)
        page = await ctx.new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))

        async def safe(js, arg=None, pg=None):
            pg = pg or page
            try:
                return await within(pg.evaluate(js, arg) if arg is not None else pg.evaluate(js), 'evaluate ' + js[:60].replace('\n', ' '))
            except Stalled:
                raise
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:200])
                return None

        async def slow(js, arg=None, pg=None, secs=240):
            pg = pg or page
            try:
                return await asyncio.wait_for(pg.evaluate(js, arg) if arg is not None else pg.evaluate(js), secs)
            except asyncio.TimeoutError:
                raise Stalled('slow ' + js[:60])

        async def set_site(fields, pg=None):
            pg = pg or page
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dSetPropTab('site');window.__a3dRefreshProps();}", pg=pg)
            for k, v in fields:
                await pg.fill('#a3d-propsbody [data-propmodel="%s"]' % k, v)
                await pg.keyboard.press('Enter')
                await pg.wait_for_timeout(80)

        async def objs(L, pg=None):
            await safe("(o)=>{window.__a3dTestSetObjs(o);}", L, pg=pg)

        async def study(k, o=None):
            r = await slow("(a)=>window.__a3dLbStudy(a[0],a[1])", [k, o or {}])
            return r or {}

        def card(C, k):
            return ([c for c in C if c['id'] == 'lb' + k] or [{}])[0]

        def off(c, act):
            return ([a.get('off') or '' for a in c.get('acts', []) if a['act'] == act] or ['?'])[0]

        try:
            await within(page.goto('file://' + str(HTML)), 'goto')
            await page.wait_for_timeout(2300)
            await safe("()=>{window.__a3dEnter();window.__a3dTestSetObjs([]);}")

            # ---------------------------------------------------------------------------------
            print("\n-- 1. The records")
            mk = await safe("()=>window.__acad3dV172c") or ''
            ck(all(w in mk for w in ('gendaymtx', 'sha256', 'numpy', 'bvh', 'tregenza', 'reinhart', 'radiation', 'directsun', 'kept', 'stale', 'draw', 'registry')),
               "the V172c marker (%s)" % mk[:80])
            ver = (await safe("()=>window.__a3dVersion()") or {}).get('v', '')
            ck(ver.startswith('V172') or ver[:2] == 'V1' and int(''.join(c for c in ver[1:4] if c.isdigit()) or 0) >= 172, "the app says V172 or later (%s)" % ver)
            REC = {r['id']: r for r in await safe("()=>window.__a3dStdRecords()") or []}
            so = REC.get('app.solar') or {}
            vals = {x['n']: x['v'] for x in ((so.get('eds') or [{}])[0].get('v') or [])}
            ck(so.get('area') == 'Climate' and vals == {'ground_ref': 0.2, 'offset': 0.1, 'step_day': 4, 'step_year': 1},
               "the registry's app.solar: Ladybug's ground reflectance 0.2, its 10 cm offset, the steps an hour (%s)" % vals)
            man = json.loads((RUNTIME / 'MANIFEST.json').read_text(encoding='utf-8'))
            gm = [f for f in man['files'] if f['path'] == 'radiance/gendaymtx.wasm']
            app = HTML.read_text(encoding='utf-8')
            ck(len(gm) == 1 and ("var BIM_LB_RAD={f:'radiance/gendaymtx.wasm',h:'%s'};" % gm[0]['sha256']) in app,
               "the app pins gendaymtx by the SHA-256 the runtime's manifest gives (%s)" % (gm[0]['sha256'][:12] if gm else None))
            ck(any(f['path'] == 'radiance/LICENSE' for f in man['files']), "Radiance's licence travels with it")

            # ---------------------------------------------------------------------------------
            print("\n-- 2. The rows before a run")
            await objs([box('A', 0, 0, 10, 10, 10)])
            C = await safe("()=>window.__a3dLbStudyCards()") or []
            ck([c['id'] for c in C] == ['lbrad', 'lbsun'] and all('Set the site' in off(c, 'lb:study:run:' + c['id'][2:]) for c in C),
               "with no place, both say to set the site first (%s)" % [off(c, 'lb:study:run:' + c['id'][2:]) for c in C])
            await set_site([('sunlat', repr(LAT)), ('sunlon', repr(LON)), ('suntz', repr(TZ)), ('sundate', '%d-12-21' % YEAR), ('truenorth', '0')])
            C = await safe("()=>window.__a3dLbStudyCards()") or []
            ck('Choose the weather' in off(card(C, 'rad'), 'lb:study:run:rad') and off(card(C, 'sun'), 'lb:study:run:sun') == '',
               "with the place: radiation asks for the weather, direct sun runs without it")
            ck(off(card(C, 'sun'), 'lb:study:show:sun') == 'Run it first' and off(card(C, 'sun'), 'lb:study:clear:sun') == 'Not run', "nothing to show or clear yet")

            # ---------------------------------------------------------------------------------
            print("\n-- 3. Direct sun on a canyon floor")
            W, H, L = 10.0, 10.0, 200.0
            floor = box('FL', -2, -2, 2, 2, 0.05)
            await objs([box('WW', -W / 2 - 1, -L / 2, -W / 2, L / 2, H), box('WE', W / 2, -L / 2, W / 2 + 1, L / 2, H), floor])
            n_rt = len(ST['rt'])
            ck(not any(x.endswith('gendaymtx.wasm') or 'numpy' in x for x in ST['rt']), "before a study, neither numpy nor gendaymtx is asked for")
            for date in ('%d-12-21' % YEAR, '%d-03-21' % YEAR):
                await set_site([('sundate', date)])
                r = await study('sun')
                mo, dd = int(date[5:7]), int(date[8:10])
                sv, steps = NAT['suns']([mo, dd, 0, mo, dd, 23], 4)
                sa = [to_app(v, 0) for v in sv]
                want = canyon_hours(sa, [0.0, 0.05 + 0.1, 0.0], W, H, L)
                got = (((r.get('r') or {}).get('faces') or {}).get('FL') or [None, None])[1]
                ck(r.get('r') and r['r'].get('dirs') == len(sv) and r['r']['pre'].get('steps') == steps,
                   "%s: Ladybug's sun steps, %d of the day's %d with the sun up, as native Sunpath gives them (%s)" % (date, len(sv), steps, (r.get('r') or {}).get('dirs') or r.get('error')))
                ck(got is not None and abs(got - want) < 1e-9, "%s: the floor's direct sun hours %.2f, exactly the canyon's (%s)" % (date, want, got))
            got_rt = ST['rt'][n_rt:]
            ck(any(x.endswith('radiance/gendaymtx.wasm') for x in got_rt) and any('numpy-2.2.5' in x for x in got_rt),
               "the first study asks for numpy and gendaymtx (%s)" % sorted(set(x for x in got_rt if 'numpy' in x or 'radiance' in x)))
            await safe("()=>window.__a3dLbAct('study:span')")
            r = await study('sun')
            sv, steps = NAT['suns']([1, 1, 0, 12, 31, 23], 1)
            ck((r.get('r') or {}).get('dirs') == len(sv) and r['r']['pre'].get('steps') == 8760 and r['params'].get('span') == 'year',
               "the year: every hour, the %d with the sun up (%s)" % (len(sv), (r.get('r') or {}).get('dirs')))
            want = canyon_hours([to_app(v, 0) for v in sv], [0.0, 0.15, 0.0], W, H, L, 1)
            got = r['r']['faces']['FL'][1]
            ck(abs(got - want) < 1e-9, "the year's direct sun on the floor: %.0f h, exactly (%s)" % (want, got))
            await safe("()=>window.__a3dLbAct('study:span')")

            # ---------------------------------------------------------------------------------
            print("\n-- 4. Radiation on a lone box")
            A = box('A', 0, 0, 10, 10, 10)
            await objs([A])
            import base64
            src = await slow("(a)=>window.__a3dLbOpenB64('fx.epw',a)", base64.b64encode(EPWT.encode('ascii')).decode('ascii'))
            ck(isinstance(src, dict) and src.get('hours') == 8760, "the weather opened (%s)" % (src or {}).get('hours'))
            r = await study('rad')
            sk = await slow("()=>window.__a3dLbCall('sky_values')") or {}
            sky = [a + b for a, b in zip(sk.get('direct') or [], sk.get('diffuse') or [])]
            ck(len(sky) == 145 and sk.get('density') == 'tregenza' and sk.get('ground_ref') == 0.2, "Tregenza's 145 patches, the ground reflecting 0.2 (%d)" % len(sky))
            NA = normals(A)
            got = (r.get('r') or {}).get('faces', {}).get('A') or []
            want = [None] + [face_rad(NA[i], NAT['treg'], sky, 0.2, 0) for i in range(1, 6)]
            ck(len(got) == 6 and got[0] is None, "the floor's underside left out, as V143 leaves it")
            bad = [(i, got[i], round(want[i], 2)) for i in range(1, 6) if got[i] is None or abs(got[i] - want[i]) > 0.02]
            ck(not bad, "each face: the sky's patches times the cosine with Ladybug's directions, and the ground's (%s)" % (bad or [round(w, 1) for w in want[1:]]))
            hz = sum(s * v[2] for s, v in zip(sky, NAT['treg']))
            ck(abs(got[1] - hz) < 0.02 and abs(r['r']['pre']['horizontal'] - hz) < 0.1, "the roof: the sky's value on open ground (%.1f)" % hz)
            dz = sum(s * v[2] for s, v in zip(sk['diffuse'], NAT['treg']))
            ck(abs(dz - NAT['dhi']) / NAT['dhi'] < 0.02, "the sky's diffuse on the horizontal within 2%% of the weather's (%.1f, %.1f)" % (dz, NAT['dhi']))
            ck(0.94 < hz / NAT['ghi'] < 1.01, "the sky on the horizontal 94 to 101%% of the weather's global (%.1f of %.1f)" % (hz, NAT['ghi']))
            ck(want[4] > want[2] and got[4] > got[2], "the south face more than the north (%s, %s)" % (got[4], got[2]))
            area = 5 * 100.0
            ck(abs(r['r']['area'] - area) < 1e-6 and abs(r['r']['total'] - sum(got[1:]) * 100.0) < 1.0, "the total: each face's value times its area (%s m2)" % r['r']['area'])

            # ---------------------------------------------------------------------------------
            print("\n-- 5. True north turned")
            await set_site([('truenorth', '90')])
            st = await safe("()=>window.__a3dLbStudyStale('rad')") or []
            ck(any('north' in s for s in st), "the result out of date, and why (%s)" % st)
            r = await study('rad')
            got = r['r']['faces']['A']
            want = [None] + [face_rad(NA[i], NAT['treg'], sky, 0.2, 90) for i in range(1, 6)]
            bad = [(i, got[i], round(want[i], 2)) for i in range(1, 6) if abs(got[i] - want[i]) > 0.02]
            ck(not bad, "each face again, the patches turned by true north (%s)" % bad)
            # true north 90: the model's north is the world's east, so the world's south falls on the model's west (-x)
            ck(abs(got[5] - face_rad(NA[4], NAT['treg'], sky, 0.2, 0)) < 0.05, "the face that looks west in the model now has the south's value (%s)" % got[5])
            await set_site([('truenorth', '0')])

            # ---------------------------------------------------------------------------------
            print("\n-- 6. Reinhart's sky")
            await safe("()=>window.__a3dLbAct('study:sky')")
            r = await study('rad')
            sk2 = await slow("()=>window.__a3dLbCall('sky_values')") or {}
            sky2 = [a + b for a, b in zip(sk2.get('direct') or [], sk2.get('diffuse') or [])]
            got = r['r']['faces']['A']
            want = [None] + [face_rad(NA[i], NAT['rein'], sky2, 0.2, 0) for i in range(1, 6)]
            bad = [(i, got[i], round(want[i], 2)) for i in range(1, 6) if abs(got[i] - want[i]) > 0.02]
            ck(len(sky2) == 577 and r['r']['dirs'] == 1154 and r['r']['pre']['density'] == 'reinhart' and not bad,
               "577 patches, their 1154 directions with the ground's, each face again (%s)" % (bad or len(sky2)))
            await safe("()=>window.__a3dLbAct('study:sky')")

            # ---------------------------------------------------------------------------------
            print("\n-- 7. Kept")
            u0 = await safe("()=>window.__a3dUndoDepth()")
            r = await study('rad')
            ck(await safe("()=>window.__a3dUndoDepth()") == u0 + 1, "a run is one undo step")
            D = await safe("()=>window.__a3dLbData()") or {}
            ck(D.get('rad', {}).get('r', {}).get('faces', {}).get('A') and D.get('lbshow') == 'rad' and D['rad'].get('src') and D['rad'].get('stamp') and D['rad'].get('std'),
               "kept with the project: the faces' values, the weather it read, the model's stamp, the standards")
            ck(await safe("()=>window.__a3dLbStudyStale('rad')") == [], "not out of date after its run")
            await objs([box('A', 0, 0, 10, 10, 12)])
            st = await safe("()=>window.__a3dLbStudyStale('rad')") or []
            ck(any('model' in s for s in st), "the box raised: out of date, the model named (%s)" % st)
            await objs([A])
            ck(await safe("()=>window.__a3dLbStudyStale('rad')") == [], "back as it was: not out of date")
            await safe("()=>window.__a3dStdOverride('app.solar','ground_ref',0.4,'for the suite')")
            st = await safe("()=>window.__a3dLbStudyStale('rad')") or []
            ck(len(st) == 1 and 'overridden' in st[0] and 'ground_ref' in st[0], "a standard overridden: out of date, the standard said (%s)" % st)
            r = await study('rad')
            sk3 = await slow("()=>window.__a3dLbCall('sky_values')") or {}
            got = r['r']['faces']['A']
            ck(sk3.get('ground_ref') == 0.4 and r['r']['pre']['ground_ref'] == 0.4 and abs(got[3] - face_rad(NA[3], NAT['treg'], sky, 0.4, 0)) < 0.02,
               "the next run uses it: the ground reflecting 0.4 (%s)" % got[3])
            await safe("()=>window.__a3dUndo()")
            D = await safe("()=>window.__a3dLbData()") or {}
            ck(D.get('rad', {}).get('r', {}).get('pre', {}).get('ground_ref') == 0.2, "undo: the run before it again")
            await safe("()=>window.__a3dStdClear('app.solar','ground_ref')")
            # a new date: radiation reads none, so stays current; direct sun on the day studied is out of date
            r = await study('sun')
            await set_site([('sundate', '%d-06-21' % YEAR)])
            ck(await safe("()=>window.__a3dLbStudyStale('rad')") == [], "a new date: radiation still current, it reads no date")
            st = await safe("()=>window.__a3dLbStudyStale('sun')") or []
            ck(st == ['the day studied has changed'], "a new date: direct sun on the day studied out of date, and why (%s)" % st)
            ck(await safe("()=>window.__a3dLbAct('study:clear:sun')") and not (await safe("()=>window.__a3dLbData()") or {}).get('sun'), "Clear takes a result away")

            # ---------------------------------------------------------------------------------
            print("\n-- 8. The selection")
            await objs([box('A', 0, 0, 10, 10, 10), box('T', 0, 20, 10, 30, 30)])
            await safe("()=>window.__a3dSelectFor(['A'])")
            G = await safe("()=>window.__a3dLbStudyGeo(['A'])") or {}
            ck(G.get('faces') == 5 and G.get('solids') == 1 and G.get('all') is False and G.get('tris') == 24, "A selected: its five faces studied, both solids' 24 triangles casting shade")
            r = await study('rad')
            fa = r['r']['faces']
            ck(list(fa) == ['A'] and r['r']['all'] is False, "only A's faces kept (%s)" % list(fa))
            ck(fa['A'][4] < face_rad(NA[4], NAT['treg'], sky, 0.2, 0) - 1, "its south face shaded by the tower beside it (%s)" % fa['A'][4])
            await safe("()=>window.__a3dSelectFor([])")

            # ---------------------------------------------------------------------------------
            print("\n-- 9. Drawn")
            await safe("()=>{window.__a3dSetView('home',false);window.__a3dFit();window.__a3dTestPaint();}")
            await page.wait_for_timeout(500)
            await safe("()=>window.__a3dTestPaint()")
            dr = await safe("()=>window.__a3dLbStudyDrawn()") or {}
            sr = await safe("()=>{var r=window.__a3dSafeViewRect?window.__a3dSafeViewRect():null;return r;}")
            ck(dr.get('kind') == 'rad' and 0 < dr.get('faces', 0) < 11 and dr.get('faces') == 3, "the faces facing the eye in the legend's colours, the rest culled (%s)" % dr)
            lg = dr.get('legend') or [0, 0, 0, 0]
            ck(sr is None or (lg[0] >= sr['x'] and lg[1] >= sr['y'] and lg[0] + lg[2] <= sr['x'] + sr['w'] + 0.5 and lg[1] + lg[3] <= sr['y'] + sr['h'] + 0.5),
               "the legend inside the view's safe area (%s in %s)" % (lg, sr))
            cl = await safe("()=>[window.__a3dLbStudyCol('rad',0,0,10),window.__a3dLbStudyCol('rad',10,0,10),window.__a3dLbStudyCol('sun',10,0,10)]")
            ck(cl == ['rgb(75,107,169)', 'rgb(234,38,0)', 'rgb(255,255,0)'], "Ladybug's colours: Colorset.original's ends, and ecotect's top (%s)" % cl)
            await safe("()=>window.__a3dLbAct('study:show:rad')")
            await safe("()=>window.__a3dTestPaint()")
            ck(await safe("()=>window.__a3dLbStudyDrawn()") is None, "Hide on the model: nothing drawn")

            # ---------------------------------------------------------------------------------
            print("\n-- 10. A runtime file not what the app pins")
            await safe("()=>window.__a3dLbStop()")
            ST['tamper'] = 'gendaymtx.wasm'
            r = await study('sun')
            ck('does not match its SHA-256' in (r.get('error') or ''), "gendaymtx changed by one byte: refused, said (%s)" % (r.get('error') or '')[:80])
            ST['tamper'] = None
            await safe("()=>window.__a3dLbStop()")
            r = await study('sun')
            ck(r.get('r') and not r.get('error'), "the file as pinned: the study runs again")

            # ---------------------------------------------------------------------------------
            print("\n-- 11. A phone")
            pctx = await browser.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
            await pctx.route(PAGES + '**', rt_route)
            p6 = await pctx.new_page()
            p6.on('pageerror', lambda e: errs.append('phone: ' + str(e)))
            await within(p6.goto('file://' + str(HTML)), 'goto phone')
            await p6.wait_for_timeout(2300)
            await safe("()=>{window.__a3dEnter();window.__a3dAwEnter&&window.__a3dAwEnter();}", pg=p6)
            await p6.wait_for_timeout(300)
            await safe("()=>window.__a3dAwPick('card','lbsun')", pg=p6)
            await p6.wait_for_timeout(300)
            hs = await safe("()=>[].map.call(document.querySelectorAll('[data-anzact^=\"lb:study:\"]'),function(b){var r=b.getBoundingClientRect();return [b.getAttribute('data-anzact'),Math.round(r.height)];}).filter(function(x){return x[1]>0;})", pg=p6) or []
            ck(len(hs) >= 3 and all(h >= 36 for _, h in hs), "the row's buttons on a phone, each at least 36 px for a finger (%s)" % hs)
            await pctx.close()

            # ---------------------------------------------------------------------------------
            print("\n-- 12. The page")
            ck(not errs, "no page errors (%s)" % errs[:3])
        except Stalled as e:
            ck(False, "the harness stalled: %s" % e)
        except Exception:
            traceback.print_exc()
            ck(False, "the suite ran to its end")
        await browser.close()
    print("\n%d/%d checks passed" % (CK.n - len(CK.bad), CK.n))
    if CK.bad:
        print("RESULT: FAIL")
        for m in CK.bad:
            print("   - " + m)
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == '__main__':
    try:
        sys.exit(asyncio.run(run()))
    finally:
        for d in TMP:
            shutil.rmtree(str(d), ignore_errors=True)
