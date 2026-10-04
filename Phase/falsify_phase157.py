"""falsify_phase157.py -- break the V157 build one way at a time, keeping the marker.
Variant names are lower case: the runner reads no other (V126)."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    'no_rail_query': [("    if(k.rail)q.push(", "    if(false)q.push(")],
    'no_tree_rows': [("'node[\"natural\"=\"tree\"]'+b+';','way[\"natural\"=\"tree_row\"]'+b+';'", "'node[\"natural\"=\"tree\"]'+b+';'")],
    'towers_ignored': [("return t.natural==='tree'?'trees':(t.power==='tower'?'power':'');", "return t.natural==='tree'?'trees':'';")],
    'abandoned_rail_kept': [("if(t.railway&&/^(rail|light_rail|narrow_gauge|subway|tram|monorail|platform)$/.test(t.railway))return 'rail';",
                             "if(t.railway)return 'rail';")],
    'farmland_kept': [("if(t.landuse&&new RegExp('^('+BIM_CTX_LANDUSE+')$').test(t.landuse))return 'landuse';", "if(t.landuse)return 'landuse';")],
    'width_tag_ignored': [("    var w=bimTagMetres(t.width);\n    if(w)return w;", "    var w=null;")],
    'lanes_ignored': [("if(isFinite(L)&&L>0&&L<20)return Math.max(2,L*3.3);", "")],
    'feet_not_converted': [("x*=0.3048;", "x*=1;")],
    'road_use_all_car': [("    if(h==='cycleway')return 'cycleway';", "")],
    'no_mitre_width': [("      L.push(v.length);v.push([b[0]+nx*s,y,b[1]+nz*s]);\n      R.push(v.length);v.push([b[0]-nx*s,y,b[1]-nz*s]);",
                        "      L.push(v.length);v.push([b[0]+nx*s/2,y,b[1]+nz*s/2]);\n      R.push(v.length);v.push([b[0]-nx*s/2,y,b[1]-nz*s/2]);")],
    'not_draped': [("      if(!st.onGround)return 0;\n      var g2=ground([x,z]);", "      return 0;\n      var g2=ground([x,z]);")],
    'bridge_flat': [("      o.mesh=bimDeckMesh(pts,w,yAt,c.deck);", "      o.mesh=bimStripMesh(pts,w,yAt,0.05);")],
    'bridge_layer_ignored': [("var ly=parseFloat(t.layer);if(!isFinite(ly)||ly<1)ly=1;", "var ly=1;")],
    'no_piers': [("        if(hgt>0.5){", "        if(false){")],
    'tunnel_surfaced': [("if(t.tunnel&&t.tunnel!=='no'){c.tunnel=true;o.name=('Tunnel: '+o.name).slice(0,60);nb3.tunnels++;return;}",
                         "if(t.tunnel&&t.tunnel!=='no'){c.tunnel=true;o.name=('Tunnel: '+o.name).slice(0,60);nb3.tunnels++;}")],
    'platform_flat': [("else if(k==='rail'&&t.railway==='platform'){h=1;lift=0;}", "else if(k==='rail'&&t.railway==='platform'){lift=0;}")],
    'aerodrome_paved': [("(k==='airports'&&/^(apron|helipad)$/.test(t.aeroway||''))", "(k==='airports')")],
    'runway_as_road': [("if(kind==='airports')return t.aeroway==='runway'?45:(t.aeroway==='taxiway'?18:10);", "")],
    'tree_no_mesh': [("            o.mesh=bimTreeMesh(tp[j][0],tp[j][1],gy,th2,cd2);o.col=BIM_CTX_COL.trees;", "            o.col=BIM_CTX_COL.trees;")],
    'tree_height_ignored': [("th2=bimTagMetres(f.tags.height)||BIM_CTX_TREE_H", "th2=BIM_CTX_TREE_H")],
    'row_end_dropped': [("n=Math.max(1,Math.round(tot/step));d=tot/n;", "n=Math.max(1,Math.floor(tot/step));d=step;")],
    'line_not_hung': [("f.kind==='power'?y0+BIM_CTX_LINE_H:y0", "y0")],
    'no_bridge_message': [("(nb3.bridges?'; '+nb3.bridges+' bridge'", "(false?'; '+nb3.bridges+' bridge'")],
    'no_deck_props': [("    if(c.bridge)r+=bimPropText('Bridge',", "    if(false)r+=bimPropText('Bridge',")],
    'new_kinds_not_replaced': [("if(BIM_CTX_KINDS[i]!=='terrain'&&k[BIM_CTX_KINDS[i]])repl[BIM_CTX_KINDS[i]]=1;",
                                "if(i<5&&k[BIM_CTX_KINDS[i]])repl[BIM_CTX_KINDS[i]]=1;")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV157' in txt
out.write_text(txt, encoding='utf-8')
