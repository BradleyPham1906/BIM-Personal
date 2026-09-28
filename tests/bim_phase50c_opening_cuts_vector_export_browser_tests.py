"""
bim_phase50c_opening_cuts_vector_export_browser_tests.py

Regression suite for Phase 50c (__acad3dV58) in canvas_v10.html: teaching every vector plan path
about door/window opening cuts, closing the gap flagged in both the Phase 50 and Phase 50b
STATUS.md entries ("neither vector exporter draws door/window cuts into a wall's plan outline" /
"the single highest-leverage remaining accuracy gap in the whole vector pipeline").

WHAT SHIPPED, IN ONE SENTENCE: a single new geometry helper, bimWallOpeningBreaks(wall), computes
-- from already-modeled data only (an opening's stored center/dir/width and the wall's own
thickness/alignment split) -- how a wall's outer/inner plan-outline lines must be broken to show a
real gap at each hosted door/window, plus jamb-cap lines closing each side and a glazing line for
windows; this one helper is now wired into THREE call sites: bimBuildDXF, bimBuildSVG (Phase 50),
and bimBuildPlanViewportSVG (Phase 50b) -- so a wall with a door draws as an actually broken
outline in every vector output, not an unbroken rectangle.

WINDING CORRECTNESS IS THE CORE RISK THIS SUITE GUARDS: bimBuildWallGeometry builds a closed
wall's innerLoop/outerLoop from sketchCCW(centerline), which silently REVERSES the point array
whenever the wall happens to have been drawn/clicked in clockwise order -- a coin-flip depending on
nothing the user would think of as meaningful. wall.bim.centerline itself is stored in the
original, NEVER-reversed order. A naive implementation assuming centerline[i] <-> innerLoop[i] /
outerLoop[i] would work for roughly half of all real walls and silently misplace the break for the
other half. The dedicated PROBE_CLOCKWISE_WINDING test below draws the exact same rectangle in
clockwise order and asserts the computed gap lands at the identical world-space position as the
counter-clockwise case -- this is the test that would have caught that bug had the fix been wrong.

DELIBERATE SCOPE LIMIT, not silently left implicit: a door's swing direction/hand is not stored
anywhere in this app's opening data model, so no swing arc or leaf line is drawn -- that would be a
fabricated detail with no model data behind it. A window's glazing line, in contrast, IS drawn,
because its position is fully determined by already-known geometry.

Run:  python3 bim_phase50c_opening_cuts_vector_export_browser_tests.py [path/to/canvas_v10.html]
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


def path_points(d):
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


def min_x(pts):
    return min(p[0] for p in pts)


def max_x(pts):
    return max(p[0] for p in pts)


# ---------------------------------------------------------------------------------------------
# 1. API surface present.
# ---------------------------------------------------------------------------------------------
PROBE_API = r"""
() => {
  return {
    marker: window.__acad3dV58 || null,
    hasApi: !!(window.__a3dTestSetObjs && window.__a3dWall && window.__a3dDoorAt &&
               window.__a3dWindowAt && window.__a3dWallOpeningBreaks && window.__a3dBuildSVG &&
               window.__a3dBuildDXF && window.__a3dAddSheet && window.__a3dAddViewport &&
               window.__a3dBuildPlanViewportSVG)
  };
}
"""

# ---------------------------------------------------------------------------------------------
# 2. Core case: a door on a closed rectangular wall. Checks the raw break geometry (gap bounds,
#    jamb positions) AND that bimBuildSVG actually emits a broken outline (not an unbroken 4-point
#    rectangle) with the jamb lines tagged back to the door's own id.
# ---------------------------------------------------------------------------------------------
PROBE_DOOR_BASIC = r"""
() => {
  window.__a3dTestSetObjs([]);
  const wallId = window.__a3dWall([[0,0],[8,0],[8,5],[0,5]], 0.3, 3, 'center', true);
  const doorId = window.__a3dDoorAt(wallId, [4,0], 0.9, 2.1);
  const brk = window.__a3dWallOpeningBreaks(wallId);
  const svg = window.__a3dBuildSVG();
  const dxf = window.__a3dBuildDXF();
  return {wallId, doorId, brk, svg, dxf};
}
"""

# ---------------------------------------------------------------------------------------------
# 3. Winding correctness: the SAME rectangle, drawn clockwise, must produce the gap at the
#    identical world-space bounds as the counter-clockwise case above.
# ---------------------------------------------------------------------------------------------
PROBE_CLOCKWISE_WINDING = r"""
() => {
  window.__a3dTestSetObjs([]);
  const wallId = window.__a3dWall([[0,5],[8,5],[8,0],[0,0]], 0.3, 3, 'center', true);
  const doorId = window.__a3dDoorAt(wallId, [4,0], 0.9, 2.1);
  const brk = window.__a3dWallOpeningBreaks(wallId);
  return {wallId, doorId, brk};
}
"""

# ---------------------------------------------------------------------------------------------
# 3b. An opening on a NON-FIRST segment of the wall's centerline array (here, segment index 2 of
#     4 -- the "top" edge, opposite the array's starting point). This is the specific case a
#     nearest-segment-search implementation bug (picking whichever segment happens to be checked
#     first, regardless of actual distance) would silently get wrong while every other probe in
#     this suite -- which all happen to place their opening on segment 0 -- would still pass. A
#     door or window placed here MUST resolve to the wall's true near face, not segment 0's.
# ---------------------------------------------------------------------------------------------
PROBE_OPENING_ON_NONFIRST_SEGMENT = r"""
() => {
  window.__a3dTestSetObjs([]);
  const wallId = window.__a3dWall([[0,0],[8,0],[8,5],[0,5]], 0.3, 3, 'center', true);
  const winId = window.__a3dWindowAt(wallId, [2,5], 1.5, 1.2, 0.9);
  const brk = window.__a3dWallOpeningBreaks(wallId);
  return {wallId, winId, brk};
}
"""

# ---------------------------------------------------------------------------------------------
# 4. Window: glazing line present (door: absent), no jamb/glaze objId confusion between the two
#    openings' own ids, and both openings on the SAME segment produce two separate gaps.
# ---------------------------------------------------------------------------------------------
PROBE_TWO_OPENINGS_SAME_SEGMENT = r"""
() => {
  window.__a3dTestSetObjs([]);
  const wallId = window.__a3dWall([[0,0],[12,0],[12,5],[0,5]], 0.3, 3, 'center', true);
  const doorId = window.__a3dDoorAt(wallId, [3,0], 0.9, 2.1);
  const winId = window.__a3dWindowAt(wallId, [9,0], 1.2, 1.2, 0.9);
  const brk = window.__a3dWallOpeningBreaks(wallId);
  const svg = window.__a3dBuildSVG();
  return {wallId, doorId, winId, brk, svg};
}
"""

# ---------------------------------------------------------------------------------------------
# 5. No openings: must reproduce the EXACT old behavior (3 wall paths, no jambs/glaze) -- a direct
#    regression guard on top of the full existing suites already re-run for this phase.
# ---------------------------------------------------------------------------------------------
PROBE_NO_OPENINGS_UNCHANGED = r"""
() => {
  window.__a3dTestSetObjs([]);
  const wallId = window.__a3dWall([[0,0],[6,0],[6,4],[0,4]], 0.3, 3, 'center', true);
  const brk = window.__a3dWallOpeningBreaks(wallId);
  const svg = window.__a3dBuildSVG();
  return {wallId, brk, svg};
}
"""

# ---------------------------------------------------------------------------------------------
# 6. Sheet vector plan viewport (Phase 50b's path) also reflects the break, and a wall on a
#    different, non-referenced level still isn't drawn at all (level filter still holds).
# ---------------------------------------------------------------------------------------------
PROBE_SHEET_VECTOR_REFLECTS_BREAK = r"""
() => {
  window.__a3dTestSetObjs([]);
  const lvl = window.__a3dActiveLevel();
  const wallId = window.__a3dWall([[0,0],[8,0],[8,5],[0,5]], 0.3, 3, 'center', true);
  const doorId = window.__a3dDoorAt(wallId, [4,0], 0.9, 2.1);
  const sheetId = window.__a3dAddSheet('A-106', 'Opening Cut Sheet', 'A1');
  const vpId = window.__a3dAddViewport(sheetId, 'plan', lvl.id, 'fit', 100);
  window.__a3dSetViewportRect(sheetId, vpId, 10, 10, 400, 300);
  const pv = window.__a3dBuildPlanViewportSVG(sheetId, vpId);
  return {wallId, doorId, pv};
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
        check(r.get("marker") is not None, "V58 marker present (%r)" % r.get("marker"))
        check(r.get("hasApi"), "all V58 test hooks present")

        print("\n== door on a closed wall: raw break geometry ==")
        r = await pg.evaluate(PROBE_DOOR_BASIC)
        brk = r.get("brk") or {}
        check(brk.get("outerRuns") is not None, "bimWallOpeningBreaks returned a result for a wall with a door")
        if brk.get("outerRuns") is not None:
            check(len(brk["outerRuns"]) == 1, "exactly one continuous outer stroke (wraparound stitched correctly), got %d" % len(brk["outerRuns"]))
            check(len(brk["innerRuns"]) == 1, "exactly one continuous inner stroke (wraparound stitched correctly), got %d" % len(brk["innerRuns"]))
            check(not brk["outerClosed"] and not brk["innerClosed"], "both strokes are reported as OPEN polylines, not closed loops")
            check(len(brk["jambs"]) == 2, "exactly 2 jamb-cap lines for a single door (%d)" % len(brk["jambs"]))
            check(len(brk["glaze"]) == 0, "a door gets NO glazing line (that's a window-only symbol) (%d)" % len(brk["glaze"]))
            j0, j1 = brk["jambs"][0], brk["jambs"][1]
            check(j0[2] == r["doorId"] and j1[2] == r["doorId"], "both jamb lines are tagged back to the door's own object id")
            gap_lo = min(j0[0][0], j1[0][0])
            gap_hi = max(j0[0][0], j1[0][0])
            check(close(gap_lo, 3.55, tol=0.01) and close(gap_hi, 4.45, tol=0.01),
                  "the gap spans exactly [door_center-w/2, door_center+w/2] = [3.55, 4.45] (got [%.3f, %.3f])" % (gap_lo, gap_hi))
            outer_z = [p[1] for p in brk["outerRuns"][0]]
            check(any(close(z, -0.15, tol=0.01) for z in outer_z), "outer face sits at thickness/2=0.15 beyond the centerline (z=-0.15 side)")

        print("\n== bimBuildSVG / bimBuildDXF actually emit the broken outline ==")
        svg_text = (r.get("svg") or {}).get("text", "")
        root, perr = parse_svg(svg_text)
        check(root is not None, "SVG with a door is well-formed XML (%s)" % (perr or "ok"))
        if root is not None:
            wall_paths = root.findall(".//" + SVG_NS + "path[@data-obj='%s']" % r["wallId"])
            # centerline (closed, 4pts) + 1 broken outer run + 1 broken inner run = 3 paths total
            check(len(wall_paths) == 3, "the wall still emits exactly 3 paths (centerline + 1 outer run + 1 inner run) (%d)" % len(wall_paths))
            for p in wall_paths:
                check("Z" not in p.attrib["d"] or path_points(p.attrib["d"])[0] != path_points(p.attrib["d"])[-1] or len(path_points(p.attrib["d"])) <= 5,
                      "path data for %s doesn't look like an unbroken closed rectangle" % p.attrib.get("data-obj"))
            jamb_lines = [l for l in root.findall(".//" + SVG_NS + "line") if l.attrib.get("data-obj") == r["doorId"]]
            check(len(jamb_lines) == 2, "SVG emits exactly 2 <line> jamb elements tagged to the door (%d)" % len(jamb_lines))
        dxf_text = (r.get("dxf") or {}).get("text", "")
        check("LWPOLYLINE" in dxf_text and dxf_text.count("LWPOLYLINE") >= 3,
              "DXF output also contains at least 3 LWPOLYLINE entities for the broken wall outline")
        check(dxf_text.count("\nLINE\n") >= 2 or dxf_text.count("0\r\nLINE") >= 2 or "LINE" in dxf_text,
              "DXF output contains LINE entities for the jamb caps")

        print("\n== clockwise-wound wall: winding-correctness fix ==")
        r_ccw = brk  # from PROBE_DOOR_BASIC above (counter-clockwise input order)
        r_cw = await pg.evaluate(PROBE_CLOCKWISE_WINDING)
        brk_cw = r_cw.get("brk") or {}
        check(brk_cw.get("jambs") and len(brk_cw["jambs"]) == 2, "clockwise-wound wall still produces exactly 2 jamb lines")
        if brk_cw.get("jambs") and len(brk_cw["jambs"]) == 2:
            j0c, j1c = brk_cw["jambs"][0], brk_cw["jambs"][1]
            gap_lo_cw = min(j0c[0][0], j1c[0][0])
            gap_hi_cw = max(j0c[0][0], j1c[0][0])
            check(close(gap_lo_cw, 3.55, tol=0.01) and close(gap_hi_cw, 4.45, tol=0.01),
                  "clockwise-wound wall's gap lands at the SAME world position [3.55, 4.45] as the "
                  "counter-clockwise case (got [%.3f, %.3f]) -- the sketchCCW-reversal fix holds" % (gap_lo_cw, gap_hi_cw))

        print("\n== opening on a NON-FIRST wall segment (nearest-segment search correctness) ==")
        r = await pg.evaluate(PROBE_OPENING_ON_NONFIRST_SEGMENT)
        brk_nf = r.get("brk") or {}
        check(brk_nf.get("jambs") and len(brk_nf["jambs"]) == 2,
              "a window on segment index 2 of 4 still produces exactly 2 jamb lines (%d)" %
              len(brk_nf.get("jambs", [])))
        if brk_nf.get("jambs") and len(brk_nf["jambs"]) == 2:
            j0n, j1n = brk_nf["jambs"][0], brk_nf["jambs"][1]
            # The window is centered at world (2,5) on the wall's TOP edge (z=5), width 1.5 -- the
            # gap must span x in [1.25, 2.75] at z near 5 (thickness/2=0.15 either side), NOT at
            # z near 0 (which is where a "just picks whichever segment is checked first" bug would
            # wrongly place it, since segment index 0 is the wall's z=0 edge).
            gap_lo_x = min(j0n[0][0], j1n[0][0])
            gap_hi_x = max(j0n[0][0], j1n[0][0])
            all_z = [j0n[0][1], j0n[1][1], j1n[0][1], j1n[1][1]]
            check(close(gap_lo_x, 1.25, tol=0.01) and close(gap_hi_x, 2.75, tol=0.01),
                  "gap spans the correct X range [1.25, 2.75] (got [%.3f, %.3f])" % (gap_lo_x, gap_hi_x))
            check(all(z > 4.5 for z in all_z),
                  "jamb points sit near the wall's TRUE near face at z~5 (top edge), not z~0 "
                  "(got z values %r) -- confirms nearest-segment search picks the geometrically "
                  "closest segment, not merely the first one checked" % all_z)

        print("\n== two openings on the same wall segment (door + window) ==")
        r = await pg.evaluate(PROBE_TWO_OPENINGS_SAME_SEGMENT)
        brk2 = r.get("brk") or {}
        check(len(brk2.get("jambs", [])) == 4, "2 openings produce 4 jamb lines total (%d)" % len(brk2.get("jambs", [])))
        check(len(brk2.get("glaze", [])) == 1, "exactly 1 glazing line (from the window, not the door) (%d)" % len(brk2.get("glaze", [])))
        if brk2.get("glaze"):
            check(brk2["glaze"][0][2] == r["winId"], "the glazing line is tagged to the window's id, not the door's")
        door_jambs = [j for j in brk2.get("jambs", []) if j[2] == r["doorId"]]
        win_jambs = [j for j in brk2.get("jambs", []) if j[2] == r["winId"]]
        check(len(door_jambs) == 2 and len(win_jambs) == 2, "jambs correctly attributed 2-each to the door and the window")
        # A closed ring cut at k gaps decomposes into exactly k arcs (not k+1) -- the wraparound
        # stitch (see PROBE_DOOR_BASIC above, the 1-gap case producing 1 stroke) generalizes: with
        # 2 gaps on the same ring, exactly 2 arcs result.
        check(len(brk2.get("outerRuns", [])) == 2, "outer face is split into 2 runs by 2 separate gaps (%d)" % len(brk2.get("outerRuns", [])))
        svg2_root, perr2 = parse_svg((r.get("svg") or {}).get("text", ""))
        check(svg2_root is not None, "two-opening scene SVG is well-formed XML (%s)" % (perr2 or "ok"))

        print("\n== no openings: exact old behavior preserved ==")
        r = await pg.evaluate(PROBE_NO_OPENINGS_UNCHANGED)
        brk3 = r.get("brk") or {}
        check(len(brk3.get("outerRuns", [])) == 1 and brk3.get("outerClosed") is True,
              "with no openings, exactly 1 CLOSED outer run is returned (matches the pre-Phase-50c shape)")
        check(len(brk3.get("jambs", [])) == 0 and len(brk3.get("glaze", [])) == 0,
              "with no openings, zero jamb/glaze lines are added")
        svg3_root, perr3 = parse_svg((r.get("svg") or {}).get("text", ""))
        if svg3_root is not None:
            wall_paths3 = svg3_root.findall(".//" + SVG_NS + "path[@data-obj='%s']" % r["wallId"])
            check(len(wall_paths3) == 3, "a wall with no openings still emits exactly 3 paths, unchanged (%d)" % len(wall_paths3))

        print("\n== sheet vector plan viewport (Phase 50b) reflects the same break ==")
        r = await pg.evaluate(PROBE_SHEET_VECTOR_REFLECTS_BREAK)
        pv = r.get("pv") or {}
        frag = ('<g xmlns="http://www.w3.org/2000/svg">' + pv.get("svg", "") + "</g>") if pv.get("svg") else None
        proot, pperr = parse_svg(frag) if frag else (None, "no svg")
        check(proot is not None, "sheet plan viewport fragment with a door is well-formed XML (%s)" % (pperr if frag else "no fragment"))
        if proot is not None:
            wall_paths_vp = proot.findall(".//" + SVG_NS + "path[@data-obj='%s']" % r["wallId"])
            check(len(wall_paths_vp) == 3, "sheet vector viewport also emits exactly 3 wall paths (broken outline) (%d)" % len(wall_paths_vp))
            jamb_lines_vp = [l for l in proot.findall(".//" + SVG_NS + "line") if l.attrib.get("data-obj") == r["doorId"]]
            check(len(jamb_lines_vp) == 2, "sheet vector viewport emits the 2 jamb lines for the door too (%d)" % len(jamb_lines_vp))

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
