#!/usr/bin/env python3
"""bim_phase172b_ladybug_boards_browser_tests.py -- V172b: Ladybug L1 (weather and comfort), and the boards made editable.

The owner's decisions (2026-10-31): Ladybug Tools' own Python, unchanged, run by Pyodide in a worker, its runtime
committed and served with the site; UTCI in CBE Clima's four conditions; the psychrometric chart at 0.5 and 1.0 clo with
Ladybug's five passive strategies; boards that are arranged -- any analysis on any board, boards of one's own -- under
the drawing's own Snap, Grid and Ortho. The runtime is served from runtime/ at the Pages address the one-file app asks
(context.route); the weather is tests/ladybug_fixture.py's made-up year; tests/ladybug_reference.py works the answers out
again, apart from the app and from Ladybug; and the same adapter on the same wheels runs natively here, so the browser's
numbers must be CPython's.

  1. THE RECORDS: the marker, the version, the runtime pinned by its manifest, the registry's four topics.
  2. THE RUNTIME: from file:// at the Pages address; every wheel's SHA-256 checked, a changed one refused and said; no
     network said; then ready, with its versions.
  3. A WEATHER FILE: the station's ZIP (its EPW and DDY) read; an EPW alone; not an EPW refused; the same file twice.
  4. UTCI: in the shade, hour by hour against the official polynomial; all four conditions against native Ladybug; the
     hours outside its range; its scale from the registry.
  5. THE PSYCHROMETRIC CHART: comfort against Fanger's PMV hour by hour (the boundary aside); the strategies against
     native; the registry's PPD and still air taking effect; a strategy parameter out of range put back, said.
  6. WIND: the sectors and calm against the EPW, in the app's speed bands.
  7. DESIGN DAYS: the DDY's five; an EPW alone approximated, and said so.
  8. OPEN-METEO: the request (the year, its variables, Etc/GMT+5); the hours aligned and their gaps filled; UTCI from them
     against the reference; a half-hour zone in UTC; a failure said, nothing lost.
  9. KEPT AND OUT OF DATE: a result keeps its source, versions and standards; a changed standard marks only what used it.
 10. ANALYZE: Climate's five rows, their panels and buttons; Run all; Show on the board; Add to a board.
 11. THE BOARDS' FIGURES: every card named; a board without a list drawn as the kept build draws it; the catalogue.
 12. EDIT: nothing kept until a change; the arrangement where the board's grid puts the figures; Grid, Snap and Ortho on
     real drags; the keys; a figure's menu, options, fit, duplicate, remove and add; reset; undo and redo.
 13. BANDS AND READING ORDER against the reference; a list's checks.
 14. BOARDS OF ONE'S OWN: new, named, any analysis on it; its notes; a board duplicated; deleted and back; the menus.
 15. PRESENT, PRINT SET, THE THUMBNAIL: as arranged, nothing of Edit.
 16. A PHONE: the figures in reading order; a figure's menu moves it earlier or later.
 17. KEPT: the set over a reload.

The harness never waits without a bound (V123).
"""
import asyncio, base64, datetime, hashlib, io, json, math, pathlib, re, shutil, subprocess, sys, tempfile, traceback, zipfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from bim_phase133_site_context_browser_tests import Checks, Stalled, within   # noqa: E402
import climate_fixture as CFX   # noqa: E402
import ladybug_fixture as F   # noqa: E402
import ladybug_reference as R   # noqa: E402
from playwright.async_api import async_playwright   # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT / 'canvas_v10.html'
KEPT = ROOT / 'Phase' / 'canvas_v10.html.bak_phase172b_pre'
RUNTIME = HTML.parent / 'runtime' if (HTML.parent / 'runtime').is_dir() else ROOT / 'runtime'
PAGES = 'https://bradleypham1906.github.io/BIM-Personal/runtime/'
CK = Checks()
YEAR = 2017
ZIPB = F.station_zip(YEAR)
EPWT = F.epw_text(YEAR)
P0 = (1408 + 12) / 12.0
BANDS = [-40, -27, -13, 0, 9, 26, 32, 38, 46]
CONDS = ['sun_wind', 'shade_wind', 'sun_still', 'shade_still']
FIGS_CLIMATE = ['clim.temp', 'clim.wind', 'clim.heat', 'clim.sun', 'clim.dd', 'clim.solar', 'clim.psy', 'risk.quake', 'risk.air']
FIGS_LB = ['lb.utci', 'lb.psych', 'lb.wind', 'lb.dd']
FIGS_ZONING = ['zn.table', 'zn.secA', 'zn.secB', 'zn.rules', 'zn.plan', 'zn.plates', 'zn.yield']
TMP = []   # the run's own folders (the wheels unpacked, the kept build), taken away at its end


def tmpdir(prefix):
    d = pathlib.Path(tempfile.mkdtemp(prefix=prefix))
    TMP.append(d)
    return d


# ---------------- native: the same adapter on the same wheels ----------------
def native():
    """the committed wheels unpacked, the adapter imported, the fixture's ZIP and EPW run; the answers"""
    d = tmpdir('bim172b_')
    for w in sorted((RUNTIME / 'wheels').glob('*.whl')):
        with zipfile.ZipFile(str(w)) as z:
            z.extractall(str(d / 'site'))
    sys.path[:0] = [str(d / 'site'), str(ROOT / 'src' / 'py')]
    import bim_ladybug as B   # noqa: E402
    (d / 'fx.zip').write_bytes(ZIPB)
    out = {'open': B.open_file(str(d / 'fx.zip'), 'fx.zip')}
    out['utci'] = B.utci(limits={'ta': [-50, 50], 'dtr': [-30, 70], 'va': [0.5, 17], 'pa': 50}, still=0.5)
    out['psych'] = B.psych(clo=[0.5, 1.0], met=[1.1, 1.1], strategy_par=[12, 3, 1, 12.8, 50, 8], ppd=10, still=0.1)
    out['psych20'] = B.psych(clo=[0.5, 1.0], met=[1.1, 1.1], strategy_par=[12, 3, 1, 12.8, 50, 8], ppd=20, still=0.1)
    out['wind'] = B.windrose(16, [0.5, 2, 4, 6, 8])
    out['dd'] = B.design_days()
    v = B.versions()
    out['versions'] = json.loads(v) if isinstance(v, str) else v
    return out


def unrle(t):
    """the app's runs of categories ('5:12,4:3') back to one an hour"""
    out = []
    for part in (t or '').split(','):
        if part:
            k, n = part.split(':')
            out += [int(k)] * int(n)
    return out


def near(a, b, t=1e-6):
    return a is not None and b is not None and abs(a - b) <= t


