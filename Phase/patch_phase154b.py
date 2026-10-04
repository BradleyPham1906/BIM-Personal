"""patch_phase154b.py -- V154: the map and the draped terrain drawn with WebGPU.

V153 handed every frame with the map or a terrain surface in 3D to WebGL. Now WebGPU draws them:
- the basemap's tiles as textured quads on the ground, drawn first without writing depth, mixed
  toward the background by the map's opacity, as WebGL's;
- a terrain surface shaded by its smooth normals, and the map draped on it tile by tile, nothing
  outside a tile, as WebGL's; the surface's arrays now built once (bimTerrainMeshData) for either
  engine;
- each tile a texture with its mipmaps made on the GPU (a 2x2 average a level, as WebGL's
  generateMipmap), kept with the tile and given back with it; a tile the browser will not hand to
  the GPU is counted against its host, as with WebGL;
- per-draw values (colour, opacity, the tile's place) in one uniform buffer read at an offset per
  draw; these draws are made each frame, before the model's recorded bundle is replayed.
WebGL still draws whenever WebGPU cannot (V153); the map and terrain no longer send a frame to it."""
NAME = 'patch_phase154b.py'
BASE = '6ebf1b27a611f944c7a427436876ea8f23eebdcd40103ddf802523509f37a0e6'
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def rep(old, new, n=1):
    global t
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: anchor count %d (want %d): %r' % (c, n, old[:80]))
    t = t.replace(old, new)


# ---- the surface's arrays, for either engine ----------------------------------------------------
rep("""  function bimTerrainGlMesh(G,T,o,org){
    var tin=bimTerrainTin(o),tn=bimTrueNorthDeg(),key,rec=T.bufs[o.id],gl=G.gl,i,k,tr,nrm,pos=[],nor=[],mer=[],A,B,C,ux,uy,uz,vx,vy,vz,nx,ny,nz,L;
    if(!tin||!tin.tris.length)return null;
    key=(o.rev||0)+':'+o.survey.length+':'+(o.pos||[0,0,0]).join(',')+':'+tn+':'+(org?org.lat+','+org.lon:'-');
    if(rec&&rec.key===key)return rec;
    if(rec){gl.deleteBuffer(rec.pos);gl.deleteBuffer(rec.nor);gl.deleteBuffer(rec.mer);}
    nrm=""", """  var A3D_TER_DATA={};   /* __acad3dV154: a surface's arrays, for either engine */
  function bimTerrainMeshData(o,org){
    var tin=bimTerrainTin(o),tn=bimTrueNorthDeg(),key,D=A3D_TER_DATA[o.id],i,k,tr,nrm,pos=[],nor=[],mer=[],A,B,C,ux,uy,uz,vx,vy,vz,nx,ny,nz,L;
    if(!tin||!tin.tris.length)return null;
    key=(o.rev||0)+':'+o.survey.length+':'+(o.pos||[0,0,0]).join(',')+':'+tn+':'+(org?org.lat+','+org.lon:'-');
    if(D&&D.key===key)return D;
    nrm=""")
rep("""    function mk(a){var b=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,b);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(a),gl.STATIC_DRAW);return b;}
    var lo0=Infinity,lo1=-Infinity,la0=Infinity,la1=-Infinity,g;
    if(org)for(i=0;i<tin.P.length;i++){g=bimModelToGeo(tin.P[i][0],tin.P[i][1],org);lo0=Math.min(lo0,g[0]);lo1=Math.max(lo1,g[0]);la0=Math.min(la0,g[1]);la1=Math.max(la1,g[1]);}
    rec=T.bufs[o.id]={key:key,pos:mk(pos),nor:mk(nor),mer:mk(mer),count:pos.length/3,ox:ox,oy:oy,ext:org?[lo0,la0,lo1,la1]:null};
    return rec;
  }""", """    var lo0=Infinity,lo1=-Infinity,la0=Infinity,la1=-Infinity,g;
    if(org)for(i=0;i<tin.P.length;i++){g=bimModelToGeo(tin.P[i][0],tin.P[i][1],org);lo0=Math.min(lo0,g[0]);lo1=Math.max(lo1,g[0]);la0=Math.min(la0,g[1]);la1=Math.max(la1,g[1]);}
    D=A3D_TER_DATA[o.id]={key:key,pos:new Float32Array(pos),nor:new Float32Array(nor),mer:new Float32Array(mer),count:pos.length/3,ox:ox,oy:oy,ext:org?[lo0,la0,lo1,la1]:null};
    return D;
  }
  function bimTerrainGlMesh(G,T,o,org){
    var D=bimTerrainMeshData(o,org),rec=T.bufs[o.id],gl=G.gl;
    if(!D)return null;
    if(rec&&rec.key===D.key)return rec;
    if(rec){gl.deleteBuffer(rec.pos);gl.deleteBuffer(rec.nor);gl.deleteBuffer(rec.mer);}
    function mk(a){var b=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,b);gl.bufferData(gl.ARRAY_BUFFER,a,gl.STATIC_DRAW);return b;}
    rec=T.bufs[o.id]={key:D.key,pos:mk(D.pos),nor:mk(D.nor),mer:mk(D.mer),count:D.count,ox:D.ox,oy:D.oy,ext:D.ext};
    return rec;
  }""")

