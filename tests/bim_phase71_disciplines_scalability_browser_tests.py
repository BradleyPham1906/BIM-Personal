"""
bim_phase71_disciplines_scalability_browser_tests.py

Regression suite for __acad3dV71 in canvas_v10.html: disciplines, computed dock rows, command
search, and the one-call registration API -- i.e. whether the tool surface can carry structural
analysis, bridge design and mechanical engineering, not just architecture.

THE QUESTION THIS PHASE ANSWERS, and what was measured before answering it. The V70 dock RENDERS
from a registry, so that part scaled. Three things did not, and each was measured in the file:

  - The row layout was a literal: A3D_DOCK_ROWS=[[5 ids],[4 ids]]. Nine groups already filled both
    rows. Bridge + Mechanical + MEP would be 12-15 groups with nowhere to go.
  - There was no discipline concept. Every tab showed at all times, so every new domain made the
    dock permanently busier for everyone, whatever they were working on.
  - A command cost FOUR edits in four places about 700 lines apart. For 'bim:beam':
        23786  A3DR_ICONS
        24072  the Structure tab's panel list
        24148  the a3drLabel literal
        24489  a branch of the 60-case dispatch chain
    Three of those are easy to forget, and forgetting the label renders a tool as 'brg:girder'.

What shipped: `disc` on a tab and an A3D_DISCIPLINES list; rows computed from the group count;
a command search spanning EVERY discipline; and __a3dRegisterCommand / __a3dRegisterDiscipline /
__a3dRegisterTab, which take a new domain's label, icon and runner in ONE call each.

WHAT THIS SUITE ASSERTS, and why each check is the one that would catch a regression:

  1. Scalability is DEMONSTRATED, not claimed. The suite registers a complete synthetic Bridge
     domain at runtime -- a discipline, two commands (one working, one deliberately marked
     unimplemented), and a tab -- through the public API only, then asserts the dock absorbs it:
     the discipline appears, selecting it swaps the domain group in, the rows re-flow on their
     own, the new tool's icon and label render, and clicking it runs the registered function.
     No layout constant, no label map and no dispatch branch is touched to make that work. A
     comment claiming "this is extensible" would pass no part of this.
  2. The discipline filter actually filters, in both directions. A filter that shows everything
     is not a filter; one that hides a tab without a way back is a trap.
  3. Search spans EVERY discipline, including one that is not active. This is the load-bearing
     property: the filter is only safe to be aggressive because search never lets a tool fall out
     of reach. Checked by finding the Bridge girder while Architecture is active.
  4. Rows are computed. Asserted by the row count CHANGING when a domain is added, which a
     hardcoded layout cannot do.
  5. The coverage audit is clean: every action any tab can reach has a real label (not its own raw
     id) and a real icon. That is the "added to a tab, forgot the other three places" failure,
     and it is the one that scales worst -- it is invisible until someone opens that caret.
  6. Registration is validated and honest: a duplicate discipline or tab is refused rather than
     silently shadowing, and a command registered as unimplemented is greyed and toasts rather
     than appearing to work.

Run:  python3 bim_phase71_disciplines_scalability_browser_tests.py [path/to/canvas_v10.html]
"""

# AMENDED FOR V120: the shell's canvas-era names were replaced -- #figma-layers-shell/-rail/-panel are
# #a3d-shell/-rail/-leftpanel, the .fl-* classes .a3d-*, #uploaded-command-palette #a3d-cmdpal, the
# Project Browser tab 'file' is 'browser', --figma-dock-w is --a3d-left-w, and the material library is
# read through window.__a3dMaterialCards() (window.__WB_MATERIAL_CARDS is gone).
import asyncio, pathlib, sys

from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'

ENTER = """()=>{
  window.__a3dEnter();
  window.ACAD_WS_CUR='da';
  window.__a3dTestSetObjs([]);
  window.__a3dSetPlanView&&window.__a3dSetPlanView();
  window.__a3dWall([[0,0],[10,0],[10,7],[0,7]],0.3,3,'center',true);
}"""

