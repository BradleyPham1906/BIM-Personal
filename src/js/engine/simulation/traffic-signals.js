  /* ================= __acad3dV171: traffic and people around the site: the signals =================
     reference/research-traffic.md, sections 2, 7 and 8 (the owner's decision 1): each signalled junction's own fixed
     plan, assumed and said, OpenStreetMap mapping where a signal is and never its timing. Two phases by axis; Webster's
     cycle from the critical lane volumes, held between the timing manual's least and its preferred most; the yellow and
     the red clearance by Kell and Fullerton within the MUTCD's limits; the greens shared by demand, each at least the
     manual's least for its class and WALK with the crossing of the street it parallels. No offsets: each junction alone. */
  /* an approach's class for its least green: the FHWA class its street is read as (app.roads), a major arterial over
     the speed set as fast */
  function bimTrGreenClass(Lk){
    var fc=(bimStd('app.roads','classes')||{})[Lk.base];
    if(fc==='interstate'||fc==='freeway'||fc==='opa')return Lk.v0*3.6>bimStd('stm.signal','fast')?'fast':'major';
    if(fc==='minor_art')return 'minor';
    return 'local';
  }
  function bimTrAxisOff(b,axis){var d=((b-axis)%180+180)%180;return d<45||d>135;}   /* within 45 degrees of the axis, either way */
  /* the plan, from what is pure: the approaches [{arm, bear, q, lanes, v, cls}] and the car arms [{k, bear, w}] */
  function bimTrPlanOf(ap,arms){
    var sat=bimStd('stm.signal','sat'),lost=bimStd('stm.signal','lost'),wb=bimStd('stm.signal','webster')||[1.5,5],cmin=bimStd('stm.signal','cycle_min'),cmax=bimStd('stm.signal','cycle_max'),
      kt=bimStd('stm.signal','kf_t'),ka=bimStd('stm.signal','kf_a'),klv=bimStd('stm.signal','kf_lv'),mg=bimStd('stm.signal','min_green')||{},
      y0=bimStd('mutcd.signal','yel_min'),y1=bimStd('mutcd.signal','yel_max'),rmax=bimStd('mutcd.signal','red_max'),walk=bimStd('mutcd.signal','walk'),
      clr=bimStd('mutcd.walk','clear'),ymax=bimStd('app.traffic','y_max'),i,k;
    if(!ap.length)return null;
    var crit=ap[0];
    for(i=1;i<ap.length;i++)if(ap[i].q/ap[i].lanes>crit.q/crit.lanes)crit=ap[i];
    var axis=crit.bear%180,ph=[{arms:[],ap:[]},{arms:[],ap:[]}];
    arms.forEach(function(a){ph[bimTrAxisOff(a.bear,axis)?0:1].arms.push(a.k);});
    ap.forEach(function(a){ph[bimTrAxisOff(a.bear,axis)?0:1].ap.push(a);});
    function wOf(p){var w=0;arms.forEach(function(a){if(ph[p].arms.indexOf(a.k)>=0&&a.w>w)w=a.w;});return w;}
    var Y=0,sumCh=0,P=[];
    for(k=0;k<2;k++){
      var A=ph[k].ap,vc=0,v=0,gd=0,o={arms:ph[k].arms,ins:A.map(function(a){return a.li;}),y:0,Y:0,AR:0,G:0};
      A.forEach(function(a){vc=Math.max(vc,a.q/a.lanes);v=Math.max(v,a.v);gd=Math.max(gd,mg[a.cls]||0);});
      o.y=vc/sat;Y+=o.y;
      if(A.length){
        o.Y=Math.min(y1,Math.max(y0,kt+v/(2*ka)));                      /* Kell and Fullerton's first term, flat */
        o.AR=Math.min(rmax,(wOf(1-k)+klv)/Math.max(v,0.1));             /* its second: across the other phase's widest street */
      }
      o.gdrv=gd;
      o.gped=walk+wOf(1-k)/clr;                                         /* WALK and the crossing of the street it parallels */
      o.gmin=Math.max(o.gdrv,o.gped);
      sumCh+=o.Y+o.AR;
      P.push(o);
    }
    var L=lost*2,C0=Y<ymax?(wb[0]*L+wb[1])/(1-Y):Infinity,C=Math.min(cmax,Math.max(cmin,C0)),grown=false;
    /* the greens: what the change intervals leave, by each phase's y, none under its least */
    var av=C-sumCh,fix=[false,false],guard=0;
    for(;;){
      var rest=av,yf=0;
      for(k=0;k<2;k++){if(fix[k])rest-=P[k].gmin;else yf+=P[k].y;}
      var any=false;
      for(k=0;k<2;k++)if(!fix[k]){P[k].G=yf>0?rest*P[k].y/yf:rest/(fix[0]||fix[1]?1:2);if(P[k].G<P[k].gmin-1e-9){fix[k]=true;any=true;}}
      for(k=0;k<2;k++)if(fix[k])P[k].G=P[k].gmin;
      if(!any||++guard>3)break;
    }
    if(P[0].G+P[1].G+sumCh>C+1e-9){C=P[0].G+P[1].G+sumCh;grown=true;}   /* the least greens do not fit: the cycle grows to hold them */
    var t=0;
    P.forEach(function(o){o.t0=t;t+=o.G+o.Y+o.AR;});
    return {C:C,C0:C0,Y:Y,L:L,ph:P,grown:grown,axis:axis};
  }
  /* a signalled junction's plan, from the network */
  function bimTrPlan(N,j){
    var ap=j.ins.map(function(li){var Lk=N.links[li],a=j.arms[Lk.arm];return {li:li,arm:a.k,bear:a.bear,q:Lk.q,lanes:Lk.lanes,v:Lk.v0,cls:bimTrGreenClass(Lk)};});
    var arms=j.arms.filter(function(a){return a.car;}).map(function(a){return {k:a.k,bear:a.bear,w:a.w};});
    var P=bimTrPlanOf(ap,arms);
    if(!P)return null;
    P.of={};P.armPh={};
    P.ph.forEach(function(o,k){o.ins.forEach(function(li){P.of[li]=k;});o.arms.forEach(function(a){P.armPh[a]=k;});});
    return P;
  }
  /* a phase's state at time t: 'g' with the green left, 'y', or 'r' */
  function bimTrSig(P,k,t,out){
    var tc=((t%P.C)+P.C)%P.C,o=P.ph[k],x=tc-o.t0;
    if(x<0)x+=P.C;
    if(x<o.G){out.s='g';out.left=o.G-x;}
    else if(x<o.G+o.Y){out.s='y';out.left=o.G+o.Y-x;}
    else{out.s='r';out.left=0;}
    return out;
  }
