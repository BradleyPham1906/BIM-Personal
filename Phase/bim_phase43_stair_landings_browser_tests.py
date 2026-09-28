"""
bim_phase43_stair_landings_browser_tests.py

Regression suite for multi-flight stairs with landings/turns + stepped guard
railings (__acad3dV43) added to canvas_v10.html. Runs the real file in
Chromium and drives the app's own build path via window.__a3dBuildStairPathGeometry
/ window.__a3dStairLayout / window.__a3dBuildStair, so it exercises the shipped
code, not a prototype copy. Railings are merged into the stair solid by
concatenating and re-welding already-valid raw faces (not a CSG boolean --
see the comment on bimBuildStairPathGeometry for why), verified sane via
bimMeshSanityCheck before being accepted.

Run:  python3 bim_phase43_stair_landings_browser_tests.py [path/to/canvas_v10.html]
"""
import asyncio, pathlib, sys
from playwright.async_api import async_playwright

TARGET = sys.argv[1] if len(sys.argv) > 1 else "canvas_v10.html"

PROBE = r"""
() => {
  const res = {};
  const mkTopology = (m) => {
    const und = {}, dir = {};
    let dupDir = 0, bad = 0, vol = 0;
    m.f.forEach(f => {
      for (let i = 0; i < f.length; i++) {
        const a = f[i], b = f[(i + 1) % f.length];
        if (a === b) bad++;
        const uk = Math.min(a, b) + '-' + Math.max(a, b);
        und[uk] = (und[uk] || 0) + 1;
        const dk = a + '>' + b;
        dir[dk] = (dir[dk] || 0) + 1;
      }
      for (let i = 1; i + 1 < f.length; i++) {
        const a = m.v[f[0]], b = m.v[f[i]], c = m.v[f[i + 1]];
        vol += (a[0]*(b[1]*c[2]-b[2]*c[1]) - a[1]*(b[0]*c[2]-b[2]*c[0]) + a[2]*(b[0]*c[1]-b[1]*c[0])) / 6;
      }
    });
    Object.keys(dir).forEach(k => { if (dir[k] > 1) dupDir++; });
    Object.keys(und).forEach(k => { if (und[k] !== 2) bad++; });
    return { dupDir, bad, vol, verts: m.v.length, faces: m.f.length };
  };

  // 1) Straight 2-point stair: no landings, single flight -- legacy-equivalent shape.
  let r = window.__a3dBuildStairPathGeometry([[0,0],[0,6]], 1.2, 0, 3, 3/17, 6/17, 1.0, false, 0);
  res.straight = r.error ? { error: r.error } : {
    numSteps: r.bim.numSteps, path: r.bim.path, topo: mkTopology(r.mesh)
  };

  // 2) L-turn: one 90-degree turn, one landing, two flights.
  r = window.__a3dBuildStairPathGeometry([[0,0],[0,4],[3,4]], 1.0, 0, 3, 3/16, 0.28, 1.0, false, 0);
  res.lturn = r.error ? { error: r.error } : {
    numSteps: r.bim.numSteps, totalRun: r.bim.totalRun, topo: mkTopology(r.mesh)
  };
  let lay = window.__a3dStairLayout([[0,0],[0,4],[3,4]], 1.0, 0, 16, 3/16, 0.28, 1.0);
  res.lturnLayout = lay.error ? { error: lay.error } : {
    flights: lay.flights.length, zones: lay.zones.length,
    landingEntries: lay.prof.filter(e => e.t === 'landing').length
  };

  // 3) U-shape: two turns, three flights.
  r = window.__a3dBuildStairPathGeometry([[0,0],[0,5],[2.4,5],[2.4,0]], 1.2, 0, 3.2, 3.2/24, 0.28, 1.2, false, 0);
  res.ushape = r.error ? { error: r.error } : { topo: mkTopology(r.mesh) };
  lay = window.__a3dStairLayout([[0,0],[0,5],[2.4,5],[2.4,0]], 1.2, 0, 24, 3.2/24, 0.28, 1.2);
  res.ushapeLayout = lay.error ? { error: lay.error } : { flights: lay.flights.length, zones: lay.zones.length };

  // 4) Railings requested: solid should be watertight and taller than the plain stair via CSG union.
  r = window.__a3dBuildStairPathGeometry([[0,0],[0,4],[3,4]], 1.0, 0, 3, 3/16, 0.28, 1.0, true, 0.9);
  res.railed = r.error ? { error: r.error } : {
    railings: r.bim.railings, railHeight: r.bim.railHeight, topo: mkTopology(r.mesh)
  };

  // 5) Fail-safe rejections (should return {error:...}, never throw or emit a corrupt mesh).
  res.badLanding = window.__a3dStairLayout([[0,0],[0,0.3],[3,0.3]], 1.0, 0, 16, 0.18, 0.28, 1.0);
  res.badShort = window.__a3dStairLayout([[0,0],[0,1]], 1.0, 0, 16, 0.18, 0.28, 1.0);
  res.badTooFewSteps = window.__a3dStairLayout([[0,0],[0,2],[1,2],[1,4],[2,4]], 1.0, 0, 3, 1, 1, 1.0);
  res.badDegenerate = window.__a3dStairLayout([[0,0],[0,0]], 1.0, 0, 16, 0.18, 0.28, 1.0);

  // 6) Full tool path via the real UI plumbing: draw a path with the sketch tool (accumulate via
  // __a3dSkPush, mirroring what skClick does per click), finish with Enter (__a3dFinishStair),
  // fill the dialog fields and click OK -- exercises skClick's accumulate-only stair branch,
  // finishStair, openStairDlg and buildStairSolid end to end against the shipped code, not a
  // hook shortcut. Then duplicate the result to exercise the path-aware duplicate branch.
  let levels = window.__a3dLevels();
  if (!levels.some(l => l.elev > 0)) { window.__a3dAddLevel(); levels = window.__a3dLevels(); }
  window.__a3dSetLevel(levels[0].id);
  window.__a3dStairToolStart();
  window.__a3dSkPush([0,0]);
  window.__a3dSkPush([0,4]);
  window.__a3dSkPush([3,4]);
  window.__a3dFinishStair();
  const dlg = document.querySelector('.a3d-dlg');
  const uiFlow = { dlgOpened: !!dlg };
  if (dlg) {
    dlg.querySelector('[data-a3dp="w"]').value = '1.0';
    const lvlSel = dlg.querySelector('[data-a3dp="lvl"]');
    for (let i=0;i<lvlSel.options.length;i++){
      const idx = parseInt(lvlSel.options[i].value,10);
      if (levels[idx] && levels[idx].elev > 0) { lvlSel.value = String(idx); break; }
    }
    const railChk = dlg.querySelector('[data-a3dp="rail"]');
    railChk.checked = true;
    railChk.dispatchEvent(new Event('change'));
    dlg.querySelector('[data-a3dlg="ok"]').click();
    uiFlow.dlgClosed = !document.querySelector('.a3d-dlg');
    const st = window.__a3dState();
    const created = st.objs[st.objs.length - 1];
    uiFlow.created = created ? { name: created.name, bimType: created.bim && created.bim.type, hasPath: !!(created.bim && created.bim.path), railings: created.bim && created.bim.railings, faces: created.mesh.f.length } : null;
    const beforeDup = st.objs.length;
    window.__a3dDuplicate();
    const st2 = window.__a3dState();
    uiFlow.dupDelta = st2.objs.length - beforeDup;
    const dup = st2.objs[st2.objs.length - 1];
    uiFlow.duplicate = dup ? { hasPath: !!(dup.bim && dup.bim.path), railings: dup.bim && dup.bim.railings, pathShifted: dup.bim && dup.bim.path && dup.bim.path[0] } : null;
  }
  res.uiFlow = uiFlow;

  res.marker = window.__acad3dV43 || null;

  return res;
}
"""

