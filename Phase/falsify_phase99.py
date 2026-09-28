"""falsify_phase99.py -- break the V99 build one way at a time, keeping the marker.

Each variant breaks one thing the region-associativity suite claims to measure.
"""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # 1. the room tool goes back to walls-only tracing: four lines make no room.
    'room_walls_only': [(
        "    try{reg=bimRegionTraceAt(pt,y0,BIM_REGION_WANT.all);}",
        "    try{reg=bimRegionTraceAt(pt,y0,BIM_REGION_WANT.walls);}")],
    # 2. the room records no region: frozen, as before V99.
    'room_no_region': [(
        "    if(boundary.region)o.region=bimCloneRegion(boundary.region);   /* __acad3dV99 */", "")],
    # 3. the graph does not link members.
    'graph_no_region_edges': [(
        "            if(o.region.members[rm]!==o.id)link(bimGraphObjKey(o.region.members[rm]),key,'region');",
        "            if(false)link(bimGraphObjKey(o.region.members[rm]),key,'region');")],
    # 4. the visitor ignores region dependents other than rooms.
    'visitor_skips_regions': [(
        "    if(bimGraphRoomSourceId(o)||bimIsRegionDep(o)){", "    if(bimGraphRoomSourceId(o)){")],
    # 5. membership changes are never noticed.
    'no_regeneration': [(
        "    bimRegenerateRegions();\n    if(saveT)clearTimeout(saveT);", "    if(saveT)clearTimeout(saveT);")],
    # 6. the seed is moved to the centre after every trace.
    'seed_recentred': [(
        "    if(!bimPointInPoly(bimRegionSeedWorld(o),b.ring)){", "    if(true){")],
    # 7. an open region is not said.
    'open_silent': [(
        "      a3dToast(o.name+' is no longer enclosed - it keeps its last shape until its boundary is closed again');", "")],
    # 8. an open region does not keep its last shape: it is left marked but the members change.
    'open_not_marked': [(
        "      o.region.open=true;\n", "")],
    # 9. members are not recorded after a re-trace, so a new line never becomes one.
    'members_not_updated': [(
        "    o.region.members=b.srcIds.slice();\n    o.region.sig=b.sig;", "    o.region.sig=b.sig;")],
    # 10. a region room moved on its own is detached instead of re-bounding.
    'room_move_detaches': [(
        "        if(origin.t==='room'||allIn)regionOrigins.push(origin);", "        if(allIn)regionOrigins.push(origin);")],
    # 11. a hatch moved on its own stays linked.
    'hatch_move_stays': [(
        "        else bimCutSource(origin,'moved on its own');\n      }\n    }\n    for(i=0;i<regionOrigins.length;i++)",
        "      }\n    }\n    for(i=0;i<regionOrigins.length;i++)")],
    # 12. the hatch pick records no region.
    'hatch_no_region': [(
        "    o.region={seed:[pt[0],pt[1]],y:y,want:'all',members:(res.srcIds||[]).slice(),", "    o.regionX={seed:[pt[0],pt[1]],y:y,want:'all',members:(res.srcIds||[]).slice(),")],
    # 13. the floor drops its region.
    'floor_no_region': [(
        "      o.region=bimCloneRegion(prof.region);o.sourceType=prof.sourceType;o.sourceId=null;\n", "\n")],
    # 14. legacy wallgroup rooms are not adopted.
    'no_legacy_adoption': [(
        "        if(o.t==='room'&&!bimIsRegionDep(o)&&o.sourceType==='wallgroup'&&o.pts&&o.pts.length>=3){",
        "        if(false){")],
    # 15. a deleted single source leaves a dangling link.
    'deleted_source_kept': [(
        "          if(bimCutSource(o,'its source was deleted'))cut++;", "")],
    # 16. a lone closed shape becomes a region instead of a single source.
    'single_source_lost': [(
        "    if(candidates.length&&(reg.error||(reg.srcIds.length===1&&reg.srcIds[0]===candidates[0].sourceId)))",
        "    if(candidates.length&&reg.error)")],
    # 17. body drag teleports again.
    'drag_teleports': [(
        "        drag.mv.pos[0]=g[0]-gb[0];drag.mv.pos[2]=g[2]-gb[1];paint();saveSoon();",
        "        drag.mv.pos[0]=g[0];drag.mv.pos[2]=g[2];paint();saveSoon();")],
    # 18. toasts replace each other again.
    'toast_overwrites': [(
        "      if(a3dToast._same&&tx.textContent){", "      if(false){")],
    # 19. the Follows text ignores regions.
    'follows_text_blind': [(
        "      return 'The region bounded by '+(names.length?names.join(', '):'nothing')+",
        "      return 'Nothing'+")],
    # 20. the plane signature ignores edge positions, so a moved non-member is missed.
    'sig_count_only': [(
        "    return edges.length+':'+h.toString(36);", "    return edges.length+':';")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d' % (name, txt.count(old))
    txt = txt.replace(old, new, 1)
assert '__acad3dV99' in txt
out.write_text(txt, encoding='utf-8')
print('wrote %s' % out)
