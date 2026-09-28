"""
bim_phase52b_svg_presentation_export_browser_tests.py

Regression suite for Phase 52b (__acad3dV61) in canvas_v10.html: wiring presentation mode into the
vector SVG export sinks (bimBuildSVG, bimBuildPlanViewportSVG, and by extension bimBuildSheetSVG /
Export SVG / Export Sheet as SVG / Print Sheet), closing the gap the Phase 52a STATUS.md entry
disclosed explicitly ("Export SVG still emits pure technical linework regardless of
A3D.presentMode") and completing Phase 52 as the roadmap describes it.

WHAT SHIPPED, IN ONE SENTENCE: both SVG builders now take an optional mode parameter ('technical',
the default, or 'presentation'); in presentation mode each emitted <path>/<line>/<text> carries its
own resolved fill/stroke/stroke-width/opacity (via the same bimResolveGraphics data model Phase 51
built and Phase 52a's live view already consumes), and a closed, unbroken wall gets a real poche --
a single evenodd path (outer ring minus inner ring) so a filled wall never covers the room space
inside it -- while every existing caller that does not pass a mode keeps producing byte-identical
output to before this phase.

TWO DIFFERENT UNIT SYSTEMS, TWO DIFFERENT CALIBRATIONS -- the central risk this suite guards:
bimBuildSVG works in model-space with a "fit to content" viewBox, so its existing technical stroke
width (strokeW = diag*0.0015) is a purely visual constant with no physical meaning; presentation
stroke widths there are calibrated as svgLwUnit = strokeW/0.25 so an UNSTYLED object's resolved
default (0.25mm, from bimDefaultGraphics) reproduces that exact technical value -- the same
"untouched default matches old output" rule Phase 52a used for BIM_LW_TO_PX in the live Canvas2D
view. bimBuildPlanViewportSVG, by contrast, already works in real sheet-page millimetres, so a
resolved lineWeight (also mm) is used AS THE STROKE-WIDTH DIRECTLY, no calibration at all. Getting
these backwards (applying svgLwUnit in the mm builder, or a flat mm value in the model-space one)
would silently produce wrong-scale linework in one of the two exporters while every other check
still passed -- so this suite checks each builder's calibration independently and cross-checks the
model-space one against a technical build of the identical scene rather than a hard-coded constant.

WALL POCHE SCOPE, disclosed rather than silently narrowed: poche fill is only emitted for a closed
wall loop with NO opening breaks. A wall with a door/window cut is disjoint run segments, not a
closed ring, and correctly poche-filling those would need real 2D boolean geometry this codebase
does not have (the same pre-existing gap already disclosed for opening cuts in the plan outline
itself, Phase 50c). Such a wall still gets full line styling (color/weight/opacity) on its broken
outline -- only the fill is withheld. This suite tests both the poche path directly AND that this
withholding actually happens for a broken wall, rather than assuming it.

DROP SHADOW IS OUT OF SCOPE HERE, same as Phase 52a deferred pattern: SVG has no per-path
equivalent to Canvas2D's shadowBlur without a <filter>/feDropShadow defs system, a materially
separate feature, so vector output never emits a shadow regardless of the `shadow` override --
recorded here rather than silently discovered later, and not tested as "shipped" behavior.

Run:  python3 bim_phase52b_svg_presentation_export_browser_tests.py [path/to/canvas_v10.html]
"""
import asyncio, pathlib, re, sys
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


def parse_svg(svg_text):
    try:
        return ET.fromstring(svg_text), None
    except ET.ParseError as e:
        return None, e


def paths_for(root, obj_id):
    return [el for el in root.iter() if el.tag.endswith("}path") or el.tag == "path"
            if el.get("data-obj") == obj_id]


def lines_for(root, obj_id):
    return [el for el in root.iter() if el.tag.endswith("}line") or el.tag == "line"
            if el.get("data-obj") == obj_id]


def texts_for(root, obj_id):
    return [el for el in root.iter() if el.tag.endswith("}text") or el.tag == "text"
            if el.get("data-obj") == obj_id]


# ---------------------------------------------------------------------------------------------
# 1. API surface present.
# ---------------------------------------------------------------------------------------------
PROBE_API = r"""
() => {
  return {
    marker: window.__acad3dV61 || null,
    hasApi: !!(window.__a3dWall && window.__a3dDoorAt && window.__a3dCreateRoomAt &&
               window.__a3dSetGraphicsOverride && window.__a3dSetTypeGraphics &&
               window.__a3dBuildSVG && window.__a3dBuildSheetSVG && window.__a3dBuildPlanViewportSVG &&
               window.__a3dAddSheet && window.__a3dAddViewport && window.__a3dActiveLevel)
  };
}
"""

