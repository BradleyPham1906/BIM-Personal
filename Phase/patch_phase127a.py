"""patch_phase127a.py -- V127: the alignment and its profile -- the geometry.

PIPELINE, Track B item 3: "Alignment / profile objects -- horizontal alignment, vertical profile,
station-offset." An alignment is its own kind of object (t:'alignment'), as a property line is
(V103), so no sketch tool can trim or offset it into something that is not a route:

  pis     the points of intersection [x, z], in the object's own frame (pos moves it)
  radii   one circular-curve radius per interior PI -- 0, or a PI the route goes straight through,
          has no curve
  sta0    the station of its first point
  profile {pvis:[{sta, elev, L}]} -- the vertical alignment, by PVI; L is a vertical curve's length

Civil 3D's "alignment from objects, curves between tangents": each interior PI gets a circular
curve tangent to both legs -- deflection D, tangent T = R tan(D/2), length L = R D, external
E = R (sec(D/2) - 1). Curves that would overlap on a leg are refused by name, never trimmed.
Stations run along the route itself, tangent and arc, from sta0; a point's station and offset are
found exactly on the arcs, not on a flattened copy. Offsets are positive to the right looking up
station.

The profile is AASHTO's: straight grades between PVIs, and at a PVI with a length, a symmetric
parabola y = y_PVC + g1 x + (g2 - g1) x^2 / 2L, whose high or low point is at x = -g1 L / (g2 - g1)
when that lies on the curve, and whose K is L / |A| (A in percent). The ground under an alignment
is read from a V108 surface: bimTinHeightAt interpolates in the triangle a point falls in.

Stations are written k+mmm.mm (1000 m to the k), the metric form; the project's units are metric."""
NAME = 'patch_phase127a.py'
BASE = '525fc46992ccd5caa25217c0729a98ab2ebe1630d54a09803bfe7ed173ca2e3f'
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


