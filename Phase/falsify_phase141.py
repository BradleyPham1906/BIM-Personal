"""falsify_phase141.py -- break the V141 build one way at a time, keeping the marker.

Each variant takes back one thing V141 does, and the V141 suite must fail on every one of them.
Variant names are lower case: the runner reads no other (V126)."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    'no_tab_strip': [("    h+=bimPropTabsHtml();   /* __acad3dV141: Project | Site | View | Analysis */\n", "")],
    'all_panes_shown': [(".a3d-ptabpane{display:none}.a3d-ptabpane.on{display:block}", ".a3d-ptabpane{display:block}")],
    'map_on_project': [("    h+=bimPTab('site',bimPropGroup('Map',bimMapPropsHtml()));", "    h+=bimPTab('project',bimPropGroup('Map',bimMapPropsHtml()));")],
    'statistics_on_analysis': [("    h+=bimPTab('project',bimPropGroup('Statistics',srows));", "    h+=bimPTab('analysis',bimPropGroup('Statistics',srows));")],
    'no_location_group': [("    h+=bimPTab('site',bimPropGroup('Location',loc));   /* __acad3dV141 */", "    h+=bimPTab('project',bimPropGroup('Identity Data',loc));")],
    'tab_not_remembered': [("    try{localStorage.setItem(BIM_PTAB_KEY,tab);}catch(eS){}\n    if(el.propsbody){", "    if(el.propsbody){")],
    'tab_rerenders': [("    bimSetPropTab(b.getAttribute('data-ptabbtn'));\n    return true;", "    A3D_PTAB=b.getAttribute('data-ptabbtn');refreshProps();\n    return true;")],
    'aria_not_kept': [("B[i].classList.toggle('on',on);B[i].setAttribute('aria-selected',String(on));", "B[i].classList.toggle('on',on);")],
    'bad_tab_taken': [("    if(!/^(project|site|view|analysis)$/.test(String(tab)))return false;\n    A3D_PTAB=tab;", "    A3D_PTAB=tab;")],
    'reveal_no_tab': [("    if(tb){A3D_PTAB=tb;try{localStorage.setItem(BIM_PTAB_KEY,tb);}catch(eS){}}", "")],
    'usages_not_revealed': [("    bimPropReveal('Usages');   /* __acad3dV141: on the Analysis tab */", "    A3D_PROP_GROUPS_OPEN['Usages']=true;")],
    'datalayers_not_revealed': [("    bimPropReveal('Data Layers');   /* __acad3dV141: on the Site tab */", "    A3D_PROP_GROUPS_OPEN['Data Layers']=true;")],
    # RE-ANCHORED FOR V159: the button carries its phone label (data-short) since V149
    'no_rail_button': [("      '<button type=\"button\" class=\"a3d-railbtn\" data-tab=\"analyze\" data-short=\"Analyze\" title=\"Analyze\" aria-label=\"Analyze\">'+   /* __acad3dV141 */\n      bimRailIcon('analyze')+'</button>'+\n", "")],
    # RE-ANCHORED FOR V159: the analyses are one of Analyze's two views
    'panel_not_built': [("    if(shell.dataset.tab==='analyze'&&!saView&&!panel.querySelector('.a3d-analyze-wrap')){   /* __acad3dV141 */", "    if(false){")],
    'panel_stale': [("    bimAnalyzeRefresh();   /* __acad3dV141 */\n", "")],
    'run_not_wired': [("    if(k==='structure:run')bimAnalyzeCommand();", "    if(k==='structure:run'){}")],
    'open_keeps_selection': [("      A3D.sel=null;A3D.sel2=null;A3D.selSet=[];\n      bimPropReveal(g);", "      bimPropReveal(g);")],
    'frame_run_always_enabled': [("off:fr?'':'Place columns and beams first'},\n        {act:'structure:off'", "off:''},\n        {act:'structure:off'")],
    'lod_last_not_kept': [("    A3D_ANZ.lod={valid:ok,bad:badL.slice()};   /* __acad3dV141: the Analyze tab shows the last check */\n", "")],
    'unclaimed': [("    {sel:'[data-anzact]',why:'an analysis: run it, show or hide it, or open its settings in Properties'},\n", "")],
    'no_command': [("    analyses:function(){bimAnalyzeCommandTab();},                 /* __acad3dV141 */\n", "")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV141' in txt
out.write_text(txt, encoding='utf-8')
