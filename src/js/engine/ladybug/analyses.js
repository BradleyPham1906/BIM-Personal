  /* ================= __acad3dV172b: the analyses, run and kept =================
     reference/research-ladybug-weather-comfort.md, 9 and 10. Each run calls the adapter in the worker, and its answer
     is kept with the project with the source it read and the versions that made it (A3D.site.ladybug):
     - utci: UTCI over the year in CBE Clima's four conditions (the owner, 2026-10-31), the official scale;
     - psych: the psychrometric chart, the merged PMV comfort polygon at 0.5 and 1.0 clo and 1.1 met, and Ladybug's
       five passive strategies with its defaults (the owner, 2026-10-31);
     - wind: Ladybug's wind rose, in the app's speed bands;
     - dd: the design days, the DDY's first, said where they are approximated from one year.
     A run is one undo step; a failure is warned and toasted with its cause and keeps what was there. */
  var BIM_LB_KINDS=['utci','psych','wind','dd'];
  var BIM_LB_NAMES={utci:'Outdoor comfort (UTCI)',psych:'Psychrometric chart and comfort',wind:'Wind rose',dd:'Design days'};
  var BIM_LB_FN={utci:'utci',psych:'psych',wind:'windrose',dd:'design_days'};
  var A3D_LBRUN={busy:null};
  /* the worker has the project's source, or gets it: Open-Meteo's year again; a file must be opened again */
  function bimLbEnsureSource(){
    var s=bimLbSrcKept();
    if(A3D_LB.src&&s&&A3D_LB.src.key===s.key)return Promise.resolve(A3D_LB.src);
    if(s&&s.kind==='openmeteo')return bimLbFetchYear();
    if(s&&s.kind==='file')return Promise.reject(new Error('Open '+s.name+' again: a weather file is not kept with the project'));
    return Promise.reject(new Error('Choose the weather first: open an EPW (or its ZIP), or get the year from Open-Meteo'));
  }
  /* the parameters a run uses, from its kind */
  function bimLbParams(kind){
    if(kind==='utci')return {conditions:['sun_wind','shade_wind','sun_still','shade_still']};
    if(kind==='psych')return {clo:[0.5,1.0],met:[1.1,1.1],merge:true};
    if(kind==='wind')return {directions:16,bins:bimClimWindBins()};
    return {};
  }
  function bimLbRun(kind,params){
    if(BIM_LB_KINDS.indexOf(kind)<0)return Promise.reject(new Error('Not a Ladybug analysis: '+kind));
    if(A3D_LBRUN.busy)return Promise.reject(new Error(BIM_LB_NAMES[A3D_LBRUN.busy]+' is still running'));
    var P=params||bimLbParams(kind),t0=Date.now();
    A3D_LBRUN.busy=kind;
    if(typeof bimLbRefresh==='function')bimLbRefresh();
    return bimLbEnsureSource().then(function(src){
      return bimLbCall(BIM_LB_FN[kind],P).then(function(r){
        var D=bimLbData();
        pushUndo();
        D[kind]={r:r,params:P,at:bimSaToday(),src:src.key,ms:Date.now()-t0,
          v:{pyodide:A3D_LB.pyodide,ladybug:A3D_LB.versions||{}}};
        return D[kind];
      });
    }).then(function(rec){
      A3D_LBRUN.busy=null;saveSoon();
      if(typeof bimLbRefresh==='function')bimLbRefresh();
      return rec;
    },function(e){
      A3D_LBRUN.busy=null;
      if(typeof bimLbRefresh==='function')bimLbRefresh();
      throw e;
    });
  }
  /* every analysis in turn, from a button: what failed is said, the rest kept */
  function bimLbRunAll(){
    var done=[],bad=[],i=0;
    function next(){
      if(i>=BIM_LB_KINDS.length){
        a3dToast(done.length?'Ladybug: '+done.join(', ')+(bad.length?'. Not done: '+bad.join('; '):''):'Ladybug: nothing was run. '+bad.join('; '));
        return {done:done,bad:bad};
      }
      var k=BIM_LB_KINDS[i++];
      return bimLbRun(k).then(function(){done.push(BIM_LB_NAMES[k]);return next();},function(e){
        console.warn('[BIM] Ladybug '+k,e);bad.push(BIM_LB_NAMES[k]+': '+(e&&e.message||e));
        if(/Choose the weather|Open .* again|could not start|did not load|cannot run/.test(String(e&&e.message)))i=BIM_LB_KINDS.length;
        return next();
      });
    }
    return next();
  }
  /* a kept result, if it is one and of the source the project names */
  function bimLbResult(kind){
    var L=A3D.site&&A3D.site.ladybug,R=L&&L[kind],s=bimLbSrcKept();
    if(!R||typeof R!=='object'||!R.r||typeof R.r!=='object')return null;
    return {r:R.r,params:R.params,at:R.at,ms:R.ms,v:R.v,stale:!s||R.src!==s.key};
  }
