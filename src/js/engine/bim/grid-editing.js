  /* ================= __acad3dV98: selecting and editing a grid ================= */
  function bimGridById(id){
    var i;
    if(!id||!A3D.grids)return null;
    for(i=0;i<A3D.grids.length;i++)if(A3D.grids[i].id===id)return A3D.grids[i];
    return null;
  }
  /* The selected grid, or null. An object selection supersedes it. */
  function bimSelectedGrid(){
    if(!A3D.selGrid)return null;
    if(A3D.sel||(A3D.selSet&&A3D.selSet.length))return null;
    return bimGridById(A3D.selGrid);
  }
  function bimSelectGrid(id){
    var g=bimGridById(id);
    A3D.sel=null;A3D.sel2=null;A3D.selSet=[];
    A3D.selGrid=g?g.id:null;
    refreshLevels();refreshTree();paint();
    return !!g;
  }
  /* Picked where it is DRAWN: the line at the active level's elevation, and the two bubbles. */
  function bimPickGrid(x,y){
    if(A3D.section||!A3D.grids||!A3D.grids.length)return null;
    var V=camVecs(A3D.cam),W=cvW(),H=cvH(),y0=bimGetActiveLevel().elev;
    var best=null,bestD=Infinity,i,g,s1,s2,d,db;
    for(i=A3D.grids.length-1;i>=0;i--){
      g=A3D.grids[i];
      s1=toScreen([g.p1[0],y0,g.p1[1]],V,W,H);s2=toScreen([g.p2[0],y0,g.p2[1]],V,W,H);
      d=bimPointSegDist(x,y,s1[0],s1[1],s2[0],s2[1]);
      d=(d<6)?d:Infinity;
      db=Math.min(Math.sqrt((x-s1[0])*(x-s1[0])+(y-s1[1])*(y-s1[1])),
                  Math.sqrt((x-s2[0])*(x-s2[0])+(y-s2[1])*(y-s2[1])));
      if(db<=10)d=0;
      if(d<bestD){bestD=d;best=g;}
    }
    return best;
  }
  function bimRenameGrid(id,name){
    var g=bimGridById(id),i;
    if(!g){a3dToast('That grid no longer exists');return false;}
    name=String(name===undefined||name===null?'':name).replace(/^\s+|\s+$/g,'');
    if(!name){a3dToast('A grid needs a name');return false;}
    if(name===g.name)return true;
    for(i=0;i<A3D.grids.length;i++){
      if(A3D.grids[i].id!==id&&A3D.grids[i].name===name){
        a3dToast('Grid '+name+' already exists - grid names must be unique');return false;
      }
    }
    pushUndo();
    var was=g.name;
    g.name=name;
    refreshLevels();refreshProps();paint();saveSoon();
    a3dToast('Grid '+was+' renamed to '+name);
    return true;
  }
  function bimSetGridEnds(id,p1,p2){
    var g=bimGridById(id);
    if(!g){a3dToast('That grid no longer exists');return false;}
    if(!p1||!p2||!isFinite(p1[0])||!isFinite(p1[1])||!isFinite(p2[0])||!isFinite(p2[1])){
      a3dToast('Grid ends must be numbers');return false;
    }
    var dx=p2[0]-p1[0],dz=p2[1]-p1[1];
    if(Math.sqrt(dx*dx+dz*dz)<1e-6){a3dToast('Grid line is too short');return false;}
    pushUndo();
    g.p1=[p1[0],p1[1]];g.p2=[p2[0],p2[1]];
    refreshProps();paint();saveSoon();
    return true;
  }
  function bimGridPropsHtml(g){
    var dx=g.p2[0]-g.p1[0],dz=g.p2[1]-g.p1[1];
    var h='<div class="a3d-ptypehd">'+
      '<div class="a3d-ptypeic">'+(a3drIcon('bim:grid')||a3drIcon('box'))+'</div>'+
      '<div class="a3d-ptypetx"><div class="a3d-ptypename">Grid '+bimEsc(g.name)+'</div>'+
      '<div class="a3d-ptypesub">Grids : Grid</div></div>'+
      '<button class="a3d-pedit" data-gridact="delete" title="Delete this grid">Delete</button>'+
      '</div>';
    var ident=bimPropRow('Name','<input type="text" data-gridf="name" value="'+bimEsc(g.name)+'">');
    function lenIn(label,v,f){
      return bimPropRow(bimLenLabel(label),'<input type="number" step="any" data-gridf="'+f+
        '" value="'+bimDispLen(v)+'">');
    }
    var geo=lenIn('Start X',g.p1[0],'x1')+lenIn('Start Y',g.p1[1],'y1')+
            lenIn('End X',g.p2[0],'x2')+lenIn('End Y',g.p2[1],'y2')+
            bimPropLenText('Length',Math.sqrt(dx*dx+dz*dz));
    return h+bimPropGroup('Identity Data',ident)+bimPropGroup('Extents',geo);
  }
  function startGridTool(){
    closeDlg();
    bimEnterDraftingMode();
    var lvl=bimGetActiveLevel();
    A3D.sk={tool:'grid',pts:[],y:lvl.elev,on:null};
    a3dToast('Grid: click the start and end of the grid line');
    paint();
  }
  function drawGrids(ctx,V,W,H){
    if(A3D.section)return;
    if(!A3D.grids||!A3D.grids.length)return;
    var y0=bimGetActiveLevel().elev,i,selG=bimSelectedGrid();
    ctx.save();
    for(i=0;i<A3D.grids.length;i++){
      var g=A3D.grids[i],gSel=(selG&&selG.id===g.id);   /* __acad3dV98 */
      var s1=toScreen([g.p1[0],y0,g.p1[1]],V,W,H),s2=toScreen([g.p2[0],y0,g.p2[1]],V,W,H);
      ctx.beginPath();
      ctx.moveTo(s1[0],s1[1]);ctx.lineTo(s2[0],s2[1]);
      ctx.strokeStyle=gSel?'#4ea1ff':'#6f7681';
      ctx.lineWidth=gSel?1.6:1;
      ctx.setLineDash([9,4,2,4]);
      ctx.stroke();
      ctx.setLineDash([]);
      /* Bubble at both ends, the way a Revit grid head reads in plan. */
      var ends=[s1,s2],k;
      for(k=0;k<2;k++){
        ctx.beginPath();
        ctx.arc(ends[k][0],ends[k][1],9,0,Math.PI*2);
        ctx.fillStyle='rgba(20,22,26,0.85)';ctx.fill();
        ctx.strokeStyle=gSel?'#4ea1ff':'#8f97a3';ctx.lineWidth=gSel?1.6:1.1;ctx.stroke();
        ctx.font='bold 9px system-ui,sans-serif';
        ctx.textAlign='center';ctx.textBaseline='middle';
        ctx.fillStyle='#dfe4ea';
        ctx.fillText(g.name,ends[k][0],ends[k][1]);
      }
    }
    ctx.restore();
  }
  /* ---------- Phase 42: parametric beam engine ----------
     A beam is a horizontal prism swept along its plan axis. Unlike a column it cannot use
     padMesh (which only extrudes vertically), so the six faces are emitted directly with
     outward winding. Revit hangs a beam below its level, so the level elevation is the
     top of the section and depth runs downward. ---------- */
