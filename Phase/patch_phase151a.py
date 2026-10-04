"""patch_phase151a.py -- V151: branches and merge (the Hub's H2).

Design options as branches of the V146 history:
- A branch is a name pointing at a version. New Branch starts one at the latest version (what is not
  committed comes along); switching loads its latest version, and is refused while there are
  changes not committed, so nothing is lost. A project's history from before is the branch "main".
- Compare: each branch's numbers side by side -- objects, walls and their length, openings, rooms
  and their area, the gross area of the usages, levels, cut and fill.
- Merge another branch into this one, three ways, element by element, against the version they
  share: an element changed on one side only is taken; changed on both, the fields each changed
  are put together; the same field changed both ways, or changed on one side and deleted on the
  other, is a conflict, shown side by side, kept from this branch or taken from the other. A branch
  behind the other simply moves up to it.
- BRANCH, MERGE and COMPAREBRANCHES open the History group."""
NAME = 'patch_phase151a.py'
BASE = '068c32e9b694acb046e0ae6194d1ca35d649baf9b9854005a218f1c276864bfa'
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


# ---- the history keeps its branches
rep("""    var head=typeof h.head==='string'&&C.some(function(c){return c.id===h.head;})?h.head:(C.length?C[C.length-1].id:null);
    return {v:1,head:head,commits:C,blobs:h.blobs};""",
    """    var head=typeof h.head==='string'&&C.some(function(c){return c.id===h.head;})?h.head:(C.length?C[C.length-1].id:null);
    /* __acad3dV151: the branches, each a name at a version that is there; a history from before is "main" */
    var ids={},br={},k;C.forEach(function(c){ids[c.id]=1;});
    if(h.branches&&typeof h.branches==='object')for(k in h.branches)if(h.branches.hasOwnProperty(k)&&/^[A-Za-z0-9][A-Za-z0-9 _.\-]{0,39}$/.test(k)&&(h.branches[k]===null||ids[h.branches[k]]))br[k]=h.branches[k];
    var cur=typeof h.branch==='string'&&br.hasOwnProperty(h.branch)?h.branch:'main';
    if(!br.hasOwnProperty(cur))br[cur]=head;
    return {v:1,head:head,commits:C,blobs:h.blobs,branches:br,branch:cur};""")
rep("""    if(!A3D.history||!Array.isArray(A3D.history.commits)||!A3D.history.blobs)A3D.history={v:1,head:null,commits:[],blobs:{}};
    return A3D.history;""", """    if(!A3D.history||!Array.isArray(A3D.history.commits)||!A3D.history.blobs)A3D.history={v:1,head:null,commits:[],blobs:{}};
    var H=A3D.history;   /* __acad3dV151 */
    if(!H.branches||typeof H.branches!=='object')H.branches={};
    if(typeof H.branch!=='string'||!H.branch)H.branch='main';
    if(!H.branches.hasOwnProperty(H.branch))H.branches[H.branch]=H.head||null;
    return H;""")
# a commit moves its branch; a merge commit has two parents
rep("""  function bimHistCommit(msg){""", """  function bimHistCommit(msg,parent2){""")
rep("""      by:String((A3D.titleBlock&&A3D.titleBlock.drawnBy)||''),tree:W.tree.slice(),stats:st};
    W.tree.forEach(function(e){if(!H.blobs.hasOwnProperty(e[1]))H.blobs[e[1]]=W.blobs[e[1]];});
    H.commits.push(c);H.head=c.id;""", """      by:String((A3D.titleBlock&&A3D.titleBlock.drawnBy)||''),tree:W.tree.slice(),stats:st,branch:H.branch};
    if(parent2)c.parent2=parent2;   /* __acad3dV151: a merge */
    W.tree.forEach(function(e){if(!H.blobs.hasOwnProperty(e[1]))H.blobs[e[1]]=W.blobs[e[1]];});
    H.commits.push(c);H.head=c.id;H.branches[H.branch]=c.id;""")

