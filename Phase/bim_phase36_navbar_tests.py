from playwright.sync_api import sync_playwright
errs=[]
with sync_playwright() as p:
    b=p.chromium.launch(args=['--use-gl=swiftshader','--enable-unsafe-swiftshader'])
    pg=b.new_page(viewport={'width':1500,'height':950})
    pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.goto('file:///home/claude/canvas_v10.html'); pg.wait_for_timeout(1800)
    def js(e):
        try: return pg.evaluate(e)
        except Exception as ex: return "THREW "+str(ex)[:200]
    js("document.querySelector('.acad-ws').click()"); pg.wait_for_timeout(250)
    js("(()=>{var i=document.querySelector('[data-wsm=\"3d\"]');if(i)i.click();})()"); pg.wait_for_timeout(1400)
    tot_missing=0
    for t in ['Architecture','Structure','Annotate','Insert','View','Modify','Massing & Site','Manage']:
        js(f"(()=>{{var b=Array.from(document.querySelectorAll('#acad-tabs .acad-tab')).filter(e=>e.style.display!=='none'&&e.textContent.trim()==={t!r})[0];if(b)b.click();}})()")
        pg.wait_for_timeout(280)
        r=js("""(()=>{var n=0;
          document.querySelectorAll('#acad-panels .acad-sm-ic, #acad-panels .acad-big-ic').forEach(function(e){
            if(!e.querySelector('svg'))n++;});
          var h=document.getElementById('acad-panels');
          var clipped=0;var hb=h.getBoundingClientRect();
          document.querySelectorAll('#acad-panels .acad-panel-title').forEach(function(e){
            if(e.getBoundingClientRect().bottom>hb.bottom+1)clipped++;});
          return JSON.stringify({noIcon:n,overflow:h.scrollWidth>h.clientWidth+2,clippedTitles:clipped});})()""")
        print(f"  {t}: {r}")
        import json
        tot_missing += json.loads(r)['noIcon']
    print()
    print("TOTAL buttons with no icon across all 3D tabs:", tot_missing)
    print("page errors:", errs if errs else "none")
    js("(()=>{var b=Array.from(document.querySelectorAll('#acad-tabs .acad-tab')).filter(e=>e.style.display!=='none'&&e.textContent.trim()==='Architecture')[0];if(b)b.click();})()")
    pg.wait_for_timeout(300)
    pg.screenshot(path='/home/claude/nav_final.png', clip={'x':0,'y':0,'width':1500,'height':160})
    b.close()
