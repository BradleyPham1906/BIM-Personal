"""patch_phase161b.py -- V161: Site analysis SA4, access and people: the board.

reference/research-access-people.md (8). The Access and people board, in the Climate board's frame:
- indicators in two rows: access (daily needs, the nearest bus and rail, lines, intersections, each
  with a state where a reference exists) and the people (population, age, income, renting, no car);
- Fig. 1, the walk-time map: the network in rings of 5, 10 and 15 minutes as Network Analyst's
  service-area lines are drawn, 15 to 20 in grey, the stops, the nearest of each daily need, and
  400 and 800 m as the crow flies for comparison; north up, a scale bar;
- Fig. 2, daily needs: the nearest of each kind and the next ones on one scale of minutes;
- Fig. 3, transit: the stops by walk time, with the lines that serve them;
- Fig. 4, the street hierarchy within 400 m: line weight by functional class, the frontage, the
  intersections counted; the frontage table (street, class, length, speed, lanes, sidewalks);
- Fig. 5, connectivity: intersection density against LEED ND's thresholds, and route directness;
- Fig. 6, the tract against its county and state: each measure on its own scale, the tract with
  its 90% margin of error, a difference counted only beyond the margins (the Census Bureau's test);
- Fig. 7, how people get to work: 100% bars, seven means in a fixed order;
- Fig. 8, the age pyramid: men and women in five-year bands, the county's outline over it;
- notes on method and sources.
Every figure has its table and a tooltip on every mark; it prints, follows the theme, and is
redrawn for a phone."""
NAME = 'patch_phase161b.py'
BASE = '392c4c9aae48fa4e8af2ef294ee179f9aaee7e85c0005b140b1eb1ae60c8dac7'   # the output of patch_phase161a.py
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


# ---- the frame takes a third kind ----
rep("""    if(kind==='climate'||kind==='zoning')A3D_CLB.kind=kind;   /* __acad3dV160 */""",
    """    if(kind==='climate'||kind==='zoning'||kind==='access')A3D_CLB.kind=kind;   /* __acad3dV160; __acad3dV161 */""")
rep("""    b.setAttribute('aria-label',A3D_CLB.kind==='zoning'?'Zoning and yield board':'Climate and risk board');   /* __acad3dV160 */""",
    """    b.setAttribute('aria-label',A3D_CLB.kind==='zoning'?'Zoning and yield board':(A3D_CLB.kind==='access'?'Access and people board':'Climate and risk board'));   /* __acad3dV160; __acad3dV161 */""")
rep("""    if(A3D_CLB.kind==='zoning')return bimZnBoardHtml();   /* __acad3dV160 */""",
    """    if(A3D_CLB.kind==='zoning')return bimZnBoardHtml();   /* __acad3dV160 */
    if(A3D_CLB.kind==='access')return bimAccBoardHtml();   /* __acad3dV161 */""")
rep("""      else if(a==='refresh')bimClimFetch();""", """      else if(a==='refresh'){if(A3D_CLB.kind==='access')bimAccFetch();else bimClimFetch();}   /* __acad3dV161 */""")

# ---- the categorical slots five to seven (the commute's seven means), in each theme and in print ----
rep("""  --s1:#3987e5;--s2:#d95926;--s3:#199e70;--s4:#c98500;--band:rgba(255,255,255,.08);""",
    """  --s1:#3987e5;--s2:#d95926;--s3:#199e70;--s4:#c98500;--s5:#d55181;--s6:#008300;--s7:#9085e9;--band:rgba(255,255,255,.08);""")
rep("""body.light-theme .a3d-clb{--surf:#fcfcfb;--page:#f1f0ec;--ink:#0b0b0b;--ink2:#52514e;--muted:#898781;--grid:#e1e0d9;--base:#c3c2b7;--ring:rgba(11,11,11,.10);
  --s1:#2a78d6;--s2:#eb6834;--s3:#1baf7a;--s4:#eda100;--band:rgba(11,11,11,.07);""",
    """body.light-theme .a3d-clb{--surf:#fcfcfb;--page:#f1f0ec;--ink:#0b0b0b;--ink2:#52514e;--muted:#898781;--grid:#e1e0d9;--base:#c3c2b7;--ring:rgba(11,11,11,.10);
  --s1:#2a78d6;--s2:#eb6834;--s3:#1baf7a;--s4:#eda100;--s5:#e87ba4;--s6:#008300;--s7:#6250d6;--band:rgba(11,11,11,.07);""")
rep("""    --s1:#2a78d6;--s2:#eb6834;--s3:#1baf7a;--s4:#eda100;--band:rgba(11,11,11,.07);
    --w1:#86b6ef;--w2:#5598e7;--w3:#2a78d6;--w4:#1c5cab;--w5:#104281;--hn:#e7e5df;color-scheme:light}
  .a3d-clb-bar,.a3d-clb-tip{display:none!important}""",
    """    --s1:#2a78d6;--s2:#eb6834;--s3:#1baf7a;--s4:#eda100;--s5:#e87ba4;--s6:#008300;--s7:#6250d6;--band:rgba(11,11,11,.07);
    --w1:#86b6ef;--w2:#5598e7;--w3:#2a78d6;--w4:#1c5cab;--w5:#104281;--hn:#e7e5df;color-scheme:light}
  .a3d-clb-bar,.a3d-clb-tip{display:none!important}""")
rep(""".a3d-clb-notes{margin:16px 0 0;""", """/* __acad3dV161: the Access and people board */
.a3d-acc-kh{grid-column:1/-1;font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);font-weight:600;margin:2px 0 -4px}
.a3d-acc-sec{grid-column:1/-1;font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--ink2);font-weight:650;margin:10px 0 -2px;padding-top:8px;border-top:1px solid var(--ring)}
.a3d-acc-sec:first-child{border-top:0;padding-top:0;margin-top:0}
.a3d-acc-warn{margin:0 0 14px;padding:9px 12px;border-radius:9px;background:var(--surf);border:1px solid var(--ring);border-left:3px solid var(--warning);font-size:12.5px;color:var(--ink2)}
.a3d-acc-mk{display:inline-block;width:11px;height:11px;border:1.5px solid var(--ink);background:var(--surf);box-sizing:border-box;flex:none}
.a3d-acc-mk.rl{border-radius:50%}
.a3d-acc-mk.lt{width:15px;height:15px;border-radius:50%;border:1.2px solid var(--ink2);font-size:9.5px;line-height:12.5px;text-align:center;font-weight:650;color:var(--ink)}
.a3d-acc-ft td.n{white-space:nowrap;font-variant-numeric:tabular-nums}
.a3d-acc-col{grid-column:span 5;display:flex;flex-direction:column;gap:12px;min-width:0}
.a3d-acc-col>.a3d-clb-card{flex:1 1 auto}
.a3d-acc-nt{width:100%;border-collapse:collapse;font-size:12px;font-variant-numeric:tabular-nums;margin-top:8px}
.a3d-acc-nt td{padding:4px 6px;border-bottom:1px solid var(--grid);vertical-align:top}
.a3d-acc-nt td.k{color:var(--ink2);white-space:nowrap}
.a3d-acc-nt td.n{text-align:right;white-space:nowrap;font-weight:600}
.a3d-acc-nt td small{display:block;color:var(--muted);font-size:11px}
@media(max-width:1100px){.a3d-acc-col{grid-column:span 6}}
@media(max-width:760px){.a3d-acc-col{grid-column:span 12}}
.a3d-clb-notes{margin:16px 0 0;""")

