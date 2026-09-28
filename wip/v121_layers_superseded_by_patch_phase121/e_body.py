rep("  function saveSoon(){\n",
    r"""  /* __acad3dV121: every object is on a layer. An object without one is adopted by the current layer
     -- the layer it was made on, since every maker calls saveSoon at once -- and one whose layer no
     longer exists by the first layer, which is what bimLayerOf reads it as. Nine makers never gave
     an object a layer, and a missing layer read as the CURRENT one: every wall followed whichever
     layer was current, out of sight when it was off and out of reach when it was locked. */
  function bimAdoptLayers(){
    var ids={},i,o,n=0,cur=bimLayerById(A3D.activeLayer)||A3D.layers[0],first=A3D.layers[0];
    if(!cur||!first)return 0;
    for(i=0;i<A3D.layers.length;i++)ids[A3D.layers[i].id]=1;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(typeof o.layer!=='string'||!o.layer){o.layer=cur.id;n++;}
      else if(!ids[o.layer]){o.layer=first.id;n++;}
    }
    return n;
  }
  function saveSoon(){
    bimAdoptLayers();   /* __acad3dV121 */
""")
rep("        if(A3D.classifications.length!==st.classifications.length)console.warn('[BIM] Discarded malformed classification(s) from '+LSK+' storage.');\n      }\n  }\n",
    "        if(A3D.classifications.length!==st.classifications.length)console.warn('[BIM] Discarded malformed classification(s) from '+LSK+' storage.');\n      }\n"
    "      /* __acad3dV121: an older project's layerless objects join the layer that was current when it\n"
    "         was saved -- the one they were being drawn as, so nothing changes on screen */\n"
    "      try{bimAdoptLayers();}\n"
    "      catch(eAd){console.warn('[BIM] Objects could not be given their layers; they follow the current one until the next save.',eAd);}\n"
    "  }\n")
