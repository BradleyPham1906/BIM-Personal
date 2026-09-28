"""
bim_phase51_graphic_overrides_browser_tests.py

Regression suite for Phase 51 (__acad3dV59) in canvas_v10.html: the graphic override data model
named in claude/roadmap-unified-presentation-pipeline.md -- per-type and per-instance "technical"
and "presentation" appearance dictionaries (line weight, line color, fill, pattern, opacity,
shadow), carried on the existing Type/Instance parameter system (A3D.types / TYPE_CATS) rather
than a parallel registry.

SCOPE, STATED PLAINLY (matches the roadmap's own phase description): this is DATA AND UI ONLY.
Nothing in bimBuildDXF/bimBuildSVG/bimBuildPlanViewportSVG or the live paint() path reads any of
this yet -- Phase 52 (presentation render mode) is the consumer. Every check below is therefore
about the DATA MODEL's own correctness (resolution order, persistence, sanitization) and the
Properties-palette / Type-dialog test hooks that expose it, not about anything drawn on screen.

TWO LEVELS: TYPE-level graphics live on A3D.types[cat][i].graphics, only for the four TYPE_CATS
categories (wall/floor/ceiling/column) that have a type system at all. INSTANCE-level overrides
live on o.graphicsOverride, at the TOP of any object (not nested under o.bim) -- because unlike
thickness or width, an appearance override is meaningful for objects with no type system behind
them at all (a room, in this suite). Resolution is instance override > type default > hard-coded
fallback, field by field, independently for each of the two modes.

FAIL-SAFE IS TESTED DIRECTLY, not assumed: a dedicated test corrupts a project file's graphics
data (negative line weight, non-hex color, out-of-range opacity, wrong-typed shadow, an unknown
pattern name, and a graphicsOverride that is a bare string instead of an object) and imports it
through the real load path (bimImportProjectFile -> bimRestoreState -> bimEnsureTypes), then
confirms every bad value was replaced with a safe default and NOT one JS error was thrown --
this is the project's own "fail gracefully... explicit console warning" constraint, verified
rather than taken on faith.

Run:  python3 bim_phase51_graphic_overrides_browser_tests.py [path/to/canvas_v10.html]
"""
import asyncio, json, pathlib, sys
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


HEX_RE_OK = lambda s: isinstance(s, str) and len(s) == 7 and s[0] == "#"

# ---------------------------------------------------------------------------------------------
# 1. API surface present.
# ---------------------------------------------------------------------------------------------
PROBE_API = r"""
() => {
  return {
    marker: window.__acad3dV59 || null,
    hasApi: !!(window.__a3dResolveGraphics && window.__a3dSetGraphicsOverride &&
               window.__a3dClearGraphicsOverride && window.__a3dSetTypeGraphics &&
               window.__a3dTypeGraphics && window.__a3dWall && window.__a3dSetWallType &&
               window.__a3dCreateRoomAt && window.__a3dProjectEnvelope && window.__a3dImportProject &&
               window.__a3dTestSetObjs)
  };
}
"""

# ---------------------------------------------------------------------------------------------
# 2. Type defaults are well-formed after bimEnsureTypes backfill (fresh model, nothing edited).
# ---------------------------------------------------------------------------------------------
PROBE_TYPE_DEFAULTS = r"""
() => {
  window.__a3dTestSetObjs([]);
  const wallId = window.__a3dWall([[0,0],[5,0]], 0.3, 3, 'center', false);
  window.__a3dSetWallType(wallId, 'wt-gen300');
  return {
    typeGfx: window.__a3dTypeGraphics('wall', 'wt-gen300'),
    resolvedTech: window.__a3dResolveGraphics(wallId, 'technical'),
    resolvedPres: window.__a3dResolveGraphics(wallId, 'presentation')
  };
}
"""

