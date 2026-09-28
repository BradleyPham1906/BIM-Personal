"""patch_phase121c.py -- V121: what is on a layer looks like its layer.

The owner asked for color, linetype and transparency in the layer table. They are real only if they
change the drawing, so the rule is set here, from AutoCAD's By Layer and Revit's materials:

  - the linework drawn with LINE, PLINE, ARC, CIRCLE, RECTANG, POLYGON and POINT takes its layer's
    color, linetype and lineweight;
  - everything on a layer takes its transparency: linework, annotation, hatches, rooms, construction
    lines, property lines, terrain, notes and solids, in the GL renderer and the CPU one;
  - a locked layer is drawn faded by 50 percent on screen, as AutoCAD's LAYLOCKFADECTL starts, and
    plotted normally;
  - building elements keep their materials, and annotation and construction lines their own styles.

Found on the way: drawSketches never asked about layers at all. Turning a layer off hid its walls,
rooms, dimensions and notes, and left every line, polyline, arc and circle on it drawn -- on screen
and on every sheet, since sheets are painted by the same function.

The linetype patterns are derived from the acadiso.lin definitions V121b keeps, in paper
millimetres (24/25.4 px to the millimetre on screen: DASHED is 12 on, 6 off). A lineweight is drawn at 6.4 px to the millimetre, so AutoCAD's
0.25 mm is the 1.6 px every line was drawn at before, and Default stays exactly that. Transparent
solids are drawn after the opaque ones, blended, without writing depth, so what is behind shows."""
NAME = 'patch_phase121c.py'
BASE = 'e9056fe70c544932f1bd80ec8952904ad4475cf8d9fb06f42dd2355cbfaec605'
import re
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def esc(s):
    """Non-ASCII in inserted text becomes a \\uXXXX escape, by code rather than by care (V103)."""
    return ''.join(ch if ord(ch) < 128 else '\\u%04x' % ord(ch) for ch in s)


def rep(old, new, n=1):
    global t
    new = esc(new)
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: %d occurrences, expected %d: %r' % (c, n, old[:90]))
    t = t.replace(old, new)


def after_line(head, new):
    """Insert new text after the whole line that starts with head (head must be unique)."""
    global t
    c = t.count(head)
    if c != 1:
        sys.exit('ABORT: %d occurrences, expected 1: %r' % (c, head[:90]))
    e = t.index('\n', t.index(head)) + 1
    t = t[:e] + esc(new) + t[e:]


def span(head, tail, new, lines):
    """Replace from the start of head up to (not including) the first tail after it. The span may
    hold non-ASCII that cannot be retyped, so it is found by its ends; head must be unique, and the
    number of lines removed must be exactly what was measured, so a tail that matched somewhere
    unexpected cannot quietly take the wrong amount."""
    global t
    c = t.count(head)
    if c != 1:
        sys.exit('ABORT: span head %d occurrences, expected 1: %r' % (c, head[:90]))
    s = t.index(head)
    e = t.find(tail, s + len(head))
    if e < 0:
        sys.exit('ABORT: span tail not found after head: %r' % tail[:90])
    got = t[s:e].count('\n')
    if got != lines:
        sys.exit('ABORT: span covers %d lines, expected %d: %r' % (got, lines, head[:60]))
    t = t[:s] + esc(new) + t[e:]
