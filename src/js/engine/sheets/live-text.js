import { bimDispNum } from '../properties/palette.js';



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
    var m = /^(-?)(\d+)(\.\d+)?$/.exec(s);
    if(!m)return s;
    var whole = m[2], neg = m[1], dec = m[3] || '';
    var grouped = '', count = 0, i;
    for(i = whole.length - 1; i >= 0; i--){
      if(count > 0 && count % 3 === 0)grouped = ',' + grouped;
      grouped = whole.charAt(i) + grouped;
      count++;
    }
    return neg + grouped + dec;
  }
  /* a value as a board shows it: a number of a kind with its unit, or text as it is */
  function bimLvFormat(v,kind,dp){
    if(v===null||v===undefined)return '\u2014';
    var K = bimLvKind(kind);
    if(!K)return String(v);
    if(typeof v !== 'number' || !isFinite(v))return '\u2014';
    var d = typeof dp === 'number' ? dp : K.dp;
    return bimLvGroup(bimDispNum(v, d)) + K.u;
  }
  /* a string with its fields replaced: look(key, dp) gives a field's words, or null for a key it does not know.
     {s, keys: the keys replaced, unknown: the keys left as typed} */
  function bimLvSubst(s,look){
    var r = {s:'', keys:[], unknown:[]};
    var tokens, t, i, pos, replacement, seenKeys, seenUnknown;
    if(typeof s !== 'string')return r;
    tokens = bimLvTokens(s);
    pos = 0;
    seenKeys = {};
    seenUnknown = {};
    for(i = 0; i < tokens.length; i++){
      t = tokens[i];
      r.s += s.slice(pos, t.i);
      replacement = look(t.key, t.dp);
      if(replacement === null || replacement === undefined){
        r.s += s.slice(t.i, t.i + t.n);
        if(!seenUnknown[t.key]){seenUnknown[t.key] = true; r.unknown.push(t.key);}
      } else {
        r.s += replacement;
        if(!seenKeys[t.key]){seenKeys[t.key] = true; r.keys.push(t.key);}
      }
      pos = t.i + t.n;
    }
    r.s += s.slice(pos);
    return r;
  }
  /* words typed over a live object: kept as its override of key, with the source's words now. true when it changed */
  function bimLvOvSet(n,key,val,cur){
    if(!n.bind)return false;
    if(val===cur){
      if(n.ov && n.ov.hasOwnProperty(key))return bimLvOvReset(n,key);
      return false;
    }
    if(n.ov && n.ov.hasOwnProperty(key) && n.ov[key]===val)return false;
    if(!n.ov)n.ov = {};
    if(!n.ovAt)n.ovAt = {};
    n.ov[key] = val;
    n.ovAt[key] = cur;
    return true;
  }
  /* an override taken off: one key, or every key when key is null. true when there was one */
  function bimLvOvReset(n,key){
    if(!n.ov)return false;
    if(key===null||key===undefined){delete n.ov; delete n.ovAt; return true;}
    if(!n.ov.hasOwnProperty(key))return false;
    delete n.ov[key];
    if(n.ovAt && n.ovAt.hasOwnProperty(key))delete n.ovAt[key];
    var empty, k;
    empty = true;
    for(k in n.ov){if(n.ov.hasOwnProperty(k)){empty=false;break;}}
    if(empty)delete n.ov;
    if(n.ovAt){
      empty = true;
      for(k in n.ovAt){if(n.ovAt.hasOwnProperty(k)){empty=false;break;}}
      if(empty)delete n.ovAt;
    }
    return true;
  }
  /* 'none', 'set', or 'changed' when the source's words are no longer what they were when the override was made */
  function bimLvOvState(n,key,cur){
    if(!n.ov || !n.ov.hasOwnProperty(key))return 'none';
    if(n.ovAt && n.ovAt.hasOwnProperty(key) && n.ovAt[key]!==cur)return 'changed';
    return 'set';
  }
  /* Keep: the override stands against the source as it is now. true when it changed */
  function bimLvOvKeep(n,key,cur){
    if(!n.ov || !n.ov.hasOwnProperty(key))return false;
    if(n.ovAt && n.ovAt.hasOwnProperty(key) && n.ovAt[key]===cur)return false;
    if(!n.ovAt)n.ovAt = {};
    n.ovAt[key] = cur;
    return true;
  }
  /* what Print says of the live objects that are out of date: items [{nm, why}]; '' when there are none */
  function bimLvPrintNote(items){
    var n, i, item, parts, part, more, plural;
    if(!items || items.length === 0)return '';
    n = items.length;
    plural = n === 1 ? 'object' : 'objects';
    part = 'Printed with ' + n + ' live ' + plural + ' not up to date: ';
    parts = [];
    for(i = 0; i < Math.min(3, n); i++){
      item = items[i];
      if(item.why === '' || item.why === undefined){
        parts.push(item.nm);
      } else {
        parts.push(item.nm + ' (' + item.why + ')');
      }
    }
    part += parts.join(', ');
    if(n > 3){
      more = ' and ' + (n - 3) + ' more';
      part += more;
    }
    return part;
  }
  /* the fields as a menu's rows, a rule between groups: rows [key, label, kind, group] give [[label, key], '-', ...] */
  function bimLvMenuItems(rows){
    var result = [], i, row, prevGroup;
    if(!rows || rows.length === 0)return result;
    for(i = 0; i < rows.length; i++){
      row = rows[i];
      if(i > 0 && row[3] !== prevGroup)result.push('-');
      result.push([row[1], row[0]]);
      prevGroup = row[3];
    }
    return result;
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
