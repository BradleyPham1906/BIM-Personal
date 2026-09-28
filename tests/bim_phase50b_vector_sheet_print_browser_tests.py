"""
bim_phase50b_vector_sheet_print_browser_tests.py

Regression suite for Phase 50b (__acad3dV57) in canvas_v10.html: real vector sheet printing,
replacing bimPrintSheet's embedded-PNG round-trip -- the priority (1) item explicitly named in the
Phase 50 STATUS.md entry's own "Next" section ("replace bimPrintSheet's embedded-PNG sheet
printing with vector output built from bimBuildSVG, which is what actually fixes print quality for
real client hand-offs, the roadmap's original stated motivation").

WHAT SHIPPED, IN ONE SENTENCE: bimBuildSheetSVG() builds one full sheet page as a single vector SVG
-- real vector geometry (bimBuildPlanViewportSVG) for every 'plan'-kind viewport, a vector title
block, and vector borders/labels on every viewport regardless of kind -- while 'elevation'/'view'/
'schedule' viewports (and any viewport whose source fails to resolve) still rasterize, embedded as
<image> elements inside that same vector page. bimPrintSheet() now prints this SVG directly (no PNG
dataURL, no <img> at all) and only falls back to the previous PNG-embed path
(bimPrintSheetRasterFallback) if the vector build itself throws. A companion "Export Sheet as SVG"
command (bimExportSheetSVG) ships alongside, mirroring Phase 50's export-command-plus-builder
precedent, wired to a new toolbar button next to "Export PNG".

WHY 'plan' ONLY GETS REAL VECTOR: a plan viewport's camera is fixed by bimResolveViewportSource at
yaw=0, pitch~1.52 rad (a deliberate near-top-down camera nudged off the exact 90-degree gimbal-lock
singularity) for EVERY plan viewport, with no rotation freedom. That fixed yaw=0 is what lets the
eye-to-target vertical-axis math cancel out exactly (not approximately) into a closed-form 2D
transform -- see the derivation comment above bimBuildPlanViewportSVG in canvas_v10.html. Elevation
and saved/section views have arbitrary yaw/pitch and would need genuine 3D mesh silhouette/
wireframe projection to vectorize correctly; that is a materially larger, separate feature,
deliberately deferred and NOT attempted here. Schedules are tabular, not geometric, and already have
their own separate raster-to-canvas draw path (bimDrawScheduleViewport) reused unchanged.

CORRECTNESS STRATEGY: rather than only re-invoking the same internal formula the implementation
uses (which would just be a tautology), the core geometry checks here are dimensionally independent
of that formula: they place a wall with EXACTLY KNOWN world-space corner coordinates, ask for a
1:100 ratio-scale plan viewport, and assert the projected SVG distance between two corners that
differ only in world X (or only in world Z) equals the expected real-world distance scaled by
1000/100 = 10 mm per model metre -- a physical invariant any correct implementation must satisfy,
independent of how the projection math is internally derived. A perpendicularity check on the two
projected edges additionally guards against any shear/skew distortion sneaking into the transform.

NOT done in this phase, flagged rather than silently left implicit: elevation/section views still
rasterize (a separate, larger feature); door/window opening cuts are still not drawn into a wall's
plan outline anywhere in the vector path (the same pre-existing, shared limitation already
documented for bimBuildDXF/bimBuildSVG in Phase 50 -- not a regression introduced here); the
interactive on-screen sheet editor (bimRenderSheet/bimSheetViewRefresh) is completely untouched.

Run:  python3 bim_phase50b_vector_sheet_print_browser_tests.py [path/to/canvas_v10.html]
"""
import asyncio, math, pathlib, sys
import xml.etree.ElementTree as ET
from playwright.async_api import async_playwright

TARGET = sys.argv[1] if len(sys.argv) > 1 else "canvas_v10.html"

TOTAL = [0]
FAILS = []


def check(cond, msg):
    TOTAL[0] += 1
    print(("  PASS  " if cond else "  FAIL  ") + msg)
    if not cond:
        FAILS.append(msg)


def close(a, b, tol=1e-3):
    return abs(a - b) <= tol


SVG_NS = "{http://www.w3.org/2000/svg}"


def parse_svg(svg_text):
    try:
        return ET.fromstring(svg_text), None
    except ET.ParseError as e:
        return None, e


def local_tag(el):
    return el.tag.split("}")[-1] if "}" in el.tag else el.tag


def path_points(d):
    """Very small M/L path-data parser -- good enough for the axis-aligned paths this suite emits."""
    pts = []
    tok = d.replace("M", " M ").replace("L", " L ").replace("Z", " Z ").split()
    i = 0
    while i < len(tok):
        if tok[i] in ("M", "L"):
            x, y = tok[i + 1].split(",")
            pts.append((float(x), float(y)))
            i += 2
        else:
            i += 1
    return pts


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


