  /* ================= __acad3dV163: SketchUp files =================
     A .skp file is read by openskp's reader (MIT; the script block above the engine), which takes
     both of SketchUp's containers: the archive of SketchUp 2020 and earlier, and the ZIP of 2021 and
     later. It hands back the placed scene -- every instance with its transform, each definition's
     triangles once -- and the model's tables: tags, materials, definitions. They become:
       faces       a locked solid for each placement and material, in world position, as an OBJ's
                   are, so a model comes in where it was drawn
       a tag       a sub-layer of the file's layer, in the tag's colour, off when SketchUp had it off
                   (Rhino and Revit both bring tags in as layers)
       a material  the solid's colour. A texture's colour is the one SketchUp keeps with it -- the
                   image's average, what SketchUp's Shaded style draws -- and the texture's file is
                   named in Properties. A see-through material goes on a sub-layer of its tag at the
                   material's opacity, as this app keeps transparency on layers
       a component an Assets block, in its own frame, the insertion point its base point, when it
                   has a name of its own. A group is not one, nor a component left as SketchUp named
                   it (Component#1): the reader keeps no mark of which a definition is, so the name
                   decides, as below
     SketchUp keeps inches, Z up and +Y north; the reader gives metres, Y up and north at -Z, which is
     this app's own frame, so nothing is turned. One undo step; the current layer stays current. */
  var BIM_SKP={maxTris:250000,blockTris:6000,blockChars:1500000};
  /* SketchUp names what nobody named, in the language it runs in: Group#1, Component#2, Agrupar#2,
     Componente#1. A name ending #N is SketchUp's own unless what comes before the # is itself a
     definition in the file -- Chair#1 is what Make Unique makes of Chair. */
  function bimSkpGenerated(n,defNames){
    var m=/^([^#]+)#\d+$/.exec(String(n||''));
    return !!m&&!(defNames&&defNames.hasOwnProperty(m[1]));
  }
  var BIM_SKP_GROUPWORDS=/^(?:Group|Gruppe|Groupe|Grupo|Agrupar|Gruppo|Groep)\d*$/i;
  var BIM_SKP_COMPWORDS=/^(?:Component|Komponente|Composant|Componente)\d*$/i;
  var BIM_SKP_DEFAULT='#ffffff';   /* SketchUp's default front face: an unpainted face */
  function bimSkpReader(){
    return (typeof OpenSkp!=='undefined'&&OpenSkp&&typeof OpenSkp.buildInstancedScene==='function'&&typeof OpenSkp.parseSkp==='function')?OpenSkp:null;
  }
  /* the SketchUp that saved the file, from the version in its header: 17 is SketchUp 2017. From 21
     on, what follows the header is a ZIP; before, SketchUp's own archive. */
  function bimSkpVersion(model){
    var m=/(\d+)\.\d+/.exec(String(model&&model.version||'')),v=m?parseInt(m[1],10):0;
    return {major:v,name:v>=13?'SketchUp '+(2000+v):(v?'SketchUp '+v:'an unnamed SketchUp version'),zip:v>=21};
  }
  function bimSkpWhy(e){
    var m=String(e&&e.message?e.message:e);
    return m.length>160?m.slice(0,157)+'...':m;
  }
  var BIM_SKP_BADCHARS=new RegExp(BIM_LAYER_BADCHARS.source,'g');
  function bimSkpLayerName(s){
    s=String(s==null?'':s).replace(BIM_SKP_BADCHARS,'-').replace(/\s+/g,' ').replace(/^\s+|\s+$/g,'');
    return s.length>64?s.slice(0,64).replace(/\s+$/,''):s;
  }
  /* the layer called name under parentId: the one already there when the same file is opened again,
     made otherwise. A layer of that name elsewhere -- one of the project's own -- is not taken over:
     the new one is numbered. */
  function bimSkpLayer(name,color,parentId,made){
    var base=bimSkpLayerName(name)||'SketchUp',n=base,ex=bimLayerByName(n),k=2;
    while(ex&&(ex.parent||null)!==(parentId||null)){n=bimSkpLayerName(base.slice(0,58)+' '+k);ex=bimLayerByName(n);k++;}
    if(ex)return {ly:ex,fresh:false};
    var ly=bimLayerNew({name:n,color:color,parent:parentId||null});
    if(ly)made.push(ly.id);
    return {ly:ly,fresh:!!ly};
  }
  function bimSkpHex(c){
    return '#'+[c.r,c.g,c.b].map(function(x){var h=Math.max(0,Math.min(255,Math.round(x))).toString(16);return h.length<2?'0'+h:h;}).join('');
  }
  /* a glTF material's colour (0-255), its opacity and its texture's index */
  function bimSkpLook(m){
    var p=(m&&m.pbrMetallicRoughness)||{},f=p.baseColorFactor||[0.6,0.6,0.6,1];
    return {r:Math.round(f[0]*255),g:Math.round(f[1]*255),b:Math.round(f[2]*255),a:isFinite(f[3])?+f[3]:1,
      tex:(p.baseColorTexture&&isFinite(p.baseColorTexture.index))?p.baseColorTexture.index:-1,two:!!(m&&m.doubleSided)};
  }
  /* The material a colour came from: by colour and texture among the file's materials, leaving out the
     Layer_ stand-ins a 2021 file keeps for its tags. '' for a face painted with none of them. */
  function bimSkpMatName(mats,c,texName){
    var pass,i,m;
    for(pass=0;pass<2;pass++)for(i=0;i<mats.length;i++){
      m=mats[i];
      if(!m||!m.color||/^Layer_/.test(String(m.name||'')))continue;
      if(m.color.r!==c.r||m.color.g!==c.g||m.color.b!==c.b)continue;
      if(!pass&&String((m.texture&&m.texture.filename)||'')!==String(texName||''))continue;
      return String(m.name||'');
    }
    return '';
  }
  /* SketchUp shows its own materials' names without the brackets they are stored in */
  function bimSkpMatShown(n){return String(n||'').replace(/^\[(.*)\]$/,'$1');}
  /* the colour an unpainted face of a resource falls back to: what its instance is painted, else its
     tag's colour -- the last two fields of openskp's variant key, which it exposes for this */
  function bimSkpFallback(key){
    var s=String(key||'').split('|');
    return s.length>=5?s[s.length-3]:(s[s.length-1]||'');
  }
  /* openskp draws a face whose two sides differ twice: its front, and its back wound the other way.
     Here a face is one face. Of two triangles on the same three points wound opposite ways, the one in
     the colour an unpainted face falls back to -- a back nobody painted -- goes; when both sides are
     painted, the one in the later primitive goes. Returns each primitive's kept triangles. */
  function bimSkpFronts(res,gm){
    var P=res.primitives||[],fb=bimSkpFallback(res.variantKey),T={},keep=[],cols=[],i,t,k;
    function pk(pos,n){return Math.round(pos[3*n]*1e5)+','+Math.round(pos[3*n+1]*1e5)+','+Math.round(pos[3*n+2]*1e5);}
    for(i=0;i<P.length;i++){
      var L=bimSkpLook(gm[P[i].materialIndex]),n=Math.floor(P[i].indices.length/3);
      cols.push(L.r+','+L.g+','+L.b);
      keep.push([]);
      for(t=0;t<n;t++)keep[i].push(true);
      if(L.two)continue;
      for(t=0;t<n;t++){
        var ix=P[i].indices,A=pk(P[i].positions,ix[3*t]),B=pk(P[i].positions,ix[3*t+1]),C=pk(P[i].positions,ix[3*t+2]);
        var s=[A,B,C].sort(),even=(A===s[0]&&B===s[1])||(B===s[0]&&C===s[1])||(C===s[0]&&A===s[1]);
        k=s.join(';');
        (T[k]||(T[k]={e:[],o:[]}))[even?'e':'o'].push([i,t]);
      }
    }
    for(k in T){
      if(!T.hasOwnProperty(k)||!T[k].e.length||!T[k].o.length)continue;
      var E=T[k].e,O=T[k].o,ce=cols[E[0][0]],co=cols[O[0][0]],drop;
      if(co===fb&&ce!==fb)drop=O;
      else if(ce===fb&&co!==fb)drop=E;
      else drop=E[0][0]>O[0][0]?E:O;
      for(i=0;i<drop.length;i++)keep[drop[i][0]][drop[i][1]]=false;
    }
    return keep.map(function(fl){var o=[],j;for(j=0;j<fl.length;j++)if(fl[j])o.push(j);return o;});
  }
  /* column-major 4x4: the glTF matrices the reader gives */
  function bimSkpMul(a,b){
    var o=[],r,c,k,s;
    for(c=0;c<4;c++)for(r=0;r<4;r++){s=0;for(k=0;k<4;k++)s+=a[k*4+r]*b[c*4+k];o[c*4+r]=s;}
    return o;
  }
  var BIM_SKP_ID=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1];
  /* a primitive's kept triangles placed by M, its points welded at a hundredth of a millimetre; a
     mirroring placement turns the faces back the right way out */
  function bimSkpMesh(p,tris,M){
    var v=[],f=[],map={},pos=p.positions,ix=p.indices,j;
    var det=M[0]*(M[5]*M[10]-M[9]*M[6])-M[4]*(M[1]*M[10]-M[9]*M[2])+M[8]*(M[1]*M[6]-M[5]*M[2]);
    function vert(n){
      var x=pos[3*n],y=pos[3*n+1],z=pos[3*n+2];
      var X=Math.round((M[0]*x+M[4]*y+M[8]*z+M[12])*1e5)/1e5,Y=Math.round((M[1]*x+M[5]*y+M[9]*z+M[13])*1e5)/1e5,Z=Math.round((M[2]*x+M[6]*y+M[10]*z+M[14])*1e5)/1e5;
      var key=X+','+Y+','+Z;
      if(!map.hasOwnProperty(key)){map[key]=v.length;v.push([X,Y,Z]);}
      return map[key];
    }
    for(j=0;j<tris.length;j++){
      var a=vert(ix[3*tris[j]]),b=vert(ix[3*tris[j]+1]),c=vert(ix[3*tris[j]+2]);
      if(a===b||b===c||a===c)continue;
      f.push(det<0?[a,c,b]:[a,b,c]);
    }
    return {v:v,f:f};
  }
  /* what a placed node is: loose faces, a group, a component, or -- left as SketchUp named it, in a
     language this does not know -- one of the two */
  function bimSkpKind(n,isRoot,G){
    if(isRoot)return 'loose';
    var d=String(n.definitionName||''),w=d.split('#')[0];
    if(!bimSkpGenerated(d,G))return 'component';
    return BIM_SKP_GROUPWORDS.test(w)?'group':(BIM_SKP_COMPWORDS.test(w)?'component':'unnamed');
  }
  /* its name, as SketchUp's Outliner shows it: the instance's own, else its component's, else the
     word SketchUp named it with (Group) */
  function bimSkpBaseName(n,isRoot,G){
    if(isRoot)return '';
    if(!n.nameIsGenerated&&n.name&&!bimSkpGenerated(n.name,G))return String(n.name);
    var d=String(n.definitionName||'');
    if(d&&!bimSkpGenerated(d,G))return d;
    return d.split('#')[0]||'Component';
  }
  /* Read a .skp into the pieces the import places: no change to the model yet. */
  function bimSkpScan(buf,name){
    var R=bimSkpReader();
    if(!R)return {error:'The SketchUp reader did not load in this browser, so '+name+' cannot be read'};
    if(!buf||!(buf.byteLength>0))return {error:name+' is empty'};
    var scene,model;
    try{scene=R.buildInstancedScene(buf);model=R.parseSkp(buf);}
    catch(eR){console.warn('[BIM] SketchUp read failed:',eR);return {error:'Could not read '+name+' as a SketchUp file: '+bimSkpWhy(eR)};}
    var gm=scene.gltfMaterials||[],tex=scene.textures||[],mats=model.materials||[],res={},fronts={},tags={},G={},i;
    if(model.definitions&&typeof model.definitions.forEach==='function')model.definitions.forEach(function(d){if(d&&d.name)G[d.name]=1;});
    var ver=bimSkpVersion(model);
    for(i=0;i<(scene.meshResources||[]).length;i++)res[scene.meshResources[i].id]=scene.meshResources[i];
    for(i=0;i<(model.layers||[]).length;i++){
      var ml=model.layers[i];
      tags[ml.name]={color:bimSkpHex(ml.color||{r:136,g:136,b:136}),hidden:!!ml.hidden};
    }
    var lh=scene.layerHidden||{},kname;
    for(kname in lh)if(lh.hasOwnProperty(kname)){if(!tags[kname])tags[kname]={color:'#888888',hidden:false};if(lh[kname]===true)tags[kname].hidden=true;}
    var parts=[],tris=0,trunc=false,defs={},defOrder=[];
    /* the triangles of one placed node, as parts placed by M; path is the chain of names above it */
    function partsOf(n,M,isRoot,path,out,count){
      if(!n.meshResourceId||!res[n.meshResourceId])return 0;
      var r=res[n.meshResourceId],keep=fronts[r.id]||(fronts[r.id]=bimSkpFronts(r,gm)),used=0,j,made=0;
      for(j=0;j<r.primitives.length;j++)if(keep[j].length)used++;
      for(j=0;j<r.primitives.length;j++){
        if(!keep[j].length)continue;
        if(count&&tris+keep[j].length>BIM_SKP.maxTris){trunc=true;return made;}
        var p=r.primitives[j],L=bimSkpLook(gm[p.materialIndex]),tn=(L.tex>=0&&tex[L.tex])?String(tex[L.tex].filename||'texture'):'';
        var mn=bimSkpMatName(mats,L,tn),shown=bimSkpMatShown(mn),mesh=bimSkpMesh(p,keep[j],M);
        if(!mesh.f.length)continue;
        if(count)tris+=mesh.f.length;
        var base=isRoot?(shown||'Unpainted')+' faces':bimSkpBaseName(n,false,G)+(used>1?' ('+(shown||'unpainted')+')':'');
        out.push({name:base.slice(0,60),mesh:mesh,col:mn?bimSkpHex(L):BIM_SKP_DEFAULT,opacity:L.a<0.98?Math.round(L.a*100)/100:1,
          tag:isRoot?'':String(n.layer||''),material:shown,texture:tn,kind:bimSkpKind(n,isRoot,G),definition:isRoot?'':String(n.definitionName||''),
          instance:isRoot?'':String(n.name||''),guid:String(n.guid||''),path:path.slice()});
        made++;
      }
      return made;
    }
    function walk(n,W,isRoot,path){
      if(trunc)return;
      var M=isRoot?BIM_SKP_ID:bimSkpMul(W,n.matrix||BIM_SKP_ID),pth=isRoot?[]:path.concat([bimSkpBaseName(n,false,G)]),c;
      if(!isRoot&&n.definitionName&&!bimSkpGenerated(n.definitionName,G)&&!defs.hasOwnProperty(n.definitionName)){
        defs[n.definitionName]=n;defOrder.push(n.definitionName);
      }
      partsOf(n,M,isRoot,pth,parts,true);
      for(c=0;c<(n.children||[]).length;c++)walk(n.children[c],M,false,pth);
    }
    walk(scene.sceneHierarchy,BIM_SKP_ID,true,[]);
    /* a component's block: its own triangles and everything placed inside it, in its own frame */
    var blocks=[];
    for(i=0;i<defOrder.length;i++){
      var bp=[],bn=defs[defOrder[i]];
      (function inner(n,W,top){
        var M=top?BIM_SKP_ID:bimSkpMul(W,n.matrix||BIM_SKP_ID),c;
        partsOf(n,M,false,[],bp,false);
        for(c=0;c<(n.children||[]).length;c++)inner(n.children[c],M,false);
      })(bn,BIM_SKP_ID,true);
      if(bp.length)blocks.push({name:defOrder[i],parts:bp,tris:bp.reduce(function(s,q){return s+q.mesh.f.length;},0)});
    }
    return {parts:parts,blocks:blocks,tags:tags,tris:tris,truncated:trunc,format:ver.name,zip:ver.zip,units:model.units||null};
  }
  /* The import. opt.blocksOnly keeps the components in Assets and places nothing (the library's
     Import). Returns what it did, or {error}. */
  function bimSkpImportBuffer(buf,filename,opt){
    opt=opt||{};
    var name=String(filename||'model.skp'),stem=name.replace(/^.*[\\\/]/,'').replace(/\.skp$/i,'')||'SketchUp',t0=Date.now();
    var S=bimSkpScan(buf,name);
    if(S.error)return S;
    if(!S.parts.length&&!S.blocks.length)return {error:'No faces in '+name+' to bring in'};
    if(opt.blocksOnly&&!S.blocks.length)return {error:'No components in '+name+' to keep as blocks: its groups and loose faces are not blocks'};
    var made=[],ids=[],seeThrough={},hiddenTags=0,usedTags={},i,was=A3D.activeLayer;
    if(!opt.blocksOnly&&S.parts.length){
      pushUndo();
      undoSuspend=true;
      try{
        var fl=bimSkpLayer(stem,'#9db4c8',null,made).ly,tagLy={};
        if(!fl)throw new Error('the layer '+stem+' could not be made');
        for(i=0;i<S.parts.length;i++){
          var q=S.parts[i],tg=(q.tag&&q.tag!=='Layer0')?q.tag:'',ly=fl;
          if(tg){
            if(!tagLy[tg]){
              var info=S.tags[tg]||{color:'#888888',hidden:false},got=bimSkpLayer(stem+' - '+tg,info.color,fl.id,made);
              tagLy[tg]=got.ly||fl;
              if(got.fresh&&info.hidden){got.ly.visible=false;hiddenTags++;}
            }
            ly=tagLy[tg];usedTags[tg]=1;
          }
          if(q.opacity<1&&ly.visible!==false){
            var pct=Math.max(5,Math.min(90,Math.round((1-q.opacity)*20)*5)),sk=ly.id+'|'+pct;
            if(!seeThrough[sk]){
              var st=bimSkpLayer(ly.name+' - '+pct+'% see-through',ly.color,ly.id,made);
              if(st.fresh)st.ly.transparency=pct;
              seeThrough[sk]=st.ly||ly;
            }
            ly=seeThrough[sk];
          }
          var o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:q.name,col:q.col,pos:[0,0,0],mesh:q.mesh,layer:ly.id,locked:true,
            skp:{file:name.slice(0,120),format:S.format,kind:q.kind,definition:q.definition.slice(0,120),instance:q.instance.slice(0,120),tag:q.tag==='Layer0'?'':q.tag,
              material:q.material,texture:q.texture,opacity:q.opacity,guid:q.guid,path:q.path.slice(0,12)}};
          A3D.objs.push(o);ids.push(o.id);
          q.layerId=ly.id;
        }
      }finally{undoSuspend=false;}
      if(bimLayerById(was))A3D.activeLayer=was;
    }
    /* the components, as blocks in the library: the same file opened again replaces its own */
    var kept=[],big=0,room=0,chars=0;
    if(!opt.noBlocks&&S.blocks.length){
      var byKey={};
      for(i=0;i<S.parts.length;i++)if(S.parts[i].layerId)byKey[S.parts[i].definition+'|'+S.parts[i].tag]=S.parts[i].layerId;
      for(i=0;i<S.blocks.length;i++){
        var B=S.blocks[i];
        if(B.tris>BIM_SKP.blockTris){big++;continue;}
        var recs=B.parts.map(function(q,k){
          var lid=byKey[q.definition+'|'+q.tag]||byKey[B.name+'|'+q.tag]||null;
          return {id:'skp-'+k,t:'solid',name:q.name,col:q.col,pos:[0,0,0],mesh:q.mesh,layer:lid,
            skp:{file:name.slice(0,120),format:S.format,kind:q.kind,definition:q.definition.slice(0,120),instance:'',tag:q.tag==='Layer0'?'':q.tag,
              material:q.material,texture:q.texture,opacity:q.opacity,guid:'',path:[]}};
        });
        var entry={id:'blk-'+Date.now().toString(36)+'-'+Math.floor(Math.random()*1e6),kind:'block',name:B.name.slice(0,60),category:'SketchUp',
          manufacturer:'',source:name.slice(0,120),recs:recs,base:[0,0],y0:0,count:recs.length,createdAt:new Date().toISOString()};
        entry.thumb=bimMeshThumb(bimMergeMeshes(recs.map(function(r){return r.mesh;})));
        var sz=JSON.stringify(entry).length;
        if(chars+sz>BIM_SKP.blockChars){room++;continue;}
        chars+=sz;
        for(var d=A3D_FAMLIB.length-1;d>=0;d--){
          var ex=A3D_FAMLIB[d];
          if(bimAssetKind(ex)==='block'&&ex.category==='SketchUp'&&ex.source===entry.source&&ex.name===entry.name)A3D_FAMLIB.splice(d,1);
        }
        A3D_FAMLIB.push(entry);
        kept.push(entry.name);
      }
      if(kept.length){bimSaveFamilyLibrary();refreshFamilyPanel();}
    }
    if(ids.length){refreshTree();refreshLayers();refreshProps();fitScene();paint();saveSoon();}
    var nt=Object.keys(usedTags).length;
    return {ids:ids,layers:made,blocks:kept,tags:Object.keys(usedTags),hiddenTags:hiddenTags,seeThrough:Object.keys(seeThrough).length,
      triangles:S.tris,truncated:S.truncated,blocksTooBig:big,blocksNoRoom:room,format:S.format,zip:S.zip,ms:Date.now()-t0,
      text:(opt.blocksOnly?'SketchUp: '+kept.length+' component'+(kept.length===1?'':'s')+' from '+name+' kept as '+(kept.length===1?'a block':'blocks')+' in Assets':
        'SketchUp: '+ids.length+' object'+(ids.length===1?'':'s')+' from '+name+' (saved by '+S.format+') on the '+stem+' layer'+
        (nt?', its '+nt+' tag'+(nt===1?'':'s')+' as sub-layers'+(hiddenTags?' ('+hiddenTags+' off, as in SketchUp)':''):'')+
        (Object.keys(seeThrough).length?'; see-through materials on their own layer':'')+
        (kept.length?'; '+kept.length+' component'+(kept.length===1?' kept as a block':'s kept as blocks')+' in Assets':''))+
        (S.truncated?'; stopped at '+BIM_SKP.maxTris+' triangles':'')+
        (big?'; '+big+' component'+(big===1?' is':'s are')+' over '+BIM_SKP.blockTris+' triangles, too large to keep as a block':'')+
        (room?'; '+room+' more component'+(room===1?'':'s')+' did not fit in the library':'')};
  }
  function bimImportSKP(buf,filename,opt){
    var name=String(filename||'model.skp');
    a3dToast('Reading '+name+'...');
    /* the toast is drawn before the read, which takes a second or two for a large model */
    setTimeout(function(){
      var r;
      try{r=bimSkpImportBuffer(buf,name,opt);}
      catch(eI){console.warn('[BIM] SketchUp import failed:',eI);a3dToast('SketchUp import failed: '+bimSkpWhy(eI));return;}
      a3dToast(r.error||r.text);
    },30);
  }
  function bimSkpPick(){
    var inp=document.createElement('input');
    inp.type='file';inp.accept='.skp';
    inp.onchange=function(){var f=inp.files&&inp.files[0];if(f)bimHandleImportFile(f);};
    inp.click();
    return true;
  }
  function bimSkpPropsHtml(o){
    var s=o.skp,r='';
    r+=bimPropText('File',s.file+(s.format?', '+s.format:''));
    if(s.kind==='loose')r+=bimPropText('Faces','loose, in no group or component');
    else if(s.kind==='group')r+=bimPropText('Group',s.instance&&s.instance!==s.definition?s.instance:'unnamed ('+s.definition+')');
    else if(s.kind==='unnamed')r+=bimPropText('Group or Component','unnamed ('+s.definition+')');
    else r+=bimPropText('Component',s.definition+(s.instance&&s.instance!==s.definition?' ('+s.instance+')':''));
    if(s.path&&s.path.length>1)r+=bimPropText('Inside',s.path.slice(0,-1).join(' / '));
    r+=bimPropText('Tag',s.tag||'Untagged');
    r+=bimPropText('Material',s.material||'none (unpainted)');
    if(s.texture)r+=bimPropText('Texture',s.texture+', drawn in the colour SketchUp keeps with it');
    if(s.opacity<1)r+=bimPropText('Opacity',Math.round(s.opacity*100)+'%, on a see-through layer');
    return r;
  }

