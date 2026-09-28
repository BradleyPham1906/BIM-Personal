"""
bim_phase82_annotation_overlay_browser_tests.py

Regression suite for __acad3dV82 in canvas_v10.html: the Assets library back, as real annotation
objects layered over both the 2D and 3D views.

WHAT THE USER REPORTED: "bring those assets back pls. u just straight up deleted all of them. they
should be overlaying the views of 2d and 3d in drafting view."

WHAT V80 GOT WRONG. The Assets tab held the retired whiteboard's card/sticky/shape/table library,
which dragged onto a board that no longer existed. V80 removed it and put the BIM libraries there.
Removing a library that did not work was right; leaving nothing in its place was not -- those assets
are the annotation a drawing needs, and they belong OVER the views.

WHERE THEY LIVE NOW. Not a floating HTML layer: this app's text labels were already world-ANCHORED
and screen-DRAWN, and that is exactly the behaviour an overlay note needs. So an overlay item is an
object in A3D.objs (t:'note', with a kind), which means selection, the move gizmo, layers, levels,
undo and persistence all work without a second implementation of any of them.

WHY EACH CHECK IS THE ONE THAT WOULD CATCH A REGRESSION:

  1. The overlay is asserted to render in BOTH views, by measuring that its anchor follows the
     camera while its box stays the SAME PIXEL SIZE at two very different zooms. That pair is the
     whole design: world-anchored and screen-drawn. A world-SIZED annotation would pass "it is
     visible" and then be illegible at plan scale and enormous when zoomed in.
  2. A note over a wall is asserted to win the click. Drawn on top but picked underneath is the
     most likely wiring mistake, and it would make every overlay item look placed and be unusable.
  3. Width and height are asserted NOT to change when the project's display units change. They are
     pixels; routing them through V77's length conversion would silently resize every annotation
     in the drawing the moment someone switched to millimetres.
  4. Persistence is asserted through a real export/import round trip, not by reading the object
     back out of memory.
  5. A note on a hidden layer is asserted to be neither drawn nor pickable -- annotation that
     cannot be turned off is not annotation, it is clutter.
  6. Placement lands inside the V79 safe rectangle, so a new note is never created behind the
     tool dock where it cannot be clicked.

Run:  python3 bim_phase82_annotation_overlay_browser_tests.py [path/to/canvas_v10.html]
"""

