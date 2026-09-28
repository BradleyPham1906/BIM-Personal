#!/usr/bin/env python3
"""bim_phase109_view_controls_browser_tests.py -- V109: the view controls live in the status bar.

  1. PLACED: no floating pill; pan, orbit, the 2D/3D switch and Tech/Pres sit in #a3d-navgrp, in
     the status bar, immediately after SNAP / ORTHO / GRID, visible and inside the bar.
  2. DRIVEN by real clicks there: the 2D/3D button switches plan and 3D and relabels itself; PAN
     and ORBIT set the navigation mode and move the highlight; Tech/Pres switches presentation.
  3. THE PANEL TOGGLE that hid the pill hides the group.
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
        ev = page.evaluate

        async def click(nav):
            try:
                await page.click('#a3d-navgrp [data-a3dnav="%s"]' % nav, timeout=3000)
                await page.wait_for_timeout(250)
            except Exception as e:
                print('      (click %s failed: %s)' % (nav, str(e)[:120]))

        async def state():
            return await ev("()=>{var s=window.__a3dState(),g=document.getElementById('a3d-navgrp');"
                            "return {flat:s.flat,nav:s.nav,pres:window.__a3dPresentMode(),"
                            "on:g?Array.prototype.filter.call(g.querySelectorAll('[data-a3dnav]'),function(b){return b.classList.contains('on');}).map(function(b){return b.getAttribute('data-a3dnav');}):null,"
                            "flip:(document.getElementById('a3d-flip')||{}).textContent,present:(document.getElementById('a3d-present')||{}).textContent};}")

        print('\n-- 1. placed')
        lay = await ev("""()=>{var g=document.getElementById('a3d-navgrp'),bar=document.getElementById('a3d-statusbar');
            if(!g||!bar)return null;var br=bar.getBoundingClientRect();
            var bs=Array.prototype.map.call(g.querySelectorAll('[data-a3dnav]'),function(b){var r=b.getBoundingClientRect();
              return {a:b.getAttribute('data-a3dnav'),vis:!!b.offsetParent&&r.width>0,inside:r.top>=br.top-1&&r.bottom<=br.bottom+1&&r.left>=br.left&&r.right<=br.right};});
            return {pill:!!document.getElementById('a3d-pill'),inBar:!!g.closest('#a3d-statusbar'),prev:g.previousElementSibling&&g.previousElementSibling.id,btns:bs};}""")
        ck(lay is not None and lay['pill'] is False and lay['inBar'], 'no floating pill; the view controls are in the status bar (%s)' % (lay and {k: lay[k] for k in ('pill', 'inBar')}))
        ck(lay is not None and lay['prev'] == 'a3d-snapgrp', 'immediately after SNAP / ORTHO / GRID (%s)' % (lay and lay['prev']))
        ck(lay is not None and [b['a'] for b in lay['btns']] == ['pan', 'orbit', 'flip', 'present'] and all(b['vis'] and b['inside'] for b in lay['btns']),
           'pan, orbit, 2D/3D and Tech/Pres, all visible inside the bar')

        print('\n-- 2. driven')
        s0 = await state()
        await click('flip')
        s1 = await state()
        ck(s0['flat'] is True and s0['flip'] == '3D' and s1['flat'] is False and s1['flip'] == '2D', 'the switch goes from plan to 3D and relabels itself (%s -> %s)' % (s0['flip'], s1['flip']))
        await click('pan')
        s2 = await state()
        await click('orbit')
        s3 = await state()
        ck(s2['nav'] == 'pan' and s2['on'] == ['pan'] and s3['nav'] == 'orbit' and s3['on'] == ['orbit'], 'PAN and ORBIT set the mode and move the highlight (%s, %s)' % (s2['on'], s3['on']))
        await click('present')
        s4 = await state()
        await click('present')
        s5 = await state()
        ck(s4['pres'] is True and s4['present'] == 'Pres' and s5['pres'] is False and s5['present'] == 'Tech', 'Tech/Pres switches presentation and says which')
        await click('flip')
        ck((await state())['flat'] is True, 'and back to plan')

        print('\n-- 3. the panel toggle')
        await ev("()=>window.__a3dSetUIPanelVisible('navpill',false)")
        hid = await ev("()=>{var g=document.getElementById('a3d-navgrp');return g?g.offsetParent===null:null;}")
        await ev("()=>window.__a3dSetUIPanelVisible('navpill',true)")
        back = await ev("()=>{var g=document.getElementById('a3d-navgrp');return g?g.offsetParent!==null:null;}")
        ck(hid is True and back is True, 'hiding the navigation panel hides the group, and showing it brings it back')
        ck(not errs, 'no uncaught page errors (%s)' % errs[:2])
        await browser.close()
    print('\n%d/%d checks passed' % (ck.n - len(ck.bad), ck.n))
    print('RESULT: ' + ('PASS' if not ck.bad else 'FAIL'))
    return 0 if not ck.bad else 1


if __name__ == '__main__':
    sys.exit(asyncio.run(run()))
