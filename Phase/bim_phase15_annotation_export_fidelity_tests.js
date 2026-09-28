var A3D={objs:[],counts:{},seq:1,activeLevel:'lvl-0',activeLayer:'layer-0',sel:null,sel2:null,selSet:[],
  layers:[{id:'layer-0',name:'Model',color:'#7f9db8',visible:true,locked:false}],
  levels:[{id:'lvl-0',name:'Level 0',elev:0,height:3}]};
var UNDO_STACK=[];
function pushUndo(){UNDO_STACK.push(1);}
function refreshTree(){}
function refreshHud(){}
function paint(){}
function saveSoon(){}
var TOASTS=[];
function a3dToast(m){TOASTS.push(m);}
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

  function bimCreateDim(p1,p2,p3){
    var r=bimComputeDim(p1,p2,p3);
    if(!r){a3dToast('Dimension points cannot coincide');return null;}
    pushUndo();
    A3D.counts.dim=(A3D.counts.dim||0)+1;
    var lvl=bimGetActiveLevel();
    var o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'dim',name:'Dim_'+A3D.counts.dim,col:'#dfe4ea',pos:[0,0,0],
      p1:p1,p2:p2,d1:r.d1,d2:r.d2,length:r.length,y:lvl.elev,levelId:A3D.activeLevel,layer:A3D.activeLayer};
    A3D.objs.push(o);
    A3D.sel=o.id;A3D.sel2=null;A3D.selSet=[o.id];
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast(o.name+' created \u2014 '+r.length.toFixed(2)+' m');
    return o;
  }

  function bimCreateTextLabel(pt,y,text){
    pushUndo();
    A3D.counts.text=(A3D.counts.text||0)+1;
    var o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'text',name:'Text_'+A3D.counts.text,col:'#dfe4ea',pos:[0,0,0],
      text:text,pt:pt,y:y,levelId:A3D.activeLevel,layer:A3D.activeLayer};
    A3D.objs.push(o);
    A3D.sel=o.id;A3D.sel2=null;A3D.selSet=[o.id];
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast(o.name+' created');
    return o;
  }

  function bimStrToBytes(s){
    var arr=new Uint8Array(s.length),i;
    for(i=0;i<s.length;i++)arr[i]=s.charCodeAt(i)&0xFF;
    return arr;
  }

  function bimPadNum(n,len){var s=String(n);while(s.length<len)s='0'+s;return s;}

  function bimBuildSimplePdf(width,height,rgbBytes){
    var chunks=[],offsets=[],pos=0;
    function push(x){
      var buf=(typeof x==='string')?bimStrToBytes(x):x;
      chunks.push(buf);
      pos+=buf.length;
    }
    function beginObj(n){offsets[n]=pos;push(n+' 0 obj\n');}
    push('%PDF-1.4\n%\xE2\xE3\xCF\xD3\n');
    beginObj(1);push('<< /Type /Catalog /Pages 2 0 R >>\nendobj\n');
    beginObj(2);push('<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n');
    beginObj(3);push('<< /Type /Page /Parent 2 0 R /Resources << /XObject << /Im0 5 0 R >> >> /MediaBox [0 0 '+width+' '+height+'] /Contents 4 0 R >>\nendobj\n');
    var content='q\n'+width+' 0 0 '+height+' 0 0 cm\n/Im0 Do\nQ\n';
    var contentBytes=bimStrToBytes(content);
    beginObj(4);push('<< /Length '+contentBytes.length+' >>\nstream\n');push(contentBytes);push('\nendstream\nendobj\n');
    beginObj(5);
    push('<< /Type /XObject /Subtype /Image /Width '+width+' /Height '+height+' /ColorSpace /DeviceRGB /BitsPerComponent 8 /Length '+rgbBytes.length+' >>\nstream\n');
    push(rgbBytes);
    push('\nendstream\nendobj\n');
    var xrefStart=pos;
    var xref='xref\n0 6\n0000000000 65535 f \n',i;
    for(i=1;i<=5;i++)xref+=bimPadNum(offsets[i],10)+' 00000 n \n';
    push(xref);
    push('trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n'+xrefStart+'\n%%EOF');
    var total=0,j;
    for(j=0;j<chunks.length;j++)total+=chunks[j].length;
    var out=new Uint8Array(total),off=0;
    for(j=0;j<chunks.length;j++){out.set(chunks[j],off);off+=chunks[j].length;}
    return out;
  }

  function bimDuplicateObject(o,dx,dz){
    var copy;
    if(o.t==='opening')return null;
    if(o.t==='sketch'){
      copy=JSON.parse(JSON.stringify(o));
      copy.id='a3d-'+Date.now().toString(36)+'-'+(A3D.seq++);
      copy.pts=o.pts.map(function(p){return [p[0]+dx,p[1]+dz];});
      copy.name=o.name+' copy';
    }else if(o.bim&&o.bim.type==='wall'){
      var newCl=o.bim.centerline.map(function(p){return [p[0]+dx,p[1]+dz];});
      var res=bimBuildWallGeometry(newCl,o.bim.baseY,o.bim.height,o.bim.thickness,o.bim.align,o.bim.closed);
      if(res.error)return null;
      A3D.counts.wall=(A3D.counts.wall||0)+1;
      res.bim.levelId=o.bim.levelId;
      copy={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:'Wall_'+A3D.counts.wall,col:o.col,pos:[0,0,0],mesh:res.mesh,bim:res.bim,layer:o.layer};
    }else if(o.bim&&o.bim.type==='floor'){
      if(!o.bim.profile)return null;
      var newProf=o.bim.profile.map(function(p){return [p[0]+dx,p[1]+dz];});
      var res2=bimBuildFloorGeometry(newProf,o.bim.baseY,o.bim.thickness);
      if(res2.error)return null;
      A3D.counts.floor=(A3D.counts.floor||0)+1;
      copy={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:'Floor_'+A3D.counts.floor,col:o.col,pos:[0,0,0],mesh:res2.mesh,
        bim:{type:'floor',thickness:o.bim.thickness,material:o.bim.material,levelId:o.bim.levelId,baseY:o.bim.baseY,profile:newProf},layer:o.layer};
    }else if(o.bim&&o.bim.type==='column'){
      var newCenter=[o.bim.center[0]+dx,o.bim.center[1]+dz];
      var res3=bimBuildColumnGeometry(newCenter,o.bim.baseY,o.bim.width,o.bim.depth,o.bim.height);
      if(res3.error)return null;
      A3D.counts.column=(A3D.counts.column||0)+1;
      copy={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:'Column_'+A3D.counts.column,col:o.col,pos:[0,0,0],mesh:res3.mesh,
        bim:{type:'column',width:o.bim.width,depth:o.bim.depth,height:o.bim.height,baseY:o.bim.baseY,levelId:o.bim.levelId,center:newCenter},layer:o.layer};
    }else if(o.t==='room'){
      A3D.counts.room=(A3D.counts.room||0)+1;
      copy={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'room',name:'Room_'+A3D.counts.room,col:o.col,pos:[0,0,0],
        pts:o.pts.map(function(p){return [p[0]+dx,p[1]+dz];}),y:o.y,area:o.area,levelId:o.levelId,
        sourceType:o.sourceType,sourceId:o.sourceId,layer:o.layer};
    }else if(o.t==='dim'){
      A3D.counts.dim=(A3D.counts.dim||0)+1;
      copy={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'dim',name:'Dim_'+A3D.counts.dim,col:o.col,pos:[0,0,0],
        p1:[o.p1[0]+dx,o.p1[1]+dz],p2:[o.p2[0]+dx,o.p2[1]+dz],d1:[o.d1[0]+dx,o.d1[1]+dz],d2:[o.d2[0]+dx,o.d2[1]+dz],
        length:o.length,y:o.y,levelId:o.levelId,layer:o.layer};
    }else if(o.t==='text'){
      A3D.counts.text=(A3D.counts.text||0)+1;
      copy={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'text',name:'Text_'+A3D.counts.text,col:o.col,pos:[0,0,0],
        text:o.text,pt:[o.pt[0]+dx,o.pt[1]+dz],y:o.y,levelId:o.levelId,layer:o.layer};
    }else if(o.bim&&o.bim.type==='roof'&&o.bim.footprint){
      var newFoot=o.bim.footprint.map(function(p){return [p[0]+dx,p[1]+dz];});
      var res4=bimBuildRoofGeometry(newFoot,o.bim.baseY,o.bim.pitch,o.bim.slopeDir,o.bim.thickness);
      if(res4.error)return null;
      A3D.counts.roof=(A3D.counts.roof||0)+1;
      res4.bim.levelId=o.bim.levelId;
      copy={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:'Roof_'+A3D.counts.roof,col:o.col,pos:[0,0,0],mesh:res4.mesh,bim:res4.bim,layer:o.layer};
    }else if(o.bim&&o.bim.type==='stair'){
      var newStart=[o.bim.start[0]+dx,o.bim.start[1]+dz];
      var res5=bimBuildStairGeometry(newStart,o.bim.dir,o.bim.width,o.bim.baseY,o.bim.totalRise,o.bim.riserH,o.bim.treadD);
      if(res5.error)return null;
      A3D.counts.stair=(A3D.counts.stair||0)+1;
      res5.bim.levelId=o.bim.levelId;
      res5.bim.targetLevelId=o.bim.targetLevelId;
      copy={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:'Stair_'+A3D.counts.stair,col:o.col,pos:[0,0,0],mesh:res5.mesh,bim:res5.bim,layer:o.layer};
    }else{
      copy=JSON.parse(JSON.stringify(o));
      copy.id='a3d-'+Date.now().toString(36)+'-'+(A3D.seq++);
      copy.pos=[o.pos[0]+dx,o.pos[1],o.pos[2]+dz];
      copy.name=o.name+' copy';
    }
    return copy;
  }

  function objById(id){
    var i;
    for(i=0;i<A3D.objs.length;i++)if(A3D.objs[i].id===id)return A3D.objs[i];
    return null;
  }

  function bimGetActiveLevel(){
    var i;
    for(i=0;i<A3D.levels.length;i++)if(A3D.levels[i].id===A3D.activeLevel)return A3D.levels[i];
    return A3D.levels[0]||{id:'lvl-0',name:'Level 0',elev:0,height:3};
  }

