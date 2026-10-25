  /* ================= __acad3dV86: AutoCAD-shaped drawing input =================

     LINE emits ONE OBJECT PER SEGMENT. That is the whole difference between LINE and PLINE in
     AutoCAD -- N points produce N-1 independent entities, which is why a finished LINE run has
     no Close option and selecting one segment selects only that segment. PLINE produces a
     single object. Copying the prompts without copying this would be copying the costume. */
  function finishLine(close){
    var sk=A3D.sk;
    if(!sk||sk.pts.length<2){A3D.sk=null;paint();return null;}
    var pts=sk.pts.slice(),y=sk.y,on=sk.on||null,made=[],i,o;
    if(close&&pts.length>=3)pts.push([pts[0][0],pts[0][1]]);
    pushUndo();   /* __acad3dV100: ONE snapshot for the whole run, not one per segment */
    /* addSketchObj reads A3D.sk for the datum plane and host face and then clears it, so the
       sketch is rebuilt for each segment rather than the loop reaching around it. */
    for(i=0;i<pts.length-1;i++){
      A3D.sk={tool:'line',pts:[],y:y,on:on};
      o=addSketchObj([[pts[i][0],pts[i][1]],[pts[i+1][0],pts[i+1][1]]],{noUndo:true});
      if(o)made.push(o.id);
    }
    A3D.sk=null;
    paint();saveSoon();
    return made;
  }

  /* Tools that take typed coordinates. Everything here accumulates points on the ground plane,
     which is what the parser below produces. */
  /* __acad3dV93: circle was missing. skPlacePoint has handled a typed circle radius since
     V87, but this gate is upstream of it, so the buffer never opened and the keystrokes fell
     through to the viewport. polygon joins on the same terms. */
  var BIM_COORD_TOOLS={line:1,poly:1,wall:1,rect:1,stair:1,arc:1,circle:1,polygon:1,point:1,xline:1,boundary:1,hatch:1};

  /* AutoCAD coordinate entry. Exactly the five forms Autodesk documents:

         3,4     absolute Cartesian        @3,4    relative Cartesian
         3<45    absolute polar            @1<45   relative polar
         #3,4    forces absolute           7       direct distance entry along the rubber band

     Angles increase counter-clockwise from +X. MEASURED on this app's plan camera: world +X
     projects screen-right and world +Z projects screen-DOWN, so screen-up is -Z and an AutoCAD
     angle maps to dx = cos(t), dz = -sin(t). That sign was measured with __a3dProject, not
     reasoned about.

     Returns a [x,z] ground point, or null when the string is not a coordinate -- the caller
     reports that rather than silently placing a point somewhere wrong.

     __acad3dV123: lengths are typed in the project's unit, as AutoCAD reads them in drawing
     units. They were read as metres, so in a millimetre project 3000 drew a wall three kilometres
     long. An angle stays in degrees. */
  function bimParseCoordInput(s,sk){
    if(!sk)return null;
    s=String(s||'').trim();
    if(!s)return null;
    var rel=false,sc=bimUnitDef().scale;
    if(s.charAt(0)==='@'){rel=true;s=s.slice(1);}
    else if(s.charAt(0)==='#'){s=s.slice(1);}
    var last=sk.pts.length?sk.pts[sk.pts.length-1]:null;
    var i,a,b;
    if(s.indexOf('<')>=0){
      i=s.indexOf('<');
      a=parseFloat(s.slice(0,i));b=parseFloat(s.slice(i+1));
      if(!isFinite(a)||!isFinite(b))return null;
      var t=b*Math.PI/180,vx=Math.cos(t)*a/sc,vz=-Math.sin(t)*a/sc;
      if(rel){if(!last)return null;return [last[0]+vx,last[1]+vz];}
      return [vx,vz];
    }
    if(s.indexOf(',')>=0){
      i=s.indexOf(',');
      a=parseFloat(s.slice(0,i));b=parseFloat(s.slice(i+1));
      if(!isFinite(a)||!isFinite(b))return null;
      a/=sc;b/=sc;
      if(rel){if(!last)return null;return [last[0]+a,last[1]+b];}
      return [a,b];
    }
    /* Direct distance entry: a bare number travels along the direction the rubber band is
       already pointing. This is the ortho workflow -- push the cursor the way you want to go,
       type the number, press Enter. */
    var d=parseFloat(s)/sc;
    if(!isFinite(d)||d<=0||!last)return null;
    var dir=sk.liveDir||[1,0];
    return [last[0]+dir[0]*d,last[1]+dir[1]*d];
  }

  function bimCanClose(sk){
    if(!sk||!sk.pts)return false;
    /* The thresholds differ, and both come from AutoCAD. Autodesk on LINE: "You can use Close
       after you have drawn a series of two or more segments" -- so 3 points. PLINE's own
       transcripts offer Close after ONE segment -- so 2 points. */
    if(sk.tool==='line')return sk.pts.length>=3;
    if(sk.tool==='poly')return sk.pts.length>=3;
    if(sk.tool==='wall')return sk.pts.length>=3;
    return false;
  }
  function bimCloseCurrent(){
    var sk=A3D.sk;if(!bimCanClose(sk))return false;
    if(sk.tool==='line')finishLine(true);
    else if(sk.tool==='wall')finishWall(true);
    else finishPoly();
    bimSyncStatusHint();
    return true;
  }
  function bimFinishCurrent(){
    var sk=A3D.sk;if(!sk)return false;
    if(sk.tool==='line'){if(sk.pts.length>=2)finishLine(false);else{A3D.sk=null;paint();}}
    else if(sk.tool==='wall'){if(sk.pts.length>=2)finishWall(false);else{A3D.sk=null;paint();}}
    else if(sk.tool==='poly'){if(sk.pts.length>=2)finishPoly(true);else{A3D.sk=null;paint();}}   /* __acad3dV100: Enter ends it OPEN */
    else if(sk.tool==='stair'){if(sk.pts.length>=2)finishStair();else{A3D.sk=null;paint();}}
    else{A3D.sk=null;paint();}
    bimSyncStatusHint();
    return true;
  }
  function bimUndoLastPoint(){
    var sk=A3D.sk;
    if(!sk||!sk.pts||!sk.pts.length)return false;
    sk.pts.pop();
    /* __acad3dV90: the segment that point closed goes with it, or the arrays drift apart. */
    if(sk.bulges&&sk.bulges.length>Math.max(0,sk.pts.length-1))sk.bulges.length=Math.max(0,sk.pts.length-1);
    bimSyncStatusHint();paint();
    return true;
  }
  /* A typed coordinate is a POINT, so it goes through the same placement path a click would --
     including the auto-finish rules for the two-point tools. */
  function bimCommitTypedPoint(str){
    var sk=A3D.sk;if(!sk)return false;
    /* __acad3dV94: in Angle mode the first thing typed is an ANGLE, not a coordinate. Parsing
       it as a coordinate would take '30' as a direct distance entry along a rubber band that
       does not exist yet. */
    if(sk.tool==='xline'&&sk.mode==='ang'&&typeof sk.angle!=='number'){
      var av=parseFloat(str);
      if(!isFinite(av)){a3dToast('Enter the angle in degrees, then Enter');paint();return false;}
      sk.angle=av;
      bimSyncStatusHint();paint();
      a3dToast('Construction lines at '+av+' degrees: click to place them');
      return true;
    }
    var p=bimParseCoordInput(str,sk);
    if(!p){a3dToast('Not a coordinate: try 3,4 or @3,4 or @5<45, or a length');paint();return false;}
    skPlacePoint(p[0],p[1],null);   /* __acad3dV87: the same handler a click reaches */
    bimSyncStatusHint();paint();saveSoon();
    return true;
  }

  /* The prompt strings AutoCAD prints, for the tools that behave like AutoCAD's.

     DELIBERATE DEPARTURE: AutoCAD's PLINE prompt reads
         Specify next point or [Arc/Halfwidth/Length/Undo/Width]:
     and this app implements none of Arc, Halfwidth, Length or Width. Printing them would offer
     four options that do nothing -- the same fault as the dead palette this phase is fixing --
     so the bracket list holds only what works. */
  /* The bracket list is DERIVED from the predicates the keys themselves consult, so a prompt
     can never advertise an option the command would refuse. The first version of this function
     hard-coded the thresholds and immediately drifted: it offered [Close/Undo] at two points
     while bimCanClose required three, so C did nothing at the exact moment the prompt said it
     would.

     bimCanClose is three points for both LINE and PLINE. AutoCAD offers PLINE's Close after one
     segment, but finishPoly builds a closed sketch profile and a two-point closed polyline is a
     line doubled back on itself -- a degenerate profile Floor, Room and Roof cannot use. The
     threshold is this app's, and the prompt states this app's. */
  /* __acad3dV90: which tools take arc segments, and when.

     WALL and PLINE do; LINE does not, exactly as in AutoCAD. An arc needs a direction to leave
     along, so it needs a finished segment to continue from: arc mode is offered only once two
     points are down. That is a real precondition, and it is the same predicate the A key
     consults, so the prompt can never offer a mode the key refuses. */
  function bimCanArc(sk){
    if(!sk||!sk.pts)return false;
    if(sk.tool!=='wall'&&sk.tool!=='poly')return false;
    return sk.pts.length>=2;
  }
  function bimSetArcMode(sk,on){
    if(!sk)return false;
    if(on&&!bimCanArc(sk))return false;
    sk.arcMode=!!on;
    bimSyncStatusHint();paint();
    return true;
  }
  /* The direction the run is travelling at its last point, which is what a tangent arc
     continues. Derived from the segment that is actually there, arc or straight. */
  function bimSkHeading(sk){
    if(!sk||!sk.pts||sk.pts.length<2)return null;
    var i=sk.pts.length-1;
    return bimSegEndDir(sk.pts[i-1],sk.pts[i],bimBulgeAt(sk.bulges,i-1));
  }
  /* __acad3dV94: the letters a point-taking tool claims, in the order they are tried. Each
     entry's test is the SAME predicate the prompt's bracket list is built from, so a key and
     the prompt that advertises it cannot drift apart. */
  var BIM_SKETCH_KEYS=[
    {name:'clineMode',
     test:function(sk,ev){
       return sk.tool==='xline'&&bimClineCanSetMode(sk)&&!!bimClineModeForKey(ev.key);},
     run:function(sk,ev){bimSetClineMode(sk,bimClineModeForKey(ev.key));}},
    {name:'undo',
     test:function(sk,ev){return (ev.key==='u'||ev.key==='U')&&!!(sk.pts&&sk.pts.length);},
     run:function(){bimUndoLastPoint();}},
    /* __acad3dV90: A switches to arc segments, L back to straight - PLINE's own keys. */
    {name:'arcOn',
     test:function(sk,ev){return (ev.key==='a'||ev.key==='A')&&bimCanArc(sk)&&!sk.arcMode;},
     run:function(sk){bimSetArcMode(sk,true);}},
    {name:'arcOff',
     test:function(sk,ev){return (ev.key==='l'||ev.key==='L')&&!!sk.arcMode;},
     run:function(sk){bimSetArcMode(sk,false);}},
    {name:'close',
     test:function(sk,ev){return (ev.key==='c'||ev.key==='C')&&bimCanClose(sk);},
     run:function(){bimCloseCurrent();}}
  ];
  function bimSketchKeyFor(sk,ev){
    if(!sk||!ev||ev.ctrlKey||ev.metaKey)return null;
    if(!BIM_COORD_TOOLS[sk.tool])return null;
    var i;
    for(i=0;i<BIM_SKETCH_KEYS.length;i++)
      if(BIM_SKETCH_KEYS[i].test(sk,ev))return BIM_SKETCH_KEYS[i];
    return null;
  }
  function bimPromptOpts(sk){
    var n=sk.pts?sk.pts.length:0,o=[];
    if(bimCanClose(sk))o.push('Close');
    if(sk&&sk.arcMode)o.push('Line');
    else if(bimCanArc(sk))o.push('Arc');
    if(n)o.push('Undo');
    return o.length?(' or ['+o.join('/')+']'):'';
  }
  function bimPromptFor(sk){
    var n=sk.pts?sk.pts.length:0;
    if(sk.tool==='line')return n?('Specify next point'+bimPromptOpts(sk)+':'):'Specify first point:';
    if(sk.tool==='poly')return n?('Specify next point'+bimPromptOpts(sk)+':'):'Specify start point:';
    if(sk.tool==='rect')return n?'Specify other corner point:':'Specify first corner point:';
    if(sk.tool==='circle')return n?'Specify radius:':'Specify center point:';
    /* __acad3dV93: the form is already chosen, so the prompt states it rather than offering
       [Inscribed/Circumscribed] at a point where no key would answer it. */
    if(sk.tool==='roomtag')return 'Select a room to tag (Escape when finished):';   /* __acad3dV101 */
    if(sk.tool==='footing')return 'Select a column to put a footing under (Escape when finished):';   /* __acad3dV102 */
    if(sk.tool==='wallfoundation')return 'Select a wall to put a foundation under (Escape when finished):';
    if(sk.tool==='foundslab')return 'Pick a point inside the slab boundary:';
    if(sk.tool==='hatch')return 'Pick an internal point to hatch (Escape when finished):'; /* __acad3dV96 */
    if(sk.tool==='boundary')return 'Pick an internal point (Escape when finished):';  /* __acad3dV95 */
    if(sk.tool==='point')return 'Specify a point (Escape when finished):';   /* __acad3dV93 */
    /* __acad3dV94: the bracket list comes from the same table the keys consult, so it can
       never offer a mode that does nothing. */
    if(sk.tool==='xline'){
      var clWhat=sk.ray?'ray':'xline';
      if(bimClineCanSetMode(sk))
        return 'Specify a point or ['+bimClineModeLabels().join('/')+']:';
      if(sk.mode==='ang'&&typeof sk.angle!=='number')
        return 'Enter angle of '+clWhat+' in degrees:';
      if(bimClineReadyDir(sk))return 'Specify through point:';
      return sk.pts.length?'Specify through point:':'Specify a point:';
    }
    if(sk.tool==='polygon')return n?('Specify radius of circle ('+
      (sk.circumscribed?'circumscribed':'inscribed')+'):'):'Specify center of polygon:';
    /* __acad3dV88: three prompts for three points, and no bracket list - this build implements
       only the 3-point form, so offering [Center/End] would advertise what it refuses. */
    if(sk.tool==='arc')return n===0?'Specify start point of arc:'
      :(n===1?'Specify second point on arc:':'Specify end point of arc:');
    if(sk.tool==='wall')return n?('Wall \u00b7 Specify next point'+bimPromptOpts(sk)+':')
                                :'Wall \u00b7 Specify start point:';
    /* __acad3dV87: the modify tools take a PICK, not a length, so they do not print the
       typed-length hint the drawing tools print. Each states what its next click does. */
    if(sk.tool==='extend')return 'Extend \u00b7 select the wall end to extend:';
    if(sk.tool==='break')return sk.breakAtPoint?'Break at point \u00b7 specify the split point:'
      :(n?'Break \u00b7 specify second break point:':'Break \u00b7 specify first break point:');
    if(sk.tool==='lengthen')return 'Lengthen \u00b7 select the end to change:';
    if(sk.tool==='scale')return 'Scale \u00b7 specify base point:';
    var msg=(SK_TOOLS[sk.tool]||sk.tool);
    return msg+(n?'  ·  click the next point, or type a length + Enter':'  ·  click to start');
  }

  /* Enter at the Command prompt repeats the previous command -- Autodesk: "You can also repeat
     the previous command by pressing Enter or the spacebar." Recorded wherever a command is
     started, so the palette and the ribbon both feed it. */
  function bimRecordCmd(fn,label){A3D.lastCmd={run:fn,label:label||''};}
  function bimRepeatLastCommand(){
    var c=A3D.lastCmd;
    if(!c||typeof c.run!=='function')return false;
    try{c.run();}
    catch(eR){console.warn('[BIM] Could not repeat the last command.',eR);a3dToast('Could not repeat that command');return false;}
    return true;
  }
  function skClick(xy){
    var sk=A3D.sk;if(!sk)return;
    var g=groundPoint(xy[0],xy[1],sk.y);if(!g)return;
    var snapped=bimSnapPoint(xy,g,sk);
    skPlacePoint(snapped[0],snapped[1],xy);
  }
  /* __acad3dV87: ONE point handler, reached by a click and by a typed coordinate alike.

     It used to be reachable only by a click. bimCommitTypedPoint pushed the parsed point onto
     sk.pts and stopped there, with two special cases bolted on for RECTANG and CIRCLE, so every
     tool that ACTS on its points rather than collecting them -- MIRROR, ROTATE, POLAR ARRAY,
     TRIM, DIM -- accepted a typed coordinate, showed it landing, and did nothing. The command
     line said the coordinate was taken and the model disagreed: the V86 fault in a second
     place, which is why this is fixed as a class rather than per tool.

     xy is the SCREEN point and is optional. It exists for one thing: the click-near-the-start
     close test at the bottom, which has no meaning for a typed coordinate. Absent, that test is
     skipped and everything else behaves identically. */
  function skPlacePoint(gx,gz,xy){
    var sk=A3D.sk;if(!sk)return;
    if(sk.tool==='hatch'){                      /* __acad3dV96 */
      bimApplyHatchAt([gx,gz],sk.y,sk.hatch);
      return;                                   /* sk stays live: HATCH keeps filling */
    }
    if(sk.tool==='boundary'){                   /* __acad3dV95 */
      bimApplyBoundary([gx,gz],sk.y);
      return;                                   /* sk stays live: BOUNDARY keeps picking */
    }
    if(sk.tool==='xline'){                      /* __acad3dV94 */
      var clDir=bimClineReadyDir(sk);
      if(clDir){
        /* Horizontal, vertical and angle all know their direction already, so every click is
           one finished construction line and the tool stays live for the next. */
        bimPlaceCline(sk,[gx,gz],clDir);
        return;
      }
      if(!sk.pts.length){
        sk.pts.push([gx,gz]);
        bimSyncStatusHint();paint();
        return;
      }
      clDir=bimClineDir(null,sk.pts[0],[gx,gz]);
      if(!clDir){a3dToast('Pick a point away from the first one');return;}
      /* The ROOT is kept, which is what lets a drafter fan several construction lines out of
         one point without restarting the command -- AutoCAD's own behaviour. */
      bimPlaceCline(sk,[sk.pts[0][0],sk.pts[0][1]],clDir);
      return;
    }
    if(sk.tool==='point'){                      /* __acad3dV93 */
      pushUndo();
      var np=bimAddPoint(gx,gz,sk.y);
      A3D.sel=np.id;A3D.sel2=null;
      refreshTree();refreshHud();paint();saveSoon();
      a3dToast(np.name+' placed at '+gx.toFixed(3)+', '+gz.toFixed(3));
      return;                                   /* sk stays live: POINT keeps placing */
    }
    if(sk.tool==='rect'||sk.tool==='circle'||sk.tool==='polygon'){
      sk.pts.push([gx,gz]);
      if(sk.pts.length>=2){
        if(sk.tool==='rect')finishRect();
        else if(sk.tool==='polygon')finishPolygon();   /* __acad3dV93 */
        else finishCircle();
      }
    }else if(sk.tool==='grid'){
      sk.pts.push([gx,gz]);
      if(sk.pts.length>=2){A3D.sk=null;bimAddGrid(sk.pts[0],sk.pts[1]);}
    }else if(sk.tool==='beam'){
      sk.pts.push([gx,gz]);
      if(sk.pts.length>=2){var bmY=sk.y,bp1=sk.pts[0],bp2=sk.pts[1];A3D.sk=null;openBeamDlg(bp1,bp2,bmY);}
    }else if(sk.tool==='column'){
      var colY=sk.y;
      A3D.sk=null;
      openColumnDlg([gx,gz],colY);
    }else if(sk.tool==='footing'){   /* __acad3dV102: stays live */
      var fc=bimColumnAtWorld([gx,gz]);
      if(!fc)a3dToast('Isolated Footing: click a column');else bimAddFootingUnder(fc);
    }else if(sk.tool==='wallfoundation'){   /* __acad3dV102: stays live */
      var fw=bimWallAtWorld([gx,gz]);
      if(!fw)a3dToast('Wall Foundation: click a wall');else bimAddFootingUnder(fw);
    }else if(sk.tool==='foundslab'){   /* __acad3dV102 */
      var fsy=sk.y;
      A3D.sk=null;
      bimFoundationSlabAt([gx,gz],fsy);
    }else if(sk.tool==='roomtag'){   /* __acad3dV101: stays live for the next room */
      bimTagRoomAt([gx,gz]);
    }else if(sk.tool==='room'){
      var roomY=sk.y;
      var boundary=bimFindRoomBoundaryAt([gx,gz],roomY);
      if(!boundary){a3dToast('Click inside a closed wall loop or closed sketch to create a room');return;}
      A3D.sk=null;
      bimCreateRoom(boundary);
    }else if(sk.tool==='floor'){
      var flB=bimFindRoomBoundaryAt([gx,gz],sk.y);
      if(!flB){a3dToast('Click inside a closed wall loop or closed sketch to place a floor');return;}
      A3D.sk=null;
      openFloorDlg(bimFloorProfileFrom(flB));   /* __acad3dV97, region __acad3dV99 */
    }else if(sk.tool==='trim'){
      var trimCutter=sk.cutterId;
      A3D.sk=null;
      bimApplyTrim(trimCutter,[gx,gz]);
    }else if(sk.tool==='ceiling'){
      var ceilB=bimFindRoomBoundaryAt([gx,gz],sk.y);
      if(!ceilB){a3dToast('Click inside a closed wall loop or closed sketch to place a ceiling');return;}
      A3D.sk=null;
      openCeilingDlg(ceilB);
    }else if(sk.tool==='roof'){
      var roofY=sk.y;
      var roofBoundary=bimFindRoofBoundaryAt([gx,gz],roofY);
      if(!roofBoundary){a3dToast('Click inside a closed wall loop or closed sketch to place a roof');return;}
      A3D.sk=null;
      openRoofDlg(roofBoundary);
    }else if(sk.tool==='stair'){
      // Multi-point path: accumulate only (no auto-finish at 2 points, unlike the legacy tool).
      // Enter finishes the path, mirroring the wall tool; a stair does not support close-to-loop.
      if(sk.pts.length){
        var lastStairPt=sk.pts[sk.pts.length-1];
        if(Math.abs(lastStairPt[0]-gx)<1e-9&&Math.abs(lastStairPt[1]-gz)<1e-9){paint();return;}
      }
      sk.pts.push([gx,gz]);
    }else if(sk.tool==='section'){
      sk.pts.push([gx,gz]);
      if(sk.pts.length>=2){
        var secStart=sk.pts[0],secP2=sk.pts[1];
        var secdx=secP2[0]-secStart[0],secdz=secP2[1]-secStart[1];
        var seclen=Math.sqrt(secdx*secdx+secdz*secdz);
        var secOrigCam=sk.origCam;
        A3D.sk=null;
        if(seclen<1e-6){a3dToast('Second click must set the cut line direction (cannot be the same point)');return;}
        bimEnterSection(secStart,[secdx/seclen,secdz/seclen],secOrigCam);
      }
    }else if((sk.tool==='wall'||sk.tool==='poly')&&sk.arcMode&&sk.pts.length>=1){
      /* __acad3dV90: an arc segment, tangent to the run so far. The bulge belongs to the
         segment being closed - index pts.length-1 - so it is written BEFORE the point is
         pushed, which keeps bulges[i] describing the segment from pts[i] to pts[i+1] exactly
         as it does everywhere else. */
      var segIdx=sk.pts.length-1;
      var heading=bimSkHeading(sk);
      var tb=heading?bimTangentBulge(heading,sk.pts[segIdx],[gx,gz]):null;
      if(tb===null){
        a3dToast('No arc continues from here to that point - pick a point off the current direction');
        paint();return;
      }
      if(!sk.bulges)sk.bulges=[];
      while(sk.bulges.length<segIdx)sk.bulges.push(0);
      sk.bulges[segIdx]=tb;
      sk.pts.push([gx,gz]);
    }else if(sk.tool==='arc'){
      sk.pts.push([gx,gz]);
      if(sk.pts.length>=3)finishArc();
    }else if(sk.tool==='extend'){
      var extBoundId=sk.boundaryId;
      A3D.sk=null;
      bimApplyExtend(extBoundId,[gx,gz]);
    }else if(sk.tool==='break'){
      sk.pts.push([gx,gz]);
      if(sk.breakAtPoint){
        var brOneId=sk.breakId,brOnePt=sk.pts[0];
        A3D.sk=null;
        bimApplyBreak(brOneId,brOnePt,null);
      }else if(sk.pts.length>=2){
        var brTwoId=sk.breakId,brA=sk.pts[0],brB=sk.pts[1];
        A3D.sk=null;
        bimApplyBreak(brTwoId,brA,brB);
      }else{
        a3dToast('Break: click the second point');
      }
    }else if(sk.tool==='lengthen'){
      var lenWallId=sk.lenId;
      A3D.sk=null;
      openLengthenDlg(lenWallId,[gx,gz]);
    }else if(sk.tool==='scale'){
      var scBase=[gx,gz],scIds=sk.scaleIds;
      A3D.sk=null;
      openScaleDlg(scBase,scIds);
    }else if(sk.tool==='mirror'){
      sk.pts.push([gx,gz]);
      if(sk.pts.length>=2){
        var mirIds=sk.mirrorIds,mirP1=sk.pts[0],mirP2=sk.pts[1];
        var mirdx=mirP2[0]-mirP1[0],mirdz=mirP2[1]-mirP1[1];
        A3D.sk=null;
        if(Math.sqrt(mirdx*mirdx+mirdz*mirdz)<1e-6){a3dToast('Second click must set the mirror line direction (cannot be the same point)');return;}
        bimMirrorSelection(mirIds,mirP1,mirP2);
      }
    }else if(sk.tool==='rotate'){
      var rotCenter=[gx,gz],rotIds=sk.rotateIds;
      A3D.sk=null;
      openRotateDlg(rotCenter,rotIds);
    }else if(sk.tool==='polararray'){
      var arrCenter=[gx,gz],arrIds=sk.arrayIds;
      A3D.sk=null;
      openPolarArrayDlg(arrCenter,arrIds);
    }else if(sk.tool==='familyplace'){
      var placeFamId=sk.placeFamId;
      A3D.sk=null;
      var fam=bimFamilyLibraryGet(placeFamId);
      if(!fam){a3dToast('Family not found (it may have been deleted)');return;}
      bimPlaceFamilyInstance(fam,[gx,gz]);
    }else if(sk.tool==='dim'){
      sk.pts.push([gx,gz]);
      if(sk.pts.length>=3){
        var dimP1=sk.pts[0],dimP2=sk.pts[1],dimP3=sk.pts[2];
        A3D.sk=null;
        bimCreateDim(dimP1,dimP2,dimP3);
      }else if(sk.pts.length===2){
        a3dToast('Click a third point to set which side the dimension line sits on');
      }
    }else if(sk.tool==='dimangular'){
      sk.pts.push([gx,gz]);
      if(sk.pts.length>=3){
        var av=sk.pts[0],ar1=sk.pts[1],ar2=sk.pts[2];
        A3D.sk=null;
        bimCreateAngularDim(av,ar1,ar2);
      }
    }else if(sk.tool==='dimradius'||sk.tool==='dimdiameter'){
      var isDia=(sk.tool==='dimdiameter');
      sk.pts.push([gx,gz]);
      if(sk.pts.length>=3){
        var q1=sk.pts[0],q2=sk.pts[1],q3=sk.pts[2];
        A3D.sk=null;
        bimCreateRadialDim(q1,q2,q3,isDia);
      }
    }else if(sk.tool==='leader'){
      sk.pts.push([gx,gz]);
      if(sk.pts.length>=3){
        var la=sk.pts[0],le=sk.pts[1],lt=sk.pts[2];
        A3D.sk=null;
        openLeaderTextDlg(la,le,lt);
      }
    }else if(sk.tool==='profileview'){   /* __acad3dV127 */
      var pvA=objById(sk.alignId);
      A3D.sk=null;
      if(!bimIsAlignment(pvA)){a3dToast('The alignment is gone');return;}
      bimPlaceProfileView(pvA,[gx,gz]);
    }else if(sk.tool==='station'){   /* __acad3dV127: stays live for the next point */
      bimStationAt(sk.alignId,[gx,gz]);
    }else if(sk.tool==='text'){
      var textY=sk.y;
      A3D.sk=null;
      openTextLabelDlg([gx,gz],textY);
    }else if(sk.tool==='door'||sk.tool==='window'){
      var owY=sk.y;
      A3D.sk=null;
      var wallHit=bimFindWallNear([gx,gz],owY);
      if(!wallHit){a3dToast('Click closer to an existing wall to place a '+(sk.tool==='door'?'door':'window'));return;}
      if(sk.tool==='door')openDoorDlg(wallHit,[gx,gz]);else openWindowDlg(wallHit,[gx,gz]);
    }else{
      if(xy&&sk.pts.length>=3){
        var V=camVecs(A3D.cam),p0=toScreen([sk.pts[0][0],sk.y,sk.pts[0][1]],V,cvW(),cvH());
        if(Math.abs(p0[0]-xy[0])<9&&Math.abs(p0[1]-xy[1])<9){
          /* __acad3dV86: LINE closes into SEGMENTS, not into one polygon. Routing it through
             finishPoly would have quietly turned a closed run of lines into a single sketch
             loop -- the exact distinction this phase exists to get right. */
          if(sk.tool==='wall')finishWall(true);
          else if(sk.tool==='line')finishLine(true);
          else finishPoly();
          return;
        }
      }
      sk.pts.push([gx,gz]);
    }
    paint();
  }
  function onHover(ev){
    /* __acad3dV111: the handle under the cursor, highlighted before it is pressed -- every
       reference tool does this, and without it a handle nobody has met is found by trial. The
       answer is compared as a KEY, because the geometry is rebuilt on every paint and no handle
       object survives one; and the repaint happens only when the answer changes, since a repaint
       on every mouse move is a repaint storm. */
    if(!drag){
      var hxy=cvXY(ev);
      var hh=bimPickGizmo(hxy[0],hxy[1]);
      var hk=bimGizmoHoverKey(hh);
      if(hk!==A3D.gizHover){
        A3D.gizHover=hk;
        A3D.gizHoverName=hh?bimGizmoHandleName(hh).replace(/^the /,'').toUpperCase():null;
        A3D.gizHoverHint=hh?bimGizmoHandleHint(hh):null;   /* __acad3dV123 */
        bimSyncStatusHint();
        paint();
      }
    }
    if(!drag&&A3D.face){   /* __acad3dV123: the held face, lit under the cursor */
      var fxy=cvXY(ev),fh=!!bimFaceHitAt(fxy[0],fxy[1]);
      if(fh!==!!A3D.faceHover){A3D.faceHover=fh;paint();}
    }else if(A3D.faceHover)A3D.faceHover=false;
    if(!A3D.sk)return;
    var xy=cvXY(ev);
    var sk=A3D.sk;
    var g=groundPoint(xy[0],xy[1],sk.y);
    if(!g){sk.hover=null;return;}
    var snapped=bimSnapPoint(xy,g,sk);
    sk.hover={x:snapped[0],z:snapped[1],snapped:snapped[2]};
    if(sk.pts.length){
      var last=sk.pts[sk.pts.length-1];
      var ddx=snapped[0]-last[0],ddz=snapped[1]-last[1];
      sk.liveLen=Math.sqrt(ddx*ddx+ddz*ddz);
      sk.liveDir=sk.liveLen>1e-6?[ddx/sk.liveLen,ddz/sk.liveLen]:[1,0];
    }else{
      sk.liveLen=0;sk.liveDir=[1,0];
    }
    paint();
  }
  /* __acad3dV75: off is the object's world offset ([0,0,0] for the in-progress sketch, whose
     points are already world). Passing it in rather than pre-transforming the array keeps the
     stored geometry local, which is what every rebuild, constraint solve and export reads. */
  /* __acad3dV93: bulges is the arc data, and the PATH is built from the flattened curve while
     the GRIPS stay on the stored vertices. Before this the viewport drew o.pts raw, so a
     committed arc appeared as its chord while the rubber band that produced it appeared
     curved. Same flattener as every other consumer -- bimFlattenPoly -- so the viewport cannot
     drift from the DXF, the SVG or the sheet. */
  function drawSketchPath(ctx,V,W,H,pts,y0,col,closed,prog,off,bulges,look){   /* __acad3dV121: look, By Layer */
    if(!pts||pts.length<1)return;
    var i,p,sp=[],gp=[],q=off||[0,0,0],y=(y0||0)+q[1];
    var path=bimHasBulge(bulges)?bimFlattenPoly(pts,bulges,!!closed):pts;
    for(i=0;i<path.length;i++){
      p=toScreen([path[i][0]+q[0],y,path[i][1]+q[2]],V,W,H);sp.push(p);
    }
    for(i=0;i<pts.length;i++){
      p=toScreen([pts[i][0]+q[0],y,pts[i][1]+q[2]],V,W,H);gp.push(p);
    }
    ctx.save();
    if(look&&look.alpha<1)ctx.globalAlpha*=look.alpha;
    ctx.beginPath();
    ctx.moveTo(sp[0][0],sp[0][1]);
    for(i=1;i<sp.length;i++)ctx.lineTo(sp[i][0],sp[i][1]);
    if(closed){
      ctx.closePath();
      ctx.fillStyle=bimHexA(look?look.color:'#5ec4b8',0.10);
      ctx.fill();
    }
    if(prog)ctx.setLineDash([5,4]);
    else if(look&&look.dash.length)ctx.setLineDash(look.dash);
    ctx.strokeStyle=col;
    ctx.lineWidth=look?look.width:1.6;
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle=col;
    for(i=0;i<gp.length;i++)ctx.fillRect(gp[i][0]-2.5,gp[i][1]-2.5,5,5);
    ctx.restore();
  }
  /* __acad3dV96: hatch, drawn under the linework. This is the one pattern sink that is NOT
     gated on presentation mode, because a hatch is geometry the drafter placed rather than an
     appearance the mode chose. */
  function drawHatches(ctx,V,W,H){
    var i,o,ring,sp,k,rg,fill;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(!bimIsHatch(o))continue;
      if(!bimLayerShown(o))continue;   /* __acad3dV121 */
      if(!bimObjectVisibleOnLevel(o))continue;
      ring=bimHatchOutline(o);
      if(ring.length<3)continue;
      var q=bimObjOffset(o);
      sp=[];
      for(k=0;k<ring.length;k++)
        sp.push(toScreen([ring[k][0]+q[0],(o.y||0)+q[1],ring[k][1]+q[2]],V,W,H));
      ctx.save();
      ctx.beginPath();
      ctx.moveTo(sp[0][0],sp[0][1]);
      for(k=1;k<sp.length;k++)ctx.lineTo(sp[k][0],sp[k][1]);
      ctx.closePath();
      ctx.globalAlpha*=bimLayerAlpha(o);   /* __acad3dV121: the layer's transparency */
      rg=bimHatchGraphics(o);
      if(rg.fill&&rg.fill!=='none'){ctx.fillStyle=rg.fill;ctx.fill();}
      fill=bimCanvasPatternFill(ctx,rg);
      if(fill){ctx.fillStyle=fill;ctx.fill();}
      /* The boundary is drawn only while selected. AutoCAD's hatch has no visible edge of its
         own -- the edge belongs to whatever bounded it -- and drawing one would put a line in
         the drawing that is not in the model. */
      if(o.id===A3D.sel){
        ctx.strokeStyle='#4ea1ff';ctx.lineWidth=1.4;
        ctx.setLineDash([6,4]);ctx.stroke();ctx.setLineDash([]);
      }
      ctx.restore();
    }
  }
  /* __acad3dV94: construction geometry, drawn under the model the way grids are, dashed so
     it never reads as a wall. */
  function drawClines(ctx,V,W,H){
    var box=null,i,o,seg,a,b,q;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(!bimIsCline(o))continue;
      if(!bimLayerShown(o))continue;   /* __acad3dV121 */
      if(!bimObjectVisibleOnLevel(o))continue;
      if(!box)box=bimDrawingExtent2D();
      seg=bimClineVisibleSeg(o,box);
      if(!seg)continue;
      q=bimObjOffset(o);
      a=toScreen([seg[0][0]+q[0],(o.y||0)+q[1],seg[0][1]+q[2]],V,W,H);
      b=toScreen([seg[1][0]+q[0],(o.y||0)+q[1],seg[1][1]+q[2]],V,W,H);
      ctx.save();
      ctx.globalAlpha*=bimLayerAlpha(o);   /* __acad3dV121: the layer's transparency */
      ctx.setLineDash([9,5]);
      ctx.strokeStyle=(o.id===A3D.sel)?'#4ea1ff':(o.col||'#8a7fd0');
      ctx.lineWidth=1.1;
      ctx.beginPath();ctx.moveTo(a[0],a[1]);ctx.lineTo(b[0],b[1]);ctx.stroke();
      ctx.setLineDash([]);
      /* The ROOT is marked, because on an xline it is the only point that means anything and
         it is the one a drafter snaps back to. */
      var rp=toScreen([o.p[0]+q[0],(o.y||0)+q[1],o.p[1]+q[2]],V,W,H);
      ctx.fillStyle=(o.id===A3D.sel)?'#4ea1ff':(o.col||'#8a7fd0');
      ctx.fillRect(rp[0]-2.5,rp[1]-2.5,5,5);
      ctx.restore();
    }
  }
  function drawSketches(ctx,V,W,H){
    var i,o;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(o.t!=='sketch')continue;
      /* __acad3dV121: this never asked about layers, so a layer turned off kept all its linework */
      if(!bimLayerShown(o))continue;
      var lk=bimLayerLook(o);
      (A3D.lastLook||(A3D.lastLook={}))[o.id]=lk;   /* what was decided, for the suite to read */
      if(bimIsPoint(o)){                        /* __acad3dV93 */
        var pmSeg=bimPointMarkerSegs(o.pts[0]),pmQ=bimObjOffset(o),pmK;
        for(pmK=0;pmK<pmSeg.length;pmK++)
          drawSketchPath(ctx,V,W,H,pmSeg[pmK],o.y,(o.id===A3D.sel)?'#4ea1ff':lk.color,false,false,pmQ,null,lk);
        continue;
      }
      drawSketchPath(ctx,V,W,H,o.pts,o.y,(o.id===A3D.sel)?'#4ea1ff':(bimAwCtxCol(o)||lk.color),(o.closed!==false),false,bimObjOffset(o),o.bulges,lk);   /* __acad3dV171b */
    }
    /* __acad3dV90: preview the CURVE, not the chords. A rubber band that draws straight and
       commits curved is the interface disagreeing with the model. */
    if(A3D.sk&&A3D.sk.pts.length)drawSketchPath(ctx,V,W,H,
      A3D.sk.pts,A3D.sk.y,'#ffd479',false,true,null,A3D.sk.bulges);
  }
  function drawRooms(ctx,V,W,H){
    A3D.pendingRoomLegend={by:A3D.roomScheme||'',items:[]};   /* __acad3dV105: rebuilt by every paint that draws rooms */
    if(A3D.section)return;
    var i,o;
    var schemeMap=A3D.roomScheme?bimRoomSchemeMap(A3D.roomScheme):null,legendSeen={};   /* __acad3dV105 */
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(o.t!=='room')continue;
      if(!bimLayerShown(o))continue;   /* __acad3dV121 */
      if(!bimObjectVisibleOnLevel(o))continue;
      var ox=(o.pos&&o.pos[0])||0,oy=(o.pos&&o.pos[1])||0,oz=(o.pos&&o.pos[2])||0;
      var y0=o.y+oy,j,sp=[],cx=0,cz=0;
      for(j=0;j<o.pts.length;j++){
        var wx=o.pts[j][0]+ox,wz=o.pts[j][1]+oz;
        cx+=wx;cz+=wz;
        sp.push(toScreen([wx,y0,wz],V,W,H));
      }
      cx/=o.pts.length;cz/=o.pts.length;
      var sel=(o.id===A3D.sel||(A3D.selSet&&A3D.selSet.indexOf(o.id)>=0));
      /* __acad3dV60: Phase 52a presentation mode for room fills. Same "fill:'none' means keep
         today's look" rule as the main solid loop -- a room with no override still renders
         exactly as before, so the default experience never regresses. */
      var rrg=bimPresentGraphics()?bimResolveGraphics(o,'presentation'):null;   /* __acad3dV122 */
      ctx.save();
      ctx.beginPath();
      ctx.moveTo(sp[0][0],sp[0][1]);
      for(j=1;j<sp.length;j++)ctx.lineTo(sp[j][0],sp[j][1]);
      ctx.closePath();
      /* __acad3dV105: a room colour fill, when one is on, is what this view was asked to show, so
         it wins over the presentation fill; the selection highlight still wins over both. */
      var se=schemeMap?bimRoomSchemeEntry(o,schemeMap):null;
      if(se&&!legendSeen['k'+se.name]){legendSeen['k'+se.name]=1;A3D.pendingRoomLegend.items.push({name:se.name,col:se.col});}
      var schemeCol=(se&&!sel)?se.col:null;
      var roomFill=sel?'rgba(78,161,255,0.16)':(schemeCol||((rrg&&rrg.fill!=='none')?rrg.fill:'rgba(127,212,196,0.14)'));
      var rla=bimLayerAlpha(o);   /* __acad3dV121: the layer's transparency */
      ctx.globalAlpha=rla*(rrg?rrg.opacity:1)*(schemeCol?BIM_SCHEME_ALPHA:1);
      ctx.fillStyle=roomFill;
      ctx.fill();
      ctx.globalAlpha=rla*(rrg?rrg.opacity:1);
      /* __acad3dV63 (Phase 53): a room takes a hatch over its colour fill exactly as a solid does
         -- a hatched room/zone fill is one of the two things presentation drawings use patterns
         for, alongside wall poche. Suppressed while the room is selected so the selection
         highlight stays readable. */
      var roomPat=(rrg&&!sel)?bimCanvasPatternFill(ctx,rrg):null;
      if(roomPat){ctx.fillStyle=roomPat;ctx.fill();}
      ctx.strokeStyle=sel?'#4ea1ff':(rrg?rrg.lineColor:'#7fd4c4');
      ctx.lineWidth=sel?1.6:(rrg?Math.max(0.3,Math.min(6,rrg.lineWeight*BIM_LW_TO_PX)):1.1);
      ctx.setLineDash([3,3]);
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.globalAlpha=rla;
      /* __acad3dV60: same test-observable style record as the main solid loop, keyed by room id
         since rooms don't live in A3D.lastPolys. */
      if(!A3D.lastRoomStyle)A3D.lastRoomStyle={};
      A3D.lastRoomStyle[o.id]={fill:roomFill,scheme:schemeCol,schemeValue:se?se.name:'',   /* __acad3dV105 */
        stroke:sel?'#4ea1ff':(rrg?rrg.lineColor:'#7fd4c4'),lineWidth:sel?1.6:(rrg?Math.max(0.3,Math.min(6,rrg.lineWeight*BIM_LW_TO_PX)):1.1),
        opacity:rrg?rrg.opacity:1,
        pattern:roomPat?rrg.pattern:'none',
        patternColor:roomPat?(rrg.patternColor||'#555555'):null,
        patternScale:roomPat?(rrg.patternScale||1):null};
      if(bimRoomTagged(o.id)){ctx.restore();continue;}   /* __acad3dV101: the tag says it */
      /* __acad3dV101: at a point INSIDE the room -- the vertex average lies outside an L */
      var inW=bimInteriorPoint(o.pts.map(function(p){return [p[0]+ox,p[1]+oz];}));
      if(inW){cx=inW[0];cz=inW[1];}
      var cp=toScreen([cx,y0,cz],V,W,H);
      var line1=(o.number?o.number+'  ':'')+o.name,line2=o.area.toFixed(2)+' m\u00b2'+
        ((bimIsRegionDep(o)&&o.region.open)?' (not enclosed)':'');   /* __acad3dV99 */
      ctx.font='bold 11px system-ui,sans-serif';
      var w1=ctx.measureText(line1).width;
      ctx.font='10px system-ui,sans-serif';
      var w2=ctx.measureText(line2).width;
      var bw=Math.max(w1,w2)+14;
      ctx.fillStyle='rgba(20,22,26,0.78)';
      ctx.fillRect(cp[0]-bw/2,cp[1]-17,bw,32);
      ctx.textAlign='center';ctx.textBaseline='middle';
      ctx.fillStyle='#dfe4ea';
      ctx.font='bold 11px system-ui,sans-serif';
      ctx.fillText(line1,cp[0],cp[1]-7);
      ctx.fillStyle='#9ec1ff';
      ctx.font='10px system-ui,sans-serif';
      ctx.fillText(line2,cp[0],cp[1]+7);
      ctx.restore();
    }
  }
  function drawSkLivePreview(ctx,V,W,H){
    var sk=A3D.sk;
    if(!sk)return;
    if(sk.pts.length&&sk.hover){
      var last=sk.pts[sk.pts.length-1];
      var p1=toScreen([last[0],sk.y,last[1]],V,W,H);
      var p2=toScreen([sk.hover.x,sk.y,sk.hover.z],V,W,H);
      ctx.save();
      ctx.strokeStyle=sk.hover.snapped?'#4ea1ff':'#ffd479';
      ctx.lineWidth=1.4;
      ctx.setLineDash([6,4]);
      ctx.beginPath();ctx.moveTo(p1[0],p1[1]);ctx.lineTo(p2[0],p2[1]);ctx.stroke();
      ctx.setLineDash([]);
      if(sk.hover.snapped){
        ctx.beginPath();ctx.arc(p2[0],p2[1],5,0,Math.PI*2);ctx.strokeStyle='#4ea1ff';ctx.lineWidth=1.6;ctx.stroke();
      }
      var mx=(p1[0]+p2[0])/2,my=(p1[1]+p2[1])/2;
      var label=(A3D_TYPING.active?(A3D_TYPING.buf||'0'):(sk.liveLen||0).toFixed(2));
      ctx.font='11px system-ui,sans-serif';
      var tw=ctx.measureText(label).width;
      ctx.fillStyle='rgba(20,22,26,0.85)';
      ctx.fillRect(mx-tw/2-5,my-19,tw+10,16);
      ctx.fillStyle=A3D_TYPING.active?'#ffd479':'#dfe4ea';
      ctx.textAlign='center';ctx.textBaseline='middle';
      ctx.fillText(label,mx,my-11);
      ctx.restore();
    }
    /* __acad3dV67: the tool/modifier banner used to be painted into the canvas at (10,10),
       over the drawing, restating what the snap pill beside it already showed. Both now live
       in the status bar, which is where the 2D workspace has always put them -- so the same
       information is in the same place in both modes and the drawing area is clear.
       bimSyncStatusHint() is called from the paint path so the bar tracks the live tool. */
    bimSyncStatusHint();
  }
  function sketchCCW(pts){
    var a=0,i,j,P=pts.slice();
    for(i=0;i<P.length;i++){
      j=(i+1)%P.length;
      a+=P[i][0]*P[j][1]-P[j][0]*P[i][1];
    }
    if(a<0)P.reverse();
    return P;
  }
  function earClip(P){
    var idx=[],i,n=P.length,tris=[],guard=0;
    for(i=0;i<n;i++)idx.push(i);
    function cross2(o,a2,b2){return (a2[0]-o[0])*(b2[1]-o[1])-(a2[1]-o[1])*(b2[0]-o[0]);}
    function inTri(p,a2,b2,c2){
      var d1=cross2(p,a2,b2),d2=cross2(p,b2,c2),d3=cross2(p,c2,a2);
      var neg=(d1<0)||(d2<0)||(d3<0),pos=(d1>0)||(d2>0)||(d3>0);
      return !(neg&&pos);
    }
    while(idx.length>3&&guard++<3000){
      var cut=false;
      for(i=0;i<idx.length;i++){
        var i0=idx[(i+idx.length-1)%idx.length],i1=idx[i],i2=idx[(i+1)%idx.length];
        if(cross2(P[i0],P[i1],P[i2])<=1e-9)continue;
        var ok=true,k;
        for(k=0;k<idx.length;k++){
          var ix=idx[k];
          if(ix===i0||ix===i1||ix===i2)continue;
          if(inTri(P[ix],P[i0],P[i1],P[i2])){ok=false;break;}
        }
        if(!ok)continue;
        tris.push([i0,i1,i2]);
        idx.splice(i,1);
        cut=true;
        break;
      }
      if(!cut)break;
    }
    if(idx.length===3)tris.push([idx[0],idx[1],idx[2]]);
    return tris;
  }
  function padMesh(P,y0,h){
    var n=P.length,v=[],f=[],i,j;
    for(i=0;i<n;i++)v.push([P[i][0],y0,P[i][1]]);
    for(i=0;i<n;i++)v.push([P[i][0],y0+h,P[i][1]]);
    var tris=earClip(P);
    for(i=0;i<tris.length;i++)f.push([tris[i][0],tris[i][1],tris[i][2]]);
    for(i=0;i<tris.length;i++)f.push([tris[i][2]+n,tris[i][1]+n,tris[i][0]+n]);
    for(i=0;i<n;i++){
      j=(i+1)%n;
      f.push([j,i,i+n,j+n]);
    }
    return {v:v,f:f};
  }
