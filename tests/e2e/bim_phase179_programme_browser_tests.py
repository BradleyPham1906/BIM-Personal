#!/usr/bin/env python3
"""bim_phase179_programme_browser_tests.py -- V179: Interiors I1, the programme and adjacency.

The one browser check of the phase's new interface (docs/work-orders/v179/SPEC.md, WO-11):

  1. THE TABLE: with nothing selected, Properties' Project tab has a Programme group; Add use adds a line,
     typing a use matches the rooms of that name; an open room is left out with a warning.
  2. THE RELATIONS: Add relation; next to across a shared wall is met; apart is not met; one edit, one undo.
  3. THE BUBBLE DIAGRAM: in the figure catalogue, drawn from the programme; and the phone width.

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


# three rooms in a row, 0.2 m walls between: Kitchen [0,4], Dining [4.2,7.2], Office [7.4,10]; a Hall not enclosed
ROOMS = [
    {'name': 'Kitchen', 'pts': [[0, 0], [4, 0], [4, 4], [0, 4]]},
    {'name': 'Dining', 'pts': [[4.2, 0], [7.2, 0], [7.2, 4], [4.2, 4]]},
    {'name': 'Office', 'pts': [[7.4, 0], [10, 0], [10, 2], [7.4, 2]]},
    {'name': 'Hall', 'pts': [[0, 5], [3, 5], [3, 7], [0, 7]], 'open': True},
]


async def run():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page(viewport={'width': 1600, 'height': 950})
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        await within(page.goto('file://' + str(HTML)), 'goto')
        await page.wait_for_timeout(2300)
        ev = lambda js, a=None: within(page.evaluate(js, a) if a is not None else page.evaluate(js), js[:50])

        print('1. The table')
        lv = await ev('(r)=>window.__a3dIntRooms(r)', ROOMS)
        ck(bool(lv), 'the rooms are on the active building\'s first level')
        await ev("()=>{const b=document.querySelector('[data-ptabbtn=\"project\"]');if(b)b.click();}")
        grps = (await ev('()=>window.__a3dModelProps()'))['groups']
        ck('Programme' in grps, 'Properties with nothing selected has a Programme group: %s' % grps)
        rep = await ev('()=>window.__a3dIntReport()')
        ck(rep['rooms'] == 3, 'three rooms read, the open one left out (%s)' % rep['rooms'])
        ck(any('Hall' in w and 'not enclosed' in w for w in rep['warnings']), 'the open room is named in a warning')
        ck(await ev("()=>/Hall is left out/.test(document.querySelector('#a3d-propsbody').textContent)"), 'and the warning is shown')

        async def add_use(name, count=None):
            await ev("()=>document.querySelector('[data-intprogact=\"iadd\"]').click()")
            await page.wait_for_timeout(100)
            await ev("""(n)=>{const L=[...document.querySelectorAll('[data-intprog$=":use"]')];const f=L[L.length-1];
              f.value=n;f.dispatchEvent(new Event('change',{bubbles:true}));}""", name)
            await page.wait_for_timeout(100)

        await add_use('Kitchen')
        await add_use('Dining')
        await add_use('Bedroom')
        rep = await ev('()=>window.__a3dIntReport()')
        ck([i['use'] for i in rep['items']] == ['Kitchen', 'Dining', 'Bedroom'], 'Add use and typing: %s' % [i['use'] for i in rep['items']])
        ck([m['status'] for m in rep['matches']] == ['ok', 'ok', 'short'], 'matched by name: Kitchen ok, Dining ok, Bedroom short (%s)' % [m['status'] for m in rep['matches']])
        await ev("""()=>{const f=document.querySelector('[data-intprog$=":areaMin"]');f.value='20';f.dispatchEvent(new Event('change',{bubbles:true}));}""")
        rep = await ev('()=>window.__a3dIntReport()')
        ck(rep['matches'][0]['status'] == 'area', 'Kitchen 16 m2 against a minimum of 20: area out of range')
        ck(await ev("()=>/area out of range/.test(document.querySelector('#a3d-propsbody').textContent)"), 'and the table says so')

        print('2. The relations')
        await ev("()=>document.querySelector('[data-intprogact=\"radd\"]').click()")
        await page.wait_for_timeout(100)
        rep = await ev('()=>window.__a3dIntReport()')
        ck(len(rep['relations']) == 1 and rep['relations'][0]['a'] == 'Kitchen' and rep['relations'][0]['b'] == 'Dining', 'Add relation joins the first two uses')
        ck(rep['checks'][0] == {'status': 'met', 'why': 'a shared wall'}, 'Kitchen next to Dining across the wall: %s' % rep['checks'][0])
        d0 = await ev('()=>window.__a3dUndoDepth()')
        await ev("""()=>{const f=document.querySelector('[data-intprog="r:0:rel"]');f.value='apart';f.dispatchEvent(new Event('change',{bubbles:true}));}""")
        rep = await ev('()=>window.__a3dIntReport()')
        ck(rep['checks'][0] == {'status': 'not met', 'why': 'a shared wall'}, 'apart from: not met, a shared wall')
        ck(await ev('()=>window.__a3dUndoDepth()') == d0 + 1, 'one edit, one undo step')
        await ev("()=>{if(document.activeElement)document.activeElement.blur();}")
        await page.keyboard.press('Control+z')
        await page.wait_for_timeout(150)
        rep = await ev('()=>window.__a3dIntReport()')
        ck(rep['relations'][0]['rel'] == 'next', 'undo brings next to back (%s)' % rep['relations'][0]['rel'])
        await ev("""()=>{const f=document.querySelector('[data-intprog="r:0:b"]');f.value='Bedroom';f.dispatchEvent(new Event('change',{bubbles:true}));}""")
        rep = await ev('()=>window.__a3dIntReport()')
        ck(rep['checks'][0]['status'] == 'not evaluated', 'a use with no room: not evaluated, never a pass (%s)' % rep['checks'][0])

        print('3. The bubble diagram')
        cat = await ev('()=>window.__a3dBrdCat()')
        bub = [c for c in cat if c['f'] == 'int.bubble']
        ck(len(bub) == 1 and bub[0]['has'], 'the catalogue has the bubble diagram, with data: %s' % bub)
        svg = await ev("""()=>{const F=window.__a3dIntBubble();if(!F)return null;const d=document.createElement('div');d.innerHTML=F.body;
          return [d.querySelectorAll('circle').length,d.querySelectorAll('line').length,F.title];}""")
        ck(svg is not None and svg[0] == 3 and svg[1] == 1, 'three circles and one line, the rejected and the missing drawn honestly (%s)' % svg)
        await page.set_viewport_size({'width': 390, 'height': 844})
        await page.wait_for_timeout(300)
        over = await ev("""()=>{const s=document.querySelector('#a3d-propsbody .a3d-int-scroll');if(!s)return null;
          return {sw:s.scrollWidth,cw:s.clientWidth,page:document.documentElement.scrollWidth<=window.innerWidth+1};}""")
        ck(over is None or over['page'], 'on a phone the page does not scroll sideways; the table does (%s)' % over)
        ck(not errs, 'no page errors: %s' % errs[:3])
        await browser.close()


try:
    asyncio.run(run())
except Exception:
    traceback.print_exc()
    BAD.append('the harness stopped')
print('\n%d checks, %d failed' % (N[0], len(BAD)))
sys.exit(1 if BAD else 0)
