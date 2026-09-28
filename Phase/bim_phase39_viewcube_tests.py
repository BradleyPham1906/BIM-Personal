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
    # build a wall so there's context
    js("(()=>{var b=document.querySelector('[data-a3dr=\"bim:wall\"]');if(b)b.click();})()"); pg.wait_for_timeout(300)
    for (x,y) in [(cx-160,cy-80),(cx+160,cy-80),(cx+160,cy+80),(cx-160,cy+80)]:
        pg.mouse.click(x,y); pg.wait_for_timeout(140)
    pg.keyboard.press('c'); pg.wait_for_timeout(350)
    js("(()=>{var d=document.querySelector('.a3d-dlg');if(d)d.querySelector('[data-a3dlg=ok]').click();})()")
    pg.wait_for_timeout(700)
    js("(()=>{var t=Array.from(document.querySelectorAll('#acad-tabs .acad-tab')).filter(e=>e.style.display!=='none'&&e.textContent.trim()==='View')[0];if(t)t.click();})()")
    pg.wait_for_timeout(400)
    js("(()=>{var b=document.querySelector('[data-a3dr=\"v:iso\"]');if(b)b.click();})()"); pg.wait_for_timeout(900)
    print("visible cube faces:", js("(()=>{try{return A3D_TEST_CUBE();}catch(e){return 'n/a'}})()"))
    print("view label:", js("(document.querySelector('#a3d-view')||{}).textContent"))
    # click a cube face to change view
    cvb=pg.evaluate("(()=>{var c=document.querySelector('#a3d-canvas');var r=c.getBoundingClientRect();return{x:r.x,y:r.y,w:r.width,h:r.height};})()")
    cubeX = cvb['x']+cvb['w']-72
    cubeY = cvb['y']+68
    pg.mouse.click(cubeX, cubeY-14); pg.wait_for_timeout(700)
    print("after clicking a cube face, view:", js("(document.querySelector('#a3d-view')||{}).textContent"))
    # click the home icon
    pg.mouse.click(cubeX-51, cubeY-34); pg.wait_for_timeout(800)
    print("after clicking the home icon, view:", js("(document.querySelector('#a3d-view')||{}).textContent"))
    print("errors:", errs if errs else "none")
    pg.screenshot(path='/home/claude/cube_full.png')
    pg.screenshot(path='/home/claude/cube_zoom.png', clip={'x':cvb['x']+cvb['w']-190,'y':cvb['y'],'width':190,'height':150})
    b.close()
