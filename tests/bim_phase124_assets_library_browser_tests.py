#!/usr/bin/env python3
"""bim_phase124_assets_library_browser_tests.py -- V124: the Assets library.

The owner, in V119: Assets "should be blocks templates premade for easy drag and drop into the project
not an overview of stuff"; in V123, the library "can be built upon from time to time like when I go
online and collect items, obj, or import models" and is "a way to quickly drag and drop stuff".

Every claim is driven with real pointer, key and file-chooser events and asserted on the MODEL and the
stored library -- positions, levels, links, undo, what is stored -- never on how the screen looks.

  1. THE STORE: a starter set of nine models at real sizes, each with a thumbnail; an entry stored
     before V124 (no kind, no thumbnail) is a model, and gets a thumbnail that is kept.
  2. CLICK: a model tile places at the centre of the view, not the origin, and leaves it selected.
  3. DRAG AND DROP: a real pointer drag from a tile onto the drawing places at the drop point on the
     active level -- the placed point projects back to where the pointer was let go -- and snaps to a
     point it is let go near; a card follows the pointer; a press that does not travel is a click; a
     drag let go off the drawing, or ended with Escape, places nothing; the click a drag leaves
     behind places nothing.
  4. BLOCKS: the Block button saves the selection's records, leaving out room tags and saying so; a
     block dragged onto another level lands on it at its elevation, its room follows its NEW wall, a
     link to an object outside the block is dropped and announced, one Undo takes it all back.
  5. MODEL: the Model button saves every selected solid as one mesh.
  6. IMPORT: an OBJ with no unit -- the dialog's first guess, the size it shows for each unit and up
     axis, and what the library stores.
  7. ON AN OBJECT: a material, a wall type and a pattern dropped on an object go on THAT object with
     nothing selected; a pattern dropped on nothing changes nothing.
  8. THE PANEL: search keeps its focus and finds by name; a group header folds; remove asks first and
     a starter model has no remove button; the Project Browser's Families are the models only.
  9. TEMPLATES: a template opens a new project that is a copy of it; the project it came from and
     the template are unchanged; removing it removes its stored project.
 10. COMMANDS: BLOCK, INSERT, ASSETS on the command line and the ribbon's Component; the shell audit
     is clean with every new control on screen.

The harness never waits without a bound: every page step has STALL seconds, and a stall or an
exception is a FAIL naming where it stopped (V123).
"""
import asyncio, pathlib, sys, tempfile, traceback
from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'


class Checks:
    def __init__(self):
        self.n, self.bad = 0, []

    def __call__(self, cond, msg):
        self.n += 1
        if not cond:
            self.bad.append(msg)
        print(('  ok    ' if cond else '  FAIL  ') + msg)


CK = Checks()
STALL = 60


class Stalled(Exception):
    pass


async def within(aw, what):
    try:
        return await asyncio.wait_for(aw, STALL)
    except asyncio.TimeoutError:
        raise Stalled(what)


def near(a, b, tol=1e-6):
    return a is not None and b is not None and abs(a - b) <= tol


LEGACY = {"id": "fam-legacy-1", "name": "Old Crate", "category": "Other", "manufacturer": "",
          "mesh": {"v": [[-0.5, 0, -0.5], [0.5, 0, -0.5], [0.5, 1, -0.5], [-0.5, 1, -0.5],
                         [-0.5, 0, 0.5], [0.5, 0, 0.5], [0.5, 1, 0.5], [-0.5, 1, 0.5]],
                   "f": [[0, 1, 2, 3], [5, 4, 7, 6], [4, 0, 3, 7], [1, 5, 6, 2], [3, 2, 6, 7], [4, 5, 1, 0]],
                   "size": [1, 1, 1]},
          "createdAt": "2026-01-01T00:00:00.000Z"}

# a box 450 wide, 900 high, 450 deep, drawn in millimetres with Y up
OBJ_MM = "\n".join(["o crate"] + ["v %g %g %g" % p for p in [
    (-225, 0, -225), (225, 0, -225), (225, 900, -225), (-225, 900, -225),
    (-225, 0, 225), (225, 0, 225), (225, 900, 225), (-225, 900, 225)]] +
    ["f 1 2 3 4", "f 6 5 8 7", "f 5 1 4 8", "f 2 6 7 3", "f 4 3 7 8", "f 5 6 2 1"]) + "\n"


