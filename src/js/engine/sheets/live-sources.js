import { A3D } from '../core/state.js';
import { bimGradeStale } from '../terrain/grading.js';
import { bimPropertyGeometry } from '../site/property.js';
import { A3D_UNITS, bimUnitDp } from '../properties/palette.js';
import { bimClbE } from '../site-analysis/climate-board.js';
import { bimZnCalc, bimZnProperty } from '../site-analysis/zoning-envelope.js';
import { A3D_REV } from '../core/objects-save.js';
import { bimProjectLabel } from '../ui/project-tabs.js';
import { bimLevelAreas, bimLevelById } from '../views/schedules.js';
import { bimPresIndex, bimPresSeq } from './boards.js';
import { bimBoardLabel } from './board-figures.js';
import { bimLvFormat, bimLvOvState, bimLvSubst } from './live-text.js';
import { bimBdsToday } from './board-design.js';



  /* ================= __acad3dV175a: live text on a board, its sources =================
     docs/research/research-presentation-live.md, 4.2, 5.1 (b) and part 7; docs/work-orders/v175/SPEC.md.
     A field's key is looked up in a fixed table (bimLiveKeys) and never evaluated (D14). Every source here is a cheap
     one, read from the model each time a board draws (D2); a kept analysis (cut and fill) is never run by a board: its
     kept value is shown and marked out of date with why (D3). Each source is computed once per revision of the model
     (A3D_REV), display units and day: the memo below, kept in memory only (D8: the value is never saved).
     A resolver takes ids, never the active level or view: a sheet's capture swaps those while it draws. */
  var A3D_LIVE={sig:'',memo:{},busy:false};
  /* the fields: [key, name, kind ('text', 'area', 'vol', 'count'), group, needs an id] */
  function bimLiveKeys(){
    return [['project.name','Project name','text','Project'],['project.client','Client','text','Project'],
      ['project.drawnBy','Drawn by','text','Project'],['project.checkedBy','Checked by','text','Project'],['date','Today\'s date','text','Project'],
      ['board.name','Board name','text','Board'],['board.number','Board number','count','Board'],['board.count','Boards and sheets in the set','count','Board'],
      ['gfa','Gross floor area','area','Building'],['rooms.area','Room area','area','Building'],['rooms','Rooms','count','Building'],['levels','Levels','count','Building'],
      ['level.area','A level\'s gross area','area','Building',1],
      ['site.area','Site area','area','Site'],['far.gfa','Floor area the zoning allows','area','Site'],['cut','Cut volume','vol','Site'],['fill','Fill volume','vol','Site']];
  }
  /* older and other names of a key (D14): a board keeps working when a key is renamed */
  function bimLiveAliases(){return {'gba':'gfa','project':'project.name','client':'project.client','site':'site.area'};}
  /* a key's row of the table, by its name or an alias; null for one that is not a field */
  function bimLiveKey(key){
    var A=bimLiveAliases(),L=bimLiveKeys(),i;
    if(typeof key!=='string')return null;
    if(A.hasOwnProperty(key))key=A[key];
    for(i=0;i<L.length;i++)if(L[i][0]===key)return L[i];
    return null;
  }
  /* ---- the sources: {st: 'ok', 'none' (nothing to show yet), 'gone' (its source was removed) or 'stale' (kept, out of
     date), v, why} ---- */
  function bimLiveOk(v){return {st:'ok',v:v,why:''};}
  function bimLiveNone(why){return {st:'none',v:null,why:why};}
  function bimLiveTextOf(v,what){v=String(v||'').replace(/\s+/g,' ').trim();return v?bimLiveOk(v):bimLiveNone(what+' is not filled in (Project information)');}
  /* gross floor area: every level's closed runs of walls, summed; a level that cannot be measured says so, never 0 */
  function bimLiveGfa(){
    var t=0,any=false,i,a,bad='';
    for(i=0;i<A3D.levels.length;i++){
      a=bimLevelAreas(A3D.levels[i].id);
      if(a.gross!==null){t+=a.gross;any=true;}
      else if(a.note&&a.note.indexOf('no closed run')<0&&!bad)bad=a.level+': '+a.note;
    }
    if(bad)return bimLiveNone('Not computed: '+bad);
    return any?bimLiveOk(t):bimLiveNone('Not computed: no level has a closed run of walls to measure');
  }
  function bimLiveLevelArea(id,nm){
    var lv=bimLevelById(id),a;
    if(!lv)return {st:'gone',v:null,why:'Source removed: '+(nm||'a level')};
    a=bimLevelAreas(id);
    return a.gross!==null?bimLiveOk(a.gross):bimLiveNone('Not computed: '+lv.name+', '+(a.note||'no closed run of walls'));
  }
  function bimLiveRooms(area){
    var n=0,t=0;
    A3D.objs.forEach(function(o){if(o.t==='room'){n++;if(o.area>0)t+=o.area;}});
    return area?(n?bimLiveOk(t):bimLiveNone('Not computed: there are no rooms yet')):bimLiveOk(n);
  }
  function bimLiveSite(){
    var P=bimZnProperty(),g;
    if(!P)return bimLiveNone('Not computed: no property line yet (Site analysis, Define)');
    g=bimPropertyGeometry(P);
    return g&&isFinite(g.area)&&g.area>0?bimLiveOk(Math.abs(g.area)):bimLiveNone('Not computed: the property line does not close');
  }
  function bimLiveFar(){
    var C=bimZnCalc();
    if(!C||C.error||!isFinite(C.achievable))return bimLiveNone('Not computed: '+((C&&C.error)||'the zoning yield'));
    return bimLiveOk(C.achievable);
  }
  /* cut or fill: the volumes CUTFILL and GRADE kept on the proposed surfaces, summed; out of date when a pad or
     the existing surface has changed since */
  function bimLiveCutFill(f){
    var t=0,n=0,stale=0;
    A3D.objs.forEach(function(o){
      var v=o.t==='terrain'&&o.grading&&o.grading.volume;
      if(!v||!isFinite(v[f]))return;
      t+=v[f];n++;
      if(bimGradeStale(o))stale++;
    });
    if(!n)return bimLiveNone('Not computed: GRADE a pad, or run CUTFILL');
    return stale?{st:'stale',v:t,why:'Out of date: a pad or the existing surface has changed since it was graded'}:bimLiveOk(t);
  }
  function bimLiveCompute(key,id,nm,B){
    var tb=A3D.titleBlock||{},i;
    if(key==='project.name')return bimLiveOk(bimProjectLabel());
    if(key==='project.client')return bimLiveTextOf(tb.client,'Client');
    if(key==='project.drawnBy')return bimLiveTextOf(tb.drawnBy,'Drawn by');
    if(key==='project.checkedBy')return bimLiveTextOf(tb.checkedBy,'Checked by');
    if(key==='date')return bimLiveOk(bimBdsToday());
    if(key==='board.name')return B?bimLiveOk(bimBoardLabel(B)):bimLiveNone('Not on a board');
    if(key==='board.number'){i=B?bimPresIndex(B.id):-1;return i>=0?bimLiveOk(i+1):bimLiveNone('This board is not in the set');}
    if(key==='board.count')return bimLiveOk(bimPresSeq().length);
    if(key==='gfa')return bimLiveGfa();
    if(key==='rooms.area')return bimLiveRooms(true);
    if(key==='rooms')return bimLiveRooms(false);
    if(key==='levels')return bimLiveOk(A3D.levels.length);
    if(key==='level.area')return bimLiveLevelArea(id,nm);
    if(key==='site.area')return bimLiveSite();
    if(key==='far.gfa')return bimLiveFar();
    if(key==='cut'||key==='fill')return bimLiveCutFill(key);
    return bimLiveNone('Not a field');
  }
  /* a source's value, computed once per revision, units and day */
  function bimLiveGet(key,id,nm,B){
    var sig=A3D_REV+'|'+A3D_UNITS.key+'|'+bimUnitDp()+'|'+bimBdsToday(),mk,r;
    if(sig!==A3D_LIVE.sig){A3D_LIVE.sig=sig;A3D_LIVE.memo={};}
    mk=key+'|'+(id||'')+'|'+(key.indexOf('board.')===0&&B?B.id:'');
    if(A3D_LIVE.memo.hasOwnProperty(mk))return A3D_LIVE.memo[mk];
    if(A3D_LIVE.busy){console.warn('[BIM] A live field was asked for while another was being computed; it is left empty: '+key);return bimLiveNone('Not computed');}
    A3D_LIVE.busy=true;
    try{r=bimLiveCompute(key,id,nm,B);}
    catch(eL){console.warn('[BIM] A live field could not be computed: '+key,eL);r=bimLiveNone('Not computed: see the console');}
    finally{A3D_LIVE.busy=false;}
    A3D_LIVE.memo[mk]=r;
    return r;
  }
  /* ---- what a live text shows ---- */
  /* n: a board's text object with a binding; B: its board; edit: in Edit, where a number with nothing to show says
     why (on paper it is a dash). {s: its words, src: the source's words as on paper, st: its worst state, why: [reasons],
     ov: overridden, changed: the source has moved since, unknown: [keys left as typed], keys: [keys shown]} */
  function bimLiveShow(n,B,edit){
    var R={s:n.s,src:n.s,st:'ok',why:[],ov:false,changed:false,unknown:[],keys:[]},rank={ok:0,stale:1,none:2,gone:3},b=n.bind,K,r,S;
    function one(key,id,nm,dp){
      var E=bimLiveKey(key),q;
      if(!E)return null;
      if(E[4]&&!id)return null;   /* a source by id is a Number's, never a typed field */
      q=bimLiveGet(E[0],id,nm,B);
      if(rank[q.st]>rank[R.st])R.st=q.st;
      if(q.why&&R.why.indexOf(q.why)<0)R.why.push(q.why);
      R.keys.push(E[0]);
      if(q.st==='none'||q.st==='gone')return '—';
      return bimLvFormat(q.v,E[2],dp===undefined?null:dp);
    }
    if(!b)return R;
    if(b.k==='tok'){
      S=bimLvSubst(n.s,function(key,dp){return one(key,null,null,dp);});
      R.src=S.s;R.unknown=S.unknown;
    }else if(b.k==='num'){
      K=bimLiveKey(b.src);
      r=K?one(b.src,b.id||null,b.nm||null,typeof b.dp==='number'?b.dp:null):null;
      if(r===null){R.unknown=[b.src];R.src='{{'+b.src+'}}';}
      else R.src=r;
    }
    R.s=b.k==='num'&&edit&&(R.st==='none'||R.st==='gone')&&R.why.length?R.why[0]:R.src;
    if(n.ov&&n.ov.hasOwnProperty('s')){R.ov=true;R.s=n.ov.s;R.changed=bimLvOvState(n,'s',R.src)==='changed';}
    return R;
  }
  /* its marks, in Edit only and never on paper (D4, D15): a corner tick for an override, a dot for a source that is
     out of date, missing, or a key that is not a field. The reasons are in the title and in Properties */
  function bimLiveMarks(R){
    var h='',t;
    if(!R)return '';
    if(R.ov)h+='<i class="a3d-clb-dlv ov" title="'+bimClbE('Overridden: typed on the board'+(R.changed?'; the source has changed since':'')+'. Reset is in Properties.')+'"></i>';
    t=R.unknown.length?'Not a field: '+R.unknown.join(', '):R.why.join('; ');
    if(R.unknown.length||R.st!=='ok')h+='<i class="a3d-clb-dlv '+(R.unknown.length||R.st==='gone'?'gone':R.st)+'" title="'+bimClbE(t)+'"></i>';
    return h;
  }
  /* a board's live objects that are not up to date, for Print's message: [{nm, why}] */
  function bimLiveStaleItems(B){
    var out=[];
    (B&&Array.isArray(B.objs)?B.objs:[]).forEach(function(n){
      var R;
      if(n.t!=='text'||!n.bind)return;
      R=bimLiveShow(n,B,false);
      if(R.st==='ok'&&!R.unknown.length)return;
      out.push({nm:n.nm||(n.bind.k==='num'&&bimLiveKey(n.bind.src)?bimLiveKey(n.bind.src)[1]:n.s.replace(/\s+/g,' ').slice(0,40)),
        why:R.unknown.length?'not a field: '+R.unknown.join(', '):R.why[0]||''});
    });
    return out;
  }
export { bimLiveGet, bimLiveKey, bimLiveKeys, bimLiveMarks, bimLiveShow, bimLiveStaleItems };
