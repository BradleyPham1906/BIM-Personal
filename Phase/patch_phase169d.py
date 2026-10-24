#!/usr/bin/env python3
"""V169d: assets -- AASHTO's design vehicles (the car, the SU-30 delivery truck, the city bus) and their turning
paths, from the Green Book's 7th Edition (the owner's copy, read 2026-10-19); every placed asset built again after a
standards change.

Run from the repository root: python3 Phase/patch_phase169d.py
"""
import hashlib, pathlib, sys

SRC = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path('canvas_v10.html')
BASE = '01744e24661d4bc154e9068dc378506bca7cf2f041a3784a2d33f6d95e234aee'   # V169c

raw = SRC.read_bytes()
sha = hashlib.sha256(raw).hexdigest()
if sha != BASE:
    sys.exit('BASE mismatch: %s (expected %s)' % (sha, BASE))
s = raw.decode('utf-8')
before = len(raw)


def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count:
        sys.exit('expected %d of %r, found %d' % (count, old[:90], n))
    s = s.replace(old, new)


# ---- the registry: the design vehicles; the wheels' sizes the app's own ----
VEH = r'''    {id:'aashto.vehicles',title:'Design vehicles',pub:'AASHTO',kind:'standard',area:'Assets',use:'The car, the delivery truck and the city bus, and their turning paths',anywhere:true,
      eds:[{id:'aashto.vehicles.7',name:'A Policy on Geometric Design of Highways and Streets, 7th Edition (2018), Tables 2-4b and 2-5b',pub:'2018',st:'current',where:'United States: 23 CFR 625.4 incorporates the 7th Edition for the National Highway System',adopt:[{at:'us'}],
        src:{t:'AASHTO, A Policy on Geometric Design of Highways and Streets (the Green Book), 7th Edition (2018), the owner\'s copy',w:'Table 2-4b: the design vehicles\' dimensions in metres (2-4a in feet); Table 2-5b: their minimum turning radii (2-5a in feet); 2.8.2: the turning path bounded by the outer trace of the front overhang and the path of the inner rear wheel',u:'https://store.transportation.org/',lv:'P',read:'2026-10-19'},
        v:[{n:'P_l',v:5.79,u:'m',say:'the passenger car\'s length',src:'19.0 ft'},{n:'P_w',v:2.13,u:'m',say:'its width',src:'7.0 ft'},{n:'P_h',v:1.3,u:'m',say:'its height',src:'4.3 ft'},
          {n:'P_of',v:0.91,u:'m',say:'its front overhang',src:'3.0 ft'},{n:'P_or',v:1.52,u:'m',say:'its rear overhang',src:'5.0 ft'},{n:'P_wb',v:3.35,u:'m',say:'its wheelbase',src:'11.0 ft'},
          {n:'P_r',v:7.26,u:'m',say:'its minimum design turning radius',src:'23.8 ft'},{n:'P_ctr',v:6.4,u:'m',say:'its centreline turning radius',src:'21.0 ft',gt:'P_wb',lt:'P_r'},{n:'P_rin',v:4.39,u:'m',say:'its minimum inside radius',src:'14.4 ft',lt:'P_ctr'},
          {n:'SU_l',v:9.14,u:'m',say:'the single-unit truck\'s (SU-30) length',src:'30.0 ft'},{n:'SU_w',v:2.44,u:'m',say:'its width',src:'8.0 ft'},{n:'SU_h',v:4.11,u:'m',say:'its height, the largest',src:'13.5 ft'},
          {n:'SU_hlo',v:3.35,u:'m',say:'its height, the smallest',src:'11.0 ft',lt:'SU_h'},{n:'SU_of',v:1.22,u:'m',say:'its front overhang',src:'4.0 ft'},{n:'SU_or',v:1.83,u:'m',say:'its rear overhang',src:'6.0 ft'},
          {n:'SU_wb',v:6.1,u:'m',say:'its wheelbase',src:'20.0 ft'},{n:'SU_r',v:12.73,u:'m',say:'its minimum design turning radius',src:'41.8 ft'},{n:'SU_ctr',v:11.58,u:'m',say:'its centreline turning radius',src:'38.0 ft',gt:'SU_wb',lt:'SU_r'},
          {n:'SU_rin',v:8.64,u:'m',say:'its minimum inside radius',src:'28.4 ft',lt:'SU_ctr'},
          {n:'BUS_l',v:12.19,u:'m',say:'the city transit bus\'s length',src:'40.0 ft'},{n:'BUS_w',v:2.59,u:'m',say:'its width',src:'8.5 ft'},{n:'BUS_h',v:3.2,u:'m',say:'its height',src:'10.5 ft'},
          {n:'BUS_of',v:2.13,u:'m',say:'its front overhang',src:'7.0 ft'},{n:'BUS_or',v:2.44,u:'m',say:'its rear overhang',src:'8.0 ft'},{n:'BUS_wb',v:7.62,u:'m',say:'its wheelbase',src:'25.0 ft'},
          {n:'BUS_r',v:12.8,u:'m',say:'its minimum design turning radius (Table 2-5b; Table 2-5a gives 41.6 ft, 12.68 m)',src:'12.80 m'},{n:'BUS_ctr',v:11.52,u:'m',say:'its centreline turning radius',src:'37.8 ft',gt:'BUS_wb',lt:'BUS_r'},
          {n:'BUS_rin',v:7.45,u:'m',say:'its minimum inside radius',src:'24.5 ft',lt:'BUS_ctr'}]}]},
'''
rep("    {id:'app.assets',title:'The assets\\' own shapes',", VEH + "    {id:'app.assets',title:'The assets\\' own shapes',")
rep("src:{t:'This app: the seat a seated person sits on, a cycle\\'s height, a Sheffield stand\\'s size, a bay\\'s painted line, and the crown of a mapped tree whose leaf type is not mapped (the context\\'s rule since V157)',",
    "src:{t:'This app: the seat a seated person sits on, a cycle\\'s height, a Sheffield stand\\'s size, a bay\\'s painted line, a vehicle\\'s wheels, and the crown of a mapped tree whose leaf type is not mapped (the context\\'s rule since V157)',")
