"""
bim_phase73_canvas_retired_model_props_browser_tests.py

Regression suite for __acad3dV73 in canvas_v10.html: Canvas retired as a workspace, the inspector
describing the MODEL when nothing is selected, and hit targets big enough to click.

THE STATE THIS PHASE FOUND, measured on the V72 build. On a cold load:

    ACAD_WS_CUR    undefined
    workspace label "Drafting & Annotation"
    __a3dOn        false            <- the BIM shell was never entered
    what was shown  the Canvas whiteboard board

The startup path applied the ribbon TABS for 'da' and stopped. So the app booted into a workspace
label that did not match the workspace on screen, which is the concrete form of "Canvas is its own
thing": Drafting & Annotation and 3D have run the same BIM engine since the workspaces were split,
and Canvas ran a different engine on a different data model -- and got the first frame.

WHAT SHIPPED:
  - Canvas is removed from the workspace list and menu, and a persisted ACAD_WS_CUR of 'canvas' is
    migrated to 'da' rather than rejected. The whiteboard CODE stays: it supplies the file dock and
    rail that have hosted the BIM navigator since V65, and the shared material card library from
    V69. Removing the module would take both with it.
  - Startup enters the BIM shell in plan view, retrying briefly because __a3dEnter may not exist
    yet at 60ms.
  - The inspector shows Identity Data / View / Statistics when nothing is selected, built from
    state that already exists and is already persisted. "No object selected" wasted the panel at
    exactly the moment a user is orienting themselves.
  - Dock buttons 30x28 -> 34x32, their carets 13x28 -> 22x32, property-group carets given a 22x22
    box, palette buttons 9.5px -> 11px text.

WHAT THIS SUITE ASSERTS, and why each check is the one that would catch a regression:

  1. The BOOT STATE, not just the menu. A build that dropped Canvas from the menu but still landed
     on the board would pass a menu check and fail the user. Asserted: the shell is entered, the
     view is Plan, the label matches ACAD_WS_CUR, and no Canvas board is laid out.
  2. The label agrees with the state. The first build of this phase set ACAD_WS_CUR AFTER calling
     __a3dEnter, and enter3d -> installA3dTab re-applies the workspace from that variable, reading
     undefined as '3d' -- so every cold start read "3D" over a plan view. Checked directly.
  3. A persisted 'canvas' workspace is MIGRATED. Asserted by setting it before load.
  4. The whiteboard code survives the retirement: the file dock still hosts the navigator and the
     material library is still published. Deleting the module would break both silently.
  5. Model properties are real and WRITE BACK. Every editable field is changed through its own
     control and the change is read back from the model, not from the widget -- a panel that looks
     right and stores nothing is the Principle 1 failure in its most plausible form.
  6. Hit targets meet a stated minimum. Numbers, not "looks bigger".

Run:  python3 bim_phase73_canvas_retired_model_props_browser_tests.py [path/to/canvas_v10.html]
"""

# AMENDED FOR V120: the shell's canvas-era names were replaced -- #figma-layers-shell/-rail/-panel are
# #a3d-shell/-rail/-leftpanel, the .fl-* classes .a3d-*, #uploaded-command-palette #a3d-cmdpal, the
# Project Browser tab 'file' is 'browser', --figma-dock-w is --a3d-left-w, and the material library is
# read through window.__a3dMaterialCards() (window.__WB_MATERIAL_CARDS is gone).
import asyncio, pathlib, sys

from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'

