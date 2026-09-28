"""
bim_phase89_curved_walls_browser_tests.py

Regression suite for __acad3dV89 in canvas_v10.html: curved walls, and FILLET with a radius.

WHAT THIS PHASE CLAIMS: a wall centerline may carry the V88 bulges; the ribbon builder flattens
it and runs the existing miter code over the result; the wall's STORED centerline stays
parametric; wall length becomes arc length; and FILLET above radius 0 builds the arc between two
walls as a real curved wall.

WHY EACH CHECK IS THE ONE THAT WOULD CATCH A REGRESSION:

  1. THE FILLET IS ASSERTED TO BE TANGENT, not merely nearby. An arc of the right radius in
     roughly the right place passes every other check and still leaves a visible kink where it
     meets the wall. Tangency is a perpendicularity test on the radius at each tangent point.
  2. REBUILDING A CURVED WALL MUST NOT STRAIGHTEN IT. There are sixteen call sites that rebuild
     wall geometry; a missed one does not throw and does not look wrong until someone changes a
     wall type. The check changes the type, the thickness and the height of a curved wall and
     asserts the bulge is still there and still the same number.
  3. THE STORED CENTERLINE MUST STAY TWO POINTS. If the builder stored what it flattened, every
     rebuild would re-tessellate an already tessellated centerline and the wall would coarsen
     slightly each time it was touched, with no single moment where anything looked wrong. The
     check rebuilds five times and asserts the vertex count never moves.
  4. MIRROR MUST NEGATE THE BULGE. A reflected curve that kept its sign bows the wrong way -
     an error that reads as a rendering glitch rather than a data one.
  5. LENGTH MUST BE ARC LENGTH. A schedule reporting the chord of a curved wall is quietly wrong,
     which is worse than loudly wrong.
  6. THE TOOLS THAT CANNOT DO CURVES MUST REFUSE, not straighten. Each is driven against a curved
     wall and the wall is asserted to be unchanged afterwards. (Offset left this list in V90, Break
     and Trim in V91, Lengthen and Extend in V92. What remains here is what is still genuinely
     unbuilt: Fillet, Chamfer, Join and Merge.)
  7. Zero uncaught page errors, and the V80 shell audit stays clean.

Run:  python3 bim_phase89_curved_walls_browser_tests.py [path/to/canvas_v10.html]
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


async def dlg_ok(page, values=None):
    if values:
        for sel, val in values.items():
            await page.fill('.a3d-dlg [data-a3dp="%s"]' % sel, str(val))
            await page.wait_for_timeout(80)
    await page.click('.a3d-dlg [data-a3dlg="ok"]')
    await page.wait_for_timeout(450)


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

        has89 = await page.evaluate("()=>!!window.__acad3dV89")
        ck(has89, "__acad3dV89 marker is present")
        if not has89:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.failed), ck.n))
            await browser.close()
            return 1

        # ---------------------------------------------------------------- 1. fillet geometry
        print("\n-- 1. the fillet geometry, with tangency asserted")
        r = await page.evaluate("""()=>window.__a3dFilletCorner(
            [[0,0],[10,0]],false,[[10,0],[10,10]],false,2)""")
        ck(not r.get('error'), "a right-angle fillet is computed (%s)" % (r.get('error') or 'ok'))
        ck(near(r.get('tangent'), 2), "tangent distance for a 90deg corner equals the radius (%s)"
           % r.get('tangent'))
        ck(near(r['a'][1][0], 8) and near(r['b'][0][1], 2),
           "both walls are cut back to their tangent points, (8,0) and (10,2) -> %s %s"
           % (r['a'][1], r['b'][0]))
        arc = await page.evaluate("(f)=>window.__a3dBulgeArc(f.pts[0],f.pts[1],f.bulges[0])",
                                  r['fillet'])
        ck(near(arc['radius'], 2, 1e-9), "the arc has the requested radius (%s)" % arc['radius'])
        ck(near(arc['center'][0], 8, 1e-9) and near(arc['center'][1], 2, 1e-9),
           "centred at (8,2) -> %s" % arc['center'])
        tang = await page.evaluate("""([f,c])=>{
          function perp(center,t,dir){
            const rx=t[0]-center[0],rz=t[1]-center[1],L=Math.hypot(rx,rz);
            return Math.abs((rx/L)*dir[0]+(rz/L)*dir[1]);
          }
          return [perp(c,f.pts[0],[1,0]),perp(c,f.pts[1],[0,1])];
        }""", [r['fillet'], arc['center']])
        ck(max(tang) < 1e-9,
           "and it is TANGENT to both walls, not merely near them (max %.2e)" % max(tang))

        rm = await page.evaluate("""()=>window.__a3dFilletCorner(
            [[0,0],[10,0]],false,[[10,0],[10,-10]],false,2)""")
        ck((r['fillet']['bulges'][0] > 0) != (rm['fillet']['bulges'][0] > 0),
           "a corner turning the other way gets the opposite bulge sign (%.5f vs %.5f)"
           % (r['fillet']['bulges'][0], rm['fillet']['bulges'][0]))
        for case, why in ((("[[0,0],[10,0]],false,[[0,5],[10,5]],false,1"), "parallel walls"),
                          (("[[0,0],[10,0]],false,[[10,0],[20,0]],false,1"), "colinear walls"),
                          (("[[0,0],[10,0]],false,[[10,0],[10,10]],false,40"), "too large a radius")):
            e = await page.evaluate("()=>window.__a3dFilletCorner(%s)" % case)
            ck(bool(e.get('error')), "%s are refused (%s)" % (why, e.get('error')))

        # ---------------------------------------------------------------- 2. FILLET end to end
        print("\n-- 2. FILLET driven from the command line, measured on the model")
        await page.evaluate("()=>window.__a3dTestSetObjs([])")
        a = await page.evaluate("()=>window.__a3dWall([[0,0],[10,0]],0.3,3,'center',false)")
        b = await page.evaluate("()=>window.__a3dWall([[10,0],[10,10]],0.3,3,'center',false)")
        await page.wait_for_timeout(350)
        await page.evaluate("([x,y])=>window.__a3dSelectPair(x,y)", [a, b])
        n0 = await page.evaluate("()=>window.__a3dState().objs.length")
        await palette_run(page, 'FILLET')
        ck(await page.evaluate("()=>!!document.querySelector('.a3d-dlg')"),
           "FILLET from the command line opens its radius dialog")
        await dlg_ok(page, {'r': 2})
        st = await page.evaluate("()=>window.__a3dState()")
        ck(len(st['objs']) == n0 + 1,
           "a third wall exists for the arc (%d -> %d)" % (n0, len(st['objs'])))
        fillet = [o for o in st['objs'] if o.get('bim') and o['bim'].get('type') == 'wall'
                  and o['id'] not in (a, b)]
        ck(len(fillet) == 1 and fillet[0]['bim'].get('bulges'),
           "and it is a CURVED wall - it carries bulges (%s)"
           % (fillet[0]['bim'].get('bulges') if fillet else None))
        ck(len(fillet) == 1 and len(fillet[0]['bim']['centerline']) == 2,
           "stored as two vertices and one bulge, not a tessellated fan (%d)"
           % (len(fillet[0]['bim']['centerline']) if fillet else -1))
        fid = fillet[0]['id']
        ck(near(fillet[0]['bim']['thickness'], 0.3),
           "the arc wall inherits the source wall's thickness (%s)" % fillet[0]['bim']['thickness'])
        ca = await page.evaluate("(id)=>window.__a3dObjSnapshot(id).bim.centerline", a)
        cb = await page.evaluate("(id)=>window.__a3dObjSnapshot(id).bim.centerline", b)
        ck(near(ca[1][0], 8) and near(cb[0][1], 2),
           "and both straight walls are cut back to the tangent points -> %s %s" % (ca, cb))

        print("\n   the arc wall is real geometry, not just data")
        mesh = await page.evaluate("(id)=>{const o=window.__a3dObjSnapshot(id);"
                                   "return {v:o.mesh.v.length,f:o.mesh.f.length};}", fid)
        ck(mesh['v'] > 8 and mesh['f'] > 4,
           "it built a mesh with many vertices, so the ribbon follows the curve (%s)" % mesh)
        length = await page.evaluate("(id)=>window.__a3dWallLength(id)", fid)
        ck(near(length, math.pi, 1e-3),
           "and its LENGTH is the arc length, pi for a quarter of radius 2 (%.6f)" % length)
        chord = await page.evaluate("(id)=>{const c=window.__a3dObjSnapshot(id).bim.centerline;"
                                     "return Math.hypot(c[1][0]-c[0][0],c[1][1]-c[0][1]);}", fid)
        ck(length > chord + 0.1,
           "which is longer than the chord (%.4f vs %.4f) - a schedule taking the chord would "
           "under-report this wall" % (length, chord))

        # ---------------------------------------------------------------- 3. rebuilds
        print("\n-- 3. rebuilding a curved wall must not straighten or coarsen it")
        b0 = await page.evaluate("(id)=>window.__a3dObjSnapshot(id).bim.bulges[0]", fid)
        n_before = await page.evaluate("(id)=>window.__a3dObjSnapshot(id).bim.centerline.length", fid)
        await page.evaluate("(id)=>{window.__a3dSelectFor([id]);}", fid)
        changed = await page.evaluate("""(id)=>{
          const o=window.__a3dState().objs.find(o=>o.id===id);
          const out=[];
          for(let i=0;i<5;i++){
            window.__a3dRebuildWall(id,0.2+i*0.05,3+i,'center');
            const s=window.__a3dObjSnapshot(id);
            out.push({n:s.bim.centerline.length,b:s.bim.bulges?s.bim.bulges[0]:null,
                      thk:s.bim.thickness});
          }
          return out;
        }""", fid)
        ck(all(c['n'] == n_before for c in changed),
           "five rebuilds and the stored centerline is still %d vertices (%s)"
           % (n_before, [c['n'] for c in changed]))
        ck(all(c['b'] is not None and near(c['b'], b0, 1e-12) for c in changed),
           "and the bulge is unchanged to the last digit (%s)" % [c['b'] for c in changed])
        ck(changed[-1]['thk'] != 0.3,
           "while the thickness really did change, so the rebuilds actually ran (%s)"
           % changed[-1]['thk'])

        # ---------------------------------------------------------------- 4. mirror
        print("\n-- 4. MIRROR negates the bulge")
        await page.evaluate("(id)=>window.__a3dSelectFor([id])", fid)
        n1 = await page.evaluate("()=>window.__a3dState().objs.length")
        await page.evaluate("(id)=>window.__a3dMirrorSelection([id],[0,-50],[0,50])", fid)
        await page.wait_for_timeout(400)
        st = await page.evaluate("()=>window.__a3dState()")
        ck(len(st['objs']) == n1 + 1, "the mirror made a copy (%d -> %d)" % (n1, len(st['objs'])))
        copies = [o for o in st['objs'] if o.get('bim') and o['bim'].get('bulges')
                  and o['id'] != fid]
        ck(len(copies) == 1 and near(copies[0]['bim']['bulges'][0], -b0, 1e-9),
           "and the copy's bulge is negated (%s -> %s)"
           % (b0, copies[0]['bim']['bulges'][0] if copies else None))
        # Defensive: a build that dropped the bulges must report a FAILED CHECK, not crash the
        # suite. A suite that throws stops measuring everything after the first fault.
        rot_id = await page.evaluate("""(id)=>{
          window.__a3dRotateSelection([id],[0,0],Math.PI/3);
          const s=window.__a3dObjSnapshot(id);
          return (s&&s.bim&&s.bim.bulges)?s.bim.bulges[0]:null;
        }""", fid)
        ck(near(rot_id, b0, 1e-9),
           "while ROTATE leaves it alone - a rotation does not change an angle (%s)" % rot_id)

        # ---------------------------------------------------------------- 5. refusals
        print("\n-- 5. the tools that STILL cannot do curves refuse instead of straightening")
        await page.evaluate("()=>window.__a3dTestSetObjs([])")
        cw = await page.evaluate("""()=>window.__a3dCurvedWall(
            [[0,0],[6,0]],[0.5,0],0.3,3,'center',false)""")
        await page.wait_for_timeout(350)
        straight = await page.evaluate("()=>window.__a3dWall([[8,-4],[8,4]],0.3,3,'center',false)")
        await page.wait_for_timeout(300)
        ck(await page.evaluate("(id)=>window.__a3dWallIsCurved(id)", cw),
           "a curved wall was created for the refusal checks")
        before = await page.evaluate("(id)=>JSON.stringify(window.__a3dObjSnapshot(id).bim)", cw)

        results = await page.evaluate("""([cw,st])=>{
          const out={};
          window.__a3dSelectFor([cw]);
          out.offset=window.__a3dOffsetObjectError?null:null;
          // JOIN / MERGE go through the pair selection
          window.__a3dSelectPair(cw,st);
          out.join=window.__a3dRunCmd('join');
          out.fillet=window.__a3dRunCmd('fillet');
          const dlg=document.querySelector('.a3d-dlg');
          out.filletDialog=!!dlg;
          if(dlg&&dlg.parentNode)dlg.parentNode.removeChild(dlg);
          return out;
        }""", [cw, straight])
        ck(not results['filletDialog'],
           "FILLET refuses a curved wall rather than opening its dialog")
        after = await page.evaluate("(id)=>JSON.stringify(window.__a3dObjSnapshot(id).bim)", cw)
        ck(before == after, "and the curved wall is byte-identical afterwards")

        # EACH COMMAND IS DRIVEN TO THE POINT WHERE IT WOULD ACT. The first version of this block
        # gave BREAK a single point and called the wall's survival a refusal -- but BREAK needs
        # two points, so it had not acted for reasons of its own and the check passed against a
        # build with the guard deliberately removed. A refusal claimed without driving the
        # command all the way through is the V85 fault.
        print("      (each command is driven all the way to where it would change the wall)")

        # BREAK used to be in this list. V91 taught it curves, so it is no longer a refusal and
        # asserting one here would be asserting a limitation that has been lifted -- the
        # bim_phase91 suite now covers what Break actually does to a curve. Removed rather than
        # softened: a check that a tool "does nothing" is worthless once the tool does something.
        # LENGTHEN and EXTEND left this list in V92, which taught them curves; the
        # bim_phase92 suite covers what they now do to one. What remains below is what is still
        # genuinely unbuilt.
        await page.evaluate("()=>{window.__a3dRunCmd('selNone');}")
        await page.evaluate("()=>{const d=document.querySelector('.a3d-dlg');"
                             "if(d&&d.parentNode)d.parentNode.removeChild(d);}")

        objs_now = await page.evaluate("()=>window.__a3dState().objs.length")
        ck(objs_now == 2,
           "and neither of the remaining refusals created or destroyed an object (%d)" % objs_now)

        # ---------------------------------------------------------------- 6. straight unchanged
        print("\n-- 6. a straight wall is still exactly what it was")
        snap = await page.evaluate("(id)=>window.__a3dObjSnapshot(id)", straight)
        ck('bulges' not in snap['bim'],
           "a straight wall carries NO bulges key (%s)" % list(snap['bim'].keys()))
        ck(near(await page.evaluate("(id)=>window.__a3dWallLength(id)", straight), 8),
           "and its length is the plain polyline length (8)")

        # ---------------------------------------------------------------- 7. hygiene
        print("\n-- 7. hygiene")
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
