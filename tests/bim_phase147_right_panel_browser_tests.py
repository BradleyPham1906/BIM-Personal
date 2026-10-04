#!/usr/bin/env python3
"""bim_phase147_right_panel_browser_tests.py -- V147: the right panel, redesigned.

Measured in the browser, not read from the stylesheet:
  1. TOKENS: the panel's colours come from one set of variables, redefined for the light theme.
  2. THE GRID: group headers in sentence case on a hairline, not uppercase boxes; every row's label
     and value inside the panel's padding; every input the same height; one button shape.
  3. RESIZE: from the left edge, by dragging, clamped to 240-560 px, remembered across a reload,
     the drawing taking the room given up; a double click resets it; not on a narrow screen.
  4. MINIMISE: to a strip and back, remembered; the header still says Properties.
  5. LONG LISTS end in Show all.

The harness never waits without a bound (V123).
"""
import asyncio, pathlib, re, sys, traceback
from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'


class Checks:
    def __init__(self):
        self.n, self.bad = 0, []

    def __call__(self, cond, msg):
        self.n += 1
        if not cond:
            self.bad.append(msg)
        print(('  ok    ' if cond else '  FAIL  ') + msg)


CK = Checks()
STALL = 90


class Stalled(Exception):
    pass


async def within(aw, what):
    try:
        return await asyncio.wait_for(aw, STALL)
    except asyncio.TimeoutError:
        raise Stalled(what)


