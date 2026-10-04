#!/usr/bin/env python3
"""bim_phase106_tributary_loads_browser_tests.py -- V106: tributary areas and the column load takedown.

Asserted on the model against hand values:
  1. LEVEL LOADS are typed into Properties (nothing selected: the model and its active level) --
     driven -- rejected when negative, undoable, and kept through a reload.
  2. TRIBUTARY AREAS on a 3 x 3 grid at 6 m under a slab overhanging 0.5 m are the half-bay rule:
     interior 36, edge 21, corner 12.25 m2, adding up to the slab's 169 m2. A roof is carried by its
     plan footprint. Grid marks read "B-2".
  3. THE TAKEDOWN over two storeys: an interior ground column carries 180 + 144 = 324 kN dead and
     86.4 + 36 = 122.4 kN live; 1.2D + 1.6L = 584.64 kN. Each upper column stands on the lower one.
  4. OFF THE GRID the cells are true bisector cells: columns at (0,0) and (4,2) under a 6 x 3 slab
     take 5.25 and 12.75 m2 (the line x = 2.5 - z/2), which no axis-aligned split gives.
  5. HONEST GAPS: a level with no load leaves the totals that need it blank and says why; a column
     in the same place as another takes nothing and says so; a slab no column reaches is reported
     unsupported.
  6. TRIBAREA from the command palette draws exactly the cells the schedule reports for the slab on
     the active level, and hides them again.
"""
import asyncio, pathlib, sys
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
        print(('ok    ' if cond else 'FAIL  ') + msg)


def near(a, b, tol=1e-6):
    return isinstance(a, (int, float)) and not isinstance(a, bool) and abs(a - b) <= tol


async def palette_run(page, name):
    await page.keyboard.press('Control+k')
    await page.wait_for_timeout(320)
    await page.keyboard.type(name)
    await page.wait_for_timeout(260)
    await page.keyboard.press('Enter')
    await page.wait_for_timeout(420)


