/* bim_phase89_fillet_prototype.js -- FILLET with a radius, on two straight wall centerlines.

   Proved before it reaches the build, because there are two independent sign traps: which end
   of each wall meets the corner, and which way the fillet arc turns. The V88 sign error cost a
   rebuild; this one would too.

   The arc core below is the V88 code verbatim (bim_phase88_bulge_prototype.js, 29/29). */
function bimCircleFrom3Points(p1,p2,p3){
  var ax=p1[0],ay=p1[1],bx=p2[0],by=p2[1],cx=p3[0],cy=p3[1];
  var d=2*(ax*(by-cy)+bx*(cy-ay)+cx*(ay-by));
  if(Math.abs(d)<1e-9)return null;
  var ux=((ax*ax+ay*ay)*(by-cy)+(bx*bx+by*by)*(cy-ay)+(cx*cx+cy*cy)*(ay-by))/d;
  var uy=((ax*ax+ay*ay)*(cx-bx)+(bx*bx+by*by)*(ax-cx)+(cx*cx+cy*cy)*(bx-ax))/d;
  return {center:[ux,uy],radius:Math.sqrt(Math.pow(ax-ux,2)+Math.pow(ay-uy,2))};
}
function bimLineLineIntersect(a1,a2,b1,b2){
  var d1x=a2[0]-a1[0],d1z=a2[1]-a1[1];
  var d2x=b2[0]-b1[0],d2z=b2[1]-b1[1];
  var denom=d1x*d2z-d1z*d2x;
  if(Math.abs(denom)<1e-9)return null;
  var dx=b1[0]-a1[0],dz=b1[1]-a1[1];
  var t=(dx*d2z-dz*d2x)/denom;
  return [a1[0]+d1x*t,a1[1]+d1z*t];
}
var BIM_BULGE_EPS=1e-9;
function bimBulgeArc(p1,p2,b){
  if(!p1||!p2||!isFinite(b)||Math.abs(b)<BIM_BULGE_EPS)return null;
  var dx=p2[0]-p1[0],dz=p2[1]-p1[1];
  var c=Math.sqrt(dx*dx+dz*dz);
  if(c<1e-12)return null;
  var ux=dx/c,uz=dz/c;
  var mx=uz,mz=-ux;
  var sag=b*c/2;
  var apex=[(p1[0]+p2[0])/2+mx*sag,(p1[1]+p2[1])/2+mz*sag];
  var cir=bimCircleFrom3Points(p1,apex,p2);
  if(!cir)return null;
  var sweep=4*Math.atan(b);
  var a1=Math.atan2(p1[1]-cir.center[1],p1[0]-cir.center[0]);
  return {center:cir.center,radius:cir.radius,a1:a1,a2:a1+sweep,sweep:sweep,apex:apex,chord:c};
}

/* ------------------------------------------------------------------ the fillet */
function bimSetEnd(cl,idx,pt){
  var out=cl.map(function(p){return [p[0],p[1]];});
  out[idx]=[pt[0],pt[1]];
  return out;
}
function bimFilletCorner(clA,closedA,clB,closedB,radius){
  if(closedA||closedB)return {error:'Fillet needs two open walls'};
  if(!clA||clA.length<2||!clB||clB.length<2)return {error:'Both walls need a usable centerline'};
  if(!isFinite(radius)||radius<0)return {error:'Fillet radius must be zero or greater'};
  var endsA=[0,clA.length-1],endsB=[0,clB.length-1],best=null,ia,ib;
  for(ia=0;ia<2;ia++)for(ib=0;ib<2;ib++){
    var pa=clA[endsA[ia]],pb=clB[endsB[ib]];
    var d=(pa[0]-pb[0])*(pa[0]-pb[0])+(pa[1]-pb[1])*(pa[1]-pb[1]);
    if(!best||d<best.d)best={d:d,ai:endsA[ia],bi:endsB[ib]};
  }
  var aNb=best.ai===0?1:clA.length-2,bNb=best.bi===0?1:clB.length-2;
  var ip=bimLineLineIntersect(clA[aNb],clA[best.ai],clB[bNb],clB[best.bi]);
  if(!ip)return {error:'Those two walls are parallel - there is no corner to fillet'};
  function unitFrom(corner,to){
    var vx=to[0]-corner[0],vz=to[1]-corner[1],L=Math.sqrt(vx*vx+vz*vz);
    if(L<1e-9)return null;
    return {u:[vx/L,vz/L],len:L};
  }
  var ra=unitFrom(ip,clA[aNb]),rb=unitFrom(ip,clB[bNb]);
  if(!ra||!rb)return {error:'A wall has zero length at the corner'};
  var dot=Math.max(-1,Math.min(1,ra.u[0]*rb.u[0]+ra.u[1]*rb.u[1]));
  var theta=Math.acos(dot);
  if(theta<1e-6||Math.PI-theta<1e-6)
    return {error:'Those walls are colinear at the corner - there is no angle to fillet'};
  if(radius<1e-9){
    return {a:bimSetEnd(clA,best.ai,ip),b:bimSetEnd(clB,best.bi,ip),corner:ip,radius:0,fillet:null};
  }
  var t=radius/Math.tan(theta/2);
  if(t>=ra.len)return {error:'Radius is too large for the first wall ('+ra.len.toFixed(3)+' m available)'};
  if(t>=rb.len)return {error:'Radius is too large for the second wall ('+rb.len.toFixed(3)+' m available)'};
  var tangA=[ip[0]+ra.u[0]*t,ip[1]+ra.u[1]*t];
  var tangB=[ip[0]+rb.u[0]*t,ip[1]+rb.u[1]*t];
  /* Travel goes INTO the corner along -ra.u and OUT along +rb.u, so the fillet turns by
     (pi - theta) in the direction of that turn. Taking the sign from ra.u and rb.u directly
     would be backwards for one of them. */
  var inDir=[-ra.u[0],-ra.u[1]],outDir=rb.u;
  var cross=inDir[0]*outDir[1]-inDir[1]*outDir[0];
  var sweep=(cross>=0?1:-1)*(Math.PI-theta);
  return {a:bimSetEnd(clA,best.ai,tangA),b:bimSetEnd(clB,best.bi,tangB),
          fillet:{pts:[tangA,tangB],bulges:[Math.tan(sweep/4),0]},
          corner:ip,radius:radius,tangent:t,sweep:sweep};
}