async def run():
    ck = CK
    print('-- native: the adapter on the committed wheels, in CPython %s' % sys.version.split()[0])
    NAT = native()
    E = R.read_epw(EPWT)
    DDY = R.read_ddy(F.ddy_text())
    col = E['cols']
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1600, 'height': 1000})
        ST = {'om': [], 'rt': [], 'tamper': None, 'rtmode': None}

        async def clim_route(route):
            u = route.request.url
            if 'direct_normal_irradiance' in u:
                ST['om'].append(u)
                if ST.get('ommode') == 'abort':
                    await route.abort('internetdisconnected')
                    return
                y = int(u.split('start_date=')[1][:4])
                await route.fulfill(status=200, body=json.dumps(F.openmeteo(y)), headers={'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'})
                return
            await CFX.route_handler(ST)(route)

        async def rt_route(route):
            u = route.request.url
            rel = u[len(PAGES):].split('?')[0]
            ST['rt'].append(rel)
            if ST.get('rtmode') == 'abort':
                await route.abort('internetdisconnected')
                return
            p = RUNTIME / rel
            if not p.is_file():
                await route.fulfill(status=404, body='not found', headers={'Access-Control-Allow-Origin': '*'})
                return
            body = p.read_bytes()
            if ST.get('tamper') and rel.endswith(ST['tamper']):
                body = body[:-1] + bytes([body[-1] ^ 1])
            ct = 'application/wasm' if rel.endswith('.wasm') else ('application/javascript' if rel.endswith('.js') else 'application/octet-stream')
            await route.fulfill(status=200, body=body, headers={'Access-Control-Allow-Origin': '*', 'Content-Type': ct})

        for h in ('https://archive-api.open-meteo.com/**', 'https://air-quality-api.open-meteo.com/**', 'https://earthquake.usgs.gov/**'):
            await ctx.route(h, clim_route)
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

        async def toast(pg=None):
            return await safe("()=>{var t=document.getElementById('a3d-toast');return t?t.textContent:'';}", pg=pg) or ''

        async def set_site(lat, lon, tz='-5', pg=None):
            await safe("()=>{var s=document.getElementById('a3d-shell');if(s&&s.getAttribute('data-tab')==='analyze')document.querySelector('#a3d-rail [data-tab=browser]').click();}", pg=pg)
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dSetPropTab('site');window.__a3dRefreshProps();}", pg=pg)
            for k, v in (('sunlat', lat), ('sunlon', lon), ('suntz', tz)):
                await safe("""(a)=>{var L=document.querySelectorAll('#a3d-propsbody input'),e=null,i;for(i=0;i<L.length;i++)if(L[i].getAttribute('data-propmodel')===a[0])e=L[i];
                  if(!e)return false;e.value=a[1];e.dispatchEvent(new Event('change',{bubbles:true}));return true;}""", [k, v], pg=pg)
                await (pg or page).wait_for_timeout(80)

        async def lot_zoning(pg=None):
            await safe("""(a)=>{var o=window.__a3dState().objs.filter(function(x){return x.t!=='property'&&x.id!=='LOT'&&!x.envelope&&x.t!=='box';});
              o.push({id:'LOT',t:'sketch',name:'Lot',col:'#5ec4b8',pos:[0,0,0],pts:a,y:0,closed:true,layer:'layer-0'});
              window.__a3dTestSetObjs(o);window.__a3dPropertyFromSketch('LOT');}""", [[0, 0], [30, 0], [30, 40], [0, 40]], pg=pg)
            for k, v in (('district', 'R7-2'), ('far', '4'), ('maxH', '30'), ('front', '3'), ('side', '2'), ('rear', '5'), ('baseH', '15'), ('step', '3'), ('cover', '70'), ('source', 'Test code (2026)')):
                await safe("(a)=>window.__a3dZnSet(a[0],a[1])", [k, v], pg=pg)

        async def st(pg=None):
            return await safe("()=>window.__a3dBrdState()", pg=pg) or {}

        async def rec(bid, pg=None):
            return await safe("(i)=>window.__a3dBrdRecord(i)", bid, pg=pg) or {}

        async def working(pg=None):
            return await safe("()=>window.__a3dBrdWorking()", pg=pg) or []

        def fk(L, k):
            return ([f for f in L if f['k'] == k] or [None])[0]

        async def drag(sel, dx, dy, pg=None, steps=8, during=None):
            pg = pg or page
            h = await pg.query_selector(sel)
            await h.scroll_into_view_if_needed()
            bb = await h.bounding_box()
            x0, y0 = bb['x'] + bb['width'] / 2, bb['y'] + bb['height'] / 2
            await pg.mouse.move(x0, y0)
            await pg.mouse.down()
            await pg.mouse.move(x0 + dx / 3, y0 + dy / 3, steps=3)
            await pg.mouse.move(x0 + dx, y0 + dy, steps=steps)
            got = await safe(during, pg=pg) if during else None
            await pg.mouse.up()
            await pg.wait_for_timeout(300)
            return got

        async def snaps(point, grid, ortho, pg=None):
            for k, v in (('point', point), ('grid', grid), ('ortho', ortho)):
                on = await safe("(k)=>{var b=document.querySelector('[data-brdsnap=\"'+k+'\"]');return b?b.getAttribute('aria-pressed')==='true':null;}", k, pg=pg)
                if on is not None and on != v:
                    await safe("(k)=>document.querySelector('[data-brdsnap=\"'+k+'\"]').click()", k, pg=pg)

        try:
            await within(page.goto('file://' + str(HTML)), 'goto')
            await page.wait_for_timeout(2300)
            await safe("()=>{window.__a3dEnter();window.__a3dTestSetObjs([]);}")

            # ---------------------------------------------------------------------------------
            print("\n-- 1. The records")
            mk = await safe("()=>window.__acad3dV172b") or ''
            ck(all(w in mk for w in ('runtime', 'sha256', 'utci4', 'pmv2clo', 'strategies5', 'figids', 'arranged', 'edit', 'snaps', 'catalogue', 'custom', 'registry', 'stdstamp', 'analyze')),
               "the V172b marker (%s)" % mk[:80])
            ver = (await safe("()=>window.__a3dVersion()") or {}).get('v', '')
            ck(re.match(r'^V\d+', ver) and int(re.match(r'^V(\d+)', ver).group(1)) >= 172, "the app says V172 or later (%s)" % ver)
            man = json.loads((RUNTIME / 'MANIFEST.json').read_text(encoding='utf-8'))
            badm = [f['path'] for f in man['files'] if hashlib.sha256((RUNTIME / f['path']).read_bytes()).hexdigest() != f['sha256'] or (RUNTIME / f['path']).stat().st_size != f['bytes']]
            ck(len(man['files']) == 11 and not badm, "the runtime's 11 files are what MANIFEST.json pins, by size and SHA-256 (%s)" % badm)
            cr = subprocess.run([sys.executable, str(ROOT / 'tools' / 'check_runtime.py')], capture_output=True, text=True)
            ck(cr.returncode == 0, "tools/check_runtime.py agrees (%s)" % cr.stdout.strip()[-120:])
            S0 = await safe("()=>window.__a3dLbState()") or {}
            W0 = {w['f']: w['h'] for w in S0.get('wheels', [])}
            MW = {pathlib.Path(f['path']).name: f['sha256'] for f in man['files'] if f['path'].startswith('wheels/')}
            ck(W0 == MW and len(W0) == 4, "the app pins the same four wheels by SHA-256 (%s)" % sorted(W0))
            ck(S0.get('base') == PAGES and S0.get('dir') == 'pyodide/0.29.5/' and S0.get('st') in (None, 'idle', '') and not ST['rt'],
               "from file:// it asks the Pages site; Pyodide 0.29.5; nothing loaded, nothing asked, until a run (%s, %d asked)" % ({k: S0.get(k) for k in ('base', 'dir', 'st')}, len(ST['rt'])))
            REC = {r['id']: r for r in await safe("()=>window.__a3dStdRecords()") or []}
            vals = {}
            for t, n in (('utci', 'bands'), ('utci', 'va_lo'), ('utci', 'va_hi'), ('utci', 'ta_lo'), ('utci', 'ta_hi'), ('utci', 'dtr_lo'), ('utci', 'dtr_hi'), ('utci', 'pa_hi'),
                         ('ashrae.55', 'ppd'), ('ashrae.55', 'still'), ('app.comfort', 'clo'), ('app.comfort', 'met'), ('ashrae.dd', 'heating'), ('ashrae.dd', 'cooling')):
                vals[t + '|' + n] = await safe("(a)=>window.__a3dStd(a[0],a[1])", [t, n])
            ck(vals['utci|bands'] == BANDS and vals['utci|va_lo'] == 0.5 and vals['utci|va_hi'] == 17 and vals['utci|ta_lo'] == -50 and vals['utci|ta_hi'] == 50 and
               vals['utci|dtr_lo'] == -30 and vals['utci|dtr_hi'] == 70 and vals['utci|pa_hi'] == 50, "UTCI's scale and range in the registry, as UTCI_a002's ReadMe and poster give them")
            ck(vals['ashrae.55|ppd'] == 10 and vals['ashrae.55|still'] == 0.1 and (REC.get('ashrae.55') or {}).get('eds', [{}])[0].get('src', {}).get('lv') == 'S',
               "ASHRAE 55-2023's PPD 10% and still air 0.1 m/s, at level S (the standard is sold)")
            ck(vals['app.comfort|clo'] == [0.5, 1] and vals['app.comfort|met'] == 1.1 and vals['ashrae.dd|heating'] == [99.6, 99] and vals['ashrae.dd|cooling'] == [0.4, 1, 2],
               "the comfort assumptions (0.5 and 1.0 clo at 1.1 met) and the design conditions' percentiles")
            pr = await safe("()=>window.__a3dLbParams('psych')") or {}
            ck(pr.get('clo') == [0.5, 1] and pr.get('met') == [1.1, 1.1] and pr.get('strategy_par') == [12, 3, 1, 12.8, 50, 8] and pr.get('ppd') == 10 and pr.get('still') == 0.1,
               "the psychrometric chart's parameters come from the registry: Ladybug's defaults (%s)" % pr)
            pu = await safe("()=>window.__a3dLbParams('utci')") or {}
            ck(pu.get('still') == 0.5 and pu.get('limits') == {'ta': [-50, 50], 'dtr': [-30, 70], 'va': [0.5, 17], 'pa': 50} and pu.get('ground_ref') == 0.25, "and UTCI's (%s)" % pu)

            # ---------------------------------------------------------------------------------
            print("\n-- 2. The runtime")
            ST['tamper'] = 'ladybug_comfort-0.19.13-py3-none-any.whl'
            s = await slow("()=>window.__a3dLbStart()")
            ck(isinstance(s, dict) and s.get('error') and 'SHA-256' in s.get('error', '') and 'ladybug_comfort' in s.get('error', ''),
               "a wheel that is not what the app pins is refused, by name (%s)" % (s or {}).get('error', '')[:120])
            S1 = await safe("()=>window.__a3dLbState()") or {}
            ck(S1.get('st') == 'failed' and 'SHA-256' in (S1.get('words') or ''), "and the state says why (%s)" % (S1.get('words') or '')[:100])
            ST['tamper'] = None
            ST['rtmode'] = 'abort'
            await safe("()=>window.__a3dLbStop()")
            s = await slow("()=>window.__a3dLbStart()")
            ck(isinstance(s, dict) and s.get('error'), "no network: it does not start, and says so (%s)" % (s or {}).get('error', '')[:120])
            ST['rtmode'] = None
            await safe("()=>window.__a3dLbStop()")
            n_rt = len(ST['rt'])
            s = await slow("()=>window.__a3dLbStart()")
            ck(isinstance(s, dict) and s.get('st') == 'ready' and s.get('pyodide') == '0.29.5' and (s.get('versions') or {}).get('ladybug-core') == '0.44.63' and
               (s.get('versions') or {}).get('ladybug-comfort') == '0.19.13', "then ready: Pyodide 0.29.5, ladybug-core 0.44.63, ladybug-comfort 0.19.13 (%s)" % {k: (s or {}).get(k) for k in ('st', 'pyodide', 'versions')})
            got = sorted(set(ST['rt'][n_rt:]))
            ck(all(x in got for x in ('pyodide/0.29.5/pyodide.js', 'pyodide/0.29.5/pyodide.asm.wasm', 'pyodide/0.29.5/python_stdlib.zip')) and
               len([x for x in got if x.startswith('wheels/')]) == 4, "from the site's runtime/: Pyodide's files and the four wheels (%s)" % got)
            ck(NAT['versions'].get('ladybug-core') == '0.44.63' and NAT['versions'].get('ladybug-comfort') == '0.19.13', "the native run is the same Ladybug (%s)" % NAT['versions'])

            # ---------------------------------------------------------------------------------
            print("\n-- 3. A weather file")
            await set_site('40.0', '-75.0')
            u0 = await safe("()=>window.__a3dUndoDepth()")
            bad = await slow("(b)=>window.__a3dLbOpenB64('notes.epw',b)", base64.b64encode(b'Not a weather file\n').decode())
            ck(isinstance(bad, dict) and 'not an EPW' in (bad.get('error') or ''), "not an EPW: refused and said (%s)" % (bad or {}).get('error'))
            S = await slow("(b)=>window.__a3dLbOpenB64('fixture.zip',b)", base64.b64encode(ZIPB).decode())
            ck(isinstance(S, dict) and S.get('city') == F.CITY and S.get('station') == F.WMO and S.get('lat') == F.LAT and S.get('lon') == F.LON and S.get('tz') == F.TZ and
               S.get('hours') == 8760 and S.get('ddy') is True and S.get('kind') == 'file', "the station's ZIP: its EPW's place and 8760 hours, and its DDY (%s)" % {k: (S or {}).get(k) for k in ('city', 'station', 'hours', 'ddy')})
            ck(E['n'] == 8760 and E['city'] == F.CITY and E['lat'] == F.LAT, "the reference reads the same EPW: 8760 hours")
            u1 = await safe("()=>window.__a3dUndoDepth()")
            S2 = await slow("(b)=>window.__a3dLbOpenB64('fixture.zip',b)", base64.b64encode(ZIPB).decode())
            ck(u1 == u0 + 1 and await safe("()=>window.__a3dUndoDepth()") == u1 and S2.get('key') == S.get('key'), "the source is one undo step; the same file again changes nothing (%d, %d)" % (u0, u1))
            kept = (await safe("()=>window.__a3dLbData()") or {}).get('src') or {}
            ck(kept.get('name') == 'fixture.zip' and kept.get('kind') == 'file' and 'hourly' not in json.dumps(kept), "the project keeps where the hours came from, not the hours (%s)" % sorted(kept))

            # ---------------------------------------------------------------------------------
            print("\n-- 4. UTCI")
            r = await slow("()=>window.__a3dLbRun('utci')")
            U = (r or {}).get('r') or {}
            ck(U.get('conditions') and sorted(U['conditions']) == sorted(CONDS), "four conditions: sun or shade, wind or still air (%s)" % sorted(U.get('conditions') or {}))
            db_i, rh_i, ws_i = R.instant(col['db']), R.instant(col['rh']), R.instant(col['ws'])   # as Ladybug holds the file's hours at an instant
            for cnd, wind in (('shade_wind', True), ('shade_still', False)):
                cnt = [0] * 10
                out = 0
                for i in range(8760):
                    ta, rh = col['db'][i], col['rh'][i]
                    va = col['ws'][i] if wind else 0.5
                    v = R.utci(ta, ta, va, rh)
                    cnt[R.utci_class(v, BANDS)] += 1
                    pa = R.es(ta) * rh / 100.0
                    if ta < -50 or ta > 50 or va < 0.5 or va > 17 or pa > 50:
                        out += 1
                a = U['conditions'][cnd]
                hrs = unrle(a.get('classes'))
                ref_h = [R.utci_class(R.utci(db_i[i], db_i[i], ws_i[i] if wind else 0.5, rh_i[i]), BANDS) for i in range(8760)]
                miss = sum(1 for x, y in zip(hrs, ref_h) if x != y)
                ck(len(hrs) == 8760 and miss <= 2 and a['counts'] == cnt and a['outside'] == out,
                   "%s: every hour's category by the official polynomial, as the app has it (%d of 8760 differ; %s); %d hours outside its range" % (cnd, miss, a['counts'], out))
            for cnd in CONDS:
                a, b = U['conditions'][cnd], NAT['utci']['conditions'][cnd]
                ck(a['counts'] == b['counts'] and a['monthly'] == b['monthly'] and a['classes'] == b['classes'] and a['outside'] == b['outside'],
                   "%s: the browser's every hour as native CPython's (%s%% no stress)" % (cnd, a['comfort']))
            ck(U.get('still') == 0.5 and U.get('limits') == {'ta': [-50, 50], 'dtr': [-30, 70], 'va': [0.5, 17], 'pa': 50}, "it used the registry's still air and range (%s)" % U.get('limits'))
            rg = await safe("()=>window.__a3dLbUtciRange()") or []
            ck(rg == ['below −40 °C', '−40 to −27 °C', '−27 to −13 °C', '−13 to 0 °C', '0 to 9 °C', '9 to 26 °C',
                      '26 to 32 °C', '32 to 38 °C', '38 to 46 °C', 'above 46 °C'], "the figure's ranges from the registry's scale (%s)" % rg[:3])

            # ---------------------------------------------------------------------------------
            print("\n-- 5. The psychrometric chart")
            r = await slow("()=>window.__a3dLbRun('psych')")
            P = (r or {}).get('r') or {}
            N = NAT['psych']
            ck(P.get('names') == ['Comfort', 'Evaporative Cooling', 'Mass + Night Vent', 'Occupant Use of Fans', 'Capture Internal Heat', 'Passive Solar Heating'],
               "the merged comfort zone, then Ladybug's five strategies (%s)" % P.get('names'))
            ck(P.get('pct') == N['pct'] and P.get('total') == N['total'] and P.get('polygons') == N['polygons'], "each zone's share and shape as native CPython's (%s, %s)" % (P.get('pct'), P.get('total')))
            edge = R.pmv_from_ppd(10)
            inside, close = 0, 0
            for i in range(8760):
                ta, rh = col['db'][i], col['rh'][i]
                m = min(abs(R.pmv_ppd(ta, ta, 0.1, rh, 1.1, c)[0]) for c in (0.5, 1.0))
                if m <= edge:
                    inside += 1
                if abs(m - edge) < 0.06:
                    close += 1
            ref = 100.0 * inside / 8760
            ck(abs(ref - P['pct'][0]) <= 100.0 * close / 8760 + 0.15, "comfort against Fanger's PMV for 0.5 and 1.0 clo, hour by hour: %.1f%% here, %.1f%% in the app, %d hours at the edge" % (ref, P['pct'][0], close))
            ck(sum(P['chart']['mesh_hours']) == 8760 and P.get('hours') == 8760, "the chart holds every hour once")
            ck(P.get('ppd') == 10 and P.get('still') == 0.1 and P.get('notes') == [], "it used the registry's PPD and still air")
            await safe("()=>window.__a3dStdOverride('ashrae.55','ppd',20,'a wider zone, for the suite')")
            r = await slow("()=>window.__a3dLbRun('psych')")
            ck(((r or {}).get('r') or {}).get('pct', [0])[0] == NAT['psych20']['pct'][0] and NAT['psych20']['pct'][0] > P['pct'][0],
               "PPD 20%% set for the project widens the zone, as natively (%s against %s)" % (((r or {}).get('r') or {}).get('pct', [0])[0], NAT['psych20']['pct'][0]))
            await safe("()=>window.__a3dStdClear('ashrae.55','ppd')")
            await safe("()=>window.__a3dStdOverride('app.comfort','fan',40,'out of range, for the suite')")
            r = await slow("()=>window.__a3dLbRun('psych')")
            ck(((r or {}).get('r') or {}).get('strategy_par', [0, 0, 0])[2] == 1.0 and 'fan air speed' in ' '.join(((r or {}).get('r') or {}).get('notes', [])),
               "a fan speed of 40 m/s goes back to Ladybug's 1.0, said (%s)" % ((r or {}).get('r') or {}).get('notes'))
            await safe("()=>window.__a3dStdClear('app.comfort','fan')")
            r = await slow("()=>window.__a3dLbRun('psych')")

            # ---------------------------------------------------------------------------------
            print("\n-- 6. Wind")
            r = await slow("()=>window.__a3dLbRun('wind')")
            Wd = (r or {}).get('r') or {}
            S_ref, calm = R.wind_rose(col['wd'], col['ws'], [0.5, 2, 4, 6, 8])
            ck(Wd.get('sectors') == S_ref and Wd.get('calm') == calm, "16 sectors centred on the compass points, in the app's speed bands, and calm as a speed of 0, as the EPW has them (%d calm)" % calm)
            ck(Wd.get('sectors') == NAT['wind']['sectors'] and Wd.get('bins') == [0.5, 2, 4, 6, 8], "and as native CPython's")

            # ---------------------------------------------------------------------------------
            print("\n-- 7. Design days")
            r = await slow("()=>window.__a3dLbRun('dd')")
            D = (r or {}).get('r') or {}
            want = {'heating': DDY[0], 'heating99': DDY[1], 'cooling': DDY[2], 'cooling1': DDY[3], 'cooling2': DDY[4]}
            badd = [k for k, d in want.items() if not D.get(k) or D[k]['how'] != 'ddy' or D[k]['db'] != d['db'] or D[k]['range'] != d['range'] or D[k]['hum'] != d['hum'] or
                    D[k]['month'] != d['month'] or D[k]['day'] != d['day'] or abs(max(D[k]['hourly']) - d['db']) > 0.05 or abs(min(D[k]['hourly']) - (d['db'] - d['range'])) > 0.05]
            ck(not badd, "the DDY's five design days: dry bulb, range, humidity, date, and a day's hours from the range down (%s)" % badd)
            ck(D == NAT['dd'], "as native CPython reads them")

            # ---------------------------------------------------------------------------------
            print("\n-- 8. Open-Meteo")
            u_before = await safe("()=>window.__a3dUndoDepth()")
            S3 = await slow("()=>window.__a3dLbFetchYear()")
            yr = datetime.date.today().year - 1
            om = ST['om'][-1] if ST['om'] else ''
            ck(isinstance(S3, dict) and S3.get('kind') == 'openmeteo' and 'start_date=%d-01-01' % yr in om and 'end_date=%d-01-01' % (yr + 1) in om and
               'timezone=Etc%2FGMT%2B5' in om and all(v in om for v in F.OM_VARS) and 'wind_speed_unit=ms' in om,
               "the last full year, its ten variables, in the site's standard time Etc/GMT+5 (%s)" % om[:200])
            n = 8784 if (yr % 4 == 0 and yr % 100 != 0) or yr % 400 == 0 else 8760
            ck(S3.get('hours') == n and S3.get('filled') == len([g for g in F.GAPS if 0 <= g < n]) and S3.get('zone') == 'Etc/GMT+5' and S3.get('year') == yr,
               "its %d hours, the gaps filled and counted (%s)" % (n, {k: S3.get(k) for k in ('hours', 'filled', 'zone')}))
            ru = await slow("()=>window.__a3dLbRun('utci')")
            Uo = (((ru or {}).get('r') or {}).get('conditions') or {}).get('shade_wind') or {}
            H = R.om_hours(F.openmeteo(yr), n)
            cnt = [0] * 10
            for i in range(n):
                cnt[R.utci_class(R.utci(H['db'][i], H['db'][i], H['ws'][i], H['rh'][i]), BANDS)] += 1
            ho = unrle(Uo.get('classes'))
            ref_o = [R.utci_class(R.utci(H['db'][i], H['db'][i], H['ws'][i], H['rh'][i]), BANDS) for i in range(n)]
            mo = sum(1 for x, y in zip(ho, ref_o) if x != y)
            ck(len(ho) == n and mo <= 2, "UTCI from those hours, hour by hour: each hour's own temperature, humidity and wind, as Ladybug holds a file's (%d differ)" % mo)
            ck(await safe("()=>window.__a3dLbOmZone(5.5)") is None and await safe("()=>window.__a3dLbOmZone(-5)") == 'Etc/GMT+5' and await safe("()=>window.__a3dLbOmZone(0)") == 'GMT',
               "a half-hour zone has no Etc zone: its hours come in UTC, said")
            ST['ommode'] = 'abort'
            k_before = ((await safe("()=>window.__a3dLbData()") or {}).get('src') or {}).get('key')
            e3 = await slow("()=>window.__a3dLbFetchYear()")
            ST['ommode'] = None
            ck(isinstance(e3, dict) and 'could not be reached' in (e3.get('error') or '') and ((await safe("()=>window.__a3dLbData()") or {}).get('src') or {}).get('key') == k_before,
               "Open-Meteo down: said, and the weather the project names kept (%s)" % (e3 or {}).get('error', '')[:80])
            # back to the file, for what follows
            await slow("(b)=>window.__a3dLbOpenB64('fixture.zip',b)", base64.b64encode(ZIPB).decode())
            for k in ('utci', 'psych', 'wind', 'dd'):
                await slow("(k)=>window.__a3dLbRun(k)", k)

            # ---------------------------------------------------------------------------------
            print("\n-- 9. Kept and out of date")
            L = await safe("()=>window.__a3dLbData()") or {}
            ck(all(L.get(k) and L[k].get('std') and L[k].get('v', {}).get('pyodide') == '0.29.5' and L[k].get('src') == L['src']['key'] for k in ('utci', 'psych', 'wind', 'dd')),
               "each result keeps its weather, the versions that made it and the standards it used")
            ck(len(json.dumps(L)) < 200000, "and the project stays small: %d bytes for the four" % len(json.dumps(L)))
            await safe("()=>window.__a3dStdOverride('utci','va_lo',0.6,'for the suite')")
            ch = {k: [c['t'] for c in await safe("(k)=>window.__a3dLbStdChanged(k)", k) or []] for k in ('utci', 'psych', 'wind', 'dd')}
            ck(ch == {'utci': ['utci'], 'psych': [], 'wind': [], 'dd': []}, "a standard changed marks only the result that used it (%s)" % ch)
            states = {c['id']: c['state'] for c in await safe("()=>window.__a3dLbCards()") or []}
            ck(states.get('lbutci') == 'stale' and states.get('lbpsych') == 'on', "its row says out of date (%s)" % states)
            r6 = await slow("()=>window.__a3dLbRun('utci')")
            U6 = ((r6 or {}).get('r') or {})
            h6 = unrle(((U6.get('conditions') or {}).get('shade_still') or {}).get('classes'))
            ref6 = [R.utci_class(R.utci(db_i[i], db_i[i], 0.6, rh_i[i]), BANDS) for i in range(8760)]
            ck(U6.get('still') == 0.6 and sum(1 for x, y in zip(h6, ref6) if x != y) <= 2 and h6 != unrle(U['conditions']['shade_still']['classes']),
               "run again, still air is the project's 0.6 m/s: in the shade and still air, every hour as the polynomial gives it at 0.6")
            await safe("()=>window.__a3dStdClear('utci','va_lo')")
            await slow("()=>window.__a3dLbRun('utci')")

            # ---------------------------------------------------------------------------------
            print("\n-- 10. Analyze")
            await safe("()=>window.__a3dAwEnter()")
            await page.wait_for_timeout(300)
            rows = await safe("()=>[].map.call(document.querySelectorAll('[data-sacat=\"climate\"] [data-anzcard]'),function(r){return r.getAttribute('data-anzcard');})") or []
            ck(rows[-5:] == ['lbweather', 'lbutci', 'lbpsych', 'lbwind', 'lbdd'], "Climate's rows: Ladybug's five after the sun's (%s)" % rows)
            await safe("()=>window.__a3dAwPick('card','lbutci')")
            await page.wait_for_timeout(200)
            pt = await safe("()=>{var p=document.querySelector('[data-awpanel=\"card:lbutci\"]');return p?p.innerText:'';}") or ''
            ck('In the sun, in the wind' in pt and 'In the shade, in still air' in pt and 'UTCI_a002' in pt and 'Run again' in pt and 'Add to a board' in pt,
               "UTCI's panel: the four conditions, the standard it used, Run again, Show, Add to a board")
            cards = {c['id']: c for c in await safe("()=>window.__a3dLbCards()") or []}
            ck(cards.get('lbpsych', {}).get('status', '').startswith('%d%% of hours comfortable indoors' % round(P['pct'][0])) and
               cards.get('lbdd', {}).get('status', '').startswith('Heating −11.2 °C'), "each row's status says what it found (%s)" % cards.get('lbdd', {}).get('status'))
            ck(await safe("()=>window.__a3dLbAct('show:psych')") and (await st()).get('kind') == 'climate', "Show on the board opens the climate board")
            n_sets = len((await safe("()=>window.__a3dPresRecord()") or {}).get('boards', []))
            await safe("()=>window.__a3dLbAddTo('wind','new')")
            await page.wait_for_timeout(500)
            s = await st()
            ck(s.get('kind') == 'custom' and [f['f'] for f in (s.get('rec') or {}).get('figs', [])] == ['lb.wind'] and s.get('h1') == 'Wind rose',
               "Add to a board, A new board: a board of its own with the figure (%s)" % s.get('h1'))
            await safe("()=>window.__a3dBrdDlgClose()")
            await safe("()=>window.__a3dBrdEdit(false)")

            # ---------------------------------------------------------------------------------
            print("\n-- 11. The boards' figures")
            r = await safe("()=>Promise.resolve(window.__a3dClimFetch())")
            await page.wait_for_timeout(500)
            await lot_zoning()
            cap = await safe("()=>window.__a3dBrdCapture('climate')") or {}
            ck(cap.get('order') == ['clim.kpis'] + FIGS_CLIMATE + FIGS_LB, "the climate board's indicators and figures, each named (%s)" % cap.get('order'))
            capz = await safe("()=>window.__a3dBrdCapture('zoning')") or {}
            ck(capz.get('order') == ['zn.kpis'] + FIGS_ZONING, "the zoning board's (%s)" % capz.get('order'))
            cat = await safe("()=>window.__a3dBrdCat()") or []
            ck(len(cat) == 33 and [c['f'] for c in cat if c['kind'] == 'climate' and not c['kpis']] == ['clim.temp', 'clim.wind', 'clim.heat', 'clim.sun', 'clim.dd', 'clim.solar', 'clim.psy'] + FIGS_LB + ['risk.quake', 'risk.air'],
               "the catalogue: 33, by group (%d)" % len(cat))
            has = {c['f']: c['has'] for c in cat}
            ck(all(has[f] for f in FIGS_CLIMATE + FIGS_LB + FIGS_ZONING + ['clim.kpis', 'zn.kpis', 'text']) and not has['acc.walk'] and not has['ppl.compare'],
               "what has data can be added; access and people, with none yet, cannot")
            # drawn as before: the kept build, the same data, its HTML against this one's with the names set aside
            c2 = await browser.new_context(viewport={'width': 1600, 'height': 1000})   # its own storage: a fresh project in each build
            for h in ('https://archive-api.open-meteo.com/**', 'https://air-quality-api.open-meteo.com/**', 'https://earthquake.usgs.gov/**'):
                await c2.route(h, clim_route)
            p2 = await c2.new_page()
            kept_html = tmpdir('bim172b_kept_') / 'kept.html'   # a file:// page is read by its name's extension
            kept_html.write_bytes(KEPT.read_bytes())
            await within(p2.goto('file://' + str(kept_html)), 'goto kept')
            await p2.wait_for_timeout(2300)
            await safe("()=>{window.__a3dEnter();window.__a3dTestSetObjs([]);}", pg=p2)
            await set_site('40.0', '-75.0', pg=p2)
            await safe("()=>Promise.resolve(window.__a3dClimFetch())", pg=p2)
            await p2.wait_for_timeout(500)
            await lot_zoning(pg=p2)
            c3 = await browser.new_context(viewport={'width': 1600, 'height': 1000})
            for h in ('https://archive-api.open-meteo.com/**', 'https://air-quality-api.open-meteo.com/**', 'https://earthquake.usgs.gov/**'):
                await c3.route(h, clim_route)
            p3 = await c3.new_page()
            await within(p3.goto('file://' + str(HTML)), 'goto new')
            await p3.wait_for_timeout(2300)
            await safe("()=>{window.__a3dEnter();window.__a3dTestSetObjs([]);}", pg=p3)
            await set_site('40.0', '-75.0', pg=p3)
            await safe("()=>Promise.resolve(window.__a3dClimFetch())", pg=p3)
            await p3.wait_for_timeout(500)
            await lot_zoning(pg=p3)
            same = []
            for k in ('climate', 'zoning'):
                await safe("(k)=>window.__a3dClbOpen(k)", k, pg=p2)
                await safe("(k)=>window.__a3dClbOpen(k)", k, pg=p3)
                a = await safe("()=>window.__a3dClbHtml()", pg=p2) or ''
                b = await safe("()=>window.__a3dClbHtml()", pg=p3) or ''
                b2 = re.sub(r' data-figid="[^"]*"', '', b)
                same.append((k, a == b2 and len(a) > 5000, len(a), len(b2)))
            ck(all(x[1] for x in same), "a board without a list is drawn exactly as the kept build draws it, the figures' names aside (%s)" % same)
            await c2.close()
            await c3.close()

            # ---------------------------------------------------------------------------------
            print("\n-- 12. Edit")
            await safe("()=>window.__a3dBoardShow('climate')")
            await page.wait_for_timeout(400)
            s = await st()
            ck(s.get('editBtn') and not s.get('arranged') and s.get('rec') == {'id': 'board-climate', 'kind': 'climate'}, "the board's bar: Edit; the board as ever, no list (%s)" % s.get('rec'))
            u0 = await safe("()=>window.__a3dUndoDepth()")
            await page.click('.a3d-clb:not(.a3d-ssboard) [data-brd="edit"]')
            await page.wait_for_timeout(500)
            s = await st()
            ck(s.get('edit') and s.get('arranged') and s.get('editBar') and len(s.get('figs', [])) == 13 and s.get('rec') == {'id': 'board-climate', 'kind': 'climate'} and
               await safe("()=>window.__a3dUndoDepth()") == u0, "Edit: the figures arranged as laid out, 13; nothing kept, no undo step yet")
            z = s.get('z') or 1
            # the main view is narrower than the board's 1408 px here: the arrangement zoomed to it, exactly, and nothing wider
            zc = await safe("""()=>{var A=document.querySelector('.a3d-clb:not(.a3d-ssboard) .a3d-clb-arr'),p=A&&A.parentNode,cs;if(!p)return null;cs=getComputedStyle(p);
              return {w:p.clientWidth-(parseFloat(cs.paddingLeft)||0)-(parseFloat(cs.paddingRight)||0),aw:A.getBoundingClientRect().width};}""") or {}
            zw = zc.get('w') or 0
            ck(zw and 0.4 < z < 1 and abs(z - min(1, zw / 1408.0)) < 1e-4 and abs(float(s.get('zoomed') or 0) - z) < 1e-4 and abs((zc.get('aw') or 0) - zw) <= 1,
               "laid out 1408 px across and zoomed to the main view: %.3f, %.0f px across of its %.0f" % (z, zc.get('aw') or 0, zw))
            # the arrangement where the board's own grid puts them, at a wide view
            await page.set_viewport_size({'width': 2400, 'height': 1300})
            await page.wait_for_timeout(700)
            await safe("()=>window.__a3dBrdEdit(false)")
            flow = await safe("""()=>{var g=document.querySelector('.a3d-clb:not(.a3d-ssboard) .a3d-clb-grid'),gr=g.getBoundingClientRect();
              return [].map.call(g.querySelectorAll('[data-figid]'),function(c){var r=c.getBoundingClientRect();return [r.left-gr.left,r.top-gr.top,r.width,r.height];});}""") or []
            await safe("()=>window.__a3dBrdEdit(true)")
            await page.wait_for_timeout(500)
            s = await st()
            worst = max([max(abs(a[0] - f['l']), abs(a[1] - f['t']), abs(a[2] - f['w']), abs(a[3] - f['h'])) for a, f in zip(flow, s.get('figs', []))] or [99])
            ck(s.get('z') == 1 and len(flow) == 13 and worst < 0.6, "at a wide view, unzoomed, each figure where the board's grid put it: within %.2f px" % worst)
            await page.set_viewport_size({'width': 1600, 'height': 1000})
            await page.wait_for_timeout(700)
            s = await st()
            z = s.get('z') or 1
            # Grid: whole steps
            await snaps(False, True, False)
            W = await working()
            f2 = fk(W, 'f2')
            pos0 = fk((await st()).get('figs', []), 'f2') or {}
            dxu, dyu = 1.2, 1.3
            await drag('.a3d-clb-arr [data-brdk="f2"] [data-brdgrip]', -dxu * P0 * z * 3, dyu * P0 * z)
            G = fk((await rec('board-climate')).get('figs', []), 'f2') or {}
            ex = max(0, min(12 - f2['w'], round(f2['x'] - 3 * dxu)))
            ck(G.get('x') == ex and G.get('y') == round(f2['y'] + dyu) and abs(G.get('w', 0) - f2['w']) < 1e-3, "Grid: a drag puts the figure on whole steps (%s, %s)" % (G.get('x'), G.get('y')))
            R1 = await rec('board-climate')
            ck(len(R1.get('figs', [])) == 13 and await safe("()=>window.__a3dUndoDepth()") == u0 + 1, "the first change keeps the list: one undo step")
            await safe("()=>window.__a3dUndo()")
            await page.wait_for_timeout(300)
            s = await st()
            pos1 = fk(s.get('figs', []), 'f2') or {}
            ck(s.get('rec') == {'id': 'board-climate', 'kind': 'climate'} and s.get('edit') and s.get('arranged') and near(pos1.get('l'), pos0.get('l'), 0.6) and near(pos1.get('t'), pos0.get('t'), 0.6),
               "undo: the board without a list again, drawn so, still in Edit")
            # Snap: an edge caught
            await snaps(True, False, False)
            W = await working()
            f4, f5 = fk(W, 'f4'), fk(W, 'f5')
            gap = (f5['x'] + f5['w'] - (f4['x'] + f4['w'])) * P0 * z
            gd = await drag('.a3d-clb-arr [data-brdk="f4"] [data-brdrsz]', gap - 7 * z, 3, during="()=>[].map.call(document.querySelectorAll('.a3d-clb-guide'),function(g){return g.className;})")
            G = fk((await rec('board-climate')).get('figs', []), 'f4') or {}
            ck(near(G.get('x', 0) + G.get('w', 0), f5['x'] + f5['w'], 1e-3) and near(G.get('h'), f4['h'], 1e-3) and 'a3d-clb-guide x' in (gd or []),
               "Snap: a corner dragged within 12 px of another figure's edge is caught on it, the edge drawn (%s)" % gd)
            # Ortho: straight across
            await snaps(False, False, True)
            W = await working()
            f7 = fk(W, 'f7')
            await drag('.a3d-clb-arr [data-brdk="f7"] [data-brdgrip]', 70, 30)
            G = fk((await rec('board-climate')).get('figs', []), 'f7') or {}
            ck(near(G.get('y'), f7['y'], 1e-3) and G.get('x', 0) > f7['x'] + 0.3, "Ortho: a slanting drag goes straight across (%s, %s)" % (G.get('x'), G.get('y')))
            # nothing on: free
            await snaps(False, False, False)
            W = await working()
            f9 = fk(W, 'f9')
            await drag('.a3d-clb-arr [data-brdk="f9"] [data-brdgrip]', 0, 0.37 * P0 * z)
            G = fk((await rec('board-climate')).get('figs', []), 'f9') or {}
            ck(near(G.get('y'), f9['y'] + 0.37, 0.02) and near(G.get('x'), f9['x'], 0.02), "no snap: where it is dropped (%s)" % G.get('y'))
            # the keys
            await page.focus('.a3d-clb-arr [data-brdk="f9"]')
            await page.keyboard.press('ArrowDown')
            await page.wait_for_timeout(250)
            await page.keyboard.press('Shift+ArrowLeft')
            await page.wait_for_timeout(250)
            G2 = fk((await rec('board-climate')).get('figs', []), 'f9') or {}
            ck(near(G2.get('y'), G.get('y', 0) + 0.1, 1e-3) and near(G2.get('w'), G.get('w', 0) - 0.1, 1e-3) and
               await safe("()=>document.activeElement&&document.activeElement.getAttribute('data-brdk')") == 'f9', "the keys: down a tenth of a step; Shift, a tenth narrower; the focus kept")
            await snaps(True, False, False)
            mi = await safe("()=>window.__a3dBrdMenu('f3')") or []
            ck([m[1] for m in mi] == ['opts', 'fit', 'dup', 'earlier', 'later', 'remove'], "a figure's menu: Options, Fit, Duplicate, earlier, later, Remove (%s)" % [m[0] for m in mi])
            await safe("()=>window.__a3dBrdOpts('f1',{t:'Our temperatures',show:'table'})")
            s = await st()
            g1 = fk(s.get('figs', []), 'f1') or {}
            ck(g1.get('title') == 'Our temperatures' and 'o-table' in g1.get('cls', '') and
               await safe("()=>getComputedStyle(document.querySelector('.a3d-clb-arr [data-brdk=\"f1\"] .a3d-clb-table')).display") == 'table', "Options: its title, and its numbers as a table")
            k_u = await safe("()=>window.__a3dBrdAdd('lb.utci',{cond:'shade_still'})")
            s = await st()
            gu = fk(s.get('figs', []), k_u) or {}
            W = await working()
            fu = fk(W, k_u) or {}
            ck(gu.get('title', '').startswith('%d%% of the year' % round(U['conditions']['shade_still']['comfort'])) and 'in the shade, in still air' in gu.get('title', '') and
               near(fu.get('y'), max(f['y'] + f['h'] for f in W if f['k'] != k_u), 1e-3) and fu.get('x') == 0 and fu.get('w') == 12 and not gu.get('over'),
               "Add: UTCI in the shade and still air, below the others at its own width and height (%s)" % gu.get('title', '')[:60])
            await safe("(k)=>window.__a3dBrdNudge(k,0,0,true)", k_u)
            h0 = fu.get('h')
            await safe("(k)=>window.__a3dBrdNudge(k,0,-2,true)", k_u)
            await safe("(k)=>window.__a3dBrdFit(k)", k_u)
            ck(near(fk(await working(), k_u).get('h'), h0, 0.01), "Fit: back to its content's height")
            kd = None
            await safe("()=>window.__a3dBrdDup('f5')")
            W = await working()
            kd = [f['k'] for f in W if f['f'] == 'clim.dd' and f['k'] != 'f5']
            ck(len(kd) == 1, "Duplicate: a second of it, below")
            await safe("()=>window.__a3dBrdRemove('f6')")
            R2 = await rec('board-climate')
            ck(R2.get('off') == ['clim.solar'] and not any(f['f'] == 'clim.solar' for f in R2.get('figs', [])), "Remove: off the board, and kept off when its data comes again (%s)" % R2.get('off'))
            await safe("()=>window.__a3dBrdAdd('clim.solar')")
            ck('off' not in await rec('board-climate'), "added again: no longer off")
            await safe("()=>window.__a3dBrdCatalogue()")
            await page.wait_for_timeout(300)
            cd = await safe("""()=>{var d=document.querySelector('.a3d-clb-dlg');if(!d)return null;var pv=d.querySelector('[data-brdaddf="clim.temp"] .a3d-clb-catpv svg .hit');
              return {n:d.querySelectorAll('[data-brdaddf]').length,dis:d.querySelectorAll('[data-brdaddf][disabled]').length,label:d.getAttribute('aria-label'),
                hitFill:pv?getComputedStyle(pv).fill:null,isBoard:!!(document.querySelector('.a3d-clb:not(.a3d-ssboard)')&&!document.querySelector('.a3d-clb:not(.a3d-ssboard)').classList.contains('a3d-clb-dlg'))};}""") or {}
            nodata = len([c for c in cat if not c['has']])
            ck(cd.get('n') == 33 and cd.get('dis') == nodata == 10 and cd.get('label') == 'Add a figure' and cd.get('isBoard'),
               "Add a figure: the 33, by group, each with its preview; the 10 of access and people, with no data yet, not offered (%s)" % cd)
            ck(cd.get('hitFill') in ('rgba(0, 0, 0, 0)', 'transparent'), "the previews in the board's own style (%s)" % cd.get('hitFill'))
            await page.keyboard.press('Escape')
            await page.wait_for_timeout(150)
            ck((await st()).get('dlg') is None and (await st()).get('edit'), "Escape closes the dialog; Edit stays")
            await page.keyboard.press('Escape')
            await page.wait_for_timeout(150)
            ck(not (await st()).get('edit') and (await st()).get('open'), "Escape again leaves Edit; the board stays")
            await safe("()=>window.__a3dBrdEdit(true)")
            n_u = await safe("()=>window.__a3dUndoDepth()")
            await safe("()=>window.__a3dBrdReset()")
            ck((await rec('board-climate')) == {'id': 'board-climate', 'kind': 'climate'} and not (await st()).get('rec', {}).get('figs'), "Reset: the board's own figures in their own places")
            await safe("()=>window.__a3dUndo()")
            await page.wait_for_timeout(300)
            ck(len((await rec('board-climate')).get('figs', [])) >= 13 and (await st()).get('arranged'), "undo: the arrangement back, drawn")
            await page.keyboard.press('Control+y')
            await page.wait_for_timeout(300)
            ck((await rec('board-climate')) == {'id': 'board-climate', 'kind': 'climate'}, "redo: reset again")
            await safe("()=>window.__a3dUndo()")
            await page.wait_for_timeout(300)

            # ---------------------------------------------------------------------------------
            print("\n-- 13. Bands and reading order")
            W = await working()
            app_b = await safe("(L)=>window.__a3dBrdBands(L)", W) or []
            ref_b = R.bands(W)
            ck(app_b == ref_b, "the board's bands and reading order, as the reference works them out (%d bands)" % len(ref_b))
            s = await st()
            order = [f['k'] for f in s.get('figs', [])]
            ck(order == [k for B in ref_b for k in B['k']], "the page's order is the reading order")
            nums = [f['no'] for f in s.get('figs', []) if f['no']]
            ck(nums == ['Fig. %d' % (i + 1) for i in range(len(nums))], "numbered in reading order (%d)" % len(nums))
            T = [{'k': 'f1', 'f': 'clim.wind', 'x': 7, 'y': 0, 'w': 5, 'h': 3}, {'k': 'f2', 'f': 'clim.temp', 'x': 0, 'y': 0.1, 'w': 7, 'h': 5},
                 {'k': 'f3', 'f': 'clim.sun', 'x': 7, 'y': 3.1, 'w': 5, 'h': 3}, {'k': 'f4', 'f': 'clim.dd', 'x': 0, 'y': 6.1, 'w': 12, 'h': 2}]
            tb = await safe("(L)=>window.__a3dBrdBands(L)", T)
            ck(tb == R.bands(T) and tb[0]['k'] == ['f2', 'f1', 'f3'], "a column beside a tall figure: row by row (tops a tenth apart are one row), left to right (%s)" % tb)
            V = await safe("(L)=>window.__a3dBrdValid(L)", [{'f': 'clim.temp', 'x': 11, 'y': -3, 'w': 30, 'h': 0}, {'f': 'nope nope'}, None, {'k': 'f1', 'f': 'text', 'x': 0, 'y': 1, 'w': 6, 'h': 1, 'o': {'t': '  A   heading ', 'show': 'x', 'cond': 'shade_still'}},
                                                            {'k': 'f1', 'f': 'lb.utci', 'x': 2, 'y': 2, 'w': 4, 'h': 4, 'o': {}}]) or []
            ck(V == [{'k': 'f2', 'f': 'clim.temp', 'x': 0, 'y': 0, 'w': 12, 'h': 0.25}, {'k': 'f1', 'f': 'text', 'x': 0, 'y': 1, 'w': 6, 'h': 1, 'o': {'t': 'A heading', 'cond': 'shade_still'}},
                     {'k': 'f3', 'f': 'lb.utci', 'x': 2, 'y': 2, 'w': 4, 'h': 4}],
               "a list read back: sizes held to the board, bad entries left out, names made unique, options checked (%s)" % V)

            # ---------------------------------------------------------------------------------
            print("\n-- 14. Boards of one's own")
            await safe("()=>window.__a3dBrdEdit(false)")
            await page.click('#a3d-rail [data-tab="presentation"]') if await safe("()=>!!document.querySelector('#a3d-rail [data-tab=\"presentation\"]')") else None
            await page.wait_for_timeout(200)
            await safe("()=>document.querySelector('#a3d-leftpanel [data-prpact=\"board\"]').click()")
            await page.wait_for_timeout(150)
            menu = await safe("()=>[].map.call(document.querySelectorAll('#a3d-ltmenu [data-ltm]'),function(b){return [b.textContent,b.getAttribute('data-ltm')];})") or []
            ck(menu[-1] == ['New board', 'new'] and len(menu) == 4, "+ Board: the three boards, then New board (%s)" % menu)
            await safe("()=>document.querySelector('#a3d-ltmenu [data-ltm=\"new\"]').click()")
            await page.wait_for_timeout(500)
            s = await st()
            cid = s.get('cid')
            ck(s.get('kind') == 'custom' and s.get('edit') and s.get('dlg') == 'Add a figure' and re.match(r'^board-c\d+$', cid or ''), "New board: opened in Edit with the catalogue (%s)" % cid)
            for f in ('clim.kpis', 'lb.psych', 'zn.secA', 'text'):
                await safe("(f)=>window.__a3dBrdAdd(f)", f)
            await safe("()=>window.__a3dBrdRename('Comfort and the envelope')")
            s = await st()
            ck([f['f'] for f in s.get('rec', {}).get('figs', [])] == ['clim.kpis', 'lb.psych', 'zn.secA', 'text'] and s.get('h1') == 'Comfort and the envelope' and s.get('label') == 'Comfort and the envelope board',
               "any analysis on it, from any board: indicators, Ladybug's chart, a zoning section, a heading; its name (%s)" % s.get('h1'))
            nt = await safe("()=>{var n=document.querySelector('.a3d-clb:not(.a3d-ssboard) .a3d-clb-notes');return n?[].map.call(n.querySelectorAll('h4'),function(h){return h.textContent;}):null;}") or []
            ck(nt == ['Climate and risk', 'Zoning and yield'], "its notes: those of the boards its figures come from (%s)" % nt)
            pr_ = await safe("()=>window.__a3dPresRecord()") or {}
            cr_ = [b for b in pr_.get('boards', []) if b['id'] == cid]
            ck(cr_ and cr_[0].get('name') == 'Comfort and the envelope' and cid in pr_.get('order', []), "in the set's record, with its name and its place")
            mi = await safe("(i)=>window.__a3dBoardMenuItems(i)", cid) or []
            ck(mi[-1] == 'Delete the board' and 'Duplicate' in mi and 'Edit' in mi, "its menu: Edit, Duplicate, Delete the board (%s)" % mi)
            did = await safe("()=>window.__a3dBrdDupBoard('board-climate')")
            await page.wait_for_timeout(400)
            s = await st()
            ck(s.get('rec', {}).get('name') == 'Copy of Climate and risk' and [f['f'] for f in s.get('rec', {}).get('figs', [])][:2] == ['clim.kpis', 'clim.temp'],
               "the climate board duplicated: a board of one's own, its indicators on top (%s)" % [f['f'] for f in s.get('rec', {}).get('figs', [])][:3])
            await safe("()=>window.__a3dBrdDlgClose()")
            await safe("(i)=>window.__a3dBoardMenuDo('remove',i)", did)
            gone = not any(b['id'] == did for b in (await safe("()=>window.__a3dPresRecord()") or {}).get('boards', []))
            ck(gone and 'deleted' in await toast(), "deleted, and said (%s)" % (await toast())[:60])
            await safe("()=>window.__a3dUndo()")
            await page.wait_for_timeout(300)
            ck(any(b['id'] == did for b in (await safe("()=>window.__a3dPresRecord()") or {}).get('boards', [])), "undo brings it back")

            # ---------------------------------------------------------------------------------
            print("\n-- 15. Present, Print set, the thumbnail")
            await safe("(i)=>window.__a3dBrdOpen(i)", cid)
            await safe("()=>window.__a3dBrdEdit(true)")
            await page.wait_for_timeout(300)
            # while Edit is on: the board as its page for print and its thumbnail draw it -- arranged, nothing of Edit
            def chrome(h):
                """Edit's controls among a page's elements, its style rules (which name them) set aside"""
                h = re.sub(r'<style\b.*?</style>', '', h, flags=re.S)
                cls = set(c for v in re.findall(r'class="([^"]*)"', h) for c in v.split())
                got = sorted(cls & {'a3d-clb-fctl', 'a3d-clb-rsz', 'a3d-clb-ebar', 'a3d-clb-arrgrid', 'a3d-clb-grip', 'a3d-clb-fmenu'})
                got += ['a3d-clb-arr edit'] if 'class="a3d-clb-arr edit"' in h else []
                return got + [a for a in ('data-brd="addnew"', 'data-brd="edit"', 'data-brdgrip', 'data-brdrsz', 'data-brdmenu') if a in h]
            eh = await safe("(i)=>window.__a3dBoardPrintHtml(i)", cid) or ''
            esh = (await safe("()=>window.__a3dPrintSetHtml()") or {}).get('html', '')
            ck((await st()).get('edit') and 'class="a3d-clb-arr"' in eh and 'class="a3d-clb-arr"' in esh and not chrome(eh) and not chrome(esh),
               "while Edit is on, the board's page for print and for its thumbnail: as arranged, nothing of Edit (%s, %s)" % (chrome(eh), chrome(esh)))
            await safe("(i)=>window.__a3dSlideshowStart(i)", cid)
            await page.wait_for_timeout(700)
            pv = await safe("""()=>{var b=document.querySelector('.a3d-ssboard'),a=b&&b.querySelector('.a3d-clb-arr');return b?{arr:!!a,figs:b.querySelectorAll('.a3d-clb-fig').length,
              ctl:b.querySelectorAll('.a3d-clb-fctl,.a3d-clb-rsz,.a3d-clb-ebar').length,label:b.getAttribute('aria-label')}:null;}""") or {}
            ck(pv.get('arr') and pv.get('figs') == 4 and pv.get('ctl') == 0 and pv.get('label') == 'Comfort and the envelope board', "Present: the board as arranged, nothing of Edit (%s)" % pv)
            await safe("()=>window.__a3dSlideshowEnd()")
            await page.wait_for_timeout(300)
            ck((await st()).get('cid') == cid, "and back on it after")
            await safe("()=>window.__a3dBrdEdit(false)")
            ph = (await safe("()=>window.__a3dPrintSetHtml()") or {}).get('html', '')
            ck(ph.count('class="a3d-clb-arr"') >= 2 and 'class="a3d-clb-fctl"' not in ph and 'class="a3d-clb-rsz"' not in ph and 'class="a3d-clb-band' in ph and 'page:a3dbrd' in ph,
               "Print set: the arranged boards on their A3 pages, nothing of Edit (%d arranged)" % ph.count('class="a3d-clb-arr"'))
            # the print set's own page, as printed: each band of figures kept whole across a page break
            pp = await ctx.new_page()
            try:
                await within(pp.set_content(re.sub(r'<script>.*?</script>', '', ph, flags=re.S)), 'print page')
                await pp.emulate_media(media='print')
                bk = await within(pp.evaluate("""()=>[].map.call(document.querySelectorAll('.a3dbrd .a3d-clb-band'),function(b){var s=getComputedStyle(b);return s.breakInside+'|'+s.position;})"""), 'print bands')
            finally:
                await pp.close()
            ck(len(bk) >= 2 and all(b == 'avoid|relative' for b in bk), "their rules go with them: on the printed page no band is split across a page break (%d bands: %s)" % (len(bk), sorted(set(bk))))
            await page.wait_for_timeout(1500)
            th = await safe("""(i)=>{var f=document.querySelector('iframe[data-prpbframe="'+i+'"]');if(!f||!f.contentDocument)return null;var a=f.contentDocument.querySelector('.a3d-clb-arr');
              return a?{zoom:f.contentDocument.defaultView.getComputedStyle(a).zoom,w:Math.round(a.getBoundingClientRect().width)}:'none';}""", cid)
            ck(isinstance(th, dict) and th.get('w') == 1216, "the thumbnail: the arranged board zoomed to its page (%s)" % th)

            # ---------------------------------------------------------------------------------
            print("\n-- 16. A phone")
            c6 = await browser.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
            for h in ('https://archive-api.open-meteo.com/**', 'https://air-quality-api.open-meteo.com/**', 'https://earthquake.usgs.gov/**'):
                await c6.route(h, clim_route)
            await c6.route(PAGES + '**', rt_route)
            p6 = await c6.new_page()
            p6.errs = []
            p6.on('pageerror', lambda e: p6.errs.append(str(e)))
            env = await safe("()=>window.__a3dProjectEnvelope()")
            await within(p6.goto('file://' + str(HTML)), 'goto phone')
            await p6.wait_for_timeout(2300)
            await safe("()=>window.__a3dEnter()", pg=p6)
            await safe("(t)=>window.__a3dImportProject(t,'set.json')", env, pg=p6)
            await p6.wait_for_timeout(1200)
            await safe("(i)=>window.__a3dBrdOpen(i)", cid, pg=p6)
            await p6.wait_for_timeout(600)
            s6 = await st(pg=p6)
            lefts = sorted(set(round(f['l']) for f in s6.get('figs', [])))
            tops = [f['t'] for f in s6.get('figs', [])]
            ck(s6.get('narrow') and lefts == [0] and tops == sorted(tops) and len(s6.get('figs', [])) == 4, "on a phone the figures flow in one column, in reading order (%s)" % lefts)
            await safe("()=>window.__a3dBrdEdit(true)", pg=p6)
            await p6.wait_for_timeout(300)
            hd = await safe("()=>[].filter.call(document.querySelectorAll('.a3d-clb-arr .a3d-clb-grip,.a3d-clb-arr .a3d-clb-rsz'),function(e){return e.getBoundingClientRect().width>0;}).length", pg=p6)
            mb = await safe("()=>Math.round(document.querySelector('.a3d-clb-arr .a3d-clb-fmenu').getBoundingClientRect().height)", pg=p6) or 0
            ck(hd == 0 and mb >= 40, "in Edit: no handles to drag, each figure's menu a finger's size (%s px)" % mb)
            o0 = [f['k'] for f in (await st(pg=p6)).get('figs', [])]
            await safe("(k)=>window.__a3dBrdSwap(k,1)", o0[0], pg=p6)
            o1 = [f['k'] for f in (await st(pg=p6)).get('figs', [])]
            ck(o1[:2] == [o0[1], o0[0]], "Later in reading order: the first and the second change places (%s)" % o1[:2])
            sw = await safe("()=>({sw:document.documentElement.scrollWidth,b:document.querySelector('.a3d-clb:not(.a3d-ssboard)').scrollWidth})", pg=p6) or {}
            ck(sw.get('sw', 999) <= 390 and sw.get('b', 999) <= 392, "nothing spills sideways (%s)" % sw)
            ck(not p6.errs, "no page errors on the phone (%s)" % p6.errs[:3])
            await c6.close()

            # ---------------------------------------------------------------------------------
            print("\n-- 17. Kept")
            before = await safe("()=>window.__a3dPresRecord()")
            lb_before = await safe("()=>window.__a3dLbData()")
            await page.reload()
            await page.wait_for_timeout(2500)
            await safe("()=>window.__a3dEnter()")
            await page.wait_for_timeout(300)
            ck(await safe("()=>window.__a3dPresRecord()") == before, "the set over a reload: its boards, their lists, a board of one's own")
            ck(await safe("()=>window.__a3dLbData()") == lb_before, "and Ladybug's results with their source")
            e9 = await slow("()=>window.__a3dLbRun('utci')")
            ck(isinstance(e9, dict) and 'again' in (e9.get('error') or ''), "a run after a reload asks for the file again: it is not kept (%s)" % (e9 or {}).get('error', '')[:80])
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
