  // ---- __acad3dV28: Revit-style Project Browser. The previous sidebar crammed 7 tabs into a
  // 210px strip -- labels clipped, later tabs unreachable, and no way to lock/unlock from the
  // tree at all. Revit doesn't use tabs here: it has a Properties palette above a hierarchical,
  // collapsible Project Browser. This replaces the tab strip with that structure. Collapsing is
  // what actually solves the crowding -- categories fold away instead of competing for width.
  var A3D_BROWSER_OPEN={views:true,floorplans:true,view3d:true,views2d:true,elevations:true,sections:true,
    schedules:false,families:false,sheets:false,classifications:false};
  function bimBrowserToggle(key){
    A3D_BROWSER_OPEN[key]=!A3D_BROWSER_OPEN[key];
    refreshBrowser();
  }
  function bimBrowserGroup(key,label,count,depth){
    var open=!!A3D_BROWSER_OPEN[key];
    return '<div class="a3d-bgrp" data-a3dbgrp="'+key+'" style="padding-left:'+(6+depth*12)+'px">'+
      '<span class="a3d-bcar">'+(open?'\u25be':'\u25b8')+'</span>'+
      '<span class="a3d-blabel">'+label+'</span>'+
      (count!==null?'<span class="a3d-bcount">'+count+'</span>':'')+
      '</div>';
  }
  function bimBrowserLeaf(label,attrs,depth,extra){
    /* __acad3dV121: the browser's search filters every leaf; it filtered only the Model group, which
       moved to the Layers panel */
    if(A3D.browserFilter&&String(label).toLowerCase().indexOf(A3D.browserFilter)<0)return '';
    return '<div class="a3d-bleaf'+(attrs.sel?' sel':'')+'" '+(attrs.data||'')+
      ' style="padding-left:'+(6+depth*12)+'px" title="'+bimEsc(attrs.title||label)+'">'+
      '<span class="a3d-bico">'+(attrs.ico||'')+'</span>'+
      '<span class="a3d-bname">'+bimEsc(label)+'</span>'+
      (extra||'')+'</div>';
  }
