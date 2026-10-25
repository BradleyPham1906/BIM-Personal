  // ---- OBJ (Wavefront, Y-up - matches this engine's convention directly) ----
  function objParse(text){
    var lines=text.split(/\r\n|\r|\n/),i;
    var verts=[];
    var groups=[];
    var cur={name:'default',faces:[]};
    groups.push(cur);
    for(i=0;i<lines.length;i++){
      var ln=lines[i].trim();
      if(!ln||ln.charAt(0)==='#')continue;
      var parts=ln.split(/\s+/),tag=parts[0];
      if(tag==='v'){
        verts.push([parseFloat(parts[1]),parseFloat(parts[2]),parseFloat(parts[3])]);
      }else if(tag==='g'||tag==='o'){
        var nm=parts.slice(1).join(' ')||('group'+(groups.length));
        if(cur.faces.length===0&&cur===groups[groups.length-1]&&groups.length===1&&cur.name==='default'){
          cur.name=nm;
        }else{
          cur={name:nm,faces:[]};
          groups.push(cur);
        }
      }else if(tag==='f'){
        var idx=[],k;
        for(k=1;k<parts.length;k++){
          var vi=parseInt(parts[k].split('/')[0],10);
          if(!isFinite(vi))continue;
          if(vi<0)vi=verts.length+1+vi;
          idx.push(vi);
        }
        if(idx.length>=3)cur.faces.push(idx);
      }
    }
    groups=groups.filter(function(g){return g.faces.length>0;});
    var out=[];
    for(i=0;i<groups.length;i++){
      var g=groups[i],vmap={},lv=[],lf=[],j,k2;
      for(j=0;j<g.faces.length;j++){
        var face=g.faces[j],lface=[];
        for(k2=0;k2<face.length;k2++){
          var gi=face[k2];
          if(vmap[gi]===undefined){vmap[gi]=lv.length;lv.push(verts[gi-1]||[0,0,0]);}
          lface.push(vmap[gi]);
        }
        lf.push(lface);
      }
      out.push({name:g.name,v:lv,f:lf});
    }
    return {meshes:out,vertCount:verts.length};
  }
  function bimImportOBJ(text,filename){
    var res;
    try{res=objParse(text);}
    catch(eP){console.warn('[BIM] OBJ parse failed:',eP);a3dToast('OBJ import failed: could not parse '+filename);return;}
    if(!res.meshes.length){a3dToast('OBJ import: no faces found in '+filename);return;}
    pushUndo();
    undoSuspend=true;
    var i,created=0,lyr;
    try{
      lyr=addLayer(filename.replace(/\.[^.]+$/,''),'#9db4c8');
      for(i=0;i<res.meshes.length;i++){
        var g=res.meshes[i];
        if(!g.v.length||!g.f.length)continue;
        A3D.counts.mesh=(A3D.counts.mesh||0)+1;
        var o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:(g.name||'Mesh')+'_'+A3D.counts.mesh,col:'#9db4c8',pos:[0,0,0],mesh:{v:g.v,f:g.f},layer:lyr.id,locked:true};
        A3D.objs.push(o);
        created++;
      }
    }finally{
      undoSuspend=false;
    }
    refreshTree();refreshLayers();fitScene();paint();saveSoon();
    a3dToast('OBJ import: '+created+' mesh object(s) from '+filename+' ('+res.vertCount+' vertices)');
  }

  // ---- STL (ASCII + binary, sniffed automatically) ----
  function stlIsBinary(buf){
    if(buf.byteLength<84)return false;
    var dv=new DataView(buf);
    var triCount=dv.getUint32(80,true);
    return (84+triCount*50)===buf.byteLength;
  }
  function stlParseBinary(buf){
    var dv=new DataView(buf);
    var triCount=dv.getUint32(80,true);
    var v=[],f=[],off=84,i;
    for(i=0;i<triCount;i++){
      var base=off+i*50;
      var ax=dv.getFloat32(base+12,true),ay=dv.getFloat32(base+16,true),az=dv.getFloat32(base+20,true);
      var bx=dv.getFloat32(base+24,true),by=dv.getFloat32(base+28,true),bz=dv.getFloat32(base+32,true);
      var cx=dv.getFloat32(base+36,true),cy=dv.getFloat32(base+40,true),cz=dv.getFloat32(base+44,true);
      var i0=v.length;
      v.push([ax,ay,az],[bx,by,bz],[cx,cy,cz]);
      f.push([i0,i0+1,i0+2]);
    }
    return {v:v,f:f};
  }
  function stlParseAscii(text){
    var v=[],f=[],re=/vertex\s+([\-0-9.eE+]+)\s+([\-0-9.eE+]+)\s+([\-0-9.eE+]+)/g,m,tri=[];
    while((m=re.exec(text))){
      tri.push([parseFloat(m[1]),parseFloat(m[2]),parseFloat(m[3])]);
      if(tri.length===3){
        var i0=v.length;
        v.push(tri[0],tri[1],tri[2]);
        f.push([i0,i0+1,i0+2]);
        tri=[];
      }
    }
    return {v:v,f:f};
  }
  function bimImportSTL(buf,filename){
    var parsed,isBin;
    try{
      isBin=stlIsBinary(buf);
      parsed=isBin?stlParseBinary(buf):stlParseAscii(bimDecodeUtf8(buf));
    }catch(eP){console.warn('[BIM] STL parse failed:',eP);a3dToast('STL import failed: could not parse '+filename);return;}
    if(!parsed||!parsed.f.length){a3dToast('STL import: no triangles found in '+filename);return;}
    pushUndo();
    undoSuspend=true;
    try{
      var lyr=addLayer(filename.replace(/\.[^.]+$/,''),'#9db4c8');
      A3D.counts.mesh=(A3D.counts.mesh||0)+1;
      var o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:'STL_'+A3D.counts.mesh,col:'#9db4c8',pos:[0,0,0],mesh:{v:parsed.v,f:parsed.f},layer:lyr.id,locked:true};
      A3D.objs.push(o);
    }finally{
      undoSuspend=false;
    }
    refreshTree();refreshLayers();fitScene();paint();saveSoon();
    a3dToast('STL import ('+(isBin?'binary':'ASCII')+'): '+parsed.f.length+' triangles from '+filename);
  }

