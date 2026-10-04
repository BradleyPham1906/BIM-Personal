#!/usr/bin/env python3
"""bim_phase148_analyze_layers_browser_tests.py -- V148: Analyze as a list; results as layers.

Measured in the browser:
  1. THE LIST: four groups (Model, Site and terrain, Structure, Environment), each analysis a row:
     its name, what it shows, its state and its first action on one line, the rest a click away;
     a row opens in place, and stays open through a reload. Off is said, not shown.
  2. THE SEARCH matches the starts of words (rain is not terrain), the group's name and the buttons;
     it survives the panel refreshing, as does the scroll.
  3. ADD AS LAYER: sun hours and rain kept as run -- the picture checked cell by cell against the
     run -- drawn once (the live overlay steps aside), out of date when the model changes, updated
     on the layer's own date; a terrain's slope or cut and fill follows its surface, gone when the
     surface is.
  4. LAYERS: Analysis and Data sections; a row opens to its opacity (live while dragged, one undo
     step when let go), legend, what it is, Update, Rename, Remove; the eye; drag to reorder, the top
     drawn last; the data layers' eye, opacity, name and removal are the V134 layer's own.
  5. SAVED: through a reload and in a project file; an undo takes one back; a History restore
     leaves them as they are; a damaged one is let go of.
  6. A PHONE, A TABLET, A COMPUTER: rows sized for a finger on a touch screen, nothing wider than
     the panel, and the Project Browser's tree no longer lies over Analyze or Layers on a phone.

The harness never waits without a bound (V123).
"""
import asyncio, json, pathlib, re, sys, traceback
from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'

LAT, LON, TZ, DATE, DATE2 = 40.0, -75.0, -5.0, '2026-12-21', '2026-06-21'
TWO = [[x, z, min(((x + 12) ** 2 + z * z), ((x - 12) ** 2 + z * z)) / 50.0, '', ''] for x in range(-24, 25, 2) for z in range(-12, 13, 2)]


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


def mk_safe(page):
    async def safe(js, arg=None):
        try:
            return await within(page.evaluate(js, arg) if arg is not None else page.evaluate(js), 'evaluate ' + js[:50])
        except Stalled:
            raise
        except Exception as e:
            print('      (evaluate failed: %s)' % str(e)[:200])
            return None
    return safe


ROWS = """()=>{var w=document.querySelector('.a3d-analyze-wrap');if(!w)return null;
  return [].map.call(w.querySelectorAll('[data-anzcard]'),function(c){var hd=c.querySelector('.a3d-anzhd'),b=c.querySelector('.a3d-anzbody'),st=c.querySelector('.a3d-anzstate');
    return {id:c.getAttribute('data-anzcard'),grp:c.closest('[data-anzgrp]').getAttribute('data-anzgrp'),open:c.classList.contains('open'),
      hidden:c.hasAttribute('hidden'),h:Math.round(hd.getBoundingClientRect().height),bodyH:Math.round(b.getBoundingClientRect().height),
      tog:hd.querySelectorAll('[data-anztog]').length,first:(hd.querySelector('[data-anzact]')||{getAttribute:function(){return null;}}).getAttribute('data-anzact'),
      state:st?st.textContent:null,stateW:st?Math.round(st.getBoundingClientRect().width):null,sum:(c.querySelector('.a3d-anzsum')||{}).textContent,
      st:(c.querySelector('.a3d-anzst')||{}).textContent,aria:(hd.querySelector('[data-anztog]')||{getAttribute:function(){return null;}}).getAttribute('aria-expanded'),
      acts:[].map.call(c.querySelectorAll('[data-anzact]'),function(x){return [x.getAttribute('data-anzact'),x.textContent,x.disabled,x.title];})};});}"""

LYROWS = """()=>[].map.call(document.querySelectorAll('#a3d-leftpanel [data-lyres]'),function(e){var b=e.querySelector('.a3d-lybadge'),r=e.getBoundingClientRect();
  return {key:e.getAttribute('data-lyres'),name:(e.querySelector('.a3d-lynm')||{}).textContent,badge:b?b.textContent:null,sel:e.classList.contains('sel'),dim:e.classList.contains('dim'),h:Math.round(r.height),
    sec:e.closest('[data-lysec]').getAttribute('data-lysec')};})"""


