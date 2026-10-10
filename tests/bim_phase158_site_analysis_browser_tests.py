#!/usr/bin/env python3
"""bim_phase158_site_analysis_browser_tests.py -- V158: Site analysis SA1, the workspace and the standard.

The owner (V156): "i want to standardize the whole process." The standard
(reference/research-site-analysis-process.md): six stages after Define, ten fixed categories, and
findings that each name a source, a date and how sure they are, classed as a constraint, an
opportunity, a red flag or a fact. The context comes from V157's Overpass fixture on V133's terrain.

  1. THE TAB AND THE STANDARD: the Site rail tab, the commands, the stages and the ten categories.
  2. FILL FROM THE MODEL: nothing known says so; then the location, the context, the property, the
     terrain's relief and slope, the sun's day lengths, trees, streets, rail, the airport, power,
     land use, each with its source and date; refilled in place, what was said about it kept.
  3. FINDINGS: added, numbered, edited (each field checked), moved, deleted, each one undo step.
  4. DEFINE AND CHECKLISTS: stage, project type, questions; the desk and site checklists.
  5. ON THE PLAN AND PHOTOGRAPHS: placed by a click, numbered pins, hidden; a photograph kept small.
  6. THE PANEL: categories open, Edit and a field typed, red flags first; a reload keeps it all;
     a phone.
  7. ANALYSIS AND DATA IN LAYERS, as Context is: rows with a caret, swatch, count and an eye in the
     layers' eye column; the eye shows or hides the whole group, one undo step.

The harness never waits without a bound (V123).
"""
import asyncio, json, pathlib, re, sys, traceback

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from bim_phase133_site_context_browser_tests import (   # noqa: E402
    Checks, Stalled, within, m2g, G, ring, terrarium_png, LAT0, LON0, near)
import bim_phase157_site_context_infra_browser_tests as V157   # noqa: E402
from playwright.async_api import async_playwright   # noqa: E402

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'

CK = Checks()
CATS = ['location', 'legal', 'landform', 'water', 'climate', 'ecology', 'risk', 'access', 'utilities', 'people']


def fixture():
    js = V157.fixture()
    js['elements'].append({'type': 'way', 'id': 9001, 'tags': {'building': 'yes', 'height': '15'},
                           'geometry': G(ring([(40, -20), (55, -20), (55, -8), (40, -8)]))})
    js['elements'].append({'type': 'way', 'id': 9002, 'tags': {'building': 'yes', 'height': '9'},
                           'geometry': G(ring([(-40, 50), (-28, 50), (-28, 60), (-40, 60)]))})
    return js


