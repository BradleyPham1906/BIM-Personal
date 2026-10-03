"""
bim_phase70_tool_dock_browser_tests.py

Regression suite for __acad3dV70 in canvas_v10.html: the Rayon-style floating tool dock replaces
the ribbon in the BIM workspace.

WHAT CHANGED AND WHY IT IS RISKY. The reference tool has no ribbon: a floating two-row dock of
grouped icon buttons sits over the drawing, each group with a caret opening the rest of its tools.
Adopting that shape here means standing the ribbon down -- and the ribbon is where every BIM
command lives. A hand-built dock would quietly drop commands, and a command that exists but cannot
be reached is the same failure as one that does not work (Product Principle 1).

So the dock is GENERATED from `A3DR_TABS`, the same registry `renderA3dPanels` renders from: one
group per ribbon TAB (nine groups over two rows), each group showing that tab's headline tools and
its caret listing every action the tab has, still under its panel headings. Buttons carry
`data-a3dr`, so the existing document-level dispatcher wires them by construction -- this phase
adds no new command routing at all.

The ribbon's tab strip and panel row are hidden under `body.a3d-mode` and `--acad-ribbon-h` drops
from 182px to 52px (28 QAT + 24 doctabs), reclaiming 130px of permanent chrome. The QAT and doc
tabs stay: they carry file/undo/redo, the workspace switcher and document switching, and removing
them would leave no way out of this workspace.

WHAT THIS SUITE ASSERTS, and why each check is the one that would catch a regression:

  1. NO COMMAND LOST -- asserted as SET EQUALITY between every action the ribbon registry can
     reach and every action the rendered dock can reach. This is the check the whole phase rests
     on. Counting buttons, or spot-checking a few tools, would both pass a dock that dropped
     Reinforcement or Foundation.
  2. The ribbon is actually gone AND the height contract was updated. Hiding the panels without
     dropping --acad-ribbon-h leaves a 130px empty band that every other surface still positions
     below; asserting the variable alone would pass a build that hid nothing.
  3. The QAT and doc tabs SURVIVE. Without them there is no workspace switcher and no way back to
     Canvas or 2D drafting -- a trap, not a layout.
  4. The caret popover opens ON SCREEN. The first build centred the dock with
     transform:translateX(-50%), and a position:fixed element inside a TRANSFORMED ancestor is
     positioned against that ancestor rather than the viewport -- the popovers rendered hundreds
     of pixels below the window while every state-level check passed. Geometry is therefore
     measured against the window, for a group at each end of each row.
  5. Unimplemented commands are listed but never promoted to the dock's face. The ribbon showed
     them greyed so the toolset's real shape was visible; the dock keeps that, but its visible
     buttons are all working tools.
  6. A dock button actually runs its command, proving the data-a3dr contract still holds after the
     rebuild.
  7. The dock stays inside the drawing area and disappears with the workspace.

Run:  python3 bim_phase70_tool_dock_browser_tests.py [path/to/canvas_v10.html]
"""

# AMENDED FOR V120: the shell's canvas-era names were replaced -- #figma-layers-shell/-rail/-panel are
# #a3d-shell/-rail/-leftpanel, the .fl-* classes .a3d-*, #uploaded-command-palette #a3d-cmdpal, the
# Project Browser tab 'file' is 'browser', --figma-dock-w is --a3d-left-w, and the material library is
# read through window.__a3dMaterialCards() (window.__WB_MATERIAL_CARDS is gone).
import asyncio, pathlib, sys

from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'

