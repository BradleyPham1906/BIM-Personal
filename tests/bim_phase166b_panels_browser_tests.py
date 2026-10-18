#!/usr/bin/env python3
"""bim_phase166b_panels_browser_tests.py -- V166b: the panels.

The owner: "make sure to fix the right panel also since i still see the analysis tab on it (looks
like from the old design). left panel needs to be dragable like the right panel also."

Measured in the browser, and read back from the model:
  1. PROPERTIES has three tabs with nothing selected -- Project, Site, View. No group of the old
     Analysis tab is left in it; a tab remembered as Analysis opens on Project; the usages are on
     Project, and USAGES and Areas by usage's button open them there, where they still edit.
  2. FRAME ANALYSIS, in Analyze, holds the frame's settings and results and the active level's floor
     loads. Each field changes the model, keeps the focus, and the row says what the model says; a
     floor load that is not one is refused and the field shows the model's value again. The search
     finds the row by its settings' names.
  3. AREAS BY USAGE, in Analyze, lists the project's areas by usage, from the model, and follows it.
  4. THE LEFT PANEL'S EDGE: dragged by a mouse or a finger, 242 to 560 px, the drawing taking the
     room given up and keeping 320 px beside Properties; remembered across a reload; a double click
     puts it back; a drag cancelled puts it back. From the keyboard it is the W3C's window splitter:
     Left and Right (Shift, further), Home and End, Enter shuts the panel and the panel button opens
     it again; the keys are the edge's, not the model's. Not on a phone or an upright tablet, whose
     drawer keeps its width; a computer's width comes back when the screen does.
  5. ONE PRESS: WCAG 2.2's 2.5.7 asks that what a drag does can be done without dragging, and 2.5.8
     that a target be 24 px or have an equivalent that is. A button beside the panel's collapse widens
     it a step at a time -- 242, 320, 400, 480, 560, within what the screen allows -- then back to
     242, saying where the next press goes; a computer's, as the edge is.

The harness never waits without a bound (V123).
"""
import asyncio, pathlib, re, sys, traceback
from playwright.async_api import async_playwright

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


