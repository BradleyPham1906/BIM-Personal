"""patch_phase145a.py -- V145: the grading engine.

- Daylight slopes: from every part of a pad's edge a slope runs out, up at the pad's cut slope
  where the ground is above it, down at its fill slope where it is below, until it meets the
  ground. Measured square to the nearest edge, it fans round an outside corner and meets itself
  in a valley at an inside one.
- The proposed surface: the existing points outside the daylight lines, the pads and their slopes,
  held by breaklines (V144); updated in place when graded again.
- Cut and fill between any two surfaces, exactly: every pair of overlapping triangles clipped to
  each other, the difference of their planes integrated over the pieces.
- Cut and fill bands; spot elevations; slope arrows' data; a bucket index for heights."""
NAME = 'patch_phase145a.py'
BASE = '79f1439d8351ea4c3669f44fdd1fb975567b39d404eb6cc28d6f96adec6b1353'
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def esc(s):
    return ''.join(ch if ord(ch) < 128 else '\\u%04x' % ord(ch) for ch in s)


def rep(old, new, n=1):
    global t
    new = esc(new)
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: %d occurrences, expected %d: %r' % (c, n, old[:90]))
    t = t.replace(old, new)


ENGINE = r"""  /* ================= __acad3dV145: grading =================
     A pad -- a closed outline with a Pad Elevation -- graded onto the existing surface. From every
     part of its edge a slope runs out: up at the pad's cut slope where the ground is above the pad,
     down at its fill slope where it is below, until it meets the ground (the daylight line). The
     slope is measured square to the pad's nearest edge, so it fans round an outside corner and
     meets itself in a valley at an inside one: the proposed ground is the existing ground held
     between Z - d/fill and Z + d/cut, d the distance to the pad. The proposed surface is the
     existing points outside the daylight lines, the pads and their slopes, held by breaklines. */
  var BIM_GRADE={step:2,fanDeg:15,march:0.25,reach:500,cut:2,fill:2};
  /* a TIN's triangles in a bucket grid: heights and overlaps without scanning every triangle */
  function bimTinIndex(tin){
    var x0=Infinity,z0=Infinity,x1=-Infinity,z1=-Infinity,i,t,n=tin.tris.length,p;
    for(i=0;i<tin.P.length;i++){p=tin.P[i];if(p[0]<x0)x0=p[0];if(p[0]>x1)x1=p[0];if(p[1]<z0)z0=p[1];if(p[1]>z1)z1=p[1];}
    if(!(x1>=x0)){x0=z0=0;x1=z1=1;}
    var cs=Math.max(Math.sqrt(Math.max((x1-x0)*(z1-z0),1e-6)/Math.max(n,1))*1.5,1e-3);
    var nx=Math.max(1,Math.ceil((x1-x0)/cs)+1),nz=Math.max(1,Math.ceil((z1-z0)/cs)+1),G=[],seen=[],stamp=0;
    function cx(x){return Math.max(0,Math.min(nx-1,Math.floor((x-x0)/cs)));}
    function cz(z){return Math.max(0,Math.min(nz-1,Math.floor((z-z0)/cs)));}
    for(t=0;t<n;t++){
      var tr=tin.tris[t],A=tin.P[tr[0]],B=tin.P[tr[1]],C=tin.P[tr[2]],a,b,k;
      var ax=cx(Math.min(A[0],B[0],C[0])),bx=cx(Math.max(A[0],B[0],C[0])),az=cz(Math.min(A[1],B[1],C[1])),bz=cz(Math.max(A[1],B[1],C[1]));
      for(a=ax;a<=bx;a++)for(b=az;b<=bz;b++){k=b*nx+a;(G[k]||(G[k]=[])).push(t);}
      seen.push(0);
    }
    function at(x,z){
      if(!(x>=x0-1e-9&&x<=x1+1e-9&&z>=z0-1e-9&&z<=z1+1e-9))return null;
      var L=G[cz(z)*nx+cx(x)]||[],j,P=tin.P,H=tin.H;
      for(j=0;j<L.length;j++){
        var tr=tin.tris[L[j]],A=P[tr[0]],B=P[tr[1]],C=P[tr[2]];
        var det=(B[0]-A[0])*(C[1]-A[1])-(C[0]-A[0])*(B[1]-A[1]);
        if(!(Math.abs(det)>1e-18))continue;
        var l1=((x-A[0])*(C[1]-A[1])-(C[0]-A[0])*(z-A[1]))/det,l2=((B[0]-A[0])*(z-A[1])-(x-A[0])*(B[1]-A[1]))/det;
        if(l1>=-1e-9&&l2>=-1e-9&&l1+l2<=1+1e-9)return H[tr[0]]+l1*(H[tr[1]]-H[tr[0]])+l2*(H[tr[2]]-H[tr[0]]);
      }
      return null;
    }
    function near(ax_,az_,bx_,bz_){
      var out=[],a,b,j,L;stamp++;
      for(a=cx(ax_);a<=cx(bx_);a++)for(b=cz(az_);b<=cz(bz_);b++){L=G[b*nx+a];if(!L)continue;for(j=0;j<L.length;j++)if(seen[L[j]]!==stamp){seen[L[j]]=stamp;out.push(L[j]);}}
      return out;
    }
    return {tin:tin,at:at,near:near};
  }
  var BIM_TIN_INDEX={};
  function bimTinIndexOf(o){
    var tin=bimTerrainTin(o),c=BIM_TIN_CACHE[o.id],key=(c?c.key:'')+'|'+JSON.stringify(bimObjOffset(o)),e=BIM_TIN_INDEX[o.id];
    if(!e||e.key!==key||e.idx.tin.P.length!==tin.P.length)e=BIM_TIN_INDEX[o.id]={key:key,idx:bimTinIndex(tin)};
    return e.idx;
  }
  function bimSegDist(p,a,b){
    var dx=b[0]-a[0],dz=b[1]-a[1],L2=dx*dx+dz*dz,u=L2>0?((p[0]-a[0])*dx+(p[1]-a[1])*dz)/L2:0;
    u=Math.max(0,Math.min(1,u));
    var ex=a[0]+dx*u-p[0],ez=a[1]+dz*u-p[1];
    return Math.sqrt(ex*ex+ez*ez);
  }
  function bimPolyDist(p,P){var d=Infinity,i;for(i=0;i<P.length;i++)d=Math.min(d,bimSegDist(p,P[i],P[(i+1)%P.length]));return d;}
  function bimPolysTouch(A,B){
    var i,j;
    for(i=0;i<A.length;i++)if(bimPointInPoly(A[i],B))return true;
    for(i=0;i<B.length;i++)if(bimPointInPoly(B[i],A))return true;
    for(i=0;i<A.length;i++)for(j=0;j<B.length;j++)if(bimSegCross(A[i],A[(i+1)%A.length],B[j],B[(j+1)%B.length]))return true;
    return false;
  }
  function bimLineTouchesPoly(L,P){
    var i,j;
    for(i=0;i<L.length;i++)if(bimPointInPoly(L[i],P))return true;
    for(i=0;i+1<L.length;i++)for(j=0;j<P.length;j++)if(bimSegCross(L[i],L[i+1],P[j],P[(j+1)%P.length]))return true;
    return false;
  }
  function bimIsPad(o){return !!(o&&o.t==='sketch'&&o.closed!==false&&!bimIsPoint(o)&&o.pts&&o.pts.length>=3&&isFinite(parseFloat(o.gradeElev)));}
  /* the pad's outline in world plan coordinates, counter-clockwise, without repeats */
  function bimPadWorld(o){
    var q=bimObjOffset(o),P=bimSketchOutline(o).map(function(p){return [p[0]+q[0],p[1]+q[2]];}),out=[],i,a,b;
    for(i=0;i<P.length;i++){a=P[i];b=out.length?out[out.length-1]:null;if(!b||Math.abs(a[0]-b[0])+Math.abs(a[1]-b[1])>1e-9)out.push(a);}
    if(out.length>2&&Math.abs(out[0][0]-out[out.length-1][0])+Math.abs(out[0][1]-out[out.length-1][1])<=1e-9)out.pop();
    return sketchCCW(out);
  }
  function bimPadSlopes(o){
    var c=parseFloat(o.cutSlope),f=parseFloat(o.fillSlope);
    return {cut:isFinite(c)&&c>0?c:BIM_GRADE.cut,fill:isFinite(f)&&f>0?f:BIM_GRADE.fill};
  }
  /* The slope lines, in order round the pad: square to each edge every BIM_GRADE.step metres; a
     fan at an outside corner; the bisector at an inside one, where the two slopes meet (it rises
     at cos(half the turn) of their rate). k is that rate. */
  function bimGradeSpokes(P){
    var n=P.length,S=[],i,j;
    function nrm(a,b){var dx=b[0]-a[0],dz=b[1]-a[1],L=Math.sqrt(dx*dx+dz*dz);return [dz/L,-dx/L];}
    for(i=0;i<n;i++){
      var a=P[i],b=P[(i+1)%n],c=P[(i+2)%n],n1=nrm(a,b),n2=nrm(b,c),dx=b[0]-a[0],dz=b[1]-a[1],L=Math.sqrt(dx*dx+dz*dz);
      var m=Math.max(1,Math.ceil(L/BIM_GRADE.step-1e-9));
      for(j=1;j<m;j++)S.push({p:[a[0]+dx*j/m,a[1]+dz*j/m],u:n1,k:1,edge:i});
      var turn=n1[0]*n2[1]-n1[1]*n2[0],dot=n1[0]*n2[0]+n1[1]*n2[1];
      if(turn>1e-9){
        var a1=Math.atan2(n1[1],n1[0]),da=Math.atan2(turn,dot),f=Math.max(1,Math.ceil(da/(BIM_GRADE.fanDeg*Math.PI/180)-1e-9));
        for(j=0;j<=f;j++){var an=a1+da*j/f;S.push({p:b.slice(),u:[Math.cos(an),Math.sin(an)],k:1,corner:(i+1)%n});}
      }else if(turn<-1e-9){
        var bx=n1[0]+n2[0],bz=n1[1]+n2[1],bl=Math.sqrt(bx*bx+bz*bz);
        if(bl>1e-9){var u=[bx/bl,bz/bl];S.push({p:b.slice(),u:u,k:u[0]*n1[0]+u[1]*n1[1],corner:(i+1)%n,valley:true});}
      }else S.push({p:b.slice(),u:n1,k:1,corner:(i+1)%n});
    }
    return S;
  }
  /* one slope line: out from the pad until it meets the ground (daylight), meets the slope from
     another edge (valley), or leaves the surface (edge) */
  function bimGradeSpoke(s,P,Z,sl,ground){
    var h0=ground(s.p[0],s.p[1]);
    if(h0===null)return {off:true};
    var dir=h0>Z+1e-9?1:(h0<Z-1e-9?-1:0),r=dir>0?sl.cut:sl.fill;
    if(!dir)return {t:0,end:s.p.slice(),h:Z,kind:'daylight',dir:0};
    function at(t){return [s.p[0]+s.u[0]*t,s.p[1]+s.u[1]*t];}
    function slope(t){return Z+dir*s.k*t/r;}
    function ok(t){var q=at(t);return bimPolyDist(q,P)>=s.k*t-1e-7&&!bimPointInPoly(q,P);}
    function f(t){var q=at(t),g=ground(q[0],q[1]);return g===null?null:dir*(g-slope(t));}   /* above 0 until the daylight */
    var t0=0,t1,dt=BIM_GRADE.march,lo,hi,mid,it,kind=null,g,good;
    for(t1=dt;t1<=BIM_GRADE.reach+1e-9;t1+=dt){
      if(!ok(t1)){kind='valley';break;}
      g=f(t1);
      if(g===null){kind='edge';break;}
      if(g<=0){kind='daylight';break;}
      t0=t1;
    }
    if(!kind)return {t:t0,end:at(t0),h:slope(t0),kind:'edge',dir:dir};
    lo=t0;hi=t1;
    for(it=0;it<80&&hi-lo>1e-11;it++){
      mid=(lo+hi)/2;
      good=kind==='valley'?ok(mid):kind==='edge'?f(mid)!==null:f(mid)>0;
      if(good)lo=mid;else hi=mid;
    }
    var te=kind==='daylight'?hi:lo;
    return {t:te,end:at(te),h:slope(te),kind:kind,dir:dir};
  }
  function bimGradePad(o,idx){
    var P=bimPadWorld(o),Z=parseFloat(o.gradeElev),sl=bimPadSlopes(o),i;
    if(P.length<3)return {error:o.name+' is not a closed outline'};
    for(i=0;i<P.length;i++)if(idx.at(P[i][0],P[i][1])===null)return {error:o.name+' is not wholly on the existing surface'};
    var S=bimGradeSpokes(P),ring=[],nOff=0,nVal=0,nCut=0,nFill=0;
    S.forEach(function(s){
      var r=bimGradeSpoke(s,P,Z,sl,idx.at);
      s.r=r;
      if(r.off){nOff++;return;}
      if(r.kind==='valley')nVal++;else ring.push([r.end[0],r.end[1],r.h]);
      if(r.kind==='edge')nOff++;
      if(r.dir>0)nCut++;else if(r.dir<0)nFill++;
    });
    return {pad:o,P:P,Z:Z,slopes:sl,spokes:S,ring:ring,offSurface:nOff,valleys:nVal,cut:nCut,fill:nFill};
  }
  function bimGradeStamp(ter,pads){
    return JSON.stringify([ter.id,ter.rev||0,ter.survey.length,ter.breaklines||[],ter.boundary||[],ter.faces?ter.faces.length:0,bimObjOffset(ter),
      pads.map(function(o){var sl=bimPadSlopes(o);return [o.id,bimPadWorld(o).map(function(p){return [Math.round(p[0]*1e4),Math.round(p[1]*1e4)];}),parseFloat(o.gradeElev),sl.cut,sl.fill];})]);
  }
  function bimGradeStale(o){
    if(!o||!o.grading)return false;
    var ter=objById(o.grading.existing);
    if(!ter||!ter.survey)return true;
    var pads=o.grading.pads.map(function(p){return objById(p.id);});
    if(pads.some(function(p){return !bimIsPad(p);}))return true;
    return bimGradeStamp(ter,pads)!==o.grading.stamp;
  }
  function bimGradedBy(pad){
    for(var i=0;i<A3D.objs.length;i++){var g=A3D.objs[i];if(g.t==='terrain'&&g.grading&&g.grading.pads.some(function(p){return p.id===pad.id;}))return g;}
    return null;
  }
  /* the proposed surface drawn in front of an existing one */
  function bimTerrainSuperseded(o){
    for(var i=0;i<A3D.objs.length;i++){var g=A3D.objs[i];if(g.t==='terrain'&&g.grading&&g.grading.existing===o.id&&bimLayerShown(g))return g;}
    return null;
  }
  /* the existing surface under the pads: the one given, else the first ungraded surface under a pad */
  function bimGradeExistingFor(pads,prefer){
    if(prefer&&prefer.t==='terrain'&&prefer.survey&&!prefer.grading)return prefer;
    var T=A3D.objs.filter(function(x){return x.t==='terrain'&&x.survey&&x.survey.length>=3&&!x.grading;}),i,j,P,ix;
    for(i=0;i<T.length;i++){ix=bimTinIndexOf(T[i]);for(j=0;j<pads.length;j++){P=bimPadWorld(pads[j]);if(P.length&&ix.at(P[0][0],P[0][1])!==null)return T[i];}}
    return null;
  }
  /* The plane h = gx x + gz z + g0 through three points. */
  function bimPlane3(A,B,C,ha,hb,hc){
    var det=(B[0]-A[0])*(C[1]-A[1])-(C[0]-A[0])*(B[1]-A[1]);
    if(!(Math.abs(det)>1e-18))return null;
    var dB=hb-ha,dC=hc-ha,gx=(dB*(C[1]-A[1])-(B[1]-A[1])*dC)/det,gz=((B[0]-A[0])*dC-(C[0]-A[0])*dB)/det;
    return [gx,gz,ha-gx*A[0]-gz*A[1]];
  }
  /* Cut and fill of B against A, exactly: each of A's triangles clipped by each of B's over it; on
     each piece both are planes, so their difference is linear: split where it is zero and taken
     area times its value at the centroid. Fill is B above A; net is cut less fill. */
  function bimTinVolume(A,B){
    var ib=bimTinIndex(B),cut=0,fill=0,cutA=0,fillA=0,area=0,t,j;
    for(t=0;t<A.tris.length;t++){
      var ta=A.tris[t],a0=A.P[ta[0]],a1=A.P[ta[1]],a2=A.P[ta[2]],pa=bimPlane3(a0,a1,a2,A.H[ta[0]],A.H[ta[1]],A.H[ta[2]]);
      if(!pa)continue;
      var cand=ib.near(Math.min(a0[0],a1[0],a2[0]),Math.min(a0[1],a1[1],a2[1]),Math.max(a0[0],a1[0],a2[0]),Math.max(a0[1],a1[1],a2[1]));
      for(j=0;j<cand.length;j++){
        var tb=B.tris[cand[j]],b0=B.P[tb[0]],b1=B.P[tb[1]],b2=B.P[tb[2]],pb=bimPlane3(b0,b1,b2,B.H[tb[0]],B.H[tb[1]],B.H[tb[2]]);
        if(!pb)continue;
        var piece=bimClipToTri([b0,b1,b2],ta,A.P);
        if(piece.length<3)continue;
        var ar=bimPolyArea(piece);
        if(!(ar>1e-12))continue;
        area+=ar;
        var dx=pb[0]-pa[0],dz=pb[1]-pa[1],d0=pb[2]-pa[2],c,dd,pa_;   /* slivers under 1e-9 m2: their centroids are noise */
        var fp=bimClipHalfPlane(piece,-dx,-dz,d0),cp=bimClipHalfPlane(piece,dx,dz,-d0);
        if(fp.length>=3){c=bimEarthCentroid(fp);pa_=bimPolyArea(fp);if(c&&pa_>1e-9){dd=dx*c[0]+dz*c[1]+d0;if(dd>1e-9){fill+=pa_*dd;fillA+=pa_;}}}
        if(cp.length>=3){c=bimEarthCentroid(cp);pa_=bimPolyArea(cp);if(c&&pa_>1e-9){dd=-(dx*c[0]+dz*c[1]+d0);if(dd>1e-9){cut+=pa_*dd;cutA+=pa_;}}}
      }
    }
    return {cut:cut,fill:fill,net:cut-fill,cutArea:cutA,fillArea:fillA,area:area};
  }
  /* Grade the pads onto the existing surface: the proposed surface, made or updated in place. The
     pads already graded on it stay graded with the new ones. */
  function bimGrade(pads,ter){
    var prev=A3D.objs.filter(function(x){return x.t==='terrain'&&x.grading&&x.grading.existing===ter.id;})[0]||null,i,j;
    if(prev)prev.grading.pads.forEach(function(p){var po=objById(p.id);if(bimIsPad(po)&&pads.indexOf(po)<0)pads=pads.concat([po]);});
    var idx=bimTinIndexOf(ter),tin=idx.tin,res=[],errs=[];
    pads.forEach(function(o){var r=bimGradePad(o,idx);if(r.error)errs.push(r.error);else res.push(r);});
    if(!res.length)return {error:errs[0]||'There is no pad to grade'};
    var regions=res.map(function(r){return r.ring.length>=3?r.ring.map(function(p){return [p[0],p[1]];}):r.P;});
    function inside(p){for(var k=0;k<res.length;k++)if(bimPointInPoly(p,res[k].P)||bimPointInPoly(p,regions[k]))return true;return false;}
    var overlaps=[];
    for(i=0;i<res.length;i++)for(j=i+1;j<res.length;j++)if(bimPolysTouch(regions[i],regions[j]))overlaps.push(res[i].pad.name+' and '+res[j].pad.name);
    var used={},pts=[],seen={},q=bimObjOffset(ter);
    tin.tris.forEach(function(x){used[x[0]]=used[x[1]]=used[x[2]]=1;});
    function add(x,z,y){var k=Math.round(x*1e6)+'_'+Math.round(z*1e6);if(seen[k])return;seen[k]=1;pts.push([x,z,y,'','']);}
    for(i=0;i<tin.P.length;i++)if(used[i]&&!inside(tin.P[i]))add(tin.P[i][0],tin.P[i][1],tin.H[i]);
    var bls=[],kept=0,dropped=0;
    function keepLine(name,w,from){
      for(var k=0;k<res.length;k++)if(bimLineTouchesPoly(w,regions[k])||bimLineTouchesPoly(w,res[k].P)){dropped++;return;}
      bls.push({name:name,pts:w,from:from||null});kept++;
    }
    (ter.breaklines||[]).forEach(function(bl){keepLine(bl.name,(bl.pts||[]).map(function(p){return [p[0]+q[0],p[1]+q[2],(p.length>2&&p[2]!==null&&isFinite(p[2]))?p[2]+q[1]:null];}),bl.from);});
    bimSurveyBreaklines(ter).forEach(function(bl){keepLine(bl.name,bl.idx.map(function(k){var s=ter.survey[k];return [s[0]+q[0],s[1]+q[2],s[2]+q[1]];}));});
    res.forEach(function(r){
      r.P.forEach(function(p){add(p[0],p[1],r.Z);});
      r.spokes.forEach(function(s){if(!s.r||s.r.off)return;add(s.p[0],s.p[1],r.Z);add(s.r.end[0],s.r.end[1],s.r.h);});
      bls.push({name:r.pad.name+' pad',pts:r.P.concat([r.P[0]]).map(function(p){return [p[0],p[1],r.Z];}),grade:'pad'});
      r.spokes.forEach(function(s){if(s.r&&!s.r.off&&s.r.t>1e-6)bls.push({name:r.pad.name+' slope',pts:[[s.p[0],s.p[1],r.Z],[s.r.end[0],s.r.end[1],s.r.h]],grade:'slope'});});
      if(r.ring.length>=2)bls.push({name:r.pad.name+' daylight',pts:r.ring.concat(r.ring.length>=3?[r.ring[0]]:[]).map(function(p){return [p[0],p[1],p[2]];}),grade:'daylight'});
    });
    pushUndo();
    var o=prev;
    if(!o){
      A3D.counts.terrain=(A3D.counts.terrain||0)+1;
      o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'terrain',name:'Proposed '+ter.name,col:'#7fa65a',pos:[0,0,0],layer:ter.layer,rev:0};
      A3D.objs.push(o);
    }
    o.pos=[0,0,0];o.survey=pts;o.breaklines=bls;delete o.faces;
    if(ter.boundary&&ter.boundary.length>=3)o.boundary=ter.boundary.map(function(p){return [p[0]+q[0],p[1]+q[2]];});else delete o.boundary;
    var src=ter.source||{},flat=!q[0]&&!q[1]&&!q[2];
    o.source={format:'Grading',units:flat&&src.base?(src.units||'m'):'m',base:flat&&src.base?{n:src.base.n,e:src.base.e,z:src.base.z}:null,from:ter.name};
    o.rev=(o.rev||0)+1;
    o.grading={existing:ter.id,pads:res.map(function(r){return {id:r.pad.id,name:r.pad.name,elev:r.Z,cut:r.slopes.cut,fill:r.slopes.fill,spokes:r.spokes.length,
        daylight:r.ring.length,valleys:r.valleys,offSurface:r.offSurface,cutSpokes:r.cut,fillSpokes:r.fill};}),
      stamp:bimGradeStamp(ter,res.map(function(r){return r.pad;})),overlaps:overlaps,dropped:dropped,kept:kept,errors:errs.slice(),at:new Date().toISOString()};
    var v=bimTinVolume(tin,bimTerrainTin(o));
    o.grading.volume={cut:v.cut,fill:v.fill,net:v.net,cutArea:v.cutArea,fillArea:v.fillArea,area:v.area};
    A3D.sel=o.id;A3D.sel2=null;A3D.selSet=[o.id];
    refreshTree();refreshProps();paint();saveSoon();bimAnalyzeRefresh();
    return {id:o.id,created:!prev,volume:o.grading.volume,pads:o.grading.pads,overlaps:overlaps,errors:errs,dropped:dropped};
  }
  function bimGradeToast(r){
    if(!r)return;
    if(r.error){a3dToast(r.error);return;}
    var o=objById(r.id),v=r.volume;
    a3dToast(o.name+': '+r.pads.length+' pad'+(r.pads.length===1?'':'s')+' graded; cut '+bimDispNum(v.cut,1)+' m³, fill '+bimDispNum(v.fill,1)+' m³, net '+
      (v.net>=0?bimDispNum(v.net,1)+' m³ to take away':bimDispNum(-v.net,1)+' m³ to bring in')+
      (r.overlaps.length?'; the slopes of '+r.overlaps[0]+' overlap':'')+(r.errors.length?'; '+r.errors[0]:''));
  }
  /* GRADE: the selected pads (a proposed surface selected: its pads again), else every pad */
  function bimGradeCommand(){
    var sel=(A3D.selSet||[]).map(objById).filter(Boolean),pads=sel.filter(bimIsPad),ter=sel.filter(function(x){return x.t==='terrain'&&x.survey;})[0]||null;
    if(ter&&ter.grading){
      if(!pads.length)pads=ter.grading.pads.map(function(p){return objById(p.id);}).filter(bimIsPad);
      ter=objById(ter.grading.existing);
    }
    var bare=sel.filter(function(x){return x.t==='sketch'&&x.closed!==false&&!bimIsPoint(x)&&!bimIsPad(x);});
    if(!pads.length&&bare.length){a3dToast('Give '+bare[0].name+' a Pad Elevation in Properties first');return null;}
    if(!pads.length)pads=A3D.objs.filter(bimIsPad);
    if(!pads.length){a3dToast('There is no pad: give a closed outline a Pad Elevation in Properties, then GRADE');return null;}
    ter=bimGradeExistingFor(pads,ter);
    if(!ter){a3dToast('There is no existing surface under the pads: make one with SURVEY, or import LandXML');return null;}
    var r=bimGrade(pads,ter);
    bimGradeToast(r);
    return r;
  }
  function bimRegrade(o){
    if(!o||!o.grading)return null;
    var ex=objById(o.grading.existing),pads=o.grading.pads.map(function(p){return objById(p.id);}).filter(bimIsPad);
    if(!ex){a3dToast('The existing surface '+o.name+' was graded on is gone');return null;}
    if(!pads.length){a3dToast('None of its pads has a Pad Elevation any more');return null;}
    var r=bimGrade(pads,ex);
    bimGradeToast(r);
    return r;
  }
  /* CUTFILL: two surfaces selected, the second against the first; else every proposed surface
     against its existing one */
  function bimCutFillCommand(){
    var T=(A3D.selSet||[]).map(objById).filter(function(x){return x&&x.t==='terrain'&&x.survey;});
    if(T.length>=2){
      var v=bimTinVolume(bimTerrainTin(T[0]),bimTerrainTin(T[1]));
      A3D_ANZ.cutfill={a:T[0].id,b:T[1].id,v:v};
      a3dToast(T[1].name+' against '+T[0].name+': cut '+bimDispNum(v.cut,1)+' m³, fill '+bimDispNum(v.fill,1)+' m³, over '+bimDispNum(v.area,1)+' m² where both are');
      bimAnalyzeRefresh();
      return v;
    }
    var G=(T.length?T:A3D.objs.filter(function(x){return x.t==='terrain'&&x.grading;})).filter(function(x){return x.grading;});
    if(!G.length){a3dToast('Select two surfaces (the existing one first), or GRADE a pad first');return null;}
    G.forEach(function(x){var e=objById(x.grading.existing);if(e){var w=bimTinVolume(bimTerrainTin(e),bimTerrainTin(x));x.grading.volume={cut:w.cut,fill:w.fill,net:w.net,cutArea:w.cutArea,fillArea:w.fillArea,area:w.area};}});
    var g=G[0].grading.volume;
    refreshProps();saveSoon();bimAnalyzeRefresh();
    a3dToast(G[0].name+': cut '+bimDispNum(g.cut,1)+' m³, fill '+bimDispNum(g.fill,1)+' m³'+(G.length>1?' (and '+(G.length-1)+' more)':''));
    return g;
  }
  /* ---- cut and fill bands: the proposed against its existing, at each triangle's centroid ---- */
  var BIM_CUTFILL_BANDS=[-2,-1,-0.5,-0.1,0.1,0.5,1,2];
  var BIM_CUTFILL_COLS=['#7f1d1d','#c62828','#e57373','#f3c1bd','#8a8f96','#bcdcf7','#64b5f6','#1e88e5','#0d47a1'];
  var BIM_CUTFILL_LABELS=['Cut over 2 m','Cut 1 to 2 m','Cut 0.5 to 1 m','Cut 0.1 to 0.5 m','Within 0.1 m','Fill 0.1 to 0.5 m','Fill 0.5 to 1 m','Fill 1 to 2 m','Fill over 2 m'];
  function bimBandsOf(o,mode){
    if(mode!=='cutfill')return bimTerrainBands(bimTerrainTin(o),mode);
    var e=o.grading&&objById(o.grading.existing);
    return e?bimTerrainBands(bimTerrainTin(o),'cutfill',bimTinIndexOf(e)):null;
  }
  function bimCutFillMapCommand(){
    var G=(A3D.selSet||[]).map(objById).filter(function(x){return x&&x.t==='terrain'&&x.grading;});
    if(!G.length)G=A3D.objs.filter(function(x){return x.t==='terrain'&&x.grading;});
    if(!G.length){a3dToast('There is no proposed surface: GRADE a pad first');return null;}
    var on=!G.every(function(x){return x.tview==='cutfill';});
    G.forEach(function(x){bimTerrainSetView(x,on?'cutfill':'');});
    a3dToast(on?G[0].name+' coloured by cut and fill against '+((objById(G[0].grading.existing)||{}).name||'the existing'):'The cut and fill colours are off');
    return on;
  }
  /* ---- spot elevations: a point labelled with the height of the surface under it ---- */
  function bimSpotElev(o){
    var q=bimObjOffset(o),x=o.pts[0][0]+q[0],z=o.pts[0][1]+q[2],i,h,pref=o.spot&&o.spot.surface?objById(o.spot.surface):null,T;
    T=pref&&pref.t==='terrain'&&pref.survey?[pref]:A3D.objs.filter(function(t){return t.t==='terrain'&&t.survey&&bimLayerShown(t);}).sort(function(a,b){return (b.grading?1:0)-(a.grading?1:0);});
    for(i=0;i<T.length;i++){h=bimTinIndexOf(T[i]).at(x,z);if(h!==null)return {h:h,surface:T[i].id,name:T[i].name,x:x,z:z};}
    return {h:null,surface:null,name:'',x:x,z:z};
  }
  function bimSpotCommand(){
    var sel=(A3D.selSet||[]).map(objById),S=sel.filter(bimIsPoint),ter=sel.filter(function(x){return x&&x.t==='terrain'&&x.survey;})[0]||null;
    if(!S.length){a3dToast('Select points (POINT places them), and a surface if it is to be that one, then SPOTELEV');return null;}
    pushUndo();
    S.forEach(function(x){x.spot={surface:ter?ter.id:null};});
    var r=S.map(function(x){var e=bimSpotElev(x);return {id:x.id,h:e.h,surface:e.surface};}),n=r.filter(function(x){return x.h===null;}).length;
    refreshProps();paint();saveSoon();
    a3dToast(S.length+' spot elevation'+(S.length===1?'':'s')+(n?'; '+n+' not over a surface':'')+(r.length===1&&r[0].h!==null?': '+bimDispNum(r[0].h,3)+' m':''));
    return r;
  }
  /* spots at every corner of a proposed surface's pads */
  function bimGradeSpots(o){
    if(!o||!o.grading)return 0;
    pushUndo();
    var n=0,ids=[];
    o.grading.pads.forEach(function(gp){var pad=objById(gp.id);if(!pad)return;bimPadWorld(pad).forEach(function(p){var s=bimAddPoint(p[0],p[1]);s.spot={surface:o.id};ids.push(s.id);n++;});});
    refreshTree();refreshProps();paint();saveSoon();
    a3dToast(n+' spot elevation'+(n===1?'':'s')+' at the pad corners');
    return ids;
  }
  /* ---- slope arrows ---- */
  function bimSetSlopeArrows(o,on){
    if(!o||o.t!=='terrain')return false;
    if(!!o.arrows===!!on)return true;
    pushUndo();
    if(on)o.arrows=true;else delete o.arrows;
    refreshProps();paint();saveSoon();
    return true;
  }
  function bimSlopeArrowsCommand(){
    var T=(A3D.selSet||[]).map(objById).filter(function(x){return x&&x.t==='terrain'&&x.survey;});
    if(!T.length)T=A3D.objs.filter(function(x){return x.t==='terrain'&&x.survey;});
    if(!T.length){a3dToast('There is no terrain surface: make one with SURVEY, or import LandXML');return null;}
    var on=!T.every(function(x){return x.arrows;});
    pushUndo();
    T.forEach(function(x){if(on)x.arrows=true;else delete x.arrows;});
    refreshProps();paint();saveSoon();
    a3dToast(on?'Slope arrows on '+T[0].name+(T.length>1?' and '+(T.length-1)+' more':'')+(bimCameraIsPlan()?'':' -- shown in plan'):'Slope arrows off');
    return on;
  }
"""

