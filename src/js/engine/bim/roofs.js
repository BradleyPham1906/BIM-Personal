  // ---- __acad3dV12: Roof tool (tilted-plane roof from a footprint + pitch, sitting on top of the wall
  // height rather than at floor level) and Stair tool (straight-run stair, built as an explicit welded
  // face soup rather than chained CSG union -- CSG-unioning many stacked step boxes accumulates enough
  // floating-point drift to produce non-watertight results; the explicit construction avoids that). ----
  /* ---------- Straight-skeleton hip/gable roof solver (Phase 39) ----------
     Plan coords are (x,z), elevation is y. Footprint is forced CCW by shoelace,
     matching sketchCCW. The wavefront moves every edge inward at unit speed; a
     vertex therefore travels at u = (nL+nR)/(1+nL.nR), and the time at which a
     point is reached equals its perpendicular distance to its owning edge, so
     roof height is simply baseY + t*tan(pitch) and every face is planar. */
  function bimSkSub(a,b){return [a[0]-b[0],a[1]-b[1]];}
  function bimSkDot(a,b){return a[0]*b[0]+a[1]*b[1];}
  function bimSkCross(a,b){return a[0]*b[1]-a[1]*b[0];}
  function bimSkLen(a){return Math.sqrt(a[0]*a[0]+a[1]*a[1]);}
  function bimSkDist(a,b){return bimSkLen(bimSkSub(a,b));}
  function bimSkNorm(a){var l=bimSkLen(a);return l<1e-7?[0,0]:[a[0]/l,a[1]/l];}
  function bimSkShoelace(P){var A=0,i,j;for(i=0;i<P.length;i++){j=(i+1)%P.length;A+=P[i][0]*P[j][1]-P[j][0]*P[i][1];}return A/2;}
  function bimSkClean(poly){
    var P=[],i;
    for(i=0;i<poly.length;i++){
      var p=poly[i];
      if(!p||!isFinite(p[0])||!isFinite(p[1]))return null;
      if(P.length&&bimSkDist(P[P.length-1],p)<1e-9)continue;
      P.push([p[0],p[1]]);
    }
    while(P.length>1&&bimSkDist(P[0],P[P.length-1])<1e-9)P.pop();
    if(P.length<3)return P;
    if(bimSkShoelace(P)<0)P.reverse();
    return P;
  }
  function bimSkInPoly(pt,P){
    var inside=false,i,j,n=P.length;
    for(i=0,j=n-1;i<n;j=i++){
      var a=P[i],b=P[j];
      if(((a[1]>pt[1])!==(b[1]>pt[1]))&&(pt[0]<(b[0]-a[0])*(pt[1]-a[1])/(b[1]-a[1]+1e-30)+a[0]))inside=!inside;
    }
    return inside;
  }
  function bimSkVelocity(nL,nR){
    var den=1+bimSkDot(nL,nR);
    if(Math.abs(den)<1e-9)return null;
    return [(nL[0]+nR[0])/den,(nL[1]+nR[1])/den];
  }
  function bimSkVertex(p,t,edgeL,edgeR,seq){
    var uRaw=bimSkVelocity(edgeL.n,edgeR.n);
    return {id:seq,p:[p[0],p[1]],t:t,edgeL:edgeL,edgeR:edgeR,u:uRaw||[0,0],
      stationary:!uRaw,reflex:bimSkCross(edgeL.d,edgeR.d)<-1e-12,valid:true,prev:null,next:null};
  }
  function bimSkEdgeEvent(a,b){
    if(a.stationary&&b.stationary)return null;
    var pa=[a.p[0]-a.u[0]*a.t,a.p[1]-a.u[1]*a.t];
    var pb=[b.p[0]-b.u[0]*b.t,b.p[1]-b.u[1]*b.t];
    var du=bimSkSub(a.u,b.u),dp=bimSkSub(pb,pa),dd=bimSkDot(du,du);
    if(dd<1e-14)return null;
    var t=bimSkDot(dp,du)/dd;
    if(!isFinite(t))return null;
    var pt=[pa[0]+a.u[0]*t,pa[1]+a.u[1]*t];
    if(bimSkDist(pt,[pb[0]+b.u[0]*t,pb[1]+b.u[1]*t])>1e-6)return null;
    if(t<Math.max(a.t,b.t)-1e-9)return null;
    return {t:t,p:pt};
  }
  function bimSkSplitEvent(v,e,P){
    if(v.stationary)return null;
    var den=1+bimSkDot(e.n,v.u);
    if(Math.abs(den)<1e-9)return null;
    var p0=[v.p[0]-v.u[0]*v.t,v.p[1]-v.u[1]*v.t];
    var t=bimSkDot(e.n,bimSkSub(e.a,p0))/den;
    if(!isFinite(t)||t<v.t+1e-9)return null;
    var B=[p0[0]+v.u[0]*t,p0[1]+v.u[1]*t];
    var sA=bimSkDot([e.uA[0]*t,e.uA[1]*t],e.d);
    var sB=bimSkDot(bimSkSub([e.b[0]+e.uB[0]*t,e.b[1]+e.uB[1]*t],e.a),e.d);
    var lo=Math.min(sA,sB),hi=Math.max(sA,sB),s=bimSkDot(bimSkSub(B,e.a),e.d);
    if(s<lo-1e-6||s>hi+1e-6)return null;
    if(!bimSkInPoly(B,P))return null;
    return {t:t,p:B};
  }
  function bimSkelSolve(polyIn){
    var P=bimSkClean(polyIn);
    if(!P)return {error:'Footprint contains a non-finite coordinate'};
    var n=P.length;
    if(n<3)return {error:'Footprint needs at least 3 distinct points'};
    var i,seq=0,edges=[];
    for(i=0;i<n;i++){
      var a=P[i],b=P[(i+1)%n],d=bimSkNorm(bimSkSub(b,a));
      if(bimSkLen(d)<0.5)return {error:'Footprint has a zero-length edge'};
      edges.push({idx:i,a:a,b:b,d:d,n:[-d[1],d[0]],left:[],right:[]});
    }
    for(i=0;i<n;i++){
      var eL=edges[(i-1+n)%n],eR=edges[i];
      var u0=bimSkVelocity(eL.n,eR.n)||[0,0];
      eR.uA=u0;eL.uB=u0;
    }
    var verts=[];
    for(i=0;i<n;i++)verts.push(bimSkVertex(P[i],0,edges[(i-1+n)%n],edges[i],seq++));
    for(i=0;i<n;i++){verts[i].prev=verts[(i-1+n)%n];verts[i].next=verts[(i+1)%n];}
    for(i=0;i<n;i++){
      verts[i].edgeL.left.push({p:verts[i].p,t:0});
      verts[i].edgeR.right.push({p:verts[i].p,t:0});
    }
    var queue=[];
    function pushEvents(v){
      if(!v.valid)return;
      var ee=bimSkEdgeEvent(v,v.next);
      if(ee)queue.push({kind:'edge',t:ee.t,p:ee.p,a:v,b:v.next});
      if(v.reflex){
        for(var k=0;k<edges.length;k++){
          var e=edges[k];
          if(e===v.edgeL||e===v.edgeR)continue;
          var se=bimSkSplitEvent(v,e,P);
          if(se)queue.push({kind:'split',t:se.t,p:se.p,a:v,e:e});
        }
      }
    }
    for(i=0;i<n;i++)pushEvents(verts[i]);
    function emit(v,pt,t){v.edgeL.left.push({p:pt,t:t});v.edgeR.right.push({p:pt,t:t});}
    function posAt(v,t){var dt=t-v.t;if(dt<0)dt=0;return [v.p[0]+v.u[0]*dt,v.p[1]+v.u[1]*dt];}
    function lavList(start){var out=[],x=start,g=0;do{out.push(x);x=x.next;}while(x&&x!==start&&g++<10000);return out;}
    function lavSize(start){return lavList(start).length;}
    function closeLav(start,t){
      var L=lavList(start),k;
      for(k=0;k<L.length;k++){if(!L[k].valid)continue;emit(L[k],posAt(L[k],t),t);L[k].valid=false;}
    }
    var degenTol=Math.max(1e-9,Math.abs(bimSkShoelace(P))*1e-9);
    function lavDegenerate(start,t){
      var L=lavList(start),k,A=0;
      if(L.length<2)return true;
      for(k=0;k<L.length;k++){
        var a2=posAt(L[k],t),b2=posAt(L[(k+1)%L.length],t);
        A+=a2[0]*b2[1]-b2[0]*a2[1];
      }
      return Math.abs(A/2)<degenTol;
    }
    var guard=0,maxIter=8*n*n+200;
    while(queue.length&&guard++<maxIter){
      var bi=-1,bt=Infinity;
      for(i=0;i<queue.length;i++)if(queue[i].t<bt){bt=queue[i].t;bi=i;}
      if(bi<0)break;
      var ev=queue.splice(bi,1)[0];
      if(!ev.a.valid)continue;
      if(ev.kind==='edge'&&(!ev.b.valid||ev.a.next!==ev.b))continue;
      if(ev.kind==='split'){
        /* A split divides one wavefront loop in two, which pinches the struck
           edge's face into a boundary that the two-chain reconstruction below
           cannot represent. Refuse rather than emit a subtly wrong roof; the
           caller falls back to the single-plane shed roof. */
        return {error:'Footprint has a deep notch or slot that the hip solver does not handle'};
      }
      var chain=[ev.a,ev.b],grew=true;
      while(grew){
        grew=false;
        for(i=queue.length-1;i>=0;i--){
          var q=queue[i];
          if(q.kind!=='edge'||!q.a.valid||!q.b.valid)continue;
          if(Math.abs(q.t-ev.t)>1e-6||bimSkDist(q.p,ev.p)>1e-6)continue;
          var head=chain[0],tail=chain[chain.length-1];
          if(q.b===head){chain.unshift(q.a);queue.splice(i,1);grew=true;}
          else if(q.a===tail){chain.push(q.b);queue.splice(i,1);grew=true;}
          else if(chain.indexOf(q.a)>=0&&chain.indexOf(q.b)>=0){queue.splice(i,1);}
        }
      }
      if(chain.length>=lavSize(ev.a)||chain[0]===chain[chain.length-1]){
        closeLav(ev.a,ev.t);
        continue;
      }
      for(i=0;i<chain.length;i++){emit(chain[i],ev.p,ev.t);chain[i].valid=false;}
      var first=chain[0],last=chain[chain.length-1];
      var nv=bimSkVertex(ev.p,ev.t,first.edgeL,last.edgeR,seq++);
      nv.prev=first.prev;nv.next=last.next;
      if(nv.prev)nv.prev.next=nv;
      if(nv.next)nv.next.prev=nv;
      if(lavSize(nv)<=2){closeLav(nv,ev.t);continue;}
      pushEvents(nv);
      if(nv.prev)pushEvents(nv.prev);
      /* A rectilinear plan drives the wavefront to a zero-area ridge tree that
         can generate no further events. That state is the terminal event. */
      if(nv.valid&&lavDegenerate(nv,ev.t))closeLav(nv,ev.t);
    }
    var stack=verts.slice(),seen={},g2=0,alive=false;
    while(stack.length&&g2++<20000){
      var q2=stack.pop();
      if(!q2||seen[q2.id])continue;
      seen[q2.id]=1;
      if(q2.valid)alive=true;
      if(q2.next)stack.push(q2.next);
      if(q2.prev)stack.push(q2.prev);
    }
    if(alive)return {error:'Straight skeleton did not converge for this footprint'};
    var faces=[];
    for(i=0;i<edges.length;i++){
      var e2=edges[i];
      if(!e2.right.length||!e2.left.length)return {error:'Skeleton face '+i+' is incomplete'};
      var seqPts=[e2.right[0]],a3,b3;
      for(a3=0;a3<e2.left.length;a3++)seqPts.push(e2.left[a3]);
      for(b3=e2.right.length-1;b3>=1;b3--)seqPts.push(e2.right[b3]);
      var out=[],c3;
      for(c3=0;c3<seqPts.length;c3++){
        if(out.length&&bimSkDist(out[out.length-1].p,seqPts[c3].p)<1e-7)continue;
        out.push(seqPts[c3]);
      }
      while(out.length>1&&bimSkDist(out[0].p,out[out.length-1].p)<1e-7)out.pop();
      if(out.length<3)continue;
      faces.push({edge:i,pts:out});
    }
    if(!faces.length)return {error:'Skeleton produced no roof faces'};
    return {poly:P,edges:edges,faces:faces};
  }
  /* A skeleton node can land partway along a neighbouring face's edge, leaving a
     T-junction that makes the solid non-manifold and breaks the BSP CSG. Split any
     edge another vertex lies on, then fan that face (a triangle or quad with extra
     collinear points on its edges stays convex, so a fan is safe). */
  function bimSkelRepairT(v,f){
    var i,j,k,out=[],changed=0;
    for(i=0;i<f.length;i++){
      var face=f[i],ring=[],grew=false;
      for(j=0;j<face.length;j++){
        var ia=face[j],ib=face[(j+1)%face.length];
        ring.push(ia);
        var a=v[ia],b=v[ib];
        var dx=b[0]-a[0],dy=b[1]-a[1],dz=b[2]-a[2],L2=dx*dx+dy*dy+dz*dz;
        if(L2<1e-18)continue;
        var hits=[];
        for(k=0;k<v.length;k++){
          if(k===ia||k===ib)continue;
          var p=v[k];
          var t=((p[0]-a[0])*dx+(p[1]-a[1])*dy+(p[2]-a[2])*dz)/L2;
          if(t<=1e-9||t>=1-1e-9)continue;
          var ex=a[0]+dx*t-p[0],ey=a[1]+dy*t-p[1],ez=a[2]+dz*t-p[2];
          if(ex*ex+ey*ey+ez*ez>1e-14)continue;
          hits.push({t:t,i:k});
        }
        if(!hits.length)continue;
        hits.sort(function(x,y){return x.t-y.t;});
        for(k=0;k<hits.length;k++)ring.push(hits[k].i);
        grew=true;
      }
      if(!grew){out.push(face);continue;}
      changed++;
      for(j=1;j+1<ring.length;j++)out.push([ring[0],ring[j],ring[j+1]]);
    }
    return out;
  }
  function bimBuildHipRoofMesh(footprint,baseY,pitchDeg,thickness,gableEdges){
    var sol=bimSkelSolve(footprint);
    if(sol.error)return {error:sol.error};
    var P=sol.poly,n=P.length,i;
    var tan=Math.tan(pitchDeg*Math.PI/180);
    var faces=sol.faces.map(function(fc){
      return {edge:fc.edge,pts:fc.pts.map(function(q){return {p:[q.p[0],q.p[1]],t:q.t};})};
    });
    function k2(p){return p[0].toFixed(6)+'|'+p[1].toFixed(6);}
    var inserts={};
    if(gableEdges&&gableEdges.length){
      var moved={},gset={};
      gableEdges.forEach(function(gi){if(gi>=0&&gi<n)gset[gi]=1;});
      Object.keys(gset).forEach(function(giS){
        var gi=+giS,e=sol.edges[gi],face=null;
        faces.forEach(function(fc){if(fc.edge===gi)face=fc;});
        if(!face)return;
        face.pts.forEach(function(q){
          if(q.t<=1e-9)return;
          var k=k2(q.p);
          if(moved[k])return;
          var s=(q.p[0]-e.a[0])*e.d[0]+(q.p[1]-e.a[1])*e.d[1];
          moved[k]={to:[e.a[0]+e.d[0]*s,e.a[1]+e.d[1]*s],t:q.t,edge:gi,s:s};
        });
      });
      faces.forEach(function(fc){
        fc.pts.forEach(function(q){
          var m2=moved[k2(q.p)];
          if(m2)q.p=[m2.to[0],m2.to[1]];
        });
      });
      Object.keys(moved).forEach(function(k){
        var m2=moved[k];
        (inserts[m2.edge]=inserts[m2.edge]||[]).push({s:m2.s,p:m2.to,t:m2.t});
      });
      faces=faces.filter(function(fc){
        var o2=[],z;
        for(z=0;z<fc.pts.length;z++){
          if(o2.length&&bimSkDist(o2[o2.length-1].p,fc.pts[z].p)<1e-7)continue;
          o2.push(fc.pts[z]);
        }
        while(o2.length>1&&bimSkDist(o2[0].p,o2[o2.length-1].p)<1e-7)o2.pop();
        fc.pts=o2;
        if(o2.length<3)return false;
        var A=0;
        for(z=0;z<o2.length;z++){
          var a4=o2[z].p,b4=o2[(z+1)%o2.length].p;
          A+=a4[0]*b4[1]-b4[0]*a4[1];
        }
        return Math.abs(A/2)>1e-9;
      });
      if(!faces.length)return {error:'Every roof face was consumed by the gable settings'};
    }
    var v=[],vmap={},f=[];
    function vid(p){
      var k=p[0].toFixed(6)+'|'+p[1].toFixed(6)+'|'+p[2].toFixed(6);
      if(vmap[k]===undefined){vmap[k]=v.length;v.push(p);}
      return vmap[k];
    }
    function hOf(t){return baseY+t*tan;}
    faces.forEach(function(fc){
      var ring2=fc.pts.map(function(q){return q.p;});
      var tris=earClip(ring2);
      if(!tris.length)return;
      var top=fc.pts.map(function(q){return vid([q.p[0],hOf(q.t),q.p[1]]);});
      var bot=fc.pts.map(function(q){return vid([q.p[0],hOf(q.t)-thickness,q.p[1]]);});
      tris.forEach(function(t3){f.push([top[t3[2]],top[t3[1]],top[t3[0]]]);});
      tris.forEach(function(t3){f.push([bot[t3[0]],bot[t3[1]],bot[t3[2]]]);});
    });
    var per=[];
    for(i=0;i<n;i++){
      per.push({p:P[i],t:0});
      var ins=inserts[i];
      if(ins&&ins.length){
        ins.sort(function(a5,b5){return a5.s-b5.s;});
        ins.forEach(function(q){per.push({p:q.p,t:q.t});});
      }
    }
    var perC=[];
    for(i=0;i<per.length;i++){
      if(perC.length&&bimSkDist(perC[perC.length-1].p,per[i].p)<1e-7)continue;
      perC.push(per[i]);
    }
    while(perC.length>1&&bimSkDist(perC[0].p,perC[perC.length-1].p)<1e-7)perC.pop();
    var m=perC.length;
    var pt2=perC.map(function(q){return vid([q.p[0],hOf(q.t),q.p[1]]);});
    var pb2=perC.map(function(q){return vid([q.p[0],hOf(q.t)-thickness,q.p[1]]);});
    for(i=0;i<m;i++){
      var j2=(i+1)%m;
      f.push([pt2[i],pt2[j2],pb2[j2],pb2[i]]);
    }
    if(!f.length)return {error:'Roof produced an empty solid'};
    return {mesh:{v:v,f:bimSkelRepairT(v,f)}};
  }
  function bimBuildRoofMesh(footprint,baseY,pitchDeg,slopeDirDeg,thickness){
    var P=sketchCCW(footprint.slice());
    var n=P.length;
    if(n<3)return null;
    var rad=pitchDeg*Math.PI/180;
    var slopeRad=slopeDirDeg*Math.PI/180;
    var dirX=Math.cos(slopeRad),dirZ=Math.sin(slopeRad);
    var i,minProj=Infinity;
    for(i=0;i<n;i++){var proj=P[i][0]*dirX+P[i][1]*dirZ;if(proj<minProj)minProj=proj;}
    var topY=[];
    for(i=0;i<n;i++){var proj=P[i][0]*dirX+P[i][1]*dirZ;topY.push(baseY+(proj-minProj)*Math.tan(rad));}
    var v=[],f=[];
    for(i=0;i<n;i++)v.push([P[i][0],topY[i],P[i][1]]);
    for(i=0;i<n;i++)v.push([P[i][0],topY[i]-thickness,P[i][1]]);
    var tris=earClip(P);
    for(i=0;i<tris.length;i++)f.push([tris[i][2],tris[i][1],tris[i][0]]);
    for(i=0;i<tris.length;i++)f.push([tris[i][0]+n,tris[i][1]+n,tris[i][2]+n]);
    /* Side walls: indices 0..n-1 are the TOP ring here (padMesh is the other way
       round), so the outward winding is top_i, top_j, bot_j, bot_i. The previous
       [j,i,i+n,j+n] matched padMesh's bottom-first order and inverted every fascia
       normal, giving the shed roof 24 duplicated half-edges and a negative signed
       volume. Verified in-browser: signed volume goes -22.53 -> +40.00. */
    for(i=0;i<n;i++){var j=(i+1)%n;f.push([i,j,j+n,i+n]);}
    return {v:v,f:f};
  }
  function bimBuildRoofGeometry(footprint,baseY,pitchDeg,slopeDirDeg,thickness,opts){
    var m,warn=null;
    var style=(opts&&opts.style)||'shed';
    var gables=(opts&&opts.gables)?opts.gables.slice():[];
    if(style==='hip'||style==='gable'){
      var hr=null;
      try{hr=bimBuildHipRoofMesh(footprint,baseY,pitchDeg,thickness,style==='gable'?gables:[]);}
      catch(eH){hr={error:'Hip solver threw: '+(eH&&eH.message?eH.message:eH)};}
      if(hr&&hr.mesh&&hr.mesh.f&&hr.mesh.f.length>=4){
        return {mesh:hr.mesh,bim:{type:'roof',footprint:footprint.slice(),baseY:baseY,pitch:pitchDeg,slopeDir:slopeDirDeg,thickness:thickness,style:style,gables:gables}};
      }
      warn=(hr&&hr.error)?hr.error:'Hip solver produced no solid';
      console.warn('[BIM] '+style+' roof failed, falling back to single-plane roof: '+warn);
      style='shed';
      gables=[];
    }
    try{m=bimBuildRoofMesh(footprint,baseY,pitchDeg,slopeDirDeg,thickness);}
    catch(eR){console.warn('[BIM] Roof solid build failed: ',eR);return {error:'Roof build failed: '+(eR&&eR.message?eR.message:eR)};}
    if(!m||!m.f||m.f.length<4)return {error:'Roof produced an empty solid: check the source footprint'};
    return {mesh:m,warning:warn,bim:{type:'roof',footprint:footprint.slice(),baseY:baseY,pitch:pitchDeg,slopeDir:slopeDirDeg,thickness:thickness,style:'shed',gables:[]}};
  }
  function bimFindRoofBoundaryAt(pt,y0){
    var b=bimFindRoomBoundaryAt(pt,y0);
    if(!b)return null;
    b.roofBaseY=b.y+(b.wallHeight||0);
    return b;
  }
  function startRoofTool(){
    closeDlg();
    bimEnterDraftingMode();
    var lvl=bimGetActiveLevel();
    A3D.sk={tool:'roof',pts:[],y:lvl.elev,on:null};
    a3dToast('Roof: click inside an enclosed wall loop or closed sketch on '+lvl.name);
    paint();
  }
  function openRoofDlg(boundary){
    closeDlg();
    /* Edge indices must match the solver's own cleaned CCW ordering, so derive
       the label list from bimSkClean rather than the raw boundary points. */
    var GP=bimSkClean(boundary.pts)||[],gableHtml='',gi;
    for(gi=0;gi<GP.length;gi++){
      var ga=GP[gi],gb=GP[(gi+1)%GP.length];
      var glen=Math.sqrt((gb[0]-ga[0])*(gb[0]-ga[0])+(gb[1]-ga[1])*(gb[1]-ga[1]));
      gableHtml+='<label style="display:block"><input type="checkbox" data-gable="'+gi+'"> Edge '+(gi+1)+' ('+glen.toFixed(2)+' m)</label>';
    }
    var d=document.createElement('div');
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">Roof parameters</div>'+
      '<div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Style</label><select data-a3dp="style">'+
        '<option value="shed">Shed (single plane)</option>'+
        '<option value="hip">Hip</option>'+
        '<option value="gable">Gable</option>'+
      '</select></div>'+
      '<div class="a3d-dlgrow"><label>Pitch (degrees)</label><input type="number" step="any" min="0" max="80" data-a3dp="pitch" value="20"></div>'+
      '<div class="a3d-dlgrow" id="a3d-roofdirrow"><label>Slope direction (deg)</label><input type="number" step="any" data-a3dp="dir" value="0"></div>'+
      '<div class="a3d-dlgrow"><label>Thickness</label><input type="number" step="any" min="0.02" data-a3dp="thk" value="0.2"></div>'+
      '<div id="a3d-roofgables" style="display:none;max-height:120px;overflow:auto;margin:4px 0;padding:4px;border:1px solid #35393d">'+
        '<div style="opacity:.7;margin-bottom:3px">Gable ends</div>'+gableHtml+'</div>'+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">OK</button></div>';
    el.root.appendChild(d);
    el.dlg=d;
    var pI=d.querySelector('[data-a3dp="pitch"]'),dI=d.querySelector('[data-a3dp="dir"]'),tI=d.querySelector('[data-a3dp="thk"]');
    var sI=d.querySelector('[data-a3dp="style"]');
    var gBox=d.querySelector('#a3d-roofgables'),dRow=d.querySelector('#a3d-roofdirrow');
    function syncStyle(){
      var st=sI.value;
      if(gBox)gBox.style.display=(st==='gable')?'block':'none';
      if(dRow)dRow.style.display=(st==='shed')?'':'none';
    }
    sI.addEventListener('change',syncStyle);
    syncStyle();
    function submit(){
      var pitch=parseFloat(pI.value),dir=parseFloat(dI.value),thk=parseFloat(tI.value);
      var eb=document.getElementById('a3d-dlgerr');
      if(!isFinite(pitch)||pitch<0||pitch>=90){eb.textContent='Pitch must be between 0 and 90 degrees';return;}
      if(!isFinite(dir)){eb.textContent='Slope direction must be a number';return;}
      if(!isFinite(thk)||thk<=0){eb.textContent='Thickness must be a positive number';return;}
      var style=sI.value,gables=[];
      if(style==='gable'){
        var cbs=d.querySelectorAll('[data-gable]'),ci;
        for(ci=0;ci<cbs.length;ci++)if(cbs[ci].checked)gables.push(parseInt(cbs[ci].getAttribute('data-gable'),10));
        if(!gables.length){eb.textContent='Select at least one gable end, or choose Hip';return;}
        if(gables.length>=GP.length){eb.textContent='At least one edge must stay a sloped hip face';return;}
      }
      closeDlg();
      buildRoofSolid(boundary,pitch,dir,thk,{style:style,gables:gables});
    }
    d.addEventListener('click',function(ev){
      var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;
      if(!b)return;
      if(b.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();
    });
    d.addEventListener('keydown',function(ev){
      if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}
      else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}
    });
    pI.focus();pI.select();
  }
  function buildRoofSolid(boundary,pitchDeg,slopeDirDeg,thickness,opts){
    var res=bimBuildRoofGeometry(boundary.pts,boundary.roofBaseY,pitchDeg,slopeDirDeg,thickness,opts);
    if(res.error){a3dToast(res.error);return null;}
    if(res.warning)a3dToast('Fell back to a single-plane roof: '+res.warning);
    pushUndo();
    A3D.counts.roof=(A3D.counts.roof||0)+1;
    res.bim.levelId=A3D.activeLevel;
    res.bim.sourceType=boundary.sourceType;
    res.bim.sourceId=boundary.sourceId;
    var o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:'Roof_'+A3D.counts.roof,col:'#a3766a',pos:[0,0,0],mesh:res.mesh,bim:res.bim,layer:A3D.activeLayer};
    if(boundary.region&&!boundary.sourceId){   /* __acad3dV99 */
      o.region=bimCloneRegion(boundary.region);o.sourceType=boundary.sourceType;o.sourceId=null;
    }
    A3D.objs.push(o);
    A3D.sel=o.id;A3D.sel2=null;A3D.selSet=[o.id];
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast(o.name+' created ('+(res.bim.style||'shed')+', '+pitchDeg+'\u00b0 pitch)');
    return o;
  }
  function bimRebuildRoof(o,newPitch,newDir,newThickness,newStyle){
    if(!o||!o.bim||o.bim.type!=='roof'||!o.bim.footprint)return false;
    var rStyle=newStyle||o.bim.style||'shed';
    var res=bimBuildRoofGeometry(o.bim.footprint,o.bim.baseY,newPitch,newDir,newThickness,
      {style:rStyle,gables:o.bim.gables||[]});
    if(res.error){a3dToast(res.error);return false;}
    if(res.warning)a3dToast('Fell back to a single-plane roof: '+res.warning);
    pushUndo();
    res.bim.levelId=o.bim.levelId;
    res.bim.sourceType=o.bim.sourceType;
    res.bim.sourceId=o.bim.sourceId;
    o.mesh=res.mesh;
    o.bim=res.bim;
    refreshTree();paint();saveSoon();
    a3dToast(o.name+' updated');
    return true;
  }
  function bimWeldMesh(rawFaces){
    var vm={},verts=[],faces=[],i,j;
    function vid(p){
      var k=p[0].toFixed(5)+','+p[1].toFixed(5)+','+p[2].toFixed(5);
      if(vm[k]===undefined){vm[k]=verts.length;verts.push(p);}
      return vm[k];
    }
    for(i=0;i<rawFaces.length;i++){
      var f=[];
      for(j=0;j<rawFaces[i].length;j++)f.push(vid(rawFaces[i][j]));
      faces.push(f);
    }
    return {v:verts,f:faces};
  }
  function bimBuildStairMesh(startXZ,dirXZ,width,baseY,numSteps,riserH,treadD){
    var nx=-dirXZ[1],nz=dirXZ[0],hw=width/2;
    function pt(run,rise,side){
      var px=startXZ[0]+dirXZ[0]*run,pz=startXZ[1]+dirXZ[1]*run;
      return [px+nx*hw*side,baseY+rise,pz+nz*hw*side];
    }
    var raw=[],i,sd;
    var maxRun=numSteps*treadD,maxRise=numSteps*riserH;
    for(sd=-1;sd<=1;sd+=2){
      for(i=0;i<numSteps;i++){
        var runA=i*treadD,runB=(i+1)*treadD,riseHere=(i+1)*riserH,risePrev=i*riserH;
        var bl=pt(runA,0,sd),br=pt(runB,0,sd),tr=pt(runB,riseHere,sd),tl=pt(runA,riseHere,sd);
        if(i===0){
          if(sd<0){raw.push([bl,br,tr]);raw.push([bl,tr,tl]);}
          else{raw.push([bl,tr,br]);raw.push([bl,tl,tr]);}
        }else{
          var ml=pt(runA,risePrev,sd);
          if(sd<0){raw.push([bl,br,tr]);raw.push([bl,tr,ml]);raw.push([ml,tr,tl]);}
          else{raw.push([bl,tr,br]);raw.push([bl,ml,tr]);raw.push([ml,tl,tr]);}
        }
      }
    }
    for(i=0;i<numSteps;i++){
      var runA3=i*treadD,runB3=(i+1)*treadD;
      raw.push([pt(runA3,0,-1),pt(runB3,0,-1),pt(runB3,0,1),pt(runA3,0,1)]);
    }
    for(i=0;i<numSteps;i++){
      var runA2=i*treadD,runB2=(i+1)*treadD,riseHere2=(i+1)*riserH,risePrev2=i*riserH;
      raw.push([pt(runA2,riseHere2,-1),pt(runB2,riseHere2,-1),pt(runB2,riseHere2,1),pt(runA2,riseHere2,1)]);
      raw.push([pt(runA2,risePrev2,-1),pt(runA2,riseHere2,-1),pt(runA2,riseHere2,1),pt(runA2,risePrev2,1)]);
    }
    raw.push([pt(maxRun,0,-1),pt(maxRun,maxRise,-1),pt(maxRun,maxRise,1),pt(maxRun,0,1)]);
    return bimWeldMesh(raw);
  }
  function bimBuildStairGeometry(startXZ,dirXZ,width,baseY,totalRise,targetRiserH,treadD){
    if(!(totalRise>0)||!(targetRiserH>0)||!(treadD>0))return {error:'Stair needs a positive rise, riser height, and tread depth'};
    var numSteps=Math.max(1,Math.round(totalRise/targetRiserH));
    var riserH=totalRise/numSteps;
    var m;
    try{m=bimBuildStairMesh(startXZ,dirXZ,width,baseY,numSteps,riserH,treadD);}
    catch(eS){console.warn('[BIM] Stair solid build failed: ',eS);return {error:'Stair build failed: '+(eS&&eS.message?eS.message:eS)};}
    if(!m||!m.f||m.f.length<4)return {error:'Stair produced an empty solid'};
    return {mesh:m,bim:{type:'stair',start:startXZ,dir:dirXZ,width:width,baseY:baseY,numSteps:numSteps,riserH:riserH,treadD:treadD,totalRise:totalRise,totalRun:numSteps*treadD}};
  }
