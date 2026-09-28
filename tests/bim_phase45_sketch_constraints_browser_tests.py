"""
bim_phase45_sketch_constraints_browser_tests.py

Regression suite for Sketch Geometric Constraints (__acad3dV45) added to
canvas_v10.html. This is an original 2D constraint solver -- damped
Gauss-Newton / Levenberg-Marquardt over a numeric central-difference
Jacobian, a standard textbook numerical method -- applied to the points of
the currently-selected sketch object. It is not a port of, or derived from,
any other CAD application's source.

This suite checks three layers:
  1. The embedded solver itself, called directly (bimSolveSketchConstraints
     via window.__a3dSolveSketchConstraints), against known-answer cases
     (a 3-4-5 right triangle, a coincident merge, a deliberately conflicting
     pair of distance constraints) -- the same class of check that validated
     the standalone Node prototype before it was ported into the app.
  2. The sketch-object integration: adding/deleting constraints through the
     app's own data model and re-solve pipeline (window.__a3dAddSketchConstraint
     / __a3dDeleteSketchConstraint / __a3dSketchConstraints), including the
     fail-safe paths (malformed constraint requests, conflicting constraints,
     a locked/pinned sketch) that must be rejected without corrupting o.pts.
  3. A real UI flow: the ribbon's Constraints panel, clicking real grip
     points on the canvas (using the app's own on-screen grip coordinates,
     not synthetic ones) to build a Horizontal + Distance constraint pair,
     and dragging a constrained grip to confirm the solver re-runs live and
     keeps the constraint satisfied.

Run:  python3 bim_phase45_sketch_constraints_browser_tests.py [path/to/canvas_v10.html]
"""
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


PROBE_SOLVER = r"""
() => {
  const res = {};
  res.marker = window.__acad3dV45 || null;

  // ---- 1a. 3-4-5 right triangle: A pinned at origin, B horizontal from A at distance 3,
  // C vertical from B at distance 4. The hypotenuse A-C must come out to exactly 5 -- nothing in
  // the constraint list states that fact directly. ----
  const pts1 = [[0.3, 0.2], [2.5, 0.6], [2.9, 3.4]];
  const cons1 = [
    { type: 'fixed', refs: [0], value: [0, 0] },
    { type: 'horizontal', refs: [0, 1] },
    { type: 'distance', refs: [0, 1], value: 3 },
    { type: 'vertical', refs: [1, 2] },
    { type: 'distance', refs: [1, 2], value: 4 }
  ];
  const r1 = window.__a3dSolveSketchConstraints(pts1, cons1);
  res.triangle = {
    error: r1.error || null,
    residualNorm: r1.residualNorm,
    a: r1.pts ? r1.pts[0] : null,
    b: r1.pts ? r1.pts[1] : null,
    c: r1.pts ? r1.pts[2] : null,
    hyp: r1.pts ? Math.hypot(r1.pts[2][0], r1.pts[2][1]) : null
  };

  // ---- 1b. Coincident merges two separated points onto each other. ----
  const r2 = window.__a3dSolveSketchConstraints([[0, 0], [4, 4]], [{ type: 'coincident', refs: [0, 1] }]);
  res.coincident = { error: r2.error || null, residualNorm: r2.residualNorm, p0: r2.pts ? r2.pts[0] : null, p1: r2.pts ? r2.pts[1] : null };

  // ---- 1c. Conflicting distance constraints (3 vs 5 on the same pinned, horizontal pair) must
  // NOT be silently reported as solved -- the residual must stay large. ----
  const r3 = window.__a3dSolveSketchConstraints([[0, 0], [4, 0]], [
    { type: 'fixed', refs: [0], value: [0, 0] },
    { type: 'horizontal', refs: [0, 1] },
    { type: 'distance', refs: [0, 1], value: 3 },
    { type: 'distance', refs: [0, 1], value: 5 }
  ]);
  res.conflicting = { error: r3.error || null, residualNorm: r3.residualNorm };

  // ---- 1d. DOF estimate sanity. ----
  res.dof = {
    unconstrained3: window.__a3dEstimateSketchDOF(3, []),
    onePinned3: window.__a3dEstimateSketchDOF(3, [{ type: 'fixed', refs: [0], value: [0, 0] }])
  };

  return res;
}
"""

