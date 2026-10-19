#!/usr/bin/env python3
"""V169b: assets -- the models, placed and edited, and the trees' leaves in the sun studies.

- People (a man, a woman, a child of 8; standing or seated), a wheelchair user, a cycle and its stand, a parking
  bay, a broadleaf tree and a conifer: each a solid whose mesh is built from its parameters and the registry's
  sizes (169a). Its first two vertices mark its back and front at the ground, which no face uses, so its heading
  and centre come through every move, turn and mirror; a tree's trunk faces come before its crown's.
- The Assets panel's group People, cycles, parking and trees: dragged onto the drawing or clicked, as the models
  are. Properties' Asset group: the sizes, each with its standard; who, pose, height; a tree's leaf, cycle, size,
  height and crown, and when it is in leaf at the site; the wheelchair's turning space, shown on the plan.
- The sun studies (the plan's shadows, sun hours, the shadows analysis) leave out a deciduous tree's crown on a
  date outside the site's growing season.
- The context's trees (V157) take OpenStreetMap's leaf_type and leaf_cycle: a conifer drawn as a cone, the crown
  of a tree with no diameter_crown from the Urban Tree Database by leaf type (the owner, 2026-10-19), 0.6 of the
  height where the leaf type is not mapped.

Run from the repository root: python3 Phase/patch_phase169b.py
"""
import hashlib, pathlib, sys

SRC = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path('canvas_v10.html')
BASE = 'cc88dfbefca1e3acb001555ec43e2f396bf871f6be8f8897531004301ca76961'   # V169a

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


ENT = r'''
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
  /* the mesh, local, front +Z, base on the ground; and where a tree's crown starts */
  function bimEntBuild(a){
    var p=a.p||{},m=null,cf=-1,i,k;
    try{
      if(a.k==='person')m=bimEntPersonMesh(bimEntBody(p));
      else if(a.k==='wheelchair')m=bimEntChairMesh();
      else if(a.k==='bike')m=bimEntBikeMesh();
      else if(a.k==='stand')m=bimEntStandMesh();
      else if(a.k==='bay')m=bimEntBayMesh();
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
    }
    return out;
  }
  function bimEntDrawTurns(ctx,V,W,H){
    var T=bimEntTurns(),i,j,k,s2,on;
    A3D.lastTurns=T.length;
    if(!T.length)return;
    ctx.save();ctx.lineWidth=1.5;if(ctx.setLineDash)ctx.setLineDash([6,4]);
    ctx.strokeStyle='rgba(56,189,248,0.95)';ctx.fillStyle='rgba(56,189,248,0.12)';
    for(i=0;i<T.length;i++)for(j=0;j<T[i].r.length;j++){
      ctx.beginPath();on=false;
      for(k=0;k<=48;k++){
        var an=k/48*Math.PI*2;
        s2=toScreen([T[i].c[0]+T[i].r[j]*Math.cos(an),T[i].y+0.02,T[i].c[1]+T[i].r[j]*Math.sin(an)],V,W,H);
        if(!s2)continue;
        if(on)ctx.lineTo(s2[0],s2[1]);else{ctx.moveTo(s2[0],s2[1]);on=true;}
      }
      ctx.closePath();ctx.fill();ctx.stroke();
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
      r+=bimPropLenText('Height',bimStd('wheel.awmp','height'))+bimPropLenText('Seat height',bimStd('wheel.awmp','seat'))+bimPropLenText('Eye height',bimStd('wheel.awmp','eye'));
      r+=bimEntBy('Clear floor space',bimStd('ada.space','clear_w'),bimStd('ada.space','clear_l'))+bimEntBy('Space for 95% of users',bimStd('wheel.awmp','space_w'),bimStd('wheel.awmp','space_l'));
      r+=bimPropLenText('Turning space, across',bimStd('ada.space','turn'));
      r+=bimPropRow('Show it on the plan','<input type="checkbox" data-propf="asset:turn"'+(p.turn?' checked':'')+'>');
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
      r+=bimPropText(bimLenLabel('Aisle to reach it'),bimDispLen(bimStd('parking.bay','aisle90'))+' at 90 degrees, '+bimDispLen(bimStd('parking.bay','aisle60'))+' at 60, '+bimDispLen(bimStd('parking.bay','aisle45'))+' at 45');
      L=['parking.bay','app.assets'];
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
    else if(key!=='turn'&&!/^(who|pose|leaf|cyc|size)$/.test(key))return false;
    pushUndo();
    if(key==='turn')p.turn=!!chk;
    else if(v!==null)p[key]=v;
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
'''
rep("      mesh:bimNormalizeMeshForFamily(bimAsmMesh(s.parts)),thumb:''};\n  });\n",
    "      mesh:bimNormalizeMeshForFamily(bimAsmMesh(s.parts)),thumb:''};\n  });\n" + ENT)

