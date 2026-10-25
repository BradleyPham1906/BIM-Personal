  /* ================= __acad3dV171: traffic and people around the site: the run =================
     reference/research-traffic.md, sections 1 to 3 and 8. One run at a time, on V170's clock: built when it starts
     (the network, the plans, the demand, the walkers' ways), warmed up, then stepped at a fixed step while the clock
     plays and drawn between steps; Stop gives it up. Cars and walkers live in fixed pools of typed arrays allocated
     once a run: nothing piles up while it runs. What it finds is tallied as it goes, never recorded step by step.
     Nothing of it is saved or undone: the settings are the project's (A3D.site.traffic), the results the elements
     Run lays down. */
  var BIM_TR_Q={light:{cars:200,walk:300,fps:20,detail:0,name:'Light'},normal:{cars:600,walk:1000,fps:30,detail:1,name:'Normal'},detailed:{cars:1500,walk:3000,fps:30,detail:2,name:'Detailed'}};
  var BIM_TR_QORDER=['light','normal','detailed'];
  var A3D_TR={run:null,allocs:0,last:null};
  function bimTrSettings(){
    var s=A3D.site&&A3D.site.traffic,o={on:false,peak:'pm',q:'auto',speed:1,seed:1};
    if(s&&typeof s==='object'){if(s.on===true)o.on=true;if(s.peak==='am')o.peak='am';if(BIM_TR_Q[s.q])o.q=s.q;if(s.speed===4||s.speed===16)o.speed=s.speed;if(s.seed>0&&s.seed<1e9)o.seed=Math.floor(s.seed);}
    return o;
  }
  /* the quality the device suggests, where the browser says its memory and cores */
  function bimTrDeviceQ(){
    var m=navigator.deviceMemory,c=navigator.hardwareConcurrency;
    if((m&&m<=2)||(c&&c<=2))return 'light';
    if(m>=8&&c>=8)return 'detailed';
    return 'normal';
  }
  function bimTrQuality(){var s=bimTrSettings();return s.q==='auto'?bimTrDeviceQ():s.q;}
  /* the run's random numbers, seeded so a run can be run again (mulberry32) */
  function bimTrRng(seed){var a=seed>>>0;return function(){a=(a+0x6D2B79F5)>>>0;var t=a;t=Math.imul(t^(t>>>15),t|1);t^=t+Math.imul(t^(t>>>7),t|61);return ((t^(t>>>14))>>>0)/4294967296;};}
  function bimTrGauss(rng){var u=Math.max(1e-12,rng()),v=rng();return Math.sqrt(-2*Math.log(u))*Math.cos(2*Math.PI*v);}
  /* the IDM's acceleration (Kesting 2010's car): v, the desired speed, the gap to the one ahead, the approach rate */
  function bimTrIdm(v,v0,s,dv,P){
    if(s<=0.01)return -9;
    var ss=P.s0+Math.max(0,v*P.T+v*dv/(2*Math.sqrt(P.a*P.b)));
    return P.a*(1-Math.pow(Math.max(0,v)/v0,P.d)-(ss/s)*(ss/s));
  }
  function bimTrIdmP(){return {T:bimStd('idm.car','T'),s0:bimStd('idm.car','s0'),a:bimStd('idm.car','a'),b:bimStd('idm.car','b'),d:bimStd('idm.car','delta'),free:bimStd('idm.car','free')};}
  /* ---- the run built: everything it reads, worked out once ---- */
  function bimTrBuild(){
    var N=bimTrNet();
    if(N.err)return {err:N.err};
    if(!N.links.length)return {err:'No street a car may use within '+bimStdSay('app.traffic','radius')+' of the lot'};
    bimTrDemand(N);
    var set=bimTrSettings(),qk=bimTrQuality(),Q=BIM_TR_Q[qk],RUN={N:N,set:set,qk:qk,Q:Q,cap:Q,rng:bimTrRng(set.seed),P:bimTrIdmP(),t:0,acc:0,step:Math.min(bimStd('app.traffic','step'),bimStd('idm.car','step_max')),
      plans:{},targets:[],tgOf:{},routes:[],srcs:[],slow:0,steps:0,frameMs:[],warm:false,y:bimDgSite().y||0};
    N.J.forEach(function(j){if(j.kind==='signal'){var P=bimTrPlan(N,j);if(P)RUN.plans[j.i]=P;else j.kind='yield';}j.majors=j.ins.filter(function(m){return j.major[m];});});
    /* the lanes' slots, and each junction's arms' crossings */
    var nl=0;N.links.forEach(function(Lk){Lk.slot=nl;nl+=Lk.lanes;});RUN.nSlots=nl;
    var na=0;N.J.forEach(function(j){j.armBase=na;na+=j.arms.length;});RUN.nArms=na;
    /* the design's own trips */
    var U=bimTrUses(),acres=bimTrLotAcres(N.L);
    RUN.uses=U;RUN.trips=bimTrTripsOf(U.rows,acres,set.peak);RUN.acres=acres;
    RUN.lotOk=!!N.lot;
    /* where the lot's drivers leave their cars: the lot, or (with no parking of its own) the car parks nearby */
    var mv=bimMvOf(),cp=[];
    if(RUN.lotOk&&!U.parking&&N.lot.prov&&mv&&mv.cp&&mv.cp.length){
      mv.cp.slice(0,3).forEach(function(c){
        var cx=0,cz=0,n=0;for(var q=0;q+1<c.ring.length;q+=2){cx+=c.ring[q];cz+=c.ring[q+1];n++;}
        if(!n)return;cx/=n;cz/=n;
        var bj=null,bd=Infinity;N.J.forEach(function(j){if(!j.ins.length||j.bnd)return;var d=Math.sqrt((j.x-cx)*(j.x-cx)+(j.z-cz)*(j.z-cz));if(d<bd){bd=d;bj=j;}});
        if(bj&&bd<=150)cp.push({n:bj.n,x:cx,z:cz,name:c.n||'Car park',j:bj.i});
      });
    }
    RUN.park=cp.length?cp:(RUN.lotOk?[{n:N.lot.n,x:N.x[N.lot.n],z:N.z[N.lot.n],name:N.lot.name,lot:true}]:[]);
    function target(n){if(!RUN.tgOf.hasOwnProperty(n)){RUN.tgOf[n]=RUN.targets.length;RUN.targets.push(bimTrToward(N,n));}return RUN.tgOf[n];}
    RUN.park.forEach(function(p){p.tg=target(p.n);});
    /* background traffic's entries, and the lot's: its cars out start at the park's link out */
    var qsum=0;N.src.forEach(function(s){qsum+=s.q;});
    N.src.forEach(function(s){if(s.q>0)RUN.srcs.push({l:s.l,q:s.q,next:0,pend:0});});
    RUN.sinks=N.sink.filter(function(s){return s.q>0||N.sink.length<4;});
    RUN.sinks.forEach(function(s){s.tg=target(N.links[s.l].b);});
    RUN.srcQ=qsum;
    /* the walkers: drivers between their cars and the doors; and, at the census tract's shares, people coming by
       transit (from the nearest stops) and on foot (from the edge); none where the census does not reach */
    var A=A3D.site&&A3D.site.access,Pp=A3D.site&&A3D.site.people,tr=Pp&&!Pp.outside&&Pp.v&&Pp.v.tract,share=null;
    if(tr){
      var e=function(x){return x&&typeof x[0]==='number'?x[0]:0;},car=e(tr.drv)+e(tr.cpl),tn=e(tr.trn),wk=e(tr.wlk);
      if(car>0)share={t:tn/car,w:wk/car,src:'the census tract\'s commuters (ACS 5-year)'};
    }
    RUN.share=share;
    var stops=[];
    if(share&&A&&Array.isArray(A.stops))A.stops.filter(function(s){return s.t<=10;}).sort(function(p,q){return p.t-q.t;}).slice(0,3).forEach(function(s){stops.push({x:s.x,z:s.z,name:s.n});});
    var edgeW=[];
    if(share){
      var bs=N.J.filter(function(j){return j.bnd&&j.arms.some(function(a){return a.car&&(N.edges[a.e].sw.l||N.edges[a.e].sw.r);});});
      bs.sort(function(p,q){var pa=0,qa=0;p.ins.forEach(function(l){pa+=N.links[l].q;});q.ins.forEach(function(l){qa+=N.links[l].q;});return qa-pa;});
      bs.slice(0,4).forEach(function(j){edgeW.push({x:j.x,z:j.z,name:'the edge'});});
    }
    RUN.stops=stops;RUN.edgeW=edgeW;
    function route(a,b,kind,door,extra){
      var r=bimTrWalkRoute(N,[a.x,a.z],[b.x,b.z]);
      if(!r)return -1;
      r.kind=kind;r.door=door;r.extra=extra;r.i=RUN.routes.length;
      RUN.routes.push(r);
      return r.i;
    }
    RUN.rIn=[];RUN.rOut=[];RUN.rTin=[];RUN.rTout=[];RUN.rWin=[];RUN.rWout=[];
    N.doors.forEach(function(d,di){
      RUN.park.forEach(function(p,pi){RUN.rIn.push(route(p,d,'in',di,pi));RUN.rOut.push(route(d,p,'out',di,pi));});
      stops.forEach(function(s,si){RUN.rTin.push(route(s,d,'tin',di,si));RUN.rTout.push(route(d,s,'tout',di,si));});
      edgeW.forEach(function(s,si){RUN.rWin.push(route(s,d,'win',di,si));RUN.rWout.push(route(d,s,'wout',di,si));});
    });
    ['rIn','rOut','rTin','rTout','rWin','rWout'].forEach(function(k){RUN[k]=RUN[k].filter(function(x){return x>=0;});});
    bimTrAlloc(RUN);
    return RUN;
  }
  /* the pools, once a run */
  function bimTrAlloc(RUN){
    var nc=RUN.Q.cars,nw=RUN.Q.walk,i;
    A3D_TR.allocs++;
    RUN.c={n:nc,L:new Int32Array(nc),ln:new Int8Array(nc),s:new Float32Array(nc),v:new Float32Array(nc),a:new Float32Array(nc),len:new Float32Array(nc),
      k:new Uint8Array(nc),tg:new Int16Array(nc),nx:new Int32Array(nc),t0:new Float32Array(nc),ta:new Float32Array(nc),st:new Uint8Array(nc),go:new Uint8Array(nc),lc:new Float32Array(nc),
      x:new Float32Array(nc),z:new Float32Array(nc),hx:new Float32Array(nc),hz:new Float32Array(nc),px:new Float32Array(nc),pz:new Float32Array(nc),
      free:new Int32Array(nc),nf:nc,ord:new Int32Array(nc),key:new Int32Array(nc),cnt:new Int32Array(RUN.nSlots+1),lead:new Int32Array(nc),fol:new Int32Array(nc),
      front:new Int32Array(RUN.N.links.length),last:new Int32Array(RUN.nSlots),head:new Int32Array(RUN.nSlots),claim:new Int32Array(RUN.nSlots),na:0};
    RUN.w={n:nw,R:new Int32Array(nw),p:new Float32Array(nw),v:new Float32Array(nw),v0:new Float32Array(nw),st:new Uint8Array(nw),cr:new Int16Array(nw),hb:new Uint8Array(nw),
      wait:new Float32Array(nw),x:new Float32Array(nw),z:new Float32Array(nw),px:new Float32Array(nw),pz:new Float32Array(nw),
      free:new Int32Array(nw),nf:nw,ord:new Int32Array(nw),key:new Int32Array(nw),cnt:new Int32Array(RUN.routes.length*4+1),na:0};
    RUN.occ=new Int16Array(RUN.nArms);   /* walkers on each arm's crossing */
    RUN.occH=new Int16Array(RUN.nArms*2);   /* and on each half of it: the half outbound cars pass (clockwise of the arm, looking out), then the inbound */
    for(i=0;i<nc;i++){RUN.c.L[i]=-1;RUN.c.free[i]=nc-1-i;}
    for(i=0;i<RUN.nSlots;i++)RUN.c.claim[i]=-1;
    for(i=0;i<nw;i++){RUN.w.R[i]=-1;RUN.w.free[i]=nw-1-i;}
    RUN.jq={};RUN.busy=new Float32Array(RUN.N.J.length);
    bimTrResetTallies(RUN);
  }
  function bimTrResetTallies(RUN){
    var N=RUN.N;
    RUN.res={t0:RUN.t,na0:RUN.c?RUN.c.na:0,spawned:0,exited:0,lotIn:0,lotOut:0,blocked:0,red:0,redAt:[],walkBad:0,lc:0,carsCap:0,walkCap:0,
      del:new Float64Array(N.links.length*2),cw:new Float64Array(N.J.length*2),doors:N.doors.map(function(){return {i:0,o:0};}),
      q:{n:0,out:0,outMax:0,st:0,stMax:0},bin:RUN.t,last:null};
  }
  /* ---- spawning ---- */
  /* a car into a link: in the lane with the most room before the car ahead (on this link or, where the link is short
     and empty, the last on the next), at the most speed that room allows without braking harder than comfortably
     (SUMO's departSpeed "max", by the IDM); none where the room is under the standstill gap */
  function bimTrCarNew(RUN,l,s,v,kind,tg){
    var C=RUN.c,N=RUN.N,Lk=N.links[l],P=RUN.P,best=-1,room=-Infinity,vl=0,ln,k,c;
    if(!C.nf||C.na>=RUN.cap.cars){RUN.res.carsCap++;return -1;}
    var nx=bimTrNextOf(RUN,tg,l);
    for(ln=0;ln<Lk.lanes;ln++){
      var lc=C.last[Lk.slot+ln],r=Infinity,rv=0;
      if(lc>=0){r=C.s[lc]-C.len[lc]-s;rv=C.v[lc];}
      else if(nx>=0){var Ln=N.links[nx],lk=C.last[Ln.slot+Math.min(ln,Ln.lanes-1)];if(lk>=0){r=Lk.len-s+C.s[lk]-C.len[lk];rv=C.v[lk];}}
      if(r>room){room=r;best=ln;vl=rv;}
    }
    if(room<P.s0)return -1;
    v=Math.min(v,Lk.v0);
    if(room<P.free&&bimTrIdm(v,Lk.v0,room,v-vl,P)<-P.b){
      var lo=0,hi=v;
      for(k=0;k<12;k++){var m=(lo+hi)/2;if(bimTrIdm(m,Lk.v0,room,m-vl,P)>=-P.b)lo=m;else hi=m;}
      v=lo;
    }
    c=C.free[--C.nf];C.na++;
    C.L[c]=l;C.ln[c]=best;C.s[c]=s;C.v[c]=v;C.a[c]=0;C.len[c]=bimStd('aashto.vehicles','P_l');C.k[c]=kind;C.tg[c]=tg;C.t0[c]=RUN.t;C.ta[c]=RUN.t;C.st[c]=0;C.go[c]=0;C.lc[c]=-99;
    C.last[Lk.slot+best]=c;   /* the lane's last until the next sort */
    C.nx[c]=nx;
    bimTrPlace(RUN,c);C.px[c]=C.x[c];C.pz[c]=C.z[c];
    RUN.res.spawned++;
    return c;
  }
  function bimTrCarFree(RUN,c){var C=RUN.c;C.L[c]=-1;C.free[C.nf++]=c;C.na--;}
  /* the link a car takes after this one: its way to its target, or a turn drawn by the junction's shares; -1 when this
     link takes it out (a boundary) or to its target */
  function bimTrNext(RUN,c,l){return bimTrNextOf(RUN,RUN.c.tg[c],l);}
  function bimTrNextOf(RUN,tg,l){
    var N=RUN.N,Lk=N.links[l],j=N.J[Lk.jb];
    if(!j)return -1;
    if(tg>=0){var nx=RUN.targets[tg].nx[l];return nx>=0?nx:-1;}
    if(j.bnd)return -1;
    var T=j.tr[l]||[],r=RUN.rng(),acc=0,i;
    for(i=0;i<T.length;i++){acc+=T[i].p;if(r<acc)return T[i].o;}
    return T.length?T[T.length-1].o:-1;
  }
  /* where a car is in plan: its link's line at its distance, moved across to its lane, and its heading */
  var BIM_TR_AT=[0,0,0,0];
  function bimTrPlace(RUN,c){
    /* lane 0 at the kerb: its middle that far right of the street's line (the whole width one way, its right half
       two ways); right of the way driven is (-dz, dx) on the plan */
    var C=RUN.c,Lk=RUN.N.links[C.L[c]],a=bimTrAt(Lk.P,Lk.C,Math.max(0,Math.min(Lk.len,C.s[c]-C.len[c]/2)),BIM_TR_AT),lw=(Lk.ow?Lk.w:Lk.w/2)/Lk.lanes,
      off=Lk.w/2-(C.ln[c]+0.5)*lw;
    C.x[c]=a[0]+(-a[3])*off;C.z[c]=a[1]+a[2]*off;C.hx[c]=a[2];C.hz[c]=a[3];
  }
  function bimTrWalkNew(RUN,r){
    var W=RUN.w,i,R=RUN.routes[r];
    if(!R)return -1;
    if(!W.nf||W.na>=RUN.cap.walk){RUN.res.walkCap++;return -1;}
    i=W.free[--W.nf];W.na++;
    if((R.kind==='out'||R.kind==='tout'||R.kind==='wout')&&RUN.res.t0<=RUN.t)RUN.res.doors[R.door].o++;   /* out of a door: counted as it leaves */
    var sp=bimStd('hm.walk','mean')+bimStd('hm.walk','sd')*bimTrGauss(RUN.rng),k=bimStd('hm.walk','cap');
    W.R[i]=r;W.p[i]=0;W.v0[i]=Math.max(0.5,Math.min(sp,bimStd('hm.walk','mean')*k));W.v[i]=W.v0[i];W.st[i]=Math.floor(RUN.rng()*2);W.cr[i]=-1;W.hb[i]=0;W.wait[i]=-1;
    bimTrWalkPlace(RUN,i);W.px[i]=W.x[i];W.pz[i]=W.z[i];
    return i;
  }
  function bimTrWalkFree(RUN,i){var W=RUN.w;W.R[i]=-1;W.free[W.nf++]=i;W.na--;}
  function bimTrWalkPlace(RUN,i){
    var W=RUN.w,r=RUN.routes[W.R[i]],a=bimTrAt(r.P,r.C,W.p[i],BIM_TR_AT),off=(W.st[i]-0.5)*bimStd('sumo.rules','stripe');
    W.x[i]=a[0]+(-a[3])*off;W.z[i]=a[1]+a[2]*off;
  }
  /* ---- one step ---- */
  function bimTrStep(RUN){
    var dt=RUN.step,C=RUN.c,i,c;
    bimTrSpawn(RUN,dt);
    bimTrSortCars(RUN);
    /* the accelerations, all from the same moment */
    for(i=0;i<C.n;i++){if(C.L[i]>=0)C.a[i]=bimTrAccOf(RUN,i);}
    bimTrLaneChanges(RUN);
    for(c=0;c<C.n;c++)if(C.L[c]>=0)bimTrMove(RUN,c,dt);
    bimTrWalkStep(RUN,dt);
    RUN.t+=dt;RUN.steps++;
    if(RUN.t-RUN.res.bin>=bimStd('app.traffic','bin'))bimTrSample(RUN);
  }
  /* a car's move: the ballistic update, a car stopping where it would rather than going back (the IDM's author) */
  function bimTrMove(RUN,c,dt){
    var C=RUN.c,N=RUN.N,l=C.L[c];
    C.px[c]=C.x[c];C.pz[c]=C.z[c];
    var v=C.v[c],a=C.a[c],nv=v+a*dt,ds;
    if(nv<0){ds=a<0?-v*v/(2*a):0;nv=0;}else ds=v*dt+a*dt*dt/2;
    var Lk=N.links[l],sl=bimTrStopLine(N,Lk),s0=C.s[c];
    C.s[c]=s0+ds;C.v[c]=nv;
    if(s0<sl&&C.s[c]>=sl)bimTrAtLine(RUN,c,Lk);
    if(nv<0.1&&C.s[c]>sl-3&&C.s[c]<=sl+0.5)C.st[c]=1;   /* stopped at its line: a stop sign is obeyed */
    while(C.L[c]>=0&&C.s[c]>=N.links[C.L[c]].len)bimTrCross(RUN,c);
    if(C.L[c]>=0)bimTrPlace(RUN,c);
  }
  function bimTrStopLine(N,Lk){var j=N.J[Lk.jb];if(!j)return Lk.len;var d=j.cw+1;return Math.max(Lk.len*0.5,Lk.len-d);}
  /* a car crossing its stop line: through a red is counted (none should); it claims the lane it goes into */
  function bimTrAtLine(RUN,c,Lk){
    var j=RUN.N.J[Lk.jb],P=j?RUN.plans[j.i]:null,o={},C=RUN.c,nx=C.nx[c];
    if(nx>=0){var Ln=RUN.N.links[nx];C.claim[Ln.slot+Math.min(C.ln[c],Ln.lanes-1)]=c;}
    if(P&&P.of.hasOwnProperty(Lk.i)){bimTrSig(P,P.of[Lk.i],RUN.t,o);if(o.s==='r'){RUN.res.red++;if(RUN.res.redAt.length<10)RUN.res.redAt.push([RUN.t,Lk.i,C.v[c],C.a[c],C.go[c],C.k[c],RUN.c.lead[c]]);}}
  }
  /* a car past its link's end: out at a boundary, into the lot (or a car park), or on to its next link */
  function bimTrCross(RUN,c){
    var N=RUN.N,C=RUN.c,l=C.L[c],Lk=N.links[l],j=N.J[Lk.jb],nx=C.nx[c],o;
    if(nx<0){
      bimTrDelay(RUN,c,Lk,j);
      if(C.tg[c]>=0&&C.k[c]===1){
        /* at the lot or its car park: the driver walks to a door */
        RUN.res.lotIn++;
        var pk=-1;RUN.park.forEach(function(p,pi){if(p.n===Lk.b)pk=pi;});
        var rs=RUN.rIn.filter(function(r){return RUN.routes[r].extra===pk;});
        if(rs.length)bimTrWalkNew(RUN,rs[Math.floor(RUN.rng()*rs.length)]);
      }else RUN.res.exited++;
      bimTrCarFree(RUN,c);return;
    }
    var Ln=N.links[nx],sn=C.s[c]-Lk.len,ln=Math.min(C.ln[c],Ln.lanes-1),k;
    /* no room in its lane there (cars from two ways at once): another lane with room, or it waits at its link's end */
    if(!bimTrRoomAt(RUN,Ln,ln,sn)){
      var alt=-1;for(k=0;k<Ln.lanes;k++)if(k!==ln&&bimTrRoomAt(RUN,Ln,k,sn)){alt=k;break;}
      if(alt<0){C.s[c]=Lk.len-0.01;var lk=C.last[Ln.slot+ln];C.v[c]=lk>=0?Math.min(C.v[c],C.v[lk]):0;return;}
      ln=alt;
    }
    bimTrDelay(RUN,c,Lk,j);
    C.s[c]=sn;C.L[c]=nx;C.ln[c]=ln;
    if(C.last[Ln.slot+ln]<0||C.s[C.last[Ln.slot+ln]]>sn)C.last[Ln.slot+ln]=c;   /* the lane's last at once, for the next to come in this step */
    C.ta[c]=RUN.t;C.st[c]=0;C.go[c]=0;
    C.nx[c]=bimTrNext(RUN,c,nx);
    if(j&&j.kind==='allstop'){RUN.busy[j.i]=RUN.t+bimTrClear(RUN,j,c,0);var q=RUN.jq[j.i];if(q){var k=q.indexOf(c);if(k>=0)q.splice(k,1);}}
  }
  /* a car's time on its link less its free-flow time, tallied for the junction it leaves by */
  function bimTrDelay(RUN,c,Lk,j){if(j&&RUN.res.t0<=RUN.t){var dl=Math.max(0,RUN.t-RUN.c.ta[c]-Lk.len/Lk.v0);RUN.res.del[Lk.i*2]+=dl;RUN.res.del[Lk.i*2+1]+=1;}}
  /* room on a lane for a car's front at s: the lane's last car's rear beyond it */
  function bimTrRoomAt(RUN,Ln,ln,s){var C=RUN.c,lk=C.last[Ln.slot+ln];return lk<0||C.s[lk]-C.len[lk]>=s;}
  /* the time a car needs to clear a junction from its line: across its widest street and its own length */
  function bimTrClear(RUN,j,c,d){
    var C=RUN.c,P=RUN.P,v=C.v[c],x=Math.max(C.len[c],d+2*j.cw+C.len[c]),t;
    t=(-v+Math.sqrt(v*v+2*P.a*x))/P.a;
    return t;
  }
  /* the lanes sorted: each car's leader and follower in its lane, each lane's last car, each link's front car */
  function bimTrSortCars(RUN){
    var C=RUN.c,N=RUN.N,n=C.n,ns=RUN.nSlots,i,k,c;
    for(k=0;k<=ns;k++)C.cnt[k]=0;
    for(c=0;c<n;c++){if(C.L[c]<0)continue;var sl=N.links[C.L[c]].slot+C.ln[c];C.key[c]=sl;C.cnt[sl+1]++;}
    for(k=0;k<ns;k++)C.cnt[k+1]+=C.cnt[k];
    var m=0;
    for(c=0;c<n;c++){if(C.L[c]<0)continue;C.ord[C.cnt[C.key[c]]++]=c;m++;}
    /* cnt[k] is now each slot's end; its start is the slot before's end */
    for(k=0;k<ns;k++){
      var st=k?C.cnt[k-1]:0,en=C.cnt[k];
      for(i=st+1;i<en;i++){var x=C.ord[i],sx=C.s[x],q=i-1;while(q>=st&&C.s[C.ord[q]]>sx){C.ord[q+1]=C.ord[q];q--;}C.ord[q+1]=x;}
      C.last[k]=en>st?C.ord[st]:-1;C.head[k]=en>st?C.ord[en-1]:-1;
      for(i=st;i<en;i++){c=C.ord[i];C.lead[c]=i+1<en?C.ord[i+1]:-1;C.fol[c]=i>st?C.ord[i-1]:-1;}
    }
    for(k=0;k<N.links.length;k++)C.front[k]=-1;
    for(i=0;i<m;i++){c=C.ord[i];var l=C.L[c],f=C.front[l];if(f<0||C.s[c]>C.s[f])C.front[l]=c;}
  }
  /* the gap and approach to what is ahead of a car in its lane: the car ahead, or the last car on its next link */
  function bimTrAhead(RUN,c,ln,out){
    var C=RUN.c,N=RUN.N,l=C.L[c],Lk=N.links[l],ld=bimTrLeaderIn(RUN,c,ln);
    if(ld>=0){out.s=C.s[ld]-C.len[ld]-C.s[c];out.v=C.v[ld];return out;}
    var nx=C.nx[c];
    if(nx>=0){var Ln=N.links[nx],lk=C.last[Ln.slot+Math.min(ln,Ln.lanes-1)];if(lk>=0){out.s=Lk.len-C.s[c]+C.s[lk]-C.len[lk];out.v=C.v[lk];return out;}}
    out.s=RUN.P.free;out.v=C.v[c];
    return out;
  }
  /* the car ahead in a lane (its own, or another for a lane change) */
  function bimTrLeaderIn(RUN,c,ln){
    var C=RUN.c,N=RUN.N,l=C.L[c];
    if(ln===C.ln[c])return C.lead[c];
    var k=N.links[l].slot+ln,st=k?C.cnt[k-1]:0,en=C.cnt[k],s=C.s[c],i;
    for(i=st;i<en;i++){var x=C.ord[i];if(x!==c&&C.s[x]>s)return x;}
    return -1;
  }
  function bimTrFollowerIn(RUN,c,ln){
    var C=RUN.c,N=RUN.N,l=C.L[c],k=N.links[l].slot+ln,st=k?C.cnt[k-1]:0,en=C.cnt[k],s=C.s[c],i,f=-1;
    for(i=st;i<en;i++){var x=C.ord[i];if(x!==c&&C.s[x]<=s)f=x;}
    return f;
  }
  /* what holds a car at its line: no room past a signal, a red, an amber it would not reach its line in (a car
     that goes on an amber keeps going), a stop not yet made, its turn at an all-way stop, a
     major road's car too near, a walker on a crossing it is about to cross. Returns the distance to the line, or
     Infinity when nothing holds it */
  var BIM_TR_SIG={};
  function bimTrHold(RUN,c){
    var C=RUN.c,N=RUN.N,l=C.L[c],Lk=N.links[l],h=bimTrHoldAt(RUN,c,l,C.s[c],C.nx[c],false),nx=C.nx[c],tg=C.tg[c];
    /* and the next link's line, where it is near: a short link before a signal is no surprise */
    if(h===Infinity&&nx>=0&&Lk.len-C.s[c]<bimStd('app.traffic','look'))h=bimTrHoldAt(RUN,c,nx,C.s[c]-Lk.len,tg>=0?RUN.targets[tg].nx[nx]:-3,true);
    return h;
  }
  /* the hold of link l's line for car c at s along it, its next link nx (-1 the lot or out, -3 not drawn yet); look: the
     line ahead, seen from the link before, where the car has made no stop and taken no amber yet */
  function bimTrHoldAt(RUN,c,l,s,nx,look){
    var C=RUN.c,N=RUN.N,Lk=N.links[l],j=N.J[Lk.jb],sl,d,h=Infinity;
    /* a walker on the crossing at this link's start, which the car has not reached: it waits short of it, in the
       junction it has entered */
    var ja=look?null:N.J[Lk.ja];
    if(ja&&!ja.bnd&&bimTrOccOn(RUN,ja,Lk.armOut,false)&&s<ja.cw-1)h=ja.cw-1-s;
    if(!j||j.bnd)return h;
    if(nx===-1&&C.tg[c]>=0)return h;            /* into the lot or its car park */
    sl=bimTrStopLine(N,Lk);d=sl-s;
    /* a walker on the crossing of the arm it turns into: it goes past its line and waits short of that crossing */
    if(nx>=0&&N.links[nx].ja===j.i&&bimTrOccOn(RUN,j,N.links[nx].armOut,false))h=Math.min(h,Lk.len-s+Math.max(0,j.cw-1));
    /* a left turn waits for the oncoming in the junction, past its line, as a permissive left does: the amber's gap is
       its */
    var P=RUN.plans[j.i],sg=!!(P&&P.of.hasOwnProperty(l)),opp=sg?P.ph[P.of[l]].ins:(j.kind==='yield'&&j.major[l]?j.majors:null);
    if(opp&&s<Lk.len-0.5&&!(!look&&C.go[c]&&d>-0.5)&&bimTrLeftWait(RUN,c,j,l,nx,d,opp))h=Math.min(h,Lk.len-s);   /* one gone on the amber reaches its line first */
    if(d<-0.5)return h;                         /* past its line: it goes on */
    /* the lane it goes into claimed by a car from another way, not yet clear of it: it waits its turn */
    if(nx>=0&&bimTrClaimed(RUN,c,l,nx))return Math.min(h,d);
    /* no room past a signal for it: it does not enter (the junction kept clear, and none caught in it by the red) */
    if(j.kind==='signal'&&nx>=0){var Ln=N.links[nx],lk=C.last[Ln.slot+Math.min(C.ln[c],Ln.lanes-1)];if(lk>=0&&lk!==c&&C.v[lk]<bimStd('app.traffic','queue_v')&&C.s[lk]-C.len[lk]<C.len[c]+RUN.P.s0)return Math.min(h,d);}
    var st=look?0:C.st[c];
    if(sg){
      bimTrSig(P,P.of[l],RUN.t,BIM_TR_SIG);
      if(BIM_TR_SIG.s==='r')return Math.min(h,d);
      if(BIM_TR_SIG.s==='y'){
        /* near goes and far stops: it goes only if it reaches its line before the amber ends, braking as it is; one gone
           that would no longer make it stops, where it still can without braking hard */
        var far=d>bimTrReach(C.v[c],C.a[c],BIM_TR_SIG.left);
        if(look||!C.go[c]){if(far)return Math.min(h,d);if(!look)C.go[c]=1;}
        else if(far&&d>=C.v[c]*C.v[c]/(2*RUN.P.b)){C.go[c]=0;return Math.min(h,d);}
      }
    }else if(j.kind==='allstop'){
      if(!st)return Math.min(h,d);
      var q=RUN.jq[j.i]||(RUN.jq[j.i]=[]);if(q.indexOf(c)<0)q.push(c);
      if(q[0]!==c||RUN.t<RUN.busy[j.i])return Math.min(h,d);
    }else if(j.kind==='yield'){
      if(j.stop[l]&&!st)return Math.min(h,d);
      if(!j.major[l]){
        var need=bimTrClear(RUN,j,c,Math.max(0,d))+bimStd('sumo.rules','gap'),k;
        for(k=0;k<j.ins.length;k++){
          var m=j.ins[k];if(m===l||!j.major[m])continue;
          var f=C.front[m];if(f<0)continue;
          var Lm=N.links[m],tau=(Lm.len-C.s[f])/Math.max(C.v[f],0.5);
          if(tau<need&&C.v[f]>0.3)return Math.min(h,d);
        }
      }
    }
    /* a walker on the crossing of its own arm, just past its line */
    if(bimTrOccOn(RUN,j,Lk.arm,true))return Math.min(h,d);
    return h;
  }
  /* a car turning left waits for the oncoming: the front car of each other approach that has the way with it (its
     phase, or the other major road), unless that one turns left too (they pass in front of each other), while it would
     reach the junction before this one has cleared it; a standing car only once it sets off (one held in a queue is
     not coming, and waiting for it would lock both ways). The front car of each lane of each */
  function bimTrLeftWait(RUN,c,j,l,nx,d,cands){
    var C=RUN.c,N=RUN.N,lim=-bimStd('app.traffic','left'),k,ln;
    if(nx<0||bimTrTurnOf(j,l,nx)>lim)return false;
    var need=bimTrClear(RUN,j,c,d)+bimStd('sumo.rules','gap'),a=RUN.P.a;
    for(k=0;k<cands.length;k++){
      var m=cands[k],Lm=N.links[m];if(m===l)continue;
      for(ln=0;ln<Lm.lanes;ln++){
        var f=C.head[Lm.slot+ln];if(f<0)continue;
        if(C.nx[f]>=0&&bimTrTurnOf(j,m,C.nx[f])<=lim)continue;
        var x=Math.max(0,Lm.len-C.s[f]),v=C.v[f];
        if(v<0.3&&C.a[f]<=0.05)continue;
        if((-v+Math.sqrt(v*v+2*a*x))/a<need)return true;
      }
    }
    return false;
  }
  /* a lane claimed: by a car from another link still in the junction, or on the lane and not yet its standing gap in */
  function bimTrClaimed(RUN,c,l,nx){
    var C=RUN.c,N=RUN.N,Ln=N.links[nx],k=Ln.slot+Math.min(C.ln[c],Ln.lanes-1),o=C.claim[k];
    if(o<0||o===c)return false;
    if(C.L[o]===nx){if(C.s[o]-C.len[o]>=RUN.P.s0){C.claim[k]=-1;return false;}return true;}
    if(C.L[o]<0||C.nx[o]!==nx||C.L[o]===l||C.s[o]<bimTrStopLine(N,N.links[C.L[o]])-0.5){if(C.L[o]!==l)C.claim[k]=-1;return false;}
    return true;
  }
  /* how far a car goes in t at its speed, braking as it is (never counting on speeding up) */
  function bimTrReach(v,a,t){if(a>=0)return v*t;var ts=v/-a;return ts<t?v*v/(2*-a):v*t+a*t*t/2;}
  function bimTrTurnOf(j,l,o){var T=j.tr[l]||[],i;for(i=0;i<T.length;i++)if(T[i].o===o)return T[i].ang;return 0;}
  /* a walker on the half of arm k's crossing a car passes: an inbound car the half beside the inbound lanes (on the
     right as it comes in), an outbound car the other, each with a walker within a step of the middle; the whole
     crossing on a one-way street */
  function bimTrOccOn(RUN,j,k,inb){
    var a=j.armBase+k,A=j.arms[k];
    if(A.lin<0||A.lout<0)return RUN.occ[a]>0;
    return RUN.occH[a*2+(inb?1:0)]>0;
  }
  function bimTrOcc(RUN,a,b,d){if(a<0)return;RUN.occ[a]+=d;if(b&1)RUN.occH[a*2]+=d;if(b&2)RUN.occH[a*2+1]+=d;}
  var BIM_TR_AH={s:0,v:0};
  function bimTrAccOf(RUN,c,ln){
    var C=RUN.c,N=RUN.N,Lk=N.links[C.L[c]],P=RUN.P,v=C.v[c];
    if(ln===undefined)ln=C.ln[c];
    bimTrAhead(RUN,c,ln,BIM_TR_AH);
    var a=bimTrIdm(v,Lk.v0,BIM_TR_AH.s,v-BIM_TR_AH.v,P);
    var h=bimTrHold(RUN,c);   /* the line holds every car before it, not only the first: the one ahead may be past it */
    if(h<Infinity){var ah=bimTrIdm(v,Lk.v0,Math.max(0.01,h),v,P);if(ah<a)a=ah;}
    return Math.max(-9,a);
  }
  /* MOBIL, symmetric, where a direction has two lanes or more: each car every other step */
  function bimTrLaneChanges(RUN){
    var C=RUN.c,N=RUN.N,P=RUN.P,p=bimStd('mobil','p'),thr=bimStd('mobil','thr'),bs=bimStd('mobil','bsafe'),c,par=RUN.steps&1;
    for(c=par;c<C.n;c+=2){
      var l=C.L[c];if(l<0)continue;
      var Lk=N.links[l];if(Lk.lanes<2||RUN.t-C.lc[c]<3||C.s[c]>bimTrStopLine(N,Lk)-5||C.s[c]<C.len[c])continue;
      var best=-1,bg=thr,cur=C.a[c],ln=C.ln[c],d;
      for(d=-1;d<=1;d+=2){
        var nl=ln+d;if(nl<0||nl>=Lk.lanes)continue;
        var nf=bimTrFollowerIn(RUN,c,nl),nld=bimTrLeaderIn(RUN,c,nl);
        if(nf>=0&&C.s[c]-C.len[c]-C.s[nf]<P.s0)continue;
        if(nld>=0&&C.s[nld]-C.len[nld]-C.s[c]<P.s0)continue;
        var an=bimTrAccOf(RUN,c,nl),gain=an-cur;
        if(nf>=0){
          var nfa=C.a[nf],gapn=C.s[c]-C.len[c]-C.s[nf],nfa2=bimTrIdm(C.v[nf],N.links[C.L[nf]].v0,gapn,C.v[nf]-C.v[c],P);
          if(nfa2<-bs)continue;                                  /* safe: the new follower brakes no harder than b_safe */
          gain+=p*(nfa2-nfa);
        }
        var of=C.fol[c];
        if(of>=0){
          var ofa=C.a[of],ld0=C.lead[c],ofa2;
          if(ld0>=0)ofa2=bimTrIdm(C.v[of],Lk.v0,C.s[ld0]-C.len[ld0]-C.s[of],C.v[of]-C.v[ld0],P);else ofa2=bimTrIdm(C.v[of],Lk.v0,P.free,0,P);
          gain+=p*(ofa2-ofa);
        }
        if(gain>bg){bg=gain;best=nl;}
      }
      if(best>=0){
        C.ln[c]=best;C.lc[c]=RUN.t;C.a[c]=bimTrAccOf(RUN,c,best);RUN.res.lc++;
        var ks=Lk.slot+best;if(C.last[ks]<0||C.s[C.last[ks]]>C.s[c])C.last[ks]=c;   /* the lane's last at once, for a car coming in this step */
      }
    }
  }
  /* ---- the walkers ---- */
  function bimTrWalkStep(RUN,dt){
    var W=RUN.w,i,k,n=W.n,nr=RUN.routes.length;
    for(k=0;k<=nr*2;k++)W.cnt[k]=0;
    for(i=0;i<n;i++){if(W.R[i]<0)continue;W.key[i]=W.R[i]*2+W.st[i];W.cnt[W.key[i]+1]++;}
    for(k=0;k<nr*2;k++)W.cnt[k+1]+=W.cnt[k];
    for(i=0;i<n;i++){if(W.R[i]<0)continue;W.ord[W.cnt[W.key[i]]++]=i;}
    for(k=0;k<nr*2;k++){
      var st=k?W.cnt[k-1]:0,en=W.cnt[k],q;
      for(q=st+1;q<en;q++){var x=W.ord[q],px=W.p[x],r=q-1;while(r>=st&&W.p[W.ord[r]]>px){W.ord[r+1]=W.ord[r];r--;}W.ord[r+1]=x;}
      for(q=en-1;q>=st;q--)bimTrWalkOne(RUN,W.ord[q],q+1<en?W.ord[q+1]:-1,dt);
    }
  }
  function bimTrWalkOne(RUN,i,ahead,dt){
    var W=RUN.w,r=RUN.routes[W.R[i]],v=W.v0[i],k,p0=W.p[i];
    if(ahead>=0&&W.R[ahead]>=0){var gap=W.p[ahead]-W.p[i];if(gap<2)v=Math.max(0,Math.min(v,W.v0[i]*(gap-0.5)/1.5));}
    var np=p0+v*dt;
    /* a crossing ahead: wait at its start until it may be crossed */
    for(k=0;k<r.cr.length;k++){
      var cr=r.cr[k];
      if(p0<cr.s0-1e-6&&np>=cr.s0-1e-6){
        if(!bimTrMayCross(RUN,cr)){np=cr.s0-1e-6;if(W.wait[i]<0)W.wait[i]=RUN.t;}
        else{
          if(!bimTrMayCrossStrict(RUN,cr))RUN.res.walkBad++;
          if(W.wait[i]>=0&&RUN.res.t0<=RUN.t){RUN.res.cw[cr.j*2]+=RUN.t-W.wait[i];}
          if(RUN.res.t0<=RUN.t)RUN.res.cw[cr.j*2+1]+=1;
          W.wait[i]=-1;
        }
        break;
      }
    }
    /* on a crossing or off it: the arm's count of walkers on it, and on each half (within a step of the middle, both) */
    var was=W.cr[i],wb=W.hb[i],now=-1,nb=0;
    for(k=0;k<r.cr.length;k++){
      var c2=r.cr[k];
      if(np>=c2.s0&&np<c2.s1){var u=(np-c2.s0)/c2.len,mg=bimStd('sumo.rules','stripe')/c2.len;now=RUN.N.J[c2.j].armBase+c2.k;nb=(u<0.5+mg?(c2.from>0?1:2):0)|(u>0.5-mg?(c2.from>0?2:1):0);break;}
    }
    if(was!==now||wb!==nb){bimTrOcc(RUN,was,wb,-1);bimTrOcc(RUN,now,nb,1);W.cr[i]=now;W.hb[i]=nb;}
    W.p[i]=np;W.v[i]=np-p0>0?(np-p0)/dt:0;
    W.px[i]=W.x[i];W.pz[i]=W.z[i];
    if(np>=r.len){
      bimTrOcc(RUN,W.cr[i],W.hb[i],-1);W.cr[i]=-1;W.hb[i]=0;
      bimTrWalkArrive(RUN,i,r);bimTrWalkFree(RUN,i);return;
    }
    bimTrWalkPlace(RUN,i);
  }
  /* a crossing may be started: at a signal while the green parallel to it leaves time to cross at the clearance
     speed (the owner's rule); elsewhere when no car is within the walk gap of it, nor on it */
  var BIM_TR_SIGW={};
  function bimTrMayCross(RUN,cr){
    var N=RUN.N,j=N.J[cr.j],a=j.arms[cr.k],P=RUN.plans[j.i];
    if(P){
      var pk=P.armPh.hasOwnProperty(cr.k)?1-P.armPh[cr.k]:0;
      bimTrSig(P,pk,RUN.t,BIM_TR_SIGW);
      return BIM_TR_SIGW.s==='g'&&BIM_TR_SIGW.left>=cr.len/bimStd('mutcd.walk','clear');
    }
    var C=RUN.c,g=bimStd('app.traffic','walk_gap'),l,f;
    if(a.lin>=0){l=N.links[a.lin];f=C.front[a.lin];
      if(f>=0){var dcw=l.len-j.cw-C.s[f];if(dcw>-3&&(dcw<0||dcw/Math.max(C.v[f],0.1)<g)&&C.v[f]>0.5||dcw>-3&&dcw<1)return false;}}
    if(a.lout>=0){var lo=N.links[a.lout],k,c;
      for(k=0;k<lo.lanes;k++){c=C.last[lo.slot+k];if(c>=0&&C.s[c]-C.len[c]<j.cw+3)return false;}
      for(k=0;k<j.ins.length;k++){var m=j.ins[k],fm=C.front[m];if(fm>=0&&C.nx[fm]===a.lout){var Lm=N.links[m];if((Lm.len-C.s[fm])/Math.max(C.v[fm],0.1)<g&&C.v[fm]>0.5)return false;}}
    }
    return true;
  }
  /* the check the suite's count rests on: a walker starting across a signalled crossing with the parallel green too
     short to finish is counted (none should be) */
  function bimTrMayCrossStrict(RUN,cr){
    var j=RUN.N.J[cr.j],P=RUN.plans[j.i];
    if(!P)return true;
    var pk=P.armPh.hasOwnProperty(cr.k)?1-P.armPh[cr.k]:0,o={};
    bimTrSig(P,pk,RUN.t,o);
    return o.s==='g'&&o.left+1e-6>=cr.len/bimStd('mutcd.walk','clear');
  }
  /* at the end of a way: at a door, counted; at the car, a car out; at a stop or the edge, gone */
  function bimTrWalkArrive(RUN,i,r){
    if(r.kind==='in'||r.kind==='tin'||r.kind==='win'){if(RUN.res.t0<=RUN.t)RUN.res.doors[r.door].i++;return;}
    if(r.kind==='out'){
      var p=RUN.park[r.extra],l=-1;
      RUN.N.links.forEach(function(Lk){if(l<0&&Lk.a===p.n&&RUN.N.J[Lk.jb]&&!RUN.N.J[Lk.jb].lot)l=Lk.i;});
      if(l>=0){var sk=RUN.sinks.length?RUN.sinks[Math.floor(RUN.rng()*RUN.sinks.length)]:null;RUN.lotQ.push({l:l,tg:sk?sk.tg:-1});}
    }
  }
  /* ---- the demand, each step: background cars at the boundaries, the lot's trips, the walkers' trips ---- */
  function bimTrSpawn(RUN,dt){
    var N=RUN.N,T=RUN.t,rng=RUN.rng,i;
    RUN.lotQ=RUN.lotQ||[];RUN.lotPend=RUN.lotPend||[];
    for(i=0;i<RUN.srcs.length;i++){
      var S=RUN.srcs[i],h=3600/S.q;
      if(!S.next)S.next=T+h*rng();
      while(S.next<=T){S.pend++;S.next+=h*(0.5+rng());}
      if(S.pend>0){if(bimTrCarNew(RUN,S.l,0,N.links[S.l].v0,0,-1)>=0){S.pend--;S.held=false;}else if(!S.held){S.held=true;RUN.res.blocked++;}}   /* a car held at the edge, counted once */
    }
    if(!RUN.lotOk)return;
    var TR=RUN.trips,dIn=TR.tin*dt/3600,dOut=TR.tout*dt/3600;
    /* in: a car from a boundary chosen by the boundaries' volumes, to the lot (or its car park) */
    RUN.accIn=(RUN.accIn||0)+dIn;
    while(RUN.accIn>=1&&RUN.srcs.length){
      RUN.accIn-=1;
      var r=rng()*RUN.srcQ,acc=0,S2=RUN.srcs[0];
      for(i=0;i<RUN.srcs.length;i++){acc+=RUN.srcs[i].q;if(r<acc){S2=RUN.srcs[i];break;}}
      var pk=RUN.park[Math.floor(rng()*RUN.park.length)];
      if(pk&&RUN.targets[pk.tg].nx[S2.l]!==-2)RUN.lotPend.push({l:S2.l,tg:pk.tg,held:false});
    }
    for(i=0;i<RUN.lotPend.length;){
      var x=RUN.lotPend[i];
      if(bimTrCarNew(RUN,x.l,0,N.links[x.l].v0,1,x.tg)>=0)RUN.lotPend.splice(i,1);
      else{if(!x.held){x.held=true;RUN.res.blocked++;}i++;}
    }
    /* out: the driver walks from a door to the car; the car then waits to leave (the lot's queue) */
    RUN.accOut=(RUN.accOut||0)+dOut;
    while(RUN.accOut>=1&&RUN.rOut.length){RUN.accOut-=1;bimTrWalkNew(RUN,RUN.rOut[Math.floor(rng()*RUN.rOut.length)]);}
    while(RUN.lotQ.length&&bimTrCarNew(RUN,RUN.lotQ[0].l,0,0,2,RUN.lotQ[0].tg)>=0){RUN.lotQ.shift();RUN.res.lotOut++;}
    /* by transit and on foot, at the tract's shares of the lot's trips */
    if(RUN.share){
      RUN.accT=(RUN.accT||0)+(TR.tin+TR.tout)*RUN.share.t*dt/3600;
      RUN.accW=(RUN.accW||0)+(TR.tin+TR.tout)*RUN.share.w*dt/3600;
      var fin=TR.tin+TR.tout>0?TR.tin/(TR.tin+TR.tout):0.5;
      while(RUN.accT>=1){RUN.accT-=1;var L1=rng()<fin?RUN.rTin:RUN.rTout;if(L1.length)bimTrWalkNew(RUN,L1[Math.floor(rng()*L1.length)]);}
      while(RUN.accW>=1){RUN.accW-=1;var L2=rng()<fin?RUN.rWin:RUN.rWout;if(L2.length)bimTrWalkNew(RUN,L2[Math.floor(rng()*L2.length)]);}
    }
  }
  /* every bin: the lot's queue sampled -- the cars waiting to leave it, and the most cars standing in a row on the
     street before its entry */
  function bimTrSample(RUN){
    var N=RUN.N,C=RUN.c,Q=RUN.res.q,vq=bimStd('app.traffic','queue_v'),qr=bimStd('app.traffic','queue_r');
    RUN.res.bin=RUN.t;
    if(!RUN.lotOk||RUN.res.t0>RUN.t)return;
    var out=RUN.lotQ.length,st=0,c;
    var ent=N.lot.at;
    N.links.forEach(function(Lk){if(Lk.b!==ent)return;var n=0;for(c=0;c<C.n;c++)if(C.L[c]===Lk.i&&C.v[c]<vq&&Lk.len-C.s[c]<=qr)n++;if(Lk.lot)out+=n;else st=Math.max(st,n);});
    Q.n++;Q.out+=out;Q.outMax=Math.max(Q.outMax,out);Q.st+=st;Q.stMax=Math.max(Q.stMax,st);
  }
  /* ---- the run on the clock ---- */
  function bimTrFps(){return A3D_TR.run?Math.min(BIM_ANIM.fps,A3D_TR.run.cap.fps):BIM_ANIM.fps;}   /* the frames a second: fewer at Light */
  function bimTrStart(){
    var R;
    try{R=bimTrBuild();}catch(eB){console.warn('[BIM] The traffic simulation could not be built',eB);a3dToast('The traffic simulation could not be built - see the console');return null;}
    if(R.err){a3dToast('Traffic and people: '+R.err);A3D_TR.run=null;return null;}
    A3D_TR.run=R;
    /* the warm-up: the streets filled before anything is tallied */
    var n=Math.round(bimStd('app.traffic','warm')/R.step),t0=performance.now(),i;
    try{for(i=0;i<n;i++)bimTrStep(R);}catch(eW){console.warn('[BIM] The traffic warm-up failed',eW);a3dToast('The traffic simulation stopped in its warm-up - see the console');A3D_TR.run=null;return null;}
    R.warmMs=performance.now()-t0;R.warm=true;
    bimTrResetTallies(R);
    return R;
  }
  function bimTrStop(){if(A3D_TR.run){A3D_TR.last=bimTrResults(A3D_TR.run);}A3D_TR.run=null;}
  /* the clock's seconds, at the run's speed, in fixed steps; a long frame lowers the quality a step */
  function bimTrAdvance(sec){
    var R=A3D_TR.run;
    if(!R||!(sec>0))return;
    R.acc+=sec*R.set.speed;
    var n=Math.floor(R.acc/R.step),max=Math.ceil(R.set.speed*0.1/R.step)+1,t0=performance.now(),i;
    if(n>max){n=max;R.acc=0;}else R.acc-=n*R.step;
    try{for(i=0;i<n;i++)bimTrStep(R);}catch(eS){console.warn('[BIM] A step of the traffic simulation failed',eS);bimTrStop();a3dToast('The traffic simulation stopped: a step failed - see the console');return;}
    var ms=performance.now()-t0;
    R.frameMs.push(ms);if(R.frameMs.length>30)R.frameMs.shift();
    var mean=0;R.frameMs.forEach(function(x){mean+=x;});mean/=R.frameMs.length;
    if(R.frameMs.length>=30&&mean>1000/R.cap.fps*0.6){
      var qi=BIM_TR_QORDER.indexOf(R.qk);
      if(qi>0){R.qk=BIM_TR_QORDER[qi-1];R.cap=BIM_TR_Q[R.qk];R.frameMs=[];R.slow++;a3dToast('Traffic and people: frames ran long, so the quality is '+R.cap.name+' now');}
    }
  }
  /* ---- what the run found, in the tallies' terms ---- */
  function bimTrResults(R){
    var N=R.N,res=R.res,span=Math.max(1e-9,R.t-res.t0),out={t:span,spawned:res.spawned,exited:res.exited,lotIn:res.lotIn,lotOut:res.lotOut,red:res.red,walkBad:res.walkBad,lc:res.lc,
      carsCap:res.carsCap,walkCap:res.walkCap,blocked:res.blocked,doors:[],j:[],q:null,trips:R.trips,qk:R.qk};
    N.doors.forEach(function(d,i){out.doors.push({name:d.name,x:d.x,z:d.z,inH:res.doors[i].i*3600/span,outH:res.doors[i].o*3600/span,n:res.doors[i].i+res.doors[i].o});});
    N.J.forEach(function(j){
      if(j.kind==='pass'||j.bnd)return;
      var sd=0,nd=0;j.ins.forEach(function(l){sd+=res.del[l*2];nd+=res.del[l*2+1];});
      var wn=res.cw[j.i*2+1];
      out.j.push({i:j.i,x:j.x,z:j.z,kind:j.kind,carDelay:nd?sd/nd:null,cars:nd,walkWait:wn?res.cw[j.i*2]/wn:null,walkers:wn});
    });
    if(R.lotOk&&res.q.n)out.q={outMean:res.q.out/res.q.n,outMax:res.q.outMax,stMean:res.q.st/res.q.n,stMax:res.q.stMax,n:res.q.n};
    return out;
  }
