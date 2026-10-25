"""falsify_phase171b.py -- break the V171b build one way at a time, keeping the marker.
Variant names are lower case: the runner reads no other (V126). Each names, in its comment, the check
of tests/bim_phase171b_workspace_browser_tests.py that should catch it."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # ---- 1. the records ----
    'marker_lost': [("look,lightdark,ground,ctxtones,mapgrey,", "look,lightdark,ground,")],   # the V171b marker
    'version_old': [("var BIM_APP_VERSION={v:'V171',", "var BIM_APP_VERSION={v:'V170',")],   # V171 or later: a sub-phase keeps its phase's number
    'command_lost': [("['SITEWORKSPACE',['ANALYSISWORKSPACE','SAWORKSPACE','SITEWS'],", "['SITEWORKSPACE',['SAWORKSPACE','SITEWS'],")],   # ANALYSISWORKSPACE its alias
    'groups_order': [("{id:'see',name:'Views and noise',an:['views','noise']},", "{id:'see',name:'Views and noise',an:['noise','views']},")],   # in Analyze's order
    # ---- 2. before a run ----
    'cross_stays': [("      if(c==='leave')r=bimAwLeave();\n", "      if(c==='leave')r=false;\n")],   # the bar's cross leaves
    'leave_list_kept': [("    if(w)w.innerHTML=bimAnalyzeHtml();\n", "")],   # out of it: Analyze's rows back
    # ---- 3. Analyze site ends in it ----
    'run_no_workspace': [("        bimAwAfterRun();   /* __acad3dV171b", "        0&&bimAwAfterRun();   /* __acad3dV171b")],   # Analyze site ends in the workspace
    'run_all_shown': [("    if(!bimDgState().last){S.focus=null;S.add=[];}\n    bimUndoHold=true;\n    try{bimAwApply(false);}finally{bimUndoHold=held;}\n    bimAwOpen();",
                       "    if(!bimDgState().last){S.focus=null;S.add=[];}\n    bimUndoHold=true;\n    bimUndoHold=held;\n    bimAwOpen();")],   # none drawn: the site and its context
    'run_own_step': [("    if(!bimDgState().last){S.focus=null;S.add=[];}\n    bimUndoHold=true;\n", "    if(!bimDgState().last){S.focus=null;S.add=[];}\n    bimUndoHold=false;pushUndo();\n")],   # inside the run's one undo step
    'list_not_shown': [("      if(A3D_AW.on){bimRenderInto(w,bimAwListHtml());return true;}   /* __acad3dV171b */\n", "")],   # the list: 23 rows in the six groups
    'dock_shown': [("body.a3d-aw #a3d-dock,body.a3d-aw .a3d-tpal{display:none!important}", "body.a3d-aw .a3d-tpal{display:none!important}")],   # nothing to draw with on screen
    # ---- 4. one at a time ----
    'focus_not_alone': [("      v=A.id===S.focus||S.add.indexOf(A.id)>=0;\n", "      v=A.id===S.focus||S.add.indexOf(A.id)>=0||ly.visible!==false;\n")],   # another name: it alone, the first gone
    'focus_no_undo': [("      pushUndo();   /* the step taken before the change,", "      0&&pushUndo();   /* the step taken before the change,")],   # one undo step
    'focus_undo_late': [("      pushUndo();   /* the step taken before the change, so undoing it gives the focus back with the layers */\n      S.focus=a;S.add=add;\n",
                         "      S.focus=a;S.add=add;\n      pushUndo();\n")],   # undone: Sun paths again
    'bar_stale': [("    if(A3D_AW.on||document.getElementById('a3d-awbar'))bimAwBar();\n", "")],   # undone: ... the bar
    'row_unpressed': [("(a===f?' focus':'')+(on&&a!==f?' add':'')+rs.cls", "(on&&a!==f?' add':'')+rs.cls")],   # its row: in focus, ticked, pressed
    # ---- 5. ticks ----
    'tick_ignored': [("    else if(S.add.indexOf(a)<0)S.add.push(a);\n", "")],   # a tick draws Street hierarchy under Noise
    'key_top_right': [("      if(bimAwLook()){LY.X=sr.x+12;LY.Y=Math.max(sr.y+12,sr.y+sr.h-LY.h-12);}", "      if(0){LY.X=sr.x+12;}")],   # at the view's bottom left
    'focus_untick_kept': [("    if(on){if(S.focus===a)S.focus=null;", "    if(on){")],   # the focus unticked: none in focus
    # ---- 6. the look ----
    'ground_dark': [("    var awB=bimAwBg();gl.clearColor(awB[0],awB[1],awB[2],1);", "    var awB=bimAwBg();gl.clearColor(0.114,0.125,0.141,1);")],   # the view's ground is the mode's
    'look_one_mode': [("return document.body.classList.contains('light-theme')?BIM_AW_LOOK.light:BIM_AW_LOOK.dark;", "return BIM_AW_LOOK.dark;")],   # light mode: the view's ground
    'ctx_untoned': [("    return c.by?(c.col[o.id]||null):bimAwCtxCol(o);", "    return c.by?(c.col[o.id]||null):null;")],   # the terrain near the camera / the context's tones drawn
    'terrain_untoned': [("      col=bimHexToRgb(sel?'#4ea1ff':(bimAwCtxCol(o)||o.col||'#b08559'));   /* __acad3dV171b */\n      gl.uniform3f",
                         "      col=bimHexToRgb(sel?'#4ea1ff':(o.col||'#b08559'));\n      gl.uniform3f")],   # the terrain near the camera in its quiet tone
    'terrain_draped': [("      if(plan.tiles.length&&rec.ext&&!bimAwLook()){", "      if(plan.tiles.length&&rec.ext){")],   # no map draped on it
    'roads_untoned': [("(o.id===A3D.sel)?'#4ea1ff':(bimAwCtxCol(o)||lk.color),(o.closed!==false)", "(o.id===A3D.sel)?'#4ea1ff':lk.color,(o.closed!==false)")],   # Market Street's line in the road tone
    'map_colour': [("c=mix(c,vec3(dot(c,vec3(0.299,0.587,0.114))),uGrey);", "c=c;")],   # the map in the workspace: grey
    'map_bright': [("r.opacity=st.opacity*(bimAwLook()?bimAwLook().fade:1);", "r.opacity=st.opacity;")],   # and faded toward the light ground
    'ink_kept': [("    if(!L.light)return col;\n    var c=bimAwRgb(col)", "    return col;\n    var c=bimAwRgb(col)")],   # a light word's colour darkened
    'panel_pale': [("body.light-theme .a3d-awl,body.light-theme .a3d-awp{color:#1f2328}", "body.light-theme .a3d-awl{color:#1f2328}")],   # the panel's title in the mode's ink
    'bar_dark': [("body.light-theme .a3d-awbar-row,body.light-theme .a3d-awchip{background:rgba(255,255,255,.96);", "body.light-theme .a3d-awchip{background:rgba(255,255,255,.96);")],   # the bar in the mode's colours
    # ---- 7. the panel ----
    'panel_props': [("      if(A3D_AW.on){bimRenderInto(el.propsbody,bimAwPanelHtml());return;}   /* __acad3dV171b: the one analysis */\n", "")],   # the panel is the overview / names it
    'key_partial': [("    return '<div class=\"a3d-awp-key\">'+rows.map(", "    return '<div class=\"a3d-awp-key\">'+rows.slice(0,2).map(")],   # its key in full
    'chart_lost': [("      if(a==='wind'&&Hh&&Hh.wind&&Hh.wind.year&&Hh.wind.year.n){", "      if(0){")],   # the winds' rose
    'panel_deaf': [("      if(t.hasAttribute('data-awact'))bimAwAct(t.getAttribute('data-awact'));\n", "")],   # Select selects its elements
    'title_kept': [("    t.textContent=on?'Analysis':'Properties';", "    t.textContent='Properties';")],   # Properties' title says Analysis
    # ---- 8. traffic ----
    'traffic_no_focus': [("    traffic:function(){if(bimTrCommand(true))bimAwTraffic();", "    traffic:function(){if(bimTrCommand(true))0;")],   # TRAFFIC: in focus in the workspace
    'traffic_two_steps': [("    S.focus='traffic';S.add=S.add.filter(function(x){return x!=='traffic';});\n    bimUndoHold=true;\n",
                           "    pushUndo();S.focus='traffic';S.add=S.add.filter(function(x){return x!=='traffic';});\n    bimUndoHold=true;\n")],   # in the command's one undo step
    'traffic_cars_map': [("  function bimMvLight(){var L=bimAwLook();if(L)return L.light;", "  function bimMvLight(){")],   # (the look: the cars follow the mode; read in section 6 through the panel's colours)
    # ---- 9. in and out ----
    'leave_hides': [("    A3D_AW.on=false;\n    document.body.classList.remove('a3d-aw');\n", "    A3D_AW.on=false;\n    document.body.classList.remove('a3d-aw');\n    bimAwState().focus=null;bimAwState().add=[];bimAwApply(false);\n")],   # what was shown stays shown
    'open_lost': [("          {act:'aw:open:'+A.id,label:'Open',", "          {act:'aw:open:'+A.id+'x',label:'Open',")],   # a row's Open
    'rerun_resets': [("    if(!bimDgState().last){S.focus=null;S.add=[];}\n", "    S.focus=null;S.add=[];\n")],   # Analyze site again keeps the focus and the ticks
    'again_missing': [("(D.last&&placed?' <button type=\"button\" class=\"a3d-awl-again\"", "(0?' <button type=\"button\" class=\"a3d-awl-again\"")],   # Analyze site again, from the list
    # ---- 10. a phone ----
    'phone_drawer': [("    if(bimShellTier()==='phone'){var sh=document.getElementById('a3d-shell');if(sh)sh.classList.add('collapsed');}   /* a phone: the view, not the drawer */\n", "")],   # the drawer closed, the view in sight
    'chips_unscrolled': [("row.scrollLeft=Math.max(0,on.offsetLeft-12);", "row.scrollLeft=0;")],   # the one in focus in view
    'details_dead': [("      else if(c==='panel'){var rp=document.getElementById('a3d-right');if(rp){rp.classList.toggle('open');refreshProps();}r=!!rp;}\n", "")],   # Details opens the panel
    'phone_no_key': [("    if(sr.w<(bimAwLook()?280:620))return null;", "    if(sr.w<620)return null;")],   # the key of the one in focus on a phone's view
    # ---- 11. a row that fits ----
    'row_squeezed': [(".a3d-anzhd>.a3d-anztog{min-width:96px}", ".a3d-anzhd>.a3d-anztog{min-width:0}")],   # Traffic's row keeps its name in sight
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV171b' in txt
out.write_text(txt, encoding='utf-8')
