#!/usr/bin/env python3
"""bim_phase141_panels_analyze_browser_tests.py -- V141: a shorter right panel, and an Analyze tab.

The owner: "clean up the right side panels because it is too much as we add more stuff", and
"adding analyze below assets".

  1. TABS: with nothing selected, Properties has Project | Site | View | Analysis; each group on its
     tab; only the shown tab's groups on screen; the site's place in its own Location group.
  2. SWITCHING: a click shows a tab in place (a half-typed value survives); the tab is remembered
     through a reload; a selection shows the object, not the tabs; each tab far shorter than the
     old panel.
  3. COMMANDS turn to the tab of the group they open: USAGES, COLOURBY, DATALAYERS, FINDDATA.
  4. ANALYZE: a rail button below Assets; seven cards, each saying what it shows now, with buttons
     that run it or open its settings; disabled with the reason when there is nothing to run.
  5. RUNNING THEM: the frame, the sun, a survey check, the LOD check, CityJSON; Settings opens the
     group on its tab; the panel follows the model as it changes.
  6. ANALYSES, the shell audit, no errors.

The harness never waits without a bound (V123).
"""
import asyncio, json, pathlib, sys, traceback
from playwright.async_api import async_playwright

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import bim_phase139_lod_cityjson_browser_tests as M139   # a CityJSON file with buildings

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'
SEED = (pathlib.Path(__file__).resolve().parent / 'data' / 'surveys' / 'seed_site_m.txt').read_text()


class Checks:
    def __init__(self):
        self.n, self.bad = 0, []

    def __call__(self, cond, msg):
        self.n += 1
        if not cond:
            self.bad.append(msg)
        print(('  ok    ' if cond else '  FAIL  ') + msg)


CK = Checks()
STALL = 60


class Stalled(Exception):
    pass


async def within(aw, what):
    try:
        return await asyncio.wait_for(aw, STALL)
    except asyncio.TimeoutError:
        raise Stalled(what)


GROUP_TAB = {'Identity Data': 'project', 'Statistics': 'project', 'Location': 'site', 'Map': 'site', 'Site Context': 'site',
             'Data Layers': 'site', 'View': 'view', 'Floor Loads: Level 0': 'analysis', 'Areas by Usage': 'analysis', 'Usages': 'analysis'}


