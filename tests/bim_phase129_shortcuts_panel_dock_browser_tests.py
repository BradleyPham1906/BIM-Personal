#!/usr/bin/env python3
"""bim_phase129_shortcuts_panel_dock_browser_tests.py -- V129: a keyboard shortcuts panel you can find
your way around, and a tool dock that says what its buttons are.

The owner, on the V128 sheet and the dock: "lets clean up these shortcuts stuff on the UI/UX becauase
it kinda hard to navigate and things not very clear", and on the mockup: "thats actually what i
want". Research: reference/research-shortcuts-ui.md (Figma, Google Docs, Linear, Fusion, Revit).

  1. THE PANEL opens on ? or SHORTCUTS, centred over the drawing, big enough to read, the search
     box ready; SHORTCUTS again leaves it open.
  2. CATEGORIES on the left with their counts; choosing one shows only it, marks it chosen for the
     eye and for a screen reader, and scrolls the list to its top; the search stays inside it.
  3. ROWS: what the key does on the left, the command to type, the keys ending on one right edge.
  4. TYPING POINTS (x,y  d<a  a bare length) is its own page after Drawing, with a note saying
     when it applies; the note goes when its rows do.
  5. CLOSING: the x; opened again it starts on All; the other rail menus stay small; ? in a field
     is a question mark.
  6. THE DOCK: a name under every tool, a name under every group, More instead of a bare triangle,
     a search pill that says what it is -- and the dock still leaves the drawing its room.
  7. TOOLTIPS: after a short pause on hover, at once on keyboard focus; name, keys, what to type,
     what it does, where it lives; a role=tooltip the button points to; Escape and leaving hide it;
     a tool not built yet says so.
  8. ICONS ONLY from Appearance: the names go, the dock gets shorter, the tooltip still names the
     tool, and the choice outlives a reload.

AMENDED FOR V130. The owner then found the dock crowded: "combine it in the shortcut table and use
search, filter sorting ... in the main screen only show the keys one". The panel became Tools and
shortcuts (every tool, then every key) and the dock one row of pinned tools, so the checks of the
dock's group names and More buttons are retired, and the rest read the new layout.

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

        has = await safe("()=>!!window.__acad3dV129")
        ck(bool(has), "__acad3dV129 marker is present")
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

        try:
            # ---------------------------------------------------------------------------------
            print("\n-- 1. the shortcuts panel opens centred, with its search ready")
            await blur()
            await page.mouse.move(800, 300)
            await page.keyboard.press('?')
            await page.wait_for_timeout(300)
            p = await panel()
            ck(p and p['open'] and p['forId'] == 'help', "? typed on the drawing opens the keyboard shortcuts (%s)" % (p and p['forId']))
            # AMENDED FOR V130: the panel is Tools and shortcuts
            ck(p and p['sheet'] and p['title'] == 'Tools and shortcuts', "as the shortcuts panel, titled (%r)" % (p and p['title']))
            if p:
                ck(abs(p['l'] + p['w'] / 2 - 800) <= 2 and abs(p['t'] + p['h'] / 2 - 475) <= 2,
                   "centred over the drawing, not squeezed beside the rail (centre %.0f,%.0f)" % (p['l'] + p['w'] / 2, p['t'] + p['h'] / 2))
                ck(p['w'] >= 800 and p['h'] >= 500 and p['l'] >= 0 and p['t'] >= 0 and p['l'] + p['w'] <= 1600 and p['t'] + p['h'] <= 950,
                   "big enough to read and inside the window (%dx%d at %d,%d)" % (p['w'], p['h'], p['l'], p['t']))
                ck(p['focus'], "its search box has the focus")
            await safe("()=>window.__a3dRunCmd('shortcuts')")
            await page.wait_for_timeout(200)
            p2 = await panel()
            ck(p2 and p2['open'] and p2['forId'] == 'help', "SHORTCUTS run again while it is open leaves it open")

            # ---------------------------------------------------------------------------------
            print("\n-- 2. categories on the left, with counts, and one list")
            p = await panel()
            # AMENDED FOR V130: All, On the dock, then every group (the tools', then the keys') in the list's order
            names = [c['name'] for c in p['cats']]
            ck(names[:2] == ['All', 'On the dock'] and [c['name'] for c in p['cats'][2:]] == p['grps'],
               "the categories are All, On the dock, then every group in the list's order (%s)" % names)
            per = {}
            for r in p['rows']:
                per[r['g']] = per.get(r['g'], 0) + 1
            ck(all(c['n'] == per.get(c['id'], -1) for c in p['cats'][2:]) and p['cats'][0]['n'] == len(p['rows']),   # AMENDED FOR V130: past On the dock
               "each category counts its own rows, and All counts them all (%d)" % p['cats'][0]['n'])
            ck(p['cats'][0]['on'] and p['cats'][0]['pressed'] == 'true' and not any(c['on'] for c in p['cats'][1:]),
               "All is the category chosen when it opens")
            await safe("()=>{var l=document.querySelector('#a3d-rupop .a3d-rukeys');l.scrollTop=l.scrollHeight;}")
            await pick('Snaps')
            p = await panel()
            ck(p['grps'] == ['Snaps'] and [r['lab'] for r in p['rows']] == ['Object snap on or off', 'Ortho on or off', 'Grid snap on or off'],
               "Snaps shows the snaps and nothing else (%s)" % [r['lab'] for r in p['rows']])
            ck([c['id'] for c in p['cats'] if c['on']] == ['Snaps'] and
               [c['id'] for c in p['cats'] if c['pressed'] == 'true'] == ['Snaps'],
               "and it is the one marked chosen, for the eye and for a screen reader")
            ck(p['scroll'] == 0, "the list starts at its top again (%s)" % p['scroll'])
            await pick('all')
            await safe("()=>{var l=document.querySelector('#a3d-rupop .a3d-rukeys');l.scrollTop=300;}")
            sc = await safe("()=>document.querySelector('#a3d-rupop .a3d-rukeys').scrollTop")
            await pick('all')
            p = await panel()
            ck(sc > 0 and p['scroll'] == 0, "even when the list is long enough to stay where it was (%s -> %s)" % (sc, p['scroll']))
            await pick('Snaps')
            await page.keyboard.press('Control+a')
            await page.keyboard.type('undo')
            await page.wait_for_timeout(150)
            p = await panel()
            ck(p['rows'] == [] and p['empty'], "search stays inside the category: 'undo' is not a snap, and it says so")
            await pick('all')
            p = await panel()
            ck('Undo' in [r['lab'] for r in p['rows']] and 'Editing' in p['grps'] and 'Snaps' not in p['grps'],
               "back on All the same words find Undo, under Editing (%s)" % p['grps'])
            await page.keyboard.press('Escape')
            await page.wait_for_timeout(120)

            # ---------------------------------------------------------------------------------
            print("\n-- 3. rows: what it does on the left, the command to type, the keys on the right")
            p = await panel()
            undo = [r for r in p['rows'] if r['lab'] == 'Undo']
            ck(undo and undo[0]['cmd'] == 'type UNDO' and undo[0]['keys'][-1] == 'Z',
               "Undo says the command to type for it and its keys (%s)" % (undo and undo[0]))
            ck(all(r['cmd'] == '' for r in p['rows'] if r['lab'].startswith('Switch between')),
               "a key with no command says nothing there")
            # AMENDED FOR V130: a tool row ends in its pin, so the keys end on one edge a pin's width in
            # from the row's; a key row's label starts at its left (a tool row's icon comes first)
            keyed = [r for r in p['rows'] if r['keys']]
            rights = sorted(set(round(r['rowR'] - r['keyR']) for r in keyed))
            ck(keyed and max(r['keyR'] for r in keyed) - min(r['keyR'] for r in keyed) <= 2,
               "every row's keys end on one right edge, one column to scan down (gaps %s)" % rights[:6])
            krows = [r for r in keyed if not r['g'].startswith('tool:')]
            ck(krows and all(abs(r['labL'] - r['rowL']) <= 12 for r in krows), "and every key's label starts at its left")

            # ---------------------------------------------------------------------------------
            print("\n-- 4. typing points is a page of its own, and says when it applies")
            p = await panel()
            order = [c['id'] for c in p['cats']]
            ck('Typing points' in order and order.index('Typing points') == order.index('Drawing') + 1,
               "Typing points follows Drawing (%s)" % order)
            tp = [r for r in p['rows'] if r['g'] == 'Typing points']
            ck([r['keys'] for r in tp] == [['x,y'], ['d<a'], ['0-9']], "with the three forms of a typed point (%s)" % [r['keys'] for r in tp])
            dr = [r['keys'] for r in p['rows'] if r['g'] == 'Drawing']
            ck(not any(k in (['x,y'], ['d<a'], ['0-9'], ['@x,y']) for k in dr), "and they are no longer rows of Drawing (%s)" % dr)
            ck(p['notes'] == ['Typing points'], "its note shows with it (%s)" % p['notes'])
            await page.keyboard.type('polar')
            await page.wait_for_timeout(150)
            p = await panel()
            # AMENDED FOR V130: the tools are in the list too (Polar Array); the key it finds is d<a
            ck([r['keys'] for r in p['rows'] if not r['g'].startswith('tool:')] == [['d<a']] and p['notes'] == ['Typing points'],
               "'polar' finds the d<a row, its note still above it")
            await page.keyboard.press('Control+a')
            await page.keyboard.type('f8')
            await page.wait_for_timeout(150)
            p = await panel()
            ck(p['notes'] == [], "a search that leaves that page out hides its note too (%s)" % p['notes'])
            await page.keyboard.press('Escape')
            await page.wait_for_timeout(120)
            await pick('Typing points')
            p = await panel()
            ck(p['grps'] == ['Typing points'] and p['notes'] == ['Typing points'] and len(p['rows']) == 3,
               "chosen on the left, it shows its note and its three rows")
            await page.click('#a3d-rupop .a3d-rkrow:not([hidden]) .a3d-rklab')
            await page.wait_for_timeout(120)
            p = await panel()
            ck([c['id'] for c in p['cats'] if c['on']] == ['Typing points'] and len(p['rows']) == 3,
               "a click on a row is not a click on a category: the choice stays (%s)" % [c['id'] for c in p['cats'] if c['on']])
            proj = await safe("()=>[...document.querySelectorAll('#a3d-rupop .a3d-rkrow[data-rkg=\"Project\"] .a3d-rklab')].map(e=>e.textContent)")
            ck(proj and any('?' in (r or '') or 'This panel' in r for r in proj), "the panel lists its own key, ? (%s)" % proj)

            # ---------------------------------------------------------------------------------
            print("\n-- 5. closing it")
            await page.click('#a3d-rupop [data-rkclose]')
            await page.wait_for_timeout(150)
            p = await panel()
            ck(p and not p['open'], "the x closes it")
            await safe("()=>window.__a3dRunCmd('shortcuts')")
            await page.wait_for_timeout(200)
            p = await panel()
            ck(p['open'] and [c['id'] for c in p['cats'] if c['on']] == ['all'] and len(p['grps']) >= 8,
               "opened again, it starts on All shortcuts (%s)" % [c['id'] for c in p['cats'] if c['on']])
            await page.keyboard.type('undo')
            await page.wait_for_timeout(150)
            p = await panel()
            ck('Undo' in [r['lab'] for r in p['rows']], "and a search then looks in all of them, not the page chosen last time (%s)" % [r['lab'] for r in p['rows']])
            await close_all()
            await safe("()=>window.__a3dRailOpen('zoom')")
            await page.wait_for_timeout(150)
            p = await panel()
            ck(p and p['open'] and not p['sheet'] and p['w'] < 400, "the other rail menus stay small popovers (%dpx)" % (p and p['w']))
            await close_all()
            await safe("()=>{var i=document.createElement('input');i.id='t129in';document.body.appendChild(i);i.focus();}")
            await page.keyboard.press('?')
            await page.wait_for_timeout(200)
            p = await panel()
            ck(not p['open'] and await safe("()=>document.getElementById('t129in').value") == '?',
               "? typed into a field is a question mark, not the panel")
            await safe("()=>{var i=document.getElementById('t129in');i.blur();i.remove();}")

            # ---------------------------------------------------------------------------------
            print("\n-- 6. the dock names its tools and its groups")
            await close_all()
            await safe("()=>window.__a3dDockLabels(true)")
            await page.wait_for_timeout(200)
            d = await dock()
            ck(d['names'], "tool names are on by default")
            ck(d['btns'] and all(b['lbl'] and b['aria'].startswith(b['lbl']) for b in d['btns']),
               "every tool on the dock has its name under its icon (%s)" % [b['lbl'] for b in d['btns']][:8])
            clipped = [b['lbl'] for b in d['btns'] if b['clipped']]
            ck(len(clipped) <= 2, "and the names fit (cut short: %s)" % clipped)
            # AMENDED FOR V130: "every group is named under its tools" and "each group's overflow says
            # More" are retired with the groups: the dock is one row of pinned tools
            ck(not any(b['title'] for b in d['btns']) and not any(c['title'] for c in d['cars']),
               "no native title, which would show a second, plainer tooltip on top of the real one")
            # AMENDED FOR V130: the one-row dock's pill is compact, its full name in its accessible name
            ck(d['pill'] and d['pill']['text'] == 'Search' and d['pill']['kbd'].endswith('K') and d['pill']['aria'] == 'Search tools and commands',
               "search is a labelled pill with its keys (%s)" % d['pill'])
            ck(d['h'] <= 150 and d['bottom'] <= 950 and d['left'] >= 0 and d['right'] <= 1600,
               "with names on, the dock still leaves the drawing its room (%.0fpx tall)" % d['h'])
            await page.click('#a3d-dsearch')
            await page.wait_for_timeout(250)
            ck(await safe("()=>document.getElementById('a3d-cmdpal').classList.contains('show')"), "the pill opens the command search")
            await close_all()

            # ---------------------------------------------------------------------------------
            print("\n-- 7. tooltips: name, keys, what to type, what it does, where it lives")
            wall = await centre('#a3d-dock .a3d-dbtn[data-a3dr="bim:wall"]')
            await page.mouse.move(800, 300)
            await page.wait_for_timeout(100)
            await page.mouse.move(wall[0], wall[1])
            await page.wait_for_timeout(90)
            ck(await tip() is None, "a pointer only passing over does not flash one")
            await page.wait_for_timeout(600)
            t = await tip()
            ck(t and t.startswith('Wall') and 'Type WALL or WA' in t, "a pause on Wall shows its tooltip (%r)" % t)
            geo = await safe("""()=>{var t=document.getElementById('a3d-tip').getBoundingClientRect(),b=document.querySelector('#a3d-dock .a3d-dbtn[data-a3dr="bim:wall"]');
              var r=b.getBoundingClientRect();return {above:t.bottom<=r.top,in:t.left>=0&&t.right<=1600&&t.top>=0,
              role:document.getElementById('a3d-tip').getAttribute('role'),desc:b.getAttribute('aria-describedby')};}""")
            ck(geo and geo['above'] and geo['in'], "above the button and inside the window (%s)" % geo)
            ck(geo and geo['role'] == 'tooltip' and geo['desc'] == 'a3d-tip', "a role=tooltip that describes the button (%s)" % geo)
            data = await safe("()=>window.__a3dDockTip('bim:wall')")
            ck(data and data['where'] and data['desc'], "it says what it does and where on the ribbon it lives (%s)" % data)
            await page.mouse.move(800, 300)
            await page.wait_for_timeout(120)
            ck(await tip() is None, "leaving the button hides it")
            rt = await safe("()=>window.__a3dDockTip('s:rect')")
            ck(rt and rt['type'] and rt['name'] == 'Rect', "a drafting tool's tooltip also names what to type (%s)" % (rt and rt['type']))
            await safe("()=>document.getElementById('a3d-discsel').focus()")   # AMENDED FOR V130: the pinned tools follow the discipline
            await page.keyboard.press('Tab')
            await page.wait_for_timeout(60)
            ft = await safe("()=>{var a=document.activeElement;return a&&a.getAttribute('data-a3dtip');}")
            t = await tip()
            ck(ft and t and t.startswith(await safe("(s)=>window.__a3dDockTip(s).name", ft)),
               "reached by the keyboard, a tool shows its tooltip at once (%s: %r)" % (ft, t))
            await page.keyboard.press('Escape')
            await page.wait_for_timeout(60)
            ck(await tip() is None, "and Escape puts it away")
            await blur()
            # AMENDED FOR V130: the unbuilt tools are greyed rows of the tools panel
            unimpl = await safe("()=>{window.__a3dToolsPanel();var e=document.querySelector('#a3d-rupop .a3d-rktool.off');var a=e?e.getAttribute('data-rkact'):null;document.querySelector('#a3d-rupop [data-rkclose]').click();return a;}")
            ud = await safe("(s)=>window.__a3dDockTip(s)", unimpl) if unimpl else None
            ck(ud and ud['desc'] == 'Not built yet', "a tool not built yet says so (%s: %s)" % (unimpl, ud))
            # AMENDED FOR V130: "More says what it opens" is retired with the More buttons; All tools says so
            md = await safe("()=>window.__a3dDockTip('__all')")
            ck(md and 'Every tool and key' in md['desc'], "All tools says what it opens (%s)" % md)

            # ---------------------------------------------------------------------------------
            print("\n-- 8. icons only, from Appearance, and remembered")
            items = await safe("()=>{var p=window.__a3dRailOpen('appear');return p?p.items:null;}")
            ck(items and 'Tool names on the dock' in str(items) and 'Icons only' in str(items),
               "Appearance offers tool names or icons only (%s)" % items)
            on_now = await safe("()=>document.querySelector('#a3d-rupop [data-a3druitem=\"appear:docknames\"]').classList.contains('on')")
            ck(on_now, "with Tool names marked as the current choice")
            names_h = d['h']
            await safe("()=>window.__a3dRailClick('appear:dockicons')")
            await page.wait_for_timeout(250)
            d2 = await dock()
            ck(not d2['names'] and all(b['lbl'] is None for b in d2['btns']) and d2['h'] < names_h,
               "Icons only takes the names off and the dock gets shorter (%.0f -> %.0fpx)" % (names_h, d2['h']))
            ck(all(b['aria'] for b in d2['btns']) and not any(b['title'] for b in d2['btns']),
               "each button keeps its name for a screen reader")
            w2 = await centre('#a3d-dock .a3d-dbtn[data-a3dr="bim:wall"]')
            await page.mouse.move(800, 300)
            await page.mouse.move(w2[0], w2[1])
            await page.wait_for_timeout(700)
            t = await tip()
            ck(t and t.startswith('Wall'), "and the tooltip gives the name back on a pause (%r)" % t)
            await page.mouse.move(800, 300)
            await within(page.reload(), 'reload')
            await page.wait_for_timeout(2300)
            d3 = await dock()
            ck(not d3['names'] and await safe("()=>window.__a3dDockLabels()") is False, "the choice outlives a reload")
            await safe("()=>window.__a3dRailOpen('appear')")
            await safe("()=>window.__a3dRailClick('appear:docknames')")
            await page.wait_for_timeout(250)
            d4 = await dock()
            ck(d4['names'] and all(b['lbl'] for b in d4['btns']), "and Tool names puts them back")
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
