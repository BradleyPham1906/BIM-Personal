"""falsify_phase153.py -- break the V153 build one way at a time, keeping the marker.
Variant names are lower case: the runner reads no other (V126)."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    'never_started': [("    if(A3D_GPU.state==='off')bimGpuStart();\n", "")],
    'depth_not_remapped': [("p.z=(p.z+p.w)*0.5;o.p=p;return o;}", "o.p=p;return o;}")],
    'offset_ignored': [("    ' var w=pos+a.xyz;if(EDGE>0.5)", "    ' var w=pos;if(EDGE>0.5)")],   # RE-ANCHORED IN V154
    'no_highlight': [("if(b.w>0.5&&b.w<1.5){o.boost=0.25;}", "")],
    'edges_not_selected': [("if(b.w>1.5){ec=vec3f(1.0,0.706,0.329);}else if(b.w>0.5){ec=vec3f(0.306,0.631,1.0);}", "")],
    # RETIRED IN V153, as V152's: a hidden object let through blends to nothing in the
    # transparent pass, the same picture; wasted work only.
    #   'hidden_drawn': [("' if(a.w<0.0||(PASS<0.5&&tr)||(PASS>0.5&&!tr)){", "' if((PASS<0.5&&tr)||(PASS>0.5&&!tr)){")],
    'no_blend': [("targets:[pass?{format:fmt,blend:blend}:{format:fmt}]", "targets:[{format:fmt}]")],
    'transparent_writes_depth': [("depthWriteEnabled:!(pass&&!edge)", "depthWriteEnabled:true")],
    'no_msaa': [("          multisample:{count:4}});", "          multisample:{count:1}});")],
    'no_transparent_pass': [("      if(c.count){L0.push(bun(c,'f0'));if(F.hasTrans)L1.push(bun(c,'f1'));}", "      if(c.count){L0.push(bun(c,'f0'));}")],   # RE-ANCHORED IN V155
    'no_edges': [("      if(F.edges&&c.ecount){L2.push(bun(c,'e0'));if(F.hasTrans)L3.push(bun(c,'e1'));}\n", "")],   # RE-ANCHORED IN V155
    'record_every_frame': [("      if(g.bun[which])return g.bun[which];", "")],   # RE-ANCHORED IN V155
    # RETIRED IN V155: one bundle for the whole scene, kept too long, is no more; a chunk's bundles go
    # with its buffers, and V155's stale_bindgroup breaks the other way they could go stale.
    #   'stale_bundle': [("    if(re||!P.bundle||P.bkey!==key){", "    if(!P.bundle){")],
    'whole_table_sent': [("    }else if(R.lo>=0){\n      dev.queue.writeBuffer(P.tab,R.lo*32,B.data.buffer,B.data.byteOffset+R.lo*32,(R.hi-R.lo+1)*32);",
                          "    }else if(R.lo>=0){R.lo=0;R.hi=B.cap-1;\n      dev.queue.writeBuffer(P.tab,R.lo*32,B.data.buffer,B.data.byteOffset+R.lo*32,(R.hi-R.lo+1)*32);")],
    'rows_not_sent': [("      dev.queue.writeBuffer(P.tab,R.lo*32,B.data.buffer,B.data.byteOffset+R.lo*32,(R.hi-R.lo+1)*32);\n", "")],
    'one_engines_rows': [("    if(ch)for(k in B.dirty)if(B.dirty.hasOwnProperty(k)){R=B.dirty[k];", "    if(ch)for(k in B.dirty)if(k==='gl'){R=B.dirty[k];")],
    # RETIRED IN V154: WebGPU draws the terrain itself; nothing hands that frame to WebGL any more.
    #  'terrain_on_gpu': [("    if(!bimCameraIsPlan())for(i=0;i<A3D.objs.length;i++){o=A3D.objs[i];if(o.t==='terrain'&&o.survey&&bimLayerShown(o)&&!bimTerrainSuperseded(o))return 'terrain';}\n", "")],
    # RETIRED IN V154: WebGPU draws the map itself; nothing hands that frame to WebGL any more.
    #  'map_on_gpu': [("    if(bimMapSettings().style!=='off'&&bimMapPlan(V,W,H).tiles.length)return 'map';\n", "")],
    'choice_ignored': [("    if(A3D_GPU.state==='ready'&&bimGpuPref()!=='webgl'&&!A3D_GPU.forceOff){", "    if(A3D_GPU.state==='ready'&&!A3D_GPU.forceOff){")],
    'choice_not_kept': [("    try{localStorage.setItem(BIM_GPU_KEY,pref==='webgl'?'webgl':'auto');}catch(eS){}", "    A3D_GPU.prefMem=pref;")],
    'loss_ignored': [("          bimGpuDrop();bimGpuFail('the device was lost ('+((info&&info.message)||'')+')');", "          return;")],
    'no_stat_row': [("    srows+=bimPropRow('Graphics',", "    if(0)srows+=bimPropRow('Graphics',")],
    'no_command': [("    ['GRAPHICS',['RENDERER','WEBGPU','WEBGL'],'graphics',", "    ['GRAPHICSX',['RENDERERX'],'graphicsx',")],
    'broken_frame_kept': [("      if(!why){try{okG=bimGpuRender(V,W,H);}catch(eR){bimGpuDrop();bimGpuFail('a frame failed: '+(eR&&eR.message));}}", "      if(!why){okG=bimGpuRender(V,W,H);}")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV153' in txt
out.write_text(txt, encoding='utf-8')
