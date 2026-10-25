  /* ================= __acad3dV93: the POINT node ================= */
  var BIM_POINT_MARK=0.15;          /* half-length of the marker cross, in model units */
  function bimIsPoint(o){
    return !!(o&&o.t==='sketch'&&o.kind==='point'&&o.pts&&o.pts.length===1);
  }
  /* The marker, as line segments in the plan. Every renderer draws from this one function, so
     the viewport, the DXF, the SVG and the sheet cannot show four different points. */
  function bimPointMarkerSegs(p){
    var m=BIM_POINT_MARK;
    return [[[p[0]-m,p[1]],[p[0]+m,p[1]]],
            [[p[0],p[1]-m],[p[0],p[1]+m]]];
  }
  /* Placed directly rather than through addSketchObj, because DIVIDE and MEASURE place many at
     once and addSketchObj clears the active sketch, selects what it made and toasts per
     object. The caller decides selection and what to say. */
  function bimAddPoint(x,z,y,layer){
    A3D.counts.point=(A3D.counts.point||0)+1;
    var o={
      id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),
      t:'sketch',kind:'point',name:'Point '+A3D.counts.point,col:'#ffd479',
      pos:[0,0,0],pts:[[x,z]],y:(typeof y==='number')?y:bimGetActiveLevel().elev,
      closed:false,layer:(layer===undefined?A3D.activeLayer:layer)
    };
    A3D.objs.push(o);
    return o;
  }
  /* __acad3dV94 */
  function bimAddCline(p,dir,isRay,y,layer){
    var len=Math.sqrt(dir[0]*dir[0]+dir[1]*dir[1]);
    if(!(len>1e-12))return null;
    A3D.counts.cline=(A3D.counts.cline||0)+1;
    var o={
      id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),
      t:'cline',ray:!!isRay,
      name:(isRay?'Ray ':'Xline ')+A3D.counts.cline,col:'#8a7fd0',
      pos:[0,0,0],p:[p[0],p[1]],dir:[dir[0]/len,dir[1]/len],
      y:(typeof y==='number')?y:bimGetActiveLevel().elev,
      layer:(layer===undefined?A3D.activeLayer:layer)
    };
    A3D.objs.push(o);
    return o;
  }
  function startClineTool(isRay){
    bimEnterDraftingMode();
    var lvl=bimGetActiveLevel();
    A3D.sk={tool:'xline',pts:[],ray:!!isRay,mode:null,angle:null,y:lvl.elev,on:null};
    bimSyncStatusHint();
    paint();
    a3dToast((isRay?'Ray':'Construction line')+': pick a point, or press '+
      bimClineModeKeyHint()+'; Escape when finished');
  }
  function bimClineModeKeyHint(){
    var out=[],i,name,m;
    for(i=0;i<BIM_CLINE_MODE_ORDER.length;i++){
      name=BIM_CLINE_MODE_ORDER[i];m=BIM_CLINE_MODES[name];
      if(m&&m.key)out.push(m.key+' for '+m.label.toLowerCase());
    }
    return out.join(', ');
  }
  /* A mode can only be chosen before a root is committed, which is where AutoCAD offers it.
     The prompt asks this same predicate, so the two cannot disagree. */
  function bimClineCanSetMode(sk){
    return !!(sk&&sk.tool==='xline'&&!sk.mode&&(!sk.pts||!sk.pts.length));
  }
  function bimSetClineMode(sk,mode){
    if(!bimClineCanSetMode(sk)||!BIM_CLINE_MODES[mode])return false;
    sk.mode=mode;
    sk.angle=null;
    bimSyncStatusHint();paint();
    return true;
  }
  /* The direction this sketch is currently able to produce without another point, or null when
     it still needs one. One predicate, consulted by the prompt and by the placement alike. */
  function bimClineReadyDir(sk){
    if(!sk||sk.tool!=='xline')return null;
    if(sk.mode==='hor'||sk.mode==='ver')return bimClineDir(sk.mode);
    if(sk.mode==='ang')return bimClineDir('ang',null,null,sk.angle);
    return null;
  }
  function bimPlaceCline(sk,p,dir){
    pushUndo();
    var o=bimAddCline(p,dir,sk.ray,sk.y,undefined);
    if(!o){
      console.warn('[BIM] Construction line could not be built',p,dir);
      a3dToast('That gives no direction for a construction line');
      return null;
    }
    A3D.sel=o.id;A3D.sel2=null;
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast(o.name+' created');
    return o;
  }
  /* __acad3dV96: what is selected that could be hatched directly. A closed sketch and a room
     are both already a closed ring; anything else means "pick a point instead". */
  function bimHatchableSelection(){
    var o=A3D.sel?objById(A3D.sel):null;
    if(!o)return null;
    /* __acad3dV97: world coordinates through the source contract, and the source recorded so
       the hatch follows the sketch or room it was put on. A room is a valid source: hatch on a
       room on a sketch is a chain, and the graph visits the room before the hatch. */
    if((o.t==='sketch'&&!bimIsPoint(o)&&o.closed!==false)||o.t==='room'){
      var sb=bimSourceBoundaryWorld(o);
      if(sb.error)return null;
      return {pts:sb.pts,bulges:sb.bulges,y:sb.y,from:o.name,sourceType:sb.type,sourceId:o.id};
    }
    return null;
  }
  function bimHatchDefaults(){
    var o=A3D.sel?objById(A3D.sel):null;
    if(bimIsHatch(o))
      return {pattern:o.pattern,patternScale:o.patternScale,patternAngle:o.patternAngle,
              patternColor:o.patternColor};
    return {pattern:(A3D.lastHatch&&A3D.lastHatch.pattern)||'diagonal',
            patternScale:(A3D.lastHatch&&A3D.lastHatch.patternScale)||1,
            patternAngle:(A3D.lastHatch&&A3D.lastHatch.patternAngle)||0,
            patternColor:(A3D.lastHatch&&A3D.lastHatch.patternColor)||'#555555'};
  }
  function bimHatchPatternOptions(sel){
    /* Derived from the renderer's own list, so the dialog cannot offer a pattern nothing draws
       and cannot miss one added later. 'none' is left out: a hatch with no pattern is not a
       hatch, it is a deletion. */
    var out='',i,n;
    for(i=0;i<BIM_HATCH_PATTERNS.length;i++){
      n=BIM_HATCH_PATTERNS[i];
      if(n==='none')continue;
      out+='<option value="'+n+'"'+(n===sel?' selected':'')+'>'+bimEsc(bimPatternLabel(n))+'</option>';
    }
    return out;
  }
  function bimOpenHatchDlg(mode){
    var editing=(mode==='edit');
    var target=editing?objById(A3D.sel):null;
    if(editing&&!bimIsHatch(target)){a3dToast('Hatchedit: select a hatch first');return;}
    var d0=bimHatchDefaults(),selObj=editing?null:bimHatchableSelection();
    closeDlg();
    var d=document.createElement('div');
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">'+(editing?'Hatch edit':'Hatch')+'</div><div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Pattern</label><select data-a3dp="pat">'+
      bimHatchPatternOptions(d0.pattern)+'</select></div>'+
      '<div class="a3d-dlgrow"><label>Angle (deg)</label><input type="number" step="any" data-a3dp="ang" value="'+(d0.patternAngle||0)+'"></div>'+
      '<div class="a3d-dlgrow"><label>Scale</label><input type="number" step="any" min="0.1" max="8" data-a3dp="sc" value="'+(d0.patternScale||1)+'"></div>'+
      '<div class="a3d-propnote">'+
      (editing?('Changing '+bimEsc(target.name)+'.')
             :(selObj?('Filling '+bimEsc(selObj.from)+' directly.')
                     :'Nothing closed is selected, so you will pick internal points; each click hatches the region around it.'))+
      '</div><div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">OK</button></div>';
    el.root.appendChild(d);el.dlg=d;
    function submit(){
      var pat=d.querySelector('[data-a3dp="pat"]').value;
      var ang=parseFloat(d.querySelector('[data-a3dp="ang"]').value);
      var sc=parseFloat(d.querySelector('[data-a3dp="sc"]').value);
      var eb=document.getElementById('a3d-dlgerr');
      if(!isFinite(ang)){eb.textContent='Angle must be a number of degrees';return;}
      if(!isFinite(sc)||sc<0.1||sc>8){eb.textContent='Scale must be between 0.1 and 8';return;}
      if(!bimPatternDraws(pat)){eb.textContent='That pattern has nothing to draw';return;}
      var opts={pattern:pat,patternAngle:ang,patternScale:sc,patternColor:d0.patternColor};
      A3D.lastHatch=opts;
      closeDlg();
      if(editing){bimApplyHatchEdit(target.id,opts);return;}
      if(selObj){
        pushUndo();
        var ho=bimAddHatch(selObj.pts,selObj.bulges,selObj.y,
          {pattern:opts.pattern,patternAngle:opts.patternAngle,patternScale:opts.patternScale,
           patternColor:opts.patternColor,sourceType:selObj.sourceType,sourceId:selObj.sourceId});
        if(!ho){a3dToast('Hatch: that boundary could not be used');return;}
        A3D.sel=ho.id;A3D.sel2=null;
        refreshTree();refreshHud();paint();saveSoon();
        a3dToast(ho.name+' created on '+selObj.from+', area '+bimHatchArea(ho).toFixed(3)+' m2');
        return;
      }
      startHatchTool(opts);
    }
    d.addEventListener('click',function(ev){var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;if(!b)return;if(b.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();});
    d.addEventListener('keydown',function(ev){if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}});
  }
  function bimApplyHatchEdit(id,opts){
    var o=objById(id);
    if(!bimIsHatch(o)){a3dToast('Hatchedit: select a hatch first');return null;}
    pushUndo();
    o.pattern=opts.pattern;
    o.patternAngle=((opts.patternAngle%180)+180)%180;
    o.patternScale=Math.max(0.1,Math.min(8,opts.patternScale));
    if(opts.patternColor)o.patternColor=opts.patternColor;
    refreshTree();refreshProps();paint();saveSoon();
    a3dToast(o.name+': '+bimPatternLabel(o.pattern)+' at '+o.patternAngle.toFixed(1)+
      ' deg, scale '+o.patternScale.toFixed(2));
    return o;
  }
  function startHatchTool(opts){
    bimEnterDraftingMode();
    var lvl=bimGetActiveLevel();
    A3D.sk={tool:'hatch',pts:[],y:lvl.elev,on:null,hatch:opts||bimHatchDefaults()};
    bimSyncStatusHint();
    paint();
    a3dToast('Hatch: click inside a region to fill it; Escape when finished');
  }
  function bimApplyHatchAt(pt,y,opts){
    var edges=bimBoundaryEdges(y,{walls:true,sketches:true,clines:true});
    if(!edges.length){a3dToast('Hatch: there is nothing on this plan to bound a region');return null;}
    var res=bimTraceBoundary(edges,pt);
    if(res.error){a3dToast('Hatch: '+res.error);return null;}
    pushUndo();
    var o=bimAddHatch(res.pts,res.bulges,y,opts);
    if(!o){a3dToast('Hatch: that region could not be filled');return null;}
    /* __acad3dV99: an associative hatch -- it follows the shapes that bound it */
    o.region={seed:[pt[0],pt[1]],y:y,want:'all',members:(res.srcIds||[]).slice(),
              sig:bimEdgesSig(edges),open:false};
    o.sourceType='region';o.sourceId=null;
    A3D.sel=o.id;A3D.sel2=null;
    refreshTree();refreshHud();paint();saveSoon();
    var msg=o.name+' created, area '+bimHatchArea(o).toFixed(3)+' m2';
    if(res.islands)
      msg+=' - NOTE: this region has something inside it, and the hatch has no hole, so it '+
           'covers the island too';
    a3dToast(msg);
    return o;
  }
  /* __acad3dV95 */
  function startBoundaryTool(){
    bimEnterDraftingMode();
    var lvl=bimGetActiveLevel();
    A3D.sk={tool:'boundary',pts:[],y:lvl.elev,on:null};
    bimSyncStatusHint();
    paint();
    a3dToast('Boundary: click inside a region to trace it; Escape when finished');
  }
  function bimApplyBoundary(pt,y){
    var edges=bimBoundaryEdges(y,{walls:true,sketches:true,clines:true});
    if(!edges.length){a3dToast('Boundary: there is nothing on this plan to trace');return null;}
    var res=bimTraceBoundary(edges,pt);
    if(res.error){a3dToast('Boundary: '+res.error);return null;}
    pushUndo();
    /* addSketchObj reads the active sketch for its plane and host and then clears it, so the
       state is put back afterwards and the command stays live for the next pick. */
    var sk=A3D.sk,keep=sk?{tool:sk.tool,pts:[],y:sk.y,on:sk.on}:null;
    A3D.sk={tool:'boundary',pts:[],y:y,on:keep?keep.on:null};
    var msg='Boundary traced, area '+res.area.toFixed(3)+' m2';
    if(res.islands)
      msg+=' - NOTE: this region has something inside it, and a polyline cannot carry a hole, '+
           'so the area above counts the island in';
    var o=addSketchObj(res.pts,{bulges:res.bulges,toast:msg,noUndo:true});   /* __acad3dV100: snapshot taken above */
    A3D.sk=keep;
    bimSyncStatusHint();paint();
    return o;
  }
  function startPointTool(){
    bimEnterDraftingMode();
    var lvl=bimGetActiveLevel();
    A3D.sk={tool:'point',pts:[],y:lvl.elev,on:null};
    bimSyncStatusHint();
    paint();
    a3dToast('Point: click to place a node; Escape or Enter when finished');
  }
  /* What curve does this object describe? One answer for both commands, so a wall and a
     sketch divide through identical code -- which is also why a CURVED wall divides correctly
     with nothing written for it, and why an arc's marks land at equal ARC LENGTH. */
  function bimDivideSource(o){
    if(!o)return null;
    if(bimIsPoint(o))return null;
    if(o.t==='sketch'&&o.pts&&o.pts.length>=2)
      return {pts:o.pts,bulges:o.bulges||null,closed:o.closed!==false,y:o.y};
    if(o.t==='solid'&&o.bim&&o.bim.centerline&&o.bim.centerline.length>=2)
      return {pts:o.bim.centerline,bulges:o.bim.bulges||null,closed:!!o.bim.closed,y:o.bim.baseY};
    return null;
  }
  function bimPlaceMarks(o,src,pts,label){
    pushUndo();
    var made=[],i,p;
    for(i=0;i<pts.length;i++){
      p=bimAddPoint(pts[i][0],pts[i][1],src.y,o.layer);
      made.push(p.id);
    }
    A3D.selSet=made;A3D.sel=made.length?made[0]:null;A3D.sel2=null;
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast(label);
    return made;
  }
  function bimApplyDivide(id,n){
    var o=objById(id);
    if(!o){a3dToast('Divide: select an object first');return null;}
    var src=bimDivideSource(o);
    if(!src){a3dToast('Divide works on sketches and walls (selected object is a '+
      (bimIsPoint(o)?'point':(o.t||'?'))+')');return null;}
    var res=bimDividePoints(src.pts,src.bulges,src.closed,n);
    if(res.error){a3dToast('Divide: '+res.error);return null;}
    if(!res.points.length){a3dToast('Divide placed no points');return null;}
    return bimPlaceMarks(o,src,res.points,'Divided into '+n+': '+res.points.length+
      ' point(s) every '+bimFmtLen(res.spacing));
  }
  function bimApplyMeasure(id,d){
    var o=objById(id);
    if(!o){a3dToast('Measure: select an object first');return null;}
    var src=bimDivideSource(o);
    if(!src){a3dToast('Measure works on sketches and walls (selected object is a '+
      (bimIsPoint(o)?'point':(o.t||'?'))+')');return null;}
    var res=bimMeasurePoints(src.pts,src.bulges,src.closed,d);
    if(res.error){a3dToast('Measure: '+res.error);return null;}
    if(!res.points.length){a3dToast('Measure placed no points');return null;}
    /* The remainder is stated. A drafter stepping off a bar spacing needs to know what is left
       at the far end, and a command that hides it has answered a different question. */
    return bimPlaceMarks(o,src,res.points,'Measured every '+bimFmtLen(d)+': '+
      res.points.length+' point(s), '+bimFmtLen(res.leftover)+' left over');
  }
  function bimOpenSpacingDlg(kind){
    var id=A3D.sel;
    var o=id?objById(id):null;
    if(!o||!bimDivideSource(o)){
      a3dToast((kind==='divide'?'Divide':'Measure')+': select a sketch or a wall first');
      return;
    }
    var src=bimDivideSource(o);
    var L=bimBulgedLength(src.pts,src.bulges,src.closed);
    closeDlg();
    var isDiv=(kind==='divide');
    var d=document.createElement('div');
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">'+(isDiv?'Divide':'Measure')+'</div><div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>'+(isDiv?'Number of segments':'Segment length')+'</label>'+
      '<input type="number" step="'+(isDiv?'1':'any')+'" data-a3dp="v" value="'+(isDiv?'4':(L/4).toFixed(3))+'"></div>'+
      '<div class="a3d-propnote">'+bimEsc(o.name||'Object')+' is '+bimFmtLen(L)+' long, measured along the curve.'+
      (isDiv?' Dividing into n places n-1 points; the ends are not marked.'
            :' Points are stepped off from the start; any remainder is left at the far end.')+'</div>'+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">OK</button></div>';
    el.root.appendChild(d);el.dlg=d;
    var vI=d.querySelector('[data-a3dp="v"]');
    function submit(){
      var v=parseFloat(vI.value);
      var eb=document.getElementById('a3d-dlgerr');
      /* Validated by the same builder the command runs, so the dialog cannot accept a value
         the geometry would then refuse. */
      var probe=isDiv?bimDividePoints(src.pts,src.bulges,src.closed,v)
                     :bimMeasurePoints(src.pts,src.bulges,src.closed,v);
      if(probe.error){eb.textContent=probe.error;return;}
      closeDlg();
      if(isDiv)bimApplyDivide(id,v);else bimApplyMeasure(id,v);
    }
    d.addEventListener('click',function(ev){var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;if(!b)return;if(b.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();});
    d.addEventListener('keydown',function(ev){if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}});
    vI.focus();vI.select();
  }
  /* __acad3dV93: what shape is this sketch. The ONE answer, so the five consumers that
     each used to read o.pts directly cannot disagree with each other or with what is drawn. */
  function bimSketchOutline(o){
    if(!o||!o.pts)return [];
    return bimFlattenSketch(o)||o.pts;
  }
  function doPad(s,h){
    var P=sketchCCW(bimSketchOutline(s));
    if(P.length<3){a3dToast('Sketch needs at least 3 points');return null;}
    var m=padMesh(P,s.y,h);
    pushUndo();
    A3D.counts.pad=(A3D.counts.pad||0)+1;
    /* __acad3dV123: at the sketch's own offset -- the outline is in the sketch's frame, so a sketch
       that had been moved was padded where it had been before the move */
    var o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:'Pad '+A3D.counts.pad,col:'#9db4c8',pos:bimObjOffset(s),mesh:m};
    var i=A3D.objs.indexOf(s);
    if(i>=0)A3D.objs.splice(i,1);
    A3D.objs.push(o);
    A3D.sel=o.id;A3D.sel2=null;
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast(o.name+' extruded from sketch');
    return o;
  }
  function doPocket(s,depth){
    var P=sketchCCW(bimSketchOutline(s));
    if(P.length<3){a3dToast('Sketch needs at least 3 points');return null;}
    /* __acad3dV123: the outline in the WORLD, where the solids are measured -- it was compared and
       cut in the sketch's own frame, so a sketch that had been moved cut where it had been */
    var sq=bimObjOffset(s),sy=(s.y||0)+sq[1];
    P=P.map(function(p){return [p[0]+sq[0],p[1]+sq[2]];});
    var tgt=objById(s.on);
    if(tgt&&tgt.t==='sketch')tgt=null;
    if(!tgt){
      var cx=0,cz=0,i2;
      for(i2=0;i2<P.length;i2++){cx+=P[i2][0];cz+=P[i2][1];}
      cx/=P.length;cz/=P.length;
      var best=null,bi;
      for(bi=0;bi<A3D.objs.length;bi++){
        var cand=A3D.objs[bi];
        if(cand.t==='sketch')continue;
        var bb=objBBox(cand);
        if(!bb)continue;
        if(cx>=bb.mn[0]-0.01&&cx<=bb.mx[0]+0.01&&cz>=bb.mn[2]-0.01&&cz<=bb.mx[2]+0.01&&sy>=bb.mn[1]-0.05&&sy<=bb.mx[1]+0.05){
          if(!best||bb.mx[1]>objBBox(best).mx[1])best=cand;
        }
      }
      tgt=best;
    }
    if(!tgt){a3dToast('Pocket needs a solid under the sketch: select the solid, then draw the sketch on it');return null;}
    var bbT=objBBox(tgt);
    var mnx=1e9,mxx=-1e9,mnz=1e9,mxz=-1e9,i3;
    for(i3=0;i3<P.length;i3++){
      if(P[i3][0]<mnx)mnx=P[i3][0];
      if(P[i3][0]>mxx)mxx=P[i3][0];
      if(P[i3][1]<mnz)mnz=P[i3][1];
      if(P[i3][1]>mxz)mxz=P[i3][1];
    }
    if(mxx<bbT.mn[0]||mnx>bbT.mx[0]||mxz<bbT.mn[2]||mnz>bbT.mx[2]){a3dToast('Pocket sketch does not overlap the target solid');return null;}
    var tool={mesh:padMesh(P,sy-depth,depth+0.02),pos:[0,0,0]};
    var out;
    try{out=csgSubtract(meshPolys(tgt),meshPolys(tool));}catch(e){a3dToast('Pocket failed: '+(e&&e.message?e.message:e));return null;}
    var nm=polysToMesh(out);
    if(!nm||nm.f.length<4){a3dToast('Pocket produced an empty result');return null;}
    pushUndo();
    A3D.counts.pocket=(A3D.counts.pocket||0)+1;
    var o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:'Pocket '+A3D.counts.pocket,col:tgt.col||'#9db4c8',pos:[0,0,0],mesh:nm};
    var ia=A3D.objs.indexOf(s);if(ia>=0)A3D.objs.splice(ia,1);
    var ib=A3D.objs.indexOf(tgt);if(ib>=0)A3D.objs.splice(ib,1);
    A3D.objs.push(o);
    A3D.sel=o.id;A3D.sel2=null;
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast(o.name+' cut into '+tgt.name);
    return o;
  }
