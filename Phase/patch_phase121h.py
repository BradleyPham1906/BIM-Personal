"""patch_phase121h.py -- V121: what is plotted and exported, by the layers.

Every output drew every layer. The plan SVG never asked about layers at all, so a layer turned off
or frozen was exported anyway; nothing knew a layer could be left out of a plot; and the DXF wrote
every layer white, Continuous, on, thawed and unlocked, whatever it was.

A plot is now a plot, as AutoCAD's is (Layer Properties Manager, AutoCAD 2024 help):
  - the plan SVG, the sheet SVG and its print, the sheet PNG and the plan PDF and PNG are drawn in a
    plot pass: a layer that is off, frozen, or set not to plot is left out; a locked layer is not
    faded; and a layer's transparency is drawn only in a presentation, since AutoCAD's Plot
    transparency option is off until it is asked for;
  - the linework LINE, PLINE, ARC, CIRCLE and POINT make is plotted By Layer: its layer's linetype
    as a dash array in paper millimetres, its lineweight in millimetres (Default being the drawing's
    own), and in a presentation its layer's color. A technical plot stays monochrome;
  - a sheet is painted at the paper's own millimetres, so a linetype and a lineweight on a sheet are
    the size they are printed at.

The DXF carries its layers as they are: the nearest of AutoCAD's nine standard colors in group 62
with the exact color in 420, negative when the layer is off; frozen and locked in 70; the linetype in
6, defined in an LTYPE table with acadiso.lin's millimetres; the lineweight in 370 and a no-plot
layer in 290. A sub-layer is written with the state it has under its parents, since a DXF layer has
no parent. Every object is written, on whatever layer, as AutoCAD's DXFOUT writes them. And the
importer reads all of it back, so a DXF written here comes back with its layers as they left."""
NAME = 'patch_phase121h.py'
BASE = 'd8fe6596c75cacfddd14d11949b66ef5ded5317c998c462dec0f44946faf2297'
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
# ---- 1. a plot pass, and what a plot draws By Layer
rep("  function bimBuildSVG(mode){\n", r"""  /* ================= __acad3dV121: a plot, by the layers =================
     A plot leaves out a layer that is off, frozen or set not to plot, does not fade a locked layer,
     and draws transparency only in a presentation (bimLayerShown and bimLayerAlpha read A3D_PLOT).
     The By Layer linework -- LINE, PLINE, ARC, CIRCLE, POINT -- is plotted with its layer's
     linetype, lineweight and, in a presentation, color; a technical plot stays monochrome. */
  function bimWithPlotPass(pres,fn){
    var was={on:A3D_PLOT.on,pres:A3D_PLOT.pres};
    A3D_PLOT.on=true;A3D_PLOT.pres=!!pres;
    try{return fn();}
    finally{A3D_PLOT.on=was.on;A3D_PLOT.pres=was.pres;}
  }
  /* In a presentation -- the only plot with graphics to resolve, rg being null in a technical one --
     the layer's color, lineweight and transparency take the place of the drawing's defaults, field
     by field, so an instance override the user set still wins. */
  function bimLookPlotGraphics(o,rg){
    if(!rg)return rg;
    var ly=bimLayerOf(o),ov=(o.graphicsOverride&&o.graphicsOverride.presentation)||{},g={},k;
    for(k in rg)if(rg.hasOwnProperty(k))g[k]=rg[k];
    if(ly&&!ov.hasOwnProperty('lineColor')&&/^#[0-9a-fA-F]{6}$/.test(ly.color||''))g.lineColor=ly.color;
    if(ly&&!ov.hasOwnProperty('lineWeight')&&ly.lineweight!==null&&ly.lineweight!==undefined&&isFinite(ly.lineweight))
      g.lineWeight=Math.max(0.05,+ly.lineweight);
    if(!ov.hasOwnProperty('opacity'))g.opacity=(isFinite(g.opacity)?g.opacity:1)*bimLayerAlpha(o);
    return g;
  }
  /* What a plot adds for the By Layer linework, `unit` being the drawing's units to a paper
     millimetre: the linetype's dash array always, and in a technical plot the lineweight (in a
     presentation the lineweight is already in the graphics above). */
  function bimLookPlotAttrs(o,unit,pres){
    var ly=bimLayerOf(o),lt=ly?bimLinetypeDef(ly.linetype):null,d=[],i,s='';
    if(lt&&lt.pat.length){
      for(i=0;i<lt.pat.length;i++)d.push(+(((lt.pat[i]===0)?0.4:Math.abs(lt.pat[i]))*unit).toFixed(6));
      s+=' stroke-dasharray="'+d.join(' ')+'"';
    }
    if(!pres&&ly&&ly.lineweight!==null&&ly.lineweight!==undefined&&isFinite(ly.lineweight))
      s+=' stroke-width="'+(Math.max(0.05,+ly.lineweight)*unit).toFixed(6)+'"';
    return s;
  }
  function bimBuildSVG(mode){
    return bimWithPlotPass(mode==='presentation',function(){return bimBuildSVGDrawing(mode);});
  }
  function bimBuildSVGDrawing(mode){
""")
rep("  function bimBuildSheetSVG(sheet,mode){\n", r"""  function bimBuildSheetSVG(sheet,mode){   /* __acad3dV121: a sheet's SVG and its print are plots */
    return bimWithPlotPass(mode==='presentation',function(){return bimBuildSheetSVGDrawing(sheet,mode);});
  }
  function bimBuildSheetSVGDrawing(sheet,mode){
""")
rep("  function bimRenderSheet(sheet,pxPerMM,paperOnly){\n", r"""  function bimRenderSheet(sheet,pxPerMM,paperOnly){
    /* __acad3dV121: paper alone is an export or a print, and so a plot; on screen a sheet shows
       what AutoCAD's layout shows -- a no-plot layer drawn, a locked one faded */
    if(paperOnly)return bimWithPlotPass(A3D.presentMode,function(){return bimRenderSheetPaper(sheet,pxPerMM,true);});
    return bimRenderSheetPaper(sheet,pxPerMM,false);
  }
  function bimRenderSheetPaper(sheet,pxPerMM,paperOnly){
""")
rep("      A3D.sheetCapture=true;\n      paint();\n",
    "      A3D.sheetCapture=true;\n      A3D_PLOT.pxmm=pxPerMM;   /* __acad3dV121: linetypes and lineweights at the paper's millimetres */\n      paint();\n")
