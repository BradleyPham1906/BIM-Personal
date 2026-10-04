"""falsify_phase154.py -- break the V154 build one way at a time, keeping the marker.
Variant names are lower case: the runner reads no other (V126)."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    'no_pull_object_path': [("        gl.uniform1f(G.loc.pull,BIM_EDGE_PULL);   /* __acad3dV154 */\n", "")],
    'no_pull_batched': [("      ' vec3 w=aPos+a.xyz;if(uEdge>0.5)w+=(uEye-w)*'+BIM_EDGE_PULL.toFixed(6)+';'+", "      ' vec3 w=aPos+a.xyz;'+")],
    'no_pull_webgpu': [("    ' var w=pos+a.xyz;if(EDGE>0.5){w=w+(u.eye.xyz-w)*'+BIM_EDGE_PULL.toFixed(6)+';}\\n'+", "    ' var w=pos+a.xyz;\\n'+")],
    'eye_not_sent': [("    u[36]=V.eye[0];u[37]=V.eye[1];u[38]=V.eye[2];   /* __acad3dV154 */\n", "")],
    'map_opacity_ignored': [("return vec4f(mix(vec3f(0.114,0.125,0.141),c,m.color.a),1.0);}", "return vec4f(c,1.0);}")],
    'drape_everywhere': [("' if(i.uv.x<0.0||i.uv.x>1.0||i.uv.y<0.0||i.uv.y>1.0){discard;}\\n'+", "")],
    'surface_unshaded': [("' if(m.tile.w<0.5){return vec4f(m.color.rgb*i.k,1.0);}\\n'+", "' if(m.tile.w<0.5){return vec4f(m.color.rgb,1.0);}\\n'+")],
    'drape_wrong_tile': [("prm:put(col,plan.opacity,[s.u0,s.v0,s.u1,s.v1],[tiles[j].x*sc-D.ox,tiles[j].y*sc-D.oy,1/sc,1])", "prm:put(col,plan.opacity,[s.u0,s.v0,s.u1,s.v1],[tiles[j].x*sc,tiles[j].y*sc,1/sc,1])")],
    'terrain_no_depth': [("    return {map:pipe(true,false),ter:pipe(false,true),", "    return {map:pipe(true,false),ter:pipe(false,false),")],
    'no_mipmaps': [("lv=pow2?Math.floor(Math.log(Math.max(w,h))/Math.LN2)+1:1", "lv=1")],
    'mipmaps_not_made': [("    if(lv>1){\n      var enc=dev.createCommandEncoder();", "    if(false){\n      var enc=dev.createCommandEncoder();")],
    'texture_every_frame': [("    if(e.gtx&&e.gtx.dev===dev)return e.gtx;", "    if(e.gtx&&e.gtx.dev===dev&&false)return e.gtx;")],
    'texture_not_freed': [("    if(e.gtx){try{e.gtx.tex.destroy();}catch(eG){}if(e.gtx.dev===A3D_GPU.device)A3D_GPU.tileLive--;e.gtx=null;}   /* __acad3dV154 */", "")],
    'no_map_on_gpu': [("        for(i=0;i<plan.tiles.length;i++){\n          s=bimMapSource(plan.tiles[i],plan.tpl);tex=s?bimGpuTileTex(P,s.e):null;", "        for(i=0;i<0;i++){\n          s=bimMapSource(plan.tiles[i],plan.tpl);tex=s?bimGpuTileTex(P,s.e):null;")],
    'not_recorded_gpu': [("      bimMapRecord('webgpu',plan,drawn,srcs);", "      bimMapRecord('gl',plan,drawn,srcs);")],
    'terrain_back_to_gl': [("    return '';   /* __acad3dV154: the map and the terrain are drawn with WebGPU too */", "    if(!bimCameraIsPlan())for(var i=0;i<A3D.objs.length;i++){var o=A3D.objs[i];if(o.t==='terrain'&&o.survey)return 'terrain';}\n    return '';")],
    'site_not_drawn': [("    bimGpuSiteEncode(P,pass,site);\n", "")],
    'stale_surface': [("          if(!rec||rec.key!==D.key){", "          if(!rec){")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV154' in txt
out.write_text(txt, encoding='utf-8')