# ---- a tile's WebGPU texture given back with the tile ---------------------------------------------
rep("""    if(e.tex&&e.texGl){try{e.texGl.deleteTexture(e.tex);}catch(eD){}}
    e.tex=null;e.texGl=null;""", """    if(e.tex&&e.texGl){try{e.texGl.deleteTexture(e.tex);}catch(eD){}}
    e.tex=null;e.texGl=null;
    if(e.gtx){try{e.gtx.tex.destroy();}catch(eG){}if(e.gtx.dev===A3D_GPU.device)A3D_GPU.tileLive--;e.gtx=null;}   /* __acad3dV154 */""")

# ---- the WebGPU side: pipelines, textures, the frame's site draws --------------------------------
rep("""  function bimGpuPref(){""", """  /* __acad3dV154: the map and the terrain. Group 0: the camera, and this draw's values at an offset;
     group 1: a tile's sampler and texture. */
  var BIM_GPU_SITE_WGSL=
    'struct U{view:mat4x4f,proj:mat4x4f,light:vec4f,eye:vec4f};\\n'+
    'struct M{color:vec4f,sub:vec4f,tile:vec4f};\\n'+   /* color.a: the opacity; tile: offset x y, 1/scale, mode */
    '@group(0) @binding(0) var<uniform> u:U;\\n'+
    '@group(0) @binding(1) var<uniform> m:M;\\n'+
    '@group(1) @binding(0) var smp:sampler;\\n'+
    '@group(1) @binding(1) var tx:texture_2d<f32>;\\n'+
    'fn clip(p:vec4f)->vec4f{var q=p;q.z=(q.z+q.w)*0.5;return q;}\\n'+
    'struct MO{@builtin(position) p:vec4f,@location(0) uv:vec2f};\\n'+
    '@vertex fn vsMap(@location(0) pos:vec3f,@location(1) uv:vec2f)->MO{var o:MO;o.p=clip(u.proj*u.view*vec4f(pos,1.0));o.uv=uv;return o;}\\n'+
    '@fragment fn fsMap(i:MO)->@location(0) vec4f{let c=textureSample(tx,smp,i.uv).rgb;return vec4f(mix(vec3f(0.114,0.125,0.141),c,m.color.a),1.0);}\\n'+
    'struct TO{@builtin(position) p:vec4f,@location(0) uv:vec2f,@location(1) k:f32};\\n'+
    '@vertex fn vsTer(@location(0) pos:vec3f,@location(1) n:vec3f,@location(2) mc:vec2f)->TO{var o:TO;\\n'+
    ' o.uv=(mc-m.tile.xy)*m.tile.z;o.k=0.5+0.5*abs(dot(normalize(n),u.light.xyz));o.p=clip(u.proj*u.view*vec4f(pos,1.0));return o;}\\n'+
    '@fragment fn fsTer(i:TO)->@location(0) vec4f{\\n'+   /* sampled first: a texture is read in uniform control flow */
    ' let c=textureSample(tx,smp,m.sub.xy+clamp(i.uv,vec2f(0.0),vec2f(1.0))*(m.sub.zw-m.sub.xy)).rgb;\\n'+
    ' if(m.tile.w<0.5){return vec4f(m.color.rgb*i.k,1.0);}\\n'+
    ' if(i.uv.x<0.0||i.uv.x>1.0||i.uv.y<0.0||i.uv.y>1.0){discard;}\\n'+
    ' return vec4f(mix(m.color.rgb*i.k,c*(0.62+0.38*i.k),m.color.a),1.0);}\\n';
  /* a level of a tile's mipmap from the one above it: a 2x2 average, as generateMipmap */
  var BIM_GPU_MIP_WGSL=
    '@group(0) @binding(0) var s:sampler;\\n'+
    '@group(0) @binding(1) var t:texture_2d<f32>;\\n'+
    'struct O{@builtin(position) p:vec4f,@location(0) uv:vec2f};\\n'+
    '@vertex fn vs(@builtin(vertex_index) i:u32)->O{var P=array<vec2f,3>(vec2f(-1.0,-1.0),vec2f(3.0,-1.0),vec2f(-1.0,3.0));\\n'+
    ' var o:O;o.p=vec4f(P[i],0.0,1.0);o.uv=vec2f((P[i].x+1.0)*0.5,(1.0-P[i].y)*0.5);return o;}\\n'+
    '@fragment fn fs(i:O)->@location(0) vec4f{return textureSample(t,s,i.uv);}\\n';
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
  function bimGpuPref(){""")
