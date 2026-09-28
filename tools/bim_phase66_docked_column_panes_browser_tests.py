"""
bim_phase66_docked_column_panes_browser_tests.py

Regression suite for __acad3dV66 in canvas_v10.html: making the unified left column behave as
SECTION PANES rather than as one long scroll.

THE PROBLEM THIS PHASE FIXED, measured before it was touched. V65 nested the BIM tree
(.a3d-tree) into the Figma dock panel so Properties and Project Browser finally lived in one
column -- the right structure, but with the wrong sizing. The docked override said:

    body.a3d-tree-docked #a3d-leftpanel > .a3d-tree{flex:0 0 auto}
    ... > .a3d-tree #a3d-browser, ... > .a3d-tree #a3d-propsbody{overflow:visible;max-height:none}

i.e. the tree's two inner scroll regions were deliberately dissolved so the column would scroll
once. The consequence is arithmetic: Properties is content-sized, and a selected wall renders
seven parameter groups. Measured with a 4-segment wall selected, 1600x950 viewport:

    panel viewport            768px
    Properties section        y=251 -> y=1623   (1372px tall)
    Project Browser header    y=1623            (855px BELOW the fold)

So selecting anything pushed the navigator off screen entirely. The undocked palette had never
had this problem -- its own CSS caps .a3d-propsbody at max-height:46% with its own scrollbar and
gives .a3d-browser flex:1 1 auto -- so the fix is to stop overriding that and let the docked
column inherit the sizing the palette already got right.

Two smaller defects fell out of the same measurement and are fixed here too:

  - The two Phase 51 appearance groups ('Graphics - Technical', 'Graphics - Presentation') are
    7-9 rows each and were absent from A3D_PROP_GROUPS_OPEN, whose lookup is
    `A3D_PROP_GROUPS_OPEN[name]!==false` -- absent means OPEN. They account for ~490px of the
    1372px. They are override editors, opened deliberately, not read at a glance like
    Constraints/Dimensions, so they now default closed. The user's toggle still persists for the
    session.
  - The Project Browser header carries seven action buttons (+View +Sht +Lvl +Bldg +Lyr +Fam
    Imp). That row fit on the title line at the palette's 268px; at the dock's 296px with the
    heavier docked title style it clipped +Fam and Imp off the right edge -- controls that exist
    but cannot be clicked, which is a Principle 1 violation. The header now wraps.

WHAT THIS SUITE ASSERTS, and why each check is the one that would catch a regression:

  1. The column does not scroll as one list, and Properties DOES scroll internally. These two
     together are the invariant. Either one alone can be satisfied by an accident (an empty
     selection; a fixed height that clips content), so both are checked with a wall selected.
  2. Project Browser is on screen and keeps a usable height. This is the symptom the user
     reported; it is asserted directly rather than inferred from the CSS.
  3. Properties is not in this column. SUPERSEDED BY V68, which moved Properties to the right
     inspector -- Rayon's actual arrangement -- so the 46% cap this phase added was retired.
     The check asserts the stronger structural fact the cap was standing in for: the two panels
     cannot compete for height because they are no longer in the same panel.
  4. Expanding a collapsed group does not break 1-3, checked under the worst case rather than
     the default one.
  5. The group click handler still fires. #a3d-propsbody is re-parented on entering 3D; its
     listener is bound directly on that element so it travels, but a future refactor that moves
     the binding to a delegated ancestor would silently kill every group toggle.
  6. No laid-out palette button is clipped by the dock edge. Hidden sections (the Schedule pane
     is display:none until a schedule is opened) are excluded -- unrendered is not unreachable.
  7. The assets tab still scrolls, and exiting 3D still restores the palette. The docked rules
     are scoped to body.a3d-tree-docked and [data-tab="browser"]; this proves the scoping holds in
     both directions rather than leaking overflow:hidden into the Canvas library.
"""

