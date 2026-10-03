"""
bim_phase62_wall_openings_and_closure_browser_tests.py

Regression suite for the three maintenance fixes shipped as __acad3dV62 in canvas_v10.html.

THE BUG THIS SUITE EXISTS FOR, stated plainly because it was silent in the product: a wall could
only ever hold ONE opening. Cutting a door or a window ran csgSubtract against the wall's CURRENT
mesh, which for the second opening is the OUTPUT of the first BSP cut -- a surface carrying
T-junctions and sliver faces. Feeding a BSP kernel its own output is where naive CSG breaks down.
Measured on the plainest possible case, an 8 m x 0.3 m x 3 m wall with two 0.9 m doors: after the
second cut the solid came back at 7.200 m3, exactly the volume of the UNCUT wall, with an open
(non-closed) shell -- the second boolean had destroyed the first hole and produced garbage. The app
still reported "Door opening cut into Wall_1" and the model tree still listed both openings. Two
openings in one wall is not an exotic case; it is what nearly every real wall looks like.

The fix regenerates the wall's base solid from its own centreline/thickness/height/alignment and
subtracts EVERY opening in a SINGLE boolean, so the kernel never sees its own output as input no
matter how many openings accumulate. This suite therefore asserts EXACT volumes rather than merely
"the geometry is valid": the old bug's signature was a volume that had gone back UP to the uncut
figure while topology checks alone could still be talked into passing, so volume is the assertion
that actually discriminates fixed from broken.

SECOND FIX -- Check Model no longer false-positives on every real wall. bimMeshSanityCheck(m,true)
demands a strict manifold (every undirected edge used by exactly two faces). A boolean cut leaves
T-junctions (an unsplit neighbouring face's long edge met by two or three shorter collinear ones),
so EVERY wall with a door or window was reported as "Open shell" -- a false positive on the app's
most common object, which made the whole report untrustworthy. bimMeshClosureCheck resolves the
T-junctions with a collinear edge-chain sweep: unmatched directed edges are grouped by supporting
line and projected onto it, and a closed surface must have forward and backward traversals cancel
over every interval. This suite checks BOTH directions of that claim -- that a T-junctioned closed
solid passes, AND that a mesh with a real hole hidden behind T-junction-looking geometry still
fails -- because a check that only ever says "fine" would also have "fixed" the false positive.

THIRD FIX is source-level and checked without a browser: the removed remote @font-face bundle. The
app declared a webfont family whose every source was a CDN URL, applied across the whole UI with a
universal !important rule. Offline -- the app's stated operating mode -- that is 25 failed network
requests per load and a silent fallback, i.e. a direct violation of the project's own local-first
principle. The assertion here is simply that the file requests nothing over the network.

Run:  python3 bim_phase62_wall_openings_and_closure_browser_tests.py [path/to/canvas_v10.html]
"""
import asyncio, pathlib, re, sys
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
    return a is not None and b is not None and abs(a - b) <= tol


# ---------------------------------------------------------------------------------------------
# 1. API surface.
# ---------------------------------------------------------------------------------------------
PROBE_API = r"""
() => ({
  v62: window.__acad3dV62 || null,
  hasApi: !!(window.__a3dWall && window.__a3dDoorAt && window.__a3dWindowAt &&
             window.__a3dCheckModel && window.__a3dMeshClosureCheck && window.__a3dMeshSanityCheck &&
             window.__a3dRebuildWall && window.__a3dOpeningsOf && window.__a3dState)
})
"""

