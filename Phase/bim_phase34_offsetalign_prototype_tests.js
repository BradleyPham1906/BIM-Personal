function bimSegNormal(a,b){
  var dx=b[0]-a[0],dz=b[1]-a[1],len=Math.sqrt(dx*dx+dz*dz)||1;
  return [-dz/len,dx/len];
}
function bimOffsetRing(pts,dist,closed){
  var n=pts.length,out=[],i;
  for(i=0;i<n;i++){
    if(!closed&&(i===0||i===n-1)){
      var a=i===0?pts[0]:pts[n-2],b=i===0?pts[1]:pts[n-1];
      var nrm=bimSegNormal(a,b);
      out.push([pts[i][0]+nrm[0]*dist,pts[i][1]+nrm[1]*dist]);
      continue;
    }
    var prev=pts[(i-1+n)%n],cur=pts[i],next=pts[(i+1)%n];
    var n1=bimSegNormal(prev,cur),n2=bimSegNormal(cur,next);
    var mx=n1[0]+n2[0],mz=n1[1]+n2[1];
    var mlen=Math.sqrt(mx*mx+mz*mz)||1;mx/=mlen;mz/=mlen;
    var cosH=(n1[0]*mx+n1[1]*mz);
    var scale=cosH>0.15?1/cosH:1;scale=Math.min(scale,4);
    out.push([cur[0]+mx*dist*scale,cur[1]+mz*dist*scale]);
  }
  return out;
}

// ---- OFFSET ----
function bimOffsetPoints(pts,dist,closed){
  if(!pts||pts.length<2)return null;
  if(Math.abs(dist)<1e-9)return null;
  return bimOffsetRing(pts,dist,!!closed);
}

// ---- ALIGN ----
// Aligns objects to a reference along one axis. Revit's Align picks a reference line then
// snaps things to it; this is the axis-aligned form, which is what's useful in plan.
function bimAlignValue(refObj,axis,edge){
  var b=refObj.bounds; // {minX,maxX,minZ,maxZ}
  if(axis==='x')return edge==='min'?b.minX:(edge==='max'?b.maxX:(b.minX+b.maxX)/2);
  return edge==='min'?b.minZ:(edge==='max'?b.maxZ:(b.minZ+b.maxZ)/2);
}
function bimAlignDelta(obj,target,axis,edge){
  var b=obj.bounds;
  var cur=(axis==='x')
    ? (edge==='min'?b.minX:(edge==='max'?b.maxX:(b.minX+b.maxX)/2))
    : (edge==='min'?b.minZ:(edge==='max'?b.maxZ:(b.minZ+b.maxZ)/2));
  return target-cur;
}

var PASS=0,FAIL=0;
function assert(n,c,d){if(c){PASS++;console.log('PASS  '+n);}else{FAIL++;console.log('FAIL  '+n+(d?' -- '+d:''));}}
function approx(a,b,e){return Math.abs(a-b)<(e||1e-6);}

// ---- Offset: straight line ----
var line=[[0,0],[10,0]];
var off=bimOffsetPoints(line,2,false);
assert('offsetting a horizontal line moves it perpendicular by the distance', approx(off[0][1],2)&&approx(off[1][1],2), JSON.stringify(off));
assert('offset preserves the line length', approx(off[1][0]-off[0][0],10));
var offNeg=bimOffsetPoints(line,-2,false);
assert('negative distance offsets to the opposite side', approx(offNeg[0][1],-2));

// ---- Offset: L-shape keeps a proper mitered corner ----
var L=[[0,0],[10,0],[10,10]];
var offL=bimOffsetPoints(L,1,false);
assert('L-shape offset produces the same point count', offL.length===3);
// mitered inner corner should sit at distance 1*sqrt(2) diagonally from the original corner
var d=Math.sqrt(Math.pow(offL[1][0]-10,2)+Math.pow(offL[1][1]-0,2));
assert('L-shape corner is mitered, not just perpendicular-shifted', approx(d,Math.SQRT2,1e-6), 'corner dist='+d);

// ---- Offset: closed rectangle shrinks/grows uniformly ----
var rect=[[0,0],[10,0],[10,6],[0,6]];
// NOTE ON SIGN: for a CCW-wound ring, bimSegNormal points INTO the shape, so a POSITIVE
// distance offsets inward and a negative one outward. Asserting the real convention rather
// than assuming; the UI exposes this as a signed distance with the direction spelled out.
var offIn=bimOffsetPoints(rect,1,true);
var xs=offIn.map(function(p){return p[0];}),zs=offIn.map(function(p){return p[1];});
assert('closed rect: POSITIVE offset shrinks inward (CCW normals point inward)',
  approx(Math.min.apply(null,xs),1)&&approx(Math.max.apply(null,xs),9)&&
  approx(Math.min.apply(null,zs),1)&&approx(Math.max.apply(null,zs),5),
  JSON.stringify([Math.min.apply(null,xs),Math.max.apply(null,xs),Math.min.apply(null,zs),Math.max.apply(null,zs)]));
var offOut=bimOffsetPoints(rect,-1,true);
var oxs=offOut.map(function(p){return p[0];});
assert('closed rect: NEGATIVE offset grows outward', approx(Math.min.apply(null,oxs),-1)&&approx(Math.max.apply(null,oxs),11));

// ---- Offset: rejections ----
assert('zero offset distance is rejected (would just duplicate in place)', bimOffsetPoints(line,0,false)===null);
assert('a single point cannot be offset', bimOffsetPoints([[0,0]],2,false)===null);
assert('null input is handled', bimOffsetPoints(null,2,false)===null);

// ---- Align ----
var ref={bounds:{minX:0,maxX:4,minZ:0,maxZ:4}};
var mover={bounds:{minX:10,maxX:12,minZ:7,maxZ:9}};
assert('align-left target is the reference min X', approx(bimAlignValue(ref,'x','min'),0));
assert('align-right target is the reference max X', approx(bimAlignValue(ref,'x','max'),4));
assert('align-center target is the reference X midpoint', approx(bimAlignValue(ref,'x','center'),2));

var dLeft=bimAlignDelta(mover,bimAlignValue(ref,'x','min'),'x','min');
assert('aligning left moves the object so its min X meets the reference min X', approx(dLeft,-10), dLeft);
var dRight=bimAlignDelta(mover,bimAlignValue(ref,'x','max'),'x','max');
assert('aligning right moves the object so its max X meets the reference max X', approx(dRight,-8), dRight);
var dCz=bimAlignDelta(mover,bimAlignValue(ref,'z','center'),'z','center');
assert('aligning centre on Z uses midpoints, not edges', approx(dCz,-6), dCz);
var dSelf=bimAlignDelta(ref,bimAlignValue(ref,'x','min'),'x','min');
assert('aligning the reference to itself is a no-op', approx(dSelf,0));

console.log('');console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
