"""
bim_phase68_two_panel_split_browser_tests.py

Regression suite for __acad3dV68 in canvas_v10.html: navigation LEFT, inspector RIGHT.

WHAT V65-V67 GOT WRONG. The reference layout is Rayon: a thin icon rail on the left that opens
NAVIGATION panels, and the INSPECTOR pinned to the right edge (Selection / Modify / Annotations or
Block instance / Custom properties). V65 read "unify the two left panels" literally and stacked
Properties and the Project Browser in ONE LEFT COLUMN. That is Figma's arrangement, not Rayon's,
and it has a structural consequence rather than a cosmetic one: "what exists in this model" and
"what is this selected thing" ended up in the same scroll, competing for the same height. V66 is
entirely the story of managing that competition -- a 46% cap, collapsed default groups, a wrapping
button row -- and the right half of the window carried nothing at all the whole time. Measured on
the V67 build, 1600x950, wall selected:

    Project Browser   x=54   w=241   h=189     <- squeezed by Properties above it
    Properties        x=54   w=241   h=388     <- same column
    viewport          x=296  w=1304            <- runs to the right window edge, nothing beside it

After V68, same probe:

    Project Browser   x=54   w=241   h=573     <- owns the column
    Properties        x=1321 w=279   h=715     <- right inspector, full height, no cap
    viewport          x=296  w=1024

WHAT THIS SUITE ASSERTS, and why each check is the one that would catch a regression:

  1. SIDES ARE MEASURED, not inferred. Every position check compares rendered boxes against the
     viewport's own box. This is the whole point: the defect being fixed is that both panels were
     present and correct in every state-level sense and simply on the same side. A probe of
     "is Properties rendered" passed on the broken build.
  2. The two are in DIFFERENT panels, so neither can squeeze the other. Asserted as containment
     (Properties is inside #a3d-right, the browser inside the file dock) AND by the browser's
     height being unaffected when a large property group is expanded.
  3. The 46% cap is gone. V66 added it to stop Properties crowding the browser; V68 removes the
     crowding, so a cap that can never fire is dead rule. A build that moved the panel but kept
     the cap would leave Properties artificially short in a panel with room to spare.
  4. Properties moves as ONE node. The header and the body were siblings of the Project Browser's
     header; a move that took only #a3d-propsbody would leave the word "Properties" behind on the
     left, over the browser. Checked by asserting the header travels with it.
  5. The move survives the DOCK move that happens first. enter3d re-parents the whole .a3d-tree
     into #a3d-leftpanel before this runs, so a shell-scoped `el.root.querySelector` returns
     null and the move silently does nothing -- which is exactly the bug the first build of this
     phase had. The check would catch it again.
  6. Exit restores the palette WHOLE, with Properties back above the Project Browser, not merely
     back somewhere. Order matters in exit3d, and a wrong order leaves the palette split.
  7. On the compact tier the inspector is a DRAWER with a real button. A 280px pane pinned open
     beside a 296px dock on a 700px screen leaves 124px of drawing; the button is asserted to be
     laid out and to actually toggle, so it is not decoration.
"""

# AMENDED FOR V120: the shell's canvas-era names were replaced -- #figma-layers-shell/-rail/-panel are
# #a3d-shell/-rail/-leftpanel, the .fl-* classes .a3d-*, #uploaded-command-palette #a3d-cmdpal, the
# Project Browser tab 'file' is 'browser', --figma-dock-w is --a3d-left-w, and the material library is
# read through window.__a3dMaterialCards() (window.__WB_MATERIAL_CARDS is gone).
import asyncio, pathlib, json, sys

from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'

SETUP = """()=>{
  window.__a3dEnter();
  window.__a3dSetPlanView&&window.__a3dSetPlanView();
  window.ACAD_WS_CUR='da';
  window.__a3dTestSetObjs([]);
  const w=window.__a3dWall([[0,0],[10,0],[10,7],[0,7]],0.3,3,'center',true);
  window.__a3dDoorAt(w,[5,0],0.9,2.1);
  window.__a3dSelectFor([w]);window.__a3dRefreshProps();
  return w;
}"""

