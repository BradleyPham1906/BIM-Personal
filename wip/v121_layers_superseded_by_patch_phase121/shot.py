import asyncio, sys, pathlib
from playwright.async_api import async_playwright
HTML = pathlib.Path(sys.argv[1]).resolve(); OUT = sys.argv[2]
async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        page = await (await b.new_context(viewport={'width':1600,'height':900})).new_page()
        errs=[]; page.on('pageerror', lambda e: errs.append(str(e)[:200]))
        page.on('console', lambda m: errs.append('console: '+m.text[:200]) if m.type in ('warning','error') else None)
        await page.goto('file://' + str(HTML))
        await page.wait_for_function("()=>!!window.__a3dActiveView&&!!window.__a3dLayerNew", timeout=20000)
        await page.wait_for_timeout(600)
        r = await page.evaluate("""()=>{
          var m=window.__a3dLayers()[0].id;
          var w=window.__a3dLayerNew({name:'A-WALL',color:'#c0a377'});
          var wf=window.__a3dLayerNew({name:'A-WALL-FULL',parent:w});
          var an=window.__a3dLayerNew({name:'A-ANNO',color:'#84b98c'});
          window.__a3dLayerSet(an,'linetype','Dashed');
          window.__a3dLayerSet(an,'lineweight',0.5);
          window.__a3dLayerCurrent(w);
          var w1=window.__a3dWall([[0,0],[8,0]],0.3,3,'center',false);
          window.__a3dLayerCurrent(an);
          var s=window.__a3dSketch?window.__a3dSketch('poly',[[0,2],[4,2],[4,5]]):null;
          window.__a3dLayerCurrent(m);
          return {m:m,w:w,wf:wf,an:an,sk:s};}""")
        print(r)
        box = await page.evaluate("()=>{var e=document.querySelector('#figma-layers-rail .fl-rail-btn[data-tab=\"layers\"]');var q=e.getBoundingClientRect();return [q.x+q.width/2,q.y+q.height/2];}")
        await page.mouse.click(box[0], box[1]); await page.wait_for_timeout(400)
        for sel in ['[data-lytog="%s"]' % r['w'], '[data-lytog="%s"]' % r['an']]:
            bx = await page.evaluate("(q)=>{var e=document.querySelector(q);if(!e)return null;var r=e.getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2];}", sel)
            if bx: await page.mouse.click(bx[0], bx[1]); await page.wait_for_timeout(250)
        await page.evaluate("()=>window.__a3dTestPaint()")
        await page.wait_for_timeout(300)
        await page.screenshot(path=OUT)
        print('errs', errs[:6])
        await b.close()
asyncio.run(main())
