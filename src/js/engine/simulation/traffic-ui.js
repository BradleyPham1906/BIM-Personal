  /* ================= __acad3dV171: traffic and people around the site: the analysis =================
     Traffic and people is an analysis of Analyze's Access category, as the movement layers are: its row turns the
     simulation on (it then plays on V170's clock, Play, Pause and Stop in the status bar), sets the peak hour, the
     quality and the speed, and says what the run assumes and finds. Run lays its elements down on Layers > Site
     analysis - Traffic and people, live and editable as every analysis's are: each signal's plan, the lot's entry with
     its queue, each door with its people, each junction with its delays, from the plan and the run so far. */
  function bimTrSetSettings(k,v){
    var s=bimTrSettings(),o={on:s.on,peak:s.peak,q:s.q,speed:s.speed,seed:s.seed};
    if(o[k]===v)return false;
    pushUndo();
    o[k]=v;
    if(!A3D.site)A3D.site={};
    A3D.site.traffic=o;
    if(k==='speed'&&A3D_TR.run)A3D_TR.run.set.speed=v;   /* the speed at once; the hour, the quality and the seed at the next Play from still */
    saveSoon();
    return true;
  }
  function bimTrCanPlay(){return bimTrSettings().on&&!!bimMvOf();}
  /* the simulation on: it plays at once; off: it stops, and its run is given up */
  function bimTrCommand(on){
    if(on===undefined||on===null)on=!bimTrSettings().on;
    if(on&&!bimMvOf()){a3dToast('Traffic and people: '+bimMvWhyNot());return false;}
    bimTrSetSettings('on',!!on);
    if(on){
      if(A3D_ANIM.on||A3D_ANIM.paused)bimAnimStop();
      bimAnimPlay(true);
      a3dToast('Traffic and people: '+(A3D_TR.run?'playing. Pause keeps the moment, Stop gives the drawing back':'could not start'));
    }else{
      bimTrStop();
      if(!bimAnimFrame().any)bimAnimStop();
      paint();
      a3dToast('Traffic and people: off');
    }
    bimAnalyzeRefresh();
    return true;
  }
  function bimTrAct(v){
    v=String(v||'');
    var p=v.split(':');
    if(p[0]==='sim')return bimTrCommand(p[1]==='on');
    if(p[0]==='peak'&&(p[1]==='am'||p[1]==='pm'))return bimTrSetSettings('peak',p[1]);
    if(p[0]==='q'&&(p[1]==='auto'||BIM_TR_Q[p[1]]))return bimTrSetSettings('q',p[1]);
    if(p[0]==='speed'&&(p[1]==='1'||p[1]==='4'||p[1]==='16'))return bimTrSetSettings('speed',parseInt(p[1],10));
    return false;
  }
  function bimTrSegBtns(lab,key,opts,cur){
    return '<div class="a3d-trset"><span class="a3d-trlab">'+bimEsc(lab)+'</span>'+opts.map(function(o){
      return '<button type="button" class="a3d-anzbtn'+(String(o[0])===String(cur)?' pri':'')+'" data-anzact="tr:'+key+':'+o[0]+'" aria-pressed="'+(String(o[0])===String(cur))+'">'+bimEsc(o[1])+'</button>';}).join('')+'</div>';
  }
  function bimTrMin(v){return v===null||v===undefined?'none yet':bimDispNum(v,v<10?1:0)+' s';}
  /* the row's own part: the settings, what the run assumes, and what it has found so far */
  function bimTrCardHtml(){
    var s=bimTrSettings(),R=A3D_TR.run,dq=bimTrDeviceQ(),h='',res=R?bimTrResults(R):A3D_TR.last;
    h+=bimTrSegBtns('Peak hour','peak',[['am','AM'],['pm','PM']],s.peak);
    h+=bimTrSegBtns('Quality','q',[['auto','Auto ('+BIM_TR_Q[dq].name+')'],['light','Light'],['normal','Normal'],['detailed','Detailed']],s.q);
    h+=bimTrSegBtns('Speed','speed',[[1,'1×'],[4,'4×'],[16,'16×']],s.speed);
    if(R){
      var C=R.c,W=R.w,TR=R.trips;
      h+='<div class="a3d-sacap" data-trlive="1">'+bimEsc(bimDispNum(Math.max(0,R.t-R.res.t0)/60,1)+' minutes of the '+(s.peak==='am'?'morning':'evening')+' peak after a '+bimStdSay('app.traffic','warm')+' warm-up: '+
        C.na+' cars and '+W.na+' walkers now, '+R.N.links.length+' links, '+Object.keys(R.plans).length+' signals ('+R.cap.name+')')+'</div>';
      h+='<div class="a3d-sacap">'+bimEsc('The design\'s own trips: '+bimDispNum(TR.tin,0)+' in and '+bimDispNum(TR.tout,0)+' out in the peak hour by San Diego\'s rates (2003)'+
        (R.uses.skip.length?'; not counted: '+R.uses.skip.join(', '):'')+(R.lotOk?'':'; '+R.N.notes.join('; ')))+'</div>';
    }
    if(res&&res.q)h+='<div class="a3d-sacap">'+bimEsc('The lot\'s entry: '+bimDispNum(res.q.outMean,1)+' cars waiting to leave on average, '+res.q.outMax+' at most; '+res.q.stMax+' standing on the street before it at most')+'</div>';
    h+='<div class="a3d-sacap">'+bimEsc('Not a calibrated model: no counts, each street at its class\'s typical traffic. Signal plans assumed: OpenStreetMap maps where a signal is, never its timing. In 3D the cars and walkers are drawn over the model.')+'</div>';
    return h;
  }
  /* the card V164 makes for the analysis, with the simulation's own part */
  function bimTrCard(card){
    var s=bimTrSettings(),mv=bimMvOf();
    card.status=(s.on?(A3D_TR.run?'Playing: ':'On: Play to run it. '):'')+card.status;
    if(s.on&&card.state!=='stale')card.state=A3D_TR.run?'on':(card.state||'on');
    card.extra=(card.extra||'')+bimTrCardHtml();
    card.acts.unshift({act:'tr:sim:'+(s.on?'off':'on'),label:s.on?'Stop the simulation':'Simulate',pri:!s.on,off:mv?'':bimMvWhyNot(),tip:'Cars and walkers around the site, on the clock: Play, Pause and Stop in the status bar'});
    return card;
  }
  /* ---- Run: the elements, from the plan and the run so far ---- */
  function bimDgTrafficRun(S){
    var A=A3D.site&&A3D.site.access,R=A3D_TR.run,N,plans={},E=[],leg=[],y=S.y+0.15,res=R?bimTrResults(R):A3D_TR.last;
    if(!bimMvOf())return {E:[],run:{note:bimMvWhyNot()}};
    if(R){N=R.N;plans=R.plans;}
    else{
      N=bimTrNet();
      if(N.err)return {E:[],run:{note:N.err}};
      bimTrDemand(N);
      N.J.forEach(function(j){if(j.kind==='signal'){var P=bimTrPlan(N,j);if(P)plans[j.i]=P;}});
    }
    var src='Signal plans assumed (FHWA Signal Timing Manual, 2008; MUTCD 11th Edition); traffic by FHWA\'s classes at Florida\'s K; '+bimMvSrc(A);
    /* each signal's plan */
    Object.keys(plans).forEach(function(ji){
      var P=plans[ji],j=N.J[ji],ph=P.ph.map(function(o,k){return 'phase '+(k+1)+': green '+bimDispNum(o.G,0)+' s, yellow '+bimDispNum(o.Y,1)+' s, all red '+bimDispNum(o.AR,1)+' s';});
      E.push({k:'sig:'+j.n,name:'Signal plan',g:{kind:'line',pts:[],marks:[{p:[j.x,y,j.z],t:'Signal: '+bimDispNum(P.C,0)+' s cycle'+(P.grown?' (grown to hold its least greens)':'')}]},s:{mark:'#2fbf71',markText:'#cfeedd'},
        info:{title:'An assumed signal plan: a '+bimDispNum(P.C,0)+' s cycle',rows:[['Phases',ph.join('; ')],['Webster\'s cycle',isFinite(P.C0)?bimDispNum(P.C0,0)+' s, held between '+bimStdSay('stm.signal','cycle_min')+' and '+bimStdSay('stm.signal','cycle_max'):'the junction is at capacity: the longest'],
          ['Least greens','WALK ('+bimStdSay('mutcd.signal','walk')+') and the crossing at '+bimStdSay('mutcd.walk','clear')+'; '+P.ph.map(function(o){return bimDispNum(o.gmin,0)+' s';}).join(' and ')]],
          method:'Two phases by axis; Webster\'s cycle from the critical lane volumes over '+bimStdSay('stm.signal','sat')+'; Kell and Fullerton\'s yellow and red clearance within the MUTCD\'s limits; no offsets',source:src}});
    });
    if(Object.keys(plans).length)leg.push({name:'Signal, its assumed plan',short:'signal',col:'#2fbf71',kind:'dot'});
    /* the lot's entry and its queue */
    if(N.lot){
      var at=N.lot.at,qt=res&&res.q?'Entry: '+bimDispNum(res.q.outMean,1)+' waiting to leave (most '+res.q.outMax+'), '+res.q.stMax+' standing on the street at most':'Entry: not simulated yet';
      E.push({k:'entry',name:'The lot\'s entry and its queue',g:{kind:'line',pts:[],marks:[{p:[N.x[at],y,N.z[at]],t:qt}]},s:{mark:'#ffb454',markText:'#ffe0b0'},
        info:{title:N.lot.name,rows:[['Queue',qt],['Trips',R?bimDispNum(R.trips.tin,0)+' in and '+bimDispNum(R.trips.tout,0)+' out in the peak hour':'when it runs']],method:'Sampled every '+bimStdSay('app.traffic','bin')+': the cars waiting to leave, and the most standing within '+bimStdSay('app.traffic','queue_r')+' of the entry',source:'San Diego\'s Trip Generation Manual (2003) by the design\'s usages'}});
      leg.push({name:'The lot\'s entry',short:'entry',col:'#ffb454',kind:'dot'});
    }
    /* each door and its people */
    N.doors.forEach(function(d,i){
      var r=res&&res.doors[i],t=r?d.name+': '+bimDispNum(r.inH,0)+' in and '+bimDispNum(r.outH,0)+' out an hour':d.name+': not simulated yet';
      E.push({k:'door:'+i,name:'People at '+d.name,g:{kind:'line',pts:[],marks:[{p:[d.x,y,d.z],t:t}]},s:{mark:'#7fd3e6',markText:'#cdeff6'},
        info:{title:'People at '+d.name,rows:[['People',t],['Door',d.mapped?'mapped in OpenStreetMap':'none mapped: the lot\'s middle']],method:'Counted as each walker arrives at the door or leaves it, over the run',source:'The run'}});
    });
    if(N.doors.length)leg.push({name:'A door, its people',short:'door',col:'#7fd3e6',kind:'dot'});
    /* each junction's delays, where the run has them */
    if(res)res.j.forEach(function(x){
      if(x.carDelay===null&&x.walkWait===null)return;
      var t='Delay '+bimTrMin(x.carDelay)+' a car'+(x.walkWait!==null?', '+bimTrMin(x.walkWait)+' a walker\'s wait':'');
      E.push({k:'xing:'+N.J[x.i].n,name:'Delay at a junction',g:{kind:'line',pts:[],marks:[{p:[x.x,y,x.z],t:t}]},s:{mark:'#e5484d',markText:'#f6c9ca'},
        info:{title:'Delay at a '+({signal:'signalled junction',yield:'junction',allstop:'junction with stops on every approach'}[x.kind]||'junction'),rows:[['Cars',t],['Counted',x.cars+' cars, '+x.walkers+' walkers']],method:'A car\'s time on its approach less its free-flow time; a walker\'s wait at the crossings',source:'The run'}});
    });
    if(res&&res.j.length)leg.push({name:'A junction\'s delay',short:'delay',col:'#e5484d',kind:'dot'});
    var note=res?'':'Simulate, then Run again for the queue, the people at the doors and the delays';
    return {E:E,run:{legend:leg,source:'Traffic and people: assumed signal plans and the run so far',note:note}};
  }
