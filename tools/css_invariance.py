"""css_invariance.py -- usage: python3 css_invariance.py REFERENCE.html CANDIDATE.html [--no-custom]
(both must end in .html, or Chromium renders them as text).
 -- a CSS prune that removes only rules which can never match must change nothing.
Drives two builds through the same states and compares, per state, every element's computed
style (with ::before and ::after) and the screenshot, pixel for pixel."""
import asyncio, pathlib, sys, json, hashlib, io
from playwright.async_api import async_playwright
from PIL import Image, ImageChops

REF, NEW = sys.argv[1], sys.argv[2]
# --no-custom: leave custom properties out of the comparison. A patch that deletes custom properties
# nothing reads changes every element's computed-style LIST (they are inherited) and nothing else;
# with this flag such a patch must compare IDENTICAL, which says no real property moved.
SKIP_CUSTOM = '--no-custom' in sys.argv[3:]

SNAP = r"""() => {
  var SKIPCUSTOM=__SKIPCUSTOM__;
  function h(s){var x=2166136261;for(var i=0;i<s.length;i++){x^=s.charCodeAt(i);x=Math.imul(x,16777619)>>>0;}return x.toString(16);}
  function path(el){
    var p=[];
    while(el&&el!==document.documentElement){
      var par=el.parentElement,i=0,sib=el;
      while((sib=sib.previousElementSibling))if(sib.tagName===el.tagName&&sib.tagName!=='STYLE'&&sib.tagName!=='SCRIPT')i++;
      p.unshift(el.tagName.toLowerCase()+':'+i);
      el=par;
    }
    return p.join('/');
  }
  function css(el,pe){var cs=getComputedStyle(el,pe),a=[],i;for(i=0;i<cs.length;i++){if(SKIPCUSTOM&&cs[i].indexOf('--')===0)continue;a.push(cs[i]+':'+cs.getPropertyValue(cs[i]));}a.sort();return a.join(';');}
  var out={},all=document.querySelectorAll('body *:not(style):not(script)'),i,el,k;
  for(i=0;i<all.length;i++){
    el=all[i];k=path(el);
    out[k]=h(css(el,null))+'|'+h(css(el,'::before'))+'|'+h(css(el,'::after'));
    if(el.id==='a3d-rail'||el.id==='figma-layers-rail'||el.tagName==='SCRIPT'&&!out['__s0'])out[(el.id==='a3d-rail'||el.id==='figma-layers-rail')?'__rail':'__s0']=css(el,null);
  }
  out['<body>']=h(css(document.body,null));
  out['<html>']=h(css(document.documentElement,null));
  return out;
}"""

STILL = "()=>{var s=document.createElement('style');s.id='__inv_still';s.textContent='*,*::before,*::after{animation:none!important;transition:none!important;caret-color:transparent!important}';document.head.appendChild(s);if(document.activeElement)document.activeElement.blur();}"

async def states(page):
    ev = page.evaluate
    async def settle(ms=500):
        await page.wait_for_timeout(ms)
    yield 'load'
    await ev("""()=>{window.__a3dFlat(true);window.__a3dTestSetObjs([]);
        [[[0,0],[12,0]],[[12,0],[12,8]],[[12,8],[0,8]],[[0,8],[0,0]]].forEach(function(s){window.__a3dWall(s,0.3,null,'center',false);});
        window.__a3dWall([[5,0],[5,8]],0.2,null,'center',false);
        var r=window.__a3dCreateRoomAt([2.5,4],0);window.__a3dCreateRoomAt([8,4],0);window.__a3dTagAllRooms();
        window.__a3dFit();window.__a3dSelectFor([r]);window.__a3dRefreshProps();window.__a3dTestPaint();}""")
    await settle(700); yield 'model'
    await ev("()=>{var b=document.querySelector('#a3d-rail .a3d-railbtn[data-tab=\"assets\"],#figma-layers-rail .fl-rail-btn[data-tab=\"assets\"]');b&&b.click();}")
    await settle(); yield 'assets'
    await ev("()=>{var b=document.querySelector('#a3d-rail .a3d-railbtn[data-tab=\"browser\"],#figma-layers-rail .fl-rail-btn[data-tab=\"file\"]');b&&b.click();}")
    await settle()
    await ev("()=>{window.openPalette();}"); await settle(300)
    await page.keyboard.type('WA'); await settle(); yield 'palette'
    await page.keyboard.press('Escape'); await settle(300)
    await ev("()=>{window.__a3dSet3DView();window.__a3dTestPaint();}"); await settle(700); yield '3d'
    await ev("()=>{window.__a3dSetPlanView();window.__a3dTestPaint();}"); await settle(400)
    await ev("()=>{var b=document.querySelector('#a3d-rail .a3d-paneltoggle,#figma-layers-rail .fl-logo');b&&b.click();}"); await settle(); yield 'collapsed'
    await ev("()=>{var b=document.querySelector('#a3d-rail .a3d-paneltoggle,#figma-layers-rail .fl-logo');b&&b.click();}"); await settle()
    await ev("()=>{window.__a3dOpenSchedule('room');}"); await settle(); yield 'schedule'
    await ev("()=>{var b=document.querySelector('[data-a3drumenu=\"appear\"]');b&&b.click();}"); await settle(); yield 'appearance-menu'
    await page.keyboard.press('Escape'); await ev("()=>{document.body.click();}"); await settle(300)
    await ev("()=>{var b=document.querySelector('[data-a3drumenu=\"help\"]');b&&b.click();}"); await settle(); yield 'help-menu'
    await page.keyboard.press('Escape'); await ev("()=>{document.body.click();}"); await settle(300)
    await ev("()=>{try{window.__a3dOpenDlg('wall');}catch(e){}}"); await settle(); yield 'wall-dialog'
    await page.keyboard.press('Escape'); await settle(300)
    await ev("()=>{var b=document.querySelector('#acad-doctabs [data-dt=\"start\"],#acad-doctabs .dt-start');if(b)b.click();}"); await settle(); yield 'start-tab'
    await page.set_viewport_size({'width': 700, 'height': 900}); await settle(700); yield 'narrow'

