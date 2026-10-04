"""patch_phase155a.py -- V155: chunks by place, what is off screen not drawn, a bundle a chunk, and
BENCHMARK on the owner's own devices (Render R4).

- Chunks by place. A new object joins the open chunk of its 64 m cell of the ground (another chunk of
  the same cell when that one is full), so a chunk holds what stands together. Each frame a chunk's
  box is the union of its objects' boxes where they stand now (an object moved far takes its
  chunk's box with it), and a chunk wholly outside the view is not drawn, in either engine.
- WebGPU records a bundle per chunk and pass, kept with the chunk; each frame executes the bundles
  of the chunks in view. Moving the camera chooses among bundles; nothing is recorded again unless a
  chunk is rebuilt or the table is reallocated. A transparent layer appearing or going no longer
  re-records anything: the blended passes' bundles are kept for when they are wanted.
- BENCHMARK: on whatever device it is run, the app puts 5,000 and then 20,000 elements in place of
  the model for a moment, draws 30 frames of each turning, with WebGPU where there is one and with
  WebGL, and puts the model back as it was. The times are in Statistics and a message, so the owner
  can read them off a phone, a tablet and a computer."""
NAME = 'patch_phase155a.py'
BASE = '4a3dd3e88964fc7e3ad0bb4fb947c33c80d0e163869c95e796d38c8ed5d68bbc'
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


# ---- chunks by place, and their boxes --------------------------------------------------------------
rep("""  var BIM_GB_CHUNK=196608,BIM_GB_TEXW=1024;""", """  var BIM_GB_CHUNK=196608,BIM_GB_TEXW=1024;
  var BIM_GB_CELL=64,A3D_CULL=true;   /* __acad3dV155: chunks by 64 m cells of the ground; the ones out of view not drawn */
  function bimMeshBox(m){
    var b=[Infinity,Infinity,Infinity,-Infinity,-Infinity,-Infinity],i,p;
    for(i=0;i<m.v.length;i++){p=m.v[i];if(p[0]<b[0])b[0]=p[0];if(p[1]<b[1])b[1]=p[1];if(p[2]<b[2])b[2]=p[2];if(p[0]>b[3])b[3]=p[0];if(p[1]>b[4])b[4]=p[1];if(p[2]>b[5])b[5]=p[2];}
    return b;
  }""")
rep("""    return A3D_SCENE||(A3D_SCENE={cap:0,data:null,slots:{},free:[],next:0,chunks:[],of:{},dirty:{},""",
    """    return A3D_SCENE||(A3D_SCENE={cap:0,data:null,slots:{},free:[],next:0,chunks:[],of:{},dirty:{},cells:{},""")
rep("""      c=B.of[id];
      if(!c){
        var nv=bimGbVerts(m),last=B.chunks[B.chunks.length-1];
        if(!last||last.verts+nv>BIM_GB_CHUNK){last={ids:[],refs:{},verts:0,count:0,ecount:0,tri:null,ed:null,ver:0,gl:null,gpu:null,dirty:true};B.chunks.push(last);}
        last.ids.push(id);last.refs[id]=m;last.verts+=nv;last.dirty=true;B.of[id]=last;
      }else if(c.refs[id]!==m){c.verts+=bimGbVerts(m)-bimGbVerts(c.refs[id]);c.refs[id]=m;c.dirty=true;}""",
    """      c=B.of[id];
      if(!c){   /* __acad3dV155: into the open chunk of its cell */
        var nv=bimGbVerts(m),lb=bimMeshBox(m),cell=Math.floor((o.pos[0]+(lb[0]+lb[3])/2)/BIM_GB_CELL)+','+Math.floor((o.pos[2]+(lb[2]+lb[5])/2)/BIM_GB_CELL),last=B.cells[cell];
        if(!last||last.verts+nv>BIM_GB_CHUNK){last={ids:[],refs:{},lb:{},verts:0,count:0,ecount:0,tri:null,ed:null,ver:0,gl:null,gpu:null,dirty:true,cell:cell,wb:null,cull:false};B.chunks.push(last);B.cells[cell]=last;}
        last.ids.push(id);last.refs[id]=m;last.lb[id]=lb;last.verts+=nv;last.dirty=true;B.of[id]=last;c=last;
      }else if(c.refs[id]!==m){c.verts+=bimGbVerts(m)-bimGbVerts(c.refs[id]);c.refs[id]=m;c.lb[id]=bimMeshBox(m);c.dirty=true;}
      /* the chunk's box: its objects where they stand now */
      var wb=c.wb,ob=c.lb[id];
      if(wb.f!==B.frame){wb[0]=wb[1]=wb[2]=Infinity;wb[3]=wb[4]=wb[5]=-Infinity;wb.f=B.frame;}
      if(o.pos[0]+ob[0]<wb[0])wb[0]=o.pos[0]+ob[0];if(o.pos[1]+ob[1]<wb[1])wb[1]=o.pos[1]+ob[1];if(o.pos[2]+ob[2]<wb[2])wb[2]=o.pos[2]+ob[2];
      if(o.pos[0]+ob[3]>wb[3])wb[3]=o.pos[0]+ob[3];if(o.pos[1]+ob[4]>wb[4])wb[4]=o.pos[1]+ob[4];if(o.pos[2]+ob[5]>wb[5])wb[5]=o.pos[2]+ob[5];""")
