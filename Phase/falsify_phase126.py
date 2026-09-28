"""falsify_phase126.py -- break the V126 build one way at a time, keeping the marker.

Each variant takes back one thing V126 does, or gets one formula wrong, and the V126 suite must fail
on every one of them."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # ---- 126a: properties, outline, sweep
    'circle_j_is_i': [("J=PI*Math.pow(p.D,4)/32;", "J=PI*Math.pow(p.D,4)/64;")],
    'pipe_j_is_i': [("Iz=Iy=PI*(Math.pow(p.D,4)-Math.pow(di,4))/64;J=2*Iz;", "Iz=Iy=PI*(Math.pow(p.D,4)-Math.pow(di,4))/64;J=Iz;")],
    'hss_j_polar': [("      J=4*Am*Am*p.t/per;", "      J=Iz+Iy;")],
    'ibeam_iz_solid': [("Iz=(p.bf*p.d*p.d*p.d-(p.bf-p.tw)*hw*hw*hw)/12;", "Iz=p.bf*p.d*p.d*p.d/12;")],
    'ibeam_iy_no_web': [("Iy=(2*p.tf*p.bf*p.bf*p.bf+hw*p.tw*p.tw*p.tw)/12;", "Iy=(2*p.tf*p.bf*p.bf*p.bf)/12;")],
    'open_j_half': [("J=(2*p.bf*p.tf*p.tf*p.tf+hw*p.tw*p.tw*p.tw)/3;", "J=(2*p.bf*p.tf*p.tf*p.tf+hw*p.tw*p.tw*p.tw)/2;")],
    'channel_centroid_at_back': [("zc=(2*p.bf*p.tf*p.bf/2+hw*p.tw*p.tw/2)/A;", "zc=0;")],
    'hss_walls_unchecked': [("    if(p.shape==='hss'&&!(2*p.t<Math.min(p.B,p.H)))return 'its walls meet: 2t must be less than B and H';\n", "")],
    'round_16': [("var BIM_ROUND_N=32;", "var BIM_ROUND_N=16;")],
    'no_caps': [("        f.push([tris[i][2],tris[i][1],tris[i][0]]);\n        f.push([tris[i][0]+n,tris[i][1]+n,tris[i][2]+n]);\n", "")],
    'no_ring_caps': [("      for(i=0;i<n;i++){j=(i+1)%n;f.push([j,i,b+i,b+j]);f.push([i+n,j+n,b+j+m,b+i+m]);}\n", "")],
    'not_turned_outward': [("    if(bimMeshSignedVolume(mesh)<0)mesh.f=mesh.f.map(function(fc){return fc.slice().reverse();});\n", "")],
    # ---- 126b: the catalogue
    'steel_as_concrete': [("BEAM_TYPE_DEFAULTS.push(bimSectionType('beam',r[0],r[1],r[2],'Steel'));", "BEAM_TYPE_DEFAULTS.push(bimSectionType('beam',r[0],r[1],r[2],'Concrete'));")],
    'column_extent_swapped': [("params:cat==='column'?{width:b.y,depth:b.z,", "params:cat==='column'?{width:b.z,depth:b.y,")],
    'w12_mistyped': [("bimW(12.2,6.49,0.380,0.230)", "bimW(12.2,6.49,0.440,0.230)")],
    'no_seeding': [("    if(!A3D.types.__v126){\n", "    if(false){\n")],
    'seeded_every_load': [("    if(!A3D.types.__v126){\n", "    if(true){\n")],
    'no_type_groups': [("    if(groups.length<2)return opts(list);", "    return opts(list);")],
    'edittype_unlocked': [("        (prof?' disabled title=\"Set by the section: choose another type to change it\"':'')+'></div>';", "        '></div>';")],
    # ---- 126c: the section in the model
    'beam_above_level': [("var ex=bimProfileExtent(sec),ux=dx/L,uz=dz/L,ya=topY-ex.ymax;", "var ex=bimProfileExtent(sec),ux=dx/L,uz=dz/L,ya=topY;")],
    'beam_web_flat': [("return [p1[0]+ux*s-uz*z,ya+y,p1[1]+uz*s+ux*z];", "return [p1[0]+ux*s-uz*y,ya+z,p1[1]+uz*s+ux*y];")],
    'column_not_turned': [("      var c=Math.cos(rot||0),sn=Math.sin(rot||0);\n      return {mesh:bimSweepMesh(", "      var c=1,sn=0;\n      return {mesh:bimSweepMesh(")],
    'beam_type_stays_box': [("var r5=bimBuildBeamGeometry(o.bim.p1,o.bim.p2,o.bim.topY,t.params.width,t.params.depth,tp5);", "var r5=bimBuildBeamGeometry(o.bim.p1,o.bim.p2,o.bim.topY,t.params.width,t.params.depth,null);")],
    'section_not_cleared': [("      if(tp5)o.bim.section=JSON.parse(JSON.stringify(tp5));else delete o.bim.section;", "      if(tp5)o.bim.section=JSON.parse(JSON.stringify(tp5));")],
    'width_edit_allowed': [("    if(o.bim.section&&(Math.abs(newW-o.bim.width)>1e-9||Math.abs(newDep-o.bim.depth)>1e-9)){", "    if(false){")],
    'height_straightens': [("var res=bimBuildColumnGeometry(o.bim.center,o.bim.baseY,newW,newDep,newH,o.bim.rotation||0,o.bim.section||null);", "var res=bimBuildColumnGeometry(o.bim.center,o.bim.baseY,newW,newDep,newH,o.bim.rotation||0,null);")],
    'rotation_straightens': [("          o.bim.height,cr*Math.PI/180,o.bim.section||null);", "          o.bim.height,cr*Math.PI/180,null);")],
    # ---- 126d: analysis, Properties, Assets
    'analysis_rect_only': [("      var sec=bimProfileProps(pf);\n", "      var sec=bimRectSection(hy,hz);\n")],
    'no_section_rows': [("    var st=bimStructOf(o),rows=bimSectionPropsRows(o),i;", "    var st=bimStructOf(o),rows='',i;")],
    'mass_as_concrete': [("rows+=bimPropText('Mass (kg/m)',mat&&mat.density?bimDispNum(pp.A*mat.density,1)", "rows+=bimPropText('Mass (kg/m)',mat&&mat.density?bimDispNum(pp.A*2400,1)")],
    'sections_open': [("closed:{materials:true,sections:true,walltypes:true,patterns:true}", "closed:{materials:true,walltypes:true,patterns:true}")],
    'drop_not_picked': [("kind==='walltype'||kind==='section')obj=pick(cx,cy)||null;", "kind==='walltype')obj=pick(cx,cy)||null;")],
    'section_any_kind': [("      tg=tg.filter(function(x){return x&&x.bim&&x.bim.type===scat;});", "      tg=tg.filter(function(x){return x&&x.bim&&(x.bim.type==='column'||x.bim.type==='beam');});")],
    'section_no_undo': [("      pushUndo();\n      var sok=[],sno=[];", "      var sok=[],sno=[];")],
    'section_search_blind': [("[secs[i].t.name,secs[i].cat,'section',sp.material||'',BIM_PROFILE_SHAPES[sp.profile.shape]||'']", "[secs[i].t.name,secs[i].cat,'section',sp.material||'']")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV126' in txt
out.write_text(txt, encoding='utf-8')
