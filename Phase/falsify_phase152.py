"""falsify_phase152.py -- break the V152 build one way at a time, keeping the marker.
Variant names are lower case: the runner reads no other (V126)."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    'never_batched': [("  var A3D_GL_BATCH=true;", "  var A3D_GL_BATCH=false;")],
    'send_every_row': [("    for(i=0;i<8;i++)if(d[o+i]!==f[i]){d[o+i]=f[i];ch=true;}", "    for(i=0;i<8;i++){d[o+i]=f[i];ch=true;}")],
    'compare_unrounded': [("    for(i=0;i<8;i++)if(d[o+i]!==f[i]){d[o+i]=f[i];ch=true;}", "    for(i=0;i<8;i++)if(d[o+i]!==v[i]){d[o+i]=f[i];ch=true;}")],
    'whole_table_sent': [("    var r0=Math.floor(R.lo*2/BIM_GB_TEXW),r1=Math.floor((R.hi*2+1)/BIM_GB_TEXW),per=BIM_GB_TEXW*4;", "    var r0=0,r1=P.texH-1,per=BIM_GB_TEXW*4;")],   # RE-ANCHORED IN V153
    'rebuild_every_frame': [("      if(c.dirty)bimGbBuild(B,c);", "      bimGbBuild(B,c);")],   # RE-ANCHORED IN V153
    'mesh_change_missed': [("      }else if(c.refs[id]!==m){", "      }else if(false){")],
    'hidden_dropped': [("      var shown=bimLayerShown(o)&&bimObjectVisibleOnLevel(o),la=1,col=null;", "      var shown=bimLayerShown(o)&&bimObjectVisibleOnLevel(o),la=1,col=null;\n      if(!shown){c=B.of[id];if(c){c.ids.splice(c.ids.indexOf(id),1);c.verts-=bimGbVerts(c.refs[id]);delete c.refs[id];c.dirty=true;delete B.of[id];}continue;}")],
    # RETIRED IN V152: a hidden object let through reaches only the transparent pass with an
    # alpha below zero, which blends to nothing and writes no depth: the same picture, only work
    # wasted. Its cost is not something a suite can see in a software renderer.
    #   'hidden_drawn': [("' if(a.w<0.0||(uPass<0.5&&tr)", "' if((uPass<0.5&&tr)")],
    'no_transparent_pass': [("        la=bimLayerAlpha(o);A3D.lastGlAlpha[id]=la;totalFaces+=m.f.length;if(la<1)hasTrans=true;", "        la=bimLayerAlpha(o);A3D.lastGlAlpha[id]=la;totalFaces+=m.f.length;")],
    'transparent_in_opaque': [("' bool tr=a.w<0.999;'", "' bool tr=false;'")],
    'edges_not_selected': [("' if(uEdge>0.5){vCol=vec4(b.w>1.5?vec3(1.0,0.706,0.329):(b.w>0.5?vec3(0.306,0.631,1.0):vec3(0.09,0.10,0.11)),a.w);}'", "' if(uEdge>0.5){vCol=vec4(vec3(0.09,0.10,0.11),a.w);}'")],
    'no_highlight': [("if(b.w>0.5&&b.w<1.5)vBoost=0.25;", "")],
    'no_lens': [("        var hx=bimLensCol(o)||o.col||", "        var hx=o.col||")],
    'offset_ignored': [("' gl_Position=uProj*uView*vec4(aPos+a.xyz,1.0);}'", "' gl_Position=uProj*uView*vec4(aPos,1.0);}'")],
    'slot_kept': [("      delete B.of[id];B.free.push(B.slots[id]);bimGbPut", "      delete B.of[id];bimGbPut")],
    'deleted_still_drawn': [("    for(id in B.of)if(B.of.hasOwnProperty(id)&&!seen[id]){", "    for(id in B.of)if(false){")],
    'no_chunk_cap': [("        if(!last||last.verts+nv>BIM_GB_CHUNK){", "        if(!last){")],
    'no_edges': [("      edges(0);\n", "")],
    'not_given_back': [("    if(A3D_SCENE)bimSceneRelease();   /* __acad3dV153: object by object, the description given back */\n", "")],   # RE-ANCHORED IN V153
    'faces_miscounted': [("    bimSceneFrameDone(B,'batched');\n    A3D.glFaces=F.totalFaces;", "    bimSceneFrameDone(B,'batched');\n    A3D.glFaces=B.st.objects;")],   # RE-ANCHORED IN V153
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV152' in txt
out.write_text(txt, encoding='utf-8')
