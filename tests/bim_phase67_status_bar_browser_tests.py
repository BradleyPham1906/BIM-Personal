"""
bim_phase67_status_bar_browser_tests.py

Regression suite for __acad3dV67 in canvas_v10.html: the BIM status bar.

THE PROBLEM THIS PHASE FIXED. Phase 64's audit closed with one documented, deliberately
unresolved shell difference: the 2D workspace has `#acad-status` pinned to the bottom of the
window (hint on the left, coordinates, then GRID / ORTHO / POLAR / OSNAP toggles) and the BIM
workspace had nothing there at all. `#acad-status` is HIDDEN on entering BIM -- correctly, because
its four toggles call `window.cadRun(...)` and read `window.CAD`, the 2D engine's state, so
showing it in BIM would put four controls on screen that do nothing, a Product Principle 1
violation. The result was that the bottom ~26px of the app changed meaning between modes, and the
BIM equivalents were scattered: snap state in a floating pill at left:14px;bottom:14px, the active
tool painted into the canvas at (10,10) over the drawing, the active level only visible if you
scrolled the Project Browser to it, and the cursor coordinates nowhere at all.

WHAT WAS BUILT. The same 26px strip, same background/border/type/toggle language, in the same
screen position -- as the third flex child of `#acad3d` (toolbar / body / status) so it spans the
work area the `--figma-dock-w` contract already defines. It carries BIM's own state only:

    hint (tool or selection)  ...spring...  Level [select]  X/Y/Z  [SNAP][ORTHO][GRID]

Two surfaces were retired into it rather than left alongside it, because duplicates of the same
control are their own Principle 1 problem: the floating snap pill (`#a3d-snappill`, deleted -- the
three buttons moved, keeping their `data-a3dsnap` contract so `syncSnapPill` and its click handler
were untouched) and the canvas-painted tool banner. The navigation pill stays: it carries camera
state, not drawing state, and belongs over the viewport it drives.

WHAT THIS SUITE ASSERTS, and why each check is the one that would catch a regression:

  1. GEOMETRY, not just existence. Height, bottom-alignment to the shell and full shell width are
     asserted numerically. "The same position as the 2D bar" is the actual requirement, and a bar
     that exists but floats mid-viewport satisfies every state check while failing the phase.
  2. The two bars are never both up. `#acad-status` must be hidden while BIM is active and
     restored on exit. Either half alone leaves a mode with two status bars or none.
  3. The bar READS, it does not own. Every field is checked against the engine state behind it
     and after a change made from OUTSIDE the bar -- F8/F3/F9 keystrokes for the snaps, addLevel
     for the level list. A bar wired only to its own buttons passes a click test and still goes
     stale the moment anything else moves.
  4. The bar WRITES. Clicking a snap button changes A3D_SNAP; changing the level select changes
     A3D.activeLevel AND the plane the coordinate read-out solves on. A read-only bar that looks
     interactive is exactly the decorative control Principle 1 forbids.
  5. The coordinate read-out is real. Two different screen points give two different world
     points, the Z figure equals the active level's elevation, and leaving the canvas clears it.
     A hard-coded or frozen read-out passes "is it non-empty" and nothing here.
  6. No duplicate snap surface survives, and the UI-visibility preference still drives something
     real. The pref keeps its stored key ('snappill') so a user who had hidden those controls
     keeps them hidden; if the key had been repointed to a dead selector the checkbox would have
     become decoration.

These checks were verified to FAIL against `canvas_v10.html.bak_phase67_pre` before the suite was
accepted. Run with a path argument to point it at any build:

    python3 bim_phase67_status_bar_browser_tests.py ../canvas_v10.html.bak_phase67_pre
"""

# AMENDED FOR V120: the shell's canvas-era names were replaced -- #figma-layers-shell/-rail/-panel are
# #a3d-shell/-rail/-leftpanel, the .fl-* classes .a3d-*, #uploaded-command-palette #a3d-cmdpal, the
# Project Browser tab 'file' is 'browser', --figma-dock-w is --a3d-left-w, and the material library is
# read through window.__a3dMaterialCards() (window.__WB_MATERIAL_CARDS is gone).
import asyncio, pathlib, re, sys

from playwright.async_api import async_playwright

DEFAULT_HTML = pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'
HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_HTML

VIEW_W, VIEW_H = 1600, 950

ENTER = """()=>{
  window.__a3dEnter();
  window.ACAD_WS_CUR='da';
  window.__a3dTestSetObjs([]);
  const w=window.__a3dWall([[0,0],[10,0],[10,7],[0,7]],0.3,3,'center',true);
  window.__a3dSelectFor([w]);window.__a3dRefreshProps();
  return w;
}"""

BAR = "()=>window.__a3dStatusBar?window.__a3dStatusBar():null"