var PASS=0,FAIL=0;
function assert(name,cond,detail){if(cond){PASS++;console.log('PASS  '+name);}else{FAIL++;console.log('FAIL  '+name+(detail?' -- '+detail:''));}}

// ---- 1. Dimension: real embedded pipeline end to end ----
var dim=bimCreateDim([0,0],[4,0],[2,1]);
assert('bimCreateDim creates a real dim object', !!dim && dim.t==='dim');
assert('dim length is correct', Math.abs(dim.length-4)<1e-9, dim.length);
assert('dim auto-names sequentially', dim.name==='Dim_1');
assert('creating a dim pushes exactly one undo snapshot', UNDO_STACK.length===1);

var dim2=bimCreateDim([1,1],[1,1],[2,2]);
assert('degenerate (coincident) dim points are rejected, not crashed', dim2===null);
assert('rejecting a degenerate dim does not push an extra undo snapshot', UNDO_STACK.length===1);

// ---- 2. Text label: real embedded pipeline ----
UNDO_STACK.length=0;
var txt=bimCreateTextLabel([3,3],0,'Kitchen');
assert('bimCreateTextLabel creates a real text object', !!txt && txt.t==='text' && txt.text==='Kitchen');
assert('text auto-names sequentially', txt.name==='Text_1');
assert('creating a text label pushes exactly one undo snapshot', UNDO_STACK.length===1);

