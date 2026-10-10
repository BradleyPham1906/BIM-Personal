#!/usr/bin/env python3
"""bim_phase162_one_analyze_board_pages_browser_tests.py -- V162: one Analyze; the boards are pages of the set.

The owner: "you are splitting the analysis and site analysis on 2 different layers. they should be
just one ... for the report/ dashboard, it should be on the presentation layer not its own thing".
The access data comes from tests/access_fixture.py (Overpass, TIGERweb and the Census API in their
own shapes), as in V161, so the Access and people board has real figures to show.

  1. ONE ANALYZE: one tab body (the old two classes on it), no switch, one search; stages, Define,
     the ten categories in order, Model last; each analysis in the category it answers; each
     category's data; Risk and People pointing to the data they share.
  2. A ROW INSIDE A CATEGORY: opens on its own, not with its category.
  3. ONE SEARCH: a category asked for by its own words shows whole and opened; otherwise only its
     analyses that match; Model; Define; a finding's words; nothing; Esc; kept over a refresh.
  4. A FIELD BEING TYPED IN: a refresh waits for it, then happens.
  5. COMMANDS AND HOOKS: SITEANALYSIS, ZONING into Legal, a category's link, the old view hook.
  6. A BOARD IS A PAGE: + Board, in the set's order, numbered, its tag; one undo step; Show in
     Presentation from Analyze; the commands; one of each kind.
  7. IN THE MAIN VIEW: over the main view only, the panels beside it, the drawing tools away; laid
     out by its own width; Esc (not from a field elsewhere); a sheet or a view gives the view back.
  8. ITS THUMBNAIL: the board as it prints, scaled to the column, following the model.
  9. THE ORDER: dragged, stepped, its menu, a sheet's menu, + Page last, removed and undone.
 10. PRESENT: a board's page as on screen, the canvas aside, scrolled by the wheel to its end, then
     the next page; back on the board last shown.
 11. PRINT: Print set with the board on its own A3 pages in the set's order; the board's own Print;
     the browser's print; the print look.
 12. KEPT WITH THE PROJECT: the file, a bad record, a reload.
 13. A TABLET AND A PHONE.

The harness never waits without a bound (V123).
"""
import asyncio, json, pathlib, re, sys, traceback

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from bim_phase133_site_context_browser_tests import Checks, Stalled, within   # noqa: E402
import access_fixture as FX   # noqa: E402
from playwright.async_api import async_playwright   # noqa: E402

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'
CK = Checks()
HOSTS = ('https://overpass-api.de/**', 'https://overpass.private.coffee/**', 'https://maps.mail.ru/**', 'https://overpass.kumi.systems/**',
         'https://tigerweb.geo.census.gov/**', 'https://api.census.gov/**')
CATS = ['location', 'legal', 'landform', 'water', 'climate', 'ecology', 'risk', 'access', 'utilities', 'people']


def width_cls(w):
    return (' w-l' if w >= 1240 else '') + (' w-m' if w < 1100 else '') + (' w-s' if w < 760 else '')


