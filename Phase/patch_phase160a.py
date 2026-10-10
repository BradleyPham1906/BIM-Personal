"""patch_phase160a.py -- V160: Site analysis SA3, regulation: the zoning record, the envelope, the yield.

reference/research-zoning-envelope-yield.md. A zoning record for the site, entered by hand or read
from council layers under the lot (V134: the district, and the FAR and height where the layer has
them), drives:
- the envelope. Each side of the property is a front, side or rear (picked, or worked out), and
  each of the three has its own rule, the way Giraffe's envelope tool gives each side a profile of
  setback against height: a setback at the ground, steps ("above 15 m, 6 m back"), and an angular
  plane rising from the lot line (the front's sky exposure plane, a side or rear daylight plane).
  The street wall and stepback are the front's first step. At any height the plate is the lot with
  every side moved in by its rule's setback there, up to the height limit. Between the heights
  where a rule changes, every corner moves in a straight line, so the volume (Simpson's rule on
  each piece, exact) and every floor plate are exact, and the solid is built from whole faces;
- the yield: GFA by FAR; the envelope's capacity (the plates under it, storey by storey, each at
  most the coverage limit); which governs; net area by efficiency; units; parking;
- the compliance of the design: proposed GFA, height and coverage against the limits, and every
  element outside the envelope.
The envelope is a translucent solid on a Zoning envelope layer. The Zoning and yield board takes the
Climate board's frame (patch 160b). Each result is a finding in Legal and regulatory. Every change
is one undo step."""
NAME = 'patch_phase160a.py'
BASE = '759e7383cf4424e311d5cb4aa05c5b37019d3caa4a0a2e9a5c11115e2eb735ee'
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


rep("""    return A.concat(bimClimAuto());   /* __acad3dV159: climate and risk */""",
    """    return A.concat(bimClimAuto()).concat(bimZnAuto());   /* __acad3dV159: climate and risk; __acad3dV160: zoning */""")
rep("""      bimClbSaHtml()+   /* __acad3dV159 */""", """      bimClbSaHtml()+   /* __acad3dV159 */
      bimZnSaHtml()+    /* __acad3dV160 */""")
rep("""    if(c==='climboard')return bimClbOpen();""", """    if(c==='climboard')return bimClbOpen('climate');
    if(c==='znedit'){A3D_ZN.edit=!A3D_ZN.edit;bimSaRefresh(true);return true;}   /* __acad3dV160 */
    if(c==='znbuild')return bimZnBuild();
    if(c==='znboard')return bimClbOpen('zoning');
    if(c==='znlayer')return bimZnFromLayer(true);
    if(c==='znclear')return bimZnRemoveEnvelope();
    if(c==='znstepadd')return bimZnStepAdd(v);
    if(c==='znstepdel'){var di=v.indexOf('.');return bimZnStepDel(v.slice(0,di),+v.slice(di+1));}""")
rep("""      if((k=e.getAttribute('data-saphoto'))){bimSaPhotoFile(k,e.files&&e.files[0]);return;}""",
    """      if((k=e.getAttribute('data-saphoto'))){bimSaPhotoFile(k,e.files&&e.files[0]);return;}
      if((k=e.getAttribute('data-znf'))){bimZnSet(k,e.value);return;}   /* __acad3dV160 */""")
rep("""    {sel:'[data-saphoto]'""", """    {sel:'[data-znf]',why:'Site analysis: a control of the zoning record'},   /* __acad3dV160 */
    {sel:'[data-saphoto]'""")
rep("""  var A3D_CLB={open:false,tables:false,narrow:false};""", """  var A3D_CLB={open:false,tables:false,narrow:false,kind:'climate'};   /* __acad3dV160: which board */""")
rep("""  function bimClbOpen(){""", """  function bimClbOpen(kind){
    if(kind==='climate'||kind==='zoning')A3D_CLB.kind=kind;   /* __acad3dV160 */""")
rep("""    b.setAttribute('role','dialog');b.setAttribute('aria-modal','true');b.setAttribute('aria-label','Climate and risk board');""",
    """    b.setAttribute('role','dialog');b.setAttribute('aria-modal','true');""")
rep("""    A3D_CLB.narrow=window.innerWidth<760;""", """    A3D_CLB.narrow=window.innerWidth<760;
    b.setAttribute('aria-label',A3D_CLB.kind==='zoning'?'Zoning and yield board':'Climate and risk board');   /* __acad3dV160 */""")
rep("""  function bimClbHtml(){""", """  function bimClbHtml(){
    if(A3D_CLB.kind==='zoning')return bimZnBoardHtml();   /* __acad3dV160 */""")
