from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(args=['--use-gl=swiftshader','--enable-unsafe-swiftshader'])
    ctx=b.new_context(viewport={'width':1500,'height':950})
    pg=ctx.new_page()
    pg.goto('file:///home/claude/canvas_v10.html'); pg.wait_for_timeout(1700)
    def js(e):
        try: return pg.evaluate(e)
        except Exception as ex: return "THREW "+str(ex)[:200]
    js("document.querySelector('.acad-ws').click()"); pg.wait_for_timeout(250)
    js("(()=>{var i=document.querySelector('[data-wsm=\"3d\"]');if(i)i.click();})()"); pg.wait_for_timeout(1400)
    box=pg.evaluate("(()=>{var c=document.querySelector('#a3d-canvas');var r=c.getBoundingClientRect();return{x:r.x,y:r.y,w:r.width,h:r.height};})()")
    cx,cy=box['x']+box['w']/2, box['y']+box['h']/2
    js("(()=>{var b=document.querySelector('[data-a3dr=\"bim:wall\"]');if(b)b.click();})()"); pg.wait_for_timeout(280)
    pg.mouse.click(cx-180,cy); pg.wait_for_timeout(130); pg.mouse.click(cx+180,cy); pg.wait_for_timeout(130)
    pg.keyboard.press('Enter'); pg.wait_for_timeout(300)
    js("(()=>{var d=document.querySelector('.a3d-dlg');if(d)d.querySelector('[data-a3dlg=ok]').click();})()")
    pg.wait_for_timeout(800)
    # create a CUSTOM type via duplicate
    js("(()=>{var r=document.querySelector('#a3d-browser [data-a3did]');if(r)r.click();})()"); pg.wait_for_timeout(400)
    pg.evaluate("window.prompt=function(){return 'My Custom 555mm';}")
    js("(()=>{var b=document.querySelector('[data-propf=\"edittype\"]');if(b)b.click();})()"); pg.wait_for_timeout(500)
    js("(()=>{var b=document.querySelector('[data-typedup]');if(b)b.click();})()"); pg.wait_for_timeout(700)
    js("""(()=>{var i=document.querySelector('[data-typep="thickness"]');if(i)i.value='0.555';})()""")
    js("(()=>{var d=document.querySelector('.a3d-dlg');if(d)d.querySelector('[data-a3dlg=ok]').click();})()")
    pg.wait_for_timeout(1100)
    print("custom type created:", js("""(()=>{var st=JSON.parse(localStorage.getItem('acad3dV1')||'{}');
      var ws=(st.types&&st.types.wall)||[];return ws.map(t=>t.name+'='+t.params.thickness).join(' | ');})()"""))
    # RELOAD
    pg.reload(); pg.wait_for_timeout(2000)
    js("document.querySelector('.acad-ws').click()"); pg.wait_for_timeout(250)
    js("(()=>{var i=document.querySelector('[data-wsm=\"3d\"]');if(i)i.click();})()"); pg.wait_for_timeout(1400)
    print("AFTER RELOAD, custom type survives:", js("""(()=>{var st=JSON.parse(localStorage.getItem('acad3dV1')||'{}');
      var ws=(st.types&&st.types.wall)||[];
      var m=ws.filter(t=>t.name.indexOf('My Custom')>=0);
      return m.length?('YES: '+m[0].name+' thickness='+m[0].params.thickness):'LOST';})()"""))
    print("wall still bound to it:", js("""(()=>{var st=JSON.parse(localStorage.getItem('acad3dV1')||'{}');
      var w=(st.objs||[]).filter(o=>o.bim&&o.bim.type==='wall')[0];
      if(!w)return 'no wall';
      var t=((st.types&&st.types.wall)||[]).filter(x=>x.id===w.bim.typeId)[0];
      return t?('bound to "'+t.name+'"'):'DANGLING typeId';})()"""))
    b.close()
