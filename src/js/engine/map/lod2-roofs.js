  /* ================= __acad3dV140: LOD2 roofs from OpenStreetMap's tags =================
     OSM's Simple 3D Buildings: roof:shape, roof:height, roof:levels, roof:angle, roof:direction,
     roof:orientation. Each roof is planes: Phase 39's straight skeleton for hipped roofs, and for the
     others on a convex footprint the lowest of a set of planes -- each plane keeps the part of the
     footprint where it is lowest, so ridges, hips and knees are exact intersections. */
  var BIM_ROOF_SHAPES={flat:1,gabled:1,hipped:1,pyramidal:1,skillion:1,'half-hipped':1,gambrel:1,mansard:1};
  var BIM_ROOF_CURVED={dome:1,onion:1,round:1,cone:1,saltbox:1,crosspitched:1,sawtooth:1,butterfly:1,'side_hipped':1,'side_half-hipped':1};
  var BIM_ROOF_ANGLE=30,BIM_ROOF_KNEE={x:0.3,y:0.7},BIM_ROOF_HALFHIP=0.6,BIM_ROOF_MINWALL=0.5;
  var BIM_COMPASS={N:0,NNE:22.5,NE:45,ENE:67.5,E:90,ESE:112.5,SE:135,SSE:157.5,S:180,SSW:202.5,SW:225,WSW:247.5,W:270,WNW:292.5,NW:315,NNW:337.5};
  /* a compass direction (degrees, or N, SSW...) as a model plan unit vector; null when it does not read */
  function bimRoofDir(s){
    s=String(s==null?'':s).replace(/^\s+|\s+$/g,'').toUpperCase();
    if(!s)return null;
    var az=BIM_COMPASS.hasOwnProperty(s)?BIM_COMPASS[s]:(/^-?[0-9]*\.?[0-9]+$/.test(s)?parseFloat(s):NaN);
    if(!isFinite(az))return null;
    var r=(az+bimTrueNorthDeg())*BIM_D2R;
    return [Math.sin(r),-Math.cos(r)];
  }
  /* the footprint's smallest bounding rectangle: u along its long side, v across */
  function bimRoofOBB(P){
    var best=null,i,j,k;
    for(i=0;i<P.length;i++){
      j=(i+1)%P.length;
      var d=bimSkNorm(bimSkSub(P[j],P[i]));
      if(bimSkLen(d)<0.5)continue;
      var n=[-d[1],d[0]],u0=Infinity,u1=-Infinity,v0=Infinity,v1=-Infinity;
      for(k=0;k<P.length;k++){var a=bimSkDot(P[k],d),b=bimSkDot(P[k],n);u0=Math.min(u0,a);u1=Math.max(u1,a);v0=Math.min(v0,b);v1=Math.max(v1,b);}
      var A=(u1-u0)*(v1-v0);
      if(!best||A<best.A-1e-9)best={A:A,u:d,v:n,u0:u0,u1:u1,v0:v0,v1:v1};
    }
    if(!best)return null;
    if(best.v1-best.v0>best.u1-best.u0+1e-9)best={A:best.A,u:best.v,v:[-best.u[0],-best.u[1]],u0:best.v0,u1:best.v1,v0:-best.u1,v1:-best.u0};
    best.L=best.u1-best.u0;best.W=best.v1-best.v0;
    return best;
  }
  /* the extent of P along a unit vector */
  function bimRoofSpan(P,d){
    var lo=Infinity,hi=-Infinity,k;
    for(k=0;k<P.length;k++){var s=bimSkDot(P[k],d);lo=Math.min(lo,s);hi=Math.max(hi,s);}
    return {lo:lo,hi:hi};
  }
  function bimRoofConvex(P){
    var i,n=P.length;
    for(i=0;i<n;i++){
      var a=P[i],b=P[(i+1)%n],c=P[(i+2)%n];
      if(bimSkCross(bimSkSub(b,a),bimSkSub(c,b))<-1e-9*(1+bimSkLen(bimSkSub(b,a))*bimSkLen(bimSkSub(c,b))))return false;
    }
    return true;
  }
  /* a plane h = a x + b z + c rising at slope k along unit d, from height m where p.d = o */
  function bimRoofPlane(d,o,k,m){return {a:k*d[0],b:k*d[1],c:m-k*o};}
  function bimRoofH(pl,p){return pl.a*p[0]+pl.b*p[1]+pl.c;}
  /* keep the part of convex polygon Q where a x + b z + c <= 0 */
  function bimRoofClip(Q,a,b,c){
    var out=[],i,n=Q.length;
    for(i=0;i<n;i++){
      var p=Q[i],q=Q[(i+1)%n],fp=a*p[0]+b*p[1]+c,fq=a*q[0]+b*q[1]+c;
      if(fp<=1e-12)out.push(p);
      if((fp<-1e-12&&fq>1e-12)||(fp>1e-12&&fq<-1e-12)){var s=fp/(fp-fq);out.push([p[0]+(q[0]-p[0])*s,p[1]+(q[1]-p[1])*s]);}
    }
    return out;
  }
  /* the lower envelope of planes over convex P: each plane's region, counter-clockwise */
  function bimRoofEnvelope(P,planes){
    var U=[],i,j,R=[];
    for(i=0;i<planes.length;i++){
      var dup=false;
      for(j=0;j<U.length;j++)if(Math.abs(U[j].a-planes[i].a)<1e-9&&Math.abs(U[j].b-planes[i].b)<1e-9&&Math.abs(U[j].c-planes[i].c)<1e-9)dup=true;
      if(!dup)U.push(planes[i]);
    }
    for(i=0;i<U.length;i++){
      var Q=P.slice();
      for(j=0;j<U.length&&Q.length>=3;j++){
        if(j===i)continue;
        Q=bimRoofClip(Q,U[i].a-U[j].a,U[i].b-U[j].b,U[i].c-U[j].c);
      }
      var C=[];
      for(j=0;j<Q.length;j++)if(!C.length||bimSkDist(C[C.length-1],Q[j])>1e-7)C.push(Q[j]);
      while(C.length>1&&bimSkDist(C[0],C[C.length-1])<1e-7)C.pop();
      if(C.length>=3&&Math.abs(bimSkShoelace(C))>1e-6)R.push({plane:U[i],poly:C});
    }
    return R;
  }
  /* the roof's height: roof:height, else roof:levels, else roof:angle over the half-width, else assumed */
  function bimRoofHeight(t,shape,half){
    var v=bimOsmMetres(t['roof:height']),L=parseFloat(t['roof:levels']),ang=parseFloat(t['roof:angle']);
    if(shape==='flat')return {h:0,from:'flat'};
    if(v!==null&&v>0&&v<200)return {h:v,from:'roof:height'};
    if(isFinite(L)&&L>0&&L<50)return {h:L*bimCtxLevelH(),from:'roof:levels'};
    if(isFinite(ang)&&ang>0&&ang<85)return {h:Math.tan(ang*BIM_D2R)*half,from:'roof:angle',angle:ang};
    return {h:Math.tan(BIM_ROOF_ANGLE*BIM_D2R)*half,from:'assumed',angle:BIM_ROOF_ANGLE};
  }
  /* the building's solid: ground, walls up to the roof's edge, and the roof faces (each a list of
     [x,y,z], counter-clockwise seen from above) */
  function bimRoofSolid(P,base,roofs){
    var v=[],vm={},f=[],i,j;
    function vid(p){var k=p[0].toFixed(6)+'|'+p[1].toFixed(6)+'|'+p[2].toFixed(6);if(vm[k]===undefined){vm[k]=v.length;v.push([p[0],p[1],p[2]]);}return vm[k];}
    function face(ids){bimCjFaceSplit(ids,v).forEach(function(ff){f.push(ff);});}
    var n=P.length;
    face(P.map(function(p){return vid([p[0],base,p[1]]);}));
    var tops=[];
    roofs.forEach(function(r){tops=tops.concat(r);});
    for(i=0;i<n;i++){
      var a=P[i],b=P[(i+1)%n],d=bimSkSub(b,a),L2=bimSkDot(d,d),on=[];
      for(j=0;j<tops.length;j++){
        var q=[tops[j][0],tops[j][2]],s=bimSkDot(bimSkSub(q,a),d)/L2;
        if(s<-1e-9||s>1+1e-9)continue;
        var e=[a[0]+d[0]*s-q[0],a[1]+d[1]*s-q[1]];
        if(e[0]*e[0]+e[1]*e[1]>1e-10)continue;
        on.push({s:s,p:tops[j]});
      }
      on.sort(function(x,y){return x.s-y.s;});
      var prof=[];
      for(j=0;j<on.length;j++){var k2=vid(on[j].p);if(!prof.length||prof[prof.length-1]!==k2)prof.push(k2);}
      face([vid([b[0],base,b[1]]),vid([a[0],base,a[1]])].concat(prof));
    }
    roofs.forEach(function(r){face(r.slice().reverse().map(vid));});
    return {v:v,f:f};
  }
  /* "; 3 roofs (2 gabled, 1 hipped); 1 roof shape not built (dome)" */
  function bimRoofCountText(R,N){
    function list(o){return Object.keys(o).sort().map(function(k){return o[k]+' '+k;}).join(', ');}
    var nr=0,nn=0,k;
    for(k in R)if(R.hasOwnProperty(k))nr+=R[k];
    for(k in N)if(N.hasOwnProperty(k))nn+=N[k];
    return (nr?'; '+nr+' LOD2 roof'+(nr===1?'':'s')+' ('+list(R)+')':'')+(nn?'; '+nn+' roof'+(nn===1?'':'s')+' not built ('+list(N)+')':'');
  }
  /* the roof for a footprint (counter-clockwise), from base with body h (a height tag: the whole;
     levels: the walls); null for no roof:shape, {why} when it is not built */
  function bimOsmRoof(Pin,t,base,h,hFrom){
    t=t||{};
    var shape=String(t['roof:shape']||'').replace(/^\s+|\s+$/g,'').toLowerCase();
    if(!shape)return null;
    if(!BIM_ROOF_SHAPES[shape])return {shape:shape,why:BIM_ROOF_CURVED[shape]?'a '+shape+' roof is curved or uneven and is not built yet':'roof:shape='+shape+' is not a shape this app knows'};
    var P=bimSkClean(Pin);
    if(!P||P.length<3)return {shape:shape,why:'the footprint is too small'};
    var ob=bimRoofOBB(P);
    if(!ob)return {shape:shape,why:'the footprint is too small'};
    var convex=bimRoofConvex(P),gab={gabled:1,'half-hipped':1,gambrel:1,skillion:1};
    if(!convex&&shape!=='hipped'&&shape!=='flat')return {shape:shape,why:'a '+shape+' roof needs a convex footprint (split the building into parts in OSM)'};
    var dir=bimRoofDir(t['roof:direction']),across=String(t['roof:orientation']||'').toLowerCase()==='across';
    var V=ob.v,U=ob.u,how='';
    if(gab[shape]&&shape!=='skillion'){
      if(dir){V=dir;U=[-dir[1],dir[0]];how='ridge across its roof:direction';}
      else if(across){V=ob.u;U=ob.v;how='ridge across the longest side (roof:orientation=across)';}
      else how='ridge along the longest side';
    }
    var sv=bimRoofSpan(P,V),su=bimRoofSpan(P,U),half=(sv.hi-sv.lo)/2;
    if(shape==='skillion'){
      if(dir){V=dir;how='sloping down to its roof:direction';}else how='sloping across the longest side (no roof:direction: assumed)';
      sv=bimRoofSpan(P,V);half=(sv.hi-sv.lo)/2;
    }
    var tmax=null;
    if(shape==='hipped'||shape==='mansard'||shape==='pyramidal'){
      if(convex){
        var unit=[];
        for(var e=0;e<P.length;e++){var a0=P[e],d0=bimSkNorm(bimSkSub(P[(e+1)%P.length],a0)),n0=[-d0[1],d0[0]];unit.push(bimRoofPlane(n0,bimSkDot(a0,n0),1,0));}
        tmax=0;
        bimRoofEnvelope(P,unit).forEach(function(r){r.poly.forEach(function(p){tmax=Math.max(tmax,bimRoofH(r.plane,p));});});
      }
      half=tmax!==null?tmax:half;
    }
    var rh=bimRoofHeight(t,shape,shape==='skillion'?2*half:half);
    var roofH=rh.h,clamped=false,eave,total;
    if(hFrom==='height'){total=h;eave=h-roofH;if(eave<BIM_ROOF_MINWALL){eave=Math.min(BIM_ROOF_MINWALL,h/2);roofH=h-eave;clamped=true;}}
    else{eave=h;total=h+roofH;}
    var B=base,E=base+eave,i,roofs=[],planes=[];
    if(shape==='flat'){
      roofs.push(P.map(function(p){return [p[0],E,p[1]];}));
    }else if(shape==='hipped'){
      var sk=bimSkelSolve(P);
      if(sk.error)return {shape:shape,why:'the hip solver could not roof this footprint: '+sk.error};
      var tm=0;
      sk.faces.forEach(function(fc){fc.pts.forEach(function(q){tm=Math.max(tm,q.t);});});
      if(tm<=1e-9)return {shape:shape,why:'the footprint has no width to roof'};
      var s=roofH/tm;
      sk.faces.forEach(function(fc){roofs.push(fc.pts.map(function(q){return [q.p[0],E+q.t*s,q.p[1]];}));});
      how='hips and ridges by the straight skeleton';
    }else if(shape==='pyramidal'){
      var ar=0,cx=0,cz=0;
      for(i=0;i<P.length;i++){var p1=P[i],p2=P[(i+1)%P.length],cr=p1[0]*p2[1]-p2[0]*p1[1];ar+=cr;cx+=(p1[0]+p2[0])*cr;cz+=(p1[1]+p2[1])*cr;}
      var apex=[cx/(3*ar),E+roofH,cz/(3*ar)];
      for(i=0;i<P.length;i++){var q1=P[i],q2=P[(i+1)%P.length];roofs.push([[q1[0],E,q1[1]],[q2[0],E,q2[1]],apex]);}
      how='to one apex over its centre';
    }else{
      var W2=half,s1,s2,kx=BIM_ROOF_KNEE.x,ky=BIM_ROOF_KNEE.y;
      if(shape==='skillion')planes.push(bimRoofPlane([-V[0],-V[1]],-sv.hi,roofH/(sv.hi-sv.lo),E));
      else if(shape==='gabled'||shape==='half-hipped'){
        s1=roofH/W2;
        planes.push(bimRoofPlane(V,sv.lo,s1,E),bimRoofPlane([-V[0],-V[1]],-sv.hi,s1,E));
        if(shape==='half-hipped'){
          planes.push(bimRoofPlane(U,su.lo,s1,E+BIM_ROOF_HALFHIP*roofH),bimRoofPlane([-U[0],-U[1]],-su.hi,s1,E+BIM_ROOF_HALFHIP*roofH));
          how+='; hipped above '+Math.round(BIM_ROOF_HALFHIP*100)+'% of the roof height';
        }
      }else if(shape==='gambrel'){
        s1=ky*roofH/(kx*W2);s2=(1-ky)*roofH/((1-kx)*W2);
        planes.push(bimRoofPlane(V,sv.lo,s1,E),bimRoofPlane([-V[0],-V[1]],-sv.hi,s1,E),
          bimRoofPlane(V,sv.lo+kx*W2,s2,E+ky*roofH),bimRoofPlane([-V[0],-V[1]],-sv.hi+kx*W2,s2,E+ky*roofH));
        how+='; the knee at '+Math.round(ky*100)+'% of the roof height';
      }else if(shape==='mansard'){
        s1=ky*roofH/(kx*W2);s2=(1-ky)*roofH/((1-kx)*W2);
        for(i=0;i<P.length;i++){
          var ea=P[i],ed=bimSkNorm(bimSkSub(P[(i+1)%P.length],ea)),en=[-ed[1],ed[0]],eo=bimSkDot(ea,en);
          planes.push(bimRoofPlane(en,eo,s1,E),bimRoofPlane(en,eo+kx*W2,s2,E+ky*roofH));
        }
        how='steep below a knee at '+Math.round(ky*100)+'% of the roof height, shallow above, on every side';
      }
      bimRoofEnvelope(P,planes).forEach(function(r){roofs.push(r.poly.map(function(p){return [p[0],bimRoofH(r.plane,p),p[1]];}));});
    }
    if(!roofs.length)return {shape:shape,why:'no roof faces came out'};
    var mesh=bimRoofSolid(P,B,roofs);
    var rt=-Infinity;
    mesh.v.forEach(function(p){rt=Math.max(rt,p[1]);});
    return {mesh:mesh,total:Math.round((rt-base)*1000)/1000,
      info:{shape:shape,height:Math.round(roofH*1000)/1000,from:rh.from,angle:rh.angle,eave:Math.round(eave*1000)/1000,
        how:how,clamped:clamped,faces:roofs.length}};
  }
