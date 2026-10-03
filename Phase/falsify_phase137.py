"""falsify_phase137.py -- break the V137 build one way at a time, keeping the marker.

Each variant takes back one thing V137 does, and the V137 suite must fail on every one of them.
Variant names are lower case: the runner reads no other (V126)."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # ---- 137a: the surface in 3D
    'not_called': [("    bimTerrainDrawGl(G,V,W,H);   /* __acad3dV137: the terrain in 3D, the map draped on it */\n", "")],
    'drawn_in_plan': [("    if(A3D_PLOT.on||bimCameraIsPlan())return;\n    var list=[],i,o;", "    if(A3D_PLOT.on)return;\n    var list=[],i,o;")],
    'hidden_layer_drawn': [("if(o.t==='terrain'&&o.survey&&bimLayerShown(o))list.push(o);", "if(o.t==='terrain'&&o.survey)list.push(o);")],
    'flat_heights': [("      pos.push(tin.P[v][0],tin.H[v],tin.P[v][1]);", "      pos.push(tin.P[v][0],0,tin.P[v][1]);")],
    'unshaded_surface': [("'void main(){if(uMode<0.5){gl_FragColor=vec4(uColor*vK,1.0);return;}'", "'void main(){if(uMode<0.5){gl_FragColor=vec4(0.0,0.0,0.0,1.0);return;}'")],
    'base_pass_skipped': [("      gl.uniform1f(T.mode,0);gl.uniform2f(T.tile,0,0);gl.uniform1f(T.inv,1);\n      gl.drawArrays(gl.TRIANGLES,0,rec.count);\n", "      gl.uniform1f(T.mode,0);gl.uniform2f(T.tile,0,0);gl.uniform1f(T.inv,1);\n")],
    # ---- 137a: the drape
    'no_drape': [("      if(plan.tiles.length&&rec.ext){", "      if(false){")],
    'no_discard': [("'if(vUV.x<0.0||vUV.x>1.0||vUV.y<0.0||vUV.y>1.0)discard;'+", "")],
    'tile_origin_wrong': [("gl.uniform2f(T.tile,tiles[j].x*sc-rec.ox,tiles[j].y*sc-rec.oy);", "gl.uniform2f(T.tile,tiles[j].x*sc,tiles[j].y*sc);")],
    'opacity_ignored': [("'gl_FragColor=vec4(mix(uColor*vK,c*(0.62+0.38*vK),uAlpha),1.0);}'", "'gl_FragColor=vec4(c*(0.62+0.38*vK),1.0);}'")],
    'tiles_not_capped': [("      if((x1-x0+1)*(y1-y0+1)<=BIM_DRAPE_MAXT||z<=1)break;\n      z--;", "      break;")],
    'drape_one_corner': [("      x0=Math.floor(bimLonToTileX(ext[0],z));x1=Math.floor(bimLonToTileX(ext[2],z));", "      x0=Math.floor(bimLonToTileX(ext[0],z));x1=x0;")],
    # ---- 137a: 2D
    'no_2d_polys': [("      if(!m){if(ob.t==='terrain'&&ob.survey&&!bimCameraIsPlan()&&bimLayerShown(ob))bimTerrainPolys(ob,polys,V,W,H);continue;}", "      if(!m)continue;")],
    'polys_in_plan': [("      if(!m){if(ob.t==='terrain'&&ob.survey&&!bimCameraIsPlan()&&bimLayerShown(ob))", "      if(!m){if(ob.t==='terrain'&&ob.survey&&bimLayerShown(ob))")],
    # ---- 137a: buildings on the terrain
    'stand_at_middle': [("        for(j=0;j<fp.length;j++){var hh=bimTinHeightAt(tin,fp[j][0],fp[j][1]);if(hh!==null&&(h===null||hh<h))h=hh;}", "")],
    'stand_highest': [("if(hh!==null&&(h===null||hh<h))h=hh;}", "if(hh!==null&&(h===null||hh>h))h=hh;}")],
    'not_on_fetch': [("      if(st.onGround)bimCtxStand(true);   /* __acad3dV137: the buildings on the terrain */\n", "")],
    'default_off': [("      onGround:c.onGround!==false};", "      onGround:c.onGround===true};")],
    'setting_not_applied': [("      var nst=bimCtxStand(nv);paint();", "      var nst=0;paint();")],
    'tin_outside_kept': [("      if(l1>=-1e-9&&l2>=-1e-9&&l1+l2<=1+1e-9)return", "      if(true)return")],   # V127's, which V137 reads
    # ---- 137b
    'no_checkbox': [("    r+=bimPropRow('Buildings','<label class=\"a3d-ctxk\"><input type=\"checkbox\" data-propctx=\"onGround\"'+(st.onGround?' checked':'')+\n      '> On the terrain</label>');   /* __acad3dV137 */\n", "")],
    'checkbox_value': [("    bimCtxSet(k,(k.indexOf('kind:')===0||k==='onGround')?f.checked:f.value);", "    bimCtxSet(k,k.indexOf('kind:')===0?f.checked:f.value);")],
    'no_stands_at': [("      if(c.standY)r+=bimPropText('Stands at',", "      if(false)r+=bimPropText('Stands at',")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV137' in txt
out.write_text(txt, encoding='utf-8')
