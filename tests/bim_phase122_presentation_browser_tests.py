"""bim_phase122_presentation_browser_tests.py -- V122: Presentation -- the pages, Present, the printed set.

The owner, V119, second in the left panel's stack: "Need a presentation for doing presentation with
clients. using layout spaces, with multi pages view like a pdf viewer." What this suite holds the
phase to, asserted on the model and on the pixels the pages are drawn with, every control driven:

  1. A PAGE IS THE SAME PAGE AT ANY SIZE, AND SHOWS NOTHING THAT IS NOT ON IT. A sheet drawn at twice
     its pixels reduces to the sheet drawn once; the PNG export is exactly that; the finest line is a
     pixel of the image. The model's selection, a selected grid and an unfinished sketch stay off the
     paper, and a schedule on a sheet draws.
  2. A SHEET IS DRAWN IN THE APPEARANCE IT PRINTS IN: Presentation reaches a sheet's viewports.
  3. THE PAGES DISPLAY IS A PDF READER OF THE SHEETS: every sheet in order, each the page as it plots,
     the page being read following the scroll and named everywhere, the page controls, the keys from
     their table, the zoom, a double-click to the layout, a model change redrawn.
  4. PRESENT: full screen, one page at a time, every key in its table does what it says, a click, the
     wheel and the bar; nothing typed reaches the model; Escape, or the browser leaving full screen,
     ends it where it started; refused full screen fills the window and says so.
  5. THE SET PRINTS AS ONE DOCUMENT, each page a vector sheet on its own paper size, in order.
  6. THE PRESENTATION PANEL: the pages in order as thumbnails of the plots; Present, + Page and Print
     set; click to read, double-click to edit, rename, drag and menu to reorder -- one order that the
     tabs, the pages and Present all follow, one undo step a move.
"""
import asyncio, base64, math, pathlib, re, sys
from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'
BLUE = [78, 161, 255]      # the selection's colour, #4ea1ff
RUBBER = [255, 212, 121]   # an unfinished sketch's rubber band, #ffd479


class Checks:
    def __init__(self):
        self.n, self.bad = 0, []

    def __call__(self, cond, msg):
        self.n += 1
        cond = bool(cond)
        if not cond:
            self.bad.append(msg)
        print(('  ok    ' if cond else '  FAIL  ') + msg)
        return cond


HELP = """()=>{window.__v122={
  load:function(url){return new Promise(function(res,rej){var i=new Image();i.onload=function(){res(i);};i.onerror=rej;i.src=url;});},
  px:async function(url){var i=await this.load(url),c=document.createElement('canvas');c.width=i.width;c.height=i.height;
    var x=c.getContext('2d');x.drawImage(i,0,0);return {w:i.width,h:i.height,d:x.getImageData(0,0,i.width,i.height).data};},
  near:async function(url,rgb,tol){var o=await this.px(url),n=0,k;
    for(k=0;k<o.d.length;k+=4)if(Math.abs(o.d[k]-rgb[0])<=tol&&Math.abs(o.d[k+1]-rgb[1])<=tol&&Math.abs(o.d[k+2]-rgb[2])<=tol)n++;return n;},
  dark:async function(url,r){var o=await this.px(url),x0=Math.round(r[0]*o.w),y0=Math.round(r[1]*o.h),x1=Math.round((r[0]+r[2])*o.w),y1=Math.round((r[1]+r[3])*o.h),n=0,x,y,k;
    for(y=y0;y<y1;y++)for(x=x0;x<x1;x++){k=(y*o.w+x)*4;if(o.d[k]+o.d[k+1]+o.d[k+2]<300)n++;}return n;},
  diff:async function(urlA,urlB,r){
    var a=await this.load(urlA),b=await this.load(urlB),w=a.width,h=a.height;
    var ca=document.createElement('canvas');ca.width=w;ca.height=h;var xa=ca.getContext('2d');xa.drawImage(a,0,0);
    var cb=document.createElement('canvas');cb.width=w;cb.height=h;var xb=cb.getContext('2d');xb.imageSmoothingEnabled=true;xb.imageSmoothingQuality='high';xb.drawImage(b,0,0,w,h);
    var x0=Math.round(r[0]*w),y0=Math.round(r[1]*h),rw=Math.max(1,Math.round(r[2]*w)),rh=Math.max(1,Math.round(r[3]*h));
    var da=xa.getImageData(x0,y0,rw,rh).data,db=xb.getImageData(x0,y0,rw,rh).data,s=0,k;
    for(k=0;k<da.length;k+=4)s+=Math.abs(da[k]-db[k])+Math.abs(da[k+1]-db[k+1])+Math.abs(da[k+2]-db[k+2]);
    return s/(rw*rh*3);}
  };return true;}"""

SETUP = """()=>{
  var w=[];
  [[[0,0],[8,0]],[[8,0],[8,6]],[[8,6],[0,6]],[[0,6],[0,0]]].forEach(function(p){w.push(window.__a3dWall(p,0.3,3,'center',false));});
  var room=window.__a3dCreateRoomAt([4,3],0);
  var opts=window.__a3dSheetSourceOptions();
  function pick(k){return opts.filter(function(o){return o.kind===k;})[0];}
  var s1=window.__a3dAddSheet('A101','Ground Floor Plan','ANSI-B-L');
  window.__a3dAddViewport(s1,'plan',pick('plan').refId,'fit',100);
  var s2=window.__a3dAddSheet('A201','Elevations','ANSI-B-L');
  window.__a3dAddViewport(s2,'elevation',pick('elevation').refId,'fit',100);
  var s3=window.__a3dAddSheet('A601','Room Schedule','A3-L');
  window.__a3dAddViewport(s3,'schedule','room','fit',100);
  return {walls:w,room:room,s:[s1,s2,s3]};
}"""


def static_checks(ck, t):
    print('\n-- 0. the file')
    code = re.sub(r'/\*.*?\*/', '', t, flags=re.S)
    ck('A3D_SHOW_KEYS[i].keys.indexOf(ev.key)' in code and 'A3D_PAGEVIEW_KEYS[i].keys.indexOf(key)' in code,
       'the key handlers of Present and of the Pages display read their tables')
    ck('bimShowSay(' in code and 'bimPageKeyWords(' in code and 'rows(A3D_PAGEVIEW_KEYS)' in code and 'rows(A3D_SHOW_KEYS)' in code,
       'and the hints and the shortcut sheet are drawn from the same tables')
    ck(code.count('bimSheetRename(') >= 3 and 'sh.name=v;' in code and code.count('sh.name=v') == 1,
       'a sheet is renamed in one place, which the tab and the page both call')
    ck('bimSheetMenuItems(id,where)' in code and 'bimSheetMenu(ev,id,\'tabs\')' in code and "bimSheetMenu(ev,it.getAttribute('data-prpitem'),'pages')" in code,
       'the layout tab and the page read one menu')


async def main():
    ck = Checks()
    t = HTML.read_text(encoding='utf-8')
    ck('__acad3dV122' in t, 'the V122 marker is present')
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


