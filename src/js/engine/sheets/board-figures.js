  /* ================= __acad3dV172b: a board's figures, arranged =================
     reference/research-ladybug-weather-comfort.md, 13. Every figure the boards draw has a name of its own
     ('clim.temp', 'zn.secA', 'lb.utci' ...). A board in the set may keep a list of figures, each placed on
     the board's own grid: 12 columns across and the same step down (x and w in columns, y and h in those
     steps), with its options. A board without a list is drawn as it always was; a board of one's own
     (kind 'custom') is only its list. A list is laid out at the board's full width, 1408 px across, as its
     12 columns are on a wide screen and on paper, and is zoomed to a narrower main view; on a phone its
     figures flow in one column, in reading order. The figures are read from the boards themselves: each
     board is drawn once, its cards kept (bimClbCard, under A3D_FIGCAP), and drawn again where the list
     puts them. */
  var BIM_BRD_W0=1408,BIM_BRD_G=12,BIM_BRD_P0=(BIM_BRD_W0+BIM_BRD_G)/12;
  var A3D_FIGCAP=null;   /* while a board is read for its figures: what each card was drawn from */
  A3D_CLB.raw=false;A3D_CLB.edit=false;A3D_CLB.cid=null;A3D_CLB.other=false;
  /* the catalogue: name, the board that draws it, its group, and what it is called. A function, not a
     list made at load: a project is read before this file has run (bimPresValid). */
  function bimFigCat(){
    if(bimFigCat.L)return bimFigCat.L;
    var I='Indicators',C='Climate',L='Comfort and design days (Ladybug)',R='Environmental risk',Z='Zoning and yield',A='Access and circulation',P='People and place';
    bimFigCat.L=[
      ['clim.kpis','climate',I,'Climate and risk indicators'],['zn.kpis','zoning',I,'Zoning and yield indicators'],
      ['acc.kpis','access',I,'Access indicators'],['ppl.kpis','access',I,'People indicators'],
      ['clim.temp','climate',C,'Temperature and rainfall by month'],['clim.wind','climate',C,'Wind rose, a year of hours'],
      ['clim.heat','climate',C,'Every hour of the year, by temperature'],['clim.sun','climate',C,'Sun path'],
      ['clim.dd','climate',C,'Heating and cooling degree days'],['clim.solar','climate',C,'Solar energy by month'],
      ['clim.psy','climate',C,'Outdoor comfort on the psychrometric chart'],
      ['lb.utci','climate',L,'UTCI, outdoor thermal comfort'],['lb.psych','climate',L,'Psychrometric chart, comfort and passive strategies'],
      ['lb.wind','climate',L,'Wind rose from the weather file'],['lb.dd','climate',L,'Design days'],
      ['risk.quake','climate',R,'Earthquakes nearby'],['risk.air','climate',R,'Air quality, PM2.5'],
      ['zn.table','zoning',Z,'Zoning analysis table'],['zn.secA','zoning',Z,'Envelope section, front to rear'],
      ['zn.secB','zoning',Z,'Envelope section, side to side'],['zn.rules','zoning',Z,'Each side\'s setback rule'],
      ['zn.plan','zoning',Z,'The lot and its buildable area'],['zn.plates','zoning',Z,'Floor plates by storey'],
      ['zn.yield','zoning',Z,'Yield: floor area, units and parking'],
      ['acc.walk','access',A,'Walk times along the streets'],['acc.needs','access',A,'Daily needs within a walk'],
      ['acc.streets','access',A,'Streets and frontage'],['acc.stops','access',A,'Transit stops'],['acc.conn','access',A,'Street connectivity'],
      ['ppl.compare','access',P,'The tract against its county and state'],['ppl.commute','access',P,'How people get to work'],
      ['ppl.pyramid','access',P,'Age and sex'],
      ['text','','Text','A heading']
    ].map(function(r){return {f:r[0],kind:r[1],cat:r[2],name:r[3],kpis:/\.kpis$/.test(r[0])};});
    return bimFigCat.L;
  }
  function bimFigEntry(f){var L=bimFigCat(),i;for(i=0;i<L.length;i++)if(L[i].f===f)return L[i];return null;}
  /* where its data comes from, when it has none */
  function bimFigHint(E){
    if(!E)return 'This figure is not known to this version of the app.';
    if(/^lb\./.test(E.f))return 'Ladybug has not run: Analyze, Climate, open a weather file or get a year of hours, then Run.';
    if(E.kind==='climate')return 'No climate and risk data: Analyze, Climate, Get climate and risk.';
    if(E.kind==='zoning')return 'No zoning: Analyze, Legal and regulatory, Enter zoning.';
    if(/^ppl\./.test(E.f))return 'No census figures: Analyze, Access and circulation, Get access and people (US sites).';
    return 'No access data: Analyze, Access and circulation, Get access and people.';
  }
  /* ---- the record: kept with the project, and read before this file has run ---- */
  function bimBrdNum(v,lo,hi,d){v=typeof v==='number'&&isFinite(v)?v:d;return Math.max(lo,Math.min(hi,Math.round(v*10000)/10000));}
  function bimBrdOpts(o){
    var r={};
    if(!o||typeof o!=='object')return r;
    if(typeof o.t==='string'&&o.t.replace(/\s+/g,''))r.t=o.t.replace(/\s+/g,' ').trim().slice(0,200);
    if(o.show==='table'||o.show==='both')r.show=o.show;
    if(o.cond==='sun_wind'||o.cond==='shade_wind'||o.cond==='sun_still'||o.cond==='shade_still')r.cond=o.cond;
    return r;
  }
  function bimBrdFigsValid(L){
    var out=[],seen={},n=0,i,f,r,k;
    if(!Array.isArray(L))return null;
    for(i=0;i<L.length&&out.length<80;i++){
      f=L[i];
      if(!f||typeof f!=='object'||typeof f.f!=='string'||!/^(text|[a-z]{2,5}\.[A-Za-z0-9]{1,12})$/.test(f.f))continue;
      r={k:'',f:f.f,x:0,y:0,w:1,h:1};
      r.w=bimBrdNum(f.w,1,12,6);r.x=bimBrdNum(f.x,0,12-r.w,0);
      r.h=bimBrdNum(f.h,0.25,400,4);r.y=bimBrdNum(f.y,0,4000,0);
      k=typeof f.k==='string'&&/^f\d{1,6}$/.test(f.k)&&!seen[f.k]?f.k:'';
      r.o=bimBrdOpts(f.o);
      if(!Object.keys(r.o).length)delete r.o;
      if(k)seen[k]=1;
      r.k=k;
      out.push(r);
    }
    out.forEach(function(r2){if(!r2.k){do{n++;}while(seen['f'+n]);r2.k='f'+n;seen[r2.k]=1;}});
    return out;
  }
  /* the fields a board's record keeps beyond its id and kind, when they are good */
  function bimBrdKeep(r,b){
    var F=bimBrdFigsValid(b&&b.figs);
    if(F)r.figs=F;
    if(r.kind!=='custom'&&b&&Array.isArray(b.off)){
      var off=b.off.filter(function(x,i){return typeof x==='string'&&/^[a-z]{2,5}\.[A-Za-z0-9]{1,12}$/.test(x)&&b.off.indexOf(x)===i;}).slice(0,100);
      if(off.length&&r.figs)r.off=off;
    }
    if(r.kind==='custom'){
      r.name=(b&&typeof b.name==='string'&&b.name.replace(/\s+/g,''))?b.name.replace(/\s+/g,' ').trim().slice(0,80):'Board';
      if(!r.figs)r.figs=[];
    }
    return r;
  }
  /* ---- the figures, read from the boards ---- */
  /* a board drawn as it always is, its cards kept: {html, figs:{f:{cls,title,dek,body,src} or {kpis}}, order, notes} */
  function bimFigCapture(kind,narrow){
    var keep=A3D_FIGCAP,raw=A3D_CLB.raw,out={html:'',figs:{},order:[],notes:''},i,j;
    A3D_FIGCAP=out;A3D_CLB.raw=true;
    try{out.html=bimBoardHtmlFor(kind,!!narrow);}
    catch(eC){console.warn('[BIM] The '+bimBoardName(kind)+' board could not be read for its figures',eC);}
    finally{A3D_FIGCAP=keep;A3D_CLB.raw=raw;}
    i=out.html.indexOf('<footer class="a3d-clb-notes">');j=i<0?-1:out.html.indexOf('</footer>',i);
    if(j>i)out.notes=out.html.slice(i,j+9);
    return out;
  }
  /* bimClbCard's part: a card drawn while a board is read */
  function bimFigCapCard(id,C,title,dek,body,src){
    if(A3D_FIGCAP&&id&&!A3D_FIGCAP.figs[id]){A3D_FIGCAP.figs[id]={cls:C,title:title,dek:dek,body:body,src:src};A3D_FIGCAP.order.push(id);}
  }
  /* a board's indicators, as it draws them */
  function bimFigCapKpis(id,kp){
    if(A3D_FIGCAP&&kp&&kp.length&&!A3D_FIGCAP.figs[id]){A3D_FIGCAP.figs[id]={kpis:kp.slice()};A3D_FIGCAP.order.push(id);}
  }
  /* a Ladybug figure with its own options (UTCI's condition) */
  function bimFigLb(f,o){
    var keep=A3D_FIGCAP,cap={figs:{},order:[]},i;
    for(i=0;i<BIM_LB_FIGS.length;i++)if(BIM_LB_FIGS[i][0]===f){
      A3D_FIGCAP=cap;
      try{BIM_LB_FIGS[i][1](o||null,0);}
      catch(eL){console.warn('[BIM] The Ladybug figure '+f+' could not be drawn',eL);}
      finally{A3D_FIGCAP=keep;}
    }
    return cap.figs[f]||null;
  }
  /* what one figure is drawn from, in a render: the boards read once each */
  function bimFigSrc(ctx,f,o){
    var E=bimFigEntry(f);
    if(!E||!E.kind)return null;
    if(/^lb\./.test(f)&&o&&o.cond)return bimFigLb(f,o);
    if(!ctx.caps[E.kind])ctx.caps[E.kind]=bimFigCapture(E.kind,ctx.narrow);
    return ctx.caps[E.kind].figs[f]||null;
  }
  /* the card of one placed figure: numbered if it is a figure with data */
  function bimFigCardHtml(F,P,no){
    var E=bimFigEntry(F.f),o=F.o||{};
    if(F.f==='text')return '<div class="a3d-clb-tcard"><h2 class="a3d-clb-texth">'+bimClbE(o.t||'A heading')+'</h2></div>';
    if(!P)return '<figure class="a3d-clb-card a3d-clb-ecard"><figcaption><div class="a3d-clb-fno">'+bimClbE(E?E.cat:'Figure')+'</div><h2 class="a3d-clb-h2">'+
      bimClbE(o.t||(E?E.name:F.f))+'</h2></figcaption><div class="a3d-clb-empty">'+bimClbE(bimFigHint(E))+'</div></figure>';
    if(P.kpis)return '<figure class="a3d-clb-card a3d-clb-kcard"><figcaption><h2 class="a3d-clb-h2">'+bimClbE(o.t||E.name)+'</h2></figcaption>'+
      '<section class="a3d-clb-kpis" aria-label="'+bimClbE(E.name)+'" style="--n:'+P.kpis.length+'">'+P.kpis.join('')+'</section></figure>';
    return bimClbCard(P.cls.concat(['@'+F.f]),no,o.t||P.title,P.dek,P.body,P.src);
  }
  /* ---- the layout ---- */
  /* reading order: bands of figures whose rows overlap, top to bottom; in a band, row by row, left to right */
  function bimBrdBands(figs){
    var L=figs.slice().sort(function(a,b){return a.y-b.y||a.x-b.x;}),bands=[],cur=null,i,f,row,ry;
    for(i=0;i<L.length;i++){
      f=L[i];
      if(cur&&f.y<cur.b-1e-6){cur.f.push(f);if(f.y+f.h>cur.b)cur.b=f.y+f.h;}
      else{cur={t:f.y,b:f.y+f.h,f:[f]};bands.push(cur);}
    }
    bands.forEach(function(D){
      row=0;ry=null;
      D.f.forEach(function(g){if(ry===null||g.y-ry>=0.25){if(ry!==null)row++;ry=g.y;}g.__row=row;});
      D.f.sort(function(a,b){return a.__row-b.__row||a.x-b.x;});
      D.f.forEach(function(g){delete g.__row;});
    });
    return bands;
  }
  function bimBrdPx(v){return Math.round(v*1000)/1000;}
  /* figures that overlap one another: shown in Edit */
  function bimBrdOverlaps(figs){
    var n=0,i,j,a,b,hit={};
    for(i=0;i<figs.length;i++)for(j=i+1;j<figs.length;j++){
      a=figs[i];b=figs[j];
      if(a.x<b.x+b.w-1e-6&&b.x<a.x+a.w-1e-6&&a.y<b.y+b.h-1e-6&&b.y<a.y+a.h-1e-6){hit[a.k]=1;hit[b.k]=1;}
    }
    for(i in hit)if(hit.hasOwnProperty(i))n++;
    return {n:n,k:hit};
  }
  /* the arranged figures: bands of absolutely placed figures, 1408 px across */
  function bimBrdArrHtml(figs,ctx){
    var bands=bimBrdBands(figs),P=BIM_BRD_P0,G=BIM_BRD_G,ov=ctx.edit?bimBrdOverlaps(figs):{k:{}},prev=null,h,bot=0;
    figs.forEach(function(f){if(f.y+f.h>bot)bot=f.y+f.h;});
    h='<section class="a3d-clb-arr'+(ctx.edit?' edit':'')+'" aria-label="Figures"'+(ctx.edit?' style="padding-bottom:'+bimBrdPx(2*P)+'px"':'')+'>';
    if(ctx.edit)h+='<div class="a3d-clb-arrgrid'+(A3D_SNAP.grid?' on':'')+'" aria-hidden="true" style="height:'+bimBrdPx((bot+2)*P)+'px"></div>';
    bands.forEach(function(D){
      var mt=prev===null?D.t*P:(D.t-prev)*P+G;
      h+='<div class="a3d-clb-band'+(prev===null?' first':'')+'" style="height:'+bimBrdPx((D.b-D.t)*P-G)+'px;margin-top:'+bimBrdPx(mt)+'px">';
      D.f.forEach(function(F){h+=bimBrdFigHtml(F,ctx,D.t,!!ov.k[F.k]);});
      h+='</div>';
      prev=D.b;
    });
    return h+'</section>';
  }
  var BIM_BRD_GRIP='<svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="5.5" cy="3.5" r="1.3"/><circle cx="10.5" cy="3.5" r="1.3"/><circle cx="5.5" cy="8" r="1.3"/><circle cx="10.5" cy="8" r="1.3"/><circle cx="5.5" cy="12.5" r="1.3"/><circle cx="10.5" cy="12.5" r="1.3"/></svg>';
  var BIM_BRD_MORE='<svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="3.5" cy="8" r="1.4"/><circle cx="8" cy="8" r="1.4"/><circle cx="12.5" cy="8" r="1.4"/></svg>';
  function bimBrdFigHtml(F,ctx,top,over){
    var P=BIM_BRD_P0,G=BIM_BRD_G,o=F.o||{},src=F.f==='text'?null:bimFigSrc(ctx,F.f,o),no=0,E=bimFigEntry(F.f),lab;
    if(src&&!src.kpis){ctx.no++;no=ctx.no;}
    lab=no?'Fig. '+no:(F.f==='text'?'Heading':(E?E.name:'Figure'));
    var cls='a3d-clb-fig'+(o.show?' o-'+o.show:'')+(over?' over':'')+(F.f==='text'?' t':'');
    var s='<div class="'+cls+'" data-brdk="'+F.k+'" data-brdf="'+bimClbE(F.f)+'" style="left:'+bimBrdPx(F.x*P)+'px;top:'+bimBrdPx((F.y-top)*P)+'px;width:'+bimBrdPx(F.w*P-G)+'px;height:'+bimBrdPx(F.h*P-G)+'px"'+
      (ctx.edit?' tabindex="0" role="group" aria-label="'+bimClbE(lab)+': arrow keys move it, Shift and the arrow keys size it, Delete removes it"':'')+'>'+bimFigCardHtml(F,src,no);
    if(ctx.edit)s+='<div class="a3d-clb-fctl"><button type="button" class="a3d-clb-grip" data-brdgrip="1" aria-label="Move '+bimClbE(lab)+'" title="Drag to move">'+BIM_BRD_GRIP+'</button>'+
      '<button type="button" class="a3d-clb-fmenu" data-brdmenu="1" aria-label="'+bimClbE(lab)+': its menu" aria-haspopup="menu" title="Options, duplicate, remove">'+BIM_BRD_MORE+'</button></div>'+
      '<div class="a3d-clb-rsz" data-brdrsz="1" title="Drag to size"></div>';
    return s+'</div>';
  }
  /* a figure's own width on a board, from its card's span */
  function bimFigSpan(P){
    if(!P||P.kpis||!P.cls)return 12;
    var m=/^s(\d+)$/,i,r;
    for(i=0;i<P.cls.length;i++){r=m.exec(P.cls[i]);if(r)return Math.max(1,Math.min(12,+r[1]));}
    return 12;
  }
  /* ---- the board's page ---- */
  function bimClbWhich(){return A3D_CLB.kind==='custom'?A3D_CLB.cid:A3D_CLB.kind;}
  function bimBoardKey(b){return b.kind==='custom'?b.id:b.kind;}
  function bimBoardLabel(b){return !b?'':(b.kind==='custom'?(b.name||'Board'):bimBoardName(b.kind));}
  function bimClbLabel(){var b=A3D_CLB.kind==='custom'?bimBoardById(A3D_CLB.cid):null;return b?bimBoardLabel(b):bimBoardName(A3D_CLB.kind);}
  function bimBoardKeyLabel(key){var b=bimBoardById(key);return b&&b.kind==='custom'?bimBoardLabel(b):bimBoardName(key);}
  /* the record of the board being drawn: its own, in the set, or null */
  function bimBrdRec(){
    if(A3D_CLB.kind==='custom')return bimBoardById(A3D_CLB.cid);
    return bimBoardById('board-'+A3D_CLB.kind);
  }
  /* the main board, editable: what Edit draws and drags (a board without a list, as it is laid out now) */
  function bimBrdEditing(){return A3D_CLB.edit&&!A3D_CLB.other;}
  /* the whole board, as bimClbHtml gives it */
  function bimBrdHtml(){
    var B=bimBrdRec(),edit=bimBrdEditing(),h,figs=null,raw;
    if(A3D_CLB.kind==='custom'){
      if(!B)return '<div class="a3d-clb-bar"><div class="a3d-clb-bart">Board</div><button type="button" class="a3d-clb-btn" data-clb="close" aria-label="Close the board">Close</button></div>'+
        '<div class="a3d-clb-page"><div class="a3d-clb-empty">This board is no longer in the set.</div></div>';
      return bimBrdCustomHtml(B,edit);
    }
    if(B&&B.figs)figs=B.figs;
    else if(B&&edit)figs=bimBrdWorking(B);
    if(!figs){
      A3D_CLB.raw=true;
      try{raw=bimClbHtml();}finally{A3D_CLB.raw=false;}
      return bimBrdBar(raw,B,false);
    }
    h=bimBrdBuiltinHtml(B,figs,edit);
    return bimBrdBar(h,B,edit);
  }
  /* the board's bar: Edit beside Close; in Edit, the edit bar in its place */
  function bimBrdBar(h,B,edit){
    var cl='<button type="button" class="a3d-clb-btn" data-clb="close" aria-label="Close the board">Close</button></div>',i=h.indexOf(cl),s;
    if(!B||A3D_CLB.other)return h;
    if(i<0){console.warn('[BIM] The board\'s bar was not found; it is drawn without Edit');return h;}
    if(!edit)return h.slice(0,i)+'<button type="button" class="a3d-clb-btn" data-brd="edit" aria-pressed="false" title="Arrange the figures, add, remove and size them; the drawing\'s Snap, Grid and Ortho apply">Edit</button>'+h.slice(i);
    s=h.indexOf('<div class="a3d-clb-bar">');
    if(s!==0){console.warn('[BIM] The board\'s bar was not where it is drawn; Edit keeps it');return h;}
    return bimBrdEditBar(B)+h.slice(i+cl.length);
  }
  function bimBrdEditBar(B){
    var c=B.kind==='custom';
    return '<div class="a3d-clb-bar a3d-clb-ebar"><div class="a3d-clb-bart">Editing '+bimClbE(bimBoardLabel(B))+'</div>'+
      (c?'<input type="text" class="a3d-clb-name" data-brdname="1" maxlength="80" value="'+bimClbE(B.name||'')+'" aria-label="The board\'s name">':'')+
      '<button type="button" class="a3d-clb-btn" data-brd="add" aria-haspopup="dialog">Add a figure</button>'+
      (!c&&B.figs?'<button type="button" class="a3d-clb-btn" data-brd="reset" title="The board\'s own figures, in their own places">Reset</button>':'')+
      '<span class="a3d-clb-snaps a3d-clb-hide-s" role="group" aria-label="Snaps, as in drawing">'+
        '<button type="button" class="a3d-clb-btn" data-brdsnap="point" aria-pressed="'+!!A3D_SNAP.point+'" title="Edges catch other figures\' edges (F3)">Snap</button>'+
        '<button type="button" class="a3d-clb-btn" data-brdsnap="grid" aria-pressed="'+!!A3D_SNAP.grid+'" title="Edges on the board\'s 12 columns and rows (F9)">Grid</button>'+
        '<button type="button" class="a3d-clb-btn" data-brdsnap="ortho" aria-pressed="'+!!A3D_SNAP.ortho+'" title="A drag straight across or straight down (F8)">Ortho</button></span>'+
      '<button type="button" class="a3d-clb-btn pri" data-brd="done">Done</button>'+
      '<button type="button" class="a3d-clb-btn" data-clb="close" aria-label="Close the board">Close</button></div>';
  }
  function bimBrdEditHint(figs){
    var ov=bimBrdOverlaps(figs).n;
    return '<p class="a3d-clb-ehint" role="note">'+(A3D_CLB.narrow?'On a phone the figures are in reading order: each one\'s menu moves it earlier or later. Arrange them on a larger screen.':
      'Drag a figure by its handle or its body, size it by its corner. Snap, Grid and Ortho are the drawing\'s own (F3, F9, F8). The figure in focus moves with the arrow keys and sizes with Shift.')+
      (ov?' <b>'+ov+' figures overlap.</b>':'')+'</p>';
  }
  /* one of the three boards with its list: its header and indicators as ever, the list where its grid was;
     its own figures that came after the list was made (new data) follow, as the board lays them out */
  function bimBrdBuiltinHtml(B,figs,edit){
    var ctx={edit:edit,narrow:A3D_CLB.narrow,caps:{},no:0},i,j,mid,own,raw,extra=[],off=B.off||[],have={};
    ctx.caps[B.kind]=bimFigCapture(B.kind,A3D_CLB.narrow);
    own=ctx.caps[B.kind];raw=own.html;   /* the board as it is drawn, read once: its page, and its cards */
    figs.forEach(function(F){have[F.f]=1;});
    mid=bimBrdArrHtml(figs,ctx);
    own.order.forEach(function(f){
      var P=own.figs[f];
      if(have[f]||off.indexOf(f)>=0||P.kpis)return;
      ctx.no++;
      extra.push('<div class="a3d-clb-xfig" data-brdx="'+bimClbE(f)+'">'+bimClbCard(P.cls.concat(['@'+f]),ctx.no,P.title,P.dek,P.body,P.src)+
        (edit?'<button type="button" class="a3d-clb-btn a3d-clb-place" data-brdplace="'+bimClbE(f)+'">Place on the board</button>':'')+'</div>');
    });
    if(extra.length)mid+=(edit?'<p class="a3d-clb-ehint">New since the board was arranged: Place puts a figure below the others.</p>':'')+
      '<section class="a3d-clb-grid a3d-clb-extra">'+extra.join('')+'</section>';
    if(edit)mid=bimBrdEditHint(figs)+mid;
    i=raw.indexOf('<section class="a3d-clb-grid"');
    if(i>=0){
      j=raw.indexOf('</section><footer class="a3d-clb-notes">',i);
      j=j>=0?j+10:raw.indexOf('</section>',i)+10;
      if(j<10){console.warn('[BIM] The board\'s figures were not found; the list is shown after them');j=i;}
      return raw.slice(0,i)+mid+raw.slice(j);
    }
    i=raw.lastIndexOf('</div>');
    return raw.slice(0,i)+mid+raw.slice(i);
  }
  /* a board of one's own: its name, its list, and the notes of the boards its figures come from */
  function bimBrdCustomHtml(B,edit){
    var ctx={edit:edit,narrow:A3D_CLB.narrow,caps:{},no:0},figs=B.figs||[],kinds=[],h,notes='',lb=false;
    var site=(A3D.site&&A3D.site.name&&A3D.site.name!=='Site')?A3D.site.name:(bimProjectLabel()||'The site');
    figs.forEach(function(F){var E=bimFigEntry(F.f);if(E&&E.kind&&kinds.indexOf(E.kind)<0)kinds.push(E.kind);if(/^lb\./.test(F.f))lb=true;});
    var arr=figs.length?bimBrdArrHtml(figs,ctx):'';
    kinds.forEach(function(k){
      var N=ctx.caps[k]&&ctx.caps[k].notes,a,b;
      if(!N)return;
      a=N.indexOf('<ul>');b=N.lastIndexOf('</ul>');
      if(a>=0&&b>a)notes+='<h4>'+bimClbE(bimBoardName(k))+'</h4>'+N.slice(a,b+5);
    });
    if(lb&&notes.indexOf('ladybug.tools')<0)notes+='<ul><li>Comfort, design days and the Ladybug wind rose: <a href="https://www.ladybug.tools/" target="_blank" rel="noopener">Ladybug Tools</a>\' own code (AGPL-3.0), unchanged, run in the browser by Pyodide, on '+
      bimClbE(bimLbSrcWords(bimLbSrcKept()))+'.</li></ul>';
    h='<div class="a3d-clb-bar"><div class="a3d-clb-bart">'+bimClbE(B.name||'Board')+'</div>'+
      '<button type="button" class="a3d-clb-btn" data-clb="tables" aria-pressed="'+A3D_CLB.tables+'">Tables</button>'+
      '<button type="button" class="a3d-clb-btn a3d-clb-hide-s" data-clb="print">Print</button>'+
      '<button type="button" class="a3d-clb-btn" data-clb="close" aria-label="Close the board">Close</button></div>'+
      '<div class="a3d-clb-page"><header><div class="a3d-clb-kicker">Board · '+bimClbE(site)+'</div><h1 class="a3d-clb-h1">'+bimClbE(B.name||'Board')+'</h1>'+
      '<p class="a3d-clb-sub">'+bimClbE(figs.length?(ctx.no+' figure'+(ctx.no===1?'':'s')+(kinds.length?' from '+kinds.map(function(k){return bimBoardName(k);}).join(', '):'')):'No figures yet')+'</p></header>'+
      (edit?bimBrdEditHint(figs):'')+
      (figs.length?arr:'<div class="a3d-clb-empty">This board has no figures yet. '+(edit?'Add a figure puts the first one on it.':'Edit, then Add a figure: any analysis the project has, from any board.')+
        (A3D_CLB.other?'':'<div style="margin-top:12px"><button type="button" class="a3d-clb-btn pri" data-brd="addnew">Add a figure</button></div>')+'</div>')+
      (notes?'<footer class="a3d-clb-notes"><h3>Method and sources</h3>'+notes+'</footer>':'')+'</div>';
    return bimBrdBar(h,B,edit);
  }
  /* the arranged figures are 1408 px across; a narrower main view zooms them to its width */
  function bimBrdZoom(root){
    var A=root&&root.querySelectorAll?root.querySelectorAll('.a3d-clb-arr'):[],i,p,cs,w,z;
    for(i=0;i<A.length;i++){
      p=A[i].parentNode;
      if(!p)continue;
      cs=(p.ownerDocument.defaultView||window).getComputedStyle(p);
      w=p.clientWidth-(parseFloat(cs.paddingLeft)||0)-(parseFloat(cs.paddingRight)||0);
      z=w>0?Math.min(1,w/BIM_BRD_W0):1;
      A[i].style.setProperty('--z',z.toFixed(5));
    }
  }
  /* ---- measuring: off screen, at the board's full width ---- */
  function bimBrdMeasurer(w,cls){
    var m=document.createElement('div');
    m.className='a3d-clb w-l'+(cls?' '+cls:'');
    m.setAttribute('aria-hidden','true');
    m.style.cssText='position:absolute;inset:auto;left:-40000px;top:0;width:'+w+'px;height:auto;overflow:visible;visibility:hidden;pointer-events:none;z-index:-1';
    document.body.appendChild(m);
    return m;
  }
  /* a board without a list, as it is laid out on a wide screen: its figures, and the access board's headings */
  function bimBrdMeasureDefault(kind){
    var cap=bimFigCapture(kind,false),m=bimBrdMeasurer(1440),out=[],g,gr,P,n=0;
    try{
      m.innerHTML=cap.html;
      g=m.querySelector('.a3d-clb-grid');
      if(!g)return out;
      gr=g.getBoundingClientRect();P=(gr.width+BIM_BRD_G)/12;
      var put=function(el,f,o){
        var r=el.getBoundingClientRect(),F={k:'f'+(++n),f:f,x:(r.left-gr.left)/P,y:(r.top-gr.top)/P,w:(r.width+BIM_BRD_G)/P,h:(r.height+BIM_BRD_G)/P};
        F.x=Math.max(0,Math.round(F.x*1000)/1000);F.w=Math.min(12-F.x,Math.round(F.w*1000)/1000);
        F.y=Math.max(0,Math.round(F.y*1000)/1000);F.h=Math.max(0.25,Math.round(F.h*1000)/1000);
        if(o)F.o=o;
        out.push(F);
      };
      [].forEach.call(g.children,function(c){
        if(c.hasAttribute('data-figid'))put(c,c.getAttribute('data-figid'));
        else if(c.classList.contains('a3d-acc-col'))[].forEach.call(c.querySelectorAll('[data-figid]'),function(d){put(d,d.getAttribute('data-figid'));});
        else if(c.classList.contains('a3d-acc-sec'))put(c,'text',{t:c.textContent});
      });
    }finally{if(m.parentNode)m.parentNode.removeChild(m);}
    return out;
  }
  /* a figure's own height at a width (columns), in the board's steps */
  function bimBrdNatH(F,w){
    var ctx={edit:false,narrow:false,caps:{},no:0},m=bimBrdMeasurer(Math.max(40,w*BIM_BRD_P0-BIM_BRD_G)),h=1,o=F.o||{},c;
    try{
      m.innerHTML='<div class="a3d-clb-fig a3d-clb-nat'+(o.show?' o-'+o.show:'')+(F.f==='text'?' t':'')+'">'+bimFigCardHtml(F,F.f==='text'?null:bimFigSrc(ctx,F.f,o),1)+'</div>';
      c=m.firstChild;
      h=(c.getBoundingClientRect().height+BIM_BRD_G)/BIM_BRD_P0;
    }finally{if(m.parentNode)m.parentNode.removeChild(m);}
    return Math.max(0.25,Math.ceil(h*1000)/1000);
  }
