"""patch_phase146a.py -- V146: history by element (the Hub's H1), the engine.

- A commit is the model split into its elements: every object by its id, and the project's other
  parts (levels, grids, layers, types, sheets, the title block, buildings, the site,
  classifications, saved views) each as one. Each element is kept once, by a 128-bit hash of its
  canonical JSON, so a commit stores only what changed.
- The difference between two versions, element by element: added, removed, changed -- and for a
  changed one, field by field (moved by, shape changed, a level added to the levels...).
- Restore any version (undoable; the history is not rewritten). An element's own history.
- The history is saved with the project, in the browser and in the project file."""
NAME = 'patch_phase146a.py'
BASE = '34327630112b809a8ff30cf81a3fefb4f2bf5333a01ee374085b81565797cd0f'
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


ENGINE = r"""  /* ================= __acad3dV146: history, by element (the Hub's H1) =================
     A commit is the model split into its elements -- each object by its id, and each of the
     project's other parts as one -- every element kept once, by the hash of its canonical JSON,
     so a commit adds only what changed: git's object store, at the grain of a building element.
     The history travels with the project. Restoring a version is an edit like any other (undo
     takes it back); nothing in the history is ever rewritten. */
  var BIM_HIST_PARTS=[['levels','Levels'],['grids','Grids'],['layers','Layers'],['types','Types'],['sheets','Sheets'],['titleBlock','Title Block'],
    ['buildings','Buildings'],['site','Site'],['classifications','Classifications'],['views','Saved Views']];
  var BIM_HIST_META=['counts','activeLevel','activeLayer','activeWallType','activeBuilding','levelFilter','roomScheme'];
  /* JSON with every object's keys in order: the same content, the same text */
  function bimCanon(v){
    if(v===null||v===undefined||typeof v!=='object')return JSON.stringify(v===undefined?null:v);
    if(Array.isArray(v))return '['+v.map(function(x){return bimCanon(x);}).join(',')+']';
    var k=Object.keys(v).filter(function(x){return v[x]!==undefined&&typeof v[x]!=='function';}).sort();
    return '{'+k.map(function(x){return JSON.stringify(x)+':'+bimCanon(v[x]);}).join(',')+'}';
  }
  function bimImul(a,b){var ah=(a>>>16)&0xffff,al=a&0xffff,bh=(b>>>16)&0xffff,bl=b&0xffff;return ((al*bl)+(((ah*bl+al*bh)<<16)>>>0))|0;}
  function bimHex8(n){var s=(n>>>0).toString(16);return '00000000'.slice(s.length)+s;}
  /* 128 bits: two 64-bit cyrb53-style mixes with different seeds */
  function bimHash(s){
    var out='',seeds=[0,0x9e3779b9],q,i,ch,h1,h2;
    for(q=0;q<2;q++){
      h1=0xdeadbeef^seeds[q];h2=0x41c6ce57^seeds[q];
      for(i=0;i<s.length;i++){ch=s.charCodeAt(i);h1=bimImul(h1^ch,2654435761);h2=bimImul(h2^ch,1597334677);}
      h1=bimImul(h1^(h1>>>16),2246822507)^bimImul(h2^(h2>>>13),3266489909);
      h2=bimImul(h2^(h2>>>16),2246822507)^bimImul(h1^(h1>>>13),3266489909);
      out+=bimHex8(h2)+bimHex8(h1);
    }
    return out;
  }
  /* a state (bimSnapshotState, parsed) as a tree: [[key, hash], ...] in the model's order, and its blobs */
  function bimHistTreeOf(st){
    var T=[],B={};
    function put(key,val){var c=bimCanon(val),h=bimHash(c);T.push([key,h]);B[h]=c;}
    (st.objs||[]).forEach(function(o){put('o:'+o.id,o);});
    BIM_HIST_PARTS.forEach(function(p){put('@'+p[0],st[p[0]]===undefined?null:st[p[0]]);});
    var m={};
    BIM_HIST_META.forEach(function(k){m[k]=st[k]===undefined?null:st[k];});
    put('#meta',m);
    return {tree:T,blobs:B};
  }
  var A3D_HIST_WORK={s:null,t:null},A3D_HIST_MAPS={};
  function bimHistWorking(){
    var s=bimSnapshotState();
    if(A3D_HIST_WORK.s!==s)A3D_HIST_WORK={s:s,t:bimHistTreeOf(JSON.parse(s))};
    return A3D_HIST_WORK.t;
  }
  function bimHistValid(h){
    if(!h||typeof h!=='object'||!Array.isArray(h.commits)||!h.blobs||typeof h.blobs!=='object')return null;
    var C=h.commits.filter(function(c){return c&&typeof c.id==='string'&&Array.isArray(c.tree)&&c.tree.every(function(e){return Array.isArray(e)&&typeof e[0]==='string'&&typeof e[1]==='string';});});
    if(C.length!==h.commits.length)console.warn('[BIM] Discarded '+(h.commits.length-C.length)+' damaged version(s) from the history.');
    var head=typeof h.head==='string'&&C.some(function(c){return c.id===h.head;})?h.head:(C.length?C[C.length-1].id:null);
    return {v:1,head:head,commits:C,blobs:h.blobs};
  }
  function bimHist(){
    if(!A3D.history||!Array.isArray(A3D.history.commits)||!A3D.history.blobs)A3D.history={v:1,head:null,commits:[],blobs:{}};
    return A3D.history;
  }
  function bimHistCommitById(id){var C=bimHist().commits,i;for(i=0;i<C.length;i++)if(C[i].id===id)return C[i];return null;}
  function bimHistHead(){var H=bimHist();return H.head?bimHistCommitById(H.head):null;}
  function bimHistMap(tree,id){
    if(id&&A3D_HIST_MAPS[id])return A3D_HIST_MAPS[id];
    var m={};tree.forEach(function(e){m[e[0]]=e[1];});
    if(id)A3D_HIST_MAPS[id]=m;
    return m;
  }
  function bimHistLabel(key,v){
    var i,t='';
    if(key.charAt(0)==='@'){for(i=0;i<BIM_HIST_PARTS.length;i++)if('@'+BIM_HIST_PARTS[i][0]===key)return BIM_HIST_PARTS[i][1];return key.slice(1);}
    try{t=v?bimObjTypeLabel(v)||'':'';}catch(eL){t='';}
    return String(v&&v.name?v.name:key.slice(2))+(t?' ('+t+')':'');
  }
  function bimHistSumm(v){
    if(v===undefined||v===null)return '(none)';
    if(typeof v==='number')return bimDispNum(v,3);
    if(typeof v==='boolean')return v?'yes':'no';
    if(typeof v==='string')return '"'+(v.length>40?v.slice(0,37)+'...':v)+'"';
    var s=JSON.stringify(v);
    if(s.length<=40)return s;
    return Array.isArray(v)?v.length+' items':Object.keys(v).length+' fields';
  }
  function bimHistIdArr(v){return Array.isArray(v)&&v.length>0&&v.every(function(x){return x&&typeof x==='object'&&typeof x.id==='string';});}
  /* field by field: what changed in one element. Records with ids (levels, sheets...) by id. */
  function bimHistProps(a,b){
    var out=[];
    function nm(x){return x.name||x.number||x.id;}
    function walk(x,y,path,depth){
      if(out.length>=24)return;
      if((bimHistIdArr(x)||bimHistIdArr(y))&&(Array.isArray(x)||x==null)&&(Array.isArray(y)||y==null)){
        var A={},Bm={},order=[],k;
        (x||[]).forEach(function(r){A[r.id]=r;order.push(r.id);});
        (y||[]).forEach(function(r){Bm[r.id]=r;if(!A.hasOwnProperty(r.id))order.push(r.id);});
        order.forEach(function(id){
          var ra=A[id],rb=Bm[id],pp=(path?path+': ':'')+nm(rb||ra);
          if(!ra)out.push({path:pp,text:pp+' added',to:rb});
          else if(!rb)out.push({path:pp,text:pp+' removed',from:ra});
          else if(bimCanon(ra)!==bimCanon(rb))walk(ra,rb,(path?path+'.':'')+nm(rb),depth+1);
        });
        return;
      }
      var ks={},kk;
      for(kk in (x||{}))if(x.hasOwnProperty(kk))ks[kk]=1;
      for(kk in (y||{}))if(y.hasOwnProperty(kk))ks[kk]=1;
      Object.keys(ks).sort().forEach(function(k){
        if(out.length>=24)return;
        var va=x?x[k]:undefined,vb=y?y[k]:undefined;
        if(bimCanon(va)===bimCanon(vb))return;
        var p=path?path+'.'+k:k;
        if(!path&&k==='pos'&&Array.isArray(va)&&Array.isArray(vb)&&va.length===3&&vb.length===3){
          out.push({path:'pos',text:'moved by '+[0,1,2].map(function(i){return bimDispNum(vb[i]-va[i],3);}).join(', '),from:va,to:vb});return;}
        if(!path&&k==='mesh'){out.push({path:'mesh',text:'shape changed'});return;}
        if(va&&vb&&typeof va==='object'&&typeof vb==='object'&&!Array.isArray(va)&&!Array.isArray(vb)&&depth<3){walk(va,vb,p,depth+1);return;}
        if((bimHistIdArr(va)||bimHistIdArr(vb))&&depth<3){walk(va,vb,p,depth+1);return;}
        out.push({path:p,text:p+': '+bimHistSumm(va)+' → '+bimHistSumm(vb),from:va===undefined?null:va,to:vb===undefined?null:vb});
      });
    }
    walk(a,b,'',0);
    return out;
  }
  /* tree a (or nothing) to tree b: added, removed, changed -- the project's bookkeeping left out */
  function bimHistDiff(ta,tb,blobsA,blobsB){
    var ma=ta?bimHistMap(ta):{},mb=bimHistMap(tb),out=[];
    tb.forEach(function(e){if(e[0]==='#meta')return;if(!ma.hasOwnProperty(e[0]))out.push({key:e[0],kind:'added'});else if(ma[e[0]]!==e[1])out.push({key:e[0],kind:'changed'});});
    if(ta)ta.forEach(function(e){if(e[0]!=='#meta'&&!mb.hasOwnProperty(e[0]))out.push({key:e[0],kind:'removed'});});
    out.forEach(function(d){
      var a=d.kind==='added'?null:JSON.parse(blobsA[ma[d.key]]),b=d.kind==='removed'?null:JSON.parse(blobsB[mb[d.key]]);
      d.label=bimHistLabel(d.key,b||a);
      if(d.kind==='changed')d.props=bimHistProps(a,b);
    });
    return out;
  }
  /* what is not committed yet */
  function bimHistChanges(){
    var H=bimHist(),head=bimHistHead(),W=bimHistWorking();
    return bimHistDiff(head?head.tree:null,W.tree,H.blobs,W.blobs);
  }
  function bimHistCommitDiff(c){
    var H=bimHist(),p=c.parent?bimHistCommitById(c.parent):null;
    return bimHistDiff(p?p.tree:null,c.tree,H.blobs,H.blobs);
  }
  function bimHistCommit(msg){
    var H=bimHist(),W=bimHistWorking(),head=bimHistHead(),d=bimHistDiff(head?head.tree:null,W.tree,H.blobs,W.blobs),st={added:0,changed:0,removed:0};
    if(!d.length)return {error:head?'Nothing has changed since "'+head.msg+'"':'There is nothing to commit yet'};
    d.forEach(function(x){st[x.kind]++;});
    msg=String(msg==null?'':msg).replace(/^\s+|\s+$/g,'').slice(0,200)||('Version '+(H.commits.length+1));
    var c={id:'c-'+Date.now().toString(36)+'-'+(H.commits.length+1),parent:head?head.id:null,msg:msg,at:new Date().toISOString(),
      by:String((A3D.titleBlock&&A3D.titleBlock.drawnBy)||''),tree:W.tree.slice(),stats:st};
    W.tree.forEach(function(e){if(!H.blobs.hasOwnProperty(e[1]))H.blobs[e[1]]=W.blobs[e[1]];});
    H.commits.push(c);H.head=c.id;
    saveSoon();
    return {id:c.id,msg:c.msg,stats:st};
  }
  function bimHistStateOf(c){
    var H=bimHist(),st={objs:[]},i,k,raw,v,m;
    for(i=0;i<c.tree.length;i++){
      k=c.tree[i][0];raw=H.blobs[c.tree[i][1]];
      if(raw===undefined)return null;
      v=JSON.parse(raw);
      if(k.indexOf('o:')===0)st.objs.push(v);
      else if(k==='#meta'){for(m in v)if(v.hasOwnProperty(m))st[m]=v[m];}
      else st[k.slice(1)]=v;
    }
    return st;
  }
  /* the model as it was at a version: an edit, so undo takes it back; the history is not rewritten */
  function bimHistRestore(id){
    var c=bimHistCommitById(id);
    if(!c)return {error:'There is no such version'};
    var st=bimHistStateOf(c);
    if(!st)return {error:'"'+c.msg+'" is damaged: some of its elements are missing'};
    pushUndo();
    bimRestoreState(JSON.stringify(st));
    A3D.selSet=[];
    refreshProps();saveSoon();
    return {id:c.id,msg:c.msg,objs:st.objs.length};
  }
  /* one element's own history, newest first: the versions that added, changed or removed it */
  function bimHistOf(key){
    var H=bimHist(),out=[],i,c,h,p,ph;
    for(i=H.commits.length-1;i>=0;i--){
      c=H.commits[i];h=bimHistMap(c.tree,c.id)[key];
      p=c.parent?bimHistCommitById(c.parent):null;ph=p?bimHistMap(p.tree,p.id)[key]:undefined;
      if(h===ph)continue;
      var r={id:c.id,msg:c.msg,at:c.at,kind:h===undefined?'removed':ph===undefined?'added':'changed'};
      if(r.kind==='changed')r.props=bimHistProps(JSON.parse(H.blobs[ph]),JSON.parse(H.blobs[h]));
      out.push(r);
    }
    return out;
  }
  function bimHistSize(){var H=bimHist(),n=0,k;for(k in H.blobs)if(H.blobs.hasOwnProperty(k))n+=H.blobs[k].length;return {blobs:Object.keys(H.blobs).length,chars:n};}
"""

rep("""  /* ================= __acad3dV138: verify the survey ================= */""",
    ENGINE + """  /* ================= __acad3dV138: verify the survey ================= */""")

# ---- saved with the project ----
rep("""roomScheme:A3D.roomScheme||'',classifications:A3D.classifications,dataFeatures:A3D.dataFeatures||{}};
  }""", """roomScheme:A3D.roomScheme||'',classifications:A3D.classifications,dataFeatures:A3D.dataFeatures||{},history:A3D.history||null};   /* __acad3dV146 */
  }""")
rep("""classifications:A3D.classifications,dataFeatures:A3D.dataFeatures||{}}});""",
    """classifications:A3D.classifications,dataFeatures:A3D.dataFeatures||{},history:A3D.history||null}});   /* __acad3dV146 */""")
rep("""      if(st&&Array.isArray(st.classifications)){
        A3D.classifications=st.classifications.filter(""", """      A3D.history=bimHistValid(st&&st.history);   /* __acad3dV146: its history, or none */
      if(st&&Array.isArray(st.classifications)){
        A3D.classifications=st.classifications.filter(""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
