import { A3D } from '../core/state.js';
import { bimGradeStale, bimRegrade } from '../terrain/grading.js';
import { bimEsc } from '../layers/layer-manager.js';
import { bimPropGroup, bimPropRow, bimPropText } from '../properties/palette.js';
import { bimLevelById } from '../views/schedules.js';
import { bimLtMenuOpen } from './layout-tabs.js';
import { bimBobFind } from './board-objects.js';
import { bimLvMenuItems, bimLvOvKeep, bimLvOvReset, bimLvOvSet, bimLvTokens } from './live-text.js';
import { bimLiveKey, bimLiveKeys, bimLiveShow } from './live-sources.js';
import { bimBdeAdd, bimBdeCommit, bimBdeSel, bimBdeSet, bimBdeWork } from './board-design-edit.js';
import { bimBdeBtn, bimBdeOpt } from './board-design-props.js';
import { a3dToast } from '../bim/csg-booleans.js';



  /* ================= __acad3dV175a: live text on a board, in Edit =================
     docs/research/research-presentation-live.md, 4.3 to 4.6; docs/work-orders/v175/SPEC.md. The board's Draw menu
     puts a Field into a text or a Number on the board, each picked from a menu (D14: a field is seldom typed). The
     selected live text has a Live group in the Properties panel: what it is bound to, what it shows, its override
     with Reset and Keep (D5, D7), Run again for a kept analysis that is out of date (D3), and Unlink, one way, which
     leaves what it shows as plain text (D6). Every change is one undo step, as the board's other changes are. */
  /* what setting a text's words does to its binding: a text with a field in it is live, one with none is plain */
  function bimLvTextPatch(n,s){
    var o={s:s},any;
    if(n.bind&&n.bind.k==='num')return o;
    any=bimLvTokens(s).some(function(t){var E=bimLiveKey(t.key);return !!E&&!E[4];});
    if(any){if(!n.bind)o.bind={k:'tok'};}
    else if(n.bind){o.bind=null;o.ov=null;o.ovAt=null;}
    return o;
  }
  /* the one selected text object and the board's working copy, or null */
  function bimLvTarget(live){
    var W=bimBdeWork(),S,f;
    if(!W)return null;
    S=bimBdeSel(W);
    f=S.length===1?bimBobFind(W.objs,S[0]):null;
    if(!f||f.n.t!=='text'||(live&&!f.n.bind))return null;
    return {W:W,n:f.n};
  }
  /* the Text row of Properties: the words, and the binding they give. true when it was a text's */
  function bimLvSetText(s){
    var T=bimLvTarget(false);
    if(!T||(T.n.bind&&T.n.bind.k==='num'))return false;
    bimBdeSet(T.n.id,bimLvTextPatch(T.n,String(s).slice(0,4000)));
    return true;
  }
  /* ---- the menus ---- */
  function bimLvFieldMenu(x,y){
    bimLtMenuOpen(x,y,bimLvMenuItems(bimLiveKeys().filter(function(k){return !k[4];})),function(key){bimLvInsertField(key);});
    return true;
  }
  /* a field put at the end of the selected text, or as a new text when none is selected */
  function bimLvInsertField(key){
    var E=bimLiveKey(key),T,tok,s;
    if(!E||E[4])return null;
    tok='{{'+E[0]+'}}';
    T=bimLvTarget(false);
    if(T&&!(T.n.bind&&T.n.bind.k==='num')){
      s=T.n.s==='Text'?tok:T.n.s+(/\s$/.test(T.n.s)||!T.n.s?'':' ')+tok;
      if(s.length>4000){a3dToast('This text is full: put the field in a new text');return null;}
      bimBdeSet(T.n.id,bimLvTextPatch(T.n,s));
      a3dToast(E[1]+' put in the text: it follows the project');
      return T.n.id;
    }
    return bimBdeAdd('text',{s:E[1]+': '+tok,bind:{k:'tok'},fit:'auto-w'});
  }
  function bimLvNumberMenu(x,y){
    var items=bimLvMenuItems(bimLiveKeys().filter(function(k){return k[2]!=='text'&&!k[4];}));
    if(A3D.levels.length){
      items.push('-');
      A3D.levels.forEach(function(L,i){items.push(['Gross area: '+L.name,'level.area#'+i]);});
    }
    bimLtMenuOpen(x,y,items,function(a){
      var m=/^level\.area#(\d+)$/.exec(a),L=m?A3D.levels[+m[1]]:null;
      if(m){if(L)bimLvAddNumber('level.area',L.id);}
      else bimLvAddNumber(a);
    });
    return true;
  }
  /* one number on the board, with its unit: a text object bound to one source */
  function bimLvAddNumber(key,id){
    var E=bimLiveKey(key),b,lv=null;
    if(!E||E[2]==='text')return null;
    b={k:'num',src:E[0]};
    if(E[4]){
      lv=bimLevelById(id);
      if(!lv){a3dToast('That level is not in the project');return null;}
      b.id=lv.id;b.nm=lv.name;
    }
    return bimBdeAdd('text',{s:'{{'+E[0]+'}}',bind:b,fs:28,fw:700,fit:'auto-w',nm:E[1]+(lv?': '+lv.name:'')});
  }
  /* ---- the selected live text ---- */
  /* words typed in Properties' Shows row: an override, or none when they are the source's own */
  function bimLvOverride(val){
    var T=bimLvTarget(true),cur;
    if(!T)return false;
    cur=bimLiveShow(T.n,T.W.B,false).src;
    if(!bimLvOvSet(T.n,'s',String(val).slice(0,4000),cur))return false;
    return bimBdeCommit(T.W,T.n.ov?'Overridden: it keeps these words until Reset':'It follows its source again',[T.n.id]);
  }
  /* a Number's decimals: '' for its kind's own */
  function bimLvSetDp(v){
    var T=bimLvTarget(true),d=parseInt(v,10);
    if(!T||T.n.bind.k!=='num')return false;
    if(isFinite(d))T.n.bind.dp=Math.max(0,Math.min(6,d));else delete T.n.bind.dp;
    return bimBdeCommit(T.W,null,[T.n.id]);
  }
  /* Reset, Reset all, Keep, Unlink, Run again, Insert field */
  function bimLvAct(a,x,y){
    var T,R,G;
    if(a==='lv-field')return bimLvFieldMenu(x||0,y||0);
    if(a==='lv-run'){   /* the graded surfaces that are out of date, graded again: never by a board on its own (D3) */
      G=A3D.objs.filter(function(o){return o.t==='terrain'&&o.grading&&bimGradeStale(o);});
      if(!G.length){a3dToast('Nothing graded is out of date');return false;}
      G.forEach(function(o){bimRegrade(o);});
      return true;
    }
    T=bimLvTarget(true);
    if(!T)return false;
    if(a==='lv-reset'||a==='lv-resetall'){
      if(!bimLvOvReset(T.n,a==='lv-reset'?'s':null))return false;
      return bimBdeCommit(T.W,'Reset: it follows its source again',[T.n.id]);
    }
    if(a==='lv-keep'){
      if(!bimLvOvKeep(T.n,'s',bimLiveShow(T.n,T.W.B,false).src))return false;
      return bimBdeCommit(T.W,'Kept: the override stands against the source as it is now',[T.n.id]);
    }
    if(a==='lv-unlink'){
      R=bimLiveShow(T.n,T.W.B,false);
      T.n.s=R.s.slice(0,4000);
      delete T.n.bind;delete T.n.ov;delete T.n.ovAt;
      return bimBdeCommit(T.W,'Unlinked: plain text now, as it showed. Ctrl+Z brings the link back',[T.n.id]);
    }
    return false;
  }
  /* ---- the Live group of the Properties panel, for one selected text ---- */
  function bimLvPropsHtml(n,W){
    var b=n.bind,R,E,g='',src,acts='';
    if(n.t!=='text')return '';
    if(!b)return bimPropGroup('Live','<div class="a3d-bdeacts">'+bimBdeBtn('lv-field','Insert field…','A value of the project, kept up to date')+'</div>'+
      '<div class="a3d-pnote">A field shows a value of the project and follows it: the project\'s name, the site area, the gross floor area. It is written {{key}} in the text.</div>');
    R=bimLiveShow(n,W.B,false);
    if(b.k==='num'){
      E=bimLiveKey(b.src);
      src=(E?E[1]:b.src)+(b.nm?': '+b.nm:'');
      g+=bimPropText('Source',src,true);
      if(E)g+=bimPropRow('Decimals','<select data-bdf="lv.dp">'+bimBdeOpt('','As its kind',typeof b.dp==='number'?b.dp:'')+[0,1,2,3].map(function(d){return bimBdeOpt(d,String(d),typeof b.dp==='number'?b.dp:'');}).join('')+'</select>');
    }else{
      src=R.keys.map(function(k){var q=bimLiveKey(k);return q?q[1]:k;}).filter(function(v,i,a){return a.indexOf(v)===i;}).join(', ');
      g+=bimPropText('Fields',src||'None',true);
    }
    g+=bimPropRow('Shows','<textarea data-bdf="ov.s" rows="2" maxlength="4000" title="Typing here overrides what the source says, until Reset">'+bimEsc(R.s)+'</textarea>');
    if(R.ov){
      g+='<div class="a3d-pnote">Overridden: these words were typed on the board. The source says: '+bimEsc(R.src)+'.'+(R.changed?' The source has changed since this was set.':'')+'</div>';
      acts+=bimBdeBtn('lv-reset','Reset','Back to what the source says')+(R.changed?bimBdeBtn('lv-keep','Keep','Keep the override, and stop saying the source has changed'):'');
    }
    if(R.unknown.length)g+='<div class="a3d-pnote">Not a field, left as typed: '+bimEsc(R.unknown.map(function(k){return '{{'+k+'}}';}).join(', '))+'. Insert field lists the fields.</div>';
    R.why.forEach(function(w){g+='<div class="a3d-pnote">'+bimEsc(w)+'</div>';});
    if(R.st==='stale')acts+=bimBdeBtn('lv-run','Run again','Grade again the surfaces that are out of date');
    if(b.k==='tok')acts+=bimBdeBtn('lv-field','Insert field…','Another value of the project, at the end of the text');
    acts+=bimBdeBtn('lv-unlink','Unlink','Keep what it shows as plain text: it no longer follows the project');
    if(R.ov)acts+=bimBdeBtn('lv-resetall','Reset all','Every override of this object taken off');
    g+='<div class="a3d-bdeacts">'+acts+'</div>';
    g+='<div class="a3d-pnote">It is drawn from the project each time the board is. Its marks (overridden, out of date, source removed) show in Edit and are never printed.</div>';
    return bimPropGroup('Live',g);
  }
export {
  bimLvAct, bimLvAddNumber, bimLvFieldMenu, bimLvInsertField, bimLvNumberMenu, bimLvOverride, bimLvPropsHtml,
  bimLvSetDp, bimLvSetText, bimLvTextPatch
};
