  /* ================= __acad3dV151: branches and merge (the Hub's H2) =================
     A branch is a name at a version: a design option. Merging is three ways, element by element,
     against the version both branches share -- git's merge, at the grain of a building element. */
  var BIM_BR_NAME=/^[A-Za-z0-9][A-Za-z0-9 _.\-]{0,39}$/;
  var A3D_MERGE=null,A3D_BR_CMP=false,A3D_BR_NEW='',A3D_BR_DEL='',A3D_BR_PICK='';
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
    ['roomArea','Room area (m\u00b2)',1],['gba','Gross area (m\u00b2)',1],['levels','Levels',0],['cut','Cut (m\u00b3)',1],['fill','Fill (m\u00b3)',1]];
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
    if(!others.some(function(b){return b.name===A3D_BR_DEL;}))A3D_BR_DEL='';
    if(others.length)r+='<div class="a3d-histrow"><select data-brmergefrom="1" aria-label="Another branch: to merge in, compare or delete">'+others.map(function(b){return '<option value="'+bimEsc(b.name)+'"'+(b.name===(A3D_BR_DEL||A3D_BR_PICK)?' selected':'')+'>'+bimEsc(b.name)+'</option>';}).join('')+
      '</select></div><div class="a3d-histrow"><button type="button" data-histact="merge">Merge In</button><button type="button" data-histact="compare">'+(A3D_BR_CMP?'Hide Compare':'Compare')+'</button>'+
      '<button type="button" data-histact="brdelete"'+(A3D_BR_DEL?' class="warn"':'')+'>'+(A3D_BR_DEL?'Delete '+bimEsc(A3D_BR_DEL)+'?':'Delete')+'</button></div>';
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
    if(k==='brdelete'){   /* __acad3dV151: asked once, deleted on the second tap */
      s=document.querySelector('#a3d-propsbody [data-brmergefrom]');n=s?s.value:'';
      if(!n)return null;
      if(A3D_BR_DEL!==n){A3D_BR_DEL=n;refreshProps();return {ask:n};}
      A3D_BR_DEL='';r=bimHistBranchDelete(n);
      if(r.error)a3dToast(r.error);else a3dToast('Branch "'+n+'" deleted: its versions stay in the project file');
      refreshProps();return r;
    }
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
  /* __acad3dV146: the History group and its actions */
  var A3D_HIST_OPEN={},A3D_HIST_MSG='',A3D_HIST_ALL=false;   /* __acad3dV147: Show all */   /* the message as typed: a re-render of the panel must not lose it */
  function bimHistWhen(iso){
    var d=new Date(iso);if(isNaN(d.getTime()))return '';
    function p(n){return n<10?'0'+n:''+n;}
    return d.getFullYear()+'-'+p(d.getMonth()+1)+'-'+p(d.getDate())+' '+p(d.getHours())+':'+p(d.getMinutes());
  }
  function bimHistStatsTxt(s){
    if(!s)return '';
    var r=[];if(s.added)r.push('+'+s.added);if(s.changed)r.push('~'+s.changed);if(s.removed)r.push('\u2212'+s.removed);
    return r.join(' ')||'no change';
  }
  function bimHistListHtml(d,max){
    return d.slice(0,max).map(function(x){
      return '<div class="a3d-histd a3d-histd-'+x.kind+'" data-histkey="'+bimEsc(x.key)+'" data-histkind="'+x.kind+'"><b>'+(x.kind==='added'?'+':x.kind==='removed'?'\u2212':'~')+'</b> '+bimEsc(x.label)+
        (x.props&&x.props.length?'<div class="a3d-histp">'+x.props.slice(0,6).map(function(p){return bimEsc(p.text);}).join('<br>')+(x.props.length>6?'<br>and '+(x.props.length-6)+' more':'')+'</div>':'')+'</div>';
    }).join('')+(d.length>max?'<div class="a3d-histmore"><button type="button" data-histact="all">Show all '+d.length+'</button></div>':'');
  }
  function bimHistHtml(){
    var H=bimHist(),head=bimHistHead(),d=[],r='';
    try{d=bimHistChanges();}catch(eD){console.warn('[BIM] history',eD);}
    r+='<div class="a3d-hist">';
    try{r+=bimHistBranchHtml();}catch(eB){console.warn('[BIM] branches',eB);}   /* __acad3dV151 */
    r+='<div class="a3d-histst" data-histstate="'+(d.length?'dirty':'clean')+'">'+(head?(d.length?d.length+' change'+(d.length===1?'':'s')+' since "'+bimEsc(head.msg)+'"':'No changes since "'+bimEsc(head.msg)+'"'):
      (d.length?'No version yet: '+d.length+' element'+(d.length===1?'':'s')+' to commit':'No version yet, and nothing to commit'))+'</div>';
    r+='<div class="a3d-histrow"><input type="text" data-histmsg maxlength="200" placeholder="What changed (Enter commits)" value="'+bimEsc(A3D_HIST_MSG)+'"><button type="button" data-histact="commit"'+(d.length?'':' disabled')+'>Commit</button></div>';
    if(d.length){
      r+='<div class="a3d-histchg" data-histchanges>'+bimHistListHtml(d,A3D_HIST_ALL?d.length:12)+'</div>';
      if(head)r+='<div class="a3d-histrow"><button type="button" data-histact="discard">Discard Changes</button></div>';
    }
    var line={};bimHistAncestry(H.head).forEach(function(x){line[x]=1;});   /* __acad3dV151: this branch's versions */
    var C=H.commits.filter(function(c){return line[c.id];}).reverse(),sz=bimHistSize();
    if(C.length)r+='<div class="a3d-histlog">'+C.slice(0,30).map(function(c){
      var open=!!A3D_HIST_OPEN[c.id];
      var tags=bimHistBranches().filter(function(b){return b.head===c.id;}).map(function(b){return '<span class="a3d-histtag a3d-brtag">'+bimEsc(b.name)+'</span>';}).join(' ');   /* __acad3dV151 */
      return '<div class="a3d-histc'+(c.id===H.head?' a3d-histc-head':'')+'" data-histc="'+c.id+'"><div class="a3d-histcm">'+bimEsc(c.msg)+(c.id===H.head?' <span class="a3d-histtag">latest</span>':'')+(tags?' '+tags:'')+'</div>'+
        '<div class="a3d-histmeta">'+bimHistWhen(c.at)+(c.by?' &middot; '+bimEsc(c.by):'')+' &middot; '+bimHistStatsTxt(c.stats)+'</div>'+
        '<div class="a3d-histacts"><button type="button" data-histact="show:'+c.id+'">'+(open?'Hide':'Changes')+'</button><button type="button" data-histact="restore:'+c.id+'">Restore</button></div>'+
        (open?'<div class="a3d-histchg">'+bimHistListHtml(bimHistCommitDiff(c),40)+'</div>':'')+'</div>';
    }).join('')+(C.length>30?'<div class="a3d-histmore">and '+(C.length-30)+' older</div>':'')+'</div>';
    if(C.length)r+='<div class="a3d-histsize">'+C.length+' version'+(C.length===1?'':'s')+', '+sz.blobs+' stored element'+(sz.blobs===1?'':'s')+' ('+Math.round(sz.chars/1024)+' KB), saved with the project</div>';
    return r+'</div>';
  }
  function bimHistObjHtml(o){
    var L=bimHistOf('o:'+o.id);
    if(!L.length)return bimPropText('History','not in any version yet');
    return L.slice(0,6).map(function(x){
      return '<div class="a3d-histd a3d-histd-'+x.kind+'" data-histobj="'+x.id+'"><b>'+(x.kind==='added'?'+':x.kind==='removed'?'\u2212':'~')+'</b> '+bimEsc(x.msg)+' <span class="a3d-histmeta">'+bimHistWhen(x.at)+'</span>'+
        (x.props&&x.props.length?'<div class="a3d-histp">'+x.props.slice(0,4).map(function(p){return bimEsc(p.text);}).join('<br>')+'</div>':'')+'</div>';
    }).join('')+(L.length>6?'<div class="a3d-histmore">and '+(L.length-6)+' earlier</div>':'');
  }
  function bimHistDoCommit(msg){
    var r=bimHistCommit(msg);
    if(r.error){a3dToast(r.error);return r;}
    A3D_HIST_MSG='';A3D_HIST_ALL=false;
    a3dToast('Committed "'+r.msg+'": '+bimHistStatsTxt(r.stats));
    refreshProps();
    return r;
  }
  function bimHistDoRestore(id){
    var r=bimHistRestore(id);
    if(r.error){a3dToast(r.error);return r;}
    a3dToast('Restored "'+r.msg+'": commit to keep it as the latest, or Undo to go back');
    return r;
  }
  function bimHistAct(k,ev){
    if(k==='commit'){var inp=document.querySelector('#a3d-propsbody [data-histmsg]');return bimHistDoCommit((inp&&inp.value)||A3D_HIST_MSG);}
    if(k==='discard'){var hd=bimHistHead();return hd?bimHistDoRestore(hd.id):null;}
    if(k==='all'){A3D_HIST_ALL=true;refreshProps();return true;}   /* __acad3dV147 */
    if(k.indexOf('show:')===0){var id=k.slice(5);A3D_HIST_OPEN[id]=!A3D_HIST_OPEN[id];refreshProps();return true;}
    if(k.indexOf('restore:')===0)return bimHistDoRestore(k.slice(8));
    var rb=bimHistBranchAct(k);if(rb!==null)return rb;   /* __acad3dV151 */
    return false;
  }
  /* COMMIT and HISTORY: the History group, on the Project tab */
  function bimHistReveal(focus){
    A3D.sel=null;A3D.sel2=null;A3D.selSet=[];
    bimPropReveal('History');
    if(bimShellOverlay()){var rpH=document.getElementById('a3d-right');if(rpH)rpH.classList.add('open');}   /* __acad3dV151: on a phone or tablet the sheet opens */
    refreshProps();paint();
    if(focus)setTimeout(function(){var i=document.querySelector('#a3d-propsbody [data-histmsg]');if(i)i.focus();},0);
    return true;
  }
  function bimHistCommitCommand(){
    var d=bimHistChanges(),hd=bimHistHead();
    if(!d.length){a3dToast(hd?'Nothing has changed since "'+hd.msg+'"':'There is nothing to commit yet');return false;}
    return bimHistReveal(true);
  }
  /* __acad3dV147: the right panel's width and its minimised state, remembered */
  var BIM_RIGHT_KEY='acad3dRightPanel',BIM_RIGHT_MIN=240,BIM_RIGHT_MAX=560;
  function bimRightPrefs(){try{var v=JSON.parse(localStorage.getItem(BIM_RIGHT_KEY)||'null');return v&&typeof v==='object'?v:{};}catch(eR){return {};}}
  function bimRightSave(p){try{localStorage.setItem(BIM_RIGHT_KEY,JSON.stringify(p));}catch(eW){}}
  /* __acad3dV166d: docked beside the drawing where the stylesheet docks it, over 1024 px wide and over
     500 px high; below that Properties is a drawer or a sheet. The same query as the rule that hides
     its edge and its width button, so the code and the stylesheet cannot disagree: V147's "wider than
     900" let the arrow shrink a drawer, or a sheet on a phone on its side, to a 42 px strip */
  var BIM_RIGHT_SHEET_MQ='(max-width:1024px),(max-height:500px)';
  function bimRightDesktop(){
    if(window.matchMedia)return !window.matchMedia(BIM_RIGHT_SHEET_MQ).matches;
    return (window.innerWidth||0)>1024&&(window.innerHeight||0)>500;
  }
  /* the widest Properties may be now: the drawing keeps BIM_LEFT_KEEP px beside the left panel at its
     narrowest, since the left panel gives way to Properties (V166b) but never below BIM_LEFT_MIN */
  function bimRightMax(){
    return Math.max(BIM_RIGHT_MIN,Math.min(BIM_RIGHT_MAX,Math.floor((window.innerWidth||0)-BIM_LEFT_RAIL-BIM_LEFT_MIN-BIM_LEFT_KEEP)));
  }
  /* the width on screen, and the next step up within what the screen allows; from the widest, back to
     the narrowest -- V166b's rule for the left panel */
  var BIM_RIGHT_STEPS=[BIM_RIGHT_MIN,320,400,480,BIM_RIGHT_MAX];
  function bimRightW(){var rp=document.getElementById('a3d-right');return rp?Math.round(rp.getBoundingClientRect().width):0;}
  function bimRightNext(){
    var w=bimRightW(),mx=bimRightMax(),i;
    for(i=0;i<BIM_RIGHT_STEPS.length;i++)if(BIM_RIGHT_STEPS[i]>w&&BIM_RIGHT_STEPS[i]<=mx)return BIM_RIGHT_STEPS[i];
    return w<mx?mx:BIM_RIGHT_MIN;
  }
  function bimRightStep(){return bimRightSetWidth(bimRightNext());}
  function bimRightApply(){
    var rp=document.getElementById('a3d-right'),p=bimRightPrefs();
    if(!rp)return null;
    document.body.classList.toggle('a3d-rmin',!!p.min&&bimRightDesktop());   /* minimised is a computer's; a phone or tablet closes the panel */
    var w=isFinite(p.w)?Math.max(BIM_RIGHT_MIN,Math.min(bimRightMax(),p.w)):null;   /* __acad3dV166d: within what the screen allows now; the one kept stays */
    rp.style.width=(w&&bimRightDesktop()&&!p.min)?w+'px':'';
    var b=document.getElementById('a3d-rminbtn');
    if(b){b.setAttribute('aria-pressed',p.min?'true':'false');b.title=p.min?'Show the Properties panel':'Minimise the Properties panel';}
    bimShellDockW();   /* __acad3dV166b: the left panel keeps the drawing its room */
    /* __acad3dV166d: the edge's value and range, and where the button's next press goes */
    var cw=bimRightW(),mx=bimRightMax(),nx=bimRightNext(),g=rp.querySelector('.a3d-rgrip'),wb=rp.querySelector('[data-rpwidth]');
    if(g){g.setAttribute('aria-valuenow',String(cw));g.setAttribute('aria-valuemin',String(BIM_RIGHT_MIN));g.setAttribute('aria-valuemax',String(mx));}
    if(wb){wb.setAttribute('aria-label','Properties width '+cw+' px: '+(nx>cw?'widen to '+nx:'back to '+nx));wb.title=wb.getAttribute('aria-label');}
    return {w:rp.getBoundingClientRect().width,min:!!p.min,kept:typeof p.w==='number'?p.w:null,max:mx,next:nx,docked:bimRightDesktop(),mq:BIM_RIGHT_SHEET_MQ,
      grip:!!(g&&getComputedStyle(g).display!=='none'),button:!!(wb&&getComputedStyle(wb).display!=='none')};
  }
  function bimRightSetWidth(w){
    var p=bimRightPrefs();
    if(w===null)delete p.w;   /* __acad3dV166d: null forgets it, as the edge's double click does */
    else p.w=Math.round(Math.max(BIM_RIGHT_MIN,Math.min(bimRightMax(),w)));
    bimRightSave(p);
    var r=bimRightApply();try{size();paint();}catch(eS){}
    return r;
  }
  function bimRightToggleMin(on){
    var p=bimRightPrefs();p.min=on===undefined?!p.min:!!on;bimRightSave(p);
    var r=bimRightApply();try{size();paint();}catch(eS){}
    return r;
  }
  function bimRightWire(rp,sec){
    if(!rp||rp.querySelector('.a3d-rgrip'))return;
    /* __acad3dV166d: the edge is the W3C's window splitter -- a focusable separator named by the
       header's "Properties", its width as its value */
    var g=document.createElement('div');g.className='a3d-rgrip';g.tabIndex=0;g.title='Drag to resize; double-click to put it back';
    g.setAttribute('role','separator');g.setAttribute('aria-orientation','vertical');g.setAttribute('aria-controls','a3d-right');g.setAttribute('aria-labelledby','a3d-rpttl');
    rp.insertBefore(g,rp.firstChild);
    /* the phone's sheet: a grab bar that raises it and lowers it */
    var sb=document.createElement('div');sb.className='a3d-rsheetbar';sb.setAttribute('role','button');sb.setAttribute('aria-label','Raise or lower Properties');sb.innerHTML='<i></i>';
    sb.addEventListener('click',function(){rp.classList.toggle('a3d-rtall');});
    rp.insertBefore(sb,sec||null);
    var hd=sec&&sec.querySelector('.a3d-palhd');
    if(hd&&!document.getElementById('a3d-rminbtn')){
      var wb=document.createElement('button');wb.type='button';wb.className='a3d-rpwbtn';wb.setAttribute('data-rpwidth','1');   /* __acad3dV166d: the width, by one press */
      wb.innerHTML='<svg viewBox="0 0 18 18" aria-hidden="true"><path d="M2.5 9h13M5.5 6 2.5 9l3 3M12.5 6l3 3-3 3"/></svg>';
      wb.addEventListener('click',function(){bimRightStep();});
      hd.appendChild(wb);
      var b=document.createElement('button');b.type='button';b.id='a3d-rminbtn';b.className='a3d-rmin';b.setAttribute('aria-label','Minimise the Properties panel');
      b.innerHTML='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M9 6l6 6-6 6"/></svg>';
      b.addEventListener('click',function(){
        if(!bimRightDesktop()){rp.classList.remove('open');rp.classList.remove('a3d-rtall');return;}   /* the sheet or drawer closes */
        bimRightToggleMin();
      });
      hd.appendChild(b);
    }
    /* __acad3dV166d: dragged by a mouse, a pen or a finger (pointer events: it took mousedown alone, so a
       finger could not move it), within what the screen allows, the left panel giving way as it goes;
       a cancelled drag puts the width back. The edge is shown only where Properties is docked. */
    var dr=null;
    g.addEventListener('pointerdown',function(ev){
      if(ev.button>0)return;
      ev.preventDefault();
      dr={x:ev.clientX,w:bimRightW(),id:ev.pointerId,now:null};
      try{g.setPointerCapture(ev.pointerId);}catch(eC){}
      g.classList.add('drag');document.body.classList.add('a3d-rpdrag');
    });
    g.addEventListener('pointermove',function(ev){
      if(!dr||ev.pointerId!==dr.id)return;
      var w=Math.round(Math.max(BIM_RIGHT_MIN,Math.min(bimRightMax(),dr.w+dr.x-ev.clientX)));
      if(w===dr.now)return;
      dr.now=w;rp.style.width=w+'px';bimShellDockW();try{size();paint();}catch(eS){}
    });
    function end(ev,keep){
      if(!dr||ev.pointerId!==dr.id)return;
      var w=dr.now;dr=null;
      g.classList.remove('drag');document.body.classList.remove('a3d-rpdrag');
      if(keep&&w!==null)bimRightSetWidth(w);
      else{bimRightApply();try{size();paint();}catch(eS){}}
    }
    g.addEventListener('pointerup',function(ev){end(ev,true);});
    g.addEventListener('pointercancel',function(ev){end(ev,false);});
    g.addEventListener('dblclick',function(){bimRightSetWidth(null);});
    /* the keys: the splitter moves the way the arrow points, so Left widens Properties, which is to its
       right; Home and End the narrowest and the widest; Enter minimises it, the focus going to the
       minimise button, whose Enter brings it back. A focused separator keeps its keys from the model (V166b). */
    g.addEventListener('keydown',function(ev){
      var k=ev.key,st=ev.shiftKey?64:16;
      if(k==='ArrowLeft'||k==='ArrowRight'){ev.preventDefault();bimRightSetWidth(bimRightW()+(k==='ArrowLeft'?st:-st));return;}
      if(k==='Home'||k==='End'){ev.preventDefault();bimRightSetWidth(k==='Home'?BIM_RIGHT_MIN:bimRightMax());return;}
      if(k==='Enter'){
        ev.preventDefault();
        bimRightToggleMin(true);
        var mb=document.getElementById('a3d-rminbtn');if(mb)mb.focus();
      }
    });
    window.addEventListener('resize',function(){bimRightApply();});
    bimRightApply();
  }