ENGINE = r"""  /* ================= __acad3dV151: branches and merge (the Hub's H2) =================
     A branch is a name at a version: a design option. Merging is three ways, element by element,
     against the version both branches share -- git's merge, at the grain of a building element. */
  var BIM_BR_NAME=/^[A-Za-z0-9][A-Za-z0-9 _.\-]{0,39}$/;
  var A3D_MERGE=null,A3D_BR_CMP=false,A3D_BR_NEW='';
  function bimHistDirty(){try{return bimHistChanges().length>0;}catch(eD){return false;}}
  function bimHistBranches(){
    var H=bimHist(),out=[],k;
    for(k in H.branches)if(H.branches.hasOwnProperty(k)){var c=H.branches[k]?bimHistCommitById(H.branches[k]):null;out.push({name:k,head:H.branches[k],current:k===H.branch,msg:c?c.msg:'',at:c?c.at:''});}
    out.sort(function(a,b){return a.name==='main'?-1:b.name==='main'?1:a.name<b.name?-1:a.name>b.name?1:0;});
    return out;
  }
  function bimHistBranchNew(name){
    var H=bimHist();
    name=String(name==null?'':name).replace(/\s+/g,' ').replace(/^ | $/g,'');
    if(!H.head)return {error:'Commit a version first: a branch starts at one'};
    if(!BIM_BR_NAME.test(name))return {error:'A branch name is letters, numbers, spaces, dots, dashes, at most 40'};
    if(H.branches.hasOwnProperty(name))return {error:'There is a branch "'+name+'" already'};
    H.branches[name]=H.head;H.branch=name;
    saveSoon();
    return {name:name,at:H.head};
  }
  /* switch: the model as the branch's latest version; refused over changes not committed */
  function bimHistSwitch(name){
    var H=bimHist();
    if(!H.branches.hasOwnProperty(name))return {error:'There is no branch "'+name+'"'};
    if(name===H.branch)return {name:name,same:true};
    if(bimHistDirty())return {error:'Commit or discard the changes first: switching would lose them'};
    var id=H.branches[name],c=id?bimHistCommitById(id):null,st=c?bimHistStateOf(c):null;
    if(c&&!st)return {error:'"'+c.msg+'" is damaged: some of its elements are missing'};
    if(st){pushUndo();bimRestoreState(JSON.stringify(st));A3D.selSet=[];}
    H.branch=name;H.head=id;A3D_MERGE=null;
    refreshProps();paint();saveSoon();
    return {name:name,head:id};
  }
  function bimHistBranchDelete(name){
    var H=bimHist();
    if(!H.branches.hasOwnProperty(name))return {error:'There is no branch "'+name+'"'};
    if(name===H.branch)return {error:'Switch to another branch first'};
    delete H.branches[name];saveSoon();
    return {name:name};
  }
  /* every version a version comes from, nearest first */
  function bimHistAncestry(id){
    var out=[],seen={},q=[id],c;
    while(q.length){id=q.shift();if(!id||seen[id])continue;seen[id]=1;out.push(id);c=bimHistCommitById(id);if(c){q.push(c.parent||null);if(c.parent2)q.push(c.parent2);}}
    return out;
  }
  function bimHistBase(a,b){
    var A={},L=bimHistAncestry(a),i;L.forEach(function(x){A[x]=1;});
    L=bimHistAncestry(b);
    for(i=0;i<L.length;i++)if(A[L[i]])return L[i];
    return null;
  }
  /* three ways, element by element; fields put together where the two sides changed different ones */
  function bimHistMerge3(base,ours,theirs){
    var H=bimHist(),B=base?bimHistMap(base.tree):{},O=bimHistMap(ours.tree),T=bimHistMap(theirs.tree),keys=[],seen={},tree=[],blobs={},conflicts=[];
    ours.tree.forEach(function(e){keys.push(e[0]);seen[e[0]]=1;});
    theirs.tree.forEach(function(e){if(!seen[e[0]]){keys.push(e[0]);seen[e[0]]=1;}});
    function val(h){return h===undefined?undefined:JSON.parse(H.blobs[h]);}
    keys.forEach(function(k){
      var b=B[k],o=O[k],t=T[k],fb,fo,ft,f,F={},m,cf=[],c;
      if(o===t||b===t){if(o!==undefined)tree.push([k,o]);return;}
      if(b===o){if(t!==undefined)tree.push([k,t]);return;}
      if(k==='#meta'){if(o!==undefined)tree.push([k,o]);return;}   /* the active level and the like: this branch's */
      if(o===undefined||t===undefined){
        conflicts.push({key:k,kind:'deleted',label:bimHistLabel(k,val(o!==undefined?o:t)),gone:o===undefined?'ours':'theirs',ours:o,theirs:t,fields:[]});
        tree.push([k,o!==undefined?o:t]);
        return;
      }
      fb=b!==undefined?val(b):{};fo=val(o);ft=val(t);
      if(!fb||!fo||!ft||typeof fo!=='object'||typeof ft!=='object'||Array.isArray(fo)||Array.isArray(ft)){
        conflicts.push({key:k,kind:'both',label:bimHistLabel(k,fo),ours:o,theirs:t,fields:[{f:'(the whole element)',base:fb,ours:fo,theirs:ft}]});
        tree.push([k,o]);return;
      }
      for(f in fo)if(fo.hasOwnProperty(f))F[f]=1;
      for(f in ft)if(ft.hasOwnProperty(f))F[f]=1;
      m={};
      for(f in F){
        var cb=bimCanon(fb[f]),co=bimCanon(fo[f]),ct=bimCanon(ft[f]);
        if(co===ct||cb===ct){if(fo.hasOwnProperty(f))m[f]=fo[f];}
        else if(cb===co){if(ft.hasOwnProperty(f))m[f]=ft[f];}
        else{cf.push({f:f,base:fb[f],ours:fo[f],theirs:ft[f]});if(fo.hasOwnProperty(f))m[f]=fo[f];}
      }
      c=bimCanon(m);var hh=bimHash(c);blobs[hh]=c;tree.push([k,hh]);
      if(cf.length)conflicts.push({key:k,kind:'both',label:bimHistLabel(k,fo),ours:o,theirs:t,merged:m,fields:cf});
    });
    return {tree:tree,blobs:blobs,conflicts:conflicts};
  }
  /* the model a tree describes, from the history's elements and a merge's own */
  function bimHistStateOfTree(tree,extra){
    var H=bimHist(),st={objs:[]},i,k,raw,v,m;
    for(i=0;i<tree.length;i++){
      k=tree[i][0];raw=(extra&&extra[tree[i][1]]!==undefined)?extra[tree[i][1]]:H.blobs[tree[i][1]];
      if(raw===undefined)return null;
      v=JSON.parse(raw);
      if(k.indexOf('o:')===0)st.objs.push(v);
      else if(k==='#meta'){for(m in v)if(v.hasOwnProperty(m))st[m]=v[m];}
      else st[k.slice(1)]=v;
    }
    return st;
  }
  /* MERGE another branch into this one */
  function bimHistMergeStart(from){
    var H=bimHist();
    if(!H.branches.hasOwnProperty(from))return {error:'There is no branch "'+from+'"'};
    if(from===H.branch)return {error:'A branch cannot be merged into itself'};
    if(bimHistDirty())return {error:'Commit or discard the changes first'};
    var oid=H.head,tid=H.branches[from];
    if(!tid)return {error:'"'+from+'" has no versions'};
    if(!oid){return bimHistFastForward(from,tid);}
    var base=bimHistBase(oid,tid);
    if(base===tid)return {upToDate:true,msg:'"'+H.branch+'" already has everything in "'+from+'"'};
    if(base===oid)return bimHistFastForward(from,tid);
    var r=bimHistMerge3(base?bimHistCommitById(base):null,bimHistCommitById(oid),bimHistCommitById(tid));
    A3D_MERGE={from:from,into:H.branch,ours:oid,theirs:tid,base:base,tree:r.tree,blobs:r.blobs,conflicts:r.conflicts};
    if(!r.conflicts.length)return bimHistMergeFinish();
    refreshProps();
    return {conflicts:r.conflicts.length,from:from};
  }
  function bimHistFastForward(from,tid){
    var H=bimHist(),c=bimHistCommitById(tid),st=bimHistStateOf(c);
    if(!st)return {error:'"'+c.msg+'" is damaged'};
    pushUndo();bimRestoreState(JSON.stringify(st));A3D.selSet=[];
    H.head=tid;H.branches[H.branch]=tid;A3D_MERGE=null;
    refreshProps();paint();saveSoon();
    return {fastForward:true,from:from,head:tid};
  }
  /* a conflict decided: 'ours' keeps this branch's, 'theirs' takes the other's */
  function bimHistMergeChoose(i,side){
    var M=A3D_MERGE;
    if(!M||!M.conflicts[i]||(side!=='ours'&&side!=='theirs'))return false;
    M.conflicts[i].choice=side;
    refreshProps();
    return true;
  }
  function bimHistMergeFinish(){
    var M=A3D_MERGE,H=bimHist(),tree,i,j,cf,k,v,c,hh,st,r;
    if(!M)return {error:'No merge is under way'};
    for(i=0;i<M.conflicts.length;i++)if(!M.conflicts[i].choice)return {error:M.conflicts.length-i+' conflict'+(M.conflicts.length-i===1?'':'s')+' to decide first',open:true};
    tree=M.tree.map(function(e){return e.slice();});
    for(i=0;i<M.conflicts.length;i++){
      cf=M.conflicts[i];k=cf.key;
      for(j=0;j<tree.length;j++)if(tree[j][0]===k)break;
      if(cf.kind==='deleted'){
        v=cf.choice==='ours'?cf.ours:cf.theirs;
        if(v===undefined){if(j<tree.length)tree.splice(j,1);}
        else if(j<tree.length)tree[j][1]=v;else tree.push([k,v]);
      }else if(cf.merged){
        var m=JSON.parse(JSON.stringify(cf.merged));
        cf.fields.forEach(function(f){var x=cf.choice==='ours'?f.ours:f.theirs;if(x===undefined)delete m[f.f];else m[f.f]=x;});
        c=bimCanon(m);hh=bimHash(c);M.blobs[hh]=c;tree[j][1]=hh;
      }else tree[j][1]=cf.choice==='ours'?cf.ours:cf.theirs;
    }
    st=bimHistStateOfTree(tree,M.blobs);
    if(!st)return {error:'The merge could not be put together: elements are missing'};
    pushUndo();bimRestoreState(JSON.stringify(st));A3D.selSet=[];
    A3D_MERGE=null;
    r=bimHistCommit('Merge "'+M.from+'" into "'+M.into+'"',M.theirs);
    if(r.error){H.branches[H.branch]=H.head;refreshProps();paint();return {merged:true,id:H.head,nothing:true,conflicts:M.conflicts.length};}
    refreshProps();paint();saveSoon();
    return {merged:true,id:r.id,stats:r.stats,conflicts:M.conflicts.length};
  }
  function bimHistMergeAbort(){var had=!!A3D_MERGE;A3D_MERGE=null;refreshProps();return had;}
  /* each branch's numbers, from its latest version (this branch's: the model as it is) */
  function bimHistMetricsOf(st){
    var O=st.objs||[],r={objects:O.length,walls:0,wallLength:0,openings:0,rooms:0,roomArea:0,gba:0,levels:(st.levels||[]).length,cut:0,fill:0};
    O.forEach(function(o){
      if(o.t==='room'){r.rooms++;r.roomArea+=+o.area||0;}
      else if(o.t==='opening')r.openings++;
      else if(o.bim&&o.bim.type==='wall'){r.walls++;if(o.bim.centerline)try{r.wallLength+=bimWallLength(o.bim.centerline,o.bim.closed,o.bim.bulges)||0;}catch(eW){}}
      if(o.t==='terrain'&&o.grading&&o.grading.volume){r.cut+=+o.grading.volume.cut||0;r.fill+=+o.grading.volume.fill||0;}
    });
    var keep={objs:A3D.objs,meshes:A3D.meshes};
    try{A3D.objs=O;A3D.meshes={};r.gba=(bimUsageSummary(null).total||{}).GBA||0;}catch(eU){r.gba=0;}
    finally{A3D.objs=keep.objs;A3D.meshes=keep.meshes;}
    return r;
  }
  function bimHistCompare(){
    var H=bimHist();
    return bimHistBranches().map(function(b){
      var st=b.current?JSON.parse(bimSnapshotState()):(b.head?bimHistStateOf(bimHistCommitById(b.head)):{objs:[],levels:[]});
      return {name:b.name,current:b.current,m:st?bimHistMetricsOf(st):null};
    });
  }
  var BIM_BR_ROWS=[['objects','Objects',0],['walls','Walls',0],['wallLength','Wall length (m)',1],['openings','Doors and windows',0],['rooms','Rooms',0],
    ['roomArea','Room area (m²)',1],['gba','Gross area (m²)',1],['levels','Levels',0],['cut','Cut (m³)',1],['fill','Fill (m³)',1]];
  function bimHistCompareHtml(){
    var C=bimHistCompare();
    return '<div class="a3d-brcmp"><table data-brcmp="1"><tr><th></th>'+C.map(function(c){return '<th'+(c.current?' class="cur"':'')+'>'+bimEsc(c.name)+'</th>';}).join('')+'</tr>'+
      BIM_BR_ROWS.map(function(r){
        var vs=C.map(function(c){return c.m?c.m[r[0]]:null;}),same=vs.every(function(v){return v===vs[0];});
        return '<tr data-brrow="'+r[0]+'"'+(same?'':' class="diff"')+'><td>'+r[1]+'</td>'+vs.map(function(v){return '<td>'+(v===null?'-':bimDispNum(v,r[2]))+'</td>';}).join('')+'</tr>';
      }).join('')+'</table></div>';
  }
  function bimBrVal(v){
    if(v===undefined)return '(none)';
    var s=typeof v==='object'?bimHistSumm(v):String(v);
    return s.length>60?s.slice(0,57)+'...':s;
  }
  function bimHistMergeHtml(){
    var M=A3D_MERGE;
    if(!M)return '';
    var left=M.conflicts.filter(function(c){return !c.choice;}).length;
    return '<div class="a3d-brmerge" data-brmerge="1"><div class="a3d-histst">Merging "'+bimEsc(M.from)+'" into "'+bimEsc(M.into)+'": '+M.conflicts.length+' conflict'+(M.conflicts.length===1?'':'s')+
      (left?', '+left+' to decide':', all decided')+'</div>'+M.conflicts.map(function(c,i){
        var body=c.kind==='deleted'?'<div class="a3d-brfield"><div class="a3d-brside"><b>'+bimEsc(M.into)+'</b>'+(c.gone==='ours'?'deleted it':'changed it')+'</div><div class="a3d-brside"><b>'+bimEsc(M.from)+'</b>'+(c.gone==='theirs'?'deleted it':'changed it')+'</div></div>':
          c.fields.map(function(f){return '<div class="a3d-brfield"><span class="a3d-brf">'+bimEsc(f.f)+'</span><div class="a3d-brside"><b>'+bimEsc(M.into)+'</b>'+bimEsc(bimBrVal(f.ours))+'</div><div class="a3d-brside"><b>'+bimEsc(M.from)+'</b>'+bimEsc(bimBrVal(f.theirs))+'</div></div>';}).join('');
        return '<div class="a3d-brconf'+(c.choice?' done':'')+'" data-brconf="'+i+'"><div class="a3d-brlabel">'+bimEsc(c.label)+'</div>'+body+
          '<div class="a3d-histacts"><button type="button" data-histact="mkeep:'+i+'"'+(c.choice==='ours'?' class="on"':'')+'>Keep '+bimEsc(M.into)+'\'s</button>'+
          '<button type="button" data-histact="mtake:'+i+'"'+(c.choice==='theirs'?' class="on"':'')+'>Take '+bimEsc(M.from)+'\'s</button></div></div>';
      }).join('')+'<div class="a3d-histacts"><button type="button" data-histact="mfinish"'+(left?' disabled':'')+'>Finish Merge</button><button type="button" data-histact="mabort">Cancel</button></div></div>';
  }
  function bimHistBranchHtml(){
    var H=bimHist(),B=bimHistBranches(),others=B.filter(function(b){return !b.current;});
    var r='<div class="a3d-brrow"><label class="a3d-brlbl">Branch</label><select data-histbranch="1" aria-label="The branch you are on">'+B.map(function(b){
      return '<option value="'+bimEsc(b.name)+'"'+(b.current?' selected':'')+'>'+bimEsc(b.name)+'</option>';}).join('')+'</select></div>';
    r+='<div class="a3d-histrow"><input type="text" data-brname="1" maxlength="40" placeholder="New branch: a design option" value="'+bimEsc(A3D_BR_NEW)+'"><button type="button" data-histact="branch"'+(H.head?'':' disabled title="Commit a version first"')+'>New Branch</button></div>';
    if(others.length)r+='<div class="a3d-histrow"><select data-brmergefrom="1" aria-label="The branch to merge in">'+others.map(function(b){return '<option value="'+bimEsc(b.name)+'">'+bimEsc(b.name)+'</option>';}).join('')+
      '</select><button type="button" data-histact="merge">Merge In</button><button type="button" data-histact="compare">'+(A3D_BR_CMP?'Hide Compare':'Compare')+'</button></div>';
    if(A3D_BR_CMP&&others.length)r+=bimHistCompareHtml();
    r+=bimHistMergeHtml();
    return r;
  }
  function bimHistBranchAct(k){
    var r,s,n;
    if(k==='branch'){
      n=document.querySelector('#a3d-propsbody [data-brname]');
      r=bimHistBranchNew((n&&n.value)||A3D_BR_NEW);
      if(r.error){a3dToast(r.error);return r;}
      A3D_BR_NEW='';refreshProps();a3dToast('On a new branch "'+r.name+'": what you commit now goes here');return r;
    }
    if(k==='merge'){
      s=document.querySelector('#a3d-propsbody [data-brmergefrom]');
      r=bimHistMergeStart(s?s.value:'');
      if(r.error)a3dToast(r.error);
      else if(r.upToDate)a3dToast(r.msg);
      else if(r.fastForward)a3dToast('Moved up to "'+r.from+'": nothing here it did not have');
      else if(r.conflicts)a3dToast(r.conflicts+' conflict'+(r.conflicts===1?'':'s')+': decide each, then Finish Merge');
      else if(r.merged)a3dToast('Merged: '+(r.stats?bimHistStatsTxt(r.stats):'nothing changed'));
      return r;
    }
    if(k==='compare'){A3D_BR_CMP=!A3D_BR_CMP;refreshProps();return A3D_BR_CMP;}
    if(k.indexOf('mkeep:')===0)return bimHistMergeChoose(+k.slice(6),'ours');
    if(k.indexOf('mtake:')===0)return bimHistMergeChoose(+k.slice(6),'theirs');
    if(k==='mfinish'){r=bimHistMergeFinish();if(r.error)a3dToast(r.error);else a3dToast('Merged, with '+r.conflicts+' conflict'+(r.conflicts===1?'':'s')+' decided');return r;}
    if(k==='mabort'){bimHistMergeAbort();a3dToast('Merge cancelled: nothing changed');return true;}
    return null;
  }
  function bimHistSwitchUI(name){
    var r=bimHistSwitch(name);
    if(r.error){a3dToast(r.error);refreshProps();return r;}
    if(!r.same)a3dToast('On "'+r.name+'"'+(r.head?'':': no versions yet'));
    return r;
  }
"""
rep("""  /* the model as it was at a version: an edit, so undo takes it back; the history is not rewritten */""",
    ENGINE + """  /* the model as it was at a version: an edit, so undo takes it back; the history is not rewritten */""")