# AMENDED FOR V120: the shell's canvas-era names were replaced -- #figma-layers-shell/-rail/-panel are
# #a3d-shell/-rail/-leftpanel, the .fl-* classes .a3d-*, #uploaded-command-palette #a3d-cmdpal, the
# Project Browser tab 'file' is 'browser', --figma-dock-w is --a3d-left-w, and the material library is
# read through window.__a3dMaterialCards() (window.__WB_MATERIAL_CARDS is gone).
import asyncio, pathlib, json, sys

from playwright.async_api import async_playwright

HTML = pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'

VIEW_W, VIEW_H = 1600, 950

SETUP = """()=>{
  window.__a3dEnter();
  window.__a3dSetPlanView&&window.__a3dSetPlanView();
  window.ACAD_WS_CUR='da';
  window.__a3dTestSetObjs([]);
  const w=window.__a3dWall([[0,0],[10,0],[10,7],[0,7]],0.3,3,'center',true);
  window.__a3dDoorAt(w,[5,0],0.9,2.1);
  window.__a3dCreateRoomAt([5,3.5],0);
  window.__a3dSelectFor([w]);window.__a3dRefreshProps();
  return w;
}"""

GEOM = """()=>{
  const p=document.getElementById('a3d-leftpanel');
  const pb=document.getElementById('a3d-propsbody');
  const br=document.getElementById('a3d-browser');
  const pr=p.getBoundingClientRect();
  // Hidden sections (the Schedule pane is display:none until a schedule is opened) are not
  // "clipped" -- only buttons that are actually laid out can be out of reach.
  const btns=[...document.querySelectorAll('#a3d-leftpanel .a3d-palbtn')]
    .filter(e=>e.offsetParent!==null).map(e=>{
      const r=e.getBoundingClientRect();
      return {t:e.textContent.trim(), inside:r.width>0&&r.right<=pr.right+0.5&&r.left>=pr.left-0.5};
    });
  const grps=[...document.querySelectorAll('#a3d-propsbody .a3d-pgrp')].map(e=>({
    g:e.getAttribute('data-a3dpgrp'),
    open:!!(e.nextElementSibling&&e.nextElementSibling.classList.contains('a3d-pgbody'))}));
  return {
    colScrolls:p.scrollHeight>p.clientHeight+1,
    colClientH:p.clientHeight,
    propsH:Math.round(pb.getBoundingClientRect().height),
    propsScrolls:pb.scrollHeight>pb.clientHeight+1,
    browserH:Math.round(br.getBoundingClientRect().height),
    browserTop:Math.round(br.getBoundingClientRect().top),
    browserInView:br.getBoundingClientRect().top<pr.bottom-40,
    btnsAllInside:btns.every(b=>b.inside),
    btnsClipped:btns.filter(b=>!b.inside).map(b=>b.t),
    groups:grps};
}"""

