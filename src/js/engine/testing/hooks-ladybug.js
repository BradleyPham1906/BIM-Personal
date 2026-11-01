  /* __acad3dV172b: the Ladybug analyses, for the suite */
  window.__acad3dV172b='runtime,manifest,worker,sha256,adapter,epw,ddy,openmeteo,standardtime,utci4,psych,pmv2clo,strategies5,windrose,designdays,kept';
  function bimLbErr(e){return {error:String(e&&e.message||e)};}
  /* where the runtime is loaded from; a suite points it at its own server */
  window.__a3dLbBase=function(u){if(u!==undefined)A3D_LB.base=u||null;return bimLbBase();};
  window.__a3dLbState=function(){
    return {st:A3D_LB.st,err:A3D_LB.err,versions:A3D_LB.versions,pyodide:A3D_LB.pyodide,ms:A3D_LB.ms,src:A3D_LB.src,
      busy:A3D_LBRUN.busy,base:bimLbBase(),pages:BIM_LB_PAGES,dir:'pyodide/'+BIM_LB_PYODIDE+'/',wheels:BIM_LB_WHEELS,
      pyLength:BIM_LB_PY.length,words:bimLbStateText()};
  };
  window.__a3dLbStart=function(){return bimLbStart().then(function(){return window.__a3dLbState();},bimLbErr);};
  window.__a3dLbStop=function(){bimLbStop('stopped by the suite');return window.__a3dLbState();};
  window.__a3dLbCall=function(fn,args){return bimLbCall(fn,args).then(function(r){return r;},bimLbErr);};
  /* a weather file's bytes, as base64 (a file chooser cannot be driven) */
  window.__a3dLbOpenB64=function(name,b64){
    var s=atob(b64),a=new Uint8Array(s.length),i;
    for(i=0;i<s.length;i++)a[i]=s.charCodeAt(i);
    return bimLbOpenBytes(name,a).then(function(r){return r;},bimLbErr);
  };
  window.__a3dLbFetchYear=function(){return bimLbFetchYear().then(function(r){return r;},bimLbErr);};
  window.__a3dLbRun=function(kind,params){return bimLbRun(kind,params).then(function(r){return r;},bimLbErr);};
  window.__a3dLbRunAll=function(){return bimLbRunAll();};
  window.__a3dLbData=function(){return JSON.parse(JSON.stringify((A3D.site&&A3D.site.ladybug)||null));};
  window.__a3dLbResult=function(kind){return bimLbResult(kind);};
  window.__a3dLbOmUrl=function(lat,lon,year,zone){return bimLbOmUrl(lat,lon,year,zone);};
  window.__a3dLbOmZone=function(off){return bimLbOmZone(off);};
