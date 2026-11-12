

  /* ================= __acad3dV175a: live text on a board, the pure part =================
     docs/research/research-presentation-live.md (D1 to D16, accepted by the owner 2026-11-11) and
     docs/work-orders/v175/SPEC.md. A text object of a board can be live: its words come from the model each time the
     board is drawn. Two kinds (n.bind.k): 'tok', a text with fields typed as {{key}} or {{key|decimals}} (D14), and
     'num', one number with its unit. What is saved is the binding, never the value (D8). Words typed over a live
     object are an override (n.ov), kept with the source's words at that moment (n.ovAt), so Properties can say when
     the source has moved since (D5, D7).
     This file holds the functions that need nothing of the page or the model: reading fields out of a string,
     formatting, the override's rules, and what is kept of a binding when a project is read. */

  /* a number's kinds: {u: the unit written after it, dp: its decimals unless a field gives its own}; null for text */
  function bimLvKind(kind){
    if(kind==='area')return {u:' m²',dp:1};
    if(kind==='vol')return {u:' m³',dp:1};
    if(kind==='count')return {u:'',dp:0};
    return null;
  }
  /* the fields in a string, in order: [{i: where it starts, n: its length, key, dp: its decimals or null}] */
  function bimLvTokens(s){
    var r = [], re, m;
    if(typeof s !== 'string')return r;
    re = /\{\{\s*([A-Za-z][A-Za-z0-9_.]{0,39})\s*(?:\|\s*([0-6])\s*)?\}\}/g;
    while((m = re.exec(s))){
      r.push({i: m.index, n: m[0].length, key: m[1], dp: m[2] === undefined ? null : +m[2]});
    }
    return r;
  }
  /* a number as text with its thousands grouped: '12345.6' gives '12,345.6' */
  function bimLvGroup(s){
    throw new Error('WO-02: not built');
  }
  /* a value as a board shows it: a number of a kind with its unit, or text as it is */
  function bimLvFormat(v,kind,dp){
    throw new Error('WO-03: not built');
  }
  /* a string with its fields replaced: look(key, dp) gives a field's words, or null for a key it does not know.
     {s, keys: the keys replaced, unknown: the keys left as typed} */
  function bimLvSubst(s,look){
    throw new Error('WO-04: not built');
  }
  /* words typed over a live object: kept as its override of key, with the source's words now. true when it changed */
  function bimLvOvSet(n,key,val,cur){
    throw new Error('WO-05: not built');
  }
  /* an override taken off: one key, or every key when key is null. true when there was one */
  function bimLvOvReset(n,key){
    throw new Error('WO-06: not built');
  }
  /* 'none', 'set', or 'changed' when the source's words are no longer what they were when the override was made */
  function bimLvOvState(n,key,cur){
    throw new Error('WO-07: not built');
  }
  /* Keep: the override stands against the source as it is now. true when it changed */
  function bimLvOvKeep(n,key,cur){
    throw new Error('WO-08: not built');
  }
  /* what Print says of the live objects that are out of date: items [{nm, why}]; '' when there are none */
  function bimLvPrintNote(items){
    throw new Error('WO-09: not built');
  }
  /* the fields as a menu's rows, a rule between groups: rows [key, label, kind, group] give [[label, key], '-', ...] */
  function bimLvMenuItems(rows){
    throw new Error('WO-10: not built');
  }
  /* ---- what is kept of a binding when a project is read (bimBobOne) ---- */
  function bimLvKeyOk(k){return typeof k==='string'&&/^[A-Za-z][A-Za-z0-9_.]{0,39}$/.test(k);}
  /* a binding as saved, good, or null. A key this build does not know is kept, and marked when drawn: a newer
     build's project keeps its bindings through this one */
  function bimLvBindValid(b){
    var r;
    if(!b||typeof b!=='object')return null;
    if(b.k==='tok')return {k:'tok'};
    if(b.k!=='num'||!bimLvKeyOk(b.src))return null;
    r={k:'num',src:b.src};
    if(typeof b.id==='string'&&b.id&&b.id.length<=120)r.id=b.id;
    if(typeof b.nm==='string'&&b.nm.replace(/\s+/g,''))r.nm=b.nm.replace(/\s+/g,' ').trim().slice(0,80);   /* its source's name when bound, to say what was removed (D8) */
    if(typeof b.dp==='number'&&isFinite(b.dp))r.dp=Math.max(0,Math.min(6,Math.round(b.dp)));
    return r;
  }
  /* the keys an override can hold: a live text's words. Its size, weight and colour are its own, never the
     source's, so styling a live number does not freeze it (D5) */
  function bimLvOvKeys(){return ['s'];}
  /* overrides (or their sources' words) as saved, good, or null; only is the override whose keys ovAt may hold */
  function bimLvOvValid(o,only){
    var r={},n=0;
    if(!o||typeof o!=='object')return null;
    bimLvOvKeys().forEach(function(k){
      if(typeof o[k]!=='string'||(only&&!only.hasOwnProperty(k)))return;
      r[k]=o[k].slice(0,4000);n++;
    });
    return n?r:null;
  }
export {
  bimLvBindValid, bimLvFormat, bimLvGroup, bimLvKind, bimLvMenuItems, bimLvOvKeep, bimLvOvReset, bimLvOvSet,
  bimLvOvState, bimLvOvValid, bimLvPrintNote, bimLvSubst, bimLvTokens
};
