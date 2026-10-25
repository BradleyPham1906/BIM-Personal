  /* ================= __acad3dV133: site context in Properties ================= */
  function bimCtxCountsText(c){
    var s=[],i,k;
    for(i=0;i<BIM_CTX_KINDS.length;i++){k=BIM_CTX_KINDS[i];if(c&&c[k])s.push(c[k]+' '+(k==='terrain'?'surface':BIM_CTX_LABEL[k].toLowerCase()));}
    return s.length?s.join(', '):'nothing';
  }
  function bimCtxModelHtml(){
    var st=bimCtxSettings(),r='',i,k,ck='',last=A3D.site&&A3D.site.context&&A3D.site.context.last;
    r+=bimPropRow('Radius (m)','<input type="number" min="50" max="1000" step="10" data-propctx="radius" value="'+st.radius+'" title="How far around the property lines, or around model 0,0">');
    for(i=0;i<BIM_CTX_KINDS.length;i++){
      k=BIM_CTX_KINDS[i];
      ck+='<label class="a3d-ctxk"><input type="checkbox" data-propctx="kind:'+k+'"'+(st.kinds[k]?' checked':'')+'> '+BIM_CTX_LABEL[k]+'</label>';
    }
    r+=bimPropRow('Get','<div class="a3d-ctxks">'+ck+'</div>');
    r+=bimPropRow('Buildings','<label class="a3d-ctxk"><input type="checkbox" data-propctx="onGround"'+(st.onGround?' checked':'')+
      '> On the terrain</label>');   /* __acad3dV137 */
    r+=bimPropRow('Overpass','<input type="text" data-propctx="overpass" value="'+bimEsc(st.overpass)+'" spellcheck="false" title="The Overpass API server OpenStreetMap is read from">');
    r+=bimPropRow('','<button type="button" class="a3d-pedit" data-propctxact="get">Get Context</button> '+
      '<button type="button" class="a3d-pedit" data-propctxact="remove">Remove Context</button>');
    r+=bimPropRow('LOD','<button type="button" class="a3d-pedit" data-propctxact="lodcheck" title="Every building\'s LOD, and whether it is a valid solid">Check LODs</button> '+
      '<button type="button" class="a3d-pedit" data-propctxact="cjout" title="The buildings as CityJSON 2.0, in the site\'s UTM zone">Export CityJSON</button> '+
      '<button type="button" class="a3d-pedit" data-propctxact="cjin">Import CityJSON</button>');   /* __acad3dV139 */
    if(last)r+=bimPropText('Last Fetch',last.date+': '+bimCtxCountsText(last.counts)+(last.parts?' ('+last.parts+' building part'+(last.parts===1?'':'s')+', LOD1.3)':'')+   /* __acad3dV139 */
      (last.roofs?' ('+last.roofs+' LOD2 roof'+(last.roofs===1?'':'s')+')':'')+   /* __acad3dV140 */
      (last.errors&&last.errors.length?'; '+last.errors.join('; '):''));
    r+=bimPropText('Sources','OpenStreetMap (ODbL) through Overpass; AWS Terrain Tiles');
    return r;
  }
  /* ================= __acad3dV139: the LOD group ================= */
  function bimLodHtml(o){
    var L=bimLodOf(o),r='',chk=bimObjSolidCheck(o),cj=o.cityjson,c=o.context;
    if(!L)return '';
    r+='<div class="a3d-prow" data-lodrow="lod"><div class="a3d-plabel">LOD</div><div class="a3d-pval"><span class="a3d-lodtag">LOD'+bimEsc(L.lod||'?')+'</span> '+
      '<span class="a3d-pstatic">'+bimEsc(bimLodText(L.lod))+'</span></div></div>';
    r+='<div class="a3d-prow" data-lodrow="how"><div class="a3d-plabel">How Made</div><div class="a3d-pval"><span class="a3d-pstatic">'+bimEsc(L.how)+'</span></div></div>';
    if(chk)r+='<div class="a3d-prow a3d-svrow" data-lodrow="solid"><div class="a3d-plabel">'+(chk.surface?'Surfaces':'Solid')+'</div><div class="a3d-pval">'+
      '<span class="a3d-svck a3d-svck-'+(chk.valid?'pass':'fail')+'">'+(chk.valid?'\u2713':'\u2717')+'</span> <span class="a3d-pstatic">'+bimEsc(bimSolidCheckText(chk))+'</span></div></div>';
    if(c&&c.building)r+=bimPropText('Building',(c.building.name||'unnamed')+' ('+c.building.osm+' '+c.building.id+')');
    if(o.solar)r+=bimPropText('Solar',(o.solar.roof!==null?'roof '+o.solar.roof+' kWh/m\u00b2 a year ('+o.solar.roofKwh+' kWh)':'no roof')+   /* __acad3dV143 */
      (o.solar.facade!==null?', facades '+o.solar.facade+' kWh/m\u00b2 a year':'')+'; clear sky, '+o.solar.computed);
    if(c&&c.roof)r+='<div class="a3d-prow" data-lodrow="roof"><div class="a3d-plabel">Roof</div><div class="a3d-pval"><span class="a3d-pstatic">'+   /* __acad3dV140 */
      bimEsc(c.roof.shape+(c.roof.shape==='flat'?'':', '+bimDispNum(c.roof.height,2)+' m, '+c.roof.faces+' plane'+(c.roof.faces===1?'':'s'))+', eaves at '+bimDispNum((c.minHeight||0)+c.roof.eave,2)+' m')+'</span></div></div>';
    else if(c&&c.roofSkipped)r+='<div class="a3d-prow a3d-svrow" data-lodrow="roof"><div class="a3d-plabel">Roof</div><div class="a3d-pval"><span class="a3d-svck a3d-svck-warn">!</span> '+
      '<span class="a3d-pstatic">'+bimEsc('roof:shape='+c.roofSkipped.shape+' not built: '+c.roofSkipped.why)+'</span></div></div>';
    if(cj){
      r+=bimPropText('CityJSON',cj.type+' '+cj.id+(cj.geomType?', '+cj.geomType:''));
      if(cj.parent)r+=bimPropText('Part Of',(cj.parentAttributes&&cj.parentAttributes.name?cj.parentAttributes.name+' ':'')+'('+cj.parent+')');
      r+=bimPropText('File',cj.file+(cj.crs?', '+cj.crs:'')+(cj.placed==='centred'?', placed by its centre':''));
      var k,n=0;
      for(k in cj.attributes)if(cj.attributes.hasOwnProperty(k)&&n<40&&k!=='lodMethod'){n++;r+=bimPropText(k,cj.attributes[k]===null?'':String(cj.attributes[k]));}
    }
    return r;
  }
  function bimCtxPropsHtml(o){
    var c=o.context,r='',k,n=0;
    r+=bimPropText('Source',c.source+(c.osm?' '+c.osm+' '+c.id:'')+(c.fetched?', '+c.fetched:''));
    r+=bimPropText('Credit',c.credit||'');
    if(c.osm)r+=bimPropRow('On OSM','<a class="a3d-ctxlink" href="https://www.openstreetmap.org/'+bimEsc(c.osm)+'/'+bimEsc(String(c.id))+'" target="_blank" rel="noopener">openstreetmap.org/'+bimEsc(c.osm)+'/'+bimEsc(String(c.id))+'</a>');
    if(c.kind==='buildings'){
      r+=bimPropText('Height',bimDispNum(c.height,2)+' m, '+({height:'from its height tag',levels:'its levels at '+bimCtxLevelH()+' m each',
        assumed:'assumed: OSM gives no height or levels'})[c.heightFrom]);
      if(c.courtyards)r+=bimPropText('Courtyards',c.courtyards+' filled in');
      if(c.ground!=null)r+=bimPropText('Ground',bimDispNum(c.ground,2)+' m from model y 0, on the terrain');
      if(c.standY)r+=bimPropText('Stands at',bimDispNum(c.standY,2)+' m: the lowest ground under '+(c.standFp?'its building':'it'));   /* __acad3dV137 */
      if(c.minHeight)r+=bimPropText('Base',bimDispNum(c.minHeight,2)+' m up, '+(c.minFrom==='levels'?'its min level at '+bimCtxLevelH()+' m each':'from its min_height tag'));   /* __acad3dV139 */
    }
    if(c.part==='hole')r+=bimPropText('Ring','a hole in the area before it');
    if(c.use)r+=bimPropText('Use',BIM_ROAD_USE_LABEL[c.use]||c.use);   /* __acad3dV157: the surroundings in 3D */
    if(c.width)r+=bimPropText('Width',bimDispNum(c.width,2)+' m');
    if(c.bridge)r+=bimPropText('Bridge','its deck '+bimDispNum(c.deck,2)+' m above the ground, on piers every '+bimCtxPier()+' m');
    if(c.tunnel)r+=bimPropText('Tunnel','below ground: its centre line only');
    if(c.kind==='trees'&&c.leaf&&(c.leaf.type||c.leaf.cyc))r+=bimPropText('Leaf',(c.leaf.type==='C'?'needle-leaved':(c.leaf.type==='B'?'broadleaved':'its leaf type not mapped'))+', '+(c.leaf.cyc==='E'?'evergreen':(c.leaf.cyc==='D'?'deciduous':'its leaf cycle not mapped')));   /* __acad3dV169 */
    if((c.kind==='trees'||c.kind==='power')&&c.height)r+=bimPropText('Height',bimDispNum(c.height,2)+' m'+(c.crown?', crown '+bimDispNum(c.crown,2)+' m across':''));
    if(c.row)r+=bimPropText('Planted','in a row, a tree every '+BIM_CTX_TREE_STEP+' m');
    if(c.kind==='terrain'){
      r+=bimPropText('Zoom',String(c.zoom));
      if(c.datum!=null)r+=bimPropText('Datum','model y 0 is '+bimDispNum(c.datum,2)+' m above sea level');
    }
    for(k in c.tags)if(c.tags&&c.tags.hasOwnProperty(k)&&n<60){n++;r+=bimPropText(k,c.tags[k]);}
    return bimPropGroup('Context',r);
  }
  function bimCtxPropChange(ev){
    var f=ev.target&&ev.target.closest?ev.target.closest('[data-propctx]'):null;
    if(!f)return false;
    var k=f.getAttribute('data-propctx');
    bimCtxSet(k,(k.indexOf('kind:')===0||k==='onGround')?f.checked:f.value);   /* __acad3dV137 */
    return true;
  }
  function bimCtxPropClick(ev){
    var b=ev.target&&ev.target.closest?ev.target.closest('[data-propctxact]'):null;
    if(!b)return false;
    var a=b.getAttribute('data-propctxact');
    if(a==='get'){bimCtxFetch();return true;}
    if(a==='remove'){bimCtxRemove();return true;}
    if(a==='lodcheck'){bimLodCheck();return true;}       /* __acad3dV139 */
    if(a==='cjout'){bimCityJsonExport();return true;}
    if(a==='cjin'){bimCityJsonPick();return true;}
    return false;
  }
  /* ================= __acad3dV134: data layers in Properties ================= */
  function bimDataStatusText(L){
    var s=L.status;
    if(A3D_DATA.busy[L.id])return 'getting ...';
    if(!s)return 'not fetched yet';
    if(s.error)return s.error;
    return s.count+' feature'+(s.count===1?'':'s')+(s.more?' (more on the server)':'')+', '+s.date;
  }
  function bimDataModelHtml(){
    var L=bimDataList(),r='',i,o='';
    for(i=0;i<L.length;i++){
      var id=bimEsc(L[i].id);
      r+='<div class="a3d-prow a3d-uhead a3d-dlrow"><div class="a3d-plabel"><label class="a3d-ctxk"><input type="checkbox" data-propdata="vis:'+id+'"'+(L[i].visible?' checked':'')+
        ' aria-label="Show '+bimEsc(L[i].name)+'"> <input type="color" data-propdata="color:'+id+'" value="'+bimEsc(L[i].color)+'" aria-label="Colour"> '+bimEsc(L[i].name)+'</label></div>'+
        '<div class="a3d-pval"><span class="a3d-pstatic'+(L[i].status&&L[i].status.error?' a3d-uerr':'')+'">'+bimEsc(bimDataStatusText(L[i]))+'</span> '+
        '<button type="button" class="a3d-pedit" data-propdataact="refresh:'+id+'">Refresh</button> '+
        '<button type="button" class="a3d-bdel" data-propdataact="remove:'+id+'" title="Remove this data layer">\u00d7</button></div></div>';
      r+=bimDataLensRow(L[i]);   /* __acad3dV136 */
    }
    if(!L.length)r+=bimPropText('None yet','parcels, zoning or flood zones: add a preset or a web address');
    for(i=0;i<BIM_DATA_PRESETS.length;i++)o+='<option value="'+i+'">'+bimEsc(BIM_DATA_PRESETS[i].name)+'</option>';
    r+=bimPropRow('Preset','<select data-propdata="preset"><option value="">Add a preset ...</option>'+o+'</select>');
    r+=bimPropRow('Address','<div class="a3d-ukv"><input type="text" data-propdata="url" placeholder="ArcGIS .../FeatureServer/0, a WFS, or GeoJSON" spellcheck="false" aria-label="Data layer address">'+
      '<button type="button" class="a3d-pedit" data-propdataact="add">Add</button></div>');
    r+=bimPropText('Area','the site context radius, '+bimCtxSettings().radius+' m');
    r+=bimFindHtml();   /* __acad3dV135 */
    return r;
  }
  /* the feature clicked on the plan */
  function bimDataFeatureHtml(){
    var s=A3D_DATA.sel,L=s?bimDataById(s.layer):null,F=L?bimDataFeats(L.id)[s.fi]:null,r='',k,n=0,c;
    if(!F)return '';
    r+=bimPropText('Layer',L.name);
    r+=bimPropText('Source',L.credit);
    for(k in F.p)if(F.p.hasOwnProperty(k)&&n<60){n++;r+=bimPropText(k,F.p[k]===null?'':String(F.p[k]));}
    if(!n)r+=bimPropText('Attributes','none');
    c=bimDataModel(L);
    var f=null,i;
    if(c)for(i=0;i<c.feats.length;i++)if(c.feats[i].fi===s.fi)f=c.feats[i];
    if(f&&f.rings.length)r+=bimPropText('Area',bimDispNum(f.area,2)+' m\u00b2');
    r+=bimPropRow('',(f&&f.rings.length?'<button type="button" class="a3d-pedit" data-propdataact="toprop">Make Property Line</button> ':'')+
      '<button type="button" class="a3d-pedit" data-propdataact="clear">Close</button>');
    return bimPropGroup('Data Feature',r);
  }
  function bimDataPropChange(ev){
    var f=ev.target&&ev.target.closest?ev.target.closest('[data-propdata]'):null;
    if(!f)return false;
    var k=f.getAttribute('data-propdata'),b=k.split(':');
    if(k==='url')return true;   /* added by Add, never as it is typed */
    if(k==='preset'){
      var p=BIM_DATA_PRESETS[parseInt(f.value,10)];
      if(p)bimDataAdd(p.url,p.name,p.color,p.credit);
      return true;
    }
    if(b[0]==='vis')return bimDataSet(b[1],'visible',f.checked);
    if(b[0]==='color')return bimDataSet(b[1],'color',f.value);
    if(b[0]==='by')return bimDataSet(b[1],'by',f.value);             /* __acad3dV136 */
    if(b[0]==='opacity')return bimDataSet(b[1],'opacity',f.value);
    return false;
  }
  function bimDataPropClick(ev){
    var bt=ev.target&&ev.target.closest?ev.target.closest('[data-propdataact]'):null;
    if(!bt)return false;
    var a=bt.getAttribute('data-propdataact'),b=a.split(':');
    if(a==='add'){var u=el.propsbody.querySelector('[data-propdata="url"]');bimDataAdd(u?u.value:'');return true;}
    if(a==='toprop'){bimDataToProperty();return true;}
    if(a==='clear'){A3D_DATA.sel=null;refreshProps();paint();return true;}
    if(b[0]==='refresh'){bimDataFetch(b[1]);refreshProps();return true;}
    if(b[0]==='remove'){bimDataRemove(b[1]);return true;}
    return false;
  }
  /* ================= __acad3dV135: find open data, in Properties ================= */
  function bimFindHtml(){
    var P=bimFindCurrent(),o='<option value="">Pick a portal ...</option>',r='',g,i,G,it,k,pk,ad;
    for(g=0;g<BIM_DATA_PORTALS.length;g++){
      G=BIM_DATA_PORTALS[g];o+='<optgroup label="'+bimEsc(G[0])+'">';
      for(i=0;i<G[1].length;i++)o+='<option value="'+bimEsc(G[1][i][1])+'"'+(P&&P.host===G[1][i][1]?' selected':'')+'>'+bimEsc(G[1][i][0])+'</option>';
      o+='</optgroup>';
    }
    r+=bimPropRow('Find data','<select data-propfind="portal" aria-label="Open-data portal to search">'+o+'</select>');
    r+=bimPropRow('','<div class="a3d-ukv"><input type="text" data-propfind="q" value="'+bimEsc(A3D_FIND.q)+'" placeholder="parcels, zoning, trees ..." spellcheck="false" aria-label="Words to find">'+
      '<button type="button" class="a3d-pedit" data-propfindact="search"'+(A3D_FIND.busy?' disabled':'')+'>Search</button></div>');
    r+=bimPropRow('','<label class="a3d-ctxk"><input type="checkbox" data-propfind="near"'+(A3D_FIND.near?' checked':'')+'> Near the site only</label>');
    if(A3D_FIND.err)r+=bimPropRow('','<span class="a3d-pstatic a3d-uerr">'+bimEsc(A3D_FIND.err)+'</span>');
    else if(A3D_FIND.said)r+=bimPropRow('','<span class="a3d-pstatic">'+bimEsc(A3D_FIND.said)+'</span>');
    for(i=0;i<A3D_FIND.res.length;i++){
      it=A3D_FIND.res[i];ad=bimFindAdded(it);
      r+='<div class="a3d-fdrow"><div class="a3d-fdt"><a class="a3d-ctxlink" href="'+bimEsc(it.page)+'" target="_blank" rel="noopener noreferrer" title="'+bimEsc(it.snippet||it.title)+'">'+bimEsc(it.title)+'</a>'+
        '<span class="a3d-fdk">'+bimEsc(it.type+(it.owner?' - '+it.owner:''))+'</span></div>'+
        (ad?'<span class="a3d-fdk">added</span>':'<button type="button" class="a3d-pedit" data-propfindact="add:'+i+'">Add</button>')+'</div>';
      pk=A3D_FIND.pick;
      if(pk&&pk.ix===i)for(k=0;k<pk.layers.length;k++){
        var lu=String(it.url||'').split('?')[0].replace(/\/+$/,'')+'/'+pk.layers[k].id,had=false,L=bimDataList(),j;
        for(j=0;j<L.length;j++)if(L[j].url===lu)had=true;
        r+='<div class="a3d-fdrow a3d-fdsub"><div class="a3d-fdt">'+bimEsc(pk.layers[k].name)+'</div>'+
          (had?'<span class="a3d-fdk">added</span>':'<button type="button" class="a3d-pedit" data-propfindact="layer:'+i+':'+k+'">Add</button>')+'</div>';
      }
    }
    if(A3D_FIND.next&&!A3D_FIND.busy)r+=bimPropRow('','<button type="button" class="a3d-pedit" data-propfindact="more">More results</button>');
    r+=bimPropText('Portals',BIM_FIND_CREDIT);
    return r;
  }
  function bimFindPropChange(ev){
    var f=ev.target&&ev.target.closest?ev.target.closest('[data-propfind]'):null;
    if(!f)return false;
    var k=f.getAttribute('data-propfind');
    if(k==='q'){A3D_FIND.q=String(f.value||'').slice(0,120);return true;}   /* searched by Search, never as it is typed */
    if(k==='near'){A3D_FIND.near=!!f.checked;return true;}
    if(k==='portal'){bimFindSetPortal(f.value);refreshProps();return true;}
    return false;
  }
  function bimFindPropClick(ev){
    var bt=ev.target&&ev.target.closest?ev.target.closest('[data-propfindact]'):null;
    if(!bt)return false;
    var a=bt.getAttribute('data-propfindact'),b=a.split(':'),q;
    if(a==='search'){q=el.propsbody.querySelector('[data-propfind="q"]');bimFindSearch(q?q.value:'');return true;}
    if(a==='more'){bimFindSearch(null,true);return true;}
    if(b[0]==='add'){bimFindAdd(parseInt(b[1],10));return true;}
    if(b[0]==='layer'){
      var pk=A3D_FIND.pick,ix=parseInt(b[1],10),ly=pk&&pk.ix===ix?pk.layers[parseInt(b[2],10)]:null;
      if(ly)bimFindAdd(ix,ly);
      return true;
    }
    return false;
  }
  /* FINDDATA: the Data Layers group, at the search */
  function bimFindCommand(){
    bimDataCommand();
    var q=el.propsbody&&el.propsbody.querySelector('[data-propfind="q"]');
    if(q){try{q.focus();q.scrollIntoView({block:'center'});}catch(eF){}}
    a3dToast('Find data: pick a city, county, state or agency portal, type what you need, and Search');
    return true;
  }
  /* ================= __acad3dV136: the lens in Properties ================= */
  function bimLensHtml(){
    var st=bimLensSettings(),o='<option value=""'+(st.by?'':' selected')+'>Off</option>',i,r='',keys,k;
    for(i=0;i<BIM_LENS_BY.length;i++)o+='<option value="'+BIM_LENS_BY[i]+'"'+(st.by===BIM_LENS_BY[i]?' selected':'')+'>'+BIM_LENS_LABEL[BIM_LENS_BY[i]]+'</option>';
    r+=bimPropRow('Colour by','<select data-proplens="by" aria-label="Colour the model by">'+o+'</select>');
    if(st.by==='prop'){
      keys=bimLensPropKeys();
      if(st.prop&&keys.indexOf(st.prop)<0)keys.unshift(st.prop);
      o='<option value="">Pick a property ...</option>';
      for(k=0;k<keys.length;k++)o+='<option value="'+bimEsc(keys[k])+'"'+(keys[k]===st.prop?' selected':'')+'>'+bimEsc(keys[k])+'</option>';
      r+=bimPropRow('Property',keys.length?'<select data-proplens="prop" aria-label="Property to colour by">'+o+'</select>':
        '<span class="a3d-pstatic">no object carries one yet: get the site context, or import GeoJSON</span>');
    }
    return r;
  }
  function bimDataLensRow(L){
    var keys=bimDataAttrKeys(L.id),o='<option value="">Its colour</option>',k,id=bimEsc(L.id);
    if(!keys.length)return '';
    for(k=0;k<keys.length;k++)o+='<option value="'+bimEsc(keys[k])+'"'+(keys[k]===L.by?' selected':'')+'>'+bimEsc(keys[k])+'</option>';
    return '<div class="a3d-prow a3d-dllens"><div class="a3d-plabel">Colour by</div><div class="a3d-pval"><div class="a3d-ukv">'+
      '<select data-propdata="by:'+id+'" aria-label="Colour '+bimEsc(L.name)+' by">'+o+'</select>'+
      '<input type="number" min="10" max="100" step="10" data-propdata="opacity:'+id+'" value="'+Math.round(bimDataOpacity(L)*100)+'" aria-label="Opacity (%)" title="Opacity (%)"></div></div></div>';
  }
  function bimLensPropChange(ev){
    var f=ev.target&&ev.target.closest?ev.target.closest('[data-proplens]'):null;
    if(!f)return false;
    var k=f.getAttribute('data-proplens'),st=bimLensSettings();
    if(k==='by'){bimLensSet(f.value,f.value==='prop'?st.prop:'');return true;}
    if(k==='prop'){bimLensSet('prop',f.value);return true;}
    return false;
  }
  /* COLOURBY: the View group, at Colour by */
  function bimLensCommand(){
    A3D.sel=null;A3D.sel2=null;A3D.selSet=[];
    bimPropReveal('View');   /* __acad3dV141 */
    refreshTree();refreshProps();paint();
    var s=el.propsbody&&el.propsbody.querySelector('[data-proplens="by"]');
    if(s){try{s.focus();s.scrollIntoView({block:'center'});}catch(eF){}}
    a3dToast('Colour by is in the View group: usage, level, type, layer, material, height or any property, with a legend');
    return true;
  }
  /* ================= __acad3dV138: the survey check in Properties ================= */
  var BIM_SURVEY_MARK={pass:'\u2713',warn:'!',fail:'\u2717',none:'\u2013'};
  function bimSurveyCheckHtml(o){
    var r=bimSurveyCheck(o),h='',i,it,ctl;
    if(!r)return '';
    h+='<div class="a3d-prow"><div class="a3d-plabel">Verdict</div><div class="a3d-pval"><span class="a3d-svck a3d-svck-'+r.verdict+'">'+
      BIM_SURVEY_MARK[r.verdict]+' '+r.verdict.toUpperCase()+'</span></div></div>';
    for(i=0;i<r.items.length;i++){
      it=r.items[i];
      h+='<div class="a3d-prow a3d-svrow" data-svitem="'+it.key+'"><div class="a3d-plabel">'+bimEsc(it.label)+'</div><div class="a3d-pval">'+
        '<span class="a3d-svck a3d-svck-'+it.status+'">'+BIM_SURVEY_MARK[it.status]+'</span> <span class="a3d-pstatic">'+bimEsc(it.text)+'</span></div></div>';
    }
    ctl=(o.control||[]).map(function(c){return c.p+'='+c.z;}).join(', ');
    h+=bimPropRow('Control','<input type="text" data-propsurvey="control" value="'+bimEsc(ctl)+'" placeholder="105=30.000, 201=28.45" spellcheck="false" '+
      'title="Points whose elevation you know, in the survey\u2019s units">');
    h+=bimPropRow('','<button type="button" class="a3d-pedit" data-propsurveyact="export">Export Report</button>');
    return h;
  }
  function bimSurveyPropChange(ev){
    var f=ev.target&&ev.target.closest?ev.target.closest('[data-propsurvey]'):null;
    if(!f)return false;
    var o=objById(A3D.sel);
    if(f.getAttribute('data-propsurvey')==='control'&&o)bimSurveySetControl(o,f.value);
    return true;
  }
  function bimSurveyPropClick(ev){
    var b=ev.target&&ev.target.closest?ev.target.closest('[data-propsurveyact]'):null;
    if(!b)return false;
    var o=objById(A3D.sel);
    if(b.getAttribute('data-propsurveyact')==='export'&&o)bimSurveyReportExport(o);
    return true;
  }
  /* SURVEYCHECK: the selected surface, or the first */
  function bimSurveyCheckCommand(){
    var o=objById(A3D.sel),i;
    if(!o||o.t!=='terrain'){o=null;for(i=0;i<A3D.objs.length;i++)if(A3D.objs[i].t==='terrain'&&A3D.objs[i].survey){o=A3D.objs[i];break;}}
    if(!o){a3dToast('There is no surface to check: make one with SURVEY');return null;}
    A3D.sel=o.id;A3D.sel2=null;A3D.selSet=[o.id];
    A3D_PROP_GROUPS_OPEN['Survey Check']=true;
    refreshTree();refreshProps();paint();
    var g=el.propsbody&&el.propsbody.querySelector('[data-a3dpgrp="Survey Check"]');
    if(g){try{g.scrollIntoView({block:'start'});}catch(eS){}}
    var r=bimSurveyCheck(o),bad=r.items.filter(function(x){return x.status==='fail'||x.status==='warn';}).map(function(x){return x.label.toLowerCase();});
    a3dToast(o.name+': '+r.verdict.toUpperCase()+(bad.length?' - see '+bad.join(', '):' - every check passed'));
    return r;
  }
  /* DATALAYERS: the group, with nothing selected */
  function bimDataCommand(){
    A3D.sel=null;A3D.sel2=null;A3D.selSet=[];
    bimPropReveal('Data Layers');   /* __acad3dV141: on the Site tab */
    refreshTree();refreshProps();paint();
    var g=el.propsbody&&el.propsbody.querySelector('[data-a3dpgrp="Data Layers"]');
    if(g){try{g.scrollIntoView({block:'start'});}catch(eS){}}
    a3dToast('Data layers are in Properties: add a preset, or the web address of an ArcGIS layer, a WFS or a GeoJSON file');
    return true;
  }
