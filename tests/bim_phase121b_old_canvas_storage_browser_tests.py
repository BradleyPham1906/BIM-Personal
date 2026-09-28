"""bim_phase121b_old_canvas_storage_browser_tests.py -- V121b: the old canvas's saved data, cleared.

The owner, on V120's note that the browser may still hold the old canvas's saved data: "No i want to
clear them up". What this suite holds the phase to, asserted on browser storage itself:

  1. EXACTLY THE OLD CANVAS'S ENTRIES GO. The seven names the whiteboard wrote -- found in every build
     from V87 to V113c -- are removed when the app starts, and nothing else is: not another page's
     entry (a page opened from disk shares storage with every other page opened from disk), and not
     one of the app's own. The model saved before the start is the model after it.
  2. THE INTERFACE THEME IS THE APP'S OWN, AND IT PERSISTS. The Appearance menu wrote canvas-theme,
     which nothing had read since V114, so a light interface went dark on every reload. It is kept as
     acad3dTheme now and put back at every start; a value still under canvas-theme is carried over
     once and the old name removed.

Stored state is written from a blank page on the same file:// origin with the app closed; no init
script touches storage (the V115 rule). The one init script here only watches the toast.
"""
import asyncio, pathlib, re, sys, tempfile
from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'
BLANK = pathlib.Path(tempfile.mkdtemp(prefix='v121b_')) / 'blank.html'
BLANK.write_text('<!doctype html><title>blank</title>', encoding='utf-8')

# what the whiteboard wrote, read out of the V87 and V113c builds (LS_KEY, LEGACY_KEYS, DKEY, LKEY,
# and the literal names) -- the evidence the phase's list is held to
OLD = ['obsidian-canvas-enhanced-v6', 'obsidian-canvas-enhanced-v5', 'acadDrawingsV1', 'acadLayoutsV1',
       'acadBlocksV1', 'acadDockV1', 'canvas-grid']
APP = ['acad3dV1', 'acad3dDocsV1', 'acad3dDocV1:', 'acad3dFamilyLibrary', 'acad3dUIPrefs', 'acad3dTheme']
OTHER = ('another-page-on-disk', 'keep me')


class Checks:
    def __init__(self):
        self.n, self.bad = 0, []

    def __call__(self, cond, msg):
        self.n += 1
        if not cond:
            self.bad.append(msg)
        print(('  ok    ' if cond else '  FAIL  ') + msg)


def static_checks(ck, t):
    code = re.sub(r'/\*.*?\*/', '', t, flags=re.S)
    print('\n-- 0. the file')
    m = re.search(r"var A3D_CANVAS_KEYS=\[([^\]]*)\]", code)
    names = re.findall(r"'([^']+)'", m.group(1)) if m else None
    ck(names == OLD, 'the list removed at start is exactly the whiteboard\'s seven entries (%s)' % names)
    else_where = [k for k in OLD if code.count(k) != 1]
    ck(else_where == [], 'and no other code reads or writes any of them (%s)' % else_where)
    ck(names is not None and not [a for a in APP if any(a in n for n in names)], 'none of the app\'s own keys is in it')
    ck('localStorage.clear(' not in code and not re.search(r'removeItem\(\s*localStorage\.key\(', code),
       'nothing clears storage wholesale or by pattern')
    ck(not re.search(r"setItem\(\s*'canvas-theme'", code) and code.count("'canvas-theme'") == 2,
       'canvas-theme is only read and removed, in the carry-over, never written')


async def main():
    ck = Checks()
    t = HTML.read_text(encoding='utf-8')
    ck('__acad3dV121b' in t, 'the V121b marker is present')
    if not ck.bad:
        try:
            static_checks(ck, t)
        except Exception as e:
            ck(False, 'the static checks ran to the end (stopped by %s: %s)' % (type(e).__name__, str(e)[:160]))
        try:
            await drive(ck)
        except Exception as e:
            ck(False, 'the suite ran to the end (stopped by %s: %s)' % (type(e).__name__, str(e).splitlines()[0][:200]))
    print('\n%d/%d checks passed' % (ck.n - len(ck.bad), ck.n))
    print('RESULT: ' + ('PASS' if not ck.bad else 'FAIL'))
    sys.exit(1 if ck.bad else 0)


