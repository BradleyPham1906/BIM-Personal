"""bim_phase124b_library_save_toast_browser_tests.py -- V124b: the Assets library's save, warned and toasted.

The owner, 2026-10-31 (decision D8 of reference/research-local-storage.md): fix now the library's silent failure.
bimSaveFamilyLibrary only warned to the console when browser storage refused the library, so an asset added to a
full store was gone at the next reload without a word, against the build contract (failures warned and toasted).
What this suite holds the phase to:

  1. A REFUSED SAVE IS SAID. When storage refuses the library, the console has the [BIM] warning and the toast
     says the Assets library could not be saved, that new assets will be lost at a reload, and what to do.
  2. ONCE PER RUN OF FAILURES. A second refused save in the same run raises no second toast, as save3d does.
  3. AND WHEN IT WORKS AGAIN. The first save that works after a failure says so, and the library stored then
     holds every asset added during the failures; a reload brings them back.
  4. NOTHING CHANGES WHEN STORAGE WORKS. An ordinary add raises no library toast and stores the asset.

Storage is made to refuse the library by replacing Storage.prototype.setItem from the page, after the app has
started, for the library's key only (the V115 way); no init script touches storage (the V115 rule). The one init
script here only watches the toast.
"""
import asyncio, pathlib, re, sys, tempfile
from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'
BLANK = pathlib.Path(tempfile.mkdtemp(prefix='v124b_')) / 'blank.html'
BLANK.write_text('<!doctype html><title>blank</title>', encoding='utf-8')

KEY = 'acad3dFamilyLibrary'
FAILED = 'The Assets library could not be saved'
AGAIN = 'Saving the Assets library works again'
MESH = "{v:[0,0,0, 1,0,0, 0,1,0],f:[0,1,2]}"


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
    m = re.search(r"function bimSaveFamilyLibrary\(\)\{(.*?)\n  \}\n", code, flags=re.S)
    body = m.group(1) if m else ''
    ck(bool(m), 'bimSaveFamilyLibrary is found')
    ck("a3dToast('" + FAILED in body, 'its failure branch toasts')
    ck('console.warn(' in body, 'and still warns to the console')
    ck(body.count('return true;') == 1 and body.count('return false;') == 1,
       'it returns whether the library was stored')
    ck(code.count('A3D_FAMLIB_SAVE_FAILED=true') == 1 and code.count('A3D_FAMLIB_SAVE_FAILED=false') == 2,
       'one flag marks a run of failures: set once, cleared at the declaration and on a working save')


async def main():
    ck = Checks()
    t = HTML.read_text(encoding='utf-8')
    ck('__acad3dV124b' in t, 'the V124b marker is present')
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
        await page.add_init_script("""(function(){window.__v124bToasts=[];
            new MutationObserver(function(){var t=document.getElementById('a3d-toast');
              if(t&&t.textContent&&window.__v124bToasts[window.__v124bToasts.length-1]!==t.textContent)window.__v124bToasts.push(t.textContent);})
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
                if await safe("()=>!!(window.__a3dOn&&window.__a3dFamilyAdd&&window.__a3dLibrary)"):
                    break
                await page.wait_for_timeout(100)
            await page.wait_for_timeout(600)

        async def toasts_with(s):
            ts = await safe("()=>window.__v124bToasts") or []
            return [x for x in ts if s in x]

        async def clear_toasts():
            await safe("()=>{window.__v124bToasts=[];var t=document.getElementById('a3d-toast');if(t)t.textContent='';}")

        async def add(name):
            return await safe("(n)=>{var e=window.__a3dFamilyAdd({name:n,category:'Site',mesh:" + MESH + "});return e?e.id:null;}", name)

        async def stored_ids():
            return await safe("(k)=>{try{return JSON.parse(localStorage.getItem(k)||'[]').map(function(e){return e.id;});}catch(e){return null;}}", KEY) or []

        print('\n-- 1. a fresh start: storage works, an ordinary add is stored without a library toast')
        await page.goto('file://' + str(BLANK))
        await safe("()=>localStorage.clear()")
        await open_app()
        await clear_toasts()
        a = await add('V124b first')
        await page.wait_for_timeout(300)
        ck(a and a in await stored_ids(), 'the first asset is in the stored library (%s)' % a)
        ck(not await toasts_with(FAILED) and not await toasts_with(AGAIN), 'and no library toast was raised')

        print('\n-- 2. storage refuses the library: warned and toasted')
        await safe("""(k)=>{window.__v124bRealSet=Storage.prototype.setItem;
            Storage.prototype.setItem=function(key,v){if(key===k){var e=new Error('full');e.name='QuotaExceededError';throw e;}
              return window.__v124bRealSet.call(this,key,v);};}""", KEY)
        nwarn = len(warns)
        await clear_toasts()
        b = await add('V124b second')
        await page.wait_for_timeout(300)
        failed = await toasts_with(FAILED)
        ck(b is not None, 'the asset is still added to the library on screen (%s)' % b)
        ck(len(failed) >= 1, 'the toast says the Assets library could not be saved (%s)' % (await safe("()=>window.__v124bToasts")))
        ck(failed and 'lost when the page reloads' in failed[-1], 'and that new assets will be lost at a reload')
        ck(failed and 'remove assets you no longer need' in failed[-1], 'and what to do about it')
        ck(any('persist family library' in w for w in warns[nwarn:]), 'the console has the [BIM] warning')
        ck(b not in await stored_ids(), 'and the stored library does not have it (the failure was real)')

        print('\n-- 3. a second refused save in the same run: no second toast')
        await clear_toasts()
        c = await add('V124b third')
        await page.wait_for_timeout(300)
        ck(c is not None and not await toasts_with(FAILED), 'no toast for the second failure (%s)' % (await safe("()=>window.__v124bToasts")))

        print('\n-- 4. storage works again: said once, and the library stored holds everything')
        await safe("()=>{Storage.prototype.setItem=window.__v124bRealSet;}")
        await clear_toasts()
        d = await add('V124b fourth')
        await page.wait_for_timeout(300)
        ck(len(await toasts_with(AGAIN)) == 1, 'the toast says saving the library works again')
        ids = await stored_ids()
        ck(all(x in ids for x in (a, b, c, d)), 'the stored library holds the four assets, those of the failures too')
        await clear_toasts()
        e = await add('V124b fifth')
        await page.wait_for_timeout(300)
        ck(not await toasts_with(AGAIN) and not await toasts_with(FAILED), 'the next working save raises no toast')

        print('\n-- 5. a reload brings them back')
        await open_app()
        lib = await safe("()=>window.__a3dLibrary().map(function(r){return r.id;})") or []
        ck(all(x in lib for x in (a, b, c, d, e)), 'the five assets are in the library after a reload')
        ck(errs == [], 'no page errors (%s)' % errs[:3])
        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
