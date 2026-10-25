  /* ================= __acad3dV80: the left shell belongs to the BIM app ================= */
  /* Every control that IS live in the left shell, each with the reason it is live. bimShellAudit
     reports anything visible and clickable that matches none of these.

     A whitelist, deliberately. A blacklist of known-dead classes only ever knows about the
     leftovers someone has already found -- which is exactly how six of them accumulated. */
  var A3D_SHELL_CLAIMS=[
    {sel:'.a3d-paneltoggle',why:'collapses the rail'},
    {sel:'.a3d-panelcollapse',why:'collapses the rail'},
    {sel:'[data-lpwidth]',why:'widens the panel a step at a time: its edge, by one press'},   /* __acad3dV166b */
    {sel:'#a3d-lgrip',why:'the left panel\'s edge: dragged to size it, or moved from the keyboard'},   /* __acad3dV166d: driven by the V166b suite */
    {sel:'.a3d-rgrip',why:'Properties\' edge: dragged to size it, or moved from the keyboard'},   /* __acad3dV166d */
    {sel:'[data-rpwidth]',why:'widens Properties a step at a time: its edge, by one press'},
    {sel:'#a3d-rminbtn',why:'minimises Properties to a strip; on a phone or a tablet, closes its sheet or drawer'},   /* __acad3dV147, driven by its suite */
    {sel:'.a3d-rsheetbar',why:'on a phone, raises or lowers the Properties sheet'},
    {sel:'[data-railmore]',why:'on a phone, shows the rail\'s tools over the tab bar'},   /* __acad3dV149 */
    {sel:'[data-tpact]',why:'the palette: a tool, Select, Pan or every tool'},   /* __acad3dV150 */
    {sel:'[data-tpgrip]',why:'the palette\'s grip: drag to move it'},
    {sel:'[data-tptoggle]',why:'folds the palette to one button'},
    {sel:'[data-tpcur]',why:'the folded palette: tap to open it, drag to move it'},
    {sel:'.a3d-railbtn[data-tab="layers"]',why:'Layers tab: the layer tree and the objects on each layer'},   /* __acad3dV121 */
    {sel:'[data-lyact]',why:'Layers panel action: new layer, sub-layer, standard layer, make current, delete'},
    {sel:'[data-lytog]',why:'opens or closes a layer in the Layers panel'},
    {sel:'[data-lycur]',why:'makes a layer current'},
    {sel:'[data-lyon]',why:'turns a layer on or off'},
    {sel:'[data-lyfrz]',why:'freezes or thaws a layer'},
    {sel:'[data-lylock]',why:'locks or unlocks a layer'},
    {sel:'[data-lypin]',why:'pins or unpins an object in the Layers panel'},
    {sel:'.a3d-railbtn[data-tab="browser"]',why:'Project Browser tab'},
    /* __acad3dV122: the Presentation panel -- each driven by the V122 suite before it was claimed */
    {sel:'.a3d-railbtn[data-tab="presentation"]',why:'Presentation tab: the pages in order, to read, reorder, present and print'},
    {sel:'[data-prpact]',why:'Presentation panel action: present, a new page, print the set'},
    {sel:'[data-prpitem]',why:'a page: click to read it, double-click to edit its layout, drag to move it, right-click for its menu'},
    {sel:'[data-prpren]',why:'the name of a page being renamed'},
    {sel:'.a3d-railbtn[data-tab="assets"]',why:'Assets tab: the library of models, blocks and templates, dragged into the project'},
    /* __acad3dV124: the library's controls -- each driven by the V124 suite before it was claimed */
    {sel:'[data-a3dasact]',why:'library action: import a model, save the selection as a block or a model, save the project as a template'},
    {sel:'[data-a3dasdel]',why:'removes a model, block or template the user added to the library, after asking'},
    /* __acad3dV141: the Analyze tab -- each driven by the V141 suite before it was claimed */
    {sel:'.a3d-railbtn[data-tab="analyze"]',why:'Analyze tab: every analysis, what it shows now, run it or open its settings'},
    {sel:'[data-anzview]',why:'Analyze: the switch between the analyses and the site analysis'},   /* __acad3dV159 */
    {sel:'[data-satog]',why:'Site analysis: a category opens and closes'},
    {sel:'[data-saact]',why:'Site analysis: Analyze site, the legend, a category\'s data and boards, the property line'},   /* __acad3dV164 */
    {sel:'[data-saaddr]',why:'Site analysis: the site\'s address, found when Analyze site runs'},
    {sel:'[data-dgf]',why:'a site analysis element: its colour, line, opacity and labels'},
    {sel:'[data-dgact]',why:'a site analysis element: reset it to the analysis, or run the analysis again'},
    {sel:'[data-anzact]',why:'an analysis: run it, show or hide it, or open its settings in Properties'},
    {sel:'[data-anztog]',why:'an analysis row: opens and closes it, to its whole status, legend and other actions'},   /* __acad3dV148 */
    {sel:'[data-lysectog]',why:'opens or closes the Analysis or Data section of the Layers panel'},
    {sel:'[data-lyreson]',why:'shows or hides a result layer or a data layer'},
    {sel:'[data-lyresupd]',why:'runs a result layer again, on its own date and surface'},
    {sel:'[data-lyresrn]',why:'renames a result layer or a data layer'},
    {sel:'[data-lyresdel]',why:'removes a result layer or a data layer'},
    {sel:'[data-lyresset]',why:'opens a data layer\'s settings in Properties'},
    /* __acad3dV83: every control in the rail's utility stack, claimed. That is the point of
       this whitelist -- a control added without being claimed fails the audit, which is exactly
       what should happen to a control added without being wired. */
    {sel:'[data-a3drumenu]',why:'rail utility menu (zoom / appearance / snaps / units)'},
    {sel:'[data-a3druact]',why:'rail utility action (save image)'},
    {sel:'.a3d-palbtn',why:'Project Browser palette action'},
    {sel:'.a3d-lvldel',why:'deletes a level/layer/building row'},
    /* __acad3dV84: claimed, not removed -- both are wired and were driven with a real pointer
       before being claimed. They went unseen until now because no suite had ever had a saved
       view AND a sheet in existence at the moment the audit ran. */
    {sel:'.a3d-bdel',why:'deletes a saved view or a sheet from the Project Browser'},
    {sel:'.a3d-row',why:'selects an object'},
    {sel:'.a3d-brow',why:'Project Browser row'},
    {sel:'.a3d-bgrp',why:'Project Browser group header'},
    {sel:'[data-a3dassets]',why:'a library item: click to place or apply it, or drag it onto the drawing'},
    {sel:'[data-a3dassetgrp]',why:'a library group header: folds and unfolds the group'},
    {sel:'input',why:'a field, not an action'},
    {sel:'select',why:'a field, not an action'}
  ];
  function bimShellAudit(){
    var shell=document.getElementById('a3d-shell');
    if(!shell)return {ok:false,reason:'no shell',unclaimed:[]};
    /* __acad3dV166d: an edge that takes the focus is a control too; and Properties' own chrome -- its
       header, its edge, the phone's grab bar -- sits outside the shell. Its body (the fields of what is
       selected) is not the shell's. */
    var Q='button,[role="button"],[role="separator"][tabindex],a[href],input,select',rpA=document.getElementById('a3d-right');
    var nodes=[].slice.call(shell.querySelectorAll(Q));
    if(rpA)[].forEach.call(rpA.querySelectorAll(Q),function(e){if(!e.closest('#a3d-propsbody'))nodes.push(e);});
    var unclaimed=[],claimed=0,i,j;
    for(i=0;i<nodes.length;i++){
      var e=nodes[i];
      var st=window.getComputedStyle(e);
      if(st.display==='none'||st.visibility==='hidden')continue;
      var r=e.getBoundingClientRect();
      if(r.width<2||r.height<2)continue;        // laid out but not actually on screen
      var hit=null;
      for(j=0;j<A3D_SHELL_CLAIMS.length;j++){
        try{if(e.matches(A3D_SHELL_CLAIMS[j].sel)||e.closest(A3D_SHELL_CLAIMS[j].sel)){
          hit=A3D_SHELL_CLAIMS[j];break;
        }}catch(eM){}
      }
      if(hit){claimed++;continue;}
      unclaimed.push({tag:e.tagName,cls:String(e.className||'').slice(0,60),
        data:Object.keys(e.dataset||{}).map(function(k){return k+'='+e.dataset[k];}).join(','),
        text:(e.textContent||'').trim().slice(0,32)});
    }
    return {ok:unclaimed.length===0,claimed:claimed,unclaimed:unclaimed};
  }

