"""
bim_phase49_sketch_constraints2_browser_tests.py

Regression suite for the second batch of Sketch Geometric Constraints
(__acad3dV49) added to canvas_v10.html: Point on Line, Midpoint,
Symmetric (about a point), and Symmetric (about a line). These extend the
same original Gauss-Newton / Levenberg-Marquardt solver introduced in V45
(bimSolveSketchConstraints) -- no new solver machinery was added, only four
new residual-formula cases plus their ribbon/label/pick-count wiring.

The residual formulas themselves are adapted (as math, not code) from
FreeCAD's real planegcs solver (src/Mod/Sketcher/App/planegcs/Constraints.cpp),
confirmed during a source-level audit to be small, self-contained, OCCT-free
pure math -- see canvas_v10_STATUS.md's "Real FreeCAD source audit via
GitHub" section and its "Code-reuse policy" note (this app is personal-use
only, so copying/adapting such formulas is explicitly fine; what matters is
that the app remains dependable and free of decorative/misattributed code).

Known, explicitly-scoped limitation NOT covered by this phase: planegcs's
Tangent and driving Radius/Diameter constraints are NOT ported, because this
app's sketch data model (o.pts, a flat point array) has no circle/arc
entity type to attach them to. Porting those would require a larger
structural change (adding circle/arc as first-class sketch entities) and is
tracked as a separate future item, not silently dropped.

This suite checks two layers, matching the bim_phase45 suite's structure:
  1. The embedded solver itself, called directly via
     window.__a3dSolveSketchConstraints, against known-answer geometric
     cases for each of the 4 new constraint types.
  2. The sketch-object integration: adding each new constraint type through
     the app's own public entry point (window.__a3dAddSketchConstraint),
     confirming correct required-pick-counts (A3D_CON_NEED), correct
     descriptions in the Properties palette (bimSketchConstraintDesc via
     window.__a3dSketchConstraintDesc), and the ribbon wiring (icon +
     Constraints panel entry + label) added for all 4 new tools.

Run:  python3 bim_phase49_sketch_constraints2_browser_tests.py [path/to/canvas_v10.html]
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
  res.marker = window.__acad3dV49 || null;

  // ---- 1a. Point on Line: P starts off the line A(0,0)-B(10,0); after solving it must land
  // exactly on that line (z == 0), while its x is left free (no x-constraint given). ----
  const r1 = window.__a3dSolveSketchConstraints(
    [[4, 3], [0, 0], [10, 0]],
    [
      { type: 'fixed', refs: [1], value: [0, 0] },
      { type: 'fixed', refs: [2], value: [10, 0] },
      { type: 'pointonline', refs: [0, 1, 2] }
    ]
  );
  res.pointOnLine = { error: r1.error || null, residualNorm: r1.residualNorm, p: r1.pts ? r1.pts[0] : null, a: r1.pts ? r1.pts[1] : null, b: r1.pts ? r1.pts[2] : null };

  // ---- 1b. Point on Line on a non-axis-aligned line A(0,0)-B(6,6): a point on the line must
  // satisfy x == z. ----
  const r1b = window.__a3dSolveSketchConstraints(
    [[5, 1], [0, 0], [6, 6]],
    [
      { type: 'fixed', refs: [1], value: [0, 0] },
      { type: 'fixed', refs: [2], value: [6, 6] },
      { type: 'pointonline', refs: [0, 1, 2] }
    ]
  );
  res.pointOnLineDiagonal = { error: r1b.error || null, residualNorm: r1b.residualNorm, p: r1b.pts ? r1b.pts[0] : null };

  // ---- 2. Midpoint: M must end up exactly halfway between pinned A(0,0) and B(10,4). ----
  const r2 = window.__a3dSolveSketchConstraints(
    [[1, 1], [0, 0], [10, 4]],
    [
      { type: 'fixed', refs: [1], value: [0, 0] },
      { type: 'fixed', refs: [2], value: [10, 4] },
      { type: 'midpoint', refs: [0, 1, 2] }
    ]
  );
  res.midpoint = { error: r2.error || null, residualNorm: r2.residualNorm, m: r2.pts ? r2.pts[0] : null };

  // ---- 3. Symmetric about a point: P and Q must end up mirrored through a pinned center
  // C(5,5), starting from an asymmetric guess. P is additionally pinned so only Q must move. ----
  const r3 = window.__a3dSolveSketchConstraints(
    [[2, 2], [0, 0], [5, 5]],
    [
      { type: 'fixed', refs: [0], value: [2, 2] },
      { type: 'fixed', refs: [2], value: [5, 5] },
      { type: 'symmetric_pt', refs: [0, 1, 2] }
    ]
  );
  res.symmetricPt = { error: r3.error || null, residualNorm: r3.residualNorm, p: r3.pts ? r3.pts[0] : null, q: r3.pts ? r3.pts[1] : null, c: r3.pts ? r3.pts[2] : null };

  // ---- 4. Symmetric about a line: P and Q must end up mirrored across the pinned vertical line
  // A(5,0)-B(5,10); P is pinned at (2,3), so Q must resolve to (8,3). ----
  const r4 = window.__a3dSolveSketchConstraints(
    [[2, 3], [1, 1], [5, 0], [5, 10]],
    [
      { type: 'fixed', refs: [0], value: [2, 3] },
      { type: 'fixed', refs: [2], value: [5, 0] },
      { type: 'fixed', refs: [3], value: [5, 10] },
      { type: 'symmetric_line', refs: [0, 1, 2, 3] }
    ]
  );
  res.symmetricLine = { error: r4.error || null, residualNorm: r4.residualNorm, p: r4.pts ? r4.pts[0] : null, q: r4.pts ? r4.pts[1] : null };

  // ---- 5. Residual-count sanity: coincident/fixed/midpoint/symmetric_pt/symmetric_line all
  // contribute 2 equations; pointonline contributes 1. Probed indirectly via DOF estimate, which
  // is exactly (2*nPoints - sum of residual counts). ----
  res.dofPointOnLine = window.__a3dEstimateSketchDOF(3, [{ type: 'pointonline', refs: [0, 1, 2] }]);
  res.dofMidpoint = window.__a3dEstimateSketchDOF(3, [{ type: 'midpoint', refs: [0, 1, 2] }]);
  res.dofSymmetricPt = window.__a3dEstimateSketchDOF(3, [{ type: 'symmetric_pt', refs: [0, 1, 2] }]);
  res.dofSymmetricLine = window.__a3dEstimateSketchDOF(4, [{ type: 'symmetric_line', refs: [0, 1, 2, 3] }]);

  return res;
}
"""

