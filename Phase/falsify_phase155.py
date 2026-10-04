"""falsify_phase155.py -- break the V155 build one way at a time, keeping the marker.
Variant names are lower case: the runner reads no other (V126)."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    'no_culling': [("      c.cull=o0===8||o1===8||o2===8||o3===8||o4===8||o5===8;", "      c.cull=false;")],
    'cull_on_one_corner': [("      c.cull=o0===8||o1===8||o2===8||o3===8||o4===8||o5===8;", "      c.cull=o0>0||o1>0||o2>0||o3>0;")],
    'behind_not_culled': [("if(cz<-cw)o4++;if(cz>cw)o5++;", "")],
    'box_not_moved': [("      if(o.pos[0]+ob[0]<wb[0])wb[0]=o.pos[0]+ob[0];", "      if(ob[0]<wb[0])wb[0]=ob[0];"), ("      if(o.pos[0]+ob[3]>wb[3])wb[3]=o.pos[0]+ob[3];", "      if(ob[3]>wb[3])wb[3]=ob[3];")],
    'box_not_reset': [("      if(wb.f!==B.frame){wb[0]=wb[1]=wb[2]=Infinity;wb[3]=wb[4]=wb[5]=-Infinity;wb.f=B.frame;}", "      if(wb.f!==B.frame){wb.f=B.frame;}")],
    'one_cell': [("cell=Math.floor((o.pos[0]+(lb[0]+lb[3])/2)/BIM_GB_CELL)+','+Math.floor((o.pos[2]+(lb[2]+lb[5])/2)/BIM_GB_CELL)", "cell='0,0'")],
    'gl_ignores_cull': [("        var ck=B.chunks[k];if(!ck.count||ck.cull)continue;", "        var ck=B.chunks[k];if(!ck.count)continue;")],
    'gpu_ignores_cull': [("      if(c.cull)continue;\n      if(c.count){L0.push(bun(c,'f0'));", "      if(c.count){L0.push(bun(c,'f0'));")],
    'bundles_not_kept': [("      if(g.bun[which])return g.bun[which];", "")],
    'stale_bindgroup': [("      if(g.bgv!==P.bgv){g.bun={};g.bgv=P.bgv;}", "      if(!g.bun){g.bun={};}")],
    'bench_model_not_back': [("      A3D.objs=keep.objs;A3D.sel=keep.sel;", "      A3D.sel=keep.sel;")],
    'bench_cam_not_back': [("      var k;for(k in keep.cam)if(keep.cam.hasOwnProperty(k))A3D.cam[k]=keep.cam[k];", "")],
    'bench_gl_only': [("        if(R.gpu)p=p.then(", "        if(false)p=p.then(")],
    'bench_engine_left_off': [("      A3D_GPU.forceOff=false;\n      A3D.objs=keep.objs;", "      A3D.objs=keep.objs;"), ("A3D_GPU.forceOff=false;row.webgl=", "row.webgl=")],
    'no_bench_stat': [("    if(A3D_BENCH&&!A3D_BENCH.running)srows+=", "    if(0)srows+=")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV155' in txt
out.write_text(txt, encoding='utf-8')
