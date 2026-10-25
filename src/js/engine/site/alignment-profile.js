  /* ================= __acad3dV127: the alignment and its profile ================= */
  var BIM_ALIGN_R0=100;         /* the radius ALIGNMENT offers, when the legs leave room for it */
  function bimIsAlignment(o){return !!(o&&o.t==='alignment'&&o.pis&&o.pis.length>=2);}
  /* 1234.5 -> "1+234.50": kilometres to the plus */
  function bimFmtStation(s){
    if(!isFinite(s))return '\u2014';
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
  /* ---- __acad3dV127: drawing */
  /* The route as stationed plan points, the arcs flattened to the V88 tolerance. */
  function bimAlignPolyline(g){
    var out=[],i,k;
    for(i=0;i<g.els.length;i++){
      var e=g.els[i],n=e.kind==='arc'?bimArcSegments(e.R,e.len/e.R):1;
      for(k=(out.length?1:0);k<=n;k++){var s=e.s0+e.len*k/n;out.push({s:s,p:bimAlignPointAt(g,s).p});}
    }
    return out;
  }
  /* the elevation the route is drawn at, at station s */
  function bimAlignDrawY(o,pg,s){
    var e=pg&&!pg.error?bimProfileElevAt(pg,s):null;
    return e?e.elev:(o.y||0)+bimObjOffset(o)[1];
  }
  /* the profile view's frame: station runs east from its point, elevation north, exaggerated */
  function bimProfileViewFrame(o,g,pg,ground){
    if(!o.profileView||!o.profileView.at||!g||g.error)return null;
    var q=bimObjOffset(o),vx=o.profileView.vx>0?o.profileView.vx:10,lo=Infinity,hi=-Infinity,i,k;
    if(pg&&!pg.error)for(i=0;i<pg.pvis.length;i++){lo=Math.min(lo,pg.pvis[i].elev);hi=Math.max(hi,pg.pvis[i].elev);}
    for(i=0;i<ground.length;i++)for(k=0;k<ground[i].length;k++){lo=Math.min(lo,ground[i][k][1]);hi=Math.max(hi,ground[i][k][1]);}
    if(!isFinite(lo)){lo=(o.y||0)+q[1];hi=lo;}
    var raw=Math.max(hi-lo,1)/6,steps=[0.1,0.2,0.25,0.5,1,2,2.5,5,10,20,25,50,100],st=100;
    for(i=0;i<steps.length;i++)if(steps[i]>=raw){st=steps[i];break;}
    var e0=Math.floor(lo/st)*st-st,e1=Math.ceil(hi/st)*st+st;
    var x0=o.profileView.at[0]+q[0],z0=o.profileView.at[1]+q[2],y=(o.y||0)+q[1];
    return {vx:vx,e0:e0,e1:e1,step:st,s0:g.sta0,s1:g.sta1,y:y,
      at:function(s,e){return [x0+(s-g.sta0),y,z0-(e-e0)*vx];}};
  }
  function drawAlignments(ctx,V,W,H){
    A3D.lastAlignDrawn={};
    if(A3D.section)return;
    var i,k,o;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(!bimIsAlignment(o)||!bimLayerShown(o))continue;
      var sel=(o.id===A3D.sel||(A3D.selSet&&A3D.selSet.indexOf(o.id)>=0));
      var g=bimAlignGeom(o),q=bimObjOffset(o),rec={ticks:0,majors:[],pcpt:[],error:g.error||null,profileView:false,pvLabels:[]};
      A3D.lastAlignDrawn[o.id]=rec;
      ctx.save();
      ctx.globalAlpha*=bimLayerAlpha(o);
      var col=sel?'#4ea1ff':(o.col||'#e06c75');
      if(g.error||sel){
        /* the PI polygon: while selected, or as all there is when the geometry is refused */
        ctx.strokeStyle=g.error?'#ff5f56':'rgba(158,193,255,0.7)';ctx.lineWidth=1;ctx.setLineDash([6,4]);
        ctx.beginPath();
        for(k=0;k<o.pis.length;k++){
          var pp=toScreen([o.pis[k][0]+q[0],(o.y||0)+q[1],o.pis[k][1]+q[2]],V,W,H);
          if(k===0)ctx.moveTo(pp[0],pp[1]);else ctx.lineTo(pp[0],pp[1]);
        }
        ctx.stroke();ctx.setLineDash([]);
        for(k=0;k<o.pis.length;k++){
          var pc=toScreen([o.pis[k][0]+q[0],(o.y||0)+q[1],o.pis[k][1]+q[2]],V,W,H);
          ctx.beginPath();ctx.arc(pc[0],pc[1],3,0,Math.PI*2);ctx.stroke();
        }
        if(g.error){
          var p0=toScreen([o.pis[0][0]+q[0],(o.y||0)+q[1],o.pis[0][1]+q[2]],V,W,H);
          ctx.fillStyle='#ff5f56';ctx.font='11px system-ui,sans-serif';ctx.textAlign='left';ctx.textBaseline='bottom';
          ctx.fillText(o.name+': '+g.error,p0[0]+6,p0[1]-6);
          ctx.restore();continue;
        }
      }
      var pg=o.profile?bimProfileGeom(o.profile,g):null;
      var line=bimAlignPolyline(g),sp=line.map(function(r){return toScreen([r.p[0],bimAlignDrawY(o,pg,r.s),r.p[1]],V,W,H);});
      ctx.strokeStyle=col;ctx.lineWidth=sel?2.4:2;
      ctx.setLineDash([22,4,4,4]);
      ctx.beginPath();
      for(k=0;k<sp.length;k++){if(k===0)ctx.moveTo(sp[k][0],sp[k][1]);else ctx.lineTo(sp[k][0],sp[k][1]);}
      ctx.stroke();ctx.setLineDash([]);
      rec.pts=line.length;
      /* station ticks, sized in pixels; thinned when there is no room to read them */
      function scr(s,off){
        var a=bimAlignPointAt(g,s),yy=bimAlignDrawY(o,pg,s);
        var c=toScreen([a.p[0],yy,a.p[1]],V,W,H),r=toScreen([a.p[0]-a.d[1],yy,a.p[1]+a.d[0]],V,W,H),f=toScreen([a.p[0]+a.d[0],yy,a.p[1]+a.d[1]],V,W,H);
        var nx=r[0]-c[0],ny=r[1]-c[1],nl=Math.sqrt(nx*nx+ny*ny)||1;
        return {c:c,n:[nx/nl,ny/nl],ang:Math.atan2(f[1]-c[1],f[0]-c[0]),ppm:Math.sqrt((f[0]-c[0])*(f[0]-c[0])+(f[1]-c[1])*(f[1]-c[1]))};
      }
      var ppm=scr(g.sta0).ppm,minor=20,major=100,s;
      ctx.strokeStyle=col;ctx.fillStyle=sel?'#9ec1ff':'#f0a8ae';ctx.lineWidth=1;
      ctx.font='10px system-ui,sans-serif';ctx.textAlign='center';ctx.textBaseline='bottom';
      if(ppm*minor>=5){
        for(s=Math.ceil(g.sta0/minor-1e-9)*minor;s<=g.sta1+1e-9;s+=minor){
          var isMaj=Math.abs(s/major-Math.round(s/major))<1e-9,T=scr(s),len=isMaj?8:4;
          ctx.beginPath();ctx.moveTo(T.c[0]-T.n[0]*len,T.c[1]-T.n[1]*len);ctx.lineTo(T.c[0]+T.n[0]*len,T.c[1]+T.n[1]*len);ctx.stroke();
          rec.ticks++;
          if(isMaj&&ppm*major>=40){
            var an=T.ang;if(an>Math.PI/2)an-=Math.PI;else if(an<-Math.PI/2)an+=Math.PI;
            ctx.save();ctx.translate(T.c[0]-T.n[0]*10,T.c[1]-T.n[1]*10);ctx.rotate(an);ctx.fillText(bimFmtStation(s),0,0);ctx.restore();
            rec.majors.push(s);
          }
        }
      }
      /* the geometry points: every PC and PT, and both ends */
      var gp=[{s:g.sta0,t:'BEG'}],j;
      for(j=0;j<g.pis.length;j++)if(g.pis[j].T>0){gp.push({s:g.pis[j].pc,t:'PC'});gp.push({s:g.pis[j].pt,t:'PT'});}
      gp.push({s:g.sta1,t:'END'});
      ctx.textAlign='left';ctx.textBaseline='middle';
      for(j=0;j<gp.length;j++){
        var G=scr(gp[j].s);
        ctx.beginPath();ctx.arc(G.c[0],G.c[1],3.5,0,Math.PI*2);ctx.stroke();
        if(ppm*20>=4||gp[j].t==='BEG'||gp[j].t==='END'){
          ctx.save();ctx.translate(G.c[0]+G.n[0]*12,G.c[1]+G.n[1]*12);
          var an2=Math.atan2(G.n[1],G.n[0]);if(an2>Math.PI/2)an2-=Math.PI;else if(an2<-Math.PI/2)an2+=Math.PI;
          ctx.rotate(an2);ctx.textAlign=Math.abs(Math.atan2(G.n[1],G.n[0]))>Math.PI/2?'right':'left';
          ctx.fillText(gp[j].t+' '+bimFmtStation(gp[j].s),0,0);ctx.restore();
        }
        rec.pcpt.push(gp[j].t+' '+bimFmtStation(gp[j].s));
      }
      /* the profile view, in model space */
      var ground=bimAlignGround(o,g),F=bimProfileViewFrame(o,g,pg,ground);
      if(F){
        rec.profileView=true;
        var gs=function(s,e){return toScreen(F.at(s,e),V,W,H);},c0=gs(F.s0,F.e0),c1=gs(F.s1,F.e1);
        ctx.fillStyle='rgba(20,22,26,0.55)';ctx.fillRect(Math.min(c0[0],c1[0]),Math.min(c0[1],c1[1]),Math.abs(c1[0]-c0[0]),Math.abs(c1[1]-c0[1]));
        ctx.strokeStyle='rgba(143,151,163,0.35)';ctx.lineWidth=1;
        ctx.font='9px system-ui,sans-serif';ctx.fillStyle='#aab2bd';
        var gstep=(gs(F.s0+20,F.e0)[0]-c0[0])>=8?20:100,e;
        for(s=Math.ceil(F.s0/gstep-1e-9)*gstep;s<=F.s1+1e-9;s+=gstep){
          var a1=gs(s,F.e0),a2=gs(s,F.e1);ctx.beginPath();ctx.moveTo(a1[0],a1[1]);ctx.lineTo(a2[0],a2[1]);ctx.stroke();
          if(Math.abs(s/100-Math.round(s/100))<1e-9){ctx.textAlign='center';ctx.textBaseline='top';ctx.fillText(bimFmtStation(s),a1[0],a1[1]+3);}
        }
        for(e=F.e0;e<=F.e1+1e-9;e+=F.step){
          var b1=gs(F.s0,e),b2=gs(F.s1,e);ctx.beginPath();ctx.moveTo(b1[0],b1[1]);ctx.lineTo(b2[0],b2[1]);ctx.stroke();
          ctx.textAlign='right';ctx.textBaseline='middle';ctx.fillText(bimTrimNum(e.toFixed(2)),b1[0]-4,b1[1]);
        }
        ctx.strokeStyle='#8f97a3';ctx.strokeRect(Math.min(c0[0],c1[0]),Math.min(c0[1],c1[1]),Math.abs(c1[0]-c0[0]),Math.abs(c1[1]-c0[1]));
        ctx.fillStyle='#dfe4ea';ctx.font='11px system-ui,sans-serif';ctx.textAlign='left';ctx.textBaseline='bottom';
        ctx.fillText(o.name+' profile  (vertical x'+F.vx+')',Math.min(c0[0],c1[0]),Math.min(c0[1],c1[1])-4);
        ctx.strokeStyle='#a0805a';ctx.lineWidth=1.2;
        for(k=0;k<ground.length;k++){
          ctx.beginPath();
          for(j=0;j<ground[k].length;j++){var gg=gs(ground[k][j][0],ground[k][j][1]);if(j===0)ctx.moveTo(gg[0],gg[1]);else ctx.lineTo(gg[0],gg[1]);}
          ctx.stroke();
        }
        rec.groundRuns=ground.length;
        if(pg&&!pg.error){
          ctx.strokeStyle=col;ctx.lineWidth=2.2;ctx.beginPath();
          var nS=Math.max(40,Math.ceil((pg.sta1-pg.sta0)/2));
          for(j=0;j<=nS;j++){var ss=pg.sta0+(pg.sta1-pg.sta0)*j/nS,ev=bimProfileElevAt(pg,ss),pp2=gs(ss,ev.elev);if(j===0)ctx.moveTo(pp2[0],pp2[1]);else ctx.lineTo(pp2[0],pp2[1]);}
          ctx.stroke();
          ctx.font='9px system-ui,sans-serif';ctx.fillStyle='#f0a8ae';ctx.textAlign='center';ctx.textBaseline='bottom';
          for(j=0;j<pg.pvis.length;j++){
            var pv=pg.pvis[j],pm=gs(pv.sta,pv.elev);
            ctx.beginPath();ctx.moveTo(pm[0],pm[1]-5);ctx.lineTo(pm[0]+4,pm[1]+3);ctx.lineTo(pm[0]-4,pm[1]+3);ctx.closePath();ctx.stroke();
            var lab='PVI '+bimFmtStation(pv.sta)+'  El '+pv.elev.toFixed(2)+(pv.L>0?'  L '+bimTrimNum(pv.L.toFixed(2))+'  K '+(isFinite(pv.K)?pv.K.toFixed(1):'\u2014'):'');
            ctx.fillText(lab,pm[0],pm[1]-8);rec.pvLabels.push(lab);
            if(pv.turnSta!==undefined){var tp=gs(pv.turnSta,pv.turnElev);ctx.beginPath();ctx.arc(tp[0],tp[1],3,0,Math.PI*2);ctx.stroke();
              ctx.textBaseline='top';ctx.fillText((pv.kind==='crest'?'High ':'Low ')+bimFmtStation(pv.turnSta)+' El '+pv.turnElev.toFixed(2),tp[0],tp[1]+5);ctx.textBaseline='bottom';}
          }
        }else if(pg&&pg.error){
          ctx.fillStyle='#ff5f56';ctx.textAlign='left';ctx.fillText('Profile: '+pg.error,Math.min(c0[0],c1[0])+6,Math.max(c0[1],c1[1])-6);
        }
        rec.frame=[Math.min(c0[0],c1[0]),Math.min(c0[1],c1[1]),Math.max(c0[0],c1[0]),Math.max(c0[1],c1[1])];
      }
      rec.profileError=pg&&pg.error?pg.error:null;
      ctx.restore();
    }
  }
  function bimPickAlignment(x,y){
    var V=camVecs(A3D.cam),W=cvW(),H=cvH(),best=null,bd=6,i,k,o;
    for(i=A3D.objs.length-1;i>=0;i--){
      o=A3D.objs[i];
      if(!bimIsAlignment(o)||!bimLayerPickable(o))continue;
      var g=bimAlignGeom(o),q=bimObjOffset(o);
      if(g.error){
        for(k=0;k+1<o.pis.length;k++){
          var e1=toScreen([o.pis[k][0]+q[0],(o.y||0)+q[1],o.pis[k][1]+q[2]],V,W,H),e2=toScreen([o.pis[k+1][0]+q[0],(o.y||0)+q[1],o.pis[k+1][1]+q[2]],V,W,H);
          var dd=bimPointSegDist(x,y,e1[0],e1[1],e2[0],e2[1]);if(dd<bd){bd=dd;best=o;}
        }
        continue;
      }
      var pg=o.profile?bimProfileGeom(o.profile,g):null,line=bimAlignPolyline(g);
      var sp=line.map(function(r){return toScreen([r.p[0],bimAlignDrawY(o,pg,r.s),r.p[1]],V,W,H);});
      for(k=0;k+1<sp.length;k++){var d=bimPointSegDist(x,y,sp[k][0],sp[k][1],sp[k+1][0],sp[k+1][1]);if(d<bd){bd=d;best=o;}}
      var F=bimProfileViewFrame(o,g,pg,[]);
      if(F&&!best){
        var c0=toScreen(F.at(F.s0,F.e0),V,W,H),c1=toScreen(F.at(F.s1,F.e1),V,W,H);
        if(x>=Math.min(c0[0],c1[0])&&x<=Math.max(c0[0],c1[0])&&y>=Math.min(c0[1],c1[1])&&y<=Math.max(c0[1],c1[1]))best=o;
      }
    }
    return best;
  }
  /* the plan points an alignment covers, in its own frame: its PIs and its profile view's corners */
  function bimAlignExtentPts(o){
    var pts=o.pis.map(function(p){return [p[0],p[1]];}),g=bimAlignGeom(o);
    if(!g.error&&o.profileView&&o.profileView.at){
      var q=bimObjOffset(o),F=bimProfileViewFrame(o,g,o.profile?bimProfileGeom(o.profile,g):null,bimAlignGround(o,g));
      if(F){var a=F.at(F.s0,F.e0),b=F.at(F.s1,F.e1);pts.push([a[0]-q[0],a[2]-q[2]]);pts.push([b[0]-q[0],b[2]-q[2]]);}
    }
    return pts;
  }
  /* ---- __acad3dV127: editing */
  /* An edit, made to a copy and checked before it is kept: fn returns a reason to refuse, or
     nothing. One undo step. */
  function bimAlignEdit(o,fn){
    var c={t:'alignment',pos:bimObjOffset(o),y:o.y,pis:JSON.parse(JSON.stringify(o.pis)),radii:(o.radii||[]).slice(),sta0:isFinite(o.sta0)?o.sta0:0,
      profile:o.profile?JSON.parse(JSON.stringify(o.profile)):null,profileView:o.profileView?JSON.parse(JSON.stringify(o.profileView)):null};
    var why=fn(c);
    if(typeof why==='string'){a3dToast(why);refreshProps();return false;}
    var g=bimAlignGeom(c);
    if(g.error){a3dToast(o.name+' was not changed: '+g.error);refreshProps();return false;}
    if(c.profile){var pg=bimProfileGeom(c.profile,g);if(pg.error){a3dToast(o.name+'\'s profile was not changed: '+pg.error);refreshProps();return false;}}
    pushUndo();
    o.pis=c.pis;o.radii=c.radii;o.sta0=c.sta0;
    if(c.profile)o.profile=c.profile;else delete o.profile;
    if(c.profileView)o.profileView=c.profileView;else delete o.profileView;
    refreshProps();paint();saveSoon();
    return true;
  }
  /* Add PVI: a profile on the ground to start with, then the longest grade split at its middle */
  function bimAlignAddPvi(c){
    var g=bimAlignGeom(c);
    if(g.error)return 'Fix the alignment first: '+g.error;
    if(!c.profile||!c.profile.pvis||c.profile.pvis.length<2){
      var gr=bimAlignGround(c,g,Math.max(g.length/200,0.25)),e0=null,e1=null,y0=(c.y||0)+bimObjOffset(c)[1];
      if(gr.length){var f=gr[0][0],l=gr[gr.length-1];if(Math.abs(f[0]-g.sta0)<1e-6)e0=f[1];if(Math.abs(l[l.length-1][0]-g.sta1)<1e-6)e1=l[l.length-1][1];}
      c.profile={pvis:[{sta:g.sta0,elev:e0!==null?+e0.toFixed(3):y0,L:0},{sta:g.sta1,elev:e1!==null?+e1.toFixed(3):y0,L:0}]};
      return;
    }
    var v=c.profile.pvis,best=0,i;
    for(i=1;i+1<v.length;i++)if(v[i+1].sta-v[i].sta>v[best+1].sta-v[best].sta)best=i;
    var sm=(v[best].sta+v[best+1].sta)/2;
    v.splice(best+1,0,{sta:+sm.toFixed(3),elev:+((v[best].elev+v[best+1].elev)/2).toFixed(3),L:0});
  }
  function bimAlignPropsHtml(o){
    var g=bimAlignGeom(o),r='',i,rp='';
    r+=bimPropRow('Start station (m)','<input type="number" step="any" data-propalign="sta0" value="'+(isFinite(o.sta0)?o.sta0:0)+'">');
    if(g.error)r+=bimPropText('Problem',g.error);
    else{
      r+=bimPropText('Stations',bimFmtStation(g.sta0)+' to '+bimFmtStation(g.sta1));
      r+=bimPropText('Length (m)',bimDispNum(g.length,3));
    }
    for(i=1;i<o.pis.length-1;i++){
      r+=bimPropRow('PI '+(i+1)+' radius (m)','<input type="number" step="any" min="0" data-propalign="r:'+(i-1)+'" value="'+((o.radii&&o.radii[i-1])||0)+'">');
      var p=g.error?null:g.pis[i];
      if(p)r+=bimPropText('PI '+(i+1)+' curve',p.T>0?
        ('\u0394 '+(p.D*180/Math.PI).toFixed(4)+'\u00b0 '+(p.turn>0?'right':'left')+', T '+p.T.toFixed(3)+', L '+p.L.toFixed(3)+', E '+p.E.toFixed(3)+', PC '+bimFmtStation(p.pc)+', PT '+bimFmtStation(p.pt))
        :(p.D>1e-9?'no curve: \u0394 '+(p.D*180/Math.PI).toFixed(4)+'\u00b0, radius 0':'none: the route runs straight through'));
    }
    if(o.profileView){
      r+=bimPropRow('Profile view exaggeration','<input type="number" step="any" min="0.1" data-propalign="vx" value="'+(o.profileView.vx||10)+'">');
      r+=bimPropRow('','<button type="button" class="a3d-pedit" data-propalignact="pv">Move profile view</button> <button type="button" class="a3d-pedit" data-propalignact="pvdel">Remove</button>');
    }else r+=bimPropRow('Profile view','<button type="button" class="a3d-pedit" data-propalignact="pv">Place profile view</button>');
    var h=bimPropGroup('Alignment',r);
    var pr=o.profile,pg=(pr&&!g.error)?bimProfileGeom(pr,g):null;
    if(pr&&pr.pvis){
      for(i=0;i<pr.pvis.length;i++){
        var v=pr.pvis[i],end=(i===0||i===pr.pvis.length-1);
        rp+=bimPropRow('PVI '+(i+1)+' sta / El / L',
          '<input type="number" step="any" style="width:31%" title="Station (m)" data-propalign="pvi:'+i+':sta" value="'+v.sta+'">'+
          '<input type="number" step="any" style="width:31%" title="Elevation (m)" data-propalign="pvi:'+i+':elev" value="'+v.elev+'">'+
          '<input type="number" step="any" min="0" style="width:24%" title="Vertical curve length (m)" data-propalign="pvi:'+i+':L" value="'+(v.L||0)+'"'+(end?' disabled':'')+'>'+
          '<button type="button" class="a3d-bdel" data-propalignact="pvidel:'+i+'" title="Remove this PVI">\u00d7</button>');
      }
      if(pg&&pg.error)rp+=bimPropText('Problem',pg.error);
      else if(pg){
        for(i=0;i<pg.grades.length;i++)rp+=bimPropText('Grade '+(i+1)+' to '+(i+2),(pg.grades[i]*100).toFixed(3)+'%');
        for(i=1;i<pg.pvis.length-1;i++){
          var q=pg.pvis[i];
          if(q.L>0)rp+=bimPropText('PVI '+(i+1)+' curve',q.kind+', A '+q.A.toFixed(3)+'%, K '+(isFinite(q.K)?q.K.toFixed(2):'\u2014')+
            ', PVC '+bimFmtStation(q.pvc)+', PVT '+bimFmtStation(q.pvt)+(q.turnSta!==undefined?', '+(q.kind==='crest'?'high':'low')+' point '+bimFmtStation(q.turnSta)+' El '+q.turnElev.toFixed(3):''));
        }
      }
    }else rp+=bimPropText('Profile','None yet: Add PVI starts one on the ground');
    rp+=bimPropRow('','<button type="button" class="a3d-pedit" data-propalignact="pvadd">Add PVI</button>');
    h+=bimPropGroup('Profile',rp);
    return h;
  }
  function bimAlignPropChange(ev){
    var f=ev.target&&ev.target.closest?ev.target.closest('[data-propalign]'):null;
    if(!f)return false;
    var o=objById(A3D.sel);
    if(!bimIsAlignment(o))return false;
    var k=f.getAttribute('data-propalign'),v=parseFloat(f.value);
    if(!isFinite(v)){a3dToast('That must be a number');refreshProps();return true;}
    if(k==='sta0')bimAlignEdit(o,function(c){var d=v-c.sta0;c.sta0=v;if(c.profile)c.profile.pvis.forEach(function(p){p.sta=+(p.sta+d).toFixed(6);});});
    else if(k==='vx')bimAlignEdit(o,function(c){if(!(v>0))return 'The exaggeration must be more than 0';c.profileView.vx=v;});
    else if(k.indexOf('r:')===0)bimAlignEdit(o,function(c){if(!(v>=0))return 'A radius is 0 (no curve) or more';c.radii[parseInt(k.slice(2),10)]=v;});
    else if(k.indexOf('pvi:')===0){
      var bits=k.split(':'),ix=parseInt(bits[1],10),fld=bits[2];
      bimAlignEdit(o,function(c){
        if(!c.profile||!c.profile.pvis[ix])return 'That PVI is gone';
        if(fld==='L'&&!(v>=0))return 'A vertical curve\'s length is 0 or more';
        c.profile.pvis[ix][fld]=v;
      });
    }
    return true;
  }
  function bimAlignPropClick(ev){
    var b=ev.target&&ev.target.closest?ev.target.closest('[data-propalignact]'):null;
    if(!b)return false;
    var o=objById(A3D.sel),a=b.getAttribute('data-propalignact');
    if(!bimIsAlignment(o))return false;
    if(a==='pv'){bimStartProfileViewTool(o);return true;}
    if(a==='pvdel'){if(bimAlignEdit(o,function(c){c.profileView=null;}))a3dToast(o.name+'\'s profile view removed');return true;}
    if(a==='pvadd'){if(bimAlignEdit(o,bimAlignAddPvi))a3dToast('PVI added to '+o.name+'\'s profile: set its station and elevation');return true;}
    if(a.indexOf('pvidel:')===0){
      var ix=parseInt(a.slice(7),10);
      bimAlignEdit(o,function(c){
        if(!c.profile||!c.profile.pvis[ix])return 'That PVI is gone';
        if(c.profile.pvis.length<=2){c.profile=null;return;}
        c.profile.pvis.splice(ix,1);
      });
      return true;
    }
    return false;
  }
  /* ---- commands */
  function bimAlignmentCommand(){
    var o=objById(A3D.sel);
    if(bimIsAlignment(o)){a3dToast(o.name+' is already an alignment: set it in Properties');return null;}
    if(o&&o.t==='sketch')return bimAlignmentFromSketch(o);
    a3dToast('Draw an open polyline through the PIs, select it, then ALIGNMENT');
    return null;
  }
  /* the alignment a command means: the selected one, or the only one */
  function bimAlignTarget(){
    var o=objById(A3D.sel);
    if(bimIsAlignment(o))return o;
    var all=A3D.objs.filter(bimIsAlignment);
    return all.length===1?all[0]:null;
  }
  function bimStartProfileViewTool(o){
    o=o||bimAlignTarget();
    if(!o){a3dToast('Select an alignment: PROFILEVIEW places its profile view');return false;}
    if(bimAlignProblem(o)){a3dToast(o.name+' cannot be drawn in profile: '+bimAlignProblem(o));return false;}
    closeDlg();
    bimEnterDraftingMode();
    var lvl=bimGetActiveLevel();
    A3D.sk={tool:'profileview',pts:[],y:lvl?lvl.elev:0,on:null,alignId:o.id};
    a3dToast('Profile view: click where its lower-left corner goes');
    paint();
    return true;
  }
  function bimPlaceProfileView(o,pt){
    var q=bimObjOffset(o);
    if(bimAlignEdit(o,function(c){c.profileView={at:[pt[0]-q[0],pt[1]-q[2]],vx:(c.profileView&&c.profileView.vx)||10};}))
      a3dToast(o.name+'\'s profile view placed'+(o.profile?'':': Add PVI in Properties to design its profile'));
  }
  function bimStartStationTool(){
    var o=bimAlignTarget();
    if(!o){a3dToast('Select an alignment: STATION reports a point\'s station and offset along it');return false;}
    if(bimAlignProblem(o)){a3dToast(o.name+' has no stations: '+bimAlignProblem(o));return false;}
    closeDlg();
    bimEnterDraftingMode();
    var lvl=bimGetActiveLevel();
    A3D.sk={tool:'station',pts:[],y:lvl?lvl.elev:0,on:null,alignId:o.id};
    A3D.stationMark=null;
    a3dToast('Station: click points to read their station and offset along '+o.name+'; Escape to finish');
    paint();
    return true;
  }
  function bimStationAt(id,pt){
    var o=objById(id);
    if(!bimIsAlignment(o)){a3dToast('The alignment is gone');A3D.sk=null;return null;}
    var g=bimAlignGeom(o);
    if(g.error){a3dToast(o.name+': '+g.error);return null;}
    var so=bimAlignStationOffset(g,pt);
    A3D.stationMark={id:id,p:[pt[0],pt[1]],foot:so.foot,sta:so.sta,off:so.off};
    a3dToast('Sta '+bimFmtStation(so.sta)+', '+Math.abs(so.off).toFixed(3)+' m '+(Math.abs(so.off)<0.0005?'on the line':(so.off>0?'right':'left'))+
      (so.beyond?' ('+so.beyond+')':'')+' -- '+o.name);
    paint();
    return so;
  }
  function drawStationMark(ctx,V,W,H){
    var m=A3D.stationMark;
    if(!m||!A3D.sk||A3D.sk.tool!=='station')return;
    var o=objById(m.id);if(!o)return;
    var y=(o.y||0)+bimObjOffset(o)[1],a=toScreen([m.p[0],y,m.p[1]],V,W,H),b=toScreen([m.foot[0],y,m.foot[1]],V,W,H);
    ctx.save();
    ctx.strokeStyle='#ffd479';ctx.fillStyle='#ffd479';ctx.lineWidth=1.2;ctx.setLineDash([4,3]);
    ctx.beginPath();ctx.moveTo(a[0],a[1]);ctx.lineTo(b[0],b[1]);ctx.stroke();ctx.setLineDash([]);
    ctx.beginPath();ctx.moveTo(a[0]-5,a[1]-5);ctx.lineTo(a[0]+5,a[1]+5);ctx.moveTo(a[0]+5,a[1]-5);ctx.lineTo(a[0]-5,a[1]+5);ctx.stroke();
    ctx.font='11px system-ui,sans-serif';ctx.textAlign='left';ctx.textBaseline='bottom';
    ctx.fillText(bimFmtStation(m.sta)+'  '+Math.abs(m.off).toFixed(3)+' m '+(m.off>=0?'R':'L'),a[0]+8,a[1]-6);
    ctx.restore();
  }
  /* ---- __acad3dV127: the tables, and the route for export */
  function bimAlignScheduleRows(){
    var rows=[],i,j;
    A3D.objs.filter(bimIsAlignment).forEach(function(o){
      var g=bimAlignGeom(o);
      if(g.error){rows.push({alignment:o.name,pi:'',note:g.error});return;}
      for(j=0;j<g.pis.length;j++){
        var p=g.pis[j],st=j===0?g.sta0:(j===g.pis.length-1?g.sta1:(p.T>0?p.pc+p.T:bimAlignStationOffset(g,p.pt).sta));
        rows.push({alignment:o.name,pi:'PI '+(j+1),station:bimFmtStation(st),delta:p.D>1e-9?+(p.D*180/Math.PI).toFixed(4):'',
          turn:p.D>1e-9?(p.turn>0?'Right':'Left'):'',radius:p.T>0?p.R:'',tangent:p.T>0?p.T:'',length:p.T>0?p.L:'',external:p.T>0?p.E:'',
          pc:p.T>0?bimFmtStation(p.pc):'',pt:p.T>0?bimFmtStation(p.pt):'',note:j===0?'Beginning':(j===g.pis.length-1?'End, length '+g.length.toFixed(3)+' m':'')});
      }
    });
    return rows;
  }
  function bimProfileScheduleRows(){
    var rows=[];
    A3D.objs.filter(bimIsAlignment).forEach(function(o){
      if(!o.profile)return;
      var g=bimAlignGeom(o),pg=g.error?{error:g.error}:bimProfileGeom(o.profile,g),j;
      if(pg.error){rows.push({alignment:o.name,pvi:'',note:pg.error});return;}
      for(j=0;j<pg.pvis.length;j++){
        var v=pg.pvis[j];
        rows.push({alignment:o.name,pvi:'PVI '+(j+1),station:bimFmtStation(v.sta),elev:v.elev,
          gin:v.gIn===null?'':v.gIn*100,gout:v.gOut===null?'':v.gOut*100,L:v.L>0?v.L:'',K:v.L>0&&isFinite(v.K)?v.K:'',
          kind:v.L>0?v.kind:'',turn:v.turnSta!==undefined?(v.kind==='crest'?'High ':'Low ')+bimFmtStation(v.turnSta)+', El '+v.turnElev.toFixed(3):'',note:''});
      }
    });
    return rows;
  }
  /* the route and its labelled points, in world plan terms, for the exporters */
  function bimAlignExport(o){
    var g=bimAlignGeom(o);
    if(g.error)return {pts:o.pis.map(function(p){var q=bimObjOffset(o);return [p[0]+q[0],p[1]+q[2]];}),labels:[]};
    var labels=[{p:g.start,t:'BEG '+bimFmtStation(g.sta0)}],j;
    for(j=0;j<g.pis.length;j++)if(g.pis[j].T>0){labels.push({p:g.pis[j].PC,t:'PC '+bimFmtStation(g.pis[j].pc)});labels.push({p:g.pis[j].PT,t:'PT '+bimFmtStation(g.pis[j].pt)});}
    labels.push({p:g.end,t:'END '+bimFmtStation(g.sta1)});
    return {pts:bimAlignPolyline(g).map(function(r){return r.p;}),labels:labels};
  }
  function bimSetTrueNorth(deg){
    var v=parseFloat(deg);
    if(!isFinite(v)){a3dToast('True North must be a number of degrees');return false;}
    v=((v%360)+360)%360;if(v>180)v-=360;
    pushUndo();
    A3D.site.trueNorth=v;
    refreshProps();paint();saveSoon();
    a3dToast('True North set to '+v.toFixed(2)+' deg from project north');
    return true;
  }
  /* __acad3dV108: SURVEY. The base point is the survey coordinate that sits at model 0,0 and the
     elevation that sits at model y 0; it is kept on the site so a second survey lands in the same
     place, and it is offered back here. Blank northing and easting take the first point. */
  function bimImportSurvey(res,fmt,units,base,checkCode){
    try{
      pushUndo();
      A3D.site.surveyBase={n:base.n,e:base.e,z:base.z,units:units};
      /* __acad3dV138: shots coded as checks are kept out of the surface, to measure it */
      var code=String(checkCode==null?BIM_SURVEY_CHECK_CODE:checkCode).replace(/^\s+|\s+$/g,'').toUpperCase(),pts=[],chk=[],q;
      for(q=0;q<res.points.length;q++){
        if(code&&String(res.points[q].d||'').replace(/^\s+/,'').toUpperCase().indexOf(code)===0)chk.push(res.points[q]);else pts.push(res.points[q]);
      }
      var model=bimSurveyToModel(pts,units,base,bimTrueNorthDeg());
      var o=bimCreateTerrain(model,{format:fmt,units:units,base:{n:base.n,e:base.e,z:base.z},skipped:res.bad.slice(0,50),checkCode:code},true);
      if(o&&chk.length)o.checks=bimSurveyToModel(chk,units,base,bimTrueNorthDeg());
      if(o&&res.bad.length)a3dToast(o.name+': '+o.survey.length+' points; line'+(res.bad.length===1?' ':'s ')+res.bad.slice(0,8).join(', ')+(res.bad.length>8?' ...':'')+' could not be read');
      if(o)fitScene();
      return o;
    }catch(e){
      console.warn('[BIM] survey import',e);
      a3dToast('The survey could not be made into a surface - see the console');
      return null;
    }
  }
  function openSurveyDlg(){
    closeDlg();
    var b=(A3D.site&&A3D.site.surveyBase)||null,d=document.createElement('div'),u=b?b.units:'m';
    function opt(v,t,cur){return '<option value="'+v+'"'+(v===cur?' selected':'')+'>'+t+'</option>';}
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">Survey Points to Surface</div><div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Points, one per line</label><textarea data-a3dp="pts" rows="8" cols="46" placeholder="1, 5000.00, 2000.00, 342.10, EP"></textarea></div>'+
      '<div class="a3d-dlgrow"><button type="button" data-a3dlg="file">Open a File ...</button> <span data-a3dp="fname" class="a3d-dlgnote"></span>'+
        '<input type="file" data-a3dp="filein" accept=".txt,.csv,.pnezd,.penzd,.xyz,.asc,text/plain,text/csv" hidden></div>'+   /* __acad3dV138 */
      '<div class="a3d-dlgrow"><label>Columns</label><select data-a3dp="fmt">'+opt('PNEZD','Point, Northing, Easting, Elevation, Description','PNEZD')+
        opt('PENZD','Point, Easting, Northing, Elevation, Description','')+opt('NEZ','Northing, Easting, Elevation','')+opt('ENZ','Easting, Northing, Elevation','')+'</select></div>'+
      '<div class="a3d-dlgrow"><label>Units</label><select data-a3dp="units">'+opt('m','metres',u)+opt('ft','international feet',u)+opt('usft','US survey feet',u)+'</select></div>'+
      '<div class="a3d-dlgrow"><label>Base northing (blank: the first point)</label><input type="number" step="any" data-a3dp="bn" value="'+(b?b.n:'')+'"></div>'+
      '<div class="a3d-dlgrow"><label>Base easting (blank: the first point)</label><input type="number" step="any" data-a3dp="be" value="'+(b?b.e:'')+'"></div>'+
      '<div class="a3d-dlgrow"><label>Elevation at model 0 (blank: 0)</label><input type="number" step="any" data-a3dp="bz" value="'+(b?b.z:'')+'"></div>'+
      '<div class="a3d-dlgrow"><label>Check shots: description starts with (blank: none)</label><input type="text" data-a3dp="chk" value="'+BIM_SURVEY_CHECK_CODE+'" '+
        'title="Shots kept out of the surface and measured against it"></div>'+   /* __acad3dV138 */
      '<div id="a3d-dlgerr"></div></div><div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">Make Surface</button></div>';
    el.root.appendChild(d);el.dlg=d;
    function q(k){return d.querySelector('[data-a3dp="'+k+'"]').value;}
    function submit(){
      var fmt=q('fmt'),units=q('units'),res=bimParseSurvey(q('pts'),fmt),err=d.querySelector('#a3d-dlgerr'),bn=q('bn'),be=q('be'),bz=q('bz'),base;
      if(res.error){err.textContent=res.error;return;}
      if(res.points.length<3){err.textContent='A surface needs at least 3 points; '+res.points.length+' read'+(res.bad.length?(', line'+(res.bad.length===1?' ':'s ')+res.bad.slice(0,6).join(', ')+' not numbers'):'');return;}
      base={n:bn===''?res.points[0].n:parseFloat(bn),e:be===''?res.points[0].e:parseFloat(be),z:bz===''?0:parseFloat(bz)};
      if(!isFinite(base.n)||!isFinite(base.e)||!isFinite(base.z)){err.textContent='The base point must be numbers';return;}
      var chk=q('chk');
      closeDlg();
      bimImportSurvey(res,fmt,units,base,chk);   /* __acad3dV138: the check shots */
    }
    /* __acad3dV138: a survey file, read into the box */
    var fin=d.querySelector('[data-a3dp="filein"]');
    fin.addEventListener('change',function(){
      var f=fin.files&&fin.files[0];if(!f)return;
      var rd=new FileReader();
      rd.onload=function(){d.querySelector('[data-a3dp="pts"]').value=String(rd.result||'');d.querySelector('[data-a3dp="fname"]').textContent=f.name;};
      rd.onerror=function(){d.querySelector('#a3d-dlgerr').textContent=f.name+' could not be read';};
      rd.readAsText(f);
    });
    d.addEventListener('click',function(ev){var bt=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;if(!bt)return;
      if(bt.getAttribute('data-a3dlg')==='file'){fin.click();return;}
      if(bt.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();});
    d.addEventListener('keydown',function(ev){
      if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}
      else if(ev.key==='Enter'&&!(ev.target&&ev.target.tagName==='TEXTAREA')){ev.preventDefault();ev.stopPropagation();submit();}
      else ev.stopPropagation();
    });
    d.querySelector('[data-a3dp="pts"]').focus();
  }
  function openTrueNorthDlg(){
    closeDlg();
    var d=document.createElement('div');
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">True North</div><div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Angle from project north, clockwise (deg)</label><input type="number" step="any" data-a3dp="tn" value="'+bimTrueNorthDeg()+'"></div>'+
      '</div><div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">OK</button></div>';
    el.root.appendChild(d);el.dlg=d;
    var tI=d.querySelector('[data-a3dp="tn"]');
    function submit(){var v=tI.value;closeDlg();bimSetTrueNorth(v);}
    d.addEventListener('click',function(ev){var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;if(!b)return;if(b.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();});
    d.addEventListener('keydown',function(ev){if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}});
    tI.focus();tI.select();
  }
  function bimRemoveGrid(id){
    var i;
    for(i=0;i<A3D.grids.length;i++)if(A3D.grids[i].id===id){
      pushUndo();
      var nm=A3D.grids[i].name;
      A3D.grids.splice(i,1);
      if(A3D.selGrid===id)A3D.selGrid=null;   /* __acad3dV98 */
      refreshLevels();refreshTree();paint();saveSoon();
      a3dToast('Grid '+nm+' deleted');
      return true;
    }
    return false;
  }

