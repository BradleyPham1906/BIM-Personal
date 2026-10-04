"""patch_phase154a.py -- V154: outlines pulled a hair toward the camera, in both engines.

An outline lies exactly on its face, so the two tie in depth and each pixel goes whichever way the
rasteriser's rounding sends it: outlines flicker and break up as the view turns, and WebGL and
WebGPU break the tie differently (V153's 61 pixels). Each outline vertex is now moved toward the
eye by 0.02% of its distance: a millimetre at 5 m, 2 cm at 100 m, so a tie is always won by the
outline, and an outline behind a face 2 cm thick or more at 100 m stays hidden. The same pull in
the object-by-object WebGL path, the batched one, and WebGPU."""
NAME = 'patch_phase154a.py'
BASE = '38bf38edf529788217a11a330242d6251afb588298e6a86f8f489c268aa2dc58'
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


# the object-by-object WebGL path
rep("""  var GL_EDGE_FACE_LIMIT=20000;""", """  var GL_EDGE_FACE_LIMIT=20000;
  var BIM_EDGE_PULL=0.0002;   /* __acad3dV154: an outline vertex moved toward the eye by this part of its distance */""")
rep("""      'uniform mat4 uView;uniform mat4 uProj;uniform vec3 uOffset;'+
      'varying vec3 vNorm;'+
      'void main(){vNorm=aNorm;gl_Position=uProj*uView*vec4(aPos+uOffset,1.0);}';""",
    """      'uniform mat4 uView;uniform mat4 uProj;uniform vec3 uOffset;uniform vec3 uEye;uniform float uPull;'+
      'varying vec3 vNorm;'+
      'void main(){vNorm=aNorm;vec3 w=aPos+uOffset;w+=(uEye-w)*uPull;gl_Position=uProj*uView*vec4(w,1.0);}';   /* __acad3dV154: uPull for outlines */""")
rep("""        flatCol:gl.getUniformLocation(prog,'uFlatCol'),alpha:gl.getUniformLocation(prog,'uAlpha')}};   /* __acad3dV121 */""",
    """        flatCol:gl.getUniformLocation(prog,'uFlatCol'),alpha:gl.getUniformLocation(prog,'uAlpha'),   /* __acad3dV121 */
        eye:gl.getUniformLocation(prog,'uEye'),pull:gl.getUniformLocation(prog,'uPull')}};   /* __acad3dV154 */""")
rep("""    gl.uniform1f(G.loc.flatCol,0);
    gl.uniform1f(G.loc.alpha,alpha);""", """    gl.uniform1f(G.loc.flatCol,0);
    gl.uniform1f(G.loc.pull,0);   /* __acad3dV154 */
    gl.uniform1f(G.loc.alpha,alpha);""")
rep("""    gl.uniform3f(G.loc.light,LIGHT[0],LIGHT[1],LIGHT[2]);
    var live={},totalFaces=0,i,trans=[];""", """    gl.uniform3f(G.loc.light,LIGHT[0],LIGHT[1],LIGHT[2]);
    gl.uniform3f(G.loc.eye,V.eye[0],V.eye[1],V.eye[2]);   /* __acad3dV154 */
    var live={},totalFaces=0,i,trans=[];""")
rep("""        gl.uniform1f(G.loc.flatCol,1);
        var la2=bimLayerAlpha(o2);""", """        gl.uniform1f(G.loc.flatCol,1);
        gl.uniform1f(G.loc.pull,BIM_EDGE_PULL);   /* __acad3dV154 */
        var la2=bimLayerAlpha(o2);""")
rep("""      gl.disable(gl.BLEND);
    }
    var k;
    for(k in G.bufs){""", """      gl.disable(gl.BLEND);
      gl.uniform1f(G.loc.pull,0);
    }
    var k;
    for(k in G.bufs){""")

# the batched WebGL path
rep("""      'uniform mat4 uView;uniform mat4 uProj;uniform sampler2D uTab;uniform vec2 uTabSize;uniform float uPass;uniform float uEdge;'+""",
    """      'uniform mat4 uView;uniform mat4 uProj;uniform sampler2D uTab;uniform vec2 uTabSize;uniform float uPass;uniform float uEdge;uniform vec3 uEye;'+""")
