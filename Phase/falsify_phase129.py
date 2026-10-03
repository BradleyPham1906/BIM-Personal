"""falsify_phase129.py -- break the V129 build one way at a time, keeping the marker.

Each variant takes back one thing V129 does, and the V129 suite must fail on every one of them.
Variant names are lower case: the runner reads no other (V126)."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # ---- 129a: the shortcuts panel
    'panel_not_centred': [("    if(id==='help'){left=Math.max(8,(window.innerWidth-pw)/2);top=Math.max(8,(window.innerHeight-ph)/2);}   /* __acad3dV129 */\n", "")],
    'panel_not_a_sheet': [("    p.classList.toggle('a3d-rksheet',id==='help');", "    p.classList.toggle('a3d-rksheet',false);")],
    'no_question_key': [("        if(e.key==='?'&&window.__a3dRunCmd){e.preventDefault();window.__a3dRunCmd('shortcuts');return;}\n", "")],
    # RETIRED IN V130: 'shortcuts_toggles_closed' removed SHORTCUTS' own already-open guard. V130 moved the
    # guard into bimOpenToolsPanel, which every way in (SHORTCUTS, ?, All tools) goes through; V130's
    # 'panel_toggles_closed' removes it there.
    'no_categories': [("      nav+='<button type=\"button\" class=\"a3d-rkcat\" data-rkcat=", "      if(0)nav+='<button type=\"button\" class=\"a3d-rkcat\" data-rkcat=")],
    'category_ignored': [("ok=(cat==='all'||e.getAttribute('data-rkg')===cat)&&words.every(", "ok=words.every(")],
    'category_not_marked': [("cats[ci].setAttribute('aria-pressed',on?'true':'false');", "")],
    'category_any_click': [("ev.target.closest('.a3d-rkcat[data-rkcat]'):null;", "ev.target.closest('[data-rkcat]'):null;")],
    'category_scroll_kept': [("          var lst=p.querySelector('.a3d-rukeys');if(lst)lst.scrollTop=0;\n", "")],
    'category_kept_on_reopen': [("    p.setAttribute('data-rkcat','all');\n", "")],
    'no_close_button': [("        if(ev.target&&ev.target.closest&&ev.target.closest('[data-rkclose]')){bimCloseRailPop();return;}\n", "")],
    'keys_left': [("#a3d-rupop.a3d-rksheet .a3d-rkkeys{flex:none;justify-content:flex-end}", "#a3d-rupop.a3d-rksheet .a3d-rkkeys{flex:none;justify-content:flex-start}")],
    'no_cmd_column': [("(r.cmd?'type '+bimEsc(r.cmd):'')", "''")],
    'typing_points_in_drawing': [("      {keys:['Arrows'],k:null,label:'Nudge the selected object'}\n    ]},\n    /* __acad3dV129: the grammar of a typed point is not a key: a group of its own, saying when */\n    {grp:'Typing points',note:'While a tool is taking points, type a position instead of clicking, then press Enter.',rows:[\n",
                                  "      {keys:['Arrows'],k:null,label:'Nudge the selected object'},\n")],
    'no_typing_note': [("      if(g.note)list+='<div class=\"a3d-rkgnote\"", "      if(0)list+='<div class=\"a3d-rkgnote\"")],
    'note_outlives_its_rows': [("{if(grp){grp.hidden=!any;if(note)note.hidden=!any;}grp=e;note=null;", "{if(grp){grp.hidden=!any;}grp=e;note=null;")],
    # ---- 129b: the dock
    # RE-ANCHORED IN V130: the dock's buttons are the pinned tools, built in one loop over pins[i]
    'no_dock_names': [("(names?'<span class=\"a3d-dblbl\">'+bimEsc(a3drLabel(a))+'</span>':'')", "''")],
    # RETIRED IN V130: 'no_group_labels' removed the names under the dock's groups. The owner found the
    # dock crowded and it became one row of pinned tools, with no groups to name.
    # RE-ANCHORED IN V130: the pinned tools' button
    'native_title_back': [("h+='<button type=\"button\" class=\"a3d-dbtn\" data-a3dr=\"'+a+'\" data-a3dtip=", "h+='<button type=\"button\" class=\"a3d-dbtn\" title=\"'+bimEsc(a3drLabel(a))+'\" data-a3dr=\"'+a+'\" data-a3dtip=")],
    # RETIRED IN V130: 'bare_caret' put the bare triangle back on the groups' More buttons, which went
    # with the groups; All tools opens the rest.
    # RE-ANCHORED IN V130: the one-row dock's pill reads Search
    'search_icon_only': [("A3DR_SEARCH_ICON+'<span>Search</span><kbd>'+bimEsc(A3D_MODKEY)+' K</kbd></button>'", "A3DR_SEARCH_ICON+'</button>'")],
    # RETIRED IN V130: 'dock_tall' made the labelled buttons 56px; a one-row dock stays far inside this
    # suite's 150px, so it is V130's suite that holds the dock to 60px, and V130's 'dock_tall' that tests it.
    'no_tooltip_delay': [("A3D_TIP.timer=setTimeout(function(){A3D_TIP.timer=null;bimTipShow(tg);},350);", "A3D_TIP.timer=setTimeout(function(){A3D_TIP.timer=null;bimTipShow(tg);},0);")],
    'no_hover_tooltip': [("A3D_TIP.timer=setTimeout(function(){A3D_TIP.timer=null;bimTipShow(tg);},350);", "")],
    'tooltip_not_on_focus': [("      bimTipHide();if(tg&&tg.matches(':focus-visible'))bimTipShow(tg);", "      bimTipHide();")],
    'tooltip_stays_on_leave': [("      if(tg&&!(ev.relatedTarget&&tg.contains(ev.relatedTarget)))bimTipHide();", "")],
    'tooltip_escape_ignored': [("    host.addEventListener('keydown',function(ev){if(ev.key==='Escape')bimTipHide();});\n", "")],
    'no_describedby': [("    target.setAttribute('aria-describedby','a3d-tip');A3D_TIP.at=target;", "    A3D_TIP.at=target;")],
    'tooltip_no_type': [("    if(d.type.length)h+='<div class=\"a3d-tiptype\">", "    if(0)h+='<div class=\"a3d-tiptype\">")],
    'unbuilt_not_flagged': [("    if(a3drIsUnimpl(spec))return {name:a3drLabel(spec),keys:null,desc:'Not built yet',type:[],where:'',off:true};\n", "")],
    'tooltip_below': [("top=r.top-hh-10;", "top=r.bottom+10;")],
    'icons_only_ignored': [("  function bimDockLabelsOn(){var p=bimLoadUIPanelPrefs();return p.dockLabels!==false;}", "  function bimDockLabelsOn(){return true;}")],
    'labels_choice_forgotten': [("    var p=bimLoadUIPanelPrefs();p.dockLabels=!!on;bimSaveUIPanelPrefs(p);", "    window.__a3dDockLblMem=!!on;"),
                                ("  function bimDockLabelsOn(){var p=bimLoadUIPanelPrefs();return p.dockLabels!==false;}", "  function bimDockLabelsOn(){return window.__a3dDockLblMem!==false;}")],
    'no_appearance_rows': [("        '<div class=\"a3d-rusep\"></div>'+   /* __acad3dV129 */\n", "        ''+\n"),
                           ("        '<button class=\"a3d-ruitem'+(bimDockLabelsOn()?' on':'')+'\" data-a3druitem=\"appear:docknames\">Tool names on the dock</button>'+\n", ""),
                           ("        '<button class=\"a3d-ruitem'+(bimDockLabelsOn()?'':' on')+'\" data-a3druitem=\"appear:dockicons\">Icons only</button>';", "        '';")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV129' in txt
out.write_text(txt, encoding='utf-8')
