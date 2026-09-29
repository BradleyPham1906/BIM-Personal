"""
bim_phase74_schedule_registry_browser_tests.py

Regression suite for __acad3dV74 in canvas_v10.html: schedules become a registry, and the Beams
schedule becomes reachable.

THE BUG THIS PHASE FOUND. SCHEDULE_DEFS carried seven schedules. The Project Browser listed six:

    var schedKeys=['room','door','window','wall','ceiling','column'];    // no 'beam'

and the only other chooser, #a3d-schedcat, is display:none. So the Beams schedule was built,
columned and CSV-exportable, with no way for a user to open it. A tool that exists but cannot be
reached is the same failure as one that does not work (Product Principle 1).

There were THREE hand-kept lists, and they had already drifted apart from each other:

    Project Browser      6 entries   (no beam)
    the hidden select    7 entries
    sheet viewport sources 7 entries

All three now derive from SCHEDULE_DEFS, which fixes the class rather than the instance and is the
same change that makes __a3dRegisterSchedule possible.

A SECOND GAP, found by writing the proof rather than by reading the code: a registered schedule's
build() has to ENUMERATE the model, and nothing exposed it -- only __a3dObjSnapshot(id), which
needs an id you do not have yet. The bridge girder takeoff written for this suite had nothing to
iterate. __a3dObjects() was added, returning snapshots rather than live objects: a schedule is a
read, and handing out live references would let a takeoff quietly mutate the model it measures.

WHAT THIS SUITE ASSERTS, and why each check is the one that would catch a regression:

  1. Every registered schedule is REACHABLE, asserted by comparing the registry against what the
     Project Browser actually rendered. That comparison is the bug: a registry and a rendered list
     that disagree. Checking the registry alone would have passed on the broken build.
  2. Beams specifically opens, since that is the schedule that was stranded.
  3. A whole domain takeoff registers at runtime through the public API, appears in the browser,
     opens, produces correct rows, and is placeable on a SHEET -- a takeoff that cannot reach a
     drawing set is half a feature.
  4. Its numbers are right, checked against independently computed values, and its material
     columns come from the same BIM_MAT_COLS the built-in schedules use rather than a parallel set
     that would format differently.
  5. Registration is validated: no build function, or no columns, is refused rather than producing
     a browser entry that throws when opened.
  6. The CSV export carries a registered schedule too.

Run:  python3 bim_phase74_schedule_registry_browser_tests.py [path/to/canvas_v10.html]
"""

import asyncio, pathlib, sys

from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'

SETUP = """()=>{
  window.__a3dTestSetObjs([]);
  window.__a3dWall([[0,0],[12,0],[12,8],[0,8]],0.3,3,'center',true);
  const b1=window.__a3dBeam([0,0],[12,0],0.3,0.6,'center');
  const b2=window.__a3dBeam([0,8],[12,8],0.3,0.6,'center');
  if(b1)window.__a3dSetMaterial(b1,'Steel');
  if(b2)window.__a3dSetMaterial(b2,'Steel');
  const g=document.querySelector('#a3d-browser [data-a3dbgrp="schedules"]');
  if(g)g.click();
  return {b1:b1,b2:b2};
}"""