# ---------------------------------------------------------------------------------------------
# 1. API surface present.
# ---------------------------------------------------------------------------------------------
PROBE_API = r"""
() => {
  return {
    marker: window.__acad3dV57 || null,
    hasApi: !!(window.__a3dTestSetObjs && window.__a3dWall && window.__a3dAddLevel &&
               window.__a3dActiveLevel && window.__a3dAddSheet && window.__a3dAddViewport &&
               window.__a3dSetViewportRect && window.__a3dBuildSheetSVG &&
               window.__a3dBuildPlanViewportSVG && window.__a3dResolveViewportSource &&
               window.__a3dSheetSolveCamera && window.__a3dSheets)
  };
}
"""

# ---------------------------------------------------------------------------------------------
# 2. Dimensional correctness: a wall with known corners, a 1:100 ratio plan viewport, and the
#    projected edge lengths must match 1000/100 = 10mm per model metre on both axes, with the two
#    edges staying perpendicular (no shear).
# ---------------------------------------------------------------------------------------------
PROBE_RATIO_SCALE_CORRECTNESS = r"""
() => {
  const out = {};
  window.__a3dTestSetObjs([]);
  const lvl = window.__a3dActiveLevel();
  const wallId = window.__a3dWall([[0,0],[8,0],[8,5],[0,5]], 0.3, 3, 'center', true);
  const sheetId = window.__a3dAddSheet('A-101', 'Ratio Test Sheet', 'A1');
  const vpId = window.__a3dAddViewport(sheetId, 'plan', lvl.id, 'ratio', 100);
  window.__a3dSetViewportRect(sheetId, vpId, 20, 20, 400, 300);

  const sheets = window.__a3dSheets();
  const sheet = sheets.find(s => s.id === sheetId);
  const vp = sheet.viewports.find(v => v.id === vpId);

  const pv = window.__a3dBuildPlanViewportSVG(sheetId, vpId);
  out.wallId = wallId;
  out.pv = pv;
  out.vp = vp;
  out.fullSvg = window.__a3dBuildSheetSVG(sheetId);
  return out;
}
"""

# ---------------------------------------------------------------------------------------------
# 3. Level filter: a plan viewport bound to Level 0 must include Level 0's wall and exclude a
#    wall created on a subsequently-added Level 1.
# ---------------------------------------------------------------------------------------------
PROBE_LEVEL_FILTER = r"""
() => {
  const out = {};
  window.__a3dTestSetObjs([]);
  const lvl0 = window.__a3dActiveLevel();
  const wall0 = window.__a3dWall([[0,0],[4,0],[4,3],[0,3]], 0.3, 3, 'center', true);
  window.__a3dAddLevel();
  const lvl1 = window.__a3dActiveLevel();
  const wall1 = window.__a3dWall([[10,10],[14,10],[14,13],[10,13]], 0.3, 3, 'center', true);

  const sheetId = window.__a3dAddSheet('A-102', 'Level Filter Sheet', 'A1');
  const vpId = window.__a3dAddViewport(sheetId, 'plan', lvl0.id, 'fit', 100);
  window.__a3dSetViewportRect(sheetId, vpId, 10, 10, 250, 180);

  out.wall0 = wall0;
  out.wall1 = wall1;
  out.lvl0Id = lvl0.id;
  out.lvl1Id = lvl1.id;
  out.svg = window.__a3dBuildSheetSVG(sheetId);
  return out;
}
"""

# ---------------------------------------------------------------------------------------------
# 4. Unresolvable viewport source (deleted level) must degrade to an error placeholder inside the
#    vector page, not throw and not crash the whole sheet build.
# ---------------------------------------------------------------------------------------------
PROBE_RESOLVE_ERROR = r"""
() => {
  const out = {};
  window.__a3dTestSetObjs([]);
  const lvl = window.__a3dActiveLevel();
  const sheetId = window.__a3dAddSheet('A-103', 'Error Sheet', 'A1');
  const vpId = window.__a3dAddViewport(sheetId, 'plan', lvl.id, 'fit', 100);
  window.__a3dSetViewportRect(sheetId, vpId, 10, 10, 200, 150);
  // A viewport referencing a level id that does not exist -- bimResolveViewportSource must error.
  const sheetId2 = window.__a3dAddSheet('A-104', 'Error Sheet 2', 'A1');
  const vpId2 = window.__a3dAddViewport(sheetId2, 'plan', 'lvl-does-not-exist', 'fit', 100);
  window.__a3dSetViewportRect(sheetId2, vpId2, 10, 10, 200, 150);

  out.threw = false;
  try {
    out.svg = window.__a3dBuildSheetSVG(sheetId2);
  } catch (e) {
    out.threw = true;
    out.err = String(e);
  }
  return out;
}
"""

