"""patch_phase152a.py -- V152: the 3D scene drawn in GPU-friendly batches (Render R1).

Until V151 the WebGL renderer drew object by object: for each one, about ten calls to set its
offset, colour, highlight and transparency, bind its buffers and draw; its edges as many again.
5,000 elements were about 100,000 calls a frame, each paid on the main thread.

Now the scene is one shared description that a WebGPU engine (V153) will read as well:
- the objects' triangles merged into large buffers ("chunks", at most 196,608 vertices each),
  every vertex carrying its object's slot; edges merged the same way;
- each object's offset, transparency, colour and selection in one table of two texels a slot (a
  float texture the vertex shader reads), uploaded only for the rows that changed;
- a chunk is rebuilt only when one of its objects' meshes changes, is added or is removed; a
  hidden object (layer off, another level) stays in its chunk and is dropped by the shader, so
  showing it again rebuilds nothing; a frame that only moves the camera rebuilds nothing at all;
- opaque solids, then the transparent ones blended without writing depth, then the edges: the
  same order and the same shading as before, in a few draw calls a chunk.
Devices without float textures or vertex textures keep the per-object path, which stays as the
fallback (and as the measure: __a3dGlBatch(false) switches to it)."""
NAME = 'patch_phase152a.py'
BASE = '7837b8047ea47d646d6303f4cd81af7a1cc059d122307fb9bd48c6897a8f82e8'
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