rep("""    B.st={draws:0,chunks:0,rebuilt:0,rebuiltVerts:0,uploads:0,uploadBytes:0,objects:0};
    A3D.lastGlAlpha={};
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];m=meshOf(o);""", """    B.st={draws:0,chunks:0,rebuilt:0,rebuiltVerts:0,uploads:0,uploadBytes:0,objects:0,culled:0,recorded:0};
    A3D.lastGlAlpha={};
    B.frame=(B.frame||0)+1;
    for(i=0;i<B.chunks.length;i++)if(!B.chunks[i].wb)B.chunks[i].wb=[0,0,0,0,0,0];
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];m=meshOf(o);""")
# a new chunk needs its box array before the box is grown: made where the chunk is made
rep("""ver:0,gl:null,gpu:null,dirty:true,cell:cell,wb:null,cull:false};""", """ver:0,gl:null,gpu:null,dirty:true,cell:cell,wb:[0,0,0,0,0,0],cull:false};""")
rep("""      c=B.of[id];c.ids.splice(c.ids.indexOf(id),1);c.verts-=bimGbVerts(c.refs[id]);delete c.refs[id];c.dirty=true;""",
    """      c=B.of[id];c.ids.splice(c.ids.indexOf(id),1);c.verts-=bimGbVerts(c.refs[id]);delete c.refs[id];delete c.lb[id];c.dirty=true;""")
rep("""      if(!c.ids.length){bimGbChunkFree(c);B.chunks.splice(i,1);continue;}""",
    """      if(!c.ids.length){bimGbChunkFree(c);B.chunks.splice(i,1);if(B.cells[c.cell]===c)delete B.cells[c.cell];continue;}""")
