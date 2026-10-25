  /* ================= __acad3dV171: traffic and people around the site: the demand =================
     reference/research-traffic.md, section 8 (the owner's decisions 3 and 4). Each street's traffic in the peak hour
     from its class's typical daily traffic (fhwa.fc) and Florida's K; the turns at each junction balanced to the
     streets' volumes by NCHRP 255's method; the design's own trips from San Diego's rates by its usages; and the
     quickest ways to the lot and away from it. Pure where it can be, so the suite works each out again. */
  /* a link's volume in the peak hour: the middle of its class's urban AADT range times K, half each way on a two-way
     street (the peak direction's share is not applied); a service road and a street of no class carry none */
  function bimTrLinkVolume(Lk){
    var rc=bimDgRoads()[Lk.base];
    if(!rc||!(rc.u>0))return 0;
    return rc.u*bimStd('fdot.k','k')/100*(Lk.ow?1:0.5);
  }
  /* NCHRP 255's balancing: a first guess of each approach's turns in proportion to the exits' volumes, then the
     matrix scaled to the approaches' volumes (its rows) and to the exits' (its columns, scaled to the same total), in
     turn, n times. qi: the approaches' volumes; qo: the exits'; ok[i][j]: the turn is allowed. Returns the shares,
     each row summing to 1 (an approach with no allowed exit has none) */
  function bimTrFurness(qi,qo,ok,n){
    var I=qi.length,Jn=qo.length,T=[],i,j,r,ti=0,to=0;
    for(i=0;i<I;i++)ti+=qi[i];
    for(j=0;j<Jn;j++)to+=qo[j];
    var sc=to>0?ti/to:0,tq=qo.map(function(v){return v*sc;});
    for(i=0;i<I;i++){
      var row=[],s=0;
      for(j=0;j<Jn;j++){var g=ok[i][j]?(qo[j]>0?qo[j]:0):0;row.push(g);s+=g;}
      for(j=0;j<Jn;j++)row[j]=s>0?row[j]/s*qi[i]:0;
      T.push(row);
    }
    if(ti>0&&to>0)for(r=0;r<n;r++){
      for(j=0;j<Jn;j++){var cs=0;for(i=0;i<I;i++)cs+=T[i][j];if(cs>0)for(i=0;i<I;i++)T[i][j]*=tq[j]/cs;}
      for(i=0;i<I;i++){var rs=0;for(j=0;j<Jn;j++)rs+=T[i][j];if(rs>0)for(j=0;j<Jn;j++)T[i][j]*=qi[i]/rs;}
    }
    var P=[];
    for(i=0;i<I;i++){
      var tot=0,row2=[];for(j=0;j<Jn;j++)tot+=T[i][j];
      if(tot>0)for(j=0;j<Jn;j++)row2.push(T[i][j]/tot);
      else{var m=0;for(j=0;j<Jn;j++)if(ok[i][j])m++;for(j=0;j<Jn;j++)row2.push(m?(ok[i][j]?1/m:0):0);}   /* no volume to share by: the allowed exits evenly */
      P.push(row2);
    }
    return P;
  }
  /* every link's volume, and each junction's turns */
  function bimTrDemand(N){
    var it=bimStd('nchrp255','iter');
    N.links.forEach(function(Lk){Lk.q=bimTrLinkVolume(Lk);});
    N.J.forEach(function(j){
      var ins=j.ins,outs=j.outs;
      if(!ins.length)return;
      var ok=ins.map(function(li){var T=j.tr[li];return outs.map(function(lo){return T.some(function(t){return t.o===lo;});});});
      var P=bimTrFurness(ins.map(function(li){return Math.max(N.links[li].q,1e-6);}),outs.map(function(lo){return N.links[lo].q;}),ok,it);
      ins.forEach(function(li,a){j.tr[li].forEach(function(t){var b=outs.indexOf(t.o);t.p=t.u?1:(b>=0?P[a][b]:0);});});
    });
    /* the boundaries: where background traffic comes in and goes out */
    N.src=[];N.sink=[];
    N.J.forEach(function(j){if(!j.bnd)return;j.outs.forEach(function(lo){N.src.push({j:j.i,l:lo,q:N.links[lo].q});});j.ins.forEach(function(li){N.sink.push({j:j.i,l:li,q:N.links[li].q});});});
  }
  /* ---- the design's own trips (San Diego's Trip Generation Manual, Table 1) ----
     rows: [{use, n}] -- the usage's San Diego use and its measure (dwelling units, thousand sq ft, rooms); acres: the
     lot's area (null where there is no lot); peak 'am' or 'pm'. Returns the trips in and out in the peak hour, by row */
  function bimTrTripsOf(rows,acres,peak){
    var T=bimStd('sd.trips','table')||{},dense=bimStd('sd.trips','dense'),out={rows:[],tin:0,tout:0,day:0},du=0,i;
    for(i=0;i<rows.length;i++)if(rows[i].use==='mdu')du+=rows[i].n;
    for(i=0;i<rows.length;i++){
      var r=rows[i],key=r.use,day=0,R;
      if(key==='mdu')key=(acres>0&&du/acres>dense)?'mdu_hi':'mdu_lo';
      R=T[key];
      if(!R||!(r.n>0)){out.rows.push({use:r.use,key:key,n:r.n,day:0,pin:0,pout:0,name:R?R.name:''});continue;}
      if(R.ln)day=Math.exp(R.ln[0]*Math.log(r.n)+R.ln[1]);else day=R.rate*r.n;
      var pk=peak==='am'?R.am:R.pm,ph=day*pk[0]/100,s=pk[1]+pk[2];
      var o={use:r.use,key:key,n:r.n,day:day,share:pk[0],pin:ph*pk[1]/s,pout:ph*pk[2]/s,name:R.name,per:R.per};
      out.rows.push(o);out.tin+=o.pin;out.tout+=o.pout;out.day+=day;
    }
    return out;
  }
  /* the design's usages as San Diego's uses, with their measures: a dwelling by the usage's units, a hotel by its keys,
     an office and retail by their gross floor area in thousand square feet (m2 to sq ft by the foot's definition) */
  function bimTrUses(){
    var U=bimStd('app.traffic','uses')||{},S=bimUsageSummary(null),rows=[],skip=[];
    S.rows.forEach(function(g){
      var use=U[g.usage],n=0;
      if(!use){if(g.usage!=='use-car')skip.push(g.name);return;}
      if(use==='mdu')n=g.values.units||0;
      else if(use==='hotel')n=g.values.keys||0;
      else n=g.GFA/(0.3048*0.3048)/1000;
      rows.push({use:use,n:n,usage:g.usage,name:g.name,GFA:g.GFA,measured:use==='mdu'?'units':(use==='hotel'?'keys':'GFA')});
    });
    var parking=S.rows.some(function(g){return g.usage==='use-car'&&(g.values.bays||0)>0;});
    return {rows:rows,skip:skip,parking:parking};
  }
  function bimTrLotAcres(L){return L.ring?Math.abs(bimPolyArea(L.ring))/4046.8564224:null;}   /* the international acre, 4046.8564224 m2 */
  /* ---- the quickest ways: for a target node, the link to take after each link to reach it (by free-flow time) ---- */
  function bimTrToward(N,target){
    var nL=N.links.length,D=new Float64Array(nL),nx=new Int32Array(nL),hk=[],hv=[],i;
    for(i=0;i<nL;i++){D[i]=Infinity;nx[i]=-2;}
    function push(k,v){var q=hk.length;hk.push(k);hv.push(v);while(q>0){var p=(q-1)>>1;if(hk[p]<=k)break;hk[q]=hk[p];hv[q]=hv[p];q=p;}hk[q]=k;hv[q]=v;}
    function pop(){var lk=hk.pop(),lv=hv.pop(),m=hk.length,q=0;if(!m)return;for(;;){var l=2*q+1,r=l+1,s=-1,sk=lk;if(l<m&&hk[l]<sk){s=l;sk=hk[l];}if(r<m&&hk[r]<sk){s=r;sk=hk[r];}if(s<0)break;hk[q]=hk[s];hv[q]=hv[s];q=s;}hk[q]=lk;hv[q]=lv;}
    for(i=0;i<nL;i++)if(N.links[i].b===target){D[i]=N.links[i].len/N.links[i].v0;nx[i]=-1;push(D[i],i);}   /* -1: this link ends there */
    var into={};N.links.forEach(function(Lk,li){(into[Lk.b]||(into[Lk.b]=[])).push(li);});
    while(hk.length){
      var t=hk[0],l=hv[0];pop();
      if(t>D[l])continue;
      (into[N.links[l].a]||[]).forEach(function(p){
        var J=N.J[N.links[p].jb];if(!J||!(J.tr[p]||[]).some(function(x){return x.o===l;}))return;   /* only the turns a car may make (a U-turn at a dead end) */
        var nt=t+N.links[p].len/N.links[p].v0;
        if(nt<D[p]){D[p]=nt;nx[p]=l;push(nt,p);}
      });
    }
    return {D:D,nx:nx};
  }