rep("      A3D.sheetCapture=false;\n      el.cv=savedCv;el.ctx=savedCtx;\n",
    "      A3D.sheetCapture=false;\n      A3D_PLOT.pxmm=0;\n      el.cv=savedCv;el.ctx=savedCtx;\n")

# ---- 2. the plan PDF and PNG are plots of the drawing on screen
rep("      var cv=bimGetCanvasRGB();\n",
    "      var cv;\n"
    "      try{cv=bimWithPlotPass(A3D.presentMode,function(){paint();return bimGetCanvasRGB();});}   /* __acad3dV121: a plot */\n"
    "      finally{paint();}\n")
rep("      var dataURL=el.cv.toDataURL('image/png');\n      var a=document.createElement('a');\n      a.href=dataURL;a.download=bimFileStem()+'-plan.png';\n",
    "      var dataURL;\n"
    "      try{dataURL=bimWithPlotPass(A3D.presentMode,function(){paint();return el.cv.toDataURL('image/png');});}   /* __acad3dV121: a plot */\n"
    "      finally{paint();}\n"
    "      var a=document.createElement('a');\n      a.href=dataURL;a.download=bimFileStem()+'-plan.png';\n")

# ---- 3. the plan SVG: what is not plotted is left out, and the linework is By Layer
rep("      var o=A3D.objs[i],lay=layerOf(o),b=o.bim;\n      EX=bimExportOffset(o);   /* __acad3dV104 */\n      var rg=pres?bimResolveGraphics(o,'presentation'):null;\n",
    "      var o=A3D.objs[i],lay=layerOf(o),b=o.bim;\n"
    "      if(!bimLayerShown(o))continue;   /* __acad3dV121: it never asked; a plot leaves out what is off, frozen or not plotted */\n"
    "      EX=bimExportOffset(o);   /* __acad3dV104 */\n      var rg=pres?bimResolveGraphics(o,'presentation'):null;\n")
rep("    function poly(pts,closed,lay,objId,rg,forFill){\n", "    function poly(pts,closed,lay,objId,rg,forFill,lk){   /* __acad3dV121: lk, the object drawn By Layer */\n")
rep("    function line(a,b,lay,objId,rg){\n", "    function line(a,b,lay,objId,rg,lk){\n")
rep("      cmds.push({k:'poly',pts:pts,closed:closed,lay:lay,objId:objId,rg:rg,forFill:!!forFill});\n",
    "      cmds.push({k:'poly',pts:pts,closed:closed,lay:lay,objId:objId,rg:rg,forFill:!!forFill,lk:lk||null});\n")
