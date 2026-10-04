"""patch_phase143a.py -- V143: Simulation -- sun hours, solar on surfaces, rain on terrain.

Three simulations, each run on request and drawn over the plan:

- SUNHOURS: hours of direct sun on the ground through the site's date. Every 15 minutes of
  daylight, every solid's triangles are projected along the sun onto the ground (V107's shadow
  model) and rasterised onto a grid; each cell counts the steps it is lit. Cells under a building
  are its roof, not ground, and are left out.
- SOLAR: clear-sky solar energy on every face of the buildings through a year -- the 21st of each
  month, every half hour. Beam: Meinel's clear-sky DNI, 1361 x 0.7^(AM^0.678), air mass by Kasten
  and Young (1989); sky: 0.1 x DNI on the horizontal, by the face's view of the sky (1 + cos tilt)/2.
  Beam only when a ray from the face's centre to the sun meets no solid (shading by the others and
  by the building itself). No clouds: this is the clear-sky potential, said wherever it is shown.
  Each building keeps its roof's and its facades' kWh/m2 a year, so Colour By can show them.
- RAINFLOW: rain on a terrain surface. The surface is sampled on a grid; Priority-Flood (Barnes et
  al. 2014) fills its depressions -- where water ponds, how deep, how much -- and, with a small
  epsilon, makes every cell drain; D8 steepest descent routes the flow; accumulation finds the
  flow lines. Ponds and flow lines are drawn over the plan."""
NAME = 'patch_phase143a.py'
BASE = '44aceab1c180f1ff19e2c223e7be1a52a4274d126685d4a602090454fb1ebf7f'
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