CLICK_TECH = """()=>{const h=[...document.querySelectorAll('#a3d-propsbody .a3d-pgrp')]
  .find(e=>e.getAttribute('data-a3dpgrp')==='Graphics — Technical');
  if(!h)return false; h.click(); return true;}"""


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
    url = 'file://' + str(HTML)
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page(viewport={'width': VIEW_W, 'height': VIEW_H})
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        await page.goto(url)
        await page.wait_for_timeout(900)

        marker = await page.evaluate("()=>window.__acad3dV66||null")
        ck(marker is not None, "__acad3dV66 marker is present")

        await page.evaluate(SETUP)
        await page.wait_for_timeout(800)

        print("\n-- docked column, wall selected, default group state")
        g = await page.evaluate(GEOM)
        print("     " + json.dumps({k: g[k] for k in
              ('colScrolls', 'colClientH', 'propsH', 'propsScrolls', 'browserH', 'browserTop')}))

        ck(g['colScrolls'] is False,
           "the docked column does not scroll as one long list")
        ck(g['propsScrolls'] is True,
           "Properties scrolls internally instead of pushing the sections below it down")
        ck(g['browserInView'] is True,
           "Project Browser is on screen with a wall selected (top=%d, panel bottom=%d)"
           % (g['browserTop'], g['colClientH']))
        ck(g['browserH'] >= 120,
           "Project Browser keeps at least 120px of usable height (%d)" % g['browserH'])
        # SUPERSEDED BY V68. V66 kept Properties in this column and capped it at 46% so it could
        # not push the Project Browser off screen. V68 moved Properties out of the column
        # entirely, to the right inspector, which achieves the same invariant structurally -- so
        # the cap was retired rather than left as a rule that can never fire. What is asserted
        # now is the stronger fact the cap was standing in for.
        ck(await page.evaluate("()=>{const p=document.getElementById('a3d-propssec'),"
                               "d=document.getElementById('a3d-leftpanel');"
                               "return !!(p&&d)&&!d.contains(p);}"),
           "Properties is not in the left column at all (V68 moved it to the right inspector, "
           "which is why the 46% cap this phase added is gone)")
        ck(g['btnsAllInside'] is True,
           "no laid-out palette button is clipped by the dock edge (clipped: %s)"
           % (g['btnsClipped'] or 'none'))

        print("\n-- property group open/closed defaults")
        by = {x['g']: x['open'] for x in g['groups']}
        ck('Graphics — Technical' in by, "the Graphics - Technical group is rendered")
        ck('Graphics — Presentation' in by, "the Graphics - Presentation group is rendered")
        ck(by.get('Graphics — Technical') is False,
           "Graphics - Technical defaults collapsed")
        ck(by.get('Graphics — Presentation') is False,
           "Graphics - Presentation defaults collapsed")
        ck(by.get('Constraints') is True, "Constraints still defaults open")
        ck(by.get('Dimensions') is True, "Dimensions still defaults open")
        ck(by.get('Identity Data') is True, "Identity Data still defaults open")

        print("\n-- toggling survives the re-parent, and the cap holds when expanded")
        clicked = await page.evaluate(CLICK_TECH)
        ck(clicked is True, "the collapsed group header is clickable")
        await page.wait_for_timeout(350)
        g2 = await page.evaluate(GEOM)
        by2 = {x['g']: x['open'] for x in g2['groups']}
        ck(by2.get('Graphics — Technical') is True,
           "clicking the collapsed header expands it (listener survived the re-parent)")
        ck(g2['colScrolls'] is False,
           "expanding it does not turn the column back into one long scroll")
        ck(g2['browserInView'] is True,
           "Project Browser stays on screen after expanding (top=%d)" % g2['browserTop'])
        ck(g2['browserH'] >= 120,
           "the Project Browser keeps its height when a property group expands (%d) -- since V68 "
           "they are in different panels, so one cannot squeeze the other at all" % g2['browserH'])
        ck(g2['propsScrolls'] is True, "the extra rows are reachable by the inner scroll")
        await page.evaluate(CLICK_TECH)
        await page.wait_for_timeout(250)
        g3 = await page.evaluate(GEOM)
        by3 = {x['g']: x['open'] for x in g3['groups']}
        ck(by3.get('Graphics — Technical') is False,
           "clicking again collapses it (the toggle is symmetric)")

        print("\n-- the docked rules stay scoped")
        await page.evaluate("()=>{document.getElementById('a3d-shell')"
                            ".setAttribute('data-tab','assets');}")
        await page.wait_for_timeout(300)
        ov = await page.evaluate("()=>getComputedStyle("
                                 "document.getElementById('a3d-leftpanel')).overflowY")
        ck(ov in ('auto', 'scroll'),
           "the assets tab keeps the column scrollable (overflow-y: %s)" % ov)
        await page.evaluate("()=>{document.getElementById('a3d-shell')"
                            ".setAttribute('data-tab','browser');}")
        await page.wait_for_timeout(250)
        ov2 = await page.evaluate("()=>getComputedStyle("
                                  "document.getElementById('a3d-leftpanel')).overflowY")
        ck(ov2 == 'hidden',
           "the file tab hands scrolling to the tree's own panes (overflow-y: %s)" % ov2)

        # AMENDED FOR V120: "leaving 3D restores the palette" is retired with exit3d, which V67 found
        # reachable only from probes; there is no leaving to restore anything for.

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
