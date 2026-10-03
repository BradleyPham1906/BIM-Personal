"""patch_phase131a.py -- V131: usages and live areas, the engine.

The first of Giraffe's ideas the owner chose (reference/research-giraffe.md, research-usages.md).
A usage is a named set of assumptions -- a colour, GBA->GFA and GFA->NSA ratios, a floor-to-floor
height, parameters and formulas -- kept with the project's types, and given to a room, a floor or a
mass:
- a MASS is stacked into floors at its usage's floor-to-floor height, and each floor is measured
  by slicing the solid at the floor's mid-height, so a tapered or stepped mass is measured as it is;
- a FLOOR slab is one floor of gross area, its outline's;
- a ROOM is already net, so it counts as NSA, measured, and adds no gross it does not have.
Formulas are read by our own small evaluator: numbers, + - * / ^, brackets, min max round floor
ceil abs sqrt, and the names GBA GFA NSA levels height footprint, the usage's parameters and its
earlier formulas. Never eval; not HyperFormula, which is GPLv3."""
NAME = 'patch_phase131a.py'
BASE = '8d5857417d52274ebe35817b5eedc47866b3f07df62aed64cfaffcdb572459b8'
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


ENGINE = r"""  /* ================= __acad3dV131: usages and live areas =================
     A usage is a set of assumptions (Giraffe's): a colour, the GBA->GFA and GFA->NSA ratios, the
     floor-to-floor height a mass is stacked at, its own parameters and formulas. The library lives
     in the project's types, so the undo, the browser store, the project file and the project tabs
     all carry it without a list of their own. */
  var BIM_USAGE_DEFAULTS=[
    {id:'use-res',name:'Residential',color:'#e8a33d',gfa:0.9,nsa:0.8,ftf:3.1,
      params:[{key:'unitSize',value:75}],formulas:[{key:'units',expr:'floor(NSA / unitSize)'}]},
    {id:'use-off',name:'Office',color:'#4e8fd6',gfa:0.9,nsa:0.85,ftf:3.6,params:[],formulas:[]},
    {id:'use-ret',name:'Retail',color:'#d6584e',gfa:0.95,nsa:0.9,ftf:4.5,params:[],formulas:[]},
    {id:'use-hot',name:'Hotel',color:'#9a6fd0',gfa:0.9,nsa:0.65,ftf:3.2,
      params:[{key:'keySize',value:30}],formulas:[{key:'keys',expr:'floor(NSA / keySize)'}]},
    {id:'use-car',name:'Parking',color:'#8a9099',gfa:0.95,nsa:0,ftf:3,
      params:[{key:'bayArea',value:30}],formulas:[{key:'bays',expr:'floor(GFA / bayArea)'}]}
  ];
  /* the names a formula can always read, and the functions it can call */
  var BIM_EXPR_NAMES={gba:1,gfa:1,nsa:1,levels:1,height:1,footprint:1};
  var BIM_EXPR_FN={min:Math.min,max:Math.max,round:Math.round,floor:Math.floor,ceil:Math.ceil,abs:Math.abs,sqrt:Math.sqrt};
  function bimUsages(){
    bimEnsureTypes();
    if(!Array.isArray(A3D.types.usage))A3D.types.usage=JSON.parse(JSON.stringify(BIM_USAGE_DEFAULTS));
    return A3D.types.usage;
  }
  function bimUsageById(id){
    var L=bimUsages(),i;
    for(i=0;i<L.length;i++)if(L[i].id===id)return L[i];
    return null;
  }
  /* what a usage can be given to: a room, a floor slab, or a mass (a primitive, or a solid that is
     no building element -- a pad) */
  function bimUsageTarget(o){
    if(!o)return '';
    if(o.t==='room'&&o.pts)return 'room';
    if(o.t==='solid'&&o.bim&&o.bim.type==='floor'&&o.bim.profile)return 'floor';
    if(TYPES[o.t]&&o.prm)return 'mass';
    if(o.t==='solid'&&o.mesh&&(!o.bim||!o.bim.type))return 'mass';
    return '';
  }
  /* ---- the plan area of a solid's cross-section at a world elevation ----
     Each triangle the plane crosses gives a segment, its ends computed from each edge's lower vertex
     index so two triangles sharing an edge give the same point; the segments chain into loops, and
     a loop inside an odd number of others is a hole. */
  function bimTriSliceY(m,ia,ib,ic,y){
    var I=[ia,ib,ic],pts=[],k;
    for(k=0;k<3;k++){
      var a=I[k],b=I[(k+1)%3],lo=Math.min(a,b),hi=Math.max(a,b),P=m.v[lo],Q=m.v[hi];
      var dp=P[1]-y,dq=Q[1]-y;
      if((dp>=0)===(dq>=0))continue;
      var s=dp/(dp-dq);
      pts.push([P[0]+(Q[0]-P[0])*s,y,P[2]+(Q[2]-P[2])*s]);
    }
    return pts.length===2?pts:null;
  }
  function bimMeshSliceArea(o,y){
    var m=meshOf(o);
    if(!m||!m.f||!m.v)return 0;
    var q=bimObjOffset(o),ly=y-q[1],edges=[],i,j,fc,seg;
    for(i=0;i<m.f.length;i++){
      fc=m.f[i];
      for(j=2;j<fc.length;j++){seg=bimTriSliceY(m,fc[0],fc[j-1],fc[j],ly);if(seg)edges.push(seg);}
    }
    var loops=bimChainEdgesToLoops(edges),polys=[],area=0,d;
    for(i=0;i<loops.length;i++)polys.push(loops[i].map(function(p){return [p[0],p[2]];}));
    for(i=0;i<polys.length;i++){
      var a=bimPolyArea(polys[i]);
      if(!(a>1e-9))continue;
      d=0;
      for(j=0;j<polys.length;j++)if(j!==i&&bimPointInPoly(polys[i][0],polys[j]))d++;
      area+=(d%2)?-a:a;
    }
    return Math.max(0,area);
  }
  /* the level a floor starting at world elevation y belongs to: the highest at or below it */
  function bimLevelAtElev(y){
    var best=null,low=null,i,lv;
    for(i=0;i<A3D.levels.length;i++){
      lv=A3D.levels[i];
      if(!low||lv.elev<low.elev)low=lv;
      if(lv.elev<=y+1e-6&&(!best||lv.elev>best.elev))best=lv;
    }
    return (best||low||{id:null}).id;
  }
  /* ---- one object, measured ---- */
  function bimUsageMeasure(o){
    var kind=bimUsageTarget(o),u=(kind&&o.usage)?bimUsageById(o.usage):null,k;
    var r={id:o?o.id:null,name:o?o.name:'',kind:kind,usage:u?u.id:null,floors:[],GBA:0,GFA:0,NSA:0,
           levels:0,height:0,footprint:0,netMeasured:false,values:{},errors:{}};
    if(!kind)return r;
    if(kind==='room'){
      r.NSA=o.area>0?o.area:0;r.footprint=r.NSA;r.levels=1;r.netMeasured=true;
      r.floors.push({levelId:o.levelId||null,gba:0,gfa:0,nsa:r.NSA});
    }else if(kind==='floor'){
      var fa=bimPolyArea(o.bim.profile);
      r.GBA=fa;r.footprint=fa;r.levels=1;
      r.floors.push({levelId:o.bim.levelId||null,gba:fa});
    }else{
      var bb=objBBox(o);
      if(!bb)return r;
      var h=bb.mx[1]-bb.mn[1],ftf=(u&&u.ftf>0)?u.ftf:3,n=Math.max(1,Math.floor(h/ftf+1e-6));
      r.height=h;r.levels=n;
      for(k=0;k<n;k++){
        var y0=bb.mn[1]+k*ftf,band=Math.min(ftf,h-k*ftf),a=bimMeshSliceArea(o,y0+band/2);
        r.floors.push({levelId:bimLevelAtElev(y0),gba:a});
        r.GBA+=a;
      }
      r.footprint=r.floors.length?r.floors[0].gba:0;
    }
    if(u&&kind!=='room'){
      r.GFA=r.GBA*u.gfa;r.NSA=r.GFA*u.nsa;
      for(k=0;k<r.floors.length;k++){r.floors[k].gfa=r.floors[k].gba*u.gfa;r.floors[k].nsa=r.floors[k].gfa*u.nsa;}
    }
    if(u)bimUsageValues(u,r);
    return r;
  }
  /* ---- formulas: our own reader. A parse error and an evaluation error each say what is wrong. ---- */
  function bimExprParse(src){
    var s=String(src==null?'':src),i=0,toks=[],c;
    while(i<s.length){
      c=s.charAt(i);
      if(/\s/.test(c)){i++;continue;}
      var mn=/^(\d+\.?\d*(?:[eE][+-]?\d+)?|\.\d+(?:[eE][+-]?\d+)?)/.exec(s.slice(i));
      if(mn){toks.push({t:'n',v:parseFloat(mn[1])});i+=mn[1].length;continue;}
      var mi=/^[A-Za-z_][A-Za-z0-9_]*/.exec(s.slice(i));
      if(mi){toks.push({t:'i',v:mi[0]});i+=mi[0].length;continue;}
      if('+-*/^(),'.indexOf(c)>=0){toks.push({t:c});i++;continue;}
      return {error:'cannot read "'+c+'"'};
    }
    if(!toks.length)return {error:'empty'};
    var p=0;
    function peek(){return toks[p]||{t:''};}
    function fail(m){throw {bimExpr:m};}
    function expr(){var a=term();while(peek().t==='+'||peek().t==='-'){var op=toks[p++].t;a={op:op,a:a,b:term()};}return a;}
    function term(){var a=unary();while(peek().t==='*'||peek().t==='/'){var op=toks[p++].t;a={op:op,a:a,b:unary()};}return a;}
    function unary(){if(peek().t==='-'){p++;return {neg:unary()};}if(peek().t==='+'){p++;return unary();}return power();}
    function power(){var a=primary();if(peek().t==='^'){p++;return {op:'^',a:a,b:unary()};}return a;}
    function primary(){
      var tk=toks[p];
      if(!tk)fail('ends too soon');
      if(tk.t==='n'){p++;return {n:tk.v};}
      if(tk.t==='i'){
        p++;
        if(peek().t==='('){
          var fn=tk.v.toLowerCase(),args=[];
          if(!BIM_EXPR_FN[fn])fail('unknown function '+tk.v);
          p++;
          if(peek().t!==')'){args.push(expr());while(peek().t===','){p++;args.push(expr());}}
          if(peek().t!==')')fail('a bracket is not closed');
          p++;
          if(!args.length)fail(tk.v+' needs a value');
          return {fn:fn,args:args};
        }
        return {v:tk.v};
      }
      if(tk.t==='('){p++;var e=expr();if(peek().t!==')')fail('a bracket is not closed');p++;return e;}
      fail('unexpected "'+tk.t+'"');
    }
    try{
      var ast=expr();
      if(p<toks.length)fail('unexpected "'+(toks[p].t==='n'?toks[p].v:(toks[p].v||toks[p].t))+'"');
      return {ast:ast};
    }catch(eX){
      if(eX&&eX.bimExpr)return {error:eX.bimExpr};
      throw eX;
    }
  }
  function bimExprEval(ast,vars){
    function ev(nd){
      if(nd.n!==undefined)return nd.n;
      if(nd.v!==undefined){
        var k=nd.v.toLowerCase();
        if(!vars.hasOwnProperty(k))throw {bimExpr:'unknown name '+nd.v};
        var vv=vars[k];
        if(vv===null||!isFinite(vv))throw {bimExpr:nd.v+' has no value'};
        return vv;
      }
      if(nd.neg)return -ev(nd.neg);
      if(nd.fn){var as=nd.args.map(ev);return BIM_EXPR_FN[nd.fn].apply(null,as);}
      var a=ev(nd.a),b=ev(nd.b);
      if(nd.op==='+')return a+b;
      if(nd.op==='-')return a-b;
      if(nd.op==='*')return a*b;
      if(nd.op==='/'){if(b===0)throw {bimExpr:'divides by zero'};return a/b;}
      return Math.pow(a,b);
    }
    try{
      var r=ev(ast);
      if(!isFinite(r))return {error:'is not a finite number'};
      return {value:r};
    }catch(eE){
      if(eE&&eE.bimExpr)return {error:eE.bimExpr};
      throw eE;
    }
  }
  function bimExpr(src,vars){
    var pz=bimExprParse(src);
    return pz.error?pz:bimExprEval(pz.ast,vars||{});
  }
  /* a parameter's or formula's name: a word, not a name the formulas already read */
  function bimUsageKeyProblem(u,key,skip){
    if(!/^[A-Za-z_][A-Za-z0-9_]*$/.test(key||''))return 'a name is a word: letters, digits and _';
    var lk=key.toLowerCase(),i;
    if(BIM_EXPR_NAMES[lk])return key+' is one of the areas';
    if(BIM_EXPR_FN[lk])return key+' is a function';
    var all=(u.params||[]).concat(u.formulas||[]);
    for(i=0;i<all.length;i++)if(all[i]!==skip&&String(all[i].key).toLowerCase()===lk)return key+' is used twice';
    return '';
  }
  /* the usage's formulas for one measured object, in order: each can read the ones before it */
  function bimUsageValues(u,r){
    var vars={gba:r.GBA,gfa:r.GFA,nsa:r.NSA,levels:r.levels,height:r.height,footprint:r.footprint},i,f;
    for(i=0;i<(u.params||[]).length;i++)vars[String(u.params[i].key).toLowerCase()]=+u.params[i].value;
    for(i=0;i<(u.formulas||[]).length;i++){
      f=u.formulas[i];
      var ev=bimExpr(f.expr,vars);
      if(ev.error){r.errors[f.key]=ev.error;vars[String(f.key).toLowerCase()]=null;r.values[f.key]=null;}
      else{r.values[f.key]=ev.value;vars[String(f.key).toLowerCase()]=ev.value;}
    }
    return r;
  }
  /* ---- the areas by usage: the selection's, or the whole project's ---- */
  function bimUsageSummary(ids){
    var objs=ids?ids.map(objById).filter(function(o){return !!o;}):A3D.objs,L=bimUsages(),by={},i,k,o,r,g;
    for(i=0;i<objs.length;i++){
      o=objs[i];
      if(!bimUsageTarget(o)||!o.usage||!bimUsageById(o.usage))continue;
      r=bimUsageMeasure(o);
      g=by[r.usage]||(by[r.usage]={usage:r.usage,count:0,GBA:0,GFA:0,NSA:0,values:{},errors:0,levels:{}});
      g.count++;g.GBA+=r.GBA;g.GFA+=r.GFA;g.NSA+=r.NSA;
      for(k in r.values)if(r.values.hasOwnProperty(k)&&r.values[k]!==null)g.values[k]=(g.values[k]||0)+r.values[k];
      for(k in r.errors)if(r.errors.hasOwnProperty(k))g.errors++;
      r.floors.forEach(function(fl){
        var lk=fl.levelId||'',lg=g.levels[lk]||(g.levels[lk]={levelId:fl.levelId,GBA:0,GFA:0,NSA:0,objs:{}});
        lg.GBA+=fl.gba||0;lg.GFA+=fl.gfa||0;lg.NSA+=fl.nsa||0;lg.objs[r.id]=1;
      });
    }
    var rows=[],tot={count:0,GBA:0,GFA:0,NSA:0};
    for(i=0;i<L.length;i++){
      g=by[L[i].id];
      if(!g)continue;
      g.name=L[i].name;g.color=L[i].color;
      rows.push(g);
      tot.count+=g.count;tot.GBA+=g.GBA;tot.GFA+=g.GFA;tot.NSA+=g.NSA;
    }
    return {rows:rows,total:tot};
  }
  /* the schedule: per usage and level, then the usage's total with its formulas' sums */
  function bimUsageScheduleRows(){
    var s=bimUsageSummary(null),out=[],i;
    for(i=0;i<s.rows.length;i++){
      var g=s.rows[i],lv,k,vals=[];
      for(lv=0;lv<A3D.levels.length;lv++){
        var lg=g.levels[A3D.levels[lv].id];
        if(lg)out.push({usage:g.name,level:A3D.levels[lv].name,objects:Object.keys(lg.objs).length,gba:lg.GBA,gfa:lg.GFA,nsa:lg.NSA,values:''});
      }
      for(k in g.values)if(g.values.hasOwnProperty(k))vals.push(k+' '+String(Math.round(g.values[k]*100)/100));
      out.push({usage:g.name,level:'All levels',objects:g.count,gba:g.GBA,gfa:g.GFA,nsa:g.NSA,
        values:vals.join(', ')+(g.errors?(vals.length?'; ':'')+g.errors+' formula error'+(g.errors===1?'':'s'):'')});
    }
    return out;
  }
"""

rep("""  function bimBuildAreaSchedule(){""", ENGINE + """  function bimBuildAreaSchedule(){""")

rep("""    arealevel:{label:'Areas by Level',""", """    usage:{label:'Areas by Usage',build:bimUsageScheduleRows,cols:[{key:'usage',label:'Usage'},{key:'level',label:'Level'},{key:'objects',label:'Objects'},{key:'gba',label:'GBA (m\\u00b2)',fmt:2},{key:'gfa',label:'GFA (m\\u00b2)',fmt:2},{key:'nsa',label:'NSA (m\\u00b2)',fmt:2},{key:'values',label:'Formulas'}]},   /* __acad3dV131 */
    arealevel:{label:'Areas by Level',""")

# a mirrored copy keeps its usage
rep("""    var copy={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),pos:bimObjOffset(o),col:o.col,layer:o.layer};   /* __acad3dV110: the geometry below is in o's own frame */""",
    """    var copy={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),pos:bimObjOffset(o),col:o.col,layer:o.layer};   /* __acad3dV110: the geometry below is in o's own frame */
    if(o.usage)copy.usage=o.usage;   /* __acad3dV131 */""", 2)

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
