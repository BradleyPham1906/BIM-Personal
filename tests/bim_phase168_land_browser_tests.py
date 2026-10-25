#!/usr/bin/env python3
"""bim_phase168_land_browser_tests.py -- V168: site analysis in the model IV, land.

The neighbourhood is tests/land_use_fixture.py's: V166's streets and walk times, V164's context, and the
land added, a case of each rule. Everything the four analyses work out is worked out again in
tests/land_use_reference.py, from the fixture's own coordinates and the methods' sources.

  1. THE STANDARDS: LBCS's families and colours, Spacematrix, 3-30-300 and the app's land settings as
     records (V167), against the reference; the crosswalk whole; how each applies.
  2. THE CONTEXT: the land use the query asks for; an amenity's grounds as land use; courtyards kept.
  3. THE CROSSWALK: every tag of the table, as a building and as an area; the order tags are read in.
  4. LAND USE: every grid cell's family against the reference, the cases by name; the mix and its
     index; the areas and buildings drawn, their colours on the light map and the dark plan, the
     textures, the labels, the key.
  5. FIGURE-GROUND: Spacematrix's measures for the square and each cell; the storeys' rules; the
     courtyard; the grain; a project fetched before V168.
  6. GREEN AND TREES: the canopy on its grid, cut to the context; the trees seen; the green spaces, the
     small and the private; the walks; 3-30-300.
  7. ZONING AROUND: a council layer's districts, its own colours read once, the site's district, the
     shares; a layer with no colours, one that fails, none; Esri's renderer read case by case.
  8. FINDINGS AND ROWS: the four findings and their standards; overrides working them out again; the
     rows in their categories; the layers hidden or shown.
  9. ON SCREEN: the texture's pixels; a phone and a tablet; a reload.

The harness never waits without a bound (V123).
"""
import asyncio, json, math, pathlib, re, sys, traceback

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from bim_phase133_site_context_browser_tests import Checks, Stalled, within   # noqa: E402
import land_use_fixture as FX     # noqa: E402
import land_use_reference as R    # noqa: E402
import access_fixture as AFX      # noqa: E402
from playwright.async_api import async_playwright   # noqa: E402

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'
CK = Checks()
BLOCKERS = ('https://server.arcgisonline.com/**', 'https://tile.openstreetmap.org/**', 'https://*.tile.openstreetmap.org/**')
LOT = [list(p) for p in AFX.LOT]
LT = {1000: ('#eda100', '#8a5e00'), 2000: ('#e34948', '#8f1f1e'), 3000: ('#7a3fb0', '#4a2370'), 4000: ('#3b8ee8', '#1b4f8f'), 5000: ('#9a9a9a', '#555555'),
      6000: ('#2f4f4f', '#0f2222'), 7000: ('#62c27a', '#2d6f3e'), 8000: ('#008300', '#004d00'), 9000: ('#ffffff', '#8a8f96')}
DK = {1000: ('#d19a00', '#f0c040'), 2000: ('#e66767', '#f39a9a'), 3000: ('#8e5cc8', '#c2a2ea'), 4000: ('#4a9af0', '#a0c8f8'), 5000: ('#8f949b', '#c8ccd0'),
      6000: ('#5f8a8a', '#a8c8c8'), 7000: ('#6fd08a', '#b0e8c0'), 8000: ('#008300', '#7fd07f'), 9000: ('#e8eaec', '#8a8f96')}
TEX = {3000: '45', 6000: '135', 8000: 'dot'}


def near(a, b, tol=1e-6):
    return a is not None and b is not None and abs(a - b) <= tol * max(1.0, abs(b))


