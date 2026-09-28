"""falsify_phase95.py -- break the V95 build eleven ways, keeping the marker.

Each variant breaks one thing the suite claims to measure. Each must make the suite FAIL.
"""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # 1. no arrangement: edges go into the graph exactly as drawn, which is the V22 behaviour.
    'no_arrangement': [(
        "      hits=bimIntersectBulgedSegs(edges[i].a,edges[i].b,edges[i].bulge,\n"
        "                                  edges[j].a,edges[j].b,edges[j].bulge);",
        "      hits=[];")],
    # 2. the angular key goes back to the chord, so a turn at an arc node can be the wrong one.
    'angle_from_chord': [(
        "  function bimEdgeDirAt(e,atStart){\n    if(!atStart)return bimSegEndDir(e.a,e.b,e.bulge);",
        "  function bimEdgeDirAt(e,atStart){\n"
        "    var cx=e.b[0]-e.a[0],cz=e.b[1]-e.a[1],cl=Math.sqrt(cx*cx+cz*cz)||1;\n"
        "    return atStart?[cx/cl,cz/cl]:[cx/cl,cz/cl];\n"
        "    /* unreachable below */\n"
        "    if(!atStart)return bimSegEndDir(e.a,e.b,e.bulge);")],
    # 3. an arc's pieces are rebuilt as straight lines, so a traced curve becomes a chord.
    'split_drops_curve': [(
        "        bulge:arc?bimArcBulgeBetween(arc.center,prev,kept[k].p,sign):0});",
        "        bulge:0});")],
    # 4. the traced loop drops its bulges, so a curved region loses its area.
    'trace_drops_bulge': [(
        "  function bimHalfBulge(g,h){var e=g.edges[h.e];return h.forward?e.bulge:-e.bulge;}",
        "  function bimHalfBulge(g,h){return 0;}")],
    # 5. the sign is ignored, so the infinite outer face is a candidate like any other.
    'outer_face_allowed': [(
        "      sa=bimBulgedSignedArea(f.pts,f.bulges,true);\n      if(sa<=1e-9)continue;",
        "      sa=Math.abs(bimBulgedSignedArea(f.pts,f.bulges,true));\n      if(sa<=1e-9)continue;")],
    # 6. islands stop being reported, so a region with a hole overstates its area in silence.
    'islands_hidden': [(
        "  function bimFaceHasIsland(g,hit){",
        "  function bimFaceHasIsland(g,hit){\n    if(true)return false;")],
    # 7. the collector stops applying pos, which is the V75 bug this phase collected.
    'collector_ignores_pos': [(
        "        bimPushRingEdges(out,o.bim.centerline,o.bim.bulges||null,!!o.bim.closed,q[0],q[2]);",
        "        bimPushRingEdges(out,o.bim.centerline,o.bim.bulges||null,!!o.bim.closed,0,0);")],
    # 8. the collector stops reading wall bulges, so a curved wall traces as its chord again.
    'collector_ignores_bulges': [(
        "        bimPushRingEdges(out,o.bim.centerline,o.bim.bulges||null,!!o.bim.closed,q[0],q[2]);",
        "        bimPushRingEdges(out,o.bim.centerline,null,!!o.bim.closed,q[0],q[2]);")],
    # 9. the arrangement size limit is removed, so a huge plan is ground through instead of refused.
    'no_size_limit': [(
        "    if(edges.length>limit)\n"
        "      return {error:'Too much geometry to trace here ('+edges.length+' edges, limit '+limit+')'};",
        "    if(false)return {error:'x'};")],
    # 10. the BIM toolset goes back to being ribbon-only.
    'bim_cmds_unreachable': [(
        "    room:function(){startRoomTool();},",
        "    roomXX:function(){startRoomTool();},")],
    # 11. bimBulgedArea stops taking the magnitude, so every schedule can go negative.
    'area_not_absolute': [(
        "  function bimBulgedArea(pts,bulges,closed){\n    return Math.abs(bimBulgedSignedArea(pts,bulges,closed));",
        "  function bimBulgedArea(pts,bulges,closed){\n    return bimBulgedSignedArea(pts,bulges,closed);")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d' % (name, txt.count(old))
    txt = txt.replace(old, new, 1)
assert '__acad3dV95' in txt
out.write_text(txt, encoding='utf-8')
print('wrote %s' % out)
