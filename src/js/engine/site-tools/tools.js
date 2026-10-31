  /* ================= __acad3dV172: the site analysis tools: the tools, their parameters, their runs =================
     Esri's geoprocessing pane, read at the source (reference/research-site-analysis-tools.md, 2): every tool opens the
     same way, its parameters typed (a layer, a number with its unit, a choice, a run from History), the required ones
     marked, each checked as it is filled in -- the tool's own checks too -- with a message beside the field; Run;
     then the status (succeeded, succeeded with warnings, failed), how long it took, the messages, and the output
     added as a layer. Every run is kept in History with the project: its parameters, when, how long, its status and
     messages, its output; one reopens the tool with the same settings, or runs again, or is removed. A tool's
     parameters as last set are kept with the project; setting one is no undo step, a run is one. */
  var BIM_TL_TOOLS=[];   /* the tools, each file below adding its own: {id, name, cmd, sum, how, params, check, run} */
  var BIM_TL_HMAX=40;
  var BIM_TL_ST={ok:'Succeeded',warn:'Succeeded with warnings',fail:'Failed'};
  /* the continuous ramps: a colour-blind-safe sequential for suitability (low to high), one hue for distance */
  var BIM_TL_RAMP_SUIT=['#440154','#3b528b','#21918c','#5ec962','#fde725'],BIM_TL_RAMP_DIST=['#eff3ff','#bdd7e7','#6baed6','#3182bd','#08519c'];
  var BIM_TL_REST='#9aa0a6',BIM_TL_REST_PAL='#9aa0a680';   /* restricted: grey, as the Suitability Modeler draws it; half seen on the plan, so the map shows through */
  var BIM_TL_LEVELS=91;   /* a continuous output's levels */
  var BIM_TL_ACRE=4046.8564224;   /* the international acre, 4046.8564224 m2 */
  function bimTlTool(id){var i;for(i=0;i<BIM_TL_TOOLS.length;i++)if(BIM_TL_TOOLS[i].id===id)return BIM_TL_TOOLS[i];return null;}
  function bimTlParam(t,id){var i;for(i=0;i<t.params.length;i++)if(t.params[i].id===id)return t.params[i];return null;}
  function bimTlCopy(o){return JSON.parse(JSON.stringify(o));}
  function bimTlArea(n,G){return n*G.cell*G.cell;}
  function bimTlAreaText(m2){return m2>=10000?bimDispNum(m2/10000,2)+' ha':bimDispNum(m2,0)+' m\u00b2';}
  /* ---- the parameters ---- */
  function bimTlDefault(p,G){return typeof p.def==='function'?p.def(G):(p.def===undefined?null:p.def);}
  /* a tool's parameters now: what was set, over the defaults; criteria field by field */
  function bimTlParams(t,over){
    var T=bimTlState(),S=over||T.params[t.id]||{},P={},G=bimTlGrid();
    t.params.forEach(function(p){
      if(p.t==='crit'){
        var C={},s=S.crit||{};
        p.crit.forEach(function(c){
          var d=c.def(G),x=s[c.id]||{},o={},k;
          for(k in d)if(d.hasOwnProperty(k))o[k]=x.hasOwnProperty(k)?x[k]:d[k];
          C[c.id]=o;
        });
        P.crit=C;return;
      }
      P[p.id]=S.hasOwnProperty(p.id)?S[p.id]:bimTlDefault(p,G);
    });
    return P;
  }
  /* a choice's options: [value, label] */
  function bimTlOpts(p,P,G){
    if(p.t==='src')return BIM_TL_SRC.filter(function(s){return !p.kinds||p.kinds.indexOf(s.kind)>=0;}).map(function(s){return [s.id,s.name];});
    if(p.t==='run'){
      var o=bimTlRuns(p.of).map(function(h){return [h.id,bimTlRunLabel(h)];});
      return p.req?o:[['','None']].concat(o);
    }
    return typeof p.opts==='function'?p.opts(P,G):p.opts;
  }
  /* one field, as typed or ticked: a number, a choice, a tick; kept, no undo step */
  function bimTlSetField(key,raw){
    var a=String(key||'').split('|'),t=bimTlTool(a[0]),T=bimTlState(),S,p,v,c,cf;
    if(!t)return false;
    S=T.params[t.id]||(T.params[t.id]={});
    if(a[1]==='crit'){
      p=bimTlParam(t,'crit');c=p&&p.crit.filter(function(x){return x.id===a[2];})[0];
      if(!c||!a[3])return false;
      cf=c.fields[a[3]];
      if(!cf)return false;
      v=cf==='num'?bimTlNum(raw):cf==='bool'?(raw===true||raw==='true'):String(raw==null?'':raw).slice(0,200);
      S.crit=S.crit||{};S.crit[c.id]=S.crit[c.id]||{};S.crit[c.id][a[3]]=v;
    }else{
      p=bimTlParam(t,a[1]);
      if(!p)return false;
      v=p.t==='num'?bimTlNum(raw):p.t==='bool'?(raw===true||raw==='true'):String(raw==null?'':raw).slice(0,80);
      S[p.id]=v;
    }
    saveSoon();
    return true;
  }
  function bimTlNum(raw){var s=String(raw==null?'':raw).replace(/^\s+|\s+$/g,'');if(s==='')return null;var v=parseFloat(s);return isFinite(v)&&/^[-+]?(\d+\.?\d*|\.\d+)(e[-+]?\d+)?$/i.test(s)?v:NaN;}
  /* the sources, worked out once for a grid and the data it reads */
  function bimTlStamp(G){
    var A=A3D.site&&A3D.site.access,LD=A3D.site&&A3D.site.land,F=LD&&LD.flood,W=bimTlState().wetlands,s=A3D_SIM.sun,n=0,i;
    for(i=0;i<A3D.objs.length;i++)if(A3D.objs[i].context)n++;
    return [G.key,A?(A.fetched||'')+':'+(A.segs?A.segs.length:0):'',F?(F.fetched||'')+':'+(F.features?F.features.length:0):'',
      W?(W.fetched||'')+':'+(W.f?W.f.length:0):'',s?(s.runId||s.date||'')+':'+s.nx+'x'+s.nz:'',n,(LD&&LD.dem&&LD.dem.fetched)||''].join('|');
  }
  function bimTlSourceOf(G,id){
    var st=bimTlStamp(G);
    if(!A3D_TL.memo||A3D_TL.memo.st!==st)A3D_TL.memo={st:st,m:{}};
    var M=A3D_TL.memo.m;
    if(!M.hasOwnProperty(id)){try{M[id]=bimTlSource(G,id);}catch(eS){console.warn('[BIM] A tool\'s layer could not be read',eS);M[id]={why:'It could not be read: '+String(eS&&eS.message||eS).slice(0,120)};}}
    return M[id];
  }
  /* the checks: each parameter by its type, then the tool's own; E errors, W warnings, by parameter ('_' the tool) */
  function bimTlCheck(t,P,G){
    var E={},W={},first=null,k;
    t.params.forEach(function(p){
      var v=P[p.id],o,s,sd,mn,mx;
      if(p.t==='crit'||p.t==='bool')return;
      if(p.t==='num'){
        if(v===null||v===undefined){if(p.req)E[p.id]='Required';return;}
        if(!isFinite(v)){E[p.id]='Type a number';return;}
        mn=typeof p.min==='function'?p.min(P,G):p.min;mx=typeof p.max==='function'?p.max(P,G):p.max;
        if(mn!==undefined&&mn!==null&&(p.gt?!(v>mn):!(v>=mn)))E[p.id]=(p.gt?'More than ':'At least ')+bimDispNum(mn,2)+(p.unit?' '+p.unit:'');
        else if(mx!==undefined&&mx!==null&&!(v<=mx))E[p.id]='At most '+bimDispNum(mx,2)+(p.unit?' '+p.unit:'');
        return;
      }
      if(v===null||v===undefined||v===''){if(p.req)E[p.id]='Required';return;}
      o=bimTlOpts(p,P,G);
      if(!o.some(function(x){return x[0]===v;})){E[p.id]=p.t==='run'?'That run is no longer in History':'Not one of the choices';return;}
      if(p.t==='src'){
        sd=bimTlSrc(v);s=bimTlSourceOf(G,v);
        if(s.why)E[p.id]=s.why;else if(s.none)W[p.id]=sd.name+': none within the extent';
      }
      if(p.t==='run'){s=bimTlRunOut(v,G);if(s.why)E[p.id]=s.why;}
    });
    if(t.check){try{t.check(P,G,E,W);}catch(eC){console.warn('[BIM] A tool\'s check',eC);E._='Its check failed: '+String(eC&&eC.message||eC).slice(0,120);}}
    for(k in E)if(E.hasOwnProperty(k)){first=(k==='_'||k.indexOf('crit.')===0?'':bimTlLabel(t,k)+': ')+E[k];break;}
    return {E:E,W:W,err:first!==null,first:first};
  }
  function bimTlLabel(t,id){var p=bimTlParam(t,id);return p?p.label:id;}
  /* ---- History ---- */
  function bimTlRuns(tool){return bimTlState().history.filter(function(h){return (!tool||h.tool===tool)&&h.st!=='fail';});}
  function bimTlRunById(id){var H=bimTlState().history,i;for(i=0;i<H.length;i++)if(H[i].id===id)return H[i];return null;}
  function bimTlRunLabel(h){var t=bimTlTool(h.tool);return (t?t.name:h.tool)+', '+h.at+(h.label?': '+h.label:'');}
  function bimTlLast(tool){var R=bimTlRuns(tool);return R.length?R[0].id:'';}
  /* a run's output, read back: its layer's levels on this grid, or why not */
  function bimTlRunOut(id,G){
    var h=bimTlRunById(id),R=null,L=bimResLayers(),i,lv;
    if(!h)return {why:'That run is no longer in History'};
    if(h.st==='fail')return {why:'That run failed'};
    for(i=0;i<L.length;i++)if(L[i].id===h.layer&&L[i].kind==='tool')R=L[i];
    if(!R)return {why:'Its output layer was removed: run '+((bimTlTool(h.tool)||{}).name||'it')+' again'};
    if(R.data.gkey!==G.key)return {why:'It ran on another lot or extent: run it again'};
    if(R.run!==h.id)return {why:'Its layer holds a later run now: pick that run'};
    lv=bimTlDecode(R.data);
    if(!lv)return {why:'Its output could not be read'};
    return {h:h,R:R,d:R.data,lv:lv};
  }
  /* ---- the outputs, as result layers (V148) ---- */
  function bimTlRamp(stops,n){
    var out=[],i,f,a,b,j,t,ca,cb;
    function rgb(h){var x=parseInt(h.slice(1),16);return [(x>>16)&255,(x>>8)&255,x&255];}
    function hx(v){var s=Math.round(Math.max(0,Math.min(255,v))).toString(16);return s.length<2?'0'+s:s;}
    for(i=0;i<n;i++){
      f=n>1?i/(n-1)*(stops.length-1):0;j=Math.min(stops.length-2,Math.floor(f));t=f-j;
      ca=rgb(stops[j]);cb=rgb(stops[j+1]);
      a=[ca[0]+(cb[0]-ca[0])*t,ca[1]+(cb[1]-ca[1])*t,ca[2]+(cb[2]-ca[2])*t];
      out.push('#'+hx(a[0])+hx(a[1])+hx(a[2]));
    }
    return out;
  }
  /* values to levels between lo and hi; NaN, none */
  function bimTlQuant(V,lo,hi,n){
    var lv=new Int16Array(V.length),k,q;
    for(k=0;k<V.length;k++){
      if(!isFinite(V[k])){lv[k]=-1;continue;}
      q=hi>lo?Math.round((V[k]-lo)/(hi-lo)*(n-1)):0;
      lv[k]=Math.max(0,Math.min(n-1,q));
    }
    return lv;
  }
  function bimTlRange(V,mask){var lo=Infinity,hi=-Infinity,k;for(k=0;k<V.length;k++){if(mask&&!mask[k])continue;if(isFinite(V[k])){if(V[k]<lo)lo=V[k];if(V[k]>hi)hi=V[k];}}return lo<=hi?[lo,hi]:null;}
  /* a run's layer: replaces the layer of an earlier run with the same parameters, as Esri's tools overwrite their output */
  function bimTlLayerPut(t,h,L,G){
    var sig=t.id+'|'+JSON.stringify(h.params),Ls=bimResLayers(),R=null,i,e=bimTlEncode(L.lv);
    for(i=0;i<Ls.length;i++)if(Ls[i].kind==='tool'&&Ls[i].sig===sig){R=Ls[i];break;}
    var d={x0:G.x0,z0:G.z0,cell:G.cell,nx:G.nx,nz:G.nz,rc:e.rc,rn:e.rn,n:L.n,pal:L.pal,keys:L.keys||[],lo:L.lo,hi:L.hi,unit:L.unit||'',
      cats:L.cats||null,rest:L.rest===undefined?null:L.rest,gkey:G.key,y:G.site.y,tool:t.id};
    if(R){R.data=d;R.run=h.id;R.updated=bimResNow();R.name=t.name+': '+L.name;delete A3D_RES_IMG[R.id];}
    else{
      R={id:'res-'+Date.now().toString(36)+'-'+(A3D.seq++),kind:'tool',tool:t.id,sig:sig,name:t.name+': '+L.name,data:d,
        opacity:L.opacity||0.75,visible:true,created:bimResNow(),run:h.id};
      Ls.unshift(R);
    }
    return R;
  }
  function bimTlStale(R){return !!(R&&R.kind==='tool'&&R.data&&R.data.gkey!==bimTlGrid().key);}
  function bimTlImage(R){
    var c=A3D_RES_IMG[R.id],d=R.data,lv,img;
    if(c&&c.d===d)return c.img;
    lv=bimTlDecode(d);
    if(!lv)return null;
    img=bimSimGridImage(d,function(k){var q=lv[k];return q<0?null:(d.pal[q]||null);});
    A3D_RES_IMG[R.id]={d:d,img:img};
    return img;
  }
  /* ---- a run ---- */
  function bimTlRun(id,opts){
    opts=opts||{};
    var t=bimTlTool(id),G,P,C,t0,M=[],out=null,st='ok',h,T;
    if(!t){a3dToast('There is no tool called '+id);return {error:'No such tool'};}
    G=bimTlGrid();
    P=opts.params?bimTlParams(t,opts.params):bimTlParams(t);
    C=bimTlCheck(t,P,G);
    if(C.err){if(!opts.quiet)a3dToast(t.name+' cannot run: '+C.first);return {error:C.first,E:C.E};}
    for(var k in C.W)if(C.W.hasOwnProperty(k))M.push({t:'warn',s:(k==='_'?'':bimTlLabel(t,k)+': ')+C.W[k]});
    t0=Date.now();
    try{out=t.run(P,G,M);}catch(eR){console.warn('[BIM] '+t.name+' failed',eR);out={error:'It stopped: '+String(eR&&eR.message||eR).slice(0,160)};}
    if(!out)out={error:'It gave no output'};
    if(out.error){st='fail';M.push({t:'err',s:out.error});}
    else if(M.some(function(m){return m.t==='warn';}))st='warn';
    pushUndo();
    T=bimTlState();
    h={id:'tlh-'+Date.now().toString(36)+'-'+(A3D.seq++),tool:t.id,params:bimTlCopy(P),at:bimResNow(),ms:Date.now()-t0,st:st,msgs:M,
      stats:out.error?[]:(out.stats||[]),sum:out.error?'':(out.sum||''),label:out.error?'':(out.label||''),gkey:G.key,
      std:!out.error&&out.std&&out.std.length?bimStdStamp(out.std):null};
    if(!out.error&&out.layer){var R=bimTlLayerPut(t,h,out.layer,G);h.layer=R.id;}
    T.history.unshift(h);
    if(T.history.length>BIM_TL_HMAX)T.history.length=BIM_TL_HMAX;
    if(out.keep)out.keep(T,h);
    refreshLayers();paint();saveSoon();
    try{if(A3D_AW.on)bimAwRefresh();else bimAnalyzeRefresh();}catch(eF){console.warn('[BIM] Analyze refresh',eF);}
    if(!opts.quiet)a3dToast(t.name+': '+BIM_TL_ST[st].toLowerCase()+(st==='fail'?' -- '+out.error:(h.sum?' -- '+h.sum:'')));
    return h;
  }
  /* History: open (the tool with the run's parameters set), run again, remove */
  function bimTlOpen(hid){
    var h=bimTlRunById(hid),t=h&&bimTlTool(h.tool);
    if(!t)return false;
    bimTlState().params[t.id]=bimTlCopy(h.params);saveSoon();
    return bimAwPick('tool',t.id);
  }
  function bimTlRerun(hid){var h=bimTlRunById(hid);return h?bimTlRun(h.tool,{params:bimTlCopy(h.params)}):null;}
  function bimTlForget(hid){
    var T=bimTlState(),i;
    for(i=0;i<T.history.length;i++)if(T.history[i].id===hid)break;
    if(i>=T.history.length)return false;
    pushUndo();
    T.history.splice(i,1);saveSoon();
    a3dToast('The run is removed from History; its layer stays in Layers');
    return true;
  }
  /* a layer's Update: its run again, with the same parameters */
  function bimTlLayerRerun(R){
    var h=bimTlRunById(R.run);
    if(!h){a3dToast(R.name+': its run is no longer in History -- open the tool and run it again');return false;}
    var r=bimTlRun(h.tool,{params:bimTlCopy(h.params)});
    return !!(r&&!r.error&&r.st!=='fail');
  }
  /* ---- shared by the tools ---- */
  /* the lot's cells, or every cell when there is no lot */
  function bimTlInLot(G){if(G.lot)return G.lot;var m=new Uint8Array(G.n);m.fill(1);return m;}
  function bimTlCountIn(G,m,w){var n=0,k;for(k=0;k<G.n;k++)if(m[k]&&(!w||w[k]))n++;return n;}
  /* the extent's words, for the messages */
  function bimTlExtentText(G){return (G.ring?'the lot and '+BIM_TL_MARGIN+' m around it':'100 m around the site')+', '+G.nx+' by '+G.nz+' cells of '+bimDispNum(G.cell,2)+' m';}
  function bimTlInfo(M,s){M.push({t:'info',s:s});}
  function bimTlWarn(M,s){M.push({t:'warn',s:s});}
