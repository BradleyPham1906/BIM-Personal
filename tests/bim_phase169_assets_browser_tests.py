#!/usr/bin/env python3
"""bim_phase169_assets_browser_tests.py -- V169: assets for scale and the simulations.

People, a wheelchair user, cycles and stands, a parking bay, AASHTO's design vehicles and trees, each
sized from the source the standards registry (V167) names, every size worked out again in
tests/assets_reference.py from those sources.

  1. THE STANDARDS: the eleven records of the Assets area against the reference; each value in the unit
     its source prints; the Green Book's two tables, and where they differ; the trees' table.
  2. THE LIBRARY: the group, its thirteen tiles and their pictures, search, a click and a drop, undo.
  3. THE SIZES: each kind placed, against the reference; a person's eyes and shoulders; a tree's trunk
     and crown; the markers that keep a heading and a centre; turned, rebuilt, still facing its way.
  4. PROPERTIES: each kind's rows; who, pose, height, a tree's leaf, size and crown, a vehicle's turning;
     a wrong value refused; undo.
  5. OVERRIDES: a standard overridden resizes what is placed (not what has its own size); cleared, back;
     the refusals; a place set.
  6. THE GROWING SEASON: ETCCDI's GSL against the reference, both hemispheres, a missing day, no season,
     always warm, the thresholds; from the climate fetched; the season in words.
  7. LEAF AND SHADOW: a deciduous tree bare out of its season, its trunk alone casting a shadow; an
     evergreen; with no climate.
  8. TURNING: the wheelchair's turning space and the vehicles' turning paths, left and right, turned,
     on a hidden layer, drawn.
  9. THE CONTEXT'S TREES: by OpenStreetMap's leaf tags, their crowns and cones, their pages.
 10. A THOUSAND TREES; A RELOAD; A PHONE AND A TABLET; THE NUMBERS NOT WRITTEN INTO THE CODE.

The harness never waits without a bound (V123).
"""
import asyncio, json, math, pathlib, re, sys, traceback

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from bim_phase133_site_context_browser_tests import (   # noqa: E402  the V133 harness: its ground, its tiles
    Checks, Stalled, within, m2g, G, terrarium_png, LAT0, LON0)
import assets_reference as R      # noqa: E402
import climate_fixture as CF      # noqa: E402
from playwright.async_api import async_playwright   # noqa: E402

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'
CK = Checks()
CLIM = ('https://archive-api.open-meteo.com/**', 'https://air-quality-api.open-meteo.com/**', 'https://earthquake.usgs.gov/**')
OVP = ('https://overpass-api.de/**', 'https://overpass.private.coffee/**', 'https://maps.mail.ru/**', 'https://overpass.kumi.systems/**')
BLOCKERS = ('https://server.arcgisonline.com/**', 'https://tile.openstreetmap.org/**', 'https://*.tile.openstreetmap.org/**')
KINDS = ['man', 'woman', 'child', 'seated', 'wheelchair', 'bike', 'stand', 'bay', 'car', 'truck', 'bus', 'broadleaf', 'conifer']
CATS = {'man': 'People', 'woman': 'People', 'child': 'People', 'seated': 'People', 'wheelchair': 'People', 'bike': 'Cycles',
        'stand': 'Cycles', 'bay': 'Parking', 'car': 'Vehicles', 'truck': 'Vehicles', 'bus': 'Vehicles', 'broadleaf': 'Trees', 'conifer': 'Trees'}


def near(a, b, tol=1e-6):
    return a is not None and b is not None and abs(a - b) <= tol


def ctx_fixture():
    def node(i, tags, x, z):
        lon, lat = m2g(x, z)
        return {'type': 'node', 'id': i, 'lat': lat, 'lon': lon, 'tags': tags}
    return {'version': 0.6, 'generator': 'Overpass API (fixture)', 'elements': [
        node(9001, {'natural': 'tree', 'leaf_type': 'broadleaved', 'leaf_cycle': 'deciduous', 'height': '14'}, 20, 20),
        node(9002, {'natural': 'tree', 'leaf_type': 'needleleaved', 'height': '12'}, 40, 20),
        node(9003, {'natural': 'tree', 'height': '12'}, 60, 20),
        node(9004, {'natural': 'tree', 'leaf_type': 'broadleaved', 'leaf_cycle': 'evergreen', 'height': '10'}, 80, 20),
        node(9005, {'natural': 'tree', 'leaf_type': 'needleleaved', 'leaf_cycle': 'deciduous', 'height': '10'}, 20, 40),
        node(9006, {'natural': 'tree', 'leaf_type': 'broadleaved', 'diameter_crown': '5', 'height': '10'}, 40, 40),
        node(9007, {'natural': 'tree', 'leaf_type': 'mixed', 'height': '10'}, 60, 40),
        {'type': 'way', 'id': 9100, 'tags': {'natural': 'tree_row', 'leaf_type': 'needleleaved', 'height': '9'}, 'geometry': G([(0, 70), (16, 70)])},
    ]}