ENTER = """()=>{
  window.__a3dEnter();
  window.ACAD_WS_CUR='da';
  window.__a3dTestSetObjs([]);
  window.__a3dSetPlanView&&window.__a3dSetPlanView();
  const w=window.__a3dWall([[0,0],[10,0],[10,7],[0,7]],0.3,3,'center',true);
  window.__a3dSelectFor([w]);window.__a3dRefreshProps();
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
        page = await browser.new_page(viewport={'width': 1600, 'height': 950})
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        await page.goto('file://' + str(HTML))
        await page.wait_for_timeout(900)

        has70 = await page.evaluate("()=>!!window.__acad3dV70")
        ck(has70, "__acad3dV70 marker is present")
        if not has70:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.failed), ck.n))
            await browser.close()
            return 1

        await page.evaluate(ENTER)
        await page.wait_for_timeout(900)

        print("\n-- 1. no command was lost in the rebuild")
        ribbon = await page.evaluate("()=>window.__a3dRibbonActions()")
        # AMENDED FOR V128: the dock's own search popover is gone -- its magnifier opens THE command
        # search, which does not live inside #a3d-dock. A tool is reachable from the dock when some
        # discipline's dock shows it, or when the search the magnifier opens finds it.
        dock = await page.evaluate("""()=>{
          var out={},cur=window.__a3dDiscipline();
          window.__a3dDisciplines().forEach(function(d){window.__a3dSetDiscipline(d.id);
            window.__a3dDockActions().forEach(function(a){out[a]=1;});});
          window.__a3dSetDiscipline(cur);
          /* AMENDED FOR V130: the dock holds the pinned few; every tool is a row of the Tools and
             shortcuts panel its All tools button opens */
          window.__a3dToolActions().forEach(function(a){out[a]=1;});
          return Object.keys(out).sort();}""")
        missing = sorted(set(ribbon) - set(dock))
        extra = sorted(set(dock) - set(ribbon))
        ck(len(ribbon) > 50,
           "the ribbon registry is non-trivial (%d actions) -- a shrunken registry would make "
           "this comparison vacuous" % len(ribbon))
        ck(not missing,
           "every ribbon action is reachable from the dock (missing: %s)" % (missing or 'none'))
        ck(not extra,
           "and the dock invents none of its own (extra: %s)" % (extra or 'none'))
        ck(sorted(ribbon) == sorted(dock),
           "the two sets are identical, %d actions each" % len(ribbon))
        # Since V71 the dock's GROUPS are filtered by discipline, so this equality holds because
        # the command search spans every discipline (since V128, the one command search). That is the design: the filter can be
        # aggressive precisely because search never lets a tool fall out of reach.

        print("\n-- 2. the ribbon is gone and the height contract was updated")
        rib = await page.evaluate("""()=>{
          const p=document.getElementById('acad-panels'),t=document.getElementById('acad-tabs');
          return {panelsShown:!!(p&&p.offsetParent!==null),
                  tabsShown:!!(t&&t.offsetParent!==null),
                  h:getComputedStyle(document.body).getPropertyValue('--a3d-top-h').trim()};}""")
        ck(rib['panelsShown'] is False, "the ribbon panel row is not laid out in BIM mode")
        ck(rib['tabsShown'] is False, "nor the ribbon tab strip")
        ck(rib['h'] == '52px',
           "--a3d-top-h (V120: --acad-ribbon-h) is 52px (28 QAT + 24 doctabs), so nothing below it is "
           "positioned against a band that is no longer there (%s)" % rib['h'])
        shell = await page.evaluate("""()=>{const s=document.getElementById('acad3d');
          return s?Math.round(s.getBoundingClientRect().top):null;}""")
        ck(shell == 52,
           "and the BIM shell actually starts at that line (top=%s)" % shell)

        print("\n-- 3. the way out of the workspace survives")
        out = await page.evaluate("""()=>{
          const q=document.getElementById('acad-qat'),d=document.getElementById('acad-doctabs');
          /* AMENDED FOR V119: the view dropdown is gone. What kept this mode from being a trap was a
             way to change views, and that is the Project Browser's views and the status bar's 3D
             switch now -- both must be on screen. */
          const pv=document.querySelector('#a3d-leftpanel [data-a3dbview3d]');
          const sb=document.getElementById('a3d-flip');
          return {qat:!!(q&&q.offsetParent!==null),
                  doctabs:!!(d&&d.offsetParent!==null),
                  wsSwitcher:!!(pv&&pv.offsetParent!==null&&sb&&sb.offsetParent!==null)};}""")
        ck(out['qat'] is True, "the QAT strip (file, undo, redo) is still on screen")
        ck(out['wsSwitcher'] is True,
           "and a way to change views with it -- the Project Browser's views and the status bar's 3D "
           "switch; without one this mode would be a trap")
        ck(out['doctabs'] is True, "document tabs survive too")

        print("\n-- 4. the dock's shape, and its popovers land ON SCREEN")
        info = await page.evaluate("()=>window.__a3dDockInfo()")
        ck(info is not None and info['visible'] is True, "the dock is rendered and visible")
        # AMENDED FOR V71. This phase shipped a fixed [[5],[4]] layout and nine always-present
        # groups. V71 made the rows COMPUTED and added a discipline filter, so the counts here
        # are no longer constants -- asserting "== 2 rows" would now be asserting the bug V71
        # fixed. What still has to hold is the shape: a leading __disc group carrying the
        # discipline selector and search, then one caret-bearing group per visible tab.
        # AMENDED FOR V130. The owner: "this tool bar is very crowded ... in the main screen only show
        # the keys one (those that most likely use the most)". The dock is ONE row: the discipline,
        # the tools pinned for it, All tools and the search. The groups' carets and popovers are
        # retired; a group's full toolset is the Tools and shortcuts panel opened on that group, and
        # the checks below ask the same of it: it opens, lands on screen, and lists the tools.
        pins = [g for g in info['groups'] if g['id'] == '__pins']
        ck(info['rows'] == 1, "the dock is one row (%d)" % info['rows'])
        ck(len(pins) == 1 and 1 <= pins[0]['buttons'] <= 12,
           "holding the pinned tools, one to twelve (%s)" % [g['buttons'] for g in pins])
        ck(info['insideViewport'] is True,
           "the dock sits inside the drawing area, not over the panels or off the bottom")

        for gid in ('arch', 'a3dmodify', 'a3dinsert', 'a3dmanage'):
            opened = await page.evaluate("(g)=>window.__a3dDockOpenGroup(g)", gid)
            await page.wait_for_timeout(220)
            geom = await page.evaluate("""(g)=>{var p=document.getElementById('a3d-rupop'),r=p.getBoundingClientRect();
              return {open:p.classList.contains('open'),left:Math.round(r.left),top:Math.round(r.top),right:Math.round(r.right),bottom:Math.round(r.bottom),
                onScreen:r.left>=0&&r.top>=0&&r.right<=window.innerWidth&&r.bottom<=window.innerHeight,
                items:[...p.querySelectorAll('.a3d-rktool[data-rkg="tool:'+g+'"]')].filter(e=>e.offsetParent!==null).length};}""", gid)
            ck(opened is True and geom['open'] is True, "the '%s' group opens in the tools panel" % gid)
            ck(geom['onScreen'] is True,
               "and it lands fully on screen (%s: l=%d t=%d r=%d b=%d)"
               % (gid, geom['left'], geom['top'], geom['right'], geom['bottom']))
            ck(geom['items'] > 0, "with %d tools listed in it" % geom['items'])
            await page.evaluate("()=>{document.body.click();}")
            await page.wait_for_timeout(150)

        closed = await page.evaluate("()=>document.getElementById('a3d-rupop').classList.contains('open')")
        ck(closed is False, "clicking away closes it")

        print("\n-- 5. unimplemented tools are listed, never promoted")
        ck(info['unimplementedOnFace'] == 0,
           "no unimplemented command sits on the dock's visible face (%d)"
           % info['unimplementedOnFace'])
        # Structure is a DISCIPLINE tab since V71, so it is only in the dock while that
        # discipline is active. Switching to it is part of the check now.
        await page.evaluate("()=>window.__a3dSetDiscipline('struct')")
        await page.wait_for_timeout(300)
        await page.evaluate("()=>window.__a3dDockOpenGroup('struct')")
        await page.wait_for_timeout(220)
        # AMENDED FOR V130: listed greyed in the tools panel, opened on the Structure group
        greyed = await page.evaluate("""()=>[...document.querySelectorAll('#a3d-rupop .a3d-rktool.off[data-rkg="tool:struct"]')]
          .filter(e=>e.offsetParent!==null&&e.querySelector('.a3d-rkrun').disabled).length""")
        ck(greyed > 0,
           "but Structure's unimplemented tools are still listed greyed in its group of the tools panel (%d), "
           "so the toolset's real shape stays visible" % greyed)
        await page.evaluate("()=>{document.body.click();window.__a3dSetDiscipline('arch');}")
        await page.wait_for_timeout(250)

        print("\n-- 6. a dock button actually runs its command")
        # __a3dSketch(tool,pts) is a BUILDER, not a getter: calling it bare starts a tool named
        # undefined and returns null, which reads exactly like "no tool active". The first run of
        # this suite failed against working code for that reason. __a3dActiveSketchTool is the
        # read-only probe.
        before = await page.evaluate("()=>window.__a3dActiveSketchTool()")
        # AMENDED FOR V130: Rectangle is not among the pinned few; Polyline is
        ran = await page.evaluate("""()=>{
          const b=document.querySelector('#a3d-dock .a3d-dbtn[data-a3dr=\"s:poly\"]');
          if(!b)return null; b.click(); return true;}""")
        await page.wait_for_timeout(350)
        after = await page.evaluate("()=>window.__a3dActiveSketchTool()")
        ck(ran is True, "the Polyline sketch tool has a dock button")
        ck(before is None, "no sketch tool is armed beforehand")
        ck(after == 'poly',
           "and clicking it arms the Polyline tool (%s -> %s) -- the data-a3dr contract survived "
           "the rebuild, with no new routing added" % (before, after))

        # AMENDED FOR V120: section 7, "the dock belongs to the workspace" (leaving BIM gave the ribbon
        # back), is retired: the exit and the ribbon are both gone.

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
