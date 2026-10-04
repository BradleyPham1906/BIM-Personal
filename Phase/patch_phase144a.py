"""patch_phase144a.py -- V144: terrain -- breaklines, boundaries, slope/elevation/aspect, LandXML.

- A surface can carry its own triangles (`o.faces`, from a LandXML file): kept as they are, never
  re-triangulated, so a Civil 3D surface comes in as it was.
- Breaklines: lines the triangles may not cross. Sketched ones take the surface's heights at their
  vertices (a survey point already there keeps its own); survey points coded BL1, BL2 ... (the code
  at the start of the description) join in file order as 3D breaklines. Each segment is forced into
  the triangulation by edge flips (Sloan 1993); a segment that crosses another breakline is
  reported, not faked.
- A boundary: an outer outline; triangles outside it are dropped, its edges are forced in too.
- Analysis bands: slope (%), elevation and aspect, triangle by triangle -- each triangle is a plane,
  so its slope and the way it faces are exact -- with the plan area of each band.
- LandXML 1.2: a surface out (points, faces, breaklines, boundary, in the survey's own coordinates
  and units) and in (its own faces kept).
- V138's survey check leaves out the points a boundary has trimmed away, and says how many."""
NAME = 'patch_phase144a.py'
BASE = 'fbb7109fe64df201030f6b2ceabc6d8a23fe13fc53f60192ef7684fe1fb5b65e'
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


# ---- the TIN: own faces, breaklines, a boundary ----
rep("""  function bimTerrainTin(o){
    if(!o||o.t!=='terrain'||!o.survey)return null;
    var key=(o.rev||0)+':'+o.survey.length,c=BIM_TIN_CACHE[o.id],q=bimObjOffset(o);
    if(!c||c.key!==key)c=BIM_TIN_CACHE[o.id]={key:key,tris:bimDelaunay(o.survey.map(function(s){return [s[0],s[1]];}))};
    return {P:o.survey.map(function(s){return [s[0]+q[0],s[1]+q[2]];}),H:o.survey.map(function(s){return s[2]+q[1];}),tris:c.tris};
  }""", """  function bimTerrainTin(o){
    if(!o||o.t!=='terrain'||!o.survey)return null;
    var key=(o.rev||0)+':'+o.survey.length+':'+(o.faces?o.faces.length:'-')+':'+JSON.stringify(o.breaklines||[])+':'+JSON.stringify(o.boundary||[]),
      c=BIM_TIN_CACHE[o.id],q=bimObjOffset(o);
    if(!c||c.key!==key)c=BIM_TIN_CACHE[o.id]=bimTinBuild(o,key);   /* __acad3dV144: own faces, breaklines, a boundary */
    var P=o.survey.map(function(s){return [s[0]+q[0],s[1]+q[2]];}),H=o.survey.map(function(s){return s[2]+q[1];});
    c.extra.forEach(function(e){P.push([e[0]+q[0],e[1]+q[2]]);H.push(e[2]+q[1]);});
    return {P:P,H:H,tris:c.tris,outside:c.outside,constraints:c.constraints,unforced:c.unforced,ownFaces:!!c.ownFaces,nSurvey:o.survey.length};
  }""")