PROBE_INTEGRATION = r"""
() => {
  const res = {};

  // ---- 2a. Create a real sketch object (3 points: a right-angle-ish triangle, perturbed) via
  // the same finishPoly() path a user drawing a Polyline sketch goes through. ----
  const sketchId = window.__a3dSketch('poly', [[0.2, 0.15], [2.6, 0.4], [2.8, 3.3]]);
  res.sketchId = sketchId;
  res.constraintsInitiallyEmpty = window.__a3dSketchConstraints(sketchId).length === 0;

  // ---- 2b. 'fixed' is an internal-only constraint kind (used transiently during a grip drag) --
  // it must be REJECTED if requested through the public add-constraint entry point. ----
  const fixedRejected = window.__a3dAddSketchConstraint(sketchId, 'fixed', [0], [0, 0]);
  res.fixedRejected = fixedRejected === null;

  // ---- 2c. Malformed requests (wrong ref count, out-of-range index) must be rejected without
  // adding anything or throwing. ----
  const badCount = window.__a3dAddSketchConstraint(sketchId, 'horizontal', [0], null);
  const badIndex = window.__a3dAddSketchConstraint(sketchId, 'horizontal', [0, 99], null);
  res.malformedRejected = { badCount: badCount === null, badIndex: badIndex === null };
  res.countAfterMalformed = window.__a3dSketchConstraints(sketchId).length;

  // ---- 2d. Real constraint sequence: pin the geometry into an exact 3-4-5 right triangle via
  // horizontal(P0,P1) + distance(P0,P1,3), then vertical(P1,P2) + distance(P1,P2,4). ----
  const c1 = window.__a3dAddSketchConstraint(sketchId, 'horizontal', [0, 1], null);
  const c2 = window.__a3dAddSketchConstraint(sketchId, 'distance', [0, 1], 3);
  const c3 = window.__a3dAddSketchConstraint(sketchId, 'vertical', [1, 2], null);
  const c4 = window.__a3dAddSketchConstraint(sketchId, 'distance', [1, 2], 4);
  res.addedIds = { c1, c2, c3, c4 };
  res.constraintCount = window.__a3dSketchConstraints(sketchId).length;
  res.dofAfter = window.__a3dEstimateSketchDOF(3, window.__a3dSketchConstraints(sketchId));

  return res;
}
"""

