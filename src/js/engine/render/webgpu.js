  /* ================= __acad3dV153: the WebGPU engine =================
     Where the browser has WebGPU the model is drawn with it, from the same description: the
     chunks as vertex buffers, the table as a storage buffer, and every draw recorded once in a
     render bundle that each frame replays, with only the camera's two matrices sent. The bundle
     is recorded again only when a chunk is rebuilt, the table grows, or the passes change.
     WebGPU starts asynchronously, so WebGL draws until it is ready, and takes over again if the
     device is lost, if the person chooses WebGL (GRAPHICS), or for a frame with the map or a
     terrain surface, which WebGPU does not draw yet. */
  var A3D_GPU={state:'off',why:'',device:null,ctx:null,cv:null,format:'',tab:null,tabCap:0,bundle:null,bkey:'',bdraws:0,w:0,h:0,
    pipes:null,ubuf:null,bg:null,depth:null,msaa:null,off:null,offscreen:!!(typeof window!=='undefined'&&window.__BIM_GPU_OFFSCREEN),engine:'',fallback:''};   /* offscreen: set before the page loads, by a test */
  var BIM_GPU_KEY='acad3dGraphics';
  var BIM_GPU_WGSL=
    'struct U{view:mat4x4f,proj:mat4x4f,light:vec4f,eye:vec4f};\n'+
    '@group(0) @binding(0) var<uniform> u:U;\n'+
    '@group(0) @binding(1) var<storage,read> tab:array<vec4f>;\n'+
    'override PASS:f32=0.0;override EDGE:f32=0.0;\n'+
    'struct VO{@builtin(position) p:vec4f,@location(0) n:vec3f,@location(1) c:vec4f,@location(2) boost:f32};\n'+
    'fn place(pos:vec3f,obj:f32,n:vec3f)->VO{\n'+
    ' var o:VO;let s=u32(obj+0.5)*2u;let a=tab[s];let b=tab[s+1u];let tr=a.w<0.999;\n'+
    ' if(a.w<0.0||(PASS<0.5&&tr)||(PASS>0.5&&!tr)){o.p=vec4f(2.0,2.0,2.0,1.0);o.n=vec3f(0.0,1.0,0.0);o.c=vec4f(0.0);o.boost=0.0;return o;}\n'+
    ' o.n=n;o.boost=0.0;\n'+
    ' if(EDGE>0.5){var ec=vec3f(0.09,0.10,0.11);if(b.w>1.5){ec=vec3f(1.0,0.706,0.329);}else if(b.w>0.5){ec=vec3f(0.306,0.631,1.0);}o.c=vec4f(ec,a.w);}\n'+
    ' else{o.c=vec4f(b.xyz,a.w);if(b.w>0.5&&b.w<1.5){o.boost=0.25;}}\n'+
    ' var w=pos+a.xyz;if(EDGE>0.5){w=w+(u.eye.xyz-w)*'+BIM_EDGE_PULL.toFixed(6)+';}\n'+   /* __acad3dV154 */
    ' var p=u.proj*u.view*vec4f(w,1.0);p.z=(p.z+p.w)*0.5;o.p=p;return o;}\n'+   /* WebGL's depth is -1..1, WebGPU's 0..1 */
    '@vertex fn vsFace(@location(0) pos:vec3f,@location(1) n:vec3f,@location(2) obj:f32)->VO{return place(pos,obj,n);}\n'+
    '@vertex fn vsEdge(@location(0) pos:vec3f,@location(2) obj:f32)->VO{return place(pos,obj,vec3f(0.0,1.0,0.0));}\n'+
    '@fragment fn fsFace(i:VO)->@location(0) vec4f{var k=0.45+0.55*abs(dot(normalize(i.n),u.light.xyz));k=min(1.35,k+i.boost);\n'+
    ' return vec4f(clamp(i.c.rgb*k,vec3f(0.0),vec3f(1.0)),i.c.a);}\n'+
    '@fragment fn fsEdge(i:VO)->@location(0) vec4f{return i.c;}\n';
  /* __acad3dV154: the map and the terrain. Group 0: the camera, and this draw's values at an offset;
     group 1: a tile's sampler and texture. */
  var BIM_GPU_SITE_WGSL=
    'struct U{view:mat4x4f,proj:mat4x4f,light:vec4f,eye:vec4f};\n'+
    'struct M{color:vec4f,sub:vec4f,tile:vec4f};\n'+   /* color.a: the opacity; tile: offset x y, 1/scale, mode */
    '@group(0) @binding(0) var<uniform> u:U;\n'+
    '@group(0) @binding(1) var<uniform> m:M;\n'+
    '@group(1) @binding(0) var smp:sampler;\n'+
    '@group(1) @binding(1) var tx:texture_2d<f32>;\n'+
    'fn clip(p:vec4f)->vec4f{var q=p;q.z=(q.z+q.w)*0.5;return q;}\n'+
    'struct MO{@builtin(position) p:vec4f,@location(0) uv:vec2f};\n'+
    '@vertex fn vsMap(@location(0) pos:vec3f,@location(1) uv:vec2f)->MO{var o:MO;o.p=clip(u.proj*u.view*vec4f(pos,1.0));o.uv=uv;return o;}\n'+
    '@fragment fn fsMap(i:MO)->@location(0) vec4f{let c=textureSample(tx,smp,i.uv).rgb;return vec4f(mix(vec3f(0.114,0.125,0.141),c,m.color.a),1.0);}\n'+
    'struct TO{@builtin(position) p:vec4f,@location(0) uv:vec2f,@location(1) k:f32};\n'+
    '@vertex fn vsTer(@location(0) pos:vec3f,@location(1) n:vec3f,@location(2) mc:vec2f)->TO{var o:TO;\n'+
    ' o.uv=(mc-m.tile.xy)*m.tile.z;o.k=0.5+0.5*abs(dot(normalize(n),u.light.xyz));o.p=clip(u.proj*u.view*vec4f(pos,1.0));return o;}\n'+
    '@fragment fn fsTer(i:TO)->@location(0) vec4f{\n'+   /* sampled first: a texture is read in uniform control flow */
    ' let c=textureSample(tx,smp,m.sub.xy+clamp(i.uv,vec2f(0.0),vec2f(1.0))*(m.sub.zw-m.sub.xy)).rgb;\n'+
    ' if(m.tile.w<0.5){return vec4f(m.color.rgb*i.k,1.0);}\n'+
    ' if(i.uv.x<0.0||i.uv.x>1.0||i.uv.y<0.0||i.uv.y>1.0){discard;}\n'+
    ' return vec4f(mix(m.color.rgb*i.k,c*(0.62+0.38*i.k),m.color.a),1.0);}\n';
  /* a level of a tile's mipmap from the one above it: a 2x2 average, as generateMipmap */
  var BIM_GPU_MIP_WGSL=
    '@group(0) @binding(0) var s:sampler;\n'+
    '@group(0) @binding(1) var t:texture_2d<f32>;\n'+
    'struct O{@builtin(position) p:vec4f,@location(0) uv:vec2f};\n'+
    '@vertex fn vs(@builtin(vertex_index) i:u32)->O{var P=array<vec2f,3>(vec2f(-1.0,-1.0),vec2f(3.0,-1.0),vec2f(-1.0,3.0));\n'+
    ' var o:O;o.p=vec4f(P[i],0.0,1.0);o.uv=vec2f((P[i].x+1.0)*0.5,(1.0-P[i].y)*0.5);return o;}\n'+
    '@fragment fn fs(i:O)->@location(0) vec4f{return textureSample(t,s,i.uv);}\n';
  function bimGpuSitePipes(dev,fmt){
    var mod=dev.createShaderModule({code:BIM_GPU_SITE_WGSL});
    var g0=dev.createBindGroupLayout({entries:[
      {binding:0,visibility:GPUShaderStage.VERTEX|GPUShaderStage.FRAGMENT,buffer:{type:'uniform'}},
      {binding:1,visibility:GPUShaderStage.VERTEX|GPUShaderStage.FRAGMENT,buffer:{type:'uniform',hasDynamicOffset:true,minBindingSize:48}}]});
    var g1=dev.createBindGroupLayout({entries:[
      {binding:0,visibility:GPUShaderStage.FRAGMENT,sampler:{type:'filtering'}},
      {binding:1,visibility:GPUShaderStage.FRAGMENT,texture:{sampleType:'float'}}]});
    var lay=dev.createPipelineLayout({bindGroupLayouts:[g0,g1]});
    function pipe(map,write){
      return dev.createRenderPipeline({layout:lay,
        vertex:{module:mod,entryPoint:map?'vsMap':'vsTer',buffers:[map?
          {arrayStride:20,attributes:[{shaderLocation:0,offset:0,format:'float32x3'},{shaderLocation:1,offset:12,format:'float32x2'}]}:
          {arrayStride:32,attributes:[{shaderLocation:0,offset:0,format:'float32x3'},{shaderLocation:1,offset:12,format:'float32x3'},{shaderLocation:2,offset:24,format:'float32x2'}]}]},
        fragment:{module:mod,entryPoint:map?'fsMap':'fsTer',targets:[{format:fmt}]},
        primitive:{topology:'triangle-list',cullMode:'none'},
        depthStencil:{format:'depth24plus',depthWriteEnabled:write,depthCompare:'less-equal'},
        multisample:{count:4}});
    }
    var mm=dev.createShaderModule({code:BIM_GPU_MIP_WGSL});
    var mip=dev.createRenderPipeline({layout:'auto',vertex:{module:mm,entryPoint:'vs'},fragment:{module:mm,entryPoint:'fs',targets:[{format:'rgba8unorm'}]},primitive:{topology:'triangle-list'}});
    var smp=dev.createSampler({magFilter:'linear',minFilter:'linear',mipmapFilter:'linear',addressModeU:'clamp-to-edge',addressModeV:'clamp-to-edge'});
    var dummy=dev.createTexture({size:[1,1],format:'rgba8unorm',usage:GPUTextureUsage.TEXTURE_BINDING|GPUTextureUsage.COPY_DST});
    return {map:pipe(true,false),ter:pipe(false,true),drape:pipe(false,false),mip:mip,g0:g0,g1:g1,smp:smp,
      dummyBg:dev.createBindGroup({layout:g1,entries:[{binding:0,resource:smp},{binding:1,resource:dummy.createView()}]}),dummy:dummy};
  }
  /* a tile's texture on this device, its mipmaps made here; null when the browser will not hand it over */
  function bimGpuTileTex(P,e){
    var dev=P.device,S=P.site;
    if(e.gtx&&e.gtx.dev===dev)return e.gtx;
    if(!e.img)return null;
    var w=e.img.naturalWidth||e.img.width,h=e.img.naturalHeight||e.img.height;
    if(!w||!h)return null;
    var pow2=!(w&(w-1))&&!(h&(h-1)),lv=pow2?Math.floor(Math.log(Math.max(w,h))/Math.LN2)+1:1,tex,l;
    tex=dev.createTexture({size:[w,h],format:'rgba8unorm',mipLevelCount:lv,usage:GPUTextureUsage.TEXTURE_BINDING|GPUTextureUsage.COPY_DST|GPUTextureUsage.RENDER_ATTACHMENT});
    try{dev.queue.copyExternalImageToTexture({source:e.img},{texture:tex},[w,h]);}
    catch(eT){   /* as bimMapTex: counted against its host, not drawn */
      tex.destroy();
      e.state='fail';A3D_MAP.fail[e.host]=(A3D_MAP.fail[e.host]||0)+1;
      return null;
    }
    if(lv>1){
      var enc=dev.createCommandEncoder();
      for(l=1;l<lv;l++){
        var bg=dev.createBindGroup({layout:S.mip.getBindGroupLayout(0),entries:[{binding:0,resource:S.smp},{binding:1,resource:tex.createView({baseMipLevel:l-1,mipLevelCount:1})}]});
        var ps=enc.beginRenderPass({colorAttachments:[{view:tex.createView({baseMipLevel:l,mipLevelCount:1}),loadOp:'clear',storeOp:'store',clearValue:{r:0,g:0,b:0,a:0}}]});
        ps.setPipeline(S.mip);ps.setBindGroup(0,bg);ps.draw(3);ps.end();
      }
      dev.queue.submit([enc.finish()]);
    }
    A3D_GPU.tileLive=(A3D_GPU.tileLive||0)+1;
    e.gtx={dev:dev,tex:tex,bg:dev.createBindGroup({layout:S.g1,entries:[{binding:0,resource:S.smp},{binding:1,resource:tex.createView()}]})};
    return e.gtx;
  }
  /* the frame's map and terrain, as bimMapDrawGl and bimTerrainDrawGl: what to draw, its values sent */
  function bimGpuSitePrepare(P,V,W,H){
    var dev=P.device,S=P.site,out={map:[],ter:[],mapVB:null,mapPrm:0,n:0},prm=[],i,j,o,c,s,tex,k,plan=null,srcs=[],drawn=0,verts=[];
    function put(col,a,sub,tile){prm.push(col[0],col[1],col[2],a,sub[0],sub[1],sub[2],sub[3],tile[0],tile[1],tile[2],tile[3]);return prm.length/12-1;}
    if(!A3D_PLOT.on){
      A3D_MAP.frame++;
      plan=bimMapPlan(V,W,H);
      if(plan.tiles.length){
        out.mapPrm=put([0,0,0],plan.opacity,[0,0,1,1],[0,0,1,0]);
        for(i=0;i<plan.tiles.length;i++){
          s=bimMapSource(plan.tiles[i],plan.tpl);tex=s?bimGpuTileTex(P,s.e):null;
          srcs.push(tex?s:null);
          if(!tex)continue;
          k=bimMapTileCorners(plan.tiles[i],plan.org,plan.ground-0.02);
          out.map.push({bg:tex.bg,first:verts.length/5});
          verts.push(k.nw[0],k.nw[1],k.nw[2],s.u0,s.v0, k.ne[0],k.ne[1],k.ne[2],s.u1,s.v0, k.se[0],k.se[1],k.se[2],s.u1,s.v1,
            k.nw[0],k.nw[1],k.nw[2],s.u0,s.v0, k.se[0],k.se[1],k.se[2],s.u1,s.v1, k.sw[0],k.sw[1],k.sw[2],s.u0,s.v1);
          drawn++;
        }
      }
      bimMapRecord('webgpu',plan,drawn,srcs);
      bimMapEvict();
    }
    A3D.lastTerrain3d=null;
    if(!A3D_PLOT.on&&!bimCameraIsPlan()){
      var list=[],org=bimMapOrigin(),tl=[],D,rec,col,sel,tiles;
      for(i=0;i<A3D.objs.length;i++){o=A3D.objs[i];if(o.t==='terrain'&&o.survey&&bimLayerShown(o)&&!bimTerrainSuperseded(o))list.push(o);}
      if(list.length){
        if(!plan)plan=bimMapPlan(V,W,H);
        for(i=0;i<list.length;i++){
          o=list[i];D=bimTerrainMeshData(o,org);
          if(!D)continue;
          rec=P.terBufs[o.id];
          if(!rec||rec.key!==D.key){
            if(rec)rec.vb.destroy();
            var iv=new Float32Array(D.count*8),q;
            for(q=0;q<D.count;q++){iv[q*8]=D.pos[q*3];iv[q*8+1]=D.pos[q*3+1];iv[q*8+2]=D.pos[q*3+2];iv[q*8+3]=D.nor[q*3];iv[q*8+4]=D.nor[q*3+1];iv[q*8+5]=D.nor[q*3+2];iv[q*8+6]=D.mer[q*2];iv[q*8+7]=D.mer[q*2+1];}
            rec=P.terBufs[o.id]={key:D.key,vb:bimGpuBuf(dev,iv,GPUBufferUsage.VERTEX)};
          }
          sel=(o.id===A3D.sel||(A3D.selSet&&A3D.selSet.indexOf(o.id)>=0));
          col=bimHexToRgb(sel?'#4ea1ff':(o.col||'#b08559'));
          out.ter.push({vb:rec.vb,count:D.count,prm:put(col,1,[0,0,1,1],[0,0,1,0]),bg:S.dummyBg,drape:false});
          c={id:o.id,triangles:D.count/3,tiles:[],drawn:0,z:null};
          if(plan.tiles.length&&D.ext){
            tiles=bimDrapeTiles(D.ext,plan.z,BIM_MAP_STYLES[plan.style].maxz);
            c.z=tiles.length?tiles[0].z:null;
            for(j=0;j<tiles.length;j++){
              s=bimMapSource(tiles[j],plan.tpl);tex=s?bimGpuTileTex(P,s.e):null;
              c.tiles.push({x:tiles[j].x,y:tiles[j].y,z:tiles[j].z,up:tex?s.up:null});
              if(!tex)continue;
              var sc=Math.pow(2,BIM_DRAPE_ZREF-tiles[j].z);
              out.ter.push({vb:rec.vb,count:D.count,prm:put(col,plan.opacity,[s.u0,s.v0,s.u1,s.v1],[tiles[j].x*sc-D.ox,tiles[j].y*sc-D.oy,1/sc,1]),bg:tex.bg,drape:true});
              c.drawn++;
            }
          }
          tl.push(c);
        }
        A3D.lastTerrain3d=tl;
      }
    }
    if(!prm.length)return out;
    /* the values, one 256-byte slot a draw (the offset a uniform buffer is read at) */
    var n=prm.length/12,pb=new Float32Array(n*64);
    for(i=0;i<n;i++)for(j=0;j<12;j++)pb[i*64+j]=prm[i*12+j];
    if(!P.prmBuf||P.prmCap<n){
      if(P.prmBuf)P.prmBuf.destroy();
      P.prmCap=Math.max(16,n*2);
      P.prmBuf=dev.createBuffer({size:P.prmCap*256,usage:GPUBufferUsage.UNIFORM|GPUBufferUsage.COPY_DST});
      P.siteBg=dev.createBindGroup({layout:S.g0,entries:[{binding:0,resource:{buffer:P.ubuf}},{binding:1,resource:{buffer:P.prmBuf,size:48}}]});
    }
    dev.queue.writeBuffer(P.prmBuf,0,pb.buffer,0,n*256);
    if(verts.length){
      var vb=new Float32Array(verts);
      if(!P.mapVB||P.mapCap<vb.byteLength){if(P.mapVB)P.mapVB.destroy();P.mapCap=Math.max(4096,vb.byteLength*2);P.mapVB=dev.createBuffer({size:P.mapCap,usage:GPUBufferUsage.VERTEX|GPUBufferUsage.COPY_DST});}
      dev.queue.writeBuffer(P.mapVB,0,vb.buffer,0,vb.byteLength);
      out.mapVB=P.mapVB;
    }
    out.n=out.map.length+out.ter.length;
    return out;
  }
  function bimGpuSiteEncode(P,pass,out){
    var S=P.site,i,d;
    if(out.map.length){
      pass.setPipeline(S.map);pass.setVertexBuffer(0,out.mapVB);pass.setBindGroup(0,P.siteBg,[out.mapPrm*256]);
      for(i=0;i<out.map.length;i++){d=out.map[i];pass.setBindGroup(1,d.bg);pass.draw(6,1,d.first,0);}
    }
    for(i=0;i<out.ter.length;i++){
      d=out.ter[i];
      pass.setPipeline(d.drape?S.drape:S.ter);pass.setBindGroup(0,P.siteBg,[d.prm*256]);pass.setBindGroup(1,d.bg);pass.setVertexBuffer(0,d.vb);pass.draw(d.count);
    }
  }
  function bimGpuPref(){var p='auto';try{p=localStorage.getItem(BIM_GPU_KEY)||'auto';}catch(eP){}return p==='webgl'?'webgl':'auto';}
  function bimGpuFail(why){
    A3D_GPU.state='failed';A3D_GPU.why=String(why||'');A3D_GPU.bundle=null;
    console.info('[BIM] WebGPU is not used: '+A3D_GPU.why+'. Drawing with WebGL.');
  }
  /* asked once, when 3D is first drawn: an adapter, a device, the canvas, the pipelines */
  function bimGpuStart(){
    if(A3D_GPU.state!=='off')return;
    if(bimGpuPref()==='webgl'){A3D_GPU.why='WebGL chosen';return;}
    if(typeof navigator==='undefined'||!navigator.gpu){A3D_GPU.state='none';A3D_GPU.why='this browser has no WebGPU';return;}
    var cv=document.getElementById('a3d-gpucanvas');
    if(!cv){A3D_GPU.why='no canvas yet';return;}
    A3D_GPU.state='starting';
    navigator.gpu.requestAdapter().then(function(ad){
      if(!ad)throw new Error('no WebGPU adapter');
      return ad.requestDevice();
    }).then(function(dev){
      var fmt=navigator.gpu.getPreferredCanvasFormat(),ctx=null;
      if(!A3D_GPU.offscreen){   /* offscreen, the canvas is never configured */
        ctx=cv.getContext('webgpu');
        if(!ctx)throw new Error('no WebGPU canvas context');
        ctx.configure({device:dev,format:fmt,alphaMode:'opaque'});
      }
      dev.pushErrorScope('validation');
      var mod=dev.createShaderModule({code:BIM_GPU_WGSL});
      var bgl=dev.createBindGroupLayout({entries:[
        {binding:0,visibility:GPUShaderStage.VERTEX|GPUShaderStage.FRAGMENT,buffer:{type:'uniform'}},
        {binding:1,visibility:GPUShaderStage.VERTEX,buffer:{type:'read-only-storage'}}]});
      var lay=dev.createPipelineLayout({bindGroupLayouts:[bgl]});
      var blend={color:{srcFactor:'src-alpha',dstFactor:'one-minus-src-alpha',operation:'add'},alpha:{srcFactor:'one',dstFactor:'one-minus-src-alpha',operation:'add'}};
      function pipe(edge,pass){
        return dev.createRenderPipeline({layout:lay,
          vertex:{module:mod,entryPoint:edge?'vsEdge':'vsFace',constants:{PASS:pass,EDGE:edge},
            buffers:[edge?{arrayStride:16,attributes:[{shaderLocation:0,offset:0,format:'float32x3'},{shaderLocation:2,offset:12,format:'float32'}]}:
              {arrayStride:28,attributes:[{shaderLocation:0,offset:0,format:'float32x3'},{shaderLocation:1,offset:12,format:'float32x3'},{shaderLocation:2,offset:24,format:'float32'}]}]},
          fragment:{module:mod,entryPoint:edge?'fsEdge':'fsFace',constants:{},targets:[pass?{format:fmt,blend:blend}:{format:fmt}]},
          primitive:{topology:edge?'line-list':'triangle-list',cullMode:'none'},
          depthStencil:{format:'depth24plus',depthWriteEnabled:!(pass&&!edge),depthCompare:'less-equal'},
          multisample:{count:4}});
      }
      var pipes={face0:pipe(0,0),face1:pipe(0,1),edge0:pipe(1,0),edge1:pipe(1,1)};
      var site=bimGpuSitePipes(dev,fmt);   /* __acad3dV154 */
      var ubuf=dev.createBuffer({size:160,usage:GPUBufferUsage.UNIFORM|GPUBufferUsage.COPY_DST});
      return dev.popErrorScope().then(function(err){
        if(err)throw new Error('pipelines: '+err.message);
        A3D_GPU.device=dev;A3D_GPU.ctx=ctx;A3D_GPU.cv=cv;A3D_GPU.format=fmt;A3D_GPU.pipes=pipes;A3D_GPU.bgl=bgl;A3D_GPU.ubuf=ubuf;
        A3D_GPU.site=site;A3D_GPU.terBufs={};A3D_GPU.prmBuf=null;A3D_GPU.prmCap=0;A3D_GPU.mapVB=null;A3D_GPU.mapCap=0;A3D_GPU.siteBg=null;
        A3D_GPU.state='ready';A3D_GPU.why='';
        dev.lost.then(function(info){
          if(A3D_GPU.device!==dev)return;
          bimGpuDrop();bimGpuFail('the device was lost ('+((info&&info.message)||'')+')');
          if(A3D.on)paint();
        });
        dev.onuncapturederror=function(ev){console.warn('[BIM] WebGPU error: '+(ev.error&&ev.error.message));};
        if(A3D.on)paint();
      });
    }).catch(function(e){bimGpuDrop();bimGpuFail(e&&e.message?e.message:e);});
  }
  /* everything the engine holds on the GPU given back; the description stays */
  function bimGpuDrop(){
    var S=A3D_SCENE,i;
    if(S)for(i=0;i<S.chunks.length;i++){var c=S.chunks[i];if(c.gpu){if(c.gpu.buf)c.gpu.buf.destroy();if(c.gpu.ebuf)c.gpu.ebuf.destroy();c.gpu=null;}}
    if(A3D_GPU.tab)A3D_GPU.tab.destroy();
    if(A3D_GPU.depth)A3D_GPU.depth.destroy();
    if(A3D_GPU.msaa)A3D_GPU.msaa.destroy();
    if(A3D_GPU.off)A3D_GPU.off.destroy();A3D_GPU.off=null;
    var kt;if(A3D_GPU.terBufs)for(kt in A3D_GPU.terBufs)if(A3D_GPU.terBufs.hasOwnProperty(kt))A3D_GPU.terBufs[kt].vb.destroy();   /* __acad3dV154 */
    if(A3D_GPU.prmBuf)A3D_GPU.prmBuf.destroy();if(A3D_GPU.mapVB)A3D_GPU.mapVB.destroy();
    A3D_GPU.terBufs={};A3D_GPU.prmBuf=null;A3D_GPU.prmCap=0;A3D_GPU.mapVB=null;A3D_GPU.mapCap=0;A3D_GPU.siteBg=null;A3D_GPU.site=null;A3D_GPU.tileLive=0;
    if(S&&S.dirty.gpu)delete S.dirty.gpu;
    A3D_GPU.tab=null;A3D_GPU.tabCap=0;A3D_GPU.bundle=null;A3D_GPU.bkey='';A3D_GPU.depth=null;A3D_GPU.msaa=null;A3D_GPU.w=0;A3D_GPU.h=0;
    if(A3D_GPU.device){var d=A3D_GPU.device;A3D_GPU.device=null;try{d.destroy();}catch(eD){}}
    A3D_GPU.ctx=null;A3D_GPU.pipes=null;A3D_GPU.ubuf=null;A3D_GPU.bg=null;
  }
  /* what WebGPU does not draw yet: the map, and a terrain surface in 3D */
  function bimGpuNeedsGl(V,W,H){
    return '';   /* __acad3dV154: the map and the terrain are drawn with WebGPU too */
  }
  function bimGpuBuf(dev,arr,usage){
    var b=dev.createBuffer({size:Math.max(16,arr.byteLength),usage:usage|GPUBufferUsage.COPY_DST});
    if(arr.byteLength)dev.queue.writeBuffer(b,0,arr.buffer,arr.byteOffset,arr.byteLength);
    return b;
  }
  function bimGpuRender(V,W,H){
    var P=A3D_GPU;
    if(P.state!=='ready')return false;
    if(P.breakNext){P.breakNext=false;throw new Error('a frame broken on purpose');}   /* a test's way to see a broken frame handed over */
    var dev=P.device,F=bimSceneSync(),B=F.S,i,c,re=false;
    bimSceneCull(B,V,W,H);   /* __acad3dV155 */
    var gs=cvScale(el.cv),wD=Math.max(1,Math.round(W*gs)),hD=Math.max(1,Math.round(H*gs));
    if(P.cv.width!==wD||P.cv.height!==hD){P.cv.width=wD;P.cv.height=hD;}
    if(P.w!==wD||P.h!==hD){
      if(P.depth)P.depth.destroy();if(P.msaa)P.msaa.destroy();
      P.depth=dev.createTexture({size:[wD,hD],format:'depth24plus',sampleCount:4,usage:GPUTextureUsage.RENDER_ATTACHMENT});
      P.msaa=dev.createTexture({size:[wD,hD],format:P.format,sampleCount:4,usage:GPUTextureUsage.RENDER_ATTACHMENT});
      P.w=wD;P.h=hD;
    }
    /* the chunks it has not got */
    for(i=0;i<B.chunks.length;i++){
      c=B.chunks[i];
      if(c.gpu&&c.gpu.ver===c.ver)continue;
      if(c.gpu){c.gpu.buf.destroy();c.gpu.ebuf.destroy();}
      c.gpu={buf:bimGpuBuf(dev,c.tri,GPUBufferUsage.VERTEX),ebuf:bimGpuBuf(dev,c.ed,GPUBufferUsage.VERTEX),ver:c.ver};
      re=true;
    }
    /* the table: whole when new or grown, else the rows that changed */
    var R=bimSceneDirty(B,'gpu');
    if(P.tabCap!==B.cap||!P.tab){
      if(P.tab)P.tab.destroy();
      P.tab=bimGpuBuf(dev,B.data||new Float32Array(8),GPUBufferUsage.STORAGE);P.tabCap=B.cap;
      P.bg=dev.createBindGroup({layout:P.bgl,entries:[{binding:0,resource:{buffer:P.ubuf}},{binding:1,resource:{buffer:P.tab}}]});
      P.bgv=(P.bgv||0)+1;   /* __acad3dV155: every chunk's bundles were recorded with the old one */
      R.lo=-1;R.hi=-1;B.st.uploads++;B.st.uploadBytes+=B.data?B.data.byteLength:0;re=true;
    }else if(R.lo>=0){
      dev.queue.writeBuffer(P.tab,R.lo*32,B.data.buffer,B.data.byteOffset+R.lo*32,(R.hi-R.lo+1)*32);
      B.st.uploads++;B.st.uploadBytes+=(R.hi-R.lo+1)*32;R.lo=-1;R.hi=-1;
    }
    /* the camera: two matrices and the light */
    var u=new Float32Array(40);
    u.set(bimGlViewMatrix(V),0);u.set(bimGlProjMatrix(W,H,A3D.flat,A3D.cam.dist),16);u[32]=LIGHT[0];u[33]=LIGHT[1];u[34]=LIGHT[2];
    u[36]=V.eye[0];u[37]=V.eye[1];u[38]=V.eye[2];   /* __acad3dV154 */
    dev.queue.writeBuffer(P.ubuf,0,u.buffer,0,160);
    /* __acad3dV155: a bundle a chunk and pass, recorded when first wanted and kept with the chunk;
       the frame executes those of the chunks in view, solids first, then blended solids, then outlines */
    var L0=[],L1=[],L2=[],L3=[],rec=0;
    function bun(ck,which){
      var g=ck.gpu,edge=which.charAt(0)==='e',be;
      if(g.bgv!==P.bgv){g.bun={};g.bgv=P.bgv;}
      if(g.bun[which])return g.bun[which];
      be=dev.createRenderBundleEncoder({colorFormats:[P.format],depthStencilFormat:'depth24plus',sampleCount:4});
      be.setBindGroup(0,P.bg);
      be.setPipeline(which==='f0'?P.pipes.face0:which==='f1'?P.pipes.face1:which==='e0'?P.pipes.edge0:P.pipes.edge1);
      be.setVertexBuffer(0,edge?g.ebuf:g.buf);be.draw(edge?ck.ecount:ck.count);
      rec++;
      return (g.bun[which]=be.finish());
    }
    for(i=0;i<B.chunks.length;i++){
      c=B.chunks[i];
      if(c.cull)continue;
      if(c.count){L0.push(bun(c,'f0'));if(F.hasTrans)L1.push(bun(c,'f1'));}
      if(F.edges&&c.ecount){L2.push(bun(c,'e0'));if(F.hasTrans)L3.push(bun(c,'e1'));}
    }
    var ALL=L0.concat(L1,L2,L3);
    P.bdraws=ALL.length;B.st.recorded=rec;
    var site=bimGpuSitePrepare(P,V,W,H);   /* __acad3dV154: the map and the terrain, under the model */
    B.st.siteDraws=site.n;
    /* the canvas, or a texture of the same size when asked (a headless browser cannot present one) */
    var dst;
    if(P.offscreen){
      if(!P.off||P.off.width!==wD||P.off.height!==hD){if(P.off)P.off.destroy();P.off=dev.createTexture({size:[wD,hD],format:P.format,usage:GPUTextureUsage.RENDER_ATTACHMENT|GPUTextureUsage.COPY_SRC});}
      dst=P.off;
    }else dst=P.ctx.getCurrentTexture();
    var enc=dev.createCommandEncoder();
    var pass=enc.beginRenderPass({
      colorAttachments:[{view:P.msaa.createView(),resolveTarget:dst.createView(),clearValue:{r:0.114,g:0.125,b:0.141,a:1},loadOp:'clear',storeOp:'discard'}],
      depthStencilAttachment:{view:P.depth.createView(),depthClearValue:1,depthLoadOp:'clear',depthStoreOp:'discard'}});
    bimGpuSiteEncode(P,pass,site);
    pass.executeBundles(ALL);
    pass.end();
    dev.queue.submit([enc.finish()]);
    B.st.draws=P.bdraws;
    bimSceneFrameDone(B,'webgpu');
    A3D.glFaces=F.totalFaces;
    return true;
  }
  /* the frame: WebGPU where it is ready and draws everything in view, else WebGL */
  function bimRender3D(V,W,H){
    var gc=document.getElementById('a3d-gpucanvas'),lc=document.getElementById('a3d-glcanvas'),why='';
    if(A3D_GPU.state==='off')bimGpuStart();
    if(A3D_GPU.state==='ready'&&bimGpuPref()!=='webgl'&&!A3D_GPU.forceOff){
      why=bimGpuNeedsGl(V,W,H);
      var okG=false;
      if(!why){try{okG=bimGpuRender(V,W,H);}catch(eR){bimGpuDrop();bimGpuFail('a frame failed: '+(eR&&eR.message));}}   /* never a broken frame: WebGL takes over */
      if(okG){
        if(gc)gc.style.visibility='visible';if(lc)lc.style.visibility='hidden';
        A3D_GPU.engine='webgpu';A3D_GPU.fallback='';
        return true;
      }
    }
    if(gc)gc.style.visibility='hidden';if(lc)lc.style.visibility='visible';
    var ok=bimGlRender(V,W,H);
    A3D_GPU.engine=ok?'webgl':'2d';A3D_GPU.fallback=why;
    return ok;
  }
  /* __acad3dV155: n boxes in a grid, each its own element sharing one mesh, as a family's */
  function bimStressModel(n,size){
    var L=[],k=Math.ceil(Math.sqrt(n)),i,sz=size||0.6;
    for(i=0;i<n;i++)L.push({id:'stress-'+i,t:'box',prm:{Length:sz/SCALE,Width:sz/SCALE,Height:(1+(i%7)*0.4)/SCALE},pos:[(i%k)*1.5,0,Math.floor(i/k)*1.5],rot:[0,0,0]});
    A3D.objs=L;A3D.sel=null;A3D.sel2=null;A3D.selSet=[];
    return L.length;
  }
  /* frames drawn with the camera turning a little each time, each finished before the next:
     the first, the average of the rest and the slowest, in milliseconds */
  function bimRenderBench(frames){
    var c=A3D.cam,y0=c.yaw,W=cvW(),H=cvH(),px=new Uint8Array(4),sum=0,mx=0,first=0,i=0,n=frames||20;
    if(!bimGlInit()&&A3D_GPU.state!=='ready')return Promise.resolve(null);
    function one(){
      c.yaw=y0+i*0.01;
      var t0=performance.now();
      bimRender3D(camVecs(c),W,H);
      var done=A3D_GPU.engine==='webgpu'?A3D_GPU.device.queue.onSubmittedWorkDone():(A3D_GL.gl.readPixels(0,0,1,1,A3D_GL.gl.RGBA,A3D_GL.gl.UNSIGNED_BYTE,px),Promise.resolve());
      return done.then(function(){
        var dt=performance.now()-t0;
        if(i===0)first=dt;else{sum+=dt;if(dt>mx)mx=dt;}
        i++;
        return i<n?one():null;
      });
    }
    return one().then(function(){
      c.yaw=y0;
      return {first:first,avg:sum/Math.max(1,n-1),max:mx,engine:A3D_GPU.engine,stats:A3D.glStats?JSON.parse(JSON.stringify(A3D.glStats)):null};
    });
  }
  /* BENCHMARK: this device's frame times, with WebGPU where it has it and with WebGL; the model is
     put back as it was, and nothing of the test is saved or undone */
  var A3D_BENCH=null;
  function bimBenchmark(){
    if(A3D_BENCH&&A3D_BENCH.running)return Promise.resolve(A3D_BENCH);
    if(!A3D.on)return Promise.resolve({error:'Open the model (3D) first'});
    var keep={objs:A3D.objs,sel:A3D.sel,sel2:A3D.sel2,selSet:A3D.selSet,cam:JSON.parse(JSON.stringify(A3D.cam)),flat:A3D.flat},
      R={running:true,at:new Date().toISOString(),device:String(navigator.userAgent||'').slice(0,160),rows:[],gpu:A3D_GPU.state==='ready'&&bimGpuPref()!=='webgl'};
    A3D_BENCH=R;
    a3dToast('Benchmark: drawing 5,000 and 20,000 elements for a few seconds...');
    var sizes=[5000,20000],q=Promise.resolve();
    sizes.forEach(function(n){
      q=q.then(function(){
        bimStressModel(n);
        var k=Math.ceil(Math.sqrt(n))*1.5;
        A3D.flat=false;A3D.cam.tx=k/2;A3D.cam.tz=k/2;A3D.cam.dist=k*1.1;A3D.cam.pitch=0.6;A3D.cam.yaw=0.7;
        var row={n:n};R.rows.push(row);
        var p=Promise.resolve();
        if(R.gpu)p=p.then(function(){A3D_GPU.forceOff=false;return bimRenderBench(3).then(function(){return bimRenderBench(30);}).then(function(r){row.webgpu=r&&r.engine==='webgpu'?r.avg:null;row.webgpuMax=r?r.max:null;});});
        return p.then(function(){A3D_GPU.forceOff=true;return bimRenderBench(3).then(function(){return bimRenderBench(30);});})
          .then(function(r){A3D_GPU.forceOff=false;row.webgl=r&&r.engine==='webgl'?r.avg:null;row.webglMax=r?r.max:null;row.draws=r&&r.stats?r.stats.draws:null;});
      });
    });
    function done(){
      A3D_GPU.forceOff=false;
      A3D.objs=keep.objs;A3D.sel=keep.sel;A3D.sel2=keep.sel2;A3D.selSet=keep.selSet;A3D.flat=keep.flat;
      var k;for(k in keep.cam)if(keep.cam.hasOwnProperty(k))A3D.cam[k]=keep.cam[k];
      R.running=false;
      paint();refreshProps();
    }
    return q.then(function(){
      done();
      a3dToast('Benchmark: '+bimBenchmarkText(R));
      return R;
    },function(e){done();R.error=String(e&&e.message||e);a3dToast('Benchmark failed: '+R.error);return R;});
  }
  function bimBenchmarkText(R){
    if(!R)return '';
    if(R.error)return R.error;
    return R.rows.map(function(r){
      return (r.n===5000?'5,000':'20,000')+': '+(r.webgpu!=null?'WebGPU '+r.webgpu.toFixed(1)+' ms, ':'')+(r.webgl!=null?'WebGL '+r.webgl.toFixed(1)+' ms':'WebGL -');
    }).join('; ')+' a frame';
  }
  /* GRAPHICS: which engine draws, and the choice of WebGL for this browser */
  function bimGraphicsLabel(){
    var P=A3D_GPU;
    if(P.engine==='webgpu')return 'WebGPU';
    if(P.engine==='2d')return 'Drawn in 2D (no WebGL)';
    if(bimGpuPref()==='webgl')return 'WebGL (chosen)';
    if(P.state==='ready'&&P.fallback)return 'WebGL (for the '+P.fallback+')';
    if(P.state==='starting')return 'WebGL (WebGPU starting)';
    return 'WebGL'+(P.why?' ('+P.why+')':'');
  }
  function bimGraphicsSet(pref){
    try{localStorage.setItem(BIM_GPU_KEY,pref==='webgl'?'webgl':'auto');}catch(eS){}
    if(pref!=='webgl'&&(A3D_GPU.state==='off'||A3D_GPU.state==='failed')){A3D_GPU.state='off';bimGpuStart();}   /* chosen again: tried again */
    if(A3D.on)paint();
    refreshProps();
    return bimGpuPref();
  }
  function bimGraphicsCommand(){
    var to=bimGpuPref()==='webgl'?'auto':'webgl';
    bimGraphicsSet(to);
    a3dToast(to==='webgl'?'Graphics: WebGL, in this browser':'Graphics: WebGPU where the browser has it, else WebGL');
  }
  /* the last WebGPU frame against a WebGL frame of the same view, pixel by pixel (offscreen only):
     the largest difference of a channel, and how many pixels differ by more than 16 and 48 */
  function bimGpuCompare(){
    var P=A3D_GPU;
    if(P.state!=='ready'||!P.offscreen)return Promise.resolve(null);
    var V=camVecs(A3D.cam),W=cvW(),H=cvH();
    if(!bimGpuRender(V,W,H))return Promise.resolve(null);
    var dev=P.device,w=P.off.width,h=P.off.height,bpr=Math.ceil(w*4/256)*256;
    var rb=dev.createBuffer({size:bpr*h,usage:GPUBufferUsage.COPY_DST|GPUBufferUsage.MAP_READ});
    var enc=dev.createCommandEncoder();
    enc.copyTextureToBuffer({texture:P.off},{buffer:rb,bytesPerRow:bpr},[w,h]);
    dev.queue.submit([enc.finish()]);
    var stats=A3D.glStats?JSON.parse(JSON.stringify(A3D.glStats)):null;
    return rb.mapAsync(GPUMapMode.READ).then(function(){
      var g=new Uint8Array(rb.getMappedRange().slice(0));rb.unmap();rb.destroy();
      var lc=document.getElementById('a3d-glcanvas');
      if(!bimGlRender(V,W,H))return null;
      var gl=A3D_GL.gl,lw=gl.drawingBufferWidth,lh=gl.drawingBufferHeight,px=new Uint8Array(lw*lh*4);
      gl.readPixels(0,0,lw,lh,gl.RGBA,gl.UNSIGNED_BYTE,px);
      if(lw!==w||lh!==h)return {error:'sizes differ',gpu:[w,h],gl:[lw,lh]};
      var bgra=P.format.indexOf('bgra')===0,mx=0,n16=0,n48=0,near=0,x,y,k,i,j,d,m,dx,dy,mm;
      function diff(i,j){var m=0,k,d;for(k=0;k<3;k++){d=Math.abs(g[i+(bgra?2-k:k)]-px[j+k]);if(d>m)m=d;}return m;}
      for(y=0;y<h;y++)for(x=0;x<w;x++){
        i=y*bpr+x*4;j=((h-1-y)*w+x)*4;m=diff(i,j);
        if(m>mx)mx=m;if(m>16)n16++;
        if(m>48){
          n48++;
          /* a thin line rasterised a pixel over: the same colour beside it is not a difference; nor is
             one of the four samples of an outline's edge covered the other way (__acad3dV154: up to 64) */
          mm=m;
          for(dy=-1;dy<=1&&mm>64;dy++)for(dx=-1;dx<=1&&mm>64;dx++){
            if(x+dx<0||x+dx>=w||y+dy<0||y+dy>=h)continue;
            mm=Math.min(mm,diff(i,((h-1-(y+dy))*w+x+dx)*4));
          }
          if(mm>64)near++;
        }
      }
      return {w:w,h:h,max:mx,over16:n16,over48:n48,over48near:near,pixels:w*h,gpuStats:stats};
    });
  }
  /* __acad3dV72: W and H arrive in CSS pixels, because the projection matrix has to agree with
     toScreen() exactly or the GL layer and the 2D overlay drift apart. The GL canvas and its
     viewport, though, are the backing store and must be in DEVICE pixels -- otherwise the whole
     shaded layer renders at half resolution under a crisp overlay. */