rep("""  /* ================= __acad3dV138: verify the survey ================= */""",
    ENGINE + """  /* ================= __acad3dV138: verify the survey ================= */""")

# cut and fill bands
rep("""  function bimTerrainBands(tin,mode){""", """  function bimTerrainBands(tin,mode,ref){   /* __acad3dV145: ref, the existing surface's index, for cutfill */""")
rep("""      BIM_ASPECT.forEach(function(a){bands.push({label:'Facing '+a.n,col:a.c,area:0});});
    }else return null;""", """      BIM_ASPECT.forEach(function(a){bands.push({label:'Facing '+a.n,col:a.c,area:0});});
    }else if(mode==='cutfill'&&ref){
      for(i=0;i<BIM_CUTFILL_LABELS.length;i++)bands.push({label:BIM_CUTFILL_LABELS[i],col:BIM_CUTFILL_COLS[i],area:0});
    }else return null;""")
rep("""      else k=pl.slope<2?0:1+Math.floor(((pl.aspect+22.5)%360)/45);
      tri.push(k);""", """      else if(mode==='cutfill'){
        var he=ref.at((A[0]+B[0]+C[0])/3,(A[1]+B[1]+C[1])/3);
        if(he===null){tri.push(-1);continue;}
        var dd=(tin.H[tr[0]]+tin.H[tr[1]]+tin.H[tr[2]])/3-he;
        for(k=0;k<BIM_CUTFILL_BANDS.length;k++)if(dd<BIM_CUTFILL_BANDS[k])break;
      }
      else k=pl.slope<2?0:1+Math.floor(((pl.aspect+22.5)%360)/45);
      tri.push(k);""")