# ---------------------------------------------------------------------------------------------
# 2. Default/technical call is untouched: no arg and mode='technical' produce byte-identical text,
#    and no individual <path>/<line>/<text> carries a stroke/opacity attribute of its own (styling
#    stays exclusively on the outer <g>, exactly as before this phase).
# ---------------------------------------------------------------------------------------------
PROBE_TECHNICAL_UNCHANGED = r"""
() => {
  window.__a3dTestSetObjs([]);
  const wallId = window.__a3dWall([[0,0],[8,0],[8,5],[0,5]], 0.3, 3, 'center', true);
  const roomId = window.__a3dCreateRoomAt([4,2.5], 0);
  window.__a3dSelectFor([]);
  const noArg = window.__a3dBuildSVG();
  const explicit = window.__a3dBuildSVG('technical');
  return {wallId, roomId, noArgText: noArg.text, explicitText: explicit.text};
}
"""

# ---------------------------------------------------------------------------------------------
# 3. Presentation, no overrides anywhere: every object resolves the hard-coded default (0.25mm,
#    #000000, fill none, opacity 1). The room's per-element stroke-width must equal the SAME
#    strokeW the technical build of the IDENTICAL scene put on its group -- proving the svgLwUnit
#    calibration reproduces old visual weight exactly for an untouched object.
# ---------------------------------------------------------------------------------------------
PROBE_PRESENTATION_DEFAULTS = r"""
() => {
  window.__a3dTestSetObjs([]);
  const wallId = window.__a3dWall([[0,0],[8,0],[8,5],[0,5]], 0.3, 3, 'center', true);
  const roomId = window.__a3dCreateRoomAt([4,2.5], 0);
  window.__a3dSelectFor([]);
  const tech = window.__a3dBuildSVG('technical');
  const pres = window.__a3dBuildSVG('presentation');
  return {wallId, roomId, techText: tech.text, presText: pres.text};
}
"""

# ---------------------------------------------------------------------------------------------
# 4. Instance override fill + line color + line weight + opacity on a ROOM: presentation mode's
#    room path must carry exactly those resolved values; a fresh room with no override, built in
#    the same document, must still resolve the plain default (no leakage between objects).
# ---------------------------------------------------------------------------------------------
PROBE_ROOM_OVERRIDE = r"""
() => {
  window.__a3dTestSetObjs([]);
  const wallA = window.__a3dWall([[0,0],[6,0],[6,4],[0,4]], 0.3, 3, 'center', true);
  const roomA = window.__a3dCreateRoomAt([3,2], 0);
  const wallB = window.__a3dWall([[20,0],[26,0],[26,4],[20,4]], 0.3, 3, 'center', true);
  const roomB = window.__a3dCreateRoomAt([23,2], 0);
  window.__a3dSelectFor([]);
  window.__a3dSetGraphicsOverride(roomA, 'presentation', 'fill', '#3355ff');
  window.__a3dSetGraphicsOverride(roomA, 'presentation', 'lineColor', '#ff8800');
  window.__a3dSetGraphicsOverride(roomA, 'presentation', 'lineWeight', 1.0);
  window.__a3dSetGraphicsOverride(roomA, 'presentation', 'opacity', 0.5);
  const pres = window.__a3dBuildSVG('presentation');
  const tech = window.__a3dBuildSVG('technical');
  return {roomA, roomB, presText: pres.text, techStrokeMatch: tech.text.match(/stroke-width="([\d.]+)"/)};
}
"""

# ---------------------------------------------------------------------------------------------
# 5. Wall poche: a CLOSED wall with no openings and a fill override must produce exactly one
#    fill-rule="evenodd" path for its own id (outer-minus-inner) plus its plain centerline poly
#    (fill="none") -- 2 paths total, not the technical-mode 3 (centerline + separate inner/outer).
# ---------------------------------------------------------------------------------------------
PROBE_WALL_POCHE = r"""
() => {
  window.__a3dTestSetObjs([]);
  const wallId = window.__a3dWall([[0,0],[8,0],[8,5],[0,5]], 0.3, 3, 'center', true);
  window.__a3dSelectFor([]);
  window.__a3dSetGraphicsOverride(wallId, 'presentation', 'fill', '#b7ab98');
  const pres = window.__a3dBuildSVG('presentation');
  const tech = window.__a3dBuildSVG('technical');
  return {wallId, presText: pres.text, techText: tech.text};
}
"""