async def drive(ck):
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1600, 'height': 950}, accept_downloads=True)
        page = await ctx.new_page()
        page.set_default_timeout(8000)
        errs, warns, dialogs = [], [], []
        page.on('pageerror', lambda e: errs.append(str(e)[:200]))
        page.on('console', lambda m: warns.append(m.text[:240]) if m.type == 'warning' and m.text.startswith('[BIM]') else None)

        async def on_dialog(d):
            dialogs.append(d.message)
            await d.accept()
        page.on('dialog', lambda d: asyncio.ensure_future(on_dialog(d)))
        ev = page.evaluate

        async def safe(js, arg=None):
            try:
                return await (ev(js, arg) if arg is not None else ev(js))
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:200])
                return None

        async def settle(ms=300):
            await page.wait_for_timeout(ms)

        async def pages():
            return await safe("()=>window.__a3dPages()") or {}

        async def pages_drawn(n=40):
            p = {}
            for _ in range(n):
                p = await pages()
                if p.get('pages') and all(x['drawn'] for x in p['pages'] if x['el']):
                    break
                await page.wait_for_timeout(100)
            return p

        async def show():
            return await safe("()=>window.__a3dSlideshow()") or {}

        async def panel():
            return await safe("()=>window.__a3dPresPanel()") or {}

        async def thumbs_drawn(n=50):
            p = {}
            for _ in range(n):
                p = await panel()
                if p.get('items') and all(i['drawn'] for i in p['items']):
                    break
                await page.wait_for_timeout(100)
            return p

        async def order():
            return await safe("()=>window.__a3dSheets().map(function(s){return s.id;})") or []

        async def blur():
            await safe("()=>{if(document.activeElement&&document.activeElement!==document.body)document.activeElement.blur();return true;}")

        async def menu_items():
            return await safe("()=>{var m=document.getElementById('a3d-ltmenu');return m?Array.prototype.map.call(m.querySelectorAll('button'),function(b){return b.textContent;}):null;}")

        async def capture_print(click_sel):
            await safe("""()=>{window.__v122print=[];window.__v122open=window.open;
                window.open=function(){var doc={write:function(h){window.__v122print.push(h);},close:function(){}};return {document:doc,focus:function(){},print:function(){}};};return true;}""")
            await page.click(click_sel)
            await settle(400)
            html = await safe("()=>{window.open=window.__v122open;return window.__v122print.join('');}") or ''
            return html

        await page.goto('file://' + str(HTML))
        for _ in range(80):
            if await safe("()=>!!(window.__a3dOn&&window.__a3dPages&&window.__a3dPresPanel)"):
                break
            await page.wait_for_timeout(100)
        await settle(600)
        await safe(HELP)

        # ------------------------------------------------------------------------------------------
        print('\n-- 1. a model, and three sheets: a plan, an elevation, a schedule on A3')
        m = await safe(SETUP) or {}
        S = m.get('s') or [None, None, None]
        ck(all(S) and m.get('room') and len(m.get('walls') or []) == 4, 'four walls, a room and three sheets (%s)' % S)
        await settle(400)

        # ------------------------------------------------------------------------------------------
        print('\n-- 2. a page is the same page at any size (122a)')
        d = await safe("""async (s)=>{
            var a=window.__a3dPageFresh(s[0],1),b=window.__a3dPageFresh(s[0],2),c=window.__a3dPageFresh(s[2],1),e=window.__a3dPageFresh(s[2],2);
            var ia=await window.__v122.load(a),ib=await window.__v122.load(b);
            return {vp:await window.__v122.diff(a,b,[20/431.8,20/279.4,120/431.8,95/279.4]),
                    sched:await window.__v122.diff(c,e,[20/420,20/297,120/420,92/297]),wa:ia.width,ha:ia.height,wb:ib.width,hb:ib.height};}""", S) or {}
        ck(d.get('wa') == round(431.8 * 3) and d.get('wb') == round(431.8 * 6) and d.get('hb') == round(279.4 * 6),
           'a sheet drawn at twice its pixels is twice the pixels (%s x %s, %s x %s)' % (d.get('wa'), d.get('ha'), d.get('wb'), d.get('hb')))
        ck(d.get('vp') is not None and d['vp'] < 3.5,
           'and reduced it is the same drawing: the plan viewport differs by %.2f of 255 (drawn at 6 px/mm as before, 7.6)' % (d.get('vp') or -1))
        ck(d.get('sched') is not None and d['sched'] < 3.5,
           'and so does the schedule, rows and text the same size on the paper (%.2f)' % (d.get('sched') or -1))
        # the finest line: a pixel of the image, not of the layout
        lw = await safe("""(s)=>{
            var ln=window.__a3dSketch('poly',[[1,1],[5,1],[5,2]]);
            var ly=window.__a3dLayerNew({name:'Fine'});window.__a3dObjSetLayer(ln,ly);window.__a3dLayerSet(ly,'lineweight',0.13);
            window.__a3dOpenSheetView(s[0]);
            window.__a3dPageFresh(s[0],1);var a=window.__a3dLastLook(ln);
            window.__a3dPageFresh(s[0],2);var b=window.__a3dLastLook(ln);
            window.__a3dLayerSet(ly,'lineweight',0.5);window.__a3dPageFresh(s[0],2);var c=window.__a3dLastLook(ln);
            window.__a3dCloseSheetView();
            return {ln:ln,ly:ly,a:a&&a.width,b:b&&b.width,c:c&&c.width};}""", S) or {}
        ck(lw.get('a') == 1 and abs((lw.get('b') or 0) - 0.5) < 1e-9 and abs((lw.get('c') or 0) - 1.5) < 1e-9,
           'a 0.13 mm line is one pixel of the image at either size (%s, %s), and 0.50 mm is its true width (%s)' % (lw.get('a'), lw.get('b'), lw.get('c')))
        # the PNG export: the layout's page at twice its pixels
        await safe("(s)=>window.__a3dOpenSheetView(s)", S[0])
        await settle(300)
        fresh2 = await safe("(s)=>window.__a3dPageFresh(s,2)", S[0]) or ''
        png = b''
        try:
            async with page.expect_download() as dl:
                await page.click('#a3d-sheetpng')
            path = await (await dl.value).path()
            png = pathlib.Path(path).read_bytes()
        except Exception as e:
            print('      (download failed: %s)' % str(e)[:160])
        want = base64.b64decode(fresh2.split(',', 1)[1]) if ',' in fresh2 else b'-'
        ck(png and png == want, 'Export PNG is the sheet as it plots at twice the layout\'s pixels, byte for byte (%d bytes, %d expected)' % (len(png), len(want)))

        # ------------------------------------------------------------------------------------------
        print('\n-- 3. nothing that is not on the page (122a)')
        sel = await safe("""async (p)=>{
            window.__a3dSelectFor([p.room]);
            var url=window.__a3dPageFresh(p.s[0],1),rs=window.__a3dLastRoomStyle(p.room);
            return {st:window.__a3dState().sel,fill:rs&&rs.fill,stroke:rs&&rs.stroke,blue:await window.__v122.near(url,p.blue,30)};}""",
                         {'room': m.get('room'), 's': S, 'blue': BLUE}) or {}
        ck(sel.get('st') == m.get('room') and sel.get('stroke') == '#7fd4c4' and sel.get('blue') == 0,
           'a room selected in the model is drawn unselected on its page, and not one pixel of the page is the selection\'s blue (%s, %s blue)' % (sel.get('stroke'), sel.get('blue')))
        gsel = await safe("""async (p)=>{
            var g=window.__a3dAddGrid([4,-1],[4,7]);window.__a3dSelectFor([]);window.__a3dSelectGrid(g);
            var url=window.__a3dPageFresh(p.s[0],1);
            return {g:g,sel:window.__a3dSelectedGrid?window.__a3dSelectedGrid():null,blue:await window.__v122.near(url,p.blue,30),dark:await window.__v122.dark(url,[20/431.8,20/279.4,120/431.8,90/279.4])};}""",
                          {'s': S, 'blue': BLUE}) or {}
        ck(gsel.get('g') and gsel.get('sel') and gsel.get('blue') == 0, 'a grid selected across the room is drawn unselected on the page (%s blue pixels)' % gsel.get('blue'))
        await safe("()=>{window.__a3dSelectFor([]);return true;}")
        sch = await safe("""async (s)=>{var url=window.__a3dPageFresh(s[2],1);
            return {head:await window.__v122.dark(url,[20/420,20/297,120/420,6/297]),row:await window.__v122.dark(url,[20/420,26/297,120/420,6/297])};}""", S) or {}
        failed = [w for w in warns if 'Viewport composite failed' in w]
        ck(failed == [] and (sch.get('row') or 0) > 20,
           'a schedule on a sheet draws its rows (%s dark pixels in the first row, %s composite failures)' % (sch.get('row'), len(failed)))
        # an unfinished sketch is not on the paper
        await safe("()=>window.__a3dSetPlanView&&window.__a3dSetPlanView()")
        await settle(500)
        await safe("()=>window.__a3dRunCmd('line')")
        await settle(200)
        cvb = await safe("()=>{var r=document.getElementById('a3d-canvas').getBoundingClientRect();return [r.left,r.top,r.width,r.height];}") or [300, 100, 900, 700]
        await page.mouse.click(cvb[0] + cvb[2] * 0.42, cvb[1] + cvb[3] * 0.45)
        await settle(150)
        await page.mouse.move(cvb[0] + cvb[2] * 0.58, cvb[1] + cvb[3] * 0.58, steps=4)
        await settle(200)
        rb = await safe("""async (p)=>{var tool=window.__a3dActiveSketchTool(),pts=window.__a3dSkPts();
            var url=window.__a3dPageFresh(p.s[0],1);
            return {tool:tool,pts:pts?pts.length:0,rubber:await window.__v122.near(url,p.rubber,30),blue:await window.__v122.near(url,p.blue,30)};}""",
                        {'s': S, 'rubber': RUBBER, 'blue': BLUE}) or {}
        ck(rb.get('tool') == 'line' and rb.get('pts') == 1 and rb.get('rubber') == 0 and rb.get('blue') == 0,
           'with a line half drawn, its rubber band is not on the page (%s)' % rb)
        await page.keyboard.press('Escape')
        await settle(150)
        await page.keyboard.press('Escape')
        await settle(200)

        # ------------------------------------------------------------------------------------------
        print('\n-- 4. a sheet is drawn in the appearance it prints in (122b)')
        ap = await safe("""(p)=>{
            window.__a3dSetGraphicsOverride(p.w,'presentation','lineColor','#cc2200');
            window.__a3dSetGraphicsOverride(p.w,'presentation','fill','#ffcc00');
            window.__a3dSetPresentMode(false);window.__a3dPageFresh(p.s[0],1);var t=window.__a3dLastDrawStyle(p.w);
            window.__a3dSetPresentMode(true);window.__a3dPageFresh(p.s[0],1);var q=window.__a3dLastDrawStyle(p.w);
            window.__a3dSetPresentMode(false);
            return {t:t,q:q};}""", {'w': (m.get('walls') or [None])[0], 's': S}) or {}
        tq, qq = ap.get('t') or {}, ap.get('q') or {}
        ck(tq.get('stroke') == 'rgba(0,0,0,0.55)' or tq.get('rStroke') == 'rgba(0,0,0,0.55)',
           'in Technical a wall on a sheet has the technical outline (%s)' % tq)
        ck((qq.get('stroke') or qq.get('rStroke')) == '#cc2200' and (qq.get('fill') or qq.get('rBaseFill')) == '#ffcc00',
           'in Presentation it has its presentation outline and fill, as the vector print has (%s)' % qq)

        # ------------------------------------------------------------------------------------------
        print('\n-- 5. the Pages display (122c)')
        await safe("(s)=>window.__a3dOpenSheetView(s)", S[0])
        await settle(300)
        vis0 = await safe("""()=>{var v=document.getElementById('a3d-sheetview');function on(sel){var e=v.querySelector(sel);return !!(e&&getComputedStyle(e).display!=='none');}
            return {pgnav:on('.a3d-pgnav'),zoom:on('#a3d-pgzoom'),addvp:on('#a3d-sheetaddvp'),print:on('#a3d-sheetprint'),present:on('#a3d-sheetpresent'),single:on('.a3d-sheetwrap')};}""") or {}
        ck(vis0.get('addvp') and vis0.get('print') and vis0.get('single') and not vis0.get('pgnav') and not vis0.get('zoom') and vis0.get('present'),
           'a sheet opens in Layout, as it did: its editing tools shown, the page controls not, Present in both (%s)' % vis0)
        await page.click('[data-shdisp="pages"]')
        p = await pages_drawn()
        vis1 = await safe("""()=>{var v=document.getElementById('a3d-sheetview');function on(sel){var e=v.querySelector(sel);return !!(e&&getComputedStyle(e).display!=='none');}
            return {pgnav:on('.a3d-pgnav'),zoom:on('#a3d-pgzoom'),addvp:on('#a3d-sheetaddvp'),print:on('#a3d-sheetprint'),pgprint:on('#a3d-pgprint'),single:on('.a3d-sheetwrap'),pages:on('#a3d-pageswrap'),
                    lay:document.querySelector('[data-shdisp="layout"]').classList.contains('on'),pg:document.querySelector('[data-shdisp="pages"]').classList.contains('on')};}""") or {}
        ck(p.get('display') == 'pages' and p.get('on') and [x['id'] for x in p.get('pages', [])] == S and p.get('dom') == S,
           'Pages shows every sheet, in the project\'s order, one under the next (%s)' % [x['label'] for x in p.get('pages', [])])
        ck(vis1.get('pgnav') and vis1.get('zoom') and vis1.get('pgprint') and vis1.get('pages') and not vis1.get('addvp') and not vis1.get('print') and not vis1.get('single')
           and vis1.get('pg') and not vis1.get('lay'), 'its bar has the page controls and not the editing tools, and marks Pages (%s)' % vis1)
        k = p.get('pxmm') or 0
        ww = await safe("()=>document.getElementById('a3d-pageswrap').clientWidth") or 0
        ck(abs(k - (ww - 36) / 431.8) < 1e-6 and all(x['cssW'] == round(s_w * k) for x, s_w in zip(p.get('pages', []), [431.8, 431.8, 420])),
           'fit width fits the widest sheet, and every page takes the same scale, the A3 page a little narrower (%.4f px/mm, %s)' % (k, [x['cssW'] for x in p.get('pages', [])]))
        same = await safe("""async (p)=>{var e=p.pages[0],cv=document.querySelector('[data-page="'+e.id+'"] canvas');
            return cv?await window.__v122.diff(cv.toDataURL(),window.__a3dPageFresh(e.id,e.scale),[0,0,1,1]):null;}""", p)
        ck(same is not None and same < 0.05, 'a page is the sheet as it plots, drawn for the screen: a fresh plot at the same scale, to %.4f of 255' % (same if same is not None else -1))
        ck(p.get('view', {}).get('kind') == 'sheet' and p.get('view', {}).get('id') == S[0] and p.get('index') == 0,
           'the view is the page being read: the first (%s)' % p.get('view'))
        # the scroll moves the page being read, and everything that names it follows
        await safe("(p)=>{var w=document.getElementById('a3d-pageswrap'),e=document.querySelector('[data-page=\"'+p+'\"]');w.scrollTop=e.offsetTop-10;return true;}", S[1])
        await settle(500)
        p = await pages()
        tab = await safe("()=>{var t=document.querySelector('#a3d-laytabs .a3d-lt.on');return t?t.getAttribute('data-ltsheet'):null;}")
        hud = await safe("()=>{var e=document.querySelector('#a3d-hud .a3d-hudview,#a3d-view,[data-a3dhud=\"view\"]');return window.__a3dSheetSpace().viewName;}")
        num = await safe("()=>[document.getElementById('a3d-pgnum').value,document.getElementById('a3d-pgof').textContent,document.getElementById('a3d-sheetnum').textContent]")
        ck(p.get('cur') == S[1] and p.get('view', {}).get('id') == S[1] and tab == S[1] and hud == 'A201 - Elevations' and num == ['2', 'of 3', 'A201 - Elevations'],
           'scrolled to the second page, it is the view, its tab is marked, and the bar and HUD name it (%s, %s, %s)' % (p.get('index'), tab, num))
        # the bar's controls
        await page.click('#a3d-pgnext')
        await settle(300)
        p = await pages()
        ck(p.get('cur') == S[2], 'the next-page button turns to page 3 (%s)' % p.get('index'))
        dis = await safe("()=>[document.getElementById('a3d-pgprev').disabled,document.getElementById('a3d-pgnext').disabled]")
        ck(dis == [False, True], 'and on the last page the next-page button is off (%s)' % dis)
        await page.click('#a3d-pgprev')
        await settle(300)
        ck((await pages()).get('cur') == S[1], 'the previous-page button turns back')
        await page.fill('#a3d-pgnum', '3')
        await page.press('#a3d-pgnum', 'Enter')
        await settle(300)
        ck((await pages()).get('cur') == S[2], 'a page number typed and Enter goes to it')
        await page.fill('#a3d-pgnum', '9')
        await page.press('#a3d-pgnum', 'Enter')
        await settle(300)
        pv = await safe("()=>document.getElementById('a3d-pgnum').value")
        ck((await pages()).get('cur') == S[2] and pv == '3', 'a number past the last page goes nowhere, and the box shows the page again (%s)' % pv)
        # the keys, from their table
        p = await pages()
        keys = p.get('keys') or []
        await blur()
        await safe("()=>window.__a3dPagesGo(1)")
        await settle(200)
        got = {}
        for row in keys:
            for key in row['keys']:
                await safe("()=>window.__a3dPagesGo(1)")
                await settle(120)
                top0 = (await pages()).get('scrollTop')
                await page.keyboard.press(key)
                await settle(250)
                q = await pages()
                got[key] = (row['act'], q.get('index'), (q.get('scrollTop') or 0) - (top0 or 0))
        expect = {'next': 2, 'prev': 0, 'first': 0, 'last': 2}
        okk = all((got[k][1] == expect[a]) if a in expect else (got[k][2] > 0 if a == 'down' else got[k][2] < 0) for k, (a, _, _) in got.items())
        ck(keys and okk and len(got) == sum(len(r['keys']) for r in keys),
           'every key in the Pages table does what its row says (%s)' % got)
        hint = p.get('hint') or ''
        ck('Page Down / Right' in hint and 'Page Up / Left' in hint, 'the status bar\'s hint names the keys from the same table (%r)' % hint)
        # zoom
        zres = {}
        for z in p.get('zooms') or []:
            await page.select_option('#a3d-pgzoom', str(z))
            await settle(250)
            q = await pages()
            zres[str(z)] = round(q.get('pxmm') or 0, 4)
        ww = await safe("()=>document.getElementById('a3d-pageswrap').clientWidth") or 0
        wh = await safe("()=>document.getElementById('a3d-pageswrap').clientHeight") or 0
        wantz = {'width': round((ww - 36) / 431.8, 4), 'page': round(min((ww - 36) / 431.8, (wh - 36) / 297), 4),
                 '50': round(0.5 * 96 / 25.4, 4), '75': round(0.75 * 96 / 25.4, 4), '100': round(96 / 25.4, 4),
                 '125': round(1.25 * 96 / 25.4, 4), '150': round(1.5 * 96 / 25.4, 4), '200': round(2 * 96 / 25.4, 4)}
        ck(zres == wantz, 'each zoom is what it says: fit width, fit page, and percentages of the paper\'s own size (%s)' % zres)
        # a short window: the page's height is what fits
        await page.set_viewport_size({'width': 1600, 'height': 640})
        await settle(400)
        await page.select_option('#a3d-pgzoom', 'page')
        await settle(400)
        kp = (await pages()).get('pxmm') or 0
        ww = await safe("()=>document.getElementById('a3d-pageswrap').clientWidth") or 0
        wh = await safe("()=>document.getElementById('a3d-pageswrap').clientHeight") or 0
        ck(abs(kp - (wh - 36) / 297) < 1e-6 and kp < (ww - 36) / 431.8,
           'in a short window fit page fits the tallest page\'s height, less than fit width would (%.4f px/mm)' % kp)
        await page.set_viewport_size({'width': 1600, 'height': 950})
        await settle(400)
        await page.select_option('#a3d-pgzoom', 'width')
        await settle(300)
        # a model change is redrawn on the pages on screen
        before = await safe("(s)=>{var cv=document.querySelector('[data-page=\"'+s+'\"] canvas');return cv?cv.toDataURL():'';}", S[1]) or ''
        lay0 = await safe("(w)=>window.__a3dLayerQ(w).layer", (m.get('walls') or [None])[0])
        await safe("(l)=>window.__a3dLayerSet(l,'visible',false)", lay0)
        await settle(200)
        p2 = await pages_drawn()
        after = await safe("(s)=>{var cv=document.querySelector('[data-page=\"'+s+'\"] canvas');return cv?cv.toDataURL():'';}", S[1]) or ''
        same2 = await safe("async (p)=>{var e=p.pages.filter(function(x){return x.id===p.id;})[0];var cv=document.querySelector('[data-page=\"'+p.id+'\"] canvas');return (e&&cv)?await window.__v122.diff(cv.toDataURL(),window.__a3dPageFresh(p.id,e.scale),[0,0,1,1]):null;}",
                           {'pages': p2.get('pages', []), 'id': S[1]})
        ck(before and after and before != after and same2 is not None and same2 < 0.05,
           'a layer turned off is redrawn on the page on screen, which is again the fresh plot (%s)' % same2)
        await safe("(l)=>window.__a3dLayerSet(l,'visible',true)", lay0)
        await settle(400)
        # a click makes a page current; a double-click opens its layout
        await safe("(s)=>window.__a3dPagesGo(0)", S)
        await settle(300)
        box = await safe("(s)=>{var r=document.querySelector('[data-page=\"'+s+'\"]').getBoundingClientRect();return [r.left,r.top,r.width,r.height];}", S[0])
        await page.mouse.click(box[0] + box[2] * 0.6, box[1] + box[3] * 0.5)
        await settle(200)
        await page.mouse.dblclick(box[0] + box[2] * 0.6, box[1] + box[3] * 0.5)
        await settle(400)
        sp = await safe("()=>window.__a3dSheetSpace()") or {}
        p = await pages()
        ck(p.get('display') == 'layout' and sp.get('onSheet') and sp.get('sheet') == S[0],
           'a double-click on a page opens its layout to edit (%s, %s)' % (p.get('display'), sp.get('sheet')))
        # a page deleted while it is read: the reader stays in the document
        await page.click('[data-shdisp="pages"]')
        await settle(300)
        extra = await safe("()=>window.__a3dAddSheet('A900','Spare','ANSI-B-L')")
        await safe("(s)=>window.__a3dPagesGo(3)", S)
        await settle(300)
        await safe("(s)=>window.__a3dPagesGo(1)", S)
        await settle(300)
        await safe("(s)=>window.__a3dDeleteSheet(s)", S[1])
        await settle(400)
        p = await pages()
        ck(p.get('display') == 'pages' and p.get('on') and p.get('cur') == S[2] and [x['id'] for x in p.get('pages', [])] == [S[0], S[2], extra],
           'deleting the page being read keeps the reader in Pages, on the page that took its place (%s)' % p.get('index'))
        await safe("()=>window.__a3dUndo()")
        await settle(400)
        await safe("(x)=>window.__a3dDeleteSheet(x)", extra)
        await settle(300)
        ck(await order() == S, 'undo puts it back, in its place (%s)' % (await order() == S))

        # ------------------------------------------------------------------------------------------
        print('\n-- 6. Present (122d)')
        await safe("()=>window.__a3dPagesGo(1)")
        await settle(300)
        await page.click('#a3d-sheetpresent')
        await settle(700)
        s = await show()
        ck(s.get('on') and s.get('open') and s.get('idx') == 1 and s.get('fs') and s.get('fsEl'),
           'Present starts on the page being read, full screen (%s)' % {k: s.get(k) for k in ('on', 'idx', 'fs', 'fsEl')})
        vw = await safe("()=>{var o=document.getElementById('a3d-slideshow');return [o.clientWidth,o.clientHeight];}") or [1600, 950]
        jsr = lambda x: int(math.floor(x + 0.5))
        mg = jsr(min(vw) * 0.03)
        kf = min((vw[0] - 2 * mg) / 431.8, (vw[1] - 2 * mg) / 279.4)
        ck(s.get('cssW') == jsr(431.8 * kf) and s.get('cssH') == jsr(279.4 * kf),
           'the page is fitted to the screen with a small margin (%s x %s on %s)' % (s.get('cssW'), s.get('cssH'), vw))
        eqs = await safe("""async ()=>{var o=window.__a3dSlideshow(),cv=document.querySelector('#a3d-slideshow canvas');
            return o.drawnKey.indexOf(o.key)===0?await window.__v122.diff(cv.toDataURL(),window.__a3dPageFresh(o.id,o.scale),[0,0,1,1]):null;}""")
        ck(eqs is not None and eqs < 0.05, 'the page shown is the sheet as it plots, drawn for the screen (%s of 255 from a fresh plot)' % eqs)
        ck('Right, Down, Page Down, Space or a click' in (s.get('hint') or '') and 'Esc to end' in (s.get('hint') or ''),
           'the hint on screen names the keys from Present\'s table (%r)' % s.get('hint'))
        keys = s.get('keys') or []
        res = {}
        for row in keys:
            if row['act'] == 'end':
                continue
            for key in row['keys']:
                # on the middle page, put there with the bar
                cur = (await show()).get('idx')
                while cur is not None and cur != 1:
                    await page.click('#a3d-slideshow [data-ssact="%s"]' % ('prev' if cur > 1 else 'next'))
                    await settle(120)
                    cur = (await show()).get('idx')
                await page.keyboard.press(key)
                await settle(200)
                res[key] = (row['act'], (await show()).get('idx'))
        want = {'next': 2, 'prev': 0, 'first': 0, 'last': 2}
        ck(keys and all(v[1] == want[v[0]] for v in res.values()) and len(res) == sum(len(r['keys']) for r in keys if r['act'] != 'end'),
           'every key in Present\'s table does what its row says (%s)' % res)
        # the mouse: a click, the wheel, the bar
        cur = (await show()).get('idx')
        while cur != 0:
            await page.click('#a3d-slideshow [data-ssact="prev"]')
            await settle(120)
            cur = (await show()).get('idx')
        bar0 = await safe("()=>[document.querySelector('#a3d-slideshow [data-ssact=\"prev\"]').disabled,document.querySelector('#a3d-slideshow .a3d-sspos').textContent]")
        ck(bar0 == [True, '1 / 3'], 'the bar says 1 / 3 and its back button is off on the first page (%s)' % bar0)
        await page.mouse.click(vw[0] / 2, vw[1] / 2)
        await settle(250)
        ck((await show()).get('idx') == 1, 'a click on the page is the next page')
        await page.click('#a3d-slideshow [data-ssact="next"]')
        await settle(250)
        bar2 = await safe("()=>[document.querySelector('#a3d-slideshow [data-ssact=\"next\"]').disabled,document.querySelector('#a3d-slideshow .a3d-sspos').textContent]")
        ck((await show()).get('idx') == 2 and bar2 == [True, '3 / 3'], 'the bar\'s next button turns the page, and is off on the last (%s)' % bar2)
        await page.mouse.move(vw[0] / 2 + 5, vw[1] / 2 + 5)
        await settle(200)
        idle0 = (await show()).get('idle')
        await settle(2800)
        idle1 = (await show()).get('idle')
        await page.mouse.move(vw[0] / 2 + 40, vw[1] / 2 + 30)
        await settle(200)
        idle2 = (await show()).get('idle')
        ck(idle0 is False and idle1 is True and idle2 is False, 'the bar and the cursor go when the mouse rests and come back when it moves (%s, %s, %s)' % (idle0, idle1, idle2))
        await page.keyboard.press('Home')
        await settle(400)
        s = await show()
        ck(s.get('ahead') == S[1], 'the next page is drawn ahead while this one is on screen (%s)' % s.get('ahead'))
        await page.keyboard.press('End')
        await settle(250)
        await page.click('#a3d-slideshow [data-ssact="end"]')
        await settle(500)
        s = await show()
        p = await pages()
        ck(not s.get('on') and not s.get('open') and not s.get('fsEl') and p.get('display') == 'pages' and p.get('cur') == S[2],
           'End ends it, leaves full screen, and the reader is on the page last shown (%s)' % p.get('index'))
        # Escape, from the layout
        await page.click('[data-shdisp="layout"]')
        await settle(300)
        await page.click('#a3d-sheetpresent')
        await settle(600)
        await page.keyboard.press('Home')
        await settle(200)
        await page.keyboard.press('Escape')
        await settle(500)
        s = await show()
        sp = await safe("()=>window.__a3dSheetSpace()") or {}
        ck(not s.get('on') and not s.get('fsEl') and sp.get('sheet') == S[0] and (await pages()).get('display') == 'layout',
           'Escape ends it, and from the layout, the layout of the page last shown is open (%s)' % sp.get('sheet'))
        # the browser leaving full screen by itself ends it too
        await page.click('#a3d-sheetpresent')
        await settle(600)
        await safe("()=>document.exitFullscreen()")
        await settle(500)
        ck(not (await show()).get('on'), 'the browser leaving full screen on its own ends the presentation')
        # refused full screen: the browser is made to say no, as one set against it does
        await safe("()=>{HTMLElement.prototype.requestFullscreen=function(){return Promise.reject(new TypeError('not allowed, for this suite'));};return true;}")
        await page.click('#a3d-sheetpresent')
        await settle(500)
        s = await show()
        cover = await safe("()=>{var r=document.getElementById('a3d-slideshow').getBoundingClientRect();return [r.left,r.top,r.width,r.height,window.innerWidth,window.innerHeight];}") or []
        ck(s.get('on') and s.get('open') and not s.get('fs') and not s.get('fsEl') and 'fill the window' in (s.get('hint') or '')
           and cover[:4] == [0, 0, cover[4], cover[5]],
           'where full screen is refused the pages fill the window, and the presentation says so on screen (%r)' % (s.get('hint') or '')[:70])
        # the wheel (headless Chromium delivers no wheel to a full-screen element; in the window it does)
        await page.keyboard.press('Home')
        await settle(200)
        await page.mouse.move(vw[0] / 2, vw[1] / 2)
        await page.mouse.wheel(0, 120)
        await settle(450)
        ck((await show()).get('idx') == 1, 'the wheel turned towards the reader is the next page')
        await page.mouse.wheel(0, -120)
        await settle(450)
        ck((await show()).get('idx') == 0, 'and away, the one before')
        await page.mouse.wheel(0, 120)
        await page.mouse.wheel(0, 120)
        await page.mouse.wheel(0, 120)
        await settle(450)
        ck((await show()).get('idx') == 1, 'one page for one turn of the wheel, however many notches it sends at once')
        await page.keyboard.press('Escape')
        await settle(400)
        await safe("()=>window.__a3dCloseSheetView()")
        await settle(300)
        r0 = await safe("(s)=>window.__a3dSlideshowStart(s)", S[0])
        await settle(500)
        # every key is the presentation's: with a wall selected in the model behind it, Delete and
        # Undo do nothing to the model
        wall0 = (m.get('walls') or [None])[0]
        await safe("(w)=>{window.__a3dSelectFor([w]);return true;}", wall0)
        n_objs = await safe("()=>window.__a3dObjects().length")
        for key in ('Delete', 'z', 'Control+z', 'Meta+z'):
            await page.keyboard.press(key)
            await settle(150)
        s = await show()
        still = await safe("(w)=>window.__a3dObjects().some(function(o){return o.id===w;})", wall0)
        ck(s.get('on') and await safe("()=>window.__a3dObjects().length") == n_objs and still and len(await order()) == 3,
           'keys not in the table reach nothing: a selected wall is not deleted and nothing is undone while it runs')
        await page.keyboard.press('Escape')
        await settle(400)
        await safe("()=>{window.__a3dSelectFor([]);return true;}")
        sp = await safe("()=>window.__a3dSheetSpace()") or {}
        ck(r0 and not (await show()).get('on') and not sp.get('onSheet'), 'started from the model, it leaves the model on screen when it ends')
        await safe("()=>{delete HTMLElement.prototype.requestFullscreen;return true;}")

        # ------------------------------------------------------------------------------------------
        print('\n-- 7. the printed set (122e)')
        await safe("(s)=>window.__a3dOpenSheetView(s)", S[0])
        await settle(300)
        await page.click('[data-shdisp="pages"]')
        await settle(400)
        html = await capture_print('#a3d-pgprint')
        ids = re.findall(r'<div class="a3dpg" data-page="([^"]+)" style="page:([a-z0-9_]+);width:([0-9.]+)mm;height:([0-9.]+)mm">\s*<svg', html)
        rules = dict(re.findall(r'@page ([a-z0-9_]+)\{size:([0-9.]+mm [0-9.]+mm);margin:0\}', html))
        first = re.search(r'@page\{size:([0-9.]+mm [0-9.]+mm);margin:0\}', html)
        ck([x[0] for x in ids] == S, 'Print set sends every page, in order, each the vector sheet (%d pages)' % len(ids))
        ck(len(rules) == 2 and all(rules.get(x[1]) == '%smm %smm' % (x[2], x[3]) for x in ids) and first and first.group(1) == '431.8mm 279.4mm',
           'each on paper of its own size -- the A3 page on A3 -- and the first size is the plain page size (%s)' % rules)
        ck(html.count('<svg') == 3 and 'window.print()' in html, 'three drawings, and the print dialog opened on load')

        # ------------------------------------------------------------------------------------------
        print('\n-- 8. the Presentation panel (122f)')
        await safe("()=>window.__a3dCloseSheetView()")
        await settle(300)
        await page.click('.a3d-railbtn[data-tab="presentation"]')
        pn = await thumbs_drawn()
        ck(pn.get('open') and [i['id'] for i in pn.get('items', [])] == S and [i['no'] for i in pn.get('items', [])] == ['1', '2', '3']
           and pn.get('head') == '3 pages', 'the panel lists the pages in order, numbered, with a count (%s)' % [i['name'] for i in pn.get('items', [])])
        ck(all(i['drawn'] for i in pn.get('items', [])) and all(abs(i['h'] / max(1, i['w']) - h / w) < 0.01 for i, (w, h) in zip(pn.get('items', []), [(431.8, 279.4), (431.8, 279.4), (420, 297)])),
           'each with its thumbnail drawn, the shape of its paper (%s)' % [(i['w'], i['h']) for i in pn.get('items', [])])
        th = await safe("""async (s)=>{var cv=document.querySelector('canvas[data-prpthumb="'+s+'"]');
            return await window.__v122.diff(cv.toDataURL(),window.__a3dPageFresh(s,1),[20/431.8,20/279.4,120/431.8,90/279.4]);}""", S[0])
        ck(th is not None and th < 10, 'a thumbnail is the page as it plots, reduced: %.2f of 255 from the plot (a blank one is 33)' % (th if th is not None else -1))
        cur = [i['cur'] for i in pn.get('items', [])]
        ck(cur == [False, False, False], 'with the model on screen no page is marked as the one being read')
        # a click reads a page
        await page.click('[data-prpitem="%s"]' % S[2])
        await settle(700)
        p = await pages()
        pn = await panel()
        ck(p.get('display') == 'pages' and p.get('on') and p.get('cur') == S[2] and [i['cur'] for i in pn.get('items', [])] == [False, False, True],
           'a click on a page opens Pages on it, and the panel marks it (%s)' % p.get('index'))
        await page.click('[data-prpitem="%s"]' % S[0])
        await settle(500)
        ck((await pages()).get('cur') == S[0] and (await pages()).get('scrollTop') == 0, 'another click, with Pages open, goes to that page')
        # a double-click edits its layout
        await page.dblclick('[data-prpitem="%s"] canvas' % S[1])
        await settle(500)
        sp = await safe("()=>window.__a3dSheetSpace()") or {}
        ck((await pages()).get('display') == 'layout' and sp.get('sheet') == S[1], 'a double-click on a thumbnail opens that page\'s layout (%s)' % sp.get('sheet'))
        # rename
        await page.dblclick('[data-prpname="%s"]' % S[1])
        await settle(250)
        focused = await safe("()=>document.activeElement&&document.activeElement.getAttribute('data-prpren')")
        await page.keyboard.press('Control+a')
        await page.keyboard.type('Elevations and Sections')
        await page.keyboard.press('Enter')
        await settle(400)
        nm = await safe("(s)=>window.__a3dSheets().filter(function(x){return x.id===s;})[0].name", S[1])
        tabtxt = await safe("(s)=>document.querySelector('#a3d-laytabs [data-ltsheet=\"'+s+'\"]').textContent", S[1])
        ck(focused == S[1] and nm == 'Elevations and Sections' and tabtxt == 'A201 - Elevations and Sections',
           'a double-click on a page\'s name renames the sheet, and its tab follows (%s, %s)' % (nm, tabtxt))
        await page.dblclick('[data-prpname="%s"]' % S[1])
        await settle(250)
        await page.keyboard.type('xyz')
        await page.keyboard.press('Escape')
        await settle(300)
        nm2 = await safe("(s)=>window.__a3dSheets().filter(function(x){return x.id===s;})[0].name", S[1])
        ck(nm2 == 'Elevations and Sections' and (await safe("()=>window.__a3dSheetSpace().onSheet")),
           'Escape cancels a rename and nothing else (%s)' % nm2)
        await safe("()=>window.__a3dUndo()")
        await settle(300)
        nm3 = await safe("(s)=>window.__a3dSheets().filter(function(x){return x.id===s;})[0].name", S[1])
        ck(nm3 == 'Elevations', 'a rename is one undo step (%s)' % nm3)
        # the menu, and moving pages
        await page.click('[data-prpitem="%s"]' % S[1], button='right')
        await settle(250)
        it = await menu_items()
        ck(it == ['Present from this page', 'New sheet', 'Rename', 'Delete', 'Move up', 'Move down', 'Sheet setup…', 'Plot…'],
           'a page\'s menu: Present from it, and the layout tab\'s own items with the move (%s)' % it)
        await page.click('#a3d-ltmenu [data-ltm="later"]')
        await settle(400)
        o1 = await order()
        tabs = await safe("()=>Array.prototype.map.call(document.querySelectorAll('#a3d-laytabs [data-ltsheet]'),function(b){return b.getAttribute('data-ltsheet');})")
        pn = await panel()
        ck(o1 == [S[0], S[2], S[1]] and tabs == o1 and [i['id'] for i in pn.get('items', [])] == o1 and [i['no'] for i in pn.get('items', [])] == ['1', '2', '3'],
           'Move down moves the sheet in the one order: the layout tabs and the panel follow (%s)' % [x[-6:] for x in o1])
        await safe("()=>window.__a3dUndo()")
        await settle(400)
        ck(await order() == S, 'a move is one undo step')
        await page.click('[data-prpitem="%s"]' % S[0], button='right')
        await settle(250)
        it0 = await menu_items()
        await page.keyboard.press('Escape')
        await safe("()=>{var m=document.getElementById('a3d-ltmenu');if(m)m.remove();return true;}")
        ck(it0 and 'Move up' not in it0 and 'Move down' in it0, 'the first page cannot move up (%s)' % it0)
        # the layout tab reads the same menu
        await page.click('#a3d-laytabs [data-ltsheet="%s"]' % S[1], button='right')
        await settle(250)
        itt = await menu_items()
        ck(itt == ['New sheet', 'Rename', 'Delete', 'Move left', 'Move right', 'Sheet setup…', 'Plot…'],
           'the layout tab\'s menu is the same list, left and right for a row of tabs (%s)' % itt)
        await page.click('#a3d-ltmenu [data-ltm="earlier"]')
        await settle(400)
        ck(await order() == [S[1], S[0], S[2]], 'and Move left moves it')
        await safe("()=>window.__a3dUndo()")
        await settle(400)
        # drag a page to a new place
        await page.drag_and_drop('[data-prpitem="%s"]' % S[2], '[data-prpitem="%s"]' % S[0], target_position={'x': 60, 'y': 8})
        await settle(500)
        o2 = await order()
        ck(o2 == [S[2], S[0], S[1]], 'a page dragged above the first becomes the first (%s)' % [x[-6:] for x in o2])
        await page.drag_and_drop('[data-prpitem="%s"]' % S[2], '[data-prpitem="%s"]' % S[1], target_position={'x': 60, 'y': 150})
        await settle(500)
        o3 = await order()
        ck(o3 == S, 'and dragged below the last, the last (%s)' % [x[-6:] for x in o3])
        await page.click('[data-prpitem="%s"]' % S[0])
        await settle(500)
        await safe("(s)=>window.__a3dSheetMove(s[2],0)", S)
        await settle(500)
        p = await pages()
        ck(p.get('dom') == [S[2], S[0], S[1]], 'the pages follow the order, on screen as in the model (%s)' % [x[-6:] for x in p.get('dom') or []])
        await safe("()=>window.__a3dUndo()")
        await settle(500)
        # Present and + Page and Print set, from the panel
        await page.click('[data-prpitem="%s"]' % S[1])
        await settle(400)
        await page.click('[data-prpact="present"]')
        await settle(600)
        s = await show()
        ck(s.get('on') and s.get('idx') == 1, 'Present in the panel starts on the page being read (%s)' % s.get('idx'))
        await page.keyboard.press('Escape')
        await settle(400)
        await safe("()=>window.__a3dCloseSheetView()")
        await settle(300)
        await page.click('[data-prpact="present"]')
        await settle(600)
        s = await show()
        ck(s.get('on') and s.get('idx') == 0, 'and with the model on screen, on the first page (%s)' % s.get('idx'))
        await page.keyboard.press('Escape')
        await settle(400)
        await page.click('[data-prpitem="%s"]' % S[2], button='right')
        await settle(250)
        await page.click('#a3d-ltmenu [data-ltm="present"]')
        await settle(600)
        ck((await show()).get('idx') == 2, 'Present from this page, in a page\'s menu, starts there')
        await page.keyboard.press('Escape')
        await settle(400)
        html = await capture_print('[data-prpact="print"]')
        ck(re.findall(r'<div class="a3dpg" data-page="([^"]+)"', html) == S, 'Print set in the panel prints the set in order')
        await page.click('[data-prpact="new"]')
        await settle(700)
        o4 = await order()
        pn = await thumbs_drawn()
        sp = await safe("()=>window.__a3dSheetSpace()") or {}
        ck(len(o4) == 4 and o4[:3] == S and pn.get('head') == '4 pages' and [i['id'] for i in pn.get('items', [])] == o4 and sp.get('sheet') == o4[3],
           '+ Page adds a sheet as the last page and opens it (%s)' % pn.get('head'))
        await safe("(x)=>window.__a3dDeleteSheet(x)", o4[3])
        await settle(400)
        # a model change redraws the thumbnails
        k0 = await safe("()=>window.__a3dPresPanel().items.map(function(i){return i.drawn;})")
        await safe("(w)=>window.__a3dSetGraphicsOverride(w,'technical','fill','#aa0000')", (m.get('walls') or [None])[0])
        await safe("()=>window.__a3dSetPresentMode(true)")
        await settle(100)
        k1 = await safe("()=>window.__a3dPresPanel().items.map(function(i){return i.drawn;})")
        pn = await thumbs_drawn()
        await safe("()=>window.__a3dSetPresentMode(false)")
        ck(k0 == [True, True, True] and k1 == [False, False, False] and all(i['drawn'] for i in pn.get('items', [])),
           'the appearance changed, the thumbnails are out of date and are drawn again (%s, %s)' % (k1, [i['drawn'] for i in pn.get('items', [])]))
        audit = await safe("()=>window.__a3dShellAudit?window.__a3dShellAudit():null")
        if audit is None:
            audit = await safe("()=>{try{return bimShellAudit();}catch(e){return null;}}")
        ck(audit and audit.get('ok'), 'every control in the panel is claimed by the shell audit (%s)' % (audit and audit.get('unclaimed')))
        # the empty set
        await safe("()=>{window.__a3dSheets().forEach(function(s){window.__a3dDeleteSheet(s.id);});return true;}")
        await settle(500)
        em = await safe("""()=>{var h=document.querySelector('#a3d-leftpanel .a3d-pres-wrap');
            return {empty:!!h.querySelector('.a3d-prpempty'),present:h.querySelector('[data-prpact="present"]').disabled,print:h.querySelector('[data-prpact="print"]').disabled,
                    title:h.querySelector('[data-prpact="present"]').title,head:h.querySelector('.a3d-prpcount').textContent};}""") or {}
        ck(em.get('empty') and em.get('present') and em.get('print') and em.get('title') == 'No pages to present yet' and em.get('head') == '0 pages',
           'with no sheets the panel says how to make a page, and Present and Print set are off and say why (%s)' % em)
        for _ in range(3):
            await safe("()=>window.__a3dUndo()")
            await settle(250)
        ck(await order() == S, 'undone, the three pages are back in order')

        # ------------------------------------------------------------------------------------------
        print('\n-- 9. the shortcut sheet, and the order kept')
        reg = await safe("()=>window.__a3dShortcuts()") or []
        grp = {g['grp']: [r['label'] for r in g['rows']] for g in reg}
        tbl_p = [r['label'] for r in (await pages()).get('keys', [])]
        tbl_s = [r['label'] for r in (await show()).get('keys', [])]
        ck(grp.get('Pages') == tbl_p and grp.get('Presenting') == tbl_s and tbl_p and tbl_s,
           'the shortcut sheet\'s Pages and Presenting groups are the handlers\' own tables (%s)' % list(grp))
        alt = await safe("""()=>{var b=document.querySelector('[data-a3drumenu="help"]');b.click();
            var rows=[].slice.call(document.querySelectorAll('#a3d-rupop .a3d-rkrow'));
            var r=rows.filter(function(x){return x.querySelector('.a3d-rklab').textContent==='Next page';})[0];
            var out=r?[].map.call(r.querySelectorAll('.a3d-rkplus'),function(e){return e.textContent;}):null;b.click();return out;}""")
        ck(alt and all(x == '/' for x in alt), 'and a row of alternatives is written with a slash, not a chord\'s plus (%s)' % alt)
        await settle(700)
        await safe("(s)=>window.__a3dSheetMove(s[2],0)", S)
        await settle(700)
        # read from storage, not after a reload: the page's pagehide flush saves the model whenever a
        # save was ever scheduled (saveT is not cleared when it fires), which would hide a missing one
        stored = await safe("()=>{var v=JSON.parse(localStorage.getItem('acad3dV1')||'{}');return (v.sheets||[]).map(function(s){return s.id;});}")
        ck(stored == [S[2], S[0], S[1]], 'a move is saved by its own save, as every change is (%s)' % [x[-6:] for x in stored or []])
        await page.reload()
        for _ in range(80):
            if await safe("()=>!!(window.__a3dOn&&window.__a3dSheets)"):
                break
            await page.wait_for_timeout(100)
        await settle(600)
        ck(await order() == [S[2], S[0], S[1]], 'the order is the project\'s: it is saved, and a reload keeps it')

        print('\n-- 10. errors')
        ck(errs == [], 'no page errors (%s)' % errs[:3])
        bad = [w for w in warns if ('could not' in w or 'failed' in w) and 'Full screen was not granted' not in w]
        ck(bad == [], 'no [BIM] warning of a failure, but the refused full screen this suite asked for (%s)' % bad[:3])
        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
