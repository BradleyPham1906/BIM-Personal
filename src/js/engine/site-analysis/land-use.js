  /* ================= __acad3dV168: Site analysis IV, land =================
     Land use by LBCS's activities; the figure-ground and its density by Spacematrix's measures; the
     green and trees by 3-30-300; the zoning around the site in its council's colours. Each is drawn
     from what the project holds -- the context (V133, V157), the walks (V161), the sight lines (V164),
     a council's layer (V134, V160) -- with the standards and the app's settings the registry's (V167). */
  /* LBCS's families, their hues adjusted so that every pair passes the colour-blindness checks: on the
     light map, normal vision 18.5 at worst and protan or deutan 7.2 (OKLab x 100, the 6 to 8 band that
     needs a second cue); on the dark plan 16.3 and 8.6. Grey, slate and white are LBCS's own neutrals.
     The second cues: a texture where a colour sits close to a neighbour's, the family's name on large
     areas, an outline on every area (yellow is 1.89:1 on the light map), the key, and Properties. */
  var BIM_LD_FAM=[
    {c:1000,short:'Residential',lt:{f:'#eda100',o:'#8a5e00'},dk:{f:'#d19a00',o:'#f0c040'}},
    {c:2000,short:'Commercial',lt:{f:'#e34948',o:'#8f1f1e'},dk:{f:'#e66767',o:'#f39a9a'}},
    {c:3000,short:'Industrial',tex:'45',lt:{f:'#7a3fb0',o:'#4a2370',i:'rgba(255,255,255,0.6)'},dk:{f:'#8e5cc8',o:'#c2a2ea',i:'rgba(20,24,28,0.6)'}},
    {c:4000,short:'Institutional',lt:{f:'#3b8ee8',o:'#1b4f8f'},dk:{f:'#4a9af0',o:'#a0c8f8'}},
    {c:5000,short:'Movement',lt:{f:'#9a9a9a',o:'#555555'},dk:{f:'#8f949b',o:'#c8ccd0'}},
    {c:6000,short:'Assembly',tex:'135',lt:{f:'#2f4f4f',o:'#0f2222',i:'rgba(255,255,255,0.6)'},dk:{f:'#5f8a8a',o:'#a8c8c8',i:'rgba(20,24,28,0.6)'}},
    {c:7000,short:'Leisure',lt:{f:'#62c27a',o:'#2d6f3e'},dk:{f:'#6fd08a',o:'#b0e8c0'}},
    {c:8000,short:'Natural resources',tex:'dot',lt:{f:'#008300',o:'#004d00',i:'rgba(255,255,255,0.7)'},dk:{f:'#008300',o:'#7fd07f',i:'rgba(255,255,255,0.7)'}},
    {c:9000,short:'No activity',lt:{f:'#ffffff',o:'#8a8f96'},dk:{f:'#e8eaec',o:'#8a8f96'}}];
  /* which tag says a feature's use, the most telling first: a building by its own amenity, shop or
     office before its building value; an area by a port before its industrial land use */
  var BIM_LD_BKEYS=['amenity','shop','office','tourism','leisure','social_facility','building','landuse','man_made','power','aeroway','industrial'];
  var BIM_LD_AKEYS=['industrial','amenity','leisure','tourism','aeroway','landuse','natural','man_made','power','railway'];
  var BIM_LD_RC=5,BIM_LD_RCC=2,BIM_LD_LABEL=2000;   /* the grids the land use and the canopy are counted on (m: a crown 4.8 m across covers a 2 m cell's centre wherever it stands); an area is named on the plan from this size (m2) */
  function bimLdFam(c){var i;for(i=0;i<BIM_LD_FAM.length;i++)if(BIM_LD_FAM[i].c===c)return BIM_LD_FAM[i];return BIM_LD_FAM[8];}
  function bimLdCol(c){var F=bimLdFam(c);return bimMvLight()?F.lt:F.dk;}
  function bimLdName(c){var L=bimStd('lbcs.activity','families')||[],i;for(i=0;i<L.length;i++)if(+L[i][0]===c)return String(L[i][1]);return 'LBCS '+c;}
  function bimLdPct(p){return bimDispNum(p*100,1)+'%';}
  /* a feature's family by the registry's crosswalk, or null where its tags do not say */
  function bimLdClassOf(t,bld){
    var X=bimStd('app.land','xw')||{},T=X.tags||{},W=X.weak||[],K=bld?BIM_LD_BKEYS:BIM_LD_AKEYS,i,k,v;
    t=t||{};
    for(i=0;i<K.length;i++){
      k=K[i];v=t[k];
      if(v===undefined||v===null||v===''||v==='no')continue;
      v=String(v);
      if(T.hasOwnProperty(k+'='+v))return {c:+T[k+'='+v],tag:k+'='+v,weak:W.indexOf(k+'='+v)>=0};
      if(T.hasOwnProperty(k+'=*'))return {c:+T[k+'=*'],tag:k+'='+v,weak:false};
    }
    return null;
  }
  function bimLdCen(P){var x=0,z=0,i;for(i=0;i<P.length;i++){x+=P[i][0];z+=P[i][1];}return P.length?[x/P.length,z/P.length]:[0,0];}
  function bimLdBox(L){var b=[Infinity,Infinity,-Infinity,-Infinity];L.forEach(function(P){P.forEach(function(p){b[0]=Math.min(b[0],p[0]);b[1]=Math.min(b[1],p[1]);b[2]=Math.max(b[2],p[0]);b[3]=Math.max(b[3],p[1]);});});return b;}
  function bimLdMeets(L,W){var b=bimLdBox(L);return b[2]>=W.x0&&b[0]<=W.x1&&b[3]>=W.z0&&b[1]<=W.z1;}
  /* the square around the site the land use and form are measured in */
  function bimLdWin(S){var w=bimStd('app.land','window'),h=w/2;return {x0:S.c[0]-h,z0:S.c[1]-h,x1:S.c[0]+h,z1:S.c[1]+h,w:w};}
  function bimLdSq(W,y){return [[W.x0,y,W.z0],[W.x1,y,W.z0],[W.x1,y,W.z1],[W.x0,y,W.z1]];}
  function bimLdCirc(x,z,r,y,n){var P=[],k;for(k=0;k<n;k++)P.push([x+r*Math.cos(2*Math.PI*k/n),y,z+r*Math.sin(2*Math.PI*k/n)]);return P;}
  /* the context's areas -- land use and green -- each feature whole: its outer rings, its holes */
  function bimLdAreas(){
    var G={},order=[],i,o,c,q;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];c=o.context;
      if(!c||(c.kind!=='landuse'&&c.kind!=='green')||!o.closed||!o.pts||o.pts.length<3)continue;
      q=bimObjOffset(o);
      var key=c.kind+':'+(c.osm||'')+':'+(c.id===undefined?o.id:c.id),P=o.pts.map(function(p){return [p[0]+q[0],p[1]+q[2]];});
      if(!G[key]){G[key]={key:key,t:c.tags||{},name:String((c.tags||{}).name||'').slice(0,60),outer:[],holes:[]};order.push(key);}
      (c.part==='hole'?G[key].holes:G[key].outer).push(P);
    }
    return order.map(function(k){
      var a=G[k],ar=0;
      a.outer.forEach(function(r){ar+=bimPolyArea(r);});
      a.holes.forEach(function(r){ar-=bimPolyArea(r);});
      a.area=Math.max(0,ar);a.cls=bimLdClassOf(a.t,false);
      return a;
    }).filter(function(a){return a.outer.length;});
  }
  function bimLdIn(a,x,z){
    var i,inn=false;
    for(i=0;i<a.outer.length;i++)if(bimPointInPoly([x,z],a.outer[i])){inn=true;break;}
    if(!inn)return false;
    for(i=0;i<a.holes.length;i++)if(bimPointInPoly([x,z],a.holes[i]))return false;
    return true;
  }
  /* the context's buildings: the footprint less its courtyards where kept, the storeys -- building:levels
     where mapped (less building:min_level for a part), else the height over a storey's, at least one
     (momepy's floor area with V168's floor of one) -- and the ground floor's when it stands on the ground */
  function bimLdBuildings(){
    var B=[],i,o,c,q,st=bimCtxLevelH();
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];c=o.context;
      if(!c||c.kind!=='buildings'||!c.footprint||c.footprint.length<3)continue;
      q=bimObjOffset(o);
      var t=c.tags||{},fp=c.footprint.map(function(p){return [p[0]+q[0],p[1]+q[2]];}),mn=+c.minHeight||0,h=+c.height||0;
      var holes=(c.holes||[]).map(function(r){return r.map(function(p){return [p[0]+q[0],p[1]+q[2]];});}).filter(function(r){return r.length>=3&&bimPointInPoly(r[0],fp);});
      var lv=parseFloat(t['building:levels']),ml=parseFloat(t['building:min_level']),sn,from;
      if(isFinite(lv)&&lv>0&&lv<300){sn=Math.max(0,lv-(isFinite(ml)&&ml>0?ml:0));from='levels';}
      else{sn=Math.max(1,Math.floor((h-mn)/st+1e-9));from='height';}
      var ar=bimPolyArea(fp);holes.forEach(function(r){ar-=bimPolyArea(r);});
      B.push({id:o.id,name:o.name,t:t,fp:fp,holes:holes,ground:!(mn>0),h:h,s:sn,from:from,area:Math.max(0,ar),part:!!c.buildingPart,
        whole:c.building?(c.building.osm+':'+c.building.id):((c.osm||'')+':'+(c.id===undefined?o.id:c.id)),cls:bimLdClassOf(t,true),yards:!!(c.courtyards&&!c.holes)});
    }
    return B;
  }
  /* a polygon cut to a box (Sutherland and Hodgman) */
  function bimLdClip(P,x0,z0,x1,z1){
    function cut(L,inside,isect){
      var out=[],i;
      for(i=0;i<L.length;i++){
        var a=L[i],b=L[(i+1)%L.length],ia=inside(a),ib=inside(b);
        if(ia)out.push(a);
        if(ia!==ib)out.push(isect(a,b));
      }
      return out;
    }
    var R=cut(P,function(p){return p[0]>=x0;},function(a,b){return [x0,a[1]+(x0-a[0])/(b[0]-a[0])*(b[1]-a[1])];});
    if(R.length)R=cut(R,function(p){return p[0]<=x1;},function(a,b){return [x1,a[1]+(x1-a[0])/(b[0]-a[0])*(b[1]-a[1])];});
    if(R.length)R=cut(R,function(p){return p[1]>=z0;},function(a,b){return [a[0]+(z0-a[1])/(b[1]-a[1])*(b[0]-a[0]),z0];});
    if(R.length)R=cut(R,function(p){return p[1]<=z1;},function(a,b){return [a[0]+(z1-a[1])/(b[1]-a[1])*(b[0]-a[0]),z1];});
    return R;
  }
  function bimLdAreaIn(b,x0,z0,x1,z1){
    var R=bimLdClip(b.fp,x0,z0,x1,z1),a=R.length>=3?bimPolyArea(R):0;
    b.holes.forEach(function(h){var Q=bimLdClip(h,x0,z0,x1,z1);if(Q.length>=3)a-=bimPolyArea(Q);});
    return Math.max(0,a);
  }
  /* Spacematrix in a box: GSI the ground floors over the land, FSI the floor area over it, OSR
     (1 - GSI) / FSI, L FSI over GSI; the land the whole box, streets and all */
  function bimLdForm(B,x0,z0,x1,z1){
    var A=(x1-x0)*(z1-z0),gf=0,fa=0,n=0,i;
    for(i=0;i<B.length;i++){
      var a=bimLdAreaIn(B[i],x0,z0,x1,z1);
      if(!(a>0))continue;
      n++;
      if(B[i].ground)gf+=a;
      fa+=a*B[i].s;
    }
    var gsi=gf/A,fsi=fa/A;
    return {A:A,gf:gf,fa:fa,gsi:gsi,fsi:fsi,osr:fsi>0?(1-gsi)/fsi:null,l:gf>0?fa/gf:null,n:n};
  }
  function bimLdFormRows(C){
    return [['GSI, the ground covered',bimDispNum(C.gsi,3)],['FSI, the floor area over the land',bimDispNum(C.fsi,3)],['OSR, the open space for each floor area',C.osr===null?'no floor area':bimDispNum(C.osr,3)],
      ['L, the storeys on average',C.l===null?'no ground floor':bimDispNum(C.l,2)],['Ground floors',bimLandHa(C.gf)],['Floor area',bimLandHa(C.fa)],['Buildings and parts in it',String(C.n)]];
  }
  /* the grain: the buildings whose footprint's middle is in the square, each once with its parts */
  function bimLdGrain(B,W){
    var seen={},n=0,area=0,lev=0,hgt=0,yards=0,i;
    for(i=0;i<B.length;i++){
      var b=B[i],c=bimLdCen(b.fp);
      if(c[0]<W.x0||c[0]>W.x1||c[1]<W.z0||c[1]>W.z1)continue;
      if(b.from==='levels')lev++;else hgt++;
      if(b.yards)yards++;
      if(b.ground)area+=b.area;
      if(!seen[b.whole]){seen[b.whole]=1;n++;}
    }
    return {n:n,ha:n/(W.w*W.w/10000),mean:n?area/n:0,lev:lev,hgt:hgt,yards:yards};
  }
  /* each cell of the square's grid: a building's own use first, then the smallest area over it, then
     grass and flowerbeds, which OpenStreetMap calls not strictly land use and which take the class of
     what they lie in; null where nothing says */
  function bimLdRaster(S,B,Ar){
    var W=bimLdWin(S),rc=BIM_LD_RC,nx=Math.round(W.w/rc),R=[],rank=[],k;
    for(k=0;k<nx*nx;k++){R.push(0);rank.push(Infinity);}
    function lay(cls,tier,area,inside,bb){
      var i0=Math.max(0,Math.floor((bb[0]-W.x0)/rc)),i1=Math.min(nx-1,Math.floor((bb[2]-W.x0)/rc)),j0=Math.max(0,Math.floor((bb[1]-W.z0)/rc)),j1=Math.min(nx-1,Math.floor((bb[3]-W.z0)/rc)),r=tier*1e12+area,ii,jj;
      for(ii=i0;ii<=i1;ii++)for(jj=j0;jj<=j1;jj++){
        var x=W.x0+(ii+0.5)*rc,z=W.z0+(jj+0.5)*rc,kk=jj*nx+ii;
        if(r<rank[kk]&&inside(x,z)){rank[kk]=r;R[kk]=cls;}
      }
    }
    B.forEach(function(b){
      if(!b.cls||!b.ground)return;
      lay(b.cls.c,0,b.area,function(x,z){if(!bimPointInPoly([x,z],b.fp))return false;for(var h=0;h<b.holes.length;h++)if(bimPointInPoly([x,z],b.holes[h]))return false;return true;},bimLdBox([b.fp]));
    });
    Ar.forEach(function(a){if(a.cls)lay(a.cls.c,a.cls.weak?2:1,a.area,function(x,z){return bimLdIn(a,x,z);},bimLdBox(a.outer));});
    return {R:R,nx:nx,rc:rc,W:W};
  }
  /* the mix: each family's share of the cells that say one (1000 to 8000), and Cervero's entropy index,
     Shannon's H over them divided by ln N, N the families the registry counts */
  function bimLdMix(S,B,Ar){
    var G=bimLdRaster(S,B,Ar),cnt={},tot=G.R.length,k,n=0,none=0,un=0,N=bimStd('app.land','mix_n'),H=0,sh=[];
    for(k=0;k<tot;k++){var c=G.R[k];if(!c)un++;else if(c===9000)none++;else{cnt[c]=(cnt[c]||0)+1;n++;}}
    BIM_LD_FAM.forEach(function(F){if(F.c<9000&&cnt[F.c])sh.push({c:F.c,n:cnt[F.c],p:cnt[F.c]/n});});
    sh.forEach(function(x){H-=x.p*Math.log(x.p);});
    return {sh:sh,n:n,tot:tot,none:none,un:un,H:H,N:N,ix:(N>=2&&n)?H/Math.log(N):null};
  }
  /* what the context's last fetch covered: the square around the property, its radius as fetched */
  function bimLdReach(){
    var a=bimCtxArea(),L=A3D.site&&A3D.site.context&&A3D.site.context.last,st=bimCtxSettings();
    if(!a||!L||!(L.radius>0))return null;
    var h=a.half-st.radius+L.radius;
    return {x0:a.cx-h,z0:a.cz-h,x1:a.cx+h,z1:a.cz+h};
  }
  function bimLdTrees(){
    var T=[],i,o,c,q;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];c=o.context;
      if(!c||c.kind!=='trees'||!o.pts||!o.pts.length)continue;
      q=bimObjOffset(o);
      var h=+c.height||bimCtxTreeH();
      T.push({id:o.id,x:o.pts[0][0]+q[0],z:o.pts[0][1]+q[2],r:Math.max(0.5,(+c.crown||h*0.6)/2),h:h,name:o.name});
    }
    return T;
  }
  function bimLdWood(a){return a.t.natural==='wood'||a.t.landuse==='forest';}
  /* the canopy: the cells of the neighbourhood under a crown or in a wood, of those the context reaches */
  function bimLdCanopy(S,T,Ar){
    var R=bimStd('app.land','hood'),rc=BIM_LD_RCC,re=bimLdReach(),cx=S.c[0],cz=S.c[1],n=Math.ceil(R/rc),N2=2*n,gx0=cx-n*rc,gz0=cz-n*rc,mark=[],cnt=0,can=0,i,j,k;
    for(k=0;k<N2*N2;k++)mark.push(0);
    function span(a,b,g0){return [Math.max(0,Math.floor((a-g0)/rc)),Math.min(N2-1,Math.floor((b-g0)/rc))];}
    T.forEach(function(t){
      var I=span(t.x-t.r,t.x+t.r,gx0),J=span(t.z-t.r,t.z+t.r,gz0),ii,jj;
      for(ii=I[0];ii<=I[1];ii++)for(jj=J[0];jj<=J[1];jj++){var x=gx0+(ii+0.5)*rc,z=gz0+(jj+0.5)*rc;if((x-t.x)*(x-t.x)+(z-t.z)*(z-t.z)<=t.r*t.r)mark[jj*N2+ii]=1;}
    });
    var woods=Ar.filter(bimLdWood);
    woods.forEach(function(a){
      var b=bimLdBox(a.outer),I=span(b[0],b[2],gx0),J=span(b[1],b[3],gz0),ii,jj;
      for(ii=I[0];ii<=I[1];ii++)for(jj=J[0];jj<=J[1];jj++){var kk=jj*N2+ii;if(!mark[kk]&&bimLdIn(a,gx0+(ii+0.5)*rc,gz0+(jj+0.5)*rc))mark[kk]=1;}
    });
    for(i=0;i<N2;i++)for(j=0;j<N2;j++){
      var x=gx0+(i+0.5)*rc,z=gz0+(j+0.5)*rc;
      if((x-cx)*(x-cx)+(z-cz)*(z-cz)>R*R)continue;
      if(re&&(x<re.x0||x>re.x1||z<re.z0||z>re.z1))continue;
      cnt++;if(mark[j*N2+i])can++;
    }
    var full=re?Math.max(0,Math.min(cx-re.x0,re.x1-cx,cz-re.z0,re.z1-cz)):R;
    return {R:R,share:cnt?can/cnt:null,cells:cnt,can:can,area:cnt*rc*rc,full:Math.min(R,full),clipped:!!re&&full<R,trees:T.length,woods:woods.length};
  }
  /* the trees seen: V164's sight lines at eye height from the site's centre, a tree counted where a line
     meets its crown first, within the registry's distance */
  function bimLdSeen(S){
    var see=bimStd('app.land','see'),iv=bimDgIsovist(S,S.y+1.6,bimDgObstacles(true),see),seen={},L=[],k;
    for(k=0;k<iv.hit.length;k++){var h=iv.hit[k];if(h&&h.kind==='t'&&!seen[h.id]){seen[h.id]=1;L.push({id:h.id,name:h.name,d:iv.D[k],k:k});}}
    return {list:L,n:L.length,see:see};
  }
  /* the public green spaces: parks, gardens, recreation grounds and village greens no one has made
     private; big enough when at least the registry's smallest */
  function bimLdGreens(Ar){
    var m2=bimStd('green.33300','green_min')*10000;
    return Ar.filter(function(a){var t=a.t;return (t.leisure==='park'||t.leisure==='garden'||t.landuse==='recreation_ground'||t.landuse==='village_green')&&!/^(private|no)$/.test(String(t.access||''));})
      .map(function(a){a.big=a.area>=m2-0.001;return a;});   /* to the square centimetre: 0.49 x 10000 is a hair over 4900 */
  }
  /* the walk network's pieces, from V161's walk times, by 60 m cells */
  function bimLdNet(A){
    var pc=[],G={},c=60;
    (A.segs||[]).forEach(function(g){for(var i=4;i+2<g.length;i+=3)pc.push([g[i-3],g[i-2],g[i-1],g[i],g[i+1],g[i+2]]);});
    pc.forEach(function(p,k){
      var i0=Math.floor(Math.min(p[0],p[3])/c),i1=Math.floor(Math.max(p[0],p[3])/c),j0=Math.floor(Math.min(p[1],p[4])/c),j1=Math.floor(Math.max(p[1],p[4])/c),i,j;
      for(i=i0;i<=i1;i++)for(j=j0;j<=j1;j++)(G[i+','+j]||(G[i+','+j]=[])).push(k);
    });
    return {pc:pc,G:G,c:c};
  }
  /* the walk to an area: to a point of the network inside it, or to its edge -- every 15 m -- from the
     nearest street within 60 m, as V161 reaches a park; in metres at the walk's own speed */
  function bimLdWalkTo(N,v,g){
    var best=null,bb=bimLdBox(g.outer),i,k;
    function take(d,p){if(!best||d<best.d)best={d:d,p:p};}
    N.pc.forEach(function(p){
      [[p[0],p[1],p[2]],[p[3],p[4],p[5]]].forEach(function(q){if(q[0]>=bb[0]&&q[0]<=bb[2]&&q[1]>=bb[1]&&q[1]<=bb[3]&&bimLdIn(g,q[0],q[1]))take(q[2]*v,[q[0],q[1]]);});
    });
    function near(x,z){
      var r=60,i0=Math.floor((x-r)/N.c),i1=Math.floor((x+r)/N.c),j0=Math.floor((z-r)/N.c),j1=Math.floor((z+r)/N.c),bd=Infinity,bt=null,seen={},ii,jj;
      for(ii=i0;ii<=i1;ii++)for(jj=j0;jj<=j1;jj++)(N.G[ii+','+jj]||[]).forEach(function(kk){
        if(seen[kk])return;seen[kk]=1;
        var p=N.pc[kk],dx=p[3]-p[0],dz=p[4]-p[1],l2=dx*dx+dz*dz,u=l2>1e-12?Math.max(0,Math.min(1,((x-p[0])*dx+(z-p[1])*dz)/l2)):0,px=p[0]+u*dx,pz=p[1]+u*dz,d=Math.sqrt((x-px)*(x-px)+(z-pz)*(z-pz));
        if(d<=r&&d<bd){bd=d;bt=p[2]+u*(p[5]-p[2]);}
      });
      if(bt!==null)take(bt*v+bd,[x,z]);
    }
    g.outer.forEach(function(r){
      for(i=0;i<r.length;i++){
        var a=r[i],b=r[(i+1)%r.length],len=Math.sqrt((b[0]-a[0])*(b[0]-a[0])+(b[1]-a[1])*(b[1]-a[1])),n=Math.max(1,Math.ceil(len/15));
        for(k=0;k<n;k++)near(a[0]+(b[0]-a[0])*k/n,a[1]+(b[1]-a[1])*k/n);
      }
    });
    return best;
  }
  /* 3-30-300 at the site, as Browning et al. measure it, with the stand-ins said */
  function bimLd33300(S){
    var Ar=bimLdAreas(),T=bimLdTrees(),A=A3D.site&&A3D.site.access,seen=bimLdSeen(S),can=bimLdCanopy(S,T,Ar),G=bimLdGreens(Ar),walks={},best=null,wd=!!(A&&Array.isArray(A.segs)&&A.speed>0);
    if(wd){var N=bimLdNet(A);G.forEach(function(g){var w=bimLdWalkTo(N,A.speed,g);walks[g.key]=w;if(g.big&&w&&(!best||w.d<best.d))best={g:g,d:w.d,p:w.p};});}
    return {Ar:Ar,T:T,seen:seen,can:can,G:G,walks:walks,best:best,walkData:wd,
      ok3:seen.n>=bimStd('green.33300','trees'),ok30:can.share!==null&&can.share*100>=bimStd('green.33300','canopy'),ok300:!!best&&best.d<=bimStd('green.33300','walk')};
  }
  function bimLd33300Rows(Q){
    var C=Q.can,b=Q.best;
    return [['Trees seen',Q.seen.n+' within '+bimStdSay('app.land','see')+' ('+bimStdSay('green.33300','trees')+' asked): '+(Q.ok3?'met':'not met')],
      ['Canopy',(C.share===null?'none counted':bimLdPct(C.share)+' of '+bimLandHa(C.area))+' ('+bimStdSay('green.33300','canopy')+' asked): '+(Q.ok30?'met':'not met')+
        (C.clipped?'; the context reaches '+bimDispNum(C.full,0)+' m of the '+bimStdSay('app.land','hood')+' neighbourhood':'')],
      ['Public green space',b?(b.g.name||'a green space')+', '+bimLandHa(b.g.area)+', '+Math.round(b.d)+' m along the streets ('+bimStdSay('green.33300','walk')+' asked): '+(Q.ok300?'met':'not met'):
        (Q.walkData?'none of '+bimStdSay('green.33300','green_min')+' or more reached by the walk network: not met':'no walk times yet: Analyze site works them out')]];
  }
  /* ---- 1. land use ---- */
  function bimDgLanduseRun(S){
    var Ar=bimLdAreas(),B=bimLdBuildings(),E=[],y=S.y+0.03,W=bimLdWin(S),light=bimMvLight(),have={},G={},src='OpenStreetMap (ODbL), by LBCS\'s activities (APA)';
    if(!Ar.some(function(a){return a.cls;})&&!B.some(function(b){return b.cls;}))return {E:[],run:{note:'No land use around the site yet: Analyze site gets it from OpenStreetMap'}};
    var MX=bimLdMix(S,B,Ar),parts=MX.sh.slice().sort(function(p,q){return q.n-p.n;}),ws=bimStdSay('app.land','window');
    function R3(r,h){return r.map(function(p){return [p[0],h,p[1]];});}
    Ar.forEach(function(a){
      if(!a.cls||!bimLdMeets(a.outer,W))return;
      var F=bimLdFam(a.cls.c),C=bimLdCol(a.cls.c),rings=a.outer.concat(a.holes).map(function(r){return R3(r,y);}),c0=bimLdCen(a.outer[0]);
      have[F.c]=1;
      E.push({k:'area:'+a.key,name:F.short+(a.name?': '+a.name:''),g:{kind:'lines',lines:rings,closed:true,bands:[{lv:a.cls.weak?-1e12:-a.area,col:C.f,rings:rings,tex:F.tex||null,ink:C.i||null}]},
        s:{stroke:C.o,w:1,fop:0.55},lb:a.area>=BIM_LD_LABEL?[{t:F.short,p:[c0[0],y,c0[1]],sz:10,col:'#f4f1e3',pri:4}]:[],
        info:{title:F.short+': '+(a.name||a.cls.tag),rows:[['LBCS activity',F.c+', '+bimLdName(F.c)],['OpenStreetMap',a.cls.tag+(a.cls.weak?': it takes the class of what it lies in':'')],['Area',bimLandHa(a.area)]],
          method:'OpenStreetMap\'s tags by the app\'s crosswalk to LBCS\'s activities, checked against their descriptions (Properties, Site, Standards)',source:src}});
    });
    B.forEach(function(b){if(b.cls&&b.ground&&bimLdMeets([b.fp],W))(G[b.cls.c]||(G[b.cls.c]=[])).push(b);});
    BIM_LD_FAM.forEach(function(F){
      var L=G[F.c];if(!L)return;
      var C=bimLdCol(F.c),fa=0,tg={};
      have[F.c]=1;
      L.forEach(function(b){fa+=b.area;tg[b.cls.tag]=(tg[b.cls.tag]||0)+1;});
      E.push({k:'bld:'+F.c,name:F.short+' buildings',g:{kind:'lines',lines:L.map(function(b){return R3(b.fp,y+b.h);}),closed:true,bands:L.map(function(b){return {lv:1,col:C.f,pts:R3(b.fp,y)};})},
        s:{stroke:C.o,w:1,fillOver:C.f,fo:0.85,tex:F.tex||null,ink:C.i||null,fop:0.55},
        info:{title:bimSaN(L.length,'building')+' used for '+F.short.toLowerCase()+' (LBCS '+F.c+')',rows:[['LBCS activity',F.c+', '+bimLdName(F.c)],['Footprints',bimLandHa(fa)],['From',Object.keys(tg).sort().map(function(k){return k+' '+tg[k];}).join(', ')]],
          method:'A building\'s own use, by its tags, before the area it stands in',source:src}});
    });
    var rows=parts.map(function(x){return [bimLdFam(x.c).short+' ('+x.c+')',bimLdPct(x.p)];});
    rows.push(['No activity, or not said',bimLdPct((MX.none+MX.un)/MX.tot)+' of the square, left out of the mix']);
    rows.push(['Entropy index',MX.ix===null?'not worked out: no family, or fewer than two counted':bimDispNum(MX.ix,3)+' (H '+bimDispNum(MX.H,3)+', over '+bimSaN(MX.N,'family','families')+')']);
    E.push({k:'window',name:'Land use, the '+ws+' square',g:{kind:'line',pts:bimLdSq(W,y),closed:true},s:{stroke:light?'#5d6670':'#c8ccd0',w:1.2,dash:[6,4],op:0.9},
      lb:[{t:MX.ix!==null?'Land use mix '+bimDispNum(MX.ix,2)+' over '+bimSaN(MX.N,'family','families'):'Land use mix: not worked out',p:[W.x0+W.w/2,y,W.z0-6],sz:11,col:'#f4f1e3',pri:1}],
      info:{title:'Land use in the '+ws+' square around the site, by area'+(parts.length?': '+parts.slice(0,3).map(function(x){return bimLdFam(x.c).short.toLowerCase()+' '+bimLdPct(x.p);}).join(', '):''),rows:rows,
        method:'Each '+BIM_LD_RC+' m cell of the square takes a building\'s own use, else the smallest area over it, else the grass\'s or flowerbed\'s; each family\'s share of the cells that say one, 1000 to 8000; Shannon\'s entropy over them divided by ln N (Cervero\'s index, as Chen and Song quote it), N the families counted',source:src}});
    var leg=BIM_LD_FAM.filter(function(F){return have[F.c];}).map(function(F){var C=bimLdCol(F.c);return {name:F.short+' ('+F.c+')',short:F.short,col:C.f,kind:'fill',tex:F.tex||null,ink:C.i||null};});
    if(leg.length<8)leg.push({name:'The square measured',short:ws+' square',col:light?'#5d6670':'#c8ccd0',kind:'dash'});
    return {E:E,run:{legend:leg,source:'LBCS\'s activities (APA) from OpenStreetMap'}};
  }
  /* ---- 2. figure-ground and density ---- */
  function bimDgFigureRun(S){
    var B=bimLdBuildings(),E=[],W=bimLdWin(S),y=S.y+0.02,light=bimMvLight(),cl=bimStd('app.land','cell'),n=Math.max(1,Math.round(W.w/cl)),cw=W.w/n,i,j;
    if(!B.length)return {E:[],run:{note:'No buildings around the site yet: Analyze site gets them from OpenStreetMap'}};
    var F=bimLdForm(B,W.x0,W.z0,W.x1,W.z1),gr=bimLdGrain(B,W),ws=bimStdSay('app.land','window'),src='OpenStreetMap buildings (ODbL); Spacematrix\'s measures',cg=light?'#fbfaf7':'#eef0f2',cc=light?'#8a8f96':'#6b7480';
    var meth='Spacematrix (Berghauser Pont and Haupt): GSI the ground floors over the land, FSI the floor area over it, OSR (1 - GSI) / FSI, L FSI over GSI; the footprints cut to the square, the land the whole square, streets and all; the storeys from building:levels, else the height over '+bimStdSay('app.context','storey')+' a storey, at least one';
    E.push({k:'ground',name:'Open ground',g:{kind:'line',pts:[],bands:[{lv:0,col:cg,rings:[bimLdSq(W,y)]}]},s:{fop:0.85},
      info:{title:'The open ground of the '+ws+' square: '+bimLdPct(1-F.gsi),rows:[['OSR',F.osr===null?'no floor area':bimDispNum(F.osr,3)]],method:'The square less the buildings\' ground floors',source:src}});
    E.push({k:'figure',name:'Buildings',g:{kind:'lines',lines:B.filter(function(b){return bimLdMeets([b.fp],W);}).map(function(b){return b.fp.map(function(p){return [p[0],y+b.h,p[1]];});}),closed:true},
      s:{stroke:light?'#0f1215':'#05070a',w:0.8,fillOver:'#1d2329',fo:0.92},
      info:{title:bimSaN(gr.n,'building')+' in the square: '+bimDispNum(gr.ha,1)+' a hectare, '+bimLandHa(gr.mean)+' a footprint on average',
        rows:[['Buildings',String(gr.n)],['A hectare',bimDispNum(gr.ha,2)],['Footprint on average',bimLandHa(gr.mean)],['Storeys',gr.lev+' footprints from building:levels, '+gr.hgt+' from the height']],
        method:'The buildings whose footprint\'s middle is in the square, a building with parts once',source:src}});
    for(i=0;i<n;i++)for(j=0;j<n;j++){
      var x0=W.x0+i*cw,z0=W.z0+j*cw,C=bimLdForm(B,x0,z0,x0+cw,z0+cw),no=j*n+i+1;
      E.push({k:'cell:'+i+','+j,name:'Cell '+no+': FSI '+bimDispNum(C.fsi,2),g:{kind:'line',pts:[[x0,y,z0],[x0+cw,y,z0],[x0+cw,y,z0+cw],[x0,y,z0+cw]],closed:true},s:{stroke:cc,w:0.8,dash:[3,3],op:0.8},
        lb:[{t:'FSI '+bimDispNum(C.fsi,2),p:[x0+cw/2,y,z0+cw/2],sz:9,col:'#e8edf2',pri:5}],
        info:{title:'Cell '+no+', '+bimStdSay('app.land','cell')+' across: GSI '+bimDispNum(C.gsi,2)+', FSI '+bimDispNum(C.fsi,2),rows:bimLdFormRows(C),method:meth,source:src}});
    }
    var rw=bimLdFormRows(F);
    rw.push(['Grain',bimSaN(gr.n,'building')+', '+bimDispNum(gr.ha,1)+' a hectare, '+bimLandHa(gr.mean)+' a footprint on average']);
    rw.push(['Storeys',gr.lev+' footprints from building:levels, '+gr.hgt+' from the height at '+bimStdSay('app.context','storey')+' a storey']);
    if(gr.yards)rw.push(['Courtyards',gr.yards+' fetched before V168 are counted as built: fetch the context again for their outlines']);
    rw.push(['Spacematrix\'s type','not given: the bounds of its types are in the book, which was not read']);
    E.push({k:'site',name:'Density in the square',g:{kind:'line',pts:bimLdSq(W,y),closed:true},s:{stroke:light?'#1d2329':'#e8edf2',w:1.6,op:0.95},
      lb:[{t:'GSI '+bimDispNum(F.gsi,2)+', FSI '+bimDispNum(F.fsi,2)+', L '+(F.l===null?'none':bimDispNum(F.l,1)),p:[W.x0+W.w/2,y,W.z0-6],sz:11,col:'#f4f1e3',pri:1}],
      info:{title:'The '+ws+' square around the site: GSI '+bimDispNum(F.gsi,2)+', FSI '+bimDispNum(F.fsi,2)+(F.osr===null?'':', OSR '+bimDispNum(F.osr,2))+(F.l===null?'':', L '+bimDispNum(F.l,1)),rows:rw,method:meth,source:src}});
    return {E:E,run:{legend:[{name:'Buildings',short:'buildings',col:'#1d2329',kind:'fill'},{name:'Open ground',short:'open ground',col:cg,kind:'fill'},{name:'Cells, '+bimStdSay('app.land','cell')+' across',short:'cells',col:cc,kind:'dash'}],
      source:'Spacematrix\'s measures from OpenStreetMap buildings'}};
  }
  /* ---- 3. green and trees, and 3-30-300 ---- */
  function bimDgGreenRun(S){
    var Q=bimLd33300(S),E=[],y=S.y+0.05,light=bimMvLight(),woods=Q.Ar.filter(bimLdWood),src='OpenStreetMap trees, woods and parks (ODbL)',tn=bimTrueNorthDeg();
    if(!Q.T.length&&!woods.length&&!Q.G.length)return {E:[],run:{note:'No trees or green space around the site yet: Analyze site gets them from OpenStreetMap'}};
    var cT=light?'#2e8b57':'#3fae5f',cW=light?'#1f6f3a':'#2f8f50',cG=light?'#8fd694':'#7fc98a',cO=light?'#2d6f3e':'#b0e8c0',leg=[],C=Q.can;
    function R3(r){return r.map(function(p){return [p[0],y,p[1]];});}
    if(Q.T.length){
      E.push({k:'crowns',name:'Tree crowns',g:{kind:'line',pts:[],bands:Q.T.map(function(t){return {lv:2,col:cT,pts:bimLdCirc(t.x,t.z,t.r,y,12)};})},s:{fop:0.6},
        info:{title:bimSaN(Q.T.length,'mapped tree')+', their crowns',rows:[['Crowns','diameter_crown where mapped, else 0.6 of the height (the context\'s rule, V157)']],method:'Each tree at its crown, a circle',source:src}});
      leg.push({name:'Tree crowns',short:'trees',col:cT,kind:'fill'});
    }
    woods.forEach(function(a){
      var rings=a.outer.concat(a.holes).map(R3);
      E.push({k:'wood:'+a.key,name:'Woods'+(a.name?': '+a.name:''),g:{kind:'lines',lines:rings,closed:true,bands:[{lv:1,col:cW,rings:rings,tex:'dot',ink:'rgba(255,255,255,0.6)'}]},s:{stroke:cW,w:1,fop:0.6},
        info:{title:'Woods'+(a.name?', '+a.name:'')+': '+bimLandHa(a.area),rows:[['OpenStreetMap',a.t.natural==='wood'?'natural=wood':'landuse=forest'],['Area',bimLandHa(a.area)]],method:'Counted as canopy',source:src}});
    });
    if(woods.length)leg.push({name:'Woods',short:'woods',col:cW,kind:'fill',tex:'dot',ink:'rgba(255,255,255,0.6)'});
    Q.G.forEach(function(g){
      var rings=g.outer.concat(g.holes).map(R3),w=Q.walks[g.key],c0=bimLdCen(g.outer[0]),tag=g.t.leisure?'leisure='+g.t.leisure:'landuse='+g.t.landuse;
      E.push({k:'green:'+g.key,name:g.name||'Public green space',g:{kind:'lines',lines:rings,closed:true,bands:[{lv:0,col:cG,rings:rings}]},s:{stroke:cO,w:g.big?1.6:1,dash:g.big?null:[4,3],fop:0.6},
        lb:g.big&&g.area>=BIM_LD_LABEL?[{t:(g.name||'Green space')+', '+bimLandHa(g.area),p:[c0[0],y,c0[1]],sz:10,col:'#eef7ee',pri:3}]:[],
        info:{title:(g.name||'A public green space')+': '+bimLandHa(g.area)+(g.big?'':', under the '+bimStdSay('green.33300','green_min')+' 3-30-300 counts'),
          rows:[['OpenStreetMap',tag],['Area',bimLandHa(g.area)],['Access',g.t.access?String(g.t.access):'not mapped: taken as public'],
            ['Walk from the site',w?Math.round(w.d)+' m along the streets':(Q.walkData?'not reached: no street within 60 m of its edge':'no walk times yet: Analyze site works them out')]],
          method:'Parks, gardens, recreation grounds and village greens no one has mapped private',source:src}});
    });
    if(Q.G.length)leg.push({name:'Public green space',short:'green space',col:cG,kind:'fill'});
    E.push({k:'hood',name:'The neighbourhood, '+bimStdSay('app.land','hood'),g:{kind:'line',pts:bimDgCircle(S,C.R,y,72),closed:true},s:{stroke:cO,w:1.2,dash:[6,4],op:0.9},
      lb:[{t:'Canopy '+(C.share===null?'none':bimLdPct(C.share))+(C.clipped?' (to '+bimDispNum(C.full,0)+' m, as far as the context reaches)':' within '+bimStdSay('app.land','hood')),p:bimDgAt(S,0,C.R,y),sz:11,col:'#eef7ee',pri:2}],
      info:{title:'The canopy of the neighbourhood: '+(C.share===null?'none counted':bimLdPct(C.share)),rows:[['Canopy',C.share===null?'none counted':bimLdPct(C.share)+' of '+bimLandHa(C.area)],
          ['Asked',bimStdSay('green.33300','canopy')+' at least'],['Counted in','the '+bimStdSay('app.land','hood')+' circle'+(C.clipped?', cut to the context\'s square: whole only to '+bimDispNum(C.full,0)+' m':'')],['From',bimSaN(C.trees,'mapped tree')+', '+bimSaN(C.woods,'wood')]],
        method:'Each '+BIM_LD_RCC+' m cell under a crown or in a wood, of the cells in the circle; from mapped trees, not a land cover map, which Browning et al. rate best (ESA\'s WorldCover cannot be read from a page)',source:src}});
    if(Q.seen.list.length){
      var P=[];
      Q.seen.list.forEach(function(t){var a=(t.k*2+tn)*Math.PI/180;P.push([S.c[0],y+0.01,S.c[1]],[S.c[0]+Math.sin(a)*t.d,y+0.01,S.c[1]-Math.cos(a)*t.d]);});
      E.push({k:'seen',name:'Trees seen from the site',g:{kind:'segs',pts:P},s:{stroke:cT,w:1.2,op:0.9},
        info:{title:bimSaN(Q.seen.n,'tree')+' seen from the site within '+bimStdSay('app.land','see'),rows:Q.seen.list.slice(0,12).map(function(t){return [t.name||'Tree',Math.round(t.d)+' m'];}),
          method:'V164\'s sight lines, every 2 degrees at eye height from the site\'s centre: a tree counted where a line meets its crown first; a window view\'s stand-in',source:src}});
      leg.push({name:'A tree seen',short:'seen',col:cT,kind:'line'});
    }
    if(Q.best)E.push({k:'walk',name:'The nearest public green space',g:{kind:'line',pts:[]},sym:{type:'dot',p:[Q.best.p[0],y,Q.best.p[1]],r:5,col:cO},
      lb:[{t:(Q.best.g.name||'Green space')+': '+Math.round(Q.best.d)+' m along the streets',p:[Q.best.p[0],y,Q.best.p[1]],sz:10,col:'#eef7ee',al:'left',pri:2}],
      info:{title:'The nearest public green space of '+bimStdSay('green.33300','green_min')+' or more: '+(Q.best.g.name||'unnamed')+', '+Math.round(Q.best.d)+' m along the streets',
        rows:[['Area',bimLandHa(Q.best.g.area)],['Walk',Math.round(Q.best.d)+' m ('+bimStdSay('green.33300','walk')+' asked)']],method:'V161\'s walk times, to a point of the network inside it or to its edge from the nearest street within 60 m',source:src}});
    var met=[Q.ok3,Q.ok30,Q.ok300].filter(function(x){return x;}).length;
    E.push({k:'site',name:'3-30-300 at the site',g:{kind:'line',pts:[]},sym:{type:'dot',p:[S.c[0],y,S.c[1]],r:4,col:cT},
      lb:[{t:'3-30-300: '+met+' of 3 met',p:[S.c[0],y,S.c[1]+S.r*0.6],sz:11,col:'#eef7ee',pri:1}],
      info:{title:'3-30-300 at the site: '+met+' of 3 met',rows:bimLd33300Rows(Q),
        method:'Browning et al. (2024): the trees seen from the site by its sight lines, the canopy of the neighbourhood from mapped trees and woods, the walk along the streets to the nearest public green space',source:src+'; '+bimStdUsedText('green.33300')}});
    return {E:E,run:{legend:leg.slice(0,8),source:'3-30-300 (Browning et al.) from OpenStreetMap'}};
  }
  /* ---- 4. zoning around: a council layer's districts, its own colours ---- */
  /* __acad3dV168: a layer's own colours, as Esri's code reads an ArcGIS layer's drawingInfo: a unique
     value renderer keyed on field1 (with field2 and field3 joined by fieldDelimiter), each value's solid
     fill and its outline, the default symbol for the rest; the layer's transparency a percentage */
  function bimZnRgba(c,tr){
    if(!Array.isArray(c)||c.length<3)return null;
    var a=(c.length>3?+c[3]:255)/255*(1-(+tr||0)/100);
    return 'rgba('+Math.round(+c[0])+','+Math.round(+c[1])+','+Math.round(+c[2])+','+Math.max(0,Math.min(1,Math.round(a*1000)/1000))+')';
  }
  function bimZnSym(sy,tr){
    if(!sy||typeof sy!=='object')return null;
    return {f:(sy.type==='esriSFS'&&(!sy.style||sy.style==='esriSFSSolid'))?bimZnRgba(sy.color,tr):null,o:(sy.outline&&sy.outline.style!=='esriSLSNull')?bimZnRgba(sy.outline.color,tr):null};
  }
  function bimZnDrawing(js){
    var di=js&&js.drawingInfo,r=di&&di.renderer,tr=di?(+di.transparency||0):0,out={at:bimSaToday(),type:r&&r.type?String(r.type).slice(0,20):''};
    if(!r)return {at:out.at,none:'gives no colours'};
    if(r.type==='uniqueValue'){
      out.f=[r.field1,r.field2,r.field3].filter(function(x){return x;}).map(function(x){return String(x).slice(0,60);});
      out.d=typeof r.fieldDelimiter==='string'?r.fieldDelimiter.slice(0,5):',';
      out.v=(r.uniqueValueInfos||[]).slice(0,300).map(function(u){var q=bimZnSym(u&&u.symbol,tr)||{};return [String(u&&u.value!=null?u.value:'').slice(0,80),String((u&&u.label)||'').slice(0,80),q.f||null,q.o||null];});
      var ds=bimZnSym(r.defaultSymbol,tr);
      if(ds)out.def=[String(r.defaultLabel||'Other').slice(0,80),ds.f,ds.o];
    }else if(r.type==='simple'){var ss=bimZnSym(r.symbol,tr);if(ss)out.def=[String(r.label||'').slice(0,80),ss.f,ss.o];}
    else return {at:out.at,none:'colours by a '+out.type+' renderer, which the app does not read'};
    return out;
  }
  /* a feature's style: its value's, compared loosely (a number may come as a string), else the default */
  function bimZnStyleOf(D,p){
    if(!D||D.none)return null;
    if(D.f&&D.f.length&&D.v){
      var key=D.f.map(function(f){var v=p[f];return v==null?'':String(v);}).join(D.d||','),i;
      for(i=0;i<D.v.length;i++)if(D.v[i][0]==key)return {f:D.v[i][2],o:D.v[i][3],label:D.v[i][1]||D.v[i][0]};
    }
    return D.def?{f:D.def[1],o:D.def[2],label:D.def[0]}:null;
  }
  /* the first loaded layer whose areas name zoning districts, and the attribute, as V160 reads one */
  function bimLdZnPick(){
    var pick=null;
    bimDataList().forEach(function(L){
      if(pick)return;
      var M=bimDataModel(L),F=bimDataFeats(L.id),attr=null,k,i;
      if(!M)return;
      for(i=0;i<M.feats.length&&!attr;i++){
        var ft=M.feats[i],pr;
        if(!ft.rings.length)continue;
        pr=(F[ft.fi]&&F[ft.fi].p)||{};
        for(k in pr)if(pr.hasOwnProperty(k)&&BIM_ZN_ATTR.district.test(k)&&String(pr[k]).length&&!bimZnNum(pr[k])){attr=k;break;}
        if(!attr)for(k in pr)if(pr.hasOwnProperty(k)&&/zon/i.test(k)&&!/far|fsr|height/i.test(k)&&String(pr[k]).length&&!bimZnNum(pr[k])){attr=k;break;}
      }
      if(attr)pick={L:L,M:M,F:F,attr:attr};
    });
    return pick;
  }
  /* the districts around: each one's value and style, the site's, the shares of the zoned ground in the square */
  function bimLdZnAround(S){
    var Z=bimLdZnPick();
    if(!Z)return null;
    var W=bimLdWin(S),D=Z.L.drawing&&!Z.L.drawing.none?Z.L.drawing:null,feats=[],by={},order=[],col={},lot=null,tot=0;
    Z.M.feats.forEach(function(ft){
      if(!ft.rings.length)return;
      var pr=(Z.F[ft.fi]&&Z.F[ft.fi].p)||{},val=String(pr[Z.attr]==null?'':pr[Z.attr]).replace(/^\s+|\s+$/g,'').slice(0,40),inn=false,aw=0;
      if(!val)return;
      ft.rings.forEach(function(r){if(bimPointInPoly(S.c,r.pts))inn=!inn;});
      if(inn&&!lot)lot=val;
      ft.rings.forEach(function(r){var Q=bimLdClip(r.pts,W.x0,W.z0,W.x1,W.z1);if(Q.length>=3)aw+=(r.hole?-1:1)*bimPolyArea(Q);});
      var sy=bimZnStyleOf(D,pr);
      if(!col.hasOwnProperty(val))col[val]=sy&&sy.f?sy.f:null;
      if(aw>0){if(!by.hasOwnProperty(val)){by[val]=0;order.push(val);}by[val]+=aw;tot+=aw;}
      feats.push({ft:ft,val:val,inn:inn,sy:sy});
    });
    return {Z:Z,W:W,D:D,feats:feats,by:by,order:order.sort(function(a,b){return by[b]-by[a];}),col:col,lot:lot,tot:tot,src:Z.L.name+(Z.L.credit?' ('+Z.L.credit+')':'')};
  }
  function bimDgZoningRun(S){
    var DL=bimDataList(),E=[],y=S.y+0.04,light=bimMvLight(),cn=light?'#9aa7b4':'#7d8794',i;
    if(!DL.length)return {E:[],run:{note:'No council layer loaded: add one in Properties, Site, Data Layers, and its districts are drawn here'}};
    var Z=bimLdZnAround(S);
    if(!Z)return {E:[],run:{note:'None of the '+bimSaN(DL.length,'loaded layer')+' names zoning districts'}};
    var dr=Z.Z.L.drawing,how=Z.D?'the layer\'s own':(dr&&dr.none?'none: the layer '+dr.none:'not read yet: Analyze site reads them');
    Z.feats.forEach(function(x){
      var R=x.ft.rings.map(function(r){return r.pts;});
      if(!bimLdMeets(R,Z.W))return;
      var rings=R.map(function(r){return r.map(function(p){return [p[0],y,p[1]];});}),c0=bimLdCen(R[0]);
      E.push({k:'zone:'+x.ft.fi,name:'District '+x.val,g:{kind:'lines',lines:rings,closed:true,bands:[{lv:x.inn?1:0,col:x.sy&&x.sy.f?x.sy.f:cn,rings:rings}]},
        s:{stroke:x.sy&&x.sy.o?x.sy.o:(light?'#4b5563':'#c8ccd0'),w:x.inn?2.2:1.1,fop:Z.D?0.6:0.18},
        lb:x.ft.area>=BIM_LD_LABEL?[{t:x.val,p:[c0[0],y,c0[1]],sz:10,col:'#f4f1e3',pri:3}]:[],
        info:{title:'District '+x.val+(x.inn?': the site is in it':''),rows:[['District',x.val+(x.sy&&x.sy.label&&x.sy.label!==x.val?' ('+x.sy.label+')':'')],['Attribute',Z.Z.attr],['Colours',how]],
          method:'The council layer\'s districts as it publishes them, in its own colours where its drawing info gives them',source:Z.src}});
    });
    var rows=Z.order.slice(0,10).map(function(v){return [v,bimLdPct(Z.by[v]/Z.tot)+' of the zoned ground in the square'];});
    E.push({k:'site',name:'Zoning at the site',g:{kind:'line',pts:[]},sym:{type:'dot',p:[S.c[0],y,S.c[1]],r:4,col:light?'#1d2329':'#e8edf2'},
      lb:[{t:Z.lot?'Site: '+Z.lot:'Site: in none of the layer\'s districts',p:[S.c[0],y,S.c[1]],sz:11,col:'#f4f1e3',al:'left',pri:1}],
      info:{title:Z.lot?'The site is in district '+Z.lot:'The site is in none of the layer\'s districts',rows:rows,
        method:'The site\'s centre against each district; the shares cut to the '+bimStdSay('app.land','window')+' square',source:Z.src}});
    var leg=Z.order.slice(0,8).map(function(v){return {name:v,short:v,col:Z.col[v]||cn,kind:'fill'};});
    return {E:E,run:{legend:leg,source:'Zoning districts from '+Z.src,note:Z.D?'':(dr&&dr.none?'The layer '+dr.none+': its districts outlined and named':'The layer\'s own colours are read by Analyze site')}};
  }
  /* a texture for a class whose colour alone would not tell it from a neighbour's: lines at 45 or 135
     degrees, or dots, in its ink, a tile of the view's pixels */
  function bimDgTex(ctx,kind,ink){
    var K=kind+'|'+(ink||''),C=A3D_DG.tex||(A3D_DG.tex={});
    if(!C[K]){
      var t=document.createElement('canvas'),x;
      t.width=t.height=8;x=t.getContext('2d');
      x.strokeStyle=x.fillStyle=ink||'rgba(20,24,28,0.55)';x.lineWidth=1.2;
      if(kind==='dot'){x.beginPath();x.arc(4,4,1.3,0,2*Math.PI);x.fill();}
      else{
        x.beginPath();
        if(kind==='45'){x.moveTo(0,8);x.lineTo(8,0);x.moveTo(-2,2);x.lineTo(2,-2);x.moveTo(6,10);x.lineTo(10,6);}
        else{x.moveTo(0,0);x.lineTo(8,8);x.moveTo(-2,6);x.lineTo(2,10);x.moveTo(6,-2);x.lineTo(10,2);}
        x.stroke();
      }
      C[K]=t;
    }
    try{return ctx.createPattern(C[K],'repeat');}catch(eT){return null;}
  }
  /* the same texture in the keys of Analyze's rows, as CSS */
  function bimDgTexCss(kind,ink){
    var c=ink||'rgba(20,24,28,0.55)';
    if(kind==='dot')return 'background-image:radial-gradient('+c+' 1px,transparent 1.5px);background-size:4px 4px';
    return 'background-image:repeating-linear-gradient('+(kind==='45'?'45deg':'135deg')+','+c+' 0 1px,transparent 1px 4px)';
  }
  var BIM_DG_RUN={frame:bimDgFrameRun,sun:bimDgSunRun,shadow:bimDgShadowRun,wind:bimDgWindRun,views:bimDgViewsRun,noise:bimDgNoiseRun,
    contours:bimDgContoursRun,slope:bimDgSlopeRun,aspect:bimDgAspectRun,flow:bimDgFlowRun,ponds:bimDgPondsRun,flood:bimDgFloodRun,   /* __acad3dV165 */
    streets:bimDgStreetsRun,cycling:bimDgCyclingRun,transit:bimDgTransitRun,walk:bimDgWalkRun,needs:bimDgNeedsRun,vehicles:bimDgVehiclesRun,   /* __acad3dV166 */
    landuse:bimDgLanduseRun,figure:bimDgFigureRun,green:bimDgGreenRun,zoning:bimDgZoningRun};   /* __acad3dV168 */
  /* every analysis, or one, laid down from what the project holds now; one undo step */
  function bimDgRunAll(only){
    var S=bimDgSite(),out={},held=bimUndoHold,i;
    if(only&&!bimDgAn(only))return null;
    if(!held){pushUndo();bimUndoHold=true;}
    try{
      for(i=0;i<BIM_DG_AN.length;i++){
        var a=BIM_DG_AN[i].id;
        if(only&&only!==a)continue;
        try{var r=BIM_DG_RUN[a](S);out[a]=bimDgPlace(a,r.E,r.run);out[a].note=(r.run&&r.run.note)||'';}
        catch(eA){console.warn('[BIM] The '+a+' analysis failed',eA);out[a]={error:String(eA&&eA.message||eA),total:0,note:''};}
      }
    }finally{if(!held)bimUndoHold=false;}
    refreshTree();refreshLayers();refreshProps();paint();saveSoon();
    return out;
  }
  /* __acad3dV166: transit's PTAL in words, for its finding; access data from before V166 says what it said */
  function bimMvPtalText(S){
    var mv=S&&S.mv&&Array.isArray(S.mv.w)?S.mv:null,P;
    if(!mv)return 'Stops and lines from OpenStreetMap; how often they run needs the operator\'s timetable (GTFS).';
    P=bimMvPtal(S,mv);
    if(!P.lines.length)return 'No bus stop within '+bimDispNum(bimMvPtalWalk().bus,2)+' minutes or station within '+bimDispNum(bimMvPtalWalk().rail,2)+': PTAL 0 by TfL\'s method.';
    if(!P.have)return 'How often the '+bimSaN(P.lines.length,'line')+' within reach run is not mapped in OpenStreetMap, so no PTAL (TfL\'s method needs each line\'s headway).';
    return 'PTAL '+(P.floor?'at least ':'')+P.band+' by TfL\'s method (index '+bimDispNum(P.ai,1)+')'+(P.floor?', from the '+P.have+' of '+P.lines.length+' lines whose headway OpenStreetMap maps':', from the headways OpenStreetMap maps')+'.';
  }
  /* __acad3dV168: what the land says about the site, as findings */
  function bimLdAuto(){
    var A=[],ctx=A3D.site&&A3D.site.context&&A3D.site.context.last,osm='OpenStreetMap (ODbL), via Overpass',S,Ar,B,dt,ws;
    if(!ctx)return A;
    dt=ctx.date||bimSaToday();
    try{S=bimDgSite();Ar=bimLdAreas();B=bimLdBuildings();ws=bimStdSay('app.land','window');}catch(eL){console.warn('[BIM] The land could not be read',eL);return A;}
    try{
      if(Ar.some(function(a){return a.cls;})||B.some(function(b){return b.cls;})){
        var MX=bimLdMix(S,B,Ar),pt=MX.sh.slice().sort(function(p,q){return q.n-p.n;}).map(function(x){return bimLdFam(x.c).short.toLowerCase()+' '+bimLdPct(x.p);}),rest=MX.none+MX.un;
        A.push({auto:'location.landuse',cat:'location',title:'Land use mix',
          value:MX.n?'In the '+ws+' square around the site, by area: '+pt.join(', ')+'; the mix '+(MX.ix===null?'not worked out':bimDispNum(MX.ix,2))+' (Shannon\'s entropy over '+bimSaN(MX.N,'LBCS family','LBCS families')+': 1 an even balance, 0 one use)'+
            (rest?'; '+bimLdPct(rest/MX.tot)+' of the square says no activity, or nothing, and is left out':'')+'.':'No land use is mapped in the '+ws+' square around the site.',
          cls:'neutral',sev:1,source:osm+'; LBCS\'s activities (APA)',date:dt});
      }
    }catch(e1){console.warn('[BIM] The land use finding could not be worked out',e1);}
    try{
      if(B.length){
        var W=bimLdWin(S),F=bimLdForm(B,W.x0,W.z0,W.x1,W.z1),gr=bimLdGrain(B,W);
        A.push({auto:'location.density',cat:'location',title:'Density and form',
          value:'In the '+ws+' square around the site: GSI '+bimDispNum(F.gsi,2)+' (the ground the buildings cover), FSI '+bimDispNum(F.fsi,2)+' (their floor area over the land)'+(F.osr===null?'':', OSR '+bimDispNum(F.osr,2))+
            (F.l===null?'':', '+bimDispNum(F.l,1)+' storeys on average')+'; '+bimSaN(gr.n,'building')+', '+bimDispNum(gr.ha,1)+' a hectare, '+bimLandHa(gr.mean)+' a footprint on average. Storeys from building:levels for '+gr.lev+' footprints, from the height at '+
            bimStdSay('app.context','storey')+' a storey for '+gr.hgt+'.'+(gr.yards?' '+bimSaN(gr.yards,'building')+' fetched before V168 with courtyards counted as built.':''),
          cls:'neutral',sev:1,source:osm+'; Spacematrix\'s measures',date:dt});
      }
    }catch(e2){console.warn('[BIM] The density finding could not be worked out',e2);}
    try{
      var Q=bimLd33300(S);
      if(Q.T.length||Q.Ar.some(bimLdWood)||Q.G.length){
        var met=[Q.ok3,Q.ok30,Q.ok300].filter(function(x){return x;}).length;
        A.push({auto:'ecology.33300',cat:'ecology',title:'3-30-300',
          value:met+' of 3 met. '+bimLd33300Rows(Q).map(function(r){return r[0]+': '+r[1];}).join('. ')+'. The trees seen by the site\'s sight lines, a window view\'s stand-in; the canopy from mapped trees and woods, not a land cover map.',
          cls:met===3?'opportunity':(met<=1?'constraint':'neutral'),sev:met<=1?2:1,source:osm+'; Browning et al. (2024)',date:dt});
      }
    }catch(e3){console.warn('[BIM] The 3-30-300 finding could not be worked out',e3);}
    try{
      var Z=bimLdZnAround(S);
      if(Z&&Z.order.length)A.push({auto:'legal.zoningaround',cat:'legal',title:'Zoning around',
        value:(Z.lot?'The site is in district '+Z.lot:'The site is in none of the layer\'s districts')+'; the zoned ground in the '+ws+' square: '+Z.order.slice(0,6).map(function(v){return v+' '+bimLdPct(Z.by[v]/Z.tot);}).join(', ')+
          (Z.order.length>6?', and '+(Z.order.length-6)+' more':'')+'.',cls:'neutral',sev:1,source:Z.src,date:bimSaToday()});
    }catch(e4){console.warn('[BIM] The zoning around could not be worked out',e4);}
    return A;
  }
  /* __acad3dV166: what movement says about the site, as findings */
  function bimMvAuto(){
    var A=[],S=A3D.site&&A3D.site.access,mv=bimMvOf(),dt,src,i;
    if(!S||!mv)return A;
    dt=S.fetched;src=bimMvSrc(S);
    try{
      var ST=bimMvStress(mv),L=bimMvLotOf(S),R=bimMvReach(mv,ST,L),okL=0,allL=0,k,fr=[],worst=0,best=9;
      for(i=0;i<mv.w.length;i++){
        if(!(ST.W[i].lts>=1))continue;
        for(k=2;k<mv.w[i].length;k++){var l=bimMvSeg(mv,mv.w[i][k-1],mv.w[i][k]);allL+=l;if(R.ok[i]&&R.ok[i][k])okL+=l;}
      }
      (S.streets||[]).forEach(function(f){
        if(!f.n)return;
        var lv=0;
        for(i=0;i<mv.w.length;i++){var t=mv.t[mv.w[i][0]]||{};if(String(t.name||'')===f.n&&ST.W[i].lts>lv)lv=ST.W[i].lts;}
        if(lv){fr.push(f.n+' '+BIM_MV_LTS[lv].n+' ('+BIM_MV_LTS[lv].w+')');worst=Math.max(worst,lv);best=Math.min(best,lv);}
      });
      var nx=ST.X.filter(function(c){return !c.ctl&&c.lts>2&&bimAccLotDist(L,c.x,c.z)<=400;}).length,share=allL?okL/allL:0;
      A.push({auto:'access.cycling',cat:'access',title:'Cycling',
        value:(fr.length?'The lot fronts '+fr.join(', ')+'. ':'')+'From the lot, '+bimMvKm(okL)+' of the '+bimMvKm(allL)+' of streets and paths a bicycle may use within '+(mv.cut||mv.r)+' m are reached at low stress (LTS 2 or less, a detour of 25% at most)'+
          (nx?'; '+bimSaN(nx,'uncontrolled crossing')+' of a main street within 400 m '+(nx===1?'is':'are')+' stressful':'')+'. Levels by Mekuria, Furth and Nixon\'s criteria from the OpenStreetMap tags; speeds and lanes the class\'s where not mapped.',
        cls:(fr.length&&best<=2&&share>=0.3)?'opportunity':((fr.length&&best>=3)||share<0.1?'constraint':'neutral'),sev:1,source:src+'; level of traffic stress (MTI report 11-19)',date:dt});
    }catch(eC){console.warn('[BIM] The cycling finding could not be worked out',eC);}
    var dw=0,lowest=null,pref={s:0,l:1,c:2,a:3};
    for(i=0;i<mv.w.length;i++){
      var t2=mv.t[mv.w[i][0]]||{},near=Infinity,k2;
      if(t2.highway!=='service'||/^(parking_aisle|drive-through)$/.test(String(t2.service||'')))continue;
      for(k2=1;k2<mv.w[i].length;k2++)near=Math.min(near,bimAccLotDist(bimMvLotOf(S),mv.x[mv.w[i][k2]],mv.z[mv.w[i][k2]]));
      if(near<=3)dw++;
    }
    (S.streets||[]).forEach(function(f){if((f.c in pref)&&(!lowest||pref[f.c]<pref[lowest.c]))lowest=f;});
    var cps=mv.cp||[],cap=0,nc=0,parts=[];
    cps.forEach(function(c){if(c.cap){cap+=c.cap;nc++;}});
    if(dw)parts.push(bimSaN(dw,'driveway')+' or service road'+(dw===1?'':'s')+' into the lot');
    else if(lowest)parts.push('no driveway mapped into the lot: an entry from '+(lowest.n?lowest.n+' ('+bimAccStreetClass(lowest)+')':'the '+bimAccStreetClass(lowest))+', its lowest street, is marked provisional');
    else parts.push('no driveway mapped into the lot, and no street faces it');
    parts.push(cps.length?bimSaN(cps.length,'car park')+' within 400 m'+(nc?' ('+bimClimInt(cap)+' spaces mapped in '+nc+')':''):'no car park mapped within 400 m');
    if(mv.pe&&mv.pe.length)parts.push(bimSaN(mv.pe.length,'garage entrance')+' within 400 m');
    var fp=(S.streets||[]).filter(function(f){return f.n;}).map(function(f){
      var pk=null;for(i=0;i<mv.w.length;i++){var t3=mv.t[mv.w[i][0]]||{};if(String(t3.name||'')===f.n){var q=bimMvParking(t3);if(q.l!==null||q.r!==null){pk=q;break;}}}
      return pk?f.n+': '+bimMvParkText(pk):'';
    }).filter(function(x){return x;});
    if(fp.length)parts.push('parking along the frontage: '+fp.join('; '));
    var v=parts.join('; ');
    A.push({auto:'access.vehicles',cat:'access',title:'Vehicle access and parking',value:v.charAt(0).toUpperCase()+v.slice(1)+'.',
      cls:(!dw&&lowest&&lowest.c==='a')?'constraint':'neutral',sev:1,source:src,date:dt});
    return A;
  }
  /* __acad3dV165: what the ground and its water say about the site, as findings */
  function bimLandAuto(){
    var A=[],LD=A3D.site&&A3D.site.land,today=bimSaToday(),S,D;
    if(!LD)return A;
    try{S=bimDgSite();D=bimLandGround(S);}catch(eG){console.warn('[BIM] The ground could not be read',eG);return A;}
    if(D){
      var hn=bimLandHornOf(D),M=bimLandSiteMask(D,S),Y=bimLandHydroOf(D),n=0,sum=0,mx=0,flat=0,steep=0,k,a2=D.cell*D.cell,sb1=bimStd('land.slope','b1'),sb3=bimStd('land.slope','b3');   /* __acad3dV167 */
      for(k=0;k<M.length;k++)if(M[k]&&isFinite(hn.slope[k])){n++;sum+=hn.slope[k];if(hn.slope[k]>mx)mx=hn.slope[k];if(hn.slope[k]<sb1)flat++;if(hn.slope[k]>=sb3)steep++;}
      if(n){
        var heavy=steep/n>0.25;
        A.push({auto:'landform.slope',cat:'landform',title:'Slope at the site',value:'Mean '+bimDispNum(sum/n,1)+'%, steepest '+bimDispNum(mx,1)+'%; '+bimLandPct(flat,n)+' under '+bimDispNum(sb1,2)+'%'+(steep?', '+bimLandPct(steep,n)+' at '+bimDispNum(sb3,2)+'% or more':''),
          cls:heavy?'constraint':(flat/n>=0.75?'opportunity':'neutral'),sev:heavy?2:1,source:D.srcShort+', Horn\'s method',date:today});
      }
      var U=bimLandUpstream(D,Y,M),nu=0,ex=bimLandExits(D,Y,M),pin=0,parts=[];
      for(k=0;k<U.length;k++)if(U[k]&&!M[k])nu++;
      Y.ponds.forEach(function(p){for(var i=0;i<p.cells.length;i++)if(M[p.cells[i]]){pin++;break;}});
      if(ex.length){var P0=bimLandP(D,ex[0].path[0]),P1=bimLandP(D,ex[0].path[ex[0].path.length-1]);parts.push('drains to the '+BIM_LAND_DIRNAME[BIM_LAND_DIRS[bimLandDir8(bimLandAz(P1[0]-P0[0],P1[2]-P0[2]))]]);}
      parts.push(nu?bimLandHa(nu*a2)+' around drains onto it':'nothing around drains onto it');
      if(Y.ponds.length)parts.push(bimSaN(Y.ponds.length,'pond')+' within '+BIM_LAND_HALF+' m'+(pin?', '+pin+' on the site':''));
      var v=parts.join('; ');
      A.push({auto:'water.drainage',cat:'water',title:'Drainage',value:v.charAt(0).toUpperCase()+v.slice(1),cls:(nu*a2>=10000||pin)?'constraint':'neutral',sev:pin?2:1,source:D.srcShort+', Priority-Flood and D8',date:today});
    }
    var Z=bimLandFloodZones(S),F=Z.F;
    if(F&&F.features){
      var zc=Z.site?Z.site.zc:null,zn=Z.site?String(Z.site.p.FLD_ZONE||Z.site.p.fld_zone||''):'',bfe=Z.site?bimLandBfe(Z.site.p):null,
        near=BIM_LAND_ZORDER.filter(function(z){return Z.present[z]&&z!==zc;}).map(function(z){return BIM_LAND_ZONES[z].short;});
      A.push({auto:'water.fema',cat:'water',title:'Flood zone (FEMA)',
        value:(zc?'The site is in zone '+zn+', '+BIM_LAND_ZONES[zc].site+(bfe?'; base flood elevation '+bfe.text:''):'The site is outside FEMA\'s mapped flood zones')+(near.length?'; within '+BIM_LAND_HALF+' m: '+near.join(', '):''),
        cls:zc==='floodway'?'redflag':(zc?'constraint':'neutral'),sev:(zc==='floodway'||zc==='sfha'||zc==='coastal')?3:1,source:'FEMA National Flood Hazard Layer, '+F.fetched,date:today});
    }
    return A;
  }
  /* ---- Properties: what it is, how it was worked out, how it looks ---- */
  function bimDgPropsHtml(o){
    var dg=o.dg,A=bimDgAn(dg.a)||{name:dg.a},info=dg.info||{},ed=bimDgEdited(o),s=dg.s||{},live=dg.g.kind==='live',h='',r='',i;
    h+='<div class="a3d-ptypehd"><div class="a3d-ptypeic">'+(a3drIcon('bim:analyses')||a3drIcon('box'))+'</div>'+
      '<div class="a3d-ptypetx"><div class="a3d-ptypename">'+bimEsc(o.name)+'</div><div class="a3d-ptypesub">'+bimEsc(bimObjTypeLabel(o))+'</div></div></div>';
    if(info.title)r+=bimPropText('What It Shows',info.title);
    (info.rows||[]).forEach(function(row){r+=bimPropText(row[0],row[1]);});
    h+=bimPropGroup('Reading',r);
    r='';
    if(info.method)r+=bimPropText('Method',info.method);
    if(info.source)r+=bimPropText('Source',info.source+(info.date?', '+info.date:''));
    h+=bimPropGroup('How It Was Worked Out',r);
    r='';
    if(!live)r+=bimPropRow('Line Colour','<input type="color" data-dgf="stroke" value="'+bimEsc(/^#[0-9a-f]{6}$/i.test(s.stroke||'')?s.stroke:'#c9d3dd')+'">');
    if(s.fill!==undefined||live)r+=bimPropRow('Fill Colour','<input type="color" data-dgf="fill" value="'+bimEsc(/^#[0-9a-f]{6}$/i.test(s.fill||'')?s.fill:'#5b6c8a')+'">');
    if(!live)r+=bimPropRow('Line Width (px)','<input type="number" min="0.5" max="12" step="0.5" data-dgf="w" value="'+(s.w||1.5)+'">');
    if(!live)r+=bimPropRow('Dashed','<input type="checkbox" data-dgf="dash"'+(s.dash&&s.dash.length?' checked':'')+'>');
    r+=bimPropRow('Opacity (%)','<input type="number" min="10" max="100" step="5" data-dgf="op" value="'+Math.round((s.op===undefined?1:s.op)*100)+'">');
    for(i=0;i<(dg.lb||[]).length;i++)if(dg.lb[i]&&dg.lb[i].t!==undefined)r+=bimPropRow(i?'Label '+(i+1):'Label','<input type="text" maxlength="120" data-dgf="lb:'+i+'" value="'+bimEsc(dg.lb[i].t)+'">');
    r+=bimPropRow('Layer','<select data-propf="layer">'+bimLayerOptionsHtml(o.layer||A3D.activeLayer)+'</select>');
    h+=bimPropGroup('Appearance',r);
    r=bimPropText('Status',dg.orphan?'Changed by you; the analysis no longer draws it':(!dg.gen?'Yours: a copy, which the analysis does not draw':(ed?'Changed by you: kept when the analysis runs again':'As the analysis drew it')));
    if(dg.newer)r+=bimPropText('Newer','The analysis would draw it differently now: Reset takes its version');
    r+=bimPropRow('','<button type="button" class="a3d-pedit" data-dgact="reset"'+((ed||dg.newer)&&dg.gen?'':' disabled')+'>Reset to the analysis</button> '+
      '<button type="button" class="a3d-pedit" data-dgact="rerun">Run the analysis again</button>');
    h+=bimPropGroup('Analysis',r);
    return h;
  }
  function bimDgSet(o,f,v){
    if(!bimIsDiag(o))return false;
    var s=o.dg.s=o.dg.s||{},n=parseFloat(v),li=String(f).indexOf('lb:')===0?parseInt(String(f).slice(3),10):-1;
    /* checked before the undo step, so a refused value leaves none */
    if((f==='stroke'||f==='fill')&&!/^#[0-9a-f]{6}$/i.test(String(v)))return false;
    if(f==='w'&&(!isFinite(n)||n<0.5||n>12)){a3dToast('A line width is 0.5 to 12 pixels');refreshProps();return false;}
    if(f==='op'&&(!isFinite(n)||n<10||n>100)){a3dToast('Opacity is 10 to 100%');refreshProps();return false;}
    if(li>=0&&!(o.dg.lb&&o.dg.lb[li]))return false;
    if(!(f==='stroke'||f==='fill'||f==='w'||f==='dash'||f==='op'||li>=0))return false;
    pushUndo();
    if(f==='stroke'||f==='fill')s[f]=String(v).toLowerCase();
    else if(f==='w')s.w=n;
    else if(f==='dash')s.dash=v?[6,4]:null;
    else if(f==='op')s.op=Math.round(n)/100;
    else o.dg.lb[li].t=String(v).slice(0,120);
    refreshProps();paint();saveSoon();
    return true;
  }
  function bimDgPropChange(ev){
    var e=ev.target,f=e&&e.getAttribute?e.getAttribute('data-dgf'):null,o;
    if(!f)return;
    o=objById(A3D.sel);
    if(!bimIsDiag(o))return;
    bimDgSet(o,f,e.type==='checkbox'?e.checked:e.value);
  }
  function bimDgPropClick(ev){
    var b=ev.target&&ev.target.closest?ev.target.closest('[data-dgact]'):null,o;
    if(!b||b.disabled)return;
    o=objById(A3D.sel);
    if(!bimIsDiag(o))return;
    if(b.getAttribute('data-dgact')==='reset')bimDgReset(o.id);
    else if(b.getAttribute('data-dgact')==='rerun')bimDgRunAll(o.dg.a);
  }