# ---------------------------------------------------------------------------------------------
# 5. Raster-fallback kinds (elevation, schedule) still embed as <image> inside the vector page,
#    and the whole multi-viewport sheet (mixing plan + elevation + schedule) builds without error.
# ---------------------------------------------------------------------------------------------
PROBE_MIXED_KINDS = r"""
() => {
  const out = {};
  window.__a3dTestSetObjs([]);
  const lvl = window.__a3dActiveLevel();
  const wallId = window.__a3dWall([[0,0],[5,0],[5,3],[0,3]], 0.3, 3, 'center', true);
  const sheetId = window.__a3dAddSheet('A-105', 'Mixed Kinds Sheet', 'A1');
  const vpPlan = window.__a3dAddViewport(sheetId, 'plan', lvl.id, 'fit', 100);
  window.__a3dSetViewportRect(sheetId, vpPlan, 10, 10, 180, 130);
  const vpElev = window.__a3dAddViewport(sheetId, 'elevation', 'front', 'fit', 100);
  window.__a3dSetViewportRect(sheetId, vpElev, 200, 10, 180, 130);
  const vpSched = window.__a3dAddViewport(sheetId, 'schedule', 'room', 'fit', 100);
  window.__a3dSetViewportRect(sheetId, vpSched, 10, 150, 370, 100);

  out.wallId = wallId;
  out.vpPlan = vpPlan;
  out.vpElev = vpElev;
  out.vpSched = vpSched;
  out.svg = window.__a3dBuildSheetSVG(sheetId);
  return out;
}
"""

