"""patch_phase160b.py -- V160: the Zoning and yield board.

reference/research-zoning-envelope-yield.md. In the Climate board's frame (V159), after the permit
zoning analysis table, NYC's ZD1 zoning diagram (sections at true scale, every distance dimensioned)
and Giraffe's envelope tool (each side's setback against height):
- indicators: lot, FAR, height, coverage, envelope capacity, achievable GFA and what governs, units,
  parking, the design (an icon and a word);
- Fig. 1 the zoning analysis table: each control, permitted, proposed, complies;
- Fig. 2 the envelope in section from the front to the rear, at true scale: street, lot lines,
  setbacks, steps, angular planes, the height limit, floors, the proposed height, dimensioned;
- Fig. 3 the same from side to side;
- Fig. 4 the rules by side: the setback each kind of side needs at each height;
- Fig. 5 the lot plan, the street at the bottom: the sides and their roles, the buildable area, the
  plate above each step, north, a scale bar;
- Fig. 6 the floor plates by storey: those the achievable area uses, those beyond, the coverage limit;
- Fig. 7 the yield: by FAR, the envelope's capacity, the achievable, the proposed; GFA to net to
  units, and parking;
- notes: method, every assumption, the source.
Each figure has a table; every mark a tooltip; drawn again for a phone; printable."""
NAME = 'patch_phase160b.py'
BASE = 'c49545faec3c6f8a3b6ab0df8b07deca190b4c29ffae7b7c6d25d0ce00b07dbd'
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def rep(old, new, n=1):
    global t
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: anchor count %d (want %d): %r' % (c, n, old[:80]))
    t = t.replace(old, new)


rep(""".a3d-clb-eqt th{color:var(--ink2);font-weight:600}""", """.a3d-clb-eqt th{color:var(--ink2);font-weight:600}
/* __acad3dV160: the zoning analysis table and the yield chain, always shown */
.a3d-zn-zt{width:100%;border-collapse:collapse;font-size:12.5px;font-variant-numeric:tabular-nums}
.a3d-zn-zt th{color:var(--ink2);font-weight:600;font-size:11.5px;text-align:left;padding:6px 8px;border-bottom:1px solid var(--base)}
.a3d-zn-zt td{padding:7px 8px;border-bottom:1px solid var(--grid);vertical-align:top}
.a3d-zn-zt td.it{font-weight:600}
.a3d-zn-zt td.it small{display:block;font-weight:400;color:var(--muted);font-size:11px}
.a3d-zn-zt tr.grp td{color:var(--muted);font-size:11px;letter-spacing:.06em;text-transform:uppercase;font-weight:600;padding-top:12px}
.a3d-zn-zt .a3d-clb-st{margin-top:0}
.a3d-zn-na{color:var(--muted);font-size:11.5px}
.a3d-zn-chain{width:100%;border-collapse:collapse;font-size:12.5px;font-variant-numeric:tabular-nums;margin-top:8px}
.a3d-zn-chain td{padding:5px 6px;border-bottom:1px solid var(--grid)}
.a3d-zn-chain td.n{text-align:right;white-space:nowrap;font-weight:600}
.a3d-zn-chain td.op{color:var(--muted);width:18px;text-align:center}
.a3d-zn-chain tr.tot td{border-bottom:0;border-top:1px solid var(--base)}
.a3d-zn-out{margin:8px 0 0;font-size:12px;color:var(--ink2)}
@media(max-width:760px){.a3d-zn-zt{font-size:12px}.a3d-zn-zt th,.a3d-zn-zt td{padding:6px 5px}}""")