async def run():
    ck = CK
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1500, 'height': 950}, accept_downloads=True)
        page = await ctx.new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        await within(page.goto('file://' + str(HTML)), 'goto')
        await page.wait_for_timeout(2300)

        async def safe(js, arg=None):
            try:
                return await within(page.evaluate(js, arg) if arg is not None else page.evaluate(js), 'evaluate ' + js[:50])
            except Stalled:
                raise
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:200])
                return None

        has = await safe("()=>window.__acad3dV141")
        ck(bool(has) and 'proptabs' in has and 'analyzerail' in has, "__acad3dV141 marker is present (%s)" % has)
        if not has:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.bad), ck.n))
            await browser.close()
            return 1

        async def nosel():
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dRefreshProps();}")
            await page.wait_for_timeout(80)

        async def toast():
            return await safe("()=>{var t=document.getElementById('a3d-toast');return t?t.textContent:'';}") or ''

        async def shown():
            """the groups on screen, and the tab buttons"""
            return await safe("""()=>{var b=document.getElementById('a3d-propsbody');
              var g=[].filter.call(b.querySelectorAll('[data-a3dpgrp]'),function(e){return e.getBoundingClientRect().height>0;}).map(function(e){return e.getAttribute('data-a3dpgrp');});
              var t=[].map.call(b.querySelectorAll('[data-ptabbtn]'),function(e){return [e.getAttribute('data-ptabbtn'),e.textContent,e.classList.contains('on'),e.getAttribute('aria-selected')];});
              return {groups:g,tabs:t,h:b.scrollHeight};}""") or {}

        async def click_tab(tb):
            await page.click('#a3d-propsbody [data-ptabbtn="%s"]' % tb)
            await page.wait_for_timeout(120)

        async def cards():
            return {c['id']: c for c in (await safe("()=>window.__a3dAnalyzeCards()") or [])}

        async def panel_cards():
            return await safe("""()=>{var w=document.querySelector('.a3d-analyze-wrap');if(!w)return null;
              return [].map.call(w.querySelectorAll('[data-anzcard]'),function(c){
                return {id:c.getAttribute('data-anzcard'),st:(c.querySelector('.a3d-anzst')||{}).textContent,
                  state:(c.querySelector('.a3d-anzstate')||{textContent:''}).textContent,
                  btns:[].map.call(c.querySelectorAll('[data-anzact]'),function(b){return [b.getAttribute('data-anzact'),b.textContent,b.disabled,b.title];})};});}""")

        try:
            # ---------------------------------------------------------------------------------
            print("\n-- 1. tabs")
            await safe("()=>{try{localStorage.removeItem('acad3dPropTab');}catch(e){}}")
            await within(page.reload(), 'reload')
            await page.wait_for_timeout(2300)
            await nosel()
            s = await shown()
            ck([t[:2] for t in s.get('tabs', [])] == [['project', 'Project'], ['site', 'Site'], ['view', 'View'], ['analysis', 'Analysis']],
               "with nothing selected, four tabs: Project, Site, View, Analysis (%s)" % s.get('tabs'))
            ck(s['tabs'][0][2] and s['tabs'][0][3] == 'true' and not any(t[2] for t in s['tabs'][1:]), "Project is the first shown")
            ck(s.get('groups') == ['Identity Data', 'Statistics'], "on it, only Identity Data and Statistics (%s)" % s.get('groups'))
            all_g = await safe("()=>[].map.call(document.querySelectorAll('#a3d-propsbody [data-a3dpgrp]'),function(e){return [e.getAttribute('data-a3dpgrp'),e.closest('[data-ptab]').getAttribute('data-ptab')];})") or []
            ck(dict(all_g) == GROUP_TAB, "each group on its tab, every one still in the page (%s)" % all_g)
            tabof = await safe("()=>['Identity Data','Location','Map','Site Context','Data Layers','View','Floor Loads: Level 2','Analysis','Areas by Usage','Usages','Statistics','Constraints'].map(window.__a3dPropTabOf)")
            ck(tabof == ['project', 'site', 'site', 'site', 'site', 'view', 'analysis', 'analysis', 'analysis', 'analysis', 'project', None],
               "a group's tab, by name; an object's group is on none (%s)" % tabof)
            loc = await safe("""()=>{var g=document.querySelector('#a3d-propsbody [data-a3dpgrp="Location"]').nextElementSibling;
              return [].map.call(g.querySelectorAll('[data-propmodel]'),function(e){return e.getAttribute('data-propmodel');});}""")
            idd = await safe("""()=>{var g=document.querySelector('#a3d-propsbody [data-a3dpgrp="Identity Data"]').nextElementSibling;
              return [].map.call(g.querySelectorAll('[data-propmodel]'),function(e){return e.getAttribute('data-propmodel');});}""")
            ck(loc == ['truenorth', 'sunlat', 'sunlon', 'suntz', 'sundate', 'suntime'] and idd == ['project', 'client', 'site'],
               "the site's place and the sun in Location; Identity Data keeps project, client and site (%s; %s)" % (loc, idd))

            # ---------------------------------------------------------------------------------
            print("\n-- 2. switching")
            h0 = s['h']
            await page.fill('#a3d-propsbody [data-propmodel="client"]', 'Half typed')
            await safe("()=>{document.querySelector('#a3d-propsbody [data-a3dpgrp=\"Location\"]').__v141mark=1;}")
            await click_tab('site')
            ck(await safe("()=>document.querySelector('#a3d-propsbody [data-a3dpgrp=\"Location\"]').__v141mark===1"),
               "the tab turns in place: the groups are the same nodes")
            s = await shown()
            ck(s.get('groups') == ['Location', 'Map', 'Site Context', 'Data Layers'] and s['tabs'][1][2] and s['tabs'][1][3] == 'true' and s['tabs'][0][3] == 'false',
               "a click on Site shows Location, Map, Site Context and Data Layers (%s)" % s.get('groups'))
            await click_tab('project')
            v = await safe("()=>document.querySelector('#a3d-propsbody [data-propmodel=\"client\"]').value")
            ck(v == 'Half typed', "and back: a half-typed field is still as typed -- the tab turns in place (%r)" % v)
            await page.keyboard.press('Escape')
            await click_tab('view')
            ck((await shown()).get('groups') == ['View'], "View: the View group")
            await click_tab('analysis')
            s = await shown()
            ck(s.get('groups') == ['Floor Loads: Level 0', 'Areas by Usage', 'Usages'], "Analysis: floor loads, areas by usage, usages (%s)" % s.get('groups'))
            hs = []
            for tb in ('project', 'site', 'view', 'analysis'):
                await safe("(t)=>window.__a3dSetPropTab(t)", tb)
                hs.append(await safe("()=>document.getElementById('a3d-propsbody').scrollHeight"))
            whole = await safe("""()=>{var P=document.querySelectorAll('#a3d-propsbody .a3d-ptabpane');[].forEach.call(P,function(p){p.style.display='block';});
              var h=document.getElementById('a3d-propsbody').scrollHeight;[].forEach.call(P,function(p){p.style.display='';});return h;}""")
            ck(max(hs) < 0.6 * whole and min(hs) < 0.35 * whole, "each tab far shorter than all the groups at once (%s against %s px)" % (hs, whole))
            ck(await safe("(t)=>window.__a3dSetPropTab(t)", 'nowhere') is False and await safe("()=>window.__a3dPropTab()") == 'analysis', "a tab that is not one is refused")
            await safe("(t)=>window.__a3dSetPropTab(t)", 'project')
            await click_tab('site')   # a click, as a person would
            await within(page.reload(), 'reload')
            await page.wait_for_timeout(2300)
            await nosel()
            s = await shown()
            ck(await safe("()=>window.__a3dPropTab()") == 'site' and s.get('groups', [None])[0] == 'Location', "the tab shown is remembered through a reload")
            cid = await safe("()=>window.__a3dColumnAt([0,0],0,0.4,0.4,3)")
            await safe("(i)=>{window.__a3dSelectFor([i]);window.__a3dRefreshProps();}", cid)
            await page.wait_for_timeout(100)
            s = await shown()
            ck(not s.get('tabs') and 'Location' not in s.get('groups', []) and 'Statistics' not in s.get('groups', []) and
               not await safe("()=>!!document.querySelector('#a3d-propsbody .a3d-ptabpane')"), "a selected column shows its own groups, with no tabs (%s)" % s.get('groups'))
            await nosel()
            ck((await shown()).get('groups', [None])[0] == 'Location', "and with nothing selected again, the same tab")
            await safe("()=>window.__a3dUndo()")

            # ---------------------------------------------------------------------------------
            print("\n-- 3. commands turn to the group's tab")
            for cmd, tb, grp in (('usages', 'analysis', 'Usages'), ('colourby', 'view', 'View'), ('datalayers', 'site', 'Data Layers')):
                await safe("(t)=>window.__a3dSetPropTab(t)", 'project')
                await safe("(c)=>window.__a3dRunCmd(c)", cmd)
                await page.wait_for_timeout(150)
                s = await shown()
                ck(await safe("()=>window.__a3dPropTab()") == tb and grp in s.get('groups', []), "%s turns to %s, its group on screen (%s)" % (cmd.upper(), tb, s.get('groups')))
            await safe("(t)=>window.__a3dSetPropTab(t)", 'view')
            await safe("()=>window.__a3dRunCmd('finddata')")
            await page.wait_for_timeout(150)
            f = await safe("()=>document.activeElement&&document.activeElement.getAttribute('data-propfind')")
            ck(await safe("()=>window.__a3dPropTab()") == 'site' and f == 'q', "FINDDATA turns to Site and puts the cursor in its search (%s)" % f)
            await page.keyboard.press('Escape')

            # ---------------------------------------------------------------------------------
            print("\n-- 4. Analyze")
            rail = await safe("()=>[].map.call(document.querySelectorAll('#a3d-rail .a3d-railbtn'),function(b){return [b.getAttribute('data-tab'),b.getAttribute('title'),!!b.querySelector('svg path')];})")
            ck(rail and [r[0] for r in rail] == ['layers', 'presentation', 'browser', 'assets', 'analyze'] and rail[-1][1] == 'Analyze' and rail[-1][2],
               "the rail: Analyze below Assets, with its icon (%s)" % rail)
            await page.click('#a3d-rail [data-tab="analyze"]')
            await page.wait_for_timeout(250)
            pc = await panel_cards()
            # AMENDED FOR V143: the Simulation section's three cards follow the seven
            # AMENDED FOR V144: the terrain card follows the survey's
            # AMENDED FOR V145: the grading card follows the terrain's
            ck(pc and [c['id'] for c in pc] == ['structure', 'sun', 'lens', 'areas', 'survey', 'terrain', 'grading', 'lod', 'stats', 'sunhours', 'solar', 'rain'],
               "seven cards: structure, sun, colour by, areas, survey, LOD, statistics (%s)" % (pc and [c['id'] for c in pc]))
            P = {c['id']: c for c in pc or []}
            ck(P.get('structure', {}).get('st') == 'No frame yet: place columns and beams' and P['structure']['btns'][0][2] and
               P['structure']['btns'][0][3] == 'Place columns and beams first', "Structure: no frame yet, Run disabled with the reason")
            ck(P.get('sun', {}).get('st', '').startswith('Set the site latitude, longitude') and P['sun']['state'] == 'Off', "Sun: the site is not placed, Off")
            ck(P.get('survey', {}).get('btns', [[0, 0, False]])[0][2] and P.get('lod', {}).get('btns', [[0, 0, False]])[0][2], "Survey and LOD checks disabled with nothing to check")
            ck(P.get('stats', {}).get('st', '').startswith('0 objects, 1 level'), "Statistics: 0 objects, 1 level (%s)" % P.get('stats', {}).get('st'))
            # the model grows; the panel follows
            ids = await safe("()=>{var a=window.__a3dColumnAt([0,0],0,0.4,0.4,3),b=window.__a3dColumnAt([6,0],0,0.4,0.4,3);var bm=window.__a3dBeam([0,0],[6,0],0.3,0.5);window.__a3dRefreshProps();return [a,b,bm];}")
            await page.wait_for_timeout(150)
            P = {c['id']: c for c in await panel_cards() or []}
            ck(P.get('structure', {}).get('st') == '2 columns, 1 beam' and not P['structure']['btns'][0][2], "the panel follows the model: 2 columns, 1 beam, Run enabled")
            await page.click('.a3d-analyze-wrap [data-anzact="structure:run"]')
            await page.wait_for_timeout(250)
            P = {c['id']: c for c in await panel_cards() or []}
            ck(P['structure']['state'] == 'On' and 'forces and deflection shown' in P['structure']['st'] and 'Largest moment' in await toast(),
               "Run solves the frame: On, and the toast gives the result")
            await page.click('.a3d-analyze-wrap [data-anzact="structure:off"]')
            await page.wait_for_timeout(150)
            ck((await cards())['structure']['state'] == 'off', "Hide turns it off")
            await page.click('.a3d-analyze-wrap [data-anzact="open:Analysis"]')
            await page.wait_for_timeout(200)
            s = await shown()
            ck(await safe("()=>window.__a3dPropTab()") == 'analysis' and 'Analysis' in s.get('groups', []) and await safe("()=>window.__a3dState().sel") is None,
               "Settings: nothing selected, Properties on Analysis, the Analysis group shown (%s)" % s.get('groups'))
            # the sun
            await safe("(t)=>window.__a3dSetPropTab(t)", 'site')
            for k, v in (('sunlat', '40'), ('sunlon', '-75'), ('suntz', '-4')):
                await page.fill('#a3d-propsbody [data-propmodel="%s"]' % k, v)
                await page.keyboard.press('Enter')
                await page.wait_for_timeout(100)
            P = {c['id']: c for c in await panel_cards() or []}
            ck(P['sun']['st'].startswith('12:00 on ') and 'the sun at' in P['sun']['st'], "once placed, the sun card gives the time and the sun's height (%s)" % P['sun']['st'])
            await page.click('.a3d-analyze-wrap [data-anzact="sun:toggle"]')
            await page.wait_for_timeout(150)
            ck((await cards())['sun']['state'] == 'on' and 'Sun study' in await toast(), "Show turns the sun study on")
            await page.click('.a3d-analyze-wrap [data-anzact="sun:toggle"]')
            await page.wait_for_timeout(150)
            ck((await cards())['sun']['state'] == 'off', "and Hide off")
            await page.click('.a3d-analyze-wrap [data-anzact="open:Location"]')
            await page.wait_for_timeout(200)
            ck(await safe("()=>window.__a3dPropTab()") == 'site' and (await shown()).get('groups', [None])[0] == 'Location', "its Settings open Location, on Site")
            # a survey
            r = await safe("(t)=>window.__a3dSurveyImport(t,'PNEZD','m')", SEED)
            await safe("()=>window.__a3dRefreshProps()")
            await page.wait_for_timeout(150)
            P = {c['id']: c for c in await panel_cards() or []}
            ck(r and r.get('id') and P['survey']['st'].startswith('1 surface: ') and not P['survey']['btns'][0][2], "a survey: the card counts it (%s)" % P['survey']['st'])
            await nosel()
            await page.click('.a3d-analyze-wrap [data-anzact="survey:run"]')
            await page.wait_for_timeout(250)
            ck(await safe("()=>window.__a3dState().sel") == r.get('id') and 'Survey' in (await safe("()=>document.getElementById('a3d-propsbody').innerHTML") or ''),
               "Check runs SURVEYCHECK: the surface selected, its Survey Check shown")
            # buildings
            await safe("(t)=>window.__a3dCityJsonImport(t,'nl.city.json')", json.dumps(M139.foreign_file()))
            await safe("()=>window.__a3dRefreshProps()")
            await page.wait_for_timeout(150)
            P = {c['id']: c for c in await panel_cards() or []}
            ck(P['lod']['st'].startswith('3 buildings and city objects (1 LOD1, 1 LOD1.2, 1 LOD2.2)'), "the buildings and city objects counted by LOD (%s)" % P['lod']['st'])
            await page.click('.a3d-analyze-wrap [data-anzact="lod:run"]')
            await page.wait_for_timeout(250)
            P = {c['id']: c for c in await panel_cards() or []}
            ck('last check: 2 valid, 1 with problems' in P['lod']['st'] and P['lod']['state'] == 'Problems', "Check runs LODCHECK; the card keeps its result (%s)" % P['lod']['st'])
            async with page.expect_download() as dl:
                await page.click('.a3d-analyze-wrap [data-anzact="lod:cityjson"]')
            ck((await dl.value).suggested_filename.endswith('.city.json'), "Export CityJSON exports")
            for act, tb, grp in (('open:View', 'view', 'View'), ('open:Areas by Usage', 'analysis', 'Areas by Usage'), ('open:Usages', 'analysis', 'Usages'),
                                 ('open:Statistics', 'project', 'Statistics')):
                await page.click('.a3d-analyze-wrap [data-anzact="%s"]' % act)
                await page.wait_for_timeout(150)
                ck(await safe("()=>window.__a3dPropTab()") == tb and grp in (await shown()).get('groups', []), "%s opens %s, on %s" % (act, grp, tb))

            # ---------------------------------------------------------------------------------
            print("\n-- 6. the command, the audit")
            await page.click('#a3d-rail [data-tab="assets"]')
            await page.wait_for_timeout(150)
            ck(not await safe("()=>!!document.querySelector('.a3d-analyze-wrap')"), "another tab takes the panel")
            await safe("()=>window.__a3dRunCmd('analyses')")
            await page.wait_for_timeout(200)
            ck(await safe("()=>document.getElementById('a3d-shell').getAttribute('data-tab')") == 'analyze' and await safe("()=>!!document.querySelector('.a3d-analyze-wrap')"),
               "ANALYSES opens the Analyze tab")
            nm = [x['name'] for x in (await safe("(q)=>window.__a3dCommandSearch(q,5)", 'dashboard') or [])]
            ck('ANALYSES' in nm[:3], "searching 'dashboard' finds it (%s)" % nm)
            au = await safe("()=>window.__a3dShellAudit()") or {}
            ck(au.get('ok') and au.get('claimed', 0) > 10, "the shell audit is clean with the Analyze tab open (%s)" % au.get('unclaimed'))
            ck(not errs, "no page errors (%s)" % errs[:3])
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