async def run():
    ck = CK
    LOT = [list(p) for p in FX.LOT]
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()

        async def open_page(vw, vh, scale=1):
            ctx = await browser.new_context(viewport={'width': vw, 'height': vh}, device_scale_factor=scale)
            ST = {'year': 2024}
            for h in HOSTS:
                await ctx.route(h, FX.route_handler(ST))
            pg = await ctx.new_page()
            errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)))
            await within(pg.goto('file://' + str(HTML)), 'goto')
            await pg.wait_for_timeout(2300)
            return ctx, pg, errs

        ctx, page, errs = await open_page(1440, 900)

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

        async def tab(name, pg=None):
            await safe("(t)=>{var b=document.querySelector('#a3d-rail .a3d-railbtn[data-tab=\"'+t+'\"]');if(b)b.click();return !!b;}", name, pg=pg)
            await (pg or page).wait_for_timeout(150)

        async def set_site(lat, lon, pg=None):
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dSetPropTab('site');window.__a3dRefreshProps();}", pg=pg)
            for k, v in (('sunlat', lat), ('sunlon', lon)):
                await safe("""(a)=>{var L=document.querySelectorAll('#a3d-propsbody input'),e=null,i;for(i=0;i<L.length;i++)if(L[i].getAttribute('data-propmodel')===a[0])e=L[i];
                  if(!e)return false;e.value=a[1];e.dispatchEvent(new Event('change',{bubbles:true}));return true;}""", [k, v], pg=pg)
                await (pg or page).wait_for_timeout(80)

        async def lot(pg=None):
            await safe("""(a)=>{var o=window.__a3dState().objs.filter(function(x){return x.t!=='property'&&x.id!=='LOT';});
              o.push({id:'LOT',t:'sketch',name:'Lot',col:'#5ec4b8',pos:[0,0,0],pts:a,y:0,closed:true,layer:'layer-0'});
              window.__a3dTestSetObjs(o);window.__a3dPropertyFromSketch('LOT');}""", LOT, pg=pg)

        async def prepare(pg=None):
            await safe("()=>{window.__a3dEnter();window.__a3dTestSetObjs([]);}", pg=pg)
            await set_site('40', '-75', pg=pg)
            await lot(pg=pg)
            return await safe("()=>Promise.resolve(window.__a3dAccFetch())", pg=pg) or {}

        async def search(q):
            return await safe("(q)=>window.__a3dAnzSearch(q)", q)

        async def seq(pg=None):
            return [e['id'] for e in (await safe("()=>window.__a3dPresSeq()", pg=pg) or [])]

        async def clb(pg=None):
            return await safe("()=>window.__a3dClbState()", pg=pg) or {}

        async def panel(pg=None):
            return await safe("()=>window.__a3dPresPanel()", pg=pg) or {}

        async def visible_cats():
            return await safe("()=>[].filter.call(document.querySelectorAll('.a3d-analyze-wrap [data-sacat]'),function(e){return !e.closest('[hidden]');}).map(function(e){return e.getAttribute('data-sacat');})") or []

        try:
            has = await safe("()=>window.__acad3dV162")
            ck(bool(has) and 'oneanalyze' in has and 'boardpages' in has and 'printset' in has, "__acad3dV162 marker is present (%s)" % (has or '')[:80])
            ver = await safe("()=>window.__a3dVersion()") or {}
            ck(re.match(r'^V(\d+)$', ver.get('v', '')) and int(ver['v'][1:]) >= 162, "the app says V162 or later (%s)" % ver.get('v'))
            if not has:
                raise Stalled('no V162')
            r = await prepare()
            ck(bool(r.get('access')), "the access data is fetched from the fixture, so its board has figures")

            # ---------------------------------------------------------------------------------
            print("\n-- 1. one Analyze")
            await tab('analyze')
            A = await safe("""()=>{var W=document.querySelectorAll('#a3d-leftpanel .a3d-analyze-wrap'),S=document.querySelectorAll('#a3d-leftpanel .a3d-sa-wrap'),x=W[0];
              if(!x)return null;
              function ids(sel,at){return [].map.call(x.querySelectorAll(sel),function(e){return e.getAttribute(at);});}
              var where={};[].forEach.call(x.querySelectorAll('[data-anzcard]'),function(r){var c=r.closest('[data-sacat]'),g=r.closest('[data-anzgrp]');where[r.getAttribute('data-anzcard')]=c?c.getAttribute('data-sacat'):(g?g.getAttribute('data-anzgrp'):null);});
              return {n:W.length,ns:S.length,same:W[0]===S[0],sw:document.querySelectorAll('[data-anzview]').length,title:(x.querySelector('.a3d-anzttl0')||{}).textContent,
                search:x.querySelectorAll('[data-anzsearch]').length,ph:(x.querySelector('[data-anzsearch]')||{}).placeholder,
                order:[].map.call(x.querySelectorAll('.a3d-anzrows>[data-anzsec],.a3d-anzrows>[data-anzgrp]'),function(e){return e.getAttribute('data-anzsec')||e.getAttribute('data-anzgrp');}),
                cats:ids('[data-anzsec="cats"] [data-sacat]','data-sacat'),model:ids('[data-anzgrp="model"] [data-anzcard]','data-anzcard'),where:where,
                names:[].map.call(x.querySelectorAll('[data-sacat]>.a3d-anzhd .a3d-anzttl'),function(e){return e.textContent;}),
                data:{location:!!x.querySelector('[data-sacat="location"] [data-ctxsec]'),legal:!!x.querySelector('[data-sacat="legal"] [data-znsec]'),
                  climate:((x.querySelector('[data-sacat="climate"] .a3d-clsec .a3d-sasechd')||{}).textContent||''),access:!!x.querySelector('[data-sacat="access"] [data-accsec]')},
                links:{risk:(x.querySelector('[data-sacat="risk"] [data-saact^="goto:"]')||{getAttribute:function(){return null;}}).getAttribute('data-saact'),
                  people:(x.querySelector('[data-sacat="people"] [data-saact^="goto:"]')||{getAttribute:function(){return null;}}).getAttribute('data-saact')},
                defineData:x.querySelectorAll('[data-anzsec="define"] .a3d-clsec').length,defineCtx:x.querySelectorAll('[data-anzsec="define"] [data-saact="cmd:context"]').length,
                locCtx:x.querySelectorAll('[data-sacat="location"] [data-saact="cmd:context"]').length,defineFill:x.querySelectorAll('[data-anzsec="define"] [data-saact="fill"]').length,
                count:(x.querySelector('.a3d-anzcount')||{}).textContent};}""") or {}
            ck(A.get('n') == 1 and A.get('ns') == 1 and A.get('same'), "one tab body, carrying both of the old classes (%s, %s)" % (A.get('n'), A.get('ns')))
            ck(A.get('sw') == 0, "no Analyses | Site analysis switch")
            ck(A.get('title') == 'Analyze' and A.get('search') == 1 and 'findings' in (A.get('ph') or ''), "titled Analyze, one search, over analyses, data and findings (%s)" % A.get('ph'))
            ck(A.get('order') == ['stages', 'define', 'cats', 'model'], "the stages, Define, the ten categories, then Model (%s)" % A.get('order'))
            ck(A.get('cats') == CATS, "the ten categories, in the standard's order (%s)" % A.get('cats'))
            ck((A.get('names') or [''])[0] == '1. Location and context' and (A.get('names') or [''] * 10)[9] == '10. People and place', "numbered 1 to 10 (%s)" % (A.get('names') or [])[:2])
            ck(A.get('model') == ['lens', 'areas', 'lod', 'stats', 'structure'], "Model: colour by, areas by usage, buildings LOD, statistics, frame analysis (%s)" % A.get('model'))
            W = A.get('where') or {}
            want = {'survey': 'landform', 'terrain': 'landform', 'grading': 'landform', 'rain': 'water', 'sun': 'climate', 'sunhours': 'climate', 'solar': 'climate',
                    'lens': 'model', 'areas': 'model', 'lod': 'model', 'stats': 'model', 'structure': 'model'}
            ck(W == want, "each analysis in the category it answers: landform, water, climate; the model's in Model (%s)" % W)
            cats = await safe("()=>window.__a3dAnzCats()") or []
            ck({c['id']: c['group'] for c in cats} == want, "the engine's grouping says the same")
            D = A.get('data') or {}
            ck(D.get('location') and D.get('legal') and D.get('climate') == 'Climate and risk' and D.get('access'),
               "each category's data in it: Location the context, Legal zoning, Climate the climate and risk, Access the access and people (%s)" % D)
            ck((A.get('links') or {}) == {'risk': 'goto:climate', 'people': 'goto:access'}, "Risk and People point to the data they share (%s)" % A.get('links'))
            ck(A.get('defineData') == 0 and A.get('defineCtx') == 0 and A.get('locCtx') == 1 and A.get('defineFill') == 1,
               "Define is the boundary, the project, the questions; the context moved to Location")
            ck(re.match(r'^\d+ findings?', A.get('count') or ''), "the count: the findings (%s)" % A.get('count'))

            # ---------------------------------------------------------------------------------
            print("\n-- 2. a row inside a category")
            await safe("()=>{window.__a3dSaGoto('climate');}")
            await page.wait_for_timeout(250)
            disp = "(id)=>{var r=document.querySelector('.a3d-analyze-wrap [data-anzcard=\"'+id+'\"]');return r?{body:getComputedStyle(r.querySelector('.a3d-anzbody')).display,sum:getComputedStyle(r.querySelector('.a3d-anzsum')).display,open:r.classList.contains('open')}:null;}"
            s0 = await safe(disp, 'sun') or {}
            ck(s0.get('body') == 'none' and s0.get('sum') != 'none', "the category open, its rows stay shut, their summary shown (%s)" % s0)
            if s0.get('open'):
                await safe("()=>window.__a3dAnzToggle('sun',false)")
            await page.click('.a3d-analyze-wrap [data-anzcard="sun"] [data-anztog]')
            s1 = await safe(disp, 'sun') or {}
            s2 = await safe(disp, 'sunhours') or {}
            ck(s1.get('open') and s1.get('body') == 'block' and s2.get('body') == 'none', "a row opens on its own: Sun and shadows open, Sun hours shut (%s, %s)" % (s1, s2))
            await page.click('.a3d-analyze-wrap [data-satog="climate"]')
            hid = await safe("()=>getComputedStyle(document.querySelector('.a3d-analyze-wrap [data-sacat=\"climate\"]>.a3d-anzbody')).display")
            ck(hid == 'none', "the category shut hides its rows with it")
            await page.click('.a3d-analyze-wrap [data-satog="climate"]')
            s3 = await safe(disp, 'sun') or {}
            ck(s3.get('open') and s3.get('body') == 'block', "opened again, the row is as it was left")
            await safe("()=>window.__a3dAnzToggle('sun',false)")

            # ---------------------------------------------------------------------------------
            print("\n-- 3. one search")
            q1 = await search('cut fill')
            st1 = await safe("""()=>{var x=document.querySelector('.a3d-analyze-wrap'),c=x.querySelector('[data-sacat="landform"]');
              return {qhit:c.classList.contains('qhit'),body:getComputedStyle(c.querySelector(':scope>.a3d-anzbody')).display,model:!!x.querySelector('[data-anzgrp="model"]').hasAttribute('hidden'),
                stages:x.querySelector('[data-anzsec="stages"]').hasAttribute('hidden'),root:x.querySelector('.a3d-anz').classList.contains('q')};}""") or {}
            ck(q1 == ['grading'] and await visible_cats() == ['landform'], "'cut fill' finds Grading alone, in Landform (%s)" % q1)
            ck(st1.get('qhit') and st1.get('body') == 'block' and st1.get('model') and st1.get('stages') and st1.get('root'),
               "Landform is opened for it; Model and the stages step aside (%s)" % st1)
            q2 = await search('slope')
            ck(q2 == ['survey', 'terrain', 'grading'] and await visible_cats() == ['landform'], "'slope' is in Landform's own question: the category shows whole (%s)" % q2)
            q3 = await search('frame')
            ck(q3 == ['structure'] and await visible_cats() == [], "'frame' finds the frame analysis in Model, and no category (%s)" % q3)
            await search('boundary')
            bd = await safe("()=>!document.querySelector('.a3d-analyze-wrap [data-anzsec=\"define\"]').hasAttribute('hidden')")
            vc = await visible_cats()
            ck(bd and 'legal' in vc, "'boundary' finds Define's boundary and Legal's markers (%s)" % vc)
            fid = await safe("()=>window.__a3dSaAdd('ecology',{title:'Badger sett',value:'Active, near the north hedge'})")
            await safe("()=>window.__a3dAnzView('site')")
            q4 = await search('badger')
            ck(fid and await visible_cats() == ['ecology'], "a finding's words find its category (%s)" % await visible_cats())
            q5 = await search('zzqx')
            emp = await safe("()=>!document.querySelector('.a3d-analyze-wrap .a3d-anzempty').hasAttribute('hidden')")
            ck(q5 == [] and await visible_cats() == [] and emp, "nothing matches: it says so")
            await search('cut fill')
            await safe("()=>window.__a3dAnalyzeRefresh(true)")
            q6 = await safe("()=>[].filter.call(document.querySelectorAll('.a3d-analyze-wrap [data-anzcard]'),function(e){return !e.closest('[hidden]');}).map(function(e){return e.getAttribute('data-anzcard');})")
            ck(q6 == ['grading'], "the search holds over a refresh of the list (%s)" % q6)
            await page.focus('.a3d-analyze-wrap [data-anzsearch]')
            await page.keyboard.press('Escape')
            await page.wait_for_timeout(100)
            esc = await safe("()=>({v:document.querySelector('.a3d-analyze-wrap [data-anzsearch]').value,q:document.querySelector('.a3d-analyze-wrap .a3d-anz').classList.contains('q'),n:document.querySelectorAll('.a3d-analyze-wrap [data-sacat].qhit').length,cats:document.querySelectorAll('.a3d-analyze-wrap [data-sacat]:not([hidden])').length})") or {}
            ck(esc.get('v') == '' and not esc.get('q') and esc.get('n') == 0 and esc.get('cats') == 10, "Esc clears it: all ten back, none opened by it (%s)" % esc)
            sticky = await safe("()=>getComputedStyle(document.querySelector('.a3d-analyze-wrap [data-anzsearch]')).position")
            ck(sticky == 'sticky', "the search stays at the top while the list scrolls under it")

            # ---------------------------------------------------------------------------------
            print("\n-- 4. a field being typed in")
            await safe("(id)=>window.__a3dSaEdit(id)", fid)
            await page.wait_for_timeout(150)
            sel = '.a3d-analyze-wrap [data-saff="%s:title"]' % fid
            await page.click(sel)
            await page.keyboard.press('End')
            await page.keyboard.type(' by the oak')
            held = await safe("()=>window.__a3dAnalyzeRefresh()")
            v1 = await safe("(s)=>document.querySelector(s).value", sel)
            ck(held is False and await safe("()=>window.__a3dAnzPending()") is True and v1 == 'Badger sett by the oak',
               "a refresh while a field is typed in waits: the words stay (%s)" % v1)
            await safe("()=>window.__a3dRefreshProps()")
            ck(await safe("(s)=>document.querySelector(s).value", sel) == 'Badger sett by the oak', "and every refresh after it waits too")
            await page.click('.a3d-analyze-wrap .a3d-anzhead')
            await page.wait_for_timeout(200)
            sa = await safe("()=>window.__a3dSa()") or {}
            ttl = [f['title'] for f in sa.get('findings', []) if f['id'] == fid]
            ck(ttl == ['Badger sett by the oak'] and await safe("()=>window.__a3dAnzPending()") is False, "left, the field is kept and the refresh happens (%s)" % ttl)
            await safe("()=>window.__a3dSaEdit(null)")

            # ---------------------------------------------------------------------------------
            print("\n-- 5. commands and hooks")
            await tab('layers')
            await safe("()=>window.__a3dRunCmd('siteanalysis')")
            await page.wait_for_timeout(150)
            ck(await safe("()=>document.getElementById('a3d-shell').dataset.tab") == 'analyze', "SITEANALYSIS opens Analyze")
            await safe("()=>window.__a3dRunCmd('zoning')")
            await page.wait_for_timeout(300)
            zn = await safe("()=>{var c=document.querySelector('.a3d-analyze-wrap [data-sacat=\"legal\"]');return {open:c.classList.contains('open'),form:!!c.querySelector('.a3d-znf')};}") or {}
            ck(zn.get('open') and zn.get('form'), "ZONING opens Legal with the zoning form in it (%s)" % zn)
            await safe("()=>window.__a3dZnEdit(false)")
            await safe("()=>window.__a3dSaToggle&&window.__a3dSaToggle('climate',false)")
            await page.click('.a3d-analyze-wrap [data-sacat="risk"] [data-satog]')
            await page.click('.a3d-analyze-wrap [data-sacat="risk"] [data-saact="goto:climate"]')
            await page.wait_for_timeout(700)
            gl = await safe("""()=>{var c=document.querySelector('.a3d-analyze-wrap [data-sacat="climate"]'),p=document.getElementById('a3d-leftpanel').getBoundingClientRect(),r=c.getBoundingClientRect();
              return {open:c.classList.contains('open'),top:Math.round(r.top-p.top),h:Math.round(p.height)};}""") or {}
            ck(gl.get('open') and 0 <= gl.get('top', -1) < gl.get('h', 0) / 2, "Risk's link opens Climate and brings it into view (%s)" % gl)
            ck(await safe("()=>window.__a3dAnzView('site')") is True and await safe("()=>window.__a3dAnzView()") == 'analyze', "the old view hook opens the one Analyze")

            # ---------------------------------------------------------------------------------
            print("\n-- 6. a board is a page")
            s1 = await safe("()=>window.__a3dAddSheet('A101','Site Plan','A3-L')")
            s2 = await safe("()=>window.__a3dAddSheet('A201','Elevations','A3-L')")
            await tab('presentation')
            bar = await safe("()=>[].map.call(document.querySelectorAll('#a3d-leftpanel .a3d-prpbar [data-prpact]'),function(b){return b.textContent;})")
            ck(bar == ['Present', '+ Page', '+ Board', 'Print set'], "the set's bar: Present, + Page, + Board, Print set (%s)" % bar)
            hdr = await safe("()=>{var h=document.querySelector('#a3d-leftpanel .a3d-projhead').getBoundingClientRect(),w=document.querySelector('#a3d-leftpanel .a3d-pres-wrap').getBoundingClientRect();return [Math.round(h.height),Math.round(w.top-h.bottom)];}") or [0, -1]
            ck(hdr[0] >= 30 and hdr[1] >= 0, "the project's name above the set, whole, not under it (%s)" % hdr)
            await page.click('#a3d-leftpanel [data-prpact="board"]')
            await page.wait_for_timeout(150)
            menu = await safe("()=>[].map.call(document.querySelectorAll('#a3d-ltmenu [data-ltm]'),function(b){return [b.textContent,b.getAttribute('data-ltm')];})")
            ck(menu == [['Climate and risk', 'climate'], ['Zoning and yield', 'zoning'], ['Access and people', 'access']], "+ Board offers the three boards (%s)" % menu)
            await page.click('#a3d-ltmenu [data-ltm="access"]')
            await page.wait_for_timeout(500)
            Q = await seq()
            ck(Q == [s1, s2, 'board-access'], "the board is the set's last page (%s)" % Q)
            ck('page 3 of the set' in await toast(), "and it says where (%s)" % (await toast())[:70])
            P = await panel()
            it = P.get('items') or []
            ck([x['id'] for x in it] == Q and [x['no'] for x in it] == ['1', '2', '3'] and P.get('head') == '3 pages' and P.get('count') == 3,
               "the panel lists the set in its order, numbered: 3 pages (%s)" % [x['id'] for x in it])
            tag = await safe("()=>{var e=document.querySelector('#a3d-leftpanel [data-prpitem=\"board-access\"] .a3d-prptag');return e?e.textContent:null;}")
            ck(it and it[2]['board'] == 'access' and it[2]['name'] == 'Access and people' and tag == 'Board' and it[2]['cur'],
               "its page: named, tagged Board, the page on screen (%s)" % (it[2] if len(it) > 2 else None))
            ck((await safe("()=>window.__a3dPresRecord()") or {}).get('boards') == [{'id': 'board-access', 'kind': 'access'}], "the record: one board, by its kind")
            await safe("()=>window.__a3dUndo()")
            ck(await seq() == [s1, s2], "one undo takes it out of the set")
            await safe("()=>window.__a3dRedo()")
            ck(await seq() == [s1, s2, 'board-access'], "redo puts it back")
            await safe("()=>window.__a3dClbClose()")
            await tab('analyze')
            await safe("()=>window.__a3dSaGoto('access')")
            await page.wait_for_timeout(200)
            labels = await safe("()=>({open:[].filter.call(document.querySelectorAll('.a3d-analyze-wrap button'),function(b){return /Open the board/.test(b.textContent);}).length,show:[].map.call(document.querySelectorAll('.a3d-analyze-wrap [data-saact$=\"board\"]'),function(b){return b.textContent;})})") or {}
            ck(labels.get('open') == 0 and labels.get('show') and all(x == 'Show in Presentation' for x in labels['show']), "Analyze no longer opens a board itself: Show in Presentation (%s)" % labels)
            await page.click('.a3d-analyze-wrap [data-sacat="access"] [data-saact="accboard"]')
            await page.wait_for_timeout(500)
            c1 = await clb()
            ck(await safe("()=>document.getElementById('a3d-shell').dataset.tab") == 'presentation' and c1.get('open') and c1.get('kind') == 'access' and c1.get('board') == 'board-access' and c1.get('inView'),
               "it opens the board's page and shows Presentation (%s)" % c1)
            ck(await seq() == [s1, s2, 'board-access'], "a board already in the set is not added again")
            await safe("()=>window.__a3dRunCmd('climate')")
            await page.wait_for_timeout(500)
            c2 = await clb()
            ck(await seq() == [s1, s2, 'board-access', 'board-climate'] and c2.get('kind') == 'climate' and c2.get('board') == 'board-climate',
               "CLIMATE puts its board in the set and opens it (%s)" % await seq())
            await safe("()=>window.__a3dRunCmd('climate')")
            ck(await seq() == [s1, s2, 'board-access', 'board-climate'], "one of each kind")

            # ---------------------------------------------------------------------------------
            print("\n-- 7. in the main view")
            await safe("()=>window.__a3dPresOpen('board-access')")
            await page.wait_for_timeout(400)
            G = await safe("""()=>{var b=document.querySelector('.a3d-clb:not(.a3d-ssboard)'),v=document.querySelector('.a3d-vp'),lp=document.getElementById('a3d-leftpanel'),rb=b.getBoundingClientRect(),rv=v.getBoundingClientRect(),rp=lp.getBoundingClientRect();
              var hit=document.elementFromPoint(rp.left+rp.width/2,rp.top+rp.height/2),dock=document.getElementById('a3d-dock');
              return {b:[rb.left,rb.top,rb.width,rb.height].map(Math.round),v:[rv.left,rv.top,rv.width,rv.height].map(Math.round),panelW:Math.round(rp.width),panelHit:!!(hit&&lp.contains(hit)),
                dock:dock?getComputedStyle(dock).display:'none',role:b.getAttribute('role'),label:b.getAttribute('aria-label'),modal:b.getAttribute('aria-modal'),cls:b.className,body:document.body.classList.contains('a3d-clb-open')};}""") or {}
            ck(G.get('b') == G.get('v') and G.get('v') and G['v'][2] < 1440, "the board fills the main view and only it (%s in %s)" % (G.get('b'), G.get('v')))
            ck(G.get('panelW', 0) > 200 and G.get('panelHit'), "the panel beside it, not under it")
            ck(G.get('dock') == 'none', "nothing to draw with over a board: the dock steps aside")
            ck(G.get('role') == 'region' and G.get('label') == 'Access and people board' and not G.get('modal'), "a page, not a dialog (%s, %s)" % (G.get('role'), G.get('label')))
            c3 = await clb()
            ck(c3.get('cls') == 'a3d-clb' + width_cls(c3.get('w', 0)) and c3.get('narrow') is False and c3.get('w') == G['v'][2],
               "laid out by its own width, %d px: %s" % (c3.get('w', 0), c3.get('cls')))
            kp = await safe("()=>getComputedStyle(document.querySelector('.a3d-clb:not(.a3d-ssboard) .a3d-clb-kpis')).gridTemplateColumns.split(' ').length")
            await safe("()=>window.__a3dShellDrawer(false)")
            await page.wait_for_timeout(500)
            c4 = await clb()
            ck(c4.get('w', 0) > c3.get('w', 0) and c4.get('cls') == 'a3d-clb' + width_cls(c4['w']), "the panel shut, the board takes the room and lays out again (%s: %s)" % (c4.get('w'), c4.get('cls')))
            await safe("()=>window.__a3dShellDrawer(true,'presentation')")
            await page.wait_for_timeout(400)
            ck(kp and kp >= 3, "the indicators in a row across the main view (%s)" % kp)
            await page.focus('.a3d-clb:not(.a3d-ssboard) [data-clb="close"]')
            await page.keyboard.press('Escape')
            ck((await clb()).get('open') is False, "Esc gives the main view back")
            await safe("()=>window.__a3dPresOpen('board-access')")
            await tab('analyze')
            await page.focus('.a3d-analyze-wrap [data-anzsearch]')
            await page.keyboard.type('zz')
            await page.keyboard.press('Escape')
            ck((await clb()).get('open') is True and await safe("()=>document.querySelector('.a3d-analyze-wrap [data-anzsearch]').value") == '',
               "Esc in Analyze's search clears the search, and the board stays")
            await tab('presentation')
            await page.click('#a3d-leftpanel [data-prpitem="%s"]' % s1)
            await page.wait_for_timeout(400)
            ck((await clb()).get('open') is False and await safe("()=>window.__a3dPresPanel().items.filter(function(i){return i.cur;}).map(function(i){return i.id;})") == [s1],
               "a sheet's page opened from the panel takes the main view")
            await safe("()=>window.__a3dPresOpen('board-access')")
            await safe("(id)=>window.__a3dOpenSheetView(id)", s2)
            ck((await clb()).get('open') is False, "so does any view")

            # ---------------------------------------------------------------------------------
            print("\n-- 8. its thumbnail")
            await safe("()=>window.__a3dPresOpen('board-access')")
            await page.wait_for_timeout(1500)
            P = await panel()
            bi = [x for x in P.get('items', []) if x['id'] == 'board-access']
            h1 = await safe("()=>document.querySelector('.a3d-clb:not(.a3d-ssboard) .a3d-clb-h1').textContent")
            fr = await safe("""()=>{var f=document.querySelector('#a3d-leftpanel iframe[data-prpbframe="board-access"]'),b=f.parentNode.getBoundingClientRect(),d=f.contentDocument,r=d.querySelector('.a3d-clb');
              return {boxW:b.width,boxH:b.height,pe:getComputedStyle(f).pointerEvents,aria:f.getAttribute('aria-hidden'),tab:f.getAttribute('tabindex'),
                cls:r?r.className:null,bg:r?getComputedStyle(r).backgroundColor:null,bar:r&&r.querySelector('.a3d-clb-bar')?getComputedStyle(r.querySelector('.a3d-clb-bar')).display:null,figs:d.querySelectorAll('.a3d-clb-card').length};}""") or {}
            ck(bi and bi[0]['drawn'] and bi[0]['thumbTitle'] == h1, "the thumbnail is the board itself (%s)" % (bi[0]['thumbTitle'] if bi else None))
            ck(fr.get('cls') == 'a3d-clb prt w-l' and fr.get('bg') == 'rgb(255, 255, 255)' and fr.get('bar') == 'none' and fr.get('figs', 0) >= 8,
               "as it prints: on paper, wide, without its bar, every figure (%s)" % fr)
            ck(abs(fr.get('boxW', 0) / 1280 - float(re.findall(r'[\d.]+', bi[0]['scale'] or '0')[0])) < 0.002 and abs(fr.get('boxH', 0) / fr.get('boxW', 1) - 297 / 420) < 0.01,
               "scaled to the column, an A3 landscape page (%s)" % (bi[0]['scale'] if bi else None))
            ck(fr.get('pe') == 'none' and fr.get('aria') == 'true' and fr.get('tab') == '-1', "a picture, not a second board: no pointer, no focus, hidden from a reader")
            await safe("""()=>{window.__a3dSelectFor([]);window.__a3dSetPropTab('site');window.__a3dRefreshProps();var L=document.querySelectorAll('#a3d-propsbody input'),i;
              for(i=0;i<L.length;i++)if(L[i].getAttribute('data-propmodel')==='site'){L[i].value='Harbour Yard';L[i].dispatchEvent(new Event('change',{bubbles:true}));}}""")
            await page.wait_for_timeout(1500)
            P = await panel()
            bi = [x for x in P.get('items', []) if x['id'] == 'board-access']
            ck(bi and bi[0]['drawn'] and bi[0]['thumbTitle'] == 'Harbour Yard: access and people', "the thumbnail follows the model (%s)" % (bi[0]['thumbTitle'] if bi else None))

            # ---------------------------------------------------------------------------------
            print("\n-- 9. the order")
            drag = """(a)=>{var h=document.querySelector('#a3d-leftpanel .a3d-pres-wrap'),src=h.querySelector('[data-prpitem="'+a[0]+'"]'),dst=h.querySelector('[data-prpitem="'+a[1]+'"]');
              if(!src||!dst)return false;var dt=new DataTransfer(),r=dst.getBoundingClientRect(),y=a[2]?r.bottom-3:r.top+3;
              src.dispatchEvent(new DragEvent('dragstart',{bubbles:true,dataTransfer:dt}));
              dst.dispatchEvent(new DragEvent('dragover',{bubbles:true,cancelable:true,dataTransfer:dt,clientY:y}));
              dst.dispatchEvent(new DragEvent('drop',{bubbles:true,cancelable:true,dataTransfer:dt,clientY:y}));
              src.dispatchEvent(new DragEvent('dragend',{bubbles:true,dataTransfer:dt}));return true;}"""
            await safe(drag, ['board-access', s1, False])
            await page.wait_for_timeout(200)
            ck(await seq() == ['board-access', s1, s2, 'board-climate'] and [s['id'] for s in await safe("()=>window.__a3dSheets()")] == [s1, s2],
               "a board dragged to the front: the sheets keep their order (%s)" % await seq())
            await safe("()=>window.__a3dUndo()")
            ck(await seq() == [s1, s2, 'board-access', 'board-climate'], "one undo step")
            await safe("()=>window.__a3dRedo()")
            await safe(drag, [s2, 'board-access', False])
            await page.wait_for_timeout(200)
            tabs = await safe("()=>[].map.call(document.querySelectorAll('#a3d-laytabs [data-ltsheet]'),function(b){return b.getAttribute('data-ltsheet');})")
            ck(await seq() == [s2, 'board-access', s1, 'board-climate'] and [s['id'] for s in await safe("()=>window.__a3dSheets()")] == [s2, s1] and tabs == [s2, s1],
               "a sheet dragged past a board: the sheets, and their tabs, take the new order (%s, tabs %s)" % (await seq(), tabs))
            mi = await safe("()=>window.__a3dBoardMenuItems('board-access')")
            ck(mi == ['Present from this page', '-', 'Open', 'Print…', '-', 'Move up', 'Move down', '-', 'Remove from the set'], "a board's own menu (%s)" % mi)
            await safe("()=>window.__a3dBoardMenuDo('earlier','board-access')")
            ck(await seq() == ['board-access', s2, s1, 'board-climate'], "Move up")
            smi = await safe("(id)=>window.__a3dSheetMenuItems(id,'pages')", s2)
            ck('Move up' in smi and 'Move down' in smi, "a sheet's menu moves it in the set, boards and all (%s)" % [x for x in smi if 'Move' in x])
            await safe("(id)=>{var it=document.querySelector('#a3d-leftpanel [data-prpitem=\"'+id+'\"]');it.dispatchEvent(new MouseEvent('contextmenu',{bubbles:true,cancelable:true,clientX:120,clientY:300}));}", s2)
            await page.click('#a3d-ltmenu [data-ltm="earlier"]')
            ck(await seq() == [s2, 'board-access', s1, 'board-climate'], "its Move up, from the page's own menu, steps over the board")
            await page.click('#a3d-leftpanel [data-prpact="new"]')
            await page.wait_for_timeout(400)
            Q = await seq()
            ck(len(Q) == 5 and Q[:4] == [s2, 'board-access', s1, 'board-climate'] and Q[4] not in Q[:4], "+ Page: a new sheet, the last page (%s)" % Q)
            s3 = Q[4]
            await safe("()=>window.__a3dBoardMenuDo('remove','board-access')")
            ck(await seq() == [s2, s1, 'board-climate', s3] and 'out of the set' in await toast() and (await safe("()=>window.__a3dAcc()") or {}).get('access'),
               "out of the set; its data stays in Analyze (%s)" % await seq())
            await safe("()=>window.__a3dUndo()")
            ck(await seq() == [s2, 'board-access', s1, 'board-climate', s3], "undone, back in its place")

            # ---------------------------------------------------------------------------------
            print("\n-- 10. Present")
            await safe("()=>window.__a3dPresOpen('board-access')")
            await safe("()=>window.__a3dSlideshowStart('board-access')")
            await page.wait_for_timeout(700)
            S = await safe("()=>window.__a3dSlideshow()") or {}
            ck(S.get('on') and S.get('board') == 'access' and S.get('boardShown') == 'board-access' and not S.get('canvasShown') and S.get('pos') == '2 / 5' and S.get('n') == 5,
               "Present from the board: its page, 2 of 5, the canvas aside (%s)" % {k: S.get(k) for k in ('board', 'boardShown', 'canvasShown', 'pos')})
            ck(S.get('boardTitle') == 'Harbour Yard: access and people' and await safe("()=>document.querySelectorAll('.a3d-clb:not(.a3d-ssboard)').length") == 0,
               "the board as on screen, and the only one: the main view's has stepped aside")
            pad = await safe("()=>getComputedStyle(document.querySelector('.a3d-ssboard .a3d-clb-page')).paddingTop")
            ck(pad == '46px', "room above it for Present's hint (%s)" % pad)
            await safe("()=>window.__a3dSlideshowStart&&document.querySelector('[data-ssact=\"next\"]').click()")
            await page.wait_for_timeout(500)
            S = await safe("()=>window.__a3dSlideshow()") or {}
            ck(S.get('id') == s1 and S.get('canvasShown') and S.get('boardShown') is None and S.get('shown') == s1, "the next page, a sheet, drawn as ever (%s)" % S.get('id'))
            await safe("()=>document.querySelector('[data-ssact=\"prev\"]').click()")
            await page.wait_for_timeout(400)
            wh = await safe("""()=>{var b=document.querySelector('.a3d-ssboard'),i0=window.__a3dSlideshow().idx;b.scrollTop=0;
              b.dispatchEvent(new WheelEvent('wheel',{bubbles:true,cancelable:true,deltaY:400}));return {i0:i0,i1:window.__a3dSlideshow().idx,sh:b.scrollHeight,ch:b.clientHeight};}""") or {}
            ck(wh.get('i0') == 1 and wh.get('i1') == 1 and wh.get('sh', 0) > wh.get('ch', 0), "the wheel over a long board scrolls it, not the pages (%s)" % wh)
            wh2 = await safe("""()=>{var b=document.querySelector('.a3d-ssboard');b.scrollTop=b.scrollHeight;
              b.dispatchEvent(new WheelEvent('wheel',{bubbles:true,cancelable:true,deltaY:400}));return window.__a3dSlideshow().idx;}""")
            ck(wh2 == 2, "at its end, the wheel goes on to the next page (%s)" % wh2)
            await safe("()=>document.querySelector('[data-ssact=\"prev\"]').click()")
            await page.wait_for_timeout(300)
            await safe("()=>window.__a3dSlideshowEnd()")
            await page.wait_for_timeout(300)
            c5 = await clb()
            ck(c5.get('open') and c5.get('kind') == 'access' and c5.get('inView') and await safe("()=>document.querySelectorAll('.a3d-ssboard').length") == 0,
               "ended on a board, back on it in the main view (%s)" % c5.get('kind'))
            await safe("()=>window.__a3dSlideshowStart('board-climate')")
            await page.wait_for_timeout(400)
            await safe("()=>document.querySelector('[data-ssact=\"next\"]').click()")
            await page.wait_for_timeout(400)
            await safe("()=>window.__a3dSlideshowEnd()")
            await page.wait_for_timeout(300)
            ck((await clb()).get('open') is False and await safe("()=>window.__a3dPresPanel().items.filter(function(i){return i.cur;}).map(function(i){return i.id;})") == [s3],
               "started on a board, ended on a sheet: that sheet")

            # ---------------------------------------------------------------------------------
            print("\n-- 11. print")
            R = await safe("""()=>{var r=window.__a3dPrintSetHtml();return {n:r.n,lost:r.lost,bad:r.bad,ids:(r.html.match(/data-page="[^"]+"/g)||[]).map(function(x){return x.slice(11,-1);}),
              brd:(r.html.match(/class="a3dbrd"/g)||[]).length,pg:(r.html.match(/class="a3dpg"/g)||[]).length,page:r.html.indexOf('@page a3dbrd{size:420mm 297mm;margin:10mm}')>=0,
              prt:(r.html.match(/class="a3d-clb prt w-l"/g)||[]).length,css:r.html.indexOf('.a3d-clb.prt')>=0,html:r.html};}""") or {}
            ck(R.get('n') == 5 and R.get('ids') == await seq() and R.get('lost') == [] and R.get('bad') == [], "Print set: every page, in the set's order (%s)" % R.get('ids'))
            ck(R.get('brd') == 2 and R.get('pg') == 3 and R.get('page') and R.get('prt') == 2 and R.get('css'),
               "the boards on A3 landscape pages of their own, in their print look, their style with them")
            p2 = await ctx.new_page()
            await p2.set_content(R.get('html', '').replace('window.print()', 'void 0'))
            await p2.emulate_media(media='print')
            pl = await p2.evaluate("""()=>{var b=document.querySelector('.a3dbrd .a3d-clb'),s=getComputedStyle(b);return {bg:s.backgroundColor,ink:s.getPropertyValue('--ink').trim(),s7:s.getPropertyValue('--s7').trim(),
              bar:getComputedStyle(b.querySelector('.a3d-clb-bar')).display,pageAttr:getComputedStyle(b.parentNode).page,figs:b.querySelectorAll('.a3d-clb-card').length};}""")
            ck(pl.get('bg') == 'rgb(255, 255, 255)' and pl.get('ink') == '#0b0b0b' and pl.get('s7') == '#6250d6' and pl.get('bar') == 'none' and pl.get('pageAttr') == 'a3dbrd',
               "printed: white paper, the print tokens, no bar, on its named page (%s)" % pl)
            await p2.close()
            await safe("()=>{window.__pw=null;window.__wo=window.open;window.open=function(){return {document:{write:function(h){window.__pw=h;},close:function(){}}};};}")
            await safe("()=>window.__a3dPresOpen('board-access')")
            await page.click('.a3d-clb:not(.a3d-ssboard) [data-clb="print"]')
            pw1 = await safe("()=>window.__pw||''") or ''
            ck('a3d-clb prt w-l' in pw1 and '@page{size:420mm 297mm;margin:10mm}' in pw1 and 'Harbour Yard: access and people' in pw1 and 'Printing Access and people' in await toast(),
               "the board's Print: alone, on A3 landscape, in a print window")
            await page.click('#a3d-leftpanel [data-prpact="print"]')
            pw2 = await safe("()=>window.__pw||''") or ''
            ck(pw2.count('class="a3dbrd"') == 2 and 'Printing 5 pages' in await toast(), "Print set, from the panel: 5 pages (%s)" % (await toast())[:40])
            await safe("()=>{window.open=window.__wo;}")
            bp = await safe("""()=>{window.dispatchEvent(new Event('beforeprint'));var b=document.querySelector('.a3d-clb:not(.a3d-ssboard)'),a={parent:b.parentNode===document.body,cls:b.className};
              window.dispatchEvent(new Event('afterprint'));b=document.querySelector('.a3d-clb:not(.a3d-ssboard)');a.back=!!(b.parentNode.classList&&b.parentNode.classList.contains('a3d-vp'));return a;}""") or {}
            ck(bp.get('parent') and 'w-l' in (bp.get('cls') or '') and bp.get('back'), "the browser's own print: the board alone on the paper, then back in the main view (%s)" % bp)

            # ---------------------------------------------------------------------------------
            print("\n-- 12. kept with the project")
            env = json.loads(await safe("()=>window.__a3dProjectEnvelope()") or '{}')
            pr = (env.get('data') or {}).get('pres') or {}
            before0 = await seq()
            ck([b['kind'] for b in pr.get('boards', [])] == ['access', 'climate'] and 'board-access' in pr.get('order', []), "saved in the project file: the boards and the order (%s)" % pr)
            await safe("(t)=>window.__a3dImportProject(t,'set.json')", json.dumps(env))
            await page.wait_for_timeout(800)
            ck(await seq() == before0, "a project opened from the file has its set, in its order (%s)" % await seq())
            bad = dict(env)
            bad['data'] = dict(env['data'])
            bad['data']['pres'] = {'boards': [{'kind': 'nope'}, {'kind': 'access'}, {'kind': 'access'}, None, 'x'], 'order': [1, 'board-access', None, 'zz']}
            await safe("(t)=>window.__a3dImportProject(t,'bad.json')", json.dumps(bad))
            await page.wait_for_timeout(800)
            rec = await safe("()=>window.__a3dPresRecord()") or {}
            ck(rec.get('boards') == [{'id': 'board-access', 'kind': 'access'}] and rec.get('order') == ['board-access', 'zz'] and (await seq())[0] == 'board-access',
               "a bad record: one board of a kind it knows, an order of names (%s)" % rec)
            await safe("(t)=>window.__a3dImportProject(t,'set2.json')", json.dumps(env))
            await page.wait_for_timeout(1500)
            before = await seq()
            await page.reload()
            await page.wait_for_timeout(2500)
            await safe("()=>window.__a3dEnter()")
            await page.wait_for_timeout(300)
            ck(await seq() == before, "kept over a reload (%s)" % await seq())
            ck(not errs, "no page errors (%s)" % errs[:3])
            await ctx.close()

            # ---------------------------------------------------------------------------------
            print("\n-- 13. a tablet and a phone")
            for name, vw, vh, sc in (('a tablet', 1024, 768, 1), ('a phone', 390, 844, 2)):
                c2x, p3, e3 = await open_page(vw, vh, sc)
                await prepare(pg=p3)
                await safe("()=>window.__a3dBoardShow('access')", pg=p3)
                await p3.wait_for_timeout(700)
                cs = await clb(pg=p3)
                g = await safe("""()=>{var b=document.querySelector('.a3d-clb:not(.a3d-ssboard)'),v=document.querySelector('.a3d-vp'),sh=document.getElementById('a3d-shell'),lp=document.getElementById('a3d-leftpanel').getBoundingClientRect();
                  return {vw:Math.round(v.getBoundingClientRect().width),sw:b.scrollWidth,cw:b.clientWidth,docw:document.documentElement.scrollWidth,collapsed:sh.classList.contains('collapsed'),
                    lp:Math.round(lp.right),vb:[].map.call(b.querySelectorAll('.a3d-clb-card svg[role="img"]'),function(s){return +s.getAttribute('viewBox').split(' ')[2];})};}""", pg=p3) or {}
                ck(cs.get('open') and cs.get('inView') and cs.get('w') == g.get('vw') and cs.get('cls') == 'a3d-clb' + width_cls(g.get('vw', 0)),
                   "on %s the board is in the main view, laid out by its width (%d: %s)" % (name, g.get('vw', 0), cs.get('cls')))
                ck(g.get('sw', 999) <= g.get('cw', 0) + 1 and g.get('docw', 999) <= vw + 1, "nothing spills across on %s" % name)
                if vw < 760:
                    ck(g.get('collapsed') and cs.get('narrow') and g.get('vb') and all(x <= 380 for x in g['vb']), "on a phone the drawer makes way, and the charts are drawn for it (%s)" % g.get('vb', [])[:4])
                else:
                    ck(cs.get('narrow') == (g.get('vw', 0) < 760), "on a tablet, drawn for the width it has (%s)" % g.get('vw'))
                await safe("()=>window.__a3dShellDrawer(true,'presentation')", pg=p3)
                await p3.wait_for_timeout(1200)
                pp = await panel(pg=p3)
                ck(any(x['id'] == 'board-access' and x['drawn'] for x in pp.get('items', [])), "and its page in Presentation, with its thumbnail, on %s" % name)
                ck(not e3, "no page errors on %s (%s)" % (name, e3[:3]))
                await c2x.close()
        except Stalled as e:
            ck(False, 'the harness stalled: %s' % e)
        except Exception:
            traceback.print_exc()
            ck(False, 'the suite raised')
        await browser.close()


def main():
    asyncio.run(run())
    print("\n%d/%d checks passed" % (CK.n - len(CK.bad), CK.n))
    if CK.bad:
        for b in CK.bad:
            print("  FAILED: " + b)
        print("RESULT: FAIL")
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == '__main__':
    sys.exit(main())