rep("""      var pipes={face0:pipe(0,0),face1:pipe(0,1),edge0:pipe(1,0),edge1:pipe(1,1)};""",
    """      var pipes={face0:pipe(0,0),face1:pipe(0,1),edge0:pipe(1,0),edge1:pipe(1,1)};
      var site=bimGpuSitePipes(dev,fmt);   /* __acad3dV154 */""")
rep("""        A3D_GPU.device=dev;A3D_GPU.ctx=ctx;A3D_GPU.cv=cv;A3D_GPU.format=fmt;A3D_GPU.pipes=pipes;A3D_GPU.bgl=bgl;A3D_GPU.ubuf=ubuf;""",
    """        A3D_GPU.device=dev;A3D_GPU.ctx=ctx;A3D_GPU.cv=cv;A3D_GPU.format=fmt;A3D_GPU.pipes=pipes;A3D_GPU.bgl=bgl;A3D_GPU.ubuf=ubuf;
        A3D_GPU.site=site;A3D_GPU.terBufs={};A3D_GPU.prmBuf=null;A3D_GPU.prmCap=0;A3D_GPU.mapVB=null;A3D_GPU.mapCap=0;A3D_GPU.siteBg=null;""")
rep("""    if(A3D_GPU.off)A3D_GPU.off.destroy();A3D_GPU.off=null;""",
    """    if(A3D_GPU.off)A3D_GPU.off.destroy();A3D_GPU.off=null;
    var kt;if(A3D_GPU.terBufs)for(kt in A3D_GPU.terBufs)if(A3D_GPU.terBufs.hasOwnProperty(kt))A3D_GPU.terBufs[kt].vb.destroy();   /* __acad3dV154 */
    if(A3D_GPU.prmBuf)A3D_GPU.prmBuf.destroy();if(A3D_GPU.mapVB)A3D_GPU.mapVB.destroy();
    A3D_GPU.terBufs={};A3D_GPU.prmBuf=null;A3D_GPU.prmCap=0;A3D_GPU.mapVB=null;A3D_GPU.mapCap=0;A3D_GPU.siteBg=null;A3D_GPU.site=null;A3D_GPU.tileLive=0;""")
# the map and the terrain no longer send a frame to WebGL
rep("""    if(A3D_PLOT.on)return '';
    var i,o;
    if(!bimCameraIsPlan())for(i=0;i<A3D.objs.length;i++){o=A3D.objs[i];if(o.t==='terrain'&&o.survey&&bimLayerShown(o)&&!bimTerrainSuperseded(o))return 'terrain';}
    if(bimMapSettings().style!=='off'&&bimMapPlan(V,W,H).tiles.length)return 'map';
    return '';""", """    return '';   /* __acad3dV154: the map and the terrain are drawn with WebGPU too */""")
rep("""    /* the canvas, or a texture of the same size when asked (a headless browser cannot present one) */""",
    """    var site=bimGpuSitePrepare(P,V,W,H);   /* __acad3dV154: the map and the terrain, under the model */
    B.st.siteDraws=site.n;
    /* the canvas, or a texture of the same size when asked (a headless browser cannot present one) */""")
rep("""    pass.executeBundles([P.bundle]);""", """    bimGpuSiteEncode(P,pass,site);
    pass.executeBundles([P.bundle]);""")

rep("""  window.__acad3dV153='webgpu,""",
    """  window.__acad3dV154='edgepull,gpumap,gputerrain,gpudrape,tilemipmaps,tilefreed,terraindata,sitefirst';
  window.__acad3dV153='webgpu,""")
rep("""  var BIM_APP_VERSION={v:'V153',date:'2026-10-04'};   /* __acad3dV153 */""",
    """  var BIM_APP_VERSION={v:'V154',date:'2026-10-04'};   /* __acad3dV154 */""")

rep("""  window.__a3dGpuBreakNext=function(){""", """  window.__a3dGpuTiles=function(){var k,e,n=0,lv=[];for(k in A3D_MAP.cache)if(A3D_MAP.cache.hasOwnProperty(k)){e=A3D_MAP.cache[k];if(e.gtx&&e.gtx.dev===A3D_GPU.device){n++;lv.push(e.gtx.tex.mipLevelCount);}}return {textures:n,levels:lv,live:A3D_GPU.tileLive||0};};   /* __acad3dV154 */
  window.__a3dMapDropAll=function(){var k,L=[];for(k in A3D_MAP.cache)if(A3D_MAP.cache.hasOwnProperty(k))L.push(A3D_MAP.cache[k]);L.forEach(bimMapDrop);return L.length;};
  window.__a3dGpuBreakNext=function(){""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
