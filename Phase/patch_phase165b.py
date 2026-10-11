"""patch_phase165b.py -- V165: land and water, the ground and the six analyses.

reference/research-site-analysis-in-model.md, section 2. The context's terrain is a point every 25 m;
a site needs its ground every few metres. Analyze site samples the same free tiles every 5 m for
150 m around the site and keeps them with the project in metres above sea level; the project's own
surface is read instead where it covers the site; with neither, the context's terrain, its spacing
said. On that ground:
  contours   every 0.25 to 50 m, at round heights above sea level, every fifth an index, labelled
  slope      Horn's method, in the five classes a planner reads (15% and 25% the decision points)
  aspect     the way each cell faces, read for warmth: equator-facing warm, pole-facing cool
  flow       Priority-Flood, then D8: flow lines by Strahler order, the divides between catchments,
             the land draining onto the site and where its water leaves
  ponds      where the filled ground stands 10 cm or more over the real one: depth, area, volume
  flood      FEMA's National Flood Hazard Layer, US sites: the 1% and 0.2% annual chance zones, the
             floodway, the base flood elevation, the zone the site is in
"""
import hashlib, pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
BASE = '395f144afaafa7e321f41a47a3ba864cbede2421083dda94f7009a25c62e71a7'   # after patch_phase165a.py

raw = SRC.read_bytes()
sha = hashlib.sha256(raw).hexdigest()
if sha != BASE:
    sys.exit('baseline sha mismatch: %s' % sha)
txt = raw.decode('utf-8')


def rep(old, new, count=1):
    global txt
    n = txt.count(old)
    assert n == count, 'anchor count %d (wanted %d): %r' % (n, count, old[:80])
    txt = txt.replace(old, new)


