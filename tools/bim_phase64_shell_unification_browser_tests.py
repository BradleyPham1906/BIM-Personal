"""
bim_phase64_shell_unification_browser_tests.py

Regression suite for __acad3dV64 and __acad3dV65 in canvas_v10.html: making the three workspaces
(Canvas, Drafting & Annotation, 3D) SWITCH rather than STACK (V64), and collapsing the two
competing left panels into ONE column (V65).

THE PROBLEM THIS PHASE FIXED, measured before it was touched. `acadApplyWorkspace()` -- the
function named as though it switches workspaces -- only ever showed and hid ribbon tabs. The
actual surfaces were layered, not exchanged:

    mode      #viewport (Canvas board)      #acad3d (BIM shell)
    canvas    block  1600x754 @ x=0         display:none
    da        block  1600x754 @ x=0   <--   flex 1546x768 @ x=54   (painted OVER it, z-index 9500)
    3d        block  1600x754 @ x=0   <--   flex 1546x768 @ x=54

The Canvas board never hid. Entering Drafting or 3D covered a still-mounted, still-live board
with an opaque shell, so two full-window surfaces were always present, disagreeing about the work
area by 54px of origin and 14px of height. Every "these two panels are fighting" symptom patched
before this (collapsing the file dock on entry; hiding the rail's Props/Layers/Blocks buttons so
a second, disconnected properties panel could not be opened over the BIM one) was a patch on that
one root cause rather than a fix of it.

WHAT THIS SUITE ASSERTS, and why each check is the one that would catch a regression:

  1. EXACTLY ONE work surface is mounted per mode. This is the invariant. A future change that
     re-mounts the board under the shell -- or forgets to restore it on exit -- breaks this and
     nothing else would notice, because a covered surface is invisible by definition.
  2. All three modes agree on the work surface's ORIGIN and WIDTH. The contract is "the drawing
     surface begins where the left dock ends," now expressed once as left:var(--figma-dock-w) and
     honoured by both surfaces instead of only by #acad3d.
  3. The Canvas board survives the round trip EXACTLY -- same world transform matrix, same node
     count, same rendered node sizes -- and does so repeatedly, so nothing accumulates across
     switches. Hiding a transformed, scrollable surface and showing it again is precisely where
     this kind of change usually breaks, so it is checked to the matrix rather than to "it looks
     fine".
  4. No uncaught page error on any transition, in either direction, over repeated cycles.
  5. (V65) The Properties/Project Browser tree is RE-PARENTED into the dock panel on entry and
     restored to its original parent on exit, so the rail selects a subject and that subject's
     sections stack beneath it -- one column -- instead of a second navigator opening beside the
     first. Before V65, opening File or Assets in a BIM workspace put a 242px panel on screen
     beside a 268px tree: 510px of chrome before any drawing surface. It is now 296px.

     Re-parenting is safe here for three reasons that were verified before the change, and each is
     asserted below so a future refactor that breaks one of them fails loudly: every tree child is
     resolved once at buildUI() time into el.* and an element reference survives a move; all five
     tree listeners are bound directly to those nodes rather than delegated from #acad3d; and no
     CSS rule scopes the tree's classes under #acad3d.

     A first attempt at this stacked the Canvas board's own Pages and Layers directly above the
     BIM Properties of a selected room. That is not "united" -- they are two different models
     sharing a scrollbar -- so the rail now switches subject instead, which is also what the tools
     this was modelled on actually do.

WHAT THIS SUITE DELIBERATELY DOES NOT CLAIM, recorded so it is not mistaken for more than it is:

  - The three workspaces still run on SEPARATE MODELS. Drafting and 3D genuinely share one
     (`A3D.*`, two cameras on one engine -- asserted below). Canvas owns a different one
     (`state.nodes/edges/draws/annotations`), and a third (`state.wires`, which carries the
     material/hatch cards) is reachable from neither BIM mode. A sweep of every function body in
     the file finds exactly two touching both `state.*` and `A3D.objs` -- `bootStrip` and
     `enter3d` -- and neither is a data bridge. This phase unified the SHELL, not the model. The
     checks below assert that separation as CURRENT BEHAVIOUR so that a future integration phase
     changes it deliberately and visibly, not by accident.
  - The 754 vs 768 work-surface HEIGHT difference is left in place and is correct, not an
     oversight: Canvas reserves 196px for the AutoCAD status bar and Model/Layout tabs, which the
     BIM shell hides. Those status-bar toggles drive `window.CAD`/`cadRun` -- the 2D engine -- not
     the BIM engine, which has its own snap pill bound to `A3D_SNAP`. Showing that bar in BIM mode
     would put four controls on screen that do nothing there, violating the project's own "real
     tools only" principle. Unifying those two surfaces properly is a separate piece of work.

Run:  python3 bim_phase64_shell_unification_browser_tests.py [path/to/canvas_v10.html]
"""
# AMENDED FOR V120: the shell's canvas-era names were replaced -- #figma-layers-shell/-rail/-panel are
# #a3d-shell/-rail/-leftpanel, the .fl-* classes .a3d-*, #uploaded-command-palette #a3d-cmdpal, the
# Project Browser tab 'file' is 'browser', --figma-dock-w is --a3d-left-w, and the material library is
# read through window.__a3dMaterialCards() (window.__WB_MATERIAL_CARDS is gone).
import asyncio, pathlib, sys
from playwright.async_api import async_playwright

