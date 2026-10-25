  // ---- __acad3dV6: Layers system + CAD/BIM file import (DXF, OBJ, STL, IFC subset) ----
  function bimLayerOf(o){
    var id=o.layer||A3D.activeLayer,i;
    for(i=0;i<A3D.layers.length;i++)if(A3D.layers[i].id===id)return A3D.layers[i];
    return A3D.layers[0]||null;
  }
  /* ================= __acad3dV121: what a layer's switches mean, asked in one place =================

     A layer is {id, name, color, visible, locked} since V6; V121 adds frozen, plot, linetype,
     lineweight, transparency, description and parent. Every flag is read tolerantly -- a layer
     without `frozen` is thawed, one without `plot` plots -- so an older acad3dV1 needs no migration.

     AutoCAD's meanings (Layer Properties Manager and SELECT, AutoCAD 2024 help):
       On (visible)  off: not displayed and not plotted; still in the drawing's extents, and still
                     selected by SELECT ALL, whose documented rule leaves out only frozen and
                     locked layers.
       Freeze        frozen: not displayed, not plotted, not regenerated, not in the extents, not
                     selected by anything.
       Lock          locked: displayed faded, snapped to and plotted; not selected or modified.
       Plot          no-plot: displayed, not plotted.
     A sub-layer is off, frozen, locked or no-plot when any layer above it is.

     Three questions, each asked in one place:
       bimLayerShown(o)       drawn, snapped to, traced, measured -- and, in a plot, plotted
       bimLayerPickable(o)    picked by a click, a window or a list row: shown and unlocked
       bimLayerSelectable(o)  taken by SELECT ALL and every select-by-criteria: thawed and unlocked
     Before V121, 28 sites read the flags for themselves. */
  /* A plot in progress: `on` while a plot or an export is being drawn -- a no-plot layer is left
     out and a locked layer is not faded, as AutoCAD plots them; `pres` when it is a presentation,
     the one kind that draws a layer's transparency; `pxmm`, the paper's pixels per millimetre while
     a sheet is painted, which linetypes and lineweights are drawn at. */
  var A3D_PLOT={on:false,pres:false,pxmm:0};
  function bimLayerById(id){
    var i;
    for(i=0;i<A3D.layers.length;i++)if(A3D.layers[i].id===id)return A3D.layers[i];
    return null;
  }
  /* The layer and every layer above it, nearest first. A parent that is missing ends the chain, and
     one already seen ends it too, so a loop in stored data cannot hang a paint. */
  function bimLayerChain(ly){
    var out=[],seen={},c=ly;
    while(c&&!seen[c.id]){
      seen[c.id]=1;out.push(c);
      c=(typeof c.parent==='string'&&c.parent)?bimLayerById(c.parent):null;
    }
    return out;
  }
  function bimLayerEff(ly){
    var s={on:true,frozen:false,locked:false,plot:true},ch=bimLayerChain(ly),i;
    for(i=0;i<ch.length;i++){
      if(ch[i].visible===false)s.on=false;
      if(ch[i].frozen)s.frozen=true;
      if(ch[i].locked)s.locked=true;
      if(ch[i].plot===false)s.plot=false;
    }
    return s;
  }
  function bimObjLayerState(o){
    var ly=bimLayerOf(o);
    return ly?bimLayerEff(ly):{on:true,frozen:false,locked:false,plot:true};
  }
  function bimLayerShown(o){
    var s=bimObjLayerState(o);
    return s.on&&!s.frozen&&(s.plot||!A3D_PLOT.on);
  }
  function bimLayerPickable(o){
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
    if(pm)return Math.max(1/cvScale(el.cv),(d?BIM_LW_DEFAULT:+mm)*pm);   /* __acad3dV122: a pixel of the image */
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
  /* AutoCAD's ALL: everything except frozen and locked layers -- a layer that is off included,
     which is why AutoCAD's users freeze a layer rather than turn it off when it must stay out of
     a selection. Whoever selects this way says how many of the selection cannot be seen. */
  function bimLayerSelectable(o){
    var s=bimObjLayerState(o);
    return !s.frozen&&!s.locked;
  }