# the panel: branches above the changes; the log is this branch's line
rep("""    r+='<div class="a3d-hist">';
    r+='<div class="a3d-histst" data-histstate=""", """    r+='<div class="a3d-hist">';
    try{r+=bimHistBranchHtml();}catch(eB){console.warn('[BIM] branches',eB);}   /* __acad3dV151 */
    r+='<div class="a3d-histst" data-histstate=""")
rep("""    var C=H.commits.slice().reverse(),sz=bimHistSize();""",
    """    var line={};bimHistAncestry(H.head).forEach(function(x){line[x]=1;});   /* __acad3dV151: this branch's versions */
    var C=H.commits.filter(function(c){return line[c.id];}).reverse(),sz=bimHistSize();""")
rep("""      return '<div class="a3d-histc'+(c.id===H.head?' a3d-histc-head':'')+'" data-histc="'+c.id+'"><div class="a3d-histcm">'+bimEsc(c.msg)+(c.id===H.head?' <span class="a3d-histtag">latest</span>':'')+'</div>'+""",
    """      var tags=bimHistBranches().filter(function(b){return b.head===c.id;}).map(function(b){return '<span class="a3d-histtag a3d-brtag">'+bimEsc(b.name)+'</span>';}).join(' ');   /* __acad3dV151 */
      return '<div class="a3d-histc'+(c.id===H.head?' a3d-histc-head':'')+'" data-histc="'+c.id+'"><div class="a3d-histcm">'+bimEsc(c.msg)+(c.id===H.head?' <span class="a3d-histtag">latest</span>':'')+(tags?' '+tags:'')+'</div>'+""")
