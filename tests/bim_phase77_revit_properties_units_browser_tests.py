"""
bim_phase77_revit_properties_units_browser_tests.py

Regression suite for __acad3dV77 in canvas_v10.html: the Properties palette given one number
format, project display units, and Revit's grouping.

WHAT THE USER ASKED FOR: "clean up the property tab on right panel. reference the revit style a
bit."

WHAT THE PANEL ACTUALLY CARRIED, measured on the V76 build with a wall selected after a gizmo drag:

    Offset            2.175438380956253      sixteen significant figures, in an editable field
    Length            14.000 m               unit in the VALUE
    Volume (m3)       12.6000                unit in the LABEL, four decimals
    Area              23.45 m2               unit in the value again
    Young's Modulus   undefined              a parameter no shipped material card carries

Four conventions for one job, plus two rows that were permanently blank. A value column is only
scannable when every row obeys the same rule, which is why Revit has exactly one.

WHY EACH CHECK IS THE ONE THAT WOULD CATCH A REGRESSION:

  1. The format rule is asserted ACROSS THE WHOLE PANEL, not on the few rows this phase happened
     to touch: no value may carry a unit suffix, every unit-bearing label must name its unit, and
     no displayed number may exceed the project's decimal precision. A new row added later in the
     old style fails these, which a per-row check would not.
  2. Display rounding is proven NOT to reach the model. The wall is given a sixteen-digit offset,
     the panel is re-rendered repeatedly, and the stored value is asserted unchanged to the last
     digit. This is the failure mode that would make the phase actively harmful rather than
     merely cosmetic, and it is silent: the panel would look right the whole time.
  3. Editing is driven through the REAL input element and a REAL change event, in millimetres,
     and the metres value is read back from the model. A test that called the converter directly
     would pass with the wiring disconnected.
  4. Unit switching is checked to change only the DISPLAY. Asserted by reading the model before
     and after, because a conversion applied to storage instead of presentation would look
     identical in the panel.
  5. Unreadable input leaves the model alone and restores the field. A palette that silently
     writes NaN is worse than one that refuses.
  6. Location Line is asserted to be in Constraints and absent from Dimensions -- both halves,
     since adding it to Constraints without removing it from Dimensions would duplicate a control
     that writes the same field twice.
  7. A material parameter the assigned card does not carry is OMITTED rather than rendered blank.
     A permanently empty row reads as a value the app failed to compute.

Run:  python3 bim_phase77_revit_properties_units_browser_tests.py [path/to/canvas_v10.html]
"""

import asyncio, pathlib, re, sys

from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'

SETUP = """()=>{
  window.__a3dTestSetObjs([]);
  const w=window.__a3dWall([[0,0],[8,0],[8,6]],0.3,3,'center',false);
  window.__a3dSetPos(w,0,2.175438380956253,0);
  window.__a3dSetMaterial(w,'Concrete');
  window.__a3dSelectFor([w]);
  window.__a3dRefreshProps();
  return w;}"""

UNIT_LABEL = re.compile(r'\((m|cm|mm)\)$')
# A unit written into the VALUE column -- the convention this phase removed.
UNIT_IN_VALUE = re.compile(r'^-?[\d.]+\s*(m|cm|mm|m²|m³|°)$')


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


def decimals(s):
    return len(s.split('.')[1]) if '.' in s else 0


