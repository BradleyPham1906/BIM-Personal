#!/usr/bin/env python3
"""bim_phase171c_one_analyze_browser_tests.py -- V171c: one Analyze.

The owner: "The analyze should be combined with the site analysis. It should not be two separate hubs." Analyze and
the analysis workspace are one place: its tab opens it and leaving the tab leaves it. The left is one list -- the site
and Analyze site, Overview, the ten categories with the analyses that answer each, the model's own -- and the words are
on the right: the overview, a category with what was found and its data, an analysis with what it found, one of the
model's analyses with its settings. Every service is answered in the browser by tests/traffic_fixture.py.

  1. THE RECORDS: the marker, the version, the old hub's hooks gone.
  2. THE TAB: Analyze opens it and another tab leaves it; the cross goes back to the tab it came from, the drawer as it was.
  3. THE LIST BEFORE A RUN: the site's part, Overview, the ten categories in order with their analyses, Model; no row
     opens in place.
  4. ANALYZE SITE: its progress in the list and in the overview's steps as they come; the overview after it: the site,
     the counts, every category's findings, the red flags first.
  5. A CATEGORY: its question, what was found, its analyses, its data and its link; a pick is no undo step and draws
     nothing; the zoning's fields typed in.
  6. AN ANALYSIS: what it found, the category it answers, what changed since it ran.
  7. ONE OF THE MODEL'S: its state, its settings and its buttons; a floor load typed, refused; Add as layer.
  8. PROPERTIES FROM A BUTTON: the model's Properties with a way back; USAGES.
  9. A PICK OVER A SELECTION: the panel shows the pick, the selection kept for the buttons that act on it.
 10. THE SEARCH: by a category's words and its findings, by a row's words, its settings and its buttons.
 11. THE LOOK: a pick in the mode's colours; the cars in the mode's, what is drawn in the map's.
 12. A PHONE: a category opens as a sheet, an analysis shows the view.

The harness never waits without a bound (V123).
"""
import asyncio, pathlib, re, sys, traceback

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from bim_phase133_site_context_browser_tests import Checks, Stalled, within   # noqa: E402
import traffic_fixture as FX   # noqa: E402
from playwright.async_api import async_playwright   # noqa: E402

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'
CK = Checks()
SC = 0.35
LOT = [list(p) for p in FX.LOT]
MASSES = [(20, -25, 18, 28, 31, 'use-res'), (40, -25, 18, 28, 18, 'use-off'), (30, -15, 38, 8, 4.5, 'use-ret'), (30, -35, 38, 8, 16, 'use-hot')]
CATS = [('location', 'Location and context', ['frame', 'landuse', 'figure'], []), ('legal', 'Legal and regulatory', ['zoning'], []),
        ('landform', 'Landform', ['contours', 'slope', 'aspect'], ['survey', 'terrain', 'grading']), ('water', 'Water', ['flow', 'ponds', 'flood'], ['rain']),
        ('climate', 'Climate', ['sun', 'shadow', 'wind'], ['sun', 'sunhours', 'solar']), ('ecology', 'Ecology', ['green'], []),
        ('risk', 'Environmental risk', ['noise'], []), ('access', 'Access and circulation', ['streets', 'cycling', 'transit', 'walk', 'vehicles', 'traffic'], []),
        ('utilities', 'Utilities', [], []), ('people', 'People and place', ['views', 'needs'], [])]
MODEL = ['lens', 'areas', 'lod', 'stats', 'structure']
LIGHT_AR = '#9e4313'   # V166's arterial on a light map (bim_phase166's LIGHT)


