"""falsify_phase130.py -- break the V130 build one way at a time, keeping the marker.

Each variant takes back one thing V130 does, and the V130 suite must fail on every one of them.
Variant names are lower case: the runner reads no other (V126)."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # ---- 130a: the panel
    'hidden_acts_dropped': [("        if(seen[a])continue;", "        if(seen[a]||BIM_ACT_HIDE[a])continue;")],
    'unbuilt_runnable': [("'<button type=\"button\" class=\"a3d-rkrun\"'+(off?' disabled':' data-a3dr=\"'+bimEsc(a)+'\"')", "'<button type=\"button\" class=\"a3d-rkrun\"'+(' data-a3dr=\"'+bimEsc(a)+'\"')")],
    'kind_filter_ignored': [("      if(ok&&kind!=='all'&&e.getAttribute('data-rkkind')!==kind)ok=false;\n", "")],
    'pinned_category_ignored': [("      if(ok&&pinnedOnly&&e.getAttribute('data-rkpinned')!=='1')ok=false;\n", "")],
    'shown_count_missing': [("if(sh)sh.textContent=shown+' shown';", "")],
    'sort_not_applied': [("p.setAttribute('data-rksort',ev.target.value);bimSortShortcuts(p);", "p.setAttribute('data-rksort',ev.target.value);")],
    'name_sort_unsorted': [("      return an<bn?-1:(an>bn?1:0);", "      return 0;")],
    'used_sort_ignored': [("      if(how==='used'){var du=(+b.getAttribute('data-rkuse')||0)-(+a.getAttribute('data-rkuse')||0);if(du)return du;}\n", "")],
    'group_not_restored': [("      if(how==='group')return (+a.getAttribute('data-rkord'))-(+b.getAttribute('data-rkord'));", "      if(how==='group')return 0;")],
    'opens_on_last_kind': [("    p.setAttribute('data-rkkind','all');p.setAttribute('data-rksort','group');", "")],
    'panel_toggles_closed': [("    if(hp&&hp.classList.contains('open')&&hp.getAttribute('data-for')==='help')return true;\n    var b=document.querySelector('[data-a3drumenu=\"help\"]');", "    var b=document.querySelector('[data-a3drumenu=\"help\"]');")],
    'row_keeps_panel': [("ev.target.closest('.a3d-rkrun[data-a3dr]')){bimCloseRailPop();return;}", "ev.target.closest('.a3d-rkrun[data-a3dr]')){return;}")],
    'pin_count_stale': [("var pc=p.querySelector('.a3d-rkpinn');if(pc)pc.textContent=String(now.length);", "")],
    # ---- 130a: the dock and its pins
    'defaults_ignored': [("      set=A3D_DOCK_PIN_DEFAULTS[disc];", "      set=null;")],
    'pins_not_saved': [("p.dockPins[A3D_DISC_CUR]=pins;bimSaveUIPanelPrefs(p);", "A3D_DOCK_PIN_DEFAULTS[A3D_DISC_CUR]=pins;")],
    'pins_shared_by_disciplines': [("p.dockPins[A3D_DISC_CUR]=pins;bimSaveUIPanelPrefs(p);", "p.dockPins.arch=pins;bimSaveUIPanelPrefs(p);"),
                                   ("set=p.dockPins&&p.dockPins[disc]", "set=p.dockPins&&p.dockPins.arch")],
    'no_pin_max': [("if(pins.length>=A3D_DOCK_PIN_MAX){a3dToast('The dock holds '+A3D_DOCK_PIN_MAX+' tools: take one off first');return false;}", "")],
    'all_tools_dead': [("ev.target.closest('#a3d-dall')){ev.stopPropagation();bimOpenToolsPanel();return;}", "ev.target.closest('#a3d-dall')){ev.stopPropagation();return;}")],
    'dock_second_row': [("'</select><div class=\"a3d-dsep\"></div>'+", "'</select></div><div class=\"a3d-dockrow\">'+")],
    'dock_tall': [("#a3d-dock.a3d-docklabels .a3d-dbtn{width:60px;height:38px;", "#a3d-dock.a3d-docklabels .a3d-dbtn{width:60px;height:56px;")],
    'usage_not_counted': [("    if(it)bimCmdUsed(it.id);", "")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV130' in txt
out.write_text(txt, encoding='utf-8')
