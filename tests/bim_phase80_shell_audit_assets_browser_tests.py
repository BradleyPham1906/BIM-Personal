"""
bim_phase80_shell_audit_assets_browser_tests.py

Regression suite for __acad3dV80 in canvas_v10.html: the left shell purged of retired-Canvas
leftovers, a real BIM Assets library, and a permanent guard against this whole class of fault.

WHAT THE USER REPORTED: "the left panel, for the assets it didn't work in drafting and annotation.
you need to keep this in mind from now on, when update or anything, you need to make sure we dont
have any left over and they gotta work in the new version."

WHAT WAS ACTUALLY THERE, measured on V79 with the BIM shell up -- four leftovers, not one:

    .fl-pages           a Pages list whose + adds a WHITEBOARD page
    .fl-layers          the retired board's own nodes (Keyboard, Quick actions, Welcome to Canvas)
    .fl-bottom-actions  Back / Front / Focus, acting on whiteboard nodes
    the Assets tab      a card/sticky/chart library that drags onto the retired board

So the File tab drew three dead blocks ABOVE the live BIM navigator, and Assets was dead end to end.
V73 retired Canvas as a workspace and deliberately kept the whiteboard CODE -- it hosts the file
dock and the shared material library -- but never went back through the panel that code draws.

TWO FURTHER FINDINGS WERE NOT FAULTS, and the corrections matter more than the count.

  * Three rail buttons (Prop. / Layers / Blocks) appeared dead because clicking each changed
    nothing. They are display:none while this shell is up; .click() fires on hidden elements, so
    the probe could reach what no user can. Left alone.
  * The header still read "Canvas Mockup / Drafts / Free" -- in an element whose container is
    display:none in BIM mode. Also unreachable; a probe reading textContent found words nobody
    could see.

Both were found by probes that could reach what a user cannot. Section 1 asserts the audit measures
VISIBILITY and a real box, precisely so the guard cannot produce that class of false finding -- an
audit that cried wolf would be worse than none.

The header was then made USEFUL rather than merely re-hidden: it was an empty bar carrying a
collapse chevron, and it now names the project and site, which is what the reference tools put
there.

THE GUARD IS THE POINT OF THIS PHASE. bimShellAudit walks every visible, interactive element in the
left shell and matches it against A3D_SHELL_CLAIMS -- a whitelist where each entry states why that
control is live. Anything unmatched is UNCLAIMED, and section 1 asserts that list is empty in every
tab. A control added without being wired, or left behind by a future retirement, now fails the
build instead of sitting in the panel doing nothing.

A whitelist deliberately, not a blacklist of known-dead classes: a blacklist only ever knows about
the leftovers someone already found, which is exactly how five of them accumulated.

WHY EACH REMAINING CHECK IS THE ONE THAT WOULD CATCH A REGRESSION:

  2. The dead blocks are asserted gone AFTER a tab round trip, not just on first paint. They are
     re-rendered by the whiteboard's own setTab, so a one-shot cleanup would pass a first-load
     check and fail the moment anyone clicked Assets and came back.
  3. Every asset row is asserted to do the thing its LABEL says, by reading the model back -- a
     material lands on the object, a wall type changes its thickness, a pattern reaches the
     resolved graphics, a family adds an object and leaves it selected. A panel that renders
     correctly and changes nothing is this phase's fault in a new costume.
  4. A row with no live target is asserted DISABLED and to say why. Including the empty-geometry
     family, which this suite found: it advertised "place", reported success, and added an object
     nobody could see.

Run:  python3 bim_phase80_shell_audit_assets_browser_tests.py [path/to/canvas_v10.html]
"""

# AMENDED FOR V120: the shell's canvas-era names were replaced -- #figma-layers-shell/-rail/-panel are
# #a3d-shell/-rail/-leftpanel, the .fl-* classes .a3d-*, #uploaded-command-palette #a3d-cmdpal, the
# Project Browser tab 'file' is 'browser', --figma-dock-w is --a3d-left-w, and the material library is
# read through window.__a3dMaterialCards() (window.__WB_MATERIAL_CARDS is gone).
import asyncio, pathlib, sys

from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'

DEAD = ['.fl-pages', '.fl-layers', '.fl-bottom-actions', '.fak-root']


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


async def tab(page, name):
    await page.evaluate("(t)=>{const b=document.querySelector"
                        "('#a3d-rail [data-tab=\"'+t+'\"]');b&&b.click();}", name)
    await page.wait_for_timeout(650)