# ---- 1. the look of a layer, derived from its fields
rep("""  function bimLayerPickable(o){
    var s=bimObjLayerState(o);
    return s.on&&!s.frozen&&!s.locked;
  }
""", r"""  function bimLayerPickable(o){
    var s=bimObjLayerState(o);
    return s.on&&!s.frozen&&!s.locked;
  }
  /* ================= __acad3dV121: what a layer looks like, By Layer =================
     The linework drawn with LINE, PLINE, ARC, CIRCLE, RECTANG, POLYGON and POINT takes its layer's
     color, linetype and lineweight, as AutoCAD's objects do By Layer. Everything on a layer takes its
     transparency. Building elements keep their materials (Revit's rule); annotation and construction
     lines keep their own styles. */
  /* A linetype's millimetres are paper millimetres. On screen a millimetre is 24/25.4 px, so DASHED
     is 12 on and 6 off at every zoom; a plot draws the millimetres themselves. A dot is 0.4 mm. */
  var BIM_LT_SCREEN_PXMM=24/25.4;
  function bimLinetypeDash(name,pxPerMm){
    var lt=bimLinetypeDef(name),out=[],i;
    if(!lt||!lt.pat.length)return out;
    for(i=0;i<lt.pat.length;i++)out.push(lt.pat[i]===0?Math.max(1,0.4*pxPerMm):Math.abs(lt.pat[i])*pxPerMm);
    return out;
  }
  /* On screen, 6.4 px to the millimetre: AutoCAD's 0.25 mm is the 1.6 px every line was drawn at
     before V121, and Default stays exactly that. On a sheet, the paper's own millimetres, Default
     being AutoCAD's LWDEFAULT of 0.25 mm, and never under a pixel. */
  var BIM_LW_DEFAULT=0.25;
  function bimLineweightPx(mm,base){
    var pm=(A3D.sheetCapture&&A3D_PLOT.pxmm>0)?A3D_PLOT.pxmm:0,d=(mm===null||mm===undefined||!isFinite(mm));
    if(pm)return Math.max(1,(d?BIM_LW_DEFAULT:+mm)*pm);
    return d?base:Math.max(0.6,mm*6.4);
  }
  /* AutoCAD fades a locked layer on screen by LAYLOCKFADECTL, 50 percent at first, and plots it
     normally. The transparency is the layer's own; the lock may come from a layer above it. A plot
     draws transparency only when it is a presentation -- AutoCAD's Plot transparency option is off
     until it is asked for. */
  var BIM_LOCK_FADE=50;
  function bimLayerAlpha(o){
    var ly=bimLayerOf(o),t=ly?+ly.transparency:0,a=(isFinite(t)&&t>0)?1-Math.min(90,t)/100:1;
    if(A3D_PLOT.on)return A3D_PLOT.pres?a:1;
    if(bimObjLayerState(o).locked)a*=1-BIM_LOCK_FADE/100;
    return a;
  }
  function bimLayerLook(o){
    var ly=bimLayerOf(o);
    return {color:(ly&&/^#[0-9a-fA-F]{6}$/.test(ly.color||''))?ly.color:'#5ec4b8',
            linetype:(ly&&bimLinetypeDef(ly.linetype))?bimLinetypeDef(ly.linetype).name:'Continuous',
            dash:bimLinetypeDash(ly&&ly.linetype,(A3D.sheetCapture&&A3D_PLOT.pxmm>0)?A3D_PLOT.pxmm:BIM_LT_SCREEN_PXMM),
            width:bimLineweightPx(ly?ly.lineweight:null,1.6),
            alpha:bimLayerAlpha(o)};
  }
  function bimHexA(hex,a){
    var m=/^#([0-9a-fA-F]{2})([0-9a-fA-F]{2})([0-9a-fA-F]{2})$/.exec(hex||'');
    if(!m)return 'rgba(94,196,184,'+a+')';
    return 'rgba('+parseInt(m[1],16)+','+parseInt(m[2],16)+','+parseInt(m[3],16)+','+a+')';
  }
""")

# ---- 2. sketch linework: By Layer, and not drawn on a layer that is off
rep("  function drawSketchPath(ctx,V,W,H,pts,y0,col,closed,prog,off,bulges){\n",
    "  function drawSketchPath(ctx,V,W,H,pts,y0,col,closed,prog,off,bulges,look){   /* __acad3dV121: look, By Layer */\n")