rep("""      else if(a==='refresh')bimClimFetch();""", """      else if(a==='refresh')bimClimFetch();
      else if(a==='envelope')bimZnBuild();   /* __acad3dV160 */""")
rep("""    climate:function(){bimClbOpen();},""", """    climate:function(){bimClbOpen('climate');},
    zoning:function(){bimAnzView('site');A3D_ZN.edit=true;bimSaRefresh(true);},   /* __acad3dV160 */
    envelope:function(){bimZnBuild();},
    zoningboard:function(){bimClbOpen('zoning');},""")
rep("""    ['CLIMATE',['CLIMATEBOARD'""", """    ['ZONING',['ZONINGSUMMARY','ZONINGANALYSIS','ZONE'],'zoning','The site\\'s zoning: district, uses, FAR, height, setbacks by side, steps and angular planes, coverage, parking (Site analysis)'],   /* __acad3dV160 */
    ['ENVELOPE',['ZONINGENVELOPE','BUILDABLEENVELOPE','ENV'],'envelope','Build the zoning envelope in 3D from the zoning record and the property, and flag massing outside it'],
    ['ZONINGBOARD',['YIELD','YIELDSTUDY','FEASIBILITY'],'zoningboard','The Zoning and yield board: the zoning analysis table, sections, the rules by side, the plan, floor plates, the yield'],
    ['CLIMATE',['CLIMATEBOARD'""")
rep("""    CLIMATE:'climate weather""", """    ZONING:'zoning zone district regulation regulations planning code far fsr floor area ratio floor space ratio height limit setbacks stepback coverage permitted uses legal',   /* __acad3dV160 */
    ENVELOPE:'zoning envelope buildable volume massing setback stepback sky exposure plane daylight plane angular plane height limit 3d',
    ZONINGBOARD:'yield feasibility zoning analysis table gfa gross floor area units parking capacity envelope section board',
    CLIMATE:'climate weather""")
rep(""".a3d-clsec .a3d-sasechd{margin-bottom:4px}""", """.a3d-clsec .a3d-sasechd{margin-bottom:4px}
/* __acad3dV160: the zoning record's form */
.a3d-znf{display:grid;grid-template-columns:1fr 1fr;gap:6px 8px;margin:6px 0 2px}
.a3d-znf label{display:flex;flex-direction:column;justify-content:space-between;gap:2px;font-size:11px;color:#8a96a3;min-width:0}
.a3d-znf label.w{grid-column:1/-1}
.a3d-znf input,.a3d-znf select{width:100%;box-sizing:border-box}
.a3d-znf .a3d-znhd{grid-column:1/-1;font-size:11.5px;font-weight:600;color:#c9d1d9;border-top:1px solid rgba(255,255,255,.08);padding-top:8px;margin-top:4px}
.a3d-znf .a3d-znhd small{font-weight:400;color:#8a96a3;margin-left:6px}
.a3d-znstep{grid-column:1/-1;display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr) auto;gap:6px 8px;align-items:end}
.a3d-znstep.add{display:block}
.a3d-znstep .a3d-anzbtn.x{min-width:30px;min-height:26px;padding:0 8px}
.a3d-sa .a3d-znf input[type=number]{box-sizing:border-box;background:#1f2327;border:1px solid #3a4048;border-radius:6px;color:#e6eaef;padding:3px 7px;min-height:26px;font:inherit;font-size:12px}
@media(pointer:coarse){.a3d-sa .a3d-znf input[type=number]{min-height:36px;font-size:16px}.a3d-znstep .a3d-anzbtn.x{min-height:36px;min-width:36px}}
body.light-theme .a3d-sa .a3d-znf input[type=number]{background:#fff;border-color:#c9ced4;color:#222}
.a3d-znlegs{grid-column:1/-1;display:grid;grid-template-columns:1fr 1fr;gap:6px 8px}
.a3d-znhint{font-size:11px;color:#8a96a3;grid-column:1/-1;margin:2px 0 0;line-height:1.35}
body.light-theme .a3d-znf label,body.light-theme .a3d-znhint,body.light-theme .a3d-znstep,body.light-theme .a3d-znf .a3d-znhd small{color:#6b737c}
body.light-theme .a3d-znf .a3d-znhd{color:#24292f;border-top-color:rgba(0,0,0,.08)}""")