rep("""    if(mode&&!/^(slope|elevation|aspect)$/.test(mode))return false;""",
    """    if(mode&&!/^(slope|elevation|aspect)$/.test(mode)&&!(mode==='cutfill'&&o.grading))return false;   /* __acad3dV145 */""")
# the survey check is for surveys: a proposed surface is made, not surveyed
rep("""      if(o.t==='terrain'&&o.survey){nTer++;""", """      if(o.t==='terrain'&&o.survey&&!o.grading){nTer++;""")
rep("""    if(o.t==='terrain'&&o.survey)h+=bimPropGroup('Survey Check',bimSurveyCheckHtml(o));   /* __acad3dV138 */""",
    """    if(o.t==='terrain'&&o.survey&&!o.grading)h+=bimPropGroup('Survey Check',bimSurveyCheckHtml(o));   /* __acad3dV138; __acad3dV145: not a proposed one */""")
# in 3D, a proposed surface stands in for the existing one under it
rep("""    for(i=0;i<A3D.objs.length;i++){o=A3D.objs[i];if(o.t==='terrain'&&o.survey&&bimLayerShown(o))list.push(o);}""",
    """    for(i=0;i<A3D.objs.length;i++){o=A3D.objs[i];if(o.t==='terrain'&&o.survey&&bimLayerShown(o)&&!bimTerrainSuperseded(o))list.push(o);}   /* __acad3dV145 */""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
