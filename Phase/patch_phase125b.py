"""patch_phase125b.py -- V125: loads, load cases and combinations.

Two load cases, D (dead) and L (live), and the combinations of ASCE 7-16 section 2.3.1 that use only
those two -- 1.4D and 1.2D + 1.6L -- with the service combination D + L and each case alone:

  self-weight   in D: the material's density x the section area x g, along every member -- on
                unless the Analysis settings turn it off
  line          on a beam: kN/m along its whole length, downward
  point         on a beam: kN downward, at a distance from the beam's start
  lateral       on a column: kN at its top, along the plan's X or Z (wind, notional loads)

A load is stored on its member as o.bim.struct.loads -- under bim, so bimCarryBim carries it through
every rebuild and copy (the V123 rule) -- and read here and nowhere else (bimStructLoads).

Not included, and said wherever results are shown: the level's floor loads (V106's kPa) as loads on
beams -- V106's column takedown remains their check -- and lateral loads other than the ones set."""
NAME = 'patch_phase125b.py'
BASE = 'a69d5f5cd8b6f9d1f0d17120948d2f38f24520fa192cf34cd8039a3f0c3e9f9f'
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
""", r"""  /* ================= __acad3dV125: loads and combinations ================= */
  var BIM_G=9.80665;
  var BIM_COMBOS=[
    {name:'1.2D+1.6L',f:{D:1.2,L:1.6},why:'strength, ASCE 7 2.3.1 combination 2'},
    {name:'1.4D',f:{D:1.4},why:'strength, ASCE 7 2.3.1 combination 1'},
    {name:'D+L',f:{D:1,L:1},why:'service'},
    {name:'D',f:{D:1},why:'dead load alone'},
    {name:'L',f:{L:1},why:'live load alone'}
  ];
  var BIM_LOAD_KINDS={line:'Line (kN/m, down)',point:'Point (kN, down)',lateral:'Lateral at top (kN)'};
  /* the analysis settings and the last result: a view of the model, not saved with it */
  var A3D_STRUCT={combo:'1.2D+1.6L',selfWeight:true,show:false,diagram:'M',deflected:true,res:null};
  function bimCombo(name){
    var i;
    for(i=0;i<BIM_COMBOS.length;i++)if(BIM_COMBOS[i].name===name)return BIM_COMBOS[i];
    return null;
  }
  /* Is a load one this member can carry? Returns null when it is, the reason when not. */
  function bimLoadProblem(o,ld){
    if(!ld||(ld.lc!=='D'&&ld.lc!=='L'))return 'A load is in case D or L';
    if(!BIM_LOAD_KINDS[ld.kind])return 'Unknown kind of load';
    if(!isFinite(ld.v))return 'A load needs a value';
    var kind=o&&o.bim&&o.bim.type;
    if((ld.kind==='line'||ld.kind==='point')&&kind!=='beam')return 'Line and point loads go on beams';
    if(ld.kind==='lateral'&&kind!=='column')return 'A lateral load goes on a column';
    if(ld.kind==='lateral'&&ld.dir!=='x'&&ld.dir!=='z')return 'A lateral load is along X or Z';
    if(ld.kind==='point'){
      var L=o.bim.length||(o.bim.p1&&o.bim.p2?Math.hypot(o.bim.p2[0]-o.bim.p1[0],o.bim.p2[1]-o.bim.p1[1]):0);
      if(!isFinite(ld.at)||ld.at<0||ld.at>L+1e-9)return 'A point load is between 0 and '+bimDispNum(L,3)+' m from the start';
    }
    return null;
  }
  /* The factored loads of one combination on the analytical model:
       el[i]    {q:[x,y,z] kN/m global, pts:[{a, P:[x,y,z]}]} on each element
       nodal[n] [fx,fy,fz] kN on each node
       total    [Fx,Fy,Fz], everything applied -- the equilibrium check's other side */
  function bimStructLoads(model,combo,selfWeight){
    var el=model.els.map(function(){return {q:[0,0,0],pts:[]};}),nodal={},total=[0,0,0],i,j,k;
    var fD=combo.f.D||0;
    if(selfWeight&&fD){
      for(i=0;i<model.els.length;i++){
        var e=model.els[i],w=e.rho*e.sec.A*BIM_G/1000*fD;
        el[i].q[1]-=w;total[1]-=w*e.L;
      }
    }
    for(i=0;i<model.members.length;i++){
      var m=model.members[i],o=objById(m.id),loads=bimStructOf(o).loads||[];
      for(j=0;j<loads.length;j++){
        var ld=loads[j],f=combo.f[ld.lc]||0;
        if(!f||bimLoadProblem(o,ld))continue;
        var v=ld.v*f;
        if(ld.kind==='line'){
          for(k=0;k<m.els.length;k++){var ee=model.els[m.els[k]];el[m.els[k]].q[1]-=v;total[1]-=v*ee.L;}
        }else if(ld.kind==='point'){
          for(k=0;k<m.els.length;k++){
            var ep=model.els[m.els[k]];
            if(ld.at>=ep.s0-1e-9&&(ld.at<ep.s1-1e-9||k===m.els.length-1)){
              el[m.els[k]].pts.push({a:Math.min(Math.max(ld.at-ep.s0,0),ep.L),P:[0,-v,0]});total[1]-=v;break;
            }
          }
        }else if(ld.kind==='lateral'){
          var nd=nodal[m.n2]||(nodal[m.n2]=[0,0,0]),ix=ld.dir==='x'?0:2;
          nd[ix]+=v;total[ix]+=v;
        }
      }
    }
    return {el:el,nodal:nodal,total:total};
  }
  function bimToggleTrib(){
""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
