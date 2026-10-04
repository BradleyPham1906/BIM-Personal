"""falsify_phase148.py -- break the V148 build one way at a time, keeping the marker.
Variant names are lower case: the runner reads no other (V126)."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # ---- the list
    'one_group': [("C.forEach(function(c){c.group=BIM_ANZ_GROUP_OF[c.id]||'model';});", "C.forEach(function(c){c.group='model';});")],
    'rows_open': [("var open=!!A3D_ANZ.open[c.id],a0=c.acts[0]", "var open=true,a0=c.acts[0]")],
    'toggle_redraws': [("    if(c){c.classList.toggle('open',v);b=c.querySelector('[data-anztog]');if(b)b.setAttribute('aria-expanded',String(v));}",
                        "    if(c&&w){w.innerHTML=bimAnalyzeHtml();}")],
    'open_forgotten': [("    try{localStorage.setItem(BIM_ANZ_KEY,JSON.stringify(A3D_ANZ.open));}catch(eS){}\n", "")],
    'off_chip_shown': [(".a3d-anzstate-off{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap;border:0}",
                        ".a3d-anzstate-off{background:transparent;color:#6e7781}")],
    'first_action_hidden': [("(c.state?'<span class=\"a3d-anzstate a3d-anzstate-'+c.state+'\">'+bimAnzStateText(c.state)+'</span>':'')+(a0?bimAnzBtn(a0):'')+'</div>'+",
                             "(c.state?'<span class=\"a3d-anzstate a3d-anzstate-'+c.state+'\">'+bimAnzStateText(c.state)+'</span>':'')+'</div>'+"),
                            ("var open=!!A3D_ANZ.open[c.id],a0=c.acts[0],rest=c.acts.slice(1)", "var open=!!A3D_ANZ.open[c.id],a0=c.acts[0],rest=c.acts.slice(0)")],
    'cards_tall': [(".a3d-anzsum{font-size:11px;color:#8a96a3;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:1px}",
                    ".a3d-anzsum{font-size:11px;color:#8a96a3;margin-top:1px}")],
    # ---- the search
    'search_substring': [("    for(i=0;i<W.length;i++)if(W[i]&&s.indexOf(' '+W[i])<0)return false;", "    for(i=0;i<W.length;i++)if(W[i]&&s.indexOf(W[i])<0)return false;")],
    'search_no_group': [("function(e){return e.textContent;}).join(' ')+' '+(hd?hd.textContent:''));", "function(e){return e.textContent;}).join(' '));")],
    'search_no_buttons': [("R[j].querySelectorAll('.a3d-anzttl,.a3d-anzst,.a3d-anzbtn')", "R[j].querySelectorAll('.a3d-anzttl,.a3d-anzst')")],
    'search_lost_on_refresh': [("      if(rows&&cnt){C=bimAnzCards();bimRenderInto(rows,bimAnzRowsHtml(C));cnt.textContent=bimAnzCountText(C);}\n      else w.innerHTML=bimAnalyzeHtml();",
                                "      w.innerHTML=bimAnalyzeHtml();")],
    'empty_not_said': [("    if(e){if(n)e.setAttribute('hidden','');else e.removeAttribute('hidden');}", "    if(e)e.setAttribute('hidden','');")],
    # RETIRED IN V148: Chromium empties a type=search field on Escape itself and fires input, so the
    # handler is unreachable in the suite's browser; it stays for the browsers that do not.
    #   [("...ev.key==='Escape'&&s.value)", "...ev.key==='Esc'&&s.value)")],
    # ---- add as layer
    'layer_act_dead': [("    else if(k.indexOf('layer:')===0)bimResultLayerAdd(k.slice(6));   /* __acad3dV148 */\n", "")],
    'layer_before_run': [("return {act:'layer:'+id,label:'Add as layer',lay:true,tip:tip,off:!s?'Run it first':bimResHolds(s)?'This run is a layer already':''};",
                          "return {act:'layer:'+id,label:'Add as layer',lay:true,tip:tip,off:bimResHolds(s)?'This run is a layer already':''};")],
    'same_run_twice': [("      if(bimResHolds(s)){a3dToast('This run is a layer already');return null;}\n", ""),
                       ("off:!s?'Run it first':bimResHolds(s)?'This run is a layer already':''", "off:!s?'Run it first':''")],
    'ramp_rounded': [("a.push(s.roof[k]?'.':String(Math.min(m-1,Math.floor(", "a.push(s.roof[k]?'.':String(Math.min(m-1,Math.round(")],
    'roof_painted': [("a.push(s.roof[k]?'.':String(", "a.push(false?'.':String(")],
    'drawn_twice': [("      if(s&&s.show!==false&&!bimResHolds(s)){", "      if(s&&s.show!==false){")],
    'not_drawn': [("    if(!capMode)drawResultLayers(ctx,V,W,H); /* __acad3dV148: the results kept as layers, over the live ones */\n", "")],
    'never_stale': [("  function bimResStale(R){return !!(R&&R.kind!=='terrain'&&R.key&&R.key!==bimResKey(R.kind));}", "  function bimResStale(R){return false;}")],
    'stale_from_add': [("R.run=s.runId;R.key=bimResKeyFrom(s.stamp,R.kind);}", "R.run=s.runId;R.key=bimResKey(R.kind);}")],
    'update_site_date': [("    if(R.kind==='sunhours'){r=bimSunHours({date:R.data&&R.data.date});", "    if(R.kind==='sunhours'){r=bimSunHours({});")],
    'update_no_undo': [("    if(R.kind==='rain')R.src=r.terrain;\n    R.key=bimResKeyFrom(r.stamp,R.kind);R.updated=bimResNow();",
                        "    UNDO_STACK.pop();\n    if(R.kind==='rain')R.src=r.terrain;\n    R.key=bimResKeyFrom(r.stamp,R.kind);R.updated=bimResNow();")],
    'terrain_colours_kept': [("    if(o&&o.tview===mode)delete o.tview;   /* the surface's own colours step aside for the layer's */\n", "")],
    'gone_not_said': [("    return !(o&&o.t==='terrain'&&o.survey)||(R.mode==='cutfill'&&!o.grading);", "    return false;")],
    'cutfill_twice': [("off:!o?'Grade first':bimResLayers().some(function(R){return R.kind==='terrain'&&R.mode==='cutfill'&&R.src===o.id;})?'Its cut and fill is a layer already':''",
                       "off:!o?'Grade first':''")],
    'bad_mode_ok': [("      if(!BIM_TVIEW_LABEL.hasOwnProperty(mode)||(mode==='cutfill'&&!o.grading)){", "      if(mode==='cutfill'&&!o.grading){")],
    # ---- the stack
    'new_at_bottom': [("    bimResLayers().unshift(R);   /* a new layer goes on top */", "    bimResLayers().push(R);")],
    'draw_order_reversed': [("    for(i=L.length-1;i>=0;i--){\n      if(L[i].visible===false)continue;", "    for(i=0;i<L.length;i++){\n      if(L[i].visible===false)continue;")],
    'drop_refused': [("      else if(A3D_LY.drag&&A3D_LY.drag.indexOf('rl:')===0&&inLyp(t)&&t.closest('[data-lyres^=\"res:\"]'))ev.preventDefault();\n", "")],
    'move_no_undo': [("    pushUndo();\n    R=L.splice(i,1)[0];L.splice(j,0,R);", "    R=L.splice(i,1)[0];L.splice(j,0,R);")],
    'move_index_ignored': [("    if(typeof to==='number'&&isFinite(to))j=Math.max(0,Math.min(L.length-1,Math.round(to)));\n", "")],
    # ---- the rows
    'eye_dead': [("    if((b=t.closest('[data-lyreson]'))){bimLyResVisible(b.getAttribute('data-lyreson'));return true;}", "    if((b=t.closest('[data-lyreson]'))){return true;}")],
    'opacity_steps': [("    if(!A3D_LY.opWas||A3D_LY.opWas.k!==k)A3D_LY.opWas={k:k,had:T.hasOwnProperty('opacity'),v:T.opacity};\n    T.opacity=v;",
                       "    bimLyResSetOpacity(k,v*100);")],
    'opacity_not_live': [("    T.opacity=v;\n    lab=inp.parentNode?", "    lab=inp.parentNode?")],
    'opacity_unclamped': [("v=Math.max(0.1,Math.min(1,v>1?v/100:v));v=Math.round(v*100)/100;}\n    else if(field==='name'){v=String(val==null?'':val).replace(/\\s+/g,' ').replace(/^ | $/g,'').slice(0,60);if(!v){a3dToast('A layer needs a name');refreshLayers();return false;}}\n    else return false;\n    if(field==='visible'?",
                           "v=v>1?v/100:v;}\n    else if(field==='name'){v=String(val==null?'':val).replace(/\\s+/g,' ').replace(/^ | $/g,'').slice(0,60);if(!v){a3dToast('A layer needs a name');refreshLayers();return false;}}\n    else return false;\n    if(field==='visible'?")],
    'escape_renames': [("    A3D_LY.redit=null;\n    if(!cancel)bimLyResRename(k,inp.value);", "    A3D_LY.redit=null;\n    bimLyResRename(k,inp.value);")],
    'empty_name_ok': [("if(!v){a3dToast('A layer needs a name');refreshLayers();return false;}}\n    else return false;\n    if(field==='visible'?", "}\n    else return false;\n    if(field==='visible'?")],
    'remove_no_undo': [("    pushUndo();\n    nm=L[i].name;L.splice(i,1);delete A3D_RES_IMG[id];", "    nm=L[i].name;L.splice(i,1);delete A3D_RES_IMG[id];")],
    'sections_in_tree': [("    return h+'</div>'+bimLySectionsHtml(f)+'</div>';", "    return h+bimLySectionsHtml(f)+'</div></div>';")],
    'section_stays_open': [("      var open=!!f||!shut[key];", "      var open=true;")],
    'search_misses_sections': [("    function hit(s){return !f||String(s).toLowerCase().indexOf(f)>=0;}\n    bimResLayers()", "    function hit(s){return true;}\n    bimResLayers()")],
    # ---- the data layers
    'data_eye_own': [("    var ok=bimDataSet(s.id,'visible',!T.visible);", "    T.visible=!T.visible;var ok=true;paint();")],
    'data_opacity_own': [("    ok=bimDataSet(s.id,'opacity',v);", "    T.opacity=v/100;ok=true;")],
    'data_not_listed': [("    bimDataList().forEach(function(L){if(hit(L.name))db+=bimLyDataRowHtml(L);});", "")],
    'data_add_unseen': [("    refreshProps();saveSoon();bimLayersPanelRefresh();   /* __acad3dV148 */", "    refreshProps();saveSoon();")],
    'data_settings_dead': [("    if((b=t.closest('[data-lyresset]'))){bimAnzAct('open:Data Layers');return true;}", "    if((b=t.closest('[data-lyresset]'))){return true;}")],
    # ---- saved
    'not_saved': [("history:A3D.history||null,resultLayers:A3D.resultLayers||[]};   /* __acad3dV146, __acad3dV148 */", "history:A3D.history||null};")],
    'not_in_file': [("history:A3D.history||null,resultLayers:A3D.resultLayers||[]}});   /* __acad3dV146, __acad3dV148 */", "history:A3D.history||null}});")],
    'not_validated': [("  function bimResValid(a){\n    if(!Array.isArray(a))return [];", "  function bimResValid(a){\n    if(Array.isArray(a))return a;\n    if(!Array.isArray(a))return [];")],
    'not_in_undo': [("classifications:A3D.classifications,resultLayers:A3D.resultLayers||[]});   /* __acad3dV148 */", "classifications:A3D.classifications});")],
    'history_clears': [("    if(Array.isArray(st.resultLayers))A3D.resultLayers=st.resultLayers;", "    A3D.resultLayers=Array.isArray(st.resultLayers)?st.resultLayers:[];")],
    # ---- a phone, a tablet, a computer
    'tree_over_phone': [("body.a3d-tree-docked #a3d-shell:not([data-tab=\"browser\"]) #a3d-leftpanel > .a3d-tree{display:none!important}", "")],
    'touch_rows_small': [(".a3d-anzhd{min-height:46px}", ".a3d-anzhd{min-height:36px}")],
    'touch_buttons_small': [(".a3d-anzbtn{min-height:34px;padding:0 12px;font-size:12.5px}", ".a3d-anzbtn{padding:0 12px;font-size:12.5px}")],
    'touch_sections_small': [(".a3d-lysechd{height:40px}", ".a3d-lysechd{height:28px}")],
    'audit_unclaimed': [("    {sel:'[data-anztog]',why:'an analysis row: opens and closes it, to its whole status, legend and other actions'},   /* __acad3dV148 */\n", "")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV148' in txt
out.write_text(txt, encoding='utf-8')