# ---------------------------------------------------------------------------------------------
# 3. Editing a TYPE's graphics propagates to every instance sharing that type -- no instance-level
#    override involved at all, matching the existing thickness/width "shared" semantics.
# ---------------------------------------------------------------------------------------------
PROBE_TYPE_EDIT_PROPAGATES = r"""
() => {
  window.__a3dTestSetObjs([]);
  const wA = window.__a3dWall([[0,0],[5,0]], 0.3, 3, 'center', false);
  const wB = window.__a3dWall([[10,0],[15,0]], 0.3, 3, 'center', false);
  window.__a3dSetWallType(wA, 'wt-gen300');
  window.__a3dSetWallType(wB, 'wt-gen300');
  window.__a3dSetTypeGraphics('wall', 'wt-gen300', 'technical', 'lineWeight', 0.5);
  window.__a3dSetTypeGraphics('wall', 'wt-gen300', 'technical', 'lineColor', '#ff0000');
  return {
    a: window.__a3dResolveGraphics(wA, 'technical'),
    b: window.__a3dResolveGraphics(wB, 'technical'),
    aPres: window.__a3dResolveGraphics(wA, 'presentation'),
    wA, wB
  };
}
"""

# ---------------------------------------------------------------------------------------------
# 4. Instance override wins over the type default, for ONLY the overridden field(s); the other
#    instance sharing the same type is unaffected (no leakage between instances).
# ---------------------------------------------------------------------------------------------
PROBE_INSTANCE_OVERRIDE_PRECEDENCE = r"""
() => {
  window.__a3dTestSetObjs([]);
  const wA = window.__a3dWall([[0,0],[5,0]], 0.3, 3, 'center', false);
  const wB = window.__a3dWall([[10,0],[15,0]], 0.3, 3, 'center', false);
  window.__a3dSetWallType(wA, 'wt-gen300');
  window.__a3dSetWallType(wB, 'wt-gen300');
  window.__a3dSetTypeGraphics('wall', 'wt-gen300', 'technical', 'lineColor', '#ff0000');
  window.__a3dSetTypeGraphics('wall', 'wt-gen300', 'technical', 'lineWeight', 0.5);
  window.__a3dSetGraphicsOverride(wA, 'technical', 'lineColor', '#00ff00');
  return {
    a: window.__a3dResolveGraphics(wA, 'technical'),
    b: window.__a3dResolveGraphics(wB, 'technical')
  };
}
"""

# ---------------------------------------------------------------------------------------------
# 5. Clearing a SINGLE override field reverts just that field to the type default and leaves the
#    object's OTHER override fields untouched; clearing a whole MODE reverts everything for that
#    mode while leaving the other mode's overrides alone.
# ---------------------------------------------------------------------------------------------
PROBE_RESET_TO_TYPE = r"""
() => {
  window.__a3dTestSetObjs([]);
  const w = window.__a3dWall([[0,0],[5,0]], 0.3, 3, 'center', false);
  window.__a3dSetWallType(w, 'wt-gen300');
  window.__a3dSetTypeGraphics('wall', 'wt-gen300', 'technical', 'lineColor', '#ff0000');
  window.__a3dSetGraphicsOverride(w, 'technical', 'lineColor', '#00ff00');
  window.__a3dSetGraphicsOverride(w, 'technical', 'shadow', true);
  window.__a3dSetGraphicsOverride(w, 'presentation', 'shadow', true);
  const beforeClearField = window.__a3dResolveGraphics(w, 'technical');
  window.__a3dSetGraphicsOverride(w, 'technical', 'lineColor', null);
  const afterClearField = window.__a3dResolveGraphics(w, 'technical');
  const presStillOverridden = window.__a3dResolveGraphics(w, 'presentation');
  window.__a3dClearGraphicsOverride(w, 'technical');
  const afterClearMode = window.__a3dResolveGraphics(w, 'technical');
  const presUnaffectedByModeClear = window.__a3dResolveGraphics(w, 'presentation');
  return {beforeClearField, afterClearField, presStillOverridden, afterClearMode, presUnaffectedByModeClear};
}
"""

# ---------------------------------------------------------------------------------------------
# 6. Fail-safe: a corrupted project file (bad line weight, bad color, out-of-range opacity, wrong
#    -typed shadow, unknown pattern, and a graphicsOverride that is a plain string) is imported
#    through the REAL load path. Every bad value must be replaced with a safe default and nothing
#    should throw.
# ---------------------------------------------------------------------------------------------
PROBE_BUILD_SCENE_FOR_CORRUPTION = r"""
() => {
  window.__a3dTestSetObjs([]);
  const w = window.__a3dWall([[0,0],[5,0]], 0.3, 3, 'center', false);
  window.__a3dSetWallType(w, 'wt-gen300');
  return {envelope: window.__a3dProjectEnvelope(), wallId: w};
}
"""