TARGET = sys.argv[1] if len(sys.argv) > 1 else "canvas_v10.html"

TOTAL = [0]
FAILS = []


def check(cond, msg):
    TOTAL[0] += 1
    print(("  PASS  " if cond else "  FAIL  ") + msg)
    if not cond:
        FAILS.append(msg)


PROBE_API = r"""
() => ({
  v64: window.__acad3dV64 || null,
  /* AMENDED FOR V120: window.__a3dExit (V67: reachable only from probes) and window.__acadApplyWorkspace
     (it showed and hid buttons in a ribbon nothing displayed) are gone */
  hasApi: !!(window.__a3dShellGeom && window.__a3dEnter &&
             window.__a3dSetPlanView && window.__a3dSet3DView)
})
"""

# Walks the three workspaces exactly the way the workspace menu does, and records the shell
# geometry plus both models' sizes at each stop.
PROBE_WALK = r"""
() => {
  const out = {};
  const snap = () => {
    const g = window.__a3dShellGeom();
    g.objs3d = (function(){ try { return window.__a3dState().objs.length; } catch(e){ return null; } })();
    g.canvasNodes = (window.state && window.state.nodes) ? window.state.nodes.length : null;
    g.wires2d = (window.state && window.state.wires) ? window.state.wires.length : null;
    return g;
  };

  window.__a3dEnter(); window.__a3dTestSetObjs([]);
  const w = window.__a3dWall([[0,0],[8,0],[8,5],[0,5]], 0.3, 3, 'center', true);
  window.__a3dCreateRoomAt([4,2.5], 0);
  window.__a3dSelectFor([]);

  window.__a3dSetPlanView();
  out.da = snap();

  window.__a3dSet3DView();
  out.threeD = snap();

  /* AMENDED FOR V119: the view dropdown that offered workspaces is gone, so what is recorded is
     whether ANY switcher is left that could offer one. */
  out.workspaceMenu = !!(document.querySelector('.acad-ws') || document.getElementById('acad-wsmenu') || window.__a3dWorkspaces);
  /* __acad3dV113c: the walk used to force a third stop by calling __acadApplyWorkspace('canvas')
     directly, and the suite said so itself -- "the stop above reaches it only by calling
     __acadApplyWorkspace directly". There is no board to switch to now, so the stop is gone and
     what is asserted instead is that nothing of it is left in the document. */
  out.boardGone = !document.getElementById('viewport') && !document.getElementById('world');

  window.__a3dSetPlanView();
  out.backToDa = snap();
  return out;
}
"""