# ---- the engine: batches and the object table -------------------------------------------------
rep("""  function bimGlDisposeBuffer(G,rec){
    var gl=G.gl;
    if(rec.pos)gl.deleteBuffer(rec.pos);
    if(rec.norm)gl.deleteBuffer(rec.norm);
    if(rec.edge)gl.deleteBuffer(rec.edge);
  }
""", """  function bimGlDisposeBuffer(G,rec){
    var gl=G.gl;
    if(rec.pos)gl.deleteBuffer(rec.pos);
    if(rec.norm)gl.deleteBuffer(rec.norm);
    if(rec.edge)gl.deleteBuffer(rec.edge);
  }
  /* ================= __acad3dV152: the scene in GPU-friendly batches =================
     One description of the scene, read by the WebGL engine now and the WebGPU engine next:
     chunks of merged triangles and edges, each vertex tagged with its object's slot, and a table
     of each object's offset, transparency, colour and selection, two texels a slot. */
  var A3D_GL_BATCH=true;
  var BIM_GB_CHUNK=196608,BIM_GB_TEXW=1024;
  function bimGbInit(G){
    if(G.gb!==undefined)return G.gb;
    var gl=G.gl;G.gb=null;
    var ext=gl.getExtension('OES_texture_float');
    if(!ext||!(gl.getParameter(gl.MAX_VERTEX_TEXTURE_IMAGE_UNITS)>0)){console.warn('[BIM] No vertex float textures: drawing object by object.');return null;}
    var vsrc='attribute vec3 aPos;attribute vec3 aNorm;attribute float aObj;'+
      'uniform mat4 uView;uniform mat4 uProj;uniform sampler2D uTab;uniform vec2 uTabSize;uniform float uPass;uniform float uEdge;'+
      'varying vec3 vNorm;varying vec4 vCol;varying float vBoost;varying float vEdge;'+
      'void main(){'+
      ' vEdge=uEdge;float t=aObj*2.0;float row=floor(t/uTabSize.x);float col=t-row*uTabSize.x;'+
      ' vec4 a=texture2D(uTab,vec2((col+0.5)/uTabSize.x,(row+0.5)/uTabSize.y));'+
      ' vec4 b=texture2D(uTab,vec2((col+1.5)/uTabSize.x,(row+0.5)/uTabSize.y));'+
      ' bool tr=a.w<0.999;'+
      ' if(a.w<0.0||(uPass<0.5&&tr)||(uPass>0.5&&!tr)){gl_Position=vec4(2.0,2.0,2.0,1.0);vNorm=vec3(0.0,1.0,0.0);vCol=vec4(0.0);vBoost=0.0;return;}'+
      ' vNorm=aNorm;vBoost=0.0;'+
      ' if(uEdge>0.5){vCol=vec4(b.w>1.5?vec3(1.0,0.706,0.329):(b.w>0.5?vec3(0.306,0.631,1.0):vec3(0.09,0.10,0.11)),a.w);}'+
      ' else{vCol=vec4(b.xyz,a.w);if(b.w>0.5&&b.w<1.5)vBoost=0.25;}'+
      ' gl_Position=uProj*uView*vec4(aPos+a.xyz,1.0);}';
    var fsrc='precision mediump float;varying vec3 vNorm;varying vec4 vCol;varying float vBoost;varying float vEdge;uniform vec3 uLight;'+
      'void main(){'+
      ' if(vEdge>0.5){gl_FragColor=vCol;return;}'+
      ' float k=0.45+0.55*abs(dot(normalize(vNorm),uLight));'+
      ' k=min(1.35,k+vBoost);'+
      ' gl_FragColor=vec4(clamp(vCol.rgb*k,0.0,1.0),vCol.a);}';
    var vs=bimGlCompile(gl,gl.VERTEX_SHADER,vsrc),fs=bimGlCompile(gl,gl.FRAGMENT_SHADER,fsrc);
    if(!vs||!fs)return null;
    var prog=gl.createProgram();
    gl.attachShader(prog,vs);gl.attachShader(prog,fs);gl.bindAttribLocation(prog,0,'aPos');gl.linkProgram(prog);
    if(!gl.getProgramParameter(prog,gl.LINK_STATUS)){console.warn('[BIM] batch shader link failed: '+gl.getProgramInfoLog(prog));return null;}
    G.gb={prog:prog,tex:gl.createTexture(),cap:0,texH:0,data:null,slots:{},free:[],next:0,chunks:[],of:{},lo:-1,hi:-1,
      loc:{pos:gl.getAttribLocation(prog,'aPos'),norm:gl.getAttribLocation(prog,'aNorm'),obj:gl.getAttribLocation(prog,'aObj'),
        view:gl.getUniformLocation(prog,'uView'),proj:gl.getUniformLocation(prog,'uProj'),tab:gl.getUniformLocation(prog,'uTab'),
        size:gl.getUniformLocation(prog,'uTabSize'),pass:gl.getUniformLocation(prog,'uPass'),edge:gl.getUniformLocation(prog,'uEdge'),
        light:gl.getUniformLocation(prog,'uLight')}};
    return G.gb;
  }
  /* the table: room for cap objects; it doubles when full and is sent whole once then */
  function bimGbSlot(B,id){
    if(B.slots.hasOwnProperty(id))return B.slots[id];
    var s=B.free.length?B.free.pop():B.next++;
    if(s>=B.cap){
      var cap=Math.max(512,B.cap*2),d=new Float32Array(cap*8);
      if(B.data)d.set(B.data);
      B.data=d;B.cap=cap;B.texH=Math.ceil(cap*2/BIM_GB_TEXW);B.realloc=true;
    }
    B.slots[id]=s;
    return s;
  }
  var BIM_GB_TMP=null;
  function bimGbPut(B,s,v){
    var d=B.data,o=s*8,i,ch=false,f=BIM_GB_TMP||(BIM_GB_TMP=new Float32Array(8));
    for(i=0;i<8;i++)f[i]=v[i];   /* compared as stored: a colour of n/255 is not exact in 32 bits */
    for(i=0;i<8;i++)if(d[o+i]!==f[i]){d[o+i]=f[i];ch=true;}
    if(ch){if(B.lo<0||s<B.lo)B.lo=s;if(s>B.hi)B.hi=s;}
  }
  function bimGbUpload(G,B){
    var gl=G.gl;
    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D,B.tex);
    if(B.realloc){
      gl.pixelStorei(gl.UNPACK_ALIGNMENT,1);
      gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.NEAREST);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.NEAREST);
      gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);
      gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,BIM_GB_TEXW,B.texH,0,gl.RGBA,gl.FLOAT,B.data);
      B.realloc=false;B.lo=-1;B.hi=-1;B.st.uploads++;B.st.uploadBytes+=B.data.length*4;
      return;
    }
    if(B.lo<0)return;
    var r0=Math.floor(B.lo*2/BIM_GB_TEXW),r1=Math.floor((B.hi*2+1)/BIM_GB_TEXW),per=BIM_GB_TEXW*4;
    gl.texSubImage2D(gl.TEXTURE_2D,0,0,r0,BIM_GB_TEXW,r1-r0+1,gl.RGBA,gl.FLOAT,B.data.subarray(r0*per,(r1+1)*per));
    B.st.uploads++;B.st.uploadBytes+=(r1-r0+1)*per*4;
    B.lo=-1;B.hi=-1;
  }
  function bimGbVerts(m){var n=0,i;for(i=0;i<m.f.length;i++)if(m.f[i].length>=3)n+=(m.f[i].length-2)*3;return n;}
  /* a chunk's buffers, from its objects' meshes; a mesh shared by many objects is triangulated once */
  function bimGbBuild(G,B,c,byId){
    var gl=G.gl,n=0,e=0,i,j,k,id,m,cache=[],fv,ev,tri,ed;
    for(i=0;i<c.ids.length;i++){m=c.refs[c.ids[i]];n+=bimGbVerts(m);for(j=0;j<m.f.length;j++)if(m.f[j].length>=3)e+=m.f[j].length*2;}
    tri=new Float32Array(n*7);ed=new Float32Array(e*4);fv=0;ev=0;
    for(i=0;i<c.ids.length;i++){
      id=c.ids[i];m=c.refs[id];var s=B.slots[id],T=null;
      for(k=0;k<cache.length;k++)if(cache[k][0]===m){T=cache[k][1];break;}
      if(!T){
        T={t:[],e:[]};
        for(j=0;j<m.f.length;j++){
          var fc=m.f[j];if(fc.length<3)continue;
          var wp=[],q;for(q=0;q<fc.length;q++)wp.push(m.v[fc[q]]);
          var nn=faceNormal(wp);
          for(q=2;q<fc.length;q++){var A=m.v[fc[0]],Bv=m.v[fc[q-1]],C=m.v[fc[q]];T.t.push(A[0],A[1],A[2],nn[0],nn[1],nn[2],Bv[0],Bv[1],Bv[2],nn[0],nn[1],nn[2],C[0],C[1],C[2],nn[0],nn[1],nn[2]);}
          for(q=0;q<fc.length;q++){var p1=m.v[fc[q]],p2=m.v[fc[(q+1)%fc.length]];T.e.push(p1[0],p1[1],p1[2],p2[0],p2[1],p2[2]);}
        }
        if(cache.length>64)cache.shift();
        cache.push([m,T]);
      }
      for(j=0;j<T.t.length;j+=6){tri[fv++]=T.t[j];tri[fv++]=T.t[j+1];tri[fv++]=T.t[j+2];tri[fv++]=T.t[j+3];tri[fv++]=T.t[j+4];tri[fv++]=T.t[j+5];tri[fv++]=s;}
      for(j=0;j<T.e.length;j+=3){ed[ev++]=T.e[j];ed[ev++]=T.e[j+1];ed[ev++]=T.e[j+2];ed[ev++]=s;}
    }
    if(!c.buf)c.buf=gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER,c.buf);gl.bufferData(gl.ARRAY_BUFFER,tri,gl.STATIC_DRAW);
    if(!c.ebuf)c.ebuf=gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER,c.ebuf);gl.bufferData(gl.ARRAY_BUFFER,ed,gl.STATIC_DRAW);
    c.count=n;c.ecount=e;c.verts=n;c.dirty=false;
    B.st.rebuilt++;B.st.rebuiltVerts+=n;
  }
  function bimGbDispose(G){
    var B=G.gb,gl=G.gl,i;
    if(!B)return;
    for(i=0;i<B.chunks.length;i++){if(B.chunks[i].buf)gl.deleteBuffer(B.chunks[i].buf);if(B.chunks[i].ebuf)gl.deleteBuffer(B.chunks[i].ebuf);}
    B.chunks=[];B.of={};B.slots={};B.free=[];B.next=0;B.lo=-1;B.hi=-1;if(B.data){B.data=new Float32Array(B.data.length);B.realloc=true;}
  }
  /* the frame: the table brought up to date, the chunks that changed rebuilt, then drawn */
  function bimGbRender(G,V,W,H){
    var B=bimGbInit(G);
    if(!B)return false;
    var gl=G.gl,i,o,m,id,c,seen={},byId={},totalFaces=0,hasTrans=false,sel=A3D.sel,sel2=A3D.sel2,v=[0,0,0,0,0,0,0,0],t0=performance.now(),rgbOf={};
    B.st={draws:0,chunks:0,rebuilt:0,rebuiltVerts:0,uploads:0,uploadBytes:0,objects:0};
    A3D.lastGlAlpha={};
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];m=meshOf(o);
      if(!m||!m.f||!m.f.length)continue;
      id=o.id;seen[id]=1;byId[id]=o;B.st.objects++;
      var s=bimGbSlot(B,id);
      c=B.of[id];
      if(!c){
        var nv=bimGbVerts(m),last=B.chunks[B.chunks.length-1];
        if(!last||last.verts+nv>BIM_GB_CHUNK){last={ids:[],refs:{},verts:0,count:0,ecount:0,buf:null,ebuf:null,dirty:true};B.chunks.push(last);}
        last.ids.push(id);last.refs[id]=m;last.verts+=nv;last.dirty=true;B.of[id]=last;
      }else if(c.refs[id]!==m){c.verts+=bimGbVerts(m)-bimGbVerts(c.refs[id]);c.refs[id]=m;c.dirty=true;}
      var shown=bimLayerShown(o)&&bimObjectVisibleOnLevel(o),la=1,col=null;
      if(shown){
        la=bimLayerAlpha(o);A3D.lastGlAlpha[id]=la;totalFaces+=m.f.length;if(la<1)hasTrans=true;
        var hx=bimLensCol(o)||o.col||(TYPES[o.t]||{}).c||'#7f9db8';col=rgbOf[hx]||(rgbOf[hx]=bimHexToRgb(hx));
      }
      v[0]=o.pos[0];v[1]=o.pos[1];v[2]=o.pos[2];v[3]=shown?la:-1;
      v[4]=col?col[0]:0;v[5]=col?col[1]:0;v[6]=col?col[2]:0;v[7]=sel===id?1:(sel2===id?2:0);
      bimGbPut(B,s,v);
    }
    /* the objects gone: out of their chunk, their slot free */
    for(id in B.of)if(B.of.hasOwnProperty(id)&&!seen[id]){
      c=B.of[id];c.ids.splice(c.ids.indexOf(id),1);c.verts-=bimGbVerts(c.refs[id]);delete c.refs[id];c.dirty=true;
      delete B.of[id];B.free.push(B.slots[id]);bimGbPut(B,B.slots[id],[0,0,0,-1,0,0,0,0]);delete B.slots[id];
    }
    for(i=B.chunks.length-1;i>=0;i--){
      c=B.chunks[i];
      if(!c.ids.length){if(c.buf)gl.deleteBuffer(c.buf);if(c.ebuf)gl.deleteBuffer(c.ebuf);B.chunks.splice(i,1);continue;}
      if(c.dirty)bimGbBuild(G,B,c,byId);
    }
    bimGbUpload(G,B);
    B.st.prepMs=performance.now()-t0;   /* the table and the rebuilds: the main thread's share */
    var L=B.loc,stride=28;
    gl.useProgram(B.prog);
    gl.uniformMatrix4fv(L.view,false,bimGlViewMatrix(V));
    gl.uniformMatrix4fv(L.proj,false,bimGlProjMatrix(W,H,A3D.flat,A3D.cam.dist));
    gl.uniform3f(L.light,LIGHT[0],LIGHT[1],LIGHT[2]);
    gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,B.tex);
    gl.uniform1i(L.tab,0);gl.uniform2f(L.size,BIM_GB_TEXW,B.texH||1);
    function faces(pass){
      gl.uniform1f(L.pass,pass);gl.uniform1f(L.edge,0);
      gl.enableVertexAttribArray(L.pos);gl.enableVertexAttribArray(L.norm);gl.enableVertexAttribArray(L.obj);
      for(var k=0;k<B.chunks.length;k++){
        var ck=B.chunks[k];if(!ck.count)continue;
        gl.bindBuffer(gl.ARRAY_BUFFER,ck.buf);
        gl.vertexAttribPointer(L.pos,3,gl.FLOAT,false,stride,0);
        gl.vertexAttribPointer(L.norm,3,gl.FLOAT,false,stride,12);
        gl.vertexAttribPointer(L.obj,1,gl.FLOAT,false,stride,24);
        gl.drawArrays(gl.TRIANGLES,0,ck.count);B.st.draws++;
      }
      gl.disableVertexAttribArray(L.norm);
    }
    function edges(pass){
      gl.uniform1f(L.pass,pass);gl.uniform1f(L.edge,1);
      gl.enableVertexAttribArray(L.pos);gl.enableVertexAttribArray(L.obj);
      gl.disableVertexAttribArray(L.norm);gl.vertexAttrib3f(L.norm,0,1,0);
      for(var k=0;k<B.chunks.length;k++){
        var ck=B.chunks[k];if(!ck.ecount)continue;
        gl.bindBuffer(gl.ARRAY_BUFFER,ck.ebuf);
        gl.vertexAttribPointer(L.pos,3,gl.FLOAT,false,16,0);
        gl.vertexAttribPointer(L.obj,1,gl.FLOAT,false,16,12);
        gl.drawArrays(gl.LINES,0,ck.ecount);B.st.draws++;
      }
    }
    faces(0);
    if(hasTrans){
      gl.enable(gl.BLEND);gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);gl.depthMask(false);
      faces(1);
      gl.depthMask(true);gl.disable(gl.BLEND);
    }
    if(totalFaces<=GL_EDGE_FACE_LIMIT){
      edges(0);
      if(hasTrans){gl.enable(gl.BLEND);gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);edges(1);gl.disable(gl.BLEND);}
    }
    gl.disableVertexAttribArray(L.pos);gl.disableVertexAttribArray(L.obj);
    B.st.chunks=B.chunks.length;B.st.mode='batched';
    var T=B.tot||(B.tot={frames:0,rebuilt:0,rebuiltVerts:0,uploads:0,uploadBytes:0});
    T.frames++;T.rebuilt+=B.st.rebuilt;T.rebuiltVerts+=B.st.rebuiltVerts;T.uploads+=B.st.uploads;T.uploadBytes+=B.st.uploadBytes;
    A3D.glStats=B.st;
    A3D.glFaces=totalFaces;
    return true;
  }
""")

