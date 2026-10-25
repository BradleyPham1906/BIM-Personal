  /* ================= __acad3dV169: assets for scale and the simulations =================
     People, a wheelchair user, a cycle and its stand, a parking bay and trees, each a solid whose mesh is built from
     its parameters and the registry's sizes (research-assets.md). Its first two vertices mark its back and its front
     at the ground and no face uses them, so its heading and centre come through every move, turn and mirror; a
     tree's trunk faces come before its crown's (asset.cf), so a bare deciduous tree casts its trunk's shadow only. */
  var BIM_ENT=[
    {k:'man',name:'Man',cat:'People',kind:'person',p:{who:'man',pose:'standing'}},
    {k:'woman',name:'Woman',cat:'People',kind:'person',p:{who:'woman',pose:'standing'}},
    {k:'child',name:'Child',cat:'People',kind:'person',p:{who:'child',pose:'standing'}},
    {k:'seated',name:'Seated person',cat:'People',kind:'person',p:{who:'woman',pose:'seated'}},
    {k:'wheelchair',name:'Wheelchair user',cat:'People',kind:'wheelchair',p:{turn:true}},
    {k:'bike',name:'Cycle',cat:'Cycles',kind:'bike',p:{}},
    {k:'stand',name:'Cycle stand',cat:'Cycles',kind:'stand',p:{}},
    {k:'bay',name:'Parking bay',cat:'Parking',kind:'bay',p:{}},
    {k:'car',name:'Car',cat:'Vehicles',kind:'vehicle',p:{v:'P',turn:false,side:'L'}},
    {k:'truck',name:'Delivery truck',cat:'Vehicles',kind:'vehicle',p:{v:'SU',turn:false,side:'L'}},
    {k:'bus',name:'City bus',cat:'Vehicles',kind:'vehicle',p:{v:'BUS',turn:false,side:'L'}},
    {k:'broadleaf',name:'Broadleaf tree',cat:'Trees',kind:'tree',p:{leaf:'B',cyc:'D',size:'M'}},
    {k:'conifer',name:'Conifer',cat:'Trees',kind:'tree',p:{leaf:'C',cyc:'E',size:'M'}}];
  var BIM_ENT_COL={People:'#c99a6e',Cycles:'#5f7f9e',Parking:'#e8e2c6',Trees:'#5b8a4c',Vehicles:'#7f8fa6'};
  function bimEntSpec(key){var i;for(i=0;i<BIM_ENT.length;i++)if(BIM_ENT[i].k===key)return BIM_ENT[i];return null;}
  function bimEntLerp(a,b,t){return a+(b-a)*t;}
  /* a person: the height (the registry's mean for who they are, or their own), then the eye height and the shoulders,
     each linear in stature between NASA's smallest and largest, as NASA's tables are built; the eyes are the head's
     top-to-eye distance (sitting height less eye height sitting) below the top, standing or seated */
  function bimEntBody(p){
    var st=p.h>0?p.h:bimStd('body.us',p.who==='child'?'child':(p.who==='man'?'man':'woman')),
      lo=bimStd('body.hidh','st_lo'),hi=bimStd('body.hidh','st_hi'),t=(st-lo)/((hi-lo)||1),
      sit=bimEntLerp(bimStd('body.hidh','sit_lo'),bimStd('body.hidh','sit_hi'),t),
      es=bimEntLerp(bimStd('body.hidh','eye_lo'),bimStd('body.hidh','eye_hi'),t),
      sh=bimEntLerp(bimStd('body.hidh','sh_lo'),bimStd('body.hidh','sh_hi'),t),seated=p.pose==='seated',seat=bimStd('app.assets','seat');
    return {st:st,t:t,sit:sit,head:sit-es,sh:sh,seated:seated,seat:seated?seat:0,eye:seated?seat+es:st-(sit-es),top:seated?seat+sit:st,
      out:t<0||t>1,speed:bimStd('walk.speed','m_min')/60};
  }
  /* a box from its middle and its sizes; a disc turned onto its side, its axis along x; the parts with their markers */
  function bimEntBox(c,z){var m=mkBoxP(z[0],z[1],z[2]);return {v:m.v.map(function(p){return [p[0]+c[0],p[1]+c[1],p[2]+c[2]];}),f:m.f};}
  function bimEntDisc(c,r,t){var m=mkCylP(r,t,360,16);return {v:m.v.map(function(p){return [c[0]+p[1],c[1]-p[0],c[2]+p[2]];}),f:m.f};}
  function bimEntMarked(parts,back,front){
    var m=bimMergeMeshes(parts);
    return {v:[[0,0,back],[0,0,front]].concat(m.v),f:m.f.map(function(fc){return fc.map(function(i){return i+2;});})};
  }
  function bimEntPersonMesh(B){
    var st=B.st,sh=B.sh,hh=Math.max(0.12,2*B.head),hw=Math.min(sh*0.42,hh*0.8),tw=sh*0.7,aw=(sh-tw)/2,d=Math.max(0.12,st*0.12),P=[],
      top=B.top,ys=top-hh-st*0.03,lw=tw*0.42;   /* the shoulders, under the neck; the eyes at the head's middle */
    P.push(bimEntBox([0,top-hh/2,0],[hw,hh,hh*0.85]));
    if(!B.seated){
      var yh=st*0.52;
      P.push(bimEntBox([0,(yh+ys)/2,0],[tw,ys-yh,d]));
      P.push(bimEntBox([-(tw/2+aw/2),ys-st*0.18,0],[aw,st*0.36,aw]),bimEntBox([tw/2+aw/2,ys-st*0.18,0],[aw,st*0.36,aw]));
      P.push(bimEntBox([-(tw/2-lw/2),yh/2,0],[lw,yh,d*0.85]),bimEntBox([tw/2-lw/2,yh/2,0],[lw,yh,d*0.85]));
    }else{
      var s2=B.seat,th=0.14,zb=-0.12;
      P.push(bimEntBox([0,s2/2,zb],[tw+0.06,s2,0.42]));
      P.push(bimEntBox([0,(s2+th+ys)/2,zb],[tw,ys-s2-th,d]));
      P.push(bimEntBox([-(tw/2+aw/2),ys-st*0.16,zb+0.05],[aw,st*0.32,aw]),bimEntBox([tw/2+aw/2,ys-st*0.16,zb+0.05],[aw,st*0.32,aw]));
      P.push(bimEntBox([-(tw/2-lw/2),s2+th/2,0.08],[lw,th,0.46]),bimEntBox([tw/2-lw/2,s2+th/2,0.08],[lw,th,0.46]));
      P.push(bimEntBox([-(tw/2-lw/2),s2/2,0.27],[lw*0.9,s2,0.1]),bimEntBox([tw/2-lw/2,s2/2,0.27],[lw*0.9,s2,0.1]));
    }
    return bimEntMarked(P,-0.3,0.3);
  }
  /* the wheelchair fills ADA's clear floor space less a margin; the person in it to the Access Board's study */
  function bimEntChairMesh(){
    var W=bimStd('ada.space','clear_w')*0.85,L=bimStd('ada.space','clear_l')*0.85,s2=bimStd('wheel.awmp','seat'),top=bimStd('wheel.awmp','height'),
      eye=bimStd('wheel.awmp','eye'),R=Math.min(0.31,s2*0.62),hh=Math.max(0.16,2*(top-eye)),tw=W*0.55,zb=-L/2+R+0.01,P=[];
    P.push(bimEntDisc([-W/2+0.02,R,zb],R,0.04),bimEntDisc([W/2-0.02,R,zb],R,0.04));
    P.push(bimEntDisc([-W/2+0.08,0.06,L/2-0.08],0.06,0.03),bimEntDisc([W/2-0.08,0.06,L/2-0.08],0.06,0.03));
    P.push(bimEntBox([0,s2-0.03,zb+0.12],[W-0.12,0.06,0.44]),bimEntBox([0,s2+0.22,zb-0.1],[W-0.12,0.44,0.04]));
    P.push(bimEntBox([0,(s2+top-hh-0.05)/2,zb+0.02],[tw,top-hh-0.05-s2,0.22]),bimEntBox([0,top-hh/2,zb+0.04],[hh*0.75,hh,hh*0.85]));
    P.push(bimEntBox([0,s2+0.06,zb+0.38],[tw,0.12,0.42]),bimEntBox([0,(s2+0.1)/2,zb+0.6],[tw,s2-0.1,0.1]));
    return bimEntMarked(P,-L/2,L/2);
  }
  function bimEntBikeMesh(){
    var L=bimStd('ltn.cycle','length'),W=bimStd('ltn.cycle','width'),D=bimStd('ltn.cycle','wheel'),H=bimStd('app.assets','bike_h'),r=D/2,zf=L/2-r,zr=-(L/2-r),P=[];
    P.push(bimEntDisc([0,r,zr],r,0.04),bimEntDisc([0,r,zf],r,0.04));
    P.push(bimEntBox([0,r+0.18,(zr+zf)/2],[0.04,0.04,zf-zr-0.2]),bimEntBox([0,(r+H*0.92)/2,zr+0.35],[0.04,H*0.92-r,0.04]));
    P.push(bimEntBox([0,H*0.9,zr+0.33],[0.12,0.04,0.24]),bimEntBox([0,(r+H)/2,zf-0.08],[0.04,H-r,0.04]),bimEntBox([0,H-0.02,zf-0.08],[W,0.04,0.04]));
    return bimEntMarked(P,-L/2,L/2);
  }
  function bimEntStandMesh(){
    var w=bimStd('app.assets','stand_w'),h=bimStd('app.assets','stand_h'),t=0.05;
    return bimEntMarked([bimEntBox([0,h/2,-w/2+t/2],[t,h,t]),bimEntBox([0,h/2,w/2-t/2],[t,h,t]),bimEntBox([0,h-t/2,0],[t,t,w])],-w/2,w/2);
  }
  /* a bay's lines on the ground, its back and sides, open at the front */
  function bimEntBayMesh(){
    var W=bimStd('parking.bay','width'),L=bimStd('parking.bay','length'),lw=bimStd('app.assets','line'),y=0.005;
    return bimEntMarked([bimEntBox([-(W/2-lw/2),y,0],[lw,0.01,L]),bimEntBox([W/2-lw/2,y,0],[lw,0.01,L]),bimEntBox([0,y,-L/2+lw/2],[W-2*lw,0.01,lw])],-L/2,L/2);
  }
  /* a tree's sizes: its type's in the Urban Tree Database (leaf, cycle, size), or its own */
  function bimEntTreeType(p){
    var T=bimStd('utd.trees','types')||[],lf=p.leaf==='C'?'C':'B',sz=/^[SML]$/.test(p.size||'')?p.size:'M',keys=[lf+(p.cyc==='E'?'E':'D')+sz,lf+'E'+sz,lf+'D'+sz],i,j;
    for(j=0;j<keys.length;j++)for(i=0;i<T.length;i++)if(T[i][0]===keys[j])return {key:keys[j],h:T[i][1],cd:T[i][2],r:T[i][3]};
    return null;
  }
  function bimEntTreeSize(p){
    var T=bimEntTreeType(p)||{h:bimCtxTreeH(),cd:bimCtxTreeH()*bimStd('app.assets','crown'),key:''};
    return {h:p.h>0?p.h:T.h,cd:p.cd>0?p.cd:T.cd,key:T.key};
  }
  /* the trunk first, then the crown: for a broadleaf V157's twenty faces, sized now to the crown's spread and the tree's
     height (V157's were 0.85 of both, its icosahedron sized by its corners); for a conifer a cone of eight sides */
  function bimEntTreeMesh(x,z,y,h,cd,con){
    var v=[],f=[],i,r=Math.max(0.08,h*0.025),cr=Math.max(con?0.4:0.6,cd/2),rv=Math.min(cr,h*0.45),cb=con?y+Math.max(0.5,h*0.2):y+h-rv,b;
    for(i=0;i<6;i++){var a=i*Math.PI/3;v.push([x+r*Math.cos(a),y,z+r*Math.sin(a)]);}
    for(i=0;i<6;i++){var a2=i*Math.PI/3;v.push([x+r*Math.cos(a2),cb,z+r*Math.sin(a2)]);}
    for(i=0;i<6;i++){var j=(i+1)%6;f.push([i,j,j+6,i+6]);}
    b=v.length;
    if(!con){
      var g=(1+Math.sqrt(5))/2,ico=[[-1,g,0],[1,g,0],[-1,-g,0],[1,-g,0],[0,-1,g],[0,1,g],[0,-1,-g],[0,1,-g],[g,0,-1],[g,0,1],[-g,0,-1],[-g,0,1]],
        tri=[[0,11,5],[0,5,1],[0,1,7],[0,7,10],[0,10,11],[1,5,9],[5,11,4],[11,10,2],[10,7,6],[7,1,8],[3,9,4],[3,4,2],[3,2,6],[3,6,8],[3,8,9],[4,9,5],[2,4,11],[6,2,10],[8,6,7],[9,8,1]];
      for(i=0;i<12;i++)v.push([x+ico[i][0]/g*cr,cb+ico[i][1]/g*rv,z+ico[i][2]/g*cr]);
      for(i=0;i<20;i++)f.push([b+tri[i][0],b+tri[i][1],b+tri[i][2]]);
      return {mesh:{v:v,f:f},cf:6};
    }
    for(i=0;i<8;i++){var a3=i*Math.PI/4;v.push([x+cr*Math.cos(a3),cb,z+cr*Math.sin(a3)]);}
    v.push([x,y+h,z]);
    for(i=0;i<8;i++)f.push([b+i,b+8,b+(i+1)%8]);
    f.push([b+7,b+6,b+5,b+4,b+3,b+2,b+1,b]);
    return {mesh:{v:v,f:f},cf:6};
  }
  /* a mapped tree's leaf, from OpenStreetMap's tags; what is not mapped stays unsaid */
  function bimEntLeafOf(t){
    t=t||{};var lt=String(t.leaf_type||''),lc=String(t.leaf_cycle||'');
    return {type:lt==='needleleaved'?'C':(lt==='broadleaved'?'B':''),cyc:/^(semi_)?deciduous$/.test(lc)?'D':(/^(semi_)?evergreen$/.test(lc)?'E':'')};
  }
  /* its crown across, of its height: the Urban Tree Database's medium tree of its kind; the app's rule where its leaf
     type is not mapped */
  function bimEntCrownRatio(t){
    var L=bimEntLeafOf(t),T=L.type?bimEntTreeType({leaf:L.type,cyc:L.cyc||(L.type==='C'?'E':'D'),size:'M'}):null;
    return T?T.r:bimStd('app.assets','crown');
  }
  /* a design vehicle (169d): AASHTO's length, width, height, overhangs, wheelbase and turning radii; the body's shape
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
  function bimEntVehMesh(V,bare){   /* __acad3dV171: bare, without its wheels (the simulation's cars) */
    var L=V.l,W=V.w,H=V.h,r=V.d/2,zf=L/2-V.of,zr=-L/2+V.or,tw=Math.min(0.3,W*0.12),xw=W/2-tw/2,y0=r*0.5,P=[];
    if(!bare)P.push(bimEntDisc([-xw,r,zf],r,tw),bimEntDisc([xw,r,zf],r,tw),bimEntDisc([-xw,r,zr],r,tw),bimEntDisc([xw,r,zr],r,tw));
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
  function bimEntBuild(a){
    var p=a.p||{},m=null,cf=-1,i,k;
    try{
      if(a.k==='person')m=bimEntPersonMesh(bimEntBody(p));
      else if(a.k==='wheelchair')m=bimEntChairMesh();
      else if(a.k==='bike')m=bimEntBikeMesh();
      else if(a.k==='stand')m=bimEntStandMesh();
      else if(a.k==='bay')m=bimEntBayMesh();
      else if(a.k==='vehicle')m=bimEntVehMesh(bimEntVeh(p));
      else if(a.k==='tree'){var S=bimEntTreeSize(p),T=bimEntTreeMesh(0,0,0,S.h,S.cd,p.leaf==='C');m=bimEntMarked([T.mesh],-S.cd/2,S.cd/2);cf=T.cf;}
    }catch(e){console.warn('[BIM] An asset could not be built',e);a3dToast('That asset could not be built - see the console');return null;}
    if(!m||!m.v||!m.v.length)return null;
    for(i=0;i<m.v.length;i++)for(k=0;k<3;k++)if(!isFinite(m.v[i][k])){
      console.warn('[BIM] An asset\'s size is missing from the standards registry: '+(a.k||''));a3dToast('That asset could not be sized - see the console');return null;}
    return {mesh:m,cf:cf};
  }
  /* its heading (0 facing +Z) and its centre, local, from the markers */
  function bimEntFrame(o){
    var v=o&&o.mesh&&o.mesh.v;
    if(!v||v.length<2)return {a:0,c:[0,0],y:0};
    return {a:Math.atan2(v[1][0]-v[0][0],v[1][2]-v[0][2]),c:[(v[0][0]+v[1][0])/2,(v[0][2]+v[1][2])/2],y:v[0][1]};
  }
  function bimEntPlace(key,posXZ,p0){
    var sp=bimEntSpec(key),k;
    if(!sp)return null;
    var a={k:sp.kind,key:key,p:JSON.parse(JSON.stringify(sp.p))};
    if(p0)for(k in p0)if(p0.hasOwnProperty(k))a.p[k]=p0[k];
    var b=bimEntBuild(a);
    if(!b)return null;
    a.cf=b.cf;
    pushUndo();
    A3D.counts.asset=(A3D.counts.asset||0)+1;
    var lvl=bimGetActiveLevel(),o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:sp.name+' '+A3D.counts.asset,
      pos:[posXZ[0],lvl.elev,posXZ[1]],mesh:b.mesh,col:BIM_ENT_COL[sp.cat],layer:A3D.activeLayer,asset:a,
      bim:{type:'familyInstance',familyId:'asset:'+key,familyName:sp.name,category:sp.cat,levelId:A3D.activeLevel}};
    A3D.objs.push(o);
    A3D.sel=o.id;A3D.sel2=null;A3D.selSet=[o.id];
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast(o.name+' placed');
    return o;
  }
  /* built again from its parameters, where it stands and facing the way it faced */
  function bimEntRebuild(o){
    var b=bimEntBuild(o.asset);
    if(!b)return false;
    var F=bimEntFrame(o),ca=Math.cos(F.a),sa=Math.sin(F.a);
    o.mesh={v:b.mesh.v.map(function(p){return [F.c[0]+p[0]*ca+p[2]*sa,F.y+p[1],F.c[1]-p[0]*sa+p[2]*ca];}),f:b.mesh.f};
    o.asset.cf=b.cf;
    return true;
  }
  /* every placed asset built again after a standards change (169d), from its own parameters and the registry's sizes */
  function bimEntRefit(){
    var n=0,i,o;
    for(i=0;i<A3D.objs.length;i++){o=A3D.objs[i];if(o.asset&&o.asset.k&&o.mesh&&bimEntRebuild(o))n++;}
    A3D.lastRefit=n;
    return n;
  }
  /* ---- the leaves: the site's growing season (169a), from its climate ---- */
  function bimEntDoy(date,sh){
    var m=/^(\d{4})-(\d{2})-(\d{2})/.exec(String(date||''));
    if(!m)return null;
    var Y=+m[1],M=+m[2],sy=(sh&&M<7)?Y-1:Y;
    return Math.round((Date.UTC(Y,M-1,+m[3])-Date.UTC(sy,sh?6:0,1))/864e5);
  }
  function bimEntSeason(){var C=A3D.site&&A3D.site.climate;return C&&C.gsl&&typeof C.gsl.s==='number'?C.gsl:null;}
  function bimEntInLeaf(date){var G=bimEntSeason(),d;if(!G)return true;d=bimEntDoy(date,G.sh);return d===null?true:(d>=G.s&&d<G.e);}
  function bimEntBare(o,date){
    var a=o&&o.asset;
    return !!(a&&a.k==='tree'&&a.p&&a.p.cyc!=='E'&&a.cf>0&&!bimEntInLeaf(date||bimSunSettings().date));
  }
  function bimEntDayName(d,sh){
    var t=new Date(Date.UTC(2025,sh?6:0,1)+d*864e5);
    return t.getUTCDate()+' '+['January','February','March','April','May','June','July','August','September','October','November','December'][t.getUTCMonth()];
  }
  function bimEntSeasonText(p){
    if(p.cyc==='E')return 'all year: evergreen';
    var G=bimEntSeason(),date=bimSunSettings().date;
    if(!G)return 'all year, taken so: the site\'s climate is not fetched (Analyze site), so its growing season is not known';
    if(G.s>=G.e)return 'never: the site\'s climate has no growing season (ETCCDI\'s GSL, '+G.years+' years)';
    return 'from '+bimEntDayName(G.s,G.sh)+' to '+bimEntDayName(G.e-1,G.sh)+', the site\'s growing season (ETCCDI\'s GSL, the median of '+G.years+' years); '+
      'the leaves come out some weeks after it starts. On the sun study\'s date, '+date+': '+(bimEntInLeaf(date)?'in leaf':'bare, its trunk alone casting a shadow');
  }
  /* ---- the turning spaces shown on the plan ---- */
  function bimEntTurns(){
    var out=[],i,o,a,F,q;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];a=o.asset;
      if(!a||!a.p||!a.p.turn||!o.mesh||!bimLayerShown(o))continue;
      F=bimEntFrame(o);q=bimObjOffset(o);
      if(a.k==='wheelchair')out.push({id:o.id,c:[F.c[0]+q[0],F.c[1]+q[2]],y:q[1]+F.y,r:[bimStd('ada.space','turn')/2],what:'the turning space'});
      else if(a.k==='vehicle'){
        var V=bimEntVeh(a.p),fx=Math.sin(F.a),fz=Math.cos(F.a),sd=a.p.side==='R'?-1:1,zr=-V.l/2+V.or,ax=F.c[0]+fx*zr,az=F.c[1]+fz*zr;
        out.push({id:o.id,c:[ax+q[0]+sd*fz*V.rr,az+q[2]-sd*fx*V.rr],y:q[1]+F.y,r:[V.rin,V.r,V.rov],what:'its turning path',side:sd>0?'L':'R'});
      }
    }
    return out;
  }
  function bimEntDrawTurns(ctx,V,W,H){
    var T=bimEntTurns(),i,j,k,s2,on;
    A3D.lastTurns=T.length;
    if(!T.length)return;
    ctx.save();ctx.lineWidth=1.5;if(ctx.setLineDash)ctx.setLineDash([6,4]);
    ctx.strokeStyle='rgba(56,189,248,0.95)';ctx.fillStyle='rgba(56,189,248,0.12)';
    function ring(t,rad){
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
    ctx.restore();
  }
  /* ---- Properties: the Asset group ---- */
  function bimEntSel(key,opts,cur){
    return '<select data-propf="asset:'+key+'">'+opts.map(function(x){return '<option value="'+x[0]+'"'+(x[0]===cur?' selected':'')+'>'+bimEsc(x[1])+'</option>';}).join('')+'</select>';
  }
  function bimEntStdHtml(L){return L.map(function(t){var s2=bimStdUsedText(t);return s2?'<div class="a3d-stdsrc">Standards: '+bimEsc(s2)+'</div>':'';}).join('');}
  function bimEntBy(label,a,b){return bimPropText(bimLenLabel(label),bimDispLen(a)+' by '+bimDispLen(b));}
  function bimEntPropsHtml(o){
    var a=o.asset,p=a.p||{},r='',L=[];
    if(a.k==='person'){
      var B=bimEntBody(p);
      r+=bimPropRow('Who',bimEntSel('who',[['man','A man'],['woman','A woman'],['child','A child of 8']],p.who));
      r+=bimPropRow('Pose',bimEntSel('pose',[['standing','Standing'],['seated','Seated']],p.pose));
      r+=bimPropLen('Height',B.st,'asset:h',0.3);
      if(B.seated)r+=bimPropLenText('Height, seated',B.top);
      r+=bimPropLenText('Eye height',B.eye)+bimPropLenText('Shoulder width',B.sh)+bimPropText('Walking speed',bimStdFmt(Math.round(B.speed*100)/100,'m/s'));
      if(B.out)r+=bimPropText('Proportions','outside the adults NASA\'s tables span: extrapolated, an estimate');
      L=['body.us','body.hidh','walk.speed'].concat(B.seated?['app.assets']:[]);
    }else if(a.k==='wheelchair'){
      r+=bimPropLenText('Height',bimStd('wheel.awmp','height'))+bimPropLenText('Seat',bimStd('wheel.awmp','seat'))+bimPropLenText('Eye height',bimStd('wheel.awmp','eye'));
      r+=bimPropText(bimLenLabel('Space'),bimDispLen(bimStd('ada.space','clear_w'))+' by '+bimDispLen(bimStd('ada.space','clear_l'))+': the clear floor space; '+
        bimDispLen(bimStd('wheel.awmp','space_w'))+' by '+bimDispLen(bimStd('wheel.awmp','space_l'))+' holds 95% of manual chair users');
      r+=bimPropText(bimLenLabel('Turning'),bimDispLen(bimStd('ada.space','turn'))+' across: the turning space');
      r+=bimPropRow('On the plan','<input type="checkbox" data-propf="asset:turn"'+(p.turn?' checked':'')+'> its turning space');
      r+=bimPropText('Speed',bimStdFmt(bimStd('mutcd.walk','slow'),'m/s'));
      L=['wheel.awmp','ada.space','mutcd.walk'];
    }else if(a.k==='bike'){
      r+=bimEntBy('Size',bimStd('ltn.cycle','length'),bimStd('ltn.cycle','width'))+bimPropLenText('Wheel',bimStd('ltn.cycle','wheel'));
      r+=bimPropText(bimLenLabel('Turning circle'),'outer radius '+bimDispLen(bimStd('ltn.cycle','turn_out'))+', inner '+bimDispLen(bimStd('ltn.cycle','turn_in')));
      L=['ltn.cycle','app.assets'];
    }else if(a.k==='stand'){
      r+=bimPropText(bimLenLabel('Spacing'),bimDispLen(bimStd('ltn.cycle','gap'))+' recommended, '+bimDispLen(bimStd('ltn.cycle','gap_min'))+' at least; two cycles a stand');
      r+=bimPropLenText('Bay length',bimStd('ltn.cycle','bay'))+bimPropLenText('Access aisle',bimStd('ltn.cycle','aisle'));
      r+=bimPropText(bimLenLabel('Clearance'),bimDispLen(bimStd('ltn.cycle','wall'))+' to a wall, '+bimDispLen(bimStd('ltn.cycle','front'))+' clear in front');
      L=['ltn.cycle','app.assets'];
    }else if(a.k==='bay'){
      r+=bimEntBy('Bay',bimStd('parking.bay','width'),bimStd('parking.bay','length'));
      r+=bimPropText(bimLenLabel('Aisle'),bimDispLen(bimStd('parking.bay','aisle90'))+' at 90 degrees, '+bimDispLen(bimStd('parking.bay','aisle60'))+' at 60, '+bimDispLen(bimStd('parking.bay','aisle45'))+' at 45');
      L=['parking.bay','app.assets'];
    }else if(a.k==='vehicle'){
      var V=bimEntVeh(p);
      r+=bimPropText('Design vehicle',V.name+' (AASHTO '+V.sym+')');
      r+=bimEntBy('Size',V.l,V.w)+(V.c==='SU'?bimPropText(bimLenLabel('Height'),bimDispLen(V.hlo)+' to '+bimDispLen(V.h)+', drawn at '+bimDispLen(V.h)):bimPropLenText('Height',V.h));
      r+=bimPropLenText('Wheelbase',V.wb)+bimPropText(bimLenLabel('Overhangs'),bimDispLen(V.of)+' in front, '+bimDispLen(V.or)+' behind');
      r+=bimPropText(bimLenLabel('Radius'),bimDispLen(V.r)+' at the least: the minimum design turning radius');
      r+=bimPropText(bimLenLabel('CTR'),bimDispLen(V.ctr)+': the centreline turning radius');
      r+=bimPropText(bimLenLabel('Inside'),bimDispLen(V.rin)+' at the least: the minimum inside radius');
      r+=bimPropText(bimLenLabel('Corner'),bimDispLen(V.rov)+': the front overhang\'s outer corner from the turn\'s centre, worked out from the sizes above');
      r+=bimPropRow('On the plan','<input type="checkbox" data-propf="asset:turn"'+(p.turn?' checked':'')+'> its turning path');
      r+=bimPropRow('Turning',bimEntSel('side',[['L','To the left'],['R','To the right']],p.side==='R'?'R':'L'));
      L=['aashto.vehicles','app.assets'];
    }else if(a.k==='tree'){
      var S=bimEntTreeSize(p);
      r+=bimPropRow('Leaf',bimEntSel('leaf',[['B','Broadleaf'],['C','Conifer']],p.leaf==='C'?'C':'B'));
      r+=bimPropRow('Leaves',bimEntSel('cyc',[['D','Deciduous'],['E','Evergreen']],p.cyc==='E'?'E':'D'));
      r+=bimPropRow('Size',bimEntSel('size',[['S','Small'],['M','Medium'],['L','Large']],p.size||'M'));
      r+=bimPropLen('Height',S.h,'asset:h',0.5)+bimPropLen('Crown across',S.cd,'asset:cd',0.3);
      r+=bimPropText('In leaf',bimEntSeasonText(p));
      L=['utd.trees','etccdi.gsl'];
    }
    return bimPropGroup('Asset',r+bimEntStdHtml(L));
  }
  function bimEntPropSet(o,key,val,chk){
    var a=o.asset,p=a.p,v=null;
    if(key==='h'||key==='cd'){v=parseFloat(val);if(!isFinite(v)||v<=0){a3dToast('Must be a positive number');refreshProps();return false;}}
    else if(key!=='turn'&&!/^(who|pose|leaf|cyc|size|side)$/.test(key))return false;
    pushUndo();
    if(key==='turn')p.turn=!!chk;
    else if(v!==null)p[key]=v;
    else if(key==='side')p.side=val==='R'?'R':'L';
    else{p[key]=String(val);if(key!=='pose')delete p.h;if(key!=='pose'&&key!=='who')delete p.cd;}
    if(!bimEntRebuild(o)){refreshProps();return false;}
    refreshProps();paint();saveSoon();
    return true;
  }
  /* the library's tiles: each kind built once with the registry's sizes, for its thumbnail */
  function bimEntLib(es){
    if(!es.lib){var b=bimEntBuild({k:es.kind,p:JSON.parse(JSON.stringify(es.p))});es.lib={id:'asset:'+es.k,kind:'model',builtin:true,name:es.name,category:es.cat,mesh:b?b.mesh:{v:[],f:[]},thumb:''};}
    return es.lib;
  }
  /* A mesh drawn from above one corner, flat-shaded, back faces first: what the thing looks like.
     No face is culled, so a mesh whose faces run either way round still draws whole. */
  function bimMeshThumb(mesh,w,h){
    w=w||96;h=h||72;
    try{
      if(!mesh||!mesh.v||!mesh.v.length||!mesh.f||!mesh.f.length)return '';
      var c=document.createElement('canvas');c.width=w;c.height=h;
      var g=c.getContext('2d');if(!g)return '';
      var S2=Math.SQRT2,S6=Math.sqrt(6),i,k;
      var P=mesh.v.map(function(v){return [(v[0]-v[2])/S2,-(2*v[1]-v[0]-v[2])/S6];});
      var mnx=Infinity,mny=Infinity,mxx=-Infinity,mxy=-Infinity;
      for(i=0;i<P.length;i++){
        if(P[i][0]<mnx)mnx=P[i][0];if(P[i][0]>mxx)mxx=P[i][0];
        if(P[i][1]<mny)mny=P[i][1];if(P[i][1]>mxy)mxy=P[i][1];
      }
      var pad=6,sc=Math.min((w-2*pad)/Math.max(mxx-mnx,1e-9),(h-2*pad)/Math.max(mxy-mny,1e-9));
      var ox=(w-(mxx-mnx)*sc)/2-mnx*sc,oy=(h-(mxy-mny)*sc)/2-mny*sc;
      var L=[0.36,0.84,0.4],faces=[];
      for(i=0;i<mesh.f.length;i++){
        var f=mesh.f[i];if(!f||f.length<3)continue;
        var n=[0,0,0],d=0;
        for(k=0;k<f.length;k++){
          var a=mesh.v[f[k]],b=mesh.v[f[(k+1)%f.length]];
          if(!a||!b){n=null;break;}
          n[0]+=(a[1]-b[1])*(a[2]+b[2]);n[1]+=(a[2]-b[2])*(a[0]+b[0]);n[2]+=(a[0]-b[0])*(a[1]+b[1]);
          d+=a[0]+a[1]+a[2];
        }
        if(!n)continue;
        var nl=Math.sqrt(n[0]*n[0]+n[1]*n[1]+n[2]*n[2])||1;
        faces.push({f:f,d:d/f.length,l:Math.abs(n[0]*L[0]+n[1]*L[1]+n[2]*L[2])/nl});
      }
      faces.sort(function(p,q){return p.d-q.d;});
      g.lineWidth=0.6;g.strokeStyle='rgba(20,28,40,.55)';
      for(i=0;i<faces.length;i++){
        var ff=faces[i].f,sh=Math.round(95+faces[i].l*120);
        g.fillStyle='rgb('+Math.round(sh*0.82)+','+Math.round(sh*0.9)+','+sh+')';
        g.beginPath();
        for(k=0;k<ff.length;k++){
          var q=P[ff[k]];
          if(k)g.lineTo(ox+q[0]*sc,oy+q[1]*sc);else g.moveTo(ox+q[0]*sc,oy+q[1]*sc);
        }
        g.closePath();g.fill();
        if(faces.length<4000)g.stroke();
      }
      return c.toDataURL('image/png');
    }catch(eT){console.warn('[BIM] A thumbnail could not be drawn.',eT);return '';}
  }
  /* The plan lines of a set of object records: outlines, centrelines, profiles and the top view of
     every mesh, each in world plan coordinates (x, z). */
  function bimRecsPlanLines(recs){
    var out=[],i,j,k;
    function add(pts,close,off){
      if(!pts||pts.length<2)return;
      var ln=[];
      for(k=0;k<pts.length;k++){var p=pts[k];if(p&&isFinite(p[0])&&isFinite(p[1]))ln.push([p[0]+off[0],p[1]+off[1]]);}
      if(close&&ln.length>2)ln.push(ln[0]);
      if(ln.length>1)out.push(ln);
    }
    for(i=0;i<(recs||[]).length;i++){
      var r=recs[i];if(!r)continue;
      var q=r.pos||[0,0,0],off=[q[0]||0,q[2]||0];
      if(r.mesh&&r.mesh.f&&r.mesh.v){
        for(j=0;j<r.mesh.f.length&&j<3000;j++){
          var f=r.mesh.f[j],pl=[];
          for(k=0;k<f.length;k++){var v=r.mesh.v[f[k]];if(v)pl.push([v[0],v[2]]);}
          add(pl,true,off);
        }
      }else if(r.pts){add(r.pts,r.t==='room'||r.closed,off);}
      else if(r.t==='dim'&&r.p1&&r.p2){add([r.p1,r.d1||r.p1,r.d2||r.p2,r.p2],false,off);}
      else if(r.t==='text'&&r.pt){add([[r.pt[0]-0.3,r.pt[1]],[r.pt[0]+0.3,r.pt[1]]],false,off);}
    }
    return out;
  }
  function bimRecsThumb(recs,w,h){
    w=w||96;h=h||72;
    try{
      var L=bimRecsPlanLines(recs),i,k;
      if(!L.length)return '';
      var c=document.createElement('canvas');c.width=w;c.height=h;
      var g=c.getContext('2d');if(!g)return '';
      var mnx=Infinity,mnz=Infinity,mxx=-Infinity,mxz=-Infinity;
      for(i=0;i<L.length;i++)for(k=0;k<L[i].length;k++){
        var p=L[i][k];
        if(p[0]<mnx)mnx=p[0];if(p[0]>mxx)mxx=p[0];if(p[1]<mnz)mnz=p[1];if(p[1]>mxz)mxz=p[1];
      }
      var pad=6,sc=Math.min((w-2*pad)/Math.max(mxx-mnx,1e-9),(h-2*pad)/Math.max(mxz-mnz,1e-9));
      var ox=(w-(mxx-mnx)*sc)/2-mnx*sc,oy=(h-(mxz-mnz)*sc)/2-mnz*sc;
      g.strokeStyle='#c9d6e6';g.lineWidth=1;g.lineJoin='round';
      for(i=0;i<L.length;i++){
        g.beginPath();
        for(k=0;k<L[i].length;k++){
          var x=ox+L[i][k][0]*sc,y=oy+L[i][k][1]*sc;
          if(k)g.lineTo(x,y);else g.moveTo(x,y);
        }
        g.stroke();
      }
      return c.toDataURL('image/png');
    }catch(eT){console.warn('[BIM] A thumbnail could not be drawn.',eT);return '';}
  }
  /* An entry's thumbnail, made the first time it is asked for when the entry has none -- every
     entry stored before V124, and the starter set -- and kept, so it is drawn once. */
  function bimAssetThumb(e){
    if(!e)return '';
    if(typeof e.thumb==='string'&&e.thumb)return e.thumb;
    var kd=bimAssetKind(e),th='';
    if(kd==='model')th=bimMeshThumb(e.mesh);
    else if(kd==='block')th=bimRecsThumb(e.recs);
    e.thumb=th;
    if(th&&!e.builtin)bimSaveFamilyLibrary();
    return th;
  }
  function bimCreateFamilyInstance(fam,posXZ,levelElev,seq){
    var meshCopy=bimCloneMesh(fam.mesh);
    return {
      id:'a3d-'+Date.now().toString(36)+'-'+seq,t:'solid',name:fam.name+'_'+seq,
      pos:[posXZ[0],levelElev,posXZ[1]],mesh:meshCopy,
      bim:{type:'familyInstance',familyId:fam.id,familyName:fam.name,category:fam.category}
    };
  }
  /* __acad3dV124: every selected solid, in world position, as one mesh -- so a table saved with its
     chairs comes back with them. It took only the first selected object before. */
  function bimSelectionMesh(ids){
    var parts=[],i,j;
    for(i=0;i<ids.length;i++){
      var so=objById(ids[i]);if(!so)continue;
      var sm=meshOf(so);if(!sm||!sm.f||!sm.f.length||!sm.v||!sm.v.length)continue;
      var q=bimObjOffset(so),v=[];
      for(j=0;j<sm.v.length;j++)v.push([sm.v[j][0]+q[0],sm.v[j][1]+q[1],sm.v[j][2]+q[2]]);
      parts.push({v:v,f:sm.f});
    }
    return parts.length?bimMergeMeshes(parts):null;
  }
  function openSaveAsFamilyDlg(){
    var o=objById(A3D.sel);
    if(!o){a3dToast('Select an object first');return;}
    var selIds=(A3D.selSet&&A3D.selSet.length)?A3D.selSet.slice():[o.id];
    var m=bimSelectionMesh(selIds);
    if(!m||!m.f||!m.f.length){a3dToast('Nothing selected has geometry to save as a model');return;}
    closeDlg();
    var d=document.createElement('div');
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">Save as Model</div>'+
      '<div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Name</label><input type="text" data-a3dp="name" value="'+bimEsc(o.name)+'" maxlength="60"></div>'+
      '<div class="a3d-dlgrow"><label>Category</label><select data-a3dp="cat">'+
        FAMILY_CATEGORIES.map(function(c){return '<option value="'+c+'">'+c+'</option>';}).join('')+
      '</select></div>'+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">OK</button></div>';
    el.root.appendChild(d);
    el.dlg=d;
    var nI=d.querySelector('[data-a3dp="name"]'),cI=d.querySelector('[data-a3dp="cat"]');
    function submit(){
      var name=nI.value.trim();
      var eb=document.getElementById('a3d-dlgerr');
      if(!name){eb.textContent='Enter a name';return;}
      closeDlg();
      var fam=bimFamilyLibraryAdd({name:name,category:cI.value,mesh:m});
      refreshFamilyPanel();
      a3dToast('Saved "'+fam.name+'" to the library'+(selIds.length>1?' ('+selIds.length+' objects as one model)':''));
    }
    d.addEventListener('click',function(ev){var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;if(!b)return;if(b.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();});
    d.addEventListener('keydown',function(ev){if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}});
    nI.focus();nI.select();
  }
  function bimImportFamilyFile(file){
    if(!file)return;
    var name=file.name||'import',ext=(name.split('.').pop()||'').toLowerCase();
    var reader=new FileReader();
    reader.onerror=function(){a3dToast('Failed to read '+name);};
    function afterParse(mesh){
      if(!mesh||!mesh.v.length||!mesh.f.length){a3dToast('No usable geometry found in '+name);return;}
      openImportFamilyNameDlg(mesh,name.replace(/\.[^.]+$/,''),{ext:ext,source:name});   /* __acad3dV124 */
    }
    if(ext==='obj'){
      reader.onload=function(ev){
        try{
          var res=objParse(ev.target.result);
          var real=res.meshes.filter(function(g){return g.v.length&&g.f.length;});
          if(!real.length){a3dToast('OBJ import: no faces found in '+name);return;}
          afterParse(real.length===1?real[0]:bimMergeMeshes(real));
        }catch(eP){console.warn('[BIM] Family OBJ parse failed:',eP);a3dToast('Could not parse '+name);}
      };
      reader.readAsText(file);
    }else if(ext==='stl'){
      reader.onload=function(ev){
        try{
          var buf=ev.target.result;
          var mesh=stlIsBinary(buf)?stlParseBinary(buf):stlParseAscii(new TextDecoder().decode(buf));
          afterParse(mesh);
        }catch(eP){console.warn('[BIM] Family STL parse failed:',eP);a3dToast('Could not parse '+name);}
      };
      reader.readAsArrayBuffer(file);
    }else if(ext==='skp'){   /* __acad3dV163: a SketchUp file's components, as blocks */
      reader.onload=function(ev){bimImportSKP(ev.target.result,name,{blocksOnly:true});};
      reader.readAsArrayBuffer(file);
    }else{
      a3dToast('The library imports .obj and .stl models, and .skp components (got .'+ext+')');
    }
  }
  /* __acad3dV124: what an imported model's numbers mean. OBJ carries no unit and STL none either,
     so the unit is asked, and the up axis with it; bimImportModelMesh is the one conversion, so what
     the dialog shows is what the library gets. */
  var A3D_IMPORT_UNITS=[['mm',0.001,'millimetres'],['cm',0.01,'centimetres'],['m',1,'metres'],
    ['in',0.0254,'inches'],['ft',0.3048,'feet']];
  function bimImportUnitScale(u){
    var i;
    for(i=0;i<A3D_IMPORT_UNITS.length;i++)if(A3D_IMPORT_UNITS[i][0]===u)return A3D_IMPORT_UNITS[i][1];
    return 1;
  }
  /* Z up to Y up is a quarter turn about X: the model's up (+Z) becomes +Y and its +Y runs away
     from the viewer, to -Z, so a right-handed model stays right-handed and is not mirrored. */
  function bimImportModelMesh(mesh,unit,zUp){
    var f=bimImportUnitScale(unit);
    return {v:mesh.v.map(function(p){return zUp?[p[0]*f,p[2]*f,-p[1]*f]:[p[0]*f,p[1]*f,p[2]*f];}),
      f:mesh.f.map(function(fc){return fc.slice();})};
  }
  /* The first guess: the unit that brings the largest side nearest 1.5 m. A guess is all it can be
     -- 180 is a person in centimetres and a door in millimetres -- so the dialog shows the size. */
  function bimGuessImportUnit(mesh){
    var b=bimMeshBounds(mesh),E=Math.max(b.mx[0]-b.mn[0],b.mx[1]-b.mn[1],b.mx[2]-b.mn[2]);
    if(!(E>0)||!isFinite(E))return 'm';
    var best='m',bd=Infinity,i;
    for(i=0;i<A3D_IMPORT_UNITS.length;i++){
      var d=Math.abs(Math.log(E*A3D_IMPORT_UNITS[i][1]/1.5));
      if(d<bd-1e-12){bd=d;best=A3D_IMPORT_UNITS[i][0];}
    }
    return best;
  }
  function openImportFamilyNameDlg(mesh,suggestedName,opt){
    opt=opt||{};
    closeDlg();
    var guess=bimGuessImportUnit(mesh),zUp=opt.ext==='stl';
    var d=document.createElement('div');
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">Import Model</div>'+
      '<div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Name</label><input type="text" data-a3dp="name" value="'+bimEsc(suggestedName)+'" maxlength="60"></div>'+
      '<div class="a3d-dlgrow"><label>Category</label><select data-a3dp="cat">'+
        FAMILY_CATEGORIES.map(function(c){return '<option value="'+c+'">'+c+'</option>';}).join('')+
      '</select></div>'+
      '<div class="a3d-dlgrow"><label>Drawn in</label><select data-a3dp="unit">'+
        A3D_IMPORT_UNITS.map(function(u){return '<option value="'+u[0]+'"'+(u[0]===guess?' selected':'')+'>'+u[2]+'</option>';}).join('')+
      '</select></div>'+
      '<div class="a3d-dlgrow"><label>Up axis</label><select data-a3dp="up">'+
        '<option value="y"'+(zUp?'':' selected')+'>Y up</option><option value="z"'+(zUp?' selected':'')+'>Z up</option>'+
      '</select></div>'+
      '<div class="a3d-impprev"><img data-a3dp="thumb" alt=""><div data-a3dp="size" class="a3d-impsize"></div></div>'+
      '<div class="a3d-propnote">The file does not say what unit it was drawn in: the first choice is a guess from its size. Check the size above.</div>'+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">Import</button></div>';
    el.root.appendChild(d);
    el.dlg=d;
    var nI=d.querySelector('[data-a3dp="name"]'),cI=d.querySelector('[data-a3dp="cat"]');
    var uI=d.querySelector('[data-a3dp="unit"]'),yI=d.querySelector('[data-a3dp="up"]');
    var sz=d.querySelector('[data-a3dp="size"]'),im=d.querySelector('[data-a3dp="thumb"]');
    function current(){return bimImportModelMesh(mesh,uI.value,yI.value==='z');}
    function show(){
      var m=current(),b=bimMeshBounds(m),u=bimUnitLabel();
      sz.textContent='Comes in at '+bimDispLen(b.mx[0]-b.mn[0])+' '+u+' wide, '+bimDispLen(b.mx[2]-b.mn[2])+' '+u+
        ' deep and '+bimDispLen(b.mx[1]-b.mn[1])+' '+u+' high';
      var th=bimMeshThumb(m,120,90);
      if(th)im.src=th;else im.removeAttribute('src');
    }
    uI.addEventListener('change',show);yI.addEventListener('change',show);
    show();
    function submit(){
      var name=nI.value.trim();
      var eb=document.getElementById('a3d-dlgerr');
      if(!name){eb.textContent='Enter a name';return;}
      var m=current();
      closeDlg();
      var fam=bimFamilyLibraryAdd({name:name,category:cI.value,mesh:m,unit:uI.value,source:opt.source||''});
      refreshFamilyPanel();
      var s=fam.mesh.size||[0,0,0],u=bimUnitLabel();
      a3dToast('Imported "'+fam.name+'" into the library ('+bimDispLen(s[0])+' x '+bimDispLen(s[2])+' x '+bimDispLen(s[1])+' '+u+')');
    }
    d.addEventListener('click',function(ev){var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;if(!b)return;if(b.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();});
    d.addEventListener('keydown',function(ev){if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}});
    nI.focus();nI.select();
  }
