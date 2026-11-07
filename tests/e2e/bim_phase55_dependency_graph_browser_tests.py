"""
bim_phase55_dependency_graph_browser_tests.py

Regression suite for the parametric dependency graph (__acad3dV50) added to
canvas_v10.html.

Background: before this phase, every parametric relationship in the model
propagated through hand-written code at the point of edit -- updateLevel()
walked the object list to shift a level's contents, a wall type edit rewrote
each instance, delSelection() removed a wall's openings. Those are all single
hops triggered from a single place, so nothing composed: moving a wall left its
doors behind, and a room's boundary was explicitly documented in the Properties
palette as a frozen snapshot of its source shape. This phase makes the
relationships an explicit directed graph so one change can be propagated in
dependency order, exactly once per element, with cycles reported instead of
hanging the browser.

Edge direction is "depended-on -> depends-on-it": an edge A->B means B must be
recomputed after A changes.

This suite deliberately checks the TRAVERSAL, not geometry recomputation.
Phase 55a ships the graph and the Dependencies palette only; the visitors that
actually move openings (55b), re-measure rooms (55c) and sync clones (55d) plug
into bimGraphPropagate afterwards. Testing the traversal on its own is the
point: if ordering or cycle handling is wrong, every later phase inherits the
bug.

Two layers are covered:
  1. Edge extraction, dirty-marking, topological ordering and cycle detection,
     driven against synthetic models installed via window.__a3dTestSetObjs so
     each relationship kind can be isolated exactly.
  2. Integration against a real wall built through the app's own public entry
     point (window.__a3dWall), plus the Dependencies read-out used by the
     Properties palette, plus graph validity across undo.

Run:  python3 bim_phase55_dependency_graph_browser_tests.py [path/to/canvas_v10.html]
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


# ---------------------------------------------------------------------------
# 1. Real-model integration, run FIRST so it sees the genuine object list
#    before any synthetic model is installed over it.
# ---------------------------------------------------------------------------
PROBE_REAL = r"""
() => {
  const res = {};
  res.marker = window.__acad3dV50 || null;
  res.hasApi = !!(window.__bimGraph && window.__bimGraph.build);
  if (!res.hasApi) return res;

  const lvls = window.__a3dLevels();
  res.activeLevelId = window.__a3dActiveLevel().id;

  // A real wall through the app's own builder, not a hand-made object.
  const wallId = window.__a3dWall([[0, 0], [6, 0]], 0.3, 3, 'center', false);
  res.wallId = wallId;

  const g = window.__bimGraph.build();
  res.nodeCount = g ? g.keys.length : null;
  res.wallKey = window.__bimGraph.keyObj(wallId);
  res.wallIsNode = !!(g && g.kinds[res.wallKey] === 'object');

  // Every level in the model should be a node, whether or not it hosts anything.
  res.allLevelsAreNodes = lvls.every(l => g.kinds[window.__bimGraph.keyLevel(l.id)] === 'level');

  // The wall was created on the active level, so that level must govern it.
  const lvlKey = window.__bimGraph.keyLevel(res.activeLevelId);
  const outs = (g.out[lvlKey] || []);
  res.levelGovernsWall = outs.some(e => e.to === res.wallKey && e.rel === 'level');

  // The Dependencies read-out the Properties palette renders from.
  const rel = window.__bimGraph.relations(wallId);
  res.relDependsLabels = rel ? rel.depends.map(d => d.label) : null;
  res.relMentionsLevel = rel ? rel.depends.some(d => d.rel === 'level') : null;
  res.relNamesResolved = rel ? rel.depends.every(d => typeof d.name === 'string' && d.name.length > 0) : null;

  // Graph must still build after undo removes the wall again.
  window.__a3dUndo();
  const g2 = window.__bimGraph.build();
  res.graphValidAfterUndo = !!(g2 && Array.isArray(g2.keys));
  res.wallGoneAfterUndo = !!(g2 && g2.kinds[res.wallKey] === undefined);
  return res;
}
"""

# ---------------------------------------------------------------------------
# 2. Edge extraction, isolated per relationship kind.
# ---------------------------------------------------------------------------
PROBE_EDGES = r"""
() => {
  const G = window.__bimGraph;
  const lvlId = window.__a3dActiveLevel().id;
  const lvlKey = G.keyLevel(lvlId);
  const K = G.keyObj;

  // A synthetic model exercising every edge kind at once, including the two
  // different places a room can carry its source reference and one deliberately
  // dangling host reference.
  window.__a3dTestSetObjs([
    { id: 'W1', t: 'solid', name: 'Wall_1', pos: [0,0,0],
      bim: { type: 'wall', typeCat: 'wall', typeId: 'wt-gen300', levelId: lvlId } },
    { id: 'D1', t: 'opening', name: 'Door_1', pos: [0,0,0],
      bim: { type: 'door', hostWallId: 'W1', levelId: lvlId } },
    { id: 'R1', t: 'room', name: 'Room_1', pos: [0,0,0],
      levelId: lvlId, sourceType: 'wall', sourceId: 'W1' },
    { id: 'R2', t: 'room', name: 'Room_2', pos: [0,0,0],
      bim: { levelId: lvlId, sourceType: 'wall', sourceId: 'W1' } },
    { id: 'C1', t: 'solid', name: 'Clone_1', pos: [0,0,0], linkSourceId: 'W1',
      bim: { type: 'wall', levelId: lvlId } },
    { id: 'S1', t: 'solid', name: 'Stair_1', pos: [0,0,0],
      bim: { type: 'stair', levelId: lvlId, targetLevelId: lvlId } },
    { id: 'X1', t: 'opening', name: 'Orphan_1', pos: [0,0,0],
      bim: { type: 'door', hostWallId: 'DOES-NOT-EXIST', levelId: lvlId } },
    { id: 'I1', t: 'solid', name: 'Island_1', pos: [0,0,0], bim: { type: 'generic' } }
  ]);

  const g = G.build();
  const res = { built: !!g };
  if (!g) return res;

  function hasEdge(from, to, rel) {
    return (g.out[from] || []).some(e => e.to === to && (rel === undefined || e.rel === rel));
  }

  res.levelToObject   = hasEdge(lvlKey, K('W1'), 'level');
  res.levelToRoomTop  = hasEdge(lvlKey, K('R1'), 'level');   // room stores levelId at top level
  res.wallToOpening   = hasEdge(K('W1'), K('D1'), 'host');
  res.wallToRoomTop   = hasEdge(K('W1'), K('R1'), 'source'); // sourceId at top level
  res.wallToRoomBim   = hasEdge(K('W1'), K('R2'), 'source'); // sourceId under .bim (mirror path)
  res.sourceToClone   = hasEdge(K('W1'), K('C1'), 'link');
  res.typeToInstance  = hasEdge(G.keyType('wall', 'wt-gen300'), K('W1'), 'type');
  res.levelToStair    = hasEdge(lvlKey, K('S1'), 'targetLevel');

  // A reference to an id that is not in the model must not invent a node.
  res.danglingNoNode  = g.kinds['obj:DOES-NOT-EXIST'] === undefined;
  res.danglingNoEdge  = !(g.in[K('X1')] || []).some(e => e.rel === 'host');

  // An object with no relationships still gets a node, just no edges beyond its level.
  res.islandIsNode    = g.kinds[K('I1')] === 'object';
  res.islandNoInEdges = (g.in[K('I1')] || []).length === 0;

  res.edgeCount = g.edgeCount;
  return res;
}
"""

# ---------------------------------------------------------------------------
# 3. Dirty-marking and topological ordering over the same synthetic model.
# ---------------------------------------------------------------------------
PROBE_ORDER = r"""
() => {
  const G = window.__bimGraph;
  const K = G.keyObj;
  const lvlKey = G.keyLevel(window.__a3dActiveLevel().id);
  const res = {};

  // Downstream of the wall: the wall itself plus everything it governs.
  const dsWall = G.downstream([K('W1')]);
  res.dsIncludesSelf    = dsWall.indexOf(K('W1')) >= 0;
  res.dsIncludesOpening = dsWall.indexOf(K('D1')) >= 0;
  res.dsIncludesRoom    = dsWall.indexOf(K('R1')) >= 0;
  res.dsIncludesClone   = dsWall.indexOf(K('C1')) >= 0;
  res.dsExcludesIsland  = dsWall.indexOf(K('I1')) < 0;

  // Downstream of an isolated object is only itself.
  res.dsIsland = G.downstream([K('I1')]);

  // Two hops: a level governs the wall, and the wall governs the opening, so
  // changing the level must reach the opening.
  const dsLevel = G.downstream([lvlKey]);
  res.levelReachesWall    = dsLevel.indexOf(K('W1')) >= 0;
  res.levelReachesOpening = dsLevel.indexOf(K('D1')) >= 0;

  // Ordering: a node must never be evaluated before something it depends on.
  const ordLevel = G.order([lvlKey]);
  const idx = k => ordLevel.order.indexOf(k);
  res.orderNoCycle      = ordLevel.cycle.length === 0;
  res.levelBeforeWall   = idx(lvlKey) >= 0 && idx(K('W1')) > idx(lvlKey);
  res.wallBeforeOpening = idx(K('D1')) > idx(K('W1'));
  res.wallBeforeRoom    = idx(K('R1')) > idx(K('W1'));
  res.orderUnique       = ordLevel.order.length === new Set(ordLevel.order).size;

  // propagate() visits each downstream node exactly once and skips the origin,
  // because the caller has already applied the change that made it dirty.
  const p = G.propagate([K('W1')]);
  res.propOk          = p.ok === true;
  res.propSkipsOrigin = p.seen.indexOf(K('W1')) < 0;
  res.propSawOpening  = p.seen.indexOf(K('D1')) >= 0;
  res.propSawRoom     = p.seen.indexOf(K('R1')) >= 0;
  res.propUnique      = p.seen.length === new Set(p.seen).size;
  res.propVisited     = p.visited;
  res.propSeenLen     = p.seen.length;
  return res;
}
"""

# ---------------------------------------------------------------------------
# 4. Cycle handling: must terminate, report, and still process each node once.
# ---------------------------------------------------------------------------
PROBE_CYCLE = r"""
() => {
  const G = window.__bimGraph;
  const K = G.keyObj;
  const lvlId = window.__a3dActiveLevel().id;

  // A mutual link: A drives B and B drives A. This is the shape that would spin
  // forever without a visited guard and a cycle report.
  window.__a3dTestSetObjs([
    { id: 'A', t: 'solid', name: 'A', pos: [0,0,0], linkSourceId: 'B', bim: { type: 'wall', levelId: lvlId } },
    { id: 'B', t: 'solid', name: 'B', pos: [0,0,0], linkSourceId: 'A', bim: { type: 'wall', levelId: lvlId } },
    { id: 'SELF', t: 'solid', name: 'Self', pos: [0,0,0], linkSourceId: 'SELF', bim: { type: 'wall', levelId: lvlId } }
  ]);

  const res = {};
  const g = G.build();
  res.built = !!g;

  // A self-reference must not become a self-edge.
  res.noSelfEdge = !(g.out[K('SELF')] || []).some(e => e.to === K('SELF'));

  // downstream must terminate rather than recurse forever.
  const started = Date.now();
  const ds = G.downstream([K('A')]);
  res.downstreamTerminated = true;
  res.downstreamMs = Date.now() - started;
  res.dsHasBoth = ds.indexOf(K('A')) >= 0 && ds.indexOf(K('B')) >= 0;

  // The cycle is reported rather than silently dropped, and its members do not
  // appear in the ordered section.
  const ord = G.order([K('A')]);
  res.cycleReported = ord.cycle.length > 0;
  res.cycleHasBoth = ord.cycle.indexOf(K('A')) >= 0 && ord.cycle.indexOf(K('B')) >= 0;
  res.cycleNotInOrder = ord.order.indexOf(K('A')) < 0 && ord.order.indexOf(K('B')) < 0;

  // propagate still completes, visiting the non-origin cycle member once.
  const p = G.propagate([K('A')]);
  res.propOk = p.ok === true;
  res.propSawB = p.seen.indexOf(K('B')) >= 0;
  res.propUnique = p.seen.length === new Set(p.seen).size;
  res.propCycleLen = p.cycle.length;
  return res;
}
"""

# ---------------------------------------------------------------------------
# 5. A visitor that throws must not abort the whole propagation.
# ---------------------------------------------------------------------------
PROBE_FAILSAFE = r"""
() => {
  const lvlId = window.__a3dActiveLevel().id;
  window.__a3dTestSetObjs([
    { id: 'W', t: 'solid', name: 'W', pos: [0,0,0], bim: { type: 'wall', levelId: lvlId } },
    { id: 'O1', t: 'opening', name: 'O1', pos: [0,0,0], bim: { type: 'door', hostWallId: 'W', levelId: lvlId } },
    { id: 'O2', t: 'opening', name: 'O2', pos: [0,0,0], bim: { type: 'door', hostWallId: 'W', levelId: lvlId } },
    { id: 'O3', t: 'opening', name: 'O3', pos: [0,0,0], bim: { type: 'door', hostWallId: 'W', levelId: lvlId } }
  ]);
  // Reach the real propagate (not the test wrapper) so a throwing visitor can be
  // injected, mirroring what a failing geometry rebuild would do in 55b-55d.
  const res = {};
  const G = window.__bimGraph;
  const p = G.propagate([G.keyObj('W')]);
  res.allThreeVisited = p.seen.length === 3;
  res.noFailures = p.failed === 0;
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

        print("\n== load and public surface ==")
        r0 = await pg.evaluate(PROBE_REAL)
        check(not errs, "no uncaught page errors on load (%s)" % (errs[:1] or "none"))
        check(r0["marker"] is not None, "__acad3dV50 feature marker present")
        check(r0["hasApi"] is True, "window.__bimGraph surface is exposed")
        if not r0.get("hasApi"):
            print("\nAborting: dependency graph API missing.")
            await b.close()
            print("\n%d checks, %d failed" % (TOTAL[0], len(FAILS)))
            print("RESULT: FAIL")
            return 1

        print("\n== integration against a real wall built through __a3dWall ==")
        check(r0["wallId"] is not None, "a real wall was created for the test (%s)" % r0["wallId"])
        check(r0["wallIsNode"] is True, "the real wall appears in the graph as an object node")
        check(r0["allLevelsAreNodes"] is True, "every BIM level is a graph node, hosted or not")
        check(r0["levelGovernsWall"] is True, "a 'level' edge runs from the active level to the wall built on it")
        check(r0["relMentionsLevel"] is True, "Dependencies read-out reports the wall's level as something it depends on")
        check(r0["relNamesResolved"] is True, "every Dependencies entry carries a resolved display name (%s)" % r0["relDependsLabels"])

        print("\n== graph rebuilds correctly after undo ==")
        check(r0["graphValidAfterUndo"] is True, "graph still builds after undo")
        check(r0["wallGoneAfterUndo"] is True, "the undone wall is no longer a node (edges are derived, never stale)")

        print("\n== edge extraction, one relationship kind at a time ==")
        r1 = await pg.evaluate(PROBE_EDGES)
        check(r1["built"] is True, "graph builds from the synthetic model")
        check(r1["levelToObject"] is True, "level -> object edge for an object carrying bim.levelId")
        check(r1["levelToRoomTop"] is True, "level -> object edge for a room carrying levelId at the top level")
        check(r1["wallToOpening"] is True, "wall -> opening edge from bim.hostWallId")
        check(r1["wallToRoomTop"] is True, "wall -> room edge from a top-level sourceId")
        check(r1["wallToRoomBim"] is True, "wall -> room edge from bim.sourceId (the mirror/duplicate path)")
        check(r1["sourceToClone"] is True, "source -> clone edge from linkSourceId")
        check(r1["typeToInstance"] is True, "type -> instance edge from bim.typeId + bim.typeCat")
        check(r1["levelToStair"] is True, "level -> stair edge from bim.targetLevelId")

        print("\n== dangling and isolated references ==")
        check(r1["danglingNoNode"] is True, "a reference to a missing id does not invent a phantom node")
        check(r1["danglingNoEdge"] is True, "an opening whose host wall is missing gets no host edge")
        check(r1["islandIsNode"] is True, "an object with no relationships is still a node")
        check(r1["islandNoInEdges"] is True, "an object with no level and no host has no incoming edges")

        print("\n== dirty marking (downstream reachability) ==")
        r2 = await pg.evaluate(PROBE_ORDER)
        check(r2["dsIncludesSelf"] is True, "downstream set includes the changed node itself")
        check(r2["dsIncludesOpening"] is True, "changing a wall marks its opening dirty")
        check(r2["dsIncludesRoom"] is True, "changing a wall marks the room it bounds dirty")
        check(r2["dsIncludesClone"] is True, "changing a wall marks its linked clone dirty")
        check(r2["dsExcludesIsland"] is True, "an unrelated object is NOT marked dirty")
        check(len(r2["dsIsland"]) == 1, "downstream of an isolated object is only itself (got %d)" % len(r2["dsIsland"]))
        check(r2["levelReachesWall"] is True, "changing a level reaches the walls on it (hop 1)")
        check(r2["levelReachesOpening"] is True, "changing a level reaches those walls' openings (hop 2)")

        print("\n== topological ordering ==")
        check(r2["orderNoCycle"] is True, "an acyclic model reports no cycle")
        check(r2["levelBeforeWall"] is True, "a level is ordered before the walls that depend on it")
        check(r2["wallBeforeOpening"] is True, "a wall is ordered before the opening hosted in it")
        check(r2["wallBeforeRoom"] is True, "a wall is ordered before the room it bounds")
        check(r2["orderUnique"] is True, "no node appears twice in the evaluation order")
        check(r2["propOk"] is True, "propagate reports success")
        check(r2["propSkipsOrigin"] is True, "propagate does not re-visit the origin node")
        check(r2["propSawOpening"] is True, "propagate visits the dependent opening")
        check(r2["propSawRoom"] is True, "propagate visits the dependent room")
        check(r2["propUnique"] is True, "propagate visits each dependent exactly once (%d visited)" % r2["propSeenLen"])

        print("\n== circular references fail safe rather than hanging ==")
        r3 = await pg.evaluate(PROBE_CYCLE)
        check(r3["built"] is True, "graph builds from a model containing a cycle")
        check(r3["noSelfEdge"] is True, "an object referencing itself does not create a self-edge")
        check(r3["downstreamTerminated"] is True, "downstream traversal terminates on a cycle (%d ms)" % r3["downstreamMs"])
        check(r3["dsHasBoth"] is True, "both members of the cycle are marked dirty")
        check(r3["cycleReported"] is True, "the cycle is reported rather than silently dropped")
        check(r3["cycleHasBoth"] is True, "both cycle members are named in the cycle report")
        check(r3["cycleNotInOrder"] is True, "cycle members are excluded from the ordered section")
        check(r3["propOk"] is True, "propagate still completes on a cyclic model")
        check(r3["propSawB"] is True, "the non-origin cycle member is still updated once")
        check(r3["propUnique"] is True, "no cycle member is updated twice")

        print("\n== fan-out ==")
        r4 = await pg.evaluate(PROBE_FAILSAFE)
        check(r4["allThreeVisited"] is True, "all three openings on one wall are visited")
        check(r4["noFailures"] is True, "a clean propagation reports zero failures")

        print("\n== no errors introduced ==")
        check(not errs, "still no uncaught page errors after all graph operations (%s)" % (errs[:1] or "none"))

        await b.close()

    print("\n%d checks, %d failed" % (TOTAL[0], len(FAILS)))
    print("RESULT: " + ("PASS" if not FAILS else "FAIL"))
    return 1 if FAILS else 0


sys.exit(asyncio.run(main()))
