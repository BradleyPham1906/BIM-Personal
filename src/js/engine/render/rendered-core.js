import { bimRvMapCanvas } from './rendered-map.js';


  /* ================= __acad3dV194: the rendered view, its picture =================
     docs/research/research-rendered-view.md. A picture of the model in daylight: materials, the sun and the sky's
     light, soft shadows and the shading of corners, drawn by three.js (MIT, runtime/three, loaded when the view is
     first asked for: the zero-dependency contract's second written exception, the owner, 2026-11-11).

     The method is BimCraft's fast render (github.com/getcadcraft/bimcraft, app/render/render-core.js and looks.js at
     commit cfbd948, Apache-2.0, Copyright 2026 The Data Design Group, Inc.; THIRD_PARTY_NOTICES.md), rewritten in ES5
     for this engine and made to refine a live view instead of rendering a still: the picture is the average of many
     passes, each with the camera moved by less than a pixel (smooth edges), the sun moved inside a small cone (soft
     shadow edges) and a second, shadow-casting light moved over the sky, cosine-weighted (soft contact shadows: the
     ambient occlusion of daylight). The first pass is shown at once; the rest are added while the view is still.
     Changed from BimCraft: one pass per call and the caller decides when; vertex colours instead of a material a
     colour; every face is shaded flat, its normal taken from the picture itself, both faces cast shadows and the bias
     is by depth only, because this app's faces are not wound one way; the first pass, the one seen while the view
     moves, has no shadows from the sky (a single direction of it stripes the walls it grazes); the shadows' box
     follows what the camera looks at, not the whole model; the ground and the sky follow it too.

     This file knows nothing of the app's model: bimRvCore takes three.js, a canvas and plain arrays. */
  var BIM_RV_SKIES={
    clear:{n:'Clear sky',zenith:'#2f6cb3',horizon:'#c4d6e8',ground:'#8f8a80',sun:3.2,sky:1.6,env:0.45,tint:'#fff4e5',skyTint:'#dfeaff'},
    overcast:{n:'Overcast',zenith:'#b9c0c8',horizon:'#dfe2e5',ground:'#8a8781',sun:0.35,sky:3.0,env:0.8,tint:'#f4f2ee',skyTint:'#eef0f3'},
    dusk:{n:'Low sun',zenith:'#3d4f78',horizon:'#e9b48a',ground:'#5d5650',sun:2.2,sky:0.9,env:0.35,tint:'#ffb877',skyTint:'#b9c4e6'},
    white:{n:'White studio',zenith:'#ffffff',horizon:'#ffffff',ground:'#f2f2f2',sun:2.6,sky:2.0,env:0.7,tint:'#fffaf2',skyTint:'#f4f7ff',plain:true}
  };
  /* the sky once the sun is down, under any sky but the white studio. BimCraft's night is lit by the model's lamps and
     is black without them; this app has no lamps yet, so its night is a dim blue light the model can be read in. */
  var BIM_RV_NIGHT={n:'Night',zenith:'#16213f',horizon:'#34425f',ground:'#22262e',sun:0,sky:1.1,env:0.5,tint:'#ffffff',skyTint:'#a8b9de',night:true};
  /* passes a picture is the average of */
  var BIM_RV_QUALITY={draft:16,good:64,best:256};
  var BIM_RV_QUALITY_NAMES={draft:'Draft (16 passes)',good:'Good (64 passes)',best:'Best (256 passes)'};
  /* the low-discrepancy sequence every pass is placed by: the same view gives the same picture */
  function bimRvHalton(i,b){
    var f=1,r=0;
    while(i>0){f/=b;r+=f*(i%b);i=Math.floor(i/b);}
    return r;
  }
  function bimRvUnit(v){var l=Math.sqrt(v[0]*v[0]+v[1]*v[1]+v[2]*v[2])||1;return [v[0]/l,v[1]/l,v[2]/l];}
  function bimRvCross(a,b){return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];}
  /* two unit vectors square to a direction */
  function bimRvBasis(up){
    var u=bimRvUnit(up),ax=Math.abs(u[2])<0.9?[0,0,1]:[1,0,0],e1=bimRvUnit(bimRvCross(u,ax));
    return {up:u,e1:e1,e2:bimRvCross(u,e1)};
  }
  /* pass i's light from the sky: cosine-weighted over the hemisphere about up, kept off the horizon */
  function bimRvHemisphere(i,up){
    var B=bimRvBasis(up),r=Math.sqrt(Math.min(0.97,bimRvHalton(i+1,11))),a=2*Math.PI*bimRvHalton(i+1,13),z=Math.sqrt(1-r*r),
      x=r*Math.cos(a),y=r*Math.sin(a);
    return bimRvUnit([B.e1[0]*x+B.e2[0]*y+B.up[0]*z,B.e1[1]*x+B.e2[1]*y+B.up[1]*z,B.e1[2]*x+B.e2[2]*y+B.up[2]*z]);
  }
  /* pass i's sun: a direction inside a cone of the given half angle about the sun's (the sun is half a degree across;
     wider is softer) */
  function bimRvSunDisc(dir,i,degrees){
    var B=bimRvBasis(dir),r=Math.sqrt(bimRvHalton(i+1,5))*Math.tan((degrees||1.5)*Math.PI/180),a=2*Math.PI*bimRvHalton(i+1,7),
      x=r*Math.cos(a),y=r*Math.sin(a);
    return bimRvUnit([B.up[0]+B.e1[0]*x+B.e2[0]*y,B.up[1]+B.e1[1]*x+B.e2[1]*y,B.up[2]+B.e1[2]*x+B.e2[2]*y]);
  }
  /* a projection with its far plane moved out and its near plane kept (so the ground reaches the horizon);
     column-major, perspective with [11] = -1, parallel with [15] = 1 */
  function bimRvFarPlane(proj,far){
    var e=[],i,n,f,fn,sum;
    for(i=0;i<16;i++)e.push(proj[i]);
    if(e[15]===1&&e[11]===0){
      fn=-2/e[10];sum=-e[14]*fn;n=(sum-fn)/2;f=Math.max(far,n+fn);
      e[10]=-2/(f-n);e[14]=-(f+n)/(f-n);
      return e;
    }
    n=e[14]/(e[10]-1);f=Math.max(far,e[14]/(e[10]+1));
    e[10]=(f+n)/(n-f);e[14]=2*f*n/(n-f);
    return e;
  }
  /* a pass's projection: the camera moved by (jx, jy) of the picture's half size, for either projection */
  function bimRvJitter(proj,jx,jy){
    var e=[],k;
    for(k=0;k<16;k++)e.push(proj[k]);
    for(k=0;k<4;k++){e[k*4]+=jx*e[k*4+3];e[k*4+1]+=jy*e[k*4+3];}
    return e;
  }
  /* the sky a picture takes: the one chosen; night once the sun is down; the low sun's colours while it is under
     eight degrees in a clear sky */
  function bimRvSkyFor(key,sunUp,elev){
    var S=BIM_RV_SKIES.hasOwnProperty(key)?BIM_RV_SKIES[key]:BIM_RV_SKIES.clear;
    if(S.plain)return S;
    if(!sunUp)return BIM_RV_NIGHT;
    if(S===BIM_RV_SKIES.clear&&typeof elev==='number'&&elev<8)return BIM_RV_SKIES.dusk;
    return S;
  }
  /* The picture. T is three.js; the canvas is drawn on. Returns
       size(w,h)           the picture's size in device pixels
       scene(items,build)  the model brought in line with items [{key,sig}]: build(item) is asked for the arrays of an
                           item that is new or whose sig changed, {op,tr,ed}: opaque and see-through triangles
                           {pos,col,n} (world positions and linear colours; see-through ones with alpha) and
                           edges {pos,n}, any of them absent or empty
       begin(spec)         a new picture: {world,proj (the camera, column-major), focus [x,y,z], reach (m), sun
                           [x,y,z] toward it or null, sky (a BIM_RV_SKIES row), ground (true or false), groundAt (m),
                           edges (true or false)}
       pass()              one more pass added; the count
       show()              the average so far, on the canvas
       stats(), dispose() */
  function bimRvCore(T,canvas,opts){
    opts=opts||{};
    var renderer=new T.WebGLRenderer({canvas:canvas,antialias:false,alpha:false,preserveDrawingBuffer:true,powerPreference:'high-performance'});
    var X=renderer.extensions,half=X.has('EXT_color_buffer_half_float')||X.has('EXT_color_buffer_float');
    if(!half){renderer.dispose();throw new Error('this device cannot keep a picture brighter than white (no half-float targets)');}
    var accType=(X.has('EXT_color_buffer_float')&&X.has('EXT_float_blend'))?T.FloatType:T.HalfFloatType;
    renderer.setPixelRatio(1);
    renderer.shadowMap.enabled=true;
    renderer.shadowMap.type=T.PCFShadowMap;   /* the softness comes from the passes, not the filter */
    renderer.toneMapping=T.ACESFilmicToneMapping;
    renderer.toneMappingExposure=1;
    renderer.outputColorSpace=T.SRGBColorSpace;
    var SM=Math.min(opts.light?2048:4096,renderer.capabilities.maxTextureSize||2048);
    var scene=new T.Scene(),recs={},w=0,h=0,done=0,passRT=null,accRT=null;
    var matO=new T.MeshStandardMaterial({vertexColors:true,flatShading:true,roughness:0.78,metalness:0,side:T.DoubleSide,fog:false});
    var matT=new T.MeshStandardMaterial({vertexColors:true,flatShading:true,roughness:0.06,metalness:0,side:T.DoubleSide,fog:false,transparent:true,depthWrite:false,envMapIntensity:1.4});
    var matE=new T.LineBasicMaterial({color:0x2a2f36,transparent:true,opacity:0.55,fog:false});
    /* the lights: the sun, and the sky sampled a direction a pass */
    var sunL=new T.DirectionalLight(0xffffff,0),skyL=new T.DirectionalLight(0xffffff,0);
    [sunL,skyL].forEach(function(L){
      L.castShadow=true;L.shadow.mapSize.set(SM,SM);L.shadow.normalBias=0;
      scene.add(L);scene.add(L.target);
    });
    /* the sky: a dome graded from the horizon to the zenith, seen behind the model and, filtered, lighting it */
    function skyDome(sky){
      var mat=new T.ShaderMaterial({side:T.BackSide,depthWrite:false,
        uniforms:{zen:{value:new T.Color(sky.zenith)},hor:{value:new T.Color(sky.horizon)},gnd:{value:new T.Color(sky.ground)}},
        vertexShader:'varying vec3 vDir; void main(){ vDir=normalize(position); gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0); }',
        fragmentShader:'uniform vec3 zen; uniform vec3 hor; uniform vec3 gnd; varying vec3 vDir;\n'+
          'void main(){ float z=normalize(vDir).y; vec3 c=z>=0.0?mix(hor,zen,pow(z,0.6)):mix(hor,gnd,pow(-z,0.4)); gl_FragColor=vec4(c,1.0); }'});
      var m=new T.Mesh(new T.SphereGeometry(1,48,24),mat);
      m.frustumCulled=false;
      return m;
    }
    var pm=new T.PMREMGenerator(renderer),dome=null,env=null,skyNow=null;
    var groundMat=new T.MeshStandardMaterial({color:0xcbc6bb,roughness:1,metalness:0,fog:true});
    var ground=new T.Mesh(new T.CircleGeometry(1,96),groundMat);
    ground.quaternion.setFromUnitVectors(new T.Vector3(0,0,1),new T.Vector3(0,1,0));
    ground.receiveShadow=true;
    ground.renderOrder=-2;   /* __acad3dV198: the sky, the ground, the map on it, then the model */
    scene.add(ground);
    function setSky(sky){
      if(sky===skyNow)return;
      if(dome){scene.remove(dome);dome.geometry.dispose();dome.material.dispose();}
      if(env)env.dispose();
      dome=skyDome(sky);dome.renderOrder=-3;scene.add(dome);
      var s2=new T.Scene(),d2=skyDome(sky);
      s2.add(d2);
      env=pm.fromScene(s2,0,0.1,100);
      d2.geometry.dispose();d2.material.dispose();
      scene.environment=env.texture;scene.environmentIntensity=sky.env;
      scene.fog=new T.Fog(new T.Color(sky.horizon),10,1000);   /* only the ground fogs: the materials say fog: false */
      groundMat.color.set(sky.plain?'#f4f4f2':'#cbc6bb');
      groundMat.fog=!sky.plain;groundMat.needsUpdate=true;
      sunL.color.set(sky.tint);skyL.color.set(sky.skyTint);
      skyNow=sky;
    }
    /* the two targets a picture is kept in, and the square that adds a pass and shows the average */
    var cam=new T.Camera();
    cam.matrixAutoUpdate=false;
    var quadVS='varying vec2 vUv; void main(){ vUv=uv; gl_Position=vec4(position.xy,0.0,1.0); }';
    var addMat=new T.ShaderMaterial({uniforms:{map:{value:null}},vertexShader:quadVS,
      fragmentShader:'uniform sampler2D map; varying vec2 vUv; void main(){ gl_FragColor=vec4(texture2D(map,vUv).rgb,1.0); }',
      blending:T.AdditiveBlending,depthTest:false,depthWrite:false,toneMapped:false});
    var outMat=new T.ShaderMaterial({uniforms:{map:{value:null},k:{value:1}},vertexShader:quadVS,
      fragmentShader:'uniform sampler2D map; uniform float k; varying vec2 vUv; void main(){ gl_FragColor=vec4(texture2D(map,vUv).rgb*k,1.0);\n#include <tonemapping_fragment>\n#include <colorspace_fragment>\n}',
      depthTest:false,depthWrite:false,toneMapped:true});
    var quad=new T.Mesh(new T.PlaneGeometry(2,2),addMat),quadScene=new T.Scene(),ortho=new T.OrthographicCamera(-1,1,1,-1,0,1);
    quadScene.add(quad);
    function size(nw,nh){
      nw=Math.max(1,Math.round(nw));nh=Math.max(1,Math.round(nh));
      if(nw===w&&nh===h&&passRT)return;
      w=nw;h=nh;
      renderer.setSize(w,h,false);
      if(passRT){passRT.dispose();accRT.dispose();}
      passRT=new T.WebGLRenderTarget(w,h,{type:T.HalfFloatType,colorSpace:T.LinearSRGBColorSpace,depthBuffer:true,samples:opts.light?0:4});
      accRT=new T.WebGLRenderTarget(w,h,{type:accType,colorSpace:T.LinearSRGBColorSpace,depthBuffer:false});
      addMat.uniforms.map.value=passRT.texture;outMat.uniforms.map.value=accRT.texture;
      done=0;
    }
    /* the model: a mesh for a part's opaque triangles, one for its see-through ones, a line set for its edges */
    function drop(rec){
      rec.objs.forEach(function(o){scene.remove(o);o.geometry.dispose();});
      (rec.own||[]).forEach(function(x){x.dispose();});   /* __acad3dV198: a map's material and its picture */
    }
    /* __acad3dV198: a surface with the map on it: its atlas as a texture, lit like the ground. On the ground, drawn
       after the ground and before the model, neither testing nor writing depth, as the shaded view draws it, so
       neither the ground under it nor anything standing on it fights it at a low angle; draped, a surface like any other */
    var MAXTEX=Math.min(opts.light?2048:4096,renderer.capabilities.maxTextureSize||2048),ANISO=renderer.capabilities.getMaxAnisotropy();
    function mapMesh(a,rec){
      var tex=new T.CanvasTexture(bimRvMapCanvas(a.atlas,MAXTEX)),g=new T.BufferGeometry(),mat,m;
      tex.colorSpace=T.SRGBColorSpace;tex.flipY=false;tex.anisotropy=ANISO;tex.needsUpdate=true;
      g.setAttribute('position',new T.BufferAttribute(a.pos,3));
      g.setAttribute('uv',new T.BufferAttribute(a.uv,2));
      g.computeBoundingSphere();
      mat=new T.MeshStandardMaterial({map:tex,flatShading:true,roughness:a.flat?1:0.78,metalness:0,side:T.DoubleSide,fog:false,depthWrite:!a.flat,depthTest:!a.flat});
      m=new T.Mesh(g,mat);
      m.receiveShadow=true;m.castShadow=!a.flat;
      if(a.flat)m.renderOrder=-1;
      rec.own.push(mat,tex);
      return m;
    }
    function geo(a,colSize){
      var g=new T.BufferGeometry();
      g.setAttribute('position',new T.BufferAttribute(a.pos,3));
      if(a.col)g.setAttribute('color',new T.BufferAttribute(a.col,colSize));
      g.computeBoundingSphere();
      return g;
    }
    function make(it,A){
      var rec={sig:it.sig,objs:[],edges:[],own:[]},m;
      if(A&&A.map&&A.map.n)rec.objs.push(mapMesh(A.map,rec));   /* __acad3dV198 */
      if(A&&A.op&&A.op.n){m=new T.Mesh(geo(A.op,3),matO);m.castShadow=true;m.receiveShadow=true;rec.objs.push(m);}
      if(A&&A.tr&&A.tr.n){m=new T.Mesh(geo(A.tr,4),matT);m.castShadow=false;m.receiveShadow=true;m.renderOrder=1;rec.objs.push(m);}
      if(A&&A.ed&&A.ed.n){m=new T.LineSegments(geo(A.ed,0),matE);m.castShadow=false;m.receiveShadow=false;rec.objs.push(m);rec.edges.push(m);}
      rec.objs.forEach(function(o){o.matrixAutoUpdate=false;scene.add(o);});
      return rec;
    }
    function setScene(items,build){
      var seen={},i,it,k,n=0;
      for(i=0;i<items.length;i++){
        it=items[i];seen[it.key]=1;
        if(recs[it.key]&&recs[it.key].sig===it.sig)continue;
        if(recs[it.key])drop(recs[it.key]);
        recs[it.key]=make(it,build(it));n++;
      }
      for(k in recs)if(recs.hasOwnProperty(k)&&!seen[k]){drop(recs[k]);delete recs[k];n++;}
      return n;
    }
    /* a new picture */
    var S=null,P0=null,UP=[0,1,0];
    function place(L,d){
      var c=S.focus,R=S.reach;
      L.position.set(c[0]+d[0]*R*4,c[1]+d[1]*R*4,c[2]+d[2]*R*4);
      /* the shadow camera's own up must not run along the light (the sun overhead) */
      if(Math.abs(d[0])<Math.abs(d[2]))L.shadow.camera.up.set(1,0,0);else L.shadow.camera.up.set(0,0,-1);
    }
    function begin(spec){
      S=spec;
      var c=S.focus,R=S.reach,sky=S.sky||BIM_RV_SKIES.clear,sunOn=!!S.sun&&S.sun[1]>0.02&&sky.sun>0,k,SKY_R=R*150;
      setSky(sky);
      S.sunOn=sunOn;
      sunL.intensity=sunOn?sky.sun:0;sunL.castShadow=sunOn;sunL.visible=sunOn;
      skyL.intensity=sky.sky*((sunOn||sky.night)?1:1.35);
      [sunL,skyL].forEach(function(L){
        var sc=L.shadow.camera;
        sc.left=-R*1.6;sc.right=R*1.6;sc.top=R*1.6;sc.bottom=-R*1.6;sc.near=R*0.05;sc.far=R*8;
        sc.updateProjectionMatrix();
        L.shadow.bias=-0.0002*(4096/SM);
        L.target.position.set(c[0],c[1],c[2]);L.target.updateMatrixWorld();
      });
      dome.scale.setScalar(SKY_R);dome.position.set(c[0],c[1],c[2]);dome.updateMatrixWorld();
      scene.fog.near=R*10;scene.fog.far=R*120;
      ground.visible=!!S.ground;
      ground.scale.setScalar(SKY_R*0.98);
      ground.position.set(c[0],(S.groundAt||0)-R*1e-4,c[2]);
      for(k in recs)if(recs.hasOwnProperty(k))recs[k].edges.forEach(function(o){o.visible=!!S.edges;});
      cam.matrix.fromArray(S.world);cam.matrixWorld.fromArray(S.world);cam.matrixWorldInverse.copy(cam.matrixWorld).invert();
      P0=bimRvFarPlane(S.proj,R*200);
      done=0;
      renderer.setRenderTarget(accRT);renderer.setClearColor(0x000000,1);renderer.clear();
      renderer.setRenderTarget(null);
    }
    function pass(){
      var i=done,a=bimRvHalton(i+1,2),b=bimRvHalton(i+1,3);
      cam.projectionMatrix.fromArray(bimRvJitter(P0,(a-0.5)*2/w,(b-0.5)*2/h));
      cam.projectionMatrixInverse.copy(cam.projectionMatrix).invert();
      if(S.sunOn)place(sunL,bimRvSunDisc(S.sun,i,1.5));
      place(skyL,bimRvHemisphere(i,UP));
      skyL.castShadow=i>0;
      renderer.setRenderTarget(passRT);
      renderer.render(scene,cam);
      quad.material=addMat;
      renderer.setRenderTarget(accRT);
      renderer.autoClear=false;
      renderer.render(quadScene,ortho);
      renderer.autoClear=true;
      renderer.setRenderTarget(null);
      done=i+1;
      return done;
    }
    function show(){
      outMat.uniforms.k.value=1/Math.max(1,done);
      quad.material=outMat;
      renderer.setRenderTarget(null);
      renderer.render(quadScene,ortho);
    }
    function dispose(){
      var k;
      for(k in recs)if(recs.hasOwnProperty(k))drop(recs[k]);
      recs={};
      if(dome){dome.geometry.dispose();dome.material.dispose();}
      if(env)env.dispose();
      pm.dispose();
      if(passRT){passRT.dispose();accRT.dispose();}
      [matO,matT,matE,groundMat,addMat,outMat].forEach(function(m){m.dispose();});
      ground.geometry.dispose();quad.geometry.dispose();
      renderer.dispose();
      if(renderer.forceContextLoss)renderer.forceContextLoss();
    }
    function stats(){
      var dbg=X.get('WEBGL_debug_renderer_info'),g=renderer.getContext(),n=0,k;
      for(k in recs)if(recs.hasOwnProperty(k))n+=recs[k].objs.length;
      return {done:done,w:w,h:h,meshes:n,shadowMap:SM,float32:accType===T.FloatType,
        gpu:String(dbg?g.getParameter(dbg.UNMASKED_RENDERER_WEBGL):g.getParameter(g.RENDERER)||'')};
    }
    return {size:size,scene:setScene,begin:begin,pass:pass,show:show,stats:stats,dispose:dispose,three:scene};
  }
export {
  BIM_RV_NIGHT, BIM_RV_QUALITY, BIM_RV_QUALITY_NAMES, BIM_RV_SKIES, bimRvBasis, bimRvCore, bimRvCross,
  bimRvFarPlane, bimRvHalton, bimRvHemisphere, bimRvJitter, bimRvSkyFor, bimRvSunDisc, bimRvUnit
};
