"""falsify_phase101.py -- break the V101 build one way at a time, keeping the marker."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    'no_number_on_create': [("    o.number=bimNextRoomNumber(o.levelId);   /* __acad3dV101 */\n", "")],
    'numbering_ignores_level': [("    base=(li+1)*100;", "    base=0;")],
    'tag_stores_text': [(
        "    var lines=[{t:r.number||'-',font:'bold 13px system-ui,sans-serif',col:'#ffffff'},",
        "    if(!o.frozen)o.frozen={n:r.number,m:r.name};r={number:o.frozen.n,name:o.frozen.m,area:r.area};\n    var lines=[{t:r.number||'-',font:'bold 13px system-ui,sans-serif',col:'#ffffff'},")],
    'tag_text_frozen': [(
        "    return (r.number?r.number+' ':'')+r.name;\n  }",
        "    if(!o.frozenText)o.frozenText=(r.number?r.number+' ':'')+r.name;return o.frozenText;\n  }")],
    'tag_props_edit_tag_not_room': [(
        "      var so=objById(A3D.sel),room=so&&so.t==='room'?so:(so&&so.roomId?objById(so.roomId):null);",
        "      var so=objById(A3D.sel),room=so&&so.t==='room'?so:null;")],
    'dup_number_silent': [(
        "      if(dup.length)a3dToast('Number '+val+' is also used by '+dup.map(function(r){return r.name;}).join(', '));", "")],
    'label_not_hidden': [("      if(bimRoomTagged(o.id)){ctx.restore();continue;}   /* __acad3dV101: the tag says it */\n", "")],
    'tag_not_pickable': [(
        "    return bimPickAnnotOfType(x,y,'roomtag')||bimPickText(x,y)||bimPickDim(x,y);",
        "    return bimPickText(x,y)||bimPickDim(x,y);")],
    'tag_no_grip': [(
        "    if(o.t==='text'||o.t==='roomtag')return o.pt?[o.pt]:null;   /* __acad3dV101 */",
        "    if(o.t==='text')return o.pt?[o.pt]:null;")],
    'tag_not_in_graph': [(
        "        if(o.t==='roomtag'&&o.roomId)link(bimGraphObjKey(o.roomId),key,'tag');   /* __acad3dV101 */\n", "")],
    'tag_does_not_follow_move': [("        o.pos[0]+=ctx.delta[0];o.pos[2]+=ctx.delta[2];\n", "")],
    'tag_survives_room_delete': [("      if(oo.t==='roomtag'&&idSet[oo.roomId])idSet[oo.id]=true;   /* __acad3dV101 */\n", "")],
    'no_orphan_sweep': [("    bimSweepOrphanTags();   /* __acad3dV101 */\n", "")],
    'tag_all_retags': [(
        "      seen++;\n      if(!bimRoomTagged(o.id))todo.push(o);", "      seen++;\n      todo.push(o);")],
    'tag_command_ends': [("      bimTagRoomAt([gx,gz]);\n", "      bimTagRoomAt([gx,gz]);A3D.sk=null;\n")],
    'ribbon_still_greyed': [(
        "    'bim:tagcat':1,'bim:linkcad':1,   /* __acad3dV101: bim:tagroom implemented */",
        "    'bim:tagroom':1,'bim:tagcat':1,'bim:linkcad':1,")],
    'schedule_no_number': [(
        "      return {number:bimRoomField(o,'number'),name:o.name,", "      return {name:o.name,")],
    'dxf_double_label': [(
        "        if(!bimRoomTagged(o.id))text(bimRoomLabelPoint(o),bimRoomLabelText(o),0.25,lay);   /* __acad3dV101 */",
        "        text(bimRoomLabelPoint(o),bimRoomLabelText(o),0.25,lay);")],
    'label_at_vertex_average': [(
        "    var ip=bimInteriorPoint(o.pts);\n    if(ip)return ip;", "    var ip=null;")],
    'fields_not_persisted_via_tag': [(
        "    if(k==='name')f={k:'name',label:'Name'};   /* a tag renames its room */\n", "")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d' % (name, txt.count(old))
    txt = txt.replace(old, new, 1)
assert '__acad3dV101' in txt
out.write_text(txt, encoding='utf-8')
print('wrote %s' % out)
