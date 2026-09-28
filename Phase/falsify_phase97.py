"""falsify_phase97.py -- break the V97 build twelve ways, keeping the marker.

Each variant breaks one thing the suite claims to measure. Each must make the suite FAIL.
"""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # 1. the contract reads RAW vertices, as the old re-measure did: a circle fails.
    'contract_reads_raw_pts': [(
        "      ring=bimSketchOutline(src);\n      if(!ring||ring.length<3)return {error:'its source sketch has too few points'};",
        "      ring=src.pts;\n      if(!ring||ring.length<3)return {error:'its source sketch has too few points'};")],
    # 2. the contract forgets the source's own offset: a moved sketch cannot be picked.
    'contract_ignores_pos': [(
        "    function w(p){return [p[0]+q[0],p[1]+q[2]];}",
        "    function w(p){return [p[0],p[1]];}")],
    # 3. a dependent's own frame is ignored: moved together, it lands twice as far away.
    'dependent_frame_ignored': [(
        "    return pts.map(function(p){return [p[0]-q[0],p[1]-q[2]];});",
        "    return pts.map(function(p){return [p[0],p[1]];});")],
    # 4. the source edge goes back to rooms only.
    'edge_room_only': [(
        "        if(srcId&&srcId!==o.id)link(bimGraphObjKey(srcId),key,'source');",
        "        if(o.t==='room'&&srcId&&srcId!==o.id)link(bimGraphObjKey(srcId),key,'source');")],
    # 5. a floor records nothing about where it came from.
    'floor_no_source': [(
        "      o.sourceId=prof.sourceId;o.sourceType=prof.sourceType;\n    }\n    A3D.objs.push(o);",
        "    }\n    A3D.objs.push(o);")],
    # 6. a hatch on a selection records nothing either.
    'hatch_no_source': [(
        "    if(opts.sourceId){o.sourceId=opts.sourceId;o.sourceType=opts.sourceType||null;}   /* __acad3dV97 */",
        "")],
    # 7. the cut goes back to being silent.
    'cut_silent': [(
        "    a3dToast(o.name+' is no longer linked to '+srcName+(why?(' ('+why+')'):'')+\n      ' - it keeps its current shape');",
        "")],
    # 8. an inserted vertex on an arc straightens both halves.
    'insert_straightens_arc': [(
        "        b1=bimArcBulgeBetween(arc.center,A,pt,sg);\n        b2=bimArcBulgeBetween(arc.center,pt,B,sg);",
        "        b1=0;b2=0;")],
    # 9. constraint indices are not shifted past an insert.
    'insert_no_constraint_shift': [(
        "        for(k=0;k<refs.length;k++)if(refs[k]>seg)refs[k]++;",
        "        for(k=0;k<refs.length;k++)if(false)refs[k]++;")],
    # 10. the gizmo is tested before grips again, swallowing the midpoint grip.
    'gizmo_before_grip': [(
        "    if(!A3D.sk&&ev.button===0){\n      var grip=bimPickGrip(xy[0],xy[1]);\n",
        "    var gzX=(!A3D.sk&&ev.button===0&&!ev.ctrlKey&&!ev.metaKey&&!ev.shiftKey)?bimPickGizmo(xy[0],xy[1]):null;\n"
        "    if(gzX){var gdX=gzX.rot?bimGizmoBeginRotate(gzX,xy):bimGizmoBegin(gzX,xy);if(gdX){pushUndo();drag=gdX;paint();}ev.preventDefault();return;}\n"
        "    if(!A3D.sk&&ev.button===0){\n      var grip=bimPickGrip(xy[0],xy[1]);\n")],
    # 11. no midpoint grips are drawn, so there is nothing to press.
    'no_midpoint_grips': [(
        "    if(ep.kind==='sketch'&&!bimIsPoint(o)&&!(A3D.conPick&&o.id===A3D.sel)){",
        "    if(false){")],
    # 12. an out-of-range segment throws again instead of being refused.
    'insert_throws': [(
        "    if(!o||!o.pts||!(seg>=0&&seg<bimSketchSegCount(o))||Math.floor(seg)!==seg)return null;\n",
        "")],
    # 13. a press inserts the vertex again, so a plain click changes the drawing.
    'click_inserts': [(
        "        drag={grip:true,objId:grip.objId,idx:-1,kind:'sketch',elev:grip.elev,moved:false,\n"
        "              pendingMid:{seg:grip.seg}};",
        "        var cmo=objById(grip.objId);var cins=bimInsertSketchVertex(cmo,grip.seg,bimSketchSegMid(cmo,grip.seg));\n"
        "        drag={grip:true,objId:grip.objId,idx:cins.idx,kind:'sketch',elev:grip.elev,moved:false};")],
    # 14. a stale grip from the last paint is live again.
    'stale_grips_live': [(
        "      if(g.objId!==A3D.sel)continue;\n",
        "")],
    # 15. the undo snapshot is taken after the insert, so undo keeps the new vertex.
    'undo_after_insert': [(
        "        if(pmo)pushUndo();\n        var pins=",
        "        var pins=")],
    # 16. a stale gizmo is live again, so a drag on a deselected sketch rotates it.
    'stale_gizmo_live': [(
        "    if(now.length!==was.length)return null;\n    var gi;\n"
        "    for(gi=0;gi<now.length;gi++)if(was.indexOf(now[gi])<0)return null;",
        "    var gi;")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d' % (name, txt.count(old))
    txt = txt.replace(old, new, 1)
assert '__acad3dV97' in txt
out.write_text(txt, encoding='utf-8')
print('wrote %s' % out)
