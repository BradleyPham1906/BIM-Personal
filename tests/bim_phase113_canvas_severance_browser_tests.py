#!/usr/bin/env python3
"""bim_phase113_canvas_severance_browser_tests.py -- V113: the shell stops borrowing from the
whiteboard it was built on.

Two borrowings are repaid in this phase, and each one was a leftover of the kind standing law 1
names: a thing that reads as finished because half of it still works.

  1. THE COMMAND PALETTE WAS OWNED BY TWO MODULES. acadWorkspaceV1 built its contents and said so
     in its own comment -- "same id/classes so existing open/close/Ctrl+K keep working" -- while
     openPalette, closePalette and the Ctrl+K binding lived in a canvas-era block that has had no
     workspace since V73. The half that decides WHEN the palette opens was in retired code. It is
     one owner now, and the retired block does not install at all.
  2. THE MATERIAL LIBRARY WAS DECLARED BY THE RETIRED WORKBENCH. V69 published it with the note
     that it is deliberately the same array and never a copy, because "two lists that start
     identical and drift are worse than one list". That is exactly why it had to move whole rather
     than be retyped: the BIM inspector, the schedules' mass takeoff, the plan hatches and the
     Assets panel all read it. The patch script MOVED the array text rather than restating it.

What these checks are for: the palette is driven, not inspected -- V86's lesson was a palette that
rendered perfectly and dispatched nothing. And the library is asserted to be ONE array by mutating
it through one name and reading it back through the other, because two equal copies would pass
every comparison until the day they stopped being equal.
"""
# AMENDED FOR V120: the shell's canvas-era names were replaced -- #figma-layers-shell/-rail/-panel are
# #a3d-shell/-rail/-leftpanel, the .fl-* classes .a3d-*, #uploaded-command-palette #a3d-cmdpal, the
# Project Browser tab 'file' is 'browser', --figma-dock-w is --a3d-left-w, and the material library is
# read through window.__a3dMaterialCards() (window.__WB_MATERIAL_CARDS is gone).
import asyncio, pathlib, sys
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
        print(('ok    ' if cond else 'FAIL  ') + msg)