# The Canvas board is a transformed, pannable surface. Hiding and re-showing one is exactly where
# this kind of change breaks, so its restoration is checked to the transform matrix.
PROBE_ROUNDTRIP = r"""
() => {
  const readBoard = () => {
    const vp = document.getElementById('viewport');
    const world = document.getElementById('world');
    const nodes = [...document.querySelectorAll('#world .node')];
    return {
      display: vp ? getComputedStyle(vp).display : 'missing',
      transform: world ? getComputedStyle(world).transform : null,
      nodeCount: nodes.length,
      nodesWithSize: nodes.filter(n => { const b = n.getBoundingClientRect(); return b.width > 0 && b.height > 0; }).length,
      stateNodes: (window.state && window.state.nodes) ? window.state.nodes.length : null
    };
  };
  /* AMENDED FOR V120: there is no exit any more -- V67 found it reachable only from probes -- so
     what is walked is entering again, which must bring nothing back */
  const before = readBoard();
  window.__a3dEnter();
  const during = readBoard();
  const after = readBoard();
  for (let i = 0; i < 3; i++) { window.__a3dEnter(); }
  const afterCycles = readBoard();
  return {before, during, after, afterCycles};
}
"""

# Drafting and 3D must be two cameras on ONE model; Canvas must be untouched by BIM edits.
PROBE_MODEL_SEPARATION = r"""
() => {
  window.__a3dEnter(); window.__a3dTestSetObjs([]);
  const canvasBefore = (window.state && window.state.nodes) ? window.state.nodes.length : null;
  const wiresBefore  = (window.state && window.state.wires) ? window.state.wires.length : null;

  window.__a3dSetPlanView();
  const w = window.__a3dWall([[0,0],[6,0],[6,4],[0,4]], 0.3, 3, 'center', true);
  const inDa = window.__a3dState().objs.length;

  window.__a3dSet3DView();
  const in3d = window.__a3dState().objs.length;

  const canvasAfter = (window.state && window.state.nodes) ? window.state.nodes.length : null;
  const wiresAfter  = (window.state && window.state.wires) ? window.state.wires.length : null;

  const objsWhileInCanvas = window.__a3dState().objs.length;   /* AMENDED FOR V120: no exit to take */
  window.__a3dEnter();
  const objsBackInBim = window.__a3dState().objs.length;

  return {inDa, in3d, objsWhileInCanvas, objsBackInBim,
          canvasBefore, canvasAfter, wiresBefore, wiresAfter,
          stateKeys: window.state ? Object.keys(window.state).sort() : null};
}
"""


# Step 3: the tree is re-parented into the dock panel so the rail selects a subject and its
# sections stack beneath it -- one column instead of two panels side by side.
PROBE_NESTED = r"""
() => {
  const rect = (sel) => { const e = document.querySelector(sel); if (!e) return null;
    const r = e.getBoundingClientRect(); return {w: Math.round(r.width), x: Math.round(r.x)}; };
  const vis = (sel) => { const e = document.querySelector(sel); if (!e) return false;
    const r = e.getBoundingClientRect(); return getComputedStyle(e).display !== 'none' && r.width > 0; };

  window.__a3dEnter(); window.__a3dSetPlanView();
  const bim = window.__a3dTreeDocked();
  const dock = rect('#a3d-shell'), shell = rect('#acad3d');
  bim.dockW = dock ? dock.w : null;
  bim.shellX = shell ? shell.x : null;
  bim.leftChrome = shell ? shell.x : null;

  /* AMENDED FOR V119: the rail's buttons are icon-only, so they are picked by the tab they open. */
  const pick = (label) => {
    const b = document.querySelector('#a3d-rail .a3d-railbtn[data-tab="' + label + '"]');
    if (b) b.click();
    return {flVisible: vis('#a3d-leftpanel > .a3d-tabbody'),
            treeVisible: vis('#a3d-leftpanel > .a3d-tree')};
  };
  const fileTab = pick('browser');
  const assetsTab = pick('assets');
  pick('browser');
  return {v65: window.__acad3dV65 || null, bim, fileTab, assetsTab};   /* AMENDED FOR V120: no exit */
}
"""


async def run(page, name, script):
    print("\n== " + name + " ==")
    try:
        return await page.evaluate(script)
    except Exception as e:
        check(False, name + " threw: " + str(e))
        return None