ENGINE = r"""  /* ================= __acad3dV144: breaklines, boundaries, own faces =================
     The triangles of a surface: its own (o.faces, from LandXML) as they are; else Delaunay of its
     points and of the breakline and boundary vertices, each breakline and boundary segment then
     forced in by flipping the edges that cross it (Sloan, 1993), and the triangles outside the
     boundary dropped. In local (survey) coordinates; bimTerrainTin adds the object's offset. */
  var BIM_BRK_CODE=/^\s*(BL|BRK)[\s_-]*([0-9A-Za-z]+)/i;
  function bimSegCross(a,b,c,d){
    function o3(p,q,r){var v=(q[0]-p[0])*(r[1]-p[1])-(q[1]-p[1])*(r[0]-p[0]);return Math.abs(v)<1e-12?0:(v>0?1:-1);}
    var d1=o3(a,b,c),d2=o3(a,b,d),d3=o3(c,d,a),d4=o3(c,d,b);
    return d1*d2<0&&d3*d4<0;
  }
  /* the survey's own coded breaklines: index lists, in file order */
  function bimSurveyBreaklines(o){
    var L={},order=[],i,m;
    for(i=0;i<o.survey.length;i++){
      m=BIM_BRK_CODE.exec(String(o.survey[i][4]||''));
      if(!m)continue;
      var k=m[1].toUpperCase()+m[2].toUpperCase();
      if(!L[k]){L[k]=[];order.push(k);}
      L[k].push(i);
    }
    return order.map(function(k){return {name:k,idx:L[k]};}).filter(function(b){return b.idx.length>=2;});
  }
  function bimTinBuild(o,key){
    var S=o.survey,P=S.map(function(s){return [s[0],s[1]];}),H=S.map(function(s){return s[2];}),extra=[],cons=[],unforced=[],i,j,k;
    var res={key:key,tris:[],extra:extra,outside:null,constraints:cons,unforced:unforced,ownFaces:false};
    if(o.faces&&o.faces.length){
      res.tris=o.faces.filter(function(f){return f[0]<S.length&&f[1]<S.length&&f[2]<S.length;}).map(function(f){return f.slice(0,3);});
      res.ownFaces=true;
      return res;
    }
    var base=bimDelaunay(P),baseTin={P:P,H:H,tris:base};
    if(!(o.breaklines&&o.breaklines.length)&&!(o.boundary&&o.boundary.length>=3)&&!bimSurveyBreaklines(o).length){res.tris=base;return res;}
    /* a vertex of a line: a survey point already there, else a new point at the given or the surface's height */
    var near={};
    for(i=0;i<P.length;i++)near[Math.round(P[i][0]*100)+'_'+Math.round(P[i][1]*100)]=i;
    function vtx(p){
      var kk=Math.round(p[0]*100)+'_'+Math.round(p[1]*100);
      if(near.hasOwnProperty(kk))return near[kk];
      var h=(p.length>2&&isFinite(p[2])&&p[2]!==null)?p[2]:bimTinHeightAt(baseTin,p[0],p[1]);
      if(h===null||!isFinite(h))return -1;
      near[kk]=P.length;P.push([p[0],p[1]]);H.push(h);extra.push([p[0],p[1],h]);
      return near[kk];
    }
    var L2=[];
    function hOf(p){return (p.length>2&&p[2]!==null&&isFinite(p[2]))?p[2]:null;}
    (o.breaklines||[]).forEach(function(bl){L2.push({name:bl.name||'breakline',pts:(bl.pts||[]).map(function(p){return [p[0],p[1],hOf(p)];})});});
    bimSurveyBreaklines(o).forEach(function(bl){L2.push({name:bl.name,pts:bl.idx.map(function(ii){return [P[ii][0],P[ii][1],H[ii]];})});});
    var bnd=(o.boundary&&o.boundary.length>=3)?o.boundary:null;
    if(bnd)L2.push({name:'boundary',pts:bnd.concat([bnd[0]]).map(function(p){return [p[0],p[1],null];})});
    /* where two lines cross, both get a vertex there: else neither could be held */
    var cuts=L2.map(function(l){return l.pts.map(function(){return [];});}),la,lb,sa,sb;
    function lerpH(p,q,u){return p[2]!==null&&q[2]!==null?p[2]+(q[2]-p[2])*u:null;}
    for(la=0;la<L2.length;la++)for(sa=0;sa+1<L2[la].pts.length;sa++)for(lb=la;lb<L2.length;lb++)for(sb=(lb===la?sa+2:0);sb+1<L2[lb].pts.length;sb++){
      var A0=L2[la].pts[sa],A1=L2[la].pts[sa+1],B0=L2[lb].pts[sb],B1=L2[lb].pts[sb+1];
      if(!bimSegCross(A0,A1,B0,B1))continue;
      var den=(A1[0]-A0[0])*(B1[1]-B0[1])-(A1[1]-A0[1])*(B1[0]-B0[0]);
      if(Math.abs(den)<1e-15)continue;
      var ta=((B0[0]-A0[0])*(B1[1]-B0[1])-(B0[1]-A0[1])*(B1[0]-B0[0]))/den,tb=((B0[0]-A0[0])*(A1[1]-A0[1])-(B0[1]-A0[1])*(A1[0]-A0[0]))/den;
      var X=[A0[0]+(A1[0]-A0[0])*ta,A0[1]+(A1[1]-A0[1])*ta],hX=lerpH(A0,A1,ta);
      if(hX===null)hX=lerpH(B0,B1,tb);
      cuts[la][sa].push([ta,X[0],X[1],hX]);cuts[lb][sb].push([tb,X[0],X[1],hX]);
    }
    var lines=L2.map(function(l,li){
      var pts=[];
      l.pts.forEach(function(p,pi){pts.push(p);cuts[li][pi].sort(function(x,y){return x[0]-y[0];}).forEach(function(c){pts.push([c[1],c[2],c[3]]);});});
      return {name:l.name,idx:pts.map(vtx)};
    });
    var T=extra.length?bimDelaunay(P):base;
    T=T.map(function(t){return t.slice();});
    /* force each segment in */
    function hasEdge(a,b){for(var t=0;t<T.length;t++){var x=T[t];if((x[0]===a||x[1]===a||x[2]===a)&&(x[0]===b||x[1]===b||x[2]===b))return true;}return false;}
    function isCons(a,b){for(var q=0;q<cons.length;q++)if((cons[q][0]===a&&cons[q][1]===b)||(cons[q][0]===b&&cons[q][1]===a))return true;return false;}
    function crossing(a,b){
      var out=[],seen={},t,e,u,v,kk;
      for(t=0;t<T.length;t++)for(e=0;e<3;e++){
        u=T[t][e];v=T[t][(e+1)%3];if(u===a||u===b||v===a||v===b)continue;
        kk=u<v?u+'_'+v:v+'_'+u;if(seen[kk])continue;
        if(bimSegCross(P[a],P[b],P[u],P[v])){seen[kk]=1;out.push([u,v]);}
      }
      return out;
    }
    /* a point lying on the segment splits it */
    function onSeg(a,b){
      var best=-1,bt=2,m;
      for(m=0;m<P.length;m++){
        if(m===a||m===b)continue;
        var dx=P[b][0]-P[a][0],dz=P[b][1]-P[a][1],L2=dx*dx+dz*dz,tt=((P[m][0]-P[a][0])*dx+(P[m][1]-P[a][1])*dz)/L2;
        if(tt<=1e-9||tt>=1-1e-9)continue;
        var ex=P[a][0]+dx*tt-P[m][0],ez=P[a][1]+dz*tt-P[m][1];
        if(ex*ex+ez*ez<1e-8&&tt<bt){bt=tt;best=m;}
      }
      return best;
    }
    function force(a,b,name){
      if(a<0||b<0||a===b)return;
      var w=onSeg(a,b);
      if(w>=0){force(a,w,name);force(w,b,name);return;}
      cons.push([a,b]);
      if(hasEdge(a,b))return;
      var Q=crossing(a,b),guard=0;
      while(Q.length&&guard++<20000){
        var e=Q.shift(),u=e[0],v=e[1],t1=-1,t2=-1,t;
        if(isCons(u,v)){unforced.push({name:name,from:a,to:b,why:'it crosses another breakline'});cons.pop();return;}
        for(t=0;t<T.length;t++){var x=T[t];if((x[0]===u||x[1]===u||x[2]===u)&&(x[0]===v||x[1]===v||x[2]===v)){if(t1<0)t1=t;else t2=t;}}
        if(t1<0||t2<0)continue;
        var p=T[t1][0]+T[t1][1]+T[t1][2]-u-v,qv=T[t2][0]+T[t2][1]+T[t2][2]-u-v;
        /* which side: [u,v,p] counter-clockwise has p left of u->v */
        var cr=(P[v][0]-P[u][0])*(P[p][1]-P[u][1])-(P[v][1]-P[u][1])*(P[p][0]-P[u][0]);
        if(cr<0){var sw=p;p=qv;qv=sw;}
        /* the quadrilateral u, q, v, p must be strictly convex to flip */
        var Qd=[P[u],P[qv],P[v],P[p]],conv=true;
        for(k=0;k<4;k++){var A=Qd[k],B=Qd[(k+1)%4],C=Qd[(k+2)%4];if((B[0]-A[0])*(C[1]-B[1])-(B[1]-A[1])*(C[0]-B[0])<=1e-12){conv=false;break;}}
        if(!conv){Q.push(e);continue;}
        T[t1]=[u,qv,p];T[t2]=[qv,v,p];
        if(!(p===a&&qv===b)&&!(p===b&&qv===a)&&bimSegCross(P[a],P[b],P[p],P[qv]))Q.push([p,qv]);
      }
      if(!hasEdge(a,b)){unforced.push({name:name,from:a,to:b,why:'the triangles could not be turned to it'});cons.pop();}
    }
    lines.forEach(function(L){for(j=0;j+1<L.idx.length;j++){if(L.idx[j]<0||L.idx[j+1]<0){unforced.push({name:L.name,why:'a vertex is off the surface'});continue;}force(L.idx[j],L.idx[j+1],L.name);}});
    /* outside the boundary: dropped */
    if(bnd){
      var keepT=[],outP={};
      T.forEach(function(tr){
        var cx=(P[tr[0]][0]+P[tr[1]][0]+P[tr[2]][0])/3,cz=(P[tr[0]][1]+P[tr[1]][1]+P[tr[2]][1])/3;
        if(bimPointInPoly([cx,cz],bnd))keepT.push(tr);
      });
      T=keepT;
      var used={};T.forEach(function(tr){used[tr[0]]=used[tr[1]]=used[tr[2]]=1;});
      for(i=0;i<S.length;i++)if(!used[i])outP[i]=1;
      res.outside=outP;
    }
    res.tris=T;
    return res;
  }
  /* ---- analysis bands ---- */
  var BIM_SLOPE_BANDS=[0,2,5,8.33,15,25,50,Infinity];
  var BIM_SLOPE_COLS=['#2e7d32','#66bb6a','#c0ca33','#fdd835','#fb8c00','#e53935','#8e24aa'];
  var BIM_ELEV_COLS=['#1b5e20','#43a047','#9ccc65','#e6ee9c','#ffcc80','#bc8f5a','#8d6e63'];
  var BIM_ASPECT=[{n:'N',c:'#3949ab'},{n:'NE',c:'#1e88e5'},{n:'E',c:'#00acc1'},{n:'SE',c:'#43a047'},{n:'S',c:'#fdd835'},{n:'SW',c:'#fb8c00'},{n:'W',c:'#e53935'},{n:'NW',c:'#8e24aa'}];
  /* one triangle's plane: h = a x + b z + c -> slope (%), the compass way it falls, its plan area */
  function bimTriPlane(A,B,C,ha,hb,hc){
    var d=(B[0]-A[0])*(C[1]-A[1])-(C[0]-A[0])*(B[1]-A[1]);
    if(Math.abs(d)<1e-12)return null;
    var a=((hb-ha)*(C[1]-A[1])-(hc-ha)*(B[1]-A[1]))/d,b=((hc-ha)*(B[0]-A[0])-(hb-ha)*(C[0]-A[0]))/d;
    var tn=bimTrueNorthDeg()*Math.PI/180,east=[Math.cos(tn),Math.sin(tn)],north=[Math.sin(tn),-Math.cos(tn)];
    var dx=-a,dz=-b,az=(Math.atan2(dx*east[0]+dz*east[1],dx*north[0]+dz*north[1])*180/Math.PI+360)%360;
    return {slope:Math.sqrt(a*a+b*b)*100,aspect:az,area:Math.abs(d)/2};
  }
  /* mode: slope | elevation | aspect -> {bands:[{label,col,area,share}], tri:[band index per triangle]} */
  function bimTerrainBands(tin,mode){
    var bands=[],tri=[],i,t,A,B,C,pl,k,r=bimTerrainRange(tin),total=0;
    if(mode==='slope')for(i=0;i+1<BIM_SLOPE_BANDS.length;i++)bands.push({label:BIM_SLOPE_BANDS[i]+(BIM_SLOPE_BANDS[i+1]===Infinity?'% and over':' to '+BIM_SLOPE_BANDS[i+1]+'%'),col:BIM_SLOPE_COLS[i],area:0});
    else if(mode==='elevation'){
      var n=BIM_ELEV_COLS.length,st=(r[1]-r[0])/n||1;
      for(i=0;i<n;i++)bands.push({label:bimDispNum(r[0]+i*st,2)+' to '+bimDispNum(r[0]+(i+1)*st,2)+' m',col:BIM_ELEV_COLS[i],area:0,lo:r[0]+i*st});
    }else if(mode==='aspect'){
      bands.push({label:'Flat (under 2%)',col:'#9e9e9e',area:0});
      BIM_ASPECT.forEach(function(a){bands.push({label:'Facing '+a.n,col:a.c,area:0});});
    }else return null;
    for(t=0;t<tin.tris.length;t++){
      var tr=tin.tris[t];A=tin.P[tr[0]];B=tin.P[tr[1]];C=tin.P[tr[2]];
      pl=bimTriPlane(A,B,C,tin.H[tr[0]],tin.H[tr[1]],tin.H[tr[2]]);
      if(!pl){tri.push(-1);continue;}
      if(mode==='slope'){for(k=0;k+1<BIM_SLOPE_BANDS.length;k++)if(pl.slope<BIM_SLOPE_BANDS[k+1])break;}
      else if(mode==='elevation'){var hm=(tin.H[tr[0]]+tin.H[tr[1]]+tin.H[tr[2]])/3;k=Math.min(bands.length-1,Math.max(0,Math.floor((hm-r[0])/((r[1]-r[0])/bands.length||1))));}
      else k=pl.slope<2?0:1+Math.floor(((pl.aspect+22.5)%360)/45);
      tri.push(k);bands[k].area+=pl.area;total+=pl.area;
    }
    bands.forEach(function(b){b.share=total?b.area/total:0;});
    return {mode:mode,bands:bands,tri:tri,total:total};
  }
  /* ---- LandXML 1.2 ---- */
  function bimXmlEsc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
  /* a model point (local to the surface) back to the survey's own northing, easting, elevation */
  function bimModelToSurvey(o,x,z,y){
    var src=o.source||{},sb=A3D.site&&A3D.site.surveyBase,b=src.base||sb||{n:0,e:0,z:0},un=src.base?(src.units||'m'):((sb&&sb.units)||'m');
    var u=BIM_SURVEY_UNITS[un]||1,tn=bimTrueNorthDeg()*Math.PI/180,ct=Math.cos(tn),st=Math.sin(tn);
    var dE=x*ct+z*st,dN=x*st-z*ct;
    return {n:b.n+dN/u,e:b.e+dE/u,z:b.z+y/u,units:un};
  }
  function bimLandXmlSurface(o){
    var q=bimObjOffset(o),tin=bimTerrainTin(o),ids=[],pts='',faces='',i,s,un='m';
    for(i=0;i<tin.P.length;i++){
      s=bimModelToSurvey(o,tin.P[i][0]-q[0],tin.P[i][1]-q[2],tin.H[i]-q[1]);un=s.units;
      pts+='<P id="'+(i+1)+'">'+s.n.toFixed(4)+' '+s.e.toFixed(4)+' '+s.z.toFixed(4)+'</P>';
    }
    tin.tris.forEach(function(f){faces+='<F>'+(f[0]+1)+' '+(f[1]+1)+' '+(f[2]+1)+'</F>';});
    var src='',vkey={};
    for(i=0;i<tin.P.length;i++)vkey[Math.round((tin.P[i][0]-q[0])*100)+'_'+Math.round((tin.P[i][1]-q[2])*100)]=i;
    if((o.breaklines&&o.breaklines.length)||(o.boundary&&o.boundary.length>=3)){
      src+='<SourceData>';
      if(o.breaklines&&o.breaklines.length){
        src+='<Breaklines>'+o.breaklines.map(function(bl){
          return '<Breakline brkType="standard" name="'+bimXmlEsc(bl.name||'breakline')+'"><PntList3D>'+bl.pts.map(function(p){
            var own=p.length>2&&p[2]!==null&&isFinite(p[2]),vi=own?-1:vkey[Math.round(p[0]*100)+'_'+Math.round(p[1]*100)];
            /* no height of its own: the one its vertex was given in the surface, even outside a boundary */
            var h=own?p[2]:(vi!==undefined&&vi>=0?tin.H[vi]-q[1]:bimTinHeightAt(tin,p[0]+q[0],p[1]+q[2]));if(h===null)return '';if(!own&&!(vi!==undefined&&vi>=0))h-=q[1];
            var w=bimModelToSurvey(o,p[0],p[1],h);return w.n.toFixed(4)+' '+w.e.toFixed(4)+' '+w.z.toFixed(4);}).join(' ')+'</PntList3D></Breakline>';
        }).join('')+'</Breaklines>';
      }
      if(o.boundary&&o.boundary.length>=3)src+='<Boundaries><Boundary bndType="outer" name="boundary"><PntList2D>'+o.boundary.concat([o.boundary[0]]).map(function(p){
        var w=bimModelToSurvey(o,p[0],p[1],0);return w.n.toFixed(4)+' '+w.e.toFixed(4);}).join(' ')+'</PntList2D></Boundary></Boundaries>';
      src+='</SourceData>';
    }
    return {xml:'<Surface name="'+bimXmlEsc(o.name)+'">'+src+'<Definition surfType="TIN"><Pnts>'+pts+'</Pnts><Faces>'+faces+'</Faces></Definition></Surface>',units:un,points:tin.P.length,faces:tin.tris.length};
  }
  function bimLandXmlDoc(ids){
    var T=(ids&&ids.length?ids.map(objById):A3D.objs).filter(function(o){return o&&o.t==='terrain'&&o.survey&&o.survey.length>=3;});
    if(!T.length)return {error:'There is no terrain surface to export'};
    var S=T.map(bimLandXmlSurface),un=S[0].units,d=new Date().toISOString();
    var units=un==='m'?'<Metric linearUnit="meter" areaUnit="squareMeter" volumeUnit="cubicMeter" angularUnit="decimal degrees" directionUnit="decimal degrees"/>':
      '<Imperial linearUnit="'+(un==='usft'?'USSurveyFoot':'foot')+'" areaUnit="squareFoot" volumeUnit="cubicFeet" angularUnit="decimal degrees" directionUnit="decimal degrees"/>';
    var xml='<?xml version="1.0" encoding="UTF-8"?>\n<LandXML xmlns="http://www.landxml.org/schema/LandXML-1.2" version="1.2" date="'+d.slice(0,10)+'" time="'+d.slice(11,19)+'">'+
      '<Units>'+units+'</Units><Project name="'+bimXmlEsc(bimFileStem())+'"/><Application name="BIM Personal" version="'+bimXmlEsc(BIM_APP_VERSION.v)+'"/>'+
      '<Surfaces>'+S.map(function(s){return s.xml;}).join('')+'</Surfaces></LandXML>\n';
    return {xml:xml,surfaces:S.length,points:S.reduce(function(a,s){return a+s.points;},0),faces:S.reduce(function(a,s){return a+s.faces;},0),units:un};
  }
  function bimLandXmlExport(ids){
    var d=bimLandXmlDoc(ids||(A3D.selSet&&A3D.selSet.length?A3D.selSet:null));
    if(d.error){a3dToast(d.error);return d;}
    var fn=bimFileStem()+'.xml';
    try{bimTriggerDownload(d.xml,fn,'application/xml');}catch(eX){console.warn('[BIM] LandXML',eX);a3dToast('LandXML export failed - see the console');return {error:String(eX)};}
    a3dToast('Exported '+fn+': LandXML 1.2, '+d.surfaces+' surface'+(d.surfaces===1?'':'s')+', '+d.points+' points, '+d.faces+' triangles, in '+(d.units==='m'?'metres':d.units==='usft'?'US survey feet':'feet'));
    return d;
  }
  /* in: every TIN surface, its own faces kept; placed by the site's survey base, else by its first point */
  function bimLandXmlImport(text,name){
    name=String(name||'LandXML');
    var doc;
    try{doc=new DOMParser().parseFromString(text,'application/xml');}catch(eP){doc=null;}
    if(!doc||doc.getElementsByTagName('parsererror').length){var m0=name+' is not XML';a3dToast(m0);return {error:m0};}
    function all(n,tag){return n?Array.prototype.slice.call(n.getElementsByTagNameNS?n.getElementsByTagNameNS('*',tag):n.getElementsByTagName(tag)):[];}
    if(!all(doc,'LandXML').length){var m1=name+' is not a LandXML file';a3dToast(m1);return {error:m1};}
    var un='m',me=all(doc,'Metric')[0],im=all(doc,'Imperial')[0];
    if(im){var lu=String(im.getAttribute('linearUnit')||'');un=/survey/i.test(lu)?'usft':'ft';}
    else if(me&&/milli/i.test(String(me.getAttribute('linearUnit')||''))){var m2='Millimetre LandXML is not read yet';a3dToast(m2);return {error:m2};}
    var surfs=all(doc,'Surface').filter(function(s){return all(s,'Pnts').length;});
    if(!surfs.length){var m3='No TIN surface in '+name;a3dToast(m3);return {error:m3};}
    var base=(A3D.site&&A3D.site.surveyBase)||null,ids=[],made=[];
    pushUndo();
    undoSuspend=true;
    try{
      surfs.forEach(function(sf){
        var P=all(sf,'P'),idx={},pts=[],i;
        P.forEach(function(p){
          var v=String(p.textContent||'').replace(/^\s+|\s+$/g,'').split(/[\s,]+/).map(parseFloat);
          if(v.length<3||!isFinite(v[0])||!isFinite(v[1])||!isFinite(v[2]))return;
          idx[p.getAttribute('id')]=pts.length;pts.push({p:String(p.getAttribute('name')||p.getAttribute('id')||''),n:v[0],e:v[1],z:v[2],d:''});
        });
        if(pts.length<3)return;
        if(!base){base={n:pts[0].n,e:pts[0].e,z:0,units:un};A3D.site.surveyBase={n:base.n,e:base.e,z:0,units:un};}
        /* the file's units into the base's */
        var k=(BIM_SURVEY_UNITS[un]||1)/(BIM_SURVEY_UNITS[base.units]||1);
        var conv=pts.map(function(q){return {p:q.p,n:q.n*k,e:q.e*k,z:q.z*k,d:''};});
        var model=bimSurveyToModel(conv,base.units,base,bimTrueNorthDeg());
        var faces=[];
        all(sf,'F').forEach(function(f){
          if(f.getAttribute('i')==='1')return;   /* an invisible face: outside the surface */
          var v=String(f.textContent||'').replace(/^\s+|\s+$/g,'').split(/\s+/);
          if(v.length<3)return;
          var a=idx[v[0]],b=idx[v[1]],c=idx[v[2]];
          if(a===undefined||b===undefined||c===undefined)return;
          /* counter-clockwise in plan */
          var A=model[a],B=model[b],C=model[c],cr=(B[0]-A[0])*(C[1]-A[1])-(B[1]-A[1])*(C[0]-A[0]);
          if(Math.abs(cr)<1e-12)return;
          faces.push(cr>0?[a,b,c]:[a,c,b]);
        });
        A3D.counts.terrain=(A3D.counts.terrain||0)+1;
        var o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'terrain',name:String(sf.getAttribute('name')||('Surface_'+A3D.counts.terrain)).slice(0,60),col:'#b08559',
          pos:[0,0,0],layer:A3D.activeLayer,survey:model,source:{format:'LandXML',units:base.units,base:{n:base.n,e:base.e,z:base.z},file:name.slice(0,120)},rev:1};
        if(faces.length)o.faces=faces;
        else{var seen={};model=model.filter(function(m){var kk=Math.round(m[0]*1e6)+'_'+Math.round(m[1]*1e6);if(seen[kk])return false;seen[kk]=1;return true;});o.survey=model;}
        A3D.objs.push(o);ids.push(o.id);made.push({name:o.name,points:model.length,faces:faces.length});
      });
    }finally{undoSuspend=false;}
    if(!ids.length){var m4='No surface in '+name+' had three points';a3dToast(m4);return {error:m4};}
    A3D.sel=ids[0];A3D.sel2=null;A3D.selSet=[ids[0]];
    refreshTree();refreshProps();fitScene();paint();saveSoon();
    a3dToast('LandXML: '+made.map(function(m){return m.name+' ('+m.points+' points, '+(m.faces?m.faces+' triangles kept':'triangulated here')+')';}).join('; ')+' from '+name);
    return {ids:ids,surfaces:made,units:un};
  }
  function bimLandXmlPick(){
    var inp=document.createElement('input');
    inp.type='file';inp.accept='.xml,.landxml,application/xml,text/xml';
    inp.onchange=function(){
      var f=inp.files&&inp.files[0];if(!f)return;
      var rd=new FileReader();
      rd.onerror=function(){a3dToast('Failed to read '+f.name);};
      rd.onload=function(){try{bimLandXmlImport(String(rd.result||''),f.name);}catch(eL){console.warn('[BIM] LandXML',eL);a3dToast('LandXML import failed - see the console');}};
      rd.readAsText(f);
    };
    inp.click();
    return true;
  }
  /* ---- breaklines and the boundary, from sketches ---- */
  function bimTerrainFor(sk){
    var sel=(A3D.selSet||[]).map(objById).filter(function(o){return o&&o.t==='terrain'&&o.survey;});
    if(sel.length)return sel[0];
    var T=A3D.objs.filter(function(o){return o.t==='terrain'&&o.survey;}),i,j,p,tin;
    for(i=0;i<T.length;i++){tin=bimTerrainTin(T[i]);for(j=0;j<sk.length;j++){p=sk[j];if(bimTinHeightAt(tin,p[0],p[1])!==null)return T[i];}}
    return T[0]||null;
  }
  function bimSketchPts(o){
    var q=bimObjOffset(o),pts=(bimFlattenSketch(o)||o.pts||[]);
    return pts.map(function(p){return [p[0]+q[0],p[1]+q[2]];});
  }
  /* BREAKLINE: the selected open or closed polylines, into the surface under them */
  function bimBreaklineCommand(){
    var sk=(A3D.selSet||[]).map(objById).filter(function(o){return o&&o.t==='sketch'&&o.pts&&o.pts.length>=2&&!bimIsPoint(o);});
    if(!sk.length){a3dToast('Select one or more polylines (and the surface, if there are several), then BREAKLINE');return null;}
    var all=[];sk.forEach(function(o){all=all.concat(bimSketchPts(o));});
    var ter=bimTerrainFor(all);
    if(!ter){a3dToast('There is no terrain surface: make one with SURVEY');return null;}
    var q=bimObjOffset(ter);
    pushUndo();
    ter.breaklines=ter.breaklines||[];
    sk.forEach(function(o){
      var p=bimSketchPts(o).map(function(v){return [v[0]-q[0],v[1]-q[2],null];});
      if(o.closed!==false&&p.length>=3)p.push(p[0].slice());
      ter.breaklines.push({name:o.name,pts:p,from:o.id});
    });
    ter.rev=(ter.rev||0)+1;
    var tin=bimTerrainTin(ter);
    refreshProps();paint();saveSoon();
    a3dToast(ter.name+': '+sk.length+' breakline'+(sk.length===1?'':'s')+' added; '+tin.constraints.length+' segment'+(tin.constraints.length===1?'':'s')+' held'+
      (tin.unforced.length?'; '+tin.unforced.length+' not: '+tin.unforced[0].why:''));
    return {terrain:ter.id,constraints:tin.constraints.length,unforced:tin.unforced.slice()};
  }
  /* TERRAINBOUNDARY: the selected closed polyline becomes the surface's outer boundary */
  function bimBoundaryCommand(){
    var sk=(A3D.selSet||[]).map(objById).filter(function(o){return o&&o.t==='sketch'&&o.closed!==false&&o.pts&&o.pts.length>=3&&!bimIsPoint(o);});
    if(!sk.length){a3dToast('Select a closed polyline (and the surface, if there are several), then TERRAINBOUNDARY');return null;}
    var pts=bimSketchPts(sk[0]),ter=bimTerrainFor(pts);
    if(!ter){a3dToast('There is no terrain surface: make one with SURVEY');return null;}
    var q=bimObjOffset(ter);
    pushUndo();
    ter.boundary=sketchCCW(pts).map(function(v){return [v[0]-q[0],v[1]-q[2]];});
    ter.rev=(ter.rev||0)+1;
    var tin=bimTerrainTin(ter),n=tin.outside?Object.keys(tin.outside).length:0;
    refreshProps();paint();saveSoon();
    a3dToast(ter.name+': bounded by '+sk[0].name+'; '+tin.tris.length+' triangles inside'+(n?', '+n+' point'+(n===1?'':'s')+' outside left out':''));
    return {terrain:ter.id,triangles:tin.tris.length,outside:n};
  }
  function bimTerrainEdit(o,what){
    if(!o||o.t!=='terrain')return false;
    pushUndo();
    if(what==='breaklines')delete o.breaklines;
    else if(what==='boundary')delete o.boundary;
    else if(what==='faces')delete o.faces;
    else return false;
    o.rev=(o.rev||0)+1;
    refreshProps();paint();saveSoon();
    return true;
  }
  /* the analysis shown on a surface: '', slope, elevation, aspect */
  function bimTerrainSetView(o,mode){
    if(!o||o.t!=='terrain')return false;
    mode=String(mode||'');
    if(mode&&!/^(slope|elevation|aspect)$/.test(mode))return false;
    if((o.tview||'')===mode)return true;
    pushUndo();
    if(mode)o.tview=mode;else delete o.tview;
    refreshProps();paint();saveSoon();bimAnalyzeRefresh();
    return true;
  }
"""
rep("""  /* ================= __acad3dV138: verify the survey ================= */""", ENGINE + """  /* ================= __acad3dV138: verify the survey ================= */""")
# the survey check: the survey's own points only (a breakline's vertices are made from them)
rep("""      for(i=0;i<tin.P.length;i++){
        if(flag[i]){devs.push(null);continue;}""", """      for(i=0;i<(tin.nSurvey||tin.P.length);i++){   /* __acad3dV144: the survey's own points */
        if(flag[i]){devs.push(null);continue;}""")