async def run():
    ck = CK
    tmp = pathlib.Path(tempfile.mkdtemp(prefix='v124_'))
    blank = tmp / 'blank.html'
    blank.write_text('<!doctype html><title>seed</title>')
    objf = tmp / 'crate_mm.obj'
    objf.write_text(OBJ_MM)
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1600, 'height': 950})
        page = await ctx.new_page()

        def guard(obj, names):
            for nm in names:
                def make(f, nm):
                    async def g(*a, **k):
                        return await within(f(*a, **k), '%s %s' % (nm, str(a[:1])[:40]))
                    return g
                setattr(obj, nm, make(getattr(obj, nm), nm))
        guard(page.keyboard, ('type', 'press', 'down', 'up'))
        guard(page.mouse, ('move', 'down', 'up', 'click', 'dblclick'))
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        dialog_answer = {'accept': True, 'seen': []}

        async def on_dialog(d):
            dialog_answer['seen'].append(d.message)
            if dialog_answer['accept']:
                await d.accept()
            else:
                await d.dismiss()
        page.on('dialog', lambda d: asyncio.ensure_future(on_dialog(d)))

        # an entry stored before V124 -- no kind, no thumbnail -- seeded from a blank page on the
        # same origin with the app closed (V115: never from an init script)
        await page.goto('file://' + str(blank))
        await page.evaluate("(e)=>{localStorage.setItem('acad3dFamilyLibrary',JSON.stringify([e]));}", LEGACY)
        await page.goto('file://' + str(HTML))
        await page.wait_for_timeout(2300)

        async def safe(js, arg=None):
            try:
                return await within(page.evaluate(js, arg) if arg is not None else page.evaluate(js),
                                    'evaluate ' + js[:60].replace('\n', ' '))
            except Stalled:
                raise
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:200])
                return None

        has = await safe("()=>!!window.__acad3dV124")
        ck(bool(has), "__acad3dV124 marker is present")
        if not has:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.bad), ck.n))
            await browser.close()
            return 1

        async def blur():
            await safe("()=>{if(document.activeElement&&document.activeElement.blur)document.activeElement.blur();}")
            await page.wait_for_timeout(60)

        async def tab(name):
            await page.click('#a3d-rail .a3d-railbtn[data-tab="%s"]' % name)
            await page.wait_for_timeout(250)

        async def lib():
            return await safe("()=>window.__a3dLibrary()") or []

        async def n_objs():
            return await safe("()=>window.__a3dState().objs.length")

        async def ids():
            return await safe("()=>window.__a3dState().objs.map(o=>o.id)") or []

        async def toast():
            return await safe("()=>{var t=document.getElementById('a3d-toast');return t?t.textContent:'';}") or ''

        async def centre_of(sel):
            """the viewport centre of an element, scrolled into view first; None when there is none"""
            return await safe("""(s)=>{var e=document.querySelector(s);if(!e)return null;
              e.scrollIntoView({block:'center'});var r=e.getBoundingClientRect();
              if(r.width<2||r.height<2)return null;return [r.left+r.width/2,r.top+r.height/2];}""", sel)

        async def crect():
            return await safe("()=>window.__a3dCanvasRect()")

        async def drag(frm, to, steps=14, mid=None):
            """a real pointer drag; mid, when given, runs after the last move and before the release.
            A missing end -- a row folded away, an element not drawn -- is no drag: the check that
            follows fails, and the suite goes on measuring (V89: a suite must fail, not throw)."""
            if not frm or not to:
                print('      (no drag: an end is missing -- %s -> %s)' % (frm, to))
                return None
            await page.mouse.move(frm[0], frm[1])
            await page.mouse.down()
            for i in range(1, steps + 1):
                await page.mouse.move(frm[0] + (to[0] - frm[0]) * i / steps, frm[1] + (to[1] - frm[1]) * i / steps)
            r = None
            if mid:
                r = await mid()
            await page.mouse.up()
            await page.wait_for_timeout(350)
            return r

        async def canvas_pt(fx, fy):
            """a whole-pixel viewport point at a fraction of the drawing area"""
            r = await crect()
            return [round(r['left'] + r['width'] * fx), round(r['top'] + r['height'] * fy)]

        async def projects_to(pos, vp):
            """how far a world point lands from a viewport point, in pixels"""
            r = await crect()
            s = await safe("(p)=>window.__a3dProject(p)", pos)
            if not s or not r:
                return None
            return ((s['x'] + r['left'] - vp[0]) ** 2 + (s['y'] + r['top'] - vp[1]) ** 2) ** 0.5

        try:
            # ---------------------------------------------------------------------------------
            print("\n-- 1. the store: a starter set, and an old entry is a model with a thumbnail")
            await tab('assets')
            L = await lib()
            starters = [e for e in L if e['builtin']]
            ck(len(starters) == 9 and all(e['kind'] == 'model' for e in starters),
               "nine starter models (%s)" % [e['name'] for e in starters])
            size = {e['name']: e['size'] for e in starters}
            ck(size.get('Chair') and near(size['Chair'][0], 0.45, 1e-9) and near(size['Chair'][2], 0.45, 1e-9)
               and 0.85 < size['Chair'][1] < 1.0,
               "at real sizes: the chair is 0.45 m square and under a metre high (%s)" % size.get('Chair'))
            ck(size.get('Dining table') and near(size['Dining table'][0], 1.6, 1e-9) and near(size['Dining table'][1], 0.75, 1e-9),
               "the table 1.6 m long and 0.75 m high (%s)" % size.get('Dining table'))
            imgs = await safe("""()=>Array.prototype.map.call(document.querySelectorAll('#a3d-leftpanel [data-a3dassets^="family:builtin:"] img'),
                                   function(i){return (i.getAttribute('src')||'').slice(0,22);})""") or []
            ck(len(imgs) == 9 and all(s == 'data:image/png;base64,' for s in imgs),
               "each shows a drawn thumbnail (%d)" % len(imgs))
            old = [e for e in L if e['id'] == 'fam-legacy-1']
            ck(len(old) == 1 and old[0]['kind'] == 'model',
               "an entry stored before V124, with no kind, is a model (%s)" % old)
            stored = await safe("""()=>{var a=JSON.parse(localStorage.getItem('acad3dFamilyLibrary')||'[]');
                                   var e=a.filter(function(x){return x.id==='fam-legacy-1';})[0];
                                   return e?{kind:e.kind||null,thumb:(e.thumb||'').slice(0,14)}:null;}""")
            ck(stored and stored['thumb'] == 'data:image/png' and stored['kind'] is None,
               "and it is given a thumbnail that is kept, while nothing else of it is rewritten (%s)" % stored)
            ck(await safe("()=>!!document.querySelector('#a3d-leftpanel [data-a3dasdel=\"fam-legacy-1\"]')") and
               not await safe("()=>!!document.querySelector('#a3d-leftpanel [data-a3dasdel^=\"builtin:\"]')"),
               "the user's entry has a remove button and no starter model does")

            # ---------------------------------------------------------------------------------
            print("\n-- 2. a click places at the centre of the view, and leaves it selected")
            await safe("""()=>{window.__a3dTestSetObjs([]);
              var w=window.__a3dWall([[30,20],[34,20]],0.3,3,'center',false);
              window.__a3dSelectFor([w]);window.__a3dZoomToSelection();window.__a3dSelectFor([]);return w;}""")
            await page.wait_for_timeout(500)
            vc = await safe("()=>window.__a3dViewCentrePlan()")
            n0 = await n_objs()
            c = await centre_of('#a3d-leftpanel [data-a3dassets="family:builtin:chair"]')
            if c:
                await page.mouse.click(c[0], c[1])
            await page.wait_for_timeout(400)
            st = await safe("()=>{var s=window.__a3dState(),o=s.objs.filter(x=>x.id===s.sel)[0];return o?{n:s.objs.length,pos:o.pos,name:o.name,fam:o.bim&&o.bim.familyId}:{n:s.objs.length};}")
            ck(st and st['n'] == n0 + 1 and st.get('fam') == 'builtin:chair',
               "clicking the Chair tile adds one chair, left selected (%s)" % st)
            ck(st and vc and st.get('pos') and near(st['pos'][0], vc[0], 1e-6) and near(st['pos'][2], vc[1], 1e-6)
               and abs(vc[0]) > 5,
               "at the centre of the view (%s), not the level's origin (%s)" % (vc, st and st.get('pos')))

            # ---------------------------------------------------------------------------------
            print("\n-- 3. drag and drop")
            await safe("()=>{window.__a3dTestSetObjs([]);window.__a3dSelectFor([]);}")
            await page.wait_for_timeout(300)
            src = await centre_of('#a3d-leftpanel [data-a3dassets="family:builtin:table"]')
            dst = await canvas_pt(0.62, 0.42)
            n0 = await n_objs()

            async def during():
                return await safe("""()=>{var g=document.querySelector('.a3d-asghost');
                  return {ghost:!!g,ok:!!(g&&g.classList.contains('ok')),dragging:window.__a3dAssetsUI().dragging};}""")
            mid = await drag(src, dst, mid=during) if src else None
            ck(mid and mid['ghost'] and mid['ok'] and mid['dragging'],
               "while dragging, a card follows the pointer and is marked over the drawing (%s)" % mid)
            ck(await safe("()=>!document.querySelector('.a3d-asghost')"), "and it goes when the pointer is let go")
            st = await safe("()=>{var s=window.__a3dState(),o=s.objs.filter(x=>x.id===s.sel)[0];return o?{n:s.objs.length,pos:o.pos,fam:o.bim&&o.bim.familyId,lvl:o.bim&&o.bim.levelId}:{n:s.objs.length};}")
            ck(st and st['n'] == n0 + 1 and st.get('fam') == 'builtin:table',
               "dropping the table tile on the drawing adds exactly one table -- the click a drag leaves behind places nothing (%s)" % st)
            d = await projects_to(st.get('pos'), dst) if st and st.get('pos') else None
            ck(d is not None and d < 1.0,
               "where it was let go: its point projects back to the drop point (%.3f px)" % (d if d is not None else -1))
            ck(st and st.get('pos') and near(st['pos'][1], 0.0, 1e-9), "on the active level's elevation (%s)" % (st and st.get('pos')))

            # a press that does not travel is a click -- the view centre, not the pointer
            vc = await safe("()=>window.__a3dViewCentrePlan()")
            src = await centre_of('#a3d-leftpanel [data-a3dassets="family:builtin:desk"]')
            if src:
                await page.mouse.move(src[0], src[1])
                await page.mouse.down()
                await page.mouse.move(src[0] + 2, src[1] + 1)
                await page.mouse.up()
            await page.wait_for_timeout(400)
            st = await safe("()=>{var s=window.__a3dState(),o=s.objs.filter(x=>x.id===s.sel)[0];return o?{pos:o.pos,fam:o.bim&&o.bim.familyId}:null;}")
            ck(st and st['fam'] == 'builtin:desk' and near(st['pos'][0], vc[0], 1e-6) and near(st['pos'][2], vc[1], 1e-6),
               "a press that moves less than the click distance is a click: the desk goes to the view centre (%s)" % st)

            # snapped to a point it is let go near
            vc = await safe("()=>window.__a3dViewCentrePlan()")
            E = [round(vc[0]) + 2, round(vc[1]) + 3]
            wid = await safe("(e)=>{var w=window.__a3dWall([[e[0]-4,e[1]],e],0.2,3,'center',false);window.__a3dSelectFor([]);return w;}", E)
            await page.wait_for_timeout(300)
            r = await crect()
            corner = await safe("(e)=>window.__a3dProject([e[0],0,e[1]])", E)
            n0 = await n_objs()
            if corner and r:
                tgt = [round(r['left'] + corner['x'] + 5), round(r['top'] + corner['y'] - 4)]
                src = await centre_of('#a3d-leftpanel [data-a3dassets="family:builtin:cabinet"]')
                await drag(src, tgt)
            st = await safe("()=>{var s=window.__a3dState(),o=s.objs.filter(x=>x.id===s.sel)[0];return o?{n:s.objs.length,pos:o.pos,fam:o.bim&&o.bim.familyId}:null;}")
            ck(st and st['n'] == n0 + 1 and st['fam'] == 'builtin:cabinet' and near(st['pos'][0], E[0], 1e-6) and near(st['pos'][2], E[1], 1e-6),
               "let go a few pixels from the wall's end, it snaps to the end exactly, as a click of the family tool does (%s)" % (st and st['pos']))

            # let go off the drawing: nothing
            n0 = await n_objs()
            src = await centre_of('#a3d-leftpanel [data-a3dassets="family:builtin:sofa"]')
            off = await centre_of('#a3d-leftpanel .a3d-asnote')
            await drag(src, [off[0] + 40, off[1]] if off else None)
            ck(await n_objs() == n0 and 'Drop onto the drawing' in await toast(),
               "let go over the panel, nothing is placed, and it says where to drop (%r)" % await toast())
            # out and back onto its own tile: the browser sends a click with that release, and it is
            # the drag's -- not a placement at the view centre
            n0 = await n_objs()
            src = await centre_of('#a3d-leftpanel [data-a3dassets="family:builtin:sofa"]')
            if src:
                await page.mouse.move(src[0], src[1])
                await page.mouse.down()
                for i in range(1, 8):
                    await page.mouse.move(src[0] + 12 * i, src[1] + 3 * i)
                for i in range(1, 8):
                    await page.mouse.move(src[0] + 84 - 12 * i, src[1] + 21 - 3 * i)
                await page.mouse.up()
            await page.wait_for_timeout(350)
            ck(await n_objs() == n0,
               "a drag that comes back to its own tile and is let go there places nothing: the click that "
               "release sends is the drag's (%d -> %d)" % (n0, await n_objs()))
            # Escape mid-drag: nothing
            dst = await canvas_pt(0.55, 0.55)

            async def esc_mid():
                await page.keyboard.press('Escape')
                await page.wait_for_timeout(80)
                return await safe("()=>({ghost:!!document.querySelector('.a3d-asghost'),dragging:window.__a3dAssetsUI().dragging})")
            m2 = await drag(src, dst, mid=esc_mid)
            ck(m2 and not m2['ghost'] and not m2['dragging'] and await n_objs() == n0,
               "Escape during a drag ends it: no card, and nothing placed when the pointer is let go (%s)" % m2)

            # ---------------------------------------------------------------------------------
            print("\n-- 4. blocks")
            await safe("()=>{window.__a3dTestSetObjs([]);window.__a3dTestClearUndo();}")
            b4 = await safe("""()=>{var w=window.__a3dWall([[0,0],[6,0],[6,4],[0,4]],0.2,3,'center',true);
              var r=window.__a3dCreateRoomAt([3,2],0);var tg=window.__a3dTagRoomAt([3,2]);
              window.__a3dSelectFor([w,r,tg]);return {w:w,r:r,tg:tg,rs:window.__a3dObjSnapshot(r).sourceId};}""")
            ck(b4 and b4['w'] and b4['r'] and b4['tg'] and b4['rs'] == b4['w'],
               "a scene: a closed wall, a room built on it, and the room's tag (%s)" % b4)
            await tab('browser')
            await tab('assets')
            await page.click('#a3d-leftpanel [data-a3dasact="block"]')
            await page.wait_for_timeout(300)
            note = await safe("()=>{var d=document.querySelector('.a3d-dlg');return d?d.textContent:'';}") or ''
            ck('Save as Block' in note and '2 object(s)' in note and '1 opening(s) or room tag(s) are not included' in note,
               "the Block button asks for a name, and says the tag is left out (%r)" % note[:160])
            await page.fill('.a3d-dlg [data-a3dp="name"]', 'Studio unit')
            await page.keyboard.press('Enter')
            await page.wait_for_timeout(300)
            blk = [e for e in await lib() if e['kind'] == 'block']
            ck(len(blk) == 1 and blk[0]['name'] == 'Studio unit' and blk[0]['count'] == 2 and blk[0]['thumb'],
               "the library has the block: two objects, with a plan thumbnail (%s)" % blk)
            bid = blk[0]['id'] if blk else ''
            stored = await safe("""(id)=>{var a=JSON.parse(localStorage.getItem('acad3dFamilyLibrary')||'[]');
              var e=a.filter(function(x){return x.id===id;})[0];
              return e?{kinds:e.recs.map(function(r){return r.t+':'+((r.bim&&r.bim.type)||'')}),base:e.base,y0:e.y0}:null;}""", bid)
            ck(stored and sorted(stored['kinds']) == ['room:', 'solid:wall'] and near(stored['base'][0], 3, 1e-9)
               and near(stored['base'][1], 2, 1e-9) and stored['y0'] == 0,
               "stored as the objects' own records -- a wall and a room -- with its base at their centre (%s)" % stored)
            # onto another level, by a drag
            lv = await safe("()=>{window.__a3dAddLevel();return window.__a3dActiveLevel();}")
            await safe("()=>window.__a3dSelectFor([])")
            await safe("()=>{window.__a3dTestClearUndo();}")
            before = await ids()
            A3D_GROUP_OPEN = await safe("()=>!window.__a3dAssetsUI().closed.blocks")
            src = await centre_of('#a3d-leftpanel [data-a3dassets="block:%s"]' % bid)
            dst = await canvas_pt(0.7, 0.35)
            await drag(src, dst)
            after = await ids()
            new = [i for i in after if i not in before]
            snaps = await safe("(ids)=>ids.map(function(i){return window.__a3dObjSnapshot(i);})", new) or []
            wall = [o for o in snaps if o.get('bim') and o['bim'].get('type') == 'wall']
            room = [o for o in snaps if o.get('t') == 'room']
            ck(A3D_GROUP_OPEN and len(new) == 2 and len(wall) == 1 and len(room) == 1,
               "dragging the block onto the drawing inserts a wall and a room (%s)" % [o.get('name') for o in snaps])
            if wall and room and lv:
                W, R = wall[0], room[0]
                ck(near(W['bim']['baseY'], lv['elev'], 1e-9) and W['bim'].get('levelId') == lv['id']
                   and near(R['y'], lv['elev'], 1e-9) and R.get('levelId') == lv['id'],
                   "on the active level, at its elevation (%s m): wall base %s, room %s"
                   % (lv['elev'], W['bim']['baseY'], R['y']))
                cl = W['bim']['centerline']
                cx = (min(p[0] for p in cl) + max(p[0] for p in cl)) / 2
                cz = (min(p[1] for p in cl) + max(p[1] for p in cl)) / 2
                d = await projects_to([cx, lv['elev'], cz], dst)
                ck(d is not None and d < 1.0, "its base point where it was let go (%.3f px)" % (d if d is not None else -1))
                ck(R.get('sourceId') == W['id'] and R.get('sourceType') == 'wall',
                   "the new room's source is the NEW wall, not the one the block was made from (%s)" % R.get('sourceId'))
                a0 = R.get('area')
                await safe("(a)=>window.__a3dDragWallGripTo(a[0],1,a[1],a[2])",
                           [W['id'], cl[1][0] + 2, cl[1][1]])
                await page.wait_for_timeout(300)
                a1 = await safe("(id)=>window.__a3dObjSnapshot(id).area", R['id'])
                a_orig = await safe("(id)=>window.__a3dObjSnapshot(id).area", b4['r'])
                ck(a1 is not None and a0 is not None and a1 > a0 + 1 and near(a_orig, 22.04, 1e-6),
                   "and follows it: the new wall moved, the new room grew (%s -> %s m2) and the original did not (%s)"
                   % (a0, a1, a_orig))
                await safe("()=>window.__a3dUndo()")
                await page.wait_for_timeout(250)
            ck(await safe("(ids)=>{var a=window.__a3dState().objs.map(o=>o.id);return a;}", None) is not None, "the scene is readable")
            await safe("()=>window.__a3dUndo()")
            await page.wait_for_timeout(300)
            ck(sorted(await ids()) == sorted(before),
               "Undo takes the whole insert back in one step: exactly the objects before it are left")
            # a link to something outside the block is dropped, and said
            b2 = await safe("(r)=>window.__a3dBlockSave('Room alone',[r])", b4['r'])
            got = await safe("(id)=>window.__a3dBlockInsert(id,40,40)", b2) or []
            rr = await safe("(id)=>window.__a3dObjSnapshot(id)", got[0]) if got else None
            ck(rr and rr.get('sourceId') is None and 'link(s) to objects outside the block were not kept' in await toast(),
               "a room saved without its wall comes in on its own, and the insert says a link was not kept (%r)" % await toast())

            # a hatch traced inside a sketch: a copy follows the copy it was made with, never the original
            hs = await safe("""()=>{window.__a3dTestSetObjs([]);
              var s=window.__a3dSketch('rect',[[40,40],[44,43]]);var h=window.__a3dApplyHatchAt([42,41.5],window.__a3dObjSnapshot(s).y,{pattern:'ansi31'});
              var both=window.__a3dBlockSave('Hatched',[s,h]),alone=window.__a3dBlockSave('Hatch alone',[h]);
              var a=window.__a3dBlockInsert(both,60,60)||[],b=window.__a3dBlockInsert(alone,80,80)||[];
              var snap=function(i){return window.__a3dObjSnapshot(i);};
              var ns=a.filter(function(i){return snap(i).t==='sketch';})[0],nh=a.filter(function(i){return snap(i).t!=='sketch';})[0];
              return {s:s,h:h,ns:ns,nh:nh,lone:b[0]};}""")
            if hs and hs.get('ns') and hs.get('nh') and hs.get('lone'):
                lone0 = await safe("(id)=>window.__a3dObjSnapshot(id).pts", hs['lone'])
                await safe("(a)=>window.__a3dDragGripTo(a[0],2,50,50)", [hs['s']])
                await page.wait_for_timeout(500)
                await safe("(a)=>window.__a3dDragGripTo(a[0],2,63,66)", [hs['ns']])
                await page.wait_for_timeout(500)
                got = await safe("""(h)=>({orig:window.__a3dObjSnapshot(h.h).pts,ins:window.__a3dObjSnapshot(h.nh).pts,
                                        lone:window.__a3dObjSnapshot(h.lone).pts})""", hs)
                ck(got and [50, 50] in got['orig'] and [63, 66] in got['ins'] and [50, 50] not in got['ins'],
                   "a hatch inserted with its sketch follows the INSERTED sketch, and not the original's (%s)" % (got and got['ins']))
                ck(got and got['lone'] == lone0,
                   "a hatch inserted without its sketch stays where it was put when the original's sketch moves (%s)" % (got and got['lone'][:2]))
            else:
                ck(False, "a hatch traced inside a sketch, saved in a block with and without it (%s)" % hs)
            # a footing is copied as its whole record, host and all: with its column it takes the new
            # column as host; alone it takes none -- never the original's column
            ft = await safe("""()=>{window.__a3dTestSetObjs([]);
              var c=window.__a3dColumnAt([10,10],window.__a3dActiveLevel().elev,0.4,0.4,3),f=window.__a3dAddFootingUnder(c);
              var both=window.__a3dBlockSave('Column and footing',[c,f]),alone=window.__a3dBlockSave('Footing',[f]);
              var a=window.__a3dBlockInsert(both,30,30)||[],b=window.__a3dBlockInsert(alone,50,50)||[];
              var snap=function(i){return window.__a3dObjSnapshot(i);};
              var nc=a.filter(function(i){return snap(i).bim.type==='column';})[0],nf=a.filter(function(i){return snap(i).bim.type==='footing';})[0];
              return {c:c,f:f,nc:nc,nfHost:nf?snap(nf).bim.hostId:'missing',loneHost:b.length?snap(b[0]).bim.hostId:'missing',
                      origHost:snap(f).bim.hostId};}""")
            ck(ft and ft['nc'] and ft['nfHost'] == ft['nc'] and ft['loneHost'] is None and ft['origHost'] == ft['c'],
               "a footing inserted with its column is hosted by the NEW column; inserted alone, by none -- not the original's (%s)" % ft)
            # the same fault, as it was in V123: Ctrl+D a traced hatch, then edit its sketch
            dd = await safe("""()=>{window.__a3dTestSetObjs([]);
              var s=window.__a3dSketch('rect',[[40,40],[44,43]]);var h=window.__a3dApplyHatchAt([42,41.5],window.__a3dObjSnapshot(s).y,{pattern:'ansi31'});
              window.__a3dSelectFor([h]);return {s:s,h:h};}""")
            await blur()
            await page.keyboard.press('Control+d')
            await page.wait_for_timeout(400)
            cp = await safe("()=>window.__a3dState().sel")
            p0 = await safe("(id)=>window.__a3dObjSnapshot(id).pts", cp)
            await safe("(a)=>window.__a3dDragGripTo(a[0],2,50,50)", [dd and dd['s']])
            await page.wait_for_timeout(500)
            p1 = await safe("(id)=>window.__a3dObjSnapshot(id).pts", cp)
            ck(dd and cp and cp != dd['h'] and p0 and p1 == p0 and 'link(s) to shapes that were not copied' in (await toast()),
               "Ctrl+D on a traced hatch: the copy stays where it was put when the original's sketch is edited -- "
               "it used to re-trace onto the original -- and the duplicate says why (%s -> %s)" % (p0 and p0[:2], p1 and p1[:2]))

            # ---------------------------------------------------------------------------------
            print("\n-- 5. the Model button saves every selected solid as one mesh")
            await safe("""()=>{window.__a3dTestSetObjs([]);
              var a=window.__a3dColumnAt([0,0],0,0.4,0.4,3),b=window.__a3dColumnAt([2,0],0,0.4,0.4,2);
              window.__a3dSelectFor([a,b]);}""")
            await tab('browser')
            await tab('assets')
            await page.click('#a3d-leftpanel [data-a3dasact="model"]')
            await page.wait_for_timeout(300)
            await page.fill('.a3d-dlg [data-a3dp="name"]', 'Two posts')
            await page.keyboard.press('Enter')
            await page.wait_for_timeout(300)
            m = [e for e in await lib() if e['name'] == 'Two posts']
            ck(len(m) == 1 and m[0]['kind'] == 'model' and near(m[0]['size'][0], 2.4, 1e-9) and near(m[0]['size'][1], 3, 1e-9),
               "both columns, where they stand: 2.4 m across and 3 m high (%s)" % (m and m[0]['size']))
            posts = m[0]['id'] if m else ''

            # ---------------------------------------------------------------------------------
            print("\n-- 6. import: an OBJ does not say its unit")
            try:
                async with page.expect_file_chooser(timeout=5000) as fc:
                    await page.click('#a3d-leftpanel [data-a3dasact="import"]')
                chooser = await fc.value
                await chooser.set_files(str(objf))
            except Exception as e:
                print('      (file chooser: %s)' % str(e)[:160])
            await page.wait_for_timeout(600)

            async def dlg():
                return await safe("""()=>{var d=document.querySelector('.a3d-dlg');if(!d)return null;
                  return {head:d.querySelector('.a3d-dlghd').textContent,unit:d.querySelector('[data-a3dp="unit"]').value,
                          up:d.querySelector('[data-a3dp="up"]').value,size:d.querySelector('[data-a3dp="size"]').textContent,
                          thumb:(d.querySelector('[data-a3dp="thumb"]').getAttribute('src')||'').slice(0,14)};}""")
            dd = await dlg()
            ck(dd and dd['head'] == 'Import Model' and dd['unit'] == 'mm' and dd['up'] == 'y',
               "the dialog's first guess for a 900-high file is millimetres, Y up (%s)" % dd)
            ck(dd and dd['size'] == 'Comes in at 0.45 m wide, 0.45 m deep and 0.9 m high' and dd['thumb'] == 'data:image/png',
               "and it shows the size that means, with a picture (%r)" % (dd and dd['size']))
            await page.select_option('.a3d-dlg [data-a3dp="unit"]', 'm')
            dd = await dlg()
            ck(dd and dd['size'] == 'Comes in at 450 m wide, 450 m deep and 900 m high',
               "choosing metres shows what that would mean (%r)" % (dd and dd['size']))
            await page.select_option('.a3d-dlg [data-a3dp="unit"]', 'mm')
            await page.select_option('.a3d-dlg [data-a3dp="up"]', 'z')
            dd = await dlg()
            ck(dd and dd['size'] == 'Comes in at 0.45 m wide, 0.9 m deep and 0.45 m high',
               "Z up turns it: the 900 becomes its depth (%r)" % (dd and dd['size']))
            await page.select_option('.a3d-dlg [data-a3dp="up"]', 'y')
            await page.click('.a3d-dlg [data-a3dlg="ok"]')
            await page.wait_for_timeout(300)
            im = [e for e in await lib() if e['name'] == 'crate_mm']
            ck(len(im) == 1 and im[0]['unit'] == 'mm' and im[0]['source'] == 'crate_mm.obj'
               and near(im[0]['size'][0], 0.45, 1e-9) and near(im[0]['size'][1], 0.9, 1e-9) and near(im[0]['size'][2], 0.45, 1e-9) and im[0]['thumb'],
               "the library stores it at 0.45 x 0.9 x 0.45 m, with its unit and file (%s)" % im)
            g = await safe("""()=>[window.__a3dImportGuess({v:[[0,0,0],[0.5,1.8,0.4]],f:[]}),
                                  window.__a3dImportGuess({v:[[0,0,0],[60,180,40]],f:[]}),
                                  window.__a3dImportGuess({v:[[0,0,0],[30,72,24]],f:[]})]""")
            ck(g == ['m', 'cm', 'in'],
               "the guess reads the size: 1.8 is metres, 180 centimetres, 72 inches (%s)" % g)

            # ---------------------------------------------------------------------------------
            print("\n-- 7. a material, a wall type and a pattern dropped ON an object")
            wid = await safe("""()=>{window.__a3dTestSetObjs([]);var w=window.__a3dWall([[0,0],[8,0]],0.6,3,'center',false);
              window.__a3dSelectFor([w]);window.__a3dZoomToSelection();window.__a3dSelectFor([]);return w;}""")
            await page.wait_for_timeout(500)
            await tab('browser')
            await tab('assets')
            r = await crect()
            on = await safe("()=>window.__a3dProject([3,3,0])")
            tgt = [round(r['left'] + on['x']), round(r['top'] + on['y'])] if on and r else None
            for gid in ('materials', 'walltypes', 'patterns'):
                if await safe("(g)=>window.__a3dAssetsUI().closed[g]", gid):
                    await page.click('#a3d-leftpanel [data-a3dassetgrp="%s"]' % gid)
                    await page.wait_for_timeout(150)
            src = await centre_of('#a3d-leftpanel [data-a3dassets="material:Concrete"]')
            await drag(src, tgt)
            ck(await safe("(id)=>window.__a3dMaterialOf(id)", wid) == 'Concrete' and await safe("()=>window.__a3dState().sel") is None,
               "Concrete dropped on the wall goes on the wall, with nothing selected")
            types = await safe("()=>window.__a3dWallTypes().map(t=>t.id)") or []
            cur = await safe("(id)=>window.__a3dObjSnapshot(id).bim.typeId||null", wid)
            other = [x for x in types if x != cur]
            if other:
                src = await centre_of('#a3d-leftpanel [data-a3dassets="walltype:%s"]' % other[-1])
                await drag(src, tgt)
            ck(other and await safe("(id)=>window.__a3dObjSnapshot(id).bim.typeId", wid) == other[-1],
               "a wall type dropped on it becomes its type (%s)" % (other and other[-1]))
            pats = await safe("()=>window.__a3dAssetRows().filter(r=>r.spec.indexOf('pattern:')===0&&r.spec!=='pattern:none').map(r=>r.spec)") or []
            if pats:
                src = await centre_of('#a3d-leftpanel [data-a3dassets="%s"]' % pats[0])
                await drag(src, tgt)
            ck(pats and await safe("(id)=>window.__a3dResolveGraphics(id,'presentation').pattern", wid) == pats[0].split(':', 1)[1],
               "and a pattern dropped on it goes in its presentation graphics (%s)" % (pats and pats[0]))
            # AMENDED FOR V129: the labelled dock is 24px taller, and 85% down the canvas is now on
            # the dock, which rightly refuses a drop -- the empty spot moves up to 70%
            empty = await canvas_pt(0.15, 0.7)
            n_under = await safe("(p)=>{var r=window.__a3dCanvasRect();return window.__a3dAssetDropAt('pattern:none',p[0]-r.left,p[1]-r.top);}", empty)
            ck(n_under is False, "a pattern dropped on nothing changes nothing (%s)" % n_under)
            if pats:
                n0 = await n_objs()
                src = await centre_of('#a3d-leftpanel [data-a3dassets="%s"]' % pats[-1])
                await drag(src, empty)
                ck(await safe("(id)=>window.__a3dResolveGraphics(id,'presentation').pattern", wid) == pats[0].split(':', 1)[1]
                   and 'Drop a pattern on an element' in await toast(),
                   "-- driven by the pointer too: the wall keeps its pattern and it says why (%r)" % await toast())
            clicked = await safe("()=>window.__a3dAssetClick('material:Steel')")
            ck(clicked is True and await safe("(id)=>window.__a3dMaterialOf(id)", wid) == 'Concrete'
               and 'Select a solid, or drag the material onto one' in await toast(),
               "with nothing selected, clicking a material changes nothing and says what to do (%r)" % await toast())

            # ---------------------------------------------------------------------------------
            print("\n-- 8. the panel")
            await page.click('#a3d-leftpanel [data-a3dassearch]')
            await page.keyboard.type('bed')
            await page.wait_for_timeout(200)
            vis = await safe("""()=>Array.prototype.filter.call(document.querySelectorAll('#a3d-leftpanel [data-a3dassets]'),
                               function(e){return e.offsetParent!==null;}).map(function(e){return e.getAttribute('data-a3dassets');})""")
            foc = await safe("()=>document.activeElement&&document.activeElement.matches('[data-a3dassearch]')&&document.activeElement.value")
            ck(vis == ['family:builtin:bed'] and foc == 'bed',
               "typing 'bed' leaves the double bed alone, and the box keeps its focus as it re-renders (%s, %r)" % (vis, foc))
            await page.keyboard.press('Escape')
            await page.wait_for_timeout(200)
            ck(await safe("()=>window.__a3dAssetsUI().q") == '' and
               len(await safe("()=>window.__a3dAssetRows()") or []) > 30,
               "Escape clears the search and everything is back")
            await blur()
            await page.click('#a3d-leftpanel [data-a3dassetgrp="families"]')
            await page.wait_for_timeout(200)
            hid = await safe("()=>document.querySelector('#a3d-leftpanel [data-a3dassets=\"family:builtin:chair\"]').offsetParent===null")
            await page.click('#a3d-leftpanel [data-a3dassetgrp="families"]')
            await page.wait_for_timeout(200)
            shown = await safe("()=>document.querySelector('#a3d-leftpanel [data-a3dassets=\"family:builtin:chair\"]').offsetParent!==null")
            ck(hid is True and shown is True, "the Models header folds the group and unfolds it (%s, %s)" % (hid, shown))
            # remove asks first
            dialog_answer['accept'] = False
            dialog_answer['seen'] = []
            await page.click('#a3d-leftpanel [data-a3dasdel="%s"]' % posts)
            await page.wait_for_timeout(300)
            still = [e for e in await lib() if e['id'] == posts]
            ck(len(still) == 1 and dialog_answer['seen'] and 'Remove "Two posts"' in dialog_answer['seen'][0],
               "remove asks first, and a No keeps it (%s)" % dialog_answer['seen'])
            dialog_answer['accept'] = True
            await page.click('#a3d-leftpanel [data-a3dasdel="%s"]' % posts)
            await page.wait_for_timeout(300)
            ck(not [e for e in await lib() if e['id'] == posts], "and a Yes removes it from the library")
            # the Project Browser's Families are the models
            await tab('browser')
            await safe("""()=>{var g=document.querySelector('[data-a3dbgrp="families"]');
              if(g&&g.querySelector('.a3d-bcar').textContent.charCodeAt(0)!==0x25be)g.click();}""")
            await page.wait_for_timeout(200)
            fam = await safe("()=>Array.prototype.map.call(document.querySelectorAll('[data-a3dbfam]'),function(e){return e.getAttribute('data-a3dbfam');})") or []
            um = [e['id'] for e in await lib() if e['kind'] == 'model' and not e['builtin']]
            ck(sorted(fam) == sorted(um) and len(um) >= 2,
               "the Project Browser's Families list the user's models, and no block or template (%s)" % fam)

            # ---------------------------------------------------------------------------------
            print("\n-- 9. templates")
            await safe("""()=>{window.__a3dTestSetObjs([]);window.__a3dWall([[0,0],[5,0]],0.2,3,'center',false);
              window.__a3dWall([[0,2],[5,2]],0.2,3,'center',false);window.__a3dSetModelField('project','Harbour Base');}""")
            await page.wait_for_timeout(400)
            await tab('assets')
            await page.click('#a3d-leftpanel [data-a3dasact="template"]')
            await page.wait_for_timeout(300)
            await page.fill('.a3d-dlg [data-a3dp="name"]', 'Two walls')
            await page.keyboard.press('Enter')
            await page.wait_for_timeout(300)
            tp = [e for e in await lib() if e['kind'] == 'template']
            ck(len(tp) == 1 and tp[0]['count'] == 2, "Save as Template keeps the project (%s)" % tp)
            tid = tp[0]['id'] if tp else ''
            ck(await safe("(id)=>!!localStorage.getItem('acad3dTemplateV1:'+id)", tid),
               "under its own key, beside the library")
            await safe("()=>window.__a3dWall([[0,4],[5,4]],0.2,3,'center',false)")
            await page.wait_for_timeout(400)
            home = await safe("()=>window.__a3dDocs.active()")
            c = await centre_of('#a3d-leftpanel [data-a3dassets="template:%s"]' % tid)
            if c:
                await page.mouse.click(c[0], c[1])
            await page.wait_for_timeout(700)
            docs = await safe("()=>({active:window.__a3dDocs.active(),list:window.__a3dDocs.list()})")
            act = [x for x in (docs or {}).get('list', []) if x['id'] == (docs or {}).get('active')]
            ck(act and docs['active'] != home and act[0]['objs'] == 2 and act[0]['name'].startswith('Project'),
               "clicking it opens a new project, named as new projects are, holding the template's two walls, not the third added since (%s)" % act)
            await safe("()=>window.__a3dWall([[9,9],[12,9]],0.2,3,'center',false)")
            await page.wait_for_timeout(400)
            await safe("(id)=>window.__a3dDocs.activate(id)", home)
            await page.wait_for_timeout(600)
            ck(await n_objs() == 3 and await safe("()=>window.__a3dProjectLabel?1:1"),
               "the project it came from still has its three walls")
            stored_n = await safe("(id)=>JSON.parse(localStorage.getItem('acad3dTemplateV1:'+id)).objs.length", tid)
            ck(stored_n == 2, "and the template still holds two, whatever was drawn in the project made from it (%s)" % stored_n)
            await tab('browser')
            await tab('assets')
            dialog_answer['accept'] = True
            await page.click('#a3d-leftpanel [data-a3dasdel="%s"]' % tid)
            await page.wait_for_timeout(300)
            ck(not [e for e in await lib() if e['id'] == tid] and await safe("(id)=>localStorage.getItem('acad3dTemplateV1:'+id)===null", tid),
               "removing the template removes its stored project too")

            # ---------------------------------------------------------------------------------
            print("\n-- 10. commands, the ribbon, the audit")
            await tab('browser')
            await safe("""()=>{window.__a3dTestSetObjs([]);var w=window.__a3dWall([[0,0],[3,0]],0.2,3,'center',false);window.__a3dSelectFor([w]);}""")
            await blur()
            await page.keyboard.press('Control+k')
            await page.wait_for_timeout(150)
            await page.keyboard.type('BLOCK')
            await page.keyboard.press('Enter')
            await page.wait_for_timeout(300)
            hd = await safe("()=>{var d=document.querySelector('.a3d-dlg .a3d-dlghd');return d?d.textContent:null;}")
            ck(hd == 'Save as Block', "BLOCK on the command line opens Save as Block (%s)" % hd)
            await page.keyboard.press('Escape')
            await page.wait_for_timeout(150)
            await safe("()=>{window.__a3dAssetsUI;}")
            await safe("()=>{var u=window.__a3dAssetsUI();}")
            await safe("""()=>{var sh=document.getElementById('a3d-shell');sh.setAttribute('data-tab','browser');}""")
            await tab('browser')
            await safe("()=>{var g=document.querySelector('#a3d-leftpanel [data-a3dassetgrp]');}")
            await blur()
            await page.keyboard.press('Control+k')
            await page.wait_for_timeout(150)
            await page.keyboard.type('INSERT')
            await page.keyboard.press('Enter')
            await page.wait_for_timeout(400)
            ins = await safe("""()=>({tab:document.getElementById('a3d-shell').getAttribute('data-tab'),
                                     open:!window.__a3dAssetsUI().closed.blocks,
                                     shown:!!document.querySelector('#a3d-leftpanel [data-a3dassetgrp="blocks"]')})""")
            ck(ins and ins['tab'] == 'assets' and ins['open'] and ins['shown'],
               "INSERT opens the library at its blocks (%s)" % ins)
            await tab('browser')
            await blur()
            await page.keyboard.press('Control+k')
            await page.wait_for_timeout(150)
            await page.keyboard.type('ADCENTER')
            await page.keyboard.press('Enter')
            await page.wait_for_timeout(400)
            ck(await safe("()=>document.getElementById('a3d-shell').getAttribute('data-tab')") == 'assets',
               "ASSETS, by its alias ADCENTER, opens the library")
            await tab('browser')
            # AMENDED FOR V130: the dock holds the pinned few; every other tool is a row of Tools and shortcuts
            acts = await safe("()=>window.__a3dToolActions()") or []
            ok = await safe("""()=>{window.__a3dToolsPanel();var b=document.querySelector('#a3d-rupop [data-a3dr="bim:component"]');if(!b)return false;
              b.click();return true;}""")
            await page.wait_for_timeout(400)
            ck('bim:component' in acts and ok and await safe("()=>document.getElementById('a3d-shell').getAttribute('data-tab')") == 'assets'
               and not await safe("()=>window.__a3dAssetsUI().closed.families")
               and 'Drag a model onto the drawing' in await toast(),
               "the toolbar's Component opens the library at its models (%s, %r)" % (ok, await toast()))
            await safe("()=>window.__a3dSelectFor([])")
            await tab('browser')
            await tab('assets')
            a = await safe("()=>window.__a3dShellAudit()")
            ck(a and a['ok'] is True, "the shell audit is clean with every library control on screen (%s claimed, %s)"
               % (a and a['claimed'], a and a['unclaimed']))
        except Stalled as e:
            ck(False, "the suite ran to the end (stalled at %s)" % e)
        except Exception as e:
            traceback.print_exc()
            ck(False, "the suite ran to the end (stopped by %s: %s)" % (type(e).__name__, str(e)[:160]))

        print("")
        ck(not errs, "zero uncaught page errors (%s)" % (errs[:3] or 'none'))
        await browser.close()

    print("\n%d/%d checks passed" % (ck.n - len(ck.bad), ck.n))
    if ck.bad:
        print("RESULT: FAIL")
        for m in ck.bad:
            print("   - " + m)
        return 1
    print("RESULT: PASS")
    return 0


sys.exit(asyncio.run(run()))