# the view's test, for either engine
rep("""  function bimSceneFrameDone(B,mode){""", """  /* __acad3dV155: a chunk wholly outside the view is not drawn: its box's eight corners all beyond
     one side of the view (or behind the eye, or past the far plane) */
  function bimSceneCull(B,V,W,H){
    var M=bimMat4Mul(bimGlProjMatrix(W,H,A3D.flat,A3D.cam.dist),bimGlViewMatrix(V)),i,c,b,k,x,y,z,cx,cy,cz,cw,o0,o1,o2,o3,o4,o5;
    for(i=0;i<B.chunks.length;i++){
      c=B.chunks[i];b=c.wb;
      if(!A3D_CULL||!b||b.f!==B.frame){c.cull=false;continue;}
      o0=o1=o2=o3=o4=o5=0;
      for(k=0;k<8;k++){
        x=k&1?b[3]:b[0];y=k&2?b[4]:b[1];z=k&4?b[5]:b[2];
        cx=M[0]*x+M[4]*y+M[8]*z+M[12];cy=M[1]*x+M[5]*y+M[9]*z+M[13];cz=M[2]*x+M[6]*y+M[10]*z+M[14];cw=M[3]*x+M[7]*y+M[11]*z+M[15];
        if(cx<-cw)o0++;if(cx>cw)o1++;if(cy<-cw)o2++;if(cy>cw)o3++;if(cz<-cw)o4++;if(cz>cw)o5++;
      }
      c.cull=o0===8||o1===8||o2===8||o3===8||o4===8||o5===8;
      if(c.cull)B.st.culled++;
    }
  }
  function bimMat4Mul(a,b){   /* column-major, a*b */
    var r=new Float32Array(16),i,j;
    for(i=0;i<4;i++)for(j=0;j<4;j++)r[j*4+i]=a[i]*b[j*4]+a[4+i]*b[j*4+1]+a[8+i]*b[j*4+2]+a[12+i]*b[j*4+3];
    return r;
  }
  function bimSceneFrameDone(B,mode){""")

# ---- WebGL: the chunks out of view skipped -----------------------------------------------------------
rep("""    var gl=G.gl,F=bimSceneSync(),B=F.S,i,c;
    for(i=0;i<B.chunks.length;i++){
      c=B.chunks[i];
      if(c.gl&&c.gl.ver===c.ver)continue;""", """    var gl=G.gl,F=bimSceneSync(),B=F.S,i,c;
    bimSceneCull(B,V,W,H);   /* __acad3dV155 */
    for(i=0;i<B.chunks.length;i++){
      c=B.chunks[i];
      if(c.gl&&c.gl.ver===c.ver)continue;""")
rep("""        var ck=B.chunks[k];if(!ck.count)continue;
        gl.bindBuffer(gl.ARRAY_BUFFER,ck.gl.buf);""", """        var ck=B.chunks[k];if(!ck.count||ck.cull)continue;
        gl.bindBuffer(gl.ARRAY_BUFFER,ck.gl.buf);""")
rep("""        var ck=B.chunks[k];if(!ck.ecount)continue;
        gl.bindBuffer(gl.ARRAY_BUFFER,ck.gl.ebuf);""", """        var ck=B.chunks[k];if(!ck.ecount||ck.cull)continue;
        gl.bindBuffer(gl.ARRAY_BUFFER,ck.gl.ebuf);""")

# ---- WebGPU: a bundle per chunk and pass ---------------------------------------------------------------
rep("""    var dev=P.device,F=bimSceneSync(),B=F.S,i,c,re=false;""", """    var dev=P.device,F=bimSceneSync(),B=F.S,i,c,re=false;
    bimSceneCull(B,V,W,H);   /* __acad3dV155 */""")
rep("""      P.bg=dev.createBindGroup({layout:P.bgl,entries:[{binding:0,resource:{buffer:P.ubuf}},{binding:1,resource:{buffer:P.tab}}]});""",
    """      P.bg=dev.createBindGroup({layout:P.bgl,entries:[{binding:0,resource:{buffer:P.ubuf}},{binding:1,resource:{buffer:P.tab}}]});
      P.bgv=(P.bgv||0)+1;   /* __acad3dV155: every chunk's bundles were recorded with the old one */""")
rep("""    /* the draws, recorded once and replayed until something they draw from changes */
    var key=B.chunks.length+':'+(F.hasTrans?1:0)+':'+(F.edges?1:0);
    for(i=0;i<B.chunks.length;i++)key+=':'+B.chunks[i].count+'/'+B.chunks[i].ecount;
    if(re||!P.bundle||P.bkey!==key){
      var be=dev.createRenderBundleEncoder({colorFormats:[P.format],depthStencilFormat:'depth24plus',sampleCount:4}),nd=0;
      be.setBindGroup(0,P.bg);
      var run=function(pp,edge){
        be.setPipeline(pp);
        for(var k=0;k<B.chunks.length;k++){
          var ck=B.chunks[k],n=edge?ck.ecount:ck.count;
          if(!n)continue;
          be.setVertexBuffer(0,edge?ck.gpu.ebuf:ck.gpu.buf);be.draw(n);nd++;
        }
      };
      run(P.pipes.face0,0);
      if(F.hasTrans)run(P.pipes.face1,0);
      if(F.edges){run(P.pipes.edge0,1);if(F.hasTrans)run(P.pipes.edge1,1);}
      P.bundle=be.finish();P.bkey=key;P.bdraws=nd;B.st.recorded=1;
    }""", """    /* __acad3dV155: a bundle a chunk and pass, recorded when first wanted and kept with the chunk;
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
    P.bdraws=ALL.length;B.st.recorded=rec;""")