rep("      cmds.push({k:'line',a:a,b:b,lay:lay,objId:objId,rg:rg});\n",
    "      cmds.push({k:'line',a:a,b:b,lay:lay,objId:objId,rg:rg,lk:lk||null});\n")
rep("        poly(bimFlattenSketch(o),o.closed!==false,lay,o.id,rg,false);   /* __acad3dV88 */\n",
    "        poly(bimFlattenSketch(o),o.closed!==false,lay,o.id,bimLookPlotGraphics(o,rg),false,o);   /* __acad3dV88; V121 By Layer */\n")
rep("        for(svPK=0;svPK<svPM.length;svPK++)line(svPM[svPK][0],svPM[svPK][1],lay,o.id,rg);\n",
    "        for(svPK=0;svPK<svPM.length;svPK++)line(svPM[svPK][0],svPM[svPK][1],lay,o.id,bimLookPlotGraphics(o,rg),o);   /* __acad3dV121 */\n")
rep("""        out='<path'+(cmd.objId?' data-obj="'+bimEscXml(cmd.objId)+'"':'')+stp.extra+' d="'+d.trim()+'" fill="'+stp.fill+'"/>';\n""",
    """        out='<path'+(cmd.objId?' data-obj="'+bimEscXml(cmd.objId)+'"':'')+stp.extra+(cmd.lk?bimLookPlotAttrs(cmd.lk,svgLwUnit,pres):'')+' d="'+d.trim()+'" fill="'+stp.fill+'"/>';\n""")
rep("""        out='<line'+(cmd.objId?' data-obj="'+bimEscXml(cmd.objId)+'"':'')+stl.extra+' x1="'""",
    """        out='<line'+(cmd.objId?' data-obj="'+bimEscXml(cmd.objId)+'"':'')+stl.extra+(cmd.lk?bimLookPlotAttrs(cmd.lk,svgLwUnit,pres):'')+' x1="'""")

# ---- 4. the sheet SVG, in paper millimetres already: the linework By Layer
rep("    function poly(pts,closed,objId,wy,rg,forFill){\n", "    function poly(pts,closed,objId,wy,rg,forFill,lk){   /* __acad3dV121: lk, the object drawn By Layer */\n")
rep("""      emit('<path'+(objId?' data-obj="'+bimEscXml(objId)+'"':'')+st.extra+' d="'+d.trim()+'" fill="'+st.fill+'"/>');\n""",
    """      emit('<path'+(objId?' data-obj="'+bimEscXml(objId)+'"':'')+st.extra+(lk?bimLookPlotAttrs(lk,1,pres):'')+' d="'+d.trim()+'" fill="'+st.fill+'"/>');\n""")
rep("    function ln(a,b,objId,wy,rg){\n", "    function ln(a,b,objId,wy,rg,lk){\n")
rep("""      emit('<line'+(objId?' data-obj="'+bimEscXml(objId)+'"':'')+st.extra+' x1="'""",
    """      emit('<line'+(objId?' data-obj="'+bimEscXml(objId)+'"':'')+st.extra+(lk?bimLookPlotAttrs(lk,1,pres):'')+' x1="'""")
rep("        poly(bimFlattenSketch(o),o.closed!==false,o.id,o.y,rg,false);   /* __acad3dV88 */\n",
    "        poly(bimFlattenSketch(o),o.closed!==false,o.id,o.y,bimLookPlotGraphics(o,rg),false,o);   /* __acad3dV88; V121 By Layer */\n")
rep("        for(shPK=0;shPK<shPM.length;shPK++)ln(shPM[shPK][0],shPM[shPK][1],o.id,o.y,rg);\n",
    "        for(shPK=0;shPK<shPM.length;shPK++)ln(shPM[shPK][0],shPM[shPK][1],o.id,o.y,bimLookPlotGraphics(o,rg),o);   /* __acad3dV121 */\n")