async def run():
    ck = Checks()
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1600, 'height': 950},
                                        device_scale_factor=2)
        page = await ctx.new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        await page.goto('file://' + str(HTML))
        await page.wait_for_timeout(2000)

        has80 = await page.evaluate("()=>!!window.__acad3dV80")
        ck(has80, "__acad3dV80 marker is present")
        if not has80:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.failed), ck.n))
            await browser.close()
            return 1

        print("\n-- 1. the guard: nothing visible in the left shell is unclaimed")
        for name in ('browser', 'assets', 'browser'):
            await tab(page, name)
            a = await page.evaluate("()=>window.__a3dShellAudit()")
            ck(a['ok'] is True,
               "%s tab: %d live controls, 0 unclaimed%s"
               % (name, a['claimed'],
                  '' if a['ok'] else (' -- UNCLAIMED: %s' % a['unclaimed'])))
        hidden = await page.evaluate("""()=>{
          const e=document.querySelector('[data-dk2="props"]');
          if(!e)return null;
          const s=getComputedStyle(e),r=e.getBoundingClientRect();
          return {display:s.display,w:Math.round(r.width),h:Math.round(r.height)};}""")
        ck(hidden is None or hidden['display'] == 'none' or hidden['w'] < 2,
           "the Prop./Layers/Blocks rail buttons are not VISIBLE (%s), which is why the audit does "
           "not flag them -- the probe that 'found' them reached hidden elements through .click()"
           % hidden)
        planted = await page.evaluate("""()=>{
          const rail=document.getElementById('a3d-rail');
          const b=document.createElement('button');
          b.className='a3d-railbtn';b.textContent='Ghost';b.style.cssText='width:40px;height:40px';
          rail.appendChild(b);
          const a=window.__a3dShellAudit();
          b.remove();
          return a;}""")
        ck(planted['ok'] is False and any(x['text'] == 'Ghost' for x in planted['unclaimed']),
           "and an unwired control planted into the rail IS caught (%s) -- the guard is what stops "
           "the next retirement leaving something behind silently"
           % [x['text'] for x in planted['unclaimed']])

        print("\n-- 2. the retired-Canvas blocks are gone, and stay gone")
        gone = await page.evaluate("(d)=>d.map(s=>[s,!!document.querySelector"
                                   "('#a3d-leftpanel '+s)])", DEAD)
        ck(all(not g[1] for g in gone), "on the File tab: %s" % gone)
        await tab(page, 'assets')
        await tab(page, 'browser')
        gone2 = await page.evaluate("(d)=>d.map(s=>[s,!!document.querySelector"
                                    "('#a3d-leftpanel '+s)])", DEAD)
        ck(all(not g[1] for g in gone2),
           "and still gone after a tab round trip (%s) -- the whiteboard's own setTab re-renders "
           "them, so a one-shot cleanup would pass on first load and fail on the first click"
           % gone2)
        ck(await page.evaluate("()=>!!document.querySelector('#a3d-leftpanel .a3d-tree')"),
           "while the BIM navigator is still nested in the panel, as it has been since V65")
        head = await page.evaluate("""()=>{
          const t=document.querySelector('.a3d-projtitle'),s=document.querySelector('.a3d-projsub');
          return [t&&t.textContent.trim(), s&&s.textContent.trim()];}""")
        ck('Canvas Mockup' not in str(head) and 'Drafts' not in str(head),
           "the file card no longer describes a whiteboard document (%s)" % head)
        await page.evaluate("()=>window.__a3dSetModelField('project','Bridge B-14')")
        await page.wait_for_timeout(400)
        head2 = await page.evaluate("()=>document.querySelector('.a3d-projtitle').textContent.trim()")
        ck(head2 == 'Bridge B-14',
           "it names the PROJECT, and follows it when the project is renamed (%s)" % head2)

        print("\n-- 3. every asset row does what its label says")
        wid = await page.evaluate("""()=>{
          window.__a3dTestSetObjs([]);
          const w=window.__a3dWall([[0,0],[6,0],[6,4],[0,4]],0.3,3,'center',true);
          window.__a3dSelectFor([w]);
          window.__a3dFamilyAdd({name:'Empty Family',category:'Site',mesh:{v:[],f:[]}});
          window.__a3dFamilyAdd({name:'Bollard',category:'Site',
                                 mesh:window.__a3dObjSnapshot(w).mesh});
          return w;}""")
        await tab(page, 'assets')
        rows = await page.evaluate("()=>window.__a3dAssetRows()")
        kinds = sorted(set(r['spec'].split(':')[0] for r in rows))
        # AMENDED AT V82, which restored the annotation library the user asked for. This asserted
        # exactly the four BIM libraries; it now asserts that all four are still THERE, rather than
        # that nothing else may ever be, so adding a library is not a failure while losing one
        # still is.
        ck(all(k in kinds for k in ('family', 'material', 'pattern', 'walltype')),
           "all four BIM libraries are present (%s)" % kinds)
        ck('note' in kinds,
           "alongside V82's annotation library, which lives in the same tab")

        ck(await page.evaluate("()=>window.__a3dAssetClick('material:Concrete')") is True,
           "a material row clicks")
        await page.wait_for_timeout(400)
        ck(await page.evaluate("(id)=>window.__a3dMaterialOf(id)", wid) == 'Concrete',
           "and the material reaches the MODEL, not just the panel")

        wt = [r for r in rows if r['spec'].startswith('walltype:')]
        t0 = await page.evaluate("(id)=>window.__a3dObjSnapshot(id).bim.thickness", wid)
        ck(await page.evaluate("(s)=>window.__a3dAssetClick(s)", wt[-1]['spec']) is True,
           "a wall-type row clicks (%s)" % wt[-1]['label'])
        await page.wait_for_timeout(450)
        t1 = await page.evaluate("(id)=>window.__a3dObjSnapshot(id).bim.thickness", wid)
        ck(t1 != t0,
           "and the wall is rebuilt to that type's thickness (%s -> %s m)" % (t0, t1))
        ck(await page.evaluate("()=>window.__a3dActiveWallType()")
           == wt[-1]['spec'].split(':', 1)[1],
           "and it becomes the active type for the next wall drawn")

        pat = [r for r in rows if r['spec'].startswith('pattern:')
               and r['spec'] != 'pattern:none'][0]
        ck(await page.evaluate("(s)=>window.__a3dAssetClick(s)", pat['spec']) is True,
           "a pattern row clicks (%s)" % pat['label'])
        await page.wait_for_timeout(400)
        ck(await page.evaluate("(id)=>window.__a3dResolveGraphics(id,'presentation').pattern", wid)
           == pat['spec'].split(':', 1)[1],
           "and it lands in the object's resolved presentation graphics")

        fam = [r for r in await page.evaluate("()=>window.__a3dAssetRows()")
               if r['spec'].startswith('family:') and r['live']][0]
        n0 = await page.evaluate("()=>window.__a3dState().objs.length")
        ck(await page.evaluate("(s)=>window.__a3dAssetClick(s)", fam['spec']) is True,
           "a family row clicks (%s)" % fam['label'])
        await page.wait_for_timeout(500)
        after = await page.evaluate("""()=>{const s=window.__a3dState();
          return {n:s.objs.length, sel:s.objs.filter(o=>o.id===s.sel).map(o=>o.name)[0]};}""")
        ck(after['n'] == n0 + 1,
           "and an object is actually added (%d -> %d)" % (n0, after['n']))
        ck(after['sel'] and after['sel'].startswith('Bollard'),
           "and left SELECTED (%s), so the V76 gizmo is already on it and the next gesture places "
           "it -- rather than leaving the user to hunt for something that appeared off screen"
           % after['sel'])

        print("\n-- 4. a row with no live target is disabled and says why")
        empty = [r for r in await page.evaluate("()=>window.__a3dAssetRows()")
                 if r['spec'].startswith('family:') and not r['live']]
        ck(len(empty) == 1 and 'geometry' in empty[0]['meta'],
           "the empty-geometry family is disabled and names the reason (%s) -- found by this "
           "suite: it advertised 'place', reported success, and added an object nobody could see"
           % (empty and empty[0]['meta']))
        ck(await page.evaluate("(s)=>window.__a3dAssetClick(s)", empty[0]['spec']) is False,
           "and clicking it does nothing rather than failing quietly")
        await page.evaluate("()=>window.__a3dSelectFor([])")
        await page.evaluate("()=>window.__a3dRefreshProps()")
        await tab(page, 'browser')
        await tab(page, 'assets')
        noSel = await page.evaluate("()=>window.__a3dAssetRows()")
        mats = [r for r in noSel if r['spec'].startswith('material:')]
        ck(all(not r['live'] for r in mats) and 'select' in mats[0]['meta'],
           "with nothing selected every material row is disabled and says what to do (%r)"
           % mats[0]['meta'])
        wts = [r for r in noSel if r['spec'].startswith('walltype:')]
        ck(all(r['live'] for r in wts),
           "while wall types stay live -- they set the ACTIVE type, which needs no selection")
        a = await page.evaluate("()=>window.__a3dShellAudit()")
        ck(a['ok'] is True, "and the audit is still clean with rows disabled (%s)" % a['claimed'])

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
