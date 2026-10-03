"""falsify_phase131.py -- break the V131 build one way at a time, keeping the marker.

Each variant takes back one thing V131 does, and the V131 suite must fail on every one of them.
Variant names are lower case: the runner reads no other (V126)."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # ---- 131a: measuring
    'slice_hole_ignored': [("      area+=(d%2)?-a:a;", "      area+=a;")],
    'floors_not_stacked': [("n=Math.max(1,Math.floor(h/ftf+1e-6));", "n=1;")],
    'floor_ftf_ignored': [("ftf=(u&&u.ftf>0)?u.ftf:3,", "ftf=3,")],
    'floor_sliced_at_base': [("a=bimMeshSliceArea(o,y0+band/2);", "a=bimMeshSliceArea(o,y0+1e-4);")],
    'gfa_ratio_ignored': [("      r.GFA=r.GBA*u.gfa;r.NSA=r.GFA*u.nsa;", "      r.GFA=r.GBA;r.NSA=r.GFA*u.nsa;")],
    'nsa_ratio_ignored': [("      r.GFA=r.GBA*u.gfa;r.NSA=r.GFA*u.nsa;", "      r.GFA=r.GBA*u.gfa;r.NSA=r.GFA;")],
    'room_counted_gross': [("      r.NSA=o.area>0?o.area:0;r.footprint=r.NSA;r.levels=1;r.netMeasured=true;",
                            "      r.GBA=o.area>0?o.area:0;r.footprint=r.GBA;r.levels=1;")],
    'wall_takes_usage': [("    if(o.t==='solid'&&o.mesh&&(!o.bim||!o.bim.type))return 'mass';", "    if(o.t==='solid'&&o.mesh)return 'mass';")],
    # ---- 131a: formulas
    'precedence_flat': [("var op=toks[p++].t;a={op:op,a:a,b:term()};", "var op=toks[p++].t;a={op:op,a:a,b:unary()};")],
    'power_left_bound': [("if(peek().t==='^'){p++;return {op:'^',a:a,b:unary()};}", "if(peek().t==='^'){p++;return {op:'^',a:a,b:primary()};}")],
    'minus_binds_tight': [("if(peek().t==='-'){p++;return {neg:unary()};}", "if(peek().t==='-'){p++;return {neg:primary()};}")],
    'names_case_sensitive': [("        var k=nd.v.toLowerCase();", "        var k=nd.v;")],
    'divide_by_zero_silent': [("if(nd.op==='/'){if(b===0)throw {bimExpr:'divides by zero'};return a/b;}", "if(nd.op==='/')return a/b;")],
    'params_unread': [("    for(i=0;i<(u.params||[]).length;i++)vars[String(u.params[i].key).toLowerCase()]=+u.params[i].value;\n", "")],
    'formulas_cannot_chain': [("      else{r.values[f.key]=ev.value;vars[String(f.key).toLowerCase()]=ev.value;}", "      else{r.values[f.key]=ev.value;}")],
    'area_names_allowed': [("    if(BIM_EXPR_NAMES[lk])return key+' is one of the areas';\n", "")],
    # ---- 131a: the summary, the schedule, copies
    'summary_ignores_selection': [("var objs=ids?ids.map(objById).filter(function(o){return !!o;}):A3D.objs,L=bimUsages()", "var objs=A3D.objs,L=bimUsages()")],
    'no_usage_schedule': [("    usage:{label:'Areas by Usage',build:bimUsageScheduleRows,", "    usage_off:{label:'Areas by Usage',build:bimUsageScheduleRows,")],
    'mirror_drops_usage': [("    if(o.usage)copy.usage=o.usage;   /* __acad3dV131 */\n    if(g.kind==='sketch'){copy.t='sketch';copy.pts=g.pts;copy.y=g.y;copy.closed=o.closed;A3D.counts.sketch",
                            "    if(g.kind==='sketch'){copy.t='sketch';copy.pts=g.pts;copy.y=g.y;copy.closed=o.closed;A3D.counts.sketch")],
    'library_not_in_types': [("    if(!Array.isArray(A3D.types.usage))A3D.types.usage=JSON.parse(JSON.stringify(BIM_USAGE_DEFAULTS));\n    return A3D.types.usage;",
                              "    if(!window.__u131)window.__u131=JSON.parse(JSON.stringify(BIM_USAGE_DEFAULTS));\n    return window.__u131;")],
    # ---- 131b: Properties and the commands
    'no_usage_page': [("    if(bimUsageTarget(o))h+=bimUsagePropsHtml(o);       /* __acad3dV131 */\n", "")],
    'no_project_areas': [("    h+=bimUsageAreasHtml(null,'Areas by Usage');   /* __acad3dV131 */\n", "")],
    'primary_only': [("    var ids=(A3D.selSet&&A3D.selSet.length)?A3D.selSet:(A3D.sel?[A3D.sel]:[]);\n    return ids.filter(function(id){return !!bimUsageTarget(objById(id));});",
                      "    var ids=A3D.sel?[A3D.sel]:[];\n    return ids.filter(function(id){return !!bimUsageTarget(objById(id));});")],
    'no_mixed': [("var same=tg.every(function(id){var x=objById(id);return (x.usage||'')===(o.usage||'');});", "var same=true;")],
    'assign_not_undoable': [("    pushUndo();\n    objs.forEach(function(o){if(u)o.usage=u.id;else delete o.usage;n++;});", "    objs.forEach(function(o){if(u)o.usage=u.id;else delete o.usage;n++;});")],
    'ratio_unbounded': [("if(fld==='gfa'||fld==='nsa'){if(x<0||x>100)return 'A ratio is from 0 to 100%';u[fld]=x/100;return;}", "if(fld==='gfa'||fld==='nsa'){u[fld]=x/100;return;}")],
    'duplicate_names': [("        if(bimUsages().some(function(o){return o.id!==u.id&&o.name.toLowerCase()===x.toLowerCase();}))return 'There is already a usage called '+x;\n", "")],
    'remove_keeps_assignment': [("    for(i=0;i<A3D.objs.length;i++)if(A3D.objs[i].usage===id){delete A3D.objs[i].usage;n++;}\n", "")],
    'remove_not_undoable': [("    pushUndo();\n    var nm=L[ix].name;", "    var nm=L[ix].name;")],
    'formula_error_hidden': [("          (fp?'<div class=\"a3d-uerr\" role=\"alert\">'+bimEsc(fp)+'</div>':''));", "          '');")],
    'usage_command_no_focus': [("    if(s){try{s.focus();s.scrollIntoView({block:'nearest'});}catch(eF){}}\n", "")],
    'add_usage_twin': [("    while(taken(nm))nm=base+' '+(++n);\n", "")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV131' in txt
out.write_text(txt, encoding='utf-8')