# ---- 5. the DXF: its layers as they are, and the linetypes they use
rep("  function bimDxfBulgesToModel(b){return b?b.map(function(v){return -(v||0);}):b;}\n",
    r"""  function bimDxfBulgesToModel(b){return b?b.map(function(v){return -(v||0);}):b;}
  /* __acad3dV121: a layer as a DXF LAYER record. 62 is the nearest of AutoCAD's nine standard colors,
     negative when the layer is off, and 420 the exact color; 70 carries frozen (1) and locked (4);
     6 the linetype; 290 a layer that does not plot; 370 the lineweight in hundredths of a millimetre,
     -3 for Default. A DXF layer has no parent, so a sub-layer is written as its parents leave it. */
  var BIM_DXF_ACI9=[[1,255,0,0],[2,255,255,0],[3,0,255,0],[4,0,255,255],[5,0,0,255],[6,255,0,255],[7,255,255,255],[8,128,128,128],[9,192,192,192]];
  function bimDxfNearestAci(hex){
    var m=/^#([0-9a-fA-F]{2})([0-9a-fA-F]{2})([0-9a-fA-F]{2})$/.exec(hex||''),best=7,bd=Infinity,i,r,g,b,d;
    if(!m)return 7;
    r=parseInt(m[1],16);g=parseInt(m[2],16);b=parseInt(m[3],16);
    for(i=0;i<BIM_DXF_ACI9.length;i++){
      d=Math.pow(r-BIM_DXF_ACI9[i][1],2)+Math.pow(g-BIM_DXF_ACI9[i][2],2)+Math.pow(b-BIM_DXF_ACI9[i][3],2);
      if(d<bd){bd=d;best=BIM_DXF_ACI9[i][0];}
    }
    return best;
  }
  function bimDxfLayerRecord(l){
    var P=bimDxfPair,s=bimLayerEff(l),lt=bimLinetypeDef(l.linetype),aci=bimDxfNearestAci(l.color),out;
    out=P(0,'LAYER')+P(2,bimDxfLayerName(l.name))+P(70,(s.frozen?1:0)|(s.locked?4:0))+P(62,s.on?aci:-aci);
    if(/^#[0-9a-fA-F]{6}$/.test(l.color||''))out+=P(420,parseInt(l.color.slice(1),16));
    out+=P(6,(lt&&lt.pat.length)?lt.name:'CONTINUOUS');
    if(!s.plot)out+=P(290,0);
    out+=P(370,(l.lineweight===null||l.lineweight===undefined||!isFinite(l.lineweight))?-3:Math.round(+l.lineweight*100));
    return out;
  }
  /* The LTYPE table: CONTINUOUS, and every linetype a layer uses, with acadiso.lin's millimetres. In
     this metre drawing a reader sets LTSCALE to suit its plot scale, as with any metric drawing. */
  function bimDxfLtypeTable(layers){
    var P=bimDxfPair,used={},list=[],i,k,lt,tot,out;
    for(i=0;i<layers.length;i++){
      lt=bimLinetypeDef(layers[i].linetype);
      if(lt&&lt.pat.length&&!used[lt.name]){used[lt.name]=1;list.push(lt);}
    }
    out=P(0,'TABLE')+P(2,'LTYPE')+P(70,list.length+1)+
      P(0,'LTYPE')+P(2,'CONTINUOUS')+P(70,0)+P(3,'Solid line')+P(72,65)+P(73,0)+P(40,'0.0');
    for(i=0;i<list.length;i++){
      lt=list[i];tot=0;
      for(k=0;k<lt.pat.length;k++)tot+=Math.abs(lt.pat[k]);
      out+=P(0,'LTYPE')+P(2,lt.name)+P(70,0)+P(3,lt.desc)+P(72,65)+P(73,lt.pat.length)+P(40,tot.toFixed(4));
      for(k=0;k<lt.pat.length;k++)out+=P(49,lt.pat[k].toFixed(4))+P(74,0);
    }
    return out+P(0,'ENDTAB');
  }
""")
rep("""    out+=P(0,'SECTION')+P(2,'TABLES')+P(0,'TABLE')+P(2,'LAYER')+P(70,layers.length+1);
    out+=P(0,'LAYER')+P(2,'0')+P(70,0)+P(62,7)+P(6,'CONTINUOUS');
    for(i=0;i<layers.length;i++)out+=P(0,'LAYER')+P(2,bimDxfLayerName(layers[i].name))+P(70,0)+P(62,7)+P(6,'CONTINUOUS');
""", """    out+=P(0,'SECTION')+P(2,'TABLES')+bimDxfLtypeTable(layers)+P(0,'TABLE')+P(2,'LAYER')+P(70,layers.length+1);   /* __acad3dV121 */
    out+=P(0,'LAYER')+P(2,'0')+P(70,0)+P(62,7)+P(6,'CONTINUOUS');
    for(i=0;i<layers.length;i++)out+=bimDxfLayerRecord(layers[i]);   /* __acad3dV121: every layer was white, on and Continuous */
""")

