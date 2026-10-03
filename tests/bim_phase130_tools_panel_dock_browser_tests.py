#!/usr/bin/env python3
"""bim_phase130_tools_panel_dock_browser_tests.py -- V130: every tool in one panel, and a dock of
the few used most.

The owner, on the V129 dock: "this tool bar is very crowded. I say we combine it in the shortcut
table and use search, filter sorting. group the features and stuff here. and in the main screen
only show the keys one (those that most likely use the most)".

  1. THE DOCK is one row: the discipline, the pinned tools with their names, All tools, the
     search -- no More menus, no second row, and a fraction of the old height.
  2. PINS per discipline: Architecture and Structure start with the tools used most; another
     discipline has its own.
  3. THE PANEL, Tools and shortcuts: every tool of every tab once, grouped by tab, then every key;
     the categories on the left count what they show.
  4. FILTER by kind: All, Tools, Keys, and the count shown.
  5. SEARCH across both: a tool by name, by what it does, by the command; a key by its key.
  6. SORT: by name, by use (a run from the dock or the panel counts), and back to by group.
  7. PIN from the panel: onto the dock and off, On the dock lists them, twelve at most, and the
     choice outlives a reload.
  8. A ROW RUNS its tool and the panel goes; a tool not built yet cannot run; ?, SHORTCUTS and
     All tools open the same panel.

The harness never waits without a bound (V123).
"""
import asyncio, pathlib, sys, traceback
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
STALL = 60


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
        ctx = await browser.new_context(viewport={'width': 1600, 'height': 950})
        page = await ctx.new_page()

        def guard(obj, names):
            for nm in names:
                def make(f, nm):
                    async def g(*a, **k):
                        return await within(f(*a, **k), '%s %s' % (nm, str(a[:1])[:40]))
                    return g
                setattr(obj, nm, make(getattr(obj, nm), nm))
        guard(page.keyboard, ('type', 'press', 'down', 'up'))
        guard(page.mouse, ('move', 'down', 'up', 'click', 'dblclick'))
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        await within(page.goto('file://' + str(HTML)), 'goto')
        await page.wait_for_timeout(2300)

        async def safe(js, arg=None):
            try:
                return await within(page.evaluate(js, arg) if arg is not None else page.evaluate(js),
                                    'evaluate ' + js[:60].replace('\n', ' '))
            except Stalled:
                raise
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:200])
                return None

        has = await safe("()=>!!window.__acad3dV130")
        ck(bool(has), "__acad3dV130 marker is present")
        if not has:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.bad), ck.n))
            await browser.close()
            return 1

        async def blur():
            await safe("()=>{if(document.activeElement&&document.activeElement.blur)document.activeElement.blur();}")
            await page.wait_for_timeout(60)

        async def close_all():
            for _ in range(3):
                await page.keyboard.press('Escape')
                await page.wait_for_timeout(80)
            await safe("()=>{window.closePalette&&window.closePalette();var p=document.getElementById('a3d-rupop');if(p)p.classList.remove('open');}")

        async def panel():
            return await safe("""()=>{var p=document.getElementById('a3d-rupop');if(!p)return null;var r=p.getBoundingClientRect();
              var vis=function(e){return e.offsetParent!==null;};
              return {open:p.classList.contains('open'),forId:p.getAttribute('data-for'),sheet:p.classList.contains('a3d-rksheet'),
                l:r.left,t:r.top,w:r.width,h:r.height,
                title:(p.querySelector('.a3d-rktitle')||{}).textContent||'',
                focus:!!(document.activeElement&&document.activeElement.classList.contains('a3d-rkfind')),
                cats:[...p.querySelectorAll('.a3d-rkcat')].map(c=>({id:c.getAttribute('data-rkcat'),name:c.firstChild.textContent,
                  n:+(c.querySelector('.a3d-rkn')||{}).textContent,on:c.classList.contains('on'),pressed:c.getAttribute('aria-pressed')})),
                grps:[...p.querySelectorAll('.a3d-rkgrp')].filter(vis).map(g=>g.textContent),
                notes:[...p.querySelectorAll('.a3d-rkgnote')].filter(vis).map(g=>g.getAttribute('data-rkg')),
                rows:[...p.querySelectorAll('.a3d-rkrow')].filter(vis).map(e=>({g:e.getAttribute('data-rkg'),
                  lab:e.querySelector('.a3d-rklab').textContent,cmd:e.querySelector('.a3d-rkcmd').textContent,
                  keys:[...e.querySelectorAll('.a3d-rkkeys kbd')].map(k=>k.textContent),
                  labL:e.querySelector('.a3d-rklab').getBoundingClientRect().left,rowL:e.getBoundingClientRect().left,
                  keyR:(function(){var k=e.querySelectorAll('.a3d-rkkeys kbd');return k.length?k[k.length-1].getBoundingClientRect().right:0;})(),
                  rowR:e.getBoundingClientRect().right-parseFloat(getComputedStyle(e).paddingRight)})),
                empty:!!(p.querySelector('.a3d-rkempty')&&p.querySelector('.a3d-rkempty').offsetParent!==null),
                scroll:(p.querySelector('.a3d-rukeys')||{}).scrollTop||0};}""")

        async def pick(cat):
            await page.click('#a3d-rupop .a3d-rkcat[data-rkcat="%s"]' % cat)
            await page.wait_for_timeout(120)

        async def tip():
            return await safe("()=>window.__a3dDockTipShown()")

        async def centre(sel):
            return await safe("(s)=>{var e=document.querySelector(s);if(!e||!e.offsetParent)return null;var r=e.getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2];}", sel)

        async def dock():
            return await safe("""()=>{var h=document.getElementById('a3d-dock');var b=h.querySelector('.a3d-dockbody').getBoundingClientRect();
              return {names:h.classList.contains('a3d-docklabels'),top:b.top,bottom:b.bottom,h:b.height,left:b.left,right:b.right,
                btns:[...h.querySelectorAll('.a3d-dbtn')].map(e=>({act:e.getAttribute('data-a3dr'),tip:e.getAttribute('data-a3dtip'),
                  title:e.getAttribute('title'),aria:e.getAttribute('aria-label')||'',lbl:(e.querySelector('.a3d-dblbl')||{}).textContent||null,
                  clipped:(function(){var l=e.querySelector('.a3d-dblbl');return l?l.scrollWidth>l.clientWidth+1:false;})()})),
                grps:[...h.querySelectorAll('.a3d-dockgrp[data-dockgrp]')].filter(g=>g.getAttribute('data-dockgrp')!=='__disc').map(g=>({id:g.getAttribute('data-dockgrp'),
                  lbl:(g.querySelector('.a3d-dglbl')||{}).textContent||null,lblShown:!!(g.querySelector('.a3d-dglbl')&&g.querySelector('.a3d-dglbl').offsetParent!==null)})),
                cars:[...h.querySelectorAll('.a3d-dcar')].map(c=>({text:c.textContent,aria:c.getAttribute('aria-label')||'',title:c.getAttribute('title'),svg:!!c.querySelector('svg')})),
                pill:(function(){var p=document.getElementById('a3d-dsearch');return p?{text:(p.querySelector('span')||{}).textContent||'',kbd:(p.querySelector('kbd')||{}).textContent||'',
                  aria:p.getAttribute('aria-label')||'',w:p.getBoundingClientRect().width}:null;})()};}""")

        async def rows(kind=None):
            return await safe("""(k)=>[...document.querySelectorAll('#a3d-rupop .a3d-rkrow')].filter(e=>e.offsetParent!==null&&(!k||e.getAttribute('data-rkkind')===k))
              .map(e=>({kind:e.getAttribute('data-rkkind'),act:e.getAttribute('data-rkact'),g:e.getAttribute('data-rkg'),
                lab:(e.querySelector('.a3d-rklab')||{}).textContent,pinned:e.getAttribute('data-rkpinned'),off:e.classList.contains('off')}))""", kind or '') or []

        async def shown():
            return await safe("()=>(document.querySelector('#a3d-rupop .a3d-rkshown')||{}).textContent||''")

        async def open_panel():
            await close_all()
            await page.click('#a3d-dall')
            await page.wait_for_timeout(250)

        async def dock_acts():
            return await safe("()=>[...document.querySelectorAll('#a3d-dock .a3d-dbtn')].map(b=>b.getAttribute('data-a3dr'))") or []

        async def kindf(k):
            await page.click('#a3d-rupop [data-rkkindf="%s"]' % k)
            await page.wait_for_timeout(120)

        async def sort(how):
            await page.select_option('#a3d-rupop .a3d-rksort', how)
            await page.wait_for_timeout(150)

        try:
            await safe("()=>window.__a3dCommandUsageClear()")
            # ---------------------------------------------------------------------------------
            print("\n-- 1. the dock is one row of the tools used most")
            d = await safe("""()=>{var h=document.getElementById('a3d-dock'),b=h.querySelector('.a3d-dockbody'),r=b.getBoundingClientRect();
              return {h:r.height,rows:b.querySelectorAll('.a3d-dockrow').length,disc:!!b.querySelector('#a3d-discsel'),all:!!b.querySelector('#a3d-dall'),
                search:!!b.querySelector('#a3d-dsearch'),more:h.querySelectorAll('[data-dockmore],[data-dockpop]').length,
                lbls:[...b.querySelectorAll('.a3d-dbtn')].map(e=>(e.querySelector('.a3d-dblbl')||{}).textContent||null),
                allLbl:(b.querySelector('#a3d-dall .a3d-dblbl')||{}).textContent||'',bottom:r.bottom,right:r.right,left:r.left};}""")
            ck(d and d['rows'] == 1 and d['disc'] and d['all'] and d['search'],
               "one row: the discipline, the tools, All tools and the search (%s rows)" % (d and d['rows']))
            ck(d and d['more'] == 0, "no More menus: the rest are in the panel")
            ck(d and d['h'] <= 60, "and it is a slim bar, %.0fpx tall (143 in V129)" % (d and d['h']))
            ck(d and d['bottom'] <= 950 and d['left'] >= 0 and d['right'] <= 1600, "inside the window")
            defaults = await safe("()=>window.__a3dDockPinDefaults()")
            acts = await dock_acts()
            ck(acts and acts == [a for a in defaults['arch'] if a in acts] and len(acts) >= 8,
               "Architecture shows the tools used most, in their order (%s)" % acts)
            ck(d and all(d['lbls']) and d['allLbl'] == 'All tools', "each with its name, and All tools says what it is (%s)" % (d and d['lbls']))
            tipd = await safe("()=>window.__a3dDockTip('__all')")
            ck(tipd and tipd['keys'] == ['?'], "All tools' tooltip gives its key, ? (%s)" % tipd)

            # ---------------------------------------------------------------------------------
            print("\n-- 2. each discipline its own")
            await page.select_option('#a3d-discsel', 'struct')
            await page.wait_for_timeout(250)
            sacts = await dock_acts()
            ck(sacts and 'bim:beam' in sacts and 'bim:analyze' in sacts and 'bim:door' not in sacts,
               "Structure shows beams, analysis and no doors (%s)" % sacts)
            ck(sacts == await safe("()=>window.__a3dDockPins('struct')"), "exactly the Structure pins")
            unb = [a for a in defaults['struct'] if a not in sacts]
            unb_desc = [await safe("(a)=>window.__a3dDockTip(a).desc", a) for a in unb]
            ck(all(x == 'Not built yet' for x in unb_desc),
               "a default not built yet is left off the dock (%s)" % unb)
            await page.select_option('#a3d-discsel', 'arch')
            await page.wait_for_timeout(250)

            # ---------------------------------------------------------------------------------
            print("\n-- 3. every tool, once, in the panel")
            await open_panel()
            p = await panel()
            ck(p and p['open'] and p['title'] == 'Tools and shortcuts', "All tools opens Tools and shortcuts (%r)" % (p and p['title']))
            ck(p and abs(p['l'] + p['w'] / 2 - 800) <= 2, "centred")
            tr = await rows('tool')
            cat_acts = await safe("()=>window.__a3dCommandCatalog().map(c=>c.act).filter(a=>!!a)") or []
            have = [r['act'] for r in tr]
            missing = [a for a in cat_acts if a not in have]
            ck(tr and not missing, "every tool the search knows has a row (%d rows; missing %s)" % (len(tr), missing[:5]))
            ck(len(have) == len(set(have)), "and each tool is there once")
            ribbon = await safe("()=>window.__a3dToolActions()") or []
            ck(sorted(have) == sorted(ribbon) and 'bim:levels' in have,
               "the rows are exactly the ribbon's actions, even one the search leaves out (%d of %d)" % (len(have), len(ribbon)))
            names = [c['id'] for c in p['cats']]
            ck(names[:2] == ['all', '__pinned'] and 'tool:arch' in names and 'tool:a3ddraft' in names and 'Snaps' in names
               and names.index('tool:a3dmanage') < names.index('Views'),
               "the categories: All, On the dock, the ribbon's tabs, then the key groups (%s)" % names)
            heads = await safe("()=>[...document.querySelectorAll('#a3d-rupop .a3d-rknavh')].map(e=>e.textContent)")
            ck(heads == ['Tools', 'Keys'], "under the headings Tools and Keys (%s)" % heads)
            kr = await rows('key')
            ck(p['cats'][0]['n'] == len(tr) + len(kr) and await shown() == '%d shown' % (len(tr) + len(kr)),
               "All counts every row, and the bar says how many are shown (%s)" % await shown())
            per = {}
            for r in tr + kr:
                per[r['g']] = per.get(r['g'], 0) + 1
            ck(all(c['n'] == per.get(c['id'], -1) for c in p['cats'][2:]), "each category counts its own rows")
            first = await safe("()=>{var g=document.querySelector('#a3d-rupop .a3d-rukeys .a3d-rkgrp');var n=g&&g.nextElementSibling;return [g&&g.textContent,n&&n.getAttribute('data-rkg')];}")
            ck(first and first[0] == 'Architecture' and first[1] == 'tool:arch', "each group's heading sits above its own tools (%s)" % first)
            wall = [r for r in tr if r['act'] == 'bim:wall']
            wrow = await safe("""()=>{var e=document.querySelector('#a3d-rupop .a3d-rkrow[data-rkact="bim:wall"]');return {cmd:e.querySelector('.a3d-rkcmd').textContent,
              desc:e.querySelector('.a3d-rkdesc').textContent,icon:!!e.querySelector('.a3d-rkrun svg'),pin:e.querySelector('[data-rkpin]').getAttribute('aria-pressed')};}""")
            ck(wrow and wrow['cmd'] == 'type WALL' and wrow['desc'] and wrow['icon'] and wrow['pin'] == 'true',
               "a tool row: icon, name, what it does, the command to type, and its pin, on (%s)" % wrow)
            ck(p['focus'], "the search has the focus")

            # ---------------------------------------------------------------------------------
            print("\n-- 4. Tools, Keys")
            await kindf('tool')
            t1 = await rows()
            ck(t1 and all(r['kind'] == 'tool' for r in t1) and len(t1) == len(tr) and await shown() == '%d shown' % len(tr),
               "Tools shows the tools only (%s)" % await shown())
            ck(await safe("()=>[...document.querySelectorAll('#a3d-rupop [data-rkkindf]')].filter(b=>b.getAttribute('aria-pressed')==='true').map(b=>b.getAttribute('data-rkkindf'))") == ['tool'],
               "and it is the one marked chosen")
            await kindf('key')
            k1 = await rows()
            ck(k1 and all(r['kind'] == 'key' for r in k1) and len(k1) == len(kr), "Keys shows the keys only (%d)" % len(k1))
            await page.click('#a3d-rupop .a3d-rkcat[data-rkcat="tool:arch"]')
            await page.wait_for_timeout(120)
            ck(await rows() == [] and await safe("()=>document.querySelector('#a3d-rupop .a3d-rkempty').offsetParent!==null"),
               "Keys in Architecture is nothing, and it says so")
            await kindf('all')
            ca = await rows()
            ck(ca and all(r['g'] == 'tool:arch' for r in ca) and len(ca) == per['tool:arch'], "All in Architecture: its tools (%d)" % len(ca))
            await page.click('#a3d-rupop .a3d-rkcat[data-rkcat="all"]')
            await page.wait_for_timeout(120)

            # ---------------------------------------------------------------------------------
            print("\n-- 5. one search over both")
            async def find(q):
                await page.click('#a3d-rupop .a3d-rkfind')
                await page.keyboard.press('Control+a')
                await page.keyboard.type(q)
                await page.wait_for_timeout(150)
                return await rows()
            r = await find('door')
            ck(any(x['act'] == 'bim:door' for x in r), "'door' finds the Door tool")
            r = await find('mirror')
            ck(any(x['act'] == 'bim:mirror' for x in r), "'mirror' finds Mirror by its name")
            r = await find('f8')
            ck([x['lab'] for x in r] == ['Ortho on or off'], "'f8' finds the key (%s)" % [x['lab'] for x in r])
            r = await find('slab')
            ck(any(x['act'] == 'bim:foundslab' for x in r), "a word of what a tool does finds it ('slab': %s)" % [x['lab'] for x in r][:4])
            r = await find('wall')
            ck(any(x['kind'] == 'tool' for x in r) and len(set(x['g'] for x in r)) >= 2, "'wall' finds tools in more than one group (%d rows)" % len(r))
            await page.keyboard.press('Escape')
            await page.wait_for_timeout(120)
            ck(len(await rows()) == len(tr) + len(kr), "Escape clears the search")

            # ---------------------------------------------------------------------------------
            print("\n-- 6. sorting")
            await kindf('tool')
            before = [x['act'] for x in await rows()]
            await sort('name')
            byname = [x['lab'].lower() for x in await rows()]
            ck(byname == sorted(byname) and len(byname) == len(before), "By name: one list, A to Z (%s ...)" % byname[:4])
            hv = await safe("()=>[...document.querySelectorAll('#a3d-rupop .a3d-rkgrp')].filter(e=>e.offsetParent!==null).length")
            ck(hv == 0, "with no group headings in it")
            await close_all()
            for a, n in (('bim:window', 2), ('bim:door', 1)):
                for _ in range(n):
                    await page.click('#a3d-dock .a3d-dbtn[data-a3dr="%s"]' % a)
                    await page.wait_for_timeout(120)
                    await page.keyboard.press('Escape')
                    await page.wait_for_timeout(60)
                    await page.keyboard.press('Escape')
                    await page.wait_for_timeout(60)
            ck(await safe("()=>window.__a3dCmdUsageOf('bim:window')") == 2 and await safe("()=>window.__a3dCmdUsageOf('bim:door')") == 1,
               "a tool run from the dock counts as a use (Window 2, Door 1)")
            await open_panel()
            await kindf('tool')
            await sort('used')
            used = [x['act'] for x in await rows()][:3]
            ck(used[:2] == ['bim:window', 'bim:door'], "Most used puts Window, then Door, first (%s)" % used)
            await sort('group')
            ck([x['act'] for x in await rows()] == before, "By group puts every row back where it was")
            ck(await safe("()=>[...document.querySelectorAll('#a3d-rupop .a3d-rkgrp')].filter(e=>e.offsetParent!==null).length") >= 8,
               "with its headings")
            await close_all()
            await safe("()=>window.__a3dRunCmd('shortcuts')")
            await page.wait_for_timeout(200)
            ck(await safe("()=>[document.getElementById('a3d-rupop').getAttribute('data-rkkind'),document.querySelector('#a3d-rupop .a3d-rksort').value]") == ['all', 'group'],
               "opened again, it starts on All, by group")

            # ---------------------------------------------------------------------------------
            print("\n-- 7. pinning")
            base = await dock_acts()
            await page.click('#a3d-rupop .a3d-rkrow[data-rkact="bim:roof"] [data-rkpin]')
            await page.wait_for_timeout(200)
            a2 = await dock_acts()
            ck(a2 == base + ['bim:roof'], "a pin puts Roof on the dock, at the end (%s)" % a2[-3:])
            ck(await safe("()=>document.querySelector('#a3d-rupop .a3d-rkrow[data-rkact=\"bim:roof\"] [data-rkpin]').getAttribute('aria-pressed')") == 'true',
               "its pin shows on")
            p = await panel()
            ck(p['open'], "and the panel stays open to pin more")
            await page.click('#a3d-rupop .a3d-rkcat[data-rkcat="__pinned"]')
            await page.wait_for_timeout(120)
            pr = [x['act'] for x in await rows()]
            ck(sorted(pr) == sorted(a2), "On the dock lists exactly what the dock shows (%d)" % len(pr))
            cnt = await safe("()=>document.querySelector('#a3d-rupop .a3d-rkpinn').textContent")
            ck(cnt == str(len(a2)), "and counts it (%s)" % cnt)
            await page.click('#a3d-rupop .a3d-rkrow[data-rkact="bim:wall"] [data-rkpin]')
            await page.wait_for_timeout(200)
            ck('bim:wall' not in await dock_acts() and 'bim:wall' not in [x['act'] for x in await rows()],
               "unpinned, Wall leaves the dock and the On the dock list")
            await page.click('#a3d-rupop .a3d-rkcat[data-rkcat="all"]')
            await page.wait_for_timeout(120)
            ck(any(x['act'] == 'bim:wall' for x in await rows()), "and stays in the panel")
            cur_acts = await dock_acts()
            extra = [x['act'] for x in await rows('tool') if not x['off'] and x['act'] not in cur_acts]
            n0 = len(await dock_acts())
            for a in extra[:12 - n0]:
                await safe("(a)=>window.__a3dSetDockPin(a,true)", a)
            full = await dock_acts()
            over = await safe("(a)=>window.__a3dSetDockPin(a,true)", extra[12 - n0])
            ck(len(full) == 12 and over is False and len(await dock_acts()) == 12, "twelve at most (%d, the 13th refused)" % len(full))
            wide = await safe("()=>{var r=document.querySelector('#a3d-dock .a3d-dockbody').getBoundingClientRect();return r.right<=1600&&r.left>=0;}")
            ck(wide, "and twelve still fit in the window")
            for a in full:
                if a not in a2:
                    await safe("(a)=>window.__a3dSetDockPin(a,false)", a)
            kept = await dock_acts()
            await close_all()
            await within(page.reload(), 'reload')
            await page.wait_for_timeout(2300)
            ck(await dock_acts() == kept, "the pins outlive a reload (%s)" % (await dock_acts())[-3:])
            await page.select_option('#a3d-discsel', 'struct')
            await page.wait_for_timeout(250)
            ck(await dock_acts() == sacts, "and Structure keeps its own")
            await page.select_option('#a3d-discsel', 'arch')
            await page.wait_for_timeout(250)

            # ---------------------------------------------------------------------------------
            print("\n-- 8. a row runs its tool")
            await blur()
            await page.keyboard.press('?')
            await page.wait_for_timeout(250)
            p = await panel()
            ck(p and p['open'] and p['title'] == 'Tools and shortcuts', "? opens the same panel")
            await page.click('#a3d-dall')
            await page.wait_for_timeout(150)
            o1 = (await panel())['open']
            await safe("()=>window.__a3dRunCmd('shortcuts')")
            await page.wait_for_timeout(150)
            o2 = (await panel())['open']
            ck(o1 and o2, "and All tools, then SHORTCUTS, while it is open each leave it open (%s, %s)" % (o1, o2))
            u0 = await safe("()=>window.__a3dCmdUsageOf('bim:wall')")
            await page.click('#a3d-rupop .a3d-rkrow[data-rkact="bim:wall"] .a3d-rkrun')
            await page.wait_for_timeout(250)
            st = await safe("()=>window.__a3dState().sk")
            p = await panel()
            ck(st and st['tool'] == 'wall' and not p['open'], "a click on Wall starts the wall tool and puts the panel away (%s)" % st)
            ck(await safe("()=>window.__a3dCmdUsageOf('bim:wall')") == u0 + 1, "and counts as a use")
            await close_all()
            await open_panel()
            off = await safe("""()=>{var e=document.querySelector('#a3d-rupop .a3d-rktool.off');if(!e)return null;var b=e.querySelector('.a3d-rkrun');
              return {act:e.getAttribute('data-rkact'),disabled:b.disabled,runs:b.hasAttribute('data-a3dr'),pin:!!e.querySelector('[data-rkpin]'),desc:e.querySelector('.a3d-rkdesc').textContent};}""")
            ck(off and off['disabled'] and not off['runs'] and not off['pin'] and off['desc'] == 'Not built yet',
               "a tool not built yet is listed, greyed, cannot run and cannot be pinned (%s)" % off)
            ok = await safe("()=>window.__a3dDockOpenGroup('a3dview')")
            p = await panel()
            ck(ok and [c['id'] for c in p['cats'] if c['on']] == ['tool:a3dview'], "a group can be opened in the panel by its id")
            await close_all()
            ck(not errs, "no page errors (%s)" % errs[:3])
        except Stalled as e:
            ck(False, "the suite ran to the end (stalled at %s)" % e)
        except Exception as e:
            traceback.print_exc()
            ck(False, "the suite ran to the end (stopped by %s: %s)" % (type(e).__name__, str(e)[:160]))

        print("")
        await browser.close()
    print("%d/%d checks passed" % (ck.n - len(ck.bad), ck.n))
    if ck.bad:
        for b in ck.bad:
            print("  FAILED: " + b)
        print("RESULT: FAIL")
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == '__main__':
    sys.exit(asyncio.run(run()))