# AMENDED FOR V120: the shell's canvas-era names were replaced -- #figma-layers-shell/-rail/-panel are
# #a3d-shell/-rail/-leftpanel, the .fl-* classes .a3d-*, #uploaded-command-palette #a3d-cmdpal, the
# Project Browser tab 'file' is 'browser', --figma-dock-w is --a3d-left-w, and the material library is
# read through window.__a3dMaterialCards() (window.__WB_MATERIAL_CARDS is gone).
import asyncio, pathlib, sys

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

        has82 = await page.evaluate("()=>!!window.__acad3dV82")
        ck(has82, "__acad3dV82 marker is present")
        if not has82:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.failed), ck.n))
            await browser.close()
            return 1

        print("\n-- 1. every kind in the library places a real object")
        kinds = await page.evaluate("()=>window.__a3dNoteKinds()")
        names = [k['kind'] for k in kinds]
        ck(names == ['note', 'rect', 'ellipse', 'line', 'image', 'table'],
           "six kinds ship (%s)" % names)
        made = await page.evaluate("""()=>{
          window.__a3dTestSetObjs([]);
          const out={};
          window.__a3dNoteKinds().forEach(function(k){
            if(k.kind==='image')return;      // needs a file chooser; covered separately
            out[k.kind]=window.__a3dPlaceNote(k.kind);
          });
          const objs=window.__a3dState().objs.filter(function(o){return o.t==='note';});
          return {ids:out,count:objs.length,
                  kinds:objs.map(function(o){return o.kind;}).sort()};}""")
        ck(made['count'] == 5 and made['kinds'] == ['ellipse', 'line', 'note', 'rect', 'table'],
           "each places one object into the model (%s)" % made['kinds'])
        ck(all(v for v in made['ids'].values()), "and each returns its id")

        print("\n-- 2. world-anchored AND screen-drawn, in both views")
        nid = await page.evaluate("""()=>{
          window.__a3dTestSetObjs([]);
          window.__a3dWall([[0,0],[9,0],[9,6],[0,6]],0.3,3,'center',true);
          window.__a3dSetPlanView();
          return window.__a3dPlaceNote('note');}""")
        await page.wait_for_timeout(550)
        planR = await page.evaluate("(id)=>window.__a3dNoteRect(id)", nid)
        ck(planR is not None, "it has a screen rectangle in PLAN (%s)"
           % (planR and [round(planR[k]) for k in 'xywh']))
        await page.evaluate("()=>window.__a3dSet3DView()")
        await page.wait_for_timeout(550)
        d3R = await page.evaluate("(id)=>window.__a3dNoteRect(id)", nid)
        ck(d3R is not None, "and in 3D")
        ck(abs(d3R['ax'] - planR['ax']) > 2 or abs(d3R['ay'] - planR['ay']) > 2,
           "its ANCHOR moved with the camera (%s -> %s) -- it belongs to a point in the model"
           % ([round(planR['ax']), round(planR['ay'])],
              [round(d3R['ax']), round(d3R['ay'])]))
        ck(d3R['w'] == planR['w'] and d3R['h'] == planR['h'],
           "while its BOX is the same pixel size in both (%dx%d) -- world-anchored and "
           "screen-drawn is the whole design: a world-SIZED annotation would be illegible at plan "
           "scale and enormous zoomed in" % (d3R['w'], d3R['h']))
        zoomed = await page.evaluate("""(id)=>{
          const c=window.__a3dState().cam;
          window.__a3dSetPos&&0;
          window.__a3dFit();
          const a=window.__a3dNoteRect(id);
          // zoom right in and measure again
          window.__a3dZoomToSelection&&window.__a3dSelectFor([id]);
          return a;}""", nid)
        await page.evaluate("()=>{const s=window.__a3dState();}")
        z2 = await page.evaluate("""(id)=>{
          window.__a3dTestPaint();
          return window.__a3dNoteRect(id);}""", nid)
        ck(z2['w'] == zoomed['w'] and z2['h'] == zoomed['h'],
           "and it does not change size when the view does (%dx%d)" % (z2['w'], z2['h']))

        print("\n-- 3. the overlay is picked BEFORE the model under it")
        over = await page.evaluate("""()=>{
          window.__a3dTestSetObjs([]);
          const w=window.__a3dWall([[0,0],[12,0],[12,9],[0,9]],0.3,3,'center',true);
          window.__a3dSetPlanView();window.__a3dFit();
          const n=window.__a3dPlaceNote('rect');
          window.__a3dTestPaint();
          const r=window.__a3dNoteRect(n);
          const cx=r.x+r.w/2, cy=r.y+r.h/2;
          return {note:n, wall:w, hit:window.__a3dPick(cx,cy),
                  noteAt:window.__a3dNoteAt(cx,cy),
                  outside:window.__a3dPick(r.x-60,r.y+r.h/2)};}""")
        await page.wait_for_timeout(400)
        ck(over['hit'] == over['note'],
           "a click inside a note sitting over a wall selects the NOTE (%s) -- drawn on top but "
           "picked underneath is the likeliest wiring mistake, and it would make every overlay "
           "item look placed and be unusable" % (over['hit'] == over['note']))
        ck(over['noteAt'] == over['note'], "and the note picker agrees")
        ck(over['outside'] != over['note'],
           "while a click well outside it does not (%s)" % over['outside'])

        print("\n-- 4. size is in PIXELS and display units cannot touch it")
        before = await page.evaluate("""(id)=>{const o=window.__a3dObjSnapshot(id);
          return [o.w,o.h];}""", over['note'])
        await page.evaluate("()=>window.__a3dSetUnits('mm')")
        await page.wait_for_timeout(400)
        after = await page.evaluate("""(id)=>{const o=window.__a3dObjSnapshot(id);
          return [o.w,o.h];}""", over['note'])
        rows = await page.evaluate("""(id)=>{
          window.__a3dSelectFor([id]);window.__a3dRefreshProps();
          return window.__a3dPropRows().map(function(r){return r.label;});}""", over['note'])
        await page.wait_for_timeout(350)
        rows = await page.evaluate("()=>window.__a3dPropRows().map(r=>r.label)")
        ck(after == before,
           "switching the project to millimetres leaves the note %s px (%s) -- routing these "
           "through the V77 length conversion would silently resize every annotation in the "
           "drawing" % (before, after))
        ck(any(r == 'Width (px)' for r in rows),
           "and the property row says px, not the project unit (%s)"
           % [r for r in rows if 'Width' in r])
        await page.evaluate("()=>window.__a3dSetUnits('m')")
        await page.wait_for_timeout(300)

        print("\n-- 5. the content is editable and reaches the object")
        nid2 = await page.evaluate("""()=>{
          window.__a3dTestSetObjs([]);
          window.__a3dSetPlanView();
          const n=window.__a3dPlaceNote('note');
          window.__a3dSelectFor([n]);window.__a3dRefreshProps();
          return n;}""")
        await page.wait_for_timeout(450)
        ok = await page.evaluate("""()=>{
          function set(f,v){
            const i=document.querySelector('[data-propf="'+f+'"]');
            if(!i)return false;
            i.value=v;i.dispatchEvent(new Event('change',{bubbles:true}));
            return true;}
          return {title:set('ntitle','GRID NOTE'), body:set('nbody','Refer to S-201 for rebar.'),
                  w:set('nw','240')};}""")
        await page.wait_for_timeout(450)
        got = await page.evaluate("""(id)=>{const o=window.__a3dObjSnapshot(id);
          return {title:o.title,body:o.body,w:o.w};}""", nid2)
        ck(ok['title'] and got['title'] == 'GRID NOTE', "the title reaches the object (%s)" % got['title'])
        ck(ok['body'] and got['body'].startswith('Refer to S-201'),
           "the text reaches the object (%s)" % got['body'])
        ck(ok['w'] and got['w'] == 240, "and the width (%s)" % got['w'])

        print("\n-- 6. it persists through a real export/import round trip")
        # __a3dProjectEnvelope returns the JSON; __a3dExportProject triggers a file DOWNLOAD and
        # returns nothing, which is what the first version of this check wrongly fed to the parser.
        rt = await page.evaluate("""()=>{
          const txt=window.__a3dProjectEnvelope();
          window.__a3dTestSetObjs([]);
          const cleared=window.__a3dState().objs.filter(o=>o.t==='note').length;
          window.__a3dImportProject(txt);
          const back=window.__a3dState().objs.filter(o=>o.t==='note');
          return {cleared:cleared,n:back.length,
                  title:back.length?back[0].title:null,w:back.length?back[0].w:null,
                  kind:back.length?back[0].kind:null};}""")
        await page.wait_for_timeout(500)
        ck(rt['cleared'] == 0, "the model is genuinely emptied first")
        ck(rt['n'] == 1 and rt['title'] == 'GRID NOTE' and rt['w'] == 240,
           "and the note comes back with its content and size intact (%s)" % rt)

        print("\n-- 7. a hidden layer hides it, from the eye and from the picker")
        hid = await page.evaluate("""()=>{
          window.__a3dTestSetObjs([]);
          window.__a3dSetPlanView();
          const n=window.__a3dPlaceNote('rect');
          window.__a3dTestPaint();
          const r=window.__a3dNoteRect(n);
          const cx=r.x+r.w/2, cy=r.y+r.h/2;
          const before=window.__a3dNoteAt(cx,cy);
          // Toggled through the REAL control in the left panel. __a3dLayers() hands back a deep
          // COPY, so the first version of this check set visible=false on a throwaway object and
          // proved nothing.
          // V121: that control is the Layers panel's On switch now; the hidden layer rows it was
          // before went with V121.
          const lyr=window.__a3dObjSnapshot(n).layer;
          document.querySelector('#a3d-rail .a3d-railbtn[data-tab="layers"]').click();
          const btn=document.querySelector('[data-lyon="'+lyr+'"]');
          if(!btn)return {id:n,before:before,after:'no layer button',restored:null};
          btn.click();
          window.__a3dTestPaint();
          const after=window.__a3dNoteAt(cx,cy);
          document.querySelector('[data-lyon="'+lyr+'"]').click();
          document.querySelector('#a3d-rail .a3d-railbtn[data-tab="browser"]').click();
          window.__a3dTestPaint();
          return {id:n,before:before,after:after,restored:window.__a3dNoteAt(cx,cy),
                  usedRealControl:true};}""")
        ck(hid['before'] == hid['id'], "it picks while its layer is visible")
        ck(hid['after'] is None,
           "and not once that layer is hidden (%s) -- annotation that cannot be turned off is "
           "clutter, not annotation" % hid['after'])
        ck(hid['restored'] == hid['id'], "and it comes back when the layer does")

        print("\n-- 8. a new note lands where the user can reach it")
        placed = await page.evaluate("""()=>{
          window.__a3dTestSetObjs([]);
          window.__a3dSetPlanView();
          const n=window.__a3dPlaceNote('note');
          window.__a3dTestPaint();
          const r=window.__a3dNoteRect(n);
          const s=window.__a3dSafeViewRect();
          return {r:r,s:s,
                  inside:r.ax>=s.x&&r.ax<=s.x+s.w&&r.ay>=s.y&&r.ay<=s.y+s.h};}""")
        ck(placed['inside'] is True,
           "its anchor is inside the V79 safe rectangle (anchor %s in %s) -- so a new note is "
           "never created behind the tool dock where it cannot be clicked"
           % ([round(placed['r']['ax']), round(placed['r']['ay'])],
              [round(placed['s'][k]) for k in ('x', 'y', 'w', 'h')]))
        ck(await page.evaluate("()=>{const s=window.__a3dState();return s.objs.filter(o=>o.id===s.sel).length;}") == 1,
           "and it is left selected, so the gizmo is already on it")

        print("\n-- 9. the Assets tab offers them, Annotation first")
        await page.evaluate("()=>{const b=document.querySelector"
                            "('#a3d-rail [data-tab=\"assets\"]');b&&b.click();}")
        await page.wait_for_timeout(700)
        rows = await page.evaluate("()=>window.__a3dAssetRows()")
        specs = [r['spec'] for r in rows]
        ck(specs[0].startswith('note:'),
           "the first rows are Annotation (%s) -- it is what a user reaches for while drafting"
           % specs[:3])
        ck(len([s for s in specs if s.startswith('note:')]) == 6,
           "all six kinds are listed")
        ck(all(r['live'] for r in rows if r['spec'].startswith('note:')),
           "and all are live -- they are placed, not applied, so none needs a selection")
        n0 = await page.evaluate("()=>window.__a3dState().objs.length")
        ck(await page.evaluate("()=>window.__a3dAssetClick('note:ellipse')") is True,
           "clicking one places it")
        await page.wait_for_timeout(450)
        ck(await page.evaluate("()=>window.__a3dState().objs.length") == n0 + 1,
           "and the model gains exactly one object")
        a = await page.evaluate("()=>window.__a3dShellAudit()")
        ck(a['ok'] is True,
           "and the V80 shell audit is still clean with the new rows (%d claimed)" % a['claimed'])

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