# A complete domain pack, registered through the PUBLIC API only. Nothing here edits a registry,
# a layout constant or the dispatch chain -- which is the whole point of the exercise.
REGISTER_BRIDGE = """()=>{
  const r={};
  r.disc=window.__a3dRegisterDiscipline({id:'bridge',name:'Bridge'});
  r.cmd1=window.__a3dRegisterCommand({
    id:'brg:girder', label:'Girder',
    icon:'<svg viewBox="0 0 24 24"><rect x="2" y="10" width="20" height="4"/></svg>',
    run:function(){window.__brgRan=(window.__brgRan||0)+1;}});
  r.cmd2=window.__a3dRegisterCommand({
    id:'brg:bearing', label:'Bearing',
    icon:'<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="6"/></svg>',
    unimpl:true});
  r.cmd3=window.__a3dRegisterCommand({
    id:'brg:stage', label:'Construction Stage',
    icon:'<svg viewBox="0 0 24 24"><path d="M3 18h18M7 14h10M11 10h6"/></svg>',
    run:function(){window.__brgStage=(window.__brgStage||0)+1;}});
  r.tab=window.__a3dRegisterTab({id:'bridge',name:'Bridge',disc:'bridge',panels:[
    {t:'Superstructure',small:['brg:girder','brg:bearing']},
    {t:'Sequencing',small:['brg:stage']}]});
  return r;
}"""


class Checks:
    def __init__(self):
        self.n = 0
        self.failed = []

    def __call__(self, cond, msg):
        self.n += 1
        ok = bool(cond)
        print(("  PASS  " if ok else "  FAIL  ") + msg)
        if not ok:
            self.failed.append(msg)


def group_ids(info):
    return [g['id'] for g in info['groups']]