rep("{n:'line',v:0.1,u:'m',say:'a bay\\'s painted line, across'},\n",
    "{n:'line',v:0.1,u:'m',say:'a bay\\'s painted line, across'},\n"
    "          {n:'wheel_p',v:0.65,u:'m',say:'a car\\'s wheel, across'},{n:'wheel_hv',v:1,u:'m',say:'a truck\\'s or a bus\\'s wheel, across'},\n")

# ---- the kinds ----
rep("    {k:'bay',name:'Parking bay',cat:'Parking',kind:'bay',p:{}},\n",
    "    {k:'bay',name:'Parking bay',cat:'Parking',kind:'bay',p:{}},\n"
    "    {k:'car',name:'Car',cat:'Vehicles',kind:'vehicle',p:{v:'P',turn:false,side:'L'}},\n"
    "    {k:'truck',name:'Delivery truck',cat:'Vehicles',kind:'vehicle',p:{v:'SU',turn:false,side:'L'}},\n"
    "    {k:'bus',name:'City bus',cat:'Vehicles',kind:'vehicle',p:{v:'BUS',turn:false,side:'L'}},\n")

# ---- the vehicle: its sizes, its turning, its mesh ----
VMESH = r'''  /* a design vehicle (169d): AASHTO's length, width, height, overhangs, wheelbase and turning radii; the body's shape
     and the wheels the app's. At its sharpest turn the centre lies on the rear axle's line, the front axle's middle on
     the centreline turning radius, so the rear axle's middle is sqrt(CTR^2 - WB^2) from it; the front overhang's outer
     corner, which bounds the path with the inner rear wheel (2.8.2), is worked out from that. */
  var BIM_ENT_VEH={P:['Passenger car','P'],SU:['Single-unit truck','SU-30'],BUS:['City transit bus','CITY-BUS']};
  function bimEntVeh(p){
    var c=p&&BIM_ENT_VEH.hasOwnProperty(p.v)?p.v:'P',g=function(n){return bimStd('aashto.vehicles',c+'_'+n);},
      V={c:c,name:BIM_ENT_VEH[c][0],sym:BIM_ENT_VEH[c][1],l:g('l'),w:g('w'),h:g('h'),of:g('of'),or:g('or'),wb:g('wb'),r:g('r'),ctr:g('ctr'),rin:g('rin'),
        d:bimStd('app.assets',c==='P'?'wheel_p':'wheel_hv')};
    if(c==='SU')V.hlo=g('hlo');
    V.rr=Math.sqrt(Math.max(0,V.ctr*V.ctr-V.wb*V.wb));
    V.rov=Math.sqrt(Math.pow(V.rr+V.w/2,2)+Math.pow(V.wb+V.of,2));
    return V;
  }
  function bimEntVehMesh(V){
    var L=V.l,W=V.w,H=V.h,r=V.d/2,zf=L/2-V.of,zr=-L/2+V.or,tw=Math.min(0.3,W*0.12),xw=W/2-tw/2,y0=r*0.5,P=[];
    P.push(bimEntDisc([-xw,r,zf],r,tw),bimEntDisc([xw,r,zf],r,tw),bimEntDisc([-xw,r,zr],r,tw),bimEntDisc([xw,r,zr],r,tw));
    if(V.c==='P'){
      var yb=H*0.6;
      P.push(bimEntBox([0,(y0+yb)/2,0],[W,yb-y0,L]),bimEntBox([0,(yb+H)/2,(zf+zr)/2-L*0.04],[W*0.86,H-yb,L*0.48]));
    }else if(V.c==='SU'){
      var cl=V.of+V.wb*0.3,gap=L*0.02,yc=H*0.72,yf=r*1.1;
      P.push(bimEntBox([0,(y0+yc)/2,L/2-cl/2],[W,yc-y0,cl]),bimEntBox([0,(yf+H)/2,-(cl+gap)/2],[W,H-yf,L-cl-gap]),bimEntBox([0,(y0+yf)/2,-cl/2],[W*0.5,yf-y0,L-cl]));
    }else P.push(bimEntBox([0,(y0+H)/2,0],[W,H-y0,L]));
    return bimEntMarked(P,-L/2,L/2);
  }
  /* the mesh, local, front +Z, base on the ground; and where a tree's crown starts */
'''
rep("  /* the mesh, local, front +Z, base on the ground; and where a tree's crown starts */\n", VMESH)
rep("      else if(a.k==='bay')m=bimEntBayMesh();\n",
    "      else if(a.k==='bay')m=bimEntBayMesh();\n      else if(a.k==='vehicle')m=bimEntVehMesh(bimEntVeh(p));\n")

