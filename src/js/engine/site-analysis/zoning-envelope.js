  /* ================= __acad3dV160: Site analysis SA3, regulation: zoning, the envelope, the yield =================
     reference/research-zoning-envelope-yield.md. A3D.site.zoning is the record; everything else is
     worked out from it and the property, when asked. */
  var BIM_ZN_ROLES=['front','side','rear'];
  var BIM_ZN_DEF={district:'',uses:'',source:'',far:null,maxH:null,maxStoreys:null,cover:null,
    front:0,side:0,rear:0,baseH:null,step:0,skyH:null,skyR:null,sideH:null,sideR:null,rearH:null,rearR:null,
    frontSteps:[],sideSteps:[],rearSteps:[],frontLeg:0,legRoles:[],
    f2f:3.2,eff:82,unit:75,res:100,park:1,parkNon:0};
  var BIM_ZN_FIELDS={district:['text',40],uses:['text',200],source:['text',200],far:['num',0,50],maxH:['num',0,1000],maxStoreys:['int',0,300],cover:['num',1,100],
    front:['num',0,500],side:['num',0,500],rear:['num',0,500],baseH:['num',0,1000],step:['num',0,200],
    skyH:['num',0,1000],skyR:['num',0.05,50],sideH:['num',0,1000],sideR:['num',0.05,50],rearH:['num',0,1000],rearR:['num',0.05,50],
    frontLeg:['int',0,999],f2f:['num',2,10],eff:['num',30,100],unit:['num',10,1000],res:['num',0,100],park:['num',0,10],parkNon:['num',0,50]};
  var BIM_ZN_ZERO={step:1,front:1,side:1,rear:1,res:1,parkNon:1,frontLeg:1};   /* blank means none: 0 for these */
  var BIM_ZN_MAXSTEPS=6;
  var A3D_ZN={edit:false};
  function bimZn(){
    A3D.site=A3D.site||{};
    var z=A3D.site.zoning,k;
    if(!z||typeof z!=='object')z=A3D.site.zoning={};
    for(k in BIM_ZN_DEF)if(BIM_ZN_DEF.hasOwnProperty(k)&&z[k]===undefined)z[k]=Array.isArray(BIM_ZN_DEF[k])?BIM_ZN_DEF[k].slice():BIM_ZN_DEF[k];
    return z;
  }
  function bimZnHas(){
    var z=A3D.site&&A3D.site.zoning;
    return !!(z&&(z.district||z.far!=null||z.maxH!=null||z.maxStoreys||z.skyH!=null||z.sideH!=null||z.rearH!=null||
      (z.frontSteps&&z.frontSteps.length)||(z.sideSteps&&z.sideSteps.length)||(z.rearSteps&&z.rearSteps.length)));
  }
  function bimZnProperty(){var P=A3D.objs.filter(bimIsProperty);return P[0]||null;}
  /* one control: checked, kept, one undo step; a built envelope follows. A step is "frontSteps.0.h"
     (the height above which it applies) or ".s" (its setback); a side's role is "legRoles.2". */
  function bimZnSet(k,v){
    var z=bimZn(),m,F,cur,key=String(k||'');
    if((m=/^(front|side|rear)Steps\.(\d+)\.([hs])$/.exec(key))){
      var L=z[m[1]+'Steps'],ix=+m[2],j=m[3]==='h'?0:1;
      if(!L[ix])return false;
      if(v===''||v===null||v===undefined)v=null;
      else{v=parseFloat(v);if(!isFinite(v)||v<0||v>(j?500:1000)){a3dToast('That value is out of range (0 to '+(j?500:1000)+')');bimSaRefresh(true);return false;}}
      if(L[ix][j]===v)return true;
      return bimZnEdit(function(){L[ix][j]=v;});
    }
    if((m=/^legRoles\.(\d+)$/.exec(key))){
      var ri=+m[1],P=bimZnProperty();
      if(!P||ri>=P.legs.length)return false;
      v=String(v||'');if(v!=='front'&&v!=='side'&&v!=='rear')v='';
      cur=z.legRoles[ri]||'';if(cur===v)return true;
      return bimZnEdit(function(){var a=z.legRoles.slice();while(a.length<P.legs.length)a.push('');a[ri]=v;z.legRoles=a;});
    }
    F=BIM_ZN_FIELDS[key];
    if(!F)return false;
    if(F[0]==='text')v=String(v==null?'':v).replace(/\s+/g,' ').replace(/^ | $/g,'').slice(0,F[1]);
    else{
      if(v===''||v===null||v===undefined)v=BIM_ZN_ZERO[key]?0:null;
      else{v=parseFloat(v);if(!isFinite(v)||v<F[1]||v>F[2]){a3dToast('That value is out of range ('+F[1]+' to '+F[2]+')');bimSaRefresh(true);return false;}if(F[0]==='int')v=Math.round(v);}
    }
    if(z[key]===v)return true;
    return bimZnEdit(function(){z[key]=v;});
  }
  /* every change to the record: one undo step, the envelope rebuilt if there is one, the findings refilled */
  function bimZnEdit(fn){
    pushUndo();
    undoSuspend=true;
    try{fn();if(bimZnEnvelopeObj())bimZnPlaceEnvelope(true);bimSaFill(true);}finally{undoSuspend=false;}
    bimZnDone();
    return true;
  }
  function bimZnStepAdd(role){
    var z=bimZn(),L=z[role+'Steps'];
    if(!L)return false;
    if(L.length>=BIM_ZN_MAXSTEPS){a3dToast('At most '+BIM_ZN_MAXSTEPS+' steps a side');return false;}
    A3D_ZN.edit=true;
    return bimZnEdit(function(){L.push([null,null]);});
  }
  function bimZnStepDel(role,i){
    var z=bimZn(),L=z[role+'Steps'];
    if(!L||!(i>=0&&i<L.length))return false;
    return bimZnEdit(function(){L.splice(i,1);});
  }
  function bimZnDone(){refreshTree();refreshLayers();refreshProps();paint();saveSoon();bimSaRefresh(true);if(A3D_CLB.open&&A3D_CLB.kind==='zoning')bimClbOpen('zoning');else if(A3D_CLB.open&&bimBrdRec()&&bimBrdRec().figs)bimClbOpen();bimPresThumbsQueue();}
  /* the property's sides: each one's inward normal, and whether it is a front, a side or a rear --
     picked by hand, else the chosen front, the rear facing it, the sides between */
  function bimZnLegs(P,front,roles){
    var g=bimPropertyGeometry(P),R=g.ring,n=R.length,sa=0,L=[],i;
    for(i=0;i<n;i++)sa+=R[i][0]*R[(i+1)%n][1]-R[(i+1)%n][0]*R[i][1];
    var sgn=sa>0?1:-1;
    for(i=0;i<n;i++){
      var a=R[i],b=R[(i+1)%n],dx=b[0]-a[0],dz=b[1]-a[1],len=Math.sqrt(dx*dx+dz*dz)||1;
      L.push({a:a,b:b,len:len,d:[dx/len,dz/len],n:[sgn>0?-dz/len:dz/len,sgn>0?dx/len:-dx/len],role:'side',auto:true});
    }
    var f=Math.max(0,Math.min(n-1,front|0));
    L.forEach(function(l,i2){
      var o=roles&&roles[i2];
      if(i2===f){l.role='front';l.auto=!(o==='front');return;}
      if(o==='front'||o==='side'||o==='rear'){l.role=o;l.auto=false;return;}
      if(l.n[0]*L[f].n[0]+l.n[1]*L[f].n[1]<-0.7)l.role='rear';
    });
    return {ring:R,legs:L,front:f,area:Math.abs(g.area),sgn:sgn,y0:(P.y||0)+bimObjOffset(P)[1]};
  }
  function bimZnConvex(R){
    var n=R.length,s=0,i;
    for(i=0;i<n;i++){
      var a=R[i],b=R[(i+1)%n],c=R[(i+2)%n],cr=(b[0]-a[0])*(c[1]-b[1])-(b[1]-a[1])*(c[0]-b[0]);
      if(Math.abs(cr)<1e-9)continue;
      if(!s)s=cr>0?1:-1;else if((cr>0?1:-1)!==s)return false;
    }
    return true;
  }
  function bimZnCentroid(P){
    var a=0,cx=0,cz=0,i;
    for(i=0;i<P.length;i++){var p=P[i],q=P[(i+1)%P.length],cr=p[0]*q[1]-q[0]*p[1];a+=cr;cx+=(p[0]+q[0])*cr;cz+=(p[1]+q[1])*cr;}
    return Math.abs(a)>1e-12?[cx/(3*a),cz/(3*a)]:P[0];
  }
  /* ---- the rules: each role's setback at a height ---- */
  function bimZnRules(z){
    var R={};
    BIM_ZN_ROLES.forEach(function(r){
      var o={base:+z[r]||0,steps:[],plane:null},st=z[r+'Steps']||[],k;
      for(k=0;k<st.length;k++){var s=st[k];if(s&&s[0]!==null&&s[1]!==null&&isFinite(s[0])&&isFinite(s[1]))o.steps.push([+s[0],+s[1]]);}
      if(r==='front'&&z.baseH!==null&&z.step>0)o.steps.push([z.baseH,(+z.front||0)+z.step]);   /* the street wall, then the stepback */
      var ph=z[r==='front'?'skyH':r+'H'],pr=z[r==='front'?'skyR':r+'R'];
      if(ph!==null&&ph!==undefined&&pr)o.plane=[+ph,+pr];
      o.steps.sort(function(x,y){return x[0]-y[0];});
      R[r]=o;
    });
    return R;
  }
  /* the setback a rule asks for at height h. side < 0: the limit from below (a step at h not yet
     taken: a 15 m street wall may reach 15 m); side > 0: from above */
  function bimZnInset(o,h,side){
    var s=o.base,k,t;
    for(k=0;k<o.steps.length;k++){t=o.steps[k][0];if((side>0?t<=h+1e-9:t<h-1e-9)&&o.steps[k][1]>s)s=o.steps[k][1];}
    if(o.plane){t=(h-o.plane[0])/o.plane[1];if(t>s)s=t;}
    return s;
  }
  /* the heights where a rule changes: its steps, and where its plane overtakes its setbacks */
  function bimZnRuleBreaks(o){
    var B=[],k;
    for(k=0;k<o.steps.length;k++)B.push(o.steps[k][0]);
    if(o.plane){B.push(o.plane[0]+o.plane[1]*o.base);for(k=0;k<o.steps.length;k++)B.push(o.plane[0]+o.plane[1]*o.steps[k][1]);}
    return B;
  }
  /* ---- the plate at a height: the lot, each side moved in by its rule's setback there ----
     Each corner carries the two sides it lies on, so plates at two heights match corner for corner. */
  function bimZnSetbacks(C,h,side){var L=C.legs.legs,sb=[],i;for(i=0;i<L.length;i++)sb.push(bimZnInset(C.rules[L[i].role],h,side));return sb;}
  function bimZnPlate(C,h,side){
    var L=C.legs.legs,n=L.length,sb=bimZnSetbacks(C,h,side),i,j,k,poly;
    if(C.convex){
      poly=[];for(i=0;i<n;i++)poly.push({p:C.legs.ring[i],t:[(i+n-1)%n,i]});
      for(j=0;j<n&&poly.length;j++){
        if(!(sb[j]>1e-12))continue;
        var out=[],m=poly.length,lj=L[j];
        for(k=0;k<m;k++){
          var A=poly[k],B=poly[(k+1)%m],da=(A.p[0]-lj.a[0])*lj.n[0]+(A.p[1]-lj.a[1])*lj.n[1]-sb[j],db=(B.p[0]-lj.a[0])*lj.n[0]+(B.p[1]-lj.a[1])*lj.n[1]-sb[j],ia=da>=-1e-9,ib=db>=-1e-9;
          if(ia)out.push(A);
          if(ia!==ib){var tt=da/(da-db);out.push({p:[A.p[0]+(B.p[0]-A.p[0])*tt,A.p[1]+(B.p[1]-A.p[1])*tt],t:ia?[A.t[1],j]:[j,A.t[1]]});}
        }
        poly=out.length>=3?out:[];
      }
    }else{
      poly=bimZnOffset(C,sb);
      if(poly===null)return null;
    }
    /* corners that coincide are one; a corner on a straight side is none */
    var q=[],P0,P1;
    for(i=0;i<poly.length;i++){
      P0=poly[i];P1=q.length?q[q.length-1]:null;
      if(P1&&Math.abs(P0.p[0]-P1.p[0])<1e-9&&Math.abs(P0.p[1]-P1.p[1])<1e-9){P1.t=[P1.t[0],P0.t[1]];continue;}
      q.push({p:P0.p,t:P0.t.slice()});
    }
    if(q.length>1){P0=q[0];P1=q[q.length-1];if(Math.abs(P0.p[0]-P1.p[0])<1e-9&&Math.abs(P0.p[1]-P1.p[1])<1e-9){P0.t=[P1.t[0],P0.t[1]];q.pop();}}
    q=q.filter(function(c){return c.t[0]!==c.t[1];});
    if(q.length<3||Math.abs(bimZnArea2(q))<1e-9)return [];
    return q;
  }
  function bimZnArea2(q){var a=0,i,n=q.length;for(i=0;i<n;i++){var p=q[i].p,r=q[(i+1)%n].p;a+=p[0]*r[1]-r[0]*p[1];}return a/2;}
  /* a lot that is not convex: each side's line moved in, neighbours meeting where the lines cross;
     a side squeezed out is dropped. null when what is left crosses itself (the lot splits). */
  function bimZnOffset(C,sb){
    var L=C.legs.legs,n=L.length,idx=[],LN=[],i,guard=0;
    for(i=0;i<n;i++){idx.push(i);LN.push({p:[L[i].a[0]+L[i].n[0]*sb[i],L[i].a[1]+L[i].n[1]*sb[i]],d:L[i].d});}
    function meet(A,B){var den=A.d[0]*B.d[1]-A.d[1]*B.d[0];if(Math.abs(den)<1e-12)return [B.p[0],B.p[1]];var tt=((B.p[0]-A.p[0])*B.d[1]-(B.p[1]-A.p[1])*B.d[0])/den;return [A.p[0]+A.d[0]*tt,A.p[1]+A.d[1]*tt];}
    while(guard++<n+2){
      var m=idx.length,pts=[],w=-1,wv=-1e-9;
      if(m<3)return [];
      for(i=0;i<m;i++)pts.push(meet(LN[idx[(i+m-1)%m]],LN[idx[i]]));
      for(i=0;i<m;i++){var A=pts[i],B=pts[(i+1)%m],D=LN[idx[i]].d,pr=(B[0]-A[0])*D[0]+(B[1]-A[1])*D[1];if(pr<wv){wv=pr;w=i;}}
      if(w>=0){idx.splice(w,1);continue;}
      var sa=0;for(i=0;i<m;i++)sa+=pts[i][0]*pts[(i+1)%m][1]-pts[(i+1)%m][0]*pts[i][1];
      if(!(Math.abs(sa)>1e-9)||(sa>0?1:-1)!==C.legs.sgn)return [];
      if(bimZnSelfCross(pts))return null;
      var out=[];for(i=0;i<m;i++)out.push({p:pts[i],t:[idx[(i+m-1)%m],idx[i]]});
      return out;
    }
    return [];
  }
  function bimZnSelfCross(P){
    var n=P.length,i,j;
    function cr(a,b,c){return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);}
    for(i=0;i<n;i++)for(j=i+2;j<n;j++){
      if(i===0&&j===n-1)continue;
      var a=P[i],b=P[(i+1)%n],c=P[j],d=P[(j+1)%n];
      if(cr(a,b,c)*cr(a,b,d)<-1e-12&&cr(c,d,a)*cr(c,d,b)<-1e-12)return true;
    }
    return false;
  }
  function bimZnArea(C,h,side){
    var p=bimZnPlate(C,h,side);
    if(p===null){if(C.split===null||h<C.split)C.split=h;return 0;}
    return p.length?Math.abs(bimZnArea2(p)):0;
  }
  function bimZnSig(C,h,side){var p=bimZnPlate(C,h,side);return p?p.map(function(c){return c.t[0]+'-'+c.t[1];}).sort().join(','):'x';}
  /* the area under a stretch of plates: Simpson's rule, halved until the halves agree (exact on a
     piece, where the area is a quadratic in the height) */
  function bimZnSimpson(C,a,b){
    var fa=bimZnArea(C,a,1),fb=bimZnArea(C,b,-1),fm=bimZnArea(C,(a+b)/2,0);
    function rec(x0,x1,f0,fm2,f1,whole,depth){
      var m=(x0+x1)/2,l=(x0+m)/2,r=(m+x1)/2,fl=bimZnArea(C,l,0),fr=bimZnArea(C,r,0),sl=(m-x0)/6*(f0+4*fl+fm2),sr=(x1-m)/6*(fm2+4*fr+f1);
      if(depth>18||Math.abs(sl+sr-whole)<=1e-10*Math.max(1,Math.abs(whole)))return sl+sr;
      return rec(x0,m,f0,fl,fm2,sl,depth+1)+rec(m,x1,fm2,fr,f1,sr,depth+1);
    }
    return rec(a,b,fa,fm,fb,(b-a)/6*(fa+4*fm+fb),0);
  }
  /* the whole working: rules, plates, pieces, volume, plates by storey, yield, the design against it */
  function bimZnCalc(){
    var P=bimZnProperty(),z=bimZn(),i,k;
    if(!P)return {error:'No property line yet: make one (Site analysis, Define)'};
    var G=bimZnLegs(P,z.frontLeg,z.legRoles);
    var C={legs:G,zoning:z,rules:bimZnRules(z),convex:bimZnConvex(G.ring),split:null};
    var maxH=z.maxH!==null?z.maxH:(z.maxStoreys?z.maxStoreys*z.f2f:null);
    C.maxH=maxH;
    if(maxH===null&&!(C.rules.front.plane||C.rules.side.plane||C.rules.rear.plane))return {error:'Give a height limit (or storeys, or an angular plane)',legs:G};
    if(!(bimZnArea(C,0,1)>1e-6))return {error:'The setbacks leave no buildable area',legs:G};
    /* the top: the height limit, or lower where the plate closes */
    var top;
    if(maxH!==null&&bimZnArea(C,maxH,-1)>1e-6)top=maxH;
    else{
      var lo=0,hi=maxH!==null?maxH:10;
      if(maxH===null){while(bimZnArea(C,hi,-1)>1e-6&&hi<4000)hi*=2;if(hi>=4000)return {error:'The envelope has no top: give a height limit',legs:G};}
      for(i=0;i<60;i++){var md=(lo+hi)/2;if(bimZnArea(C,md,-1)>1e-6)lo=md;else hi=md;}
      top=lo;
    }
    /* where the setbacks would split the lot, the envelope stops a millimetre short: its roof is then
       still one ring, not two that touch */
    if(C.split!==null&&top>C.split-0.001)top=Math.max(0,C.split-0.001);
    C.top=top;
    /* where a rule changes; then, between those, where a corner comes or goes */
    var Z=[0,top];
    BIM_ZN_ROLES.forEach(function(r){bimZnRuleBreaks(C.rules[r]).forEach(function(b){if(b>1e-6&&b<top-1e-6)Z.push(b);});});
    Z.sort(function(x,y){return x-y;});
    Z=Z.filter(function(v,j){return !j||v-Z[j-1]>1e-7;});
    var pieces=[];
    for(i=0;i+1<Z.length;i++){
      var a=Z[i],b=Z[i+1],u=a,su=bimZnSig(C,a+(b-a)*1e-6,0),last=a,N=8;
      for(k=1;k<=N;k++){
        var zz=k<N?a+(b-a)*k/N:b-(b-a)*1e-6,s2=bimZnSig(C,zz,0),it,l2,h2,ev=0;
        while(s2!==su&&ev++<64){
          l2=last;h2=zz;
          for(it=0;it<44;it++){var mz=(l2+h2)/2;if(bimZnSig(C,mz,0)===su)l2=mz;else h2=mz;}
          if(l2-u>1e-7)pieces.push([u,l2]);
          u=h2;last=h2;su=bimZnSig(C,h2,0);
          if(zz-h2<1e-9)break;
        }
        last=zz;
      }
      if(b-u>1e-7)pieces.push([u,b]);
    }
    /* every piece keeps its corners from its bottom to its top: one that does not is halved */
    var okP=[],queue=pieces.slice(),g2=0;
    while(queue.length&&g2++<400){
      var pc=queue.shift(),pu=pc[0],pw=pc[1],dd=Math.min(1e-6,(pw-pu)/4),Bq=bimZnRing(C,pu+dd,0,null);
      if(!Bq||pw-pu<1e-6||bimZnRing(C,pw-dd,0,Bq)){okP.push(pc);continue;}
      var pm=(pu+pw)/2;queue.unshift([pm,pw]);queue.unshift([pu,pm]);
    }
    pieces=okP.concat(queue).sort(function(x,y){return x[0]-y[0];});
    C.Z=Z;C.pieces=pieces;
    var vol=0;pieces.forEach(function(pc){vol+=bimZnSimpson(C,pc[0],pc[1]);});
    C.volume=vol;
    /* the floors: each storey's plate where it is tightest, at its ceiling; at most the coverage limit */
    var nSt=Math.floor(top/z.f2f+1e-9);if(z.maxStoreys)nSt=Math.min(nSt,z.maxStoreys);
    var covA=z.cover!==null?z.cover/100*G.area:Infinity,plates=[],cap=0;
    for(i=0;i<nSt;i++){var pa=Math.min(covA,bimZnArea(C,(i+1)*z.f2f,-1));if(pa<0.01)break;plates.push(Math.round(pa*100)/100);cap+=pa;}
    var farGFA=z.far!==null?z.far*G.area:null,ach=farGFA!==null?Math.min(farGFA,cap):cap,gov=farGFA===null?'envelope':(farGFA<=cap+1e-6?'FAR':'envelope');
    var used=0,acc=0;for(i=0;i<plates.length&&acc<ach-1e-6;i++){acc+=plates[i];used++;}
    var nsa=ach*z.eff/100,resN=nsa*z.res/100,units=Math.floor(resN/z.unit+1e-9),non=ach*(100-z.res)/100;
    var Lf=G.legs[G.front],lotD=-Infinity;
    G.ring.forEach(function(p){var d=(p[0]-Lf.a[0])*Lf.n[0]+(p[1]-Lf.a[1])*Lf.n[1];if(d>lotD)lotD=d;});
    var fp=bimZnPlate(C,0,1)||[];
    C.fp=fp.map(function(c){return c.p;});C.fpArea=Math.abs(bimZnArea2(fp));C.lot=G.area;C.lotD=lotD;C.hTop=top;
    C.plates=plates;C.capacity=cap;C.farGFA=farGFA;C.achievable=ach;C.governs=gov;C.storeysUsed=used;C.nsa=nsa;C.units=units;C.nonRes=non;
    C.parking=Math.ceil(units*z.park+non/100*z.parkNon-1e-9);
    C.ok=true;
    C.proposed=bimZnProposed(C);
    return C;
  }
  /* is this point, at this height above the lot, inside the envelope? A centimetre's tolerance;
     at and below the ground the envelope does not apply (a basement, its roof, paving) */
  function bimZnAllows(C,p,y){
    if(y<=0.05)return true;
    if(y>C.top+0.01)return false;
    var h=Math.max(0,y-0.01),key=h.toFixed(3),pl;
    C.cache=C.cache||{};
    pl=C.cache[key];
    if(pl===undefined){var q=bimZnPlate(C,h,-1);pl=C.cache[key]=q?q.map(function(c){return c.p;}):[];}
    if(pl.length<3)return false;
    if(bimPointInPoly(p,pl))return true;
    var k;for(k=0;k<pl.length;k++){var A=pl[k],B=pl[(k+1)%pl.length];if(bimPointSegDist(p[0],p[1],A[0],A[1],B[0],B[1])<1e-3)return true;}
    return false;
  }
  /* the design against it: GFA (usages), height, ground coverage, every element outside the envelope */
  function bimZnProposed(C){
    var out=[],hmax=null,i,j,o,m,q,v,s=bimUsageSummary(null),gfa=s.total.GFA>0?s.total.GFA:null,cov=null,base=[],y0=C.legs.y0;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(o.context||o.envelope)continue;
      var ut=o.usage?bimUsageTarget(o):'';
      if(!((o.t==='solid'&&o.bim&&BIM_SETBACK_TYPES[o.bim.type])||ut==='mass'||ut==='floor'))continue;
      m=meshOf(o);if(!m||!m.v||!m.v.length)continue;
      q=bimObjOffset(o);var bad=false,lo=Infinity;
      for(j=0;j<m.v.length;j++){
        v=m.v[j];var p=[v[0]+q[0],v[2]+q[2]],y=v[1]+q[1]-y0;
        if(hmax===null||y>hmax)hmax=y;
        if(y<lo)lo=y;
        if(!bad&&!bimZnAllows(C,p,y))bad=true;
      }
      if(bad)out.push({id:o.id,name:o.name});
      if((ut==='mass'||ut==='floor')&&lo>-0.5)base.push({a:bimUsageMeasure(o).footprint,y:lo});   /* a basement covers no ground */
    }
    /* coverage: the footprints of the usages that stand on the lowest ground, at or above the lot */
    if(base.length){
      var yl=Infinity;base.forEach(function(b){if(b.y<yl)yl=b.y;});
      cov=0;base.forEach(function(b){if(b.y<=yl+0.5)cov+=b.a;});
    }
    return {gfa:gfa,height:hmax!==null?Math.round(hmax*100)/100:null,coverArea:cov,outside:out};
  }
  /* ---- the envelope as one translucent solid, made of whole faces: per piece, a side face for
     each side, a terrace where the plate steps in, a roof ---- */
  function bimZnRing(C,h,side,ref){
    var q=bimZnPlate(C,h,side);if(!q||q.length<3)return null;
    if(bimZnArea2(q)<0)q=q.slice().reverse().map(function(c){return {p:c.p,t:[c.t[1],c.t[0]]};});
    if(!ref)return q;
    /* matched to ref's corners by their sides */
    var by={},i,out=[];q.forEach(function(c){by[c.t[0]+'-'+c.t[1]]=c;});
    for(i=0;i<ref.length;i++){var c2=by[ref[i].t[0]+'-'+ref[i].t[1]];if(!c2)return null;out.push(c2);}
    return out.length===q.length?out:null;
  }
  function bimZnMesh(C){
    var v=[],f=[],y0=C.legs.y0,prev=null,i,j;
    function addRing(R,h){var b=v.length;R.forEach(function(c){v.push([c.p[0],y0+h,c.p[1]]);});return b;}
    /* a face: repeated corners dropped, and none at all when it has no area (Newell's normal) */
    function face(F){
      var G=[],k,a,b;
      for(k=0;k<F.length;k++){a=v[F[k]];b=G.length?v[G[G.length-1]]:null;if(b&&Math.abs(a[0]-b[0])+Math.abs(a[1]-b[1])+Math.abs(a[2]-b[2])<1e-7)continue;G.push(F[k]);}
      while(G.length>1){a=v[G[0]];b=v[G[G.length-1]];if(Math.abs(a[0]-b[0])+Math.abs(a[1]-b[1])+Math.abs(a[2]-b[2])<1e-7)G.pop();else break;}
      if(G.length<3)return;
      var nx=0,ny=0,nz=0;
      for(k=0;k<G.length;k++){a=v[G[k]];b=v[G[(k+1)%G.length]];nx+=(a[1]-b[1])*(a[2]+b[2]);ny+=(a[2]-b[2])*(a[0]+b[0]);nz+=(a[0]-b[0])*(a[1]+b[1]);}
      if(Math.sqrt(nx*nx+ny*ny+nz*nz)<1e-8)return;
      f.push(G);
    }
    /* a roof or a floor: one face when it is convex, else cut into convex parts (a face is drawn as a fan) */
    function cap(b,R,up){
      bimZnConvexParts(R.map(function(c){return c.p;})).forEach(function(part){
        var F=part.map(function(k){return b+k;});
        face(up?F.reverse():F);   /* a ring that turns positive faces down */
      });
    }
    for(i=0;i<C.pieces.length;i++){
      var u=C.pieces[i][0],w=C.pieces[i][1],Bt=bimZnRingEnd(C,u,w,false,null);if(!Bt)continue;
      var Tp=bimZnRingEnd(C,u,w,true,Bt)||Bt,n=Bt.length;
      if(!prev)cap(addRing(Bt,u),Bt,false);
      else{
        var M=bimZnRingEnd(C,u,w,false,prev.R);
        if(M&&bimZnSameRing(prev.R,M)){}   /* the plate carries on */
        else if(M){
          /* the plate steps in: a terrace, one face for each side that moved */
          var tb=addRing(M,u),m=M.length;
          for(j=0;j<m;j++){var j2=(j+1)%m;face([tb+j,tb+j2,prev.b+j2,prev.b+j]);}
        }
        else if(bimZnSamePoly(prev.R,Bt)){}   /* the same outline with a corner more or less */
        else{cap(prev.b,prev.R,true);cap(addRing(Bt,u),Bt,false);}   /* both closed: never the open side */
      }
      var bb=addRing(Bt,u),bt=addRing(Tp,w);
      for(j=0;j<n;j++){var k2=(j+1)%n;face([bb+k2,bb+j,bt+j,bt+k2]);}
      prev={R:Tp,b:bt};
    }
    if(prev)cap(prev.b,prev.R,true);
    return {v:v,f:f};
  }
  /* a piece's ring at its bottom or top, exactly: read just inside, where its corners are its own,
     and carried to the end along their straight paths */
  function bimZnRingEnd(C,u,w,atTop,ref){
    var d=Math.min(1e-4,(w-u)/8),R1=bimZnRing(C,atTop?w-d:u+d,0,ref),R2;
    if(!R1)return null;
    R2=bimZnRing(C,atTop?w-2*d:u+2*d,0,R1);
    if(!R2)return R1;
    return R1.map(function(c,k){var q=R2[k].p;return {p:[2*c.p[0]-q[0],2*c.p[1]-q[1]],t:c.t};});
  }
  function bimZnSameRing(A,B){
    if(A.length!==B.length)return false;
    var i;for(i=0;i<A.length;i++)if(Math.abs(A[i].p[0]-B[i].p[0])+Math.abs(A[i].p[1]-B[i].p[1])>1e-6)return false;
    return true;
  }
  /* two rings with the same corners, once corners that coincide are one */
  function bimZnSamePoly(A,B){
    function pts(R){var o=[];R.forEach(function(c){var l=o.length?o[o.length-1]:null;if(!l||Math.abs(l[0]-c.p[0])+Math.abs(l[1]-c.p[1])>1e-6)o.push(c.p);});
      if(o.length>1&&Math.abs(o[0][0]-o[o.length-1][0])+Math.abs(o[0][1]-o[o.length-1][1])<=1e-6)o.pop();return o;}
    var P=pts(A),Q=pts(B);
    if(P.length!==Q.length)return false;
    return P.every(function(p){return Q.some(function(q){return Math.abs(p[0]-q[0])+Math.abs(p[1]-q[1])<=1e-6;});});
  }
  /* a polygon (turning positive) as convex parts: ears clipped, then neighbours merged while the
     union stays convex (Hertel and Mehlhorn) */
  function bimZnConvexParts(P){
    var n=P.length,i;
    function cr(a,b,c){return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);}
    function convex(Q){var m=Q.length,k;for(k=0;k<m;k++)if(cr(P[Q[k]],P[Q[(k+1)%m]],P[Q[(k+2)%m]])<-1e-9)return false;return true;}
    var all=[];for(i=0;i<n;i++)all.push(i);
    if(convex(all))return [all];
    var parts=earClip(P.slice()).map(function(t2){return t2.slice();}),merged=true,want=0,got=0;
    for(i=0;i<n;i++)want+=P[i][0]*P[(i+1)%n][1]-P[(i+1)%n][0]*P[i][1];
    parts.forEach(function(t2){got+=cr(P[t2[0]],P[t2[1]],P[t2[2]]);});
    if(Math.abs(got-want)>1e-6*Math.max(1,Math.abs(want)))return [all];   /* the ears missed some: one face, never a hole */
    while(merged){
      merged=false;
      for(i=0;i<parts.length&&!merged;i++)for(var j2=i+1;j2<parts.length&&!merged;j2++){
        var A=parts[i],B=parts[j2],a,b2;
        for(a=0;a<A.length&&!merged;a++){
          var p=A[a],q=A[(a+1)%A.length];
          for(b2=0;b2<B.length;b2++)if(B[b2]===q&&B[(b2+1)%B.length]===p){
            var U=[],k;
            for(k=0;k<A.length;k++)U.push(A[(a+1+k)%A.length]);   /* q ... p */
            for(k=2;k<B.length;k++)U.push(B[(b2+k)%B.length]);   /* after p, up to before q */
            if(convex(U)){parts[i]=U;parts.splice(j2,1);merged=true;}
            break;
          }
        }
      }
    }
    return parts;
  }
  function bimZnEnvelopeObj(){var i;for(i=0;i<A3D.objs.length;i++)if(A3D.objs[i].envelope)return A3D.objs[i];return null;}
  function bimZnLayer(){
    var ly=bimLayerByName('Zoning envelope');
    if(!ly){ly=bimLayerNew({name:'Zoning envelope',color:'#e0b85e'});if(ly)ly.transparency=70;}
    return ly;
  }
  /* placed in the caller's undo step */
  function bimZnPlaceEnvelope(quiet){
    var C=bimZnCalc();
    A3D.objs=A3D.objs.filter(function(o){return !o.envelope;});
    if(!C.ok){if(!quiet)a3dToast('No envelope: '+C.error);return C;}
    var ly=bimZnLayer(),z=C.zoning;
    A3D.objs.push({id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:'Zoning envelope'+(z.district?' ('+z.district+')':''),pos:[0,0,0],
      mesh:bimZnMesh(C),col:'#e0b85e',locked:true,layer:ly?ly.id:A3D.activeLayer,
      envelope:{district:z.district,volume:Math.round(C.volume),capacity:Math.round(C.capacity),built:bimSaToday()}});
    return C;
  }
  /* ENVELOPE: built, or built again, and the findings with it; one undo step */
  function bimZnBuild(){
    var C0=bimZnCalc();
    if(!C0.ok){a3dToast('No envelope: '+C0.error);return C0;}
    pushUndo();
    undoSuspend=true;var C;
    try{C=bimZnPlaceEnvelope(false);bimSaFill(true);}finally{undoSuspend=false;}
    bimZnDone();
    var pr=C.proposed;
    a3dToast('Zoning envelope: '+bimClimInt(C.volume)+' m³, room for '+bimClimInt(C.capacity)+' m² over '+C.plates.length+' storeys; '+
      (C.governs==='FAR'?'the FAR governs at '+bimClimInt(C.achievable)+' m²':'the envelope governs')+(pr.outside.length?'. '+pr.outside.length+' element'+(pr.outside.length===1?'':'s')+' outside it':''));
    return C;
  }
  function bimZnRemoveEnvelope(){
    if(!bimZnEnvelopeObj())return false;
    pushUndo();A3D.objs=A3D.objs.filter(function(o){return !o.envelope;});bimZnDone();return true;
  }
  /* ---- council layers under the lot: the district, and the FAR and height where a layer has them ----
     Names as published: NYC MapPLUTO (ZoneDist1, ResidFAR, CommFAR, FacilFAR), NSW's planning
     layers (an FSR, a building height), and the usual zone, FAR and height names elsewhere. */
  var BIM_ZN_ATTR={
    district:/^(zone|zoning|zonedist1?|zone_?dist(rict)?|zone_?code|zoning_?code|zoning_?district|district|zone_?class|zoneclass|zone_?type|zone_?name)$/i,
    far:/^(fsr|far|floor_?space_?ratio|floor_?area_?ratio|max_?far|max_?fsr|far_?max|fsr_?max|residfar|commfar|facilfar)$/i,
    height:/^(max_?b_?h|hob|height|max_?height|height_?max|max_?hgt|height_?lim(it)?|max_?bldg_?h(eigh)?t?|bldg_?ht_?max|height_?ft|max_?height_?ft|height_?m)$/i};
  function bimZnNum(v){var x=parseFloat(String(v==null?'':v).replace(/,/g,''));return isFinite(x)&&x>0?x:null;}
  function bimZnFromLayer(apply){
    var P=bimZnProperty();if(!P)return null;
    var g=bimPropertyGeometry(P),c=bimZnCentroid(g.ring),z=bimZn(),found={};
    bimDataList().forEach(function(L){
      var M=bimDataModel(L),F=bimDataFeats(L.id);if(!M)return;
      M.feats.forEach(function(f){
        if(!f.rings.length)return;
        var inside=false;f.rings.forEach(function(r){if(bimPointInPoly(c,r.pts))inside=!inside;});
        if(!inside)return;
        var pr=(F[f.fi]&&F[f.fi].p)||{},k,src=function(attr){return {layer:L.name,credit:L.credit||'',attr:attr};};
        if(!found.district){
          for(k in pr)if(pr.hasOwnProperty(k)&&BIM_ZN_ATTR.district.test(k)&&String(pr[k]).length&&!bimZnNum(pr[k])){found.district=src(k);found.district.value=String(pr[k]).slice(0,40);break;}
          if(!found.district)for(k in pr)if(pr.hasOwnProperty(k)&&/zon/i.test(k)&&!/far|fsr|height/i.test(k)&&String(pr[k]).length&&!bimZnNum(pr[k])){found.district=src(k);found.district.value=String(pr[k]).slice(0,40);break;}
        }
        if(!found.far){
          var fk=[];for(k in pr)if(pr.hasOwnProperty(k)&&BIM_ZN_ATTR.far.test(k)&&bimZnNum(pr[k])!==null)fk.push(k);
          /* MapPLUTO: the residential FAR for a mostly residential scheme, else the commercial */
          fk.sort(function(x,y){function w(s){s=s.toLowerCase();return s==='residfar'?(z.res>=50?0:2):s==='commfar'?(z.res>=50?2:0):s==='facilfar'?3:1;}return w(x)-w(y);});
          if(fk.length){found.far=src(fk[0]);found.far.value=Math.min(50,bimZnNum(pr[fk[0]]));}
        }
        if(!found.height){
          for(k in pr)if(pr.hasOwnProperty(k)&&BIM_ZN_ATTR.height.test(k)&&bimZnNum(pr[k])!==null){
            var hv=bimZnNum(pr[k]),ft=/ft|feet/i.test(k)||/^(ft|feet|foot)$/i.test(String(pr.UNITS||pr.units||pr.Units||''));
            found.height=src(k);found.height.value=Math.min(1000,Math.round((ft?hv*0.3048:hv)*100)/100);found.height.feet=ft;break;
          }
        }
      });
    });
    if(!found.district&&!found.far&&!found.height)return null;
    if(!apply)return found;
    var parts=[];
    ['district','far','height'].forEach(function(k2){var f=found[k2];if(f)parts.push(f.layer+(f.credit?' ('+f.credit+')':'')+', '+f.attr);});
    return bimZnEdit(function(){
      if(found.district)z.district=found.district.value;
      if(found.far)z.far=found.far.value;
      if(found.height)z.maxH=found.height.value;
      z.source=parts.join('; ').slice(0,200);
      a3dToast('From the layers: '+bimZnFoundText(found));
    })&&found;
  }
  function bimZnFoundText(f){
    var p=[];
    if(f.district)p.push(f.district.value);
    if(f.far)p.push('FAR '+f.far.value);
    if(f.height)p.push(bimClimFmt(f.height.value)+' m'+(f.height.feet?' (from feet)':''));
    return p.join(' · ');
  }
  /* ---- in words ---- */
  function bimZnRuleText(C,role){
    var o=C.rules[role],p=[bimClimFmt(o.base)+' m'];
    o.steps.forEach(function(s){p.push(bimClimFmt(s[1])+' m above '+bimClimFmt(s[0])+' m');});
    if(o.plane)p.push((role==='front'?'sky plane ':'angular plane ')+bimClimFmt(o.plane[1],1)+':1 from '+bimClimFmt(o.plane[0])+' m');
    return p.join('; ');
  }
  /* ---- the findings ---- */
  function bimZnAuto(){
    if(!bimZnHas())return [];
    var z=bimZn(),A=[],src=z.source||'Entered by hand',dt=bimSaToday(),C=bimZnCalc();
    var parts=[];
    if(z.far!==null)parts.push('FAR '+z.far);
    if(z.maxH!==null)parts.push('height '+bimClimFmt(z.maxH)+' m');
    if(z.maxStoreys)parts.push(z.maxStoreys+' storeys');
    if(z.cover!==null)parts.push('coverage '+bimClimFmt(z.cover,0)+'%');
    if(C.ok)BIM_ZN_ROLES.forEach(function(r){if(C.legs.legs.some(function(l){return l.role===r;}))parts.push(r+' '+bimZnRuleText(C,r));});
    else parts.push('setbacks '+[z.front,z.side,z.rear].map(function(x){return bimClimFmt(x);}).join(' / ')+' m (front / side / rear)');
    A.push({auto:'legal.zoning',cat:'legal',title:'Zoning',value:(z.district?z.district+': ':'')+parts.join(', ')+(z.uses?'. Uses: '+z.uses:''),source:src,date:dt});
    if(!C.ok)return A;
    A.push({auto:'legal.envelope',cat:'legal',title:'Zoning envelope',value:bimClimInt(C.volume)+' m³ up to '+bimClimFmt(C.top)+' m; room for '+bimClimInt(C.capacity)+' m² GFA over '+C.plates.length+' storeys of '+bimClimFmt(z.f2f)+' m; '+
      (C.governs==='FAR'?'the FAR governs: '+bimClimInt(C.achievable)+' m²':'the envelope governs: '+bimClimInt(C.achievable)+' m²'),cls:'opportunity',source:src+'; worked out in the app',date:dt});
    A.push({auto:'legal.yield',cat:'legal',title:'Yield',value:bimClimInt(C.achievable)+' m² GFA, '+bimClimInt(C.nsa)+' m² net at '+bimClimFmt(z.eff,0)+'%: '+C.units+' unit'+(C.units===1?'':'s')+' of '+bimClimFmt(z.unit,0)+' m²; '+
      C.parking+' parking space'+(C.parking===1?'':'s')+' required',cls:'opportunity',source:'Assumptions in the zoning record',date:dt});
    var pr=C.proposed,iss=[],gfaOver=pr.gfa!==null&&C.farGFA!==null&&pr.gfa>C.farGFA+0.5,hOver=pr.height!==null&&C.maxH!==null&&pr.height>C.maxH+0.01;
    if(gfaOver)iss.push('GFA '+bimClimInt(pr.gfa)+' m² is over the FAR limit by '+bimClimInt(pr.gfa-C.farGFA)+' m²');
    if(hOver)iss.push('height '+bimClimFmt(pr.height)+' m is over the limit of '+bimClimFmt(C.maxH)+' m');
    if(pr.coverArea!==null&&z.cover!==null&&pr.coverArea>z.cover/100*C.lot+0.5)iss.push('coverage '+bimClimFmt(100*pr.coverArea/C.lot,0)+'% is over '+bimClimFmt(z.cover,0)+'%');
    if(pr.outside.length)iss.push(pr.outside.length+' element'+(pr.outside.length===1?'':'s')+' outside the envelope');
    if(iss.length)A.push({auto:'legal.compliance',cat:'legal',title:'Design against the zoning',value:iss.join('; '),cls:gfaOver||hOver?'redflag':'constraint',sev:3,source:'The model against the zoning record',date:dt});
    return A;
  }

  /* ---- __acad3dV160: the Zoning and yield board ---- */
  var BIM_ZN_ROLECOL={front:'var(--s1)',side:'var(--s2)',rear:'var(--s3)'};
  var BIM_ZN_ROLENAME={front:'Front',side:'Side',rear:'Rear'};
  function bimZnM(v,d){return bimClbNum(v,d===undefined?1:d)+' m';}
  /* a dimension: a thin line with ticks, its value beside it; the words go first when it is tight */
  function bimZnDimH(x1,x2,y,txt,below){
    if(Math.abs(x2-x1)<2)return '';
    if(String(txt).length*6.2>Math.abs(x2-x1)-4)txt=String(txt).replace(/^[A-Za-z ]+ (?=[\d−])/,'');
    var s='<path d="M'+bimClbF(x1)+' '+bimClbF(y)+'H'+bimClbF(x2)+'M'+bimClbF(x1)+' '+bimClbF(y-4)+'v8M'+bimClbF(x2)+' '+bimClbF(y-4)+'v8" stroke="var(--ink2)" stroke-width="1" fill="none"/>';
    return s+'<text class="tl2" x="'+bimClbF((x1+x2)/2)+'" y="'+bimClbF(below?y+13:y-5)+'" text-anchor="middle">'+bimClbE(txt)+'</text>';
  }
  function bimZnDimV(x,y1,y2,txt,left){
    if(Math.abs(y2-y1)<2)return '';
    var s='<path d="M'+bimClbF(x)+' '+bimClbF(y1)+'V'+bimClbF(y2)+'M'+bimClbF(x-4)+' '+bimClbF(y1)+'h8M'+bimClbF(x-4)+' '+bimClbF(y2)+'h8" stroke="var(--ink2)" stroke-width="1" fill="none"/>';
    return s+'<text class="tl2" x="'+bimClbF(left?x-6:x+6)+'" y="'+bimClbF((y1+y2)/2+4)+'" text-anchor="'+(left?'end':'start')+'">'+bimClbE(txt)+'</text>';
  }
  /* a scale bar of a round length, at most maxW wide */
  function bimZnScaleBar(x,y,k,maxW){
    var L=[1,2,5,10,20,25,50,100,200,500,1000],m=L[0],i;
    for(i=0;i<L.length;i++)if(L[i]*k<=maxW)m=L[i];
    var w=m*k,h=5;
    return '<g aria-hidden="true"><rect x="'+bimClbF(x)+'" y="'+y+'" width="'+bimClbF(w/2)+'" height="'+h+'" fill="var(--ink2)"/><rect x="'+bimClbF(x+w/2)+'" y="'+y+'" width="'+bimClbF(w/2)+'" height="'+h+'" fill="none" stroke="var(--ink2)" stroke-width="1"/>'+
      '<text class="tk" x="'+bimClbF(x)+'" y="'+(y+h+12)+'">0</text><text class="tk" x="'+bimClbF(x+w)+'" y="'+(y+h+12)+'" text-anchor="middle">'+m+' m</text></g>';
  }
  /* ---- sections: the envelope cut along a line through the footprint's centre, square to the
     front (A) or along it (B); distances along the line from the front's first corner ---- */
  function bimZnAxis(C,kind){
    var G=C.legs,Lf=G.legs[G.front];
    return {o:Lf.a,dir:kind==='B'?Lf.d:Lf.n,c:bimZnCentroid(C.fp.length>=3?C.fp:G.ring),kind:kind};
  }
  function bimZnChordOf(pts,ax){
    var nr=[-ax.dir[1],ax.dir[0]],T=[],i,n=pts.length,c=ax.c;
    for(i=0;i<n;i++){
      var p=pts[i],q=pts[(i+1)%n],sp=(p[0]-c[0])*nr[0]+(p[1]-c[1])*nr[1],sq=(q[0]-c[0])*nr[0]+(q[1]-c[1])*nr[1];
      if(sp*sq>0||Math.abs(sp-sq)<1e-12)continue;
      var u=sp/(sp-sq),x=[p[0]+(q[0]-p[0])*u,p[1]+(q[1]-p[1])*u];
      T.push({v:(x[0]-ax.o[0])*ax.dir[0]+(x[1]-ax.o[1])*ax.dir[1],e:i});
    }
    if(T.length<2)return null;
    T.sort(function(a,b){return a.v-b.v;});
    return {a:T[0].v,b:T[T.length-1].v,ea:T[0].e,eb:T[T.length-1].e};
  }
  function bimZnChordAt(C,ax,h,side){var q=bimZnPlate(C,h,side);return q&&q.length>=3?bimZnChordOf(q.map(function(c){return c.p;}),ax):null;}
  function bimZnSection(C,kind){
    var ax=bimZnAxis(C,kind),L=[],R=[],lot=bimZnChordOf(C.legs.ring,ax);
    C.pieces.forEach(function(pc){
      var u=pc[0],w=pc[1],k,N=6;
      for(k=0;k<=N;k++){var h=u+(w-u)*k/N,ch=bimZnChordAt(C,ax,h,k===0?1:(k===N?-1:0));if(ch){L.push([ch.a,h]);R.push([ch.b,h]);}}
    });
    return {ax:ax,lot:lot,L:L,R:R};
  }
  /* along the line, how far a setback of s from a side reaches (s itself when the line is square to it) */
  function bimZnAlong(C,ax,e,s){var l=C.legs.legs[e],c=Math.abs(ax.dir[0]*l.n[0]+ax.dir[1]*l.n[1]);return c>0.05?s/c:s;}
  function bimZnSectionSvg(C,kind){
    var z=C.zoning,nw=A3D_CLB.narrow,W=nw?360:560,Lm=nw?46:64,Rm=nw?16:84,T0=26,Bm=80,pr=C.proposed,S=bimZnSection(C,kind);
    if(!S.lot||!S.L.length)return '<p class="a3d-clb-empty">This lot has no section here.</p>';
    var la=S.lot.a,lb=S.lot.b,st=kind==='A'?Math.max(4,Math.min(12,(lb-la)*0.22)):Math.max(2,(lb-la)*0.05),d0=la-st,d1=lb+Math.max(2,(lb-la)*0.05);
    var top=Math.max(C.top,C.maxH||0,pr.height||0,1)*1.12;
    var k=(W-Lm-Rm)/(d1-d0),H=Math.round(T0+top*k+Bm),cap=nw?420:440;
    if(H>cap){k=(cap-T0-Bm)/top;H=cap;}
    var ox=Lm+((W-Lm-Rm)-(d1-d0)*k)/2,B=H-Bm;
    function X(d){return ox+(d-d0)*k;}function Y(h){return B-h*k;}
    var roleA=C.legs.legs[S.lot.ea].role,roleB=C.legs.legs[S.lot.eb].role;
    var s='<svg viewBox="0 0 '+W+' '+H+'" role="img" aria-label="Zoning envelope in section, '+(kind==='A'?'front to rear':'side to side')+', at true scale">';
    if(kind==='A'){
      s+='<rect x="'+bimClbF(X(d0))+'" y="'+bimClbF(B)+'" width="'+bimClbF(X(la)-X(d0))+'" height="6" fill="var(--band)"/>'+
        '<text class="tk" x="'+bimClbF((X(d0)+X(la))/2)+'" y="'+bimClbF(B+18)+'" text-anchor="middle">Street</text>';
    }
    s+='<line x1="'+bimClbF(X(d0))+'" x2="'+bimClbF(X(d1))+'" y1="'+bimClbF(B)+'" y2="'+bimClbF(B)+'" stroke="var(--ink2)" stroke-width="1.5"/>';
    [[la,BIM_ZN_ROLENAME[roleA]+' lot line',0],[lb,BIM_ZN_ROLENAME[roleB]+' lot line',1]].forEach(function(l){
      s+='<line x1="'+bimClbF(X(l[0]))+'" x2="'+bimClbF(X(l[0]))+'" y1="'+bimClbF(B+4)+'" y2="'+bimClbF(T0-8)+'" stroke="var(--muted)" stroke-width="1" stroke-dasharray="6 3 1.5 3"/>'+
        '<text class="tk" x="'+bimClbF(X(l[0])+(l[2]?-4:4))+'" y="'+(T0-12)+'" text-anchor="'+(l[2]?'end':'start')+'">'+l[1]+'</text>';
    });
    /* the envelope */
    var poly=S.L.concat(S.R.slice().reverse());
    s+='<polygon class="mk" points="'+poly.map(function(p){return bimClbF(X(p[0]))+','+bimClbF(Y(p[1]));}).join(' ')+'" fill="var(--s4)" fill-opacity=".16" stroke="var(--s4)" stroke-width="2" stroke-linejoin="round"'+
      bimClbTip('Zoning envelope|Up to '+bimZnM(C.top)+' high|'+bimZnM(S.L[0][0]-la)+' from the '+roleA+' lot line, '+bimZnM(lb-S.R[0][0])+' from the '+roleB+' at the ground|'+bimClimInt(C.volume)+' m³ in all')+'/>';
    /* the floors that fit */
    var i,nf=C.plates.length;
    for(i=1;i<=nf;i++){var ch=bimZnChordAt(C,S.ax,i*z.f2f,-1);if(ch)s+='<line x1="'+bimClbF(X(ch.a))+'" x2="'+bimClbF(X(ch.b))+'" y1="'+bimClbF(Y(i*z.f2f))+'" y2="'+bimClbF(Y(i*z.f2f))+'" stroke="var(--s4)" stroke-opacity="'+(i<=C.storeysUsed?'.55':'.25')+'" stroke-width="1"/>';}
    /* the height limit; each end's angular plane; the proposed height */
    if(C.maxH!==null)s+='<line x1="'+bimClbF(X(d0))+'" x2="'+bimClbF(X(d1))+'" y1="'+bimClbF(Y(C.maxH))+'" y2="'+bimClbF(Y(C.maxH))+'" stroke="var(--ink2)" stroke-width="1" stroke-dasharray="5 4"/>'+
      '<text class="tl2" x="'+bimClbF(X(d0))+'" y="'+bimClbF(Y(C.maxH)-5)+'">Height limit '+bimZnM(C.maxH)+'</text>';
    [[S.lot.ea,la,1,roleA],[S.lot.eb,lb,-1,roleB]].forEach(function(E){
      var o=C.rules[E[3]];if(!o.plane)return;
      var h0=o.plane[0],r=o.plane[1],sMax=(top-h0)/r;if(!(sMax>0))return;
      var span=Math.min(sMax,(lb-la)),xa=E[1],xb=E[1]+E[2]*bimZnAlong(C,S.ax,E[0],span),ya=h0,yb=h0+r*span;
      s+='<line x1="'+bimClbF(X(xa))+'" y1="'+bimClbF(Y(ya))+'" x2="'+bimClbF(X(xb))+'" y2="'+bimClbF(Y(yb))+'" stroke="'+BIM_ZN_ROLECOL[E[3]]+'" stroke-width="1.25" stroke-dasharray="7 4"/>'+
        '<text class="tl2" x="'+bimClbF(X(xa)+(E[2]>0?-4:4))+'" y="'+bimClbF(Y(ya)+4)+'" text-anchor="'+(E[2]>0?'end':'start')+'" style="fill:'+BIM_ZN_ROLECOL[E[3]]+'">'+bimClbNum(r,1)+':1</text>';   /* by its start, clear of the top */
    });
    if(pr.height!==null)s+='<line x1="'+bimClbF(X(S.L[0][0]))+'" x2="'+bimClbF(X(S.R[0][0]))+'" y1="'+bimClbF(Y(pr.height))+'" y2="'+bimClbF(Y(pr.height))+'" stroke="var(--s1)" stroke-width="2"'+bimClbTip('The design|Its highest point '+bimZnM(pr.height)+' above the lot')+'/>'+
      '<text class="lb" x="'+bimClbF((X(S.L[0][0])+X(S.R[0][0]))/2)+'" y="'+bimClbF(Y(pr.height)-6)+'" text-anchor="middle" style="fill:var(--s1)">Proposed '+bimZnM(pr.height)+'</text>';
    /* dimensions: the setbacks at the ground and each step across the bottom; each step's height up the side */
    var yd=B+32,yd2=B+48;
    function ends(E){
      var o=C.rules[E[3]],lot=E[1],dirn=E[2],out=[],prevS=0,nd=0;
      [[0,o.base]].concat(o.steps).forEach(function(stp,j){
        if(stp[1]<=prevS+1e-9&&j)return;
        var x1=lot+dirn*bimZnAlong(C,S.ax,E[0],prevS),x2=lot+dirn*bimZnAlong(C,S.ax,E[0],stp[1]);
        if(stp[1]>prevS+1e-9)out.push(bimZnDimH(X(Math.min(x1,x2)),X(Math.max(x1,x2)),yd,(j?(nw?'':'Step '):(nw?'':BIM_ZN_ROLENAME[E[3]]+' '))+bimZnM(stp[1]-prevS),!(nd++%2)));
        if(j&&stp[0]<C.top)out.push(bimZnDimV(X(x1)+(dirn>0?-(nw?10:14):(nw?10:14)),Y(0),Y(stp[0]),bimZnM(stp[0]),dirn>0));
        prevS=Math.max(prevS,stp[1]);
      });
      return out.join('');
    }
    s+=ends([S.lot.ea,la,1,roleA])+ends([S.lot.eb,lb,-1,roleB]);
    s+=bimZnDimH(X(la),X(lb),yd2,(kind==='A'?'Lot depth ':'Lot width ')+bimZnM(lb-la),true);
    s+=bimZnDimV(X(lb)+(nw?8:16),Y(0),Y(C.top),nw?bimZnM(C.top,0):'Envelope '+bimZnM(C.top),false);
    if(nf)s+='<text class="tk" x="'+bimClbF((X(S.L[0][0])+X(S.R[0][0]))/2)+'" y="'+bimClbF(Y(Math.min(z.f2f,C.top))+12)+'" text-anchor="middle">'+nf+' floor'+(nf===1?'':'s')+' of '+bimZnM(z.f2f)+'</text>';
    s+=bimZnScaleBar(nw?10:Lm,H-20,k,(W-Lm-Rm)/4);
    return s+'</svg>';
  }
  function bimZnPlaneLeg(C){var L=[];BIM_ZN_ROLES.forEach(function(r){if(C.rules[r].plane&&C.legs.legs.some(function(l){return l.role===r;}))L.push([BIM_ZN_ROLECOL[r],r==='front'?'Sky exposure plane':BIM_ZN_ROLENAME[r]+' angular plane','ln']);});return L;}
  /* Fig. 4: each kind of side's rule, the way Giraffe's envelope tool draws it: setback across,
     height up, steps and planes; the height limit dashed */
  function bimZnRoles(C){var R=[];BIM_ZN_ROLES.forEach(function(r){if(C.legs.legs.some(function(l){return l.role===r;}))R.push(r);});return R;}
  function bimZnRulePts(C,role){
    var o=C.rules[role],Z=[0,C.top],P=[];
    bimZnRuleBreaks(o).forEach(function(b){if(b>0&&b<C.top)Z.push(b);});
    Z.sort(function(a,b){return a-b;});
    Z.forEach(function(h,j){
      var sl=bimZnInset(o,h,-1),sr=bimZnInset(o,h,1);
      if(j)P.push([sl,h]);
      if(j<Z.length-1&&(!j||Math.abs(sr-sl)>1e-9||!P.length))P.push([sr,h]);
    });
    return P;
  }
  function bimZnRulesSvg(C){
    var nw=A3D_CLB.narrow,W=nw?360:420,H=nw?256:286,L=40,R=W-(nw?64:78),T0=24,B=H-34,roles=bimZnRoles(C),mx=1,lines=[];
    roles.forEach(function(r){var P=bimZnRulePts(C,r);lines.push([r,P]);P.forEach(function(p){if(p[0]>mx)mx=p[0];});});
    var Tx=bimClbTicks(0,mx*1.1,nw?3:4),x1=Tx[Tx.length-1],Ty=bimClbTicks(0,Math.max(C.top,C.maxH||0),4),y1=Ty[Ty.length-1];
    function x(v){return L+v/x1*(R-L);}function y(v){return B-v/y1*(B-T0);}
    var s='<svg viewBox="0 0 '+W+' '+H+'" role="img" aria-label="Setback against height, by kind of side">'+bimClbAxisY(Ty,y,L,R,function(v){return v;});
    Tx.forEach(function(v){s+='<text class="tk" x="'+bimClbF(x(v))+'" y="'+(B+14)+'" text-anchor="middle">'+v+'</text>';});
    s+='<line class="bs" x1="'+L+'" x2="'+R+'" y1="'+B+'" y2="'+B+'"/><text class="tk" x="'+R+'" y="'+(B+28)+'" text-anchor="end">Setback from the lot line, m</text><text class="tk" x="'+(L-34)+'" y="'+(T0-12)+'">Height, m</text>';
    if(C.maxH!==null)s+='<line x1="'+L+'" x2="'+R+'" y1="'+bimClbF(y(C.maxH))+'" y2="'+bimClbF(y(C.maxH))+'" stroke="var(--ink2)" stroke-width="1" stroke-dasharray="5 4"/>';
    var ends=[];
    lines.forEach(function(Ln,i){
      var r=Ln[0],P=Ln[1],off=(i-(lines.length-1)/2)*1.6;
      s+='<polyline points="'+P.map(function(p){return bimClbF(x(p[0])+off)+','+bimClbF(y(p[1]));}).join(' ')+'" fill="none" stroke="'+BIM_ZN_ROLECOL[r]+'" stroke-width="2" stroke-linejoin="round"/>';
      P.forEach(function(p,j){if(j&&j<P.length-1&&Math.abs(p[0]-P[j-1][0])>1e-9)s+='<circle cx="'+bimClbF(x(p[0])+off)+'" cy="'+bimClbF(y(p[1]))+'" r="3" fill="'+BIM_ZN_ROLECOL[r]+'" stroke="var(--surf)" stroke-width="1.5"/>';});
      var e=P[P.length-1];ends.push({r:r,x:x(e[0])+off,y:y(e[1]),s:e[0]});
      s+='<polyline class="hit" points="'+P.map(function(p){return bimClbF(x(p[0])+off)+','+bimClbF(y(p[1]));}).join(' ')+'" fill="none" stroke="transparent" stroke-width="10"'+bimClbTip(BIM_ZN_ROLENAME[r]+'|'+bimZnRuleText(C,r))+'/>';
    });
    ends.sort(function(a,b){return a.y-b.y;});
    var lastY=-1e9;ends.forEach(function(e){var yy=Math.max(e.y,lastY+13);lastY=yy;s+='<text class="lb" x="'+bimClbF(e.x+6)+'" y="'+bimClbF(yy+4)+'" style="fill:'+BIM_ZN_ROLECOL[e.r]+'">'+BIM_ZN_ROLENAME[e.r]+' '+bimZnM(e.s)+'</text>';});
    return s+'</svg>';
  }
  /* Fig. 5: the lot plan, turned so the street is at the bottom */
  function bimZnPlanSvg(C){
    var nw=A3D_CLB.narrow,W=nw?360:420,G=C.legs,Lf=G.legs[G.front],a0=Lf.a,e2=[-Lf.n[0],-Lf.n[1]],e1=[e2[1],-e2[0]],z=C.zoning;
    function U(p){return [(p[0]-a0[0])*e1[0]+(p[1]-a0[1])*e1[1],(p[0]-a0[0])*e2[0]+(p[1]-a0[1])*e2[1]];}
    var R=G.ring.map(U),F=C.fp.map(U),u0=Infinity,u1=-Infinity,v0=Infinity,v1=-Infinity;
    R.forEach(function(p){u0=Math.min(u0,p[0]);u1=Math.max(u1,p[0]);v0=Math.min(v0,p[1]);v1=Math.max(v1,p[1]);});
    var st=Math.max(4,Math.min(12,(v1-v0)*0.18)),M=nw?34:44,k=Math.min((W-2*M)/(u1-u0),(nw?280:300)/((v1-v0)+st)),H=Math.round((v1-v0+st)*k+2*M+10);
    var ox=(W-(u1-u0)*k)/2-u0*k,oy=M-v0*k;
    function S(p){return bimClbF(ox+p[0]*k)+','+bimClbF(oy+p[1]*k);}
    function SX(u){return ox+u*k;}function SY(v){return oy+v*k;}
    var s='<svg viewBox="0 0 '+W+' '+H+'" role="img" aria-label="Lot plan with setbacks; the street at the bottom">',yS=SY(0);
    s+='<rect x="0" y="'+bimClbF(yS)+'" width="'+W+'" height="'+bimClbF(st*k)+'" fill="var(--band)"/><text class="tk" x="'+(W/2)+'" y="'+bimClbF(yS+Math.max(st*k/2+4,st*k-6))+'" text-anchor="middle">Street</text>';
    s+='<polygon points="'+R.map(S).join(' ')+'" fill="var(--surf)" stroke="var(--ink)" stroke-width="2" stroke-linejoin="round" class="mk"'+bimClbTip('The lot|'+bimClimInt(C.lot)+' m²|'+G.legs.length+' sides')+'/>';
    s+='<polygon points="'+F.map(S).join(' ')+'" fill="var(--s4)" fill-opacity=".2" stroke="var(--s4)" stroke-width="1.5" stroke-dasharray="6 3" class="mk"'+
      bimClbTip('Buildable area at the ground|'+bimClimInt(C.fpArea)+' m² inside the setbacks|'+bimClbNum(100*C.fpArea/C.lot,0)+'% of the lot')+'/>';
    /* the plate above each step */
    var steps=[];BIM_ZN_ROLES.forEach(function(r){C.rules[r].steps.forEach(function(x){if(x[0]>0&&x[0]<C.top&&steps.indexOf(x[0])<0)steps.push(x[0]);});});
    steps.sort(function(a,b){return a-b;});
    steps.slice(0,3).forEach(function(h,si){
      var q=bimZnPlate(C,h,1);if(!q||q.length<3)return;
      var Q=q.map(function(c){return U(c.p);}),at=Q[0];
      Q.forEach(function(p){if(p[1]>at[1]+1e-9||(Math.abs(p[1]-at[1])<=1e-9&&p[0]>at[0]))at=p;});   /* its corner nearest the street, on the right */
      s+='<polygon points="'+Q.map(S).join(' ')+'" fill="none" stroke="var(--s4)" stroke-width="1" stroke-dasharray="2 3" class="mk"'+bimClbTip('Above '+bimZnM(h)+'|The plate: '+bimClimInt(Math.abs(bimZnArea2(q)))+' m²')+'/>'+
        '<text class="tk" x="'+bimClbF(SX(at[0])-4)+'" y="'+bimClbF(SY(at[1])-4-si*12)+'" text-anchor="end">Above '+bimZnM(h,0)+'</text>';
    });
    /* each side: its length outside; its role and setback inside */
    var cx=0,cy=0;R.forEach(function(p){cx+=p[0];cy+=p[1];});cx/=R.length;cy/=R.length;
    G.legs.forEach(function(l){
      var a=U(l.a),b=U(l.b),mx=(a[0]+b[0])/2,my=(a[1]+b[1])/2,dx=b[0]-a[0],dy=b[1]-a[1],ln=Math.sqrt(dx*dx+dy*dy)||1,nx=-dy/ln,ny=dx/ln;
      if((cx-mx)*nx+(cy-my)*ny>0){nx=-nx;ny=-ny;}
      var o=nw?12:15,sb=C.rules[l.role].base,ang=Math.atan2(dy,dx)*180/Math.PI;if(ang>90)ang-=180;if(ang<-90)ang+=180;
      var px=SX(mx+nx*o/k),py=SY(my+ny*o/k)+4;
      s+='<text class="tl2" x="'+bimClbF(px)+'" y="'+bimClbF(py)+'" text-anchor="middle" transform="rotate('+bimClbF(ang)+' '+bimClbF(px)+' '+bimClbF(py-4)+')">'+bimZnM(l.len)+'</text>';
      if(ln*k>44){
        var qx=SX(mx-nx*Math.max(sb/2,9/k)),qy=SY(my-ny*Math.max(sb/2,9/k))+4;
        s+='<text class="tk" x="'+bimClbF(qx)+'" y="'+bimClbF(qy)+'" text-anchor="middle" transform="rotate('+bimClbF(ang)+' '+bimClbF(qx)+' '+bimClbF(qy-4)+')" style="fill:'+BIM_ZN_ROLECOL[l.role]+'">'+BIM_ZN_ROLENAME[l.role]+(sb>0?' '+bimZnM(sb):'')+'</text>';
      }
    });
    var fc=bimZnCentroid(F);
    s+='<text class="lb" x="'+bimClbF(SX(fc[0]))+'" y="'+bimClbF(SY(fc[1])-2)+'" text-anchor="middle">Buildable</text><text class="tl2" x="'+bimClbF(SX(fc[0]))+'" y="'+bimClbF(SY(fc[1])+12)+'" text-anchor="middle">'+bimClimInt(C.fpArea)+' m²</text>';
    var tn=bimTrueNorthDeg()*Math.PI/180,nv=[Math.sin(tn),-Math.cos(tn)],ndx=nv[0]*e1[0]+nv[1]*e1[1],ndy=nv[0]*e2[0]+nv[1]*e2[1],nax=W-24,nay=24;
    s+='<g aria-label="North"><line x1="'+bimClbF(nax-ndx*11)+'" y1="'+bimClbF(nay-ndy*11)+'" x2="'+bimClbF(nax+ndx*11)+'" y2="'+bimClbF(nay+ndy*11)+'" stroke="var(--ink)" stroke-width="1.5"/>'+
      '<circle cx="'+bimClbF(nax+ndx*11)+'" cy="'+bimClbF(nay+ndy*11)+'" r="2.5" fill="var(--ink)"/><text class="lb" x="'+bimClbF(nax+ndx*20)+'" y="'+bimClbF(nay+ndy*20+4)+'" text-anchor="middle">N</text></g>';
    s+=bimZnScaleBar(12,H-22,k,W/4);
    return s+'</svg>';
  }
  /* Fig. 6: the floor plates by storey, the ground at the bottom */
  function bimZnPlatesSvg(C){
    var nw=A3D_CLB.narrow,W=nw?360:520,n=C.plates.length,bh=n>30?Math.max(4,Math.floor(360/n)-2):Math.min(18,Math.max(8,Math.floor(300/Math.max(1,n))-4)),gap=n>30?2:4,L=nw?40:48,R=W-(nw?50:66),T0=24,z=C.zoning;
    var H=T0+n*(bh+gap)+34,mx=Math.max.apply(null,C.plates.concat([1])),cov=z.cover!==null?z.cover/100*C.lot:null;
    var Tk=bimClbTicks(0,Math.max(mx,cov||0),nw?3:4),x1=Tk[Tk.length-1];
    function x(v){return L+v/x1*(R-L);}
    var s='<svg viewBox="0 0 '+W+' '+H+'" role="img" aria-label="Floor plates by storey">',B=T0+n*(bh+gap),acc=0,i;
    Tk.forEach(function(v){s+='<line class="gd" x1="'+bimClbF(x(v))+'" x2="'+bimClbF(x(v))+'" y1="'+T0+'" y2="'+B+'"/><text class="tk" x="'+bimClbF(x(v))+'" y="'+(B+14)+'" text-anchor="middle">'+bimClimInt(v)+'</text>';});
    s+='<text class="tk" x="'+R+'" y="'+(B+28)+'" text-anchor="end">m² a floor</text>';
    for(i=0;i<n;i++){
      var y=B-(i+1)*(bh+gap)+gap/2,p=C.plates[i],use=Math.max(0,Math.min(p,C.achievable-acc));acc+=p;
      var tip='Storey '+(i+1)+'|Plate '+bimClimInt(p)+' m², at '+bimZnM(i*z.f2f)+' to '+bimZnM((i+1)*z.f2f)+'|'+(use>=p-0.01?'Used by the achievable area':(use>0?bimClimInt(use)+' m² used, the rest beyond the '+C.governs:'Beyond the '+C.governs+': room the zoning does not let you use'));
      s+='<rect x="'+L+'" y="'+bimClbF(y)+'" width="'+bimClbF(x(p)-L)+'" height="'+bh+'" rx="2" fill="var(--hn)" class="mk"'+bimClbTip(tip)+'/>';
      if(use>0)s+='<rect x="'+L+'" y="'+bimClbF(y)+'" width="'+bimClbF(x(use)-L)+'" height="'+bh+'" rx="2" fill="var(--s1)" pointer-events="none"/>';
      if(n<=30||(i+1)%5===0||i===0)s+='<text class="tk" x="'+(L-6)+'" y="'+bimClbF(y+bh/2+4)+'" text-anchor="end">'+(i+1)+'</text>';
      if(n<=24&&bh>=10)s+='<text class="tk" x="'+bimClbF(x(p)+4)+'" y="'+bimClbF(y+bh/2+4)+'">'+bimClimInt(p)+'</text>';
    }
    if(cov!==null&&cov<=x1)s+='<line x1="'+bimClbF(x(cov))+'" x2="'+bimClbF(x(cov))+'" y1="'+(T0-6)+'" y2="'+B+'" stroke="var(--ink2)" stroke-width="1" stroke-dasharray="5 4"/>'+
      '<text class="tl2" x="'+bimClbF(x(cov))+'" y="'+(T0-10)+'" text-anchor="middle">Coverage limit</text>';
    s+='<text class="tk" x="'+(L-6)+'" y="'+(B+14)+'" text-anchor="end">'+(nw?'':'Storey')+'</text>';
    return s+'</svg>';
  }
  /* Fig. 7: the yield compared, on one scale from zero */
  function bimZnYieldSvg(C){
    var nw=A3D_CLB.narrow,W=nw?360:520,L=nw?104:150,R=W-(nw?58:70),rows=[],pr=C.proposed;
    if(C.farGFA!==null)rows.push(['Permitted by FAR',C.farGFA,'var(--hn)',C.zoning.far+' × '+bimClimInt(C.lot)+' m² lot']);
    rows.push(['Envelope capacity',C.capacity,'var(--hn)',C.plates.length+' plates under the envelope'+(C.zoning.cover!==null?', each at most the coverage limit':'')]);
    rows.push(['Achievable',C.achievable,'var(--s1)','The lesser: the '+C.governs+' governs']);
    if(pr.gfa!==null)rows.push(['Proposed',pr.gfa,pr.gfa>C.achievable+0.5?'var(--critical)':'var(--s3)','The design\'s gross floor area (usages)']);
    var bh=22,gap=12,T0=6,H=T0+rows.length*(bh+gap)+22,mx=0;rows.forEach(function(r){mx=Math.max(mx,r[1]);});
    var Tk=bimClbTicks(0,Math.max(1,mx),nw?3:4),x1=Tk[Tk.length-1];
    function x(v){return L+v/x1*(R-L);}
    var B=T0+rows.length*(bh+gap),s='<svg viewBox="0 0 '+W+' '+H+'" role="img" aria-label="Yield compared">';
    Tk.forEach(function(v){s+='<line class="gd" x1="'+bimClbF(x(v))+'" x2="'+bimClbF(x(v))+'" y1="'+T0+'" y2="'+B+'"/><text class="tk" x="'+bimClbF(x(v))+'" y="'+(B+14)+'" text-anchor="middle">'+bimClimInt(v)+'</text>';});
    rows.forEach(function(r,i){
      var y=T0+i*(bh+gap)+gap/2;
      s+='<text class="'+(r[0]==='Achievable'?'lb':'tl2')+'" x="'+(L-8)+'" y="'+(y+bh/2+4)+'" text-anchor="end">'+bimClbE(r[0])+'</text>'+
        '<rect class="mk" x="'+L+'" y="'+y+'" width="'+bimClbF(Math.max(1,x(r[1])-L))+'" height="'+bh+'" rx="3" fill="'+r[2]+'"'+bimClbTip(r[0]+'|'+bimClimInt(r[1])+' m² GFA|'+r[3])+'/>'+
        '<text class="lb" x="'+bimClbF(x(r[1])+5)+'" y="'+(y+bh/2+4)+'">'+bimClimInt(r[1])+'</text>';
    });
    s+='<line x1="'+L+'" x2="'+L+'" y1="'+T0+'" y2="'+B+'" stroke="var(--ink2)" stroke-width="1"/>';
    return s+'</svg>';
  }
  /* the zoning analysis table: permitted, proposed, complies */
  function bimZnState(ok){
    if(ok===null)return '<span class="a3d-zn-na">Not checked</span>';
    var S=BIM_STATE[ok?'good':'critical'];
    return '<div class="a3d-clb-st"><svg viewBox="0 0 16 16" style="color:'+S[1]+'" aria-hidden="true">'+S[2]+'</svg>'+(ok?'Complies':'Exceeds')+'</div>';
  }
  function bimZnRows(C){
    var z=C.zoning,pr=C.proposed,R=[],has=pr.height!==null||pr.gfa!==null,G=C.legs;
    function row(item,sub,perm,prop,ok){R.push({item:item,sub:sub,perm:perm,prop:prop,ok:ok});}
    R.push({grp:'Lot and use'});
    row('District',z.source||'',z.district||'—','',null);
    if(z.uses)row('Permitted uses','',z.uses,'',null);
    row('Lot area','From the property line','',bimClimInt(C.lot)+' m²',null);
    R.push({grp:'Bulk'});
    if(z.far!==null)row('Floor area ratio','Gross floor area ÷ lot area',bimClbNum(z.far,2)+' ('+bimClimInt(C.farGFA)+' m²)',pr.gfa!==null?bimClbNum(pr.gfa/C.lot,2)+' ('+bimClimInt(pr.gfa)+' m²)':'—',pr.gfa!==null?pr.gfa<=C.farGFA+0.5:null);
    if(C.maxH!==null)row('Building height','Above the lot',bimZnM(C.maxH),pr.height!==null?bimZnM(pr.height):'—',pr.height!==null?pr.height<=C.maxH+0.01:null);
    if(z.maxStoreys)row('Storeys','At '+bimZnM(z.f2f)+' floor to floor',String(z.maxStoreys),'—',null);
    if(z.cover!==null)row('Lot coverage','Ground floor ÷ lot area',bimClbNum(z.cover,0)+'% ('+bimClimInt(z.cover/100*C.lot)+' m²)',pr.coverArea!==null?bimClbNum(100*pr.coverArea/C.lot,0)+'% ('+bimClimInt(pr.coverArea)+' m²)':'—',pr.coverArea!==null?pr.coverArea<=z.cover/100*C.lot+0.5:null);
    R.push({grp:'Yards, steps and planes'});
    bimZnRoles(C).forEach(function(r){
      var sides=[];G.legs.forEach(function(l,i){if(l.role===r)sides.push(i+1);});
      row(BIM_ZN_ROLENAME[r]+(r==='front'?'':(sides.length>1?' yards':' yard')),'Side'+(sides.length>1?'s ':' ')+sides.join(', '),bimZnRuleText(C,r),'',null);
    });
    row('Inside the envelope','Every element, in plan and in height','Every element',has?(pr.outside.length?pr.outside.length+' outside':'All inside'):'—',has?!pr.outside.length:null);
    R.push({grp:'Parking'});
    row('Parking spaces','Required at the yield',C.parking+' required','Not modelled',null);
    return R;
  }
  function bimZnTableHtml(C){
    return '<div class="a3d-clb-tw"><table class="a3d-zn-zt"><thead><tr><th>Item</th><th>Permitted or required</th><th>Proposed</th><th>Complies</th></tr></thead><tbody>'+
      bimZnRows(C).map(function(r){
        if(r.grp)return '<tr class="grp"><td colspan="4">'+bimClbE(r.grp)+'</td></tr>';
        return '<tr data-znrow="'+bimClbE(r.item)+'"><td class="it">'+bimClbE(r.item)+(r.sub?'<small>'+bimClbE(r.sub)+'</small>':'')+'</td><td class="n">'+bimClbE(r.perm)+'</td><td class="n">'+bimClbE(r.prop)+'</td><td>'+(r.prop===''||r.perm===''?'':bimZnState(r.ok))+'</td></tr>';
      }).join('')+'</tbody></table></div>';
  }
  function bimZnSectionTable(C,kind){
    var S=bimZnSection(C,kind);if(!S.lot)return '';
    return bimClbTable(['Height','From the '+C.legs.legs[S.lot.ea].role+' lot line','To the '+C.legs.legs[S.lot.eb].role+' lot line','Envelope width'],
      S.L.map(function(p,i){return [bimZnM(p[1],2),bimZnM(p[0]-S.lot.a,2),bimZnM(S.lot.b-S.R[i][0],2),bimZnM(S.R[i][0]-p[0],2)];}));
  }
  function bimZnBoardHtml(){
    var z=bimZnHas()?bimZn():null,C=z?bimZnCalc():null,cards=[],kp=[],fig=0,env=!!bimZnEnvelopeObj();
    var site=(A3D.site&&A3D.site.name&&A3D.site.name!=='Site')?A3D.site.name:(bimProjectLabel()||'The site');
    var bar='<div class="a3d-clb-bar"><div class="a3d-clb-bart">Zoning and yield</div>'+
      '<button type="button" class="a3d-clb-btn" data-clb="tables" aria-pressed="'+A3D_CLB.tables+'">Tables</button>'+
      (C&&C.ok?'<button type="button" class="a3d-clb-btn a3d-clb-hide-s" data-clb="envelope">'+(env?'Rebuild envelope':'Build envelope')+'</button>':'')+
      '<button type="button" class="a3d-clb-btn a3d-clb-hide-s" data-clb="print">Print</button>'+
      '<button type="button" class="a3d-clb-btn" data-clb="close" aria-label="Close the board">Close</button></div>';
    var head='<div class="a3d-clb-page"><header><div class="a3d-clb-kicker">Site analysis · 3 Legal and regulatory</div><h1 class="a3d-clb-h1">'+bimClbE(site)+': zoning and yield</h1>';
    if(!z||!C.ok)return bar+head+'</header><div class="a3d-clb-empty">'+(z?bimClbE(C.error)+'.':'No zoning yet. Enter the district\'s controls in Site analysis (Zoning and yield, Enter zoning), or read them from a council zoning layer under the lot.')+'</div></div>';
    var pr=C.proposed,has=pr.height!==null||pr.gfa!==null,T=bimZnRows(C),bad=T.filter(function(r){return r.ok===false;}),Lf=C.legs.legs[C.legs.front];
    var anyPlane=C.rules.front.plane||C.rules.side.plane||C.rules.rear.plane;
    head+='<p class="a3d-clb-sub">'+bimClbE((z.district?'District '+z.district+' · ':'')+'Lot '+bimClimInt(C.lot)+' m² · '+(z.source?'Source: '+z.source:'Entered by hand')+' · worked out '+bimSaToday())+'</p></header>';
    kp.push(bimClbKpi('Lot area',bimClimInt(C.lot),'m²','Frontage '+bimZnM(Lf.len)+'; depth '+bimZnM(C.lotD)));
    if(z.far!==null)kp.push(bimClbKpi('Floor area ratio',bimClbNum(z.far,2),'',bimClimInt(C.farGFA)+' m² GFA permitted'));
    if(C.maxH!==null)kp.push(bimClbKpi('Height limit',bimClbNum(C.maxH,1),'m',z.maxStoreys?z.maxStoreys+' storeys at most':(anyPlane?'And angular planes':'')));
    if(z.cover!==null)kp.push(bimClbKpi('Lot coverage',bimClbNum(z.cover,0),'%',bimClimInt(z.cover/100*C.lot)+' m² a floor at most'));
    kp.push(bimClbKpi('Envelope capacity',bimClimInt(C.capacity),'m²',C.plates.length+' storeys of '+bimZnM(z.f2f)+'; '+bimClimInt(C.volume)+' m³'));
    kp.push(bimClbKpi('Achievable GFA',bimClimInt(C.achievable),'m²','The '+C.governs+' governs; '+C.storeysUsed+' storey'+(C.storeysUsed===1?'':'s')));
    kp.push(bimClbKpi('Units',String(C.units),'',bimClimInt(C.nsa)+' m² net at '+bimClbNum(z.eff,0)+'%; '+bimClbNum(z.unit,0)+' m² each'));
    kp.push(bimClbKpi('Parking',String(C.parking),'spaces',bimClbNum(z.park,2)+' a unit'+(z.parkNon&&z.res<100?', '+bimClbNum(z.parkNon,1)+' per 100 m² other':'')));
    kp.push(bimClbKpi('The design',has?(bad.length?bad.length+' issue'+(bad.length===1?'':'s'):'Complies'):'None yet','',has?(bad.length?bad.map(function(r){return r.item;}).join(', '):'Every control checked'):'Model the massing with usages',has?(bad.length?'critical':'good'):''));
    bimFigCapKpis('zn.kpis',kp);   /* __acad3dV172b */
    var h=bar+head+'<section class="a3d-clb-kpis" aria-label="Indicators" style="--n:'+kp.length+'">'+kp.join('')+'</section><section class="a3d-clb-grid">';
    var src=(z.source||'Entered by hand')+'; worked out in the app';
    fig++;
    cards.push(bimClbCard(['s7','wide','@zn.table'],fig,!has?'The zoning analysis: '+T.filter(function(r){return r.item;}).length+' controls; the design is checked once it has massing':
      (bad.length?'The design exceeds '+bad.length+' control'+(bad.length===1?'':'s')+': '+bad.map(function(r){return r.item.toLowerCase();}).join(', '):
        'The design complies with all '+T.filter(function(r){return r.ok===true;}).length+' controls the model can check'),
      'Each control of the district, what it permits or requires, what the model proposes, and whether it complies. Controls the model cannot check are marked so.',
      bimZnTableHtml(C)+(pr.outside.length?'<p class="a3d-zn-out">Outside the envelope: '+pr.outside.slice(0,8).map(function(o){return bimClbE(o.name||o.id);}).join(', ')+(pr.outside.length>8?' and '+(pr.outside.length-8)+' more':'')+'.</p>':''),src));
    var why=[],fr=C.rules.front;
    if(fr.steps.length)why.push(fr.steps.length===1?'a step back at '+bimZnM(fr.steps[0][0]):fr.steps.length+' steps back');
    if(anyPlane)why.push('angular planes');
    if(C.maxH!==null&&C.top>=C.maxH-1e-6)why.push('the '+bimZnM(C.maxH)+' height limit');
    fig++;
    cards.push(bimClbCard(['s5','@zn.secA'],fig,'The envelope rises to '+bimZnM(C.top)+(why.length?': '+why.join(', then '):''),
      'Section from the front to the rear, square to the front lot line, at true scale: the most the rules allow at each distance behind the street. Floor lines every '+bimZnM(z.f2f)+'.',
      '<div class="a3d-clb-chart">'+bimZnSectionSvg(C,'A')+'</div>'+bimClbLeg([['var(--s4)','Zoning envelope'],['var(--ink2)','Height limit','dsh']].concat(bimZnPlaneLeg(C)).concat(pr.height!==null?[['var(--s1)','Proposed height','ln']]:[]))+
      bimZnSectionTable(C,'A'),src));
    var Sb=bimZnSection(C,'B');
    fig++;
    cards.push(bimClbCard(['s4','@zn.secB'],fig,Sb.lot&&Sb.L.length?'Side to side the envelope is '+bimZnM(Sb.R[0][0]-Sb.L[0][0])+' wide at the ground, '+bimZnM(Sb.R[Sb.R.length-1][0]-Sb.L[Sb.L.length-1][0])+' at the top':'Side to side',
      'Section across the lot, along the front, through the middle of the buildable area, at true scale.',
      '<div class="a3d-clb-chart">'+bimZnSectionSvg(C,'B')+'</div>'+bimZnSectionTable(C,'B'),src));
    fig++;
    var roles=bimZnRoles(C);
    cards.push(bimClbCard(['s4','@zn.rules'],fig,'Each side\'s rule: '+roles.map(function(r){var P=bimZnRulePts(C,r);return r+' '+bimZnM(P[0][0])+(P[P.length-1][0]>P[0][0]+1e-9?' to '+bimZnM(P[P.length-1][0]):'');}).join(', '),
      'The setback each kind of side needs at each height: across, the distance from the lot line; up, the height. A step is a jump back; an angular plane, a slope.',
      '<div class="a3d-clb-chart">'+bimZnRulesSvg(C)+'</div>'+bimClbLeg(roles.map(function(r){return [BIM_ZN_ROLECOL[r],BIM_ZN_ROLENAME[r],'ln'];}).concat(C.maxH!==null?[['transparent','Height limit','dsh']]:[]))+
      bimClbTable(['Side','At the ground','Steps','Angular plane'],roles.map(function(r){var o=C.rules[r];return [BIM_ZN_ROLENAME[r],bimZnM(o.base),o.steps.map(function(x){return bimZnM(x[1])+' above '+bimZnM(x[0]);}).join('; ')||'—',o.plane?bimClbNum(o.plane[1],1)+':1 from '+bimZnM(o.plane[0]):'—'];})),src));
    fig++;
    cards.push(bimClbCard(['s4','@zn.plan'],fig,bimClimInt(C.fpArea)+' m² buildable at the ground, '+bimClbNum(100*C.fpArea/C.lot,0)+'% of the lot',
      'The lot, turned so the street is at the bottom: each side\'s length outside, its role and setback inside; the buildable area dashed, the plate above each step dotted.',
      '<div class="a3d-clb-chart">'+bimZnPlanSvg(C)+'</div>'+
      bimClbTable(['Side','Length','Role','Setback at the ground'],C.legs.legs.map(function(l,i){return ['Side '+(i+1),bimZnM(l.len,2),l.role+(l.auto?'':' (picked)'),bimZnM(C.rules[l.role].base,2)];})),src));
    fig++;
    cards.push(bimClbCard(['s6','@zn.plates'],fig,C.plates.length+' storeys fit under the envelope; the '+C.governs+' lets '+C.storeysUsed+' of them be used',
      'Floor plate by storey: the area under the envelope at each floor\'s ceiling'+(z.cover!==null?', at most the coverage limit':'')+'. Blue: used by the achievable area; grey: beyond it.',
      '<div class="a3d-clb-chart">'+bimZnPlatesSvg(C)+'</div>'+bimClbLeg([['var(--s1)','Used by the achievable area'],['var(--hn)','Beyond it']].concat(z.cover!==null?[['transparent','Coverage limit','dsh']]:[]))+
      bimClbTable(['Storey','From','To','Plate m²'],C.plates.map(function(p,i){return [i+1,bimZnM(i*z.f2f),bimZnM((i+1)*z.f2f),bimClimInt(p)];})),src));
    fig++;
    var chain='<table class="a3d-zn-chain" aria-label="Yield"><tbody>'+
      '<tr><td class="op"></td><td>Achievable gross floor area</td><td class="n">'+bimClimInt(C.achievable)+' m²</td></tr>'+
      '<tr><td class="op">×</td><td>Efficiency, net to gross</td><td class="n">'+bimClbNum(z.eff,0)+'%</td></tr>'+
      '<tr><td class="op">=</td><td>Net area</td><td class="n">'+bimClimInt(C.nsa)+' m²</td></tr>'+
      (z.res<100?'<tr><td class="op">×</td><td>Residential share</td><td class="n">'+bimClbNum(z.res,0)+'%</td></tr>':'')+
      '<tr><td class="op">÷</td><td>Average unit, net</td><td class="n">'+bimClbNum(z.unit,0)+' m²</td></tr>'+
      '<tr class="tot"><td class="op">=</td><td>Units (whole)</td><td class="n">'+C.units+'</td></tr>'+
      '<tr class="tot"><td class="op"></td><td>Parking: '+C.units+' × '+bimClbNum(z.park,2)+(z.res<100&&z.parkNon?' + '+bimClimInt(C.nonRes)+' m² ÷ 100 × '+bimClbNum(z.parkNon,1):'')+'</td><td class="n">'+C.parking+' spaces</td></tr></tbody></table>';
    cards.push(bimClbCard(['s6','wide','@zn.yield'],fig,'The '+C.governs+' governs: '+bimClimInt(C.achievable)+' m² GFA, '+bimClimInt(C.nsa)+' m² net, '+C.units+' unit'+(C.units===1?'':'s'),
      'Gross floor area on one scale from zero: what the FAR permits, what the envelope can hold, the lesser of the two, and the design. Then from gross to units and parking.',
      '<div class="a3d-clb-chart">'+bimZnYieldSvg(C)+'</div>'+chain,'Assumptions in the zoning record'));
    h+=cards.join('')+'</section>';
    h+='<footer class="a3d-clb-notes"><h3>Method, assumptions and sources</h3><ul>'+
      '<li>Zoning: '+bimClbE(z.source||'entered by hand')+'. Check every control against the current code and any overlay, variance or bonus before relying on it.</li>'+
      '<li>Envelope: each side of the property is a front, a side or a rear (picked, or worked out from the chosen front); each kind has its own rule: a setback at the ground, steps back above set heights, and an angular plane rising from the lot line. At every height the plate is the lot with each side moved in by its rule there, up to the height limit. Worked out exactly, piece by piece between the heights where a rule changes.'+(C.convex?'':' The lot is not convex: its sides are moved in and joined where they meet, as for the setback line.')+'</li>'+
      (C.split!==null?'<li>Above '+bimZnM(C.split)+' the setbacks would split this lot in two; the envelope stops there. Check the upper floors by hand.</li>':'')+
      '<li>Capacity: the area under the envelope at each floor\'s ceiling, every '+bimZnM(z.f2f)+(z.cover!==null?', each floor at most the coverage limit ('+bimClimInt(z.cover/100*C.lot)+' m²)':'')+(z.maxStoreys?', at most '+z.maxStoreys+' storeys':'')+'. The achievable area is the lesser of it and FAR × lot area.</li>'+
      '<li>Yield: net area at '+bimClbNum(z.eff,0)+'% efficiency (residential is typically 75–85%); units of '+bimClbNum(z.unit,0)+' m² net, rounded down; parking '+bimClbNum(z.park,2)+' a unit'+(z.res<100?' and '+bimClbNum(z.parkNon,1)+' per 100 m² of other uses':'')+', rounded up.</li>'+
      '<li>The design: gross floor area from its usages; height from the highest building element; coverage from the footprints of the usages standing on the ground (a basement covers none). Elements outside the envelope in plan or height are listed; at and below the ground the envelope does not apply.</li>'+
      '<li>Presentation after the permit zoning analysis table, New York\'s <a href="https://www.nyc.gov/assets/buildings/pdf/zd1_guide.pdf" target="_blank" rel="noopener">ZD1 zoning diagram</a> (sections at true scale, dimensioned), and the setback-against-height profile of envelope tools such as Giraffe\'s.</li>'+
      '</ul></footer></div>';
    return h;
  }
  /* ---- the Site analysis section ---- */
  function bimZnInput(k,label,cls){
    var z=bimZn(),F=BIM_ZN_FIELDS[k],v=z[k];
    return '<label'+(cls?' class="'+cls+'"':'')+'>'+bimEsc(label)+'<input '+(F[0]==='text'?'type="text" maxlength="'+F[1]+'"':'type="number" step="any" inputmode="decimal" min="'+F[1]+'" max="'+F[2]+'"')+
      ' data-znf="'+k+'" value="'+(v===null||v===undefined?'':bimEsc(String(v)))+'"></label>';
  }
  function bimZnStepsHtml(role){
    var z=bimZn(),L=z[role+'Steps']||[];
    return L.map(function(s,i){
      function inp(j,lbl){return '<label>'+lbl+'<input type="number" step="any" inputmode="decimal" min="0" max="'+(j?500:1000)+'" data-znf="'+role+'Steps.'+i+'.'+(j?'s':'h')+'" value="'+(s[j]===null||s[j]===undefined?'':bimEsc(String(s[j])))+'"></label>';}
      return '<div class="a3d-znstep" data-znstep="'+role+'.'+i+'">'+inp(0,'Step '+(i+1)+': above (m)')+inp(1,'set back (m)')+
        '<button type="button" class="a3d-anzbtn x" data-saact="znstepdel:'+role+'.'+i+'" aria-label="Remove step '+(i+1)+'" title="Remove this step">×</button></div>';
    }).join('')+(L.length<BIM_ZN_MAXSTEPS?'<div class="a3d-znstep add"><button type="button" class="a3d-anzbtn" data-saact="znstepadd:'+role+'">Add a step</button></div>':'');
  }
  function bimZnSaHtml(){
    var z=bimZnHas()?bimZn():null,P=bimZnProperty(),s='<div class="a3d-clsec" data-znsec="1"><div class="a3d-sasechd">Zoning and yield</div>',C=z?bimZnCalc():null;
    if(z){
      var p=[];if(z.district)p.push(z.district);if(z.far!==null)p.push('FAR '+z.far);if(z.maxH!==null)p.push(bimClimFmt(z.maxH)+' m');
      if(C&&C.ok)p.push(bimClimInt(C.achievable)+' m² achievable ('+C.governs+' governs), '+C.units+' units');
      else if(C)p.push(C.error);
      s+='<p class="a3d-clsum">'+bimEsc(p.join(' · '))+'</p>';
    }else s+='<p class="a3d-clsum">The district\'s controls: FAR, height, setbacks by side with their steps and angular planes, coverage and parking. They give the envelope in 3D, the yield, and a zoning analysis table.</p>';
    s+='<div class="a3d-saacts"><button type="button" class="a3d-anzbtn'+(z?'':' pri')+'" data-saact="znedit" aria-expanded="'+A3D_ZN.edit+'">'+(A3D_ZN.edit?'Done':(z?'Edit zoning':'Enter zoning'))+'</button>'+
      (z?'<button type="button" class="a3d-anzbtn pri" data-saact="znbuild"'+(P?'':' disabled title="Make a property line first"')+'>'+(bimZnEnvelopeObj()?'Rebuild envelope':'Build envelope')+'</button>'+
        '<button type="button" class="a3d-anzbtn" data-saact="znboard" title="The board is a page of the set: it opens here and presents and prints with the sheets">Show in Presentation</button>':'')+'</div>';
    if(A3D_ZN.edit){
      var cand=bimZnFromLayer(false),G=P?bimZnLegs(P,bimZn().frontLeg,bimZn().legRoles):null,lay=[];
      if(cand)['district','far','height'].forEach(function(k){if(cand[k])lay.push(cand[k].layer+': '+cand[k].attr);});
      s+='<div class="a3d-znf">'+bimZnInput('district','District')+
        (cand?'<label>From the layers<button type="button" class="a3d-anzbtn" data-saact="znlayer" title="'+bimEsc(lay.join('; '))+'">Use '+bimEsc(bimZnFoundText(cand))+'</button></label>':'<label>From the layers<span class="a3d-znhint" style="margin:4px 0 0">No zoning layer under the lot</span></label>')+
        bimZnInput('uses','Permitted uses','w')+bimZnInput('far','Floor area ratio')+bimZnInput('maxH','Height limit (m)')+bimZnInput('maxStoreys','Storeys limit')+bimZnInput('cover','Coverage limit (%)')+
        '<div class="a3d-znhd">Front<small>the street side</small></div>'+bimZnInput('front','Setback (m)');
      s+=G?'<label>Front of the lot<select data-znf="frontLeg">'+G.legs.map(function(l,i){return '<option value="'+i+'"'+(i===G.front?' selected':'')+'>Side '+(i+1)+' · '+bimClimFmt(l.len,0)+' m</option>';}).join('')+'</select></label>':'<span></span>';
      s+=bimZnInput('baseH','Street wall height (m)')+bimZnInput('step','Stepback above it (m)')+bimZnInput('skyH','Sky plane starts at (m)')+bimZnInput('skyR','Sky plane ratio (V:H)')+bimZnStepsHtml('front')+
        '<div class="a3d-znhd">Sides</div>'+bimZnInput('side','Setback (m)')+'<span></span>'+bimZnInput('sideH','Angular plane starts at (m)')+bimZnInput('sideR','Angular plane ratio (V:H)')+bimZnStepsHtml('side')+
        '<div class="a3d-znhd">Rear</div>'+bimZnInput('rear','Setback (m)')+'<span></span>'+bimZnInput('rearH','Angular plane starts at (m)')+bimZnInput('rearR','Angular plane ratio (V:H)')+bimZnStepsHtml('rear');
      if(G)s+='<div class="a3d-znhd">The lot\'s sides<small>a corner lot has two fronts</small></div><div class="a3d-znlegs">'+G.legs.map(function(l,i){
        var o=(z&&z.legRoles&&z.legRoles[i])||'',auto=i===G.front?'The front':'Auto ('+l.role+')';
        return '<label>Side '+(i+1)+' · '+bimClimFmt(l.len)+' m<select data-znf="legRoles.'+i+'"'+(i===G.front?' disabled':'')+'>'+
          [['',auto],['front','Front'],['side','Side'],['rear','Rear']].map(function(r){return '<option value="'+r[0]+'"'+(r[0]===o&&i!==G.front?' selected':'')+'>'+r[1]+'</option>';}).join('')+'</select></label>';}).join('')+'</div>';
      s+='<div class="a3d-znhd">Yield assumptions</div>'+bimZnInput('f2f','Floor to floor (m)')+bimZnInput('eff','Efficiency, net/gross (%)')+bimZnInput('unit','Average unit, net (m²)')+bimZnInput('res','Residential share (%)')+
        bimZnInput('park','Parking per unit')+bimZnInput('parkNon','Parking per 100 m² other')+bimZnInput('source','Source (code, section, date)','w')+
        '<p class="a3d-znhint">Leave a control blank where the code sets none. Each side keeps its setback up to the first step; a step moves it back above a height; an angular plane rises from the lot line at its ratio. The envelope is the lot with every side moved in by its rule, up to the height limit.</p></div>';
    }
    return s+'</div>';
  }

