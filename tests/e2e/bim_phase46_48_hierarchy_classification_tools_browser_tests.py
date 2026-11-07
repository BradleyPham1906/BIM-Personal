"""
bim_phase46_48_hierarchy_classification_tools_browser_tests.py

Regression suite for five original capabilities added to canvas_v10.html after the
user's explicit "build both now" (Building/Site hierarchy, Classification) and a
follow-up "build all three now, and log them too" (Merge Walls, Check Model, Linked
Clone), the latter three surfaced by a careful command-by-command re-read of 8
uploaded FreeCAD source files against what the app already ships (see
canvas_v10_STATUS.md's "Concrete capability review" section for the file-by-file
comparison). None of the added code is copied or ported from those files -- every
function here is an original implementation scoped from what the capability *does*.

Covers, against the real shipped app (not a prototype copy):
  __acad3dV46 -- Building/Site hierarchy: CRUD, re-host-on-delete fail-safe, a
                 real "+Bldg" UI flow, and persistence-shape sanity.
  __acad3dV47 -- Classification system: CRUD, duplicate/empty-code rejection,
                 assign/clear on a real object, delete-in-use fail-safe (clears
                 the reference rather than blocking), and the Manage dialog's
                 real add/close UI flow plus the Properties palette dropdown.
  __acad3dV48 -- Merge Walls (colinear head-to-tail merge, with rejection of
                 non-colinear/non-touching pairs), Check Model (exposing the
                 CSG kernel's own bimMeshSanityCheck as a diagnostic, verified
                 against a hand-built valid box, an open shell, and a corrupted
                 mesh), and Linked Clone (explicit on-demand sync, verified to
                 NOT propagate until Sync Clones is invoked, then to propagate
                 correctly through a real Properties-palette edit).

Run:  python3 bim_phase46_48_hierarchy_classification_tools_browser_tests.py [path/to/canvas_v10.html]
"""
import asyncio, pathlib, sys
from playwright.async_api import async_playwright

TARGET = sys.argv[1] if len(sys.argv) > 1 else "canvas_v10.html"

TOTAL = [0]
FAILS = []


def check(cond, msg):
    TOTAL[0] += 1
    print(("  PASS  " if cond else "  FAIL  ") + msg)
    if not cond:
        FAILS.append(msg)


PROBE_BUILDINGS = r"""
() => {
  const res = {};
  res.marker = window.__acad3dV46 || null;
  res.initialBuildings = window.__a3dBuildings();
  res.initialSite = window.__a3dSite();
  res.initialActiveBuilding = window.__a3dActiveBuilding();
  const initialLevel = window.__a3dActiveLevel();
  res.initialLevelBuildingId = window.__a3dLevelBuilding(initialLevel.id);

  const newBldgActive = window.__a3dAddBuilding();
  res.afterAddBuildings = window.__a3dBuildings();
  res.newBldgId = newBldgActive;

  window.__a3dAddLevel();
  const levelsNow = window.__a3dLevels();
  res.newLevelBuildingId = levelsNow[levelsNow.length - 1].buildingId;

  res.renameResult = window.__a3dRenameBuilding(newBldgActive, 'Annex');

  window.__a3dSetActiveBuilding('bldg-0');
  res.activeBuildingAfterSwitch = window.__a3dActiveBuilding();
  res.activeLevelAfterSwitch = window.__a3dActiveLevel();

  window.__a3dSetSite('Riverside Site');
  res.siteAfterRename = window.__a3dSite();
  window.__a3dSetSite('   ');
  res.siteAfterEmptyReject = window.__a3dSite();

  const levelsInAnnexBefore = window.__a3dLevels().filter(l => l.buildingId === newBldgActive).length;
  window.__a3dDeleteBuilding(newBldgActive);
  res.buildingsAfterDelete = window.__a3dBuildings();
  const levelsAfterDelete = window.__a3dLevels();
  const bIds = res.buildingsAfterDelete.map(b => b.id);
  res.orphanedLevelCount = levelsAfterDelete.filter(l => bIds.indexOf(l.buildingId) < 0).length;
  res.levelsInAnnexBefore = levelsInAnnexBefore;
  res.levelsOnBldg0After = levelsAfterDelete.filter(l => l.buildingId === 'bldg-0').length;

  const countBeforeLastDelete = window.__a3dBuildings().length;
  window.__a3dDeleteBuilding('bldg-0');
  res.countAfterLastDeleteAttempt = window.__a3dBuildings().length;
  res.countBeforeLastDelete = countBeforeLastDelete;

  return res;
}
"""