async def run():
    ck = CK
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1500, 'height': 950})
        page = await ctx.new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))

        async def answer(route):
            await route.fulfill(status=200, headers={'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                                body=json.dumps({'type': 'FeatureCollection', 'features': [
                                    {'type': 'Feature', 'properties': {'zone': 'R1'}, 'geometry': {'type': 'Polygon', 'coordinates': [[
                                        [LON - 0.0002, LAT - 0.0002], [LON + 0.0002, LAT - 0.0002], [LON + 0.0002, LAT + 0.0002], [LON - 0.0002, LAT + 0.0002], [LON - 0.0002, LAT - 0.0002]]]}}]}))
        await ctx.route('https://data.example.org/**', answer)
        await within(page.goto('file://' + str(HTML)), 'goto')
        await page.wait_for_timeout(2300)
        safe = mk_safe(page)

        has = await safe("()=>window.__acad3dV148")
        ck(bool(has) and 'addaslayer' in has and 'anzlist' in has, "__acad3dV148 marker is present (%s)" % has)
        if not has:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.bad), ck.n))
            await browser.close()
            return 1
        mv = re.search(r"var BIM_APP_VERSION=\{v:'V(\d+)'", HTML.read_text(encoding='utf-8'))
        ck(mv and int(mv.group(1)) >= 148, "the app says V148 or later (%s)" % (mv and mv.group(1)))

        async def toast():
            return await safe("()=>{var t=document.getElementById('a3d-toast');return t?t.textContent:'';}") or ''

        async def rows():
            return {r['id']: r for r in (await safe(ROWS) or [])}

        async def layers():
            return await safe("()=>window.__a3dResultLayers()") or []

        async def lyrows():
            return await safe(LYROWS) or []

        async def tab(t):
            await page.click('#a3d-rail [data-tab="%s"]' % t)
            await page.wait_for_timeout(250)

        async def set_site(date=DATE):
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dSetPropTab('site');window.__a3dRefreshProps();}")
            for k, v in (('sunlat', repr(LAT)), ('sunlon', repr(LON)), ('suntz', repr(TZ)), ('sundate', date)):
                await page.fill('#a3d-propsbody [data-propmodel="%s"]' % k, v)
                await page.keyboard.press('Enter')
                await page.wait_for_timeout(60)

        async def pixel(x, z):
            """the colour of the plan at a model point"""
            p = await safe("""(a)=>{var c=document.getElementById('a3d-canvas'),r=c.getBoundingClientRect(),q=window.__a3dProject([a[0],0,a[1]]);
              return [r.left+q.x,r.top+q.y];}""", [x, z])
            shot = await page.screenshot(clip={'x': p[0] - 2, 'y': p[1] - 2, 'width': 4, 'height': 4})
            return shot

        try:
            await safe("()=>{window.__a3dEnter();window.__a3dSetPlanView&&window.__a3dSetPlanView();window.__a3dTestSetObjs([]);}")
            await page.wait_for_timeout(200)

            # ---------------------------------------------------------------------------------
            print("\n-- 1. the list")
            await tab('analyze')
            R = await rows()
            order = await safe("()=>[].map.call(document.querySelectorAll('.a3d-analyze-wrap .a3d-anzgrphd'),function(e){return e.textContent;})")
            ck(order == ['Model', 'Site and terrain', 'Structure', 'Environment'], "four groups, in order: Model, Site and terrain, Structure, Environment (%s)" % order)
            G = {}
            for r in R.values():
                G.setdefault(r['grp'], []).append(r['id'])
            ck(G == {'model': ['lens', 'areas', 'lod', 'stats'], 'site': ['survey', 'terrain', 'grading', 'rain'], 'structure': ['structure'], 'env': ['sun', 'sunhours', 'solar']},
               "each analysis in its group (%s)" % G)
            ck(all(not r['open'] and r['bodyH'] == 0 and r['aria'] == 'false' for r in R.values()), "every row starts closed: its body takes no room")
            ck(all(r['tog'] == 1 for r in R.values()), "each row has one control that opens it")
            cards = {c['id']: c for c in await safe("()=>window.__a3dAnalyzeCards()") or []}
            ck(all(R[k]['first'] == cards[k]['acts'][0]['act'] for k in cards), "its first action is on its line, without opening it")
            ck(all(R[k]['sum'] == cards[k]['status'] and R[k]['st'] == cards[k]['status'] for k in cards), "and what it shows: one line on the row, whole when it opens")
            ck(all(36 <= r['h'] <= 52 for r in R.values()), "a row is one line of a list, 36 to 52 px, not a card (%s)" % sorted(set(r['h'] for r in R.values())))
            off = [r for r in R.values() if r['state'] == 'Off']
            ck(off and all(r['stateW'] <= 1 for r in off), "an analysis that is off says so to a screen reader, and shows no chip (%d rows)" % len(off))
            titles = [c['title'] for c in cards.values()]
            ck(all(t[0].isupper() and t[1:] == t[1:].replace(' On', ' on') and not re.search(r' [A-Z][a-z]', t.replace('LOD', '')) for t in titles),
               "names in sentence case, as the rest of the panels (%s)" % titles)
            await page.click('.a3d-analyze-wrap [data-anztog="sunhours"]')
            await page.wait_for_timeout(120)
            await safe("()=>{document.querySelector('.a3d-analyze-wrap [data-anzcard=\"sunhours\"]').__v148=1;}")
            R = await rows()
            ck(R['sunhours']['open'] and R['sunhours']['bodyH'] > 20 and R['sunhours']['aria'] == 'true', "a click opens a row: its whole status and its other actions (%d px)" % R['sunhours']['bodyH'])
            ck([a[0] for a in R['sunhours']['acts']] == ['sunhours:run', 'sim:clear:sun', 'open:Location', 'layer:sunhours'], "Run, then Clear, Date and Add as layer (%s)" % R['sunhours']['acts'])
            await page.click('.a3d-analyze-wrap [data-anztog="sunhours"]')
            await page.wait_for_timeout(120)
            R = await rows()
            ck(not R['sunhours']['open'] and R['sunhours']['bodyH'] == 0, "and a second click closes it")
            ck(await safe("()=>document.querySelector('.a3d-analyze-wrap [data-anzcard=\"sunhours\"]').__v148===1"), "in place: the row is the same node")
            await page.click('.a3d-analyze-wrap [data-anztog="rain"]')
            await page.wait_for_timeout(1300)
            await within(page.reload(), 'reload')
            await page.wait_for_timeout(2300)
            await safe("()=>{window.__a3dEnter();window.__a3dSetPlanView&&window.__a3dSetPlanView();}")
            await tab('analyze')
            R = await rows()
            ck(R['rain']['open'] and not R['sunhours']['open'], "the rows opened stay open through a reload, in this browser")
            await safe("()=>window.__a3dAnzToggle('rain',false)")

            # ---------------------------------------------------------------------------------
            print("\n-- 2. the search")
            s = await safe("(q)=>window.__a3dAnzSearch(q)", 'rain')
            ck(s == ['rain'], "'rain' finds Rain on terrain, not every row that says terrain (%s)" % s)
            s = await safe("(q)=>window.__a3dAnzSearch(q)", 'arrows')
            ck(s == ['grading'], "'arrows' finds the row whose button is Slope arrows: the buttons are searched too (%s)" % s)
            s = await safe("(q)=>window.__a3dAnzSearch(q)", 'environment')
            ck(s == ['sun', 'sunhours', 'solar'], "a group's name finds its rows (%s)" % s)
            s = await safe("(q)=>window.__a3dAnzSearch(q)", 'sun hours')
            ck(s == ['sunhours'], "two words, both at the start of words (%s)" % s)
            ck(await safe("(a)=>[window.__a3dAnzWordsHit(a[0],a[1]),window.__a3dAnzWordsHit(a[2],a[1])]", ['rain', 'Slope on the terrain', 'ter']) == [False, True],
               "the rule: a word asked for starts a word of the text")
            s = await safe("(q)=>window.__a3dAnzSearch(q)", 'zzzq')
            nm = await safe("()=>{var e=document.querySelector('.a3d-analyze-wrap .a3d-anzempty'),g=[].filter.call(document.querySelectorAll('.a3d-analyze-wrap [data-anzgrp]'),function(x){return x.getBoundingClientRect().height>0;});return [!!e&&e.getBoundingClientRect().height>0,g.length];}")
            ck(s == [] and nm == [True, 0], "nothing found: 'Nothing matches', and no empty group headings (%s)" % nm)
            await safe("(q)=>window.__a3dAnzSearch(q)", '')
            await page.click('.a3d-analyze-wrap [data-anzsearch]')
            await page.keyboard.type('sola')   # not 'sol': solids, in Buildings, LOD and solids, start so too
            await page.wait_for_timeout(100)
            vis = [k for k, r in (await rows()).items() if not r['hidden']]
            ck(vis == ['solar'], "typed into the field, the list narrows as it is typed (%s)" % vis)
            await safe("()=>window.__a3dColumnAt([200,200],0,1,1,3)")
            await safe("()=>window.__a3dRefreshProps()")
            await page.wait_for_timeout(150)
            f = await safe("()=>{var a=document.activeElement;return [a&&a.getAttribute('data-anzsearch'),a&&a.value];}")
            vis = [k for k, r in (await rows()).items() if not r['hidden']]
            ck(f == ['1', 'sola'] and vis == ['solar'], "the model changes and the panel refreshes: the search keeps its text, its focus and its rows (%s, %s)" % (f, vis))
            await page.keyboard.press('Escape')
            await page.wait_for_timeout(100)
            vis = [k for k, r in (await rows()).items() if not r['hidden']]
            ck(len(vis) == 12 and await safe("()=>document.querySelector('.a3d-analyze-wrap [data-anzsearch]').value") == '', "Escape empties it: every row again")
            # the left panel is the one scroll container (V65)
            sc = await safe("()=>{var a=document.getElementById('a3d-leftpanel');window.__a3dAnzOpenAll(true);a.scrollTop=a.scrollHeight;return a.scrollTop;}")
            await safe("()=>window.__a3dColumnAt([210,200],0,1,1,3)")
            await safe("()=>window.__a3dRefreshProps()")
            await page.wait_for_timeout(150)
            sc2 = await safe("()=>document.getElementById('a3d-leftpanel').scrollTop")
            ck(sc and sc > 50 and abs(sc2 - sc) <= 2, "and the list keeps its scroll (%s -> %s)" % (sc, sc2))
            await safe("()=>{window.__a3dAnzOpenAll(false);window.__a3dTestSetObjs([]);}")

            # ---------------------------------------------------------------------------------
            print("\n-- 3. Add as layer: sun hours")
            await set_site()
            await safe("()=>window.__a3dCamSet({tx:0,tz:0,dist:90})")
            await tab('analyze')
            await safe("()=>window.__a3dAnzToggle('sunhours',true)")
            R = await rows()
            la = [a for a in R['sunhours']['acts'] if a[0] == 'layer:sunhours'][0]
            ck(la[2] and la[3] == 'Run it first', "Add as layer waits for a run (%s)" % la)
            col = await safe("()=>window.__a3dColumnAt([0,0],0,6,6,15)")
            await page.wait_for_timeout(150)
            px_bg = await pixel(12, 9)
            sh = await safe("()=>window.__a3dSunHours({margin:25,cell:1})") or {}
            await page.wait_for_timeout(150)
            px_live = await pixel(12, 9)
            R = await rows()
            la = [a for a in R['sunhours']['acts'] if a[0] == 'layer:sunhours'][0]
            ck(not la[2] and la[1] == 'Add as layer', "after a run, Add as layer is there (%s)" % la)
            await page.click('.a3d-analyze-wrap [data-anzact="layer:sunhours"]')
            await page.wait_for_timeout(200)
            L = await layers()
            ck(len(L) == 1 and L[0]['kind'] == 'sunhours' and L[0]['name'] == 'Sun hours, ' + DATE and L[0]['visible'] and L[0]['opacity'] == 0.6 and not L[0]['stale'],
               "one layer: Sun hours, its date, shown, at 60%% (%s)" % L)
            sid = L[0]['id'] if L else None
            ck('is a layer now' in await toast(), "and the toast says where it went (%s)" % await toast())
            d = await safe("(i)=>window.__a3dResultLayerData(i)", sid) or {}
            ok = d.get('nx') == sh.get('nx') and d.get('nz') == sh.get('nz') and len(d.get('cells', '')) == sh['nx'] * sh['nz']
            bad = 0
            if ok:
                for k in range(len(d['cells'])):
                    c = d['cells'][k]
                    if sh['roof'][k]:
                        bad += c != '.'
                    else:
                        want = min(7, int(max(0, min(1, sh['hours'][k] / sh['day'] if sh['day'] else 0)) * 8))
                        bad += c != str(want)
            ck(ok and bad == 0, "its picture is the run's, cell by cell: the ramp's place, a roof left clear (%d of %d differ)" % (bad, len(d.get('cells', ''))))
            ck(await safe("()=>window.__a3dSimHolds().sun") and await safe("()=>window.__a3dResultDrawn()") == [sid],
               "it is drawn as the layer, and the live overlay steps aside: drawn once")
            px_layer = await pixel(12, 9)
            ck(px_layer != px_live, "at 60% rather than the live 55%: the plan shows the layer")
            R = await rows()
            la = [a for a in R['sunhours']['acts'] if a[0] == 'layer:sunhours'][0]
            ck(la[2] and 'already' in la[3], "the same run cannot be added twice (%s)" % la[3])

            # ---------------------------------------------------------------------------------
            print("\n-- 4. Layers: the Analysis section")
            await tab('layers')
            secs = await safe("()=>[].map.call(document.querySelectorAll('#a3d-leftpanel .a3d-lyp [data-lysec]'),function(e){return [e.getAttribute('data-lysec'),e.querySelector('.a3d-lysecttl').textContent,e.querySelector('.a3d-lycnt').textContent];})")
            ck(secs == [['analysis', 'Analysis', '1'], ['data', 'Data', '']], "below the layer tree: Analysis (1) and Data (%s)" % secs)
            after = await safe("()=>{var l=document.querySelector('#a3d-leftpanel [data-lylist]'),s=document.querySelector('#a3d-leftpanel [data-lysec=\"analysis\"]');return l.getBoundingClientRect().bottom<=s.getBoundingClientRect().top+1;}")
            ck(after, "after the layers, not among them")
            hint = await safe("()=>(document.querySelector('#a3d-leftpanel [data-lysec=\"data\"] .a3d-lyhint')||{}).textContent")
            ck(hint and 'Data Layers' in hint, "an empty Data section says where its layers come from (%s)" % hint)
            Y = await lyrows()
            ck(len(Y) == 1 and Y[0]['key'] == 'res:' + sid and Y[0]['sel'], "the new layer's row, opened (%s)" % Y)
            det = await safe("""()=>{var d=document.querySelector('#a3d-leftpanel [data-lyresd]');if(!d)return null;var r=d.querySelector('[data-lyresop]');
              return {op:r&&r.value,lab:(d.querySelector('.a3d-lyopv')||{}).textContent,ramp:d.querySelectorAll('.a3d-anzramp i').length,meta:(d.querySelector('.a3d-lyresmeta')||{}).textContent,
                acts:[].map.call(d.querySelectorAll('.a3d-lyresacts button'),function(b){return b.textContent;})};}""")
            ck(det and det['op'] == '60' and det['lab'] == '60%' and det['ramp'] == 8 and 'Direct sun on the ground on ' + DATE in det['meta'] and det['acts'] == ['Update', 'Rename', 'Remove'],
               "opened: its opacity, its legend, what it is, and Update, Rename, Remove (%s)" % det)
            await page.click('#a3d-leftpanel [data-lyres="res:%s"] .a3d-lynm' % sid)
            await page.wait_for_timeout(120)
            ck(not await safe("()=>!!document.querySelector('#a3d-leftpanel [data-lyresd]')"), "a click on the row closes it")
            await page.click('#a3d-leftpanel [data-lyres="res:%s"] .a3d-lynm' % sid)
            await page.wait_for_timeout(120)
            # the eye
            await page.click('#a3d-leftpanel [data-lyreson="res:%s"]' % sid)
            await page.wait_for_timeout(120)
            L = await layers()
            ck(not L[0]['visible'] and await safe("()=>window.__a3dResultDrawn()") == [] and (await lyrows())[0]['dim'], "the eye hides it: not drawn, the row dimmed")
            px_off = await pixel(12, 9)
            ck(px_off != px_layer and px_off == px_bg, "and the plan shows it gone: the ground as it was before the run, the live overlay not drawn under it")
            await safe("()=>window.__a3dUndo()")
            await page.wait_for_timeout(120)
            ck((await layers())[0]['visible'], "an undo shows it again")
            # the opacity: live while dragged, one step when let go
            await safe("()=>{window.__a3dSelectFor([]);}")
            depth0 = await safe("()=>window.__a3dUndoDepth?window.__a3dUndoDepth():null")
            await safe("""()=>{var r=document.querySelector('#a3d-leftpanel [data-lyresop]');[90,95,100].forEach(function(v){r.value=v;r.dispatchEvent(new Event('input',{bubbles:true}));});}""")
            await page.wait_for_timeout(100)
            mid = (await layers())[0]['opacity']
            lab = await safe("()=>document.querySelector('#a3d-leftpanel .a3d-lyopv').textContent")
            px_full = await pixel(12, 9)
            ck(mid == 1.0 and lab == '100%' and px_full != px_layer, "dragged, the opacity shows at once, on the plan and beside the slider (%s, %s)" % (mid, lab))
            await safe("""()=>{var r=document.querySelector('#a3d-leftpanel [data-lyresop]');r.dispatchEvent(new Event('change',{bubbles:true}));}""")
            await page.wait_for_timeout(100)
            ck((await layers())[0]['opacity'] == 1.0, "let go, it stays")
            await safe("()=>window.__a3dUndo()")
            await page.wait_for_timeout(100)
            ck((await layers())[0]['opacity'] == 0.6, "and one undo takes the whole drag back, to 60%% (%s)" % (await layers())[0]['opacity'])
            ck(await safe("(i)=>window.__a3dResultLayerSet(i,'opacity',3)", sid) and (await layers())[0]['opacity'] == 0.1, "an opacity below 10% is 10%")
            await safe("()=>window.__a3dUndo()")
            # rename
            await page.dblclick('#a3d-leftpanel [data-lyresname="res:%s"]' % sid)
            await page.wait_for_timeout(120)
            ren = await safe("()=>{var e=document.activeElement;return e&&e.getAttribute('data-lyresren');}")
            ck(ren == 'res:' + sid, "a double-click on its name edits it (%s)" % ren)
            await page.keyboard.press('Control+a')
            await page.keyboard.type('December sun')
            await page.keyboard.press('Enter')
            await page.wait_for_timeout(120)
            ck((await layers())[0]['name'] == 'December sun', "Enter keeps the name typed")
            await page.dblclick('#a3d-leftpanel [data-lyresname="res:%s"]' % sid)
            await page.wait_for_timeout(100)
            await page.keyboard.type('zzz')
            await page.keyboard.press('Escape')
            await page.wait_for_timeout(100)
            ck((await layers())[0]['name'] == 'December sun', "Escape leaves it as it was")
            ck(await safe("(i)=>window.__a3dResultLayerSet(i,'name','   ')", sid) is False and (await layers())[0]['name'] == 'December sun', "an empty name is refused")

            # ---------------------------------------------------------------------------------
            print("\n-- 5. out of date, and Update on the layer's own date")
            await safe("()=>window.__a3dColumnAt([-14,-6],0,4,4,25)")
            await safe("()=>window.__a3dRefreshProps()")
            await page.wait_for_timeout(150)
            L = await layers()
            Y = await lyrows()
            ck(L[0]['stale'] and Y[0]['badge'] == 'Out of date', "a new building: the layer is out of date, and its row says so")
            meta = await safe("()=>(document.querySelector('#a3d-leftpanel .a3d-lyresmeta')||{}).textContent")
            ck(meta and 'Update runs it again for ' + DATE in meta, "with what Update will do (%s)" % meta)
            await set_site(DATE2)
            await page.wait_for_timeout(100)
            c0 = (await safe("(i)=>window.__a3dResultLayerData(i)", sid) or {}).get('cells')
            await safe("()=>{window.__a3dSetPropTab('project');}")
            await tab('layers')
            if not await safe("()=>!!document.querySelector('#a3d-leftpanel [data-lyresupd]')"):
                await page.click('#a3d-leftpanel [data-lyres="res:%s"] .a3d-lynm' % sid)
                await page.wait_for_timeout(120)
            await page.click('#a3d-leftpanel [data-lyresupd]')
            await page.wait_for_timeout(250)
            L = await layers()
            d2 = await safe("(i)=>window.__a3dResultLayerData(i)", sid) or {}
            ck(not L[0]['stale'] and d2.get('date') == DATE and d2.get('cells') != c0 and L[0]['name'] == 'December sun',
               "Update runs it again on its own date, %s, though the site's is now %s: up to date, the new building's shadow in it" % (DATE, DATE2))
            ck(not (await lyrows())[0]['badge'], "the badge goes")
            await safe("()=>window.__a3dUndo()")
            await page.wait_for_timeout(100)
            ck((await safe("(i)=>window.__a3dResultLayerData(i)", sid) or {}).get('cells') == c0 and (await safe("()=>window.__a3dSunSettings()") or {}).get('date') == DATE2,
               "an undo takes the update back, and only the update: the site's date stays %s" % DATE2)
            await safe("()=>window.__a3dRedo()")
            # a second sun layer, of June, to lay over it
            await safe("()=>window.__a3dSunHours({margin:25,cell:1})")
            await safe("()=>window.__a3dColumnAt([16,-16],0,2,2,4)")
            sid2 = await safe("()=>window.__a3dResultLayerAdd('sunhours')")
            L = await layers()
            ck(len(L) == 2 and L[0]['id'] == sid2 and L[0]['name'] == 'Sun hours, ' + DATE2 and L[1]['id'] == sid,
               "a June run, added: a second layer, on top of December's (%s)" % [x['name'] for x in L])
            ck(L[0]['stale'], "a building put up between the run and Add as layer: the layer is out of date at once -- it is as the run was")
            await safe("(i)=>window.__a3dResultLayerUpdate(i)", sid2)

            # ---------------------------------------------------------------------------------
            print("\n-- 6. rain, and the terrain's own")
            tid = await safe("(p)=>window.__a3dMakeTerrain(p)", TWO)
            rr = await safe("(a)=>window.__a3dRainFlow(a,{cell:1})", tid) or {}
            await tab('analyze')
            await safe("()=>window.__a3dAnzToggle('rain',true)")
            await page.click('.a3d-analyze-wrap [data-anzact="layer:rain"]')
            await page.wait_for_timeout(200)
            L = await layers()
            rid = L[0]['id']
            dr = await safe("(i)=>window.__a3dResultLayerData(i)", rid) or {}
            ponds = sum(p['cells'] for p in rr.get('ponds', []))
            ck(L[0]['kind'] == 'rain' and L[0]['src'] == tid and dr.get('cells', '').count('1') == ponds and ponds > 0 and len(dr.get('segs', [])) == rr.get('segs') and dr.get('ponds') == 2,
               "rain kept: its %d pond cells, its %d flow lines, its two ponds" % (ponds, rr.get('segs', 0)))
            ck(await safe("()=>window.__a3dSimHolds().rain"), "the live ponds step aside for it")
            await safe("(i)=>{window.__a3dSelectFor([i]);window.__a3dRefreshProps();}", tid)
            await safe("()=>window.__a3dAnzToggle('terrain',true)")
            await page.wait_for_timeout(100)
            R = await rows()
            la = [a for a in R['terrain']['acts'] if a[0] == 'layer:terrain'][0]
            ck(la[2] and 'Show slope' in la[3], "the terrain's Add as layer waits for slope, elevation or aspect (%s)" % la[3])
            await page.click('.a3d-analyze-wrap [data-anzact="terrain:slope"]')
            await page.wait_for_timeout(150)
            await page.click('.a3d-analyze-wrap [data-anzact="layer:terrain"]')
            await page.wait_for_timeout(200)
            L = await layers()
            tl = L[0]
            tv = await safe("(i)=>window.__a3dState().objs.filter(function(o){return o.id===i;})[0].tview||''", tid)
            ck(tl['kind'] == 'terrain' and tl['mode'] == 'slope' and tl['src'] == tid and tl['name'] == 'Slope, ' + (await safe("(i)=>window.__a3dState().objs.filter(function(o){return o.id===i;})[0].name", tid)) and tv == '',
               "slope as a layer: it follows the surface, whose own colours step aside (%s)" % tl)
            dn = await safe("()=>window.__a3dResultDrawn()") or []
            L = await layers()
            ck(dn == [x['id'] for x in L if x['visible']][::-1], "drawn bottom to top: the top of the list last (%s)" % dn)
            await safe("()=>window.__a3dColumnAt([-30,30],0,1,1,3)")
            ck(not [x for x in await layers() if x['id'] == tl['id']][0]['stale'], "a terrain layer is never out of date")
            await safe("(i)=>{window.__a3dSelectFor([i]);window.__a3dRunCmd('del');}", tid)
            await safe("()=>window.__a3dRefreshProps()")
            await page.wait_for_timeout(150)
            tl2 = [x for x in await layers() if x['id'] == tl['id']][0]
            await tab('layers')
            Y = {y['key']: y for y in await lyrows()}
            ck(tl2['gone'] and tl['id'] not in (await safe("()=>window.__a3dResultDrawn()") or []) and Y['res:' + tl['id']]['badge'] == 'Gone',
               "its surface deleted: the layer says Gone and draws nothing")
            await safe("()=>window.__a3dUndo()")
            await page.wait_for_timeout(150)
            ck(not [x for x in await layers() if x['id'] == tl['id']][0]['gone'], "an undo brings the surface back, and the layer with it")
            # cut and fill
            pts = [[x, z, 0.05 * x, '', ''] for x in range(0, 61, 5) for z in range(0, 61, 5)]
            ex = await safe("(p)=>window.__a3dMakeTerrain(p)", pts)
            pd = await safe("(p)=>window.__a3dSketch('poly',p)", [[20, 20], [40, 20], [40, 40], [20, 40]])
            await safe("(i)=>{window.__a3dSelectFor([i]);window.__a3dSetPropTab('project');window.__a3dRefreshProps();}", pd)
            await page.fill('#a3d-propsbody [data-propf="gradeelev"]', '1.5')
            await page.keyboard.press('Enter')
            await page.wait_for_timeout(80)
            g = await safe("(a)=>window.__a3dGrade(a[0],a[1])", [[pd], ex]) or {}
            cf = await safe("()=>window.__a3dResultLayerAdd('cutfill')")
            L = await layers()
            ck(cf and L[0]['mode'] == 'cutfill' and L[0]['src'] == g.get('id'), "a graded pad's cut and fill, as a layer (%s)" % L[0])
            await tab('analyze')
            await safe("()=>window.__a3dAnzToggle('grading',true)")
            R = await rows()
            la = [a for a in R['grading']['acts'] if a[0] == 'layer:cutfill'][0]
            ck(la[2] and 'already' in la[3], "and not twice (%s)" % la[3])
            ck(await safe("()=>window.__a3dResultLayerAdd('terrain',{id:'nope',mode:'slope'})") is None and
               await safe("(i)=>window.__a3dResultLayerAdd('terrain',{id:i,mode:'cutfill'})", ex) is None and
               await safe("(i)=>window.__a3dResultLayerAdd('terrain',{id:i,mode:'colour'})", ex) is None,
               "no layer for a surface that is not there, cut and fill of a surface never graded, or a mode that is not one")

            # ---------------------------------------------------------------------------------
            print("\n-- 7. the stack")
            await tab('layers')
            L = await layers()
            ids = [x['id'] for x in L]
            pv = await safe("""(a)=>{var src=document.querySelector('#a3d-leftpanel [data-lyres="res:'+a[0]+'"]'),dst=document.querySelector('#a3d-leftpanel [data-lyres="res:'+a[1]+'"]');
              var dt=new DataTransfer();src.dispatchEvent(new DragEvent('dragstart',{bubbles:true,dataTransfer:dt}));
              var ov=new DragEvent('dragover',{bubbles:true,cancelable:true,dataTransfer:dt});dst.dispatchEvent(ov);
              dst.dispatchEvent(new DragEvent('drop',{bubbles:true,cancelable:true,dataTransfer:dt}));src.dispatchEvent(new DragEvent('dragend',{bubbles:true,dataTransfer:dt}));
              return ov.defaultPrevented;}""", [ids[-1], ids[0]])
            L2 = [x['id'] for x in await layers()]
            ck(pv and L2 == [ids[-1]] + ids[:-1], "the bottom layer dragged onto the top one goes to the top (%s)" % L2)
            ck([y['key'][4:] for y in await lyrows() if y['sec'] == 'analysis'] == L2, "the rows follow")
            ck((await safe("()=>window.__a3dResultDrawn()") or [])[-1] == ids[-1], "and it is drawn last, over the rest")
            await safe("()=>window.__a3dUndo()")
            ck([x['id'] for x in await layers()] == ids, "an undo puts it back")
            ck(await safe("(a)=>window.__a3dResultLayerMove(a,99)", ids[0]) and [x['id'] for x in await layers()][-1] == ids[0], "to an index past the end: the bottom")
            ck(await safe("(a)=>window.__a3dResultLayerMove('nope',0)", None) is False, "an id that is not one moves nothing")
            await safe("()=>window.__a3dUndo()")

            # ---------------------------------------------------------------------------------
            print("\n-- 8. Remove")
            n0 = len(await layers())
            await safe("(i)=>window.__a3dResultLayerSet(i,'name','Kept name')", sid)
            await page.click('#a3d-leftpanel [data-lyres="res:%s"] .a3d-lynm' % sid)
            await page.wait_for_timeout(120)
            if not await safe("(k)=>!!document.querySelector('#a3d-leftpanel [data-lyresdel=\"'+k+'\"]')", 'res:' + sid):
                await page.click('#a3d-leftpanel [data-lyres="res:%s"] .a3d-lynm' % sid)
                await page.wait_for_timeout(120)
            await page.click('#a3d-leftpanel [data-lyresdel="res:%s"]' % sid)
            await page.wait_for_timeout(150)
            ck(len(await layers()) == n0 - 1 and sid not in [x['id'] for x in await layers()], "Remove takes the layer away")
            await safe("()=>window.__a3dUndo()")
            await page.wait_for_timeout(100)
            ck([x['name'] for x in await layers() if x['id'] == sid] == ['Kept name'], "and an undo brings it back whole, as it was the moment before")
            # removing the layer of the live run: the live overlay comes back
            await safe("(i)=>window.__a3dResultLayerRemove(i)", sid2)
            ck(not await safe("()=>window.__a3dSimHolds().sun"), "once no layer holds the June run, the live overlay is drawn again")
            await safe("()=>window.__a3dUndo()")

            # ---------------------------------------------------------------------------------
            print("\n-- 9. the Data section")
            add = await safe("()=>window.__a3dDataAdd('https://data.example.org/zoning.geojson','Zoning','#aa3377')") or {}
            await page.wait_for_timeout(300)
            did = add.get('id')
            Y = [y for y in await lyrows() if y['sec'] == 'data']   # Layers is open: no click on its tab, which would redraw it
            ck(did and len(Y) == 1 and Y[0]['name'] == 'Zoning', "a data layer added in Properties is in Layers, under Data (%s)" % Y)
            await page.click('#a3d-leftpanel [data-lyreson="data:%s"]' % did)
            await page.wait_for_timeout(150)
            dl = (await safe("()=>window.__a3dDataLayers()") or [{}])[0]
            ck(dl.get('visible') is False and [y for y in await lyrows() if y['sec'] == 'data'][0]['dim'], "its eye is the data layer's own Show (%s)" % dl.get('visible'))
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dSetPropTab('site');window.__a3dRefreshProps();}")
            cb = await safe("(i)=>{var e=document.querySelector('#a3d-propsbody [data-propdata=\"vis:'+i+'\"]');return e?e.checked:null;}", did)
            ck(cb is False, "and Properties' box follows (%s)" % cb)
            await safe("()=>window.__a3dUndo()")
            await page.wait_for_timeout(120)
            dls = await safe("()=>window.__a3dDataLayers()") or []
            ck(len(dls) == 1 and dls[0].get('visible') is True, "one undo step: an undo shows it again (%s)" % [x.get('visible') for x in dls])
            await page.click('#a3d-leftpanel [data-lyres="data:%s"] .a3d-lynm' % did)
            await page.wait_for_timeout(120)
            dd = await safe("""(k)=>{var d=document.querySelector('#a3d-leftpanel [data-lyresd="'+k+'"]');return d?{op:d.querySelector('[data-lyresop]').value,meta:d.querySelector('.a3d-lyresmeta').textContent,
              acts:[].map.call(d.querySelectorAll('.a3d-lyresacts button'),function(b){return b.textContent;})}:null;}""", 'data:' + did)
            ck(dd and dd['op'] == '100' and 'Source: data.example.org' in dd['meta'] and dd['acts'] == ['Settings', 'Rename', 'Remove'], "opened: its opacity, its source, Settings, Rename, Remove (%s)" % dd)
            await safe("""(k)=>{var r=document.querySelector('#a3d-leftpanel [data-lyresop="'+k+'"]');r.value=40;r.dispatchEvent(new Event('input',{bubbles:true}));r.dispatchEvent(new Event('change',{bubbles:true}));}""", 'data:' + did)
            await page.wait_for_timeout(120)
            dl = (await safe("()=>window.__a3dDataLayers()") or [{}])[0]
            ck(dl.get('opacity') == 0.4, "its opacity is the data layer's own (%s)" % dl.get('opacity'))
            await safe("()=>window.__a3dSetPropTab('project')")
            await page.click('#a3d-leftpanel [data-lyresset="data:%s"]' % did)
            await page.wait_for_timeout(200)
            ck(await safe("()=>window.__a3dPropTab()") == 'site' and await safe("()=>!!document.querySelector('#a3d-propsbody [data-a3dpgrp=\"Data Layers\"]')"),
               "Settings opens its group in Properties, on Site")
            await tab('layers')
            if not await safe("(k)=>!!document.querySelector('#a3d-leftpanel [data-lyresdel=\"'+k+'\"]')", 'data:' + did):
                await page.click('#a3d-leftpanel [data-lyres="data:%s"] .a3d-lynm' % did)
                await page.wait_for_timeout(120)
            await page.click('#a3d-leftpanel [data-lyresdel="data:%s"]' % did)
            await page.wait_for_timeout(150)
            ck(not await safe("()=>window.__a3dDataLayers()") and not [y for y in await lyrows() if y['sec'] == 'data'], "Remove removes the data layer, from both")
            await safe("()=>window.__a3dUndo()")
            await page.wait_for_timeout(150)
            ck(len(await safe("()=>window.__a3dDataLayers()") or []) == 1 and [y for y in await lyrows() if y['sec'] == 'data'], "and an undo brings it back, to both")
            await page.fill('#a3d-leftpanel [data-lysearch]', 'zon')
            await page.wait_for_timeout(120)
            sv = await safe("()=>[].map.call(document.querySelectorAll('#a3d-leftpanel [data-lysec]'),function(e){return e.getAttribute('data-lysec');})")
            ck(sv == ['data'] and len([y for y in await lyrows()]) == 1, "the layers' search reaches these rows: 'zon' leaves Zoning alone (%s)" % sv)
            await page.fill('#a3d-leftpanel [data-lysearch]', '')
            await page.click('#a3d-leftpanel [data-lysectog="analysis"]')
            await page.wait_for_timeout(100)
            ck(not [y for y in await lyrows() if y['sec'] == 'analysis'], "a section closes to its heading")
            await page.click('#a3d-leftpanel [data-lysectog="analysis"]')
            await page.wait_for_timeout(100)

            # ---------------------------------------------------------------------------------
            print("\n-- 10. saved")
            before = [(x['id'], x['name'], x['kind'], x['opacity'], x['visible']) for x in await layers()]
            await safe("(i)=>window.__a3dResultLayerSet(i,'visible',false)", sid2)
            before = [(x['id'], x['name'], x['kind'], x['opacity'], x['visible']) for x in await layers()]
            await page.wait_for_timeout(1500)
            await within(page.reload(), 'reload')
            await page.wait_for_timeout(2300)
            await safe("()=>{window.__a3dEnter();window.__a3dSetPlanView&&window.__a3dSetPlanView();}")
            await page.wait_for_timeout(200)
            after = [(x['id'], x['name'], x['kind'], x['opacity'], x['visible']) for x in await layers()]
            ck(after == before, "through a reload, every layer as it was, hidden ones hidden (%d)" % len(after))
            d3 = await safe("(i)=>window.__a3dResultLayerData(i)", sid) or {}
            ck(d3.get('cells') == (await safe("(i)=>window.__a3dResultLayerData(i)", sid) or {}).get('cells') and len(d3.get('cells', '')) > 100 and
               sid in (await safe("()=>window.__a3dResultDrawn()") or []), "with their pictures, drawn, with no run since: offline")
            env = await safe("()=>JSON.parse(window.__a3dProjectEnvelope())")
            ck(env and [x['id'] for x in env['data'].get('resultLayers', [])] == [x[0] for x in after], "a project file carries them")
            n_tabs = await safe("()=>document.querySelectorAll('.acad-doctab.dt-doc').length")
            ok_imp = await safe("(t)=>window.__a3dImportProject(t,'v148.acad3d.json')", json.dumps(env))
            await page.wait_for_timeout(400)
            ck(ok_imp and await safe("()=>document.querySelectorAll('.acad-doctab.dt-doc').length") == n_tabs + 1 and
               [x['id'] for x in await layers()] == [x[0] for x in after], "and opened, in a new tab, it has them")
            env['data']['resultLayers'] = [{'id': 'a', 'name': 'x', 'kind': 'sunhours', 'data': {'cells': '00', 'nx': 3, 'nz': 1, 'x0': 0, 'z0': 0, 'cell': 1}},
                                           {'id': 'b', 'name': 'y', 'kind': 'terrain', 'src': 'q', 'mode': 'colour'},
                                           {'id': 'c', 'name': 'z', 'kind': 'terrain', 'src': 'q', 'mode': 'slope'}, None, 7]
            ck(await safe("(a)=>window.__a3dResultLayersValid(a)", env['data']['resultLayers']) == ['c'], "a damaged layer is let go of, the rest kept")
            # History: a version restored leaves the layers as they are
            await safe("()=>window.__a3dHistCommit('before')")
            v1 = (await safe("()=>window.__a3dHistory()") or {}).get('head')
            n1 = len(await layers())
            await safe("()=>window.__a3dSunHours({margin:25,cell:1,date:'2026-03-21'})")
            await safe("()=>window.__a3dResultLayerAdd('sunhours')")
            r = await safe("(i)=>window.__a3dHistRestore(i)", v1) or {}
            ck(r.get('id') == v1 and len(await layers()) == n1 + 1, "History's restore leaves the layers as they are: they are not the model's")
            ch = await safe("()=>window.__a3dHistChanges()") or {}
            ck(not any(str(k).startswith('@result') for k in json.dumps(ch).split('"')), "and a layer is not a change to commit")

            # ---------------------------------------------------------------------------------
            print("\n-- 11. the command audit, the page")
            au = await safe("()=>window.__a3dShellAudit()") or {}
            ck(au.get('ok'), "the shell audit is clean with the Layers sections open (%s)" % au.get('unclaimed'))
            await tab('analyze')
            await safe("()=>window.__a3dAnzOpenAll(true)")
            au = await safe("()=>window.__a3dShellAudit()") or {}
            ck(au.get('ok'), "and with every Analyze row open (%s)" % au.get('unclaimed'))
            await safe("()=>window.__a3dAnzOpenAll(false)")
            ck(not errs, "no page errors (%s)" % errs[:3])
        except Stalled as s:
            ck(False, "the harness stalled at %s" % s)
        except Exception:
            traceback.print_exc()
            ck(False, "the suite ran to its end")
        await browser.close()

        # -------------------------------------------------------------------------------------
        print("\n-- 12. a phone, a tablet, a computer")
        for name, vp, touch in (('phone', {'width': 390, 'height': 844}, True), ('tablet', {'width': 820, 'height': 1180}, True), ('computer', {'width': 1500, 'height': 950}, False)):
            b = await pw.chromium.launch()
            c = await b.new_context(viewport=vp, has_touch=touch, is_mobile=touch)
            p = await c.new_page()
            perr = []
            p.on('pageerror', lambda e: perr.append(str(e)))
            sf = mk_safe(p)
            try:
                await within(p.goto('file://' + str(HTML)), 'goto ' + name)
                await p.wait_for_timeout(2000)
                await sf("()=>{window.__a3dEnter();window.__a3dSetPlanView&&window.__a3dSetPlanView();window.__a3dTestSetObjs([]);}")
                await p.click('#a3d-rail [data-tab="analyze"]')
                await p.wait_for_timeout(300)
                await sf("()=>window.__a3dAnzToggle('sunhours',true)")
                m = await sf("""()=>{var w=document.querySelector('.a3d-analyze-wrap'),a=w.querySelector('.a3d-anz'),lp=document.getElementById('a3d-leftpanel').getBoundingClientRect();
                  var hd=[].map.call(w.querySelectorAll('.a3d-anzhd'),function(e){return e.getBoundingClientRect().height;});
                  var bt=[].map.call(w.querySelectorAll('.a3d-anzbtn'),function(e){return e.getBoundingClientRect();}).filter(function(r){return r.height>0;});
                  var tree=document.querySelector('#a3d-leftpanel > .a3d-tree');
                  return {hd:Math.min.apply(0,hd),hdMax:Math.max.apply(0,hd),bt:Math.min.apply(0,bt.map(function(r){return r.height;})),over:a.scrollWidth-a.clientWidth,
                    out:bt.filter(function(r){return r.right>lp.right+0.5;}).length,tree:tree?getComputedStyle(tree).display:'none',
                    search:w.querySelector('[data-anzsearch]').getBoundingClientRect().height};}""") or {}
                if touch:
                    ck(m.get('hd', 0) >= 44 and m.get('bt', 0) >= 34 and m.get('search', 0) >= 36,
                       "%s: rows %d px, buttons %d px, the search %d px: for a finger" % (name, m.get('hd', 0), m.get('bt', 0), m.get('search', 0)))
                else:
                    ck(36 <= m.get('hd', 0) and m.get('hdMax', 99) <= 46 and m.get('bt', 0) <= 26, "%s: rows %d px and buttons %d px: a list, for a mouse" % (name, m.get('hd', 0), m.get('bt', 0)))
                ck(m.get('over', 1) == 0 and m.get('out', 1) == 0, "%s: nothing wider than the panel, no button past its edge (%s)" % (name, m))
                ck(m.get('tree') == 'none', "%s: the Project Browser's tree does not lie over Analyze (%s)" % (name, m.get('tree')))
                await p.click('#a3d-rail [data-tab="layers"]')
                await p.wait_for_timeout(250)
                await sf("""()=>{window.__a3dTestSetObjs([]);}""")
                t2 = await sf("""()=>{var tree=document.querySelector('#a3d-leftpanel > .a3d-tree'),h=document.querySelector('#a3d-leftpanel [data-lysec="analysis"] .a3d-lysechd');
                  return [tree?getComputedStyle(tree).display:'none',h?Math.round(h.getBoundingClientRect().height):0];}""") or ['?', 0]
                ck(t2[0] == 'none' and (t2[1] >= 40 if touch else 26 <= t2[1] <= 30), "%s: on Layers too, and its section headings %d px" % (name, t2[1]))
                ck(not perr, "%s: no page errors (%s)" % (name, perr[:2]))
            except Stalled as s:
                ck(False, "%s: the harness stalled at %s" % (name, s))
            except Exception:
                traceback.print_exc()
                ck(False, "%s: ran to its end" % name)
            await b.close()

    print("\n%d/%d checks passed" % (ck.n - len(ck.bad), ck.n))
    if ck.bad:
        print("RESULT: FAIL")
        for m in ck.bad:
            print("   - " + m)
        return 1
    print("RESULT: PASS")
    return 0


sys.exit(asyncio.run(run()))
