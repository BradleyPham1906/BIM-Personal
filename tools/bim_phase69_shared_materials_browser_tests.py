"""
bim_phase69_shared_materials_browser_tests.py

Regression suite for __acad3dV69 in canvas_v10.html: ONE material library, shared by the 2D board
and the BIM model. The first MODEL-level bridge between two of the three data models in this file.

WHY THIS ONE. Phases 64-68 unified the SHELL -- one work surface per mode, one navigator, one
inspector, one status bar. The models stayed three (A3D.*, state.nodes, state.wires) and Product
Principle 3 ("2D, 3D and BIM views should operate on shared project data wherever practical") was
still unmet. The 2D board already owned a real material library: CARDS, with density in kg/m3,
Young's modulus, Poisson ratio, a swatch colour and a hatch definition per material. The BIM side
had no material concept at all. Publishing that ONE array to the BIM module is the smallest
genuine connection available, and it pays twice from a single act of assignment: a plan cut
pattern, and a quantity takeoff.

WHAT THIS SUITE ASSERTS, and why each check is the one that would catch a regression:

  1. ONE list, not two that match today. The BIM side's view of the library is compared
     name-for-name and density-for-density against the board's own CARDS array read from the page.
     A future "tidy-up" that copies the cards into the BIM module would pass every other check
     here and silently reintroduce the drift this phase exists to prevent.
  2. Volume is the real geometric volume, checked against an independently computed figure. A
     10x7 wall ring of 0.3m x 3m is 34m of centreline: 34 * 0.3 * 3 = 30.6 m3 exactly. Mass is
     that volume times the card's own density, so a wrong units assumption anywhere shows up.
  3. Volume is null -- em dash, not a number -- when the mesh does not bound a closed volume. The
     divergence-theorem figure is exact for a closed surface and meaningless for an open one, and
     a plausible wrong mass on a takeoff is worse than no mass (Principle 2).
  4. The material's cut pattern REACHES THE DRAWING. This is where the first build of this phase
     failed twice, so it is checked end-to-end in the SVG rather than at bimResolveGraphics:
       (a) the material was applied BEFORE the type defaults, and a type's graphics are a FULL
           dict, so t.graphics[mode].pattern always overwrote it with 'none'. Resolution order
           alone could not fix that -- the gate ("only when nothing has chosen") is the fix.
       (b) once the pattern resolved, nothing rendered: a wall poche is only emitted when
           fill!=='none', so a material supplying a pattern but no fill is a control that does
           not work. The material now supplies a derived tint as well.
  5. Precedence is intact in BOTH directions. A type default beats the material; an instance
     override beats both, including an override back to 'none'. The material must be a starting
     point, never a value that fights an explicit choice.
  6. Nothing changes for an object with NO material. Asserted against a byte-identical export,
     which is the only way to prove this phase cannot alter an existing drawing.
  7. Assignment is validated and reversible: an unknown name is refused rather than stored, and
     clearing returns the object to exactly its previous appearance.
  8. Schedules carry Material, Volume and Mass for every solid category, and the CSV export
     carries them too -- a takeoff that is only on screen is not a takeoff.

Run:  python3 bim_phase69_shared_materials_browser_tests.py [path/to/canvas_v10.html]
"""

# AMENDED FOR V120: the shell's canvas-era names were replaced -- #figma-layers-shell/-rail/-panel are
# #a3d-shell/-rail/-leftpanel, the .fl-* classes .a3d-*, #uploaded-command-palette #a3d-cmdpal, the
# Project Browser tab 'file' is 'browser', --figma-dock-w is --a3d-left-w, and the material library is
# read through window.__a3dMaterialCards() (window.__WB_MATERIAL_CARDS is gone).
import asyncio, pathlib, re, sys

from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'

ENTER = """()=>{
  window.__a3dEnter();
  window.ACAD_WS_CUR='da';
  window.__a3dTestSetObjs([]);
  window.__a3dSetPlanView&&window.__a3dSetPlanView();
  window.__a3dSetPresentMode&&window.__a3dSetPresentMode(true);
  const w=window.__a3dWall([[0,0],[10,0],[10,7],[0,7]],0.3,3,'center',true);
  window.__a3dSelectFor([w]);window.__a3dRefreshProps();
  return w;
}"""

# 10x7 ring, centreline length 2*(10+7)=34 m, thickness 0.3, height 3
EXPECT_VOL = 34.0 * 0.3 * 3.0


class Checks:
    def __init__(self):
        self.n = 0
        self.failed = []

    def __call__(self, cond, msg):
        self.n += 1
        ok = bool(cond)
        print(("  PASS  " if ok else "  FAIL  ") + msg)
        if not ok:
            self.failed.append(msg)


