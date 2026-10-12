#!/usr/bin/env python3
"""bim_phase164_site_analysis_in_model_browser_tests.py -- V164: site analysis in the model, from one button.

Every service is answered inside the browser by tests/site_analysis_fixture.py, in its own shape.
What the analyses draw is worked out again here another way: the CRTN and ISO 9613-2 arithmetic
written out from the standards, the sight lines cast in Python against the context's footprints, the
year of hourly wind binned again from the climate fixture, the sun's highest elevation from its
declination.

  1. ANALYZE BEFORE A RUN: the site section and its button; what went (stages, Define, typed
     findings, photographs, pins, checklists) and its hooks; asking for the address.
  2. THE RUN: an address and Enter; each source, in order; the steps; the time zone; the radius;
     one undo step, undone and redone.
  3. LAYERS AND ELEMENTS: Site analysis and its sub-layers; no mesh; the legend.
  4. COMPASS AND SUN: the ring and the distance rings on true north; the three paths on the dome,
     their hours and highest elevations; the sun now.
  5. SHADOWS: three dates, three times, live from the model, drawn and following it; not turned.
  6. WINDS: one arrow for each prevailing direction, the seasons named, the mean speeds, the
     strongest, the rose -- against the fixture binned again.
  7. VIEWS: both isovists against the reference ray cast; the views named by what is seen.
  8. NOISE: CRTN and the barrier term; the classes along Market Street against the reference; the
     streets grouped; the tunnel and the footway out; the site's level; the railway.
  9. LIVE AND EDITABLE: a run again changes nothing; restyled, moved, turned, mirrored, deleted,
     reset; Reset of an analysis; true north turned; an element no longer drawn.
 10. PROPERTIES AND PICKING: the groups; an edit, a refused edit; a click picks an element; a
     locked or hidden layer.
 11. THE CARDS AND FINDINGS: the six rows in their categories; Show, Select, Run again, Reset;
     read-only findings; the search.
 12. FAILURES: a source down; an address not found; busy; the place already set; ANALYZESITE.
     A project from before V164: its stage, a finding typed in and one written on stay in the
     file, unread; a class set by hand gives way to the data's.
 13. A RELOAD, A PHONE AND A TABLET.

The harness never waits without a bound (V123).
"""
import asyncio, datetime, json, math, pathlib, sys, traceback

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from bim_phase133_site_context_browser_tests import Checks, Stalled, within   # noqa: E402
import site_analysis_fixture as FX   # noqa: E402
import climate_fixture as CFX   # noqa: E402
from playwright.async_api import async_playwright   # noqa: E402

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'
CK = Checks()
BLOCKERS = ('https://server.arcgisonline.com/**', 'https://tile.openstreetmap.org/**', 'https://*.tile.openstreetmap.org/**')
TOWER = [-12, -10, 12, 10, 24]   # the project's own building: 24 by 20 m, 24 m high, on the site
L10 = math.log10


# ---- the standards, written out ----------------------------------------------------------------
def crtn_l0(q18, v, p):
    return 29.1 + 10 * L10(q18) + 33 * L10(v + 40 + 500 / v) + 10 * L10(1 + 5 * p / v) - 68.8


def crtn_at(l0, dcl, half):
    d = max(1.0, dcl - half)
    return l0 - 10 * L10(math.sqrt((d + 3.5) ** 2 + 3.5 ** 2) / 13.5)


def crtn_reach(l0, t, half):
    dp = 13.5 * 10 ** ((l0 - t) / 10)
    d2 = dp * dp - 3.5 * 3.5
    if d2 <= 0:
        return 0.0
    d = math.sqrt(d2) - 3.5
    return min(300.0, d + half) if d > 0 else 0.0


def iso9613_dz(a, h, x):
    """the barrier term at 500 Hz: source 0.5 m up at 0, a wall a off and h high, the point x off 4 m up"""
    if not h > 0 or not x > a or h <= 0.5 + 3.5 * a / x:
        return 0.0
    z = math.hypot(a, h - 0.5) + math.hypot(x - a, h - 4) - math.hypot(x, 3.5)
    return min(20.0, 10 * L10(3 + 20 * z / 0.686)) if z > 0 else 0.0


def ray_hit(ox, oz, dx, dz, poly, mx):
    best, n = mx, len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        ex, ez = b[0] - a[0], b[1] - a[1]
        den = dx * ez - dz * ex
        if abs(den) < 1e-12:
            continue
        t = ((a[0] - ox) * ez - (a[1] - oz) * ex) / den
        s = ((a[0] - ox) * dz - (a[1] - oz) * dx) / den
        if t > 0.01 and 0 <= s <= 1 and t < best:
            best = t
    return best


def jround(v, d=1):
    k = 10 ** d
    return math.floor(v * k + 0.5) / k


def winds(year, lat=40.0):
    """the climate fixture's year of hours, binned as Open-Meteo's would be by any wind rose"""
    h = CFX.hourly(year)['hourly']
    bins, calm = [0.5, 2, 4, 6, 8], 0.5
    months = {'year': list(range(12)), 'winter': [11, 0, 1], 'summer': [5, 6, 7], 'spring': [2, 3, 4], 'autumn': [8, 9, 10]}
    R = {k: {'c': [[0] * 5 for _ in range(16)], 'n': 0, 'calm': 0, 'sws': [0.0] * 16, 'sn': [0] * 16} for k in months}
    for t, ws, wd in zip(h['time'], h['wind_speed_10m'], h['wind_direction_10m']):
        mm = int(t[5:7]) - 1
        sec = int(math.floor(((wd % 360) + 360) % 360 / 22.5 + 0.5)) % 16
        b = -1
        if ws >= calm:
            for k in range(4, -1, -1):
                if ws >= bins[k]:
                    b = k
                    break
        for key, ms in months.items():
            if mm not in ms:
                continue
            r = R[key]
            r['n'] += 1
            if b < 0:
                r['calm'] += 1
            else:
                r['c'][sec][b] += 1
                r['sws'][sec] += ws
                r['sn'][sec] += 1
    out = {}
    for key, r in R.items():
        prev, pp = None, 0.0
        for k in range(16):
            tot = 100.0 * sum(r['c'][k]) / r['n'] if r['n'] else 0
            if tot > pp:
                pp, prev = jround(tot, 1), k
        best, bv = -1, 0
        for k in range(16):
            sv = r['c'][k][4] + r['c'][k][3]
            if sv > bv:
                bv, best = sv, k
        out[key] = {'prev': prev, 'prevPct': pp, 'strong': best, 'secMean': [jround(r['sws'][k] / r['sn'][k], 1) if r['sn'][k] else None for k in range(16)]}
    return out


DIRS = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']


