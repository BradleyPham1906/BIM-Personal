  /* ================= __acad3dV83: the rail's utility stack =================

     The foot of the left rail was a single 24px "A?" button under 900px of empty column. The
     reference tool stacks its view and document utilities there, and that is the right place for
     them: always reachable, never in the drawing.

     Inserted by the shell's render pass, which the panel's MutationObserver re-runs, so the stack
     is present across a re-render. */
  var A3D_RAIL_ICONS={
    zoom:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">'+
      '<circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5 L21 21"/><path d="M7.5 10.5h6"/></svg>',
    appear:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">'+
      '<circle cx="12" cy="12" r="8"/><path d="M12 4a8 8 0 0 0 0 16z" fill="currentColor" stroke="none"/></svg>',
    snaps:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">'+
      '<path d="M4 9h16M4 15h16M9 4v16M15 4v16"/></svg>',
    units:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">'+
      '<path d="M3 14h18v5H3z"/><path d="M7 14v-3M11 14v-4M15 14v-3M19 14v-4"/></svg>',
    capture:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">'+
      '<path d="M4 8h3l1.5-2h7L17 8h3v11H4z"/><circle cx="12" cy="13" r="3.2"/></svg>',
    /* __acad3dV85: a keyboard, because that is what this one opens. The button it replaces
       said "A?" and did nothing at all. */
    help:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">'+
      '<rect x="2.5" y="6.5" width="19" height="11" rx="2"/>'+
      '<path d="M6 10h.01M9 10h.01M12 10h.01M15 10h.01M18 10h.01M8 13.5h8"/></svg>'
  };
  var A3D_RAIL_UTILS=[
    {id:'zoom',   label:'Zoom',       menu:true },
    {id:'appear', label:'Appearance', menu:true },
    {id:'snaps',  label:'Snaps',      menu:true },
    {id:'units',  label:'Units',      menu:true },
    {id:'capture',label:'Save image', menu:false},
    {id:'help',   label:'Keyboard shortcuts', menu:true}
  ];

