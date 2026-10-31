  /* ================= __acad3dV148: results as layers =================
     A result kept as a layer. Sun hours and rain are kept as they were when run -- their picture is
     saved with the project, so it opens offline and two runs (June and December, say) can be laid
     over each other. A terrain's slope, elevation, aspect or cut and fill follows its surface, so
     it is never out of date. Each layer has its visibility, its opacity and its place in the
     stack; the top of the list is drawn last, over the rest, as in any layers panel. */
  var A3D_RES_IMG={};
  var BIM_TVIEW_LABEL={slope:'Slope',elevation:'Elevation',aspect:'Aspect',cutfill:'Cut and fill'};
  function bimResLayers(){if(!Array.isArray(A3D.resultLayers))A3D.resultLayers=[];return A3D.resultLayers;}
  function bimResById(id){var L=bimResLayers(),i;for(i=0;i<L.length;i++)if(L[i].id===id)return L[i];return null;}
  function bimResOpacity(R){var v=R&&R.opacity;return typeof v==='number'&&v>=0.1&&v<=1?v:0.6;}
  /* a run that a layer keeps: drawn as that layer, not twice */
  function bimResHolds(s){
    if(!s||!s.runId)return false;
    var L=bimResLayers(),i;
    for(i=0;i<L.length;i++)if(L[i].run===s.runId)return true;
    return false;
  }
  function bimResNow(){var d=new Date();function p(n){return (n<10?'0':'')+n;}return d.getFullYear()+'-'+p(d.getMonth()+1)+'-'+p(d.getDate())+' '+p(d.getHours())+':'+p(d.getMinutes());}
  /* what a kept result depends on: the model, and for the sun the site's place -- not the date,
     which the layer keeps as its own */
  function bimResKeyFrom(stamp,kind){
    stamp=String(stamp||'');
    var i=stamp.indexOf(':'),j=i<0?-1:stamp.indexOf(':',i+1),st;
    if(i<0)return stamp;
    if(kind!=='sunhours')return stamp.slice(0,i);
    try{st=JSON.parse(stamp.slice(j+1));}catch(eK){st={};}
    return stamp.slice(0,i)+':'+stamp.slice(i+1,j)+':'+[st.lat,st.lon,st.tz].join(',');
  }
  function bimResKey(kind){return bimResKeyFrom(bimSimStamp(),kind);}
  function bimResStale(R){if(R&&R.kind==='tool')return bimTlStale(R);   /* __acad3dV172: a tool's output, when the lot has changed */
    return !!(R&&R.kind!=='terrain'&&R.kind!=='walk'&&R.key&&R.key!==bimResKey(R.kind));}   /* __acad3dV161: walk times follow their data */
  /* a terrain layer whose surface is gone, or no longer proposed */
  function bimResGone(R){
    if(!R)return true;
    if(R.kind==='walk')return !bimAccHas();   /* __acad3dV161 */
    if(R.kind!=='terrain')return false;
    var o=objById(R.src);
    return !(o&&o.t==='terrain'&&o.survey)||(R.mode==='cutfill'&&!o.grading);
  }
  /* a run's picture as text: one character a cell, the colour's place on the ramp */
  function bimResSunData(s){
    var n=s.nx*s.nz,m=BIM_SIM_RAMP.length,a=[],k;
    for(k=0;k<n;k++)a.push(s.roof[k]?'.':String(Math.min(m-1,Math.floor(Math.max(0,Math.min(1,s.day?s.hours[k]/s.day:0))*m))));
    return {x0:s.x0,z0:s.z0,cell:s.cell,nx:s.nx,nz:s.nz,ground:s.ground,date:s.date,day:s.day,min:s.min,max:s.max,sixPlus:s.sixPlus,cells:a.join('')};
  }
  function bimResRainData(r){
    var n=r.nx*r.nz,a=[],k;
    function r3(v){return Math.round(v*1000)/1000;}
    for(k=0;k<n;k++)a.push(r.pid[k]?'1':'0');
    return {x0:r.x0,z0:r.z0,cell:r.cell,nx:r.nx,nz:r.nz,cells:a.join(''),maxAcc:r.maxAcc,ponds:r.ponds.length,pondVolume:r.pondVolume,
      deepest:r.ponds.length?r.ponds[0].depth:0,threshold:r.threshold,segs:r.segs.map(function(g){return [r3(g[0]),r3(g[1]),r3(g[2]),r3(g[3]),Math.round(g[4]*100)/100];})};
  }
  /* Add as layer: sunhours, rain, terrain (the surface shown by slope, elevation or aspect, or
     opts.id and opts.mode), cutfill (a proposed surface's cut and fill) */
  function bimResultLayerAdd(kind,opts){
    opts=opts||{};
    var R=null,s=null,o=null,mode;
    if(kind==='sunhours'||kind==='rain'){
      s=kind==='sunhours'?A3D_SIM.sun:A3D_SIM.rain;
      if(!s){a3dToast('Run '+(kind==='sunhours'?'Sun hours':'Rain on terrain')+' first, then add it as a layer');return null;}
      if(bimResHolds(s)){a3dToast('This run is a layer already');return null;}
      R=kind==='sunhours'?{kind:'sunhours',name:'Sun hours, '+s.date,data:bimResSunData(s),opacity:0.6}:
        {kind:'rain',name:'Rain on '+s.name,src:s.terrain,data:bimResRainData(s),opacity:0.9};
    }else if(kind==='terrain'||kind==='cutfill'){
      o=opts.id?objById(opts.id):(kind==='cutfill'?A3D.objs.filter(function(x){return x.t==='terrain'&&x.grading;})[0]:bimAnzTerrainShown())||null;
      mode=kind==='cutfill'?'cutfill':String(opts.mode||(o&&o.tview)||'');
      if(!o||o.t!=='terrain'||!o.survey){a3dToast(kind==='cutfill'?'There is no proposed surface: GRADE a pad first':'Show a surface by slope, elevation or aspect first');return null;}
      if(!BIM_TVIEW_LABEL.hasOwnProperty(mode)||(mode==='cutfill'&&!o.grading)){a3dToast('A terrain layer shows slope, elevation or aspect, or a proposed surface\'s cut and fill');return null;}
      R={kind:'terrain',mode:mode,name:BIM_TVIEW_LABEL[mode]+', '+o.name,src:o.id,opacity:0.55};
    }else if(kind==='walk'){   /* __acad3dV161 */
      if(!bimAccHas()){a3dToast('Get access and people first (Site analysis), then add the walk times as a layer');return null;}
      if(bimResLayers().some(function(x){return x.kind==='walk';})){a3dToast('The walk times are a layer already, in Layers under Analysis');return null;}
      R={kind:'walk',name:'Walk times',src:'access',opacity:0.9};
    }else return null;
    pushUndo();
    R.id='res-'+Date.now().toString(36)+'-'+(A3D.seq++);
    R.visible=true;R.created=bimResNow();
    if(s){if(!s.runId)s.runId='run-'+Date.now().toString(36)+'-'+(A3D.seq++);R.run=s.runId;R.key=bimResKeyFrom(s.stamp,R.kind);}   /* as it was when it ran, not when it was added */
    bimResLayers().unshift(R);   /* a new layer goes on top */
    if(o&&o.tview===mode)delete o.tview;   /* the surface's own colours step aside for the layer's */
    A3D_LY.rsel='res:'+R.id;
    if(A3D_LY.secShut)delete A3D_LY.secShut.analysis;
    refreshLayers();refreshProps();paint();saveSoon();bimAnalyzeRefresh();
    if(!opts.quiet)a3dToast(R.name+' is a layer now, in Layers under Analysis');
    return R;
  }
  /* Update: run it again, on the layer's own date and surface */
  function bimResultLayerUpdate(id){
    var R=bimResById(id),r;
    if(!R)return false;
    if(R.kind==='terrain'){a3dToast(R.name+' follows its surface: it is up to date');return true;}
    if(R.kind==='walk'){a3dToast(R.name+' follows the access data: it is up to date');return true;}   /* __acad3dV161 */
    if(R.kind==='tool')return bimTlLayerRerun(R);   /* __acad3dV172: its run again, with the same parameters */
    if(R.kind==='sunhours'){r=bimSunHours({date:R.data&&R.data.date});if(r.error){a3dToast('Sun hours: '+r.error);return false;}}
    else{r=bimRainFlow(objById(R.src)?R.src:null);if(r.error){a3dToast('Rain flow: '+r.error);return false;}}
    pushUndo();
    R.data=R.kind==='sunhours'?bimResSunData(r):bimResRainData(r);
    if(R.kind==='rain')R.src=r.terrain;
    R.key=bimResKeyFrom(r.stamp,R.kind);R.updated=bimResNow();
    delete A3D_RES_IMG[R.id];
    refreshLayers();paint();saveSoon();bimAnalyzeRefresh();
    a3dToast(R.name+' updated');
    return true;
  }
  function bimResultLayerRemove(id){
    var L=bimResLayers(),i,nm;
    for(i=0;i<L.length;i++)if(L[i].id===id)break;
    if(i>=L.length)return false;
    pushUndo();
    nm=L[i].name;L.splice(i,1);delete A3D_RES_IMG[id];
    if(A3D_LY.rsel==='res:'+id)A3D_LY.rsel=null;
    refreshLayers();paint();saveSoon();bimAnalyzeRefresh();
    a3dToast(nm+' removed');
    return true;
  }
  function bimResultLayerSet(id,field,val){
    var R=bimResById(id),v;
    if(!R)return false;
    if(field==='visible')v=!!val&&val!=='false';
    else if(field==='opacity'){v=parseFloat(val);if(!isFinite(v)){a3dToast('Opacity is a percentage, 10 to 100');return false;}v=Math.max(0.1,Math.min(1,v>1?v/100:v));v=Math.round(v*100)/100;}
    else if(field==='name'){v=String(val==null?'':val).replace(/\s+/g,' ').replace(/^ | $/g,'').slice(0,60);if(!v){a3dToast('A layer needs a name');refreshLayers();return false;}}
    else return false;
    if(field==='visible'?(R.visible!==false)===v:R[field]===v)return true;
    pushUndo();
    R[field]=v;
    refreshLayers();paint();saveSoon();
    return true;
  }
  /* to: another layer's id (its place), or an index */
  function bimResultLayerMove(id,to){
    var L=bimResLayers(),i=-1,j=-1,k,R;
    for(k=0;k<L.length;k++){if(L[k].id===id)i=k;if(L[k].id===to)j=k;}
    if(typeof to==='number'&&isFinite(to))j=Math.max(0,Math.min(L.length-1,Math.round(to)));
    if(i<0||j<0||i===j)return false;
    pushUndo();
    R=L.splice(i,1)[0];L.splice(j,0,R);
    refreshLayers();paint();saveSoon();
    return true;
  }
  /* the layers from a file or a store: what can be drawn, the rest let go */
  function bimResValid(a){
    if(!Array.isArray(a))return [];
    return a.filter(function(R){
      if(!R||typeof R.id!=='string'||typeof R.name!=='string')return false;
      if(R.kind==='terrain')return typeof R.src==='string'&&/^(slope|elevation|aspect|cutfill)$/.test(R.mode);
      if(R.kind==='walk')return R.src==='access';   /* __acad3dV161 */
      if(R.kind==='tool')return bimTlDataOk(R.data);   /* __acad3dV172 */   /* a regex: this runs at start-up, before the table above is set */
      return (R.kind==='sunhours'||R.kind==='rain')&&!!R.data&&typeof R.data.cells==='string'&&R.data.cells.length===R.data.nx*R.data.nz&&
        isFinite(R.data.x0)&&isFinite(R.data.z0)&&R.data.cell>0;
    });
  }
  /* ---- drawing ---- */
  function bimDrawBandTris(ctx,tin,tb,sp,alpha){
    var j,a,b,c;
    ctx.save();ctx.globalAlpha*=alpha;
    for(j=0;j<tin.tris.length;j++){
      if(tb.tri[j]<0)continue;
      a=sp[tin.tris[j][0]];b=sp[tin.tris[j][1]];c=sp[tin.tris[j][2]];
      if(!a||!b||!c)continue;
      ctx.fillStyle=ctx.strokeStyle=tb.bands[tb.tri[j]].col;ctx.lineWidth=0.5;
      ctx.beginPath();ctx.moveTo(a[0],a[1]);ctx.lineTo(b[0],b[1]);ctx.lineTo(c[0],c[1]);ctx.closePath();ctx.fill();ctx.stroke();
    }
    ctx.restore();
  }
  function bimSimDrawFlow(ctx,V,W,H,segs,maxAcc,alpha){
    var lm=Math.log(maxAcc+1)||1,i,g,a,b;
    ctx.save();ctx.globalAlpha=alpha;ctx.strokeStyle='#1565c0';ctx.lineCap='round';
    for(i=0;i<segs.length;i++){
      g=segs[i];a=toScreen([g[0],0,g[1]],V,W,H);b=toScreen([g[2],0,g[3]],V,W,H);
      if(!a||!b)continue;
      ctx.lineWidth=0.8+2.6*Math.log(g[4]+1)/lm;
      ctx.beginPath();ctx.moveTo(a[0],a[1]);ctx.lineTo(b[0],b[1]);ctx.stroke();
    }
    ctx.restore();
  }
  function bimResImage(R){
    var c=A3D_RES_IMG[R.id],d=R.data,img;
    if(c&&c.d===d)return c.img;
    img=bimSimGridImage(d,R.kind==='sunhours'?function(k){var ch=d.cells.charAt(k);return ch==='.'?null:(BIM_SIM_RAMP[+ch]||null);}:function(k){return d.cells.charAt(k)==='1'?'#2f7fe0c0':null;});
    A3D_RES_IMG[R.id]={d:d,img:img};
    return img;
  }
  function bimResDraw(ctx,V,W,H,R){
    var op=bimResOpacity(R),d=R.data,o,tin,tb;
    if(R.kind==='tool'){var im=bimTlDataOk(d)?bimTlImage(R):null;if(!im)return false;bimSimDrawGrid(ctx,V,W,H,d,im,d.y||0,op);return true;}   /* __acad3dV172 */
    if(R.kind==='sunhours'||R.kind==='rain'){
      if(!d||typeof d.cells!=='string')return false;
      bimSimDrawGrid(ctx,V,W,H,d,bimResImage(R),R.kind==='sunhours'?(d.ground||0):0,op);
      if(R.kind==='rain'&&Array.isArray(d.segs))bimSimDrawFlow(ctx,V,W,H,d.segs,d.maxAcc||0,op);
      return true;
    }
    if(R.kind==='walk')return bimResGone(R)?false:bimAccDrawPlan(ctx,V,W,H,op);   /* __acad3dV161 */
    if(R.kind!=='terrain'||bimResGone(R))return false;
    o=objById(R.src);tin=bimTerrainTin(o);
    tb=tin?(R.mode==='cutfill'?bimBandsOf(o,'cutfill'):bimTerrainBands(tin,R.mode)):null;
    if(!tb)return false;
    bimDrawBandTris(ctx,tin,tb,tin.P.map(function(p){return toScreen([p[0],0,p[1]],V,W,H);}),op);
    return true;
  }
  function drawResultLayers(ctx,V,W,H){
    A3D.lastResultDrawn=[];
    if(!bimCameraIsPlan())return;
    var L=bimResLayers(),i;
    for(i=L.length-1;i>=0;i--){
      if(L[i].visible===false)continue;
      try{if(bimResDraw(ctx,V,W,H,L[i]))A3D.lastResultDrawn.push(L[i].id);}
      catch(eR){console.warn('[BIM] A result layer could not be drawn',eR);}
    }
  }
  /* the commands */
  function bimSunHoursCommand(opts){
    var r=bimSunHours(opts);
    if(r.error){a3dToast('Sun hours: '+r.error);return r;}
    r.show=true;A3D_SIM.sun=r;
    paint();bimAnalyzeRefresh();
    a3dToast('Sun hours on '+r.date+': '+bimDispNum(r.min,1)+' to '+bimDispNum(r.max,1)+' h of '+bimDispNum(r.day,1)+' h of daylight; '+
      Math.round(r.sixPlus*100)+'% of the ground has 6 h or more'+(bimCameraIsPlan()?'':' (drawn in plan)'));
    return r;
  }
  function bimRainCommand(id,opts){
    var r=bimRainFlow(id,opts);
    if(r.error){a3dToast('Rain flow: '+r.error);return r;}
    r.show=true;A3D_SIM.rain=r;
    paint();bimAnalyzeRefresh();
    a3dToast('Rain on '+r.name+': '+r.ponds.length+' pond'+(r.ponds.length===1?'':'s')+
      (r.ponds.length?', '+bimDispNum(r.pondVolume,1)+' m\u00b3 held, the deepest '+bimDispNum(r.ponds[0].depth,2)+' m':'')+'; flow lines drawn'+(bimCameraIsPlan()?'':' in plan'));
    return r;
  }
  function bimSolarCommand(opts){
    a3dToast('Solar: putting a clear-sky year of sun on '+bimSolarTargets((opts&&opts.ids)||(A3D.selSet&&A3D.selSet.length?A3D.selSet:null)).length+' solid(s) ...');
    return bimSolarRun(opts).then(function(r){
      if(r.error){a3dToast('Solar: '+r.error);return r;}
      bimAnalyzeRefresh();
      a3dToast('Solar (clear sky, no clouds): '+r.count+' solid'+(r.count===1?'':'s')+(r.roofMean!==null?', roofs '+Math.round(r.roofMean)+' kWh/m\u00b2 a year on average':'')+
        ' -- Colour By "Solar on roof (kWh/m2 a year)" shows each');
      return r;
    });
  }
  function bimSimClear(which){
    var n=0;
    ['sun','solar','rain'].forEach(function(k){if((!which||which===k)&&A3D_SIM[k]){A3D_SIM[k]=null;n++;}});
    if(!which||which==='solar')A3D.objs.forEach(function(o){if(o.solar){delete o.solar;n++;}});
    paint();refreshProps();bimAnalyzeRefresh();
    return n;
  }
