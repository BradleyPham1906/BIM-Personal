"""
bim_phase95_boundary_browser_tests.py

Regression suite for __acad3dV95 in canvas_v10.html: BOUNDARY, and the planar arrangement it
stands on.

WHAT THIS PHASE CLAIMS: every edge is split at every crossing before the face walk runs; the
walk sorts turns by the tangent so curved edges are followed where they actually go; the traced
region keeps its curves and its exact area; islands are reported rather than absorbed; and the
V22 wall-face tracer is REPLACED by this one, not left running beside it.

WHY EACH CHECK IS THE ONE THAT WOULD CATCH A REGRESSION:

  1. FOUR LINES THAT MERELY CROSS. No two of them share a vertex, so the V22 graph had no node
     at any crossing and the square in the middle did not exist. The area is asserted as exactly
     1.0, which no approximation reaches.
  2. A CIRCLE CUT BY A CHORD, ASSERTED AT THE EXACT SEGMENT AREA r^2/2*(theta - sin theta).
     Drop the bulge and that region has NO area at all, so this separates a curve-carrying trace
     from a chord one with nothing in between.
  3. THE SPUR. A dead-end edge inside a region must be walked in and back out; the two
     traversals cancel in the shoelace. A walk that takes a wrong turn at the dead end returns a
     different area, and every count check still passes.
  4. THE THREE FIXES ROOM AND FLOOR INHERIT are each driven separately: crossing walls, a
     CURVED wall (area asserted against the chord polygon, which differs), and a MOVED wall
     (the V75 bug in a place the V75 fix never reached).
  5. ROOM IS CREATED END TO END, because the tracer under it was replaced and "the geometry is
     right" is not the same claim as "the command still works".
  6. THE DELETED FUNCTIONS ARE ASSERTED GONE from the page source, so the old tracer cannot
     come back as a second answer to the same question.
  7. Zero uncaught page errors, and the V80 shell audit stays clean.

Run:  python3 bim_phase95_boundary_browser_tests.py [path/to/canvas_v10.html]
"""
import asyncio, math, pathlib, sys

from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'

Q = math.tan(math.pi / 8)


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
    await page.wait_for_timeout(220)
    await page.keyboard.press('Enter')
    await page.wait_for_timeout(420)


def line_obj(i, a, b):
    return {'id': 'ck-l%d' % i, 't': 'sketch', 'name': 'L%d' % i, 'col': '#5ec4b8',
            'pos': [0, 0, 0], 'pts': [a, b], 'y': 0, 'closed': False}


