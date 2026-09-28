"""
bim_phase53_pattern_library_browser_tests.py

Regression suite for Phase 53 (__acad3dV63) in canvas_v10.html: the procedural pattern/hatch
library, and the wiring that finally makes the `pattern` graphics field DO something. Phase 51
stored the field, Phase 52a/52b consumed every other field in the live view and in vector export
and explicitly deferred this one; this phase closes it in both sinks at once.

WHAT SHIPPED, IN ONE SENTENCE: a table of procedural tile definitions (BIM_PATTERN_DEFS) expressed
once in normalised tile coordinates plus a physical tile size in millimetres, rendered by a
Canvas2D sink (an offscreen tile handed to createPattern) and by an SVG sink (a <pattern> element
in <defs>, referenced by a second path drawn over the object's own fill), with two new graphics
keys -- patternColor and patternScale -- carried on the existing Phase 51 type/instance override
system.

THE CALIBRATION TRAP THIS SUITE GUARDS, inherited from Phase 52b and now applying to a second
quantity: the two SVG writers work in different units. bimBuildSVG is model-space with a
fit-to-content viewBox, so it converts millimetres through svgLwUnit (the same constant that turns
a 0.25 mm line weight into that drawing's stroke width). bimBuildPlanViewportSVG is already in real
sheet-page millimetres, so a millimetre IS a user unit and no conversion applies at all. Getting
these backwards would print hatch at the wrong density in one exporter while every structural
check still passed, so each writer's tile size is asserted independently: the model-space one is
derived from a technical build of the identical scene rather than a hard-coded constant, and the
plan-viewport one is asserted as the raw millimetre figure.

WHAT IS DELIBERATELY NOT CLAIMED, recorded here rather than left to be discovered:
  - The Canvas2D hatch is applied in SCREEN space. In a plan or elevation view -- an orthographic,
    uniformly scaled projection, which is what presentation mode exists for -- that reads exactly
    as a drafted hatch should. In a perspective 3D view it is screen-aligned rather than
    surface-aligned, i.e. it does not foreshorten with the face. Surface alignment needs per-face
    UV projection and is a different feature.
  - Drop shadow still never reaches vector output (a Phase 52b scope boundary, unchanged here).
  - Patterns are procedural only. User-imported image textures, the other half of the roadmap's
    Phase 53 description, are not in this delivery and are not tested as if they were.

Run:  python3 bim_phase53_pattern_library_browser_tests.py [path/to/canvas_v10.html]
"""
import asyncio, pathlib, sys
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


def close(a, b, tol=1e-4):
    return a is not None and b is not None and abs(a - b) <= tol


def parse_svg(text):
    try:
        return ET.fromstring(text), None
    except ET.ParseError as e:
        return None, e


def tag_is(el, name):
    return el.tag == name or el.tag.endswith("}" + name)


def find_all(root, name):
    return [el for el in root.iter() if tag_is(el, name)]


def paths_for(root, obj_id):
    return [el for el in find_all(root, "path") if el.get("data-obj") == obj_id]


PROBE_API = r"""
() => ({
  v63: window.__acad3dV63 || null,
  hasApi: !!(window.__a3dPatternDefs && window.__a3dPatternNames && window.__a3dPatternDraws &&
             window.__a3dPatternLabel && window.__a3dPatternTileSize && window.__a3dPatternSvgDef &&
             window.__a3dLwToPx && window.__a3dSetGraphicsOverride && window.__a3dResolveGraphics &&
             window.__a3dBuildSVG && window.__a3dBuildPlanViewportSVG && window.__a3dLastDrawStyle &&
             window.__a3dLastRoomStyle && window.__a3dTestForceCpu)
})
"""

# ---------------------------------------------------------------------------------------------
# The definition table itself. A tile whose geometry strays outside the unit square would bleed
# across the seam and tile visibly wrong, so that invariant is checked for every entry rather than
# spot-checked on the one pattern a screenshot happened to show.
# ---------------------------------------------------------------------------------------------
PROBE_TABLE = r"""
() => ({
  names: window.__a3dPatternNames(),
  defs: window.__a3dPatternDefs(),
  draws: window.__a3dPatternNames().map(n => [n, window.__a3dPatternDraws(n)]),
  labels: window.__a3dPatternNames().map(n => [n, window.__a3dPatternLabel(n)]),
  unknownDraws: window.__a3dPatternDraws('no-such-pattern'),
  unknownLabel: window.__a3dPatternLabel('no-such-pattern'),
  lwToPx: window.__a3dLwToPx(),
  tiles: {
    diagonal1: window.__a3dPatternTileSize('diagonal', 1),
    diagonal2: window.__a3dPatternTileSize('diagonal', 2),
    brick1: window.__a3dPatternTileSize('brick', 1),
    none: window.__a3dPatternTileSize('none', 1),
    solid: window.__a3dPatternTileSize('solid', 1)
  }
})
"""

