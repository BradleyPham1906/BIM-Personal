import { A3D, el } from '../core/state.js';
import { camVecs } from '../core/mesh-primitives.js';
import { bimObjOffset, pushUndo } from '../drawing/plan-mode-sketch.js';
import { bimCreateTerrain, bimSurveyCheck } from '../survey/survey-check.js';
import { bimLayerShown } from '../layers/layer-rules.js';
import { bimEsc } from '../layers/layer-manager.js';
import { bimPropRow, bimPropText } from '../properties/palette.js';
import { refreshProps } from '../site-analysis/panel.js';
import { toScreen } from '../io/import-entry.js';
import { bimGlCompile, bimGlProjMatrix, bimGlViewMatrix } from '../render/webgl.js';
import { paint } from './terrain-3d.js';
import {
  bimPcClassName, bimPcGround, bimPcHeightColour, bimPcLasHeader, bimPcLasPoints, bimPcOrigin, bimPcPlyHeader,
  bimPcPlyPoints, bimPcSniff
} from './pointcloud.js';
import { fitScene } from '../ui/tool-palette.js';
import { refreshHud, saveSoon } from '../bim/region-regenerate.js';
import { refreshTree } from '../sheets/presentation-panel.js';
import { closeDlg } from '../ui/touch-input.js';
import { a3dToast, objById } from '../bim/csg-booleans.js';
import { cvH, cvScale, cvW } from '../ui/canvas-size.js';

  /* ================= __acad3dV190 WO-12, WO-13: point clouds in the model =================
     docs/work-orders/v190/SPEC.md parts 1 and 5, on pointcloud.js's pure functions (Cline's WO-01 to WO-11).
     - Import a .las or .ply: sniffed (a .laz is named, not read: LAZ waits for laz-perf's research), sampled to the
       point budget (2,000,000 unless set), rebased on its whole-metre origin, which the object keeps in double
       precision. A cloud has no known CRS here, so it opens as an "unregistered preview" at the model's origin, for
       the owner to place (MOVE); nothing is georeferenced silently.
     - Its points live beside the object (A3D_PC.data), not in it, so an undo step does not copy them. A cloud of
       up to 500,000 points is saved with the project (its sampled points, base64); a larger one keeps a reference,
       and after a reload asks for its file again.
     - Drawn as GL points (a WebGPU frame hands a frame with a cloud to WebGL), else, without WebGL, a thinned set
       on the 2D canvas. Coloured by RGB when the file has it, else by height; Properties sets RGB, class or height,
       hides classes, and runs Ground to surface: the lowest ground point per cell, previewed, then on confirmation
       a terrain surface (V108) whose survey check (V138) is reported. */
  var A3D_PC={data:{},gl:null,preview:null,budget:2000000};
  var BIM_PC_KEEP=500000,BIM_PC_2D_MAX=60000;
  /* ---------- reading ---------- */
  function bimPcLatin1(bytes,n){
    var s='',i,end=Math.min(bytes.length,n),CH=8192;
    for(i=0;i<end;i+=CH)s+=String.fromCharCode.apply(null,Array.prototype.slice.call(bytes.subarray(i,Math.min(end,i+CH))));
    return s;
  }
  /* A file's bytes to {kind, count, origin, cloud} or {error}. Pure on its inputs. */
  function bimPcReadBytes(bytes,max){
    var kind=bimPcSniff(bytes),dv,h,origin,cloud;
    if(kind==='laz')return {error:'LAZ (compressed LAS) is not read yet: decompress it to .las first (for example: laszip -i in.laz -o out.las)'};
    if(kind==='las'){
      dv=new DataView(bytes.buffer,bytes.byteOffset,bytes.byteLength);
      h=bimPcLasHeader(dv);
      if(h.error)return {error:'LAS: '+h.error};
      origin=bimPcOrigin(h);
      cloud=bimPcLasPoints(dv,h,max,origin);
      return {kind:'las',count:h.count,origin:origin,cloud:cloud,version:h.versionMajor+'.'+h.versionMinor,format:h.pointFormat};
    }
    if(kind==='ply'){
      h=bimPcPlyHeader(bimPcLatin1(bytes,65536));
      if(h.error)return {error:'PLY: '+h.error};
      cloud=bimPcPlyPoints(bytes,h,max,[0,0,0]);
      if(cloud.error)return {error:'PLY: '+cloud.error};
      origin=bimPcRebase(cloud);   /* PLY has no bounds in its header: the origin from its points */
      return {kind:'ply',count:h.count,origin:origin,cloud:cloud,format:h.format};
    }
    return {error:'Not a LAS or PLY file'};
  }
  /* A cloud read at [0, 0, 0] moved onto its own whole-metre origin (as bimPcOrigin's for LAS). Pure. */
  function bimPcRebase(cloud){
    var mn=[Infinity,Infinity,Infinity],mx=[-Infinity,-Infinity,-Infinity],i,k;
    for(i=0;i<cloud.n;i++)for(k=0;k<3;k++){var v=cloud.xyz[i*3+k];if(v<mn[k])mn[k]=v;if(v>mx[k])mx[k]=v;}
    if(!cloud.n)return [0,0,0];
    var o=[Math.floor((mn[0]+mx[0])/2),Math.floor((mn[1]+mx[1])/2),Math.floor(mn[2])];
    for(i=0;i<cloud.n;i++)for(k=0;k<3;k++)cloud.xyz[i*3+k]-=o[k];
    return o;
  }
  /* The cloud's height range (its own z, the file's up). Pure. */
  function bimPcZRange(cloud){
    var lo=Infinity,hi=-Infinity,i;
    for(i=0;i<cloud.n;i++){var z=cloud.xyz[i*3+2];if(z<lo)lo=z;if(z>hi)hi=z;}
    return cloud.n?[lo,hi]:[0,0];
  }
  /* The classes a cloud has, sorted. Pure. */
  function bimPcClasses(cloud){
    var seen={},out=[],i;
    if(!cloud.cls)return out;
    for(i=0;i<cloud.n;i++)if(!seen[cloud.cls[i]]){seen[cloud.cls[i]]=1;out.push(cloud.cls[i]);}
    return out.sort(function(a,b){return a-b;});
  }
  /* Each point's colour in a mode: 'rgb' (else height), 'class', 'height'; a hidden class's points alpha 0. Pure. */
  var BIM_PC_CLASS_COL={0:[150,150,150],1:[190,190,190],2:[166,124,82],3:[120,190,90],4:[70,160,60],5:[30,120,40],6:[220,90,70],7:[255,0,255],9:[70,130,220],
    10:[120,100,90],11:[90,90,90],13:[250,210,60],14:[250,170,40],15:[200,200,60],17:[160,160,200],18:[255,0,128]};
  function bimPcColours(cloud,mode,hidden){
    var out=new Uint8Array(cloud.n*4),zr=bimPcZRange(cloud),i;
    var m=mode==='class'&&cloud.cls?'class':(mode==='rgb'||!mode)&&cloud.rgb?'rgb':'height';
    for(i=0;i<cloud.n;i++){
      var c;
      if(m==='rgb')c=[cloud.rgb[i*3],cloud.rgb[i*3+1],cloud.rgb[i*3+2]];
      else if(m==='class')c=BIM_PC_CLASS_COL[cloud.cls[i]]||[200,200,200];
      else c=bimPcHeightColour(cloud.xyz[i*3+2],zr[0],zr[1]);
      out[i*4]=c[0];out[i*4+1]=c[1];out[i*4+2]=c[2];
      out[i*4+3]=(hidden&&cloud.cls&&hidden[cloud.cls[i]])?0:255;
    }
    return out;
  }
  /* ---------- in the model ---------- */
  function bimPcAdd(res,name,bytes){
    var cl=res.cloud;
    if(!cl.n)return null;
    pushUndo();
    A3D.counts.pointcloud=(A3D.counts.pointcloud||0)+1;
    var o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'pointcloud',name:'Cloud_'+A3D.counts.pointcloud+' '+String(name||'').replace(/\.[^.]+$/,'').slice(0,40),
      pos:[0,0,0],layer:A3D.activeLayer,col:'#9ec1ff',
      pc:{file:String(name||'').slice(0,120),bytes:bytes||0,kind:res.kind,count:res.count,n:cl.n,origin:res.origin,
        unregistered:true,mode:cl.rgb?'rgb':'height',hidden:{},zr:bimPcZRange(cl),classes:bimPcClasses(cl),hasRgb:!!cl.rgb}};
    o.pc.dataId=o.id;   /* a copy (COPY, MIRROR) shares the points by this */
    A3D_PC.data[o.id]={cloud:cl};
    A3D.objs.push(o);
    A3D.sel=o.id;A3D.sel2=null;A3D.selSet=[o.id];
    refreshTree();refreshHud();refreshProps();paint();saveSoon();
    return o;
  }
  function bimPcImport(buf,name){
    var bytes=new Uint8Array(buf),res=bimPcReadBytes(bytes,A3D_PC.budget);
    if(res.error){a3dToast(name+': '+res.error);return null;}
    var o=bimPcAdd(res,name,bytes.length);
    if(!o){a3dToast(name+': no points');return null;}
    fitScene();
    a3dToast(o.name+': '+o.pc.n.toLocaleString()+' points'+(o.pc.n<o.pc.count?' of '+o.pc.count.toLocaleString()+' (sampled to the budget)':'')+
      '. An unregistered preview: place it with MOVE');
    return o;
  }
  function bimPcIsCloud(o){return !!(o&&o.t==='pointcloud'&&o.pc);}
  /* the cloud's point i where the model shows it: file (x east, y north, z up) to app (x, y up, z south), plus pos */
  function bimPcWorld(o,cl,i){var q=bimObjOffset(o);return [cl.xyz[i*3]+q[0],cl.xyz[i*3+2]+q[1],-cl.xyz[i*3+1]+q[2]];}
  function bimPcData(o){return bimPcIsCloud(o)?A3D_PC.data[o.pc.dataId||o.id]||null:null;}
  /* the colours per object (a copy may colour its shared points its own way) */
  function bimPcColOf(o){
    var D=bimPcData(o);if(!D)return null;
    if(!D.cols)D.cols={};
    var key=o.pc.mode+'|'+JSON.stringify(o.pc.hidden||{}),C=D.cols[o.id];
    if(!C||C.key!==key){if(C&&C.gl&&C.G)C.G.gl.deleteBuffer(C.gl);C=D.cols[o.id]={key:key,col:bimPcColours(D.cloud,o.pc.mode,o.pc.hidden),gl:null};}
    return C;
  }
  function bimPcVisible(){return A3D.objs.filter(function(o){return bimPcData(o)&&bimLayerShown(o);});}
  /* The cloud under a screen point: the nearest of its points (every k-th, at most 20,000) within 6 px. */
  function bimPcPick(x,y){
    var L=bimPcVisible(),V=camVecs(A3D.cam),W=cvW(),H=cvH(),best=null,bd=6,i,j;
    for(i=0;i<L.length;i++){
      var o=L[i],D=bimPcData(o),n=D.cloud.n,step=Math.max(1,Math.ceil(n/20000));
      for(j=0;j<n;j+=step){var s=toScreen(bimPcWorld(o,D.cloud,j),V,W,H),d=Math.abs(s[0]-x)+Math.abs(s[1]-y);if(d<bd){bd=d;best=o;}}
    }
    return best;
  }
  /* ---------- drawing ---------- */
  function bimPcGlProg(G){
    if(A3D_PC.gl&&A3D_PC.gl.G===G)return A3D_PC.gl;
    var gl=G.gl;
    var vs=bimGlCompile(gl,gl.VERTEX_SHADER,'attribute vec3 aPos;attribute vec4 aCol;uniform mat4 uView;uniform mat4 uProj;uniform vec3 uOffset;uniform float uSize;varying vec4 vCol;'+
      'void main(){vCol=aCol;gl_Position=uProj*uView*vec4(aPos.x+uOffset.x,aPos.z+uOffset.y,-aPos.y+uOffset.z,1.0);gl_PointSize=aCol.a>0.0?uSize:0.0;}');
    var fs=bimGlCompile(gl,gl.FRAGMENT_SHADER,'precision mediump float;varying vec4 vCol;uniform vec3 uSel;uniform float uIsSel;'+
      'void main(){if(vCol.a<0.5)discard;gl_FragColor=vec4(mix(vCol.rgb,uSel,uIsSel*0.35),1.0);}');
    if(!vs||!fs)return null;
    var p=gl.createProgram();gl.attachShader(p,vs);gl.attachShader(p,fs);gl.linkProgram(p);
    if(!gl.getProgramParameter(p,gl.LINK_STATUS)){console.warn('[BIM] point cloud shader: '+gl.getProgramInfoLog(p));return null;}
    A3D_PC.gl={G:G,prog:p,pos:gl.getAttribLocation(p,'aPos'),col:gl.getAttribLocation(p,'aCol'),view:gl.getUniformLocation(p,'uView'),
      proj:gl.getUniformLocation(p,'uProj'),off:gl.getUniformLocation(p,'uOffset'),size:gl.getUniformLocation(p,'uSize'),
      sel:gl.getUniformLocation(p,'uSel'),isSel:gl.getUniformLocation(p,'uIsSel')};
    return A3D_PC.gl;
  }
  function bimPcDrawGl(G,V,W,H){
    A3D_PC.drewGl=false;
    var L=bimPcVisible();if(!L.length)return;
    var P=bimPcGlProg(G);if(!P)return;
    var gl=G.gl,i;
    gl.useProgram(P.prog);
    gl.uniformMatrix4fv(P.view,false,bimGlViewMatrix(V));
    gl.uniformMatrix4fv(P.proj,false,bimGlProjMatrix(W,H,A3D.flat,A3D.cam.dist));
    gl.uniform1f(P.size,Math.max(1,Math.round(2*cvScale(el.cv))));
    gl.uniform3f(P.sel,0.306,0.631,1.0);
    gl.enableVertexAttribArray(P.pos);gl.enableVertexAttribArray(P.col);
    for(i=0;i<L.length;i++){
      var o=L[i],D=bimPcData(o),C=bimPcColOf(o),q=bimObjOffset(o);
      if(!D.glPos||D.glG!==G){D.glPos=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,D.glPos);gl.bufferData(gl.ARRAY_BUFFER,D.cloud.xyz,gl.STATIC_DRAW);D.glG=G;}
      if(!C.gl||C.G!==G){C.gl=gl.createBuffer();C.G=G;gl.bindBuffer(gl.ARRAY_BUFFER,C.gl);gl.bufferData(gl.ARRAY_BUFFER,C.col,gl.STATIC_DRAW);}
      gl.uniform3f(P.off,q[0],q[1],q[2]);
      gl.uniform1f(P.isSel,(A3D.sel===o.id||(A3D.selSet&&A3D.selSet.indexOf(o.id)>=0))?1:0);
      gl.bindBuffer(gl.ARRAY_BUFFER,D.glPos);gl.vertexAttribPointer(P.pos,3,gl.FLOAT,false,0,0);
      gl.bindBuffer(gl.ARRAY_BUFFER,C.gl);gl.vertexAttribPointer(P.col,4,gl.UNSIGNED_BYTE,true,0,0);
      gl.drawArrays(gl.POINTS,0,D.cloud.n);
    }
    gl.disableVertexAttribArray(P.pos);gl.disableVertexAttribArray(P.col);
    A3D_PC.drewGl=true;
  }
  /* Without WebGL: every k-th point, at most BIM_PC_2D_MAX, as small squares on the 2D canvas. */
  function bimPcDraw2d(ctx,V,W,H,glOn){
    var L=bimPcVisible(),i,j;
    if(A3D_PC.preview)bimPcDrawPreview(ctx,V,W,H);
    if(!L.length||(glOn&&A3D_PC.drewGl))return;
    for(i=0;i<L.length;i++){
      var o=L[i],D=bimPcData(o),col=bimPcColOf(o).col,n=D.cloud.n,step=Math.max(1,Math.ceil(n/BIM_PC_2D_MAX));
      for(j=0;j<n;j+=step){
        if(!col[j*4+3])continue;
        var s=toScreen(bimPcWorld(o,D.cloud,j),V,W,H);
        if(s[0]<0||s[1]<0||s[0]>W||s[1]>H)continue;
        ctx.fillStyle='rgb('+col[j*4]+','+col[j*4+1]+','+col[j*4+2]+')';
        ctx.fillRect(s[0]-1,s[1]-1,2,2);
      }
    }
  }
  function bimPcDrawPreview(ctx,V,W,H){
    var P=A3D_PC.preview,o=objById(P&&P.id),i;
    if(!o)return;
    var q=bimObjOffset(o);
    ctx.save();ctx.fillStyle='#ff9f1a';
    for(i=0;i<P.pts.length;i++){var p=P.pts[i],s=toScreen([p[0]+q[0],p[2]+q[1],-p[1]+q[2]],V,W,H);ctx.fillRect(s[0]-2,s[1]-2,4,4);}
    ctx.restore();
  }
  /* ---------- saved with the project ---------- */
  function bimPcB64(arr){
    var b=new Uint8Array(arr.buffer,arr.byteOffset,arr.byteLength),s='',i,CH=8192;
    for(i=0;i<b.length;i+=CH)s+=String.fromCharCode.apply(null,Array.prototype.slice.call(b.subarray(i,i+CH)));
    return btoa(s);
  }
  function bimPcUnB64(s,Type){
    var t=atob(String(s||'')),b=new Uint8Array(t.length),i;
    for(i=0;i<t.length;i++)b[i]=t.charCodeAt(i);
    return new Type(b.buffer);
  }
  function bimPcSaveData(){
    var out={},i;
    for(i=0;i<A3D.objs.length;i++){
      var o=A3D.objs[i],D=bimPcData(o),k=o.pc&&(o.pc.dataId||o.id);
      if(!D||D.cloud.n>BIM_PC_KEEP||out[k])continue;
      try{out[k]={n:D.cloud.n,xyz:bimPcB64(D.cloud.xyz),cls:D.cloud.cls?bimPcB64(D.cloud.cls):null,rgb:D.cloud.rgb?bimPcB64(D.cloud.rgb):null};}
      catch(e){console.warn('[BIM] point cloud not saved: '+o.name,e);}
    }
    return out;
  }
  function bimPcRestoreData(saved){
    A3D_PC.data={};A3D_PC.preview=null;
    if(!saved||typeof saved!=='object')return;
    var k;
    for(k in saved){
      var s=saved[k];
      try{
        var cl={n:+s.n,xyz:bimPcUnB64(s.xyz,Float32Array),cls:s.cls?bimPcUnB64(s.cls,Uint8Array):null,rgb:s.rgb?bimPcUnB64(s.rgb,Uint8Array):null};
        if(cl.xyz.length===cl.n*3)A3D_PC.data[k]={cloud:cl};
      }catch(e){console.warn('[BIM] a saved point cloud could not be read',e);}
    }
  }
  /* ---------- Properties ---------- */
  function bimPcPropsHtml(o){
    var p=o.pc,D=bimPcData(o),h='',modes=[['rgb','RGB'],['class','Class'],['height','Height']];
    h+=bimPropText('Points',p.n.toLocaleString()+(p.n<p.count?' of '+p.count.toLocaleString()+' (sampled)':''));
    h+=bimPropText('File',p.file+' ('+String(p.kind).toUpperCase()+')');
    h+=bimPropText('Origin (file x, y, z)',p.origin.join(', '));
    if(p.unregistered)h+=bimPropText('Placement','Unregistered preview: no CRS; place it with MOVE');
    if(!D)return h+'<div class="a3d-propnote">Its points are not in this session (a cloud over '+BIM_PC_KEEP.toLocaleString()+' points is not saved inside the project): import '+bimEsc(p.file)+' again.</div>';
    h+=bimPropRow('Colour by','<select data-propf="pcmode">'+modes.filter(function(m){return m[0]!=='rgb'||p.hasRgb;}).filter(function(m){return m[0]!=='class'||p.classes.length;})
      .map(function(m){return '<option value="'+m[0]+'"'+(p.mode===m[0]?' selected':'')+'>'+m[1]+'</option>';}).join('')+'</select>');
    p.classes.forEach(function(c){
      h+=bimPropRow(bimEsc(bimPcClassName(c)),'<input type="checkbox" data-propf="pccls:'+c+'"'+(p.hidden&&p.hidden[c]?'':' checked')+'> shown');
    });
    h+=bimPropRow('Budget for imports','<input type="number" min="1000" step="1000" data-propf="pcbudget" value="'+A3D_PC.budget+'">');
    if(p.classes.indexOf(2)>=0)h+=bimPropRow('Ground to surface','<button data-propf="pcground">Preview…</button>');
    return h;
  }
  function bimPcPropField(o,f,inp){
    if(!bimPcIsCloud(o))return false;
    if(f==='pcmode'){pushUndo();o.pc.mode=inp.value;paint();saveSoon();return true;}
    if(f.indexOf('pccls:')===0){pushUndo();var c=+f.slice(6);if(!o.pc.hidden)o.pc.hidden={};if(inp.checked)delete o.pc.hidden[c];else o.pc.hidden[c]=true;paint();saveSoon();return true;}
    if(f==='pcbudget'){var b=Math.floor(+inp.value);if(!(b>=1000)){a3dToast('A budget is 1,000 points or more');refreshProps();return true;}A3D_PC.budget=b;a3dToast('The next import keeps up to '+b.toLocaleString()+' points');return true;}
    return false;
  }
  /* Ground to surface: the lowest ground point per cell, previewed; on confirmation a terrain surface, checked. */
  function openPcGroundDlg(o){
    var D=bimPcData(o);
    if(!D){a3dToast('Select a point cloud whose points are loaded');return null;}
    closeDlg();
    var d=document.createElement('div');d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">Ground to surface</div><div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Cell, m</label><input type="number" min="0.1" step="any" data-a3dpg="cell" value="2"></div>'+
      '<div class="a3d-propnote" data-a3dpg="msg">The lowest ground point (class 2) in each cell. Preview shows them; Create makes a terrain surface and checks it.</div>'+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dpgact="preview">Preview</button><button data-a3dpgact="create">Create surface</button></div>';
    el.root.appendChild(d);el.dlg=d;
    function pts(){
      var cell=+d.querySelector('[data-a3dpg="cell"]').value;
      if(!(cell>0)){d.querySelector('#a3d-dlgerr').textContent='The cell is more than 0';return null;}
      var g=bimPcGround(D.cloud,cell);
      if(g.length<3){d.querySelector('#a3d-dlgerr').textContent='Fewer than 3 ground points: a larger cell, or a cloud with ground classified';return null;}
      if(g.length>40000){d.querySelector('#a3d-dlgerr').textContent=g.length.toLocaleString()+' cells is more than a surface should take (40,000): a larger cell';return null;}
      return g;
    }
    d.addEventListener('click',function(ev){
      var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dpgact],[data-a3dlg]'):null;if(!b)return;
      if(b.getAttribute('data-a3dlg')){A3D_PC.preview=null;closeDlg();paint();return;}
      var g=pts();if(!g)return;
      if(b.getAttribute('data-a3dpgact')==='preview'){
        A3D_PC.preview={id:o.id,pts:g};paint();
        d.querySelector('[data-a3dpg="msg"]').textContent=g.length.toLocaleString()+' ground points (orange). Create makes the surface.';
        return;
      }
      A3D_PC.preview=null;closeDlg();
      var q=bimObjOffset(o),model=g.map(function(p,i){return [p[0]+q[0],-p[1]+q[2],p[2]+q[1],'G'+(i+1),'ground'];});
      var t=bimCreateTerrain(model,{format:'Point cloud ground',units:'m',file:o.pc.file,from:o.id});
      if(t){var r=bimSurveyCheck(t);a3dToast(t.name+' from '+g.length+' ground points'+(r?': survey check '+r.verdict:''));}
    });
    return d;
  }
export {
  bimPcDraw2d, bimPcDrawGl, bimPcImport, bimPcPick, bimPcPropField, bimPcPropsHtml, bimPcRestoreData,
  bimPcSaveData, bimPcVisible, openPcGroundDlg
};
