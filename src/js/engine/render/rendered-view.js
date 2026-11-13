import { A3D, el } from '../core/state.js';
import { bimEsc } from '../layers/layer-manager.js';
import { bimPropRow } from '../properties/palette.js';
import { refreshProps } from '../site-analysis/panel.js';
import { bimLbBase } from '../ladybug/runtime.js';
import { bimSceneFrameDone } from './gpu-batches.js';
import {
  BIM_RV_QUALITY, BIM_RV_QUALITY_NAMES, BIM_RV_SKIES, bimRvCore, bimRvSkyFor
} from './rendered-core.js';
import { bimRvBuild, bimRvCamera, bimRvPlan, bimRvReach, bimRvSun } from './rendered-scene.js';
import { A3D_BENCH } from './webgpu.js';
import { paint } from '../map/terrain-3d.js';
import { bimShadowGround } from '../site/shadows.js';
import { a3dToast } from '../bim/csg-booleans.js';
import { cvScale } from '../ui/canvas-size.js';


  /* ================= __acad3dV194: the rendered view =================
     docs/research/research-rendered-view.md. A third way the 3D view is drawn, beside WebGPU and WebGL: the model in
     daylight, by three.js (render/rendered-core.js draws it, render/rendered-scene.js says what). Off until asked for
     (RENDER, or Properties > View > Display), and never kept on between sessions: the app opens as it always has.

     three.js is not part of the build. It is one file, runtime/three/<version>/bim-three.min.js (MIT, pinned in
     runtime/MANIFEST.json by its SHA-256, built by tools/three), fetched when the view is first asked for: from the
     page's own folder over http(s), and from a copy opened from a disk first from a runtime folder beside it, then
     from the Pages address. Where the browser can check it against its hash, it does (subresource integrity).

     The picture is drawn on a canvas of its own under the overlay, where the other two engines' canvases are, with
     the view's own camera, so the grips, dimensions and text drawn over it, picking and Save image work as before.
     Each paint that changes what is seen (the model, the camera, the sun, a setting) starts the picture again with one
     pass; while nothing changes, passes are added a few a frame until the quality's number is reached. Anything that
     fails (no three.js, no WebGL 2, a lost context, a frame that throws) is said once and the shaded view is back in
     the same frame: never a broken view. */
  var BIM_RV_VER='0.186.1',BIM_RV_FILE='three/'+BIM_RV_VER+'/bim-three.min.js';
  var BIM_RV_SRI='sha256-nlMhFtFZ48EpXw4milRquaT/Hc0JPr3IqG6LCINZo5E=';   /* __acad3dV195: with the glTF addons */   /* the file's SHA-256, as runtime/MANIFEST.json pins it */
  var BIM_RV_KEY='acad3dRenderedV1';
  var BIM_RV_STILL_MS=140;   /* passes are added once the view has been still this long */
  var A3D_RV={on:false,st:'idle',err:'',T:null,core:null,cv:null,sig:'',done:0,want:64,raf:0,per:1,last:0,stillAt:0,
    load:null,hold:false,drew:false,set:null,sun:null,sky:null,info:null};
  /* the view's settings, this browser's: the sky, the ground, the edges, the quality */
  function bimRvSettings(){
    if(A3D_RV.set)return A3D_RV.set;
    var s={sky:'clear',ground:true,edges:false,quality:'good'},r=null;
    try{r=JSON.parse(localStorage.getItem(BIM_RV_KEY)||'null');}catch(eS){r=null;}
    if(r&&typeof r==='object'){
      if(BIM_RV_SKIES.hasOwnProperty(r.sky))s.sky=r.sky;
      if(BIM_RV_QUALITY.hasOwnProperty(r.quality))s.quality=r.quality;
      if(typeof r.ground==='boolean')s.ground=r.ground;
      if(typeof r.edges==='boolean')s.edges=r.edges;
    }
    A3D_RV.set=s;
    return s;
  }
  function bimRvSetting(k,v){
    var s=bimRvSettings();
    if(k==='sky'&&BIM_RV_SKIES.hasOwnProperty(v))s.sky=v;
    else if(k==='quality'&&BIM_RV_QUALITY.hasOwnProperty(v))s.quality=v;
    else if(k==='ground'||k==='edges')s[k]=(v===true||v==='1');
    else return false;
    try{localStorage.setItem(BIM_RV_KEY,JSON.stringify(s));}
    catch(eS){console.warn('[BIM] The rendered view\'s settings could not be kept in this browser',eS);}
    A3D_RV.sig='';
    if(A3D.on)paint();
    refreshProps();
    return true;
  }
  /* where three.js is asked for, in order, [{u, sri}]: from the runtime's address (base: the page's own folder over
     http(s), the Pages address for a copy on a disk), and for a copy on a disk first from a runtime folder beside it */
  function bimRvSources(protocol,base){
    var p=String(protocol||''),out=[];
    if(p!=='http:'&&p!=='https:')out.push({u:'runtime/'+BIM_RV_FILE,sri:false});
    out.push({u:String(base)+BIM_RV_FILE,sri:true});
    return out;
  }
  /* three.js, asked for once; a promise of it */
  function bimRvLoad(){
    var R=A3D_RV;
    if(R.load)return R.load;
    if(window.BIMTHREE&&window.BIMTHREE.WebGLRenderer){R.T=window.BIMTHREE;R.st='ready';R.load=Promise.resolve(R.T);return R.load;}
    var src=bimRvSources(window.location&&window.location.protocol,bimLbBase()),i=0;
    R.st='loading';R.err='';
    R.load=new Promise(function(res,rej){
      function next(){
        if(i>=src.length){rej(new Error('three.js could not be loaded from '+src.map(function(s){return s.u;}).join(' or ')));return;}
        var s=src[i++],tag=document.createElement('script');
        tag.src=s.u;
        if(s.sri){tag.integrity=BIM_RV_SRI;tag.crossOrigin='anonymous';}
        tag.onload=function(){if(window.BIMTHREE&&window.BIMTHREE.WebGLRenderer)res(window.BIMTHREE);else next();};
        tag.onerror=function(){if(tag.parentNode)tag.parentNode.removeChild(tag);next();};
        document.head.appendChild(tag);
      }
      next();
    }).then(function(T){R.T=T;R.st='ready';return T;},function(e){R.st='failed';R.err=String(e&&e.message||e);R.load=null;throw e;});
    return R.load;
  }
  /* a phone or a small tablet: smaller shadow maps and no multisampling */
  function bimRvLightDevice(){
    var m=navigator.deviceMemory,t=navigator.maxTouchPoints||0,s=window.screen?Math.min(window.screen.width||0,window.screen.height||0):0;
    return (typeof m==='number'&&m<=4)||(t>0&&s>0&&s<=900);
  }
  /* the picture's canvas, under the overlay beside the other engines' */
  function bimRvCanvas(){
    var R=A3D_RV,over=el.cv,cv;
    if(R.cv)return R.cv;
    if(!over||!over.parentNode)return null;
    cv=document.createElement('canvas');
    cv.id='a3d-rvcanvas';
    over.parentNode.insertBefore(cv,over);
    cv.addEventListener('webglcontextlost',function(ev){ev.preventDefault();bimRvLost();},false);
    R.cv=cv;
    return cv;
  }
  /* the picture given back: its canvas and everything three.js holds */
  function bimRvDrop(){
    var R=A3D_RV;
    if(R.raf){cancelAnimationFrame(R.raf);R.raf=0;}
    if(R.core){try{R.core.dispose();}catch(eD){console.warn('[BIM] Rendered view: its picture could not be given back',eD);}}
    if(R.cv&&R.cv.parentNode)R.cv.parentNode.removeChild(R.cv);
    R.core=null;R.cv=null;R.sig='';R.done=0;R.drew=false;
  }
  function bimRvLost(){
    var R=A3D_RV;
    if(!R.core)return;
    R.core=null;   /* its context is gone: nothing to give back */
    bimRvDrop();
    R.on=false;R.err='the graphics context was lost';
    console.warn('[BIM] Rendered view: the graphics context was lost; the shaded view is back.');
    a3dToast('The rendered view lost its graphics context. The shaded view is back.');
    setTimeout(function(){if(A3D.on)paint();refreshProps();},0);
  }
  function bimRvFail(e){
    var R=A3D_RV,s=String(e&&e.message||e);
    R.on=false;R.err=s;
    console.warn('[BIM] Rendered view stopped: '+s,e);
    a3dToast('The rendered view stopped: '+s+'. The shaded view is back.');
    bimRvDrop();
    setTimeout(function(){if(A3D.on)paint();refreshProps();},0);
  }
  function bimRvEnsure(){
    var R=A3D_RV,cv;
    if(R.cv&&!R.cv.parentNode)bimRvDrop();   /* the view was rebuilt under it */
    if(R.core)return R.core;
    cv=bimRvCanvas();
    if(!cv)return null;
    R.core=bimRvCore(R.T,cv,{light:bimRvLightDevice()});
    R.info=R.core.stats();
    return R.core;
  }
  /* everything the picture depends on, in one string: a paint that changes none of it adds no work */
  function bimRvSig(cam,sun,sky,st,plan,wD,hD,reach,groundAt,ground){
    var s=[wD,hD,ground?1:0,st.edges?1:0,sky.n,sun.up?1:0,Math.round(reach*100),Math.round(groundAt*1000)],i;
    for(i=0;i<16;i++)s.push(Math.round(cam.world[i]*1e4));
    for(i=0;i<16;i++)s.push(Math.round(cam.proj[i]*1e5));
    for(i=0;i<3;i++)s.push(Math.round(sun.dir[i]*1e4));
    for(i=0;i<plan.items.length;i++)s.push(plan.items[i].key+'='+plan.items[i].sig);
    return s.join(',');
  }
  /* the frame, when the view is on and ready: true when the picture is what is seen */
  function bimRvRender(V,W,H){
    var R=A3D_RV;
    R.drew=false;
    if(!R.on||R.st!=='ready'||R.hold||(A3D_BENCH&&A3D_BENCH.running))return false;
    try{
      var core=bimRvEnsure();
      if(!core)return false;
      var st=bimRvSettings(),gs=cvScale(el.cv),wD=Math.max(1,Math.round(W*gs)),hD=Math.max(1,Math.round(H*gs)),
        sun=bimRvSun(),sky=bimRvSkyFor(st.sky,sun.up,sun.elev),
        plan=bimRvPlan(st.edges,{V:V,W:W,H:H,bg:sky.plain?'#f4f4f2':'#cbc6bb'}),cam=bimRvCamera(V,W,H,A3D.flat,A3D.cam.dist),   /* __acad3dV198: the map's ground colour */reach=bimRvReach(A3D.cam.dist,plan.box),groundAt=bimShadowGround(),
        ground=st.ground&&!plan.terrains,   /* a terrain is the ground */
        sig=bimRvSig(cam,sun,sky,st,plan,wD,hD,reach,groundAt,ground);
      R.sun=sun;R.sky=sky;
      if(sig!==R.sig){
        core.size(wD,hD);
        core.scene(plan.items,function(it){return bimRvBuild(plan,it);});
        core.begin({world:cam.world,proj:cam.proj,focus:[A3D.cam.tx||0,A3D.cam.ty||0,A3D.cam.tz||0],reach:reach,
          sun:sun.up?sun.dir:null,sky:sky,ground:ground,groundAt:groundAt,edges:st.edges});
        R.done=core.pass();
        core.show();
        R.sig=sig;R.want=BIM_RV_QUALITY[st.quality]||BIM_RV_QUALITY.good;
        R.stillAt=performance.now()+BIM_RV_STILL_MS;R.last=0;
      }
      R.drew=true;
      if(R.done<R.want&&!R.raf)R.raf=requestAnimationFrame(bimRvRefine);
      bimSceneFrameDone(plan.S,'rendered');
      A3D.glFaces=plan.totalFaces;
      return true;
    }catch(eR){bimRvFail(eR);return false;}
  }
  /* passes added while the view is still: more a frame while the frames come on time, fewer when they come late */
  function bimRvRefine(t){
    var R=A3D_RV,n,i;
    R.raf=0;
    if(!R.on||!R.core||!R.drew||R.done>=R.want)return;
    if(performance.now()<R.stillAt){R.raf=requestAnimationFrame(bimRvRefine);return;}
    if(R.last){if(t-R.last<22)R.per=Math.min(8,R.per+1);else if(t-R.last>40)R.per=Math.max(1,R.per>>1);}
    R.last=t;
    try{
      n=Math.min(R.per,R.want-R.done);
      for(i=0;i<n;i++)R.done=R.core.pass();
      R.core.show();
    }catch(eP){bimRvFail(eP);return;}
    if(R.done<R.want)R.raf=requestAnimationFrame(bimRvRefine);
    else{R.last=0;bimRvTell();}
  }
  /* the view's state in words, for Properties */
  function bimRvStateText(){
    var R=A3D_RV;
    if(R.st==='loading')return 'Loading three.js (about 750 KB, once)';
    if(R.st==='failed')return 'Could not start: '+R.err;
    if(!R.on)return 'Off';
    if(!R.drew)return 'Not drawn here: Presentation and sheets are drawn in 2D';
    return (R.done<R.want?R.done+' of '+R.want+' passes':R.want+' passes')+'; lit by '+(R.sun?R.sun.text:'the sun');
  }
  /* Properties' line brought up to date without redrawing the panel */
  function bimRvTell(){
    var e=document.querySelector('[data-rvstate]');
    if(e)e.textContent=bimRvStateText();
  }
  /* the view turned on or off; a promise of whether it is on */
  function bimRvSetOn(on){
    var R=A3D_RV;
    if(!on){
      R.on=false;R.drew=false;R.sig='';
      if(R.raf){cancelAnimationFrame(R.raf);R.raf=0;}
      if(A3D.on)paint();
      refreshProps();
      return Promise.resolve(false);
    }
    if(!A3D.on){a3dToast('Open the model (3D) first');return Promise.resolve(false);}
    R.on=true;R.sig='';
    if(R.st!=='ready')a3dToast('Rendered view: loading three.js (about 750 KB, once)');
    refreshProps();
    return bimRvLoad().then(function(){
      if(!R.on)return false;
      paint();
      refreshProps();
      if(R.on&&R.drew)a3dToast('Rendered view: lit by '+R.sun.text+'. RENDER again for the shaded view.');
      else if(R.on)a3dToast('Rendered view on: Presentation and sheets are still drawn in 2D');
      return R.on;
    },function(e){
      R.on=false;
      console.warn('[BIM] Rendered view: '+String(e&&e.message||e));
      a3dToast('The rendered view could not start: '+String(e&&e.message||e));
      if(A3D.on)paint();
      refreshProps();
      return false;
    });
  }
  function bimRvCommand(){
    if(A3D_RV.on){bimRvSetOn(false);a3dToast('Shaded view');return;}
    bimRvSetOn(true);
  }
  /* Properties > View: the display, and the rendered view's settings while it is on */
  function bimRvProp(mk,mv){
    if(mk==='rendered'){bimRvSetOn(mv==='1');return true;}
    if(mk==='rvsky')return bimRvSetting('sky',mv);
    if(mk==='rvquality')return bimRvSetting('quality',mv);
    if(mk==='rvground')return bimRvSetting('ground',mv);
    if(mk==='rvedges')return bimRvSetting('edges',mv);
    return false;
  }
  function bimRvPropsHtml(){
    var R=A3D_RV,s=bimRvSettings(),h,k,o='';
    function two(key,on,a,b){
      return '<select data-propmodel="'+key+'"><option value="1"'+(on?' selected':'')+'>'+a+'</option><option value="0"'+(on?'':' selected')+'>'+b+'</option></select>';
    }
    h=bimPropRow('Display','<select data-propmodel="rendered"><option value="0"'+(R.on?'':' selected')+'>Shaded</option>'+
      '<option value="1"'+(R.on?' selected':'')+'>Rendered</option></select>');
    if(!R.on)return h;
    for(k in BIM_RV_SKIES)if(BIM_RV_SKIES.hasOwnProperty(k))o+='<option value="'+k+'"'+(s.sky===k?' selected':'')+'>'+bimEsc(BIM_RV_SKIES[k].n)+'</option>';
    h+=bimPropRow('Sky','<select data-propmodel="rvsky">'+o+'</select>');
    o='';
    for(k in BIM_RV_QUALITY_NAMES)if(BIM_RV_QUALITY_NAMES.hasOwnProperty(k))o+='<option value="'+k+'"'+(s.quality===k?' selected':'')+'>'+bimEsc(BIM_RV_QUALITY_NAMES[k])+'</option>';
    h+=bimPropRow('Quality','<select data-propmodel="rvquality">'+o+'</select>');
    h+=bimPropRow('Ground',two('rvground',s.ground,'Shown','Hidden'));
    h+=bimPropRow('Edges',two('rvedges',s.edges,'Shown','Hidden'));
    h+=bimPropRow('Rendered','<span class="a3d-pstatic" data-rvstate="1">'+bimEsc(bimRvStateText())+'</span>');
    return h;
  }
  /* Statistics' Graphics line while the picture is what is seen */
  function bimRvLabel(){
    return 'Rendered (three.js r'+(A3D_RV.T?A3D_RV.T.REVISION:'')+')';
  }
export {
  A3D_RV, BIM_RV_FILE, BIM_RV_KEY, BIM_RV_SRI, BIM_RV_VER, bimRvCommand, bimRvDrop, bimRvLabel, bimRvLoad,
  bimRvProp, bimRvPropsHtml, bimRvRender, bimRvSetOn, bimRvSetting, bimRvSettings, bimRvSources,
  bimRvStateText
};