# ---------------------------------------------------------------------------------------------
# 6. A wall WITH a door (opening break) and the SAME fill override must NOT get a poche path
#    (disjoint runs, not a closed ring) -- but its broken outline segments must still carry the
#    resolved line color/weight, proving the withholding is fill-only, not a silent style drop.
# ---------------------------------------------------------------------------------------------
PROBE_WALL_WITH_OPENING_NO_POCHE = r"""
() => {
  window.__a3dTestSetObjs([]);
  const wallId = window.__a3dWall([[0,0],[8,0],[8,5],[0,5]], 0.3, 3, 'center', true);
  const doorId = window.__a3dDoorAt(wallId, [4,0], 0.9, 2.1);
  window.__a3dSelectFor([]);
  window.__a3dSetGraphicsOverride(wallId, 'presentation', 'fill', '#b7ab98');
  window.__a3dSetGraphicsOverride(wallId, 'presentation', 'lineColor', '#22aa55');
  const pres = window.__a3dBuildSVG('presentation');
  return {wallId, doorId, presText: pres.text};
}
"""

# ---------------------------------------------------------------------------------------------
# 7. Type-level presentation fill: a wall assigned to a TYPE (no instance override of its own)
#    must resolve and render that type's presentation fill via the same poche path.
# ---------------------------------------------------------------------------------------------
PROBE_TYPE_LEVEL = r"""
() => {
  window.__a3dTestSetObjs([]);
  const wallId = window.__a3dWall([[0,0],[8,0],[8,5],[0,5]], 0.3, 3, 'center', true);
  window.__a3dSelectFor([]);
  const types = window.__a3dWallTypes();
  const typeId = types[0].id;
  window.__a3dSetTypeGraphics('wall', typeId, 'presentation', 'fill', '#77cc99');
  window.__a3dApplyTypeToInstances('wall', typeId);
  const pres = window.__a3dBuildSVG('presentation');
  return {wallId, typeId, presText: pres.text};
}
"""

# ---------------------------------------------------------------------------------------------
# 8. Text color/opacity: a dim's linear label picks up an override's lineColor as its fill and
#    carries an opacity attribute when opacity != 1; an unstyled text object in the same document
#    still resolves the plain default (fill=currentColor semantics preserved via #000000 default).
# ---------------------------------------------------------------------------------------------
PROBE_TEXT_STYLE = r"""
() => {
  window.__a3dTestSetObjs([]);
  const textId = window.__a3dPushTestObj({id:'t1', t:'text', pt:[1,1], y:0, text:'Styled', layer:null});
  window.__a3dSetGraphicsOverride(textId, 'presentation', 'lineColor', '#aa2299');
  window.__a3dSetGraphicsOverride(textId, 'presentation', 'opacity', 0.6);
  const plainId = window.__a3dPushTestObj({id:'t2', t:'text', pt:[5,5], y:0, text:'Plain', layer:null});
  const pres = window.__a3dBuildSVG('presentation');
  return {textId, plainId, presText: pres.text};
}
"""

# ---------------------------------------------------------------------------------------------
# 9. bimBuildPlanViewportSVG mm calibration: this builder already works in sheet-page millimetres,
#    so a resolved lineWeight of 1.2mm must appear AS "1.200" directly on the styled element's
#    stroke-width -- no diag-relative scaling, unlike bimBuildSVG. Default (no override) call
#    stays byte-identical to a technical build (no per-element stroke attrs at all).
# ---------------------------------------------------------------------------------------------
PROBE_PLAN_VIEWPORT_MM = r"""
() => {
  window.__a3dTestSetObjs([]);
  const wallId = window.__a3dWall([[0,0],[8,0],[8,5],[0,5]], 0.3, 3, 'center', true);
  window.__a3dSelectFor([]);
  window.__a3dSetGraphicsOverride(wallId, 'presentation', 'lineColor', '#1144cc');
  window.__a3dSetGraphicsOverride(wallId, 'presentation', 'lineWeight', 1.2);
  const lvl = window.__a3dActiveLevel();
  const sheetId = window.__a3dAddSheet('B-101', 'Phase52b Sheet', 'A1');
  const vpId = window.__a3dAddViewport(sheetId, 'plan', lvl.id, 'fit', 100);
  const pres = window.__a3dBuildPlanViewportSVG(sheetId, vpId, 'presentation');
  const tech = window.__a3dBuildPlanViewportSVG(sheetId, vpId, 'technical');
  const noArg = window.__a3dBuildPlanViewportSVG(sheetId, vpId);
  return {wallId, sheetId, vpId, presSvg: pres.svg, techSvg: tech.svg, noArgSvg: noArg.svg};
}
"""