rep("""    ctx.save();
    ctx.beginPath();
    ctx.moveTo(sp[0][0],sp[0][1]);
    for(i=1;i<sp.length;i++)ctx.lineTo(sp[i][0],sp[i][1]);
    if(closed){
      ctx.closePath();
      ctx.fillStyle='rgba(94,196,184,0.10)';
      ctx.fill();
    }
    if(prog)ctx.setLineDash([5,4]);
    ctx.strokeStyle=col;
    ctx.lineWidth=1.6;
""", """    ctx.save();
    if(look&&look.alpha<1)ctx.globalAlpha*=look.alpha;
    ctx.beginPath();
    ctx.moveTo(sp[0][0],sp[0][1]);
    for(i=1;i<sp.length;i++)ctx.lineTo(sp[i][0],sp[i][1]);
    if(closed){
      ctx.closePath();
      ctx.fillStyle=bimHexA(look?look.color:'#5ec4b8',0.10);
      ctx.fill();
    }
    if(prog)ctx.setLineDash([5,4]);
    else if(look&&look.dash.length)ctx.setLineDash(look.dash);
    ctx.strokeStyle=col;
    ctx.lineWidth=look?look.width:1.6;
""")
rep("""      if(o.t!=='sketch')continue;
      if(bimIsPoint(o)){                        /* __acad3dV93 */
        var pmSeg=bimPointMarkerSegs(o.pts[0]),pmQ=bimObjOffset(o),pmK;
        for(pmK=0;pmK<pmSeg.length;pmK++)
          drawSketchPath(ctx,V,W,H,pmSeg[pmK],o.y,(o.id===A3D.sel)?'#4ea1ff':'#ffd479',false,false,pmQ,null);
        continue;
      }
      drawSketchPath(ctx,V,W,H,o.pts,o.y,(o.id===A3D.sel)?'#4ea1ff':'#5ec4b8',(o.closed!==false),false,bimObjOffset(o),o.bulges);
""", """      if(o.t!=='sketch')continue;
      /* __acad3dV121: this never asked about layers, so a layer turned off kept all its linework */
      if(!bimLayerShown(o))continue;
      var lk=bimLayerLook(o);
      (A3D.lastLook||(A3D.lastLook={}))[o.id]=lk;   /* what was decided, for the suite to read */
      if(bimIsPoint(o)){                        /* __acad3dV93 */
        var pmSeg=bimPointMarkerSegs(o.pts[0]),pmQ=bimObjOffset(o),pmK;
        for(pmK=0;pmK<pmSeg.length;pmK++)
          drawSketchPath(ctx,V,W,H,pmSeg[pmK],o.y,(o.id===A3D.sel)?'#4ea1ff':lk.color,false,false,pmQ,null,lk);
        continue;
      }
      drawSketchPath(ctx,V,W,H,o.pts,o.y,(o.id===A3D.sel)?'#4ea1ff':lk.color,(o.closed!==false),false,bimObjOffset(o),o.bulges,lk);
""")

# ---- 3. everything on a layer takes its transparency
LA = "ctx.globalAlpha*=bimLayerAlpha(o);   /* __acad3dV121: the layer's transparency */\n"
rep("      rg=bimHatchGraphics(o);\n", "      " + LA + "      rg=bimHatchGraphics(o);\n")
rep("      ctx.save();\n      ctx.setLineDash([9,5]);\n", "      ctx.save();\n      " + LA + "      ctx.setLineDash([9,5]);\n")
rep("      ctx.globalAlpha=(rrg?rrg.opacity:1)*(schemeCol?BIM_SCHEME_ALPHA:1);\n",
    "      var rla=bimLayerAlpha(o);   /* __acad3dV121: the layer's transparency */\n"
    "      ctx.globalAlpha=rla*(rrg?rrg.opacity:1)*(schemeCol?BIM_SCHEME_ALPHA:1);\n")
rep("      ctx.globalAlpha=rrg?rrg.opacity:1;\n", "      ctx.globalAlpha=rla*(rrg?rrg.opacity:1);\n")
rep("      ctx.setLineDash([]);\n      ctx.globalAlpha=1;\n      /* __acad3dV60: same test-observable style record as the main solid loop, keyed by room id\n",
    "      ctx.setLineDash([]);\n      ctx.globalAlpha=rla;\n      /* __acad3dV60: same test-observable style record as the main solid loop, keyed by room id\n")