async def run():
    ck = CK
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()

        async def fresh(store, vw=(1440, 900), mobile=False):
            c = await browser.new_context(viewport={'width': vw[0], 'height': vw[1]}, has_touch=mobile, is_mobile=mobile)
            for h in FX.HOSTS:
                await c.route(h, FX.route_handler(store))
            for h in BLOCKERS:
                await c.route(h, lambda r: r.abort())
            p = await c.new_page()
            e = []
            p.on('pageerror', lambda x: e.append(str(x)))
            await within(p.goto('file://' + str(HTML)), 'goto')
            await p.wait_for_timeout(2000)
            await p.evaluate("()=>window.__a3dEnter()")
            await p.evaluate("""(a)=>{var o=window.__a3dState().objs.filter(function(x){return x.t!=='property'&&x.id!=='LOT';});
              o.push({id:'LOT',t:'sketch',name:'Lot',col:'#5ec4b8',pos:[0,0,0],pts:a,y:0,closed:true,layer:'layer-0'});
              window.__a3dTestSetObjs(o);window.__a3dPropertyFromSketch('LOT');}""", LOT)
            await p.evaluate("()=>window.__a3dAnzView(true)")
            await p.wait_for_timeout(200)
            return c, p, e

        ST = {}
        ctx, page, errs = await fresh(ST)

        async def safe(js, arg=None, pg=None):
            pg = pg or page
            try:
                return await within(pg.evaluate(js, arg) if arg is not None else pg.evaluate(js), 'evaluate ' + js[:60].replace('\n', ' '))
            except Stalled:
                raise
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:200])
                return None

        async def wait_run(pg=None, bound=120):
            for _ in range(bound * 4):
                s = await safe("()=>window.__a3dSiteRunState()", pg=pg) or {}
                if not s.get('busy'):
                    await safe("()=>window.__a3dAwClassic&&window.__a3dAwClassic()", pg=pg)   # V171b: a run ends in the analysis workspace with none shown; this suite reads each analysis as a run drew it before
                    return s
                await (pg or page).wait_for_timeout(250)
            raise Stalled('the run did not end')

        async def analyze(pg=None):
            pg = pg or page
            if await pg.query_selector('[data-saaddr]'):
                await pg.fill('[data-saaddr]', '1 Market Street')
            await safe("()=>document.querySelector('[data-saact=\"analyze\"]').click()", pg=pg)
            await pg.wait_for_timeout(100)
            return await wait_run(pg=pg)

        async def diags(a=None, pg=None):
            return [o for o in ((await safe("()=>window.__a3dState().objs", pg=pg)) or []) if o.get('t') == 'diag' and (a is None or o['dg']['a'] == a)]

        def by_k(L):
            return {o['dg']['k']: o for o in L}

        def rows(o):
            return {r[0]: r[1] for r in o['dg']['info'].get('rows', [])}

        async def finding(auto, pg=None):
            for f in (await safe("()=>window.__a3dSaAuto()", pg=pg)) or []:
                if f.get('auto') == auto:
                    return f
            return None

        A = R.areas()
        B = R.buildings()
        T = R.trees()
        RE = R.reach()
        W = R.window()

        try:
            fin = await analyze()
            steps = {s['id']: s for s in fin.get('steps', [])}
            ck(steps.get('context', {}).get('state') == 'ok' and steps.get('draw', {}).get('state') == 'ok', "Analyze site: the context and the drawing done (%s)" % steps.get('context', {}).get('text', '')[:80])

            # ---------------------------------------------------------------------------------
            print("\n-- 1. The standards")
            ck(await safe("()=>typeof window.__acad3dV168==='string'&&/lbcs/.test(window.__acad3dV168)&&/33300/.test(window.__acad3dV168)") is True, "the V168 marker")
            ver = (await safe("()=>window.__a3dVersion()") or {}).get('v', '')
            ck(re.match(r'^V\d+$', ver) and int(ver[1:]) >= 168, "the app says V168 or later (%s)" % ver)
            RECS = {r['id']: r for r in (await safe("()=>window.__a3dStdRecords()") or [])}
            land = [t for t in ('lbcs.activity', 'spacematrix', 'green.33300', 'app.land') if RECS.get(t, {}).get('area') == 'Land and green']
            ck(len(land) == 4, "four topics in Land and green: LBCS, Spacematrix, 3-30-300, the app's land settings (%s)" % land)
            lb = RECS.get('lbcs.activity', {}).get('eds', [{}])[0]
            fam = [tuple(x) for x in ([v for v in lb.get('v', []) if v['n'] == 'families'] or [{'v': []}])[0]['v']]
            ck(fam == R.FAMILIES, "LBCS's nine families and their colours, as APA's workbook gives them")
            ck(lb.get('src', {}).get('lv') == 'P' and 'planning.org/lbcs' in lb.get('src', {}).get('u', '') and lb.get('adopt') == [],
               "LBCS read at its source (P), linked to APA, adopted nowhere as a rule")
            g3 = RECS.get('green.33300', {}).get('eds', [{}])[0]
            gv = {v['n']: (v['v'], v.get('u')) for v in g3.get('v', [])}
            ck(gv == {'trees': (3, 'trees'), 'canopy': (30, '%'), 'walk': (300, 'm'), 'green_min': (0.5, 'ha')},
               "3-30-300: 3 trees, 30%%, 300 m, a green space of 0.5 ha (%s)" % gv)
            ck(g3.get('src', {}).get('lv') == 'P' and 'doi.org/10.1016/j.scitotenv.2023.167739' in g3.get('src', {}).get('u', ''), "3-30-300 read at its source, Browning et al. (2024)")
            al = RECS.get('app.land', {}).get('eds', [{}])[0]
            av = {v['n']: v['v'] for v in al.get('v', [])}
            ck({k: av.get(k) for k in ('hood', 'mix_n', 'window', 'cell', 'see')} == {'hood': 500, 'mix_n': 8, 'window': 400, 'cell': 100, 'see': 100},
               "the app's land settings: the owner's 500 m neighbourhood and 8 families, the 400 m square, 100 m cells, trees seen within 100 m")
            ck(al.get('src', {}).get('lv') == 'A', "the app's settings said as its own assumption (A)")
            xw = av.get('xw') or {}
            ck(xw.get('tags') == R.XW and xw.get('weak') == R.WEAK, "the crosswalk in the registry is the research's, tag for tag (%d tags)" % len(xw.get('tags') or {}))
            sm = RECS.get('spacematrix', {}).get('eds', [{}])[0]
            ck(sm.get('v') == [] and sm.get('method') == 'spacematrix.2010' and 'doi.org/10.5334/bc.83' in sm.get('src', {}).get('u', ''),
               "Spacematrix: a method with no values, read in Buildings and Cities' box")
            how = {t: (await safe("(t)=>window.__a3dStdEdition(t)", t) or {}).get('how') for t in ('lbcs.activity', 'spacematrix', 'green.33300', 'app.land')}
            ck(how == {'lbcs.activity': 'outside', 'spacematrix': 'international', 'green.33300': 'international', 'app.land': 'assumption'},
               "how each applies: LBCS outside its place, Spacematrix and 3-30-300 anywhere, the settings the app's (%s)" % how)
            ck(await safe("()=>window.__a3dStdSay('green.33300','green_min')") == '0.5 ha' and await safe("()=>window.__a3dStdSay('app.land','mix_n')") == '8 families',
               "the new units in words: 0.5 ha, 8 families")
            await safe("()=>window.__a3dStdCommand()")
            await page.wait_for_timeout(200)
            SG = await safe("""()=>{var b=document.getElementById('a3d-propsbody'),g=b&&b.querySelector('[data-a3dpgrp="Standards"]'),body=g&&g.nextElementSibling;
              return body?{areas:[].map.call(body.querySelectorAll('.a3d-stdarea'),function(e){return e.textContent;}),topics:[].map.call(body.querySelectorAll('[data-stdtopic]'),function(e){return e.getAttribute('data-stdtopic');})}:null;}""") or {}
            ar = SG.get('areas') or []
            # AMENDED FOR V169: Assets (V169) comes between Land and green and Climate
            ck('Land and green' in ar and 'Climate' in ar and ar.index('Land and green') < ar.index('Climate') and all(t in (SG.get('topics') or []) for t in ('lbcs.activity', 'spacematrix', 'green.33300', 'app.land')),
               "Properties, Site, Standards: Land and green before Climate, its four topics listed (%s)" % ar)

            # ---------------------------------------------------------------------------------
            print("\n-- 2. The context")
            q = await safe("()=>window.__a3dCtxQuery()") or ''
            ck('way["landuse"~"^(residential|commercial|retail|industrial|railway|construction|education|institutional|civic_admin|religious|churchyard|cemetery|military|garages|landfill|brownfield|greenfield|farmland|field|farmyard|orchard|vineyard|allotments|plant_nursery|greenhouse_horticulture|aquaculture|quarry|port|school|flowerbed)$"]' in q,
               "the query asks for every land use value the crosswalk reads")
            ck('way["amenity"~"^(school|' in q and '|parking|' in q and 'way["leisure"~"^(playground|pitch|' in q and 'way["tourism"~"^(hotel|' in q,
               "and the grounds of amenities, leisure and tourism")
            kinds = await safe("""()=>[[{type:'way',tags:{amenity:'school'}}],[{type:'way',tags:{leisure:'pitch'}}],[{type:'way',tags:{tourism:'hotel'}}],[{type:'way',tags:{building:'hotel',tourism:'hotel'}}],
              [{type:'node',tags:{amenity:'school'}}],[{type:'way',tags:{amenity:'bench'}}],[{type:'way',tags:{landuse:'farmland'}}],[{type:'way',tags:{landuse:'grass'}}]].map(function(x){return window.__a3dOsmKind(x[0]);})""")
            ck(kinds == ['landuse', 'landuse', 'landuse', 'buildings', '', '', 'landuse', 'green'],
               "a school's or a pitch's grounds and a hotel's are land use; a hotel building a building; a school's point, a bench nothing (%s)" % kinds)
            court = [o for o in (await safe("()=>window.__a3dState().objs") or []) if (o.get('context') or {}).get('id') == FX.COURT[0]]
            hz = court and court[0]['context'].get('holes')
            ck(court and court[0]['context'].get('courtyards') == 1 and hz and len(hz) == 1 and abs(R.area([tuple(p) for p in hz[0]]) - 900) < 0.01,
               "Court House keeps its courtyard's outline (900 m2)")

            L = await safe("()=>window.__a3dLand()") or {}
            ck(not L.get('error') and L.get('S', {}).get('c') == [30, -25] and L.get('W') == {'x0': -170, 'z0': -225, 'x1': 230, 'z1': 175, 'w': 400},
               "the site's centre and the 400 m square around it (%s)" % L.get('W'))

            # ---------------------------------------------------------------------------------
            print("\n-- 3. The crosswalk")
            cases = []
            for tg in R.XW:
                k, v = tg.split('=')
                cases.append(({k: 'anything' if v == '*' else v}, True))
                cases.append(({k: 'anything' if v == '*' else v}, False))
            extra = [({'building': 'yes'}, True), ({'building': 'yes', 'shop': 'no'}, True), ({'shop': 'bakery', 'amenity': 'cafe'}, True),
                     ({'landuse': 'industrial', 'industrial': 'port'}, False), ({'landuse': 'industrial', 'industrial': 'port'}, True),
                     ({'building': 'hotel', 'tourism': 'hotel'}, True), ({'building': 'apartments', 'shop': 'convenience'}, True), ({'landuse': 'grass'}, False),
                     ({'amenity': 'school', 'landuse': 'residential'}, False), ({'natural': 'water'}, False), ({}, False)]
            cases += extra
            got = await safe("(C)=>C.map(function(c){return window.__a3dLandClass(c[0],c[1]);})", [[c[0], c[1]] for c in cases]) or []
            bad = [(cases[i], got[i] if i < len(got) else None, R.classify(cases[i][0], cases[i][1])) for i in range(len(cases))
                   if (got[i] if i < len(got) else 'x') != R.classify(cases[i][0], cases[i][1])]
            ck(len(got) == len(cases) and not bad, "every tag of the table as a building and as an area, and %d cases of the order (%d asked; %s)" % (len(extra), len(cases), bad[:3]))
            ck(got[len(cases) - len(extra) + 3]['c'] == 5000 and got[len(cases) - len(extra) + 5]['c'] == 1000 and got[len(cases) - len(extra) + 2]['tag'] == 'amenity=cafe',
               "a port is movement (LBCS 5520) before industrial; a hotel residential (1200); a building's amenity read before its shop")

            # ---------------------------------------------------------------------------------
            print("\n-- 4. Land use")
            mx = L.get('mix') or {}
            rm = R.mix(A, B)
            app_cnt = {str(s['c']): s['n'] for s in mx.get('sh', [])}
            ck(app_cnt == {str(c): n for c, n in rm['cnt'].items()} and mx.get('none') == rm['none'] and mx.get('un') == rm['un'] and mx.get('tot') == 6400,
               "every 5 m cell of the square in the reference's family: %s, none %s, unsaid %s" % (app_cnt, mx.get('none'), mx.get('un')))
            ck(near(mx.get('H'), rm['H'], 1e-9) and near(mx.get('ix'), rm['ix'], 1e-9) and mx.get('N') == 8,
               "Shannon's H %.4f and the index over 8 families %.4f, as the reference" % (rm['H'], rm['ix']))
            pts = [(-135, -185), (-102.5, -125), (-160, 130), (-50, -185), (-122.5, -122.5), (10, -190), (90, 130), (160, -190), (130, -110), (-30, 120), (170, 40), (200, 140), (-140, -60), (-127.5, -150), (-40, -120), (140, -20), (110, 0)]
            want = [4000, 1000, 9000, 1000, 2000, 2000, 0, 5000, 3000, 6000, 5000, 8000, 4000, 1000, 2000, 0, 1000]
            cells = await safe("(P)=>window.__a3dLandCell(P)", [list(p) for p in pts]) or []
            ck(cells == want, "the cases by name: a school in homes, grass in homes, grass alone, a hotel, a bakery, a building with no use, a courtyard, a port, works, worship, a car park, farmland, a supermarket over a smaller car park, homes round a hole (%s)" % cells)
            ck(cells and cells[7] == 5000 and cells[1] == 1000, "the port's ground is movement, not industrial; the grass inside the homes residential")
            LU = by_k(await diags('landuse'))
            light = True
            for i, t, pts_ in FX.AREAS[:12]:
                a = [x for x in A if x['key'].endswith(':way:' + str(i))][0]
                o = LU.get('area:' + a['key'])
                if not a['cls'] or not o:
                    ck(False, "the area %s drawn" % i)
                    continue
                c = a['cls']['c']
                b0 = o['dg']['g']['bands'][0]
                ok = b0['col'] == LT[c][0] and o['dg']['s']['stroke'] == LT[c][1] and (b0.get('tex') or None) == TEX.get(c) and bool(o['dg']['lb']) == (a['area'] >= 2000)
                if not ok:
                    ck(False, "area %s: fill %s, outline %s, texture %s, label %s" % (i, b0['col'], o['dg']['s']['stroke'], b0.get('tex'), bool(o['dg']['lb'])))
                    light = False
            ck(light, "every area in its family's colour on the light map, outlined, the textures where colours sit close, named when 2000 m2 or more")
            ck('area:green:way:8113' not in LU and 'area:green:way:8114' not in LU, "the woods and forest outside the square not drawn by land use")
            b1, b2 = LU.get('bld:1000'), LU.get('bld:2000')
            ck(b1 and b2 and len(b1['dg']['g']['lines']) == 2 and len(b2['dg']['g']['lines']) == 4 and b1['dg']['s'].get('fillOver') == LT[1000][0] and b2['dg']['s'].get('fillOver') == LT[2000][0],
               "the buildings with a use of their own, filled in their family's colour: the hotel and Court House residential, the bakery, the office, the kiosk and the supermarket commercial")
            ck(b1 and abs(b1['dg']['g']['lines'][0][0][1] - (L['S']['y'] + 0.03 + 15)) < 1e-6, "a building's lid at its height (the hotel's 15 m)")
            fams = [r['short'] for r in (await safe("()=>(window.__a3dDgState().runs.landuse||{}).legend") or [])]
            ck(fams == ['Residential', 'Commercial', 'Industrial', 'Institutional', 'Movement', 'Assembly', 'Leisure', 'Natural resources', 'No activity'],
               "the key: the nine families drawn, in LBCS's order (%s)" % fams)
            leg = (await safe("()=>(window.__a3dDgState().runs.landuse||{}).legend") or [])
            ck([r.get('tex') for r in leg if r.get('tex')] == ['45', '135', 'dot'], "the key carries the textures too")
            wl = LU.get('window', {}).get('dg', {}).get('lb', [{}])[0].get('t', '')
            ck(wl == 'Land use mix %s over 8 families' % ('%.2f' % rm['ix']).rstrip('0').rstrip('.'), "the square labelled with the mix (%s)" % wl)
            await safe("()=>window.__a3dMapSet('style','off')")
            await safe("()=>window.__a3dDgRun('landuse')")
            LU2 = by_k(await diags('landuse'))
            o = LU2.get('area:landuse:way:8106')
            ck(o and o['dg']['g']['bands'][0]['col'] == DK[3000][0] and o['dg']['s']['stroke'] == DK[3000][1], "on the dark plan the dark plan's steps (industrial %s)" % (o and o['dg']['g']['bands'][0]['col']))

            # ---------------------------------------------------------------------------------
            print("\n-- 5. Figure-ground")
            F = L.get('form') or {}
            rf = R.form(B, *W)
            ck(near(F.get('gsi'), rf['gsi']) and near(F.get('fsi'), rf['fsi']) and near(F.get('osr'), rf['osr']) and near(F.get('l'), rf['l']) and F.get('n') == rf['n'],
               "Spacematrix for the square: GSI %.4f, FSI %.4f, OSR %.4f, L %.3f, as the reference" % (rf['gsi'], rf['fsi'], rf['osr'], rf['l']))
            bs = {b['name']: b for b in L.get('buildings', [])}
            ck(bs.get('Office Five', {}).get('s') == 5 and bs.get('Office Five', {}).get('from') == 'levels', "Office Five: 5 storeys from building:levels, not 6 from its 20 m")
            ck(bs.get('Kiosk', {}).get('s') == 1 and bs.get('Kiosk', {}).get('from') == 'height', "the kiosk, 2.5 m tall: one storey, not none")
            parts = [b for b in L.get('buildings', []) if b['whole'] == 'way:8301']
            ck(len(parts) == 2 and sorted((p['s'], p['ground']) for p in parts) == [(3, False), (4, True)],
               "Part House's parts: 4 storeys on the ground; 5 levels from the second, 3, standing at 6 m: its floors count, its ground does not")
            ck(near(bs.get('Court House', {}).get('area'), 2700, 1e-9), "Court House covers 2700 m2: its courtyard is not built on")
            FG = by_k(await diags('figure'))
            cells_ok = 0
            for i in range(4):
                for j in range(4):
                    x0, z0 = W[0] + i * 100, W[1] + j * 100
                    rc = R.form(B, x0, z0, x0 + 100, z0 + 100)
                    o = FG.get('cell:%d,%d' % (i, j))
                    rw = rows(o) if o else {}
                    if o and rw.get('GSI, the ground covered') == ('%.3f' % rc['gsi']).rstrip('0').rstrip('.') and rw.get('FSI, the floor area over the land') == ('%.3f' % rc['fsi']).rstrip('0').rstrip('.'):
                        cells_ok += 1
            ck(cells_ok == 16, "each of the 16 cells, 100 m across, with its GSI and FSI as the reference (%d)" % cells_ok)
            gr, rg = L.get('grain') or {}, R.grain(B)
            ck(gr.get('n') == rg['n'] and near(gr.get('mean'), rg['mean']) and gr.get('lev') == rg['lev'] and gr.get('hgt') == rg['hgt'],
               "the grain: %d buildings (Part House once), %.1f m2 a footprint, storeys from levels for %d and heights for %d" % (rg['n'], rg['mean'], rg['lev'], rg['hgt']))
            ck(FG.get('ground') and FG['ground']['dg']['g']['bands'][0]['rings'][0][0][0] == -170 and FG.get('figure', {}).get('dg', {}).get('s', {}).get('fillOver') == '#1d2329',
               "the open ground over the square, the buildings filled")
            sl = FG.get('site', {}).get('dg', {}).get('lb', [{}])[0].get('t', '')
            ck(sl.startswith('GSI %s, FSI %s' % (('%.2f' % rf['gsi']).rstrip('0').rstrip('.'), ('%.2f' % rf['fsi']).rstrip('0').rstrip('.'))), "the square labelled with its density (%s)" % sl)
            ck("the book, which was not read" in rows(FG['site']).get("Spacematrix's type", ''), "Spacematrix's type not given: its bounds are in the book, not read")

            # ---------------------------------------------------------------------------------
            print("\n-- 6. Green and trees")
            cp, rcn = L.get('canopy') or {}, R.canopy(T, A, re=RE)
            ck(cp.get('cells') == rcn['cells'] and cp.get('can') == rcn['can'] and cp.get('clipped') is True and near(cp.get('full'), rcn['full']),
               "the canopy: %d of %d 2 m cells under a crown or in a wood, cut to the context's square (whole to %d m), as the reference (%s of %s)" % (rcn['can'], rcn['cells'], rcn['full'], cp.get('can'), cp.get('cells')))
            got_seen = sorted(x['name'] for x in (L.get('seen') or {}).get('list', []))
            want_seen = sorted('Tree %d' % (k + 1) for k in R.seen(B, T))
            ck(got_seen == want_seen and 'Tree 5' not in got_seen and 'Tree 6' not in got_seen and 'Tree 4' in got_seen,
               "the trees seen: %s; the one behind East Hall and the one 150 m off, on a clear line, not" % got_seen)
            G = {g['name']: g for g in L.get('greens', [])}
            ck(set(G) == {'Mill Park', 'Small Garden'} and G['Mill Park']['big'] is True and G['Small Garden']['big'] is False,
               "the public green spaces: Mill Park (0.63 ha); Small Garden under 0.5 ha; the private park left out")
            ACC = (await safe("()=>window.__a3dAcc()") or {}).get('access') or {}
            segs, v = ACC.get('segs') or [], ACC.get('speed')
            ra = {nm: R.walk_to(segs, v, [x for x in A if x['name'] == nm][0]) for nm in ('Mill Park', 'Small Garden')}
            ck(all(G[nm]['walk'] and near(G[nm]['walk']['d'], ra[nm], 1e-9) for nm in ra), "the walks along the streets: Mill Park %.1f m, Small Garden %.1f m, as the reference" % (ra['Mill Park'], ra['Small Garden']))
            ck((L.get('best') or {}).get('key') == 'green:way:5001' and ra['Small Garden'] < ra['Mill Park'], "the nearest of 0.5 ha or more is Mill Park, though the small garden is nearer")
            tl = [l for l in (await safe("()=>window.__a3dLayers()") or []) if l['name'] == 'Context trees']
            await safe("(id)=>window.__a3dLayerSet(id,'visible',false)", tl[0]['id'] if tl else '')
            nh = ((await safe("()=>window.__a3dLand()") or {}).get('seen') or {}).get('n')
            await safe("(id)=>window.__a3dLayerSet(id,'visible',true)", tl[0]['id'] if tl else '')
            ck(tl and nh == len(want_seen), "the trees seen counted with their layer hidden too: a layer shown is a view, not the ground (%s)" % nh)
            ok = [len(want_seen) >= 3, rcn['share'] * 100 >= 30, ra['Mill Park'] <= 300]
            ck(L.get('ok') == ok, "3-30-300: %s" % ok)
            GR = by_k(await diags('green'))
            ck(len(GR.get('crowns', {}).get('dg', {}).get('g', {}).get('bands', [])) == 6 and 'wood:green:way:8113' in GR and 'wood:green:way:8114' in GR and GR['wood:green:way:8113']['dg']['g']['bands'][0].get('tex') == 'dot',
               "drawn: six crowns, the wood and the forest dotted")
            ck('green:green:way:5001' in GR and 'green:green:way:8115' in GR and 'green:green:way:8116' not in GR and GR['green:green:way:8115']['dg']['s'].get('dash'),
               "the green spaces drawn, the small one dashed, the private one not")
            ck(len(GR.get('seen', {}).get('dg', {}).get('g', {}).get('pts', [])) == 2 * len(want_seen), "a sight line to each tree seen")
            ck(GR.get('site', {}).get('dg', {}).get('lb', [{}])[0].get('t') == '3-30-300: %d of 3 met' % sum(ok), "the site labelled: %d of 3 met" % sum(ok))
            hr = rows(GR['hood'])
            ck('cut to the context' in hr.get('Counted in', '') and GR['hood']['dg']['g']['closed'], "the neighbourhood's circle, said cut to the context's square")

            # ---------------------------------------------------------------------------------
            print("\n-- 7. Zoning around")
            ZR = by_k(await diags('zoning'))
            ck(not ZR and 'No council layer loaded' in ((await safe("()=>window.__a3dDgState().runs.zoning") or {}).get('note') or ''), "no layer loaded: nothing drawn, and it says so")
            ad = await safe("(u)=>window.__a3dDataAdd(u,'Zoning','#e0b85e','Example Council')", FX.ZN_URL) or {}
            fr = ad.get('result') or {}
            ck(fr.get('count') == 3, "the council's layer: its three districts around the site (%s)" % fr)
            nh0 = len([h for h in ST.get('hits', []) if h[0] == 'zn' and 'f=json' in h[1]])
            await analyze()
            nh1 = len([h for h in ST.get('hits', []) if h[0] == 'zn' and 'f=json' in h[1]])
            DLs = await safe("()=>window.__a3dDataLayers()") or []
            dr = (DLs[0] if DLs else {}).get('drawing') or {}
            ck(nh0 == 0 and nh1 == 1, "Analyze site asks for the layer's description once (%d, %d)" % (nh0, nh1))
            vv = {x[0]: x[1:] for x in dr.get('v', [])}
            ck(dr.get('f') == ['ZONE'] and dr.get('d') == ', ' and vv.get('R6') == ['Residence R6', R.rgba([255, 255, 0, 255], 20), R.rgba([120, 120, 0, 255], 20)] and
               vv.get('C4') == ['Commercial C4', R.rgba([255, 0, 0, 204], 20), None] and vv.get('M1') == ['Manufacturing M1', None, R.rgba([80, 16, 120, 255], 20)] and
               dr.get('def') == ['Other', R.rgba([200, 200, 200, 255], 20), R.rgba([110, 110, 110, 255], 20)],
               "its renderer read as Esri's code reads it: the solid fills, the alpha and the 20%% transparency, a null outline, a hatch left out, the default")
            L2 = await safe("()=>window.__a3dLand()") or {}
            zn, rz = L2.get('zn') or {}, R.zoning()
            ck(zn.get('lot') == 'R6' and zn.get('order') == rz['order'] and all(near(zn['by'][k] / zn['tot'], rz['share'][k], 1e-9) for k in rz['share']),
               "the site in R6; the zoned ground in the square: %s" % {k: round(v, 3) for k, v in rz['share'].items()})
            ZR = by_k(await diags('zoning'))
            z0, z1, z2 = ZR.get('zone:0'), ZR.get('zone:1'), ZR.get('zone:2')
            ck(z0 and z0['dg']['g']['bands'][0]['col'] == vv['R6'][1] and z0['dg']['s']['stroke'] == vv['R6'][2] and z0['dg']['s']['w'] == 2.2,
               "R6 in the layer's own yellow, its outline, heavier: the site is in it")
            ck(z1 and z1['dg']['g']['bands'][0]['col'] == vv['C4'][1] and z1['dg']['s']['stroke'] != vv['C4'][1] and z2 and z2['dg']['g']['bands'][0]['col'] in ('#9aa7b4', '#7d8794') and z2['dg']['s']['stroke'] == vv['M1'][2],
               "C4 with no outline of its own takes the app's; M1's hatch is not drawn: the app's neutral fill, its own outline")
            ck(ZR.get('site', {}).get('dg', {}).get('lb', [{}])[0].get('t') == 'Site: R6', "the site labelled with its district")
            await safe("()=>window.__a3dDgRun('zoning')")
            await analyze()
            ck(len([h for h in ST.get('hits', []) if h[0] == 'zn' and 'f=json' in h[1]]) == 1, "the colours kept with the layer: the layer run again and Analyze site again, not asked again")
            P = await safe("""()=>{var R=window.__a3dZnDrawing,S=window.__a3dZnStyleOf,
              a=R({drawingInfo:{renderer:{type:'uniqueValue',field1:'ZONE',field2:'OVL',fieldDelimiter:'/',uniqueValueInfos:[{value:'R6/C1',label:'R6 with C1',symbol:{type:'esriSFS',style:'esriSFSSolid',color:[1,2,3,255]}}]}}}),
              b=R({drawingInfo:{renderer:{type:'classBreaks',field:'FAR'}}}),c=R({drawingInfo:{renderer:{type:'simple',symbol:{type:'esriSFS',color:[9,9,9,128]}}}}),d=R({name:'x'}),
              e=R({drawingInfo:{renderer:{type:'uniqueValue',field1:'CODE',uniqueValueInfos:[{value:'2',symbol:{type:'esriSFS',color:[5,5,5,255]}}]}}});
              return [S(a,{ZONE:'R6',OVL:'C1'}),b.none||'',S(c,{}),d.none||'',S(e,{CODE:2}),S(a,{ZONE:'R6',OVL:'C2'})];}""") or []
            ck(len(P) == 6 and P[0] and P[0]['f'] == 'rgba(1,2,3,1)' and 'not read' in P[1] and P[2]['f'] == 'rgba(9,9,9,0.502)' and P[3] == 'gives no colours' and P[4]['f'] == 'rgba(5,5,5,1)' and P[5] is None,
               "Esri's renderers case by case: two fields joined by the delimiter, class breaks named and not read, a simple renderer, none, a number matched loosely (%s)" % P)

            # ---------------------------------------------------------------------------------
            print("\n-- 8. Findings and rows")
            f1, f2, f3, f4 = [await finding(a) for a in ('location.landuse', 'location.density', 'ecology.33300', 'legal.zoningaround')]
            top = sorted(rm['sh'], key=lambda s: -s[1])[0]
            nm = {1000: 'residential', 2000: 'commercial', 3000: 'industrial', 4000: 'institutional', 5000: 'movement', 6000: 'assembly', 7000: 'leisure', 8000: 'natural resources'}
            pct = ('%.1f' % (top[2] * 100)).rstrip('0').rstrip('.') + '%'
            ck(f1 and f1['cat'] == 'location' and ('by area: %s %s' % (nm[top[0]], pct)) in f1['value'] and ('the mix %s' % ('%.2f' % rm['ix']).rstrip('0').rstrip('.')) in f1['value'],
               "the land use finding: the largest share first (%s %s), the mix" % (nm[top[0]], pct))
            ck(f2 and f2['cat'] == 'location' and ('GSI %s' % ('%.2f' % rf['gsi']).rstrip('0').rstrip('.')) in f2['value'] and 'from the height at 3 m a storey' in f2['value'],
               "the density finding: GSI, FSI, OSR, the storeys, the grain")
            ck(f3 and f3['cat'] == 'ecology' and f3['value'].startswith('%d of 3 met.' % sum(ok)) and 'Mill Park' in f3['value'] and ('%d m along the streets' % round(ra['Mill Park'])) in f3['value'],
               "the 3-30-300 finding: %d of 3, Mill Park %d m along the streets" % (sum(ok), round(ra['Mill Park'])))
            ck(f4 and f4['cat'] == 'legal' and f4['value'].startswith('The site is in district R6;'), "the zoning around: the site's district and the shares")
            sx = await safe("()=>['location.landuse','location.density','ecology.33300','legal.zoningaround'].map(window.__a3dSaStdText)") or []
            ck(len(sx) == 4 and 'Land-Based Classification Standards' in sx[0] and 'Spacematrix' in sx[1] and '3-30-300' in sx[2] and 'Land use, form and green' in sx[3],
               "each finding names its standards")
            await safe("()=>window.__a3dTestClearUndo()")
            await safe("()=>window.__a3dStdOverride('green.33300','walk',200,'a stricter test')")
            f3b = await finding('ecology.33300')
            ck(f3b and f3b['value'].startswith('%d of 3 met.' % (sum(ok) - 1)) and '200 m asked' in f3b['value'], "the walk overridden to 200 m: the finding works out again, one fewer met")
            chg = await safe("()=>window.__a3dDgStdChanged('green')") or {}
            ck(len(chg.get('run', [])) == 1, "and the green layer is out of date, Run again")
            await safe("()=>window.__a3dStdClear('green.33300','walk')")
            await safe("()=>window.__a3dStdOverride('green.33300','green_min',0.49,'the garden counts')")
            L3 = await safe("()=>window.__a3dLand()") or {}
            ck((L3.get('best') or {}).get('key') == 'green:way:8115' and near(L3['best']['d'], ra['Small Garden'], 1e-9), "the smallest green space overridden to 0.49 ha: the nearer garden counts")
            await safe("()=>window.__a3dStdClear('green.33300','green_min')")
            await safe("(n)=>window.__a3dStdOverride('green.33300','trees',n,'as many as are seen')", len(want_seen))
            ok4 = (await safe("()=>window.__a3dLand()") or {}).get('ok') or [None]
            ck(ok4[0] is True, "the edge: as many trees asked as are seen (%d), met: at least, not more than" % len(want_seen))
            await safe("()=>window.__a3dStdClear('green.33300','trees')")
            await safe("()=>window.__a3dStdOverride('app.land','mix_n',4,'four families')")
            L4 = await safe("()=>window.__a3dLand()") or {}
            ck(near((L4.get('mix') or {}).get('ix'), rm['H'] / math.log(4), 1e-9), "the mix over 4 families: H over ln 4")
            await safe("()=>window.__a3dStdClear('app.land','mix_n')")
            cats = {c['id']: c['group'] for c in (await safe("()=>window.__a3dAnzCats()") or [])}
            ck(cats.get('dglanduse') == 'location' and cats.get('dgfigure') == 'location' and cats.get('dggreen') == 'ecology' and cats.get('dgzoning') == 'legal',
               "the rows in their categories: land use and figure-ground in Location, green in Ecology, zoning in Legal")
            lys = {l['name']: l for l in (await safe("()=>window.__a3dLayers()") or [])}
            ck(lys.get('Site analysis - Land use', {}).get('visible') is False and lys.get('Site analysis - Figure-ground', {}).get('visible') is False and
               lys.get('Site analysis - Zoning around', {}).get('visible') is False and lys.get('Site analysis - Green and trees', {}).get('visible') is not False,
               "land use, the figure-ground and the zoning cover the ground and start hidden; green and trees shown")

            # ---------------------------------------------------------------------------------
            print("\n-- 9. On screen")
            await safe("()=>window.__a3dMapSet('style','off')")
            await safe("""()=>{var L=window.__a3dLayers();L.forEach(function(l){if(/^Site analysis - /.test(l.name))window.__a3dLayerSet(l.id,'visible',l.name==='Site analysis - Land use');});
              window.__a3dDgRun('landuse');window.__a3dSetPlanView();window.__a3dCamSet({tx:30,tz:-160,dist:260});}""")
            await page.wait_for_timeout(600)
            spread = "(p)=>{var s=window.__a3dDgToScreen(p),c=document.getElementById('a3d-canvas'),r=window.devicePixelRatio||1,d=c.getContext('2d').getImageData(Math.round(s[0]*r)-6,Math.round(s[1]*r)-6,13,13).data,lo=1e9,hi=-1,i;for(i=0;i<d.length;i+=4){var v=d[i]+d[i+1]+d[i+2];if(v<lo)lo=v;if(v>hi)hi=v;}return hi-lo;}"
            s_ind = await safe(spread, [110, 0, -145])
            s_res = await safe(spread, [-150, 0, -130])
            ck(s_ind is not None and s_res is not None and s_ind > s_res + 60, "on the plan the industrial area is hatched, the residential plain (spread %s against %s)" % (s_ind, s_res))
            lg = [b for b in ((await safe("()=>window.__a3dDgLegend()") or {}).get('blocks') or []) if b.get('title') == 'Land use']
            ck(lg and len(lg[0].get('rows', [])) == 9, "the key on the view: the nine families (%s)" % (lg and lg[0].get('rows')))
            await safe("""()=>{var L=window.__a3dLayers();L.forEach(function(l){if(/^Site analysis - /.test(l.name))window.__a3dLayerSet(l.id,'visible',l.name==='Site analysis - Figure-ground');});
              window.__a3dDgRun('figure');window.__a3dCamSet({tx:125,tz:-75,dist:120});}""")
            await page.wait_for_timeout(600)
            lum = await safe("(p)=>{var s=window.__a3dDgToScreen(p),c=document.getElementById('a3d-canvas'),r=window.devicePixelRatio||1,d=c.getContext('2d').getImageData(Math.round(s[0]*r)-3,Math.round(s[1]*r)-3,7,7).data,t=0,i;for(i=0;i<d.length;i+=4)t+=d[i]+d[i+1]+d[i+2];return t/(d.length/4);}", [125, 0, -75])
            ck(lum is not None and lum < 150, "the figure-ground: Office Five filled dark over the model (%s)" % lum)
            css = await safe("()=>window.__a3dDgTexCss('45','rgba(1,2,3,0.5)')") or ''
            ck('repeating-linear-gradient(45deg,rgba(1,2,3,0.5) 0 1px' in css, "the key's texture in Analyze's rows, as CSS")
            await safe("()=>{window.__a3dAnzView(true);window.__a3dAnzOpenAll(true);}")
            await page.wait_for_timeout(300)
            html = await safe("()=>{var e=document.querySelector('[data-anzcard=\"dglanduse\"]');return e?e.outerHTML:'';}") or ''
            ck('repeating-linear-gradient(45deg' in html and 'radial-gradient(' in html, "the land use row's key shows the industrial hatch and the natural resources' dots")
            ck(not errs, "no page errors (%s)" % errs[:2])

            # a project fetched before V168: the courtyard's outline not kept
            await safe("""()=>{var o=window.__a3dState().objs;o.forEach(function(x){if(x.context&&x.context.id===%d)delete x.context.holes;});window.__a3dTestSetObjs(o);}""" % FX.COURT[0])
            L5 = await safe("()=>window.__a3dLand()") or {}
            ck((L5.get('grain') or {}).get('yards') == 1 and near(({b['name']: b for b in L5.get('buildings', [])}.get('Court House') or {}).get('area'), 3600, 1e-9),
               "a building fetched before V168: its courtyard counted as built, and said")
            f2b = await finding('location.density')
            ck(f2b and 'fetched before V168 with courtyards counted as built' in f2b['value'], "the density finding says so")

            # a reload keeps it all
            await page.evaluate("()=>window.dispatchEvent(new Event('beforeunload'))")
            await page.wait_for_timeout(400)
            await page.reload()
            await page.wait_for_timeout(2500)
            await safe("()=>window.__a3dEnter()")
            DL2 = await safe("()=>window.__a3dDataLayers()") or []
            ck(DL2 and (DL2[0].get('drawing') or {}).get('f') == ['ZONE'] and len(await diags('landuse')) > 5, "a reload keeps the layer's colours and the drawings")
            await ctx.close()

            # ---------------------------------------------------------------------------------
            print("\n-- A layer with no colours, one that fails")
            for mode, want in (('nodraw', 'gives no colours'), ('fail', None)):
                S2 = {'zn': mode}
                c2, p2, e2 = await fresh(S2)
                W2 = []
                p2.on('console', lambda m: W2.append(m.text) if m.type == 'warning' and 'colours of' in m.text else None)
                await analyze(p2)
                await safe("(u)=>window.__a3dDataAdd(u,'Zoning','#e0b85e','Example Council')", FX.ZN_URL, pg=p2)
                await analyze(p2)
                toast = await safe("()=>(document.getElementById('a3d-toast')||{}).textContent||''", pg=p2) or ''
                d2 = ((await safe("()=>window.__a3dDataLayers()", pg=p2) or [{}])[0]).get('drawing')
                note = ((await safe("()=>window.__a3dDgState().runs.zoning", pg=p2)) or {}).get('note', '')
                Z2 = by_k(await diags('zoning', pg=p2))
                if mode == 'nodraw':
                    ck(d2 and d2.get('none') == want and 'its districts outlined and named' in note and Z2.get('zone:0', {}).get('dg', {}).get('s', {}).get('fop') == 0.18,
                       "a layer with no renderer: kept as none, its districts outlined and named in a light neutral (%s)" % note)
                else:
                    ck(d2 is None and 'read by Analyze site' in note and len(Z2) == 4, "its description failing: districts drawn in the app's colours, asked again next time (%s)" % note)
                    ck(any('The colours of Zoning could not be read' in w for w in W2) and 'Zoning: its own colours could not be read (gis.example-council.gov answered HTTP 500)' in toast,
                       "the failure named, and warned (%s)" % toast.replace('\n', ' / ')[:160])
                await c2.close()

            # ---------------------------------------------------------------------------------
            print("\n-- A phone and a tablet")
            for vw, mob, nm in (((390, 844), True, 'a phone'), ((820, 1180), True, 'a tablet')):
                S3 = {}
                c3, p3, e3 = await fresh(S3, vw=vw, mobile=mob)
                await analyze(p3)
                n3 = len(await diags('landuse', pg=p3)) + len(await diags('green', pg=p3))
                cats3 = {c['id']: c['group'] for c in (await safe("()=>window.__a3dAnzCats()", pg=p3) or [])}
                ck(n3 > 10 and cats3.get('dggreen') == 'ecology' and not e3, "on %s: drawn, and the rows in their categories" % nm)
                await c3.close()

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
