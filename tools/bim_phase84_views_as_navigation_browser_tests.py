"""
bim_phase84_views_as_navigation_browser_tests.py

Regression suite for __acad3dV84 in canvas_v10.html: Drafting & Annotation stops being a MODE and
becomes what it always should have been -- a view you open, like a layout view.

WHAT THE USER ASKED FOR: "drafting and annotation is basically 2d view which is not true. it
should be a view, like layout view."

WHAT WAS MEASURED BEFORE THE PATCH (probe84.py, against f8b607a9):

    start       view=Plan             flat=True   label='Drafting & Annotation'
    3D view     view=Isometric        flat=False  label='Drafting & Annotation'   <- the label lies
    Front elev  view=Front Elevation  yaw=0.000   pitch=0.020
    Floor plan  view=Front Elevation  yaw=0.000   pitch=0.020                     <- INERT
    Right elev  view=Right Elevation  yaw=1.571   pitch=0.020
    Floor plan  view=Right Elevation  yaw=1.571   pitch=0.020                     <- INERT again

Two faults, both of which this suite is built to catch again:

  1. The floor-plan row read "if(!A3D.flat)toggleFlat()". An ELEVATION IS ALSO FLAT, so from any
     elevation the row changed the active level and left the camera looking sideways at the plan
     it had just opened. This is the same flat-is-not-plan confusion V18 fixed for the drafting
     tools and never fixed here.
  2. The ribbon label reported the workspace, so it read "Drafting & Annotation" over an isometric
     3D view.

WHY EACH CHECK IS THE ONE THAT WOULD CATCH A REGRESSION:

  1. The floor-plan row is exercised from ALL FOUR elevations, from the 3D view, and from a
     section -- not from one of them. This is the V81 lesson paid forward: V78's rotate suite
     tested only walls, so a column branch with no orientation at all shipped and the user found
     it. A suite that exercises one branch of a dispatcher has tested one branch. The failing
     case here is specifically flat-to-flat, which a single check starting from 3D would miss
     entirely -- and starting from 3D is the obvious thing to write.
  2. Every view switch is asserted on the CAMERA (yaw/pitch/flat), never on the label or the row
     highlight. A label that updates over an unchanged camera is exactly the decorative control
     Product Principle 1 forbids, and it is the more likely regression of the two.
  3. The label is asserted to MATCH the measured view rather than to contain a fixed string. The
     phase73 check it replaces asserted the literal "Drafting" and would have passed forever on
     the bug the user reported, because the bug was that the label never changed.
  4. Failure paths are asserted to return false AND leave the previous view's camera untouched.
     A view switch that half-happens is worse than one that declines.
  5. The V80 shell audit is asserted clean, which is the standing rule.
  6. Zero uncaught page errors across every probe.

Run:  python3 bim_phase84_views_as_navigation_browser_tests.py [path/to/canvas_v10.html]
"""

# AMENDED FOR V120: the shell's canvas-era names were replaced -- #figma-layers-shell/-rail/-panel are
# #a3d-shell/-rail/-leftpanel, the .fl-* classes .a3d-*, #uploaded-command-palette #a3d-cmdpal, the
# Project Browser tab 'file' is 'browser', --figma-dock-w is --a3d-left-w, and the material library is
# read through window.__a3dMaterialCards() (window.__WB_MATERIAL_CARDS is gone).
import asyncio, pathlib, sys

from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'

