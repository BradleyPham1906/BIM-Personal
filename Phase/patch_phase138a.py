"""patch_phase138a.py -- V138: verify the survey, the engine.

The owner: "build the genesis of a good foundation so data can be verified every time". Every
surface gets one report, worked out the same way every time:
  read        every line read, or skipped by its line number; duplicates by point name
  fidelity    the surface passes through every survey point (1 mm)
  triangles   none degenerate; slivers counted
  bust shots  a point far from what its neighbours predict (a plane through its TIN neighbours,
              weighted by inverse squared distance); the worst is set aside and the rest looked at again, so one bust does not
              make its neighbours suspects
  check shots shots coded CHK (by default) are kept out of the surface and measured against it:
              their RMSE and the worst
  control     points whose elevation is known, typed in, checked to 2 cm
  public      against the site context's terrain: the offset (a base elevation or datum off) and the
              relief ratio (feet read as metres, or metres as feet)
A verdict: fail if any check fails, warn if any warns, else pass. The report is cached against the
survey, the checks, the control and the context terrain."""
NAME = 'patch_phase138a.py'
BASE = '3d63565958383183ad0a552210c7f21a45364d285396495d2d76dc61a6780b82'
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def esc(s):
    return ''.join(ch if ord(ch) < 128 else '\\u%04x' % ord(ch) for ch in s)


def rep(old, new, n=1):
    global t
    new = esc(new)
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: %d occurrences, expected %d: %r' % (c, n, old[:90]))
    t = t.replace(old, new)


ENGINE = r"""  /* ================= __acad3dV138: verify the survey ================= */
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
      for(i=0;i<tin.P.length;i++){
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
      for(i=0;i<tin.P.length;i++){
        h=bimTinHeightAt(tin,tin.P[i][0],tin.P[i][1]);
        if(h===null){out++;continue;}
        if(Math.abs(h-tin.H[i])>maxr){maxr=Math.abs(h-tin.H[i]);wi=i;}
      }
      item('fidelity','Through every point',(maxr<=BIM_SURVEY_TOL.fidelity&&!out)?'pass':'fail',
        out?out+' point'+(out===1?'':'s')+' not on the surface':('largest difference '+(maxr*1000).toFixed(1)+' mm'+(wi>=0&&maxr>BIM_SURVEY_TOL.fidelity?' at '+bimSurveyName(o,wi):'')),{max:maxr,outside:out});
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
      for(i=0;i<tin.P.length;i++){gh=bimTinHeightAt(ctin,tin.P[i][0],tin.P[i][1]);if(gh!==null){dd.push(tin.H[i]-gh);ps.push([gh,tin.H[i]]);}}
      if(dd.length<3)item('public','Public terrain','none','the survey and the public terrain overlap at '+dd.length+' point'+(dd.length===1?'':'s'));
      else{
        var off=bimMedian(dd),spr=bimMedian(dd.map(function(v){return Math.abs(v-off);}))*1.4826,mxg=0,myg=0,sxx=0,sxy=0,slope=null,note='',st='pass';
        for(i=0;i<ps.length;i++){mxg+=ps[i][0];myg+=ps[i][1];}mxg/=ps.length;myg/=ps.length;
        for(i=0;i<ps.length;i++){sxx+=(ps[i][0]-mxg)*(ps[i][0]-mxg);sxy+=(ps[i][0]-mxg)*(ps[i][1]-myg);}
        var rel=Math.sqrt(sxx/ps.length);
        if(rel>=0.25){slope=sxy/sxx;
          if(Math.abs(slope-1/0.3048)<0.45){note='the survey’s relief is 3.28 times the public terrain’s: elevations in feet read as metres?';st='warn';}
          else if(Math.abs(slope-0.3048)<0.08){note='the survey’s relief is 0.30 of the public terrain’s: metres read as feet?';st='warn';}}
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
"""

rep("""  /* __acad3dV108: a terrain surface -- its survey points in model coordinates, [x, z, y, point,
     description], and where they came from. Duplicate plan positions keep the first point. */""",
    ENGINE + """  /* __acad3dV108: a terrain surface -- its survey points in model coordinates, [x, z, y, point,
     description], and where they came from. Duplicate plan positions keep the first point. */""")
# duplicates kept by name in the source
rep("""    var seen={},keep=[],dup=0,i,k,tris,o;
    for(i=0;i<model.length;i++){
      k=Math.round(model[i][0]*1e6)+'_'+Math.round(model[i][1]*1e6);
      if(seen[k]){dup++;continue;}""", """    var seen={},keep=[],dup=0,i,k,tris,o,dupNames=[];
    for(i=0;i<model.length;i++){
      k=Math.round(model[i][0]*1e6)+'_'+Math.round(model[i][1]*1e6);
      if(seen[k]){dup++;dupNames.push(String(model[i][3]||('#'+(i+1))));continue;}   /* __acad3dV138: named */""")
rep("""    if(!skipUndo)pushUndo();
    A3D.counts.terrain=(A3D.counts.terrain||0)+1;""", """    if(!skipUndo)pushUndo();
    if(src&&typeof src==='object'&&dupNames.length)src.duplicates=dupNames.slice(0,200);   /* __acad3dV138 */
    A3D.counts.terrain=(A3D.counts.terrain||0)+1;""")
# check shots kept out of the surface at import
rep("""  function bimImportSurvey(res,fmt,units,base){
    try{
      pushUndo();
      A3D.site.surveyBase={n:base.n,e:base.e,z:base.z,units:units};
      var model=bimSurveyToModel(res.points,units,base,bimTrueNorthDeg());
      var o=bimCreateTerrain(model,{format:fmt,units:units,base:{n:base.n,e:base.e,z:base.z},skipped:res.bad.slice(0,50)},true);""",
    """  function bimImportSurvey(res,fmt,units,base,checkCode){
    try{
      pushUndo();
      A3D.site.surveyBase={n:base.n,e:base.e,z:base.z,units:units};
      /* __acad3dV138: shots coded as checks are kept out of the surface, to measure it */
      var code=String(checkCode==null?BIM_SURVEY_CHECK_CODE:checkCode).replace(/^\\s+|\\s+$/g,'').toUpperCase(),pts=[],chk=[],q;
      for(q=0;q<res.points.length;q++){
        if(code&&String(res.points[q].d||'').replace(/^\\s+/,'').toUpperCase().indexOf(code)===0)chk.push(res.points[q]);else pts.push(res.points[q]);
      }
      var model=bimSurveyToModel(pts,units,base,bimTrueNorthDeg());
      var o=bimCreateTerrain(model,{format:fmt,units:units,base:{n:base.n,e:base.e,z:base.z},skipped:res.bad.slice(0,50),checkCode:code},true);
      if(o&&chk.length)o.checks=bimSurveyToModel(chk,units,base,bimTrueNorthDeg());""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
