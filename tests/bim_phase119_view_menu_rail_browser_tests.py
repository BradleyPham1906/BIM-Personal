#!/usr/bin/env python3
"""bim_phase119_view_menu_rail_browser_tests.py -- V119: the view dropdown is gone, the HUD names the
active view -- whichever control opened it -- and the left rail is icon-only.

  1. THE DROPDOWN IS GONE. No label in the quick-access bar, no menu, none of the hooks that built,
     read or wrote them -- and the bar it sat in still works: its Undo undoes.
  2. THE VIEWS IT OFFERED ARE STILL ONE CLICK AWAY, and the HUD names the open one: the Project
     Browser's floor plan, 3D view and an elevation, and a sheet, driven with a real pointer.
  3. EVERY CONTROL THAT CHANGES THE VIEW SAYS SO. The status bar's 3D / 2D, the '>' key, the ViewCube's
     faces and Home, the tool dock's Top and 3D View, and Zoom extents in an empty plan -- which keeps
     the plan. The cube answers clicks only where it is drawn.
  4. A SECTION IS A VIEW. The Section tool's two clicks open one, Escape goes back to the view it was
     cut from -- the plan, 3D, or an elevation -- and a saved section view goes back to the view before
     it. A sheet opened over a section leaves it live and the Model tab comes back to it; with the
     section ended behind the sheet, the Model tab goes back to the view it was cut from.
  5. THE NAME FOLLOWS WHAT IT NAMES. A level added or switched from the status bar; a saved view saved,
     deleted while open, or undone away -- leaving the view its camera shows, a 3D view, an elevation,
     a plan or a section; and an undo is not a navigation. The hidden saved-views list and the
     __a3dApplyView hook open a view through the record too.
  6. FLAT IS NOT PLAN. A drawing command started in an elevation opens the plan and its clicks land;
     the north arrow, the terrain, the shadows and the sun path are drawn in the plan and not in an
     elevation, and the sun study says so when it is turned on there.
  7. A QUESTION CHANGES NOTHING: __a3dShellGeom and __a3dFlat() leave the view as it is.
  8. THE RAIL. Its buttons are icons with an accessible name and no caption; each opens its own panel,
     the open one is the only one marked, the top button shows and hides the panel, and the V80 shell
     audit finds nothing unclaimed.
  9. No page errors.

After every switch the suite checks the record against the screen: the HUD, Properties' View row and
the record name the same view; the camera shows that kind of view; the plan is the active level's; the
saved-view mark is the record's; and the Project Browser marks that view's row and no other.
"""
# AMENDED FOR V120: the shell's canvas-era names were replaced -- #figma-layers-shell/-rail/-panel are
# #a3d-shell/-rail/-leftpanel, the .fl-* classes .a3d-*, #uploaded-command-palette #a3d-cmdpal, the
# Project Browser tab 'file' is 'browser', --figma-dock-w is --a3d-left-w, and the material library is
# read through window.__a3dMaterialCards() (window.__WB_MATERIAL_CARDS is gone).
import asyncio, pathlib, sys
from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'

GONE_HOOKS = ['__acadBuildWsMenu', '__a3dWorkspaces', '__a3dSyncViewLabel']

# The record against the screen. Returns a list of disagreements; empty is agreement.
CONSIST = r"""()=>{
  var a=window.__a3dActiveView(),s=window.__a3dState(),bad=[],c=s.cam;
  var hud=(document.getElementById('a3d-view')||{}).textContent;
  if(hud!==a.name)bad.push('HUD "'+hud+'" / record "'+a.name+'"');
  var pv=null;
  [].forEach.call(document.querySelectorAll('#a3d-propsbody .a3d-prow'),function(r){
    var l=r.querySelector('.a3d-plabel');
    if(l&&l.textContent.trim()==='View'){var v=r.querySelector('.a3d-pstatic');pv=v?v.textContent:null;}});
  if(pv!==null&&pv!==a.name)bad.push('Properties "'+pv+'"');
  var sv=document.getElementById('a3d-sheetview'),sheetOn=!!(sv&&sv.classList.contains('open'));
  var plan=s.flat&&!s.section&&c.pitch>1.4;
  var shows={plan:plan,'3d':!s.flat,elev:s.flat&&!s.section&&!plan,section:s.section,sheet:sheetOn,saved:true}[a.kind];
  if(!shows)bad.push('the camera is not a '+a.kind+' (flat '+s.flat+', pitch '+c.pitch.toFixed(2)+', section '+s.section+')');
  if(a.kind!=='sheet'&&sheetOn)bad.push('a sheet is on screen');
  if(a.kind==='plan'&&a.id!==s.activeLevel)bad.push('the plan of '+a.id+' with '+s.activeLevel+' active');
  var want=(a.kind==='saved')?a.id:null;
  if(s.activeViewId!==want)bad.push('saved-view mark '+s.activeViewId);
  var key={plan:'data-a3dbplan="'+a.id+'"','3d':'data-a3dbview3d',elev:'data-a3dbviewpreset="'+a.id+'"',
           saved:'data-a3dbviewgo="'+a.id+'"',sheet:'data-a3dbsheetgo="'+a.id+'"'}[a.kind]||null;
  var exp=key?document.querySelector('#a3d-leftpanel .a3d-bleaf['+key+']'):null;
  var marked=[].slice.call(document.querySelectorAll('#a3d-leftpanel .a3d-bleaf.sel'));
  marked.forEach(function(e){if(e!==exp)bad.push('the browser marks "'+e.textContent.trim()+'"');});
  if(exp&&marked.indexOf(exp)<0)bad.push('the browser does not mark "'+exp.textContent.trim()+'"');
  return bad;
}"""


