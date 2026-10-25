  /* ================= __acad3dV121b: the old canvas's saved data, cleared =================
     The old canvas this file grew from kept its board, its predecessor's board, and the 2D wire
     shell's drawings, layouts, blocks, dock and grid in browser storage under these names. Nothing
     has read them since V113c and V117 took that code out, and the owner asked for them to go.
     Exactly these names are removed, at every start (an old copy of the file opened in the same
     browser writes them again): a page opened from disk shares its storage with every other page
     opened from disk, so nothing is removed by pattern, and the app's own keys are never here. */
  var A3D_CANVAS_KEYS=['obsidian-canvas-enhanced-v6','obsidian-canvas-enhanced-v5','acadDrawingsV1',
    'acadLayoutsV1','acadBlocksV1','acadDockV1','canvas-grid'];
  function bimClearCanvasStorage(){
    var gone=[],i,k;
    for(i=0;i<A3D_CANVAS_KEYS.length;i++){
      k=A3D_CANVAS_KEYS[i];
      try{
        if(localStorage.getItem(k)!==null){localStorage.removeItem(k);gone.push(k);}
      }catch(eC){
        console.warn('[BIM] The old canvas entry '+k+' could not be removed from browser storage.',eC);
        a3dToast('Some of the old canvas\'s saved data could not be removed from this browser');
        return gone;
      }
    }
    if(gone.length)a3dToast('Removed the old canvas\'s saved data from this browser ('+gone.length+' entr'+(gone.length===1?'y':'ies')+')');
    return gone;
  }
  var A3D_CANVAS_CLEARED=bimClearCanvasStorage();
  /* __acad3dV121b: the interface theme, the Appearance menu's Light or Dark, kept under the app's own
     name and put back at every start. The menu wrote 'canvas-theme', which nothing has read since
     V114 took the old canvas's start-up out; a value still there is carried over once and the old
     name removed. */
  var A3D_THEME_KEY='acad3dTheme';
  function bimThemeStore(light){
    try{localStorage.setItem(A3D_THEME_KEY,light?'light':'dark');}
    catch(eT){console.warn('[BIM] The interface theme could not be saved to browser storage.',eT);a3dToast('The interface theme could not be saved in this browser');}
  }
  function bimThemeRestore(){
    var v=null,old=null;
    try{
      v=localStorage.getItem(A3D_THEME_KEY);
      old=localStorage.getItem('canvas-theme');
      if(old!==null){
        if(v===null&&(old==='light'||old==='dark')){v=old;localStorage.setItem(A3D_THEME_KEY,v);}
        localStorage.removeItem('canvas-theme');
      }
    }catch(eR){console.warn('[BIM] The interface theme could not be read from browser storage.',eR);}
    if(v==='light'||v==='dark')document.body.classList.toggle('light-theme',v==='light');
    return v;
  }
  var A3D_THEME_AT_START=bimThemeRestore();