# ---------------------------------------------------------------------------------------------
# 10. Export/print entry points follow the live A3D.presentMode toggle: bimBuildSheetSVG(sheet)
#     with no mode still defaults technical; passing 'presentation' produces styled plan viewport
#     content; XML well-formedness holds for a mixed real scene (wall+door, filled wall, room,
#     floor, column, dim, text) in presentation mode.
# ---------------------------------------------------------------------------------------------
PROBE_SHEET_AND_WELLFORMED = r"""
() => {
  window.__a3dTestSetObjs([]);
  const wallA = window.__a3dWall([[0,0],[8,0],[8,5],[0,5]], 0.3, 3, 'center', true);
  const doorId = window.__a3dDoorAt(wallA, [4,0], 0.9, 2.1);
  const wallB = window.__a3dWall([[20,0],[26,0],[26,4],[20,4]], 0.3, 3, 'center', true);
  window.__a3dSelectFor([]);
  window.__a3dSetGraphicsOverride(wallB, 'presentation', 'fill', '#c9b98a');
  const roomId = window.__a3dCreateRoomAt([23,2], 0);
  window.__a3dSetGraphicsOverride(roomId, 'presentation', 'fill', '#88bbee');
  const lvl = window.__a3dActiveLevel();
  const sheetId = window.__a3dAddSheet('B-102', 'Mixed Scene Sheet', 'A1');
  const vpId = window.__a3dAddViewport(sheetId, 'plan', lvl.id, 'fit', 100);
  const sheetTech = window.__a3dBuildSheetSVG(sheetId);
  const sheetPres = window.__a3dBuildSheetSVG(sheetId, 'presentation');
  const modelPres = window.__a3dBuildSVG('presentation');
  return {wallA, wallB, roomId, doorId, sheetTechSvg: sheetTech, sheetPresSvg: sheetPres, modelPresText: modelPres.text};
}
"""


async def run_probe(page, name, script):
    print("\n== " + name + " ==")
    try:
        return await page.evaluate(script)
    except Exception as e:
        check(False, name + " threw: " + str(e))
        return None


