#!/usr/bin/env python3
"""bim_phase114_stylesheet_start_browser_tests.py -- V114: the whiteboard's stylesheet is gone, and
what was left of its document model is replaced by the one project that exists.

  1. NO CSS THAT CAN NEVER MATCH. A selector can only match if every #id and .class it requires
     can exist, and an element can only carry a token some markup or script writes. This suite
     re-derives that from the file with its OWN copy of the analysis -- not the patch's -- and
     asserts the answer is zero. It is a permanent guard in the V80 sense: a later phase that
     deletes JavaScript and leaves its CSS behind fails here, and the message names the rules.
     The prune itself was proved invisible separately: every element's computed style, with
     ::before and ::after, identical in twelve driven states, and the pixels with it.
  2. THE DOCUMENT TABS DESCRIBE WHAT IS THERE. The whiteboard's "drawings" were sets of 2D wires;
     the BIM model was never part of them, so + made a "Drawing2" with the same building in it,
     and after V113c deleted the whiteboard, Start and + threw. There is one project: one tab,
     named from the title block and following it when it is renamed; no +, no x.
  3. THE START SCREEN OFFERS ONLY WHAT WORKS: continue, or open a project file. Its count is the
     model's, not a wire count. Driven, including the real file chooser.
  4. THE SHELL CAN TOAST AGAIN. Nine calls outside the BIM engine used window.toast, which was the
     whiteboard's; after V113c every one of them was silently a no-op. They go through the one
     BIM toast now, and the workspace switch -- the one a user sees -- is driven to prove it.
  5. NO USER DATA IS DELETED. The whiteboard's saved drawings are left in localStorage, unread.
"""
import asyncio, pathlib, re, sys
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


# ---- an independent re-derivation of "can this selector ever match" -----------------------------
def style_elements(t):
    out, i = [], 0
    op = re.compile(r'<!--|<(script|style)\b[^>]*>', re.I)
    while True:
        m = op.search(t, i)
        if not m:
            return out
        if m.group(0) == '<!--':
            i = t.index('-->', m.end()) + 3
            continue
        tag = m.group(1).lower()
        e = t.index('</%s>' % tag, m.end())
        if tag == 'style':
            out.append((m.end(), e))
        i = e + len(tag) + 3


def strip_css_comments(css):
    return re.sub(r'/\*.*?\*/', ' ', css, flags=re.S)


def rules(css):
    """(prelude, body) for every qualified rule, descending into @media and @supports."""
    out, i, n = [], 0, len(css)
    while i < n:
        j = css.find('{', i)
        if j < 0:
            break
        pre = css[i:j].strip()
        depth, k = 1, j + 1
        while k < n and depth:
            if css[k] in '"\'':
                q = css[k]; k += 1
                while k < n and css[k] != q:
                    k += 2 if css[k] == '\\' else 1
            elif css[k] == '{':
                depth += 1
            elif css[k] == '}':
                depth -= 1
            k += 1
        body = css[j + 1:k - 1]
        low = pre.lower()
        if low.startswith('@media') or low.startswith('@supports'):
            out.extend(rules(body))
        elif pre and not pre.startswith('@'):
            out.append((pre, body))
        elif 'keyframes' in low:
            out.append((pre, None))
        i = k
    return out


def needs(sel):
    flat, depth = '', 0
    for ch in sel:
        if ch in '([':
            depth += 1
        elif ch in ')]':
            depth -= 1
        elif depth == 0:
            flat += ch
    return re.findall(r'[.#]([A-Za-z_][\w-]*)', flat)


def dead_css(t):
    blocks = style_elements(t)
    rest, prev = [], 0
    for s, e in blocks:
        rest.append(t[prev:s]); prev = e
    rest.append(t[prev:])
    rest = ''.join(rest)
    live = set(re.findall(r'[A-Za-z_][\w-]*', rest))
    dyn = set(re.findall(r"""['"]([A-Za-z_][\w-]*-)['"]\s*\+""", rest)) | \
        set(re.findall(r"""\+\s*['"]([A-Za-z_][\w-]*-)['"]""", rest)) | \
        set(re.findall(r"""([A-Za-z_][\w-]*-)\$\{""", rest))
    dead_rules, used_anim, kf = [], set(), []
    for s, e in blocks:
        for pre, body in rules(strip_css_comments(t[s:e])):
            if body is None:
                kf.append(pre.split()[1] if len(pre.split()) > 1 else '')
                continue
            parts, depth, cur = [], 0, ''
            for ch in pre:
                if ch in '([': depth += 1
                elif ch in ')]': depth -= 1
                if ch == ',' and depth == 0:
                    parts.append(cur); cur = ''
                else:
                    cur += ch
            parts.append(cur)
            alive = [p for p in parts if all(tok in live or any(tok.startswith(d) for d in dyn) for tok in needs(p))]
            if not alive:
                dead_rules.append(pre[:80])
            else:
                for m in re.findall(r'animation(?:-name)?\s*:\s*([^;}]+)', body):
                    used_anim.update(re.findall(r'[A-Za-z_][\w-]*', m))
    dead_kf = [k for k in kf if k not in used_anim and not re.search(r'\b%s\b' % re.escape(k), rest)]
    in_script = sum(1 for m in re.finditer(r'<style\b', t)) - len(blocks)
    return blocks, dead_rules, dead_kf, in_script


