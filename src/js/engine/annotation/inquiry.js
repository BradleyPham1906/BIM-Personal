import { A3D, el } from '../core/state.js';
import { bimEnterDraftingMode, bimObjOffset } from '../drawing/plan-mode-sketch.js';
import { bimGetActiveLevel } from '../bim/levels-walls-floors.js';
import { bimIsLocked } from '../bim/import-compliance.js';
import { bimDimKind } from './dimensions.js';
import { bimLayerById } from '../layers/layer-rules.js';
import { bimEsc } from '../layers/layer-manager.js';
import { bimTrimNum, bimUnitDef, bimUnitDp } from '../properties/palette.js';
import { paint } from '../map/terrain-3d.js';
import { bimFmtLen } from '../gizmo/gizmo-handles.js';
import { bimBulgedArea, bimBulgedLength, bimHasBulge } from '../drawing/arc-storage.js';
import { closeDlg } from '../ui/touch-input.js';
import { a3dToast, objById } from '../bim/csg-booleans.js';

  /* ================= __acad3dV255: AutoCAD's inquiry commands (D8) =================
     ID, DIST (DI), AREA (AA) and LIST (LI), by AutoCAD's names: they measure and leave nothing in the drawing, unlike
     a dimension (FreeCAD's Measure does the same; docs/research/research-cadcraft-gap.md). Points are picked with the
     running object snaps; the answer opens in a read-out that stays until it is closed, so a value can be copied.
     X and Y are the plan's as the status bar shows them, Z the active level's elevation.
     The arithmetic is pure (bimInquiryDist, bimInquiryArea, bimListRows), tested without a canvas. */
  function bimInquiryDist(a,b){
    var dx=b[0]-a[0],dy=b[1]-a[1],d=Math.sqrt(dx*dx+dy*dy),ang=Math.atan2(dy,dx)*180/Math.PI;
    if(ang<0)ang+=360;
    return {d:d,dx:dx,dy:dy,angle:ang};
  }
  /* The area and perimeter of a closed run of points (bulges optional: arcs count as arcs). */
  function bimInquiryArea(pts,bulges){
    if(!pts||pts.length<3)return null;
    return {area:bimBulgedArea(pts,bulges||null,true),perimeter:bimBulgedLength(pts,bulges||null,true)};
  }
  /* What LIST says of one object: [label, value] rows. */
  function bimListRows(o){
    var rows=[['Name',o.name||o.id],['Type',bimListType(o)]],q=bimObjOffset(o),ly=bimLayerById(o.layer);
    rows.push(['Layer',ly?ly.name:(o.layer||'0')]);
    if(o.col)rows.push(['Color',o.col]);
    if(o.t==='sketch'&&o.pts){
      var closed=o.closed!==false&&(o.pts.length>2||bimHasBulge(o.bulges));   /* a circle is two points and two arcs */
      rows.push(['Vertices',String(o.pts.length)]);
      rows.push([closed?'Perimeter':'Length',bimFmtLen(bimBulgedLength(o.pts,o.bulges||null,closed))]);
      if(closed)rows.push(['Area',bimFmtArea(bimBulgedArea(o.pts,o.bulges||null,true))]);
      if(o.pts.length===2&&!bimHasBulge(o.bulges)){
        var D=bimInquiryDist(o.pts[0],o.pts[1]);
        rows.push(['Angle in plan',D.angle.toFixed(2)+'\u00b0']);
      }
      rows.push(['From',bimListPt([o.pts[0][0]+q[0],o.pts[0][1]+q[2]],(o.y||0)+q[1])]);
    }else if(o.t==='room'&&o.pts){
      rows.push(['Area',bimFmtArea(bimBulgedArea(o.pts,null,true))]);
      rows.push(['Perimeter',bimFmtLen(bimBulgedLength(o.pts,null,true))]);
    }else if(o.t==='text'){
      rows.push(['Text',String(o.text)]);
      if(o.height>0)rows.push(['Height',bimFmtLen(o.height)]);
      if(o.rot)rows.push(['Rotation',(+o.rot).toFixed(2)+'\u00b0']);
      rows.push(['Insertion point',bimListPt([o.pt[0]+q[0],o.pt[1]+q[2]],(o.y||0)+q[1])]);
    }else if(o.t==='dim'){
      rows.push(['Kind',bimDimKind(o)]);
      if(typeof o.length==='number')rows.push(['Measurement',bimFmtLen(o.length)]);
      if(typeof o.value==='number')rows.push(['Measurement',bimFmtLen(o.value)]);
      if(typeof o.degrees==='number')rows.push(['Measurement',o.degrees.toFixed(2)+'\u00b0']);
    }else if(o.bim&&o.bim.type==='wall'){
      var cl=o.bim.centerline||[];
      rows.push(['Length',bimFmtLen(bimBulgedLength(cl,o.bim.bulges||null,!!o.bim.closed))]);
      rows.push(['Thickness',bimFmtLen(o.bim.thickness||0)]);
      rows.push(['Height',bimFmtLen(o.bim.height||0)]);
    }else if(o.bim&&(o.bim.type==='floor'||o.bim.type==='ceiling'||o.bim.type==='roof')&&(o.bim.profile||o.bim.footprint)){
      var pf=o.bim.profile||o.bim.footprint;
      rows.push(['Area',bimFmtArea(bimBulgedArea(pf,null,true))]);
      rows.push(['Perimeter',bimFmtLen(bimBulgedLength(pf,null,true))]);
      if(o.bim.thickness)rows.push(['Thickness',bimFmtLen(o.bim.thickness)]);
    }else if(o.bim&&o.bim.type==='column'){
      rows.push(['Size',bimFmtLen(o.bim.width||0)+' \u00d7 '+bimFmtLen(o.bim.depth||0)]);
      rows.push(['Height',bimFmtLen(o.bim.height||0)]);
    }
    if(o.mesh&&o.mesh.v&&o.mesh.v.length){
      var mn=[Infinity,Infinity,Infinity],mx=[-Infinity,-Infinity,-Infinity],i,k;
      for(i=0;i<o.mesh.v.length;i++)for(k=0;k<3;k++){mn[k]=Math.min(mn[k],o.mesh.v[i][k]);mx[k]=Math.max(mx[k],o.mesh.v[i][k]);}
      rows.push(['Extents',bimFmtLen(mx[0]-mn[0])+' \u00d7 '+bimFmtLen(mx[2]-mn[2])+' \u00d7 '+bimFmtLen(mx[1]-mn[1])+' high']);
    }
    if(o.blockRef)rows.push(['Block',String(o.blockRef.name)]);   /* __acad3dV260 */
    if(o.xref)rows.push(['External reference',String(o.xref.name)]);   /* __acad3dV265 */
    if(o.attrib)rows.push(['Attribute',String(o.attrib.tag)]);
    if(o.attdef)rows.push(['Attribute definition',String(o.attdef.tag)+(o.attdef.def?' (default '+o.attdef.def+')':'')]);
    if(bimIsLocked(o))rows.push(['Locked','yes']);
    return rows;
  }
  function bimListType(o){
    if(o.bim&&o.bim.type)return o.bim.type.charAt(0).toUpperCase()+o.bim.type.slice(1);
    if(o.t==='sketch')return o.pts&&o.pts.length===1?'Point':(o.pts&&o.pts.length===2&&!bimHasBulge(o.bulges)?'Line':
      (o.bulges&&o.closed!==false&&o.pts.length===2?'Circle':'Polyline'));
    return o.t?o.t.charAt(0).toUpperCase()+o.t.slice(1):'Object';
  }
  function bimListPt(p,y){return 'X '+p[0].toFixed(3)+'  Y '+p[1].toFixed(3)+'  Z '+(+y||0).toFixed(3);}
  /* An area in square metres, in the project's unit squared (m\u00b2, mm\u00b2, ft\u00b2), at the unit's precision */
  function bimFmtArea(a){
    var U=bimUnitDef(),s=U.scale||1;
    return bimTrimNum((Math.abs(a)*s*s).toFixed(Math.max(bimUnitDp(),2)))+' '+U.label+'\u00b2';
  }
  /* The read-out: a small window of [label, value] rows, kept until closed. */
  function bimInquiryShow(title,rows){
    closeDlg();
    var d=document.createElement('div'),h='',i;
    d.className='a3d-dlg';
    d.setAttribute('data-a3dinq','1');
    for(i=0;i<rows.length;i++){
      if(rows[i]==='-'){h+='<hr style="border:0;border-top:1px solid #3b4a5e;margin:6px 0">';continue;}
      h+='<div class="a3d-dlgrow"><label>'+bimEsc(rows[i][0])+'</label><span style="user-select:text" data-a3dinqv="'+bimEsc(rows[i][0])+'">'+bimEsc(rows[i][1])+'</span></div>';
    }
    d.innerHTML='<div class="a3d-dlghd">'+bimEsc(title)+'</div><div class="a3d-dlgbody">'+h+'</div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="ok">Close</button></div>';
    el.root.appendChild(d);el.dlg=d;
    d.addEventListener('click',function(ev){var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;if(b)closeDlg();});
    d.addEventListener('keydown',function(ev){if(ev.key==='Escape'||ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();closeDlg();}});
    return d;
  }
  /* ---------- the commands ---------- */
  function startInquiryTool(kind){
    closeDlg();
    bimEnterDraftingMode();
    if(kind==='area'){
      var ids=(A3D.selSet&&A3D.selSet.length)?A3D.selSet.slice():(A3D.sel?[A3D.sel]:[]);
      if(ids.length){bimAreaOfObjects(ids);return;}
    }
    A3D.sk={tool:'inq'+kind,pts:[],y:bimGetActiveLevel().elev,on:null};
    a3dToast(kind==='id'?'ID: specify a point':kind==='dist'?'Distance: specify the first point':
      'Area: specify corner points, then Enter (or select closed objects first)');
    paint();
  }
  function bimIsInquiryTool(sk){return !!sk&&(sk.tool==='inqid'||sk.tool==='inqdist'||sk.tool==='inqarea');}
  function bimInquiryPoint(sk,p){
    var y=sk.y;
    if(sk.tool==='inqid'){
      A3D.sk=null;paint();
      bimInquiryShow('ID',[['Point',bimListPt(p,y)]]);
      return;
    }
    sk.pts.push([p[0],p[1]]);
    if(sk.tool==='inqdist'){
      if(sk.pts.length<2){a3dToast('Distance: specify the second point');paint();return;}
      var D=bimInquiryDist(sk.pts[0],sk.pts[1]);
      A3D.sk=null;paint();
      bimInquiryShow('Distance',[['Distance',bimFmtLen(D.d)],['Angle in plan',D.angle.toFixed(2)+'\u00b0'],
        ['Delta X',bimFmtLen(D.dx)],['Delta Y',bimFmtLen(D.dy)],'-',['From',bimListPt(sk.pts[0],y)],['To',bimListPt(sk.pts[1],y)]]);
      return;
    }
    a3dToast('Area: next point, or Enter to measure ('+sk.pts.length+' so far)');
    paint();
  }
  /* AREA's Enter: the points picked so far, closed. */
  function bimInquiryFinish(sk){
    if(!sk||sk.tool!=='inqarea')return false;
    var r=bimInquiryArea(sk.pts);
    A3D.sk=null;paint();
    if(!r){a3dToast('Area: pick three or more points');return true;}
    bimInquiryShow('Area',[['Area',bimFmtArea(r.area)],['Perimeter',bimFmtLen(r.perimeter)],['Points',String(sk.pts.length)]]);
    return true;
  }
  function bimAreaOfObjects(ids){
    var tot=0,per=0,n=0,i,o,rows=[];
    for(i=0;i<ids.length;i++){
      o=objById(ids[i]);if(!o)continue;
      var pts=null,bl=null;
      if(o.t==='sketch'&&o.closed!==false&&o.pts&&o.pts.length>=2&&(o.pts.length>2||o.bulges)){pts=o.pts;bl=o.bulges||null;}
      else if(o.t==='room')pts=o.pts;
      else if(o.bim&&(o.bim.profile||o.bim.footprint))pts=o.bim.profile||o.bim.footprint;
      if(!pts)continue;
      var a=bimBulgedArea(pts,bl,true),p=bimBulgedLength(pts,bl,true);
      tot+=a;per+=p;n++;
      if(ids.length>1)rows.push([o.name||o.id,bimFmtArea(a)]);
    }
    if(!n){a3dToast('Area: none of the selected objects is closed');return null;}
    if(rows.length)rows.push('-');
    rows.push(['Total area',bimFmtArea(tot)]);
    rows.push(['Total perimeter',bimFmtLen(per)]);
    bimInquiryShow('Area of '+n+' object'+(n>1?'s':''),rows);
    return {area:tot,perimeter:per,n:n};
  }
  function bimListCommand(){
    var ids=(A3D.selSet&&A3D.selSet.length)?A3D.selSet.slice():(A3D.sel?[A3D.sel]:[]),rows=[],i,o;
    if(!ids.length){a3dToast('List: select the objects first');return null;}
    for(i=0;i<ids.length&&i<50;i++){
      o=objById(ids[i]);if(!o)continue;
      if(rows.length)rows.push('-');
      rows=rows.concat(bimListRows(o));
    }
    if(ids.length>50)rows.push('-',['More',(ids.length-50)+' further objects not listed']);
    return bimInquiryShow('List: '+ids.length+' object'+(ids.length>1?'s':''),rows);
  }
export {
  bimInquiryFinish, bimInquiryPoint, bimInquiryShow, bimIsInquiryTool, bimListCommand, startInquiryTool
};
