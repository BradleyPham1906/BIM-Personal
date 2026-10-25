  /* ================= __acad3dV121: a plot, by the layers =================
     A plot leaves out a layer that is off, frozen or set not to plot, does not fade a locked layer,
     and draws transparency only in a presentation (bimLayerShown and bimLayerAlpha read A3D_PLOT).
     The By Layer linework -- LINE, PLINE, ARC, CIRCLE, POINT -- is plotted with its layer's
     linetype, lineweight and, in a presentation, color; a technical plot stays monochrome. */
  /* __acad3dV122: whether the drawing is drawn with its presentation graphics -- in a plot, the
     appearance it is plotted in; otherwise the Appearance setting. A sheet's viewports are drawn by
     the same paint() as the model and ask the same question, so a sheet on screen, its PNG, its
     raster print, its pages and its vector print are all one appearance. */
  function bimPresentGraphics(){return A3D_PLOT.on?!!A3D_PLOT.pres:!!A3D.presentMode;}
  function bimWithPlotPass(pres,fn){
    var was={on:A3D_PLOT.on,pres:A3D_PLOT.pres};
    A3D_PLOT.on=true;A3D_PLOT.pres=!!pres;
    try{return fn();}
    finally{A3D_PLOT.on=was.on;A3D_PLOT.pres=was.pres;}
  }
  /* In a presentation -- the only plot with graphics to resolve, rg being null in a technical one --
     the layer's color, lineweight and transparency take the place of the drawing's defaults, field
     by field, so an instance override the user set still wins. */
  function bimLookPlotGraphics(o,rg){
    if(!rg)return rg;
    var ly=bimLayerOf(o),ov=(o.graphicsOverride&&o.graphicsOverride.presentation)||{},g={},k;
    for(k in rg)if(rg.hasOwnProperty(k))g[k]=rg[k];
    if(ly&&!ov.hasOwnProperty('lineColor')&&/^#[0-9a-fA-F]{6}$/.test(ly.color||''))g.lineColor=ly.color;
    if(ly&&!ov.hasOwnProperty('lineWeight')&&ly.lineweight!==null&&ly.lineweight!==undefined&&isFinite(ly.lineweight))
      g.lineWeight=Math.max(0.05,+ly.lineweight);
    if(!ov.hasOwnProperty('opacity'))g.opacity=(isFinite(g.opacity)?g.opacity:1)*bimLayerAlpha(o);
    return g;
  }
  /* What a plot adds for the By Layer linework, `unit` being the drawing's units to a paper
     millimetre: the linetype's dash array always, and in a technical plot the lineweight (in a
     presentation the lineweight is already in the graphics above). */
  function bimLookPlotAttrs(o,unit,pres){
    var ly=bimLayerOf(o),lt=ly?bimLinetypeDef(ly.linetype):null,d=[],i,s='';
    if(lt&&lt.pat.length){
      for(i=0;i<lt.pat.length;i++)d.push(+(((lt.pat[i]===0)?0.4:Math.abs(lt.pat[i]))*unit).toFixed(6));
      s+=' stroke-dasharray="'+d.join(' ')+'"';
    }
    if(!pres&&ly&&ly.lineweight!==null&&ly.lineweight!==undefined&&isFinite(ly.lineweight))
      s+=' stroke-width="'+(Math.max(0.05,+ly.lineweight)*unit).toFixed(6)+'"';
    return s;
  }
  function bimBuildSVG(mode){
    return bimWithPlotPass(mode==='presentation',function(){return bimBuildSVGDrawing(mode);});
  }
  function bimBuildSVGDrawing(mode){
    var pres=(mode==='presentation');
    var layers=A3D.layers,i;
    var minX=Infinity,maxX=-Infinity,minZ=Infinity,maxZ=-Infinity;
    var buckets={},order=[];
    var stats={polyline:0,line:0,text:0,skipped:0};
    var EX=[0,0,0];   /* __acad3dV104 */
    function W(p){return [p[0]+EX[0],p[1]+EX[2]];}
    function WL(ps){return ps?ps.map(W):ps;}
    var cmds=[];
    function bucket(lay){
      if(!buckets[lay]){buckets[lay]=[];order.push(lay);}
      return buckets[lay];
    }
    function trackPt(p){
      if(p[0]<minX)minX=p[0];if(p[0]>maxX)maxX=p[0];
      if(p[1]<minZ)minZ=p[1];if(p[1]>maxZ)maxZ=p[1];
    }
    function layerOf(o){
      var k;
      for(k=0;k<layers.length;k++)if(layers[k].id===o.layer)return bimDxfLayerName(layers[k].name);
      return '0';
    }
    // __acad3dV61: geometry emission is now decoupled from string-building -- poly/line/text push a
    // command record and only track bounds (trackPt) here; the actual <path>/<line>/<text> markup is
    // built in a second pass below, once diag/strokeW are known, because presentation stroke widths
    // are calibrated against strokeW (which itself depends on the full drawing's bounds).
    function poly(pts,closed,lay,objId,rg,forFill,lk){   /* __acad3dV121: lk, the object drawn By Layer */
      if(!pts||pts.length<2)return;
      pts=WL(pts);   /* __acad3dV104 */
      var q;for(q=0;q<pts.length;q++)trackPt(pts[q]);
      bucket(lay);
      cmds.push({k:'poly',pts:pts,closed:closed,lay:lay,objId:objId,rg:rg,forFill:!!forFill,lk:lk||null});
      stats.polyline++;
    }
    function line(a,b,lay,objId,rg,lk){
      a=W(a);b=W(b);   /* __acad3dV104 */
      trackPt(a);trackPt(b);
      bucket(lay);
      cmds.push({k:'line',a:a,b:b,lay:lay,objId:objId,rg:rg,lk:lk||null});
      stats.line++;
    }
    function text(pt,str,h,lay,objId,rg){
      pt=W(pt);   /* __acad3dV104 */
      trackPt(pt);
      bucket(lay);
      cmds.push({k:'text',pt:pt,str:str,h:h,lay:lay,objId:objId,rg:rg});
      stats.text++;
    }
    // Wall poche: outer ring minus inner ring as ONE evenodd path, so a filled wall never covers the
    // room space inside it. Only emitted when presentation mode actually resolves a fill and the wall
    // has no opening breaks -- a broken (door/window cut) outline is disjoint run segments, not a
    // closed ring, and poche-filling those correctly needs real 2D boolean geometry this codebase
    // does not have (the same pre-existing gap already disclosed for opening cuts in the plan outline
    // itself, Phase 50c).
    function wallPoche(outer,inner,lay,objId,rg){
      if(!outer||outer.length<3||!inner||inner.length<3)return;
      outer=WL(outer);inner=WL(inner);   /* __acad3dV104 */
      var q;for(q=0;q<outer.length;q++)trackPt(outer[q]);for(q=0;q<inner.length;q++)trackPt(inner[q]);
      bucket(lay);
      cmds.push({k:'poche',outer:outer,inner:inner,lay:lay,objId:objId,rg:rg});
      stats.polyline++;
    }
    for(i=0;i<A3D.objs.length;i++){
      var o=A3D.objs[i],lay=layerOf(o),b=o.bim;
      if(!bimLayerShown(o))continue;   /* __acad3dV121: it never asked; a plot leaves out what is off, frozen or not plotted */
      EX=bimExportOffset(o);   /* __acad3dV104 */
      var rg=pres?bimResolveGraphics(o,'presentation'):null;
      if(b&&b.type==='wall'&&b.centerline){
        poly(b.centerline,!!b.closed,lay,o.id,rg,false);
        if(b.innerLoop&&b.outerLoop){
          var brkS=bimWallOpeningBreaks(o);
          // bimWallOpeningBreaks ALWAYS returns a truthy result for a wall with valid loops -- a
          // wall with no openings gets the whole loop back as a single closed "run", not null. So
          // "no openings" (the only case a poche ring is geometrically valid) is detected from the
          // shape of that result, not from brkS's own truthiness.
          var noOpeningsS=brkS&&brkS.outerClosed&&brkS.innerClosed&&brkS.outerRuns.length===1&&
            brkS.innerRuns.length===1&&!brkS.jambs.length&&!brkS.glaze.length;
          if(pres&&rg&&rg.fill!=='none'&&noOpeningsS){
            wallPoche(b.outerLoop,b.innerLoop,lay,o.id,rg);
          }else if(brkS){
            var bsi;
            for(bsi=0;bsi<brkS.outerRuns.length;bsi++)poly(brkS.outerRuns[bsi],brkS.outerClosed,lay,o.id,rg,false);
            for(bsi=0;bsi<brkS.innerRuns.length;bsi++)poly(brkS.innerRuns[bsi],brkS.innerClosed,lay,o.id,rg,false);
            for(bsi=0;bsi<brkS.jambs.length;bsi++)line(brkS.jambs[bsi][0],brkS.jambs[bsi][1],lay,brkS.jambs[bsi][2],rg);
            for(bsi=0;bsi<brkS.glaze.length;bsi++)line(brkS.glaze[bsi][0],brkS.glaze[bsi][1],lay,brkS.glaze[bsi][2],rg);
          }else{
            poly(b.innerLoop,true,lay,o.id,rg,false);
            poly(b.outerLoop,true,lay,o.id,rg,false);
          }
        }
      }else if(o.t==='room'){
        poly(o.pts,true,lay,o.id,bimRoomSchemeGraphics(o,rg,pres),true);   /* __acad3dV105: the colour fill, as on the canvas */
        if(!bimRoomTagged(o.id))text(bimRoomLabelPoint(o),bimRoomLabelText(o),0.25,lay,o.id,rg);   /* __acad3dV101 */
      }else if(bimIsHatch(o)){                  /* __acad3dV96: rg is the hatch's OWN
        appearance, passed whatever the mode is, because a hatch is geometry and not a
        presentation override. forFill true is what turns the pattern overlay on. */
        poly(bimHatchOutline(o),true,lay,o.id,bimHatchGraphics(o),true);
      }else if(bimIsCline(o)){                  /* __acad3dV94 */
        var svCL=bimClineVisibleSeg(o,null);
        if(svCL)line(svCL[0],svCL[1],lay,o.id,rg);
      }else if(bimIsPoint(o)){                  /* __acad3dV93 */
        var svPM=bimPointMarkerSegs(o.pts[0]),svPK;
        for(svPK=0;svPK<svPM.length;svPK++)line(svPM[svPK][0],svPM[svPK][1],lay,o.id,bimLookPlotGraphics(o,rg),o);   /* __acad3dV121 */
      }else if(o.t==='sketch'&&o.pts&&o.pts.length>=2){
        poly(bimFlattenSketch(o),o.closed!==false,lay,o.id,bimLookPlotGraphics(o,rg),false,o);   /* __acad3dV88; V121 By Layer */
      }else if(o.t==='dim'&&bimDimKind(o)==='linear'){
        line(o.d1,o.d2,lay,o.id,rg);line(o.p1,o.d1,lay,o.id,rg);line(o.p2,o.d2,lay,o.id,rg);
        text([(o.d1[0]+o.d2[0])/2,(o.d1[1]+o.d2[1])/2],o.length.toFixed(2),0.2,lay,o.id,rg);
      }else if(o.t==='dim'&&bimDimKind(o)==='angular'){
        line(o.vertex,o.ap1,lay,o.id,rg);line(o.vertex,o.ap2,lay,o.id,rg);
        var arcPts=[],ai;
        for(ai=0;ai<=16;ai++){
          var aa=o.a1+o.sweep*(ai/16);
          arcPts.push([o.vertex[0]+Math.cos(aa)*o.arcRadius,o.vertex[1]+Math.sin(aa)*o.arcRadius]);
        }
        poly(arcPts,false,lay,o.id,rg,false);
        var midA=o.a1+o.sweep/2;
        text([o.vertex[0]+Math.cos(midA)*o.arcRadius*1.25,o.vertex[1]+Math.sin(midA)*o.arcRadius*1.25],o.degrees.toFixed(1)+'deg',0.2,lay,o.id,rg);
      }else if(o.t==='dim'&&(bimDimKind(o)==='radius'||bimDimKind(o)==='diameter')){
        var cPts=[],ci2;
        for(ci2=0;ci2<=32;ci2++){
          var cc=(ci2/32)*Math.PI*2;
          cPts.push([o.center[0]+Math.cos(cc)*o.radius,o.center[1]+Math.sin(cc)*o.radius]);
        }
        poly(cPts,true,lay,o.id,rg,false);
        line(o.dStart,o.dEdge,lay,o.id,rg);
        text([(o.dStart[0]+o.dEdge[0])/2,(o.dStart[1]+o.dEdge[1])/2],(bimDimKind(o)==='diameter'?'D':'R')+o.value.toFixed(2),0.2,lay,o.id,rg);
      }else if(o.t==='dim'&&bimDimKind(o)==='leader'){
        poly([o.anchor,o.elbow,o.landing],false,lay,o.id,rg,false);
        text(o.landing,o.label||'',0.2,lay,o.id,rg);
      }else if(bimIsAlignment(o)){   /* __acad3dV127 */
        var axS=bimAlignExport(o),alS;
        poly(axS.pts,false,lay,o.id,rg,false);
        for(alS=0;alS<axS.labels.length;alS++)text(axS.labels[alS].p,axS.labels[alS].t,0.25,lay,o.id,rg);
      }else if(bimIsProperty(o)){   /* __acad3dV103 */
        var pgS=bimPropertyGeometry(o),lks;
        poly(pgS.ring,true,lay,o.id,rg,false);
        for(lks=0;lks<o.legs.length&&lks+1<pgS.pts.length;lks++)
          text([(pgS.pts[lks][0]+pgS.pts[lks+1][0])/2,(pgS.pts[lks][1]+pgS.pts[lks+1][1])/2],
               bimFormatBearing(o.legs[lks].az)+' '+o.legs[lks].d.toFixed(2),0.25,lay,o.id,rg);
      }else if(o.t==='roomtag'){   /* __acad3dV101 */
        if(bimAnnotDrawable(o))text(o.pt,bimRoomTagText(o),0.25,lay,o.id,rg);
      }else if(o.t==='text'){
        text(o.pt,o.text,0.25,lay,o.id,rg);
      }else if(b&&(b.type==='floor'||b.type==='ceiling'||b.type==='roof')&&(b.profile||b.footprint)){
        poly(b.profile||b.footprint,true,lay,o.id,rg,true);
      }else if(b&&b.type==='column'&&b.center){
        var c=b.center,hw=b.width/2,hd=b.depth/2;
        poly(bimRectFootprint(c,b.width,b.depth,b.rotation||0),true,lay,o.id,rg,true);
      }else if(bimIsFooting(o)&&b.plan){   /* __acad3dV102 */
        var fps;
        for(fps=0;fps<b.plan.length;fps++)poly(b.plan[fps],true,lay,o.id,rg,true);
      }else{
        stats.skipped++;
      }
    }
    if(!isFinite(minX)){minX=0;maxX=10;minZ=0;maxZ=10;}
    var diag=Math.max(Math.hypot(maxX-minX,maxZ-minZ),1e-6);
    var margin=Math.max(diag*0.04,0.1);
    var vbX=minX-margin,vbY=minZ-margin,   /* __acad3dV104: y down, as the plan */
        vbW=(maxX-minX)+2*margin,vbH=(maxZ-minZ)+2*margin;
    var strokeW=Math.max(diag*0.0015,0.005);
    // Presentation stroke widths are calibrated against this same strokeW so an unstyled object's
    // resolved default (0.25mm, from bimDefaultGraphics) reproduces this exact technical value --
    // the same "an untouched default matches old output" rule Phase 52a used for BIM_LW_TO_PX.
    var svgLwUnit=strokeW/0.25;
    function styleAttrs(rg,fillOn){
      if(!bimPatternAlways(pres,rg))return {fill:'none',extra:''};   /* __acad3dV96 */
      var fillVal=(fillOn&&rg.fill!=='none')?rg.fill:'none';
      var sw=Math.max(strokeW*0.1,svgLwUnit*rg.lineWeight);
      var extra=' stroke="'+rg.lineColor+'" stroke-width="'+sw.toFixed(6)+'"'+(rg.opacity!==1?' opacity="'+rg.opacity+'"':'');
      return {fill:fillVal,extra:extra};
    }
    /* __acad3dV63: model space works in metres and svgLwUnit is already "model units per mm"
       (it is what turns a 0.25 mm line weight into this drawing's stroke width), so it is exactly
       the units-per-mm the pattern tiles need -- no second calibration constant. flipY is true
       because every coordinate below is emitted as -y. */
    var patReg=bimPatternRegistry(svgLwUnit,true,'a3dpat');
    /* __acad3dV63: in PRESENTATION mode only, room commands are emitted before everything else so
       a room's colour fill sits UNDER the model rather than over it. This was invisible until now
       because the live view's default room fill is a 14%-alpha wash; once Phase 52a let a room
       take a real opaque fill and this phase let it take a hatch, a room drawn last simply painted
       over every column, wall face and dimension inside it -- which is not what a room colour
       scheme means in any BIM tool. The partition is stable (relative order within rooms, and
       within everything else, is untouched) and is skipped entirely in technical mode, so a
       technical export is emitted in exactly the order it always was. */
    var roomIds={},ri,roomFillOut=[];
    if(pres)for(ri=0;ri<A3D.objs.length;ri++)if(A3D.objs[ri].t==='room')roomIds[A3D.objs[ri].id]=true;
    // Only a room's FILL is moved under. Its name/area label stays with everything else: a label
    // is meant to be read on top of the drawing, not buried beneath a wall poche.
    function isRoomFill(cmd){return pres&&roomIds[cmd.objId]&&cmd.k!=='text';}
    /* A hatch is drawn OVER the object's own fill, not instead of it, matching the live view: the
       base path keeps its colour and outline, and a second path with the same geometry carries
       the pattern with no stroke of its own. Emitting one path with fill="url(#...)" instead
       would silently discard whatever poche colour sits underneath. */
    function patternOverlay(cmd,d,extraAttrs){
      if(!bimPatternAlways(pres,cmd.rg))return null;   /* __acad3dV96 */
      var pf=patReg.resolve(cmd.rg);
      if(!pf)return null;
      var op=(cmd.rg.opacity!==1)?' opacity="'+cmd.rg.opacity+'"':'';
      return '<path'+(cmd.objId?' data-obj="'+bimEscXml(cmd.objId)+'"':'')+' data-pattern="'+bimEscXml(cmd.rg.pattern)+'"'+
             op+(extraAttrs||'')+' d="'+d+'" fill="'+pf+'" stroke="none"/>';
    }
    var ci,out,ovl;
    for(ci=0;ci<cmds.length;ci++){
      var cmd=cmds[ci];
      ovl=null;
      if(cmd.k==='poly'){
        var q,d='';
        for(q=0;q<cmd.pts.length;q++)d+=(q?'L':'M')+cmd.pts[q][0].toFixed(6)+','+(cmd.pts[q][1]).toFixed(6)+' ';
        if(cmd.closed)d+='Z';
        var stp=styleAttrs(cmd.rg,cmd.forFill);
        out='<path'+(cmd.objId?' data-obj="'+bimEscXml(cmd.objId)+'"':'')+stp.extra+(cmd.lk?bimLookPlotAttrs(cmd.lk,svgLwUnit,pres):'')+' d="'+d.trim()+'" fill="'+stp.fill+'"/>';
        // Only a closed, fill-bearing outline can carry a hatch; an open polyline has no interior.
        if(cmd.forFill&&cmd.closed)ovl=patternOverlay(cmd,d.trim(),'');
      }else if(cmd.k==='poche'){
        var q2,d2='';
        for(q2=0;q2<cmd.outer.length;q2++)d2+=(q2?'L':'M')+cmd.outer[q2][0].toFixed(6)+','+(cmd.outer[q2][1]).toFixed(6)+' ';
        d2+='Z ';
        for(q2=0;q2<cmd.inner.length;q2++)d2+=(q2?'L':'M')+cmd.inner[q2][0].toFixed(6)+','+(cmd.inner[q2][1]).toFixed(6)+' ';
        d2+='Z';
        var stpo=styleAttrs(cmd.rg,true);
        out='<path'+(cmd.objId?' data-obj="'+bimEscXml(cmd.objId)+'"':'')+stpo.extra+' fill-rule="evenodd" d="'+d2.trim()+'" fill="'+stpo.fill+'"/>';
        // The hatch has to honour the same outer-minus-inner rule as the poche it sits on, or it
        // would fill the room inside the wall as well as the wall itself.
        ovl=patternOverlay(cmd,d2.trim(),' fill-rule="evenodd"');
      }else if(cmd.k==='line'){
        var stl=styleAttrs(cmd.rg,false);
        out='<line'+(cmd.objId?' data-obj="'+bimEscXml(cmd.objId)+'"':'')+stl.extra+(cmd.lk?bimLookPlotAttrs(cmd.lk,svgLwUnit,pres):'')+' x1="'+cmd.a[0].toFixed(6)+'" y1="'+(cmd.a[1]).toFixed(6)+'" x2="'+cmd.b[0].toFixed(6)+'" y2="'+(cmd.b[1]).toFixed(6)+'"/>';
      }else{
        var fillColor=(pres&&cmd.rg)?cmd.rg.lineColor:'currentColor';
        var opAttr=(pres&&cmd.rg&&cmd.rg.opacity!==1)?' opacity="'+cmd.rg.opacity+'"':'';
        out='<text'+(cmd.objId?' data-obj="'+bimEscXml(cmd.objId)+'"':'')+opAttr+' x="'+cmd.pt[0].toFixed(6)+'" y="'+(cmd.pt[1]).toFixed(6)+'" font-size="'+(cmd.h*1.4).toFixed(4)+'" stroke="none" fill="'+fillColor+'">'+bimEscXml(cmd.str)+'</text>';
      }
      /* Room fills leave the per-layer buckets and go into their own group, emitted first (see
         the presentation-room-fills group below). They cannot simply be reordered inside their
         bucket: the final assembly walks the LAYER groups in the order the layers were first
         used, so a room on a different layer from the walls would still land after them however
         its own bucket was sorted. Each path keeps a data-layer attribute so no layer information
         is lost by moving it out of the layer group. */
      if(isRoomFill(cmd)){
        var lattr=' data-layer="'+bimEscXml(cmd.lay)+'"';
        roomFillOut.push(out.replace('<path','<path'+lattr));
        if(ovl)roomFillOut.push(ovl.replace('<path','<path'+lattr));
      }else{
        buckets[cmd.lay].push(out);
        if(ovl)buckets[cmd.lay].push(ovl);
      }
    }
    var svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="'+vbX.toFixed(6)+' '+vbY.toFixed(6)+' '+vbW.toFixed(6)+' '+vbH.toFixed(6)+
      '" font-family="system-ui,sans-serif" color="#000000">\n'+
      // __acad3dV63: empty string in technical mode and whenever no pattern was used, so a
      // drawing that uses no hatch is byte-identical to its pre-Phase-53 output.
      patReg.defs()+
      '<rect x="'+vbX.toFixed(6)+'" y="'+vbY.toFixed(6)+'" width="'+vbW.toFixed(6)+'" height="'+vbH.toFixed(6)+'" fill="#ffffff"/>\n'+
      '<g fill="none" stroke="#000000" stroke-width="'+strokeW.toFixed(6)+'">\n'+
      (roomFillOut.length?'<g id="presentation-room-fills">\n'+roomFillOut.join('\n')+'\n</g>\n':'');
    for(i=0;i<order.length;i++){
      svg+='<g id="layer-'+bimEscXml(order[i])+'" data-layer="'+bimEscXml(order[i])+'">\n'+buckets[order[i]].join('\n')+'\n</g>\n';
    }
    svg+='</g>\n</svg>\n';
    return {text:svg,stats:stats};
  }
  function bimExportSVG(){
    try{
      var res=bimBuildSVG(A3D.presentMode?'presentation':'technical');
      if(!res.stats.polyline&&!res.stats.line&&!res.stats.text){a3dToast('Nothing with a 2D footprint to export');return;}
      bimTriggerDownload(res.text,bimFileStem()+'-plan.svg','image/svg+xml');
      a3dToast('Exported '+bimFileStem()+'-plan.svg ('+res.stats.polyline+' path(s), '+res.stats.line+' line(s), '+res.stats.text+' text'+(res.stats.skipped?'; '+res.stats.skipped+' object(s) had no 2D footprint':'')+')');
    }catch(eS){console.warn('[BIM] SVG export failed: ',eS);a3dToast('SVG export failed: '+(eS&&eS.message?eS.message:eS));}
  }
