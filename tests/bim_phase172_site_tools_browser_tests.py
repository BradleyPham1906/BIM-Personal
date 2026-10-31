#!/usr/bin/env python3
"""bim_phase172_site_tools_browser_tests.py -- V172: the site analysis tools, ArcGIS's way.

The owner's four decisions (2026-10-27): the tools live in the analysis workspace; the buildable area is Pennsylvania's
site capacity calculation; sun hours are left to V172c; a simple Locate. Every service is answered in the browser by
tests/traffic_fixture.py (V171's neighbourhood, its lot at x 10..50, z -40..-10), the ground and FEMA's zones by
tests/land_fixture.py, the National Wetlands Inventory by a polygon here. What each tool should give is worked out again
in tests/site_tools_reference.py from the sources, independent of the app.

  1. THE RECORDS: the marker, the version, the tools and their commands, the two registry records.
  2. THE GRID: the extent from the lot, the cells inside a ring and along a line, the codes kept.
  3. DISTANCE TRANSFORM: Felzenszwalb and Huttenlocher's one-dimensional pass and the grid's, against brute force.
  4. BUFFER: around a line, outside and inside an area; the checks on its parameters.
  5. DISTANCE: the values and the maximum; the lot's nearest, mean and farthest.
  6. SLOPE CLASSES: the ground's slope between its points, the registry's classes.
  7. EXCLUSIONS: each reason in its order, a buffer from History, a missing layer a warning.
  8. SUITABILITY: the transforms against QGIS's formulas and Esri's rescale; multiplier and percent; restricted and
     no value; the checks.
  9. LOCATE: the region against the reference's, connected, of the area, on the lot.
 10. BUILDABLE AREA: Chalfont's form -- the overlaps at the highest ratio, forest with another resource, the wetlands
     fetched, units not rounded up, an override.
 11. CONSTRAINTS AND OPPORTUNITIES: each cell's first constraint, else its first opportunity; the setbacks.
 12. THE PANE: a field typed and checked, Run from its button, the last run, Open, Run again (the layer overwritten),
     Remove, Reset, undo.
 13. LAYERS: a tool's layer in Layers, drawn in plan, hidden from the panel, Update, out of date when the lot moves.
 14. THE SEARCH AND THE COMMANDS.
 15. KEPT: a reload keeps the runs, the parameters and the layers.
 16. A PHONE: the tool in the sheet, its fields a finger's height, nothing spilling.

The harness never waits without a bound (V123).
"""
import asyncio, json, math, pathlib, re, sys, traceback

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from bim_phase133_site_context_browser_tests import Checks, Stalled, within, m2g   # noqa: E402
import traffic_fixture as FX   # noqa: E402
import land_fixture as LFX     # noqa: E402
import site_tools_reference as R   # noqa: E402
import numpy as np   # noqa: E402
from playwright.async_api import async_playwright   # noqa: E402

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'
CK = Checks()
LOT = [list(p) for p in FX.LOT]
TOOLS = ['buffer', 'distance', 'slopecls', 'exclude', 'suit', 'locate', 'synth', 'capacity']
CMDS = {'buffer': ('BUFFER', 'tlbuffer'), 'distance': ('DISTANCEFROM', 'tldistance'), 'slopecls': ('SLOPECLASSES', 'tlslope'),
        'exclude': ('EXCLUSIONS', 'tlexclude'), 'suit': ('SUITABILITY', 'tlsuit'), 'locate': ('LOCATE', 'tllocate'),
        'synth': ('CONSTRAINTSMAP', 'tlsynth'), 'capacity': ('BUILDABLE', 'tlcapacity')}
WETLAND = [(15, -38), (25, -38), (25, -30), (15, -30)]   # a wetland on the lot's west part, model x, z
TREES = [(40.0, -22.6), (15.0, -25.0)]   # one across the floodplain's edge and the steep band, one on clear ground


def disp(v, dp):
    """the app's bimDispNum: fixed, its trailing zeros dropped"""
    s = ('%.' + str(dp) + 'f') % v
    if '.' in s:
        s = s.rstrip('0').rstrip('.')
    return '0' if s in ('', '-', '-0') else s


def area_text(m2):
    return disp(m2 / 10000, 2) + ' ha' if m2 >= 10000 else disp(m2, 0) + ' m²'


def grid2(G, flat):
    return np.array([np.nan if v is None else v for v in flat], dtype=float).reshape(G['nz'], G['nx'])


def mask2(G, flat):
    return np.array([bool(v) for v in flat]).reshape(G['nz'], G['nx'])


def valley_d(X, Z):
    return (X - LFX.P0[0]) * LFX.N[0] + (Z - LFX.P0[1]) * LFX.N[1]


def wetland_body():
    ring = [list(m2g(x, z)) for (x, z) in WETLAND]
    ring.append(ring[0])
    return {'objectIdFieldName': 'OBJECTID', 'fields': [{'name': 'WETLAND_TYPE'}, {'name': 'ATTRIBUTE'}],
            'features': [{'attributes': {'WETLAND_TYPE': 'Freshwater Emergent Wetland', 'ATTRIBUTE': 'PEM1C'}, 'geometry': {'rings': [ring]}}]}