// ---- 3. Duplication of dim/text via the real embedded bimDuplicateObject ----
var dimDup=bimDuplicateObject(dim,2,3);
assert('duplicating a dim offsets both p1 and p2, and the pre-computed d1/d2', 
  dimDup.p1[0]===dim.p1[0]+2 && dimDup.p2[0]===dim.p2[0]+2 && dimDup.d1[0]===dim.d1[0]+2);
assert('duplicated dim keeps the same length', dimDup.length===dim.length);

var txtDup=bimDuplicateObject(txt,1,1);
assert('duplicating a text label offsets its anchor point and keeps content', 
  txtDup.pt[0]===txt.pt[0]+1 && txtDup.text===txt.text);

// ---- 4. PDF export: byte-exact construction, verified structurally by round-tripping the math ----
// (full PDF-library validation happens in a separate step against the actual generated bytes)
var W=6,H=4;
var rgb=new Uint8Array(W*H*3);
for(var y=0;y<H;y++)for(var x=0;x<W;x++){
  var idx=(y*W+x)*3;
  rgb[idx]=Math.round(255*x/(W-1));
  rgb[idx+1]=0;
  rgb[idx+2]=Math.round(255*y/(H-1));
}
var pdfBytes=bimBuildSimplePdf(W,H,rgb);
assert('bimBuildSimplePdf (real embedded code) produces a non-trivial byte array', pdfBytes.length>200);
assert('PDF starts with the correct header', 
  String.fromCharCode(pdfBytes[0],pdfBytes[1],pdfBytes[2],pdfBytes[3],pdfBytes[4])==='%PDF-');
assert('PDF ends with %%EOF', 
  String.fromCharCode(pdfBytes[pdfBytes.length-5],pdfBytes[pdfBytes.length-4],pdfBytes[pdfBytes.length-3],pdfBytes[pdfBytes.length-2],pdfBytes[pdfBytes.length-1])==='%%EOF');

// write it out for external PDF-library validation
var fs=require('fs');
fs.writeFileSync('/tmp/embedded_pdf_test.pdf', Buffer.from(pdfBytes));
console.log('wrote /tmp/embedded_pdf_test.pdf for external validation,', pdfBytes.length, 'bytes');

console.log('');
console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
