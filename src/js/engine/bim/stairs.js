  // ---- __acad3dV43: multi-flight stairs (landings/turns) + stepped guard railings ----
  // Path-based stair engine. A stair is now defined by a click-polyline centerline (bim.path);
  // a landing is centered on each interior vertex, sized from the corridor's own mitered corner
  // via the existing bimOffsetRing (the same math already proven for wall corners), so a turn's
  // inside/outside edges never gap or overlap. Steps are apportioned across the flights either
  // side of each landing by available run length (largest-remainder method -- the same idea the
  // app already uses for riserH: a *target* tread depth, adjusted per flight to fit exactly)
  // rather than walking forward in fixed increments and hoping a landing lands on a step
  // boundary. Legacy stairs (bim.start/bim.dir, no bim.path) keep using bimBuildStairGeometry/
  // bimBuildStairMesh above untouched; new stairs always carry bim.path.
  function bimCleanStairPath(pathIn){
    var P=[],i;
    if(!pathIn||pathIn.length<2)return null;
    for(i=0;i<pathIn.length;i++){
      var p=pathIn[i];
      if(!p||!isFinite(p[0])||!isFinite(p[1]))return null;
      if(P.length){
        var dx=p[0]-P[P.length-1][0],dz=p[1]-P[P.length-1][1];
        if(Math.sqrt(dx*dx+dz*dz)<1e-9)continue;
      }
      P.push([p[0],p[1]]);
    }
    return P.length>=2?P:null;
  }
  // Shared "walk layout" used by both the solid-stair mesh and the railing mesh: segment table,
  // landing zones, and the ordered list of flat/rising profile entries (steps interleaved with
  // landing flats, landings pre-split at their vertex so the true mitered corner point is used
  // on both sides of a turn).
  function bimBuildStairLayout(pathIn,width,baseY,numSteps,riserH,treadD,landingLen){
    var P=bimCleanStairPath(pathIn);
    if(!P)return {error:'Stair path needs at least 2 distinct points'};
    if(!(width>0))return {error:'Width must be a positive number'};
    if(!(numSteps>0)||!(riserH>0)||!(treadD>0))return {error:'Stair needs a positive step count, riser height, and tread depth'};
    var hw=width/2,n=P.length,i;
    var segs=[];
    for(i=0;i<n-1;i++){
      var a=P[i],b=P[i+1];
      var dx=b[0]-a[0],dz=b[1]-a[1],len=Math.sqrt(dx*dx+dz*dz);
      if(!(len>1e-6))return {error:'Stair path has a zero-length segment'};
      segs.push({a:a,b:b,len:len});
    }
    var cum=[0];
    for(i=0;i<segs.length;i++)cum.push(cum[i]+segs[i].len);
    var total=cum[cum.length-1];

    var landingHalf=landingLen/2;
    var zones=[],k;
    for(k=1;k<=n-2;k++)zones.push({vertex:k,vRun:cum[k],start:cum[k]-landingHalf,end:cum[k]+landingHalf});
    for(i=0;i<segs.length;i++){
      var need=0;
      if(i>0)need+=landingHalf;
      if(i<segs.length-1)need+=landingHalf;
      if(segs[i].len<need-1e-9)return {error:'Segment '+(i+1)+' is too short for a '+landingLen.toFixed(2)+'m landing at both ends'};
    }

    var ringL=bimOffsetRing(P,hw,false),ringR=bimOffsetRing(P,-hw,false);

    function segAt(run){
      for(var s=0;s<segs.length;s++)if(run<=cum[s+1]+1e-7)return s;
      return segs.length-1;
    }
    function plainPt(run,side){
      var s=segAt(run),seg=segs[s];
      var t=run-cum[s];
      var ux=(seg.b[0]-seg.a[0])/seg.len,uz=(seg.b[1]-seg.a[1])/seg.len;
      var px=seg.a[0]+ux*t,pz=seg.a[1]+uz*t;
      var nrm=bimSegNormal(seg.a,seg.b);
      return [px+nrm[0]*hw*side,pz+nrm[1]*hw*side];
    }
    function cpt(run,side){
      for(var zi=0;zi<zones.length;zi++){
        if(Math.abs(run-zones[zi].vRun)<1e-7)return side>0?ringL[zones[zi].vertex]:ringR[zones[zi].vertex];
      }
      return plainPt(run,side);
    }

    var flightBounds=[],prevEnd=0;
    for(k=0;k<zones.length;k++){flightBounds.push([prevEnd,zones[k].start]);prevEnd=zones[k].end;}
    flightBounds.push([prevEnd,total]);
    var flights=flightBounds.map(function(b){return {start:b[0],end:b[1],len:b[1]-b[0]};});
    var totalFlightLen=flights.reduce(function(s,f){return s+f.len;},0);
    var minFlight=Math.min.apply(null,flights.map(function(f){return f.len;}));
    if(minFlight<1e-6)return {error:'A landing leaves no room for a flight next to it — lengthen that segment or remove the turn'};
    if(numSteps<flights.length)return {error:'Not enough steps ('+numSteps+') to give each of the '+flights.length+' flights at least one tread — raise the rise or reduce landings'};

    var raw=flights.map(function(f){return numSteps*f.len/totalFlightLen;});
    var counts=raw.map(Math.floor);
    var used=counts.reduce(function(s,c){return s+c;},0);
    var remainder=numSteps-used;
    var order=raw.map(function(r,idx){return {idx:idx,frac:r-Math.floor(r)};}).sort(function(a,b){return b.frac-a.frac;});
    for(i=0;i<remainder;i++)counts[order[i%order.length].idx]++;
    for(i=0;i<counts.length;i++)if(counts[i]<1)return {error:'Flight '+(i+1)+' would get zero treads — raise the rise, reduce landings, or lengthen that run'};
    for(i=0;i<flights.length;i++)flights[i].steps=counts[i];
    for(i=0;i<flights.length;i++)flights[i].treadLocal=flights[i].len/flights[i].steps;
    var STAIR_MIN_TREAD=0.15;
    for(i=0;i<flights.length;i++){
      if(flights[i].treadLocal<STAIR_MIN_TREAD-1e-9)return {
        error:'Stair path is too short: flight '+(i+1)+' would need a '+flights[i].treadLocal.toFixed(3)+
          'm tread depth (below the '+STAIR_MIN_TREAD.toFixed(2)+'m minimum) to fit '+flights[i].steps+
          ' of the '+numSteps+' treads in '+flights[i].len.toFixed(2)+'m — lengthen the path or add a landing to split it up'
      };
    }

    var treads=[],stepIdx=0,fi;
    for(fi=0;fi<flights.length;fi++){
      var fl=flights[fi],r=fl.start;
      for(i=0;i<fl.steps;i++){
        var nextR=r+fl.treadLocal;
        treads.push({t:'step',runStart:r,runEnd:nextR,riseStart:stepIdx*riserH,riseEnd:(stepIdx+1)*riserH});
        r=nextR;stepIdx++;
      }
    }
    var finalRun=treads.length?treads[treads.length-1].runEnd:0;
    var totalRise=numSteps*riserH;

    var prof=[],stepCursor=0;
    for(fi=0;fi<flights.length;fi++){
      var stepsHere=flights[fi].steps;
      for(i=0;i<stepsHere;i++){prof.push(treads[stepCursor]);stepCursor++;}
      if(fi<zones.length){
        var zone=zones[fi];
        var lastRise=prof[prof.length-1].riseEnd;
        prof.push({t:'landing',runStart:zone.start,runEnd:zone.vRun,riseStart:lastRise,riseEnd:lastRise});
        prof.push({t:'landing',runStart:zone.vRun,runEnd:zone.end,riseStart:lastRise,riseEnd:lastRise});
      }
    }

    return {
      path:P,segs:segs,cum:cum,total:total,zones:zones,flights:flights,prof:prof,
      finalRun:finalRun,totalRise:totalRise,hw:hw,cpt:cpt,
      treadAvg:totalFlightLen/numSteps
    };
  }
  // Pushes a face after collapsing any consecutive (including wraparound) coincident vertices.
  // A tight inner turn (a landing zone as wide as the corridor's own half-width pinches to a
  // point exactly at the corner) legitimately degenerates some quads to triangles or to nothing
  // on that side; dropping the repeated vertex keeps every remaining face non-degenerate instead
  // of emitting a zero-area face with a self-loop edge.
  function bimPushStairPoly(raw,pts){
    var out=[],i;
    function same(a,b){return Math.abs(a[0]-b[0])<1e-9&&Math.abs(a[1]-b[1])<1e-9&&Math.abs(a[2]-b[2])<1e-9;}
    for(i=0;i<pts.length;i++){if(!out.length||!same(out[out.length-1],pts[i]))out.push(pts[i]);}
    while(out.length>1&&same(out[0],out[out.length-1]))out.pop();
    if(out.length>=3)raw.push(out);
  }
  function bimBuildStairPathMesh(pathIn,width,baseY,numSteps,riserH,treadD,landingLen){
    var L=bimBuildStairLayout(pathIn,width,baseY,numSteps,riserH,treadD,landingLen);
    if(L.error)return L;
    var prof=L.prof,cpt=L.cpt,raw=[],i,sd;
    function y3(xz,rise){return [xz[0],baseY+rise,xz[1]];}

    for(sd=-1;sd<=1;sd+=2){
      for(i=0;i<prof.length;i++){
        var e=prof[i];
        var blXZ=cpt(e.runStart,sd),brXZ=cpt(e.runEnd,sd);
        var bl=y3(blXZ,0),br=y3(brXZ,0);
        var tr=y3(brXZ,e.riseEnd),tl=y3(blXZ,e.riseEnd);
        var flat=Math.abs(e.riseEnd-e.riseStart)<1e-9;
        if(i===0||flat){
          if(sd<0){bimPushStairPoly(raw,[bl,br,tr]);bimPushStairPoly(raw,[bl,tr,tl]);}
          else{bimPushStairPoly(raw,[bl,tr,br]);bimPushStairPoly(raw,[bl,tl,tr]);}
        }else{
          var ml=y3(blXZ,e.riseStart);
          if(sd<0){bimPushStairPoly(raw,[bl,br,tr]);bimPushStairPoly(raw,[bl,tr,ml]);bimPushStairPoly(raw,[ml,tr,tl]);}
          else{bimPushStairPoly(raw,[bl,tr,br]);bimPushStairPoly(raw,[bl,ml,tr]);bimPushStairPoly(raw,[ml,tl,tr]);}
        }
      }
    }
    for(i=0;i<prof.length;i++){
      var e2=prof[i];
      bimPushStairPoly(raw,[y3(cpt(e2.runEnd,-1),0),y3(cpt(e2.runStart,-1),0),y3(cpt(e2.runStart,1),0),y3(cpt(e2.runEnd,1),0)]);
      bimPushStairPoly(raw,[y3(cpt(e2.runStart,-1),e2.riseEnd),y3(cpt(e2.runEnd,-1),e2.riseEnd),y3(cpt(e2.runEnd,1),e2.riseEnd),y3(cpt(e2.runStart,1),e2.riseEnd)]);
      if(Math.abs(e2.riseEnd-e2.riseStart)>1e-9){
        bimPushStairPoly(raw,[y3(cpt(e2.runStart,-1),e2.riseStart),y3(cpt(e2.runStart,-1),e2.riseEnd),y3(cpt(e2.runStart,1),e2.riseEnd),y3(cpt(e2.runStart,1),e2.riseStart)]);
      }
    }
    bimPushStairPoly(raw,[y3(cpt(L.finalRun,1),0),y3(cpt(L.finalRun,1),L.totalRise),y3(cpt(L.finalRun,-1),L.totalRise),y3(cpt(L.finalRun,-1),0)]);

    // Global orientation flip: the per-face windings above are internally consistent (every
    // undirected edge is already shared by exactly two faces with no duplicated direction), but
    // come out net inward. Reversing every face flips overall handedness to outward without
    // touching that already-correct topology.
    raw=raw.map(function(f){return f.slice().reverse();});
    var m=bimWeldMesh(raw);
    return {mesh:m,layout:L};
  }
  // Stepped guard railing: a top rail following the tread/landing nosing line (jumping at each
  // riser, flat across treads/landings), plus a vertical post under each waypoint. Built from
  // small boxes so it's real, dimensioned geometry, then CSG-unioned into the stair solid by the
  // caller using the app's already-proven csgUnion kernel.
  function bimBoxBetween3D(p1,p2,thick){
    var ax=[p2[0]-p1[0],p2[1]-p1[1],p2[2]-p1[2]];
    var len=Math.sqrt(ax[0]*ax[0]+ax[1]*ax[1]+ax[2]*ax[2]);
    if(!(len>1e-9))return null;
    ax=[ax[0]/len,ax[1]/len,ax[2]/len];
    var refUp=Math.abs(ax[1])>0.9?[1,0,0]:[0,1,0];
    function cross(a,b){return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];}
    function norm(a){var l=Math.sqrt(a[0]*a[0]+a[1]*a[1]+a[2]*a[2])||1;return [a[0]/l,a[1]/l,a[2]/l];}
    var side=norm(cross(ax,refUp));
    var up2=norm(cross(side,ax));
    var h=thick/2;
    function corner(p,s,u){return [p[0]+side[0]*s*h+up2[0]*u*h,p[1]+side[1]*s*h+up2[1]*u*h,p[2]+side[2]*s*h+up2[2]*u*h];}
    var v=[
      corner(p1,-1,-1),corner(p1,1,-1),corner(p1,1,1),corner(p1,-1,1),
      corner(p2,-1,-1),corner(p2,1,-1),corner(p2,1,1),corner(p2,-1,1)
    ];
    var f=[
      [0,1,2,3],[7,6,5,4],
      [4,5,1,0],[5,6,2,1],[6,7,3,2],[7,4,0,3]
    ];
    return {v:v,f:f};
  }
  function bimBuildStairGuardMesh(layout,baseY,side,railHeight,railThick,postThick){
    var prof=layout.prof,cpt=layout.cpt,i;
    var kf=[];
    // Dedup by the ACTUAL resulting 3D point, not the raw (run,rise) pair: at a pinched landing
    // corner (landingLen equal to the corridor width is a common, natural setting) two different
    // run values can land on the exact same mitered corner point once passed through cpt -- the
    // same pinch already handled for the main stair mesh via pushPoly. Deduping on (run,rise)
    // alone misses that and would otherwise place two literally-coincident posts on top of each
    // other, which is exactly the kind of silent corruption this project's fail-safe rule forbids.
    function pushKf(run,rise){
      var xz=cpt(run,side),pt=[xz[0],rise,xz[1]];
      var last=kf[kf.length-1];
      if(last&&Math.abs(last.pt[0]-pt[0])<1e-9&&Math.abs(last.pt[1]-pt[1])<1e-9&&Math.abs(last.pt[2]-pt[2])<1e-9)return;
      kf.push({run:run,rise:rise,pt:pt});
    }
    pushKf(prof[0].runStart,prof[0].riseStart);
    for(i=0;i<prof.length;i++){
      pushKf(prof[i].runStart,prof[i].riseEnd);
      pushKf(prof[i].runEnd,prof[i].riseEnd);
    }
    function kf3(k,extra){
      return [k.pt[0],baseY+k.pt[1]+(extra||0),k.pt[2]];
    }
    // Rails only span the flat (same-rise) keyframe pairs, following one tread/landing's top
    // nosing. A same-run, different-rise pair is the vertical jump at a riser: that segment sits
    // entirely inside the taller of the two posts at that riser (identical vertical axis,
    // identical local frame, fully overlapping range), so a rail box there would duplicate the
    // post's own cap face rather than add anything visible -- skip it and let the posts alone
    // carry the verticals.
    var flatPairs=[];
    for(i=0;i<kf.length-1;i++){
      if(Math.abs(kf[i+1].rise-kf[i].rise)>1e-9)continue;
      flatPairs.push({a:i,b:i+1});
    }
    // Adjacent flat pairs that continue in the exact same direction (a straight run of several
    // treads, or -- as seen at a wide-miter turn's landing -- two landing sub-segments that stay
    // collinear on one side) are merged into a single box before building. Chaining separate
    // boxes end to end instead would leave an internal cap at every junction whose vertex
    // numbering, once welded, exactly collides in direction with the next box's own side face --
    // a genuine duplicated half-edge, not a harmless touching seam. Merging removes the
    // redundant internal cap outright rather than trying to detect and tolerate the collision.
    function segDir3(ia,ib){
      var A=kf3(kf[ia],railHeight),B=kf3(kf[ib],railHeight);
      var dx=B[0]-A[0],dy=B[1]-A[1],dz=B[2]-A[2],len=Math.sqrt(dx*dx+dy*dy+dz*dz)||1;
      return [dx/len,dy/len,dz/len];
    }
    var mergedPairs=[];
    for(i=0;i<flatPairs.length;i++){
      var curP=flatPairs[i];
      if(mergedPairs.length){
        var lastP=mergedPairs[mergedPairs.length-1];
        if(lastP.b===curP.a){
          var d1=segDir3(lastP.a,lastP.b),d2=segDir3(curP.a,curP.b);
          var cx=d1[1]*d2[2]-d1[2]*d2[1],cy=d1[2]*d2[0]-d1[0]*d2[2],cz=d1[0]*d2[1]-d1[1]*d2[0];
          if(Math.sqrt(cx*cx+cy*cy+cz*cz)<1e-6){lastP.b=curP.b;continue;}
        }
      }
      mergedPairs.push({a:curP.a,b:curP.b});
    }
    var raw=[],boxCount=0,postCount=0;
    for(i=0;i<mergedPairs.length;i++){
      var a=kf3(kf[mergedPairs[i].a],railHeight),b=kf3(kf[mergedPairs[i].b],railHeight);
      var box=bimBoxBetween3D(a,b,railThick);
      if(box){for(var j=0;j<box.f.length;j++)raw.push(box.f[j].map(function(idx){return box.v[idx];}));boxCount++;}
    }
    for(i=0;i<kf.length;i++){
      var top=kf3(kf[i],railHeight),bot=kf3(kf[i],0);
      var post=bimBoxBetween3D(bot,top,postThick);
      if(post){for(var j2=0;j2<post.f.length;j2++)raw.push(post.f[j2].map(function(idx){return post.v[idx];}));postCount++;}
    }
    return {mesh:bimWeldMesh(raw),rails:boxCount,posts:postCount};
  }
  // Computes the same signed-volume/edge-usage sweep the project's own test suites use, so a
  // build step can verify its own output before accepting it -- this project's fail-safe rule is
  // that a code path must never silently hand back corrupt geometry. dupDir (a directed half-edge
  // used more than once) always indicates real corruption -- e.g. a face pushed twice, or a
  // boolean gone wrong -- regardless of what the mesh represents. Full watertight closure (every
  // undirected edge used by exactly two faces) is additionally required only when strict is true;
  // an *assembly* of separately-built, merely touching solids (see the railing merge below) is
  // legitimately not a single closed manifold at every T-junction, so it is checked with
  // strict=false and a volume/face-count sanity comparison instead.
  function bimMeshSanityCheck(m,strict){
    if(!m||!m.f||!m.v||!m.f.length)return {ok:false,vol:0};
    var und={},dir={},i,j,k,vol=0;
    for(i=0;i<m.f.length;i++){
      var f=m.f[i];
      if(f.length<3)return {ok:false,vol:0};
      for(j=0;j<f.length;j++){
        var a=f[j],b=f[(j+1)%f.length];
        if(a===b)return {ok:false,vol:0};
        var uk=Math.min(a,b)+'-'+Math.max(a,b);und[uk]=(und[uk]||0)+1;
        var dk=a+'>'+b;dir[dk]=(dir[dk]||0)+1;
      }
      for(j=1;j+1<f.length;j++){
        var A=m.v[f[0]],B=m.v[f[j]],C=m.v[f[j+1]];
        vol+=(A[0]*(B[1]*C[2]-B[2]*C[1])-A[1]*(B[0]*C[2]-B[2]*C[0])+A[2]*(B[0]*C[1]-B[1]*C[0]))/6;
      }
    }
    for(k in dir)if(dir[k]>1)return {ok:false,vol:vol};
    if(strict)for(k in und)if(und[k]!==2)return {ok:false,vol:vol};
    return {ok:true,vol:vol};
  }
  /* __acad3dV62: T-junction-tolerant CLOSED-VOLUME test, and why it had to exist.

     bimMeshSanityCheck(m,true) asks for a strict manifold: every undirected edge used by exactly
     two faces. That is the right question for a mesh this app BUILDS itself (a box, a pad, a
     welded railing assembly), and it stays the primary test everywhere it is already used. It is
     the wrong question for a mesh that came out of the BSP boolean kernel. Cutting a door or a
     window out of a wall splits the wall's large faces around the opening but leaves the
     neighbouring faces unsplit, so an unsplit face's long edge is met by two or three shorter
     collinear edges instead of one matching partner -- a T-junction. The surface is still closed
     (it bounds a real volume, and the divergence-theorem volume above is exact), but the
     edge-pairing count is not 2 at those seams. That is why every wall with an opening -- which
     is to say very nearly every wall in a real building -- used to be reported as "Open shell" by
     Check Model, a false positive on the app's single most common object.

     This resolves the T-junctions instead of ignoring them, so a genuine hole is still caught:

       1. Undirected edges used exactly twice are already accounted for and are dropped.
       2. Every DIRECTED edge belonging to an unmatched undirected edge is collected as a real
          coordinate segment. This set is small (tens of edges on a cut wall), so the collinear
          grouping below can afford true tolerance comparisons rather than hash quantisation,
          which would risk splitting one line into two buckets on a rounding boundary and
          reporting a false hole -- the exact failure mode this function exists to remove.
       3. Segments are grouped by supporting line (same direction up to sign, and each endpoint
          within TOL of the other segment's line).
       4. Within a group the segments are projected onto the line and swept: a segment traversed
          along the group's canonical direction carries weight +1, against it -1. On a closed,
          consistently oriented surface every point of every line must be covered by equal numbers
          of forward and backward traversals, so the running sum must be zero on every interval.
          A missing face leaves its boundary loop uncancelled and the sum is non-zero -- caught.

     Returns {closed, manifold, corrupt, vol}: manifold true means it also passed the strict test,
     closed true with manifold false means "closed volume, T-junctions present". */
  function bimMeshClosureCheck(m){
    var strict=bimMeshSanityCheck(m,true);
    if(strict.ok)return {closed:true,manifold:true,corrupt:false,vol:strict.vol,groups:0};
    var loose=bimMeshSanityCheck(m,false);
    if(!loose.ok)return {closed:false,manifold:false,corrupt:true,vol:loose.vol,groups:0};
    var TOL=1e-6,i,j,f,a,b,uk;
    var und={};
    for(i=0;i<m.f.length;i++){
      f=m.f[i];
      for(j=0;j<f.length;j++){
        a=f[j];b=f[(j+1)%f.length];
        uk=Math.min(a,b)+'-'+Math.max(a,b);und[uk]=(und[uk]||0)+1;
      }
    }
    var segs=[];
    for(i=0;i<m.f.length;i++){
      f=m.f[i];
      for(j=0;j<f.length;j++){
        a=f[j];b=f[(j+1)%f.length];
        uk=Math.min(a,b)+'-'+Math.max(a,b);
        if(und[uk]===2)continue;
        var A=m.v[a],B=m.v[b];
        var dx=B[0]-A[0],dy=B[1]-A[1],dz=B[2]-A[2];
        var len=Math.sqrt(dx*dx+dy*dy+dz*dz);
        if(!(len>TOL))continue; // degenerate edge: no length to cover, contributes nothing
        segs.push({A:A,B:B,d:[dx/len,dy/len,dz/len]});
      }
    }
    if(!segs.length)return {closed:true,manifold:false,corrupt:false,vol:loose.vol,groups:0};
    function cross(u,v){return [u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];}
    function norm(u){return Math.sqrt(u[0]*u[0]+u[1]*u[1]+u[2]*u[2]);}
    function dot(u,v){return u[0]*v[0]+u[1]*v[1]+u[2]*v[2];}
    // Perpendicular distance from point p to the line through q with unit direction d.
    function distToLine(p,q,d){
      var w=[p[0]-q[0],p[1]-q[1],p[2]-q[2]];
      return norm(cross(w,d));
    }
    var groups=[],gi,g,placed;
    for(i=0;i<segs.length;i++){
      var s=segs[i];placed=false;
      for(gi=0;gi<groups.length;gi++){
        g=groups[gi];
        if(norm(cross(s.d,g.d))>1e-6)continue;                 // not parallel
        if(distToLine(s.A,g.q,g.d)>TOL)continue;               // parallel but offset
        if(distToLine(s.B,g.q,g.d)>TOL)continue;
        g.segs.push(s);placed=true;break;
      }
      if(!placed)groups.push({q:s.A,d:s.d,segs:[s]});
    }
    for(gi=0;gi<groups.length;gi++){
      g=groups[gi];
      var ev=[],k;
      for(k=0;k<g.segs.length;k++){
        var sg=g.segs[k];
        var tA=dot(sg.A,g.d),tB=dot(sg.B,g.d);
        var w=(tB>tA)?1:-1;
        ev.push({t:Math.min(tA,tB),w:w});
        ev.push({t:Math.max(tA,tB),w:-w});
      }
      ev.sort(function(x,y){return x.t-y.t;});
      var run=0,p2=0;
      while(p2<ev.length){
        var t0=ev[p2].t;
        while(p2<ev.length&&ev[p2].t-t0<=TOL){run+=ev[p2].w;p2++;}
        // Between this cluster of events and the next distinct one, coverage is `run`. On a
        // closed surface forward and backward traversals cancel, so anything else is a real hole.
        if(run!==0&&p2<ev.length&&ev[p2].t-t0>TOL)
          return {closed:false,manifold:false,corrupt:false,vol:loose.vol,groups:groups.length};
      }
      if(run!==0)return {closed:false,manifold:false,corrupt:false,vol:loose.vol,groups:groups.length};
    }
    return {closed:true,manifold:false,corrupt:false,vol:loose.vol,groups:groups.length};
  }
  // Path-based counterpart to bimBuildStairGeometry: computes numSteps/riserH from totalRise the
  // same way, builds the multi-flight solid, and -- when railings are requested -- adds a stepped
  // guard mesh on each side. Railing posts and rail segments never share a vertex with the stair
  // mesh or with each other (their centerlines meet, but their box corners are offset by
  // different local frames, so the boxes only ever touch, never fuse) -- so the whole railing is
  // really a union of separately-closed solids, not a single manifold to be booleaned. This
  // concatenates their already-welded raw faces with the stair's and re-welds coincident
  // vertices, rather than running everything through the CSG boolean kernel: a full boolean
  // union is for resolving true volumetric overlap (like the multi-segment wall-corner union
  // elsewhere in this file), and forcing dozens of flush, chained-collinear rail faces through
  // the BSP union produced corrupted, wildly-wrong-volume topology in testing -- a known weak
  // point of naive BSP CSG for many-way unions of non-overlapping touching solids, not something
  // worth working around with the wrong tool. Chained collinear rail segments are additionally
  // merged into single boxes before this (see bimBuildStairGuardMesh) so no redundant internal
  // cap faces are ever produced. The merged assembly is verified strict (bimMeshSanityCheck: a
  // proper closed manifold, every undirected edge shared by exactly two faces, and volume only
  // goes up) before being accepted; any failure falls back to the plain stair solid with a
  // console warning and a toast, per this project's fail-safe rule.
  function bimBuildStairPathGeometry(pathIn,width,baseY,totalRise,targetRiserH,treadD,landingLen,railings,railHeight){
    if(!(totalRise>0)||!(targetRiserH>0)||!(treadD>0))return {error:'Stair needs a positive rise, riser height, and tread depth'};
    if(!(landingLen>0))landingLen=width;
    var numSteps=Math.max(1,Math.round(totalRise/targetRiserH));
    var riserH=totalRise/numSteps;
    var res;
    try{res=bimBuildStairPathMesh(pathIn,width,baseY,numSteps,riserH,treadD,landingLen);}
    catch(eS){console.warn('[BIM] Stair path solid build failed: ',eS);return {error:'Stair build failed: '+(eS&&eS.message?eS.message:eS)};}
    if(res.error)return res;
    var mesh=res.mesh,layout=res.layout;
    if(!mesh||!mesh.f||mesh.f.length<4)return {error:'Stair produced an empty solid'};
    var stairCheck=bimMeshSanityCheck(mesh,true);
    if(!stairCheck.ok)return {error:'Stair produced an invalid solid (failed its own topology check)'};
    var railH=(railHeight>0)?railHeight:0.9;
    var railingsOk=false;
    if(railings){
      try{
        var raw=mesh.f.map(function(f){return f.map(function(idx){return mesh.v[idx];});});
        var sides=[1,-1],si,addedAny=false;
        for(si=0;si<sides.length;si++){
          var guard=bimBuildStairGuardMesh(layout,baseY,sides[si],railH,0.05,0.05);
          if(guard&&guard.mesh&&guard.mesh.f&&guard.mesh.f.length){
            var gm=guard.mesh;
            gm.f.forEach(function(gf){raw.push(gf.map(function(idx){return gm.v[idx];}));});
            addedAny=true;
          }
        }
        if(addedAny){
          // Each post and each (now collinear-merged) rail segment is its own independently
          // closed box -- none of them share a vertex with the stair mesh or with each other
          // (touching centerlines, not coincident corners), so the combined assembly is really a
          // union of disjoint watertight components. That makes full closure (every undirected
          // edge used exactly twice) the correct, expected invariant here -- not an aspiration to
          // relax -- so this is checked strict, same as the stair solid itself above.
          var merged=bimWeldMesh(raw);
          var mergedCheck=bimMeshSanityCheck(merged,true);
          if(mergedCheck.ok&&merged.f.length>mesh.f.length&&mergedCheck.vol>stairCheck.vol-1e-6){mesh=merged;railingsOk=true;}
          else console.warn('[BIM] Stair railing merge failed its sanity check, keeping stair without railings');
        }
      }catch(eR){
        console.warn('[BIM] Stair railing build failed, keeping stair without railings: ',eR);
      }
      if(!railingsOk)a3dToast('Railings could not be added to this stair (kept the stair solid)');
    }
    return {mesh:mesh,bim:{type:'stair',path:layout.path,width:width,baseY:baseY,numSteps:numSteps,riserH:riserH,treadD:treadD,landingLen:landingLen,totalRise:totalRise,totalRun:layout.finalRun,railings:railingsOk,railHeight:railingsOk?railH:null}};
  }
  function startStairTool(){
    closeDlg();
    bimEnterDraftingMode();
    var lvl=bimGetActiveLevel();
    A3D.sk={tool:'stair',pts:[],y:lvl.elev,on:null};
    a3dToast('Stair: click points to trace the centerline (turns become landings), press Enter to finish');
    paint();
  }
  function finishStair(){
    var sk=A3D.sk;
    if(!sk||sk.pts.length<2){a3dToast('Stair needs at least 2 points');A3D.sk=null;paint();return;}
    openStairDlg(sk.pts.slice(),sk.y);
  }
  function openStairDlg(path,baseY){
    closeDlg();
    var opts='',i;
    for(i=0;i<A3D.levels.length;i++)opts+='<option value="'+i+'">'+bimEsc(A3D.levels[i].name)+'</option>';
    var d=document.createElement('div');
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">Stair parameters</div>'+
      '<div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Width</label><input type="number" step="any" min="0.4" data-a3dp="w" value="1.0"></div>'+
      '<div class="a3d-dlgrow"><label>Target level</label><select data-a3dp="lvl">'+opts+'</select></div>'+
      '<div class="a3d-dlgrow"><label>Target riser height</label><input type="number" step="any" min="0.1" max="0.3" data-a3dp="rh" value="0.178"></div>'+
      '<div class="a3d-dlgrow"><label>Tread depth</label><input type="number" step="any" min="0.15" data-a3dp="td" value="0.28"></div>'+
      '<div class="a3d-dlgrow"><label>Landing size</label><input type="number" step="any" min="0.4" data-a3dp="ll" value="1.0"></div>'+
      '<div class="a3d-dlgrow"><label>Add railings</label><input type="checkbox" data-a3dp="rail"></div>'+
      '<div class="a3d-dlgrow" id="a3d-stairrhrow" style="display:none"><label>Railing height</label><input type="number" step="any" min="0.6" max="1.5" data-a3dp="railh" value="0.9"></div>'+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">OK</button></div>';
    el.root.appendChild(d);
    el.dlg=d;
    var wI=d.querySelector('[data-a3dp="w"]'),lvlI=d.querySelector('[data-a3dp="lvl"]'),rhI=d.querySelector('[data-a3dp="rh"]'),tdI=d.querySelector('[data-a3dp="td"]');
    var llI=d.querySelector('[data-a3dp="ll"]'),railI=d.querySelector('[data-a3dp="rail"]'),railhI=d.querySelector('[data-a3dp="railh"]');
    var railhRow=d.querySelector('#a3d-stairrhrow');
    function syncRail(){railhRow.style.display=railI.checked?'':'none';}
    railI.addEventListener('change',syncRail);
    syncRail();
    function submit(){
      var w=parseFloat(wI.value),targetLvl=A3D.levels[parseInt(lvlI.value,10)],rh=parseFloat(rhI.value),td=parseFloat(tdI.value);
      var ll=parseFloat(llI.value),railings=!!railI.checked,railh=parseFloat(railhI.value);
      var eb=document.getElementById('a3d-dlgerr');
      if(!isFinite(w)||w<0.4){eb.textContent='Width must be at least 0.4';return;}
      if(!targetLvl){eb.textContent='Pick a target level';return;}
      var totalRise=targetLvl.elev-baseY;
      if(!(totalRise>0)){eb.textContent='Target level must be above the current level';return;}
      if(!isFinite(rh)||rh<=0){eb.textContent='Riser height must be a positive number';return;}
      if(!isFinite(td)||td<=0){eb.textContent='Tread depth must be a positive number';return;}
      if(!isFinite(ll)||ll<0.4){eb.textContent='Landing size must be at least 0.4';return;}
      if(railings&&(!isFinite(railh)||railh<=0)){eb.textContent='Railing height must be a positive number';return;}
      closeDlg();
      A3D.sk=null;
      buildStairSolid(path,w,baseY,totalRise,rh,td,ll,targetLvl,railings,railh);
    }
    d.addEventListener('click',function(ev){
      var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;
      if(!b)return;
      if(b.getAttribute('data-a3dlg')==='ok')submit();else{closeDlg();A3D.sk=null;paint();}
    });
    d.addEventListener('keydown',function(ev){
      if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}
      else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();A3D.sk=null;paint();}
    });
    wI.focus();wI.select();
  }
  function buildStairSolid(path,width,baseY,totalRise,targetRiserH,treadD,landingLen,targetLvl,railings,railHeight){
    var res=bimBuildStairPathGeometry(path,width,baseY,totalRise,targetRiserH,treadD,landingLen,railings,railHeight);
    if(res.error){a3dToast(res.error);return null;}
    pushUndo();
    A3D.counts.stair=(A3D.counts.stair||0)+1;
    res.bim.levelId=A3D.activeLevel;
    res.bim.targetLevelId=targetLvl?targetLvl.id:null;
    var o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:'Stair_'+A3D.counts.stair,col:'#8a8f96',pos:[0,0,0],mesh:res.mesh,bim:res.bim,layer:A3D.activeLayer};
    A3D.objs.push(o);
    A3D.sel=o.id;A3D.sel2=null;A3D.selSet=[o.id];
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast(o.name+' created ('+res.bim.numSteps+' steps'+(res.bim.railings?', railings':'')+')');
    return o;
  }