BOARD = r"""
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
    var h=bar+head+'<section class="a3d-clb-kpis" aria-label="Indicators" style="--n:'+kp.length+'">'+kp.join('')+'</section><section class="a3d-clb-grid">';
    var src=(z.source||'Entered by hand')+'; worked out in the app';
    fig++;
    cards.push(bimClbCard(['s7','wide'],fig,!has?'The zoning analysis: '+T.filter(function(r){return r.item;}).length+' controls; the design is checked once it has massing':
      (bad.length?'The design exceeds '+bad.length+' control'+(bad.length===1?'':'s')+': '+bad.map(function(r){return r.item.toLowerCase();}).join(', '):
        'The design complies with all '+T.filter(function(r){return r.ok===true;}).length+' controls the model can check'),
      'Each control of the district, what it permits or requires, what the model proposes, and whether it complies. Controls the model cannot check are marked so.',
      bimZnTableHtml(C)+(pr.outside.length?'<p class="a3d-zn-out">Outside the envelope: '+pr.outside.slice(0,8).map(function(o){return bimClbE(o.name||o.id);}).join(', ')+(pr.outside.length>8?' and '+(pr.outside.length-8)+' more':'')+'.</p>':''),src));
    var why=[],fr=C.rules.front;
    if(fr.steps.length)why.push(fr.steps.length===1?'a step back at '+bimZnM(fr.steps[0][0]):fr.steps.length+' steps back');
    if(anyPlane)why.push('angular planes');
    if(C.maxH!==null&&C.top>=C.maxH-1e-6)why.push('the '+bimZnM(C.maxH)+' height limit');
    fig++;
    cards.push(bimClbCard('s5',fig,'The envelope rises to '+bimZnM(C.top)+(why.length?': '+why.join(', then '):''),
      'Section from the front to the rear, square to the front lot line, at true scale: the most the rules allow at each distance behind the street. Floor lines every '+bimZnM(z.f2f)+'.',
      '<div class="a3d-clb-chart">'+bimZnSectionSvg(C,'A')+'</div>'+bimClbLeg([['var(--s4)','Zoning envelope'],['var(--ink2)','Height limit','dsh']].concat(bimZnPlaneLeg(C)).concat(pr.height!==null?[['var(--s1)','Proposed height','ln']]:[]))+
      bimZnSectionTable(C,'A'),src));
    var Sb=bimZnSection(C,'B');
    fig++;
    cards.push(bimClbCard('s4',fig,Sb.lot&&Sb.L.length?'Side to side the envelope is '+bimZnM(Sb.R[0][0]-Sb.L[0][0])+' wide at the ground, '+bimZnM(Sb.R[Sb.R.length-1][0]-Sb.L[Sb.L.length-1][0])+' at the top':'Side to side',
      'Section across the lot, along the front, through the middle of the buildable area, at true scale.',
      '<div class="a3d-clb-chart">'+bimZnSectionSvg(C,'B')+'</div>'+bimZnSectionTable(C,'B'),src));
    fig++;
    var roles=bimZnRoles(C);
    cards.push(bimClbCard('s4',fig,'Each side\'s rule: '+roles.map(function(r){var P=bimZnRulePts(C,r);return r+' '+bimZnM(P[0][0])+(P[P.length-1][0]>P[0][0]+1e-9?' to '+bimZnM(P[P.length-1][0]):'');}).join(', '),
      'The setback each kind of side needs at each height: across, the distance from the lot line; up, the height. A step is a jump back; an angular plane, a slope.',
      '<div class="a3d-clb-chart">'+bimZnRulesSvg(C)+'</div>'+bimClbLeg(roles.map(function(r){return [BIM_ZN_ROLECOL[r],BIM_ZN_ROLENAME[r],'ln'];}).concat(C.maxH!==null?[['transparent','Height limit','dsh']]:[]))+
      bimClbTable(['Side','At the ground','Steps','Angular plane'],roles.map(function(r){var o=C.rules[r];return [BIM_ZN_ROLENAME[r],bimZnM(o.base),o.steps.map(function(x){return bimZnM(x[1])+' above '+bimZnM(x[0]);}).join('; ')||'—',o.plane?bimClbNum(o.plane[1],1)+':1 from '+bimZnM(o.plane[0]):'—'];})),src));
    fig++;
    cards.push(bimClbCard('s4',fig,bimClimInt(C.fpArea)+' m² buildable at the ground, '+bimClbNum(100*C.fpArea/C.lot,0)+'% of the lot',
      'The lot, turned so the street is at the bottom: each side\'s length outside, its role and setback inside; the buildable area dashed, the plate above each step dotted.',
      '<div class="a3d-clb-chart">'+bimZnPlanSvg(C)+'</div>'+
      bimClbTable(['Side','Length','Role','Setback at the ground'],C.legs.legs.map(function(l,i){return ['Side '+(i+1),bimZnM(l.len,2),l.role+(l.auto?'':' (picked)'),bimZnM(C.rules[l.role].base,2)];})),src));
    fig++;
    cards.push(bimClbCard('s6',fig,C.plates.length+' storeys fit under the envelope; the '+C.governs+' lets '+C.storeysUsed+' of them be used',
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
    cards.push(bimClbCard(['s6','wide'],fig,'The '+C.governs+' governs: '+bimClimInt(C.achievable)+' m² GFA, '+bimClimInt(C.nsa)+' m² net, '+C.units+' unit'+(C.units===1?'':'s'),
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
"""

rep("""  /* ---- the Site analysis section ---- */
  function bimZnInput(""", BOARD + """  /* ---- the Site analysis section ---- */
  function bimZnInput(""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