rep("""  function bimSetTrueNorth(deg){""", r"""  /* ================= __acad3dV127: the alignment and its profile ================= */
  var BIM_ALIGN_R0=100;         /* the radius ALIGNMENT offers, when the legs leave room for it */
  function bimIsAlignment(o){return !!(o&&o.t==='alignment'&&o.pis&&o.pis.length>=2);}
  /* 1234.5 -> "1+234.50": kilometres to the plus */
  function bimFmtStation(s){
    if(!isFinite(s))return '—';
    var neg=s<0,a=Math.abs(s),k=Math.floor(a/1000+1e-9),m=a-k*1000;
    if(m<0)m=0;
    var ms=m.toFixed(2);if(parseFloat(ms)>=1000){k++;ms='0.00';}
    while(ms.indexOf('.')<3)ms='0'+ms;
    return (neg?'-':'')+k+'+'+ms;
  }
  /* The ONE derivation of the horizontal alignment, in world plan terms. */
  function bimAlignGeom(o){
    var q=bimObjOffset(o),P=o.pis.map(function(p){return [p[0]+q[0],p[1]+q[2]];}),n=P.length,i,j;
    var sta0=isFinite(o.sta0)?o.sta0:0,legs=[],pis=[];
    for(j=0;j+1<n;j++){
      var dx=P[j+1][0]-P[j][0],dz=P[j+1][1]-P[j][1],len=Math.sqrt(dx*dx+dz*dz);
      if(!(len>1e-9))return {error:'PI '+(j+1)+' and PI '+(j+2)+' are the same point'};
      legs.push({len:len,u:[dx/len,dz/len]});
    }
    for(i=0;i<n;i++){
      var pi={i:i,pt:P[i],R:0,D:0,T:0,L:0,E:0,turn:0};
      if(i>0&&i<n-1){
        var a=legs[i-1].u,b=legs[i].u,cr=a[0]*b[1]-a[1]*b[0],dt=a[0]*b[0]+a[1]*b[1];
        var D=Math.atan2(cr,dt),R=o.radii&&o.radii[i-1];
        pi.D=Math.abs(D);pi.turn=D>0?1:(D<0?-1:0);
        if(pi.D>1e-9&&R>0){
          if(pi.D>Math.PI-1e-6)return {error:'the route turns back on itself at PI '+(i+1)};
          pi.R=R;pi.T=R*Math.tan(pi.D/2);pi.L=R*pi.D;pi.E=R*(1/Math.cos(pi.D/2)-1);
        }
      }
      pis.push(pi);
    }
    for(j=0;j+1<n;j++){
      if(pis[j].T+pis[j+1].T>legs[j].len+1e-9)
        return {error:(pis[j].T>0&&pis[j+1].T>0?'the curves at PI '+(j+1)+' and PI '+(j+2)+' overlap':'the curve at PI '+(pis[j].T>0?j+1:j+2)+' runs past the end of its leg')+
          ' ('+(pis[j].T+pis[j+1].T).toFixed(2)+' m of tangent on a '+legs[j].len.toFixed(2)+' m leg)'};
    }
    var els=[],s=sta0;
    for(j=0;j+1<n;j++){
      var u=legs[j].u,A=[P[j][0]+u[0]*pis[j].T,P[j][1]+u[1]*pis[j].T],B=[P[j+1][0]-u[0]*pis[j+1].T,P[j+1][1]-u[1]*pis[j+1].T];
      var ll=legs[j].len-pis[j].T-pis[j+1].T;
      if(ll>1e-9){els.push({kind:'line',s0:s,s1:s+ll,a:A,u:u,len:ll});s+=ll;}
      var pk=pis[j+1];
      if(pk.T>0){
        var u2=legs[j+1].u,nrm=pk.turn>0?[-u[1],u[0]]:[u[1],-u[0]];
        var C=[B[0]+nrm[0]*pk.R,B[1]+nrm[1]*pk.R];
        pk.pc=s;pk.pt=s+pk.L;pk.PC=B;pk.PT=[P[j+1][0]+u2[0]*pk.T,P[j+1][1]+u2[1]*pk.T];pk.C=C;
        els.push({kind:'arc',s0:s,s1:s+pk.L,c:C,R:pk.R,a0:Math.atan2(B[1]-C[1],B[0]-C[0]),dir:pk.turn,len:pk.L,pi:j+1});
        s+=pk.L;
      }
    }
    return {pis:pis,legs:legs,els:els,sta0:sta0,sta1:s,length:s-sta0,start:P[0],end:P[n-1]};
  }
  function bimAlignProblem(o){var g=bimAlignGeom(o);return g.error||null;}
  /* the point and the unit direction at station s, on the route itself */
  function bimAlignPointAt(g,s){
    if(!g||!g.els||!g.els.length)return null;
    var i,e=g.els[g.els.length-1];
    for(i=0;i<g.els.length;i++)if(s<=g.els[i].s1+1e-9){e=g.els[i];break;}
    var t=Math.max(0,Math.min(e.len,s-e.s0));
    if(e.kind==='line')return {p:[e.a[0]+e.u[0]*t,e.a[1]+e.u[1]*t],d:[e.u[0],e.u[1]]};
    var an=e.a0+e.dir*t/e.R;
    return {p:[e.c[0]+e.R*Math.cos(an),e.c[1]+e.R*Math.sin(an)],d:[-e.dir*Math.sin(an),e.dir*Math.cos(an)]};
  }
  /* A plan point's station and offset: the nearest point on the route, exact on the arcs. The
     offset is + to the right looking up station; 'beyond' says the point lies past an end. */
  function bimAlignStationOffset(g,p){
    if(!g||!g.els||!g.els.length)return null;
    var best=null,i,e,t,f;
    for(i=0;i<g.els.length;i++){
      e=g.els[i];
      if(e.kind==='line'){t=(p[0]-e.a[0])*e.u[0]+(p[1]-e.a[1])*e.u[1];}
      else{
        var ang=Math.atan2(p[1]-e.c[1],p[0]-e.c[0]),da=(ang-e.a0)*e.dir;
        da=((da%(2*Math.PI))+2*Math.PI)%(2*Math.PI);
        t=da*e.R;
        if(t>e.len){var over=t-e.len,under=2*Math.PI*e.R-t;t=over<under?e.len:0;}
      }
      t=Math.max(0,Math.min(e.len,t));
      f=bimAlignPointAt(g,e.s0+t);
      var dx=p[0]-f.p[0],dz=p[1]-f.p[1],d2=dx*dx+dz*dz;
      if(!best||d2<best.d2-1e-12)best={d2:d2,sta:e.s0+t,foot:f.p,dir:f.d,off:dx*(-f.d[1])+dz*f.d[0]};
    }
    var along=(p[0]-best.foot[0])*best.dir[0]+(p[1]-best.foot[1])*best.dir[1];
    return {sta:best.sta,off:best.off,foot:best.foot,dist:Math.sqrt(best.d2),
      beyond:(best.sta<=g.sta0+1e-9&&along<-1e-6)?'before the start':((best.sta>=g.sta1-1e-9&&along>1e-6)?'past the end':'')};
  }
  /* ---- the profile */
  function bimProfileGeom(pr,g){
    if(!pr||!pr.pvis||pr.pvis.length<2)return {error:'a profile needs at least two PVIs'};
    var v=pr.pvis.map(function(x){return {sta:+x.sta,elev:+x.elev,L:+(x.L||0)};}),n=v.length,i;
    for(i=0;i<n;i++){
      if(!isFinite(v[i].sta)||!isFinite(v[i].elev))return {error:'PVI '+(i+1)+' needs a station and an elevation'};
      if(!(v[i].L>=0))return {error:'PVI '+(i+1)+'\'s curve length cannot be negative'};
      if(i>0&&!(v[i].sta>v[i-1].sta+1e-9))return {error:'PVI '+(i+1)+' must be up station of PVI '+i};
    }
    if(g&&!g.error&&(v[0].sta<g.sta0-1e-6||v[n-1].sta>g.sta1+1e-6))
      return {error:'the profile runs off the alignment ('+bimFmtStation(g.sta0)+' to '+bimFmtStation(g.sta1)+')'};
    v[0].L=0;v[n-1].L=0;
    var gr=[];
    for(i=0;i+1<n;i++)gr.push((v[i+1].elev-v[i].elev)/(v[i+1].sta-v[i].sta));
    for(i=0;i<n;i++){
      var p=v[i];p.gIn=i>0?gr[i-1]:null;p.gOut=i<n-1?gr[i]:null;
      if(p.L>0){
        p.pvc=p.sta-p.L/2;p.pvt=p.sta+p.L/2;p.A=(p.gOut-p.gIn)*100;
        p.K=Math.abs(p.A)>1e-12?p.L/Math.abs(p.A):Infinity;
        p.kind=p.gOut<p.gIn?'crest':'sag';
        var x=Math.abs(p.gOut-p.gIn)>1e-15?-p.gIn*p.L/(p.gOut-p.gIn):-1;
        if(x>1e-9&&x<p.L-1e-9){p.turnSta=p.pvc+x;p.turnElev=p.elev-p.gIn*p.L/2+p.gIn*x+(p.gOut-p.gIn)*x*x/(2*p.L);}
      }
    }
    for(i=1;i<n-1;i++){
      var lo=v[i-1].L>0?v[i-1].pvt:v[i-1].sta,hi=v[i+1].L>0?v[i+1].pvc:v[i+1].sta;
      if(v[i].L>0&&(v[i].pvc<lo-1e-9||v[i].pvt>hi+1e-9))
        return {error:'the vertical curve at PVI '+(i+1)+' ('+v[i].L+' m) overlaps '+(v[i].pvc<lo-1e-9?'PVI '+i:'PVI '+(i+2))+(v[i].pvc<lo-1e-9&&v[i-1].L>0||v[i].pvt>hi+1e-9&&v[i+1].L>0?'\'s curve':'')};
    }
    return {pvis:v,grades:gr,sta0:v[0].sta,sta1:v[n-1].sta};
  }
  /* elevation and grade at station s; null off the profile */
  function bimProfileElevAt(pg,s){
    if(!pg||pg.error||s<pg.sta0-1e-9||s>pg.sta1+1e-9)return null;
    var v=pg.pvis,i;
    for(i=1;i<v.length-1;i++){
      var p=v[i];
      if(p.L>0&&s>=p.pvc&&s<=p.pvt){
        var x=s-p.pvc;
        return {elev:p.elev-p.gIn*p.L/2+p.gIn*x+(p.gOut-p.gIn)*x*x/(2*p.L),grade:p.gIn+(p.gOut-p.gIn)*x/p.L,onCurve:i};
      }
    }
    for(i=0;i+1<v.length;i++)if(s<=v[i+1].sta+1e-9)return {elev:v[i].elev+pg.grades[i]*(s-v[i].sta),grade:pg.grades[i],onCurve:-1};
    return null;
  }
  /* The ground at a plan point: the surface's triangle it falls in, interpolated. null off it. */
  function bimTinHeightAt(tin,x,z){
    if(!tin||!tin.tris)return null;
    var t,P=tin.P,H=tin.H;
    for(t=0;t<tin.tris.length;t++){
      var tr=tin.tris[t],A=P[tr[0]],B=P[tr[1]],C=P[tr[2]];
      var det=(B[0]-A[0])*(C[1]-A[1])-(C[0]-A[0])*(B[1]-A[1]);
      if(!(Math.abs(det)>1e-18))continue;
      var l1=((x-A[0])*(C[1]-A[1])-(C[0]-A[0])*(z-A[1]))/det,l2=((B[0]-A[0])*(z-A[1])-(x-A[0])*(B[1]-A[1]))/det;
      if(l1>=-1e-9&&l2>=-1e-9&&l1+l2<=1+1e-9)return H[tr[0]]+l1*(H[tr[1]]-H[tr[0]])+l2*(H[tr[2]]-H[tr[0]]);
    }
    return null;
  }
  /* The ground along the alignment, from the first surface under it: [station, elevation] runs,
     broken where the route leaves the surface. */
  function bimAlignGround(o,g,step){
    var ters=A3D.objs.filter(function(t){return t.t==='terrain'&&t.survey&&t.survey.length>=3;}),out=[],run=[],k,s,n;
    if(!ters.length||!g||g.error)return out;
    var tin=null;
    try{tin=bimTerrainTin(ters[0]);}catch(eT){console.warn('[BIM] The surface could not be read for the profile',eT);return out;}
    step=step||Math.max(g.length/400,0.5);
    n=Math.max(2,Math.ceil(g.length/step));
    for(k=0;k<=n;k++){
      s=g.sta0+g.length*k/n;
      var pa=bimAlignPointAt(g,s),h=pa?bimTinHeightAt(tin,pa.p[0],pa.p[1]):null;
      if(h===null){if(run.length>1)out.push(run);run=[];}
      else run.push([s,h]);
    }
    if(run.length>1)out.push(run);
    return out;
  }
  /* The radius ALIGNMENT puts at every PI: BIM_ALIGN_R0, or the largest the legs leave room for
     (95% of it, rounded down), whichever is less. 0 when there is no room at all. */
  function bimAlignFitRadius(P){
    var n=P.length,tn=[],fit=Infinity,i;
    for(i=0;i<n;i++){
      if(i===0||i===n-1){tn.push(0);continue;}
      var a=[P[i][0]-P[i-1][0],P[i][1]-P[i-1][1]],b=[P[i+1][0]-P[i][0],P[i+1][1]-P[i][1]];
      var D=Math.abs(Math.atan2(a[0]*b[1]-a[1]*b[0],a[0]*b[0]+a[1]*b[1]));
      tn.push(D>1e-9?Math.tan(D/2):0);
    }
    for(i=0;i+1<n;i++){
      var sm=tn[i]+tn[i+1],len=Math.sqrt(Math.pow(P[i+1][0]-P[i][0],2)+Math.pow(P[i+1][1]-P[i][1],2));
      if(sm>0)fit=Math.min(fit,len/sm);
    }
    if(fit===Infinity)return BIM_ALIGN_R0;
    var r=Math.min(BIM_ALIGN_R0,fit*0.95);
    return r>=2?Math.floor(r):Math.floor(r*10)/10;
  }
  function bimNewAlignment(pis,pos,y){
    A3D.counts.alignment=(A3D.counts.alignment||0)+1;
    var R=bimAlignFitRadius(pis.map(function(p){return [p[0]+(pos?pos[0]:0),p[1]+(pos?pos[2]:0)];})),r=[],i;
    for(i=1;i<pis.length-1;i++)r.push(R);
    return {id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'alignment',name:'Alignment_'+A3D.counts.alignment,
      col:'#e06c75',pos:pos?[pos[0],pos[1],pos[2]]:[0,0,0],pis:pis.map(function(p){return [p[0],p[1]];}),radii:r,sta0:0,
      y:isFinite(y)?y:0,layer:A3D.activeLayer};
  }
  /* ALIGNMENT: an open polyline of straight legs becomes an alignment -- its vertices the PIs --
     and takes its place. */
  function bimAlignmentFromSketch(o){
    if(!o||o.t!=='sketch'||!o.pts){a3dToast('Select an open polyline to make an alignment from: its vertices become the PIs');return null;}
    if(o.closed!==false){a3dToast('An alignment runs from one end to another: select an open polyline, not a closed shape');return null;}
    if(o.pts.length<2){a3dToast('An alignment needs at least two points');return null;}
    if(bimHasBulge(o.bulges)){a3dToast('An alignment is built from straight legs and puts its own curves at the PIs; this polyline has arcs');return null;}
    var al=bimNewAlignment(o.pts,bimObjOffset(o),o.y);
    if(al.radii.length&&al.radii[0]<0.1){a3dToast('The PIs are too close together to fit a curve between the legs');return null;}
    var gc=bimAlignGeom(al);
    if(gc.error){a3dToast('That polyline cannot be an alignment: '+gc.error);return null;}
    pushUndo();
    var ix=A3D.objs.indexOf(o);
    if(ix>=0)A3D.objs.splice(ix,1,al);else A3D.objs.push(al);
    A3D.sel=al.id;A3D.selSet=[al.id];A3D.sel2=null;
    refreshTree();refreshProps();paint();saveSoon();
    a3dToast(al.name+' from '+o.name+': '+gc.length.toFixed(2)+' m, '+al.radii.filter(function(r,k){return gc.pis[k+1].T>0;}).length+' curve(s)'+
      (al.radii.length?' of radius '+al.radii[0]+' m':'')+' -- set the radii in Properties');
    return al;
  }
  function bimSetTrueNorth(deg){""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