rep("      if(!bimLayerShown(o))continue;   /* __acad3dV121 */\n      ctx.save();\n      try{\n",
    "      if(!bimLayerShown(o))continue;   /* __acad3dV121 */\n      ctx.save();\n      " + LA + "      try{\n")
rep("      ctx.save();\n      ctx.strokeStyle=sel?'#4ea1ff':'#d8a657';ctx.lineWidth=sel?2.2:1.8;\n",
    "      ctx.save();\n      " + LA + "      ctx.strokeStyle=sel?'#4ea1ff':'#d8a657';ctx.lineWidth=sel?2.2:1.8;\n")
rep("      ctx.save();\n      ctx.strokeStyle=sel?'#4ea1ff':'#b8c0ca';\n      ctx.lineWidth=sel?1.4:1;\n",
    "      ctx.save();\n      " + LA + "      ctx.strokeStyle=sel?'#4ea1ff':'#b8c0ca';\n      ctx.lineWidth=sel?1.4:1;\n")
rep("    ctx.save();\n    ctx.strokeStyle=sel?'#4ea1ff':'#b8c0ca';\n    ctx.fillStyle=sel?'#9ec1ff':'#dfe4ea';\n",
    "    ctx.save();\n    " + LA + "    ctx.strokeStyle=sel?'#4ea1ff':'#b8c0ca';\n    ctx.fillStyle=sel?'#9ec1ff':'#dfe4ea';\n")
rep("      ctx.save();\n      ctx.fillStyle=sel?'#4ea1ff':'#dfe4ea';\n      ctx.beginPath();ctx.arc(sp[0],sp[1],2.5,0,Math.PI*2);ctx.fill();\n",
    "      ctx.save();\n      " + LA + "      ctx.fillStyle=sel?'#4ea1ff':'#dfe4ea';\n      ctx.beginPath();ctx.arc(sp[0],sp[1],2.5,0,Math.PI*2);ctx.fill();\n")
rep("      ctx.save();\n      ctx.fillStyle='rgba(20,22,26,0.88)';\n      ctx.fillRect(L.box[0],L.box[1],L.box[2]-L.box[0],L.box[3]-L.box[1]);\n",
    "      ctx.save();\n      " + LA + "      ctx.fillStyle='rgba(20,22,26,0.88)';\n      ctx.fillRect(L.box[0],L.box[1],L.box[2]-L.box[0],L.box[3]-L.box[1]);\n")
rep("      ctx.save();\n      ctx.lineWidth=st.lineWidth||1.2;\n",
    "      ctx.save();\n      " + LA + "      ctx.lineWidth=st.lineWidth||1.2;\n")

# ---- 4. solids, when the CPU draws them
rep("        polys.push({o:ob,pts:pts,z:zs/fc.length,n:faceNormal(wpts),col:col,lock:!bimLayerPickable(ob)});\n",
    "        polys.push({o:ob,pts:pts,z:zs/fc.length,n:faceNormal(wpts),col:col,lock:!bimLayerPickable(ob),la:bimLayerAlpha(ob)});   /* __acad3dV121 */\n")
rep("      ctx.globalAlpha=rg?rg.opacity:1;\n      ctx.fill();\n",
    "      ctx.globalAlpha=pl.la*(rg?rg.opacity:1);   /* __acad3dV121: the layer's transparency */\n      ctx.fill();\n")
rep("      if(rg)ctx.globalAlpha=1;\n", "      ctx.globalAlpha=1;\n")
rep("      pl.rBaseFill=baseFill;pl.rStroke=baseStroke;pl.rLineWidth=baseLW;pl.rOpacity=rg?rg.opacity:1;pl.rShadow=!!(rg&&rg.shadow);\n",
    "      pl.rBaseFill=baseFill;pl.rStroke=baseStroke;pl.rLineWidth=baseLW;pl.rOpacity=rg?rg.opacity:1;pl.rShadow=!!(rg&&rg.shadow);\n"
    "      pl.rLayerAlpha=pl.la;   /* __acad3dV121 */\n")
