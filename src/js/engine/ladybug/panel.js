  /* ================= __acad3dV172b: Ladybug in the analysis workspace =================
     Climate's rows, as V171b's cards are: the weather Ladybug reads, then its four analyses. A row's panel says what it
     is and what it found, in numbers, with its buttons: open a weather file or get a year of hours, Run (or Run all
     four), Show on the board, and Add to a board -- any board in the set, or a new one (V172b's editable boards). */
  BIM_ANZ_GROUP_OF.lbweather='climate';BIM_ANZ_GROUP_OF.lbutci='climate';BIM_ANZ_GROUP_OF.lbpsych='climate';
  BIM_ANZ_GROUP_OF.lbwind='climate';BIM_ANZ_GROUP_OF.lbdd='climate';
  var BIM_LB_ROW={utci:'Outdoor comfort, UTCI (Ladybug)',psych:'Psychrometric chart and strategies (Ladybug)',wind:'Wind rose, weather file (Ladybug)',dd:'Design days (Ladybug)'};
  var BIM_LB_FIG={utci:'lb.utci',psych:'lb.psych',wind:'lb.wind',dd:'lb.dd'};
  function bimLbRows(R){return '<div class="a3d-awp-rows">'+R.map(function(r){return '<div class="a3d-awp-r"><span>'+bimEsc(r[0])+'</span><b>'+bimEsc(r[1])+'</b></div>';}).join('')+'</div>';}
  function bimLbNote(t,cls){return '<p class="a3d-awp-note'+(cls?' '+cls:'')+'">'+bimEsc(t)+'</p>';}
  /* the prevailing direction of a wind result: the fullest of its sectors */
  function bimLbWindPrev(Wr){
    var best=-1,k=0,i,j,t;
    for(i=0;i<(Wr.sectors||[]).length;i++){t=0;for(j=0;j<Wr.sectors[i].length;j++)t+=Wr.sectors[i][j];if(t>best){best=t;k=i;}}
    return BIM_CLIM_DIRS[k]||'';
  }
  /* a result in one line: a row's status */
  function bimLbSummary(k,R){
    var r=R.r,C,h,c;
    if(k==='utci'){C=r.conditions||{};return ['sun_wind','shade_wind'].filter(function(x){return C[x];}).map(function(x,i){return bimClimFmt(C[x].comfort,0)+'%'+(i?'':' of hours without thermal stress')+' '+BIM_LB_COND[x].toLowerCase();}).join('; ');}
    if(k==='psych')return bimClimFmt(r.pct[0],0)+'% of hours comfortable indoors as the weather is; '+bimClimFmt(r.total,0)+'% with the '+(r.names.length-1)+' passive strategies';
    if(k==='wind')return 'From the '+bimLbWindPrev(r)+' most often, '+bimClimFmt(r.mean,1)+' m/s on average; calm '+bimClimFmt(r.calm_pct,0)+'% of hours';
    h=r.heating;c=r.cooling;
    return (h?'Heating '+bimClimFmt(h.db,1)+' °C':'')+(h&&c?'; ':'')+(c?'cooling '+bimClimFmt(c.db,1)+' °C with '+bimClimFmt(c.hum,1)+' °C '+(c.hum_type==='Wetbulb'?'wet bulb':String(c.hum_type).toLowerCase()):'');
  }
  /* the weather's panel: where the hours come from, and the runtime */
  function bimLbWeatherHtml(s){
    var r=[],L=A3D_LB,v=L.versions||{};
    if(s){
      r.push(['Source',s.kind==='openmeteo'?'Open-Meteo ERA5, '+s.year+(s.half?' (in UTC: a half-hour time zone)':''):s.name]);
      r.push(['Place',(s.city||s.name||'')+(s.station?' ('+s.station+')':'')+', '+bimClimFmt(s.lat,4)+', '+bimClimFmt(s.lon,4)]);
      if(typeof s.elev==='number')r.push(['Elevation',bimClimFmt(s.elev,0)+' m']);
      r.push(['Hours',bimClimInt(s.hours||0)+(s.leap?', a leap year':'')+(s.filled?'; '+s.filled+' filled between their neighbours':'')]);
      r.push(['Design days',s.ddy?'From the station\'s DDY (ASHRAE)':(s.design_read?'From the file\'s design conditions':'Approximated from this one year')]);
      r.push(['Opened',s.at||'']);
    }
    r.push(['Ladybug',L.st==='ready'?'ladybug-core '+(v['ladybug-core']||'')+', ladybug-comfort '+(v['ladybug-comfort']||'')+', in Pyodide '+L.pyodide:(L.st==='loading'?'Loading (about 13 MB, once)':(L.st==='failed'?'Could not start: '+L.err:'Loads when an analysis first runs (about 13 MB, once)'))]);
    return bimLbRows(r)+
      bimLbNote((s&&s.kind==='file'?'A weather file is read in this browser and not uploaded; it is not kept with the project, so after a reload Run asks for it again. ':'')+
        'Ladybug Tools\' own code (AGPL-3.0), unchanged, runs here through Pyodide; a station\'s weather files are at climate.onebuilding.org (its ZIP holds the EPW and the DDY).');
  }
  /* a result's panel: its numbers, the standards it used, and whether it is out of date */
  function bimLbResultHtml(k,R,ch){
    if(!R)return '';
    var r=R.r,P=R.params||{},h='',rows=[],C,x;
    if(k==='utci'){
      C=r.conditions||{};
      ['sun_wind','shade_wind','sun_still','shade_still'].forEach(function(c){
        if(C[c])rows.push([BIM_LB_COND[c],bimClimFmt(C[c].comfort,0)+'% no stress, '+bimClimFmt(C[c].heat,0)+'% heat, '+bimClimFmt(C[c].cold,0)+'% cold']);});
      x=C.sun_wind||C.shade_wind;
      if(x&&x.outside)rows.push(['Outside the formula\'s range',bimClimInt(x.outside)+' hours, its extrapolation']);
      h=bimLbRows(rows)+bimLbNote('Still air: '+bimStdFmt(r.still!==undefined?r.still:P.still,'m/s')+'. '+bimStdUsedText('utci')+'.','a3d-awp-std');
    }else if(k==='psych'){
      r.names.forEach(function(n,i){rows.push([n,bimClimFmt(r.pct[i],1)+'%']);});
      rows.push(['With any of them',bimClimFmt(r.total,1)+'%']);
      h=bimLbRows(rows)+bimLbNote('Clothing '+r.clo.join(' and ')+' clo at '+r.met[0]+' met; PPD '+bimStdFmt(r.ppd!==undefined?r.ppd:bimStd('ashrae.55','ppd'),'%')+' or less; still air '+bimStdFmt(r.still!==undefined?r.still:bimStd('ashrae.55','still'),'m/s')+'. '+
        bimStdUsedText('ashrae.55')+'; '+bimStdUsedText('app.comfort')+'.','a3d-awp-std')+((r.notes&&r.notes.length)?bimLbNote(r.notes.join('; ')+'.'):'');
    }else if(k==='wind'){
      rows.push(['Prevailing',bimLbWindPrev(r)],['Mean speed',bimClimFmt(r.mean,1)+' m/s'],['Calm (a speed of 0)',bimClimFmt(r.calm_pct,1)+'% of hours'],['Hours',bimClimInt(r.hours)]);
      h=bimLbRows(rows)+bimLbNote(bimStdUsedText('app.climate')+'.','a3d-awp-std');
    }else{
      ['heating','heating99','cooling','cooling1','cooling2'].forEach(function(q){var d=r[q];if(d)rows.push([d.name.replace(/^.*?Ann /,''),bimClimFmt(d.db,1)+' °C'+(q.indexOf('cooling')===0?', '+d.hum_type+' '+bimClimFmt(d.hum,1):'')]);});
      h=bimLbRows(rows)+bimLbNote(bimStdUsedText('ashrae.dd')+'.','a3d-awp-std');
    }
    if(R.stale)h+=bimLbNote('Worked out from other weather than the project names now: Run again.','a3d-awp-stale');
    if(ch&&ch.length)h+=bimLbNote(bimStdChangedText(ch)+' since it was run: Run again.','a3d-awp-stale');
    return h+bimLbNote('Run '+R.at+(R.ms?', in '+bimClimFmt(R.ms/1000,1)+' s':'')+'.');
  }
  /* the rows: Climate's, after its own */
  function bimLbCards(){
    var C=[],src=bimLbSrcKept(),busy=A3D_LBRUN.busy,off=src?(busy?'Running: '+BIM_LB_NAMES[busy]:''):'Choose the weather first: open a weather file, or get a year of hours';
    C.push({id:'lbweather',title:'Weather for Ladybug',state:A3D_LB.st==='loading'?'busy':(src?'on':null),
      status:src?'Weather: '+bimLbSrcWords(src)+'.':'No weather yet: open an EPW, or a station\'s ZIP with its design days, or get a year of hours from Open-Meteo.',
      extra:bimLbWeatherHtml(src),
      acts:[{act:'lb:open',label:'Open a weather file',pri:!src,tip:'An EPW, or the station\'s ZIP from climate.onebuilding.org'},
        {act:'lb:year',label:'Get a year of hours',tip:'Open-Meteo ERA5, the last full year, at the site, in its standard time'},
        {act:'lb:runall',label:'Run all four',pri:!!src,off:off}]});
    BIM_LB_KINDS.forEach(function(k){
      var R=bimLbResult(k),ch=R?bimLbStdChanged(k):[];
      C.push({id:'lb'+k,title:BIM_LB_ROW[k],state:busy===k?'busy':(R?((R.stale||ch.length)?'stale':'on'):'off'),
        status:R?bimLbSummary(k,R):(src?'Not run yet: Run works it out from '+bimLbSrcWords(src)+'.':'Choose the weather first, in Weather for Ladybug.'),
        extra:bimLbResultHtml(k,R,ch),
        acts:[{act:'lb:run:'+k,label:R?'Run again':'Run',pri:!R,off:off},
          {act:'lb:show:'+k,label:'Show on the board',off:R?'':'Run it first'},
          {act:'lb:to:'+k,label:'Add to a board',off:R?'':'Run it first'}]});
    });
    return C;
  }
  /* Analyze and the open board, after the weather or a result changed */
  function bimLbRefresh(){
    try{if(A3D_AW.on)bimAwRefresh();else bimAnalyzeRefresh();}catch(eA){console.warn('[BIM] Analyze could not show Ladybug\'s rows again',eA);}
    if(A3D_CLB.open){try{bimClbRefresh();}catch(eB){console.warn('[BIM] The board could not be drawn again',eB);}}
  }
  /* a Ladybug figure onto a board: one in the set, or a new one with it */
  function bimLbAddTo(k,id){
    var f=BIM_LB_FIG[k],B,ctx,P,F;
    if(!f||!bimLbResult(k)){a3dToast('Run it first');return false;}
    if(id==='new'){
      ctx={edit:false,narrow:false,caps:{},no:0};P=bimFigSrc(ctx,f,null);
      F={k:'',f:f,x:0,y:0,w:bimFigSpan(P),h:1};F.h=bimBrdNatH(F,F.w);
      return !!bimBrdNewUi(BIM_LB_NAMES[k],[F]);
    }
    B=bimBoardById(id);
    if(!B&&id==='board-climate'){bimBoardShow('climate');return true;}
    if(!B){a3dToast('That board is no longer in the set');return false;}
    bimShellSetTab('presentation');
    if(!bimPresOpenBoard(id))return false;
    if(B.kind==='climate'&&!B.figs){a3dToast(BIM_LB_NAMES[k]+' is on this board already, after its own figures');return true;}
    if(B.figs&&B.figs.some(function(x){return x.f===f;})){a3dToast(BIM_LB_NAMES[k]+' is on this board already');return true;}
    return !!bimBrdAddFig(f);
  }
  function bimLbToBoard(k){
    var b=document.querySelector('.a3d-awp [data-anzact="lb:to:'+k+'"]')||document.querySelector('[data-anzact="lb:to:'+k+'"]'),r=b?b.getBoundingClientRect():{left:80,bottom:80};
    var it=bimPresData().boards.map(function(B){return [bimBoardLabel(B),B.id];});
    if(!bimBoardById('board-climate'))it.unshift([bimBoardName('climate')+', into the set','board-climate']);
    it.push('-',['A new board','new']);
    bimLtMenuOpen(r.left,r.bottom+4,it,function(id){bimLbAddTo(k,id);});
    return true;
  }
  /* the rows' buttons (bimAnzAct): lb:open, lb:year, lb:runall, lb:run:<kind>, lb:show:<kind>, lb:to:<kind> */
  function bimLbAct(a){
    var i=a.indexOf(':'),c=i<0?a:a.slice(0,i),k=i<0?'':a.slice(i+1);
    function fail(what){return function(e){console.warn('[BIM] Ladybug: '+what,e);a3dToast(what+': '+(e&&e.message||e));bimLbRefresh();};}
    if(c==='open'){bimLbPickFile();return true;}
    if(c==='study')return bimLbsAct(k);   /* __acad3dV172c: the studies on the model */
    if(c==='year'){
      a3dToast('Getting a year of hours from Open-Meteo, then Ladybug reads them ...');
      bimLbFetchYear().then(function(s){a3dToast('Weather: '+bimLbSrcWords(s));},fail('The year of hours could not be had'));
      return true;
    }
    if(c==='runall'){a3dToast('Running Ladybug\'s four analyses ...');bimLbRunAll();return true;}
    if(BIM_LB_KINDS.indexOf(k)<0)return false;
    if(c==='run'){
      a3dToast('Running '+BIM_LB_NAMES[k]+' ...');
      bimLbRun(k).then(function(){a3dToast(BIM_LB_NAMES[k]+': done. Show on the board draws it');},fail(BIM_LB_NAMES[k]+' did not run'));
      return true;
    }
    if(c==='show'){
      if(!bimBoardShow('climate'))return false;
      var B=bimBoardById('board-climate');
      if(B&&B.figs&&!B.figs.some(function(x){return x.f===BIM_LB_FIG[k];})&&(B.off||[]).indexOf(BIM_LB_FIG[k])>=0)a3dToast('It was taken off this arranged board: Add to a board puts it back');
      return true;
    }
    if(c==='to')return bimLbToBoard(k);
    return false;
  }
