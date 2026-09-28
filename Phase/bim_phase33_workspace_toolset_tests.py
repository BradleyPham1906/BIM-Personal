from playwright.sync_api import sync_playwright
errs=[]
with sync_playwright() as p:
    b=p.chromium.launch(args=['--use-gl=swiftshader','--enable-unsafe-swiftshader'])
    pg=b.new_page(viewport={'width':1700,'height':1000})
    pg.on('pageerror', lambda e: errs.append(str(e)[:250]))
    pg.goto('file:///home/claude/canvas_v10.html'); pg.wait_for_timeout(1800)
    def js(e):
        try: return pg.evaluate(e)
        except Exception as ex: return "THREW "+str(ex)[:200]
    def ws(k):
        js("document.querySelector('.acad-ws').click()"); pg.wait_for_timeout(250)
        js(f"(()=>{{var i=document.querySelector('[data-wsm=\"{k}\"]');if(i)i.click();}})()"); pg.wait_for_timeout(800)
    def tabs(): return js("Array.from(document.querySelectorAll('#acad-tabs .acad-tab')).filter(e=>e.style.display!=='none').map(e=>e.textContent).join(' | ')")
    def panels(): return js("Array.from(document.querySelectorAll('#acad-panels .acad-panel-title')).map(e=>e.textContent.trim()).join(' | ')")
    def cmds(): return js("Array.from(document.querySelectorAll('#acad-panels button')).map(e=>e.textContent.trim().replace(/\\s+/g,' ')).filter(Boolean).join(', ')")
    def clicktab(t): js(f"(()=>{{var b=Array.from(document.querySelectorAll('#acad-tabs .acad-tab')).filter(e=>e.style.display!=='none'&&e.textContent.trim()==={t!r})[0];if(b)b.click();}})()"); pg.wait_for_timeout(400)
    def fits(): return js("(()=>{var h=document.querySelector('#acad-panels');return h.scrollWidth<=h.clientWidth+4;})()")

    print("=========== CANVAS ===========")
    ws('canvas')
    print("tabs:", tabs())
    for t in ['Insert','Arrange','View','Output']:
        clicktab(t); print(f"  [{t}] panels: {panels()}")
        print(f"       cmds: {cmds()[:150]}")
        print(f"       fits: {fits()}")
    print()
    print("======= DRAFTING & ANNOTATION =======")
    ws('da')
    print("tabs:", tabs())
    for t in ['Home','Annotate','View','Output']:
        clicktab(t); print(f"  [{t}] panels: {panels()}")
        print(f"       cmds: {cmds()[:160]}")
        print(f"       fits: {fits()}")
    print()
    print("=========== 3D ===========")
    ws('3d')
    print("tabs:", tabs())
    for t in ['Architecture','Annotate','Modify','Massing & Site']:
        clicktab(t); print(f"  [{t}] panels: {panels()}  fits={fits()}")
    print("secondary toolbar:", js("Array.from(document.querySelectorAll('.a3d-tb .a3d-btn')).map(e=>e.textContent.trim()).join(' | ')"))
    print()
    print("errors:", errs if errs else "none")
    ws('canvas'); pg.screenshot(path='/home/claude/ws_canvas2.png')
    ws('da'); pg.screenshot(path='/home/claude/ws_da.png')
    b.close()
