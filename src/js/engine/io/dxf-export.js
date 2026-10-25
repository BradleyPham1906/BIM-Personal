  // ---- __acad3dV24: DXF export + Ceiling tool ----
  // DXF export writes standard ASCII DXF (HEADER/TABLES/ENTITIES). Only the 2D plan footprint of
  // each object is exported -- walls as centerline + inner/outer loops, rooms/floors/roofs as
  // outlines, columns as rectangles, dims as line+text, text as TEXT. Openings have no 2D
  // footprint of their own and are counted as skipped rather than silently dropped.
  // Verified by round-tripping the output through this app's OWN dxfParse: layers, polylines,
  // vertex coordinates, closed flags and $INSUNITS all survive. TEXT entities are written
  // correctly for other CAD apps but come back as "skipped" here, since this app's importer has
  // never supported TEXT (LINE/CIRCLE/ARC/LWPOLYLINE/POLYLINE/3DFACE/POINT only) -- that's an
  // importer limitation, not an export defect, and the export is standard-conformant.
  function bimDxfPair(code,val){return code+'\r\n'+val+'\r\n';}
  function bimDxfLayerName(raw){
    return String(raw||'0').replace(/[<>\/\\":;?*|=`,]/g,'_').replace(/\s+/g,'_').slice(0,255)||'0';
  }
  /* __acad3dV58: shared opening-cut geometry for every vector plan path (DXF, SVG, sheet vector).
     See the patch script header (phase50c_patch.py) for the full derivation and the winding-
     correctness argument (bp = sketchCCW(centerline), not centerline itself). */
  function bimWallOpeningBreaks(wall){
    if(!wall||!wall.bim||!wall.bim.innerLoop||!wall.bim.outerLoop||!wall.bim.centerline)return null;
    var cl=wall.bim.centerline;
    var bp=sketchCCW(cl);
    var n=bp.length;
    var outerLoop=wall.bim.outerLoop,innerLoop=wall.bim.innerLoop;
    if(n<2||outerLoop.length!==n||innerLoop.length!==n)return null;
    var segCount=n;
    var off=bimAlignOffsets(wall.bim.thickness,wall.bim.align||'center');
    var bySeg={},any=false,i,oi;
    for(oi=0;oi<A3D.objs.length;oi++){
      var o=A3D.objs[oi];
      if(o.t!=='opening'||!o.bim||o.bim.hostWallId!==wall.id||!o.bim.center)continue;
      var best=null;
      for(i=0;i<segCount;i++){
        var a=bp[i],bb=bp[(i+1)%n];
        var dx=bb[0]-a[0],dz=bb[1]-a[1],len2=dx*dx+dz*dz;
        var t=len2>1e-9?(((o.bim.center[0]-a[0])*dx+(o.bim.center[1]-a[1])*dz)/len2):0;
        t=Math.max(0.08,Math.min(0.92,t));
        var cx=a[0]+t*dx,cz=a[1]+t*dz;
        var ddx=o.bim.center[0]-cx,ddz=o.bim.center[1]-cz,d=Math.sqrt(ddx*ddx+ddz*ddz);
        if(!best||d<best.d)best={idx:i,a:a,b:bb,t:t,center:[cx,cz],d:d};
      }
      if(!best)continue;
      var dx2=best.b[0]-best.a[0],dz2=best.b[1]-best.a[1],len=Math.sqrt(dx2*dx2+dz2*dz2)||1;
      var dir=[dx2/len,dz2/len],nx=-dir[1],nz=dir[0];
      var hw=(o.bim.width||0)/2,c=best.center;
      var j1=[c[0]-dir[0]*hw,c[1]-dir[1]*hw],j2=[c[0]+dir[0]*hw,c[1]+dir[1]*hw];
      var rec={
        t:best.t,
        outerA:[j1[0]-nx*off.dRight,j1[1]-nz*off.dRight],
        outerB:[j2[0]-nx*off.dRight,j2[1]-nz*off.dRight],
        innerA:[j1[0]+nx*off.dLeft,j1[1]+nz*off.dLeft],
        innerB:[j2[0]+nx*off.dLeft,j2[1]+nz*off.dLeft],
        type:o.bim.type,objId:o.id
      };
      if(!bySeg[best.idx])bySeg[best.idx]=[];
      bySeg[best.idx].push(rec);
      any=true;
    }
    if(!any){
      return {outerRuns:[outerLoop.slice()],innerRuns:[innerLoop.slice()],outerClosed:true,innerClosed:true,jambs:[],glaze:[]};
    }
    var segIdxKey;
    for(segIdxKey in bySeg){
      if(bySeg.hasOwnProperty(segIdxKey))bySeg[segIdxKey].sort(function(p,q){return p.t-q.t;});
    }
    var startSeg=0;
    for(i=0;i<segCount;i++){if(bySeg[i]){startSeg=i;break;}}
    function walk(ring,side){
      var strokes=[[]];
      var idx=startSeg,count=0;
      strokes[0].push(ring[idx]);
      while(count<segCount){
        var list=bySeg[idx]||[],k;
        for(k=0;k<list.length;k++){
          var rec=list[k];
          strokes[strokes.length-1].push(side==='outer'?rec.outerA:rec.innerA);
          strokes.push([side==='outer'?rec.outerB:rec.innerB]);
        }
        idx=(idx+1)%n;
        strokes[strokes.length-1].push(ring[idx]);
        count++;
      }
      if(strokes.length>1){
        var first=strokes[0],last=strokes[strokes.length-1];
        var merged=last.concat(first.slice(1));
        strokes=[merged].concat(strokes.slice(1,strokes.length-1));
      }
      return strokes;
    }
    var jambs=[],glaze=[];
    for(i=0;i<segCount;i++){
      var list=bySeg[i];
      if(!list)continue;
      var k;
      for(k=0;k<list.length;k++){
        jambs.push([list[k].outerA,list[k].innerA,list[k].objId]);
        jambs.push([list[k].outerB,list[k].innerB,list[k].objId]);
        if(list[k].type==='window'){
          var mA=[(list[k].outerA[0]+list[k].innerA[0])/2,(list[k].outerA[1]+list[k].innerA[1])/2];
          var mB=[(list[k].outerB[0]+list[k].innerB[0])/2,(list[k].outerB[1]+list[k].innerB[1])/2];
          glaze.push([mA,mB,list[k].objId]);
        }
      }
    }
    return {outerRuns:walk(outerLoop,'outer'),innerRuns:walk(innerLoop,'inner'),outerClosed:false,innerClosed:false,jambs:jambs,glaze:glaze};
  }
