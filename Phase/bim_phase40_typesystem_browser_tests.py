from playwright.sync_api import sync_playwright
errs=[]
with sync_playwright() as p:
    b=p.chromium.launch(args=['--use-gl=swiftshader','--enable-unsafe-swiftshader'])
    pg=b.new_page(viewport={'width':1500,'height':950})
    pg.on('pageerror', lambda e: errs.append(str(e)[:250]))
    pg.goto('file:///home/claude/canvas_v10.html'); pg.wait_for_timeout(1800)
    def js(e):
        try: return pg.evaluate(e)
        except Exception as ex: return "THREW "+str(ex)[:250]
    js("document.querySelector('.acad-ws').click()"); pg.wait_for_timeout(250)
    js("(()=>{var i=document.querySelector('[data-wsm=\"3d\"]');if(i)i.click();})()"); pg.wait_for_timeout(1500)
    box=pg.evaluate("(()=>{var c=document.querySelector('#a3d-canvas');var r=c.getBoundingClientRect();return{x:r.x,y:r.y,w:r.width,h:r.height};})()")
    cx,cy=box['x']+box['w']/2, box['y']+box['h']/2
    def okdlg(): js("(()=>{var d=document.querySelector('.a3d-dlg');if(d){var o=d.querySelector('[data-a3dlg=ok]');if(o)o.click();}})()")
    # two walls of the same type
    for off in [(-200,-110,200,-110),(-200,110,200,110)]:
        js("(()=>{var b=document.querySelector('[data-a3dr=\"bim:wall\"]');if(b)b.click();})()"); pg.wait_for_timeout(280)
        pg.mouse.click(cx+off[0],cy+off[1]); pg.wait_for_timeout(130)
        pg.mouse.click(cx+off[2],cy+off[3]); pg.wait_for_timeout(130)
        pg.keyboard.press('Enter'); pg.wait_for_timeout(300); okdlg(); pg.wait_for_timeout(700)
    print("walls created:", js("document.querySelectorAll('#a3d-browser [data-a3did]').length"))
    print("both share one typeId:", js("""(()=>{var st=JSON.parse(localStorage.getItem('acad3dV1')||'{}');
      var ws=(st.objs||[]).filter(o=>o.bim&&o.bim.type==='wall');
      return ws.length+' walls, typeIds='+JSON.stringify(ws.map(w=>w.bim.typeId));})()"""))
    print("type categories available:", js("Object.keys(window.__a3dTypeCats()).join(', ')"))
    print("default types per category:", js("""(()=>{var st=JSON.parse(localStorage.getItem('acad3dV1')||'{}');
      var t=st.types||{};var o={};for(var k in t)o[k]=t[k].length;return JSON.stringify(o);})()"""))
    # open Edit Type and change the shared thickness
    js("(()=>{var r=document.querySelector('#a3d-browser [data-a3did]');if(r)r.click();})()"); pg.wait_for_timeout(500)
    js("(()=>{var b=document.querySelector('[data-propf=\"edittype\"]');if(b)b.click();})()"); pg.wait_for_timeout(600)
    print("Edit Type dialog opened:", js("!!document.querySelector('.a3d-dlg')"))
    print("  header:", js("(document.querySelector('.a3d-dlghd')||{}).textContent"))
    print("  type list:", js("Array.from(document.querySelectorAll('[data-typesel] option')).map(e=>e.textContent).join(' | ')"))
    js("""(()=>{var i=document.querySelector('[data-typep="thickness"]');if(i)i.value='0.6';})()""")
    okdlg(); pg.wait_for_timeout(1100)
    print("  toast:", js("(document.querySelector('#a3d-toast')||{}).textContent"))
    print("BOTH walls updated to the new shared thickness:", js("""(()=>{var st=JSON.parse(localStorage.getItem('acad3dV1')||'{}');
      var ws=(st.objs||[]).filter(o=>o.bim&&o.bim.type==='wall');
      return JSON.stringify(ws.map(w=>w.bim.thickness));})()"""))
    print("errors:", errs if errs else "none")
    pg.screenshot(path='/home/claude/typedlg.png')
    b.close()
