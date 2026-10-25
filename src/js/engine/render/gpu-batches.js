  /* ================= __acad3dV152: the scene in GPU-friendly batches =================
     One description of the scene, read by both engines (__acad3dV153: WebGL and WebGPU):
     chunks of merged triangles and edges, each vertex tagged with its object's slot, and a table
     of each object's offset, transparency, colour and selection, two texels (32 bytes) a slot.
     The description keeps the arrays; each engine keeps its own copies on the GPU and its own
     record of which rows of the table it has yet to receive. */
  var A3D_GL_BATCH=true;
  var BIM_GB_CHUNK=196608,BIM_GB_TEXW=1024;
  var BIM_GB_CELL=64,A3D_CULL=true;   /* __acad3dV155: chunks by 64 m cells of the ground; the ones out of view not drawn */
  function bimMeshBox(m){
    var b=[Infinity,Infinity,Infinity,-Infinity,-Infinity,-Infinity],i,p;
    for(i=0;i<m.v.length;i++){p=m.v[i];if(p[0]<b[0])b[0]=p[0];if(p[1]<b[1])b[1]=p[1];if(p[2]<b[2])b[2]=p[2];if(p[0]>b[3])b[3]=p[0];if(p[1]>b[4])b[4]=p[1];if(p[2]>b[5])b[5]=p[2];}
    return b;
  }
  var A3D_SCENE=null;
  function bimScene(){
    return A3D_SCENE||(A3D_SCENE={cap:0,data:null,slots:{},free:[],next:0,chunks:[],of:{},dirty:{},cells:{},mark:{},n:0,
      st:null,tot:{frames:0,rebuilt:0,rebuiltVerts:0,uploads:0,uploadBytes:0,recorded:0}});
  }
  /* an engine's record of the table: rows lo..hi still to send, or all of it when it has none */
  function bimSceneDirty(S,eng){return S.dirty[eng]||(S.dirty[eng]={lo:-1,hi:-1,cap:0});}
  function bimGbSlot(B,id){
    if(B.slots.hasOwnProperty(id))return B.slots[id];
    var s=B.free.length?B.free.pop():B.next++;
    if(s>=B.cap){
      var cap=Math.max(512,B.cap*2),d=new Float32Array(cap*8);
      if(B.data)d.set(B.data);
      B.data=d;B.cap=cap;
    }
    B.slots[id]=s;
    return s;
  }
  var BIM_GB_TMP=null;
  function bimGbPut(B,s,v){
    var d=B.data,o=s*8,i,ch=false,f=BIM_GB_TMP||(BIM_GB_TMP=new Float32Array(8)),k,R;
    for(i=0;i<8;i++)f[i]=v[i];   /* compared as stored: a colour of n/255 is not exact in 32 bits */
    for(i=0;i<8;i++)if(d[o+i]!==f[i]){d[o+i]=f[i];ch=true;}
    if(ch)for(k in B.dirty)if(B.dirty.hasOwnProperty(k)){R=B.dirty[k];if(R.lo<0||s<R.lo)R.lo=s;if(s>R.hi)R.hi=s;}
  }
  function bimGbVerts(m){var n=0,i;for(i=0;i<m.f.length;i++)if(m.f[i].length>=3)n+=(m.f[i].length-2)*3;return n;}
  /* a chunk's arrays, from its objects' meshes; a mesh shared by many objects is triangulated once */
  function bimGbBuild(B,c){
    var n=0,e=0,i,j,k,id,m,cache=[],fv,ev,tri,ed;
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
    c.tri=tri;c.ed=ed;c.count=n;c.ecount=e;c.verts=n;c.dirty=false;c.ver=(c.ver||0)+1;
    B.st.rebuilt++;B.st.rebuiltVerts+=n;
  }
  /* a chunk's GPU copies, in either engine */
  function bimGbChunkFree(c){
    if(c.gl&&A3D_GL){A3D_GL.gl.deleteBuffer(c.gl.buf);A3D_GL.gl.deleteBuffer(c.gl.ebuf);}
    if(c.gpu){if(c.gpu.buf)c.gpu.buf.destroy();if(c.gpu.ebuf)c.gpu.ebuf.destroy();}
    c.gl=null;c.gpu=null;
  }
  /* the description given back, with both engines' copies */
  function bimSceneRelease(){
    var S=A3D_SCENE,i;
    if(!S)return;
    for(i=0;i<S.chunks.length;i++)bimGbChunkFree(S.chunks[i]);
    A3D_SCENE=null;
    if(A3D_GL&&A3D_GL.gb)A3D_GL.gb.texCap=0;
    if(A3D_GPU.tab){A3D_GPU.tab.destroy();A3D_GPU.tab=null;A3D_GPU.tabCap=0;A3D_GPU.bundle=null;}
  }
  /* the frame's part common to both engines: the table brought up to date, the chunks that
     changed rebuilt. Returns what the engine needs to draw. */
  function bimSceneSync(){
    var B=bimScene(),i,o,m,id,c,seenN=0,mark=B.mark,totalFaces=0,hasTrans=false,sel=A3D.sel,sel2=A3D.sel2,v=[0,0,0,0,0,0,0,0],t0=performance.now(),rgbOf={},typeCol={};   /* __acad3dV156 */
    B.st={draws:0,chunks:0,rebuilt:0,rebuiltVerts:0,uploads:0,uploadBytes:0,objects:0,culled:0,recorded:0};
    A3D.lastGlAlpha={};
    B.frame=(B.frame||0)+1;
    for(i=0;i<B.chunks.length;i++)if(!B.chunks[i].wb)B.chunks[i].wb=[0,0,0,0,0,0];
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];m=meshOf(o);
      if(!m||!m.f||!m.f.length)continue;
      id=o.id;if(mark[id]!==B.frame){mark[id]=B.frame;seenN++;}B.st.objects++;   /* __acad3dV156: seen this frame, counted */
      var s=bimGbSlot(B,id);
      c=B.of[id];
      if(!c){   /* __acad3dV155: into the open chunk of its cell */
        var nv=bimGbVerts(m),lb=bimMeshBox(m),cell=Math.floor((o.pos[0]+(lb[0]+lb[3])/2)/BIM_GB_CELL)+','+Math.floor((o.pos[2]+(lb[2]+lb[5])/2)/BIM_GB_CELL),last=B.cells[cell];
        if(!last||last.verts+nv>BIM_GB_CHUNK){last={ids:[],refs:{},lb:{},verts:0,count:0,ecount:0,tri:null,ed:null,ver:0,gl:null,gpu:null,dirty:true,cell:cell,wb:[0,0,0,0,0,0],cull:false};B.chunks.push(last);B.cells[cell]=last;}
        last.ids.push(id);last.refs[id]=m;last.lb[id]=lb;last.verts+=nv;last.dirty=true;B.of[id]=last;c=last;B.n++;
      }else if(c.refs[id]!==m){c.verts+=bimGbVerts(m)-bimGbVerts(c.refs[id]);c.refs[id]=m;c.lb[id]=bimMeshBox(m);c.dirty=true;}
      /* the chunk's box: its objects where they stand now */
      var wb=c.wb,ob=c.lb[id];
      if(wb.f!==B.frame){wb[0]=wb[1]=wb[2]=Infinity;wb[3]=wb[4]=wb[5]=-Infinity;wb.f=B.frame;}
      if(o.pos[0]+ob[0]<wb[0])wb[0]=o.pos[0]+ob[0];if(o.pos[1]+ob[1]<wb[1])wb[1]=o.pos[1]+ob[1];if(o.pos[2]+ob[2]<wb[2])wb[2]=o.pos[2]+ob[2];
      if(o.pos[0]+ob[3]>wb[3])wb[3]=o.pos[0]+ob[3];if(o.pos[1]+ob[4]>wb[4])wb[4]=o.pos[1]+ob[4];if(o.pos[2]+ob[5]>wb[5])wb[5]=o.pos[2]+ob[5];
      var shown=bimLayerShown(o)&&bimObjectVisibleOnLevel(o),la=1,col=null;
      if(shown){
        la=bimLayerAlpha(o);A3D.lastGlAlpha[id]=la;totalFaces+=m.f.length;if(la<1)hasTrans=true;
        var hx=bimLensCol(o)||o.col;
        if(!hx){hx=typeCol[o.t];if(hx===undefined)hx=typeCol[o.t]=(TYPES[o.t]&&TYPES[o.t].c)||'#7f9db8';}   /* __acad3dV156: a type's colour once a frame */
        col=rgbOf[hx]||(rgbOf[hx]=bimHexToRgb(hx));
      }
      v[0]=o.pos[0];v[1]=o.pos[1];v[2]=o.pos[2];v[3]=shown?la:-1;
      v[4]=col?col[0]:0;v[5]=col?col[1]:0;v[6]=col?col[2]:0;v[7]=sel===id?1:(sel2===id?2:0);
      bimGbPut(B,s,v);
    }
    /* the objects gone: out of their chunk, their slot free; looked for only when the count says some are */
    if(seenN!==B.n)B.st.scanned=1;
    if(seenN!==B.n)for(id in B.of)if(B.of.hasOwnProperty(id)&&mark[id]!==B.frame){
      c=B.of[id];c.ids.splice(c.ids.indexOf(id),1);c.verts-=bimGbVerts(c.refs[id]);delete c.refs[id];delete c.lb[id];c.dirty=true;
      delete B.of[id];delete mark[id];B.n--;B.free.push(B.slots[id]);bimGbPut(B,B.slots[id],[0,0,0,-1,0,0,0,0]);delete B.slots[id];
    }
    for(i=B.chunks.length-1;i>=0;i--){
      c=B.chunks[i];
      if(!c.ids.length){bimGbChunkFree(c);B.chunks.splice(i,1);if(B.cells[c.cell]===c)delete B.cells[c.cell];continue;}
      if(c.dirty)bimGbBuild(B,c);
    }
    B.st.prepMs=performance.now()-t0;   /* the table and the rebuilds: the main thread's share */
    return {S:B,totalFaces:totalFaces,hasTrans:hasTrans,edges:totalFaces<=GL_EDGE_FACE_LIMIT};
  }
  /* __acad3dV155: a chunk wholly outside the view is not drawn: its box's eight corners all beyond
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
  function bimSceneFrameDone(B,mode){
    B.st.chunks=B.chunks.length;B.st.mode=mode;
    var T=B.tot;
    T.frames++;T.rebuilt+=B.st.rebuilt;T.rebuiltVerts+=B.st.rebuiltVerts;T.uploads+=B.st.uploads;T.uploadBytes+=B.st.uploadBytes;T.recorded+=B.st.recorded||0;
    A3D.glStats=B.st;
  }
  /* ---- the WebGL engine's side: a program, the table as a float texture ---- */
  function bimGbInit(G){
    if(G.gb!==undefined)return G.gb;
    var gl=G.gl;G.gb=null;
    var ext=gl.getExtension('OES_texture_float');
    if(!ext||!(gl.getParameter(gl.MAX_VERTEX_TEXTURE_IMAGE_UNITS)>0)){console.warn('[BIM] No vertex float textures: drawing object by object.');return null;}
    var vsrc='attribute vec3 aPos;attribute vec3 aNorm;attribute float aObj;'+
      'uniform mat4 uView;uniform mat4 uProj;uniform sampler2D uTab;uniform vec2 uTabSize;uniform float uPass;uniform float uEdge;uniform vec3 uEye;'+
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
      ' vec3 w=aPos+a.xyz;if(uEdge>0.5)w+=(uEye-w)*'+BIM_EDGE_PULL.toFixed(6)+';'+   /* __acad3dV154 */
      ' gl_Position=uProj*uView*vec4(w,1.0);}';
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
    G.gb={prog:prog,tex:gl.createTexture(),texCap:0,texH:0,
      loc:{pos:gl.getAttribLocation(prog,'aPos'),norm:gl.getAttribLocation(prog,'aNorm'),obj:gl.getAttribLocation(prog,'aObj'),
        view:gl.getUniformLocation(prog,'uView'),proj:gl.getUniformLocation(prog,'uProj'),tab:gl.getUniformLocation(prog,'uTab'),
        size:gl.getUniformLocation(prog,'uTabSize'),pass:gl.getUniformLocation(prog,'uPass'),edge:gl.getUniformLocation(prog,'uEdge'),
        light:gl.getUniformLocation(prog,'uLight'),eye:gl.getUniformLocation(prog,'uEye')}};
    return G.gb;
  }
  function bimGbUpload(G,P,B){
    var gl=G.gl,R=bimSceneDirty(B,'gl');
    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D,P.tex);
    if(P.texCap!==B.cap){   /* new, or grown: sent whole */
      P.texCap=B.cap;P.texH=Math.ceil(B.cap*2/BIM_GB_TEXW);
      gl.pixelStorei(gl.UNPACK_ALIGNMENT,1);
      gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.NEAREST);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.NEAREST);
      gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);
      gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,BIM_GB_TEXW,P.texH,0,gl.RGBA,gl.FLOAT,B.data);
      R.lo=-1;R.hi=-1;B.st.uploads++;B.st.uploadBytes+=B.data.length*4;
      return;
    }
    if(R.lo<0)return;
    var r0=Math.floor(R.lo*2/BIM_GB_TEXW),r1=Math.floor((R.hi*2+1)/BIM_GB_TEXW),per=BIM_GB_TEXW*4;
    gl.texSubImage2D(gl.TEXTURE_2D,0,0,r0,BIM_GB_TEXW,r1-r0+1,gl.RGBA,gl.FLOAT,B.data.subarray(r0*per,(r1+1)*per));
    B.st.uploads++;B.st.uploadBytes+=(r1-r0+1)*per*4;
    R.lo=-1;R.hi=-1;
  }
  /* the frame with WebGL: the description brought up to date, the chunks it has not got sent,
     then drawn */
  /* __acad3dV156: the description brought up to date and what WebGL lacks of it sent */
  function bimGbPrepare(G,P,V,W,H){
    var gl=G.gl,F=bimSceneSync(),B=F.S,i,c;
    bimSceneCull(B,V,W,H);   /* __acad3dV155 */
    for(i=0;i<B.chunks.length;i++){
      c=B.chunks[i];
      if(c.gl&&c.gl.ver===c.ver)continue;
      if(!c.gl)c.gl={buf:gl.createBuffer(),ebuf:gl.createBuffer(),ver:0};
      gl.bindBuffer(gl.ARRAY_BUFFER,c.gl.buf);gl.bufferData(gl.ARRAY_BUFFER,c.tri,gl.STATIC_DRAW);
      gl.bindBuffer(gl.ARRAY_BUFFER,c.gl.ebuf);gl.bufferData(gl.ARRAY_BUFFER,c.ed,gl.STATIC_DRAW);
      c.gl.ver=c.ver;
    }
    bimGbUpload(G,P,B);
    return F;
  }
  function bimGbRender(G,V,W,H){
    var P=bimGbInit(G);
    if(!P)return false;
    var gl=G.gl,F=bimGbPrepare(G,P,V,W,H),B=F.S,i,c;
    var L=P.loc,stride=28;
    gl.useProgram(P.prog);
    gl.uniformMatrix4fv(L.view,false,bimGlViewMatrix(V));
    gl.uniformMatrix4fv(L.proj,false,bimGlProjMatrix(W,H,A3D.flat,A3D.cam.dist));
    gl.uniform3f(L.light,LIGHT[0],LIGHT[1],LIGHT[2]);
    gl.uniform3f(L.eye,V.eye[0],V.eye[1],V.eye[2]);   /* __acad3dV154 */
    gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,P.tex);
    gl.uniform1i(L.tab,0);gl.uniform2f(L.size,BIM_GB_TEXW,P.texH||1);
    function faces(pass){
      gl.uniform1f(L.pass,pass);gl.uniform1f(L.edge,0);
      gl.enableVertexAttribArray(L.pos);gl.enableVertexAttribArray(L.norm);gl.enableVertexAttribArray(L.obj);
      for(var k=0;k<B.chunks.length;k++){
        var ck=B.chunks[k];if(!ck.count||ck.cull)continue;
        gl.bindBuffer(gl.ARRAY_BUFFER,ck.gl.buf);
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
        var ck=B.chunks[k];if(!ck.ecount||ck.cull)continue;
        gl.bindBuffer(gl.ARRAY_BUFFER,ck.gl.ebuf);
        gl.vertexAttribPointer(L.pos,3,gl.FLOAT,false,16,0);
        gl.vertexAttribPointer(L.obj,1,gl.FLOAT,false,16,12);
        gl.drawArrays(gl.LINES,0,ck.ecount);B.st.draws++;
      }
    }
    faces(0);
    if(F.hasTrans){
      gl.enable(gl.BLEND);gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);gl.depthMask(false);
      faces(1);
      gl.depthMask(true);gl.disable(gl.BLEND);
    }
    if(F.edges){
      edges(0);
      if(F.hasTrans){gl.enable(gl.BLEND);gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);edges(1);gl.disable(gl.BLEND);}
    }
    gl.disableVertexAttribArray(L.pos);gl.disableVertexAttribArray(L.obj);
    bimSceneFrameDone(B,'batched');
    A3D.glFaces=F.totalFaces;
    return true;
  }