LAND = r"""  /* ================= __acad3dV165: site analysis in the model II, land and water =================
     reference/research-site-analysis-in-model.md, section 2. The ground at the site's scale -- a grid
     every 5 m for 150 m around it -- and six analyses on it, each a layer of the same button. The grid
     is kept with the project in metres above sea level (A3D.site.land), so each runs again offline;
     the model's own heights come from it less the datum, the height of model 0. */
  var BIM_LAND_HALF=150,BIM_LAND_CELL=5,BIM_LAND_FLAT=2,BIM_LAND_STREAM=2500,BIM_LAND_POND=0.1,BIM_LAND_POND_AREA=50,BIM_LAND_PONDS=8,
    BIM_LAND_EPS=1e-5,BIM_LAND_CATCH=0.04,BIM_LAND_LEVELS=24;
  var BIM_LAND_FEMA='https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/28';
  /* the five classes: [from %, to %, name, short, what it means, colour] -- the steeper the darker */
  var BIM_LAND_SLOPE=[[0,5,'0 to 5%','0-5','flat to gentle: the easiest to build on','#ffffb2'],[5,10,'5 to 10%','5-10','moderate','#fecc5c'],
    [10,15,'10 to 15%','10-15','moderately steep','#fd8d3c'],[15,25,'15 to 25%','15-25','steep: walls and drainage engineered','#f03b20'],
    [25,Infinity,'Over 25%','25+','not developable without great cost','#bd0026']];
  var BIM_LAND_DIRS=['N','NE','E','SE','S','SW','W','NW'];
  var BIM_LAND_DIRNAME={N:'north',NE:'north-east',E:'east',SE:'south-east',S:'south',SW:'south-west',W:'west',NW:'north-west'};
  /* warmth: the pole-facing coolest to the equator-facing warmest; flat grey */
  var BIM_LAND_WARM=['#4575b4','#91bfdb','#e6dfc8','#fc8d59','#d7301f'],BIM_LAND_FLATCOL='#bdbdbd';
  var BIM_LAND_HYPSO=['#2f7d4a','#7fb86a','#d9cf86','#b98a4e','#7d5537'];
  var BIM_LAND_ZONES={floodway:{lv:4,name:'Regulatory floodway',short:'floodway',col:'#c2416b',site:'in the regulatory floodway'},
    coastal:{lv:3,name:'1% annual chance, coastal (V, VE)',short:'1% coast',col:'#2b5aa8',site:'1% annual chance, coastal'},
    sfha:{lv:2,name:'1% annual chance (A, AE, AH, AO)',short:'1%',col:'#3d85d8',site:'1% annual chance'},
    x02:{lv:1,name:'0.2% annual chance (shaded X)',short:'0.2%',col:'#f0a04b',site:'0.2% annual chance'},
    undetermined:{lv:0,name:'Not determined (D)',short:'D',col:'#9aa3ad',site:'hazard not determined'}};
  var BIM_LAND_ZORDER=['floodway','coastal','sfha','x02','undetermined'];
  var A3D_LAND={key:null,D:null};
  function bimLandR(v){return Math.round(v*100)/100;}
  function bimLandPct(n,t){return t?bimDispNum(100*n/t,1)+'%':'\u2014';}
  function bimLandHa(m2){return m2>=2000?bimDispNum(m2/10000,2)+' ha':bimDispNum(m2,0)+' m\u00b2';}
  function bimLandDir8(az){return Math.floor(((az+22.5)%360)/45)%8;}
  /* the compass bearing of a plan vector, from true north */
  function bimLandAz(vx,vz){var tn=bimTrueNorthDeg()*Math.PI/180;return (Math.atan2(vx*Math.cos(tn)+vz*Math.sin(tn),vx*Math.sin(tn)-vz*Math.cos(tn))*180/Math.PI+360)%360;}
  /* the square analysed: 150 m around the site's centre, in model metres and in degrees */
  function bimLandArea(S){
    var org=bimMapOrigin(),h=BIM_LAND_HALF,cx=S.c[0],cz=S.c[1],C=[[cx-h,cz-h],[cx+h,cz-h],[cx+h,cz+h],[cx-h,cz+h]],lo0=Infinity,lo1=-Infinity,la0=Infinity,la1=-Infinity,i,q;
    if(!org)return null;
    for(i=0;i<4;i++){q=bimModelToGeo(C[i][0],C[i][1],org);lo0=Math.min(lo0,q[0]);lo1=Math.max(lo1,q[0]);la0=Math.min(la0,q[1]);la1=Math.max(la1,q[1]);}
    return {cx:cx,cz:cz,half:h,s:la0,w:lo0,n:la1,e:lo1,org:org};
  }
  /* FEMA maps the US and its territories: a box for each, the lower 48, Alaska, Hawaii, Puerto Rico and
     the Virgin Islands, Guam and the Marianas, American Samoa */
  function bimLandUS(org){
    var la=org.lat,lo=org.lon;
    return (la>24&&la<50&&lo>-125&&lo<-66)||(la>51&&la<72&&(lo<-129||lo>172))||(la>18.5&&la<22.5&&lo>-161&&lo<-154)||
      (la>17.5&&la<18.6&&lo>-67.5&&lo<-64.5)||(la>13&&la<21&&lo>144&&lo<146.2)||(la>-14.6&&la<-11&&lo>-171.2&&lo<-168);
  }
  /* Analyze site's ground and water: the tiles sampled every 5 m, and FEMA's zones; each in its own
     words when it fails, what came before kept */
  function bimLandFetch(){
    var S=bimDgSite(),a=bimLandArea(S),out={errors:[]},date=bimSaToday();
    if(!a){a3dToast('Set the site latitude and longitude first, or find an address: the ground is read around the site');return null;}
    var pt=bimCtxTerrain(a).then(function(ter){
      if(!ter.ok){out.errors.push(bimCtxErr(bimMapHost(BIM_TERRARIUM_URL),ter.err));return;}
      var n=Math.round(2*a.half/BIM_LAND_CELL)+1,x0=a.cx-a.half,z0=a.cz-a.half,h=[],i,j,g,ev,got=0;
      for(j=0;j<n;j++)for(i=0;i<n;i++){
        g=bimModelToGeo(x0+i*BIM_LAND_CELL,z0+j*BIM_LAND_CELL,a.org);ev=bimCtxElevAt(ter,g[0],g[1]);
        if(isFinite(ev)){h.push(Math.round(ev*100));got++;}else h.push(null);
      }
      out.dem={x0:x0,z0:z0,cell:BIM_LAND_CELL,nx:n,nz:n,h:h,zoom:ter.range.z,sources:ter.sources,org:{lat:a.org.lat,lon:a.org.lon},tn:bimTrueNorthDeg(),fetched:date};
      out.cells=got;
    });
    var pf=(bimLandUS(a.org)?bimLandFloodFetch(a,date):Promise.resolve({outside:true,fetched:date})).then(function(r){out.flood=r;if(r.error)out.errors.push(r.error);});
    return Promise.all([pt,pf]).then(function(){
      A3D.site=A3D.site||{};
      var LD=A3D.site.land=A3D.site.land||{};
      if(out.dem)LD.dem=out.dem;
      if(out.flood&&!(out.flood.error&&LD.flood&&LD.flood.features))LD.flood=out.flood;
      A3D_LAND.key=null;A3D_LAND.D=null;
      saveSoon();
      return out;
    });
  }
  function bimLandFloodFetch(a,date){
    var url=bimDataQueryUrl({kind:'arcgis',url:BIM_LAND_FEMA},a),host=bimMapHost(url);
    return fetch(url).then(function(r){
      if(!r.ok)throw {http:r.status};
      return r.text();
    }).then(function(tx){
      var js,res;
      try{js=JSON.parse(tx);}catch(eJ){throw {bad:true};}
      res=bimDataParse(js,a);
      if(res.error)return {error:host+' '+res.error,fetched:date};
      return {features:res.features,more:!!res.more,host:host,fetched:date};
    }).then(null,function(e){return {error:bimCtxErr(host,e),fetched:date};});
  }
  /* ---- the ground the analyses read ---- */
  function bimLandDatum(){var d=bimCtxDatum();return (d===null||d===undefined||!isFinite(d))?null:d;}
  /* the kept grid's height above sea level at a model point, between its four nearest points */
  function bimLandAbsAt(d,x,z){
    var gx=Math.max(0,Math.min(d.nx-1,(x-d.x0)/d.cell)),gz=Math.max(0,Math.min(d.nz-1,(z-d.z0)/d.cell)),i=Math.min(d.nx-2,Math.floor(gx)),j=Math.min(d.nz-2,Math.floor(gz)),
      fx=gx-i,fz=gz-j,k=j*d.nx+i,q=[k,k+1,k+d.nx,k+d.nx+1],w=[(1-fx)*(1-fz),fx*(1-fz),(1-fx)*fz,fx*fz],s=0,t=0,m;
    for(m=0;m<4;m++)if(d.h[q[m]]!==null&&isFinite(d.h[q[m]])){s+=w[m]*d.h[q[m]]/100;t+=w[m];}
    return t>1e-9?s/t:null;
  }
  /* the ground's model height at a point, between the grid's four nearest points; at the edge the edge's */
  function bimLandAt(D,x,z){
    var gx=Math.max(0,Math.min(D.nx-1,(x-D.x0)/D.cell)),gz=Math.max(0,Math.min(D.nz-1,(z-D.z0)/D.cell)),i=Math.min(D.nx-2,Math.floor(gx)),j=Math.min(D.nz-2,Math.floor(gz)),
      fx=gx-i,fz=gz-j,k=j*D.nx+i,q=[k,k+1,k+D.nx,k+D.nx+1],w=[(1-fx)*(1-fz),fx*(1-fz),(1-fx)*fz,fx*fz],s=0,t=0,m;
    for(m=0;m<4;m++)if(D.ok[q[m]]){s+=w[m]*D.H[q[m]];t+=w[m];}
    return t>1e-9?s/t:null;
  }
  /* the context's terrain: its points' spacing, for saying how coarse it is */
  function bimLandCtxSpacing(T){
    var S=T.survey,x0=Infinity,x1=-Infinity,i,n=Math.round(Math.sqrt(S.length));
    for(i=0;i<S.length;i++){x0=Math.min(x0,S[i][0]);x1=Math.max(x1,S[i][0]);}
    return n>1?(x1-x0)/(n-1):0;
  }
  /* the project's own surface where it covers the site; else the tiles Analyze site kept, when the site
     is where they were fetched for; else the context's terrain. Cached until any of it changes. */
  function bimLandGround(S){
    var LD=A3D.site&&A3D.site.land,d=LD&&LD.dem,own=null,ct=null,org=bimMapOrigin(),tn=bimTrueNorthDeg(),i,j,o,key,from,dat,D;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(o.t!=='terrain'||!o.survey||o.survey.length<3||!bimLayerShown(o))continue;
      if(o.context){if(!ct)ct=o;continue;}
      if(!own&&bimTinIndexOf(o).at(S.c[0],S.c[1])!==null)own=o;
    }
    var fresh=!!(d&&d.h&&d.nx>1&&d.nz>1&&d.h.length===d.nx*d.nz&&org&&d.org&&Math.abs(d.org.lat-org.lat)<1e-9&&Math.abs(d.org.lon-org.lon)<1e-9&&Math.abs((d.tn||0)-tn)<1e-6);
    dat=bimLandDatum();
    if(own)from='own';else if(fresh)from='tiles';else if(ct)from='context';else return null;
    if(from==='tiles'&&dat===null){   /* model 0 at the ground under the site's origin, as the context sets it */
      var b0=bimLandAbsAt(d,0,0);
      if(b0===null)return null;
      A3D.site.terrainBase=Math.round(b0*100)/100;dat=A3D.site.terrainBase;
    }
    key=JSON.stringify(from==='own'?['own',own.id,own.rev||0,own.survey.length,bimObjOffset(own),S.c]:
      (from==='tiles'?['tiles',d.fetched,d.x0,d.z0,d.nx,d.nz,dat,d.h.length]:['context',ct.id,ct.rev||0,ct.survey.length,bimObjOffset(ct),S.c]));
    if(A3D_LAND.key===key&&A3D_LAND.D)return A3D_LAND.D;
    if(from==='tiles'){
      D={x0:d.x0,z0:d.z0,cell:d.cell,nx:d.nx,nz:d.nz,H:new Float64Array(d.nx*d.nz),ok:new Uint8Array(d.nx*d.nz),from:from,datum:dat};
      for(i=0;i<d.h.length;i++)if(d.h[i]!==null&&isFinite(d.h[i])){D.H[i]=d.h[i]/100-dat;D.ok[i]=1;}
      D.src='AWS Terrain Tiles at zoom '+d.zoom+(d.sources&&d.sources.length?' ('+d.sources.join(', ')+')':'')+', sampled every '+d.cell+' m, '+d.fetched;
      D.srcShort='AWS Terrain Tiles, every '+d.cell+' m';
    }else{
      var T=from==='own'?own:ct,ix=bimTinIndexOf(T),n=Math.round(2*BIM_LAND_HALF/BIM_LAND_CELL)+1,h;
      D={x0:S.c[0]-BIM_LAND_HALF,z0:S.c[1]-BIM_LAND_HALF,cell:BIM_LAND_CELL,nx:n,nz:n,H:new Float64Array(n*n),ok:new Uint8Array(n*n),from:from,datum:dat};
      for(j=0;j<n;j++)for(i=0;i<n;i++){h=ix.at(D.x0+i*D.cell,D.z0+j*D.cell);if(h!==null&&isFinite(h)){D.H[j*n+i]=h;D.ok[j*n+i]=1;}}
      if(from==='own'){D.src=T.name+', the project\'s own surface, sampled every '+D.cell+' m';D.srcShort=String(T.name).slice(0,40)+', every '+D.cell+' m';}
      else{D.src='The context\'s terrain (AWS Terrain Tiles, a point every '+bimDispNum(bimLandCtxSpacing(T),0)+' m), sampled every '+D.cell+' m: Analyze site fetches it finer';D.srcShort='Context terrain, a point every '+bimDispNum(bimLandCtxSpacing(T),0)+' m';}
    }
    var got=0;for(i=0;i<D.ok.length;i++)if(D.ok[i])got++;
    if(got<9)return null;
    D.cells=got;
    A3D_LAND.key=key;A3D_LAND.D=D;
    return D;
  }
  /* the heights with no value where there is no ground, for the contours */
  function bimLandField(D){
    if(!D.field){D.field=new Float64Array(D.H.length);for(var k=0;k<D.H.length;k++)D.field[k]=D.ok[k]?D.H[k]:NaN;}
    return D.field;
  }
  /* ---- slope and aspect: Horn (1981), the fall across each cell from its eight neighbours, the nearest
     two counted twice; a neighbour off the grid or without ground takes the cell's own height ---- */
  function bimLandHornOf(D){if(!D.horn)D.horn=bimLandHorn(D);return D.horn;}
  function bimLandHorn(D){
    var nx=D.nx,nz=D.nz,H=D.H,ok=D.ok,c=D.cell,N=nx*nz,sl=new Float64Array(N),as=new Float64Array(N),i,j,k;
    var tn=bimTrueNorthDeg()*Math.PI/180,ex=Math.cos(tn),ez=Math.sin(tn),nxv=Math.sin(tn),nzv=-Math.cos(tn);
    function h(i2,j2,e){if(i2<0||j2<0||i2>=nx||j2>=nz)return e;var q=j2*nx+i2;return ok[q]?H[q]:e;}
    for(j=0;j<nz;j++)for(i=0;i<nx;i++){
      k=j*nx+i;
      if(!ok[k]){sl[k]=NaN;as[k]=NaN;continue;}
      var e=H[k],a=h(i-1,j-1,e),b=h(i,j-1,e),cc=h(i+1,j-1,e),d=h(i-1,j,e),f=h(i+1,j,e),g=h(i-1,j+1,e),hh=h(i,j+1,e),ii=h(i+1,j+1,e);
      var dx=((cc+2*f+ii)-(a+2*d+g))/(8*c),dz=((g+2*hh+ii)-(a+2*b+cc))/(8*c);
      sl[k]=Math.sqrt(dx*dx+dz*dz)*100;
      as[k]=sl[k]<BIM_LAND_FLAT?-1:(Math.atan2(-dx*ex-dz*ez,-dx*nxv-dz*nzv)*180/Math.PI+360)%360;   /* the way it falls */
    }
    return {slope:sl,aspect:as};
  }
  /* ---- marching squares over the grid's points: the lines where V crosses lev, chained, in the grid's
     own coordinates. A point at the level counts as above it; a saddle is read by the cell's centre.
     pad, a number: the grid ringed with it, so every area is a closed ring; null: lines may run out at
     the edge, and a cell with a point of no value is passed. ---- */
  function bimLandMs(V,nx,nz,lev,pad){
    var o=pad===null||pad===undefined?0:1,NX=nx+2*o,NZ=nz+2*o,segs=[],adj={},i,j,s,out=[];
    function val(i2,j2){i2-=o;j2-=o;if(i2<0||j2<0||i2>=nx||j2>=nz)return pad;return V[j2*nx+i2];}
    function seg(e1,p1,e2,p2){var n=segs.length;segs.push([e1,p1,e2,p2]);(adj[e1]||(adj[e1]=[])).push(n);(adj[e2]||(adj[e2]=[])).push(n);}
    for(j=0;j<NZ-1;j++)for(i=0;i<NX-1;i++){
      var a=val(i,j),b=val(i+1,j),c=val(i+1,j+1),d=val(i,j+1);
      if(a!==a||b!==b||c!==c||d!==d)continue;
      var idx=(a>=lev?8:0)|(b>=lev?4:0)|(c>=lev?2:0)|(d>=lev?1:0);
      if(idx===0||idx===15)continue;
      var eT=2*(j*NX+i),eB=2*((j+1)*NX+i),eL=2*(j*NX+i)+1,eR=2*(j*NX+i+1)+1,gx=i-o,gz=j-o;
      var T=[gx+(lev-a)/(b-a),gz],B=[gx+(lev-d)/(c-d),gz+1],L=[gx,gz+(lev-a)/(d-a)],R=[gx+1,gz+(lev-b)/(c-b)],up=(a+b+c+d)/4>=lev;
      if(idx===1||idx===14)seg(eL,L,eB,B);
      else if(idx===2||idx===13)seg(eB,B,eR,R);
      else if(idx===3||idx===12)seg(eL,L,eR,R);
      else if(idx===4||idx===11)seg(eT,T,eR,R);
      else if(idx===6||idx===9)seg(eT,T,eB,B);
      else if(idx===7||idx===8)seg(eL,L,eT,T);
      else if(idx===5){if(up){seg(eL,L,eT,T);seg(eB,B,eR,R);}else{seg(eL,L,eB,B);seg(eT,T,eR,R);}}
      else if(idx===10){if(up){seg(eT,T,eR,R);seg(eL,L,eB,B);}else{seg(eL,L,eT,T);seg(eB,B,eR,R);}}
    }
    var used=new Uint8Array(segs.length);
    function walk(si,e){
      var pts=[segs[si][0]===e?segs[si][1]:segs[si][3]],cur=si,guard=0;
      while(guard++<=segs.length){
        used[cur]=1;
        var S2=segs[cur],eo=S2[0]===e?S2[2]:S2[0];
        pts.push(S2[0]===e?S2[3]:S2[1]);
        var L2=adj[eo],nx2=-1,q;
        for(q=0;q<L2.length;q++)if(!used[L2[q]]){nx2=L2[q];break;}
        if(nx2<0)break;
        cur=nx2;e=eo;
      }
      return pts;
    }
    for(s in adj)if(adj.hasOwnProperty(s)&&adj[s].length===1&&!used[adj[s][0]])out.push(walk(adj[s][0],+s));   /* the lines running out at the edge */
    for(s=0;s<segs.length;s++)if(!used[s]){var rg=walk(s,segs[s][0]);if(o)rg.pop();out.push(rg);}   /* the closed ones: a ring, or a line ending where it began */
    return out;
  }
  /* Douglas and Peucker: the points kept within tol metres of the line; p[0], p[1] in plan */
  function bimLandDP(P,tol,closed){
    if(P.length<=2)return P.slice();
    var Q=closed?P.concat([P[0]]):P,keep=new Uint8Array(Q.length),st=[[0,Q.length-1]],i,out=[];
    keep[0]=keep[Q.length-1]=1;
    while(st.length){
      var r=st.pop(),a=r[0],b=r[1],md=-1,mi=-1;
      for(i=a+1;i<b;i++){var dd=bimPointSegDist(Q[i][0],Q[i][1],Q[a][0],Q[a][1],Q[b][0],Q[b][1]);if(dd>md){md=dd;mi=i;}}
      if(mi>=0&&md>tol){keep[mi]=1;st.push([a,mi],[mi,b]);}
    }
    for(i=0;i<Q.length;i++)if(keep[i])out.push(Q[i]);
    if(closed)out.pop();
    return out;
  }
  /* the areas where mask is 1, as rings of model points lifted just over the ground. Only the points
     along a straight run go: two classes side by side keep one edge between them, with no sliver */
  function bimLandRings(D,mask,lift){
    var ch=bimLandMs(mask,D.nx,D.nz,0.5,0),out=[],i,j,r;
    for(i=0;i<ch.length;i++){
      r=[];for(j=0;j<ch[i].length;j++)r.push([D.x0+ch[i][j][0]*D.cell,D.z0+ch[i][j][1]*D.cell]);
      r=bimLandDP(r,D.cell*0.002,true);
      if(r.length<3)continue;
      out.push(r.map(function(q){var y=bimLandAt(D,q[0],q[1]);return [bimLandR(q[0]),bimLandR((y===null?0:y)+(lift||0.03)),bimLandR(q[1])];}));
    }
    return out;
  }
  /* the divides: where a cell of one large catchment sits beside a cell of another, the edge between
     them, chained into lines -- each divide once, so its dashes are not drawn twice out of step; in the
     grid's coordinates, kept within the ground analysed */
  function bimLandDivides(D,Y,big){
    var nx=D.nx,nz=D.nz,G={},order=[],i,j,k,a,b,out=[];
    function cl(v,n){return Math.max(0,Math.min(n-1,v));}
    function add(p,q,x1,z1,x2,z2){   /* the corners doubled, so they are whole numbers to join by */
      var lo=Math.min(p,q),hi=Math.max(p,q),key=lo+'-'+hi,g=G[key];
      if(!g){g=G[key]={a:lo,b:hi,seg:[],adj:{}};order.push(key);}
      var n=g.seg.length,e1=x1+','+z1,e2=x2+','+z2;
      g.seg.push([e1,e2,[cl(x1/2,nx),cl(z1/2,nz)],[cl(x2/2,nx),cl(z2/2,nz)]]);
      (g.adj[e1]||(g.adj[e1]=[])).push(n);(g.adj[e2]||(g.adj[e2]=[])).push(n);
    }
    for(j=0;j<nz;j++)for(i=0;i<nx;i++){
      k=j*nx+i;
      if(!D.ok[k]||!big[Y.lab[k]])continue;
      a=Y.lab[k];
      if(i+1<nx&&D.ok[k+1]&&(b=Y.lab[k+1])!==a&&big[b])add(a,b,2*i+1,2*j-1,2*i+1,2*j+1);
      if(j+1<nz&&D.ok[k+nx]&&(b=Y.lab[k+nx])!==a&&big[b])add(a,b,2*i-1,2*j+1,2*i+1,2*j+1);
    }
    order.forEach(function(key){
      var g=G[key],used=new Uint8Array(g.seg.length),lines=[],e,s2,q;
      function walk(si,at){   /* on to the next edge until an end, a meeting of three, or back to the start */
        var pts=[g.seg[si][0]===at?g.seg[si][2]:g.seg[si][3]],cur=si,guard=0;
        while(guard++<=g.seg.length){
          used[cur]=1;
          var S2=g.seg[cur],to=S2[0]===at?S2[1]:S2[0],L=g.adj[to];
          pts.push(S2[0]===at?S2[3]:S2[2]);
          if(L.length!==2)break;
          var nxt=L[0]===cur?L[1]:L[0];
          if(used[nxt])break;
          cur=nxt;at=to;
        }
        return pts;
      }
      for(e in g.adj)if(g.adj.hasOwnProperty(e)&&g.adj[e].length!==2)for(q=0;q<g.adj[e].length;q++)if(!used[g.adj[e][q]])lines.push(walk(g.adj[e][q],e));
      for(s2=0;s2<g.seg.length;s2++)if(!used[s2])lines.push(walk(s2,g.seg[s2][0]));   /* the loops */
      out.push({a:g.a,b:g.b,lines:lines});
    });
    return out;
  }
  /* the cells inside the site: its property line, else the ring of its buildings; at least the one under it */
  function bimLandSiteMask(D,S){
    var M=new Uint8Array(D.nx*D.nz),i,j,k,x,z,n=0,best=-1,bd=Infinity;
    for(j=0;j<D.nz;j++)for(i=0;i<D.nx;i++){
      k=j*D.nx+i;if(!D.ok[k])continue;
      x=D.x0+i*D.cell;z=D.z0+j*D.cell;
      var dx=x-S.c[0],dz=z-S.c[1],d2=dx*dx+dz*dz;
      if(d2<bd){bd=d2;best=k;}
      if((S.ring&&S.ring.length>=3)?bimPointInPoly([x,z],S.ring):d2<=S.r*S.r){M[k]=1;n++;}
    }
    if(!n&&best>=0)M[best]=1;
    return M;
  }
  /* ---- water: Priority-Flood (Barnes, Lehman and Mulla, 2014) from the edge inward, each cell raised
     to the lowest level water could leave it by, BIM_LAND_EPS a metre more along the way so a flat
     drains; D8 (O'Callaghan and Mark, 1984) on the filled ground; accumulation, highest first; Strahler's
     order on the flow lines; each cell's catchment, the outlet it drains to; the ponds ---- */
  function bimLandHydroOf(D){if(!D.hydro)D.hydro=bimLandHydro(D);return D.hydro;}
  function bimLandHydro(D){
    var nx=D.nx,nz=D.nz,N=nx*nz,H=D.H,ok=D.ok,c=D.cell,a2=c*c,F=new Float64Array(N),dir=new Int32Array(N),down=new Int32Array(N),acc=new Float64Array(N),done=new Uint8Array(N),i,j,k,d;
    var DX=[1,1,0,-1,-1,-1,0,1],DZ=[0,1,1,1,0,-1,-1,-1],DL=[1,Math.SQRT2,1,Math.SQRT2,1,Math.SQRT2,1,Math.SQRT2],Q=bimRainHeap(),ord=[];
    for(k=0;k<N;k++){dir[k]=-2;down[k]=-1;}
    function edge(i2,j2){if(i2===0||j2===0||i2===nx-1||j2===nz-1)return true;for(var e=0;e<8;e++)if(!ok[(j2+DZ[e])*nx+i2+DX[e]])return true;return false;}
    for(j=0;j<nz;j++)for(i=0;i<nx;i++){k=j*nx+i;if(ok[k]&&edge(i,j)){F[k]=H[k];done[k]=1;dir[k]=-1;Q.push([F[k],k]);}}
    while(Q.size()){
      var top=Q.pop(),cc=top[1],ci=cc%nx,cj=(cc-ci)/nx;
      ord.push(cc);
      for(d=0;d<8;d++){
        var a=ci+DX[d],b=cj+DZ[d];
        if(a<0||b<0||a>=nx||b>=nz)continue;
        var nk=b*nx+a;
        if(!ok[nk]||done[nk])continue;
        done[nk]=1;F[nk]=Math.max(H[nk],F[cc]+BIM_LAND_EPS*DL[d]);Q.push([F[nk],nk]);
      }
    }
    for(k=0;k<N;k++){
      if(!ok[k]||dir[k]===-1)continue;
      var ki=k%nx,kj=(k-ki)/nx,best=-1,bs=0;
      for(d=0;d<8;d++){
        var a3=ki+DX[d],b3=kj+DZ[d];
        if(a3<0||b3<0||a3>=nx||b3>=nz)continue;
        var q=b3*nx+a3;
        if(!ok[q])continue;
        var s2=(F[k]-F[q])/(DL[d]*c);
        if(s2>bs){bs=s2;best=d;}
      }
      dir[k]=best;
      if(best>=0)down[k]=(kj+DZ[best])*nx+ki+DX[best];
    }
    var byF=ord.slice().sort(function(p,q2){return F[q2]-F[p]||q2-p;});   /* highest first */
    for(k=0;k<N;k++)acc[k]=ok[k]?a2:0;
    for(i=0;i<byF.length;i++){k=byF[i];if(down[k]>=0)acc[down[k]]+=acc[k];}
    var stream=new Uint8Array(N),nin=new Int32Array(N),order=new Int32Array(N),mxo=new Int32Array(N),cnt=new Int32Array(N),head=new Int32Array(N),nxt=new Int32Array(N),lab=new Int32Array(N);
    for(k=0;k<N;k++){head[k]=-1;lab[k]=-1;if(ok[k]&&acc[k]>=BIM_LAND_STREAM)stream[k]=1;}
    for(k=0;k<N;k++)if(down[k]>=0){nxt[k]=head[down[k]];head[down[k]]=k;if(stream[k]&&stream[down[k]])nin[down[k]]++;}
    for(i=0;i<byF.length;i++){
      k=byF[i];if(!stream[k])continue;
      order[k]=mxo[k]?(cnt[k]>=2?mxo[k]+1:mxo[k]):1;
      var t=down[k];
      if(t>=0&&stream[t]){if(order[k]>mxo[t]){mxo[t]=order[k];cnt[t]=1;}else if(order[k]===mxo[t])cnt[t]++;}
    }
    var outl={},outs=[];
    for(i=byF.length-1;i>=0;i--){   /* lowest first: a cell's downstream already labelled */
      k=byF[i];
      lab[k]=dir[k]===-1?k:(down[k]>=0?lab[down[k]]:k);
      if(!outl.hasOwnProperty(lab[k])){outl[lab[k]]=0;outs.push(lab[k]);}
      outl[lab[k]]++;
    }
    /* the ponds: cells under water 10 cm or more, joined, the largest first */
    var pid=new Int32Array(N),ponds=[],stack,u;
    for(k=0;k<N;k++){
      if(!ok[k]||pid[k]||F[k]-H[k]<BIM_LAND_POND)continue;
      var pool={cells:[],volume:0,depth:0,deep:k,level:-Infinity};
      stack=[k];pid[k]=-1;
      while(stack.length){
        u=stack.pop();
        var ui=u%nx,uj=(u-ui)/nx,dd=F[u]-H[u];
        pool.cells.push(u);pool.volume+=dd*a2;pool.level=Math.max(pool.level,F[u]);
        if(dd>pool.depth){pool.depth=dd;pool.deep=u;}
        for(d=0;d<8;d++){
          var a4=ui+DX[d],b4=uj+DZ[d];
          if(a4<0||b4<0||a4>=nx||b4>=nz)continue;
          var v=b4*nx+a4;
          if(ok[v]&&!pid[v]&&F[v]-H[v]>=BIM_LAND_POND){pid[v]=-1;stack.push(v);}
        }
      }
      pool.area=pool.cells.length*a2;
      if(pool.area>=BIM_LAND_POND_AREA)ponds.push(pool);
    }
    ponds.sort(function(p,q2){return q2.volume-p.volume||p.deep-q2.deep;});
    return {F:F,dir:dir,down:down,acc:acc,byF:byF,stream:stream,nin:nin,order:order,head:head,nxt:nxt,lab:lab,outlets:outs,outCells:outl,ponds:ponds.slice(0,BIM_LAND_PONDS),pondsAll:ponds.length};
  }
  /* the flow lines: a link from a source or a confluence down to the next confluence, or off the grid */
  function bimLandLinks(D,Y){
    var N=D.nx*D.nz,out=[],k;
    for(k=0;k<N;k++){
      if(!Y.stream[k]||Y.nin[k]===1)continue;
      var nodes=[k],cur=k,guard=0;
      while(guard++<N){var t=Y.down[cur];if(t<0)break;nodes.push(t);if(Y.nin[t]!==1)break;cur=t;}
      out.push({from:k,to:nodes[nodes.length-1],nodes:nodes,order:Y.order[k],outlet:Y.down[nodes[nodes.length-1]]<0});
    }
    return out;
  }
  /* the land whose water reaches the site: everything upstream of its cells */
  function bimLandUpstream(D,Y,M){
    var N=D.nx*D.nz,U=new Uint8Array(N),st=[],k,u;
    for(k=0;k<N;k++)if(M[k]){U[k]=1;st.push(k);}
    while(st.length){k=st.pop();for(u=Y.head[k];u>=0;u=Y.nxt[u])if(!U[u]){U[u]=1;st.push(u);}}
    return U;
  }
  /* where the site's water leaves it: the cells inside draining to a cell outside, the most first */
  function bimLandExits(D,Y,M){
    var N=D.nx*D.nz,E=[],k,i,j,out=[];
    for(k=0;k<N;k++)if(M[k]&&Y.down[k]>=0&&!M[Y.down[k]])E.push(k);
    E.sort(function(a,b){return Y.acc[b]-Y.acc[a]||a-b;});
    for(i=0;i<E.length&&out.length<2;i++){
      if(out.length&&Y.acc[E[i]]<0.25*out[0].acc)break;
      var p=[E[i]],c=E[i];
      for(j=0;j<4;j++){c=Y.down[c];if(c<0)break;p.push(c);}
      if(p.length>1)out.push({k:E[i],acc:Y.acc[E[i]],path:p});
    }
    return out;
  }
  function bimLandP(D,k,lift){var nx=D.nx,i=k%nx,j=(k-i)/nx;return [bimLandR(D.x0+i*D.cell),bimLandR(D.H[k]+(lift===undefined?0.08:lift)),bimLandR(D.z0+j*D.cell)];}
  function bimLandNone(){return {E:[],run:{note:'No ground yet: Analyze site fetches it'}};}
  /* ---- the analyses ---- */
  /* contours: the step giving at most BIM_LAND_LEVELS lines, at round heights above sea level */
  function bimLandStep(D,base){
    var lo=Infinity,hi=-Infinity,i,k,steps=[0.25,0.5,1,2,2.5,5,10,20,25,50];
    for(i=0;i<D.H.length;i++)if(D.ok[i]){if(D.H[i]<lo)lo=D.H[i];if(D.H[i]>hi)hi=D.H[i];}
    for(k=0;k<steps.length;k++)if(Math.floor((hi+base)/steps[k]+1e-9)-Math.ceil((lo+base)/steps[k]-1e-9)+1<=BIM_LAND_LEVELS)return {step:steps[k],lo:lo,hi:hi};
    return {step:100,lo:lo,hi:hi};
  }
  function bimLandMix(a,b,f){
    var A=parseInt(a.slice(1),16),B=parseInt(b.slice(1),16),r=Math.round(((A>>16)&255)*(1-f)+((B>>16)&255)*f),g=Math.round(((A>>8)&255)*(1-f)+((B>>8)&255)*f),bl=Math.round((A&255)*(1-f)+(B&255)*f);
    return '#'+((1<<24)+(r<<16)+(g<<8)+bl).toString(16).slice(1);
  }
  function bimLandHypso(t){t=Math.max(0,Math.min(1,t));var n=BIM_LAND_HYPSO.length-1,i=Math.min(n-1,Math.floor(t*n));return bimLandMix(BIM_LAND_HYPSO[i],BIM_LAND_HYPSO[i+1],t*n-i);}
  function bimLandHeightText(D,y,dp){return D.datum!==null&&D.datum!==undefined?bimDispNum(D.datum+y,dp)+' m':(y>=0?'+':'\u2212')+bimDispNum(Math.abs(y),dp)+' m';}
  function bimDgContoursRun(S){
    var D=bimLandGround(S);
    if(!D)return bimLandNone();
    var base=D.datum||0,st=bimLandStep(D,base),V=bimLandField(D),E=[],k,i,j,dp=st.step<1?2:(st.step<5&&st.step!==Math.round(st.step)?1:0),
      k0=Math.ceil((st.lo+base)/st.step-1e-9),k1=Math.floor((st.hi+base)/st.step+1e-9),RL=Math.max(1.6*S.Rc,60),span=st.hi-st.lo||1;
    for(k=k0;k<=k1;k++){
      var lev=k*st.step,y=lev-base,idx=Math.round(k)%5===0,ch=bimLandMs(V,D.nx,D.nz,y,null),lines=[],best=null,bd=Infinity;
      for(i=0;i<ch.length;i++){
        var L=[];for(j=0;j<ch[i].length;j++)L.push([D.x0+ch[i][j][0]*D.cell,D.z0+ch[i][j][1]*D.cell]);
        L=bimLandDP(L,0.4,false);   /* a closed one keeps its first point at its end, so it is drawn closed */
        if(L.length<2)continue;
        var L3=L.map(function(q){return [bimLandR(q[0]),bimLandR(y+0.03),bimLandR(q[1])];});
        lines.push(L3);
        if(idx)for(j=0;j<L3.length;j++){var dd=Math.abs(Math.sqrt((L3[j][0]-S.c[0])*(L3[j][0]-S.c[0])+(L3[j][2]-S.c[1])*(L3[j][2]-S.c[1]))-RL);if(dd<bd){bd=dd;best=L3[j];}}
      }
      if(!lines.length)continue;
      var col=bimLandHypso((y-st.lo)/span),ht=bimLandHeightText(D,y,dp);
      E.push({k:'c:'+Math.round(lev*100),name:'Contour '+ht,g:{kind:'lines',lines:lines},s:{stroke:col,w:idx?1.7:0.8,op:idx?0.95:0.8},
        lb:idx&&best?[{t:ht.replace(/ m$/,''),p:best,sz:10,col:'#efe4cf',pri:3}]:[],   /* a number, as a topographic map labels a contour: the key gives the unit */
        info:{title:'The '+ht+' contour'+(idx?', an index contour':''),rows:[['Height',ht+(D.datum!==null&&D.datum!==undefined?' above sea level':' from the model\'s 0')],['Interval',bimDispNum(st.step,2)+' m; every fifth an index contour, labelled']],
          method:'Marching squares over the ground every '+D.cell+' m: a line where the ground crosses the height, placed between the grid\'s points',source:D.src}});
    }
    return {E:E,run:{legend:[{name:'Low ground, '+bimLandHeightText(D,st.lo,1),short:bimLandHeightText(D,st.lo,0),col:bimLandHypso(0),kind:'line'},
      {name:'High ground, '+bimLandHeightText(D,st.hi,1),short:bimLandHeightText(D,st.hi,0),col:bimLandHypso(1),kind:'line'},
      {name:'Every '+bimDispNum(st.step,2)+' m; every fifth labelled with its height in metres'+(D.datum!==null&&D.datum!==undefined?' above sea level':''),short:'every '+bimDispNum(st.step,2)+' m',col:'#efe4cf',kind:'line'}],source:D.srcShort,note:''}};
  }
  /* slope: Horn's method, in the five classes */
  function bimDgSlopeRun(S){
    var D=bimLandGround(S);
    if(!D)return bimLandNone();
    var hn=bimLandHornOf(D),M=bimLandSiteMask(D,S),N=D.nx*D.nz,cls=new Int8Array(N),cnt=[0,0,0,0,0],sc=[0,0,0,0,0],tot=0,stot=0,sum=0,mx=0,mxk=-1,i,k,E=[],a2=D.cell*D.cell;
    for(k=0;k<N;k++){
      cls[k]=-1;
      if(!D.ok[k]||!isFinite(hn.slope[k]))continue;
      for(i=0;i<BIM_LAND_SLOPE.length-1;i++)if(hn.slope[k]<BIM_LAND_SLOPE[i][1])break;
      cls[k]=i;cnt[i]++;tot++;
      if(M[k]){sc[i]++;stot++;sum+=hn.slope[k];if(hn.slope[k]>mx){mx=hn.slope[k];mxk=k;}}
    }
    for(i=0;i<BIM_LAND_SLOPE.length;i++){
      if(!cnt[i])continue;
      var C=BIM_LAND_SLOPE[i],mask=new Uint8Array(N);
      for(k=0;k<N;k++)if(cls[k]===i)mask[k]=1;
      var rings=bimLandRings(D,mask,0.03);
      if(!rings.length)continue;
      E.push({k:'class:'+i,name:'Slope '+C[2],g:{kind:'line',pts:[],bands:[{lv:i,col:C[5],rings:rings}]},s:{fill:C[5],fop:0.55},
        info:{title:'Slope '+C[2]+': '+C[4],rows:[['Of the ground around',bimLandPct(cnt[i],tot)+' ('+bimLandHa(cnt[i]*a2)+')'],['Of the site',stot?bimLandPct(sc[i],stot):'\u2014']],
          method:'Horn (1981): the fall across each '+D.cell+' m cell from its eight neighbours, the nearest two counted twice; rise over run, as a percentage',source:D.src}});
    }
    if(stot){
      var mainC=0;for(i=1;i<BIM_LAND_SLOPE.length;i++)if(sc[i]>sc[mainC])mainC=i;
      var cy=bimLandAt(D,S.c[0],S.c[1]),cp=[S.c[0],(cy===null?S.y:cy)+0.05,S.c[1]],falls=mxk>=0&&hn.aspect[mxk]>=0?', falling to the '+BIM_LAND_DIRNAME[BIM_LAND_DIRS[bimLandDir8(hn.aspect[mxk])]]:'';
      E.push({k:'site',name:'Slope at the site',g:{kind:'line',pts:[]},sym:{type:'dot',p:cp,r:4,col:BIM_LAND_SLOPE[mainC][5]},
        lb:[{t:'Site: mostly '+BIM_LAND_SLOPE[mainC][2]+', mean '+bimDispNum(sum/stot,1)+'%',p:cp,sz:11,col:'#ffe9a8',al:'left',pri:2}],
        info:{title:'The site\'s slope: '+BIM_LAND_SLOPE[mainC][2]+' for the most part, '+BIM_LAND_SLOPE[mainC][4],
          rows:[['Mean',bimDispNum(sum/stot,1)+'%'],['Steepest',bimDispNum(mx,1)+'%'+falls]].concat(BIM_LAND_SLOPE.map(function(C2,j){return [C2[2],bimLandPct(sc[j],stot)];})),
          method:'The cells inside the '+(S.ring?'property line':'ring of its buildings')+', each by Horn\'s method',source:D.src}});
    }
    return {E:E,run:{legend:BIM_LAND_SLOPE.map(function(C2){return {name:C2[2]+': '+C2[4],short:C2[3]+'%',col:C2[5],kind:'fill'};}),source:D.srcShort,note:''}};
  }
  /* aspect, read for warmth: 0 the coolest, facing the pole, to 4 the warmest, facing the equator */
  function bimLandWarm(d8,lat){var az=d8*45,eq=lat<0?0:180,dd=Math.abs(((az-eq)%360+540)%360-180);return 4-Math.round(dd/45);}
  function bimDgAspectRun(S){
    var D=bimLandGround(S);
    if(!D)return bimLandNone();
    var st=bimSunSettings(),lat=bimSunNum(st.lat)?st.lat:40,hn=bimLandHornOf(D),M=bimLandSiteMask(D,S),N=D.nx*D.nz,cls=new Int8Array(N),cnt=[],sc=[],tot=0,stot=0,i,k,E=[],a2=D.cell*D.cell;
    for(i=0;i<9;i++){cnt.push(0);sc.push(0);}
    for(k=0;k<N;k++){
      cls[k]=-1;
      if(!D.ok[k]||!isFinite(hn.aspect[k]))continue;
      cls[k]=hn.aspect[k]<0?8:bimLandDir8(hn.aspect[k]);
      cnt[cls[k]]++;tot++;if(M[k]){sc[cls[k]]++;stot++;}
    }
    for(i=0;i<9;i++){
      if(!cnt[i])continue;
      var flat=i===8,col=flat?BIM_LAND_FLATCOL:BIM_LAND_WARM[bimLandWarm(i,lat)],mask=new Uint8Array(N),nm=flat?'Flat (under '+BIM_LAND_FLAT+'%)':'Facing '+BIM_LAND_DIRNAME[BIM_LAND_DIRS[i]];
      for(k=0;k<N;k++)if(cls[k]===i)mask[k]=1;
      var rings=bimLandRings(D,mask,0.03);
      if(!rings.length)continue;
      var w=flat?-1:bimLandWarm(i,lat);
      E.push({k:flat?'flat':'dir:'+BIM_LAND_DIRS[i],name:'Aspect: '+nm.toLowerCase(),g:{kind:'line',pts:[],bands:[{lv:i,col:col,rings:rings}]},s:{fill:col,fop:0.55},
        info:{title:nm+(flat?'':(w===4?': the warmest, facing the equator':(w===0?': the coolest, facing the pole':(w===3?': warm':(w===1?': cool':': between'))))),
          rows:[['Of the ground around',bimLandPct(cnt[i],tot)+' ('+bimLandHa(cnt[i]*a2)+')'],['Of the site',stot?bimLandPct(sc[i],stot):'\u2014']],
          method:'Horn (1981): the way each '+D.cell+' m cell falls, clockwise from true north; under '+BIM_LAND_FLAT+'% it is flat',source:D.src}});
    }
    if(stot){
      var mainA=0;for(i=1;i<9;i++)if(sc[i]>sc[mainA])mainA=i;
      var cy=bimLandAt(D,S.c[0],S.c[1]),cp=[S.c[0],(cy===null?S.y:cy)+0.05,S.c[1]],wm=mainA===8?-1:bimLandWarm(mainA,lat);
      E.push({k:'site',name:'Aspect at the site',g:{kind:'line',pts:[]},sym:{type:'dot',p:cp,r:4,col:mainA===8?BIM_LAND_FLATCOL:BIM_LAND_WARM[wm]},
        lb:[{t:mainA===8?'Site: flat for the most part':'Site: faces '+BIM_LAND_DIRS[mainA]+(wm>=3?', warm':(wm<=1?', cool':'')),p:cp,sz:11,col:'#ffe9a8',al:'left',pri:2}],
        info:{title:mainA===8?'The site is flat for the most part':'The site faces '+BIM_LAND_DIRNAME[BIM_LAND_DIRS[mainA]]+' for the most part',
          rows:BIM_LAND_DIRS.map(function(dn,j){return ['Facing '+dn,bimLandPct(sc[j],stot)];}).concat([['Flat',bimLandPct(sc[8],stot)]]),method:'The cells inside the '+(S.ring?'property line':'ring of its buildings'),source:D.src}});
    }
    var eqD=lat<0?'N':'S',poD=lat<0?'S':'N';
    return {E:E,run:{legend:[{name:'Facing '+BIM_LAND_DIRNAME[eqD]+', the warmest',short:eqD,col:BIM_LAND_WARM[4],kind:'fill'},{name:'Facing '+(lat<0?'NE or NW':'SE or SW'),short:lat<0?'NE, NW':'SE, SW',col:BIM_LAND_WARM[3],kind:'fill'},
      {name:'Facing east or west',short:'E, W',col:BIM_LAND_WARM[2],kind:'fill'},{name:'Facing '+(lat<0?'SE or SW':'NE or NW'),short:lat<0?'SE, SW':'NE, NW',col:BIM_LAND_WARM[1],kind:'fill'},
      {name:'Facing '+BIM_LAND_DIRNAME[poD]+', the coolest',short:poD,col:BIM_LAND_WARM[0],kind:'fill'},{name:'Flat, under '+BIM_LAND_FLAT+'%',short:'flat',col:BIM_LAND_FLATCOL,kind:'fill'}],source:D.srcShort,note:''}};
  }
  /* water flow: the flow lines, the divides between the large catchments, the land draining onto the
     site, and where the site's water leaves it */
  function bimDgFlowRun(S){
    var D=bimLandGround(S);
    if(!D)return bimLandNone();
    var Y=bimLandHydroOf(D),M=bimLandSiteMask(D,S),E=[],N=D.nx*D.nz,a2=D.cell*D.cell,i,k,W=[1.1,1.7,2.4,3.1,3.8],tot=0;
    for(k=0;k<N;k++)if(D.ok[k])tot++;
    var meth='Priority-Flood (Barnes, Lehman and Mulla, 2014) fills the hollows; D8 (O\'Callaghan and Mark, 1984) sends each '+D.cell+' m cell to its steepest neighbour';
    bimLandLinks(D,Y).forEach(function(lk){
      var P=bimLandDP(lk.nodes.map(function(n){var p=bimLandP(D,n);return [p[0],p[2],p[1]];}),0.8,false).map(function(q){return [q[0],q[2],q[1]];});
      if(P.length<2)return;
      var ac=Y.acc[lk.to],o=Math.max(1,Math.min(5,lk.order)),lbl=[];
      if(lk.outlet&&ac>=10000){
        var e=P[P.length-1],b=P[P.length-2];
        lbl.push({t:bimLandHa(ac)+' runs off to the '+BIM_LAND_DIRNAME[BIM_LAND_DIRS[bimLandDir8(bimLandAz(e[0]-b[0],e[2]-b[2]))]],p:e,sz:10,col:'#bfe0ff',pri:3});
      }
      E.push({k:'flow:'+lk.from+'-'+lk.to,name:'Flow line, order '+lk.order,g:{kind:'line',pts:P},s:{stroke:'#3b8fd9',w:W[o-1],head:true,op:0.95},lb:lbl,
        info:{title:'Water running over the ground: '+bimLandHa(ac)+' drains through its end',rows:[['Order',lk.order+(lk.order>1?' (Strahler: two of order '+(lk.order-1)+' have joined)':' (it starts here)')],['Draining',bimLandHa(ac)],['Ends',lk.outlet?'off the ground analysed':'where it joins another']],
          method:meth+'; a flow line where '+bimLandHa(BIM_LAND_STREAM)+' or more drains',source:D.src}});
    });
    /* the large catchments, each named at its middle; the divides between them dashed, each once */
    var big={};
    Y.outlets.filter(function(o){return Y.outCells[o]>=BIM_LAND_CATCH*tot;}).sort(function(p,q){return Y.outCells[q]-Y.outCells[p]||p-q;}).forEach(function(o){
      var sx=0,sz=0,n=0,j;
      big[o]=1;
      for(k=0;k<N;k++)if(Y.lab[k]===o){sx+=k%D.nx;sz+=(k-k%D.nx)/D.nx;n++;}
      var ci=Math.round(sx/n),cj=Math.round(sz/n),ck=cj*D.nx+ci,bd=Infinity;
      if(Y.lab[ck]!==o)for(j=0;j<N;j++)if(Y.lab[j]===o){var dx=j%D.nx-ci,dz=(j-j%D.nx)/D.nx-cj;if(dx*dx+dz*dz<bd){bd=dx*dx+dz*dz;ck=j;}}
      E.push({k:'catch:'+o,name:'Catchment, '+bimLandHa(n*a2),g:{kind:'line',pts:[]},
        lb:[{t:'Catchment, '+bimLandHa(n*a2),p:bimLandP(D,ck,0.1),sz:10,col:'#b8cde0',pri:4}],
        info:{title:'A catchment: '+bimLandHa(n*a2)+' of the ground around drains to one point',rows:[['Area',bimLandHa(n*a2)],['Of the ground analysed',bimLandPct(n,tot)]],
          method:meth+'; each cell belongs to the outlet it drains to',source:D.src}});
    });
    bimLandDivides(D,Y,big).forEach(function(dv){
      var lines=[];
      dv.lines.forEach(function(L0){
        var L=bimLandDP(L0.map(function(g){return [D.x0+g[0]*D.cell,D.z0+g[1]*D.cell];}),D.cell,false);   /* the cells' steps eased: their inner corners stand 0.71 of a cell off the line through the outer ones */
        if(L.length>=2)lines.push(L.map(function(q){var y=bimLandAt(D,q[0],q[1]);return [bimLandR(q[0]),bimLandR((y===null?0:y)+0.06),bimLandR(q[1])];}));
      });
      if(!lines.length)return;
      E.push({k:'divide:'+dv.a+'-'+dv.b,name:'Divide between catchments',g:{kind:'lines',lines:lines},s:{stroke:'#8fa9c4',w:1.1,dash:[6,4],op:0.85},
        info:{title:'A divide: the water either side of it runs to a different place',rows:[['One side','a catchment of '+bimLandHa(Y.outCells[dv.a]*a2)],['The other','a catchment of '+bimLandHa(Y.outCells[dv.b]*a2)]],
          method:meth+'; the line runs along the edges between the cells of the two catchments',source:D.src}});
    });
    /* the land draining onto the site, and where its water leaves it */
    var U=bimLandUpstream(D,Y,M),nu=0,ns=0,ux=0,uz=0,um=new Uint8Array(N);
    for(k=0;k<N;k++){if(M[k])ns++;else if(U[k]){nu++;ux+=k%D.nx;uz+=(k-k%D.nx)/D.nx;}if(U[k]||M[k])um[k]=1;}
    if(ns){
      var ur=bimLandRings(D,um,0.05),up=nu?bimLandP(D,Math.round(uz/nu)*D.nx+Math.round(ux/nu),0.1):[S.c[0],S.y,S.c[1]];
      E.push({k:'upstream',name:'Draining onto the site',g:{kind:'lines',lines:ur,closed:true,bands:[{lv:0,col:'#7fb5e6',rings:ur}]},s:{stroke:'#7fb5e6',w:1.2,fill:'#7fb5e6',fop:0.22},
        lb:[{t:nu?bimLandHa(nu*a2)+' drains onto the site':'Nothing drains onto the site',p:up,sz:11,col:'#cfe6ff',al:'left',pri:2}],
        info:{title:nu?bimLandHa(nu*a2)+' of the ground around drains onto the site':'The site is high ground: no water runs onto it',rows:[['Upstream of the site',bimLandHa(nu*a2)],['With the site',bimLandHa((nu+ns)*a2)]],
          method:meth+'; every cell whose water reaches the site',source:D.src}});
      bimLandExits(D,Y,M).forEach(function(x,j){
        var P=x.path.map(function(n){return bimLandP(D,n,0.12);}),e=P[P.length-1],dn=BIM_LAND_DIRNAME[BIM_LAND_DIRS[bimLandDir8(bimLandAz(e[0]-P[0][0],e[2]-P[0][2]))]];
        E.push({k:'exit:'+x.k,name:'Where the site drains',g:{kind:'line',pts:P},s:{stroke:'#1f6fb2',w:2.6,head:true},
          lb:[{t:'Drains to the '+dn,p:e,sz:11,col:'#cfe6ff',al:'left',pri:j?3:2}],
          info:{title:'The site\'s water leaves it here, running to the '+dn,rows:[['From the site and above it',bimLandHa(x.acc)]],method:meth,source:D.src}});
      });
    }
    return {E:E,run:{legend:[{name:'Flow line, wider by its order',short:'flow',col:'#3b8fd9',kind:'line'},{name:'Divide between catchments',short:'divide',col:'#8fa9c4',kind:'dash'},
      {name:'Draining onto the site',short:'onto site',col:'#7fb5e6',kind:'fill'},{name:'Where the site drains',short:'drains',col:'#1f6fb2',kind:'line'}],source:D.srcShort,note:''}};
  }
  /* ponds: where the filled ground stands BIM_LAND_POND or more over the real one */
  function bimDgPondsRun(S){
    var D=bimLandGround(S);
    if(!D)return bimLandNone();
    var Y=bimLandHydroOf(D),N=D.nx*D.nz,E=[],a2=D.cell*D.cell;
    Y.ponds.forEach(function(p){
      var mask=new Uint8Array(N),i;
      for(i=0;i<p.cells.length;i++)mask[p.cells[i]]=1;
      var rings=bimLandRings(D,mask,0.06),dp=bimLandP(D,p.deep,0.1);
      if(!rings.length)return;
      E.push({k:'pond:'+p.deep,name:'Pond, '+bimDispNum(p.depth,2)+' m deep',g:{kind:'marks',pts:[],marks:[{p:dp,t:''}],bands:[{lv:0,col:'#3f7fcf',rings:rings}]},s:{fill:'#3f7fcf',fop:0.5,mark:'#9fd0ff'},
        lb:[{t:bimDispNum(p.depth,1)+' m deep, '+bimDispNum(p.volume,0)+' m\u00b3',p:dp,sz:10,col:'#cfe6ff',al:'left',pri:3}],
        info:{title:'Water collects here: '+bimDispNum(p.depth,2)+' m at the deepest',rows:[['Area',bimLandHa(p.area)],['Volume',bimDispNum(p.volume,1)+' m\u00b3'],['Deepest',bimDispNum(p.depth,2)+' m'],
          ['Spills at',bimLandHeightText(D,p.level,2)]],method:'Priority-Flood: the cells the filled ground stands '+bimDispNum(BIM_LAND_POND*100,0)+' cm or more above, joined; '+bimLandHa(BIM_LAND_POND_AREA)+' or more',source:D.src}});
    });
    return {E:E,run:{legend:[{name:'Pond, '+bimDispNum(BIM_LAND_POND*100,0)+' cm or deeper',short:'pond',col:'#3f7fcf',kind:'fill'},{name:'Its deepest point',short:'deepest',col:'#9fd0ff',kind:'dot'}],
      source:D.srcShort,note:Y.pondsAll?(Y.pondsAll>Y.ponds.length?'The '+Y.ponds.length+' largest of '+Y.pondsAll:''):'No pond: the ground drains everywhere'}};
  }
  /* flood zones: FEMA's, read as FEMA classes them */
  function bimLandZoneOf(p){
    var z=String(p.FLD_ZONE||p.fld_zone||'').toUpperCase().replace(/\s+/g,''),st=String(p.ZONE_SUBTY||p.zone_subty||'').toUpperCase(),sf=String(p.SFHA_TF||p.sfha_tf||'').toUpperCase();
    if(/FLOODWAY/.test(st))return 'floodway';
    if(sf==='T'||/^(A|AE|AH|AO|AR|A99|V|VE|A\d+|V\d+)(\/|$)/.test(z))return /^V/.test(z)?'coastal':'sfha';
    if((z==='X'&&/0\.2|1 PCT/.test(st))||z==='B')return 'x02';
    if(z==='D')return 'undetermined';
    return null;
  }
  function bimLandBfe(p){
    var v=parseFloat(p.STATIC_BFE!==undefined?p.STATIC_BFE:p.static_bfe);
    if(!isFinite(v)||v<=-9000)return null;
    var u=String(p.LEN_UNIT||p.len_unit||'Feet'),ft=/^f/i.test(u),m=ft?v*0.3048:v,dat=String(p.V_DATUM||p.v_datum||'').replace(/^\s+|\s+$/g,'');
    return {m:m,text:(ft?bimDispNum(v,1)+' ft ('+bimDispNum(m,2)+' m)':bimDispNum(v,2)+' m')+(dat?', '+dat:''),short:ft?bimDispNum(v,1)+' ft':bimDispNum(v,2)+' m'};
  }
  function bimLandClip(r,b){
    r=bimClipHalfPlane(r,1,0,b[2]);if(r.length<3)return r;
    r=bimClipHalfPlane(r,-1,0,-b[0]);if(r.length<3)return r;
    r=bimClipHalfPlane(r,0,1,b[3]);if(r.length<3)return r;
    return bimClipHalfPlane(r,0,-1,-b[1]);
  }
  function bimLandInRings(p,R){var n=0,i;for(i=0;i<R.length;i++)if(bimPointInPoly(p,R[i]))n++;return n%2===1;}
  /* a label's place in the zone: the middle of its largest ring when that is in it, else its point nearest the site */
  function bimLandLabelAt(R,S){
    var big=null,ba=-1,i,j;
    for(i=0;i<R.length;i++){var ar=Math.abs(bimPolyArea(R[i]));if(ar>ba){ba=ar;big=R[i];}}
    if(!big)return null;
    var cx=0,cz=0;for(j=0;j<big.length;j++){cx+=big[j][0];cz+=big[j][1];}cx/=big.length;cz/=big.length;
    if(bimLandInRings([cx,cz],R))return [cx,cz];
    var best=big[0],bd=Infinity;
    for(j=0;j<big.length;j++){var dx=big[j][0]-S.c[0],dz=big[j][1]-S.c[1];if(dx*dx+dz*dz<bd){bd=dx*dx+dz*dz;best=big[j];}}
    return best;
  }
  /* FEMA's zones around the site, cut to the square analysed, as rings in plan; the most hazardous one
     the site's centre is in */
  function bimLandFloodZones(S){
    var LD=A3D.site&&A3D.site.land,F=LD&&LD.flood,out={F:F,zones:[],site:null,present:{}},i,j,seen={},rank=99;
    if(!F||!F.features)return out;
    var box=[S.c[0]-BIM_LAND_HALF,S.c[1]-BIM_LAND_HALF,S.c[0]+BIM_LAND_HALF,S.c[1]+BIM_LAND_HALF];
    for(i=0;i<F.features.length;i++){
      var p=F.features[i].p||{},zc=bimLandZoneOf(p);
      if(!zc)continue;
      var parts=bimGeoParts(F.features[i].g||{}),rings=[];
      for(j=0;j<parts.length;j++){
        if(parts[j].kind!=='ring')continue;
        var pos=bimGeoPositions(parts[j].pts);
        if(!pos||pos.length<3)continue;
        var r=bimLandClip(pos.map(function(q){return bimGeoToModel(q[0],q[1]);}),box);
        if(r.length<3)continue;
        rings.push(r);   /* as published, not simplified: two zones keep their one edge */
      }
      if(!rings.length)continue;
      if(bimLandInRings([S.c[0],S.c[1]],rings)&&BIM_LAND_ZORDER.indexOf(zc)<rank){rank=BIM_LAND_ZORDER.indexOf(zc);out.site={zc:zc,p:p};}
      out.present[zc]=1;
      var key='zone:'+String(p.FLD_AR_ID||p.fld_ar_id||('f'+i));
      if(seen[key])key+='-'+i;
      seen[key]=1;
      out.zones.push({key:key,zc:zc,p:p,rings:rings});
    }
    return out;
  }
  function bimDgFloodRun(S){
    var Z0=bimLandFloodZones(S),F=Z0.F,E=[],D=bimLandGround(S),present=Z0.present,siteZ=Z0.site;
    if(!F)return {E:[],run:{note:'Not fetched yet: Analyze site gets FEMA\'s flood map'}};
    if(F.outside)return {E:[],run:{note:'FEMA maps US sites only'}};
    if(F.error&&!F.features)return {E:[],run:{note:'FEMA\'s map: '+F.error}};
    var feats=F.features||[],src='FEMA National Flood Hazard Layer ('+(F.host||'hazards.fema.gov')+'), '+F.fetched;
    function y3(q,lift){var y=D?bimLandAt(D,q[0],q[1]):null;return [bimLandR(q[0]),bimLandR((y===null?S.y:y)+lift),bimLandR(q[1])];}
    Z0.zones.forEach(function(z){
      var p=z.p,zc=z.zc,Z=BIM_LAND_ZONES[zc],rings=z.rings;
      var zn=String(p.FLD_ZONE||p.fld_zone||'').replace(/^\s+|\s+$/g,''),bfe=bimLandBfe(p),lp=bimLandLabelAt(rings,S),sub=String(p.ZONE_SUBTY||p.zone_subty||'').replace(/^\s+|\s+$/g,'');
      E.push({k:z.key,name:'Flood zone '+zn+(zc==='floodway'?', floodway':''),g:{kind:'line',pts:[],bands:[{lv:Z.lv,col:Z.col,rings:rings.map(function(r2){return r2.map(function(q){return y3(q,0.05);});})}]},s:{fill:Z.col,fop:0.42},
        lb:lp?[{t:'Zone '+zn+(zc==='floodway'?', floodway':(zc==='x02'?' (0.2%)':''))+(bfe?', BFE '+bfe.short:''),p:y3(lp,0.1),sz:10,col:'#d9e9ff',pri:3}]:[],
        info:{title:Z.name+': zone '+zn,rows:[['Zone',zn+(sub?' ('+sub.toLowerCase()+')':'')],['Base flood elevation',bfe?bfe.text:'not given'],['Special flood hazard area',String(p.SFHA_TF||p.sfha_tf||'').toUpperCase()==='T'?'yes':'no']],
          method:'FEMA\'s zones as published, cut to 150 m around the site',source:src}});
    });
    var cp=y3([S.c[0],S.c[1]],0.1),sz2=siteZ?BIM_LAND_ZONES[siteZ.zc]:null;
    E.push({k:'site',name:'Flood zone at the site',g:{kind:'line',pts:[]},sym:{type:'dot',p:cp,r:4,col:sz2?sz2.col:'#9aa7b4'},
      lb:[{t:siteZ?'Site: zone '+String(siteZ.p.FLD_ZONE||siteZ.p.fld_zone)+', '+sz2.site:'Site: outside the mapped flood zones',p:cp,sz:11,col:'#d9e9ff',al:'left',pri:2}],
      info:{title:siteZ?'The site is in zone '+String(siteZ.p.FLD_ZONE||siteZ.p.fld_zone)+': '+sz2.site:'The site is outside FEMA\'s mapped flood zones',rows:[['Zones around it',Object.keys(present).length?BIM_LAND_ZORDER.filter(function(z){return present[z];}).map(function(z){return BIM_LAND_ZONES[z].short;}).join(', '):'none'],['Features read',String(feats.length)+(F.more?' (more were there)':'')]],
        method:'The site\'s centre against each zone',source:src}});
    return {E:E,run:{legend:BIM_LAND_ZORDER.filter(function(z){return present[z];}).map(function(z){var Z=BIM_LAND_ZONES[z];return {name:Z.name,short:Z.short,col:Z.col,kind:'fill'};}),
      source:'FEMA National Flood Hazard Layer',note:feats.length?'':'No flood zone mapped within 150 m'}};
  }
"""

