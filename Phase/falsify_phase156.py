"""falsify_phase156.py -- break the V156 build one way at a time, keeping the marker.
Variant names are lower case: the runner reads no other (V126)."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    'always_search': [("    if(seenN!==B.n)B.st.scanned=1;\n    if(seenN!==B.n)for(id in B.of)", "    B.st.scanned=1;\n    for(id in B.of)")],
    'count_not_raised': [("B.of[id]=last;c=last;B.n++;", "B.of[id]=last;c=last;")],
    'count_not_lowered': [("delete B.of[id];delete mark[id];B.n--;", "delete B.of[id];delete mark[id];")],
    'never_gpu_pick': [("    if(A3D_PICK_GPU==='on')return true;\n    return (A3D.glFaces||0)>BIM_PICK_GPU_FACES;", "    return false;")],
    'gpu_pick_always': [("    return (A3D.glFaces||0)>BIM_PICK_GPU_FACES;", "    return true;")],
    'locked_picked': [("      if(gp.ok&&gp.o&&bimLayerPickable(gp.o))return gp.o;", "      if(gp.ok&&gp.o)return gp.o;")],
    'id_offset_ignored': [("      ' gl_Position=uProj*uView*vec4(aPos+a.xyz,1.0);}');", "      ' gl_Position=uProj*uView*vec4(aPos,1.0);}');")],
    'id_off_by_one': [("    var n=out[0]+out[1]*256+out[2]*65536,slot=n-1,id,o=null;", "    var n=out[0]+out[1]*256+out[2]*65536,slot=n,id,o=null;")],
    'y_not_flipped': [("px=Math.floor(x*gs),py=h-1-Math.floor(y*gs)", "px=Math.floor(x*gs),py=Math.floor(y*gs)")],
    'no_depth_in_id_pass': [("    gl.enable(gl.DEPTH_TEST);gl.depthFunc(gl.LEQUAL);gl.depthMask(true);gl.disable(gl.BLEND);\n    gl.useProgram(K.prog);", "    gl.disable(gl.DEPTH_TEST);gl.disable(gl.BLEND);\n    gl.useProgram(K.prog);")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV156' in txt
out.write_text(txt, encoding='utf-8')