# ---------------------------------------------------------------------------------------------
# 2. Exact volumes for a straight wall taking one, two and three openings in sequence. Each figure
#    is computed by hand from the parameters, not read back from the app, so a regression that
#    merely produces "some valid solid" is caught:
#       base            8.0 * 0.3 * 3.0            = 7.200
#       door            0.9 * 2.1 * 0.3            = 0.567
#       window          1.2 * 1.4 * 0.3            = 0.504
# ---------------------------------------------------------------------------------------------
PROBE_SEQUENTIAL = r"""
() => {
  const M=(id)=>{const st=window.__a3dState();const o=st.objs.find(x=>x.id===id);
                 return o?window.__a3dMeshClosureCheck(o.mesh):null;};
  window.__a3dEnter(); window.__a3dTestSetObjs([]);
  const w=window.__a3dWall([[0,0],[8,0]],0.3,3,'center',false);
  const steps=[M(w)];
  window.__a3dDoorAt(w,[2,0],0.9,2.1);   steps.push(M(w));
  window.__a3dDoorAt(w,[6,0],0.9,2.1);   steps.push(M(w));
  window.__a3dWindowAt(w,[4,0],1.2,1.4,0.9); steps.push(M(w));
  return {wallId:w, steps:steps, openings:(window.__a3dOpeningsOf(w)||[]).length};
}
"""

# ---------------------------------------------------------------------------------------------
# 3. A CLOSED (4-segment) wall taking an opening on each of its four sides -- the perimeter-wall
#    case, and the one where the old sequential cut degraded fastest.
#       base   (10*2 + 7*2) * 0.3 * 3 minus corner double-count is not hand-derivable, so this
#              case asserts the DELTA from the app's own uncut base instead: every opening must
#              remove exactly its own box volume, and the total must equal the sum.
# ---------------------------------------------------------------------------------------------
PROBE_CLOSED_LOOP = r"""
() => {
  const M=(id)=>{const st=window.__a3dState();const o=st.objs.find(x=>x.id===id);
                 return o?window.__a3dMeshClosureCheck(o.mesh):null;};
  window.__a3dEnter(); window.__a3dTestSetObjs([]);
  const w=window.__a3dWall([[0,0],[10,0],[10,7],[0,7]],0.3,3,'center',true);
  const base=M(w);
  window.__a3dDoorAt(w,[5,0],0.9,2.1);
  window.__a3dWindowAt(w,[10,3.5],1.2,1.4,0.9);
  window.__a3dWindowAt(w,[5,7],1.2,1.4,0.9);
  window.__a3dWindowAt(w,[0,3.5],1.2,1.4,0.9);
  return {wallId:w, base:base, after:M(w), openings:(window.__a3dOpeningsOf(w)||[]).length,
          report:window.__a3dCheckModel()};
}
"""

# ---------------------------------------------------------------------------------------------
# 4. A parametric rebuild must re-cut EVERY opening at the new thickness, not just the first. This
#    is the same bug on the other code path (bimReapplyOpeningsToWall used to loop and re-feed
#    too), so it gets its own hand-computed figure:
#       new base    8.0 * 0.4 * 3.0 = 9.600
#       door        0.9 * 2.1 * 0.4 = 0.756
#       window      1.2 * 1.4 * 0.4 = 0.672
#       expected    9.600 - 0.756 - 0.672 = 8.172
# ---------------------------------------------------------------------------------------------
PROBE_REBUILD = r"""
() => {
  const M=(id)=>{const st=window.__a3dState();const o=st.objs.find(x=>x.id===id);
                 return o?window.__a3dMeshClosureCheck(o.mesh):null;};
  window.__a3dEnter(); window.__a3dTestSetObjs([]);
  const w=window.__a3dWall([[0,0],[8,0]],0.3,3,'center',false);
  window.__a3dDoorAt(w,[2,0],0.9,2.1);
  window.__a3dWindowAt(w,[6,0],1.2,1.4,0.9);
  const before=M(w);
  const ok=window.__a3dRebuildWall(w,0.4,3,'center');
  return {wallId:w, before:before, after:M(w), rebuilt:!!ok,
          openings:(window.__a3dOpeningsOf(w)||[]).length};
}
"""