# ---- 6. and the importer reads it back
rep("""        var nm=dxfStr(r.items,2,'0');
        var col=dxfNum(r.items,62,7);
        layers[nm]={name:nm,color:dxfAciToHex(col)};
""", """        var nm=dxfStr(r.items,2,'0');
        var col=dxfNum(r.items,62,7),tc=dxfNum(r.items,420,null),lf=dxfNum(r.items,70,0);
        var lwv=dxfNum(r.items,370,-3),plv=dxfNum(r.items,290,1);
        /* __acad3dV121: the layer comes back as it was written -- 420's exact color over 62's standard
           one, 62 negative for a layer that is off, 70 frozen (1) and locked (4), 6, 370 and 290 */
        layers[nm]={name:nm,color:(tc!==null&&isFinite(tc)&&tc>=0)?'#'+('000000'+Math.round(tc).toString(16)).slice(-6):dxfAciToHex(Math.abs(col)),
          off:col<0,frozen:!!(lf&1),locked:!!(lf&4),linetype:dxfStr(r.items,6,'CONTINUOUS'),
          lineweight:(isFinite(lwv)&&lwv>=0)?lwv/100:null,plot:plv!==0};
""")
rep("""      for(i=0;i<dxfNames.length;i++){
        var dl=res.layers[dxfNames[i]];
        var lyr=addLayer(dxfNames[i],dl?dl.color:'#9db4c8');
        layerMap[dxfNames[i]]=lyr.id;
      }
""", """      var dxfWasCur=A3D.activeLayer,dxfMade={};   /* __acad3dV121 */
      for(i=0;i<dxfNames.length;i++){
        var dl=res.layers[dxfNames[i]];
        if(!bimLayerByName(dxfNames[i]))dxfMade[dxfNames[i]]=1;
        var lyr=addLayer(dxfNames[i],dl?dl.color:'#9db4c8');
        layerMap[dxfNames[i]]=lyr.id;
      }
      /* __acad3dV121: a layer the import made takes the state it was written with; a layer the project
         already had keeps its own, as AutoCAD's does when a drawing brings in a layer it has. The
         current layer goes back to the one it was, since addLayer made each current in turn and a
         frozen layer cannot be current. */
      if(bimLayerById(dxfWasCur))A3D.activeLayer=dxfWasCur;
      for(i=0;i<dxfNames.length;i++)if(dxfMade[dxfNames[i]])bimDxfApplyLayer(layerMap[dxfNames[i]],res.layers[dxfNames[i]]);
""")
rep("  function bimImportDXF(text,filename){\n", r"""  function bimDxfApplyLayer(id,dl){
    var ly=bimLayerById(id),lt;
    if(!ly||!dl)return;
    lt=bimLinetypeDef(dl.linetype);
    if(lt)ly.linetype=lt.name;
    if(dl.lineweight!==null&&dl.lineweight!==undefined&&BIM_LINEWEIGHTS.indexOf(dl.lineweight)>=0)ly.lineweight=dl.lineweight;
    if(dl.plot===false)ly.plot=false;
    if(dl.locked)ly.locked=true;
    if(dl.off)ly.visible=false;
    if(dl.frozen&&ly.id!==A3D.activeLayer)ly.frozen=true;
  }
  function bimImportDXF(text,filename){
""")

# ---- the checks: every plot builder runs in a plot pass
code = re.sub(r'/\*.*?\*/', '', t, flags=re.S)
for fn in ('bimBuildSVG', 'bimBuildSheetSVG'):
    m = re.search(r'\n  function ' + fn + r'\((?:mode|sheet,mode)\)\{\s*return bimWithPlotPass\(', code)
    if not m:
        sys.exit('ABORT: %s is not a plot pass' % fn)
if code.count("P(62,7)+P(6,'CONTINUOUS')") != 1:
    sys.exit('ABORT: a layer is still written white and Continuous')
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