BOARD = r"""
  /* ================= __acad3dV161: the Access and people board =================
     reference/research-access-people.md (8). Every figure is titled with its finding and has its
     source and its table; the people's figures carry their margins of error. */
  var BIM_ACC_LETTER={food:'F',health:'H',learn:'L',parks:'P',eat:'E',services:'S',community:'C'};
  var BIM_ACC_SHORT={food:'Food',health:'Health',learn:'Learning',parks:'Parks, play',eat:'Eating out',services:'Banks, post',community:'Community'};
  var BIM_ACC_WCOL=['var(--w5)','var(--w3)','var(--w1)','var(--grid)'];
  var BIM_ACC_COMMUTE=[['Drove alone',['drv']],['Carpooled',['cpl']],['Transit',['trn']],['Walked',['wlk']],['Bicycle',['bik']],['Other',['txi','mcy','oth']],['Worked from home',['wfh']]];
  var BIM_ACC_SLOT=['var(--s1)','var(--s2)','var(--s3)','var(--s4)','var(--s5)','var(--s6)','var(--s7)'];   /* the categorical slots, in their fixed order */
  var BIM_ACC_GEO_LABEL={tract:'Tract',county:'County',state:'State'};
  /* model plan metres to east and north, so every map is drawn north up */
  function bimAccEN(x,z){var t=bimTrueNorthDeg()*BIM_D2R,c=Math.cos(t),s=Math.sin(t);return [x*c+z*s,x*s-z*c];}
  /* the frame that holds box [e0, n0, e1, n1] in W by H at one scale, m from the edges */
  function bimAccFrame(b,W,H,m){
    var w=Math.max(b[2]-b[0],1),h=Math.max(b[3]-b[1],1),k=Math.min((W-2*m)/w,(H-2*m)/h),ox=(W-k*w)/2,oy=(H-k*h)/2;
    return {k:k,X:function(e){return bimClbF(ox+(e-b[0])*k);},Y:function(n){return bimClbF(oy+(b[3]-n)*k);}};
  }
  /* paths by key, a run that carries on from where the last piece ended drawn as one line */
  function bimAccPaths(){
    var P={},last={};
    return {add:function(key,x1,y1,x2,y2){
      var s=P[key]||'',l=last[key];
      if(l&&Math.abs(l[0]-x1)<0.06&&Math.abs(l[1]-y1)<0.06)s+='L'+x2+' '+y2;else s+='M'+x1+' '+y1+'L'+x2+' '+y2;
      P[key]=s;last[key]=[x2,y2];
    },get:function(key){return P[key]||'';}};
  }
  function bimAccMinShort(t){return t<0.5?'<1 min':Math.round(t)+' min';}
  /* a label beside a mark, to its right, or its left where it would leave the frame; kept inside */
  function bimAccLabel(x,y,txt,W,H){
    var w=String(txt).length*6.7,right=x+9+w<=W-4,X=right?x+9:Math.max(4+w,x-9),Y=Math.max(14,Math.min(H-6,y-7));
    return '<text class="lb" x="'+bimClbF(X)+'" y="'+bimClbF(Y)+'"'+(right?'':' text-anchor="end"')+'>'+bimClbE(txt)+'</text>';
  }
  /* the frontage in words: "Market Street, an arterial; an alley; and 5th Street, a collector" */
  var BIM_ACC_ARTICLE={arterial:'an arterial',collector:'a collector','local':'a local street',alley:'an alley','service road':'a service road','pedestrian street':'a pedestrian street',path:'a path'};
  function bimAccFrontPhrase(fs){
    var L=fs.slice(0,3).map(function(f){var c=bimAccStreetClass(f),a=BIM_ACC_ARTICLE[c]||c;return f.n?f.n+', '+a:(f.c==='s'||f.hw==='pedestrian'?a:'an unnamed '+c+' street');});
    if(fs.length>3)L.push((fs.length-3)+' more');
    return L.length>1?L.slice(0,-1).join('; ')+'; and '+L[L.length-1]:L[0];
  }
  function bimAccIsRail(s){return s.m.indexOf('metro')>=0||s.m.indexOf('rail')>=0||s.m.indexOf('light')>=0;}
  function bimAccModesText(s){return s.m.map(function(m){return BIM_ACC_MODES[m];}).join(', ');}
  function bimAccLinesText(s,n){var L=s.l.map(function(l){return l[1];});return n&&L.length>n?L.slice(0,n).join(' · ')+' +'+(L.length-n):L.join(' · ');}
  function bimAccCut(s,n){s=String(s||'');return s.length>n?s.slice(0,Math.max(1,n-1))+'…':s;}
  /* a scale bar of a round length, about a fifth of the width */
  function bimAccScaleBar(F,W,H,y){
    var want=W*0.2/F.k,L=[25,50,100,200,250,500,1000,2000,5000],len=L[0],i;
    for(i=0;i<L.length;i++)if(L[i]<=want)len=L[i];
    var px=bimClbF(len*F.k),x0=12,yy=y||H-14;
    return '<g aria-hidden="true"><rect x="'+(x0-6)+'" y="'+(yy-20)+'" width="'+bimClbF(px+30)+'" height="26" rx="5" fill="var(--surf)" opacity=".86"/><rect x="'+x0+'" y="'+(yy-4)+'" width="'+bimClbF(px/2)+'" height="4" fill="var(--ink)"/><rect x="'+bimClbF(x0+px/2)+'" y="'+(yy-4)+'" width="'+bimClbF(px/2)+'" height="4" fill="var(--surf)" stroke="var(--ink)" stroke-width="1"/>'+
      '<text class="tk" x="'+x0+'" y="'+(yy-8)+'">0</text><text class="tk" x="'+bimClbF(x0+px)+'" y="'+(yy-8)+'" text-anchor="middle">'+(len>=1000?(len/1000)+' km':len+' m')+'</text></g>';
  }
  function bimAccNorth(W){return '<g aria-hidden="true" transform="translate('+(W-22)+',16)"><rect x="-11" y="-14" width="22" height="36" rx="5" fill="var(--surf)" opacity=".86"/><path d="M0 -10L6 6L0 2L-6 6Z" fill="var(--ink)"/><text class="tk" x="0" y="17" text-anchor="middle" style="font-weight:600">N</text></g>';}
  function bimAccLotPoly(S,F,cls){
    if(!S.lot.ring){var c=bimAccEN(0,0);return '<circle cx="'+F.X(c[0])+'" cy="'+F.Y(c[1])+'" r="5" fill="var(--ink)" stroke="var(--surf)" stroke-width="2"/>';}
    return '<polygon points="'+S.lot.ring.map(function(p){var q=bimAccEN(p[0],p[1]);return F.X(q[0])+','+F.Y(q[1]);}).join(' ')+'" fill="var(--ink)" stroke="var(--surf)" stroke-width="1.5"'+(cls?' class="'+cls+'"':'')+'/>';
  }
  function bimAccLotCentre(S){
    var r=S.lot.ring,i,a=0,cx=0,cz=0;
    if(!r)return [0,0];
    for(i=0;i<r.length;i++){var p=r[i],q=r[(i+1)%r.length],f=p[0]*q[1]-q[0]*p[1];a+=f;cx+=(p[0]+q[0])*f;cz+=(p[1]+q[1])*f;}
    if(Math.abs(a)<1e-9){r.forEach(function(p){cx+=p[0];cz+=p[1];});return [cx/r.length,cz/r.length];}
    return [cx/(3*a),cz/(3*a)];
  }
  /* Fig. 1: the walk-time map */
  function bimAccWalkMapSvg(S){
    var nw=A3D_CLB.narrow,W=nw?360:760,H=nw?380:560,b=[Infinity,Infinity,-Infinity,-Infinity],wd={a:2.6,c:2.2,l:1.7,s:1.1,p:1.2},s,i;
    function ext(x,z){var p=bimAccEN(x,z);if(p[0]<b[0])b[0]=p[0];if(p[1]<b[1])b[1]=p[1];if(p[0]>b[2])b[2]=p[0];if(p[1]>b[3])b[3]=p[1];}
    S.segs.forEach(function(g){for(var j=1;j+2<g.length;j+=3)if(g[j+2]<=S.bands[2])ext(g[j],g[j+1]);});
    (S.lot.ring||[[0,0]]).forEach(function(p){ext(p[0],p[1]);});
    var pad=Math.max(b[2]-b[0],b[3]-b[1])*0.04+20;
    b=[b[0]-pad,b[1]-pad,b[2]+pad,b[3]+pad];
    var F=bimAccFrame(b,W,H,6),pb=bimAccPaths();
    S.segs.forEach(function(g){
      var c=g[0];
      for(var j=4;j+2<g.length;j+=3)bimAccSplitBands(g[j-3],g[j-2],g[j-1],g[j],g[j+1],g[j+2],function(bd,x1,z1,x2,z2){var p=bimAccEN(x1,z1),q=bimAccEN(x2,z2);pb.add(bd+c,F.X(p[0]),F.Y(p[1]),F.X(q[0]),F.Y(q[1]));});
    });
    s='<svg viewBox="0 0 '+W+' '+H+'" role="img" aria-label="Walk-time map: the streets reached in 5, 10 and 15 minutes" style="overflow:hidden" data-accmap="walk">';
    [3,2,1,0].forEach(function(bd){['p','s','l','c','a'].forEach(function(c){var d=pb.get(bd+c);if(!d)return;
      s+='<path d="'+d+'" fill="none" stroke="'+BIM_ACC_WCOL[bd]+'" stroke-width="'+(bd===3?Math.max(1,wd[c]-0.6):wd[c])+'" stroke-linecap="round" stroke-linejoin="round"'+(c==='p'?' stroke-dasharray="3 2.5"':'')+' data-band="'+bd+'" data-cls="'+c+'"/>';});});
    var cc=bimAccEN.apply(null,bimAccLotCentre(S)),cx=F.X(cc[0]),cy=F.Y(cc[1]);
    [400,800].forEach(function(r){var rp=bimClbF(r*F.k);
      s+='<circle cx="'+cx+'" cy="'+cy+'" r="'+rp+'" fill="none" stroke="var(--muted)" stroke-width="1" stroke-dasharray="5 4" data-crow="'+r+'"/>'+
        '<text class="tk" x="'+bimClbF(cx+rp*0.707+3)+'" y="'+bimClbF(cy-rp*0.707-3)+'">'+r+' m</text>';});
    s+=bimAccLotPoly(S,F);
    var lab=[];
    S.places.forEach(function(p){
      var q=p.near[0];if(!q||q.t>S.bands[2])return;
      var e=bimAccEN(q.x,q.z),K=bimAccKind(p.k);
      s+='<g class="mk"'+bimClbTip((q.n||K.sub[q.sub])+'|'+K.sub[q.sub]+' · '+K.name+'|'+bimAccMin(q.t)+' on foot; '+bimClimInt(q.d)+' m as the crow flies')+' data-accplace="'+p.k+'">'+
        '<circle cx="'+F.X(e[0])+'" cy="'+F.Y(e[1])+'" r="7.5" fill="var(--surf)" stroke="var(--ink2)" stroke-width="1.2"/>'+
        '<text x="'+F.X(e[0])+'" y="'+bimClbF(F.Y(e[1])+3.6)+'" text-anchor="middle" style="font-size:10px;font-weight:650;fill:var(--ink)">'+BIM_ACC_LETTER[p.k]+'</text></g>';
    });
    S.stops.forEach(function(st,j){
      if(st.t>S.bands[2])return;
      var e=bimAccEN(st.x,st.z),X=F.X(e[0]),Y=F.Y(e[1]),rl=bimAccIsRail(st),tip=bimClbTip(st.n+'|'+bimAccModesText(st)+(st.l.length?': '+bimAccLinesText(st):'')+'|'+bimAccMin(st.t)+' on foot; '+bimClimInt(st.d)+' m as the crow flies');
      s+=rl?'<g class="mk"'+tip+' data-accstop="'+j+'"><circle cx="'+X+'" cy="'+Y+'" r="5.5" fill="var(--surf)" stroke="var(--ink)" stroke-width="1.6"/><circle cx="'+X+'" cy="'+Y+'" r="2" fill="var(--ink)"/></g>':
        '<rect class="mk" x="'+bimClbF(X-4)+'" y="'+bimClbF(Y-4)+'" width="8" height="8" fill="var(--surf)" stroke="var(--ink)" stroke-width="1.6"'+tip+' data-accstop="'+j+'"/>';
      if(j===S.bus||j===S.rail)lab.push([X,Y,bimAccCut(st.n,nw?18:28)+' · '+bimAccMinShort(st.t)]);
    });
    lab.forEach(function(l){s+=bimAccLabel(l[0],l[1],l[2],W,H);});
    return s+bimAccNorth(W)+bimAccScaleBar(F,W,H)+'</svg>';
  }
  /* the minutes axis shared by Figs. 2 and 3: the bands shaded as the map's */
  function bimAccMinAxis(x,T0,y1,mx){
    var s='';
    [[0,5,'var(--w5)',0.18],[5,10,'var(--w3)',0.13],[10,15,'var(--w1)',0.1]].forEach(function(b){s+='<rect x="'+x(b[0])+'" y="'+(T0-6)+'" width="'+bimClbF(x(b[1])-x(b[0]))+'" height="'+bimClbF(y1-T0+6)+'" fill="'+b[2]+'" opacity="'+b[3]+'"/>';});
    [0,5,10,15,20].forEach(function(t){if(t>mx)return;s+='<line class="gd" x1="'+x(t)+'" x2="'+x(t)+'" y1="'+(T0-6)+'" y2="'+bimClbF(y1)+'"/><text class="tk" x="'+x(t)+'" y="'+(T0-10)+'" text-anchor="middle">'+t+'</text>';});
    return s+'<text class="tk" x="'+x(0)+'" y="'+(T0-26)+'">Minutes on foot</text>';
  }
  /* Fig. 2: daily needs, the nearest of each kind and the next ones */
  function bimAccNeedsSvg(S){
    var nw=A3D_CLB.narrow,W=nw?360:560,L=nw?84:150,R=W-(nw?72:104),T0=44,rh=32,n=S.places.length,y1=T0+n*rh-6,H=T0+n*rh+6,mx=S.maxT;
    function x(t){return bimClbF(L+Math.min(t,mx)/mx*(R-L));}
    var s='<svg viewBox="0 0 '+W+' '+H+'" role="img" aria-label="Daily needs by walk time">'+bimAccMinAxis(x,T0,y1,mx);
    s+='<text class="tk" x="'+(W-2)+'" y="'+(T0-26)+'" text-anchor="end">How many within</text><text class="tk" x="'+(W-2)+'" y="'+(T0-10)+'" text-anchor="end">5 · 10 · 15</text>';
    S.places.forEach(function(p,i){
      var K=bimAccKind(p.k),y=bimClbF(T0+i*rh+rh/2-6),q=p.near[0];
      s+='<text class="tl2" x="'+(L-10)+'" y="'+bimClbF(y+4)+'" text-anchor="end">'+bimClbE(nw?BIM_ACC_SHORT[p.k]:K.name)+'</text><line class="bs" x1="'+L+'" x2="'+R+'" y1="'+y+'" y2="'+y+'"/>';
      p.near.slice(1).forEach(function(o){s+='<circle class="mk" cx="'+x(o.t)+'" cy="'+y+'" r="3.6" fill="var(--surf)" stroke="var(--ink2)" stroke-width="1.4"'+
        bimClbTip((o.n||K.sub[o.sub])+'|'+K.sub[o.sub]+'|'+bimAccMin(o.t)+' on foot; '+bimClimInt(o.d)+' m as the crow flies')+'/>';});
      if(q){
        var qx=+x(q.t),left=qx>R-44;
        s+='<circle class="mk" cx="'+qx+'" cy="'+y+'" r="5.5" fill="var(--ink)" stroke="var(--surf)" stroke-width="2"'+bimClbTip((q.n||K.sub[q.sub])+'|Nearest '+K.name.toLowerCase()+': '+K.sub[q.sub]+'|'+bimAccMin(q.t)+' on foot; '+bimClimInt(q.d)+' m as the crow flies')+' data-accnear="'+p.k+'"/>'+
          '<text class="lb" x="'+bimClbF(qx+(left?-8:8))+'" y="'+bimClbF(y-7)+'"'+(left?' text-anchor="end"':'')+'>'+bimAccMinShort(q.t)+'</text>';
      }else s+='<text class="tk" x="'+(L+6)+'" y="'+bimClbF(y-6)+'">None within '+mx+' min</text>';
      s+='<text class="tl2" x="'+(W-2)+'" y="'+bimClbF(y+4)+'" text-anchor="end">'+p.n[0]+' · '+p.n[1]+' · '+p.n[2]+'</text>';
    });
    return s+'</svg>';
  }
  /* Fig. 3: the stops by walk time, with their lines */
  function bimAccStopsSvg(S){
    var nw=A3D_CLB.narrow,list=S.stops.slice(0,nw?8:10),W=nw?360:560,NL=nw?112:176,LW=nw?82:150,L=NL,R=W-LW-8,T0=44,rh=28,n=Math.max(1,list.length),y1=T0+n*rh-6,H=T0+n*rh+6,mx=S.maxT;
    function x(t){return bimClbF(L+Math.min(t,mx)/mx*(R-L));}
    var s='<svg viewBox="0 0 '+W+' '+H+'" role="img" aria-label="Transit stops by walk time">'+bimAccMinAxis(x,T0,y1,mx);
    s+='<text class="tk" x="'+(R+14)+'" y="'+(T0-10)+'">Lines</text>';
    if(!list.length)s+='<text class="tk" x="'+(L+6)+'" y="'+(T0+12)+'">No stop within '+mx+' minutes</text>';
    list.forEach(function(st,i){
      var y=bimClbF(T0+i*rh+rh/2-6),X=+x(st.t),rl=bimAccIsRail(st),tip=bimClbTip(st.n+'|'+bimAccModesText(st)+(st.l.length?': '+bimAccLinesText(st):'')+'|'+bimAccMin(st.t)+' on foot; '+bimClimInt(st.d)+' m as the crow flies');
      s+=(rl?'<circle cx="6" cy="'+y+'" r="4.5" fill="var(--surf)" stroke="var(--ink)" stroke-width="1.4"/><circle cx="6" cy="'+y+'" r="1.6" fill="var(--ink)"/>':'<rect x="2.5" y="'+bimClbF(y-3.5)+'" width="7" height="7" fill="var(--surf)" stroke="var(--ink)" stroke-width="1.4"/>')+
        '<text class="tl2" x="16" y="'+bimClbF(y+4)+'">'+bimClbE(bimAccCut(st.n,Math.floor((NL-26)/6.3)))+'</text><line class="bs" x1="'+L+'" x2="'+R+'" y1="'+y+'" y2="'+y+'"/>'+
        (rl?'<circle class="mk" cx="'+X+'" cy="'+y+'" r="5" fill="var(--ink)" stroke="var(--surf)" stroke-width="2"'+tip+' data-accstopdot="'+i+'"/>':'<rect class="mk" x="'+bimClbF(X-4.5)+'" y="'+bimClbF(y-4.5)+'" width="9" height="9" fill="var(--ink)" stroke="var(--surf)" stroke-width="2"'+tip+' data-accstopdot="'+i+'"/>')+
        '<text class="lb" x="'+bimClbF(X+(X>R-40?-9:9))+'" y="'+bimClbF(y-7)+'"'+(X>R-40?' text-anchor="end"':'')+'>'+bimAccMinShort(st.t)+'</text>'+
        '<text class="tl2" x="'+(R+14)+'" y="'+bimClbF(y+4)+'">'+bimClbE(bimAccCut(bimAccLinesText(st,nw?3:5)||'—',Math.floor((LW-10)/6.2)))+'</text>';
    });
    return s+'</svg>';
  }
  /* the line 400 m from the lot all round: out from its centre, ray by ray, to where the distance is r */
  function bimAccBufferPath(S,F,r){
    var L=S.lot.ring?{ring:S.lot.ring}:{ring:null,pt:[0,0]},c=bimAccLotCentre(S),out=[],a,k,lo,hi,mid;
    for(a=0;a<360;a+=4){
      var dx=Math.cos(a*BIM_D2R),dz=Math.sin(a*BIM_D2R);
      lo=0;hi=r+2000;
      for(k=0;k<26;k++){mid=(lo+hi)/2;if(bimAccLotDist(L,c[0]+mid*dx,c[1]+mid*dz)<r)lo=mid;else hi=mid;}
      var e=bimAccEN(c[0]+lo*dx,c[1]+lo*dz);
      out.push(F.X(e[0])+' '+F.Y(e[1]));
    }
    return 'M'+out.join('L')+'Z';
  }
  /* Fig. 4: the street hierarchy within 400 m, the frontage, the intersections counted */
  function bimAccStreetsSvg(S){
    var nw=A3D_CLB.narrow,W=nw?360:760,H=nw?360:540,R=S.conn.r+40,b=[Infinity,Infinity,-Infinity,-Infinity],wd={a:4.6,c:3.2,l:1.9,s:1.1,p:1.1},s;
    (S.lot.ring||[[0,0]]).forEach(function(p){var e=bimAccEN(p[0],p[1]);b=[Math.min(b[0],e[0]-R),Math.min(b[1],e[1]-R),Math.max(b[2],e[0]+R),Math.max(b[3],e[1]+R)];});
    var F=bimAccFrame(b,W,H,4),pb=bimAccPaths();
    S.segs.forEach(function(g){
      var c=g[0];
      for(var j=4;j+2<g.length;j+=3){var p=bimAccEN(g[j-3],g[j-2]),q=bimAccEN(g[j],g[j+1]);pb.add(c,F.X(p[0]),F.Y(p[1]),F.X(q[0]),F.Y(q[1]));}
    });
    s='<svg viewBox="0 0 '+W+' '+H+'" role="img" aria-label="Street hierarchy within 400 m of the lot" style="overflow:hidden" data-accmap="streets">';
    ['p','s','l','c','a'].forEach(function(c){var d=pb.get(c);if(!d)return;
      s+='<path d="'+d+'" fill="none" stroke="'+(c==='p'||c==='s'?'var(--muted)':'var(--ink2)')+'" stroke-width="'+wd[c]+'" stroke-linecap="round" stroke-linejoin="round"'+(c==='p'?' stroke-dasharray="3 2.5"':'')+' data-cls="'+c+'"/>';});
    s+='<path d="'+bimAccBufferPath(S,F,S.conn.r)+'" fill="none" stroke="var(--muted)" stroke-width="1" stroke-dasharray="5 4" data-buffer="'+S.conn.r+'"/>';
    S.conn.pts.forEach(function(p){var e=bimAccEN(p[0],p[1]);s+='<circle cx="'+F.X(e[0])+'" cy="'+F.Y(e[1])+'" r="3" fill="var(--s1)" stroke="var(--surf)" stroke-width="1" data-accix="1"/>';});
    s+=bimAccLotPoly(S,F);
    var c0=bimAccEN.apply(null,bimAccLotCentre(S));
    (S.streets||[]).forEach(function(f,i){
      var best=null,bl=-1;
      f.pcs.forEach(function(pc){
        var p=bimAccEN(pc[0],pc[1]),q=bimAccEN(pc[2],pc[3]),l=Math.sqrt((q[0]-p[0])*(q[0]-p[0])+(q[1]-p[1])*(q[1]-p[1]));
        s+='<line x1="'+F.X(p[0])+'" y1="'+F.Y(p[1])+'" x2="'+F.X(q[0])+'" y2="'+F.Y(q[1])+'" stroke="var(--s4)" stroke-width="6" stroke-linecap="butt" class="mk"'+
          bimClbTip(bimAccStreetName(f).replace(/^an? /,'')+'|'+bimAccStreetClass(f)+'|Fronts '+bimClimFmt(f.len,0)+' m of the lot')+' data-accfront="'+i+'"/>';
        if(l>bl){bl=l;best=[(p[0]+q[0])/2,(p[1]+q[1])/2];}
      });
      if(best){
        var dx=best[0]-c0[0],dy=best[1]-c0[1],dl=Math.sqrt(dx*dx+dy*dy)||1,X=+F.X(best[0])+dx/dl*16,Y=+F.Y(best[1])-dy/dl*16;
        var lt=bimAccCut(f.n||bimAccStreetClass(f),nw?16:24),lw=lt.length*6.7,an=Math.abs(dx/dl)<0.4?'middle':(dx>0?'start':'end');
        X=an==='start'?Math.min(X,W-4-lw):(an==='end'?Math.max(X,4+lw):Math.max(4+lw/2,Math.min(W-4-lw/2,X)));
        s+='<text class="lb" x="'+bimClbF(X)+'" y="'+bimClbF(Math.max(14,Math.min(H-6,Y+4)))+'" text-anchor="'+an+'">'+bimClbE(lt)+'</text>';
      }
    });
    return s+bimAccNorth(W)+bimAccScaleBar(F,W,H)+'</svg>';
  }
  /* the frontage, as a table to read: always shown */
  function bimAccFrontTable(S){
    var F=S.streets||[];
    if(!S.lot.ring)return '<p class="a3d-zn-out">Draw the property line to find the lot\'s frontage.</p>';
    if(!F.length)return '<p class="a3d-zn-out">No street faces the lot line within '+S.front+' m: access needs an easement or a private road.</p>';
    function sw(v){return {both:'Both sides',left:'One side',right:'One side',no:'None',none:'None',separate:'Mapped separately',yes:'Yes'}[v]||(v?v:'—');}
    return '<div class="a3d-clb-tw"><table class="a3d-zn-zt a3d-acc-ft" data-accfronttable="1"><thead><tr><th>Street</th><th>Class</th><th>Fronts</th><th>Speed limit</th><th>Lanes</th><th>Sidewalks</th><th>Cycleway</th></tr></thead><tbody>'+
      F.map(function(f){return '<tr><td class="it">'+bimClbE(f.n||bimAccStreetName(f).replace(/^an? /,'').replace(/^unnamed/,'Unnamed'))+'<small>'+bimClbE(f.hw+(f.ow==='yes'?', one way':''))+'</small></td><td>'+bimClbE(bimAccStreetClass(f).replace(/^./,function(c){return c.toUpperCase();}))+'</td>'+
        '<td class="n">'+bimClimFmt(f.len,0)+' m</td><td class="n">'+bimClbE(f.sp?(/^\d+$/.test(f.sp)?f.sp+' km/h':f.sp):'—')+'</td><td class="n">'+bimClbE(f.ln||'—')+'</td><td>'+bimClbE(sw(f.sw))+'</td><td>'+bimClbE(f.cy&&!/^(no|none)$/.test(f.cy)?f.cy.replace(/_/g,' '):(f.cy?'None':'—'))+'</td></tr>';}).join('')+'</tbody></table></div>'+
      '<p class="a3d-zn-out">A dash: not mapped in OpenStreetMap. Fronts: the length of the lot line that faces the street within '+S.front+' m.</p>';
  }
  /* Fig. 5: intersection density against LEED ND's thresholds, and route directness */
  var BIM_ACC_LEED=[[90,'LEED ND prerequisite'],[140,'with internal streets'],[300,'1 point'],[400,'2 points']];
  function bimAccConnSvg(S){
    var nw=A3D_CLB.narrow,W=nw?360:560,C=S.conn,L=14,R=W-14,mx=Math.max(500,Math.ceil(C.sqmi*1.15/100)*100),y0=48,yd=y0+122,H=yd+30,s,v;
    function x(q){return bimClbF(L+Math.min(q,mx)/mx*(R-L));}
    s='<svg viewBox="0 0 '+W+' '+H+'" role="img" aria-label="Intersection density against LEED ND, and route directness">';
    s+='<text class="tl2" x="'+L+'" y="14">Intersections per square mile within '+C.r+' m of the lot: <tspan style="font-weight:650;fill:var(--ink)">'+bimClimFmt(C.sqmi,0)+'</tspan></text>';
    /* the ranges, darker as they ask more: under the prerequisite, to the first point, beyond */
    s+='<rect x="'+x(0)+'" y="'+y0+'" width="'+bimClbF(x(mx)-x(0))+'" height="24" fill="var(--band)"/>'+
      '<rect x="'+x(90)+'" y="'+y0+'" width="'+bimClbF(x(mx)-x(90))+'" height="24" fill="var(--band)"/>'+
      '<rect x="'+x(300)+'" y="'+y0+'" width="'+bimClbF(x(mx)-x(300))+'" height="24" fill="var(--band)"/>';
    s+='<path class="mk" d="M'+x(0)+' '+(y0+7)+'H'+x(C.sqmi)+'V'+(y0+17)+'H'+x(0)+'Z" fill="var(--s1)"'+bimClbTip('Intersection density|'+bimClimFmt(C.sqmi,0)+' per square mile ('+bimClimFmt(C.dens,0)+' per km²)|'+C.ix+' intersections in '+bimClimFmt(C.area,2)+' km²')+' data-accdens="1"/>';
    BIM_ACC_LEED.forEach(function(t,j){
      var X=x(t[0]),up=j%2===0;
      s+='<line x1="'+X+'" x2="'+X+'" y1="'+(y0-3)+'" y2="'+(y0+27)+'" stroke="var(--ink)" stroke-width="1.5"/>'+
        '<text class="tk" x="'+X+'" y="'+(up?y0-9:y0+40)+'" text-anchor="middle">'+t[0]+(nw?'':' · '+t[1])+'</text>';
    });
    for(v=0;v<=mx;v+=100)s+='<text class="tk" x="'+x(v)+'" y="'+(y0+58)+'" text-anchor="'+(v===0?'start':(v===mx?'end':'middle'))+'">'+v+'</text>';
    var dx0=1,dx1=2.5;
    function xd(q){return bimClbF(L+(Math.min(Math.max(q,dx0),dx1)-dx0)/(dx1-dx0)*(R-L));}
    s+='<text class="tl2" x="'+L+'" y="'+(yd-30)+'">The walk over the straight line, to each place and stop</text><line class="bs" x1="'+L+'" x2="'+R+'" y1="'+yd+'" y2="'+yd+'"/>';
    [1,1.5,2,2.5].forEach(function(q){s+='<line class="gd" x1="'+xd(q)+'" x2="'+xd(q)+'" y1="'+(yd-7)+'" y2="'+(yd+7)+'"/><text class="tk" x="'+xd(q)+'" y="'+(yd+20)+'" text-anchor="'+(q===1?'start':(q===2.5?'end':'middle'))+'">'+q.toFixed(1)+(q===1?', straight':'')+'</text>';});
    (C.rats||[]).forEach(function(r){s+='<line x1="'+xd(r)+'" x2="'+xd(r)+'" y1="'+(yd-6)+'" y2="'+(yd+6)+'" stroke="var(--ink2)" stroke-width="1.2" opacity=".7"/>';});
    if(C.dir!==null)s+='<path class="mk" d="M'+xd(C.dir)+' '+(yd-8)+'l7 8-7 8-7-8z" fill="var(--s1)" stroke="var(--surf)" stroke-width="1.5"'+bimClbTip('Route directness|Median '+C.dir.toFixed(2)+' of '+C.ndir+' places and stops|The walk over the straight line; 1 is straight')+' data-accdir="1"/>'+
      bimAccLabel(+xd(C.dir),yd-4,'Median '+C.dir.toFixed(2),W,H);
    return s+'</svg>';
  }
  /* Fig. 6: the measures, the tract against its county and state */
  function bimAccCmpRows(P){
    var V=P.v||{},G=P.geo||{},geos=['tract','county','state'];
    function dens(v,g){var a=g&&g.aland;return v.pop&&v.pop[0]!==null&&a>0?[v.pop[0]/(a/1e6),v.pop[1]===null?null:v.pop[1]/(a/1e6)]:null;}
    function sh(k,tt){return function(v){return bimCenShare(v[k],v[tt]);};}
    var defs=[['Population density','per km²',dens,'int','Density'],['Median age','years',function(v){return v.age;},'1','Median age'],['Median household income','dollars',function(v){return v.inc;},'money','Income'],
      ['Household size','people',function(v){return v.hhs;},'2','Household'],['Renting','share of homes',sh('rent','ten'),'pct','Renting'],['Vacant','share of homes',sh('vac','hu'),'pct','Vacant'],
      ['No car','share of households',sh('vh0','vht'),'pct','No car'],['To work by transit','share of workers',sh('trn','wrk'),'pct','Transit'],
      ['On foot or by bike','share of workers',function(v){return bimCenShare(bimCenSum([v.wlk,v.bik]),v.wrk);},'pct','Foot or bike'],['Work from home','share of workers',sh('wfh','wrk'),'pct','From home']];
    return defs.map(function(d){
      var vals=geos.map(function(g){var r=V[g]?d[2](V[g],G[g]):null;return r&&r[0]!==null?r:null;}),T=vals[0],C=vals[1],vs=null;
      if(T&&C&&T[1]!==null&&C[1]!==null){var dd=T[0]-C[0];vs=Math.abs(dd)>Math.sqrt(T[1]*T[1]+C[1]*C[1])?(dd>0?'higher':'lower'):'same';}
      return {name:d[0],unit:d[1],fmt:d[3],short:d[4],v:vals,vs:vs};
    });
  }
  function bimAccFmtV(v,f){if(v===null||v===undefined)return '—';return f==='pct'?bimClimFmt(v*100,0)+'%':(f==='money'?'$'+bimClimInt(v):(f==='int'?bimClimInt(v):bimClimFmt(v,f==='2'?2:1)));}
  function bimAccFmtM(m,f){if(m===null||m===undefined)return '';return '± '+(f==='pct'?(m*100<1?'<1':bimClimFmt(m*100,0)):(f==='money'?'$'+bimClimInt(m):(f==='int'?bimClimInt(m):bimClimFmt(m,f==='2'?2:1))));}
  var BIM_ACC_VS={higher:'Higher than the county',lower:'Lower than the county',same:'No clear difference'};
  /* the key facts, counts with their margins, always shown */
  function bimAccFactsTable(P){
    var V=P.v,G=P.geo,geos=['tract','county','state'].filter(function(g){return V[g];});
    function c(X){return X&&X[0]!==null?bimClimInt(X[0])+(X[1]?'<small>± '+bimClimInt(X[1])+'</small>':''):'—';}
    var rows=[['People','pop'],['Households','hh'],['Homes','hu'],['Workers, 16 and over','wrk']];
    return '<div class="a3d-clb-tw"><table class="a3d-acc-nt" data-accfacts="1"><thead><tr><th style="text-align:left;color:var(--ink2);font-weight:600;padding:4px 6px">Key facts</th>'+geos.map(function(g){return '<th style="text-align:right;color:var(--ink2);font-weight:600;padding:4px 6px">'+bimClbE(A3D_CLB.narrow?BIM_ACC_GEO_LABEL[g]:(G[g].name||BIM_ACC_GEO_LABEL[g]))+'</th>';}).join('')+'</tr></thead><tbody>'+
      rows.map(function(r){return '<tr><td class="k">'+r[0]+'</td>'+geos.map(function(g){return '<td class="n">'+c(V[g][r[1]])+'</td>';}).join('')+'</tr>';}).join('')+
      '<tr><td class="k">Land area, km²</td>'+geos.map(function(g){return '<td class="n">'+(G[g].aland>0?(G[g].aland<1e8?bimClimFmt(G[g].aland/1e6,2):bimClimInt(G[g].aland/1e6)):'—')+'</td>';}).join('')+'</tr></tbody></table></div>';
  }
  function bimAccCompareSvg(rows,P){
    var nw=A3D_CLB.narrow,W=nw?360:760,L=nw?104:180,RW=nw?78:150,R=W-RW-12,T0=12,rh=nw?38:38,H=T0+rows.length*rh+4,s,G=P.geo;
    s='<svg viewBox="0 0 '+W+' '+H+'" role="img" aria-label="The tract against its county and state">';
    rows.forEach(function(r,i){
      var y=bimClbF(T0+i*rh+rh/2-2),lo=Infinity,hi=-Infinity;
      r.v.forEach(function(v){if(!v)return;var m=v[1]||0;lo=Math.min(lo,v[0]-m);hi=Math.max(hi,v[0]+m);});
      s+='<text class="tl2" x="'+(L-10)+'" y="'+bimClbF(y-1)+'" text-anchor="end">'+bimClbE(nw?r.short:r.name)+'</text><text class="tk" x="'+(L-10)+'" y="'+bimClbF(y+11)+'" text-anchor="end">'+bimClbE(nw?r.unit.replace(/^share of /,'% of '):r.unit)+'</text>';
      s+='<line class="bs" x1="'+L+'" x2="'+R+'" y1="'+y+'" y2="'+y+'"/>';
      if(!isFinite(lo)){s+='<text class="tk" x="'+(L+6)+'" y="'+bimClbF(y-5)+'">Not available</text>';return;}
      if(r.fmt==='pct'){lo=Math.max(0,lo);hi=Math.min(1,hi);}
      var pad=(hi-lo)*0.1||Math.abs(hi)*0.1||1;lo-=pad;hi+=pad;
      function x(v){return bimClbF(L+(v-lo)/(hi-lo)*(R-L));}
      var T=r.v[0],C=r.v[1],St=r.v[2];
      if(St)s+='<rect class="mk" x="'+bimClbF(+x(St[0])-4)+'" y="'+bimClbF(y-4)+'" width="8" height="8" fill="var(--surf)" stroke="var(--muted)" stroke-width="1.6"'+bimClbTip(G.state.name+'|'+r.name+': '+bimAccFmtV(St[0],r.fmt)+' '+bimAccFmtM(St[1],r.fmt))+' data-accgeo="state"/>';
      if(C)s+='<path class="mk" d="M'+x(C[0])+' '+bimClbF(y-5.5)+'l5.5 5.5-5.5 5.5-5.5-5.5z" fill="var(--surf)" stroke="var(--ink2)" stroke-width="1.6"'+bimClbTip(G.county.name+'|'+r.name+': '+bimAccFmtV(C[0],r.fmt)+' '+bimAccFmtM(C[1],r.fmt))+' data-accgeo="county"/>';
      if(T){
        if(T[1]!==null)s+='<line x1="'+x(Math.max(lo,T[0]-T[1]))+'" x2="'+x(Math.min(hi,T[0]+T[1]))+'" y1="'+y+'" y2="'+y+'" stroke="var(--s1)" stroke-width="3" stroke-linecap="round" opacity=".55" data-accmoe="'+i+'"/>';
        s+='<circle class="mk" cx="'+x(T[0])+'" cy="'+y+'" r="5" fill="var(--s1)" stroke="var(--surf)" stroke-width="2"'+bimClbTip(G.tract.name+'|'+r.name+': '+bimAccFmtV(T[0],r.fmt)+' '+bimAccFmtM(T[1],r.fmt)+' (90% margin)'+(r.vs?'|'+BIM_ACC_VS[r.vs]:''))+' data-accgeo="tract"/>';
      }
      s+='<text class="tl2" x="'+(R+12)+'" y="'+bimClbF(y-1)+'">'+bimClbE(T?bimAccFmtV(T[0],r.fmt)+(T[1]!==null&&!nw?' '+bimAccFmtM(T[1],r.fmt):''):'—')+'</text>'+
        '<text class="tk" x="'+(R+12)+'" y="'+bimClbF(y+11)+'">'+bimClbE(r.vs?(nw?{same:'Same',higher:'Higher',lower:'Lower'}[r.vs]:(r.vs==='same'?'No clear difference':(r.vs==='higher'?'Higher':'Lower')+' than county')):'')+'</text>';
    });
    return s+'</svg>';
  }
  /* Fig. 7: how people get to work, 100% bars */
  function bimAccCommuteShares(v){
    if(!v||!v.wrk||!(v.wrk[0]>0))return null;
    return BIM_ACC_COMMUTE.map(function(c){var S=bimCenShare(bimCenSum(c[1].map(function(k){return v[k];})),v.wrk);return S;});
  }
  function bimAccCommuteSvg(P){
    var nw=A3D_CLB.narrow,W=nw?360:560,L=nw?52:70,R=W-6,T0=6,bh=nw?24:28,gap=nw?14:16,geos=['tract','county','state'].filter(function(g){return bimAccCommuteShares(P.v[g]);}),H=T0+geos.length*(bh+gap),s;
    s='<svg viewBox="0 0 '+W+' '+H+'" role="img" aria-label="How people get to work">';
    geos.forEach(function(g,i){
      var sh=bimAccCommuteShares(P.v[g]),y=T0+i*(bh+gap),cum=0;
      s+='<text class="tl2" x="'+(L-8)+'" y="'+bimClbF(y+bh/2+4)+'" text-anchor="end">'+BIM_ACC_GEO_LABEL[g]+'</text>';
      sh.forEach(function(S,j){
        if(!S||!(S[0]>0))return;
        var x0=L+cum*(R-L),w=S[0]*(R-L);cum+=S[0];
        s+='<rect class="mk" x="'+bimClbF(x0)+'" y="'+y+'" width="'+bimClbF(Math.max(0.5,w))+'" height="'+bh+'" fill="'+BIM_ACC_SLOT[j]+'" stroke="var(--surf)" stroke-width="2"'+
          bimClbTip(P.geo[g].name+'|'+BIM_ACC_COMMUTE[j][0]+': '+bimCenPct(S))+' data-acccom="'+g+':'+j+'"/>';
        if(w>=(nw?30:34))s+='<text class="lb" x="'+bimClbF(x0+w/2)+'" y="'+bimClbF(y+bh/2+4)+'" text-anchor="middle">'+Math.round(S[0]*100)+'%</text>';
      });
    });
    return s+'</svg>';
  }
  /* Fig. 8: the age pyramid, the county's outline over the tract's bars */
  function bimAccPyrShares(p){
    if(!p)return null;
    var tot=0,i;
    for(i=0;i<18;i++){if(p.m[i]===null||p.f[i]===null)return null;tot+=p.m[i]+p.f[i];}
    if(!(tot>0))return null;
    return {m:p.m.map(function(v){return v/tot*100;}),f:p.f.map(function(v){return v/tot*100;}),tot:tot};
  }
  function bimAccPyramidSvg(P){
    var nw=A3D_CLB.narrow,T=bimAccPyrShares(P.pyr.tract),C=bimAccPyrShares(P.pyr.county),W=nw?360:560,rh=nw?13:14.5,T0=18,n=18,gw=nw?40:52,mid=W/2,half=mid-gw/2-12,H=T0+n*rh+28,s,i,mx=0;
    for(i=0;i<n;i++){mx=Math.max(mx,T.m[i],T.f[i]);if(C)mx=Math.max(mx,C.m[i],C.f[i]);}
    var tk=bimClbTicks(0,mx,nw?2:3),top=tk[tk.length-1];
    function xm(v){return bimClbF(mid-gw/2-v/top*half);}function xf(v){return bimClbF(mid+gw/2+v/top*half);}
    function yb(j){return T0+(n-1-j)*rh;}
    s='<svg viewBox="0 0 '+W+' '+H+'" role="img" aria-label="Age and sex pyramid">';
    s+='<text class="tl2" x="'+bimClbF(mid-gw/2-4)+'" y="11" text-anchor="end">Men</text><text class="tl2" x="'+bimClbF(mid+gw/2+4)+'" y="11">Women</text>';
    tk.forEach(function(v){if(v<=0)return;s+='<line class="gd" x1="'+xm(v)+'" x2="'+xm(v)+'" y1="'+T0+'" y2="'+bimClbF(T0+n*rh)+'"/><line class="gd" x1="'+xf(v)+'" x2="'+xf(v)+'" y1="'+T0+'" y2="'+bimClbF(T0+n*rh)+'"/>'+
      '<text class="tk" x="'+xm(v)+'" y="'+bimClbF(T0+n*rh+14)+'" text-anchor="middle">'+v+'%</text><text class="tk" x="'+xf(v)+'" y="'+bimClbF(T0+n*rh+14)+'" text-anchor="middle">'+v+'%</text>';});
    for(i=0;i<n;i++){
      var y=yb(i),tip=bimClbTip('Age '+BIM_CEN_BAND_NAMES[i]+'|Men '+bimClimFmt(T.m[i],1)+'%, women '+bimClimFmt(T.f[i],1)+'% of the tract'+(C?'|County: men '+bimClimFmt(C.m[i],1)+'%, women '+bimClimFmt(C.f[i],1)+'%':''));
      s+='<rect class="mk" x="'+xm(T.m[i])+'" y="'+bimClbF(y+1)+'" width="'+bimClbF(Math.max(0.5,mid-gw/2-xm(T.m[i])))+'" height="'+bimClbF(rh-2)+'" fill="var(--s1)"'+tip+' data-accpyr="m'+i+'"/>'+
        '<rect class="mk" x="'+bimClbF(mid+gw/2)+'" y="'+bimClbF(y+1)+'" width="'+bimClbF(Math.max(0.5,xf(T.f[i])-mid-gw/2))+'" height="'+bimClbF(rh-2)+'" fill="var(--s2)"'+tip+' data-accpyr="f'+i+'"/>';
      if(!nw||i%2===0)s+='<text class="tk" x="'+mid+'" y="'+bimClbF(y+rh/2+3.5)+'" text-anchor="middle">'+BIM_CEN_BAND_NAMES[i]+'</text>';
    }
    if(C){
      var pm='',pf='';
      for(i=0;i<n;i++){var y0=yb(i)+rh,y1=yb(i);pm+=(i?'L':'M')+xm(C.m[i])+' '+bimClbF(y0)+'L'+xm(C.m[i])+' '+bimClbF(y1);pf+=(i?'L':'M')+xf(C.f[i])+' '+bimClbF(y0)+'L'+xf(C.f[i])+' '+bimClbF(y1);}
      s+='<path d="'+pm+'" fill="none" stroke="var(--ink)" stroke-width="1.5" data-acccounty="m"/><path d="'+pf+'" fill="none" stroke="var(--ink)" stroke-width="1.5" data-acccounty="f"/>';
    }
    return s+'</svg>';
  }
  /* the board */
  function bimAccBoardHtml(){
    var S=bimAccHas()?A3D.site.access:null,P=A3D.site&&A3D.site.people,st=bimSunSettings(),cards=[],fig=0,h;
    var site=(A3D.site&&A3D.site.name&&A3D.site.name!=='Site')?A3D.site.name:(bimProjectLabel()||'The site');
    var bar='<div class="a3d-clb-bar"><div class="a3d-clb-bart">Access and people</div>'+
      '<button type="button" class="a3d-clb-btn" data-clb="tables" aria-pressed="'+A3D_CLB.tables+'">Tables</button>'+
      '<button type="button" class="a3d-clb-btn a3d-clb-hide-s" data-clb="refresh">Refresh data</button>'+
      '<button type="button" class="a3d-clb-btn a3d-clb-hide-s" data-clb="print">Print</button>'+
      '<button type="button" class="a3d-clb-btn" data-clb="close" aria-label="Close the board">Close</button></div>';
    var head='<div class="a3d-clb-page"><header><div class="a3d-clb-kicker">Site analysis · 8 Access and circulation · 10 People and place</div><h1 class="a3d-clb-h1">'+bimClbE(site)+': access and people</h1>';
    if(!S&&!P)return bar+head+'</header><div class="a3d-clb-empty">No access or people data yet. The walk times, transit and daily needs come from OpenStreetMap through Overpass, and the people from the US Census Bureau (TIGERweb and the American Community Survey): free, no account.'+
      (bimSunNum(st.lat)&&bimSunNum(st.lon)?'':' Set the site latitude and longitude first (Properties, Site, Location).')+
      '<div style="margin-top:12px"><button type="button" class="a3d-clb-btn pri" data-clb="refresh">Get access and people</button></div></div></div>';
    var lat=S?S.lat:P.lat,lon=S?S.lon:P.lon,sub=[Math.abs(lat).toFixed(4)+'° '+(lat<0?'S':'N')+', '+Math.abs(lon).toFixed(4)+'° '+(lon<0?'W':'E')],hasP=P&&!P.outside&&P.v&&P.v.tract;
    if(S)sub.push('walking at '+bimClimFmt(S.speed*0.06,1)+' km/h from the '+(S.lot.ring?'lot':'site point')+' · OpenStreetMap data of '+S.fetched);
    if(hasP)sub.push(P.geo.tract.name+(P.geo.county.name?', '+P.geo.county.name:'')+' · ACS '+(P.year-4)+'–'+P.year);
    head+='<p class="a3d-clb-sub">'+bimClbE(sub.join(' · '))+'</p></header>';
    var warn=S?bimAccStaleText(S):'';
    h=bar+head+(warn?'<div class="a3d-acc-warn" role="note">'+bimClbE(warn)+'</div>':'');
    /* the indicators, access then the people */
    var ka=[],kq=[];
    if(S){
      var w10=S.places.filter(function(p){return p.near.length&&p.near[0].t<=10;}).length,w15=S.places.filter(function(p){return p.near.length&&p.near[0].t<=15;}).length,nb=S.bus>=0?S.stops[S.bus]:null,nr=S.rail>=0?S.stops[S.rail]:null,C=S.conn;
      ka.push(bimClbKpi('Daily needs',w10+' of '+S.places.length,'','Kinds within a 10-minute walk; '+w15+' within 15',w10>=6?'good':(w10>=4?'warning':(w10>=2?'serious':'critical'))));
      ka.push(nb?bimClbKpi('Nearest bus or tram',nb.t<0.5?'<1':String(Math.round(nb.t)),'min',bimAccCut(nb.n,34)+(nb.l.length?' · '+bimAccLinesText(nb,3):''),nb.t<=5?'good':(nb.t<=10?'warning':'serious')):
        bimClbKpi('Nearest bus or tram','None','','Within a '+S.maxT+'-minute walk','serious'));
      ka.push(nr?bimClbKpi('Nearest rail or metro',nr.t<0.5?'<1':String(Math.round(nr.t)),'min',bimAccCut(nr.n,34)+(nr.l.length?' · '+bimAccLinesText(nr,3):''),nr.t<=10?'good':'warning'):
        bimClbKpi('Nearest rail or metro','None','','Within a '+S.maxT+'-minute walk'));
      ka.push(bimClbKpi('Lines within 10 min',String(S.lines10),'',S.stops.filter(function(x){return x.t<=10;}).length+' stops; OpenStreetMap, no timetables'));
      ka.push(bimClbKpi('Intersections',bimClimFmt(C.dens,0),'per km²',bimClimFmt(C.sqmi,0)+' per sq mi within '+C.r+' m; LEED ND asks 90',C.sqmi>=140?'good':(C.sqmi>=90?'warning':'serious')));
    }
    if(hasP){
      var V=P.v.tract,Cv=P.v.county||null,dn=bimCenDens(V.pop,P.geo.tract.aland),rent=bimCenShare(V.rent,V.ten),nv=bimCenShare(V.vh0,V.vht);
      kq.push(bimClbKpi('Population',bimCenFmt(V.pop[0],0),'',(V.pop[1]!==null?'± '+bimClimInt(V.pop[1]):'')+(dn!==null?' · '+bimClimInt(dn)+' per km²':'')));
      kq.push(bimClbKpi('Median age',bimCenFmt(V.age[0],1),'years',(V.age[1]!==null?'± '+bimClimFmt(V.age[1],1):'')+(Cv&&Cv.age[0]!==null?' · county '+bimClimFmt(Cv.age[0],1):'')));
      kq.push(bimClbKpi('Household income',V.inc[0]!==null?'$'+bimClimInt(V.inc[0]):'—','median',(V.inc[1]!==null?'± $'+bimClimInt(V.inc[1]):'')+(Cv&&Cv.inc[0]!==null?' · county $'+bimClimInt(Cv.inc[0]):'')));
      kq.push(bimClbKpi('Renting',rent?bimClimFmt(rent[0]*100,0):'—','%',(rent&&rent[1]!==null?'± '+bimClimFmt(rent[1]*100,0)+' · ':'')+bimClimInt(V.ten[0]||0)+' occupied homes'));
      kq.push(bimClbKpi('No car',nv?bimClimFmt(nv[0]*100,0):'—','%',(nv&&nv[1]!==null?'± '+bimClimFmt(nv[1]*100,0)+' · ':'')+'of households'+(Cv&&bimCenShare(Cv.vh0,Cv.vht)?'; county '+bimClimFmt(bimCenShare(Cv.vh0,Cv.vht)[0]*100,0)+'%':'')));
    }
    if(ka.length)h+='<div class="a3d-acc-kh">Access and circulation</div><section class="a3d-clb-kpis" aria-label="Access indicators" style="--n:'+ka.length+'">'+ka.join('')+'</section>';
    if(kq.length)h+='<div class="a3d-acc-kh">People and place · '+bimClbE(P.geo.tract.name)+'</div><section class="a3d-clb-kpis" aria-label="People indicators" style="--n:'+kq.length+'">'+kq.join('')+'</section>';
    h+='<section class="a3d-clb-grid">';
    if(S){
      var R=S.reach.len,k10=R[0]+R[1],src=S.src+', data of '+S.fetched+'; walk times worked out in this app',f1,f2,f3,f4,f5;
      var miss=S.places.filter(function(p){return !p.near.length;}).map(function(p){return bimAccKind(p.k).name.toLowerCase();});
      var inBand=function(t,j){return j===0?t<=5:(j===1?t>5&&t<=10:(j===2?t>10&&t<=15:t>15&&t<=20));};
      cards.push('<h2 class="a3d-acc-sec">8 · Access and circulation</h2>');
      f1=bimClbCard('s7',++fig,'A 10-minute walk reaches '+bimAccKm(k10)+' of streets and '+w10+' of '+S.places.length+' daily needs',
        'Along the streets from the '+(S.lot.ring?'lot':'site point')+' at '+S.speed+' m a minute, as rings of 5, 10 and 15 minutes; 15 to 20 minutes in grey. Dashed circles: 400 and 800 m as the crow flies. Letters: the nearest of each daily need.',
        '<div class="a3d-clb-chart">'+bimAccWalkMapSvg(S)+'</div>'+
        bimClbLeg([['var(--w5)','5 min or less','ln'],['var(--w3)','5 to 10 min','ln'],['var(--w1)','10 to 15 min','ln'],['var(--grid)','15 to 20 min','ln']])+
        '<div class="a3d-clb-legend"><span><i class="a3d-acc-mk" style="border-radius:1px"></i>Bus or tram stop</span><span><i class="a3d-acc-mk rl"></i>Rail or metro</span><span><i style="background:var(--ink)"></i>The '+(S.lot.ring?'lot':'site')+'</span>'+
        BIM_ACC_KINDS.map(function(K){return '<span><i class="a3d-acc-mk lt">'+BIM_ACC_LETTER[K.id]+'</i>'+bimClbE(BIM_ACC_SHORT[K.id])+'</span>';}).join('')+'</div>'+
        bimClbTable(['Walk','Streets and paths (km)','Daily-needs places','Stops'],['5 min or less','5 to 10 min','10 to 15 min','15 to 20 min'].map(function(lbl,j){
          var np=0;S.places.forEach(function(p){p.near.forEach(function(q){if(inBand(q.t,j))np++;});});
          return [lbl,bimClimFmt(R[j],2),np,S.stops.filter(function(x){return inBand(x.t,j);}).length];})),src);
      var nearest=S.places.filter(function(p){return p.near.length;}).sort(function(a,b){return a.near[0].t-b.near[0].t;});
      f2=bimClbCard('s5',++fig,w10+' of '+S.places.length+' daily needs within a 10-minute walk'+(miss.length?'; no '+miss.join(' or ')+' within '+S.maxT+' minutes':(nearest.length?'; the farthest, '+bimAccKind(nearest[nearest.length-1].k).name.toLowerCase()+', '+bimAccMinShort(nearest[nearest.length-1].near[0].t):'')),
        'The nearest of each kind (solid, with its minutes) and the next ones (open), along the streets; at right, how many within 5, 10 and 15 minutes. The kinds follow the 15-minute city\'s functions; this is not a Walk Score.',
        '<div class="a3d-clb-chart">'+bimAccNeedsSvg(S)+'</div>'+bimClbLeg([['var(--w5)','5 min or less'],['var(--w3)','5 to 10'],['var(--w1)','10 to 15']])+
        '<table class="a3d-acc-nt" data-accnearest="1"><tbody>'+S.places.map(function(p){var K=bimAccKind(p.k),q=p.near[0];
          return '<tr><td class="k">'+bimClbE(K.name)+'</td><td>'+(q?bimClbE(q.n||'Unnamed')+'<small>'+bimClbE(K.sub[q.sub])+'</small>':'<small>None within '+S.maxT+' minutes</small>')+'</td><td class="n">'+(q?bimAccMinShort(q.t):'—')+'</td></tr>';}).join('')+'</tbody></table>'+
        bimClbTable(['Kind','Nearest','Place','Minutes','Metres','In 5','In 10','In 15','In 20'],S.places.map(function(p){var K=bimAccKind(p.k),q=p.near[0];
          return [K.name,q?(q.n||'Unnamed'):'None within '+S.maxT+' min',q?K.sub[q.sub]:'',q?bimClimFmt(q.t,1):'',q?q.d:'',p.n[0],p.n[1],p.n[2],p.n[3]];})),src);
      var fs=S.streets||[];
      f3=bimClbCard('s7',++fig,!S.lot.ring?'The streets within '+S.conn.r+' m of the site: draw the property line for its frontage':
        (fs.length?'The lot fronts '+bimAccFrontPhrase(fs):'No street faces the lot line within '+S.front+' m'),
        'Within '+S.conn.r+' m of the lot: streets by functional class (OpenStreetMap\'s highway tags crosswalked to the FHWA classes, approximately), the heaviest the arterials; paths dashed; the frontage in amber; the intersections counted for connectivity as dots.',
        '<div class="a3d-clb-chart">'+bimAccStreetsSvg(S)+'</div>'+
        bimClbLeg([['var(--ink2)','Arterial, collector, local (by weight)','ln'],['var(--muted)','Service road or path','ln'],['var(--s4)','Frontage'],['var(--s1)','Intersection counted']])+bimAccFrontTable(S)+
        bimClbTable(['Class','Within 5 min (km)','5 to 10','10 to 15','15 to 20'],['a','c','l','s','p'].filter(function(c){return S.reach.cls[c];}).map(function(c){return [BIM_ACC_CLASS_NAME[c]].concat(S.reach.cls[c].map(function(v){return bimClimFmt(v,2);}));})),src);
      var nb2=S.bus>=0?S.stops[S.bus]:null,nr2=S.rail>=0?S.stops[S.rail]:null;
      f4=bimClbCard('s5',++fig,(nb2?'The nearest bus or tram stop is '+(nb2.t<0.5?'under a minute':bimAccMin(nb2.t))+' away':'No bus or tram stop within a '+S.maxT+'-minute walk')+'; '+bimSaN(S.lines10,'line')+' within 10 minutes',
        (nr2?'The nearest rail or metro station, '+nr2.n+', is '+bimAccMin(nr2.t)+' away. ':'No rail or metro station within '+S.maxT+' minutes. ')+'Stops by walk time; a stop\'s sides and a station\'s entrances count as one. OpenStreetMap holds the stops and lines, not timetables: how often each runs needs the operator\'s GTFS feed.',
        '<div class="a3d-clb-chart">'+bimAccStopsSvg(S)+'</div>'+
        '<div class="a3d-clb-legend"><span><i class="a3d-acc-mk" style="border-radius:1px"></i>Bus or tram</span><span><i class="a3d-acc-mk rl"></i>Rail or metro</span></div>'+
        bimClbTable(['Stop','Modes','Lines','Minutes','Metres'],S.stops.map(function(x){return [x.n,bimAccModesText(x),bimAccLinesText(x)||'—',bimClimFmt(x.t,1),x.d];})),src);
      var C2=S.conn,lv=C2.sqmi>=400?'above LEED ND\'s top threshold':(C2.sqmi>=300?'earns LEED ND\'s connectivity point':(C2.sqmi>=90?'meets LEED ND\'s prerequisite':'below LEED ND\'s prerequisite of 90 per square mile'));
      f5=bimClbCard('s5',++fig,bimClimFmt(C2.dens,0)+' intersections per km² ('+bimClimFmt(C2.sqmi,0)+' per square mile): '+lv,
        'Intersections of streets and paths within '+C2.r+' m of the lot, as LEED ND v4 counts them: junctions that lead only to dead ends left out, a divided road\'s crossing counted once. Below: the walk over the straight line for each place and stop 150 m or more away.',
        '<div class="a3d-clb-chart">'+bimAccConnSvg(S)+'</div>'+
        bimClbTable(['Measure','Value'],[['Intersections within '+C2.r+' m',C2.ix],['The area (the lot and '+C2.r+' m around), km²',bimClimFmt(C2.area,3)],['Per km²',bimClimFmt(C2.dens,1)],['Per square mile',bimClimFmt(C2.sqmi,1)]].concat(
          BIM_ACC_LEED.map(function(t){return ['LEED ND: '+t[1],t[0]+' per sq mi'];})).concat([['Route directness (median)',C2.dir===null?'Too few places':C2.dir.toFixed(2)],['Places and stops measured',C2.ndir]])),src+'; LEED ND v4 Neighborhood Pattern and Design');
      cards.push(f1,f2,f3,'<div class="a3d-acc-col">'+f4+f5+'</div>');
    }else cards.push('<h2 class="a3d-acc-sec">8 · Access and circulation</h2><div class="a3d-clb-card"><div class="a3d-clb-empty">The walk times are not available'+(P&&P.errors&&P.errors.length?': '+bimClbE(P.errors.join('; ')):'')+'. Refresh data to try again.</div></div>');
    if(P){
      cards.push('<h2 class="a3d-acc-sec">10 · People and place</h2>');
      if(!hasP)cards.push('<div class="a3d-clb-card"><div class="a3d-clb-empty">'+(P.outside?'The census figures cover sites in the United States (the American Community Survey). Elsewhere, the national statistics office publishes the equivalent, such as the ONS in the UK, the ABS in Australia or Statistics Canada.':'The census figures are not available.')+'</div></div>');
      else{
        var rows=bimAccCmpRows(P),G=P.geo,psrc=P.src+'; geography and land area from TIGERweb',diff=rows.filter(function(r){return r.vs==='higher'||r.vs==='lower';}),tested=rows.filter(function(r){return r.vs;}).length,big=null,bd=0,f6,col='';
        diff.forEach(function(r){var a=r.v[0][0],b=r.v[1][0],q=Math.abs(a-b)/Math.max(Math.abs(b),1e-9);if(q>bd){bd=q;big=r;}});
        f6=bimClbCard('s7',++fig,big?G.tract.name+': '+big.name.toLowerCase()+' '+bimAccFmtV(big.v[0][0],big.fmt)+' against '+bimAccFmtV(big.v[1][0],big.fmt)+' in the county; '+diff.length+' of '+tested+' measures differ beyond the margins of error':
          G.tract.name+': no measure differs from the county beyond the margins of error',
          'Each measure on its own scale: the tract (dot) with its 90% margin of error (bar), its county (diamond) and its state (square). A difference counts only where it is larger than the two margins together (the Census Bureau\'s test at 90%).',
          '<div class="a3d-clb-chart">'+bimAccCompareSvg(rows,P)+'</div>'+
          '<div class="a3d-clb-legend"><span><i style="background:var(--s1);border-radius:50%"></i>'+bimClbE(G.tract.name)+', with its margin</span><span><i style="background:var(--surf);border:1.5px solid var(--ink2);transform:rotate(45deg) scale(.8)"></i>'+bimClbE(G.county.name||'County')+'</span><span><i style="background:var(--surf);border:1.5px solid var(--muted)"></i>'+bimClbE(G.state.name||'State')+'</span></div>'+
          bimAccFactsTable(P)+
          bimClbTable(['Measure','Tract','Margin','County','State','Against the county'],rows.map(function(r){return [r.name+' ('+r.unit+')',r.v[0]?bimAccFmtV(r.v[0][0],r.fmt):'—',r.v[0]?bimAccFmtM(r.v[0][1],r.fmt):'',r.v[1]?bimAccFmtV(r.v[1][0],r.fmt)+' '+bimAccFmtM(r.v[1][1],r.fmt):'—',r.v[2]?bimAccFmtV(r.v[2][0],r.fmt)+' '+bimAccFmtM(r.v[2][1],r.fmt):'—',r.vs?BIM_ACC_VS[r.vs]:'Not tested'];})),psrc);
        var cs=bimAccCommuteShares(P.v.tract),cc=P.v.county?bimAccCommuteShares(P.v.county):null,bj=0,bv=-1;
        if(cs){
          cs.forEach(function(S2,j){if(!S2)return;var d=cc&&cc[j]?Math.abs(S2[0]-cc[j][0]):S2[0];if(d>bv){bv=d;bj=j;}});
          var sv=P.v.state?bimAccCommuteShares(P.v.state):null;
          col+=bimClbCard('s5',++fig,BIM_ACC_COMMUTE[bj][0]+': '+Math.round(cs[bj][0]*100)+'% of the tract\'s workers'+(cc&&cc[bj]?', against '+Math.round(cc[bj][0]*100)+'% in the county'+(sv&&sv[bj]?' and '+Math.round(sv[bj][0]*100)+'% in the state':''):''),
            'How workers 16 and over get to work (ACS table B08301), the share of each means, the tract against its county and state. Other: taxi, motorcycle and other means.',
            '<div class="a3d-clb-chart">'+bimAccCommuteSvg(P)+'</div>'+bimClbLeg(BIM_ACC_COMMUTE.map(function(c,j){return [BIM_ACC_SLOT[j],c[0]];}))+
            bimClbTable(['Means','Tract','County','State'],BIM_ACC_COMMUTE.map(function(c,j){
              function one(g){var x=bimAccCommuteShares(P.v[g]);return x&&x[j]?bimCenPct(x[j]):'—';}
              return [c[0],one('tract'),P.v.county?one('county'):'—',P.v.state?one('state'):'—'];})),psrc);
        }
        var PT=bimAccPyrShares(P.pyr.tract),PC=bimAccPyrShares(P.pyr.county);
        if(PT){
          var grp=[['under 20',0,3],['20 to 34',4,6],['35 to 64',7,12],['65 and over',13,17]],gi=0,gd=-1;
          var gs=function(Q,g){var v=0;for(var j=g[1];j<=g[2];j++)v+=Q.m[j]+Q.f[j];return v;};
          grp.forEach(function(g,j){var d=PC?Math.abs(gs(PT,g)-gs(PC,g)):0;if(d>gd){gd=d;gi=j;}});
          col+=bimClbCard('s5',++fig,bimClimFmt(gs(PT,grp[gi]),0)+'% of the tract\'s people are '+grp[gi][0]+(PC?', against '+bimClimFmt(gs(PC,grp[gi]),0)+'% in the county':'')+'; median age '+bimCenFmt(P.v.tract.age[0],1),
            'Men to the left, women to the right, in five-year bands, each as a share of everyone in the tract; the line is the county, for comparison. Single bands carry large margins of error at this scale: read the shape, not one bar.',
            '<div class="a3d-clb-chart">'+bimAccPyramidSvg(P)+'</div>'+bimClbLeg([['var(--s1)','Men, the tract'],['var(--s2)','Women, the tract']].concat(PC?[['var(--ink)','The county','ln']]:[]))+
            bimClbTable(['Age','Men %','Women %','County men %','County women %'],BIM_CEN_BAND_NAMES.map(function(nm,j){return [nm,bimClimFmt(PT.m[j],1),bimClimFmt(PT.f[j],1),PC?bimClimFmt(PC.m[j],1):'—',PC?bimClimFmt(PC.f[j],1):'—'];})),psrc+', table B01001');
        }
        cards.push(f6);
        if(col)cards.push('<div class="a3d-acc-col">'+col+'</div>');
      }
    }
    h+=cards.join('')+'</section>';
    var errs=[];((S&&S.errors)||[]).concat((P&&P.errors)||[]).forEach(function(e){if(errs.indexOf(e)<0)errs.push(e);});
    h+='<footer class="a3d-clb-notes"><h3>Method and sources</h3><ul>'+
      (S?'<li>Walk times: the streets and paths of <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> (© OpenStreetMap contributors, ODbL), through the Overpass API ('+bimClbE(S.server||'')+'), data of '+bimClbE(S.fetched)+'. The shortest walk along the network (Dijkstra) at '+S.speed+' m a minute, steps at half that; it leaves the lot anywhere within '+S.front+' m of its line. Motorways, private roads and ways closed to people on foot are left out; sidewalks are walked but not drawn. The rings of 5, 10 and 15 minutes are drawn as lines along the streets, as ArcGIS Network Analyst draws service-area lines.</li>'+
        '<li>Daily needs: '+S.places.map(function(p){return bimAccKind(p.k).name.toLowerCase();}).join(', ')+', after the 15-minute city\'s functions and the categories Walk Score uses; a park is reached at the nearest point of its edge. This is not a Walk Score. Transit: stops and lines from OpenStreetMap, without timetables.</li>'+
        '<li>Streets: OpenStreetMap\'s highway tags crosswalked to the FHWA\'s functional classes (motorway, trunk and primary as arterials; secondary and tertiary as collectors; residential and unclassified as local). Connectivity after LEED ND v4 (Neighborhood Pattern and Design): 90 intersections per square mile within a quarter mile to qualify, 140 inside a project with streets of its own, points from 300.</li>':'')+
      (hasP?'<li>The people: the US Census Bureau\'s <a href="https://www.census.gov/programs-surveys/acs" target="_blank" rel="noopener">American Community Survey</a> 5-year estimates, '+(P.year-4)+'–'+P.year+', for '+bimClbE(P.geo.tract.name)+' (the tract the site is in; a walk can cross several tracts), with 90% margins of error. A share\'s margin is worked out by the Bureau\'s formula for a derived proportion (<a href="https://www.census.gov/programs-surveys/acs/library/handbooks/general.html" target="_blank" rel="noopener">ACS General Handbook</a>, chapter 8), and a difference is counted only where it is larger than the two margins together. Geography and land area from TIGERweb.</li>':
        (P&&P.outside?'<li>The census figures cover US sites only.</li>':''))+
      (errs.length?'<li>Not available at the last fetch: '+bimClbE(errs.join('; '))+'.</li>':'')+
      '</ul></footer></div>';
    return h;
  }"""