async def run():
    ck = CK
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1440, 'height': 900})
        ST = {}
        for h in FX.HOSTS:
            await ctx.route(h, FX.route_handler(ST))
        for h in BLOCKERS:
            await ctx.route(h, lambda r: r.abort())
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

        async def toast(pg=None):
            return await safe("()=>{var t=document.getElementById('a3d-toast');return t?t.textContent:'';}", pg=pg) or ''

        async def wait_run(pg=None, bound=60):
            for _ in range(bound * 4):
                s = await safe("()=>window.__a3dSiteRunState()", pg=pg) or {}
                if not s.get('busy'):
                    return s
                await (pg or page).wait_for_timeout(250)
            raise Stalled('the run did not end')

        async def objs(pg=None):
            return (await safe("()=>window.__a3dState().objs", pg=pg)) or []

        async def diags(a=None, pg=None):
            return [o for o in await objs(pg) if o.get('t') == 'diag' and (a is None or o['dg']['a'] == a)]

        async def by_key(k, pg=None):
            for o in await diags(pg=pg):
                if o['dg']['k'] == k:
                    return o
            return None

        async def state(pg=None):
            return (await safe("()=>window.__a3dDgState()", pg=pg)) or {}

        async def steps(pg=None):
            return {s['id']: s for s in ((await safe("()=>window.__a3dSiteRunState()", pg=pg)) or {}).get('steps', [])}

        async def panel(sel, pg=None):
            return await safe("(s)=>{var w=document.querySelector('.a3d-analyze-wrap');return w?[].map.call(w.querySelectorAll(s),function(e){return (e.textContent||'').replace(/\\s+/g,' ').trim();}):null;}", sel, pg=pg)

        async def tower(pg=None):
            await safe("""(a)=>{var x0=a[0],z0=a[1],x1=a[2],z1=a[3],h=a[4];return window.__a3dPushTestObj({id:'TOWER',t:'solid',name:'Tower',pos:[0,0,0],layer:'layer-0',
              mesh:{v:[[x0,0,z0],[x1,0,z0],[x1,0,z1],[x0,0,z1],[x0,h,z0],[x1,h,z0],[x1,h,z1],[x0,h,z1]],f:[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]}});}""", TOWER, pg=pg)

        def dist2(p, c=(0, 0)):
            return math.hypot(p[0] - c[0], p[2] - c[1])

        try:
            await within(page.goto('file://' + str(HTML)), 'goto')
            await page.wait_for_timeout(2300)
            await safe("()=>window.__a3dEnter()")
            await tower()

            # ---------------------------------------------------------------------------------
            print("\n-- 1. Analyze before a run")
            await safe("()=>window.__a3dAnzView(true)")
            await page.wait_for_timeout(300)
            ck(await safe("()=>!!document.querySelector('.a3d-analyze-wrap [data-anzsec=\"site\"] [data-saact=\"analyze\"]')") is True, "Analyze opens on the site and its one button")
            ck((await panel('[data-saact="analyze"]') or [''])[0] == 'Analyze site', "the button reads Analyze site")
            ck(await safe("()=>!!document.querySelector('.a3d-analyze-wrap [data-saaddr]')") is True, "the site not placed: an address box beside it")
            gone = await safe("""()=>{var w=document.querySelector('.a3d-analyze-wrap'),t=w.textContent;return {stages:!!w.querySelector('[data-sastage],.a3d-sastages'),define:!!w.querySelector('[data-anzsec="define"],[data-saf],#a3d-saptype,#a3d-saq'),
              checks:!!w.querySelector('[data-sachk]')||/At the desk|On site/.test(t),add:/Add finding/.test(t),edit:!!w.querySelector('[data-saact^="edit"],[data-saff]'),photo:!!w.querySelector('[data-saphoto],input[type=file]'),
              fill:!!w.querySelector('[data-saact="fill"]')};}""") or {}
            ck(gone and not any(gone.values()), "no stages, no Define, no checklists, no Add finding, no Edit, no photographs, no Fill (%s)" % gone)
            hooks = await safe("()=>['__a3dSaAdd','__a3dSaSet','__a3dSaDel','__a3dSaDefine','__a3dSaCheck','__a3dSaPlace','__a3dSaStartPin','__a3dSaPhotoUrl','__a3dSaPins','__a3dSaEdit'].filter(function(k){return typeof window[k]!=='undefined';})")
            ck(hooks == [], "and the hooks that served them are gone (%s)" % hooks)
            stdz = await safe("()=>window.__a3dSaStandard()") or {}
            ck('stages' not in stdz and len(stdz.get('cats', [])) == 10 and all(set(c) == {'id', 'n'} for c in stdz['cats']), "the standard: ten categories, no stages, no checklists")
            ck(await safe("()=>window.__acad3dV158.length>0&&/analyzesite/.test(window.__acad3dV164)") is True, "the V164 marker")
            ver = await safe("""()=>{var m=Array.prototype.map.call(document.scripts,function(s){return s.textContent;}).join('').match(/var BIM_APP_VERSION=\\{v:'(V\\d+)'/);return m?m[1]:null;}""")
            ck(ver and int(ver[1:]) >= 164, "and the app says V164 or later (%s)" % ver)   # AMENDED FOR V165: a later version
            # AMENDED FOR V165: the land and water rows are V165's to check; these six are as they were
            cards = await safe("()=>window.__a3dAnzCats().filter(function(c){return /^dg(frame|sun|shadow|wind|views|noise)$/.test(c.id);})") or []
            ck(cards == [{'id': 'dgframe', 'group': 'location'}, {'id': 'dgsun', 'group': 'climate'}, {'id': 'dgshadow', 'group': 'climate'},
                         {'id': 'dgwind', 'group': 'climate'}, {'id': 'dgviews', 'group': 'people'}, {'id': 'dgnoise', 'group': 'risk'}],
               "six analysis rows, each in the category it answers (%s)" % cards)
            ck(all('Not run yet' in (t or '') for t in (await panel('[data-anzcard^="dg"] .a3d-anzsum') or ['x'])), "each says it has not run yet")
            n0 = len(ST.get('hits', []))
            await safe("()=>document.querySelector('[data-saact=\"analyze\"]').click()")
            await page.wait_for_timeout(200)
            ck('Where is the site' in await toast() and len(ST.get('hits', [])) == n0, "with no address and no place, it asks where the site is, and fetches nothing")
            ck(await safe("()=>document.activeElement&&document.activeElement.hasAttribute('data-saaddr')") is True, "and puts the cursor in the address box")

            # ---------------------------------------------------------------------------------
            print("\n-- 2. The run")
            u0 = await safe("()=>window.__a3dUndoDepth()")
            await page.fill('[data-saaddr]', '1 Market Street')
            await page.press('[data-saaddr]', 'Enter')
            await page.wait_for_timeout(150)
            ck(await safe("()=>window.__a3dSiteRunState().busy") is True, "Enter in the address runs it")
            ck((await panel('[data-saact="analyze"]') or [''])[0] == 'Analyzing ...' and await safe("()=>document.querySelector('[data-saact=\"analyze\"]').disabled") is True,
               "while it runs the button says so and waits")
            fin = await wait_run()
            S = {s['id']: s for s in fin.get('steps', [])}
            hits = [h[0] for h in ST.get('hits', [])]
            ck(hits.count('geo') == 1, "the address asked for once (Nominatim)")
            ck('ctx' in hits and 'acc' in hits and hits.index('ctx') < hits.index('acc'), "the context first, the access after it: Overpass asked one thing at a time")
            ck(hits.count('clim') == 4, "the climate's four sources asked")
            ck([S[k]['state'] for k in ('place', 'context', 'climate', 'access', 'zoning', 'draw')] == ['ok', 'ok', 'ok', 'ok', 'skip', 'ok'],
               "the steps: the site, context, climate, access done; zoning skipped; the analyses drawn (%s)" % [S[k]['state'] for k in S])
            ck('1 Market Street, Sample Town' in S['place']['text'] and '40.00000' in S['place']['text'], "the site step names the address and its place")
            ck('45 buildings' in S['context']['text'] and '300 m now (it was 150 m)' in S['context']['text'], "the context step counts what came, and says the radius is 300 m now")
            ck('UTC−5' in S['climate']['text'] and '4 earthquakes' in S['climate']['text'], "the climate step: its sources, and the time zone")
            ck('walk times' in S['access']['text'] and 'census tract' in S['access']['text'], "the access step")
            ck('Needs the property line' in S['zoning']['text'], "zoning skipped, saying why")
            ck(isinstance((await state()).get('last', {}).get('date'), str), "the last run kept with the project")
            site_tz = await safe("""()=>{window.__a3dSelectFor([]);window.__a3dSetPropTab('site');window.__a3dRefreshProps();
              var e=document.querySelector('#a3d-propsbody input[data-propmodel="suntz"]');return e?e.value:null;}""")
            ck(site_tz == '-5', "the UTC offset is -5, from Open-Meteo's answer: the sun needs no typing (%s)" % site_tz)
            u1 = await safe("()=>window.__a3dUndoDepth()")
            ck(u1 == u0 + 1, "one undo step for the whole run (%s -> %s)" % (u0, u1))
            n_all = len(await diags())
            ck(n_all >= 35, "%d elements drawn" % n_all)
            ck(S['draw']['text'].startswith('%d elements on Layers, Site analysis' % n_all), "the last step counts them (%s)" % S['draw']['text'][:70])
            await safe("()=>window.__a3dUndo()")
            await page.wait_for_timeout(200)
            ob = await objs()
            ck(not [o for o in ob if o.get('t') == 'diag'] and not [o for o in ob if o.get('context')], "undo takes it all away: the elements and the context")
            ck(await safe("""()=>{window.__a3dSelectFor([]);window.__a3dSetPropTab('site');window.__a3dRefreshProps();var e=document.querySelector('#a3d-propsbody input[data-propmodel="sunlat"]');return e?e.value:null;}""") == '',
               "and the site's place with it: one step back")
            await safe("()=>window.__a3dRedo()")
            await page.wait_for_timeout(200)
            ck(len(await diags()) == n_all, "redo brings it all back")

            # ---------------------------------------------------------------------------------
            print("\n-- 3. Layers and elements")
            D = await state()
            LY = {l['id']: l for l in (await safe("()=>window.__a3dLayers()") or [])}
            root = LY.get(D.get('layers', {}).get('root'))
            ck(root is not None and root['name'] == 'Site analysis' and not root.get('parent'), "a root layer, Site analysis")
            NAMES = {'frame': 'Compass and distance', 'sun': 'Sun paths', 'shadow': 'Shadows', 'wind': 'Winds', 'views': 'Views', 'noise': 'Noise'}
            subs = [LY.get(D['layers'].get(a)) for a in NAMES]
            ck(all(subs) and all(l['name'] == 'Site analysis - ' + NAMES[a] and l.get('parent') == root['id'] for a, l in zip(NAMES, subs)),
               "under it a layer for each analysis, Site analysis - its name")
            shl = D['layers'].get('shadow')
            want = [('shadow:03-20', 'Site analysis - Shadows 20 March', True), ('shadow:06-21', 'Site analysis - Shadows 21 June', False), ('shadow:12-21', 'Site analysis - Shadows 21 December', False)]
            ck(all(LY.get(D['layers'].get(k)) and LY[D['layers'][k]]['name'] == n and LY[D['layers'][k]].get('parent') == shl and (LY[D['layers'][k]].get('visible') is not False) == v for k, n, v in want),
               "the shadows' dates under Shadows: 20 March shown, the solstices off")
            DG = await diags()
            lay_ok = all(o['layer'] == (D['layers'].get('shadow:' + o['dg']['g']['live']['date'][5:]) if o['dg']['g'].get('kind') == 'live' else D['layers'][o['dg']['a']]) for o in DG)
            ck(lay_ok, "every element on its analysis's layer, each shadow on its date's")
            ck(all('mesh' not in o for o in DG), "no element has a mesh: schedules, quantities, the LOD checks and the exports pass them by")
            ck(all(o['dg'].get('gen') and o['dg'].get('info', {}).get('title') for o in DG if o['dg']['g'].get('kind') != 'live' or True), "each keeps the analysis's own version and says what it shows")
            # AMENDED FOR V165: the land and water layers off while the key is read, so it is V164's six as before;
            # V165's suite reads the key with them, and its compacting
            LAND = ('contours', 'slope', 'aspect', 'flow', 'ponds', 'flood')
            was = {a: (LY.get(D['layers'].get(a)) or {}).get('visible') is not False for a in LAND}
            for a in LAND:
                if D['layers'].get(a):
                    await safe("(i)=>window.__a3dLayerSet(i,'visible',false)", D['layers'][a])
            # AMENDED FOR V166: movement's layers too, those shown, and left off after (V166's suite reads them): each
            # toggle is an undo step, and the history holds 50, which the run's own step is counted against below
            for a in ('streets', 'cycling', 'transit', 'walk', 'needs', 'vehicles'):
                if D['layers'].get(a) and (LY.get(D['layers'][a]) or {}).get('visible') is not False:
                    await safe("(i)=>window.__a3dLayerSet(i,'visible',false)", D['layers'][a])
            await safe("()=>{window.__a3dSetPlanView();window.__a3dCamSet({tx:0,tz:0,dist:300});}")
            await page.wait_for_timeout(400)
            LG = await safe("()=>window.__a3dDgLegend()") or {}
            ck([b['title'] for b in LG.get('blocks', [])] == list(NAMES.values()), "the legend: each analysis shown, in order (%s)" % [b['title'] for b in LG.get('blocks', [])])
            nb = [b for b in LG.get('blocks', []) if b['title'] == 'Noise']
            ck(nb and nb[0]['rows'] == ['55', '60', '65', '70', '75+ dB', 'source'] and 'CRTN' in nb[0]['src'], "a key, not a list: noise's classes in short, and its source")
            sr = await safe("()=>window.__a3dSafeViewRect()") or {}
            bx = LG.get('box') or [0, 0, 9999, 9999]
            ck(bx[0] >= sr.get('x', 0) and bx[0] + bx[2] <= sr.get('x', 0) + sr.get('w', 0) + 0.5 and bx[1] + bx[3] <= sr.get('y', 0) + sr.get('h', 0) + 0.5 and bx[3] < 460,
               "the legend inside the view, at the top right, %d px tall" % bx[3])
            await safe("()=>window.__a3dAnzView(true)")
            await safe("()=>document.querySelector('[data-saact=\"dglegend\"]').click()")
            await page.wait_for_timeout(150)
            ck(await safe("()=>window.__a3dDgLegend()") is None and (await state()).get('legendOff') is True, "Hide the legend hides it, and the project remembers")
            ck((await panel('[data-saact="dglegend"]') or [''])[0] == 'Show the legend', "the button says Show the legend")
            await safe("()=>document.querySelector('[data-saact=\"dglegend\"]').click()")
            await page.wait_for_timeout(150)
            ck(await safe("()=>window.__a3dDgLegend()") is not None, "and shows it again")
            for a in LAND:   # AMENDED FOR V165: as they were
                if D['layers'].get(a) and was[a]:
                    await safe("(i)=>window.__a3dLayerSet(i,'visible',true)", D['layers'][a])
            keep = await objs()
            await safe("(o)=>{window.__a3dTestSetObjs(o.filter(function(x){return x.t==='diag';}));window.__a3dFit();}", keep)
            cam = await safe("()=>window.__a3dState().cam") or {}
            ck(cam.get('dist', 0) > 150, "Zoom Extents fits the diagrams too: a drawing of only them frames them (%s)" % round(cam.get('dist', 0)))
            await safe("(o)=>window.__a3dTestSetObjs(o)", keep)

            # ---------------------------------------------------------------------------------
            print("\n-- 4. Compass and sun")
            site = await safe("()=>window.__a3dDgSite()") or {}
            ck(site.get('c') == [0, 0] and abs(site.get('r', 0) - math.hypot(24, 20) / 2) < 1e-9 and site.get('Rc') == 30 and site.get('own') == 1 and site.get('top') == 24 and site.get('ctxR') == 300,
               "the site: the building's centre, its half-diagonal, a 30 m ring, its top 24 m, the context 300 m")
            # a wing 20 m east: the two together 62 by 20 m, so the ring is past its 30 m floor
            await safe("""()=>window.__a3dPushTestObj({id:'WING',t:'solid',name:'Wing',pos:[0,0,0],layer:'layer-0',
              mesh:{v:[[30,0,-10],[50,0,-10],[50,0,10],[30,0,10],[30,10,-10],[50,10,-10],[50,10,10],[30,10,10]],f:[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]}})""")
            s2 = await safe("()=>window.__a3dDgSite()") or {}
            r2 = math.hypot(62, 20) / 2
            ck(s2.get('own') == 2 and abs(s2.get('r', 0) - r2) < 1e-9 and s2.get('Rc') == max(30, math.ceil(r2 * 1.7 / 5) * 5) == 60,
               "a wing added: the ring grows to 60 m, 1.7 times the half-diagonal (%.1f m) to the next 5 m (%s)" % (r2, s2.get('Rc')))
            await safe("()=>window.__a3dDel('WING')")
            ck((await safe("()=>window.__a3dDgSite()") or {}).get('Rc') == 30, "and back to 30 m without it")
            ring = await by_key('ring')
            ck(ring and len(ring['dg']['g']['pts']) == 96 and max(abs(dist2(p) - 30) for p in ring['dg']['g']['pts']) < 1e-9, "the compass ring: 96 points 30 m from the centre")
            ck([k for k in ('dist:100', 'dist:200', 'dist:300', 'dist:400') if await by_key(k)] == ['dist:100', 'dist:200', 'dist:300'], "distance rings every 100 m to the context's edge")
            r200 = await by_key('dist:200')
            ck(r200 and max(abs(dist2(p) - 200) for p in r200['dg']['g']['pts']) < 1e-9 and 'about 3 min' in json.dumps(r200['dg']['info']), "each ring at its distance, its walk in minutes")
            tk = await by_key('ticks')
            nl = [l for l in tk['dg']['lb'] if l['t'] == 'N'][0] if tk else None
            ck(nl and abs(nl['p'][0]) < 1e-9 and abs(nl['p'][2] + 36) < 1e-9 and len(tk['dg']['lb']) == 16, "sixteen points, N on true north 1.2 rings out")
            YR = str(datetime.date.today().year)
            paths = {k: await by_key('path:' + k) for k in ('06-21', '03-20', '12-21')}
            ck(all(paths.values()), "three sun paths: 21 June, the equinoxes, 21 December")
            ck(all(max(abs(math.sqrt(p[0] ** 2 + p[1] ** 2 + p[2] ** 2) - 30) for p in o['dg']['g']['pts']) < 1e-9 for o in paths.values() if o), "each on a dome 30 m over the site, as the compass ring")
            def highest(o):
                for r in o['dg']['info']['rows']:
                    if r[0] == 'Highest':
                        return float(r[1].split('°')[0])
            # the declination at each date's noon: 23.43 at the June solstice, -23.43 at December's, near 0 at the equinox
            ck(paths['06-21'] and abs(highest(paths['06-21']) - (90 - 40 + 23.43)) < 0.25, "21 June: highest %.1f°, as 90 - 40 + 23.4" % (highest(paths['06-21']) or 0))
            ck(paths['12-21'] and abs(highest(paths['12-21']) - (90 - 40 - 23.43)) < 0.25, "21 December: highest %.1f°, as 90 - 40 - 23.4" % (highest(paths['12-21']) or 0))
            ck(paths['03-20'] and abs(highest(paths['03-20']) - 50) < 0.6, "the equinox: highest %.1f°, near 50" % (highest(paths['03-20']) or 0))
            mk = paths['06-21']['dg']['g']['marks']
            ck(14 <= len(mk) <= 16 and all(m['t'].endswith('h') and m['t'][:-1].isdigit() for m in mk), "a dot an hour while the sun is up in June (%d)" % len(mk))
            ck(paths['06-21']['dg']['info']['date'] == YR + '-06-21' and 'UTC−5' in json.dumps(paths['06-21']['dg']['info'], ensure_ascii=False), "dated, and clocked at the site's offset")
            now = await by_key('now')
            ck(now and now['dg']['sym']['type'] == 'dot' and abs(math.sqrt(sum(c * c for c in now['dg']['sym']['p'])) - 30) < 1e-9, "the sun now: a dot on the dome")

            # ---------------------------------------------------------------------------------
            print("\n-- 5. Shadows")
            SH = await diags('shadow')
            ck(len(SH) == 9 and all(o['dg']['g']['kind'] == 'live' and 'pts' not in o['dg']['g'] for o in SH), "nine shadows, three dates by 9, 12 and 15, live: no geometry kept")
            ck(sorted(set(o['dg']['g']['live']['date'][5:] for o in SH)) == ['03-20', '06-21', '12-21'] and sorted(set(o['dg']['g']['live']['time'] for o in SH)) == ['09:00', '12:00', '15:00'], "the dates and times")
            cr = await safe("()=>window.__a3dCanvasRect()") or {}

            async def pix(pt):
                s = await safe("(p)=>window.__a3dDgToScreen(p)", pt)
                if not s:
                    return None
                x, y = cr.get('left', 0) + s[0], cr.get('top', 0) + s[1]
                im = await page.screenshot(clip={'x': x - 2, 'y': y - 2, 'width': 4, 'height': 4})
                return im

            async def shade_diff(pt):
                lid = D['layers']['shadow:03-20']
                a = await pix(pt)
                await safe("(i)=>window.__a3dLayerSet(i,'visible',false)", lid)
                await page.wait_for_timeout(250)
                b = await pix(pt)
                await safe("(i)=>window.__a3dLayerSet(i,'visible',true)", lid)
                await page.wait_for_timeout(250)
                return a != b

            await safe("()=>{window.__a3dSelectFor([]);window.__a3dSetPlanView();window.__a3dCamSet({tx:0,tz:0,dist:120});}")
            await page.wait_for_timeout(400)
            ck(await shade_diff([0, 0, -22]) is True, "the equinox's shadows are drawn: north of the building at noon, the ground darker")
            await safe("()=>window.__a3dCamSet({tx:0,tz:-70,dist:120})")
            await page.wait_for_timeout(300)
            ck(await shade_diff([45, 0, -110]) is False, "the tower next door casts none: the shadows are the project's, the context is what they fall among")
            await safe("()=>window.__a3dCamSet({tx:0,tz:0,dist:120})")
            await page.wait_for_timeout(300)
            await safe("()=>{window.__a3dMoveObjects(['TOWER'],60,0,0);window.__a3dCamSet({tx:30,tz:0,dist:120});}")   # both points clear of the legend
            await page.wait_for_timeout(300)
            ck(await shade_diff([60, 0, -22]) is True and await shade_diff([0, 0, -22]) is False, "move the building and its shadow follows: drawn from the model each time")
            await safe("()=>window.__a3dMoveObjects(['TOWER'],-60,0,0)")
            await page.wait_for_timeout(200)
            t0 = (await by_key('sh:03-20:12h'))
            await safe("(id)=>window.__a3dRotateSelection([id],[0,0],Math.PI/2)", t0['id'])
            ck((await by_key('sh:03-20:12h'))['dg']['g'] == t0['dg']['g'] and 'skipped' in await toast(), "a live shadow is not turned: it follows the sun")

            # ---------------------------------------------------------------------------------
            print("\n-- 6. Winds")
            W = winds(datetime.date.today().year - 1)
            order = []
            for sn in ('winter', 'spring', 'summer', 'autumn'):
                if W[sn]['prev'] not in order:
                    order.append(W[sn]['prev'])
            WD = await diags('wind')
            arrows = [o for o in WD if o['dg']['k'].startswith('prevail:')]
            ck([o['dg']['k'] for o in arrows] == ['prevail:' + DIRS[s] for s in order], "one arrow for each prevailing direction (%s)" % [o['dg']['k'] for o in arrows])
            for o in arrows:
                sec = DIRS.index(o['dg']['k'].split(':')[1])
                seas = [sn for sn in ('winter', 'spring', 'summer', 'autumn') if W[sn]['prev'] == sec]
                words = ', '.join(('%s %d%%' % (sn.capitalize() if j == 0 else sn, int(math.floor(W[sn]['prevPct'] + 0.5)))) for j, sn in enumerate(seas))
                ck(o['dg']['lb'][0]['t'] == 'Wind from %s: %s of hours' % (DIRS[sec], words), "its label names its seasons and their shares: %s" % o['dg']['lb'][0]['t'])
                rows = {r[0].split(' (')[0].lower(): r[1] for r in o['dg']['info']['rows']}
                sp_ok = all(abs(float(rows[sn].split(', ')[1].split(' m/s')[0]) - W[sn]['secMean'][sec]) < 0.051 for sn in seas)
                ck(sp_ok, "and Properties each season's mean speed from that quarter, as the hours binned again")
                P = o['dg']['g']['pts']
                az = (math.degrees(math.atan2(P[3][0], -P[3][2])) + 360) % 360
                ck(len(P) == 7 and abs(dist2(P[3]) - 33) < 1e-6 and min(abs(az - sec * 22.5), 360 - abs(az - sec * 22.5)) < 1e-6 and dist2(P[0]) > dist2(P[3]),
                   "drawn from the %s, its point 1.1 rings from the centre, towards the site" % DIRS[sec])
            stg = await by_key('strong')
            ck(stg and stg['dg']['sym']['type'] == 'storm' and stg['dg']['lb'][0]['t'] == 'Strongest winds: ' + DIRS[W['year']['strong']], "the strongest winds, from %s, as binned again" % DIRS[W['year']['strong']])
            rose = await by_key('rose')
            ck(rose and len(rose['dg']['g']['pts']) == 48 and rose['dg']['g']['closed'], "the year's rose, sixteen petals")
            leg = [r for r in (await state())['runs']['wind']['legend']]
            ck([r['short'] for r in leg][:len(order)] == [', '.join(sn.capitalize() for sn in ('winter', 'spring', 'summer', 'autumn') if W[sn]['prev'] == s) for s in order], "the key names each arrow by its seasons")

            # ---------------------------------------------------------------------------------
            print("\n-- 7. Views")
            O = await objs()
            BLD, TRE = [], []
            for o in O:
                c = o.get('context') or {}
                q = o.get('pos') or [0, 0, 0]
                if c.get('kind') == 'buildings' and c.get('footprint') and c.get('height', 0) > 0:
                    BLD.append(([[p[0] + q[0], p[1] + q[2]] for p in c['footprint']], c['height'], (c.get('tags') or {}).get('name') or o['name']))
                elif c.get('kind') == 'trees' and c.get('height', 0) > 0:
                    cx, cz, rr = o['pts'][0][0] + q[0], o['pts'][0][1] + q[2], max(1, (c.get('crown') or 4) / 2)
                    TRE.append(([[cx + rr * math.cos(k * math.pi / 4), cz + rr * math.sin(k * math.pi / 4)] for k in range(8)], c['height'], o['name']))

            def iso(eye):
                use = [b for b in BLD + TRE if b[1] > eye]
                out = []
                for k in range(180):
                    a = math.radians(k * 2)
                    dx, dz, d = math.sin(a), -math.cos(a), 300.0
                    for b in use:
                        d = ray_hit(0, 0, dx, dz, b[0], d)
                    out.append(d)
                return out
            ie, it = iso(1.6), iso(22.5)
            ae, at = await by_key('iso:eye'), await by_key('iso:top')
            de = max(abs(dist2(p) - max(1, r)) for p, r in zip(ae['dg']['g']['pts'], ie))
            dt = max(abs(dist2(p) - max(1, r)) for p, r in zip(at['dg']['g']['pts'], it))
            ck(len(ae['dg']['g']['pts']) == 180 and de < 1e-6, "at eye height: 180 sight lines, each as far as the Python ray cast says (%.2g)" % de)
            ck(dt < 1e-6 and '22.5 m up (the top floor)' in at['dg']['info']['title'], "from the top floor, 22.5 m up: only the 45 m tower stops a line (%.2g)" % dt)
            VW = sorted([o for o in await diags('views') if o['dg']['k'].startswith('view:')], key=lambda o: o['name'])
            names = [o['name'] for o in VW]
            ck(names == ['View: Sample Tower', 'View: green space', 'View: water (Sample Lake)'], "the views: the lake, the meadow, the tower; the park within 15° of the lake gives way (%s)" % names)

            def az_of(o):
                p = o['dg']['g']['pts'][1]
                return (math.degrees(math.atan2(p[0], -p[2])) + 360) % 360

            def run_of(ks):
                on = [k in ks for k in range(180)]
                best, st = (0, 0), -1
                for k in range(360):
                    if on[k % 180]:
                        if st < 0:
                            st = k
                        n = k - st + 1
                        if n > best[1] and n <= 180:
                            best = (st % 180, n)
                    else:
                        st = -1
                return ((best[0] + (best[1] - 1) / 2) * 2) % 360
            tw = [b for b in BLD if b[2] == 'Sample Tower'][0]
            tks = [k for k in range(180) if ray_hit(0, 0, math.sin(math.radians(2 * k)), -math.cos(math.radians(2 * k)), tw[0], it[k] + 0.5) < it[k] + 0.5]
            lake = [o for o in O if (o.get('context') or {}).get('kind') == 'water'][0]
            lp = [[p[0], p[1]] for p in lake['pts']]

            def inside(x, z, poly):
                r, j = False, len(poly) - 1
                for i in range(len(poly)):
                    xi, zi, xj, zj = poly[i][0], poly[i][1], poly[j][0], poly[j][1]
                    if (zi > z) != (zj > z) and x < (xj - xi) * (z - zi) / (zj - zi) + xi:
                        r = not r
                    j = i
                return r
            lks = [k for k in range(180) if any(inside(d * math.sin(math.radians(2 * k)), -d * math.cos(math.radians(2 * k)), lp) for d in range(20, int(it[k]) + 1, 10))]
            v_t = [o for o in VW if o['name'] == 'View: Sample Tower'][0]
            v_l = [o for o in VW if o['name'].startswith('View: water')][0]
            ck(abs(az_of(v_t) - run_of(tks)) < 1e-6 and 15 < az_of(v_t) < 50, "the tower's view towards it, NNE, %.0f°" % az_of(v_t))
            ck(abs(az_of(v_l) - run_of(lks)) < 1e-6 and 200 < az_of(v_l) < 250, "the lake's towards it, SW, %.0f°" % az_of(v_l))
            ck(all(o['dg']['s'].get('head') and o['dg']['lb'][0]['t'] == o['name'].upper() for o in VW), "each an arrow, labelled in capitals")

            # ---------------------------------------------------------------------------------
            print("\n-- 8. Noise")
            c1 = await safe("()=>window.__a3dDgCrtn(1000,75,0,10,0)") or {}
            ck(abs(c1.get('L0', 0) - 59.11) < 0.01, "CRTN: 1000 vehicles in 18 hours at 75 km/h, none heavy: 59.1 dB, the speed correction nil (%.3f)" % c1.get('L0', 0))
            ck(abs(c1.get('at', 0) - crtn_at(c1['L0'], 10, 0)) < 1e-9 and abs(c1['at'] - (c1['L0'] - 10 * L10(math.hypot(13.5, 3.5) / 13.5))) < 1e-9, "10 m from the kerb, 4 m up: the slant distance's correction")
            ck(all(abs(a - crtn_reach(c1['L0'], t, 0)) < 1e-9 for a, t in zip(c1.get('reach', []), (55, 60, 65, 70, 75))), "each class's reach")
            ck((await safe("()=>window.__a3dDgCrtn(1e6,100,15,10,0)") or {}).get('reach', [0])[0] == 300, "no class reaches past 300 m, where CRTN stops")
            g = await safe("()=>window.__a3dDgBarrier(10,0.5+3.5*10/20+1e-3,20)")
            ck(abs((g or 0) - 10 * L10(3)) < 0.01, "ISO 9613-2: a wall just grazing the line of sight, 4.8 dB")
            ck(await safe("()=>window.__a3dDgBarrier(10,1,20)") == 0 and await safe("()=>window.__a3dDgBarrier(5,60,200)") == 20, "a wall under the line of sight, nothing; a tall one, 20 dB at most")
            rc = await safe("()=>[window.__a3dDgRoadClass('motorway_link'),window.__a3dDgRoadClass('service'),window.__a3dDgRoadClass('primary')]") or [None, None, None]
            ck(rc[0] and rc[0]['u'] == 20500 and rc[0]['link'] and 'slip road' in rc[0]['fc'] and rc[1] is None and rc[2]['u'] == 17000, "FHWA's classes: a slip road a quarter of its road, a service road none")
            NZ = await diags('noise')
            nn = sorted(o['name'] for o in NZ)
            ck(nn == sorted(['Noise, I 99', 'Noise, Market Street', 'Noise, Elm Street', 'Noise, Local road, unnamed', 'Noise source, I 99', 'Noise source, Market Street',
                             'Noise source, Elm Street', 'Noise source, Local road', 'Noise source, railway Main Line', 'Noise at the site']),
               "a street once, the unnamed ones of a class together, the loudest marked; the tunnel and the footway out (%s)" % nn)
            ROADS = {}
            for o in O:
                c = o.get('context') or {}
                if c.get('kind') == 'roads':
                    ROADS[(c.get('tags') or {}).get('name') or (c.get('tags') or {}).get('ref') or ('#' + str(c.get('id')))] = [[p[0], p[1]] for p in o['pts']]
            ms = ROADS['Market Street']
            L0m = crtn_l0(0.94 * 17000, 30 * 1.609344, 8)
            mk_ = [o for o in NZ if o['name'] == 'Noise, Market Street'][0]
            ck('about %d dB 10 m from the kerb' % round(L0m) in mk_['dg']['info']['title'] and '48 km/h (its limit)' in json.dumps(mk_['dg']['info']) and 'urban' in json.dumps(mk_['dg']['info']),
               "Market Street: urban (45 buildings), 30 mph, four lanes, 8%% heavy: about %d dB at 10 m" % round(L0m))
            BB = [(b[0], b[1], b[2]) for b in BLD]

            def first_wall(ox, oz, dx, dz, mx, skip_site=False):
                d, H = mx, 0
                for poly, h, nm in BB:
                    if skip_site and inside(0, 0, poly):
                        continue
                    t = ray_hit(ox, oz, dx, dz, poly, d)
                    if t < d:
                        d, H = t, h
                return d, H

            def reach_side(px, pz, nx, nz, l0, half, T):
                R = [crtn_reach(l0, t, half) for t in (55, 60, 65, 70, 75)]
                d, H = first_wall(px, pz, nx, nz, R[0])
                r = crtn_reach(l0, T, half)
                if r <= d:
                    return r
                best, x = d, d + 5
                while x <= R[0] + 0.01:
                    if crtn_at(l0, x, half) - iso9613_dz(d, H, x) >= T:
                        best = x
                    else:
                        break
                    x += 5
                return best
            a0, a1 = ms[0], ms[-1]
            Lm = math.hypot(a1[0] - a0[0], a1[1] - a0[1])
            m = math.ceil(Lm / 15)
            k = 30
            px, pz = a0[0] + (a1[0] - a0[0]) * k / m, a0[1] + (a1[1] - a0[1]) * k / m
            nx, nz = -(a1[1] - a0[1]) / Lm, (a1[0] - a0[0]) / Lm
            b55 = [b for b in mk_['dg']['g']['bands'] if b['lv'] == 55][0]['pts']
            south, north = reach_side(px, pz, nx, nz, L0m, 7.3, 55), reach_side(px, pz, -nx, -nz, L0m, 7.3, 55)
            vs, vn = b55[k], b55[2 * (m + 1) - 1 - k]
            ck(abs(math.hypot(vs[0] - px, vs[2] - pz) - south) < 1e-6 and south < 60,
               "55 dB south of Market Street at x %.0f: %.1f m, stopped at the Low Shed and screened behind it" % (px, south))
            ck(abs(math.hypot(vn[0] - px, vn[2] - pz) - north) < 1e-6 and north > 100, "and north, %.1f m, across the open site to the tower" % north)

            def at_site(name, l0, half):
                P = ROADS[name]
                best = None
                for i in range(len(P) - 1):
                    ax, az_, ex, ez = P[i][0], P[i][1], P[i + 1][0] - P[i][0], P[i + 1][1] - P[i][1]
                    l2 = ex * ex + ez * ez
                    t = max(0, min(1, ((0 - ax) * ex + (0 - az_) * ez) / l2)) if l2 > 1e-9 else 0
                    cx_, cz_ = ax + t * ex, az_ + t * ez
                    dd = math.hypot(cx_, cz_)
                    if best is None or dd < best[0]:
                        best = (dd, cx_, cz_)
                dd, cx_, cz_ = best
                x = max(half + 1, dd - site['r'])
                d, H = first_wall(cx_, cz_, -cx_ / dd, -cz_ / dd, x, True)
                return crtn_at(l0, x, half) - (iso9613_dz(d, H, x) if d < x else 0)
            Ls = {'I 99': at_site('I 99', crtn_l0(0.94 * 82000, 100, 15), 7.3), 'Market Street': at_site('Market Street', L0m, 7.3),
                  'Elm Street': at_site('Elm Street', crtn_l0(0.94 * 390, 40, 2), 3.65)}
            loc = [r for r in ROADS if r.startswith('#')]
            Ls['Local road'] = max(at_site(r, crtn_l0(0.94 * 390, 40, 2), 3.65) for r in loc if ROADS[r] and r != '#1005')
            for nm_, v in Ls.items():
                src = [o for o in NZ if o['name'] == 'Noise source, ' + nm_]
                ck(src and src[0]['dg']['lb'][0]['t'] == '%s: about %d dB' % (nm_, round(v)), "%s at the site: about %d dB, screened where a building stands between" % (nm_, round(v)))
            elm = [o for o in NZ if o['name'] == 'Noise source, Elm Street'][0]
            ck('behind West House' in json.dumps(elm['dg']['info']), "Elm Street's level is lower behind West House, and Properties says so")
            tot = 10 * L10(sum(10 ** (v / 10) for v in Ls.values()))
            st_ = [o for o in NZ if o['name'] == 'Noise at the site'][0]
            ck(st_['dg']['lb'][0]['t'] == 'About %d dB at the site' % round(tot), "the site: about %d dB, each street once, added as energy" % round(tot))
            rl = [o for o in NZ if o['name'] == 'Noise source, railway Main Line'][0]
            ck(rl['dg']['lb'][0]['t'] == 'Railway (Main Line), 220 m: noise and vibration' and rl['dg']['sym']['type'] == 'noise', "the railway, 220 m east, named as a source")
            ck('Under Road' not in json.dumps([o['name'] for o in NZ]) and all(b['lv'] in (55, 60, 65, 70, 75) for o in NZ for b in (o['dg']['g'].get('bands') or [])), "classes in 5 dB steps from 55")

            # ---------------------------------------------------------------------------------
            print("\n-- 9. Live and editable")
            b4 = {o['id']: o for o in await diags()}
            u = await safe("()=>window.__a3dUndoDepth()")
            r = await safe("()=>window.__a3dDgRun()") or {}
            af = {o['id']: o for o in await diags()}
            ck(set(af) == set(b4) and all(af[i]['dg']['g'] == b4[i]['dg']['g'] for i in af), "run again with nothing changed: the same elements, the same geometry")
            ck(all(v.get('made') == 0 and v.get('updated') == v.get('total') for v in r.values()) and await safe("()=>window.__a3dUndoDepth()") == u + 1, "updated in place, nothing new; one undo step")
            e200 = await by_key('dist:200')
            await safe("(id)=>window.__a3dDgSet(id,'stroke','#ff0000')", e200['id'])
            await safe("(id)=>window.__a3dMoveObjects([id],0,0,4)", e200['id'])
            e2 = await by_key('ring2')
            await safe("(id)=>window.__a3dMoveObjects([id],5,0,0)", e2['id'])
            etk = await by_key('ticks')
            await safe("(id)=>window.__a3dRotateSelection([id],[0,0],Math.PI/2)", etk['id'])
            e100 = await by_key('dist:100')
            await safe("(id)=>window.__a3dMirrorSelection([id],[0,-10],[0,10])", e100['id'])
            e300 = await by_key('dist:300')
            await safe("(id)=>window.__a3dSelectFor([id])", e300['id'])
            await page.focus('canvas') if await safe("()=>!!document.querySelector('canvas')") else None
            await page.keyboard.press('Delete')
            await page.wait_for_timeout(150)
            ck(await by_key('dist:300') is None, "an element deleted, as anything is: Delete")
            lst = {x['k']: x for x in await safe("()=>window.__a3dDgList('frame')") or []}
            ck(lst['dist:200']['edited'] and lst['ring2']['edited'] and lst['ticks']['edited'] and not lst['ring']['edited'], "restyled, moved and turned elements read as changed; the rest as drawn")
            cp = [x for x in lst.values() if '#' in x['k']]
            ck(len(cp) == 1 and cp[0]['mine'] and cp[0]['k'].startswith('dist:100#'), "a mirror copy is yours: a key of its own, nothing to reset to")
            await safe("()=>window.__a3dDgRun('frame')")
            ck((await by_key('dist:200'))['dg']['s']['stroke'] == '#ff0000' and (await by_key('dist:200'))['pos'] == [0, 0, 4] and (await by_key('ring2'))['pos'][0] == 5, "run again: the colour and the moves are kept")
            ck((await by_key('ticks'))['dg']['g']['pts'][0] != b4[etk['id']]['dg']['g']['pts'][0] and len([x for x in await diags('frame') if '#' in x['dg']['k']]) == 1, "the turn and the copy too")
            ck(await by_key('dist:300') is None and 'dist:300' in (await state())['runs']['frame']['gone'], "what you deleted stays deleted")
            l2 = {x['k']: x for x in await safe("()=>window.__a3dDgList('frame')") or []}
            ck(not l2['dist:200']['newer'] and [x for x in l2.values() if '#' in x['k']][0]['orphan'], "nothing newer to offer; the copy, which the analysis does not draw, kept")
            await safe("(id)=>window.__a3dDgReset(id)", (await by_key('dist:200'))['id'])
            d200 = await by_key('dist:200')
            ck(d200['dg']['s']['stroke'] == '#9aa7b4' and d200['pos'] == [0, 0, 0], "Reset gives an element back its analysis's look and its place (%s)" % d200['pos'])
            u = await safe("()=>window.__a3dUndoDepth()")
            await safe("()=>window.__a3dDgResetAnalysis('frame')")
            fr = {o['dg']['k']: o for o in await diags('frame')}
            ck('dist:300' in fr and not [k for k in fr if '#' in k] and fr['ring2']['pos'] == [0, 0, 0] and fr['ticks']['dg']['g'] == b4[etk['id']]['dg']['g'],
               "Reset of the analysis: the deleted back, the copy gone, the moved and turned as drawn")
            ck(await safe("()=>window.__a3dUndoDepth()") == u + 1 and not (await state())['runs']['frame']['gone'], "one undo step, and nothing deleted any longer")
            await safe("(id)=>window.__a3dDgSet(id,'stroke','#00ff00')", fr['ring']['id'])
            await safe("""()=>{window.__a3dSelectFor([]);window.__a3dSetPropTab('site');window.__a3dRefreshProps();var e=document.querySelector('#a3d-propsbody input[data-propmodel="truenorth"]');e.value='20';e.dispatchEvent(new Event('change',{bubbles:true}));}""")
            await safe("()=>window.__a3dDgRun('frame')")
            tk2 = await by_key('ticks')
            n2 = [l for l in tk2['dg']['lb'] if l['t'] == 'N'][0]
            ck(abs(n2['p'][0] - 36 * math.sin(math.radians(20))) < 1e-9 and abs(n2['p'][2] + 36 * math.cos(math.radians(20))) < 1e-9, "true north turned 20°: the compass follows")
            lr = {x['k']: x for x in await safe("()=>window.__a3dDgList('frame')") or []}
            ck(lr['ring']['edited'] and (await by_key('ring'))['dg']['s']['stroke'] == '#00ff00', "the restyled ring is kept as you left it")
            ck(lr['ring']['newer'] and not lr['ring2']['newer'], "and marked: turned, the analysis would draw the ring differently now; the outer ring, redrawn, is as drawn")
            await safe("(id)=>{window.__a3dSelectFor([id]);window.__a3dRefreshProps();}", (await by_key('ring'))['id'])
            ck(await safe("()=>/would draw it differently now/.test(document.getElementById('a3d-propsbody').innerText)&&!document.querySelector('#a3d-propsbody [data-dgact=\"reset\"]').disabled") is True,
               "Properties says so, and Reset is ready to take the analysis's version")
            await safe("""()=>{window.__a3dSelectFor([]);window.__a3dSetPropTab('site');window.__a3dRefreshProps();var e=document.querySelector('#a3d-propsbody input[data-propmodel="truenorth"]');e.value='0';e.dispatchEvent(new Event('change',{bubbles:true}));}""")
            await safe("()=>window.__a3dDgResetAnalysis('frame')")
            saved = await objs()
            esrc = [o for o in await diags('noise') if o['name'] == 'Noise source, Elm Street'][0]
            await safe("(id)=>window.__a3dDgSet(id,'stroke','#123456')", esrc['id'])
            await safe("()=>{var o=window.__a3dState().objs.filter(function(x){return !(x.context&&x.context.kind==='roads'&&x.context.tags&&x.context.tags.name==='Elm Street');});window.__a3dTestSetObjs(o);}")
            await safe("()=>window.__a3dDgRun('noise')")
            names2 = [o['name'] for o in await diags('noise')]
            ek = [x for x in await safe("()=>window.__a3dDgList('noise')") or [] if x['name'] == 'Noise source, Elm Street']
            ck('Noise, Elm Street' not in names2 and ek and ek[0]['orphan'], "a street gone from the context: its classes go; the marker you changed stays, marked as no longer drawn")
            await safe("(o)=>window.__a3dTestSetObjs(o)", saved)
            await safe("()=>window.__a3dDgResetAnalysis('noise')")

            # ---------------------------------------------------------------------------------
            print("\n-- 10. Properties and picking")
            rg = await by_key('ring')
            await safe("(id)=>{window.__a3dSelectFor([id]);window.__a3dRefreshProps();}", rg['id'])
            await page.wait_for_timeout(150)
            pt = await safe("()=>document.getElementById('a3d-propsbody').innerText") or ''
            ck('Site analysis : Compass and distance' in pt and all(w in pt for w in ('What It Shows', 'How It Was Worked Out', 'Appearance', 'Analysis', 'As the analysis drew it')),
               "Properties: what it is, what it shows, how it was worked out, how it looks, its status")
            u = await safe("()=>window.__a3dUndoDepth()")
            await safe("()=>{var e=document.querySelector('#a3d-propsbody [data-dgf=\"w\"]');e.value='3';e.dispatchEvent(new Event('change',{bubbles:true}));}")
            ck((await by_key('ring'))['dg']['s']['w'] == 3 and await safe("()=>window.__a3dUndoDepth()") == u + 1, "a width typed: the element changes, one undo step")
            await safe("()=>{var e=document.querySelector('#a3d-propsbody [data-dgf=\"w\"]');e.value='40';e.dispatchEvent(new Event('change',{bubbles:true}));}")
            ck((await by_key('ring'))['dg']['s']['w'] == 3 and await safe("()=>window.__a3dUndoDepth()") == u + 1 and 'A line width is 0.5 to 12 pixels' in await toast(), "a width out of range refused, saying so, and no undo step")
            ck(await safe("()=>/Changed by you/.test(document.getElementById('a3d-propsbody').innerText)&&!document.querySelector('#a3d-propsbody [data-dgact=\"reset\"]').disabled") is True, "its status: changed by you, and Reset ready")
            await safe("()=>document.querySelector('#a3d-propsbody [data-dgact=\"reset\"]').click()")
            ck((await by_key('ring'))['dg']['s'].get('w') == 1.6, "Reset in Properties")
            d2 = await by_key('dist:200')
            await safe("(id)=>{window.__a3dSelectFor([id]);window.__a3dRefreshProps();}", d2['id'])
            await safe("()=>{var e=document.querySelector('#a3d-propsbody [data-dgf=\"lb:0\"]');e.value='Two hundred metres';e.dispatchEvent(new Event('change',{bubbles:true}));}")
            ck((await by_key('dist:200'))['dg']['lb'][0]['t'] == 'Two hundred metres', "a label retyped")
            await safe("()=>window.__a3dDgResetAnalysis('frame')")
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dSetPlanView();window.__a3dCamSet({tx:0,tz:0,dist:260});}")
            await page.wait_for_timeout(400)
            target = [o for o in await diags('noise') if o['dg']['k'] == 'site'][0]   # AMENDED FOR V165: a key is the analysis's own; slope, aspect and flood have a 'site' too
            hits = await safe("()=>window.__a3dDgHits()") or []
            hb = [h for h in hits if h['id'] == target['id'] and h['boxes']]
            ck(bool(hb), "the site's noise label is drawn, and kept to pick")
            if hb:
                b = hb[0]['boxes'][-1]
                cx, cy = cr['left'] + b[0] + b[2] / 2, cr['top'] + b[1] + b[3] / 2
                ck(await safe("(a)=>window.__a3dPick(a[0],a[1])", [b[0] + b[2] / 2, b[1] + b[3] / 2]) == target['id'], "a click on it picks it, before the model under it")
                await page.mouse.click(cx, cy)
                await page.wait_for_timeout(200)
                ck((await safe("()=>window.__a3dState().sel")) == target['id'], "and a real click selects it")
                await safe("(i)=>window.__a3dLayerSet(i,'locked',true)", D['layers']['noise'])
                await page.wait_for_timeout(200)
                ck(await safe("(a)=>window.__a3dPick(a[0],a[1])", [b[0] + b[2] / 2, b[1] + b[3] / 2]) != target['id'], "on a locked layer it is not picked")
                await safe("(i)=>window.__a3dLayerSet(i,'locked',false)", D['layers']['noise'])
            await safe("(i)=>window.__a3dLayerSet(i,'visible',false)", D['layers']['views'])
            await page.wait_for_timeout(250)
            vids = set(o['id'] for o in await diags('views'))
            ck(not [h for h in (await safe("()=>window.__a3dDgHits()") or []) if h['id'] in vids] and 'Views' not in [b['title'] for b in (await safe("()=>window.__a3dDgLegend()") or {}).get('blocks', [])],
               "a hidden layer: not drawn, not picked, not in the legend")
            await safe("(i)=>window.__a3dLayerSet(i,'visible',true)", D['layers']['views'])

            # ---------------------------------------------------------------------------------
            print("\n-- 11. The cards and the findings")
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dAnzView(true);window.__a3dAnalyzeRefresh(true);}")
            await page.wait_for_timeout(200)
            # AMENDED FOR V165: V164's six rows; the land and water rows are V165's to read
            sums = await safe("()=>[].map.call(document.querySelectorAll('[data-anzcard=\"dgframe\"],[data-anzcard=\"dgsun\"],[data-anzcard=\"dgshadow\"],[data-anzcard=\"dgwind\"],[data-anzcard=\"dgviews\"],[data-anzcard=\"dgnoise\"]'),function(r){return r.querySelector('.a3d-anzsum').textContent;})") or []
            ck(len(sums) == 6 and all('element' in t for t in sums), "each row counts its elements on its layer (%s)" % sums[:2])
            await safe("()=>document.querySelector('[data-anzact=\"dg:show:frame\"]').click()")
            await page.wait_for_timeout(150)
            vis = {l['id']: l for l in await safe("()=>window.__a3dLayers()")}
            ck(vis[D['layers']['frame']].get('visible') is False and (await panel('[data-anzact="dg:show:frame"]') or [''])[0] == 'Show', "Hide turns its layer off, and the button says Show")
            await safe("()=>document.querySelector('[data-anzact=\"dg:show:frame\"]').click()")
            vis = {l['id']: l for l in await safe("()=>window.__a3dLayers()")}
            ck(vis[D['layers']['frame']].get('visible') is not False, "and Show turns it on")
            await safe("()=>document.querySelector('[data-anzcard=\"dgnoise\"] [data-anzact=\"dg:select:noise\"]').click()")
            ck(sorted(await safe("()=>window.__a3dState().selSet||[]") or []) == sorted(o['id'] for o in await diags('noise')) or
               sorted((await safe("()=>JSON.parse(JSON.stringify(window.__a3dSelSet?window.__a3dSelSet():[]))")) or []) == sorted(o['id'] for o in await diags('noise')),
               "Select selects the analysis's elements")
            await safe("()=>window.__a3dTestClearUndo()")   # AMENDED FOR V166: from an empty history, as the history holds 50 and the steps before reach it
            u = await safe("()=>window.__a3dUndoDepth()")
            await safe("()=>window.__a3dSelectFor([])")
            await safe("()=>document.querySelector('[data-anzact=\"dg:run:sun\"]').click()")
            ck(await safe("()=>window.__a3dUndoDepth()") == u + 1, "Run again: one undo step")
            ck(await safe("()=>document.querySelectorAll('[data-anzcard=\"dgnoise\"] .a3d-dglegi').length") == 6, "each row carries its key")
            F = (await safe("()=>window.__a3dSa()") or {}).get('findings', [])
            shown = await safe("()=>document.querySelectorAll('.a3d-analyze-wrap .a3d-safind').length")
            ck(shown == len([f for f in F if f.get('auto')]) and shown > 0, "the findings shown are those the data wrote (%d)" % shown)
            ck(await safe("()=>!document.querySelector('.a3d-analyze-wrap .a3d-safind button,.a3d-analyze-wrap .a3d-safind input,.a3d-analyze-wrap .a3d-safind textarea')") is True, "read only: nothing to edit in them")
            li = await safe("()=>[].map.call(document.querySelectorAll('[data-sasteps] li'),function(l){return l.className;})") or []
            ck(len(li) == 7 and 's-ok' in li[0] and 's-skip' in li[5], "the last run's steps stay listed")   # AMENDED FOR V165: Ground and water is a step
            ck((await panel('[data-saact="analyze"]') or [''])[0] == 'Analyze site again', "the button: Analyze site again")
            # 'seismic' is in Environmental risk's question, nowhere in the site's own words (its steps name the noise)
            await safe("()=>{var s=document.querySelector('[data-anzsearch]');s.value='seismic';s.dispatchEvent(new Event('input',{bubbles:true}));}")
            await page.wait_for_timeout(200)
            ck(await safe("()=>{var st=document.querySelector('[data-anzsec=\"site\"]');return !/seismic/i.test(st.textContent)&&!st.hasAttribute('hidden')&&!!st.querySelector('[data-saact=\"analyze\"]')&&!document.querySelector('[data-anzcard=\"dgnoise\"]').hasAttribute('hidden');}") is True,
               "a search: the site and its button stay though none of its words match; the noise row is found in its category")
            await safe("()=>{var s=document.querySelector('[data-anzsearch]');s.value='';s.dispatchEvent(new Event('input',{bubbles:true}));}")

            # ---------------------------------------------------------------------------------
            print("\n-- 12. Failures, and the command")
            ck(await safe("()=>window.__a3dCmdSupported('analyzesite')&&!window.__a3dCmdSupported('safill')") is True, "ANALYZESITE runs; SAFILL's action is gone")
            reg = [c for c in await safe("()=>window.__wsRegistry") if c['name'] in ('ANALYZESITE', 'SAFILL')]
            ck(len(reg) == 1 and reg[0]['name'] == 'ANALYZESITE' and 'SAFILL' in reg[0]['aliases'], "SAFILL is typed into it now")
            n0 = len([h for h in ST['hits'] if h[0] == 'geo'])
            await safe("""()=>{window.__a3dSelectFor([]);window.__a3dSetPropTab('site');window.__a3dRefreshProps();var e=document.querySelector('#a3d-propsbody input[data-propmodel="suntz"]');e.value='-4';e.dispatchEvent(new Event('change',{bubbles:true}));}""")
            await safe("()=>window.__a3dTestClearUndo()")   # AMENDED FOR V166: from an empty history, likewise
            u = await safe("()=>window.__a3dUndoDepth()")
            twice = await safe("""()=>{window.__a3dRunCmd('analyzesite');var b=window.__a3dSiteRunState().busy,r=window.__a3dSiteRun('');
              var t=document.getElementById('a3d-toast');return {busy:b,second:r,said:t?t.textContent:''};}""") or {}
            ck(twice.get('busy') is True and twice.get('second') is None and 'already running' in twice.get('said', ''), "a second run while one runs is refused, and says so")
            fin = await wait_run()
            ck(len([h for h in ST['hits'] if h[0] == 'geo']) == n0 and {s['id']: s['state'] for s in fin['steps']}['place'] == 'ok', "with the site placed, no address is looked up")
            ck(await safe("()=>window.__a3dUndoDepth()") == u + 1, "and the run is one undo step")
            tz2 = await safe("""()=>{window.__a3dSelectFor([]);window.__a3dSetPropTab('site');window.__a3dRefreshProps();var e=document.querySelector('#a3d-propsbody input[data-propmodel="suntz"]');return e?e.value:null;}""")
            ck(tz2 == '-4' and 'the offset already given is kept' in {s['id']: s for s in fin['steps']}['climate']['text'], "an offset you gave is yours: kept, and the step says so")
            ck(not errs, "no page errors (%s)" % errs[:3])
            await page.wait_for_timeout(700)

            # ---- a reload: section 13 begins with it ----
            before = sorted((o['dg']['k'], json.dumps(o['dg']['g'], sort_keys=True)) for o in await diags())
            await within(page.reload(), 'reload')
            await page.wait_for_timeout(2300)
            after = sorted((o['dg']['k'], json.dumps(o['dg']['g'], sort_keys=True)) for o in await diags())
            ck(after == before and len(after) > 30, "a reload keeps every element as it was")
            D2 = await state()
            # AMENDED FOR V165: V164's runs among them, beside the land and water ones
            ck(set(NAMES) <= set(D2.get('runs', {})) and D2.get('last', {}).get('steps') and D2['layers'] == D['layers'], "and the runs, the last run's steps and the layers")
            await ctx.close()

            # ---- failures, each in a fresh browser ----
            async def fresh(mode, vw=(1440, 900), mobile=False):
                c = await browser.new_context(viewport={'width': vw[0], 'height': vw[1]}, has_touch=mobile, is_mobile=mobile)
                st = {'mode': mode}
                for h in FX.HOSTS:
                    await c.route(h, FX.route_handler(st))
                for h in BLOCKERS:
                    await c.route(h, lambda r: r.abort())
                p = await c.new_page()
                e = []
                p.on('pageerror', lambda x: e.append(str(x)))
                await within(p.goto('file://' + str(HTML)), 'goto')
                await p.wait_for_timeout(1800)
                await safe("()=>{window.__a3dEnter();window.__a3dAnzView(true);}", pg=p)
                await p.wait_for_timeout(200)
                return c, p, st, e

            c3, p3, st3, e3 = await fresh({'geo': 'none'})
            u = await safe("()=>window.__a3dUndoDepth()", pg=p3)
            await p3.fill('[data-saaddr]', 'Nowhere Lane')
            await safe("()=>document.querySelector('[data-saact=\"analyze\"]').click()", pg=p3)
            f3 = await wait_run(pg=p3)
            s3 = {s['id']: s for s in f3['steps']}
            ck(s3['place']['state'] == 'fail' and 'Nothing found for Nowhere Lane' in s3['place']['text'] and all(s3[k]['state'] == 'wait' for k in ('context', 'climate', 'access', 'draw')),
               "an address not found: the site step says so, nothing else is asked")
            ck([h[0] for h in st3.get('hits', [])] == ['geo'] and await safe("()=>window.__a3dUndoDepth()", pg=p3) == u, "one request, and no undo step left behind")
            ck(await safe("()=>!document.querySelector('[data-saact=\"analyze\"]').disabled", pg=p3) is True, "and the button is ready again")
            await c3.close()

            c4, p4, st4, e4 = await fresh({'ctx': 'abort'})
            await p4.fill('[data-saaddr]', '1 Market Street')
            await p4.press('[data-saaddr]', 'Enter')
            f4 = await wait_run(pg=p4)
            s4 = {s['id']: s for s in f4['steps']}
            ck(s4['context']['state'] == 'part' and 'Not available: overpass-api.de' in s4['context']['text'] and '1 surface' in s4['context']['text'],
               "OpenStreetMap's servers down: the context step reads Partly -- the terrain came, the servers named (%s)" % s4['context']['text'][-90:])
            ck(s4['climate']['state'] == 'ok' and s4['access']['state'] == 'ok' and s4['draw']['state'] == 'ok', "the rest stands: the climate, the access, the analyses")
            D4 = await state(pg=p4)
            ck('No buildings around' in D4['runs']['views']['note'] and 'No roads' in D4['runs']['noise']['note'] and D4['runs']['sun']['keys'], "views and noise say what they lack; the sun is drawn")
            ck('Context' in s4['draw']['text'] or 'Views: No buildings' in s4['draw']['text'], "the last step names what could not be drawn and why")
            ck(not e4, "no page errors (%s)" % e4[:3])
            await c4.close()

            c5, p5, st5, e5 = await fresh({'clim': 'abort'})
            await p5.fill('[data-saaddr]', '1 Market Street')
            await p5.press('[data-saaddr]', 'Enter')
            f5 = await wait_run(pg=p5)
            s5 = {s['id']: s for s in f5['steps']}
            D5 = await state(pg=p5)
            ck(s5['climate']['state'] == 'fail' and 'UTC offset' in D5['runs']['sun']['note'] and 'No wind yet' in D5['runs']['wind']['note'],
               "the climate down: no time zone, so the sun asks for its offset; no wind")
            ck(D5['runs']['frame']['keys'] and D5['runs']['noise']['keys'], "the compass and the noise drawn all the same")
            await c5.close()

            # ---- a project from before V164: what was typed in it stays in its file, unread ----
            c7, p7, st7, e7 = await fresh({})
            await p7.fill('[data-saaddr]', '1 Market Street')
            await safe("()=>document.querySelector('[data-saact=\"analyze\"]').click()", pg=p7)
            await wait_run(pg=p7)
            env = json.loads(await safe("()=>window.__a3dProjectEnvelope()", pg=p7) or '{}')
            an = env.get('data', {}).get('site', {}).get('analysis', {})
            FD = {f.get('auto'): f for f in an.get('findings', [])}
            ck(FD.get('location.place') and FD.get('access.roads') and FD.get('location.built'), "(a run's findings, to make an old project of: %d)" % len(FD))
            if FD.get('location.place') and FD.get('access.roads'):
                cls0 = FD['location.place']['cls']
                FD['location.place'].update({'cls': 'redflag', 'sev': 3, 'touched': True})          # a class set by hand in V158
                FD['access.roads']['note'] = 'Lorries use it at night'                                 # a note written on a finding
                an['findings'].append({'id': 'safind-typed', 'cat': 'access', 'title': 'School run', 'value': 'Parents park along Market Street at 8 and 3',
                                       'cls': 'constraint', 'sev': 2, 'conf': 'site', 'source': 'Seen on site', 'date': '2026-05-02', 'auto': ''})   # a finding typed in
                an['stage'] = 2                                                                         # V158's stages
                await safe("(t)=>window.__a3dImportProject(t,'Before V164.acad3d.json')", json.dumps(env), pg=p7)
                await safe("()=>{window.__a3dAnzView(true);window.__a3dAnalyzeRefresh(true);}", pg=p7)
                await p7.wait_for_timeout(200)
                shown_t = "()=>[].map.call(document.querySelectorAll('.a3d-analyze-wrap .a3d-safind .a3d-saftt'),function(e){return e.textContent;})"
                S7 = await safe("()=>window.__a3dSa()", pg=p7) or {}
                t7 = await safe(shown_t, pg=p7) or []
                ck(S7.get('stage') == 2 and [f for f in S7.get('findings', []) if f['id'] == 'safind-typed'] and 'School run' not in t7 and 'Streets' in t7 and not await safe("()=>document.querySelector('[data-sastage]')", pg=p7),
                   "an old project opens: its stage and its typed finding kept in the file, neither shown (%d shown)" % len(t7))
                await safe("()=>window.__a3dSaFill()", pg=p7)
                pl = [f for f in (await safe("()=>window.__a3dSa()", pg=p7) or {}).get('findings', []) if f.get('auto') == 'location.place']
                ck(pl and pl[0]['cls'] == cls0, "a class set by hand gives way to the data's at the next fill (%s)" % (pl and pl[0]['cls']))
                await safe("()=>window.__a3dRunCmd('contextremove')", pg=p7)
                await safe("()=>window.__a3dSaFill()", pg=p7)
                await safe("()=>window.__a3dAnalyzeRefresh(true)", pg=p7)
                S8 = {f['id']: f for f in (await safe("()=>window.__a3dSa()", pg=p7) or {}).get('findings', [])}
                rd = S8.get(FD['access.roads']['id']) or {}
                t8 = await safe(shown_t, pg=p7) or []
                ck(rd.get('note') == 'Lorries use it at night' and rd.get('auto') == '' and FD['location.built']['id'] not in S8 and 'safind-typed' in S8 and 'Streets' not in t8,
                   "the context gone: its findings go, but the one written on stays in the file, unread, as does the typed one")
            ck(not e7, "no page errors (%s)" % e7[:3])
            await c7.close()

            # ---------------------------------------------------------------------------------
            print("\n-- 13. A phone and a tablet")
            for vw, label in (((390, 844), 'a phone'), ((820, 1180), 'a tablet')):
                c6, p6, st6, e6 = await fresh({}, vw=vw, mobile=True)
                await p6.fill('[data-saaddr]', '1 Market Street')
                await safe("()=>document.querySelector('[data-saact=\"analyze\"]').click()", pg=p6)
                await wait_run(pg=p6)
                await safe("()=>window.__a3dAnzView(true)", pg=p6)
                await p6.wait_for_timeout(300)
                g6 = await safe("""()=>{var w=document.querySelector('.a3d-analyze-wrap'),b=document.querySelector('[data-saact="analyze"]'),r=b.getBoundingClientRect(),s=document.querySelector('[data-sasteps]');
                  return {bw:r.width,bh:r.height,right:r.right,vw:window.innerWidth,sw:w.scrollWidth,cw:w.clientWidth,ssw:s?s.scrollWidth:0,scw:s?s.clientWidth:0,doc:document.documentElement.scrollWidth};}""", pg=p6) or {}
                ck(g6.get('right', 999) <= g6.get('vw', 0) and g6.get('bh', 0) >= 30, "%s: the button within the screen, %d px tall to touch" % (label, g6.get('bh', 0)))
                ck(g6.get('sw', 9) <= g6.get('cw', 0) + 1 and g6.get('ssw', 9) <= g6.get('scw', 0) + 1 and g6.get('doc', 9999) <= vw[0] + 1, "%s: nothing spills across the panel or the page" % label)
                await safe("()=>{window.__a3dShellSetTab?window.__a3dShellSetTab('model'):0;window.__a3dSetPlanView();window.__a3dCamSet({tx:0,tz:0,dist:300});}", pg=p6)
                await p6.wait_for_timeout(400)
                lg6 = await safe("()=>window.__a3dDgLegend()", pg=p6)
                sr6 = await safe("()=>window.__a3dSafeViewRect()", pg=p6) or {}
                if sr6.get('w', 0) < 620:
                    ck(lg6 is None, "%s: no legend over a view %d px wide; the keys are in Analyze's rows" % (label, sr6.get('w', 0)))
                else:
                    b6 = (lg6 or {}).get('box') or [0, 0, 99999, 0]
                    ck(lg6 is not None and b6[0] >= sr6['x'] - 0.5 and b6[0] + b6[2] <= sr6['x'] + sr6['w'] + 0.5 and b6[1] + b6[3] <= sr6['y'] + sr6['h'] + 0.5,
                       "%s: the legend inside the view, %d px wide" % (label, sr6.get('w', 0)))
                ck(not e6, "%s: no page errors (%s)" % (label, e6[:3]))
                await c6.close()
        except Stalled as e:
            ck(False, 'stalled: %s' % e)
        except Exception:
            traceback.print_exc()
            ck(False, 'the suite raised')
        await browser.close()
    print('\n%d/%d checks passed' % (CK.n - len(CK.bad), CK.n))
    print('RESULT: ' + ('PASS' if not CK.bad else 'FAIL'))
    return not CK.bad


if __name__ == '__main__':
    sys.exit(0 if asyncio.run(run()) else 1)