FAILS = []
TOTAL = [0]


def check(cond, msg):
    TOTAL[0] += 1
    print(("  PASS  " if cond else "  FAIL  ") + msg)
    if not cond:
        FAILS.append(msg)


def topo_ok(label, t, expect_vol=None):
    check(t is not None, label + ": solid was produced")
    if not t:
        return
    check(t["dupDir"] == 0, label + ": no duplicated half-edge (got %d)" % t["dupDir"])
    check(t["bad"] == 0, label + ": every edge shared by exactly two faces (got %d bad)" % t["bad"])
    check(t["vol"] > 0, label + ": outward winding, positive volume (got %.4f)" % t["vol"])
    if expect_vol is not None:
        check(abs(t["vol"] - expect_vol) < 1e-4,
              label + ": volume close to expected (%.6f vs %.6f)" % (t["vol"], expect_vol))


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
        r = await pg.evaluate(PROBE)
        await b.close()

    print("\n== load ==")
    check(not errs, "no uncaught page errors on load (%s)" % (errs[:1] or "none"))
    check(r["marker"] is not None, "__acad3dV43 feature marker present")

    print("\n== straight (2-point, no landings) ==")
    s = r["straight"]
    check("error" not in s, "straight stair builds without error (%s)" % s.get("error"))
    if "error" not in s:
        topo_ok("straight", s["topo"])
        check(len(s["path"]) == 2, "path is preserved as the two clicked points")

    print("\n== L-turn (one landing, two flights) ==")
    l = r["lturn"]
    check("error" not in l, "L-turn stair builds without error (%s)" % l.get("error"))
    if "error" not in l:
        topo_ok("L-turn", l["topo"])
    ll = r["lturnLayout"]
    check("error" not in ll, "L-turn layout computes without error")
    if "error" not in ll:
        check(ll["flights"] == 2, "two flights either side of the turn (got %d)" % ll["flights"])
        check(ll["zones"] == 1, "one landing zone at the turn (got %d)" % ll["zones"])
        check(ll["landingEntries"] == 2, "landing represented as two sub-entries split at the mitered corner (got %d)" % ll["landingEntries"])

    print("\n== U-shape (two turns, three flights) ==")
    u = r["ushape"]
    check("error" not in u, "U-shape stair builds without error (%s)" % u.get("error"))
    if "error" not in u:
        topo_ok("U-shape", u["topo"])
    ul = r["ushapeLayout"]
    check("error" not in ul, "U-shape layout computes without error")
    if "error" not in ul:
        check(ul["flights"] == 3, "three flights for two turns (got %d)" % ul["flights"])
        check(ul["zones"] == 2, "two landings for two turns (got %d)" % ul["zones"])

    print("\n== guard railings (merged into the solid) ==")
    rl = r["railed"]
    check("error" not in rl, "railed stair builds without error (%s)" % rl.get("error"))
    if "error" not in rl:
        check(rl["railings"] is True, "bim.railings recorded true")
        check(abs(rl["railHeight"] - 0.9) < 1e-9, "bim.railHeight recorded (%s)" % rl["railHeight"])
        topo_ok("railed L-turn", rl["topo"])

    print("\n== fail-safe rejections ==")
    check(bool(r["badLanding"].get("error")), "segment too short for its landing is refused")
    check(bool(r["badShort"].get("error")), "path too short for the requested steps is refused")
    check(bool(r["badTooFewSteps"].get("error")), "too few steps for the number of flights is refused")
    check(bool(r["badDegenerate"].get("error")), "degenerate duplicate-point path is refused")

    print("\n== real UI flow (clicks -> Enter -> dialog -> duplicate) ==")
    uf = r["uiFlow"]
    check(uf.get("dlgOpened") is True, "Enter after 3 clicks opens the parameter dialog (finishStair)")
    check(uf.get("dlgClosed") is True, "OK submits and closes the dialog (buildStairSolid)")
    c = uf.get("created")
    check(c is not None, "a stair object was actually created")
    if c:
        check(c["bimType"] == "stair", "created object is bim.type stair")
        check(c["hasPath"] is True, "created stair carries a bim.path (new schema, not legacy start/dir)")
        check(c["railings"] is True, "created stair has railings recorded true (checkbox was honored)")
        check(c["faces"] > 0, "created stair has a non-empty mesh")
    check(uf.get("dupDelta") == 1, "duplicateSelection created exactly one copy")
    d = uf.get("duplicate")
    check(d is not None, "duplicate object exists")
    if d:
        check(d["hasPath"] is True, "duplicate also carries a bim.path (path-aware duplicate branch used)")
        check(d["railings"] is True, "duplicate preserves railings")
        check(d["pathShifted"] == [1, 1], "duplicate's path is shifted by the duplicate offset, not left in place")

    print("\n%d checks, %d failed" % (TOTAL[0], len(FAILS)))
    print("RESULT: " + ("PASS" if not FAILS else "FAIL"))
    return 1 if FAILS else 0


sys.exit(asyncio.run(main()))
