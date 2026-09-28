"""
bim_phase83_rail_utility_stack_browser_tests.py

Regression suite for __acad3dV83 in canvas_v10.html: the foot of the left rail becomes a vertical
stack of real view and document utilities.

WHAT THE USER ASKED FOR: "can you update this left bottom corner section for our app for stuff like
settings, zoom, just like how rayon have in vertical stack. the current one we have s just 'A?'."

WHAT WAS THERE: one 24px "A?" button under roughly 900px of empty column.

WHAT SHIPPED -- Zoom (extents / to selection / window), Appearance (Technical / Presentation, Dark /
Light), Snaps (point / grid / ortho and the grid size), Units (m / cm / mm and decimals), Save image,
and -- at the time -- the existing "A?" button kept beneath the stack.

__acad3dV85 AMENDED THIS SUITE. The "A?" button was not a Shortcuts button and was never
restyled into anything: it had no click handler anywhere in the file, no title, and driven with
a real pointer it produced no dialog, no toast and no visible change. This suite described it as
"the existing Shortcuts button kept" on the strength of its appearance, which is the same mistake
V80's whitelist made when it claimed '.fl-help' as "keyboard help". V85 removed the dead button
and added a real Keyboard shortcuts sheet as the stack's sixth entry. The checks below now expect
six utilities and NO leftover button; what they were defending -- a vertical stack at the foot of
the rail that survives a shell re-render -- is unchanged and still checked.

WHY EACH CHECK IS THE ONE THAT WOULD CATCH A REGRESSION:

  1. Every popover is asserted to open fully ON SCREEN, by measuring its rectangle against the
     window. This is the V70 lesson paid forward: the dock's carets once opened at top:1109 in a
     950px window while every state check passed, because a fixed-position element inside a
     transformed ancestor resolves against that ancestor. A "did the menu open" check cannot see
     that; only measuring where it landed can.
  2. Every action is asserted by reading the MODEL or the DOCUMENT back, never by the menu's own
     appearance. A menu that highlights the right row and changes nothing is precisely the fault
     Product Principle 1 forbids, and it is what the previous "A?"-only corner would have become if
     it had been filled in carelessly.
  3. Zoom window is driven with real pointer events through the whole gesture -- arm, rubber-band,
     release -- and asserted to change the camera AND disarm afterwards. A modal view operation that
     stays armed silently eats the next click the user makes on the drawing.
  4. Escape is asserted to close a popover and to cancel an armed zoom window. A modal state with no
     way out is worse than no modal state.
  5. The stack is asserted to survive a File/Assets round trip, because the whiteboard's own setTab
     re-renders the shell and V80's observer is what keeps it there.
  6. The V80 shell audit is asserted clean, which is the standing rule: a control added without
     being claimed fails the build, exactly as a control added without being wired should.

Run:  python3 bim_phase83_rail_utility_stack_browser_tests.py [path/to/canvas_v10.html]
"""

# AMENDED FOR V120: the shell's canvas-era names were replaced -- #figma-layers-shell/-rail/-panel are
# #a3d-shell/-rail/-leftpanel, the .fl-* classes .a3d-*, #uploaded-command-palette #a3d-cmdpal, the
# Project Browser tab 'file' is 'browser', --figma-dock-w is --a3d-left-w, and the material library is
# read through window.__a3dMaterialCards() (window.__WB_MATERIAL_CARDS is gone).
import asyncio, pathlib, sys

from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'


async def open_menu_with_mouse(page, mid):
    """Open a rail menu with a REAL mouse click.

    Playwright only delivers keyboard events to a page that has genuine input focus, and a
    synthetic element.click() does not give it any. The first version of the Escape checks below
    opened the menu through __a3dRailOpen (which calls .click()) and then pressed Escape into a
    void: every keydown listener in the page, including a freshly added probe, saw nothing at all.
    The feature was fine; the test was not delivering the key.
    """
    utils = await page.evaluate("()=>window.__a3dRailUtils()")
    btn = [u for u in utils if u['id'] == mid][0]
    await page.mouse.click(btn['x'] + btn['w'] / 2, btn['y'] + btn['h'] / 2)
    await page.wait_for_timeout(250)
    return await page.evaluate("()=>{const p=document.getElementById('a3d-rupop');"
                               "return !!(p&&p.classList.contains('open'));}")


class Checks:
    def __init__(self):
        self.n = 0
        self.failed = []

    def __call__(self, cond, msg):
        self.n += 1
        ok = bool(cond)
        print(("  PASS  " if ok else "  FAIL  ") + msg)
        if not ok:
            self.failed.append(msg)


