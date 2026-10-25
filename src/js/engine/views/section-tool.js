  // ---- __acad3dV15/16: Section tool. Non-destructive: cuts are computed fresh into a per-object
  // cache and never touch A3D.objs' own mesh data.
  // NOTE ON APPROACH: the first implementation used csgIntersect against a large half-space box,
  // reusing the existing CSG kernel. Testing found it does NOT reliably produce a watertight cap
  // when a solid is cut through its middle (confirmed via 8+ controlled variations -- box size,
  // rotation, cut position, argument order -- all produced 10-12 unmatched edges on a simple box
  // cut). The pre-existing wall-opening subtract avoids this because it cuts a small, fully-
  // contained box out of a wall, which is structurally different from bisecting a solid. This is
  // a direct single-plane clip instead: classify each triangle against the cutting plane, split
  // the straddling ones directly (bimClipTriangle), chain the resulting boundary edges into
  // closed loop(s) (bimChainEdgesToLoops -- handles multiple disjoint loops naturally, e.g. a
  // wall interrupted by another object at the cut height), and cap each loop by projecting to 2D
  // and triangulating (bimCapLoop). Verified watertight on the exact case that broke the CSG
  // approach, plus a 17-step stair mesh and a genuine multi-loop case -- 16/16 tests. ----
  function bimClipTriangle(A,B,C,dA,dB,dC){
    var pts=[A,B,C],ds=[dA,dB,dC];
    var keep=[ds[0]>=-1e-7,ds[1]>=-1e-7,ds[2]>=-1e-7];
    var numKeep=(keep[0]?1:0)+(keep[1]?1:0)+(keep[2]?1:0);
    if(numKeep===3)return {kept:[[A,B,C]],cutEdge:null};
    if(numKeep===0)return {kept:[],cutEdge:null};
    var outPts=[],intersections=[],i;
    for(i=0;i<3;i++){
      var j=(i+1)%3;
      var pi=pts[i],pj=pts[j],di=ds[i],dj=ds[j];
      if(keep[i])outPts.push(pi);
      if(keep[i]!==keep[j]){
        var t=di/(di-dj);
        var ip=[pi[0]+(pj[0]-pi[0])*t,pi[1]+(pj[1]-pi[1])*t,pi[2]+(pj[2]-pi[2])*t];
        outPts.push(ip);
        intersections.push(ip);
      }
    }
    var tris=[];
    for(i=1;i<outPts.length-1;i++)tris.push([outPts[0],outPts[i],outPts[i+1]]);
    var cutEdge=(intersections.length===2)?[intersections[0],intersections[1]]:null;
    return {kept:tris,cutEdge:cutEdge};
  }
  function bimChainEdgesToLoops(edges){
    function keyOf(p){return p[0].toFixed(4)+','+p[1].toFixed(4)+','+p[2].toFixed(4);}
    function edgeKey(a,b){return a<b?a+'|'+b:b+'|'+a;}
    var pointByKey={},adj={},i;
    for(i=0;i<edges.length;i++){
      var k1=keyOf(edges[i][0]),k2=keyOf(edges[i][1]);
      if(k1===k2)continue;
      pointByKey[k1]=edges[i][0];pointByKey[k2]=edges[i][1];
      if(!adj[k1])adj[k1]=[];
      if(!adj[k2])adj[k2]=[];
      adj[k1].push(k2);
      adj[k2].push(k1);
    }
    var usedEdge={},loops=[];
    var allKeys=Object.keys(adj),ki;
    for(ki=0;ki<allKeys.length;ki++){
      var startKey=allKeys[ki];
      var neighbors=adj[startKey],ni;
      for(ni=0;ni<neighbors.length;ni++){
        var ek=edgeKey(startKey,neighbors[ni]);
        if(usedEdge[ek])continue;
        var loop=[startKey];
        var current=startKey,next=neighbors[ni];
        usedEdge[edgeKey(current,next)]=true;
        var guard=0;
        while(next!==startKey&&guard++<10000){
          loop.push(next);
          var nextNeighbors=adj[next],found=null,nj;
          for(nj=0;nj<nextNeighbors.length;nj++){
            var ek2=edgeKey(next,nextNeighbors[nj]);
            if(!usedEdge[ek2]){found=nextNeighbors[nj];usedEdge[ek2]=true;break;}
          }
          if(found===null)break;
          current=next;next=found;
        }
        if(next===startKey&&loop.length>=3)loops.push(loop.map(function(k){return pointByKey[k];}));
      }
    }
    return loops;
  }
  function bimCapLoop(loop3D,normal){
    if(loop3D.length<3)return [];
    var n=normal;
    var arbitrary=Math.abs(n[0])<0.9?[1,0,0]:[0,1,0];
    var u=vnorm(vcross(arbitrary,n));
    var v=vcross(n,u);
    var pts2D=loop3D.map(function(p){return [vdot(p,u),vdot(p,v)];});
    var area=0,i;
    for(i=0;i<pts2D.length;i++){var j=(i+1)%pts2D.length;area+=pts2D[i][0]*pts2D[j][1]-pts2D[j][0]*pts2D[i][1];}
    var pts3=loop3D.slice(),pts2=pts2D.slice();
    if(area<0){pts3.reverse();pts2.reverse();}
    var tris=earClip(pts2);
    var out=[];
    for(i=0;i<tris.length;i++)out.push([pts3[tris[i][0]],pts3[tris[i][1]],pts3[tris[i][2]]]);
    return out;
  }
  function bimClipMeshToPlane(mesh,planeP,planeN){
    var kept=[],cutEdges=[],i,j;
    for(i=0;i<mesh.f.length;i++){
      var fc=mesh.f[i];
      var faceTris=[];
      for(j=2;j<fc.length;j++)faceTris.push([fc[0],fc[j-1],fc[j]]);
      var t;
      for(t=0;t<faceTris.length;t++){
        var tri=faceTris[t];
        var A=mesh.v[tri[0]],B=mesh.v[tri[1]],C=mesh.v[tri[2]];
        var dA=vdot(vsub(A,planeP),planeN),dB=vdot(vsub(B,planeP),planeN),dC=vdot(vsub(C,planeP),planeN);
        var res=bimClipTriangle(A,B,C,dA,dB,dC);
        kept=kept.concat(res.kept);
        if(res.cutEdge)cutEdges.push(res.cutEdge);
      }
    }
    var loops=bimChainEdgesToLoops(cutEdges);
    var capTris=[];
    for(i=0;i<loops.length;i++)capTris=capTris.concat(bimCapLoop(loops[i],planeN));
    return bimWeldMesh(kept.concat(capTris));
  }
  function bimComputeSectionCuts(P,dir,keepSign){
    var perp=[-dir[1],dir[0]];
    var planeN=[perp[0]*keepSign,0,perp[1]*keepSign];
    var cuts={},i;
    for(i=0;i<A3D.objs.length;i++){
      var o=A3D.objs[i];
      if(o.t!=='solid'||!o.mesh||!o.mesh.f||!o.mesh.f.length)continue;
      try{
        var localP=[P[0]-o.pos[0],0-o.pos[1],P[1]-o.pos[2]];
        cuts[o.id]=bimClipMeshToPlane(o.mesh,localP,planeN);
      }catch(eC){
        console.warn('[BIM] Section cut failed for object '+o.id+': ',eC);
      }
    }
    return cuts;
  }
  function startSectionTool(){
    closeDlg();
    if(A3D.sk)bimEndSketch();   /* __acad3dV100: the one starter that skips bimEnterDraftingMode */
    if(A3D.section)bimExitSection();
    var c0=A3D.cam;
    var origCam={yaw:c0.yaw,pitch:c0.pitch,dist:c0.dist,tx:c0.tx,ty:c0.ty,tz:c0.tz,flat:A3D.flat,view:A3D.view,
      record:{kind:A3D_VIEW.kind,id:A3D_VIEW.id}};   /* __acad3dV119: the view to come back to */
    if(!A3D.flat)toggleFlat();
    else if(!bimCameraIsPlan())bimActivateView('plan',null,{anim:false});   /* __acad3dV119: an elevation is flat too */
    var lvl=bimGetActiveLevel();
    A3D.sk={tool:'section',pts:[],y:lvl.elev,on:null,origCam:origCam};
    a3dToast('Section: click the start point, then click again to draw the cut line');
    paint();
  }
  function bimAimSectionCamera(){
    if(!A3D.section)return;
    var perp=[-A3D.section.dir[1],A3D.section.dir[0]];
    var viewDirX=-perp[0]*A3D.section.keepSign,viewDirZ=-perp[1]*A3D.section.keepSign;
    var yaw=Math.atan2(viewDirX,viewDirZ);
    var c=A3D.cam;
    c.yaw=yaw;c.pitch=0.02;
    A3D.flat=true;
    if(el.flip){el.flip.textContent='3D';el.flip.setAttribute('title','Go to 3D (>)');}
    if(el.root)el.root.classList.add('flat');
    fitScene();
    A3D.view='Section';
    refreshHud();
  }
  function bimEnterSection(P,dir,origCam){
    var keepSign=1;
    var cuts=bimComputeSectionCuts(P,dir,keepSign);
    A3D.section={p:P,dir:dir,keepSign:keepSign,cutMeshes:cuts,
      prevCam:origCam,prevFlat:origCam.flat,prevView:origCam.view,
      prevRecord:origCam.record||{kind:A3D_VIEW.kind,id:A3D_VIEW.id}};   /* __acad3dV119: the view it was cut from */
    bimAimSectionCamera();
    /* __acad3dV119: a section is a view. The HUD names it, and the Project Browser and Properties stop
       naming the plan it was drawn in. Opened as part of a saved view, the saved view records itself
       when its activation finishes. */
    if(A3D_VIEW.kind!=='sheet')bimSetActiveView('section',null,null);
    A3D.sel=null;A3D.sel2=null;A3D.selSet=[];
    refreshTree();paint();saveSoon();
    a3dToast('Section view active \u2014 use Flip Section to see the other side, Exit Section to return');
  }
  function bimFlipSection(){
    if(!A3D.section){a3dToast('No active section to flip');return;}
    A3D.section.keepSign=-A3D.section.keepSign;
    A3D.section.cutMeshes=bimComputeSectionCuts(A3D.section.p,A3D.section.dir,A3D.section.keepSign);
    bimAimSectionCamera();
    paint();saveSoon();
  }
  function bimExitSection(){
    if(!A3D.section)return;
    var prev=A3D.section.prevCam,prevFlat=A3D.section.prevFlat,prevView=A3D.section.prevView,
        rec=A3D.section.prevRecord;   /* __acad3dV119 */
    var c=A3D.cam;
    c.yaw=prev.yaw;c.pitch=prev.pitch;c.dist=prev.dist;c.tx=prev.tx;c.ty=prev.ty;c.tz=prev.tz;
    A3D.flat=prevFlat;
    A3D.view=prevView||'Home';
    if(el.flip){el.flip.textContent=A3D.flat?'3D':'2D';el.flip.setAttribute('title',A3D.flat?'Go to 3D (>)':'Go to 2D (>)');}
    if(el.root)el.root.classList.toggle('flat',A3D.flat);
    A3D.section=null;
    /* __acad3dV119: back to the view the section was cut from, the record with the camera. A record
       that is not a model view to go back to (a sheet, a section) gives way to the view the camera
       now shows. With a sheet on screen -- a view switch that closes the sheet ends the section before
       it records its own view -- the sheet stays the view, and the Model tab's way back, if it named
       this section, is pointed at the view the section came from. */
    if(!rec||rec.kind==='sheet'||rec.kind==='section')rec=bimViewOfCamera();
    if(A3D_VIEW.kind==='sheet'){
      if(A3D_LAST_MODEL_VIEW&&A3D_LAST_MODEL_VIEW.kind==='section')
        A3D_LAST_MODEL_VIEW={kind:rec.kind,id:rec.id,cam:{yaw:c.yaw,pitch:c.pitch,dist:c.dist,tx:c.tx,ty:c.ty,tz:c.tz}};
      refreshHud();
    }else bimSetActiveView(rec.kind,rec.id,null);
    paint();saveSoon();
    a3dToast('Exited section view');
  }

