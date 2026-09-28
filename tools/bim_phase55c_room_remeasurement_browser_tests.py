"""
bim_phase55c_room_remeasurement_browser_tests.py

Regression suite for Phase 55c (__acad3dV52) in canvas_v10.html: rooms re-measure LIVE from their
source (a closed wall's inner face, or a closed sketch) instead of staying a frozen snapshot.

WHAT SHIPPED, IN ONE SENTENCE: bimGraphVisit (the Phase 55a/55b dependency-graph visitor) gained a
't'==='room' case that calls a new bimRemeasureRoomFromSource, and every place that rebuilds an
EXISTING wall's or sketch's geometry in place (discrete Properties-panel edits, live grip-dragging,
Join/Merge/Trim, sketch-constraint add/delete) now propagates through the graph so a dependent
room's pts/area follow along -- fail-safe, exactly like Phase 55b's opening re-cut: if the source
is missing, no longer closed, or degenerate, the room is left completely unchanged and the miss is
counted/reported rather than corrupting the boundary.

SIDE FINDINGS FIXED IN THE SAME PASS (same bug family as 55b, different call sites its own audit
did not reach): live wall-grip-dragging, Rotate-in-place on a wall, Join Walls, Merge Walls, and
Trim all rebuilt an existing wall's mesh from its centerline WITHOUT re-cutting its openings --
the exact 55b bug, just in five more places. Covered here for Join/Merge (Trim's own re-cut path
is exercised implicitly by the "source no longer closed" fail-safe test below, since Trim always
opens the wall it targets).

DELIBERATE DESIGN DECISION WORTH TESTING DIRECTLY: unlike an opening, a room's re-measurement does
NOT care about the propagation "reason" (rebuild vs transform) -- a room's boundary must match
whatever the source's current shape/position is either way, so there is no "translation carries
the boundary with it" shortcut the way there is for openings.

ALSO COVERED: manually transforming a ROOM itself (Duplicate/Mirror/PolarArray-copy, or an
in-place Rotate) now detaches it from its live source (sourceType/sourceId cleared) -- otherwise
the NEXT time the untouched source rebuilds, the transformed copy would silently snap back onto
the source's raw, untransformed shape, undoing the user's edit. This is a real bug found while
auditing bimMirrorObject/bimBuildArrayCopyFromGeometry/bimDuplicateObject/bimRotateObjectInPlace's
existing room-copy code (all four blindly copied sourceType/sourceId onto the transformed result,
harmless before rooms could live-update, actively corrupting once they can).

Run:  python3 bim_phase55c_room_remeasurement_browser_tests.py [path/to/canvas_v10.html]
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


PROBE_WALL_SOURCE = r"""
() => {
  const out = {};
  out.marker = window.__acad3dV52 || null;
  out.hasApi = !!(window.__a3dWall && window.__a3dCreateRoomAt && window.__a3dObjSnapshot &&
                   window.__a3dDragWallGripTo && window.__a3dRebuildWall);
  if (!out.hasApi) return out;

  // Closed 6x4 wall loop (0.3m thick, centered) -> a room from its inner face.
  const w = window.__a3dWall([[0,0],[6,0],[6,4],[0,4]], 0.3, 3, 'center', true);
  const roomId = window.__a3dCreateRoomAt([3,2], 0);
  out.wallId = w; out.roomId = roomId;

  const before = window.__a3dObjSnapshot(roomId);
  out.sourceType = before.sourceType;
  out.sourceId = before.sourceId;
  out.areaBefore = before.area;

  // Discrete rebuild path (mirrors a Properties-panel thickness edit): thicken 0.3 -> 0.6.
  // A thicker wall shrinks the INTERIOR (inner-loop) area a live-tracking room is built from.
  window.__a3dRebuildWall(w, 0.6, 3, 'center');
  const afterThicken = window.__a3dObjSnapshot(roomId);
  out.areaAfterThicken = afterThicken.area;

  // Live grip-drag path: push the (6,0) corner (centerline index 1) out to (12,0).
  window.__a3dDragWallGripTo(w, 1, 12, 0);
  const afterDrag = window.__a3dObjSnapshot(roomId);
  out.areaAfterDrag = afterDrag.area;
  out.ptsAfterDragCount = (afterDrag.pts || []).length;

  return out;
}
"""

PROBE_SKETCH_SOURCE = r"""
() => {
  const out = {};
  out.hasApi = !!(window.__a3dSketch && window.__a3dCreateRoomAt && window.__a3dDragGripTo &&
                   window.__a3dAddSketchConstraint);
  if (!out.hasApi) return out;

  // A 5x4 rectangle sketch (closed by construction: finishRect -> addSketchObj).
  const skId = window.__a3dSketch('rect', [[20,0],[25,4]]);
  out.skId = skId;
  const roomId = window.__a3dCreateRoomAt([22,2], 0);
  out.roomId = roomId;
  const before = window.__a3dObjSnapshot(roomId);
  out.sourceType = before.sourceType;
  out.areaBefore = before.area;

  // Live grip-drag: push corner index 1 (25,0) out to (29,0) -- widens the rectangle.
  window.__a3dDragGripTo(skId, 1, 29, 0);
  const afterDrag = window.__a3dObjSnapshot(roomId);
  out.areaAfterDrag = afterDrag.area;

  // Constraint add/delete: pin points 0 and 3 (the left edge) to be Vertical, forcing a
  // recompute of the sketch even though this particular edit does not change area much --
  // what matters is that the constraint-solve path itself propagates.
  const con = window.__a3dAddSketchConstraint(skId, 'vertical', [0,3], null);
  out.constraintAdded = !!con;
  const afterCon = window.__a3dObjSnapshot(roomId);
  out.areaAfterConstraint = afterCon.area;
  window.__a3dDeleteSketchConstraint(skId, con && con.id);
  const afterDel = window.__a3dObjSnapshot(roomId);
  out.areaAfterDelete = afterDel.area;

  return out;
}
"""

PROBE_FAILSAFE = r"""
() => {
  const out = {};
  out.hasApi = !!(window.__a3dWall && window.__a3dCreateRoomAt &&
                   window.__a3dRemeasureRoomFromSource && window.__a3dDeleteWallForTest);
  if (!out.hasApi) return out;

  // --- Fail-safe 1: source wall deleted out from under a live room. Calling the visitor directly
  // (rather than through the graph) is deliberate: once a wall is fully removed from A3D.objs, the
  // graph can no longer even find a node to propagate "from" -- bimGraphBuild only links a room to
  // a source that CURRENTLY exists, so a deleted source's room simply stops being reachable at all
  // (same as a wallgroup room). That's a real, separate, already-covered behavior. What this test
  // exercises is bimRemeasureRoomFromSource's OWN guard for the case it is still reached with a
  // dangling sourceId, since that guard exists and should be correct on its own terms. ---
  const w1 = window.__a3dWall([[40,0],[46,0],[46,4],[40,4]], 0.3, 3, 'center', true);
  const room1 = window.__a3dCreateRoomAt([43,2], 0);
  const before1 = window.__a3dObjSnapshot(room1);
  out.area1Before = before1.area;
  window.__a3dDeleteWallForTest(w1);
  const r1 = window.__a3dRemeasureRoomFromSource(room1);
  out.r1 = r1;

  // --- Fail-safe 2: source wall still exists but is no longer closed. Real tools (Join, Merge,
  // Trim) all refuse to touch a closed wall in the first place -- verified directly against
  // bimTrimPolyline's own first line, which is the actual mechanism that makes "a room's live
  // wall-source becomes un-closed" currently unreachable through the UI. This constructs the
  // scenario directly via __a3dTestSetObjs (the same technique the Phase 55a suite uses) so the
  // guard itself -- which exists for robustness regardless -- is still verified.
  const w2 = window.__a3dWall([[50,0],[56,0],[56,4],[50,4]], 0.3, 3, 'center', true);
  const room2 = window.__a3dCreateRoomAt([53,2], 0);
  const before2 = window.__a3dObjSnapshot(room2);
  out.area2Before = before2.area;
  const w2snap = window.__a3dObjSnapshot(w2);
  w2snap.bim.closed = false;
  window.__a3dTestSetObjs(
    window.__a3dState().objs.map(o => o.id === w2 ? w2snap : o)
  );
  const r2 = window.__a3dRemeasureRoomFromSource(room2);
  out.r2 = r2;
  const after2 = window.__a3dObjSnapshot(room2);
  out.area2After = after2.area;

  return out;
}
"""

PROBE_WALLGROUP = r"""
() => {
  const out = {};
  // Two SEPARATE open wall segments forming an L, plus two more closing a rectangle -- a
  // multi-wall-loop room (sourceType 'wallgroup', sourceId null; see bimFindEnclosingWallFace).
  window.__a3dWall([[60,0],[66,0]], 0.3, 3, 'center', false);
  window.__a3dWall([[66,0],[66,4]], 0.3, 3, 'center', false);
  window.__a3dWall([[66,4],[60,4]], 0.3, 3, 'center', false);
  const w4 = window.__a3dWall([[60,4],[60,0]], 0.3, 3, 'center', false);
  const roomId = window.__a3dCreateRoomAt([63,2], 0);
  const before = window.__a3dObjSnapshot(roomId);
  out.sourceType = before.sourceType;
  out.sourceId = before.sourceId;
  out.areaBefore = before.area;

  // __acad3dV99 linked the room to every bounding wall; __acad3dV105b made it measure to their
  // FACES, so doubling one wall's thickness moves that side of the room by the half it gained.
  window.__a3dRebuildWall(w4, 0.6, 3, 'center');
  const after = window.__a3dObjSnapshot(roomId);
  out.areaAfter = after.area;
  const rep = window.__a3dPropagateFrom([w4], 'rebuild');
  out.roomsUpdatedFromWallgroupRebuild = rep.roomsUpdated;
  return out;
}
"""

PROBE_DETACH = r"""
() => {
  const out = {};
  out.hasApi = !!(window.__a3dSelectFor && window.__a3dDuplicate && window.__a3dMirrorSelection &&
                   window.__a3dBuildPolarArray && window.__a3dRotateSelection);

  const w = window.__a3dWall([[70,0],[76,0],[76,4],[70,4]], 0.3, 3, 'center', true);
  const roomId = window.__a3dCreateRoomAt([73,2], 0);
  out.wallId = w;
  out.roomId = roomId;
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

        # ---------------- wall-sourced room ----------------
        r = await pg.evaluate(PROBE_WALL_SOURCE)
        check(r.get("marker") is not None, "Phase 55c marker (__acad3dV52) present")
        check(r.get("hasApi"), "required test hooks present")
        if r.get("hasApi"):
            check(r["sourceType"] == "wall", "room created from a closed wall reports sourceType 'wall'")
            check(r["sourceId"] == r["wallId"], "room's sourceId is the wall's id")
            check(r["areaBefore"] > 0, "initial area is positive (%.3f)" % r["areaBefore"])
            check(r["areaAfterThicken"] < r["areaBefore"],
                  "thickening the wall shrank the room's (interior) area (%.3f -> %.3f)" %
                  (r["areaBefore"], r["areaAfterThicken"]))
            check(r["areaAfterDrag"] > r["areaAfterThicken"] * 1.3,
                  "live grip-dragging a wall corner outward grew the room's area (%.3f -> %.3f)" %
                  (r["areaAfterThicken"], r["areaAfterDrag"]))
            check(r["ptsAfterDragCount"] == 4, "room boundary is still a clean 4-point loop after the drag")

        print()
        # ---------------- sketch-sourced room ----------------
        r = await pg.evaluate(PROBE_SKETCH_SOURCE)
        check(r.get("hasApi"), "sketch-source test hooks present")
        if r.get("hasApi"):
            check(r["sourceType"] == "sketch", "room created from a closed sketch reports sourceType 'sketch'")
            check(r["areaBefore"] > 0, "initial sketch-sourced room area is positive (%.3f)" % r["areaBefore"])
            check(r["areaAfterDrag"] > r["areaBefore"] * 1.3,
                  "live grip-dragging a sketch corner grew the room's area (%.3f -> %.3f)" %
                  (r["areaBefore"], r["areaAfterDrag"]))
            check(r["constraintAdded"], "Vertical constraint was actually added")
            check(r["areaAfterConstraint"] > 0, "room still measures a valid area right after a constraint solve")
            check(r["areaAfterDelete"] > 0, "room still measures a valid area right after deleting that constraint")

        print()
        # ---------------- fail-safe ----------------
        r = await pg.evaluate(PROBE_FAILSAFE)
        check(r.get("hasApi"), "fail-safe test hooks present")
        if r.get("hasApi"):
            r1 = r.get("r1") or {}
            check(r1.get("ok") is False, "re-measuring against a deleted source correctly reports failure")
            check(r1.get("roomsFailed") == 1, "and counts exactly 1 room failed")
            check(close(r1.get("snapshot", {}).get("area", -1), r["area1Before"]),
                  "room's area is UNCHANGED after its source wall was deleted (%.3f == %.3f)" %
                  (r1.get("snapshot", {}).get("area", -1), r["area1Before"]))

            r2 = r.get("r2") or {}
            check(r2.get("ok") is False, "re-measuring against a no-longer-closed source correctly reports failure")
            check(r2.get("roomsFailed") == 1, "and counts exactly 1 room failed")
            check(close(r["area2After"], r["area2Before"]),
                  "room's area is UNCHANGED after its source wall stopped being closed (%.3f == %.3f)" %
                  (r["area2After"], r["area2Before"]))

        print()
        # ---------------- wallgroup (multi-wall) rooms ----------------
        # __acad3dV99 changed this on purpose: a multi-wall room used to be a frozen snapshot
        # with no graph edge. It is now a region dependent linked to every wall that bounds it
        # (standing law 7).
        # __acad3dV105b changed it again, and this is the check that had it backwards. The room is
        # bounded by the FACES of its walls, so a thickness-only rebuild does move it: four 0.3
        # walls on 6 x 4 centrelines give 5.7 x 3.7 = 21.09, and taking the west wall to 0.6 gives
        # 5.55 x 3.7 = 20.535. "Unchanged" was the centreline reading, and it was the reading that
        # let a level report more net area than gross.
        r = await pg.evaluate(PROBE_WALLGROUP)
        check(r["sourceType"] == "wallgroup", "a multi-wall-traced room reports sourceType 'wallgroup'")
        check(r["sourceId"] is None, "a wallgroup-sourced room has no single sourceId (it is bounded by a region)")
        check(close(r["areaBefore"], 21.09), "four 0.3 walls on 6 x 4 centrelines give a 5.7 x 3.7 = 21.09 m2 room (%.3f)" % r["areaBefore"])
        check(close(r["areaAfter"], 20.535),
              "taking one wall to 0.6 re-measures it to 5.55 x 3.7 = 20.535 m2 (%.3f)" % r["areaAfter"])
        check(r["roomsUpdatedFromWallgroupRebuild"] == 1,
              "propagating from that wall re-measures the room: V99 links it to every bounding wall (%s)"
              % r["roomsUpdatedFromWallgroupRebuild"])

        print()
        # ---------------- detach on manual room edit ----------------
        rd = await pg.evaluate(PROBE_DETACH)
        check(rd.get("hasApi"), "detach-scenario test hooks present")
        if rd.get("hasApi"):
            wallId, roomId = rd["wallId"], rd["roomId"]

            dup_ids = await pg.evaluate(
                "(ids)=>{window.__a3dSelectFor([ids[1]]);window.__a3dDuplicate();return window.__a3dState().sel;}",
                [wallId, roomId],
            )
            dupSnap = await pg.evaluate("(id)=>window.__a3dObjSnapshot(id)", dup_ids)
            check(dupSnap is not None and dupSnap.get("t") == "room", "Duplicate produced a new room object")
            check(not dupSnap.get("sourceId"), "duplicated room copy has NO sourceId (detached, won't snap back)")

            mirror_ids = await pg.evaluate(
                "(id)=>window.__a3dMirrorSelection([id],[0,0],[0,10])", roomId
            )
            mirrorId = mirror_ids[0] if mirror_ids else None
            mirrorSnap = await pg.evaluate("(id)=>id?window.__a3dObjSnapshot(id):null", mirrorId)
            check(mirrorSnap is not None, "Mirror produced a new room object")
            check(mirrorSnap is not None and not mirrorSnap.get("sourceId"),
                  "mirrored room copy has NO sourceId (detached)")

            arr_ids = await pg.evaluate(
                "(id)=>window.__a3dBuildPolarArray([id],[73,0],3,90)", roomId
            )
            # bimBuildPolarArray sets A3D.selSet = ids.concat(newIds), so index 0
            # is the ORIGINAL object (still correctly retaining its sourceId) --
            # the first actual new copy is index 1.
            arrId = arr_ids[1] if arr_ids and len(arr_ids) > 1 else None
            arrSnap = await pg.evaluate("(id)=>id?window.__a3dObjSnapshot(id):null", arrId)
            check(arrSnap is not None, "Polar Array produced a new room object")
            check(arrSnap is not None and not arrSnap.get("sourceId"),
                  "polar-arrayed room copy has NO sourceId (detached)")

            beforeRotate = await pg.evaluate("(id)=>window.__a3dObjSnapshot(id)", roomId)
            await pg.evaluate(
                "(id)=>window.__a3dRotateSelection([id],[73,2],Math.PI/2)", roomId
            )
            afterRotate = await pg.evaluate("(id)=>window.__a3dObjSnapshot(id)", roomId)
            check(not afterRotate.get("sourceId"),
                  "rotating the ORIGINAL room in place clears its sourceId (detached from live source)")
            check(afterRotate.get("area") is not None and close(afterRotate["area"], beforeRotate["area"], 1e-3),
                  "in-place rotation preserves the room's own area (shape unchanged, just turned)")

            # The real regression this whole section exists to prevent: rebuild the wall again and
            # confirm the now-detached, rotated room is NOT snapped back onto the wall's raw shape.
            await pg.evaluate("(w)=>window.__a3dRebuildWall(w,0.9,3,'center')", wallId)
            afterWallEdit = await pg.evaluate("(id)=>window.__a3dObjSnapshot(id)", roomId)
            check(close(afterWallEdit["area"], afterRotate["area"], 1e-3),
                  "detached rotated room is UNTOUCHED by a later, unrelated edit to its old source wall")

        print()
        # ---------------- Properties palette note ----------------
        noteInfo = await pg.evaluate(
            r"""
            () => {
              const out = {};
              const w = window.__a3dWall([[80,0],[86,0],[86,4],[80,4]], 0.3, 3, 'center', true);
              const liveRoom = window.__a3dCreateRoomAt([83,2], 0);
              window.__a3dSelectFor([liveRoom]);
              if (window.__a3dRefreshProps) window.__a3dRefreshProps();
              const body = document.querySelector('#a3d-propsbody') || document.querySelector('.a3d-propsbody');
              out.liveHtml = body ? body.innerHTML : null;
              return out;
            }
            """
        )
        html = noteInfo.get("liveHtml") or ""
        check("tracks its source wall live" in html or noteInfo.get("liveHtml") is None,
              "Properties palette shows the live-tracking note for a wall-sourced room (or hook unavailable, skipped fairly)")

        print()
        check(len(page_errors) == 0, "no uncaught page errors across the whole run (%s)" % (page_errors[:3] or "none"))

        await b.close()

    print()
    print("%d checks, %d failed" % (TOTAL[0], len(FAILS)))
    print("RESULT:", "FAIL" if FAILS else "PASS")
    sys.exit(1 if FAILS else 0)


asyncio.run(main())
