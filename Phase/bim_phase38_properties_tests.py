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
    js("(()=>{var b=document.querySelector('[data-a3dr=\"bim:wall\"]');if(b)b.click();})()"); pg.wait_for_timeout(300)
    for (x,y) in [(cx-180,cy-90),(cx+180,cy-90),(cx+180,cy+90),(cx-180,cy+90)]:
        pg.mouse.click(x,y); pg.wait_for_timeout(140)
    pg.keyboard.press('c'); pg.wait_for_timeout(350)
    js("(()=>{var d=document.querySelector('.a3d-dlg');if(d)d.querySelector('[data-a3dlg=ok]').click();})()")
    pg.wait_for_timeout(900)
    print("=== PROPERTIES (Revit shape) ===")
    print("  type header present:", js("!!document.querySelector('.a3d-ptypehd')"))
    print("  object name:", js("(document.querySelector('.a3d-ptypename')||{}).textContent"))
    print("  family:type line:", js("(document.querySelector('.a3d-ptypesub')||{}).textContent"))
    print("  Edit Type button:", js("!!document.querySelector('.a3d-pedit')"))
    print("  parameter groups:", js("Array.from(document.querySelectorAll('.a3d-pgrp')).map(e=>e.textContent.replace(/[▴▾]/g,'').trim()).join(' | ')"))
    print("  rows in Dimensions:", js("""(()=>{var gs=Array.from(document.querySelectorAll('.a3d-pgrp'));
      var g=gs.filter(e=>e.textContent.indexOf('Dimensions')>=0)[0];
      if(!g)return 'none';var body=g.nextElementSibling;
      return Array.from(body.querySelectorAll('.a3d-plabel')).map(e=>e.textContent).join(', ');})()"""))
    print("  Apply button:", js("!!document.querySelector('.a3d-papply button')"))
    # collapse a group
    js("(()=>{var g=Array.from(document.querySelectorAll('.a3d-pgrp')).filter(e=>e.textContent.indexOf('Graphics')>=0)[0];if(g)g.click();})()")
    pg.wait_for_timeout(300)
    print("  Graphics collapsed:", js("""(()=>{var g=Array.from(document.querySelectorAll('.a3d-pgrp')).filter(e=>e.textContent.indexOf('Graphics')>=0)[0];
      return g && (!g.nextElementSibling || !g.nextElementSibling.classList.contains('a3d-pgbody'));})()"""))
    # edit thickness through the new layout (uses the pre-existing handler)
    r=js("""(()=>{var i=document.querySelector('[data-propf="thickness"]');
      if(!i)return 'no field';i.value='0.5';i.dispatchEvent(new Event('change',{bubbles:true}));return 'set';})()""")
    pg.wait_for_timeout(700)
    print("  editing Thickness via new layout:", r, "->", js("""(()=>{var st=JSON.parse(localStorage.getItem('acad3dV1')||'{}');
      var w=(st.objs||[]).filter(o=>o.bim&&o.bim.type==='wall')[0];return w?('model thickness='+w.bim.thickness):'none';})()"""))
    print()
    print("=== PROJECT BROWSER search ===")
    print("  search box:", js("!!document.querySelector('#a3d-bsearch')"))
    print("  model leaves before:", js("document.querySelectorAll('#a3d-browser [data-a3did]').length"))
    js("(()=>{var s=document.querySelector('#a3d-bsearch');s.value='zzz';s.dispatchEvent(new Event('input',{bubbles:true}));})()")
    pg.wait_for_timeout(400)
    print("  after searching 'zzz':", js("document.querySelectorAll('#a3d-browser [data-a3did]').length"), "(expect 0)")
    js("(()=>{var s=document.querySelector('#a3d-bsearch');s.value='wall';s.dispatchEvent(new Event('input',{bubbles:true}));})()")
    pg.wait_for_timeout(400)
    print("  after searching 'wall':", js("document.querySelectorAll('#a3d-browser [data-a3did]').length"))
    print()
    print("errors:", errs if errs else "none")
    pg.screenshot(path='/home/claude/props_revit.png')
    b.close()