PROBE_IMPORT_CORRUPTED = r"""
(text) => {
  window.__a3dTestSetObjs([]);
  const ok = window.__a3dImportProject(text, 'corrupt.json');
  return {ok};
}
"""

PROBE_READ_AFTER_CORRUPT_IMPORT = r"""
(args) => {
  return {
    typeGfx: window.__a3dTypeGraphics('wall', args.typeId),
    resolved: window.__a3dResolveGraphics(args.wallId, 'technical')
  };
}
"""

# ---------------------------------------------------------------------------------------------
# 7. Persistence round trip through the real export/import path: type-level edits AND an instance
#    override both survive a full envelope export -> clear -> import cycle unchanged.
# ---------------------------------------------------------------------------------------------
PROBE_ROUNDTRIP_SETUP = r"""
() => {
  window.__a3dTestSetObjs([]);
  const w = window.__a3dWall([[0,0],[5,0]], 0.3, 3, 'center', false);
  window.__a3dSetWallType(w, 'wt-ext400');
  window.__a3dSetTypeGraphics('wall', 'wt-ext400', 'presentation', 'fill', '#b7ab98');
  window.__a3dSetTypeGraphics('wall', 'wt-ext400', 'presentation', 'pattern', 'diagonal');
  window.__a3dSetGraphicsOverride(w, 'technical', 'lineWeight', 0.7);
  const before = window.__a3dResolveGraphics(w, 'technical');
  const beforePres = window.__a3dResolveGraphics(w, 'presentation');
  return {envelope: window.__a3dProjectEnvelope(), wallId: w, before, beforePres};
}
"""

PROBE_ROUNDTRIP_RELOAD = r"""
(text) => {
  window.__a3dTestSetObjs([]);
  const ok = window.__a3dImportProject(text, 'roundtrip.json');
  return {ok};
}
"""

PROBE_ROUNDTRIP_READ = r"""
(wallId) => {
  return {
    tech: window.__a3dResolveGraphics(wallId, 'technical'),
    pres: window.__a3dResolveGraphics(wallId, 'presentation')
  };
}
"""

# ---------------------------------------------------------------------------------------------
# 8. Opacity clamps into [0,1] on read even when an out-of-range value was written directly
#    (defense in depth: the Properties-palette change handler already clamps at write time, but
#    the resolver clamps independently too, since overrides can also arrive via project import).
# ---------------------------------------------------------------------------------------------
PROBE_OPACITY_CLAMP = r"""
() => {
  window.__a3dTestSetObjs([]);
  const w = window.__a3dWall([[0,0],[5,0]], 0.3, 3, 'center', false);
  window.__a3dSetGraphicsOverride(w, 'technical', 'opacity', 5);
  const high = window.__a3dResolveGraphics(w, 'technical').opacity;
  window.__a3dSetGraphicsOverride(w, 'technical', 'opacity', -3);
  const low = window.__a3dResolveGraphics(w, 'technical').opacity;
  return {high, low};
}
"""

# ---------------------------------------------------------------------------------------------
# 9. An invalid color override (not #rrggbb) is rejected by the sanitizer -- resolve falls back
#    to the type/default value rather than propagating the bad string.
# ---------------------------------------------------------------------------------------------
PROBE_INVALID_COLOR_REJECTED = r"""
() => {
  window.__a3dTestSetObjs([]);
  const w = window.__a3dWall([[0,0],[5,0]], 0.3, 3, 'center', false);
  window.__a3dSetGraphicsOverride(w, 'technical', 'lineColor', 'red');
  return window.__a3dResolveGraphics(w, 'technical');
}
"""