# ---- the frame: batched where it can be, object by object where it cannot ------------------
rep("""    bimTerrainDrawGl(G,V,W,H);   /* __acad3dV137: the terrain in 3D, the map draped on it */
    gl.useProgram(G.prog);""", """    bimTerrainDrawGl(G,V,W,H);   /* __acad3dV137: the terrain in 3D, the map draped on it */
    if(A3D_GL_BATCH&&bimGbRender(G,V,W,H)){   /* __acad3dV152: the batches */
      var kb;for(kb in G.bufs)if(G.bufs.hasOwnProperty(kb)){bimGlDisposeBuffer(G,G.bufs[kb]);delete G.bufs[kb];}
      return true;
    }
    if(G.gb&&(G.gb.chunks.length||G.gb.next))bimGbDispose(G);
    var draws=0;   /* __acad3dV152: counted, to set against the batches */
    gl.useProgram(G.prog);""")
rep("""      if(la<1){trans.push([o,rec,la]);continue;}
      bimGlDrawFaces(G,o,rec,1);
    }""", """      if(la<1){trans.push([o,rec,la]);continue;}
      bimGlDrawFaces(G,o,rec,1);draws++;
    }""")
rep("""      for(i=0;i<trans.length;i++)bimGlDrawFaces(G,trans[i][0],trans[i][1],trans[i][2]);""",
    """      for(i=0;i<trans.length;i++){bimGlDrawFaces(G,trans[i][0],trans[i][1],trans[i][2]);draws++;}""")
