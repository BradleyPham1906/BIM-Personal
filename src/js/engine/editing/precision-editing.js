  // ---- __acad3dV17: Precision editing for BIM objects (Mirror, Rotate, Polar Array, Wall Join).
  // Operates on A3D.objs directly. ----
  function bimMirrorPoint(pt,P1,P2){
    var dx=P2[0]-P1[0],dz=P2[1]-P1[1];
    var len=Math.sqrt(dx*dx+dz*dz)||1e-9;
    var ux=dx/len,uz=dz/len;
    var vx=pt[0]-P1[0],vz=pt[1]-P1[1];
    var proj=vx*ux+vz*uz;
    var perpX=vx-proj*ux,perpZ=vz-proj*uz;
    return [P1[0]+proj*ux-perpX,P1[1]+proj*uz-perpZ];
  }
  function bimRotatePoint(pt,center,angleRad){
    var vx=pt[0]-center[0],vz=pt[1]-center[1];
    var c=Math.cos(angleRad),s=Math.sin(angleRad);
    return [center[0]+vx*c-vz*s,center[1]+vx*s+vz*c];
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
  /* __acad3dV81: xf says WHAT the transform is -- {kind:'rotate',angle} or
     {kind:'mirror',P1,P2} -- alongside the point mapper.

     A point mapper cannot express ORIENTATION, and that is exactly why the column branch below
     could not carry one: given only a function from point to point, the only thing it could do
     with a column was move its centre and redraw the footprint square. Every parametric type
     that grows a direction later needs the same information, so it is passed rather than
     inferred. xf is optional: without it the existing orientation is preserved unchanged, which
     is the safe reading for a transform this function does not recognise. */
  /* __acad3dV110: a parametric primitive (Box, Cylinder, Wedge ...) stores no orientation -- its
     mesh is regenerated from Length / Width / Height about its own axes every time it is drawn. A
     turn, a mirror or a one-way stretch therefore cannot be written back as new parameter values,
     and before this phase it was written back as nothing: the transform moved the primitive's
     position and left it facing the way it always had, while the ring read 'ANGLE 90'. The honest
     record of the new shape is the mesh itself, so the primitive becomes a plain solid and the
     user is told once, at the end of the operation. */
  function bimPrimitiveMesh(o){
    if(!o||o.mesh||!o.prm||!TYPES[o.t])return null;
    var m=TYPES[o.t].mk(mergePrm(o.t,o.prm));
    return (m&&m.v&&m.f)?bimCloneMesh(m):null;
  }
  var A3D_MATERIALIZED=[];
  function bimNoteMaterialized(name){
    if(A3D_MATERIALIZED.indexOf(name)<0)A3D_MATERIALIZED.push(name);
  }
  function bimMaterializeInto(o,mesh){
    o.mesh=mesh;
    delete o.prm;
    o.t='solid';
    bimNoteMaterialized(o.name);
  }
  function bimFlushMaterialized(){
    var n=A3D_MATERIALIZED.length;
    if(!n)return 0;
    var names=A3D_MATERIALIZED.slice(0,2).join(', ')+(n>2?(' and '+(n-2)+' more'):'');
    A3D_MATERIALIZED=[];
    a3dToast(names+(n===1?' is now a plain solid':' are now plain solids')+
      ' - a primitive cannot hold a turn or a one-way stretch in its size parameters, so the new shape is kept in its mesh');
    return n;
  }
  function bimComputeTransformedGeometry(o,transformPt,xf){
    /* __acad3dV110: transformPt is a WORLD plan transform -- a centre, a mirror line or a base
       point the user picked in the drawing -- but every branch below applies it to the object's
       LOCAL geometry, which sits at o.pos. Treating the two as one meant that any object that had
       been moved (by the gizmo, a body drag, MOVE) turned about a point offset from the one the
       user picked, and swung away across the plan: a wall moved 5 m and turned 90 degrees landed
       5 m east and 5 m north of where it should have been. Converted once, here, so every branch
       and every caller -- Rotate, Mirror, Scale, Polar Array, the gizmo -- is right together. */
    var q=bimObjOffset(o),worldPt=transformPt;
    if(q[0]||q[2])transformPt=function(p){
      var w=worldPt([p[0]+q[0],p[1]+q[2]]);
      return [w[0]-q[0],w[1]-q[2]];
    };
    if(bimIsDiag(o)){   /* __acad3dV164 */
      if(o.dg.g.kind==='live')return {error:'A live shadow follows the sun and the model: it cannot be turned, mirrored or scaled'};
      if(o.dg.g.kind==='mesh')return {error:'The temperature on the dome follows the sun: it cannot be turned, mirrored or scaled'};   /* __acad3dV171d */
      return bimDgTransformed(o.dg,transformPt);
    }
    if(o.t==='sketch')return {kind:'sketch',pts:o.pts.map(transformPt),y:o.y};
    if(o.t==='alignment')return {kind:'alignment',pis:o.pis.map(transformPt),pv:o.profileView&&o.profileView.at?transformPt(o.profileView.at):null,k:xf&&xf.kind==='scale'&&xf.k>0?xf.k:1};   /* __acad3dV127 */
    if(o.t==='room')return {kind:'room',pts:o.pts.map(transformPt),y:o.y,area:o.area};
    if(o.t==='text')return {kind:'text',pt:transformPt(o.pt),y:o.y,text:o.text};
    if(o.t==='dim'){
      if(bimDimKind(o)!=='linear')return {error:'Only linear dimensions support Mirror/Rotate for now \u2014 angular/radial/leader dims store angles that need extra handling'};
      var np1=transformPt(o.p1),np2=transformPt(o.p2),nd1=transformPt(o.d1),nd2=transformPt(o.d2);
      return {kind:'dim',p1:np1,p2:np2,d1:nd1,d2:nd2,length:o.length,y:o.y};
    }
    if(o.bim&&o.bim.type==='wall'){
      if(!o.bim.centerline)return {error:'Imported wall has no editable centerline'};
      var newCl=o.bim.centerline.map(transformPt);
      /* __acad3dV89: rotation and scaling preserve a bulge (it is tan of a quarter of the swept
         angle, and neither changes an angle). A MIRROR reverses the sense of every arc, so each
         bulge is negated - a reflected curve that kept its sign would bow the wrong way, which
         is the kind of error that looks like a rendering glitch rather than a data one. */
      var newBulges=o.bim.bulges;
      if(newBulges&&xf&&xf.kind==='mirror')
        newBulges=newBulges.map(function(bv){return -bv;});
      var res=bimBuildWallGeometry(newCl,o.bim.baseY,o.bim.height,o.bim.thickness,o.bim.align,o.bim.closed,newBulges);
      if(res.error)return {error:res.error};
      return {kind:'wall',mesh:res.mesh,bim:res.bim};
    }
    if(o.bim&&o.bim.type==='floor'){
      if(!o.bim.profile)return {error:'Imported floor has no editable profile'};
      var newProf=o.bim.profile.map(transformPt);
      var res2=bimBuildFloorGeometry(newProf,o.bim.baseY,o.bim.thickness);
      if(res2.error)return {error:res2.error};
      /* __acad3dV123: bimBuildFloorGeometry returns a solid and no record, so this returned no
         outline: a turned floor kept its old one, the next rebuild put it back, and a mirrored copy
         threw on the missing record */
      return {kind:'floor',mesh:res2.mesh,bim:{type:'floor',profile:newProf}};
    }
    if(o.bim&&o.bim.type==='column'){
      var newCenter=transformPt(o.bim.center);
      /* A rotation ADDS to the orientation; a mirror REFLECTS it about the mirror line
         (2*phi - theta), which is a different answer and the reason xf carries a kind rather
         than just an angle. */
      var rot0=o.bim.rotation||0,rotN=rot0;
      if(xf&&xf.kind==='rotate')rotN=rot0+(xf.angle||0);
      else if(xf&&xf.kind==='mirror'&&xf.P1&&xf.P2){
        var phi=Math.atan2(xf.P2[1]-xf.P1[1],xf.P2[0]-xf.P1[0]);
        rotN=2*phi-rot0;
      }
      var res3=bimBuildColumnGeometry(newCenter,o.bim.baseY,o.bim.width,o.bim.depth,o.bim.height,rotN,o.bim.section||null);   /* __acad3dV126 */
      if(res3.error)return {error:res3.error};
      return {kind:'column',mesh:res3.mesh,bim:{type:'column',width:o.bim.width,depth:o.bim.depth,height:o.bim.height,baseY:o.bim.baseY,levelId:o.bim.levelId,center:newCenter,rotation:rotN}};
    }
    if(o.bim&&(o.bim.type==='roof'||o.bim.type==='stair')){
      return {error:'Roof and Stair do not support Mirror/Rotate yet (their direction/slope parameters need extra handling) \u2014 redraw instead'};
    }
    if(o.t==='opening'){
      return {error:'Openings move with their host wall and cannot be transformed independently'};
    }
    var srcMesh=o.mesh||bimPrimitiveMesh(o);   /* __acad3dV110: a primitive is transformed as its mesh */
    if(srcMesh){
      var newV=srcMesh.v.map(function(v3){var p2=transformPt([v3[0],v3[2]]);return [p2[0],v3[1],p2[1]];});
      /* A reflection reverses the sense of every face, so a mirrored mesh whose faces kept their
         winding would be inside out. */
      var newF=(xf&&xf.kind==='mirror')?srcMesh.f.map(function(fc){return fc.slice().reverse();}):srcMesh.f;
      return {kind:'mesh',mesh:{v:newV,f:newF},materialized:!o.mesh};
    }
    if(o.pos){
      /* the position IS a world point, so it takes the world transform directly */
      var npz=worldPt([o.pos[0],o.pos[2]]);
      return {kind:'pos',pos:[npz[0],o.pos[1],npz[1]]};
    }
    return {error:'This object type cannot be transformed'};
  }
  function bimMirrorObject(o,P1,P2){
    var transformPt=function(p){return bimMirrorPoint(p,P1,P2);};
    var g=bimComputeTransformedGeometry(o,transformPt,{kind:'mirror',P1:P1,P2:P2});
    if(g.error)return g;
    var copy={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),pos:bimObjOffset(o),col:o.col,layer:o.layer};   /* __acad3dV110: the geometry below is in o's own frame */
    if(o.usage)copy.usage=o.usage;   /* __acad3dV131 */
    if(g.kind==='sketch'){copy.t='sketch';copy.pts=g.pts;copy.y=g.y;copy.closed=o.closed;A3D.counts.sketch=(A3D.counts.sketch||0)+1;copy.name=(o.name||'Sketch')+' mirror';
      if(o.bulges)copy.bulges=o.bulges.map(function(bv){return -bv;});}   /* __acad3dV110: arcs kept, reflected */
    else if(g.kind==='room'){A3D.counts.room=(A3D.counts.room||0)+1;copy.t='room';copy.name='Room_'+A3D.counts.room;copy.pts=g.pts;copy.y=g.y;copy.area=g.area;copy.levelId=o.levelId;}
    else if(g.kind==='text'){A3D.counts.text=(A3D.counts.text||0)+1;copy.t='text';copy.name='Text_'+A3D.counts.text;copy.text=g.text;copy.pt=g.pt;copy.y=g.y;copy.levelId=o.levelId;}
    else if(g.kind==='dim'){A3D.counts.dim=(A3D.counts.dim||0)+1;copy.t='dim';copy.name='Dim_'+A3D.counts.dim;copy.p1=g.p1;copy.p2=g.p2;copy.d1=g.d1;copy.d2=g.d2;copy.length=g.length;copy.y=g.y;copy.levelId=o.levelId;}
    else if(g.kind==='wall'){A3D.counts.wall=(A3D.counts.wall||0)+1;copy.t='solid';copy.name='Wall_'+A3D.counts.wall;copy.mesh=g.mesh;copy.bim=bimCarryBim(o.bim,g.bim);}
    else if(g.kind==='floor'){A3D.counts.floor=(A3D.counts.floor||0)+1;copy.t='solid';copy.name='Floor_'+A3D.counts.floor;copy.mesh=g.mesh;copy.bim=bimCarryBim(o.bim,g.bim);}
    else if(g.kind==='column'){A3D.counts.column=(A3D.counts.column||0)+1;copy.t='solid';copy.name='Column_'+A3D.counts.column;copy.mesh=g.mesh;copy.bim=bimCarryBim(o.bim,g.bim);}
    else if(g.kind==='mesh'){copy.t=g.materialized?'solid':o.t;copy.name=o.name+' mirror';copy.mesh=g.mesh;if(o.prm&&!g.materialized)copy.prm=JSON.parse(JSON.stringify(o.prm));if(g.materialized)bimNoteMaterialized(copy.name);}   /* __acad3dV110 */
    else if(g.kind==='pos'){copy.t=o.t;copy.name=o.name+' mirror';copy.pos=g.pos;if(o.prm)copy.prm=JSON.parse(JSON.stringify(o.prm));}
    else if(g.kind==='diag')bimDgCopy(o,g,copy,'mirror');   /* __acad3dV164 */
    else if(g.kind==='alignment'){   /* __acad3dV127 */
      A3D.counts.alignment=(A3D.counts.alignment||0)+1;copy.t='alignment';copy.name='Alignment_'+A3D.counts.alignment;
      copy.pis=g.pis;copy.radii=(o.radii||[]).slice();copy.sta0=o.sta0||0;copy.y=o.y||0;
      if(o.profile)copy.profile=JSON.parse(JSON.stringify(o.profile));
      if(o.profileView)copy.profileView={at:g.pv,vx:o.profileView.vx};
    }
    return copy;
  }
  function startMirrorTool(){
    var ids=(A3D.selSet&&A3D.selSet.length)?A3D.selSet.slice():(A3D.sel?[A3D.sel]:[]);
    if(!ids.length){a3dToast('Select one or more objects to mirror first');return;}
    closeDlg();
    bimEnterDraftingMode();
    var lvl=bimGetActiveLevel();
    A3D.sk={tool:'mirror',pts:[],y:lvl.elev,on:null,mirrorIds:ids};
    a3dToast('Mirror: click two points to define the mirror line');
    paint();
  }
  function bimMirrorSelection(ids,P1,P2){
    pushUndo();
    var newIds=[],i,failCount=0;
    for(i=0;i<ids.length;i++){
      var o=objById(ids[i]);
      if(!o)continue;
      var copy=bimMirrorObject(o,P1,P2);
      if(copy&&!copy.error){A3D.objs.push(copy);newIds.push(copy.id);}
      else failCount++;
    }
    if(!newIds.length){a3dToast('Mirror failed: unsupported object type(s)');return;}
    A3D.selSet=newIds;A3D.sel=newIds[0];A3D.sel2=null;
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast('Mirrored '+newIds.length+' object(s)'+(failCount?' ('+failCount+' skipped)':''));
    bimFlushMaterialized();   /* __acad3dV110 */
  }
  function bimRotateObjectInPlace(o,center,angleRad){
    var transformPt=function(p){return bimRotatePoint(p,center,angleRad);};
    var g=bimComputeTransformedGeometry(o,transformPt,{kind:'rotate',angle:angleRad});
    if(g.error)return false;
    if(g.kind==='sketch'){o.pts=g.pts;bimAfterSketchEdit(o);}
    else if(g.kind==='room'){o.pts=g.pts;bimCutSource(o,'rotated on its own');}   /* __acad3dV97 */
    else if(g.kind==='text'){o.pt=g.pt;}
    else if(g.kind==='dim'){o.p1=g.p1;o.p2=g.p2;o.d1=g.d1;o.d2=g.d2;}
    else if(g.kind==='wall'||g.kind==='floor'||g.kind==='column'){o.mesh=g.mesh;o.bim=bimCarryBim(o.bim,g.bim);bimAfterWallRebuild(o);}   // __acad3dV53: floor/column now propagate too
    else if(g.kind==='mesh'){if(g.materialized)bimMaterializeInto(o,g.mesh);else o.mesh=g.mesh;}   /* __acad3dV110 */
    else if(g.kind==='pos'){o.pos=g.pos;}
    else if(g.kind==='diag'){o.dg.g=g.g;o.dg.lb=g.lb;o.dg.sym=g.sym;}   /* __acad3dV164 */
    else if(g.kind==='alignment'){o.pis=g.pis;if(g.pv&&o.profileView)o.profileView.at=g.pv;if(g.k!==1)o.radii=(o.radii||[]).map(function(r){return r*g.k;});}   /* __acad3dV127: a scaled route keeps its shape */
    return true;
  }
  function startRotateTool(){
    var ids=(A3D.selSet&&A3D.selSet.length)?A3D.selSet.slice():(A3D.sel?[A3D.sel]:[]);
    if(!ids.length){a3dToast('Select one or more objects to rotate first');return;}
    closeDlg();
    bimEnterDraftingMode();
    var lvl=bimGetActiveLevel();
    A3D.sk={tool:'rotate',pts:[],y:lvl.elev,on:null,rotateIds:ids};
    a3dToast('Rotate: click the rotation center point');
    paint();
  }
  function openRotateDlg(center,ids){
    closeDlg();
    var d=document.createElement('div');
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">Rotate</div>'+
      '<div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Angle (degrees, CCW)</label><input type="number" step="any" data-a3dp="ang" value="90"></div>'+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">OK</button></div>';
    el.root.appendChild(d);
    el.dlg=d;
    var aI=d.querySelector('[data-a3dp="ang"]');
    function submit(){
      var ang=parseFloat(aI.value);
      var eb=document.getElementById('a3d-dlgerr');
      if(!isFinite(ang)){eb.textContent='Angle must be a number';return;}
      closeDlg();
      bimRotateSelection(ids,center,ang*Math.PI/180);
    }
    d.addEventListener('click',function(ev){var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;if(!b)return;if(b.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();});
    d.addEventListener('keydown',function(ev){if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}});
    aI.focus();aI.select();
  }
  function bimRotateSelection(ids,center,angleRad){
    var lockedIds=ids.filter(function(id){var oo=objById(id);return oo&&bimIsLocked(oo);});
    var rotatable=ids.filter(function(id){var oo=objById(id);return oo&&!bimIsLocked(oo);});
    if(!rotatable.length){a3dToast('Selected object(s) are locked \u2014 unlock to rotate');return;}
    pushUndo();
    var ok=0,fail=0,i;
    for(i=0;i<rotatable.length;i++){
      var o=objById(rotatable[i]);
      if(!o)continue;
      if(bimRotateObjectInPlace(o,center,angleRad))ok++;else fail++;
    }
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast('Rotated '+ok+' object(s)'+(fail?' ('+fail+' skipped)':'')+(lockedIds.length?' ('+lockedIds.length+' locked, skipped)':''));
    bimFlushMaterialized();   /* __acad3dV110 */
  }
  function startPolarArrayTool(){
    var ids=(A3D.selSet&&A3D.selSet.length)?A3D.selSet.slice():(A3D.sel?[A3D.sel]:[]);
    if(!ids.length){a3dToast('Select one or more objects to array first');return;}
    closeDlg();
    bimEnterDraftingMode();
    var lvl=bimGetActiveLevel();
    A3D.sk={tool:'polararray',pts:[],y:lvl.elev,on:null,arrayIds:ids};
    a3dToast('Polar Array: click the center point');
    paint();
  }
  function openPolarArrayDlg(center,ids){
    closeDlg();
    var d=document.createElement('div');
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">Polar Array</div>'+
      '<div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Count</label><input type="number" step="1" min="2" data-a3dp="n" value="6"></div>'+
      '<div class="a3d-dlgrow"><label>Total angle (degrees)</label><input type="number" step="any" data-a3dp="ang" value="360"></div>'+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">OK</button></div>';
    el.root.appendChild(d);
    el.dlg=d;
    var nI=d.querySelector('[data-a3dp="n"]'),aI=d.querySelector('[data-a3dp="ang"]');
    function submit(){
      var n=parseInt(nI.value,10),ang=parseFloat(aI.value);
      var eb=document.getElementById('a3d-dlgerr');
      if(!isFinite(n)||n<2){eb.textContent='Count must be 2 or more';return;}
      if(!isFinite(ang)||ang===0){eb.textContent='Total angle must be non-zero';return;}
      closeDlg();
      bimBuildPolarArray(ids,center,n,ang*Math.PI/180);
    }
    d.addEventListener('click',function(ev){var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;if(!b)return;if(b.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();});
    d.addEventListener('keydown',function(ev){if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}});
    nI.focus();nI.select();
  }
  function bimBuildPolarArray(ids,center,n,totalAngleRad){
    pushUndo();
    var newIds=[],i,k,fail=0;
    var stepAngle=totalAngleRad/n;
    for(i=0;i<ids.length;i++){
      var o=objById(ids[i]);
      if(!o)continue;
      for(k=1;k<n;k++){
        var ang=stepAngle*k;
        var transformPt=function(p){return bimRotatePoint(p,center,ang);};
        var g=bimComputeTransformedGeometry(o,transformPt);
        if(g.error){fail++;continue;}
        var built=bimBuildArrayCopyFromGeometry(o,g);
        if(built){A3D.objs.push(built);newIds.push(built.id);}else fail++;
      }
    }
    if(!newIds.length){a3dToast('Array failed: unsupported object type(s)');return;}
    A3D.selSet=ids.concat(newIds);
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast('Polar array created '+newIds.length+' cop'+(newIds.length===1?'y':'ies')+(fail?' ('+fail+' skipped)':''));
    bimFlushMaterialized();   /* __acad3dV110 */
  }
  function bimBuildArrayCopyFromGeometry(o,g){
    var copy={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),pos:bimObjOffset(o),col:o.col,layer:o.layer};   /* __acad3dV110: the geometry below is in o's own frame */
    if(o.usage)copy.usage=o.usage;   /* __acad3dV131 */
    if(g.kind==='sketch'){copy.t='sketch';copy.pts=g.pts;copy.y=g.y;copy.closed=o.closed;copy.name=(o.name||'Sketch')+' copy';
      if(o.bulges)copy.bulges=o.bulges.slice();}   /* __acad3dV110: a turned arc is the same arc */
    else if(g.kind==='room'){A3D.counts.room=(A3D.counts.room||0)+1;copy.t='room';copy.name='Room_'+A3D.counts.room;copy.pts=g.pts;copy.y=g.y;copy.area=g.area;copy.levelId=o.levelId;}
    else if(g.kind==='text'){A3D.counts.text=(A3D.counts.text||0)+1;copy.t='text';copy.name='Text_'+A3D.counts.text;copy.text=g.text;copy.pt=g.pt;copy.y=g.y;copy.levelId=o.levelId;}
    else if(g.kind==='dim'){A3D.counts.dim=(A3D.counts.dim||0)+1;copy.t='dim';copy.name='Dim_'+A3D.counts.dim;copy.p1=g.p1;copy.p2=g.p2;copy.d1=g.d1;copy.d2=g.d2;copy.length=g.length;copy.y=g.y;copy.levelId=o.levelId;}
    else if(g.kind==='wall'){A3D.counts.wall=(A3D.counts.wall||0)+1;copy.t='solid';copy.name='Wall_'+A3D.counts.wall;copy.mesh=g.mesh;copy.bim=bimCarryBim(o.bim,g.bim);}
    else if(g.kind==='floor'){A3D.counts.floor=(A3D.counts.floor||0)+1;copy.t='solid';copy.name='Floor_'+A3D.counts.floor;copy.mesh=g.mesh;copy.bim=bimCarryBim(o.bim,g.bim);}
    else if(g.kind==='column'){A3D.counts.column=(A3D.counts.column||0)+1;copy.t='solid';copy.name='Column_'+A3D.counts.column;copy.mesh=g.mesh;copy.bim=bimCarryBim(o.bim,g.bim);}
    else if(g.kind==='mesh'){copy.t=g.materialized?'solid':o.t;copy.name=o.name+' copy';copy.mesh=g.mesh;if(o.prm&&!g.materialized)copy.prm=JSON.parse(JSON.stringify(o.prm));if(g.materialized)bimNoteMaterialized(copy.name);}   /* __acad3dV110 */
    else if(g.kind==='pos'){copy.t=o.t;copy.name=o.name+' copy';copy.pos=g.pos;if(o.prm)copy.prm=JSON.parse(JSON.stringify(o.prm));}
    else if(g.kind==='diag')bimDgCopy(o,g,copy,'copy');   /* __acad3dV164 */
    else return null;
    return copy;
  }
  function bimFindClosestWallEndpoints(wallA,wallB){
    var clA=wallA.bim.centerline,clB=wallB.bim.centerline;
    if(wallA.bim.closed||wallB.bim.closed)return null;
    if(clA.length<2||clB.length<2)return null;
    var endsA=[{idx:0,pt:clA[0]},{idx:clA.length-1,pt:clA[clA.length-1]}];
    var endsB=[{idx:0,pt:clB[0]},{idx:clB.length-1,pt:clB[clB.length-1]}];
    var best=null,bestDist=Infinity,ea,eb;
    for(ea=0;ea<2;ea++)for(eb=0;eb<2;eb++){
      var dx=endsA[ea].pt[0]-endsB[eb].pt[0],dz=endsA[ea].pt[1]-endsB[eb].pt[1];
      var d=Math.sqrt(dx*dx+dz*dz);
      if(d<bestDist){bestDist=d;best={a:endsA[ea],b:endsB[eb],dist:d};}
    }
    return best;
  }
  function bimJoinWalls(wallA,wallB){
    if(!wallA.bim||wallA.bim.type!=='wall'||!wallA.bim.centerline)return {error:'First object is not an editable wall'};
    if(!wallB.bim||wallB.bim.type!=='wall'||!wallB.bim.centerline)return {error:'Second object is not an editable wall'};
    if(bimWallIsCurved(wallA)||bimWallIsCurved(wallB))   /* __acad3dV89 */
      return {error:'Join does not support curved walls yet'};
    var ends=bimFindClosestWallEndpoints(wallA,wallB);
    if(!ends)return {error:'Both walls must be open (non-closed) polylines to join'};
    var clA=wallA.bim.centerline.slice(),clB=wallB.bim.centerline.slice();
    var aNeighborIdx=ends.a.idx===0?1:ends.a.idx-1;
    var bNeighborIdx=ends.b.idx===0?1:ends.b.idx-1;
    var aNeighbor=clA[aNeighborIdx],aEnd=clA[ends.a.idx];
    var bNeighbor=clB[bNeighborIdx],bEnd=clB[ends.b.idx];
    var ip=bimLineLineIntersect(aNeighbor,aEnd,bNeighbor,bEnd);
    if(!ip)return {error:'Wall directions are parallel; cannot compute a corner intersection'};
    clA[ends.a.idx]=ip;
    clB[ends.b.idx]=ip;
    var resA=bimBuildWallGeometry(clA,wallA.bim.baseY,wallA.bim.height,wallA.bim.thickness,wallA.bim.align,false,null);
    var resB=bimBuildWallGeometry(clB,wallB.bim.baseY,wallB.bim.height,wallB.bim.thickness,wallB.bim.align,false,null);
    if(resA.error)return {error:'Wall A: '+resA.error};
    if(resB.error)return {error:'Wall B: '+resB.error};
    return {meshA:resA.mesh,bimA:resA.bim,meshB:resB.mesh,bimB:resB.bim,joinPoint:ip};
  }
  function applyWallJoin(){
    var a=objById(A3D.sel),b=objById(A3D.sel2);
    if(!a||!b||a===b){a3dToast('Join Walls needs two walls: click the first, Ctrl+click the second');return;}
    if(bimIsLocked(a)||bimIsLocked(b)){a3dToast('One of the selected walls is locked \u2014 unlock to join');return;}
    var res=bimJoinWalls(a,b);
    if(res.error){a3dToast('Join failed: '+res.error);return;}
    pushUndo();
    a.mesh=res.meshA;a.bim=bimCarryBim(a.bim,res.bimA);   /* __acad3dV123: Join dropped both walls' */
    b.mesh=res.meshB;b.bim=bimCarryBim(b.bim,res.bimB);   /* types and levels */
    bimAfterWallRebuild(a);bimAfterWallRebuild(b);
    refreshTree();paint();saveSoon();
    a3dToast('Walls joined at their corner');
  }
  /* ---------- Merge Walls: collapses two colinear, head-to-tail wall segments into one object.
     Distinct from Join Walls above, which miters the corner of two walls but leaves them as two
     separate objects -- Merge goes the other direction, closing a redundant seam (e.g. left over
     after a Trim/Extend, or two segments drawn consecutively that should have been one polyline)
     into a single wall with one continuous centerline. Scoped to straight (2-point) wall segments
     that share an endpoint and run in the same direction; anything else (multi-point walls,
     non-colinear or non-touching walls) is rejected with a specific reason rather than guessed
     at, per this file's fail-safe rule. ---------- */
  function bimMergeWalls(wallA,wallB){
    if(!wallA.bim||wallA.bim.type!=='wall'||!wallA.bim.centerline)return {error:'First object is not an editable wall'};
    if(!wallB.bim||wallB.bim.type!=='wall'||!wallB.bim.centerline)return {error:'Second object is not an editable wall'};
    if(bimWallIsCurved(wallA)||bimWallIsCurved(wallB))   /* __acad3dV89 */
      return {error:'Merge does not support curved walls yet'};
    if(wallA.bim.closed||wallB.bim.closed)return {error:'Closed wall loops cannot be merged'};
    var clA=wallA.bim.centerline,clB=wallB.bim.centerline;
    if(clA.length!==2||clB.length!==2)return {error:'Merge Walls only supports straight (2-point) wall segments'};
    if(Math.abs(wallA.bim.thickness-wallB.bim.thickness)>1e-6)return {error:'Walls have different thickness — merge requires matching thickness'};
    if(Math.abs(wallA.bim.height-wallB.bim.height)>1e-6)return {error:'Walls have different height — merge requires matching height'};
    if(Math.abs(wallA.bim.baseY-wallB.bim.baseY)>1e-6)return {error:'Walls are on different levels — merge requires the same base elevation'};
    if(wallA.bim.align!==wallB.bim.align)return {error:'Walls have different alignment — merge requires matching alignment'};
    var TOL=1e-4;
    function eqPt(p,q){return Math.abs(p[0]-q[0])<TOL&&Math.abs(p[1]-q[1])<TOL;}
    function dirOf(p,q){var dx=q[0]-p[0],dz=q[1]-p[1],len=Math.sqrt(dx*dx+dz*dz)||1;return [dx/len,dz/len];}
    var dA=dirOf(clA[0],clA[1]),dB=dirOf(clB[0],clB[1]);
    var cross=Math.abs(dA[0]*dB[1]-dA[1]*dB[0]);
    if(cross>1e-3)return {error:'Walls are not colinear — merge requires matching direction'};
    var newCl=null;
    if(eqPt(clA[1],clB[0]))newCl=[clA[0],clB[1]];
    else if(eqPt(clA[1],clB[1]))newCl=[clA[0],clB[0]];
    else if(eqPt(clA[0],clB[0]))newCl=[clA[1],clB[1]];
    else if(eqPt(clA[0],clB[1]))newCl=[clA[1],clB[0]];
    else return {error:'Walls do not share an endpoint — merge requires them to be head-to-tail'};
    var res=bimBuildWallGeometry(newCl,wallA.bim.baseY,wallA.bim.height,wallA.bim.thickness,wallA.bim.align,false,null);
    if(res.error)return {error:res.error};
    return {mesh:res.mesh,bim:res.bim};
  }
  function applyMergeWalls(){
    var a=objById(A3D.sel),b=objById(A3D.sel2);
    if(!a||!b||a===b){a3dToast('Merge Walls needs two walls: click the first, Ctrl+click the second');return;}
    if(bimIsLocked(a)||bimIsLocked(b)){a3dToast('One of the selected walls is locked — unlock to merge');return;}
    var res=bimMergeWalls(a,b);
    if(res.error){a3dToast('Merge failed: '+res.error);return;}
    pushUndo();
    a.mesh=res.mesh;a.bim=bimCarryBim(a.bim,res.bim);   /* __acad3dV123 */
    bimAfterWallRebuild(a);
    var idx=-1,i;for(i=0;i<A3D.objs.length;i++)if(A3D.objs[i]===b){idx=i;break;}
    if(idx>=0)A3D.objs.splice(idx,1);
    A3D.sel=a.id;A3D.sel2=null;A3D.selSet=[a.id];
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast('Walls merged into one');
  }
  /* ---------- Check Model: exposes the CSG kernel's own internal manifold/closed-volume test
     (bimMeshSanityCheck, already used privately before every boolean) as a standalone, on-demand
     diagnostic over every solid in the project, rather than only a silent precondition inside
     Union/Cut/Intersect. No new geometry math -- just a report over an existing, already-tested
     check. ---------- */
  function bimCheckModel(){
    var report=[],i;
    for(i=0;i<A3D.objs.length;i++){
      var o=A3D.objs[i];
      if(o.t!=='solid'||!o.mesh||!o.mesh.f||!o.mesh.f.length)continue;
      /* __acad3dV62: verdict now comes from bimMeshClosureCheck, which resolves the T-junctions
         the boolean kernel leaves behind when an opening is cut, instead of from the raw strict
         manifold test. Before this, every wall carrying a door or a window was reported as an
         open shell -- a false positive on the app's most common object, which made the whole
         report untrustworthy. A real hole and a real corruption are still reported exactly as
         before, with the same wording; what changed is only that a closed volume is no longer
         called open because its faces meet at T-junctions. That distinction is still surfaced
         rather than hidden: such a solid passes with a `note` explaining the topology, since a
         T-junction is a genuine (if harmless here) quality difference from a clean manifold. */
      var cl=bimMeshClosureCheck(o.mesh);
      var issue=null,note=null;
      if(cl.corrupt){
        issue='Corrupted geometry (a face edge is used more than once)';
      }else if(!cl.closed){
        issue='Open shell (not fully closed) — may be a legitimate multi-part assembly, or a boolean/build defect';
      }else if(!cl.manifold){
        note='Closed volume; faces meet at T-junctions (normal for a wall cut by an opening)';
      }
      report.push({id:o.id,name:o.name,type:(o.bim&&o.bim.type)||o.t,ok:cl.closed&&!cl.corrupt,
                   volume:cl.vol,issue:issue,note:note,manifold:!!cl.manifold});
    }
    return report;
  }
  function openCheckModelDlg(){
    closeDlg();
    var report=bimCheckModel();
    var bad=report.filter(function(r){return !r.ok;});
    var rows=report.length?report.map(function(r){
      return '<div class="a3d-dlgrow" data-checkid="'+r.id+'" style="cursor:pointer">'+
        '<span style="flex:1 1 auto">'+bimEsc(r.name)+' ('+bimEsc(r.type)+')</span>'+
        '<span style="color:'+(r.ok?'#7ec27e':'#e08080')+'">'+(r.ok?'OK':'ISSUE')+'</span></div>'+
        (r.ok?(r.note?'<div class="a3d-propnote">'+bimEsc(r.note)+'</div>':'')
             :'<div class="a3d-propnote">'+bimEsc(r.issue)+'</div>');
    }).join(''):'<div class="a3d-propnote">No solids in the project to check.</div>';
    var d=document.createElement('div');
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">Check Model</div><div class="a3d-dlgbody">'+
      '<div class="a3d-propnote">'+(bad.length?bad.length+' of '+report.length+' solid(s) flagged.':(report.length?'All '+report.length+' solid(s) passed.':''))+'</div>'+
      rows+'</div><div class="a3d-dlgft"><button data-a3dlg="cancel">Close</button></div>';
    el.root.appendChild(d);el.dlg=d;
    d.addEventListener('click',function(ev){
      var r=ev.target&&ev.target.closest?ev.target.closest('[data-checkid]'):null;
      if(r){
        var cko=objById(r.getAttribute('data-checkid')),ckw=cko?bimLayerPickRefusal(cko):'';   /* __acad3dV121 */
        if(!cko){a3dToast('That object no longer exists');return;}
        if(ckw){a3dToast(ckw);return;}
        A3D.sel=cko.id;A3D.selSet=[A3D.sel];refreshTree();paint();return;
      }
      var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;
      if(b)closeDlg();
    });
    if(bad.length)a3dToast('Check Model: '+bad.length+' of '+report.length+' solid(s) flagged');
    else if(report.length)a3dToast('Check Model: all '+report.length+' solid(s) passed');
    else a3dToast('Check Model: no solids in the project to check');
  }
  /* ---------- Linked (parametric) component clone: distinct from Duplicate (m:dup, an
     independent hard copy with no memory of its origin) and from Family instances (V21:
     placed instances are explicitly independent by design). A linked clone remembers its source
     object (linkSourceId) and its own placement offset from that source, so after editing the
     source's geometry the user can re-apply that shape to every clone at once via Sync Clones,
     instead of redoing the edit by hand once per copy. Like this file's existing Room boundary
     (a snapshot, not a live link until asked), sync here is explicit-on-demand rather than
     automatic on every source edit -- an honest scope rather than pretending to be fully live. ---------- */
  function cloneLinked(objId,dx,dy,dz){
    var src=objById(objId);
    if(!src||src.t!=='solid'||!src.mesh){a3dToast('Select a solid object to clone');return null;}
    pushUndo();
    dx=dx||0;dy=dy||0;dz=dz||0;
    var clone=JSON.parse(JSON.stringify(src));
    clone.id='a3d-'+Date.now().toString(36)+'-'+(A3D.seq++);
    A3D.counts.clone=(A3D.counts.clone||0)+1;
    clone.name=src.name+'_Clone'+A3D.counts.clone;
    clone.linkSourceId=src.id;
    clone.linkOffset=[dx,dy,dz];
    /* __acad3dV55: src.pos (the drag/Align/nudge offset -- see bimSyncOneClone) is baked into
       the clone's own mesh/bim fields here, exactly like the fixed linkOffset itself, and the
       clone's own .pos is reset to zero -- a clone is not draggable independently of a re-sync
       in any way that matters, so it has no reason to carry a nonzero .pos of its own, and
       leaving src.pos copied forward here (JSON.parse/stringify copies it by default) would
       double-count it the moment bimSyncOneClone re-syncs this clone later. */
    var spx0=(src.pos&&isFinite(src.pos[0]))?src.pos[0]:0;
    var spy0=(src.pos&&isFinite(src.pos[1]))?src.pos[1]:0;
    var spz0=(src.pos&&isFinite(src.pos[2]))?src.pos[2]:0;
    var tdx=dx+spx0,tdy=dy+spy0,tdz=dz+spz0;
    if(clone.mesh&&clone.mesh.v)clone.mesh={v:clone.mesh.v.map(function(v){return [v[0]+tdx,v[1]+tdy,v[2]+tdz];}),f:clone.mesh.f};
    if(clone.bim){
      if(typeof clone.bim.baseY==='number')clone.bim.baseY+=tdy;
      if(Array.isArray(clone.bim.centerline))clone.bim.centerline=clone.bim.centerline.map(function(p){return [p[0]+tdx,p[1]+tdz];});
      if(Array.isArray(clone.bim.profile))clone.bim.profile=clone.bim.profile.map(function(p){return [p[0]+tdx,p[1]+tdz];});
      if(Array.isArray(clone.bim.innerLoop))clone.bim.innerLoop=clone.bim.innerLoop.map(function(p){return [p[0]+tdx,p[1]+tdz];});
      if(Array.isArray(clone.bim.outerLoop))clone.bim.outerLoop=clone.bim.outerLoop.map(function(p){return [p[0]+tdx,p[1]+tdz];});
      if(Array.isArray(clone.bim.center))clone.bim.center=[clone.bim.center[0]+tdx,clone.bim.center[1]+tdz];
    }
    clone.pos=[0,0,0];
    A3D.objs.push(clone);
    refreshTree();paint();saveSoon();
    a3dToast('Linked clone created: '+clone.name);
    return clone.id;
  }
  function bimLinkedClonesOf(sourceId){
    return A3D.objs.filter(function(o){return o.linkSourceId===sourceId;});
  }
  /* __acad3dV53: single-clone sync, factored out of syncLinkedClones so the manual "Sync
     Clones" button and the automatic graph visitor (bimGraphVisit's o.linkSourceId branch,
     below) share one implementation instead of two copies that could drift apart. Fail-safe,
     the same shape as bimReapplyOpeningsToWall and bimRemeasureRoomFromSource: if the source
     is gone or has no mesh, the clone is left COMPLETELY UNCHANGED, a console.warn names it,
     and the failure is counted rather than the clone being blanked out. */
  function bimSyncOneClone(clone,ctx){
    if(!clone||!clone.linkSourceId)return false;
    var src=objById(clone.linkSourceId);
    if(!src||!src.mesh){
      console.warn('[BIM] '+clone.name+"'s link source is missing or has no mesh; it was NOT re-synced.");
      if(ctx)ctx.clonesFailed++;
      return false;
    }
    var lo=clone.linkOffset||[0,0,0];
    /* __acad3dV55: src may itself have been dragged/Aligned/nudged since the clone was created
       or last synced -- that lives entirely in src.pos, never baked into src.mesh/src.bim (see
       bimRemeasureRoomFromSource for the same convention), so it must be added on top of the
       clone's own fixed linkOffset here, or a moved source's clone would silently stop
       following it. */
    var spx=(src.pos&&isFinite(src.pos[0]))?src.pos[0]:0;
    var spy=(src.pos&&isFinite(src.pos[1]))?src.pos[1]:0;
    var spz=(src.pos&&isFinite(src.pos[2]))?src.pos[2]:0;
    var off=[lo[0]+spx,lo[1]+spy,lo[2]+spz];
    var srcCopy=JSON.parse(JSON.stringify(src));
    if(srcCopy.mesh&&srcCopy.mesh.v)clone.mesh={v:srcCopy.mesh.v.map(function(v){return [v[0]+off[0],v[1]+off[1],v[2]+off[2]];}),f:srcCopy.mesh.f};
    if(srcCopy.bim){
      var kLvl=clone.bim&&clone.bim.levelId;
      clone.bim=srcCopy.bim;
      if(typeof clone.bim.baseY==='number')clone.bim.baseY+=off[1];
      if(Array.isArray(clone.bim.centerline))clone.bim.centerline=clone.bim.centerline.map(function(p){return [p[0]+off[0],p[1]+off[2]];});
      if(Array.isArray(clone.bim.profile))clone.bim.profile=clone.bim.profile.map(function(p){return [p[0]+off[0],p[1]+off[2]];});
      /* __acad3dV55: innerLoop/outerLoop (read by bimRemeasureRoomFromSource when a room is
         sourced from THIS clone) and center (read for column clones) were never offset here
         before -- only centerline/profile were -- so a room built on a cloned wall, or a clone
         of a column, silently drifted out of sync with everything else this function fixes. */
      if(Array.isArray(clone.bim.innerLoop))clone.bim.innerLoop=clone.bim.innerLoop.map(function(p){return [p[0]+off[0],p[1]+off[2]];});
      if(Array.isArray(clone.bim.outerLoop))clone.bim.outerLoop=clone.bim.outerLoop.map(function(p){return [p[0]+off[0],p[1]+off[2]];});
      if(Array.isArray(clone.bim.center))clone.bim.center=[clone.bim.center[0]+off[0],clone.bim.center[1]+off[2]];
      if(kLvl)clone.bim.levelId=kLvl;
    }
    /* __acad3dV55: the clone's own .pos is reset every sync -- src.pos is now fully baked into
       the fields above, so leaving a stale .pos here would double-count that offset on top of
       the freshly-baked mesh. */
    clone.pos=[0,0,0];
    if(ctx)ctx.clonesUpdated++;
    return true;
  }
  function syncLinkedClones(sourceId){
    var src=objById(sourceId);
    if(!src||!src.mesh){a3dToast('Source object no longer exists');return 0;}
    var clones=bimLinkedClonesOf(sourceId),i;
    if(!clones.length){a3dToast('No linked clones reference this object');return 0;}
    pushUndo();
    var ctx={clonesUpdated:0,clonesFailed:0};
    for(i=0;i<clones.length;i++)bimSyncOneClone(clones[i],ctx);
    refreshTree();paint();saveSoon();
    a3dToast(ctx.clonesUpdated+' linked clone(s) synced to source'+(ctx.clonesFailed?' ('+ctx.clonesFailed+' could not be synced)':''));
    return ctx.clonesUpdated;
  }
