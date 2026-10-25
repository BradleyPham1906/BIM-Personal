  // ---- DXF (AutoCAD ASCII exchange format) ----
  var DXF_ACI={1:'#ff5555',2:'#e8d24a',3:'#5ac25a',4:'#4ac6c6',5:'#5a7fe0',6:'#c85ac0',7:'#d8d8d8',8:'#8a8a8a',9:'#bcbcbc'};
  var DXF_UNIT_SCALE={1:0.0254,2:0.3048,4:0.001,5:0.01,6:1,10:0.9144};
  function dxfAciToHex(idx){
    idx=parseInt(idx,10);
    if(!isFinite(idx)||idx<=0)return '#9db4c8';
    return DXF_ACI[idx]||'#9db4c8';
  }
  function dxfTokenize(text){
    var lines=text.split(/\r\n|\r|\n/),pairs=[],i;
    for(i=0;i+1<lines.length;i+=2){
      var codeStr=lines[i];if(codeStr===undefined)break;
      var code=parseInt(codeStr.trim(),10);
      var val=lines[i+1];if(val===undefined)val='';
      val=val.replace(/\r$/,'').trim();
      if(isNaN(code))continue;
      pairs.push([code,val]);
    }
    return pairs;
  }
  function dxfNum(items,code,def){
    var i;for(i=0;i<items.length;i++)if(items[i][0]===code)return parseFloat(items[i][1]);
    return def;
  }
  function dxfAllNums(items,code){
    var out=[],i;for(i=0;i<items.length;i++)if(items[i][0]===code)out.push(parseFloat(items[i][1]));
    return out;
  }
  function dxfStr(items,code,def){
    var i;for(i=0;i<items.length;i++)if(items[i][0]===code)return items[i][1];
    return def;
  }
  function dxfHeaderVar(items,varname,code){
    var j;
    for(j=0;j<items.length-1;j++)if(items[j][0]===9&&items[j][1]===varname&&items[j+1][0]===code)return items[j+1][1];
    return null;
  }
  function dxfParse(text){
    var pairs=dxfTokenize(text);
    var i,rec=null,records=[];
    for(i=0;i<pairs.length;i++){
      var code=pairs[i][0],val=pairs[i][1];
      if(code===0){
        if(rec)records.push(rec);
        rec={type:val,items:[]};
        continue;
      }
      if(rec)rec.items.push([code,val]);
    }
    if(rec)records.push(rec);

    var section=null,inTable=null,insUnits=null;
    var layers={},entities=[],skipped={};
    var curPoly=null;
    var ENTITY_TYPES={LINE:1,CIRCLE:1,ARC:1,LWPOLYLINE:1,POLYLINE:1,VERTEX:1,SEQEND:1,'3DFACE':1,POINT:1};

    for(i=0;i<records.length;i++){
      var r=records[i],t=r.type;
      if(t==='SECTION'){
        section=dxfStr(r.items,2,null);
        if(section==='HEADER'){
          var iu=dxfHeaderVar(r.items,'$INSUNITS',70);
          if(iu!==null)insUnits=parseInt(iu,10);
        }
        continue;
      }
      if(t==='ENDSEC'){section=null;continue;}
      if(t==='TABLE'){inTable=dxfStr(r.items,2,null);continue;}
      if(t==='ENDTAB'){inTable=null;continue;}
      if(t==='EOF')continue;

      if(section==='TABLES'&&inTable==='LAYER'&&t==='LAYER'){
        var nm=dxfStr(r.items,2,'0');
        var col=dxfNum(r.items,62,7),tc=dxfNum(r.items,420,null),lf=dxfNum(r.items,70,0);
        var lwv=dxfNum(r.items,370,-3),plv=dxfNum(r.items,290,1);
        /* __acad3dV121: the layer comes back as it was written -- 420's exact color over 62's standard
           one, 62 negative for a layer that is off, 70 frozen (1) and locked (4), 6, 370 and 290 */
        layers[nm]={name:nm,color:(tc!==null&&isFinite(tc)&&tc>=0)?'#'+('000000'+Math.round(tc).toString(16)).slice(-6):dxfAciToHex(Math.abs(col)),
          off:col<0,frozen:!!(lf&1),locked:!!(lf&4),linetype:dxfStr(r.items,6,'CONTINUOUS'),
          lineweight:(isFinite(lwv)&&lwv>=0)?lwv/100:null,plot:plv!==0};
        continue;
      }
      if(section!=='ENTITIES')continue;

      var layerName=dxfStr(r.items,8,'0');
      var colOverride=dxfNum(r.items,62,null);

      if(t==='POLYLINE'){
        var flags=dxfNum(r.items,70,0);
        curPoly={type:'POLYLINE',closed:!!(flags&1),layer:layerName,color:colOverride,pts:[]};
        continue;
      }
      if(t==='VERTEX'&&curPoly){
        curPoly.pts.push([dxfNum(r.items,10,0),dxfNum(r.items,20,0)]);
        continue;
      }
      if(t==='SEQEND'){
        if(curPoly&&curPoly.pts.length>=2)entities.push(curPoly);
        curPoly=null;
        continue;
      }
      if(!ENTITY_TYPES[t]){
        skipped[t]=(skipped[t]||0)+1;
        continue;
      }
      if(t==='LINE'){
        entities.push({type:'LINE',layer:layerName,color:colOverride,
          p1:[dxfNum(r.items,10,0),dxfNum(r.items,20,0),dxfNum(r.items,30,0)],
          p2:[dxfNum(r.items,11,0),dxfNum(r.items,21,0),dxfNum(r.items,31,0)]});
      }else if(t==='CIRCLE'){
        entities.push({type:'CIRCLE',layer:layerName,color:colOverride,
          c:[dxfNum(r.items,10,0),dxfNum(r.items,20,0),dxfNum(r.items,30,0)],r:dxfNum(r.items,40,1)});
      }else if(t==='ARC'){
        entities.push({type:'ARC',layer:layerName,color:colOverride,
          c:[dxfNum(r.items,10,0),dxfNum(r.items,20,0),dxfNum(r.items,30,0)],r:dxfNum(r.items,40,1),
          a1:dxfNum(r.items,50,0),a2:dxfNum(r.items,51,360)});
      }else if(t==='LWPOLYLINE'){
        var flags2=dxfNum(r.items,70,0);
        var xs=dxfAllNums(r.items,10),ys=dxfAllNums(r.items,20);
        var pts=[],k;for(k=0;k<Math.min(xs.length,ys.length);k++)pts.push([xs[k],ys[k]]);
        /* __acad3dV88: a bulge belongs to the vertex it FOLLOWS, and straight vertices carry no
           42 at all, so the codes cannot be read as a parallel list - they are walked in
           document order alongside the 10s, which is the only reading that survives a file
           where some segments are arcs and some are not. */
        var bulges=null,vi=-1,ri;
        for(ri=0;ri<r.items.length;ri++){
          var code=r.items[ri][0];
          if(code===10)vi++;
          else if(code===42&&vi>=0){
            if(!bulges){bulges=[];for(k=0;k<pts.length;k++)bulges.push(0);}
            if(vi<bulges.length)bulges[vi]=parseFloat(r.items[ri][1])||0;
          }
        }
        if(pts.length>=2)entities.push({type:'LWPOLYLINE',closed:!!(flags2&1),layer:layerName,color:colOverride,pts:pts,bulges:bulges});
      }else if(t==='3DFACE'){
        entities.push({type:'3DFACE',layer:layerName,color:colOverride,pts:[
          [dxfNum(r.items,10,0),dxfNum(r.items,20,0),dxfNum(r.items,30,0)],
          [dxfNum(r.items,11,0),dxfNum(r.items,21,0),dxfNum(r.items,31,0)],
          [dxfNum(r.items,12,0),dxfNum(r.items,22,0),dxfNum(r.items,32,0)],
          [dxfNum(r.items,13,0),dxfNum(r.items,23,0),dxfNum(r.items,33,0)]
        ]});
      }else if(t==='POINT'){
        entities.push({type:'POINT',layer:layerName,color:colOverride,
          p:[dxfNum(r.items,10,0),dxfNum(r.items,20,0),dxfNum(r.items,30,0)]});
      }
    }
    var scale=DXF_UNIT_SCALE[insUnits]||1;
    return {layers:layers,entities:entities,skipped:skipped,scale:scale,insUnits:insUnits};
  }
  function bimDxfApplyLayer(id,dl){
    var ly=bimLayerById(id),lt;
    if(!ly||!dl)return;
    lt=bimLinetypeDef(dl.linetype);
    if(lt)ly.linetype=lt.name;
    if(dl.lineweight!==null&&dl.lineweight!==undefined&&BIM_LINEWEIGHTS.indexOf(dl.lineweight)>=0)ly.lineweight=dl.lineweight;
    if(dl.plot===false)ly.plot=false;
    if(dl.locked)ly.locked=true;
    if(dl.off)ly.visible=false;
    if(dl.frozen&&ly.id!==A3D.activeLayer)ly.frozen=true;
  }
  function bimImportDXF(text,filename){
    var res;
    try{res=dxfParse(text);}
    catch(eP){console.warn('[BIM] DXF parse failed: ',eP);a3dToast('DXF import failed: could not parse '+filename);return;}
    pushUndo();
    undoSuspend=true;
    var __dxfStart=A3D.objs.length;
    var scale,layerMap={},dxfNames,created=0,skippedPoints=0,i;
    try{
      scale=res.scale;dxfNames=Object.keys(res.layers);
      if(!dxfNames.length)dxfNames=['0'];
      var dxfWasCur=A3D.activeLayer,dxfMade={};   /* __acad3dV121 */
      for(i=0;i<dxfNames.length;i++){
        var dl=res.layers[dxfNames[i]];
        if(!bimLayerByName(dxfNames[i]))dxfMade[dxfNames[i]]=1;
        var lyr=addLayer(dxfNames[i],dl?dl.color:'#9db4c8');
        layerMap[dxfNames[i]]=lyr.id;
      }
      /* __acad3dV121: a layer the import made takes the state it was written with; a layer the project
         already had keeps its own, as AutoCAD's does when a drawing brings in a layer it has. The
         current layer goes back to the one it was, since addLayer made each current in turn and a
         frozen layer cannot be current. */
      if(bimLayerById(dxfWasCur))A3D.activeLayer=dxfWasCur;
      for(i=0;i<dxfNames.length;i++)if(dxfMade[dxfNames[i]])bimDxfApplyLayer(layerMap[dxfNames[i]],res.layers[dxfNames[i]]);
      var baseY=bimGetActiveLevel().elev;
      for(i=0;i<res.entities.length;i++){
        var e=res.entities[i],lid=layerIdFor(e.layer||'0'),o=null;
        try{
          if(e.type==='LINE'){
            o=bimMakeImportedSketch([bimDxfToModel(e.p1[0],e.p1[1],scale),bimDxfToModel(e.p2[0],e.p2[1],scale)],baseY+(e.p1[2]||0)*scale,false);   /* __acad3dV104 */
          }else if(e.type==='LWPOLYLINE'||e.type==='POLYLINE'){
            var pts=e.pts.map(function(p){return bimDxfToModel(p[0],p[1],scale);});   /* __acad3dV104 */
            /* __acad3dV88: bulge is scale-invariant (it is tan of a quarter of the swept
               angle), so it is carried across unscaled while the points are scaled. */
            o=bimMakeImportedSketch(pts,baseY,!!e.closed,bimDxfBulgesToModel(e.bulges));
          }else if(e.type==='CIRCLE'){
            var cpts=[],k,n=24;
            for(k=0;k<n;k++){var an=k/n*Math.PI*2;cpts.push(bimDxfToModel(e.c[0]+Math.cos(an)*e.r,e.c[1]+Math.sin(an)*e.r,scale));}
            o=bimMakeImportedSketch(cpts,baseY+(e.c[2]||0)*scale,true);
          }else if(e.type==='ARC'){
            /* __acad3dV88: an ARC is now STORED as an arc - two vertices and one bulge -
               instead of being tessellated into a fan of chords on the way in. DXF arcs are
               always counter-clockwise from a1 to a2, so the sweep is positive by definition
               and the bulge is tan(sweep/4). Before this phase an imported arc could never
               leave this app as an arc again. */
            var a1=e.a1*Math.PI/180,a2=e.a2*Math.PI/180;
            if(a2<a1)a2+=Math.PI*2;
            var sweep=a2-a1;
            var ap1=bimDxfToModel(e.c[0]+Math.cos(a1)*e.r,e.c[1]+Math.sin(a1)*e.r,scale);
            var ap2=bimDxfToModel(e.c[0]+Math.cos(a2)*e.r,e.c[1]+Math.sin(a2)*e.r,scale);
            /* __acad3dV104: counter-clockwise in DXF is clockwise in the model -- the bulge flips */
            o=bimMakeImportedSketch([ap1,ap2],baseY+(e.c[2]||0)*scale,false,[-Math.tan(sweep/4),0]);
          }else if(e.type==='3DFACE'){
            o=bimMakeImportedFace(e.pts,scale,baseY);
          }else if(e.type==='POINT'){
            skippedPoints++;
          }
        }catch(eE){
          console.warn('[BIM] Failed to import a '+e.type+' entity: ',eE);
        }
        if(o){if(e.color!==null&&e.color!==undefined)o.col=dxfAciToHex(e.color);o.layer=lid;created++;}
      }
    }finally{
      var __dxfI;for(__dxfI=__dxfStart;__dxfI<A3D.objs.length;__dxfI++)A3D.objs[__dxfI].locked=true;
      undoSuspend=false;
    }
    function layerIdFor(nm){
      if(layerMap[nm])return layerMap[nm];
      var lyr=addLayer(nm||'0','#9db4c8');
      layerMap[nm]=lyr.id;
      return lyr.id;
    }
    refreshTree();refreshLayers();fitScene();paint();saveSoon();
    var skipMsg=Object.keys(res.skipped).map(function(k){return res.skipped[k]+' '+k;}).join(', ');
    a3dToast('DXF import: '+created+' entities on '+dxfNames.length+' layer(s)'+
      (skipMsg?'; skipped (unsupported): '+skipMsg:'')+
      (skippedPoints?'; '+skippedPoints+' POINT entities not rendered':'')+
      (res.insUnits===null?' (no units in file, assumed meters)':''));
  }