rep("""  /* the Site analysis view's section: what is known, and the two ways in */
  function bimClbSaHtml(){""", BOARD + """
  /* the Site analysis view's section: what is known, and the two ways in */
  function bimClbSaHtml(){""")

# ---- the command ----
rep("""    ['ACCESSGET',['GETACCESS','CENSUSGET','WALKABILITYDATA'],'accessget',""",
    """    ['ACCESS',['ACCESSBOARD','PEOPLEBOARD','WALKABILITY','DEMOGRAPHICS'],'access','The Access and people board: the walk-time map, daily needs, transit, the street hierarchy and frontage, connectivity, and the census tract against its county and state'],   /* __acad3dV161 */
    ['ACCESSGET',['GETACCESS','CENSUSGET','WALKABILITYDATA'],'accessget',""")
rep("""    accessget:function(){bimAccFetch();},                        /* __acad3dV161 */""",
    """    accessget:function(){bimAccFetch();},                        /* __acad3dV161 */
    access:function(){bimClbOpen('access');},""")
rep("""    ACCESSGET:'access walk walking walkability""",
    """    ACCESS:'access people board walk times walkability daily needs 15-minute city amenities transit lines stops street hierarchy frontage intersection density connectivity demographics census age pyramid income households commute vehicles',   /* __acad3dV161 */
    ACCESSGET:'access walk walking walkability""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