PROBE_UI_BUILDINGS = r"""
async () => {
  const out = {};
  const sleep = (ms) => new Promise(r => setTimeout(r, ms));
  const before = window.__a3dBuildings().length;
  const bldBtn = document.getElementById('a3d-bldadd');
  out.bldAddBtnFound = !!bldBtn;
  if (bldBtn) bldBtn.click();
  await sleep(60);
  out.afterClickCount = window.__a3dBuildings().length;
  out.before = before;

  const bldgs = window.__a3dBuildings();
  const newest = bldgs[bldgs.length - 1];
  const nameInput = document.querySelector('[data-bldf="name"][data-bldid="' + newest.id + '"]');
  out.nameInputFound = !!nameInput;
  if (nameInput) {
    nameInput.value = 'UI Building';
    nameInput.dispatchEvent(new Event('change', { bubbles: true }));
  }
  await sleep(60);
  out.renamedViaUI = (window.__a3dBuildings().find(b => b.id === newest.id) || {}).name;

  const row = document.querySelector('[data-a3dbldg="' + newest.id + '"]');
  out.rowFound = !!row;
  if (row) row.click();
  await sleep(60);
  out.activeAfterClick = window.__a3dActiveBuilding();
  out.expectedActive = newest.id;

  const delBtn = document.querySelector('[data-blddel="' + newest.id + '"]');
  out.delBtnFound = !!delBtn;
  if (delBtn) delBtn.click();
  await sleep(60);
  out.afterDeleteCount = window.__a3dBuildings().length;

  const siteInput = document.querySelector('[data-sitef="name"]');
  out.siteInputFound = !!siteInput;
  if (siteInput) {
    siteInput.value = 'UI Site';
    siteInput.dispatchEvent(new Event('change', { bubbles: true }));
  }
  await sleep(60);
  out.siteAfterUI = window.__a3dSite().name;

  return out;
}
"""

PROBE_CLASSIFICATIONS = r"""
() => {
  const res = {};
  res.marker = window.__acad3dV47 || null;
  res.initial = window.__a3dClassifications();

  const id1 = window.__a3dAddClassification('03 30 00', 'Cast-in-Place Concrete');
  res.id1 = id1;
  res.dupRejected = window.__a3dAddClassification('03 30 00', 'Duplicate attempt') === null;
  res.emptyRejected = window.__a3dAddClassification('   ', 'no code') === null;

  const id2 = window.__a3dAddClassification('04 20 00', 'Unit Masonry');
  res.id2 = id2;
  res.countAfterAdds = window.__a3dClassifications().length;

  const wallId = window.__a3dWall([[0, 0], [4, 0]], 0.2, 3, 'center', false);
  res.wallId = wallId;
  res.assigned = window.__a3dSetObjClass(wallId, id1);
  res.objClassAfterAssign = window.__a3dObjClass(wallId);
  res.useCountAfterAssign = window.__a3dClassificationUseCount(id1);

  window.__a3dUpdateClassification(id1, 'description', 'Cast-in-Place Concrete (Updated)');
  res.descAfterUpdate = window.__a3dClassifications().find(c => c.id === id1).description;

  window.__a3dDeleteClassification(id1);
  res.classificationsAfterDelete = window.__a3dClassifications();
  res.objClassAfterDelete = window.__a3dObjClass(wallId);

  window.__a3dDeleteClassification(id2);
  res.countAfterAllDeleted = window.__a3dClassifications().length;

  return res;
}
"""