async def set_objs(page, objs):
    await page.evaluate("(o)=>window.__a3dTestSetObjs(o)", objs)
    await page.wait_for_timeout(120)


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

        has95 = await page.evaluate("()=>!!window.__acad3dV95")
        ck(has95, "__acad3dV95 marker is present")
        if not has95:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.failed), ck.n))
            await browser.close()
            return 1

        # ------------------------------------------------- 1. the arrangement
        print("\n-- 1. lines that merely cross: the case V22 could not see")
        GRID = [line_obj(1, [-5, 0], [5, 0]), line_obj(2, [-5, 1], [5, 1]),
                line_obj(3, [0, -5], [0, 5]), line_obj(4, [1, -5], [1, 5])]
        await set_objs(page, GRID)
        raw = await page.evaluate("()=>window.__a3dBoundaryEdges(0,{walls:true,sketches:true,clines:true})")
        ck(len(raw) == 4, "four edges collected, none of them sharing a vertex (%d)" % len(raw))
        arr = await page.evaluate("(e)=>window.__a3dArrangeEdges(e)", raw)
        ck(len(arr['edges']) == 12,
           "the arrangement splits them into twelve at the four crossings (%d)"
           % len(arr['edges']))
        res = await page.evaluate("(e)=>window.__a3dTraceBoundary(e,[0.5,0.5])", raw)
        ck(not res.get('error') and near(res['area'], 1, 1e-9),
           "and the point in the middle finds the unit square, exactly (%s)"
           % (res.get('error') or ('%.9f' % res['area'])))
        ck(not res.get('error') and len(res['pts']) == 4,
           "with four corners (%s)" % (res.get('error') or len(res['pts'])))
        ck(not res.get('error') and res['islands'] is False, "and no islands")
        out = await page.evaluate("(e)=>window.__a3dTraceBoundary(e,[3,0.5])", raw)
        ck(bool(out.get('error')),
           "a point in a region that is NOT closed is refused (%s)" % out.get('error'))

        print("\n-- 2. the same thing, driven as the BOUNDARY command")
        await set_objs(page, GRID)
        await palette_run(page, 'BOUNDARY')
        st = await page.evaluate("()=>window.__a3dState()")
        ck(st['sk'] and st['sk']['tool'] == 'boundary',
           "BOUNDARY starts from the palette (%s)" % (st['sk'] and st['sk']['tool']))
        pr = await page.evaluate("()=>window.__a3dPrompt()")
        ck('internal point' in pr, "and asks for an internal point (%r)" % pr)
        await page.evaluate("()=>window.__a3dPlacePoint(0.5,0.5)")
        await page.wait_for_timeout(400)
        objs = await page.evaluate("()=>window.__a3dState().objs")
        made = [o for o in objs if o['id'] not in ('ck-l1', 'ck-l2', 'ck-l3', 'ck-l4')]
        ck(len(made) == 1 and len(made[0]['pts']) == 4,
           "one closed polyline created with four vertices (%d)" % len(made))
        # guarded: an earlier failure must make the NEXT check fail, not crash the suite
        area = await page.evaluate(
            "(o)=>window.__a3dBulgedArea(o.pts,o.bulges||null,true)", made[0]) if made else None
        ck(area is not None and near(area, 1, 1e-9),
           "measuring exactly 1 m2 (%s)" % ('%.9f' % area if area is not None else 'nothing made'))
        st = await page.evaluate("()=>window.__a3dState()")
        ck(st['sk'] and st['sk']['tool'] == 'boundary',
           "and the command stays live for the next pick")

        # ------------------------------------------------- 3. curves
        print("\n-- 3. a circle cut by a chord, at the exact segment area")
        CIRC = [{'id': 'ck-c', 't': 'sketch', 'name': 'C', 'col': '#5ec4b8', 'pos': [0, 0, 0],
                 'pts': [[-2, 0], [2, 0]], 'bulges': [1, 1], 'y': 0},
                line_obj(9, [-5, 1], [5, 1])]
        await set_objs(page, CIRC)
        edges = await page.evaluate("()=>window.__a3dBoundaryEdges(0,{walls:true,sketches:true,clines:true})")
        theta = 2 * math.pi / 3
        cap = 4 / 2 * (theta - math.sin(theta))
        minor = await page.evaluate("(e)=>window.__a3dTraceBoundary(e,[0,1.5])", edges)
        ck(not minor.get('error') and near(minor['area'], cap, 1e-7),
           "the minor segment is r^2/2*(theta-sin theta) (%s vs %.9f)"
           % (minor.get('error') or ('%.9f' % minor['area']), cap))
        major = await page.evaluate("(e)=>window.__a3dTraceBoundary(e,[0,-1])", edges)
        ck(not major.get('error') and near(major['area'], math.pi * 4 - cap, 1e-7),
           "the major segment is the rest of the circle (%s)"
           % (major.get('error') or ('%.9f' % major['area'])))
        chord_only = await page.evaluate(
            "(r)=>window.__a3dBulgedArea(r.pts,null,true)", minor) if not minor.get('error') else None
        ck(chord_only is not None and chord_only < 1e-9,
           "drop the bulge and that region has NO area at all, which is what makes this exact "
           "(%s)" % ('%.9f' % chord_only if chord_only is not None else minor.get('error')))
        ck(not minor.get('error') and any(abs(b) > 1e-9 for b in minor['bulges']),
           "so the curved edge stayed curved (%s)" % (minor.get('error') or minor['bulges']))

        print("\n-- 4. a spur poking into the region")
        SPUR = GRID + [line_obj(5, [0.5, 0], [0.5, 0.4])]
        await set_objs(page, SPUR)
        e2 = await page.evaluate("()=>window.__a3dBoundaryEdges(0,{walls:true,sketches:true,clines:true})")
        sp = await page.evaluate("(e)=>window.__a3dTraceBoundary(e,[0.8,0.8])", e2)
        ck(not sp.get('error') and near(sp['area'], 1, 1e-9),
           "the square still measures exactly 1 with a dead end inside it (%s)"
           % (sp.get('error') or ('%.9f' % sp['area'])))
        ck(not sp.get('error') and len(sp['pts']) > 4,
           "and the loop walks into the spur and back out (%s points)"
           % (sp.get('error') or len(sp['pts'])))

        print("\n-- 5. islands are reported, not absorbed")
        NEST = [{'id': 'ck-o', 't': 'sketch', 'name': 'O', 'col': '#5ec4b8', 'pos': [0, 0, 0],
                 'pts': [[0, 0], [10, 0], [10, 10], [0, 10]], 'y': 0},
                {'id': 'ck-i', 't': 'sketch', 'name': 'I', 'col': '#5ec4b8', 'pos': [0, 0, 0],
                 'pts': [[3, 3], [7, 3], [7, 7], [3, 7]], 'y': 0}]
        await set_objs(page, NEST)
        e3 = await page.evaluate("()=>window.__a3dBoundaryEdges(0,{walls:true,sketches:true,clines:true})")
        between = await page.evaluate("(e)=>window.__a3dTraceBoundary(e,[1,1])", e3)
        ck(not between.get('error') and between['islands'] is True,
           "a point between two nested squares reports an island (%s)"
           % (between.get('error') or between['islands']))
        inside = await page.evaluate("(e)=>window.__a3dTraceBoundary(e,[5,5])", e3)
        ck(not inside.get('error') and inside['islands'] is False
           and near(inside['area'], 16, 1e-9),
           "a point inside the inner square does not (area %s, islands %s)"
           % (inside.get('error') or ('%.6f' % inside['area']),
              inside.get('error') or inside['islands']))

        # ------------------------------------------------- 6. what Room and Floor inherit
        print("\n-- 6. the three fixes Room, Floor and Ceiling inherit")
        # (a) walls that CROSS rather than meet
        await page.evaluate("()=>window.__a3dTestSetObjs([])")
        for a, b in (([-5, 0], [5, 0]), ([-5, 4], [5, 4]), ([0, -5], [0, 5]), ([4, -5], [4, 5])):
            await page.evaluate("(p)=>window.__a3dCurvedWall(p,null,0.3,3,'center',false)",
                                [a, b])
        await page.wait_for_timeout(350)
        face = await page.evaluate("()=>window.__a3dFindEnclosingWallFace([2,2],0)")
        ck(face and near(face['area'], 16, 1e-6),
           "four walls that CROSS now enclose a face of 16 m2 (%s)"
           % (('%.6f' % face['area']) if face else None))

        # (b) a CURVED wall traces as a curve, not as its chord
        await page.evaluate("()=>window.__a3dTestSetObjs([])")
        await page.evaluate(
            "(q)=>window.__a3dCurvedWall([[0,0],[4,0],[4,4],[0,4]],[0,0,q,0],0.3,3,'center',true)",
            Q)
        await page.wait_for_timeout(350)
        cface = await page.evaluate("()=>window.__a3dFindEnclosingWallFace([2,2],0)")
        chord_area = await page.evaluate(
            "()=>window.__a3dBulgedArea([[0,0],[4,0],[4,4],[0,4]],null,true)")
        ck(cface and abs(cface['area'] - chord_area) > 0.5,
           "a curved wall no longer traces as its chord: %s vs the chord polygon's %.4f"
           % (('%.6f' % cface['area']) if cface else None, chord_area))
        ck(cface and cface.get('bulges') and any(abs(b) > 1e-9 for b in cface['bulges']),
           "the face it returns carries the curve (%s)"
           % (cface.get('bulges') if cface else None))
        ck(cface and len(cface['pts']) > 4,
           "while pts stays FLATTENED, so Room and Floor read it as they always did (%s)"
           % (len(cface['pts']) if cface else None))

        # (c) a MOVED wall traces where it is now, not where it was
        await page.evaluate("()=>window.__a3dTestSetObjs([])")
        ids = []
        for a, b in (([0, 0], [6, 0]), ([6, 0], [6, 6]), ([6, 6], [0, 6]), ([0, 6], [0, 0])):
            ids.append(await page.evaluate(
                "(p)=>window.__a3dCurvedWall(p,null,0.3,3,'center',false)", [a, b]))
        await page.wait_for_timeout(350)
        before_face = await page.evaluate("()=>window.__a3dFindEnclosingWallFace([3,3],0)")
        ck(before_face and near(before_face['area'], 36, 1e-6),
           "a square of four walls encloses 36 m2 (%s)"
           % (('%.6f' % before_face['area']) if before_face else None))
        await page.evaluate("(id)=>window.__a3dSetPos(id,0,0,20)", ids[0])
        await page.wait_for_timeout(250)
        after_face = await page.evaluate("()=>window.__a3dFindEnclosingWallFace([3,3],0)")
        ck(after_face is None,
           "move one wall 20 m away and the room is gone -- it used to go on bounding the room "
           "from where it no longer is (%s)"
           % (('area %.3f' % after_face['area']) if after_face else 'gone'))

        # ------------------------------------------------- 7. Room still works end to end
        print("\n-- 7. Room still works on the replaced tracer")
        await page.keyboard.press('Escape')      # BOUNDARY is still live from section 2
        await page.wait_for_timeout(150)
        await page.evaluate("()=>window.__a3dTestSetObjs([])")
        for a, b in (([0, 0], [6, 0]), ([6, 0], [6, 6]), ([6, 6], [0, 6]), ([0, 6], [0, 0])):
            await page.evaluate("(p)=>window.__a3dCurvedWall(p,null,0.3,3,'center',false)",
                                [a, b])
        await page.wait_for_timeout(350)
        await palette_run(page, 'ROOM')
        st = await page.evaluate("()=>window.__a3dState()")
        if st['sk'] and st['sk']['tool'] == 'room':
            await page.evaluate("()=>window.__a3dPlacePoint(3,3)")
            await page.wait_for_timeout(450)
            rooms = [o for o in (await page.evaluate("()=>window.__a3dState().objs"))
                     if o.get('t') == 'room']
            ck(len(rooms) == 1, "clicking inside makes a room (%d)" % len(rooms))
            ck(rooms and rooms[0].get('area', 0) > 30,
               "of a sensible area (%s)" % (rooms[0].get('area') if rooms else None))
        else:
            ck(False, "ROOM did not start from the palette (%s)" % (st['sk'],))

        # ------------------------------------------------- 7b. the BIM toolset, from the
        # command line for the first time. Found by this suite: typing ROOM started BOUNDARY,
        # because there was no ROOM command -- nor any of the other ten.
        print("\n-- 7b. the BIM toolset is reachable from the command line")
        BIM_CMDS = [('ROOM', 'room'), ('FLOOR', 'floor'), ('CEILING', 'ceiling'),
                    ('ROOF', 'roof'), ('STAIR', 'stair'), ('COLUMN', 'column'),
                    ('BEAM', 'beam'), ('DOOR', 'door'), ('WINDOW', 'window'),
                    ('GRIDLINE', 'grid'), ('SECTION', 'section')]
        for cmd, tool in BIM_CMDS:
            await page.keyboard.press('Escape')
            await page.wait_for_timeout(110)
            await palette_run(page, cmd)
            st = await page.evaluate("()=>window.__a3dState()")
            got = st['sk']['tool'] if st['sk'] else None
            ck(got == tool, "%s starts the %s tool (%s)" % (cmd, tool, got))
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(150)
        # GRID must still mean grid snap, not the structural gridline tool
        snap_before = await page.evaluate("()=>window.__a3dSnapState().grid")
        await palette_run(page, 'GRID')
        st = await page.evaluate("()=>window.__a3dState()")
        snap_after = await page.evaluate("()=>window.__a3dSnapState().grid")
        ck((st['sk'] is None) and snap_after != snap_before,
           "GRID still toggles grid snap rather than being hijacked by the gridline tool "
           "(%s -> %s, sk %s)" % (snap_before, snap_after, st['sk']))

        # ------------------------------------------------- 8. no second tracer
        print("\n-- 8. the old tracer is gone, not parked")
        src = await page.evaluate("()=>document.documentElement.outerHTML.length")
        for gone in ('bimCollectWallSegments', 'bimBuildWallGraph', 'bimTraceFaces'):
            present = await page.evaluate("(n)=>document.documentElement.outerHTML.indexOf(n)>=0",
                                          gone)
            ck(not present, "%s is deleted, not left beside the new tracer" % gone)
        ck(src > 0, "page source readable (%d chars)" % src)
        # the derived area still reports a magnitude
        cw = await page.evaluate("()=>window.__a3dBulgedArea([[0,3],[4,3],[4,0],[0,0]],null,true)")
        sg = await page.evaluate("()=>window.__a3dBulgedSignedArea([[0,3],[4,3],[4,0],[0,0]],null,true)")
        ck(near(cw, 12) and sg < 0,
           "a clockwise ring: area 12 and signed area negative, from one formula (%.4f / %.4f)"
           % (cw, sg))

        print("\n-- 9. refusals")
        await page.evaluate("()=>window.__a3dTestSetObjs([])")
        empty = await page.evaluate("()=>window.__a3dTraceBoundary([],[0,0])")
        ck(bool(empty.get('error')), "no geometry at all is refused (%s)" % empty.get('error'))
        one = await page.evaluate(
            "()=>window.__a3dTraceBoundary([{a:[0,0],b:[5,0],bulge:0}],[1,1])")
        ck(bool(one.get('error')), "a single line encloses nothing (%s)" % one.get('error'))
        big = await page.evaluate("""()=>{
          var e=[],i;for(i=0;i<420;i++)e.push({a:[i,-1],b:[i,1],bulge:0});
          return window.__a3dTraceBoundary(e,[0,0]);}""")
        ck(bool(big.get('error')) and 'limit' in big['error'],
           "and too much geometry is refused rather than hung on (%s)" % big.get('error'))

        print("\n-- 10. hygiene")
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
