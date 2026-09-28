"""patch_phase125d.py -- V125: the analysis display, its commands and its tables.

The owner, mid-phase: "make sure this feature is cleanly add-in the design and not overloading the
UI/UX. everything must be consistent ... look into rhinoceros documentation". Rhino shows an analysis
as a DISPLAY MODE over the model already on screen -- Zebra, CurvatureAnalysis, DraftAngleAnalysis --
turned on by its command and off by its Off form (reference/research-structural-ui.md). So:

  ANALYZE      solves the frame for the chosen combination and turns the analysis display on:
               the analytical lines, a diagram along each member (bending moment unless another is
               chosen) and the deflected shape, drawn over the model, scaled to it and labelled with
               each member's peak. It says the headline numbers Karamba reports: the largest moment,
               the largest deflection with its span ratio, and the equilibrium check.
  ANALYZEOFF   turns it off.

Results belong to the model they were solved for. Every paint compares the model's signature -- its
nodes, members, sections, releases, supports and loads, the combination and self-weight -- with the
one solved; when they differ the display draws no result and says it is out of date, never a stale
answer that looks current. The two tables, Member Forces and Reactions, are schedules in the existing
registry (V74), read from the same solve."""
NAME = 'patch_phase125d.py'
BASE = 'd9d274be0be220ed0aaf857fca5f30ca954c5fb7edb62057dd75ca6e818d58ab'
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