# ---------------------------------------------------------------------------------------------
# The default resolution is what protects every project that predates this phase: an untouched
# object must still resolve pattern 'none', and its exports must be free of pattern machinery.
# ---------------------------------------------------------------------------------------------
PROBE_DEFAULTS = r"""
() => {
  window.__a3dEnter(); window.__a3dTestSetObjs([]);
  const w=window.__a3dWall([[0,0],[8,0],[8,5],[0,5]],0.3,3,'center',true);
  const room=window.__a3dCreateRoomAt([4,2.5],0);
  window.__a3dSelectFor([]);
  return {
    wallId:w, roomId:room,
    resolved: window.__a3dResolveGraphics(w,'presentation'),
    tech: window.__a3dBuildSVG('technical').text,
    presNoPattern: window.__a3dBuildSVG('presentation').text
  };
}
"""

# ---------------------------------------------------------------------------------------------
# Model-space SVG. The expected tile size is derived from the SAME scene's technical build:
# strokeW is the technical group's stroke-width, svgLwUnit is strokeW/0.25 by construction, so
# tile width must be def.mm * def.w * svgLwUnit * scale. No constant is hard-coded here.
# ---------------------------------------------------------------------------------------------
PROBE_MODEL_SVG = r"""
() => {
  window.__a3dEnter(); window.__a3dTestSetObjs([]);
  const w=window.__a3dWall([[0,0],[8,0],[8,5],[0,5]],0.3,3,'center',true);
  window.__a3dSelectFor([]);
  window.__a3dSetGraphicsOverride(w,'presentation','fill','#c9b98a');
  window.__a3dSetGraphicsOverride(w,'presentation','pattern','concrete');
  window.__a3dSetGraphicsOverride(w,'presentation','patternColor','#884422');
  window.__a3dSetGraphicsOverride(w,'presentation','patternScale',1.5);
  return {
    wallId:w,
    defs: window.__a3dPatternDefs(),
    pres: window.__a3dBuildSVG('presentation').text,
    tech: window.__a3dBuildSVG('technical').text
  };
}
"""

# ---------------------------------------------------------------------------------------------
# Interning: same appearance on two walls must define ONE <pattern>; a differing scale must define
# a second. A registry that failed either way would still render correctly, so neither direction
# is observable without asserting the count.
# ---------------------------------------------------------------------------------------------
PROBE_INTERNING = r"""
() => {
  window.__a3dEnter(); window.__a3dTestSetObjs([]);
  const a=window.__a3dWall([[0,0],[6,0],[6,4],[0,4]],0.3,3,'center',true);
  const b=window.__a3dWall([[20,0],[26,0],[26,4],[20,4]],0.3,3,'center',true);
  const c=window.__a3dWall([[40,0],[46,0],[46,4],[40,4]],0.3,3,'center',true);
  window.__a3dSelectFor([]);
  [a,b,c].forEach(id=>{
    window.__a3dSetGraphicsOverride(id,'presentation','fill','#dddddd');
    window.__a3dSetGraphicsOverride(id,'presentation','pattern','diagonal');
    window.__a3dSetGraphicsOverride(id,'presentation','patternColor','#334455');
  });
  const same = window.__a3dBuildSVG('presentation').text;
  window.__a3dSetGraphicsOverride(c,'presentation','patternScale',3);
  const differing = window.__a3dBuildSVG('presentation').text;
  return {a:a,b:b,c:c,same:same,differing:differing};
}
"""