# Everything a view switch must be judged on, read straight from the engine and the DOM.
# AMENDED FOR V119: 'label' is the HUD's View readout. The view dropdown whose label this phase made
# name the active view is gone, and the name it carried moved to the HUD; every check below that was
# made against the label holds the HUD to the same standard.
STATE = """()=>{
  const s=window.__a3dState?window.__a3dState():{};
  const lab=document.getElementById('a3d-view');
  const sv=document.getElementById('a3d-sheetview');
  const av=window.__a3dActiveView?window.__a3dActiveView():null;
  return {view:s.view, flat:s.flat, lvl:s.activeLevel, ws:window.ACAD_WS_CUR,
          label:lab?lab.textContent.trim():null,
          sheetOpen:!!(sv&&sv.classList.contains('open')),
          kind:av?av.kind:null, name:av?av.name:null, id:av?av.id:null,
          section:!!s.section,
          yaw:s.cam?Math.round(s.cam.yaw*1000)/1000:null,
          pitch:s.cam?Math.round(s.cam.pitch*1000)/1000:null};
}"""

# A plan camera looks straight down: pitch ~1.52, yaw 0. An elevation looks sideways: pitch ~0.02.
PLAN_PITCH = 1.52
ELEV_PITCH = 0.02


async def click_leaf(page, attr, val):
    """Click a Project Browser row with a REAL pointer at its own rectangle.

    A synthetic element.click() can reach a row the user cannot reach and can skip the delegate
    path a pointer takes -- the V80 audit shipped two false 'leftovers' for exactly that reason.
    """
    sel = '[data-%s="%s"]' % (attr, val)
    box = await page.evaluate("""(sel)=>{
      const e=document.querySelector(sel);
      if(!e)return null;
      e.scrollIntoView({block:'center'});
      const r=e.getBoundingClientRect();
      if(r.width<2||r.height<2)return null;
      return {x:r.left+18,y:r.top+r.height/2};
    }""", sel)
    if not box:
        return None
    await page.mouse.click(box['x'], box['y'])
    await page.wait_for_timeout(480)          # the camera tween is 260ms
    # V100: a fixed wait flaked twice under the parallel runner (the tween had not finished on
    # a loaded machine). Wait for the camera to SETTLE -- two identical reads -- up to 3 s.
    prev = await page.evaluate(STATE)
    for _ in range(20):
        await page.wait_for_timeout(150)
        cur = await page.evaluate(STATE)
        if cur == prev:
            return cur
        prev = cur
    return prev


async def open_group(page, key):
    box = await page.evaluate("""(k)=>{
      const e=document.querySelector('[data-a3dbgrp="'+k+'"]');
      if(!e)return null;
      e.scrollIntoView({block:'center'});
      const r=e.getBoundingClientRect();
      return {x:r.left+20,y:r.top+r.height/2};
    }""", key)
    if not box:
        return False
    await page.mouse.click(box['x'], box['y'])
    await page.wait_for_timeout(260)
    return True