async def run():
    ck = Checks()
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1600, 'height': 950})
        page = await ctx.new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        await page.goto('file://' + str(HTML))
        await page.wait_for_timeout(2300)
        await page.mouse.click(800, 500)
        await page.wait_for_timeout(250)

        async def safe(js, arg=None):
            try:
                return await (page.evaluate(js, arg) if arg is not None else page.evaluate(js))
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:140])
                return None

        async def blur():
            await safe("()=>{if(document.activeElement)document.activeElement.blur();}")

        async def show_level(lid):
            await safe("(i)=>{window.__a3dSetLevel(i);window.__a3dSelectFor([]);window.__a3dRefreshProps();}", lid)
            await page.wait_for_timeout(80)

        async def set_load(lid, f, v):
            await show_level(lid)
            await safe("()=>window.__a3dSetPropTab&&window.__a3dSetPropTab('analysis')")   # AMENDED FOR V141: the field is on Properties' Analysis tab
            try:
                loc = page.locator('input[data-propmodel="%s"]' % f)
                await loc.fill(v, timeout=3000)
                await loc.press('Enter', timeout=3000)
                await page.wait_for_timeout(150)
            except Exception as e:
                print('      (driving the %s field failed: %s)' % (f, str(e)[:120]))

        async def load_val(lid, f):
            await show_level(lid)
            return await safe("(f)=>{var e=document.querySelector('input[data-propmodel='+JSON.stringify(f)+']');return e?e.value:null;}", f)

        async def loads():
            r = (await safe("()=>window.__a3dColumnLoads()")) or {}
            return r.get('rows') or [], {l['levelId']: l for l in (r.get('levels') or [])}

        def row(rows, mark, base):
            for r in rows:
                if r.get('grid') == mark and near(r.get('base'), base, 1e-3):
                    return r
            return {}

        # ---- set-up: three levels, a 3 x 3 grid, two storeys of columns, a floor, a roof, a ground slab
        await safe("()=>{window.__a3dAddLevel();window.__a3dAddLevel();}")
        lv = sorted(((await safe("()=>Array.prototype.map.call(document.querySelectorAll('input[data-lvlf=\"elev\"]'),function(e){return [e.getAttribute('data-lvlid'),parseFloat(e.value)];})")) or []), key=lambda p: p[1])
        ck(len(lv) == 3, 'three levels (%s)' % lv)
        (L0, e0), (L1, e1), (L2, e2) = lv[0], lv[1], lv[2]
        gids = []
        for x in (0, 6, 12):
            gids.append(await safe("([a,b])=>window.__a3dAddGrid(a,b)", [[x, -2], [x, 14]]))
        for z in (0, 6, 12):
            gids.append(await safe("([a,b])=>window.__a3dAddGrid(a,b)", [[-2, z], [14, z]]))
        for gid, nm in zip(gids, ['A', 'B', 'C', '1', '2', '3']):
            await safe("([i,n])=>window.__a3dRenameGrid(i,n)", [gid, nm])
        pts = [(x, z) for x in (0, 6, 12) for z in (0, 6, 12)]
        for lid, y, h in ((L0, e0, e1 - e0), (L1, e1, e2 - e1)):
            await safe("(i)=>window.__a3dSetLevel(i)", lid)
            for x, z in pts:
                await safe("([p,y,h])=>window.__a3dColumnAt(p,y,0.4,0.4,h)", [[x, z], y, h])
        await safe("(i)=>window.__a3dSetLevel(i)", L0)
        await safe("([p,y])=>window.__a3dFloorAt(p,y,0.2)", [[[0, 0], [12, 0], [12, 12], [0, 12]], e0])
        await safe("(i)=>window.__a3dSetLevel(i)", L1)
        await safe("([p,y])=>window.__a3dFloorAt(p,y,0.2)", [[[-0.5, -0.5], [12.5, -0.5], [12.5, 12.5], [-0.5, 12.5]], e1])
        await safe("(i)=>window.__a3dSetLevel(i)", L2)
        await safe("([p,y])=>{window.__a3dBuildRoof({pts:p,roofBaseY:y},10,0,0.2);}", [[[0, 0], [12, 0], [12, 12], [0, 12]], e2])
        await blur()

        print('\n-- 1. level loads typed into Properties')
        for lid, f, v in ((L1, 'dl', '5'), (L1, 'll', '2.4'), (L2, 'dl', '4'), (L2, 'll', '1')):
            await set_load(lid, f, v)
        got = [await load_val(L1, 'dl'), await load_val(L1, 'll'), await load_val(L2, 'dl'), await load_val(L2, 'll')]
        ck(got == ['5', '2.4', '4', '1'], 'dead and live loads typed into Properties are on the levels (%s)' % got)
        await set_load(L1, 'dl', '-3')
        ck((await load_val(L1, 'dl')) == '5', 'a negative load is refused and the field shows the kept value')
        await set_load(L2, 'll', '1.5')
        mid = await load_val(L2, 'll')
        await blur()
        await safe("()=>window.__a3dUndo()")
        await page.wait_for_timeout(150)
        ck(mid == '1.5' and (await load_val(L2, 'll')) == '1', 'a load change is one undo step (%s, then %s)' % (mid, await load_val(L2, 'll')))
        ck('colload' in ((await safe("()=>window.__a3dScheduleKeys()")) or []), 'Column Loads is a schedule')

        print('\n-- 2. tributary areas, the half-bay rule on a grid')
        rows, lvls = await loads()
        low = {r['grid']: r for r in rows if near(r.get('base'), e0, 1e-3)}
        up = {r['grid']: r for r in rows if near(r.get('base'), e1, 1e-3)}
        marks = {'%s-%s' % (a, b) for a in 'ABC' for b in '123'}
        ck(set(low) == marks and set(up) == marks, 'every column has its grid mark, letters first (%s)' % sorted(low)[:3])
        exp1 = {m: (36 if m == 'B-2' else (12.25 if m[0] in 'AC' and m[2] in '13' else 21)) for m in marks}
        exp2 = {m: (36 if m == 'B-2' else (9 if m[0] in 'AC' and m[2] in '13' else 18)) for m in marks}
        ck(all(near(low[m].get('tribArea'), exp1[m]) for m in marks if m in low), 'the overhanging floor: interior 36, edge 21, corner 12.25 m2')
        ck(all(near(up[m].get('tribArea'), exp2[m]) for m in marks if m in up), 'the roof, by its footprint: interior 36, edge 18, corner 9 m2')
        l1, l2, l0 = lvls.get(L1, {}), lvls.get(L2, {}), lvls.get(L0, {})
        ck(near(l1.get('slabArea'), 169) and near(l1.get('onColumns'), 169) and l1.get('columns') == 9 and near(l1.get('unsupported'), 0),
           'the floor adds up: 169 of 169 m2 on 9 columns (%s)' % l1)
        ck(near(l2.get('slabArea'), 144) and near(l2.get('onColumns'), 144), 'the roof adds up: 144 of 144 m2')
        ck(near(l0.get('unsupported'), 144) and l0.get('columns') == 0, 'the ground slab is reported as carried by no column (%s)' % l0)

        print('\n-- 3. the takedown')
        b2, a1, b1 = low.get('B-2', {}), low.get('A-1', {}), low.get('B-1', {})
        ck(near(b2.get('floorD'), 180) and near(b2.get('floorL'), 86.4), 'ground B-2 floor load: 36 m2 x 5 = 180 kN dead, x 2.4 = 86.4 kN live')
        ck(near(b2.get('axialD'), 324) and near(b2.get('axialL'), 122.4), 'ground B-2 axial: 180 + 144 = 324 kN dead, 86.4 + 36 = 122.4 kN live (%s, %s)' % (b2.get('axialD'), b2.get('axialL')))
        ck(near(b2.get('service'), 446.4) and near(b2.get('factored'), 584.64), 'D+L = 446.4 kN, 1.2D + 1.6L = 584.64 kN (%s)' % b2.get('factored'))
        ck(near(a1.get('axialD'), 97.25) and near(a1.get('axialL'), 38.4) and near(b1.get('axialD'), 177) and near(b1.get('axialL'), 68.4),
           'corner A-1: 61.25 + 36 = 97.25 / 29.4 + 9 = 38.4 kN; edge B-1: 105 + 72 = 177 / 50.4 + 18 = 68.4 kN')
        ck(all(up[m].get('carriedBy') == low[m].get('name') for m in marks if m in up and m in low), 'each upper column stands on the one below it')
        ck(near(up.get('B-2', {}).get('axialD'), 144) and b2.get('note', 'x') == '', 'the top storey carries only the roof, and a full column has no note (%r)' % b2.get('note'))

        print('\n-- 4. honest gaps')
        await set_load(L2, 'dl', '')
        await blur()
        rows, lvls = await loads()
        u2, g2 = row(rows, 'B-2', e1), row(rows, 'B-2', e0)
        ck(u2.get('axialD') == '' and 'loads not set on' in u2.get('note', ''), 'no dead load on the roof level: the upper total is blank and says why (%r)' % u2.get('note'))
        ck(near(g2.get('floorD'), 180) and g2.get('axialD') == '' and g2.get('service') == '' and near(g2.get('axialL'), 122.4),
           'the ground column keeps its own floor load but not a total that would be missing the roof')
        await set_load(L2, 'dl', '4')
        await safe("(i)=>window.__a3dSetLevel(i)", L1)
        await safe("([p,y,h])=>window.__a3dColumnAt(p,y,0.4,0.4,h)", [[6, 6], e1, e2 - e1])
        rows, lvls = await loads()
        dup = [r for r in rows if r.get('grid') == 'B-2' and near(r.get('base'), e1, 1e-3)]
        twin = [r for r in dup if 'same place as' in r.get('note', '')]
        ck(len(dup) == 2 and len(twin) == 1 and near(twin[0].get('tribArea'), 0), 'a second column in the same place takes nothing and says so')
        ck(near(lvls.get(L2, {}).get('onColumns'), 144) and near(row(rows, 'B-2', e0).get('axialD'), 324), 'and nothing is counted twice: roof 144 m2, ground B-2 still 324 kN')
        await blur()
        await safe("()=>window.__a3dUndo()")

        print('\n-- 5. TRIBAREA from the command palette')
        await safe("(i)=>window.__a3dSetLevel(i)", L1)
        await blur()
        await palette_run(page, 'TRIBAREA')
        await safe("()=>{window.__a3dSelectFor([]);window.__a3dTestPaint();}")
        shown = (await safe("()=>window.__a3dTribShown()")) or {}
        items = {i['name']: i['area'] for i in shown.get('items') or []}
        want = {low[m]['name']: low[m]['tribArea'] for m in low}
        ck(shown.get('levelId') == L1 and len(items) == 9 and all(near(items.get(k), v) for k, v in want.items()),
           'on Level 1 it draws the nine cells of the columns below, with the schedule areas (%d)' % len(items))
        await palette_run(page, 'TRIBAREA')
        await safe("()=>window.__a3dTestPaint()")
        ck((await safe("()=>window.__a3dTribShown()")) is None, 'run again, it hides them')

        print('\n-- 6. kept through a reload; off the grid')
        await page.wait_for_timeout(1500)
        await page.reload()
        await page.wait_for_timeout(2300)
        rows, lvls = await loads()
        ck((await load_val(L1, 'dl')) == '5' and near(row(rows, 'B-2', e0).get('axialD'), 324), 'loads and the takedown survive a reload')
        await safe("()=>window.__a3dTestSetObjs([])")
        await safe("(i)=>window.__a3dSetLevel(i)", L0)
        for p in ([0, 0], [4, 2]):
            await safe("([p,y,h])=>window.__a3dColumnAt(p,y,0.4,0.4,h)", [p, e0, e1 - e0])
        await safe("(i)=>window.__a3dSetLevel(i)", L1)
        await safe("([p,y])=>window.__a3dFloorAt(p,y,0.2)", [[[0, 0], [6, 0], [6, 3], [0, 3]], e1])
        rows, lvls = await loads()
        byxz = {(round(r['x'], 3), round(r['z'], 3)): r for r in rows}
        ta, tb = byxz.get((0, 0), {}).get('tribArea'), byxz.get((4, 2), {}).get('tribArea')
        ck(near(ta, 5.25) and near(tb, 12.75), 'columns at (0,0) and (4,2) under a 6 x 3 slab take 5.25 and 12.75 m2 (%s, %s)' % (ta, tb))
        ck(not errs, 'no uncaught page errors (%s)' % errs[:2])
        await browser.close()
    print('\n%d/%d checks passed' % (ck.n - len(ck.bad), ck.n))
    print('RESULT: ' + ('PASS' if not ck.bad else 'FAIL'))
    return 0 if not ck.bad else 1


if __name__ == '__main__':
    sys.exit(asyncio.run(run()))
