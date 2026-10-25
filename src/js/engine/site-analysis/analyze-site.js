  /* ================= __acad3dV164: Analyze site =================
     The owner: "all i want is button then the analysis run, then it leverage appropriate relevant
     data from target api to analyze the site, then put that under analysis layers". One button,
     needing only the site's place -- its latitude and longitude, or an address found on the map. It
     fetches what the place lets the app fetch, each from its free source: the context (OpenStreetMap,
     AWS Terrain Tiles), and after it the access and people (OpenStreetMap, the US Census), so the
     public Overpass servers are asked one thing at a time; the climate (Open-Meteo, CAMS, USGS) beside
     them, with the time zone; the zoning where a council's layer is loaded. Then every analysis is
     drawn. Each source is listed as it arrives, or with its reason when it fails, and what failed
     leaves the rest standing. One undo step: the snapshot taken as it starts -- or, when the address
     is found first, the one placing the site takes -- and every step after it held. An address not
     found leaves none. */
  var A3D_SITERUN={busy:false,steps:[]};
  var BIM_SITERUN_RADIUS=300;   /* far enough for the views; the noise needs CRTN's range, the registry's */
  function bimSiteRunRadius(){return Math.max(BIM_SITERUN_RADIUS,Math.ceil(bimDgCrtnMax()||0));}   /* __acad3dV167h */
  var BIM_SITERUN_STEPS=[['place','The site'],['context','Context'],['land','Ground and water'],['climate','Climate and time zone'],['access','Access and people'],['zoning','Zoning'],['draw','The analyses, in the model']];
  var BIM_SITERUN_WORD={wait:'Waiting',busy:'Running',ok:'Done',part:'Partly',fail:'Failed',skip:'Skipped'};
  var BIM_SITERUN_CLS={wait:'s-wait',busy:'s-busy',ok:'s-ok',part:'s-part',fail:'s-fail',skip:'s-skip'};
  function bimSiteStep(id,state,text){
    var s=A3D_SITERUN.steps,i;
    for(i=0;i<s.length;i++)if(s[i].id===id){s[i].state=state;s[i].text=String(text==null?'':text).slice(0,400);}
    bimAnalyzeRefresh(true);
  }
  /* why a fetch would not start: it says so in the message it shows */
  function bimSiteToastText(){var t=document.getElementById('a3d-toast'),L=t?String(t.textContent||'').split('\n'):[];return L.length?L[L.length-1]:'';}
  function bimSitePlaceText(){
    var st=bimSunSettings(),at=Math.abs(st.lat).toFixed(5)+'\u00b0 '+(st.lat<0?'S':'N')+', '+Math.abs(st.lon).toFixed(5)+'\u00b0 '+(st.lon<0?'W':'E');
    return A3D.site&&A3D.site.address?String(A3D.site.address).slice(0,140)+' ('+at+')':at;
  }
  function bimSiteAddrFocus(){
    bimAnzView();
    var i=document.querySelector('.a3d-analyze-wrap [data-saaddr]');
    if(i){try{i.focus();}catch(eF){}}
  }
  function bimSiteAnalyze(q){
    if(A3D_SITERUN.busy){a3dToast('Analyze site is already running');return null;}
    var st=bimSunSettings(),placed=bimSunNum(st.lat)&&bimSunNum(st.lon),R;
    q=String(q==null?'':q).replace(/^\s+|\s+$/g,'');
    if(!placed&&!q){a3dToast('Where is the site? Type its address, or give its latitude and longitude in Properties, Site, Location');bimSiteAddrFocus();return null;}
    if(typeof fetch!=='function'){a3dToast('This browser cannot fetch: Analyze site gets its data from the web');return null;}
    R=A3D_SITERUN={busy:true,t0:Date.now(),held:false,steps:BIM_SITERUN_STEPS.map(function(s){return {id:s[0],name:s[1],state:'wait',text:''};})};
    function hold(){if(!R.held){R.held=true;bimUndoHold=true;}}
    if(placed){pushUndo();hold();}
    function finish(ok){
      if(R.held)bimUndoHold=false;
      R.busy=false;
      var D=bimDgState();
      D.last={date:bimSaToday(),ok:!!ok,steps:R.steps.map(function(s){return {id:s.id,name:s.name,state:s.state,text:s.text};})};
      refreshTree();refreshLayers();refreshProps();paint();saveSoon();
      bimAnalyzeRefresh(true);
      return {ok:!!ok,steps:D.last.steps};
    }
    bimSiteStep('place','busy',placed?'':'Finding '+q+' ...');
    var p0=placed?Promise.resolve({found:true}):(bimMapFind(q)||Promise.resolve({found:false,error:bimSiteToastText()}));
    return p0.then(function(f){
      if(!f||!f.found){
        bimSiteStep('place','fail',f&&f.error?f.error:'Nothing found for '+q+': try the street and the town, or give the latitude and longitude in Location');
        a3dToast('Analyze site: the site could not be found');
        return finish(false);
      }
      hold();   /* placing the site took the snapshot */
      bimSiteStep('place','ok',bimSitePlaceText());
      var cs=bimCtxSettings(),wid='';
      if(cs.radius<bimSiteRunRadius()){A3D.site.context=A3D.site.context||{};A3D.site.context.radius=bimSiteRunRadius();wid='; the context radius is '+bimSiteRunRadius()+' m now (it was '+cs.radius+' m), for the noise and the views';}
      bimSiteStep('context','busy','Buildings, roads, water, green, trees, land use and terrain, '+Math.max(cs.radius,bimSiteRunRadius())+' m around ...');
      bimSiteStep('climate','busy','Ten years of days, a year of hours, air quality, earthquakes ...');
      var pk=bimSiteOne('climate',bimClimFetch(),function(r){
        var got=[];
        if(r.climate)got.push('ten years of climate');if(r.hourly)got.push('a year of hourly wind and heat');if(r.air)got.push('air quality');
        if(r.quakes!==null&&r.quakes!==undefined)got.push(bimSaN(r.quakes,'earthquake')+' within 100 km');
        if(r.tz!==null&&r.tz!==undefined)got.push('UTC'+(r.tz>=0?'+':'\u2212')+bimDispNum(Math.abs(r.tz),2)+(r.tzSet?'':' (the offset already given is kept)'));
        return [bimSiteState(got.length,r.errors),got.join(', ')+(r.errors&&r.errors.length?'. Not available: '+r.errors.join('; '):'')];
      });
      /* __acad3dV165: the ground every 5 m and FEMA's zones, from AWS and FEMA: beside the context, not after it */
      bimSiteStep('land','busy','The ground every '+BIM_LAND_CELL+' m for '+BIM_LAND_HALF+' m around, and the flood zones ...');
      var pl=bimSiteOne('land',bimLandFetch(),function(r){
        var got=[];
        if(r.dem)got.push('the ground every '+r.dem.cell+' m for '+BIM_LAND_HALF+' m around');
        if(r.flood&&r.flood.outside)got.push('FEMA maps US sites only');
        else if(r.flood&&r.flood.features)got.push(r.flood.features.length?bimSaN(r.flood.features.length,'flood zone')+' from FEMA':'no flood zone mapped within '+BIM_LAND_HALF+' m');
        return [bimSiteState(got.length,r.errors),got.join(', ')+(r.errors&&r.errors.length?'. Not available: '+r.errors.join('; '):'')];
      });
      var pc=bimSiteOne('context',bimCtxFetch(),function(r){
        return [bimSiteState(r.counts?1:0,r.errors),r.counts?bimCtxCountsText(r.counts)+wid+(r.errors&&r.errors.length?'. Not available: '+r.errors.join('; '):''):'nothing came back'];
      }).then(function(){
        bimSiteStep('access','busy','Walk times to daily needs and transit, the streets, the census tract ...');
        return bimSiteOne('access',bimAccFetch(),function(r){
          var got=[];
          if(r.access)got.push('walk times, '+bimSaN(r.stops||0,'transit stop'));if(r.people)got.push('the census tract');if(r.outside)got.push('the census covers US sites only');
          return [bimSiteState(got.length,r.errors),got.join(', ')+(r.errors&&r.errors.length?'. Not available: '+r.errors.join('; '):'')];
        });
      });
      return Promise.all([pc,pk,pl]).then(function(){return bimZnDrawingFetch();}).then(function(){   /* __acad3dV168: a council layer's own colours, once */
        bimSiteZoning();
        bimSiteStep('draw','busy','');
        var out=bimDgRunAll(),said=[],notes=[],n=0,bad;
        BIM_DG_AN.forEach(function(A){var r=out[A.id];if(!r)return;if(r.error)notes.push(A.name+': '+r.error);else if(r.total){n+=r.total;said.push(A.name.toLowerCase()+' '+r.total);}else if(r.note)notes.push(A.name+': '+r.note);});
        bimSaFill(true);
        bimSiteStep('draw',n?'ok':'fail',(n?bimSaN(n,'element')+' on Layers, Site analysis: '+said.join(', '):'Nothing to draw')+(notes.length?'. '+notes.join('. '):''));
        bad=R.steps.filter(function(s){return s.state==='fail';}).map(function(s){return s.name;});
        var res=finish(true);
        a3dToast('Analyze site: '+(n?bimSaN(n,'element')+' drawn in the model, on Layers, Site analysis':'nothing could be drawn')+'; one undo step'+(bad.length?'. Not available: '+bad.join(', '):''));
        return res;
      });
    }).then(null,function(e){
      console.warn('[BIM] Analyze site',e);
      a3dToast('Analyze site stopped - see the console');
      R.steps.forEach(function(s){if(s.state==='busy'||s.state==='wait'){s.state='fail';s.text='Stopped: '+String(e&&e.message||e).slice(0,160);}});
      return finish(false);
    });
  }
  /* what came back: all of it, part of it (some sources down, named), or none */
  function bimSiteState(got,errors){return !got?'fail':(errors&&errors.length?'part':'ok');}
  /* one fetch, its step marked by what came back; a fetch that would not start says why */
  function bimSiteOne(id,p,read){
    if(!p){bimSiteStep(id,'fail',bimSiteToastText()||'It did not start');return Promise.resolve(null);}
    return p.then(function(r){
      var v;
      try{v=r&&!r.error?read(r):['fail',(r&&r.error)||'nothing came back'];}
      catch(eR){console.warn('[BIM] Analyze site: '+id,eR);v=['fail','It could not be read - see the console'];}
      bimSiteStep(id,v[0],v[1]);
      return r;
    },function(e){bimSiteStep(id,'fail',String(e&&e.message||e).slice(0,200));return null;});
  }
  /* __acad3dV168: an ArcGIS layer's own colours, read once from its description (?f=json) and kept with
     it; a failure named, its districts then drawn in the app's colours */
  function bimZnDrawingFetch(){
    var L=bimDataList().filter(function(x){return x&&x.kind==='arcgis'&&!x.drawing;}).slice(0,3);
    if(!L.length||typeof fetch!=='function')return Promise.resolve(0);
    return Promise.all(L.map(function(x){
      var u=String(x.url).replace(/\/?(\?.*)?$/,'')+'?f=json',done=false;
      return new Promise(function(res){
        function fail(e){
          if(done)return;
          done=true;clearTimeout(tm);
          console.warn('[BIM] The colours of '+x.name+' could not be read',e);
          a3dToast(x.name+': its own colours could not be read ('+bimCtxErr(bimMapHost(u),e)+'); its districts are drawn in the app\'s');
          res(0);
        }
        var tm=setTimeout(function(){fail({timeout:true});},15000);
        try{
          fetch(u).then(function(r){if(!r.ok)throw {http:r.status};return r.text();}).then(function(tx){
            if(done)return;
            var js;
            try{js=JSON.parse(tx);}catch(eJ){throw {bad:true};}
            done=true;clearTimeout(tm);
            x.drawing=bimZnDrawing(js);
            res(1);
          }).then(null,fail);
        }catch(eF){fail(eF);}
      });
    })).then(function(r){return r.reduce(function(a,b){return a+b;},0);});
  }
  /* the zoning, where a council's layer loaded in Data Layers covers the property */
  function bimSiteZoning(){
    var DL=bimDataList(),f=null;
    if(!bimZnProperty()){bimSiteStep('zoning','skip','Needs the property line: draw it from a shape or from its bearings');return;}
    if(!DL.length){bimSiteStep('zoning','skip','No council layer loaded: add one in Properties, Site, Data Layers, and its zoning is read here');return;}
    try{f=bimZnFromLayer(false);}catch(eZ){console.warn('[BIM] Analyze site: zoning',eZ);}
    if(!f){bimSiteStep('zoning','skip','None of the '+bimSaN(DL.length,'loaded layer')+' gives the zoning at the property');return;}
    try{bimZnFromLayer(true);}catch(eZ2){console.warn('[BIM] Analyze site: zoning',eZ2);bimSiteStep('zoning','fail','It could not be read - see the console');return;}
    bimSiteStep('zoning','ok',bimZnFoundText(f)+' (from '+(f.district||f.far||f.height).layer+')');
  }
  /* the top of Analyze: where the site is, the button, and what the last run brought */
  function bimSiteRunHtml(){
    var st=bimSunSettings(),placed=bimSunNum(st.lat)&&bimSunNum(st.lon),D=bimDgState(),R=A3D_SITERUN,P=A3D.objs.filter(bimIsProperty),bd,h,steps;
    if(P.length){var g=bimPropertyGeometry(P[0]);bd=bimEsc(P[0].name)+', '+bimDispNum(g.area,1)+' m\u00b2';}
    else bd='None yet <button type="button" class="a3d-anzbtn" data-saact="cmd:propertyshape">From a shape</button> <button type="button" class="a3d-anzbtn" data-saact="cmd:propertyline">From bearings</button>';
    h='<div class="a3d-sasec a3d-sarun" data-anzsec="site"><div class="a3d-sasechd">Site</div>'+
      '<div class="a3d-sarow"><span class="a3d-salab">Place</span><span class="a3d-saval">'+(placed?bimEsc(bimSitePlaceText()):'Not placed yet')+'</span></div>';
    if(!placed)h+='<div class="a3d-sarow"><label for="a3d-saaddr">Address</label><input type="text" id="a3d-saaddr" data-saaddr="1" maxlength="200" enterkeyhint="search" autocomplete="off" placeholder="A street address or a place"></div>';
    h+='<div class="a3d-sarow"><span class="a3d-salab">Boundary</span><span class="a3d-saval">'+bd+'</span></div>'+
      '<div class="a3d-saacts"><button type="button" class="a3d-anzbtn pri a3d-sago" data-saact="analyze"'+(R.busy?' disabled':'')+'>'+(R.busy?'Analyzing ...':(D.last?'Analyze site again':'Analyze site'))+'</button>'+
      (D.last?'<button type="button" class="a3d-anzbtn" data-saact="dglegend" aria-pressed="'+(!D.legendOff)+'">'+(D.legendOff?'Show the legend':'Hide the legend')+'</button>':'')+'</div>'+
      '<div class="a3d-sacap">'+(D.last&&!R.busy?bimEsc('Last run '+D.last.date+'. Each analysis is on Layers, Site analysis: select an element to move, restyle or relabel it; what you change is kept when it runs again.'):
        'Gets what is around the site from free open data -- buildings, roads, terrain, climate, access, zoning -- and draws each analysis in the model, on Layers, Site analysis. One undo step.')+'</div>';
    steps=R.steps.length?R.steps:((D.last&&D.last.steps)||[]);
    if(steps.length)h+='<ol class="a3d-sasteps" data-sasteps="1">'+steps.map(function(s){
      return '<li class="a3d-sastep '+(BIM_SITERUN_CLS[s.state]||'s-wait')+'" data-sastep="'+bimEsc(s.id)+'"><span class="a3d-sastepic" aria-hidden="true"></span><span class="a3d-sastepn">'+bimEsc(s.name)+'</span>'+
        '<span class="a3d-sastepst">'+bimEsc(BIM_SITERUN_WORD[s.state]||s.state)+'</span>'+(s.text?'<span class="a3d-sastept">'+bimEsc(s.text)+'</span>':'')+'</li>';}).join('')+'</ol>';
    return h+'</div>';
  }
  /* ---- each analysis drawn in the model, a row in its category ---- */
  var BIM_DG_KEYCLS={fill:'k-fill',line:'k-line',dash:'k-dash',dot:'k-dot'};
  function bimDgLegendHtml(rows){
    if(!rows||!rows.length)return '';
    return '<div class="a3d-dgleg">'+rows.map(function(r){
      var st=(r.kind==='line'||r.kind==='dash')?'color:'+r.col:'background:'+r.col;
      if(r.tex)st+=';'+bimDgTexCss(r.tex,r.ink);   /* __acad3dV168 */
      return '<span class="a3d-dglegi"><i class="'+(BIM_DG_KEYCLS[r.kind]||'k-fill')+'" style="'+bimEsc(st)+'"></i>'+bimEsc(r.name)+'</span>';}).join('')+'</div>';
  }
  function bimDgCards(){
    var D=bimDgState();
    return BIM_DG_AN.map(function(A){
      var R=D.runs[A.id],L=bimDgDiags(A.id),ly=bimLayerById(D.layers[A.id]),on=!!(ly&&bimLayerEff(ly).on),ed=L.filter(bimDgEdited).length;
      var st=!R?'Not run yet: Analyze site draws it':(L.length?bimSaN(L.length,'element')+' on Site analysis - '+A.name+(ed?', '+ed+' changed by you':'')+', '+R.date:(R.note||'Nothing to draw'));
      /* __acad3dV167: Out of date when a standard it used changed: an edition, a value, an override */
      var SC=R?bimDgStdChanged(A.id):{run:[],data:[]},stale=!!(SC.run.length||SC.data.length),sx=bimDgStdText(A.id);
      if(stale)st+='. Out of date: '+(SC.run.length?bimStdChangedText(SC.run)+' since it ran: Run again':'')+(SC.run.length&&SC.data.length?'; ':'')+(SC.data.length?bimStdChangedText(SC.data)+' since '+BIM_STD_DATA[SC.kind].name+' was fetched: Analyze site again':'');
      return {id:'dg'+A.id,title:A.name,state:!R?null:(stale?'stale':(L.length?(on?'on':'off'):'warn')),status:st,
        extra:R?bimDgLegendHtml(R.legend)+(R.note&&L.length?'<div class="a3d-sacap">'+bimEsc(R.note)+'</div>':'')+(R.source?'<div class="a3d-sacap">Source: '+bimEsc(R.source)+'</div>':'')+
          (sx?'<div class="a3d-sacap a3d-sastd" data-dgstd="'+A.id+'">'+bimEsc(sx)+'</div>':''):'',
        acts:[{act:'dg:show:'+A.id,label:on?'Hide':'Show',pri:!on&&L.length>0,off:L.length?'':'Nothing drawn yet'},
          {act:'dg:run:'+A.id,label:R?'Run again':'Run',tip:'From what the project holds now; Analyze site fetches the data again'},
          {act:'dg:select:'+A.id,label:'Select',off:L.length?'':'Nothing drawn yet'},
          {act:'dg:reset:'+A.id,label:'Reset',off:R?'':'Not run yet',tip:'As the analysis draws it: what you changed, copied or deleted on it goes back'}]};
    });
  }
  function bimDgAct(v){
    v=String(v||'');
    var i=v.indexOf(':'),c=v.slice(0,i),a=v.slice(i+1),D=bimDgState(),L,ly;
    if(i<0||!bimDgAn(a))return false;
    if(c==='run')return !!bimDgRunAll(a);
    if(c==='reset')return !!bimDgResetAnalysis(a);
    L=bimDgDiags(a);
    if(c==='select'){
      if(!L.length)return false;
      A3D.selSet=L.map(function(o){return o.id;});A3D.sel=A3D.selSet[0];A3D.sel2=null;
      refreshTree();refreshProps();paint();
      return true;
    }
    if(c==='show'){
      ly=bimLayerById(D.layers[a]);
      if(!ly)return false;
      if(bimLayerEff(ly).on)bimLayerSet(ly.id,'visible',false);
      else bimLayerChain(ly).forEach(function(x){if(x.visible===false)bimLayerSet(x.id,'visible',true);});   /* the layer and those above it */
      paint();
      return true;
    }
    return false;
  }
