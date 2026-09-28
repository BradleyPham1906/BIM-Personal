"""falsify_phase106.py -- break the V106 build one way at a time, keeping the marker."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')
BIS = "cell=bimClipHalfPlane(cell,nx,nz,nx*(c.x+d.x)/2+nz*(c.z+d.z)/2);"

VARIANTS = {
    'half_plane_far_side': [("      if(da<=0)out.push(a);\n      if((da<0&&db>0)||(da>0&&db<0)){t=da/(da-db);", "      if(da>=0)out.push(a);\n      if((da<0&&db>0)||(da>0&&db<0)){t=da/(da-db);")],
    'bisector_through_column': [(BIS, "cell=bimClipHalfPlane(cell,nx,nz,nx*c.x+nz*c.z);")],
    'axis_aligned_split': [(BIS, "cell=bimClipHalfPlane(cell,nx,0,nx*(c.x+d.x)/2);")],
    'twin_counted_twice': [("        if(twin){c.notes.push('same place as '+twin.name+', which takes the area');continue;}\n", "")],
    'no_takedown': [("        c.aD=(c.aD==null||u.aD==null)?null:c.aD+u.aD;", "        c.aD=c.aD;")],
    'missing_load_as_zero': [("c.fD=c.sup.dl==null?null:c.area*c.sup.dl;", "c.fD=c.area*(c.sup.dl||0);")],
    'factored_wrong': [("factored:both?1.2*c.aD+1.6*c.aL:''", "factored:both?1.4*c.aD+1.6*c.aL:''")],
    'carries_own_level': [("      d=Math.abs((lv.elev||0)-c.top);", "      d=Math.abs((lv.elev||0)-c.base);")],
    'mark_numbers_first': [("if(na!==nb)return na?1:-1;", "if(na!==nb)return na?-1:1;")],
    'roof_ignored': [("pts=o.bim.type==='floor'?o.bim.profile:(o.bim.type==='roof'?o.bim.footprint:null);", "pts=o.bim.type==='floor'?o.bim.profile:null;")],
    'negative_load_accepted': [("      if(ls!==''&&(!isFinite(lq)||lq<0)){", "      if(ls!==''&&!isFinite(lq)){")],
    'load_not_undoable': [("      pushUndo();\n      if(ls==='')delete lvl[field];else lvl[field]=lq;", "      if(ls==='')delete lvl[field];else lvl[field]=lq;")],
    'properties_not_wired': [("        if(mk==='dl'||mk==='ll'){updateLevel(A3D.activeLevel,mk,mv);return;}   /* __acad3dV106 */\n", "")],
    'unsupported_hidden': [("columns:sup.length,unsupported:Math.max(0,slabArea-onCols)});", "columns:sup.length,unsupported:0});")],
    'stacks_ignore_position': [("||Math.abs(u.x-c.x)>BIM_TRIB_TOL||Math.abs(u.z-c.z)>BIM_TRIB_TOL)continue;", ")continue;")],
    'overlay_wrong_level': [("        if(r.supportsId!==lv.id)continue;", "        if(r.supportsId===lv.id)continue;")],
    'command_does_nothing': [("    tribarea:function(){bimToggleTrib();},", "    tribarea:function(){},")],
    'schedule_missing': [("    colload:{label:'Column Loads',", "    colloadX:{label:'Column Loads',")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d' % (name, txt.count(old))
    txt = txt.replace(old, new, 1)
assert '__acad3dV106' in txt
out.write_text(txt, encoding='utf-8')