async def main():
    path = pathlib.Path(TARGET).resolve()
    if not path.exists():
        print("Target file not found: " + str(path))
        sys.exit(1)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1600, "height": 950})
        page_errors = []
        page.on("pageerror", lambda e: page_errors.append(str(e)))
        await page.goto("file://" + str(path))
        await page.wait_for_timeout(900)

        r = await run(page, "API surface", PROBE_API)
        if r:
            check(r["v64"] is not None, "V64 marker present: " + str(r["v64"]))
            check(r["hasApi"], "all required test hooks present")

        r = await run(page, "One work surface per workspace", PROBE_WALK)
        if r:
            stops = [("Drafting", r["da"]), ("3D", r["threeD"]),
                     ("back to Drafting", r["backToDa"])]

            for label, g in stops:
                check(g["workSurfaces"] == 1,
                      "%s: exactly ONE full-window work surface is mounted (got %d)"
                      % (label, g["workSurfaces"]))

            # __acad3dV113c: the board is deleted, so "hidden, not painted over" has nothing left
            # to say. What matters now is that its elements are not in the document at all and the
            # BIM shell is the only surface there is.
            check(r["boardGone"] is True,
                  "the whiteboard's viewport and world are gone from the document (%r)" % r["boardGone"])
            for label, g in stops:
                check(g.get("viewport") is None,   # AMENDED FOR V120: the hook no longer reports a board
                      "%s: there is no board element to hide (%r)" % (label, g.get("viewport")))
                check(g["acad3d"] is not None and g["acad3d"]["visible"],
                      "%s: the BIM shell is the mounted surface" % label)

            # AMENDED AT V75. This contract was written when Canvas was a workspace a user could
            # switch to, and it compared all four stops including Canvas. V73 retired Canvas as a
            # workspace: the board is still mounted (it hosts the file dock and the shared material
            # library), but it is no longer something anyone can navigate to, and it carries no BIM
            # ribbon -- so its work surface legitimately starts at y=52 where the two live
            # workspaces start at y=182. Holding the retired stop to the shared-geometry contract
            # made the rig report a 130px "inconsistency" that no user could ever see, which is a
            # false signal in exactly the place this suite exists to be trusted.
            #
            # The contract now covers the workspaces that actually exist, and the Canvas stop is
            # asserted for what it is instead: unreachable.
            live = [(label, g["work"]) for label, g in stops
                    if g["work"] and label != "Canvas"]
            check(len(live) == 3, "a work surface was resolvable in every LIVE workspace stop")
            if len(live) == 3:
                xs = set(wk["x"] for _, wk in live)
                ws = set(wk["w"] for _, wk in live)
                ys = set(wk["y"] for _, wk in live)
                hs = sorted(set(wk["h"] for _, wk in live))
                check(len(xs) == 1,
                      "the live workspaces share ONE work-surface left origin: %r" % sorted(xs))
                check(len(ws) == 1,
                      "the live workspaces share ONE work-surface width: %r" % sorted(ws))
                check(len(ys) == 1,
                      "the live workspaces share ONE work-surface top edge: %r" % sorted(ys))
                check(len(hs) == 1,
                      "and ONE height -- with Canvas retired there is no bottom-chrome reserve "
                      "left to differ by: %r" % hs)

            check(r["da"]["ribbon"] and r["threeD"]["ribbon"]
                  and r["da"]["ribbon"]["h"] == r["threeD"]["ribbon"]["h"],
                  "the ribbon is one shared surface at one height in both live workspaces")
            check(r.get("workspaceMenu") is False,
                  "and no workspace is offered at all -- V119 removed the view dropdown that offered "
                  "them, so a retired one cannot be reached from the UI (switcher present: %r)" % (r.get("workspaceMenu"),))

        # __acad3dV113c: this section measured that the whiteboard board survived being hidden
        # and re-shown, down to its transform matrix, because entering and leaving the BIM shell
        # moved it. The board is deleted, and so is the exit path that used to restore it -- see
        # V67 section 8 for why that path was never reachable by a user. What is left to assert is
        # that entering and leaving the BIM shell does not resurrect any of it.
        r = await run(page, "nothing of the board comes back", PROBE_ROUNDTRIP)
        if r:
            b, d, a, c = r["before"], r["during"], r["after"], r["afterCycles"]
            for label, g in (("before", b), ("during", d), ("after", a), ("after 3 cycles", c)):
                check(g["display"] == "missing",
                      "%s: there is no board element (%s)" % (label, g["display"]))
                check(g["nodeCount"] == 0 and g["stateNodes"] is None,
                      "%s: no board nodes and no board model (%r / %r)"
                      % (label, g["nodeCount"], g["stateNodes"]))

        r = await run(page, "Model separation is what it claims to be", PROBE_MODEL_SEPARATION)
        if r:
            check(r["inDa"] == r["in3d"] == 1,
                  "Drafting and 3D are two cameras on ONE model -- the wall is present in both "
                  "(%r / %r)" % (r["inDa"], r["in3d"]))
            check(r["objsWhileInCanvas"] == 1 and r["objsBackInBim"] == 1,
                  "and entering again leaves the model as it was (%r / %r)"
                  % (r["objsWhileInCanvas"], r["objsBackInBim"]))
            # __acad3dV113c: these three checks used to document a separation -- a BIM model, a
            # whiteboard model in state.nodes, and a third one in state.wires carrying the
            # material cards -- and said in their own text that they documented it rather than
            # endorsed it. The whiteboard engine is deleted, so there is no separation left to
            # document. What is asserted now is the end of it.
            check(r["canvasBefore"] is None and r["canvasAfter"] is None,
                  "the whiteboard's node model is gone (%r -> %r)"
                  % (r["canvasBefore"], r["canvasAfter"]))
            check(r["wiresBefore"] is None and r["wiresAfter"] is None,
                  "and so is the wire model that used to carry the material cards -- those moved "
                  "to the shell services block in V113 (%r -> %r)"
                  % (r["wiresBefore"], r["wiresAfter"]))
            check(r["stateKeys"] is None,
                  "state itself is gone: one model now, A3D.objs (%r)" % (r["stateKeys"],))

        r = await run(page, "One left column: the tree nests into the dock panel", PROBE_NESTED)
        if r:
            check(r["v65"] is not None, "V65 marker present: " + str(r["v65"]))
            # AMENDED FOR V120: "in Canvas the tree is not in the dock panel" is retired -- there is no
            # Canvas, and no exit that could reach a state without the BIM shell.
            check(r["bim"]["docked"] is True,
                  "in BIM the tree IS nested inside #a3d-leftpanel: parent=%r" % r["bim"]["parent"])
            check(r["bim"]["propsAlive"] and r["bim"]["browserAlive"],
                  "re-parenting kept the tree's nodes alive -- the el.* references cached at "
                  "buildUI() time survive the move, which is why this approach is safe")
            # AMENDED FOR V120: "on exit the tree is restored" is retired with exit3d.
            check(r["bim"]["dockVar"] == "296px",
                  "--figma-dock-w reflects the OPEN dock while the tree is hosted there (%r) -- the "
                  "stale-variable bug that let a 242px panel and a 268px tree both lay out at x=54"
                  % r["bim"]["dockVar"])
            # One column, not two: the work surface must begin immediately after the single dock.
            check(r["bim"]["shellX"] == r["bim"]["dockW"],
                  "the drawing area starts exactly where the one dock column ends (shell x=%r, "
                  "dock width=%r) -- no second panel between them"
                  % (r["bim"]["shellX"], r["bim"]["dockW"]))
            check(r["bim"]["leftChrome"] <= 320,
                  "total left chrome is one column, not two stacked panels: %rpx (was 510px with "
                  "the dock panel and the tree side by side)" % r["bim"]["leftChrome"])
            # The rail selects a subject; it does not pile unrelated models into one scroll.
            check(r["fileTab"]["flVisible"] is False and r["fileTab"]["treeVisible"] is True,
                  "File shows the BIM navigator and hides the Canvas board's own Pages/Layers -- "
                  "those belong to a different model and stacking them would not be 'united'")
            check(r["assetsTab"]["flVisible"] is True and r["assetsTab"]["treeVisible"] is False,
                  "Assets shows the asset library and hides the BIM navigator")

        await browser.close()

        print("\n== Page errors ==")
        for e in page_errors:
            print("  " + e)
        check(len(page_errors) == 0,
              "zero uncaught page errors across every workspace transition")

    print("\n" + str(TOTAL[0] - len(FAILS)) + "/" + str(TOTAL[0]) + " checks passed")
    if FAILS:
        print("\nFAILED:")
        for f in FAILS:
            print("  - " + f)
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