# ---------------------------------------------------------------------------------------------
# Sheet-page SVG: raw millimetres, no calibration. Also confirms a technical viewport is free of
# any pattern machinery, and that ids are unique across the several fragments a sheet concatenates.
# ---------------------------------------------------------------------------------------------
PROBE_SHEET_SVG = r"""
() => {
  window.__a3dEnter(); window.__a3dTestSetObjs([]);
  const w=window.__a3dWall([[0,0],[8,0],[8,5],[0,5]],0.3,3,'center',true);
  window.__a3dSelectFor([]);
  window.__a3dSetGraphicsOverride(w,'presentation','fill','#c9b98a');
  window.__a3dSetGraphicsOverride(w,'presentation','pattern','brick');
  window.__a3dSetGraphicsOverride(w,'presentation','patternColor','#7a5c3a');
  window.__a3dSetGraphicsOverride(w,'presentation','patternScale',2);
  const lvl=window.__a3dActiveLevel();
  const sheet=window.__a3dAddSheet('A-301','Hatch Sheet','A1');
  const vp1=window.__a3dAddViewport(sheet,'plan',lvl.id,'fit',100);
  const vp2=window.__a3dAddViewport(sheet,'plan',lvl.id,'fit',50);
  return {
    wallId:w, defs: window.__a3dPatternDefs(),
    vpPres: window.__a3dBuildPlanViewportSVG(sheet,vp1,'presentation').svg,
    vpTech: window.__a3dBuildPlanViewportSVG(sheet,vp1,'technical').svg,
    vpNoArg: window.__a3dBuildPlanViewportSVG(sheet,vp1).svg,
    sheetPres: window.__a3dBuildSheetSVG(sheet,'presentation'),
    sheetTech: window.__a3dBuildSheetSVG(sheet)
  };
}
"""

# ---------------------------------------------------------------------------------------------
# Live Canvas2D. The GPU path is forced off because it skips the CPU face loop entirely and leaves
# A3D.lastPolys holding the previous frame's decisions -- reading a stale record would make this
# probe assert nothing.
# ---------------------------------------------------------------------------------------------
PROBE_CANVAS = r"""
() => {
  window.__a3dEnter(); window.__a3dTestForceCpu(true); window.__a3dTestSetObjs([]);
  const w=window.__a3dWall([[0,0],[8,0],[8,5],[0,5]],0.3,3,'center',true);
  const room=window.__a3dCreateRoomAt([4,2.5],0);
  window.__a3dSelectFor([]);
  window.__a3dSetGraphicsOverride(w,'presentation','fill','#c9b98a');
  window.__a3dSetGraphicsOverride(w,'presentation','pattern','concrete');
  window.__a3dSetGraphicsOverride(w,'presentation','patternColor','#884422');
  window.__a3dSetGraphicsOverride(w,'presentation','patternScale',1.5);
  window.__a3dSetGraphicsOverride(room,'presentation','fill','#dce9f5');
  window.__a3dSetGraphicsOverride(room,'presentation','pattern','diagonal');
  window.__a3dSetPresentMode(true); window.__a3dTestPaint();
  const presWall=window.__a3dLastDrawStyle(w), presRoom=window.__a3dLastRoomStyle(room);
  window.__a3dSetPresentMode(false); window.__a3dTestPaint();
  const techRoom=window.__a3dLastRoomStyle(room);
  window.__a3dTestForceCpu(false);
  return {wallId:w, roomId:room, presWall:presWall, presRoom:presRoom, techRoom:techRoom};
}
"""