/* ------------------------------------------------------------------ checks */
var n=0,bad=[];
function ck(c,m){n++;console.log((c?'  PASS  ':'  FAIL  ')+m);if(!c)bad.push(m);}
function near(a,b,t){return Math.abs(a-b)<=(t||1e-9);}
/* TANGENCY is what makes it a fillet rather than a nearby arc: at each tangent point the
   radius must be square to the wall. */
function tangentOk(arc,tang,wallDir){
  var rx=tang[0]-arc.center[0],rz=tang[1]-arc.center[1];
  var L=Math.sqrt(rx*rx+rz*rz);
  return Math.abs((rx/L)*wallDir[0]+(rz/L)*wallDir[1])<1e-9;
}

var r=bimFilletCorner([[0,0],[10,0]],false,[[10,0],[10,10]],false,2);
ck(!r.error,'a right-angle fillet is computed ('+(r.error||'ok')+')');
ck(near(r.tangent,2),'tangent distance for a 90deg corner equals the radius -> '+r.tangent);
ck(near(r.a[1][0],8)&&near(r.a[1][1],0),'wall A is cut back to (8,0) -> '+r.a[1]);
ck(near(r.b[0][0],10)&&near(r.b[0][1],2),'wall B is cut back to (10,2) -> '+r.b[0]);
var farc=bimBulgeArc(r.fillet.pts[0],r.fillet.pts[1],r.fillet.bulges[0]);
ck(near(farc.radius,2,1e-9),'the fillet arc really has the requested radius -> '+farc.radius);
ck(near(farc.center[0],8,1e-9)&&near(farc.center[1],2,1e-9),
   'centred where the two offsets meet, (8,2) -> '+farc.center);
ck(near(Math.abs(farc.sweep),Math.PI/2,1e-9),'sweeping 90 degrees -> '+(farc.sweep*180/Math.PI).toFixed(4));
ck(tangentOk(farc,r.fillet.pts[0],[1,0]),'the arc is TANGENT to wall A where it meets it');
ck(tangentOk(farc,r.fillet.pts[1],[0,1]),'and tangent to wall B where it meets it');

var r2=bimFilletCorner([[10,0],[0,0]],false,[[10,10],[10,0]],false,2);
var f2=bimBulgeArc(r2.fillet.pts[0],r2.fillet.pts[1],r2.fillet.bulges[0]);
ck(!r2.error&&near(f2.radius,2,1e-9)&&near(f2.center[0],8,1e-9)&&near(f2.center[1],2,1e-9),
   'the same corner with both walls reversed fillets identically -> c='+f2.center);

var rm=bimFilletCorner([[0,0],[10,0]],false,[[10,0],[10,-10]],false,2);
var fm=bimBulgeArc(rm.fillet.pts[0],rm.fillet.pts[1],rm.fillet.bulges[0]);
ck(near(fm.center[0],8,1e-9)&&near(fm.center[1],-2,1e-9),
   'a corner turning the other way centres at (8,-2) -> '+fm.center);
ck((r.fillet.bulges[0]>0)!==(rm.fillet.bulges[0]>0),
   'and its bulge has the opposite sign ('+r.fillet.bulges[0].toFixed(5)+' vs '+rm.fillet.bulges[0].toFixed(5)+')');

var r45=bimFilletCorner([[0,0],[10,0]],false,[[10,0],[17.07106781186548,7.07106781186548]],false,1.5);
var f45=bimBulgeArc(r45.fillet.pts[0],r45.fillet.pts[1],r45.fillet.bulges[0]);
ck(!r45.error&&near(f45.radius,1.5,1e-6),'a 135deg corner fillets to the requested radius -> '+f45.radius);
ck(tangentOk(f45,r45.fillet.pts[0],[1,0]),'and is still tangent to wall A');

ck(!!bimFilletCorner([[0,0],[10,0]],false,[[0,5],[10,5]],false,1).error,'parallel walls are refused');
ck(!!bimFilletCorner([[0,0],[10,0]],false,[[10,0],[20,0]],false,1).error,'colinear walls are refused');
ck(!!bimFilletCorner([[0,0],[10,0]],false,[[10,0],[10,10]],false,40).error,'a radius bigger than the walls is refused');
var r0=bimFilletCorner([[0,0],[8,0]],false,[[10,2],[10,10]],false,0);
ck(!r0.error&&r0.fillet===null&&near(r0.a[1][0],10)&&near(r0.a[1][1],0),
   'radius 0 is the square corner: both ends meet at (10,0), no arc -> '+r0.a[1]);

console.log('\n'+(n-bad.length)+'/'+n+' checks passed');
console.log('RESULT: '+(bad.length?'FAIL':'PASS'));
process.exit(bad.length?1:0);