async def capture(path):
    out = {}
    cur = ['boot']
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        c = await b.new_context(viewport={'width': 1600, 'height': 950})
        p = await c.new_page()
        errs = []
        p.on('pageerror', lambda e: errs.append((cur[0], str(e)[:80], (getattr(e,'stack','') or '')[:300])))
        await p.goto('file://' + str(pathlib.Path(path).resolve()))
        await p.wait_for_timeout(2600)
        await p.mouse.click(800, 500); await p.wait_for_timeout(200)
        await p.evaluate(STILL)
        async for name in states(p):
            cur[0] = name
            await p.evaluate("()=>{if(document.activeElement&&document.activeElement.tagName!=='INPUT')document.activeElement.blur();}")
            styles = await p.evaluate(SNAP.replace("__SKIPCUSTOM__", "true" if SKIP_CUSTOM else "false"))
            png = await p.screenshot()
            await p.wait_for_timeout(350)
            png2 = await p.screenshot()
            out[name] = (styles, png, png2)
            pathlib.Path('/tmp/p114/shot_%s_%s.png' % (pathlib.Path(path).stem, name)).write_bytes(png)
        out['__errors__'] = errs
        await b.close()
    return out

async def main():
    ref = await capture(REF)
    new = await capture(NEW)
    bad = 0
    for name in [k for k in ref if k != '__errors__']:
        rs, rp, rp2 = ref[name]; ns, np_, np2 = new[name]
        missing = set(rs) ^ set(ns)
        diff = [k for k in rs if k in ns and rs[k] != ns[k]]
        def img(x): return Image.open(io.BytesIO(x)).convert('RGB')
        a, a2, b, b2 = img(rp), img(rp2), img(np_), img(np2)
        # A difference between the builds only counts where EACH build is stable against itself:
        # a region that flickers between two captures of one build is rendering noise, not CSS.
        noise = ImageChops.lighter(ImageChops.difference(a, a2), ImageChops.difference(b, b2)) if a.size == a2.size == b.size == b2.size else None
        cross = ImageChops.difference(a, b) if a.size == b.size else None
        if cross is None:
            bbox = ('size', a.size, b.size)
        else:
            nm = noise.convert('L').point(lambda v: 255 if v else 0)
            real = ImageChops.subtract(cross.convert('L').point(lambda v: 255 if v else 0), nm)
            bbox = real.getbbox()
        ok = not missing and not diff and bbox is None
        bad += 0 if ok else 1
        print('%-16s elements %5d  structure %s  styles %s  pixels %s' % (
            name, len(rs), 'same' if not missing else ('%d differ' % len(missing)),
            'same' if not diff else ('%d differ' % len(diff)),
            'same' if bbox is None else ('differ in %r' % (bbox,))))
        if diff:
            for k in diff[:2]: print('      style differs at', k)
            for key in ('__s0','__rail'):
                if key in rs and key in ns and rs[key]!=ns[key]:
                    A=dict(x.split(':',1) for x in rs[key].split(';') if ':' in x); B=dict(x.split(':',1) for x in ns[key].split(';') if ':' in x)
                    print('      %s: only-ref %s only-new %s changed %s' % (key, sorted(set(A)-set(B))[:5], sorted(set(B)-set(A))[:5], [(q,A[q][:30],B[q][:30]) for q in A if q in B and A[q]!=B[q]][:4]))
        if missing:
            for k in sorted(missing)[:3]: print('      only in one build:', k)
    print('page errors  ref:', ref['__errors__'][:2], ' new:', new['__errors__'][:2])
    print('RESULT:', 'IDENTICAL' if bad == 0 else '%d STATES DIFFER' % bad)

asyncio.run(main())
