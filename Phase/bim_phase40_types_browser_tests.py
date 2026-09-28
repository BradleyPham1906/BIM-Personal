from playwright.sync_api import sync_playwright
errs=[]
with sync_playwright() as p:
    b=p.chromium.launch(args=['--use-gl=swiftshader','--enable-unsafe-swiftshader'])
    pg=b.new_page(viewport={'width':1500,'height':950})
    pg.on('pageerror', lambda e: errs.append(str(e)[:250]))
    pg.goto('file:///home/claude/canvas_v10.html'); pg.wait_for_timeout(1800)
    def js(e):
        try: return pg.evaluate(e)
        except Exception as ex: return "THREW "+str(ex)[:200]
    js("document.querySelector('.acad-ws').click()"); pg.wait_for_timeout(250)
    js("(()=>{var i=document.querySelector('[data-wsm=\"3d\"]');if(i)i.click();})()"); pg.wait_for_timeout(1500)
    box=pg.evaluate("(()=>{var c=document.querySelector('#a3d-canvas');var r=c.getBoundingClientRect();return{x:r.x,y:r.y,w:r.width,h:r.height};})()")
    cx,cy=box['x']+box['w']/2, box['y']+box['h']/2
    def wall(pts):
        js("(()=>{var b=document.querySelector('[data-a3dr=\"bim:wall\"]');if(b)b.click();})()"); pg.wait_for_timeout(250)
        for (x,y) in pts: pg.mouse.click(x,y); pg.wait_for_timeout(130)
        pg.keyboard.press('Enter'); pg.wait_for_timeout(300)
        js("(()=>{var d=document.querySelector('.a3d-dlg');if(d)d.querySelector('[data-a3dlg=ok]').click();})()")
        pg.wait_for_timeout(700)
    print("default wall types:", js("window.__a3dWallTypes().map(t=>t.name).join(' | ')"))
    wall([(cx-250,cy-100),(cx+250,cy-100)])
    wall([(cx-250,cy+40),(cx+250,cy+40)])
    print("walls created:", js("document.querySelectorAll('#a3d-browser [data-a3did]').length"))
    print("both on the same type:", js("""(()=>{var st=JSON.parse(localStorage.getItem('acad3dV1')||'{}');
      var ws=(st.objs||[]).filter(o=>o.bim&&o.bim.type==='wall');
      return ws.map(w=>w.bim.typeId).join(',');})()"""))
    print("thickness before:", js("""(()=>{var st=JSON.parse(localStorage.getItem('acad3dV1')||'{}');
      return (st.objs||[]).filter(o=>o.bim&&o.bim.type==='wall').map(w=>w.bim.thickness).join(', ');})()"""))
    print()
    print("=== THE key test: edit the TYPE, both walls must change ===")
    r=js("""(()=>{
      var types=window.__a3dWallTypes();
      var t=types[0];
      t.params.thickness=0.55;
      var res=window.__a3dApplyWallType(t.id);
      return JSON.stringify(res);
    })()""")
    pg.wait_for_timeout(700)
    print("  propagation result:", r)
    print("  thickness after:", js("""(()=>{var out=[];
      document.querySelectorAll('#a3d-browser [data-a3did]');
      return window.__a3dWallTypes()[0].params.thickness;})()"""), "(type value)")
    print("  LIVE instance thicknesses:", js("JSON.stringify(window.__a3dLiveWalls().map(w=>w.thickness))"))
    print("  each wall still knows its type:", js("JSON.stringify(window.__a3dLiveWalls().map(w=>w.typeId))"))
    print()
    print("=== instance params stay independent ===")
    print("  LIVE heights (instance param, unchanged by type edit):", js("JSON.stringify(window.__a3dLiveWalls().map(w=>w.height))"))
    print()
    print("=== Properties shows the type and Edit Type opens ===")
    js("(()=>{var r=document.querySelector('#a3d-browser [data-a3did]');if(r)r.click();})()")
    pg.wait_for_timeout(500)
    print("  type line:", js("(document.querySelector('.a3d-ptypesub')||{}).textContent"))
    print("  Type dropdown in Properties:", js("!!document.querySelector('[data-propf=\"walltype\"]')"))
    js("(()=>{var b=document.querySelector('.a3d-pedit');if(b)b.click();})()")
    pg.wait_for_timeout(500)
    print("  Edit Type dialog opened:", js("!!document.querySelector('.a3d-dlg')"))
    print("  dialog says how many walls use the type:", js("(document.querySelector('#a3d-typecount')||{}).textContent"))
    js("(()=>{var d=document.querySelector('.a3d-dlg');if(d)d.querySelector('[data-a3dlg=cancel]').click();})()")
    pg.wait_for_timeout(300)
    print()
    print("errors:", errs if errs else "none")
    pg.screenshot(path='/home/claude/types.png')
    b.close()
