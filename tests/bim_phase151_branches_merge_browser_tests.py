#!/usr/bin/env python3
"""bim_phase151_branches_merge_browser_tests.py -- V151: branches and merge (the Hub's H2).

  1. BRANCHES: a history from before is "main"; a new branch starts at the latest version and
     carries what is not committed; names checked; commits move the branch they are on.
  2. SWITCH: loads the branch's latest version; refused over changes not committed; an undo takes
     it back; the log is the branch's own line, its heads tagged.
  3. MERGE: up to date; moving up (fast-forward); three ways element by element -- one side's change
     taken, different fields of one element put together, an element added on each side kept; the
     same field changed both ways a conflict, side by side, kept or taken, Finish refused until
     each is decided; changed against deleted a conflict; Cancel changes nothing; the merge version
     has both parents, so the next merge starts from it.
  4. COMPARE: each branch's numbers, this branch's from the model as it is, a row that differs
     marked.
  5. SAVED: through a reload and in a project file; the panel's controls and the commands.

The harness never waits without a bound (V123).
"""
import asyncio, json, pathlib, re, sys, traceback
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
        page = await browser.new_page(viewport={'width': 1500, 'height': 950})
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        await within(page.goto('file://' + str(HTML)), 'goto')
        await page.wait_for_timeout(2000)

        async def safe(js, arg=None):
            try:
                return await within(page.evaluate(js, arg) if arg is not None else page.evaluate(js), 'evaluate ' + js[:50])
            except Stalled:
                raise
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:200])
                return None

        async def obj(i):
            return await safe("(i)=>window.__a3dState().objs.filter(function(o){return o.id===i;})[0]||null", i)

        async def rename(i, n):
            await safe("(i)=>{window.__a3dSelectFor([i]);window.__a3dRefreshProps();}", i)
            await page.fill('#a3d-propsbody [data-propf="name"]', n)
            await page.keyboard.press('Enter')
            await page.wait_for_timeout(80)

        async def commit(m):
            return await safe("(m)=>window.__a3dHistCommit(m)", m) or {}

        async def branches():
            return {b['name']: b for b in (await safe("()=>window.__a3dBranches()") or [])}

        async def cur():
            return [k for k, b in (await branches()).items() if b['current']]

        async def history():
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dSetPropTab('project');window.__a3dRunCmd('history');}")
            await page.wait_for_timeout(150)

        try:
            has = await safe("()=>window.__acad3dV151")
            ck(bool(has) and 'merge3' in has, "__acad3dV151 marker is present (%s)" % has)
            mv = re.search(r"var BIM_APP_VERSION=\{v:'V(\d+)'", HTML.read_text(encoding='utf-8'))
            ck(mv and int(mv.group(1)) >= 151, "the app says V151 or later (%s)" % (mv and mv.group(1)))
            await safe("()=>{window.__a3dEnter();window.__a3dSetPlanView&&window.__a3dSetPlanView();window.__a3dTestSetObjs([]);}")

            print("\n-- 1. branches")
            B = await branches()
            ck(list(B) == ['main'] and B['main']['current'] and B['main']['head'] is None, "a project starts on one branch, main, with no versions (%s)" % B)
            r = await safe("()=>window.__a3dBranchNew('Option A')")
            ck(r and 'Commit a version first' in r.get('error', ''), "a branch needs a version to start at (%s)" % r)
            a, b2 = await safe("()=>[window.__a3dColumnAt([0,0],0,0.4,0.4,3),window.__a3dColumnAt([6,0],0,0.4,0.4,3)]")
            base = await commit('base')
            for bad, why in (('', 'empty'), ('-x', 'a leading dash'), ('x' * 41, 'over 40'), ('a/b', 'a slash')):
                r = await safe("(n)=>window.__a3dBranchNew(n)", bad)
                ck(r and r.get('error'), "a branch name refused: %s" % why)
            await safe("(i)=>window.__a3dMoveObjects([i],2,0,0)", a)
            r = await safe("()=>window.__a3dBranchNew('Option A')")
            B = await branches()
            ck(r and r.get('name') == 'Option A' and B['Option A']['current'] and B['Option A']['head'] == base['id'] and B['main']['head'] == base['id'],
               "New Branch starts at the latest version and puts you on it (%s)" % r)
            ck((await obj(a))['pos'][0] == 2, "what was not committed comes along")
            ck((await safe("()=>window.__a3dBranchNew('Option A')") or {}).get('error', '').startswith('There is a branch'), "a name taken is refused")
            ca = await commit('A moves column 1')
            B = await branches()
            ck(B['Option A']['head'] == ca['id'] and B['main']['head'] == base['id'], "a commit moves only the branch it is on")

            print("\n-- 2. switch")
            await safe("(i)=>window.__a3dMoveObjects([i],0,0,1)", b2)
            r = await safe("()=>window.__a3dBranchSwitch('main')")
            ck(r and 'Commit or discard' in r.get('error', '') and await cur() == ['Option A'], "switching over changes not committed is refused (%s)" % r)
            await safe("(i)=>window.__a3dMoveObjects([i],0,0,-1)", b2)
            r = await safe("()=>window.__a3dBranchSwitch('main')")
            ck(r and r.get('name') == 'main' and await cur() == ['main'] and (await obj(a))['pos'][0] == 0, "clean, it switches: main's column 1 where main left it")
            await safe("()=>window.__a3dUndo()")
            ck((await obj(a))['pos'][0] == 2, "an undo brings back the model it left")
            await safe("()=>window.__a3dRedo()")
            await history()
            log = await safe("()=>[].map.call(document.querySelectorAll('#a3d-propsbody .a3d-histc .a3d-histcm'),function(e){return e.textContent;})") or []
            ck(log and all('A moves' not in x for x in log) and 'base' in log[0], "main's log is main's line: not Option A's version (%s)" % log)
            ck('main' in log[0] and 'Option A' not in log[0] and 'latest' in log[0], "its head is tagged main (%s)" % log[0])

            print("\n-- 3. merge")
            r = await safe("()=>window.__a3dMergeStart('Option A')")
            ck(r and r.get('fastForward') and (await branches())['main']['head'] == ca['id'] and (await obj(a))['pos'][0] == 2,
               "main had nothing new: merging Option A moves it up to Option A (%s)" % r)
            r = await safe("()=>window.__a3dBranchSwitch('Option A')")
            r = await safe("()=>window.__a3dMergeStart('main')")
            ck(r and r.get('upToDate'), "Option A already has all of main: up to date (%s)" % r)
            # different fields of one element, and one element added on each side
            await rename(a, 'A name')
            colA = await safe("()=>window.__a3dColumnAt([12,0],0,0.4,0.4,3)")
            ca2 = await commit('A renames, adds')
            await safe("()=>window.__a3dBranchSwitch('main')")
            await safe("(i)=>window.__a3dMoveObjects([i],0,0,3)", a)
            colM = await safe("()=>window.__a3dColumnAt([0,9],0,0.4,0.4,3)")
            cm = await commit('main moves, adds')
            ck(await safe("(a)=>window.__a3dHistBase(a[0],a[1])", [cm['id'], ca2['id']]) == ca['id'], "the version both share is found")
            r = await safe("()=>window.__a3dMergeStart('Option A')")
            o = await obj(a)
            ck(r and r.get('merged') and r.get('conflicts') == 0 and o['name'] == 'A name' and o['pos'] == [2, 0, 3],
               "a clean merge: column 1 has Option A's name and main's move -- different fields put together (%s)" % (o and [o['name'], o['pos']]))
            ck(await obj(colA) and await obj(colM), "and each side's new column")
            H = await safe("()=>window.__a3dHistory()") or {}
            mc = [c for c in H.get('commits', []) if c['id'] == r.get('id')]
            ck(mc and mc[0]['parent'] == cm['id'] and mc[0].get('parent2') == ca2['id'] and mc[0]['msg'] == 'Merge "Option A" into "main"',
               "the merge is a version with both parents (%s)" % (mc and mc[0].get('msg')))
            ck((await branches())['main']['head'] == r.get('id') and not await safe("()=>window.__a3dHistChanges().length"), "main is at it, nothing left to commit")
            # the same field both ways
            await safe("()=>window.__a3dBranchSwitch('Option A')")
            await rename(b2, 'A says')
            ca3 = await commit('A2')
            await safe("()=>window.__a3dBranchSwitch('main')")
            await rename(b2, 'main says')
            cm3 = await commit('M2')
            ck(await safe("(a)=>window.__a3dHistBase(a[0],a[1])", [cm3['id'], ca3['id']]) == ca2['id'], "after a merge, the next one starts from what it brought in")
            r = await safe("()=>window.__a3dMergeStart('Option A')")
            M = await safe("()=>window.__a3dMergeState()") or {}
            c0 = (M.get('conflicts') or [{}])[0]
            ck(r and r.get('conflicts') == 1 and c0.get('kind') == 'both' and c0.get('fields') == [{'f': 'name', 'base': 'Column_2', 'ours': 'main says', 'theirs': 'A says'}],
               "the same field changed both ways is a conflict: name, Column_2, main says against A says (%s)" % c0.get('fields'))
            r = await safe("()=>window.__a3dMergeFinish()")
            ck(r and '1 conflict to decide' in r.get('error', ''), "Finish waits for each to be decided (%s)" % r)
            await history()
            ui = await safe("""()=>{var m=document.querySelector('#a3d-propsbody [data-brmerge]');if(!m)return null;
              return {txt:m.textContent,sides:[].map.call(m.querySelectorAll('.a3d-brside'),function(e){return e.textContent;}),fin:m.querySelector('[data-histact="mfinish"]').disabled};}""")
            ck(ui and ui['sides'] == ['mainmain says', 'Option AA says'] and ui['fin'] and '1 to decide' in ui['txt'],
               "shown side by side in History, Finish greyed (%s)" % (ui and ui['sides']))
            await page.click('#a3d-propsbody [data-histact="mkeep:0"]')
            await page.wait_for_timeout(100)
            await page.click('#a3d-propsbody [data-histact="mfinish"]')
            await page.wait_for_timeout(200)
            ck((await obj(b2))['name'] == 'main says' and not await safe("()=>window.__a3dMergeState()"), "Keep main's, then Finish: main's name stands")
            # taken from the other side
            await safe("()=>window.__a3dBranchSwitch('Option A')")
            await rename(b2, 'A again')
            await commit('A3')
            await safe("()=>window.__a3dBranchSwitch('main')")
            await rename(b2, 'main again')
            await commit('M3')
            await safe("()=>window.__a3dMergeStart('Option A')")
            await safe("()=>{window.__a3dMergeChoose(0,'theirs');}")
            r = await safe("()=>window.__a3dMergeFinish()")
            ck(r and r.get('merged') and (await obj(b2))['name'] == 'A again', "Take Option A's: its name comes in")
            # changed against deleted
            await safe("()=>window.__a3dBranchSwitch('Option A')")
            await rename(a, 'A keeps it')
            await commit('A4')
            await safe("()=>window.__a3dBranchSwitch('main')")
            await safe("(i)=>{window.__a3dSelectFor([i]);window.__a3dRunCmd('del');}", a)
            await commit('M4 deletes')
            n0 = len(await safe("()=>window.__a3dState().objs") or [])
            r = await safe("()=>window.__a3dMergeStart('Option A')")
            c0 = ((await safe("()=>window.__a3dMergeState()") or {}).get('conflicts') or [{}])[0]
            ck(r and r.get('conflicts') == 1 and c0.get('kind') == 'deleted' and c0.get('gone') == 'ours', "deleted on main, changed on Option A: a conflict (%s)" % c0)
            ck(await safe("()=>window.__a3dMergeAbort()") and not await safe("()=>window.__a3dMergeState()") and len(await safe("()=>window.__a3dState().objs") or []) == n0,
               "Cancel: no merge, the model as it was")
            await safe("()=>window.__a3dMergeStart('Option A')")
            await safe("()=>window.__a3dMergeChoose(0,'theirs')")
            await safe("()=>window.__a3dMergeFinish()")
            o = await obj(a)
            ck(o and o['name'] == 'A keeps it', "Take Option A's: the column comes back, as Option A has it")
            r = await safe("()=>window.__a3dMergeStart('Option Z')")
            ck(r and r.get('error', '').startswith('There is no branch'), "a branch that is not there is refused (%s)" % r)
            r = await safe("()=>window.__a3dMergeStart('main')")
            ck(r and 'into itself' in r.get('error', ''), "a branch is not merged into itself")
            await safe("(i)=>window.__a3dMoveObjects([i],1,0,0)", a)
            r = await safe("()=>window.__a3dMergeStart('Option A')")
            ck(r and 'Commit or discard' in r.get('error', ''), "nor over changes not committed")
            await safe("(i)=>window.__a3dMoveObjects([i],-1,0,0)", a)

            print("\n-- 4. compare")
            await safe("()=>window.__a3dBranchSwitch('Option A')")
            w = await safe("()=>window.__a3dWall([[0,20],[10,20]],0.3,3,'center',false)")
            await commit('A adds a wall')
            await safe("()=>window.__a3dBranchSwitch('main')")
            C = {c['name']: c for c in await safe("()=>window.__a3dBranchCompare()") or []}
            ck(C['Option A']['m']['walls'] == C['main']['m']['walls'] + 1 and abs(C['Option A']['m']['wallLength'] - C['main']['m']['wallLength'] - 10) < 1e-6,
               "Option A has one wall more, 10 m of it (%s)" % {k: (v['m']['walls'], round(v['m']['wallLength'], 2)) for k, v in C.items()})
            await safe("()=>window.__a3dColumnAt([30,30],0,0.4,0.4,3)")
            C2 = {c['name']: c for c in await safe("()=>window.__a3dBranchCompare()") or []}
            ck(C2['main']['m']['objects'] == C['main']['m']['objects'] + 1, "this branch's numbers are the model as it is, committed or not")
            await safe("()=>window.__a3dUndo()")
            await safe("()=>window.__a3dRunCmd('comparebranches')")
            await page.wait_for_timeout(150)
            tb = await safe("""()=>{var t=document.querySelector('#a3d-propsbody [data-brcmp]');if(!t)return null;
              return {head:[].map.call(t.querySelectorAll('th'),function(e){return e.textContent;}),diff:[].map.call(t.querySelectorAll('tr.diff'),function(e){return e.getAttribute('data-brrow');})};}""")
            ck(tb and tb['head'] == ['', 'main', 'Option A'] and 'walls' in tb['diff'] and 'wallLength' in tb['diff'] and 'levels' not in tb['diff'],
               "COMPAREBRANCHES shows the table, the rows that differ marked (%s)" % tb)

            print("\n-- 5. the panel, the commands, saved")
            await page.fill('#a3d-propsbody [data-brname]', 'Option C')
            await page.keyboard.press('Enter')
            await page.wait_for_timeout(150)
            ck(await cur() == ['Option C'], "a name typed and Enter: a new branch, Option C")
            await page.select_option('#a3d-propsbody [data-histbranch]', 'main')
            await page.wait_for_timeout(200)
            ck(await cur() == ['main'], "the Branch list switches")
            await page.select_option('#a3d-propsbody [data-brmergefrom]', 'Option A')
            await page.click('#a3d-propsbody [data-histact="merge"]')
            await page.wait_for_timeout(200)
            ck(await obj(w), "Merge In brings Option A's wall into main")
            cat = await safe("()=>window.__a3dCommandCatalog().filter(function(c){return ['BRANCH','MERGE','COMPAREBRANCHES'].indexOf(c.name)>=0;}).map(function(c){return c.name;})") or []
            ck(sorted(cat) == ['BRANCH', 'COMPAREBRANCHES', 'MERGE'], "BRANCH, MERGE and COMPAREBRANCHES are commands (%s)" % cat)
            nm = [x['name'] for x in (await safe("(q)=>window.__a3dCommandSearch(q,5)", 'design option') or [])]
            ck('BRANCH' in nm[:3], "searching 'design option' finds BRANCH (%s)" % nm)
            r = await safe("()=>window.__a3dBranchDelete('main')")
            ck(r and r.get('error'), "the branch you are on cannot be deleted")
            ck((await safe("()=>window.__a3dBranchDelete('Option C')") or {}).get('name') == 'Option C' and 'Option C' not in await branches(), "another can")
            await safe("()=>{window.__a3dBranchNew('Option D');window.__a3dBranchSwitch('main');}")
            await history()
            await page.select_option('#a3d-propsbody [data-brmergefrom]', 'Option D')
            await page.click('#a3d-propsbody [data-histact="brdelete"]')
            await page.wait_for_timeout(100)
            t1 = await safe("()=>{var b=document.querySelector('#a3d-propsbody [data-histact=\"brdelete\"]');return b&&b.textContent;}")
            ck(t1 == 'Delete Option D?' and 'Option D' in await branches(), "Delete asks once first (%s)" % t1)
            await page.click('#a3d-propsbody [data-histact="brdelete"]')
            await page.wait_for_timeout(100)
            ck('Option D' not in await branches() and await cur() == ['main'], "and deletes on the second tap")
            tabs = await safe("""()=>{var e=document.querySelector('#a3d-right .a3d-ptabs');if(!e)return null;var s=getComputedStyle(e);
              return {pos:s.position,img:s.backgroundImage,col:s.backgroundColor};}""")
            ck(tabs and tabs['pos'] == 'sticky' and 'gradient' in tabs['img'] and tabs['col'].startswith('rgb('),
               "the Properties tabs, stuck at the top, are not see-through (%s)" % tabs)
            before = await branches()
            env = await safe("()=>JSON.parse(window.__a3dProjectEnvelope())")
            ck(env and sorted(env['data']['history']['branches']) == sorted(before) and env['data']['history']['branch'] == 'main', "a project file carries the branches")
            r = await safe("()=>window.__a3dBranchSwitch('Option A')")
            ck(r and r.get('name') == 'Option A', "on Option A before the reload (%s)" % r)
            before = await branches()
            await page.wait_for_timeout(1500)
            await within(page.reload(), 'reload')
            await page.wait_for_timeout(2000)
            await safe("()=>window.__a3dEnter()")
            after = await branches()
            ck({k: (v['head'], v['current']) for k, v in after.items()} == {k: (v['head'], v['current']) for k, v in before.items()}, "through a reload, the branches and the one you are on")
            old = json.loads(json.dumps(env))
            del old['data']['history']['branches']
            del old['data']['history']['branch']
            ok = await safe("(t)=>window.__a3dImportProject(t,'v146.acad3d.json')", json.dumps(old))
            await page.wait_for_timeout(300)
            B = await branches()
            ck(ok and list(B) == ['main'] and B['main']['current'] and B['main']['head'] == old['data']['history']['head'], "a V146 project's history opens as main, at its latest version (%s)" % list(B))
            bad = json.loads(json.dumps(env))
            bad['data']['history']['branches'] = {'main': bad['data']['history']['head'], 'ghost': 'c-nope', '../x': bad['data']['history']['head']}
            bad['data']['history']['branch'] = 'ghost'
            await safe("(t)=>window.__a3dImportProject(t,'bad.acad3d.json')", json.dumps(bad))
            await page.wait_for_timeout(300)
            B = await branches()
            ck(list(B) == ['main'] and B['main']['current'], "a branch at a version that is not there, or with a bad name, is let go of (%s)" % list(B))
            await page.set_viewport_size({'width': 390, 'height': 844})
            await page.wait_for_timeout(400)
            await safe("()=>{var r=document.getElementById('a3d-right');if(r)r.classList.remove('open');window.__a3dRunCmd('branch');}")
            await page.wait_for_timeout(300)
            ph = await safe("()=>{var r=document.getElementById('a3d-right'),i=document.querySelector('#a3d-propsbody [data-brname]');return {open:!!(r&&r.classList.contains('open')),focus:document.activeElement===i,vis:!!(i&&i.getBoundingClientRect().height)};}")
            ck(ph and ph['open'] and ph['vis'], "on a phone, BRANCH opens the Properties sheet at History (%s)" % ph)
            ck(not errs, "no page errors (%s)" % errs[:3])
        except Stalled as s:
            ck(False, "the harness stalled at %s" % s)
        except Exception:
            traceback.print_exc()
            ck(False, "the suite ran to its end")
        await browser.close()

    print("\n%d/%d checks passed" % (CK.n - len(CK.bad), CK.n))
    if CK.bad:
        print("RESULT: FAIL")
        for m in CK.bad:
            print("   - " + m)
        return 1
    print("RESULT: PASS")
    return 0


sys.exit(asyncio.run(run()))
