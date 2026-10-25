  /* ================= __acad3dV146: history, by element (the Hub's H1) =================
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
    /* __acad3dV151: the branches, each a name at a version that is there; a history from before is "main" */
    var ids={},br={},k;C.forEach(function(c){ids[c.id]=1;});
    if(h.branches&&typeof h.branches==='object')for(k in h.branches)if(h.branches.hasOwnProperty(k)&&/^[A-Za-z0-9][A-Za-z0-9 _.\-]{0,39}$/.test(k)&&(h.branches[k]===null||ids[h.branches[k]]))br[k]=h.branches[k];
    var cur=typeof h.branch==='string'&&br.hasOwnProperty(h.branch)?h.branch:'main';
    if(!br.hasOwnProperty(cur))br[cur]=head;
    return {v:1,head:head,commits:C,blobs:h.blobs,branches:br,branch:cur};
  }
  function bimHist(){
    if(!A3D.history||!Array.isArray(A3D.history.commits)||!A3D.history.blobs)A3D.history={v:1,head:null,commits:[],blobs:{}};
    var H=A3D.history;   /* __acad3dV151 */
    if(!H.branches||typeof H.branches!=='object')H.branches={};
    if(typeof H.branch!=='string'||!H.branch)H.branch='main';
    if(!H.branches.hasOwnProperty(H.branch))H.branches[H.branch]=H.head||null;
    return H;
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
        out.push({path:p,text:p+': '+bimHistSumm(va)+' \u2192 '+bimHistSumm(vb),from:va===undefined?null:va,to:vb===undefined?null:vb});
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
  function bimHistCommit(msg,parent2){
    var H=bimHist(),W=bimHistWorking(),head=bimHistHead(),d=bimHistDiff(head?head.tree:null,W.tree,H.blobs,W.blobs),st={added:0,changed:0,removed:0};
    if(!d.length)return {error:head?'Nothing has changed since "'+head.msg+'"':'There is nothing to commit yet'};
    d.forEach(function(x){st[x.kind]++;});
    msg=String(msg==null?'':msg).replace(/^\s+|\s+$/g,'').slice(0,200)||('Version '+(H.commits.length+1));
    var c={id:'c-'+Date.now().toString(36)+'-'+(H.commits.length+1),parent:head?head.id:null,msg:msg,at:new Date().toISOString(),
      by:String((A3D.titleBlock&&A3D.titleBlock.drawnBy)||''),tree:W.tree.slice(),stats:st,branch:H.branch};
    if(parent2)c.parent2=parent2;   /* __acad3dV151: a merge */
    W.tree.forEach(function(e){if(!H.blobs.hasOwnProperty(e[1]))H.blobs[e[1]]=W.blobs[e[1]];});
    H.commits.push(c);H.head=c.id;H.branches[H.branch]=c.id;
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
