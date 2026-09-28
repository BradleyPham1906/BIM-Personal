"""falsify_phase105.py -- break the V105 build one way at a time, keeping the marker."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')
CEIL = "    return Math.ceil(o.area/f.m2-1e-9);"

VARIANTS = {
    'ft2_not_converted': [("return {name:r[0],ft2:r[1],m2:r[1]*BIM_FT2_M2,basis:r[2]};", "return {name:r[0],ft2:r[1],m2:r[1],basis:r[2]};")],
    'first_attempt_arithmetic': [(CEIL, "    return Math.round(o.area*f.m2/BIM_FT2_M2);")],
    'round_not_ceil': [(CEIL, "    return Math.round(o.area/f.m2);")],
    'no_epsilon': [(CEIL, "    return Math.ceil(o.area/f.m2);")],
    'owner_factor_ignored': [("    if(isFinite(own)&&own>0)return {m2:own,basis:'',src:'Set'};", "    if(false)return {m2:own,basis:'',src:'Set'};")],
    'unknown_is_zero': [("    if(!f||!(o.area>0))return null;", "    if(!f||!(o.area>0))return 0;")],
    'case_sensitive_occupancy': [(".replace(/^ | $/g,'').toLowerCase();}", ".replace(/^ | $/g,'');}")],
    'schedule_zero_not_blank': [("occupants:occ===null?'':occ,", "occupants:occ===null?0:occ,")],
    'panel_disagrees': [("    return (n===null?'-':String(n))+' at '", "    return (n===null?'-':String(Math.round(o.area/f.m2)))+' at '")],
    'tab_drops_focus': [("      A3D.roomFieldNext=nx?nx.getAttribute('data-roomf'):null;", "      A3D.roomFieldNext=null;")],
    'fill_on_by_default': [("    roomScheme:'',   /* __acad3dV105", "    roomScheme:'dept',   /* __acad3dV105")],
    'legend_colour_not_drawn': [("A3D.pendingRoomLegend.items.push({name:se.name,col:se.col});", "A3D.pendingRoomLegend.items.push({name:se.name,col:BIM_SCHEME_COLS[0]});")],
    'case_splits_values': [("      if(v&&!seen['k'+v.toLowerCase()]){seen['k'+v.toLowerCase()]=1;out.push(v);}", "      if(v&&!seen['k'+v]){seen['k'+v]=1;out.push(v);}")],
    'fill_not_restored': [("      if(st&&(st.roomScheme==='dept'||st.roomScheme==='occupancy'))A3D.roomScheme=st.roomScheme;   /* __acad3dV105 */\n", "")],
    'fill_not_undoable': [("    if(by!==(A3D.roomScheme||'')){pushUndo();A3D.roomScheme=by;}", "    if(by!==(A3D.roomScheme||'')){A3D.roomScheme=by;}")],
    'copy_drops_fields': [("      bimCopyRoomFields(o,copy);   /* __acad3dV105 */\n", "")],
    'svg_no_fill': [("        poly(o.pts,true,lay,o.id,bimRoomSchemeGraphics(o,rg,pres),true);", "        poly(o.pts,true,lay,o.id,rg,true);")],
    'sheet_no_fill': [("        poly(o.pts,true,o.id,o.y,bimRoomSchemeGraphics(o,rg,pres),true);", "        poly(o.pts,true,o.id,o.y,rg,true);")],
    'legend_inherits_alignment': [("ctx.textBaseline='middle';ctx.textAlign='left';   /* the tag pass leaves it centred */", "ctx.textBaseline='middle';")],
    'command_does_nothing': [("    roomcolor:function(){bimCycleRoomScheme();},", "    roomcolor:function(){},")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d' % (name, txt.count(old))
    txt = txt.replace(old, new, 1)
assert '__acad3dV105' in txt
out.write_text(txt, encoding='utf-8')