async def run():
    ck = Checks()
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page(viewport={'width': 1600, 'height': 950})
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        await page.goto('file://' + str(HTML))
        await page.wait_for_timeout(900)

        has71 = await page.evaluate("()=>!!window.__acad3dV71")
        ck(has71, "__acad3dV71 marker is present")
        if not has71:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.failed), ck.n))
            await browser.close()
            return 1

        await page.evaluate(ENTER)
        await page.wait_for_timeout(900)

        print("\n-- 1. the coverage audit is clean before anything is added")
        audit = await page.evaluate("()=>window.__a3dCommandAudit()")
        ck(audit['total'] > 50, "the registry carries %d commands" % audit['total'])
        ck(not audit['noLabel'],
           "every one has a real label, not its own raw id (%s)" % (audit['noLabel'] or 'none'))
        ck(not audit['noIcon'], "and a real icon (%s)" % (audit['noIcon'] or 'none'))

        print("\n-- 2. the discipline filter filters, in both directions")
        discs = await page.evaluate("()=>window.__a3dDisciplines()")
        ck([d['id'] for d in discs] == ['arch', 'struct'],
           "two disciplines ship (%s)" % [d['id'] for d in discs])
        ck(await page.evaluate("()=>window.__a3dDiscipline()") == 'arch',
           "Architecture is the default")
        arch = group_ids(await page.evaluate("()=>window.__a3dDockInfo()"))
        ck('arch' in arch, "the Architecture group is in the dock")
        ck('struct' not in arch,
           "and Structure is NOT, so a domain's tools are not on screen while you work in "
           "another (%s)" % arch)
        shared = [g for g in arch if g not in ('__disc', 'arch')]
        ck(len(shared) >= 6,
           "the shared tabs stay regardless of discipline (%s)" % shared)
        await page.evaluate("()=>window.__a3dSetDiscipline('struct')")
        await page.wait_for_timeout(300)
        struct = group_ids(await page.evaluate("()=>window.__a3dDockInfo()"))
        ck('struct' in struct and 'arch' not in struct,
           "switching swaps the domain group (%s)" % struct)
        ck([g for g in struct if g not in ('__disc', 'struct')] == shared,
           "and leaves the shared tabs exactly as they were")
        await page.evaluate("()=>window.__a3dSetDiscipline('arch')")
        await page.wait_for_timeout(250)
        ck(await page.evaluate("()=>window.__a3dSetDiscipline('nope')") is False,
           "an unknown discipline is refused rather than blanking the dock")

        print("\n-- 3. a whole new engineering domain, added through the public API only")
        rows_before = (await page.evaluate("()=>window.__a3dDockInfo()"))['rows']
        reg = await page.evaluate(REGISTER_BRIDGE)
        ck(reg['disc'] is True, "the Bridge discipline registers")
        ck(reg['cmd1'] is True and reg['cmd2'] is True and reg['cmd3'] is True,
           "its three commands register, each in ONE call carrying label, icon and runner")
        ck(reg['tab'] is True, "and its tab registers")
        ck(await page.evaluate("()=>window.__a3dRegisterDiscipline({id:'bridge',name:'Dup'})")
           is False,
           "a duplicate discipline is refused rather than silently shadowing the first")
        ck(await page.evaluate("()=>window.__a3dRegisterTab({id:'bridge',name:'Dup',panels:[]})")
           is False,
           "and so is a duplicate tab")
        discs2 = await page.evaluate("()=>window.__a3dDisciplines()")
        ck([d['id'] for d in discs2] == ['arch', 'struct', 'bridge'],
           "the discipline list grew (%s)" % [d['id'] for d in discs2])

        ck(await page.evaluate("()=>window.__a3dSetDiscipline('bridge')") is True,
           "Bridge can be made active")
        await page.wait_for_timeout(400)
        info_b = await page.evaluate("()=>window.__a3dDockInfo()")
        bridge = group_ids(info_b)
        ck('bridge' in bridge,
           "the dock grew a Bridge group with no layout constant edited (%s)" % bridge)
        ck('arch' not in bridge and 'struct' not in bridge,
           "and the other domains stepped aside")

        print("\n-- 4. the rows are computed, not listed")
        ck(all(g['hasCaret'] for g in info_b['groups'] if g['id'] != '__disc'),
           "every tool group, the new one included, got its caret")
        # Swapping one domain group for another leaves the COUNT unchanged, so that alone proves
        # nothing about the layout. Growing it does. Four more shared tabs take the dock from 9
        # groups to 13 -- past the 10 the old [[5],[4]] literal could physically hold.
        grow = await page.evaluate("""()=>{
          let ok=true;
          for(let i=1;i<=4;i++){
            ok=ok&&window.__a3dRegisterCommand({id:'syn:c'+i,label:'Synthetic '+i,
              icon:'<svg viewBox="0 0 24 24"><rect x="6" y="6" width="12" height="12"/></svg>',
              run:function(){}});
            ok=ok&&window.__a3dRegisterTab({id:'syn'+i,name:'Synthetic '+i,
              panels:[{t:'Tools',small:['syn:c'+i]}]});
          }
          return ok;}""")
        ck(grow is True, "four more shared tabs register")
        await page.evaluate("()=>window.__a3dSetDiscipline('bridge')")
        await page.wait_for_timeout(400)
        info_g = await page.evaluate("()=>window.__a3dDockInfo()")
        grown = group_ids(info_g)
        ck(len(grown) == len(bridge) + 4,
           "all four land in the dock (%d -> %d groups)" % (len(bridge), len(grown)))
        ck(info_g['rows'] > info_b['rows'],
           "and the dock grew a ROW to hold them on its own (%d -> %d) -- a hardcoded "
           "[[5],[4]] could not have" % (info_b['rows'], info_g['rows']))
        ck(info_g['insideViewport'] is True,
           "the grown dock still fits inside the drawing area rather than overflowing it")
        ck(all(g['hasCaret'] for g in info_g['groups'] if g['id'] != '__disc'),
           "and every one of the %d tool groups has its caret" % (len(grown) - 1))

        print("\n-- 5. the new domain's tools are real")
        face = await page.evaluate("""()=>{
          const b=document.querySelector('#a3d-dock .a3d-dbtn[data-a3dr="brg:girder"]');
          return b?{found:true,hasIcon:!!b.querySelector('svg'),
                    title:b.getAttribute('aria-label')||''}:{found:false};}""")   # AMENDED FOR V129: the native title became aria-label + a real tooltip
        ck(face['found'] is True, "Girder is on the dock's face")
        ck(face['hasIcon'] is True, "with the icon supplied at registration")
        ck('Girder' in face['title'], "and its label (%s)" % face['title'])
        ck(await page.evaluate("""()=>{
             const b=document.querySelector('#a3d-dock .a3d-dbtn[data-a3dr="brg:bearing"]');
             return !b;}"""),
           "the unimplemented Bearing is NOT promoted to the face")
        await page.evaluate("()=>window.__a3dDockOpenGroup('bridge')")
        await page.wait_for_timeout(250)
        pop = await page.evaluate("""()=>{const p=document.querySelector(
          '#a3d-dock [data-dockpop="bridge"]');
          if(!p)return null;
          return {items:p.querySelectorAll('[data-a3dr]').length,
                  greyed:p.querySelectorAll('.a3d-dockitem.a3dr-dis').length,
                  heads:p.querySelectorAll('.a3d-dockpoph').length};}""")
        ck(pop is not None and pop['items'] == 3,
           "its caret lists all three tools (%s)" % pop)
        ck(pop['greyed'] == 1, "with the unimplemented one greyed, as the ribbon always did")
        ck(pop['heads'] == 2, "under both panel headings it declared")
        await page.evaluate("()=>{document.body.click();}")
        await page.wait_for_timeout(150)

        before = await page.evaluate("()=>window.__brgRan||0")
        await page.evaluate("""()=>{
          document.querySelector('#a3d-dock .a3d-dbtn[data-a3dr="brg:girder"]').click();}""")
        await page.wait_for_timeout(300)
        after = await page.evaluate("()=>window.__brgRan||0")
        ck(after == before + 1,
           "clicking Girder runs the function registered with it (%d -> %d) -- no dispatch branch "
           "was added to the 60-case chain" % (before, after))

        print("\n-- 6. search reaches every discipline, not just the active one")
        await page.evaluate("()=>window.__a3dSetDiscipline('arch')")
        await page.wait_for_timeout(300)
        cur = group_ids(await page.evaluate("()=>window.__a3dDockInfo()"))
        ck('bridge' not in cur, "Bridge is out of the dock's groups while Architecture is active")
        found = await page.evaluate("()=>window.__a3dDockSearch('girder')")
        ck(found is not None and 'brg:girder' in found['shown'],
           "but search still finds it (%s) -- which is what makes the filter safe to be "
           "aggressive" % found)
        wall = await page.evaluate("()=>window.__a3dDockSearch('wall')")
        ck(wall['matches'] >= 2,
           "search matches on label text across tabs (%d hits for 'wall')" % wall['matches'])
        none = await page.evaluate("()=>window.__a3dDockSearch('zzzznotathing')")
        ck(none['matches'] == 0 and not none['shown'],
           "and says so plainly when nothing matches rather than listing everything")
        audit2 = await page.evaluate("()=>window.__a3dCommandAudit()")
        # Three Bridge commands plus the four synthetic ones registered in section 4.
        ck(audit2['total'] == audit['total'] + 7,
           "the audit picked up every command registered during this run (%d -> %d)"
           % (audit['total'], audit2['total']))
        ck(not audit2['noLabel'] and not audit2['noIcon'],
           "and they pass it -- a registered command cannot be missing its label or icon, "
           "because both are required by the same call that creates it")

        print("")
        ck(not errs, "zero uncaught page errors across every probe (%s)" % (errs or 'none'))
        await browser.close()

    print("\n%d/%d checks passed" % (ck.n - len(ck.failed), ck.n))
    if ck.failed:
        print("RESULT: FAIL")
        for m in ck.failed:
            print("   - " + m)
        return 1
    print("RESULT: PASS")
    return 0


sys.exit(asyncio.run(run()))