SIM = r"""  /* ================= __acad3dV143: Simulation ================= */
  var A3D_SIM={sun:null,solar:null,rain:null,busy:null};
  var BIM_SIM_RAMP=['#2c3e78','#3a64a8','#3f8fc2','#5fb7b2','#9fd28e','#e7e36b','#f7b545','#f0703a'];
  function bimSimRampCol(f){f=Math.max(0,Math.min(1,f));return BIM_SIM_RAMP[Math.min(BIM_SIM_RAMP.length-1,Math.floor(f*BIM_SIM_RAMP.length))];}
  /* the model's shape, to say when a result is out of date */
  function bimSimStamp(){
    var s=A3D.objs.length+':',i,o,m;
    for(i=0;i<A3D.objs.length;i++){o=A3D.objs[i];m=o.mesh;s+=(m&&m.v?m.v.length:0)+(o.pos?','+o.pos.join(','):'')+(o.survey?'s'+o.survey.length+'r'+(o.rev||0):'')+';';}
    var h=0;for(i=0;i<s.length;i++)h=(h*31+s.charCodeAt(i))|0;
    return h+':'+(bimTrueNorthDeg())+':'+JSON.stringify(bimSunSettings());
  }
  function bimSimStale(r){return !!(r&&r.stamp!==bimSimStamp());}
  /* the site's day, every step minutes: [{t, sun}] with the sun up */
  function bimSimDaySteps(date,step){
    var st=bimSunSettings(),out=[],m,s;
    if(!bimSunNum(st.lat)||!bimSunNum(st.lon)||!bimSunNum(st.tz))return null;
    for(m=step/2;m<1440;m+=step){
      s=bimSunCalc(st.lat,st.lon,st.tz,date,bimHHMM(m));
      if(s&&s.elevation>0)out.push({m:m,sun:s});
    }
    return out;
  }
  /* ---- sun hours on the ground ---- */
  function bimSunHours(o){
    o=o||{};
    var st=bimSunSettings(),miss=bimSunNow().missing;
    if(miss)return {error:'Set the site '+miss.join(', ')+' first (Properties > Site > Location)'};
    var date=o.date||st.date,step=o.step||15,g=bimShadowGround(),list=bimShadowCasters(g),i,j,k;
    var steps=bimSimDaySteps(date,step);
    if(!steps)return {error:'The site has no place yet'};
    /* the area: the solids' plan, with room for their shadows */
    var x0=Infinity,x1=-Infinity,z0=Infinity,z1=-Infinity,top=g;
    for(i=0;i<list.length;i++)for(k=0;k<list[i].w.length;k++){var p=list[i].w[k];x0=Math.min(x0,p[0]);x1=Math.max(x1,p[0]);z0=Math.min(z0,p[2]);z1=Math.max(z1,p[2]);top=Math.max(top,p[1]);}
    if(!list.length){x0=-25;x1=25;z0=-25;z1=25;}
    var mg=o.margin!=null?o.margin:Math.min(150,Math.max(10,2*(top-g)));
    x0-=mg;x1+=mg;z0-=mg;z1+=mg;
    var cell=o.cell||Math.max(0.25,Math.max(x1-x0,z1-z0)/(o.res||120));
    var nx=Math.max(1,Math.ceil((x1-x0)/cell)),nz=Math.max(1,Math.ceil((z1-z0)/cell)),N=nx*nz;
    var lit=new Float32Array(N),roof=new Uint8Array(N),shade=new Uint8Array(N);
    function raster(a,b,c,mark,stamp){
      var minx=Math.min(a[0],b[0],c[0]),maxx=Math.max(a[0],b[0],c[0]),minz=Math.min(a[1],b[1],c[1]),maxz=Math.max(a[1],b[1],c[1]);
      var i0=Math.max(0,Math.ceil((minx-x0)/cell-0.5)),i1=Math.min(nx-1,Math.floor((maxx-x0)/cell-0.5));
      var j0=Math.max(0,Math.ceil((minz-z0)/cell-0.5)),j1=Math.min(nz-1,Math.floor((maxz-z0)/cell-0.5));
      if(i0>i1||j0>j1)return;
      var d=(b[0]-a[0])*(c[1]-a[1])-(c[0]-a[0])*(b[1]-a[1]);
      if(Math.abs(d)<1e-12)return;
      var ii,jj,px,pz,l1,l2;
      for(jj=j0;jj<=j1;jj++){pz=z0+(jj+0.5)*cell;
        for(ii=i0;ii<=i1;ii++){px=x0+(ii+0.5)*cell;
          l1=((px-a[0])*(c[1]-a[1])-(c[0]-a[0])*(pz-a[1]))/d;l2=((b[0]-a[0])*(pz-a[1])-(px-a[0])*(b[1]-a[1]))/d;
          if(l1>=-1e-9&&l2>=-1e-9&&l1+l2<=1+1e-9)mark[jj*nx+ii]=stamp;
        }}
    }
    function each(it,proj,mark,stamp){
      var sp=it.w.map(proj),f,q;
      for(k=0;k<it.f.length;k++){f=it.f[k];if(!f||f.length<3)continue;for(q=1;q+1<f.length;q++)raster(sp[f[0]],sp[f[q]],sp[f[q+1]],mark,stamp);}
    }
    for(i=0;i<list.length;i++)each(list[i],function(p){return [p[0],p[2]];},roof,1);
    for(j=0;j<steps.length;j++){
      var s=bimSunVector(steps[j].sun),stamp=(j%250)+1;
      for(i=0;i<list.length;i++)each(list[i],function(p){return bimShadowPoint(p,s,g);},shade,stamp);
      for(k=0;k<N;k++)if(shade[k]!==stamp)lit[k]+=step/60;
    }
    var lo=Infinity,hi=-Infinity,n6=0,nG=0;
    for(k=0;k<N;k++){if(roof[k])continue;nG++;if(lit[k]<lo)lo=lit[k];if(lit[k]>hi)hi=lit[k];if(lit[k]>=6-1e-9)n6++;}
    var day=steps.length*step/60;
    var r={date:date,step:step,x0:x0,z0:z0,cell:cell,nx:nx,nz:nz,hours:lit,roof:roof,day:day,min:nG?lo:0,max:nG?hi:0,
      sixPlus:nG?n6/nG:0,ground:g,casters:list.length,steps:steps.length,stamp:bimSimStamp()};
    return r;
  }
  /* ---- clear-sky solar on surfaces ---- */
  var BIM_SOLAR_CONST=1361;
  function bimSolarAirMass(el){
    var z=90-el;
    return 1/(Math.cos(z*Math.PI/180)+0.50572*Math.pow(96.07995-z,-1.6364));
  }
  function bimSolarDNI(el){return el>0?BIM_SOLAR_CONST*Math.pow(0.7,Math.pow(bimSolarAirMass(el),0.678)):0;}
  /* the year's sun: the 21st of each month, every half hour, weighted by the days in that month */
  function bimSolarYear(year){
    var st=bimSunSettings(),out=[],mo,m,s,dm=[31,28,31,30,31,30,31,31,30,31,30,31];
    if(!bimSunNum(st.lat)||!bimSunNum(st.lon)||!bimSunNum(st.tz))return null;
    year=year||parseInt(String(st.date).slice(0,4),10)||new Date().getFullYear();
    if((year%4===0&&year%100!==0)||year%400===0)dm[1]=29;
    for(mo=0;mo<12;mo++)for(m=15;m<1440;m+=30){
      s=bimSunCalc(st.lat,st.lon,st.tz,year+'-'+bimPad2(mo+1)+'-21',bimHHMM(m));
      if(s&&s.elevation>0)out.push({sun:s,v:bimSunVector(s),dni:bimSolarDNI(s.elevation),w:dm[mo]*0.5});
    }
    return out;
  }
  /* the faces of the solids, in the world: centre, unit normal, area */
  function bimSolarFaces(o){
    var m=meshOf(o),q=bimObjOffset(o),out=[],i,j,f,nx,ny,nz,cx,cy,cz,a,b,L;
    if(!m||!m.f)return out;
    for(i=0;i<m.f.length;i++){
      f=m.f[i];if(!f||f.length<3)continue;
      nx=ny=nz=cx=cy=cz=0;
      for(j=0;j<f.length;j++){
        a=m.v[f[j]];b=m.v[f[(j+1)%f.length]];
        nx+=(a[1]-b[1])*(a[2]+b[2]);ny+=(a[2]-b[2])*(a[0]+b[0]);nz+=(a[0]-b[0])*(a[1]+b[1]);
        cx+=a[0];cy+=a[1];cz+=a[2];
      }
      L=Math.sqrt(nx*nx+ny*ny+nz*nz);if(L<1e-9)continue;
      out.push({c:[cx/f.length+q[0],cy/f.length+q[1],cz/f.length+q[2]],n:[nx/L,ny/L,nz/L],area:L/2});
    }
    return out;
  }
  /* every solid's world triangles, with its box, for the shading rays */
  function bimSolarOccluders(){
    var out=[],i,k,o,m,q,w,b,f,j;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];m=(o.t==='solid')?meshOf(o):null;
      if(!m||!m.f||!m.v||!bimLayerShown(o))continue;
      q=bimObjOffset(o);w=m.v.map(function(p){return [p[0]+q[0],p[1]+q[1],p[2]+q[2]];});
      b=[Infinity,Infinity,Infinity,-Infinity,-Infinity,-Infinity];
      for(k=0;k<w.length;k++)for(j=0;j<3;j++){b[j]=Math.min(b[j],w[k][j]);b[j+3]=Math.max(b[j+3],w[k][j]);}
      var T=[];
      for(k=0;k<m.f.length;k++){f=m.f[k];if(!f||f.length<3)continue;for(j=1;j+1<f.length;j++)T.push([w[f[0]],w[f[j]],w[f[j+1]]]);}
      out.push({id:o.id,box:b,tris:T});
    }
    return out;
  }
  function bimRayBox(o,d,b){
    var t0=0,t1=Infinity,k,inv,a,c;
    for(k=0;k<3;k++){
      if(Math.abs(d[k])<1e-12){if(o[k]<b[k]||o[k]>b[k+3])return false;continue;}
      inv=1/d[k];a=(b[k]-o[k])*inv;c=(b[k+3]-o[k])*inv;
      if(a>c){var tt=a;a=c;c=tt;}
      t0=Math.max(t0,a);t1=Math.min(t1,c);if(t0>t1)return false;
    }
    return true;
  }
  /* Moller-Trumbore: does the ray from o along d meet the triangle, ahead of o? */
  function bimRayTri(o,d,T){
    var e1=[T[1][0]-T[0][0],T[1][1]-T[0][1],T[1][2]-T[0][2]],e2=[T[2][0]-T[0][0],T[2][1]-T[0][1],T[2][2]-T[0][2]];
    var p=[d[1]*e2[2]-d[2]*e2[1],d[2]*e2[0]-d[0]*e2[2],d[0]*e2[1]-d[1]*e2[0]],det=e1[0]*p[0]+e1[1]*p[1]+e1[2]*p[2];
    if(Math.abs(det)<1e-12)return false;
    var inv=1/det,s=[o[0]-T[0][0],o[1]-T[0][1],o[2]-T[0][2]],u=(s[0]*p[0]+s[1]*p[1]+s[2]*p[2])*inv;
    if(u<0||u>1)return false;
    var qv=[s[1]*e1[2]-s[2]*e1[1],s[2]*e1[0]-s[0]*e1[2],s[0]*e1[1]-s[1]*e1[0]],v=(d[0]*qv[0]+d[1]*qv[1]+d[2]*qv[2])*inv;
    if(v<0||u+v>1)return false;
    return (e2[0]*qv[0]+e2[1]*qv[1]+e2[2]*qv[2])*inv>1e-6;
  }
  function bimRayBlocked(o,d,occ){
    var i,k;
    for(i=0;i<occ.length;i++){
      if(!bimRayBox(o,d,occ[i].box))continue;
      for(k=0;k<occ[i].tris.length;k++)if(bimRayTri(o,d,occ[i].tris[k]))return true;
    }
    return false;
  }
  /* one face's year: kWh/m2, beam and sky, the sun's steps seen */
  function bimSolarFace(fc,yr,occ,noShade){
    var beam=0,sky=0,seen=0,i,s,c,o,sv=(1+fc.n[1])/2;
    o=[fc.c[0]+fc.n[0]*0.01,fc.c[1]+fc.n[1]*0.01,fc.c[2]+fc.n[2]*0.01];
    for(i=0;i<yr.length;i++){
      s=yr[i];
      sky+=0.1*s.dni*sv*s.w;
      c=fc.n[0]*s.v[0]+fc.n[1]*s.v[1]+fc.n[2]*s.v[2];
      if(c<=0)continue;
      if(!noShade&&bimRayBlocked(o,s.v,occ))continue;
      beam+=s.dni*c*s.w;seen++;
    }
    return {beam:beam/1000,sky:sky/1000,total:(beam+sky)/1000,seen:seen};
  }
  /* the buildings asked for: the selection's solids, else (none selected, or none of it solid) every solid */
  function bimSolarTargets(ids){
    function solid(o){return o&&o.t==='solid'&&meshOf(o)&&bimLayerShown(o);}
    var T=ids&&ids.length?ids.map(objById).filter(solid):[];
    return T.length?T:A3D.objs.filter(solid);
  }
  function bimSolarObject(o,yr,occ,noShade){
    var F=bimSolarFaces(o),r={roof:{area:0,kwh:0},facade:{area:0,kwh:0},faces:[]},i,fc,e,k;
    for(i=0;i<F.length;i++){
      fc=F[i];
      if(fc.n[1]<-0.99)continue;   /* the ground floor's underside */
      e=bimSolarFace(fc,yr,occ,noShade);
      k=fc.n[1]>0.01?'roof':'facade';
      r[k].area+=fc.area;r[k].kwh+=e.total*fc.area;
      r.faces.push({k:k,c:fc.c,n:fc.n,area:fc.area,kwhm2:e.total,beam:e.beam,sky:e.sky});
    }
    r.roof.kwhm2=r.roof.area?r.roof.kwh/r.roof.area:null;
    r.facade.kwhm2=r.facade.area?r.facade.kwh/r.facade.area:null;
    return r;
  }
  /* SOLAR: in slices, so the page stays alive; resolves with the result */
  function bimSolarRun(opts){
    opts=opts||{};
    var miss=bimSunNow().missing;
    if(miss)return Promise.resolve({error:'Set the site '+miss.join(', ')+' first (Properties > Site > Location)'});
    if(A3D_SIM.busy)return Promise.resolve({error:'A simulation is already running'});
    var yr=bimSolarYear(opts.year),T=bimSolarTargets(opts.ids||(A3D.selSet&&A3D.selSet.length?A3D.selSet:null));
    if(!T.length)return Promise.resolve({error:'There are no buildings or solids to put the sun on'});
    var occ=bimSolarOccluders(),res={},i=0,t0=Date.now(),stamp=bimSimStamp();
    A3D_SIM.busy='solar';
    return new Promise(function(done){
      function slice(){
        var until=Date.now()+40;
        try{
          while(i<T.length&&Date.now()<until){res[T[i].id]=bimSolarObject(T[i],yr,occ,!!opts.noShade);i++;}
        }catch(eS){A3D_SIM.busy=null;console.warn('[BIM] solar',eS);done({error:'The solar simulation failed - see the console'});return;}
        if(i<T.length){if(i%5===0)bimAnalyzeRefresh();setTimeout(slice,0);return;}
        A3D_SIM.busy=null;
        var k,o,R,best=null,sumA=0,sumK=0;
        for(k in res)if(res.hasOwnProperty(k)){
          o=objById(k);R=res[k];
          if(o)o.solar={roof:R.roof.kwhm2===null?null:Math.round(R.roof.kwhm2),facade:R.facade.kwhm2===null?null:Math.round(R.facade.kwhm2),
            roofKwh:Math.round(R.roof.kwh),computed:new Date().toISOString().slice(0,10),shaded:!opts.noShade};
          if(R.roof.area){sumA+=R.roof.area;sumK+=R.roof.kwh;if(!best||R.roof.kwhm2>best.v)best={id:k,v:R.roof.kwhm2};}
        }
        A3D_SIM.solar={objects:res,count:T.length,steps:yr.length,roofMean:sumA?sumK/sumA:null,best:best,ms:Date.now()-t0,stamp:stamp,shaded:!opts.noShade};
        saveSoon();refreshProps();paint();
        done(A3D_SIM.solar);
      }
      setTimeout(slice,0);
    });
  }
  /* ---- rain on a terrain ---- */
  function bimRainHeap(){
    var a=[];
    return {size:function(){return a.length;},
      push:function(x){a.push(x);var i=a.length-1;while(i>0){var p=(i-1)>>1;if(a[p][0]<=x[0])break;a[i]=a[p];i=p;}a[i]=x;},
      pop:function(){var top=a[0],x=a.pop(),i=0,n=a.length;if(n){while(true){var l=2*i+1,r=l+1,m=i,mv=x[0];
        if(l<n&&a[l][0]<mv){m=l;mv=a[l][0];}if(r<n&&a[r][0]<mv){m=r;}if(m===i)break;a[i]=a[m];i=m;}a[i]=x;}return top;}};
  }
  function bimRainTerrain(id){
    var o=id?objById(id):objById(A3D.sel);
    if(o&&o.t==='terrain'&&o.survey)return o;
    for(var i=0;i<A3D.objs.length;i++)if(A3D.objs[i].t==='terrain'&&A3D.objs[i].survey)return A3D.objs[i];
    return null;
  }
  function bimRainFlow(id,opts){
    opts=opts||{};
    var ter=bimRainTerrain(id);
    if(!ter)return {error:'There is no terrain surface: make one with SURVEY, or get the site context'};
    var tin=bimTerrainTin(ter);
    if(!tin||!tin.tris||!tin.tris.length)return {error:ter.name+' has no triangles'};
    var x0=Infinity,x1=-Infinity,z0=Infinity,z1=-Infinity,i,j,k;
    for(i=0;i<tin.P.length;i++){x0=Math.min(x0,tin.P[i][0]);x1=Math.max(x1,tin.P[i][0]);z0=Math.min(z0,tin.P[i][1]);z1=Math.max(z1,tin.P[i][1]);}
    var cell=opts.cell||Math.max(0.25,Math.max(x1-x0,z1-z0)/(opts.res||120));
    var nx=Math.max(2,Math.floor((x1-x0)/cell)),nz=Math.max(2,Math.floor((z1-z0)/cell)),N=nx*nz;
    var H=new Float64Array(N),F=new Float64Array(N),ok=new Uint8Array(N),dir=new Int32Array(N),acc=new Float64Array(N),done=new Uint8Array(N);
    /* the surface, cell by cell (a triangle walk would be faster; the grid is small) */
    for(j=0;j<nz;j++)for(i=0;i<nx;i++){
      var h=bimTinHeightAt(tin,x0+(i+0.5)*cell,z0+(j+0.5)*cell);
      k=j*nx+i;if(h!==null&&isFinite(h)){H[k]=h;ok[k]=1;}
    }
    var DX=[1,1,0,-1,-1,-1,0,1],DZ=[0,1,1,1,0,-1,-1,-1],DL=[1,Math.SQRT2,1,Math.SQRT2,1,Math.SQRT2,1,Math.SQRT2];
    function edge(i,j){
      if(i===0||j===0||i===nx-1||j===nz-1)return true;
      for(var d=0;d<8;d++){var a=i+DX[d],b=j+DZ[d];if(!ok[b*nx+a])return true;}
      return false;
    }
    /* Priority-Flood: from the edge inward, each cell raised to the lowest spill height around it */
    var Q=bimRainHeap(),eps=opts.eps!=null?opts.eps:1e-5,ord=[];
    for(j=0;j<nz;j++)for(i=0;i<nx;i++){k=j*nx+i;if(ok[k]&&edge(i,j)){F[k]=H[k];done[k]=1;dir[k]=-1;Q.push([F[k],k]);}}
    while(Q.size()){
      var e=Q.pop(),c=e[1],ci=c%nx,cj=(c-ci)/nx;
      ord.push(c);
      for(var d=0;d<8;d++){
        var a=ci+DX[d],b=cj+DZ[d];
        if(a<0||b<0||a>=nx||b>=nz)continue;
        var nk=b*nx+a;
        if(!ok[nk]||done[nk])continue;
        done[nk]=1;
        F[nk]=Math.max(H[nk],F[c]+eps*DL[d]);
        dir[nk]=(d+4)%8;   /* toward the cell it was reached from: downhill on the filled surface */
        Q.push([F[nk],nk]);
      }
    }
    /* D8 on the filled surface where it falls; inside a pond, the way the flood came */
    for(k=0;k<N;k++){
      if(!ok[k]||dir[k]===-1)continue;
      var ki=k%nx,kj=(k-ki)/nx,best=-1,bs=0;
      for(d=0;d<8;d++){
        a=ki+DX[d];b=kj+DZ[d];if(a<0||b<0||a>=nx||b>=nz)continue;var q=b*nx+a;if(!ok[q])continue;
        var sl=(F[k]-F[q])/(DL[d]*cell);if(sl>bs+1e-12&&F[k]-H[k]<1e-3){bs=sl;best=d;}
      }
      if(best>=0)dir[k]=best;
    }
    /* accumulation, highest first: each cell's rain (one cell's worth) passed downstream */
    for(k=0;k<N;k++)if(ok[k])acc[k]=1;
    ord.sort(function(p,q){return F[q]-F[p];});
    for(i=0;i<ord.length;i++){
      k=ord[i];if(dir[k]<0)continue;
      var ii=k%nx,jj=(k-ii)/nx,t2=(jj+DZ[dir[k]])*nx+ii+DX[dir[k]];
      if(ok[t2])acc[t2]+=acc[k];
    }
    /* ponds: cells under water deeper than the threshold, joined into pools */
    var pmin=opts.pondMin!=null?opts.pondMin:0.02,pid=new Int32Array(N),ponds=[],stack;
    for(k=0;k<N;k++){
      if(!ok[k]||pid[k]||F[k]-H[k]<pmin)continue;
      var pool={cells:0,volume:0,depth:0,level:-Infinity,low:null};
      stack=[k];pid[k]=ponds.length+1;
      while(stack.length){
        var u=stack.pop(),ui=u%nx,uj=(u-ui)/nx,dd=F[u]-H[u];
        pool.cells++;pool.volume+=dd*cell*cell;if(dd>pool.depth){pool.depth=dd;pool.low=[x0+(ui+0.5)*cell,z0+(uj+0.5)*cell];}
        pool.level=Math.max(pool.level,F[u]);
        for(d=0;d<8;d++){a=ui+DX[d];b=uj+DZ[d];if(a<0||b<0||a>=nx||b>=nz)continue;var v=b*nx+a;
          if(ok[v]&&!pid[v]&&F[v]-H[v]>=pmin){pid[v]=ponds.length+1;stack.push(v);}}
      }
      pool.area=pool.cells*cell*cell;
      ponds.push(pool);
    }
    ponds.sort(function(p,q){return q.volume-p.volume;});
    /* flow lines: cells draining at least the threshold's area */
    var nOk=0;for(k=0;k<N;k++)if(ok[k])nOk++;
    var thr=opts.streamCells||Math.max(8,Math.round(nOk*0.01)),segs=[],outlets=0,maxAcc=0;
    for(k=0;k<N;k++){
      if(!ok[k])continue;
      if(acc[k]>maxAcc)maxAcc=acc[k];
      if(dir[k]===-1&&acc[k]>=thr)outlets++;
      if(acc[k]<thr||dir[k]<0)continue;
      var si=k%nx,sj=(k-si)/nx;
      segs.push([x0+(si+0.5)*cell,z0+(sj+0.5)*cell,x0+(si+DX[dir[k]]+0.5)*cell,z0+(sj+DZ[dir[k]]+0.5)*cell,acc[k]]);
    }
    var vol=0;ponds.forEach(function(p){vol+=p.volume;});
    return {terrain:ter.id,name:ter.name,x0:x0,z0:z0,cell:cell,nx:nx,nz:nz,ok:ok,H:H,F:F,acc:acc,dir:dir,pid:pid,
      ponds:ponds,pondVolume:vol,segs:segs,threshold:thr,outlets:outlets,maxAcc:maxAcc,cells:nOk,stamp:bimSimStamp()};
  }
  /* ---- drawing over the plan ---- */
  function bimSimGridImage(r,colOf){
    var c=document.createElement('canvas');c.width=r.nx;c.height=r.nz;
    var x=c.getContext('2d'),im=x.createImageData(r.nx,r.nz),k,col,d=im.data;
    for(k=0;k<r.nx*r.nz;k++){
      col=colOf(k);if(!col)continue;
      d[k*4]=parseInt(col.slice(1,3),16);d[k*4+1]=parseInt(col.slice(3,5),16);d[k*4+2]=parseInt(col.slice(5,7),16);d[k*4+3]=col.length>7?parseInt(col.slice(7,9),16):255;
    }
    x.putImageData(im,0,0);
    return c;
  }
  function bimSimDrawGrid(ctx,V,W,H,r,img,y,alpha){
    var p0=toScreen([r.x0,y,r.z0],V,W,H),p1=toScreen([r.x0+r.nx*r.cell,y,r.z0],V,W,H),p2=toScreen([r.x0,y,r.z0+r.nz*r.cell],V,W,H);
    if(!p0||!p1||!p2)return;
    ctx.save();
    ctx.globalAlpha=alpha;
    ctx.imageSmoothingEnabled=false;
    ctx.transform((p1[0]-p0[0])/r.nx,(p1[1]-p0[1])/r.nx,(p2[0]-p0[0])/r.nz,(p2[1]-p0[1])/r.nz,p0[0],p0[1]);
    ctx.drawImage(img,0,0);
    ctx.restore();
  }
  function drawSimOverlays(ctx,V,W,H){
    if(!bimCameraIsPlan())return;
    try{
      var s=A3D_SIM.sun;
      if(s&&s.show!==false){
        if(!s.img)s.img=bimSimGridImage(s,function(k){return s.roof[k]?null:bimSimRampCol(s.day?s.hours[k]/s.day:0);});
        bimSimDrawGrid(ctx,V,W,H,s,s.img,s.ground,0.55);
      }
      var r=A3D_SIM.rain;
      if(r&&r.show!==false){
        if(!r.img)r.img=bimSimGridImage(r,function(k){return r.pid[k]?'#2f7fe0c0':null;});
        bimSimDrawGrid(ctx,V,W,H,r,r.img,0,0.9);
        ctx.save();ctx.strokeStyle='#1565c0';ctx.lineCap='round';
        var lm=Math.log(r.maxAcc+1),i,g,a,b;
        for(i=0;i<r.segs.length;i++){
          g=r.segs[i];a=toScreen([g[0],0,g[1]],V,W,H);b=toScreen([g[2],0,g[3]],V,W,H);
          if(!a||!b)continue;
          ctx.lineWidth=0.8+2.6*Math.log(g[4]+1)/lm;
          ctx.beginPath();ctx.moveTo(a[0],a[1]);ctx.lineTo(b[0],b[1]);ctx.stroke();
        }
        ctx.restore();
      }
    }catch(eD){console.warn('[BIM] simulation overlay',eD);}
  }
  /* the commands */
  function bimSunHoursCommand(opts){
    var r=bimSunHours(opts);
    if(r.error){a3dToast('Sun hours: '+r.error);return r;}
    r.show=true;A3D_SIM.sun=r;
    paint();bimAnalyzeRefresh();
    a3dToast('Sun hours on '+r.date+': '+bimDispNum(r.min,1)+' to '+bimDispNum(r.max,1)+' h of '+bimDispNum(r.day,1)+' h of daylight; '+
      Math.round(r.sixPlus*100)+'% of the ground has 6 h or more'+(bimCameraIsPlan()?'':' (drawn in plan)'));
    return r;
  }
  function bimRainCommand(id,opts){
    var r=bimRainFlow(id,opts);
    if(r.error){a3dToast('Rain flow: '+r.error);return r;}
    r.show=true;A3D_SIM.rain=r;
    paint();bimAnalyzeRefresh();
    a3dToast('Rain on '+r.name+': '+r.ponds.length+' pond'+(r.ponds.length===1?'':'s')+
      (r.ponds.length?', '+bimDispNum(r.pondVolume,1)+' m³ held, the deepest '+bimDispNum(r.ponds[0].depth,2)+' m':'')+'; flow lines drawn'+(bimCameraIsPlan()?'':' in plan'));
    return r;
  }
  function bimSolarCommand(opts){
    a3dToast('Solar: putting a clear-sky year of sun on '+bimSolarTargets((opts&&opts.ids)||(A3D.selSet&&A3D.selSet.length?A3D.selSet:null)).length+' solid(s) ...');
    return bimSolarRun(opts).then(function(r){
      if(r.error){a3dToast('Solar: '+r.error);return r;}
      bimAnalyzeRefresh();
      a3dToast('Solar (clear sky, no clouds): '+r.count+' solid'+(r.count===1?'':'s')+(r.roofMean!==null?', roofs '+Math.round(r.roofMean)+' kWh/m² a year on average':'')+
        ' -- Colour By "Solar on roof (kWh/m2 a year)" shows each');
      return r;
    });
  }
  function bimSimClear(which){
    var n=0;
    ['sun','solar','rain'].forEach(function(k){if((!which||which===k)&&A3D_SIM[k]){A3D_SIM[k]=null;n++;}});
    if(!which||which==='solar')A3D.objs.forEach(function(o){if(o.solar){delete o.solar;n++;}});
    paint();refreshProps();bimAnalyzeRefresh();
    return n;
  }
"""
rep("""  /* ================= __acad3dV141: Properties' tabs, with nothing selected =================""",
    SIM + """  /* ================= __acad3dV141: Properties' tabs, with nothing selected =================""")
