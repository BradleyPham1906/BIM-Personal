  /* ---- the legend, on the view: each analysis shown, its key and its source ----
     A key, not a list: each analysis's title, then its swatches with short names flowing in lines,
     then its source, shortened to fit. Not on a view under 620 px, a phone's: there it would cover
     the drawing and the tools, and each analysis's key is in its row in Analyze. */
  function bimDgFit(ctx,t,w){
    if(ctx.measureText(t).width<=w)return t;
    while(t.length>1&&ctx.measureText(t+'\u2026').width>w)t=t.slice(0,-1);
    return t+'\u2026';
  }
  /* __acad3dV165: the key's layout, apart from its drawing, so the words placed before it can keep clear
     of its box. What does not fit a short view goes: the sources first, then whole analyses, those
     shown longest ago first, and a line says how many; the rest keep their order. When each analysis
     was last shown is noticed here, frame by frame, however its layer came on. */
  function bimDgLegendLayout(ctx,W,H){
    if(A3D.sheetCapture||A3D_PLOT.on)return null;
    var D=bimDgState(),blocks=[],i,sr,seen=A3D_DG.seen||(A3D_DG.seen={}),at=A3D_DG.at||(A3D_DG.at={}),tick=null;
    if(D.legendOff)return null;
    for(i=0;i<BIM_DG_AN.length;i++){
      var A=BIM_DG_AN[i],R=D.runs[A.id],on=!!R&&bimDgDiags(A.id).some(function(o){return bimLayerShown(o);});   /* a layer off or frozen, its own or one above it: none of it shown */
      if(on&&!seen[A.id]){if(tick===null)tick=A3D_DG.tick=(A3D_DG.tick||0)+1;at[A.id]=tick;}   /* shown again: the most recent */
      seen[A.id]=on;
      if(on)blocks.push({title:A.name,rows:(R.legend||[]).slice(0,9),src:R.source||'',drawn:[],at:at[A.id]||0,i:blocks.length});
    }
    if(!blocks.length)return null;
    sr=bimSafeViewRect();   /* asked only with a key to place, as the other keys do: it warns when the chrome covers the view */
    if(sr.w<620)return null;   /* a phone's view: each analysis's row in Analyze carries its key */
    ctx.save();
    try{
      var pad=8,rowH=15,sw=12,maxW=Math.round(Math.min(300,Math.max(170,sr.w*0.3))),inner=maxW-2*pad,j,b;
      var lay=function(withSrc,list){   /* the key for these blocks, with or without their sources */
        var ops=[],y=pad,x,w=0,k;
        for(k=0;k<list.length;k++){
          b=list[k];if(k)y+=6;b.drawn=[];b.tt='';b.st='';
          ctx.font='bold 11px sans-serif';
          var tt=bimDgFit(ctx,b.title,inner);ops.push({k:'t',t:tt,x:pad,y:y+rowH/2});b.tt=tt;w=Math.max(w,ctx.measureText(tt).width);y+=rowH;
          ctx.font='11px sans-serif';x=pad;
          for(j=0;j<b.rows.length;j++){
            var r=b.rows[j],nm=r.short||r.name,iw=sw+4+ctx.measureText(nm).width;
            if(x>pad&&x+iw>pad+inner){x=pad;y+=rowH;}
            ops.push({k:'r',r:r,t:nm,x:x,y:y+rowH/2});b.drawn.push(nm);w=Math.max(w,x+iw-pad);x+=iw+10;
          }
          if(b.rows.length)y+=rowH;
          if(withSrc&&b.src){ctx.font='10px sans-serif';var st=bimDgFit(ctx,b.src,inner);ops.push({k:'s',t:st,x:pad,y:y+rowH/2-1});b.st=st;w=Math.max(w,ctx.measureText(st).width);y+=rowH-2;}
        }
        var mt='';
        if(list.length<blocks.length){ctx.font='10px sans-serif';mt=bimDgFit(ctx,'+ '+(blocks.length-list.length)+' more: their keys are in Analyze',inner);y+=6;ops.push({k:'s',t:mt,x:pad,y:y+rowH/2-1});w=Math.max(w,ctx.measureText(mt).width);y+=rowH-2;}
        return {ops:ops,w:Math.ceil(Math.min(maxW,w+2*pad)),h:y+pad,src:withSrc,list:list,mt:mt};
      };
      var Y=sr.y+12;
      if(sr.x+sr.w-12>W-84&&Y<108)Y=108;   /* under the north arrow */
      var avail=sr.y+sr.h-12-Y,LY=lay(true,blocks),gone={},n=0,
        drop=blocks.slice().sort(function(p,q){return (p.at-q.at)||(q.i-p.i);});
      if(LY.h>avail)LY=lay(false,blocks);
      while(LY.h>avail&&n<blocks.length-1){gone[drop[n++].i]=1;LY=lay(false,blocks.filter(function(bb){return !gone[bb.i];}));}
      LY.X=sr.x+sr.w-LY.w-12;LY.Y=Y;LY.all=blocks.length;
      return LY;
    }finally{ctx.restore();}
  }
  function drawDiagramLegend(ctx,V,W,H){
    A3D_DG.legend=null;
    var LY=(A3D_DG.lyCtx===ctx&&A3D_DG.lyFrame===A3D.frames)?A3D_DG.ly:bimDgLegendLayout(ctx,W,H);   /* laid out already this frame, as the words were placed */
    A3D_DG.lyCtx=null;
    if(!LY)return;
    ctx.save();
    try{
      var sw=12,ops=LY.ops,w=LY.w,h=LY.h,X=LY.X,Y=LY.Y,i;
      ctx.globalAlpha=1;ctx.fillStyle='rgba(22,26,32,0.9)';ctx.fillRect(X,Y,w,h);
      ctx.strokeStyle='rgba(255,255,255,0.18)';ctx.lineWidth=1;ctx.strokeRect(X+0.5,Y+0.5,w-1,h-1);
      ctx.beginPath();ctx.rect(X,Y,w,h);ctx.clip();
      ctx.textBaseline='middle';ctx.textAlign='left';
      for(i=0;i<ops.length;i++){
        var op=ops[i],ox=X+op.x,oy=Y+op.y;
        if(op.k==='t'){ctx.font='bold 11px sans-serif';ctx.fillStyle='#e8edf2';ctx.fillText(op.t,ox,oy);continue;}
        if(op.k==='s'){ctx.font='10px sans-serif';ctx.fillStyle='#9aa7b4';ctx.fillText(op.t,ox,oy);continue;}
        var rr=op.r;ctx.strokeStyle=rr.col;ctx.fillStyle=rr.col;ctx.lineWidth=2;
        if(rr.kind==='fill'){ctx.globalAlpha=0.75;ctx.fillRect(ox,oy-5,sw,10);ctx.globalAlpha=1;if(rr.tex){var tk=bimDgTex(ctx,rr.tex,rr.ink);if(tk){ctx.fillStyle=tk;ctx.fillRect(ox,oy-5,sw,10);ctx.fillStyle=rr.col;}}}   /* __acad3dV168: tex */
        else if(rr.kind==='dot'){ctx.beginPath();ctx.arc(ox+sw/2,oy,4,0,2*Math.PI);ctx.fill();}
        else{ctx.setLineDash(rr.kind==='dash'?[4,3]:[]);ctx.beginPath();ctx.moveTo(ox,oy);ctx.lineTo(ox+sw,oy);ctx.stroke();ctx.setLineDash([]);}
        ctx.font='11px sans-serif';ctx.fillStyle='#e8edf2';ctx.fillText(op.t,ox+sw+4,oy);
      }
      A3D_DG.legend={box:[X,Y,w,h],blocks:LY.list.map(function(bb){return {title:bb.tt,rows:bb.drawn,src:bb.st||''};}),more:LY.all-LY.list.length,moreText:LY.mt,sources:LY.src};   /* what was drawn, as drawn */
    }catch(eL){console.warn('[BIM] The site analysis legend could not be drawn',eL);}
    ctx.restore();
  }
  /* ---- the analyses, each laid down by bimDgPlace ----
     The site: the property line's ring if there is one, else the model's buildings, else the map's
     origin; its ground is the lowest level's. Directions are true: an azimuth is measured clockwise
     from true north, which the plan turns by the site's true-north angle (north is -Z). */
  function bimDgSite(){
    var P=A3D.objs.filter(bimIsProperty),ring=null,own,b=null,cx=0,cz=0,r=0,i;
    own=A3D.objs.filter(function(o){return o.t==='solid'&&!o.context&&o.mesh&&o.mesh.v&&o.mesh.v.length&&bimLayerShown(o);});
    if(own.length){b=bimWorldBounds(own.map(function(o){return o.id;}));if(b&&!(b.mn[0]<1e8))b=null;}
    if(P.length){try{ring=bimPropertyGeometry(P[0]).ring;}catch(eP){ring=null;}}
    if(ring&&ring.length>=3){
      for(i=0;i<ring.length;i++){cx+=ring[i][0];cz+=ring[i][1];}
      cx/=ring.length;cz/=ring.length;
      for(i=0;i<ring.length;i++)r=Math.max(r,Math.sqrt((ring[i][0]-cx)*(ring[i][0]-cx)+(ring[i][1]-cz)*(ring[i][1]-cz)));
    }else if(b){cx=(b.mn[0]+b.mx[0])/2;cz=(b.mn[2]+b.mx[2])/2;r=0.5*Math.sqrt((b.mx[0]-b.mn[0])*(b.mx[0]-b.mn[0])+(b.mx[2]-b.mn[2])*(b.mx[2]-b.mn[2]));}
    r=Math.max(8,r||15);
    var y=bimShadowGround(),Rc=Math.max(30,Math.ceil(r*1.7/5)*5),ctx=A3D.site&&A3D.site.context&&A3D.site.context.last;
    return {c:[cx,cz],r:r,y:y,ring:ring,own:own.length,top:b?b.mx[1]:null,Rc:Rc,ctxR:(ctx&&ctx.radius>0)?+ctx.radius:null};
  }
  /* a plan point at an azimuth (degrees from true north) and a distance from the site's centre */
  function bimDgAt(S,az,d,y){
    var a=(az+bimTrueNorthDeg())*Math.PI/180;
    return [S.c[0]+d*Math.sin(a),y===undefined?S.y:y,S.c[1]-d*Math.cos(a)];
  }
  function bimDgCircle(S,R,y,n){var P=[],i;for(i=0;i<n;i++)P.push(bimDgAt(S,360*i/n,R,y));return P;}
  var BIM_DG_DIRS=['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW'];
  function bimDgYear(){var yr=String(bimSunSettings().date||'').slice(0,4);return /^\d{4}$/.test(yr)?yr:String(new Date().getFullYear());}
  function bimDgNoPlace(){var st=bimSunSettings();return !bimSunNum(st.lat)||!bimSunNum(st.lon)||!bimSunNum(st.tz);}
  /* the compass ring, north being true north, and the distance rings: the north arrow and the scale */
  function bimDgFrameRun(S){
    var E=[],Rc=S.Rc,y=S.y+0.05,T=[],lb=[],k,d;
    E.push({k:'ring',name:'Compass ring',g:{kind:'line',pts:bimDgCircle(S,Rc,y,96),closed:true},s:{stroke:'#c9d3dd',w:1.6},
      info:{title:'The compass ring, '+Rc+' m from the centre of the site',rows:[['True north',bimDispNum(bimTrueNorthDeg(),1)+'\u00b0 from the plan\'s up']],
        method:'A circle about the site\'s centre, turned by the site\'s true-north angle',source:'The site\'s settings'}});
    E.push({k:'ring2',name:'Compass ring, outer',g:{kind:'line',pts:bimDgCircle(S,Rc*1.045,y,96),closed:true},s:{stroke:'#c9d3dd',w:0.8,op:0.8},
      info:{title:'The compass ring\'s outer line',method:'A circle about the site\'s centre'}});
    for(k=0;k<16;k++){
      var L=k%4===0?0.09:(k%2===0?0.06:0.035);
      T.push(bimDgAt(S,k*22.5,Rc*(1-L*0.4),y),bimDgAt(S,k*22.5,Rc*(1.045+L*0.6),y));
      lb.push({t:BIM_DG_DIRS[k],p:bimDgAt(S,k*22.5,Rc*(k%4===0?1.2:1.15),y),sz:k%4===0?13:10,col:k===0?'#ffffff':'#c9d3dd',pri:k%4===0?1:3});
    }
    E.push({k:'ticks',name:'Compass points',g:{kind:'segs',pts:T},s:{stroke:'#c9d3dd',w:1.2},lb:lb,
      info:{title:'The sixteen points of the compass, on true north',method:'Every 22.5\u00b0 from true north'}});
    var max=Math.min(500,S.ctxR||500),first=100*Math.ceil((Rc*1.3)/100);
    for(d=first;d<=max;d+=100)
      E.push({k:'dist:'+d,name:d+' m from the site',g:{kind:'line',pts:bimDgCircle(S,d,y,120),closed:true},s:{stroke:'#9aa7b4',w:1.1,dash:[8,6],op:0.85},
        lb:[{t:d+' m',p:bimDgAt(S,90,d,y),col:'#c9d3dd'},{t:d+' m',p:bimDgAt(S,270,d,y),col:'#c9d3dd'}],
        info:{title:d+' m from the centre of the site',rows:[['On foot','about '+Math.max(1,Math.round(d/bimAccSpeed()))+' min, at '+bimDispNum(bimAccSpeed(),1)+' m a minute, as the crow flies']],method:'A circle about the site\'s centre'}});
    return {E:E,run:{legend:[{name:'Compass, on true north',short:'True north',col:'#c9d3dd',kind:'line'},{name:'Every 100 m',short:'100 m rings',col:'#9aa7b4',kind:'dash'}],source:'True north from the site\'s settings'}};
  }
  /* the sun's paths for the solstices and the equinoxes, on a dome over the site, with their hours */
  var BIM_DG_SUNDAYS=[['06-21','21 June','#ffb347'],['03-20','20 March and 22 September','#e8d36a'],['12-21','21 December','#8ab4f8']];
  function bimDgDome(S,R,sp){
    var a=(sp.azimuth+bimTrueNorthDeg())*Math.PI/180,e=sp.elevation*Math.PI/180;
    return [S.c[0]+R*Math.cos(e)*Math.sin(a),S.y+R*Math.sin(e),S.c[1]-R*Math.cos(e)*Math.cos(a)];
  }
  function bimDgSunRun(S){
    var st=bimSunSettings(),E=[],k,m;
    if(bimDgNoPlace())return {E:[],run:{note:'The site\'s latitude, longitude and UTC offset are needed: Analyze site gets the offset with the climate'}};
    var yr=bimDgYear(),R=S.Rc,tzt='UTC'+(st.tz>=0?'+':'\u2212')+bimDispNum(Math.abs(st.tz),2);
    for(k=0;k<BIM_DG_SUNDAYS.length;k++){
      var dd=yr+'-'+BIM_DG_SUNDAYS[k][0],pts=[],marks=[],noon=null;
      for(m=0;m<1440;m+=10){
        var sp=bimSunCalc(st.lat,st.lon,st.tz,dd,bimPad2(m/60)+':'+bimPad2(m%60));
        if(!sp||!(sp.elevation>0))continue;
        var p=bimDgDome(S,R,sp);pts.push(p);
        if(m%60===0)marks.push({p:p,t:(m/60)+'h'});
        if(!noon||sp.elevation>noon.e)noon={e:sp.elevation,p:p,az:sp.azimuth};
      }
      if(pts.length<2)continue;
      var day=bimSunCalc(st.lat,st.lon,st.tz,dd,'12:00');
      E.push({k:'path:'+BIM_DG_SUNDAYS[k][0],name:'Sun path, '+BIM_DG_SUNDAYS[k][1],g:{kind:'marks',pts:pts,marks:marks},
        s:{stroke:BIM_DG_SUNDAYS[k][2],w:1.6,dash:[6,4],mark:'#ffd23f'},
        lb:[{t:BIM_DG_SUNDAYS[k][1],p:[noon.p[0],noon.p[1]+R*0.05,noon.p[2]],col:BIM_DG_SUNDAYS[k][2]}],
        info:{title:'The sun on '+BIM_DG_SUNDAYS[k][1],rows:[['Highest',bimDispNum(noon.e,1)+'\u00b0 up, at '+bimDispNum(noon.az,0)+'\u00b0 from north'],
          ['Sunrise',day&&day.sunrise!==null?bimHHMM(day.sunrise):'-'],['Sunset',day&&day.sunset!==null?bimHHMM(day.sunset):'-'],
          ['Daylight',day&&day.sunrise!==null?bimDispNum((day.sunset-day.sunrise)/60,1)+' h':(day&&day.polar==='day'?'the sun does not set':'the sun does not rise')],
          ['Clock',tzt+(A3D.site.climate&&A3D.site.climate.tzName?' ('+A3D.site.climate.tzName+')':'')]],
          method:'NOAA\'s solar position equations every 10 minutes, on a dome '+R+' m from the site\'s centre; a dot an hour, by the clock at the site\'s UTC offset',
          source:'Sun position (NOAA)',date:dd}});
    }
    var now=bimSunNow();
    if(now&&!now.missing&&now.elevation>0){
      var q=bimDgDome(S,R,now);
      E.push({k:'now',name:'The sun now',g:{kind:'line',pts:[]},sym:{type:'dot',p:q,r:6,col:'#e5484d'},
        lb:[{t:'Now',p:[q[0],q[1]+R*0.06,q[2]],col:'#ff8a8f'}],
        info:{title:'The sun at '+now.settings.time+' on '+now.settings.date,rows:[['Position',bimDispNum(now.elevation,1)+'\u00b0 up, at '+bimDispNum(now.azimuth,0)+'\u00b0 from north']],
          method:'The date and time in Properties, Site, Location',source:'Sun position (NOAA)'}});
    }
    return {E:E,run:{legend:[{name:'21 June',short:'June',col:'#ffb347',kind:'dash'},{name:'20 March, 22 September',short:'March, September',col:'#e8d36a',kind:'dash'},{name:'21 December',short:'December',col:'#8ab4f8',kind:'dash'},
      {name:'An hour',short:'hour',col:'#ffd23f',kind:'dot'},{name:'The sun now',short:'now',col:'#e5484d',kind:'dot'}],source:'NOAA solar position equations',dome:{c:S.c,y:S.y,R:R}}};   /* __acad3dV170: the dome */
  }
  /* the model's shadows at 9, 12 and 15 on the equinox and both solstices: drawn from the model each
     time, so they follow it; each date a layer, the equinox shown */
  var BIM_DG_SHTIMES=[['09:00','9h','#4f8bd6'],['12:00','12h','#8a93a3'],['15:00','15h','#a46bd6']];
  function bimDgShadowRun(S){
    var st=bimSunSettings(),E=[],layers={},k,t;
    if(bimDgNoPlace())return {E:[],run:{note:'The site\'s place and UTC offset are needed for its shadows'}};
    if(!S.own)return {E:[],run:{note:'No building in the model yet: shadows are cast by what is drawn'}};
    var yr=bimDgYear(),order=[1,0,2];   /* the equinox first: the date planners compare */
    for(k=0;k<order.length;k++){
      var D=BIM_DG_SUNDAYS[order[k]],key='shadow:'+D[0],nm=D[1].split(' and ')[0];
      layers[key]={name:'Site analysis - Shadows '+nm,col:'#7c8db0',hidden:k>0};
      for(t=0;t<BIM_DG_SHTIMES.length;t++){
        var sp=bimSunCalc(st.lat,st.lon,st.tz,yr+'-'+D[0],BIM_DG_SHTIMES[t][0]);
        if(!sp||!(sp.elevation>0))continue;
        E.push({k:'sh:'+D[0]+':'+BIM_DG_SHTIMES[t][1],name:'Shadow, '+nm+' '+BIM_DG_SHTIMES[t][1],layer:key,
          g:{kind:'live',live:{kind:'shadow',date:yr+'-'+D[0],time:BIM_DG_SHTIMES[t][0],c:S.c,r:S.r+80}},s:{fill:BIM_DG_SHTIMES[t][2],fop:0.38},
          info:{title:'The model\'s shadow at '+BIM_DG_SHTIMES[t][0]+' on '+nm,rows:[['Sun',bimDispNum(sp.elevation,1)+'\u00b0 up, at '+bimDispNum(sp.azimuth,0)+'\u00b0 from north'],
            ['Shadow',bimDispNum(1/Math.tan(sp.elevation*Math.PI/180),2)+' times a building\'s height long']],
            method:'The model\'s own solids projected along the sun onto the ground, drawn again whenever the model changes',source:'Sun position (NOAA); the model',date:yr+'-'+D[0]}});
      }
    }
    return {E:E,run:{layers:layers,legend:BIM_DG_SHTIMES.map(function(x){return {name:'Shadow at '+x[1],short:x[1],col:x[2],kind:'fill'};}),source:'The model\'s own buildings; 20 March shown'}};
  }
  /* the winds by season from a year of hours, the strongest, and the year's rose */
  var BIM_DG_SEASONS=[['winter','Winter','#7fd3e6'],['spring','Spring','#9be7a7'],['summer','Summer','#f5c26b'],['autumn','Autumn','#e59866']];
  function bimDgSeasonMonths(s,lat){
    var N={winter:'December to February',spring:'March to May',summer:'June to August',autumn:'September to November'},
        So={winter:'June to August',spring:'September to November',summer:'December to February',autumn:'March to May'};
    return (lat<0?So:N)[s];
  }
  /* an arrow from tail to tip, w half its shaft's width, in the plan at height y */
  function bimDgArrow(tail,tip,hw,y){
    var dx=tip[0]-tail[0],dz=tip[1]-tail[1],L=Math.sqrt(dx*dx+dz*dz)||1,u=[dx/L,dz/L],n=[-u[1],u[0]],hh=hw*2.3,hl=Math.min(L*0.45,hw*4.2),nk=[tip[0]-u[0]*hl,tip[1]-u[1]*hl];
    function Q(p,w){return [p[0]+n[0]*w,y,p[1]+n[1]*w];}
    return [Q(tail,hw),Q(nk,hw),Q(nk,hh),[tip[0],y,tip[1]],Q(nk,-hh),Q(nk,-hw),Q(tail,-hw)];
  }
  function bimDgWindRun(S){
    var C=A3D.site&&A3D.site.climate,Hh=C&&C.hourly,Wd=Hh&&Hh.wind,E=[],leg=[],G={},order=[],k;
    if(!Wd||!Wd.year)return {E:[],run:{note:'No wind yet: Analyze site gets a year of hourly wind with the climate'}};
    var Rc=S.Rc,y=S.y+0.1,lat=bimSunSettings().lat||0,src='ERA5 reanalysis (ECMWF), via Open-Meteo';
    /* seasons that blow from the same quarter share one arrow, which names them */
    BIM_DG_SEASONS.forEach(function(x){
      var R=Wd[x[0]];
      if(!R||R.prev===null||R.prev===undefined)return;
      if(!G[R.prev]){G[R.prev]=[];order.push(R.prev);}
      G[R.prev].push({id:x[0],name:x[1],col:x[2],R:R});
    });
    order.forEach(function(sec,gi){
      var L=G[sec],share=0,rows=[],a=(sec*22.5+bimTrueNorthDeg())*Math.PI/180,f=[Math.sin(a),-Math.cos(a)],yy=y+gi*0.02;
      L.forEach(function(it){
        var R=it.R,sp=(R.secMean&&R.secMean[sec]!==null&&R.secMean[sec]!==undefined)?R.secMean[sec]:null;
        share=Math.max(share,R.prevPct||0);
        rows.push([it.name+' ('+bimDgSeasonMonths(it.id,lat)+')',bimDispNum(R.prevPct||0,1)+'% of its hours from '+BIM_DG_DIRS[sec]+(sp!==null?', '+bimDispNum(sp,1)+' m/s on average from there':'')+'; calm '+bimDispNum(R.calm||0,1)+'%']);
      });
      var hw=Rc*(0.025+0.05*Math.min(share,40)/40),tail=[S.c[0]+f[0]*Rc*2.05,S.c[1]+f[1]*Rc*2.05],tip=[S.c[0]+f[0]*Rc*1.1,S.c[1]+f[1]*Rc*1.1];
      var names=L.map(function(it){return it.name;}),words=L.map(function(it,j){return (j?it.name.toLowerCase():it.name)+' '+bimDispNum(it.R.prevPct||0,0)+'%';}).join(', ');
      E.push({k:'prevail:'+BIM_DG_DIRS[sec],name:'Prevailing wind from '+BIM_DG_DIRS[sec]+' ('+names.join(', ').toLowerCase()+')',
        g:{kind:'line',pts:bimDgArrow(tail,tip,hw,yy),closed:true},s:{stroke:L[0].col,fill:L[0].col,fop:0.42,w:1.2},
        lb:[{t:'Wind from '+BIM_DG_DIRS[sec]+': '+words+' of hours',p:[tail[0]+f[0]*Rc*0.16,yy,tail[1]+f[1]*Rc*0.16],col:L[0].col}],
        info:{title:(L.length>1?names.slice(0,-1).join(', ')+' and '+names[names.length-1].toLowerCase():names[0])+': the wind blows most often from '+BIM_DG_DIRS[sec],rows:rows,
          method:'A year of hourly wind 10 m up in sixteen sectors; a season\'s prevailing sector is the one it blows from most often; the arrow is as wide as the largest share',
          source:src,date:Hh.start?Hh.start.slice(0,4):''}});
      leg.push({name:names.join(', ')+' prevailing wind',short:names.join(', '),col:L[0].col,kind:'fill'});
    });
    var Y=Wd.year;
    if(Y.strong!==null&&Y.strong!==undefined&&Y.strong>=0){
      E.push({k:'strong',name:'Strongest winds',g:{kind:'line',pts:[]},sym:{type:'storm',p:bimDgAt(S,Y.strong*22.5,Rc*0.86,y),r:13,col:'#e5484d'},
        lb:[{t:'Strongest winds: '+BIM_DG_DIRS[Y.strong],p:bimDgAt(S,Y.strong*22.5,Rc*0.72,y),col:'#ff8a8f'}],
        info:{title:'The strongest winds come from '+BIM_DG_DIRS[Y.strong],
          rows:[['How','The sector with the most hours in the two fastest classes ('+(Wd.bins&&Wd.bins.length>1?Wd.bins[Wd.bins.length-2]+' m/s and over':'the fastest')+')']],
          method:'A year of hourly wind: storms and gales come from where the fastest hours do',source:src}});
      leg.push({name:'Strongest winds',short:'strongest',col:'#e5484d',kind:'line'});
    }
    var tot=[],mx=0;
    for(k=0;k<16;k++){var sm=0;(Y.pct[k]||[]).forEach(function(v){sm+=v;});tot.push(sm);if(sm>mx)mx=sm;}
    if(mx>0){
      var rp=[];
      for(k=0;k<16;k++){var rr=Rc*(0.16+0.5*tot[k]/mx);rp.push(bimDgAt(S,k*22.5-8,rr,y),bimDgAt(S,k*22.5+8,rr,y),bimDgAt(S,k*22.5+11.25,Rc*0.12,y));}
      E.push({k:'rose',name:'Wind rose, the year',g:{kind:'line',pts:rp,closed:true},s:{stroke:'#7fd3e6',fill:'#7fd3e6',fop:0.16,w:1},
        info:{title:'Where the wind comes from over the year',rows:[['Most often','from '+BIM_DG_DIRS[Y.prev]+', '+bimDispNum(Y.prevPct||0,1)+'% of hours'],['Calm',bimDispNum(Y.calm||0,1)+'%'],['Mean speed',bimDispNum(Y.mean||0,1)+' m/s']],
          method:'Sixteen petals, each as long as its share of the year\'s hours',source:src}});
      leg.push({name:'Wind rose, the year',short:'the year',col:'#7fd3e6',kind:'fill'});
    }
    return {E:E,run:{legend:leg,source:'ERA5 hourly wind via Open-Meteo'+(Hh.year?', '+Hh.year:'')}};
  }
  /* ---- views: what can be seen from the site ----
     An isovist (Benedikt, 1979): sight lines every 2 degrees from the site's centre, each stopped by
     the first building or tree around it that stands taller than the eye -- once at eye height on the
     ground, once from the top floor. From the top floor, what a sight line reaches is a view: water,
     then parks and woods, then a landmark (a tower, a listed or a sacred building, seen over the
     roofs or standing in the way), then open land. Each such thing is one view, towards the middle
     of the sight lines that reach it, as wide as they are. */
  function bimDgObstacles(all){   /* __acad3dV168: all, hidden layers too (3-30-300) */
    var B=[],i,o,c,q,t;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];c=o.context;
      if(!c||(!all&&!bimLayerShown(o)))continue;
      q=bimObjOffset(o);t=c.tags||{};
      if(c.kind==='buildings'&&c.footprint&&c.footprint.length>=3&&c.height>0)
        B.push({kind:'b',pts:c.footprint.map(function(p){return [p[0]+q[0],p[1]+q[2]];}),top:c.height,name:String(t.name||o.name||'').slice(0,40),
          lm:(c.height>=30||!!t.tourism||!!t.historic||t.amenity==='place_of_worship'),tall:c.height>=30});
      else if(c.kind==='trees'&&c.height>0&&o.pts&&o.pts.length){
        var cx=o.pts[0][0]+q[0],cz=o.pts[0][1]+q[2],rr=Math.max(1,(c.crown||4)/2),P=[],k;
        for(k=0;k<8;k++)P.push([cx+rr*Math.cos(k*Math.PI/4),cz+rr*Math.sin(k*Math.PI/4)]);
        B.push({kind:'t',pts:P,top:c.height,name:o.name,id:o.id});
      }
    }
    return B;
  }
  function bimDgRayHit(ox,oz,dx,dz,P,max){
    var best=max,i,n=P.length;
    for(i=0;i<n;i++){
      var a=P[i],b=P[(i+1)%n],ex=b[0]-a[0],ez=b[1]-a[1],den=dx*ez-dz*ex;
      if(Math.abs(den)<1e-12)continue;
      var t=((a[0]-ox)*ez-(a[1]-oz)*ex)/den,s=((a[0]-ox)*dz-(a[1]-oz)*dx)/den;
      if(t>0.01&&s>=0&&s<=1&&t<best)best=t;
    }
    return best;
  }
  /* the sight lines from the site's centre at eye height: how far each runs, and what stops it */
  function bimDgIsovist(S,eye,Bs,Rv){
    var D=[],hit=[],k,i,t,cx=S.c[0],cz=S.c[1],tn=bimTrueNorthDeg();
    /* what holds the eye is the site's own building, not in the way */
    var use=Bs.filter(function(b){return b.top>eye-S.y&&!bimPointInPoly([cx,cz],b.pts);});
    for(k=0;k<180;k++){
      var a=(k*2+tn)*Math.PI/180,dx=Math.sin(a),dz=-Math.cos(a),d=Rv,h=null;
      for(i=0;i<use.length;i++){t=bimDgRayHit(cx,cz,dx,dz,use[i].pts,d);if(t<d){d=t;h=use[i];}}
      D.push(d);hit.push(h);
    }
    return {D:D,hit:hit};
  }
  function bimDgViewFeats(){
    var F=[],i,o,c,q;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];c=o.context;if(!c||!bimLayerShown(o))continue;
      var t=c.tags||{},nm=t.name?String(t.name).slice(0,40):'';
      q=bimObjOffset(o);
      if((c.kind==='water'||c.kind==='green'||c.kind==='landuse')&&o.pts&&o.pts.length>=3&&o.closed&&c.part!=='hole'){
        var open=/^(farmland|meadow|grass|recreation_ground|forest|orchard|vineyard)$/.test(t.landuse||''),pri=c.kind==='water'?1:(c.kind==='green'?2:(open?4:0));
        if(!pri)continue;
        var what=c.kind==='water'?'water':(c.kind==='green'?(t.leisure==='park'?'a park':(t.natural==='wood'||t.landuse==='forest'?'woods':'green space')):'open land');
        F.push({pri:pri,key:c.kind+':'+(nm||c.id||o.id),poly:o.pts.map(function(p){return [p[0]+q[0],p[1]+q[2]];}),label:what+(nm?' ('+nm+')':'')});
      }
    }
    return F;
  }
  /* a target's widest run of neighbouring sight lines, across north too: [first, count] */
  function bimDgRun(ks){
    var on=[],k,best=[0,0],st=-1,n;
    for(k=0;k<180;k++)on.push(false);
    ks.forEach(function(x){on[x]=true;});
    if(ks.length>=180)return [0,180];
    for(k=0;k<360;k++){
      if(on[k%180]){if(st<0)st=k;n=k-st+1;if(n>best[1]&&n<=180)best=[st%180,n];}
      else st=-1;
    }
    return best;
  }
  function bimDgViewsRun(S){
    var Bs=bimDgObstacles(),E=[],T={},k,i;
    if(!Bs.length)return {E:[],run:{note:'No buildings around the site yet: Analyze site gets them from OpenStreetMap'}};
    var Rv=Math.min(400,S.ctxR||400),y=S.y+0.15,eye=S.y+1.6,top=S.own&&S.top!==null?Math.max(S.top-1.5,S.y+3):S.y+10,tn=bimTrueNorthDeg();
    var Ie=bimDgIsovist(S,eye,Bs,Rv),It=bimDgIsovist(S,top,Bs,Rv),src='OpenStreetMap buildings and trees (their tagged heights, else their levels, else an assumed height)';
    function ring(D,yy){var P=[];for(var q=0;q<180;q++)P.push(bimDgAt(S,q*2,Math.max(1,D[q]),yy));return P;}
    function openPct(D){var n=0;D.forEach(function(d){if(d>=Rv*0.98)n++;});return Math.round(n/1.8);}
    E.push({k:'iso:eye',name:'What can be seen at eye level',g:{kind:'line',pts:ring(Ie.D,y),closed:true},s:{stroke:'#8fd694',fill:'#8fd694',fop:0.12,w:1},
      info:{title:'From the ground at eye height (1.6 m), '+openPct(Ie.D)+'% of the horizon is open to '+Rv+' m',rows:[['Sight lines','180, every 2\u00b0, to '+Rv+' m']],
        method:'An isovist: each sight line stops at the first building or tree around the site taller than the eye',source:src}});
    E.push({k:'iso:top',name:'What can be seen from the top floor',g:{kind:'line',pts:ring(It.D,y+0.02),closed:true},s:{stroke:'#c6f0a8',w:1.2,dash:[5,4]},
      info:{title:'From '+bimDispNum(top-S.y,1)+' m up'+(S.own?' (the top floor)':' (no building drawn yet: about a fourth floor)')+', '+openPct(It.D)+'% of the horizon is open to '+Rv+' m',
        rows:[['Sight lines','180, every 2\u00b0, to '+Rv+' m']],method:'An isovist: only what stands taller than this eye stops a sight line',source:src}});
    /* what each sight line from the top floor reaches */
    var F=bimDgViewFeats(),LM=Bs.filter(function(b){return b.lm&&!bimPointInPoly(S.c,b.pts);});
    function add(key,pri,label,kk,d){if(!T[key])T[key]={pri:pri,label:label,ks:[],d:d};T[key].ks.push(kk);T[key].d=Math.min(T[key].d,d);}
    for(k=0;k<180;k++){
      var a=(k*2+tn)*Math.PI/180,dx=Math.sin(a),dz=-Math.cos(a),free=It.D[k],d,seen={};
      for(d=20;d<=free;d+=10){
        var x=S.c[0]+d*dx,z=S.c[1]+d*dz;
        for(i=0;i<F.length;i++)if(!seen[i]&&bimPointInPoly([x,z],F[i].poly)){seen[i]=1;add(F[i].key,F[i].pri,F[i].label,k,d);}
      }
      for(i=0;i<LM.length;i++){var t=bimDgRayHit(S.c[0],S.c[1],dx,dz,LM[i].pts,free+0.5);if(t<free+0.5)add('lm:'+(LM[i].name||i),3,LM[i].name||(LM[i].tall?'a tall building':'a landmark'),k,t);}
    }
    var L=Object.keys(T).map(function(key){var r=bimDgRun(T[key].ks),o=T[key];o.key=key;o.st=r[0];o.n=r[1];o.az=((r[0]+(r[1]-1)/2)*2)%360;return o;})
      .filter(function(o){return o.n>=2;})
      .sort(function(p,q){return p.pri-q.pri||q.n-p.n;});
    var chosen=[];
    L.forEach(function(o){
      if(chosen.length>=5)return;
      for(var j=0;j<chosen.length;j++){var dd=Math.abs(chosen[j].az-o.az);if(Math.min(dd,360-dd)<15)return;}
      chosen.push(o);
    });
    if(!chosen.length){   /* nothing named: the widest open run, if the horizon is not all open */
      var ks=[];for(k=0;k<180;k++)if(It.D[k]>=Rv*0.98)ks.push(k);
      var r0=bimDgRun(ks);
      if(r0[1]>=6&&r0[1]<180)chosen.push({key:'open',pri:5,label:'',st:r0[0],n:r0[1],az:((r0[0]+(r0[1]-1)/2)*2)%360,d:null});
    }
    chosen.forEach(function(o){
      var lab='View'+(o.label?': '+o.label:', open'),w=o.n*2,p1=bimDgAt(S,o.az,S.Rc*1.03,y),p2=bimDgAt(S,o.az,S.Rc*1.6,y);
      E.push({k:'view:'+o.key,name:lab,g:{kind:'line',pts:[p1,p2]},s:{stroke:'#8fd694',w:2.2,dash:[7,5],head:true},
        lb:[{t:lab.toUpperCase(),p:bimDgAt(S,o.az,S.Rc*1.78,y),col:'#b6f0b0'}],
        info:{title:lab+', towards '+BIM_DG_DIRS[Math.round(o.az/22.5)%16]+(o.d?', about '+Math.round(o.d)+' m away':''),
          rows:[['Seen across',w+'\u00b0 of the horizon from the top floor'],['From',bimDispNum(top-S.y,1)+' m up']],
          method:'The top floor\'s sight lines that reach it before a building or a tree taller than the eye stops them; water, then parks and woods, then landmarks, then open land',
          source:'OpenStreetMap'}});
    });
    return {E:E,run:{legend:[{name:'Seen at eye level',short:'eye level',col:'#8fd694',kind:'fill'},{name:'Seen from the top floor',short:'top floor',col:'#c6f0a8',kind:'dash'},{name:'A view',short:'a view',col:'#8fd694',kind:'line'}],
      source:'OpenStreetMap buildings and trees'}};
  }
  /* ---- noise from the roads: a screening estimate ----
     CRTN (Calculation of Road Traffic Noise, 1988): the basic level L10(18h) = 29.1 + 10 log Q dB(A)
     10 m from the kerb, for the 18-hour flow Q; + 33 log(V + 40 + 500/V) + 10 log(1 + 5p/V) - 68.8
     for the speed V (km/h) and heavy vehicles p (%); - 10 log(d'/13.5) for the distance, d' the slant
     distance from a line 3.5 m in from the kerb and 0.5 m up to a point 4 m up. CRTN holds to 300 m,
     so no class reaches further. Open data has a road's class and seldom its traffic, so the flow is
     the class's typical daily traffic (FHWA's functional classes), 94% of it in the 18 hours.
     A building between screens what is behind it, by ISO 9613-2's barrier term at 500 Hz -- the path
     over its roof against the straight one -- and no more than the 20 dB it allows one edge. So the
     classes follow the street: wide where it is open, stopped at the frontages. Hard ground, and only
     the first building on each line: the estimate errs loud, and says it is an estimate. */
  /* __acad3dV167: the classes, their traffic and the app's speeds, heavy vehicles and lanes are the registry's (fhwa.fc, app.roads): bimDgRoads */
  var BIM_DG_NOISE_BANDS=[[55,'#f08a24','55 to 60 dB','55'],[60,'#e34a33','60 to 65 dB','60'],[65,'#b5174a','65 to 70 dB','65'],[70,'#8e4fa3','70 to 75 dB','70'],[75,'#3b5fc0','75 dB and over','75+ dB']];
  var BIM_DG_LAMBDA=0.686,BIM_DG_STEP=15;   /* __acad3dV167: CRTN's range is the registry's (crtn) */
  function bimDgRoadClass(hw){
    hw=String(hw||'');var link=/_link$/.test(hw),base=hw.replace(/_link$/,''),c=bimDgRoads()[base];
    if(!c)return null;
    return {key:base,link:link,fc:c.fc+(link?' (a slip road)':''),u:c.u*(link?0.25:1),r:c.r*(link?0.25:1),v:c.v,p:c.p,l:c.l};
  }
  function bimDgKmh(t){
    var m=/^\s*(\d+(?:\.\d+)?)\s*(mph)?/.exec(String(t||''));
    if(!m)return null;
    var v=parseFloat(m[1]);
    return v>0?(m[2]?v*1.609344:v):null;
  }
  function bimDgL0(Q18,V,p){return 29.1+10*Math.log(Q18)/Math.LN10+33*Math.log(V+40+500/V)/Math.LN10+10*Math.log(1+5*p/V)/Math.LN10-68.8;}
  /* the level a distance from the road's centre line, 4 m up */
  function bimDgLat(L0,dcl,half){
    var d=Math.max(1,dcl-half),dp=Math.sqrt((d+3.5)*(d+3.5)+3.5*3.5);
    return L0-10*Math.log(dp/13.5)/Math.LN10;
  }
  /* how far from the centre line the level falls to T, no further than CRTN holds */
  function bimDgReach(L0,T,half){
    var dp=13.5*Math.pow(10,(L0-T)/10),d2=dp*dp-3.5*3.5;
    if(d2<=0)return 0;
    var d=Math.sqrt(d2)-3.5;
    return d>0?Math.min(bimDgCrtnMax(),d+half):0;
  }
  /* a building's screening, ISO 9613-2: Dz = 10 log(3 + 20 z / lambda), z the path over its roof less
     the straight path, the source 0.5 m up at the road, the building's face a metres off and H high,
     the point x metres off and 4 m up; nothing where the roof is under the line of sight; 20 dB at most */
  function bimDgBarrier(a,H,x){
    if(!(H>0)||!(x>a)||H<=0.5+3.5*a/x)return 0;
    var z=Math.sqrt(a*a+(H-0.5)*(H-0.5))+Math.sqrt((x-a)*(x-a)+(H-4)*(H-4))-Math.sqrt(x*x+3.5*3.5);
    return z>0?Math.min(20,10*Math.log(3+20*z/BIM_DG_LAMBDA)/Math.LN10):0;
  }
  function bimDgSegDist(px,pz,P){
    var best=1e18,at=null,i;
    for(i=0;i+1<P.length;i++){
      var ax=P[i][0],az=P[i][1],ex=P[i+1][0]-ax,ez=P[i+1][1]-az,l2=ex*ex+ez*ez,t=l2>1e-9?((px-ax)*ex+(pz-az)*ez)/l2:0;
      t=Math.max(0,Math.min(1,t));
      var cx=ax+t*ex,cz=az+t*ez,d=Math.sqrt((px-cx)*(px-cx)+(pz-cz)*(pz-cz));
      if(d<best){best=d;at=[cx,cz];}
    }
    return {d:best,at:at};
  }
  /* points about every step metres along a line, each with the line's left-hand normal there */
  function bimDgAlong(P,step){
    var out=[],i,k;
    for(i=0;i+1<P.length;i++){
      var ax=P[i][0],az=P[i][1],dx=P[i+1][0]-ax,dz=P[i+1][1]-az,L=Math.sqrt(dx*dx+dz*dz);
      if(L<1e-6)continue;
      var n=[-dz/L,dx/L],m=Math.max(1,Math.ceil(L/step));
      for(k=out.length?1:0;k<=m;k++)out.push({p:[ax+dx*k/m,az+dz*k/m],n:n});
    }
    return out;
  }
  /* the first building along a line from a point: how far, and how high */
  function bimDgFirstWall(ox,oz,dx,dz,Bb,max){
    var hit=max,H=0,nm='',k,t;
    for(k=0;k<Bb.length;k++){t=bimDgRayHit(ox,oz,dx,dz,Bb[k].pts,hit);if(t<hit){hit=t;H=Bb[k].top;nm=Bb[k].name;}}
    return {d:hit,H:H,name:nm};
  }
  /* a way's classes: from its centre line every BIM_DG_STEP metres, each side out to where the level
     falls to the class, screened behind the first building; each class an area */
  function bimDgNoiseBands(w,Bb,y){
    var R=BIM_DG_NOISE_BANDS.map(function(b){return bimDgReach(w.L0,b[0],w.half);}),Rm=R[0],out=[],A=bimDgAlong(w.P,BIM_DG_STEP),reach=[],i,j,sd;
    if(!(Rm>0)||A.length<2)return out;
    var bx0=1e18,bz0=1e18,bx1=-1e18,bz1=-1e18;
    w.P.forEach(function(p){bx0=Math.min(bx0,p[0]-Rm);bz0=Math.min(bz0,p[1]-Rm);bx1=Math.max(bx1,p[0]+Rm);bz1=Math.max(bz1,p[1]+Rm);});
    var near=Bb.filter(function(b){return b.x1>=bx0&&b.x0<=bx1&&b.z1>=bz0&&b.z0<=bz1;});
    for(i=0;i<A.length;i++){
      reach.push([]);
      for(sd=0;sd<2;sd++){
        var sg=sd?-1:1,wall=bimDgFirstWall(A[i].p[0],A[i].p[1],A[i].n[0]*sg,A[i].n[1]*sg,near,Rm),r=[];
        for(j=0;j<R.length;j++){
          if(R[j]<=wall.d){r.push(R[j]);continue;}
          var x,best=wall.d,T=BIM_DG_NOISE_BANDS[j][0];
          for(x=wall.d+5;x<=Rm+0.01;x+=5){if(bimDgLat(w.L0,x,w.half)-bimDgBarrier(wall.d,wall.H,x)>=T)best=x;else break;}
          r.push(best);
        }
        reach[i].push(r);
      }
    }
    for(j=0;j<R.length;j++){
      if(!(R[j]>0))continue;
      var poly=[];
      for(i=0;i<A.length;i++)poly.push([A[i].p[0]+A[i].n[0]*reach[i][0][j],y,A[i].p[1]+A[i].n[1]*reach[i][0][j]]);
      for(i=A.length-1;i>=0;i--)poly.push([A[i].p[0]-A[i].n[0]*reach[i][1][j],y,A[i].p[1]-A[i].n[1]*reach[i][1][j]]);
      out.push({lv:BIM_DG_NOISE_BANDS[j][0],col:BIM_DG_NOISE_BANDS[j][1],pts:poly});
    }
    return out;
  }
  /* a way's level at the site's edge nearest it, screened by the first building between */
  function bimDgNoiseAt(w,S,Bb){
    var dx=S.c[0]-w.at[0],dz=S.c[1]-w.at[1],d=Math.sqrt(dx*dx+dz*dz)||1,x=Math.max(w.half+1,d-S.r);
    var wall=bimDgFirstWall(w.at[0],w.at[1],dx/d,dz/d,Bb.filter(function(b){return !bimPointInPoly(S.c,b.pts);}),x);
    var Dz=wall.d<x?bimDgBarrier(wall.d,wall.H,x):0;
    return {L:bimDgLat(w.L0,x,w.half)-Dz,Dz:Dz,dcl:x,by:Dz>0?wall.name:''};
  }
  function bimDgNoiseRun(S){
    var E=[],ways=[],groups={},rails={},nb=0,reach=bimDgCrtnMax()+S.r,i,o,c;
    var Bb=bimDgObstacles().filter(function(b){return b.kind==='b';});
    Bb.forEach(function(b){b.x0=1e18;b.z0=1e18;b.x1=-1e18;b.z1=-1e18;b.pts.forEach(function(p){b.x0=Math.min(b.x0,p[0]);b.z0=Math.min(b.z0,p[1]);b.x1=Math.max(b.x1,p[0]);b.z1=Math.max(b.z1,p[1]);});});
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];c=o.context;if(!c)continue;
      if(c.kind==='buildings')nb++;
      if(!o.pts||o.pts.length<2||c.part==='hole')continue;
      var q=bimObjOffset(o),P=o.pts.map(function(p){return [p[0]+q[0],p[1]+q[2]];}),sd;
      if(c.kind==='roads'&&c.tags){
        var rc=bimDgRoadClass(c.tags.highway);if(!rc||c.tunnel||c.tags.tunnel==='yes')continue;
        sd=bimDgSegDist(S.c[0],S.c[1],P);if(sd.d>reach)continue;
        ways.push({P:P,rc:rc,tags:c.tags,d:sd.d,at:sd.at,name:String(c.tags.name||c.tags.ref||'').slice(0,60)});
      }else if(c.kind==='rail'&&!c.tunnel&&!(c.tags&&c.tags.tunnel==='yes')&&!(c.tags&&c.tags.railway==='platform')){
        sd=bimDgSegDist(S.c[0],S.c[1],P);if(sd.d>reach)continue;
        var rn=String((c.tags&&c.tags.name)||'').slice(0,60),rk=rn||((c.osm||'way')+(c.id||o.id));
        if(!rails[rk]||sd.d<rails[rk].d)rails[rk]={d:sd.d,at:sd.at,name:rn,key:rk};
      }
    }
    var rl=Object.keys(rails).map(function(k){return rails[k];}).sort(function(a,b){return a.d-b.d;});
    if(!ways.length&&!rl.length)return {E:[],run:{note:'No roads within '+bimDgCrtnMax()+' m yet: Analyze site gets them from OpenStreetMap'}};
    var urban=nb>=40,y=S.y+0.02;
    /* a street in many ways is one; the unnamed roads of a class are one */
    ways.forEach(function(w){
      var t=w.tags,rc=w.rc,lanes=parseInt(t.lanes,10);if(!(lanes>0))lanes=rc.l;
      w.V=bimDgKmh(t.maxspeed)||rc.v;w.aadt=urban?rc.u:rc.r;w.lanes=lanes;w.half=lanes*3.65/2;
      w.L0=bimDgL0(0.94*w.aadt,w.V,rc.p);
      var at=bimDgNoiseAt(w,S,Bb);w.Ls=at.L;w.Dz=at.Dz;w.dcl=at.dcl;w.by=at.by;
      var gk=w.name?'n:'+w.name+'|'+rc.key:'u:'+rc.key;
      if(!groups[gk])groups[gk]={key:gk,name:w.name,rc:rc,ways:[],top:null};
      groups[gk].ways.push(w);
      if(!groups[gk].top||w.Ls>groups[gk].top.Ls)groups[gk].top=w;
    });
    var G=Object.keys(groups).map(function(k){return groups[k];}).sort(function(a,b){return b.top.Ls-a.top.Ls;}),sum=0;
    G.forEach(function(g){
      var w=g.top,nm=g.name||(w.rc.fc+(g.ways.length>1?'s':'')+', unnamed'),bands=[],segs=[];
      sum+=Math.pow(10,w.Ls/10);
      g.ways.forEach(function(x){
        bands=bands.concat(bimDgNoiseBands(x,Bb,y));
        for(var k=0;k+1<x.P.length;k++)segs.push([x.P[k][0],y,x.P[k][1]],[x.P[k+1][0],y,x.P[k+1][1]]);
      });
      if(!bands.length)return;
      var r55=bimDgReach(w.L0,55,w.half);
      E.push({k:'road:'+g.key,name:'Noise, '+nm,g:{kind:'segs',pts:segs,bands:bands},s:{fop:0.34},
        info:{title:nm+': about '+Math.round(w.L0)+' dB 10 m from the kerb (L10,18h, estimated)',rows:[['Road',(g.name?g.name+', ':'')+'OpenStreetMap '+w.tags.highway+', taken as '+w.rc.fc+(g.ways.length>1?' ('+g.ways.length+' ways)':'')],
          ['Traffic assumed',bimClimInt(w.aadt)+' vehicles a day ('+(urban?'urban':'rural')+': FHWA\'s typical range for the class)'],['Speed',Math.round(w.V)+' km/h'+(w.tags.maxspeed?' (its limit)':' (assumed for the class)')],
          ['Heavy vehicles',w.rc.p+'% (assumed)'],['Lanes',w.lanes+(w.tags.lanes?'':' (assumed)')],['55 dB reaches',Math.round(r55)+' m from its centre line where nothing stands between'+(r55>=bimDgCrtnMax()?' (CRTN\'s limit)':'')],
          ['At the site',Math.round(w.dcl)+' m from its centre line: about '+Math.round(w.Ls)+' dB'+(w.Dz>0?', '+Math.round(w.Dz)+' dB less behind '+(w.by||'a building'):'')]],
          method:'CRTN (1988): the basic level, the speed and heavy-vehicle correction, and the distance to a point 4 m up, to '+bimDispNum(bimDgCrtnMax(),0)+' m; behind the first building, less its screening (ISO 9613-2, 500 Hz, at most 20 dB). Hard ground: it errs loud. A screening estimate: measure where it matters',
          source:'OpenStreetMap roads and buildings; FHWA functional classification (typical daily traffic)'}});
    });
    G.slice(0,5).forEach(function(g){   /* the loudest, marked where they come nearest */
      var w=g.top,nm=g.name||w.rc.fc,lab=nm+': about '+Math.round(w.Ls)+' dB',ap=[w.at[0],y,w.at[1]];
      E.push({k:'src:'+g.key,name:'Noise source, '+nm,g:{kind:'line',pts:[]},sym:{type:'noise',p:ap,r:9,col:'#f0a04b',toward:[S.c[0],y,S.c[1]]},
        lb:[{t:lab,p:ap,col:'#ffc27a',al:'left'}],
        info:{title:nm+': about '+Math.round(w.Ls)+' dB L10,18h at the site, estimated',rows:[['Road',w.rc.fc],['Distance',Math.round(w.dcl)+' m from the site to its centre line'],
          ['Screening',w.Dz>0?Math.round(w.Dz)+' dB, behind '+(w.by||'a building'):'none: the road is in sight']],method:'As the road\'s classes',source:'OpenStreetMap; FHWA; CRTN; ISO 9613-2'}});
    });
    rl.slice(0,3).forEach(function(r){
      var rp=[r.at[0],y,r.at[1]];
      E.push({k:'rail:'+r.key,name:'Noise source, railway'+(r.name?' '+r.name:''),g:{kind:'line',pts:[]},sym:{type:'noise',p:rp,r:9,col:'#d7a7ff',toward:[S.c[0],y,S.c[1]]},
        lb:[{t:'Railway'+(r.name?' ('+r.name+')':'')+', '+Math.round(r.d)+' m: noise and vibration',p:rp,col:'#e2c4ff',al:'left'}],
        info:{title:'A railway '+Math.round(r.d)+' m from the site: a noise and vibration source',rows:[['Level','not estimated: a railway\'s level needs its trains']],method:'Found in OpenStreetMap',source:'OpenStreetMap'}});
    });
    if(sum>0){
      var Lt=10*Math.log(sum)/Math.LN10;
      E.push({k:'site',name:'Noise at the site',g:{kind:'line',pts:[]},sym:{type:'dot',p:[S.c[0],y,S.c[1]],r:4,col:'#f0a04b'},
        lb:[{t:'About '+Math.round(Lt)+' dB at the site',p:[S.c[0],y,S.c[1]+S.r*0.35],col:'#ffc27a',pri:1}],
        info:{title:'About '+Math.round(Lt)+' dB L10,18h at the site from the roads, estimated',rows:[['Roads within '+bimDgCrtnMax()+' m',String(G.length)],['Loudest',G[0]?(G[0].name||G[0].rc.fc)+', '+Math.round(G[0].top.Ls)+' dB':'-'],
          ['For scale','WHO advises road noise below '+bimStdSay('who.noise','road_lden')+' Lden; CRTN\'s L10,18h reads about 2 dB above it']],
          method:'Each street once, at the edge of the site nearest it and screened as its classes are, added as energy: 10 log of the sum of 10^(L/10)',source:'OpenStreetMap; FHWA; CRTN; ISO 9613-2'}});
    }
    return {E:E,run:{legend:BIM_DG_NOISE_BANDS.map(function(b){return {name:b[2],short:b[3],col:b[1],kind:'fill'};}).concat([{name:'A noise source',short:'source',col:'#f0a04b',kind:'dot'}]),
      source:'L10,18h estimated from road class (CRTN, FHWA), screened (ISO 9613-2)'}};
  }