rep("""    if(k.indexOf('restore:')===0)return bimHistDoRestore(k.slice(8));
    return false;""", """    if(k.indexOf('restore:')===0)return bimHistDoRestore(k.slice(8));
    var rb=bimHistBranchAct(k);if(rb!==null)return rb;   /* __acad3dV151 */
    return false;""")
# wiring: the branch select, the name typed
rep("""    if(el.propsbody)el.propsbody.addEventListener('input',function(ev){
      if(ev.target&&ev.target.hasAttribute&&ev.target.hasAttribute('data-histmsg'))A3D_HIST_MSG=ev.target.value;
    });""", """    if(el.propsbody)el.propsbody.addEventListener('input',function(ev){
      if(ev.target&&ev.target.hasAttribute&&ev.target.hasAttribute('data-histmsg'))A3D_HIST_MSG=ev.target.value;
      if(ev.target&&ev.target.hasAttribute&&ev.target.hasAttribute('data-brname'))A3D_BR_NEW=ev.target.value;   /* __acad3dV151 */
    });
    if(el.propsbody)el.propsbody.addEventListener('change',function(ev){   /* __acad3dV151: switch branch */
      if(ev.target&&ev.target.hasAttribute&&ev.target.hasAttribute('data-histbranch'))bimHistSwitchUI(ev.target.value);
    });""")