async def drive(ck):
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1600, 'height': 950})
        page = await ctx.new_page()
        page.set_default_timeout(6000)
        errs, warns = [], []
        page.on('pageerror', lambda e: errs.append(str(e)[:200]))
        page.on('console', lambda m: warns.append(m.text[:200]) if m.type == 'warning' and m.text.startswith('[BIM]') else None)
        # the toast is watched, not storage: every text the toast shows is kept
        await page.add_init_script("""(function(){window.__v121bToasts=[];
            new MutationObserver(function(){var t=document.getElementById('a3d-toast');
              if(t&&t.textContent&&window.__v121bToasts[window.__v121bToasts.length-1]!==t.textContent)window.__v121bToasts.push(t.textContent);})
            .observe(document,{subtree:true,childList:true,characterData:true});})();""")
        ev = page.evaluate

        async def safe(js, arg=None):
            try:
                return await (ev(js, arg) if arg is not None else ev(js))
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:200])
                return None

        async def open_app():
            await page.goto('file://' + str(HTML))
            for _ in range(60):
                if await safe("()=>!!(window.__a3dOn&&window.__a3dCanvasCleared)"):
                    break
                await page.wait_for_timeout(100)
            await page.wait_for_timeout(600)

        async def store():
            return await safe("()=>{var o={},i,k;for(i=0;i<localStorage.length;i++){k=localStorage.key(i);o[k]=localStorage.getItem(k);}return o;}") or {}

        # ------------------------------------------------------------------------------------------
        print('\n-- 1. a first session saves a model')
        await page.goto('file://' + str(BLANK))
        await safe("()=>localStorage.clear()")
        await open_app()
        wall = await safe("()=>window.__a3dWall([[0,0],[6,0]],0.3,3,'center',false)")
        await page.wait_for_timeout(900)
        s0 = await store()
        ck(wall and 'acad3dV1' in s0 and wall in s0.get('acad3dV1', ''), 'the wall is saved in acad3dV1 (%s)' % sorted(s0))
        app_before = {k: v for k, v in s0.items() if k.startswith('acad3d')}

        print('\n-- 2. with the app closed, the old canvas\'s entries are put back, beside another page\'s')
        await page.goto('file://' + str(BLANK))
        seeded = await safe("""(a)=>{a.old.forEach(function(k){localStorage.setItem(k,'{"from":"the old canvas"}');});
            localStorage.setItem('canvas-theme','light');localStorage.removeItem('acad3dTheme');
            localStorage.setItem(a.other[0],a.other[1]);return localStorage.length;}""", {'old': OLD, 'other': list(OTHER)})
        ck(seeded and seeded >= len(OLD) + 2, 'seeded from a blank page on the same origin (%s entries)' % seeded)

        print('\n-- 3. the next start removes them, and only them')
        await open_app()
        cl = await safe("()=>window.__a3dCanvasCleared()") or {}
        s1 = await store()
        ck(cl.get('removed') == OLD, 'the start removed the seven entries (%s)' % cl.get('removed'))
        ck(not [k for k in OLD if k in s1], 'and none of them is in storage (%s)' % [k for k in OLD if k in s1])
        ck(s1.get(OTHER[0]) == OTHER[1], 'another page\'s entry is untouched (%r)' % s1.get(OTHER[0]))
        lost = [k for k in app_before if k not in s1]
        ck(lost == [], 'every one of the app\'s own entries is still there (%s lost)' % lost)
        objs = await safe("()=>window.__a3dObjects().map(function(o){return o.id;})") or []
        ck(wall in objs, 'and the model is the one saved before: the wall is in it (%d objects)' % len(objs))
        toasts = await safe("()=>window.__v121bToasts") or []
        ck(any("Removed the old canvas's saved data from this browser (7 entries)" in x for x in toasts),
           'the start says what it removed (%s)' % [x for x in toasts if 'old canvas' in x][:1])
        th = await safe("()=>({cls:document.body.classList.contains('light-theme'),at:window.__a3dThemeAtStart(),"
                        "k:localStorage.getItem('acad3dTheme'),old:localStorage.getItem('canvas-theme')})") or {}
        ck(th.get('cls') is True and th.get('at') == 'light' and th.get('k') == 'light' and th.get('old') is None,
           'the light interface saved under canvas-theme is carried over to acad3dTheme, and the old name removed (%s)' % th)

        print('\n-- 4. a start with nothing left to remove removes nothing, and keeps the theme')
        await page.reload()
        for _ in range(60):
            if await safe("()=>!!(window.__a3dOn&&window.__a3dCanvasCleared)"):
                break
            await page.wait_for_timeout(100)
        await page.wait_for_timeout(600)
        cl = await safe("()=>window.__a3dCanvasCleared()") or {}
        toasts = await safe("()=>window.__v121bToasts") or []
        light = await safe("()=>document.body.classList.contains('light-theme')")
        ck(cl.get('removed') == [] and not any('old canvas' in x for x in toasts), 'nothing removed and nothing said (%s)' % cl.get('removed'))
        ck(light is True, 'and the light interface comes back from the app\'s own key')

        print('\n-- 5. the Appearance menu keeps the choice under the app\'s own name')
        await page.mouse.move(900, 500)
        await page.click('[data-a3drumenu="appear"]')
        await page.wait_for_timeout(200)
        await page.click('[data-a3druitem="appear:dark"]')
        await page.wait_for_timeout(250)
        st = await safe("()=>({k:localStorage.getItem('acad3dTheme'),old:localStorage.getItem('canvas-theme'),"
                        "cls:document.body.classList.contains('light-theme')})") or {}
        ck(st.get('k') == 'dark' and st.get('old') is None and st.get('cls') is False,
           'Dark in the Appearance menu is saved as acad3dTheme, and canvas-theme is not written (%s)' % st)
        await page.reload()
        for _ in range(60):
            if await safe("()=>!!(window.__a3dOn&&window.__a3dThemeAtStart)"):
                break
            await page.wait_for_timeout(100)
        await page.wait_for_timeout(400)
        dark = await safe("()=>[document.body.classList.contains('light-theme'),window.__a3dThemeAtStart()]")
        ck(dark == [False, 'dark'], 'and the next start puts Dark back (%s)' % dark)

        print('\n-- 6. no errors')
        ck(errs == [], 'no page errors (%s)' % errs[:3])
        bad = [w for w in warns if 'could not' in w or 'failed' in w]
        ck(bad == [], 'no [BIM] warning of a failure (%s)' % bad[:3])
        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