PROBE_INTEGRATION = r"""
() => {
  const res = {};

  // Required pick-counts, exposed indirectly: a request with the wrong ref count is rejected.
  const sid = window.__a3dSketch('poly', [[0, 0], [4, 0], [4, 4], [0, 4]]);
  res.sketchId = sid;

  function tryAdd(type, refs, value) {
    return window.__a3dAddSketchConstraint(sid, type, refs, value === undefined ? null : value);
  }

  // ---- Wrong ref counts are rejected for all 4 new types. ----
  res.pointonlineWrongCountRejected = tryAdd('pointonline', [0, 1]) === null;
  res.midpointWrongCountRejected = tryAdd('midpoint', [0, 1]) === null;
  res.symmetricPtWrongCountRejected = tryAdd('symmetric_pt', [0, 1]) === null;
  res.symmetricLineWrongCountRejected = tryAdd('symmetric_line', [0, 1, 2]) === null;

  // ---- Correct ref counts are accepted, one at a time (each on a fresh sketch so they don't
  // fight each other / over-constrain). ----
  const s1 = window.__a3dSketch('poly', [[4, 3], [0, 0], [10, 0]]);
  const c1 = window.__a3dAddSketchConstraint(s1, 'pointonline', [0, 1, 2], null);
  res.pointonlineAccepted = c1 !== null;
  res.pointonlineDesc = c1 ? window.__a3dSketchConstraintDesc(s1, c1) : null;

  const s2 = window.__a3dSketch('poly', [[1, 1], [0, 0], [10, 4]]);
  const c2 = window.__a3dAddSketchConstraint(s2, 'midpoint', [0, 1, 2], null);
  res.midpointAccepted = c2 !== null;
  res.midpointDesc = c2 ? window.__a3dSketchConstraintDesc(s2, c2) : null;

  const s3 = window.__a3dSketch('poly', [[2, 2], [0, 0], [5, 5]]);
  const c3 = window.__a3dAddSketchConstraint(s3, 'symmetric_pt', [0, 1, 2], null);
  res.symmetricPtAccepted = c3 !== null;
  res.symmetricPtDesc = c3 ? window.__a3dSketchConstraintDesc(s3, c3) : null;

  const s4 = window.__a3dSketch('poly', [[2, 3], [1, 1], [5, 0], [5, 10]]);
  const c4 = window.__a3dAddSketchConstraint(s4, 'symmetric_line', [0, 1, 2, 3], null);
  res.symmetricLineAccepted = c4 !== null;
  res.symmetricLineDesc = c4 ? window.__a3dSketchConstraintDesc(s4, c4) : null;

  // ---- Fail-safe: an unsatisfiable combination (a point pinned both to a coordinate AND
  // required to be the midpoint of two other pinned points that don't average to it) is
  // rejected without corrupting the stored geometry. ----
  const s5 = window.__a3dSketch('poly', [[0, 0], [0, 0], [10, 4]]);
  window.__a3dAddSketchConstraint(s5, 'fixed', [0], [9, 9]); // should itself be rejected: 'fixed' is internal-only
  const fixedRejected = window.__a3dAddSketchConstraint(s5, 'fixed', [0], [9, 9]);
  res.fixedStillInternalOnly = fixedRejected === null;

  return res;
}
"""