rep("""        gl.drawArrays(gl.LINES,0,rec2.edgeCount);
      }""", """        gl.drawArrays(gl.LINES,0,rec2.edgeCount);draws++;
      }""")
rep("""    A3D.glFaces=totalFaces;
    return true;
  }
  // Picking still needs""", """    A3D.glFaces=totalFaces;
    A3D.glStats={mode:'object',draws:draws,chunks:0,rebuilt:0,rebuiltVerts:0,uploads:0,uploadBytes:0,objects:Object.keys(G.bufs).length};
    return true;
  }
  // Picking still needs""")

# ---- hooks: the switch, the numbers, a stress model, a bench ----------------------------------
rep("""  window.__a3dGlFaces=function(){return A3D.glFaces||0;};""",
    """  window.__a3dGlFaces=function(){return A3D.glFaces||0;};
  window.__a3dGlBatch=function(on){if(on!==undefined){A3D_GL_BATCH=!!on;paint();}return A3D_GL_BATCH;};   /* __acad3dV152 */
  window.__a3dGlStats=function(){return A3D.glStats?JSON.parse(JSON.stringify(A3D.glStats)):null;};
  window.__a3dGlBatchInfo=function(){var B=A3D_GL&&A3D_GL.gb;if(!B)return null;
    return {chunks:B.chunks.map(function(c){return {objects:c.ids.length,verts:c.count,edges:c.ecount};}),slots:Object.keys(B.slots).length,cap:B.cap,free:B.free.length};};
  window.__a3dGlTotals=function(){var B=A3D_GL&&A3D_GL.gb;return B&&B.tot?JSON.parse(JSON.stringify(B.tot)):{frames:0,rebuilt:0,rebuiltVerts:0,uploads:0,uploadBytes:0};};
  window.__a3dGlTableOf=function(id){var B=A3D_GL&&A3D_GL.gb;if(!B||!B.slots.hasOwnProperty(id))return null;var s=B.slots[id];return [].slice.call(B.data.subarray(s*8,s*8+8));};
  /* a grid of n boxes, each its own element, for measuring; the mesh is shared, as a family's is */
  window.__a3dStressModel=function(n,size){
    var L=[],k=Math.ceil(Math.sqrt(n)),i,sz=size||0.6;
    for(i=0;i<n;i++)L.push({id:'stress-'+i,t:'box',prm:{Length:sz/SCALE,Width:sz/SCALE,Height:(1+(i%7)*0.4)/SCALE},pos:[(i%k)*1.5,0,Math.floor(i/k)*1.5],rot:[0,0,0]});
    A3D.objs=L;A3D.sel=null;A3D.sel2=null;A3D.selSet=[];paint();
    return L.length;
  };
  /* frames drawn with the camera turning a little each time, each finished before the next
     (a pixel read waits for the GPU): the average and the slowest, in milliseconds */
  window.__a3dRenderBench=function(frames){
    var G=bimGlInit();if(!G)return null;
    var c=A3D.cam,y0=c.yaw,W=cvW(),H=cvH(),px=new Uint8Array(4),t,sum=0,mx=0,i,first=0;
    for(i=0;i<(frames||20);i++){
      c.yaw=y0+i*0.01;
      t=performance.now();
      bimGlRender(camVecs(c),W,H);
      G.gl.readPixels(0,0,1,1,G.gl.RGBA,G.gl.UNSIGNED_BYTE,px);
      t=performance.now()-t;
      if(i===0)first=t;else{sum+=t;if(t>mx)mx=t;}
    }
    c.yaw=y0;paint();
    return {first:first,avg:sum/Math.max(1,(frames||20)-1),max:mx,stats:A3D.glStats?JSON.parse(JSON.stringify(A3D.glStats)):null};
  };""")
rep("""  window.__a3dTestForceCpu=function(on){A3D_GL_FAILED=!!on;if(on)A3D_GL=null;};""",
    """  window.__a3dTestForceCpu=function(on){A3D_GL_FAILED=!!on;if(on){if(A3D_GL&&A3D_GL.gb)bimGbDispose(A3D_GL);A3D_GL=null;}};""")

rep("""  var BIM_APP_VERSION={v:'V151',date:'2026-10-04'};   /* __acad3dV151 */""",
    """  var BIM_APP_VERSION={v:'V152',date:'2026-10-04'};   /* __acad3dV152 */""")
rep("""  window.__acad3dV151='branches,""",
    """  window.__acad3dV152='batches,objecttable,chunkrebuild,hiddenstays,transparentpass,edgebatch,fallback,stressmodel,bench';
  window.__acad3dV151='branches,""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
