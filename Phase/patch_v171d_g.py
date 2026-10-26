#!/usr/bin/env python3
"""V171d, patch g: what the suite's first runs showed.

- The sync remembered the inputs it last drew from in one place for the session: a run made with other inputs, or a
  project opened, left the sun's elements as they came while the sync thought them current (the suite: an offset typed,
  Analyze site again, the offset set back -- the paths stayed at the typed one). Each element now keeps the inputs it
  was drawn from (dg.sk); any element whose inputs are not the moment's is drawn again.
- A path's name above or below its line was 12 px off it: the hours' dots on the line, 5 px each way, still met a word
  15 px tall. It goes 15 px off now.

Run from the repository root: python3 Phase/patch_v171d_g.py
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from p171 import begin, rep, done   # noqa: E402

begin('89ecba99a4f269b9dd387e628ff57205afa2595f356866830022a9ea2eb3135b')   # after patch f

SPF = 'js/engine/site-analysis/sun-path.js'
rep(SPF, "  var A3D_SUNSYNC={place:'',moment:''};", "  var A3D_SUNSYNC={hk:'',hb:null};   /* the temperature's bands, worked out once for the half-year */")
rep(SPF, """  /* as a run would draw them, no undo step: a cache of what the place and the clock give. An element moved, or
     whose shape the owner changed, is theirs (marked newer, as a run marks it); a colour changed keeps its colour
     and follows the sun */
  function bimDgSunSync(force){
    var D=bimDgState(),R=D.runs.sun,L,st,K,grp,E,by={},n=0;""", """  /* as a run would draw them, no undo step: a cache of what the place and the clock give, each element keeping the
     inputs it was drawn from (dg.sk). An element moved, or whose shape the owner changed, is theirs (marked newer, as
     a run marks it); a colour changed keeps its colour and follows the sun */
  function bimDgSunSync(force){
    var D=bimDgState(),R=D.runs.sun,L,st,K,grp=null,E,by={},n=0;""")
rep(SPF, """    K=bimSunSyncKeys(st);
    grp=K.place!==A3D_SUNSYNC.place?'all':(K.moment!==A3D_SUNSYNC.moment?'moment':null);
    if(!grp)return 0;
    A3D_SUNSYNC.place=K.place;A3D_SUNSYNC.moment=K.moment;
    E=bimDgSunRun(bimSunDomeOf(R),grp==='all'?null:'moment').E;""", """    K=bimSunSyncKeys(st);
    L.forEach(function(x){var m=BIM_SUN_MOMENT.indexOf(x.dg.k)>=0;if(x.dg.sk!==(m?K.moment:K.place))grp=(!m||grp==='all')?'all':'moment';});
    if(!grp)return 0;
    E=bimDgSunRun(bimSunDomeOf(R),grp==='all'?null:'moment').E;""")
rep(SPF, """      x.dg.gen=gen;x.dg.info=e.info||{};
    });
    return n;""", """      x.dg.gen=gen;x.dg.info=e.info||{};x.dg.sk=BIM_SUN_MOMENT.indexOf(x.dg.k)>=0?K.moment:K.place;
    });
    return n;""")

rep('js/engine/site-analysis/model-layers.js',
    "    for(i=0;i<P.length;i++)C.push([P[i][0],P[i][1]-12,'center'],[P[i][0],P[i][1]+12,'center'],[P[i][0],P[i][1],'center']);   /* above the line, below it, on it */",
    "    for(i=0;i<P.length;i++)C.push([P[i][0],P[i][1]-15,'center'],[P[i][0],P[i][1]+15,'center'],[P[i][0],P[i][1],'center']);   /* above the line, below it, on it */")
done()
