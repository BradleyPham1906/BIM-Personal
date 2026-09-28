#!/usr/bin/env python3
"""bim_phase105_room_colour_occupancy_browser_tests.py -- V105: occupant load and room colour fill.

Asserted on the model, not on appearance:
  1. OCCUPANT LOAD = AREA / FACTOR, ROUNDED UP, with the IBC Table 1004.5 factor converted from the
     published square feet. 100 m2 of Business areas (150 sq ft = 13.935 m2) holds 8 -- the first
     V105 attempt reported 14,286. An exact multiple does not round up on float noise: a 1.1 x 3 m
     room drawn at x = 60 measures 3.3000000000000114 m2 and at 1.1 m2/person holds 3, not 4.
  2. THE OWNER'S FACTOR WINS; blank or unreadable falls back to the default; an occupancy the table
     does not have gives NO load -- blank in the schedule, never 0.
  3. THE SCHEDULE AND PROPERTIES show the same numbers. The panel's Occupancy field, driven by
     typing, changes the model and updates the load row in place without taking the focus.
  4. THE COLOUR FILL IS OFF BY DEFAULT: each room's recorded fill is exactly V104's.
  5. ROOMCOLOR from the command palette goes Department -> Occupancy -> off. Every room's fill is
     its legend entry's colour, equal values (any case) share one, different values do not, a room
     with no value keeps the plain fill, and the legend lists exactly the values drawn.
  6. THE SETTING IS KEPT: it survives a reload; undo reverts it and not the edit before it; a copied
     room keeps every field, Comments included; plan SVG and a sheet viewport carry the colour.
"""
import asyncio, math, pathlib, re, sys
from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'
FT2 = 0.09290304
PLAIN = 'rgba(127,212,196,0.14)'


class Checks:
    def __init__(self):
        self.n, self.bad = 0, []

    def __call__(self, cond, msg):
        self.n += 1
        if not cond:
            self.bad.append(msg)
        print(('ok    ' if cond else 'FAIL  ') + msg)


def occ(area, m2):
    return math.ceil(area / m2 - 1e-9)