rep("        return {fill:p.rBaseFill,stroke:p.rStroke,lineWidth:p.rLineWidth,opacity:p.rOpacity,shadow:p.rShadow,\n",
    "        return {fill:p.rBaseFill,stroke:p.rStroke,lineWidth:p.rLineWidth,opacity:p.rOpacity,shadow:p.rShadow,layerAlpha:p.rLayerAlpha,   /* __acad3dV121 */\n")

# ---- 5. solids, when the GPU draws them: an alpha, and a second pass for what is transparent
rep("      'uniform vec3 uColor;uniform vec3 uLight;uniform float uBoost;uniform float uFlatCol;'+\n"
    "      'void main(){'+\n"
    "      ' if(uFlatCol>0.5){gl_FragColor=vec4(uColor,1.0);return;}'+\n",
    "      'uniform vec3 uColor;uniform vec3 uLight;uniform float uBoost;uniform float uFlatCol;uniform float uAlpha;'+   /* __acad3dV121 */\n"
    "      'void main(){'+\n"
    "      ' if(uFlatCol>0.5){gl_FragColor=vec4(uColor,uAlpha);return;}'+\n")
rep("      ' gl_FragColor=vec4(clamp(uColor*k,0.0,1.0),1.0);}';\n",
    "      ' gl_FragColor=vec4(clamp(uColor*k,0.0,1.0),uAlpha);}';\n")
rep("        flatCol:gl.getUniformLocation(prog,'uFlatCol')}};\n",
    "        flatCol:gl.getUniformLocation(prog,'uFlatCol'),alpha:gl.getUniformLocation(prog,'uAlpha')}};   /* __acad3dV121 */\n")
rep("""      totalFaces+=rec.faces;
      if(!rec.count)continue;
      var col=bimHexToRgb(o.col||(TYPES[o.t]||{}).c||'#7f9db8');
      gl.uniform3f(G.loc.offset,o.pos[0],o.pos[1],o.pos[2]);
      gl.uniform3f(G.loc.color,col[0],col[1],col[2]);
      gl.uniform1f(G.loc.boost,(A3D.sel===o.id)?0.25:0);
      gl.uniform1f(G.loc.flatCol,0);
      gl.bindBuffer(gl.ARRAY_BUFFER,rec.pos);
      gl.enableVertexAttribArray(G.loc.pos);
      gl.vertexAttribPointer(G.loc.pos,3,gl.FLOAT,false,0,0);
      gl.bindBuffer(gl.ARRAY_BUFFER,rec.norm);
      gl.enableVertexAttribArray(G.loc.norm);
      gl.vertexAttribPointer(G.loc.norm,3,gl.FLOAT,false,0,0);
      gl.drawArrays(gl.TRIANGLES,0,rec.count);
    }
""", """      totalFaces+=rec.faces;
      if(!rec.count)continue;
      /* __acad3dV121: a transparent layer's solids are drawn after every opaque one, blended and
         without writing depth, so what stands behind them shows through */
      var la=bimLayerAlpha(o);
      A3D.lastGlAlpha[o.id]=la;
      if(la<1){trans.push([o,rec,la]);continue;}
      bimGlDrawFaces(G,o,rec,1);
    }
    if(trans.length){
      gl.enable(gl.BLEND);gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);gl.depthMask(false);
      for(i=0;i<trans.length;i++)bimGlDrawFaces(G,trans[i][0],trans[i][1],trans[i][2]);
      gl.depthMask(true);gl.disable(gl.BLEND);
    }
""")
rep("    var live={},totalFaces=0,i;\n    for(i=0;i<A3D.objs.length;i++){\n      var o=A3D.objs[i],m=meshOf(o);\n",
    "    var live={},totalFaces=0,i,trans=[];   /* __acad3dV121 */\n    A3D.lastGlAlpha={};\n"
    "    for(i=0;i<A3D.objs.length;i++){\n      var o=A3D.objs[i],m=meshOf(o);\n")