rep("""      ' gl_Position=uProj*uView*vec4(aPos+a.xyz,1.0);}';""",
    """      ' vec3 w=aPos+a.xyz;if(uEdge>0.5)w+=(uEye-w)*'+BIM_EDGE_PULL.toFixed(6)+';'+   /* __acad3dV154 */
      ' gl_Position=uProj*uView*vec4(w,1.0);}';""")
rep("""        light:gl.getUniformLocation(prog,'uLight')}};
    return G.gb;""", """        light:gl.getUniformLocation(prog,'uLight'),eye:gl.getUniformLocation(prog,'uEye')}};
    return G.gb;""")
rep("""    gl.uniform3f(L.light,LIGHT[0],LIGHT[1],LIGHT[2]);
    gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,P.tex);""", """    gl.uniform3f(L.light,LIGHT[0],LIGHT[1],LIGHT[2]);
    gl.uniform3f(L.eye,V.eye[0],V.eye[1],V.eye[2]);   /* __acad3dV154 */
    gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,P.tex);""")

# WebGPU
rep("""    'struct U{view:mat4x4f,proj:mat4x4f,light:vec4f};\\n'+""", """    'struct U{view:mat4x4f,proj:mat4x4f,light:vec4f,eye:vec4f};\\n'+""")
rep("""    ' var p=u.proj*u.view*vec4f(pos+a.xyz,1.0);p.z=(p.z+p.w)*0.5;o.p=p;return o;}\\n'+""",
    """    ' var w=pos+a.xyz;if(EDGE>0.5){w=w+(u.eye.xyz-w)*'+BIM_EDGE_PULL.toFixed(6)+';}\\n'+   /* __acad3dV154 */
    ' var p=u.proj*u.view*vec4f(w,1.0);p.z=(p.z+p.w)*0.5;o.p=p;return o;}\\n'+""")
rep("""      var ubuf=dev.createBuffer({size:144,usage:GPUBufferUsage.UNIFORM|GPUBufferUsage.COPY_DST});""",
    """      var ubuf=dev.createBuffer({size:160,usage:GPUBufferUsage.UNIFORM|GPUBufferUsage.COPY_DST});""")
rep("""    var u=new Float32Array(36);
    u.set(bimGlViewMatrix(V),0);u.set(bimGlProjMatrix(W,H,A3D.flat,A3D.cam.dist),16);u[32]=LIGHT[0];u[33]=LIGHT[1];u[34]=LIGHT[2];
    dev.queue.writeBuffer(P.ubuf,0,u.buffer,0,144);""", """    var u=new Float32Array(40);
    u.set(bimGlViewMatrix(V),0);u.set(bimGlProjMatrix(W,H,A3D.flat,A3D.cam.dist),16);u[32]=LIGHT[0];u[33]=LIGHT[1];u[34]=LIGHT[2];
    u[36]=V.eye[0];u[37]=V.eye[1];u[38]=V.eye[2];   /* __acad3dV154 */
    dev.queue.writeBuffer(P.ubuf,0,u.buffer,0,160);""")

# the comparison: a difference beyond one multisample's worth of the brightest outline (64 of 255),
# not explained by the same colour a pixel over, is a real one
rep("""        if(m>48){
          n48++;
          /* a thin line rasterised a pixel over: the same colour beside it is not a difference */
          mm=m;
          for(dy=-1;dy<=1&&mm>48;dy++)for(dx=-1;dx<=1&&mm>48;dx++){
            if(x+dx<0||x+dx>=w||y+dy<0||y+dy>=h)continue;
            mm=Math.min(mm,diff(i,((h-1-(y+dy))*w+x+dx)*4));
          }
          if(mm>48)near++;
        }""", """        if(m>48){
          n48++;
          /* a thin line rasterised a pixel over: the same colour beside it is not a difference; nor is
             one of the four samples of an outline's edge covered the other way (__acad3dV154: up to 64) */
          mm=m;
          for(dy=-1;dy<=1&&mm>64;dy++)for(dx=-1;dx<=1&&mm>64;dx++){
            if(x+dx<0||x+dx>=w||y+dy<0||y+dy>=h)continue;
            mm=Math.min(mm,diff(i,((h-1-(y+dy))*w+x+dx)*4));
          }
          if(mm>64)near++;
        }""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
