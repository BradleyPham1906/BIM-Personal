# ---- 1. the two questions, and what they are asked of
rep("""  function bimLayerOf(o){
    var id=o.layer||A3D.activeLayer,i;
    for(i=0;i<A3D.layers.length;i++)if(A3D.layers[i].id===id)return A3D.layers[i];
    return A3D.layers[0]||null;
  }
""", r"""  function bimLayerOf(o){
    var id=o.layer||A3D.activeLayer,i;
    for(i=0;i<A3D.layers.length;i++)if(A3D.layers[i].id===id)return A3D.layers[i];
    return A3D.layers[0]||null;
  }
  /* ================= __acad3dV121: what a layer's switches mean, asked in one place =================

     A layer is {id, name, color, visible, locked} since V6; V121 adds frozen, plot, linetype,
     lineweight, transparency, description and parent. Every flag is read tolerantly -- a layer
     without `frozen` is thawed, one without `plot` plots -- so an older acad3dV1 needs no migration.

     AutoCAD's meanings (Layer Properties Manager, AutoCAD 2024 help):
       On (visible)  off: not displayed and not plotted; still part of the drawing's extents.
       Freeze        frozen: not displayed, not plotted, not regenerated, not in the extents.
       Lock          locked: displayed, snapped to and plotted; not selected or modified.
     A sub-layer is off, frozen or locked when any layer above it is.

     Everything that draws, snaps, traces or measures asks bimLayerShown(o); everything that selects
     asks bimLayerPickable(o). Before V121, 28 sites read the flags for themselves. */
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
    return s.on&&!s.frozen;
  }
  function bimLayerPickable(o){
    var s=bimObjLayerState(o);
    return s.on&&!s.frozen&&!s.locked;
  }
""")

# ---- 2. the 28 sites
SHOWN = "   /* __acad3dV121 */\n"
rep("      var lyr=bimLayerOf(o);\n      if(lyr&&lyr.visible===false)continue;\n",
    "      if(!bimLayerShown(o))continue;" + SHOWN, 12)
rep("      lyr=bimLayerOf(o);\n      if(lyr&&lyr.visible===false)continue;\n",
    "      if(!bimLayerShown(o))continue;" + SHOWN, 2)
rep("    var drawn=[],i,j,k,s,o,lyr,tin,step,cs,sel,sp,a,b,c,best,bl,L,txt,ang,nseg;\n",
    "    var drawn=[],i,j,k,s,o,tin,step,cs,sel,sp,a,b,c,best,bl,L,txt,ang,nseg;\n")
rep("    var out=[],i,k,o,q,v,w,top,lyr;\n", "    var out=[],i,k,o,q,v,w,top;\n")
rep("      var lyr=bimLayerOf(o);\n      if(lyr&&(lyr.visible===false||lyr.locked))continue;\n",
    "      if(!bimLayerPickable(o))continue;" + SHOWN, 7)
rep("    var lyr=bimLayerOf(o);\n    if(lyr&&lyr.visible===false)return null;\n",
    "    if(!bimLayerShown(o))return null;" + SHOWN)
rep("      var lyr=bimLayerOf(o);\n      if(lyr&&(lyr.visible===false||lyr.locked))return false;\n",
    "      if(!bimLayerPickable(o))return false;" + SHOWN)
rep("      var lyr=bimLayerOf(ob);\n      if(lyr&&lyr.visible===false)continue;\n",
    "      if(!bimLayerShown(ob))continue;" + SHOWN, 2)
rep("lock:!!(lyr&&lyr.locked)", "lock:!bimLayerPickable(ob)", 2)
rep("var lyr=bimLayerOf(o);if(lyr&&lyr.visible===false)continue;",
    "if(!bimLayerShown(o))continue;   /* __acad3dV121 */", 2)

# ---- 3. a locked layer's annotation is drawn; it is the picking that stops
rep("    var lyr=bimLayerOf(o);\n    if(lyr&&(lyr.visible===false||lyr.locked))return false;\n",
    "    /* __acad3dV121: shown, not pickable -- a locked layer is drawn. This read `locked` as hidden,\n"
    "       and it decides whether a room tag is drawn, exported and counted: locking a layer took its\n"
    "       tags off the canvas, the exports and every sheet, and brought the rooms' own labels back.\n"
    "       Picking asks bimLayerPickable below. */\n"
    "    if(!bimLayerShown(o))return false;\n")
rep("      if(o.t!==t||!bimAnnotDrawable(o))continue;\n",
    "      if(o.t!==t||!bimAnnotDrawable(o)||!bimLayerPickable(o))continue;   /* __acad3dV121 */\n")

# ---- 4. nothing snaps to what is not drawn
rep("      if(skip&&skip.indexOf(o.id)>=0)continue;   /* __acad3dV112 */\n",
    "      if(skip&&skip.indexOf(o.id)>=0)continue;   /* __acad3dV112 */\n"
    "      if(!bimLayerShown(o))continue;   /* __acad3dV121: a hidden layer's corners were snap targets */\n")
rep("          if(bimIsCline(t))continue;\n",
    "          if(bimIsCline(t)||!bimLayerShown(t))continue;   /* __acad3dV121 */\n")

# ---- 5. the extents leave out frozen layers, as AutoCAD's do (an off layer stays in them)
rep("      var o=list[i],m=meshOf(o),q=bimObjOffset(o);\n",
    "      var o=list[i],m=meshOf(o),q=bimObjOffset(o);\n"
    "      if(!ids&&bimObjLayerState(o).frozen)continue;   /* __acad3dV121 */\n")

# ---- nothing reads the flags for itself any more
code = re.sub(r'/\*.*?\*/', '', t, flags=re.S)
if re.search(r'lyr\s*&&\s*\(?\s*lyr\.(visible|locked)', code):
    sys.exit('ABORT: a site still reads a layer flag for itself')
callers = len(re.findall(r'(?<![\w.])bimLayerOf\(', code)) - 1
if callers != 1:
    sys.exit('ABORT: bimLayerOf has %d callers besides the state lookup, expected 1' % callers)
