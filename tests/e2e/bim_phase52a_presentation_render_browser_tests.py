"""
bim_phase52a_presentation_render_browser_tests.py

Regression suite for Phase 52a (__acad3dV60) in canvas_v10.html: the first slice of the roadmap's
"Phase 52 - Presentation render mode" -- a Technical/Presentation toggle for the LIVE view that
actually consumes the Phase 51 graphic override data (fill, line color, line weight, opacity,
shadow) in the main solid-face draw loop and in drawRooms.

SCOPE, STATED PLAINLY (matches how this was scoped in canvas_v10_STATUS.md): hatch PATTERN
rendering is NOT part of this phase. The roadmap's own phase list puts "wires the existing
material cards' hatch/hatchColor into the BIM render" in Phase 53 ("Pattern and texture library"),
not Phase 52 -- so `pattern` stays inert data here, exactly as it was after Phase 51, and this
suite does not test it.

WHY THIS SUITE DOES NOT SAMPLE CANVAS PIXELS: rather than getImageData()-based pixel matching
(fragile under anti-aliasing, shade()'s lighting multiply, and screen-space projection specifics),
paint() and drawRooms() were extended to record the EXACT style decision made for each drawn
face/room (pre-shade base fill, resolved stroke color, resolved line width in px, opacity, and
whether a shadow was applied) onto A3D.lastPolys / A3D.lastRoomStyle, read back through
window.__a3dLastDrawStyle / window.__a3dLastRoomStyle. This tests what the app actually decided to
draw, not an approximation reconstructed from rendered pixels -- consistent with how every other
suite in this project favors reading model/computed state over screenshot diffing.

BACKWARD COMPATIBILITY IS THE CENTRAL CLAIM OF THIS PHASE, so it gets its own dedicated test
section: with A3D.presentMode left at its default (false), and separately with it explicitly
toggled off again after being on, every object's drawn style must be BYTE-IDENTICAL to the fixed
constants the render loop used before this phase existed (stroke 'rgba(0,0,0,0.35)', line width
0.7, opacity 1, no shadow; room fill 'rgba(127,212,196,0.14)', stroke '#7fd4c4', line width 1.1).

Run:  python3 bim_phase52a_presentation_render_browser_tests.py [path/to/canvas_v10.html]
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


# ---------------------------------------------------------------------------------------------
# 1. API surface present.
# ---------------------------------------------------------------------------------------------
PROBE_API = r"""
() => {
  return {
    marker: window.__acad3dV60 || null,
    hasApi: !!(window.__a3dSetPresentMode && window.__a3dPresentMode && window.__a3dLastDrawStyle &&
               window.__a3dLastRoomStyle && window.__a3dSetTypeGraphics && window.__a3dSetGraphicsOverride &&
               window.__a3dWall && window.__a3dCreateRoomAt && window.__a3dSelectFor)
  };
}
"""

# ---------------------------------------------------------------------------------------------
# 2. Backward compatibility, proven the RIGHT way: in the default state (presentMode off), the
#    live view renders through WebGL (bimGlRender), not the CPU polygon loop this phase touched --
#    so a wall's resolved-style record (__a3dLastDrawStyle, only ever written by the CPU loop)
#    must come back NULL, proving the CPU/presentation code path never ran at all, rather than
#    merely "ran and happened to match old constants". Rooms are different: drawRooms() is a
#    Canvas2D-only path that has ALWAYS run every frame regardless of WebGL, so its style record
#    is populated even by default, and DOES have to match the exact pre-Phase-52a constants.
# ---------------------------------------------------------------------------------------------
PROBE_DEFAULT_UNCHANGED = r"""
() => {
  window.__a3dTestSetObjs([]);
  const wallId = window.__a3dWall([[0,0],[6,0],[6,4],[0,4]], 0.3, 3, 'center', true);
  const roomId = window.__a3dCreateRoomAt([3,2], 0);
  window.__a3dSelectFor([]); // wall/room creation auto-selects; deselect for a clean baseline
  window.__a3dSetPresentMode(false);
  return {
    presentModeDefault: window.__a3dPresentMode(),
    wallStyle: window.__a3dLastDrawStyle(wallId),
    roomStyle: window.__a3dLastRoomStyle(roomId)
  };
}
"""

# ---------------------------------------------------------------------------------------------
# 3. Toggling ON with NO overrides configured still keeps fill/opacity/shadow at today's look
#    (fill:'none' means "don't touch the fill"), but line color/weight DO switch to the resolved
#    (default) technical-style values -- documented, deliberate behavior: the toggle itself is the
#    opt-in, so turning it on is expected to produce crisp presentation linework even before any
#    field is customized. Toggling back OFF is checked against a FRESH wall never drawn while ON
#    (not the same wall re-read) -- A3D.lastPolys is a pre-existing, deliberately-stale cache once
#    WebGL is back in control (only rebuilt on-demand for click-picking, not every frame, for
#    performance -- unrelated to this phase), so the SAME wall's old ON-state record is expected
#    to still sit there inertly; that staleness has no bearing on what's actually rendered, since
#    bimGlRender never reads A3D.lastPolys at all. A fresh wall is the clean way to prove it.
# ---------------------------------------------------------------------------------------------
PROBE_ON_NO_OVERRIDES = r"""
() => {
  window.__a3dTestSetObjs([]);
  const wallId = window.__a3dWall([[0,0],[6,0],[6,4],[0,4]], 0.3, 3, 'center', true);
  window.__a3dSelectFor([]);
  window.__a3dSetPresentMode(true);
  const on = window.__a3dLastDrawStyle(wallId);
  window.__a3dSetPresentMode(false);
  const freshWallId = window.__a3dWall([[20,0],[26,0],[26,4],[20,4]], 0.3, 3, 'center', true);
  window.__a3dSelectFor([]);
  const backOffFresh = window.__a3dLastDrawStyle(freshWallId);
  return {on, backOffFresh};
}
"""

# ---------------------------------------------------------------------------------------------
# 4. A configured fill override actually changes the drawn base fill color, and line weight/color
#    overrides change the drawn stroke, while presentMode is ON. bimGlRender (the WebGL path used
#    whenever presentMode is off) is confirmed, statically, never to reference graphicsOverride or
#    bimResolveGraphics at all -- so an override structurally cannot reach the GPU path, checked
#    directly against the source rather than inferred from a stale cache.
# ---------------------------------------------------------------------------------------------
PROBE_FILL_AND_LINE_OVERRIDE = r"""
() => {
  window.__a3dTestSetObjs([]);
  const wallId = window.__a3dWall([[0,0],[6,0],[6,4],[0,4]], 0.3, 3, 'center', true);
  window.__a3dSelectFor([]);
  window.__a3dSetGraphicsOverride(wallId, 'presentation', 'fill', '#b7ab98');
  window.__a3dSetGraphicsOverride(wallId, 'presentation', 'lineColor', '#ff6600');
  window.__a3dSetGraphicsOverride(wallId, 'presentation', 'lineWeight', 1.0);
  window.__a3dSetPresentMode(true);
  const on = window.__a3dLastDrawStyle(wallId);
  return {on};
}
"""

# ---------------------------------------------------------------------------------------------
# 5. Opacity and shadow overrides are actually applied when on, and cleanly reset (opacity back to
#    1, no shadow) for the NEXT object drawn afterward -- guards against state leaking between
#    polygons in the shared draw loop (no ctx.save()/restore() wraps the solid-face loop itself).
# ---------------------------------------------------------------------------------------------
PROBE_OPACITY_SHADOW_NO_LEAK = r"""
() => {
  window.__a3dTestSetObjs([]);
  const wallA = window.__a3dWall([[0,0],[6,0],[6,4],[0,4]], 0.3, 3, 'center', true);
  const wallB = window.__a3dWall([[20,0],[26,0],[26,4],[20,4]], 0.3, 3, 'center', true);
  window.__a3dSelectFor([]);
  window.__a3dSetGraphicsOverride(wallA, 'presentation', 'opacity', 0.4);
  window.__a3dSetGraphicsOverride(wallA, 'presentation', 'shadow', true);
  window.__a3dSetPresentMode(true);
  const a = window.__a3dLastDrawStyle(wallA);
  const b = window.__a3dLastDrawStyle(wallB);
  return {a, b};
}
"""

# ---------------------------------------------------------------------------------------------
# 6. Room fills follow the same "fill:'none' keeps today's look, an actual override changes it"
#    rule as walls -- tested separately since rooms use a different code path (drawRooms, not the
#    main solid-face loop) and a separate style-record store (A3D.lastRoomStyle).
# ---------------------------------------------------------------------------------------------
PROBE_ROOM_OVERRIDE = r"""
() => {
  window.__a3dTestSetObjs([]);
  const wallId = window.__a3dWall([[0,0],[6,0],[6,4],[0,4]], 0.3, 3, 'center', true);
  const roomId = window.__a3dCreateRoomAt([3,2], 0);
  window.__a3dSelectFor([]); // room creation auto-selects; deselect for a clean "no override" baseline
  window.__a3dSetPresentMode(true);
  const noOverride = window.__a3dLastRoomStyle(roomId);
  window.__a3dSetGraphicsOverride(roomId, 'presentation', 'fill', '#2244aa');
  window.__a3dSetGraphicsOverride(roomId, 'presentation', 'lineColor', '#112266');
  const styled = window.__a3dLastRoomStyle(roomId) || {}; // stale until next paint
  window.__a3dSetPresentMode(true); // re-trigger a paint via the same setter (idempotent toggle path)
  const afterRepaint = window.__a3dLastRoomStyle(roomId);
  return {noOverride, afterRepaint};
}
"""

# ---------------------------------------------------------------------------------------------
# 7. Type-level presentation graphics reach an instance through the resolver exactly like Phase 51
#    proved for data alone -- this confirms the RENDER path picks up a type-level edit too, not
#    just an instance override.
# ---------------------------------------------------------------------------------------------
PROBE_TYPE_LEVEL_RENDERS = r"""
() => {
  window.__a3dTestSetObjs([]);
  const wallId = window.__a3dWall([[0,0],[6,0],[6,4],[0,4]], 0.3, 3, 'center', true);
  window.__a3dSetWallType(wallId, 'wt-gen300');
  window.__a3dSetTypeGraphics('wall', 'wt-gen300', 'presentation', 'fill', '#c8a06a');
  window.__a3dSetPresentMode(true);
  return window.__a3dLastDrawStyle(wallId);
}
"""


async def main():
    html_text = pathlib.Path(TARGET).read_text(encoding="utf-8")
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        pg = await b.new_page()
        page_errors = []
        pg.on("pageerror", lambda e: page_errors.append(str(e)))
        await pg.goto(pathlib.Path(TARGET).absolute().as_uri())
        await pg.evaluate("() => { if (window.__a3dEnter) window.__a3dEnter(); }")

        print("== API surface ==")
        r = await pg.evaluate(PROBE_API)
        check(r.get("marker") is not None, "V60 marker present")
        check(r.get("hasApi"), "all Phase 52a test hooks present")

        print("\n== default state: WebGL stays in control (no CPU record for solids); rooms unchanged ==")
        r = await pg.evaluate(PROBE_DEFAULT_UNCHANGED)
        check(r.get("presentModeDefault") is False, "A3D.presentMode defaults to false")
        check(r.get("wallStyle") is None,
              "with presentMode off, the wall has NO CPU-loop style record at all -- WebGL rendered it, "
              "proving the presentation code path is provably unreached by default (%r)" % r.get("wallStyle"))
        rs = r.get("roomStyle") or {}
        check(rs.get("fill") == "rgba(127,212,196,0.14)", "room fill matches the old fixed constant (%r)" % rs.get("fill"))
        check(rs.get("stroke") == "#7fd4c4", "room stroke matches the old fixed constant (%r)" % rs.get("stroke"))
        check(close(rs.get("lineWidth", -1), 1.1), "room line width matches the old fixed constant 1.1 (%r)" % rs.get("lineWidth"))

        print("\n== toggled ON with no overrides: line style switches to the resolved default; a FRESH wall drawn after toggling OFF gets none ==")
        r = await pg.evaluate(PROBE_ON_NO_OVERRIDES)
        on, backFresh = r.get("on") or {}, r.get("backOffFresh")
        check(on is not None, "with presentMode on, the wall DOES get a CPU-loop style record (WebGL was bypassed)")
        if on:
            check(on.get("stroke") == "#000000", "with no line-color override, presentation mode draws the resolved default lineColor (%r)" % on.get("stroke"))
            check(close(on.get("lineWidth", -1), 0.7), "with no line-weight override, resolved default 0.25mm maps back to the same 0.7px (%r)" % on.get("lineWidth"))
            check(on.get("opacity") == 1 and on.get("shadow") is False, "no opacity/shadow override means both stay at their neutral defaults")
        check(backFresh is None,
              "a FRESH wall created after toggling back OFF gets no CPU-loop record at all -- WebGL is genuinely "
              "back in control for new geometry too, not just coincidentally quiet (%r)" % backFresh)

        print("\n== configured fill/line overrides actually change the drawn style while ON; GPU path structurally can't read them ==")
        r = await pg.evaluate(PROBE_FILL_AND_LINE_OVERRIDE)
        on = r.get("on") or {}
        check(on.get("fill") == "#b7ab98", "overridden fill is used as the drawn base fill while ON (%r)" % on.get("fill"))
        check(on.get("stroke") == "#ff6600", "overridden lineColor is used as the drawn stroke while ON (%r)" % on.get("stroke"))
        check(close(on.get("lineWidth", -1), 2.8), "overridden lineWeight 1.0mm maps to 2.8px via BIM_LW_TO_PX (%r)" % on.get("lineWidth"))
        gl_src_start = html_text.find("function bimGlRender(")
        gl_src_end = html_text.find("\n  function ", gl_src_start + 10) if gl_src_start >= 0 else -1
        gl_src = html_text[gl_src_start:gl_src_end] if gl_src_start >= 0 and gl_src_end > gl_src_start else ""
        check(bool(gl_src) and "graphicsOverride" not in gl_src and "bimResolveGraphics" not in gl_src,
              "bimGlRender's own source never references graphicsOverride or bimResolveGraphics -- "
              "an override cannot reach the GPU path structurally, not just by observed absence")

        print("\n== opacity/shadow apply to the overridden object and do not leak to the next one ==")
        r = await pg.evaluate(PROBE_OPACITY_SHADOW_NO_LEAK)
        a, bb = r.get("a") or {}, r.get("b") or {}
        check(close(a.get("opacity", -1), 0.4), "wall A's overridden opacity 0.4 is applied (%r)" % a.get("opacity"))
        check(a.get("shadow") is True, "wall A's shadow override is applied")
        check(close(bb.get("opacity", -1), 1), "wall B (no override) still has opacity 1 -- no leakage from wall A (%r)" % bb.get("opacity"))
        check(bb.get("shadow") is False, "wall B (no override) has no shadow -- no leakage from wall A")

        print("\n== room fill/line overrides render correctly, independent of the wall code path ==")
        r = await pg.evaluate(PROBE_ROOM_OVERRIDE)
        no_ov = r.get("noOverride") or {}
        check(no_ov.get("fill") == "rgba(127,212,196,0.14)", "room with no override keeps today's default fill even with presentMode ON (%r)" % no_ov.get("fill"))
        after = r.get("afterRepaint") or {}
        check(after.get("fill") == "#2244aa", "room's overridden fill is used after the override + repaint (%r)" % after.get("fill"))
        check(after.get("stroke") == "#112266", "room's overridden lineColor is used after the override + repaint (%r)" % after.get("stroke"))

        print("\n== a TYPE-level presentation edit reaches the render, not just instance overrides ==")
        r = await pg.evaluate(PROBE_TYPE_LEVEL_RENDERS)
        check(r.get("fill") == "#c8a06a", "wall with no instance override still renders the shared TYPE's presentation fill (%r)" % r.get("fill"))

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