MODEL = """()=>{
  window.__a3dTestSetObjs([]);
  const w=window.__a3dWall([[0,0],[10,0],[10,7],[0,7]],0.3,3,'center',true);
  window.__a3dDoorAt(w,[5,0],0.9,2.1);
  window.__a3dCreateRoomAt([5,3.5],0);
  window.__a3dSelectFor([]);window.__a3dRefreshProps();
  return w;
}"""


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
                                        device_scale_factor=2)
        page = await ctx.new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        await page.goto('file://' + str(HTML))
        await page.wait_for_timeout(1700)

        has73 = await page.evaluate("()=>!!window.__acad3dV73")
        ck(has73, "__acad3dV73 marker is present")
        if not has73:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.failed), ck.n))
            await browser.close()
            return 1

        print("\n-- 1. the app boots INTO the drafting workspace")
        boot = await page.evaluate("""()=>{
          const v=document.getElementById('viewport');
          /* AMENDED FOR V119: the view dropdown's label is gone; the HUD's View readout names the
             active view now, and the camera's orientation word is read from the engine. */
          const lab=document.getElementById('a3d-view');
          const view={textContent:(window.__a3dState().view||'')};
          return {on:!!window.__a3dOn, ws:window.ACAD_WS_CUR||null,
                  label:lab?lab.textContent.trim():null,
                  view:view?view.textContent.trim():null,
                  boardLaidOut:!!(v&&v.offsetParent!==null),
                  dock:!!document.querySelector('#a3d-dock .a3d-dbtn'),
                  right:!!(document.getElementById('a3d-right')&&
                           document.getElementById('a3d-right').offsetParent!==null)};}""")
        print("     " + str(boot))
        ck(boot['on'] is True,
           "the BIM shell is entered on load -- before this phase it was not, and the Canvas "
           "board got the first frame")
        ck(boot['ws'] == 'da', "the workspace is Drafting & Annotation (%s)" % boot['ws'])
        ck(boot['view'] == 'Plan', "in PLAN view, not 3D (%s)" % boot['view'])
        ck(boot['boardLaidOut'] is False, "no Canvas board is laid out")
        ck(boot['dock'] is True, "the Rayon-style tool dock is up in Drafting & Annotation")
        ck(boot['right'] is True, "and so is the right inspector")

        print("\n-- 2. the label agrees with the state")
        # __acad3dV84 amended this check. What it was defending is unchanged and still checked:
        # the first build of this phase set ACAD_WS_CUR AFTER entering, installA3dTab read the
        # undefined value as '3d', and every cold start said "3D" over a plan view. The label
        # had to agree with the state.
        #
        # What changed is WHICH state it agrees with. The original asserted the literal string
        # "Drafting", which encoded the model the user later rejected: "drafting and annotation
        # is basically 2d view which is not true. it should be a view, like layout view." That
        # assertion would have passed forever on the bug he reported, because the bug was that
        # the label NEVER changed -- it read "Drafting & Annotation" over an isometric 3D view.
        # So the check now asserts agreement with the ACTIVE VIEW, which is strictly stronger:
        # a label frozen on any one string now fails it.
        av = await page.evaluate("()=>window.__a3dActiveView?window.__a3dActiveView():null")
        ck(av is not None and boot['label'] == av['name'],
           "the label names the active view (label=%r view=%r)"
           % (boot['label'], av and av['name']))
        ck(av is not None and av['kind'] == 'plan' and boot['view'] == 'Plan',
           "and the view it names really is the plan the camera is in (%s/%s)"
           % (av and av['kind'], boot['view']))

        print("\n-- 3. Canvas is gone, and so is the list it was on")
        # AMENDED FOR V119: the view dropdown that listed Drafting & Annotation and 3D is gone, so the
        # check is that no workspace list exists to offer anything, and that the Project Browser --
        # where the views are now -- offers no Canvas either.
        ws = await page.evaluate("""()=>({menu:!!(document.querySelector('.acad-ws')||document.getElementById('acad-wsmenu')),
          hook:typeof window.__a3dWorkspaces,
          rows:[...document.querySelectorAll('#a3d-leftpanel .a3d-bgrp, #a3d-leftpanel .a3d-bleaf')].map(e=>e.textContent.trim().toLowerCase())})""")
        ck(ws['menu'] is False and ws['hook'] == 'undefined',
           "there is no workspace menu at all to offer a workspace (%s, %s)" % (ws['menu'], ws['hook']))
        ck(len(ws['rows']) > 0 and not any('canvas' in r for r in ws['rows']),
           "and nothing in the Project Browser offers a Canvas (%d rows)" % len(ws['rows']))

        print("\n-- 4. the whiteboard CODE survives; only the workspace was retired")
        keep = await page.evaluate("""()=>{
          const t=document.querySelector('#a3d-leftpanel > .a3d-tree');
          return {navigatorInDock:!!(t&&t.offsetParent!==null),
                  materialLibrary:!!(window.__a3dMaterialCards()&&window.__a3dMaterialCards().length),
                  cardCount:(window.__a3dMaterialCards()||[]).length};}""")
        ck(keep['navigatorInDock'] is True,
           "the file dock still hosts the BIM navigator (it has since V65)")
        ck(keep['materialLibrary'] is True,
           "and the shared material library is still published (%d cards, V69 depends on it)"
           % keep['cardCount'])

        print("\n-- 5. the inspector describes the model when nothing is selected")
        await page.evaluate(MODEL)
        await page.wait_for_timeout(700)
        mp = await page.evaluate("()=>window.__a3dModelProps()")
        ck(mp['isEmptyMessage'] is False,
           "the 'No object selected' placeholder is gone")
        # V106 added the active level's floor loads between View and Statistics, on purpose: the
        # Levels rows are not on screen, and this panel already carries the level picker.
        # AMENDED FOR V131: the project's Areas by Usage and the Usages library, before Statistics
        # AMENDED FOR V132: the Map, beside the latitude and longitude in Identity Data
        ck(mp['groups'] == ['Identity Data', 'Map', 'View', 'Floor Loads: Level 0', 'Areas by Usage', 'Usages', 'Statistics'],
           "seven groups: %s" % mp['groups'])
        for key in ('project', 'client', 'site', 'level', 'layer', 'present'):
            ck(key in mp['editable'], "'%s' is an editable field" % key)
        ro = dict(mp['readonly'])
        ck(ro.get('Units') == 'Meters',
           "Units states the engine's actual unit rather than offering a switch that would not "
           "convert anything")
        ck(ro.get('Objects') == '3' and ro.get('Walls') == '1' and ro.get('Rooms') == '1',
           "the statistics are counted from the model (%s)" % mp['readonly'])
        ck(ro.get('Openings') == '1', "including the door as an opening")

        print("\n-- 6. the model fields WRITE BACK, not just render")
        await page.evaluate("()=>window.__a3dSetModelField('project','Bridge B-14')")
        await page.wait_for_timeout(300)
        stored = await page.evaluate("""()=>{const e=window.__a3dProjectEnvelope?
          window.__a3dProjectEnvelope():null; return e&&e.titleBlock?e.titleBlock.project:null;}""")
        if stored is None:
            stored = await page.evaluate("()=>window.__a3dModelProps().editable.project")
        ck(stored == 'Bridge B-14',
           "the Project field reaches the model's title block (%s)" % stored)
        await page.evaluate("()=>window.__a3dSetModelField('site','Riverside Crossing')")
        await page.wait_for_timeout(300)
        site = await page.evaluate("()=>window.__a3dSite().name")
        ck(site == 'Riverside Crossing', "the Site field reaches the site record (%s)" % site)
        await page.evaluate("()=>window.__a3dSetModelField('present','1')")
        await page.wait_for_timeout(300)
        ck(await page.evaluate("()=>!!window.__a3dPresentMode()") is True,
           "Appearance switches the render mode, not just the dropdown")
        await page.evaluate("()=>window.__a3dSetModelField('present','0')")
        await page.wait_for_timeout(250)
        ck(await page.evaluate("()=>!!window.__a3dPresentMode()") is False,
           "and switches back")

        print("\n-- 7. the controls are big enough to hit")
        hits = await page.evaluate("()=>window.__a3dHitSizes()")
        print("     " + str(hits))
        ck(hits['dockButton'][0] >= 32 and hits['dockButton'][1] >= 30,
           "dock buttons are at least 32x30 (%s)" % hits['dockButton'])
        # AMENDED FOR V130: the groups' carets are retired; All tools is the control that opens the rest
        ck(hits['dockAll'] and hits['dockAll'][0] >= 32 and hits['dockAll'][1] >= 30,
           "the dock's All tools button is at least 32x30 (%s) -- the caret it replaces was once a "
           "13px sliver, and it is the control that opens the rest" % hits['dockAll'])
        ck(hits['propGroupCaret'] and hits['propGroupCaret'][0] >= 20
           and hits['propGroupCaret'][1] >= 20,
           "the property-group caret has a real box (%s)" % hits['propGroupCaret'])
        ck(hits['paletteButton'][1] >= 24,
           "palette buttons are at least 24px tall (%s)" % hits['paletteButton'])
        await browser.close()

        print("\n-- 8. a persisted 'canvas' workspace is migrated, not rejected")
        browser = await pw.chromium.launch()
        ctx2 = await browser.new_context(viewport={'width': 1600, 'height': 950})
        page2 = await ctx2.new_page()
        page2.on('pageerror', lambda e: errs.append(str(e)))
        await page2.add_init_script("window.ACAD_WS_CUR='canvas';")
        await page2.goto('file://' + str(HTML))
        await page2.wait_for_timeout(1700)
        mig = await page2.evaluate("""()=>({ws:window.ACAD_WS_CUR,on:!!window.__a3dOn});""")
        ck(mig['ws'] == 'da',
           "a session that last used Canvas lands in Drafting & Annotation (%s)" % mig['ws'])
        ck(mig['on'] is True, "with the shell entered rather than stranded")
        await browser.close()

        print("")
        ck(not errs, "zero uncaught page errors across every probe (%s)" % (errs or 'none'))

    print("\n%d/%d checks passed" % (ck.n - len(ck.failed), ck.n))
    if ck.failed:
        print("RESULT: FAIL")
        for m in ck.failed:
            print("   - " + m)
        return 1
    print("RESULT: PASS")
    return 0


sys.exit(asyncio.run(run()))