# ---------------------------------------------------------------------------------------------
# 5. bimMeshClosureCheck against hand-built meshes whose correct answer is known by construction.
#    The T-junction pair is the important one: 'tjunction' is a closed box whose front face was
#    split in two while its neighbours were not (exactly what a boolean cut leaves behind), and
#    'tjunctionHole' is the SAME mesh with one of the split halves removed. A check that passes
#    the first and fails the second is actually resolving T-junctions; one that passes both has
#    simply been weakened until it stopped complaining.
# ---------------------------------------------------------------------------------------------
PROBE_CLOSURE_SYNTHETIC = r"""
() => {
  const V=[[0,0,0],[1,0,0],[1,1,0],[0,1,0],[0,0,1],[1,0,1],[1,1,1],[0,1,1]];
  const F=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]];
  const V2=V.concat([[0.5,0,0],[0.5,0,1]]);
  const F2=[[0,3,2,1],[4,5,6,7],[0,8,9,4],[8,1,5,9],[1,2,6,5],[2,3,7,6],[3,0,4,7]];
  return {
    box:          window.__a3dMeshClosureCheck({v:V,f:F}),
    openBox:      window.__a3dMeshClosureCheck({v:V,f:F.slice(0,5)}),
    corrupt:      window.__a3dMeshClosureCheck({v:V,f:F.concat([[0,3,2,1]])}),
    tjunction:    window.__a3dMeshClosureCheck({v:V2,f:F2}),
    tjunctionHole:window.__a3dMeshClosureCheck({v:V2,f:[[0,3,2,1],[4,5,6,7],[0,8,9,4],
                                                        [1,2,6,5],[2,3,7,6],[3,0,4,7]]}),
    empty:        window.__a3dMeshClosureCheck({v:[],f:[]})
  };
}
"""

# ---------------------------------------------------------------------------------------------
# 6. Check Model's report, end to end: a plain wall, an opening-cut wall, and a deliberately
#    broken solid in ONE project, so the report has to discriminate rather than answer uniformly.
# ---------------------------------------------------------------------------------------------
PROBE_CHECK_MODEL = r"""
() => {
  window.__a3dEnter(); window.__a3dTestSetObjs([]);
  const clean=window.__a3dWall([[0,0],[6,0]],0.3,3,'center',false);
  const cut=window.__a3dWall([[0,10],[8,10]],0.3,3,'center',false);
  window.__a3dDoorAt(cut,[3,10],0.9,2.1);
  window.__a3dDoorAt(cut,[6,10],0.9,2.1);
  // A hand-built open shell pushed straight into the object list: a box missing its top face.
  const V=[[20,0,0],[21,0,0],[21,1,0],[20,1,0],[20,0,1],[21,0,1],[21,1,1],[20,1,1]];
  const F=[[0,3,2,1],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]];
  const openId=window.__a3dPushTestObj({id:'openshell',t:'solid',name:'OpenShell',col:'#888',
                                        pos:[0,0,0],mesh:{v:V,f:F}});
  const report=window.__a3dCheckModel();
  const by=(id)=>report.filter(r=>r.id===id)[0]||null;
  return {clean:by(clean), cut:by(cut), open:by(openId), total:report.length};
}
"""

# ---------------------------------------------------------------------------------------------
# 7. Fail-safe: an opening that cannot be placed must leave the wall EXACTLY as it was. The old
#    path's real damage was accepting a bad boolean result; the new one verifies closure and a
#    strictly decreasing volume before it will touch wall.mesh, so a rejected cut has to be a
#    no-op on the geometry rather than a partially-applied one.
# ---------------------------------------------------------------------------------------------
PROBE_FAILSAFE = r"""
() => {
  const M=(id)=>{const st=window.__a3dState();const o=st.objs.find(x=>x.id===id);
                 return o?window.__a3dMeshClosureCheck(o.mesh):null;};
  window.__a3dEnter(); window.__a3dTestSetObjs([]);
  const w=window.__a3dWall([[0,0],[8,0]],0.3,3,'center',false);
  window.__a3dDoorAt(w,[4,0],0.9,2.1);
  const before=M(w);
  const beforeCount=(window.__a3dOpeningsOf(w)||[]).length;
  // A "door" taller and wider than the wall itself: the cut would consume the whole solid.
  const huge=window.__a3dDoorAt(w,[4,0],40,40);
  return {huge:huge, before:before, after:M(w),
          beforeCount:beforeCount, afterCount:(window.__a3dOpeningsOf(w)||[]).length};
}
"""