# A bridge girder takeoff, registered through the PUBLIC API only. Nothing here edits
# SCHEDULE_DEFS, the browser list, the hidden select or the sheet source list.
REGISTER = """()=>{
  return window.__a3dRegisterSchedule({
    id:'girder', label:'Girders',
    cols:[{key:'name',label:'Mark'},{key:'span',label:'Span (m)',fmt:2},
          {key:'depth',label:'Depth (m)',fmt:3}].concat(window.__a3dMaterialCols()),
    build:function(){
      return window.__a3dObjects()
        .filter(function(o){return o.bim&&o.bim.type==='beam';})
        .map(function(o){
          var extra=window.__a3dMaterialRowFor(o.id)||{};
          var row={name:o.name,span:o.bim.length,depth:o.bim.depth};
          for(var k in extra)if(extra.hasOwnProperty(k))row[k]=extra[k];
          return row;
        });
    }});
}"""


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
        # AMENDED FOR V128: a bound on every page call (V123's rule, which this suite predates). One
        # full regression run stalled here for its whole 900 s with the page idle, and six repeats
        # did not reproduce it; a stall now fails at once and says which call it was in.
        def bounded(f, nm):
            async def g(*a, **k):
                try:
                    return await asyncio.wait_for(f(*a, **k), 60)
                except asyncio.TimeoutError:
                    raise RuntimeError('stalled 60 s in page.%s %s' % (nm, str(a[:1])[:60]))
            return g
        for nm in ('goto', 'evaluate', 'wait_for_timeout'):
            setattr(page, nm, bounded(getattr(page, nm), nm))
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        await page.goto('file://' + str(HTML))
        await page.wait_for_timeout(1700)

        has74 = await page.evaluate("()=>!!window.__acad3dV74")
        ck(has74, "__acad3dV74 marker is present")
        if not has74:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.failed), ck.n))
            await browser.close()
            return 1

        ids = await page.evaluate(SETUP)
        await page.wait_for_timeout(800)

        print("\n-- 1. the registry and the rendered list agree")
        keys = await page.evaluate("()=>window.__a3dScheduleKeys()")
        shown = await page.evaluate("()=>window.__a3dBrowserSchedules()")
        shown_keys = [s['key'] for s in shown]
        # __acad3dV102: this counted exactly seven; later phases add schedules by design
        # (V102: Isolated Footings, Wall Foundations). What V74 claims is that the seven it
        # found are all still registered -- a subset, not a count that forbids growth.
        base7 = ['room', 'door', 'window', 'wall', 'ceiling', 'column', 'beam']
        ck(all(k in keys for k in base7) and len(set(keys)) == len(keys),
           "the seven V74 schedules all still ship, none twice (%s)" % keys)
        ck(shown_keys == keys,
           "the Project Browser lists exactly what the registry holds -- before this phase it "
           "listed six of seven (browser: %s)" % shown_keys)
        ck('beam' in shown_keys,
           "Beams is among them; it was the one stranded by the hardcoded list")

        print("\n-- 2. every listed schedule actually opens")
        for k in keys:
            ok = await page.evaluate("(c)=>window.__a3dOpenSchedule(c)", k)
            ck(ok is True, "'%s' opens from the browser" % k)

        print("\n-- 3. a domain takeoff registers at runtime and reaches everything")
        ck(await page.evaluate(REGISTER) is True,
           "a bridge Girders schedule registers through the public API alone")
        await page.wait_for_timeout(500)
        keys2 = await page.evaluate("()=>window.__a3dScheduleKeys()")
        shown2 = [s['key'] for s in await page.evaluate("()=>window.__a3dBrowserSchedules()")]
        ck('girder' in keys2, "it is in the registry")
        ck('girder' in shown2,
           "and in the Project Browser with no edit to any list (%s)" % shown2)
        ck(shown2 == keys2, "the two still agree after registration")
        ck(await page.evaluate("()=>window.__a3dOpenSchedule('girder')") is True,
           "it opens -- the hidden select picked up the new option")
        sources = await page.evaluate("""()=>window.__a3dSheetSourceOptions()
          .filter(function(s){return s.kind==='schedule';}).map(function(s){return s.refId;})""")
        ck('girder' in sources,
           "and it can be placed on a sheet (%s) -- a takeoff that cannot reach a drawing set is "
           "half a feature" % sources)

        print("\n-- 4. its numbers and columns are right")
        sch = await page.evaluate("()=>window.__a3dScheduleRows('girder')")
        ck(len(sch['rows']) == 2, "both beams are in it (%d rows)" % len(sch['rows']))
        row = sch['rows'][0]
        ck(abs(row['span'] - 12.0) < 1e-6,
           "the span matches the 12m beam it was built from (%s)" % row['span'])
        ck(abs(row['depth'] - 0.6) < 1e-6, "and the depth (%s)" % row['depth'])
        ck(row.get('material') == 'Steel',
           "the material assigned to it comes through (%s)" % row.get('material'))
        ck(row.get('volume') is not None and row['volume'] > 0,
           "with a real volume (%s)" % row.get('volume'))
        dens = await page.evaluate("""()=>{const c=window.__a3dMaterialCards()
          .filter(function(x){return x.name==='Steel';})[0];return c?c.density:null;}""")
        ck(row.get('mass') is not None
           and abs(row['mass'] - row['volume'] * dens) < 1e-3,
           "and a mass that is volume x the Steel card's own density (%s)" % row.get('mass'))
        matcols = await page.evaluate("()=>window.__a3dMaterialCols().map(c=>c.key)")
        ck(all(k in sch['cols'] for k in matcols),
           "its takeoff columns are the shared ones (%s), not a parallel set that would round "
           "differently" % matcols)
        ck(await page.evaluate("""()=>{const a=window.__a3dMaterialCols();
          a.push({key:'tampered'}); return window.__a3dMaterialCols().length;}""") == len(matcols),
           "and the published column list is a copy -- a caller cannot mutate the app's own")

        print("\n-- 5. registration is validated")
        ck(await page.evaluate("()=>window.__a3dRegisterSchedule({id:'x',label:'X'})") is False,
           "a schedule with no build function is refused")
        ck(await page.evaluate("()=>window.__a3dRegisterSchedule({id:'y',build:function(){return [];}})")
           is False,
           "and one with no columns -- either would render a browser entry that throws when opened")
        ck(await page.evaluate("()=>window.__a3dScheduleKeys().indexOf('x')") == -1,
           "neither reaches the registry")

        print("\n-- 6. the CSV export carries a registered schedule")
        csv = await page.evaluate("""()=>{const s=window.__a3dScheduleRows('girder');
          const defs=s.cols.map(function(k){return {key:k,label:k};});
          return window.__a3dScheduleCSV(s.rows,defs);}""")
        head = (csv or '').split('\r\n')[0]
        body = (csv or '').split('\r\n')[1] if csv and '\r\n' in csv else ''
        ck('span' in head and 'mass' in head, "the header carries its columns (%s)" % head)
        ck('Steel' in body, "and the rows carry the values (%s)" % body)

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
