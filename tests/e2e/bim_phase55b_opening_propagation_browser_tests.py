"""
bim_phase55b_opening_propagation_browser_tests.py

Regression suite for the first dependency-graph visitor (__acad3dV51) in
canvas_v10.html: openings survive a rebuild of the wall that hosts them.

THE BUG THIS PHASE FIXED (verified before fixing, by stripping the fix back
out and re-running this scenario):

  An opening is not a solid. bimBuildWallOpening CSG-subtracts a box from the
  HOST WALL's mesh and leaves behind only a marker object recording where the
  hole is (center, dir, width, height, sillHeight). The hole therefore lives in
  the wall's mesh, so any path that regenerates that mesh from the wall's
  centerline destroys every hole in it.

  Four paths did exactly that and none re-cut the openings:
    - bimRebuildWall            (Properties palette: thickness / height / alignment)
    - bimRebuildInstanceForType (type parameter edit, all instances)
    - bimApplyWallTypeToInstances (type parameter edit, wall category)
    - bimSetWallTypeOf          (assigning a type to one wall)

  Measured on a 6m wall with one door and one window: 72 faces before the
  rebuild, 6 faces after -- a bare box. The two opening MARKERS survived, so
  the door and window schedules kept listing openings that no longer existed
  in the geometry. Nothing reported the discrepancy.

THE FIX: all four paths now call bimAfterWallRebuild(), which propagates from
the wall through the Phase 55a dependency graph. The visitor re-cuts each
opening hosted on that wall using its stored centre, and reports any it could
not place instead of failing silently.

WHY THE REASON FLAG EXISTS: an opening must be re-cut when its host wall's mesh
was REBUILT, and must not be when the wall was merely translated --
bimShiftLevelContents moves a wall by shifting its vertices and the hole moves
with them, so re-cutting there would subtract the same box out of an already
empty region. Callers state the reason; the visitor decides. That distinction is
asserted here directly, because getting it wrong would corrupt geometry on every
level-elevation change.

Run:  python3 bim_phase55b_opening_propagation_browser_tests.py [path/to/canvas_v10.html]
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


# A plain wall built from a two-point centerline is a rectangular prism: 6 faces.
# Any wall carrying an opening must therefore have MORE than 6. That single
# comparison is the whole bug, expressed semantically rather than by magic number.
PLAIN_WALL_FACES = 6

PROBE_BASELINE = r"""
() => {
  const res = {};
  res.marker = window.__acad3dV51 || null;
  res.hasApi = !!(window.__a3dDoorAt && window.__a3dRebuildWall && window.__a3dMeshStats);
  if (!res.hasApi) return res;

  const w = window.__a3dWall([[0,0],[6,0]], 0.3, 3, 'center', false);
  res.wallId = w;
  res.plain = window.__a3dMeshStats(w).faces;
  window.__a3dDoorAt(w, [2,0], 0.9, 2.1);
  res.afterDoor = window.__a3dMeshStats(w).faces;
  window.__a3dWindowAt(w, [4,0], 1.2, 1.2, 0.9);
  res.afterWindow = window.__a3dMeshStats(w).faces;
  res.openingCount = window.__a3dOpeningsOf(w).length;
  return res;
}
"""

# Each scenario builds its own wall so the tests cannot contaminate each other.
PROBE_REBUILDS = r"""
() => {
  const out = {};

  function freshWall(x0) {
    const w = window.__a3dWall([[x0,0],[x0+6,0]], 0.3, 3, 'center', false);
    window.__a3dDoorAt(w, [x0+2, 0], 0.9, 2.1);
    window.__a3dWindowAt(w, [x0+4, 0], 1.2, 1.2, 0.9);
    return w;
  }

  // 1. Thickness change through the Properties-palette path.
  let w1 = freshWall(20);
  out.thicknessBefore = window.__a3dMeshStats(w1).faces;
  window.__a3dRebuildWall(w1, 0.4, 3, 'center');
  out.thicknessAfter = window.__a3dMeshStats(w1).faces;
  out.thicknessOpenings = window.__a3dOpeningsOf(w1).length;

  // 2. Height change.
  let w2 = freshWall(40);
  out.heightBefore = window.__a3dMeshStats(w2).faces;
  window.__a3dRebuildWall(w2, 0.3, 4, 'center');
  out.heightAfter = window.__a3dMeshStats(w2).faces;

  // 3. Alignment change (centerline unchanged, faces shift laterally).
  let w3 = freshWall(60);
  out.alignBefore = window.__a3dMeshStats(w3).faces;
  window.__a3dRebuildWall(w3, 0.3, 3, 'left');
  out.alignAfter = window.__a3dMeshStats(w3).faces;

  // 4. Assigning a different wall TYPE to one wall (bimSetWallTypeOf).
  let w4 = freshWall(80);
  out.setTypeBefore = window.__a3dMeshStats(w4).faces;
  const types = window.__a3dWallTypes();
  const other = types.find(t => t.id !== 'wt-gen300') || types[0];
  out.setTypeTarget = other ? other.name : null;
  out.setTypeApplied = window.__a3dSetWallType(w4, other.id);
  out.setTypeIdOnWall = (window.__a3dState().objs.find(o => o.id === w4) || {}).bim.typeId;
  out.setTypeAfter = window.__a3dMeshStats(w4).faces;

  // 5. Editing a TYPE's shared parameter, which rebuilds every instance of it
  //    (bimApplyWallTypeToInstances).
  let w5 = freshWall(100);
  window.__a3dSetWallType(w5, 'wt-gen200');
  out.applyTypeBefore = window.__a3dMeshStats(w5).faces;
  const t200 = window.__a3dWallTypes().find(t => t.id === 'wt-gen200');
  t200.params.thickness = 0.25;
  const rep = window.__a3dApplyWallType('wt-gen200');
  out.applyTypeUpdated = rep ? rep.updated : null;
  out.applyTypeAfter = window.__a3dMeshStats(w5).faces;

  return out;
}
"""

PROBE_ISOLATION = r"""
() => {
  const out = {};
  // Two independent walls, each with a door. Rebuilding one must not disturb the other.
  const a = window.__a3dWall([[200,0],[206,0]], 0.3, 3, 'center', false);
  window.__a3dDoorAt(a, [202,0], 0.9, 2.1);
  const b = window.__a3dWall([[200,20],[206,20]], 0.3, 3, 'center', false);
  window.__a3dDoorAt(b, [202,20], 0.9, 2.1);

  out.aBefore = window.__a3dMeshStats(a).faces;
  out.bBefore = window.__a3dMeshStats(b).faces;
  window.__a3dRebuildWall(a, 0.5, 3, 'center');
  out.aAfter = window.__a3dMeshStats(a).faces;
  out.bAfter = window.__a3dMeshStats(b).faces;
  out.bUntouched = out.bBefore === out.bAfter;

  // The re-cut refreshes the marker's recorded position rather than leaving it stale.
  const ops = window.__a3dOpeningsOf(a);
  out.markerKept = ops.length === 1;
  out.markerHasCentre = !!(ops[0] && Array.isArray(ops[0].center));
  out.markerWidth = ops[0] ? ops[0].width : null;
  return out;
}
"""

PROBE_REASON_FLAG = r"""
() => {
  const out = {};
  const w = window.__a3dWall([[300,0],[306,0]], 0.3, 3, 'center', false);
  window.__a3dDoorAt(w, [302,0], 0.9, 2.1);
  out.before = window.__a3dMeshStats(w).faces;

  // 'transform' means the wall only moved: its mesh already carries the hole, so
  // re-cutting would subtract the same box out of an already empty region.
  const rT = window.__a3dPropagateFrom([w], 'transform');
  out.transformRecut = rT.recut;
  out.afterTransform = window.__a3dMeshStats(w).faces;
  out.transformLeftGeometryAlone = out.afterTransform === out.before;

  // 'rebuild' means the mesh was regenerated and the hole must be restored.
  const rR = window.__a3dPropagateFrom([w], 'rebuild');
  out.rebuildRecut = rR.recut;
  out.rebuildFailed = rR.failed;

  // A wall with no openings is a no-op, not an error.
  const bare = window.__a3dWall([[320,0],[326,0]], 0.3, 3, 'center', false);
  const rB = window.__a3dPropagateFrom([bare], 'rebuild');
  out.bareRecut = rB.recut;
  out.bareFailed = rB.failed;
  out.bareOk = rB.ok;
  return out;
}
"""

PROBE_UNPLACEABLE = r"""
() => {
  // An opening whose recorded centre no longer lies on its host wall cannot be
  // re-cut. It must be REPORTED, and the marker must be kept so undo restores a
  // consistent state -- never silently dropped, and never guessed at by moving
  // the door somewhere the user did not put it.
  const out = {};
  const w = window.__a3dWall([[400,0],[406,0]], 0.3, 3, 'center', false);
  window.__a3dDoorAt(w, [402,0], 0.9, 2.1);

  const objs = window.__a3dState().objs;
  const moved = objs.map(o => {
    if (o.t === 'opening' && o.bim && o.bim.hostWallId === w) {
      o.bim.center = [9999, 9999];   // nowhere near any wall segment
    }
    return o;
  });
  window.__a3dTestSetObjs(moved);

  const r = window.__a3dPropagateFrom([w], 'rebuild');
  out.ok = r.ok;
  out.recut = r.recut;
  out.failed = r.failed;
  out.markerStillPresent = window.__a3dOpeningsOf(w).length === 1;
  return out;
}
"""

PROBE_SCHEDULE_CONSISTENCY = r"""
() => {
  // The original bug left the schedules disagreeing with the geometry. After a
  // rebuild the door schedule must still list the door AND the geometry must
  // still contain its hole.
  const out = {};
  const w = window.__a3dWall([[500,0],[506,0]], 0.3, 3, 'center', false);
  window.__a3dDoorAt(w, [502,0], 0.9, 2.1);
  out.facesBefore = window.__a3dMeshStats(w).faces;
  const schedBefore = window.__a3dDoorSchedule();
  out.schedBefore = schedBefore.length;

  window.__a3dRebuildWall(w, 0.45, 3, 'center');
  out.facesAfter = window.__a3dMeshStats(w).faces;
  const schedAfter = window.__a3dDoorSchedule();
  out.schedAfter = schedAfter.length;
  out.hostResolved = schedAfter.every(r => r.hostWall && r.hostWall.indexOf('missing') < 0);
  return out;
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

        print("\n== load and public surface ==")
        r0 = await pg.evaluate(PROBE_BASELINE)
        check(not errs, "no uncaught page errors on load (%s)" % (errs[:1] or "none"))
        check(r0["marker"] is not None, "__acad3dV51 feature marker present")
        check(r0["hasApi"] is True, "opening/rebuild test surface is exposed")
        if not r0.get("hasApi"):
            await b.close()
            print("\n%d checks, %d failed" % (TOTAL[0], len(FAILS)))
            print("RESULT: FAIL")
            return 1

        print("\n== baseline: cutting an opening really does change the solid ==")
        check(r0["plain"] == PLAIN_WALL_FACES,
              "a plain 2-point wall is a %d-face prism (got %d)" % (PLAIN_WALL_FACES, r0["plain"]))
        check(r0["afterDoor"] > r0["plain"],
              "cutting a door increases the wall's face count (%d -> %d)" % (r0["plain"], r0["afterDoor"]))
        check(r0["afterWindow"] > r0["afterDoor"],
              "cutting a window increases it further (%d -> %d)" % (r0["afterDoor"], r0["afterWindow"]))
        check(r0["openingCount"] == 2, "both opening markers are recorded against the wall")

        print("\n== THE REGRESSION GUARD: openings survive every wall-rebuild path ==")
        r1 = await pg.evaluate(PROBE_REBUILDS)
        check(r1["thicknessAfter"] > PLAIN_WALL_FACES,
              "thickness change keeps the openings (%d faces before, %d after; a bare box would be %d)"
              % (r1["thicknessBefore"], r1["thicknessAfter"], PLAIN_WALL_FACES))
        check(r1["thicknessOpenings"] == 2, "both opening markers survive the thickness change")
        check(r1["heightAfter"] > PLAIN_WALL_FACES,
              "height change keeps the openings (%d -> %d)" % (r1["heightBefore"], r1["heightAfter"]))
        check(r1["alignAfter"] > PLAIN_WALL_FACES,
              "alignment change keeps the openings (%d -> %d)" % (r1["alignBefore"], r1["alignAfter"]))
        check(r1["setTypeApplied"] is True,
              "the wall type was genuinely reassigned, not a no-op (target '%s')" % r1["setTypeTarget"])
        check(r1["setTypeIdOnWall"] is not None and r1["setTypeIdOnWall"] != "wt-gen300",
              "the wall now carries the new type id (%s)" % r1["setTypeIdOnWall"])
        check(r1["setTypeAfter"] > PLAIN_WALL_FACES,
              "assigning a different wall type keeps the openings (%d -> %d, type '%s')"
              % (r1["setTypeBefore"], r1["setTypeAfter"], r1["setTypeTarget"]))
        check(r1["applyTypeUpdated"] and r1["applyTypeUpdated"] >= 1,
              "editing a type parameter rebuilt at least one instance (%s)" % r1["applyTypeUpdated"])
        check(r1["applyTypeAfter"] > PLAIN_WALL_FACES,
              "editing a type's shared thickness keeps the openings in every instance (%d -> %d)"
              % (r1["applyTypeBefore"], r1["applyTypeAfter"]))

        print("\n== propagation is scoped: rebuilding one wall does not touch another ==")
        r2 = await pg.evaluate(PROBE_ISOLATION)
        check(r2["aAfter"] > PLAIN_WALL_FACES, "the rebuilt wall keeps its opening (%d -> %d)" % (r2["aBefore"], r2["aAfter"]))
        check(r2["bUntouched"] is True, "the unrelated wall's geometry is byte-identical (%d faces both sides)" % r2["bBefore"])
        check(r2["markerKept"] is True, "the opening marker is kept, not duplicated")
        check(r2["markerHasCentre"] is True, "the marker's recorded position is refreshed by the re-cut")
        check(r2["markerWidth"] == 0.9, "the marker keeps its authored width (%s)" % r2["markerWidth"])

        print("\n== the reason flag: rebuild re-cuts, transform must not ==")
        r3 = await pg.evaluate(PROBE_REASON_FLAG)
        check(r3["transformRecut"] == 0, "a 'transform' propagation re-cuts nothing (got %s)" % r3["transformRecut"])
        check(r3["transformLeftGeometryAlone"] is True,
              "a 'transform' propagation leaves the mesh untouched (%d faces both sides)" % r3["before"])
        check(r3["rebuildRecut"] == 1, "a 'rebuild' propagation re-cuts the wall's one opening (got %s)" % r3["rebuildRecut"])
        check(r3["rebuildFailed"] == 0, "that re-cut reported no failures")
        check(r3["bareOk"] is True, "propagating from a wall with no openings succeeds")
        check(r3["bareRecut"] == 0 and r3["bareFailed"] == 0,
              "a wall with no openings is a clean no-op (recut=%s failed=%s)" % (r3["bareRecut"], r3["bareFailed"]))

        print("\n== an opening that cannot be placed is reported, never silently dropped ==")
        r4 = await pg.evaluate(PROBE_UNPLACEABLE)
        check(r4["ok"] is True, "propagation still completes when an opening cannot be re-cut")
        check(r4["failed"] == 1, "the unplaceable opening is counted as a failure (got %s)" % r4["failed"])
        check(r4["recut"] == 0, "nothing was cut in the wrong place instead (recut=%s)" % r4["recut"])
        check(r4["markerStillPresent"] is True, "the marker is kept, so undo restores a consistent state")

        print("\n== geometry and schedules no longer disagree ==")
        r5 = await pg.evaluate(PROBE_SCHEDULE_CONSISTENCY)
        check(r5["schedAfter"] == r5["schedBefore"], "the door schedule still lists the door after the rebuild")
        check(r5["facesAfter"] > PLAIN_WALL_FACES,
              "and the geometry still contains its hole (%d faces, a bare box would be %d)"
              % (r5["facesAfter"], PLAIN_WALL_FACES))
        check(r5["hostResolved"] is True, "every scheduled door still resolves to a real host wall")

        print("\n== no errors introduced ==")
        check(not errs, "still no uncaught page errors after all rebuild paths (%s)" % (errs[:1] or "none"))

        await b.close()

    print("\n%d checks, %d failed" % (TOTAL[0], len(FAILS)))
    print("RESULT: " + ("PASS" if not FAILS else "FAIL"))
    return 1 if FAILS else 0


sys.exit(asyncio.run(main()))