async def run_probe(page, name, script):
    print("\n== " + name + " ==")
    try:
        return await page.evaluate(script)
    except Exception as e:
        check(False, name + " threw: " + str(e))
        return None


def source_level_checks(path):
    print("\n== Source-level: no remote dependency ==")
    src = path.read_text(errors="replace")
    hosts = set(re.findall(r'https?://([A-Za-z0-9._-]+)', src))
    # AMENDED FOR V132: the owner asked for the map and open data ("just like how giraffe do").
    # The map's own servers and their credit links are the only remote names allowed, and they are
    # asked only once the map is turned on or an address is found -- V132's suite proves no
    # request is made before that. example.org is the reserved name in the custom URL's hint.
    v132 = {"tile.openstreetmap.org", "server.arcgisonline.com", "nominatim.openstreetmap.org",
            "www.openstreetmap.org", "www.arcgis.com", "tiles.example.org"}
    external = sorted(h for h in hosts if not h.endswith("w3.org") and h not in v132)
    check(not external,
          "no external host referenced anywhere in the file (found: " + (", ".join(external) or "none") + ")")
    check("@font-face" not in src or "font-public" not in src,
          "no remote @font-face bundle remains")
    check("canva-fonts-loaded" not in src,
          "the universal !important font rule and its body class are gone")