# ---- the Assets panel: the group, the click and the drop ----
rep("    h+=grp('families','Models',models.length+' item(s)',body,true);",
    "    h+=grp('families','Models',models.length+' item(s)',body,true);\n"
    "    /* __acad3dV169: people, cycles, parking and trees, sized from the registry */\n"
    "    body='';\n"
    "    for(i=0;i<BIM_ENT.length;i++){\n"
    "      if(!bimAssetMatch(q,[BIM_ENT[i].name,BIM_ENT[i].cat,'asset','people','scale','entourage']))continue;\n"
    "      body+=tile('asset:'+BIM_ENT[i].k,bimEntLib(BIM_ENT[i]),BIM_ENT[i].cat,true,'');\n"
    "    }\n"
    "    h+=grp('entourage','People, cycles, parking and trees',BIM_ENT.length+' item(s)',body,true);")
rep("    if(kind==='family'){\n      var fam=bimFamilyLibraryGet(key);",
    "    if(kind==='asset')return !!bimEntPlace(key,at||bimViewCentrePlan());   /* __acad3dV169 */\n"
    "    if(kind==='family'){\n      var fam=bimFamilyLibraryGet(key);")
rep("    if(!pt&&(kind==='family'||kind==='block'||kind==='note')){",
    "    if(!pt&&(kind==='family'||kind==='block'||kind==='note'||kind==='asset')){")

# ---- Properties ----
rep("    h+=bimPropGroup('Constraints',cons);",
    "    h+=bimPropGroup('Constraints',cons);\n"
    "    if(o.asset&&o.asset.k)h+=bimEntPropsHtml(o);   /* __acad3dV169: the asset's sizes and their standards */")
rep("      if(f==='name'){\n        pushUndo();",
    "      if(f.indexOf('asset:')===0&&o.asset){bimEntPropSet(o,f.slice(6),inp.value,inp.checked);return;}   /* __acad3dV169 */\n"
    "      if(f==='name'){\n        pushUndo();")

# ---- the sun studies: a bare deciduous tree casts its trunk only ----
rep("  function bimShadowCasters(g){", "  function bimShadowCasters(g,date){   /* __acad3dV169: the date, for the trees' leaves */")
rep("      out.push({id:o.id,w:w,f:o.mesh.f});",
    "      out.push({id:o.id,w:w,f:bimEntBare(o,date)?o.mesh.f.slice(0,o.asset.cf):o.mesh.f});")
rep("var date=o.date||st.date,step=o.step||15,g=bimShadowGround(),list=bimShadowCasters(g),i,j,k;",
    "var date=o.date||st.date,step=o.step||15,g=bimShadowGround(),list=bimShadowCasters(g,date),i,j,k;")
rep("  function bimDgCasters(gr,c,r){\n    return bimShadowCasters(gr).filter(function(it){",
    "  function bimDgCasters(gr,c,r,date){\n    return bimShadowCasters(gr,date).filter(function(it){")
rep("    var sv=bimSunVector(sun),gr=bimShadowGround(),list=bimDgCasters(gr,L.c||[0,0],L.r||200);",
    "    var sv=bimSunVector(sun),gr=bimShadowGround(),list=bimDgCasters(gr,L.c||[0,0],L.r||200,L.date);")

# ---- the plan: the turning spaces ----
rep("    if(!capMode)drawSimOverlays(ctx,V,W,H);  /* __acad3dV143: sun hours, ponds and flow lines */",
    "    if(!capMode)drawSimOverlays(ctx,V,W,H);  /* __acad3dV143: sun hours, ponds and flow lines */\n"
    "    if(!capMode)bimEntDrawTurns(ctx,V,W,H);  /* __acad3dV169: the turning spaces of placed assets */")

