  /* ================= __acad3dV172: the site analysis tools: the grid =================
     reference/research-site-analysis-tools.md. Every tool reads and writes one grid over the lot and around it, its
     processing extent: 1 m cells over the lot's extent and 100 m beyond it (100 m around the site's centre with no
     lot), at most 250,000 cells, coarser where the lot is larger. As in Esri's tools, a feature outside the extent
     is not counted, and the messages say so. Areas are counted on it, so an area is good to a cell's width
     along its edge, and said so. A feature drawn on it: an area by its cells' centres inside, a line or a point by
     the cells within half a cell of it. Straight-line distance by Felzenszwalb and Huttenlocher's exact transform
     ("Distance Transforms of Sampled Functions", Theory of Computing 8, 2012, Algorithm 1), run along the rows then
     the columns. A tool's output is kept as levels, one character a cell, run-length coded, so a project keeps it
     small and a later tool reads it back. */
  var BIM_TL_MARGIN=100,BIM_TL_MAXCELLS=250000,BIM_TL_BIG=1e10;   /* far above any squared distance in cells, near enough that q*q still counts beside it */
  /* the levels' characters: printable ASCII from '!' less the quote and the backslash, 92 of them (91 levels and
     restricted); a cell with no value is ' ' */
  var BIM_TL_ALPH=(function(){var s='',c;for(c=33;c<=126;c++)if(c!==34&&c!==92)s+=String.fromCharCode(c);return s;})();
  var A3D_TL={grid:null,gkey:null};
  /* the grid: its corner, its cell, its size, and the lot it is over */
  function bimTlGrid(){
    var S=bimDgSite(),ring=S.ring&&S.ring.length>=3?S.ring:null,x0,x1,z0,z1,i,cell,nx,nz,key;
    if(ring){x0=Infinity;x1=-Infinity;z0=Infinity;z1=-Infinity;
      for(i=0;i<ring.length;i++){x0=Math.min(x0,ring[i][0]);x1=Math.max(x1,ring[i][0]);z0=Math.min(z0,ring[i][1]);z1=Math.max(z1,ring[i][1]);}
      x0-=BIM_TL_MARGIN;x1+=BIM_TL_MARGIN;z0-=BIM_TL_MARGIN;z1+=BIM_TL_MARGIN;}
    else{x0=S.c[0]-BIM_TL_MARGIN;x1=S.c[0]+BIM_TL_MARGIN;z0=S.c[1]-BIM_TL_MARGIN;z1=S.c[1]+BIM_TL_MARGIN;}
    /* the property's corners carry float noise (250.00000000000003): a millionth of a cell is not a cell */
    cell=1;
    while(Math.ceil((x1-x0)/cell-1e-6)*Math.ceil((z1-z0)/cell-1e-6)>BIM_TL_MAXCELLS)cell*=2;
    x0=Math.floor(x0/cell+1e-6)*cell;z0=Math.floor(z0/cell+1e-6)*cell;
    nx=Math.ceil((x1-x0)/cell-1e-6);nz=Math.ceil((z1-z0)/cell-1e-6);
    key=[x0,z0,cell,nx,nz,ring?ring.map(function(p){return Math.round(p[0]*1000)+','+Math.round(p[1]*1000);}).join(';'):'none'].join('|');
    if(A3D_TL.gkey===key&&A3D_TL.grid)return A3D_TL.grid;
    var G={x0:x0,z0:z0,cell:cell,nx:nx,nz:nz,n:nx*nz,ring:ring,site:S,key:key,lot:null,lotArea:0};
    if(ring){G.lot=new Uint8Array(G.n);bimTlFillPoly(G,ring,G.lot,1);G.lotArea=bimTlCount(G,G.lot)*cell*cell;}
    A3D_TL.grid=G;A3D_TL.gkey=key;
    return G;
  }
  function bimTlCx(G,i){return G.x0+(i+0.5)*G.cell;}
  function bimTlCz(G,j){return G.z0+(j+0.5)*G.cell;}
  function bimTlCount(G,m){var n=0,k;for(k=0;k<G.n;k++)if(m[k])n++;return n;}
  /* an area: every cell whose centre is inside the ring (even-odd, so a ring's holes are holes) */
  function bimTlFillPoly(G,ring,m,v){
    var nz=G.nz,nx=G.nx,j,i,k,a,b,x,X=[],pz,i0,i1;
    for(j=0;j<nz;j++){
      pz=bimTlCz(G,j);X.length=0;
      for(k=0;k<ring.length;k++){
        a=ring[k];b=ring[(k+1)%ring.length];
        if((a[1]<=pz)!==(b[1]<=pz)){x=a[0]+(pz-a[1])*(b[0]-a[0])/(b[1]-a[1]);X.push(x);}
      }
      if(X.length<2)continue;
      X.sort(function(p,q){return p-q;});
      for(k=0;k+1<X.length;k+=2){
        i0=Math.max(0,Math.ceil((X[k]-G.x0)/G.cell-0.5));i1=Math.min(nx-1,Math.floor((X[k+1]-G.x0)/G.cell-0.5));
        for(i=i0;i<=i1;i++)m[j*nx+i]=v;
      }
    }
  }
  /* a line: the cells within half a cell of a segment */
  function bimTlStroke(G,a,b,m,v){
    var h=G.cell/2,x0=Math.min(a[0],b[0])-h,x1=Math.max(a[0],b[0])+h,z0=Math.min(a[1],b[1])-h,z1=Math.max(a[1],b[1])+h,
      i0=Math.max(0,Math.floor((x0-G.x0)/G.cell)),i1=Math.min(G.nx-1,Math.floor((x1-G.x0)/G.cell)),
      j0=Math.max(0,Math.floor((z0-G.z0)/G.cell)),j1=Math.min(G.nz-1,Math.floor((z1-G.z0)/G.cell)),i,j;
    for(j=j0;j<=j1;j++)for(i=i0;i<=i1;i++)if(bimTlSegDist(bimTlCx(G,i),bimTlCz(G,j),a,b)<=h+1e-9)m[j*G.nx+i]=v;
  }
  function bimTlSegDist(px,pz,a,b){
    var dx=b[0]-a[0],dz=b[1]-a[1],L=dx*dx+dz*dz,t=L>0?((px-a[0])*dx+(pz-a[1])*dz)/L:0;
    t=Math.max(0,Math.min(1,t));
    var qx=a[0]+t*dx-px,qz=a[1]+t*dz-pz;
    return Math.sqrt(qx*qx+qz*qz);
  }
  function bimTlPoint(G,p,r,m,v){
    var h=Math.max(r||0,G.cell/2),i0=Math.max(0,Math.floor((p[0]-h-G.x0)/G.cell)),i1=Math.min(G.nx-1,Math.floor((p[0]+h-G.x0)/G.cell)),
      j0=Math.max(0,Math.floor((p[1]-h-G.z0)/G.cell)),j1=Math.min(G.nz-1,Math.floor((p[1]+h-G.z0)/G.cell)),i,j,dx,dz;
    for(j=j0;j<=j1;j++)for(i=i0;i<=i1;i++){dx=bimTlCx(G,i)-p[0];dz=bimTlCz(G,j)-p[1];if(Math.sqrt(dx*dx+dz*dz)<=h+1e-9)m[j*G.nx+i]=v;}
  }
  /* Felzenszwalb and Huttenlocher's Algorithm 1, the squared distance along one line of n samples, f the line's
     values (0 at a source, BIM_TL_BIG elsewhere), in cells */
  function bimTlDt1(f,n,d,v,z){
    var k=0,q,s;
    v[0]=0;z[0]=-Infinity;z[1]=Infinity;
    for(q=1;q<n;q++){
      s=((f[q]+q*q)-(f[v[k]]+v[k]*v[k]))/(2*q-2*v[k]);
      while(s<=z[k]){k--;s=((f[q]+q*q)-(f[v[k]]+v[k]*v[k]))/(2*q-2*v[k]);}
      k++;v[k]=q;z[k]=s;z[k+1]=Infinity;
    }
    k=0;
    for(q=0;q<n;q++){while(z[k+1]<q)k++;d[q]=(q-v[k])*(q-v[k])+f[v[k]];}
  }
  /* the straight-line distance in metres from each cell's centre to the nearest source cell's centre; null with no source */
  function bimTlDistance(G,src){
    var nx=G.nx,nz=G.nz,N=G.n,D=new Float64Array(N),m=Math.max(nx,nz),f=new Float64Array(m),d=new Float64Array(m),v=new Int32Array(m),z=new Float64Array(m+1),i,j,any=false;
    for(i=0;i<N;i++){D[i]=src[i]?0:BIM_TL_BIG;if(src[i])any=true;}
    if(!any)return null;
    for(j=0;j<nz;j++){for(i=0;i<nx;i++)f[i]=D[j*nx+i];bimTlDt1(f,nx,d,v,z);for(i=0;i<nx;i++)D[j*nx+i]=d[i];}
    for(i=0;i<nx;i++){for(j=0;j<nz;j++)f[j]=D[j*nx+i];bimTlDt1(f,nz,d,v,z);for(j=0;j<nz;j++)D[j*nx+i]=d[j];}
    for(i=0;i<N;i++)D[i]=Math.sqrt(D[i])*G.cell;
    return D;
  }
  /* ---- the outputs kept: levels, run-length coded ---- */
  function bimTlEncode(lv){
    var rc='',rn=[],k,ch,prev=null,run=0;
    for(k=0;k<lv.length;k++){
      if(lv[k]>=BIM_TL_ALPH.length)throw new Error('a level beyond the '+BIM_TL_ALPH.length+' kept');
      ch=lv[k]<0?' ':BIM_TL_ALPH.charAt(lv[k]);
      if(ch===prev){run++;continue;}
      if(prev!==null){rc+=prev;rn.push(run);}
      prev=ch;run=1;
    }
    if(prev!==null){rc+=prev;rn.push(run);}
    return {rc:rc,rn:rn};
  }
  /* the levels again, -1 where there is none; null when the runs do not fill the grid */
  function bimTlDecode(d){
    if(!d||typeof d.rc!=='string'||!Array.isArray(d.rn)||d.rc.length!==d.rn.length)return null;
    var N=d.nx*d.nz,lv=new Int16Array(N),k=0,r,c,n,t,q;
    for(r=0;r<d.rc.length;r++){
      c=d.rc.charAt(r);n=+d.rn[r];
      if(!(n>0)||k+n>N)return null;
      q=c===' '?-1:BIM_TL_ALPH.indexOf(c);
      if(c!==' '&&q<0)return null;
      for(t=0;t<n;t++)lv[k++]=q;
    }
    return k===N?lv:null;
  }
  /* a level's value: a class's index, or a number between lo and hi in n steps */
  function bimTlValue(d,q){return q<0||(d.rest!==null&&d.rest!==undefined&&q===d.rest)?null:(d.n>1&&d.hi!==undefined&&d.hi!==null?d.lo+(d.hi-d.lo)*q/(d.n-1):q);}
  /* a kept output that can be drawn; a literal for the size, as this runs at start-up, before the file's vars are set */
  function bimTlDataOk(d){
    return !!(d&&isFinite(d.x0)&&isFinite(d.z0)&&d.cell>0&&d.nx>0&&d.nz>0&&d.nx*d.nz<=1000000&&Array.isArray(d.pal)&&
      typeof d.rc==='string'&&Array.isArray(d.rn)&&d.rc.length===d.rn.length);
  }
