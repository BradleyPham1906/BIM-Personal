  /* ================= __acad3dV142: the user guide, and versions =================
     The guide is in docs/ beside the app, on the same site (and in the repository, so it opens
     offline). Its command reference has a section per command, anchored by the command's id. */
  var BIM_APP_VERSION={v:'V172',date:'2026-11-01'};   /* __acad3dV162; __acad3dV163; __acad3dV164; __acad3dV165; __acad3dV166; __acad3dV167; __acad3dV168; __acad3dV170; __acad3dV171; __acad3dV172; __acad3dV172b; __acad3dV172c */
  var BIM_DOCS_BASE='docs/';
  /* a command's anchor in the reference: cmd:LINE -> cmd-LINE, act:bim:wall -> act-bim-wall */
  function bimDocsAnchor(id){return String(id||'').replace(/[^A-Za-z0-9_-]+/g,'-');}
  function bimDocsUrl(page,anchor){return BIM_DOCS_BASE+page+(anchor?'#'+anchor:'');}
  var A3D_GUIDE={opened:[]};
  function bimDocsOpen(page,anchor){
    var u=bimDocsUrl(page,anchor),w=null;
    A3D_GUIDE.opened.push(u);
    try{w=window.open(u,'_blank','noopener');}catch(eW){w=null;}
    a3dToast('Opening the user guide: '+u+(w?'':' (allow pop-ups for this page if nothing opened)'));
    return u;
  }
  function bimVersionHtml(){
    return '<a class="a3d-ctxlink" href="'+bimEsc(bimDocsUrl('changelog.html',BIM_APP_VERSION.v.toLowerCase()))+'" target="_blank" rel="noopener" data-docslink="notes">'+
      bimEsc(BIM_APP_VERSION.v)+', '+bimEsc(BIM_APP_VERSION.date)+'</a> \u00b7 '+
      '<a class="a3d-ctxlink" href="'+bimEsc(bimDocsUrl('index.html'))+'" target="_blank" rel="noopener" data-docslink="guide">User Guide</a>';
  }