NUM = re.compile(r'-?\d+\.\d+')


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
        page = await browser.new_page(viewport={'width': VIEW_W, 'height': VIEW_H})
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        await page.goto('file://' + str(HTML))
        await page.wait_for_timeout(900)

        marker = await page.evaluate("()=>window.__acad3dV67||null")
        ck(marker is not None, "__acad3dV67 marker is present")

        await page.evaluate(ENTER)
        await page.wait_for_timeout(700)

        print("\n-- 1. the bar exists where the 2D bar is, with the 2D bar stood down")
        b = await page.evaluate(BAR)
        ck(b is not None, "the BIM status bar is built and exposed")
        if b is None:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.failed), ck.n))
            await browser.close()
            return 1
        ck(b['visible'] is True, "the bar is visible in BIM mode")
        ck(b['height'] == 26,
           "the bar is 26px tall, matching #acad-status exactly (%d)" % b['height'])
        ck(b['atBottomOfShell'] is True, "the bar is flush with the bottom of the BIM shell")
        ck(b['spansShellWidth'] is True, "the bar spans the full width of the work area")
        # __acad3dV113c: V67 asserted the 2D status bar was hidden rather than deleted, because a
        # 2D shell still existed to hand the strip back to. It does not: the engine that drew
        # #acad-status is deleted with the rest of the retired 2D workspace, and section 8 below
        # records why that restore path was unreachable in the first place. Two bars can no longer
        # exist because there is only one bar.
        st2d = await page.evaluate("""()=>{const e=document.getElementById('acad-status');
          if(!e)return null; const r=e.getBoundingClientRect();
          return {display:getComputedStyle(e).display,h:Math.round(r.height),
                  shown:getComputedStyle(e).display!=='none'&&r.height>0};}""")
        ck(st2d is None, "the 2D status bar element is gone, so two bars cannot be drawn at once")
        ck((await page.evaluate("()=>document.querySelectorAll('[id$=\"-statusbar\"],#acad-status').length")) == 1,
           "and the document holds exactly one status bar element")

        print("\n-- 2. the bar reads engine state it does not own")
        snaps0 = await page.evaluate("()=>({point:window.__a3dSnapState?window.__a3dSnapState():null})")
        ck(b['snaps'].get('point') is True,
           "SNAP renders lit, matching A3D_SNAP.point's default of true")
        ck(b['snaps'].get('ortho') is False, "ORTHO renders unlit by default")
        ck(b['snaps'].get('grid') is False, "GRID renders unlit by default")
        for key, code in (('ortho', 'F8'), ('point', 'F3'), ('grid', 'F9')):
            await page.evaluate("(k)=>{window.dispatchEvent(new KeyboardEvent('keydown',"
                                "{key:k,bubbles:true,cancelable:true}));}", code)
            await page.wait_for_timeout(200)
            nb = await page.evaluate(BAR)
            ck(nb['snaps'][key] != b['snaps'][key],
               "%s pressed outside the bar flips its %s button (the bar tracks, it does not own)"
               % (code, key.upper()))
            b = nb

        print("\n-- 3. the bar writes back")
        before = await page.evaluate(BAR)
        await page.evaluate("""()=>{document.querySelector('#a3d-snapgrp [data-a3dsnap=\"grid\"]').click();}""")
        await page.wait_for_timeout(200)
        after = await page.evaluate(BAR)
        ck(after['snaps']['grid'] != before['snaps']['grid'],
           "clicking GRID in the bar changes the state (the button is wired, not painted)")
        gridReal = await page.evaluate("()=>{let s=null;try{s=window.__a3dGridSnapOn?"
                                       "window.__a3dGridSnapOn():null;}catch(e){}return s;}")
        if gridReal is not None:
            ck(gridReal == after['snaps']['grid'], "the engine agrees with the button")

        print("\n-- 4. the level selector is the real level list")
        lvls = await page.evaluate("()=>window.__a3dLevels()")
        bb = await page.evaluate(BAR)
        ck(bb['levelOptions'] == [l['id'] for l in lvls],
           "every level, in model order, is an option (%s)" % bb['levelOptions'])
        active = await page.evaluate("()=>window.__a3dActiveLevel()")
        ck(bb['levelValue'] == active['id'], "the selected option is the active level")
        await page.evaluate("()=>{window.__a3dAddLevel();}")
        await page.wait_for_timeout(300)
        lvls2 = await page.evaluate("()=>window.__a3dLevels()")
        bb2 = await page.evaluate(BAR)
        ck(len(lvls2) == len(lvls) + 1, "a level was added")
        ck(bb2['levelOptions'] == [l['id'] for l in lvls2],
           "a level added from outside the bar appears in it without a manual refresh")
        first_id = lvls2[0]['id']
        await page.select_option('#a3d-stlevel', first_id)
        await page.wait_for_timeout(300)
        active2 = await page.evaluate("()=>window.__a3dActiveLevel()")
        ck(active2['id'] == first_id,
           "changing the select changes the ACTIVE LEVEL, not just the widget")

        print("\n-- 5. the coordinate read-out is solved, not decorative")
        c_out = await page.evaluate(BAR)
        ck(c_out['coords'].strip() == '—',
           "with the cursor off the canvas the read-out is an em dash, not a stale number")
        t1 = await page.evaluate("()=>window.__a3dStatusHoverAt(420,300)")
        t2 = await page.evaluate("()=>window.__a3dStatusHoverAt(900,560)")
        n1, n2 = NUM.findall(t1 or ''), NUM.findall(t2 or '')
        ck(len(n1) == 3, "the read-out carries three figures (%s)" % t1)
        ck(n1 != n2, "two different screen points give two different world points")
        ck(abs(float(n1[2]) - float(active2['elev'])) < 1e-6,
           "the third figure is the ACTIVE LEVEL's elevation, the plane the point was solved on "
           "(%s vs %s)" % (n1[2], active2['elev']))
        await page.evaluate("()=>{window.__a3dSetLevel(window.__a3dLevels()[1].id);}")
        await page.wait_for_timeout(250)
        lvl_b = await page.evaluate("()=>window.__a3dActiveLevel()")
        t3 = await page.evaluate("()=>window.__a3dStatusHoverAt(420,300)")
        n3 = NUM.findall(t3 or '')
        ck(abs(float(n3[2]) - float(lvl_b['elev'])) < 1e-6,
           "switching level moves the plane the read-out solves on (%s -> %s)" % (n1[2], n3[2]))
        await page.evaluate("""()=>{const cv=document.getElementById('a3d-canvas');
          cv.dispatchEvent(new MouseEvent('mouseleave',{bubbles:true}));}""")
        await page.wait_for_timeout(200)
        ck((await page.evaluate(BAR))['coords'].strip() == '—',
           "leaving the canvas clears the read-out rather than freezing the last point")

        print("\n-- 6. no duplicate snap surface, and the preference still bites")
        ck(await page.evaluate("()=>!document.getElementById('a3d-snappill')"),
           "the floating snap pill is gone (its three toggles live in the bar now)")
        # V109 moved the navigation pill into the bar too, on the owner's call: the check is now
        # that the view controls are in the bar and the floating pill is gone.
        ck(await page.evaluate("()=>{var g=document.getElementById('a3d-navgrp');return !!g&&!!g.closest('#a3d-statusbar')&&!document.getElementById('a3d-pill');}"),
           "the navigation controls sit in the status bar (V109), no floating pill")
        await page.evaluate("()=>{window.__a3dSetUIPanelVisible('snappill',false);}")
        await page.wait_for_timeout(200)
        ck(await page.evaluate("()=>document.getElementById('a3d-snapgrp').offsetParent===null"),
           "the stored 'snappill' preference hides the bar's snap group (the key still drives "
           "something real, so an existing hidden preference is honoured)")
        await page.evaluate("()=>{window.__a3dSetUIPanelVisible('snappill',true);}")
        await page.wait_for_timeout(200)
        ck(await page.evaluate("()=>document.getElementById('a3d-snapgrp').offsetParent!==null"),
           "turning it back on restores them")

        print("\n-- 7. the hint tracks what is actually happening")
        h_sel = (await page.evaluate(BAR))['hint']
        ck('Wall_1' in h_sel,
           "with a wall selected the hint names it (%s)" % h_sel)
        ck(':' in h_sel,
           "and gives its Revit-shaped Family : Type, not the internal primitive kind (%s)" % h_sel)
        await page.evaluate("()=>{window.__a3dSelectFor([]);window.__a3dRefreshProps();}")
        await page.wait_for_timeout(250)
        h_none = (await page.evaluate(BAR))['hint']
        ck(h_none.strip() != '' and 'Wall_1' not in h_none,
           "clearing the selection changes the hint rather than leaving the old name (%s)" % h_none)

        # __acad3dV113c: this section used to assert that leaving BIM handed the bottom strip back
        # to a 2D status bar. Measured before deleting it: NOTHING reaches exit3d -- no control
        # emits act === 'exit', and V85 took it out of the Escape chain, writing at the time that
        # "views are the navigation, and there is nothing sensible left to back out TO". So the
        # restore path was reachable only by a probe, which is the V80 lesson exactly. The 2D
        # status bar and the engine that drew it are deleted; there is one bar now.
        print("\n-- 8. there is one status bar, and nothing to hand it back to")
        out = await page.evaluate("""()=>{const bim=document.getElementById('a3d-statusbar');
          const br=bim?bim.getBoundingClientRect():null;
          return {bimShown:!!(bim&&bim.offsetParent!==null),
                  bimBottom:br?Math.round(br.bottom):null,
                  two:!!document.getElementById('acad-status'),
                  bars:document.querySelectorAll('#a3d-statusbar,#acad-status').length};}""")
        ck(out['two'] is False, "the 2D status bar element is gone, not merely hidden")
        ck(out['bars'] == 1, "exactly one status bar exists (%s)" % out['bars'])
        ck(out['bimShown'] is True, "and it is the BIM bar, still showing")
        ck(out['bimBottom'] == VIEW_H,
           "sitting on the bottom edge where it always did (bottom=%s)" % out['bimBottom'])

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
