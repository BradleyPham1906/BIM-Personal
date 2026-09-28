#!/usr/bin/env python3
"""bim_phase105b_area_plans_browser_tests.py -- V105b: gross and net area plans per level.

Asserted on the model, against areas worked out by hand, not on appearance:
  1. GROSS IS MEASURED TO THE INSIDE FACE of the exterior walls. A 10 x 6 rectangle of 0.3 walls
     encloses 9.7 x 5.7 = 55.29 m2, not 60. One wall thickened to 0.5 moves the corner and the
     area with it. An interior partition does not change gross, and it does change net.
  2. THE INSET IS THE WALL'S OWN BODY, not half its thickness on principle. The same rectangle
     drawn left-aligned and right-aligned gives 50.76 and 60 -- a centred assumption gives 55.29
     for both, and cannot produce that pair.
  3. A CURVED EXTERIOR WALL is offset arc-wise. Two semicircles of centreline radius 5 and
     thickness 0.4 enclose pi * 4.8^2 = 72.38 m2, not the chord figure and not pi * 5^2.
  4. SPURS AND ISLANDS. A wall stub is walked in and back out of the traced face; it must come out
     before the offset or it drags the perimeter with it. A closed run of partitions touching
     nothing is its own component and traces its own outer face: counting it would count that
     floor twice.
  5. OCCUPANT LOAD IS TAKEN PER FACTOR, NOT PER ROOM. Two rooms of 21.375 and 32.775 m2 at 5
     m2/person hold 11 between them, although room by room they round to 5 + 7 = 12. A gross
     factor is taken against gross area: the rooms are apportioned by gross/net, and the schedule
     says so.
  6. THE SCHEDULE, THE OVERLAY AND THE TOAST read one function. AREAPLAN from the command palette
     draws the ring and hides it again, and the schedule is registered, so the Project Browser and
     the CSV export list it without being told.
"""
import asyncio, math, pathlib, sys
from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'
FT2 = 0.09290304


class Checks:
    def __init__(self):
        self.n, self.bad = 0, []

    def __call__(self, cond, msg):
        self.n += 1
        if not cond:
            self.bad.append(msg)
        print(('ok    ' if cond else 'FAIL  ') + msg)


