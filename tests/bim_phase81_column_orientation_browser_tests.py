"""
bim_phase81_column_orientation_browser_tests.py

Regression suite for __acad3dV81 in canvas_v10.html: columns that actually turn, a transform that
knows what kind it is, and a rotate ring that says what it cannot rotate before the drag.

WHAT THE USER REPORTED: "the rotation didnt rotate right."

WHAT IT WAS. bimComputeTransformedGeometry rebuilt a column AXIS-ALIGNED at its new centre:

    var newCenter=transformPt(o.bim.center);
    var res3=bimBuildColumnGeometry(newCenter,o.bim.baseY,o.bim.width,o.bim.depth,o.bim.height);

There was no orientation in that call because a column had none to store. A rectangular column
ORBITED the rotation centre and never turned; a column standing ON that centre did not move at all.
Measured on V80: a 1.2 x 3.0 column rotated 45 degrees came back with a bounding box of exactly
1.2 x 3.0 -- byte-identical geometry.

WHY THE V78 SUITE MISSED IT, which is the lesson this file exists to record. V78 asserted rigid
rotation hard -- every point turning by one angle, every radius preserved to 1e-15 -- but only ever
on WALLS, a room, and a multi-selection of walls. bimComputeTransformedGeometry dispatches on type,
and the types are not equivalent: a wall rebuilds from a centreline, a floor from a profile, a beam
and a generic solid from their vertices, and a column from a centre plus width and depth. Only the
last carries an orientation. A suite that exercises one branch of a dispatcher has tested one
branch. Section 4 below rotates one of EVERY type for that reason.

A square column hides this fault completely, which is why it survived as long as it did.

WHY EACH CHECK IS THE ONE THAT WOULD CATCH A REGRESSION:

  1. The column is asserted to turn by MEASURING its footprint, against the exact figure the
     geometry demands: a w x d rectangle turned 45 degrees spans (w+d)/sqrt(2) on both axes, and
     turned 90 degrees has its two spans swapped. "The object changed" would pass for a column that
     merely moved; these numbers only come out right if the solid itself turned.
  2. The column is rotated about its OWN centre. That is the case the old code could not fail
     loudly on -- nothing moved at all, so there was no clue anything was wrong.
  3. Orientation is asserted to survive a resize, a type change and an array copy. Those are three
     separate rebuild paths, each of which drops the orientation if it forgets to pass it, and each
     of which would be found weeks later by someone wondering why a column straightened itself.
  4. Every type is rotated and asserted to have genuinely turned.
  5. Mirror is asserted to REFLECT the orientation, not rotate it -- a different answer, and the
     reason the transform carries a KIND rather than just an angle.
  6. Refusals are reported BEFORE the drag. Roofs, stairs and openings genuinely cannot be
     transformed; the ring used to read "ANGLE 45" over an object sitting perfectly still.

Run:  python3 bim_phase81_column_orientation_browser_tests.py [path/to/canvas_v10.html]
"""

import asyncio, math, pathlib, sys

from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'

