#!/usr/bin/env python3
"""bim_phase131_usages_browser_tests.py -- V131: usages and live areas.

The first of Giraffe's ideas the owner chose (reference/research-giraffe.md, research-usages.md):
a usage is a set of assumptions -- colour, GBA->GFA and GFA->NSA ratios, a floor-to-floor height,
parameters and formulas -- given to a room, a floor or a mass.

  1. THE LIBRARY: five usages to start, kept with the project's types.
  2. FORMULAS: our own reader -- precedence, the power, the functions, names; every mistake said in
     words; no JavaScript.
  3. A MASS is stacked into floors and each floor sliced: a box, a tapered cone, a tube's hole.
  4. A FLOOR is one floor of gross; a ROOM is net, measured; a wall takes no usage.
  5. THE AREAS BY USAGE: the project's and the selection's, in Properties.
  6. THE USAGE PAGE: set, with its areas and formulas; one undo; several at once; Mixed.
  7. EDITING: ratios, refusals, parameters and formulas, an unknown name, removal and its undo.
  8. THE SCHEDULE, USAGE and USAGES, a mirrored copy, and a reload.

The harness never waits without a bound (V123).
"""
import asyncio, pathlib, sys, traceback
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
STALL = 60


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
        ctx = await browser.new_context(viewport={'width': 1600, 'height': 950})
        page = await ctx.new_page()

        def guard(obj, names):
            for nm in names:
                def make(f, nm):
                    async def g(*a, **k):
                        return await within(f(*a, **k), '%s %s' % (nm, str(a[:1])[:40]))
                    return g
                setattr(obj, nm, make(getattr(obj, nm), nm))
        guard(page.keyboard, ('type', 'press', 'down', 'up'))
        guard(page.mouse, ('move', 'down', 'up', 'click', 'dblclick'))
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
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

        has = await safe("()=>!!window.__acad3dV131")
        ck(bool(has), "__acad3dV131 marker is present")
        if not has:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.bad), ck.n))
            await browser.close()
            return 1

        async def blur():
            await safe("()=>{if(document.activeElement&&document.activeElement.blur)document.activeElement.blur();}")
            await page.wait_for_timeout(60)

        async def close_all():
            for _ in range(3):
                await page.keyboard.press('Escape')
                await page.wait_for_timeout(80)
            await safe("()=>{window.closePalette&&window.closePalette();var p=document.getElementById('a3d-rupop');if(p)p.classList.remove('open');}")

        import math
        SC = 0.35   # SCALE: a primitive's parameters are multiplied by it

        def near(a, b, tol=1e-6):
            return a is not None and b is not None and abs(a - b) <= tol

        async def toast():
            return await safe("()=>{var t=document.getElementById('a3d-toast');return t?t.textContent:'';}") or ''

        async def measure(oid):
            return await safe("(i)=>window.__a3dUsageMeasure(i)", oid)

        async def fresh():
            await safe("()=>{window.__a3dTestSetObjs([]);window.__a3dSelectFor([]);}")
            await page.wait_for_timeout(80)

        async def box(L, W, H):
            return await safe("(a)=>window.__a3dAdd('box',{Length:a[0],Width:a[1],Height:a[2]}).id", [L, W, H])

        async def props_html():
            return await safe("()=>document.getElementById('a3d-propsbody').innerHTML") or ''

        async def set_field(sel, val):
            ok = await safe("""(a)=>{var e=document.querySelector('#a3d-propsbody '+a[0]);if(!e)return false;
              e.value=a[1];e.dispatchEvent(new Event('change',{bubbles:true}));return true;}""", [sel, val])
            await page.wait_for_timeout(150)
            return ok

        async def click_act(act):
            ok = await safe("(a)=>{var e=document.querySelector('#a3d-propsbody [data-propusageact=\"'+a+'\"]');if(!e)return false;e.click();return true;}", act)
            await page.wait_for_timeout(150)
            return ok

        try:
            # ---------------------------------------------------------------------------------
            print("\n-- 1. the library, kept with the project's types")
            lib = await safe("()=>window.__a3dUsages()") or []
            ck([u['name'] for u in lib] == ['Residential', 'Office', 'Retail', 'Hotel', 'Parking'],
               "five usages to start with (%s)" % [u['name'] for u in lib])
            res = lib[0] if lib else {}
            ck(near(res.get('gfa'), 0.9) and near(res.get('nsa'), 0.8) and near(res.get('ftf'), 3.1)
               and res.get('params') == [{'key': 'unitSize', 'value': 75}] and res.get('formulas') == [{'key': 'units', 'expr': 'floor(NSA / unitSize)'}],
               "Residential: GFA 90%, NSA 80%, 3.1 m floors, a unit size and a units formula")
            ck(await safe("()=>window.__a3dTypesOf('usage').length") == 5, "they are the types library's 'usage' list, saved with it")

            # ---------------------------------------------------------------------------------
            print("\n-- 2. formulas: our own reader")
            cases = [('2+3*4^2', 50), ('(2+3)*4', 20), ('-2^2', -4), ('2^3^2', 512), ('10/4', 2.5), ('min(3, 1+1)', 2),
                     ('max(1,2,7)', 7), ('round(2.5)', 3), ('floor(7.9)+ceil(0.1)', 8), ('sqrt(16)+abs(-1)', 5), ('1.5e2', 150), ('.5*4', 2)]
            got = [await safe("(s)=>window.__a3dExpr(s)", c[0]) for c in cases]
            bad = [(c[0], g) for c, g in zip(cases, got) if not (g and 'value' in g and near(g['value'], c[1], 1e-9))]
            ck(not bad, "arithmetic, precedence, the power's right reach and the functions (%d cases; wrong: %s)" % (len(cases), bad))
            v = await safe("()=>window.__a3dExpr('GFA * rate + Units', {gfa:100, rate:2, units:5})")
            ck(v and near(v.get('value'), 205), "names read from the variables, in any case (%s)" % v)
            errs_ = {'foo*2': 'unknown name foo', '1/0': 'divides by zero', '(1+2': 'a bracket is not closed',
                     '3 $ 4': 'cannot read "$"', 'bar(2)': 'unknown function bar', '': 'empty', '2 3': 'unexpected "3"', 'min()': 'min needs a value'}
            wrong = []
            for src, msg in errs_.items():
                r = await safe("(s)=>window.__a3dExpr(s)", src)
                if not (r and r.get('error') == msg):
                    wrong.append((src, r))
            ck(not wrong, "and each mistake is said in words (%s)" % wrong)
            ck(await safe("()=>{try{window.__a3dExpr('alert(1)');return window.__a3dExpr('constructor').error;}catch(e){return 'threw';}}") == 'unknown name constructor',
               "it reads no JavaScript: no functions but its own, no names but the variables")

            # ---------------------------------------------------------------------------------
            print("\n-- 3. a mass, stacked into floors and sliced")
            await fresh()
            bx = await box(20, 15, 31)
            await safe("(i)=>window.__a3dUsageAssign([i],'use-res')", bx)
            m = await measure(bx)
            L, W, H = 20 * SC, 15 * SC, 31 * SC
            n = int(math.floor(H / 3.1 + 1e-6))
            gba = n * L * W
            ck(m and m['kind'] == 'mass' and m['levels'] == n and near(m['height'], H, 1e-9),
               "a %.2f m box at 3.1 m floors is %d floors (%s)" % (H, n, m and m['levels']))
            ck(m and near(m['GBA'], gba, 1e-6) and near(m['GFA'], gba * 0.9, 1e-6) and near(m['NSA'], gba * 0.9 * 0.8, 1e-6),
               "GBA %.4f, GFA 90%% of it, NSA 80%% of that (%s)" % (gba, m and (m['GBA'], m['GFA'], m['NSA'])))
            ck(m and m['values'] == {'units': math.floor(gba * 0.72 / 75)} and m['errors'] == {},
               "and units = floor(NSA / 75) = %d (%s)" % (math.floor(gba * 0.72 / 75), m and m['values']))
            await safe("(i)=>window.__a3dUsageAssign([i],'use-ret')", bx)
            m = await measure(bx)
            n2 = int(math.floor(H / 4.5 + 1e-6))
            ck(m and m['levels'] == n2 and near(m['GBA'], n2 * L * W, 1e-6) and near(m['NSA'], n2 * L * W * 0.95 * 0.9, 1e-6),
               "as Retail, 4.5 m floors: %d, with Retail's ratios" % n2)
            cn = await safe("()=>window.__a3dAdd('cone',{Radius1:2,Radius2:4,Height:10}).id")
            bnd = await safe("(i)=>window.__a3dWorldBounds([i])", cn)
            ymid = (bnd['mn'][1] + bnd['mx'][1]) / 2 if bnd else 0
            r = (2 + 4) / 2 * SC
            poly = 10 * r * r * math.sin(2 * math.pi / 20)
            sl = await safe("(a)=>window.__a3dSliceArea(a[0],a[1])", [cn, ymid])
            ck(near(sl, poly, 1e-6), "a cone sliced half way up is its 20-gon at the mean radius: %.6f (%s)" % (poly, sl))
            await safe("(i)=>window.__a3dUsageAssign([i],'use-off')", cn)
            mc = await measure(cn)
            hc = 10 * SC
            nc = max(1, int(math.floor(hc / 3.6 + 1e-6)))   # a mass shorter than a floor is one floor
            exp = 0
            for k in range(nc):
                y0 = k * 3.6
                band = min(3.6, hc - y0)
                rr = 2 * SC + (4 * SC - 2 * SC) * ((y0 + band / 2) / hc)
                exp += 10 * rr * rr * math.sin(2 * math.pi / 20)
            ck(mc and mc['levels'] == nc and near(mc['GBA'], exp, 1e-6),
               "a tapered mass: each floor measured at its own height, %d floors, GBA %.6f (%s)" % (nc, exp, mc and mc['GBA']))
            tb = await safe("()=>window.__a3dAdd('tube',{OuterRadius:5,InnerRadius:2,Height:10}).id")
            tbb = await safe("(i)=>window.__a3dWorldBounds([i])", tb)
            ann = 10 * math.sin(2 * math.pi / 20) * ((5 * SC) ** 2 - (2 * SC) ** 2)
            sl2 = await safe("(a)=>window.__a3dSliceArea(a[0],a[1])", [tb, (tbb['mn'][1] + tbb['mx'][1]) / 2])
            ck(near(sl2, ann, 1e-6), "a tube's hole is not floor: the slice is the ring, %.6f (%s)" % (ann, sl2))
            ck(await safe("(a)=>window.__a3dSliceArea(a[0],a[1])", [tb, tbb['mx'][1] + 1]) == 0, "and above it there is nothing")

            # ---------------------------------------------------------------------------------
            print("\n-- 4. a floor is one floor of gross; a room is net, measured")
            await fresh()
            fl = await safe("()=>window.__a3dFloorAt([[0,0],[12,0],[12,8],[0,8]],0,0.2)")
            await safe("(i)=>window.__a3dUsageAssign([i],'use-off')", fl)
            mf = await measure(fl)
            ck(mf and mf['kind'] == 'floor' and mf['levels'] == 1 and near(mf['GBA'], 96) and near(mf['GFA'], 86.4) and near(mf['NSA'], 86.4 * 0.85),
               "a 12 x 8 Office slab: GBA 96, GFA 86.4, NSA 73.44 (%s)" % str(mf and (mf['GBA'], mf['GFA'], mf['NSA'])))
            await safe("""()=>{var o=window.__a3dState().objs;o.push({id:'RM1',t:'room',name:'Room_1',col:'#7fd4c4',pos:[0,0,0],
              pts:[[20,0],[26,0],[26,5],[20,5]],y:0,area:30,levelId:'lvl-0',layer:'layer-0'});window.__a3dTestSetObjs(o);}""")
            await safe("()=>window.__a3dUsageAssign(['RM1'],'use-res')")
            mr = await measure('RM1')
            ck(mr and mr['kind'] == 'room' and near(mr['NSA'], 30) and mr['GBA'] == 0 and mr['GFA'] == 0 and mr['netMeasured'],
               "a 30 m2 room: NSA 30, measured; no gross invented (%s)" % str(mr and (mr['GBA'], mr['NSA'])))
            ck(mr and mr['values'] == {'units': 0}, "its formula reads the room's NSA: floor(30 / 75) = 0")
            wall = await safe("()=>window.__a3dWall([[0,20],[5,20]],0.2,3,'center',false)")
            ck(await safe("(i)=>window.__a3dUsageAssign([i],'use-res')", wall) == 0 and await safe("(i)=>window.__a3dUsageOf(i)", wall) is None,
               "a wall cannot take a usage, and says so (%r)" % await toast())

            # ---------------------------------------------------------------------------------
            print("\n-- 5. the areas by usage")
            s = await safe("()=>window.__a3dUsageSummary(null)")
            names = [g['name'] for g in s['rows']] if s else []
            ck(names == ['Residential', 'Office'], "the project's areas, by usage, in the library's order (%s)" % names)
            ro = s['rows'][1] if s and len(s['rows']) > 1 else {}
            rr_ = s['rows'][0] if s and s['rows'] else {}
            ck(ro.get('count') == 1 and near(ro.get('GBA'), 96) and rr_.get('count') == 1 and near(rr_.get('NSA'), 30),
               "each with its count and its areas")
            ck(near(s['total']['GBA'], 96) and near(s['total']['NSA'], 30 + 73.44, 1e-6), "and the totals (%s)" % (s and s['total']))
            s2 = await safe("()=>window.__a3dUsageSummary(['RM1'])")
            ck(s2 and [g['name'] for g in s2['rows']] == ['Residential'], "the selection's areas: only what is selected")
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dRefreshProps();}")
            await page.wait_for_timeout(200)
            h = await props_html()
            ck('data-a3dpgrp="Areas by Usage"' in h and 'Residential' in h and 'GBA 96' in h,
               "with nothing selected, Properties shows the project's Areas by Usage")

            # ---------------------------------------------------------------------------------
            print("\n-- 6. the Usage page")
            await safe("(i)=>{window.__a3dSelectFor([i]);window.__a3dRefreshProps();}", fl)
            await page.wait_for_timeout(200)
            sel = await safe("()=>{var s=document.querySelector('#a3d-propsbody [data-propusage=\"set\"]');return s?{v:s.value,opts:[...s.options].map(o=>o.text)}:null;}")
            ck(sel and sel['v'] == 'use-off' and sel['opts'][:2] == ['None', 'Residential'],
               "a floor's Properties has a Usage, set to Office (%s)" % sel)
            h = await props_html()
            ck('GBA' in h and '96 m' in h and '(90% of GBA)' in h and '(85% of GFA)' in h, "with its GBA, GFA and NSA, and the ratios that made them")
            await set_field('[data-propusage="set"]', 'use-ret')
            await set_field('[data-propusage="set"]', 'use-res')
            ck(await safe("(i)=>window.__a3dUsageOf(i)", fl) == 'use-res' and 'Residential given to 1 object' in await toast(),
               "choosing Residential gives it Residential (%r)" % await toast())
            h = await props_html()
            ck('>units<' in h, "and its formulas show: units, floor(69.12 / 75) = 0")
            await safe("()=>window.__a3dUndo()")
            await page.wait_for_timeout(200)
            ck(await safe("(i)=>window.__a3dUsageOf(i)", fl) == 'use-ret', "Undo takes back that one choice: Retail, the one before")
            await safe("(i)=>window.__a3dUsageAssign([i],'use-off')", fl)
            b1 = await box(10, 10, 20)
            b2 = await box(10, 10, 20)
            await safe("(a)=>{window.__a3dSelectFor(a);window.__a3dRefreshProps();}", [b1, b2])
            await page.wait_for_timeout(200)
            h = await props_html()
            ck('Usage (2 selected)' in h, "two masses selected: one Usage for both")
            await set_field('[data-propusage="set"]', 'use-hot')
            ck(await safe("(a)=>a.map(window.__a3dUsageOf)", [b1, b2]) == ['use-hot', 'use-hot'], "given to both at once")
            h = await props_html()
            ck('data-a3dpgrp="Areas: the Selection"' in h and 'Hotel' in h, "and the selection's areas follow")
            await safe("(i)=>window.__a3dUsageAssign([i],'use-res')", b2)
            await safe("(a)=>{window.__a3dSelectFor(a);window.__a3dRefreshProps();}", [b1, b2])
            await page.wait_for_timeout(200)
            ck(await safe("()=>{var s=document.querySelector('#a3d-propsbody [data-propusage=\"set\"]');return s?s.options[s.selectedIndex].text:null;}") == 'Mixed',
               "two different usages read Mixed")

            # ---------------------------------------------------------------------------------
            print("\n-- 7. editing the usages")
            await safe("()=>window.__a3dRunCmd('usages')")
            await page.wait_for_timeout(250)
            ck(await safe("()=>window.__a3dState().sel") is None and 'data-a3dpgrp="Usages"' in await props_html(),
               "USAGES opens the library in Properties, with nothing selected")
            ck(await click_act('open:use-off'), "Edit opens a usage's fields")
            await set_field('[data-propusage="u:use-off:nsa"]', '50')
            mf2 = await measure(fl)
            ck(near(mf2['NSA'], 86.4 * 0.5, 1e-9), "GFA to NSA set to 50%%: the Office slab's NSA follows, %.4f (%s)" % (86.4 * 0.5, mf2['NSA']))
            await set_field('[data-propusage="u:use-off:nsa"]', '150')
            ck(near((await safe("()=>window.__a3dUsages()"))[1]['nsa'], 0.5) and 'from 0 to 100' in await toast(),
               "150%% is refused, and says why (%r)" % await toast())
            await set_field('[data-propusage="u:use-off:name"]', 'retail')
            ck((await safe("()=>window.__a3dUsages()"))[1]['name'] == 'Office' and 'already a usage called' in await toast(),
               "a name another usage has is refused")
            await set_field('[data-propusage="u:use-off:ftf"]', '4')
            ck(near((await safe("()=>window.__a3dUsages()"))[1]['ftf'], 4), "the floor-to-floor height is set")
            await click_act('padd:use-off')
            await click_act('fadd:use-off')
            off = (await safe("()=>window.__a3dUsages()"))[1]
            ck(off['params'] == [{'key': 'rate', 'value': 0}] and off['formulas'] == [{'key': 'value', 'expr': 'GFA'}],
               "Add parameter and Add formula give a named, working start (%s, %s)" % (off['params'], off['formulas']))
            await set_field('[data-propusage="p:use-off:0:value"]', '1200')
            await set_field('[data-propusage="f:use-off:0:expr"]', 'NSA * rate')
            mf3 = await measure(fl)
            ck(near(mf3['values'].get('value'), 86.4 * 0.5 * 1200, 1e-6), "value = NSA * rate reads the parameter (%s)" % mf3['values'])
            await click_act('fadd:use-off')
            await set_field('[data-propusage="f:use-off:1:expr"]', 'value * 2')
            mf4 = await measure(fl)
            ck(near(mf4['values'].get('value2'), 2 * mf4['values'].get('value', 0), 1e-6) and mf4['values'].get('value', 0) > 0,
               "a formula reads the formulas before it: value2 = value * 2 (%s)" % mf4['values'])
            await click_act('fdel:use-off:1')
            await set_field('[data-propusage="f:use-off:0:expr"]', 'NSA * price')
            h = await props_html()
            ck('unknown name price' in h, "a formula that reads an unknown name says so where it is written")
            await set_field('[data-propusage="p:use-off:0:key"]', 'GFA')
            ck('one of the areas' in await toast(), "a parameter cannot take an area's name (%r)" % await toast())
            await safe("(i)=>window.__a3dUsageAssign([i],'use-off')", fl)
            await set_field('[data-propusage="u:use-off:ftf"]', '4.5')
            await click_act('udel:use-off')
            ck('use-off' not in [u['id'] for u in await safe("()=>window.__a3dUsages()")] and await safe("(i)=>window.__a3dUsageOf(i)", fl) is None,
               "Remove usage takes it away, and its objects have no usage (%r)" % await toast())
            await safe("()=>window.__a3dUndo()")
            await page.wait_for_timeout(200)
            back = [u for u in await safe("()=>window.__a3dUsages()") if u['id'] == 'use-off']
            ck(back and near(back[0]['ftf'], 4.5) and await safe("(i)=>window.__a3dUsageOf(i)", fl) == 'use-off',
               "and Undo brings both back, in one step: as they were just before (4.5 m)")
            nid = await safe("()=>window.__a3dUsageAdd('Office')")
            ck(nid and (await safe("()=>window.__a3dUsages()"))[-1]['name'] == 'Office 2', "Add usage names it so it is not a twin (Office 2)")

            # ---------------------------------------------------------------------------------
            print("\n-- 8. the schedule, the commands, a copy and a reload")
            rows = (await safe("()=>window.__a3dScheduleRows('usage')") or {}).get('rows') or []
            tot = [r for r in rows if r.get('level') == 'All levels']
            ck(rows and tot and all('gba' in r and 'nsa' in r for r in rows), "Areas by Usage is a schedule (%d rows)" % len(rows))
            hot = [r for r in tot if r['usage'] == 'Hotel']
            ck(hot and 'keys' in hot[0]['values'], "a usage's total row carries its formulas' sums (%s)" % (hot and hot[0]['values']))
            await safe("(i)=>{window.__a3dSelectFor([i]);window.__a3dRefreshProps();}", b1)
            await safe("()=>window.__a3dRunCmd('usage')")
            await page.wait_for_timeout(200)
            ck(await safe("()=>document.activeElement&&document.activeElement.getAttribute('data-propusage')") == 'set',
               "USAGE with a mass selected puts the keyboard on its Usage")
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dRefreshProps();}")
            await safe("()=>window.__a3dRunCmd('usage')")
            await page.wait_for_timeout(200)
            ck('Select a room, a floor or a mass' in await toast() and 'data-a3dpgrp="Usages"' in await props_html(),
               "USAGE with nothing selected says what it needs and shows the usages")
            cat = await safe("()=>window.__a3dCommandCatalog().filter(c=>c.name==='USAGE'||c.name==='USAGES').map(c=>({n:c.name,act:c.act,where:c.where}))")
            ck(cat and len(cat) == 2 and any('Room & Area' in w for c in cat for w in c['where']) and any('Program' in w for c in cat for w in c['where']),
               "both are on the ribbon and in the search, where they live (%s)" % cat)
            await safe("(i)=>window.__a3dMirrorSelection([i],[0,-50],[1,-50])", b1)
            await page.wait_for_timeout(150)
            cp = await safe("()=>{var s=window.__a3dState();return s.sel;}")
            ck(cp and cp != b1 and await safe("(i)=>window.__a3dUsageOf(i)", cp) == 'use-hot', "a mirrored copy keeps its usage")
            before = await safe("()=>window.__a3dUsages().map(u=>u.name)")
            await page.wait_for_timeout(500)
            await within(page.reload(), 'reload')
            await page.wait_for_timeout(2300)
            ck(await safe("()=>window.__a3dUsages().map(u=>u.name)") == before and await safe("(i)=>window.__a3dUsageOf(i)", fl) == 'use-off',
               "the usages and who has them outlive a reload")
            ck(not errs, "no page errors (%s)" % errs[:3])
        except Stalled as e:
            ck(False, "the suite ran to the end (stalled at %s)" % e)
        except Exception as e:
            traceback.print_exc()
            ck(False, "the suite ran to the end (stopped by %s: %s)" % (type(e).__name__, str(e)[:160]))

        print("")
        await browser.close()
    print("%d/%d checks passed" % (ck.n - len(ck.bad), ck.n))
    if ck.bad:
        for b in ck.bad:
            print("  FAILED: " + b)
        print("RESULT: FAIL")
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == '__main__':
    sys.exit(asyncio.run(run()))