rep("""      if(ev.key!=='Enter'||!ev.target||!ev.target.hasAttribute||!ev.target.hasAttribute('data-histmsg'))return;""",
    """      if(ev.key==='Enter'&&ev.target&&ev.target.hasAttribute&&ev.target.hasAttribute('data-brname')){ev.preventDefault();ev.stopPropagation();bimHistBranchAct('branch');return;}   /* __acad3dV151 */
      if(ev.key!=='Enter'||!ev.target||!ev.target.hasAttribute||!ev.target.hasAttribute('data-histmsg'))return;""")

CSS = """.a3d-brrow{display:flex;align-items:center;gap:8px;margin:0 0 6px}
.a3d-brlbl{font-size:11.5px;color:var(--pp-muted,#8f98a2)}
.a3d-brrow select{flex:1 1 auto;min-width:0}
.a3d-brcmp{overflow-x:auto;margin:4px 0 8px}
.a3d-brcmp table{border-collapse:collapse;width:100%;font-size:11.5px}
.a3d-brcmp th,.a3d-brcmp td{padding:3px 6px;text-align:right;border-bottom:1px solid var(--pp-line,#30353c);white-space:nowrap}
.a3d-brcmp th:first-child,.a3d-brcmp td:first-child{text-align:left;color:var(--pp-muted,#8f98a2)}
.a3d-brcmp th.cur{color:var(--pp-accent,#4ea1ff)}
.a3d-brcmp tr.diff td{font-weight:600}
.a3d-brmerge{border:1px solid rgba(255,183,77,.45);border-radius:8px;padding:8px;margin:6px 0}
.a3d-brconf{border-top:1px solid var(--pp-line,#30353c);padding:6px 0}
.a3d-brconf.done{opacity:.7}
.a3d-brlabel{font-weight:600;margin-bottom:3px}
.a3d-brfield{display:grid;grid-template-columns:1fr 1fr;gap:2px 10px;margin:4px 0}
.a3d-brf{grid-column:1/-1;font-size:11px;color:var(--pp-muted,#8f98a2)}
.a3d-brside{min-width:0;font-size:11.5px;overflow-wrap:anywhere}
.a3d-brside b{display:block;font-size:10.5px;color:var(--pp-muted,#8f98a2);font-weight:600}
.a3d-histacts button.on{background:var(--pp-accent,#4ea1ff);color:#fff}
.a3d-brtag{background:rgba(78,161,255,.18);color:#9cc9ff}
"""
rep(""".a3d-hist{display:flex;flex-direction:column;gap:6px;font-size:12px}""",
    """.a3d-hist{display:flex;flex-direction:column;gap:6px;font-size:12px}
""" + CSS.rstrip('\n'))

