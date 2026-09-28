"""falsify_phase102.py -- break the V102 build one way at a time, keeping the marker."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    'footing_top_at_zero': [("        top=(h.bim.baseY||0)+hq[1]-q[1];rot=h.bim.rotation||0;", "        top=0.5;rot=h.bim.rotation||0;")],
    'footing_ignores_host_pos': [("        c=[h.bim.center[0]+hq[0]-q[0],h.bim.center[1]+hq[2]-q[2]];", "        c=[h.bim.center[0],h.bim.center[1]];")],
    'footing_not_turned': [(
        "      res=bimBuildColumnGeometry(c,top-b.thickness,b.width,b.length,b.thickness,rot);",
        "      rot=0;res=bimBuildColumnGeometry(c,top-b.thickness,b.width,b.length,b.thickness,rot);")],
    'strip_under_centreline': [("      off=(wo.dLeft-wo.dRight)/2;", "      off=0;")],
    'no_graph_edge': [("        if(bimIsFooting(o)&&o.bim.hostId)link(bimGraphObjKey(o.bim.hostId),key,'support');   /* __acad3dV102 */\n", "")],
    'visitor_skips_footing': [("      if(o.bim.hostId)bimRebuildFooting(o,ctx);\n      return;", "      return;")],
    'not_deleted_with_host': [("      if(bimIsFooting(oo)&&oo.bim.hostId&&idSet[oo.bim.hostId])idSet[oo.id]=true;   /* __acad3dV102 */\n", "")],
    'moved_alone_stays_linked': [("        origin.bim.hostId=null;\n        a3dToast(origin.name+' is no longer under '", "        a3dToast(origin.name+' is no longer under '")],
    'no_host_sweep': [("    bimSweepFootingHosts(); /* __acad3dV102 */\n", "")],
    'duplicate_footing_allowed': [("    if(ex){if(!quiet)a3dToast(host.name+' already has '+ex.name);return null;}\n", "")],
    'type_change_no_rebuild': [("      return bimRebuildFooting(o);\n    }\n    return false;", "      return true;\n    }\n    return false;")],
    'beam_type_no_rebuild': [("      o.mesh=r5.mesh;o.bim.width=t.params.width;o.bim.depth=t.params.depth;o.bim.baseY=r5.bim.baseY;",
                              "      o.bim.width=t.params.width;o.bim.depth=t.params.depth;")],
    'volume_wrong': [("    if(o.bim.type==='footing')return (o.bim.width||0)*(o.bim.length||0)*(o.bim.thickness||0);",
                      "    if(o.bim.type==='footing')return (o.bim.width||0)*(o.bim.length||0);")],
    'schedule_unregistered': [("    footing:{label:'Isolated Footings',build:function(){return bimBuildFootingSchedule('footing');},", "    footingX:{label:'Isolated Footings',build:function(){return bimBuildFootingSchedule('footing');},")],
    'ribbon_still_greyed': [("    'bim:truss':1,'bim:brace':1,'bim:rebar':1,   /* __acad3dV102: foundwall and foundslab implemented */",
                             "    'bim:truss':1,'bim:brace':1,'bim:foundwall':1,'bim:foundslab':1,'bim:rebar':1,")],
    'tool_ends_after_one': [("      if(!fc)a3dToast('Isolated Footing: click a column');else bimAddFootingUnder(fc);",
                             "      if(!fc)a3dToast('Isolated Footing: click a column');else bimAddFootingUnder(fc);A3D.sk=null;")],
    'dxf_skips_footing': [("        for(fpi=0;fpi<b.plan.length;fpi++)poly(b.plan[fpi],true,lay);", "")],
    'export_column_unturned': [("    var th=rot||0,cs=Math.cos(th),sn=Math.sin(th),qi;\n    for(qi=0;qi<quad.length;qi++){\n      var qx=quad[qi][0],qz=quad[qi][1];\n      quad[qi]=[center[0]+qx*cs-qz*sn,center[1]+qx*sn+qz*cs];\n    }\n    return quad;",
                                "    var qi;\n    for(qi=0;qi<quad.length;qi++)quad[qi]=[center[0]+quad[qi][0],center[1]+quad[qi][1]];\n    return quad;")],
    'foundslab_not_flagged': [("    o.bim.structural='foundation';\n", "")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d' % (name, txt.count(old))
    txt = txt.replace(old, new, 1)
assert '__acad3dV102' in txt
out.write_text(txt, encoding='utf-8')
print('wrote %s' % out)
