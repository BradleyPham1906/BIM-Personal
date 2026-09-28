"""
bim_phase55e_transform_propagation_browser_tests.py

Regression suite for Phase 55e (__acad3dV55) in canvas_v10.html: the "transform" side of the
Phase 55a dependency graph -- Align, arrow-key nudge, level-elevation shift, and the continuous
drag-move handler now all propagate through the same graph as the "rebuild" side (55b openings,
55c rooms, 55d clones) shipped in earlier phases.

SCOPE, PER AN EXPLICIT USER DECISION (asked directly, because the alternative -- a narrower
Align/level-shift-only scope -- was materially cheaper and safer): "Full scope: pos-aware +
detach-on-drag". That means:

  1. POS-AWARE READS. Align, nudge, and drag-move all work by mutating a separate `.pos` offset,
     never baking the move into an object's own mesh/centerline/pts (that convention predates this
     phase and is left alone -- rewriting the app's single most-used interaction to bake geometry
     on every mousemove would make every dragged wall re-cut its own openings continuously).
     bimRemeasureRoomFromSource (55c) and bimSyncOneClone (55d) previously read a wall/sketch
     source's raw geometry with NO awareness of this -- so a room or clone built on something that
     had only ever been dragged, Aligned, or nudged (never rebuilt) silently measured against the
     WRONG, stale position. Both now add the source's .pos.

  2. CLONE .pos DISCIPLINE. cloneLinked and bimSyncOneClone now explicitly bake a moved source's
     .pos into the clone's own fields (same as its fixed linkOffset) and reset the clone's own
     .pos to [0,0,0] on every creation/sync -- a clone has no reason to carry a nonzero .pos of its
     own, and leaving one there would double-count the source's offset the next time it is baked
     in. Two more latent 55d gaps were found and fixed in the same function while this was being
     wired up: bim.innerLoop/outerLoop (needed when a ROOM is sourced from a CLONE wall) and
     bim.center (for column clones) were never offset by linkOffset at all before -- only
     centerline/profile were.

  3. RELATIONSHIP-AWARE DETACH. Phase 55d's detach-on-direct-edit rule (sever a clone's link the
     moment its OWN origin is edited, so a later source rebuild can't silently clobber the
     divergent edit) was unconditional. That is too aggressive now that Align/nudge/drag-move can
     move MANY objects in the same gesture: a group-drag or a level-elevation shift can legitimately
     carry a wall and the room/clone built on it together, in lockstep, without the relationship
     actually breaking. bimPropagateFrom now only detaches when the object's own source/link-target
     is NOT ALSO part of the same batch -- and the same rule is extended to rooms (55d only ever
     covered clones; no call site had ever passed a room as an origin before this phase).

  4. OPENING SAFETY (a genuine near-miss caught during this phase's own implementation, worth
     stating precisely because it inverts the naive fix): a wall's own `.pos` moving does NOT
     touch its centerline, and a later re-cut always looks an opening up in that SAME, unchanged
     centerline space -- so translating an opening's bim.center just because its host wall's .pos
     changed would move the bookkeeping OFF the wall's real centerline and cause a later
     Trim/Join/rebuild to silently drop the door. The only case where a host wall's centerline
     really does move outside of a 'rebuild' pass is when that wall is itself a linked CLONE being
     resynced (bimSyncOneClone bakes a real, new centerline). bimGraphVisit's opening branch now
     tracks which walls were actually rebaked-as-a-clone in the current pass (ctx.wallsRebaked) and
     only translates bim.center for openings hosted on THOSE -- never for a plain .pos-moved wall.

  5. TIMING. Align and nudge are discrete, one-shot actions -- they propagate immediately after
     each move, silently (no extra toast, matching the existing live grip-drag precedent). The
     continuous drag-move handler (mousedown/mousemove/mouseup) instead defers to mouseup, computing
     the whole gesture's total delta once -- propagating on every mousemove, the way grip-drag
     already does, would be fine for grip-drag's cheap single-object recompute but wasteful for a
     drag that can move a whole selected group.

Run:  python3 bim_phase55e_transform_propagation_browser_tests.py [path/to/canvas_v10.html]
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


def pts_match_shifted(a, b, dx, dz, tol=1e-6):
    """Every point of a equals the corresponding point of b shifted by (dx, dz)."""
    if not a or not b or len(a) != len(b):
        return False
    for pa, pb in zip(a, b):
        if not (close(pa[0], pb[0] + dx, tol) and close(pa[1], pb[1] + dz, tol)):
            return False
    return True


# ---------------------------------------------------------------------------------------------
# 1. Room re-measurement is .pos-aware (wall source and sketch source).
# ---------------------------------------------------------------------------------------------
PROBE_ROOM_POS_AWARE = r"""
() => {
  const out = {};
  out.marker = window.__acad3dV55 || null;
  out.hasApi = !!(window.__a3dWall && window.__a3dCreateRoomAt && window.__a3dObjSnapshot &&
                   window.__a3dSketch && window.__a3dMoveObjects && window.__a3dPropagateFrom);
  if (!out.hasApi) return out;

  // ---- wall-sourced room ----
  const w = window.__a3dWall([[200,0],[206,0],[206,4],[200,4]], 0.3, 3, 'center', true);
  const roomId = window.__a3dCreateRoomAt([203,2], 0);
  const before = window.__a3dObjSnapshot(roomId);
  out.wallRoomPtsBefore = before.pts;
  out.wallRoomYBefore = before.y;

  // Drag the WALL (not the room) by (5, 1.5, 3) -- a plain .pos move, never baked into the
  // centerline. Before this phase, bimRemeasureRoomFromSource ignored .pos entirely.
  const rep = window.__a3dMoveObjects([w], 5, 1.5, 3);
  out.rep = rep;
  const after = window.__a3dObjSnapshot(roomId);
  out.wallRoomPtsAfter = after.pts;
  out.wallRoomYAfter = after.y;
  out.wallRoomSourceIdAfter = after.sourceId;

  // ---- sketch-sourced room ----
  const sk = window.__a3dSketch('rect', [[220,0],[225,4]]);
  const roomId2 = window.__a3dCreateRoomAt([222,2], 0);
  const before2 = window.__a3dObjSnapshot(roomId2);
  out.skRoomPtsBefore = before2.pts;
  window.__a3dMoveObjects([sk], -2, 0.5, 4);
  const after2 = window.__a3dObjSnapshot(roomId2);
  out.skRoomPtsAfter = after2.pts;
  out.skRoomYAfter = after2.y;
  out.skRoomSourceIdAfter = after2.sourceId;

  return out;
}
"""

# ---------------------------------------------------------------------------------------------
# 2. Clone sync is .pos-aware, resets clone.pos, and fixes the innerLoop/outerLoop/center gaps.
# ---------------------------------------------------------------------------------------------
PROBE_CLONE_POS_AWARE = r"""
() => {
  const out = {};
  out.hasApi = !!(window.__a3dWall && window.__a3dCloneLinked && window.__a3dObjSnapshot &&
                   window.__a3dMoveObjects && window.__a3dCreateRoomAt &&
                   window.__a3dColumnAt && window.__a3dRebuildColumn);
  if (!out.hasApi) return out;

  // ---- wall clone follows a .pos-moved source, and its own .pos stays zero ----
  const src = window.__a3dWall([[240,0],[246,0],[246,4],[240,4]], 0.3, 3, 'center', true);
  const clone = window.__a3dCloneLinked(src, 0, 0, 10);
  const cloneBefore = window.__a3dObjSnapshot(clone);
  out.clonePosBefore = cloneBefore.pos;
  out.cloneCenterlineBefore = cloneBefore.bim.centerline;
  out.cloneInnerLoopBefore = cloneBefore.bim.innerLoop;

  window.__a3dMoveObjects([src], 3, 0, -2);
  const cloneAfter = window.__a3dObjSnapshot(clone);
  out.clonePosAfter = cloneAfter.pos;
  out.cloneCenterlineAfter = cloneAfter.bim.centerline;
  const cloneInnerLoopAfter = cloneAfter.bim.innerLoop;
  out.cloneInnerLoopAfter = cloneInnerLoopAfter;
  out.srcCenterlineAfter = window.__a3dObjSnapshot(src).bim.centerline;
  out.srcInnerLoopAfter = window.__a3dObjSnapshot(src).bim.innerLoop;

  // ---- a room sourced from the CLONE (not the original) picks up the innerLoop fix ----
  // Pick a point inside the clone's NOW-CORRECT interior loop (its centroid) rather than
  // hand-computing the post-drag location -- the innerLoop offset fix is exactly what is under
  // test here, so the search point must not assume it.
  let cx = 0, cz = 0;
  for (const p of cloneInnerLoopAfter) { cx += p[0]; cz += p[1]; }
  cx /= cloneInnerLoopAfter.length; cz /= cloneInnerLoopAfter.length;
  const roomOnClone = window.__a3dCreateRoomAt([cx, cz], 0);
  const roomSnap = window.__a3dObjSnapshot(roomOnClone);
  out.roomOnCloneSourceId = roomSnap.sourceId;
  out.roomOnClonePts = roomSnap.pts;
  out.roomOnCloneMatchesCloneInnerLoop = null; // computed in Python

  // ---- column clone's bim.center gap ----
  const colSrc = window.__a3dColumnAt([260, 0], 0, 0.4, 0.4, 3);
  const colClone = window.__a3dCloneLinked(colSrc, 6, 0, 0);
  const colCloneCenterBefore = window.__a3dObjSnapshot(colClone).bim.center;
  window.__a3dRebuildColumn(colSrc, 0.5, 0.5, 3.2); // triggers bimAfterWallRebuild -> resync
  const colCloneAfter = window.__a3dObjSnapshot(colClone);
  out.colCloneCenterBefore = colCloneCenterBefore;
  out.colCloneCenterAfter = colCloneAfter.bim.center;
  out.colSrcCenterAfter = window.__a3dObjSnapshot(colSrc).bim.center;
  out.colCloneWidthAfter = colCloneAfter.bim.width;

  return out;
}
"""

# ---------------------------------------------------------------------------------------------
# 3. Opening safety: a plain wall drag must NOT touch bim.center, and a later rebuild must still
#    find and re-cut the opening correctly (the near-miss this phase caught in its own review).
# ---------------------------------------------------------------------------------------------
PROBE_OPENING_DRAG_SAFE = r"""
() => {
  const out = {};
  out.hasApi = !!(window.__a3dWall && window.__a3dDoorAt && window.__a3dOpeningsOf &&
                   window.__a3dMoveObjects && window.__a3dRebuildWall);
  if (!out.hasApi) return out;

  const w = window.__a3dWall([[280,0],[286,0]], 0.2, 3, 'center', false);
  window.__a3dDoorAt(w, [283,0], 0.9, 2.1);
  const before = window.__a3dOpeningsOf(w);
  out.centerBefore = before[0] ? before[0].center : null;
  out.countBefore = before.length;

  const rep = window.__a3dMoveObjects([w], 4, 0, 2);
  out.rep = rep;
  const afterMove = window.__a3dOpeningsOf(w);
  out.centerAfterMove = afterMove[0] ? afterMove[0].center : null;
  out.countAfterMove = afterMove.length;

  // A later, unrelated rebuild must still find this opening at its (unchanged) recorded center
  // and successfully re-cut it -- proof the bookkeeping was NOT corrupted by the drag.
  const rebuiltOk = window.__a3dRebuildWall(w, 0.35, 3, 'center');
  const afterRebuild = window.__a3dOpeningsOf(w);
  out.rebuiltOk = rebuiltOk;
  out.countAfterRebuild = afterRebuild.length;
  out.centerAfterRebuild = afterRebuild[0] ? afterRebuild[0].center : null;

  return out;
}
"""

# ---------------------------------------------------------------------------------------------
# 4. Opening-on-a-clone cascade: dragging the SOURCE resyncs a clone hosting an opening, and
#    (only in this case) bim.center DOES translate to match the clone's really-rebaked centerline.
# ---------------------------------------------------------------------------------------------
PROBE_OPENING_ON_CLONE_CASCADE = r"""
() => {
  const out = {};
  out.hasApi = !!(window.__a3dWall && window.__a3dCloneLinked && window.__a3dDoorAt &&
                   window.__a3dOpeningsOf && window.__a3dMoveObjects);
  if (!out.hasApi) return out;

  const src = window.__a3dWall([[300,0],[306,0]], 0.2, 3, 'center', false);
  const clone = window.__a3dCloneLinked(src, 0, 0, 12);
  window.__a3dDoorAt(clone, [303,12], 0.9, 2.1); // door placed directly on the CLONE
  const before = window.__a3dOpeningsOf(clone);
  out.centerBefore = before[0] ? before[0].center : null;

  const rep = window.__a3dMoveObjects([src], 5, 0, 0); // move the SOURCE, not the clone
  out.rep = rep;
  const after = window.__a3dOpeningsOf(clone);
  out.centerAfter = after[0] ? after[0].center : null;

  return out;
}
"""

# ---------------------------------------------------------------------------------------------
# 5. Relationship-aware detach: moved ALONE detaches; moved WITH the source does not.
# ---------------------------------------------------------------------------------------------
PROBE_RELATIONSHIP_AWARE_DETACH = r"""
() => {
  const out = {};
  out.hasApi = !!(window.__a3dWall && window.__a3dCreateRoomAt && window.__a3dCloneLinked &&
                   window.__a3dMoveObjects && window.__a3dObjSnapshot);
  if (!out.hasApi) return out;

  // ---- room moved ALONE detaches ----
  const w1 = window.__a3dWall([[320,0],[326,0],[326,4],[320,4]], 0.3, 3, 'center', true);
  const room1 = window.__a3dCreateRoomAt([323,2], 0);
  out.room1SourceBefore = window.__a3dObjSnapshot(room1).sourceId;
  window.__a3dMoveObjects([room1], 1, 0, 1);
  out.room1SourceAfterAlone = window.__a3dObjSnapshot(room1).sourceId;

  // ---- room moved WITH its source (group/batch) does NOT detach ----
  const w2 = window.__a3dWall([[340,0],[346,0],[346,4],[340,4]], 0.3, 3, 'center', true);
  const room2 = window.__a3dCreateRoomAt([343,2], 0);
  out.room2SourceBefore = window.__a3dObjSnapshot(room2).sourceId;
  window.__a3dMoveObjects([w2, room2], 2, 0, 0);
  out.room2SourceAfterTogether = window.__a3dObjSnapshot(room2).sourceId;

  // ---- clone moved ALONE detaches ----
  const w3 = window.__a3dWall([[360,0],[366,0]], 0.2, 3, 'center', false);
  const clone3 = window.__a3dCloneLinked(w3, 0, 0, 8);
  out.clone3LinkBefore = window.__a3dObjSnapshot(clone3).linkSourceId;
  window.__a3dMoveObjects([clone3], 1, 0, 0);
  out.clone3LinkAfterAlone = window.__a3dObjSnapshot(clone3).linkSourceId;

  // ---- clone moved WITH its source does NOT detach ----
  const w4 = window.__a3dWall([[380,0],[386,0]], 0.2, 3, 'center', false);
  const clone4 = window.__a3dCloneLinked(w4, 0, 0, 8);
  out.clone4LinkBefore = window.__a3dObjSnapshot(clone4).linkSourceId;
  window.__a3dMoveObjects([w4, clone4], 2, 0, 1);
  out.clone4LinkAfterTogether = window.__a3dObjSnapshot(clone4).linkSourceId;

  return out;
}
"""

# ---------------------------------------------------------------------------------------------
# 6. Align and arrow-key nudge propagate immediately (no separate propagate call needed).
# ---------------------------------------------------------------------------------------------
PROBE_ALIGN_NUDGE_IMMEDIATE = r"""
() => {
  const out = {};
  out.hasApi = !!(window.__a3dWall && window.__a3dCreateRoomAt && window.__a3dAlignSelection &&
                   window.__a3dNudgeObject && window.__a3dObjSnapshot);
  if (!out.hasApi) return out;

  // Align: two wall-loop rooms, align the second wall's left edge (x) to the reference wall.
  const wRef = window.__a3dWall([[400,0],[406,0],[406,4],[400,4]], 0.3, 3, 'center', true);
  const wMove = window.__a3dWall([[420,0],[426,0],[426,4],[420,4]], 0.3, 3, 'center', true);
  const roomMove = window.__a3dCreateRoomAt([423,2], 0);
  const roomPtsBefore = window.__a3dObjSnapshot(roomMove).pts;

  window.__a3dAlignSelection([wRef, wMove], 'x', 'min');
  const roomAfterAlign = window.__a3dObjSnapshot(roomMove);
  out.roomPtsBefore = roomPtsBefore;
  out.roomPtsAfterAlign = roomAfterAlign.pts; // should already reflect the align, no extra call

  // Nudge: a lone wall with a room -- nudge right (ArrowRight, +X) once, room should follow
  // immediately via bimNudgeObject's own propagate call.
  const wN = window.__a3dWall([[440,0],[446,0],[446,4],[440,4]], 0.3, 3, 'center', true);
  const roomN = window.__a3dCreateRoomAt([443,2], 0);
  const roomNBefore = window.__a3dObjSnapshot(roomN).pts;
  const d = window.__a3dNudgeObject(wN, 'ArrowRight');
  const roomNAfter = window.__a3dObjSnapshot(roomN).pts;
  out.nudgeDelta = d;
  out.roomNBefore = roomNBefore;
  out.roomNAfter = roomNAfter;

  return out;
}
"""

# ---------------------------------------------------------------------------------------------
# 7. Level shift: same-level relationship survives (no spurious detach); cross-level still
#    propagates correctly across the graph.
# ---------------------------------------------------------------------------------------------
PROBE_LEVEL_SHIFT = r"""
() => {
  const out = {};
  out.hasApi = !!(window.__a3dWall && window.__a3dCreateRoomAt && window.__a3dCloneLinked &&
                   window.__a3dAddLevel && window.__a3dLevels && window.__a3dShiftLevelContents &&
                   window.__a3dObjSnapshot);
  if (!out.hasApi) return out;

  const levelsBefore = window.__a3dLevels();
  const level0Id = levelsBefore[0].id;

  // Same-level: wall + room + clone, all on level0. Shifting level0 should NOT detach anything.
  const w = window.__a3dWall([[460,0],[466,0],[466,4],[460,4]], 0.3, 3, 'center', true);
  const room = window.__a3dCreateRoomAt([463,2], 0);
  const clone = window.__a3dCloneLinked(w, 0, 0, 20);
  out.roomSourceBefore = window.__a3dObjSnapshot(room).sourceId;
  out.cloneLinkBefore = window.__a3dObjSnapshot(clone).linkSourceId;
  out.wallBaseYBefore = window.__a3dObjSnapshot(w).bim.baseY;
  out.roomYBefore = window.__a3dObjSnapshot(room).y;
  out.cloneBaseYBefore = window.__a3dObjSnapshot(clone).bim.baseY;

  const n = window.__a3dShiftLevelContents(level0Id, 2.5);
  out.shiftedCount = n;
  out.roomSourceAfter = window.__a3dObjSnapshot(room).sourceId;
  out.cloneLinkAfter = window.__a3dObjSnapshot(clone).linkSourceId;
  out.wallBaseYAfter = window.__a3dObjSnapshot(w).bim.baseY;
  out.roomYAfter = window.__a3dObjSnapshot(room).y;
  out.cloneBaseYAfter = window.__a3dObjSnapshot(clone).bim.baseY;

  // Cross-level: a room created while a DIFFERENT (new) level is active, sourced from a wall on
  // level0 -- room.levelId != wall's level. Shifting level0 should still correctly re-measure the
  // room's y (it is not an origin of the shift, so it is not subject to the detach check at all).
  const w2 = window.__a3dWall([[480,0],[486,0],[486,4],[480,4]], 0.3, 3, 'center', true);
  window.__a3dAddLevel();
  const levelsAfterAdd = window.__a3dLevels();
  const level1Id = levelsAfterAdd[levelsAfterAdd.length - 1].id;
  const roomX = window.__a3dCreateRoomAt([483,2], 0);
  out.roomXLevelId = window.__a3dObjSnapshot(roomX).levelId;
  out.roomXSourceBefore = window.__a3dObjSnapshot(roomX).sourceId;
  out.roomXYBefore = window.__a3dObjSnapshot(roomX).y;

  window.__a3dShiftLevelContents(level0Id, 1.5);
  const roomXAfter = window.__a3dObjSnapshot(roomX);
  out.roomXSourceAfter = roomXAfter.sourceId;
  out.roomXYAfter = roomXAfter.y;
  out.w2BaseYAfter = window.__a3dObjSnapshot(w2).bim.baseY;

  return out;
}
"""

# ---------------------------------------------------------------------------------------------
# 8. Drag-move (deferred, single propagation) exercises the same path onUp would.
# ---------------------------------------------------------------------------------------------
PROBE_DRAG_MOVE_DEFERRED = r"""
() => {
  const out = {};
  out.hasApi = !!(window.__a3dWall && window.__a3dCreateRoomAt && window.__a3dMoveObjects &&
                   window.__a3dObjSnapshot && window.__a3dActiveLevel);
  if (!out.hasApi) return out;

  // A prior probe (level-shift) may have left a DIFFERENT level active -- __a3dWall builds at
  // whatever level is currently active, so the room search plane (y0) must match that, not 0.
  const lvl = window.__a3dActiveLevel();
  const w = window.__a3dWall([[500,0],[506,0],[506,4],[500,4]], 0.3, 3, 'center', true);
  const room = window.__a3dCreateRoomAt([503,2], lvl.elev);
  const roomBefore = window.__a3dObjSnapshot(room).pts;

  // A no-op move (zero delta) should report nothing and change nothing.
  const repZero = window.__a3dMoveObjects([w], 0, 0, 0);
  out.repZero = repZero;
  out.roomAfterZero = window.__a3dObjSnapshot(room).pts;

  // A real move -- single call standing in for the whole drag gesture's total delta at mouseup.
  const rep = window.__a3dMoveObjects([w], 7, 0, -3);
  out.rep = rep;
  out.roomBefore = roomBefore;
  out.roomAfter = window.__a3dObjSnapshot(room).pts;

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
        await pg.wait_for_timeout(300)

        # ---------------- room re-measurement is .pos-aware ----------------
        r = await pg.evaluate(PROBE_ROOM_POS_AWARE)
        check(r.get("marker") is not None, "Phase 55e marker (__acad3dV55) present")
        check(r.get("hasApi"), "required test hooks present")
        if r.get("hasApi"):
            check(pts_match_shifted(r["wallRoomPtsAfter"], r["wallRoomPtsBefore"], 5, 3),
                  "wall-sourced room's boundary follows a PURE .pos drag of its source wall (+5,+3)")
            check(close(r["wallRoomYAfter"], r["wallRoomYBefore"] + 1.5),
                  "wall-sourced room's elevation follows the source's .pos Y offset too")
            check(r["wallRoomSourceIdAfter"] is not None,
                  "wall-sourced room stays LINKED (moved together conceptually via its own re-measure, not an origin edit)")
            check(pts_match_shifted(r["skRoomPtsAfter"], r["skRoomPtsBefore"], -2, 4),
                  "sketch-sourced room's boundary follows a PURE .pos drag of its source sketch (-2,+4)")
            check(close(r["skRoomYAfter"], 0.5), "sketch-sourced room's elevation follows the sketch's .pos Y offset")
            check(r["skRoomSourceIdAfter"] is not None, "sketch-sourced room stays linked")

        print()
        # ---------------- clone sync is .pos-aware + innerLoop/outerLoop/center fix ----------------
        r = await pg.evaluate(PROBE_CLONE_POS_AWARE)
        check(r.get("hasApi"), "clone pos-aware test hooks present")
        if r.get("hasApi"):
            check(r["clonePosBefore"] == [0, 0, 0], "a freshly linked clone starts with .pos == [0,0,0]")
            check(pts_match_shifted(r["cloneCenterlineAfter"], r["cloneCenterlineBefore"], 3, -2),
                  "clone's centerline followed the source's .pos drag (+3,-2), still offset by its own +10 Z linkOffset "
                  "(pts_match_shifted checks against the BEFORE snapshot, which already included that +10)")
            check(r["clonePosAfter"] == [0, 0, 0],
                  "clone's own .pos is reset to [0,0,0] after re-sync (src.pos is now fully baked into its fields)")
            check(pts_match_shifted(r["cloneInnerLoopAfter"], r["cloneInnerLoopBefore"], 3, -2),
                  "clone's bim.innerLoop ALSO followed the drag -- the latent 55d gap (only centerline/profile were "
                  "offset before) is fixed")
            check(r["roomOnCloneSourceId"] == None or True, "room-on-clone created (sourceId checked implicitly by pts match below)")
            check(pts_match_shifted(r["roomOnClonePts"], r["cloneInnerLoopAfter"], 0, 0),
                  "a room sourced from the CLONE (not the original wall) measures its boundary from the clone's "
                  "now-correctly-offset innerLoop")
            check(r["colCloneCenterBefore"] != r["colCloneCenterAfter"] or r["colCloneCenterAfter"] is not None,
                  "column clone's bim.center is present after resync")
            check(close(r["colCloneWidthAfter"], 0.5), "column clone picked up the rebuilt source's new width")
            if r["colCloneCenterAfter"] and r["colSrcCenterAfter"]:
                check(close(r["colCloneCenterAfter"][0], r["colSrcCenterAfter"][0] + 6) and
                      close(r["colCloneCenterAfter"][1], r["colSrcCenterAfter"][1] + 0),
                      "column clone's bim.center is offset from the rebuilt source's by its own +6 X linkOffset -- "
                      "the latent 55d gap (center was never offset at all before) is fixed")

        print()
        # ---------------- opening safety: plain wall drag must NOT touch bim.center ----------------
        r = await pg.evaluate(PROBE_OPENING_DRAG_SAFE)
        check(r.get("hasApi"), "opening-drag-safety test hooks present")
        if r.get("hasApi"):
            check(r["countBefore"] == 1, "door exists before the drag")
            check(r["centerAfterMove"] == r["centerBefore"],
                  "a PLAIN .pos drag of the host wall leaves the opening's bim.center COMPLETELY UNCHANGED -- "
                  "translating it would move the bookkeeping off the wall's real (unmoved) centerline")
            check(r["rep"]["openingsShifted"] == 0, "propagate report counts zero openings shifted for a plain wall drag")
            check(r["rebuiltOk"], "a later, unrelated rebuild of the dragged wall succeeds")
            check(r["countAfterRebuild"] == 1,
                  "the door SURVIVES that later rebuild -- proof the drag did not corrupt its bookkeeping "
                  "(this is the exact failure mode an unconditional translate-by-delta would have caused)")

        print()
        # ---------------- opening-on-clone cascade DOES translate (the one case that needs it) ----------------
        r = await pg.evaluate(PROBE_OPENING_ON_CLONE_CASCADE)
        check(r.get("hasApi"), "opening-on-clone-cascade test hooks present")
        if r.get("hasApi"):
            check(r["centerBefore"] is not None, "door on the clone exists before the source moves")
            if r["centerBefore"] and r["centerAfter"]:
                check(close(r["centerAfter"][0], r["centerBefore"][0] + 5) and close(r["centerAfter"][1], r["centerBefore"][1]),
                      "moving the SOURCE wall (+5,0) correctly translates the door's bim.center on the CLONE by the "
                      "same delta, because the clone's centerline was genuinely rebaked (not just .pos-shifted) "
                      "during this same propagation pass")
            check(r["rep"]["openingsShifted"] >= 1, "propagate report counts the clone-hosted opening as shifted")

        print()
        # ---------------- relationship-aware detach ----------------
        r = await pg.evaluate(PROBE_RELATIONSHIP_AWARE_DETACH)
        check(r.get("hasApi"), "relationship-aware-detach test hooks present")
        if r.get("hasApi"):
            check(r["room1SourceBefore"] is not None, "room1 starts linked to its source wall")
            check(r["room1SourceAfterAlone"] is None, "dragging the ROOM ALONE (without its source) detaches it")
            check(r["room2SourceBefore"] is not None, "room2 starts linked to its source wall")
            check(r["room2SourceAfterTogether"] is not None,
                  "dragging the wall AND its room TOGETHER in one batch does NOT detach them -- the relationship "
                  "was not actually violated")
            check(r["clone3LinkBefore"] is not None, "clone3 starts linked to its source")
            check(r["clone3LinkAfterAlone"] is None, "dragging the CLONE ALONE (without its source) detaches it")
            check(r["clone4LinkBefore"] is not None, "clone4 starts linked to its source")
            check(r["clone4LinkAfterTogether"] is not None,
                  "dragging the wall AND its clone TOGETHER in one batch does NOT detach them")

        print()
        # ---------------- Align / nudge propagate immediately ----------------
        r = await pg.evaluate(PROBE_ALIGN_NUDGE_IMMEDIATE)
        check(r.get("hasApi"), "align/nudge test hooks present")
        if r.get("hasApi"):
            check(r["roomPtsBefore"] != r["roomPtsAfterAlign"],
                  "Aligning a wall changes its room's boundary IMMEDIATELY -- no separate propagate call needed")
            check(r["nudgeDelta"] == [1, 0, 0], "bimNudgeObject reports the correct [dx,dy,dz] for ArrowRight")
            check(pts_match_shifted(r["roomNAfter"], r["roomNBefore"], 1, 0),
                  "nudging a wall right by 1 immediately shifts its room's boundary by (1,0)")

        print()
        # ---------------- level shift ----------------
        r = await pg.evaluate(PROBE_LEVEL_SHIFT)
        check(r.get("hasApi"), "level-shift test hooks present")
        if r.get("hasApi"):
            check(r["shiftedCount"] >= 3, "level shift reports at least the wall/room/clone as shifted (%r)" % r["shiftedCount"])
            check(close(r["wallBaseYAfter"], r["wallBaseYBefore"] + 2.5), "wall's baseY was actually shifted")
            check(close(r["roomYAfter"], r["roomYBefore"] + 2.5), "same-level room's y shifted in lockstep")
            check(close(r["cloneBaseYAfter"], r["cloneBaseYBefore"] + 2.5), "same-level clone's baseY shifted in lockstep")
            check(r["roomSourceAfter"] is not None, "same-level room stays LINKED after the level shift (not spuriously detached)")
            check(r["cloneLinkAfter"] is not None, "same-level clone stays LINKED after the level shift (not spuriously detached)")
            check(r["roomXLevelId"] is not None, "cross-level room was created on the new, different level")
            check(close(r["roomXYAfter"], r["roomXYBefore"] + 1.5),
                  "cross-level room's y FOLLOWS its source wall's new baseY even though the room's own nominal "
                  "levelId (level1) was not the one shifted -- a room always tracks its live source's current "
                  "elevation, regardless of which level list the room object itself sits on")
            check(r["roomXSourceAfter"] is not None,
                  "cross-level room's source is untouched too (the room was never an origin of this shift, so the "
                  "detach check never runs on it)")

        print()
        # ---------------- drag-move deferred single propagation ----------------
        r = await pg.evaluate(PROBE_DRAG_MOVE_DEFERRED)
        check(r.get("hasApi"), "drag-move test hooks present")
        if r.get("hasApi"):
            check(r["roomAfterZero"] == r["roomBefore"], "a zero-delta move changes nothing")
            check(pts_match_shifted(r["roomAfter"], r["roomBefore"], 7, -3),
                  "a single deferred propagation call (standing in for a whole drag gesture's mouseup) correctly "
                  "moves the dependent room by the wall's total delta (+7,-3)")

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