rep("""    if(!capMode)drawSunShadows(ctx,V,W,H);   /* __acad3dV107: first, so everything else draws over it */""",
    """    if(!capMode)drawSunShadows(ctx,V,W,H);   /* __acad3dV107: first, so everything else draws over it */
    if(!capMode)drawSimOverlays(ctx,V,W,H);  /* __acad3dV143: sun hours, ponds and flow lines */""")
# Colour By: the solar results, as properties
rep("""    if(o.context)take(o.context);
    return out;""", """    if(o.context)take(o.context);
    if(o.solar){   /* __acad3dV143 */
      if(o.solar.roof!==null)out['Solar on roof (kWh/m2 a year)']=o.solar.roof;
      if(o.solar.facade!==null)out['Solar on facades (kWh/m2 a year)']=o.solar.facade;
    }
    return out;""")
rep("""  /* __acad3dV142: the guide and the version */""", """  /* __acad3dV143: simulation */
  window.__a3dSunHours=function(o){var r=bimSunHoursCommand(o||{});if(r.error)return r;
    return {date:r.date,step:r.step,x0:r.x0,z0:r.z0,cell:r.cell,nx:r.nx,nz:r.nz,day:r.day,min:r.min,max:r.max,sixPlus:r.sixPlus,ground:r.ground,steps:r.steps,
      hours:Array.prototype.slice.call(r.hours),roof:Array.prototype.slice.call(r.roof)};};
  window.__a3dSolar=function(o){return bimSolarCommand(o||{}).then(function(r){return r.error?r:JSON.parse(JSON.stringify({count:r.count,steps:r.steps,roofMean:r.roofMean,best:r.best,shaded:r.shaded,objects:r.objects}));});};
  window.__a3dSolarYear=function(){return (bimSolarYear()||[]).map(function(s){return {el:s.sun.elevation,az:s.sun.azimuth,v:s.v,dni:s.dni,w:s.w};});};
  window.__a3dRainFlow=function(id,o){var r=bimRainCommand(id,o||{});if(r.error)return r;
    return {terrain:r.terrain,x0:r.x0,z0:r.z0,cell:r.cell,nx:r.nx,nz:r.nz,cells:r.cells,ponds:r.ponds,pondVolume:r.pondVolume,threshold:r.threshold,outlets:r.outlets,
      maxAcc:r.maxAcc,segs:r.segs.length,acc:Array.prototype.slice.call(r.acc),dir:Array.prototype.slice.call(r.dir)};};
  window.__a3dSimClear=function(w){return bimSimClear(w);};
  window.__a3dSimState=function(){return {sun:!!A3D_SIM.sun,solar:!!A3D_SIM.solar,rain:!!A3D_SIM.rain,busy:A3D_SIM.busy,
    stale:{sun:bimSimStale(A3D_SIM.sun),solar:bimSimStale(A3D_SIM.solar),rain:bimSimStale(A3D_SIM.rain)}};};
  /* __acad3dV142: the guide and the version */""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