# ---------------------------------------------------------------------------------------------
# 6. Title block, XML-hostile sheet name/number round-trip correctly; border+label rects/text
#    exist for every viewport regardless of kind.
# ---------------------------------------------------------------------------------------------
PROBE_TITLE_BLOCK = r"""
() => {
  const out = {};
  window.__a3dTestSetObjs([]);
  const lvl = window.__a3dActiveLevel();
  window.__a3dWall([[0,0],[3,0],[3,2],[0,2]], 0.3, 3, 'center', true);
  const sheetId = window.__a3dAddSheet('B-1 & <2>', 'Client "Ltd" Sheet', 'A1');
  const vpId = window.__a3dAddViewport(sheetId, 'plan', lvl.id, 'fit', 100);
  window.__a3dSetViewportRect(sheetId, vpId, 10, 10, 200, 150);
  if (window.__a3dTitleBlockSet) {
    window.__a3dTitleBlockSet({project: 'Test & <Project>', drawnBy: 'X', checkedBy: 'Y', client: 'Acme "Co"'});
  }
  out.svg = window.__a3dBuildSheetSVG(sheetId);
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

        print("== API surface ==")
        r = await pg.evaluate(PROBE_API)
        check(r.get("marker") is not None, "V57 marker present (%r)" % r.get("marker"))
        check(r.get("hasApi"), "all V57 test hooks present")

        print("\n== 1:100 ratio-scale dimensional correctness ==")
        r = await pg.evaluate(PROBE_RATIO_SCALE_CORRECTNESS)
        pv = r.get("pv") or {}
        check(bool(pv.get("svg")), "bimBuildPlanViewportSVG returned an svg fragment")
        frag = ('<g xmlns="http://www.w3.org/2000/svg">' + pv.get("svg", "") + "</g>") if pv.get("svg") else None
        root = None
        if frag:
            root, perr = parse_svg(frag)
            check(root is not None, "plan viewport fragment is well-formed XML (%s)" % (perr or "ok"))
        if root is not None:
            path_el = root.find(".//" + SVG_NS + "path[@data-obj='%s']" % r["wallId"])
            check(path_el is not None, "wall centerline emits a <path> tagged with its object id")
            if path_el is not None:
                pts = path_points(path_el.attrib["d"])
                check(len(pts) >= 4, "wall path has at least 4 projected corner points (%d)" % len(pts))
                if len(pts) >= 4:
                    # centerline is stored in the exact input order: (0,0),(8,0),(8,5),(0,5)
                    edge_x = dist(pts[0], pts[1])   # world delta: (8,0) i.e. pure X, 8m
                    edge_z = dist(pts[1], pts[2])   # world delta: (0,5) i.e. pure Z, 5m
                    expect_x = 8 * (1000 / 100)     # 80mm
                    expect_z = 5 * (1000 / 100)     # 50mm
                    check(close(edge_x, expect_x, tol=0.5),
                          "pure-X 8m edge projects to %.3fmm at 1:100 (expected %.1fmm)" % (edge_x, expect_x))
                    check(close(edge_z, expect_z, tol=0.5),
                          "pure-Z 5m edge projects to %.3fmm at 1:100 (expected %.1fmm)" % (edge_z, expect_z))
                    # perpendicularity: dot product of the two edge vectors should be ~0 (no shear)
                    v1 = (pts[1][0]-pts[0][0], pts[1][1]-pts[0][1])
                    v2 = (pts[2][0]-pts[1][0], pts[2][1]-pts[1][1])
                    dot = v1[0]*v2[0] + v1[1]*v2[1]
                    mag = math.hypot(*v1) * math.hypot(*v2)
                    cos_angle = dot / mag if mag > 1e-9 else None
                    check(cos_angle is not None and close(cos_angle, 0.0, tol=0.01),
                          "the two projected edges stay perpendicular, no shear/skew (cos=%r)" % cos_angle)
        full_root, fperr = parse_svg(r.get("fullSvg", ""))
        check(full_root is not None, "full sheet SVG (with this viewport) is well-formed XML (%s)" % (fperr or "ok"))
        if full_root is not None:
            vb = full_root.attrib.get("viewBox", "").split()
            check(len(vb) == 4 and close(float(vb[2]), 594.0, tol=1.0) and close(float(vb[3]), 841.0, tol=1.0),
                  "sheet viewBox matches the A1 page size in mm (%r)" % vb)

        print("\n== level filter ==")
        r = await pg.evaluate(PROBE_LEVEL_FILTER)
        root, perr = parse_svg(r.get("svg", ""))
        check(root is not None, "level-filter sheet SVG is well-formed XML (%s)" % (perr or "ok"))
        if root is not None:
            has_wall0 = root.find(".//" + SVG_NS + "path[@data-obj='%s']" % r["wall0"]) is not None
            has_wall1 = root.find(".//" + SVG_NS + "path[@data-obj='%s']" % r["wall1"]) is not None
            check(has_wall0, "Level 0's wall is drawn in the Level-0-bound plan viewport")
            check(not has_wall1, "Level 1's wall is NOT drawn in the Level-0-bound plan viewport (level filter holds)")

        print("\n== unresolvable viewport source degrades safely ==")
        r = await pg.evaluate(PROBE_RESOLVE_ERROR)
        check(not r.get("threw"), "bimBuildSheetSVG does not throw for an unresolvable viewport (%r)" % r.get("err"))
        if not r.get("threw"):
            root, perr = parse_svg(r.get("svg", ""))
            check(root is not None, "error-viewport sheet SVG is still well-formed XML (%s)" % (perr or "ok"))
            if root is not None:
                err_rect = root.find(".//" + SVG_NS + "rect[@fill='#f4f4f4']")
                err_text = None
                for t in root.iter(SVG_NS + "text"):
                    if t.attrib.get("fill") == "#cc3333":
                        err_text = t
                        break
                check(err_rect is not None, "an error-placeholder rect is drawn for the unresolvable viewport")
                check(err_text is not None and "Level no longer exists" in (err_text.text or ""),
                      "the error placeholder shows the actual resolver error message (%r)" %
                      (err_text.text if err_text is not None else None))

        print("\n== mixed viewport kinds (plan + elevation + schedule) ==")
        r = await pg.evaluate(PROBE_MIXED_KINDS)
        root, perr = parse_svg(r.get("svg", ""))
        check(root is not None, "mixed-kinds sheet SVG is well-formed XML (%s)" % (perr or "ok"))
        if root is not None:
            plan_path = root.find(".//" + SVG_NS + "path[@data-obj='%s']" % r["wallId"])
            check(plan_path is not None, "the plan viewport still drew real vector geometry alongside raster viewports")
            images = root.findall(".//" + SVG_NS + "image")
            check(len(images) == 2, "exactly 2 raster <image> embeds exist (elevation + schedule), got %d" % len(images))
            for img in images:
                href = img.attrib.get("href", "")
                check(href.startswith("data:image/png"), "raster embed href is an inline PNG data URL (%r...)" % href[:24])
            borders = root.findall(".//" + SVG_NS + "rect[@stroke='#888888']")
            check(len(borders) == 3, "every one of the 3 viewports (plan/elevation/schedule) got a vector border rect (%d)" % len(borders))

        print("\n== title block + XML-hostile content ==")
        r = await pg.evaluate(PROBE_TITLE_BLOCK)
        root, perr = parse_svg(r.get("svg", ""))
        check(root is not None, "title-block sheet SVG is well-formed XML (%s)" % (perr or "ok"))
        if root is not None:
            texts = [t.text or "" for t in root.iter(SVG_NS + "text")]
            check(any("B-1 & <2>" in t for t in texts), "sheet number with XML-hostile characters round-trips correctly")
            check(any('Client "Ltd" Sheet' in t for t in texts), "sheet name with XML-hostile characters round-trips correctly")
            check(any("Test & <Project>" in t for t in texts), "title block project field round-trips correctly")
            check(any('Acme "Co"' in t for t in texts), "title block client field round-trips correctly")

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
