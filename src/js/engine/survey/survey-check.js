  /* ================= __acad3dV138: verify the survey ================= */
  var BIM_SURVEY_TOL={fidelity:0.001,bustMin:0.5,bustK:6,bustMax:25,checkPass:0.05,checkWarn:0.15,control:0.02,offsetWarn:1.0};
  var BIM_SURVEY_CHECK_CODE='CHK';
  var A3D_SURVEYCHK={};
  function bimMedian(a){
    if(!a.length)return 0;
    var s=a.slice().sort(function(x,y){return x-y;}),m=s.length>>1;
    return s.length%2?s[m]:(s[m-1]+s[m])/2;
  }
  function bimSurveyName(o,i){var s=o.survey[i];return String((s&&s[3])||('#'+(i+1)));}
  /* the TIN's neighbours of each point */
  function bimTinNeighbours(tin){
    var nb=tin.P.map(function(){return {};}),t,k,a,b;
    for(t=0;t<tin.tris.length;t++)for(k=0;k<3;k++){a=tin.tris[t][k];b=tin.tris[t][(k+1)%3];nb[a][b]=1;nb[b][a]=1;}
    return nb.map(function(m){var out=[],j;for(j in m)if(m.hasOwnProperty(j))out.push(+j);return out;});
  }
  /* bust shots: each point against a plane through its neighbours, the flagged left out */
  function bimSurveyBusts(tin){
    var nb=bimTinNeighbours(tin),out=[],flag={},iter,i,j,k,ws,s,d,dev,devs,best,bi,thr,mad;
    for(iter=0;iter<BIM_SURVEY_TOL.bustMax;iter++){
      devs=[];best=0;bi=-1;
      for(i=0;i<(tin.nSurvey||tin.P.length);i++){   /* __acad3dV144: the survey's own points */
        if(flag[i]){devs.push(null);continue;}
        /* a plane through the neighbours, weighted 1/d^2, read at the point: a tilted ground is
           predicted exactly, even at the edge, where every neighbour is on one side */
        var S=[0,0,0,0,0,0],R=[0,0,0],dx,dy,w,cnt=0,pr=null,J=[],seenJ={},k2;
        for(k=0;k<nb[i].length;k++)if(!flag[nb[i][k]]){J.push(nb[i][k]);seenJ[nb[i][k]]=1;}
        /* a corner has two neighbours, too few for a plane: their neighbours too */
        if(J.length<3)for(k=0,k2=J.length;k<k2;k++)nb[J[k]].forEach(function(q){if(q!==i&&!flag[q]&&!seenJ[q]){seenJ[q]=1;J.push(q);}});
        ws=0;s=0;
        for(k=0;k<J.length;k++){
          j=J[k];
          dx=tin.P[j][0]-tin.P[i][0];dy=tin.P[j][1]-tin.P[i][1];d=dx*dx+dy*dy;if(!(d>1e-12))continue;
          w=1/d;cnt++;ws+=w;s+=w*tin.H[j];
          S[0]+=w;S[1]+=w*dx;S[2]+=w*dy;S[3]+=w*dx*dx;S[4]+=w*dx*dy;S[5]+=w*dy*dy;
          R[0]+=w*tin.H[j];R[1]+=w*tin.H[j]*dx;R[2]+=w*tin.H[j]*dy;
        }
        if(cnt>=3){
          var det=S[0]*(S[3]*S[5]-S[4]*S[4])-S[1]*(S[1]*S[5]-S[4]*S[2])+S[2]*(S[1]*S[4]-S[3]*S[2]);
          if(Math.abs(det)>1e-12*Math.max(1,S[0]*S[3]*S[5]))
            pr=(R[0]*(S[3]*S[5]-S[4]*S[4])-S[1]*(R[1]*S[5]-S[4]*R[2])+S[2]*(R[1]*S[4]-S[3]*R[2]))/det;
        }
        if(pr===null&&ws>0)pr=s/ws;   /* too few, or in a line: their weighted mean */
        dev=pr!==null?tin.H[i]-pr:null;devs.push(dev);
      }
      mad=bimMedian(devs.filter(function(v){return v!==null;}).map(Math.abs))*1.4826;
      thr=Math.max(BIM_SURVEY_TOL.bustMin,BIM_SURVEY_TOL.bustK*mad);
      for(i=0;i<devs.length;i++)if(devs[i]!==null&&Math.abs(devs[i])>best){best=Math.abs(devs[i]);bi=i;}
      if(bi<0||best<=thr)break;
      flag[bi]=1;out.push({i:bi,dev:devs[bi],thr:thr});
    }
    return out;
  }
  function bimSurveyCheckKey(o){
    var ct=bimCtxTerrainObj();
    return (o.rev||0)+':'+(o.survey||[]).length+':'+JSON.stringify(o.checks||[]).length+':'+JSON.stringify(o.control||[])+':'+
      (ct&&ct!==o?ct.id+'/'+(ct.rev||0)+'/'+ct.survey.length:'-')+':'+JSON.stringify(o.pos||[]);
  }
  /* the report */
  function bimSurveyCheck(o){
    if(!o||o.t!=='terrain'||!o.survey)return null;
    var key=bimSurveyCheckKey(o),c=A3D_SURVEYCHK[o.id];
    if(c&&c.key===key)return c.r;
    var tin=bimTerrainTin(o),src=o.source||{},u=BIM_SURVEY_UNITS[src.units]||1,items=[],r,i,h,x;
    function item(key,label,status,text,detail){items.push({key:key,label:label,status:status,text:text,detail:detail||null});}
    var skipped=src.skipped||[],dups=src.duplicates||[];
    item('read','Read',skipped.length?'warn':'pass',o.survey.length+' point'+(o.survey.length===1?'':'s')+' in the surface'+
      ((o.checks||[]).length?', '+o.checks.length+' check shot'+(o.checks.length===1?'':'s')+' kept out':'')+
      (skipped.length?'; line'+(skipped.length===1?' ':'s ')+skipped.slice(0,12).join(', ')+(skipped.length>12?' ...':'')+' could not be read':'; every line read'),{skipped:skipped.slice()});
    item('duplicates','Duplicates',dups.length?'warn':'pass',dups.length?dups.length+' at a place already surveyed, left out: '+dups.slice(0,10).join(', ')+(dups.length>10?' ...':''):'none',{names:dups.slice()});
    if(!tin||!tin.tris.length){item('fidelity','Surface','fail','could not be triangulated');}
    else{
      /* fidelity: the surface through every point */
      var maxr=0,wi=-1,out=0;
      var trimmed=0;
      for(i=0;i<(tin.nSurvey||tin.P.length);i++){   /* the survey's own points: not a breakline's */
        if(tin.outside&&tin.outside[i]){trimmed++;continue;}   /* __acad3dV144: outside the boundary, by design */
        h=bimTinHeightAt(tin,tin.P[i][0],tin.P[i][1]);
        if(h===null){out++;continue;}
        if(Math.abs(h-tin.H[i])>maxr){maxr=Math.abs(h-tin.H[i]);wi=i;}
      }
      item('fidelity','Through every point',(maxr<=BIM_SURVEY_TOL.fidelity&&!out)?'pass':'fail',
        (out?out+' point'+(out===1?'':'s')+' not on the surface':('largest difference '+(maxr*1000).toFixed(1)+' mm'+(wi>=0&&maxr>BIM_SURVEY_TOL.fidelity?' at '+bimSurveyName(o,wi):'')))+
        (trimmed?'; '+trimmed+' point'+(trimmed===1?'':'s')+' outside the boundary, left out':''),{max:maxr,outside:out,trimmed:trimmed});   /* __acad3dV144 */
      /* triangles */
      var degen=0,sliv=0,t2,A,B,C,ar,ang;
      for(t2=0;t2<tin.tris.length;t2++){
        A=tin.P[tin.tris[t2][0]];B=tin.P[tin.tris[t2][1]];C=tin.P[tin.tris[t2][2]];
        ar=Math.abs((B[0]-A[0])*(C[1]-A[1])-(C[0]-A[0])*(B[1]-A[1]))/2;
        if(!(ar>1e-9)){degen++;continue;}
        /* the smallest angle is opposite the shortest side, between the two longer: sin = 2 area / (their product) */
        var sd=[Math.hypot(B[0]-C[0],B[1]-C[1]),Math.hypot(A[0]-C[0],A[1]-C[1]),Math.hypot(A[0]-B[0],A[1]-B[1])].sort(function(p2,q2){return p2-q2;});
        ang=Math.asin(Math.min(1,2*ar/(sd[1]*sd[2])))*180/Math.PI;
        if(ang<1)sliv++;
      }
      item('triangles','Triangles',degen?'fail':'pass',tin.tris.length+' triangles'+(degen?', '+degen+' with no area':'')+(sliv?', '+sliv+' thin (under 1 degree) at the edge':''),{count:tin.tris.length,degenerate:degen,slivers:sliv});
      /* bust shots */
      var bs=bimSurveyBusts(tin);
      item('busts','Bust shots',bs.length?'fail':'pass',bs.length?bs.length+' far from their neighbours: '+bs.slice(0,8).map(function(b){
          return bimSurveyName(o,b.i)+' '+(b.dev>0?'+':'')+(b.dev/u).toFixed(2)+' '+(src.units||'m');}).join(', ')+(bs.length>8?' ...':''):'none far from its neighbours',
        {points:bs.map(function(b){return {name:bimSurveyName(o,b.i),desc:String(o.survey[b.i][4]||''),dev:b.dev,devUnits:b.dev/u};})});
      /* check shots */
      var ch=o.checks||[],res=[],sq=0,mx=0,mw=null,oo=0;
      for(i=0;i<ch.length;i++){
        x=bimObjOffset(o);
        h=bimTinHeightAt(tin,ch[i][0]+x[0],ch[i][1]+x[2]);
        if(h===null){oo++;res.push({name:String(ch[i][3]||''),dev:null});continue;}
        var dv=(ch[i][2]+x[1])-h;res.push({name:String(ch[i][3]||''),dev:dv});
        sq+=dv*dv;if(Math.abs(dv)>mx){mx=Math.abs(dv);mw=String(ch[i][3]||'');}
      }
      var nIn=res.length-oo,rmse=nIn?Math.sqrt(sq/nIn):null;
      item('checks','Check shots',!ch.length?'none':(nIn?(rmse<=BIM_SURVEY_TOL.checkPass?'pass':(rmse<=BIM_SURVEY_TOL.checkWarn?'warn':'fail')):'warn'),
        !ch.length?'none: code shots '+BIM_SURVEY_CHECK_CODE+' to keep them out of the surface and measure it':
        (nIn?'RMSE '+(rmse/u).toFixed(3)+' '+(src.units||'m')+', worst '+(mx/u).toFixed(3)+' at '+mw+' ('+nIn+' shot'+(nIn===1?'':'s')+(oo?', '+oo+' off the surface':'')+')':'every check shot is off the surface'),
        {rmse:rmse,max:mx,worst:mw,shots:res});
    }
    /* control */
    var ctl=o.control||[],cres=[],cf=0,bz=(src.base&&isFinite(src.base.z))?src.base.z:0,j;
    for(i=0;i<ctl.length;i++){
      var got=null,nm=String(ctl[i].p);
      for(j=0;j<o.survey.length;j++)if(String(o.survey[j][3])===nm){got=o.survey[j][2]+bimObjOffset(o)[1];break;}
      if(got===null)for(j=0;j<(o.checks||[]).length;j++)if(String(o.checks[j][3])===nm){got=o.checks[j][2]+bimObjOffset(o)[1];break;}
      var want=(ctl[i].z-bz)*u,df=got===null?null:got-want,ok=df!==null&&Math.abs(df)<=BIM_SURVEY_TOL.control;
      if(!ok)cf++;
      cres.push({p:nm,z:ctl[i].z,diff:df,ok:ok});
    }
    item('control','Control points',!ctl.length?'none':(cf?'fail':'pass'),!ctl.length?'none given: type the known elevations below':
      cres.map(function(q){return q.p+(q.diff===null?' not in the survey':(q.ok?' ok':' off by '+(q.diff/u).toFixed(3)+' '+(src.units||'m')));}).join('; '),{points:cres});
    /* against the public terrain */
    var ct=bimCtxTerrainObj(),ctin=ct&&ct!==o?bimTerrainTin(ct):null;
    if(!ctin||!tin)item('public','Public terrain','none',ct&&ct!==o?'could not be read':'none to compare with: get the site context');
    else{
      var dd=[],ps=[],gh;
      for(i=0;i<(tin.nSurvey||tin.P.length);i++){gh=bimTinHeightAt(ctin,tin.P[i][0],tin.P[i][1]);if(gh!==null){dd.push(tin.H[i]-gh);ps.push([gh,tin.H[i]]);}}
      if(dd.length<3)item('public','Public terrain','none','the survey and the public terrain overlap at '+dd.length+' point'+(dd.length===1?'':'s'));
      else{
        var off=bimMedian(dd),spr=bimMedian(dd.map(function(v){return Math.abs(v-off);}))*1.4826,mxg=0,myg=0,sxx=0,sxy=0,slope=null,note='',st='pass';
        for(i=0;i<ps.length;i++){mxg+=ps[i][0];myg+=ps[i][1];}mxg/=ps.length;myg/=ps.length;
        for(i=0;i<ps.length;i++){sxx+=(ps[i][0]-mxg)*(ps[i][0]-mxg);sxy+=(ps[i][0]-mxg)*(ps[i][1]-myg);}
        var rel=Math.sqrt(sxx/ps.length);
        if(rel>=0.25){slope=sxy/sxx;
          if(Math.abs(slope-1/0.3048)<0.45){note='the survey\u2019s relief is 3.28 times the public terrain\u2019s: elevations in feet read as metres?';st='warn';}
          else if(Math.abs(slope-0.3048)<0.08){note='the survey\u2019s relief is 0.30 of the public terrain\u2019s: metres read as feet?';st='warn';}}
        if(!note&&Math.abs(off)>BIM_SURVEY_TOL.offsetWarn){note='the survey sits '+Math.abs(off).toFixed(2)+' m '+(off>0?'above':'below')+' the public terrain: check the base elevation or the datum';st='warn';}
        item('public','Public terrain',st,(note?note+'; ':'')+dd.length+' points compared: offset '+(off>=0?'+':'')+off.toFixed(2)+' m, spread '+spr.toFixed(2)+' m'+
          (slope!==null?', relief ratio '+slope.toFixed(2):'')+' (public terrain is good to a few metres)',{n:dd.length,offset:off,spread:spr,slope:slope});
      }
    }
    var verdict='pass';
    for(i=0;i<items.length;i++){if(items[i].status==='fail'){verdict='fail';break;}if(items[i].status==='warn')verdict='warn';}
    r={id:o.id,name:o.name,verdict:verdict,items:items,units:src.units||'m',format:src.format||null,base:src.base||null,date:new Date().toISOString().slice(0,10),tol:BIM_SURVEY_TOL};
    A3D_SURVEYCHK[o.id]={key:key,r:r};
    return r;
  }
  function bimSurveyItem(r,key){var i;for(i=0;r&&i<r.items.length;i++)if(r.items[i].key===key)return r.items[i];return null;}
  /* control points, typed as "105=30.000, 201=28.45": one undo step */
  function bimSurveySetControl(o,text){
    if(!o||o.t!=='terrain')return false;
    var parts=String(text==null?'':text).split(/[,;\n]+/),out=[],bad=[],i,m;
    for(i=0;i<parts.length;i++){
      var s=parts[i].replace(/^\s+|\s+$/g,'');if(!s)continue;
      m=/^([^=\s]+)\s*=\s*(-?\d+(\.\d+)?)$/.exec(s);
      if(m)out.push({p:m[1],z:parseFloat(m[2])});else bad.push(s);
    }
    if(bad.length){a3dToast('A control point is name=elevation, like 105=30.000: '+bad.slice(0,3).join(', ')+' is not');refreshProps();return false;}
    if(JSON.stringify(out)===JSON.stringify(o.control||[]))return true;
    pushUndo();
    if(out.length)o.control=out;else delete o.control;
    refreshProps();saveSoon();
    var r=bimSurveyCheck(o),c=bimSurveyItem(r,'control');
    a3dToast(o.name+': control '+(c?c.text:''));
    return true;
  }
  /* the report as a page to keep with the project */
  function bimSurveyReportHtml(o){
    var r=bimSurveyCheck(o),h,i,it,col={pass:'#2e7d32',warn:'#b26a00',fail:'#c62828',none:'#666'};
    if(!r)return '';
    function e(s){return bimEsc(String(s==null?'':s));}
    h='<!doctype html><html><head><meta charset="utf-8"><title>Survey check: '+e(r.name)+'</title><style>body{font:14px/1.45 system-ui,sans-serif;margin:24px;color:#222}'+
      'table{border-collapse:collapse;width:100%}td,th{border-bottom:1px solid #ddd;padding:6px 8px;text-align:left;vertical-align:top}.s{font-weight:600;text-transform:uppercase}</style></head><body>'+
      '<h1>Survey check: '+e(r.name)+'</h1><p>'+e(r.date)+' &middot; '+e((r.format||'surface')+', '+r.units)+(r.base?' &middot; base N '+e(r.base.n)+', E '+e(r.base.e)+', Z '+e(r.base.z):'')+
      '</p><p class="s" style="color:'+col[r.verdict]+'">'+e(r.verdict)+'</p><table><tr><th>Check</th><th>Result</th><th></th></tr>';
    for(i=0;i<r.items.length;i++){it=r.items[i];h+='<tr><td>'+e(it.label)+'</td><td class="s" style="color:'+col[it.status]+'">'+e(it.status)+'</td><td>'+e(it.text)+'</td></tr>';}
    h+='</table><p>Tolerances: surface '+(r.tol.fidelity*1000)+' mm; bust shots over '+r.tol.bustMin+' m and '+r.tol.bustK+' times the typical scatter; check shots RMSE '+
      r.tol.checkPass+' m (pass), '+r.tol.checkWarn+' m (warn); control '+r.tol.control+' m; public terrain offset '+r.tol.offsetWarn+' m.</p></body></html>';
    return h;
  }
  function bimSurveyReportExport(o){
    var h=bimSurveyReportHtml(o);
    if(!h){a3dToast('Select a surface to report on');return false;}
    bimTriggerDownload(h,bimFileStem()+'-'+String(o.name).replace(/[^\w\-]+/g,'_')+'-survey-check.html','text/html');
    a3dToast('Survey check report saved');
    return true;
  }
  /* __acad3dV108: a terrain surface -- its survey points in model coordinates, [x, z, y, point,
     description], and where they came from. Duplicate plan positions keep the first point. */
  function bimCreateTerrain(model,src,skipUndo){
    var seen={},keep=[],dup=0,i,k,tris,o,dupNames=[];
    for(i=0;i<model.length;i++){
      k=Math.round(model[i][0]*1e6)+'_'+Math.round(model[i][1]*1e6);
      if(seen[k]){dup++;dupNames.push(String(model[i][3]||('#'+(i+1))));continue;}   /* __acad3dV138: named */
      seen[k]=1;keep.push(model[i]);
    }
    if(keep.length<3){a3dToast('A surface needs at least 3 points in different places');return null;}
    try{tris=bimDelaunay(keep.map(function(p){return [p[0],p[1]];}));}
    catch(eD){console.warn('[BIM] survey triangulation',eD);a3dToast('Those points could not be triangulated - see the console');return null;}
    if(!tris.length){a3dToast('Those points all lie on one line, so they make no surface');return null;}
    if(!skipUndo)pushUndo();
    if(src&&typeof src==='object'&&dupNames.length)src.duplicates=dupNames.slice(0,200);   /* __acad3dV138 */
    A3D.counts.terrain=(A3D.counts.terrain||0)+1;
    o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'terrain',name:'Surface_'+A3D.counts.terrain,col:'#b08559',
      pos:[0,0,0],layer:A3D.activeLayer,survey:keep,source:src||null,rev:1};
    A3D.objs.push(o);
    A3D.sel=o.id;A3D.sel2=null;A3D.selSet=[o.id];
    refreshTree();refreshProps();paint();saveSoon();
    a3dToast(o.name+': '+keep.length+' points, '+tris.length+' triangles'+(dup?(', '+dup+' duplicate'+(dup===1?'':'s')+' skipped'):''));
    return o;
  }
  function bimSetTerrainInterval(o,val){
    var v=String(val==null?'':val).replace(/^\s+|\s+$/g,''),n=parseFloat(v);
    if(!o||o.t!=='terrain')return false;
    if(v!==''&&!(isFinite(n)&&n>0)){a3dToast('A contour interval is a number of metres above 0');refreshProps();return false;}
    if(v===''?o.interval==null:o.interval===n)return true;
    pushUndo();
    if(v==='')delete o.interval;else o.interval=n;
    refreshProps();paint();saveSoon();
    a3dToast(o.name+': contours every '+bimTerrainInterval(o,bimTerrainTin(o))+' m'+(v===''?' (from the relief)':''));
    return true;
  }
  function bimDecimals(step){var s=String(step),p=s.indexOf('.');return p<0?0:Math.min(3,s.length-p-1);}
  /* Plan only: the TIN faintly, the contours over it, index contours heavier and labelled on
     their longest segment, and the survey points. */
  function drawTerrain(ctx,V,W,H){
    A3D.lastTerrainDrawn=null;A3D.lastSpotsDrawn=null;   /* __acad3dV145 */
    if(!bimCameraIsPlan())return;   /* __acad3dV119: flat is not plan -- an elevation is flat */
    var drawn=[],i,j,k,s,o,tin,step,cs,sel,sp,a,b,c,best,bl,L,txt,ang,nseg,legendFor=null;
    A3D.lastTerrainLegend=null;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(o.t!=='terrain')continue;
      if(!bimLayerShown(o))continue;   /* __acad3dV121 */
      ctx.save();
      ctx.globalAlpha*=bimLayerAlpha(o);   /* __acad3dV121: the layer's transparency */
      try{
        tin=bimTerrainTin(o);step=bimTerrainInterval(o,tin);cs=bimContours(tin,step);
        sel=(o.id===A3D.sel||(A3D.selSet&&A3D.selSet.indexOf(o.id)>=0));
        sp=tin.P.map(function(p){return toScreen([p[0],0,p[1]],V,W,H);});
        var tb=o.tview?(o.tview==='cutfill'?bimBandsOf(o,'cutfill'):bimTerrainBands(tin,o.tview)):null;   /* __acad3dV144: coloured by its bands */
        var sup=!o.grading&&!!bimTerrainSuperseded(o);   /* __acad3dV145: an existing surface under a proposed one */
        if(tb){
          bimDrawBandTris(ctx,tin,tb,sp,0.55);   /* __acad3dV148: shared with the terrain's layers */
          if(!legendFor||sel)legendFor={name:o.name,view:o.tview,bands:tb.bands};
        }
        ctx.setLineDash([]);ctx.lineWidth=0.6;ctx.strokeStyle=sel?'rgba(78,161,255,0.35)':'rgba(176,133,89,0.2)';
        ctx.beginPath();
        for(j=0;j<tin.tris.length;j++){
          a=sp[tin.tris[j][0]];b=sp[tin.tris[j][1]];c=sp[tin.tris[j][2]];
          if(!a||!b||!c)continue;
          ctx.moveTo(a[0],a[1]);ctx.lineTo(b[0],b[1]);ctx.lineTo(c[0],c[1]);ctx.closePath();
        }
        ctx.stroke();
        nseg=0;
        for(j=0;j<cs.length;j++){
          ctx.lineWidth=cs[j].index?1.5:0.8;ctx.strokeStyle=sel?'#4ea1ff':o.grading?(cs[j].index?'#a5d47f':'#6f9a52'):(cs[j].index?'#c89a6a':'#8f7050');
          ctx.setLineDash(sup?[5,4]:[]);   /* __acad3dV145: proposed green, the existing under it dashed */
          ctx.beginPath();best=null;bl=0;
          for(k=0;k<cs[j].segs.length;k++){
            a=toScreen([cs[j].segs[k][0][0],0,cs[j].segs[k][0][1]],V,W,H);b=toScreen([cs[j].segs[k][1][0],0,cs[j].segs[k][1][1]],V,W,H);
            if(!a||!b)continue;
            ctx.moveTo(a[0],a[1]);ctx.lineTo(b[0],b[1]);nseg++;
            L=Math.sqrt((b[0]-a[0])*(b[0]-a[0])+(b[1]-a[1])*(b[1]-a[1]));
            if(L>bl){bl=L;best=[a,b];}
          }
          ctx.stroke();
          if(cs[j].index&&best&&bl>30){
            txt=cs[j].level.toFixed(bimDecimals(step));
            ang=Math.atan2(best[1][1]-best[0][1],best[1][0]-best[0][0]);
            if(ang>Math.PI/2)ang-=Math.PI;else if(ang<-Math.PI/2)ang+=Math.PI;
            ctx.save();ctx.translate((best[0][0]+best[1][0])/2,(best[0][1]+best[1][1])/2);ctx.rotate(ang);
            ctx.font='10px sans-serif';ctx.textAlign='center';ctx.textBaseline='middle';
            ctx.fillStyle='#1d2024';ctx.fillRect(-ctx.measureText(txt).width/2-2,-6,ctx.measureText(txt).width+4,12);
            ctx.fillStyle='#e6c9a8';ctx.fillText(txt,0,0);ctx.restore();
          }
        }
        ctx.setLineDash([]);
        /* __acad3dV144: breaklines bold, the boundary dashed */
        if(tin.constraints.length){
          ctx.setLineDash([]);ctx.lineWidth=o.grading?0.9:1.8;ctx.strokeStyle=sel?'#82c0ff':o.grading?'#9ccc65':'#e0795a';ctx.beginPath();
          for(j=0;j<tin.constraints.length;j++){a=sp[tin.constraints[j][0]];b=sp[tin.constraints[j][1]];if(a&&b){ctx.moveTo(a[0],a[1]);ctx.lineTo(b[0],b[1]);}}
          ctx.stroke();
        }
        if(o.boundary&&o.boundary.length>=3){
          var tq=bimObjOffset(o);
          ctx.setLineDash([7,4]);ctx.lineWidth=1.4;ctx.strokeStyle=sel?'#4ea1ff':'#f0d0a8';ctx.beginPath();
          for(j=0;j<=o.boundary.length;j++){a=toScreen([o.boundary[j%o.boundary.length][0]+tq[0],0,o.boundary[j%o.boundary.length][1]+tq[2]],V,W,H);if(!a)continue;if(j)ctx.lineTo(a[0],a[1]);else ctx.moveTo(a[0],a[1]);}
          ctx.stroke();ctx.setLineDash([]);
        }
        ctx.fillStyle=sel?'#4ea1ff':'#d9b38c';ctx.strokeStyle=ctx.fillStyle;ctx.lineWidth=1;
        for(j=0;j<sp.length;j++)if(sp[j]){if(tin.outside&&tin.outside[j])ctx.strokeRect(sp[j][0]-1.5,sp[j][1]-1.5,3,3);else ctx.fillRect(sp[j][0]-1.5,sp[j][1]-1.5,3,3);}
        var arrows=o.arrows?bimDrawSlopeArrows(ctx,tin,V,W,H,sel):null;   /* __acad3dV145 */
        drawn.push({id:o.id,step:step,levels:cs.map(function(x){return x.level;}),segments:nseg,triangles:tin.tris.length,arrows:arrows,grading:!!o.grading,dashed:sup,
          view:o.tview||'',bands:tb?tb.bands.map(function(x){return {label:x.label,col:x.col,area:x.area};}):null,constraints:tin.constraints.length,boundary:!!(o.boundary&&o.boundary.length>=3)});
      }catch(e){
        console.warn('[BIM] terrain',e);
        if(!A3D.terrainWarned){A3D.terrainWarned=true;a3dToast('A terrain surface could not be drawn');}
      }
      ctx.restore();
    }
    try{A3D.lastSpotsDrawn=bimDrawSpots(ctx,V,W,H);}catch(eS){console.warn('[BIM] spot elevations',eS);}   /* __acad3dV145 */
    if(legendFor){try{A3D.lastTerrainLegend=bimTerrainLegend(ctx,W,H,legendFor);}catch(eL){console.warn('[BIM] terrain legend',eL);}}   /* __acad3dV144 */
    A3D.lastTerrainDrawn=drawn;
  }
  /* __acad3dV108: building pads. A closed outline with a Pad Elevation is a flat pad; it is
     measured against each surface it lies over. Area off the surface is reported, not guessed. */
  /* __acad3dV145: a pad's cut or fill slope, as horizontal units per vertical unit */
  function bimSetPadSlope(o,which,val){
    var v=String(val==null?'':val).replace(/^\s+|\s+$/g,''),n=parseFloat(v),key=which==='cutslope'?'cutSlope':'fillSlope';
    if(!bimIsPad(o))return false;
    if(v!==''&&!(isFinite(n)&&n>0&&n<=100)){a3dToast('A slope is the horizontal run for a rise of one, over 0 (2 is 2:1)');refreshProps();return false;}
    if(v===''?o[key]==null:o[key]===n)return true;
    pushUndo();
    if(v==='')delete o[key];else o[key]=n;
    refreshProps();paint();saveSoon();bimAnalyzeRefresh();
    return true;
  }
  function bimSetGradeElev(o,val){
    var v=String(val==null?'':val).replace(/^\s+|\s+$/g,''),n=parseFloat(v);
    if(!o||o.t!=='sketch'||o.closed===false||bimIsPoint(o)){a3dToast('Only a closed outline can be a pad');return false;}
    if(v!==''&&!isFinite(n)){a3dToast('A pad elevation is a number of metres');refreshProps();return false;}
    if(v===''?o.gradeElev==null:o.gradeElev===n)return true;
    pushUndo();
    if(v==='')delete o.gradeElev;else o.gradeElev=n;
    refreshProps();paint();saveSoon();
    a3dToast(o.name+(v===''?' is no longer a pad':(' is a pad at '+n+' m')));
    return true;
  }
  function bimEarthwork(){
    var rows=[],i,j,o,pl,py,q,r,hit,ters=A3D.objs.filter(function(t){return t.t==='terrain'&&t.survey;});
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(o.t!=='sketch'||o.closed===false||bimIsPoint(o)||!isFinite(parseFloat(o.gradeElev)))continue;
      q=bimObjOffset(o);pl=bimSketchOutline(o).map(function(p){return [p[0]+q[0],p[1]+q[2]];});py=parseFloat(o.gradeElev);hit=false;
      if(pl.length<3)continue;
      for(j=0;j<ters.length;j++){
        try{r=bimCutFill(bimTerrainTin(ters[j]),pl,py);}
        catch(eW){
          console.warn('[BIM] earthwork',eW);hit=true;
          rows.push({pad:o.name,padId:o.id,surface:ters[j].name,surfaceId:ters[j].id,padElev:py,padArea:bimPolyArea(pl),onSurface:'',cut:'',fill:'',net:'',method:'',note:'could not be measured - see the console'});
          continue;
        }
        if(!(r.onSurface>1e-9))continue;
        hit=true;
        rows.push({pad:o.name,padId:o.id,surface:ters[j].name,surfaceId:ters[j].id,padElev:py,padArea:r.padArea,onSurface:r.onSurface,
          cut:r.cut,fill:r.fill,net:r.net,method:'TIN prism',note:r.outside>0.005?(r.outside.toFixed(2)+' m\u00b2 off the surface, not measured'):''});
      }
      if(!hit)rows.push({pad:o.name,padId:o.id,surface:'',surfaceId:'',padElev:py,padArea:bimPolyArea(pl),onSurface:0,cut:'',fill:'',net:'',method:'',note:'no surface under it'});
    }
    return rows;
  }
