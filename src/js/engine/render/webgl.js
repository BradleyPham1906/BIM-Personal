  // ---- __acad3dV27: WebGL renderer. The canvas-2D path transformed every vertex, sorted every
  // polygon by depth, and issued one ctx.fill() PER FACE, every frame -- measured at ~16fps by
  // 12k faces, which is why a real IFC import was unusable. Solids now render on the GPU;
  // canvas-2D stays on top as a transparent overlay for grid, sketches, rooms, dimensions,
  // text, grips, marquee and the view cube (low face count, and vector lines look better in 2D).
  // Design choices that matter:
  //  - PER-OBJECT buffers cached by mesh REFERENCE. Every geometry rebuild in this codebase
  //    assigns a fresh o.mesh, so reference identity is an exact, zero-cost dirty check with
  //    no manual invalidation to forget.
  //  - Object position is a UNIFORM, not baked into vertices, so dragging costs a uniform
  //    update rather than a re-upload, and a 300k-face import is ONE draw call.
  //  - Projection matrices were derived from, and verified against, the existing toScreen() to
  //    sub-pixel accuracy, so GPU rendering and CPU picking agree exactly. If they diverged,
  //    clicks would silently land on the wrong object.
  //  - Falls back to the canvas-2D path if WebGL is unavailable.
  var A3D_GL=null,A3D_GL_FAILED=false;
  var GL_EDGE_FACE_LIMIT=20000;
  var BIM_EDGE_PULL=0.0002;   /* __acad3dV154: an outline vertex moved toward the eye by this part of its distance */
  function bimGlViewMatrix(V){
    var r=V.r,u=V.u,d=V.d,e=V.eye;
    return new Float32Array([
      r[0],u[0],d[0],0,
      r[1],u[1],d[1],0,
      r[2],u[2],d[2],0,
      -(r[0]*e[0]+r[1]*e[1]+r[2]*e[2]),
      -(u[0]*e[0]+u[1]*e[1]+u[2]*e[2]),
      -(d[0]*e[0]+d[1]*e[1]+d[2]*e[2]),1
    ]);
  }
  function bimGlProjMatrix(W,H,flat,camDist){
    var near=camDist>1000?camDist/2000:0.5,far=Math.max(4000,camDist*8);   /* __acad3dV133e: the view's own depth */
    if(flat){
      var k=H*1.2/Math.max(camDist,0.5);
      return new Float32Array([
        k/(W/2),0,0,0, 0,k/(H/2),0,0,
        0,0,-2/(far-near),0, 0,0,-(far+near)/(far-near),1
      ]);
    }
    var f=H*1.2;
    return new Float32Array([
      f/(W/2),0,0,0, 0,f/(H/2),0,0,
      0,0,-(far+near)/(far-near),-1, 0,0,-2*far*near/(far-near),0
    ]);
  }
  function bimGlCompile(gl,type,src){
    var sh=gl.createShader(type);
    gl.shaderSource(sh,src);gl.compileShader(sh);
    if(!gl.getShaderParameter(sh,gl.COMPILE_STATUS)){
      console.warn('[BIM] shader compile failed: '+gl.getShaderInfoLog(sh));
      return null;
    }
    return sh;
  }
  function bimGlInit(){
    if(A3D_GL)return A3D_GL;
    if(A3D_GL_FAILED)return null;
    var cv=document.getElementById('a3d-glcanvas');
    if(!cv)return null;
    var gl=null;
    try{gl=cv.getContext('webgl',{antialias:true,alpha:false,depth:true})||cv.getContext('experimental-webgl');}
    catch(eG){gl=null;}
    if(!gl){console.warn('[BIM] WebGL unavailable; using the canvas-2D renderer.');A3D_GL_FAILED=true;return null;}
    var vsrc='attribute vec3 aPos;attribute vec3 aNorm;'+
      'uniform mat4 uView;uniform mat4 uProj;uniform vec3 uOffset;uniform vec3 uEye;uniform float uPull;'+
      'varying vec3 vNorm;'+
      'void main(){vNorm=aNorm;vec3 w=aPos+uOffset;w+=(uEye-w)*uPull;gl_Position=uProj*uView*vec4(w,1.0);}';   /* __acad3dV154: uPull for outlines */
    var fsrc='precision mediump float;varying vec3 vNorm;'+
      'uniform vec3 uColor;uniform vec3 uLight;uniform float uBoost;uniform float uFlatCol;uniform float uAlpha;'+   /* __acad3dV121 */
      'void main(){'+
      ' if(uFlatCol>0.5){gl_FragColor=vec4(uColor,uAlpha);return;}'+
      ' float k=0.45+0.55*abs(dot(normalize(vNorm),uLight));'+
      ' k=min(1.35,k+uBoost);'+
      ' gl_FragColor=vec4(clamp(uColor*k,0.0,1.0),uAlpha);}';
    var vs=bimGlCompile(gl,gl.VERTEX_SHADER,vsrc),fs=bimGlCompile(gl,gl.FRAGMENT_SHADER,fsrc);
    if(!vs||!fs){A3D_GL_FAILED=true;return null;}
    var prog=gl.createProgram();
    gl.attachShader(prog,vs);gl.attachShader(prog,fs);gl.linkProgram(prog);
    if(!gl.getProgramParameter(prog,gl.LINK_STATUS)){
      console.warn('[BIM] shader link failed: '+gl.getProgramInfoLog(prog));
      A3D_GL_FAILED=true;return null;
    }
    A3D_GL={gl:gl,cv:cv,prog:prog,bufs:{},
      loc:{pos:gl.getAttribLocation(prog,'aPos'),norm:gl.getAttribLocation(prog,'aNorm'),
        view:gl.getUniformLocation(prog,'uView'),proj:gl.getUniformLocation(prog,'uProj'),
        offset:gl.getUniformLocation(prog,'uOffset'),color:gl.getUniformLocation(prog,'uColor'),
        light:gl.getUniformLocation(prog,'uLight'),boost:gl.getUniformLocation(prog,'uBoost'),
        flatCol:gl.getUniformLocation(prog,'uFlatCol'),alpha:gl.getUniformLocation(prog,'uAlpha'),   /* __acad3dV121 */
        eye:gl.getUniformLocation(prog,'uEye'),pull:gl.getUniformLocation(prog,'uPull')}};   /* __acad3dV154 */
    return A3D_GL;
  }
  function bimHexToRgb(hex){
    var n=parseInt(String(hex||'#7f9db8').slice(1),16);
    if(!isFinite(n))n=0x7f9db8;
    return [((n>>16)&255)/255,((n>>8)&255)/255,(n&255)/255];
  }
  function bimGlBuildObjBuffer(G,m){
    var gl=G.gl,tri=[],nrm=[],edge=[],i,j;
    for(i=0;i<m.f.length;i++){
      var fc=m.f[i];
      if(fc.length<3)continue;
      var wp=[];
      for(j=0;j<fc.length;j++)wp.push(m.v[fc[j]]);
      var n=faceNormal(wp);
      for(j=2;j<fc.length;j++){
        var a=m.v[fc[0]],b=m.v[fc[j-1]],c=m.v[fc[j]];
        tri.push(a[0],a[1],a[2], b[0],b[1],b[2], c[0],c[1],c[2]);
        nrm.push(n[0],n[1],n[2], n[0],n[1],n[2], n[0],n[1],n[2]);
      }
      for(j=0;j<fc.length;j++){
        var p1=m.v[fc[j]],p2=m.v[fc[(j+1)%fc.length]];
        edge.push(p1[0],p1[1],p1[2], p2[0],p2[1],p2[2]);
      }
    }
    function mk(arr){
      var b=gl.createBuffer();
      gl.bindBuffer(gl.ARRAY_BUFFER,b);
      gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(arr),gl.STATIC_DRAW);
      return b;
    }
    return {meshRef:m,pos:mk(tri),norm:mk(nrm),count:tri.length/3,
      edge:edge.length?mk(edge):null,edgeCount:edge.length/3,faces:m.f.length};
  }
  function bimGlDisposeBuffer(G,rec){
    var gl=G.gl;
    if(rec.pos)gl.deleteBuffer(rec.pos);
    if(rec.norm)gl.deleteBuffer(rec.norm);
    if(rec.edge)gl.deleteBuffer(rec.edge);
  }