def rect(i, x, z, w, d):
    return {'id': 'S%d' % i, 't': 'sketch', 'name': 'S%d' % i, 'col': '#5ec4b8', 'pos': [0, 0, 0],
            'pts': [[x, z], [x + w, z], [x + w, z + d], [x, z + d]], 'y': 0, 'closed': True}


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
        ev = page.evaluate

        async def safe(js, arg=None):
            try:
                return await (ev(js, arg) if arg is not None else ev(js))
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:120])
                return None

        async def blur():
            await safe("()=>{if(document.activeElement)document.activeElement.blur();}")

        async def paint():
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dTestPaint();}")

        async def setf(i, k, v):
            return await safe("([i,k,v])=>window.__a3dSetRoomField(i,k,v)", [i, k, v])

        async def load(i):
            return (await safe("(i)=>window.__a3dRoomLoad(i)", i)) or {}

        async def style(i):
            return (await safe("(i)=>window.__a3dLastRoomStyle(i)", i)) or {}

        async def sched():
            s = (await safe("()=>window.__a3dScheduleRows('room')")) or {'cols': [], 'rows': []}
            return s['cols'], {r.get('number'): r for r in s['rows']}

        # ---- set-up: four rooms of known area, on sketches
        await safe("(o)=>window.__a3dTestSetObjs(o)", [rect(1, 0, 0, 10, 10), rect(2, 20, 0, 8, 5), rect(3, 40, 0, 6, 6), rect(4, 60, 0, 1.1, 3)])
        await safe("()=>{window.__a3dFlat(true);window.__a3dFit();window.__a3dTestPaint();}")
        A = await safe("()=>window.__a3dCreateRoomAt([5,5],0)")
        B = await safe("()=>window.__a3dCreateRoomAt([24,2.5],0)")
        C = await safe("()=>window.__a3dCreateRoomAt([43,3],0)")
        D = await safe("()=>window.__a3dCreateRoomAt([60.75,1],0)")
        ck(all([A, B, C, D]), 'four rooms made on sketches')
        areas = [(await load(r)).get('area') for r in (A, B, C, D)]
        ck(all(a is not None for a in areas) and [round(a, 9) for a in areas] == [100, 40, 36, 3.3], 'room areas are 100, 40, 36 and 3.3 m2 (%s)' % areas)
        for r, n in ((A, 'A'), (B, 'B'), (C, 'C'), (D, 'D')):
            await setf(r, 'number', n)

        print('\n-- 1. occupant load against hand values')
        table = {r['name']: r for r in ((await safe("()=>window.__a3dOccLoads()")) or [])}
        spot = {'Business areas': (150, 'gross'), 'Mercantile': (60, 'gross'), 'Residential': (200, 'gross'),
                'Warehouses': (500, 'gross'), 'Industrial areas': (100, 'gross'), 'Parking garages': (200, 'gross'),
                'Educational - classroom area': (20, 'net'), 'Assembly without fixed seats - concentrated': (7, 'net'),
                'Assembly without fixed seats - unconcentrated': (15, 'net'), 'Assembly without fixed seats - standing space': (5, 'net')}
        ck(len(table) == 36, 'the IBC table has its 36 area-rate rows (%d)' % len(table))
        ck(all(table.get(k, {}).get('ft2') == v[0] and table[k].get('basis') == v[1] for k, v in spot.items()),
           'ten spot-checked rows carry the published sq ft and basis')
        await setf(A, 'occupancy', 'Business areas')
        await setf(B, 'occupancy', 'Assembly without fixed seats - concentrated')
        await setf(C, 'occupancy', '  educational -  CLASSROOM area ')
        fD = await safe("(i)=>{var a=window.__a3dRoomLoad(i).area,c=[1.1,0.55,0.3,0.11,0.33],j,x,n;for(j=0;j<c.length;j++){x=a/c[j];n=Math.round(x);if(x>n&&x-n<1e-9)return [c[j],x];}return null;}", D)
        await setf(D, 'loadFactor', str(fD[0]) if fD else '1.1')
        la, lb, lc, ld = [await load(r) for r in (A, B, C, D)]
        fa = la.get('factor') or {}
        ck(abs(fa.get('m2', 0) - 150 * FT2) < 1e-9 and fa.get('basis') == 'gross' and fa.get('src') == 'IBC 1004.5',
           'Business areas: 13.935 m2/person gross, labelled IBC 1004.5 (%s)' % fa)
        ck(la.get('occupants') == occ(100, 150 * FT2) == 8, '100 m2 of Business areas holds 8 (got %s; the first attempt said 14286)' % la.get('occupants'))
        ck(lb.get('occupants') == occ(40, 7 * FT2) == 62, '40 m2 concentrated assembly (7 sq ft net) holds 62 (got %s)' % lb.get('occupants'))
        ck(lc.get('occupants') == occ(36, 20 * FT2) == 20, 'a classroom typed in any case and spacing matches the table: 36 m2 holds 20 (got %s)' % lc.get('occupants'))
        ck(fD is not None and ld.get('occupants') == round(fD[1]), 'exact multiple: %s m2 at %s m2/person holds %s although the quotient is %r (got %s)' % (areas[3], fD and fD[0], fD and round(fD[1]), fD and fD[1], ld.get('occupants')))

        print('\n-- 2. the owner sets the factor; no factor means no load')
        await setf(A, 'loadFactor', '10')
        l1 = await load(A)
        ck(l1.get('occupants') == 10 and (l1.get('factor') or {}).get('src') == 'Set', "the owner's 10 m2/person wins: 10 occupants, source Set (%s)" % l1.get('text'))
        await setf(A, 'loadFactor', 'abc')
        l2 = await load(A)
        await setf(A, 'loadFactor', '')
        l3 = await load(A)
        ck(l2.get('occupants') == 8 and l3.get('occupants') == 8, 'an unreadable or blank factor falls back to the IBC default (%s, %s)' % (l2.get('occupants'), l3.get('occupants')))
        await setf(A, 'occupancy', 'Warp core')
        l4 = await load(A)
        cols, rows = await sched()
        ck(l4.get('occupants') is None and l4.get('text') == 'no load factor', 'an occupancy the table lacks has no load (%s)' % l4.get('text'))
        ck(rows.get('A', {}).get('occupants') == '' and rows.get('A', {}).get('loadFactor') == '', "and the schedule leaves it blank, not 0 (%r)" % rows.get('A', {}).get('occupants'))
        await setf(A, 'occupancy', 'Business areas')

        print('\n-- 3. schedule and Properties agree; the panel field is driven')
        cols, rows = await sched()
        k = cols.index('occupancy') if 'occupancy' in cols else -1
        ck(k >= 0 and cols[k + 1:k + 5] == ['loadFactor', 'loadBasis', 'loadSrc', 'occupants'], 'room schedule columns follow Occupancy (%s)' % cols[k + 1:k + 5])
        ra, rd = rows.get('A', {}), rows.get('D', {})
        ck(ra.get('occupants') == 8 and abs((ra.get('loadFactor') or 0) - 150 * FT2) < 1e-9 and ra.get('loadBasis') == 'gross' and ra.get('loadSrc') == 'IBC 1004.5',
           'schedule row A: 8 occupants at 13.935 gross, IBC 1004.5')
        ck(rd.get('occupants') == (round(fD[1]) if fD else -1) and rd.get('loadSrc') == 'Set', 'schedule row D: the same count, owner-set factor')
        await safe("(i)=>{window.__a3dSelectFor([i]);window.__a3dRefreshProps();}", A)
        await page.wait_for_timeout(200)
        row = await safe("()=>{var e=document.querySelector('[data-roomload]');return e?e.textContent:null;}")
        nopt = await safe("()=>document.querySelectorAll('#bimOccList option').length")
        ck(row is not None and row.startswith('8 at 13.94 m²/person gross (IBC 1004.5)'), 'Properties shows the same load (%r)' % row)
        ck(nopt == len(table), 'the Occupancy field offers every table row (%s)' % nopt)
        inp = page.locator('input[data-roomf="occupancy"]')
        try:
            await inp.fill('Mercantile')
            await inp.press('Tab')
            await page.wait_for_timeout(250)
        except Exception as e:
            print('      (driving the field failed: %s)' % str(e)[:120])
        snap = (await safe("(i)=>window.__a3dObjSnapshot(i)", A)) or {}
        row2 = await safe("()=>{var e=document.querySelector('[data-roomload]');return e?e.textContent:null;}")
        foc = await safe("()=>document.activeElement&&document.activeElement.getAttribute('data-roomf')")
        ph = await safe("()=>{var e=document.querySelector('input[data-roomf=\"loadFactor\"]');return e?e.getAttribute('placeholder'):null;}")
        ck(snap.get('occupancy') == 'Mercantile', 'typing Mercantile into the panel sets the room (%r)' % snap.get('occupancy'))
        ck(row2 is not None and row2.startswith('%d at 5.57' % occ(100, 60 * FT2)), 'the load row updates in place: 18 at 5.57 (%r)' % row2)
        ck(foc == 'loadFactor' and ph is not None and '5.57 IBC default (60 sq ft gross)' in ph, 'focus moved on to Load Factor, whose hint now shows the Mercantile default (%r, %r)' % (foc, ph))
        await blur()

        print('\n-- 4. off by default')
        await paint()
        sa = await style(A)
        ck((await safe("()=>window.__a3dRoomScheme()")) == '' and sa.get('fill') == PLAIN and sa.get('scheme') is None,
           "no colour fill until asked: A's fill is V104's (%s)" % sa.get('fill'))
        ck((await safe("()=>window.__a3dRoomLegend()")) is None, 'and no legend')

        print('\n-- 5. ROOMCOLOR from the command palette')
        await setf(A, 'dept', 'Admin')
        await setf(B, 'dept', 'Sales')
        await setf(C, 'dept', 'admin')
        await paint()
        await blur()
        await palette_run(page, 'ROOMCOLOR')
        await paint()
        s = {n: await style(r) for n, r in (('A', A), ('B', B), ('C', C), ('D', D))}
        lg = (await safe("()=>window.__a3dRoomLegend()")) or {}
        items = lg.get('items') or []
        ck((await safe("()=>window.__a3dRoomScheme()")) == 'dept' and lg.get('by') == 'dept', 'the first ROOMCOLOR fills by Department')
        ck(s['A'].get('scheme') and s['A']['scheme'] == s['C'].get('scheme') and s['A']['scheme'] != s['B'].get('scheme'),
           'Admin and admin share a colour, Sales has another (%s %s %s)' % (s['A'].get('scheme'), s['C'].get('scheme'), s['B'].get('scheme')))
        ck(s['D'].get('scheme') is None and s['D'].get('fill') == PLAIN, 'a room with no department keeps the plain fill')
        ck([i['name'] for i in items] == ['Admin', 'Sales'] and items[0]['col'] == s['A'].get('scheme') and items[1]['col'] == s['B'].get('scheme'),
           'the legend is exactly the drawn values, each in its room colour (%s)' % [(i['name'], i['col']) for i in items])
        box = lg.get('box') or [0, 0, 0, 0]
        cr = (await safe("()=>{var r=window.__a3dCanvasRect();return [r.x||r.left||0,r.y||r.top||0,r.width||r.w,r.height||r.h];}")) or [0, 0, 1e9, 1e9]
        ck(box[2] > 0 and box[0] >= 0 and box[1] >= 0 and box[0] + box[2] <= cr[2] and box[1] + box[3] <= cr[3], 'the legend is drawn inside the canvas (%s)' % box)
        ck(lg.get('align') == 'left', 'the legend sets its own text alignment rather than inheriting the tags\' centring (%r)' % lg.get('align'))
        await palette_run(page, 'ROOMCOLOR')
        await paint()
        lg = (await safe("()=>window.__a3dRoomLegend()")) or {}
        items = lg.get('items') or []
        names = [i['name'] for i in items]
        ck(lg.get('by') == 'occupancy' and names == ['Assembly without fixed seats - concentrated', 'educational - CLASSROOM area', 'Mercantile'],
           'the second fills by Occupancy, listing the three drawn (%s)' % names)
        ck(len(items) == 3 and all(i.get('note') for i in items) and items[2]['note'] == '5.57 m²/p gross', 'each IBC occupancy carries its factor in the legend (%s)' % [i.get('note') for i in items])
        await palette_run(page, 'ROOMCOLOR')
        await paint()
        ck((await safe("()=>window.__a3dRoomScheme()")) == '' and (await style(A)).get('fill') == PLAIN and (await safe("()=>window.__a3dRoomLegend()")) is None,
           'the third turns it off: V104 fill back, no legend')

        print('\n-- 6. kept: reload, undo, copy, SVG, sheet')
        await safe("()=>window.__a3dRoomScheme('dept')")
        await page.wait_for_timeout(1500)
        await page.reload()
        await page.wait_for_timeout(2300)
        await paint()
        ck((await safe("()=>window.__a3dRoomScheme()")) == 'dept' and (await style(A)).get('scheme') == s['A'].get('scheme'), 'the Department fill survives a reload, same colour')
        await setf(A, 'comments', 'north corner')
        await safe("()=>window.__a3dRoomScheme('occupancy')")
        await safe("()=>window.__a3dUndo()")
        snap = (await safe("(i)=>window.__a3dObjSnapshot(i)", A)) or {}
        ck((await safe("()=>window.__a3dRoomScheme()")) == 'dept' and snap.get('comments') == 'north corner', 'undo reverts the fill alone; the edit before it stays (%r)' % snap.get('comments'))
        await setf(A, 'loadFactor', '12')
        before = set(o['id'] for o in ((await safe("()=>window.__a3dState()")) or {}).get('objs', []))
        await safe("(i)=>window.__a3dSelectFor([i])", A)
        await blur()
        await page.keyboard.press('Control+d')
        await page.wait_for_timeout(300)
        new = [o for o in ((await safe("()=>window.__a3dState()")) or {}).get('objs', []) if o['id'] not in before and o.get('t') == 'room']
        cp = new[0] if len(new) == 1 else {}
        ck(cp and all(cp.get(k) == v for k, v in (('dept', 'Admin'), ('occupancy', 'Mercantile'), ('comments', 'north corner'), ('loadFactor', '12'))) and cp.get('number') != 'A',
           'a copied room keeps Department, Occupancy, Comments and Load Factor, with a new number (%s)' % {k: cp.get(k) for k in ('number', 'dept', 'comments', 'loadFactor')})
        await paint()
        svg = ((await safe("()=>window.__a3dBuildSVG('technical')")) or {}).get('text', '')
        m = re.search(r'<path data-obj="%s"[^>]*fill="([^"]+)"' % re.escape(A), svg)
        ck(m is not None and m.group(1) == s['A'].get('scheme'), 'plan SVG fills room A with its canvas colour (%s)' % (m.group(1) if m else None))
        pv = await safe("""()=>{var l=window.__a3dActiveLevel();var sh=window.__a3dAddSheet('A-105','Colour','A3');
            var vp=window.__a3dAddViewport(sh,'plan',l.id,'fit',100);return window.__a3dBuildPlanViewportSVG(sh,vp);}""")
        pv = pv.get('svg', '') if isinstance(pv, dict) else (pv or '')
        m2 = re.search(r'<path data-obj="%s"[^>]*fill="([^"]+)"' % re.escape(A), pv)
        ck(m2 is not None and m2.group(1) == s['A'].get('scheme'), 'a sheet viewport fills it with the same colour (%s)' % (m2.group(1) if m2 else None))
        ck(not errs, 'no uncaught page errors (%s)' % errs[:2])
        await browser.close()
    print('\n%d/%d checks passed' % (ck.n - len(ck.bad), ck.n))
    print('RESULT: ' + ('PASS' if not ck.bad else 'FAIL'))
    return 0 if not ck.bad else 1


if __name__ == '__main__':
    sys.exit(asyncio.run(run()))
