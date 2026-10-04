"""patch_phase156b.py -- V156: a click on a large model picked by the GPU.

pick() projected every face of every element to the screen on each click (bimBuildPickPolys) and
walked them back to front: about 100 ms at 20,000 elements here, a pause a person feels. Now, on a
model of more than 20,000 faces, the click is answered by an id pass: the batched scene drawn once
into a small offscreen target, each element's slot in its colour, and the one pixel under the
pointer read back. That is the frontmost element there by the depth test, as the projected faces
gave. It is drawn with WebGL, whose read is immediate, even while WebGPU draws the screen.
- The element hit, if it may be picked, is the answer. On a locked layer, the old walk decides, so
  the element behind it is found as before. Nothing hit: the sketches are tried, as before.
- A smaller model keeps the old walk, exactly as it was. PICKGPU is not a command; the hook
  __a3dPickMode('on'|'off'|'auto') is for tests."""
NAME = 'patch_phase156b.py'
BASE = '30aabe74303ce8d1613857fb1e898b351fa79740a894838a2f711163f5a2c779'
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


# the WebGL side's preparation, shared by the frame and the id pass
rep("""  function bimGbRender(G,V,W,H){
    var P=bimGbInit(G);
    if(!P)return false;
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
    var L=P.loc,stride=28;""", """  /* __acad3dV156: the description brought up to date and what WebGL lacks of it sent */
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
    var L=P.loc,stride=28;""")

# the id pass
rep("""  /* ================= __acad3dV153: the WebGPU engine =================""", """  /* ================= __acad3dV156: a click picked by the GPU =================
     The batched scene drawn into an offscreen target, each element's slot+1 in its colour (24 bits),
     only the pixel under the pointer, and that pixel read back. */
  var A3D_PICK_GPU='auto',BIM_PICK_GPU_FACES=20000;
  function bimPickProg(G){
    if(G.pk!==undefined)return G.pk;
    var gl=G.gl;G.pk=null;
    var vs=bimGlCompile(gl,gl.VERTEX_SHADER,'attribute vec3 aPos;attribute float aObj;'+
      'uniform mat4 uView;uniform mat4 uProj;uniform sampler2D uTab;uniform vec2 uTabSize;varying vec3 vId;'+
      'void main(){float t=aObj*2.0;float row=floor(t/uTabSize.x);float col=t-row*uTabSize.x;'+
      ' vec4 a=texture2D(uTab,vec2((col+0.5)/uTabSize.x,(row+0.5)/uTabSize.y));'+
      ' if(a.w<0.0){gl_Position=vec4(2.0,2.0,2.0,1.0);vId=vec3(0.0);return;}'+
      ' float n=aObj+1.0;vId=vec3(mod(n,256.0),mod(floor(n/256.0),256.0),floor(n/65536.0))/255.0;'+
      ' gl_Position=uProj*uView*vec4(aPos+a.xyz,1.0);}');
    var fs=bimGlCompile(gl,gl.FRAGMENT_SHADER,'precision highp float;varying vec3 vId;void main(){gl_FragColor=vec4(vId,1.0);}');
    if(!vs||!fs)return null;
    var p=gl.createProgram();
    gl.attachShader(p,vs);gl.attachShader(p,fs);gl.bindAttribLocation(p,0,'aPos');gl.linkProgram(p);
    if(!gl.getProgramParameter(p,gl.LINK_STATUS)){console.warn('[BIM] pick shader link failed: '+gl.getProgramInfoLog(p));return null;}
    G.pk={prog:p,fb:null,tex:null,rb:null,w:0,h:0,
      pos:gl.getAttribLocation(p,'aPos'),obj:gl.getAttribLocation(p,'aObj'),view:gl.getUniformLocation(p,'uView'),proj:gl.getUniformLocation(p,'uProj'),
      tab:gl.getUniformLocation(p,'uTab'),size:gl.getUniformLocation(p,'uTabSize')};
    return G.pk;
  }
  /* the frontmost element under (x,y), in CSS pixels: {ok,o} -- ok false when the GPU cannot say */
  function bimPickGpu(x,y){
    var G=A3D_GL,P=G&&bimGbInit(G),K=G&&P&&bimPickProg(G);
    if(!K)return {ok:false};
    var gl=G.gl,V=camVecs(A3D.cam),W=cvW(),H=cvH(),gs=cvScale(el.cv),w=Math.max(1,Math.round(W*gs)),h=Math.max(1,Math.round(H*gs));
    var F=bimGbPrepare(G,P,V,W,H),B=F.S,k,c,px=Math.floor(x*gs),py=h-1-Math.floor(y*gs),out=new Uint8Array(4);
    if(px<0||py<0||px>=w||py>=h)return {ok:true,o:null};
    if(K.w!==w||K.h!==h){
      if(K.fb){gl.deleteFramebuffer(K.fb);gl.deleteTexture(K.tex);gl.deleteRenderbuffer(K.rb);}
      K.tex=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,K.tex);
      gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,w,h,0,gl.RGBA,gl.UNSIGNED_BYTE,null);
      gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.NEAREST);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.NEAREST);
      gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);
      K.rb=gl.createRenderbuffer();gl.bindRenderbuffer(gl.RENDERBUFFER,K.rb);gl.renderbufferStorage(gl.RENDERBUFFER,gl.DEPTH_COMPONENT16,w,h);
      K.fb=gl.createFramebuffer();gl.bindFramebuffer(gl.FRAMEBUFFER,K.fb);
      gl.framebufferTexture2D(gl.FRAMEBUFFER,gl.COLOR_ATTACHMENT0,gl.TEXTURE_2D,K.tex,0);
      gl.framebufferRenderbuffer(gl.FRAMEBUFFER,gl.DEPTH_ATTACHMENT,gl.RENDERBUFFER,K.rb);
      K.w=w;K.h=h;
    }
    gl.bindFramebuffer(gl.FRAMEBUFFER,K.fb);
    if(gl.checkFramebufferStatus(gl.FRAMEBUFFER)!==gl.FRAMEBUFFER_COMPLETE){gl.bindFramebuffer(gl.FRAMEBUFFER,null);return {ok:false};}
    gl.viewport(0,0,w,h);
    gl.enable(gl.SCISSOR_TEST);gl.scissor(px,py,1,1);   /* only the pixel asked about */
    gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);
    gl.enable(gl.DEPTH_TEST);gl.depthFunc(gl.LEQUAL);gl.depthMask(true);gl.disable(gl.BLEND);
    gl.useProgram(K.prog);
    gl.uniformMatrix4fv(K.view,false,bimGlViewMatrix(V));
    gl.uniformMatrix4fv(K.proj,false,bimGlProjMatrix(W,H,A3D.flat,A3D.cam.dist));
    gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,P.tex);gl.uniform1i(K.tab,0);gl.uniform2f(K.size,BIM_GB_TEXW,P.texH||1);
    gl.enableVertexAttribArray(K.pos);gl.enableVertexAttribArray(K.obj);
    for(k=0;k<B.chunks.length;k++){
      c=B.chunks[k];if(!c.count||c.cull)continue;
      gl.bindBuffer(gl.ARRAY_BUFFER,c.gl.buf);
      gl.vertexAttribPointer(K.pos,3,gl.FLOAT,false,28,0);gl.vertexAttribPointer(K.obj,1,gl.FLOAT,false,28,24);
      gl.drawArrays(gl.TRIANGLES,0,c.count);
    }
    gl.disableVertexAttribArray(K.pos);gl.disableVertexAttribArray(K.obj);
    gl.readPixels(px,py,1,1,gl.RGBA,gl.UNSIGNED_BYTE,out);
    gl.disable(gl.SCISSOR_TEST);
    gl.bindFramebuffer(gl.FRAMEBUFFER,null);
    gl.viewport(0,0,G.cv.width,G.cv.height);
    var n=out[0]+out[1]*256+out[2]*65536,slot=n-1,id,o=null;
    A3D.lastPickGpu={px:px,py:py,slot:slot};
    if(n<=0)return {ok:true,o:null};
    for(id in B.slots)if(B.slots.hasOwnProperty(id)&&B.slots[id]===slot){o=objById(id);break;}
    return {ok:!!o,o:o};
  }
  function bimPickGpuWanted(){
    if(A3D_PICK_GPU==='off'||!A3D_GL||!A3D_GL.gb)return false;
    if(A3D_PICK_GPU==='on')return true;
    return (A3D.glFaces||0)>BIM_PICK_GPU_FACES;
  }
  /* ================= __acad3dV153: the WebGPU engine =================""")
