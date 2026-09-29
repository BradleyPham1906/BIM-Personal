"""patch_phase127b.py -- V127: the alignment drawn, picked, framed and transformed.

The route is drawn from its derivation (bimAlignGeom): tangents, and true arcs flattened to the V88
chord tolerance -- never the PI polygon, which is shown dashed only while the alignment is
selected, with its PIs. Stations are ticked along it, minor every 20 m and major, labelled, every
100 m (Civil 3D's major/minor label set), and every PC and PT is marked with its station. Ticks
and labels are sized in pixels and thinned when the view is too far out to read them.

With a profile, the route is drawn at its design elevations -- the 3D view shows the road line
rising and falling -- and the profile view, when placed (PROFILEVIEW, 127c), is drawn in model
space at its point, as Civil 3D draws one: a station / elevation grid, the ground from the surface
under the route (thin), the design profile (bold), each PVI and each vertical curve's length, K and
high or low point. Its vertical scale is exaggerated (10x unless set).

An alignment is picked on its route or anywhere in its profile view; it frames and exports with
its extent; Rotate, Mirror and the gizmo move its PIs and its profile view with it."""
NAME = 'patch_phase127b.py'
BASE = '133771d3d18e42854c55d1c1a7ac7198d793e5ce01dbac145c885a8c32948bfb'
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


rep("""  function bimSetTrueNorth(deg){""", r"""  /* ---- __acad3dV127: drawing */
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
            var lab='PVI '+bimFmtStation(pv.sta)+'  El '+pv.elev.toFixed(2)+(pv.L>0?'  L '+bimTrimNum(pv.L.toFixed(2))+'  K '+(isFinite(pv.K)?pv.K.toFixed(1):'—'):'');
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
  function bimSetTrueNorth(deg){""")

# paint and pick
rep("""    drawProperties(ctx,V,W,H);     /* __acad3dV103: under the model, like grids */""",
    """    drawProperties(ctx,V,W,H);     /* __acad3dV103: under the model, like grids */
    drawAlignments(ctx,V,W,H);     /* __acad3dV127 */""")
rep("""||bimPickProperty(x,y);   /* __acad3dV98""", """||bimPickProperty(x,y)||bimPickAlignment(x,y);   /* __acad3dV127: alignments after property lines; __acad3dV98""")

# extents
rep("""    else if(bimIsProperty(o)){   /* __acad3dV103: world points, so the offset below is taken off */""",
    """    else if(bimIsAlignment(o))pts=bimAlignExtentPts(o);   /* __acad3dV127 */
    else if(bimIsProperty(o)){   /* __acad3dV103: world points, so the offset below is taken off */""")
rep("""      }else if(bimIsProperty(o)||((o.t==='text'||o.t==='roomtag')&&o.pt)){""",
    """      }else if(bimIsAlignment(o)){   /* __acad3dV127 */
        var aep=bimAlignExtentPts(o);
        for(j=0;j<aep.length;j++){
          var awp=bimWorldPt(o,aep[j],o.y||0);
          for(k=0;k<3;k++){if(awp[k]<mn[k])mn[k]=awp[k];if(awp[k]>mx[k])mx[k]=awp[k];}
          any=true;
        }
      }else if(bimIsProperty(o)||((o.t==='text'||o.t==='roomtag')&&o.pt)){""")

# transforms: the PIs and the profile view's point move; the radii and the profile are the route's own
rep("""    if(o.t==='sketch')return {kind:'sketch',pts:o.pts.map(transformPt),y:o.y};""",
    """    if(o.t==='sketch')return {kind:'sketch',pts:o.pts.map(transformPt),y:o.y};
    if(o.t==='alignment')return {kind:'alignment',pis:o.pis.map(transformPt),pv:o.profileView&&o.profileView.at?transformPt(o.profileView.at):null,k:xf&&xf.kind==='scale'&&xf.k>0?xf.k:1};   /* __acad3dV127 */""")
rep("""    else if(g.kind==='pos'){copy.t=o.t;copy.name=o.name+' mirror';copy.pos=g.pos;if(o.prm)copy.prm=JSON.parse(JSON.stringify(o.prm));}
    return copy;""", """    else if(g.kind==='pos'){copy.t=o.t;copy.name=o.name+' mirror';copy.pos=g.pos;if(o.prm)copy.prm=JSON.parse(JSON.stringify(o.prm));}
    else if(g.kind==='alignment'){   /* __acad3dV127 */
      A3D.counts.alignment=(A3D.counts.alignment||0)+1;copy.t='alignment';copy.name='Alignment_'+A3D.counts.alignment;
      copy.pis=g.pis;copy.radii=(o.radii||[]).slice();copy.sta0=o.sta0||0;copy.y=o.y||0;
      if(o.profile)copy.profile=JSON.parse(JSON.stringify(o.profile));
      if(o.profileView)copy.profileView={at:g.pv,vx:o.profileView.vx};
    }
    return copy;""")
rep("""    else if(g.kind==='pos'){o.pos=g.pos;}
    return true;""", """    else if(g.kind==='pos'){o.pos=g.pos;}
    else if(g.kind==='alignment'){o.pis=g.pis;if(g.pv&&o.profileView)o.profileView.at=g.pv;if(g.k!==1)o.radii=(o.radii||[]).map(function(r){return r*g.k;});}   /* __acad3dV127: a scaled route keeps its shape */
    return true;""", 2)

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
