"""falsify_phase125.py -- break the V125 build one way at a time, keeping the marker.

Each variant takes back one thing V125 does, or breaks one rule of the solve, and the V125 suite must
fail on every one of them."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # ---- 125a: the analytical model
    'no_node_merge': [("        if(Math.abs(q[0]-p[0])<=BIM_AN_TOL&&", "        if(false&&Math.abs(q[0]-p[0])<=BIM_AN_TOL&&")],
    'no_member_split': [("        if(bimVLen(perp)<=BIM_AN_TOL)on.push({n:k,s:s});\n", "")],
    'j_polar': [("            J:a*b*b*b*(1/3-0.21*(b/a)*(1-Math.pow(b/a,4)/12))};", "            J:hy*hz*(hy*hy+hz*hz)/12};")],
    'column_axes_swapped': [("        yRef=[Math.cos(r),0,Math.sin(r)];hy=b.width;hz=b.depth;", "        yRef=[Math.cos(r),0,Math.sin(r)];hy=b.depth;hz=b.width;")],
    'beam_at_centroid': [("        var ty=(isFinite(b.topY)?b.topY:(b.baseY+b.depth))+q[1];", "        var ty=(isFinite(b.topY)?b.topY:(b.baseY+b.depth))+q[1]-b.depth/2;")],
    'gpa_as_mpa': [("    return u==='gpa'?v*1e6:(u==='mpa'?v*1e3:v);", "    return u==='gpa'?v*1e3:(u==='mpa'?v*1e3:v);")],
    'g_equals_e': [("G:E/(2*(1+nu))", "G:E")],
    'no_ground_support': [("    if(Math.abs(baseY-bimLowestElev())<=BIM_AN_TOL)return {kind:'fixed',set:false,why:'on the lowest level'};\n", "")],
    'pinned_ends_ignored': [("        if(m.kind==='beam'&&bimStructOf(objById(m.id)).ends==='pinned'){", "        if(false){")],
    'walls_unnamed': [("          var kk=o.bim.type;notAnalysed[kk]=(notAnalysed[kk]||0)+1;", "")],
    # ---- 125b: loads
    'no_self_weight': [("        el[i].q[1]-=w;total[1]-=w*e.L;", "")],
    'live_factor_wrong': [("{name:'1.2D+1.6L',f:{D:1.2,L:1.6}", "{name:'1.2D+1.6L',f:{D:1.2,L:1.5}")],
    'point_load_ignored': [("              el[m.els[k]].pts.push({a:Math.min(Math.max(ld.at-ep.s0,0),ep.L),P:[0,-v,0]});total[1]-=v;break;",
                            "              total[1]-=v;break;")],
    'lateral_always_x': [("ix=ld.dir==='x'?0:2;", "ix=0;")],
    'point_range_unchecked': [("      if(!isFinite(ld.at)||ld.at<0||ld.at>L+1e-9)return", "      if(!isFinite(ld.at))return")],
    # ---- 125c: the solve
    'fef_moment_sign': [("r[1]-=q[1]*L/2;r[5]-=q[1]*L*L/12;", "r[1]-=q[1]*L/2;r[5]+=q[1]*L*L/12;")],
    'no_condensation': [("    if(!rel||!rel.length)return {k:kl,fef:fef,inv:null};", "    return {k:kl,fef:fef,inv:null};")],
    'no_rotation_recovery': [("          dl[cd.rel[p3]]=th;\n", "")],
    'no_load_deflection': [("    v+=q[1]*x*x*(L-x)*(L-x)/(24*EIz);", "")],
    'no_shear_zero_points': [("      xs=xs.concat(zs).sort(function(a,b){return a-b;});", "")],
    'pinned_as_fixed': [("fix=nd.sup==='fixed'?6:(nd.sup==='pinned'?3:0);", "fix=nd.sup?6:0;")],
    # the whole guard: no case was found where round-off leaves a positive pivot under the threshold,
    # so the threshold's size is not falsified -- only that a vanished pivot is refused, not solved
    'singular_accepted': [("          if(!(s>1e-10*Math.max(diag0[i],1e-12*maxd))||!isFinite(s)){bad=i;break;}", "          if(false){bad=i;break;}")],
    'reaction_misses_nodal': [("      for(j=0;j<3;j++)Rv[j]-=an[j];\n", "")],
    'transform_transposed': [("    for(b=0;b<4;b++)for(i=0;i<3;i++)l.push(R[i][0]*g[b*3]+R[i][1]*g[b*3+1]+R[i][2]*g[b*3+2]);",
                              "    for(b=0;b<4;b++)for(i=0;i<3;i++)l.push(R[0][i]*g[b*3]+R[1][i]*g[b*3+1]+R[2][i]*g[b*3+2]);")],
    # ---- 125d: the display
    'never_stale': [("    return bimStructSig(bimAnalyticalModel())===r.sig?r:null;", "    return r;")],
    'no_diagram': [("            drawn.diagPts+=poly.length;", "")],
    'label_not_peak': [("            if(!best||Math.abs(val)>Math.abs(best.v))best={v:val,o:pts[pts.length-1].o};", "            if(!best)best={v:val,o:pts[pts.length-1].o};")],
    'analyzeoff_dead': [("    A3D_STRUCT.show=false;paint();refreshProps();\n    a3dToast('Analysis display off');", "    a3dToast('Analysis display off');")],
    'schedule_other_combo': [("shear:m.V,mz:m.Mz.v,my:m.My.v,", "shear:m.V,mz:m.Mz.v*1.4,my:m.My.v,")],
    # ---- 125e: Properties and the commands
    'support_not_stored': [("    if(k==='support')bimStructEdit(o,function(st){if(BIM_SUPPORTS.indexOf(v)>=0)st.support=v;else delete st.support;});",
                            "    if(k==='support')refreshProps();")],
    'edit_no_undo': [("  function bimStructEdit(o,fn){\n    pushUndo();", "  function bimStructEdit(o,fn){")],
    'draft_not_kept': [("    if(el.propsbody){el.propsbody.addEventListener('input',bimLoadDraftInput,true);el.propsbody.addEventListener('change',bimLoadDraftInput,true);}", "")],
    'support_command_no_focus': [("    if(f){if(f.scrollIntoView)f.scrollIntoView({block:'center'});f.focus();}", "")],
    'analysis_page_missing': [("    h+=bimAnalysisPropsHtml();   /* __acad3dV125: the model's Analysis page, beside its floor loads */\n", "")],
    'dock_button_missing': [(",'bim:truss','bim:brace','bim:analyze']},", ",'bim:truss','bim:brace']},")],
    'copy_loses_struct': [("      to[k]=(v&&typeof v==='object')?JSON.parse(JSON.stringify(v)):v;", "      if(k!=='struct')to[k]=(v&&typeof v==='object')?JSON.parse(JSON.stringify(v)):v;")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV125' in txt
out.write_text(txt, encoding='utf-8')