# the commands
rep("""    ['HISTORY',['VERSIONS','VERSIONHISTORY'],'history','The model\\'s versions: what changed in each, element by element, and Restore'],""",
    """    ['HISTORY',['VERSIONS','VERSIONHISTORY'],'history','The model\\'s versions: what changed in each, element by element, and Restore'],
    ['BRANCH',['NEWBRANCH','DESIGNOPTION','OPTION'],'branch','Start a design option: a branch of the history, switched to and compared with the others'],   /* __acad3dV151 */
    ['MERGE',['MERGEBRANCH'],'merge','Merge another branch into this one, element by element, with conflicts shown side by side'],
    ['COMPAREBRANCHES',['COMPAREOPTIONS','OPTIONS'],'comparebranches','Each branch\\'s numbers side by side: walls, rooms, areas, cut and fill'],""")
rep("""    history:function(){bimHistReveal(false);},""", """    history:function(){bimHistReveal(false);},
    branch:function(){bimHistReveal(false);setTimeout(function(){var i=document.querySelector('#a3d-propsbody [data-brname]');if(i)i.focus();},0);},   /* __acad3dV151 */
    merge:function(){bimHistReveal(false);if(bimHistBranches().length<2)a3dToast('There is one branch: start another with BRANCH');},
    comparebranches:function(){A3D_BR_CMP=true;bimHistReveal(false);},""")