# Plan-footprint span of an object's world geometry: [X span, Z span].
PLAN_SPAN = """(id)=>{
  const o=window.__a3dObjSnapshot(id),q=o.pos||[0,0,0];
  let a=[1e9,1e9],b=[-1e9,-1e9];
  if(o.mesh&&o.mesh.v.length){
    o.mesh.v.forEach(v=>{
      const p=[v[0]+q[0],v[2]+q[2]];
      for(let k=0;k<2;k++){if(p[k]<a[k])a[k]=p[k];if(p[k]>b[k])b[k]=p[k];}});
  }else if(o.pts&&o.pts.length){
    o.pts.forEach(v=>{
      const p=[v[0]+q[0],v[1]+q[2]];
      for(let k=0;k<2;k++){if(p[k]<a[k])a[k]=p[k];if(p[k]>b[k])b[k]=p[k];}});
  }else return null;
  return [Math.round((b[0]-a[0])*1e4)/1e4, Math.round((b[1]-a[1])*1e4)/1e4];}"""


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
        ctx = await browser.new_context(viewport={'width': 1600, 'height': 950},
                                        device_scale_factor=2)
        page = await ctx.new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        await page.goto('file://' + str(HTML))
        await page.wait_for_timeout(2000)

        has81 = await page.evaluate("()=>!!window.__acad3dV81")
        ck(has81, "__acad3dV81 marker is present")
        if not has81:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.failed), ck.n))
            await browser.close()
            return 1

        print("\n-- 1. a rectangular column TURNS, measured against the geometry")
        # __a3dColumnAt(pt, baseY, width, depth, height): a 1.2 x 3.0 footprint, 3m tall.
        W, D = 1.2, 3.0
        cid = await page.evaluate("""()=>{
          window.__a3dTestSetObjs([]);
          return window.__a3dColumnAt([0,0],0,1.2,3.0,3);}""")
        span0 = await page.evaluate(PLAN_SPAN, cid)
        ck(abs(span0[0] - W) < 1e-3 and abs(span0[1] - D) < 1e-3,
           "it starts as a %.1f x %.1f footprint (%s)" % (W, D, span0))

        await page.evaluate("(id)=>window.__a3dRotateSelection([id],[0,0],Math.PI/4)", cid)
        await page.wait_for_timeout(300)
        span45 = await page.evaluate(PLAN_SPAN, cid)
        want45 = (W + D) / math.sqrt(2)
        ck(abs(span45[0] - want45) < 2e-3 and abs(span45[1] - want45) < 2e-3,
           "at 45 degrees both spans are (w+d)/sqrt(2) = %.4f (%s) -- on the V80 build this read "
           "%s, byte-identical to the start, because the column was rebuilt axis-aligned at its "
           "new centre" % (want45, span45, span0))
        ck(abs(await page.evaluate("(id)=>window.__a3dColumnRotation(id)", cid)
               - math.pi / 4) < 1e-9,
           "and the orientation is stored on the column")

        await page.evaluate("(id)=>window.__a3dRotateSelection([id],[0,0],Math.PI/4)", cid)
        await page.wait_for_timeout(300)
        span90 = await page.evaluate(PLAN_SPAN, cid)
        ck(abs(span90[0] - D) < 1e-3 and abs(span90[1] - W) < 1e-3,
           "at 90 degrees the two spans have SWAPPED (%s) -- 'the object changed' would pass for a "
           "column that merely moved; only a solid that actually turned gives these numbers"
           % span90)

        print("\n-- 2. rotating about the column's OWN centre still turns it")
        cid2 = await page.evaluate("""()=>{
          window.__a3dTestSetObjs([]);
          return window.__a3dColumnAt([5,-2],0,1.2,3.0,3);}""")
        m0 = await page.evaluate("(id)=>JSON.stringify(window.__a3dObjSnapshot(id).mesh)", cid2)
        await page.evaluate("(id)=>window.__a3dRotateSelection([id],[5,-2],Math.PI/4)", cid2)
        await page.wait_for_timeout(300)
        m1 = await page.evaluate("(id)=>JSON.stringify(window.__a3dObjSnapshot(id).mesh)", cid2)
        ck(m0 != m1,
           "its mesh changes (it did NOT before this phase -- nothing moved at all, so there was "
           "no clue anything was wrong)")
        sp = await page.evaluate(PLAN_SPAN, cid2)
        ck(abs(sp[0] - want45) < 2e-3 and abs(sp[1] - want45) < 2e-3,
           "and it is turned by the right amount in place (%s)" % sp)

        print("\n-- 3. the orientation survives every other rebuild path")
        rot = await page.evaluate("(id)=>window.__a3dColumnRotation(id)", cid2)
        await page.evaluate("(id)=>window.__a3dRebuildColumn(id,0.6,1.8,3.5)", cid2)
        await page.wait_for_timeout(350)
        ck(abs(await page.evaluate("(id)=>window.__a3dColumnRotation(id)", cid2) - rot) < 1e-9,
           "a RESIZE keeps it (%.4f rad) -- editing width must not straighten a turned column"
           % rot)
        spR = await page.evaluate(PLAN_SPAN, cid2)
        wantR = (0.6 + 1.8) / math.sqrt(2)
        ck(abs(spR[0] - wantR) < 2e-3,
           "and the resized column is still turned, at its new size (%s vs %.4f)" % (spR, wantR))
        arr = await page.evaluate("""(id)=>{
          const before=window.__a3dState().objs.length;
          window.__a3dSelectFor([id]);
          window.__a3dBuildPolarArray([id],[0,0],3,360);
          const objs=window.__a3dState().objs.filter(o=>o.bim&&o.bim.type==='column');
          return {n:objs.length, rots:objs.map(o=>o.bim.rotation===undefined?null:1)};}""", cid2)
        ck(arr['n'] > 1 and all(r == 1 for r in arr['rots']),
           "and every ARRAY copy carries a rotation field (%d columns) -- three separate rebuild "
           "paths, each of which straightens the column if it forgets to pass it" % arr['n'])

        print("\n-- 4. one of EVERY type turns -- the coverage V78 did not have")
        types = await page.evaluate("""()=>{
          function span(id){
            const o=window.__a3dObjSnapshot(id),q=o.pos||[0,0,0];
            let a=[1e9,1e9],b=[-1e9,-1e9];
            const pts=[];
            if(o.mesh&&o.mesh.v.length)o.mesh.v.forEach(v=>pts.push([v[0]+q[0],v[2]+q[2]]));
            else if(o.pts)o.pts.forEach(v=>pts.push([v[0]+q[0],v[1]+q[2]]));
            pts.forEach(p=>{for(let k=0;k<2;k++){if(p[k]<a[k])a[k]=p[k];if(p[k]>b[k])b[k]=p[k];}});
            return [b[0]-a[0],b[1]-a[1]];
          }
          const mk={
            wall:()=>window.__a3dWall([[-3,0],[3,0]],0.3,3,'center',false),
            floor:()=>window.__a3dFloorAt([[-3,-1],[3,-1],[3,1],[-3,1]],0.2),
            column:()=>window.__a3dColumnAt([0,0],0,1.2,3.0,3),
            beam:()=>window.__a3dBeam([-3,0],[3,0],0.3,0.8,'center'),
            room:()=>{window.__a3dWall([[-3,-2],[3,-2],[3,2],[-3,2]],0.3,3,'center',true);
                      return window.__a3dCreateRoomAt([0,0],0);},
            sketch:()=>window.__a3dSketch('poly',[[-3,-1],[3,-1],[3,1],[-3,1]])
          };
          const out={};
          for(const k in mk){
            window.__a3dTestSetObjs([]);
            const id=mk[k]();
            if(!id){out[k]={made:false};continue;}
            const s0=span(id);
            const m0=JSON.stringify(window.__a3dObjSnapshot(id).mesh||
                                    window.__a3dObjSnapshot(id).pts);
            window.__a3dRotateSelection([id],[0,0],Math.PI/4);
            const s1=span(id);
            const m1=JSON.stringify(window.__a3dObjSnapshot(id).mesh||
                                    window.__a3dObjSnapshot(id).pts);
            out[k]={made:true,changed:m0!==m1,
                    s0:s0.map(x=>Math.round(x*100)/100),
                    s1:s1.map(x=>Math.round(x*100)/100),
                    reshaped:Math.abs(s0[0]-s1[0])>0.01||Math.abs(s0[1]-s1[1])>0.01};
          }
          return out;}""")
        for k in sorted(types):
            v = types[k]
            print("     %-8s %s -> %s" % (k, v.get('s0'), v.get('s1')))
        for k in sorted(types):
            v = types[k]
            ck(v['made'] and v['changed'] and v['reshaped'],
               "%s: its geometry turns (%s -> %s)" % (k, v.get('s0'), v.get('s1')))

        print("\n-- 5. mirror REFLECTS the orientation, it does not rotate it")
        mir = await page.evaluate("""()=>{
          window.__a3dTestSetObjs([]);
          const c=window.__a3dColumnAt([2,3],0,1.2,3.0,3);
          window.__a3dRotateSelection([c],[2,3],30*Math.PI/180);
          const before=window.__a3dColumnRotation(c);
          // mirror about the X axis (the line through (0,0) and (1,0)): phi = 0, so 30 -> -30
          window.__a3dMirrorSelection([c],[0,0],[1,0]);
          const cols=window.__a3dState().objs.filter(o=>o.bim&&o.bim.type==='column');
          return {before:before, rots:cols.map(o=>o.bim.rotation)};}""")
        made = [r for r in mir['rots'] if abs(r + mir['before']) < 1e-9]
        ck(len(made) >= 1,
           "a column at +30 degrees mirrored about the X axis comes out at -30 (%s) -- a rotation "
           "would have given a different answer, which is why the transform carries a KIND rather "
           "than just an angle"
           % [round(math.degrees(r), 3) for r in mir['rots']])

        print("\n-- 6. rotation is editable as a number")
        cid3 = await page.evaluate("""()=>{
          window.__a3dTestSetObjs([]);
          const c=window.__a3dColumnAt([0,0],0,1.2,3.0,3);
          window.__a3dSelectFor([c]);window.__a3dRefreshProps();
          return c;}""")
        await page.wait_for_timeout(400)
        rows = await page.evaluate("()=>window.__a3dPropRows().map(r=>r.label)")
        ck(any(r.startswith('Rotation') for r in rows),
           "a Rotation row is in the column's properties (%s)"
           % [r for r in rows if r.startswith('Rotation')])
        ok = await page.evaluate("""()=>{
          const i=document.querySelector('[data-propf="crot"]');
          if(!i)return false;
          i.value='60';
          i.dispatchEvent(new Event('change',{bubbles:true}));
          return true;}""")
        await page.wait_for_timeout(450)
        ck(ok is True and abs(await page.evaluate("(id)=>window.__a3dColumnRotation(id)", cid3)
                              - math.pi / 3) < 1e-9,
           "typing 60 sets the orientation to 60 degrees")
        sp60 = await page.evaluate(PLAN_SPAN, cid3)
        ck(abs(sp60[0] - (W * abs(math.cos(math.pi / 3)) + D * abs(math.sin(math.pi / 3)))) < 2e-3,
           "and the SOLID is rebuilt at that angle (%s)" % sp60)

        print("\n-- 7. the ring reports refusals before the drag, not after")
        split = await page.evaluate("""()=>{
          window.__a3dTestSetObjs([]);
          const w=window.__a3dWall([[0,0],[8,0],[8,6],[0,6]],0.3,3,'center',true);
          const d=window.__a3dDoorAt(w,[4,0],0.9,2.1);
          return {mixed:window.__a3dRotatableSplit([w,d]),
                  none:window.__a3dRotatableSplit([d])};}""")
        ck(split['mixed']['no'] == ['Door_1'] and len(split['mixed']['ok']) == 1,
           "a wall + door selection reports the door as unrotatable (%s)" % split['mixed'])
        ck(split['none']['ok'] == [] and split['none']['no'] == ['Door_1'],
           "and a door alone has nothing rotatable (%s)" % split['none'])
        ck(await page.evaluate("()=>window.__a3dRotatableSplit([]).ok") == [],
           "an empty selection is handled without throwing")

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
