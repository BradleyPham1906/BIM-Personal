  // ---- Unified import entry point ----
  function bimHandleImportFile(file){
    if(!file)return;
    var name=file.name||'import',ext=(name.split('.').pop()||'').toLowerCase();
    var reader=new FileReader();
    reader.onerror=function(){a3dToast('Failed to read '+name);};
    if(ext==='stl'){
      reader.onload=function(ev){try{bimImportSTL(ev.target.result,name);}catch(eI){console.warn('[BIM] STL import crashed:',eI);a3dToast('STL import failed: '+(eI&&eI.message?eI.message:eI));}};
      reader.readAsArrayBuffer(file);
    }else if(ext==='skp'){   /* __acad3dV163: SketchUp */
      reader.onload=function(ev){bimImportSKP(ev.target.result,name);};
      reader.readAsArrayBuffer(file);
    }else if(ext==='dxf'){
      reader.onload=function(ev){try{bimImportDXF(ev.target.result,name);}catch(eI){console.warn('[BIM] DXF import crashed:',eI);a3dToast('DXF import failed: '+(eI&&eI.message?eI.message:eI));}};
      reader.readAsText(file);
    }else if(ext==='obj'){
      reader.onload=function(ev){try{bimImportOBJ(ev.target.result,name);}catch(eI){console.warn('[BIM] OBJ import crashed:',eI);a3dToast('OBJ import failed: '+(eI&&eI.message?eI.message:eI));}};
      reader.readAsText(file);
    }else if(ext==='ifc'){
      reader.onload=function(ev){try{bimImportIFC(ev.target.result,name);}catch(eI){console.warn('[BIM] IFC import crashed:',eI);a3dToast('IFC import failed: '+(eI&&eI.message?eI.message:eI));}};
      reader.readAsText(file);
    }else if(ext==='xml'||ext==='landxml'){   /* __acad3dV144: LandXML */
      reader.onload=function(ev){try{bimLandXmlImport(ev.target.result,name);}catch(eI){console.warn('[BIM] LandXML import crashed:',eI);a3dToast('LandXML import failed: '+(eI&&eI.message?eI.message:eI));}};
      reader.readAsText(file);
    }else if(ext==='geojson'||ext==='kml'||ext==='kmz'){   /* __acad3dV132: site data */
      bimGeoImportFile(file);
    }else if(ext==='cityjson'||(ext==='json'&&/\.city\.json$/i.test(name))){   /* __acad3dV139 */
      bimCityJsonFile(file);
    }else if(ext==='json'){
      bimOpenProjectFileObj(file);   /* __acad3dV115: the one project-file reader */
    }else if(ext==='dwg'||ext==='step'||ext==='stp'||ext==='iges'||ext==='igs'){
      a3dToast('.'+ext.toUpperCase()+' is not supported (proprietary binary / full B-rep format). Export as DXF (CAD) or IFC (BIM) instead.');
    }else{
      a3dToast('Unsupported file type: .'+ext+' (supported: .dxf, .ifc, .obj, .stl, .skp SketchUp, .json project files, .geojson and .kml site data, .city.json CityJSON, .xml LandXML)');
    }
  }

  function openPadDlg(kind){
    var s=selSketch();
    if(!s){a3dToast((kind==='pad'?'Pad':'Pocket')+' needs a sketch selected: draw one with the Sketch tools first');return;}
    closeDlg();
    var lab=kind==='pad'?'Height':'Depth';
    var d=document.createElement('div');
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">'+(kind==='pad'?'Pad':'Pocket')+' parameters</div>'+
      '<div class="a3d-dlgbody"><label>'+lab+'</label> <input type="number" step="any" data-a3dp="val" value="'+(kind==='pad'?'5':'2')+'"><div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">OK</button></div>';
    el.root.appendChild(d);
    el.dlg=d;
    var inp=d.querySelector('[data-a3dp="val"]');
    function submit(){
      var v=parseFloat(inp.value);
      if(!isFinite(v)||v<=0){document.getElementById('a3d-dlgerr').textContent=lab+' must be a positive number';return;}
      closeDlg();
      if(kind==='pad')doPad(s,v);else doPocket(s,v);
    }
    d.addEventListener('click',function(ev){
      var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;
      if(!b)return;
      if(b.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();
    });
    d.addEventListener('keydown',function(ev){
      if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}
      else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}
    });
    inp.focus();inp.select();
  }

  function toScreen(p,V,W,H){
    var x=p[0]-V.eye[0],y=p[1]-V.eye[1],z=p[2]-V.eye[2];
    var xc=x*V.r[0]+y*V.r[1]+z*V.r[2];
    var yc=x*V.u[0]+y*V.u[1]+z*V.u[2];
    var zc=x*V.d[0]+y*V.d[1]+z*V.d[2];
    if(A3D.flat){
      var k=H*1.2/Math.max(A3D.cam.dist,0.5);
      return [W/2+xc*k,H/2-yc*k,Math.max(-zc,0.5)];
    }
    var w=-zc;if(w<0.5)w=0.5;
    var f=H*1.2;
    return [W/2+xc*f/w,H/2-yc*f/w,w];
  }
  function shade(hex,k){
    var n=parseInt(hex.slice(1),16),r=(n>>16)&255,g=(n>>8)&255,b=n&255;
    r=Math.max(0,Math.min(255,Math.round(r*k)));
    g=Math.max(0,Math.min(255,Math.round(g*k)));
    b=Math.max(0,Math.min(255,Math.round(b*k)));
    return 'rgb('+r+','+g+','+b+')';
  }
