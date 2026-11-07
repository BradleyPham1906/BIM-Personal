"""
bim_phase50_vector_svg_export_browser_tests.py

Regression suite for Phase 50 (__acad3dV56) in canvas_v10.html: "Export view as SVG", the first
piece of the deferred presentation-pipeline roadmap (claude/roadmap-unified-presentation-pipeline.md)
picked up now that the dependency graph (Phase 55a-55e) is fully shipped.

WHAT SHIPPED, IN ONE SENTENCE: bimBuildSVG() mirrors the already-shipped bimBuildDXF()'s exact
per-object-type entity walk (wall centerline/inner/outer loop, room boundary + label, sketch
outline, all five dim kinds, text, floor/ceiling/roof footprint, column footprint) but emits real
SVG markup -- <path>/<line>/<text> grouped one <g> per model layer, a computed viewBox fit to the
actual drawing bounds. (V104: the Z axis maps to SVG y UNflipped, y down like the plan; the
-z flip this suite once required was the plan's mirror image.)

WHY MODEL-SPACE, NOT SCREEN-SPACE: the roadmap's own architecture diagram suggested a third sink
hanging off the live 3D camera projection (toScreen), alongside the existing WebGL and Canvas2D
sinks. Investigating first (per this project's own working method -- gather material before
building) found that a strictly better foundation already exists and ships today: bimBuildDXF()
already separates geometry from its output sink, in TRUE PLAN COORDINATES independent of the
current camera/zoom/pan. Screen-projecting the current 3D view would have produced a vector trace
of whatever perspective the camera happened to be at -- not a dimensionally correct technical
drawing. bimBuildSVG() is deliberately built the DXF way instead: same helper shape (poly/line/
text), same branches, so the two vector exporters cannot silently drift apart in what they consider
"the model's 2D footprint."

DELIBERATE DIFFERENCES FROM bimBuildDXF, EACH FOR A REASON:
  - Every emitted <path>/<line>/<text> carries a data-obj attribute pointing back to its source
    object's id -- something DXF's flat, id-less entity list cannot do, and useful for anyone
    post-processing the SVG (highlighting an element, driving it from the model).
  - Fill is explicitly none everywhere (pure linework) -- poche and material fills belong to the
    still-deferred Phase 52, not this one.
  - A computed viewBox with a margin proportional to the drawing's own diagonal, rather than a
    fixed page size -- the export is a "fit to content" plan, not an letter/A4-shaped print (sheet
    printing is left for a dedicated follow-up phase, noted as NOT done below).

NOT done in this phase, flagged rather than silently left implicit: the live Canvas2D paint()
pipeline is untouched (zero risk to the interactive viewport); no graphic overrides/poche/shadows
(Phase 51/52); bimPrintSheet still embeds a PNG for sheet printing, not yet replaced by vector
output.

Run:  python3 bim_phase50_vector_svg_export_browser_tests.py [path/to/canvas_v10.html]
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
    return abs(a - b) <= tol


SVG_NS = "{http://www.w3.org/2000/svg}"


def parse_svg(svg_text):
    """Returns the parsed root Element, or None (with the exception) on a malformed document."""
    try:
        return ET.fromstring(svg_text), None
    except ET.ParseError as e:
        return None, e


# ---------------------------------------------------------------------------------------------
# 1. A real, mixed scene: wall loop + room + linear dim + text (with XML-hostile characters).
# ---------------------------------------------------------------------------------------------
PROBE_MIXED_SCENE = r"""
() => {
  const out = {};
  out.marker = window.__acad3dV56 || null;
  out.hasApi = !!(window.__a3dTestSetObjs && window.__a3dWall && window.__a3dCreateRoomAt &&
                   window.__a3dPushTestObj && window.__a3dBuildSVG && window.__a3dAddLayer &&
                   window.__a3dLayers);
  if (!out.hasApi) return out;

  window.__a3dTestSetObjs([]);
  const w = window.__a3dWall([[0,0],[6,0],[6,4],[0,4]], 0.3, 3, 'center', true);
  const roomId = window.__a3dCreateRoomAt([3,2], 0);

  const dimId = window.__a3dPushTestObj({
    id: 'test-dim-1', t: 'dim', y: 0, pos: [0,0,0],
    p1: [0,0], p2: [6,0], d1: [0,-1], d2: [6,-1], length: 6
  });
  const textId = window.__a3dPushTestObj({
    id: 'test-text-1', t: 'text', y: 0, pos: [0,0,0],
    pt: [1, -2], text: 'Client A & <Sons> "Ltd"'
  });

  const res = window.__a3dBuildSVG();
  out.svg = res.text;
  out.stats = res.stats;
  out.wallId = w;
  out.roomId = roomId;
  out.dimId = dimId;
  out.textId = textId;
  return out;
}
"""

# ---------------------------------------------------------------------------------------------
# 2. Layer grouping: two objects on two different (real, named) layers land in two separate <g>s.
# ---------------------------------------------------------------------------------------------
PROBE_LAYER_GROUPING = r"""
() => {
  const out = {};
  out.hasApi = !!(window.__a3dTestSetObjs && window.__a3dAddLayer && window.__a3dPushTestObj &&
                   window.__a3dBuildSVG && window.__a3dLayers);
  if (!out.hasApi) return out;

  window.__a3dTestSetObjs([]);
  const layerA = window.__a3dAddLayer('Structural Grid A');
  const layerB = window.__a3dAddLayer('Annotation B');
  const layers = window.__a3dLayers();
  const la = layers.find(l => l.name === 'Structural Grid A');
  const lb = layers.find(l => l.name === 'Annotation B');

  window.__a3dPushTestObj({id:'la-text', t:'text', y:0, pos:[0,0,0], pt:[0,0], text:'On A', layer: la.id});
  window.__a3dPushTestObj({id:'lb-text', t:'text', y:0, pos:[0,0,0], pt:[1,1], text:'On B', layer: lb.id});
  // No .layer at all -- must fall into the DXF-equivalent implicit '0' bucket, not throw.
  window.__a3dPushTestObj({id:'l0-text', t:'text', y:0, pos:[0,0,0], pt:[2,2], text:'On none'});

  const res = window.__a3dBuildSVG();
  out.svg = res.text;
  out.stats = res.stats;
  return out;
}
"""

# ---------------------------------------------------------------------------------------------
# 3. Empty scene: no crash, zero counts, still a parseable (if trivial) document.
# ---------------------------------------------------------------------------------------------
PROBE_EMPTY_SCENE = r"""
() => {
  const out = {};
  out.hasApi = !!(window.__a3dTestSetObjs && window.__a3dBuildSVG);
  if (!out.hasApi) return out;
  window.__a3dTestSetObjs([]);
  const res = window.__a3dBuildSVG();
  out.svg = res.text;
  out.stats = res.stats;
  return out;
}
"""

# ---------------------------------------------------------------------------------------------
# 4. Coordinate correctness: X and Z pass through as the plan draws them (V104: y = +Z).
# ---------------------------------------------------------------------------------------------
PROBE_COORD_FLIP = r"""
() => {
  const out = {};
  out.hasApi = !!(window.__a3dTestSetObjs && window.__a3dPushTestObj && window.__a3dBuildSVG);
  if (!out.hasApi) return out;
  window.__a3dTestSetObjs([]);
  window.__a3dPushTestObj({id:'flip-text', t:'text', y:0, pos:[0,0,0], pt:[7.5, 3.25], text:'Pt'});
  const res = window.__a3dBuildSVG();
  out.svg = res.text;
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

        # ---------------- mixed scene ----------------
        r = await pg.evaluate(PROBE_MIXED_SCENE)
        check(r.get("marker") is not None, "Phase 50 marker (__acad3dV56) present")
        check(r.get("hasApi"), "required test hooks present")
        if r.get("hasApi"):
            root, perr = parse_svg(r["svg"])
            check(root is not None, "exported SVG is well-formed XML (%s)" % (perr or "ok"))
            if root is not None:
                check(root.tag == SVG_NS + "svg", "root element is <svg>")
                check("viewBox" in root.attrib, "root <svg> carries a viewBox")
                vb = [float(x) for x in root.attrib["viewBox"].split()]
                check(vb[2] > 0 and vb[3] > 0, "viewBox has a positive width/height (%r)" % vb)
                paths = root.findall(".//" + SVG_NS + "path")
                lines = root.findall(".//" + SVG_NS + "line")
                texts = root.findall(".//" + SVG_NS + "text")
                check(len(paths) == r["stats"]["polyline"],
                      "path count in the document matches reported stats (%d)" % len(paths))
                check(len(lines) == r["stats"]["line"],
                      "line count in the document matches reported stats (%d)" % len(lines))
                check(len(texts) == r["stats"]["text"],
                      "text count in the document matches reported stats (%d)" % len(texts))
                wall_paths = [p for p in paths if p.attrib.get("data-obj") == r["wallId"]]
                check(len(wall_paths) == 3,
                      "the closed wall loop emits exactly 3 paths (centerline + inner + outer loop), "
                      "all tagged data-obj=<wall id> (%d)" % len(wall_paths))
                room_texts = [t for t in texts if t.attrib.get("data-obj") == r["roomId"]]
                check(len(room_texts) == 1 and "m2" in (room_texts[0].text or ""),
                      "room emits exactly one area-label <text>, tagged back to the room's id")
                dim_lines = [l for l in lines if l.attrib.get("data-obj") == r["dimId"]]
                check(len(dim_lines) == 3,
                      "the linear dim emits exactly 3 <line> elements (2 extension lines + 1 dimension line)")
                free_text = [t for t in texts if t.attrib.get("data-obj") == r["textId"]]
                check(len(free_text) == 1, "the text object emits exactly one <text>")
                if free_text:
                    check(free_text[0].text == 'Client A & <Sons> "Ltd"',
                          "the text object's XML-hostile content (&, <, \") round-trips correctly through escaping, "
                          "not just \"parses without throwing\" (got %r)" % free_text[0].text)
            check(r["stats"]["skipped"] == 0, "no objects were skipped as having no 2D footprint (%d)" % r["stats"]["skipped"])

        print()
        # ---------------- layer grouping ----------------
        r = await pg.evaluate(PROBE_LAYER_GROUPING)
        check(r.get("hasApi"), "layer-grouping test hooks present")
        if r.get("hasApi"):
            root, perr = parse_svg(r["svg"])
            check(root is not None, "layer-grouping SVG is well-formed XML (%s)" % (perr or "ok"))
            if root is not None:
                groups = root.findall(".//" + SVG_NS + "g[@data-layer]")
                check(len(groups) == 3,
                      "three distinct layer groups exist: two real layers plus the implicit '0' bucket for the "
                      "layerless object (%d)" % len(groups))
                by_layer_text = {}
                for g in groups:
                    for t in g.findall(SVG_NS + "text"):
                        by_layer_text.setdefault(g.attrib.get("data-layer"), []).append(t.text)
                found_a = any("On A" in v for vals in by_layer_text.values() for v in vals if "On A" == v)
                # Simpler: just confirm each label appears in exactly one group's subtree and not mixed together.
                flat = {k: set(v) for k, v in by_layer_text.items()}
                labels_seen = [v for vals in flat.values() for v in vals]
                check(sorted(labels_seen) == ["On A", "On B", "On none"],
                      "each text landed in some layer group, none lost or duplicated (%r)" % sorted(labels_seen))
                # No two different labels share the same group (each of the 3 objects is on its own layer).
                singleton_groups = sum(1 for vals in flat.values() if len(vals) == 1)
                check(singleton_groups == 3, "each of the 3 differently-layered objects got its own separate group")

        print()
        # ---------------- empty scene ----------------
        r = await pg.evaluate(PROBE_EMPTY_SCENE)
        check(r.get("hasApi"), "empty-scene test hooks present")
        if r.get("hasApi"):
            root, perr = parse_svg(r["svg"])
            check(root is not None, "an empty model still produces a well-formed SVG document (%s)" % (perr or "ok"))
            check(r["stats"]["polyline"] == 0 and r["stats"]["line"] == 0 and r["stats"]["text"] == 0,
                  "an empty model reports zero entities of every kind, no crash")

        print()
        # ---------------- coordinate flip ----------------
        r = await pg.evaluate(PROBE_COORD_FLIP)
        check(r.get("hasApi"), "coordinate-flip test hooks present")
        if r.get("hasApi"):
            root, perr = parse_svg(r["svg"])
            check(root is not None, "coordinate-flip SVG is well-formed XML (%s)" % (perr or "ok"))
            if root is not None:
                t = root.find(".//" + SVG_NS + "text[@data-obj='flip-text']")
                check(t is not None, "the probe's text element is present")
                if t is not None:
                    x = float(t.attrib["x"]); y = float(t.attrib["y"])
                    check(close(x, 7.5), "X coordinate is passed through UNFLIPPED (model X=7.5 -> svg x=%.4f)" % x)
                    # __acad3dV104 reversed this on purpose. Model +Z runs DOWN the plan (project
                    # north is -Z) and SVG y runs down too, so y = +Z is the plan; y = -Z, which this
                    # line asserted, was the plan's mirror image. The V104 suite checks orientation
                    # against an independent rule.
                    check(close(y, 3.25), "Z maps to SVG y unflipped, y down like the plan (model Z=3.25 -> svg y=%.4f)" % y)

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