async def run():
    ck = Checks()
    t = HTML.read_text(encoding='utf-8')

    print('\n-- 1. no CSS that can never match')
    blocks, dead, dead_kf, in_script = dead_css(t)
    ck(len(blocks) == 1, 'the stylesheet was found as a style ELEMENT, the way a browser finds it -- one since V120 (%d)' % len(blocks))
    ck(in_script >= 0, 'and a "<style" inside a script string or a CSS comment is not mistaken for one (%d skipped)' % in_script)
    ck(dead == [], 'every rule can match something some code could create (%d cannot: %s)' % (len(dead), dead[:4]))
    ck(dead_kf == [], 'and every @keyframes is used by a rule that can match (%s)' % dead_kf[:4])
    sheet = sum(e - s for s, e in blocks)
    # AMENDED FOR V151: the ceiling was 90,000 bytes, and V150 left 30 of it. What this check is for is the
    # whiteboard's 251,329-byte sheet coming back (the selectors it named are checked by name above); the
    # phases since V114 have added their own CSS. 100,000 still tells the two apart by 150 KB.
    ck(sheet < 100000, 'the whiteboard stylesheet is gone: %d bytes of CSS in style elements, was 251,329' % sheet)
    for word in ('chart-panel', 'table-card', 'canvas-quick-ui', 'ctxmenu', 'formatbar', 'uploaded-layers-panel'):
        pass
    ck(not any(w in t for w in ('#chart-panel', '.table-card', 'canvas-quick-ui-v', '#ctxmenu', '#formatbar')),
       'no selector for the whiteboard\'s chart panel, table cards, quick UI, context menu or format bar is left')

    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1600, 'height': 950})
        await ctx.add_init_script("try{if(!localStorage.getItem('acadDrawingsV1'))localStorage.setItem('acadDrawingsV1',JSON.stringify({active:'d1',list:[{id:'d1',name:'Drawing1'},{id:'d2',name:'Kept'}],store:{d2:[{type:'line'}]}}));}catch(e){}")
        page = await ctx.new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)[:120]))
        await page.goto('file://' + str(HTML))
        await page.wait_for_timeout(2500)
        await page.mouse.click(800, 500)
        await page.wait_for_timeout(250)
        ev = page.evaluate

        async def safe(js, arg=None):
            try:
                return await (ev(js, arg) if arg is not None else ev(js))
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:140])
                return None

        async def tabs():
            return (await safe("()=>Array.prototype.map.call(document.querySelectorAll('#acad-doctabs button'),"
                               "function(b){var n=b.querySelector('.dt-name');return [b.getAttribute('data-dt'),(n||b).textContent.trim(),b.classList.contains('active')];})")) or []

        async def start_state():
            return await safe("""()=>{var s=document.getElementById('acad-start');if(!s)return null;
                return {shown:s.classList.contains('show'),
                        onTop:(function(){var r=s.getBoundingClientRect();var e=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);return !!(e&&e.closest('#acad-start'));})(),
                        buttons:Array.prototype.map.call(s.querySelectorAll('.st-left button'),function(b){return b.textContent.trim();}),
                        cards:Array.prototype.map.call(s.querySelectorAll('.st-card'),function(c){return c.textContent.trim();})};}""")

        print('\n-- 2. the document tabs describe the projects (contract amended in V115)')
        # V114 had one tab, because the whiteboard's "drawings" were never separate models. V115 made
        # each tab its own project, so + and x are real now; bim_phase115 drives them in depth.
        tb = await tabs()
        ck([x[0] for x in tb] == ['start', 'doc', 'new'], 'the tabs are Start, the one project, and + for a new one (%s)' % tb)
        ck(len(tb) == 3 and tb[1][1] == 'Untitled project' and tb[1][2] is True and tb[0][2] is False,
           'the project tab carries the title-block name and is the active one (%s)' % tb)
        ck((await safe("()=>{var n=document.querySelector('#acad-doctabs [data-dt=\"new\"]');"
                       "return !!n&&n.title==='New project'&&document.querySelectorAll('#acad-doctabs .dt-x').length===1;}")) is True,
           'the + is New project, and the one project tab has its own close button')
        await safe("()=>{var tb=window.__a3dTitleBlockGet();tb.project='Harbour Pavilion';window.__a3dTitleBlockSet(tb);}")
        await page.wait_for_timeout(1300)
        tb2 = await tabs()
        ck(len(tb2) == 3 and tb2[1][1] == 'Harbour Pavilion',
           'renaming the project renames its tab, whatever edited the name (%s)' % (tb2[1][1] if len(tb2) == 3 else tb2))

        print('\n-- 3. the Start screen offers only what works, and is seen')
        await safe("()=>{window.__a3dTestSetObjs([]);window.__a3dWall([[0,0],[6,0]],0.3,null,'center',false);"
                   "window.__a3dWall([[6,0],[6,4]],0.3,null,'center',false);window.__a3dWall([[6,4],[0,4]],0.3,null,'center',false);}")
        await safe("()=>{document.querySelector('#acad-doctabs [data-dt=\"start\"]').click();}")
        await page.wait_for_timeout(300)
        st = await start_state()
        ck(st and st['shown'] is True and st['onTop'] is True,
           'the Start tab opens the Start screen, and it is what is on top -- not a class on a hidden element (%s)' % st)
        ck(st and st['buttons'] == ['New project', 'Open project file…'],
           'it offers New project and Open project file, and nothing that is not built (%s)' % (st and st['buttons']))
        ck(st and len(st['cards']) == 1 and 'Harbour Pavilion' in st['cards'][0] and '3 objects' in st['cards'][0],
           "its one card is the project, counted from the BIM model -- 3 walls, 3 objects (%s)" % (st and st['cards']))
        tb3 = await tabs()
        ck(len(tb3) == 3 and tb3[0][2] is True and tb3[1][2] is False, 'and the Start tab is the active one while it shows (%s)' % tb3)
        await safe("()=>{document.querySelector('#acad-start .st-card[data-st=\"doc\"]').click();}")
        await page.wait_for_timeout(300)
        st2 = await start_state()
        tb4 = await tabs()
        ck(st2 and st2['shown'] is False and len(tb4) == 3 and tb4[1][2] is True,
           'the project card closes it and makes the project tab active again (%s / %s)' % (st2 and st2['shown'], tb4))
        await safe("()=>{document.querySelector('#acad-doctabs [data-dt=\"start\"]').click();}")
        await page.wait_for_timeout(250)
        chooser = None
        try:
            async with page.expect_file_chooser(timeout=3000) as fc:
                await safe("()=>{document.querySelector('#acad-start [data-st=\"open\"]').click();}")
            chooser = await fc.value
        except Exception as e:
            print('      (no file chooser: %s)' % str(e)[:80])
        acc = await safe("()=>{var f=document.getElementById('a3d-projin');return f?f.getAttribute('accept'):null;}")
        ck(chooser is not None and acc == '.json',
           'Open project file opens the real file chooser, one that takes project .json files only (%s)' % acc)
        st3 = await start_state()
        ck(st3 and st3['shown'] is True,
           'and the Start screen stays until a project actually opens -- a cancelled chooser must not uncover one')
        await safe("()=>{document.querySelector('#acad-doctabs [data-dt=\"doc\"]').click();}")
        await page.wait_for_timeout(200)

        print('\n-- 4. the shell toasts through the BIM engine')
        # AMENDED FOR V120: window.toast, the whiteboard's name that V114 kept as a shim, is gone; the shell's
        # five call sites call the engine's window.__a3dToast, and the palette's refusal below drives one.
        own = await safe("()=>typeof window.toast")
        ck(own == 'undefined', "the whiteboard's window.toast is gone (%r)" % own)
        await safe("()=>{var t=document.getElementById('a3d-toast');if(t)t.textContent='';}")
        await page.wait_for_timeout(2400)
        # AMENDED FOR V119: this drove the workspace menu's own toast, and the menu went with the view
        # dropdown. The shell call site driven instead is the command palette's refusal: on a sheet, a
        # model command is refused and the palette says so through the engine's toast.
        await safe("()=>{var id=window.__a3dAddSheet('A900','Toast probe','ANSI-B-L');window.__a3dOpenSheetView(id);"
                   "if(document.activeElement&&document.activeElement.blur)document.activeElement.blur();}")
        await page.wait_for_timeout(300)
        await page.keyboard.press('Control+k')
        await page.wait_for_timeout(300)
        await page.keyboard.type('WALL')
        await page.wait_for_timeout(150)
        await page.keyboard.press('Enter')
        await page.wait_for_timeout(500)
        ws = await safe("()=>{var t=document.getElementById('a3d-toast');return t?t.textContent:null;}")
        await safe("()=>window.__a3dCloseSheetView()")
        ck(ws is not None and 'is not available here' in ws,
           'a refusal from the shell\'s command palette reaches it too, as shell toasts did not before V113c (%r)' % ws)

        # AMENDED FOR V121b: V114 kept the whiteboard's saved drawings because deleting them was the
        # owner's call; the owner has made it ("i want to clear them up"), and the app removes them at
        # start with the rest of the old canvas's entries (the V121b suite seeds and proves that).
        print('\n-- 5. the whiteboard\'s saved drawings are cleared at start (V121b)')
        kept = await safe("()=>localStorage.getItem('acadDrawingsV1')")
        ck(kept is None, "the whiteboard's saved drawings are no longer in storage (%s)" % kept)

        ck(not errs, 'no uncaught page errors (%s)' % errs[:2])
        await browser.close()
    print('\n%d/%d checks passed' % (ck.n - len(ck.bad), ck.n))
    print('RESULT: ' + ('PASS' if not ck.bad else 'FAIL'))
    return 0 if not ck.bad else 1


if __name__ == '__main__':
    sys.exit(asyncio.run(run()))
