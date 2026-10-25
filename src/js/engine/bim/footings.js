  /* ================= __acad3dV102: footings ================= */
  /* The strip's length is the wall's, measured along the curve (V89). */
  function bimFootingLength(o){
    if(!o||!o.bim)return 0;
    if(o.bim.type==='footing')return o.bim.length||0;
    return o.bim.centerline?bimWallLength(o.bim.centerline,!!o.bim.closed,o.bim.bulges||null):0;
  }
  function bimFootingVolume(o){
    if(!o||!o.bim)return 0;
    if(o.bim.type==='footing')return (o.bim.width||0)*(o.bim.length||0)*(o.bim.thickness||0);
    return bimFootingLength(o)*(o.bim.width||0)*(o.bim.thickness||0);
  }
  function bimIsFooting(o){return !!(o&&o.t==='solid'&&o.bim&&(o.bim.type==='footing'||o.bim.type==='stripfooting'));}
  function bimFootingHostOf(o){return (o&&o.bim&&o.bim.hostId)?objById(o.bim.hostId):null;}
  /* The ONE derivation: host (world) -> footing (its own frame). {mesh,set} or {error}. */
  function bimFootingGeometry(o){
    var b=o.bim,q=bimObjOffset(o),h=bimFootingHostOf(o),hq,res;
    if(!(b.width>0)||!(b.thickness>0))return {error:'its size must be positive'};
    if(b.type==='footing'){
      if(!(b.length>0))return {error:'its length must be positive'};
      var c,top,rot;
      if(h){
        if(!(h.t==='solid'&&h.bim&&h.bim.type==='column'&&h.bim.center))return {error:'its host is no longer a column'};
        hq=bimObjOffset(h);
        c=[h.bim.center[0]+hq[0]-q[0],h.bim.center[1]+hq[2]-q[2]];
        top=(h.bim.baseY||0)+hq[1]-q[1];rot=h.bim.rotation||0;
      }else{
        if(!b.center)return {error:'it has no position'};
        c=b.center;top=b.topY;rot=b.rotation||0;
      }
      res=bimBuildColumnGeometry(c,top-b.thickness,b.width,b.length,b.thickness,rot);
      if(res.error)return res;
      return {mesh:res.mesh,set:{center:[c[0],c[1]],topY:top,baseY:top-b.thickness,rotation:rot,
              plan:[bimRectFootprint(c,b.width,b.length,rot)]}};
    }
    var cl,bul,closed,top2,off;
    if(h){
      if(!(h.t==='solid'&&h.bim&&h.bim.type==='wall'&&h.bim.centerline&&h.bim.centerline.length>=2))
        return {error:'its host is no longer a wall'};
      hq=bimObjOffset(h);
      cl=h.bim.centerline.map(function(p){return [p[0]+hq[0]-q[0],p[1]+hq[2]-q[2]];});
      bul=bimHasBulge(h.bim.bulges)?h.bim.bulges.slice():null;closed=!!h.bim.closed;
      top2=(h.bim.baseY||0)+hq[1]-q[1];
      var wo=bimAlignOffsets(h.bim.thickness,h.bim.align);
      off=(wo.dLeft-wo.dRight)/2;
    }else{
      if(!b.centerline)return {error:'it has no path'};
      cl=b.centerline;bul=b.bulges||null;closed=!!b.closed;top2=b.topY;off=b.bodyOffset||0;
    }
    var hw=b.width/2;
    res=bimBuildWallGeometry(cl,top2-b.thickness,b.thickness,b.width,{dLeft:hw+off,dRight:hw-off},closed,bul);
    if(res.error)return res;
    var flat=bimHasBulge(bul)?bimFlattenPoly(cl,bul,closed):cl;
    var ra=bimOffsetRing(flat,hw+off,closed),rb=bimOffsetRing(flat,-(hw-off),closed);
    var plan=closed?[ra,rb]:[ra.concat(rb.slice().reverse())];
    return {mesh:res.mesh,set:{plan:plan,centerline:cl.map(function(p){return [p[0],p[1]];}),bulges:bul,closed:closed,
            topY:top2,baseY:top2-b.thickness,bodyOffset:off}};
  }
  function bimRebuildFooting(o,ctx){
    var g=bimFootingGeometry(o),k;
    if(g.error){
      console.warn('[BIM] '+o.name+': '+g.error+'; it was NOT updated.');
      if(ctx)ctx.dependentsFailed=(ctx.dependentsFailed||0)+1;
      else a3dToast(o.name+' could not be rebuilt: '+g.error);
      return false;
    }
    o.mesh=g.mesh;
    for(k in g.set)if(g.set.hasOwnProperty(k))o.bim[k]=g.set[k];
    A3D.meshes={};
    if(ctx)ctx.dependentsUpdated=(ctx.dependentsUpdated||0)+1;
    return true;
  }
  function bimFootingOf(hostId){
    var i;
    for(i=0;i<A3D.objs.length;i++)if(bimIsFooting(A3D.objs[i])&&A3D.objs[i].bim.hostId===hostId)return A3D.objs[i];
    return null;
  }
  /* The first type in the category is the default, as the dialogs' first option is. */
  function bimNewFooting(host){
    var isCol=!!(host&&host.t==='solid'&&host.bim&&host.bim.type==='column'&&host.bim.center);
    var isWall=!!(host&&host.t==='solid'&&host.bim&&host.bim.type==='wall'&&host.bim.centerline);
    if(!isCol&&!isWall)return {error:'A footing goes under a column or a wall'};
    var cat=isCol?'footing':'stripfooting';
    bimEnsureTypes();
    var t=A3D.types[cat][0];
    A3D.counts[cat]=(A3D.counts[cat]||0)+1;
    var o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',
      name:(isCol?'Footing_':'Wall Foundation_')+A3D.counts[cat],col:'#a8a295',pos:[0,0,0],mesh:null,
      layer:A3D.activeLayer,
      bim:{type:cat,hostId:host.id,typeId:t.id,typeCat:cat,levelId:bimObjectLevelId(host)||A3D.activeLevel}},k;
    for(k in t.params)if(t.params.hasOwnProperty(k))o.bim[k]=t.params[k];
    var g=bimFootingGeometry(o);
    if(g.error)return {error:g.error};
    o.mesh=g.mesh;
    for(k in g.set)if(g.set.hasOwnProperty(k))o.bim[k]=g.set[k];
    return {obj:o};
  }
  function bimAddFootingUnder(host,quiet){
    if(!host)return null;
    var ex=bimFootingOf(host.id);
    if(ex){if(!quiet)a3dToast(host.name+' already has '+ex.name);return null;}
    var r=bimNewFooting(host);
    if(r.error){if(!quiet)a3dToast('Footing: '+r.error);return null;}
    if(!quiet)pushUndo();
    A3D.objs.push(r.obj);
    A3D.meshes={};
    if(!quiet){refreshTree();paint();saveSoon();a3dToast(r.obj.name+' placed under '+host.name);}
    return r.obj;
  }
  /* World-aware pickers for the footing tools: a column whose footprint holds the point (or the
     nearest column centre within 1 m), a wall whose centreline passes within 1 m. */
  function bimColumnAtWorld(pt){
    var best=null,bd=1.0,i,o,q,d;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(!(o.t==='solid'&&o.bim&&o.bim.type==='column'&&o.bim.center))continue;
      if(bimObjectLevelId(o)&&bimObjectLevelId(o)!==A3D.activeLevel)continue;
      q=bimObjOffset(o);
      d=Math.sqrt(Math.pow(pt[0]-o.bim.center[0]-q[0],2)+Math.pow(pt[1]-o.bim.center[1]-q[2],2));
      if(d<Math.max(bd,Math.max(o.bim.width||0,o.bim.depth||0)/2)&&(!best||d<bd)){best=o;bd=d;}
    }
    return best;
  }
  function bimWallAtWorld(pt){
    var best=null,bd=1.0,i,o,q,cl,n,segs,k,d;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(!(o.t==='solid'&&o.bim&&o.bim.type==='wall'&&o.bim.centerline))continue;
      if(bimObjectLevelId(o)&&bimObjectLevelId(o)!==A3D.activeLevel)continue;
      q=bimObjOffset(o);
      cl=o.bim.centerline.map(function(p){return [p[0]+q[0],p[1]+q[2]];});
      n=cl.length;segs=o.bim.closed?n:n-1;
      for(k=0;k<segs;k++){
        d=bimPtDistToBulgedSeg(pt,cl[k],cl[(k+1)%n],bimBulgeAt(o.bim.bulges,k)).dist;
        if(d<bd){bd=d;best=o;}
      }
    }
    return best;
  }
  /* Every column on the level that has no footing. One undo step. */
  function bimFootingsUnderAllColumns(){
    var todo=[],i,o;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(o.t==='solid'&&o.bim&&o.bim.type==='column'&&o.bim.center&&
         (!bimObjectLevelId(o)||bimObjectLevelId(o)===A3D.activeLevel)&&!bimFootingOf(o.id))todo.push(o);
    }
    if(!todo.length){a3dToast('Every column on '+bimGetActiveLevel().name+' already has a footing (or there are none)');return [];}
    pushUndo();
    var made=[];
    for(i=0;i<todo.length;i++){var f=bimAddFootingUnder(todo[i],true);if(f)made.push(f.id);}
    refreshTree();paint();saveSoon();
    a3dToast(made.length+' footing'+(made.length===1?'':'s')+' placed'+
      (made.length<todo.length?' ('+(todo.length-made.length)+' could not be built - see console)':''));
    return made;
  }
  /* A host that went some other way than Delete: the footing keeps its shape, and is told. */
  function bimSweepFootingHosts(){
    var i,o,n=0;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(bimIsFooting(o)&&o.bim.hostId&&!objById(o.bim.hostId)){o.bim.hostId=null;n++;}
    }
    if(n)a3dToast(n+' footing'+(n===1?' is':'s are')+' no longer under anything - the host was removed; kept where they are');
    return n;
  }
  function startFootingTool(kind){
    closeDlg();
    bimEnterDraftingMode();
    var lvl=bimGetActiveLevel();
    A3D.sk={tool:kind==='wall'?'wallfoundation':'footing',pts:[],y:lvl.elev,on:null};
    bimSyncStatusHint();paint();
    a3dToast(kind==='wall'?'Wall Foundation: click a wall; Escape when finished':'Isolated Footing: click a column; Escape when finished');
  }
  function startFoundationSlabTool(){
    closeDlg();
    bimEnterDraftingMode();
    var lvl=bimGetActiveLevel();
    A3D.sk={tool:'foundslab',pts:[],y:lvl.elev,on:null};
    bimSyncStatusHint();paint();
    a3dToast('Foundation Slab: click inside an enclosed region on '+lvl.name);
  }
  /* A foundation slab is a floor in the foundation category: same geometry, same region
     following (V99), its own name and flag, 300 mm by default. */
  function bimFoundationSlabAt(pt,y){
    var b=bimFindRoomBoundaryAt(pt,y);
    if(!b){a3dToast('Foundation Slab: click inside an enclosed region');return null;}
    var o=buildFloorSolid(bimFloorProfileFrom(b),0.3,'Concrete Slab',bimGetActiveLevel());
    if(!o)return null;
    A3D.counts.foundslab=(A3D.counts.foundslab||0)+1;
    o.name='Foundation Slab_'+A3D.counts.foundslab;
    o.bim.structural='foundation';
    o.col='#a8a295';
    refreshTree();paint();saveSoon();
    a3dToast(o.name+' created');
    return o;
  }
  function bimAlignOffsets(thickness,align){
    /* __acad3dV102: explicit side offsets, for a strip centred under a wall's body */
    if(align&&typeof align==='object'&&isFinite(align.dLeft)&&isFinite(align.dRight))return align;
    if(align==='left')return {dLeft:0,dRight:thickness};
    if(align==='right')return {dLeft:thickness,dRight:0};
    return {dLeft:thickness/2,dRight:thickness/2};
  }
  function startWallTool(){
    closeDlg();
    bimEnterDraftingMode();
    var lvl=bimGetActiveLevel();
    A3D.sk={tool:'wall',pts:[],y:lvl.elev,on:null};
    a3dToast('Wall on '+lvl.name+': click along the centerline. C = close the loop, Enter = finish open, Escape = cancel');
    paint();
  }
  function finishWall(closed){
    var sk=A3D.sk;
    if(!sk||sk.pts.length<2){a3dToast('Wall needs at least 2 points');A3D.sk=null;paint();return;}
    openWallDlg(sk.pts.slice(),sk.y,!!closed,sk.bulges?sk.bulges.slice():null);   /* __acad3dV90 */
  }
  /* __acad3dV100: what the wall dialog offers, and what an interrupted chain is built with. */
  function bimWallDlgDefaults(){
    var lvl=bimGetActiveLevel();
    return {thk:0.3,hgt:lvl.height,align:'center'};
  }
  function openWallDlg(pts,y0,closed,bulges){
    closeDlg();
    var lvl=bimGetActiveLevel(),wd=bimWallDlgDefaults();
    var d=document.createElement('div');
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">Wall parameters</div>'+
      '<div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Thickness</label><input type="number" step="any" min="0.02" data-a3dp="thk" value="'+wd.thk+'"></div>'+
      '<div class="a3d-dlgrow"><label>Height</label><input type="number" step="any" min="0.1" data-a3dp="hgt" value="'+wd.hgt+'"></div>'+
      '<div class="a3d-dlgrow"><label>Alignment</label><select data-a3dp="align">'+
        '<option value="center">Center</option><option value="left">Left</option><option value="right">Right</option>'+
      '</select></div>'+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">OK</button></div>';
    el.root.appendChild(d);
    el.dlg=d;
    var thkI=d.querySelector('[data-a3dp="thk"]'),hgtI=d.querySelector('[data-a3dp="hgt"]'),alignI=d.querySelector('[data-a3dp="align"]');
    function submit(){
      var thk=parseFloat(thkI.value),hgt=parseFloat(hgtI.value),align=alignI.value;
      var eb=document.getElementById('a3d-dlgerr');
      if(!isFinite(thk)||thk<=0){eb.textContent='Thickness must be a positive number';return;}
      if(!isFinite(hgt)||hgt<=0){eb.textContent='Height must be a positive number';return;}
      closeDlg();
      A3D.sk=null;
      buildWallSolid(pts,y0,hgt,thk,align,closed,bulges);   /* __acad3dV90 */
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
    thkI.focus();thkI.select();
  }
