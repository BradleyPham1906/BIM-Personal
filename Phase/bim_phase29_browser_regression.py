from playwright.sync_api import sync_playwright
errs=[]
with sync_playwright() as p:
    b=p.chromium.launch(args=['--use-gl=swiftshader','--enable-unsafe-swiftshader'])
    pg=b.new_page(viewport={'width':1600,'height':1000})
    pg.on('pageerror', lambda e: errs.append(str(e)[:250]))
    pg.goto('file:///home/claude/canvas_v10.html'); pg.wait_for_timeout(1500)
    pg.evaluate("window.__a3dEnter()"); pg.wait_for_timeout(1000)
    def js(e):
        try: return pg.evaluate(e)
        except Exception as ex: return "THREW "+str(ex)[:200]
    def tool(l):
        return js(f"""(()=>{{var w=Array.from(document.querySelectorAll('#acad-panels [data-a3dr]')).filter(e=>e.textContent.trim()==={l!r})[0];
          if(!w)return 'NF'; w.click(); return 'ok';}})()""")
    def okdlg(): js("(()=>{var d=document.querySelector('.a3d-dlg');if(d){var o=d.querySelector('[data-a3dlg=ok]');if(o)o.click();}})()")
    box=pg.evaluate("(()=>{var c=document.querySelector('#a3d-canvas');var r=c.getBoundingClientRect();return{x:r.x,y:r.y,w:r.width,h:r.height};})()")
    cx,cy=box['x']+box['w']/2, box['y']+box['h']/2
    R={}
    tool('Wall'); pg.wait_for_timeout(250)
    for (x,y) in [(cx-200,cy-120),(cx+200,cy-120),(cx+200,cy+120),(cx-200,cy+120)]:
        pg.mouse.click(x,y); pg.wait_for_timeout(130)
    pg.keyboard.press('c'); pg.wait_for_timeout(350); okdlg(); pg.wait_for_timeout(800)
    R['wall']=js("document.querySelectorAll('#a3d-rows .a3d-row').length")
    tool('Room'); pg.wait_for_timeout(220); pg.mouse.click(cx,cy); pg.wait_for_timeout(700)
    tool('Floor'); pg.wait_for_timeout(220); pg.mouse.click(cx,cy); pg.wait_for_timeout(350); okdlg(); pg.wait_for_timeout(700)
    tool('Ceiling'); pg.wait_for_timeout(220); pg.mouse.click(cx,cy); pg.wait_for_timeout(350); okdlg(); pg.wait_for_timeout(700)
    R['objs']=js("Array.from(document.querySelectorAll('#a3d-rows .a3d-row')).map(e=>e.querySelector('.a3d-nm').textContent).join(', ')")
    tool('Dimension'); pg.wait_for_timeout(220)
    for (x,y) in [(cx-200,cy-120),(cx+200,cy-120),(cx,cy-180)]:
        pg.mouse.click(x,y); pg.wait_for_timeout(180)
    pg.wait_for_timeout(400)
    R['dims']=js("document.querySelectorAll('#a3d-rows .a3d-row').length")
    # click-select a solid: exercises on-demand pick poly build
    js("(()=>{var t=Array.from(document.querySelectorAll('#acad-panels [data-a3dr]')).filter(e=>e.textContent.trim()==='Deselect')[0];if(t)t.click();})()")
    pg.wait_for_timeout(200); pg.mouse.click(cx-200,cy-120); pg.wait_for_timeout(400)
    R['pick']=js("(()=>{var r=document.querySelector('#a3d-rows .a3d-row.sel');return r?r.querySelector('.a3d-nm').textContent:'NONE';})()")
    # 3D orbit (perspective mode) still renders
    js("(()=>{var t=Array.from(document.querySelectorAll('#acad-panels [data-a3dr]')).filter(e=>e.textContent.trim()==='Iso')[0];if(t)t.click();})()")
    pg.wait_for_timeout(700)
    R['iso_faces']=js("window.__a3dGlFaces()")
    R['dxf']=js("(()=>{var r=window.__a3dBuildDXF();return 'poly='+r.stats.lwpolyline;})()")
    js("(()=>{var t=Array.from(document.querySelectorAll('.a3d-treetab')).filter(e=>e.textContent.trim()==='Sched')[0];if(t)t.click();})()")
    pg.wait_for_timeout(400)
    R['sched']=js("(document.querySelector('#a3d-schedbody')||{}).textContent.slice(0,60)")
    pg.keyboard.press('Control+z'); pg.wait_for_timeout(500)
    R['undo_ok']=js("document.querySelectorAll('#a3d-rows .a3d-row').length")
    for k,v in R.items(): print(f"  {k}: {v}")
    print("  ERRORS:", errs if errs else "none")
    pg.screenshot(path='/home/claude/gl_regress.png')
    b.close()
