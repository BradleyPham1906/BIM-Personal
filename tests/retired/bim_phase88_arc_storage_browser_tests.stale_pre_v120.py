"""
bim_phase88_arc_storage_browser_tests.py

Regression suite for __acad3dV88 in canvas_v10.html: arc storage, and ARC.

THE DECISION THIS SUITE DEFENDS: a polyline carries an optional `bulges` array parallel to
`pts`; bulges[i] describes the segment from pts[i] to pts[i+1]; 0 or absent means straight.
bulge = tan(sweep/4), positive = counter-clockwise. That is DXF group code 42.

The alternative was a segment-type array. The reason bulge won is that it DEGRADES GRACEFULLY:
every existing reader of a points array keeps working and sees the chord. So the most important
checks here are not about arcs at all - they are the ones asserting that a straight sketch is
still exactly the object it was before this phase (no bulges key, flatten returns it unchanged).
If those ever fail, the storage decision has stopped paying for itself.

WHY EACH CHECK IS THE ONE THAT WOULD CATCH A REGRESSION:

  1. ORIENTATION IS PINNED BY "THE ARC ENDS WHERE THE CHORD ENDS". A flipped perpendicular
     produces the right radius, the right centre distance and a plausible picture, and fails
     only this. The prototype had exactly that bug.
  2. THE 3-POINT ROUND TRIP. A bulge derived from three points must describe an arc that passes
     through the middle one, asserted with an exact angle-in-sweep test rather than by walking
     sampled points - the first version of that test sampled more coarsely than its own
     tolerance and reported a failure that was entirely its own.
  3. ARC IS ASSERTED TO STORE TWO VERTICES AND ONE BULGE, not a fan of chords. This is the
     storage decision itself. A tessellating ARC would draw identically and pass every
     appearance check.
  4. PICKING IS AIMED AT THE ARC AND AT ITS CHORD SEPARATELY. Picking on the chord used to work
     and picking on the curve used to fail; both are asserted, because only the pair proves the
     pick follows what is drawn.
  5. THE DXF ROUND TRIP, which is the second reason bulge was chosen: export, re-import, and the
     bulge must survive. Before this phase an imported ARC was tessellated on the way in and
     could never leave as an arc again.
  6. Zero uncaught page errors, and the V80 shell audit stays clean.

Run:  python3 bim_phase88_arc_storage_browser_tests.py [path/to/canvas_v10.html]
"""
import asyncio, math, pathlib, sys

from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'


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


def near(a, b, tol=1e-6):
    try:
        return abs(a - b) <= tol
    except TypeError:
        return False


async def palette_run(page, name):
    await page.keyboard.press('Control+k')
    await page.wait_for_timeout(320)
    await page.keyboard.type(name)
    await page.wait_for_timeout(200)
    await page.keyboard.press('Enter')
    await page.wait_for_timeout(400)