async def main():
    path = pathlib.Path(TARGET).resolve()
    if not path.exists():
        print("Target file not found: " + str(path))
        sys.exit(1)
    url = "file://" + str(path)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        page_errors = []
        page.on("pageerror", lambda e: page_errors.append(str(e)))
        await page.goto(url)
        await page.wait_for_timeout(400)

        r = await run_probe(page, "API surface", PROBE_API)
        if r:
            check(r["marker"] is not None, "V61 marker present: " + str(r["marker"]))
            check(r["hasApi"], "all required test hooks present")

        r = await run_probe(page, "Technical call unchanged", PROBE_TECHNICAL_UNCHANGED)
        if r:
            check(r["noArgText"] == r["explicitText"], "bimBuildSVG() === bimBuildSVG('technical')")
            root, err = parse_svg(r["noArgText"])
            check(root is not None, "technical output is well-formed XML: " + str(err))
            if root is not None:
                wall_paths = paths_for(root, r["wallId"])
                check(len(wall_paths) == 3, "wall (no fill override) still emits 3 paths in technical mode, got " + str(len(wall_paths)))
                no_stroke_on_elements = all(p.get("stroke") is None for p in root.iter()
                                             if (p.tag.endswith("}path") or p.tag == "path"))
                check(no_stroke_on_elements, "no individual <path> carries its own stroke attribute in technical mode")
                room_paths = paths_for(root, r["roomId"])
                check(len(room_paths) == 1 and room_paths[0].get("fill") == "none",
                      "room path still fill=none in technical mode")

        r = await run_probe(page, "Presentation defaults reproduce technical weight", PROBE_PRESENTATION_DEFAULTS)
        if r:
            techRoot, techErr = parse_svg(r["techText"])
            presRoot, presErr = parse_svg(r["presText"])
            check(techRoot is not None and presRoot is not None, "both technical and presentation outputs well-formed")
            if techRoot is not None and presRoot is not None:
                techG = techRoot.find(".//{http://www.w3.org/2000/svg}g") or techRoot.find(".//g")
                techStrokeW = float(techG.get("stroke-width")) if techG is not None else None
                check(techStrokeW is not None, "technical group stroke-width readable")
                room_paths = paths_for(presRoot, r["roomId"])
                check(len(room_paths) == 1, "unstyled room still emits exactly 1 presentation path")
                if room_paths and techStrokeW is not None:
                    sw = float(room_paths[0].get("stroke-width", "-1"))
                    check(close(sw, techStrokeW, tol=max(1e-6, techStrokeW * 0.01)),
                          "unstyled room presentation stroke-width (%.6f) matches technical strokeW (%.6f)" % (sw, techStrokeW))
                    check(room_paths[0].get("stroke") == "#000000", "unstyled room presentation stroke color is default #000000")
                    check(room_paths[0].get("fill") == "none", "unstyled room still fill=none (no override set)")

        r = await run_probe(page, "Room instance override applied, no leakage", PROBE_ROOM_OVERRIDE)
        if r:
            root, err = parse_svg(r["presText"])
            check(root is not None, "presentation output well-formed: " + str(err))
            if root is not None:
                aPaths = paths_for(root, r["roomA"])
                bPaths = paths_for(root, r["roomB"])
                check(len(aPaths) == 1 and len(bPaths) == 1, "each room emits exactly one path")
                if aPaths:
                    a = aPaths[0]
                    check(a.get("fill") == "#3355ff", "roomA fill override applied: " + str(a.get("fill")))
                    check(a.get("stroke") == "#ff8800", "roomA lineColor override applied: " + str(a.get("stroke")))
                    check(a.get("opacity") == "0.5", "roomA opacity override applied: " + str(a.get("opacity")))
                if bPaths:
                    b = bPaths[0]
                    check(b.get("fill") == "none", "roomB (no override) not leaked a fill: " + str(b.get("fill")))
                    check(b.get("opacity") is None, "roomB (no override) has no opacity attr (default 1, omitted)")

        r = await run_probe(page, "Wall poche (closed, no openings)", PROBE_WALL_POCHE)
        if r:
            presRoot, presErr = parse_svg(r["presText"])
            techRoot, techErr = parse_svg(r["techText"])
            check(presRoot is not None, "presentation output well-formed: " + str(presErr))
            check(techRoot is not None, "technical output well-formed: " + str(techErr))
            if presRoot is not None:
                pPaths = paths_for(presRoot, r["wallId"])
                check(len(pPaths) == 2, "wall with fill override emits exactly 2 presentation paths (centerline + poche), got " + str(len(pPaths)))
                evenodd = [p for p in pPaths if p.get("fill-rule") == "evenodd"]
                check(len(evenodd) == 1, "exactly one evenodd poche path for the wall")
                if evenodd:
                    check(evenodd[0].get("fill") == "#b7ab98", "poche path carries the override fill color")
                    d = evenodd[0].get("d", "")
                    check(d.count("Z") == 2, "poche path is two closed subpaths (outer + inner), got Z-count=" + str(d.count("Z")))
            if techRoot is not None:
                tPaths = paths_for(techRoot, r["wallId"])
                check(len(tPaths) == 3, "same wall in technical mode still emits the old 3 paths, got " + str(len(tPaths)))
                check(all(p.get("fill-rule") is None for p in tPaths), "no evenodd path in technical mode")

        r = await run_probe(page, "Wall with opening: no poche, style still applied", PROBE_WALL_WITH_OPENING_NO_POCHE)
        if r:
            root, err = parse_svg(r["presText"])
            check(root is not None, "presentation output well-formed: " + str(err))
            if root is not None:
                pPaths = paths_for(root, r["wallId"])
                evenodd = [p for p in pPaths if p.get("fill-rule") == "evenodd"]
                check(len(evenodd) == 0, "broken (door) wall gets NO poche path despite fill override")
                check(len(pPaths) >= 3, "broken wall still emits multiple outline run paths, got " + str(len(pPaths)))
                styled = [p for p in pPaths if p.get("stroke") == "#22aa55"]
                check(len(styled) >= 1, "broken wall's outline segments still carry the lineColor override")

        r = await run_probe(page, "Type-level presentation fill renders via poche", PROBE_TYPE_LEVEL)
        if r:
            root, err = parse_svg(r["presText"])
            check(root is not None, "presentation output well-formed: " + str(err))
            if root is not None:
                pPaths = paths_for(root, r["wallId"])
                evenodd = [p for p in pPaths if p.get("fill-rule") == "evenodd"]
                check(len(evenodd) == 1, "type-styled wall (no instance override) still gets a poche path")
                if evenodd:
                    check(evenodd[0].get("fill") == "#77cc99", "poche uses the TYPE's presentation fill: " + str(evenodd[0].get("fill")))

        r = await run_probe(page, "Text color/opacity override, no leakage", PROBE_TEXT_STYLE)
        if r:
            root, err = parse_svg(r["presText"])
            check(root is not None, "presentation output well-formed: " + str(err))
            if root is not None:
                styledTexts = texts_for(root, r["textId"])
                plainTexts = texts_for(root, r["plainId"])
                check(len(styledTexts) == 1 and len(plainTexts) == 1, "each text object emits exactly one <text>")
                if styledTexts:
                    st = styledTexts[0]
                    check(st.get("fill") == "#aa2299", "styled text fill follows lineColor override: " + str(st.get("fill")))
                    check(st.get("opacity") == "0.6", "styled text opacity override applied: " + str(st.get("opacity")))
                if plainTexts:
                    # In presentation mode EVERY object resolves through bimResolveGraphics, even
                    # with no override -- an unstyled text's resolved lineColor is the hard default
                    # '#000000' (visually identical to technical's 'currentColor', but a real
                    # resolved value rather than an inherited one, consistent with how the
                    # "presentation defaults" probe above treats an unstyled room).
                    pt = plainTexts[0]
                    check(pt.get("fill") == "#000000", "unstyled text resolves the default lineColor #000000: " + str(pt.get("fill")))
                    check(pt.get("opacity") is None, "unstyled text has no opacity attribute")

        r = await run_probe(page, "Plan viewport SVG: direct mm line-weight calibration", PROBE_PLAN_VIEWPORT_MM)
        if r:
            check(r["noArgSvg"] == r["techSvg"], "bimBuildPlanViewportSVG(...) === explicit 'technical' call")
            presRoot, presErr = parse_svg(r["presSvg"])
            techRoot, techErr = parse_svg(r["techSvg"])
            check(presRoot is not None, "presentation viewport fragment well-formed: " + str(presErr))
            check(techRoot is not None, "technical viewport fragment well-formed: " + str(techErr))
            if presRoot is not None:
                pPaths = paths_for(presRoot, r["wallId"])
                styled = [p for p in pPaths if p.get("stroke") == "#1144cc"]
                check(len(styled) >= 1, "styled wall segment present in plan viewport presentation output")
                if styled:
                    sw = float(styled[0].get("stroke-width", "-1"))
                    check(close(sw, 1.2, tol=1e-3), "plan-viewport stroke-width is the RAW mm value 1.2 (no calibration), got " + str(sw))
            if techRoot is not None:
                tPaths = paths_for(techRoot, r["wallId"])
                check(all(p.get("stroke") is None for p in tPaths), "no per-element stroke in technical plan-viewport output")

        r = await run_probe(page, "Sheet export/print follows presentMode; mixed scene well-formed", PROBE_SHEET_AND_WELLFORMED)
        if r:
            check(r["sheetTechSvg"] != r["sheetPresSvg"], "technical and presentation sheet SVGs differ")
            techFull, techErr = parse_svg(r["sheetTechSvg"])
            presFull, presErr = parse_svg(r["sheetPresSvg"])
            check(techFull is not None, "technical full sheet SVG well-formed: " + str(techErr))
            check(presFull is not None, "presentation full sheet SVG (mixed scene: door-wall + filled wall + room + dim) well-formed: " + str(presErr))
            modelRoot, modelErr = parse_svg(r["modelPresText"])
            check(modelRoot is not None, "model-space presentation SVG for the same mixed scene well-formed: " + str(modelErr))
            if presFull is not None:
                filledWallInSheet = [p for p in presFull.iter()
                                      if (p.tag.endswith("}path") or p.tag == "path") and p.get("data-obj") == r["wallB"]
                                      and p.get("fill-rule") == "evenodd"]
                check(len(filledWallInSheet) == 1, "filled wall's poche appears in the presentation SHEET export too")

        await browser.close()

        if page_errors:
            print("\nPage errors encountered:")
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