async def run():
    ck = CK
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1400, 'height': 900})
        page = await ctx.new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))

        async def ovp_route(route):
            await route.fulfill(status=200, body=json.dumps(fixture()),
                                headers={'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'})
        for host in ('https://overpass-api.de/**', 'https://overpass.private.coffee/**', 'https://maps.mail.ru/**',
                     'https://overpass.kumi.systems/**'):
            await ctx.route(host, ovp_route)

        async def ter_route(route):
            m = re.search(r'/terrarium/(\d+)/(\d+)/(\d+)\.png$', route.request.url)
            if not m:
                await route.abort('internetdisconnected')
                return
            await route.fulfill(status=200, body=terrarium_png(int(m.group(1)), int(m.group(2)), int(m.group(3))), headers={
                'Content-Type': 'image/png', 'Access-Control-Allow-Origin': '*'})
        await ctx.route('https://s3.amazonaws.com/**', ter_route)
        await ctx.route('https://data.example.org/**', lambda r: r.fulfill(status=200, body='{"type":"FeatureCollection","features":[]}',
                                                                        headers={'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'}))

        await within(page.goto('file://' + str(HTML)), 'goto')
        await page.wait_for_timeout(2300)

        async def safe(js, arg=None):
            try:
                return await within(page.evaluate(js, arg) if arg is not None else page.evaluate(js),
                                    'evaluate ' + js[:60].replace('\n', ' '))
            except Stalled:
                raise
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:200])
                return None

        async def toast():
            return await safe("()=>{var t=document.getElementById('a3d-toast');return t?t.textContent:'';}") or ''

        async def sa():
            return await safe("()=>window.__a3dSa()") or {}

        async def fnd(key=None, fid=None):
            for f in (await sa()).get('findings', []):
                if (key and f.get('auto') == key) or (fid and f['id'] == fid):
                    return f
            return None

        async def panel():
            return await safe("()=>{var w=document.querySelector('.a3d-sa-wrap');return w?w.innerHTML:null;}")

        async def set_field(sel, val):
            ok = await safe("""(a)=>{var e=document.querySelector('#a3d-propsbody '+a[0]);if(!e)return false;
              e.value=a[1];e.dispatchEvent(new Event('change',{bubbles:true}));return true;}""", [sel, val])
            await page.wait_for_timeout(120)
            return ok

        try:
            has = await safe("()=>window.__acad3dV158")
            ck(bool(has) and 'findings' in has and 'checklists' in has, "__acad3dV158 marker is present (%s)" % has)
            mv = re.search(r"var BIM_APP_VERSION=\{v:'V(\d+)'", HTML.read_text(encoding='utf-8'))
            ck(mv and int(mv.group(1)) >= 158, "the app says V158 or later (%s)" % (mv and mv.group(1)))
            if not has:
                raise Stalled('no V158')
            await safe("()=>{window.__a3dEnter();window.__a3dTestSetObjs([]);}")

            # ---------------------------------------------------------------------------------
            print("\n-- 1. the tab and the standard")
            # AMENDED FOR V159: the owner asked for Site analysis inside Analyze, so no rail tab of its own:
            # Analyze's switch, Analyses | Site analysis
            await safe("()=>{document.querySelector('#a3d-rail .a3d-railbtn[data-tab=\"analyze\"]').click();}")
            await page.wait_for_timeout(150)
            # AMENDED FOR V162: one Analyze -- the site analysis is in its one list, no switch, no rail tab
            rb = await safe("""()=>{var w=document.querySelector('#a3d-leftpanel .a3d-analyze-wrap');
              return w?{sa:w.classList.contains('a3d-sa-wrap'),cats:w.querySelectorAll('[data-sacat]').length,sw:document.querySelectorAll('[data-anzview]').length,rail:!!document.querySelector('#a3d-rail [data-tab="site"]')}:null;}""")
            ck(rb == {'sa': True, 'cats': 10, 'sw': 0, 'rail': False}, "Site analysis in Analyze's one list, no rail tab of its own (%s)" % rb)
            await safe("()=>window.__a3dRunCmd('siteanalysis')")
            await page.wait_for_timeout(150)
            ck(await safe("()=>document.getElementById('a3d-shell').dataset.tab") == 'analyze' and await panel(),
               "SITEANALYSIS opens it")
            for q, want in (('site analysis', 'SITEANALYSIS'), ('due diligence', None), ('fill site analysis', 'SAFILL')):
                nm = [x['name'] for x in (await safe("(q)=>window.__a3dCommandSearch(q,5)", q) or [])]
                if want:
                    ck(want in nm[:3], "searching %r finds %s (%s)" % (q, want, nm))
            nm = [x['name'] for x in (await safe("(q)=>window.__a3dCommandSearch(q,5)", 'railway') or [])]
            ck('CONTEXT' in nm[:2], "CONTEXT's description names V157's kinds")
            stn = await safe("()=>window.__a3dSaStandard()") or {}
            ck(stn.get('stages') == ['Define', 'Desktop', 'Visit', 'Surveys', 'Analysis', 'Synthesis', 'Report'],
               "seven stages: Define, then the six (%s)" % stn.get('stages'))
            ck([c['id'] for c in stn.get('cats', [])] == CATS and all(c['desk'] >= 2 and c['visit'] >= 2 for c in stn.get('cats', [])),
               "the ten categories in their fixed order, each with what to find at the desk and check on site")
            s0 = await sa()
            ck(s0.get('stage') == 0 and s0.get('findings') == [] and s0.get('pins') is True, "a new project: at Define, no findings")
            h = await panel() or ''
            ck(h.count('data-sacat=') == 10 and h.count('data-sastage=') == 7 and 'data-sastage="0" aria-pressed="true"' in h,
               "the panel: seven stage buttons, Define pressed, ten categories")
            ck('From a shape' in h and 'Fill from the model' in h, "no boundary yet: it offers to make one")

            # ---------------------------------------------------------------------------------
            print("\n-- 2. fill from the model")
            r = await safe("()=>window.__a3dSaFill()") or {}
            ck(r.get('total') == 0 and 'nothing known yet' in await toast() and (await sa()).get('findings') == [],
               "nothing known: it says so, and adds nothing")
            await safe("()=>window.__a3dUndo()")
            await safe("()=>window.__a3dRunCmd('3d')")
            await safe("()=>window.__a3dRunCmd('2d')")
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dRefreshProps();}")
            await set_field('[data-propmodel="sunlat"]', repr(LAT0))
            await set_field('[data-propmodel="sunlon"]', repr(LON0))
            await safe("""()=>{var o=window.__a3dState().objs;o.push({id:'LOT',t:'sketch',name:'Lot',col:'#5ec4b8',pos:[0,0,0],pts:[[0,0],[30,0],[30,20],[0,20]],y:0,closed:true,layer:'layer-0'});
              window.__a3dTestSetObjs(o);window.__a3dPropertyFromSketch('LOT');}""")
            rc = await safe("()=>Promise.resolve(window.__a3dCtxFetch())") or {}
            ck((rc.get('counts') or {}).get('buildings') == 2, "(the context fetched: %s)" % rc.get('counts'))
            r = await safe("()=>window.__a3dSaFill()") or {}
            S = await sa()
            keys = sorted(f.get('auto') for f in S.get('findings', []))
            want = sorted(['location.place', 'location.built', 'legal.boundary', 'landform.terrain', 'climate.sun', 'ecology.green',
                           'access.roads', 'access.rail', 'access.airport', 'utilities.power', 'people.landuse'])
            ck(keys == want and r.get('added') == 11, "eleven findings from what the model knows (%s)" % keys)
            ck(all(f['source'] and re.match(r'^\d{4}-\d{2}-\d{2}$', f['date']) and f['conf'] == 'desktop' for f in S['findings']),
               "every one with a source, a date, and Desktop as its confidence")
            ck(S.get('stage') == 1, "the project moved on to the desktop study")
            f = await fnd('location.place')
            ck(f and f['value'].startswith('40.00000° N, 75.00000° W') and f['source'] == 'Project location', "the location (%s)" % (f and f['value']))
            f = await fnd('location.built')
            ck(f and f['value'] == '2 buildings within 150 m; mean height 12.0 m, tallest 15.0 m' and 'OpenStreetMap' in f['source'],
               "the built context: count, mean and tallest heights, credited to OpenStreetMap (%s)" % (f and f['value']))
            f = await fnd('legal.boundary')
            ck(f and f['cat'] == 'legal' and '600 m²' in f['value'] and 'perimeter 100 m' in f['value'] and f['cls'] == 'neutral',
               "the property line: its area and perimeter (%s)" % (f and f['value']))
            f = await fnd('landform.terrain')
            m = re.match(r'Ground (\d+\.\d) to (\d+\.\d) m above sea level \(relief (\d+\.\d) m\); mean slope (\d+\.\d)%, steepest (\d+)%', (f or {}).get('value', ''))
            ck(m and abs(float(m.group(2)) - float(m.group(1)) - float(m.group(3))) < 0.11 and 'Terrain Tiles' in f['source'],
               "the terrain: its heights above sea level, relief and slope, credited to the tiles (%s)" % (f and f['value']))
            ck(m and float(m.group(4)) < 5 and f['cls'] == 'opportunity', "gentle ground (under 5%) is an opportunity")
            sl = await safe("""()=>window.__a3dSaSlope({P:[[0,0],[10,0],[0,10],[110,0],[10,100],[200,0],[201,0],[200,1]],H:[0,0,0,0,10,0,0,1],
              tris:[[0,1,2],[1,3,4],[5,6,7]],outside:{}})""") or {}
            ck(near(sl.get('mean'), 500.5 / 5050.5, 1e-9) and near(sl.get('max'), 1, 1e-9) and near(sl.get('steepShare'), 0.5 / 5050.5, 1e-9) and near(sl.get('area'), 5050.5, 1e-9),
               "the slope weighed by area: a flat corner, a 10%% field, one 100%% bank (%s)" % sl)
            f = await fnd('climate.sun')
            dm = re.match(r'21 June: (\d+) h (\d\d) min; 21 December: (\d+) h (\d\d) min', (f or {}).get('value', ''))
            ck(dm and 14 * 60 + 50 <= int(dm.group(1)) * 60 + int(dm.group(2)) <= 15 * 60 + 10 and 9 * 60 + 10 <= int(dm.group(3)) * 60 + int(dm.group(4)) <= 9 * 60 + 30,
               "the day lengths at 40° N: about 15 hours in June, 9 h 20 in December (%s)" % (f and f['value']))
            f = await fnd('access.roads')
            ck(f and f['value'].startswith('6 roads within 150 m: ') and '1 bridge' in f['value'] and '1 tunnel' in f['value'] and 'car road' in f['value'] and '1 footway' in f['value'],
               "the streets: counted by use, with the bridge and the tunnel (%s)" % (f and f['value']))
            f = await fnd('access.airport')
            ck(f and f['cls'] == 'constraint' and f['sev'] == 2 and 'height limits' in f['value'], "an airport: a medium constraint, noise and height limits")
            f = await fnd('utilities.power')
            ck(f and f['cls'] == 'constraint' and f['cat'] == 'utilities' and f['value'].startswith('3 pylons and lines'), "overhead power: a constraint (%s)" % (f and f['value']))
            f = await fnd('people.landuse')
            ck(f and f['value'] == '1 residential area within 150 m', "the land use around (%s)" % (f and f['value']))
            f = await fnd('ecology.green')
            ck(f and f['value'].startswith('7 trees, 0 green areas') and f['cls'] == 'opportunity', "trees and green")
            ck(not await fnd('water.bodies'), "no water in the fixture, no water finding")
            n0 = len(S['findings'])
            r = await safe("()=>window.__a3dSaFill()") or {}
            ck(len((await sa())['findings']) == n0 and r.get('added') == 0 and r.get('updated') == 0, "filled again: nothing doubled, nothing changed")
            fa = await fnd('access.airport')
            await safe("(i)=>window.__a3dSaSet(i,'cls','redflag')", fa['id'])
            await safe("(i)=>window.__a3dSaSet(i,'note','Check the airport\\'s height surfaces')", (await fnd('access.rail'))['id'])
            await safe("()=>window.__a3dSaFill()")
            ck((await fnd('access.airport'))['cls'] == 'redflag', "a class the owner set is kept on a refill")
            await safe("()=>window.__a3dRunCmd('contextremove')")
            r = await safe("()=>window.__a3dSaFill()") or {}
            S = await sa()
            keys2 = sorted(f.get('auto') for f in S['findings'])
            kept = [f for f in S['findings'] if f['title'] == 'Railways']
            ck(r.get('removed') == 6 and 'access.roads' not in keys2 and 'location.place' in keys2 and 'legal.boundary' in keys2,
               "the context removed and refilled: its findings go (%s gone), the rest stay" % r.get('removed'))
            ck(len(kept) == 1 and kept[0]['auto'] == '' and kept[0]['note'] and len([f for f in S['findings'] if f['title'] == 'Airport']) == 1,
               "except those the owner wrote on or classed: kept, no longer refilled")
            await safe("()=>window.__a3dUndo()")
            await safe("()=>window.__a3dUndo()")
            ck(await fnd('access.roads') is not None, "the fill and the removal, one undo step each")

            # ---------------------------------------------------------------------------------
            print("\n-- 3. findings")
            a = await safe("()=>window.__a3dSaAdd('risk',{title:'Former petrol station next door',value:'Tanks may remain',cls:'redflag',sev:3,source:'Historic aerial photographs, 1962'})")
            b = await safe("()=>window.__a3dSaAdd('risk',{title:'Rail noise'})")
            f = await fnd(fid=a)
            ck(f and f['cat'] == 'risk' and f['cls'] == 'redflag' and f['sev'] == 3 and f['conf'] == 'desktop' and f['date'] == (await safe("()=>new Date().toISOString().slice(0,10)")),
               "a finding added: its class, severity, confidence and today's date")
            ck(await safe("(i)=>window.__a3dSaNumber(i)", a) == '7.1' and await safe("(i)=>window.__a3dSaNumber(i)", b) == '7.2',
               "numbered by category: 7.1 and 7.2 under Environmental risk")
            ck(await safe("()=>window.__a3dSaAdd('nonsense',{})") is None, "no finding in a category that is not one of the ten")
            for k, v, ok in (('cls', 'constraint', True), ('cls', 'bad', False), ('sev', '2', True), ('sev', '5', False), ('conf', 'site', True),
                             ('conf', 'rumour', False), ('date', '2026-09-30', True), ('date', '30/09/2026', False), ('title', 'Rail noise, day and night', True),
                             ('source', 'Heard on the visit', True), ('nope', 'x', False)):
                got = await safe("(a)=>window.__a3dSaSet(a[0],a[1],a[2])", [b, k, v])
                ck(got is ok, "set %s to %r: %s" % (k, v, 'taken' if ok else 'refused'))
            f = await fnd(fid=b)
            ck(f['cls'] == 'constraint' and f['sev'] == 2 and f['conf'] == 'site' and f['date'] == '2026-09-30' and f['title'] == 'Rail noise, day and night',
               "what was taken is kept; what was refused changed nothing")
            await safe("()=>window.__a3dUndo()")
            ck((await fnd(fid=b))['source'] == '', "each edit one undo step")
            await safe("(i)=>window.__a3dSaSet(i,'cat','access')", b)
            ck(await safe("(i)=>window.__a3dSaNumber(i)", b) == '8.%d' % (1 + len([x for x in (await sa())['findings'] if x['cat'] == 'access']) - 1),
               "moved to Access: numbered there")
            ck(await safe("(i)=>window.__a3dSaDel(i)", b) and await fnd(fid=b) is None and await safe("(i)=>window.__a3dSaDel(i)", b) is False,
               "deleted, once")

            # ---------------------------------------------------------------------------------
            print("\n-- 4. define and the checklists")
            ck(await safe("()=>window.__a3dSaDefine('ptype','Mixed use')") and (await sa())['ptype'] == 'Mixed use', "the project type")
            ck(await safe("()=>window.__a3dSaDefine('ptype','Spaceport')") is False, "only a type from the list")
            await safe("()=>window.__a3dSaDefine('questions','How many homes fit, and where is the entry?')")
            await safe("()=>window.__a3dSaDefine('stage',2)")
            S = await sa()
            ck(S['questions'].startswith('How many homes') and S['stage'] == 2, "the questions, and the stage: Visit")
            ck(await safe("()=>window.__a3dSaDefine('stage',7)") is False, "no eighth stage")
            ck(await safe("()=>window.__a3dSaCheck('legal:d:0',true)") and await safe("()=>window.__a3dSaCheck('legal:v:1',true)"), "two checklist items ticked")
            ck(await safe("()=>window.__a3dSaCheck('legal:d:9',true)") is False and await safe("()=>window.__a3dSaCheck('mars:d:0',true)") is False,
               "an item that is not on the list is refused")
            ck((await sa())['checks'] == {'legal:d:0': True, 'legal:v:1': True}, "kept with the project")
            await safe("()=>window.__a3dSaCheck('legal:v:1',false)")
            ck((await sa())['checks'] == {'legal:d:0': True}, "and unticked")

            # ---------------------------------------------------------------------------------
            print("\n-- 5. on the plan, and photographs")
            await safe("()=>window.__a3dRunCmd('siteanalysis')")
            await safe("(i)=>window.__a3dSaPlace(i,[5,5])", a)
            await safe("()=>window.__a3dTestPaint&&window.__a3dTestPaint()")
            await page.wait_for_timeout(150)
            pins = await safe("()=>window.__a3dSaPins()") or []
            ck(len(pins) == 1 and pins[0]['n'] == '7.1' and pins[0]['cls'] == 'redflag', "a pin on the plan, numbered as in the list (%s)" % pins)
            ck(await safe("(i)=>window.__a3dSaStartPin(i)", (await fnd('legal.boundary'))['id']), "Place on the plan: a click awaited")
            cr = await safe("()=>window.__a3dCanvasRect()")
            sp = await safe("(p)=>window.__a3dProject(p)", [12, 0, 8])
            px, py = cr['left'] + sp['x'], cr['top'] + sp['y']
            await page.mouse.click(px, py)
            await page.wait_for_timeout(200)
            fb = await fnd('legal.boundary')
            pins = await safe("()=>window.__a3dSaPins()") or []
            pb = [p for p in pins if p['id'] == fb['id']]
            ck(fb['at'] and abs(fb['at'][0] - 12) < 0.05 and abs(fb['at'][1] - 8) < 0.05, "clicked: pinned at the point clicked, 12, 8 (%s)" % fb['at'])
            ck(pb and abs(pb[0]['x'] - sp['x']) < 1.5 and abs(pb[0]['y'] - sp['y']) < 1.5, "its pin drawn there (%s)" % pb)
            ck('pinned on the plan' in await toast(), "and it says so")
            await safe("()=>window.__a3dSaDefine('pins',false)")
            await safe("()=>window.__a3dTestPaint&&window.__a3dTestPaint()")
            ck(await safe("()=>window.__a3dSaPins()") == [], "hidden with the switch")
            await safe("()=>window.__a3dSaDefine('pins',true)")
            await safe("(i)=>window.__a3dSaPlace(i,null)", fb['id'])
            ck((await fnd(fid=fb['id']))['at'] is None, "taken off the plan")
            ok = await safe("""(i)=>{var c=document.createElement('canvas');c.width=2400;c.height=1200;var x=c.getContext('2d');x.fillStyle='#3a7';x.fillRect(0,0,2400,1200);
              return window.__a3dSaPhotoUrl(i,c.toDataURL('image/png'));}""", a)
            fp = await fnd(fid=a)
            dims = await safe("""(u)=>new Promise(function(r){var im=new Image();im.onload=function(){r([im.width,im.height]);};im.onerror=function(){r(null);};im.src=u;})""", fp.get('photo') or '')
            ck(ok and fp['photo'].startswith('data:image/jpeg') and dims == [960, 480], "a photograph: a JPEG, at most 960 px across (%s)" % dims)
            await safe("(i)=>window.__a3dSaEdit(i)", a)
            await safe("()=>{var b=document.querySelector('.a3d-sa-wrap [data-satog=\"risk\"]');var c=b.closest('[data-sacat]');if(!c.classList.contains('open'))b.click();}")
            ck(await safe("(i)=>!!document.querySelector('.a3d-sa-wrap [data-safind=\"'+i+'\"] img.a3d-safph')", a), "shown in the finding")

            # ---------------------------------------------------------------------------------
            print("\n-- 6. the panel")
            h = await panel() or ''
            ck('Red flags first' in h and '7.1 Former petrol station next door' in h, "red flags first, numbered")
            # AMENDED FOR V162: the one list's count says the analyses on as well
            ck(re.search(r'class="a3d-anzcount">\d+ findings, 2 red flags( \u00b7 \d+ on)?<', h) is not None, "the count says the red flags (%s)" % re.findall(r'a3d-anzcount">([^<]*)<', h))
            ck('Property_1, 600 m' in h, "the boundary: the property and its area")
            ck(await safe("()=>document.querySelector('.a3d-sa-wrap [data-sacat=\"risk\"]').classList.contains('open')"), "a category opens with a click")
            await safe("""(i)=>{var e=document.querySelector('.a3d-sa-wrap [data-saff="'+i+':title"]');e.value='Former filling station next door';e.dispatchEvent(new Event('change',{bubbles:true}));}""", a)
            await page.wait_for_timeout(120)
            ck((await fnd(fid=a))['title'] == 'Former filling station next door', "a field typed in the panel is kept")
            await safe("""(i)=>{var e=document.querySelector('.a3d-sa-wrap [data-saff="'+i+':cls"]');e.value='constraint';e.dispatchEvent(new Event('change',{bubbles:true}));}""", a)
            await page.wait_for_timeout(120)
            h = await panel() or ''
            ck((await fnd(fid=a))['cls'] == 'constraint' and '7.1 Former filling' not in h.split('The ten categories')[0], "classed down: no longer a red flag")
            await safe("()=>{var b=document.querySelector('.a3d-sa-wrap [data-sachk=\"risk:d:0\"]');b.click();}")
            await page.wait_for_timeout(120)
            ck((await sa())['checks'].get('risk:d:0') is True, "a checklist box ticked in the panel")
            await safe("()=>{var b=document.querySelector('.a3d-sa-wrap [data-sastage=\"4\"]');b.click();}")
            await page.wait_for_timeout(120)
            ck((await sa())['stage'] == 4 and 'data-sastage="4" aria-pressed="true"' in (await panel() or ''), "a stage pressed in the panel")
            await safe("()=>{var b=document.querySelector('.a3d-sa-wrap [data-saact=\"add:water\"]');b.click();}")
            await page.wait_for_timeout(120)
            S = await sa()
            ck(any(f['cat'] == 'water' and f['title'] == 'New finding' for f in S['findings']) and 'data-saff=' in (await panel() or ''),
               "Add finding in Water: a new one, open to edit")
            # a reload
            before = await sa()
            await page.wait_for_timeout(700)
            await within(page.reload(), 'reload')
            await page.wait_for_timeout(2300)
            after = await sa()
            ck(after.get('findings') == before.get('findings') and after.get('checks') == before.get('checks') and after.get('stage') == 4 and after.get('ptype') == 'Mixed use',
               "a reload keeps it all: findings, photograph, checklists, stage, project")

            # ---------------------------------------------------------------------------------
            print("\n-- 7. analysis and data in Layers")
            await safe("()=>{document.querySelector('#a3d-rail [data-tab=\"layers\"]').click();}")
            await page.wait_for_timeout(200)
            ck(await safe("()=>window.__a3dLySecVisible('analysis')") is None and 'Nothing in Analysis yet' in await toast(), "an empty group's eye says there is nothing in it")
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dSetPropTab('site');window.__a3dRefreshProps();}")
            await set_field('[data-propmodel="suntz"]', '-5')
            await safe("()=>{window.__a3dColumnAt([0,0],0,6,6,15);window.__a3dSunHours({margin:25,cell:1});}")
            await page.wait_for_timeout(200)
            rid = await safe("()=>window.__a3dResultLayerAdd('sunhours')")
            dad = await safe("()=>window.__a3dDataAdd('https://data.example.org/zoning.geojson','Zoning','#aa3377')") or {}
            await page.wait_for_timeout(400)
            await safe("()=>{window.__a3dLayerNew({name:'Context',color:'#9aa3ad'});}")
            await page.wait_for_timeout(200)
            G = await safe("""()=>{var out={};[].forEach.call(document.querySelectorAll('.a3d-lysec'),function(s){var h=s.querySelector('.a3d-lysechd'),
                e=h.querySelector('[data-lysecon]'),r=e.getBoundingClientRect();
                out[s.getAttribute('data-lysec')]={car:!!h.querySelector('[data-lysectog]'),sw:!!h.querySelector('.a3d-lygsw'),name:h.querySelector('.a3d-lynm').textContent,
                  cnt:h.querySelector('.a3d-lycnt').textContent,eye:Math.round(r.left),kid:(function(){var k=s.querySelector('[data-lyres] [data-lyreson]');return k?Math.round(k.getBoundingClientRect().left):null;})()};});
              var l=document.querySelector('.a3d-lyrow [data-lyon]');out.layerEye=l?Math.round(l.getBoundingClientRect().left):null;
              var lr=document.querySelectorAll('.a3d-lylist .a3d-lyrow'),last=lr[lr.length-1].getBoundingClientRect(),a=document.querySelector('.a3d-lysec .a3d-lysechd').getBoundingClientRect();
              out.gap=Math.round(a.top-last.bottom);return out;}""") or {}
            ck(rid and dad.get('id') and G.get('analysis', {}).get('car') and G['analysis']['sw'] and G['analysis']['name'] == 'Analysis' and G['analysis']['cnt'] == '1' and
               G.get('data', {}).get('name') == 'Data' and G['data']['cnt'] == '1', "Analysis and Data: rows like a layer's, a caret, a swatch, a name and a count (%s)" % G)
            ck(G.get('layerEye') is not None and G['analysis']['eye'] == G['layerEye'] and G['data']['eye'] == G['layerEye'] and
               G['analysis']['kid'] == G['layerEye'] and G['data']['kid'] == G['layerEye'], "every eye in one column: the layers', the groups' and their layers'")
            ck(G.get('gap') is not None and G['gap'] <= 6, "the groups right under the layers, no gap between (%s px)" % G.get('gap'))
            await safe("()=>{document.querySelector('.a3d-lysec[data-lysec=\"analysis\"] [data-lysecon]').click();}")
            await page.wait_for_timeout(150)
            ck(await safe("()=>window.__a3dLySecHidden('analysis')") is True and await safe("()=>document.querySelector('.a3d-lysec[data-lysec=\"analysis\"]').classList.contains('dim')"),
               "Analysis's eye hides its layers, and the group dims")
            ck(await safe("()=>window.__a3dLySecHidden('data')") is False, "Data is left as it was")
            await safe("()=>{document.querySelector('.a3d-lysec[data-lysec=\"analysis\"] [data-lysecon]').click();}")
            await page.wait_for_timeout(100)
            ck(await safe("()=>window.__a3dLySecHidden('analysis')") is False, "pressed again, shown")
            await safe("()=>window.__a3dLySecVisible('data',false)")
            ck(await safe("()=>window.__a3dDataLayers()[0].visible") is False, "Data's eye hides the data layers")
            await safe("()=>window.__a3dUndo()")
            ck(await safe("()=>window.__a3dDataLayers()[0].visible") is True, "one undo shows them again")
            ck(not errs, "no page errors (%s)" % errs[:3])
            await ctx.close()

            # a phone
            ctx2 = await browser.new_context(viewport={'width': 390, 'height': 844}, has_touch=True, is_mobile=True)
            p2 = await ctx2.new_page()
            await within(p2.goto('file://' + str(HTML)), 'goto')
            await p2.wait_for_timeout(1800)
            await within(p2.evaluate("()=>{window.__a3dEnter();}"), 'enter')
            await p2.wait_for_timeout(300)
            await within(p2.evaluate("()=>{document.querySelector('#a3d-rail .a3d-railbtn[data-tab=\"analyze\"]').click();}"), 'tab')   # AMENDED FOR V159: in Analyze
            await p2.wait_for_timeout(300)
            # AMENDED FOR V162: no view to choose: the site analysis is in Analyze's one list
            await p2.wait_for_timeout(300)
            g = await within(p2.evaluate("""()=>{var w=document.querySelector('.a3d-sa');if(!w)return null;var r=w.getBoundingClientRect(),
              b=document.querySelector('.a3d-sa [data-saact="fill"]').getBoundingClientRect(),s=document.querySelector('.a3d-sa select').getBoundingClientRect();
              return {w:r.width,left:r.left,right:r.right,sw:w.scrollWidth,cw:w.clientWidth,bh:b.height,sh:s.height,
                fs:parseFloat(getComputedStyle(document.querySelector('.a3d-sa select')).fontSize),vw:innerWidth};}"""), 'geom')
            ck(g and g['right'] <= g['vw'] + 0.5 and g['sw'] <= g['cw'] + 1, "on a phone: the panel fits the screen, nothing scrolls sideways (%s)" % g)
            ck(g and g['bh'] >= 34 and g['sh'] >= 36 and g['fs'] >= 16, "touch-sized buttons and fields, 16 px text so the phone does not zoom")
            await ctx2.close()
        except Stalled as e:
            ck(False, "the harness stalled: %s" % e)
        except Exception:
            traceback.print_exc()
            ck(False, "the harness raised")
        await browser.close()

    print("\n%d/%d checks passed" % (ck.n - len(ck.bad), ck.n))
    if ck.bad:
        for b in ck.bad:
            print("  FAILED: " + b)
        print("RESULT: FAIL")
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == '__main__':
    sys.exit(asyncio.run(run()))