rep("""  function bimToggleTrib(){
""", r"""  /* ================= __acad3dV125: the analysis display ================= */
  var BIM_DIAGRAMS={M:'Bending moment (kN·m)',N:'Axial force (kN)',V:'Shear (kN)'};
  /* what the solve depends on: when it changes, the result on screen is out of date */
  function bimStructSig(model){
    var loads=model.members.map(function(m){var st=bimStructOf(objById(m.id));return [m.id,st.loads||[],st.ends||'',st.support||''];});
    return JSON.stringify({n:model.nodes.map(function(n){return [n.p,n.sup];}),
      e:model.els.map(function(e){return [e.n1,e.n2,e.E,e.G,e.rho,e.sec,e.rel,e.ax.ey];}),
      l:loads,c:A3D_STRUCT.combo,w:A3D_STRUCT.selfWeight});
  }
  /* Solve, or return the result already solved for exactly this model. */
  function bimStructAnalyze(){
    var model=bimAnalyticalModel(),sig=bimStructSig(model);
    if(A3D_STRUCT.res&&A3D_STRUCT.res.sig===sig)return A3D_STRUCT.res;
    var combo=bimCombo(A3D_STRUCT.combo)||BIM_COMBOS[0],res;
    try{res=bimFrameSolve(model,combo,A3D_STRUCT.selfWeight);}
    catch(eS){console.warn('[BIM] The frame could not be solved',eS);res={error:'The frame could not be solved - see the console'};}
    res.sig=sig;res.model=model;
    A3D_STRUCT.res=res;
    return res;
  }
  /* the last result, if it is still the model's -- otherwise null */
  function bimStructCurrent(){
    var r=A3D_STRUCT.res;
    if(!r||r.error)return null;
    return bimStructSig(bimAnalyticalModel())===r.sig?r:null;
  }
  /* Karamba's headline numbers: the largest moment, the largest deflection and its span ratio, and
     equilibrium */
  function bimStructHeadline(r){
    var mM=null,mD=null,i,a;
    for(i=0;i<r.members.length;i++){
      var m=r.members[i];
      a=Math.max(Math.abs(m.Mz.v),Math.abs(m.My.v));
      if(!mM||a>mM.v)mM={v:a,name:m.name};
      if(!mD||m.drel>mD.v)mD={v:m.drel,name:m.name,L:m.L};
    }
    var ld=r.equilibrium.load,re=r.equilibrium.reaction;
    return {moment:mM,defl:mD,
      ratio:mD&&mD.v>1e-9?Math.round(mD.L/mD.v):null,
      load:Math.sqrt(ld[0]*ld[0]+ld[1]*ld[1]+ld[2]*ld[2]),reaction:Math.sqrt(re[0]*re[0]+re[1]*re[1]+re[2]*re[2]),
      balanced:r.equilibrium.err<=1e-6*Math.max(1,Math.abs(ld[1])+Math.abs(ld[0])+Math.abs(ld[2]))};
  }
  function bimStructSummary(r){
    var h=bimStructHeadline(r);
    return r.combo+': '+r.members.length+' member(s). Largest moment '+(h.moment?h.moment.v.toFixed(1)+' kN·m ('+h.moment.name+')':'none')+
      '. Largest deflection '+(h.defl?(h.defl.v*1000).toFixed(1)+' mm'+(h.ratio?' = L/'+h.ratio:'')+' ('+h.defl.name+')':'none')+
      '. Loads '+h.load.toFixed(1)+' kN, reactions '+h.reaction.toFixed(1)+' kN'+(h.balanced?'':' -- NOT in equilibrium')+'.';
  }
  function bimAnalyzeCommand(){
    A3D_STRUCT.res=null;
    var r=bimStructAnalyze();
    if(r.error){A3D_STRUCT.show=false;paint();refreshProps();a3dToast(r.error);return false;}
    A3D_STRUCT.show=true;
    if(!A3D_STRUCT.diagram)A3D_STRUCT.diagram='M';
    paint();refreshProps();
    var na=r.model.notAnalysed,k,parts=[];
    for(k in na)if(na.hasOwnProperty(k))parts.push(na[k]+' '+k+(na[k]===1?'':'s'));
    a3dToast(bimStructSummary(r)+(parts.length?' Not in the frame: '+parts.join(', ')+'.':''));
    return true;
  }
  function bimAnalyzeOff(){
    A3D_STRUCT.show=false;paint();refreshProps();
    a3dToast('Analysis display off');
    return true;
  }
  /* the value a diagram shows at one sample */
  function bimDiagramValue(s,kind){
    return kind==='N'?s.N:(kind==='V'?s.Vy:s.Mz);
  }
  function drawStructResults(ctx,V,W,H){
    A3D.lastStructDrawn=null;
    if(!A3D_STRUCT.show||A3D.section||A3D.sheetCapture)return;
    ctx.save();
    try{
      var r=bimStructCurrent();
      if(!r){
        ctx.font='12px sans-serif';ctx.textAlign='left';ctx.textBaseline='top';
        var msg='Analysis results are out of date - run ANALYZE';
        ctx.lineWidth=3;ctx.strokeStyle='rgba(0,0,0,0.75)';ctx.strokeText(msg,14,14);
        ctx.fillStyle='#ffe8a3';ctx.fillText(msg,14,14);
        A3D.lastStructDrawn={stale:true};
        ctx.restore();return;
      }
      var m=r.model,i,j,k,drawn={stale:false,lines:0,diagram:A3D_STRUCT.diagram||'',diagPts:0,deflPts:0,labels:[]};
      /* the model's size sets the scales: a diagram's peak is an eighth of it, the largest movement a
         twentieth */
      var mn=[1e9,1e9,1e9],mx=[-1e9,-1e9,-1e9];
      for(i=0;i<m.nodes.length;i++)for(k=0;k<3;k++){mn[k]=Math.min(mn[k],m.nodes[i].p[k]);mx[k]=Math.max(mx[k],m.nodes[i].p[k]);}
      var ext=Math.max(bimVLen(bimVSub(mx,mn)),1);
      function sc(p){var q=toScreen(p,V,W,H);return q&&isFinite(q[0])&&isFinite(q[1])?q:null;}
      /* the analytical lines */
      ctx.setLineDash([]);ctx.lineWidth=1.5;ctx.strokeStyle='#5ec8f0';
      for(i=0;i<m.els.length;i++){
        var a=sc(m.nodes[m.els[i].n1].p),b=sc(m.nodes[m.els[i].n2].p);
        if(!a||!b)continue;
        ctx.beginPath();ctx.moveTo(a[0],a[1]);ctx.lineTo(b[0],b[1]);ctx.stroke();drawn.lines++;
      }
      /* supports: a filled triangle fixed, an open one pinned */
      for(i=0;i<m.nodes.length;i++){
        var nd=m.nodes[i];if(!nd.sup)continue;
        var sp=sc(nd.p);if(!sp)continue;
        ctx.beginPath();ctx.moveTo(sp[0],sp[1]);ctx.lineTo(sp[0]-7,sp[1]+11);ctx.lineTo(sp[0]+7,sp[1]+11);ctx.closePath();
        ctx.strokeStyle='#5ec8f0';ctx.fillStyle='#5ec8f0';
        if(nd.sup==='fixed')ctx.fill();else ctx.stroke();
      }
      /* the diagram, drawn on each member's local y side: a sagging moment below a beam */
      var kind=A3D_STRUCT.diagram,peak=0;
      if(BIM_DIAGRAMS[kind]){
        for(i=0;i<r.members.length;i++)for(j=0;j<r.members[i].samples.length;j++)peak=Math.max(peak,Math.abs(bimDiagramValue(r.members[i].samples[j],kind)));
        var dsc=peak>1e-9?ext/8/peak:0;
        drawn.diagScale=dsc;
        ctx.lineWidth=1.2;ctx.strokeStyle=kind==='N'?'#9be38a':(kind==='V'?'#f5a3ff':'#ff9d6b');
        ctx.fillStyle=kind==='N'?'rgba(155,227,138,0.10)':(kind==='V'?'rgba(245,163,255,0.10)':'rgba(255,157,107,0.10)');
        for(i=0;i<r.members.length;i++){
          var rm=r.members[i],mm=null;
          for(k=0;k<m.members.length;k++)if(m.members[k].id===rm.id)mm=m.members[k];
          if(!mm||!rm.samples.length)continue;
          var ey=mm.ax.ey,pts=[],best=null;
          for(j=0;j<rm.samples.length;j++){
            var s=rm.samples[j],val=bimDiagramValue(s,kind);
            var base=[mm.p1[0]+mm.ax.ex[0]*s.s,mm.p1[1]+mm.ax.ex[1]*s.s,mm.p1[2]+mm.ax.ex[2]*s.s];
            var off=kind==='M'?-val*dsc:val*dsc;
            pts.push({b:base,o:[base[0]+ey[0]*off,base[1]+ey[1]*off,base[2]+ey[2]*off]});
            if(!best||Math.abs(val)>Math.abs(best.v))best={v:val,o:pts[pts.length-1].o};
          }
          var b0=sc(pts[0].b),poly=[];
          for(j=0;j<pts.length;j++){var q=sc(pts[j].o);if(q)poly.push(q);}
          var b1=sc(pts[pts.length-1].b);
          if(b0&&b1&&poly.length>1){
            ctx.beginPath();ctx.moveTo(b0[0],b0[1]);
            for(j=0;j<poly.length;j++)ctx.lineTo(poly[j][0],poly[j][1]);
            ctx.lineTo(b1[0],b1[1]);ctx.closePath();ctx.fill();ctx.stroke();
            drawn.diagPts+=poly.length;
          }
          /* the member's peak, where it is -- only where it matters, to keep the picture clear */
          if(best&&peak>0&&Math.abs(best.v)>=0.05*peak){
            var lp=sc(best.o);
            if(lp){
              var txt=best.v.toFixed(1);
              ctx.font='11px sans-serif';ctx.textAlign='center';ctx.textBaseline='middle';
              ctx.lineWidth=3;ctx.strokeStyle='rgba(0,0,0,0.75)';ctx.strokeText(txt,lp[0],lp[1]);
              ctx.fillStyle='#fff3e6';ctx.fillText(txt,lp[0],lp[1]);
              drawn.labels.push({member:rm.name,v:best.v});
              ctx.lineWidth=1.2;ctx.strokeStyle=kind==='N'?'#9be38a':(kind==='V'?'#f5a3ff':'#ff9d6b');
            }
          }
        }
      }
      /* the deflected shape, dashed, at a stated scale */
      if(A3D_STRUCT.deflected){
        var dmax=0;
        for(i=0;i<r.members.length;i++)dmax=Math.max(dmax,r.members[i].dmax);
        var fs=dmax>1e-12?ext/20/dmax:0;
        drawn.deflScale=fs;
        ctx.setLineDash([5,4]);ctx.lineWidth=1.4;ctx.strokeStyle='#ffd24a';
        for(i=0;i<r.members.length;i++){
          var rs=r.members[i],m2=null;
          for(k=0;k<m.members.length;k++)if(m.members[k].id===rs.id)m2=m.members[k];
          if(!m2)continue;
          ctx.beginPath();var st=false;
          for(j=0;j<rs.samples.length;j++){
            var sj=rs.samples[j],bp=[m2.p1[0]+m2.ax.ex[0]*sj.s+sj.d[0]*fs,m2.p1[1]+m2.ax.ex[1]*sj.s+sj.d[1]*fs,m2.p1[2]+m2.ax.ex[2]*sj.s+sj.d[2]*fs];
            var qq=sc(bp);if(!qq)continue;
            if(st)ctx.lineTo(qq[0],qq[1]);else{ctx.moveTo(qq[0],qq[1]);st=true;}
            drawn.deflPts++;
          }
          ctx.stroke();
        }
        ctx.setLineDash([]);
      }
      /* what is shown, stated once */
      var cap=r.combo+(BIM_DIAGRAMS[kind]?'  ·  '+BIM_DIAGRAMS[kind]:'')+
        (A3D_STRUCT.deflected&&drawn.deflScale?'  ·  deflection x'+Math.round(drawn.deflScale):'');
      ctx.font='12px sans-serif';ctx.textAlign='left';ctx.textBaseline='top';
      ctx.lineWidth=3;ctx.strokeStyle='rgba(0,0,0,0.75)';ctx.strokeText(cap,14,14);
      ctx.fillStyle='#dfe7f1';ctx.fillText(cap,14,14);
      drawn.caption=cap;
      A3D.lastStructDrawn=drawn;
    }catch(e){
      console.warn('[BIM] analysis display',e);
      if(!A3D.structWarned){A3D.structWarned=true;a3dToast('The analysis display could not be drawn');}
    }
    ctx.restore();
  }
  /* the two tables */
  function bimMemberForceRows(){
    var r=bimStructAnalyze();
    if(r.error)return [{member:'',note:r.error}];
    return r.members.map(function(m){
      return {member:m.name,kind:m.kind==='beam'?'Beam':'Column',combo:r.combo,length:m.L,
        tension:Math.max(m.N[1],0),compression:Math.max(-m.N[0],0),shear:m.V,mz:m.Mz.v,my:m.My.v,
        defl:m.drel*1000,ratio:m.drel>1e-9?'L/'+Math.round(m.L/m.drel):'',note:''};
    });
  }
  function bimReactionRows(){
    var r=bimStructAnalyze();
    if(r.error)return [{at:'',note:r.error}];
    return r.reactions.map(function(x){
      var by=objById(x.by);
      return {at:(by?by.name:'')+' base',support:x.sup==='fixed'?'Fixed':'Pinned',combo:r.combo,
        fx:x.R[0],fy:x.R[1],fz:x.R[2],mx:x.R[3],my:x.R[4],mz:x.R[5],note:''};
    });
  }
  function bimToggleTrib(){
""")