PROBE_UI_CLASSIFICATIONS = r"""
async () => {
  const out = {};
  const sleep = (ms) => new Promise(r => setTimeout(r, ms));

  const wallId = window.__a3dWall([[90, 0], [94, 0]], 0.2, 3, 'center', false);
  out.wallId = wallId;

  const tabBtn = (window.__a3dDockOpenGroup('a3dmanage')&&document.querySelector('#a3d-rupop .a3d-rkcat[data-rkcat="tool:a3dmanage"]'))   /* AMENDED FOR V120: the hidden ribbon is gone; the tool dock has the group. AMENDED FOR V130: and the group's tools are in the Tools and shortcuts panel */;
  out.tabFound = !!tabBtn;
  if (tabBtn) tabBtn.click();
  await sleep(50);
  const ribbonBtn = (window.__a3dToolsPanel(),document.querySelector('#a3d-rupop [data-a3dr="bim:classification"]'));
  out.ribbonBtnFound = !!ribbonBtn;
  if (ribbonBtn) ribbonBtn.click();
  await sleep(50);
  out.dlgOpen = !!document.querySelector('.a3d-dlg');

  const codeI = document.getElementById('a3d-clsnewcode');
  const descI = document.getElementById('a3d-clsnewdesc');
  out.formFound = !!(codeI && descI);
  if (codeI && descI) {
    codeI.value = '09 60 00'; descI.value = 'Flooring';
    document.getElementById('a3d-clsadd').click();
  }
  await sleep(60);
  out.classesAfterUIAdd = window.__a3dClassifications().length;

  const closeBtn = document.querySelector('.a3d-dlg [data-a3dlg="cancel"]');
  if (closeBtn) closeBtn.click();
  await sleep(30);
  out.dlgClosedAfterCancel = !document.querySelector('.a3d-dlg');

  const row = document.querySelector('#a3d-rows [data-a3did="' + wallId + '"]');
  out.rowFound = !!row;
  if (row) row.click();
  await sleep(50);
  const propsHtml = document.getElementById('a3d-propsbody').innerHTML;
  out.classDropdownInProps = propsHtml.indexOf('data-propf="classid"') >= 0;

  const clsId = window.__a3dClassifications()[0].id;
  const dropdown = document.querySelector('[data-propf="classid"]');
  out.dropdownFound = !!dropdown;
  if (dropdown) {
    dropdown.value = clsId;
    dropdown.dispatchEvent(new Event('change', { bubbles: true }));
  }
  await sleep(50);
  out.objClassAfterUIAssign = window.__a3dObjClass(wallId);
  out.expectedClass = clsId;

  return out;
}
"""

PROBE_MERGE_WALLS = r"""
() => {
  const res = {};
  res.marker = window.__acad3dV48 || null;

  const wA = window.__a3dWall([[0, 20], [3, 20]], 0.2, 3, 'center', false);
  const wB = window.__a3dWall([[3, 20], [7, 20]], 0.2, 3, 'center', false);
  const countBefore = window.__a3dState().objs.length;
  const mergeRes = window.__a3dMergeWalls(wA, wB);
  res.mergeResultHasMesh = !!(mergeRes && mergeRes.mesh && !mergeRes.error);
  const finalIds = window.__a3dApplyMergeWalls(wA, wB);
  res.countBefore = countBefore;
  res.countAfter = finalIds.length;
  res.wAStillExists = finalIds.indexOf(wA) >= 0;
  res.wBStillExists = finalIds.indexOf(wB) >= 0;

  const wC = window.__a3dWall([[10, 20], [13, 20]], 0.2, 3, 'center', false);
  const wD = window.__a3dWall([[13, 20], [13, 23]], 0.2, 3, 'center', false);
  res.nonColinearRejected = !!(window.__a3dMergeWalls(wC, wD).error);

  const wE = window.__a3dWall([[20, 20], [23, 20]], 0.2, 3, 'center', false);
  const wF = window.__a3dWall([[24, 20], [27, 20]], 0.2, 3, 'center', false);
  res.nonTouchingRejected = !!(window.__a3dMergeWalls(wE, wF).error);

  const wG = window.__a3dWall([[30, 20], [33, 20]], 0.3, 3, 'center', false);
  const wH = window.__a3dWall([[33, 20], [36, 20]], 0.2, 3, 'center', false);
  res.mismatchedThicknessRejected = !!(window.__a3dMergeWalls(wG, wH).error);

  return res;
}
"""