rep("""  var BIM_APP_VERSION={v:'V150',date:'2026-10-04'};   /* __acad3dV150 */""",
    """  var BIM_APP_VERSION={v:'V151',date:'2026-10-04'};   /* __acad3dV151 */""")
rep("""  window.__acad3dV150='toolpalette,""", """  /* __acad3dV151: branches and merge */
  window.__a3dBranches=function(){return JSON.parse(JSON.stringify(bimHistBranches()));};
  window.__a3dBranchNew=function(n){return bimHistBranchNew(n);};
  window.__a3dBranchSwitch=function(n){return bimHistSwitch(n);};
  window.__a3dBranchDelete=function(n){return bimHistBranchDelete(n);};
  window.__a3dMergeStart=function(n){var r=bimHistMergeStart(n);return JSON.parse(JSON.stringify(r));};
  window.__a3dMergeState=function(){return A3D_MERGE?JSON.parse(JSON.stringify({from:A3D_MERGE.from,into:A3D_MERGE.into,base:A3D_MERGE.base,
    conflicts:A3D_MERGE.conflicts.map(function(c){return {key:c.key,kind:c.kind,label:c.label,gone:c.gone||null,choice:c.choice||null,fields:c.fields.map(function(f){return {f:f.f,base:f.base===undefined?null:f.base,ours:f.ours===undefined?null:f.ours,theirs:f.theirs===undefined?null:f.theirs};})};})})):null;};
  window.__a3dMergeChoose=function(i,s){return bimHistMergeChoose(i,s);};
  window.__a3dMergeFinish=function(){return JSON.parse(JSON.stringify(bimHistMergeFinish()));};
  window.__a3dMergeAbort=function(){return bimHistMergeAbort();};
  window.__a3dBranchCompare=function(){return JSON.parse(JSON.stringify(bimHistCompare()));};
  window.__a3dHistBase=function(a,b){return bimHistBase(a,b);};
  window.__acad3dV151='branches,branchnew,branchswitch,switchrefused,mainbranch,mergebase,merge3,fieldmerge,conflicts,deleteconflict,fastforward,uptodate,mergecommit,compare,branchcommands,branchsaved';
  window.__acad3dV150='toolpalette,""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
