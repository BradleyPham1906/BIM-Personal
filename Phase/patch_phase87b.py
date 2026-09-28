"""patch_phase87b.py -- Phase 87 part 2: the command layer for the modify toolbox.

Model-touching apply functions, the pick tools that feed them, and their dialogs. Inserted
ahead of openOffsetDlg, beside the Trim/Offset/Align command layer it matches.
"""
import hashlib, pathlib, sys

BASE = '5a819c87fad2021aafddb6cc5fe4afe6de6c72e3645c97a779482b8dace5a563'
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')

src = P.read_text(encoding='utf-8')
h0 = hashlib.sha256(src.encode('utf-8')).hexdigest()
assert h0 == BASE, 'baseline hash mismatch: %s' % h0
b0 = len(src.encode('utf-8'))

ANCHOR = "  function openOffsetDlg(){"
assert src.count(ANCHOR) == 1, 'anchor count %d' % src.count(ANCHOR)

BLOCK = r'''  /* ---------- __acad3dV87: the command layer over the Phase 87 geometry core.

     One rule runs through all of it: a wall that comes out of a modify command is the SAME
     BIM object it was going in -- same level, same wall type, same material, same layer -- and
     a wall newly created by one (Break's second piece, Chamfer's bevel) inherits those from the
     wall it came from. bimDuplicateObject does not copy typeId/typeCat, so a copied wall
     silently loses its type; that is not repeated here. ---------- */
  function bimNewWallFromSource(src,pts,closed,nameHint){
    var res=bimBuildWallGeometry(pts,src.bim.baseY,src.bim.height,src.bim.thickness,src.bim.align,!!closed);
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
  function bimRebuildWallFrom(o,pts,closed){
    var res=bimBuildWallGeometry(pts,o.bim.baseY,o.bim.height,o.bim.thickness,o.bim.align,!!closed);
    if(res.error)return {error:res.error};
    var keepLevel=o.bim.levelId,keepType=o.bim.typeId,keepCat=o.bim.typeCat;
    o.mesh=res.mesh;
    o.bim=res.bim;
    o.bim.levelId=keepLevel;
    if(keepType)o.bim.typeId=keepType;
    if(keepCat)o.bim.typeCat=keepCat;
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
        var d=bimPtSegDist2D(clickPt,cl[k],cl[(k+1)%n]);
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
      var r=bimExtendPolyline(target.bim.centerline,target.bim.closed,
                              bound.bim.centerline,bound.bim.closed,clickPt);
      if(r.error){a3dToast('Extend: '+r.error);return false;}
      pushUndo();
      var rb=bimRebuildWallFrom(target,r.pts,target.bim.closed);
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
      var r=bimBreakPolyline(w.bim.centerline,w.bim.closed,p1,p2);
      if(r.error){a3dToast('Break: '+r.error);return false;}
      var made=bimNewWallFromSource(w,r.b,false,'Wall');
      if(made.error){a3dToast('Break: '+made.error);return false;}
      pushUndo();
      var rb=bimRebuildWallFrom(w,r.a,false);
      if(rb.error){a3dToast('Break: '+rb.error);return false;}
      A3D.objs.push(made.obj);
      A3D.sel=w.id;A3D.sel2=null;A3D.selSet=[w.id,made.obj.id];
      refreshTree();refreshHud();paint();saveSoon();
      a3dToast(p2?('Broken into 2 walls, '+bimFmtLen(Math.abs(r.removed))+' removed')
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
    var cur=bimPolyLength(w.bim.centerline,w.bim.closed);
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
      var r=bimLengthenPolyline(w.bim.centerline,w.bim.closed,mode,value,clickPt);
      if(r.error){a3dToast('Lengthen: '+r.error);return false;}
      pushUndo();
      var rb=bimRebuildWallFrom(w,r.pts,w.bim.closed);
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
    else if(g.kind==='room'){o.pts=g.pts;o.sourceType=null;o.sourceId=null;
      if(typeof bimPolyArea==='function')o.area=Math.abs(bimPolyArea(o.pts));}
    else if(g.kind==='text'){o.pt=g.pt;}
    else if(g.kind==='dim'){o.p1=g.p1;o.p2=g.p2;o.d1=g.d1;o.d2=g.d2;
      o.length=Math.sqrt((g.p2[0]-g.p1[0])*(g.p2[0]-g.p1[0])+(g.p2[1]-g.p1[1])*(g.p2[1]-g.p1[1]));}
    else if(g.kind==='wall'||g.kind==='floor'||g.kind==='column'){o.mesh=g.mesh;o.bim=Object.assign(o.bim,g.bim);bimAfterWallRebuild(o);}
    else if(g.kind==='mesh'){o.mesh=g.mesh;}
    else if(g.kind==='pos'){o.pos=g.pos;}
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
    return ok>0;
  }
  /* FILLET at radius 0 is exactly the corner miter Join Walls already performs, so it dispatches
     there rather than growing a second implementation of the same corner. The toast names the
     radius so nobody reads this as a rounded fillet; a radius fillet needs arc storage, which
     Phase 88 decides. */
  function applyFilletCorner(){
    var a=objById(A3D.sel),b=objById(A3D.sel2);
    if(!a||!b||a===b){a3dToast('Fillet needs two walls: click the first, Ctrl+click the second');return;}
    applyWallJoin();
    a3dToast('Filleted at radius 0 (square corner). A rounded fillet needs arc geometry, which this build does not store yet.');
  }
'''

out = src.replace(ANCHOR, BLOCK + ANCHOR, 1)
assert out != src
b1 = len(out.encode('utf-8'))
P.write_text(out, encoding='utf-8')
print('bytes before %d  after %d  (+%d)' % (b0, b1, b1 - b0))
print('sha256 %s' % hashlib.sha256(out.encode('utf-8')).hexdigest())