# ---- every placed asset built again after a standards change ----
rep("  /* ---- the leaves: the site's growing season (169a), from its climate ---- */\n",
    "  /* every placed asset built again after a standards change (169d), from its own parameters and the registry's sizes */\n"
    "  function bimEntRefit(){\n"
    "    var n=0,i,o;\n"
    "    for(i=0;i<A3D.objs.length;i++){o=A3D.objs[i];if(o.asset&&o.asset.k&&o.mesh&&bimEntRebuild(o))n++;}\n"
    "    A3D.lastRefit=n;\n"
    "    return n;\n"
    "  }\n"
    "  /* ---- the leaves: the site's growing season (169a), from its climate ---- */\n")
rep("    try{refreshProps();}catch(e1){console.warn('[BIM] Properties could not be drawn after a standards change',e1);}\n",
    "    try{if(typeof bimEntRefit==='function')bimEntRefit();}catch(e3){console.warn('[BIM] The assets could not be built again after a standards change',e3);a3dToast('The assets could not be resized to the standards - see the console');}\n"
    "    try{refreshProps();}catch(e1){console.warn('[BIM] Properties could not be drawn after a standards change',e1);}\n")

# ---- the turning paths: a vehicle's ring, from its inner rear wheel out to its front overhang's corner ----
rep("      if(a.k==='wheelchair')out.push({id:o.id,c:[F.c[0]+q[0],F.c[1]+q[2]],y:q[1]+F.y,r:[bimStd('ada.space','turn')/2],what:'the turning space'});\n",
    "      if(a.k==='wheelchair')out.push({id:o.id,c:[F.c[0]+q[0],F.c[1]+q[2]],y:q[1]+F.y,r:[bimStd('ada.space','turn')/2],what:'the turning space'});\n"
    "      else if(a.k==='vehicle'){\n"
    "        var V=bimEntVeh(a.p),fx=Math.sin(F.a),fz=Math.cos(F.a),sd=a.p.side==='R'?-1:1,zr=-V.l/2+V.or,ax=F.c[0]+fx*zr,az=F.c[1]+fz*zr;\n"
    "        out.push({id:o.id,c:[ax+q[0]+sd*fz*V.rr,az+q[2]-sd*fx*V.rr],y:q[1]+F.y,r:[V.rin,V.r,V.rov],what:'its turning path',side:sd>0?'L':'R'});\n"
    "      }\n")