def is_plan(st):
    return bool(st) and st['flat'] is True and abs(st['pitch'] - PLAN_PITCH) < 0.05 \
        and abs(st['yaw']) < 0.05


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
        await page.wait_for_timeout(2200)

        has84 = await page.evaluate("()=>!!window.__acad3dV84")
        ck(has84, "__acad3dV84 marker is present")
        if not has84:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.failed), ck.n))
            await browser.close()
            return 1

        # ------------------------------------------------------------------ 1
        print("\n-- 1. the app boots INTO a view, and says which one")
        boot = await page.evaluate(STATE)
        print("     " + str(boot))
        ck(boot['kind'] == 'plan', "the active view is a floor plan (%s)" % boot['kind'])
        ck(is_plan(boot), "with a real plan camera: flat=%s yaw=%s pitch=%s"
           % (boot['flat'], boot['yaw'], boot['pitch']))
        ck(boot['view'] == 'Plan',
           "the HUD still reads 'Plan' (%s) -- other code reads that exact string, so routing "
           "the boot through setView('top') must not rename it to 'Top (Plan)'" % boot['view'])
        ck(boot['lvl'] is not None, "on a real level (%s)" % boot['lvl'])
        ck(boot['label'] == boot['name'],
           "the ribbon label IS the active view's name: label=%r name=%r"
           % (boot['label'], boot['name']))
        ck('Floor Plan' in (boot['label'] or ''),
           "and names it as a view, not as a mode (%r)" % boot['label'])
        ck(boot['ws'] == 'da',
           "the drafting tool set is up, because that is what a plan view uses (%s)" % boot['ws'])

        # ------------------------------------------------------------------ 2
        print("\n-- 2. each Project Browser row opens ITS view, measured on the camera")
        st3d = await click_leaf(page, 'a3dbview3d', 'iso')
        print("     {3D}        " + str(st3d))
        ck(st3d and st3d['flat'] is False and abs(st3d['pitch'] - 0.42) < 0.05,
           "{3D} opens the isometric camera (flat=%s pitch=%s)"
           % (st3d and st3d['flat'], st3d and st3d['pitch']))
        ck(st3d and st3d['kind'] == '3d', "and the active view kind is 3d (%s)"
           % (st3d and st3d['kind']))
        ck(st3d and st3d['label'] == st3d['name'] == '3D View',
           "the label reads '3D View' (%r) -- before this phase it read 'Drafting & Annotation' "
           "over this very camera, which is what the user reported" % (st3d and st3d['label']))
        ck(st3d and st3d['ws'] == '3d',
           "the RIBBON FOLLOWS THE VIEW into the modelling tool set (%s)"
           % (st3d and st3d['ws']))

        elevs = {'front': 0.0, 'back': 3.142, 'left': -1.571, 'right': 1.571}
        for key, yaw in elevs.items():
            st = await click_leaf(page, 'a3dbviewpreset', key)
            ok = st and st['flat'] is True and abs(st['pitch'] - ELEV_PITCH) < 0.05 \
                and abs(st['yaw'] - yaw) < 0.05
            ck(ok, "the %s elevation row opens a sideways camera (yaw=%s pitch=%s)"
               % (key, st and st['yaw'], st and st['pitch']))
            ck(st and st['kind'] == 'elev' and st['id'] == key,
               "  and is the active view (%s/%s)" % (st and st['kind'], st and st['id']))
            ck(st and st['label'] == st['name'] and 'Elevation' in (st['label'] or ''),
               "  and the label names it (%r)" % (st and st['label']))
            ck(st and st['ws'] == 'da',
               "  and an elevation keeps the drafting tool set (%s)" % (st and st['ws']))

        # ------------------------------------------------------------------ 3
        print("\n-- 3. THE REGRESSION: a floor plan opens from every view, not just from 3D")
        print("     flat-to-flat is the case that was broken. A single check starting from the")
        print("     3D view -- the obvious one to write -- would have passed on the shipped bug.")
        lvl = boot['lvl']
        for start_kind, opener in (
                ('the 3D view', lambda: click_leaf(page, 'a3dbview3d', 'iso')),
                ('the front elevation', lambda: click_leaf(page, 'a3dbviewpreset', 'front')),
                ('the back elevation', lambda: click_leaf(page, 'a3dbviewpreset', 'back')),
                ('the left elevation', lambda: click_leaf(page, 'a3dbviewpreset', 'left')),
                ('the right elevation', lambda: click_leaf(page, 'a3dbviewpreset', 'right'))):
            before = await opener()
            after = await click_leaf(page, 'a3dbplan', lvl)
            ck(is_plan(after),
               "from %s, the floor plan row restores the PLAN camera "
               "(was yaw=%s pitch=%s, now yaw=%s pitch=%s)"
               % (start_kind, before and before['yaw'], before and before['pitch'],
                  after and after['yaw'], after and after['pitch']))
            ck(after and after['kind'] == 'plan' and after['lvl'] == lvl,
               "  on the level that was clicked (%s / %s)"
               % (after and after['kind'], after and after['lvl']))

        # from a SECTION, which is flat too and additionally has a cut plane to leave
        # bimEnterSection needs the camera to come back to; passing it is the caller's job, and
        # the first version of this check omitted it and measured a TypeError rather than a view.
        sec = await page.evaluate("""()=>{
          try{
            const s=window.__a3dState();
            window.__a3dEnterSection([0,0,0],[1,0,0],
              {yaw:s.cam.yaw,pitch:s.cam.pitch,dist:s.cam.dist,
               tx:s.cam.tx,ty:s.cam.ty,tz:s.cam.tz,flat:s.flat,view:s.view});
            return true;
          }catch(e){ return String(e); }
        }""")
        await page.wait_for_timeout(400)
        in_sec = await page.evaluate(STATE)
        ck(sec is True, "a section view can be entered for the next check (%s)" % sec)
        after_sec = await click_leaf(page, 'a3dbplan', lvl)
        ck(is_plan(after_sec),
           "from a section (flat, with a cut plane), the floor plan row restores the plan camera "
           "(was pitch=%s, now pitch=%s)"
           % (in_sec['pitch'], after_sec and after_sec['pitch']))
        ck(in_sec['section'] is True,
           "the section cut really was active before the switch (%s)" % in_sec['section'])
        ck(after_sec is not None and after_sec['section'] is False,
           "and the section's cut plane is left behind rather than following into the plan (%s)"
           % (after_sec and after_sec['section']))

        # ------------------------------------------------------------------ 4
        print("\n-- 4. the active row is the row for the view you are actually in")
        await click_leaf(page, 'a3dbviewpreset', 'front')
        marks = await page.evaluate("""(lvl)=>{
          const sel=s=>{const e=document.querySelector(s);
                        return e?e.classList.contains('sel'):null;};
          return {plan:sel('[data-a3dbplan="'+lvl+'"]'),
                  front:sel('[data-a3dbviewpreset="front"]'),
                  right:sel('[data-a3dbviewpreset="right"]'),
                  v3d:sel('[data-a3dbview3d="iso"]')};
        }""", lvl)
        print("     in the front elevation: " + str(marks))
        ck(marks['front'] is True, "the front elevation row is marked active")
        ck(marks['plan'] is False,
           "the floor plan row is NOT marked -- its old test was '&& A3D.flat', and an elevation "
           "is flat, so it sat highlighted while the user looked at an elevation (%s)"
           % marks['plan'])
        ck(marks['right'] is False and marks['v3d'] is False,
           "and no other view row is marked (right=%s 3d=%s)" % (marks['right'], marks['v3d']))

        await click_leaf(page, 'a3dbplan', lvl)
        marks2 = await page.evaluate("""(lvl)=>{
          const sel=s=>{const e=document.querySelector(s);
                        return e?e.classList.contains('sel'):null;};
          return {plan:sel('[data-a3dbplan="'+lvl+'"]'),
                  front:sel('[data-a3dbviewpreset="front"]')};
        }""", lvl)
        ck(marks2['plan'] is True and marks2['front'] is False,
           "back in the plan, the marking moves with it (%s)" % marks2)

        # ------------------------------------------------------------------ 5
        print("\n-- 5. a sheet is a view like any other")
        sheet_id = await page.evaluate("()=>window.__a3dAddSheet()")
        await page.wait_for_timeout(300)
        ck(bool(sheet_id), "a sheet exists to open (%s)" % sheet_id)
        await open_group(page, 'sheets')
        st_sheet = await click_leaf(page, 'a3dbsheetgo', sheet_id)
        print("     " + str(st_sheet))
        ck(st_sheet and st_sheet['sheetOpen'] is True, "the sheet row opens the paper canvas")
        ck(st_sheet and st_sheet['kind'] == 'sheet',
           "and it is the active view (%s)" % (st_sheet and st_sheet['kind']))
        ck(st_sheet and st_sheet['label'] == st_sheet['name']
           and 'A101' in (st_sheet['label'] or ''),
           "the label names the sheet (%r)" % (st_sheet and st_sheet['label']))
        ck(st_sheet and st_sheet['ws'] == 'da',
           "a sheet is documentation, so it keeps the drafting tool set (%s)"
           % (st_sheet and st_sheet['ws']))

        st_leave = await click_leaf(page, 'a3dbview3d', 'iso')
        ck(st_leave and st_leave['sheetOpen'] is False,
           "leaving for another view CLOSES the paper canvas -- it covers the model canvas, so a "
           "sheet left open means opening a view you cannot see (%s)"
           % (st_leave and st_leave['sheetOpen']))

        # ------------------------------------------------------------------ 6
        print("\n-- 6. a saved view carries its own tool set")
        made = await page.evaluate("""()=>{
          window.prompt=function(){return 'Saved Iso';};
          const b=document.getElementById('a3d-viewsave');
          if(!b)return 'no save button';
          b.click();
          return true;
        }""")
        await page.wait_for_timeout(400)
        ck(made is True, "a 3D view was saved through the real button (%s)" % made)
        saved = await page.evaluate("""()=>{
          const r=[...document.querySelectorAll('[data-a3dbviewgo]')]
            .map(e=>e.getAttribute('data-a3dbviewgo'));
          return r.length?r[0]:null;
        }""")
        ck(bool(saved), "and appears in the Project Browser (%s)" % saved)
        if saved:
            await click_leaf(page, 'a3dbplan', lvl)
            st_saved = await click_leaf(page, 'a3dbviewgo', saved)
            print("     " + str(st_saved))
            ck(st_saved and st_saved['kind'] == 'saved',
               "the saved view row opens it (%s)" % (st_saved and st_saved['kind']))
            ck(st_saved and st_saved['flat'] is False and st_saved['ws'] == '3d',
               "a saved 3D view brings the modelling tool set with it (flat=%s ws=%s)"
               % (st_saved and st_saved['flat'], st_saved and st_saved['ws']))
            ck(st_saved and st_saved['label'] == 'Saved Iso',
               "and the label uses the name the user gave it (%r)"
               % (st_saved and st_saved['label']))

        # ------------------------------------------------------------------ 6b
        print("\n-- 6b. a view saved from a 2D camera has somewhere to live")
        print("     Before V84 it had none: the 3D Views group filters out flat views and the")
        print("     Sections group filters out non-sections, so a view saved from a plan or an")
        print("     elevation appeared in the palette list and NOWHERE in the browser tree.")
        await click_leaf(page, 'a3dbplan', lvl)
        made2d = await page.evaluate("""()=>{
          window.prompt=function(){return 'Saved Plan';};
          const b=document.getElementById('a3d-viewsave');
          if(!b)return 'no save button';
          b.click();
          return true;
        }""")
        await page.wait_for_timeout(400)
        ck(made2d is True, "a view is saved from the plan camera (%s)" % made2d)
        rows2d = await page.evaluate("""()=>[...document.querySelectorAll('[data-a3dbviewgo]')]
          .map(e=>e.closest('.a3d-bleaf').textContent.trim())""")
        print("     browser view rows: " + str(rows2d))
        ck(any('Saved Plan' in r for r in rows2d),
           "and it appears in the Project Browser (%s)" % rows2d)
        grp = await page.evaluate("""()=>{
          const g=document.querySelector('[data-a3dbgrp="views2d"]');
          return g?g.textContent.trim():null;}""")
        ck(grp is not None and '2D Views' in grp, "under a 2D Views group (%r)" % grp)

        saved2d = await page.evaluate("""()=>{
          const r=[...document.querySelectorAll('[data-a3dbviewgo]')]
            .filter(e=>e.closest('.a3d-bleaf').textContent.indexOf('Saved Plan')>=0);
          return r.length?r[0].getAttribute('data-a3dbviewgo'):null;}""")
        await click_leaf(page, 'a3dbview3d', 'iso')
        st2d = await click_leaf(page, 'a3dbviewgo', saved2d)
        ck(st2d and st2d['flat'] is True and st2d['ws'] == 'da',
           "opening it returns the 2D camera AND the drafting tool set (flat=%s ws=%s)"
           % (st2d and st2d['flat'], st2d and st2d['ws']))

        print("     the delete buttons are claimed, so they must also WORK")
        before_del = await page.evaluate(
            "()=>[...document.querySelectorAll('[data-a3dbviewgo]')].length")
        await page.evaluate("()=>{window.confirm=function(){return true;};}")
        delbox = await page.evaluate("""(id)=>{
          const e=document.querySelector('[data-a3dbviewdel="'+id+'"]');
          if(!e)return null;
          e.scrollIntoView({block:'center'});
          const r=e.getBoundingClientRect();
          if(r.width<2||r.height<2)return null;
          return {x:r.left+r.width/2,y:r.top+r.height/2};
        }""", saved2d)
        ck(delbox is not None, "the saved view's delete button is reachable by a pointer")
        if delbox:
            await page.mouse.click(delbox['x'], delbox['y'])
            await page.wait_for_timeout(400)
            after_del = await page.evaluate(
                "()=>[...document.querySelectorAll('[data-a3dbviewgo]')].length")
            ck(after_del == before_del - 1,
               "and deletes exactly that view (%d -> %d) -- a claimed control that does nothing "
               "is the one thing the whitelist exists to prevent" % (before_del, after_del))

        # ------------------------------------------------------------------ 7
        print("\n-- 7. a view that cannot be opened declines, and changes nothing")
        await click_leaf(page, 'a3dbviewpreset', 'front')
        before_bad = await page.evaluate(STATE)
        bad = await page.evaluate("""()=>({
          preset: window.__a3dOpenView('elev','northwest'),
          kind:   window.__a3dOpenView('teleport'),
          sheet:  window.__a3dOpenView('sheet','sheet-does-not-exist'),
          saved:  window.__a3dOpenView('saved','view-does-not-exist')
        })""")
        await page.wait_for_timeout(300)
        after_bad = await page.evaluate(STATE)
        print("     returns " + str(bad))
        ck(bad['preset'] is False, "an unknown elevation preset returns false")
        ck(bad['kind'] is False, "an unknown view kind returns false")
        ck(bad['sheet'] is False, "an unknown sheet returns false")
        ck(bad['saved'] is False, "an unknown saved view returns false")
        ck(after_bad['yaw'] == before_bad['yaw'] and after_bad['pitch'] == before_bad['pitch']
           and after_bad['kind'] == before_bad['kind'],
           "and all four leave the previous view untouched (%s/%s -> %s/%s) -- a view switch "
           "that half-happens is worse than one that declines"
           % (before_bad['kind'], before_bad['pitch'], after_bad['kind'], after_bad['pitch']))
        ck(after_bad['label'] == before_bad['label'],
           "including the label (%r)" % after_bad['label'])

        # ------------------------------------------------------------------ 8
        print("\n-- 8. the view menu is gone; the views it offered are in the Project Browser")
        # AMENDED FOR V119: the dropdown offered two entries, named as views by this phase -- Floor Plan
        # and 3D View. The owner removed it as redundant: both are Project Browser views, opened
        # through the same activation path this section goes on to check.
        rows = await page.evaluate("""()=>({menu:!!(document.querySelector('#acad-shell .acad-ws')||document.getElementById('acad-wsmenu')),
          plan:!!document.querySelector('#a3d-leftpanel [data-a3dbplan]'),
          view3d:!!document.querySelector('#a3d-leftpanel [data-a3dbview3d]')})""")
        print("     " + str(rows))
        ck(rows['menu'] is False, "the view dropdown and its menu are gone (%s)" % rows['menu'])
        ck(rows['plan'] and rows['view3d'],
           "and the two views it offered, the floor plan and the 3D view, are Project Browser views (%s)" % rows)

        await page.evaluate("()=>window.__a3dSet3DView()")
        await page.wait_for_timeout(300)
        via_hook = await page.evaluate(STATE)
        ck(via_hook['kind'] == '3d' and via_hook['label'] == '3D View',
           "__a3dSet3DView goes through the same activation path, label included (%r)"
           % via_hook['label'])
        await page.evaluate("()=>window.__a3dSetPlanView()")
        await page.wait_for_timeout(300)
        via_hook2 = await page.evaluate(STATE)
        ck(via_hook2['kind'] == 'plan' and is_plan(via_hook2) and via_hook2['view'] == 'Plan',
           "and so does __a3dSetPlanView (%s, pitch=%s, view=%r)"
           % (via_hook2['kind'], via_hook2['pitch'], via_hook2['view']))

        # ------------------------------------------------------------------ 8b
        print("\n-- 8b. every readout of 'which view' agrees with every other")
        print("     The Phase 84 visual review caught a Properties panel reading 'View  3D'")
        print("     beside a status bar reading 'View: Plan'. Two causes: the row was computed")
        print("     as (A3D.flat ? 'Plan' : '3D'), which calls an elevation a plan; and nothing")
        print("     re-rendered the panel on a view change, so it showed its boot-time render.")

        async def readouts():
            return await page.evaluate("""()=>{
              const rows=[...document.querySelectorAll('#a3d-right .a3d-prow')];
              let propView=null;
              for(const r of rows){
                const k=r.querySelector('.a3d-plabel')||r.firstElementChild;
                if(k&&k.textContent.trim()==='View'){
                  propView=r.textContent.trim().replace(/^View/,'').trim();
                }
              }
              const hud=document.getElementById('a3d-view');
              const lab=document.getElementById('a3d-view');   /* AMENDED FOR V119: the HUD */
              const av=window.__a3dActiveView();
              return {prop:propView, hud:hud?hud.textContent.trim():null,
                      label:lab?lab.textContent.trim():null, name:av.name, kind:av.kind};
            }""")

        for kind, attr, val in (('plan', 'a3dbplan', lvl),
                                ('3d', 'a3dbview3d', 'iso'),
                                ('elev', 'a3dbviewpreset', 'front'),
                                ('elev', 'a3dbviewpreset', 'right')):
            await click_leaf(page, attr, val)
            r = await readouts()
            print("     %-6s %s" % (val, r))
            ck(r['prop'] == r['name'],
               "in %s, the Properties panel names the active view (panel=%r view=%r)"
               % (val, r['prop'], r['name']))
            ck(r['label'] == r['name'],
               "  and the HUD agrees (%r)" % r['label'])
            if kind == 'elev':
                ck(r['prop'] != 'Plan',
                   "  and an elevation is NOT called a plan (%r) -- it is flat, which is what "
                   "the old readout tested" % r['prop'])

        # ------------------------------------------------------------------ 9
        print("\n-- 9. nothing was left behind in the shell")
        audit = await page.evaluate("()=>window.__a3dShellAudit()")
        ck(audit and audit.get('ok') is True,
           "the V80 shell audit is clean: %d claimed, unclaimed=%s"
           % (audit.get('claimed', -1), audit.get('unclaimed')))
        body = await page.evaluate("()=>document.body.className")
        ck('a3d-mode' in body,
           "and the app is still inside the BIM shell (%r) -- V83's Escape handler silently "
           "exited it, and this is the check that caught it" % body)

        print("")
        ck(not errs, "zero uncaught page errors across every probe (%s)" % (errs or 'none'))

        await browser.close()

    print("\n%d/%d checks passed" % (ck.n - len(ck.failed), ck.n))
    if ck.failed:
        print("RESULT: FAIL")
        for f in ck.failed:
            print("  - " + f)
        return 1
    print("RESULT: PASS")
    return 0


sys.exit(asyncio.run(run()))
