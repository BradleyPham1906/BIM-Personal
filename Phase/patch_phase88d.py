"""patch_phase88d.py -- Phase 88 part 4: the imported-sketch factory keeps the bulges.

88c passes bulges into bimMakeImportedSketch; this is the end that stores them. Split out rather
than folded in, because a factory that silently drops its fourth argument is the failure mode
the patch protocol exists to make impossible - and it is caught here by an assertion, not later
by a drawing that looks wrong.
"""
import hashlib, pathlib, sys

BASE = '3f1be3daa2521e717c4edaa66701b17fa959819521c191b7498ea88bd4bf884c'
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')

src = P.read_text(encoding='utf-8')
h0 = hashlib.sha256(src.encode('utf-8')).hexdigest()
assert h0 == BASE, 'baseline hash mismatch: %s' % h0
b0 = len(src.encode('utf-8'))

OLD = """  function bimMakeImportedSketch(pts,y,closed){
    if(!pts||pts.length<2)return null;
    A3D.counts.sketch=(A3D.counts.sketch||0)+1;
    var o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'sketch',name:'Import '+A3D.counts.sketch,col:'#5ec4b8',pos:[0,0,0],pts:pts,y:y,on:null,closed:!!closed};
    A3D.objs.push(o);
    return o;
  }"""
NEW = """  function bimMakeImportedSketch(pts,y,closed,bulges){
    if(!pts||pts.length<2)return null;
    A3D.counts.sketch=(A3D.counts.sketch||0)+1;
    var o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'sketch',name:'Import '+A3D.counts.sketch,col:'#5ec4b8',pos:[0,0,0],pts:pts,y:y,on:null,closed:!!closed};
    /* __acad3dV88: only when there is a real arc in it, so an imported straight polyline is the
       same object it was before this phase - no bulges key at all. */
    if(bimHasBulge(bulges))o.bulges=bulges.slice();
    A3D.objs.push(o);
    return o;
  }"""
assert src.count(OLD) == 1, 'anchor count %d' % src.count(OLD)
out = src.replace(OLD, NEW, 1)
b1 = len(out.encode('utf-8'))
P.write_text(out, encoding='utf-8')
print('bytes before %d  after %d  (+%d)' % (b0, b1, b1 - b0))
print('sha256 %s' % hashlib.sha256(out.encode('utf-8')).hexdigest())