rep('''    for(i=0;i<T.length;i++)for(j=0;j<T[i].r.length;j++){
      ctx.beginPath();on=false;
      for(k=0;k<=48;k++){
        var an=k/48*Math.PI*2;
        s2=toScreen([T[i].c[0]+T[i].r[j]*Math.cos(an),T[i].y+0.02,T[i].c[1]+T[i].r[j]*Math.sin(an)],V,W,H);
        if(!s2)continue;
        if(on)ctx.lineTo(s2[0],s2[1]);else{ctx.moveTo(s2[0],s2[1]);on=true;}
      }
      ctx.closePath();ctx.fill();ctx.stroke();
    }
''', '''    function ring(t,rad){
      on=false;
      for(k=0;k<=48;k++){
        var an=k/48*Math.PI*2;
        s2=toScreen([t.c[0]+rad*Math.cos(an),t.y+0.02,t.c[1]+rad*Math.sin(an)],V,W,H);
        if(!s2)continue;
        if(on)ctx.lineTo(s2[0],s2[1]);else{ctx.moveTo(s2[0],s2[1]);on=true;}
      }
      ctx.closePath();
    }
    /* one radius fills its disc; several fill the ring between the smallest and the largest, the path swept */
    for(i=0;i<T.length;i++){
      var R=T[i].r,lo=Math.min.apply(null,R),hi=Math.max.apply(null,R);
      ctx.beginPath();ring(T[i],hi);if(R.length>1)ring(T[i],lo);ctx.fill(R.length>1?'evenodd':'nonzero');
      for(j=0;j<R.length;j++){ctx.beginPath();ring(T[i],R[j]);ctx.stroke();}
    }
''')

# ---- Properties ----
rep('''      L=['parking.bay','app.assets'];
    }else if(a.k==='tree'){''', '''      L=['parking.bay','app.assets'];
    }else if(a.k==='vehicle'){
      var V=bimEntVeh(p);
      r+=bimPropText('Design vehicle',V.name+' (AASHTO '+V.sym+')');
      r+=bimEntBy('Size',V.l,V.w)+(V.c==='SU'?bimPropText(bimLenLabel('Height'),bimDispLen(V.hlo)+' to '+bimDispLen(V.h)+', drawn at '+bimDispLen(V.h)):bimPropLenText('Height',V.h));
      r+=bimPropLenText('Wheelbase',V.wb)+bimPropText(bimLenLabel('Overhangs'),bimDispLen(V.of)+' in front, '+bimDispLen(V.or)+' behind');
      r+=bimPropText(bimLenLabel('Radius'),bimDispLen(V.r)+' at the least: the minimum design turning radius');
      r+=bimPropText(bimLenLabel('CTR'),bimDispLen(V.ctr)+': the centreline turning radius');
      r+=bimPropText(bimLenLabel('Inside'),bimDispLen(V.rin)+' at the least: the minimum inside radius');
      r+=bimPropText(bimLenLabel('Corner'),bimDispLen(V.rov)+': the front overhang\\'s outer corner from the turn\\'s centre, worked out from the sizes above');
      r+=bimPropRow('On the plan','<input type="checkbox" data-propf="asset:turn"'+(p.turn?' checked':'')+'> its turning path');
      r+=bimPropRow('Turning',bimEntSel('side',[['L','To the left'],['R','To the right']],p.side==='R'?'R':'L'));
      L=['aashto.vehicles','app.assets'];
    }else if(a.k==='tree'){''')
rep("    else if(key!=='turn'&&!/^(who|pose|leaf|cyc|size)$/.test(key))return false;\n",
    "    else if(key!=='turn'&&!/^(who|pose|leaf|cyc|size|side)$/.test(key))return false;\n")
rep("    else{p[key]=String(val);if(key!=='pose')delete p.h;if(key!=='pose'&&key!=='who')delete p.cd;}\n",
    "    else if(key==='side')p.side=val==='R'?'R':'L';\n"
    "    else{p[key]=String(val);if(key!=='pose')delete p.h;if(key!=='pose'&&key!=='who')delete p.cd;}\n")

