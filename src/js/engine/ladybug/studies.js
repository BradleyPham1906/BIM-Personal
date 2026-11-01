  /* ================= __acad3dV172c: sun-hours and radiation on the model, by Ladybug =================
     reference/research-ladybug-sun-radiation.md (5b). Two studies, beside V143's Solar and V148's Sun hours (kept,
     the owner, 2026-11-01):
     - rad: incident radiation on each face, kWh/m2 over the weather's year (or some months): Ladybug's SkyMatrix from
       the weather V172b opened, with Radiance's gendaymtx (WebAssembly), and RadiationStudy's own sum;
     - sun: direct sun hours on each face over the day studied (the site's date) or the year: Ladybug's Sunpath and
       DirectSunStudy's own sum; no weather needed.
     The rays are the worker's (rays.js), over every solid shown, as V143's are; the faces studied are the
     selection's solids, else every solid, each face once (Ladybug's study of a mesh), its point moved off the face
     by the registry's offset. The sky is Tregenza's by default, as Ladybug's; Reinhart's the finer choice. A run is
     one undo step and is kept with the project with what it read (the weather, the versions, the standards, the
     model's stamp), out of date when any of them changes. Shown on the model as Ladybug draws a study: the faces in
     its legend's colours, the rest in grey, with the legend. */
  var BIM_LBS_KINDS=['rad','sun'];
  var BIM_LBS_NAMES={rad:'Incident radiation (Ladybug)',sun:'Direct sun hours (Ladybug)'};
  /* Ladybug's legend colours (ladybug/color.py): Colorset.original, a study's default; Colorset.ecotect, the one
     DirectSunStudy.draw sets */
  var BIM_LBS_RAMP={rad:['#4b6ba9','#7393ca','#aac8f7','#c1d5d0','#f5ef67','#fce64a','#ef9c15','#ea7b00','#ea4a00','#ea2600'],
    sun:['#0000ff','#3500ca','#6b0094','#a0005f','#d60029','#ff0c00','#ff4200','#ff7700','#ffad00','#ffe200','#ffff00']};
  var BIM_LBS_CONTEXT='#9aa1a9';
  var BIM_LB_STUDY_MS=600000;
  var A3D_LBS={busy:null};
  function bimLbsOpts(){
    var D=bimLbData(),o=D.studyOpts;
    if(!o||typeof o!=='object'||Array.isArray(o))o=D.studyOpts={};
    if(o.dense!==true)o.dense=false;
    if(o.span!=='year')o.span='day';
    return o;
  }
  /* a kept study, if it is one */
  function bimLbsKept(k){
    var L=A3D.site&&A3D.site.ladybug,R=L&&L[k];
    if(!R||typeof R!=='object'||!R.r||typeof R.r!=='object'||!R.r.faces||typeof R.r.faces!=='object')return null;
    return R;
  }
  /* why a kept study is out of date: none when it is not */
  function bimLbsStale(k,R){
    var why=[],s;
    if(!R)return why;
    if(R.stamp!==bimResKeyFrom(bimSimStamp(),'sunhours'))why.push('the model, its north or the site\'s place has changed');
    if(k==='sun'&&R.params&&R.params.span!=='year'&&R.params.date!==bimSunSettings().date)why.push('the day studied has changed');
    if(k==='rad'){s=bimLbSrcKept();if(!s||R.src!==s.key)why.push('the weather is not what it read');}
    if(R.std&&bimStdChanged(R.std).length)why.push(bimStdChangedText(bimStdChanged(R.std)));
    return why;
  }
  /* the faces studied and the model's triangles: the app's frame, metres */
  function bimLbsGeometry(ids){
    var T=bimSolarTargets(ids),occ=bimSolarOccluders(),off=bimStd('app.solar','offset'),nt=0,q=0,TA,sens=[],map=[],i,k;
    for(i=0;i<occ.length;i++)nt+=occ[i].tris.length;
    TA=new Float64Array(nt*9);
    occ.forEach(function(o){o.tris.forEach(function(t){for(k=0;k<3;k++){TA[q++]=t[k][0];TA[q++]=t[k][1];TA[q++]=t[k][2];}});});
    T.forEach(function(o){
      var m=meshOf(o),rec={id:o.id,n:m&&m.f?m.f.length:0,f:[]};
      bimSolarFaces(o).forEach(function(fc){
        if(fc.n[1]<-0.99)return;   /* the underside on the ground, as V143 leaves it */
        rec.f.push([fc.i,fc.area]);
        sens.push(fc.c[0]+fc.n[0]*off,fc.c[1]+fc.n[1]*off,fc.c[2]+fc.n[2]*off,fc.n[0],fc.n[1],fc.n[2]);
      });
      if(rec.f.length)map.push(rec);
    });
    /* all: every solid was studied (none selected, or the selection had no solid, and bimSolarTargets took them all) */
    return {tris:TA,sens:new Float64Array(sens),map:map,faces:sens.length/6,solids:map.length,all:T.length===bimSolarTargets(null).length};
  }
  /* the day studied, or the year, as Ladybug's analysis period [month, day, hour, month, day, hour] */
  function bimLbsPeriod(span,date){
    if(span==='year')return [1,1,0,12,31,23];
    var m=/^(\d{4})-(\d{2})-(\d{2})$/.exec(String(date||'')),mo=m?+m[2]:6,d=m?+m[3]:21;
    if(mo===2&&d===29)d=28;   /* Ladybug's period is of a year that is not a leap year */
    return [mo,d,0,mo,d,23];
  }
  /* the worker's two calls, and the rays between them */
  function bimLbsRequest(k,G){
    var st=bimSunSettings(),o=bimLbsOpts(),tn=bimTrueNorthDeg()||0;
    if(k==='rad')return {kind:'rad',tn:tn,tris:G.tris,sens:G.sens,
      pre:{fn:'sky',args:{density:o.dense?1:0,ground_ref:bimStd('app.solar','ground_ref')}},post:{fn:'radiation',args:{}}};
    var step=bimStd('app.solar',o.span==='year'?'step_year':'step_day');
    return {kind:'sun',tn:tn,tris:G.tris,sens:G.sens,
      pre:{fn:'sun_vectors',args:{lat:st.lat,lon:st.lon,tz:st.tz,period:bimLbsPeriod(o.span,st.date),timestep:step}},
      post:{fn:'sun_hours',args:{timestep:step}}};
  }
  /* the answer's numbers onto the faces: per solid, one value a face (null where not studied) */
  function bimLbsPack(G,vals){
    var faces={},i=0,lo=Infinity,hi=-Infinity,A=0,S=0;
    G.map.forEach(function(rec){
      var a=[],j;for(j=0;j<rec.n;j++)a.push(null);
      rec.f.forEach(function(f){var v=vals[i++];if(typeof v!=='number')return;a[f[0]]=v;
        if(v<lo)lo=v;if(v>hi)hi=v;A+=f[1];S+=v*f[1];});
      faces[rec.id]=a;
    });
    return {faces:faces,min:isFinite(lo)?lo:0,max:isFinite(hi)?hi:0,mean:A?S/A:0,area:A,total:S,count:i};
  }
  function bimLbsRun(k,opts){
    opts=opts||{};
    if(BIM_LBS_KINDS.indexOf(k)<0)return Promise.reject(new Error('Not a Ladybug study: '+k));
    if(A3D_LBS.busy)return Promise.reject(new Error(BIM_LBS_NAMES[A3D_LBS.busy]+' is still running'));
    var miss=bimSunNow(true).missing;
    if(miss)return Promise.reject(new Error('Set the site '+miss.join(', ')+' first (Properties > Site > Location)'));
    var ids=opts.ids||(A3D.selSet&&A3D.selSet.length?A3D.selSet:null),G=bimLbsGeometry(ids);
    if(!G.faces)return Promise.reject(new Error('There are no solids to study: draw or bring in buildings first'));
    var stamp=bimResKeyFrom(bimSimStamp(),'sunhours'),t0=Date.now(),req=bimLbsRequest(k,G),src=null,o=bimLbsOpts();
    A3D_LBS.busy=k;
    bimLbRefresh();
    var p=k==='rad'?bimLbEnsureSource().then(function(s){src=s;}):Promise.resolve();
    return p.then(function(){return bimLbStudyCall(req,[req.tris.buffer,req.sens.buffer]);}).then(function(ans){
      if(!ans||!Array.isArray(ans.values)||ans.values.length!==G.faces)throw new Error('The study answered '+(ans&&ans.values?ans.values.length:0)+' values for '+G.faces+' faces');
      var D=bimLbData(),r=bimLbsPack(G,ans.values),ver;
      if(ans.versions){try{ver=JSON.parse(ans.versions);if(ver&&typeof ver==='object')A3D_LB.versions=ver;}catch(eV){console.warn('[BIM] Ladybug versions',eV);}}
      r.pre=ans.pre;r.dirs=ans.dirs;r.ms=ans.ms;r.solids=G.solids;r.all=G.all;
      pushUndo();
      D[k]={r:r,params:{dense:o.dense,span:o.span,date:bimSunSettings().date,ids:ids?ids.slice():null},at:bimSaToday(),
        ms:Date.now()-t0,src:src?src.key:null,stamp:stamp,std:bimStdStamp(['app.solar']),
        v:{pyodide:A3D_LB.pyodide,ladybug:A3D_LB.versions||{},gendaymtx:'Radiance rad6R0P1a'}};
      D.lbshow=k;
      A3D_LBS.busy=null;saveSoon();bimLbRefresh();paint();
      return D[k];
    }).then(null,function(e){A3D_LBS.busy=null;bimLbRefresh();throw e;});
  }
  function bimLbsClear(k){
    var D=bimLbData();
    if(!D[k])return false;
    pushUndo();delete D[k];if(D.lbshow===k)D.lbshow='';
    saveSoon();bimLbRefresh();paint();return true;
  }
  /* a value's colour on Ladybug's legend: continuous between its colours, as Ladybug's legend is by default */
  function bimLbsCol(k,v,lo,hi){
    var C=BIM_LBS_RAMP[k],f=hi>lo?(v-lo)/(hi-lo):0,x,i,a,b,t;
    f=Math.max(0,Math.min(1,f));x=f*(C.length-1);i=Math.min(C.length-2,Math.floor(x));t=x-i;
    a=parseInt(C[i].slice(1),16);b=parseInt(C[i+1].slice(1),16);
    function ch(s){var p=(a>>s)&255,q=(b>>s)&255;return Math.round(p+(q-p)*t);}
    return 'rgb('+ch(16)+','+ch(8)+','+ch(0)+')';
  }
  /* the study shown, over the model: the faces facing the eye, far to near; the studied in the legend's colours,
     the rest of the solids in grey; then the legend */
  function bimLbsDraw(ctx,V,W,H){
    var D=A3D.site&&A3D.site.ladybug,k=D&&D.lbshow,R=k?bimLbsKept(k):null;
    A3D.lastLbsDrawn=null;
    if(!R)return;
    ctx.save();
    try{
      var r=R.r,lo=r.min,hi=r.max,polys=[],i,j,q,o,m,wv,f,pts,w,c,n,z,vals,val,eye=V.eye,flat=!!A3D.flat,nf=0;
      for(i=0;i<A3D.objs.length;i++){
        o=A3D.objs[i];m=(o.t==='solid')?meshOf(o):null;
        if(!m||!m.f||!m.v||!bimLayerShown(o)||!bimObjectVisibleOnLevel(o))continue;
        wv=m.v.map(function(p){return [p[0]+o.pos[0],p[1]+o.pos[1],p[2]+o.pos[2]];});
        vals=r.faces[o.id]||null;
        for(j=0;j<m.f.length;j++){
          f=m.f[j];if(!f||f.length<3)continue;
          w=[];c=[0,0,0];for(q=0;q<f.length;q++){w.push(wv[f[q]]);c[0]+=wv[f[q]][0]/f.length;c[1]+=wv[f[q]][1]/f.length;c[2]+=wv[f[q]][2]/f.length;}
          n=faceNormal(w);
          if(flat?vdot(n,V.d)>=0:vdot(n,[eye[0]-c[0],eye[1]-c[1],eye[2]-c[2]])<=0)continue;
          pts=[];z=0;for(q=0;q<w.length;q++){var s=toScreen(w[q],V,W,H);pts.push(s);z+=s[2];}
          val=vals?vals[j]:null;
          polys.push({pts:pts,z:z/w.length,col:typeof val==='number'?bimLbsCol(k,val,lo,hi):shade(BIM_LBS_CONTEXT,0.7+0.3*Math.abs(vdot(n,LIGHT))),v:typeof val==='number'});
        }
      }
      polys.sort(function(a,b){return b.z-a.z;});
      for(i=0;i<polys.length;i++){
        f=polys[i];ctx.beginPath();ctx.moveTo(f.pts[0][0],f.pts[0][1]);
        for(q=1;q<f.pts.length;q++)ctx.lineTo(f.pts[q][0],f.pts[q][1]);
        ctx.closePath();ctx.fillStyle=f.col;ctx.fill();ctx.strokeStyle='rgba(0,0,0,0.25)';ctx.lineWidth=0.6;ctx.stroke();
        if(f.v)nf++;
      }
      /* the legend: Ladybug's colours, the study's own range */
      var sr=bimSafeViewRect(),lw=196,lh=72,lx=Math.max(sr.x+12,sr.x+sr.w-lw-12),ly=Math.max(sr.y+12,sr.y+sr.h-lh-12),g=ctx.createLinearGradient(lx+10,0,lx+lw-10,0),C=BIM_LBS_RAMP[k];
      for(i=0;i<C.length;i++)g.addColorStop(i/(C.length-1),C[i]);
      ctx.fillStyle='rgba(22,26,32,0.9)';ctx.fillRect(lx,ly,lw,lh);
      ctx.strokeStyle='rgba(255,255,255,0.18)';ctx.lineWidth=1;ctx.strokeRect(lx+0.5,ly+0.5,lw-1,lh-1);
      ctx.font='12px system-ui, sans-serif';ctx.textBaseline='middle';ctx.fillStyle='#e8edf2';ctx.textAlign='left';
      ctx.fillText(k==='rad'?'Incident radiation, kWh/m²':'Direct sun hours',lx+10,ly+14);
      ctx.fillStyle=g;ctx.fillRect(lx+10,ly+26,lw-20,12);
      ctx.fillStyle='#e8edf2';ctx.fillText(bimClimFmt(lo,k==='rad'?0:1),lx+10,ly+50);
      ctx.textAlign='right';ctx.fillText(bimClimFmt(hi,k==='rad'?0:1),lx+lw-10,ly+50);
      ctx.fillStyle='#9aa7b4';ctx.textAlign='left';ctx.fillText('Ladybug Tools'+(bimLbsStale(k,R).length?', out of date':''),lx+10,ly+64);
      A3D.lastLbsDrawn={kind:k,faces:nf,polys:polys.length,legend:[lx,ly,lw,lh]};
    }catch(eD){
      console.warn('[BIM] The Ladybug study could not be drawn',eD);
      if(!A3D.lbsDrawWarned){A3D.lbsDrawWarned=true;a3dToast('The Ladybug study could not be drawn: see the console');}
    }
    ctx.restore();
  }
  /* ---- the rows in Analyze, in Climate, after Ladybug's weather and comfort ---- */
  BIM_ANZ_GROUP_OF.lbrad='climate';BIM_ANZ_GROUP_OF.lbsun='climate';
  function bimLbsSummary(k,R){
    var r=R.r;
    if(k==='rad')return bimClimFmt(r.mean,0)+' kWh/m² on average over '+bimClimInt(r.count)+' faces ('+bimClimFmt(r.min,0)+' to '+bimClimFmt(r.max,0)+'), '+bimClimInt(r.total)+' kWh in all';
    return bimClimFmt(r.mean,1)+' h of direct sun on average over '+bimClimInt(r.count)+' faces ('+bimClimFmt(r.min,1)+' to '+bimClimFmt(r.max,1)+')';
  }
  function bimLbsResultHtml(k,R){
    if(!R)return '';
    var r=R.r,p=r.pre||{},P=R.params||{},rows=[],why=bimLbsStale(k,R);
    rows.push(['Faces',bimClimInt(r.count)+' on '+bimClimInt(r.solids||0)+' solid'+(r.solids===1?'':'s')+(r.all?'':' (the selection)')]);
    if(k==='rad'){
      rows.push(['Sky',(p.density==='reinhart'?'Reinhart, 577 patches':'Tregenza, 145 patches')+', ground reflectance '+bimClimFmt(p.ground_ref,2)]);
      rows.push(['Weather',bimClimInt(p.hours||0)+' hours; '+bimClimFmt(p.horizontal,0)+' kWh/m² on open ground']);
      rows.push(['On average',bimClimFmt(r.mean,0)+' kWh/m² ('+bimClimFmt(r.min,0)+' to '+bimClimFmt(r.max,0)+')']);
      rows.push(['In all',bimClimInt(r.total)+' kWh on '+bimClimInt(r.area)+' m²']);
    }else{
      rows.push(['Period',P.span==='year'?'The year, every hour':'The day studied, '+(P.date||'')+', every quarter hour']);
      rows.push(['The sun up',bimClimInt(r.dirs||0)+' steps']);
      rows.push(['On average',bimClimFmt(r.mean,1)+' h ('+bimClimFmt(r.min,1)+' to '+bimClimFmt(r.max,1)+')']);
    }
    var h=bimLbRows(rows)+bimLbNote(bimStdUsedText('app.solar')+'.','a3d-awp-std');
    if(why.length)h+=bimLbNote('Out of date: '+why.join('; ')+'. Run again.','a3d-awp-stale');
    return h+bimLbNote('Run '+R.at+(R.ms?', in '+bimClimFmt(R.ms/1000,1)+' s':'')+(r.ms?' (the rays '+bimClimFmt(r.ms.rays/1000,1)+' s)':'')+'.');
  }
  function bimLbsCards(){
    var C=[],o=bimLbsOpts(),busy=A3D_LBS.busy||A3D_LBRUN.busy,src=bimLbSrcKept(),miss=bimSunNow(true).missing,D=A3D.site&&A3D.site.ladybug,shown=D&&D.lbshow;
    var place=miss?'Set the site '+miss.join(', ')+' first (Site: Location)':'';
    BIM_LBS_KINDS.forEach(function(k){
      var R=bimLbsKept(k),why=bimLbsStale(k,R),off=place||(busy?'Running: '+(BIM_LBS_NAMES[busy]||BIM_LB_NAMES[busy]):'')||(k==='rad'&&!src?'Choose the weather first, in Weather for Ladybug':'');
      var acts=[{act:'lb:study:run:'+k,label:R?'Run again':'Run',pri:!R,off:off},
        {act:'lb:study:show:'+k,label:shown===k?'Hide on the model':'Show on the model',off:R?'':'Run it first'},
        {act:'lb:study:clear:'+k,label:'Clear',off:R?'':'Not run'}];
      if(k==='rad')acts.push({act:'lb:study:sky',label:o.dense?'Sky: Reinhart (finer)':'Sky: Tregenza (Ladybug\'s default)',tip:'Tregenza\'s 145 patches, Ladybug\'s default, read about 4% high in a deep courtyard; Reinhart\'s 577 match the exact view, with four times the rays'});
      else acts.push({act:'lb:study:span',label:o.span==='year'?'Period: the year':'Period: the day studied',tip:'The day studied is the site\'s date (the sun panel), every quarter hour; the year, every hour'});
      C.push({id:'lb'+k,title:BIM_LBS_NAMES[k],state:A3D_LBS.busy===k?'busy':(R?(why.length?'stale':'on'):'off'),
        status:R?bimLbsSummary(k,R):(off||'Not run yet: Run studies '+(A3D.selSet&&A3D.selSet.length?'the selected solids':'every solid')+(k==='rad'?' with '+bimLbSrcWords(src):', on '+(o.span==='year'?'the year':'the day studied'))+'.'),
        extra:bimLbsResultHtml(k,R)+(R?'':bimLbNote(k==='rad'?'Ladybug\'s SkyMatrix from the weather (Radiance\'s gendaymtx, as WebAssembly) and its RadiationStudy, on each face of the solids, every solid shown blocking the sky; no reflections, as in Ladybug.':'Ladybug\'s Sunpath at the site and its DirectSunStudy, on each face of the solids, every solid shown casting shade; no weather needed.')),
        acts:acts});
    });
    return C;
  }
  /* the rows' buttons, from bimLbAct: study:run:<k>, study:show:<k>, study:clear:<k>, study:sky, study:span */
  function bimLbsAct(a){
    var p=String(a).split(':'),c=p[0],k=p[1],o=bimLbsOpts();
    if(c==='sky'){pushUndo();o.dense=!o.dense;saveSoon();bimLbRefresh();a3dToast(o.dense?'The finer Reinhart sky: four times the rays':'Tregenza\'s sky, Ladybug\'s default');return true;}
    if(c==='span'){pushUndo();o.span=o.span==='year'?'day':'year';saveSoon();bimLbRefresh();a3dToast(o.span==='year'?'Direct sun over the year, every hour':'Direct sun on the day studied, every quarter hour');return true;}
    if(BIM_LBS_KINDS.indexOf(k)<0)return false;
    if(c==='run'){
      a3dToast('Running '+BIM_LBS_NAMES[k]+' ...');
      bimLbsRun(k).then(function(R){a3dToast(BIM_LBS_NAMES[k]+': '+bimLbsSummary(k,R));},function(e){
        console.warn('[BIM] Ladybug study '+k,e);a3dToast(BIM_LBS_NAMES[k]+' did not run: '+(e&&e.message||e));});
      return true;
    }
    if(c==='show'){var D=bimLbData();if(!bimLbsKept(k))return false;D.lbshow=D.lbshow===k?'':k;saveSoon();bimLbRefresh();paint();return true;}
    if(c==='clear')return bimLbsClear(k);
    return false;
  }