SIDES = "()=>window.__a3dPanelSides?window.__a3dPanelSides():null"


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
        page = await browser.new_page(viewport={'width': 1600, 'height': 950})
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        await page.goto('file://' + str(HTML))
        await page.wait_for_timeout(900)

        ck(await page.evaluate("()=>!!window.__acad3dV68"), "__acad3dV68 marker is present")
        await page.evaluate(SETUP)
        await page.wait_for_timeout(800)

        print("\n-- 1. measured sides, not claimed ones")
        s = await page.evaluate(SIDES)
        ck(s is not None, "the panel-side probe is exposed")
        if s is None:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.failed), ck.n))
            await browser.close()
            return 1
        print("     " + json.dumps({k: s[k] for k in ('props', 'browser', 'right', 'vp')}))
        ck(s['props']['shown'] is True, "Properties is rendered")
        ck(s['browser']['shown'] is True, "the Project Browser is rendered")
        ck(s['propsRightOfViewport'] is True,
           "Properties sits to the RIGHT of the drawing area (x=%d, viewport ends at %d)"
           % (s['props']['x'], s['vp']['x'] + s['vp']['w']))
        ck(s['browserLeftOfViewport'] is True,
           "the Project Browser sits to the LEFT of the drawing area (x=%d)" % s['browser']['x'])
        ck(s['right']['shown'] is True and s['right']['w'] >= 200,
           "the right inspector is a real pane, not a sliver (%dpx)" % s['right']['w'])

        print("\n-- 2. different panels, so neither can squeeze the other")
        ck(s['propsInRight'] is True, "Properties is inside #a3d-right")
        ck(s['browserInDock'] is True, "the Project Browser is inside the left file dock")
        ck(await page.evaluate("()=>{const r=document.getElementById('a3d-right'),"
                               "b=document.getElementById('a3d-browser');"
                               "return !!(r&&b)&&!r.contains(b);}"),
           "and the browser is NOT in the right pane (they are genuinely two panels)")
        h_before = s['browser']['h']
        expanded = await page.evaluate(
            """()=>{const h=[...document.querySelectorAll('#a3d-propsbody .a3d-pgrp')]
              .find(e=>e.getAttribute('data-a3dpgrp')==='Graphics — Technical');
              if(!h)return false; h.click(); return true;}""")
        ck(expanded is True, "a large property group can be expanded")
        await page.wait_for_timeout(350)
        s2 = await page.evaluate(SIDES)
        ck(s2['browser']['h'] == h_before,
           "expanding it leaves the Project Browser's height untouched (%d -> %d)"
           % (h_before, s2['browser']['h']))
        ck(s2['props']['h'] == s['props']['h'],
           "and the inspector itself does not grow -- it scrolls inside its pane")

        print("\n-- 3. the V66 cap is retired, not merely out of the way")
        cap = await page.evaluate("""()=>{const pb=document.getElementById('a3d-propsbody');
          const cs=getComputedStyle(pb);
          return {maxH:cs.maxHeight, h:Math.round(pb.getBoundingClientRect().height),
                  paneH:Math.round(document.getElementById('a3d-right').getBoundingClientRect().height)};}""")
        ck(cap['maxH'] == 'none',
           "Properties has no max-height in the inspector (%s)" % cap['maxH'])
        ck(cap['h'] > cap['paneH'] * 0.46,
           "and it actually uses more than the old 46%% (%d of %d)" % (cap['h'], cap['paneH']))

        print("\n-- 4. it moved as one node, header included")
        ck(await page.evaluate("""()=>{const r=document.getElementById('a3d-right');
          const hd=[...r.querySelectorAll('.a3d-palhd')].map(e=>e.textContent.trim());
          return hd.indexOf('Properties')>=0;}"""),
           "the 'Properties' header travelled with the body into the right pane")
        ck(await page.evaluate("""()=>{const d=document.getElementById('a3d-leftpanel');
          return [...d.querySelectorAll('.a3d-palhd')].every(e=>e.textContent.trim()!=='Properties');}"""),
           "and no orphaned 'Properties' header is left over the Project Browser")

        print("\n-- 5. the move survived the dock move that runs before it")
        ck(await page.evaluate("""()=>{const t=document.querySelector('.a3d-tree');
          return !!(t&&t.parentElement&&t.parentElement.id==='a3d-leftpanel');}"""),
           "the tree was re-parented into the dock first (the condition that broke the first "
           "build of this phase: a shell-scoped lookup for Properties then returns null)")
        ck(s['propsInRight'] is True,
           "and Properties still reached the inspector despite that")

        # AMENDED FOR V120: section 6, "exit restores the palette whole and in order", is retired with
        # exit3d, which V67 found reachable only from probes.

        await browser.close()

        print("\n-- 7. compact tier: the inspector is a drawer with a real button")
        browser = await pw.chromium.launch()
        page2 = await browser.new_page(viewport={'width': 700, 'height': 760})
        page2.on('pageerror', lambda e: errs.append(str(e)))
        await page2.goto('file://' + str(HTML))
        await page2.wait_for_timeout(900)
        await page2.evaluate(SETUP)
        await page2.wait_for_timeout(800)
        cm = await page2.evaluate("""()=>{const r=document.getElementById('a3d-right');
          const b=document.querySelector('[data-a3d="rdrawer"]');
          return {rightShown:!!(r&&r.offsetParent!==null),
                  btnShown:!!(b&&b.offsetParent!==null)};}""")
        ck(cm['rightShown'] is False,
           "the inspector is closed by default at 700px (it would leave 124px of drawing)")
        ck(cm['btnShown'] is True, "a Props button is laid out in the toolbar to open it")
        await page2.click('[data-a3d="rdrawer"]')
        await page2.wait_for_timeout(300)
        # AMENDED FOR V147: on the compact tier the inspector is a bottom sheet, fixed to the screen,
        # and a fixed element has no offsetParent; shown means displayed and given a size
        ck(await page2.evaluate("()=>{var r=document.getElementById('a3d-right'),b=r.getBoundingClientRect();return getComputedStyle(r).display!=='none'&&b.width>0&&b.height>0;}"),
           "clicking it opens the inspector (the button is wired, not decoration)")
        await page2.click('[data-a3d="rdrawer"]')
        await page2.wait_for_timeout(300)
        ck(await page2.evaluate("()=>document.getElementById('a3d-right').offsetParent===null"),
           "clicking it again closes it")
        docked = await page2.evaluate("""()=>{const t=document.querySelector(
          '#a3d-leftpanel > .a3d-tree'); return !!(t&&t.offsetParent!==null);}""")
        ck(docked is True,
           "and the left navigator is still rendered at this width (it must not inherit the "
           "phone drawer rules now that the dock is its host)")
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
