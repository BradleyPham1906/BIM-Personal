  /* ================= __acad3dV87: the modify toolbox, part one =========================

     Pure polyline operations. Each takes point arrays and returns point arrays or an {error};
     none of them touch the model or the DOM, so the browser suite asserts on the GEOMETRY that
     comes out rather than on what the screen looks like afterwards. That is the V86 lesson
     applied before the bug rather than after it.

     WHAT IS DELIBERATELY NOT HERE: a radius FILLET. A rounded corner is an ARC, and this file
     has no arc storage yet -- Phase 88 decides between a bulge factor per vertex and a
     segment-type array, and four drawing tools depend on that answer. A chord-approximated arc
     written here would be geometry the real arc storage then disagrees with, which is precisely
     the leftover Standing Law 1 is about. So FILLET runs at radius 0 -- the corner case, which
     is AutoCAD's own behaviour when the radius is 0 -- and says so in the toast. CHAMFER is
     straight geometry, needs no arcs, and is implemented in full below.

     AutoCAD reference this was built against:
       EXTEND  "Extends objects to meet the edges of other objects." The picked END is the one
               that moves, and it moves along its own direction until it meets the boundary.
       BREAK   two points: the piece BETWEEN them is removed, leaving two objects.
       BREAKATPOINT  one point: split in place with nothing removed.
       LENGTHEN  DElta / Total / Percent, applied at the end nearest the pick.
       CHAMFER "Bevels the edges of objects", two distances measured back from the corner.
     ---------------------------------------------------------------------------------------- */
  function bimPolyLength(pts,closed){
    if(!pts||pts.length<2)return 0;
    var n=pts.length,segs=closed?n:n-1,L=0,i;
    for(i=0;i<segs;i++){
      var a=pts[i],b=pts[(i+1)%n];
      L+=Math.sqrt((b[0]-a[0])*(b[0]-a[0])+(b[1]-a[1])*(b[1]-a[1]));
    }
    return L;
  }
  function bimProjectOntoPolyline(pts,closed,p){
    if(!pts||pts.length<2)return null;
    var n=pts.length,segs=closed?n:n-1,best=null,i;
    for(i=0;i<segs;i++){
      var a=pts[i],b=pts[(i+1)%n];
      var dx=b[0]-a[0],dz=b[1]-a[1],L2=dx*dx+dz*dz;
      var t=L2?((p[0]-a[0])*dx+(p[1]-a[1])*dz)/L2:0;
      t=Math.max(0,Math.min(1,t));
      var q=[a[0]+dx*t,a[1]+dz*t];
      var d=Math.sqrt((p[0]-q[0])*(p[0]-q[0])+(p[1]-q[1])*(p[1]-q[1]));
      if(!best||d<best.dist)best={seg:i,t:t,pt:q,dist:d};
    }
    return best;
  }
  /* Which free end the user meant, by proximity to the pick -- the same rule AutoCAD uses for
     EXTEND and LENGTHEN, and the reason both commands take a click rather than a dialog field. */
  function bimNearestEndIndex(pts,p){
    var n=pts.length;
    var d0=(pts[0][0]-p[0])*(pts[0][0]-p[0])+(pts[0][1]-p[1])*(pts[0][1]-p[1]);
    var d1=(pts[n-1][0]-p[0])*(pts[n-1][0]-p[0])+(pts[n-1][1]-p[1])*(pts[n-1][1]-p[1]);
    return d0<=d1?0:n-1;
  }
  function bimChamferPolylines(clA,closedA,clB,closedB,d1,d2){
    if(closedA||closedB)return {error:'Chamfer needs two open walls'};
    if(!clA||clA.length<2||!clB||clB.length<2)return {error:'Both walls need a usable centerline'};
    if(!isFinite(d1)||!isFinite(d2)||d1<=0||d2<=0)
      return {error:'Both chamfer distances must be greater than zero (a zero-distance chamfer IS the corner case - run Fillet)'};
    var endsA=[0,clA.length-1],endsB=[0,clB.length-1],best=null,ia,ib;
    for(ia=0;ia<2;ia++)for(ib=0;ib<2;ib++){
      var pa=clA[endsA[ia]],pb=clB[endsB[ib]];
      var d=(pa[0]-pb[0])*(pa[0]-pb[0])+(pa[1]-pb[1])*(pa[1]-pb[1]);
      if(!best||d<best.d)best={d:d,ai:endsA[ia],bi:endsB[ib]};
    }
    var aNb=best.ai===0?1:clA.length-2,bNb=best.bi===0?1:clB.length-2;
    var ip=bimLineLineIntersect(clA[aNb],clA[best.ai],clB[bNb],clB[best.bi]);
    if(!ip)return {error:'Those two walls are parallel - there is no corner to chamfer'};
    function backFrom(corner,neigh,dist,label){
      var vx=neigh[0]-corner[0],vz=neigh[1]-corner[1];
      var L=Math.sqrt(vx*vx+vz*vz);
      if(L<1e-9)return {error:'The wall '+label+' has zero length at the corner'};
      if(dist>=L)return {error:'Chamfer distance '+label+' is longer than the wall it cuts back ('+L.toFixed(3)+' m available)'};
      return {pt:[corner[0]+vx/L*dist,corner[1]+vz/L*dist]};
    }
    var ra=backFrom(ip,clA[aNb],d1,'on the first wall');
    if(ra.error)return {error:ra.error};
    var rb=backFrom(ip,clB[bNb],d2,'on the second wall');
    if(rb.error)return {error:rb.error};
    var outA=clA.map(function(p){return [p[0],p[1]];});
    var outB=clB.map(function(p){return [p[0],p[1]];});
    outA[best.ai]=[ra.pt[0],ra.pt[1]];
    outB[best.bi]=[rb.pt[0],rb.pt[1]];
    return {a:outA,b:outB,chamfer:[[ra.pt[0],ra.pt[1]],[rb.pt[0],rb.pt[1]]],corner:[ip[0],ip[1]]};
  }
  function bimScalePoint(p,base,k){
    return [base[0]+(p[0]-base[0])*k,base[1]+(p[1]-base[1])*k];
  }
  function startTrimTool(){
    var cutter=objById(A3D.sel);
    if(!cutter||!cutter.bim||cutter.bim.type!=='wall'||!cutter.bim.centerline){
      a3dToast('Select the cutting wall first, then run Trim and click the part to remove');
      return;
    }
    bimEnterDraftingMode();
    var lvl=bimGetActiveLevel();
    A3D.sk={tool:'trim',pts:[],y:lvl.elev,on:null,cutterId:cutter.id};
    a3dToast('Trim: click the portion of a wall to remove (cutter: '+cutter.name+')');
    paint();
  }
  function bimApplyTrim(cutterId,clickPt){
    var cutter=objById(cutterId);
    if(!cutter){a3dToast('Cutting wall no longer exists');return;}
    var target=null,bestD=Infinity,i;
    for(i=0;i<A3D.objs.length;i++){
      var o=A3D.objs[i];
      if(o.id===cutterId)continue;
      if(!o.bim||o.bim.type!=='wall'||!o.bim.centerline)continue;
      if(bimIsLocked(o))continue;
      /* __acad3dV91: measure to the CURVE. Picking a curved wall by its chords finds it in the
         wrong place, and on a tight arc can fail to find it at all. */
      var cl=o.bim.centerline,n=cl.length,segs=o.bim.closed?n:n-1,k;
      for(k=0;k<segs;k++){
        var d=bimPtDistToBulgedSeg(clickPt,cl[k],cl[(k+1)%n],bimBulgeAt(o.bim.bulges,k)).dist;
        if(d<bestD){bestD=d;target=o;}
      }
    }
    if(!target||bestD>3){a3dToast('Click closer to the wall you want to trim');return;}
    var r=bimTrimBulged(target.bim.centerline,target.bim.bulges,target.bim.closed,
                        cutter.bim.centerline,cutter.bim.bulges,cutter.bim.closed,clickPt);
    if(r.error){a3dToast('Trim: '+r.error);return;}
    var res=bimBuildWallGeometry(r.pts,target.bim.baseY,target.bim.height,target.bim.thickness,target.bim.align,false,r.bulges);
    if(res.error){a3dToast('Trim: '+res.error);return;}
    pushUndo();
    target.mesh=res.mesh;
    target.bim=bimCarryBim(target.bim,res.bim);   /* __acad3dV123: Trim dropped the type */
    bimAfterWallRebuild(target);
    refreshTree();paint();saveSoon();
    a3dToast(target.name+' trimmed');
  }
  /* ---------- __acad3dV87: the command layer over the Phase 87 geometry core.

     One rule runs through all of it: a wall that comes out of a modify command is the SAME
     BIM object it was going in -- same level, same wall type, same material, same layer -- and
     a wall newly created by one (Break's second piece, Chamfer's bevel) inherits those from the
     wall it came from. bimDuplicateObject does not copy typeId/typeCat, so a copied wall
     silently loses its type; that is not repeated here. ---------- */
  /* __acad3dV89: one predicate and one message shape for every tool that cannot yet do curves.

     The alternative was to let them run on the chord, which would silently straighten a curved
     wall and look like a successful edit. A refusal that names the tool is the honest form of
     "not yet", and it is one line at each call layer rather than a guess inside the geometry. */
  function bimWallIsCurved(o){
    return !!(o&&o.bim&&o.bim.type==='wall'&&bimHasBulge(o.bim.bulges));
  }
  function bimRefuseIfCurved(o,what){
    if(!bimWallIsCurved(o))return false;
    a3dToast(what+' does not support curved walls yet - '+(o.name||'that wall')+' has an arc in it');
    return true;
  }
  function bimNewWallFromSource(src,pts,closed,nameHint,bulges){
    var res=bimBuildWallGeometry(pts,src.bim.baseY,src.bim.height,src.bim.thickness,src.bim.align,!!closed,bulges);
    if(res.error)return {error:res.error};
    A3D.counts.wall=(A3D.counts.wall||0)+1;
    res.bim.levelId=src.bim.levelId;
    if(src.bim.typeId)res.bim.typeId=src.bim.typeId;
    if(src.bim.typeCat)res.bim.typeCat=src.bim.typeCat;
    var o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',
      name:(nameHint||'Wall')+'_'+A3D.counts.wall,col:src.col,pos:[0,0,0],
      mesh:res.mesh,bim:res.bim,layer:src.layer};
    if(src.materialName)o.materialName=src.materialName;
    return {obj:o};
  }
  function bimRebuildWallFrom(o,pts,closed,bulges){
    var res=bimBuildWallGeometry(pts,o.bim.baseY,o.bim.height,o.bim.thickness,o.bim.align,!!closed,bulges);
    if(res.error)return {error:res.error};
    o.mesh=res.mesh;
    o.bim=bimCarryBim(o.bim,res.bim);   /* __acad3dV123 */
    bimAfterWallRebuild(o);
    return {ok:true};
  }
  /* Finds the editable wall nearest a picked point, excluding one id (the boundary/cutter).
     Shared by Extend, Break and Lengthen so all three agree on what "the wall you clicked"
     means -- one predicate, not three that can drift. */
  function bimPickWallNear(clickPt,excludeId,maxDist){
    var best=null,bestD=Infinity,i;
    for(i=0;i<A3D.objs.length;i++){
      var o=A3D.objs[i];
      if(excludeId&&o.id===excludeId)continue;
      if(!o.bim||o.bim.type!=='wall'||!o.bim.centerline)continue;
      if(bimIsLocked(o))continue;
      var cl=o.bim.centerline,n=cl.length,segs=o.bim.closed?n:n-1,k;
      for(k=0;k<segs;k++){
        /* __acad3dV91: to the curve, not the chord. */
        var d=bimPtDistToBulgedSeg(clickPt,cl[k],cl[(k+1)%n],bimBulgeAt(o.bim.bulges,k)).dist;
        if(d<bestD){bestD=d;best=o;}
      }
    }
    if(!best||bestD>(maxDist||3))return null;
    return best;
  }
  /* ---------- EXTEND: the mirror image of Trim. Same interaction, same preconditions, opposite
     direction: Trim takes the clicked side away at the crossing, Extend pushes the clicked END
     forward until it reaches the boundary. ---------- */
  function startExtendTool(){
    var bound=objById(A3D.sel);
    if(!bound||!bound.bim||bound.bim.type!=='wall'||!bound.bim.centerline){
      a3dToast('Select the boundary wall first, then run Extend and click the end to extend');
      return;
    }
    bimEnterDraftingMode();
    var lvl=bimGetActiveLevel();
    A3D.sk={tool:'extend',pts:[],y:lvl.elev,on:null,boundaryId:bound.id};
    a3dToast('Extend: click the wall end to extend (boundary: '+bound.name+')');
    paint();
  }
  function bimApplyExtend(boundaryId,clickPt){
    try{
      var bound=objById(boundaryId);
      if(!bound){a3dToast('Boundary wall no longer exists');return false;}
      var target=bimPickWallNear(clickPt,boundaryId,3);
      if(!target){a3dToast('Click closer to the end of the wall you want to extend');return false;}
      /* __acad3dV92: an arc end extends along its own circle. */
      var r=bimExtendBulged(target.bim.centerline,target.bim.bulges,target.bim.closed,
                            bound.bim.centerline,bound.bim.bulges,bound.bim.closed,clickPt);
      if(r.error){a3dToast('Extend: '+r.error);return false;}
      pushUndo();
      var rb=bimRebuildWallFrom(target,r.pts,target.bim.closed,r.bulges);
      if(rb.error){a3dToast('Extend: '+rb.error);return false;}
      refreshTree();paint();saveSoon();
      a3dToast(target.name+' extended '+bimFmtLen(r.added)+' to '+bound.name);
      return true;
    }catch(eX){
      console.warn('[BIM] Extend failed.',eX);
      a3dToast('Extend could not complete');
      return false;
    }
  }
  /* ---------- BREAK / BREAKATPOINT: one wall becomes two objects. BREAK removes the piece
     between the two picks; BREAKATPOINT removes nothing and splits in place. ---------- */
  function startBreakTool(atPoint){
    var w=objById(A3D.sel);
    if(!w||!w.bim||w.bim.type!=='wall'||!w.bim.centerline){
      a3dToast('Select the wall to break first');
      return;
    }
    if(bimIsLocked(w)){a3dToast(w.name+' is locked - unlock it to break it');return;}
    bimEnterDraftingMode();
    var lvl=bimGetActiveLevel();
    A3D.sk={tool:'break',pts:[],y:lvl.elev,on:null,breakId:w.id,breakAtPoint:!!atPoint};
    a3dToast(atPoint?('Break at point: click where to split '+w.name)
                    :('Break: click the first point on '+w.name));
    paint();
  }
  function bimApplyBreak(wallId,p1,p2){
    try{
      var w=objById(wallId);
      if(!w){a3dToast('That wall no longer exists');return false;}
      /* __acad3dV91: both pieces keep whatever curve they had, with the split arc's two halves
         recomputed rather than inherited. */
      var before=bimBulgedLength(w.bim.centerline,w.bim.bulges,w.bim.closed);
      var r=bimBreakBulged(w.bim.centerline,w.bim.bulges,w.bim.closed,p1,p2);
      if(r.error){a3dToast('Break: '+r.error);return false;}
      var made=bimNewWallFromSource(w,r.b.pts,false,'Wall',r.b.bulges);
      if(made.error){a3dToast('Break: '+made.error);return false;}
      pushUndo();
      var rb=bimRebuildWallFrom(w,r.a.pts,false,r.a.bulges);
      if(rb.error){a3dToast('Break: '+rb.error);return false;}
      A3D.objs.push(made.obj);
      A3D.sel=w.id;A3D.sel2=null;A3D.selSet=[w.id,made.obj.id];
      refreshTree();refreshHud();paint();saveSoon();
      /* What was removed is what neither surviving piece accounts for. Measured after the
         rebuild, on the arc lengths, so a curved break reports the length of the CURVE that
         went rather than the chord across the gap. */
      var keptA=bimBulgedLength(w.bim.centerline,w.bim.bulges,false);
      var keptB=bimBulgedLength(made.obj.bim.centerline,made.obj.bim.bulges,false);
      a3dToast(p2?('Broken into 2 walls, '+bimFmtLen(Math.max(0,before-keptA-keptB))+' removed')
                 :'Split into 2 walls');
      return true;
    }catch(eB){
      console.warn('[BIM] Break failed.',eB);
      a3dToast('Break could not complete');
      return false;
    }
  }
  /* ---------- LENGTHEN: DElta / Total / Percent, at the end nearest the pick. ---------- */
  function startLengthenTool(){
    var w=objById(A3D.sel);
    if(!w||!w.bim||w.bim.type!=='wall'||!w.bim.centerline){
      a3dToast('Select the wall to lengthen first');
      return;
    }
    if(bimIsLocked(w)){a3dToast(w.name+' is locked - unlock it to lengthen it');return;}
    bimEnterDraftingMode();
    var lvl=bimGetActiveLevel();
    A3D.sk={tool:'lengthen',pts:[],y:lvl.elev,on:null,lenId:w.id};
    a3dToast('Lengthen: click near the end of '+w.name+' that should move');
    paint();
  }
  function openLengthenDlg(wallId,clickPt){
    var w=objById(wallId);
    if(!w){a3dToast('That wall no longer exists');return;}
    var cur=bimBulgedLength(w.bim.centerline,w.bim.bulges,w.bim.closed);   /* __acad3dV92 */
    closeDlg();
    var d=document.createElement('div');
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">Lengthen</div><div class="a3d-dlgbody">'+
      '<div class="a3d-propnote">Current length '+bimFmtLen(cur)+'. The end you clicked is the one that moves.</div>'+
      '<div class="a3d-dlgrow"><label>Mode</label><select data-a3dp="mode">'+
      '<option value="delta">Delta (add to length)</option>'+
      '<option value="total">Total (set length)</option>'+
      '<option value="percent">Percent of current</option></select></div>'+
      '<div class="a3d-dlgrow"><label>Value</label><input type="number" step="any" data-a3dp="v" value="1"></div>'+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">OK</button></div>';
    el.root.appendChild(d);el.dlg=d;
    var vI=d.querySelector('[data-a3dp="v"]');
    function submit(){
      var mode=d.querySelector('[data-a3dp="mode"]').value;
      var v=parseFloat(vI.value);
      var eb=document.getElementById('a3d-dlgerr');
      if(!isFinite(v)){eb.textContent='Value must be a number';return;}
      closeDlg();
      bimApplyLengthen(wallId,mode,v,clickPt);
    }
    d.addEventListener('click',function(ev){var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;if(!b)return;if(b.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();});
    d.addEventListener('keydown',function(ev){if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}});
    vI.focus();vI.select();
  }
  function bimApplyLengthen(wallId,mode,value,clickPt){
    try{
      var w=objById(wallId);
      if(!w){a3dToast('That wall no longer exists');return false;}
      /* __acad3dV92: on an arc this changes the sweep, not the radius. */
      var r=bimLengthenBulged(w.bim.centerline,w.bim.bulges,w.bim.closed,mode,value,clickPt);
      if(r.error){a3dToast('Lengthen: '+r.error);return false;}
      pushUndo();
      var rb=bimRebuildWallFrom(w,r.pts,w.bim.closed,r.bulges);
      if(rb.error){a3dToast('Lengthen: '+rb.error);return false;}
      refreshTree();paint();saveSoon();
      a3dToast(w.name+' is now '+bimFmtLen(r.length));
      return true;
    }catch(eL){
      console.warn('[BIM] Lengthen failed.',eL);
      a3dToast('Lengthen could not complete');
      return false;
    }
  }
  /* ---------- CHAMFER: cuts the corner off two walls and builds the bevel as a real wall, so
     the result is three connected walls rather than a gap with a line drawn over it. ---------- */
  function startChamferTool(){
    var a=objById(A3D.sel),b=objById(A3D.sel2);
    if(!a||!b||a===b){a3dToast('Chamfer needs two walls: click the first, Ctrl+click the second');return;}
    if(!a.bim||a.bim.type!=='wall'||!a.bim.centerline||!b.bim||b.bim.type!=='wall'||!b.bim.centerline){
      a3dToast('Chamfer works on two editable walls');return;
    }
    if(bimIsLocked(a)||bimIsLocked(b)){a3dToast('One of those walls is locked - unlock to chamfer');return;}
    openChamferDlg(a.id,b.id);
  }
  function openChamferDlg(idA,idB){
    closeDlg();
    var d=document.createElement('div');
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">Chamfer</div><div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Distance 1</label><input type="number" step="any" min="0" data-a3dp="d1" value="1"></div>'+
      '<div class="a3d-dlgrow"><label>Distance 2</label><input type="number" step="any" min="0" data-a3dp="d2" value="1"></div>'+
      '<div class="a3d-propnote">Measured back from the corner along each wall. The bevel is built as a third wall, taking its type and thickness from the first.</div>'+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">OK</button></div>';
    el.root.appendChild(d);el.dlg=d;
    var d1I=d.querySelector('[data-a3dp="d1"]'),d2I=d.querySelector('[data-a3dp="d2"]');
    function submit(){
      var v1=parseFloat(d1I.value),v2=parseFloat(d2I.value);
      var eb=document.getElementById('a3d-dlgerr');
      if(!isFinite(v1)||!isFinite(v2)||v1<=0||v2<=0){eb.textContent='Both distances must be greater than zero';return;}
      closeDlg();
      bimApplyChamfer(idA,idB,v1,v2);
    }
    d.addEventListener('click',function(ev){var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;if(!b)return;if(b.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();});
    d.addEventListener('keydown',function(ev){if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}});
    d1I.focus();d1I.select();
  }
  function bimApplyChamfer(idA,idB,d1,d2){
    try{
      var a=objById(idA),b=objById(idB);
      if(!a||!b){a3dToast('One of those walls no longer exists');return false;}
      if(bimRefuseIfCurved(a,'Chamfer')||bimRefuseIfCurved(b,'Chamfer'))return false;   /* __acad3dV89 */
      var r=bimChamferPolylines(a.bim.centerline,a.bim.closed,b.bim.centerline,b.bim.closed,d1,d2);
      if(r.error){a3dToast('Chamfer: '+r.error);return false;}
      var bev=bimNewWallFromSource(a,r.chamfer,false,'Chamfer');
      if(bev.error){a3dToast('Chamfer: '+bev.error);return false;}
      pushUndo();
      var ra=bimRebuildWallFrom(a,r.a,false);
      if(ra.error){a3dToast('Chamfer: '+ra.error);return false;}
      var rb=bimRebuildWallFrom(b,r.b,false);
      if(rb.error){a3dToast('Chamfer: '+rb.error);return false;}
      A3D.objs.push(bev.obj);
      A3D.sel=bev.obj.id;A3D.sel2=null;A3D.selSet=[bev.obj.id];
      refreshTree();refreshHud();paint();saveSoon();
      a3dToast('Corner chamfered - '+bev.obj.name+' created');
      return true;
    }catch(eC){
      console.warn('[BIM] Chamfer failed.',eC);
      a3dToast('Chamfer could not complete');
      return false;
    }
  }
  /* ---------- SCALE. What scales is the DRAWN geometry: centerlines, profiles, centres and
     positions. What does not is the section: wall thickness, column width and depth, floor
     thickness, heights. Those are type and instance PARAMETERS in a BIM model, not drawn
     geometry, and a wall type that reads "Generic - 300mm" must not quietly become 600 because
     someone scaled the plan. Properties is where those change. ---------- */
  function startScaleTool(){
    var ids=(A3D.selSet&&A3D.selSet.length)?A3D.selSet.slice():(A3D.sel?[A3D.sel]:[]);
    if(!ids.length){a3dToast('Select one or more objects to scale first');return;}
    closeDlg();
    bimEnterDraftingMode();
    var lvl=bimGetActiveLevel();
    A3D.sk={tool:'scale',pts:[],y:lvl.elev,on:null,scaleIds:ids};
    a3dToast('Scale: click the base point');
    paint();
  }
  function openScaleDlg(base,ids){
    closeDlg();
    var d=document.createElement('div');
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">Scale</div><div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Scale factor</label><input type="number" step="any" data-a3dp="k" value="2"></div>'+
      '<div class="a3d-propnote">Scales plan geometry about the base point. Section parameters (wall thickness, column size, heights) are BIM parameters and are left unchanged - edit those in Properties.</div>'+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">OK</button></div>';
    el.root.appendChild(d);el.dlg=d;
    var kI=d.querySelector('[data-a3dp="k"]');
    function submit(){
      var k=parseFloat(kI.value);
      var eb=document.getElementById('a3d-dlgerr');
      if(!isFinite(k)||k<=0){eb.textContent='Scale factor must be greater than zero';return;}
      if(Math.abs(k-1)<1e-9){eb.textContent='A factor of 1 would change nothing';return;}
      closeDlg();
      bimScaleSelection(ids,base,k);
    }
    d.addEventListener('click',function(ev){var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;if(!b)return;if(b.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();});
    d.addEventListener('keydown',function(ev){if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}});
    kI.focus();kI.select();
  }
  function bimScaleObjectInPlace(o,base,k){
    var transformPt=function(p){return bimScalePoint(p,base,k);};
    var g=bimComputeTransformedGeometry(o,transformPt,{kind:'scale',k:k});
    if(g.error)return false;
    if(g.kind==='sketch'){o.pts=g.pts;bimAfterSketchEdit(o);}
    else if(g.kind==='room'){o.pts=g.pts;bimCutSource(o,'scaled on its own');   /* __acad3dV97 */
      if(typeof bimPolyArea==='function')o.area=Math.abs(bimPolyArea(o.pts));}
    else if(g.kind==='text'){o.pt=g.pt;}
    else if(g.kind==='dim'){o.p1=g.p1;o.p2=g.p2;o.d1=g.d1;o.d2=g.d2;
      o.length=Math.sqrt((g.p2[0]-g.p1[0])*(g.p2[0]-g.p1[0])+(g.p2[1]-g.p1[1])*(g.p2[1]-g.p1[1]));}
    else if(g.kind==='wall'||g.kind==='floor'||g.kind==='column'){o.mesh=g.mesh;o.bim=bimCarryBim(o.bim,g.bim);bimAfterWallRebuild(o);}
    else if(g.kind==='mesh'){if(g.materialized)bimMaterializeInto(o,g.mesh);else o.mesh=g.mesh;}   /* __acad3dV110 */
    else if(g.kind==='pos'){o.pos=g.pos;}
    else if(g.kind==='diag'){o.dg.g=g.g;o.dg.lb=g.lb;o.dg.sym=g.sym;}   /* __acad3dV164 */
    else if(g.kind==='alignment'){o.pis=g.pis;if(g.pv&&o.profileView)o.profileView.at=g.pv;if(g.k!==1)o.radii=(o.radii||[]).map(function(r){return r*g.k;});}   /* __acad3dV127: a scaled route keeps its shape */
    return true;
  }
  function bimScaleSelection(ids,base,k){
    var locked=ids.filter(function(id){var oo=objById(id);return oo&&bimIsLocked(oo);});
    var scalable=ids.filter(function(id){var oo=objById(id);return oo&&!bimIsLocked(oo);});
    if(!scalable.length){a3dToast('Selected object(s) are locked - unlock to scale');return false;}
    pushUndo();
    var ok=0,fail=0,i;
    for(i=0;i<scalable.length;i++){
      var o=objById(scalable[i]);
      if(!o)continue;
      if(bimScaleObjectInPlace(o,base,k))ok++;else fail++;
    }
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast('Scaled '+ok+' object(s) by '+k+(fail?' ('+fail+' skipped)':'')+(locked.length?' ('+locked.length+' locked, skipped)':''));
    bimFlushMaterialized();   /* __acad3dV110 */
    return ok>0;
  }
  /* ---------- __acad3dV89: FILLET with a radius, the V87 deferral collected.

     At radius 0 this is the square corner Join Walls performs; above 0 it cuts both walls back
     to their tangent points and builds the arc between them as a real curved wall. One code
     path computes both, so the two cannot disagree about where the corner is.

     The tangent distance is r/tan(theta/2) for an interior angle theta, and the arc sweeps
     (pi - theta) in the direction of the turn. The turn direction comes from the TRAVEL
     vectors - into the corner along -uA and out along +uB - not from uA and uB themselves,
     which point the same way (back down each wall) and would give the wrong sign for one of
     them. Both signs and the tangency are proved in Phase/bim_phase89_fillet_prototype.js. ---- */
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
    if(radius<1e-9)
      return {a:bimSetEnd(clA,best.ai,ip),b:bimSetEnd(clB,best.bi,ip),corner:ip,radius:0,fillet:null};
    var t=radius/Math.tan(theta/2);
    if(t>=ra.len)return {error:'Radius is too large for the first wall ('+bimFmtLen(ra.len)+' available)'};
    if(t>=rb.len)return {error:'Radius is too large for the second wall ('+bimFmtLen(rb.len)+' available)'};
    var tangA=[ip[0]+ra.u[0]*t,ip[1]+ra.u[1]*t];
    var tangB=[ip[0]+rb.u[0]*t,ip[1]+rb.u[1]*t];
    var inDir=[-ra.u[0],-ra.u[1]],outDir=rb.u;
    var cross=inDir[0]*outDir[1]-inDir[1]*outDir[0];
    var sweep=(cross>=0?1:-1)*(Math.PI-theta);
    return {a:bimSetEnd(clA,best.ai,tangA),b:bimSetEnd(clB,best.bi,tangB),
            fillet:{pts:[tangA,tangB],bulges:[Math.tan(sweep/4),0]},
            corner:ip,radius:radius,tangent:t,sweep:sweep};
  }
  /* AutoCAD remembers the fillet radius between runs, and so does this. */
  function bimFilletRadius(){
    return (typeof A3D.filletRadius==='number'&&isFinite(A3D.filletRadius))?A3D.filletRadius:0.5;
  }
  function applyFilletCorner(){
    var a=objById(A3D.sel),b=objById(A3D.sel2);
    if(!a||!b||a===b){a3dToast('Fillet needs two walls: click the first, Ctrl+click the second');return;}
    if(!a.bim||a.bim.type!=='wall'||!a.bim.centerline||!b.bim||b.bim.type!=='wall'||!b.bim.centerline){
      a3dToast('Fillet works on two editable walls');return;
    }
    if(bimIsLocked(a)||bimIsLocked(b)){a3dToast('One of those walls is locked - unlock to fillet');return;}
    if(bimRefuseIfCurved(a,'Fillet')||bimRefuseIfCurved(b,'Fillet'))return;
    openFilletDlg(a.id,b.id);
  }
  function openFilletDlg(idA,idB){
    closeDlg();
    var d=document.createElement('div');
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">Fillet</div><div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Radius</label><input type="number" step="any" min="0" data-a3dp="r" value="'+bimFilletRadius()+'"></div>'+
      '<div class="a3d-propnote">Radius 0 gives a square corner. Above 0, both walls are cut back to their tangent points and the arc between them is built as a curved wall.</div>'+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">OK</button></div>';
    el.root.appendChild(d);el.dlg=d;
    var rI=d.querySelector('[data-a3dp="r"]');
    function submit(){
      var r=parseFloat(rI.value);
      var eb=document.getElementById('a3d-dlgerr');
      if(!isFinite(r)||r<0){eb.textContent='Radius must be zero or greater';return;}
      A3D.filletRadius=r;
      closeDlg();
      bimApplyFillet(idA,idB,r);
    }
    d.addEventListener('click',function(ev){var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;if(!b)return;if(b.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();});
    d.addEventListener('keydown',function(ev){if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}});
    rI.focus();rI.select();
  }
  function bimApplyFillet(idA,idB,radius){
    try{
      var a=objById(idA),b=objById(idB);
      if(!a||!b){a3dToast('One of those walls no longer exists');return false;}
      var r=bimFilletCorner(a.bim.centerline,a.bim.closed,b.bim.centerline,b.bim.closed,radius);
      if(r.error){a3dToast('Fillet: '+r.error);return false;}
      /* The curved wall is built BEFORE anything is committed, so a failure here leaves both
         walls untouched rather than half-filleted. */
      var arcWall=null;
      if(r.fillet){
        arcWall=bimNewWallFromSource(a,r.fillet.pts,false,'Fillet',r.fillet.bulges);
        if(arcWall.error){a3dToast('Fillet: '+arcWall.error);return false;}
      }
      pushUndo();
      var ra=bimRebuildWallFrom(a,r.a,false,null);
      if(ra.error){a3dToast('Fillet: '+ra.error);return false;}
      var rb=bimRebuildWallFrom(b,r.b,false,null);
      if(rb.error){a3dToast('Fillet: '+rb.error);return false;}
      if(arcWall){
        A3D.objs.push(arcWall.obj);
        A3D.sel=arcWall.obj.id;A3D.sel2=null;A3D.selSet=[arcWall.obj.id];
      }else{
        A3D.sel=a.id;A3D.sel2=null;A3D.selSet=[a.id];
      }
      refreshTree();refreshHud();paint();saveSoon();
      a3dToast(radius>0?('Filleted at radius '+bimFmtLen(radius)+' - '+arcWall.obj.name+' created')
                       :'Filleted at radius 0 (square corner)');
      return true;
    }catch(eF){
      console.warn('[BIM] Fillet failed.',eF);
      a3dToast('Fillet could not complete');
      return false;
    }
  }
  function openOffsetDlg(){
    var ids=(A3D.selSet&&A3D.selSet.length)?A3D.selSet.slice():(A3D.sel?[A3D.sel]:[]);
    if(!ids.length){a3dToast('Select a wall or sketch to offset');return;}
    closeDlg();
    var d=document.createElement('div');
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">Offset</div><div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Distance</label><input type="number" step="any" data-a3dp="d" value="0.5"></div>'+
      '<div class="a3d-propnote">On a closed loop, a positive distance offsets inward and a negative one outward.</div>'+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">OK</button></div>';
    el.root.appendChild(d);el.dlg=d;
    var dI=d.querySelector('[data-a3dp="d"]');
    function submit(){
      var dist=parseFloat(dI.value);
      var eb=document.getElementById('a3d-dlgerr');
      if(!isFinite(dist)||Math.abs(dist)<1e-9){eb.textContent='Distance must be a non-zero number';return;}
      closeDlg();
      bimOffsetSelection(ids,dist);
    }
    d.addEventListener('click',function(ev){var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;if(!b)return;if(b.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();});
    d.addEventListener('keydown',function(ev){if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}});
    dI.focus();dI.select();
  }
  function bimOffsetSelection(ids,dist){
    pushUndo();
    var made=[],fails=0,i;
    for(i=0;i<ids.length;i++){
      var o=objById(ids[i]);
      if(!o)continue;
      var r=bimOffsetObject(o,dist);
      if(r.error){fails++;continue;}
      A3D.objs.push(r.obj);made.push(r.obj.id);
    }
    if(!made.length){a3dToast('Offset failed: nothing offsettable in the selection');return;}
    A3D.selSet=made;A3D.sel=made[0];A3D.sel2=null;
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast('Offset '+made.length+' object(s)'+(fails?' ('+fails+' skipped)':''));
  }
  function openAlignDlg(){
    var ids=(A3D.selSet&&A3D.selSet.length)?A3D.selSet.slice():[];
    if(ids.length<2){a3dToast('Select 2 or more objects to align (the first selected is the reference)');return;}
    closeDlg();
    var d=document.createElement('div');
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">Align</div><div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Axis</label><select data-a3dp="ax"><option value="x">X (left/right)</option><option value="z">Z (up/down in plan)</option></select></div>'+
      '<div class="a3d-dlgrow"><label>Edge</label><select data-a3dp="ed"><option value="min">Min side</option><option value="center">Centre</option><option value="max">Max side</option></select></div>'+
      '<div class="a3d-propnote">The first object in the selection is the reference; the rest move to match it.</div>'+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">OK</button></div>';
    el.root.appendChild(d);el.dlg=d;
    function submit(){
      var ax=d.querySelector('[data-a3dp="ax"]').value,ed=d.querySelector('[data-a3dp="ed"]').value;
      closeDlg();
      bimAlignSelection(ids,ax,ed);
    }
    d.addEventListener('click',function(ev){var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;if(!b)return;if(b.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();});
    d.addEventListener('keydown',function(ev){if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}});
  }
  function bimAlignEdgeValue(b,axis,edge){
    if(axis==='x')return edge==='min'?b.minX:(edge==='max'?b.maxX:(b.minX+b.maxX)/2);
    return edge==='min'?b.minZ:(edge==='max'?b.maxZ:(b.minZ+b.maxZ)/2);
  }
  function bimAlignSelection(ids,axis,edge){
    var ref=objById(ids[0]);
    if(!ref){a3dToast('Reference object not found');return;}
    var rb=bimObjBounds2D(ref);
    if(!rb){a3dToast('Reference object has no measurable extent');return;}
    var target=bimAlignEdgeValue(rb,axis,edge);
    pushUndo();
    var moved=0,skipped=0,i;
    for(i=1;i<ids.length;i++){
      var o=objById(ids[i]);
      if(!o||bimIsLocked(o)){skipped++;continue;}
      var b=bimObjBounds2D(o);
      if(!b){skipped++;continue;}
      var delta=target-bimAlignEdgeValue(b,axis,edge);
      if(!o.pos)o.pos=[0,0,0];
      var d3=[0,0,0];
      if(axis==='x'){o.pos[0]+=delta;d3[0]=delta;}else{o.pos[2]+=delta;d3[2]=delta;}
      /* __acad3dV55: discrete, one-shot per object -- propagate right away (unlike the
         continuous drag-move handler, which defers to mouseup for performance) so any
         dependent opening/room/clone follows this object's new position immediately,
         silently (no extra toast -- see the 'Aligned N object(s)' summary below). */
      bimPropagateFrom([o.id],'transform',d3);
      moved++;
    }
    refreshTree();paint();saveSoon();
    a3dToast('Aligned '+moved+' object(s)'+(skipped?' ('+skipped+' skipped)':''));
  }
  /* __acad3dV55: arrow-key nudge, factored out of the keydown handler so it can call
     bimPropagateFrom immediately after each keypress (nudge is discrete/one-shot per press,
     not continuous like a mouse drag -- see the drag-move onUp handling for the continuous
     case) and so it is directly testable without simulating a real keyboard event. Returns
     the [dx,dy,dz] delta applied, or null if the key was not a nudge key. */
  function bimNudgeObject(o,key){
    if(!o||!o.pos)return null;
    var d=[0,0,0];
    if(key==='ArrowLeft')d[0]=-1;
    else if(key==='ArrowRight')d[0]=1;
    else if(key==='ArrowUp')d[2]=-1;
    else if(key==='ArrowDown')d[2]=1;
    else if(key==='PageUp')d[1]=1;
    else if(key==='PageDown')d[1]=-1;
    else return null;
    o.pos[0]+=d[0];o.pos[1]+=d[1];o.pos[2]+=d[2];
    bimPropagateFrom([o.id],'transform',d);
    return d;
  }
  function openArrayDlg(){
    var ids=(A3D.selSet&&A3D.selSet.length)?A3D.selSet.slice():(A3D.sel?[A3D.sel]:[]);
    if(!ids.length){a3dToast('Select one or more objects to array first');return;}
    closeDlg();
    var d=document.createElement('div');
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">Linear Array</div>'+
      '<div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Count</label><input type="number" step="1" min="2" data-a3dp="n" value="3"></div>'+
      '<div class="a3d-dlgrow"><label>Spacing X</label><input type="number" step="any" data-a3dp="dx" value="2"></div>'+
      '<div class="a3d-dlgrow"><label>Spacing Z</label><input type="number" step="any" data-a3dp="dz" value="0"></div>'+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">OK</button></div>';
    el.root.appendChild(d);
    el.dlg=d;
    var nI=d.querySelector('[data-a3dp="n"]'),dxI=d.querySelector('[data-a3dp="dx"]'),dzI=d.querySelector('[data-a3dp="dz"]');
    function submit(){
      var n=parseInt(nI.value,10),ax=parseFloat(dxI.value),az=parseFloat(dzI.value);
      var eb=document.getElementById('a3d-dlgerr');
      if(!isFinite(n)||n<2){eb.textContent='Count must be 2 or more';return;}
      if(!isFinite(ax)||!isFinite(az)){eb.textContent='Spacing must be numeric';return;}
      if(ax===0&&az===0){eb.textContent='Spacing cannot be zero in both directions';return;}
      closeDlg();
      buildArray(ids,n,ax,az);
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
    nI.focus();nI.select();
  }
  function buildArray(ids,n,ax,az){
    pushUndo();
    var newIds=[],i,k;
    var steps={},cut=0;   /* __acad3dV124: the copies of one step are relinked among themselves */
    for(i=0;i<ids.length;i++){
      var o=objById(ids[i]);
      if(!o)continue;
      for(k=1;k<n;k++){
        var copy=bimDuplicateObject(o,ax*k,az*k);
        if(copy){A3D.objs.push(copy);newIds.push(copy.id);(steps[k]=steps[k]||[]).push([o,copy]);}
      }
    }
    if(!newIds.length){a3dToast('Array failed: unsupported object type(s)');return;}
    for(k=1;k<n;k++)if(steps[k])cut+=bimRelinkCopies(steps[k],ax*k,az*k,0);
    A3D.selSet=ids.concat(newIds);
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast('Array created '+newIds.length+' cop'+(newIds.length===1?'y':'ies')+bimRelinkNote(cut));
  }
  function cubeHit(x,y){
    var i;
    for(i=0;i<A3D.cubePolys.length;i++){
      if(inPoly(x,y,A3D.cubePolys[i].pts))return A3D.cubePolys[i].n;
    }
    return null;
  }
  function inRect(x,y,r){return r&&x>=r[0]&&x<=r[0]+r[2]&&y>=r[1]&&y<=r[1]+r[3];}

  var VIEWS={
    home:{yaw:-0.7,pitch:0.42,label:'Home',ortho:false},
    iso:{yaw:-0.7,pitch:0.42,label:'Isometric',ortho:false},
    top:{yaw:0,pitch:1.52,label:'Top (Plan)',ortho:true},
    bottom:{yaw:0,pitch:-1.52,label:'Bottom',ortho:true},
    front:{yaw:0,pitch:0.02,label:'Front Elevation',ortho:true},
    back:{yaw:Math.PI,pitch:0.02,label:'Back Elevation',ortho:true},
    right:{yaw:Math.PI/2,pitch:0.02,label:'Right Elevation',ortho:true},
    left:{yaw:-Math.PI/2,pitch:0.02,label:'Left Elevation',ortho:true}
  };
  /* __acad3dV119: a preset is a view, and opens as one. The ViewCube's faces and its Home, the View
     tab's Top / Front / Right / 3D View / Home and the __a3dSetView hook all moved the camera below
     directly, so none of them told the record: after a click on the cube's Front face the HUD, the
     Project Browser and Properties went on naming the plan. They open the view through the one
     activation path now -- which also leaves a section behind, as every other view switch does.
     Top is the floor plan of the active level; Home and Isometric are the 3D view, Home framed
     afresh; the other faces are elevations. */
  function setView(name,anim){
    var v=VIEWS[name],o={anim:anim!==false};
    if(!v)return false;
    if(name==='top')return bimActivateView('plan',null,o);
    if(!v.ortho){o.home=(name==='home');return bimActivateView('3d',null,o);}
    return bimActivateView('elev',name,o);
  }
  /* The camera move itself, which bimActivateView makes for a plan, the 3D view and an elevation. */
  function bimAimPreset(name,anim){
    var v=VIEWS[name];if(!v)return;
    A3D.flat=!!v.ortho;
    A3D.prevCam=null;A3D.prevView=null;
    if(el.flip){el.flip.textContent=A3D.flat?'3D':'2D';el.flip.setAttribute('title',A3D.flat?'Go to 3D (>)':'Go to 2D (>)');}
    if(el.root)el.root.classList.toggle('flat',A3D.flat);
    A3D.view=v.label;
    refreshHud();
    var c=A3D.cam;
    var to={yaw:v.yaw,pitch:v.pitch,dist:c.dist,tx:c.tx,ty:c.ty,tz:c.tz};
    if(name==='home'){to.dist=DEFCAM.dist;to.tx=DEFCAM.tx;to.ty=DEFCAM.ty;to.tz=DEFCAM.tz;}
    if(anim===false){
      c.yaw=to.yaw;c.pitch=to.pitch;c.dist=to.dist;c.tx=to.tx;c.ty=to.ty;c.tz=to.tz;
      paint();saveSoon();return;
    }
    var from={yaw:c.yaw,pitch:c.pitch,dist:c.dist,tx:c.tx,ty:c.ty,tz:c.tz};
    var t0=Date.now(),dur=260;
    function step(){
      var t=Math.min(1,(Date.now()-t0)/dur);
      var e=1-Math.pow(1-t,3),k;
      for(k in to)if(to.hasOwnProperty(k))c[k]=from[k]+(to[k]-from[k])*e;
      paint();
      if(t<1&&A3D.on)requestAnimationFrame(step);
      else saveSoon();
    }
    requestAnimationFrame(step);
  }