async def run():
    ck = CK
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()

        async def page_for(vp, mobile=False, nwi='one'):
            ctx = await browser.new_context(viewport=vp, is_mobile=mobile, has_touch=mobile, device_scale_factor=2 if mobile else 1)
            ST = {'tr': (), 'ground': 'land', 'flood': 'zones'}
            for h in FX.HOSTS:
                await ctx.route(h, FX.route_handler(ST))
            for h in ('https://server.arcgisonline.com/**', 'https://tile.openstreetmap.org/**', 'https://*.tile.openstreetmap.org/**'):
                await ctx.route(h, lambda r: r.abort())
            ST['nwi'] = []

            async def nwi_route(route):
                ST['nwi'].append(route.request.url)
                if nwi == 'abort':
                    await route.abort('internetdisconnected')
                    return
                await route.fulfill(status=200, body=json.dumps(wetland_body()), headers={'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'})
            await ctx.route('https://fwspublicservices.wim.usgs.gov/**', nwi_route)
            pg = await ctx.new_page()
            pg.errs = []
            pg.on('pageerror', lambda e: pg.errs.append(str(e)))
            pg.store = ST
            return ctx, pg

        ctx, page = await page_for({'width': 1440, 'height': 900})
        errs = page.errs

        async def safe(js, arg=None, pg=None):
            pg = pg or page
            try:
                return await within(pg.evaluate(js, arg) if arg is not None else pg.evaluate(js), 'evaluate ' + js[:60].replace('\n', ' '))
            except Stalled:
                raise
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:200])
                return None

        async def click(sel, pg=None):
            return await safe("(s)=>{var b=document.querySelector(s);if(!b||b.disabled)return false;b.click();return true;}", sel, pg=pg)

        async def text(sel, pg=None):
            return await safe("(s)=>{var e=document.querySelector(s);return e?e.textContent.replace(/\\s+/g,' ').trim():null;}", sel, pg=pg)

        async def design(pg=None):
            await safe("""(a)=>{var o=window.__a3dState().objs.filter(function(x){return x.t!=='property'&&x.id!=='LOT';});
              o.push({id:'LOT',t:'sketch',name:'Lot',col:'#5ec4b8',pos:[0,0,0],pts:a,y:0,closed:true,layer:'layer-0'});
              window.__a3dTestSetObjs(o);window.__a3dPropertyFromSketch('LOT');}""", LOT, pg=pg)

        async def design_ring(ring, pg=None):
            await safe("""(a)=>{var o=window.__a3dState().objs.filter(function(x){return x.t!=='property'&&x.id!=='LOT';});
              o.push({id:'LOT',t:'sketch',name:'Lot',col:'#5ec4b8',pos:[0,0,0],pts:a,y:0,closed:true,layer:'layer-0'});
              window.__a3dTestSetObjs(o);window.__a3dPropertyFromSketch('LOT');}""", ring, pg=pg)

        async def analyse(pg=None):
            pg = pg or page
            await safe("()=>window.__a3dAnzView(true)", pg=pg)
            await pg.wait_for_timeout(300)
            if await safe("()=>!!document.querySelector('.a3d-awl [data-saaddr]')", pg=pg):
                await pg.fill('.a3d-awl [data-saaddr]', '1 Market Street')
                await pg.press('.a3d-awl [data-saaddr]', 'Enter')
            else:
                await click('.a3d-awl [data-saact="analyze"]', pg=pg)
            for _ in range(300):
                s = await safe("()=>window.__a3dSiteRunState()", pg=pg) or {}
                if not s.get('busy'):
                    return s
                await pg.wait_for_timeout(120)
            raise Stalled('the run did not end')

        async def runt(tid, over=None, pg=None):
            return await safe("(a)=>window.__a3dTlRun(a[0],a[1])", [tid, over], pg=pg) or {}

        async def layer(lid, pg=None):
            return await safe("(i)=>window.__a3dTlLayer(i)", lid, pg=pg) or {}

        async def check(tid, over=None, pg=None):
            return await safe("(a)=>window.__a3dTlCheck(a[0],a[1])", [tid, over], pg=pg) or {}

        async def source(sid, pg=None):
            return await safe("(i)=>window.__a3dTlSource(i)", sid, pg=pg) or {}

        try:
            await within(page.goto('file://' + str(HTML)), 'goto')
            await page.wait_for_timeout(2300)
            await safe("()=>window.__a3dEnter()")

            # ---------------------------------------------------------------------------------
            print("\n-- 1. The records")
            mk = await safe("()=>window.__acad3dV172") or ''
            ck(all(w in mk for w in ('grid', 'dt', 'buffer', 'suitability', 'locate', 'capacity', 'synthesis', 'history', 'pane', 'phone')), "the V172 marker (%s)" % mk[:80])
            mv = re.search(r"var BIM_APP_VERSION=\{v:'V(\d+)'", HTML.read_text(encoding='utf-8'))
            ck(bool(mv) and int(mv.group(1)) >= 172, "the version is V172 or later (%s)" % (mv.group(1) if mv else None))
            T = await safe("()=>window.__a3dTlTools()") or []
            ck([t['id'] for t in T] == TOOLS and all(t['cmd'] == CMDS[t['id']][0] for t in T), "eight tools in the workspace's order, each a command (%s)" % [t['id'] for t in T])
            ck(all(t['sum'] and t['how'] for t in T), "each says what it does and how it works")
            for k, v in R.CHALFONT.items():
                got = await safe("(a)=>window.__a3dStd('land.site_capacity',a)", k)
                if got != v:
                    break
            ck(all([await safe("(a)=>window.__a3dStd('land.site_capacity',a)", k) == v for k, v in R.CHALFONT.items()]),
               "the registry's site capacity record has Chalfont's open space ratios and slope bounds as read (section 440-17)")
            E = await safe("()=>window.__a3dStdEdition('land.site_capacity')") or {}
            ck(E.get('id') == 'land.site_capacity.chalfont' and E.get('lv') == 'S' and E.get('kind') == 'code' and 'Chalfont' in (E.get('where') or ''),
               "its edition: Chalfont's code, read in a secondary copy and said so (%s, %s)" % (E.get('id'), E.get('lv')))
            ck(all([await safe("(a)=>window.__a3dStd('app.synthesis',a)", k) == v for k, v in R.SYNTH.items()]) and
               ((await safe("()=>window.__a3dStdEdition('app.synthesis')")) or {}).get('lv') == 'A',
               "the constraints map's distances and hours are a registry record, the app's own assumption")

            await design()
            st = await analyse()
            ck(not st.get('busy'), "Analyze site ran on the fixture's neighbourhood")

            # ---------------------------------------------------------------------------------
            print("\n-- 2. The grid")
            G = await safe("()=>window.__a3dTlGrid()") or {}
            RG = R.grid(LOT)
            ck(all(G.get(k) == RG[k] for k in ('x0', 'z0', 'cell', 'nx', 'nz')) and G.get('margin') == R.MARGIN,
               "the extent: the lot and 100 m around it, in 1 m cells (%s)" % {k: G.get(k) for k in ('x0', 'z0', 'cell', 'nx', 'nz')})
            lot = mask2(G, G.get('lot') or [0] * (RG['nx'] * RG['nz']))
            ck(np.array_equal(lot, R.inside(RG, LOT)) and G.get('lotArea') == 1200, "the lot's cells by their centres, 1,200 m² (%s)" % G.get('lotArea'))
            tri = [[3.3, -61.7], [77.9, -12.4], [22.1, 31.6]]
            got = mask2(G, await safe("(r)=>window.__a3dTlFill(r)", tri) or [])
            ref, edge = R.inside(RG, tri), R.near_edge(RG, tri)
            ck(got.shape == ref.shape and np.array_equal(got[~edge], ref[~edge]) and got.sum() > 1000, "a ring's cells, even-odd by the centres (%d cells)" % got.sum())
            cup = [[-30.25, -70.25], [60.25, -70.25], [60.25, 20.25], [30.25, 20.25], [30.25, -40.25], [0.25, -40.25], [0.25, 20.25], [-30.25, 20.25]]
            got = mask2(G, await safe("(r)=>window.__a3dTlFill(r)", cup) or [])
            Xc, Zc = R.centres(RG)
            notch = (Xc > 0.25) & (Xc < 30.25) & (Zc > -40.25) & (Zc < 20.25)
            ck(np.array_equal(got, R.inside(RG, cup)) and not got[notch].any() and got.sum() == 90 * 90 - 30 * 60, "a concave ring: its notch left out, row by row (%d cells)" % got.sum())
            BIG_LOT = [[-250, -200], [350, -200], [350, 250], [-250, 250]]
            await design_ring(BIG_LOT)
            Gb = await safe("()=>{var g=window.__a3dTlGrid();delete g.lot;return g;}") or {}
            RGb = R.grid(BIG_LOT)
            one = np.zeros((RGb['nz'], RGb['nx']), dtype=bool)
            one[123, 77] = True
            Db = await safe("(m)=>window.__a3dTlDistance(m)", [int(v) for v in one.ravel()]) or []
            ck(Gb.get('cell') == 2 and RGb['cell'] == 2 and all(Gb.get(k) == RGb[k] for k in ('x0', 'z0', 'nx', 'nz')) and
               len(Db) == RGb['nx'] * RGb['nz'] and np.nanmax(np.abs(grid2(Gb, Db) - R.edt(RGb, one))) < 1e-9,
               "a lot too large for 250,000 cells of 1 m: cells of 2 m, distances still in metres (%sx%s cells of %s m)" % (Gb.get('nx'), Gb.get('nz'), Gb.get('cell')))
            await design()
            seg = [[-7.3, -55.2], [64.8, 12.9]]
            got = mask2(G, await safe("(a)=>window.__a3dTlStroke(a[0],a[1])", seg) or [])
            ck(np.array_equal(got, R.stroke(RG, [seg])), "a line's cells: within half a cell of it (%d cells)" % got.sum())
            LV = [-1, -1, 0, 0, 0, 90, 91, 5, -1, 7, 7, 7]
            cd = await safe("(l)=>window.__a3dTlCode(l)", LV) or {}
            ck(cd.get('back') == LV and len(cd.get('alph', '')) == 92 and '"' not in cd.get('alph', '"') and '\\' not in cd.get('alph', '\\') and
               cd.get('rn') == [2, 3, 1, 1, 1, 1, 3] and len(cd.get('rc', '')) == 7,
               "the codes kept: runs of levels, 92 characters (91 levels and restricted), no quote or backslash, back as they were")

            # ---------------------------------------------------------------------------------
            print("\n-- 3. The distance transform")
            BIG = 1e10
            ok = True
            for f in ([None, None, 0, None, None, None, 0, None], [5, 1, 9, 0, 4, 4, 2, 8, 3], [None] * 6 + [0], [3, None, None, None, None, 0.5, None, 2]):
                d = await safe("(f)=>window.__a3dTlDt1(f)", f) or []
                bf = R.dt1_brute([BIG if v is None else v for v in f])
                ok = ok and len(d) == len(bf) and all(abs(a - b) < 1e-6 for a, b in zip(d, bf))
            ck(ok, "Algorithm 1 along a line: the lower envelope of the parabolas, against brute force")
            streets = mask2(G, (await source('streets')).get('m') or [])
            D = grid2(G, await safe("(m)=>window.__a3dTlDistance(m)", [int(v) for v in streets.ravel()]) or [])
            DR = R.edt(RG, streets)
            ck(D.shape == DR.shape and np.nanmax(np.abs(D - DR)) < 1e-9, "the grid's distances from the streets, exact to brute force (largest %.3g m)" % (np.nanmax(np.abs(D - DR)) if D.shape == DR.shape else -1))
            rng = np.random.RandomState(172)
            sp = rng.rand(RG['nz'], RG['nx']) > 0.9993
            D2 = grid2(G, await safe("(m)=>window.__a3dTlDistance(m)", [int(v) for v in sp.ravel()]) or [])
            ck(D2.shape == DR.shape and np.nanmax(np.abs(D2 - R.edt(RG, sp))) < 1e-9, "and from %d scattered cells" % sp.sum())

            # ---------------------------------------------------------------------------------
            print("\n-- 4. Buffer")
            h = await runt('buffer', {'src': 'streets', 'dist': 7.5, 'side': 'full'})
            L = await layer(h.get('layer'))
            ref = DR <= 7.5 + 1e-9
            got = mask2(G, [v is not None and v >= 0 for v in (L.get('lv') or [])])
            ck(h.get('st') == 'ok' and np.array_equal(got, ref), "around the streets, 7.5 m: every cell within 7.5 m centre to centre (%d of %d)" % (got.sum(), ref.sum()))
            ck(h.get('sum', '').startswith(area_text(ref.sum())) and area_text((ref & lot).sum()) + ' on the lot' in h.get('sum', ''),
               "its area, and the lot's (%s)" % h.get('sum'))
            h = await runt('buffer', {'src': 'lot', 'dist': 5, 'side': 'outside'})
            L = await layer(h.get('layer'))
            got = mask2(G, [v is not None and v >= 0 for v in (L.get('lv') or [])])
            ck(np.array_equal(got, (~lot) & (R.edt(RG, lot) <= 5 + 1e-9)), "Outside an area: the ring around the lot, not the lot (%d cells)" % got.sum())
            h = await runt('buffer', {'src': 'lot', 'dist': 3, 'side': 'inside'})
            L = await layer(h.get('layer'))
            got = mask2(G, [v is not None and v >= 0 for v in (L.get('lv') or [])])
            ck(np.array_equal(got, lot & (np.nan_to_num(R.edt(RG, ~lot, where=lot), nan=1e9) <= 3 + 1e-9)), "Inside an area: the band along the lot's edge, within it (%d cells)" % got.sum())
            c1 = await check('buffer', {'src': 'streets', 'dist': 5, 'side': 'outside'})
            c2 = await check('buffer', {'src': 'streets', 'dist': 0})
            c3 = await check('buffer', {'src': 'streets', 'dist': 100.5})
            c4 = await check('buffer', {'src': 'streets', 'dist': None})
            c5 = await check('buffer', {'src': 'wetlands', 'dist': 5})
            ck((c1.get('E') or {}).get('side') == 'Outside or Inside is for an area layer' and (c2.get('E') or {}).get('dist') == 'More than 0 m' and
               (c3.get('E') or {}).get('dist') == 'At most 100 m' and (c4.get('E') or {}).get('dist') == 'Required' and
               'Not fetched yet' in ((c5.get('E') or {}).get('src') or ''),
               "its checks: Outside for a line, 0 m, beyond the margin, empty, a layer not fetched (%s)" % [c.get('first') for c in (c1, c2, c3, c4, c5)])
            hn = len(await safe("()=>window.__a3dTlHistory()") or [])
            r0 = await runt('buffer', {'src': 'streets', 'dist': 0})
            ck(bool(r0.get('error')) and len(await safe("()=>window.__a3dTlHistory()") or []) == hn, "a tool with an error does not run, and nothing is kept")

            # ---------------------------------------------------------------------------------
            print("\n-- 5. Distance")
            art = mask2(G, (await source('arterials')).get('m') or [])
            DA = R.edt(RG, art)
            h = await runt('distance', {'src': 'arterials', 'max': None})
            L = await layer(h.get('layer'))
            V = grid2(G, L.get('vals') or [])
            hi = float(np.nanmax(DA))
            ck(h.get('st') == 'ok' and L['data']['lo'] == 0 and abs(L['data']['hi'] - hi) < 1e-9 and np.nanmax(np.abs(V - DA)) <= hi / 180 + 1e-9,
               "from the arterials: each cell's distance, kept to its level of 91 (largest difference %.3f m, half a level %.3f)" % (np.nanmax(np.abs(V - DA)), hi / 180))
            inl = DA[lot]
            want = [['On the lot, nearest', disp(inl.min(), 1) + ' m'], ['On the lot, mean', disp(inl.mean(), 1) + ' m'], ['On the lot, farthest', disp(inl.max(), 1) + ' m']]
            ck(h.get('stats') == want, "the lot's nearest, mean and farthest (%s)" % h.get('stats'))
            h = await runt('distance', {'src': 'arterials', 'max': 25})
            V = grid2(G, (await layer(h.get('layer'))).get('vals') or [])
            ck(np.array_equal(np.isnan(V), DA > 25 + 1e-9) and np.nanmax(np.abs(V - DA)) <= 25 / 180 + 1e-9, "with a maximum of 25 m, no value beyond it (%d cells)" % np.isnan(V).sum())

            # ---------------------------------------------------------------------------------
            print("\n-- 6. Slope classes")
            hn_ = await safe("()=>window.__a3dLandHorn()") or {}
            sv = grid2(G, (await source('slope')).get('v') or [])
            grd = await safe("()=>window.__a3dTlGroundGrid()") or {}
            ref = R.resample(RG, grd, hn_.get('slope') or []) if grd else None
            ck(ref is not None and np.array_equal(np.isnan(sv), np.isnan(ref)) and np.nanmax(np.abs(sv - ref)) < 1e-9,
               "the ground's slope on the grid: between the 5 m grid's points, those with no value left out (%s)" % (None if ref is None else '%.2g' % np.nanmax(np.abs(sv - ref))))
            ub = [await safe("(a)=>window.__a3dStd('land.slope',a)", k) for k in ('b1', 'b2', 'b3', 'b4')] + [math.inf]
            h = await runt('slopecls')
            L = await layer(h.get('layer'))
            lv = np.array([-1 if v is None else v for v in L.get('lv') or []]).reshape(RG['nz'], RG['nx'])
            cls = R.classes(sv, ub)
            ck(np.array_equal(lv, cls) and L['data']['n'] == 5 and L['data']['cats'][3] == '15 to 25%', "each cell in the registry's class, a slope at a bound in the class above (%s)" % ub[:4])
            cnt = [int(((cls == i) & lot).sum()) for i in range(5)]
            ck([r[0] for r in h.get('stats', [])] == [L['data']['cats'][i] for i in range(5) if cnt[i]] and
               all(r[1].startswith(area_text(c)) for r, c in zip(h.get('stats', []), [c for c in cnt if c])), "the lot's area in each class (%s)" % h.get('stats'))

            # ---------------------------------------------------------------------------------
            print("\n-- 7. Exclusions")
            X, Zg = R.centres(RG)
            dv = valley_d(X, Zg)
            flood_ref = np.abs(dv) <= 18
            fl = mask2(G, (await source('flood')).get('m') or [])
            fedge = (np.abs(np.abs(dv) - 18) < 1e-3) | (np.abs(np.abs(dv) - 6) < 1e-3)
            ck(np.array_equal(fl[~fedge], flood_ref[~fedge]) and (fl & lot).sum() > 0, "FEMA's 1%% zones (the floodway and AE) on the grid, as the fixture draws them (%d cells, %d on the lot)" % (fl.sum(), (fl & lot).sum()))
            c = await check('exclude')
            ck('Not fetched yet' in ((c.get('W') or {}).get('wetlands') or '') and not c.get('err'), "the wetlands not fetched: a warning, not an error")
            h = await runt('exclude')
            L = await layer(h.get('layer'))
            lv = np.array([-1 if v is None else v for v in L.get('lv') or []]).reshape(RG['nz'], RG['nx'])
            steepAt = await safe("()=>window.__a3dStd('land.slope','b4')")
            want = np.full(lv.shape, -1)
            st_ = np.isfinite(sv) & (sv >= steepAt - 1e-9)
            for i, m in ((0, ~lot), (2, fl), (4, st_)):
                want[(want < 0) & m] = i
            ck(h.get('st') == 'warn' and np.array_equal(lv, want), "outside the lot, then the flood zones, then slopes from %s%%, each cell its first reason (%s)" % (steepAt, h.get('st')))
            ck(h.get('stats', [[None]])[0] == ['Restricted on the lot', area_text((fl & lot).sum()) + ' of 1200 m²'] and ['Left to use', area_text(1200 - (fl & lot).sum())] in h.get('stats', []),
               "what is restricted on the lot, and what is left (%s)" % h.get('stats'))
            hs_ = await runt('exclude', {'outside': False, 'setbacks': False, 'flood': False, 'wetlands': False, 'steep': True, 'steepAt': steepAt, 'buildings': False, 'buffer': ''})
            lvs = np.array([-1 if v is None else v for v in (await layer(hs_.get('layer'))).get('lv') or []]).reshape(RG['nz'], RG['nx'])
            band30 = st_ & (sv < steepAt + 5)
            ck(np.array_equal(lvs == 4, st_) and int(band30.sum()) > 0, "steep slopes alone: every cell from %s%% (%d cells, %d of them under %s%%)" % (steepAt, int(st_.sum()), int(band30.sum()), steepAt + 5))
            hb = await runt('buffer', {'src': 'streets', 'dist': 4, 'side': 'full'})
            h2 = await runt('exclude', {'outside': False, 'setbacks': False, 'flood': True, 'wetlands': False, 'steep': False, 'buildings': True, 'buffer': hb.get('id')})
            lv2 = np.array([-1 if v is None else v for v in (await layer(h2.get('layer'))).get('lv') or []]).reshape(RG['nz'], RG['nx'])
            bld = mask2(G, (await source('buildings')).get('m') or [])
            want = np.full(lv2.shape, -1)
            for i, m in ((2, fl), (5, bld), (6, DR <= 4 + 1e-9)):
                want[(want < 0) & m] = i
            ck(np.array_equal(lv2, want), "the flood zones, the buildings standing, and a buffer from History, in that order")
            c = await check('exclude', {'outside': False, 'setbacks': False, 'flood': False, 'wetlands': False, 'steep': False, 'buildings': False, 'buffer': ''})
            ck((c.get('E') or {}).get('_') == 'Tick at least one reason, or pick a buffer', "nothing ticked: refused")
            excl = await runt('exclude')

            # ---------------------------------------------------------------------------------
            print("\n-- 8. Suitability")
            xs = [0.0, 2.0, 5.0, 7.5, 10.0, 12.5, 20.0, None, 3.3]
            ok = True
            cases = [({'how': 'linear', 'dir': 'up'}, (1, 10)), ({'how': 'linear', 'dir': 'down'}, (1, 10)), ({'how': 'linear', 'dir': 'up', 'lo': 2, 'hi': 12.5}, (1, 5)),
                     ({'how': 'small', 'mid': 6, 'spread': 3}, (1, 10)), ({'how': 'large', 'mid': 6, 'spread': 2.5, 'lo': 1, 'hi': 15}, (1, 9)),
                     ({'how': 'near', 'mid': 7.5}, (1, 10)), ({'how': 'near', 'mid': 30, 'spread': 0.01}, (1, 10)),
                     ({'how': 'classes', 'breaks': '5, 10', 'vals': '9,5,1'}, (1, 10))]
            for o, sc in cases:
                full = {'how': o['how'], 'dir': o.get('dir', 'up'), 'lo': o.get('lo'), 'hi': o.get('hi'), 'mid': o.get('mid'), 'spread': o.get('spread'),
                        'breaks': o.get('breaks', ''), 'vals': o.get('vals', '')}
                t = await safe("(a)=>window.__a3dTlTransform(a[0],a[1],a[2])", [full, xs, list(sc)]) or {}
                ro = dict(full)
                if o['how'] == 'classes':
                    ro['breaks'], ro['vals'] = [5.0, 10.0], [9.0, 5.0, 1.0]
                want = R.transform(ro, [np.nan if x is None else x for x in xs], sc)
                g = np.array([np.nan if v is None else v for v in t.get('out', [])])
                good = g.shape == want.shape and np.array_equal(np.isnan(g), np.isnan(want)) and np.nanmax(np.abs(g - want)) < 1e-9
                if not good:
                    print('      transform %s: %s against %s' % (o, list(g), list(want)))
                ok = ok and good
            ck(ok, "the transforms against QGIS's formulas and Esri's rescale: linear either way, small, large, near, classes (at a break, the class above)")
            t = await safe("(a)=>window.__a3dTlTransform(a[0],a[1],a[2],'cat')", [{'how': 'cats', 'vals': ''}, [0, 1, 2, 3, 4], [1, 10]]) or {}
            t2 = await safe("(a)=>window.__a3dTlTransform(a[0],a[1],a[2])", [{'how': 'linear', 'dir': 'up', 'lo': None, 'hi': None}, [4, 4, 4], [1, 9]]) or {}
            ck(t.get('out') == [10, 7.75, 5.5, 3.25, 1] and t2.get('flat') and t2.get('out') == [5, 5, 5],
               "categories with no values spread over the scale, the first class best; a criterion the same everywhere adds the scale's middle (%s, %s)" % (t.get('out'), t2.get('out')))
            P = await safe("()=>window.__a3dTlParams('suit')") or {}
            ck(P.get('restrict') == excl.get('id') and P.get('crit', {}).get('slope', {}).get('on') and not P.get('crit', {}).get('sunhours', {}).get('on'),
               "its defaults: the latest Exclusions run restricts; a criterion whose layer is missing (sun hours) is off (%s)" % P.get('restrict'))
            crit = {'slope': {'on': True, 'how': 'linear', 'dir': 'down', 'w': 2}, 'streets': {'on': True, 'how': 'small', 'mid': 15, 'spread': 3, 'w': 1},
                    'arterials': {'on': True, 'how': 'linear', 'dir': 'up', 'lo': 0, 'hi': 60, 'w': 1.5}, 'sunhours': {'on': False}, 'trees': {'on': False}, 'slopecls': {'on': False}}
            h = await runt('suit', {'scale': '10', 'weightBy': 'mult', 'restrict': excl.get('id'), 'crit': crit})
            L = await layer(h.get('layer'))
            exl = np.array([-1 if v is None else v for v in (await layer(excl.get('layer'))).get('lv') or []]).reshape(RG['nz'], RG['nx'])
            t_sl = R.transform({'how': 'linear', 'dir': 'down'}, sv.ravel(), (1, 10)).reshape(sv.shape)
            t_st = R.transform({'how': 'small', 'mid': 15, 'spread': 3}, DR.ravel(), (1, 10)).reshape(DR.shape)
            t_ar = R.transform({'how': 'linear', 'dir': 'up', 'lo': 0, 'hi': 60}, DA.ravel(), (1, 10)).reshape(DA.shape)
            S = R.weigh([t_sl, t_st, t_ar], [2, 1, 1.5], 'mult')
            S[exl >= 0] = np.nan
            fin = S[np.isfinite(S)]
            V = grid2(G, L.get('vals') or [])
            lvl = np.array([-1 if v is None else v for v in L.get('lv') or []]).reshape(RG['nz'], RG['nx'])
            step = (fin.max() - fin.min()) / 90
            ck(h.get('st') == 'ok' and abs(L['data']['lo'] - fin.min()) < 1e-9 and abs(L['data']['hi'] - fin.max()) < 1e-9 and
               np.nanmax(np.abs(V - S)) <= step / 2 + 1e-9 and np.array_equal(np.isnan(V), np.isnan(S)),
               "by multiplier: 2 x slope (lower better) + small distance to the streets + 1.5 x linear distance from the arterials, each cell (%.3f of half a level %.3f)" % (np.nanmax(np.abs(V - S)), step / 2))
            ck(L['data']['rest'] == 91 and np.array_equal(lvl == 91, exl >= 0) and L['data']['pal'][91].startswith('#9aa0a6'),
               "the restricted cells kept as restricted, not no value, and drawn grey")
            ck(any('Distance to the streets: small, midpoint 15 m, spread 3' in m.get('s', '') for m in h.get('msgs', [])), "each criterion's transform in the messages")
            crit2 = dict(crit)
            crit2['slope'] = {'on': True, 'how': 'linear', 'dir': 'down', 'w': 50}
            crit2['streets'] = {'on': True, 'how': 'small', 'mid': 15, 'spread': 3, 'w': 30}
            crit2['arterials'] = {'on': True, 'how': 'linear', 'dir': 'up', 'lo': 0, 'hi': 60, 'w': 20}
            h = await runt('suit', {'scale': '5', 'weightBy': 'pct', 'restrict': '', 'crit': crit2})
            V = grid2(G, (await layer(h.get('layer'))).get('vals') or [])
            t_sl5 = R.transform({'how': 'linear', 'dir': 'down'}, sv.ravel(), (1, 5)).reshape(sv.shape)
            t_st5 = R.transform({'how': 'small', 'mid': 15, 'spread': 3}, DR.ravel(), (1, 5)).reshape(DR.shape)
            t_ar5 = R.transform({'how': 'linear', 'dir': 'up', 'lo': 0, 'hi': 60}, DA.ravel(), (1, 5)).reshape(DA.shape)
            S5 = R.weigh([t_sl5, t_st5, t_ar5], [50, 30, 20], 'pct', (1, 5))
            ck(h.get('st') == 'warn' and abs(np.nanmin(V) - 1) < 1e-9 and abs(np.nanmax(V) - 5) < 1e-9 and np.nanmax(np.abs(V - S5)) <= 4 / 180 + 1e-9,
               "by percent, 50, 30 and 20 on the scale 1 to 5: added at their share, the result rescaled to 1 to 5; no restriction, a warning")
            crit2['arterials'] = dict(crit2['arterials'], w=10)
            c = await check('suit', {'weightBy': 'pct', 'crit': crit2})
            ck((c.get('E') or {}).get('_') == 'The percentages add to 90%: they must add to 100%', "percentages that do not add to 100: refused (%s)" % c.get('first'))
            bad = dict(crit)
            bad['slope'] = {'on': True, 'how': 'classes', 'breaks': '10, 5', 'vals': '1,2,3', 'w': 1}
            c1 = await check('suit', {'crit': bad})
            bad['slope'] = {'on': True, 'how': 'classes', 'breaks': '5, 10', 'vals': '1,2', 'w': 1}
            c2 = await check('suit', {'crit': bad})
            bad['slope'] = {'on': True, 'how': 'small', 'mid': 0, 'w': 1}
            c3 = await check('suit', {'crit': bad})
            bad['slope'] = {'on': True, 'how': 'linear', 'lo': 9, 'hi': 3, 'w': 1}
            c4 = await check('suit', {'crit': bad})
            bad['sunhours'] = {'on': True, 'how': 'linear', 'w': 1}
            c5 = await check('suit', {'crit': {k: (v if k == 'sunhours' else {'on': False}) for k, v in bad.items()}})
            E5 = c5.get('E') or {}
            ck('must rise' in ((c1.get('E') or {}).get('crit.slope') or '') and '3 values' in ((c2.get('E') or {}).get('crit.slope') or '') and
               'more than 0' in ((c3.get('E') or {}).get('crit.slope') or '') and 'upper threshold' in ((c4.get('E') or {}).get('crit.slope') or '') and
               'Sun hours: Run Sun hours first' in (E5.get('crit.sunhours') or ''),
               "a criterion's checks: breaks that fall, too few values, a midpoint of 0, thresholds the wrong way, its layer missing")
            await safe("()=>window.__a3dRunCmd('sunhours')")
            sun = grid2(G, (await source('sunhours')).get('v') or [])
            critS = {'slope': {'on': True, 'how': 'linear', 'dir': 'down', 'w': 1}, 'streets': {'on': False}, 'arterials': {'on': False},
                     'sunhours': {'on': True, 'how': 'linear', 'dir': 'up', 'w': 1}, 'trees': {'on': False}, 'slopecls': {'on': False}}
            h = await runt('suit', {'scale': '10', 'weightBy': 'mult', 'restrict': '', 'crit': critS})
            V = grid2(G, (await layer(h.get('layer'))).get('vals') or [])
            t_sun = R.transform({'how': 'linear', 'dir': 'up'}, sun.ravel(), (1, 10)).reshape(sun.shape)
            S2 = R.weigh([t_sl, t_sun], [1, 1], 'mult')
            ck(sun.shape == V.shape and np.isnan(sun).sum() > 0 and (~np.isnan(sun)).sum() > 0 and np.array_equal(np.isnan(V), np.isnan(sun) | np.isnan(sv)) and
               np.nanmax(np.abs(V - S2)) <= (np.nanmax(S2) - np.nanmin(S2)) / 180 + 1e-9,
               "a cell where a criterion has no value (beyond the sun hours run) has none in the result; the rest scored (%d without)" % np.isnan(V).sum())
            await safe("()=>window.__a3dSimClear?window.__a3dSimClear('sun'):null")
            suit_h = await runt('suit', {'scale': '10', 'weightBy': 'mult', 'restrict': excl.get('id'), 'crit': crit})

            # ---------------------------------------------------------------------------------
            print("\n-- 9. Locate")
            h = await runt('locate', {'from': suit_h.get('id'), 'area': 300, 'within': 'lot'})
            L = await layer(h.get('layer'))
            SV = (await layer(suit_h.get('layer'))).get('vals') or []
            okm = [v is not None and bool(lot.ravel()[k]) for k, v in enumerate(SV)]
            cells, mean, nseeds = R.locate([-1e9 if v is None else v for v in SV], okm, RG['nx'], RG['nz'], 300)
            got = [k for k, v in enumerate(L.get('lv') or []) if v == 0]
            ck(h.get('st') == 'ok' and got == cells, "the region: from the best seeds, grown by the best neighbour sharing a side; the reference's own (%d cells)" % len(got))
            ck(R.connected(got, RG['nx']) and len(got) == 300 and all(okm[k] for k in got) and abs(h.get('region', {}).get('mean', 0) - mean) < 1e-9 and
               h.get('region', {}).get('n') == 300 and ['Seeds compared', str(nseeds)] in h.get('stats', []),
               "one connected region, 300 m², on the lot, none of it restricted, its mean the best of %d seeds (%.3f)" % (nseeds, mean or 0))
            free = await runt('suit', {'scale': '10', 'weightBy': 'mult', 'restrict': '', 'crit': crit})
            hl = await runt('locate', {'from': free.get('id'), 'area': 400, 'within': 'lot'})
            ga = [k for k, v in enumerate((await layer(hl.get('layer'))).get('lv') or []) if v == 0]
            ha = await runt('locate', {'from': free.get('id'), 'area': 400, 'within': 'all'})
            gb = [k for k, v in enumerate((await layer(ha.get('layer'))).get('lv') or []) if v == 0]
            ck(len(ga) == 400 and all(lot.ravel()[k] for k in ga) and len(gb) == 400 and not all(lot.ravel()[k] for k in gb),
               "from a map with nothing restricted: within the lot, the region stays on it; over the whole extent, it need not")
            usable = sum(okm)
            c = await check('locate', {'from': suit_h.get('id'), 'area': usable + 1, 'within': 'lot'})
            ck((c.get('E') or {}).get('area') == 'Only %s can be used there' % area_text(usable), "an area larger than can be used: refused (%s)" % c.get('first'))

            # ---------------------------------------------------------------------------------
            print("\n-- 10. Buildable area")
            ids = await safe("""(T)=>{var L=window.__a3dState().objs,src=L.filter(function(o){return o.context&&o.context.kind==='trees';})[0],out=[];
              if(!src)return null;
              T.forEach(function(p,i){var c=JSON.parse(JSON.stringify(src));c.id='TREE172-'+i;c.name='Tree '+i;c.pts=[[p[0],p[1]]];c.pos=[0,0,0];L.push(c);out.push(c.id);});
              window.__a3dTestSetObjs(L);return out;}""", [list(t) for t in TREES])
            ck(bool(ids), "two trees placed on the lot, one across the floodplain's edge and the steep band, one on clear ground")
            w = await safe("()=>window.__a3dTlWetlands()") or {}
            ck(w.get('ok') and len((w.get('w') or {}).get('f') or []) == 1 and page.store['nwi'] and 'geometryType=esriGeometryEnvelope' in page.store['nwi'][-1] and
               'outSR=4326' in page.store['nwi'][-1], "Get wetlands asks the National Wetlands Inventory over the extent, one wetland back")
            wl = mask2(G, (await source('wetlands')).get('m') or [])
            wref = R.inside(RG, WETLAND)
            ck(np.array_equal(wl[~R.near_edge(RG, WETLAND, 0.02)], wref[~R.near_edge(RG, WETLAND, 0.02)]) and wl.sum() == 80, "the wetland on the grid (%d cells)" % wl.sum())
            fo = mask2(G, (await source('forest')).get('m') or [])
            tr = await safe("()=>window.__a3dState().objs.filter(function(o){return o.id.indexOf('TREE172-')===0;}).map(function(o){return o.context;})") or []
            water = mask2(G, (await source('water')).get('m') or [0] * (RG['nx'] * RG['nz'])) if not (await source('water')).get('why') else np.zeros(lot.shape, dtype=bool)
            h = await runt('capacity', {'less': 50, 'density': 13, 'imperv': 60})
            L = await layer(h.get('layer'))
            cat, rr = R.capacity(lot, fl, wl, water, sv, fo, 1)
            lv = np.array([-1 if v is None else v for v in L.get('lv') or []]).reshape(RG['nz'], RG['nx'])
            ck(np.array_equal(np.where(lv < 7, lv, -1)[lot], cat[lot]), "each lot cell's resource: the highest ratio of those there (the floodplain over a steep slope)")
            band = np.isfinite(sv) & (sv >= R.CHALFONT['slope_lo']) & (sv < R.CHALFONT['slope_hi'])
            ov = int(((cat == 0) & band & lot).sum())
            ck(ov > 0 and int(((cat == 4) & lot).sum()) > 0 and int((cat == 5).sum()) > 0 and int((cat == 6).sum()) > 0 and np.array_equal(np.where(lv < 7, lv, -1)[lot & band & fl], np.zeros(int((lot & band & fl).sum()), dtype=int)),
               "overlaps counted once: %d floodplain cells on the lower steep class counted at the floodplain's ratio; forest with another resource %d cells at its own ratio, forest alone %d" % (ov, int((cat == 5).sum()), int((cat == 6).sum())))
            N = R.capacity_numbers(cat, rr, 1200, 50, 1, density=13, imperv=60)
            hc = h.get('capacity') or {}
            ck(abs(hc.get('total', 0) - 1200) < 1e-6 and abs(hc.get('base', 0) - N['base']) < 1e-6 and abs(hc.get('prot', 0) - N['prot']) < 1e-6 and abs(hc.get('net', 0) - N['net']) < 1e-6,
               "Chalfont's form: base %s, resource protection land %s, net buildable %s m²" % (N['base'], round(N['prot'], 2), round(N['net'], 2)))
            rows = dict((r[0], r[1]) for r in h.get('stats', []))
            ck(rows.get('Dwelling units allowed', '').startswith(str(N['units']) + ' at 13 an acre') and abs(hc.get('net', 0) / R.ACRE * 13 % 1) >= 0.5 and rows.get('Impervious surface allowed', '').startswith(area_text(N['imperv'])) and
               rows.get('Net buildable site area') == area_text(N['net']) + ' (' + disp(N['net'] / R.ACRE, 2) + ' acres)',
               "units at 13 an acre not rounded up (%d of %.2f), impervious at 60%%, the net in acres (%s)" % (N['units'], hc.get('net', 0) / R.ACRE * 13, rows.get('Dwelling units allowed')))
            ck(any('Chalfont' in m.get('s', '') for m in h.get('msgs', [])) and (h.get('std') or {}).get('list', [{}])[0].get('t') == 'land.site_capacity',
               "the run says the registry's edition, and keeps its stamp")
            await safe("()=>window.__a3dStdOverride('land.site_capacity','floodplain',0.9,'The municipality counts 90%')")
            h2 = await runt('capacity', {'less': 50, 'density': 13, 'imperv': 60})
            R2 = dict(R.CHALFONT, floodplain=0.9)
            cat2, rr2 = R.capacity(lot, fl, wl, water, sv, fo, 1, R2)
            N2 = R.capacity_numbers(cat2, rr2, 1200, 50, 1)
            ck(abs((h2.get('capacity') or {}).get('prot', 0) - N2['prot']) < 1e-6 and any('overridden' in m.get('s', '') for m in h2.get('msgs', [])),
               "an override of the floodplain's ratio (0.9) changes the calculation, and the run says so")
            await safe("()=>window.__a3dStdClear('land.site_capacity','floodplain')")
            cap_h = await runt('capacity', {'less': 50, 'density': 13, 'imperv': 60})

            # ---------------------------------------------------------------------------------
            print("\n-- 11. Constraints and opportunities")
            h = await runt('synth', {'scope': 'lot'})
            lv = np.array([-1 if v is None else v for v in (await layer(h.get('layer'))).get('lv') or []]).reshape(RG['nz'], RG['nx'])
            DF = R.edt(RG, fo)
            flat = await safe("()=>window.__a3dStd('land.slope','b1')")
            ms = [fl, wl, np.isfinite(sv) & (sv >= steepAt - 1e-9), bld, None, DA <= R.SYNTH['near_art'] + 1e-9, None,
                  DR <= R.SYNTH['front'] + 1e-9, None, DF <= R.SYNTH['green'] + 1e-9, np.isfinite(sv) & (sv < flat - 1e-9)]
            want = np.full(lv.shape, -1)
            for i, m in enumerate(ms):
                if m is not None:
                    want[(want < 0) & m & lot] = i
            ck(np.array_equal(lv, want), "on the lot, each cell's first constraint, else its first opportunity (%s)" % [r[0] for r in h.get('stats', [])])
            ck(any('Sun hours' in m.get('s', '') and 'not shown' in m.get('s', '') for m in h.get('msgs', [])), "with no sun hours run, sunny and overshadowed are not shown, and said so")
            await safe("()=>window.__a3dZnSet('side',4)")
            await safe("()=>window.__a3dZnSet('front',6)")
            h = await runt('synth', {'scope': 'lot'})
            lv3 = np.array([-1 if v is None else v for v in (await layer(h.get('layer'))).get('lv') or []]).reshape(RG['nz'], RG['nx'])
            ck(int((lv3 == 4).sum()) > 0 and any(r[0] == 'Constraint: In the setbacks' for r in h.get('stats', [])), "the zoning's setbacks a constraint once they are recorded (%d cells)" % int((lv3 == 4).sum()))
            hc2 = await runt('capacity', {'less': 50})
            rows = dict((r[0], r[1]) for r in hc2.get('stats', []))
            plate_ok = int(((lv3 != 4) & lot & (cat < 0)).sum())
            ck(rows.get('Buildable within the setbacks, clear of every resource') == area_text(plate_ok), "the buildable area within the setbacks, clear of every resource (%s)" % rows.get('Buildable within the setbacks, clear of every resource'))

            # ---------------------------------------------------------------------------------
            print("\n-- 12. The pane")
            await click('[data-anzact="aw:tool:buffer"]')
            await page.wait_for_timeout(200)
            ck(await safe("()=>{var p=document.querySelector('#a3d-propsbody [data-awpanel]');return p&&p.getAttribute('data-awpanel');}") == 'tool:buffer',
               "a tool's row opens it on the right")
            sel = '#a3d-propsbody [data-tlf="buffer|dist"]'
            await page.fill(sel, '0')
            await safe("(s)=>document.querySelector(s).dispatchEvent(new Event('change',{bubbles:true}))", sel)
            await page.wait_for_timeout(150)
            msg = await text('#a3d-propsbody [data-tlp="dist"] .a3d-tl-msg.err')
            run_off = await safe("()=>{var b=document.querySelector('#a3d-propsbody [data-awact=\"tl:run:buffer\"]');return b?[b.disabled,b.title]:null;}")
            ck(msg == 'More than 0 m' and run_off and run_off[0] and 'Distance: More than 0 m' in run_off[1], "a field typed is checked at once: its message beside it, Run held with why (%s)" % msg)
            await page.fill(sel, '12')
            await safe("(s)=>document.querySelector(s).dispatchEvent(new Event('change',{bubbles:true}))", sel)
            await page.wait_for_timeout(150)
            ck((await safe("()=>window.__a3dTlParams('buffer')") or {}).get('dist') == 12 and not await text('#a3d-propsbody [data-tlp="dist"] .a3d-tl-msg.err'),
               "a good value is kept as the tool's parameter, its message gone")
            n0 = len(await safe("()=>window.__a3dTlHistory()") or [])
            await page.click('#a3d-propsbody [data-awact="tl:run:buffer"]')   # a real click: the field is left, its held refresh done
            await page.wait_for_timeout(300)
            H = await safe("()=>window.__a3dTlHistory()") or []
            ck(len(H) == n0 + 1 and H[0]['tool'] == 'buffer' and H[0]['params']['dist'] == 12, "Run runs it: one more run in History, its parameters kept")
            st_txt = await text('#a3d-propsbody [data-tlst]')
            lay_txt = await text('#a3d-propsbody .a3d-tl-lay')
            ck(st_txt and st_txt.startswith('Succeeded') and await safe("()=>!!document.querySelector('#a3d-propsbody .a3d-tl-stats')") and
               'On the plan: Buffer: Streets and paths, 12 m' in (lay_txt or ''),
               "the last run: its status, its results and its layer on the plan (%s; %s)" % (st_txt, lay_txt))
            lid = H[0].get('layer')
            await click('#a3d-propsbody [data-awact="tl:run:buffer"]')
            await page.wait_for_timeout(250)
            H2 = await safe("()=>window.__a3dTlHistory()") or []
            nl = len([x for x in await safe("()=>window.__a3dResultLayers()") or [] if x['name'] == 'Buffer: Streets and paths, 12 m'])
            ck(len(H2) == n0 + 2 and H2[0].get('layer') == lid and nl == 1 and (await layer(lid)).get('run') == H2[0]['id'],
               "Run again with the same parameters: a new run, the same layer overwritten, as Esri's outputs are")
            await safe("()=>window.__a3dTlSet('buffer|dist','20')")
            await safe("(i)=>window.__a3dTlAct('open:'+i)", H2[1]['id'])
            await page.wait_for_timeout(150)
            ck((await safe("()=>window.__a3dTlParams('buffer')") or {}).get('dist') == 12, "Open from History sets the tool's parameters to the run's")
            await safe("()=>window.__a3dTlAct('reset:buffer')")
            ck((await safe("()=>window.__a3dTlParams('buffer')") or {}).get('dist') == 10, "Reset parameters: the defaults again")
            await safe("(i)=>window.__a3dTlAct('forget:'+i)", H2[1]['id'])
            H3 = await safe("()=>window.__a3dTlHistory()") or []
            ck(len(H3) == n0 + 1 and not any(x['id'] == H2[1]['id'] for x in H3) and bool(await layer(lid)), "Remove takes a run from History; its layer stays")
            n1 = len(await safe("()=>window.__a3dResultLayers()") or [])
            hz = await runt('buffer', {'src': 'trees', 'dist': 3})
            ck(len(await safe("()=>window.__a3dResultLayers()") or []) == n1 + 1, "a run with new parameters adds its own layer")
            await safe("()=>window.__a3dUndo()")
            ck(len(await safe("()=>window.__a3dResultLayers()") or []) == n1 and not any(x['id'] == hz.get('id') for x in await safe("()=>window.__a3dTlHistory()") or []),
               "undo takes the run and its layer back: one step")
            await click('[data-anzact="aw:tool:history"]')
            await page.wait_for_timeout(150)
            ck(await safe("()=>document.querySelectorAll('#a3d-propsbody [data-tlh]').length") == len(await safe("()=>window.__a3dTlHistory()") or []),
               "History lists every run, newest first")

            # ---------------------------------------------------------------------------------
            print("\n-- 13. Layers")
            hc3 = await runt('capacity', {'less': 50})
            shown = [x['id'] for x in await safe("()=>window.__a3dResultLayers()") or [] if x['kind'] == 'tool' and x['visible']]
            ck(shown == [hc3.get('layer')], "a run's output is shown alone, the other tools' hidden, as the workspace shows one analysis at a time (%d shown)" % len(shown))
            RLs = [x for x in await safe("()=>window.__a3dResultLayers()") or [] if x['kind'] == 'tool']
            ck(len(RLs) >= 8 and all(x['cells'] == RG['nx'] * RG['nz'] for x in RLs), "each tool's output is a result layer (%d)" % len(RLs))
            await safe("()=>window.__a3dSetPlanView()")
            await safe("()=>window.__a3dCamSet({tx:30,tz:-25,dist:200})")
            await page.wait_for_timeout(500)
            capL = [x for x in await safe("()=>window.__a3dTlHistory()") or [] if x['tool'] == 'capacity'][0].get('layer')
            ck(capL in (await safe("()=>window.__a3dResultDrawn()") or []), "drawn on the plan")
            await click('[data-anzact="aw:tool:capacity"]')
            await page.wait_for_timeout(150)
            await click('#a3d-propsbody [data-awact="tl:show:%s"]' % capL)
            await page.wait_for_timeout(300)
            ck((await layer(capL)).get('visible') is False and capL not in (await safe("()=>window.__a3dResultDrawn()") or []), "Hide in the panel hides it")
            await click('#a3d-propsbody [data-awact="tl:show:%s"]' % capL)
            await page.wait_for_timeout(200)
            nH = len(await safe("()=>window.__a3dTlHistory()") or [])
            await safe("(i)=>window.__a3dResultLayerUpdate(i)", capL)
            ck(len(await safe("()=>window.__a3dTlHistory()") or []) == nH + 1 and (await safe("()=>window.__a3dTlHistory()"))[0]['tool'] == 'capacity',
               "Update in Layers runs its tool again with the same parameters")
            await safe("""()=>{var L=window.__a3dState().objs.filter(function(o){return o.t!=='property';});L.forEach(function(o){if(o.id==='LOT')o.pts=o.pts.map(function(p){return [p[0]+2,p[1]];});});
              window.__a3dTestSetObjs(L);window.__a3dPropertyFromSketch('LOT');}""")
            ck((await layer(capL)).get('stale') is True, "the lot moved: the layer is out of date")
            await safe("(i)=>window.__a3dResultLayerUpdate(i)", capL)
            ck((await layer(capL)).get('stale') is False, "Update runs it on the lot as it is now")
            await safe("""()=>{var L=window.__a3dState().objs.filter(function(o){return o.t!=='property';});L.forEach(function(o){if(o.id==='LOT')o.pts=o.pts.map(function(p){return [p[0]-2,p[1]];});});
              window.__a3dTestSetObjs(L);window.__a3dPropertyFromSketch('LOT');}""")
            await safe("(i)=>window.__a3dResultLayerUpdate(i)", capL)

            # ---------------------------------------------------------------------------------
            print("\n-- 14. The search and the commands")
            await safe("()=>window.__a3dAnzView(true)")
            await page.wait_for_timeout(200)
            await page.fill('.a3d-awl [data-anzsearch]', 'weighted overlay')
            await page.wait_for_timeout(250)
            vis = await safe("()=>[].filter.call(document.querySelectorAll('.a3d-awl [data-tlrow]'),function(r){return !r.hidden&&!r.closest('[hidden]');}).map(function(r){return r.getAttribute('data-tlrow');})") or []
            ck(vis == ['suit'], "the search finds Suitability by Esri's words for it (%s)" % vis)
            await page.fill('.a3d-awl [data-anzsearch]', 'site capacity')
            await page.wait_for_timeout(250)
            vis = await safe("()=>[].filter.call(document.querySelectorAll('.a3d-awl [data-tlrow]'),function(r){return !r.hidden&&!r.closest('[hidden]');}).map(function(r){return r.getAttribute('data-tlrow');})") or []
            ck(vis == ['capacity'], "and Buildable area by its own (%s)" % vis)
            await page.fill('.a3d-awl [data-anzsearch]', '')
            await page.wait_for_timeout(150)
            okc = True
            for tid, (nm, hk) in CMDS.items():
                await safe("(h)=>window.__a3dRunCmd(h)", hk)
                await page.wait_for_timeout(80)
                p = await safe("()=>{var p=document.querySelector('#a3d-propsbody [data-awpanel]');return p&&p.getAttribute('data-awpanel');}")
                if p != 'tool:' + tid:
                    print('      %s opened %s' % (nm, p))
                    okc = False
            ck(okc, "each command opens its tool in the workspace")
            CAT = pathlib.Path(__file__).resolve().parent.parent / 'docs' / 'data' / 'catalog.json'   # the repository's, whatever build is tested
            cat_json = json.loads(CAT.read_text(encoding='utf-8')) if CAT.exists() else None
            names = json.dumps(cat_json) if cat_json else ''
            ck(all(nm in names for nm, _ in CMDS.values()) and 'SITETOOLS' in names, "the guide's command catalogue has the tools' commands")

            # ---------------------------------------------------------------------------------
            print("\n-- 15. Kept")
            before = await safe("()=>({h:window.__a3dTlHistory().map(function(x){return x.id;}),p:window.__a3dTlParams('suit'),l:window.__a3dResultLayers().filter(function(r){return r.kind==='tool';}).map(function(r){return r.id;})})")
            await page.wait_for_timeout(1500)
            await within(page.reload(), 'reload')
            await page.wait_for_timeout(2300)
            after = await safe("()=>({h:window.__a3dTlHistory().map(function(x){return x.id;}),p:window.__a3dTlParams('suit'),l:window.__a3dResultLayers().filter(function(r){return r.kind==='tool';}).map(function(r){return r.id;})})")
            ck(before and after == before and len(after['h']) > 5, "a reload keeps the runs, the parameters and the layers (%d runs, %d layers)" % (len((after or {}).get('h', [])), len((after or {}).get('l', []))))
            Lr = await layer(capL)
            ck(Lr and (Lr.get('lv') or []) and not Lr.get('stale'), "a kept layer reads back whole, up to date")

            # ---------------------------------------------------------------------------------
            print("\n-- 16. A phone")
            c6, p6 = await page_for({'width': 390, 'height': 844}, mobile=True)
            await within(p6.goto('file://' + str(HTML)), 'goto phone')
            await p6.wait_for_timeout(2300)
            await safe("()=>window.__a3dEnter()", pg=p6)
            await design(p6)
            await safe("()=>{window.__a3dTlSet('suit|crit|slope|on',true);window.__a3dTlSet('suit|crit|slope|how','small');}", pg=p6)
            await safe("()=>window.__a3dRunCmd('tlsuit')", pg=p6)
            await p6.wait_for_timeout(400)
            ph = await safe("""()=>{var p=document.querySelector('#a3d-propsbody [data-awpanel]');if(!p)return null;
              var f=[].map.call(p.querySelectorAll('input[type=text],select'),function(e){return Math.round(e.getBoundingClientRect().height);});
              var b=document.getElementById('a3d-propsbody');return {panel:p.getAttribute('data-awpanel'),min:Math.min.apply(null,f.concat([99])),n:f.length,
              spill:b.scrollWidth>b.clientWidth+1,w:document.documentElement.scrollWidth};}""", pg=p6) or {}
            ck(ph.get('panel') == 'tool:suit' and ph.get('n', 0) >= 6 and ph.get('min', 0) >= 36 and not ph.get('spill') and ph.get('w', 999) <= 390,
               "on a phone the tool is in the sheet, its fields a finger's height, nothing spilling (%s)" % ph)
            ck(not p6.errs, "no page errors on the phone (%s)" % p6.errs[:3])
            await c6.close()

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
    sys.exit(asyncio.run(run()))