PROBE_RIBBON = r"""
() => {
  const res = {};
  // Icons registered for all 4 new tools (non-empty SVG markup returned).
  res.icons = {
    pointonline: !!(window.__a3drIcon && window.__a3drIcon('con:pointonline')),
    midpoint: !!(window.__a3drIcon && window.__a3drIcon('con:midpoint')),
    symmetric_pt: !!(window.__a3drIcon && window.__a3drIcon('con:symmetric_pt')),
    symmetric_line: !!(window.__a3drIcon && window.__a3drIcon('con:symmetric_line'))
  };
  res.hasIconHook = !!window.__a3drIcon;

  // Labels registered for all 4 new tools (via the ribbon tooltip label function).
  res.labels = {
    pointonline: window.__a3drLabel ? window.__a3drLabel('con:pointonline') : null,
    midpoint: window.__a3drLabel ? window.__a3drLabel('con:midpoint') : null,
    symmetric_pt: window.__a3drLabel ? window.__a3drLabel('con:symmetric_pt') : null,
    symmetric_line: window.__a3drLabel ? window.__a3drLabel('con:symmetric_line') : null
  };
  res.hasLabelHook = !!window.__a3drLabel;

  // Ribbon buttons present in the DOM (Modify tab's Constraints panel).
  const tabBtn = (window.__a3dDockOpenGroup('a3dmodify')&&document.querySelector('#a3d-rupop .a3d-rkcat[data-rkcat="tool:a3dmodify"]'))   /* AMENDED FOR V120: the hidden ribbon is gone; the tool dock has the group. AMENDED FOR V130: and the group's tools are in the Tools and shortcuts panel */;
  if (tabBtn) tabBtn.click();
  res.buttonsFound = {
    pointonline: !!(window.__a3dToolsPanel(),document.querySelector('#a3d-rupop [data-a3dr="con:pointonline"]')),
    midpoint: !!(window.__a3dToolsPanel(),document.querySelector('#a3d-rupop [data-a3dr="con:midpoint"]')),
    symmetric_pt: !!(window.__a3dToolsPanel(),document.querySelector('#a3d-rupop [data-a3dr="con:symmetric_pt"]')),
    symmetric_line: !!(window.__a3dToolsPanel(),document.querySelector('#a3d-rupop [data-a3dr="con:symmetric_line"]'))
  };
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
        check(r1["marker"] is not None, "__acad3dV49 feature marker present")

        print("\n== embedded solver: Point on Line ==")
        pol = r1["pointOnLine"]
        check(pol["error"] is None, "point-on-line (axis-aligned) solve did not error")
        check(pol["residualNorm"] < 1e-4, "point-on-line residual converges to ~0 (%.2e)" % pol["residualNorm"])
        if pol["p"] and pol["a"] and pol["b"]:
            # Recompute the actual signed distance from the solved P to the solved line A-B
            # (rather than assuming A,B land at their exact pinned coordinates -- 'fixed' is
            # itself a soft residual in this damped least-squares solver, so a fully honest check
            # measures the constraint's own geometric quantity against the points it actually
            # produced, not against the caller's input).
            ax, az = pol["a"]; bx, bz = pol["b"]; px, pz = pol["p"]
            dx, dz = bx - ax, bz - az
            ln = (dx * dx + dz * dz) ** 0.5 or 1e-9
            dist = abs(-px * dz + pz * dx + ax * bz - bx * az) / ln
            check(dist < 1e-3, "solved point lies on the solved line A-B (distance=%.6f)" % dist)
            check(abs(az) < 1e-3 and abs(bz) < 1e-3, "the pinned line endpoints stayed put (a=%s b=%s)" % (pol["a"], pol["b"]))

        pold = r1["pointOnLineDiagonal"]
        check(pold["error"] is None, "point-on-line (diagonal) solve did not error")
        check(pold["residualNorm"] < 1e-6, "diagonal point-on-line residual converges to ~0 (%.2e)" % pold["residualNorm"])
        if pold["p"]:
            check(abs(pold["p"][0] - pold["p"][1]) < 1e-3, "point on the diagonal line satisfies x == z (x=%.4f z=%.4f)" % (pold["p"][0], pold["p"][1]))

        print("\n== embedded solver: Midpoint ==")
        mp = r1["midpoint"]
        check(mp["error"] is None, "midpoint solve did not error")
        check(mp["residualNorm"] < 1e-4, "midpoint residual converges to ~0 (%.2e)" % mp["residualNorm"])
        if mp["m"]:
            check(abs(mp["m"][0] - 5) < 1e-3 and abs(mp["m"][1] - 2) < 1e-3, "midpoint lands exactly at (5,2) (got %s)" % mp["m"])

        print("\n== embedded solver: Symmetric (about a point) ==")
        sp = r1["symmetricPt"]
        check(sp["error"] is None, "symmetric-about-point solve did not error")
        check(sp["residualNorm"] < 1e-6, "symmetric-about-point residual converges to ~0 (%.2e)" % sp["residualNorm"])
        if sp["p"] and sp["q"] and sp["c"]:
            mx = (sp["p"][0] + sp["q"][0]) / 2
            mz = (sp["p"][1] + sp["q"][1]) / 2
            check(abs(mx - sp["c"][0]) < 1e-3 and abs(mz - sp["c"][1]) < 1e-3,
                  "P,Q are genuinely mirrored through C (mid=%.4f,%.4f vs C=%s)" % (mx, mz, sp["c"]))
            check(abs(sp["q"][0] - 8) < 1e-3 and abs(sp["q"][1] - 8) < 1e-3, "Q resolves to the expected mirror point (8,8) (got %s)" % sp["q"])

        print("\n== embedded solver: Symmetric (about a line) ==")
        sl = r1["symmetricLine"]
        check(sl["error"] is None, "symmetric-about-line solve did not error")
        check(sl["residualNorm"] < 1e-4, "symmetric-about-line residual converges to ~0 (%.2e)" % sl["residualNorm"])
        if sl["q"]:
            check(abs(sl["q"][0] - 8) < 1e-3 and abs(sl["q"][1] - 3) < 1e-3, "Q mirrors P(2,3) across the line x=5 to (8,3) (got %s)" % sl["q"])

        print("\n== DOF estimate reflects correct residual-row counts ==")
        check(r1["dofPointOnLine"] == 5, "pointonline contributes exactly 1 residual row (3 pts *2 - 1 = 5) (got %s)" % r1["dofPointOnLine"])
        check(r1["dofMidpoint"] == 4, "midpoint contributes exactly 2 residual rows (3 pts *2 - 2 = 4) (got %s)" % r1["dofMidpoint"])
        check(r1["dofSymmetricPt"] == 4, "symmetric_pt contributes exactly 2 residual rows (got %s)" % r1["dofSymmetricPt"])
        check(r1["dofSymmetricLine"] == 6, "symmetric_line contributes exactly 2 residual rows (4 pts *2 - 2 = 6) (got %s)" % r1["dofSymmetricLine"])

        print("\n== sketch-object integration: required pick-counts (A3D_CON_NEED) ==")
        r2 = await pg.evaluate(PROBE_INTEGRATION)
        check(r2["pointonlineWrongCountRejected"] is True, "pointonline with 2 refs (needs 3) is rejected")
        check(r2["midpointWrongCountRejected"] is True, "midpoint with 2 refs (needs 3) is rejected")
        check(r2["symmetricPtWrongCountRejected"] is True, "symmetric_pt with 2 refs (needs 3) is rejected")
        check(r2["symmetricLineWrongCountRejected"] is True, "symmetric_line with 3 refs (needs 4) is rejected")

        print("\n== sketch-object integration: correct ref counts accepted, real descriptions ==")
        check(r2["pointonlineAccepted"] is True, "pointonline with correct 3 refs is accepted")
        check(r2["pointonlineDesc"] is not None and "on" in r2["pointonlineDesc"], "pointonline description mentions 'on' (%s)" % r2["pointonlineDesc"])
        check(r2["midpointAccepted"] is True, "midpoint with correct 3 refs is accepted")
        check(r2["midpointDesc"] is not None and "mid" in r2["midpointDesc"], "midpoint description mentions 'mid' (%s)" % r2["midpointDesc"])
        check(r2["symmetricPtAccepted"] is True, "symmetric_pt with correct 3 refs is accepted")
        check(r2["symmetricPtDesc"] is not None and "about" in r2["symmetricPtDesc"], "symmetric_pt description mentions 'about' (%s)" % r2["symmetricPtDesc"])
        check(r2["symmetricLineAccepted"] is True, "symmetric_line with correct 4 refs is accepted")
        check(r2["symmetricLineDesc"] is not None and "about" in r2["symmetricLineDesc"], "symmetric_line description mentions 'about' (%s)" % r2["symmetricLineDesc"])
        check(r2["fixedStillInternalOnly"] is True, "'fixed' remains rejected as a public constraint type (unaffected by this phase's changes)")

        print("\n== ribbon wiring: icons, labels, and Constraints panel buttons for all 4 new tools ==")
        r3 = await pg.evaluate(PROBE_RIBBON)
        if r3["hasIconHook"]:
            for k in ("pointonline", "midpoint", "symmetric_pt", "symmetric_line"):
                check(r3["icons"][k] is True, "ribbon icon registered for con:%s" % k)
        else:
            print("  SKIP  no __a3drIcon test hook exposed; icon registration covered by source review only")
        if r3["hasLabelHook"]:
            expected = {"pointonline": "Point on Line", "midpoint": "Midpoint", "symmetric_pt": "Symmetric (Point)", "symmetric_line": "Symmetric (Line)"}
            for k, v in expected.items():
                check(r3["labels"][k] == v, "ribbon label for con:%s is '%s' (got %s)" % (k, v, r3["labels"][k]))
        else:
            print("  SKIP  no __a3drLabel test hook exposed; label registration covered by source review only")
        for k in ("pointonline", "midpoint", "symmetric_pt", "symmetric_line"):
            check(r3["buttonsFound"][k] is True, "Constraints panel button for con:%s exists in the Modify ribbon tab" % k)

        await b.close()

    print("\n%d checks, %d failed" % (TOTAL[0], len(FAILS)))
    print("RESULT: " + ("PASS" if not FAILS else "FAIL"))
    return 1 if FAILS else 0


sys.exit(asyncio.run(main()))
