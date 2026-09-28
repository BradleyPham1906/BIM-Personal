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
  var BIM_LT_PX=24;   /* screen px to one acad.lin unit: Dashed is 12 on, 6 off */
  function bimLinetypeDash(name,unit){
    var lt=bimLinetypeDef(name),out=[],i;
    if(!lt||!lt.pat.length)return out;
    for(i=0;i<lt.pat.length;i++)out.push(lt.pat[i]===0?Math.max(1,unit*0.05):Math.abs(lt.pat[i])*unit);
    return out;
  }
  /* 6.4 px to the millimetre: AutoCAD's 0.25 mm is the 1.6 px every line was drawn at before V121 */
  function bimLineweightPx(mm,base){
    return (mm===null||mm===undefined||!isFinite(mm))?base:Math.max(0.6,mm*6.4);
  }
  function bimLayerAlpha(o){
    var ly=bimLayerOf(o),t=ly?+ly.transparency:0;
    return (isFinite(t)&&t>0)?1-Math.min(90,t)/100:1;
  }
  function bimLayerLook(o){
    var ly=bimLayerOf(o);
    return {color:(ly&&/^#[0-9a-fA-F]{6}$/.test(ly.color||''))?ly.color:'#5ec4b8',
            linetype:(ly&&bimLinetypeDef(ly.linetype))?bimLinetypeDef(ly.linetype).name:'Continuous',
            dash:bimLinetypeDash(ly&&ly.linetype,BIM_LT_PX),
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
