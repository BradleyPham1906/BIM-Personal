"""
bim_phase55d_clone_autosync_browser_tests.py

Regression suite for Phase 55d (__acad3dV53) in canvas_v10.html: linked clones auto-sync through
the Phase 55a dependency graph -- the third and last deferred visitor named in 55a's own writeup,
closing the gap left by the other two (55b's openings, 55c's rooms).

WHAT SHIPPED, IN ONE SENTENCE: bimGraphVisit gained an `o.linkSourceId` branch that calls a new
bimSyncOneClone, so every one of the nine existing propagation call sites (wall rebuild/type edit,
Join/Merge/Trim, live wall/sketch grip-drag, sketch constraint add/delete, Rotate-in-place) now
also re-syncs any linked clone downstream of the object it touches -- no more relying on the user
remembering to press Sync Clones. bimSyncOneClone was factored out of the pre-existing
syncLinkedClones (the manual button), so the manual and automatic paths share one implementation
rather than two copies that could drift apart.

FAIL-SAFE, SAME SHAPE AS 55B/55C: if a clone's link source is missing or has no mesh, the clone is
left COMPLETELY UNCHANGED, a console.warn names it, and the miss is counted -- never a corrupted or
blanked-out clone.

ALSO FIXED IN THE SAME PASS: two related, previously-real gaps found while wiring this up --
  - bimRebuildFloor / bimRebuildColumn (the Properties-palette parameter-edit paths for floors and
    columns) did not propagate through the graph AT ALL before this phase, so a floor or column
    clone could never auto-sync no matter what. Both now call bimAfterWallRebuild, same as
    bimRebuildWall already did.
  - Rotate-in-place's floor/column branch also never propagated (only its wall branch did); now all
    three solid kinds do.

DELIBERATE DESIGN DECISION WORTH TESTING DIRECTLY: unlike an opening (which skips a pure
'transform'), a clone sync fires regardless of ctx.reason -- a linked clone tracks its source at a
fixed relative offset, so a pure reposition of the source should carry the clone along exactly as
much as a parametric rebuild should.

ALSO COVERED: detach-on-direct-edit. If a clone is itself directly edited (grip-dragged, rotated in
place, trimmed, joined, merged, or rebuilt through the Properties palette) it has diverged from
being a pure derived copy of its source -- bimPropagateFrom now clears linkSourceId/linkOffset on
any origin object that carries one, the same way Phase 55c detaches a room that is rotated in
place. Without this, the NEXT time the real source rebuilds, the auto-sync visitor would silently
overwrite the user's direct edit to the clone.

ALSO COVERED: a clone-of-clone chain (source -> clone1 -> clone2) syncs both hops correctly in one
propagation pass, a free consequence of the dependency graph's topological ordering rather than
anything explicitly coded for chains.

Run:  python3 bim_phase55d_clone_autosync_browser_tests.py [path/to/canvas_v10.html]
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


def close(a, b, tol=1e-6):
    return abs(a - b) <= tol


def centerline_matches_offset(clone_cl, src_cl, dx, dz):
    """A linked clone's centerline is the source's centerline shifted by its OWN fixed
    linkOffset (dx, dz) -- not identical to the source's raw centerline. cloneLinked/
    bimSyncOneClone both apply [p[0]+dx, p[1]+dz] to every point."""
    if not clone_cl or not src_cl or len(clone_cl) != len(src_cl):
        return False
    for cp, sp in zip(clone_cl, src_cl):
        if not (close(cp[0], sp[0] + dx) and close(cp[1], sp[1] + dz)):
            return False
    return True


PROBE_WALL_CLONE_REBUILD = r"""
() => {
  const out = {};
  out.marker = window.__acad3dV53 || null;
  out.hasApi = !!(window.__a3dWall && window.__a3dCloneLinked && window.__a3dObjSnapshot &&
                   window.__a3dRebuildWall && window.__a3dDragWallGripTo && window.__a3dPropagateFrom);
  if (!out.hasApi) return out;

  const src = window.__a3dWall([[100,0],[106,0]], 0.2, 3, 'center', false);
  const clone = window.__a3dCloneLinked(src, 0, 0, 8);
  out.srcId = src; out.cloneId = clone;

  const before = window.__a3dObjSnapshot(clone);
  out.cloneThicknessBefore = before.bim.thickness;

  // Discrete rebuild path (mirrors a Properties-panel thickness edit).
  const rep = window.__a3dRebuildWall(src, 0.5, 3, 'center');
  out.rebuildOk = rep;
  const afterRebuild = window.__a3dObjSnapshot(clone);
  out.cloneThicknessAfterRebuild = afterRebuild.bim.thickness;
  out.srcThicknessAfterRebuild = window.__a3dObjSnapshot(src).bim.thickness;

  // Live grip-drag path.
  window.__a3dDragWallGripTo(src, 1, 106, 20);
  const afterDrag = window.__a3dObjSnapshot(clone);
  out.cloneCenterlineAfterDrag = afterDrag.bim.centerline;
  out.srcCenterlineAfterDrag = window.__a3dObjSnapshot(src).bim.centerline;

  // The report from an explicit propagate call should count the clone sync.
  const rep2 = window.__a3dPropagateFrom([src], 'rebuild');
  out.rep2ClonesUpdated = rep2.clonesUpdated;
  out.rep2ClonesFailed = rep2.clonesFailed;

  return out;
}
"""

PROBE_JOIN_CLONE = r"""
() => {
  const out = {};
  out.hasApi = !!(window.__a3dWall && window.__a3dCloneLinked && window.__a3dApplyWallJoin);
  if (!out.hasApi) return out;

  const a = window.__a3dWall([[120,0],[126,0]], 0.2, 3, 'center', false);
  const b = window.__a3dWall([[126,0.01],[126,6]], 0.2, 3, 'center', false);
  const cloneOfA = window.__a3dCloneLinked(a, 0, 0, 10);
  out.beforeLen = window.__a3dObjSnapshot(cloneOfA).bim.centerline.length;

  window.__a3dApplyWallJoin(a, b);
  const after = window.__a3dObjSnapshot(cloneOfA);
  out.afterCenterlineA = window.__a3dObjSnapshot(a).bim.centerline;
  out.afterCenterlineClone = after.bim.centerline;
  return out;
}
"""

PROBE_FLOOR_COLUMN_CLONE = r"""
() => {
  const out = {};
  out.hasApi = !!(window.__a3dFloorAt && window.__a3dColumnAt && window.__a3dRebuildFloor &&
                   window.__a3dRebuildColumn && window.__a3dCloneLinked);
  if (!out.hasApi) return out;

  const floor = window.__a3dFloorAt([[140,0],[146,0],[146,5],[140,5]], 0, 0.2, 'Concrete Slab');
  out.floorId = floor;
  const floorClone = window.__a3dCloneLinked(floor, 0, 0, 12);
  out.floorCloneThicknessBefore = window.__a3dObjSnapshot(floorClone).bim.thickness;
  window.__a3dRebuildFloor(floor, 0.35, 'Steel Deck');
  out.floorThicknessAfter = window.__a3dObjSnapshot(floor).bim.thickness;
  out.floorCloneThicknessAfter = window.__a3dObjSnapshot(floorClone).bim.thickness;
  out.floorCloneMaterialAfter = window.__a3dObjSnapshot(floorClone).bim.material;

  const col = window.__a3dColumnAt([150,3], 0, 0.4, 0.4, 3);
  out.colId = col;
  const colClone = window.__a3dCloneLinked(col, 0, 0, 6);
  out.colCloneWidthBefore = window.__a3dObjSnapshot(colClone).bim.width;
  window.__a3dRebuildColumn(col, 0.6, 0.5, 3.5);
  out.colWidthAfter = window.__a3dObjSnapshot(col).bim.width;
  out.colCloneWidthAfter = window.__a3dObjSnapshot(colClone).bim.width;
  out.colCloneHeightAfter = window.__a3dObjSnapshot(colClone).bim.height;

  return out;
}
"""

PROBE_FAILSAFE = r"""
() => {
  const out = {};
  out.hasApi = !!(window.__a3dWall && window.__a3dCloneLinked && window.__a3dSyncOneClone &&
                   window.__a3dDeleteWallForTest);
  if (!out.hasApi) return out;

  const src = window.__a3dWall([[160,0],[166,0]], 0.2, 3, 'center', false);
  const clone = window.__a3dCloneLinked(src, 0, 0, 5);
  const before = window.__a3dObjSnapshot(clone);
  out.thicknessBefore = before.bim.thickness;

  window.__a3dDeleteWallForTest(src);
  const r1 = window.__a3dSyncOneClone(clone);
  out.r1 = r1;

  return out;
}
"""

PROBE_DETACH_ON_DIRECT_EDIT = r"""
() => {
  const out = {};
  out.hasApi = !!(window.__a3dWall && window.__a3dCloneLinked && window.__a3dDragWallGripTo &&
                   window.__a3dObjLinkSource && window.__a3dRebuildWall);
  if (!out.hasApi) return out;

  // Grip-dragging the CLONE's own corner directly should detach it.
  const src1 = window.__a3dWall([[180,0],[186,0]], 0.2, 3, 'center', false);
  const clone1 = window.__a3dCloneLinked(src1, 0, 0, 5);
  out.linkBefore1 = window.__a3dObjLinkSource(clone1);
  window.__a3dDragWallGripTo(clone1, 1, 186, 15);
  out.linkAfter1 = window.__a3dObjLinkSource(clone1);
  // The detached clone's own edit must survive a later, unrelated edit to the OLD source.
  const clone1CenterlineAfterDetach = window.__a3dObjSnapshot(clone1).bim.centerline;
  window.__a3dRebuildWall(src1, 0.5, 3, 'center');
  out.clone1CenterlineAfterSrcRebuild = window.__a3dObjSnapshot(clone1).bim.centerline;
  out.clone1CenterlineAfterDetach = clone1CenterlineAfterDetach;

  // Rotating the CLONE itself in place should also detach it.
  const src2 = window.__a3dWall([[200,0],[206,0]], 0.2, 3, 'center', false);
  const clone2 = window.__a3dCloneLinked(src2, 0, 0, 5);
  out.linkBefore2 = window.__a3dObjLinkSource(clone2);
  window.__a3dSelectFor([clone2]);
  window.__a3dRotateSelection([clone2], [203,15], Math.PI / 6);
  out.linkAfter2 = window.__a3dObjLinkSource(clone2);

  return out;
}
"""

PROBE_CLONE_CHAIN = r"""
() => {
  const out = {};
  out.hasApi = !!(window.__a3dWall && window.__a3dCloneLinked && window.__a3dRebuildWall &&
                   window.__a3dObjSnapshot);
  if (!out.hasApi) return out;

  const src = window.__a3dWall([[220,0],[226,0]], 0.2, 3, 'center', false);
  const clone1 = window.__a3dCloneLinked(src, 0, 0, 5);
  const clone2 = window.__a3dCloneLinked(clone1, 0, 0, 5);
  out.clone1Link = window.__a3dObjLinkSource(clone1);
  out.clone2Link = window.__a3dObjLinkSource(clone2);

  window.__a3dRebuildWall(src, 0.55, 3, 'center');
  out.srcThicknessAfter = window.__a3dObjSnapshot(src).bim.thickness;
  out.clone1ThicknessAfter = window.__a3dObjSnapshot(clone1).bim.thickness;
  out.clone2ThicknessAfter = window.__a3dObjSnapshot(clone2).bim.thickness;

  return out;
}
"""

PROBE_PROPS_NOTE = r"""
() => {
  const out = {};
  out.hasApi = !!(window.__a3dWall && window.__a3dCloneLinked && window.__a3dSelectFor && window.__a3dRefreshProps);
  if (!out.hasApi) return out;

  const src = window.__a3dWall([[240,0],[246,0]], 0.2, 3, 'center', false);
  window.__a3dCloneLinked(src, 0, 0, 5);
  window.__a3dSelectFor([src]);
  window.__a3dRefreshProps();
  const html = document.getElementById('a3d-propsbody') ? document.getElementById('a3d-propsbody').innerHTML : '';
  out.hasSyncButton = html.indexOf('data-propf="syncclones"') >= 0;
  out.hasAutoNote = html.indexOf('Clones follow this object automatically') >= 0;
  return out;
}
"""


async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        pg = await b.new_page()
        page_errors = []
        pg.on("pageerror", lambda e: page_errors.append(str(e)))
        await pg.goto(pathlib.Path(TARGET).absolute().as_uri())
        await pg.wait_for_timeout(1500)
        await pg.evaluate("()=>{try{localStorage.clear();}catch(e){}}")
        await pg.evaluate("()=>{ if(window.__a3dEnter) window.__a3dEnter(); }")
        await pg.wait_for_timeout(300)

        # ---------------- wall clone: rebuild + live grip-drag ----------------
        r = await pg.evaluate(PROBE_WALL_CLONE_REBUILD)
        check(r.get("marker") is not None, "Phase 55d marker (__acad3dV53) present")
        check(r.get("hasApi"), "required test hooks present")
        if r.get("hasApi"):
            check(close(r["cloneThicknessBefore"], 0.2), "clone starts out matching the source's thickness")
            check(close(r["srcThicknessAfterRebuild"], 0.5), "source thickness was actually rebuilt")
            check(close(r["cloneThicknessAfterRebuild"], 0.5),
                  "clone auto-synced to the new thickness after a discrete rebuild, no Sync Clones press needed")
            check(centerline_matches_offset(r["cloneCenterlineAfterDrag"], r["srcCenterlineAfterDrag"], 0, 8),
                  "clone's centerline matches the source's after a live grip-drag, still shifted by its own +8 Z linkOffset")
            check(r["rep2ClonesUpdated"] >= 1, "bimPropagateFrom's report counts the clone as updated (%d)" % r["rep2ClonesUpdated"])
            check(r["rep2ClonesFailed"] == 0, "and reports zero clone failures")

        print()
        # ---------------- Join Walls also propagates to a clone of one of the joined walls ----------------
        r = await pg.evaluate(PROBE_JOIN_CLONE)
        check(r.get("hasApi"), "join-clone test hooks present")
        if r.get("hasApi"):
            check(centerline_matches_offset(r["afterCenterlineClone"], r["afterCenterlineA"], 0, 10),
                  "Join Walls' corner-mitered centerline propagates to a clone of the joined wall, "
                  "still shifted by its own +10 Z linkOffset")

        print()
        # ---------------- floor/column: previously-missing propagation now wired ----------------
        r = await pg.evaluate(PROBE_FLOOR_COLUMN_CLONE)
        check(r.get("hasApi"), "floor/column test hooks present")
        if r.get("hasApi"):
            check(close(r["floorCloneThicknessBefore"], 0.2), "floor clone starts out matching the source")
            check(close(r["floorThicknessAfter"], 0.35), "floor source thickness was actually rebuilt")
            check(close(r["floorCloneThicknessAfter"], 0.35),
                  "floor clone auto-synced -- bimRebuildFloor did not propagate at all before Phase 55d")
            check(r["floorCloneMaterialAfter"] == "Steel Deck", "floor clone's material also followed the rebuild")
            check(close(r["colCloneWidthBefore"], 0.4), "column clone starts out matching the source")
            check(close(r["colWidthAfter"], 0.6), "column source width was actually rebuilt")
            check(close(r["colCloneWidthAfter"], 0.6),
                  "column clone auto-synced -- bimRebuildColumn did not propagate at all before Phase 55d")
            check(close(r["colCloneHeightAfter"], 3.5), "column clone's height also followed the rebuild")

        print()
        # ---------------- fail-safe: link source deleted out from under a clone ----------------
        r = await pg.evaluate(PROBE_FAILSAFE)
        check(r.get("hasApi"), "fail-safe test hooks present")
        if r.get("hasApi"):
            r1 = r.get("r1") or {}
            check(r1.get("ok") is False, "re-syncing against a deleted link source correctly reports failure")
            check(r1.get("clonesFailed") == 1, "and counts exactly 1 clone failed")
            check(close(r1.get("snapshot", {}).get("bim", {}).get("thickness", -1), r["thicknessBefore"]),
                  "clone's geometry is UNCHANGED after its link source was deleted (%.3f == %.3f)" %
                  (r1.get("snapshot", {}).get("bim", {}).get("thickness", -1), r["thicknessBefore"]))

        print()
        # ---------------- detach on direct edit ----------------
        r = await pg.evaluate(PROBE_DETACH_ON_DIRECT_EDIT)
        check(r.get("hasApi"), "detach-scenario test hooks present")
        if r.get("hasApi"):
            check(r["linkBefore1"] is not None, "clone starts out linked to its source")
            check(r["linkAfter1"] is None, "grip-dragging the CLONE's own corner detaches it from its source")
            check(r["clone1CenterlineAfterSrcRebuild"] == r["clone1CenterlineAfterDetach"],
                  "detached clone's own edit is UNTOUCHED by a later, unrelated rebuild of its old source")
            check(r["linkBefore2"] is not None, "second clone starts out linked to its source")
            check(r["linkAfter2"] is None, "rotating the CLONE itself in place also detaches it from its source")

        print()
        # ---------------- clone-of-clone chain ----------------
        r = await pg.evaluate(PROBE_CLONE_CHAIN)
        check(r.get("hasApi"), "clone-chain test hooks present")
        if r.get("hasApi"):
            check(r["clone1Link"] is not None and r["clone2Link"] is not None, "both hops of the chain start out linked")
            check(close(r["srcThicknessAfter"], 0.55), "chain source thickness was actually rebuilt")
            check(close(r["clone1ThicknessAfter"], 0.55), "first hop (clone-of-source) auto-synced")
            check(close(r["clone2ThicknessAfter"], 0.55),
                  "second hop (clone-of-clone) ALSO auto-synced in the same propagation pass -- a free "
                  "consequence of the graph's topological ordering, not special-cased code")

        print()
        # ---------------- Properties palette wording ----------------
        r = await pg.evaluate(PROBE_PROPS_NOTE)
        check(r.get("hasApi"), "props-note test hooks present (or skipped fairly if UI hooks unavailable)")
        if r.get("hasApi"):
            check(r.get("hasSyncButton"), "Properties palette still shows the Sync Clones button")
            check(r.get("hasAutoNote"), "Properties palette now notes clones follow the source automatically")

        print()
        check(not page_errors, "no uncaught page errors across the whole run (%s)" % (page_errors[:1] or "none"))

        print("\n%d checks, %d failed" % (TOTAL[0], len(FAILS)))
        if FAILS:
            print("\nFAILED:")
            for m in FAILS:
                print("  - " + m)
        bad = FAILS or page_errors
        print("RESULT:", "FAIL" if bad else "PASS")
        await b.close()
        sys.exit(1 if bad else 0)


asyncio.run(main())