async def run():
    ck = CK
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1500, 'height': 950})
        page = await ctx.new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        await within(page.goto('file://' + str(HTML)), 'goto')
        await page.wait_for_timeout(2300)

        async def safe(js, arg=None):
            try:
                return await within(page.evaluate(js, arg) if arg is not None else page.evaluate(js), 'evaluate ' + js[:50])
            except Stalled:
                raise
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:200])
                return None

        has = await safe("()=>window.__acad3dV147")
        ck(bool(has) and 'resizable' in has and 'paneltokens' in has, "__acad3dV147 marker is present (%s)" % has)
        if not has:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.bad), ck.n))
            await browser.close()
            return 1
        mv = re.search(r"var BIM_APP_VERSION=\{v:'V(\d+)'", HTML.read_text(encoding='utf-8'))
        ck(mv and int(mv.group(1)) >= 147, "the app says V147 or later (%s)" % (mv and mv.group(1)))

        async def width():
            return await safe("()=>document.getElementById('a3d-right').getBoundingClientRect().width")

        async def canvas_w():
            return await safe("()=>{var c=document.querySelector('#a3d-viewport canvas')||document.querySelector('canvas');return c.getBoundingClientRect().width;}")

        try:
            cid = await safe("()=>{window.__a3dColumnAt([10,10],0,0.4,0.4,3);var s=window.__a3dState().objs;return s[s.length-1].id;}")
            await safe("(i)=>{window.__a3dSelectFor([i]);window.__a3dRefreshProps();}", cid)
            await page.wait_for_timeout(150)

            print("\n-- 1. tokens")
            tok = await safe("()=>{var s=getComputedStyle(document.getElementById('a3d-right'));return [s.getPropertyValue('--pp-bg').trim(),s.getPropertyValue('--pp-text').trim(),s.backgroundColor];}")
            ck(tok and tok[0] == '#1e2226' and tok[2] == 'rgb(30, 34, 38)', "the panel's surface is its token (%s)" % tok)
            lt = await safe("()=>{document.body.classList.add('light-theme');var s=getComputedStyle(document.getElementById('a3d-right'));var r=[s.getPropertyValue('--pp-bg').trim(),s.backgroundColor,getComputedStyle(document.querySelector('#a3d-right .a3d-plabel')).color];document.body.classList.remove('light-theme');return r;}")
            ck(lt and lt[0] == '#fbfbfc' and lt[1] == 'rgb(251, 251, 252)' and lt[2] == 'rgb(104, 114, 128)', "the light theme redefines the same tokens (%s)" % lt)

            print("\n-- 2. the grid")
            g = await safe("""()=>{var e=document.querySelector('#a3d-right .a3d-pgrp'),s=getComputedStyle(e);
              return {tt:s.textTransform,fs:s.fontSize,bg:s.backgroundColor,bt:s.borderTopWidth,text:e.firstChild.textContent};}""")
            ck(g and g['tt'] == 'none' and g['fs'] == '12px' and g['bg'] in ('rgba(0, 0, 0, 0)', 'transparent') and g['bt'] == '1px',
               "group headers: sentence case, 12 px, no box, a hairline above (%s)" % g)
            box = await safe("""()=>{var b=document.getElementById('a3d-propsbody').getBoundingClientRect(),cs=getComputedStyle(document.getElementById('a3d-propsbody')),
              right=b.right-parseFloat(cs.paddingRight)-(document.getElementById('a3d-propsbody').offsetWidth-document.getElementById('a3d-propsbody').clientWidth),left=b.left+parseFloat(cs.paddingLeft),bad=[];
              [].forEach.call(document.querySelectorAll('#a3d-right .a3d-prow'),function(r){var x=r.getBoundingClientRect();if(x.width&&(x.right>right+0.5||x.left<left-0.5))bad.push([r.textContent.slice(0,20),x.left,x.right,left,right]);
                [].forEach.call(r.querySelectorAll('input,select,button'),function(c){var y=c.getBoundingClientRect();if(y.width&&y.right>right+0.5)bad.push([r.textContent.slice(0,20),'control',y.right,right]);});});
              return {n:document.querySelectorAll('#a3d-right .a3d-prow').length,bad:bad};}""")
            ck(box and box['n'] > 8 and not box['bad'], "every row and control inside the panel's padding (%d rows; %s)" % (box and box['n'], box and box['bad'][:2]))
            hs = await safe("""()=>[].map.call(document.querySelectorAll('#a3d-right .a3d-pval input[type=number],#a3d-right .a3d-pval input[type=text],#a3d-right .a3d-pval select'),function(e){return Math.round(e.getBoundingClientRect().height);}).filter(function(h){return h>0;})""") or []
            ck(len(hs) >= 4 and len(set(hs)) == 1 and hs[0] == 26, "every input the same height, 26 px (%s)" % sorted(set(hs)))
            bs = await safe("""()=>[].map.call(document.querySelectorAll('#a3d-propsbody button'),function(e){var s=getComputedStyle(e);return s.borderTopLeftRadius+'/'+Math.round(e.getBoundingClientRect().height);}).filter(function(x){return !/\\/0$/.test(x);})""") or []
            ck(bs and all(b.startswith('6px/') for b in bs), "one button shape, 6 px corners (%s)" % sorted(set(bs)))
            th = await safe("()=>{var n=document.querySelector('#a3d-right .a3d-ptypename');return n?[getComputedStyle(n).fontSize,n.textContent]:null;}")
            ck(th and th[0] == '13px' and th[1].startswith('Column'), "the element's name heads the panel, 13 px (%s)" % th)
            pc = await safe("()=>document.querySelectorAll('#a3d-propsbody [data-propf]').length")
            ck(pc and pc > 5, "the controls keep their data attributes (%d)" % pc)

            print("\n-- 3. resize")
            w0, c0 = await width(), await canvas_w()
            ck(abs(w0 - 280) < 1, "the panel starts at 280 px (%s)" % w0)
            r = await safe("()=>window.__a3dRightSetWidth(380)")
            await page.wait_for_timeout(120)
            w1, c1 = await width(), await canvas_w()
            ck(abs(w1 - 380) < 1 and abs((c0 - c1) - 100) < 2, "set to 380 px, the drawing gives up the 100 px (%s, %s)" % (w1, c0 - c1))
            ck(abs(((await safe("()=>window.__a3dRightSetWidth(100)")) or {}).get('w', 0) - 240) < 1 and abs(((await safe("()=>window.__a3dRightSetWidth(2000)")) or {}).get('w', 0) - 560) < 1,
               "clamped to 240 and 560 px")
            await safe("()=>window.__a3dRightSetWidth(300)")
            gb = await safe("()=>{var r=document.querySelector('#a3d-right .a3d-rgrip').getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2];}")
            await page.mouse.move(gb[0], gb[1])
            await page.mouse.down()
            await page.mouse.move(gb[0] - 40, gb[1], steps=4)
            await page.mouse.move(gb[0] - 60, gb[1], steps=4)
            await page.mouse.up()
            await page.wait_for_timeout(120)
            w2 = await width()
            ck(abs(w2 - 360) < 2, "dragging its left edge 60 px out widens it to 360 px (%s)" % w2)
            await page.wait_for_timeout(300)
            await within(page.reload(), 'reload')
            await page.wait_for_timeout(2300)
            ck(abs((await width()) - 360) < 2, "the width is remembered across a reload")
            gb = await safe("()=>{var r=document.querySelector('#a3d-right .a3d-rgrip').getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2];}")
            await page.mouse.dblclick(gb[0], gb[1])
            await page.wait_for_timeout(120)
            ck(abs((await width()) - 280) < 1, "a double click on the edge puts it back to 280 px")

            print("\n-- 4. minimise")
            hd = await safe("()=>document.querySelector('#a3d-right .a3d-palhd').textContent.trim()")
            await page.click('#a3d-rminbtn')
            await page.wait_for_timeout(120)
            st = await safe("()=>[document.getElementById('a3d-right').getBoundingClientRect().width,getComputedStyle(document.getElementById('a3d-propsbody')).display,document.getElementById('a3d-rminbtn').getAttribute('aria-pressed')]")
            ck(hd == 'Properties' and st and abs(st[0] - 42) < 1 and st[1] == 'none' and st[2] == 'true', "Minimise: a 42 px strip, the body hidden; the header still says Properties (%s)" % st)
            await page.wait_for_timeout(300)
            await within(page.reload(), 'reload')
            await page.wait_for_timeout(2300)
            ck(abs((await width()) - 42) < 1, "minimised is remembered across a reload")
            await page.click('#a3d-rminbtn')
            await page.wait_for_timeout(120)
            ck(abs((await width()) - 280) < 1 and await safe("()=>getComputedStyle(document.getElementById('a3d-propsbody')).display") != 'none', "and the button brings it back")

            print("\n-- 5. long lists")
            await safe("()=>{for(var i=0;i<20;i++)window.__a3dSketch('poly',[[i*3,40],[i*3+1,40],[i*3+1,41]]);window.__a3dSelectFor([]);window.__a3dSetPropTab('project');window.__a3dRefreshProps();}")
            await page.wait_for_timeout(150)
            n0 = await safe("()=>document.querySelectorAll('#a3d-propsbody [data-histchanges] [data-histkey]').length")
            btn = await safe("()=>{var b=document.querySelector('#a3d-propsbody [data-histact=\"all\"]');return b?b.textContent:null;}")
            ck(n0 == 12 and btn and btn.startswith('Show all '), "a long list shows twelve, then Show all (%s, %s)" % (n0, btn))
            await page.click('#a3d-propsbody [data-histact="all"]')
            await page.wait_for_timeout(120)
            n1 = await safe("()=>document.querySelectorAll('#a3d-propsbody [data-histchanges] [data-histkey]').length")
            ck(n1 and n1 > 12 and str(n1) in btn, "Show all shows them all (%s)" % n1)

            # a narrow screen keeps its own layout
            await safe("()=>window.__a3dRightSetWidth(380)")
            ck(await safe("()=>document.getElementById('a3d-right').style.width") == '380px', "a width saved on a wide screen")
            await page.set_viewport_size({'width': 800, 'height': 900})
            await page.wait_for_timeout(200)
            ck(await safe("()=>document.getElementById('a3d-right').style.width") == '', "on a narrow screen the remembered width is not forced on the drawer")
            print("\n-- 6. a phone and a tablet")
            for nm, w, h in (('phone', 390, 844), ('tablet', 820, 1180)):
                c2 = await browser.new_context(viewport={'width': w, 'height': h}, has_touch=True, is_mobile=(w < 700))
                p2 = await c2.new_page()
                p2.on('pageerror', lambda e: errs.append(str(e)))
                await within(p2.goto('file://' + str(HTML)), 'goto ' + nm)
                await p2.wait_for_timeout(2300)
                await p2.evaluate("()=>{window.__a3dColumnAt([10,10],0,0.4,0.4,3);var s=window.__a3dState().objs;window.__a3dSelectFor([s[s.length-1].id]);window.__a3dRefreshProps();}")
                closed = await p2.evaluate("()=>getComputedStyle(document.getElementById('a3d-right')).display")
                await p2.click('.a3d-rdrawerbtn')
                await p2.wait_for_timeout(300)
                r = await p2.evaluate("()=>{var e=document.getElementById('a3d-right'),b=e.getBoundingClientRect(),g=document.querySelector('#a3d-right .a3d-rgrip');return {l:b.left,t:b.top,w:b.width,h:b.height,r:b.right,bt:b.bottom,grip:getComputedStyle(g).display,bar:getComputedStyle(document.querySelector('#a3d-right .a3d-rsheetbar')).display};}")
                ih = await p2.evaluate("()=>[].map.call(document.querySelectorAll('#a3d-right .a3d-pval input[type=number],#a3d-right .a3d-pval select'),function(e){return Math.round(e.getBoundingClientRect().height);}).filter(function(x){return x>0;})")
                if nm == 'phone':
                    ck(closed == 'none' and abs(r['l']) < 1 and abs(r['w'] - w) < 1 and abs(r['bt'] - h) < 1 and abs(r['h'] - 0.62 * h) < 2 and r['bar'] == 'flex',
                       "phone: Properties opens as a sheet the width of the screen, 62%% of its height, with a grab bar (%s)" % r)
                    await p2.click('#a3d-right .a3d-rsheetbar')
                    await p2.wait_for_timeout(300)
                    hh = await p2.evaluate("()=>document.getElementById('a3d-right').getBoundingClientRect().height")
                    ck(abs(hh - 0.92 * h) < 2, "the grab bar raises it to 92%% (%s)" % hh)
                else:
                    ck(closed == 'none' and abs(r['w'] - 340) < 1 and abs(r['r'] - w) < 1 and r['bar'] == 'none', "tablet: a 340 px drawer from the right (%s)" % r)
                ck(r['grip'] == 'none', "%s: no resize edge" % nm)
                ck(ih and min(ih) >= 36, "%s: inputs a finger can hit, 36 px (%s)" % (nm, sorted(set(ih))))
                await p2.click('#a3d-rminbtn')
                await p2.wait_for_timeout(200)
                st = await p2.evaluate("()=>[getComputedStyle(document.getElementById('a3d-right')).display,document.body.classList.contains('a3d-rmin')]")
                ck(st == ['none', False], "%s: the panel's arrow closes it, not minimise it (%s)" % (nm, st))
                await c2.close()
            ck(not errs, "no page errors (%s)" % errs[:3])
        except Stalled as e:
            ck(False, "the harness stalled at: %s" % e)
        except Exception:
            traceback.print_exc()
            ck(False, "the suite ran to its end")
        await browser.close()
    print("\n%d/%d checks passed" % (ck.n - len(ck.bad), ck.n))
    print("RESULT: " + ("PASS" if not ck.bad else "FAIL"))
    return 0 if not ck.bad else 1


if __name__ == '__main__':
    sys.exit(asyncio.run(run()))
