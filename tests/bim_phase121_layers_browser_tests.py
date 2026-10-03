"""bim_phase121_layers_browser_tests.py -- V121: Layers, merged with the model, and AutoCAD's table.

The owner: "layers (this should combine with model) and i should be able to manipulate a table like
how autocad do like linetype, color, hide/show, layer, sub layer, transparency, ... do some research
on this". What this suite holds the phase to, each asserted on the model and each control driven:

  1. THE RULES. AutoCAD's meanings (Layer Properties Manager and SELECT, AutoCAD 2024 help): a layer
     that is off is not drawn or plotted and is still taken by SELECT ALL; a frozen layer is taken
     by nothing; a locked layer is drawn faded, snapped to and plotted, and not selected; a no-plot
     layer is drawn and not plotted. A sub-layer is what its parents leave it. The refusals are
     AutoCAD's: the current layer is not frozen or deleted, a frozen layer is not made current, a
     name is new and legal, layer 0's counterpart and a layer holding objects are not deleted.
  2. THE LOOK. The linework LINE, PLINE, ARC, CIRCLE and POINT make is drawn By Layer -- color,
     acadiso linetype, lineweight -- and everything on a layer takes its transparency.
  3. THE LAYERS PANEL, the model inside it: switches, current mark, rename, color, search, drag an
     object onto a layer, drag a layer under another, object rows that select.
  4. THE LAYER PROPERTIES MANAGER, from LAYER in the command line, with AutoCAD's columns, every
     cell editable, a refused change shown as refused.
  5. EVERY WAY OF SELECTING asks the layers: SELECT ALL and the classification rows take AutoCAD's
     ALL, a window picks what is shown and unlocked, a row naming one object refuses one it cannot
     select, and nothing drawn on a locked layer is left selected.
  6. A PLOT IS A PLOT: the plan SVG, the sheet SVG and the sheet's paper leave out what is off,
     frozen or not plotted, draw no lock fade, and draw the linework's linetype and lineweight in
     paper millimetres. The DXF carries every layer's state and linetype, and reads them back.
  7. OLDER DATA LOADS UNCHANGED, and the new fields survive a reload.
"""
import asyncio, json, pathlib, re, sys
from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'

HEADERS = ['Status', 'Name', 'On', 'Freeze', 'Lock', 'Plot', 'Color', 'Linetype', 'Lineweight',
           'Transparency', 'Objects', 'Description']
ACADISO = {'DASHED': [12.7, -6.35], 'HIDDEN': [6.35, -3.175], 'CENTER': [31.75, -6.35, 6.35, -6.35],
           'PHANTOM': [31.75, -6.35, 6.35, -6.35, 6.35, -6.35], 'DOT': [0, -6.35],
           'DASHDOT': [12.7, -6.35, 0, -6.35], 'BORDER': [12.7, -6.35, 12.7, -6.35, 0, -6.35],
           'DIVIDE': [12.7, -6.35, 0, -6.35, 0, -6.35]}
LWS = [0, 0.05, 0.09, 0.13, 0.15, 0.18, 0.2, 0.25, 0.3, 0.35, 0.4, 0.5, 0.53, 0.6, 0.7, 0.8, 0.9, 1,
       1.06, 1.2, 1.4, 1.58, 2, 2.11]


class Checks:
    def __init__(self):
        self.n, self.bad = 0, []

    def __call__(self, cond, msg):
        self.n += 1
        if not cond:
            self.bad.append(msg)
        print(('  ok    ' if cond else '  FAIL  ') + msg)


def near(a, b, tol=1e-6):
    try:
        return abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return False


def nears(a, b, tol=1e-6):
    return isinstance(a, list) and len(a) == len(b) and all(near(x, y, tol) for x, y in zip(a, b))


# ======================================================================= the file, statically
def static_checks(ck, t):
    code = re.sub(r'/\*.*?\*/', '', t, flags=re.S)
    print('\n-- 0. the file')
    ck(not re.search(r'lyr\s*&&\s*\(?\s*lyr\.(visible|locked)', code),
       'no site reads a layer\'s visible or locked flag for itself: all of them ask the layer questions')
    ck('\\ud83d\\udd12' not in t and '\\ud83d\\udd13' not in t,
       'no lock is drawn as an emoji (the Project Browser\'s layer and model rows drew them)')
    gone = [g for g in ('a3d-layerrows', 'a3d-layeradd', 'data-a3dblayer', 'data-a3dblock', 'toggleLayerVisible',
                        'toggleLayerLock', 'removeLayer(', 'renameLayer(') if g in code]
    ck(gone == [], 'the hidden layer rows, +Lyr and the browser\'s layer and model toggles are gone (%s)' % gone)
    ck(re.search(r"\['LAYER',\['LA','LAYERS'\],'layers','Layer Properties Manager'\]", t) is not None
       and re.search(r"\n    layers:function\(\)\{bimLayerManagerOpen\(\);\}", code) is not None,
       'LAYER, LA and LAYERS name the Layer Properties Manager, and the engine runs it')
    plots = [fn for fn in ('bimBuildSVG', 'bimBuildSheetSVG')
             if not re.search(r'\n  function ' + fn + r'\((?:mode|sheet,mode)\)\{[^\n]*\n\s*return bimWithPlotPass\(', code)]
    ck(plots == [], 'the plan SVG and the sheet SVG are drawn in a plot pass (%s are not)' % plots)
    ck(code.count("P(62,7)+P(6,'CONTINUOUS')") == 1,
       'the DXF writes layer 0 white and Continuous, and no other layer so (%d)' % code.count("P(62,7)+P(6,'CONTINUOUS')"))


# ======================================================================= the running app
async def main():
    ck = Checks()
    t = HTML.read_text(encoding='utf-8')
    ck('__acad3dV121' in t, 'the V121 marker is present')
    if not ck.bad:
        try:
            static_checks(ck, t)
        except Exception as e:
            ck(False, 'the static checks ran to the end (stopped by %s: %s)' % (type(e).__name__, str(e)[:160]))
        try:
            await drive(ck)
        except Exception as e:
            ck(False, 'the suite ran to the end (stopped by %s: %s)' % (type(e).__name__, str(e).splitlines()[0][:200]))
    print('\n%d/%d checks passed' % (ck.n - len(ck.bad), ck.n))
    print('RESULT: ' + ('PASS' if not ck.bad else 'FAIL'))
    sys.exit(1 if ck.bad else 0)


LAST_TOAST = "()=>{var t=document.getElementById('a3d-toast');if(!t)return '';var s=t.textContent.split('\\n');return s[s.length-1];}"


