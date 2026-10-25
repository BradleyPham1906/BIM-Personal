  /* ================= __acad3dV104: the export mappings ================= */
  function bimExportOffset(o){
    if(!o||bimIsProperty(o)||bimIsAlignment(o))return [0,0,0];   /* derived in world terms already; __acad3dV127: so is an alignment */
    return bimObjOffset(o);
  }
  function bimDxfToModel(x,y,s){return [x*(s||1),-y*(s||1)];}
  function bimDxfBulgesToModel(b){return b?b.map(function(v){return -(v||0);}):b;}
  /* __acad3dV121: a layer as a DXF LAYER record. 62 is the nearest of AutoCAD's nine standard colors,
     negative when the layer is off, and 420 the exact color; 70 carries frozen (1) and locked (4);
     6 the linetype; 290 a layer that does not plot; 370 the lineweight in hundredths of a millimetre,
     -3 for Default. A DXF layer has no parent, so a sub-layer is written as its parents leave it. */
  var BIM_DXF_ACI9=[[1,255,0,0],[2,255,255,0],[3,0,255,0],[4,0,255,255],[5,0,0,255],[6,255,0,255],[7,255,255,255],[8,128,128,128],[9,192,192,192]];
  function bimDxfNearestAci(hex){
    var m=/^#([0-9a-fA-F]{2})([0-9a-fA-F]{2})([0-9a-fA-F]{2})$/.exec(hex||''),best=7,bd=Infinity,i,r,g,b,d;
    if(!m)return 7;
    r=parseInt(m[1],16);g=parseInt(m[2],16);b=parseInt(m[3],16);
    for(i=0;i<BIM_DXF_ACI9.length;i++){
      d=Math.pow(r-BIM_DXF_ACI9[i][1],2)+Math.pow(g-BIM_DXF_ACI9[i][2],2)+Math.pow(b-BIM_DXF_ACI9[i][3],2);
      if(d<bd){bd=d;best=BIM_DXF_ACI9[i][0];}
    }
    return best;
  }
  function bimDxfLayerRecord(l){
    var P=bimDxfPair,s=bimLayerEff(l),lt=bimLinetypeDef(l.linetype),aci=bimDxfNearestAci(l.color),out;
    out=P(0,'LAYER')+P(2,bimDxfLayerName(l.name))+P(70,(s.frozen?1:0)|(s.locked?4:0))+P(62,s.on?aci:-aci);
    if(/^#[0-9a-fA-F]{6}$/.test(l.color||''))out+=P(420,parseInt(l.color.slice(1),16));
    out+=P(6,(lt&&lt.pat.length)?lt.name:'CONTINUOUS');
    if(!s.plot)out+=P(290,0);
    out+=P(370,(l.lineweight===null||l.lineweight===undefined||!isFinite(l.lineweight))?-3:Math.round(+l.lineweight*100));
    return out;
  }
  /* The LTYPE table: CONTINUOUS, and every linetype a layer uses, with acadiso.lin's millimetres. In
     this metre drawing a reader sets LTSCALE to suit its plot scale, as with any metric drawing. */
  function bimDxfLtypeTable(layers){
    var P=bimDxfPair,used={},list=[],i,k,lt,tot,out;
    for(i=0;i<layers.length;i++){
      lt=bimLinetypeDef(layers[i].linetype);
      if(lt&&lt.pat.length&&!used[lt.name]){used[lt.name]=1;list.push(lt);}
    }
    out=P(0,'TABLE')+P(2,'LTYPE')+P(70,list.length+1)+
      P(0,'LTYPE')+P(2,'CONTINUOUS')+P(70,0)+P(3,'Solid line')+P(72,65)+P(73,0)+P(40,'0.0');
    for(i=0;i<list.length;i++){
      lt=list[i];tot=0;
      for(k=0;k<lt.pat.length;k++)tot+=Math.abs(lt.pat[k]);
      out+=P(0,'LTYPE')+P(2,lt.name)+P(70,0)+P(3,lt.desc)+P(72,65)+P(73,lt.pat.length)+P(40,tot.toFixed(4));
      for(k=0;k<lt.pat.length;k++)out+=P(49,lt.pat[k].toFixed(4))+P(74,0);
    }
    return out+P(0,'ENDTAB');
  }
  function bimBuildDXF(){
    var P=bimDxfPair,out='',layers=A3D.layers,i;
    out+=P(0,'SECTION')+P(2,'HEADER')+P(9,'$INSUNITS')+P(70,6)+P(0,'ENDSEC');
    out+=P(0,'SECTION')+P(2,'TABLES')+bimDxfLtypeTable(layers)+P(0,'TABLE')+P(2,'LAYER')+P(70,layers.length+1);   /* __acad3dV121 */
    out+=P(0,'LAYER')+P(2,'0')+P(70,0)+P(62,7)+P(6,'CONTINUOUS');
    for(i=0;i<layers.length;i++)out+=bimDxfLayerRecord(layers[i]);   /* __acad3dV121: every layer was white, on and Continuous */
    out+=P(0,'ENDTAB')+P(0,'ENDSEC')+P(0,'SECTION')+P(2,'ENTITIES');
    var stats={lwpolyline:0,line:0,text:0,skipped:0};
    var EX=[0,0,0];   /* __acad3dV104: the current object's offset */
    function DX(p){return (p[0]+EX[0]).toFixed(6);}
    function DY(p){return (-(p[1]+EX[2])).toFixed(6);}   /* north up: DXF +Y is -Z */
    function layerOf(o){
      var k;
      for(k=0;k<layers.length;k++)if(layers[k].id===o.layer)return bimDxfLayerName(layers[k].name);
      return '0';
    }
    /* __acad3dV88: bulges is optional and parallel to pts. Group code 42 follows its vertex,
       which is where the DXF reference puts it, and is omitted entirely when the segment is
       straight - so a polyline with no arcs produces byte-identical output to before. */
    function poly(pts,closed,lay,bulges){
      out+=P(0,'LWPOLYLINE')+P(8,lay)+P(100,'AcDbEntity')+P(100,'AcDbPolyline')+P(90,pts.length)+P(70,closed?1:0);
      var q;
      for(q=0;q<pts.length;q++){
        out+=P(10,DX(pts[q]))+P(20,DY(pts[q]));
        var bq=-bimBulgeAt(bulges,q);   /* __acad3dV104: a reflection reverses every arc */
        if(Math.abs(bq)>BIM_BULGE_EPS)out+=P(42,bq.toFixed(8));
      }
      stats.lwpolyline++;
    }
    function line(a,b,lay){
      out+=P(0,'LINE')+P(8,lay)+P(10,DX(a))+P(20,DY(a))+P(30,'0.0')+P(11,DX(b))+P(21,DY(b))+P(31,'0.0');
      stats.line++;
    }
    function text(pt,str,h,lay){
      out+=P(0,'TEXT')+P(8,lay)+P(10,DX(pt))+P(20,DY(pt))+P(30,'0.0')+P(40,h.toFixed(4))+P(1,String(str).replace(/[\r\n]+/g,' '));
      stats.text++;
    }
    for(i=0;i<A3D.objs.length;i++){
      var o=A3D.objs[i],lay=layerOf(o),b=o.bim;
      EX=bimExportOffset(o);   /* __acad3dV104 */
      if(b&&b.type==='wall'&&b.centerline){
        poly(b.centerline,!!b.closed,lay);
        if(b.innerLoop&&b.outerLoop){
          var brkD=bimWallOpeningBreaks(o);
          if(brkD){
            var bdi;
            for(bdi=0;bdi<brkD.outerRuns.length;bdi++)poly(brkD.outerRuns[bdi],brkD.outerClosed,lay);
            for(bdi=0;bdi<brkD.innerRuns.length;bdi++)poly(brkD.innerRuns[bdi],brkD.innerClosed,lay);
            for(bdi=0;bdi<brkD.jambs.length;bdi++)line(brkD.jambs[bdi][0],brkD.jambs[bdi][1],lay);
            for(bdi=0;bdi<brkD.glaze.length;bdi++)line(brkD.glaze[bdi][0],brkD.glaze[bdi][1],lay);
          }else{
            poly(b.innerLoop,true,lay);
            poly(b.outerLoop,true,lay);
          }
        }
      }else if(o.t==='room'){
        poly(o.pts,true,lay);
        if(!bimRoomTagged(o.id))text(bimRoomLabelPoint(o),bimRoomLabelText(o),0.25,lay);   /* __acad3dV101 */
      }else if(bimIsHatch(o)){                  /* __acad3dV96 */
        /* R12 ASCII has no HATCH entity either -- it arrived in R13, and R12 drawings carry
           hatching as exploded lines. This export writes the BOUNDARY as a closed polyline and
           nothing else, which is true rather than approximate: the region is there, the
           pattern is not. Generating the pattern as clipped LINE entities is real work and is
           its own phase. */
        poly(o.pts,true,lay,o.bulges||null);
        stats.hatch=(stats.hatch||0)+1;
      }else if(bimIsCline(o)){                  /* __acad3dV94 */
        /* R12 ASCII has no XLINE or RAY entity (both arrived in R13), so what goes out is the
           clipped LINE. Stated here rather than silently approximated. */
        var dxCL=bimClineVisibleSeg(o,null);
        if(dxCL)line(dxCL[0],dxCL[1],lay);
      }else if(bimIsPoint(o)){                  /* __acad3dV93 */
        var dxPM=bimPointMarkerSegs(o.pts[0]),dxPK;
        for(dxPK=0;dxPK<dxPM.length;dxPK++)line(dxPM[dxPK][0],dxPM[dxPK][1],lay);
      }else if(o.t==='sketch'&&o.pts&&o.pts.length>=2){
        /* __acad3dV88: DXF carries the arc itself. This is the one consumer that does NOT
           flatten, because the format it writes stores exactly what this app stores. */
        poly(o.pts,o.closed!==false,lay,o.bulges);
      }else if(o.t==='dim'&&bimDimKind(o)==='linear'){
        line(o.d1,o.d2,lay);line(o.p1,o.d1,lay);line(o.p2,o.d2,lay);
        text([(o.d1[0]+o.d2[0])/2,(o.d1[1]+o.d2[1])/2],o.length.toFixed(2),0.2,lay);
      }else if(o.t==='dim'&&bimDimKind(o)==='angular'){
        line(o.vertex,o.ap1,lay);line(o.vertex,o.ap2,lay);
        var arcPts=[],ai;
        for(ai=0;ai<=16;ai++){
          var aa=o.a1+o.sweep*(ai/16);
          arcPts.push([o.vertex[0]+Math.cos(aa)*o.arcRadius,o.vertex[1]+Math.sin(aa)*o.arcRadius]);
        }
        poly(arcPts,false,lay);
        var midA=o.a1+o.sweep/2;
        text([o.vertex[0]+Math.cos(midA)*o.arcRadius*1.25,o.vertex[1]+Math.sin(midA)*o.arcRadius*1.25],o.degrees.toFixed(1)+'deg',0.2,lay);
      }else if(o.t==='dim'&&(bimDimKind(o)==='radius'||bimDimKind(o)==='diameter')){
        var cPts=[],ci2;
        for(ci2=0;ci2<=32;ci2++){
          var cc=(ci2/32)*Math.PI*2;
          cPts.push([o.center[0]+Math.cos(cc)*o.radius,o.center[1]+Math.sin(cc)*o.radius]);
        }
        poly(cPts,true,lay);
        line(o.dStart,o.dEdge,lay);
        text([(o.dStart[0]+o.dEdge[0])/2,(o.dStart[1]+o.dEdge[1])/2],(bimDimKind(o)==='diameter'?'D':'R')+o.value.toFixed(2),0.2,lay);
      }else if(o.t==='dim'&&bimDimKind(o)==='leader'){
        poly([o.anchor,o.elbow,o.landing],false,lay);
        text(o.landing,o.label||'',0.2,lay);
      }else if(bimIsAlignment(o)){   /* __acad3dV127 */
        var axD=bimAlignExport(o),alD;
        poly(axD.pts,false,lay);
        for(alD=0;alD<axD.labels.length;alD++)text(axD.labels[alD].p,axD.labels[alD].t,0.25,lay);
      }else if(bimIsProperty(o)){   /* __acad3dV103: WORLD points; %%d is the R12 degree mark */
        var pgD=bimPropertyGeometry(o),lk;
        poly(pgD.ring,true,lay);
        for(lk=0;lk<o.legs.length&&lk+1<pgD.pts.length;lk++)
          text([(pgD.pts[lk][0]+pgD.pts[lk+1][0])/2,(pgD.pts[lk][1]+pgD.pts[lk+1][1])/2],
               bimFormatBearing(o.legs[lk].az,'%%d')+' '+o.legs[lk].d.toFixed(2),0.25,lay);
      }else if(o.t==='roomtag'){   /* __acad3dV101 */
        if(bimAnnotDrawable(o))text(o.pt,bimRoomTagText(o),0.25,lay);
      }else if(o.t==='text'){
        text(o.pt,o.text,0.25,lay);
      }else if(b&&(b.type==='floor'||b.type==='ceiling'||b.type==='roof')&&(b.profile||b.footprint)){
        poly(b.profile||b.footprint,true,lay);
      }else if(b&&b.type==='column'&&b.center){
        var c=b.center,hw=b.width/2,hd=b.depth/2;
        poly(bimRectFootprint(c,b.width,b.depth,b.rotation||0),true,lay);
      }else if(bimIsFooting(o)&&b.plan){   /* __acad3dV102 */
        var fpi;
        for(fpi=0;fpi<b.plan.length;fpi++)poly(b.plan[fpi],true,lay);
      }else{
        stats.skipped++;
      }
    }
    out+=P(0,'ENDSEC')+P(0,'EOF');
    return {text:out,stats:stats};
  }
  function bimExportDXF(){
    try{
      var res=bimBuildDXF();
      if(!res.stats.lwpolyline&&!res.stats.line&&!res.stats.text){a3dToast('Nothing with a 2D footprint to export');return;}
      bimTriggerDownload(res.text,bimFileStem()+'-plan.dxf','application/dxf');
      a3dToast('Exported '+bimFileStem()+'-plan.dxf ('+res.stats.lwpolyline+' polyline(s), '+res.stats.line+' line(s), '+res.stats.text+' text'+(res.stats.skipped?'; '+res.stats.skipped+' object(s) had no 2D footprint':'')+')');
    }catch(eX){console.warn('[BIM] DXF export failed: ',eX);a3dToast('DXF export failed: '+(eX&&eX.message?eX.message:eX));}
  }
  function bimEscXml(s){
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }
  /* __acad3dV56: real vector plan export, Phase 50. Deliberately mirrors bimBuildDXF's exact
     per-object-type entity walk (same branches, same poly/line/text helper shape) rather than
     screen-projecting the live 3D camera view -- this reads model-space plan coordinates
     directly (wall centerline/loops, room/sketch outlines, all five dim kinds, text, floor/
     ceiling/roof footprints, column footprints), so it is dimensionally correct regardless of
     the current zoom, pan, or camera angle, exactly like the DXF export it is modeled on. Fill
     is intentionally none everywhere (pure linework, matching DXF's own philosophy) -- poche
     and material fills are Phase 52's job. Each emitted element carries a data-obj attribute
     back to its source object's id, something the flat DXF entity list cannot do. */
  /* __acad3dV63 (Phase 53): the vector pattern sink, shared by both SVG writers.

     Same definition table as the Canvas2D tiles (BIM_PATTERN_DEFS), so a drawing exported to SVG
     carries the hatch the screen showed rather than a second, separately-maintained rendition of
     it. What differs between the two writers is only how many user units make a millimetre --
     exactly the same asymmetry the two writers already have for lineWeight, and for the same
     reason: bimBuildSVG works in model metres with a fit-to-content viewBox, while
     bimBuildPlanViewportSVG works in real sheet-page millimetres. Both pass their own
     unitsPerMm in, so neither has to know anything about the other's calibration.

     flipY exists because a writer that negates world Y (bimBuildSVG does, to turn a
     +Y-is-north model plan into +Y-is-down SVG) would otherwise mirror the tile artwork and show
     a '\' where the screen showed a '/'. Flipping the tile's own Y in that writer keeps the
     printed hatch running the same way as the one on screen. */
  // Global so ids stay unique across the several viewport fragments a single sheet export
  // concatenates into one document.
  var BIM_PAT_SVG_SEQ=1;
  function bimPatternSvgDef(id,name,color,unitsPerMm,scale,flipY,angleDeg){
    var def=bimPatternDef(name);
    if(!def)return null;
    var sc=(scale>0)?scale:1;
    var tw=def.mm*(def.w||1)*unitsPerMm*sc,th=def.mm*unitsPerMm*sc;
    if(!(tw>0)||!(th>0))return null;
    var sw=th*0.055;
    function fy(v){return flipY?(1-v):v;}
    var body='',L=def.lines||[],D=def.dots||[],i;
    for(i=0;i<L.length;i++)
      body+='<line x1="'+(L[i][0]*tw).toFixed(6)+'" y1="'+(fy(L[i][1])*th).toFixed(6)+
            '" x2="'+(L[i][2]*tw).toFixed(6)+'" y2="'+(fy(L[i][3])*th).toFixed(6)+
            '" stroke="'+color+'" stroke-width="'+sw.toFixed(6)+'"/>';
    for(i=0;i<D.length;i++)
      body+='<circle cx="'+(D[i][0]*tw).toFixed(6)+'" cy="'+(fy(D[i][1])*th).toFixed(6)+
            '" r="'+(D[i][2]*Math.min(tw,th)).toFixed(6)+'" fill="'+color+'" stroke="none"/>';
    /* __acad3dV96: same rotation function the canvas sink uses, so a drawing on screen and
       the SVG exported from it cannot disagree about which way a hatch runs. */
    var rot=bimPatternRotation(angleDeg,!!flipY);
    var xf=rot?(' patternTransform="rotate('+rot.toFixed(4)+')"'):'';
    return '<pattern id="'+id+'" patternUnits="userSpaceOnUse" width="'+tw.toFixed(6)+
           '" height="'+th.toFixed(6)+'"'+xf+'>'+body+'</pattern>';
  }
  /* One registry per export. Interns each distinct (pattern, colour, scale) once so a plan with
     forty concrete-hatched walls emits one <pattern> and forty references, not forty definitions.
     The id prefix is passed in so a sheet SVG containing several viewport fragments cannot end up
     with two different <pattern> elements sharing an id. */
  function bimPatternRegistry(unitsPerMm,flipY,prefix){
    var defs=[],map={},n=0;
    return {
      resolve:function(rg){
        if(!rg||!bimPatternDraws(rg.pattern))return null;
        var col=rg.patternColor||'#555555';
        if(rg.pattern==='solid')return col;          // a flood needs no <pattern> element
        var sc=(rg.patternScale>0)?rg.patternScale:1;
        /* __acad3dV96: the angle is part of the identity. Without it the first hatch to use a
           pattern would define it and every later one at a different angle would reference that
           same definition -- the angle would be stored, shown in the panel, and ignored. */
        var ang=(typeof rg.patternAngle==='number'&&isFinite(rg.patternAngle))?rg.patternAngle:0;
        var key=rg.pattern+'|'+col+'|'+sc+'|'+ang;
        if(!map[key]){
          var id=prefix+(++n);
          var d=bimPatternSvgDef(id,rg.pattern,col,unitsPerMm,sc,flipY,ang);
          if(!d)return null;
          defs.push(d);map[key]=id;
        }
        return 'url(#'+map[key]+')';
      },
      defs:function(){return defs.length?('<defs>'+defs.join('')+'</defs>'):'';},
      count:function(){return defs.length;}
    };
  }
