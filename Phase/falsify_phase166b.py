"""falsify_phase166b.py -- break the V166b build one way at a time, keeping the marker.
Variant names are lower case: the runner reads no other (V126)."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # ---- Properties: three tabs, the usages on Project ----
    'analysis_tab_back': [("{id:'view',label:'View'}];", "{id:'view',label:'View'},{id:'analysis',label:'Analysis'}];")],
    'usages_untabbed': [("if(name==='Identity Data'||name==='Usages'||name==='Statistics'||name==='History')return 'project';", "if(name==='Identity Data'||name==='Statistics'||name==='History')return 'project';")],
    'usages_on_view': [("h+=bimPTab('project',bimPropGroup('Usages',bimUsageLibraryHtml()));", "h+=bimPTab('view',bimPropGroup('Usages',bimUsageLibraryHtml()));")],
    'remembered_tab_trusted': [("return bimPTabOk(v)?v:'project';", "return v||'project';")],
    'settab_unchecked': [("    if(!bimPTabOk(String(tab)))return false;\n", "    if(!tab)return false;\n")],
    # ---- Frame analysis's row ----
    'frame_settings_gone': [("      extra:bimAnzFrameHtml(),", "      extra:'',")],
    'settings_button_back': [("{act:'structure:off',label:'Hide',off:A3D_STRUCT.show?'':'Not shown'}]});", "{act:'structure:off',label:'Hide',off:A3D_STRUCT.show?'':'Not shown'},{act:'open:Analysis',label:'Settings'}]});")],
    'fields_unwired': [("      bimAnzWireFields(abox);   /* __acad3dV166b */\n", "")],
    'settings_not_redrawn': [("if(e.hasAttribute('data-propstr')){bimStructPropChange(ev);bimAnalyzeRefresh(true);return;}", "if(e.hasAttribute('data-propstr')){bimStructPropChange(ev);return;}")],
    'loads_not_redrawn': [("updateLevel(A3D.activeLevel,k,e.value);bimAnalyzeRefresh(true);", "updateLevel(A3D.activeLevel,k,e.value);")],
    'dead_as_live': [("id=\"a3d-anzf-dl\" data-anzload=\"dl\"", "id=\"a3d-anzf-dl\" data-anzload=\"ll\"")],
    'labels_unlinked': [("<label class=\"a3d-anzlab\" for=\"a3d-anzf-'+id+'\">'", "<label class=\"a3d-anzlab\">'")],
    'results_dropped': [("      h+=bimAnzKv(kv);\n", "")],
    'display_shows_off': [("var h='',cur=A3D_STRUCT.show?(A3D_STRUCT.diagram||'M'):'off',", "var h='',cur='off',")],
    'search_ignores_settings': [("'.a3d-anzttl,.a3d-anzst,.a3d-anzbtn,.a3d-anzlab,.a3d-anzsub'", "'.a3d-anzttl,.a3d-anzst,.a3d-anzbtn'")],
    'loads_unexplained': [("'</div><div class=\"a3d-anzcap\">What this level\\'s floors and roof put on the columns under them, in the Column Loads schedule and TRIBAREA. The active level is set in Properties, View.</div>'", "'</div>'")],
    'no_frame_no_loads': [("    if(lvA){\n      h+='<div class=\"a3d-anzsub\">Floor loads on '", "    if(lvA&&(nC||nB)){\n      h+='<div class=\"a3d-anzsub\">Floor loads on '")],
    # ---- Areas by usage's row ----
    'areas_gone': [("      extra:bimAnzAreasHtml(),", "      extra:'',")],
    'areas_no_total': [("    if(s.rows.length>1)h+='<div class=\"a3d-anzarea a3d-anzareatot\">", "    if(false)h+='<div class=\"a3d-anzarea a3d-anzareatot\">")],
    'areas_count_dropped': [("'<span class=\"a3d-anzarean\">'+g.count+'</span></div>'", "'<span class=\"a3d-anzarean\"></span></div>'")],
    'areas_gfa_as_gba': [("'<div class=\"a3d-anzareav\">GBA '+bimDispNum(g.GBA,2)+' \\u00b7 GFA '+bimDispNum(g.GFA,2)+", "'<div class=\"a3d-anzareav\">GBA '+bimDispNum(g.GBA,2)+' \\u00b7 GFA '+bimDispNum(g.GBA,2)+")],
    'usages_button_gone': [("      acts:[{act:'open:Usages',label:'Usages'}]});", "      acts:[]});")],
    'empty_unsaid': [("if(!s.rows.length)return '<div class=\"a3d-anzcap\">Give a room, a floor or a mass a usage in its Properties (USAGE).</div>';", "if(!s.rows.length)return '';")],
    # ---- the left panel's edge ----
    'width_fixed': [("#a3d-leftpanel{width:var(--a3d-lp-w,242px);", "#a3d-leftpanel{width:242px;")],
    'dock_fixed': [("(sh&&sh.classList.contains('collapsed'))?'54px':(BIM_LEFT_RAIL+w)+'px');", "(sh&&sh.classList.contains('collapsed'))?'54px':'296px');")],
    'width_not_kept': [("    bimLeftSave(p);bimShellDockW();   /*", "    bimShellDockW();   /*")],
    'kept_unread': [("return typeof p.w==='number'&&isFinite(p.w)?Math.max(BIM_LEFT_MIN,Math.min(bimLeftMax(),Math.round(p.w))):BIM_LEFT_MIN;", "return BIM_LEFT_MIN;")],
    'min_lower': [("BIM_LEFT_MIN=242,", "BIM_LEFT_MIN=160,")],
    'max_higher': [("BIM_LEFT_MAX=560,", "BIM_LEFT_MAX=900,")],
    'properties_ignored': [("Math.floor((window.innerWidth||0)-BIM_LEFT_RAIL-rw-BIM_LEFT_KEEP)", "Math.floor((window.innerWidth||0)-BIM_LEFT_RAIL-BIM_LEFT_KEEP)")],
    'properties_change_unheard': [("    bimShellDockW();   /* __acad3dV166b: the left panel keeps the drawing its room */\n", "")],
    'drag_not_live': [("      root.style.setProperty('--a3d-lp-w',w+'px');root.style.setProperty('--a3d-left-w',(BIM_LEFT_RAIL+w)+'px');\n", "")],
    'dblclick_dead': [("    g.addEventListener('dblclick',function(){bimLeftSetWidth(null);});\n", "")],
    # RE-ANCHORED IN V166c (cancel_kept, shift_step_same, not_a_separator): Properties' edge has the same lines
    'cancel_kept': [("g.addEventListener('pointercancel',function(ev){end(ev,false);});\n    g.addEventListener('dblclick',function(){bimLeftSetWidth(null);});", "g.addEventListener('pointercancel',function(ev){end(ev,true);});\n    g.addEventListener('dblclick',function(){bimLeftSetWidth(null);});")],
    'touch_refused': [("if(A3D_SHELL_TIER!=='desktop'||ev.button>0)return;", "if(A3D_SHELL_TIER!=='desktop'||ev.button>0||ev.pointerType==='touch')return;")],
    'keys_to_model': [("    if(tg.getAttribute&&tg.getAttribute('role')==='separator'&&tg.tabIndex>=0)return !(ev.ctrlKey||ev.metaKey||/^F\\d+$/.test(ev.key));   /* __acad3dV166b */\n", "")],
    'shift_step_same': [("var k=ev.key,st=ev.shiftKey?64:16;\n      if(k==='ArrowLeft'||k==='ArrowRight'){ev.preventDefault();bimLeftSetWidth(", "var k=ev.key,st=16;\n      if(k==='ArrowLeft'||k==='ArrowRight'){ev.preventDefault();bimLeftSetWidth(")],
    'home_end_swapped': [("bimLeftSetWidth(k==='Home'?BIM_LEFT_MIN:bimLeftMax());", "bimLeftSetWidth(k==='Home'?bimLeftMax():BIM_LEFT_MIN);")],
    'enter_focus_lost': [("var t=sh.querySelector('#a3d-rail .a3d-paneltoggle');if(t)t.focus();", "")],
    'edge_on_drawers': [("#a3d-shell.collapsed .a3d-lgrip,body.a3d-tier-overlay .a3d-lgrip{display:none}", "#a3d-shell.collapsed .a3d-lgrip{display:none}")],
    'drawer_moves_drawing': [("A3D_SHELL_TIER==='overlay'?'54px':   /* __acad3dV149: a drawer leaves the drawing where it is */\n        (sh&&sh.classList.contains('collapsed'))?'54px':(BIM_LEFT_RAIL+w)+'px');",
                              "A3D_SHELL_TIER==='overlay'?(BIM_LEFT_RAIL+w)+'px':\n        (sh&&sh.classList.contains('collapsed'))?'54px':(BIM_LEFT_RAIL+w)+'px');")],
    'finger_edge_thin': [(".a3d-lgrip{width:12px;left:calc(var(--a3d-left-w,296px) - 12px);", ".a3d-lgrip{width:6px;left:calc(var(--a3d-left-w,296px) - 6px);")],
    'not_a_separator': [("g.setAttribute('role','separator');g.setAttribute('aria-orientation','vertical');g.setAttribute('aria-controls','a3d-leftpanel');", "g.setAttribute('aria-orientation','vertical');g.setAttribute('aria-controls','a3d-leftpanel');")],
    'value_stale': [("if(g){g.setAttribute('aria-valuenow',String(w));", "if(g){")],
    # RETIRED IN V166b (drawing_not_resized): not caught, rightly -- the drawing has sized itself by a ResizeObserver since V72, so the edge's own size() did nothing; it is gone.
    'phone_fields_small': [("@media(pointer:coarse){.a3d-sa .a3d-anzform input[type=number]{min-height:36px;font-size:16px}", "@media(pointer:coarse){.a3d-sa .a3d-anzform input[type=number]{}")],
    # ---- the width by one press (166f) ----
    'step_button_dead': [("      if(ev.target&&ev.target.closest&&ev.target.closest('[data-lpwidth]')){bimLeftStep();return;}   /* __acad3dV166b */\n", "")],
    'steps_no_wrap': [("return w<mx?mx:BIM_LEFT_MIN;", "return w<mx?mx:w;")],
    'screen_max_skipped': [("return w<mx?mx:BIM_LEFT_MIN;", "return BIM_LEFT_MIN;")],
    'steps_past_screen': [("if(BIM_LEFT_STEPS[i]>w&&BIM_LEFT_STEPS[i]<=mx)return BIM_LEFT_STEPS[i];", "if(BIM_LEFT_STEPS[i]>w)return BIM_LEFT_STEPS[i];")],
    'button_label_stale': [("if(b){b.setAttribute('aria-label','Panel width '+w+' px: '+(nx>w?'widen to '+nx:'back to '+nx));b.title=b.getAttribute('aria-label');}", "if(b){}")],
    'button_on_drawers': [("body.a3d-tier-overlay .a3d-lpwbtn{display:none}\n", "")],
    'button_unclaimed': [("    {sel:'[data-lpwidth]',why:'widens the panel a step at a time: its edge, by one press'},   /* __acad3dV166b */\n", "")],
    'button_small': [(".a3d-lpwbtn{width:30px;height:30px;", ".a3d-lpwbtn{width:18px;height:18px;")],
    'collapse_white_on_light': [("body.light-theme .a3d-panelcollapse{color:#6b7280}\n", "")],
    # Not a variant: the edge's pointerdown refuses a phone's and an upright tablet's layout, but the edge
    # is not displayed there (edge_on_drawers), so no pointer reaches it.
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV166b' in txt
out.write_text(txt, encoding='utf-8')