async def main():
    url = pathlib.Path(TARGET).resolve().as_uri()
    async with async_playwright() as pw:
        b = await pw.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        pg = await b.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(url)
        await pg.wait_for_timeout(3000)
        await pg.evaluate("() => { if (window.__a3dEnter) window.__a3dEnter(); }")
        await pg.wait_for_timeout(1200)

        r1 = await pg.evaluate(PROBE_SOLVER)

        print("\n== load ==")
        check(not errs, "no uncaught page errors on load (%s)" % (errs[:1] or "none"))
        check(r1["marker"] is not None, "__acad3dV45 feature marker present")

        print("\n== embedded solver: known-answer cases ==")
        tri = r1["triangle"]
        check(tri["error"] is None, "3-4-5 triangle solve did not error")
        check(tri["residualNorm"] < 1e-6, "3-4-5 triangle residual converges to ~0 (%.2e)" % tri["residualNorm"])
        check(abs(tri["a"][0]) < 1e-4 and abs(tri["a"][1]) < 1e-4, "point A pinned at the origin")
        check(abs(tri["b"][0] - 3) < 1e-3 and abs(tri["b"][1]) < 1e-3, "point B is horizontal from A at distance 3")
        check(abs(tri["c"][0] - 3) < 1e-3 and abs(tri["c"][1] - 4) < 1e-3, "point C is vertical from B at distance 4")
        check(abs(tri["hyp"] - 5) < 1e-3, "hypotenuse A-C computes to 5 (not asserted by any single constraint) (%.5f)" % tri["hyp"])

        co = r1["coincident"]
        check(co["error"] is None, "coincident solve did not error")
        check(co["residualNorm"] < 1e-6, "coincident residual converges to ~0")
        check(abs(co["p0"][0] - co["p1"][0]) < 1e-4 and abs(co["p0"][1] - co["p1"][1]) < 1e-4, "coincident points end up equal")

        cf = r1["conflicting"]
        check(cf["error"] is None, "conflicting-constraint solve reports via residual, not an exception")
        check(cf["residualNorm"] > 0.5, "contradictory distance constraints (3 vs 5) leave a large residual, not falsely marked solved (%.3f)" % cf["residualNorm"])

        dof = r1["dof"]
        check(dof["unconstrained3"] == 6, "3 unconstrained points report 6 degrees of freedom")
        check(dof["onePinned3"] == 4, "pinning one point removes exactly 2 degrees of freedom")

        print("\n== sketch-object integration ==")
        r2 = await pg.evaluate(PROBE_INTEGRATION)
        sketchId = r2["sketchId"]
        check(sketchId is not None, "real sketch object created via the Polyline tool path")
        check(r2["constraintsInitiallyEmpty"] is True, "a freshly-drawn sketch starts with no constraints")
        check(r2["fixedRejected"] is True, "'fixed' cannot be added as a public constraint (internal-only, drag-pin use)")
        mr = r2["malformedRejected"]
        check(mr["badCount"] is True, "wrong ref count is rejected")
        check(mr["badIndex"] is True, "out-of-range point index is rejected")
        check(r2["countAfterMalformed"] == 0, "rejected malformed requests add nothing to the constraint list")
        added = r2["addedIds"]
        check(all(added[k] is not None for k in ("c1", "c2", "c3", "c4")), "horizontal/distance/vertical/distance constraints all accepted (%s)" % added)
        check(r2["constraintCount"] == 4, "sketch now carries exactly 4 stored constraints")
        check(r2["dofAfter"] == 2, "DOF estimate drops from 6 to 2 after 4 single-row constraints (2 points x 2 minus 4 rows)")

        print("\n== solved geometry matches the 3-4-5 triangle (through the real object, not the raw solver) ==")
        geoPts = await pg.evaluate("(sid) => window.__a3dSketchPts(sid)", sketchId)
        check(geoPts is not None and len(geoPts) == 3, "sketch still has 3 points after constraining")
        if geoPts:
            p0, p1, p2 = geoPts
            check(abs(p0[1] - p1[1]) < 1e-3, "P0-P1 is horizontal after constraining (z0=%.4f z1=%.4f)" % (p0[1], p1[1]))
            check(abs(p0[0] - p1[0] - 3) < 1e-2 or abs(p1[0] - p0[0] - 3) < 1e-2, "P0-P1 distance solved to 3 (%.4f)" % abs(p1[0] - p0[0]))
            check(abs(p1[0] - p2[0]) < 1e-3, "P1-P2 is vertical after constraining (x1=%.4f x2=%.4f)" % (p1[0], p2[0]))
            check(abs(abs(p2[1] - p1[1]) - 4) < 1e-2, "P1-P2 distance solved to 4 (%.4f)" % abs(p2[1] - p1[1]))

        print("\n== fail-safe rejections leave stored geometry untouched ==")
        conflict = await pg.evaluate(r"""
        (sid) => {
          const before = window.__a3dSketchConstraints(sid).length;
          const toastBefore = document.getElementById('a3d-toast') ? document.getElementById('a3d-toast').textContent : '';
          // P0-P1 is already constrained to distance 3 (horizontal) -- asking for 5 as well is
          // unsatisfiable and must be rejected, not silently applied.
          const rejected = window.__a3dAddSketchConstraint(sid, 'distance', [0, 1], 5);
          const after = window.__a3dSketchConstraints(sid).length;
          const toastAfter = document.getElementById('a3d-toast') ? document.getElementById('a3d-toast').textContent : '';
          return { rejected, before, after, toastChanged: toastBefore !== toastAfter, toastAfter };
        }
        """, sketchId)
        check(conflict["rejected"] is None, "conflicting distance constraint (5 where 3 already holds) is rejected")
        check(conflict["after"] == conflict["before"], "rejected conflicting constraint does not change the stored count (%d)" % conflict["after"])
        check("not be fully satisfied" in conflict["toastAfter"] or "not fully satisfied" in conflict["toastAfter"],
              "a toast explains the conflicting-constraint rejection (%s)" % conflict["toastAfter"])

        locked = await pg.evaluate(r"""
        (sid) => {
          window.__a3dSetLockedById ? window.__a3dSetLockedById(sid, true) : null;
          const before = window.__a3dSketchConstraints(sid).length;
          const rejected = window.__a3dAddSketchConstraint(sid, 'horizontal', [0, 1], null);
          const after = window.__a3dSketchConstraints(sid).length;
          if (window.__a3dSetLockedById) window.__a3dSetLockedById(sid, false);
          return { rejected, before, after, hasHook: !!window.__a3dSetLockedById };
        }
        """, sketchId)
        if locked["hasHook"]:
            check(locked["rejected"] is None, "adding a constraint to a pinned/locked sketch is rejected")
            check(locked["after"] == locked["before"], "rejected pinned-sketch constraint changes nothing")
        else:
            print("  SKIP  no __a3dSetLocked test hook exposed; locked-sketch rejection covered by source review only")

        print("\n== deleting a constraint re-solves with the remainder, not silently ==")
        delFlow = await pg.evaluate(r"""
        (sid) => {
          const consBefore = window.__a3dSketchConstraints(sid);
          const vertCon = consBefore.find(c => c.type === 'vertical');
          const distCon4 = consBefore.find(c => c.type === 'distance' && Math.abs(c.value - 4) < 1e-9);
          const ok1 = window.__a3dDeleteSketchConstraint(sid, vertCon.id);
          const ok2 = window.__a3dDeleteSketchConstraint(sid, distCon4.id);
          const consAfter = window.__a3dSketchConstraints(sid);
          return { ok1, ok2, countBefore: consBefore.length, countAfter: consAfter.length,
                   dofAfter: window.__a3dEstimateSketchDOF(3, consAfter) };
        }
        """, sketchId)
        check(delFlow["ok1"] is True and delFlow["ok2"] is True, "deleting existing constraints reports success")
        check(delFlow["countAfter"] == delFlow["countBefore"] - 2, "constraint count drops by exactly 2 after two deletes")
        check(delFlow["dofAfter"] == 4, "DOF estimate rises back up after removing 2 single-row constraints")

        # ---- 3. Real UI flow: ribbon Constraints panel + real grip clicks on canvas ----
        print("\n== real UI flow (ribbon Constraints panel + click-to-pick grip points) ==")
        uiFlow = await pg.evaluate(r"""
        async () => {
          const out = {};
          const sleep = (ms) => new Promise(r => setTimeout(r, ms));

          // Fresh sketch for the UI flow, independent of the earlier direct-hook sketch.
          const sid = window.__a3dSketch('poly', [[5, 5], [8.4, 5.6], [8.7, 9.9]]);
          out.sketchId = sid;

          // Switch to the Modify ribbon tab, which carries the Constraints panel.
          const tabBtn = document.querySelector('[data-dockgrp="a3dmodify"]')   /* AMENDED FOR V120: the hidden ribbon is gone; the tool dock has the group */;
          out.tabFound = !!tabBtn;
          if (tabBtn) tabBtn.click();
          await sleep(50);

          const conBtn = document.querySelector('[data-a3dr="con:horizontal"]');
          out.ribbonButtonFound = !!conBtn;
          if (conBtn) conBtn.click();
          await sleep(50);
          out.pickModeArmed = !!window.__a3dConPickState();

          // Click the first two real grip points (screen coordinates the app itself computed).
          const cv = document.getElementById('a3d-canvas');
          const rect = cv.getBoundingClientRect();
          const scaleX = rect.width / cv.width, scaleY = rect.height / cv.height;
          function clickGrip(idx) {
            const grips = window.__a3dGrips().filter(g => g.objId === sid);
            const g = grips.find(gr => gr.idx === idx);
            if (!g) return false;
            const cx = rect.left + g.x * scaleX, cy = rect.top + g.y * scaleY;
            cv.dispatchEvent(new MouseEvent('mousedown', { clientX: cx, clientY: cy, button: 0, bubbles: true }));
            window.dispatchEvent(new MouseEvent('mouseup', { clientX: cx, clientY: cy, button: 0, bubbles: true }));
            return true;
          }
          out.clickedP0 = clickGrip(0);
          await sleep(30);
          out.pickStateAfterFirst = window.__a3dConPickState();
          out.clickedP1 = clickGrip(1);
          await sleep(30);
          out.pickStateAfterSecond = window.__a3dConPickState();

          const consAfterHoriz = window.__a3dSketchConstraints(sid);
          out.horizAdded = consAfterHoriz.some(c => c.type === 'horizontal');

          // Now a Distance constraint, which routes through a value dialog.
          document.querySelector('[data-a3dr="con:distance"]').click();
          await sleep(30);
          clickGrip(0);
          await sleep(30);
          clickGrip(1);
          await sleep(50);
          out.distanceDlgOpen = !!document.querySelector('.a3d-dlg');
          const dlg = document.querySelector('.a3d-dlg');
          if (dlg) {
            dlg.querySelector('[data-a3dp="v"]').value = '5';
            dlg.querySelector('[data-a3dlg="ok"]').click();
          }
          await sleep(50);
          const consAfterDist = window.__a3dSketchConstraints(sid);
          const distCon = consAfterDist.find(c => c.type === 'distance');
          out.distanceValue = distCon ? distCon.value : null;

          // Properties palette: the Sketch Constraints group should now list both, with delete buttons.
          const propsHtml = document.getElementById('a3d-propsbody') ? document.getElementById('a3d-propsbody').innerHTML : '';
          out.constraintsListedInProps = propsHtml.indexOf('data-concondel=') >= 0;
          out.dofRowInProps = propsHtml.indexOf('Degrees of Freedom') >= 0;

          // Escape cancels an in-progress pick.
          document.querySelector('[data-a3dr="con:parallel"]').click();
          await sleep(30);
          out.pickArmedBeforeEscape = !!window.__a3dConPickState();
          window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
          await sleep(30);
          out.pickArmedAfterEscape = !!window.__a3dConPickState();

          // Drag the constrained grip P1 -- the solver should re-run live and keep the sketch
          // horizontal (P0.z === P1.z) even though the drag target was off-axis.
          const beforeDrag = window.__a3dGrips().filter(g => g.objId === sid);
          const p0 = beforeDrag.find(g => g.idx === 0), p1 = beforeDrag.find(g => g.idx === 1);
          out.horizontalBeforeDrag = null;
          const ptsAfterDragNudge = window.__a3dDragGripTo(sid, 1, 20, 13.7);
          out.p1AfterOffAxisDrag = ptsAfterDragNudge ? ptsAfterDragNudge[1] : null;
          out.p0AfterDrag = ptsAfterDragNudge ? ptsAfterDragNudge[0] : null;
          out.stillHorizontalAfterDrag = ptsAfterDragNudge ? Math.abs(ptsAfterDragNudge[0][1] - ptsAfterDragNudge[1][1]) < 1e-3 : null;
          out.distanceHeldAfterDrag = ptsAfterDragNudge ?
            Math.abs(Math.hypot(ptsAfterDragNudge[1][0]-ptsAfterDragNudge[0][0], ptsAfterDragNudge[1][1]-ptsAfterDragNudge[0][1]) - 5) < 1e-2 : null;

          return out;
        }
        """)

        check(uiFlow.get("sketchId") is not None, "second sketch for the UI flow created")
        check(uiFlow.get("tabFound") is True, "the Modify group is in the tool dock")
        check(uiFlow.get("ribbonButtonFound") is True, "the Constraints panel's Horizontal button exists in the tool dock")
        check(uiFlow.get("pickModeArmed") is True, "clicking the Horizontal tool arms constraint-pick mode")
        check(uiFlow.get("clickedP0") is True and uiFlow.get("clickedP1") is True, "both grip points were clickable on the real canvas")
        check(uiFlow.get("pickStateAfterFirst") is not None, "pick mode still armed after the first point (needs 2)")
        check(uiFlow.get("pickStateAfterSecond") is None, "pick mode auto-completes and clears after the second point")
        check(uiFlow.get("horizAdded") is True, "Horizontal constraint was actually added by the real click flow")
        check(uiFlow.get("distanceDlgOpen") is True, "picking 2 points for Distance opens the value dialog")
        check(uiFlow.get("distanceValue") == 5, "submitting 5 in the Distance dialog stores value=5 (%s)" % uiFlow.get("distanceValue"))
        check(uiFlow.get("constraintsListedInProps") is True, "Properties palette lists constraints with a delete control")
        check(uiFlow.get("dofRowInProps") is True, "Properties palette shows the approximate DOF readout")
        check(uiFlow.get("pickArmedBeforeEscape") is True, "Parallel tool armed pick mode before Escape")
        check(uiFlow.get("pickArmedAfterEscape") is False, "Escape cancels an in-progress constraint pick")
        check(uiFlow.get("stillHorizontalAfterDrag") is True,
              "dragging P1 off-axis still re-solves back to horizontal (P0.z == P1.z) (%s)" % uiFlow.get("p1AfterOffAxisDrag"))
        check(uiFlow.get("distanceHeldAfterDrag") is True, "distance=5 constraint still holds after the drag re-solve")

        await b.close()

    print("\n%d checks, %d failed" % (TOTAL[0], len(FAILS)))
    print("RESULT: " + ("PASS" if not FAILS else "FAIL"))
    return 1 if FAILS else 0


sys.exit(asyncio.run(main()))