rep("""        gl.uniform3f(G.loc.offset,o2.pos[0],o2.pos[1],o2.pos[2]);
        gl.uniform1f(G.loc.flatCol,1);
""", """        gl.uniform3f(G.loc.offset,o2.pos[0],o2.pos[1],o2.pos[2]);
        gl.uniform1f(G.loc.flatCol,1);
        var la2=bimLayerAlpha(o2);   /* __acad3dV121: the edges fade with their faces */
        gl.uniform1f(G.loc.alpha,la2);
        if(la2<1){gl.enable(gl.BLEND);gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);}else gl.disable(gl.BLEND);
""")
rep("        gl.drawArrays(gl.LINES,0,rec2.edgeCount);\n      }\n    }\n",
    "        gl.drawArrays(gl.LINES,0,rec2.edgeCount);\n      }\n      gl.disable(gl.BLEND);\n    }\n")
rep("  function bimGlRender(V,W,H){\n", r"""  /* __acad3dV121: one solid's faces, at an alpha -- the body of the face pass, shared by the opaque
     pass and the transparent one */
  function bimGlDrawFaces(G,o,rec,alpha){
    var gl=G.gl,col=bimHexToRgb(o.col||(TYPES[o.t]||{}).c||'#7f9db8');
    gl.uniform3f(G.loc.offset,o.pos[0],o.pos[1],o.pos[2]);
    gl.uniform3f(G.loc.color,col[0],col[1],col[2]);
    gl.uniform1f(G.loc.boost,(A3D.sel===o.id)?0.25:0);
    gl.uniform1f(G.loc.flatCol,0);
    gl.uniform1f(G.loc.alpha,alpha);
    gl.bindBuffer(gl.ARRAY_BUFFER,rec.pos);
    gl.enableVertexAttribArray(G.loc.pos);
    gl.vertexAttribPointer(G.loc.pos,3,gl.FLOAT,false,0,0);
    gl.bindBuffer(gl.ARRAY_BUFFER,rec.norm);
    gl.enableVertexAttribArray(G.loc.norm);
    gl.vertexAttribPointer(G.loc.norm,3,gl.FLOAT,false,0,0);
    gl.drawArrays(gl.TRIANGLES,0,rec.count);
  }
  function bimGlRender(V,W,H){
""")

# ---- 6. what the suite reads: the decision, and the pixels
rep("  window.__a3dLastDrawStyle=function(objId){\n", r"""  /* __acad3dV121: the look a sketch was drawn with; the GL alpha each solid was drawn with; and the
     alpha of the drawing canvas at a point on the page, for everything else on a layer */
  window.__a3dLastLook=function(id){return (A3D.lastLook&&A3D.lastLook[id])?JSON.parse(JSON.stringify(A3D.lastLook[id])):null;};
  window.__a3dLastGlAlpha=function(id){return (A3D.lastGlAlpha&&A3D.lastGlAlpha.hasOwnProperty(id))?A3D.lastGlAlpha[id]:null;};
  window.__a3dPixelAlpha=function(px,py){
    try{
      var r=el.cv.getBoundingClientRect(),sx=Math.round((px-r.left)*el.cv.width/r.width),sy=Math.round((py-r.top)*el.cv.height/r.height);
      return el.cv.getContext('2d').getImageData(sx,sy,1,1).data[3];
    }catch(eP){console.warn('[BIM] The canvas could not be read',eP);return null;}
  };
  window.__a3dLastDrawStyle=function(objId){
""")

# ---- the checks: every draw function that walks the objects asks about layers
code = re.sub(r'/\*.*?\*/', '', t, flags=re.S)
m = re.search(r'\n  function drawSketches\(', code)
body = code[m.end():code.find('\n  function ', m.end())]
if 'bimLayerShown' not in body:
    sys.exit('ABORT: drawSketches still draws every layer')
if code.count('ctx.globalAlpha*=bimLayerAlpha(o);') != 9:
    sys.exit('ABORT: %d draw functions take the transparency, expected 9' % code.count('ctx.globalAlpha*=bimLayerAlpha(o);'))
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