def near(a, b, tol=1e-6):
    return a is not None and b is not None and abs(a - b) <= tol


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
                print('      (evaluate failed: %s)' % str(e)[:140])
                return None

        async def blur():
            await safe("()=>{if(document.activeElement)document.activeElement.blur();}")

        async def clear():
            await safe("()=>{window.__a3dTestSetObjs([]);window.__a3dTestPaint();}")

        async def wall(pts, thk=0.3, align='center', closed=False, bulges=None):
            if bulges is None:
                return await safe("([p,t,a,c])=>window.__a3dWall(p,t,null,a,c)", [pts, thk, align, closed])
            return await safe("([p,b,t,a,c])=>window.__a3dCurvedWall(p,b,t,null,a,c)", [pts, bulges, thk, align, closed])

        async def rect_walls(x0, z0, x1, z1, thk=0.3, align='center'):
            ids = []
            for a, b in (([x0, z0], [x1, z0]), ([x1, z0], [x1, z1]), ([x1, z1], [x0, z1]), ([x0, z1], [x0, z0])):
                ids.append(await wall([a, b], thk, align))
            return ids

        async def rings(level=None):
            return (await safe("(l)=>window.__a3dGrossRings(l)", level or '')) or {}

        async def areas(level=None):
            return (await safe("(l)=>window.__a3dLevelAreas(l)", level or '')) or {}

        async def gross():
            return (await areas()).get('gross')

        async def room(pt, y=0):
            return await safe("([p,y])=>window.__a3dCreateRoomAt(p,y)", [pt, y])

        async def setf(i, k, v):
            return await safe("([i,k,v])=>window.__a3dSetRoomField(i,k,v)", [i, k, v])

        async def load(i):
            return (await safe("(i)=>window.__a3dRoomLoad(i)", i)) or {}

        async def palette_run(name):
            await blur()
            await page.keyboard.press('Control+k')
            await page.wait_for_timeout(320)
            await page.keyboard.type(name)
            await page.wait_for_timeout(260)
            await page.keyboard.press('Enter')
            await page.wait_for_timeout(450)

        await safe("()=>{window.__a3dFlat(true);window.__a3dTestPaint();}")

        print('\n-- 1. gross is measured to the inside face of the exterior walls')
        await clear()
        await rect_walls(0, 0, 10, 6, 0.3)
        r = await rings()
        ck(r.get('error') is None and len(r.get('rings') or []) == 1,
           'a rectangle of four walls traces one gross ring (%s rings, error %r)' % (len(r.get('rings') or []), r.get('error')))
        g1 = (r.get('rings') or [{}])[0].get('area')
        ck(near(g1, 55.29, 1e-6), '10 x 6 centrelines, 0.3 walls: gross 9.7 x 5.7 = 55.29 m2 (got %r)' % g1)
        ck(not near(g1, 60.0, 1e-3) and not near(g1, 54.15, 1e-3),
           'and it is neither the centreline area 60 nor the outside-to-outside figure')

        await clear()
        await wall([[0, 0], [10, 0], [10, 6], [0, 6]], 0.3, 'center', True)
        gcl = await gross()
        ck(near(gcl, 55.29, 1e-6),
           'ONE closed wall round the same rectangle measures the same 55.29 m2 (got %r)' % gcl)

        await clear()
        await rect_walls(0, 0, 10, 6, 0.3)
        await safe("()=>{var st=window.__a3dState(),i;for(i=0;i<st.objs.length;i++)window.__a3dSetPos(st.objs[i].id,7,0,-4);}")
        gmv = await gross()
        ck(near(gmv, 55.29, 1e-6), 'moving the whole building leaves gross at 55.29 m2 (got %r)' % gmv)

        await clear()
        ids = await rect_walls(0, 0, 10, 6, 0.3)
        await safe("(i)=>window.__a3dDeleteWallForTest(i)", ids[3])
        await wall([[0, 6], [0, 0]], 0.5)
        g2 = await gross()
        ck(near(g2, 54.72, 1e-6), 'one wall thickened to 0.5 moves the corner: 9.6 x 5.7 = 54.72 m2 (got %r)' % g2)

        print('\n-- 2. the inset is the wall body, not half the thickness by assumption')
        await clear()
        await rect_walls(0, 0, 10, 6, 0.3, 'left')
        gl = await gross()
        await clear()
        await rect_walls(0, 0, 10, 6, 0.3, 'right')
        grt = await gross()
        pair = sorted([round(x, 6) for x in (gl, grt)]) if (gl is not None and grt is not None) else None
        ck(pair == [50.76, 60.0],
           'left- and right-aligned give 9.4 x 5.4 = 50.76 and 10 x 6 = 60 (got %s)' % pair)
        ck(pair is not None and abs(sum(pair) - 110.76) < 1e-6 and abs(2 * 55.29 - 110.58) < 1e-9,
           'their sum 110.76 is not 2 x 55.29 = 110.58, so a centred inset cannot produce this pair')

        async def ray(poly, closed, pt, n, lim):
            return await safe("([q,c,p,n,l])=>window.__a3dRayPolyDepth(q,c,p,n,l)", [poly, closed, pt, n, lim])

        U = [[0, 1], [4, 1], [4, 3], [0, 3]]
        d1 = await ray(U, False, [2, 0], [0, 1], 10)
        d2 = await ray(U, False, [2, 0], [0, 1], 2)
        d3 = await ray([[0, 1], [2, 1]], False, [5, 0], [0, 1], 10)
        d4 = await ray(U, False, [2, 4], [0, 1], 10)
        ck(near(d1, 3.0, 1e-9), 'the ray takes the FAR face of a body it passes through twice (%r)' % d1)
        ck(near(d2, 1.0, 1e-9), 'and the thickness limit keeps it on the near face (%r)' % d2)
        ck(d3 is None, 'a segment the ray misses is not used as an infinite line (%r)' % d3)
        ck(d4 is None, 'nothing ahead of the ray means no inset, not a crossing behind it (%r)' % d4)
        ins = await safe("()=>{window.__a3dTestSetObjs([]);var i=window.__a3dWall([[0,0],[10,0]],0.4,null,'center',false);return [window.__a3dWallInsetAt(i,[5,0],[0,1]),window.__a3dWallInsetAt(i,[5,0],[0,-1])];}")
        ck(ins and near(ins[0], 0.2, 1e-9) and near(ins[1], 0.2, 1e-9),
           'a centred 0.4 wall reaches 0.2 either way from its centreline (%s)' % ins)
        ins2 = await safe("()=>{window.__a3dTestSetObjs([]);var i=window.__a3dWall([[0,0],[10,0]],0.4,null,'right',false);return [window.__a3dWallInsetAt(i,[5,0],[0,1]),window.__a3dWallInsetAt(i,[5,0],[0,-1])];}")
        ck(ins2 and sorted(round(x, 9) for x in ins2) == [0.0, 0.4],
           'a one-sided 0.4 wall reaches its whole thickness one way and nothing the other (%s)' % ins2)

        print('\n-- 3. a curved exterior wall is offset arc-wise')
        await clear()
        await wall([[5, 0], [-5, 0]], 0.4, 'center', False, [1, 0])
        await wall([[-5, 0], [5, 0]], 0.4, 'center', False, [1, 0])
        rc = await rings()
        gc = (rc.get('rings') or [{}])[0].get('area') if (rc.get('rings') or []) else None
        want = math.pi * 4.8 * 4.8
        ck(gc is not None and abs(gc - want) / want < 0.005,
           'two semicircles, centreline r 5, 0.4 thick: gross pi*4.8^2 = %.4f m2 (got %r)' % (want, gc))
        ck(gc is not None and abs(gc - math.pi * 25) / want > 0.02,
           'and it is not the centreline circle pi*5^2 = %.4f' % (math.pi * 25))

        print('\n-- 4. spurs come out, islands are not counted twice')
        await clear()
        await rect_walls(0, 0, 10, 6, 0.3)
        await wall([[10, 3], [13, 3]], 0.3)
        gs = await gross()
        ck(near(gs, 55.29, 1e-6), 'a 3 m stub off the east wall leaves gross at 55.29 m2 (got %r)' % gs)

        await clear()
        await rect_walls(0, 0, 10, 6, 0.3)
        await wall([[2, 2], [4, 2], [4, 4], [2, 4]], 0.2, 'center', True)
        ri = await rings()
        gi = (await areas()).get('gross')
        ck(len(ri.get('rings') or []) == 1 and near(gi, 55.29, 1e-6),
           'a free-standing closed partition ring inside is not a second footprint (%s rings, gross %r)'
           % (len(ri.get('rings') or []), gi))

        await clear()
        await rect_walls(0, 0, 10, 6, 0.3)
        await rect_walls(20, 0, 30, 6, 0.3)
        r2 = await rings()
        g2r = (await areas()).get('gross')
        ck(len(r2.get('rings') or []) == 2 and near(g2r, 110.58, 1e-6),
           'two separate buildings on one level give two rings and 110.58 m2 (%s rings, %r)'
           % (len(r2.get('rings') or []), g2r))

        print('\n-- 5. net, efficiency and occupant load')
        await clear()
        await rect_walls(0, 0, 10, 6, 0.3)
        await wall([[4, 0], [4, 6]], 0.2)
        gp = await gross()
        ck(near(gp, 55.29, 1e-6), 'an interior partition does not change gross: still 55.29 m2 (got %r)' % gp)
        A = await room([2, 3])
        B = await room([7, 3])
        la = (await load(A)).get('area')
        lb = (await load(B)).get('area')
        ck(near(la, 21.375, 1e-6) and near(lb, 32.775, 1e-6),
           'the two rooms measure 3.75 x 5.7 = 21.375 and 5.75 x 5.7 = 32.775 m2 (%r, %r)' % (la, lb))
        a5 = await areas()
        ck(near(a5.get('net'), 54.15, 1e-6) and a5.get('rooms') == 2,
           'net is the rooms: 54.15 m2 over 2 rooms (got %r over %r)' % (a5.get('net'), a5.get('rooms')))
        ck(near(a5.get('efficiency'), 54.15 / 55.29 * 100, 1e-9),
           'efficiency is net over gross: %.4f%% (got %r)' % (54.15 / 55.29 * 100, a5.get('efficiency')))

        await setf(A, 'loadFactor', '5')
        await setf(B, 'loadFactor', '5')
        a6 = await areas()
        ra, rb = (await load(A)).get('occupants'), (await load(B)).get('occupants')
        ck(ra == 5 and rb == 7, 'room by room, 21.375 and 32.775 at 5 m2/person round up to 5 and 7 (%r, %r)' % (ra, rb))
        ck(a6.get('occupants') == 11,
           'the floor holds 11, not the 12 that rounding each room up separately invents (got %r)' % a6.get('occupants'))
        await setf(B, 'loadFactor', '4')
        a7 = await areas()
        ck(a7.get('occupants') == 5 + math.ceil(32.775 / 4 - 1e-9) == 14,
           'two different factors are not merged: 5 + 9 = 14 (got %r)' % a7.get('occupants'))

        await setf(A, 'loadFactor', '')
        await setf(B, 'loadFactor', '')
        await setf(A, 'occupancy', 'Business areas')
        await setf(B, 'occupancy', 'Business areas')
        a8 = await areas()
        want8 = math.ceil(55.29 / (150 * FT2) - 1e-9)
        ck(a8.get('occupants') == want8 == 4,
           'a gross factor is taken against gross area: 55.29 / 13.9355 = 4 occupants (got %r)' % a8.get('occupants'))
        ck('apportioned' in (a8.get('note') or ''),
           'and the apportionment is said, not hidden (%r)' % a8.get('note'))
        await setf(A, 'occupancy', 'Educational - classroom area')
        await setf(B, 'occupancy', 'Educational - classroom area')
        a9 = await areas()
        ck(a9.get('occupants') == math.ceil(54.15 / (20 * FT2) - 1e-9) == 30,
           'a net factor is taken against room area: 54.15 / 1.85806 = 30 (got %r)' % a9.get('occupants'))
        await setf(B, 'occupancy', 'Warp core')
        a10 = await areas()
        ck('1 room with no load factor' in (a10.get('note') or ''),
           'a room the table has no factor for is counted in the note (%r)' % a10.get('note'))

        await safe("()=>window.__a3dRegenerateRegions()")
        await page.wait_for_timeout(200)
        ra2, rb2 = (await load(A)).get('area'), (await load(B)).get('area')
        ck(near(ra2, 21.375, 1e-6) and near(rb2, 32.775, 1e-6),
           're-measuring the rooms from their region keeps them at the wall faces (%r, %r)' % (ra2, rb2))
        part = await safe("()=>{var st=window.__a3dState(),i,o;for(i=0;i<st.objs.length;i++){o=st.objs[i];if(o.bim&&o.bim.type==='wall'&&Math.abs(o.bim.thickness-0.2)<1e-9)return o.id;}return null;}")
        await safe("(i)=>window.__a3dRebuildWall(i,0.4)", part)
        await page.wait_for_timeout(250)
        ra3, rb3 = (await load(A)).get('area'), (await load(B)).get('area')
        a11 = await areas()
        ck(near(ra3, 20.805, 1e-6) and near(rb3, 32.205, 1e-6),
           'thickening the partition to 0.4 re-measures the rooms to 20.805 and 32.205 m2 (%r, %r)' % (ra3, rb3))
        ck(near(a11.get('gross'), 55.29, 1e-6) and near(a11.get('net'), 53.01, 1e-6),
           'gross is unchanged at 55.29 and net falls to 53.01 m2 (%r, %r)' % (a11.get('gross'), a11.get('net')))
        await safe("(i)=>window.__a3dRebuildWall(i,0.2)", part)
        await page.wait_for_timeout(250)

        print('\n-- 6. schedule, overlay and command')
        keys = (await safe("()=>window.__a3dScheduleKeys()")) or []
        await safe("()=>window.__a3dRefreshBrowser()")
        await page.wait_for_timeout(200)
        await safe("()=>{var g=document.querySelector('#a3d-browser [data-a3dbgrp=\"schedules\"]');if(g)g.click();}")
        await page.wait_for_timeout(300)
        brow = (await safe("()=>window.__a3dBrowserSchedules()")) or []
        bk = [b.get('key') for b in brow if isinstance(b, dict)]
        ck('arealevel' in keys, 'the schedule is registered (%s)' % ('arealevel' in keys))
        ck('arealevel' in bk, 'so the Project Browser lists it without being told (%s)' % bk[-3:])
        s = (await safe("()=>window.__a3dScheduleRows('arealevel')")) or {'cols': [], 'rows': []}
        ck(s['cols'] == ['level', 'gross', 'net', 'efficiency', 'rooms', 'occupants', 'note'],
           'columns are Level, Gross, Net, Efficiency, Rooms, Occupant Load, Note (%s)' % s['cols'])
        lv = (await safe("()=>window.__a3dLevels()")) or []
        ck(len(s['rows']) == len(lv), 'one row per level (%d rows, %d levels)' % (len(s['rows']), len(lv)))
        cur = await areas()
        row0 = [x for x in s['rows'] if x.get('level') == cur.get('level')]
        ck(len(row0) == 1 and near(row0[0].get('gross'), cur.get('gross'), 1e-9) and near(row0[0].get('net'), cur.get('net'), 1e-9),
           'the row for the active level carries the same gross and net the API reports')
        opened = await safe("()=>window.__a3dOpenSchedule('arealevel')")
        await page.wait_for_timeout(220)
        body = (await safe("()=>{var e=document.querySelector('#a3d-schedbody');return e?e.textContent:'';}")) or ''
        ck(opened is True, 'the hidden category chooser carries it, so it can actually be opened (%r)' % opened)
        ck('Gross' in body and ('%.2f' % (cur.get('gross') or 0)) in body,
           'and the rendered table shows the gross figure (%r)' % body[:70])
        csv = (await safe("()=>{var r=window.__a3dScheduleRows('arealevel');return window.__a3dScheduleCSV(r.rows,r.cols.map(function(k){return {key:k,label:k};}));}")) or ''
        lines = [x for x in csv.replace('\r', '').split('\n') if x]
        ck(lines and lines[0].startswith('level,gross,net,efficiency') and len(lines) == 1 + len(s['rows']),
           'the CSV writer takes its columns and every row (%r)' % (lines[0] if lines else None))

        lid = await safe("()=>{var l=window.__a3dAddLevel();window.__a3dTestPaint();return window.__a3dLevels();}")
        lid = lid or []
        ck(len(lid) >= 2, 'a second level exists (%d)' % len(lid))
        if len(lid) >= 2:
            up = [x for x in lid if x['id'] != cur.get('levelId')][0]
            await safe("(i)=>{window.__a3dSetLevel(i);window.__a3dTestPaint();}", up['id'])
            au = await areas()
            ck(au.get('gross') is None and au.get('occupants') is None and 'no closed run of walls' in (au.get('note') or ''),
               'an empty level reports no gross area and says why, rather than 0 (%r / %r)' % (au.get('gross'), au.get('note')))
            await rect_walls(0, 20, 10, 26, 0.3)
            au2 = await areas()
            ck(near(au2.get('gross'), 55.29, 1e-6), 'walls on the upper level measure there (got %r)' % au2.get('gross'))
            s2 = (await safe("()=>window.__a3dScheduleRows('arealevel')")) or {'rows': []}
            base = [x for x in s2['rows'] if x.get('level') == cur.get('level')]
            names = sorted(x.get('level') for x in s2['rows'])
            ck(len(base) == 1 and near(base[0].get('gross'), 55.29, 1e-6),
               'and the level below is still reported at 55.29 (got %r)' % (base[0].get('gross') if base else None))
            ck(len(s2['rows']) == len(lid) and names == sorted(x['name'] for x in lid),
               'the schedule has a row for every level, not just the first (%s)' % names)
            await safe("(i)=>{window.__a3dSetLevel(i);window.__a3dTestPaint();}", cur.get('levelId'))

        drawn0 = await safe("()=>{window.__a3dTestPaint();return window.__a3dAreaDrawn();}")
        ck(drawn0 is None, 'the overlay is off until it is asked for (%r)' % drawn0)
        await palette_run('AREAPLAN')
        await safe("()=>window.__a3dTestPaint()")
        drawn1 = await safe("()=>window.__a3dAreaDrawn()")
        ck(isinstance(drawn1, dict) and drawn1.get('rings') == 1 and near(drawn1.get('gross'), 55.29, 1e-6),
           'AREAPLAN from the command palette draws one ring of 55.29 m2 (%r)' % drawn1)
        ck(isinstance(drawn1, dict) and near(drawn1.get('net'), (await areas()).get('net'), 1e-9),
           'and the overlay carries the same net the schedule reports')
        await palette_run('AREAPLAN')
        await safe("()=>window.__a3dTestPaint()")
        drawn2 = await safe("()=>window.__a3dAreaDrawn()")
        ck(drawn2 is None, 'running it again hides it (%r)' % drawn2)

        fr = await safe("()=>{var st=window.__a3dState(),i;for(i=0;i<st.objs.length;i++)if(st.objs[i].bim&&st.objs[i].bim.type==='wall')return window.__a3dWallFaceRings(st.objs[i].id);return null;}")
        ck(isinstance(fr, dict) and len(fr.get('a') or []) >= 2 and len(fr.get('b') or []) >= 2,
           'a wall publishes both of its built faces (%s / %s points)' % (len(fr.get('a') or []) if fr else None, len(fr.get('b') or []) if fr else None))
        ck(not errs, 'no uncaught page errors (%s)' % errs[:2])
        await browser.close()
    print('\n%d/%d checks passed' % (ck.n - len(ck.bad), ck.n))
    print('RESULT: ' + ('PASS' if not ck.bad else 'FAIL'))
    return 0 if not ck.bad else 1


if __name__ == '__main__':
    sys.exit(asyncio.run(run()))