# ---- V157's tree mesh, now bimEntTreeMesh's: gone ----
TREE157 = '  /* a tree: a hexagonal trunk and a crown of 20 faces */\n  function bimTreeMesh(x,z,y,h,cd){\n    var v=[],f=[],i,r=Math.max(0.08,h*0.025),cr=Math.max(0.6,cd/2),cy=y+Math.max(h-cr,h*0.45),th=Math.max(0.5,cy-y);\n    for(i=0;i<6;i++){var a=i*Math.PI/3;v.push([x+r*Math.cos(a),y,z+r*Math.sin(a)]);}\n    for(i=0;i<6;i++){var a2=i*Math.PI/3;v.push([x+r*Math.cos(a2),y+th,z+r*Math.sin(a2)]);}\n    for(i=0;i<6;i++){var j=(i+1)%6;f.push([i,j,j+6,i+6]);}\n    var p=(1+Math.sqrt(5))/2,s=cr/Math.sqrt(1+p*p),b=v.length,\n      ico=[[-1,p,0],[1,p,0],[-1,-p,0],[1,-p,0],[0,-1,p],[0,1,p],[0,-1,-p],[0,1,-p],[p,0,-1],[p,0,1],[-p,0,-1],[-p,0,1]],\n      tri=[[0,11,5],[0,5,1],[0,1,7],[0,7,10],[0,10,11],[1,5,9],[5,11,4],[11,10,2],[10,7,6],[7,1,8],[3,9,4],[3,4,2],[3,2,6],[3,6,8],[3,8,9],[4,9,5],[2,4,11],[6,2,10],[8,6,7],[9,8,1]];\n    for(i=0;i<12;i++)v.push([x+ico[i][0]*s,cy+ico[i][1]*s,z+ico[i][2]*s]);\n    for(i=0;i<20;i++)f.push([b+tri[i][0],b+tri[i][1],b+tri[i][2]]);\n    return {v:v,f:f};\n  }\n'
rep(TREE157, "")

# ---- the context's trees: by leaf type ----
rep("th2=bimTagMetres(f.tags.height)||bimCtxTreeH(),cd2=bimTagMetres(f.tags.diameter_crown)||th2*0.6;",
    "th2=bimTagMetres(f.tags.height)||bimCtxTreeH(),cd2=bimTagMetres(f.tags.diameter_crown)||th2*bimEntCrownRatio(f.tags),lf2=bimEntLeafOf(f.tags);   /* __acad3dV169: the crown by leaf type */")
rep("            o.context.height=th2;o.context.crown=Math.round(cd2*100)/100;",
    "            o.context.height=th2;o.context.crown=Math.round(cd2*100)/100;o.context.leaf=lf2;")
rep("            o.mesh=bimTreeMesh(tp[j][0],tp[j][1],gy,th2,cd2);o.col=BIM_CTX_COL.trees;",
    "            o.mesh=bimEntTreeMesh(tp[j][0],tp[j][1],gy,th2,cd2,lf2.type==='C').mesh;o.col=BIM_CTX_COL.trees;   /* __acad3dV169: a conifer a cone */")
rep("    if((c.kind==='trees'||c.kind==='power')&&c.height)r+=bimPropText('Height'",
    "    if(c.kind==='trees'&&c.leaf&&(c.leaf.type||c.leaf.cyc))r+=bimPropText('Leaf',(c.leaf.type==='C'?'needle-leaved':(c.leaf.type==='B'?'broadleaved':'its leaf type not mapped'))+', '+(c.leaf.cyc==='E'?'evergreen':(c.leaf.cyc==='D'?'deciduous':'its leaf cycle not mapped')));   /* __acad3dV169 */\n"
    "    if((c.kind==='trees'||c.kind==='power')&&c.height)r+=bimPropText('Height'")

out = s.encode('utf-8')
na0 = sum(1 for c in raw.decode('utf-8') if ord(c) > 127)
na1 = sum(1 for c in s if ord(c) > 127)
if na1 > na0:
    sys.exit('the patch added %d non-ASCII characters' % (na1 - na0))
SRC.write_bytes(out)
print('bytes', before, '->', len(out))
print('sha256', hashlib.sha256(out).hexdigest())