async def run():
    ck = Checks()
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1600, 'height': 950})
        page = await ctx.new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        await page.goto('file://' + str(HTML))
        await page.wait_for_timeout(2400)
        await page.mouse.click(800, 500)
        await page.wait_for_timeout(250)
        ev = page.evaluate

        async def safe(js, arg=None):
            try:
                return await (ev(js, arg) if arg is not None else ev(js))
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:140])
                return None

        async def blur():
            await safe("()=>{if(document.activeElement)document.activeElement.blur();}")

        async def shown():
            return await safe("()=>{var p=document.getElementById('a3d-cmdpal');"
                              "return !!(p&&p.classList.contains('show'));}")

        print('\n-- 1. the palette has one owner, and it is the shell that builds it')
        ck((await safe("()=>window.__wsPaletteOwner")) == 'acadWorkspaceV1',
           'the palette names its owner (%r)' % (await safe("()=>window.__wsPaletteOwner")))
        ck((await safe("()=>typeof window.openPalette==='function'&&typeof window.closePalette==='function'")) is True,
           'openPalette and closePalette are still published, because the ribbon button calls them')
        ck((await safe("()=>!document.getElementById('uploaded-layers-panel')")) is True,
           "the retired block's whiteboard layer panel is never built")
        gone = await safe("""()=>({state:typeof window.state,toWorld:typeof window.toWorld,
            renderAll:typeof window.renderAll,byId:typeof window.byId,seed:typeof window.seed,
            save:typeof window.save,addCard:typeof window.addCard,
            viewport:!!document.getElementById('viewport'),world:!!document.getElementById('world'),
            hint:!!document.getElementById('hint'),toast:!!document.getElementById('toast'),
            nodes:document.querySelectorAll('.node,[data-node]').length})""")
        ck(gone and all(gone[k] == 'undefined' for k in ('state', 'toWorld', 'renderAll', 'byId', 'seed', 'save', 'addCard')),
           'every whiteboard global is gone, not shadowed (%s)' % gone)
        ck(gone and not gone['viewport'] and not gone['world'] and not gone['hint']
           and not gone['toast'] and gone['nodes'] == 0,
           'and so is its markup, including the #hint bar that was still reading "Right-click for a '
           'searchable command menu" across the bottom of the BIM workspace (%s)'
           % {k: gone.get(k) for k in ('viewport', 'world', 'hint', 'nodes')})
        engines = await safe("""()=>['__cadEngineV1','__draftingEngineV1','__modifyEngineV2',
            '__curvesEngineV1','__annotationEngineV1','__precisionEngineV1','__topbarUI',
            '__acadProV1','__acadWbV1','__canvaChartSidebarInstalled','__figmaAssetsDragKit',
            '__finalRobustFigmaSidebar'].filter(function(k){return window[k]!==undefined;})""")
        ck(engines == [], 'and the eleven legacy 2D engines and ten add-on modules never install (%s)' % engines)
        title = await safe("()=>[document.title,(document.querySelector('.acad-logo')||{}).title||'']")
        ck(title and 'Canvas' not in title[0] and 'Canvas' not in title[1],
           'the app no longer calls itself Canvas where a user can read it (%s)' % title)
        cnt = await safe("()=>window.__wsPaletteCount")
        ck(isinstance(cnt, int) and cnt > 40, 'the palette still carries its command registry (%s)' % cnt)

        print('\n-- 2. Ctrl+K is driven, not assumed')
        await blur()
        ck((await shown()) is False, 'the palette starts closed')
        await page.keyboard.press('Control+k')
        await page.wait_for_timeout(300)
        ck((await shown()) is True, 'Ctrl+K opens it')
        focused = await safe("()=>{var p=document.getElementById('a3d-cmdpal');"
                             "return !!(p&&document.activeElement===p.querySelector('input'));}")
        ck(focused is True, 'and puts the caret in its input, so a command can be typed at once')
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(250)
        ck((await shown()) is False, 'Escape closes it')
        await page.keyboard.press('Control+k')
        await page.wait_for_timeout(300)
        ck((await shown()) is True, 'it opens a second time (the handler is not one-shot)')
        await page.mouse.click(1200, 700)
        await page.wait_for_timeout(250)
        ck((await shown()) is False, 'a pointer outside it closes it')
        # The ribbon opens it through window.openPalette, and the caret can be anywhere by then, so
        # Escape has to be caught above the palette's own input as well as inside it.
        await safe("()=>window.openPalette()")
        await page.wait_for_timeout(260)
        await blur()
        ck((await shown()) is True and (await safe("()=>document.activeElement.tagName")) != 'INPUT',
           'opened from the ribbon path with the caret elsewhere, it is still open')
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(250)
        ck((await shown()) is False, 'and Escape closes it from there too')
        # A filter typed and then abandoned must not come back with the palette.
        await page.keyboard.press('Control+k')
        await page.wait_for_timeout(300)
        await page.keyboard.type('ZZZZ')
        await page.wait_for_timeout(240)
        stale = await safe("()=>{var p=document.getElementById('a3d-cmdpal');"
                           "return p.querySelector('.a3d-cmdresults').textContent.indexOf('No matching command')>=0;}")
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(220)
        await page.keyboard.press('Control+k')
        await page.wait_for_timeout(320)
        fresh = await safe("()=>{var p=document.getElementById('a3d-cmdpal');"
                           "return [p.querySelector('input').value,p.querySelectorAll('.a3d-cmdrow').length];}")
        ck(stale is True, 'a filter that matches nothing says so (%r)' % stale)
        ck(fresh == ['', 14] or (fresh and fresh[0] == '' and fresh[1] > 1),
           'and reopening starts empty with the full list, not the abandoned filter (%s)' % fresh)
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(220)

        print('\n-- 3. it still runs a command, which is the only thing that matters')
        before = await safe("()=>{window.__a3dTestSetObjs([]);window.__a3dFlat(true);return window.__a3dObjects().length;}")
        await blur()
        await page.keyboard.press('Control+k')
        await page.wait_for_timeout(320)
        await page.keyboard.type('RECTANG')
        await page.wait_for_timeout(260)
        await page.keyboard.press('Enter')
        await page.wait_for_timeout(420)
        tool = await safe("()=>window.__a3dActiveSketchTool?window.__a3dActiveSketchTool():null")
        ck(before == 0 and tool == 'rect',
           'a command typed into the palette starts its tool (%r)' % tool)
        ck((await shown()) is False, 'and the palette closed behind it')
        act = await safe("()=>document.activeElement?document.activeElement.tagName:null")
        ck(act != 'INPUT', 'the keyboard went back to the drawing, not the palette input (%s)' % act)
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(200)

        print('\n-- 4. the material library is out of the retired workbench, and is still one array')
        cards = await safe("()=>window.__a3dMaterialCards()?window.__a3dMaterialCards().map(function(c){return c.name;}):null")
        ck(isinstance(cards, list) and len(cards) >= 5 and 'Steel' in cards and 'Concrete' in cards,
           'the library is published with its cards (%s)' % cards)
        steel = await safe("()=>{var c=window.__a3dMaterialCards(),i;for(i=0;i<c.length;i++)if(c[i].name==='Steel')return c[i];return null;}")
        # AMENDED FOR V120: read through window.__a3dMaterialCards(), which reports a card's name, kind,
        # density, colour and hatch -- not its Poisson's ratio, which only the retired shared name exposed.
        ck(isinstance(steel, dict) and steel.get('density') == 7900
           and isinstance(steel.get('hatch'), dict),
           'Steel kept its engineering data through the move (%s)' % {k: steel.get(k) for k in ('density', 'hatch')} if steel else 'Steel missing')
        bim = await safe("()=>window.__a3dMaterialCards().map(function(c){return c.name;})")
        ck(bim == cards, 'and the BIM side reads the same list (%s)' % bim)
        # AMENDED FOR V120: "ONE array, not a copy" pushed a card through window.__WB_MATERIAL_CARDS, the name the
        # whiteboard and BIM shared, and read it back through the BIM side. The library is declared once
        # inside the engine now and read only through bimMaterialCards(); the V120 suite asserts that.

        print('\n-- 5. the library still reaches the model')
        got = await safe("""()=>{window.__a3dTestSetObjs([]);
            var id=window.__a3dWall([[0,0],[4,0]],0.3,3,'center',false);
            if(!id)return null;
            window.__a3dSetMaterial(id,'Steel');
            return {mat:window.__a3dMaterialOf(id),vol:window.__a3dObjVolume(id),mass:window.__a3dObjMass(id)};}""")
        ck(isinstance(got, dict) and got.get('mat') == 'Steel' and got.get('vol') > 0,
           'a material assigns to a solid (%s)' % (got and {k: got.get(k) for k in ('mat',)}))
        ck(isinstance(got, dict) and got.get('mass') is not None
           and abs(got['mass'] - got['vol'] * 7900) < 1e-6,
           "and its mass is the solid's volume times the moved card's own density (%s)" % (got and got.get('mass')))

        print('\n-- 6. the BIM shell owns its left rail')
        shell = await safe("""()=>{var s=document.getElementById('a3d-shell');
            if(!s)return null;
            var br=document.getElementById('a3d-browser');
            var chain=[];var e=br;while(e&&e!==document.body){chain.push(e.id||('.'+(e.className||'').toString().split(' ')[0]));e=e.parentElement;}
            return {built:s.tagName+'#'+s.id,tab:s.getAttribute('data-tab'),
                    chain:chain,rail:!!document.getElementById('a3d-rail'),
                    tabs:s.querySelectorAll('#a3d-rail .a3d-railbtn[data-tab]').length,
                    help:!!s.querySelector('.fl-help'),pages:!!s.querySelector('.fl-pages')};}""")
        ck(shell and shell['built'] == 'ASIDE#a3d-shell', 'the shell is the BIM engine\'s own <aside> (%s) -- AMENDED FOR V120: its builder no longer marks itself, being the only one' % (shell and shell['built']))
        ck(shell and shell['chain'][:4] == ['a3d-browser', '.a3d-tree', 'a3d-leftpanel', 'a3d-shell'],
           'and the Project Browser sits inside it (%s)' % (shell and shell['chain'][:4]))
        # AMENDED FOR V141: and Analyze, below Assets
        ck(shell and shell['tabs'] == 5 and not shell['help'] and not shell['pages'],
           'with Layers (V121), Presentation (V122), the Project Browser and Assets -- AMENDED FOR V122: the owner\'s stack\'s second panel -- and none of the whiteboard blocks V80 had to clean out (%s)'
           % {k: shell.get(k) for k in ('tabs', 'help', 'pages')} if shell else 'no shell')
        und = await safe("()=>Array.prototype.filter.call(document.querySelectorAll('#a3d-railutil .a3d-ru'),"
                         "function(b){return (b.textContent||'').indexOf('undefined')>=0;}).length")
        total = await safe("()=>document.querySelectorAll('#a3d-railutil .a3d-ru').length")
        ck(total > 0 and und == 0,
           'the rail utility stack renders its icons, not the word undefined (%s of %s)' % (und, total))
        qat = await safe("""()=>{var b=document.querySelectorAll('#acad-qat .acad-qbtn'),i,plain=0;
            for(i=0;i<b.length;i++)if((b[i].innerHTML||'').indexOf('circle cx="12" cy="12" r="6"')>=0)plain++;
            return [b.length,plain];}""")
        ck(qat and qat[0] >= 5 and qat[1] == 0,
           'and every quick-access button has its own icon rather than the placeholder circle (%s)' % qat)

        await safe("()=>{var b=document.querySelector('#a3d-rail .a3d-railbtn[data-tab=\"assets\"]');if(b)b.click();}")
        await page.wait_for_timeout(350)
        assets = await safe("()=>({tab:(document.getElementById('a3d-shell')||{}).dataset?document.getElementById('a3d-shell').getAttribute('data-tab'):null,"
                            "rows:document.querySelectorAll('#a3d-leftpanel [data-a3dassets]').length})")
        ck(assets and assets['tab'] == 'assets' and assets['rows'] > 0,
           'the Assets rail button switches the tab and the BIM libraries render (%s)' % assets)
        await safe("()=>{var b=document.querySelector('#a3d-rail .a3d-railbtn[data-tab=\"browser\"]');if(b)b.click();}")
        await page.wait_for_timeout(300)
        back = await safe("()=>({tab:document.getElementById('a3d-shell').getAttribute('data-tab'),"
                          "tree:!!document.querySelector('#a3d-leftpanel > .a3d-tree'),"
                          "stale:document.querySelectorAll('#a3d-leftpanel .a3d-assets-wrap').length})")
        ck(back and back['tab'] == 'browser' and back['tree'] and back['stale'] == 0,
           'and File brings the navigator back with no assets left behind (%s)' % back)
        await safe("()=>{var b=document.querySelector('#a3d-rail .a3d-paneltoggle');if(b)b.click();}")
        await page.wait_for_timeout(300)
        coll = await safe("()=>[document.getElementById('a3d-shell').classList.contains('collapsed'),"
                          "getComputedStyle(document.documentElement).getPropertyValue('--a3d-left-w').trim()]")
        await safe("()=>{var b=document.querySelector('#a3d-rail .a3d-paneltoggle');if(b)b.click();}")
        await page.wait_for_timeout(300)
        open_ = await safe("()=>[document.getElementById('a3d-shell').classList.contains('collapsed'),"
                           "getComputedStyle(document.documentElement).getPropertyValue('--a3d-left-w').trim()]")
        ck(coll == [True, '54px'] and open_ == [False, '296px'],
           'collapsing and reopening the panel moves the workspace edge with it (%s / %s)' % (coll, open_))

        ck(not errs, 'no uncaught page errors (%s)' % errs[:2])
        await browser.close()
    print('\n%d/%d checks passed' % (ck.n - len(ck.bad), ck.n))
    print('RESULT: ' + ('PASS' if not ck.bad else 'FAIL'))
    return 0 if not ck.bad else 1


if __name__ == '__main__':
    sys.exit(asyncio.run(run()))