rep("""    drawTribAreas(ctx,V,W,H);          /* __acad3dV106 */
""", """    drawTribAreas(ctx,V,W,H);          /* __acad3dV106 */
    drawStructResults(ctx,V,W,H);      /* __acad3dV125: the analysis display */
""")

rep("""    arealevel:{label:'Areas by Level',""", """    memberforces:{label:'Member Forces',build:bimMemberForceRows,cols:[{key:'member',label:'Member'},{key:'kind',label:'Kind'},{key:'combo',label:'Combination'},{key:'length',label:'Length (m)',fmt:2},{key:'tension',label:'Tension (kN)',fmt:1},{key:'compression',label:'Compression (kN)',fmt:1},{key:'shear',label:'Shear (kN)',fmt:1},{key:'mz',label:'Moment, major (kN\\u00b7m)',fmt:1},{key:'my',label:'Moment, minor (kN\\u00b7m)',fmt:1},{key:'defl',label:'Deflection (mm)',fmt:1},{key:'ratio',label:'Span / deflection'},{key:'note',label:'Note'}]},   /* __acad3dV125 */
    reactions:{label:'Reactions',build:bimReactionRows,cols:[{key:'at',label:'At'},{key:'support',label:'Support'},{key:'combo',label:'Combination'},{key:'fx',label:'Fx (kN)',fmt:1},{key:'fy',label:'Fy (kN)',fmt:1},{key:'fz',label:'Fz (kN)',fmt:1},{key:'mx',label:'Mx (kN\\u00b7m)',fmt:1},{key:'my',label:'My (kN\\u00b7m)',fmt:1},{key:'mz',label:'Mz (kN\\u00b7m)',fmt:1},{key:'note',label:'Note'}]},
    arealevel:{label:'Areas by Level',""")

# ---- the commands
rep("""    ['BLOCK',['B','BMAKE'],'blockmake','Save the selection to the library as a block'],""",
    """    ['BLOCK',['B','BMAKE'],'blockmake','Save the selection to the library as a block'],
    /* __acad3dV125: the frame analysis -- a display turned on and off, as Rhino's analysis modes are */
    ['ANALYZE',['ANALYSE','AN'],'analyze','Solve the frame and show its forces and deflection over the model'],
    ['ANALYZEOFF',['ANALYSEOFF'],'analyzeoff','Turn the analysis display off'],""")
rep("""    blockmake:function(){openSaveBlockDlg();},                   /* __acad3dV124 */""",
    """    blockmake:function(){openSaveBlockDlg();},                   /* __acad3dV124 */
    analyze:function(){bimAnalyzeCommand();},                    /* __acad3dV125 */
    analyzeoff:function(){bimAnalyzeOff();},""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