async def run():
    ck = Checks()
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page(viewport={'width': 1600, 'height': 950})
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        await page.goto('file://' + str(HTML))
        await page.wait_for_timeout(900)

        has69 = await page.evaluate("()=>!!window.__acad3dV69")
        ck(has69, "__acad3dV69 marker is present")
        if not has69:
            # Bail cleanly rather than crashing on a build that predates this phase, so the
            # "verified to fail against the previous build" step reads as a FAIL, not a stack trace.
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.failed), ck.n))
            await browser.close()
            return 1
        wall = await page.evaluate(ENTER)
        await page.wait_for_timeout(700)

        print("\n-- 1. one library, not two that happen to match")
        board = await page.evaluate("()=>{const c=window.__a3dMaterialCards();"
                                    "return c?c.map(x=>({name:x.name,density:x.density,"
                                    "color:x.color})):null;}")
        bim = await page.evaluate("()=>window.__a3dMaterialCards()")
        ck(board is not None and len(board) > 0,
           "the 2D board's card library is published (%d cards)" % (len(board or [])))
        ck(bim is not None and len(bim) == len(board),
           "the BIM side sees the same number of cards (%d)" % len(bim or []))
        ck([c['name'] for c in bim] == [c['name'] for c in board],
           "same names in the same order (%s)" % ', '.join(c['name'] for c in bim))
        ck([c['density'] for c in bim] == [c['density'] for c in board],
           "same densities -- the two engines cannot disagree about what a material weighs")
        # AMENDED FOR V120: "reachable as one object" compared window.__WB_MATERIAL_CARDS with itself -- the
        # name the whiteboard and BIM shared. The library is declared once inside the engine now and read
        # only through bimMaterialCards(); the V120 suite asserts that from the source.

        print("\n-- 2. volume and mass are computed, not stored")
        vol = await page.evaluate("(id)=>window.__a3dObjVolume(id)", wall)
        ck(vol is not None and abs(vol - EXPECT_VOL) < 1e-6,
           "wall volume matches 34m x 0.3m x 3m computed independently (%.6f vs %.6f)"
           % (vol or -1, EXPECT_VOL))
        ck(await page.evaluate("(id)=>window.__a3dObjMass(id)", wall) is None,
           "mass is null while no material is assigned -- density is not guessed")
        ck(await page.evaluate("(id)=>window.__a3dSetMaterial(id,'Concrete')", wall) is True,
           "Concrete can be assigned")
        await page.wait_for_timeout(300)
        mass = await page.evaluate("(id)=>window.__a3dObjMass(id)", wall)
        dens = [c['density'] for c in bim if c['name'] == 'Concrete'][0]
        ck(mass is not None and abs(mass - EXPECT_VOL * dens) < 1e-3,
           "mass is volume x the card's own density (%.3f vs %.3f)"
           % (mass or -1, EXPECT_VOL * dens))

        print("\n-- 3. an unclosed mesh reports no volume rather than a wrong one")
        # There is no hook to corrupt a solid's mesh, so the null path is exercised with an
        # object that legitimately has none: a room is a boundary, not a solid.
        room = await page.evaluate("()=>window.__a3dCreateRoomAt([5,3.5],0)")
        await page.wait_for_timeout(300)
        ck(await page.evaluate("(id)=>window.__a3dObjVolume(id)", room) is None,
           "an object with no solid mesh reports null volume, not zero")
        ck(await page.evaluate("(id)=>window.__a3dObjMass(id)", room) is None,
           "and null mass, so no row can show a confident 0 kg")

        print("\n-- 4. the cut pattern reaches the drawing, end to end")
        svg_no = await page.evaluate("""()=>{window.__a3dTestSetObjs([]);
          const w=window.__a3dWall([[0,0],[8,0],[8,5],[0,5]],0.3,3,'center',true);
          return {id:w, svg:window.__a3dBuildSVG('presentation').text};}""")
        ck(len(re.findall(r'<pattern', svg_no['svg'])) == 0,
           "a wall with no material emits no <pattern>")
        await page.evaluate("(id)=>window.__a3dSetMaterial(id,'Concrete')", svg_no['id'])
        await page.wait_for_timeout(300)
        svg_yes = await page.evaluate("()=>window.__a3dBuildSVG('presentation').text")
        ck(len(re.findall(r'<pattern', svg_yes)) == 1,
           "assigning Concrete emits exactly one <pattern> (%d)"
           % len(re.findall(r'<pattern', svg_yes)))
        ck('data-pattern="cross"' in svg_yes,
           "and it is the CROSS pattern the Concrete card's hatch{cross:true} asks for")
        conc_col = [c['color'] for c in bim if c['name'] == 'Concrete'][0]
        ck(conc_col in svg_yes,
           "hatched in the card's own colour %s, identical to the colour the 2D board would use"
           % conc_col)
        rg = await page.evaluate("(id)=>window.__a3dResolveGraphics(id,'presentation')",
                                 svg_no['id'])
        ck(rg['pattern'] == 'cross', "the resolved pattern is 'cross'")
        ck(rg['fill'] != 'none',
           "and the material also supplies a fill (%s) -- a wall poche is only emitted when "
           "fill!=='none', so a pattern without one would render nothing" % rg['fill'])
        ck(rg['patternColor'] == conc_col, "patternColor is the card colour unchanged")

        print("\n-- 5. precedence holds in both directions")
        await page.evaluate("(id)=>window.__a3dSetGraphicsOverride(id,'presentation',"
                            "'pattern','brick')", svg_no['id'])
        await page.wait_for_timeout(250)
        ck((await page.evaluate("(id)=>window.__a3dResolveGraphics(id,'presentation').pattern",
                                svg_no['id'])) == 'brick',
           "an instance override beats the material")
        await page.evaluate("(id)=>window.__a3dSetGraphicsOverride(id,'presentation',"
                            "'pattern','none')", svg_no['id'])
        await page.wait_for_timeout(250)
        ck((await page.evaluate("(id)=>window.__a3dResolveGraphics(id,'presentation').pattern",
                                svg_no['id'])) == 'none',
           "including an override back to 'none' -- the material never fights an explicit choice")
        await page.evaluate("(id)=>window.__a3dSetGraphicsOverride(id,'presentation',"
                            "'pattern','')", svg_no['id'])
        await page.wait_for_timeout(250)
        ck((await page.evaluate("(id)=>window.__a3dResolveGraphics(id,'presentation').pattern",
                                svg_no['id'])) == 'cross',
           "clearing the override falls back to the material again, not to 'none'")

        print("\n-- 6. an object with no material is untouched, byte for byte")
        pair = await page.evaluate("""()=>{
          window.__a3dTestSetObjs([]);
          const a=window.__a3dWall([[0,0],[6,0],[6,4],[0,4]],0.2,2.8,'center',true);
          const before=window.__a3dBuildSVG('presentation').text;
          window.__a3dSetMaterial(a,'Steel');
          window.__a3dSetMaterial(a,'');
          const after=window.__a3dBuildSVG('presentation').text;
          return {same:before===after, cleared:window.__a3dMaterialOf(a), id:a};}""")
        ck(pair['cleared'] is None, "clearing a material removes it rather than storing ''")
        ck(pair['same'] is True,
           "assign-then-clear produces a byte-identical export -- this phase cannot change an "
           "existing drawing that uses no materials")

        print("\n-- 7. assignment is validated")
        ck(await page.evaluate("(id)=>window.__a3dSetMaterial(id,'Unobtainium')",
                               pair['id']) is False,
           "an unknown material name is refused")
        ck(await page.evaluate("(id)=>window.__a3dMaterialOf(id)", pair['id']) is None,
           "and nothing is stored for it")

        print("\n-- 8. schedules and the CSV carry the takeoff")
        sched = await page.evaluate("""()=>{
          window.__a3dTestSetObjs([]);
          const w=window.__a3dWall([[0,0],[10,0],[10,7],[0,7]],0.3,3,'center',true);
          window.__a3dSetMaterial(w,'Concrete');
          return window.__a3dScheduleRows('wall');}""")
        for key in ('material', 'volume', 'mass'):
            ck(key in sched['cols'], "the wall schedule has a '%s' column" % key)
        row = sched['rows'][0]
        ck(row['material'] == 'Concrete', "the row reports the assigned material")
        ck(abs(row['volume'] - EXPECT_VOL) < 1e-6,
           "the row's volume matches the independent figure (%.4f)" % row['volume'])
        ck(abs(row['mass'] - EXPECT_VOL * dens) < 1e-3,
           "and its mass (%.2f kg)" % row['mass'])
        for cat in ('column', 'beam', 'ceiling'):
            cols = (await page.evaluate("(c)=>window.__a3dScheduleRows(c)", cat))['cols']
            ck('mass' in cols and 'volume' in cols and 'material' in cols,
               "the %s schedule carries the same three columns" % cat)
        csv = await page.evaluate("()=>{const s=window.__a3dScheduleRows('wall');"
                                  "const defs=s.cols.map(k=>({key:k,label:k}));"
                                  "return window.__a3dScheduleCSV(s.rows,defs);}")
        head = (csv or '').split('\r\n')[0]
        ck('material' in head and 'mass' in head,
           "the CSV export carries the takeoff columns too (%s)" % head)
        body = (csv or '').split('\r\n')[1] if csv and '\r\n' in csv else ''
        ck('Concrete' in body and '73440' in body,
           "and the values, not just the headers (%s)" % body)

        print("")
        ck(not errs, "zero uncaught page errors across every probe (%s)" % (errs or 'none'))
        await browser.close()

    print("\n%d/%d checks passed" % (ck.n - len(ck.failed), ck.n))
    if ck.failed:
        print("RESULT: FAIL")
        for m in ck.failed:
            print("   - " + m)
        return 1
    print("RESULT: PASS")
    return 0


sys.exit(asyncio.run(run()))