# ---- the labels kept short enough to show whole in Properties' label column ----
rep("      r+=bimEntBy('Clear floor space',bimStd('ada.space','clear_w'),bimStd('ada.space','clear_l'))+bimEntBy('Space for 95% of users',bimStd('wheel.awmp','space_w'),bimStd('wheel.awmp','space_l'));\n"
    "      r+=bimPropLenText('Turning space, across',bimStd('ada.space','turn'));\n"
    "      r+=bimPropRow('Show it on the plan','<input type=\"checkbox\" data-propf=\"asset:turn\"'+(p.turn?' checked':'')+'>');\n",
    "      r+=bimPropText(bimLenLabel('Space'),bimDispLen(bimStd('ada.space','clear_w'))+' by '+bimDispLen(bimStd('ada.space','clear_l'))+': the clear floor space; '+\n"
    "        bimDispLen(bimStd('wheel.awmp','space_w'))+' by '+bimDispLen(bimStd('wheel.awmp','space_l'))+' holds 95% of manual chair users');\n"
    "      r+=bimPropText(bimLenLabel('Turning'),bimDispLen(bimStd('ada.space','turn'))+' across: the turning space');\n"
    "      r+=bimPropRow('On the plan','<input type=\"checkbox\" data-propf=\"asset:turn\"'+(p.turn?' checked':'')+'> its turning space');\n")
rep("      r+=bimPropText(bimLenLabel('Aisle to reach it'),",
    "      r+=bimPropText(bimLenLabel('Aisle'),")
rep("      r+=bimPropLenText('Height',bimStd('wheel.awmp','height'))+bimPropLenText('Seat height',bimStd('wheel.awmp','seat'))+bimPropLenText('Eye height',bimStd('wheel.awmp','eye'));\n",
    "      r+=bimPropLenText('Height',bimStd('wheel.awmp','height'))+bimPropLenText('Seat',bimStd('wheel.awmp','seat'))+bimPropLenText('Eye height',bimStd('wheel.awmp','eye'));\n")

# ---- the library, the marker, the hook ----
rep("    h+=grp('entourage','People, cycles, parking and trees',BIM_ENT.length+' item(s)',body,true);\n",
    "    h+=grp('entourage','People, cycles, vehicles, parking and trees',BIM_ENT.length+' item(s)',body,true);\n")
rep("    /* __acad3dV169: people, cycles, parking and trees, sized from the registry */\n",
    "    /* __acad3dV169: people, cycles, vehicles, parking and trees, sized from the registry */\n")
rep("  window.__acad3dV169='assets,people,wheelchair,cycles,stands,bay,trees,leaf,gsl,shadows,turning,contexttrees,registry';\n",
    "  window.__acad3dV169='assets,people,wheelchair,cycles,stands,bay,trees,leaf,gsl,shadows,turning,contexttrees,registry,vehicles,turningpaths,refit';\n")
rep("      body:o.asset.k==='person'?bimEntBody(o.asset.p||{}):null,tree:o.asset.k==='tree'?bimEntTreeSize(o.asset.p||{}):null};\n",
    "      body:o.asset.k==='person'?bimEntBody(o.asset.p||{}):null,tree:o.asset.k==='tree'?bimEntTreeSize(o.asset.p||{}):null,\n"
    "      veh:o.asset.k==='vehicle'?bimEntVeh(o.asset.p||{}):null};\n")
rep("  window.__a3dEntTurns=function(){return {turns:bimEntTurns(),drawn:A3D.lastTurns||0};};\n",
    "  window.__a3dEntTurns=function(){return {turns:bimEntTurns(),drawn:A3D.lastTurns||0};};\n"
    "  window.__a3dEntRefit=function(){return {n:bimEntRefit(),last:A3D.lastRefit};};\n")

out = s.encode('utf-8')
na0 = sum(1 for c in raw.decode('utf-8') if ord(c) > 127)
na1 = sum(1 for c in s if ord(c) > 127)
if na1 > na0:
    sys.exit('the patch added %d non-ASCII characters' % (na1 - na0))
SRC.write_bytes(out)
print('bytes', before, '->', len(out))
print('sha256', hashlib.sha256(out).hexdigest())