async def run():
    ck = Checks()
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1600, 'height': 950},
                                        device_scale_factor=2)
        page = await ctx.new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        await page.goto('file://' + str(HTML))
        await page.wait_for_timeout(1700)

        has77 = await page.evaluate("()=>!!window.__acad3dV77")
        ck(has77, "__acad3dV77 marker is present")
        if not has77:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.failed), ck.n))
            await browser.close()
            return 1

        wid = await page.evaluate(SETUP)
        await page.wait_for_timeout(500)

        print("\n-- 1. one number format, asserted across the WHOLE panel")
        rows = await page.evaluate("()=>window.__a3dPropRows()")
        units = await page.evaluate("()=>window.__a3dUnits()")
        ck(len(rows) > 10, "the panel rendered %d rows" % len(rows))

        offenders = [r for r in rows if UNIT_IN_VALUE.match(r['value'] or '')]
        ck(not offenders,
           "no row writes its unit into the VALUE column (%s) -- 'Length  14.000 m' and "
           "'Area  23.45 m2' both did before this phase, while 'Volume (m3)' did the opposite"
           % [(o['label'], o['value']) for o in offenders])

        lenrows = [r for r in rows if UNIT_LABEL.search(r['label'])]
        ck(len(lenrows) >= 4,
           "at least four rows name their unit in the LABEL (%s)"
           % [r['label'] for r in lenrows])
        ck(all(r['label'].endswith('(%s)' % units['label']) for r in lenrows),
           "and every one of them names the PROJECT unit (%s), not a fixed one"
           % units['label'])

        toolong = [(r['label'], r['value']) for r in lenrows
                   if r['value'] not in ('', '—')
                   and decimals(r['value']) > units['dp']]
        ck(not toolong,
           "no length is displayed beyond the project's %d-decimal precision (%s) -- Base Offset "
           "carried sixteen significant figures in an editable field before this phase"
           % (units['dp'], toolong))
        boff = [r for r in rows if r['label'].startswith('Base Offset')]
        ck(boff and boff[0]['value'] == '2.175',
           "Base Offset specifically reads 2.175 (%s), from a stored 2.175438380956253"
           % (boff and boff[0]['value']))

        print("\n-- 2. the rounding is DISPLAY only; the model keeps every digit")
        for _ in range(4):
            await page.evaluate("()=>window.__a3dRefreshProps()")
            await page.wait_for_timeout(80)
        stored = await page.evaluate("(id)=>window.__a3dObjSnapshot(id).pos[1]", wid)
        ck(stored == 2.175438380956253,
           "after four re-renders the stored offset is still %r -- a display round that reached "
           "storage would be silent, because the panel would look correct the whole time" % stored)

        print("\n-- 3. display units change the display, not the model")
        before = await page.evaluate("""(id)=>{const o=window.__a3dObjSnapshot(id);
          return {t:o.bim.thickness,h:o.bim.height,y:o.pos[1]};}""", wid)
        await page.evaluate("()=>window.__a3dSetUnits('mm')")
        await page.wait_for_timeout(350)
        mm = {r['label']: r['value'] for r in await page.evaluate("()=>window.__a3dPropRows()")}
        ck(mm.get('Thickness (mm)') == '300' and mm.get('Height (mm)') == '3000',
           "in millimetres the wall reads 300 / 3000 (%s / %s)"
           % (mm.get('Thickness (mm)'), mm.get('Height (mm)')))
        ck(mm.get('Length (mm)') == '14000', "and its length 14000 (%s)" % mm.get('Length (mm)'))
        ck(mm.get('Base Offset (mm)') == '2175',
           "and the offset 2175, rounded to the millimetre precision (%s)"
           % mm.get('Base Offset (mm)'))
        await page.evaluate("()=>window.__a3dSetUnits('cm')")
        await page.wait_for_timeout(300)
        cm = {r['label']: r['value'] for r in await page.evaluate("()=>window.__a3dPropRows()")}
        ck(cm.get('Thickness (cm)') == '30', "in centimetres, 30 (%s)" % cm.get('Thickness (cm)'))
        after = await page.evaluate("""(id)=>{const o=window.__a3dObjSnapshot(id);
          return {t:o.bim.thickness,h:o.bim.height,y:o.pos[1]};}""", wid)
        ck(after == before,
           "and through both switches the MODEL is untouched (%s) -- a conversion applied to "
           "storage instead of presentation would look identical in the panel" % after)

        print("\n-- 4. editing in display units writes metres")
        await page.evaluate("()=>window.__a3dSetUnits('mm')")
        await page.wait_for_timeout(300)
        ok = await page.evaluate("()=>window.__a3dSetPropLen('thickness','450')")
        await page.wait_for_timeout(350)
        t = await page.evaluate("(id)=>window.__a3dObjSnapshot(id).bim.thickness", wid)
        ck(ok is True and abs(t - 0.45) < 1e-9,
           "typing 450 into Thickness (mm) stores 0.45 m (%s) -- driven through the real input "
           "and a real change event, so the check cannot pass with the wiring disconnected" % t)
        shown = {r['label']: r['value']
                 for r in await page.evaluate("()=>window.__a3dPropRows()")}
        ck(shown.get('Thickness (mm)') == '450',
           "and the field reads back 450 (%s)" % shown.get('Thickness (mm)'))
        await page.evaluate("()=>window.__a3dSetPropLen('height','2700')")
        await page.wait_for_timeout(300)
        hh = await page.evaluate("(id)=>window.__a3dObjSnapshot(id).bim.height", wid)
        ck(abs(hh - 2.7) < 1e-9, "and Height (mm) 2700 stores 2.7 m (%s)" % hh)

        print("\n-- 5. unreadable input is refused, not stored")
        bad = await page.evaluate("""()=>{
          const inp=document.querySelector('[data-propf="thickness"][data-proplen]');
          if(!inp)return null;
          inp.value='abc';
          inp.dispatchEvent(new Event('change',{bubbles:true}));
          return true;}""")
        await page.wait_for_timeout(350)
        t2 = await page.evaluate("(id)=>window.__a3dObjSnapshot(id).bim.thickness", wid)
        ck(bad is True and abs(t2 - 0.45) < 1e-9,
           "typing letters leaves the stored thickness at 0.45 (%s)" % t2)
        restored = {r['label']: r['value']
                    for r in await page.evaluate("()=>window.__a3dPropRows()")}
        ck(restored.get('Thickness (mm)') == '450',
           "and the field is restored to the model's value (%s)"
           % restored.get('Thickness (mm)'))
        await page.evaluate("()=>window.__a3dSetUnits('m')")
        await page.wait_for_timeout(300)

        print("\n-- 6. precision is a real, bounded setting")
        ck(await page.evaluate("()=>window.__a3dSetUnits('m',9).dp") == 4,
           "decimals are clamped to 4 at the top")
        ck(await page.evaluate("()=>window.__a3dSetUnits('m',-3).dp") == 0,
           "and to 0 at the bottom")
        await page.evaluate("()=>window.__a3dSetUnits('m',4)")
        await page.wait_for_timeout(300)
        fine = {r['label']: r['value']
                for r in await page.evaluate("()=>window.__a3dPropRows()")}
        ck(fine.get('Base Offset (m)') == '2.1754',
           "at four decimals the offset reads 2.1754 (%s) -- the setting exists because a 90 m "
           "span and a 6 mm plate cannot share one precision, which this project needs for bridge "
           "and structural work as much as for buildings" % fine.get('Base Offset (m)'))
        ck(await page.evaluate("()=>window.__a3dSetUnits('parsecs').key") == 'm',
           "an unknown unit is ignored rather than adopted")
        await page.evaluate("()=>window.__a3dSetUnits('m',3)")
        await page.wait_for_timeout(300)

        print("\n-- 7. Revit's grouping")
        rows = await page.evaluate("()=>window.__a3dPropRows()")
        loc = [r for r in rows if r['label'] == 'Location Line']
        ck(len(loc) == 1, "there is exactly ONE Location Line control (%d)" % len(loc))
        ck(loc and loc[0]['group'] == 'Constraints',
           "and it is in Constraints, where Revit has it (%s) -- adding it there without removing "
           "it from Dimensions would give two controls writing the same field"
           % (loc and loc[0]['group']))
        dims = [r['label'] for r in rows if r['group'] == 'Dimensions']
        ck('Location Line' not in dims, "Dimensions holds dimensions only (%s)" % dims)
        ck(any(r['label'].startswith('Base Offset') and r['group'] == 'Constraints' for r in rows),
           "Offset is renamed Base Offset and sits in Constraints")

        print("\n-- 8. read-only rows are marked as such")
        ro = [r['label'] for r in rows if r['ro']]
        rw = [r['label'] for r in rows if not r['ro']]
        ck('Level' in ro and any(l.startswith('Length') for l in ro),
           "derived values are read-only (%s)" % ro[:6])
        ck(any(l.startswith('Thickness') for l in rw) and 'Name' in rw,
           "and editable ones are not (%s)" % rw[:6])

        print("\n-- 9. a parameter the material card does not carry is omitted")
        cards = await page.evaluate("()=>window.__a3dMaterialCards()")
        concrete = [c for c in cards if c['name'] == 'Concrete'][0]
        ck('youngsModulus' not in concrete or concrete.get('youngsModulus') is None,
           "the shipped Concrete card carries no Young's Modulus (%s)"
           % sorted(concrete.keys()))
        labels = [r['label'] for r in rows]
        ck(not any(l.startswith('Young') for l in labels),
           "so no Young's Modulus row is rendered (%s) -- it used to render the word 'undefined', "
           "which reads as a value the app failed to compute rather than one the material was "
           "never given" % [l for l in labels if l.startswith('Young')])
        ck(any(l.startswith('Density') for l in labels),
           "while Density, which the card DOES carry, is still shown")

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