# ---------------------------------------------------------------------------------------------
# 10. Instance overrides work on an object with NO type system behind it at all (a room has no
#     .bim, so there is nothing to inherit from) -- confirms the resolver's fallback path, not
#     just its type-aware path.
# ---------------------------------------------------------------------------------------------
PROBE_NONTYPED_OBJECT = r"""
() => {
  window.__a3dTestSetObjs([]);
  const w = window.__a3dWall([[0,0],[6,0],[6,4],[0,4]], 0.3, 3, 'center', true);
  const roomId = window.__a3dCreateRoomAt([3,2], 0);
  window.__a3dSetGraphicsOverride(roomId, 'presentation', 'fill', '#88ccee');
  window.__a3dSetGraphicsOverride(roomId, 'presentation', 'lineColor', '#003366');
  return window.__a3dResolveGraphics(roomId, 'presentation');
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
        check(r.get("marker") is not None, "V59 marker present")
        check(r.get("hasApi"), "all Phase 51 test hooks present")

        print("\n== fresh type defaults, well-formed ==")
        r = await pg.evaluate(PROBE_TYPE_DEFAULTS)
        tg = r.get("typeGfx") or {}
        for mode in ("technical", "presentation"):
            m = tg.get(mode) or {}
            check(m.get("lineWeight") == 0.25, "%s default lineWeight is 0.25 (%r)" % (mode, m.get("lineWeight")))
            check(m.get("lineColor") == "#000000", "%s default lineColor is #000000 (%r)" % (mode, m.get("lineColor")))
            check(m.get("fill") == "none", "%s default fill is 'none' (%r)" % (mode, m.get("fill")))
            check(m.get("pattern") == "none", "%s default pattern is 'none' (%r)" % (mode, m.get("pattern")))
            check(m.get("opacity") == 1, "%s default opacity is 1 (%r)" % (mode, m.get("opacity")))
            check(m.get("shadow") is False, "%s default shadow is false (%r)" % (mode, m.get("shadow")))
        rt = r.get("resolvedTech") or {}
        check(rt.get("lineWeight") == 0.25 and rt.get("lineColor") == "#000000",
              "a wall with no edits resolves to the untouched type default")

        print("\n== type-level edit propagates to every instance of that type ==")
        r = await pg.evaluate(PROBE_TYPE_EDIT_PROPAGATES)
        check(close(r["a"]["lineWeight"], 0.5), "wall A picks up the new shared lineWeight (%r)" % r["a"]["lineWeight"])
        check(r["a"]["lineColor"] == "#ff0000", "wall A picks up the new shared lineColor")
        check(close(r["b"]["lineWeight"], 0.5) and r["b"]["lineColor"] == "#ff0000",
              "wall B (same type, never touched directly) picks up the SAME shared edit")
        check(r["aPres"]["lineColor"] == "#000000",
              "presentation mode is untouched by a technical-mode type edit (mode independence)")

        print("\n== instance override wins over type default, scoped to one instance and one field ==")
        r = await pg.evaluate(PROBE_INSTANCE_OVERRIDE_PRECEDENCE)
        check(r["a"]["lineColor"] == "#00ff00", "wall A's overridden lineColor wins over the type default")
        check(close(r["a"]["lineWeight"], 0.5),
              "wall A's NON-overridden lineWeight still inherits from the type (%r)" % r["a"]["lineWeight"])
        check(r["b"]["lineColor"] == "#ff0000",
              "wall B (same type, no override of its own) is unaffected by wall A's override -- no leakage")

        print("\n== reset to type: single field vs whole mode, and mode isolation ==")
        r = await pg.evaluate(PROBE_RESET_TO_TYPE)
        check(r["beforeClearField"]["lineColor"] == "#00ff00", "override is in effect before any reset")
        check(r["afterClearField"]["lineColor"] == "#ff0000",
              "clearing just the lineColor field reverts it to the type default (#ff0000)")
        check(r["afterClearField"]["shadow"] is True,
              "clearing lineColor did NOT clear the separate shadow override on the same mode")
        check(r["presStillOverridden"]["shadow"] is True,
              "the presentation-mode shadow override is untouched by a technical-mode field clear")
        check(r["afterClearMode"]["shadow"] is False,
              "clearing the whole technical mode reverts shadow to the type default too")
        check(r["presUnaffectedByModeClear"]["shadow"] is True,
              "clearing the technical mode entirely left the presentation mode's own override alone")

        print("\n== fail-safe: corrupted project file sanitizes on import, no page errors ==")
        r = await pg.evaluate(PROBE_BUILD_SCENE_FOR_CORRUPTION)
        env = json.loads(r["envelope"])
        wall_id = r["wallId"]
        wt = None
        for t in env["data"]["types"]["wall"]:
            if t["id"] == "wt-gen300":
                wt = t
        check(wt is not None, "wt-gen300 present in the exported envelope to corrupt")
        if wt is not None:
            wt["graphics"] = {
                "technical": {"lineWeight": -5, "lineColor": "not-a-color", "fill": 12345,
                              "pattern": "bogus-pattern", "opacity": 99, "shadow": "yes"},
                "presentation": "not-even-an-object"
            }
        # Also corrupt the instance-level override on the wall object itself.
        for o in env["data"]["objs"]:
            if o.get("id") == wall_id:
                o["graphicsOverride"] = "not-an-object-either"
        corrupted_text = json.dumps(env)
        r2 = await pg.evaluate(PROBE_IMPORT_CORRUPTED, corrupted_text)
        check(r2.get("ok") is True, "corrupted project file still imports successfully (does not hard-fail)")
        r3 = await pg.evaluate(PROBE_READ_AFTER_CORRUPT_IMPORT, {"typeId": "wt-gen300", "wallId": wall_id})
        tgc = (r3.get("typeGfx") or {}).get("technical") or {}
        check(tgc.get("lineWeight") == 0.25, "negative lineWeight replaced with the safe default (%r)" % tgc.get("lineWeight"))
        check(tgc.get("lineColor") == "#000000", "non-hex lineColor replaced with the safe default (%r)" % tgc.get("lineColor"))
        check(tgc.get("fill") == "none", "non-string fill replaced with 'none' (%r)" % tgc.get("fill"))
        check(tgc.get("pattern") == "none", "unknown pattern name replaced with 'none' (%r)" % tgc.get("pattern"))
        check(tgc.get("opacity") == 1, "opacity 99 was clamped/rejected back to 1 (%r)" % tgc.get("opacity"))
        check(tgc.get("shadow") is False, "wrong-typed shadow ('yes') replaced with false (%r)" % tgc.get("shadow"))
        tgp = (r3.get("typeGfx") or {}).get("presentation") or {}
        check(tgp.get("lineWeight") == 0.25 and tgp.get("lineColor") == "#000000",
              "a presentation dict that was a bare string is replaced wholesale with safe defaults")
        resolved_after = r3.get("resolved") or {}
        check(resolved_after.get("lineWeight") == 0.25 and resolved_after.get("lineColor") == "#000000",
              "resolving the wall whose graphicsOverride was a bare string falls back to type/default cleanly")

        print("\n== persistence round trip: type edit AND instance override both survive export/import ==")
        r = await pg.evaluate(PROBE_ROUNDTRIP_SETUP)
        before, beforePres = r["before"], r["beforePres"]
        check(close(before["lineWeight"], 0.7), "instance override in place before round trip")
        check(beforePres["fill"] == "#b7ab98" and beforePres["pattern"] == "diagonal",
              "type-level presentation edits in place before round trip")
        r2 = await pg.evaluate(PROBE_ROUNDTRIP_RELOAD, r["envelope"])
        check(r2.get("ok") is True, "project file re-imports successfully")
        r3 = await pg.evaluate(PROBE_ROUNDTRIP_READ, r["wallId"])
        check(close(r3["tech"]["lineWeight"], 0.7),
              "instance-level lineWeight override survived the export/import round trip (%r)" % r3["tech"]["lineWeight"])
        check(r3["pres"]["fill"] == "#b7ab98" and r3["pres"]["pattern"] == "diagonal",
              "type-level presentation fill/pattern edits survived the export/import round trip")

        print("\n== opacity clamps into [0,1] on read ==")
        r = await pg.evaluate(PROBE_OPACITY_CLAMP)
        check(r["high"] == 1, "opacity 5 clamps down to 1 (%r)" % r["high"])
        check(r["low"] == 0, "opacity -3 clamps up to 0 (%r)" % r["low"])

        print("\n== invalid (non-hex) color override is rejected, falls back cleanly ==")
        r = await pg.evaluate(PROBE_INVALID_COLOR_REJECTED)
        check(r.get("lineColor") == "#000000", "'red' is not #rrggbb, so it never overrides the default (%r)" % r.get("lineColor"))

        print("\n== instance override works on an object with no type system (a Room) ==")
        r = await pg.evaluate(PROBE_NONTYPED_OBJECT)
        check(r.get("fill") == "#88ccee", "room's overridden fill resolves correctly with no type to inherit from")
        check(r.get("lineColor") == "#003366", "room's overridden lineColor resolves correctly")
        check(r.get("lineWeight") == 0.25, "room's NON-overridden lineWeight falls back to the hard default (no type at all)")

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