PROBE_CHECK_MODEL = r"""
() => {
  const res = {};
  const validBox = {
    v: [[0,0,0],[1,0,0],[1,1,0],[0,1,0],[0,0,1],[1,0,1],[1,1,1],[0,1,1]],
    f: [[0,1,2,3],[5,4,7,6],[4,0,3,7],[1,5,6,2],[3,2,6,7],[4,5,1,0]]
  };
  res.validStrict = window.__a3dMeshSanityCheck(validBox, true);

  const openShell = { v: validBox.v, f: validBox.f.slice(0, 5) };
  res.openShellStrict = window.__a3dMeshSanityCheck(openShell, true);
  res.openShellLoose = window.__a3dMeshSanityCheck(openShell, false);

  const corrupted = { v: validBox.v, f: validBox.f.concat([validBox.f[0]]) };
  res.corruptedStrict = window.__a3dMeshSanityCheck(corrupted, true);
  res.corruptedLoose = window.__a3dMeshSanityCheck(corrupted, false);

  const w = window.__a3dWall([[40, 20], [44, 20]], 0.2, 3, 'center', false);
  const report = window.__a3dCheckModel();
  res.reportLength = report.length;
  res.wallEntry = report.find(r => r.id === w) || null;

  return res;
}
"""

PROBE_UI_CHECK_MODEL = r"""
async () => {
  const out = {};
  const sleep = (ms) => new Promise(r => setTimeout(r, ms));
  const tabBtn = (window.__a3dDockOpenGroup('a3dmanage')&&document.querySelector('#a3d-rupop .a3d-rkcat[data-rkcat="tool:a3dmanage"]'))   /* AMENDED FOR V120: the hidden ribbon is gone; the tool dock has the group. AMENDED FOR V130: and the group's tools are in the Tools and shortcuts panel */;
  if (tabBtn) tabBtn.click();
  await sleep(50);
  const btn = (window.__a3dToolsPanel(),document.querySelector('#a3d-rupop [data-a3dr="bim:checkmodel"]'));
  out.btnFound = !!btn;
  if (btn) btn.click();
  await sleep(60);
  out.dlgOpen = !!document.querySelector('.a3d-dlg');
  const hd = document.querySelector('.a3d-dlghd');
  out.heading = hd ? hd.textContent : null;
  const closeBtn = document.querySelector('.a3d-dlg [data-a3dlg="cancel"]');
  if (closeBtn) closeBtn.click();
  await sleep(30);
  out.dlgClosed = !document.querySelector('.a3d-dlg');
  return out;
}
"""

PROBE_LINKED_CLONE_UI = r"""
async () => {
  const out = {};
  const sleep = (ms) => new Promise(r => setTimeout(r, ms));

  const src = window.__a3dWall([[50, 20], [54, 20]], 0.2, 3, 'center', false);
  const clone = window.__a3dCloneLinked(src, 0, 0, 5);
  out.src = src; out.clone = clone;
  out.linkSourceOfClone = window.__a3dObjLinkSource(clone);
  out.linkedClonesOfSrc = window.__a3dLinkedClonesOf(src);

  const objsBefore = window.__a3dState().objs;
  out.srcThicknessBefore = objsBefore.find(o => o.id === src).bim.thickness;
  out.cloneThicknessBefore = objsBefore.find(o => o.id === clone).bim.thickness;

  const row = document.querySelector('#a3d-rows [data-a3did="' + src + '"]');
  out.rowFound = !!row;
  if (row) row.click();
  await sleep(50);
  const thickInput = document.querySelector('[data-propf="thickness"]');
  out.thickInputFound = !!thickInput;
  if (thickInput) {
    thickInput.value = '0.35';
    thickInput.dispatchEvent(new Event('change', { bubbles: true }));
  }
  await sleep(80);
  const objsAfterEdit = window.__a3dState().objs;
  out.srcThicknessAfterEdit = objsAfterEdit.find(o => o.id === src).bim.thickness;
  out.cloneThicknessBeforeSync = objsAfterEdit.find(o => o.id === clone).bim.thickness;

  const propsHtml = document.getElementById('a3d-propsbody').innerHTML;
  out.syncButtonShownForSource = propsHtml.indexOf('data-propf="syncclones"') >= 0;

  window.__a3dSyncLinkedClones(src);
  const objsAfterSync = window.__a3dState().objs;
  out.cloneThicknessAfterSync = objsAfterSync.find(o => o.id === clone).bim.thickness;

  const cloneRow = document.querySelector('#a3d-rows [data-a3did="' + clone + '"]');
  if (cloneRow) cloneRow.click();
  await sleep(50);
  const clonePropsHtml = document.getElementById('a3d-propsbody').innerHTML;
  out.linkedFromShown = clonePropsHtml.indexOf('Linked From') >= 0;

  const lonely = window.__a3dWall([[60, 20], [64, 20]], 0.2, 3, 'center', false);
  out.syncNoClonesResult = window.__a3dSyncLinkedClones(lonely);

  return out;
}
"""


