#!/usr/bin/env python3
"""bim_phase128_command_search_browser_tests.py -- V128: one command search, and a command line that
listens everywhere.

The owner: "lets make command UI easy to use. shortcuts searchable and stuff ... as this app become
more sophisticate, it is hard." Research: reference/research-command-ui.md (AutoCAD's Input Search
Options, Rhino, VS Code, Blender F3, Revit's Keyboard Shortcuts dialog).

  1. THE CATALOGUE: every runnable typed command and every implemented ribbon tool, once each; a
     ribbon button that is a typed command is that command's row, with its ribbon place; the keys a
     row shows are the shortcut sheet's own.
  2. MATCHING: exact name and alias first; prefixes; synonyms (ROUND finds FILLET); every word
     typed must match; abbreviations (PLNE); keyboard chords (Ctrl+Z, F8); a typo only when nothing
     matched as typed; the matched letters marked.
  3. USE: the more a command is used the higher it ranks among equals, never above a better match;
     the most recent lead the empty list.
  4. THE PALETTE: rows show the ribbon place, alias and keys; ? searches the keyboard shortcuts and
     runs the command a chord belongs to; Tab cycles; the ARIA combobox; a ribbon-only tool runs;
     Enter repeats it; on a sheet a model command says why it cannot run.
  5. TYPE ANYWHERE: letters typed on the drawing open the search and run WALL from "wa"; not while a
     tool takes points, a field has the focus, or a dialog is open.
  6. ONE SEARCH: the dock's magnifier opens it; every ribbon tooltip names the command to type.
  7. THE SHORTCUT SHEET searches: by what a key does or the key; Escape clears, then closes.

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
        await page.goto('file://' + str(HTML))
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

        has = await safe("()=>!!window.__acad3dV128")
        ck(bool(has), "__acad3dV128 marker is present")
        if not has:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.bad), ck.n))
            await browser.close()
            return 1

        async def blur():
            await safe("()=>{if(document.activeElement&&document.activeElement.blur)document.activeElement.blur();}")
            await page.wait_for_timeout(60)

        async def toast():
            return await safe("()=>{var t=document.getElementById('a3d-toast');return t?t.textContent:'';}") or ''

        async def search(q, n=8):
            return await safe("(a)=>window.__a3dCommandSearch(a[0],a[1])", [q, n]) or []

        async def names(q, n=8):
            return [r['name'] for r in await search(q, n)]

        async def pal_open():
            return await safe("()=>document.getElementById('a3d-cmdpal').classList.contains('show')")

        async def pal_rows():
            return await safe("""()=>[...document.querySelectorAll('#a3d-cmdpal .a3d-cmdrow[data-idx]')].map(r=>({
              name:(r.querySelector('.a3d-cmdname')||{}).textContent||'',text:r.textContent,
              where:(r.querySelector('.a3d-cmdwhere')||{}).textContent||'',alias:(r.querySelector('.a3d-cmdkey')||{}).textContent||'',
              kbd:[...r.querySelectorAll('.a3d-cmdkbd kbd')].map(k=>k.textContent),hl:[...r.querySelectorAll('.a3d-cmdhl')].map(b=>b.textContent).join(''),
              off:(r.querySelector('.a3d-cmdoff')||{}).textContent||'',active:r.classList.contains('active'),id:r.id,sel:r.getAttribute('aria-selected')}))""") or []

        async def pal_heads():
            return await safe("()=>[...document.querySelectorAll('#a3d-cmdpal .a3d-cmdhd')].map(h=>h.textContent)") or []

        async def open_pal(q=''):
            await blur()
            await page.keyboard.press('Control+k')
            await page.wait_for_timeout(250)
            if q:
                await page.keyboard.type(q)
                await page.wait_for_timeout(200)

        async def close_all():
            for _ in range(3):
                await page.keyboard.press('Escape')
                await page.wait_for_timeout(80)
            await safe("()=>{window.closePalette&&window.closePalette();}")

        try:
            await safe("()=>window.__a3dCommandUsageClear()")
            # ---------------------------------------------------------------------------------
            print("\n-- 1. the catalogue")
            cat = await safe("()=>window.__a3dCommandCatalog()") or []
            nm = [c['name'] for c in cat]
            ck(len(cat) > 130 and len(nm) == len(set(nm)), "%d entries, every name once" % len(cat))
            reg = await safe("""()=>window.__wsRegistry.filter(c=>window.__a3dCmdSupported(c.cad)).map(c=>c.name)""") or []
            ck(reg and all(n in nm for n in reg), "every typed command that runs is in it (%d)" % len(reg))
            shown = await safe("()=>window.__a3dDockSearch('').shown") or []
            ck(len(shown) > 40, "the ribbon's tools are in it (%d)" % len(shown))
            wall = [c for c in cat if c['name'] == 'WALL']
            ck(len(wall) == 1 and wall[0]['kind'] == 'cmd' and wall[0]['act'] == 'bim:wall' and 'Architecture › Build' in wall[0]['where']
               and not [c for c in cat if c['kind'] == 'act' and c['act'] == 'bim:wall'],
               "the ribbon's Wall button is the WALL command's row, with its place on the ribbon -- not a second row")
            keys = await safe("()=>window.__a3dShortcuts()") or []
            with_cmd = [(r['cmd'], r['keys']) for g in keys for r in g['rows'] if r.get('cmd')]
            by = {c['name']: c for c in cat}
            ck(with_cmd and all(c in by and by[c]['keys'] == k for c, k in with_cmd),
               "every chord on the shortcut sheet that runs a command is that command's keys in the search (%s)" % [c for c, k in with_cmd])
            ck(by.get('BOX', {}).get('kind') == 'act' and by['BOX']['desc'] == 'Place a box' and 'Massing' in by['BOX']['where'][0],
               "a ribbon-only tool has a name to type, what it does and where it is (BOX)")

            # ---------------------------------------------------------------------------------
            print("\n-- 2. matching")
            ck((await names('WALL'))[0] == 'WALL' and (await names('wa'))[0] == 'WALL' and (await names('l'))[0] == 'LINE'
               and (await names('e'))[0] == 'ERASE',
               "an exact name, and an alias, come first: WALL, wa -> WALL, l -> LINE, e -> ERASE (not EXTEND, listed first)")
            ck((await names('round')).count('FILLET') == 1 and 'ERASE' in await names('delete'),
               "synonyms: round finds FILLET, delete finds ERASE (AutoCAD's search content)")
            ck((await names('export pdf'))[0] == 'EXPORTPDF' and 'EXPORTDXF' not in await names('export pdf'),
               "every word typed must match: export pdf is EXPORTPDF, not EXPORTDXF")
            ck((await names('plne'))[0] == 'PLINE', "an abbreviation from the first letter: plne finds PLINE")
            ck((await names('ctrl+z'))[:1] == ['UNDO'] and (await names('cmd+z'))[:1] == ['UNDO'] and (await names('f8'))[:1] == ['ORTHO'],
               "a keyboard chord finds its command: Ctrl+Z (or Cmd+Z) UNDO, F8 ORTHO")
            fl = await search('fillit')
            ck([r['name'] for r in fl] == ['FILLET'] and fl[0]['typo'], "a typo is offered when nothing matched as typed: fillit -> FILLET, marked")
            rn = await search('rectnag')
            ck([r['name'] for r in rn] == ['RECTANG'] and rn[0]['typo'],
               "two letters swapped in the name itself: rectnag -> RECTANG (no word of its description is that close)")
            fe = await search('filet')
            ck(fe and fe[0]['name'] == 'FILLET' and not any(r['typo'] for r in fe), "and not when something did: filet finds FILLET directly")
            tr = await search('tri')
            trim = [r for r in tr if r['name'] == 'TRIM']
            ck(trim and trim[0]['hl'] == [0, 1, 2], "the letters that matched are marked: TRI of TRIM")
            ck(await search('qqxzzv') == [], "nothing matches nonsense")
            ck((await names('gcpar'))[:1] == ['GCPARALLEL'] and (await names('sketch parallel'))[:1] == ['GCPARALLEL'],
               "the sketch constraints go by AutoCAD's names, and by what they do")

            # ---------------------------------------------------------------------------------
            print("\n-- 3. use")
            before = await names('foot')
            for _ in range(2):
                await safe("()=>window.__a3dCommandRun('cmd:FOOTINGSALL')")
            await close_all()
            after = await names('foot')
            ck(before[:2] == ['FOOTING', 'FOOTINGSALL'] and after[:2] == ['FOOTINGSALL', 'FOOTING'],
               "used twice, FOOTINGSALL rises above FOOTING for 'foot' (%s -> %s)" % (before[:2], after[:2]))
            ck((await names('footing'))[0] == 'FOOTING', "but never above a better match: 'footing' is still FOOTING")
            await safe("()=>window.__a3dCommandRun('cmd:GRID')")
            rec = await safe("()=>window.__a3dCommandRecent(5).map(r=>r.name)")
            ck(rec and rec[:2] == ['GRID', 'FOOTINGSALL'], "the most recent lead, not the most used (%s)" % rec)

            # ---------------------------------------------------------------------------------
            print("\n-- 4. the palette")
            await close_all()
            await open_pal()
            heads = await pal_heads()
            rows = await pal_rows()
            ck(heads[:2] == ['Recently used', 'All commands'] and [r['name'] for r in rows[:2]] == ['GRID', 'FOOTINGSALL'],
               "opened empty: the recently used, then every command (%s)" % heads)
            ck(len([r for r in rows if r['name'] == 'GRID']) == 1, "a recent command is not listed twice")
            await page.keyboard.type('wall')
            await page.wait_for_timeout(200)
            rows = await pal_rows()
            w = rows[0] if rows else {}
            ck(w.get('name') == 'WALL' and w.get('where', '').startswith('Architecture') and w.get('alias') == 'WA' and w.get('hl') == 'WALL',
               "the WALL row: its ribbon place, its alias, the letters that matched (%s)" % {k: w.get(k) for k in ('name', 'where', 'alias', 'hl')})
            ck(w.get('text', '').startswith('WALL — '), "and it still reads 'WALL -- what it does' (V86's row)")
            await page.keyboard.press('Control+a')
            await page.keyboard.type('undo')
            await page.wait_for_timeout(200)
            rows = await pal_rows()
            mod = await safe("()=>(navigator.platform&&/Mac|iPhone|iPad/.test(navigator.platform))?'Cmd':'Ctrl'")
            ck(rows and rows[0]['name'] == 'UNDO' and rows[0]['kbd'] == [mod, 'Z'], "the UNDO row shows its keys, %s+Z" % mod)
            ar = await safe("""()=>{var i=document.querySelector('#a3d-cmdpal input'),l=document.getElementById('a3d-cmdlist');
              return {role:i.getAttribute('role'),controls:i.getAttribute('aria-controls'),list:l.getAttribute('role'),
                active:i.getAttribute('aria-activedescendant'),opt:(document.getElementById(i.getAttribute('aria-activedescendant'))||{}).getAttribute?
                  document.getElementById(i.getAttribute('aria-activedescendant')).getAttribute('aria-selected'):null,focus:document.activeElement===i};}""")
            ck(ar and ar['role'] == 'combobox' and ar['controls'] == 'a3d-cmdlist' and ar['list'] == 'listbox' and ar['opt'] == 'true' and ar['focus'],
               "the ARIA combobox: the input keeps the focus and names the active row (%s)" % ar)
            await page.keyboard.press('Control+a')
            await page.keyboard.type('foot')
            await page.wait_for_timeout(200)
            n_rows = len(await pal_rows())
            await page.keyboard.press('Tab')
            a1 = [r['name'] for r in await pal_rows() if r['active']]
            for _ in range(n_rows - 1):
                await page.keyboard.press('Tab')
            a2 = [r['name'] for r in await pal_rows() if r['active']]
            await page.keyboard.press('Shift+Tab')
            a3 = [r['name'] for r in await pal_rows() if r['active']]
            ck(n_rows >= 2 and a1 == ['FOOTING'] and a2 == ['FOOTINGSALL'] and a3[0] != 'FOOTINGSALL',
               "Tab moves to the next row and wraps round; Shift+Tab goes back (%s, %s, %s)" % (a1, a2, a3))
            await page.keyboard.press('Control+a')
            await page.keyboard.type('?f8')
            await page.wait_for_timeout(200)
            kr = await pal_rows()
            ck(await pal_heads() == ['Keyboard shortcuts'] and len(kr) == 1 and kr[0]['kbd'] == ['F8'] and kr[0]['alias'] == 'ORTHO',
               "? searches the keyboard shortcuts: ?f8 is the F8 row, which runs ORTHO")
            o0 = await safe("()=>window.__a3dSnapState().ortho")
            await page.keyboard.press('Enter')
            await page.wait_for_timeout(250)
            o1 = await safe("()=>window.__a3dSnapState().ortho")
            ck(o0 is not None and o1 == (not o0) and not await pal_open(), "Enter on it runs ORTHO, as F8 would")
            await safe("()=>window.__a3dRunCmd('bimOrtho')")
            await open_pal('?ctrl')
            ctrl_rows = await pal_rows()
            ck(len(ctrl_rows) >= 5 and all(any(mod in k for k in r['kbd']) for r in ctrl_rows), "?ctrl lists every %s chord (%d)" % (mod, len(ctrl_rows)))
            await page.keyboard.press('Control+a')
            await page.keyboard.type('box')
            await page.wait_for_timeout(200)
            await page.keyboard.press('Enter')
            await page.wait_for_timeout(300)
            dlg = await safe("()=>{var d=document.querySelector('.a3d-dlg .a3d-dlghd');return d?d.textContent:null;}")
            ck(dlg == 'Box parameters', "a ribbon-only tool runs from the search: BOX opens the Box dialog (%s)" % dlg)
            await page.keyboard.press('Escape')
            await page.wait_for_timeout(200)
            await page.mouse.click(1000, 450)
            await page.wait_for_timeout(150)
            await page.keyboard.press('Escape')
            await page.keyboard.press('Enter')
            await page.wait_for_timeout(300)
            dlg2 = await safe("()=>{var d=document.querySelector('.a3d-dlg .a3d-dlghd');return d?d.textContent:null;}")
            ck(dlg2 == 'Box parameters', "and Enter on the drawing repeats it, as it repeats a typed command (%s)" % dlg2)
            await close_all()
            await safe("""()=>{var id=window.__a3dAddSheet('A901','Search probe','ANSI-B-L');window.__a3dOpenSheetView(id);}""")
            await page.wait_for_timeout(300)
            await open_pal('wall')
            wr = [r for r in await pal_rows() if r['name'] == 'WALL']
            await page.keyboard.press('Enter')
            await page.wait_for_timeout(300)
            ck(wr and wr[0]['off'] == 'works on the model, not a sheet' and 'not available here' in await toast(),
               "on a sheet the WALL row says why it cannot run, and Enter says so (%s)" % await toast())
            await safe("()=>window.__a3dSetPlanView()")
            await page.wait_for_timeout(300)

            # ---------------------------------------------------------------------------------
            print("\n-- 5. type anywhere")
            await close_all()
            await page.mouse.click(1000, 450)
            await page.wait_for_timeout(150)
            await page.keyboard.press('Escape')
            await page.keyboard.type('wa')
            await page.wait_for_timeout(200)
            val = await safe("()=>document.querySelector('#a3d-cmdpal input').value")
            ck(await pal_open() and val == 'wa', "letters typed on the drawing open the search, holding them (%r)" % val)
            await page.keyboard.press('Enter')
            await page.wait_for_timeout(300)
            tool = await safe("()=>window.__a3dActiveSketchTool()")
            ck(not await pal_open() and tool == 'wall', "wa, Enter: the wall tool is armed (%s)" % tool)
            await page.keyboard.press('l')
            await page.wait_for_timeout(150)
            ck(not await pal_open(), "while a tool takes points, a letter is the tool's, not the search's")
            await close_all()
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dRefreshProps();var f=document.querySelector('#a3d-propsbody input[type=text],#a3d-propsbody input:not([type])');if(f)f.focus();}")
            infield = await safe("()=>document.activeElement&&document.activeElement.tagName")
            await page.keyboard.type('x')
            await page.wait_for_timeout(150)
            ck(infield == 'INPUT' and not await pal_open(), "in a field, a letter is the field's")
            await close_all()
            await blur()
            await safe("()=>window.__a3dRunAct('box')")
            await page.wait_for_timeout(200)
            await blur()
            await page.keyboard.press('q')
            await page.wait_for_timeout(150)
            ck(not await pal_open() and await safe("()=>!!document.querySelector('.a3d-dlg')"), "with a dialog open, a letter does not open the search")
            await close_all()
            ck(await safe("()=>window.__a3dTypeAnywhere({key:'k',ctrlKey:true,target:document.body})") is False
               and await safe("()=>window.__a3dTypeAnywhere({key:'5',target:document.body})") is False
               and await safe("()=>window.__a3dTypeAnywhere({key:'m',target:document.body})") is True,
               "only a plain letter (or ?) with nothing else listening opens it")

            # ---------------------------------------------------------------------------------
            print("\n-- 6. one search")
            await close_all()
            await safe("()=>document.getElementById('a3d-dsearch').click()")
            await page.wait_for_timeout(250)
            ck(await pal_open() and not await safe("()=>!!document.querySelector('#a3d-dock [data-dockpop=\"__search\"]')"),
               "the dock's magnifier opens the command search; the dock has no search of its own")
            await close_all()
            # AMENDED FOR V129: the dock's native title became a real tooltip (#a3d-tip); the
            # button's accessible name carries the same hint, so that is what is read here
            tips = await safe("""()=>{var o={};['bim:wall','bim:door','s:rect'].forEach(function(a){var b=document.querySelector('#a3d-dock .a3d-dbtn[data-a3dr="'+a+'"]');o[a]=b?b.getAttribute('aria-label'):null;});return o;}""")
            ck(tips and 'type WALL or WA' in (tips.get('bim:wall') or '') and 'type DOOR or DR' in (tips.get('bim:door') or ''),
               "a ribbon button's tooltip names the command to type for it (%s)" % tips)

            # ---------------------------------------------------------------------------------
            print("\n-- 7. the shortcut sheet searches")
            await blur()
            await safe("()=>window.__a3dRunCmd('shortcuts')")
            await page.wait_for_timeout(300)
            foc = await safe("()=>document.activeElement&&document.activeElement.classList.contains('a3d-rkfind')")
            ck(foc, "the sheet opens with its search box ready")

            async def sheet_state():
                return await safe("""()=>{var p=document.getElementById('a3d-rupop');return {open:p.classList.contains('open'),
                  rows:[...p.querySelectorAll('.a3d-rkrow')].filter(r=>r.offsetParent!==null).map(r=>r.querySelector('.a3d-rklab').textContent),
                  grps:[...p.querySelectorAll('.a3d-rkgrp')].filter(g=>g.offsetParent!==null).map(g=>g.textContent),
                  empty:p.querySelector('.a3d-rkempty').offsetParent!==null};}""")
            total = len((await sheet_state())['rows'])
            await page.keyboard.type('undo')
            await page.wait_for_timeout(150)
            s1 = await sheet_state()
            ck('Undo' in s1['rows'] and len(s1['rows']) < total and 'Editing' in s1['grps'] and 'Snaps' not in s1['grps'],
               "'undo' leaves the rows about undoing and their groups, and hides the rest (%s)" % s1['rows'])
            await page.keyboard.press('Control+a')
            await page.keyboard.type('f8')
            await page.wait_for_timeout(150)
            ck((await sheet_state())['rows'] == ['Ortho on or off'], "'f8', the key itself, finds its row")
            await page.keyboard.press('Control+a')
            await page.keyboard.type('cmd+z')
            await page.wait_for_timeout(150)
            ck('Undo' in (await sheet_state())['rows'], "Cmd and Ctrl read as one: cmd+z finds Undo")
            await page.keyboard.press('Control+a')
            await page.keyboard.type('zqzq')
            await page.wait_for_timeout(150)
            s4 = await sheet_state()
            ck(s4['rows'] == [] and s4['empty'], "nothing matching says so")
            await page.keyboard.press('Escape')
            await page.wait_for_timeout(150)
            s5 = await sheet_state()
            ck(s5['open'] and len(s5['rows']) == total, "Escape clears the search first (%d rows back)" % len(s5['rows']))
            await page.keyboard.press('Escape')
            await page.wait_for_timeout(150)
            ck(not (await sheet_state())['open'], "and closes the sheet the second time")
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
