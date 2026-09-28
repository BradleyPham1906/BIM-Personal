"""
bim_phase90_arc_drawing_offset_browser_tests.py

Regression suite for __acad3dV90 in canvas_v10.html: drawing curves, and offsetting them.

WHAT THIS PHASE CLAIMS: WALL and PLINE take arc segments with the A key and go back to straight
with L; each arc leaves the run TANGENT to the segment before it; the rubber band previews the
curve rather than the chord; and Offset handles curves by producing concentric arcs, so the V89
refusal is gone.

WHY EACH CHECK IS THE ONE THAT WOULD CATCH A REGRESSION:

  1. TANGENCY IS ASSERTED AT THE JOINT, not just "an arc appeared". An arc of the right endpoints
     that leaves at the wrong angle draws a visible kink in exactly the place this feature exists
     to smooth, and every other check passes on it.
  2. THE PROMPT AND THE KEY ARE ASSERTED TO AGREE at each point count: [Arc] appears if and only
     if pressing A actually switches modes, and [Line] only while in arc mode. This is the V86
     lesson applied where the option was added rather than after it drifted.
  3. THE OFFSET ARC IS ASSERTED TO BE CONCENTRIC - same centre, radius changed by exactly the
     offset distance - at a tangent joint AND at a kink. The kink is the case that earned the
     phase's one real correction: the offset vertex lands elsewhere on the offset circle, so the
     stored bulge has to be recomputed. Keeping the original bulge passes a radius check and
     fails this one.
  4. THE V89 REFUSAL IS ASSERTED GONE by driving Offset on a curved wall and reading back a new
     object, not by reading the source.
  5. UNDO IS ASSERTED TO DROP THE BULGE WITH ITS POINT. Arrays that drift apart by one silently
     reassign every arc to the wrong segment.
  6. Zero uncaught page errors, and the V80 shell audit stays clean.

Run:  python3 bim_phase90_arc_drawing_offset_browser_tests.py [path/to/canvas_v10.html]
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

        has90 = await page.evaluate("()=>!!window.__acad3dV90")
        ck(has90, "__acad3dV90 marker is present")
        if not has90:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.failed), ck.n))
            await browser.close()
            return 1

        # ---------------------------------------------------------------- 1. tangent maths
        print("\n-- 1. tangent continuation, on answers that can be computed by hand")
        tb = await page.evaluate("()=>window.__a3dTangentBulge([1,0],[0,0],[0,2])")
        ck(near(tb, 1, 1e-12),
           "travelling +x from the origin and ending at (0,2) is a CCW semicircle, bulge +1 (%s)"
           % tb)
        arc = await page.evaluate("(b)=>window.__a3dBulgeArc([0,0],[0,2],b)", tb)
        ck(near(arc['center'][1], 1, 1e-9) and near(arc['radius'], 1, 1e-9),
           "centred at (0,1), radius 1 -> c=%s r=%s" % (arc['center'], arc['radius']))
        start = await page.evaluate("""(b)=>{
          const a=window.__a3dBulgeArc([0,0],[0,2],b);
          const rx=0-a.center[0],rz=0-a.center[1],L=Math.hypot(rx,rz);
          const s=a.sweep>=0?1:-1;
          return [-s*rz/L,s*rx/L];
        }""", tb)
        ck(near(start[0], 1, 1e-9) and near(start[1], 0, 1e-9),
           "and it LEAVES along +x, tangent to the run it continues -> %s" % start)
        ck(await page.evaluate("()=>window.__a3dTangentBulge([1,0],[0,0],[-3,0])") is None,
           "doubling straight back is refused rather than made into an infinite arc")
        neg = await page.evaluate("()=>window.__a3dTangentBulge([1,0],[0,0],[0,-2])")
        ck(neg is not None and neg < 0, "turning the other way gets the opposite sign (%s)" % neg)

        # ---------------------------------------------------------------- 2. drawing a curved wall
        print("\n-- 2. drawing a curved wall: A for arc, L for line")
        await page.evaluate("()=>window.__a3dTestSetObjs([])")
        await palette_run(page, 'WALL')
        st = await page.evaluate("()=>window.__a3dState()")
        ck(st['sk'] and st['sk']['tool'] == 'wall',
           "WALL starts from the command line (%s)" % (st['sk'] and st['sk']['tool']))
        if not (st['sk'] and st['sk']['tool'] == 'wall'):
            # Nothing below can mean anything without the tool running, and a cascade of
            # failures hides which one is the real fault.
            print("\n   wall tool did not start -- skipping the rest of section 2")
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.failed), ck.n))
            await browser.close()
            return 1

        # THE PROMPT AND THE KEY HAVE TO AGREE, at every point count.
        p0 = await page.evaluate("()=>window.__a3dPrompt()")
        armed0 = await page.evaluate("()=>window.__a3dSetArcMode(true)")
        ck(('Arc' in p0) == bool(armed0),
           "with no segment yet, [Arc] is offered if and only if A works (prompt %r, A=%s)"
           % (p0, armed0))
        ck(not armed0, "and with nothing to continue from, it is refused")

        await page.evaluate("()=>window.__a3dTypedPoint('0,0')")
        await page.wait_for_timeout(200)
        # ONE POINT DOWN is the only count where the prompt and the key can disagree: there is a
        # point but no segment to continue from. Checked explicitly, because a prompt that offers
        # [Arc] whenever the TOOL is a wall - rather than when an arc is actually possible - is
        # invisible at every other count.
        p_one = await page.evaluate("()=>window.__a3dPrompt()")
        armed_one = await page.evaluate("()=>window.__a3dSetArcMode(true)")
        ck(('Arc' in p_one) == bool(armed_one) and not armed_one,
           "with ONE point down, [Arc] is offered if and only if A works, and neither happens "
           "(prompt %r, A=%s)" % (p_one, armed_one))
        # The first segment runs diagonally ON PURPOSE. Drawing it along +x would make a
        # hardcoded +x heading indistinguishable from the real one, and the tangency check below
        # is the whole point of this feature.
        await page.evaluate("()=>window.__a3dTypedPoint('3,3')")
        await page.wait_for_timeout(250)
        p1 = await page.evaluate("()=>window.__a3dPrompt()")
        ck('Arc' in p1, "once a segment exists the prompt offers [Arc] (%r)" % p1)
        armed = await page.evaluate("()=>window.__a3dSetArcMode(true)")
        ck(armed and await page.evaluate("()=>window.__a3dSkArcMode()"),
           "and A switches into arc mode")
        p2 = await page.evaluate("()=>window.__a3dPrompt()")
        ck('Line' in p2 and 'Arc' not in p2,
           "the prompt now offers [Line] and no longer [Arc] (%r)" % p2)

        await page.evaluate("()=>window.__a3dTypedPoint('0,6')")
        await page.wait_for_timeout(250)
        bulges = await page.evaluate("()=>window.__a3dSkBulges()")
        ck(bulges and len(bulges) == 2 and near(bulges[0], 0) and abs(bulges[1]) > 1e-6,
           "the arc segment recorded a bulge on segment 1, not segment 0 -> %s" % bulges)
        # TANGENCY AT THE JOINT: the arc must leave along the direction the straight run arrived.
        tangent_err = await page.evaluate("""()=>{
          const pts=window.__a3dSkPts(), b=window.__a3dSkBulges();
          if(!pts||pts.length<3||!b||b.length<2)return 1e9;
          const a=window.__a3dBulgeArc(pts[1],pts[2],b[1]);
          if(!a)return 1e9;
          const rx=pts[1][0]-a.center[0],rz=pts[1][1]-a.center[1],L=Math.hypot(rx,rz);
          const s=a.sweep>=0?1:-1;
          const dir=[-s*rz/L,s*rx/L];
          // the run arrived along the diagonal (0,0)->(3,3), normalised
          const k=Math.SQRT1_2;
          return Math.abs(dir[0]-k)+Math.abs(dir[1]-k);
        }""")
        ck(tangent_err < 1e-9,
           "and the arc leaves TANGENT to the straight run before it (error %.2e)" % tangent_err)

        print("\n   L goes back to straight, and Undo takes the bulge with the point")
        await page.evaluate("()=>window.__a3dSetArcMode(false)")
        ck(not await page.evaluate("()=>window.__a3dSkArcMode()"), "L leaves arc mode")
        # Undo is tested on a point that CLOSED AN ARC SEGMENT. Undoing a straight one proves
        # nothing here: the bulge array has no entry for it, so it would not shrink either way
        # and the check would pass against a build that never trimmed the array at all.
        await page.evaluate("()=>window.__a3dSetArcMode(true)")
        # NOT a point straight ahead of the arc's exit heading: a point on that line is a
        # tangent continuation of zero curvature and correctly records a bulge of 0, which would
        # make this check measure nothing.
        await page.evaluate("()=>window.__a3dTypedPoint('-4,6')")
        await page.wait_for_timeout(250)
        b_before = await page.evaluate("()=>window.__a3dSkBulges()")
        n_before = await page.evaluate("()=>window.__a3dSkPts().length")
        ck(b_before and len(b_before) == n_before - 1 and abs(b_before[-1]) > 1e-9,
           "a second arc segment recorded its own bulge (%s over %d points)"
           % (b_before, n_before))
        await page.keyboard.press('u')
        await page.wait_for_timeout(250)
        b_after = await page.evaluate("()=>window.__a3dSkBulges()")
        n_after = await page.evaluate("()=>window.__a3dSkPts().length")
        ck(n_after == n_before - 1,
           "Undo removed the point (%d -> %d)" % (n_before, n_after))
        ck(b_after is not None and len(b_after) == n_after - 1,
           "and the bulge array shrank with it, so no arc is left describing a segment that is "
           "gone (%s -> %s)" % (b_before, b_after))
        await page.evaluate("()=>window.__a3dSetArcMode(false)")

        print("\n   the finished wall is curved")
        await page.keyboard.press('Enter')
        await page.wait_for_timeout(400)
        if await page.evaluate("()=>!!document.querySelector('.a3d-dlg')"):
            await dlg_ok(page)
        walls = await page.evaluate("""()=>window.__a3dState().objs
            .filter(o=>o.bim&&o.bim.type==='wall')
            .map(o=>({id:o.id,cl:o.bim.centerline,bulges:o.bim.bulges||null}))""")
        ck(len(walls) == 1 and walls[0]['bulges'],
           "one wall, and it carries bulges (%s)" % (walls[0]['bulges'] if walls else None))
        ck(len(walls) == 1 and len(walls[0]['cl']) == 3,
           "with its three drawn vertices intact, not a tessellated fan (%s)"
           % (len(walls[0]['cl']) if walls else -1))
        if not walls:
            print("\n   no wall was created -- the rest of the suite cannot measure anything")
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.failed), ck.n))
            await browser.close()
            return 1
        wid = walls[0]['id']
        arc_len = await page.evaluate("(id)=>window.__a3dWallLength(id)", wid)
        ck(arc_len > 4, "and its length counts the arc (%.4f)" % arc_len)

        # ---------------------------------------------------------------- 3. offset the curve
        print("\n-- 3. Offset produces CONCENTRIC arcs, and no longer refuses")
        n0 = await page.evaluate("()=>window.__a3dState().objs.length")
        await page.evaluate("(id)=>window.__a3dSelectFor([id])", wid)
        await palette_run(page, 'OFFSET')
        ck(await page.evaluate("()=>!!document.querySelector('.a3d-dlg')"),
           "OFFSET opens its dialog for a curved wall instead of refusing it")
        await dlg_ok(page, {'d': 0.5})
        st = await page.evaluate("()=>window.__a3dState()")
        ck(len(st['objs']) == n0 + 1,
           "and produces a new object (%d -> %d)" % (n0, len(st['objs'])))
        made = [o for o in st['objs'] if o.get('bim') and o['bim'].get('type') == 'wall'
                and o['id'] != wid]
        ck(len(made) == 1 and made[0]['bim'].get('bulges'),
           "which is itself curved (%s)" % (made[0]['bim'].get('bulges') if made else None))

        # Defensive throughout: a build that lost its bulges must produce FAILED CHECKS, not a
        # stack trace. A suite that throws reports one fault where it could have reported five.
        conc = await page.evaluate("""([a,b])=>{
          const sa=window.__a3dObjSnapshot(a), sb=b?window.__a3dObjSnapshot(b):null;
          if(!sa||!sb||!sa.bim.bulges||!sb.bim.bulges)return {missing:true};
          const arcA=window.__a3dBulgeArc(sa.bim.centerline[1],sa.bim.centerline[2],sa.bim.bulges[1]);
          const arcB=window.__a3dBulgeArc(sb.bim.centerline[1],sb.bim.centerline[2],sb.bim.bulges[1]);
          if(!arcA||!arcB)return {missing:true};
          return {ca:arcA.center,cb:arcB.center,ra:arcA.radius,rb:arcB.radius};
        }""", [wid, made[0]['id'] if made else None])
        ck(not conc.get('missing')
           and near(conc['ca'][0], conc['cb'][0], 1e-6) and near(conc['ca'][1], conc['cb'][1], 1e-6),
           "the offset arc shares the original's centre -> %s"
           % ('one of them has no arc at all' if conc.get('missing')
              else '%s vs %s' % (conc['ca'], conc['cb'])))
        ck(not conc.get('missing') and near(abs(conc['ra'] - conc['rb']), 0.5, 1e-6),
           "and its radius differs by exactly the offset distance (%s)"
           % ('no arc to measure' if conc.get('missing')
              else '%.6f vs %.6f' % (conc['ra'], conc['rb'])))

        print("\n   and the same holds at a KINK, where the bulge has to be recomputed")
        kink = await page.evaluate("""()=>{
          const pts=[[-4,-3],[0,0],[0,2]], bul=[0,1];
          const off=window.__a3dOffsetBulged(pts,bul,false,0.5);
          if(off.error)return {error:off.error};
          const src=window.__a3dBulgeArc(pts[1],pts[2],bul[1]);
          const out=window.__a3dBulgeArc(off.pts[1],off.pts[2],off.bulges[1]);
          return {srcC:src.center,srcR:src.radius,outC:out.center,outR:out.radius,
                  vertexOnArc:Math.abs(Math.hypot(off.pts[1][0]-src.center[0],
                                                  off.pts[1][1]-src.center[1])-(src.radius-0.5))};
        }""")
        ck(not kink.get('error'), "a line kinking into an arc offsets (%s)" % (kink.get('error') or 'ok'))
        ck(near(kink['outC'][0], kink['srcC'][0], 1e-6) and near(kink['outC'][1], kink['srcC'][1], 1e-6),
           "the offset arc is still exactly concentric -> %s vs %s" % (kink['srcC'], kink['outC']))
        ck(near(abs(kink['srcR'] - kink['outR']), 0.5, 1e-6),
           "with the radius changed by exactly the distance (%.6f -> %.6f)"
           % (kink['srcR'], kink['outR']))
        ck(kink['vertexOnArc'] < 1e-9,
           "and the shared vertex lies ON the offset arc, so line and arc still meet (%.2e)"
           % kink['vertexOnArc'])

        bad_off = await page.evaluate("""()=>window.__a3dOffsetBulged(
            [[2,0],[0,2]],[Math.tan(Math.PI/8),0],false,3)""")
        ck(bool(bad_off.get('error')),
           "offsetting inward by more than the radius is refused, not flipped (%s)"
           % bad_off.get('error'))

        # ---------------------------------------------------------------- 4. straight unchanged
        print("\n-- 4. straight drawing is untouched")
        await page.evaluate("()=>window.__a3dTestSetObjs([])")
        await palette_run(page, 'PLINE')
        for c in ('0,0', '4,0', '4,4'):
            await page.evaluate("(s)=>window.__a3dTypedPoint(s)", c)
        await page.wait_for_timeout(200)
        await page.keyboard.press('Enter')
        await page.wait_for_timeout(400)
        sk = await page.evaluate("""()=>{
          const o=window.__a3dState().objs.find(o=>o.t==='sketch');
          return o?{pts:o.pts.length,hasBulges:'bulges' in o}:null;
        }""")
        ck(sk and sk['pts'] == 3 and not sk['hasBulges'],
           "a PLINE drawn without arc mode carries NO bulges key (%s)" % sk)
        straight_prompt = await page.evaluate("()=>window.__a3dPrompt()")
        ck('Arc' not in straight_prompt,
           "and with no tool running nothing offers [Arc] (%r)" % straight_prompt)

        await palette_run(page, 'LINE')
        await page.evaluate("()=>window.__a3dTypedPoint('0,0')")
        await page.evaluate("()=>window.__a3dTypedPoint('3,0')")
        await page.wait_for_timeout(200)
        line_prompt = await page.evaluate("()=>window.__a3dPrompt()")
        armed_line = await page.evaluate("()=>window.__a3dSetArcMode(true)")
        ck('Arc' not in line_prompt and not armed_line,
           "LINE offers no arc mode and refuses A, exactly as AutoCAD's LINE does (%r)"
           % line_prompt)
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(200)

        # ---------------------------------------------------------------- 5. hygiene
        print("\n-- 5. hygiene")
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