ENGINE = r"""
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
  function bimZnDone(){refreshTree();refreshLayers();refreshProps();paint();saveSoon();bimSaRefresh(true);if(A3D_CLB.open&&A3D_CLB.kind==='zoning')bimClbOpen('zoning');}
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
  /* a polygon cut by the half-plane D(p) >= c (keep) or <= c */
  function bimZnClip(poly,D,c,keepAbove){
    var out=[],i,n=poly.length;
    for(i=0;i<n;i++){
      var p=poly[i],q=poly[(i+1)%n],dp=D(p)-c,dq=D(q)-c,ip=keepAbove?dp>=-1e-9:dp<=1e-9,iq=keepAbove?dq>=-1e-9:dq<=1e-9;
      if(ip)out.push(p);
      if(ip!==iq){var tt=dp/(dp-dq);out.push([p[0]+(q[0]-p[0])*tt,p[1]+(q[1]-p[1])*tt]);}
    }
    return out.length>=3?out:[];
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
        '<button type="button" class="a3d-anzbtn" data-saact="znboard">Open the board</button>':'')+'</div>';
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
"""

rep("""  /* ---- edits: each one undo step ---- */
  function bimSaAdd(cat,f){""", ENGINE + """
  /* ---- edits: each one undo step ---- */
  function bimSaAdd(cat,f){""")

rep("""  window.__a3dAnzView=function(v){""", """  window.__a3dZn=function(){return JSON.parse(JSON.stringify(bimZn()));};   /* __acad3dV160 */
  window.__a3dZnSet=function(k,v){return bimZnSet(k,v);};
  window.__a3dZnStepAdd=function(r){return bimZnStepAdd(r);};
  window.__a3dZnStepDel=function(r,i){return bimZnStepDel(r,i);};
  window.__a3dZnCalc=function(){var C=bimZnCalc();if(!C.ok)return {error:C.error};
    return {lot:C.lot,fpArea:C.fpArea,fp:C.fp,volume:C.volume,top:C.top,hTop:C.hTop,plates:C.plates,capacity:C.capacity,farGFA:C.farGFA,achievable:C.achievable,governs:C.governs,
      storeysUsed:C.storeysUsed,nsa:C.nsa,units:C.units,parking:C.parking,maxH:C.maxH,lotD:C.lotD,convex:C.convex,split:C.split,roles:C.legs.legs.map(function(l){return l.role;}),
      pieces:C.pieces,breaks:C.Z,proposed:C.proposed};};
  window.__a3dZnPlate=function(h,side){var C=bimZnCalc();if(!C.ok)return null;var q=bimZnPlate(C,+h,side===undefined?-1:side);
    return q?{area:Math.abs(bimZnArea2(q)),pts:q.map(function(c){return c.p;}),tags:q.map(function(c){return c.t;})}:{split:true};};
  window.__a3dZnInset=function(role,h,side){var z=bimZn(),R=bimZnRules(z);return R[role]?bimZnInset(R[role],+h,side===undefined?-1:side):null;};
  window.__a3dZnAllows=function(x,zc,y){var C=bimZnCalc();return C.ok?bimZnAllows(C,[x,zc],y):null;};
  window.__a3dZnBuild=function(){var C=bimZnBuild();return C&&C.ok?true:(C&&C.error)||false;};
  window.__a3dZnFromLayer=function(apply){var r=bimZnFromLayer(!!apply);return r?JSON.parse(JSON.stringify(r)):null;};
  window.__a3dZnEnvelope=function(){var o=bimZnEnvelopeObj();return o?{id:o.id,name:o.name,layer:o.layer,locked:o.locked,envelope:o.envelope,nv:o.mesh.v.length,nf:o.mesh.f.length,
    v:o.mesh.v,f:o.mesh.f}:null;};
  window.__a3dZnEdit=function(on){A3D_ZN.edit=!!on;bimSaRefresh(true);return true;};
  window.__a3dAnzView=function(v){""")
rep("""  window.__a3dClbOpen=function(){return bimClbOpen();};""", """  window.__a3dClbOpen=function(k){return bimClbOpen(k);};   /* __acad3dV160: 'climate' or 'zoning'; none keeps the last */""")
rep("""  window.__acad3dV159='climatefetch,""", """  window.__acad3dV160='zoningrecord,fromlayers,farheightfromlayers,envelope,rolesbyside,cornerlot,steps,angularplanes,skyplane,stepback,heightlimit,exactplates,exactvolume,wholefaces,yield,compliance,zoningboard,zoningtable,sections,rulesbyside,plandiagram';
  window.__acad3dV159='climatefetch,""")
rep("""  var BIM_APP_VERSION={v:'V159',date:'2026-10-05'};   /* __acad3dV159 */""",
    """  var BIM_APP_VERSION={v:'V160',date:'2026-10-10'};   /* __acad3dV160 */""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