class Checks:
    def __init__(self):
        self.n, self.bad = 0, []

    def __call__(self, cond, msg):
        self.n += 1
        if not cond:
            self.bad.append(msg)
        print(('ok    ' if cond else 'FAIL  ') + msg)


async def main():
    ck = Checks()
    ck('__acad3dV119' in HTML.read_text(encoding='utf-8'), 'the V119 marker is present')
    if not ck.bad:
        try:
            await drive(ck)
        except Exception as e:
            ck(False, 'the suite ran to the end (stopped by %s: %s)' % (type(e).__name__, str(e).splitlines()[0][:160]))
    print('\n%d/%d checks passed' % (ck.n - len(ck.bad), ck.n))
    print('RESULT: ' + ('PASS' if not ck.bad else 'FAIL'))
    sys.exit(1 if ck.bad else 0)


async def drive(ck):
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1600, 'height': 950})
        page = await ctx.new_page()
        page.set_default_timeout(6000)
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)[:160]))
        page.on('dialog', lambda d: asyncio.ensure_future(d.dismiss()))
        ev = page.evaluate

        async def safe(js, arg=None):
            try:
                return await (ev(js, arg) if arg is not None else ev(js))
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:160])
                return None

        async def view():
            return await safe("""()=>{var a=window.__a3dActiveView(),s=window.__a3dState(),h=document.getElementById('a3d-view');
                return {kind:a.kind,id:a.id,name:a.name,hud:h?h.textContent:null,pitch:Math.round(s.cam.pitch*100)/100,
                        yaw:Math.round(s.cam.yaw*100)/100,dist:Math.round(s.cam.dist*100)/100,flat:s.flat,section:s.section,
                        lvl:s.activeLevel,mark:s.activeViewId};}""")

        async def consistent(what):
            bad = await safe(CONSIST)
            ck(bad == [], 'the record, the HUD, Properties, the camera and the browser agree %s (%s)' % (what, bad))

        async def click_xy(x, y, wait=350):
            await page.mouse.click(x, y)
            await page.wait_for_timeout(wait)

        async def click_sel(sel, wait=350):
            """A real pointer click on the first VISIBLE element the selector finds."""
            box = await safe("""(q)=>{var es=document.querySelectorAll(q),i,r;
                for(i=0;i<es.length;i++){r=es[i].getBoundingClientRect();
                  if(r.width>0&&r.height>0&&getComputedStyle(es[i]).visibility!=='hidden'){
                    es[i].scrollIntoView({block:'center'});r=es[i].getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2];}}
                return null;}""", sel)
            if box:
                await click_xy(box[0], box[1], wait)
            else:
                print('      (nothing visible to click for %s)' % sel)
            return box is not None

        # AMENDED FOR V130: the dock holds the pinned few (Top, 3D View and Section are not among
        # them); every tool is a row of the Tools and shortcuts panel, which a click on a row closes
        async def tool_sel(sel):
            await safe("()=>window.__a3dToolsPanel()")
            await page.wait_for_timeout(150)
            await click_sel(sel)

        async def blur():
            await safe("()=>{if(document.activeElement&&document.activeElement.blur)document.activeElement.blur();}")

        async def key(k, wait=350):
            await blur()
            await page.keyboard.press(k)
            await page.wait_for_timeout(wait)

        async def palette_run(name):
            await blur()
            await page.keyboard.press('Control+k')
            await page.wait_for_timeout(320)
            await page.keyboard.type(name)
            await page.wait_for_timeout(260)
            await page.keyboard.press('Enter')
            await page.wait_for_timeout(420)

        async def canvas_box():
            return await safe("()=>{var r=document.getElementById('a3d-canvas').getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height};}")

        async def paint():
            await safe("()=>window.__a3dTestPaint()")

        async def model_props():
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dRefreshProps();}")
            await page.wait_for_timeout(80)

        await page.goto('file://' + str(HTML))
        try:
            await page.wait_for_function("()=>!!window.__a3dActiveView&&!!document.querySelector('#a3d-leftpanel [data-a3dbplan]')", timeout=20000)
        except Exception as e:
            print('      (the workspace did not come up: %s)' % str(e)[:100])
        await page.wait_for_timeout(500)
        v0 = await view()
        lvl0 = v0 and v0['lvl']

        # -------------------------------------------------------------------------------------------
        print('\n-- 1. the view dropdown is gone')
        await click_xy(260, 14, 200)   # where the label sat, right of the Plot button
        gone = await safe("(hooks)=>[!!document.querySelector('.acad-ws'),!!document.getElementById('acad-wsmenu'),"
                          "hooks.filter(function(n){return typeof window[n]!=='undefined';})]", GONE_HOOKS)
        ck(gone == [False, False, []], 'no label, no menu -- not even after a click where it sat -- and none of its hooks (%s)' % gone)
        qat = await safe("()=>Array.prototype.map.call(document.querySelectorAll('#acad-qat .acad-qbtn'),function(b){return b.getAttribute('data-acad-act');})")
        n0 = len((await safe("()=>window.__a3dState().objs")) or [])
        await safe("()=>window.__a3dWall([[0,0],[5,0]],0.3,3,'center',false)")
        await page.wait_for_timeout(200)
        n1 = len((await safe("()=>window.__a3dState().objs")) or [])
        await click_sel('#acad-qat .acad-qbtn[data-acad-act="undo"]')
        n2 = len((await safe("()=>window.__a3dState().objs")) or [])
        ck(qat == ['saveJson', 'openJson', 'undo', 'redo', 'print'] and n1 == n0 + 1 and n2 == n0,
           'the quick-access bar keeps its five buttons, and its Undo undoes (%s; %d -> %d -> %d)' % (qat, n0, n1, n2))

        # -------------------------------------------------------------------------------------------
        print('\n-- 2. the views are one click away, and the HUD names the open one')
        ck(v0 and v0['kind'] == 'plan' and v0['hud'] == v0['name'] and 'Floor Plan' in (v0['name'] or ''),
           'at boot the plan is open and the HUD names it (%s)' % v0)
        await consistent('at boot')
        await click_sel('#a3d-leftpanel [data-a3dbview3d]')
        v1 = await view()
        ck(v1 and v1['kind'] == '3d' and not v1['flat'] and v1['hud'] == v1['name'] == '3D View',
           'the Project Browser\'s {3D} opens the 3D view, and the HUD says so (%s)' % v1)
        await consistent('in the 3D view')
        await click_sel('#a3d-leftpanel [data-a3dbviewpreset="front"]')
        v2 = await view()
        ck(v2 and v2['kind'] == 'elev' and v2['pitch'] < 0.2 and v2['hud'] == v2['name'] and 'Front' in (v2['name'] or ''),
           'its Front Elevation opens the elevation, looking sideways, and the HUD names it (%s)' % v2)
        await consistent('in the Front Elevation')
        await click_sel('#a3d-leftpanel [data-a3dbplan]')
        v3 = await view()
        ck(v3 and v3['kind'] == 'plan' and v3['flat'] and v3['pitch'] > 1.4 and v3['hud'] == v3['name'] == v0['name'],
           'its floor plan brings the plan back, looking down, under the same name (%s)' % v3)
        sid = await safe("()=>window.__a3dAddSheet('A119','Rail review','ANSI-B-L')")
        await safe("(id)=>window.__a3dOpenSheetView(id)", sid)
        await page.wait_for_timeout(300)
        v6 = await view()
        await consistent('on a sheet')
        await safe("()=>window.__a3dCloseSheetView()")
        await page.wait_for_timeout(300)
        v7 = await view()
        ck(v6 and v6['kind'] == 'sheet' and v6['hud'] == 'A119 - Rail review' and v7 and v7['hud'] == v0['name'],
           'a sheet is named by its number and name, and leaving it names the plan again (%s, %s)'
           % (v6 and v6['hud'], v7 and v7['hud']))
        await consistent('back from the sheet')

        # -------------------------------------------------------------------------------------------
        print('\n-- 3. every control that changes the view says so')
        await click_sel('#a3d-flip')
        s1 = await view()
        await consistent('after the status bar\'s switch to 3D')
        await click_sel('#a3d-flip')
        s2 = await view()
        ck(s1 and s2 and s1['kind'] == '3d' and not s1['flat'] and s1['hud'] == '3D View'
           and s2['kind'] == 'plan' and s2['flat'] and s2['hud'] == v0['name'],
           'the status bar\'s 3D / 2D goes to 3D and back to the plan, and the HUD follows both ways (%s -> %s)'
           % (s1 and s1['hud'], s2 and s2['hud']))
        await consistent('after the switch back')
        await key('Shift+Period')
        k1 = await view()
        await consistent('after the > key')
        await key('Shift+Period')
        k2 = await view()
        ck(k1 and k2 and k1['kind'] == '3d' and k1['hud'] == '3D View' and k2['kind'] == 'plan' and k2['hud'] == v0['name'],
           'the > key does the same (%s -> %s)' % (k1 and k1['hud'], k2 and k2['hud']))

        # the ViewCube is drawn in 3D; in the plan it has no faces, and where it stood is only canvas
        faces_plan = await safe("()=>window.__a3dCubeFaces()")
        cb = await canvas_box()
        moved = []
        for dx in range(-40, 41, 20):
            for dy in range(-40, 41, 20):
                await click_xy(cb['x'] + cb['w'] - 72 + dx, cb['y'] + 68 + dy, 90)
                w = await view()
                if not (w and w['kind'] == 'plan' and w['pitch'] > 1.4):
                    moved.append((dx, dy, w and w['name']))
                    await click_sel('#a3d-leftpanel [data-a3dbplan]')
        ck(faces_plan == [] and moved == [],
           'in the plan the ViewCube has no faces, and 25 clicks where it stands in 3D change nothing (%s, %s)' % (faces_plan, moved[:3]))
        await click_sel('#a3d-leftpanel [data-a3dbview3d]')
        await paint()
        faces = {f['n']: f for f in ((await safe("()=>window.__a3dCubeFaces()")) or [])}
        if 'front' in faces:
            await click_xy(faces['front']['x'], faces['front']['y'], 450)
        c1 = await view()
        ck('front' in faces and c1 and c1['kind'] == 'elev' and c1['id'] == 'front' and c1['hud'] == 'Front Elevation' and c1['pitch'] < 0.2,
           'in 3D, the ViewCube\'s Front face opens the Front Elevation, and the HUD names it (%s; faces %s)' % (c1, sorted(faces)))
        await consistent('after the cube\'s Front face')
        await click_sel('#a3d-leftpanel [data-a3dbview3d]')
        cb = await canvas_box()
        mx, my = cb['x'] + cb['w'] / 2, cb['y'] + cb['h'] / 2 + 60
        await page.mouse.move(mx, my)
        await page.mouse.wheel(0, 600)                  # zoom out, and orbit: Home has to undo both
        await page.wait_for_timeout(200)
        await page.mouse.down()
        await page.mouse.move(mx + 90, my, steps=6)
        await page.mouse.up()
        await page.wait_for_timeout(250)
        moved3d = await view()
        await paint()
        faces = {f['n']: f for f in ((await safe("()=>window.__a3dCubeFaces()")) or [])}
        if 'home' in faces:
            await click_xy(faces['home']['x'], faces['home']['y'], 450)
        c2 = await view()
        ck('home' in faces and moved3d and (moved3d['yaw'], moved3d['dist']) != (-0.7, 30.0)
           and c2 and c2['kind'] == '3d' and c2['hud'] == '3D View' and c2['yaw'] == -0.7 and c2['dist'] == 30,
           'orbited and zoomed out, its Home opens the 3D view framed as it starts: yaw -0.7, distance 30 (%s -> %s)'
           % (moved3d and (moved3d['yaw'], moved3d['dist']), c2))
        await consistent('after the cube\'s Home')
        await tool_sel('#a3d-rupop [data-a3dr="v:top"]')
        d1 = await view()
        await consistent('after the dock\'s Top')
        await tool_sel('#a3d-rupop [data-a3dr="v:iso"]')
        d2 = await view()
        await consistent('after the dock\'s 3D View')
        ck(d1 and d2 and d1['kind'] == 'plan' and d1['hud'] == v0['name'] and d2['kind'] == '3d' and d2['hud'] == '3D View',
           'the tool dock\'s Top opens the plan and its 3D View the 3D view, each named (%s, %s)' % (d1 and d1['hud'], d2 and d2['hud']))
        await click_sel('#a3d-leftpanel [data-a3dbplan]')
        nobj = len((await safe("()=>window.__a3dState().objs")) or [])
        cb = await canvas_box()
        await page.mouse.move(cb['x'] + cb['w'] / 2, cb['y'] + cb['h'] / 2)
        await page.mouse.wheel(0, 600)
        await page.wait_for_timeout(200)
        z0 = await view()
        await click_sel('#a3d-railutil .a3d-ru[data-a3drumenu="zoom"]')
        await click_sel('#a3d-rupop [data-a3druitem="zoom:extents"]')
        z1 = await view()
        ck(nobj == 0 and z0 and z0['dist'] != 30 and z1 and z1['kind'] == 'plan' and z1['flat'] and z1['pitch'] > 1.4 and z1['dist'] == 30,
           'Zoom extents in an empty plan keeps the plan and frames it afresh -- it used to open 3D (%d objects; distance %s -> %s)'
           % (nobj, z0 and z0['dist'], z1))
        await consistent('after Zoom extents')

        # -------------------------------------------------------------------------------------------
        print('\n-- 4. a section is a view')
        await safe("()=>window.__a3dWall([[-4,0],[4,0]],0.3,3,'center',false)")
        await click_sel('#a3d-leftpanel [data-a3dbplan]')

        async def draw_section():
            await tool_sel('#a3d-rupop [data-a3dr="bim:section"]')
            a = await safe("()=>window.__a3dToScreen([0,-3])")
            b = await safe("()=>window.__a3dToScreen([0,3])")
            cbx = await canvas_box()
            if a and b:
                await click_xy(cbx['x'] + a[0], cbx['y'] + a[1], 200)
                await click_xy(cbx['x'] + b[0], cbx['y'] + b[1], 450)

        await draw_section()
        x1 = await view()
        ck(x1 and x1['kind'] == 'section' and x1['section'] and x1['hud'] == 'Section' and x1['pitch'] < 0.2,
           'the dock\'s Section tool, two clicks: the cut is live, the camera looks along it, the HUD says Section (%s)' % x1)
        await consistent('in the section')
        await key('Escape', 450)
        x2 = await view()
        ck(x2 and x2['kind'] == 'plan' and not x2['section'] and x2['pitch'] > 1.4 and x2['hud'] == v0['name'],
           'Escape goes back to the plan it was cut from, the record with the camera (%s)' % x2)
        await consistent('after Escape')
        await click_sel('#a3d-leftpanel [data-a3dbview3d]')
        await draw_section()
        x3 = await view()
        await key('Escape', 450)
        x4 = await view()
        ck(x3 and x3['kind'] == 'section' and x4 and x4['kind'] == '3d' and not x4['flat'] and x4['hud'] == '3D View',
           'started in 3D, the tool cuts from the plan and Escape goes back to 3D (%s -> %s)' % (x3 and x3['hud'], x4 and x4['hud']))
        await consistent('back in 3D')
        await click_sel('#a3d-leftpanel [data-a3dbplan]')
        await draw_section()
        await safe("()=>{window.prompt=function(){return 'Cut A';};}")
        await click_sel('#a3d-viewsave')
        x5 = await view()
        ck(x5 and x5['kind'] == 'saved' and x5['hud'] == 'Cut A' and x5['section'],
           'a section saved as a view is that view, and named so (%s)' % x5)
        await consistent('in the saved section view')
        cut = x5 and x5['id']
        await click_sel('#a3d-leftpanel [data-a3dbview3d]')
        await click_sel('#a3d-leftpanel [data-a3dbviewgo="%s"]' % cut)
        x6 = await view()
        await consistent('in the saved section view, opened from 3D')
        await key('Escape', 450)
        x7 = await view()
        ck(x6 and x6['kind'] == 'saved' and x6['section'] and x6['hud'] == 'Cut A'
           and x7 and x7['kind'] == '3d' and not x7['flat'] and not x7['section'] and x7['hud'] == '3D View',
           'opened from 3D, the saved section view is named, and Escape goes back to 3D (%s -> %s)' % (x6 and x6['hud'], x7 and x7['hud']))
        await consistent('after leaving the saved section view')

        # started in an elevation, the tool cuts from the plan and Escape goes back to the elevation
        await click_sel('#a3d-leftpanel [data-a3dbviewpreset="front"]')
        await tool_sel('#a3d-rupop [data-a3dr="bim:section"]')
        e0 = await view()
        a = await safe("()=>window.__a3dToScreen([0,-3])")
        b = await safe("()=>window.__a3dToScreen([0,3])")
        cbx = await canvas_box()
        if a and b:
            await click_xy(cbx['x'] + a[0], cbx['y'] + a[1], 200)
            await click_xy(cbx['x'] + b[0], cbx['y'] + b[1], 450)
        e1 = await view()
        await key('Escape', 450)
        e2 = await view()
        ck(e0 and e0['kind'] == 'plan' and e0['pitch'] > 1.4 and e1 and e1['kind'] == 'section'
           and e2 and e2['kind'] == 'elev' and e2['id'] == 'front' and e2['pitch'] < 0.2 and e2['hud'] == 'Front Elevation',
           'started in the Front Elevation, the Section tool opens the plan for its cut line, and Escape goes back to the elevation (%s, %s, %s)'
           % (e0 and e0['hud'], e1 and e1['hud'], e2 and e2['hud']))
        await consistent('back in the Front Elevation')

        # a sheet opened over a section leaves it live, and the Model tab comes back to it
        await click_sel('#a3d-leftpanel [data-a3dbplan]')
        await draw_section()
        await click_sel('#a3d-laytabs [data-lt="sheet"][data-ltsheet="%s"]' % sid)
        m1 = await view()
        await click_sel('#a3d-laytabs [data-lt="model"]')
        m2 = await view()
        ck(m1 and m1['kind'] == 'sheet' and m1['section'] and m2 and m2['kind'] == 'section' and m2['section'] and m2['hud'] == 'Section',
           'a sheet opened over a section leaves the cut live, and the Model tab goes back to the section (%s -> %s)'
           % (m1 and m1['hud'], m2 and m2['hud']))
        await consistent('back in the section from the sheet')

        # ... and when the section is ended behind the sheet -- a switch to another project and back --
        # the Model tab goes back to the view the section was cut from, not to a section that is gone
        await click_sel('#a3d-laytabs [data-lt="sheet"][data-ltsheet="%s"]' % sid)
        home = await safe("()=>window.__a3dDocs.active()")
        other = await safe("()=>window.__a3dDocs.create()")
        await page.wait_for_timeout(300)
        await safe("(id)=>window.__a3dDocs.activate(id)", home)
        await page.wait_for_timeout(400)
        m3 = await view()
        await safe("()=>{var t=document.getElementById('a3d-toast');if(t)t.textContent='';}")
        await click_sel('#a3d-laytabs [data-lt="model"]')
        m4 = await view()
        t4 = await safe("()=>{var t=document.getElementById('a3d-toast');return t?t.textContent:'';}")
        ck(bool(other) and m3 and m3['kind'] == 'sheet' and not m3['section'] and m4 and m4['kind'] == 'plan'
           and m4['pitch'] > 1.4 and 'no longer open' not in (t4 or ''),
           'with the section ended behind the sheet, the Model tab goes back to the plan it was cut from (%s -> %s; %r)'
           % (m3 and m3['hud'], m4 and m4['hud'], t4))
        await consistent('back from the sheet after the section ended')
        await safe("(id)=>window.__a3dDocs.close&&window.__a3dDocs.close(id)", other)

        # a section whose way back is not a model view gives way to the view its camera shows
        await safe("""()=>{var s=window.__a3dState().cam;window.__a3dEnterSection([0,0,0],[1,0,0],
            {yaw:0,pitch:0.02,dist:s.dist,tx:s.tx,ty:s.ty,tz:s.tz,flat:true,view:'Right Elevation',record:{kind:'sheet',id:'no-such'}});}""")
        await page.wait_for_timeout(250)
        await key('Escape', 450)
        h1 = await view()
        ck(h1 and h1['kind'] == 'elev' and h1['id'] == 'front' and h1['hud'] == 'Front Elevation',
           'a section whose way back names a sheet comes back to the view its camera shows -- here the Front Elevation (%s)' % h1)
        await consistent('after a section with nowhere to go back to')

        # -------------------------------------------------------------------------------------------
        print('\n-- 5. the name follows what it names')
        await click_sel('#a3d-leftpanel [data-a3dbplan]')
        await click_sel('#a3d-lvladd')
        l1 = await view()
        ck(l1 and l1['kind'] == 'plan' and l1['lvl'] != lvl0 and l1['hud'] == 'Level 1 - Floor Plan',
           '+Lvl makes the new level active, and the open plan is its plan, named so (%s)' % l1)
        await consistent('after +Lvl')
        try:
            await page.select_option('#a3d-stlevel', lvl0)
        except Exception as e:
            print('      (the status bar level could not be set: %s)' % str(e)[:100])
        await page.wait_for_timeout(300)
        l2 = await view()
        ck(l2 and l2['kind'] == 'plan' and l2['lvl'] == lvl0 and l2['hud'] == v0['name'],
           'the status bar\'s level switches the plan with it, and the HUD names it (%s)' % l2)
        await consistent('after the status bar level')
        await click_sel('#a3d-leftpanel [data-a3dbview3d]')
        await safe("()=>{window.prompt=function(){return 'Walk';};}")
        await click_sel('#a3d-viewsave')
        w1 = await view()
        ck(w1 and w1['kind'] == 'saved' and w1['hud'] == 'Walk', '+View in 3D saves the view, and it is the open one (%s)' % w1)
        await consistent('in the saved view')
        cam_before = w1 and (w1['yaw'], w1['pitch'], w1['dist'])
        await safe("()=>{window.confirm=function(){return true;};}")
        await click_sel('#a3d-leftpanel [data-a3dbviewdel="%s"]' % (w1 and w1['id']))
        w2 = await view()
        ck(w2 and w2['kind'] == '3d' and w2['hud'] == '3D View' and (w2['yaw'], w2['pitch'], w2['dist']) == cam_before,
           'deleting it while it is open leaves the 3D view it shows, named so, and moves nothing (%s)' % w2)
        await consistent('after deleting the open saved view')
        await safe("()=>{window.prompt=function(){return 'Temp';};}")
        await click_sel('#a3d-viewsave')
        nw0 = len((await safe("()=>window.__a3dState().objs")) or [])
        await safe("()=>window.__a3dWall([[10,0],[14,0]],0.3,3,'center',false)")   # a model change made in 'Temp'
        await click_sel('#a3d-leftpanel [data-a3dbplan]')
        await key('Control+z')
        u1 = await view()
        nw1 = len((await safe("()=>window.__a3dState().objs")) or [])
        await consistent('after an undo in the plan')
        await key('Control+y')
        u2 = await view()
        ck(u1 and u2 and nw1 == nw0 and u1['kind'] == u2['kind'] == 'plan' and u1['mark'] is None and u2['mark'] is None,
           'a wall added in a saved view, undone and redone from the plan: the wall goes and comes back, and the plan '
           'stays open with no saved view marked (%s, %s)' % (u1, u2))
        await consistent('after a redo in the plan')
        await click_sel('#a3d-leftpanel [data-a3dbview3d]')
        await safe("()=>{window.prompt=function(){return 'Gone';};}")
        await click_sel('#a3d-viewsave')
        g1 = await view()
        await key('Control+z')
        g2 = await view()
        ck(g1 and g1['hud'] == 'Gone' and g2 and g2['kind'] == '3d' and g2['hud'] == '3D View'
           and (g2['yaw'], g2['pitch'], g2['dist']) == (g1['yaw'], g1['pitch'], g1['dist']),
           'undoing the save of the open view leaves the view it showed, named so, and moves nothing (%s -> %s)'
           % (g1 and g1['hud'], g2))
        await consistent('after undoing the open view away')

        # the view the camera shows, whichever kind: an elevation, a plan, a section
        await click_sel('#a3d-leftpanel [data-a3dbviewpreset="right"]')
        await safe("()=>{window.prompt=function(){return 'Side';};}")
        await click_sel('#a3d-viewsave')
        r1 = await view()
        await click_sel('#a3d-leftpanel [data-a3dbviewdel="%s"]' % (r1 and r1['id']))
        r2 = await view()
        ck(r1 and r1['hud'] == 'Side' and r2 and r2['kind'] == 'elev' and r2['id'] == 'right' and r2['hud'] == 'Right Elevation',
           'a saved elevation deleted while open leaves the Right Elevation it shows (%s -> %s)' % (r1 and r1['hud'], r2 and r2['hud']))
        await consistent('after deleting an open saved elevation')
        await click_sel('#a3d-leftpanel [data-a3dbplan]')
        await safe("()=>{window.prompt=function(){return 'Plan B';};}")
        await click_sel('#a3d-viewsave')
        r3 = await view()
        await key('Control+z')
        r4 = await view()
        ck(r3 and r3['hud'] == 'Plan B' and r4 and r4['kind'] == 'plan' and r4['hud'] == v0['name'],
           'a saved plan undone away while open leaves the plan (%s -> %s)' % (r3 and r3['hud'], r4 and r4['hud']))
        await consistent('after undoing an open saved plan away')
        await click_sel('#a3d-leftpanel [data-a3dbview3d]')
        await click_sel('#a3d-leftpanel [data-a3dbviewgo="%s"]' % cut)
        await click_sel('#a3d-leftpanel [data-a3dbviewdel="%s"]' % cut)
        r5 = await view()
        await consistent('after deleting the open saved section view')
        await key('Escape', 450)
        r6 = await view()
        ck(r5 and r5['kind'] == 'section' and r5['section'] and r5['hud'] == 'Section' and r6 and r6['kind'] == '3d' and r6['hud'] == '3D View',
           'the saved section view deleted while open leaves its cut, a Section, whose Escape goes back to 3D (%s -> %s)'
           % (r5 and r5['hud'], r6 and r6['hud']))
        await consistent('after leaving that section')

        # the saved-views list's Go (hidden since V84, still in the page) and the hook both open through the record
        await safe("()=>{window.prompt=function(){return 'Kept';};}")
        await click_sel('#a3d-viewsave')
        kept = (await view() or {}).get('id')
        await click_sel('#a3d-leftpanel [data-a3dbplan]')
        await safe("(id)=>{var b=document.querySelector('#a3d-viewrows [data-viewgo=\"'+id+'\"]');if(b)b.click();}", kept)
        await page.wait_for_timeout(300)
        k1 = await view()
        await click_sel('#a3d-leftpanel [data-a3dbplan]')
        await safe("(id)=>window.__a3dApplyView(id)", kept)
        await page.wait_for_timeout(300)
        k2 = await view()
        ck(k1 and k2 and k1['kind'] == k2['kind'] == 'saved' and k1['hud'] == k2['hud'] == 'Kept',
           'the hidden list\'s Go and __a3dApplyView open the saved view as a view, named (%s, %s)' % (k1 and k1['hud'], k2 and k2['hud']))
        await consistent('after the hook')

        # -------------------------------------------------------------------------------------------
        print('\n-- 6. flat is not plan')
        await click_sel('#a3d-leftpanel [data-a3dbviewpreset="front"]')
        await palette_run('LINE')
        f1 = await view()
        cbx = await canvas_box()
        pts0 = await safe("()=>{var s=window.__a3dState().sk;return s?s.pts:null;}")
        await click_xy(cbx['x'] + cbx['w'] / 2 - 120, cbx['y'] + cbx['h'] / 2 + 40, 200)
        await click_xy(cbx['x'] + cbx['w'] / 2 + 120, cbx['y'] + cbx['h'] / 2 + 40, 200)
        pts = await safe("()=>{var s=window.__a3dState().sk;return s?[s.tool,s.pts]:null;}")
        ck(f1 and f1['kind'] == 'plan' and f1['pitch'] > 1.4 and f1['hud'] == v0['name'] and pts0 == 0 and pts == ['line', 2],
           'LINE started in the Front Elevation opens the plan, and both clicks land (%s; %s)' % (f1 and f1['hud'], pts))
        await consistent('drawing from the elevation')
        await key('Escape')
        await key('Escape')
        tid = await safe("()=>window.__a3dMakeTerrain([[-5,-5,100,'',''],[5,-5,100,'',''],[5,5,100,'',''],[-5,5,100,'',''],[0,0,104,'','']])")
        await safe("()=>window.__a3dColumnAt([3,3],0,0.4,0.4,3)")
        await model_props()
        await safe("()=>window.__a3dSetPropTab&&window.__a3dSetPropTab('site')")   # AMENDED FOR V141: the field is on Properties' Site tab
        for fld, val in (('sunlat', '40.2732'), ('sunlon', '-76.8867'), ('suntz', '-4'), ('sundate', '2024-06-20'), ('suntime', '13:00')):
            try:
                loc = page.locator('input[data-propmodel="%s"]' % fld)
                await loc.fill(val, timeout=3000)
                await loc.press('Enter', timeout=3000)
                await page.wait_for_timeout(120)
            except Exception as e:
                print('      (the site field %s could not be set: %s)' % (fld, str(e)[:100]))
        await palette_run('SUNSTUDY')
        await click_sel('#a3d-leftpanel [data-a3dbplan]')
        await paint()
        inplan = await safe("()=>({north:window.__a3dNorthArrow(),terrain:!!window.__a3dTerrainShown(),"
                            "shadow:(window.__a3dShadowInfo()||{}).casters||0,path:!!window.__a3dSunPath()})")
        await click_sel('#a3d-leftpanel [data-a3dbviewpreset="right"]')
        await paint()
        inelev = await safe("()=>({north:window.__a3dNorthArrow(),terrain:!!window.__a3dTerrainShown(),"
                            "shadow:window.__a3dShadowInfo(),path:!!window.__a3dSunPath()})")
        ck(bool(tid) and inplan and inplan['north'] is not None and inplan['terrain'] and inplan['shadow'] >= 1 and inplan['path'],
           'in the plan the north arrow, the terrain, the shadows and the sun path are drawn (%s)' % inplan)
        ck(inelev and inelev['north'] is None and not inelev['terrain'] and inelev['shadow'] is None and not inelev['path'],
           'in the Right Elevation none of them is -- they are plan drawings, and an elevation is flat too (%s)' % inelev)
        await palette_run('SUNSTUDY')
        await palette_run('SUNSTUDY')
        toast = await safe("()=>{var t=document.getElementById('a3d-toast');return t?t.textContent:null;}")
        ck(toast == 'Sun study on: shadows and the sun path are drawn in plan',
           'turned on in the elevation, the sun study says it is drawn in plan (%r)' % toast)
        await consistent('in the Right Elevation')

        # -------------------------------------------------------------------------------------------
        print('\n-- 7. a question changes nothing')
        await click_sel('#a3d-leftpanel [data-a3dbplan]')
        q0 = await view()
        geom = await safe("()=>window.__a3dShellGeom().mode")
        flat = await safe("()=>window.__a3dFlat()")
        q1 = await view()
        ck(q0 and q1 and q0 == q1 and geom == 'da' and flat is True,
           'asking __a3dShellGeom for the mode and __a3dFlat() whether the view is flat leaves the plan open (%s, %s; %s)'
           % (geom, flat, q1 and q1['hud']))
        await consistent('after the questions')

        # -------------------------------------------------------------------------------------------
        print('\n-- 8. the rail')
        rail = await safe("""()=>Array.prototype.map.call(document.querySelectorAll('#a3d-rail .a3d-railbtn'),function(b){
            var s=b.querySelector('svg'),r=s?s.getBoundingClientRect():null;
            return {tab:b.getAttribute('data-tab'),text:b.textContent.trim(),aria:b.getAttribute('aria-label'),title:b.getAttribute('title'),
                    icon:!!(s&&s.children.length&&r&&r.width>=14&&r.height>=14)};})""") or []
        ck([(r['tab'], r['aria'], r['title']) for r in rail] == [('layers', 'Layers', 'Layers'), ('presentation', 'Presentation', 'Presentation'),
                                                                 ('browser', 'Project Browser', 'Project Browser'), ('assets', 'Assets', 'Assets'),
                                                                 ('analyze', 'Analyze', 'Analyze')]   # AMENDED FOR V141: Analyze below Assets; FOR V159: Site analysis inside it
           and all(r['text'] == '' and r['icon'] for r in rail),
           'the rail buttons -- AMENDED FOR V121: Layers first; FOR V122: Presentation second -- icons only, each named for what it opens (%s)' % rail)

        async def panel():
            return await safe("""()=>{var sh=document.getElementById('a3d-shell');
                function vis(q){var e=document.querySelector(q);if(!e)return false;var r=e.getBoundingClientRect();return r.width>0&&r.height>0&&getComputedStyle(e).visibility!=='hidden';}
                return {tab:sh.getAttribute('data-tab'),tree:vis('#a3d-leftpanel > .a3d-tree'),assets:vis('#a3d-leftpanel .a3d-assets'),
                        active:Array.prototype.map.call(document.querySelectorAll('#a3d-rail .a3d-railbtn.active'),function(b){return b.getAttribute('data-tab');}),
                        collapsed:sh.classList.contains('collapsed'),panelW:Math.round(document.getElementById('a3d-leftpanel').getBoundingClientRect().width)};}""")

        await click_sel('#a3d-rail .a3d-railbtn[data-tab="assets"]')
        p1 = await panel()
        await click_sel('#a3d-rail .a3d-railbtn[data-tab="browser"]')
        p2 = await panel()
        ck(p1 and p1['tab'] == 'assets' and p1['assets'] and not p1['tree'] and p1['active'] == ['assets'],
           'Assets opens the Assets panel, and is the one button marked (%s)' % p1)
        ck(p2 and p2['tab'] == 'browser' and p2['tree'] and not p2['assets'] and p2['active'] == ['browser'],
           'the Project Browser button opens the Project Browser, and is the one marked (%s)' % p2)
        async def settled():
            # the panel's width is animated: read it once it has stopped moving (a loaded machine
            # measured 1 px mid-transition)
            last = None
            for _ in range(30):
                cur = await panel()
                if cur and last and cur['panelW'] == last['panelW']:
                    return cur
                last = cur
                await page.wait_for_timeout(100)
            return last

        await click_sel('#a3d-rail .a3d-paneltoggle')
        p3 = await settled()
        await click_sel('#a3d-rail .a3d-paneltoggle')
        p4 = await settled()
        ck(p3 and p4 and p3['collapsed'] and p3['panelW'] == 0 and not p4['collapsed'] and p4['panelW'] > 200,
           'the top button hides the panel and shows it again (%s -> %s px)' % (p3 and p3['panelW'], p4 and p4['panelW']))
        audit = await safe("()=>window.__a3dShellAudit()")
        ck(audit and audit.get('ok') is True, 'the V80 shell audit finds nothing unclaimed (%s)' % (audit and audit.get('unclaimed')))

        # -------------------------------------------------------------------------------------------
        print('\n-- 9. errors')
        ck(errs == [], 'no page errors (%s)' % errs[:3])
        await browser.close()


asyncio.run(main())
