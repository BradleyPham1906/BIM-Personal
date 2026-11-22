import { bimTriggerDownload } from '../annotation/annotation-pick.js';
import { bimFileStem } from './project-file.js';
import { bimBuildDXF } from './export-mappings.js';
import { bimLbBase } from '../ladybug/runtime.js';
import { dxfEllipsePts, dxfExpandInserts, dxfSplinePts, dxfTextPlain, dxfXform } from './dxf-entities.js';
import { DXF_UNIT_SCALE, bimImportParsed, dxfAciToHex, dxfParse } from './import-dxf.js';
import { a3dToast } from '../bim/csg-booleans.js';

  /* ================= __acad3dV252: DWG open and save, through cc-dwg =================
     The owner's approval, 2026-11-22: "yes". cc-dwg is BimCraft's own DWG library (Apache-2.0,
     docs/research/research-dwg-library.md), pinned at runtime/cc-dwg/<rev>/ and loaded only when a DWG is opened or
     saved (tools/dwg/build_dwg.mjs). It reads R13 to R2018 and writes R2000 to R2018.

     This file is the only one that calls it. OPEN: the library's model is turned into the entity list the DXF
     reader makes (import-dxf.js), so a DWG brings in what a DXF does -- layers, blocks, dimensions, text, arcs,
     ellipses, splines, hatches' boundaries -- through the same code. SAVE: the plan is written as the DXF export
     writes it (bimBuildDXF), read back by the same DXF reader, and handed to the library's writer, so a DWG carries
     exactly what the DXF does. */
  var BIM_DWG={rev:'e36a94d',file:'cc-dwg/e36a94d/bim-dwg.min.js',sri:'sha256-eXuvbnF1EY5eH8fbSGH0oX8BJErk8X//c5p2qzt5fAk=',
    saveVersion:'AC1027'};
  var A3D_DWG={load:null,st:'',err:''};
  function bimDwgLoad(){
    var R=A3D_DWG;
    if(R.load)return R.load;
    var p=String(window.location&&window.location.protocol||''),src=[],i=0;
    if(p!=='http:'&&p!=='https:')src.push({u:'runtime/'+BIM_DWG.file,sri:false});
    src.push({u:String(bimLbBase())+BIM_DWG.file,sri:true});
    R.st='loading';
    R.load=new Promise(function(res,rej){
      if(window.BIMDWG&&window.BIMDWG.readDwg){res(window.BIMDWG);return;}
      function next(){
        if(i>=src.length){rej(new Error('the DWG library could not be loaded from '+src.map(function(s){return s.u;}).join(' or ')));return;}
        var s=src[i++],tag=document.createElement('script');
        tag.src=s.u;
        if(s.sri){tag.integrity=BIM_DWG.sri;tag.crossOrigin='anonymous';}
        tag.onload=function(){if(window.BIMDWG&&window.BIMDWG.readDwg)res(window.BIMDWG);else next();};
        tag.onerror=function(){if(tag.parentNode)tag.parentNode.removeChild(tag);next();};
        document.head.appendChild(tag);
      }
      next();
    }).then(function(D){R.st='ready';return D;},function(e){R.st='failed';R.err=String(e&&e.message||e);R.load=null;throw e;});
    return R.load;
  }
  /* A cc-dwg colour as the DXF reader's: an AutoCAD index (1..255), a hex string for a true colour, null for ByLayer. */
  function bimDwgColor(c){
    if(!c)return null;
    if(typeof c.rgb==='number')return '#'+('000000'+(c.rgb&0xffffff).toString(16)).slice(-6);
    if(c.index>=1&&c.index<=255)return c.index;
    return null;
  }
  function bimDwgPt(p){return [p&&p.x||0,p&&p.y||0,p&&p.z||0];}
  /* One cc-dwg entity as the DXF reader's, or null (angles: radians there, degrees here, as DXF stores them). */
  function bimDwgEntity(e){
    var L=e.layer||'0',C=bimDwgColor(e.color),o=null,k,D=180/Math.PI;
    if(e.invisible)return null;
    var t=e.type;
    if(t==='LINE')o={type:'LINE',p1:bimDwgPt(e.start),p2:bimDwgPt(e.end)};
    else if(t==='CIRCLE')o={type:'CIRCLE',c:bimDwgPt(e.center),r:e.radius};
    else if(t==='ARC')o={type:'ARC',c:bimDwgPt(e.center),r:e.radius,a1:e.startAngle*D,a2:e.endAngle*D};
    else if(t==='LWPOLYLINE'||t==='POLYLINE_2D'){
      var vs=e.vertices||[],pts=[],bl=[],any=false;
      for(k=0;k<vs.length;k++){pts.push([vs[k].x,vs[k].y]);bl.push(vs[k].bulge||0);if(vs[k].bulge)any=true;}
      if(pts.length>=2)o={type:'LWPOLYLINE',closed:!!e.closed,pts:pts,bulges:any?bl:null};
    }else if(t==='POLYLINE_3D'){
      var v3=(e.vertices||[]).map(function(v){return [v.x,v.y];});
      if(v3.length>=2)o={type:'POLYPTS',pts:v3,closed:!!e.closed};
    }else if(t==='ELLIPSE'){
      var el=dxfEllipsePts([e.center.x,e.center.y],[e.majorAxis.x,e.majorAxis.y],e.ratio,e.startParam,e.endParam);
      o={type:'POLYPTS',pts:el.pts,closed:el.closed,z:e.center.z||0};
    }else if(t==='SPLINE'){
      var ctrl=(e.control||[]).map(function(q){return [q.x,q.y];}),fit=(e.fit||[]).map(function(q){return [q.x,q.y];});
      var sp=dxfSplinePts(e.degree,ctrl,e.knots||[],e.weights||null,fit);
      if(sp.length>=2)o={type:'POLYPTS',pts:sp,closed:!!e.closed};
    }else if(t==='TEXT'||t==='ATTRIB'){
      o={type:'TEXT',text:dxfTextPlain(e.value),p:bimDwgPt(e.insert),h:e.height||0,rot:(e.rotation||0)*D};
    }else if(t==='MTEXT'){
      o={type:'TEXT',text:dxfTextPlain(e.value),p:bimDwgPt(e.insert),h:e.height||0,
        rot:e.xAxis?Math.atan2(e.xAxis.y,e.xAxis.x)*D:0};
    }else if(t==='INSERT'||t==='MINSERT'){
      o={type:'INSERT',name:e.block,at:[e.insert.x,e.insert.y],sx:e.scale?e.scale.x:1,sy:e.scale?e.scale.y:1,rot:(e.rotation||0)*D,
        cols:e.cols||1,rows:e.rows||1,colSp:e.colSpacing||0,rowSp:e.rowSpacing||0};
    }else if(/DIMENSION/.test(t)||t==='ACAD_TABLE'){
      if(e.block)o={type:'INSERT',name:e.block,at:[0,0],sx:1,sy:1,rot:0};
    }else if(t==='SOLID'||t==='TRACE'){
      var q=(e.points||[]).map(function(p){return [p.x,p.y];});
      if(q.length===4){q=[q[0],q[1],q[3],q[2]];if(Math.abs(q[2][0]-q[3][0])<1e-12&&Math.abs(q[2][1]-q[3][1])<1e-12)q.pop();}
      if(q.length>=3)o={type:'POLYPTS',pts:q,closed:true};
    }else if(t==='3DFACE'){
      o={type:'3DFACE',pts:(e.points||[]).map(bimDwgPt)};
    }else if(t==='POINT'){
      o={type:'POINT',p:bimDwgPt(e.position)};
    }else if(t==='HATCH'){
      return bimDwgHatchLoops(e,L,C);
    }
    if(!o)return null;
    o.layer=L;o.color=C;
    /* an entity whose plane faces down (extrusion 0,0,-1, how a mirrored copy is often stored) is mirrored in x */
    if(e.extrusion&&e.extrusion.z<0&&o.type!=='INSERT'&&o.type!=='3DFACE')o=dxfXform(o,{at:[0,0],sx:-1,sy:1,rot:0},[0,0]);
    return o;
  }
  /* A hatch's boundaries, as outlines: polyline loops as they are, edge loops of lines, arcs and ellipses as points. */
  function bimDwgHatchLoops(e,L,C){
    var out=[],i,j;
    for(i=0;i<(e.loops||[]).length;i++){
      var lp=e.loops[i];
      if(lp.polyline&&lp.polyline.vertices&&lp.polyline.vertices.length>=2){
        var vs=lp.polyline.vertices;
        out.push({type:'LWPOLYLINE',closed:true,layer:L,color:C,pts:vs.map(function(v){return [v.x,v.y];}),
          bulges:lp.polyline.hasBulges?vs.map(function(v){return v.bulge||0;}):null});
        continue;
      }
      var pts=[];
      for(j=0;j<(lp.edges||[]).length;j++){
        var g=lp.edges[j],seg=[];
        if(g.type==='line')seg=[[g.start.x,g.start.y],[g.end.x,g.end.y]];
        else if(g.type==='arc'){
          var a0=g.startAngle,a1=g.endAngle,n=16,s;
          if(g.ccw===false){a0=-g.startAngle;a1=-g.endAngle;}
          if(a1<a0&&g.ccw!==false)a1+=Math.PI*2;
          for(s=0;s<=n;s++){var a=a0+(a1-a0)*s/n;seg.push([g.center.x+Math.cos(a)*g.radius,g.center.y+Math.sin(a)*g.radius]);}
        }else if(g.type==='ellipse'){
          seg=dxfEllipsePts([g.center.x,g.center.y],[g.majorAxis.x,g.majorAxis.y],g.ratio,g.startAngle,g.endAngle,16).pts;
        }else if(g.type==='spline'){
          seg=dxfSplinePts(g.degree,(g.control||[]).map(function(q){return [q.x,q.y];}),g.knots||[],g.weights||null,
            (g.fit||[]).map(function(q){return [q.x,q.y];}));
        }
        for(var k=0;k<seg.length;k++){
          var last=pts[pts.length-1];
          if(!last||Math.abs(last[0]-seg[k][0])>1e-9||Math.abs(last[1]-seg[k][1])>1e-9)pts.push(seg[k]);
        }
      }
      if(pts.length>=3)out.push({type:'POLYPTS',pts:pts,closed:true,layer:L,color:C});
    }
    return out.length?out:null;
  }
  /* The library's model as the DXF reader's result: layers, the model space with every block expanded, the units. */
  function bimDwgToParsed(m){
    var layers={},blocks={},ents=[],skipped={},i,j,b,ms=null;
    var tl=(m.tables&&m.tables.layers)||[];
    for(i=0;i<tl.length;i++){
      var ly=tl[i],c=bimDwgColor(ly.color);
      layers[ly.name]={name:ly.name,color:typeof c==='string'?c:dxfAciToHex(c||7),off:!!ly.off,frozen:!!ly.frozen,locked:!!ly.locked,
        linetype:ly.linetypeName||'CONTINUOUS',lineweight:ly.lineweight>=0?ly.lineweight/100:null,plot:ly.plot!==false};
    }
    function conv(list){
      var out=[],k,r;
      for(k=0;k<list.length;k++){
        r=bimDwgEntity(list[k]);
        /* an ATTDEF is the block's template for an attribute: AutoCAD never draws it in an insert, the ATTRIB is drawn */
        if(!r){if(!list[k].invisible&&list[k].type!=='ATTDEF')skipped[list[k].type]=(skipped[list[k].type]||0)+1;continue;}
        if(r.length!==undefined)out=out.concat(r);else out.push(r);
        /* an insert's attributes are drawn where they are, in world coordinates */
        if(list[k].attribs)for(j=0;j<list[k].attribs.length;j++){var at=bimDwgEntity(list[k].attribs[j]);if(at)out.push(at);}
      }
      return out;
    }
    for(i=0;i<(m.blocks||[]).length;i++){
      b=m.blocks[i];
      if(b.name==='*Model_Space'){ms=b;continue;}
      if(/^\*Paper_Space/i.test(b.name))continue;
      blocks[b.name]={name:b.name,base:[b.base?b.base.x:0,b.base?b.base.y:0],ents:conv(b.entities||[])};
    }
    if(ms)ents=conv(ms.entities||[]);
    var nIns=ents.filter(function(e){return e.type==='INSERT';}).length;
    var iu=m.header&&typeof m.header.INSUNITS==='number'?m.header.INSUNITS:null;
    return {layers:layers,entities:dxfExpandInserts(ents,blocks,0),blocks:Object.keys(blocks).length,inserts:nIns,
      skipped:skipped,scale:DXF_UNIT_SCALE[iu]||1,insUnits:iu,version:m.version};
  }
  function bimImportDWG(buf,name){
    a3dToast('Opening '+name+'...');
    return bimDwgLoad().then(function(D){
      var m=D.readDwg(new Uint8Array(buf));
      if(m.report&&m.report.error){a3dToast('DWG import failed: '+m.report.error);return null;}
      var res=bimDwgToParsed(m);
      bimImportParsed(res,name,'DWG '+((D.VERSIONS&&D.VERSIONS[m.version])||m.version||''));
      return res;
    }).catch(function(e){
      console.warn('[BIM] DWG import failed:',e);
      a3dToast('DWG import failed: '+(e&&e.message||e));
      return null;
    });
  }
  /* ---------- save ---------- */
  /* The DXF reader's result as a cc-dwg model: the layers and model space the writer takes (model.js's shape). */
  function bimDwgModelFrom(res,version){
    var layers=[],ents=[],k,i,e,D=Math.PI/180;
    function col(c){return typeof c==='number'&&c>=1&&c<=255?{index:c}:{index:256};}
    for(k in res.layers)if(res.layers.hasOwnProperty(k)){
      var l=res.layers[k],rgb=parseInt(String(l.color||'#ffffff').slice(1),16);
      layers.push({name:l.name,color:{rgb:rgb},off:!!l.off,frozen:!!l.frozen,locked:!!l.locked,plot:l.plot!==false,
        linetypeName:'Continuous',lineweight:l.lineweight!=null?Math.round(l.lineweight*100):-3});
    }
    var base={linetype:'ByLayer',lineweight:-1,ltscale:1,invisible:false,extrusion:{x:0,y:0,z:1}};
    function mk(o,e){var q;for(q in base)if(base.hasOwnProperty(q))o[q]=base[q];o.layer=e.layer||'0';o.color=col(e.color);return o;}
    function P(p){return {x:p[0],y:p[1],z:p[2]||0};}
    for(i=0;i<res.entities.length;i++){
      e=res.entities[i];
      if(e.type==='LINE')ents.push(mk({type:'LINE',start:P(e.p1),end:P(e.p2),thickness:0},e));
      else if(e.type==='LWPOLYLINE'||e.type==='POLYLINE'||e.type==='POLYPTS')
        ents.push(mk({type:'LWPOLYLINE',closed:!!e.closed,constantWidth:0,elevation:0,thickness:0,flags:0,plinegen:false,
          vertices:e.pts.map(function(p,j){return {x:p[0],y:p[1],bulge:e.bulges?(e.bulges[j]||0):0,startWidth:0,endWidth:0};})},e));
      else if(e.type==='CIRCLE')ents.push(mk({type:'CIRCLE',center:P(e.c),radius:e.r,thickness:0},e));
      else if(e.type==='ARC')ents.push(mk({type:'ARC',center:P(e.c),radius:e.r,startAngle:e.a1*D,endAngle:e.a2*D,thickness:0},e));
      else if(e.type==='TEXT')ents.push(mk({type:'TEXT',insert:P(e.p),align:P(e.p),height:e.h||0.25,value:e.text,rotation:(e.rot||0)*D,
        widthFactor:1,oblique:0,style:'Standard',hAlign:0,vAlign:0,generation:0,thickness:0,elevation:0},e));
      else if(e.type==='3DFACE')ents.push(mk({type:'3DFACE',points:e.pts.map(P),invisibleEdges:0},e));
      else if(e.type==='POINT')ents.push(mk({type:'POINT',position:P(e.p),thickness:0,xAxisAngle:0},e));
    }
    return {version:version||BIM_DWG.saveVersion,header:{INSUNITS:res.insUnits!=null?res.insUnits:6},
      tables:{layers:layers},blocks:[{name:'*Model_Space',base:{x:0,y:0,z:0},flags:0,xrefPath:'',description:'',entities:ents}]};
  }
  function bimExportDWG(version){
    var built;
    try{built=bimBuildDXF();}catch(eB){a3dToast('DWG export failed: '+(eB&&eB.message||eB));return Promise.resolve(null);}
    if(!built.stats.lwpolyline&&!built.stats.line&&!built.stats.text){a3dToast('Nothing with a 2D footprint to export');return Promise.resolve(null);}
    return bimDwgLoad().then(function(D){
      var model=bimDwgModelFrom(dxfParse(built.text),version);
      var w=D.writeDwg(model,{version:model.version});
      var nm=bimFileStem()+'-plan.dwg';
      bimTriggerDownload(w.bytes,nm,'application/acad');
      a3dToast('Exported '+nm+' (AutoCAD '+(D.VERSIONS[model.version]||model.version)+', '+model.blocks[0].entities.length+' entities)');
      return w;
    }).catch(function(e){
      console.warn('[BIM] DWG export failed:',e);
      a3dToast('DWG export failed: '+(e&&e.message||e));
      return null;
    });
  }
export { bimExportDWG, bimImportDWG };