async def run():
    ck = CK
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1500, 'height': 950})
        page = await ctx.new_page()
        errs, warns = [], []
        page.on('pageerror', lambda e: errs.append(str(e)))
        page.on('console', lambda m: warns.append(m.text) if m.type == 'warning' and '[BIM]' in m.text else None)
        await within(page.goto('file://' + str(HTML)), 'goto')
        await page.wait_for_timeout(2300)

        async def safe(js, arg=None, pg=None):
            p = pg or page
            try:
                return await within(p.evaluate(js, arg) if arg is not None else p.evaluate(js), 'evaluate ' + js[:50])
            except Stalled:
                raise
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:200])
                return None

        async def toast(pg=None):
            return await safe("()=>{var t=document.getElementById('a3d-toast');return t?t.textContent:'';}", pg=pg) or ''

        has = await safe("()=>window.__acad3dV166b")
        ck(bool(has) and 'noanalysistab' in has and 'anzframe' in has and 'leftresize' in has and 'leftkeys' in has,
           "__acad3dV166b marker is present (%s)" % (has or '')[:60])
        if not has:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.bad), ck.n))
            await browser.close()
            return 1

        async def model_props():
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dRefreshProps();}")
            await page.wait_for_timeout(120)
            return await safe("""()=>{var b=document.getElementById('a3d-propsbody');
              return {tabs:[].map.call(b.querySelectorAll('[data-ptabbtn]'),function(e){return [e.getAttribute('data-ptabbtn'),e.textContent];}),
                groups:[].map.call(b.querySelectorAll('[data-a3dpgrp]'),function(e){var p=e.closest('[data-ptab]');return [e.getAttribute('data-a3dpgrp'),p?p.getAttribute('data-ptab'):null];}),
                html:b.innerHTML};}""") or {}

        async def anz_open(ids):
            await safe("()=>{var b=document.querySelector('#a3d-rail [data-tab=\"analyze\"]');var s=document.getElementById('a3d-shell');if(s.getAttribute('data-tab')!=='analyze'||s.classList.contains('collapsed'))b.click();}")
            await page.wait_for_timeout(150)
            for i in ids:
                await safe("(k)=>{var t=document.querySelector('.a3d-analyze-wrap [data-anztog=\"'+k+'\"]');if(t&&t.getAttribute('aria-expanded')!=='true')t.click();}", i)
            await page.wait_for_timeout(80)

        async def card(cid):
            return await safe("""(k)=>{var c=document.querySelector('.a3d-analyze-wrap [data-anzcard="'+k+'"]');if(!c)return null;
              var f=function(s){return [].map.call(c.querySelectorAll(s),function(e){return e;});};
              return {acts:f('[data-anzact]').map(function(e){return e.getAttribute('data-anzact');}),
                fields:f('select,input').map(function(e){var l=e.id?c.querySelector('label[for="'+e.id+'"]'):null;
                  return {id:e.id,key:e.getAttribute('data-propstr')||e.getAttribute('data-anzload'),v:e.value,label:l?l.textContent:null,h:e.getBoundingClientRect().height,
                    w:e.getBoundingClientRect().width,fs:getComputedStyle(e).fontSize,opts:e.tagName==='SELECT'?[].map.call(e.options,function(o){return o.value;}):null};}),
                kv:f('.a3d-anzkv dt').map(function(e){return [e.textContent,e.nextElementSibling.textContent];}),
                sub:f('.a3d-anzsub').map(function(e){return e.textContent;}),
                areas:f('.a3d-anzarea').map(function(e){return [e.getAttribute('data-anzarea'),e.querySelector('.a3d-anzareanm').textContent,
                  (e.querySelector('.a3d-anzarean')||{textContent:''}).textContent,[].map.call(e.querySelectorAll('.a3d-anzareav'),function(v){return v.textContent;})];}),
                cap:f('.a3d-anzcap').map(function(e){return e.textContent;}).join(' '),
                state:(c.querySelector('.a3d-anzstate')||{textContent:''}).textContent,st:(c.querySelector('.a3d-anzst')||{textContent:''}).textContent,
                open:c.classList.contains('open'),shown:!c.hasAttribute('hidden')&&c.getBoundingClientRect().height>0};}""", cid) or {}

        async def change(sel, val):
            # as a person does it: the field focused, its value set, its change fired
            await page.focus(sel)
            if (await safe("(s)=>document.querySelector(s).tagName", sel)) == 'SELECT':
                await page.select_option(sel, val)
            else:
                await page.fill(sel, val)
                await page.press(sel, 'Tab')
            await page.wait_for_timeout(150)

        try:
            # ---------------------------------------------------------------------------------
            print("\n-- 1. Properties: three tabs")
            mp = await model_props()
            ck(mp.get('tabs') == [['project', 'Project'], ['site', 'Site'], ['view', 'View']], "with nothing selected: Project, Site, View (%s)" % mp.get('tabs'))
            G = dict((g[0], g[1]) for g in mp.get('groups', []))
            ck(G == {'Identity Data': 'project', 'Usages': 'project', 'Statistics': 'project', 'History': 'project',
                     'Location': 'site', 'Map': 'site', 'Site Context': 'site', 'Data Layers': 'site', 'View': 'view',
                     'Standards': 'site'},   # AMENDED FOR V167: the standards registry's group, on Site
               "every group on its tab, the usages on Project (%s)" % G)
            h = mp.get('html', '')
            ck('data-ptab="analysis"' not in h and 'data-ptabbtn="analysis"' not in h and 'Floor Loads' not in h and 'data-propstr=' not in h
               and 'Areas by Usage' not in h and 'data-propmodel="dl"' not in h,
               "nothing of the old Analysis tab is left in Properties: no floor loads, no frame settings, no areas")
            order = [g[0] for g in mp.get('groups', []) if g[1] == 'project']
            ck(order == ['Identity Data', 'Usages', 'Statistics', 'History'], "Project: Identity Data, Usages, Statistics, History (%s)" % order)
            ck(await safe("()=>window.__a3dSetPropTab('analysis')") is False and await safe("()=>window.__a3dPropTabOf('Usages')") == 'project'
               and await safe("()=>window.__a3dPropTabOf('Analysis')") is None and await safe("()=>window.__a3dPropTabOf('Areas by Usage')") is None,
               "there is no Analysis tab to show; Usages is Project's")
            # a viewer whose last tab was Analysis
            await safe("()=>localStorage.setItem('acad3dPropTab','analysis')")
            await within(page.reload(), 'reload')
            await page.wait_for_timeout(2300)
            mp = await model_props()
            on = await safe("()=>[].map.call(document.querySelectorAll('#a3d-propsbody .a3d-ptabpane.on'),function(e){return e.getAttribute('data-ptab');})")
            ck(await safe("()=>window.__a3dPropTab()") == 'project' and on and set(on) == {'project'} and len(on) >= 3,
               "a tab remembered as Analysis opens on Project, and only Project's groups show (%s)" % on)
            await safe("()=>{window.__a3dSetPropTab('view');window.__a3dSelectFor([]);window.__a3dRunCmd('usages');}")
            await page.wait_for_timeout(200)
            u = await safe("""()=>{var g=document.querySelector('#a3d-propsbody [data-a3dpgrp="Usages"]');return g?{tab:window.__a3dPropTab(),h:g.getBoundingClientRect().height,
              pane:g.closest('[data-ptab]').getAttribute('data-ptab'),sel:window.__a3dState().sel}:null;}""")
            ck(u and u['tab'] == 'project' and u['pane'] == 'project' and u['h'] > 0 and u['sel'] is None, "USAGES opens the usages, on Project, and they show (%s)" % u)
            # they still edit
            ok = await safe("()=>{var e=document.querySelector('#a3d-propsbody [data-propusageact=\"open:use-off\"]');if(!e)return false;e.click();return true;}")
            await page.wait_for_timeout(120)
            if ok:
                await change('#a3d-propsbody [data-propusage="u:use-off:nsa"]', '50')
            off = [x for x in (await safe("()=>window.__a3dUsages()") or []) if x.get('id') == 'use-off']
            ck(ok and off and abs(off[0]['nsa'] - 0.5) < 1e-9, "a usage edited on Project changes the library: Office's NSA 50%% (%s)" % (off and off[0].get('nsa')))
            await safe("()=>{var e=document.querySelector('#a3d-propsbody [data-propusageact=\"open:use-off\"]');if(e)e.click();}")

            # ---------------------------------------------------------------------------------
            print("\n-- 2. Frame analysis, in Analyze")
            await safe("()=>{window.__a3dTestSetObjs([]);window.__a3dSelectFor([]);window.__a3dStructSettings({show:false});window.__a3dTestClearUndo();}")
            lv0 = (await safe("()=>window.__a3dLevels()") or [{}])[0]
            await anz_open(['structure', 'areas'])
            c = await card('structure')
            ks = [f['key'] for f in c.get('fields', [])]
            ck(c.get('open') and ks == ['dl', 'll'] and c.get('acts') == ['structure:run', 'structure:off'],
               "no frame yet: the row holds the floor loads only, and Run and Hide (%s, %s)" % (ks, c.get('acts')))
            ck(c.get('sub') == ['Floor loads on ' + lv0.get('name', '?')] and 'Column Loads schedule' in c.get('cap', '') and
               [f['label'] for f in c['fields']] == ['Dead (kPa)', 'Live (kPa)'],
               "the floor loads are the active level's, each field labelled, and the row says what reads them (%s)" % c.get('sub'))
            ck(not await safe("()=>!!document.querySelector('[data-anzact=\"open:Analysis\"],[data-anzact=\"open:Areas by Usage\"]')"),
               "no button opens a settings page in Properties any more")
            await change('#a3d-anzf-dl', '4.5')
            lv = (await safe("()=>window.__a3dLevels()") or [{}])[0]
            ck(lv.get('dl') == 4.5 and 'dead load 4.5 kPa' in await toast(), "a dead load typed in the row is the level's: 4.5 kPa (%s)" % lv.get('dl'))
            await change('#a3d-anzf-ll', '2')
            lv = (await safe("()=>window.__a3dLevels()") or [{}])[0]
            ck(lv.get('ll') == 2, "and the live load, 2 kPa (%s)" % lv.get('ll'))
            await page.focus('#a3d-anzf-ll')
            await page.fill('#a3d-anzf-ll', '-3')
            await page.dispatch_event('#a3d-anzf-ll', 'change')
            await page.wait_for_timeout(150)
            shown = await safe("()=>[document.getElementById('a3d-anzf-ll').value,document.activeElement&&document.activeElement.id]")
            lv = (await safe("()=>window.__a3dLevels()") or [{}])[0]
            ck(lv.get('ll') == 2 and 'a number of kPa' in await toast() and shown and shown[0] == '2' and shown[1] == 'a3d-anzf-ll',
               "a negative load is refused, and the field, still focused, shows the model's 2 again (%s)" % shown)
            foc = await safe("()=>document.activeElement&&document.activeElement.id")
            # Undo is a click away from the field (V162: a refresh waits while a field is focused)
            await safe("()=>{document.activeElement.blur();window.__a3dUndo();}")
            await page.wait_for_timeout(150)
            lv = (await safe("()=>window.__a3dLevels()") or [{}])[0]
            ck(lv.get('ll') is None and lv.get('dl') == 4.5 and await safe("()=>document.getElementById('a3d-anzf-ll').value") == '',
               "each load is one undo step, and the row follows the undo (%s)" % [lv.get('dl'), lv.get('ll')])
            ck(foc == 'a3d-anzf-dl' or foc == 'a3d-anzf-ll', "a field keeps the focus through its change (%s)" % foc)
            # a frame
            await safe("""()=>{window.__a3dColumnAt([0,0],0,0.4,0.3,3);window.__a3dColumnAt([6,0],0,0.4,0.3,3);window.__a3dBeam([0,0],[6,0],0.3,0.5);
              window.__a3dSelectFor([]);window.__a3dRefreshProps();}""")
            await page.wait_for_timeout(150)
            c = await card('structure')
            F = dict((f['key'], f) for f in c.get('fields', []))
            st = await safe("()=>window.__a3dStructSettings()") or {}
            combos = await safe("()=>window.__a3dCombos()") or []
            ck([f['key'] for f in c.get('fields', [])] == ['combo', 'selfweight', 'display', 'deflected', 'dl', 'll'],
               "with a frame: Combination, Self-weight, Display, Deflected shape, then the floor loads (%s)" % [f['key'] for f in c.get('fields', [])])
            ck(F.get('combo', {}).get('opts') == combos and F['combo']['v'] == st.get('combo') and F['selfweight']['v'] == ('1' if st.get('selfWeight') else '0')
               and F['display']['v'] == 'off' and F['deflected']['v'] == ('1' if st.get('deflected') else '0'),
               "each field shows the model's setting (%s)" % st)
            ck([f['label'] for f in c['fields']][:4] == ['Combination', 'Self-weight', 'Display', 'Deflected shape'], "each labelled by its own label")
            kv = dict(c.get('kv', []))
            ck(kv.get('Result') == 'Run it to solve the frame' and kv.get('Not included') == 'Floor loads, wind, seismic' and kv.get('Basis'),
               "before a run the row says to run it, and what the frame leaves out (%s)" % kv)
            await change('#a3d-anzf-display', 'N')
            st = await safe("()=>window.__a3dStructSettings()") or {}
            dr = await safe("()=>window.__a3dStructDrawn()") or {}
            c = await card('structure')
            kv = dict(c.get('kv', []))
            foc = await safe("()=>[document.activeElement&&document.activeElement.id,document.activeElement&&document.activeElement.value]")
            ck(st.get('show') and st.get('diagram') == 'N' and st.get('current') and dr.get('diagram') == 'N' and 'Axial force' in dr.get('caption', ''),
               "Display: Axial force solves the frame and draws the axial diagram (%s)" % [st.get('diagram'), dr.get('caption')])
            ck(c.get('state') == 'On' and kv.get('Largest moment', '').endswith('Beam_1') and kv.get('Equilibrium', '').startswith('Balanced'),
               "the row is On and gives the results: the largest moment, on Beam_1, and the balance (%s)" % kv)
            ck(foc == ['a3d-anzf-display', 'N'], "the select keeps the focus and its value through the redraw (%s)" % foc)
            b0 = kv.get('Basis')
            if len(combos) > 1:
                await change('#a3d-anzf-combo', combos[1])
            st = await safe("()=>window.__a3dStructSettings()") or {}
            kv = dict((await card('structure')).get('kv', []))
            ck(len(combos) > 1 and st.get('combo') == combos[1] and st.get('current') and kv.get('Basis') and kv.get('Basis') != b0,
               "Combination changes the model's and solves again; the basis follows (%s)" % st.get('combo'))
            await change('#a3d-anzf-selfweight', '0')
            await change('#a3d-anzf-deflected', '0')
            st = await safe("()=>window.__a3dStructSettings()") or {}
            ck(st.get('selfWeight') is False and st.get('deflected') is False, "Self-weight and Deflected shape are the model's too (%s)" % st)
            await change('#a3d-anzf-display', 'off')
            st = await safe("()=>window.__a3dStructSettings()") or {}
            c = await card('structure')
            ck(st.get('show') is False and await safe("()=>window.__a3dStructDrawn()") is None and c.get('state') == 'Off',
               "Display: Off turns the display off, and the row says Off (%s)" % c.get('state'))
            # the search finds the row by its settings
            for q in ('combination', 'floor loads', 'deflected'):
                await safe("(q)=>{var s=document.querySelector('.a3d-analyze-wrap [data-anzsearch]');s.value=q;s.dispatchEvent(new Event('input',{bubbles:true}));}", q)
                await page.wait_for_timeout(60)
                c = await card('structure')
                ck(c.get('shown'), "the search '%s' finds Frame analysis" % q)
            await safe("()=>{var s=document.querySelector('.a3d-analyze-wrap [data-anzsearch]');s.value='';s.dispatchEvent(new Event('input',{bubbles:true}));}")

            # ---------------------------------------------------------------------------------
            print("\n-- 3. Areas by usage, in Analyze")
            await safe("()=>{document.activeElement.blur();window.__a3dTestSetObjs([]);window.__a3dSelectFor([]);window.__a3dRefreshProps();}")
            await page.wait_for_timeout(100)
            c = await card('areas')
            ck(c.get('open') and not c.get('areas') and 'Give a room, a floor or a mass a usage' in c.get('cap', '') and c.get('acts') == ['open:Usages'],
               "no usages given: the row says how to give one; its button is Usages (%s)" % c.get('acts'))
            ids = await safe("""()=>{var a=window.__a3dAdd('box',{Length:10,Width:8,Height:9}).id,b=window.__a3dAdd('box',{Length:6,Width:5,Height:6}).id;
              window.__a3dUsageAssign([a],'use-res');window.__a3dUsageAssign([b],'use-off');window.__a3dSelectFor([]);window.__a3dRefreshProps();return [a,b];}""")
            await page.wait_for_timeout(120)
            S = await safe("()=>window.__a3dUsageSummary()") or {}
            c = await card('areas')
            A = c.get('areas', [])

            def fmt(v):   # the app's bimDispNum(v, 2): two places, trailing zeros trimmed
                s = '%.2f' % v
                s = s.rstrip('0').rstrip('.') if '.' in s else s
                return s if s not in ('', '-') else '0'

            want = [[r['usage'], r['name'], str(r['count']), 'GBA %s \u00b7 GFA %s \u00b7 NSA %s m\u00b2' % (fmt(r['GBA']), fmt(r['GFA']), fmt(r['NSA']))] for r in S.get('rows', [])]
            got = [[a[0], a[1], a[2], a[3][0] if a[3] else ''] for a in A if a[0]]
            ck(len(want) == 2 and got == want, "a row per usage, from the model: its name, its count, GBA, GFA and NSA (%s)" % got)
            tot = [a for a in A if a[1] == 'Total']
            T = S.get('total', {})
            ck(tot and tot[0][3][0] == 'GBA %s \u00b7 GFA %s \u00b7 NSA %s m\u00b2' % (fmt(T.get('GBA', 0)), fmt(T.get('GFA', 0)), fmt(T.get('NSA', 0))),
               "and the total (%s)" % (tot and tot[0][3]))
            # the fields wear Analyze's colours, dark and light
            col = await safe("""()=>{var f=function(){var e=document.getElementById('a3d-anzf-dl'),s=getComputedStyle(e),l=getComputedStyle(document.querySelector('.a3d-anzlab'));
              return [s.backgroundColor,s.color,l.color];};var d=f();document.body.classList.add('light-theme');var l=f();document.body.classList.remove('light-theme');return [d,l];}""") or [[], []]
            ck(col[0] == ['rgb(31, 35, 39)', 'rgb(230, 234, 239)', 'rgb(138, 150, 163)'] and col[1] == ['rgb(255, 255, 255)', 'rgb(34, 34, 34)', 'rgb(95, 103, 112)'],
               "the row's fields and labels in Analyze's colours, dark and light (%s)" % col)
            await safe("(i)=>window.__a3dUsageAssign([i],'use-res')", ids[1])
            await page.wait_for_timeout(120)
            c = await card('areas')
            ck([a[1] for a in c.get('areas', [])] == ['Residential'] and c['areas'][0][2] == '2', "it follows the model: both boxes Residential now, one row (%s)" % c.get('areas'))
            await safe("()=>document.querySelector('.a3d-analyze-wrap [data-anzcard=\"areas\"] [data-anzact=\"open:Usages\"]').click()")
            await page.wait_for_timeout(200)
            u = await safe("""()=>{var g=document.querySelector('#a3d-propsbody [data-a3dpgrp="Usages"]');return g?[window.__a3dPropTab(),g.getBoundingClientRect().height>0,window.__a3dState().sel]:null;}""")
            ck(u == ['project', True, None], "its Usages button opens the usages on Project (%s)" % u)

            # ---------------------------------------------------------------------------------
            print("\n-- 4. the left panel's edge")
            async def lp(pg=None):
                return await safe("()=>window.__a3dLeftPanel()", pg=pg) or {}

            async def geo(pg=None):
                return await safe("""()=>{var p=document.getElementById('a3d-leftpanel').getBoundingClientRect(),a=document.getElementById('acad3d').getBoundingClientRect(),
                  g=document.getElementById('a3d-lgrip'),gr=g.getBoundingClientRect(),c=document.querySelector('#a3d-viewport canvas')||document.querySelector('#acad3d canvas');
                  return {pl:Math.round(p.left),pr:Math.round(p.right),pw:Math.round(p.width),al:Math.round(a.left),aw:Math.round(a.width),gl:gr.left,gr:gr.right,gw:gr.width,
                    gd:getComputedStyle(g).display,cw:c?Math.round(c.getBoundingClientRect().width):null,role:g.getAttribute('role'),ctl:g.getAttribute('aria-controls'),
                    now:g.getAttribute('aria-valuenow'),min:g.getAttribute('aria-valuemin'),max:g.getAttribute('aria-valuemax'),tab:g.tabIndex,
                    store:localStorage.getItem('acad3dLeftPanel')};}""", pg=pg) or {}

            await safe("()=>{window.__a3dSetLeftWidth(null);}")
            await page.wait_for_timeout(300)
            g0 = await geo()
            ck(g0.get('pw') == 242 and g0.get('al') == 296 and g0.get('pr') == 296 and g0.get('gd') == 'block' and g0.get('gr') <= 296.5 and g0.get('gl') >= 289,
               "at first: 242 px, the drawing from 296, the edge on the panel's side of its border (%s)" % g0)
            ck(g0.get('role') == 'separator' and g0.get('ctl') == 'a3d-leftpanel' and g0.get('now') == '242' and g0.get('min') == '242' and g0.get('max') == '560' and g0.get('tab') == 0,
               "the edge is a window splitter: a focusable separator with its value, 242 of 242 to 560, controlling the panel")
            cw0 = g0.get('cw')
            x, y = (g0['gl'] + g0['gr']) / 2, 420
            await page.mouse.move(x, y)
            await page.mouse.down()
            await page.mouse.move(x + 70, y, steps=4)
            mid = await geo()
            await page.mouse.move(x + 150, y, steps=4)
            await page.mouse.up()
            await page.wait_for_timeout(300)
            g1 = await geo()
            ck(mid.get('pw') == 312 and mid.get('al') == 366 and await safe("()=>document.body.classList.contains('a3d-lpdrag')") is False,
               "the panel follows the mouse while it drags (%s)" % [mid.get('pw'), mid.get('al')])
            ck(g1.get('pw') == 392 and g1.get('al') == 446 and g1.get('aw') == 1500 - 446 and g1.get('store') == '{"w":392}' and g1.get('now') == '392',
               "let go 150 px further: 392 px, kept; the drawing starts at 446 and gives up the room (%s)" % g1)
            ck(cw0 and g1.get('cw') and cw0 - g1['cw'] == 150, "the drawing's canvas is 150 px narrower (%s to %s)" % (cw0, g1.get('cw')))
            await page.mouse.move(g1['gl'] + 3, y)
            await page.mouse.down()
            await page.mouse.move(g1['gl'] + 900, y, steps=5)
            await page.mouse.up()
            await page.wait_for_timeout(300)
            ck((await lp()).get('w') == 560, "dragged far right it stops at 560 (%s)" % (await lp()).get('w'))
            g2 = await geo()
            await page.mouse.move(g2['gl'] + 3, y)
            await page.mouse.down()
            await page.mouse.move(5, y, steps=5)
            await page.mouse.up()
            await page.wait_for_timeout(300)
            ck((await lp()).get('w') == 242, "and far left at 242 (%s)" % (await lp()).get('w'))
            await safe("()=>window.__a3dSetLeftWidth(392)")
            await within(page.reload(), 'reload')
            await page.wait_for_timeout(2300)
            await page.wait_for_timeout(300)
            g3 = await geo()
            ck(g3.get('pw') == 392 and g3.get('al') == 446, "after a reload it is 392 px again (%s)" % [g3.get('pw'), g3.get('al')])
            await page.dblclick('#a3d-lgrip')
            await page.wait_for_timeout(300)
            g4 = await geo()
            ck(g4.get('pw') == 242 and g4.get('al') == 296 and g4.get('store') == '{}', "a double click puts it back to 242 and forgets the width (%s)" % g4.get('store'))
            # the keyboard: the W3C window splitter
            cid = await safe("()=>{var c=window.__a3dColumnAt([20,20],0,0.4,0.4,3);var s=window.__a3dState().objs;var id=s[s.length-1].id;window.__a3dSelectFor([id]);return id;}")
            pos0 = (await safe("(i)=>window.__a3dObjSnapshot(i)", cid) or {}).get('pos')
            await page.focus('#a3d-lgrip')
            await page.keyboard.press('ArrowRight')
            w1 = (await lp()).get('set')
            await page.keyboard.press('Shift+ArrowRight')
            w2 = (await lp()).get('set')
            await page.keyboard.press('ArrowLeft')
            w3 = (await lp()).get('set')
            ck([w1, w2, w3] == [258, 322, 306], "Right 16 px, Shift+Right 64, Left 16 back (%s)" % [w1, w2, w3])
            await page.keyboard.press('End')
            w4 = (await lp()).get('set')
            await page.keyboard.press('Home')
            w5 = (await lp()).get('set')
            ck([w4, w5] == [560, 242], "End the widest, Home the narrowest (%s)" % [w4, w5])
            await page.keyboard.press('ArrowRight')
            await page.keyboard.press('d')
            await page.wait_for_timeout(150)
            pos1 = (await safe("(i)=>window.__a3dObjSnapshot(i)", cid) or {}).get('pos')
            pal = await safe("()=>{var p=document.getElementById('a3d-cmdpal');return !!(p&&p.classList.contains('show'));}")
            ck(pos0 and pos1 == pos0 and pal is False and await safe("()=>document.activeElement.id") == 'a3d-lgrip',
               "the keys are the edge's: the selected column does not move, a letter opens no search (%s, %s)" % (pos0, pos1))
            await page.keyboard.press('Enter')
            await page.wait_for_timeout(300)
            sh = await safe("()=>[document.getElementById('a3d-shell').classList.contains('collapsed'),window.__a3dLeftPanel().dock,document.activeElement&&document.activeElement.className,window.__a3dLeftPanel().grip]")
            ck(sh and sh[0] is True and sh[1] == '54px' and 'a3d-paneltoggle' in (sh[2] or '') and sh[3] is False,
               "Enter shuts the panel, the edge goes with it, and the focus is on the panel button (%s)" % sh)
            await page.keyboard.press('Enter')
            await page.wait_for_timeout(350)
            g5 = await geo()
            ck(g5.get('pw') == 258 and g5.get('al') == 312 and g5.get('gd') == 'block', "Enter on the button opens it again, at its width (%s)" % [g5.get('pw'), g5.get('al')])
            await safe("()=>window.__a3dSelectFor([])")
            # a drag cancelled puts the width back
            await safe("""()=>{var g=document.getElementById('a3d-lgrip'),r=g.getBoundingClientRect(),x=r.left+3,y=300;
              var ev=function(t,dx){g.dispatchEvent(new PointerEvent(t,{pointerId:7,pointerType:'touch',isPrimary:true,clientX:x+dx,clientY:y,bubbles:true,cancelable:true}));};
              ev('pointerdown',0);ev('pointermove',60);window.__lpMid=window.__a3dLeftPanel().dock;ev('pointercancel',60);}""")
            await page.wait_for_timeout(300)
            ck(await safe("()=>window.__lpMid") == '372px' and (await geo()).get('pw') == 258 and (await lp()).get('kept') == 258,
               "a finger's drag follows it, and a cancelled one puts the width back (%s)" % await safe("()=>window.__lpMid"))
            await safe("""()=>{var g=document.getElementById('a3d-lgrip'),r=g.getBoundingClientRect(),x=r.left+3,y=300;
              var ev=function(t,dx){g.dispatchEvent(new PointerEvent(t,{pointerId:8,pointerType:'touch',isPrimary:true,clientX:x+dx,clientY:y,bubbles:true,cancelable:true}));};
              ev('pointerdown',0);ev('pointermove',40);ev('pointermove',100);ev('pointerup',100);}""")
            await page.wait_for_timeout(300)
            ck((await lp()).get('kept') == 358 and (await geo()).get('pw') == 358, "a finger's drag let go is kept (%s)" % (await lp()).get('kept'))
            # one press: the edge's alternative for a pointer that cannot drag
            await safe("()=>window.__a3dSetLeftWidth(null)")
            await page.wait_for_timeout(300)
            seen = []
            for k in range(5):
                seen.append(await safe("""()=>{var b=document.querySelector('#a3d-leftpanel [data-lpwidth]'),r=b.getBoundingClientRect();
                  return [window.__a3dLeftPanel().set,b.getAttribute('aria-label'),Math.round(r.width),Math.round(r.height),getComputedStyle(b).display];}""") or [None, '', 0, 0, ''])
                await page.click('#a3d-leftpanel [data-lpwidth]')
                await page.wait_for_timeout(250)
            last = await lp()
            ck([s[0] for s in seen] == [242, 320, 400, 480, 560] and last.get('set') == 242 and last.get('kept') == 242 and (await geo()).get('al') == 296,
               "the button widens it a step at a time, 242 to 560, then back to 242, kept (%s)" % [s[0] for s in seen])
            ck(seen[0][1] == 'Panel width 242 px: widen to 320' and seen[4][1] == 'Panel width 560 px: back to 242',
               "it says where the next press goes (%r, %r)" % (seen[0][1], seen[4][1]))
            ck(min(s[2] for s in seen) >= 24 and min(s[3] for s in seen) >= 24, "a target of 24 px or more (%s)" % seen[0][2:4])
            au = await safe("()=>window.__a3dShellAudit()") or {}
            ck(au.get('ok'), "the shell's audit knows it (%s)" % au.get('unclaimed'))
            hc = await safe("""()=>{var f=function(){return [getComputedStyle(document.querySelector('#a3d-leftpanel [data-lpwidth]')).color,
              getComputedStyle(document.querySelector('#a3d-leftpanel .a3d-panelcollapse')).color,getComputedStyle(document.querySelector('#a3d-leftpanel .a3d-projhead')).backgroundColor,
              getComputedStyle(document.getElementById('a3d-leftpanel')).backgroundColor];};var d=f();document.body.classList.add('light-theme');var l=f();document.body.classList.remove('light-theme');return [d,l];}""") or [[], []]
            ck(hc[0][:2] == ['rgb(154, 163, 173)', 'rgb(255, 255, 255)'] and hc[1][:2] == ['rgb(107, 114, 128)', 'rgb(107, 114, 128)'] and hc[1][3] == 'rgb(255, 255, 255)',
               "the header's buttons show on both themes: grey on the light theme's white, the collapse no longer white on white (%s)" % hc)
            # the drawing keeps 320 px beside Properties
            await safe("()=>{window.__a3dSetLeftWidth(560);}")
            await page.set_viewport_size({'width': 1280, 'height': 900})
            await page.wait_for_timeout(400)
            await safe("()=>window.__a3dRightSetWidth(560)")
            await page.wait_for_timeout(300)
            r = await safe("""()=>{var a=document.getElementById('acad3d').getBoundingClientRect(),rp=document.getElementById('a3d-right').getBoundingClientRect();
              return {lp:window.__a3dLeftPanel(),draw:Math.round(rp.left-a.left),rw:Math.round(rp.width)};}""") or {}
            ck(r.get('rw') == 560 and r.get('lp', {}).get('w') == 346 and r.get('lp', {}).get('kept') == 560 and r.get('draw') == 320,
               "on a 1280 px screen with Properties at 560, the panel gives way to 346 and the drawing keeps 320; the 560 kept (%s)" % r)
            await safe("()=>window.__a3dRightSetWidth(280)")
            await page.wait_for_timeout(300)
            ck((await lp()).get('w') == 560, "Properties narrower again: the panel is back at its 560 (%s)" % (await lp()).get('w'))
            await safe("()=>window.__a3dRightSetWidth(560)")
            await page.wait_for_timeout(300)
            st = []
            for k in range(3):
                await page.click('#a3d-leftpanel [data-lpwidth]')
                await page.wait_for_timeout(250)
                st.append((await lp()).get('w'))
            ck(st == [242, 320, 346], "where the screen allows 346 at most, the button goes 242, 320, then 346 (%s)" % st)
            await safe("()=>window.__a3dRightSetWidth(280)")
            await page.wait_for_timeout(300)
            # an upright tablet and a phone: the drawer keeps its width
            await safe("()=>window.__a3dSetLeftWidth(450)")
            for nm, vw, vh, dw, dock in (('tablet', 820, 1180, 340, '54px'), ('phone', 390, 844, 343, '0px')):
                await page.set_viewport_size({'width': vw, 'height': vh})
                await page.wait_for_timeout(400)
                await safe("()=>{var b=document.querySelector('#a3d-rail [data-tab=\"layers\"]');b.click();}")
                await page.wait_for_timeout(400)
                s = await lp()
                pw_ = await safe("()=>Math.round(document.getElementById('a3d-leftpanel').getBoundingClientRect().width)")
                bd = await safe("()=>getComputedStyle(document.querySelector('#a3d-leftpanel [data-lpwidth]')).display")
                ck(s.get('grip') is False and bd == 'none' and s.get('dock') == dock and pw_ == dw and s.get('kept') == 450,
                   "%s: the drawer opens at its own %d px, with no edge and no width button; the computer's 450 is kept (%s)" % (nm, dw, [pw_, s.get('dock'), s.get('grip'), bd]))
                await safe("()=>{var b=document.querySelector('#a3d-rail [data-tab=\"layers\"]');b.click();}")
                await page.wait_for_timeout(200)
            await page.set_viewport_size({'width': 1500, 'height': 950})
            await page.wait_for_timeout(500)
            g6 = await geo()
            ck(g6.get('pw') == 450 and g6.get('al') == 504 and g6.get('gd') == 'block', "back on a computer's screen it is 450 again (%s)" % [g6.get('pw'), g6.get('al')])
            await safe("()=>window.__a3dSetLeftWidth(null)")
            await page.wait_for_timeout(300)

            # ---------------------------------------------------------------------------------
            print("\n-- 5. a tablet on its side, by touch; a phone's fields")
            c2 = await browser.new_context(viewport={'width': 1366, 'height': 1024}, has_touch=True, is_mobile=True)
            p2 = await c2.new_page()
            p2.on('pageerror', lambda e: errs.append(str(e)))
            await within(p2.goto('file://' + str(HTML)), 'goto tablet')
            await p2.wait_for_timeout(2300)
            t = await geo(p2)
            ck(t.get('gd') == 'block' and t.get('gw') == 12 and t.get('pw') == 242 and abs(t.get('gr') - 296) < 0.6,
               "a tablet on its side keeps the panel beside the drawing, with a 12 px edge for a finger (%s)" % [t.get('gd'), t.get('gw')])
            box = await safe("()=>{var r=document.getElementById('a3d-lgrip').getBoundingClientRect();return [r.left+r.width/2,500];}", pg=p2)
            cdp = await c2.new_cdp_session(p2)

            async def touch(kind, xx, yy):
                pts = [] if kind == 'touchEnd' else [{'x': xx, 'y': yy, 'id': 1}]
                await cdp.send('Input.dispatchTouchEvent', {'type': kind, 'touchPoints': pts})

            await touch('touchStart', box[0], box[1])
            for k in range(1, 7):
                await touch('touchMove', box[0] + k * 20, box[1])
            await touch('touchEnd', 0, 0)
            await p2.wait_for_timeout(350)
            t = await geo(p2)
            ck(t.get('pw') == 362 and t.get('al') == 416 and t.get('store') == '{"w":362}', "a finger drags it 120 px wider, kept (%s)" % [t.get('pw'), t.get('al')])
            await c2.close()
            c3 = await browser.new_context(viewport={'width': 390, 'height': 844}, has_touch=True, is_mobile=True)
            p3 = await c3.new_page()
            p3.on('pageerror', lambda e: errs.append(str(e)))
            await within(p3.goto('file://' + str(HTML)), 'goto phone')
            await p3.wait_for_timeout(2300)
            await p3.evaluate("()=>{window.__a3dColumnAt([0,0],0,0.4,0.3,3);window.__a3dColumnAt([6,0],0,0.4,0.3,3);window.__a3dBeam([0,0],[6,0],0.3,0.5);window.__a3dSelectFor([]);}")
            await p3.evaluate("()=>document.querySelector('#a3d-rail [data-tab=\"analyze\"]').click()")
            await p3.wait_for_timeout(300)
            await p3.evaluate("()=>{var t=document.querySelector('[data-anztog=\"structure\"]');if(t.getAttribute('aria-expanded')!=='true')t.click();}")
            await p3.wait_for_timeout(100)
            ff = await p3.evaluate("""()=>[].map.call(document.querySelectorAll('[data-anzcard="structure"] select,[data-anzcard="structure"] input'),function(e){var r=e.getBoundingClientRect(),
              d=document.getElementById('a3d-leftpanel').getBoundingClientRect();return [Math.round(r.height),getComputedStyle(e).fontSize,r.right<=d.right+0.5,r.left>=d.left-0.5];})""")
            ck(len(ff) == 6 and all(f[0] >= 36 and f[1] == '16px' and f[2] and f[3] for f in ff),
               "phone: every field in the row is a finger's 36 px, 16 px text so the page does not zoom, inside the drawer (%s)" % ff[:2])
            await c3.close()
            ck(not errs, "no page errors (%s)" % errs[:3])
            ck(not warns, "nothing went wrong quietly: no [BIM] warnings (%s)" % warns[:3])
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