async def run():
    ck = Checks()
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1600, 'height': 950},
                                        device_scale_factor=2, accept_downloads=True)
        page = await ctx.new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        await page.goto('file://' + str(HTML))
        await page.wait_for_timeout(2100)

        has83 = await page.evaluate("()=>!!window.__acad3dV83")
        ck(has83, "__acad3dV83 marker is present")
        if not has83:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.failed), ck.n))
            await browser.close()
            return 1

        print("\n-- 1. a vertical stack at the FOOT of the rail")
        stack = await page.evaluate("()=>window.__a3dRailUtils()")
        ck(stack is not None and len(stack) == 6,
           "six utilities (%s)" % [s['id'] for s in (stack or [])])
        ck([s['id'] for s in stack] == ['zoom', 'appear', 'snaps', 'units', 'capture', 'help'],
           "in order: %s" % [s['id'] for s in stack])
        xs = set(s['x'] for s in stack)
        ys = [s['y'] for s in stack]
        ck(len(xs) == 1, "all on one column (x=%s) -- a vertical stack, not a row" % list(xs))
        ck(ys == sorted(ys) and ys[-1] > ys[0],
           "stacked downwards (%s)" % ys)
        geom = await page.evaluate("""()=>{
          const rail=document.getElementById('a3d-rail');
          const tabs=rail.querySelectorAll('.a3d-railbtn');
          const help=rail.querySelector('.fl-help');
          const box=document.getElementById('a3d-railutil');
          const rr=rail.getBoundingClientRect(), br=box.getBoundingClientRect();
          let lastTab=0;
          tabs.forEach(t=>{const r=t.getBoundingClientRect();
            if(r.height>2&&r.bottom>lastTab)lastTab=r.bottom;});
          return {railBottom:rr.bottom, stackTop:br.top, stackBottom:br.bottom,
                  lastTabBottom:lastTab,
                  helpPresent:!!help};}""")
        ck(geom['stackTop'] > geom['lastTabBottom'],
           "below the File/Assets tabs (stack starts at %d, tabs end at %d)"
           % (round(geom['stackTop']), round(geom['lastTabBottom'])))
        ck(geom['railBottom'] - geom['stackBottom'] < 120,
           "and hard against the bottom of the rail (%d px of slack)"
           % round(geom['railBottom'] - geom['stackBottom']))
        # V85: the check this replaces asserted the dead "A?" button was kept below the stack.
        # It is gone, and its job is now the stack's own sixth entry.
        ck(geom['helpPresent'] is False,
           "and no leftover 'A?' button under it (%s) -- it was never a shortcuts button, it "
           "had no handler at all" % geom['helpPresent'])

        print("\n-- 2. every menu opens fully ON SCREEN")
        for mid, want in (('zoom', 3), ('appear', 4), ('snaps', 0), ('units', 3)):
            p = await page.evaluate("(m)=>window.__a3dRailOpen(m)", mid)
            ck(p is not None and p['onScreen'] is True,
               "%s: opens inside the window (l%d t%d r%d b%d) -- V70's dock carets once opened at "
               "top 1109 in a 950px window while every state check passed"
               % (mid, p['left'], p['top'], p['right'], p['bottom']) if p else "%s: did not open" % mid)
            ck(len(p['items']) == want,
               "   and carries %d action row(s) (%s)"
               % (want, [i['label'] for i in p['items']]))
            await page.evaluate("()=>document.body.click()")
            await page.wait_for_timeout(120)
        snaps = await page.evaluate("()=>window.__a3dRailOpen('snaps')")
        ck([f['spec'] for f in snaps['fields']]
           == ['snap:point', 'snap:grid', 'snap:ortho', 'snap:size'],
           "Snaps carries its four fields (%s)" % [f['spec'] for f in snaps['fields']])
        await page.evaluate("()=>document.body.click()")

        print("\n-- 3. Zoom does what it says, measured on the camera")
        await page.evaluate("""()=>{
          window.__a3dTestSetObjs([]);
          window.__a3dWall([[0,0],[26,0],[26,18],[0,18]],0.3,3,'center',true);
          window.__a3dWall([[60,60],[64,60]],0.3,3,'center',false);
          window.__a3dSetPlanView();}""")
        await page.wait_for_timeout(600)
        await page.evaluate("()=>window.__a3dRailOpen('zoom')")
        d0 = await page.evaluate("()=>window.__a3dState().cam.dist")
        ck(await page.evaluate("()=>window.__a3dRailClick('zoom:extents')") is True,
           "Zoom extents clicks")
        await page.wait_for_timeout(500)
        d1 = await page.evaluate("()=>window.__a3dState().cam.dist")
        inside = await page.evaluate("""()=>{
          const bb=window.__a3dWorldBounds(null), s=window.__a3dSafeViewRect();
          const xs=[],ys=[];
          for(let i=0;i<8;i++){
            const q=window.__a3dProject([i&1?bb.mx[0]:bb.mn[0],i&2?bb.mx[1]:bb.mn[1],
                                         i&4?bb.mx[2]:bb.mn[2]]);
            xs.push(q.x);ys.push(q.y);}
          return Math.min(...xs)>=s.x-1&&Math.max(...xs)<=s.x+s.w+1&&
                 Math.min(...ys)>=s.y-1&&Math.max(...ys)<=s.y+s.h+1;}""")
        ck(d1 != d0 and inside,
           "and the whole model lands inside the V79 safe rectangle (dist %.1f -> %.1f)"
           % (d0, d1))

        print("\n-- 4. Zoom window is a real gesture, and it disarms")
        await page.evaluate("()=>window.__a3dRailOpen('zoom')")
        ck(await page.evaluate("()=>window.__a3dRailClick('zoom:window')") is True,
           "Zoom window clicks")
        await page.wait_for_timeout(300)
        ck(await page.evaluate("()=>window.__a3dZoomWindowArmed()") is True, "and arms")
        rect = await page.evaluate("()=>window.__a3dCanvasRect()")
        dBefore = await page.evaluate("()=>window.__a3dState().cam.dist")
        await page.mouse.move(rect['left'] + 400, rect['top'] + 280)
        await page.mouse.down()
        await page.mouse.move(rect['left'] + 570, rect['top'] + 400, steps=8)
        await page.mouse.up()
        await page.wait_for_timeout(550)
        dAfter = await page.evaluate("()=>window.__a3dState().cam.dist")
        ck(dAfter < dBefore,
           "dragging a rectangle zooms IN to it (dist %.1f -> %.1f)" % (dBefore, dAfter))
        ck(await page.evaluate("()=>window.__a3dZoomWindowArmed()") is False,
           "and it disarms afterwards -- a modal view operation left armed silently eats the "
           "user's next click on the drawing")

        print("\n-- 5. Appearance reaches the render mode and the interface")
        await page.evaluate("()=>window.__a3dRailOpen('appear')")
        await page.evaluate("()=>window.__a3dRailClick('appear:presentation')")
        await page.wait_for_timeout(400)
        ck(await page.evaluate("()=>!!window.__a3dPresentMode()") is True,
           "Presentation switches the V52a render mode")
        marked = await page.evaluate("()=>window.__a3dRailOpen('appear')")
        await page.wait_for_timeout(150)
        pres_on = [i for i in marked['items'] if i['label'] == 'Presentation' and i['on']]
        ck(len(pres_on) == 1, "and the menu marks it as current")
        await page.evaluate("()=>window.__a3dRailClick('appear:technical')")
        await page.wait_for_timeout(350)
        ck(await page.evaluate("()=>!!window.__a3dPresentMode()") is False, "Technical switches back")
        await page.evaluate("()=>window.__a3dRailOpen('appear')")
        await page.evaluate("()=>window.__a3dRailClick('appear:light')")
        await page.wait_for_timeout(350)
        # AMENDED FOR V121b: the whiteboard's theme button, whose key this shared, went in V114 and
        # nothing read the key after; the theme is the app's own acad3dTheme now, read at every start.
        theme = await page.evaluate("""()=>({cls:document.body.classList.contains('light-theme'),
          stored:localStorage.getItem('acad3dTheme'),old:localStorage.getItem('canvas-theme')});""")
        ck(theme['cls'] is True and theme['stored'] == 'light' and theme['old'] is None,
           "Light switches the interface AND persists under the app's own key, acad3dTheme, not the "
           "whiteboard's canvas-theme (%s)" % theme)
        await page.evaluate("()=>window.__a3dRailOpen('appear')")
        await page.evaluate("()=>window.__a3dRailClick('appear:dark')")
        await page.wait_for_timeout(300)
        ck(await page.evaluate("()=>!document.body.classList.contains('light-theme')") is True,
           "and Dark switches back")

        print("\n-- 6. Snaps and Units reach the state the rest of the app reads")
        before = await page.evaluate("()=>window.__a3dSnapState()")
        await page.evaluate("()=>window.__a3dRailOpen('snaps')")
        await page.evaluate("()=>window.__a3dRailSet('snap:grid',true)")
        await page.evaluate("()=>window.__a3dRailSet('snap:ortho',true)")
        await page.evaluate("()=>window.__a3dRailSet('snap:size',0.25)")
        await page.wait_for_timeout(400)
        after = await page.evaluate("()=>window.__a3dSnapState()")
        ck(after['grid'] is True and after['ortho'] is True and after['gridSize'] == 0.25,
           "the three snap toggles and the grid size all land in A3D_SNAP (%s -> %s)"
           % (before, after))
        bad = await page.evaluate("""()=>{
          window.__a3dRailOpen('snaps');
          window.__a3dRailSet('snap:size','abc');
          return window.__a3dSnapState().gridSize;}""")
        ck(bad == 0.25,
           "and an unreadable grid size is refused rather than stored as NaN (%s)" % bad)
        await page.evaluate("()=>{window.__a3dSnapSet({grid:false,ortho:false});}")
        await page.evaluate("()=>window.__a3dRailOpen('units')")
        await page.evaluate("()=>window.__a3dRailClick('units:mm')")
        await page.wait_for_timeout(400)
        ck((await page.evaluate("()=>window.__a3dUnits()"))['key'] == 'mm',
           "Units switches the V77 project display units")
        await page.evaluate("()=>window.__a3dRailOpen('units')")
        await page.evaluate("()=>window.__a3dRailSet('units:dp',2)")
        await page.wait_for_timeout(350)
        ck((await page.evaluate("()=>window.__a3dUnits()"))['dp'] == 2,
           "and the decimals with it")
        await page.evaluate("()=>window.__a3dSetUnits('m',3)")

        print("\n-- 7. Save image produces a file")
        try:
            async with page.expect_download(timeout=6000) as dl_info:
                await page.evaluate("()=>{const b=document.querySelector"
                                    "('[data-a3druact=\"capture\"]');b.click();}")
            dl = await dl_info.value
            ck(dl.suggested_filename.endswith('.png'),
               "a PNG of the viewport downloads (%s) -- the canvas itself, locally, with no server"
               % dl.suggested_filename)
        except Exception as e:
            ck(False, "a PNG of the viewport downloads (%s)" % str(e)[:90])

        print("\n-- 8. it survives a tab round trip, and the audit stays clean")
        for t in ('assets', 'browser'):
            await page.evaluate("(x)=>{const b=document.querySelector"
                                "('#a3d-rail [data-tab=\"'+x+'\"]');b&&b.click();}", t)
            await page.wait_for_timeout(650)
        again = await page.evaluate("()=>window.__a3dRailUtils()")
        ck(again is not None and len(again) == 6,
           "the stack is still there after File/Assets (%d) -- the whiteboard's setTab re-renders "
           "the shell, and V80's observer is what keeps it" % len(again or []))
        ck((await page.evaluate("()=>window.__a3dRailOpen('units')"))['onScreen'] is True,
           "and its menus still open on screen")
        await page.evaluate("()=>document.body.click()")
        a = await page.evaluate("()=>window.__a3dShellAudit()")
        ck(a['ok'] is True,
           "the shell audit is clean with every new control claimed (%d claimed, %s unclaimed)"
           % (a['claimed'], a['unclaimed']))

        print("\n-- 9. Escape backs out of the innermost thing first")
        ck(await open_menu_with_mouse(page, 'zoom') is True,
           "a menu opens on a real mouse click")
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(300)
        ck(await page.evaluate("()=>{const p=document.getElementById('a3d-rupop');"
                               "return !p||!p.classList.contains('open');}") is True,
           "Escape closes it")
        ck(await page.evaluate("()=>!!window.__a3dOn") is True,
           "and does NOT fall through to the app's own Escape handler, which exits the BIM shell "
           "entirely -- measured before this layer consumed the event: one Escape took the whole "
           "workspace down, and the V80 audit caught it by the retired-Canvas blocks reappearing "
           "the moment a3d-mode came off the body")
        await open_menu_with_mouse(page, 'zoom')
        await page.evaluate("()=>window.__a3dRailClick('zoom:window')")
        await page.wait_for_timeout(300)
        ck(await page.evaluate("()=>window.__a3dZoomWindowArmed()") is True,
           "a zoom window arms")
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(350)
        ck(await page.evaluate("()=>window.__a3dZoomWindowArmed()") is False,
           "Escape cancels it -- a modal state with no way out is worse than none")
        ck(await page.evaluate("()=>!!window.__a3dOn") is True,
           "and the workspace is still up afterwards")

        print("")
        ck(not errs, "zero uncaught page errors across every probe (%s)" % (errs or 'none'))
        await browser.close()

    print("\n%d/%d checks passed" % (ck.n - len(ck.failed), ck.n))
    if ck.failed:
        print("RESULT: FAIL")
        for m in ck.failed:
            print("   - " + m)
        return 1
    print("RESULT: PASS")
    return 0


sys.exit(asyncio.run(run()))
