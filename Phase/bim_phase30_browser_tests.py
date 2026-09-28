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
    print("browser present:", js("!!document.querySelector('#a3d-browser')"))
    print("old tabs gone:", js("document.querySelectorAll('.a3d-treetab').length===0"))
    print("groups:", js("Array.from(document.querySelectorAll('.a3d-bgrp .a3d-blabel')).map(e=>e.textContent).join(' | ')"))
    # build a model
    tool('Wall'); pg.wait_for_timeout(250)
    for (x,y) in [(cx-200,cy-120),(cx+200,cy-120),(cx+200,cy+120),(cx-200,cy+120)]:
        pg.mouse.click(x,y); pg.wait_for_timeout(130)
    pg.keyboard.press('c'); pg.wait_for_timeout(350); okdlg(); pg.wait_for_timeout(800)
    tool('Room'); pg.wait_for_timeout(200); pg.mouse.click(cx,cy); pg.wait_for_timeout(700)
    print("model leaves:", js("Array.from(document.querySelectorAll('[data-a3did] .a3d-bname')).map(e=>e.textContent).join(', ')"))
    print("lock buttons present:", js("document.querySelectorAll('[data-a3dblock]').length"))
    # LOCK an object from the tree - the thing that was impossible before
    js("(()=>{var b=document.querySelector('[data-a3dblock]');if(b)b.click();})()")
    pg.wait_for_timeout(500)
    print("after lock click, locked state:", js("""(()=>{var st=JSON.parse(localStorage.getItem('acad3dV1')||'{}');
      var o=(st.objs||[])[0]; return o?('name='+o.name+' locked='+!!o.locked):'none';})()"""))
    # unlock again
    js("(()=>{var b=document.querySelector('[data-a3dblock]');if(b)b.click();})()")
    pg.wait_for_timeout(400)
    print("after 2nd click (unlock):", js("""(()=>{var st=JSON.parse(localStorage.getItem('acad3dV1')||'{}');
      var o=(st.objs||[])[0]; return o?('locked='+!!o.locked):'none';})()"""))
    # collapse a group -> crowding fix
    js("(()=>{var g=document.querySelector('[data-a3dbgrp=\"views\"]');if(g)g.click();})()")
    pg.wait_for_timeout(300)
    print("after collapsing Views, leaf count:", js("document.querySelectorAll('.a3d-bleaf').length"))
    js("(()=>{var g=document.querySelector('[data-a3dbgrp=\"views\"]');if(g)g.click();})()")
    pg.wait_for_timeout(300)
    # schedules from the tree
    js("(()=>{var g=document.querySelector('[data-a3dbgrp=\"schedules\"]');if(g)g.click();})()")
    pg.wait_for_timeout(300)
    js("(()=>{var b=document.querySelector('[data-a3dbsched=\"room\"]');if(b)b.click();})()")
    pg.wait_for_timeout(500)
    print("schedule opened:", js("(document.querySelector('#a3d-schedbody')||{}).textContent.slice(0,60)"))
    # layers lock
    js("(()=>{var g=document.querySelector('[data-a3dbgrp=\"layers\"]');if(g)g.click();})()")
    pg.wait_for_timeout(300)
    print("layer lock buttons:", js("document.querySelectorAll('[data-a3dblayerlock]').length"))
    print("errors:", errs if errs else "none")
    pg.screenshot(path='/home/claude/browser_new.png')
    b.close()
