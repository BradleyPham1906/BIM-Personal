  // ---- __acad3dV13: Annotation (linear dimensions, text labels) + PNG/PDF export ----
  // ---- __acad3dV25: angular / radius / diameter dimensions + leaders. All stored as t:'dim'
  // with a dimKind discriminator, so they inherit the existing dim plumbing (view-scoping,
  // level filtering, duplication, layer/lock handling) for free. dimKind is absent on
  // pre-existing linear dims, which is why every read defaults to 'linear'. ----
  function bimDimKind(o){return (o&&o.dimKind)||'linear';}
  function bimComputeAngularDim(vertex,p1,p2){
    var a1=Math.atan2(p1[1]-vertex[1],p1[0]-vertex[0]);
    var a2=Math.atan2(p2[1]-vertex[1],p2[0]-vertex[0]);
    var r1=Math.sqrt(Math.pow(p1[0]-vertex[0],2)+Math.pow(p1[1]-vertex[1],2));
    var r2=Math.sqrt(Math.pow(p2[0]-vertex[0],2)+Math.pow(p2[1]-vertex[1],2));
    if(r1<1e-9||r2<1e-9)return null;
    var sweep=a2-a1;
    while(sweep<=-Math.PI)sweep+=Math.PI*2;
    while(sweep>Math.PI)sweep-=Math.PI*2;
    return {vertex:vertex,a1:a1,a2:a2,sweep:sweep,radius:Math.min(r1,r2)*0.6,degrees:Math.abs(sweep)*180/Math.PI};
  }
  function bimCircleFrom3Points(p1,p2,p3){
    var ax=p1[0],ay=p1[1],bx=p2[0],by=p2[1],cx=p3[0],cy=p3[1];
    var d=2*(ax*(by-cy)+bx*(cy-ay)+cx*(ay-by));
    if(Math.abs(d)<1e-9)return null;
    var ux=((ax*ax+ay*ay)*(by-cy)+(bx*bx+by*by)*(cy-ay)+(cx*cx+cy*cy)*(ay-by))/d;
    var uy=((ax*ax+ay*ay)*(cx-bx)+(bx*bx+by*by)*(ax-cx)+(cx*cx+cy*cy)*(bx-ax))/d;
    return {center:[ux,uy],radius:Math.sqrt(Math.pow(ax-ux,2)+Math.pow(ay-uy,2))};
  }
  function bimComputeRadialDim(center,radius,anglePt,isDiameter){
    var ang=Math.atan2(anglePt[1]-center[1],anglePt[0]-center[0]);
    var edge=[center[0]+Math.cos(ang)*radius,center[1]+Math.sin(ang)*radius];
    var start=isDiameter?[center[0]-Math.cos(ang)*radius,center[1]-Math.sin(ang)*radius]:center;
    return {center:center,radius:radius,start:start,edge:edge,value:isDiameter?radius*2:radius,isDiameter:!!isDiameter};
  }
  function bimComputeLeader(anchorPt,elbowPt,textPt){
    var dir=textPt[0]>=elbowPt[0]?1:-1;
    return {anchor:anchorPt,elbow:elbowPt,landing:[elbowPt[0]+dir*0.5,elbowPt[1]],textPt:textPt,dir:dir};
  }
  function bimNewDimBase(){
    A3D.counts.dim=(A3D.counts.dim||0)+1;
    var lvl=bimGetActiveLevel();
    return {id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'dim',col:'#dfe4ea',pos:[0,0,0],
      y:lvl.elev,levelId:A3D.activeLevel,layer:A3D.activeLayer,viewId:A3D.activeViewId};
  }
  function bimCreateAngularDim(vertex,p1,p2){
    var r=bimComputeAngularDim(vertex,p1,p2);
    if(!r){a3dToast('Angle rays cannot be zero-length');return null;}
    pushUndo();
    var o=bimNewDimBase();
    o.dimKind='angular';o.name='Angle_'+A3D.counts.dim;
    o.vertex=vertex;o.ap1=p1;o.ap2=p2;o.a1=r.a1;o.sweep=r.sweep;o.arcRadius=r.radius;o.degrees=r.degrees;
    A3D.objs.push(o);
    A3D.sel=o.id;A3D.sel2=null;A3D.selSet=[o.id];
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast(o.name+' \u2014 '+r.degrees.toFixed(1)+'\u00b0');
    return o;
  }
  function bimCreateRadialDim(p1,p2,p3,isDiameter){
    var circ=bimCircleFrom3Points(p1,p2,p3);
    if(!circ){a3dToast('Those three points are collinear \u2014 no circle through them');return null;}
    var r=bimComputeRadialDim(circ.center,circ.radius,p3,isDiameter);
    pushUndo();
    var o=bimNewDimBase();
    o.dimKind=isDiameter?'diameter':'radius';
    o.name=(isDiameter?'Dia_':'Rad_')+A3D.counts.dim;
    o.center=circ.center;o.radius=circ.radius;o.dStart=r.start;o.dEdge=r.edge;o.value=r.value;
    A3D.objs.push(o);
    A3D.sel=o.id;A3D.sel2=null;A3D.selSet=[o.id];
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast(o.name+' \u2014 '+r.value.toFixed(2)+' m');
    return o;
  }
  function bimCreateLeader(anchorPt,elbowPt,textPt,label){
    var r=bimComputeLeader(anchorPt,elbowPt,textPt);
    pushUndo();
    var o=bimNewDimBase();
    o.dimKind='leader';o.name='Leader_'+A3D.counts.dim;
    o.anchor=r.anchor;o.elbow=r.elbow;o.landing=r.landing;o.label=label;o.ldir=r.dir;
    A3D.objs.push(o);
    A3D.sel=o.id;A3D.sel2=null;A3D.selSet=[o.id];
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast(o.name+' created');
    return o;
  }
  function startAngularDimTool(){
    bimEnterDraftingMode();
    var lvl=bimGetActiveLevel();
    A3D.sk={tool:'dimangular',pts:[],y:lvl.elev,on:null};
    a3dToast('Angular: click the corner vertex, then a point on each ray');
    paint();
  }
  function startRadialDimTool(isDiameter){
    bimEnterDraftingMode();
    var lvl=bimGetActiveLevel();
    A3D.sk={tool:isDiameter?'dimdiameter':'dimradius',pts:[],y:lvl.elev,on:null};
    a3dToast((isDiameter?'Diameter':'Radius')+': click three points on the arc/circle');
    paint();
  }
  function startLeaderTool(){
    bimEnterDraftingMode();
    var lvl=bimGetActiveLevel();
    A3D.sk={tool:'leader',pts:[],y:lvl.elev,on:null};
    a3dToast('Leader: click the arrow tip, then the elbow, then where the text goes');
    paint();
  }
  function openLeaderTextDlg(anchorPt,elbowPt,textPt){
    closeDlg();
    var d=document.createElement('div');
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">Leader text</div><div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Text</label><input type="text" data-a3dp="t" value="" maxlength="120"></div>'+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">OK</button></div>';
    el.root.appendChild(d);el.dlg=d;
    var tI=d.querySelector('[data-a3dp="t"]');
    function submit(){
      var v=tI.value.trim();
      var eb=document.getElementById('a3d-dlgerr');
      if(!v){eb.textContent='Enter some text';return;}
      closeDlg();
      bimCreateLeader(anchorPt,elbowPt,textPt,v);
    }
    d.addEventListener('click',function(ev){var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;if(!b)return;if(b.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();});
    d.addEventListener('keydown',function(ev){if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}ev.stopPropagation();});
    tI.focus();
  }
  function drawDimExtras(ctx,V,W,H,o,sel){
    var ox=(o.pos&&o.pos[0])||0,oy=(o.pos&&o.pos[1])||0,oz=(o.pos&&o.pos[2])||0;
    var y0=o.y+oy;
    function S(p){return toScreen([p[0]+ox,y0,p[1]+oz],V,W,H);}
    ctx.save();
    ctx.globalAlpha*=bimLayerAlpha(o);   /* __acad3dV121: the layer's transparency */
    ctx.strokeStyle=sel?'#4ea1ff':'#b8c0ca';
    ctx.fillStyle=sel?'#9ec1ff':'#dfe4ea';
    ctx.lineWidth=sel?1.4:1;
    ctx.font='11px system-ui,sans-serif';
    ctx.textAlign='center';ctx.textBaseline='middle';
    var kind=bimDimKind(o),label='',lp=null,i;
    if(kind==='angular'){
      var vtx=S(o.vertex);
      ctx.beginPath();ctx.moveTo(vtx[0],vtx[1]);var e1=S(o.ap1);ctx.lineTo(e1[0],e1[1]);ctx.stroke();
      ctx.beginPath();ctx.moveTo(vtx[0],vtx[1]);var e2=S(o.ap2);ctx.lineTo(e2[0],e2[1]);ctx.stroke();
      var steps=24;
      ctx.beginPath();
      for(i=0;i<=steps;i++){
        var a=o.a1+o.sweep*(i/steps);
        var wp=[o.vertex[0]+Math.cos(a)*o.arcRadius,o.vertex[1]+Math.sin(a)*o.arcRadius];
        var sp=S(wp);
        if(i===0)ctx.moveTo(sp[0],sp[1]);else ctx.lineTo(sp[0],sp[1]);
      }
      ctx.stroke();
      var midA=o.a1+o.sweep/2;
      lp=S([o.vertex[0]+Math.cos(midA)*o.arcRadius*1.25,o.vertex[1]+Math.sin(midA)*o.arcRadius*1.25]);
      label=o.degrees.toFixed(1)+'\u00b0';
    }else if(kind==='radius'||kind==='diameter'){
      var cs=S(o.center),st=S(o.dStart),ed=S(o.dEdge);
      ctx.beginPath();
      for(i=0;i<=48;i++){
        var ca=(i/48)*Math.PI*2;
        var cp=S([o.center[0]+Math.cos(ca)*o.radius,o.center[1]+Math.sin(ca)*o.radius]);
        if(i===0)ctx.moveTo(cp[0],cp[1]);else ctx.lineTo(cp[0],cp[1]);
      }
      ctx.setLineDash([3,3]);ctx.stroke();ctx.setLineDash([]);
      ctx.beginPath();ctx.moveTo(st[0],st[1]);ctx.lineTo(ed[0],ed[1]);ctx.stroke();
      lp=[(st[0]+ed[0])/2,(st[1]+ed[1])/2-10];
      label=(kind==='diameter'?'\u00d8':'R')+o.value.toFixed(2);
    }else if(kind==='leader'){
      var an=S(o.anchor),el2=S(o.elbow),la=S(o.landing);
      ctx.beginPath();ctx.moveTo(an[0],an[1]);ctx.lineTo(el2[0],el2[1]);ctx.lineTo(la[0],la[1]);ctx.stroke();
      var adx=el2[0]-an[0],ady=el2[1]-an[1],alen=Math.sqrt(adx*adx+ady*ady)||1;
      var ux=adx/alen,uy=ady/alen,ah=7;
      ctx.beginPath();
      ctx.moveTo(an[0],an[1]);
      ctx.lineTo(an[0]+ux*ah-uy*ah*0.4,an[1]+uy*ah+ux*ah*0.4);
      ctx.lineTo(an[0]+ux*ah+uy*ah*0.4,an[1]+uy*ah-ux*ah*0.4);
      ctx.closePath();ctx.fill();
      ctx.textAlign=o.ldir<0?'right':'left';
      lp=[la[0]+(o.ldir<0?-4:4),la[1]-6];
      label=o.label||'';
    }
    if(label&&lp){
      var tw=ctx.measureText(label).width;
      var bx=ctx.textAlign==='center'?lp[0]-tw/2:(ctx.textAlign==='right'?lp[0]-tw:lp[0]);
      ctx.save();
      ctx.fillStyle='rgba(20,22,26,0.82)';
      ctx.fillRect(bx-4,lp[1]-8,tw+8,15);
      ctx.restore();
      ctx.fillStyle=sel?'#9ec1ff':'#dfe4ea';
      ctx.fillText(label,lp[0],lp[1]);
    }
    ctx.restore();
  }
  function bimComputeDim(p1,p2,p3){
    var dx=p2[0]-p1[0],dz=p2[1]-p1[1];
    var len=Math.sqrt(dx*dx+dz*dz);
    if(len<1e-9)return null;
    var ux=dx/len,uz=dz/len;
    var perpX=-uz,perpZ=ux;
    var offSigned=(p3[0]-p1[0])*perpX+(p3[1]-p1[1])*perpZ;
    var d1=[p1[0]+perpX*offSigned,p1[1]+perpZ*offSigned];
    var d2=[p2[0]+perpX*offSigned,p2[1]+perpZ*offSigned];
    return {d1:d1,d2:d2,length:len,offset:offSigned};
  }
  function startDimTool(){
    closeDlg();
    bimEnterDraftingMode();
    var lvl=bimGetActiveLevel();
    A3D.sk={tool:'dim',pts:[],y:lvl.elev,on:null};
    a3dToast('Dimension: click first point, second point, then a third point to set the offset side');
    paint();
  }
  function bimCreateDim(p1,p2,p3){
    var r=bimComputeDim(p1,p2,p3);
    if(!r){a3dToast('Dimension points cannot coincide');return null;}
    pushUndo();
    A3D.counts.dim=(A3D.counts.dim||0)+1;
    var lvl=bimGetActiveLevel();
    var o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'dim',name:'Dim_'+A3D.counts.dim,col:'#dfe4ea',pos:[0,0,0],
      p1:p1,p2:p2,d1:r.d1,d2:r.d2,length:r.length,y:lvl.elev,levelId:A3D.activeLevel,layer:A3D.activeLayer,viewId:A3D.activeViewId};
    A3D.objs.push(o);
    A3D.sel=o.id;A3D.sel2=null;A3D.selSet=[o.id];
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast(o.name+' created \u2014 '+r.length.toFixed(2)+' m');
    return o;
  }
  function startTextTool(){
    closeDlg();
    bimEnterDraftingMode();
    var lvl=bimGetActiveLevel();
    A3D.sk={tool:'text',pts:[],y:lvl.elev,on:null};
    a3dToast('Text: click where the label should go');
    paint();
  }
  function openTextLabelDlg(pt,y){
    closeDlg();
    var d=document.createElement('div');
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">Text label</div>'+
      '<div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Text</label><input type="text" data-a3dp="txt" value="" maxlength="120"></div>'+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">OK</button></div>';
    el.root.appendChild(d);
    el.dlg=d;
    var tI=d.querySelector('[data-a3dp="txt"]');
    function submit(){
      var txt=tI.value;
      var eb=document.getElementById('a3d-dlgerr');
      if(!txt||!txt.trim()){eb.textContent='Enter some text';return;}
      closeDlg();
      bimCreateTextLabel(pt,y,txt.trim());
    }
    d.addEventListener('click',function(ev){
      var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;
      if(!b)return;
      if(b.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();
    });
    d.addEventListener('keydown',function(ev){
      if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}
      else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}
      ev.stopPropagation();
    });
    tI.focus();
  }
  function bimCreateTextLabel(pt,y,text){
    pushUndo();
    A3D.counts.text=(A3D.counts.text||0)+1;
    var o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'text',name:'Text_'+A3D.counts.text,col:'#dfe4ea',pos:[0,0,0],
      text:text,pt:pt,y:y,levelId:A3D.activeLevel,layer:A3D.activeLayer,viewId:A3D.activeViewId};
    A3D.objs.push(o);
    A3D.sel=o.id;A3D.sel2=null;A3D.selSet=[o.id];
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast(o.name+' created');
    return o;
  }
  function drawDims(ctx,V,W,H){
    if(A3D.section)return;
    var i,o;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(o.t!=='dim')continue;
      if(!bimLayerShown(o))continue;   /* __acad3dV121 */
      if(!bimAnnotationVisible(o))continue;
      if(!bimObjectVisibleOnLevel(o))continue;
      var selX=(o.id===A3D.sel||(A3D.selSet&&A3D.selSet.indexOf(o.id)>=0));
      if(bimDimKind(o)!=='linear'){drawDimExtras(ctx,V,W,H,o,selX);continue;}
      var ox=(o.pos&&o.pos[0])||0,oy=(o.pos&&o.pos[1])||0,oz=(o.pos&&o.pos[2])||0;
      var y0=o.y+oy;
      var p1=toScreen([o.p1[0]+ox,y0,o.p1[1]+oz],V,W,H);
      var p2=toScreen([o.p2[0]+ox,y0,o.p2[1]+oz],V,W,H);
      var d1=toScreen([o.d1[0]+ox,y0,o.d1[1]+oz],V,W,H);
      var d2=toScreen([o.d2[0]+ox,y0,o.d2[1]+oz],V,W,H);
      var sel=(o.id===A3D.sel||(A3D.selSet&&A3D.selSet.indexOf(o.id)>=0));
      ctx.save();
      ctx.globalAlpha*=bimLayerAlpha(o);   /* __acad3dV121: the layer's transparency */
      ctx.strokeStyle=sel?'#4ea1ff':'#b8c0ca';
      ctx.lineWidth=sel?1.4:1;
      ctx.beginPath();ctx.moveTo(p1[0],p1[1]);ctx.lineTo(d1[0],d1[1]);ctx.stroke();
      ctx.beginPath();ctx.moveTo(p2[0],p2[1]);ctx.lineTo(d2[0],d2[1]);ctx.stroke();
      ctx.beginPath();ctx.moveTo(d1[0],d1[1]);ctx.lineTo(d2[0],d2[1]);ctx.stroke();
      var tdx=d2[0]-d1[0],tdy=d2[1]-d1[1],tlen=Math.sqrt(tdx*tdx+tdy*tdy)||1;
      var tux=tdx/tlen,tuy=tdy/tlen,tick=4;
      ctx.beginPath();ctx.moveTo(d1[0]-tuy*tick-tux*tick,d1[1]+tux*tick-tuy*tick);ctx.lineTo(d1[0]+tuy*tick+tux*tick,d1[1]-tux*tick+tuy*tick);ctx.stroke();
      ctx.beginPath();ctx.moveTo(d2[0]-tuy*tick-tux*tick,d2[1]+tux*tick-tuy*tick);ctx.lineTo(d2[0]+tuy*tick+tux*tick,d2[1]-tux*tick+tuy*tick);ctx.stroke();
      var mx=(d1[0]+d2[0])/2,my=(d1[1]+d2[1])/2;
      var label=o.length.toFixed(2)+' m';
      ctx.font='11px system-ui,sans-serif';
      var tw=ctx.measureText(label).width;
      ctx.fillStyle='rgba(20,22,26,0.82)';
      ctx.fillRect(mx-tw/2-4,my-16,tw+8,14);
      ctx.fillStyle=sel?'#9ec1ff':'#dfe4ea';
      ctx.textAlign='center';ctx.textBaseline='middle';
      ctx.fillText(label,mx,my-9);
      ctx.restore();
    }
  }
  function drawTextLabels(ctx,V,W,H){
    if(A3D.section)return;
    var i,o;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(o.t!=='text')continue;
      if(!bimLayerShown(o))continue;   /* __acad3dV121 */
      if(!bimAnnotationVisible(o))continue;
      if(!bimObjectVisibleOnLevel(o))continue;
      var ox=(o.pos&&o.pos[0])||0,oy=(o.pos&&o.pos[1])||0,oz=(o.pos&&o.pos[2])||0;
      var y0=o.y+oy;
      var sp=toScreen([o.pt[0]+ox,y0,o.pt[1]+oz],V,W,H);
      var sel=(o.id===A3D.sel||(A3D.selSet&&A3D.selSet.indexOf(o.id)>=0));
      ctx.save();
      ctx.globalAlpha*=bimLayerAlpha(o);   /* __acad3dV121: the layer's transparency */
      ctx.fillStyle=sel?'#4ea1ff':'#dfe4ea';
      ctx.beginPath();ctx.arc(sp[0],sp[1],2.5,0,Math.PI*2);ctx.fill();
      ctx.font='12px system-ui,sans-serif';
      ctx.textAlign='left';ctx.textBaseline='middle';
      var tw2=ctx.measureText(o.text).width;
      ctx.fillStyle='rgba(20,22,26,0.72)';
      ctx.fillRect(sp[0]+6,sp[1]-9,tw2+8,18);
      ctx.fillStyle=sel?'#9ec1ff':'#dfe4ea';
      ctx.fillText(o.text,sp[0]+10,sp[1]);
      ctx.restore();
    }
  }