async def drive(ck):
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1600, 'height': 950})
        page = await ctx.new_page()
        page.set_default_timeout(6000)
        errs, warns = [], []
        page.on('pageerror', lambda e: errs.append(str(e)[:200]))
        page.on('console', lambda m: warns.append(m.text[:200]) if m.type == 'warning' and m.text.startswith('[BIM]') else None)
        page.on('dialog', lambda d: asyncio.ensure_future(d.dismiss()))
        ev = page.evaluate

        async def safe(js, arg=None):
            try:
                return await (ev(js, arg) if arg is not None else ev(js))
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:200])
                return None

        async def boot():
            for _ in range(60):
                if await safe("()=>!!(window.__a3dOn&&window.__a3dLayerNew&&window.__a3dSketch)"):
                    break
                await page.wait_for_timeout(100)
            await page.wait_for_timeout(500)

        async def toast():
            return await safe(LAST_TOAST) or ''

        async def blur():
            await safe("()=>{var a=document.activeElement;if(a&&a!==document.body&&a.blur)a.blur();}")

        async def palette(cmd):
            await blur()
            await page.mouse.click(900, 480)
            await page.keyboard.press('Escape')
            await page.keyboard.press('Control+k')
            await page.wait_for_timeout(150)
            await page.keyboard.type(cmd)
            await page.wait_for_timeout(120)
            await page.keyboard.press('Enter')
            await page.wait_for_timeout(300)

        await page.goto('file://' + str(HTML))
        await boot()

        # ------------------------------------------------------------------------------------------
        print('\n-- 1. the rules, by AutoCAD')
        ids = await safe("""()=>{
          window.__a3dTestSetObjs([]);
          window.__a3dSetPlanView();
          var L0=window.__a3dLayers()[0].id;
          window.__a3dLayerCurrent(L0);
          var wall=window.__a3dLayerNew({name:'A-WALL',color:'#c0a377'});
          var full=window.__a3dLayerNew({name:'A-WALL-FULL',parent:wall});
          var anno=window.__a3dLayerNew({name:'A-ANNO',color:'#84b98c'});
          window.__a3dLayerSet(anno,'linetype','HIDDEN');
          window.__a3dLayerSet(anno,'lineweight',0.5);
          window.__a3dLayerSet(anno,'transparency',30);
          var copy=window.__a3dLayerNew({from:anno});
          return {L0:L0,wall:wall,full:full,anno:anno,copy:copy};}""")
        ck(ids and all(ids.get(k) for k in ('L0', 'wall', 'full', 'anno', 'copy')), 'layers and a sub-layer are made (%s)' % ids)
        layers = await safe("()=>window.__a3dLayers()") or []
        by = {l['id']: l for l in layers}
        cp = by.get(ids and ids['copy'], {})
        ck(cp.get('name') == 'Layer 1' and cp.get('linetype') == 'HIDDEN' and near(cp.get('lineweight'), 0.5)
           and near(cp.get('transparency'), 30) and cp.get('color') == '#84b98c',
           'a new layer is named Layer 1 and takes the appearance of the layer it is made from, as AutoCAD\'s New Layer does (%s)'
           % {k: cp.get(k) for k in ('name', 'linetype', 'lineweight', 'transparency', 'color')})
        tree = await safe("()=>window.__a3dLayerTree()") or []
        ck([(x['name'], x['depth']) for x in tree] == [('Model', 0), ('A-WALL', 0), ('A-WALL-FULL', 1), ('A-ANNO', 0), ('Layer 1', 0)],
           'the tree lists the sub-layer under its parent (%s)' % [(x['name'], x['depth']) for x in tree])
        lts = await safe("()=>window.__a3dLinetypes()") or []
        ck(all(nears([p for p in (l.get('pat') or [])], ACADISO[l['name']]) for l in lts if l['name'] in ACADISO)
           and sorted(l['name'] for l in lts) == sorted(list(ACADISO) + ['Continuous']),
           'the linetypes are acadiso.lin\'s, in millimetres (%s)' % [l['name'] for l in lts])
        lws = await safe("()=>window.__a3dLineweights()") or []
        ck(nears(lws, LWS), 'the lineweights are AutoCAD\'s list (%d of them)' % len(lws))

        ref = await safe(r"""(ids)=>{
          function last(){var t=document.getElementById('a3d-toast');var s=t?t.textContent.split('\n'):[''];return s[s.length-1];}
          var out={};
          out.dupName=[window.__a3dLayerSet(ids.copy,'name','a-wall'),last()];
          out.badChar=[window.__a3dLayerSet(ids.copy,'name','A/B'),last()];
          out.freezeCur=[window.__a3dLayerSet(ids.L0,'frozen',true),last()];
          window.__a3dLayerCurrent(ids.full);
          out.freezeParentOfCur=[window.__a3dLayerSet(ids.wall,'frozen',true),last()];
          window.__a3dLayerCurrent(ids.L0);
          window.__a3dLayerSet(ids.copy,'frozen',true);
          out.frozenCurrent=[window.__a3dLayerCurrent(ids.copy),last()];
          window.__a3dLayerSet(ids.copy,'frozen',false);
          out.underSelf=[window.__a3dLayerSet(ids.wall,'parent',ids.full),last()];
          out.trans95=[window.__a3dLayerSet(ids.anno,'transparency',95),last()];
          out.lw=[window.__a3dLayerSet(ids.anno,'lineweight',0.33),last()];
          out.lt=[window.__a3dLayerSet(ids.anno,'linetype','ZIGZAG'),last()];
          window.__a3dLayerCurrent(ids.wall);   /* so that only the first-layer rule can refuse */
          out.delFirst=[window.__a3dLayerDelete(ids.L0),last()];
          window.__a3dLayerCurrent(ids.copy);
          out.delCur=[window.__a3dLayerDelete(ids.copy),last()];
          window.__a3dLayerCurrent(ids.anno);
          var sk=window.__a3dSketch('poly',[[0,0],[3,0],[3,2]]);
          window.__a3dLayerCurrent(ids.L0);
          out.delFull=[window.__a3dLayerDelete(ids.anno),last()];
          var tmp=window.__a3dLayerNew({name:'TEMP'}),tsub=window.__a3dLayerNew({name:'TEMP-SUB',parent:tmp});
          out.delEmpty=[window.__a3dLayerDelete(tmp),last()];
          var L=window.__a3dLayers(),sub=L.filter(function(l){return l.id===tsub;})[0];
          out.subUp=sub?sub.parent:'gone';
          window.__a3dLayerDelete(tsub);
          return {out:out,sk:sk,layers:window.__a3dLayers()};}""", ids)
        o = (ref or {}).get('out', {})
        by = {l['id']: l for l in (ref or {}).get('layers', [])}
        ck(o.get('dupName', [1])[0] is False and 'already a layer' in o['dupName'][1] and by.get(ids['copy'], {})['name'] == 'Layer 1',
           'a name already taken -- in any case -- is refused, and says so (%s)' % o.get('dupName'))
        ck(o.get('badChar', [1])[0] is False and 'cannot contain' in o['badChar'][1], 'a name with a character AutoCAD forbids is refused (%s)' % o.get('badChar'))
        ck(o.get('freezeCur', [1])[0] is False and 'current layer cannot be frozen' in o['freezeCur'][1] and not by.get(ids['L0'], {}).get('frozen'),
           'the current layer cannot be frozen (%s)' % o.get('freezeCur'))
        ck(o.get('freezeParentOfCur', [1])[0] is False and 'holds the current layer' in o['freezeParentOfCur'][1],
           'nor the layer above it (%s)' % o.get('freezeParentOfCur'))
        ck(o.get('frozenCurrent', [1])[0] is False and 'frozen layer cannot be current' in o['frozenCurrent'][1],
           'a frozen layer cannot be made current (%s)' % o.get('frozenCurrent'))
        ck(o.get('underSelf', [1])[0] is False and by.get(ids['wall'], {}).get('parent') in (None,),
           'a layer cannot go under one of its own sub-layers (%s)' % o.get('underSelf'))
        ck(o.get('trans95', [1])[0] is False and '0 to 90' in o['trans95'][1] and near(by.get(ids['anno'], {}).get('transparency'), 30),
           'transparency is 0 to 90 (%s)' % o.get('trans95'))
        ck(o.get('lw', [1])[0] is False and o.get('lt', [1])[0] is False and by.get(ids['anno'], {}).get('linetype') == 'HIDDEN',
           'a lineweight or a linetype AutoCAD does not have is refused (%s, %s)' % (o.get('lw'), o.get('lt')))
        ck(o.get('delFirst', [1])[0] is False and 'cannot be deleted' in o['delFirst'][1],
           'the first layer, layer 0\'s counterpart, cannot be deleted (%s)' % o.get('delFirst'))
        ck(o.get('delCur', [1])[0] is False and 'current layer cannot be deleted' in o['delCur'][1],
           'the current layer cannot be deleted (%s)' % o.get('delCur'))
        ck(o.get('delFull', [1])[0] is False and 'holds 1 object' in o['delFull'][1] and ids['anno'] in by,
           'a layer that holds objects cannot be deleted (%s)' % o.get('delFull'))
        ck(o.get('delEmpty', [0])[0] is True and o.get('subUp') is None,
           'an empty layer is deleted, and its sub-layer moves up (%s, parent %s)' % (o.get('delEmpty'), o.get('subUp')))
        sk = (ref or {}).get('sk')
        un = await safe("""(ids)=>{window.__a3dLayerSet(ids.anno,'linetype','PHANTOM');
            var a=window.__a3dLayers().filter(function(l){return l.id===ids.anno;})[0].linetype;
            window.__a3dRunCmd('undo');
            var L=window.__a3dLayers(),b=L.filter(function(l){return l.id===ids.anno;})[0].linetype;
            return [a,b,L.some(function(l){return l.name==='TEMP-SUB';})];}""", ids)
        ck(un == ['PHANTOM', 'HIDDEN', False], 'a layer change is one undo step: Undo takes back the change and nothing before it (%s)' % un)

        # ------------------------------------------------------------------------------------------
        print('\n-- 2. the three questions, and a sub-layer under its parent')
        q = await safe("""(a)=>{
          var ids=a.ids,sk=a.sk,res={base:window.__a3dLayerQ(sk)};
          window.__a3dLayerSet(ids.anno,'visible',false);res.off=window.__a3dLayerQ(sk);
          window.__a3dLayerSet(ids.anno,'visible',true);
          window.__a3dLayerSet(ids.anno,'frozen',true);res.frozen=window.__a3dLayerQ(sk);
          window.__a3dLayerSet(ids.anno,'frozen',false);
          window.__a3dLayerSet(ids.anno,'locked',true);res.locked=window.__a3dLayerQ(sk);
          window.__a3dLayerSet(ids.anno,'locked',false);
          window.__a3dLayerSet(ids.anno,'plot',false);res.noplot=window.__a3dLayerQ(sk);
          window.__a3dLayerSet(ids.anno,'plot',true);
          window.__a3dLayerCurrent(ids.full);
          var sk2=window.__a3dSketch('poly',[[5,0],[8,0],[8,1]]);
          window.__a3dLayerCurrent(ids.L0);
          res.sk2=window.__a3dLayerQ(sk2);
          window.__a3dLayerSet(ids.wall,'visible',false);res.childOff=window.__a3dLayerQ(sk2);
          window.__a3dLayerSet(ids.wall,'visible',true);
          window.__a3dLayerSet(ids.wall,'locked',true);res.childLocked=window.__a3dLayerQ(sk2);
          window.__a3dLayerSet(ids.wall,'locked',false);
          res.sk2id=sk2;
          return res;}""", {'ids': ids, 'sk': sk})
        q = q or {}

        def qs(k):
            v = q.get(k) or {}
            return (v.get('shown'), v.get('pickable'), v.get('selectable'))
        ck((q.get('base') or {}).get('layer') == ids['anno'] and qs('base') == (True, True, True), 'a sketch drawn on A-ANNO is on it: shown, pickable, selectable (%s)' % (qs('base'),))
        ck(qs('off') == (False, False, True), 'off: not drawn, not picked -- and still taken by SELECT ALL, as AutoCAD\'s ALL takes it (%s)' % (qs('off'),))
        ck(qs('frozen') == (False, False, False), 'frozen: taken by nothing (%s)' % (qs('frozen'),))
        ck(qs('locked') == (True, False, False) and near((q.get('locked') or {}).get('alpha'), 0.35, 1e-9),
           'locked: drawn, faded by half on screen over its 30 percent transparency, not selected (%s, alpha %s)' % (qs('locked'), (q.get('locked') or {}).get('alpha')))
        ck(qs('noplot') == (True, True, True) and (q.get('noplot') or {}).get('plot') is False, 'no-plot: drawn on screen, and not plotted (%s)' % (qs('noplot'),))
        ck((q.get('sk2') or {}).get('layer') == ids['full'] and qs('childOff') == (False, False, True) and qs('childLocked')[1] is False,
           'a sub-layer is off or locked when the layer above it is (%s, %s)' % (qs('childOff'), qs('childLocked')))
        sk2 = q.get('sk2id')

        # ------------------------------------------------------------------------------------------
        print('\n-- 3. the look: By Layer on screen')
        look = await safe("""(a)=>{
          var ids=a.ids,sk=a.sk;
          window.__a3dSetPlanView();window.__a3dTestPaint();
          var r={a:window.__a3dLastLook(sk)};
          window.__a3dLayerSet(ids.anno,'linetype','DASHED');window.__a3dLayerSet(ids.anno,'lineweight',null);
          window.__a3dTestPaint();r.b=window.__a3dLastLook(sk);
          window.__a3dLayerSet(ids.anno,'color','#d06040');window.__a3dTestPaint();r.c=window.__a3dLastLook(sk);
          window.__a3dLayerCurrent(ids.wall);
          var w=window.__a3dWall([[0,6],[6,6]],0.3,3,'center',false);
          window.__a3dLayerCurrent(ids.L0);
          window.__a3dLayerSet(ids.wall,'transparency',50);
          window.__a3dTestPaint();
          r.wall=w;r.wallQ=window.__a3dLayerQ(w);r.gl=window.__a3dLastGlAlpha(w);
          window.__a3dLayerSet(ids.wall,'transparency',0);
          return r;}""", {'ids': ids, 'sk': sk})
        look = look or {}
        la, lb, lc = look.get('a') or {}, look.get('b') or {}, look.get('c') or {}
        ck(nears(la.get('dash'), [6, 3]) and near(la.get('width'), 3.2) and near(la.get('alpha'), 0.7) and la.get('color') == '#84b98c',
           'HIDDEN at 0.50 mm and 30 percent: dashes 6 on 3 off, 3.2 px, alpha 0.7, the layer\'s color (%s)' % la)
        ck(nears(lb.get('dash'), [12, 6]) and near(lb.get('width'), 1.6),
           'DASHED at Default: 12 on 6 off, and the 1.6 px every line had before (%s)' % lb)
        ck(lc.get('color') == '#d06040', 'a new layer color is the linework\'s color (%s)' % lc.get('color'))
        thick = await safe("""(ids)=>{
          var L=window.__a3dLayerNew({name:'W-THICK'});window.__a3dLayerSet(L,'lineweight',2);
          window.__a3dLayerCurrent(L);window.__a3dSketch('poly',[[20,20],[26,20],[32,20]]);window.__a3dLayerCurrent(ids.L0);
          window.__a3dSelectFor([]);window.__a3dSetPlanView();window.__a3dFit();return L;}""", ids)
        await page.wait_for_timeout(700)   # the framing settles before anything is measured
        mxy = await safe("""()=>{var r=document.getElementById('a3d-canvas').getBoundingClientRect(),m=window.__a3dToScreen([23,20]);
            return [r.left+m[0],r.top+m[1]];}""")
        if mxy:   # the cursor's crosshair is drawn on the same canvas: keep it well away from the line
            await page.mouse.move(mxy[0] + 170, mxy[1] + 150)
            await page.wait_for_timeout(150)
        px = await safe("""(L)=>{
          window.__a3dTestPaint();
          var r=document.getElementById('a3d-canvas').getBoundingClientRect(),m=window.__a3dToScreen([23,20]);
          var x=r.left+m[0],y=r.top+m[1];
          /* the run of drawn pixels across the line, found by scanning rather than assumed at the
             projected point: the width is what is measured */
          var run=function(){var d,best=null,cur=null;for(d=-24;d<=24;d++){var a=window.__a3dPixelAlpha(x,y+d)>0;
            if(a){if(!cur)cur=[d,d];else cur[1]=d;}else if(cur){if(!best||Math.abs((cur[0]+cur[1])/2)<Math.abs((best[0]+best[1])/2))best=cur;cur=null;}}
            if(cur&&(!best||Math.abs((cur[0]+cur[1])/2)<Math.abs((best[0]+best[1])/2)))best=cur;
            return best?best[1]-best[0]+1:0;};
          var res={thick:run(),onscreen:m[0]>0&&m[1]>0&&m[0]<r.width&&m[1]<r.height};
          window.__a3dLayerSet(L,'lineweight',null);window.__a3dTestPaint();
          res.thin=run();
          return res;}""", thick)
        ck(px and px['onscreen'] and 12 <= px['thick'] <= 15 and 1 <= px['thin'] <= 3,
           'and the line is drawn that wide: 2.00 mm is 12.8 px across on the canvas, Default 1.6 (%s)' % px)
        ck((look.get('wallQ') or {}).get('layer') == ids['wall'] and near(look.get('gl'), 0.5),
           'a wall keeps its material and takes its layer\'s transparency in the GL renderer (%s)' % look.get('gl'))
        wall = look.get('wall')

        # ------------------------------------------------------------------------------------------
        print('\n-- 4. every way of selecting asks the layers')
        sel = await safe("""(ids)=>{
          window.__a3dTestSetObjs([]);
          var mk=function(name,st){var l=window.__a3dLayerNew({name:name});if(st)window.__a3dLayerSet(l,st[0],st[1]);return l;};
          var LB=mk('B-OFF'),LC=mk('C-FRZ'),LD=mk('D-LCK');
          var out={LB:LB,LC:LC,LD:LD};
          function on(l,pts){window.__a3dLayerCurrent(l);var s=window.__a3dSketch('poly',pts);return s;}
          out.a=on(ids.L0,[[0,0],[2,0],[2,1]]);out.b=on(LB,[[3,0],[5,0],[5,1]]);
          out.c=on(LC,[[6,0],[8,0],[8,1]]);out.d=on(LD,[[9,0],[11,0],[11,1]]);
          window.__a3dLayerCurrent(ids.L0);
          window.__a3dLayerSet(LB,'visible',false);window.__a3dLayerSet(LC,'frozen',true);window.__a3dLayerSet(LD,'locked',true);
          var cls=window.__a3dAddClassification('Pr_40','Linework');
          [out.a,out.b,out.c,out.d].forEach(function(id){window.__a3dSetObjClass(id,cls);});
          out.cls=cls;
          window.__a3dSelectFor([]);
          window.__a3dFit();window.__a3dTestPaint();
          return out;}""", ids)
        sel = sel or {}
        await palette('SELECTALL')
        got = await safe("()=>window.__a3dSelSet()") or []
        tst = await toast()
        ck(sorted(got) == sorted([sel.get('a'), sel.get('b')]),
           'SELECTALL, typed in the command line, takes what is on and off and leaves out frozen and locked (%d of 4)' % len(got))
        ck('1 of them on layers that are off' in tst and '2 on frozen or locked layers left out' in tst,
           'and says how many cannot be seen and how many were left out (%r)' % tst)
        mq = await safe("()=>{window.__a3dSelectFor([]);return window.__a3dMarquee(-10000,-10000,10000,10000);}") or []
        ck(mq == [sel.get('a')], 'a window over everything picks only what is shown and unlocked (%s)' % mq)
        await safe("()=>{window.__a3dSelectFor([]);document.querySelector('#a3d-rail .a3d-railbtn[data-tab=\"browser\"]').click();}")
        opened = await safe("""(cls)=>{var g=document.querySelector('[data-a3dbgrp="classifications"]');
            if(!document.querySelector('[data-a3dbclass="'+cls+'"]')&&g)g.click();
            return !!document.querySelector('[data-a3dbclass="'+cls+'"]');}""", sel.get('cls'))
        if opened:
            await page.click('[data-a3dbclass="%s"]' % sel.get('cls'))
            await page.wait_for_timeout(200)
        got = await safe("()=>window.__a3dSelSet()") or []
        ck(opened and sorted(got) == sorted([sel.get('a'), sel.get('b')]),
           'the Project Browser\'s classification row selects by the same rule (%s)' % len(got))
        cur = await safe("""(a)=>{window.__a3dSelectFor([a.a]);window.__a3dLayerSet(a.L0,'locked',true);
            var r=window.__a3dSelSet();window.__a3dLayerSet(a.L0,'locked',false);return r;}""", {'a': sel.get('a'), 'L0': ids['L0']})
        ck(cur == [], 'locking a layer drops its objects from the selection (%s)' % cur)
        cur = await safe("""(a)=>{window.__a3dSelectFor([a.a]);window.__a3dLayerSet(a.L0,'visible',false);
            var r=window.__a3dSelSet();window.__a3dLayerSet(a.L0,'visible',true);return r;}""", {'a': sel.get('a'), 'L0': ids['L0']})
        ck(cur == [], 'and so does turning it off: a selection made by picking holds nothing that cannot be seen (%s)' % cur)
        drawn = await safe("""(a)=>{window.__a3dSelectFor([]);var before=window.__a3dObjects().map(function(o){return o.id;});
            window.__a3dLayerCurrent(a.LD);window.__a3dSketch('poly',[[0,4],[2,4],[2,5]]);window.__a3dLayerCurrent(a.L0);
            var made=window.__a3dObjects().filter(function(o){return before.indexOf(o.id)<0;}).map(function(o){return o.id;});
            var ran=window.__a3dRunCmd('del');
            var still=window.__a3dObjects().filter(function(o){return made.indexOf(o.id)>=0;}).length;
            return {made:made,layer:made.length?window.__a3dLayerQ(made[0]).layer:null,sel:window.__a3dSelSet(),still:still};}""",
                           {'LD': sel.get('LD'), 'L0': ids['L0']})
        ck(drawn and len(drawn['made']) == 1 and drawn['layer'] == sel.get('LD') and drawn['sel'] == [] and drawn['still'] == 1,
           'a sketch drawn on a locked current layer is made there and not left selected: ERASE right after it erases nothing (%s)' % drawn)

        chk = await safe("""(a)=>{window.__a3dLayerSet(a.LD,'locked',false);window.__a3dLayerCurrent(a.LD);
            var w=window.__a3dWall([[0,8],[4,8]],0.3,3,'center',false);window.__a3dLayerCurrent(a.L0);
            window.__a3dLayerSet(a.LD,'locked',true);window.__a3dSelectFor([]);window.__a3dOpenCheckModelDlg();
            return {w:w,row:!!document.querySelector('[data-checkid="'+w+'"]')};}""", {'LD': sel.get('LD'), 'L0': ids['L0']})
        if chk and chk.get('row'):
            await page.click('[data-checkid="%s"]' % chk['w'])
            await page.wait_for_timeout(150)
        got = await safe("()=>window.__a3dSelSet()")
        tst = await toast()
        ck(chk and chk.get('row') and got == [] and 'locked: it cannot be selected' in tst,
           'a Check Model row naming a wall on a locked layer refuses it, and says why (%r)' % tst)
        await safe("()=>{var b=document.querySelector('.a3d-dlg [data-a3dlg]');if(b)b.click();}")

        dep = await safe("""(a)=>{window.__a3dLayerSet(a.LD,'locked',false);window.__a3dLayerCurrent(a.L0);
            var s=window.__a3dSketch('rect',[[0,12],[3,14]]);
            var p=window.__a3dCreateRoomAt([1.5,13],0);window.__a3dObjSetLayer(s,a.LD);window.__a3dLayerSet(a.LD,'locked',true);
            window.__a3dSelectFor([p]);window.__a3dRefreshProps();
            return {s:s,p:p,row:!!document.querySelector('[data-propsel="'+s+'"]')};}""", {'LD': sel.get('LD'), 'L0': ids['L0']})
        if dep and dep.get('row'):
            await page.click('[data-propsel="%s"]' % dep['s'])
            await page.wait_for_timeout(150)
        got = await safe("()=>window.__a3dSelSet()")
        tst = await toast()
        ck(dep and dep.get('row') and got == [dep['p']] and 'locked: it cannot be selected' in tst,
           'the Dependencies row naming a room\'s source sketch on a locked layer refuses it, and the room stays selected (%s, %r)' % (got, tst))

        # ------------------------------------------------------------------------------------------
        print('\n-- 5. the Layers panel: the model inside the layers')
        await safe("()=>{window.__a3dSelectFor([]);}")
        await page.click('#a3d-rail .a3d-railbtn[data-tab="layers"]')
        await page.wait_for_timeout(250)
        if not await safe("(id)=>!!document.querySelector('[data-lyid=\"'+id+'\"]')", ids['full']):
            await page.click('[data-lytog="%s"]' % ids['wall'])   # a closed layer lists no sub-layers
            await page.wait_for_timeout(150)
        pan = await safe("""()=>{var p=document.querySelector('#a3d-leftpanel .a3d-lyp');if(!p)return null;
            var r=p.getBoundingClientRect(),hit=document.elementFromPoint(r.left+r.width/2,r.top+40);
            return {shown:!!(hit&&p.contains(hit)),rows:[].map.call(p.querySelectorAll('[data-lyid]'),function(e){
              return [e.getAttribute('data-lyid'),parseFloat(e.style.paddingLeft)];})};}""")
        tree = await safe("()=>window.__a3dLayerTree()") or []
        ck(pan and pan['shown'], 'the Layers tab shows the panel, and it is what the pointer hits')
        ck(pan and [r[0] for r in pan['rows']] == [x['id'] for x in tree]
           and all(near(r[1], 4 + 14 * x['depth']) for r, x in zip(pan['rows'], tree)),
           'its rows are the layer tree, sub-layers indented (%d rows)' % (len(pan['rows']) if pan else 0))
        await page.click('[data-lyon="%s"]' % ids['anno'])
        await page.wait_for_timeout(150)
        v1 = await safe("(id)=>window.__a3dLayers().filter(function(l){return l.id===id;})[0].visible", ids['anno'])
        await page.click('[data-lyon="%s"]' % ids['anno'])
        await page.wait_for_timeout(150)
        v2 = await safe("(id)=>window.__a3dLayers().filter(function(l){return l.id===id;})[0].visible", ids['anno'])
        ck(v1 is False and v2 is True, 'its On switch turns the layer off and on (%s, %s)' % (v1, v2))
        cl = await safe("()=>window.__a3dActiveLayer()")
        await page.click('[data-lyfrz="%s"]' % cl)
        await page.wait_for_timeout(150)
        fz = await safe("(id)=>!!window.__a3dLayers().filter(function(l){return l.id===id;})[0].frozen", cl)
        tst = await toast()
        ck(fz is False and 'cannot be frozen' in tst, 'its Freeze switch on the current layer is refused, and says so (%r)' % tst)
        await page.click('[data-lycur="%s"]' % ids['wall'])
        await page.wait_for_timeout(150)
        ck(await safe("()=>window.__a3dActiveLayer()") == ids['wall'], 'its status mark makes a layer current')
        await page.click('[data-lycur="%s"]' % ids['L0'])
        await page.dblclick('[data-lyname="%s"]' % ids['anno'])
        await page.wait_for_timeout(150)
        await page.fill('[data-lyren="%s"]' % ids['anno'], 'A-ANNO-TEXT')
        await page.keyboard.press('Enter')
        await page.wait_for_timeout(150)
        await page.dblclick('[data-lyname="%s"]' % ids['anno'])
        await page.wait_for_timeout(150)
        await page.fill('[data-lyren="%s"]' % ids['anno'], 'THROWN-AWAY')
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(150)
        nm = await safe("(id)=>window.__a3dLayers().filter(function(l){return l.id===id;})[0].name", ids['anno'])
        ck(nm == 'A-ANNO-TEXT', 'a double-click renames in place: Enter keeps the name, Escape does not (%s)' % nm)
        await safe("""(id)=>{var e=document.querySelector('[data-lycol="'+id+'"]');e.value='#3070e0';e.dispatchEvent(new Event('change',{bubbles:true}));}""", ids['anno'])
        await page.wait_for_timeout(120)
        col = await safe("(id)=>window.__a3dLayers().filter(function(l){return l.id===id;})[0].color", ids['anno'])
        ck(col == '#3070e0', 'its color field sets the layer\'s color (%s)' % col)
        if await safe("(id)=>!document.querySelector('[data-lyobj]')&&!!document.querySelector('[data-lytog=\"'+id+'\"]')", ids['L0']):
            await page.click('[data-lytog="%s"]' % ids['L0'])
            await page.wait_for_timeout(150)
        objrow = await safe("(id)=>{var r=document.querySelector('[data-lyobj=\"'+id+'\"]');return !!r;}", sel.get('a'))
        if objrow:
            await page.click('[data-lyobj="%s"] .a3d-lynm' % sel.get('a'))
            await page.wait_for_timeout(150)
        got = await safe("()=>window.__a3dSelSet()")
        ck(objrow and got == [sel.get('a')], 'a layer opens to its objects, and an object row selects it (%s)' % got)
        if objrow:
            await page.drag_and_drop('[data-lyobj="%s"]' % sel.get('a'), '[data-lyid="%s"]' % ids['wall'])
            await page.wait_for_timeout(200)
        lq = await safe("(id)=>window.__a3dLayerQ(id).layer", sel.get('a'))
        ck(lq == ids['wall'], 'dragging an object onto a layer moves it there (%s)' % lq)
        await page.drag_and_drop('[data-lyid="%s"]' % ids['copy'], '[data-lyid="%s"]' % ids['wall'])
        await page.wait_for_timeout(200)
        par = await safe("(id)=>window.__a3dLayers().filter(function(l){return l.id===id;})[0].parent", ids['copy'])
        ck(par == ids['wall'], 'dragging a layer onto another makes it a sub-layer (%s)' % par)
        await page.fill('.a3d-lysearch[data-lysearch]', 'full')
        await page.wait_for_timeout(150)
        vis = await safe("()=>[].map.call(document.querySelectorAll('#a3d-leftpanel [data-lyid]'),function(e){return e.getAttribute('data-lyid');})") or []
        ck(vis == [ids['wall'], ids['full']], 'the search lists the layers that match, with their parents (%s)' % vis)
        await page.fill('.a3d-lysearch[data-lysearch]', '')
        await page.wait_for_timeout(100)
        n0 = len(await safe("()=>window.__a3dLayers()") or [])
        await page.click('.a3d-lyp [data-lyact="new"]')
        await page.wait_for_timeout(200)
        foc = await safe("()=>{var a=document.activeElement;return a&&a.hasAttribute('data-lyren')?a.getAttribute('data-lyren'):null;}")
        await page.keyboard.type('S-COLS')
        await page.keyboard.press('Enter')
        await page.wait_for_timeout(150)
        ly = await safe("()=>window.__a3dLayers()") or []
        ck(len(ly) == n0 + 1 and foc and any(l['id'] == foc and l['name'] == 'S-COLS' for l in ly),
           'New layer makes one and puts its name up for typing (%s)' % [l['name'] for l in ly][-2:])

        # ------------------------------------------------------------------------------------------
        print('\n-- 6. the Layer Properties Manager: LAYER in the command line')
        await blur()
        await palette('LA')
        dlg = await safe("""()=>{var d=document.querySelector('.a3d-dlg.a3d-lpm');if(!d)return null;var r=d.getBoundingClientRect();
            var hit=document.elementFromPoint(r.left+r.width/2,r.top+12);
            return {top:!!(hit&&d.contains(hit)),heads:[].map.call(d.querySelectorAll('th'),function(t){return t.textContent;}),
                    rows:[].map.call(d.querySelectorAll('[data-lpmid]'),function(t){return t.getAttribute('data-lpmid');})};}""")
        tree = await safe("()=>window.__a3dLayerTree()") or []
        ck(dlg and dlg['top'], 'LA opens the Layer Properties Manager, and it is on top')
        ck(dlg and dlg['heads'] == HEADERS, 'its columns are AutoCAD\'s (%s)' % (dlg and dlg['heads']))
        ck(dlg and dlg['rows'] == [x['id'] for x in tree], 'its rows are the layer tree (%d)' % (len(dlg['rows']) if dlg else 0))
        A = ids['anno']
        row = '.a3d-lpm [data-lpmid="%s"] ' % A

        def lay(id_):
            return safe("(id)=>window.__a3dLayers().filter(function(l){return l.id===id;})[0]", id_)
        await page.select_option(row + '[data-lpmf="linetype"]', 'CENTER')
        await page.wait_for_timeout(100)
        await page.select_option(row + '[data-lpmf="lineweight"]', '0.35')
        await page.wait_for_timeout(100)
        la = await lay(A) or {}
        ck(la.get('linetype') == 'CENTER' and near(la.get('lineweight'), 0.35), 'its Linetype and Lineweight cells set the layer (%s, %s)' % (la.get('linetype'), la.get('lineweight')))
        await page.fill(row + '[data-lpmf="transparency"]', '95')
        await page.keyboard.press('Tab')
        await page.wait_for_timeout(150)
        shown = await safe("(sel)=>document.querySelector(sel).value", row + '[data-lpmf="transparency"]')
        la = await lay(A) or {}
        ck(near(la.get('transparency'), 30) and shown == '30', 'a transparency of 95 is refused, and the cell goes back to the layer\'s 30 (%s)' % shown)
        await page.fill(row + '[data-lpmf="transparency"]', '40')
        await page.keyboard.press('Tab')
        await page.wait_for_timeout(150)
        await page.fill(row + '[data-lpmf="description"]', 'Notes and tags')
        await page.keyboard.press('Tab')
        await page.wait_for_timeout(150)
        await page.click(row + '[data-lpmtgl="plot"]')
        await page.wait_for_timeout(150)
        la = await lay(A) or {}
        ck(near(la.get('transparency'), 40) and la.get('description') == 'Notes and tags' and la.get('plot') is False,
           'its Transparency, Description and Plot cells set the layer (%s, %r, %s)' % (la.get('transparency'), la.get('description'), la.get('plot')))
        await page.click(row + '[data-lpmtgl="plot"]')
        await page.wait_for_timeout(100)
        curL = await safe("()=>window.__a3dActiveLayer()")
        await page.click('.a3d-lpm [data-lpmid="%s"] [data-lpmtgl="frozen"]' % curL)
        await page.wait_for_timeout(150)
        pressed = await safe("(id)=>document.querySelector('.a3d-lpm [data-lpmid=\"'+id+'\"] [data-lpmtgl=\"frozen\"]').getAttribute('aria-pressed')", curL)
        cz = await lay(curL) or {}
        ck(not cz.get('frozen') and pressed == 'false', 'Freeze on the current layer is refused, and the cell shows it thawed (%s)' % pressed)
        await page.fill(row + '[data-lpmf="name"]', 'A-WALL')
        await page.keyboard.press('Enter')
        await page.wait_for_timeout(150)
        shown = await safe("(sel)=>document.querySelector(sel).value", row + '[data-lpmf="name"]')
        ck(shown == 'A-ANNO-TEXT', 'a name already taken is refused in the table too, and the cell shows the layer\'s own (%s)' % shown)
        n0 = len(await safe("()=>window.__a3dLayers()") or [])
        await page.click('.a3d-lpm [data-lpmact="new"]')
        await page.wait_for_timeout(200)
        n1 = len(await safe("()=>window.__a3dLayers()") or [])
        await page.click('.a3d-lpm [data-lpmact="del"]')
        await page.wait_for_timeout(200)
        n2 = len(await safe("()=>window.__a3dLayers()") or [])
        ck(n1 == n0 + 1 and n2 == n0, 'New layer and Delete act on the picked row (%d, %d, %d)' % (n0, n1, n2))
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(150)
        ck(await safe("()=>!document.querySelector('.a3d-lpm')"), 'Escape closes it')

        ac = await safe("""()=>{window.__a3dSelectFor([]);window.__a3dRefreshProps();
            var s=document.querySelector('[data-propmodel="layer"]');if(!s)return null;
            return {ids:[].map.call(s.options,function(o){return o.value;}),txt:[].map.call(s.options,function(o){return o.textContent;})};}""")
        tree = await safe("()=>window.__a3dLayerTree()") or []
        ck(ac and ac['ids'] == [x['id'] for x in tree]
           and all(tx.startswith('\u00a0' * 3 * x['depth']) and not tx.startswith('\u00a0' * (3 * x['depth'] + 1)) for tx, x in zip(ac['txt'], tree)),
           'Model Properties\' Active Layer lists the same tree, sub-layers indented (%d)' % (len(ac['ids']) if ac else 0))
        fzid = await safe("""(ids)=>{window.__a3dLayerSet(ids.full,'frozen',true);window.__a3dRefreshProps();return ids.full;}""", ids)
        await safe("()=>window.__a3dSetPropTab&&window.__a3dSetPropTab('view')")   # AMENDED FOR V141: the field is on Properties' View tab
        await page.select_option('[data-propmodel="layer"]', fzid)
        await page.wait_for_timeout(200)
        shown = await safe("()=>document.querySelector('[data-propmodel=\"layer\"]').value")
        curL = await safe("()=>window.__a3dActiveLayer()")
        await safe("(ids)=>window.__a3dLayerSet(ids.full,'frozen',false)", ids)
        ck(curL != fzid and shown == curL, 'and choosing a frozen layer there is refused, the field showing the current layer again (%s)' % (shown == curL))

        # ------------------------------------------------------------------------------------------
        print('\n-- 7. a plot is a plot')
        pl = await safe("""()=>{
          window.__a3dTestSetObjs([]);
          var L0=window.__a3dLayers()[0].id;window.__a3dLayerCurrent(L0);
          var mk=function(n){return window.__a3dLayerNew({name:n});};
          var PA=mk('P-A'),PB=mk('P-OFF'),PC=mk('P-FRZ'),PN=mk('P-NOPLOT'),PK=mk('P-LCK');
          window.__a3dLayerSet(PA,'linetype','DASHED');window.__a3dLayerSet(PA,'lineweight',0.5);window.__a3dLayerSet(PA,'color','#c03030');
          function on(l,y){window.__a3dLayerCurrent(l);return window.__a3dSketch('poly',[[0,y],[6,y],[6,y+1]]);}
          var r={L0:L0,PA:PA,PB:PB,PC:PC,PN:PN,PK:PK,a:on(PA,0),b:on(PB,2),c:on(PC,4),n:on(PN,6),k:on(PK,8)};
          window.__a3dLayerCurrent(L0);
          window.__a3dLayerSet(PB,'visible',false);window.__a3dLayerSet(PC,'frozen',true);
          window.__a3dLayerSet(PN,'plot',false);window.__a3dLayerSet(PK,'locked',true);
          return r;}""")
        pl = pl or {}
        svg = await safe("()=>window.__a3dBuildSVG('technical').text") or ''
        has = {k: ('data-obj="%s"' % pl.get(k)) in svg for k in ('a', 'b', 'c', 'n', 'k')}
        ck(has == {'a': True, 'b': False, 'c': False, 'n': False, 'k': True},
           'the plan SVG leaves out off, frozen and no-plot layers and keeps a locked one (%s)' % has)
        m = re.search(r'<path data-obj="%s"([^>]*)>' % re.escape(pl.get('a') or 'x'), svg)
        g = re.search(r'<g fill="none" stroke="#000000" stroke-width="([0-9.]+)"', svg)
        attrs = m.group(1) if m else ''
        da = re.search(r'stroke-dasharray="([^"]+)"', attrs)
        sw = re.search(r'stroke-width="([0-9.]+)"', attrs)
        unit = float(g.group(1)) / 0.25 if g else None
        dv = [float(x) for x in da.group(1).split()] if da else []
        ck(unit and nears(dv, [12.7 * unit, 6.35 * unit], 1e-4) and sw and near(float(sw.group(1)), 0.5 * unit, 1e-5) and 'stroke="#' not in attrs,
           'DASHED at 0.50 mm plots as its millimetres against the drawing\'s own 0.25 mm, monochrome in a technical plot (%s)' % attrs.strip()[:120])
        svgp = await safe("()=>window.__a3dBuildSVG('presentation').text") or ''
        mp = re.search(r'<path data-obj="%s"([^>]*)>' % re.escape(pl.get('a') or 'x'), svgp)
        mk2 = re.search(r'<path data-obj="%s"([^>]*)>' % re.escape(pl.get('k') or 'x'), svgp)
        ck(mp and 'stroke="#c03030"' in mp.group(1) and mk2 and 'opacity="0.5' not in mk2.group(1),
           'a presentation plots the layer\'s color, and no lock fade (%s)' % (mp.group(1).strip()[:90] if mp else None))
        sh = await safe("""(p)=>{var s=window.__a3dAddSheet('A-101','Layers','ANSI-B-L');
            var lv=window.__a3dLevels?window.__a3dLevels()[0].id:null;
            var opts=window.__a3dSheetSourceOptions?window.__a3dSheetSourceOptions():[];
            var plan=opts.filter(function(o){return o.kind==='plan';})[0];
            var vp=plan?window.__a3dAddViewport(s,'plan',plan.refId||plan.id,'fit',100):null;
            var svg=window.__a3dBuildSheetSVG(s,'technical');
            return {s:s,vp:vp,svg:svg,plan:plan||null};}""", pl)
        ssvg = (sh or {}).get('svg') or ''
        ms = re.search(r'<path data-obj="%s"([^>]*)>' % re.escape(pl.get('a') or 'x'), ssvg)
        ck(ms and 'stroke-dasharray="12.7 6.35"' in ms.group(1) and 'stroke-width="0.500000"' in ms.group(1)
           and ('data-obj="%s"' % pl.get('n')) not in ssvg,
           'the sheet SVG, in paper millimetres, draws DASHED as 12.7 on 6.35 off at 0.50 mm, and leaves out the no-plot layer (%s)'
           % (ms.group(1).strip()[:100] if ms else (sh or {}).get('plan')))
        onsh = await safe("""(s)=>{window.__a3dOpenSheetView(s);var ran=window.__a3dRunCmd('layers');
            var open=!!document.querySelector('.a3d-dlg.a3d-lpm');var b=document.querySelector('.a3d-lpm [data-lpmact="close"]');if(b)b.click();
            window.__a3dCloseSheetView();return {ran:ran,open:open};}""", (sh or {}).get('s'))
        ck(onsh and onsh['ran'] is True and onsh['open'], 'LAYER runs on a sheet as well, as AutoCAD\'s does (%s)' % onsh)
        ppl = await safe("""(p)=>{window.__a3dOpenSheetView(p.s);
            var a=window.__a3dPlotLook(p.a,6),n=window.__a3dPlotLook(p.n,6),k=window.__a3dPlotLook(p.k,6);
            window.__a3dRenderSheetPNG(3);var ns=window.__a3dLastLook(p.n);
            window.__a3dCloseSheetView();
            return {a:a,n:n,k:k,ns:ns};}""", {'s': (sh or {}).get('s'), 'a': pl.get('a'), 'n': pl.get('n'), 'k': pl.get('k')})
        ppl = ppl or {}
        ck(nears((ppl.get('a') or {}).get('dash'), [76.2, 38.1], 1e-6) and near((ppl.get('a') or {}).get('width'), 3.0),
           'on the sheet\'s paper at 6 px/mm a DASHED 0.50 mm line is 76.2 on, 38.1 off and 3 px wide (%s)' % ppl.get('a'))
        ck(ppl.get('n') is None and ppl.get('ns') is not None,
           'a no-plot layer is drawn on the sheet on screen and left off its paper (%s, %s)' % (bool(ppl.get('ns')), ppl.get('n')))
        ck(near((ppl.get('k') or {}).get('alpha'), 1), 'and a locked layer is plotted unfaded (%s)' % (ppl.get('k') or {}).get('alpha'))

        dxf = await safe("()=>window.__a3dBuildDXF().text") or ''
        lines = dxf.replace('\r\n', '\n').split('\n')
        pairs = [(lines[i].strip(), lines[i + 1].strip()) for i in range(0, len(lines) - 1, 2)]
        recs, cur = [], None
        for c, v in pairs:
            if c == '0':
                cur = {'type': v, 'g': []}
                recs.append(cur)
            elif cur is not None:
                cur['g'].append((c, v))

        def rec(typ, name):
            for r in recs:
                if r['type'] == typ and ('2', name) in r['g']:
                    return dict(r['g'])
            return None
        ra, rb, rc, rn, rk = (rec('LAYER', x) for x in ('P-A', 'P-OFF', 'P-FRZ', 'P-NOPLOT', 'P-LCK'))
        ck(ra and ra.get('6') == 'DASHED' and ra.get('370') == '50' and ra.get('420') == str(0xc03030) and ra.get('62') == '1',
           'the DXF writes a layer\'s linetype, lineweight and exact color, with the nearest standard color in 62 (%s)' % ra)
        ck(rb and int(rb.get('62', '0')) < 0 and rc and rc.get('70') == '1' and rk and rk.get('70') == '4' and rn and rn.get('290') == '0',
           'off as a negative color, frozen and locked in 70, no-plot in 290 (%s %s %s %s)'
           % (rb and rb.get('62'), rc and rc.get('70'), rk and rk.get('70'), rn and rn.get('290')))
        lt = rec('LTYPE', 'DASHED')
        ck(lt and lt.get('73') == '2' and near(lt.get('40'), 19.05, 1e-4),
           'and defines DASHED in its LTYPE table with acadiso\'s millimetres (%s)' % lt)
        rt = await safe("""(a)=>{
          window.__a3dTestSetObjs([]);window.__a3dLayerCurrent(a.L0);
          ['P-A','P-OFF','P-FRZ','P-NOPLOT','P-LCK'].forEach(function(n){
            var l=window.__a3dLayers().filter(function(x){return x.name===n;})[0];
            if(l){window.__a3dLayerSet(l.id,'frozen',false);window.__a3dLayerDelete(l.id);}});
          window.__a3dImportText(a.dxf,'layers-roundtrip.dxf');
          var L=window.__a3dLayers(),o={};
          ['P-A','P-OFF','P-FRZ','P-NOPLOT','P-LCK'].forEach(function(n){o[n]=L.filter(function(x){return x.name===n;})[0]||null;});
          return o;}""", {'dxf': dxf, 'L0': pl.get('L0')})
        rt = rt or {}
        g2 = lambda n, k: (rt.get(n) or {}).get(k)
        ck(g2('P-A', 'linetype') == 'DASHED' and near(g2('P-A', 'lineweight'), 0.5) and g2('P-A', 'color') == '#c03030'
           and g2('P-OFF', 'visible') is False and g2('P-FRZ', 'frozen') is True and g2('P-LCK', 'locked') is True
           and g2('P-NOPLOT', 'plot') is False,
           'and the importer reads every one of them back (%s)' % {n: (rt.get(n) or {}).get('id') is not None for n in rt})

        # ------------------------------------------------------------------------------------------
        print('\n-- 8. older data loads unchanged, and the new fields survive a reload')
        old = await safe("""()=>{
          window.__a3dTestSetObjs([]);
          var L0=window.__a3dLayers()[0].id;window.__a3dLayerCurrent(L0);
          var s=window.__a3dSketch('poly',[[0,0],[2,0],[2,2]]);
          var snap=window.__a3dObjSnapshot(s);delete snap.layer;
          var env=JSON.parse(window.__a3dProjectEnvelope());
          env.data.objs=[snap];
          env.data.layers=[{id:'layer-0',name:'Model',color:'#7f9db8',visible:true,locked:false},
                           {id:'layer-old',name:'Old',color:'#c0a377',visible:true,locked:false}];
          env.data.activeLayer='layer-old';
          var ok=window.__a3dImportProject(JSON.stringify(env),'older.acad3d.json');
          var L=window.__a3dLayers();
          return {ok:ok,layers:L,q:window.__a3dLayerQ(snap.id),id:snap.id};}""")
        old = old or {}
        lo = [l for l in old.get('layers', []) if l.get('id') == 'layer-old']
        ck(old.get('ok') is True and lo and set(lo[0].keys()) == {'id', 'name', 'color', 'visible', 'locked'},
           'an older project opens, and its layers are not rewritten (%s)' % (lo and sorted(lo[0].keys())))
        oq = old.get('q') or {}
        ck(oq.get('layer') == 'layer-old' and oq.get('shown') and oq.get('pickable') and oq.get('selectable') and oq.get('plot'),
           'its layerless object joins the layer that was current, which reads thawed, unlocked and plotted (%s)' % oq)
        await safe("""()=>{var L=window.__a3dLayers(),l=L[L.length-1];
            window.__a3dLayerSet(l.id,'linetype','PHANTOM');window.__a3dLayerSet(l.id,'lineweight',0.7);
            window.__a3dLayerSet(l.id,'description','kept');window.__a3dLayerNew({name:'OLD-SUB',parent:l.id});}""")
        await page.wait_for_timeout(900)
        before = await safe("()=>window.__a3dLayers()") or []
        await page.reload()
        await boot()
        after = await safe("()=>window.__a3dLayers()") or []
        keep = lambda L: [(l.get('name'), l.get('linetype'), l.get('lineweight'), l.get('description'), l.get('parent')) for l in L]
        ck(after and keep(after) == keep(before) and any(l.get('linetype') == 'PHANTOM' for l in after),
           'linetype, lineweight, description and sub-layers survive a reload (%s)' % keep(after)[-2:])

        print('\n-- 9. no errors')
        ck(errs == [], 'no page errors (%s)' % errs[:3])
        bad = [w for w in warns if 'could not' in w or 'failed' in w]
        ck(bad == [], 'no [BIM] warning of a failure (%s)' % bad[:3])
        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