# ---------------------------------------------------------------------------------------------
# Validation and inheritance. Every rejection here must FALL BACK to the type value rather than to
# the hard default, which is what distinguishes a working override sanitiser from one that simply
# discards the whole dict on a bad key.
# ---------------------------------------------------------------------------------------------
PROBE_VALIDATION = r"""
() => {
  window.__a3dEnter(); window.__a3dTestSetObjs([]);
  const w=window.__a3dWall([[0,0],[8,0],[8,5],[0,5]],0.3,3,'center',true);
  window.__a3dSelectFor([]);
  const types=window.__a3dWallTypes();
  window.__a3dSetTypeGraphics('wall',types[0].id,'presentation','pattern','concrete');
  window.__a3dSetTypeGraphics('wall',types[0].id,'presentation','patternColor','#224466');
  const fromType=window.__a3dResolveGraphics(w,'presentation');
  window.__a3dSetGraphicsOverride(w,'presentation','pattern','brick');
  window.__a3dSetGraphicsOverride(w,'presentation','patternColor','#aa3311');
  window.__a3dSetGraphicsOverride(w,'presentation','patternScale',2.5);
  const overridden=window.__a3dResolveGraphics(w,'presentation');
  const envelope=window.__a3dProjectEnvelope();
  window.__a3dUndo(); window.__a3dRedo();
  const afterUndoRedo=window.__a3dResolveGraphics(w,'presentation');
  window.__a3dSetGraphicsOverride(w,'presentation','patternScale',999);
  const clampedHigh=window.__a3dResolveGraphics(w,'presentation').patternScale;
  window.__a3dSetGraphicsOverride(w,'presentation','patternScale',0.0001);
  const clampedLow=window.__a3dResolveGraphics(w,'presentation').patternScale;
  window.__a3dSetGraphicsOverride(w,'presentation','patternColor','not-a-colour');
  const badColour=window.__a3dResolveGraphics(w,'presentation').patternColor;
  window.__a3dSetGraphicsOverride(w,'presentation','pattern','no-such-pattern');
  const badPattern=window.__a3dResolveGraphics(w,'presentation').pattern;
  window.__a3dClearGraphicsOverride(w,'presentation');
  const cleared=window.__a3dResolveGraphics(w,'presentation');
  return {fromType, overridden, afterUndoRedo, clampedHigh, clampedLow, badColour, badPattern,
          cleared, envHasPatternColor: envelope.indexOf('patternColor')>=0};
}
"""