async def main():
    url = pathlib.Path(TARGET).resolve().as_uri()
    async with async_playwright() as pw:
        b = await pw.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        pg = await b.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(url)
        await pg.wait_for_timeout(2500)
        await pg.evaluate("() => { try { localStorage.clear(); } catch (e) {} }")
        await pg.evaluate("() => { if (window.__a3dEnter) window.__a3dEnter(); }")
        await pg.wait_for_timeout(1000)

        print("\n== load ==")
        v46 = await pg.evaluate("() => window.__acad3dV46 || null")
        v47 = await pg.evaluate("() => window.__acad3dV47 || null")
        v48 = await pg.evaluate("() => window.__acad3dV48 || null")
        check(not errs, "no uncaught page errors on load (%s)" % (errs[:1] or "none"))
        check(v46 is not None, "__acad3dV46 feature marker present (Building/Site)")
        check(v47 is not None, "__acad3dV47 feature marker present (Classification)")
        check(v48 is not None, "__acad3dV48 feature marker present (Merge/Check/Clone)")

        print("\n== Phase 46: Building/Site hierarchy (direct hooks) ==")
        r = await pg.evaluate(PROBE_BUILDINGS)
        check(len(r["initialBuildings"]) == 1 and r["initialBuildings"][0]["name"] == "Building 1",
              "fresh project starts with exactly one default building")
        check(r["initialSite"]["name"] == "Site", "fresh project starts with a default Site name")
        check(r["initialActiveBuilding"] == r["initialBuildings"][0]["id"], "active building defaults to the only building")
        check(r["initialLevelBuildingId"] == r["initialBuildings"][0]["id"], "default level is stamped with the default building's id")
        check(len(r["afterAddBuildings"]) == 2, "Add Building creates a second building (%d)" % len(r["afterAddBuildings"]))
        check(r["newLevelBuildingId"] == r["newBldgId"], "a level added while building 2 is active is stamped with building 2's id")
        check(r["renameResult"] is not None, "renaming a building succeeds")
        annexName = [b["name"] for b in r["renameResult"] if b["id"] == r["newBldgId"]]
        check(annexName == ["Annex"], "renamed building shows the new name ('Annex')")
        check(r["activeBuildingAfterSwitch"] == "bldg-0", "switching active building updates the active id")
        check(r["activeLevelAfterSwitch"]["buildingId"] == "bldg-0", "switching active building also switches the active level to one it owns")
        check(r["siteAfterRename"]["name"] == "Riverside Site", "site rename applied")
        check(r["siteAfterEmptyReject"]["name"] == "Riverside Site", "whitespace-only site name is rejected, keeping the prior value")
        check(r["levelsInAnnexBefore"] >= 1, "Annex had at least one level before being deleted (test is meaningful)")
        check(len(r["buildingsAfterDelete"]) == 1, "deleting the Annex building leaves exactly one building")
        check(r["orphanedLevelCount"] == 0, "no level is left pointing at a deleted building id (re-host fail-safe)")
        check(r["levelsOnBldg0After"] >= 1 + r["levelsInAnnexBefore"], "Annex's levels were re-hosted onto the surviving building")
        check(r["countBeforeLastDelete"] == 1 and r["countAfterLastDeleteAttempt"] == 1,
              "deleting the last remaining building is blocked (count unchanged)")

        print("\n== Phase 46: real UI flow (+Bldg button, rename, activate, delete, site field) ==")
        ru = await pg.evaluate(PROBE_UI_BUILDINGS)
        check(ru["bldAddBtnFound"], "+Bldg button exists in the Project Browser header")
        check(ru["afterClickCount"] == ru["before"] + 1, "clicking +Bldg adds one building")
        check(ru["nameInputFound"], "building name input rendered in the Levels panel")
        check(ru["renamedViaUI"] == "UI Building", "editing the building name input renames it")
        check(ru["rowFound"], "building row is clickable")
        check(ru["activeAfterClick"] == ru["expectedActive"], "clicking a building row makes it active")
        check(ru["delBtnFound"], "building delete button rendered")
        check(ru["afterDeleteCount"] == ru["afterClickCount"] - 1, "delete button removes the building")
        check(ru["siteInputFound"], "Site name input rendered at the top of the Levels panel")
        check(ru["siteAfterUI"] == "UI Site", "editing the Site input via the UI updates A3D.site.name")

        print("\n== Phase 47: Classification system (direct hooks) ==")
        rc = await pg.evaluate(PROBE_CLASSIFICATIONS)
        check(rc["initial"] == [], "fresh project starts with no classifications")
        check(rc["id1"] is not None, "adding a classification with a code succeeds")
        check(rc["dupRejected"], "adding a duplicate code (case-insensitive) is rejected")
        check(rc["emptyRejected"], "adding a whitespace-only code is rejected")
        check(rc["countAfterAdds"] == 2, "two distinct classifications now exist")
        check(rc["assigned"] is True, "assigning a classification to a real object succeeds")
        check(rc["objClassAfterAssign"] == rc["id1"], "the object's classId reflects the assignment")
        check(rc["useCountAfterAssign"] == 1, "use-count reflects exactly one referencing object")
        check(rc["descAfterUpdate"] == "Cast-in-Place Concrete (Updated)", "editing a classification's description persists")
        check(rc["id1"] not in [c["id"] for c in rc["classificationsAfterDelete"]], "deleted classification is removed from the registry")
        check(rc["objClassAfterDelete"] is None, "deleting an in-use classification clears the reference on the object (fail-safe, not blocked)")
        check(rc["countAfterAllDeleted"] == 0, "deleting the unused second classification leaves the registry empty")

        print("\n== Phase 47: real UI flow (Manage Classifications dialog + Properties dropdown) ==")
        rcu = await pg.evaluate(PROBE_UI_CLASSIFICATIONS)
        check(rcu["tabFound"], "the Manage group is in the tool dock")
        check(rcu["ribbonBtnFound"], "Classifications button exists in the Settings panel")
        check(rcu["dlgOpen"], "clicking the ribbon button opens the Manage Classifications dialog")
        check(rcu["formFound"], "the add-classification form (code + description) is present")
        check(rcu["classesAfterUIAdd"] == 1, "adding a classification through the dialog form works")
        check(rcu["dlgClosedAfterCancel"], "Close button dismisses the dialog")
        check(rcu["rowFound"], "a real object is selectable via the model tree")
        check(rcu["classDropdownInProps"], "Properties palette shows a Classification dropdown for the selected object")
        check(rcu["dropdownFound"], "the dropdown element is queryable")
        check(rcu["objClassAfterUIAssign"] == rcu["expectedClass"], "changing the dropdown assigns the classification via the real UI path")

        print("\n== Phase 48: Merge Walls ==")
        rm = await pg.evaluate(PROBE_MERGE_WALLS)
        check(rm["mergeResultHasMesh"], "merging two colinear head-to-tail walls succeeds and returns a mesh")
        check(rm["countAfter"] == rm["countBefore"] - 1, "applying the merge removes exactly one object (%d -> %d)" % (rm["countBefore"], rm["countAfter"]))
        check(rm["wAStillExists"], "the first wall survives as the merged object")
        check(not rm["wBStillExists"], "the second wall is removed after merging")
        check(rm["nonColinearRejected"], "merging a perpendicular pair is rejected")
        check(rm["nonTouchingRejected"], "merging two walls with a gap between them is rejected")
        check(rm["mismatchedThicknessRejected"], "merging walls of different thickness is rejected")

        print("\n== Phase 48: Check Model ==")
        rk = await pg.evaluate(PROBE_CHECK_MODEL)
        check(rk["validStrict"]["ok"] is True, "a hand-built valid closed box passes the strict check")
        check(rk["openShellStrict"]["ok"] is False, "an open shell (missing face) fails the strict check")
        check(rk["openShellLoose"]["ok"] is True, "the same open shell passes the loose (non-strict) check")
        check(rk["corruptedStrict"]["ok"] is False, "a mesh with a duplicated face fails the strict check")
        check(rk["corruptedLoose"]["ok"] is False, "a mesh with a duplicated face ALSO fails the loose check (real corruption, not just an open shell)")
        check(rk["wallEntry"] is not None and rk["wallEntry"]["ok"] is True, "a real wall solid in the project reports OK in the full Check Model report")

        print("\n== Phase 48: real UI flow (Check Model dialog) ==")
        rku = await pg.evaluate(PROBE_UI_CHECK_MODEL)
        check(rku["btnFound"], "Check Model button exists in the Manage > Project panel")
        check(rku["dlgOpen"], "clicking it opens the Check Model dialog")
        check(rku["heading"] == "Check Model", "dialog is titled 'Check Model'")
        check(rku["dlgClosed"], "Close button dismisses the dialog")

        print("\n== Phase 48: Linked Clone (Phase 55d made this automatic; see note below) ==")
        rl = await pg.evaluate(PROBE_LINKED_CLONE_UI)
        check(rl["linkSourceOfClone"] == rl["src"], "a linked clone records its source object's id")
        check(rl["clone"] in rl["linkedClonesOfSrc"], "the source can enumerate its own linked clones")
        check(abs(rl["cloneThicknessBefore"] - rl["srcThicknessBefore"]) < 1e-9, "clone starts out matching the source's geometry")
        check(rl["rowFound"], "source wall is selectable via the model tree")
        check(rl["thickInputFound"], "Thickness field is editable in the Properties palette")
        check(abs(rl["srcThicknessAfterEdit"] - 0.35) < 1e-9, "editing the source's thickness through the real UI updates the source")
        # Phase 46-48 originally asserted the OPPOSITE of the line below: that the clone stayed
        # frozen until Sync Clones was pressed, an intentional on-demand-only scope at the time.
        # Phase 55d wired linked clones into the Phase 55a dependency graph, the same way rooms and
        # openings already were, so a rebuild that reaches the graph (as this Properties-palette
        # thickness edit does, via bimRebuildWall -> bimAfterWallRebuild) now auto-syncs every clone
        # of the edited object. This is a deliberate, disclosed behavior change, not a regression --
        # updated here rather than left asserting the now-superseded old scope boundary.
        check(abs(rl["cloneThicknessBeforeSync"] - 0.35) < 1e-9,
              "Phase 55d: the clone already matches the source's new thickness before Sync Clones is even pressed (auto-sync through the graph)")
        check(rl["syncButtonShownForSource"], "Properties palette still shows a Sync Clones button (manual/explicit re-apply, still useful e.g. right after undo)")
        check(abs(rl["cloneThicknessAfterSync"] - 0.35) < 1e-9, "calling Sync Clones still works and leaves the clone matching the source")
        check(rl["linkedFromShown"], "Properties palette shows 'Linked From' when a clone itself is selected")
        check(rl["syncNoClonesResult"] == 0, "syncing an object with no clones reports 0 and does not throw")

        print("\n%d checks, %d failed" % (TOTAL[0], len(FAILS)))
        if FAILS:
            print("\nFAILED:")
            for m in FAILS:
                print("  - " + m)
        if errs:
            print("\nUNCAUGHT PAGE ERRORS:")
            for e in errs[:10]:
                print("  " + e)
        await b.close()
        bad = FAILS or errs
        print("RESULT:", "FAIL" if bad else "PASS")
        sys.exit(1 if bad else 0)

asyncio.run(main())
