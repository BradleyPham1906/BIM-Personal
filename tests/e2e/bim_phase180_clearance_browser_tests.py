#!/usr/bin/env python3
"""bim_phase180_clearance_browser_tests.py -- V180: Interiors I2, clearance and ergonomics.

The one browser check of the phase's new interface (docs/work-orders/v180/SPEC.md, WO-07):

  1. AN ITEM: a furniture model in a 4 m room; Properties' Clearance group; a kind gives it a zone in front;
     facing the wall the zone is blocked by it, turned 180 degrees it is clear; one undo a change; drawn on the plan.
  2. ANOTHER ITEM'S BODY blocks the zone; the two zones may overlap.
  3. A DOOR'S CLEAR WIDTH and A ROOM'S TURNING SPACE against 404.2.3 and 304.3.1, with their edition.

The harness never waits without a bound (V123).
"""
import asyncio, pathlib, sys, traceback
from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parents[2] / 'canvas_v10.html'
STALL = 60
N, BAD = [0], []


def ck(cond, msg):
    N[0] += 1
    if not cond:
        BAD.append(msg)
    print(('  ok    ' if cond else '  FAIL  ') + msg)


async def within(aw, what):
    try:
        return await asyncio.wait_for(aw, STALL)
    except asyncio.TimeoutError:
        raise RuntimeError('stalled: ' + what)


async def run():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page(viewport={'width': 1600, 'height': 950})
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        await within(page.goto('file://' + str(HTML)), 'goto')
        await page.wait_for_timeout(2300)
        ev = lambda js, a=None: within(page.evaluate(js, a) if a is not None else page.evaluate(js), js[:50])

        async def item(i):
            st = await ev('()=>window.__a3dClrState()')
            return [x for x in st['items'] if x['id'] == i][0], st

        async def select(i):
            await ev("(id)=>{window.__a3dSelectFor([id]);window.__a3dRefreshProps();}", i)

        async def setf(sel, v):
            await ev("""([s,v])=>{const f=document.querySelector('#a3d-propsbody '+s);f.value=v;f.dispatchEvent(new Event('change',{bubbles:true}));}""", [sel, v])
            await page.wait_for_timeout(100)

        print('1. An item')
        await ev("()=>window.__a3dTestSetObjs([])")
        wall = await ev("()=>window.__a3dCurvedWall([[0,0],[4,0],[4,4],[0,4]],[0,0,0,0],0.2,3,'center',true)")
        ck(bool(wall), 'a closed 4 m wall')
        room = await ev("()=>window.__a3dCreateRoomAt([2,2],0)")
        ck(bool(room), 'a room inside it')
        # a 1.0 by 0.5 m cabinet against the bottom wall, at z 0.4: its front (+z when facing 0) is into the room
        cab = await ev("()=>window.__a3dClrItem('Furniture',2,0.4,1.0,0.5)")
        await select(cab)
        ck(await ev("()=>!!document.querySelector('#a3d-propsbody [data-a3dpgrp=\"Clearance\"]')"), 'Properties has a Clearance group')
        it, st = await item(cab)
        ck(not it['zone'], 'no kind, no zone')
        d0 = await ev('()=>window.__a3dUndoDepth()')
        await setf('[data-clr="kind"]', 'storage')
        it, st = await item(cab)
        ck(it['kind'] == 'storage' and it['zone'], 'a kind gives a zone')
        ck(await ev('()=>window.__a3dUndoDepth()') == d0 + 1, 'one change, one undo step')
        ck(it['blocked'] == [], 'facing into the room: the zone is clear (%s)' % it['blocked'])
        ck(abs(it['w'] - 1.0) < 1e-6 and abs(it['d'] - 0.5) < 1e-6, 'its body is its footprint, 1.0 by 0.5')
        await setf('[data-clr="face"]', '180')
        it, st = await item(cab)
        ck(len(it['blocked']) == 1, 'facing the wall: the zone is blocked by the wall (%s)' % it['blocked'])
        txt = await ev("()=>document.querySelector('#a3d-propsbody').textContent")
        ck('blocked by' in txt and 'int.zone' not in txt and 'clearance zones' in txt.lower(), 'Properties says it, and names its standard')
        await ev("()=>window.__a3dTestPaint&&window.__a3dTestPaint()")
        ck((await ev('()=>window.__a3dClrState()'))['lastZones'] == 1, 'the selected item\'s zone is drawn on the plan')
        await ev("()=>{if(document.activeElement)document.activeElement.blur();}")
        await page.mouse.click(5, 5)
        await select(cab)
        await page.keyboard.press('Control+z')
        await page.wait_for_timeout(200)
        it, st = await item(cab)
        ck(it['blocked'] == [], 'undo turns it back: clear again (%s)' % it['blocked'])

        print('2. Another item\'s body')
        tab = await ev("()=>window.__a3dClrItem('Furniture',2,1.4,1.2,0.8)")
        it, st = await item(cab)
        ck(len(it['blocked']) == 1, 'a table in front blocks the cabinet\'s zone (%s)' % it['blocked'])
        await select(tab)
        await setf('[data-clr="kind"]', 'work')
        await setf('[data-clr="face"]', '180')
        it2, st = await item(tab)
        it, st = await item(cab)
        ck(len(it2['blocked']) == 1, 'the table facing the cabinet: its zone meets the cabinet\'s body (%s)' % it2['blocked'])

        print('3. A door and a room')
        door = await ev("()=>window.__a3dDoorAt(%s,[4,2],0.9,2.1)" % repr(wall).replace("'", '"'))
        if door:
            d = await ev('(id)=>window.__a3dClrDoor(id)', door)
            ck(d['status'] == 'meets' and d['clause'] == '404.2.3' and '2010 ADA' in d['edition'], 'a 0.9 m door: meets 404.2.3, 2010 ADA (%s)' % d)
            await select(door)
            ck('Clear width' in await ev("()=>document.querySelector('#a3d-propsbody').textContent"), 'the door\'s Properties show it')
        else:
            ck(False, 'the door could not be cut')
        r = await ev('(id)=>window.__a3dClrRoom(id)', room)
        ck(r['rule']['clause'] == '304.3.1' and r['rule']['status'] in ('meets', 'below') and r['d'] > 0, 'the room\'s turning space measured: %s, %.2f m' % (r['rule']['status'], r['d']))
        await select(room)
        ck('Turning space' in await ev("()=>document.querySelector('#a3d-propsbody').textContent"), 'the room\'s Properties show it')
        ck(not errs, 'no page errors: %s' % errs[:3])
        await browser.close()


try:
    asyncio.run(run())
except Exception:
    traceback.print_exc()
    BAD.append('the harness stopped')
print('\n%d checks, %d failed' % (N[0], len(BAD)))
sys.exit(1 if BAD else 0)