async def run():
    ck = CK
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()

        async def page_for(vp, mobile=False):
            ctx = await browser.new_context(viewport=vp, is_mobile=mobile, has_touch=mobile, device_scale_factor=2 if mobile else 1)
            ST = {'tr': ()}
            for h in FX.HOSTS:
                await ctx.route(h, FX.route_handler(ST))
            for h in ('https://server.arcgisonline.com/**', 'https://tile.openstreetmap.org/**', 'https://*.tile.openstreetmap.org/**'):
                await ctx.route(h, lambda r: r.abort())
            pg = await ctx.new_page()
            pg.errs = []
            pg.on('pageerror', lambda e: pg.errs.append(str(e)))
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

        async def aw(pg=None):
            return await safe("()=>window.__a3dAw()", pg=pg) or {}

        async def click(sel, pg=None):
            return await safe("(s)=>{var b=document.querySelector(s);if(!b)return false;b.click();return true;}", sel, pg=pg)

        async def text(sel, pg=None):
            return await safe("(s)=>{var e=document.querySelector(s);return e?e.textContent.replace(/\\s+/g,' ').trim():null;}", sel, pg=pg)

        async def texts(sel, pg=None):
            return await safe("(s)=>[].map.call(document.querySelectorAll(s),function(e){return e.textContent.replace(/\\s+/g,' ').trim();})", sel, pg=pg) or []

        async def tab(t, pg=None):
            await click('#a3d-rail .a3d-railbtn[data-tab="%s"]' % t, pg=pg)
            await (pg or page).wait_for_timeout(200)

        async def findings(pg=None):
            return [f for f in ((await safe("()=>window.__a3dSa()", pg=pg)) or {}).get('findings', []) if f.get('auto')]

        async def design(pg=None):
            pg = pg or page
            await safe("""(a)=>{var o=window.__a3dState().objs.filter(function(x){return x.t!=='property'&&x.id!=='LOT'&&x.t!=='box';});
              o.push({id:'LOT',t:'sketch',name:'Lot',col:'#5ec4b8',pos:[0,0,0],pts:a,y:0,closed:true,layer:'layer-0'});
              window.__a3dTestSetObjs(o);window.__a3dPropertyFromSketch('LOT');}""", LOT, pg=pg)
            for (x, z, w, d, h, u) in MASSES:
                bid = await safe("(a)=>window.__a3dAdd('box',{Length:a[0],Width:a[1],Height:a[2]}).id", [w / SC, d / SC, h / SC], pg=pg)
                await safe("(a)=>{var L=window.__a3dState().objs;L.forEach(function(o){if(o.id===a[0])o.pos=[a[1],a[2],a[3]];});window.__a3dTestSetObjs(L);}", [bid, x, h / 2, z], pg=pg)
                await safe("(a)=>window.__a3dUsageAssign([a[0]],a[1])", [bid, u], pg=pg)
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dRefreshProps();}", pg=pg)

        async def analyse(pg=None, watch=None):
            pg = pg or page
            await safe("()=>window.__a3dAnzView(true)", pg=pg)
            await pg.wait_for_timeout(300)
            if await safe("()=>!!document.querySelector('.a3d-awl [data-saaddr]')", pg=pg):
                await pg.fill('.a3d-awl [data-saaddr]', '1 Market Street')
                await pg.press('.a3d-awl [data-saaddr]', 'Enter')
            else:
                await click('.a3d-awl [data-saact="analyze"]', pg=pg)
            for _ in range(240):
                s = await safe("()=>window.__a3dSiteRunState()", pg=pg) or {}
                if not s.get('busy'):
                    return s
                if watch is not None:
                    w = await safe("""()=>({run:(document.querySelector('.a3d-awl-run')||{}).textContent,
                      steps:[].map.call(document.querySelectorAll('#a3d-propsbody [data-awpanel="overview"] [data-sastep]'),function(l){return l.className;})})""", pg=pg) or {}
                    watch.append(w)
                await pg.wait_for_timeout(120)
            raise Stalled('the run did not end')

        try:
            await within(page.goto('file://' + str(HTML)), 'goto')
            await page.wait_for_timeout(2300)
            await safe("()=>window.__a3dEnter()")

            # ---------------------------------------------------------------------------------
            print("\n-- 1. The records")
            mk = await safe("()=>window.__acad3dV171c") or ''
            ck(all(w in mk for w in ('oneanalyze', 'tab', 'categories', 'findings', 'card', 'props', 'search', 'phone')), "the V171c marker (%s)" % mk)
            ck(bool(await safe("()=>window.__acad3dV171b")), "V171b's marker kept: the workspace is V171b's, Analyze now")
            mv = re.search(r"var BIM_APP_VERSION=\{v:'V(\d+)'", HTML.read_text(encoding='utf-8'))
            ck(mv and int(mv.group(1)) >= 171, "the app says V171 or later: a sub-phase keeps its phase's number (%s)" % (mv and mv.group(1)))
            gone = await safe("()=>['__a3dAnzToggle','__a3dAnzOpenAll','__a3dAwGroups'].filter(function(k){return typeof window[k]!=='undefined';})")
            ck(gone == [], "the old hub's hooks are gone: no row to open, no six groups (%s)" % gone)

            # ---------------------------------------------------------------------------------
            print("\n-- 2. The tab")
            await tab('assets')
            ck((await aw()).get('on') is False, "(Assets: not in Analyze)")
            await tab('analyze')
            a0 = await aw()
            ck(a0.get('on') is True and a0.get('tab') == 'analyze' and a0.get('prev') == 'assets', "Analyze's tab opens it, from Assets (%s)" % {k: a0.get(k) for k in ('on', 'tab', 'prev')})
            ck(await safe("()=>document.body.classList.contains('a3d-aw')&&!!document.getElementById('a3d-awbar')") and a0.get('look') == 'dark',
               "the bar over the view, the view quiet in the mode")
            ck(await text('#a3d-awbar .a3d-awbar-k') == 'Analyze' and await text('#a3d-awbar [data-awbart]') == 'Overview', "the bar says Analyze, and Overview")
            ck(await text('#a3d-rpttl') == 'Analysis' and a0.get('panel') == 'overview', "the right is the overview, titled Analysis")
            await tab('layers')
            a1 = await aw()
            ck(a1.get('on') is False and not await safe("()=>!!document.getElementById('a3d-awbar')") and a1.get('look') is None and await text('#a3d-rpttl') == 'Properties',
               "another tab leaves it: no bar, the view as it was, Properties")
            await tab('assets')
            await tab('analyze')
            await click('#a3d-shell [data-toggle]')
            await page.wait_for_timeout(150)
            ck(await safe("()=>document.getElementById('a3d-shell').classList.contains('collapsed')") and (await aw()).get('on') is True, "the panel put away, still in Analyze")
            await click('#a3d-awbar [data-awact="leave"]')
            await page.wait_for_timeout(200)
            sh = await safe("()=>{var s=document.getElementById('a3d-shell');return [s.getAttribute('data-tab'),s.classList.contains('collapsed')];}")
            ck((await aw()).get('on') is False and sh == ['assets', True], "the cross goes back to the tab it came from, the panel left as it was (%s)" % sh)
            await click('#a3d-shell [data-toggle]')
            await page.wait_for_timeout(150)

            # ---------------------------------------------------------------------------------
            print("\n-- 3. The list before a run")
            await tab('analyze')
            ck(await text('.a3d-awl-place') == 'Not placed yet' and await safe("()=>!!document.querySelector('.a3d-awl [data-saaddr]')"), "not placed: the place says so, an address box")
            bd = await safe("()=>[].map.call(document.querySelectorAll('.a3d-awl-bd [data-saact]'),function(b){return b.getAttribute('data-saact');})")
            ck(bd == ['cmd:propertyshape', 'cmd:propertyline'], "no boundary yet: from a shape, or from bearings (%s)" % bd)
            ck(await text('.a3d-awl [data-saact="analyze"]') == 'Analyze site' and 'every analysis drawn' in (await text('.a3d-awl-run') or ''), "Analyze site, and what it does")
            ck(await safe("()=>document.querySelector('.a3d-awl-ov').classList.contains('pick')"), "Overview picked")
            L = await safe("""()=>[].map.call(document.querySelectorAll('.a3d-awl>[data-sacat]'),function(g){return {id:g.getAttribute('data-sacat'),
              no:g.querySelector('.a3d-awl-no').textContent,n:g.querySelector('.a3d-awl-cn').textContent,
              dg:[].map.call(g.querySelectorAll('[data-awrow]'),function(r){return r.getAttribute('data-awrow');}),
              cards:[].map.call(g.querySelectorAll('.a3d-awl-tool'),function(r){return r.getAttribute('data-anzcard');})};})""") or []
            ck([(x['id'], x['n']) for x in L] == [(c[0], c[1]) for c in CATS] and [x['no'] for x in L] == [str(i) for i in range(1, 11)],
               "the ten categories in the standard's order, numbered 1 to 10 (%s)" % [x['id'] for x in L])
            ck([x['dg'] for x in L] == [c[2] for c in CATS], "each analysis in the model under the category it answers")
            ck([x['cards'] for x in L] == [c[3] for c in CATS], "the others too: the survey, terrain and grading in Landform, rain in Water, the sun's in Climate")
            ck(await texts('.a3d-awl-grphd') == ['Model'] and await safe("()=>[].map.call(document.querySelectorAll('[data-anzgrp=\"model\"] [data-anzcard]'),function(r){return r.getAttribute('data-anzcard');})") == MODEL,
               "Model last: colour by, areas, buildings, statistics, frame analysis")
            ck(await safe("()=>!document.querySelector('.a3d-awl [data-anztog],.a3d-awl .a3d-anzbody,.a3d-awl-row .a3d-anzbtn,.a3d-awl-cat .a3d-anzbtn')"), "no row opens in place, and none carries a button")
            ck(await safe("()=>[].every.call(document.querySelectorAll('.a3d-awl [data-awrow] .a3d-awl-nm'),function(b){return b.disabled;})") and
               set(await texts('.a3d-awl [data-awrow] .a3d-awl-st')) == {'Not run'}, "not run yet: each says so, and waits")

            # ---------------------------------------------------------------------------------
            print("\n-- 4. Analyze site")
            await design()
            ck('Property_1' in (await text('.a3d-awl-bd') or ''), "the boundary named once drawn")
            u0 = await safe("()=>window.__a3dUndoDepth()")
            W = []
            await analyse(watch=W)
            runs = [w.get('run') or '' for w in W]
            ck(any(re.search(r'\d of 7 done', r) for r in runs), "while it runs, the list says how far it is (%s)" % (runs[:1]))
            sts = [w.get('steps') or [] for w in W]
            ck(any(len(s) == 7 and any('s-busy' in c for c in s) for s in sts), "and the overview's steps follow it as they come")
            ck(await safe("()=>window.__a3dUndoDepth()") == (u0 or 0) + 1, "one undo step")
            a2 = await aw()
            ck(a2.get('on') is True and a2.get('panel') == 'overview' and a2.get('shown') == [] and len(a2.get('run', [])) == 23, "it ends on the overview, none drawn, all 23 run")
            F = await findings()
            per = {}
            for f in F:
                per[f['cat']] = per.get(f['cat'], 0) + 1
            rows = {r[0]: r[1] for r in await safe("()=>[].map.call(document.querySelectorAll('[data-awpanel=\"overview\"] .a3d-awp-r'),function(r){return [r.querySelector('span').textContent,r.querySelector('b').textContent];})") or []}
            ck(rows.get('Analyses') == '23 of 23' and rows.get('Findings', '').startswith('%d finding' % len(F)) and 'Property_1' in rows.get('Boundary', ''),
               "the overview: the site, its boundary, the analyses run, the findings (%s)" % rows)
            ov = await safe("()=>[].map.call(document.querySelectorAll('[data-awpanel=\"overview\"] .a3d-awp-cat'),function(b){return [b.getAttribute('data-awact'),b.querySelector('.a3d-awp-catf').textContent];})") or []
            ck([o[0] for o in ov] == ['cat:' + c[0] for c in CATS], "the ten categories, each a link")
            ck(all(o[1].startswith('%d finding' % per[o[0][4:]]) if per.get(o[0][4:]) else o[1] == 'No findings yet' for o in ov), "each with its findings counted (%s)" % ov[:2])
            fn = {g: n for g, n in await safe("()=>[].map.call(document.querySelectorAll('.a3d-awl>[data-sacat]'),function(g){return [g.getAttribute('data-sacat'),g.querySelector('.a3d-awl-fn').textContent];})") or []}
            ck(all(fn.get(c[0]) == (str(per[c[0]]) if per.get(c[0]) else '') for c in CATS), "and in the list, beside each category (%s)" % fn)
            ck(await text('.a3d-awl [data-saact="analyze"]') == 'Analyze site again' and 'Last run' in (await text('.a3d-awl-run') or ''), "Analyze site again, and when it last ran")
            # a red flag: the design over a height limit (V160's check of the design)
            await safe("(a)=>window.__a3dZnSet(a[0],a[1])", ['maxH', '10'])
            await safe("()=>window.__a3dSaFill()")
            await page.wait_for_timeout(150)
            rf = [f for f in await findings() if f['cls'] == 'redflag']
            fl = await safe("""()=>{var b=document.querySelector('[data-awpanel="overview"] .a3d-awp-flags'),c=document.querySelector('[data-awpanel="overview"] .a3d-awp-cats');
              return b?{n:b.querySelectorAll('.a3d-awp-flag').length,first:!!(b.compareDocumentPosition(c)&Node.DOCUMENT_POSITION_FOLLOWING),act:b.querySelector('.a3d-awp-flag').getAttribute('data-awact'),
                t:b.textContent}:null;}""") or {}
            ck(rf and fl.get('n') == len(rf) and fl.get('first') and 'Design against the zoning' in fl.get('t', ''), "a red flag: listed first in the overview, above the categories (%s)" % fl)
            ck(await text('.a3d-awl [data-sacat="legal"] .a3d-awl-rf') == str(len([f for f in rf if f['cat'] == 'legal'])) and not await safe("()=>!!document.querySelector('.a3d-awl [data-sacat=\"climate\"] .a3d-awl-rf')"),
               "and counted on its category's line in red, only there")
            await click('[data-awpanel="overview"] .a3d-awp-flag')
            await page.wait_for_timeout(150)
            ck((await aw()).get('panel') == 'cat:legal', "a red flag pressed: its category")

            # ---------------------------------------------------------------------------------
            print("\n-- 5. A category")
            u1 = await safe("()=>window.__a3dUndoDepth()")
            await click('.a3d-awl [data-anzact="aw:cat:climate"]')
            await page.wait_for_timeout(150)
            a3 = await aw()
            cf = [f for f in F if f['cat'] == 'climate']
            ck(a3.get('panel') == 'cat:climate' and a3.get('shown') == [] and await safe("()=>window.__a3dUndoDepth()") == u1, "Climate on the right; nothing drawn, no undo step")
            ck(await safe("()=>{var b=document.querySelector('.a3d-awl [data-anzact=\"aw:cat:climate\"]');return b.classList.contains('pick')&&b.getAttribute('aria-pressed')==='true';}") and
               not await safe("()=>document.querySelector('.a3d-awl-ov').classList.contains('pick')"), "its line picked, Overview no longer")
            hd = [await text('[data-awpanel="cat:climate"] .a3d-awp-no'), await text('[data-awpanel="cat:climate"] .a3d-awp-ttl'), await text('[data-awpanel="cat:climate"] .a3d-awp-sub')]
            ck(hd == ['5', 'Climate', '%d findings' % len(cf)], "its number, its name, its findings counted (%s)" % hd)
            ck(await text('[data-awpanel="cat:climate"] .a3d-awp-about') == 'Temperature, rain, climate zone, sun path, shadows, wind, solar.', "its question")
            ft = await texts('[data-awpanel="cat:climate"] .a3d-safind .a3d-saftt')
            ck(ft == [f['title'] for f in cf] and len(ft) >= 5, "what was found: each finding, its title (%s)" % ft[:3])
            ck(await safe("()=>!document.querySelector('[data-awpanel=\"cat:climate\"] .a3d-safind input,[data-awpanel=\"cat:climate\"] .a3d-safind button')"), "read only")
            an = await safe("()=>[].map.call(document.querySelectorAll('[data-awpanel=\"cat:climate\"] .a3d-awp-an'),function(b){return b.getAttribute('data-awact');})")
            ck(an == ['focus:sun', 'focus:shadow', 'focus:wind', 'card:sun', 'card:sunhours', 'card:solar'], "the analyses that answer it (%s)" % an)
            ck(await text('[data-awpanel="cat:climate"] .a3d-clsec .a3d-sasechd') == 'Climate and risk' and await safe("()=>!!document.querySelector('[data-awpanel=\"cat:climate\"] [data-saact=\"climboard\"]')"),
               "its data: the climate and risk, with its board")
            await click('[data-awpanel="cat:climate"] [data-awact="focus:wind"]')
            await page.wait_for_timeout(150)
            ck((await aw()).get('panel') == 'wind' and (await aw()).get('now') == 'wind', "an analysis from it: in focus, its panel")
            await click('.a3d-awl [data-anzact="aw:cat:risk"]')
            await page.wait_for_timeout(120)
            ck('climate data' in (await text('[data-awpanel="cat:risk"] .a3d-salink') or ''), "Risk says where its data is")
            await click('[data-awpanel="cat:risk"] [data-saact="goto:climate"]')
            await page.wait_for_timeout(150)
            ck((await aw()).get('panel') == 'cat:climate' and (await aw()).get('now') == 'wind', "and its link goes there; the focus as it was")
            # the zoning's form, in Legal
            await click('.a3d-awl [data-anzact="aw:cat:legal"]')
            await click('[data-awpanel="cat:legal"] [data-saact="znedit"]')
            await page.wait_for_timeout(150)
            ck(await safe("()=>!!document.querySelector('[data-awpanel=\"cat:legal\"] .a3d-znf [data-znf=\"far\"]')"), "Legal's zoning: Edit opens its form in the panel")
            await page.fill('#a3d-propsbody [data-znf="far"]', '3.5')
            await page.press('#a3d-propsbody [data-znf="far"]', 'Tab')
            await page.wait_for_timeout(150)
            ck((await safe("()=>window.__a3dZn()") or {}).get('far') == 3.5, "a field changed: the zoning takes it")
            await page.click('#a3d-propsbody [data-znf="district"]')
            await page.keyboard.press('End')
            await page.keyboard.type('R6 by the oak')
            await safe("()=>window.__a3dRefreshProps()")
            v1 = await safe("()=>document.querySelector('#a3d-propsbody [data-znf=\"district\"]').value") or ''
            ck((await aw()).get('pend') is True and v1.endswith('R6 by the oak'), "a refresh while a field is typed in waits, the words kept (%s)" % v1)
            await page.click('.a3d-awl-hd')
            await page.wait_for_timeout(200)
            ck((await safe("()=>window.__a3dZn()") or {}).get('district', '').endswith('R6 by the oak') and (await aw()).get('pend') is False, "left: kept, and the refresh done")
            await page.fill('#a3d-propsbody [data-znf="far"]', '-4')
            await page.press('#a3d-propsbody [data-znf="far"]', 'Enter')
            await page.wait_for_timeout(150)
            ck(await safe("()=>document.querySelector('#a3d-propsbody [data-znf=\"far\"]').value") == '3.5' and (await safe("()=>window.__a3dZn()") or {}).get('far') == 3.5,
               "refused: the field, still in use, shows the zoning's own again")
            await safe("()=>window.__a3dZnEdit(false)")

            # ---------------------------------------------------------------------------------
            print("\n-- 6. An analysis")
            await click('.a3d-awl [data-awrow="wind"] .a3d-awl-nm')
            await page.wait_for_timeout(150)
            wk = await safe("()=>window.__a3dAwFinds('wind')") or []
            want = [f['title'] for f in F if f['auto'] in wk]
            got = await texts('[data-awpanel="wind"] .a3d-safind .a3d-saftt')
            ck(wk == ['climate.wind', 'climate.comfort'] and got == want and got, "what it found: the findings the winds draw (%s)" % got)
            ck((await text('[data-awpanel="wind"] .a3d-awp-sub') or '').startswith('Climate') and await text('[data-awpanel="wind"] .a3d-awp-in') == 'Answers 5. Climate',
               "the category it answers, named")
            await click('[data-awpanel="wind"] .a3d-awp-in [data-awact]')
            await page.wait_for_timeout(120)
            ck((await aw()).get('panel') == 'cat:climate' and (await aw()).get('now') == 'wind', "and a link to it")
            await click('.a3d-awl [data-awrow="views"] .a3d-awl-nm')
            await page.wait_for_timeout(120)
            ck(await text('[data-awpanel="views"] .a3d-awp-note') == "It writes no finding of its own; its category's are under People and place.", "one that writes no finding says where its category's are")
            await safe("()=>window.__a3dStdOverride('tfl.ptal','walk_bus',10,'Slower still')")
            await click('.a3d-awl [data-awrow="transit"] .a3d-awl-nm')
            await page.wait_for_timeout(150)
            ck('Out of date: Public Transport Accessibility Level (PTAL): walk_bus overridden since it ran: Run again' in (await text('[data-awpanel="transit"] .a3d-awp-stale') or '') and
               await text('.a3d-awl [data-awrow="transit"] .a3d-awl-st') == 'Out of date', "a standard changed since it ran: its line and its panel say so, and what to do")

            # ---------------------------------------------------------------------------------
            print("\n-- 7. One of the model's")
            await click('.a3d-awl [data-anzact="aw:card:structure"]')
            await page.wait_for_timeout(150)
            P = '[data-awpanel="card:structure"]'
            ck(await text(P + ' .a3d-awp-ttl') == 'Frame analysis' and await text(P + ' .a3d-awp-sub') == 'Model · Off' and
               await text(P + ' .a3d-awp-about') == 'No frame yet: place columns and beams', "Frame analysis on the right: Model, Off, and what it says")
            fs = await safe("(p)=>[].map.call(document.querySelectorAll(p+' [data-propstr],'+p+' [data-anzload]'),function(e){return e.getAttribute('data-propstr')||e.getAttribute('data-anzload');})", P)
            ck(fs == ['dl', 'll'] or set(fs or []) >= {'dl', 'll'}, "its settings: the floor loads (%s)" % fs)
            bt = await safe("(p)=>[].map.call(document.querySelectorAll(p+' .a3d-awp-acts [data-anzact]'),function(b){return [b.getAttribute('data-anzact'),b.disabled,b.title];})", P) or []
            ck([b[0] for b in bt] == ['structure:run', 'structure:off'] and bt[0][1] and bt[0][2] == 'Place columns and beams first', "its buttons, and why Run waits (%s)" % bt)
            await page.fill('#a3d-propsbody [data-anzload="dl"]', '4')
            await page.press('#a3d-propsbody [data-anzload="dl"]', 'Enter')
            await page.wait_for_timeout(150)
            ck((await safe("()=>window.__a3dLevels()") or [{}])[0].get('dl') == 4, "a floor load typed: the level takes it")
            await page.fill('#a3d-propsbody [data-anzload="dl"]', '-3')
            await page.press('#a3d-propsbody [data-anzload="dl"]', 'Enter')
            await page.wait_for_timeout(150)
            ck(await safe("()=>document.querySelector('#a3d-propsbody [data-anzload=\"dl\"]').value") == '4' and (await safe("()=>window.__a3dLevels()") or [{}])[0].get('dl') == 4,
               "a negative one refused: the field shows the level's 4 again")
            await click('.a3d-awl [data-anzact="aw:card:sunhours"]')
            await page.wait_for_timeout(150)
            la = await safe("()=>{var b=document.querySelector('[data-awpanel=\"card:sunhours\"] [data-anzact=\"layer:sunhours\"]');return b?[b.textContent,b.disabled,b.title]:null;}")
            ck(la == ['Add as layer', True, 'Run it first'], "Sun hours: Add as layer, waiting for a run (%s)" % la)
            ck(await text('[data-awpanel="card:sunhours"] .a3d-awp-in') == 'Answers 5. Climate', "and the category it answers")
            await click('#a3d-propsbody [data-anzact="sunhours:run"]')
            await page.wait_for_timeout(400)
            ck(await text('.a3d-awl [data-anzcard="sunhours"] .a3d-anzstate') == 'On' and not await safe("()=>document.querySelector('[data-awpanel=\"card:sunhours\"] [data-anzact=\"layer:sunhours\"]').disabled"),
               "Run: its line says On, and Add as layer is ready")
            await safe("()=>window.__a3dRunCmd('simclear')")

            # ---------------------------------------------------------------------------------
            print("\n-- 8. Properties from a button")
            await click('.a3d-awl [data-anzact="aw:card:sun"]')
            await click('[data-awpanel="card:sun"] [data-anzact="open:Location"]')
            await page.wait_for_timeout(200)
            a4 = await aw()
            ck(a4.get('props') is True and await text('#a3d-rpttl') == 'Properties' and await safe("()=>!!document.querySelector('#a3d-propsbody [data-a3dpgrp=\"Location\"]')") and
               await safe("()=>window.__a3dPropTab()") == 'site', "Settings: the model's Properties at Location, on Site")
            ck(await text('#a3d-propsbody .a3d-awp-backrow') == 'Back to the analysis', "with a way back above them")
            await click('#a3d-propsbody .a3d-awp-backrow [data-awact="back"]')
            await page.wait_for_timeout(150)
            ck((await aw()).get('panel') == 'card:sun' and (await aw()).get('props') is False and await text('#a3d-rpttl') == 'Analysis', "back: the analysis as it was")
            await safe("()=>window.__a3dRunCmd('usages')")
            await page.wait_for_timeout(150)
            ck((await aw()).get('props') is True and await safe("()=>!!document.querySelector('#a3d-propsbody [data-a3dpgrp=\"Usages\"]')") and (await aw()).get('on') is True,
               "USAGES in Analyze: the usages in Properties, still in Analyze")
            await click('#a3d-propsbody [data-awact="back"]')

            # ---------------------------------------------------------------------------------
            print("\n-- 9. A pick over a selection")
            box = await safe("()=>window.__a3dState().objs.filter(function(o){return o.t==='box';})[0].id")
            await safe("(i)=>{window.__a3dSelectFor([i]);window.__a3dRefreshProps();}", box)
            await page.wait_for_timeout(120)
            ck(await text('#a3d-rpttl') == 'Properties' and not await safe("()=>!!document.querySelector('#a3d-propsbody [data-awpanel]')"), "a mass selected: its properties, as anywhere")
            await click('.a3d-awl [data-anzact="aw:card:solar"]')
            await page.wait_for_timeout(150)
            ck((await aw()).get('panel') == 'card:solar' and await safe("()=>window.__a3dState().sel") == box and await text('#a3d-rpttl') == 'Analysis',
               "a row picked: its panel, the mass still selected for what acts on it")
            await safe("()=>window.__a3dRefreshProps()")
            ck((await aw()).get('panel') == 'card:solar', "and a refresh keeps it")
            other = await safe("()=>window.__a3dState().objs.filter(function(o){return o.t==='box';})[1].id")
            await safe("(i)=>{window.__a3dSelectFor([i]);window.__a3dRefreshProps();}", other)
            ck(await text('#a3d-rpttl') == 'Properties', "another selection: its properties")
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dRefreshProps();}")
            ck((await aw()).get('panel') == 'card:solar', "nothing selected: the pick again")
            await safe("(i)=>{window.__a3dSelectFor([i]);window.__a3dRefreshProps();}", other)
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dRefreshProps();}")
            await safe("(i)=>{window.__a3dSelectFor([i]);window.__a3dRefreshProps();}", box)
            ck(await text('#a3d-rpttl') == 'Properties', "the first selected again, later: its properties, not the pick made over it before")
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dRefreshProps();}")

            # ---------------------------------------------------------------------------------
            print("\n-- 10. The search")

            async def search(q):
                return await safe("(q)=>window.__a3dAnzSearch(q)", q) or []

            async def vis_cats():
                return await safe("()=>[].filter.call(document.querySelectorAll('.a3d-awl>[data-sacat]'),function(e){return !e.hasAttribute('hidden');}).map(function(e){return e.getAttribute('data-sacat');})") or []
            s1 = await search('seismic')
            ck(await vis_cats() == ['risk'] and s1 == ['dgnoise'], "a word of a category's question: the category whole (%s)" % s1)
            st = await safe("()=>({ov:document.querySelector('.a3d-awl-ov').hasAttribute('hidden'),site:!document.querySelector('.a3d-awl-site').hasAttribute('hidden'),model:document.querySelector('[data-anzgrp=\"model\"]').hasAttribute('hidden')})")
            ck(st == {'ov': True, 'site': True, 'model': True}, "Overview and Model step aside; the site stays (%s)" % st)
            await search('subtropical')
            ck(await vis_cats() == ['climate'], "a word of a finding: its category (%s)" % await vis_cats())
            await search('constraint')
            vc = await vis_cats()
            FC = await findings()
            ck(vc and all(any(f['cat'] == c and f['cls'] == 'constraint' for f in FC) for c in vc), "a finding's class: the categories holding one (%s)" % vc)
            ck(await search('arrows') == ['grading'], "a row's button: Slope arrows finds Grading")
            ck(await search('floor loads') == ['structure'], "a row's settings: the floor loads find Frame analysis")
            ck(await search('divides') == ['dgflow'], "what an analysis shows: the divides find Water flow")
            await search('zzqx')
            ck(await safe("()=>!document.querySelector('.a3d-awl .a3d-anzempty').hasAttribute('hidden')") and await vis_cats() == [], "nothing: it says so")
            await page.focus('.a3d-awl [data-anzsearch]')
            await page.keyboard.press('Escape')
            await page.wait_for_timeout(100)
            ck(len(await vis_cats()) == 10 and not await safe("()=>document.querySelector('.a3d-awl-ov').hasAttribute('hidden')"), "Esc: every category back, and Overview")
            await search('wind')
            await safe("()=>window.__a3dSaGoto('water')")
            ck(await safe("()=>document.querySelector('.a3d-awl [data-anzsearch]').value") == '' and 'water' in await vis_cats() and (await aw()).get('panel') == 'cat:water',
               "a link to a category the search hid: the search cleared, the category on the right")

            # ---------------------------------------------------------------------------------
            print("\n-- 11. The look")
            await click('.a3d-awl [data-anzact="aw:cat:water"]')
            cd = await safe("()=>getComputedStyle(document.querySelector('.a3d-awl [data-anzact=\"aw:cat:water\"]')).backgroundColor")
            await safe("()=>document.body.classList.add('light-theme')")
            cl = await safe("()=>getComputedStyle(document.querySelector('.a3d-awl [data-anzact=\"aw:cat:water\"]')).backgroundColor")
            ck(cd == 'rgb(232, 237, 242)' and cl == 'rgb(31, 35, 40)', "a pick in the mode's colours, dark and light (%s, %s)" % (cd, cl))
            ck(await safe("()=>window.__a3dAwMvLight()") is True, "the cars on the light ground take the light colours")
            await safe("()=>document.body.classList.remove('light-theme')")
            ck(await safe("()=>window.__a3dAwMvLight()") is False, "on the dark, the dark")
            ar = await safe("()=>{var o=window.__a3dState().objs.filter(function(x){return x.t==='diag'&&x.dg.a==='streets'&&/^street:ar\\|/.test(x.dg.k);})[0];return o?o.dg.s.stroke:null;}")
            ck(await safe("()=>window.__a3dMapSettings().style") == 'street' and ar == LIGHT_AR, "what a run draws keeps the map's colours: an arterial for the light street map (%s)" % ar)

            # ---------------------------------------------------------------------------------
            print("\n-- 12. Out and in")
            await tab('presentation')
            ck((await aw()).get('on') is False and (await aw()).get('props') is False, "out of it")
            await tab('analyze')
            ck((await aw()).get('panel') == 'cat:water', "back in: the pick as it was left")
            print("")
            ck(not errs, "zero uncaught page errors (%s)" % (errs[:3] or 'none'))
            await ctx.close()

            # ---------------------------------------------------------------------------------
            print("\n-- 13. A phone")
            pc, pp = await page_for({'width': 390, 'height': 844}, mobile=True)
            await within(pp.goto('file://' + str(HTML)), 'goto phone')
            await pp.wait_for_timeout(2300)
            await safe("()=>window.__a3dEnter()", pg=pp)
            await design(pp)
            await analyse(pp)
            await pp.wait_for_timeout(300)
            ck(await safe("()=>document.getElementById('a3d-shell').classList.contains('collapsed')", pg=pp), "the run done: the drawer shut, the view in sight")
            await tab('analyze', pg=pp)
            g = await safe("""()=>{var s=document.getElementById('a3d-shell'),w=document.querySelector('.a3d-awl'),r=w?w.getBoundingClientRect():null;
              return {open:!s.classList.contains('collapsed'),right:r?r.right:0,sw:w?w.scrollWidth:0,cw:w?w.clientWidth:0,h:Math.min.apply(0,[].map.call(document.querySelectorAll('.a3d-awl-cat'),function(b){return b.getBoundingClientRect().height;}))};}""", pg=pp) or {}
            ck(g.get('open') and g.get('right', 999) <= 390 and g.get('sw', 9) <= g.get('cw', 0) + 1 and g.get('h', 0) >= 44, "Analyze's tab: the list in the drawer, nothing spilling, lines a finger's height (%s)" % g)
            await click('.a3d-awl [data-anzact="aw:cat:access"]', pg=pp)
            await pp.wait_for_timeout(300)
            p1 = await safe("()=>({shut:document.getElementById('a3d-shell').classList.contains('collapsed'),sheet:document.getElementById('a3d-right').classList.contains('open'),panel:window.__a3dAw().panel})", pg=pp) or {}
            ck(p1 == {'shut': True, 'sheet': True, 'panel': 'cat:access'}, "a category: the drawer shut, the category open as a sheet (%s)" % p1)
            await tab('analyze', pg=pp)
            await click('.a3d-awl [data-awrow="transit"] .a3d-awl-nm', pg=pp)
            await pp.wait_for_timeout(300)
            p2 = await safe("()=>({shut:document.getElementById('a3d-shell').classList.contains('collapsed'),sheet:document.getElementById('a3d-right').classList.contains('open'),now:window.__a3dAw().now})", pg=pp) or {}
            ck(p2 == {'shut': True, 'sheet': False, 'now': 'transit'}, "an analysis: the drawer shut and the sheet too, the view with it in focus (%s)" % p2)
            ck(await click('#a3d-awbar [data-awact="panel"]', pg=pp) and await safe("()=>document.getElementById('a3d-right').classList.contains('open')&&!!document.querySelector('#a3d-propsbody [data-awpanel=\"transit\"]')", pg=pp),
               "Details opens its panel")
            ck(not pp.errs, "the phone: zero uncaught page errors (%s)" % (pp.errs[:2] or 'none'))
            await pc.close()
        except Stalled as e:
            ck(False, "STALLED: %s" % e)
        except Exception:
            traceback.print_exc()
            ck(False, "the suite raised")
        await browser.close()

    print("\n%d/%d checks passed" % (ck.n - len(ck.bad), ck.n))
    if ck.bad:
        print("RESULT: FAIL")
        for m in ck.bad:
            print("   - " + m)
        return 1
    print("RESULT: PASS")
    return 0


sys.exit(asyncio.run(run()))
