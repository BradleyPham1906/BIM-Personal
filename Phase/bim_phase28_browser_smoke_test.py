from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1600,'height':1000})
    pg.goto('file:///home/claude/canvas_v10.html'); pg.wait_for_timeout(1500)
    pg.evaluate("window.__a3dEnter()"); pg.wait_for_timeout(800)
    def js(e):
        try: return pg.evaluate(e)
        except Exception as ex: return "THREW "+str(ex)[:200]
    def tool(l):
        return js(f"""(()=>{{var w=Array.from(document.querySelectorAll('#acad-panels [data-a3dr]')).filter(e=>e.textContent.trim()==={l!r})[0];
          if(!w)return 'NF'; w.click(); return 'ok';}})()""")
    box=pg.evaluate("(()=>{var c=document.querySelector('#a3d-canvas');var r=c.getBoundingClientRect();return{x:r.x,y:r.y,w:r.width,h:r.height};})()")
    cx,cy=box['x']+box['w']/2, box['y']+box['h']/2
    tool('Wall'); pg.wait_for_timeout(300)
    for (x,y) in [(cx-200,cy-120),(cx+200,cy-120),(cx+200,cy+120),(cx-200,cy+120)]:
        pg.mouse.click(x,y); pg.wait_for_timeout(150)
    pg.keyboard.press('c'); pg.wait_for_timeout(400)
    js("(()=>{var d=document.querySelector('.a3d-dlg');if(d)d.querySelector('[data-a3dlg=ok]').click();})()")
    pg.wait_for_timeout(900)
    tool('Room'); pg.wait_for_timeout(250); pg.mouse.click(cx,cy); pg.wait_for_timeout(800)
    print("after room:", js("Array.from(document.querySelectorAll('#a3d-rows .a3d-row')).map(e=>e.querySelector('.a3d-nm').textContent).join(', ')"))
    # Floor: now click-inside (Room is selected, so old path won't fire)
    tool('Floor'); pg.wait_for_timeout(300)
    print("floor tool armed (dialog not yet):", js("!!document.querySelector('.a3d-dlg')"))
    pg.mouse.click(cx,cy); pg.wait_for_timeout(500)
    print("floor dialog appeared:", js("!!document.querySelector('.a3d-dlg')"))
    js("(()=>{var d=document.querySelector('.a3d-dlg');if(d)d.querySelector('[data-a3dlg=ok]').click();})()")
    pg.wait_for_timeout(900)
    print("FINAL objects:", js("Array.from(document.querySelectorAll('#a3d-rows .a3d-row')).map(e=>e.querySelector('.a3d-nm').textContent).join(', ')"))
    # Ceiling too
    tool('Ceiling'); pg.wait_for_timeout(250); pg.mouse.click(cx,cy); pg.wait_for_timeout(400)
    js("(()=>{var d=document.querySelector('.a3d-dlg');if(d)d.querySelector('[data-a3dlg=ok]').click();})()")
    pg.wait_for_timeout(800)
    print("with ceiling:", js("Array.from(document.querySelectorAll('#a3d-rows .a3d-row')).map(e=>e.querySelector('.a3d-nm').textContent).join(', ')"))
    print("DXF:", js("(()=>{var r=window.__a3dBuildDXF();return 'poly='+r.stats.lwpolyline+' skipped='+r.stats.skipped+' bytes='+r.text.length;})()"))
    pg.screenshot(path='/home/claude/final_check.png')
    b.close()