rep("""for(i=0;i<tin.P.length;i++){gh=bimTinHeightAt(ctin,""", """for(i=0;i<(tin.nSurvey||tin.P.length);i++){gh=bimTinHeightAt(ctin,""")
# the survey check: points a boundary trimmed away are left out, and said
rep("""      for(i=0;i<tin.P.length;i++){
        h=bimTinHeightAt(tin,tin.P[i][0],tin.P[i][1]);
        if(h===null){out++;continue;}""", """      var trimmed=0;
      for(i=0;i<(tin.nSurvey||tin.P.length);i++){   /* the survey's own points: not a breakline's */
        if(tin.outside&&tin.outside[i]){trimmed++;continue;}   /* __acad3dV144: outside the boundary, by design */
        h=bimTinHeightAt(tin,tin.P[i][0],tin.P[i][1]);
        if(h===null){out++;continue;}""")
rep("""        out?out+' point'+(out===1?'':'s')+' not on the surface':('largest difference '+(maxr*1000).toFixed(1)+' mm'+(wi>=0&&maxr>BIM_SURVEY_TOL.fidelity?' at '+bimSurveyName(o,wi):'')),{max:maxr,outside:out});""",
    """        (out?out+' point'+(out===1?'':'s')+' not on the surface':('largest difference '+(maxr*1000).toFixed(1)+' mm'+(wi>=0&&maxr>BIM_SURVEY_TOL.fidelity?' at '+bimSurveyName(o,wi):'')))+
        (trimmed?'; '+trimmed+' point'+(trimmed===1?'':'s')+' outside the boundary, left out':''),{max:maxr,outside:out,trimmed:trimmed});   /* __acad3dV144 */""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
