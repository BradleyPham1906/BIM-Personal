"""patch_phase99.py -- __acad3dV99: the region dependent, part 1 -- reading a region.

A room, floor, ceiling, roof or hatch traced from SEVERAL shapes has no single source. What it
does have is a place: the point it was picked at, on a plane. Re-tracing from that point
against the shapes on that plane gives its boundary again, from whatever encloses it now --
walls, sketches and construction lines alike, which is the owner's direction: a room is bounded
by the shapes around it, not only by walls.

This patch adds the reader, with the same contract as bimSourceBoundaryWorld (V97): world
coordinates in, {ring,pts,bulges,y,srcIds,sig} or {error} out, and the dependent converts into
its own frame. `sig` is a signature of every edge on that plane, so a later check can tell
whether ANYTHING on the plane changed -- a shape added, deleted or moved -- without re-tracing.
"""
import hashlib, pathlib

SRC = pathlib.Path('canvas_v10.html')
BASE = 'c1c394547e6a3310b5fef317b75a0c837df6c9c6c720af19093359bfde3ab756'

txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

OLD = """  /* World points into a dependent's own frame. */
  function bimToFrame(o,pts){
    var q=bimObjOffset(o);
    return pts.map(function(p){return [p[0]-q[0],p[1]-q[2]];});
  }
"""
NEW = OLD + """  /* ================= __acad3dV99: region dependents =================

     o.region = {seed:[x,z], y, want:'all'|'walls', members:[ids], sig, open}

     seed and y are in the dependent's OWN frame, like its points, so moving the dependent moves
     the place it is traced from. members are the objects whose edges the last trace walked --
     what the dependency graph links it to. sig is the signature of the whole plane at the last
     trace. open is true while the region is no longer enclosed; the dependent then keeps its
     last shape and says so once. want is 'all' for everything made from V99 on; a room saved
     by an older build as 'wallgroup' is adopted with 'walls', so re-tracing it cannot pick up
     sketches it never used to see. */
  var BIM_REGION_WANT={all:{walls:true,sketches:true,clines:true},walls:{walls:true}};
  function bimIsRegionDep(o){
    return !!(o&&o.region&&o.region.seed&&o.region.seed.length===2&&
              isFinite(o.region.seed[0])&&isFinite(o.region.seed[1]));
  }
  function bimRegionWant(o){
    return BIM_REGION_WANT[(o&&o.region&&o.region.want==='walls')?'walls':'all'];
  }
  function bimRegionPlaneY(o){return (o.region.y||0)+bimObjOffset(o)[1];}
  function bimRegionSeedWorld(o){
    var q=bimObjOffset(o);
    return [o.region.seed[0]+q[0],o.region.seed[1]+q[2]];
  }
  function bimCloneRegion(r){
    if(!r||!r.seed)return null;
    return {seed:[r.seed[0],r.seed[1]],y:r.y||0,want:r.want==='walls'?'walls':'all',
            members:(r.members||[]).slice(),sig:r.sig||'',open:!!r.open};
  }
  /* A signature of every edge on a plane. Two planes with the same signature trace the same
     faces, so a dependent whose recorded signature still matches needs no re-trace. */
  function bimEdgesSig(edges){
    var h=2166136261,i,s,k;
    function mix(str){
      for(k=0;k<str.length;k++){h^=str.charCodeAt(k);h=(h*16777619)>>>0;}
    }
    for(i=0;i<edges.length;i++){
      s=edges[i].a[0].toFixed(6)+','+edges[i].a[1].toFixed(6)+','+edges[i].b[0].toFixed(6)+','+
        edges[i].b[1].toFixed(6)+','+(edges[i].bulge||0).toFixed(6)+','+(edges[i].src||'')+';';
      mix(s);
    }
    return edges.length+':'+h.toString(36);
  }
  /* A point strictly inside a polygon. The centroid when it is inside; otherwise the middle of
     the widest interior span of a horizontal scan line, tried at several heights -- an L-shaped
     or U-shaped room has its centroid outside itself. */
  function bimInteriorPoint(poly){
    if(!poly||poly.length<3)return null;
    var n=poly.length,i,cx=0,cz=0,minz=Infinity,maxz=-Infinity;
    for(i=0;i<n;i++){cx+=poly[i][0];cz+=poly[i][1];
      if(poly[i][1]<minz)minz=poly[i][1];if(poly[i][1]>maxz)maxz=poly[i][1];}
    cx/=n;cz/=n;
    if(bimPointInPoly([cx,cz],poly))return [cx,cz];
    var fr=[0.5,0.37,0.63,0.25,0.75,0.13,0.87],f,z,xs,j,a,b,best=null,bw=0;
    for(f=0;f<fr.length;f++){
      z=minz+(maxz-minz)*fr[f];
      xs=[];
      for(i=0,j=n-1;i<n;j=i++){
        a=poly[i];b=poly[j];
        if((a[1]>z)!==(b[1]>z))xs.push(a[0]+(z-a[1])*(b[0]-a[0])/(b[1]-a[1]));
      }
      xs.sort(function(p,q){return p-q;});
      for(i=0;i+1<xs.length;i+=2){
        if(xs[i+1]-xs[i]>bw&&bimPointInPoly([(xs[i]+xs[i+1])/2,z],poly)){
          bw=xs[i+1]-xs[i];best=[(xs[i]+xs[i+1])/2,z];
        }
      }
      if(best)return best;
    }
    return null;
  }
  /* Trace the region containing pt on plane y, from the shapes `want` selects. WORLD in and out. */
  function bimRegionTraceAt(pt,y,want){
    var edges=bimBoundaryEdges(y,want||BIM_REGION_WANT.all),sig=bimEdgesSig(edges),res,flat;
    if(edges.length<2)return {error:'there is nothing on this plan to bound it',sig:sig};
    try{res=bimTraceBoundary(edges,pt);}
    catch(eR){
      console.warn('[BIM] Region trace failed',eR);
      return {error:'its boundary could not be traced',sig:sig};
    }
    if(!res||res.error)return {error:(res&&res.error)||'it is not inside a closed region',sig:sig};
    flat=bimFlattenPoly(res.pts,res.bulges,true);
    if(!flat||flat.length<3||!(res.area>1e-6))return {error:'its region has no area',sig:sig};
    return {ring:flat,pts:res.pts,bulges:bimHasBulge(res.bulges)?res.bulges.slice():null,y:y,
            srcIds:(res.srcIds||[]).slice(),islands:!!res.islands,sig:sig,type:'region'};
  }
  /* The dependent's current boundary in WORLD plan coordinates -- what it looks like now. */
  function bimDependentRingWorld(o){
    var q=bimObjOffset(o),ring=null;
    if(o.t==='room')ring=o.pts;
    else if(bimIsHatch(o))ring=bimFlattenPoly(o.pts,o.bulges||null,true);
    else if(o.bim&&(o.bim.type==='floor'||o.bim.type==='ceiling'))ring=o.bim.profile;
    else if(o.bim&&o.bim.type==='roof')ring=o.bim.footprint;
    if(!ring||ring.length<3)return null;
    return ring.map(function(p){return [p[0]+q[0],p[1]+q[2]];});
  }
  /* A region dependent's boundary now. From its seed first; when the seed no longer lands in a
     region (a wall was dragged over it), from a point inside the shape it has now. */
  function bimRegionBoundaryWorld(o){
    if(!bimIsRegionDep(o))return {error:'it has no region to trace'};
    var y=bimRegionPlaneY(o),want=bimRegionWant(o);
    var r=bimRegionTraceAt(bimRegionSeedWorld(o),y,want);
    if(!r.error)return r;
    var cur=bimDependentRingWorld(o),ip=cur?bimInteriorPoint(cur):null,r2;
    if(ip){
      r2=bimRegionTraceAt(ip,y,want);
      if(!r2.error)return r2;
    }
    return {error:'it is no longer enclosed',unenclosed:true,sig:r.sig};
  }
  /* Record what a successful trace found: its members, the plane signature, and a fresh seed
     well inside the new shape, so the next trace does not start from a point on an edge. */
  function bimRegionRecord(o,b){
    var q=bimObjOffset(o),ip=bimInteriorPoint(b.ring),i,allWalls=b.srcIds.length>0,m;
    o.region.members=b.srcIds.slice();
    o.region.sig=b.sig;
    o.region.open=false;
    if(ip)o.region.seed=[ip[0]-q[0],ip[1]-q[2]];
    for(i=0;i<b.srcIds.length;i++){
      m=objById(b.srcIds[i]);
      if(!(m&&m.t==='solid'&&m.bim&&m.bim.type==='wall')){allWalls=false;break;}
    }
    o.sourceType=allWalls?'wallgroup':'region';o.sourceId=null;
    if(o.bim&&o.bim.type==='roof'){o.bim.sourceType=o.sourceType;o.bim.sourceId=null;}
  }
  /* The region is no longer closed: keep the last shape, say so ONCE, and remember the plane
     signature so the same open plane is not re-traced on every save. */
  function bimRegionNoteOpen(o,b,ctx){
    if(!o.region.open){
      o.region.open=true;
      console.warn('[BIM] '+o.name+' is no longer enclosed; it keeps its last shape.');
      a3dToast(o.name+' is no longer enclosed - it keeps its last shape until its boundary is closed again');
    }
    if(b&&b.sig)o.region.sig=b.sig;
    if(ctx)ctx.regionsOpen=(ctx.regionsOpen||0)+1;
    return false;
  }
"""
assert txt.count(OLD) == 1
txt = txt.replace(OLD, NEW, 1)
SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
