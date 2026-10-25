  // ---- __acad3dV44: Sheets (printable layouts). A Sheet is a titled page composing one or more
  // Viewports, each a scaled window onto an existing orthographic Plan/Elevation/Section view (or
  // a Schedule table, drawn as a table). Viewports are rendered by temporarily redirecting the
  // existing paint() pipeline at an offscreen canvas sized and framed for that viewport, then
  // compositing the result onto the sheet canvas -- this reuses the proven plan/elevation/section
  // renderer exactly as-is instead of duplicating it, at the cost of being restricted to
  // orthographic (flat) sources: a perspective 3D view has no fixed "scale" to print at, so
  // (matching real CAD/BIM practice) only Plan, Elevation, Section and Schedule content can be
  // placed on a sheet -- attempting to add a perspective 3D view is rejected with a clear reason
  // rather than silently producing an unscaled drawing. Fail-safe: any viewport whose source can
  // no longer be resolved (a deleted view or level) renders as a labeled placeholder box with a
  // console warning instead of crashing the sheet; any render that throws is caught per-viewport
  // so one bad viewport cannot blank the rest of the sheet.
  var SHEET_SIZES={
    'ANSI-A':{label:'ANSI A / Letter (8.5x11 in)',w:215.9,h:279.4},
    'ANSI-B':{label:'ANSI B / Tabloid (11x17 in)',w:279.4,h:431.8},
    /* __acad3dV116: every size here was portrait, and drawing sheets are landscape -- the way an
       AutoCAD page setup and a Revit title block lay them out. The portrait sizes stay for the
       sheets already made with them. */
    'ANSI-B-L':{label:'ANSI B landscape (17x11 in)',w:431.8,h:279.4},
    'ANSI-D-L':{label:'ANSI D landscape (36x24 in)',w:914.4,h:609.6},
    'A3-L':{label:'A3 landscape (420x297 mm)',w:420,h:297},
    'A1-L':{label:'A1 landscape (841x594 mm)',w:841,h:594},
    'ANSI-D':{label:'ANSI D (24x36 in)',w:609.6,h:914.4},
    'A4':{label:'A4 (210x297 mm)',w:210,h:297},
    'A3':{label:'A3 (297x420 mm)',w:297,h:420},
    'A1':{label:'A1 (594x841 mm)',w:594,h:841},
    'Custom':{label:'Custom size',w:420,h:297}
  };
  var SHEET_NEW_SIZE='ANSI-B-L';   /* __acad3dV116: what + and New Sheet start from */
  /* __acad3dV116: the standard metric scales, detail to site. The five that were here stopped at
     1:500, too coarse for the civil work this app is for, and they are also the steps the wheel
     takes in a viewport, so a viewport's scale is always one a drawing set can carry. */
  var SHEET_SCALES=[
    {label:'1:1',denom:1},{label:'1:2',denom:2},{label:'1:5',denom:5},{label:'1:10',denom:10},
    {label:'1:20',denom:20},{label:'1:25',denom:25},{label:'1:50',denom:50},{label:'1:100',denom:100},
    {label:'1:200',denom:200},{label:'1:250',denom:250},{label:'1:500',denom:500},{label:'1:1000',denom:1000},
    {label:'1:1250',denom:1250},{label:'1:2000',denom:2000},{label:'1:2500',denom:2500},{label:'1:5000',denom:5000}
  ];
  var SHEET_PREVIEW_PXMM=3.0, SHEET_EXPORT_PXMM=6.0;
  var A3D_SHEET_SCRATCH=null;

  function bimNewSheet(number,name,sizeKey){
    var sz=SHEET_SIZES[sizeKey]||SHEET_SIZES['ANSI-B'];
    return {id:'sheet-'+Date.now().toString(36)+'-'+Math.floor(Math.random()*1e6),
      number:number||bimNextSheetNumber(),name:name||'Untitled',   /* __acad3dV116 */
      sizeKey:sizeKey||'ANSI-B',w:sz.w,h:sz.h,viewports:[]};
  }
  /* __acad3dV116: the one label for a sheet -- layout tab, sheet toolbar, HUD, Project Browser
     and print title all read it, so a rename shows everywhere at once. */
  function bimSheetLabel(sh){
    if(!sh)return 'Sheet';
    var n=String(sh.number==null?'':sh.number).trim(),m=String(sh.name==null?'':sh.name).trim();
    return (n&&m)?(n+' - '+m):(n||m||'Sheet');
  }
  /* __acad3dV116: the next number no sheet has. It was 'A'+(101+count), which repeats a number as
     soon as one sheet is deleted: with A101 and A102, delete A101 and the next sheet was A102 again. */
  function bimNextSheetNumber(){
    var max=100,i,m;
    for(i=0;i<A3D.sheets.length;i++){
      m=/^A(\d+)$/i.exec(String(A3D.sheets[i].number==null?'':A3D.sheets[i].number).trim());
      if(m&&+m[1]>max)max=+m[1];
    }
    return 'A'+(max+1);
  }
  /* __acad3dV116: three places deleted a sheet, two asked first in different words, one did not ask.
     One path now: it names the sheet and says the delete can be undone, which it can. */
  function bimConfirmDeleteSheet(id){
    var sh=bimSheetById(id);
    if(!sh)return false;
    if(!window.confirm('Delete sheet "'+bimSheetLabel(sh)+'"? Undo (Ctrl+Z) brings it back.'))return false;
    return bimDeleteSheet(id);
  }
  function bimSheetById(id){
    var i;for(i=0;i<A3D.sheets.length;i++)if(A3D.sheets[i].id===id)return A3D.sheets[i];
    return null;
  }
  function bimAddSheet(number,name,sizeKey){
    pushUndo();
    var s=bimNewSheet(number,name,sizeKey);
    A3D.sheets.push(s);
    A3D.activeSheetId=s.id;
    refreshBrowser();saveSoon();
    return s;
  }
  function bimDeleteSheet(id){
    var i;
    for(i=0;i<A3D.sheets.length;i++){
      if(A3D.sheets[i].id===id){
        pushUndo();
        A3D.sheets.splice(i,1);
        var wasOn=(A3D.activeSheetId===id&&bimSheetOnScreen());   /* __acad3dV116 */
        /* __acad3dV122: in Pages the reader stays in the document, on the page that took its place */
        var inPages=wasOn&&A3D_PAGES.display==='pages'&&A3D.sheets.length>0;
        if(A3D.activeSheetId===id)A3D.activeSheetId=A3D.sheets.length?A3D.sheets[inPages?Math.min(i,A3D.sheets.length-1):0].id:null;
        if(inPages)bimSetActiveView('sheet',A3D.activeSheetId,null);
        else if(wasOn)bimShowModel();
        refreshBrowser();bimSheetViewRefresh();saveSoon();
        a3dToast('Sheet deleted');
        return true;
      }
    }
    return false;
  }
  function bimNewViewport(kind,refId,label){
    return {id:'vp-'+Date.now().toString(36)+'-'+Math.floor(Math.random()*1e6),
      kind:kind,refId:refId,label:label||'',x:20,y:20,w:120,h:90,scaleMode:'fit',scaleDenom:100};
  }
  // Mirrors the Project Browser's Views/Schedules groups so a sheet can only reference things
  // that actually exist -- a fail-safe reference by id, not free text.
  function bimSheetSourceOptions(){
    var out=[],i;
    for(i=0;i<A3D.levels.length;i++)out.push({kind:'plan',refId:A3D.levels[i].id,label:'Floor Plan: '+A3D.levels[i].name});
    ['front','back','left','right'].forEach(function(k){out.push({kind:'elevation',refId:k,label:VIEWS[k].label});});
    for(i=0;i<A3D.views.length;i++){
      var v=A3D.views[i];
      if(!v.flat)continue; // perspective 3D views have no fixed print scale -- see header note
      out.push({kind:'view',refId:v.id,label:(v.section?'Section: ':'View: ')+v.name});
    }
    /* __acad3dV74: derived too -- a registered schedule has to be placeable on a sheet, or the
       takeoff it produces cannot reach a drawing set. */
    bimScheduleKeys().forEach(function(k){
      out.push({kind:'schedule',refId:k,label:'Schedule: '+SCHEDULE_DEFS[k].label});
    });
    return out;
  }
  function bimResolveViewportSource(vp){
    if(vp.kind==='plan'){
      var lv=null,i;for(i=0;i<A3D.levels.length;i++)if(A3D.levels[i].id===vp.refId){lv=A3D.levels[i];break;}
      if(!lv)return {error:'Level no longer exists'};
      return {label:'Floor Plan: '+lv.name,cam:{yaw:0,pitch:1.52,tx:0,ty:lv.elev+0.01,tz:0},flat:true,
        levelId:lv.id,levelFilter:true,section:null};
    }
    if(vp.kind==='elevation'){
      var v=VIEWS[vp.refId];
      if(!v)return {error:'Unknown elevation preset'};
      return {label:v.label,cam:{yaw:v.yaw,pitch:v.pitch,tx:0,ty:1,tz:0},flat:true,
        levelId:null,levelFilter:false,section:null};
    }
    if(vp.kind==='view'){
      var sv=null,j;for(j=0;j<A3D.views.length;j++)if(A3D.views[j].id===vp.refId){sv=A3D.views[j];break;}
      if(!sv)return {error:'Saved view no longer exists'};
      if(!sv.flat)return {error:'Perspective views cannot be placed on a sheet'};
      return {label:(sv.section?'Section: ':'View: ')+sv.name,
        cam:{yaw:sv.cam.yaw,pitch:sv.cam.pitch,tx:sv.cam.tx,ty:sv.cam.ty,tz:sv.cam.tz},
        flat:true,levelId:sv.levelId,levelFilter:!!sv.levelFilter,section:sv.section};
    }
    if(vp.kind==='schedule'){
      var def=SCHEDULE_DEFS[vp.refId];
      if(!def)return {error:'Unknown schedule category'};
      return {label:'Schedule: '+def.label,schedule:vp.refId};
    }
    return {error:'Unknown viewport type'};
  }
  // Projects every visible object's world AABB corners into camera space (independent of `dist`,
  // since translation along the view direction cannot move a point's projection in an orthographic
  // camera) to find the on-screen extent a "fit" viewport must frame.
  function bimFlatExtent(camBase,levelFilterOn,levelId){
    var V=camVecs({yaw:camBase.yaw,pitch:camBase.pitch,dist:1,tx:camBase.tx,ty:camBase.ty,tz:camBase.tz});
    var xmin=1e18,xmax=-1e18,ymin=1e18,ymax=-1e18,found=false,i,j;
    for(i=0;i<A3D.objs.length;i++){
      var o=A3D.objs[i];
      if(!bimLayerShown(o))continue;   /* __acad3dV121 */
      if(levelFilterOn){
        var lv=bimObjectLevelId(o);
        if(lv&&lv!==levelId)continue;
      }
      var bb=bimWorldBounds([o.id]);if(!bb)continue;   /* __acad3dV104: sketches, rooms, text, parcels too */
      for(j=0;j<8;j++){
        var p=[(j&1)?bb.mx[0]:bb.mn[0],(j&2)?bb.mx[1]:bb.mn[1],(j&4)?bb.mx[2]:bb.mn[2]];
        var dx=p[0]-V.eye[0],dy=p[1]-V.eye[1],dz=p[2]-V.eye[2];
        var xc=dx*V.r[0]+dy*V.r[1]+dz*V.r[2];
        var yc=dx*V.u[0]+dy*V.u[1]+dz*V.u[2];
        if(xc<xmin)xmin=xc;if(xc>xmax)xmax=xc;if(yc<ymin)ymin=yc;if(yc>ymax)ymax=yc;
        found=true;
      }
    }
    if(!found)return null;
    return {xmin:xmin,xmax:xmax,ymin:ymin,ymax:ymax,V:V};
  }
  // Solves the camera (yaw/pitch kept, dist+target adjusted) that frames a resolved viewport
  // source at a given pixel size, either at an explicit architectural ratio (paperMM =
  // modelMeters*1000/scaleDenom -- the model is in meters throughout this app) or auto-fit with
  // an 8% margin, recentring the target on the model's extent for that view direction.
  /* __acad3dV116: pan is where the viewport looks, in metres along the view's right and up from the
     source's own target -- the same frame 'fit' recentres in below. Only a fixed-scale viewport has
     one; a fitted viewport recentres on the model every time it is drawn. */
  function bimSheetSolveCamera(src,pxW,pxH,pxPerMM,scaleMode,scaleDenom,pan){
    var base=src.cam;
    if(scaleMode==='ratio'){
      var mmPerModelUnit=1000/Math.max(1,scaleDenom||100);
      var pxPerModelUnit=mmPerModelUnit*pxPerMM;
      var dist=1.2*pxH/Math.max(pxPerModelUnit,1e-6);
      var tx=base.tx,ty=base.ty,tz=base.tz;
      if(pan&&isFinite(pan[0])&&isFinite(pan[1])&&(pan[0]||pan[1])){
        var Vp=camVecs({yaw:base.yaw,pitch:base.pitch,dist:1,tx:base.tx,ty:base.ty,tz:base.tz});
        tx+=Vp.r[0]*pan[0]+Vp.u[0]*pan[1];ty+=Vp.r[1]*pan[0]+Vp.u[1]*pan[1];tz+=Vp.r[2]*pan[0]+Vp.u[2]*pan[1];
      }
      return {yaw:base.yaw,pitch:base.pitch,dist:dist,tx:tx,ty:ty,tz:tz};
    }
    var ext=bimFlatExtent(base,src.levelFilter,src.levelId);
    if(!ext){
      var kDef=(1000/100)*pxPerMM;
      return {yaw:base.yaw,pitch:base.pitch,dist:1.2*pxH/kDef,tx:base.tx,ty:base.ty,tz:base.tz};
    }
    var cx=(ext.xmin+ext.xmax)/2,cy=(ext.ymin+ext.ymax)/2;
    var hx=Math.max((ext.xmax-ext.xmin)/2,1e-6),hy=Math.max((ext.ymax-ext.ymin)/2,1e-6);
    var margin=0.92;
    var k=Math.min((pxW*margin/2)/hx,(pxH*margin/2)/hy);
    if(!isFinite(k)||k<=0)k=(1000/100)*pxPerMM;
    var dist=1.2*pxH/k;
    var V=ext.V;
    return {
      yaw:base.yaw,pitch:base.pitch,dist:dist,
      tx:base.tx+V.r[0]*cx+V.u[0]*cy,
      ty:base.ty+V.r[1]*cx+V.u[1]*cy,
      tz:base.tz+V.r[2]*cx+V.u[2]*cy
    };
  }
  function bimGetScratchCanvas(w,h){
    if(!A3D_SHEET_SCRATCH)A3D_SHEET_SCRATCH=document.createElement('canvas');
    if(A3D_SHEET_SCRATCH.width!==w)A3D_SHEET_SCRATCH.width=w;
    if(A3D_SHEET_SCRATCH.height!==h)A3D_SHEET_SCRATCH.height=h;
    return A3D_SHEET_SCRATCH;
  }
  // Renders one resolved viewport source into an offscreen canvas by temporarily redirecting the
  // live paint() pipeline at it (swapping el.cv/el.ctx and the relevant A3D fields, all restored
  // in a finally block so a mid-render exception can never leave the app's real on-screen state
  // corrupted -- the live canvas is never touched by this function at all).
  function bimRenderSourceToCanvas(src,pxW,pxH,pxPerMM,scaleMode,scaleDenom,pan,scale){
    pxW=Math.max(1,Math.round(pxW));pxH=Math.max(1,Math.round(pxH));
    var cam=bimSheetSolveCamera(src,pxW,pxH,pxPerMM,scaleMode,scaleDenom,pan);   /* __acad3dV116 */
    /* __acad3dV122: drawn at the page's scale -- paint() lays out at cv.width / cvScale(cv), as it
       does on a high-density screen, so the view is the one the layout shows, at more pixels */
    var bs=(isFinite(scale)&&scale>0)?scale:1;
    var scratch=bimGetScratchCanvas(Math.max(1,Math.round(pxW*bs)),Math.max(1,Math.round(pxH*bs)));
    scratch.__a3dScale=bs;
    var sctx=scratch.getContext('2d');
    var savedCv=el.cv,savedCtx=el.ctx;
    var savedCam={yaw:A3D.cam.yaw,pitch:A3D.cam.pitch,dist:A3D.cam.dist,tx:A3D.cam.tx,ty:A3D.cam.ty,tz:A3D.cam.tz};
    var savedFlat=A3D.flat,savedActiveLevel=A3D.activeLevel,savedLevelFilter=A3D.levelFilter,
        savedActiveViewId=A3D.activeViewId,savedSection=A3D.section,savedSel=A3D.sel,savedSel2=A3D.sel2,
        savedView=A3D.view,savedSelSet=A3D.selSet,savedSelGrid=A3D.selGrid;   /* __acad3dV122 */
    try{
      el.cv=scratch;el.ctx=sctx;
      A3D.cam={yaw:cam.yaw,pitch:cam.pitch,dist:cam.dist,tx:cam.tx,ty:cam.ty,tz:cam.tz};
      A3D.flat=true;
      if(src.levelId)A3D.activeLevel=src.levelId;
      A3D.levelFilter=!!src.levelFilter;
      A3D.activeViewId=null;A3D.sel=null;A3D.sel2=null;A3D.view=src.label||'';
      /* __acad3dV122: the whole selection. sel and sel2 were cleared and the rest drew: a room, its
         tag, a dimension, a text, a note, a hatch, terrain and a property line selected in the model
         read A3D.selSet, a grid A3D.selGrid, and came out blue on the sheet and its plots. */
      A3D.selSet=[];A3D.selGrid=null;
      if(src.section){
        A3D.section={p:src.section.p,dir:src.section.dir,keepSign:src.section.keepSign,
          cutMeshes:bimComputeSectionCuts(src.section.p,src.section.dir,src.section.keepSign)};
      }else{
        A3D.section=null;
      }
      A3D.sheetCapture=true;
      A3D_PLOT.pxmm=pxPerMM;   /* __acad3dV121: linetypes and lineweights at the paper's millimetres */
      paint();
    }catch(eR){
      console.warn('[BIM] Sheet viewport render failed: ',eR);
    }finally{
      A3D.sheetCapture=false;
      A3D_PLOT.pxmm=0;
      el.cv=savedCv;el.ctx=savedCtx;
      A3D.cam=savedCam;A3D.flat=savedFlat;A3D.activeLevel=savedActiveLevel;A3D.levelFilter=savedLevelFilter;
      A3D.activeViewId=savedActiveViewId;A3D.section=savedSection;A3D.sel=savedSel;A3D.sel2=savedSel2;A3D.view=savedView;
      A3D.selSet=savedSelSet;A3D.selGrid=savedSelGrid;   /* __acad3dV122 */
      /* the scratch is shared: the next user draws on it unscaled (bimBuildScheduleImageEmbed) */
      scratch.__a3dScale=1;sctx.setTransform(1,0,0,1,0,0);
    }
    return scratch;
  }
  function bimDrawScheduleViewport(ctx,vp,x,y,w,h){
    var def=SCHEDULE_DEFS[vp.refId];
    ctx.fillStyle='#ffffff';ctx.fillRect(x,y,w,h);
    if(!def)return;
    var rows=[];
    try{rows=def.build();}catch(eB){rows=[];}
    var pad=4,rowH=16,colW=w/Math.max(1,def.cols.length),i,j;
    ctx.font='bold 10px system-ui,sans-serif';ctx.fillStyle='#222';ctx.textAlign='left';ctx.textBaseline='middle';
    var cy=y+pad+rowH/2;
    for(i=0;i<def.cols.length;i++)ctx.fillText(String(def.cols[i].label),x+i*colW+pad,cy);
    ctx.strokeStyle='#999';ctx.lineWidth=0.5;
    ctx.beginPath();ctx.moveTo(x,y+pad+rowH);ctx.lineTo(x+w,y+pad+rowH);ctx.stroke();
    ctx.font='9.5px system-ui,sans-serif';
    var maxRows=Math.max(0,Math.floor((h-pad-rowH)/rowH)-1);
    for(i=0;i<Math.min(rows.length,maxRows);i++){
      var ry=y+pad+rowH*(i+2)-rowH/2;
      for(j=0;j<def.cols.length;j++){
        var col=def.cols[j],val=rows[i][col.key];
        /* __acad3dV122: fmt is the number of decimals (V19), never a function -- calling it threw on
           the first number, and every schedule on a sheet was a grey box. The table's own formatter. */
        var txt=bimFmtScheduleValue(val,col.fmt);
        ctx.fillText(txt,x+j*colW+pad,ry);
      }
    }
    if(rows.length>maxRows){
      ctx.fillStyle='#888';ctx.font='italic 9px system-ui,sans-serif';
      ctx.fillText('+'+(rows.length-maxRows)+' more row(s) not shown at this viewport size',x+pad,y+h-8);
    }
  }
  function bimCompositeViewport(ctx,vp,pageOriginPxX,pageOriginPxY,pxPerMM,scale){
    var destX=pageOriginPxX+vp.x*pxPerMM, destY=pageOriginPxY+vp.y*pxPerMM;
    var destW=vp.w*pxPerMM, destH=vp.h*pxPerMM;
    ctx.save();
    ctx.beginPath();ctx.rect(destX,destY,destW,destH);ctx.clip();
    var errMsg=null;
    if(vp.kind==='schedule'){
      bimDrawScheduleViewport(ctx,vp,destX,destY,destW,destH);
    }else{
      var src=bimResolveViewportSource(vp);
      if(src.error){
        errMsg=src.error;
        ctx.fillStyle='#f4f4f4';ctx.fillRect(destX,destY,destW,destH);
      }else{
        try{
          var img=bimRenderSourceToCanvas(src,destW,destH,pxPerMM,vp.scaleMode,vp.scaleDenom,vp.pan,scale);   /* __acad3dV122 */
          ctx.drawImage(img,destX,destY,destW,destH);
        }catch(eV){
          errMsg='Render failed';
          console.warn('[BIM] Sheet viewport render crashed: ',eV);
          ctx.fillStyle='#f4f4f4';ctx.fillRect(destX,destY,destW,destH);
        }
      }
    }
    ctx.restore();
    if(errMsg){
      ctx.save();
      ctx.strokeStyle='#c33';ctx.lineWidth=1;ctx.strokeRect(destX+0.5,destY+0.5,destW-1,destH-1);
      ctx.fillStyle='#c33';ctx.font='11px system-ui,sans-serif';ctx.textAlign='center';ctx.textBaseline='middle';
      ctx.fillText(errMsg,destX+destW/2,destY+destH/2);
      ctx.restore();
      console.warn('[BIM] Sheet viewport '+vp.id+' could not be resolved: '+errMsg);
    }
    ctx.strokeStyle='#888';ctx.lineWidth=0.75;ctx.strokeRect(destX+0.5,destY+0.5,destW-1,destH-1);
    var scaleTxt=vp.kind==='schedule'?'':(vp.scaleMode==='ratio'?(' — 1 : '+vp.scaleDenom):' — Fit');
    var lbl=(vp.label||'')+scaleTxt;
    ctx.fillStyle='#222';ctx.font='bold '+Math.max(9,3.2*pxPerMM)+'px system-ui,sans-serif';
    ctx.textAlign='left';ctx.textBaseline='bottom';
    ctx.fillText(lbl,destX+2,destY+destH+11);
  }
  function bimDrawTitleBlock(ctx,sheet,pageOriginPxX,pageOriginPxY,pageWmm,pageHmm,pxPerMM){
    var tbWmm=Math.min(90,pageWmm*0.42), tbHmm=Math.min(28,pageHmm*0.22);
    var x=pageOriginPxX+(pageWmm-tbWmm)*pxPerMM, y=pageOriginPxY+(pageHmm-tbHmm)*pxPerMM;
    var w=tbWmm*pxPerMM,h=tbHmm*pxPerMM;
    ctx.save();
    ctx.fillStyle='#ffffff';ctx.fillRect(x,y,w,h);
    ctx.strokeStyle='#222';ctx.lineWidth=1.2;ctx.strokeRect(x+0.5,y+0.5,w-1,h-1);
    var tb=A3D.titleBlock||{};
    var rowH=h/4,ri;
    ctx.strokeStyle='#999';ctx.lineWidth=0.5;
    for(ri=1;ri<4;ri++){ctx.beginPath();ctx.moveTo(x,y+rowH*ri);ctx.lineTo(x+w,y+rowH*ri);ctx.stroke();}
    ctx.beginPath();ctx.moveTo(x+w*0.62,y+rowH*2);ctx.lineTo(x+w*0.62,y+h);ctx.stroke();
    ctx.fillStyle='#222';ctx.textBaseline='middle';
    ctx.font='bold 9px system-ui,sans-serif';ctx.textAlign='left';
    ctx.fillText(bimProjectLabel(),x+4,y+rowH*0.5);   /* __acad3dV115: the one derivation of the name */
    ctx.font='8px system-ui,sans-serif';
    ctx.fillText('Drawn by: '+(tb.drawnBy||'-')+'   Checked by: '+(tb.checkedBy||'-'),x+4,y+rowH*1.5);
    ctx.fillText((tb.client||''),x+4,y+rowH*2.5);
    ctx.fillText(new Date().toLocaleDateString(),x+w*0.62+4,y+rowH*2.5);
    ctx.font='9px system-ui,sans-serif';ctx.fillText('Sheet Name',x+4,y+rowH*3.5-6);
    ctx.font='11px system-ui,sans-serif';ctx.fillText(sheet.name||'Untitled',x+4,y+rowH*3.5+4);
    ctx.font='bold 16px system-ui,sans-serif';ctx.textAlign='right';
    ctx.fillText(sheet.number||'',x+w-4,y+rowH*3);
    ctx.restore();
  }
  /* __acad3dV116: paperOnly draws the sheet as it prints -- no selection outline, no model-space
     highlight. The exports asked for that by clearing and restoring the selection around the call;
     a flag cannot be left set by a render that throws. */
  function bimRenderSheet(sheet,pxPerMM,paperOnly,cv,scale){
    /* __acad3dV121: paper alone is an export or a print, and so a plot; on screen a sheet shows
       what AutoCAD's layout shows -- a no-plot layer drawn, a locked one faded */
    if(paperOnly)return bimWithPlotPass(A3D.presentMode,function(){return bimRenderSheetPaper(sheet,pxPerMM,true,cv,scale);});
    return bimRenderSheetPaper(sheet,pxPerMM,false,cv,scale);
  }
  /* __acad3dV122: `cv` is the canvas drawn on -- the sheet view's own when it is left out -- and
     `scale` its pixels to one of the layout's. The page is laid out at pxPerMM, as every size in it
     was made for (the title block's text, a viewport's label, a schedule's rows, the text in a
     viewport), and drawn at pxPerMM x scale, so it is the same page at any resolution: a thumbnail,
     a page fitted to the window, a projector. */
  function bimRenderSheetPaper(sheet,pxPerMM,paperOnly,cvIn,scale){
    var s=(isFinite(scale)&&scale>0)?scale:1;
    var pxW=Math.round(sheet.w*pxPerMM),pxH=Math.round(sheet.h*pxPerMM);
    var cv=cvIn||el.sheetcv;
    if(!cv)return null;
    var dW=Math.max(1,Math.round(sheet.w*pxPerMM*s)),dH=Math.max(1,Math.round(sheet.h*pxPerMM*s));
    if(cv.width!==dW)cv.width=dW;
    if(cv.height!==dH)cv.height=dH;
    var ctx=cv.getContext('2d');
    ctx.setTransform(s,0,0,s,0,0);
    ctx.fillStyle='#ffffff';ctx.fillRect(0,0,pxW,pxH);
    ctx.strokeStyle='#333';ctx.lineWidth=1.5;ctx.strokeRect(0.75,0.75,pxW-1.5,pxH-1.5);
    var i;
    for(i=0;i<sheet.viewports.length;i++){
      try{bimCompositeViewport(ctx,sheet.viewports[i],0,0,pxPerMM,s);}   /* __acad3dV122 */
      catch(eC){console.warn('[BIM] Viewport composite failed: ',eC);}
    }
    bimDrawTitleBlock(ctx,sheet,0,0,sheet.w,sheet.h,pxPerMM);
    if(!paperOnly&&A3D.sheetActiveVp){   /* __acad3dV116: model space -- the rest of the sheet recedes */
      var av=bimSheetVp(sheet,A3D.sheetActiveVp);
      if(av){
        var ax=av.x*pxPerMM,ay=av.y*pxPerMM,aw=av.w*pxPerMM,ah=av.h*pxPerMM;
        ctx.save();
        ctx.fillStyle='rgba(22,26,32,0.34)';
        ctx.fillRect(0,0,pxW,ay);ctx.fillRect(0,ay+ah,pxW,pxH-ay-ah);
        ctx.fillRect(0,ay,ax,ah);ctx.fillRect(ax+aw,ay,pxW-ax-aw,ah);
        ctx.strokeStyle='#2f7fe0';ctx.lineWidth=3;ctx.strokeRect(ax+1.5,ay+1.5,aw-3,ah-3);
        ctx.restore();
      }
    }
    if(!paperOnly&&A3D.sheetSelVp){
      var sv=null;for(i=0;i<sheet.viewports.length;i++)if(sheet.viewports[i].id===A3D.sheetSelVp){sv=sheet.viewports[i];break;}
      if(sv){
        ctx.save();
        ctx.strokeStyle='#4ea1ff';ctx.lineWidth=2;
        ctx.strokeRect(sv.x*pxPerMM,sv.y*pxPerMM,sv.w*pxPerMM,sv.h*pxPerMM);
        var hs=8;
        ctx.fillStyle='#4ea1ff';
        ctx.fillRect((sv.x+sv.w)*pxPerMM-hs/2,(sv.y+sv.h)*pxPerMM-hs/2,hs,hs);
        ctx.restore();
      }
    }
    return cv;
  }
  function bimSheetViewRefresh(){
    if(!el.sheetview)return;
    var sheet=bimSheetById(A3D.activeSheetId);
    if(!sheet){
      /* __acad3dV116: the sheet on screen is gone -- an undo of its creation, say. Its paper went
         away before and the view state kept saying Sheet; the model it came from comes back. */
      if(bimSheetOnScreen()||A3D_VIEW.kind==='sheet')bimShowModel();
      else el.sheetview.classList.remove('open');
      return;
    }
    if(el.sheetnum)el.sheetnum.textContent=bimSheetLabel(sheet);   /* __acad3dV116 */
    bimRenderLayoutTabs();
    if(A3D_PAGES.display==='pages'){bimPagesRefresh();return;}   /* __acad3dV122 */
    bimRenderSheet(sheet,SHEET_PREVIEW_PXMM);
  }