async def run():
    ck = Checks()
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1600, 'height': 950})
        page = await ctx.new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        await page.goto('file://' + str(HTML))
        await page.wait_for_timeout(2300)
        await page.mouse.click(800, 500)
        await page.wait_for_timeout(250)

        has88 = await page.evaluate("()=>!!window.__acad3dV88")
        ck(has88, "__acad3dV88 marker is present")
        if not has88:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.failed), ck.n))
            await browser.close()
            return 1

        # ---------------------------------------------------------------- 1. the arc core
        print("\n-- 1. bulge -> arc, on answers that can be computed by hand")
        a = await page.evaluate("()=>window.__a3dBulgeArc([0,0],[2,0],1)")
        ck(near(a['radius'], 1) and near(a['center'][0], 1) and near(a['center'][1], 0),
           "bulge +1 on a chord of 2 is a semicircle r=1 centred at (1,0) -> r=%s c=%s"
           % (a['radius'], a['center']))
        ck(near(a['sweep'], math.pi), "and sweeps +pi (counter-clockwise) -> %s" % a['sweep'])
        ck(near(a['apex'][1], -1),
           "a positive (CCW) bulge swells BELOW a left-to-right chord -> apex %s" % a['apex'])
        ck(await page.evaluate("()=>window.__a3dBulgeArc([0,0],[2,0],0)") is None,
           "bulge 0 is a straight segment, not an arc")

        # The check a flipped perpendicular fails and everything else passes.
        ends = await page.evaluate("""()=>{
          const cases=[[[0,0],[2,0],1],[[0,0],[2,0],-1],[[1,0],[0,1],Math.tan(Math.PI/8)],
                       [[3,-2],[-1,5],0.37],[[-4,1],[2,-6],-2.1]];
          return cases.map(([p1,p2,b])=>{
            const a=window.__a3dBulgeArc(p1,p2,b);
            if(!a)return 1e9;
            const x=a.center[0]+Math.cos(a.a2)*a.radius, y=a.center[1]+Math.sin(a.a2)*a.radius;
            return Math.max(Math.abs(x-p2[0]),Math.abs(y-p2[1]));
          });
        }""")
        ck(max(ends) < 1e-9,
           "the swept arc ENDS where the chord ends, for every chord and bulge (max error %.2e)"
           % max(ends))

        print("\n   3 points -> bulge -> arc through the middle point (exact, not sampled)")
        rt = await page.evaluate("""()=>{
          const cases=[[[0,0],[1,1],[2,0]],[[0,0],[1,-1],[2,0]],[[0,0],[0.3,1.4],[2,0]],
                       [[5,5],[2,9],[-4,4]],[[-3,-3],[0,-7],[4,-2]]];
          return cases.map(([p1,pm,p2])=>{
            const b=window.__a3dBulgeFrom3Pts(p1,pm,p2);
            const a=window.__a3dBulgeArc(p1,p2,b);
            return {b:b, on:!!a&&window.__a3dPointOnSweptArc(a,pm,1e-9)};
          });
        }""")
        ck(all(r['on'] for r in rt),
           "every 3-point arc passes through its own middle point (%s)"
           % [round(r['b'], 4) for r in rt])
        b_up = await page.evaluate("()=>window.__a3dBulgeFrom3Pts([0,0],[1,1],[2,0])")
        b_dn = await page.evaluate("()=>window.__a3dBulgeFrom3Pts([0,0],[1,-1],[2,0])")
        ck(near(b_up, -1, 1e-9) and near(b_dn, 1, 1e-9),
           "and the two directions get opposite signs (%.4f / %.4f)" % (b_up, b_dn))
        ck(await page.evaluate("()=>window.__a3dBulgeFrom3Pts([0,0],[1,0],[2,0])") == 0,
           "three colinear points give bulge 0, not a huge-radius arc")

        print("\n   length and area know about the curve")
        ck(near(await page.evaluate("()=>window.__a3dBulgedLength([[0,0],[2,0]],[1],false)"),
                math.pi, 1e-9),
           "a half-circle on a chord of 2 measures pi, not 2")
        ck(near(await page.evaluate("()=>window.__a3dBulgedArea([[-1,0],[1,0]],[1,1],true)"),
                math.pi, 1e-9),
           "two vertices with bulge 1 each enclose pi - a unit circle, DXF's own convention")
        ck(near(await page.evaluate("()=>window.__a3dBulgedLength([[0,0],[3,0],[3,4]],null,false)"), 7),
           "with no bulges the length is the plain polyline (7)")
        ck(near(await page.evaluate("()=>window.__a3dBulgedArea([[0,0],[4,0],[4,4],[0,4]],null,true)"), 16),
           "and the area is the plain shoelace (16)")

        print("\n   flattening is tolerance-driven, not a fixed segment count")
        flat = await page.evaluate("""()=>{
          const f=window.__a3dFlattenPoly([[0,0],[2,0]],[1],false);
          let maxR=0,maxChord=0;
          for(const p of f) maxR=Math.max(maxR,Math.abs(Math.hypot(p[0]-1,p[1])-1));
          for(let i=0;i+1<f.length;i++){
            const mx=(f[i][0]+f[i+1][0])/2,my=(f[i][1]+f[i+1][1])/2;
            maxChord=Math.max(maxChord,Math.abs(1-Math.hypot(mx-1,my)));
          }
          return {n:f.length,maxR:maxR,maxChord:maxChord,
                  first:f[0],last:f[f.length-1],
                  big:window.__a3dFlattenPoly([[0,0],[200,0]],[1],false).length,
                  small:window.__a3dFlattenPoly([[0,0],[0.2,0]],[1],false).length};
        }""")
        ck(flat['maxR'] < 1e-9,
           "every flattened point lies exactly on the arc (max radial error %.2e)" % flat['maxR'])
        ck(flat['maxChord'] <= 0.002 + 1e-9,
           "and no chord departs from it by more than the 2mm tolerance (%.6f)" % flat['maxChord'])
        ck(near(flat['first'][0], 0) and near(flat['last'][0], 2),
           "the real endpoints survive flattening")
        ck(flat['big'] > flat['small'],
           "a 200m arc gets more segments than a 200mm one (%d vs %d)"
           % (flat['big'], flat['small']))

        # ---------------------------------------------------------------- 2. nothing regresses
        print("\n-- 2. the reason bulge was chosen: a straight polyline is untouched")
        ck(await page.evaluate(
            "()=>JSON.stringify(window.__a3dFlattenPoly([[0,0],[3,0],[3,4]],null,false))"
            "===JSON.stringify([[0,0],[3,0],[3,4]])"),
           "a polyline with no bulges flattens to itself, point for point")
        await page.evaluate("()=>window.__a3dTestSetObjs([])")
        await palette_run(page, 'RECTANG')
        await page.evaluate("()=>window.__a3dTypedPoint('0,0')")
        await page.evaluate("()=>window.__a3dTypedPoint('4,3')")
        await page.wait_for_timeout(350)
        rect = await page.evaluate("""()=>{
          const o=window.__a3dState().objs.find(o=>o.t==='sketch');
          return o?{keys:Object.keys(o),pts:o.pts.length,hasBulges:'bulges' in o}:null;
        }""")
        ck(rect and rect['pts'] == 4 and not rect['hasBulges'],
           "a RECTANG sketch carries NO bulges key at all - the same object as before V88 (%s)"
           % (rect and rect['keys']))

        # ---------------------------------------------------------------- 3. the ARC command
        print("\n-- 3. ARC, driven from the command line, measured on the stored object")
        await page.evaluate("()=>window.__a3dTestSetObjs([])")
        await palette_run(page, 'ARC')
        st = await page.evaluate("()=>window.__a3dState()")
        ck(st['sk'] and st['sk']['tool'] == 'arc',
           "ARC from the command line starts the arc tool (%s)" % (st['sk'] and st['sk']['tool']))
        p0 = await page.evaluate("()=>window.__a3dPrompt()")
        await page.evaluate("()=>window.__a3dTypedPoint('0,0')")
        p1 = await page.evaluate("()=>window.__a3dPrompt()")
        await page.evaluate("()=>window.__a3dTypedPoint('1,-1')")
        p2 = await page.evaluate("()=>window.__a3dPrompt()")
        await page.evaluate("()=>window.__a3dTypedPoint('2,0')")
        await page.wait_for_timeout(420)
        ck('start point' in p0 and 'second point' in p1 and 'end point' in p2,
           "and prompts for start, second, end in order (%r / %r / %r)" % (p0, p1, p2))
        arcobj = await page.evaluate("""()=>{
          const o=window.__a3dState().objs.find(o=>o.t==='sketch');
          return o?{id:o.id,pts:o.pts,bulges:o.bulges||null,closed:o.closed}:null;
        }""")
        ck(arcobj and len(arcobj['pts']) == 2,
           "the arc is stored as TWO vertices, not a fan of chords (%d)"
           % (len(arcobj['pts']) if arcobj else -1))
        ck(arcobj and arcobj['bulges'] and near(arcobj['bulges'][0], 1, 1e-6),
           "with one bulge of +1 for a semicircle through (1,-1) -> %s"
           % (arcobj and arcobj['bulges']))
        ck(arcobj and arcobj['closed'] is False,
           "and it is open, so nothing draws the return chord (%s)"
           % (arcobj and arcobj['closed']))
        fl = await page.evaluate("(id)=>window.__a3dFlattenSketch(id)", arcobj['id'])
        maxr = max(abs(math.hypot(p[0] - 1, p[1]) - 1) for p in fl)
        ck(len(fl) > 8 and maxr < 1e-9,
           "but it DRAWS as %d points, every one on the arc (max radial error %.2e)"
           % (len(fl), maxr))
        ck(all(p[1] <= 1e-9 for p in fl),
           "and the drawn curve is on the (1,-1) side, matching the point the user clicked")

        print("\n   three points in a line are refused as an arc and said so")
        await page.evaluate("()=>window.__a3dTestSetObjs([])")
        await palette_run(page, 'ARC')
        for c in ('0,0', '1,0', '2,0'):
            await page.evaluate("(s)=>window.__a3dTypedPoint(s)", c)
        await page.wait_for_timeout(400)
        lin = await page.evaluate("""()=>{
          const o=window.__a3dState().objs.find(o=>o.t==='sketch');
          return o?{pts:o.pts.length,hasBulges:'bulges' in o}:null;
        }""")
        ck(lin and lin['pts'] == 2 and not lin['hasBulges'],
           "colinear points make a straight 2-point sketch with no bulge (%s)" % lin)

        # ---------------------------------------------------------------- 4. picking
        print("\n-- 4. the pick follows the curve, not the chord")
        await page.evaluate("()=>window.__a3dTestSetObjs([])")
        await palette_run(page, 'ARC')
        for c in ('-4,0', '0,-4', '4,0'):
            await page.evaluate("(s)=>window.__a3dTypedPoint(s)", c)
        await page.wait_for_timeout(450)
        aid = await page.evaluate("()=>{const o=window.__a3dState().objs.find(o=>o.t==='sketch');return o?o.id:null;}")
        # __a3dToScreen returns CANVAS coordinates; page.mouse takes VIEWPORT coordinates, and
        # the drawing canvas starts below the ribbon and right of the navigator. Clicking
        # without this offset lands on chrome and selects nothing -- which looks exactly like a
        # pick that does not follow the curve.
        rect = await page.evaluate(
            "()=>{const r=document.getElementById('a3d-canvas').getBoundingClientRect();"
            "return {l:r.left,t:r.top};}")
        await page.evaluate("()=>window.__a3dSelectFor([])")
        scr_arc = await page.evaluate("()=>window.__a3dToScreen([0,-4],0)")
        scr_chord = await page.evaluate("()=>window.__a3dToScreen([0,0],0)")
        await page.mouse.click(scr_arc[0] + rect['l'], scr_arc[1] + rect['t'])
        await page.wait_for_timeout(300)
        sel_on_arc = await page.evaluate("()=>window.__a3dState().sel")
        await page.evaluate("()=>window.__a3dSelectFor([])")
        await page.mouse.click(scr_chord[0] + rect['l'], scr_chord[1] + rect['t'])
        await page.wait_for_timeout(300)
        sel_on_chord = await page.evaluate("()=>window.__a3dState().sel")
        ck(sel_on_arc == aid, "clicking ON the drawn arc selects it (%s)" % sel_on_arc)
        ck(sel_on_chord != aid,
           "and clicking on its CHORD, where nothing is drawn, does not (%s)" % sel_on_chord)

        # ---------------------------------------------------------------- 5. DXF round trip
        print("\n-- 5. the DXF round trip: an arc leaves and comes back an arc")
        # bimBuildDXF returns {text, stats}, not a string.
        dxf = (await page.evaluate("()=>window.__a3dBuildDXF()"))['text']
        ck('LWPOLYLINE' in dxf, "the export writes an LWPOLYLINE")
        codes = [l.strip() for l in dxf.splitlines()]
        has42 = '42' in codes
        ck(has42, "and carries group code 42, the bulge, with it")
        before = await page.evaluate("(id)=>window.__a3dObjSnapshot(id).bulges", aid)
        await page.evaluate("()=>window.__a3dTestSetObjs([])")
        await page.evaluate("(t)=>window.__a3dImportDXF(t)", dxf)
        await page.wait_for_timeout(700)
        back = await page.evaluate("""()=>{
          const o=window.__a3dState().objs.filter(o=>o.t==='sketch'&&o.bulges);
          return o.length?{n:o.length,pts:o[0].pts,bulges:o[0].bulges}:null;
        }""")
        ck(back is not None, "re-importing that DXF produces a sketch that still has bulges")
        ck(back and len(back['pts']) == 2,
           "it is still TWO vertices, not a tessellated fan (%s)"
           % (len(back['pts']) if back else -1))
        ck(back and near(back['bulges'][0], before[0], 1e-6),
           "and the bulge survived the round trip (%s -> %s)"
           % (before[0] if before else None, back['bulges'][0] if back else None))

        print("\n   and a DXF ARC entity is stored as an arc on the way in")
        arc_dxf = ("0\nSECTION\n2\nENTITIES\n0\nARC\n8\n0\n10\n0.0\n20\n0.0\n30\n0.0\n"
                   "40\n5.0\n50\n0.0\n51\n90.0\n0\nENDSEC\n0\nEOF\n")
        await page.evaluate("()=>window.__a3dTestSetObjs([])")
        await page.evaluate("(t)=>window.__a3dImportDXF(t)", arc_dxf)
        await page.wait_for_timeout(700)
        imported = await page.evaluate("""()=>{
          const o=window.__a3dState().objs.filter(o=>o.t==='sketch');
          return o.length?{n:o.length,pts:o[0].pts,bulges:o[0].bulges||null}:null;
        }""")
        ck(imported and len(imported['pts']) == 2 and imported['bulges'],
           "a 90-degree ARC imports as 2 vertices with a bulge (%s)" % imported)
        ck(imported and imported['bulges']
           and near(imported['bulges'][0], math.tan(math.pi / 8), 1e-6),
           "and the bulge is tan(90deg/4) = %.6f -> %s"
           % (math.tan(math.pi / 8), imported['bulges'][0] if imported else None))

        # ---------------------------------------------------------------- 6. hygiene
        print("\n-- 6. hygiene")
        audit = await page.evaluate("()=>window.__a3dShellAudit()")
        bad = [k for k, v in (audit or {}).items()
               if isinstance(v, list) and v] if isinstance(audit, dict) else []
        ck(not bad, "V80 shell audit is clean (%s)" % (bad or 'clean'))
        ck(not errs, "no uncaught page errors (%s)" % (errs[:3] or 'none'))

        passed = ck.n - len(ck.failed)
        print("\n%d/%d checks passed" % (passed, ck.n))
        print("RESULT: %s" % ('PASS' if not ck.failed else 'FAIL'))
        if ck.failed:
            print("FAILURES:")
            for f in ck.failed:
                print("  - " + f)
        await browser.close()
        return 1 if ck.failed else 0


if __name__ == '__main__':
    sys.exit(asyncio.run(run()))