rep("""    pass.executeBundles([P.bundle]);""", """    pass.executeBundles(ALL);""")

# ---- the benchmark -------------------------------------------------------------------------------------
rep("""  /* GRAPHICS: which engine draws, and the choice of WebGL for this browser */""",
    """  /* __acad3dV155: n boxes in a grid, each its own element sharing one mesh, as a family's */
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
  /* GRAPHICS: which engine draws, and the choice of WebGL for this browser */""")
rep("""    srows+=bimPropRow('Graphics','<span class="a3d-pstatic" data-graphics="1">'+bimEsc(bimGraphicsLabel())+'</span>');   /* __acad3dV153 */""",
    """    srows+=bimPropRow('Graphics','<span class="a3d-pstatic" data-graphics="1">'+bimEsc(bimGraphicsLabel())+'</span>');   /* __acad3dV153 */
    if(A3D_BENCH&&!A3D_BENCH.running)srows+=bimPropRow('Benchmark','<span class="a3d-pstatic" data-bench="1">'+bimEsc(bimBenchmarkText(A3D_BENCH))+'</span>');   /* __acad3dV155 */""")
rep("""    ['GRAPHICS',['RENDERER','WEBGPU','WEBGL'],'graphics',""",
    """    ['BENCHMARK',['BENCH','FRAMETIME','SPEEDTEST'],'benchmark','Time this device drawing 5,000 and 20,000 elements, with WebGPU and with WebGL; the model is put back as it was'],   /* __acad3dV155 */
    ['GRAPHICS',['RENDERER','WEBGPU','WEBGL'],'graphics',""")
rep("""    graphics:function(){bimGraphicsCommand();},   /* __acad3dV153 */""",
    """    graphics:function(){bimGraphicsCommand();},   /* __acad3dV153 */
    benchmark:function(){bimBenchmark();},   /* __acad3dV155 */""")

# ---- hooks ---------------------------------------------------------------------------------------------
i0 = t.index("  window.__a3dStressModel=function(n,size){")
i1 = t.index("  window.__a3dTestSetObjs=function(list){")
t = t[:i0] + """  window.__a3dStressModel=function(n,size){var r=bimStressModel(n,size);paint();return r;};   /* __acad3dV155: the app's own */
  window.__a3dRenderBench=function(frames){return bimRenderBench(frames).then(function(r){paint();return r;});};
  window.__a3dBenchmark=function(){return bimBenchmark().then(function(r){return JSON.parse(JSON.stringify(r));});};
  window.__a3dCull=function(on){if(on!==undefined){A3D_CULL=!!on;paint();}return A3D_CULL;};
  window.__a3dChunkCells=function(){var B=A3D_SCENE;return B?B.chunks.map(function(c){return {cell:c.cell,objects:c.ids.length,cull:c.cull,box:c.wb?c.wb.slice(0,6):null};}):[];};
""" + t[i1:]
rep("""  var BIM_APP_VERSION={v:'V154',date:'2026-10-04'};   /* __acad3dV154 */""",
    """  var BIM_APP_VERSION={v:'V155',date:'2026-10-04'};   /* __acad3dV155 */""")
rep("""  window.__acad3dV154='edgepull,""",
    """  window.__acad3dV155='spatialchunks,chunkboxes,culling,bundleperchunk,benchmark,benchstat';
  window.__acad3dV154='edgepull,""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