# the analyses, after V164's six
rep("    {id:'noise',name:'Noise',col:'#f08a24'}];\n",
    "    {id:'noise',name:'Noise',col:'#f08a24'},\n"
    "    /* __acad3dV165: land and water; slope and aspect cover the ground, so they start hidden */\n"
    "    {id:'contours',name:'Contours',col:'#b98a4e'},\n"
    "    {id:'slope',name:'Slope',col:'#fd8d3c',hidden:true},\n"
    "    {id:'aspect',name:'Aspect',col:'#fc8d59',hidden:true},\n"
    "    {id:'flow',name:'Water flow',col:'#3b8fd9'},\n"
    "    {id:'ponds',name:'Ponds',col:'#3f7fcf'},\n"
    "    {id:'flood',name:'Flood zones',col:'#3d85d8'}];\n")
rep("  var BIM_DG_RUN={frame:bimDgFrameRun,sun:bimDgSunRun,shadow:bimDgShadowRun,wind:bimDgWindRun,views:bimDgViewsRun,noise:bimDgNoiseRun};\n",
    LAND +
    "  var BIM_DG_RUN={frame:bimDgFrameRun,sun:bimDgSunRun,shadow:bimDgShadowRun,wind:bimDgWindRun,views:bimDgViewsRun,noise:bimDgNoiseRun,\n"
    "    contours:bimDgContoursRun,slope:bimDgSlopeRun,aspect:bimDgAspectRun,flow:bimDgFlowRun,ponds:bimDgPondsRun,flood:bimDgFloodRun};   /* __acad3dV165 */\n")

assert all(ord(ch) < 128 for ch in LAND), 'non-ASCII in the land block'
out = txt.encode('utf-8')
SRC.write_bytes(out)
print('wrote %s: %d bytes, sha256 %s' % (SRC, len(out), hashlib.sha256(out).hexdigest()))