async def main():
    path = pathlib.Path(TARGET).resolve()
    if not path.exists():
        print("Target file not found: " + str(path))
        sys.exit(1)

    source_level_checks(path)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        page_errors = []
        page.on("pageerror", lambda e: page_errors.append(str(e)))
        await page.goto("file://" + str(path))
        await page.wait_for_timeout(400)

        r = await run_probe(page, "API surface", PROBE_API)
        if r:
            check(r["v62"] is not None, "V62 marker present: " + str(r["v62"]))
            check(r["hasApi"], "all required test hooks present")

        r = await run_probe(page, "Straight wall, three openings in sequence", PROBE_SEQUENTIAL)
        if r:
            steps = r["steps"]
            check(len(steps) == 4 and all(s for s in steps), "all four states readable")
            if len(steps) == 4 and all(steps):
                expected = [7.200, 7.200 - 0.567, 7.200 - 0.567 - 0.567,
                            7.200 - 0.567 - 0.567 - 0.504]
                labels = ["uncut", "after 1 door", "after 2 doors", "after 2 doors + 1 window"]
                for i in range(4):
                    check(close(steps[i]["vol"], expected[i], 1e-6),
                          "%s volume is %.3f m3 (got %.6f)" % (labels[i], expected[i], steps[i]["vol"]))
                    check(steps[i]["closed"] and not steps[i]["corrupt"],
                          labels[i] + ": solid is closed and not corrupt")
                check(steps[0]["manifold"],
                      "the uncut wall is a strict manifold (nothing has been cut yet)")
                check(not steps[1]["manifold"],
                      "a cut wall is NOT a strict manifold -- it has T-junctions, which is precisely "
                      "why the strict test alone gave a false positive")
            check(r["openings"] == 3, "all three opening markers exist, got " + str(r["openings"]))

        r = await run_probe(page, "Closed 4-segment wall, one opening per side", PROBE_CLOSED_LOOP)
        if r and r["base"] and r["after"]:
            removed = r["base"]["vol"] - r["after"]["vol"]
            expected = 0.9 * 2.1 * 0.3 + 3 * (1.2 * 1.4 * 0.3)
            check(close(removed, expected, 1e-6),
                  "exactly the four opening volumes were removed: %.6f expected, %.6f removed"
                  % (expected, removed))
            check(r["after"]["closed"] and not r["after"]["corrupt"],
                  "the four-opening perimeter wall is still a closed, uncorrupted solid")
            check(r["openings"] == 4, "all four opening markers exist, got " + str(r["openings"]))
            flagged = [x for x in r["report"] if not x["ok"]]
            check(not flagged, "Check Model flags nothing in this project, got " + str(len(flagged)))

        r = await run_probe(page, "Parametric rebuild re-cuts every opening", PROBE_REBUILD)
        if r and r["after"]:
            check(r["rebuilt"], "the thickness rebuild reported success")
            check(close(r["after"]["vol"], 8.172, 1e-6),
                  "after rebuilding to 0.4 m thick, volume is 8.172 m3 (got %.6f) -- i.e. BOTH "
                  "openings were re-cut at the new thickness" % r["after"]["vol"])
            check(r["after"]["closed"] and not r["after"]["corrupt"],
                  "the rebuilt wall is a closed, uncorrupted solid")
            check(r["openings"] == 2, "both opening markers survived the rebuild")

        r = await run_probe(page, "Closure check against hand-built meshes", PROBE_CLOSURE_SYNTHETIC)
        if r:
            check(r["box"]["closed"] and r["box"]["manifold"] and not r["box"]["corrupt"],
                  "a clean box: closed and a strict manifold")
            check(close(abs(r["box"]["vol"]), 1.0, 1e-9), "the box's volume is 1.0")
            check(not r["openBox"]["closed"] and not r["openBox"]["corrupt"],
                  "a box missing one face: open, and not mistaken for corruption")
            check(r["corrupt"]["corrupt"] and not r["corrupt"]["closed"],
                  "a duplicated face: reported as corruption, not as an open shell")
            check(r["tjunction"]["closed"] and not r["tjunction"]["manifold"]
                  and not r["tjunction"]["corrupt"],
                  "a T-junctioned closed box: closed, but correctly NOT called a strict manifold")
            check(not r["tjunctionHole"]["closed"],
                  "the SAME mesh with one split half removed is still reported OPEN -- the "
                  "T-junction tolerance did not become a blanket pass")
            check(not r["empty"]["closed"], "an empty mesh is not reported closed")

        r = await run_probe(page, "Check Model discriminates within one project", PROBE_CHECK_MODEL)
        if r:
            check(r["clean"] and r["clean"]["ok"] and r["clean"]["issue"] is None,
                  "a plain wall passes with no issue")
            check(r["clean"] and r["clean"]["manifold"] is True,
                  "a plain wall is reported as a strict manifold")
            check(r["cut"] and r["cut"]["ok"] and r["cut"]["issue"] is None,
                  "a wall with two doors passes -- the false positive is gone")
            check(r["cut"] and r["cut"]["manifold"] is False and r["cut"]["note"],
                  "the cut wall still DISCLOSES its T-junction topology in a note rather than "
                  "hiding the difference: " + str(r["cut"] and r["cut"]["note"]))
            check(r["open"] and not r["open"]["ok"] and r["open"]["issue"]
                  and "Open shell" in r["open"]["issue"],
                  "a genuinely open shell in the same project is still flagged: "
                  + str(r["open"] and r["open"]["issue"]))

        r = await run_probe(page, "Fail-safe: an impossible opening changes nothing", PROBE_FAILSAFE)
        if r and r["before"] and r["after"]:
            check(r["huge"] is None, "the oversized opening was refused (no marker returned)")
            check(close(r["after"]["vol"], r["before"]["vol"], 1e-9),
                  "the wall's volume is untouched by the refused cut (%.6f vs %.6f)"
                  % (r["before"]["vol"], r["after"]["vol"]))
            check(r["after"]["closed"] and not r["after"]["corrupt"],
                  "the wall is still a closed, uncorrupted solid after the refusal")
            check(r["afterCount"] == r["beforeCount"],
                  "no orphan opening marker was left behind by the refused cut")

        await browser.close()

        print("\n== Page errors ==")
        for e in page_errors:
            print("  " + e)
        check(len(page_errors) == 0, "zero uncaught page errors across all probes")

    print("\n" + str(TOTAL[0] - len(FAILS)) + "/" + str(TOTAL[0]) + " checks passed")
    if FAILS:
        print("\nFAILED:")
        for f in FAILS:
            print("  - " + f)
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