# ---------------------------------------------------------------------------------------------
# Room fills belong UNDER the model. Invisible while a room's fill was a 14%-alpha wash; once
# Phase 52a allowed an opaque fill and this phase allowed a hatch, a room drawn last painted over
# every column and wall inside it. The label is the exception -- it stays on top.
# ---------------------------------------------------------------------------------------------
PROBE_ROOM_ORDER = r"""
() => {
  window.__a3dEnter(); window.__a3dTestSetObjs([]);
  const w=window.__a3dWall([[0,0],[10,0],[10,7],[0,7]],0.3,3,'center',true);
  const col=window.__a3dColumnAt([5,3.5],0,0.5,0.5,3);
  const room=window.__a3dCreateRoomAt([2,2],0);
  window.__a3dSelectFor([]);
  window.__a3dSetGraphicsOverride(room,'presentation','fill','#eef4fa');
  window.__a3dSetGraphicsOverride(room,'presentation','pattern','diagonal');
  return {wallId:w, colId:col, roomId:room,
          pres: window.__a3dBuildSVG('presentation').text,
          tech: window.__a3dBuildSVG('technical').text};
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

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        page_errors = []
        page.on("pageerror", lambda e: page_errors.append(str(e)))
        await page.goto("file://" + str(path))
        await page.wait_for_timeout(400)

        r = await run_probe(page, "API surface", PROBE_API)
        if r:
            check(r["v63"] is not None, "V63 marker present: " + str(r["v63"]))
            check(r["hasApi"], "all required test hooks present")

        r = await run_probe(page, "Pattern definition table", PROBE_TABLE)
        if r:
            names, defs = r["names"], r["defs"]
            check("none" in names and "solid" in names,
                  "'none' and 'solid' are still offered (they carry no tile geometry)")
            check(len(names) >= 8, "the library offers a real set, got " + str(len(names)))
            geometric = [n for n in names if n not in ("none", "solid")]
            check(all(n in defs for n in geometric),
                  "every non-special pattern name has a definition")
            check(all(n in names for n in defs),
                  "every definition is reachable from the name list (no orphan entries)")
            bad_bounds = []
            for n, d in defs.items():
                for ln in d.get("lines") or []:
                    if any(v < -1e-9 or v > 1 + 1e-9 for v in ln):
                        bad_bounds.append(n + " line " + str(ln))
                for dot in d.get("dots") or []:
                    if any(v < -1e-9 or v > 1 + 1e-9 for v in dot[:2]) or not (0 < dot[2] <= 0.5):
                        bad_bounds.append(n + " dot " + str(dot))
                if not (d.get("mm", 0) > 0):
                    bad_bounds.append(n + " has no positive physical tile size")
                if not (d.get("w", 1) >= 1):
                    bad_bounds.append(n + " has a bad width multiple")
            check(not bad_bounds,
                  "every tile primitive lies inside its unit tile, so patterns tile seamlessly"
                  + ((" -- offenders: " + "; ".join(bad_bounds)) if bad_bounds else ""))
            draws = dict(r["draws"])
            check(draws.get("none") is False, "'none' does not draw")
            check(draws.get("solid") is True, "'solid' draws (a flood of patternColor)")
            check(all(draws.get(n) for n in geometric), "every geometric pattern reports drawable")
            check(r["unknownDraws"] is False, "an unknown pattern name does not draw")
            check(r["unknownLabel"] == "no-such-pattern",
                  "an unknown name falls back to itself as a label rather than throwing")
            labels = dict(r["labels"])
            check(labels.get("none") == "None" and labels.get("solid") == "Solid fill",
                  "the special entries get human labels")
            check(all(labels.get(n) and labels.get(n) != n for n in geometric),
                  "every geometric pattern has a human-readable label distinct from its id")
            t = r["tiles"]
            lw = r["lwToPx"]
            d_diag = defs["diagonal"]
            check(close(t["diagonal1"]["w"], round(d_diag["mm"] * lw), 0.51)
                  and t["diagonal1"]["w"] == t["diagonal1"]["h"],
                  "a square pattern's canvas tile is mm * px-per-mm, and square: "
                  + str(t["diagonal1"]))
            check(t["diagonal2"]["w"] >= t["diagonal1"]["w"] * 1.9,
                  "doubling patternScale roughly doubles the canvas tile: "
                  + str(t["diagonal1"]["w"]) + " -> " + str(t["diagonal2"]["w"]))
            check(t["brick1"]["w"] == 2 * t["brick1"]["h"],
                  "the running-bond tile is exactly 2:1, got " + str(t["brick1"]))
            check(t["none"] is None and t["solid"] is None,
                  "'none' and 'solid' have no tile size (neither needs a tile)")

        r = await run_probe(page, "Untouched objects are unchanged by this phase", PROBE_DEFAULTS)
        if r:
            res = r["resolved"]
            check(res["pattern"] == "none", "an untouched object still resolves pattern 'none'")
            check(res.get("patternColor") and res.get("patternScale") == 1,
                  "the new keys resolve to their defaults: " + str(res.get("patternColor"))
                  + " / " + str(res.get("patternScale")))
            for label, text in (("technical", r["tech"]), ("presentation", r["presNoPattern"])):
                check("<defs>" not in text,
                      "a project with no hatch emits no <defs> in " + label + " mode")
                check("data-pattern" not in text,
                      "a project with no hatch emits no pattern overlay in " + label + " mode")
                root, err = parse_svg(text)
                check(root is not None, label + " output is well-formed XML: " + str(err))

        r = await run_probe(page, "Model-space SVG: pattern def, overlay and calibration",
                            PROBE_MODEL_SVG)
        if r:
            pres_root, pres_err = parse_svg(r["pres"])
            tech_root, tech_err = parse_svg(r["tech"])
            check(pres_root is not None, "presentation output well-formed: " + str(pres_err))
            check(tech_root is not None, "technical output well-formed: " + str(tech_err))
            check("<defs>" not in r["tech"], "technical mode still emits no <defs>")
            if pres_root is not None and tech_root is not None:
                pats = find_all(pres_root, "pattern")
                check(len(pats) == 1, "exactly one <pattern> defined, got " + str(len(pats)))
                # svgLwUnit is strokeW/0.25 by construction; strokeW is the technical group's own
                # stroke-width, read back from a technical build of this identical scene.
                tech_g = find_all(tech_root, "g")
                strokeW = None
                for g in tech_g:
                    if g.get("stroke-width"):
                        strokeW = float(g.get("stroke-width"))
                        break
                check(strokeW is not None, "technical group stroke-width readable")
                if pats and strokeW:
                    d = r["defs"]["concrete"]
                    svg_lw_unit = strokeW / 0.25
                    expected = d["mm"] * d.get("w", 1) * svg_lw_unit * 1.5
                    got = float(pats[0].get("width"))
                    check(close(got, expected, max(1e-6, expected * 0.001)),
                          "model-space tile width is mm * svgLwUnit * scale (%.6f expected, %.6f got)"
                          % (expected, got))
                    check(close(float(pats[0].get("height")), expected, max(1e-6, expected * 0.001)),
                          "the concrete tile is square in model space too")
                    kids = list(pats[0])
                    check(len(kids) == len(d["lines"]) + len(d["dots"]),
                          "the <pattern> carries exactly the table's primitives, got " + str(len(kids)))
                    check(all(k.get("stroke") == "#884422" for k in kids if tag_is(k, "line")),
                          "tile lines use the resolved patternColor")
                    check(all(k.get("fill") == "#884422" for k in kids if tag_is(k, "circle")),
                          "tile dots use the resolved patternColor")
                wall_paths = paths_for(pres_root, r["wallId"])
                base = [q for q in wall_paths if q.get("fill") == "#c9b98a"]
                ovl = [q for q in wall_paths if q.get("data-pattern")]
                check(len(base) == 1,
                      "the wall's own poche fill survives underneath the hatch, got " + str(len(base)))
                check(len(ovl) == 1, "exactly one hatch overlay path, got " + str(len(ovl)))
                if ovl:
                    check(ovl[0].get("data-pattern") == "concrete",
                          "the overlay records which pattern it is")
                    check(ovl[0].get("fill", "").startswith("url(#"),
                          "the overlay references the <pattern>: " + str(ovl[0].get("fill")))
                    check(ovl[0].get("stroke") == "none",
                          "the overlay draws no outline of its own (the base path already did)")
                    check(ovl[0].get("fill-rule") == "evenodd",
                          "the poche overlay honours outer-minus-inner, so the hatch does not "
                          "flood the room inside the wall")
                if base and ovl:
                    check(base[0].get("d") == ovl[0].get("d"),
                          "the overlay uses the identical geometry as the fill it sits on")

        r = await run_probe(page, "Pattern interning", PROBE_INTERNING)
        if r:
            same_root, _ = parse_svg(r["same"])
            diff_root, _ = parse_svg(r["differing"])
            check(same_root is not None and diff_root is not None, "both outputs well-formed")
            if same_root is not None and diff_root is not None:
                check(len(find_all(same_root, "pattern")) == 1,
                      "three walls sharing one appearance define ONE <pattern>, got "
                      + str(len(find_all(same_root, "pattern"))))
                check(len([e for e in find_all(same_root, "path") if e.get("data-pattern")]) == 3,
                      "...and all three still reference it")
                check(len(find_all(diff_root, "pattern")) == 2,
                      "changing one wall's scale defines a SECOND <pattern>, got "
                      + str(len(find_all(diff_root, "pattern"))))
                ids = [e.get("id") for e in find_all(diff_root, "pattern")]
                check(len(set(ids)) == len(ids), "pattern ids are unique: " + str(ids))

        r = await run_probe(page, "Sheet-page SVG: raw millimetres, no calibration", PROBE_SHEET_SVG)
        if r:
            check(r["vpNoArg"] == r["vpTech"],
                  "bimBuildPlanViewportSVG(...) with no mode still equals an explicit 'technical' call")
            check("<pattern" not in r["vpTech"], "a technical viewport emits no <pattern>")
            pres_root, pres_err = parse_svg(r["vpPres"])
            check(pres_root is not None, "presentation viewport fragment well-formed: " + str(pres_err))
            if pres_root is not None:
                pats = find_all(pres_root, "pattern")
                check(len(pats) == 1, "one <pattern> in the viewport fragment, got " + str(len(pats)))
                if pats:
                    d = r["defs"]["brick"]
                    check(close(float(pats[0].get("width")), d["mm"] * d["w"] * 2, 1e-3),
                          "sheet tile width is the RAW millimetre figure %.3f (no calibration), got %s"
                          % (d["mm"] * d["w"] * 2, pats[0].get("width")))
                    check(close(float(pats[0].get("height")), d["mm"] * 2, 1e-3),
                          "sheet tile height is the raw millimetre figure %.3f, got %s"
                          % (d["mm"] * 2, pats[0].get("height")))
            sheet_root, sheet_err = parse_svg(r["sheetPres"])
            check(sheet_root is not None,
                  "the full presentation sheet SVG is well-formed: " + str(sheet_err))
            check("<pattern" not in r["sheetTech"], "the technical sheet SVG emits no <pattern>")
            if sheet_root is not None:
                ids = [e.get("id") for e in find_all(sheet_root, "pattern")]
                check(len(ids) >= 2,
                      "both viewports on the sheet define their own pattern, got " + str(len(ids)))
                check(len(set(ids)) == len(ids),
                      "pattern ids are unique across the sheet's viewport fragments: " + str(ids))

        r = await run_probe(page, "Live Canvas2D sink", PROBE_CANVAS)
        if r:
            pw, pr, tr = r["presWall"], r["presRoom"], r["techRoom"]
            check(pw and pw["pattern"] == "concrete",
                  "the wall's face records the resolved pattern: " + str(pw and pw["pattern"]))
            check(pw and pw["patternColor"] == "#884422" and close(pw["patternScale"], 1.5),
                  "...with its resolved colour and scale: " + str(pw))
            check(pw and pw["fill"] == "#c9b98a",
                  "the base fill is still the object's own colour -- the hatch went ON it, not "
                  "instead of it")
            check(pr and pr["pattern"] == "diagonal",
                  "a room fill takes a hatch too: " + str(pr and pr["pattern"]))
            check(tr and tr["pattern"] == "none",
                  "in technical mode the same room draws no hatch: " + str(tr and tr["pattern"]))
            check(tr and tr["fill"] == "rgba(127,212,196,0.14)",
                  "...and reverts to the pre-presentation room wash")

        r = await run_probe(page, "Validation, inheritance and persistence", PROBE_VALIDATION)
        if r:
            check(r["fromType"]["pattern"] == "concrete"
                  and r["fromType"]["patternColor"] == "#224466",
                  "a type's pattern and patternColor reach an instance with no override of its own")
            check(r["overridden"]["pattern"] == "brick"
                  and r["overridden"]["patternColor"] == "#aa3311"
                  and close(r["overridden"]["patternScale"], 2.5),
                  "an instance override wins field by field")
            check(r["envHasPatternColor"],
                  "the new keys are written into the saved project envelope")
            check(r["afterUndoRedo"] == r["overridden"],
                  "an undo/redo round trip preserves the hatch settings exactly")
            check(close(r["clampedHigh"], 8), "an absurdly high scale clamps to 8, got "
                  + str(r["clampedHigh"]))
            check(close(r["clampedLow"], 0.1), "an absurdly low scale clamps to 0.1, got "
                  + str(r["clampedLow"]))
            check(r["badColour"] == "#224466",
                  "an invalid patternColor falls back to the TYPE's value, not to the hard "
                  "default -- got " + str(r["badColour"]))
            check(r["badPattern"] == "concrete",
                  "an unknown pattern name falls back to the TYPE's value -- got "
                  + str(r["badPattern"]))
            check(r["cleared"]["pattern"] == "concrete"
                  and r["cleared"]["patternColor"] == "#224466",
                  "clearing the instance override returns the object to its type's hatch")

        r = await run_probe(page, "Room fills render under the model", PROBE_ROOM_ORDER)
        if r:
            check("presentation-room-fills" not in r["tech"],
                  "technical export is emitted in its original order, with no room-fill group")
            pres_root, pres_err = parse_svg(r["pres"])
            check(pres_root is not None, "presentation output well-formed: " + str(pres_err))
            if pres_root is not None:
                groups = [g for g in find_all(pres_root, "g")
                          if g.get("id") == "presentation-room-fills"]
                check(len(groups) == 1, "there is a presentation-room-fills group")
                if groups:
                    ids_in = set(e.get("data-obj") for e in groups[0].iter() if e.get("data-obj"))
                    check(ids_in == {r["roomId"]},
                          "only the room's own fill was moved under the model: " + str(ids_in))
                    check(all(e.get("data-layer") for e in groups[0] if tag_is(e, "path")),
                          "each moved path keeps a data-layer attribute, so no layer information "
                          "was lost by taking it out of its layer group")
                    check(not find_all(groups[0], "text"),
                          "the room's name/area label was NOT moved under -- a label is meant to "
                          "be read on top of the drawing")
                # Document order decides paint order in SVG: the room fill must precede the
                # column's path, or the fill would cover the column exactly as it used to.
                order = [e.get("data-obj") for e in find_all(pres_root, "path") if e.get("data-obj")]
                check(order and order[0] == r["roomId"],
                      "the room fill is the first path in the document, got " + str(order[:3]))
                check(r["colId"] in order and order.index(r["roomId"]) < order.index(r["colId"]),
                      "the column inside the room is drawn AFTER the room fill, so it stays visible")

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
