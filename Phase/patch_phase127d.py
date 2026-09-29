"""patch_phase127d.py -- V127: the alignment's tables, and the alignment on paper.

Two schedules in the registry every schedule uses (V125's pattern): Alignment -- each PI's station,
deflection, radius, T, L, E, PC and PT -- and Profile -- each PVI's station and elevation, the grades
in and out, and each vertical curve's length, K, and high or low point. Both read bimAlignGeom and
bimProfileGeom, the derivation the drawing and Properties read, so the three cannot disagree.

DXF, SVG and a sheet's plan viewport draw the route itself -- tangents and flattened arcs, in world
terms -- with its ends, PCs and PTs labelled by station. The profile view is not exported yet."""
NAME = 'patch_phase127d.py'
BASE = 'cacaea952a6ca7e5715c7d7d4ac0fe1ec7a4865209e3dd7e2ce8d354c7221003'
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


rep("""  function bimSetTrueNorth(deg){""", r"""  /* ---- __acad3dV127: the tables, and the route for export */
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
  function bimSetTrueNorth(deg){""")
rep("""    reactions:{label:'Reactions',build:bimReactionRows,""", """    alignment:{label:'Alignment',build:bimAlignScheduleRows,cols:[{key:'alignment',label:'Alignment'},{key:'pi',label:'PI'},{key:'station',label:'Station'},{key:'delta',label:'Deflection (°)'},{key:'turn',label:'Turn'},{key:'radius',label:'Radius (m)',fmt:3},{key:'tangent',label:'T (m)',fmt:3},{key:'length',label:'L (m)',fmt:3},{key:'external',label:'E (m)',fmt:3},{key:'pc',label:'PC'},{key:'pt',label:'PT'},{key:'note',label:'Note'}]},   /* __acad3dV127 */
    profile:{label:'Profile',build:bimProfileScheduleRows,cols:[{key:'alignment',label:'Alignment'},{key:'pvi',label:'PVI'},{key:'station',label:'Station'},{key:'elev',label:'Elevation (m)',fmt:3},{key:'gin',label:'Grade in (%)',fmt:3},{key:'gout',label:'Grade out (%)',fmt:3},{key:'L',label:'Curve L (m)',fmt:2},{key:'K',label:'K',fmt:2},{key:'kind',label:'Curve'},{key:'turn',label:'High / low point'},{key:'note',label:'Note'}]},
    reactions:{label:'Reactions',build:bimReactionRows,""")
rep("""    if(!o||bimIsProperty(o))return [0,0,0];   /* derived in world terms already */""",
    """    if(!o||bimIsProperty(o)||bimIsAlignment(o))return [0,0,0];   /* derived in world terms already; __acad3dV127: so is an alignment */""")
rep("""      }else if(bimIsProperty(o)){   /* __acad3dV103: WORLD points; %%d is the R12 degree mark */""",
    """      }else if(bimIsAlignment(o)){   /* __acad3dV127 */
        var axD=bimAlignExport(o),alD;
        poly(axD.pts,false,lay);
        for(alD=0;alD<axD.labels.length;alD++)text(axD.labels[alD].p,axD.labels[alD].t,0.25,lay);
      }else if(bimIsProperty(o)){   /* __acad3dV103: WORLD points; %%d is the R12 degree mark */""")
rep("""      }else if(bimIsProperty(o)){   /* __acad3dV103 */
        var pgS=bimPropertyGeometry(o),lks;""", """      }else if(bimIsAlignment(o)){   /* __acad3dV127 */
        var axS=bimAlignExport(o),alS;
        poly(axS.pts,false,lay,o.id,rg,false);
        for(alS=0;alS<axS.labels.length;alS++)text(axS.labels[alS].p,axS.labels[alS].t,0.25,lay,o.id,rg);
      }else if(bimIsProperty(o)){   /* __acad3dV103 */
        var pgS=bimPropertyGeometry(o),lks;""")
rep("""      }else if(bimIsProperty(o)){   /* __acad3dV103 */
        var pgV=bimPropertyGeometry(o),lkv;""", """      }else if(bimIsAlignment(o)){   /* __acad3dV127 */
        var axV=bimAlignExport(o),alV;
        poly(axV.pts,false,o.id,null,rg,false);
        for(alV=0;alV<axV.labels.length;alV++)txt(axV.labels[alV].p,axV.labels[alV].t,2.4,o.id,null,rg);
      }else if(bimIsProperty(o)){   /* __acad3dV103 */
        var pgV=bimPropertyGeometry(o),lkv;""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