rep("""    if(A3D_GL||A3D_GPU.engine==='webgpu')bimBuildPickPolys();
    for(i=A3D.lastPolys.length-1;i>=0;i--){""", """    if(bimPickGpuWanted()){   /* __acad3dV156: a large model: the GPU says what is under the pointer */
      var gp=bimPickGpu(x,y);
      A3D.lastPickPath='gpu';
      if(gp.ok&&gp.o&&bimLayerPickable(gp.o))return gp.o;
      if(gp.ok&&!gp.o)return bimPickSketch(x,y);
    }
    A3D.lastPickPath='cpu';
    if(A3D_GL||A3D_GPU.engine==='webgpu')bimBuildPickPolys();
    for(i=A3D.lastPolys.length-1;i>=0;i--){""")
rep("""  window.__a3dCull=function(on){""", """  window.__a3dPickMode=function(m){if(m==='on'||m==='off'||m==='auto')A3D_PICK_GPU=m;return A3D_PICK_GPU;};   /* __acad3dV156 */
  window.__a3dPickInfo=function(x,y){var t=performance.now(),o=pick(x,y);return {id:o&&o.id?o.id:null,path:A3D.lastPickPath||null,ms:performance.now()-t};};
  window.__a3dCull=function(on){""")
rep("""  window.__acad3dV156='seencount,typecolour';""", """  window.__acad3dV156='seencount,typecolour,gpupick,pickidpass,picklockedcpu,picksmallcpu';""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
