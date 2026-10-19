"""falsify_phase164.py -- break the V164 build one way at a time, keeping the marker.
Variant names are lower case: the runner reads no other (V126)."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # ---- the engine: live and editable ----
    'edits_overwritten': [("        if(bimDgEdited(x)){\n          if(x.dg.gen!==gen)x.dg.newer=true;", "        if(false){\n          if(x.dg.gen!==gen)x.dg.newer=true;")],
    'deleted_return': [("      keys.push(e.k);\n      if(gone[e.k])continue;\n", "      keys.push(e.k);\n")],
    'orphans_dropped': [("      if(bimDgEdited(have[k])){have[k].dg.orphan=true;kept++;}", "      if(false){have[k].dg.orphan=true;kept++;}")],
    'newer_unmarked': [("          if(x.dg.gen!==gen)x.dg.newer=true;\n", "")],
    'reset_leaves_move': [("    o.dg.g=c.g;o.dg.s=c.s;o.dg.lb=c.lb;o.dg.sym=c.sym;o.pos=[0,0,0];delete o.dg.newer;\n    refreshProps();paint();saveSoon();\n    a3dToast(o.name+' is as the analysis drew it again');",
                           "    o.dg.g=c.g;o.dg.s=c.s;o.dg.lb=c.lb;o.dg.sym=c.sym;delete o.dg.newer;\n    refreshProps();paint();saveSoon();\n    a3dToast(o.name+' is as the analysis drew it again');")],
    'reset_analysis_keeps_all': [("      A3D.objs=A3D.objs.filter(function(x){return !(bimIsDiag(x)&&x.dg.a===a);});\n      D.runs[a].gone=[];D.runs[a].keys=[];", "      D.runs[a].gone=[];D.runs[a].keys=[];")],
    'edit_is_move_only': [("    return !!(q[0]||q[1]||q[2])||!o.dg.gen||bimDgCore(o.dg)!==o.dg.gen;", "    return !!(q[0]||q[1]||q[2])||!o.dg.gen;")],
    'copy_keeps_key': [("    copy.dg={a:o.dg.a,k:o.dg.k+'#'+copy.id,g:g.g,s:JSON.parse(JSON.stringify(o.dg.s||{})),lb:g.lb,sym:g.sym,info:JSON.parse(JSON.stringify(o.dg.info||{})),gen:''};",
                        "    copy.dg={a:o.dg.a,k:o.dg.k,g:g.g,s:JSON.parse(JSON.stringify(o.dg.s||{})),lb:g.lb,sym:g.sym,info:JSON.parse(JSON.stringify(o.dg.info||{})),gen:o.dg.gen};")],
    'turn_not_applied': [("    else if(g.kind==='diag'){o.dg.g=g.g;o.dg.lb=g.lb;o.dg.sym=g.sym;}   /* __acad3dV164 */\n    else if(g.kind==='alignment'){o.pis=g.pis;if(g.pv&&o.profileView)o.profileView.at=g.pv;if(g.k!==1)o.radii=(o.radii||[]).map(function(r){return r*g.k;});}   /* __acad3dV127: a scaled route keeps its shape */\n    return true;\n  }\n  function startRotateTool",
                          "    else if(g.kind==='alignment'){o.pis=g.pis;if(g.pv&&o.profileView)o.profileView.at=g.pv;if(g.k!==1)o.radii=(o.radii||[]).map(function(r){return r*g.k;});}   /* __acad3dV127: a scaled route keeps its shape */\n    return true;\n  }\n  function startRotateTool")],
    'live_turned': [("      if(o.dg.g.kind==='live')return {error:'A live shadow follows the sun and the model: it cannot be turned, mirrored or scaled'};\n", "")],
    'no_undo_hold': [("    if(undoSuspend||bimUndoHold)return;", "    if(undoSuspend)return;")],
    'sublayers_flat': [("ly=(key===a)?bimDgAnLayer(a):bimDgLayer(key,sub?sub.name:key,sub?sub.col:bimDgAn(a).col,a,!!(sub&&sub.hidden));",
                        "ly=(key===a)?bimDgAnLayer(a):bimDgLayer(key,sub?sub.name:key,sub?sub.col:bimDgAn(a).col,null,!!(sub&&sub.hidden));")],
    'solstices_shown': [("      if(hidden)ly.visible=false;\n", "")],
    'mesh_given': [("A3D.objs.push({id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'diag',name:String(e.name||e.k).slice(0,80),layer:lay(e.layer),pos:[0,0,0],",
                    "A3D.objs.push({id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'diag',mesh:{v:[],f:[]},name:String(e.name||e.k).slice(0,80),layer:lay(e.layer),pos:[0,0,0],")],
    'bounds_ignored': [("      }else if(bimIsDiag(o)){   /* __acad3dV164: a diagram's points, labels and symbols */\n        var dgb=bimDgBounds(o);\n        for(j=0;j<dgb.length;j++)for(k=0;k<3;k++){if(dgb[j][k]<mn[k])mn[k]=dgb[j][k];if(dgb[j][k]>mx[k])mx[k]=dgb[j][k];any=true;}\n", "")],
    # ---- drawing, picking, Properties ----
    'not_picked_first': [("    var dgp=bimPickDiag(x,y);   /* __acad3dV164: the site analysis, drawn over the model */\n    if(dgp)return dgp;\n", "")],
    'locked_picked': [("      if(!o||!bimLayerPickable(o))continue;\n      for(j=0;j<H[i].boxes.length;j++)", "      if(!o)continue;\n      for(j=0;j<H[i].boxes.length;j++)")],
    'hidden_drawn': [("        if(!bimLayerShown(L[i]))continue;\n        if(over)A3D_DG.hits.push(", "        if(over)A3D_DG.hits.push(")],
    'shadows_not_drawn': [("    if(g.kind==='live'){bimDgDrawShadow(ctx,V,W,H,o,a);return;}", "    if(g.kind==='live'){return;}")],
    'context_casts': [("      if(!o||o.context)return false;", "      if(!o)return false;")],
    # RE-ANCHORED IN V165: the key's layout is bimDgLegendLayout's, apart from its drawing
    'legend_ignores_off': [("    if(D.legendOff)return null;\n    for(i=0;i<BIM_DG_AN.length;i++){\n      var A=BIM_DG_AN[i],R=D.runs[A.id],on=", "    for(i=0;i<BIM_DG_AN.length;i++){\n      var A=BIM_DG_AN[i],R=D.runs[A.id],on=")],
    # RE-ANCHORED IN V165: an analysis is shown when one of its elements is
    'legend_hidden_layer': [("on=!!R&&bimDgDiags(A.id).some(function(o){return bimLayerShown(o);});", "on=!!R;")],
    # RE-ANCHORED IN V165: the layout says there is no key on a phone
    'legend_on_phone': [("    if(sr.w<620)return null;   /* a phone's view", "    if(false)return null;   /* a phone's view")],
    'legend_full_names': [("          var r=b.rows[j],nm=r.short||r.name,iw=", "          var r=b.rows[j],nm=r.name,iw=")],
    'props_generic': [("    if(bimIsDiag(o)){bimRenderInto(el.propsbody,bimDgPropsHtml(o));return;}   /* __acad3dV164: a site analysis element */\n", "")],
    'width_unchecked': [("    if(f==='w'&&(!isFinite(n)||n<0.5||n>12)){a3dToast('A line width is 0.5 to 12 pixels');refreshProps();return false;}\n", "")],
    'props_reset_dead': [("    if(b.getAttribute('data-dgact')==='reset')bimDgReset(o.id);", "    if(b.getAttribute('data-dgact')==='reset')return;")],
    # ---- the analyses ----
    'ring_unscaled': [("Rc=Math.max(30,Math.ceil(r*1.7/5)*5)", "Rc=Math.max(30,Math.ceil(r*1.0/5)*5)")],
    'north_ignored': [("    var a=(az+bimTrueNorthDeg())*Math.PI/180;\n    return [S.c[0]+d*Math.sin(a)", "    var a=az*Math.PI/180;\n    return [S.c[0]+d*Math.sin(a)")],
    'rings_past_context': [("var max=Math.min(500,S.ctxR||500),first=", "var max=500,first=")],
    'dome_flat': [("return [S.c[0]+R*Math.cos(e)*Math.sin(a),S.y+R*Math.sin(e),S.c[1]-R*Math.cos(e)*Math.cos(a)];", "return [S.c[0]+R*Math.cos(e)*Math.sin(a),S.y,S.c[1]-R*Math.cos(e)*Math.cos(a)];")],
    'hours_every_half': [("        if(m%60===0)marks.push({p:p,t:(m/60)+'h'});", "        if(m%30===0)marks.push({p:p,t:(m/60)+'h'});")],
    'shadow_dates_all_shown': [("      layers[key]={name:'Site analysis - Shadows '+nm,col:'#7c8db0',hidden:k>0};", "      layers[key]={name:'Site analysis - Shadows '+nm,col:'#7c8db0',hidden:false};")],
    'wind_ungrouped': [("      if(!G[R.prev]){G[R.prev]=[];order.push(R.prev);}", "      G[R.prev]=[];order.push(R.prev);")],
    'wind_wrong_way': [("tail=[S.c[0]+f[0]*Rc*2.05,S.c[1]+f[1]*Rc*2.05],tip=[S.c[0]+f[0]*Rc*1.1,S.c[1]+f[1]*Rc*1.1];",
                        "tail=[S.c[0]+f[0]*Rc*1.1,S.c[1]+f[1]*Rc*1.1],tip=[S.c[0]+f[0]*Rc*2.05,S.c[1]+f[1]*Rc*2.05];")],
    'no_seasons_between': [("        if(spr.indexOf(mm)>=0)L.push(RS.spring);if(aut.indexOf(mm)>=0)L.push(RS.autumn);\n", "")],
    'no_sector_speed': [("        L.forEach(function(R){R.n++;R.ws+=ws;if(b<0)R.calm++;else{R.c[sec][b]++;R.sws[sec]+=ws;R.sn[sec]++;}});",
                         "        L.forEach(function(R){R.n++;R.ws+=ws;if(b<0)R.calm++;else{R.c[sec][b]++;R.sws[sec]+=ws*1.5;R.sn[sec]++;}});")],
    'trees_hide_nothing': [("      else if(c.kind==='trees'&&c.height>0&&o.pts&&o.pts.length){\n        var cx=o.pts[0][0]+q[0]", "      else if(false){\n        var cx=o.pts[0][0]+q[0]")],
    'top_floor_at_eye': [("var Ie=bimDgIsovist(S,eye,Bs,Rv),It=bimDgIsovist(S,top,Bs,Rv)", "var Ie=bimDgIsovist(S,eye,Bs,Rv),It=bimDgIsovist(S,eye,Bs,Rv)")],
    'landmark_always_seen': [("if(t<free+0.5)add('lm:'", "if(t<=free+0.5)add('lm:'")],
    'views_crowded': [("for(var j=0;j<chosen.length;j++){var dd=Math.abs(chosen[j].az-o.az);if(Math.min(dd,360-dd)<15)return;}", "")],
    'noise_unscreened': [("    return z>0?Math.min(20,10*Math.log(3+20*z/BIM_DG_LAMBDA)/Math.LN10):0;", "    return 0;")],
    # RE-ANCHORED IN V168: CRTN's range is the registry's since V167
    'noise_unlimited': [("    return d>0?Math.min(bimDgCrtnMax(),d+half):0;", "    return d>0?d+half:0;")],
    'noise_always_rural': [("    var urban=nb>=40,y=S.y+0.02;", "    var urban=false,y=S.y+0.02;")],
    'noise_limit_ignored': [("      w.V=bimDgKmh(t.maxspeed)||rc.v;", "      w.V=rc.v;")],
    'noise_tunnel_kept': [("var rc=bimDgRoadClass(c.tags.highway);if(!rc||c.tunnel||c.tags.tunnel==='yes')continue;", "var rc=bimDgRoadClass(c.tags.highway);if(!rc)continue;")],
    'noise_summed_flat': [("      sum+=Math.pow(10,w.Ls/10);", "      sum+=w.Ls;")],
    'noise_speed_term': [("+33*Math.log(V+40+500/V)/Math.LN10", "+33*Math.log(V+40)/Math.LN10")],
    # ---- Analyze site ----
    'tz_not_taken': [("        if(!bimSunNum(A3D.site.sun.tz)){A3D.site.sun.tz=C.tz;tzSet=true;}", "")],
    'tz_overwritten': [("        if(!bimSunNum(A3D.site.sun.tz)){A3D.site.sun.tz=C.tz;tzSet=true;}", "        A3D.site.sun.tz=C.tz;tzSet=true;")],
    # RE-ANCHORED IN V168: the radius reaches CRTN's since V167h
    'radius_unraised': [("      if(cs.radius<bimSiteRunRadius()){A3D.site.context=A3D.site.context||{};", "      if(false){A3D.site.context=A3D.site.context||{};")],
    'access_alongside': [("      }).then(function(){\n        bimSiteStep('access','busy',", "      });(function(){\n        bimSiteStep('access','busy',"),
                          ("          return [bimSiteState(got.length,r.errors),got.join(', ')+(r.errors&&r.errors.length?'. Not available: '+r.errors.join('; '):'')];\n        });\n      });",
                           "          return [bimSiteState(got.length,r.errors),got.join(', ')+(r.errors&&r.errors.length?'. Not available: '+r.errors.join('; '):'')];\n        });\n      })();")],
    'no_snapshot_when_placed': [("    if(placed){pushUndo();hold();}", "    if(placed){hold();}")],
    'snapshot_before_find': [("    if(placed){pushUndo();hold();}", "    pushUndo();hold();")],
    'busy_unguarded': [("    if(A3D_SITERUN.busy){a3dToast('Analyze site is already running');return null;}\n", "")],
    'last_run_forgotten': [("      D.last={date:bimSaToday(),ok:!!ok,steps:", "      var lastRun={date:bimSaToday(),ok:!!ok,steps:"),
                            ("      return {ok:!!ok,steps:D.last.steps};", "      return {ok:!!ok,steps:lastRun.steps};")],
    'partly_reads_done': [("  function bimSiteState(got,errors){return !got?'fail':(errors&&errors.length?'part':'ok');}", "  function bimSiteState(got,errors){return !got?'fail':'ok';}")],
    'enter_dead': [("      if(ev.key!=='Enter'||!e||!e.getAttribute||!e.getAttribute('data-saaddr'))return;", "      return;")],
    'no_address_prompt': [("    if(!placed&&!q){a3dToast('Where is the site? Type its address, or give its latitude and longitude in Properties, Site, Location');bimSiteAddrFocus();return null;}\n", "")],
    'cards_in_model': [("    dgframe:'location',dgsun:'climate',dgshadow:'climate',dgwind:'climate',dgviews:'people',dgnoise:'risk'};", "    dgnone:''};")],
    'card_show_dead': [("      if(bimLayerEff(ly).on)bimLayerSet(ly.id,'visible',false);", "      if(bimLayerEff(ly).on)return true;")],
    'legend_button_dead': [("    if(c==='dglegend'){var D=bimDgState();D.legendOff=!D.legendOff;", "    if(c==='dglegend'){var D=bimDgState();")],
    'search_hides_site': [("    S=root.querySelectorAll('[data-anzsec=\"flags\"]');", "    S=root.querySelectorAll('[data-anzsec=\"flags\"],[data-anzsec=\"site\"]');")],
    'typed_class_kept': [("        f.cls=bimSaPair(BIM_SA_CLS,A[i].cls)?A[i].cls:'neutral';f.sev=A[i].sev||1;   /* __acad3dV164",
                          "        if(!f.touched){f.cls=bimSaPair(BIM_SA_CLS,A[i].cls)?A[i].cls:'neutral';f.sev=A[i].sev||1;}   /* __acad3dV164")],
    # moved here from falsify_phase158.py in V164: only a project from before V164 holds a note, and this suite opens one
    'noted_dropped': [("      if(x.note||x.photo||x.at||x.touched){x.auto='';return true;}", "")],
    'typed_findings_shown': [("  function bimSaShown(){return bimSa().findings.filter(function(f){return !!f.auto;});}", "  function bimSaShown(){return bimSa().findings.filter(function(f){return true;}).slice(1);}")],
    'safill_alias_lost': [("['SITEANALYZE','RUNSITEANALYSIS','SAFILL','SITEANALYSISFILL','SAFROMMODEL']", "['SITEANALYZE','RUNSITEANALYSIS','SITEANALYSISFILL','SAFROMMODEL']")],
    'command_missing': [("    analyzesite:function(){bimAnzView();bimSiteAnalyze('');},   /* __acad3dV164 */\n", "")],
    # RETIRED IN V165: 'version_old' -- anchored on V164's version; V165's script checks the version now.
    # 'version_old': [("  var BIM_APP_VERSION={v:'V164',date:'2026-10-11'};", "  var BIM_APP_VERSION={v:'V163',date:'2026-10-10'};")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV164' in txt
out.write_text(txt, encoding='utf-8')
