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
  3-5. AMENDED FOR V164: findings by hand, Define and the checklists, pins and photographs are gone,
     with their hooks; the data's findings are numbered by category.
  6. THE PANEL: categories open, findings read only; a reload keeps them; a phone.
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
            # AMENDED FOR V164: Fill from the model is in Analyze site now; SAFILL is one of its names
            for q, want in (('site analysis', 'SITEANALYSIS'), ('due diligence', None), ('fill site analysis', 'ANALYZESITE')):
                nm = [x['name'] for x in (await safe("(q)=>window.__a3dCommandSearch(q,5)", q) or [])]
                if want:
                    ck(want in nm[:3], "searching %r finds %s (%s)" % (q, want, nm))
            nm = [x['name'] for x in (await safe("(q)=>window.__a3dCommandSearch(q,5)", 'railway') or [])]
            ck('CONTEXT' in nm[:2], "CONTEXT's description names V157's kinds")
            stn = await safe("()=>window.__a3dSaStandard()") or {}
            # AMENDED FOR V164: the owner: remove the checklist entirely; the stages, Define and the checklists are gone
            ck('stages' not in stn, "no stages (%s)" % stn.get('stages'))
            ck([c['id'] for c in stn.get('cats', [])] == CATS and all(set(c) == {'id', 'n'} for c in stn.get('cats', [])),
               "the ten categories in their fixed order, no checklists in them")
            s0 = await sa()
            ck(s0.get('findings') == [] and 'stage' not in s0 and 'pins' not in s0, "a new project: no findings, no stage")
            h = await panel() or ''
            ck(h.count('data-sacat=') == 10 and 'data-sastage=' not in h, "the panel: ten categories, no stage buttons")
            ck('From a shape' in h and 'Analyze site' in h, "no boundary yet: it offers to make one, and Analyze site")

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
            ck('stage' not in S, "no stage to move on")   # AMENDED FOR V164: no stages
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
            # AMENDED FOR V164: findings are the data's: none is classed or written on by hand, so all of a source's go with it
            await safe("()=>window.__a3dRunCmd('contextremove')")
            r = await safe("()=>window.__a3dSaFill()") or {}
            S = await sa()
            keys2 = sorted(f.get('auto') for f in S['findings'])
            ck(r.get('removed') == 8 and 'access.roads' not in keys2 and 'location.place' in keys2 and 'legal.boundary' in keys2,
               "the context removed and refilled: its eight findings go (%s gone), the rest stay" % r.get('removed'))
            ck(all(f.get('auto') for f in S['findings']), "every finding left is one the data wrote")
            await safe("()=>window.__a3dUndo()")
            await safe("()=>window.__a3dUndo()")
            ck(await fnd('access.roads') is not None, "the fill and the removal, one undo step each")

            # ---------------------------------------------------------------------------------
            print("\n-- 3, 4 and 5. findings by hand, Define and checklists, pins and photographs")
            # AMENDED FOR V164: the owner: "i have to input information, which is not the right way ... remove that
            # entirely". Adding and editing findings, the stages, project type and questions, the checklists,
            # pins on the plan and photographs are gone, and so are the hooks that drove them.
            gone = await safe("""()=>['__a3dSaAdd','__a3dSaSet','__a3dSaDel','__a3dSaDefine','__a3dSaCheck','__a3dSaPlace','__a3dSaStartPin','__a3dSaPhotoUrl','__a3dSaPins','__a3dSaEdit']
              .filter(function(k){return typeof window[k]!=='undefined';})""")
            ck(gone == [], "no way left to type a finding, a stage, a checklist, a pin or a photograph in (%s)" % gone)
            # AMENDED FOR V164: every finding's number counted again here, by category in the list's order
            S = await sa()
            exp, seen = {}, {}
            for f in S['findings']:
                if f.get('auto'):
                    seen[f['cat']] = seen.get(f['cat'], 0) + 1
                    exp[f['id']] = '%d.%d' % (CATS.index(f['cat']) + 1, seen[f['cat']])
            got = {i: await safe("(i)=>window.__a3dSaNumber(i)", i) for i in exp}
            lb = [f['id'] for f in S['findings'] if f.get('auto') == 'legal.boundary']
            ck(got == exp and lb and got.get(lb[0]) == '2.1' and len(seen) > 3,
               "the data's findings numbered by category: Location's 1.1 and 1.2, then Legal's 2.1 (%s)" % [got.get(i) for i in list(exp)[:4]])

            # ---------------------------------------------------------------------------------
            print("\n-- 6. the panel")
            h = await panel() or ''
            # AMENDED FOR V164: no red flags typed by hand: the count is the data's findings
            # AMENDED FOR V162: the one list's count says the analyses on as well
            ck(re.search(r'class="a3d-anzcount">\d+ findings( \u00b7 \d+ on)?<', h) is not None, "the count says the findings (%s)" % re.findall(r'a3d-anzcount">([^<]*)<', h))
            ck('Property_1, 600 m' in h, "the boundary: the property and its area")
            # AMENDED FOR V164: a category opens with a click; its findings are to read, not to edit
            await safe("()=>{var b=document.querySelector('.a3d-sa-wrap [data-satog=\"legal\"]');var c=b.closest('[data-sacat]');if(!c.classList.contains('open'))b.click();}")
            await page.wait_for_timeout(120)
            ck(await safe("()=>document.querySelector('.a3d-sa-wrap [data-sacat=\"legal\"]').classList.contains('open')"), "a category opens with a click")
            ck(await safe("()=>{var c=document.querySelector('.a3d-sa-wrap [data-sacat=\"legal\"]');return !!c.querySelector('.a3d-safind')&&!c.querySelector('.a3d-safind input,.a3d-safind select,.a3d-safind textarea,.a3d-safind button,[data-sachk]')&&!/Add finding|At the desk|On site/.test(c.textContent);}") is True,
               "its findings read only: no field, no Add finding, no checklist")
            # a reload
            before = await sa()
            await page.wait_for_timeout(700)
            await within(page.reload(), 'reload')
            await page.wait_for_timeout(2300)
            after = await sa()
            ck(after.get('findings') == before.get('findings') and len(after.get('findings', [])) > 0,
               "a reload keeps the findings")   # AMENDED FOR V164: nothing else is typed to keep

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
            # AMENDED FOR V164: the button is Analyze site, the field the site's address
            g = await within(p2.evaluate("""()=>{var w=document.querySelector('.a3d-sa');if(!w)return null;var r=w.getBoundingClientRect(),
              b=document.querySelector('.a3d-sa [data-saact="analyze"]').getBoundingClientRect(),s=document.querySelector('.a3d-sa [data-saaddr]').getBoundingClientRect();
              return {w:r.width,left:r.left,right:r.right,sw:w.scrollWidth,cw:w.clientWidth,bh:b.height,sh:s.height,
                fs:parseFloat(getComputedStyle(document.querySelector('.a3d-sa [data-saaddr]')).fontSize),vw:innerWidth};}"""), 'geom')
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