async def run():
    ck = CK
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ST = {}

        async def ovp_route(route):
            ST.setdefault('ovp', []).append(route.request.url)
            await route.fulfill(status=200, body=json.dumps(ctx_fixture()), headers={'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'})

        async def ter_route(route):
            m = re.search(r'/terrarium/(\d+)/(\d+)/(\d+)\.png$', route.request.url)
            if not m:
                await route.abort('internetdisconnected')
                return
            await route.fulfill(status=200, body=terrarium_png(int(m.group(1)), int(m.group(2)), int(m.group(3))),
                                headers={'Content-Type': 'image/png', 'Access-Control-Allow-Origin': '*'})

        async def fresh(vw=(1440, 900), mobile=False):
            c = await browser.new_context(viewport={'width': vw[0], 'height': vw[1]}, has_touch=mobile, is_mobile=mobile)
            for h in CLIM:
                await c.route(h, CF.route_handler(ST))
            for h in OVP:
                await c.route(h, ovp_route)
            await c.route('https://s3.amazonaws.com/**', ter_route)
            for h in BLOCKERS:
                await c.route(h, lambda r: r.abort())
            p = await c.new_page()
            e, w = [], []
            p.on('pageerror', lambda x: e.append(str(x)))
            p.on('console', lambda m: w.append(m.text) if m.type == 'warning' and '[BIM]' in m.text else None)
            await within(p.goto('file://' + str(HTML)), 'goto')
            await p.wait_for_timeout(2000)
            await p.evaluate("()=>window.__a3dEnter()")
            await p.wait_for_timeout(200)
            return c, p, e, w

        ctx, page, errs, warns = await fresh()

        async def safe(js, arg=None, pg=None):
            pg = pg or page
            try:
                return await within(pg.evaluate(js, arg) if arg is not None else pg.evaluate(js), 'evaluate ' + js[:60].replace('\n', ' '))
            except Stalled:
                raise
            except Exception as ex:
                print('      (evaluate failed: %s)' % str(ex)[:200])
                return None

        async def toast(pg=None):
            return await safe("()=>{var t=document.getElementById('a3d-toast');return t?t.textContent:'';}", pg=pg) or ''

        async def place(key, x=0, z=0, p=None, pg=None):
            return await safe("(a)=>window.__a3dEntPlace(a[0],a[1],a[2],a[3])", [key, x, z, p], pg=pg)

        async def info(i, pg=None):
            return await safe("(i)=>window.__a3dEntInfo(i)", i, pg=pg) or {}

        async def props_of(i, pg=None):
            await safe("(i)=>{window.__a3dSelectFor([i]);window.__a3dRefreshProps();}", i, pg=pg)
            await (pg or page).wait_for_timeout(60)
            return await safe("()=>document.getElementById('a3d-propsbody').innerHTML", pg=pg) or ''

        async def props_text(i, pg=None):
            await props_of(i, pg=pg)
            return await safe("()=>document.getElementById('a3d-propsbody').innerText.replace(/\\s+/g,' ')", pg=pg) or ''

        async def set_field(sel, val, pg=None):
            ok = await safe("""(a)=>{var e=document.querySelector('#a3d-propsbody '+a[0]);if(!e)return false;
              if(e.type==='checkbox')e.checked=!!a[1];else e.value=a[1];e.dispatchEvent(new Event('change',{bubbles:true}));return true;}""", [sel, val], pg=pg)
            await (pg or page).wait_for_timeout(120)
            return ok

        async def clear_all(pg=None):
            await safe("()=>{window.__a3dTestSetObjs(window.__a3dState().objs.filter(function(o){return !o.asset;}));window.__a3dTestClearUndo();}", pg=pg)

        async def nosel(pg=None):
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dSetPropTab('site');window.__a3dRefreshProps();}", pg=pg)
            await (pg or page).wait_for_timeout(60)

        async def set_site(lat, lon, pg=None):
            await nosel(pg)
            for k, v in (('sunlat', lat), ('sunlon', lon), ('suntz', '-5')):
                await set_field('[data-propmodel="%s"]' % k, v, pg=pg)

        async def set_date(d, pg=None):
            await nosel(pg)
            await set_field('[data-propmodel="sundate"]', d, pg=pg)

        def sz(I):
            return [round(x, 6) for x in (I.get('size') or [0, 0, 0])]

        try:
            has = await safe("()=>window.__acad3dV169") or ''
            ck(all(w in has for w in ('assets', 'people', 'vehicles', 'turningpaths', 'refit', 'gsl', 'contexttrees')), "__acad3dV169 marker is present (%s)" % has)
            mv = re.search(r"var BIM_APP_VERSION=\{v:'V(\d+)'", HTML.read_text(encoding='utf-8'))
            ck(mv and int(mv.group(1)) >= 169, "the app says V169 or later (%s)" % (mv and mv.group(1)))
            if not has:
                raise Stalled('no V169')

            # ---------------------------------------------------------------------------------
            print("\n-- 1. The standards")
            recs = {r['id']: r for r in (await safe("()=>window.__a3dStdRecords()") or [])}
            mine = [t for t in recs if recs[t].get('area') == 'Assets']
            want = sorted(list(R.TOPICS) + ['utd.trees'])
            ck(sorted(mine) == want, "eleven records in the Assets area (%s)" % sorted(mine))
            for t in want:
                r = recs.get(t) or {'eds': [{}]}
                ed = r['eds'][0]
                src = ed.get('src') or {}
                vals = {x['n']: x for x in ed.get('v', [])}
                ok_v = t == 'utd.trees' or (sorted(vals) == sorted(R.TOPICS[t]) and all(near(vals[n]['v'], R.TOPICS[t][n], 1e-12) for n in R.TOPICS[t]))
                ck(ok_v and all(x.get('say') for x in vals.values()), "%s: every value as its source prints it, each said in words" % t)
                ck(r.get('anywhere') is True and not r.get('cat') and ed.get('st') == 'current' and src.get('lv') == R.LEVELS[t] and
                   (t == 'app.assets' or (src.get('u', '').startswith('https://' + R.HOSTS[t] + '/') and src.get('read') == '2026-10-19')),
                   "%s: applied anywhere and said so, current, level %s, read from %s" % (t, R.LEVELS[t], R.HOSTS.get(t, 'this app')))
                got = await safe("(a)=>window.__a3dStd(a[0],a[1])", [t, (sorted(R.TOPICS[t])[0] if t in R.TOPICS else 'types')])
                ck(got is not None, "%s: the app reads it (%s)" % (t, str(got)[:40]))
            for (t, n), m in R.IN_SOURCE.items():
                ck(abs(R.TOPICS[t][n] - m) <= 0.0015, "%s %s: %.3f m is the source's own figure (%.4f)" % (t, n, R.TOPICS[t][n], m))
            gbv = {x['n']: x for x in ((recs.get('aashto.vehicles') or {'eds': [{'v': []}]})['eds'][0]['v'])}
            agree = [n for n, ft in R.GB_FEET.items() if n not in R.GB_DIFFER and abs(R.TOPICS['aashto.vehicles'][n] - ft * R.FT) <= 0.02]
            ck(len(agree) == len(R.GB_FEET) - 1, "the Green Book's metric tables agree with its feet within 0.02 m, all but one (%d of %d)" % (len(agree), len(R.GB_FEET)))
            ck(abs(R.TOPICS['aashto.vehicles']['BUS_r'] - 41.6 * R.FT) > 0.1 and '41.6 ft' in (gbv.get('BUS_r') or {}).get('say', ''),
               "the city bus's turning radius: 12.80 m in Table 2-5b, 41.6 ft in 2-5a; the record says so")
            ck(all((gbv.get(n) or {}).get('src') == ('%.1f ft' % ft) for n, ft in R.GB_FEET.items() if n not in R.GB_DIFFER),
               "each design vehicle's value carries its figure in feet")
            ck(all((gbv.get(n) or {}).get('gt') == c + '_wb' and gbv[n].get('lt') == c + '_r' for c in ('P', 'SU', 'BUS') for n in [c + '_ctr']) and
               all((gbv.get(c + '_rin') or {}).get('lt') == c + '_ctr' for c in ('P', 'SU', 'BUS')),
               "each turning radius kept in order: wheelbase < centreline < design radius; inside < centreline")
            ut = ((recs.get('utd.trees') or {'eds': [{'v': [{}]}]})['eds'][0]['v'] or [{}])[0]
            ck(ut.get('t') and ut.get('lv') == 'S' and ut.get('v') == R.UTD, "the trees' sizes: a table by type, our medians of the Urban Tree Database's trees (S)")
            ad = (recs.get('aashto.vehicles') or {'eds': [{}]})['eds'][0]
            ck('7th Edition (2018)' in ad.get('name', '') and '23 CFR 625.4' in ad.get('where', '') and ad.get('adopt') == [{'at': 'us'}],
               "the design vehicles: the 7th Edition, the United States' through 23 CFR 625.4")
            used = await safe("()=>window.__a3dStdUsed('aashto.vehicles')") or ''
            ck('applied outside its place' in used, "outside the United States, the vehicles are said to be applied outside their place (%s)" % used[:120])

            # ---------------------------------------------------------------------------------
            print("\n-- 2. The library")
            await page.click('#a3d-rail .a3d-railbtn[data-tab="assets"]')
            await page.wait_for_timeout(300)
            rows = [r for r in (await safe("()=>window.__a3dAssetRows()") or []) if r['spec'].startswith('asset:')]
            ck([r['spec'][6:] for r in rows] == KINDS, "thirteen tiles, in order: people, cycles, parking, vehicles, trees (%s)" % [r['spec'] for r in rows])
            ck(all(r['meta'] == CATS[r['spec'][6:]] and r['live'] for r in rows), "each under its category, each live")
            grp = await safe("""()=>{var g=document.querySelector('[data-a3dassetgrp="entourage"]')||document.querySelector('[data-a3dasgrp="entourage"]');
              var all=document.getElementById('a3d-leftpanel').textContent;return all.indexOf('People, cycles, vehicles, parking and trees')>=0&&all.indexOf('13 item(s)')>=0;}""")
            ck(grp is True, "the group: People, cycles, vehicles, parking and trees, 13 items")
            th = await safe("""()=>{var L=document.querySelectorAll('[data-a3dassets^="asset:"] img'),n=0,i;for(i=0;i<L.length;i++)if(/^data:image\\/png;base64,.{200}/.test(L[i].getAttribute('src')||''))n++;return n;}""")
            ck(th == 13, "each with its picture, drawn from its model (%s)" % th)
            for q, want in (('vehicle', ['car', 'truck', 'bus']), ('tree', ['broadleaf', 'conifer']), ('wheelchair', ['wheelchair']), ('cycle', ['bike', 'stand'])):
                await page.fill('[data-a3dassearch]', q)
                await page.wait_for_timeout(250)
                got = [r['spec'][6:] for r in (await safe("()=>window.__a3dAssetRows()") or []) if r['spec'].startswith('asset:')]
                ck(got == want, "search %r: %s (%s)" % (q, want, got))
            await page.fill('[data-a3dassearch]', '')
            await page.wait_for_timeout(250)
            await clear_all()
            ok = await safe("()=>window.__a3dAssetClick('asset:man')")
            A = [o for o in (await safe("()=>window.__a3dState().objs") or []) if o.get('asset')]
            ck(ok and len(A) == 1 and A[0]['name'] == 'Man %d' % 1 or (A and re.match(r'^Man \d+$', A[0]['name'])), "a click places a man (%s)" % [o['name'] for o in A])
            r0 = await safe("()=>window.__a3dCanvasRect()") or {}
            n0 = await safe("(p)=>window.__a3dAssetDropAt('asset:bike',p[0],p[1])", [int(r0.get('width', 800) * 0.6), int(r0.get('height', 600) * 0.5)])
            A = [o for o in (await safe("()=>window.__a3dState().objs") or []) if o.get('asset')]
            ck(len(A) == 2 and A[1]['asset']['key'] == 'bike', "a drop places a cycle where it was dropped (%s)" % n0)
            await safe("()=>window.__a3dUndo()")
            A = [o for o in (await safe("()=>window.__a3dState().objs") or []) if o.get('asset')]
            ck(len(A) == 1 and A[0]['asset']['key'] == 'man', "undo takes the cycle away")

            # ---------------------------------------------------------------------------------
            print("\n-- 3. The sizes")
            await clear_all()
            ids = {}
            for i, k in enumerate(KINDS):
                ids[k] = await place(k, i * 25, 10)
            I = {k: await info(ids[k]) for k in KINDS}
            for k, who, pose in (('man', 'man', 'standing'), ('woman', 'woman', 'standing'), ('child', 'child', 'standing'), ('seated', 'woman', 'seated')):
                B = R.body(who, pose)
                ck(near(I[k]['size'][0], B['sh'], 1e-9) and near(I[k]['size'][1], B['top'], 1e-9), "%s: shoulders %.3f m across, %.3f m tall (%s)" % (k, B['sh'], B['top'], sz(I[k])))
                b = I[k].get('body') or {}
                ck(near(b.get('eye'), B['eye'], 1e-9) and near(b.get('st'), B['st'], 1e-12) and b.get('out') == B['out'] and near(b.get('speed'), B['speed'], 1e-12),
                   "%s: eyes at %.3f m, NASA's proportions%s" % (k, B['eye'], ', extrapolated' if B['out'] else ''))
            wc = I['wheelchair']['size']
            ck(near(wc[0], 0.85 * R.v('ada.space', 'clear_w'), 1e-9) and near(wc[1], R.v('wheel.awmp', 'height'), 1e-9) and
               0.95 * 0.85 * R.v('ada.space', 'clear_l') < wc[2] <= 0.85 * R.v('ada.space', 'clear_l') + 1e-9,
               "the wheelchair user: within ADA's clear floor space less 15%%, as tall as the Access Board's users (%s)" % sz(I['wheelchair']))
            for k, w in (('bike', [R.v('ltn.cycle', 'width'), R.v('app.assets', 'bike_h'), R.v('ltn.cycle', 'length')]),
                         ('stand', [0.05, R.v('app.assets', 'stand_h'), R.v('app.assets', 'stand_w')]),
                         ('bay', [R.v('parking.bay', 'width'), 0.01, R.v('parking.bay', 'length')])):
                ck(all(near(a, b, 1e-9) for a, b in zip(I[k]['size'], w)), "%s: %s (%s)" % (k, w, sz(I[k])))
            for k, c in R.VEH.items():
                V = R.vehicle(c)
                ck(all(near(a, b, 1e-9) for a, b in zip(I[k]['size'], [V['w'], V['h'], V['l']])), "%s: AASHTO %s, %.2f by %.2f, %.2f m high (%s)" % (k, c, V['l'], V['w'], V['h'], sz(I[k])))
            for k, lf in (('broadleaf', 'B'), ('conifer', 'C')):
                T = R.tree_type(lf, 'D' if lf == 'B' else 'E', 'M')
                ck(all(near(a, b, 1e-9) for a, b in zip(I[k]['size'], [T['cd'], T['h'], T['cd']])), "%s: the Urban Tree Database's %s, %.1f m high, %.1f m across (%s)" % (k, T['key'], T['h'], T['cd'], sz(I[k])))
            ck(I['broadleaf']['faces'] == 26 and I['broadleaf']['cf'] == 6 and I['conifer']['faces'] == 15 and I['conifer']['cf'] == 6,
               "a trunk of six faces first, then twenty for a broadleaf's crown, a cone of nine for a conifer's")
            ck(all(near(I[k]['heading'], 0, 1e-12) and near(I[k]['centre'][0], i * 25, 1e-9) and near(I[k]['centre'][1], 10, 1e-9) and near(I[k]['base'], 0, 1e-12)
                   for i, k in enumerate(KINDS)), "each facing +z, centred where it was put, on the level")
            S = {o['id']: o for o in (await safe("()=>window.__a3dState().objs") or [])}
            ck(all(S[ids[k]]['bim'] == {'type': 'familyInstance', 'familyId': 'asset:' + k, 'familyName': S[ids[k]]['bim']['familyName'],
                                        'category': CATS[k], 'levelId': S[ids[k]]['bim']['levelId']} and S[ids[k]]['asset']['key'] == k for k in KINDS),
               "each a family instance of its kind, in its category")
            cols = {CATS[k]: S[ids[k]]['col'] for k in KINDS}
            ck(len(set(cols.values())) == 5, "each category its own colour (%s)" % cols)
            # turned, then rebuilt: still facing its way
            await safe("(i)=>window.__a3dRotateSelection([i],[25,10],Math.PI/2)", ids['woman'])
            I2 = await info(ids['woman'])
            await set_field('[data-propf="asset:h"]', '1.7') if await props_of(ids['woman']) else None
            I3 = await info(ids['woman'])
            ck(near(abs(I2['heading']), math.pi / 2, 1e-9) and near(I3['heading'], I2['heading'], 1e-9) and near(I3['centre'][0], 25, 1e-9) and near(I3['size'][1], 1.7, 1e-9),
               "turned a quarter, then made 1.7 m tall: rebuilt where it stood, facing the way it faced (%.4f, %.4f)" % (I2['heading'], I3['heading']))

            # ---------------------------------------------------------------------------------
            print("\n-- 4. Properties")
            t = await props_text(ids['man'])
            B = R.body('man')
            ck('Who' in t and 'Pose' in t and 'Eye height (m) %.3f' % B['eye'] in t and 'Shoulder width (m) %.3f' % B['sh'] in t and 'Walking speed 1.33 m/s' in t,
               "a man's rows: who, pose, height, eyes %.3f, shoulders %.3f, walking 1.33 m/s" % (B['eye'], B['sh']))
            ck('Body size: height' in t and 'Body proportions by height' in t and 'Walking speed' in t, "and the standards they come from")
            await set_field('[data-propf="asset:who"]', 'child')
            t = await props_text(ids['man'])
            ck(near((await info(ids['man']))['size'][1], R.v('body.us', 'child'), 1e-9) and 'extrapolated, an estimate' in t, "made a child: 1.321 m, the proportions an estimate, said")
            await set_field('[data-propf="asset:pose"]', 'seated')
            Bc = R.body('child', 'seated')
            ck(near((await info(ids['man']))['size'][1], Bc['top'], 1e-9) and 'Height, seated' in await props_text(ids['man']), "seated: %.3f m to the top of the head, said" % Bc['top'])
            await set_field('[data-propf="asset:h"]', '-1')
            ck('Must be a positive number' in await toast() and near((await info(ids['man']))['size'][1], Bc['top'], 1e-9), "a height of -1 refused, saying why, nothing changed")
            await set_field('[data-propf="asset:h"]', '1.9')
            Bh = R.body('child', 'seated', 1.9)
            ck(near((await info(ids['man']))['body']['eye'], Bh['eye'], 1e-9), "a height of its own, 1.9 m: the eyes follow (%.3f)" % Bh['eye'])
            await safe("()=>window.__a3dUndo()")
            ck(near((await info(ids['man']))['size'][1], Bc['top'], 1e-9), "undo: back to the child's height")
            await props_of(ids['man'])
            await set_field('[data-propf="asset:h"]', '1.9')
            await set_field('[data-propf="asset:who"]', 'woman')
            ck(near((await info(ids['man']))['size'][1], R.body('woman', 'seated')['top'], 1e-9), "someone else chosen: their own height goes, the woman's mean is taken")
            t = await props_text(ids['wheelchair'])
            ck('Height (m) 1.249' in t and 'Seat (m) 0.495' in t and 'Eye height (m) 1.152' in t and '0.76 by 1.22: the clear floor space' in t and
               '0.82 by 1.42 holds 95% of manual chair users' in t and '1.525 across: the turning space' in t and 'Speed 0.91 m/s' in t,
               "the wheelchair user's rows: the Access Board's sizes, ADA's spaces, MUTCD's slower speed")
            t = await props_text(ids['bike'])
            ck('Size (m) 1.8 by 0.65' in t and 'outer radius 1.65, inner 0.85' in t and 'Cycles and cycle parking' in t, "the cycle's: LTN 1/20's size and turning circle")
            t = await props_text(ids['stand'])
            ck('1.2 recommended, 1 at least' in t and 'Access aisle (m) 3' in t and '0.6 to a wall' in t, "the stand's: LTN 1/20's spacing, aisle and clearances")
            t = await props_text(ids['bay'])
            ck('Bay (m) 2.4 by 4.8' in t and '6 at 90 degrees, 4.2 at 60, 3.6 at 45' in t, "the bay's: Manual for Streets' bay and aisles")
            t = await props_text(ids['truck'])
            V = R.vehicle('SU')
            ck('Single-unit truck (AASHTO SU-30)' in t and 'Height (m) 3.35 to 4.11, drawn at 4.11' in t and 'Wheelbase (m) 6.1' in t and '1.22 in front, 1.83 behind' in t,
               "the delivery truck's: AASHTO's SU-30, its height range, wheelbase, overhangs")
            ck('12.73 at the least' in t and '11.58: the centreline' in t and '8.64 at the least' in t and ('%.3f' % V['rov']) in t and 'Design vehicles' in t,
               "and its turning: 12.73, 11.58, 8.64, its overhang's corner %.3f, worked out" % V['rov'])
            ck('Passenger car (AASHTO P)' in await props_text(ids['car']) and 'City transit bus (AASHTO CITY-BUS)' in await props_text(ids['bus']), "the car and the bus named as AASHTO names them")
            t = await props_text(ids['broadleaf'])
            ck('Leaf' in t and 'Leaves' in t and 'Height (m)' in t and 'Crown across (m)' in t and 'all year, taken so' in t and 'Tree sizes' in t and 'Growing season' in t,
               "a tree's rows: leaf, leaves, size, height, crown; in leaf all year until the climate is fetched, said")
            await set_field('[data-propf="asset:size"]', 'L')
            ck(sz(await info(ids['broadleaf'])) == [15.9, 20, 15.9], "made large: the database's large broadleaf, 20 m, 15.9 m across")
            await set_field('[data-propf="asset:leaf"]', 'C')
            Ic = await info(ids['broadleaf'])
            ck(sz(Ic) == [10.7, 20, 10.7] and Ic['faces'] == 15, "made a conifer, still deciduous: the large conifer (no deciduous one measured), a cone")
            await set_field('[data-propf="asset:h"]', '9')
            ck(sz(await info(ids['broadleaf'])) == [10.7, 9, 10.7], "a height of its own: only the height changes")
            await set_field('[data-propf="asset:cd"]', 'wide')
            ck('Must be a number' in await toast() and sz(await info(ids['broadleaf'])) == [10.7, 9, 10.7], "a crown of 'wide' refused, nothing changed")

            # ---------------------------------------------------------------------------------
            print("\n-- 5. Overrides")
            await clear_all()
            m1 = await place('man', 0, 0)
            m2 = await place('man', 3, 0, {'h': 1.8})
            c1 = await place('car', 10, 0)
            t1 = await place('conifer', 20, 0)
            ok = await safe("()=>window.__a3dStdOverride('body.us','man',1.6,'a shorter population')")
            ck(ok and near((await info(m1))['size'][1], 1.6, 1e-9) and near((await info(m2))['size'][1], 1.8, 1e-9),
               "the men's height overridden to 1.6 m: the placed man resizes, the one with his own height does not")
            ck((await safe("()=>window.__a3dEntRefit()") or {}).get('n') == 4, "every placed asset rebuilt")
            ck('overridden' in (await props_text(m1)) or '1.6' in (await props_text(m1)), "the man's page shows the override")
            await safe("()=>window.__a3dStdClear('body.us','man')")
            ck(near((await info(m1))['size'][1], 1.753, 1e-9), "cleared: back to 1.753 m")
            await safe("()=>window.__a3dStdOverride('aashto.vehicles','P_l',5,'a smaller car')")
            ck(near((await info(c1))['size'][2], 5, 1e-9), "the car's length overridden: 5 m")
            ok = await safe("()=>window.__a3dStdOverride('aashto.vehicles','P_ctr',3,'too tight')")
            ck(ok is False and 'must be more than 3.35' in await toast(), "a centreline radius under the wheelbase refused (%s)" % (await toast())[:80])
            ok = await safe("()=>window.__a3dStdOverride('utd.trees','types',1,'x')")
            ck(ok is False and 'is a table' in await toast() and near((await info(t1))['size'][1], 12.5, 1e-9), "the trees' table refused as an override: a pack changes it")
            await safe("()=>window.__a3dStdOverride('app.assets','wheel_p',0.8,'bigger wheels')")
            ck(near((await info(c1))['size'][2], 5, 1e-9), "the app's own wheel size overridden: rebuilt, the car still 5 m")
            await safe("()=>{window.__a3dStdClear('aashto.vehicles','P_l');window.__a3dStdClear('app.assets','wheel_p');}")
            await safe("()=>window.__a3dStdSetPlace({cc:'us',r:'us-pa'},'hand')")
            used = await safe("()=>window.__a3dStdUsed('aashto.vehicles')") or ''
            ck('applied outside its place' not in used, "the site in Pennsylvania: the vehicles are its own country's (%s)" % used[:100])
            await safe("()=>window.__a3dStdSetPlace(null)")

            # ---------------------------------------------------------------------------------
            print("\n-- 6. The growing season")
            D = CF.daily(2015, 2024)
            for lat in (40, -35):
                g = await safe("(a)=>window.__a3dClimGsl(a[0],a[1])", [D, lat]) or {}
                r = R.gsl(D, lat)
                ck(g == r, "lat %d: from day %s to day %s, the median of %s years (%s)" % (lat, r['s'], r['e'], r['years'], g))
            D2 = json.loads(json.dumps(D))
            k = D2['daily']['time'].index('2016-05-05')
            D2['daily']['temperature_2m_mean'][k] = None
            D2['daily']['temperature_2m_max'][k] = None
            ck((await safe("(a)=>window.__a3dClimGsl(a[0],a[1])", [D2, 40]) or {}) == R.gsl(D2, 40) and R.gsl(D2, 40)['years'] == 9, "a year with a missing day left out (9 years)")
            D3 = json.loads(json.dumps(D))
            D3['daily']['temperature_2m_mean'] = [None] * len(D3['daily']['time'])
            ck((await safe("(a)=>window.__a3dClimGsl(a[0],a[1])", [D3, 40]) or {}) == R.gsl(D3, 40), "no means: the middle of the highest and lowest, as ETCCDI's TG")

            def year(vals, y=2021):
                import datetime as _d
                t0 = _d.date(y, 1, 1)
                n = len(vals)
                return {'daily': {'time': [(t0 + _d.timedelta(days=i)).isoformat() for i in range(n)], 'temperature_2m_mean': vals,
                                  'temperature_2m_max': vals, 'temperature_2m_min': vals}}
            cold = year([-10.0] * 365)
            warm = year([20.0] * 365)
            edge = year([5.0] * 100 + [5.1] * 6 + [5.0] * 259)
            five = year([5.0] * 120 + [9.0] * 5 + [5.0] * 240)
            fall = year([4.0] * 80 + [12.0] * 220 + [5.0] * 10 + [4.9] * 55)
            april = year([4.0] * 70 + [9.0] * 20 + [2.0] * 10 + [15.0] * 200 + [1.0] * 65)
            for nm, Y, w in (('never above 5 C', cold, {'s': 365, 'e': 365}), ('always warm', warm, {'s': 0, 'e': 365}),
                             ('5.0 C is not above 5: the season starts at the first 6 days of 5.1', edge, {'s': 100, 'e': 365}),
                             ('five warm days are not a span of six', five, {'s': 365, 'e': 365}),
                             ('5.0 C is not below 5: the season ends at the first 6 days of 4.9', fall, {'s': 80, 'e': 310}),
                             ('a cold April does not end it: the end is looked for after 1 July', april, {'s': 70, 'e': 300})):
                g = await safe("(a)=>window.__a3dClimGsl(a[0],a[1])", [Y, 40]) or {}
                r = R.gsl(Y, 40)
                ck(g.get('s') == r['s'] == w['s'] and g.get('e') == r['e'] == w['e'], "%s (%s)" % (nm, g))
            await safe("()=>window.__a3dStdOverride('etccdi.gsl','t',10,'a later spring')")
            g10 = await safe("(a)=>window.__a3dClimGsl(a[0],a[1])", [D, 40]) or {}
            R.TOPICS['etccdi.gsl']['t'] = 10
            r10 = R.gsl(D, 40)
            R.TOPICS['etccdi.gsl']['t'] = 5
            ck(g10 == r10 and g10.get('s', 0) > R.gsl(D, 40)['s'], "the threshold overridden to 10 C: a shorter season (%s)" % g10)
            await safe("()=>window.__a3dStdClear('etccdi.gsl','t')")
            # from the climate fetched
            await clear_all()
            tb = await place('broadleaf', 0, 0)
            tc = await place('conifer', 15, 0)
            tl = await place('conifer', 30, 0, {'cyc': 'D'})
            sh0 = await safe("()=>window.__a3dShadowFaces('2025-01-15')") or {}
            ck(sh0.get(tb) == 26 and sh0.get(tl) == 15, "with no climate: a deciduous tree in leaf all year, as said (%s)" % sh0.get(tb))
            await set_site('40', '-75')
            ST['hits'] = []
            r = await safe("()=>Promise.resolve(window.__a3dClimFetch())") or {}
            du = [u for u in ST.get('hits', []) if 'daily=' in u]
            m = re.search(r'start_date=(\d{4})-.*end_date=(\d{4})-', du[0]) if du else None
            Df = CF.daily(int(m.group(1)), int(m.group(2))) if m else None
            Gs = await safe("()=>window.__a3dEntSeason()") or {}
            Gr = R.gsl(Df, 40) if Df else {}
            ck(r.get('climate') and {k: Gs.get(k) for k in ('s', 'e', 'years', 'sh')} == Gr and (Gs.get('std') or {}),
               "the climate fetched: the season kept with the site, with the standard it used (%s)" % {k: Gs.get(k) for k in ('s', 'e', 'years')})
            await set_date('2025-06-21')
            t = await props_text(tb)
            ck(('from %s to %s' % (R.day_name(Gr.get('s', 0), False), R.day_name(Gr.get('e', 1) - 1, False))) in t and 'the median of %d years' % Gr.get('years', 0) in t and
               'On the sun study\'s date, 2025-06-21: in leaf' in t, "its page: in leaf from %s to %s, and on the sun study's date" % (R.day_name(Gr.get('s', 0), False), R.day_name(Gr.get('e', 1) - 1, False)))
            ck('all year: evergreen' in await props_text(tc), "an evergreen: all year")

            # ---------------------------------------------------------------------------------
            print("\n-- 7. Leaf and shadow")
            for d in ('2025-01-15', '2025-03-01', '2025-04-20', '2025-06-21', '2025-11-30', '2025-12-24'):
                il = await safe("(d)=>window.__a3dEntInLeaf(d)", d)
                sf = await safe("(d)=>window.__a3dShadowFaces(d)", d) or {}
                w_ = R.in_leaf(Gr, d)
                ck(il == w_ and sf.get(tb) == (26 if w_ else 6) and sf.get(tc) == 15 and sf.get(tl) == (15 if w_ else 6),
                   "%s: the deciduous trees %s; the evergreen casts all of itself" % (d, 'in leaf, all of each' if w_ else 'bare, their trunks alone casting a shadow'))
            import datetime as _dt
            for d_, w_ in ((Gr['s'] - 1, False), (Gr['s'], True), (Gr['e'] - 1, True), (Gr['e'], False)):
                ds = (_dt.date(2025, 1, 1) + _dt.timedelta(days=d_)).isoformat()
                ck(await safe("(d)=>window.__a3dEntInLeaf(d)", ds) is w_ and R.in_leaf(Gr, ds) is w_, "%s, day %d: %s" % (ds, d_, 'in leaf' if w_ else 'bare'))
            await set_date('2025-01-15')
            ck('bare, its trunk alone casting a shadow' in await props_text(tb), "its page on a winter date: bare, said")
            sh_ = await safe("()=>window.__a3dShadowFaces()") or {}
            ck(sh_.get(tb) == 6, "with no date given, the sun study's: bare in January")

            # ---------------------------------------------------------------------------------
            print("\n-- 8. Turning")
            await clear_all()
            wc1 = await place('wheelchair', 5, 5)
            cars = {}
            for i, (k, c) in enumerate(R.VEH.items()):
                cars[k] = await place(k, 40 * i, 50, {'turn': True})
            ct = await place('car', 0, 120, {'turn': True, 'side': 'R'})
            T = {x['id']: x for x in ((await safe("()=>window.__a3dEntTurns()") or {}).get('turns') or [])}
            ck(wc1 in T and len(T[wc1]['r']) == 1 and near(T[wc1]['r'][0], R.v('ada.space', 'turn') / 2, 1e-12) and near(T[wc1]['c'][0], 5, 1e-9) and near(T[wc1]['c'][1], 5, 1e-9),
               "the wheelchair user's turning space: ADA's 1.525 m across, round the user")
            for i, (k, c) in enumerate(R.VEH.items()):
                V = R.vehicle(c)
                x = T.get(cars[k]) or {'r': [0, 0, 0], 'c': [0, 0]}
                cc = R.turn_centre(c, 40 * i, 50)
                ck(len(x['r']) == 3 and all(near(a, b, 1e-9) for a, b in zip(x['r'], [V['rin'], V['r'], V['rov']])) and near(x['c'][0], cc[0], 1e-9) and near(x['c'][1], cc[1], 1e-9),
                   "%s: its path from the inside radius %.2f out to the overhang's corner %.3f, round a centre %.2f m off its rear axle, to its left" % (k, V['rin'], V['rov'], V['rr']))
            x = T.get(ct) or {'c': [0, 0]}
            cc = R.turn_centre('P', 0, 120, 0, 'R')
            ck(near(x['c'][0], cc[0], 1e-9) and x.get('side') == 'R' and x['c'][0] < 0, "turning right: the centre on its other side")
            await safe("(i)=>window.__a3dRotateSelection([i],[0,50],Math.PI/2)", cars['car'])
            I4 = await info(cars['car'])
            x = {y['id']: y for y in (await safe("()=>window.__a3dEntTurns()") or {}).get('turns', [])}.get(cars['car']) or {'c': [0, 0]}
            cc = R.turn_centre('P', I4['centre'][0], I4['centre'][1], I4['heading'])
            ck(near(x['c'][0], cc[0], 1e-9) and near(x['c'][1], cc[1], 1e-9), "the car turned a quarter: its turning centre turns with it")
            await safe("()=>{window.__a3dSetView('top');window.__a3dCamSet({dist:160,tx:40,ty:0,tz:60});}")
            await page.wait_for_timeout(500)
            dr = (await safe("()=>window.__a3dEntTurns()") or {}).get('drawn')
            ck(dr == 5, "the five drawn on the plan (%s)" % dr)
            await props_of(cars['bus'])
            await set_field('[data-propf="asset:turn"]', False)
            T2 = {y['id'] for y in (await safe("()=>window.__a3dEntTurns()") or {}).get('turns', [])}
            ck(cars['bus'] not in T2 and len(T2) == 4, "the bus's box unticked: its path not shown")
            await set_field('[data-propf="asset:turn"]', True)
            await set_field('[data-propf="asset:side"]', 'R')
            x = {y['id']: y for y in (await safe("()=>window.__a3dEntTurns()") or {}).get('turns', [])}.get(cars['bus']) or {}
            ck(x.get('side') == 'R', "ticked again, and turned to the right")
            lay = await safe("""(i)=>{var o=window.__a3dState().objs.filter(function(x){return x.id===i;})[0];var L=window.__a3dLayers().filter(function(l){return l.id===o.layer;})[0];
              window.__a3dLayerSet(L.id,'visible',false);var n=window.__a3dEntTurns().turns.length;window.__a3dLayerSet(L.id,'visible',true);return n;}""", cars['bus'])
            ck(lay == 0, "their layer hidden: none shown (%s)" % lay)

            # ---------------------------------------------------------------------------------
            print("\n-- 9. The context's trees")
            for tags, w in (({'leaf_type': 'broadleaved', 'leaf_cycle': 'deciduous'}, 0.85), ({'leaf_type': 'needleleaved'}, 0.74),
                            ({'leaf_type': 'broadleaved', 'leaf_cycle': 'evergreen'}, 0.98), ({'leaf_type': 'broadleaved'}, 0.85),
                            ({'leaf_type': 'needleleaved', 'leaf_cycle': 'deciduous'}, 0.74), ({}, 0.6), ({'leaf_type': 'mixed'}, 0.6),
                            ({'leaf_type': 'leafless'}, 0.6), ({'leaf_cycle': 'semi_evergreen'}, 0.6),
                            ({'leaf_type': 'broadleaved', 'leaf_cycle': 'semi_evergreen'}, 0.98), ({'leaf_type': 'broadleaved', 'leaf_cycle': 'semi_deciduous'}, 0.85)):
                got = (await safe("(t)=>window.__a3dEntCrown(t)", tags) or {}).get('ratio')
                ck(near(got, w, 1e-12) and near(R.crown_ratio(tags), w, 1e-12), "a mapped tree %s: its crown %.2f of its height" % (tags or 'untagged', w))
            await clear_all()
            await set_site(repr(LAT0), repr(LON0))
            await safe("()=>Promise.resolve(window.__a3dCtxFetch())")
            for _ in range(80):
                if [o for o in (await safe("()=>window.__a3dState().objs") or []) if (o.get('context') or {}).get('kind') == 'trees']:
                    break
                await page.wait_for_timeout(250)
            TR = {}
            for o in await safe("()=>window.__a3dState().objs") or []:
                c_ = o.get('context') or {}
                if c_.get('kind') == 'trees':
                    TR.setdefault(c_.get('id'), []).append(o)

            def crown(o):
                vv = o['mesh']['v'][6:] if o.get('mesh') else []
                return (max(p[0] for p in vv) - min(p[0] for p in vv)) if vv else None
            for i, (h, cd, cone) in ((9001, (14, 11.9, False)), (9002, (12, 12 * 0.74, True)), (9003, (12, 7.2, False)), (9004, (10, 9.8, False)),
                                     (9005, (10, 7.4, True)), (9006, (10, 5, False)), (9007, (10, 6, False))):
                o = (TR.get(i) or [{}])[0]
                c_ = o.get('context') or {}
                ck(o and near(crown(o), cd, 1e-6) and near(c_.get('crown'), round(cd * 100) / 100, 1e-9) and len(o['mesh']['f']) == (15 if cone else 26),
                   "OSM tree %d: %.2f m across, %s (%s)" % (i, cd, 'a cone' if cone else 'a crown of twenty faces', crown(o)))
            row = TR.get(9100) or []
            ck(len(row) == 3 and all(len(o['mesh']['f']) == 15 for o in row), "a row of needle-leaved trees: every tree a cone (%d)" % len(row))
            t = await props_text((TR.get(9001) or [{}])[0].get('id', ''))
            ck('Leaf broadleaved, deciduous' in t, "a mapped tree's page: its leaf, as mapped")
            t = await props_text((TR.get(9002) or [{}])[0].get('id', ''))
            ck('needle-leaved, its leaf cycle not mapped' in t, "and what is not mapped, said")
            t = await props_text((TR.get(9003) or [{}])[0].get('id', ''))
            ck('Leaf ' not in t and '12 m, crown 7.2 m across' in t, "an untagged tree: no leaf line, V157's crown")

            # ---------------------------------------------------------------------------------
            print("\n-- 10. A thousand trees")
            await clear_all()
            res = await within(page.evaluate("""()=>{var T=[],i,t;for(i=0;i<1000;i++){t=performance.now();window.__a3dEntPlace('broadleaf',(i%40)*12,Math.floor(i/40)*12+200,{});T.push(performance.now()-t);}
              var objs=window.__a3dState().objs.filter(function(o){return o.asset;});var s=JSON.stringify(objs).length;
              t=performance.now();var n=window.__a3dEntRefit().n;return {n:objs.length,json:s,last:T.slice(990).reduce(function(a,b){return a+b;},0)/10,refit:performance.now()-t,rn:n};}"""), 'a thousand trees')
            ck(res['n'] == 1000 and res['json'] / 1000 < 2048, "a thousand trees, %.0f bytes each in the project (under 2 KB)" % (res['json'] / 1000))
            ck(res['last'] < 150 and res['refit'] < 500 and res['rn'] == 1000, "the thousandth placed in %.0f ms, all rebuilt in %.0f ms" % (res['last'], res['refit']))
            await clear_all()

            # ---------------------------------------------------------------------------------
            print("\n-- 11. A reload")
            pr = await place('seated', 1, 2, {'who': 'man'})
            pv = await place('truck', 20, 2, {'turn': True})
            before = await info(pr)
            await page.evaluate("()=>window.dispatchEvent(new Event('beforeunload'))")
            await page.wait_for_timeout(400)
            await page.reload()
            await page.wait_for_timeout(2500)
            await safe("()=>window.__a3dEnter()")
            after = await info(pr)
            ck(after and after.get('p') == before.get('p') and sz(after) == sz(before) and after.get('key') == 'seated', "a reload keeps a placed asset: its parameters and its model")
            ck(pv in {y['id'] for y in (await safe("()=>window.__a3dEntTurns()") or {}).get('turns', [])}, "and the truck's turning path")
            ck({k: (await safe("()=>window.__a3dEntSeason()") or {}).get(k) for k in ('s', 'e')} == {'s': Gr.get('s'), 'e': Gr.get('e')}, "and the site's growing season")
            ck(not errs, "no page errors (%s)" % errs[:2])
            ck(not [w for w in warns if 'could not' in w], "no warnings (%s)" % warns[:2])
            await ctx.close()

            # ---------------------------------------------------------------------------------
            print("\n-- 12. A phone and a tablet")
            for vw, nm in (((390, 844), 'a phone'), ((820, 1180), 'a tablet')):
                c3, p3, e3, w3 = await fresh(vw=vw, mobile=True)
                await p3.click('#a3d-rail .a3d-railbtn[data-tab="assets"]')
                await p3.wait_for_timeout(300)
                rows = [r['spec'][6:] for r in (await safe("()=>window.__a3dAssetRows()", pg=p3) or []) if r['spec'].startswith('asset:')]
                ok = await safe("()=>window.__a3dAssetClick('asset:car')", pg=p3)
                A = [o for o in (await safe("()=>window.__a3dState().objs", pg=p3) or []) if o.get('asset')]
                t = await props_text(A[0]['id'] if A else '', pg=p3)
                ck(rows == KINDS and ok and len(A) == 1 and 'Passenger car (AASHTO P)' in t and not e3, "on %s: the thirteen tiles, a car placed, its page" % nm)
                await c3.close()

            # ---------------------------------------------------------------------------------
            print("\n-- 13. The numbers not written into the code")
            src = HTML.read_text(encoding='utf-8')
            a0, a1 = src.find('  var BIM_ENT=['), src.find('  /* A mesh drawn from above one corner')
            g0 = src.find('  function bimClimGsl(')
            code = src[a0:a1] + src[g0:src.find('  /* ten years of days', g0)]
            ck(a0 > 0 and a1 > a0 and g0 > 0, "the assets' code found (%d characters)" % (a1 - a0))
            vals = set()
            for t_, d_ in R.TOPICS.items():
                for n_, v_ in d_.items():
                    s_ = repr(float(v_)).rstrip('0').rstrip('.')
                    if len(s_.replace('.', '').lstrip('0')) >= 3:
                        vals.add(s_)
            for row_ in R.UTD:
                for v_ in row_[1:]:
                    s_ = repr(float(v_)).rstrip('0').rstrip('.')
                    if len(s_.replace('.', '').lstrip('0')) >= 3:
                        vals.add(s_)
            found = sorted(s_ for s_ in vals if re.search(r'(?<![\w.])' + re.escape(s_) + r'(?![\d])', code))
            ck(len(vals) > 40 and not found, "none of the %d sources' values written into the code: all read from the registry (%s)" % (len(vals), found))
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
    ok_ = asyncio.run(run())
    sys.exit(0 if ok_ else 1)
