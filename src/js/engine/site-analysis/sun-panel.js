  /* ================= __acad3dV171d: the sun's panel =================
     reference/research-sun-path.md (7). In Analyze, the Sun paths' panel: the sun now in numbers, its point on the
     dome by the formula; sliders for a place tried (never saved) and for the study's date and time (one undo step when
     let go); Play through the day or through the year; the year's turning points by hemisphere; the sky looking up and
     the sun's height through the day; the temperature's key. Its numbers follow the clock and the sliders without the
     panel being drawn again. */
  var A3D_SUNP={key:'',dkey:''};
  function bimSunLatText(v){return bimDispNum(Math.abs(v),2)+'\u00b0 '+(v<0?'S':'N');}
  function bimSunLonText(v){return bimDispNum(Math.abs(v),2)+'\u00b0 '+(v<0?'W':'E');}
  function bimSunYearDays(y){return ((y%4===0&&y%100!==0)||y%400===0)?366:365;}
  function bimSunDoy(d){var m=/^(\d{4})-(\d{2})-(\d{2})$/.exec(String(d||''));return m?Math.round((Date.UTC(+m[1],+m[2]-1,+m[3])-Date.UTC(+m[1],0,1))/864e5)+1:1;}
  function bimSunDateOf(y,doy){var D=new Date(Date.UTC(y,0,1)+(doy-1)*864e5);return D.getUTCFullYear()+'-'+bimPad2(D.getUTCMonth()+1)+'-'+bimPad2(D.getUTCDate());}
  function bimSunMin(t){var m=/^(\d{1,2}):(\d{2})/.exec(String(t||''));return m?(+m[1])*60+(+m[2]):720;}
  function bimSunF(v){return String(Math.round(v*10)/10);}
  /* the sun now in words: the panel's rows, as drawn and as they follow the clock */
  function bimSunNowVals(){
    var st=bimSunStudy(),R=bimSunDomeOf(bimDgState().runs.sun).Rc,v={st:st,R:R},tz,now,f,X,h;
    v.place=bimSunLatText(st.lat)+', '+bimSunLonText(st.lon)+(st.trial?', tried':'');
    v.day=bimSunDayText(st.date);
    v.time=st.time+' ('+bimSunClockText(st,st.date,st.time)+')';
    tz=bimSunTzAt(st,st.date,st.time);
    now=bimSunCalc(st.lat,st.lon,tz,st.date,st.time);
    v.now=now;v.up=!!(now&&now.elevation>0);
    v.alt=now?bimDispNum(now.elevation,2)+'\u00b0'+(v.up?'':', below the horizon'):'-';
    v.az=now?bimDispNum(now.azimuth,2)+'\u00b0 from true north':'-';
    X=now&&v.up?bimSunXyz(now,R):null;
    v.xyz=X?'X '+bimDispNum(X[0],2)+', Y '+bimDispNum(X[1],2)+', Z '+bimDispNum(X[2],2)+' m':'below the horizon';
    f=bimSunDayFacts(st,st.date);
    v.dayf=!f?'-':(f.rise!==undefined?'sunrise '+bimHHMM(f.rise)+' at '+bimDispNum(f.riseAz,0)+'\u00b0, sunset '+bimHHMM(f.set)+' at '+bimDispNum(f.setAz,0)+'\u00b0, '+bimSunLen(f.len):
      (f.polar==='day'?'the sun does not set':'the sun does not rise'));
    h=v.up?bimSunHeatAt(st,st.date,st.time):null;
    v.heat=h?bimDispNum(h.v,1)+' \u00b0C typical at this hour, '+bimSunMd(h.from)+' to '+bimSunMd(h.to):
      (!v.up?'the sun is down':(st.trial?'the climate is the site\'s':'no year of hours yet: Analyze site gets it'));
    return v;
  }
  function bimSunRow(label,k,val){return '<div class="a3d-awp-r"><span>'+bimEsc(label)+'</span><b data-sunv="'+k+'">'+bimEsc(val)+'</b></div>';}
  function bimSunSliderHtml(k,label,min,max,step,val,out){
    return '<label class="a3d-sun-slr"><span class="a3d-sun-sll">'+bimEsc(label)+'</span><output data-sunout="'+k+'">'+bimEsc(out)+'</output>'+
      '<input type="range" min="'+min+'" max="'+max+'" step="'+step+'" value="'+val+'" data-sunsl="'+k+'" aria-label="'+bimEsc(label)+'"></label>';
  }
  /* the top of the panel: the sun now, and the sliders */
  function bimSunPanelHtml(){
    var v,st,y,z,h='';
    if(bimDgNoPlace()&&!bimSunTrying())return '';
    try{
      v=bimSunNowVals();st=v.st;y=+String(st.date).slice(0,4);z=bimSunZone();
      A3D_SUNP.key='';A3D_SUNP.dkey=[st.lat,st.lon,st.date].join('|');
      h='<div class="a3d-sunp" data-sunpanel="1">';
      if(st.trial)h+='<p class="a3d-awp-note a3d-sun-trial">Trying '+bimEsc(bimSunLatText(st.lat)+', '+bimSunLonText(st.lon))+': not saved, its clock by the longitude. '+
        '<button type="button" class="a3d-awl-lk" data-awact="sun:back">Back to the site\'s place</button></p>';
      h+=bimAwSec('The sun now')+'<div class="a3d-awp-rows a3d-sun-now">'+bimSunRow('Place','place',v.place)+bimSunRow('Day','day',v.day)+bimSunRow('Time','time',v.time)+
        (z.zone&&!st.trial?'<div class="a3d-awp-r"><span>Daylight saving</span><b><button type="button" class="a3d-awl-lk" data-awact="sun:dst" aria-pressed="'+z.dst+'" '+
          'title="Off: standard time all year. Auto: each date\'s own offset, by the time zone">'+(z.dst?'Auto, by the time zone':'Off, standard time all year')+'</button></b></div>':'')+
        bimSunRow('Altitude \u03b1','alt',v.alt)+bimSunRow('Azimuth A','az',v.az)+bimSunRow('On the dome','xyz',v.xyz)+bimSunRow('The day','dayf',v.dayf)+bimSunRow('Temperature','heat',v.heat)+'</div>'+
        '<p class="a3d-awp-note a3d-sun-f">X = R cos \u03b1 sin A, Y = R sin \u03b1, Z = R cos \u03b1 cos A, with the dome\'s R of '+v.R+' m, Y up and Z to true north; the sun by NOAA\'s solar position equations.</p>';
      h+=bimAwSec('Try it')+'<div class="a3d-sun-sl">'+
        bimSunSliderHtml('lat','Latitude',-89.9,89.9,0.1,st.lat,bimSunLatText(st.lat))+
        bimSunSliderHtml('lon','Longitude',-180,180,0.1,st.lon,bimSunLonText(st.lon))+
        bimSunSliderHtml('date','Date',1,bimSunYearDays(y),1,bimSunDoy(st.date),bimSunDayText(st.date))+
        bimSunSliderHtml('time','Time',0,1435,5,bimSunMin(st.time),st.time)+'</div>'+
        '<p class="a3d-awp-note">The latitude and the longitude try another place, never saved; the date and the time are the study\'s own, one undo step when let go.</p>';
      h+='</div>';
    }catch(eP){console.warn('[BIM] The sun\'s panel could not be drawn',eP);h='';}
    return h;
  }
  /* the bottom: the turning points, the two diagrams, the temperature's key */
  function bimSunChartsHtml(){
    var st=bimSunStudy(),h;
    if(!bimSunNum(st.lat)||!bimSunNum(st.lon)||!bimSunNum(st.tz))return '';
    try{
      h='<div class="a3d-sunp2" data-sunpanel2="1">'+bimSunTurnHtml(st)+bimAwSec('Diagrams')+
        '<div class="a3d-awp-chart a3d-sun-chart" data-sunchart="polar">'+bimSunPolarSvg(st)+'</div><div class="a3d-awp-cap">The sky dome in plan, north up: the centre overhead, the rim the horizon; the solstices, the equinoxes, the day studied and the sun now</div>'+
        '<div class="a3d-awp-chart a3d-sun-chart" data-sunchart="height">'+bimSunHeightSvg(st)+'</div><div class="a3d-awp-cap">The sun\'s height through the day, by the clock</div>'+
        bimSunHeatKeyHtml(st)+'</div>';
    }catch(eC){console.warn('[BIM] The sun\'s diagrams could not be drawn',eC);h='';}
    return h;
  }
  /* the summer solstice, the equinoxes, the winter solstice: the seasons by the hemisphere */
  function bimSunTurnHtml(st){
    var y=String(st.date).slice(0,4),N=st.lat>=0,nm={'06-21':N?'Summer solstice':'Winter solstice','03-20':'Equinoxes','12-21':N?'Winter solstice':'Summer solstice'},
      order=N?[0,1,2]:[2,1,0],h=bimAwSec('The year\'s turning points')+'<div class="a3d-sun-tp">';
    function r(a,b){return '<div class="a3d-awp-r"><span>'+bimEsc(a)+'</span><b>'+bimEsc(b)+'</b></div>';}
    order.forEach(function(i){
      var B=BIM_DG_SUNDAYS[i],f=bimSunDayFacts(st,y+'-'+B[0]),up=f&&f.rise!==undefined,sh=f&&f.noonAlt>0?10/Math.tan(f.noonAlt*Math.PI/180):null;
      h+='<div class="a3d-sun-card" data-sunturn="'+B[0]+'"><div class="a3d-sun-cardh"><i style="background:'+B[2]+'" aria-hidden="true"></i><b>'+bimEsc(nm[B[0]])+'</b><span>'+bimEsc(B[1])+'</span></div><div class="a3d-awp-rows">'+
        r('Sunrise',up?bimHHMM(f.rise)+' at '+bimDispNum(f.riseAz,0)+'\u00b0':'-')+r('Sunset',up?bimHHMM(f.set)+' at '+bimDispNum(f.setAz,0)+'\u00b0':'-')+
        r('Noon',f&&f.noonAlt!==null?bimDispNum(f.noonAlt,1)+'\u00b0 up at '+bimHHMM(f.noonAt):'-')+
        r('Daylight',up?bimSunLen(f.len):(f&&f.polar==='day'?'the sun does not set':'the sun does not rise'))+
        r('A 10 m building',sh!==null?'casts '+bimDispNum(sh,1)+' m at noon':'no sun at noon')+'</div></div>';
    });
    return h+'</div>';
  }
  /* the days a diagram draws: the solstices, the equinoxes, and the day studied when it is none of them */
  function bimSunChartDays(st){
    var y=String(st.date).slice(0,4),D=BIM_DG_SUNDAYS.map(function(B){return {d:y+'-'+B[0],c:B[2],t:0};});
    if(!bimSunNearDrawn(st.date))D.push({d:st.date,c:BIM_SUN_DAYC,t:1});
    return D;
  }
  /* looking up, stereographic: the centre overhead, the rim the horizon */
  function bimSunPolarPt(a,az){var t=az*Math.PI/180,r=116*Math.tan((90-Math.max(0,a))*Math.PI/360);return [150+r*Math.sin(t),150-r*Math.cos(t)];}
  function bimSunHX(m){return 34+258*m/1440;}
  function bimSunHY(a){return 146-136*Math.max(0,a)/90;}
  function bimSunVis(e,up){if(up)e.removeAttribute('visibility');else e.setAttribute('visibility','hidden');}
  function bimSunPolarSvg(st){
    var S=300,cx=150,cy=150,R=116,s,k,tz,now;
    function rad(a){return R*Math.tan((90-Math.max(0,a))*Math.PI/360);}
    var pt=bimSunPolarPt;
    s='<svg viewBox="0 0 '+S+' '+S+'" role="img" aria-label="The sun\'s paths on the sky dome, in plan" data-sunpolar="1">';
    [15,30,45,60,75].forEach(function(a){s+='<circle class="gd" cx="'+cx+'" cy="'+cy+'" r="'+bimSunF(rad(a))+'"/>';});
    s+='<circle class="bs" cx="'+cx+'" cy="'+cy+'" r="'+R+'"/>';
    for(k=0;k<24;k++){var t=k*15*Math.PI/180,o=k%6===0?9:4;
      s+='<line class="bs" x1="'+bimSunF(cx+R*Math.sin(t))+'" y1="'+bimSunF(cy-R*Math.cos(t))+'" x2="'+bimSunF(cx+(R+o)*Math.sin(t))+'" y2="'+bimSunF(cy-(R+o)*Math.cos(t))+'"/>';}
    ['N','E','S','W'].forEach(function(n,i){var t=i*Math.PI/2;s+='<text class="lb" x="'+bimSunF(cx+(R+20)*Math.sin(t))+'" y="'+bimSunF(cy-(R+20)*Math.cos(t)+4)+'" text-anchor="middle">'+n+'</text>';});
    [30,60].forEach(function(a){var p=pt(a,0);s+='<text class="tk" x="'+bimSunF(p[0]+3)+'" y="'+bimSunF(p[1]-3)+'">'+a+'\u00b0</text>';});
    bimSunChartDays(st).forEach(function(D){
      var tzd=bimSunTzAt(st,D.d,'12:00'),P=[],H=[],m,r;
      for(m=0;m<=1440;m+=6){r=bimSunCalc(st.lat,st.lon,tzd,D.d,bimPad2(Math.floor(m/60))+':'+bimPad2(m%60));if(r&&r.elevation>0){P.push(pt(r.elevation,r.azimuth));if(m%60===0)H.push(P[P.length-1]);}}
      if(P.length>1)s+='<polyline points="'+P.map(function(q){return bimSunF(q[0])+','+bimSunF(q[1]);}).join(' ')+'" fill="none" stroke="'+D.c+'" stroke-width="2"'+(D.t?' stroke-dasharray="3 3"':'')+' data-sunday="'+D.d+'"/>';
      H.forEach(function(q){s+='<circle cx="'+bimSunF(q[0])+'" cy="'+bimSunF(q[1])+'" r="2.4" fill="'+D.c+'"/>';});
    });
    tz=bimSunTzAt(st,st.date,st.time);now=bimSunCalc(st.lat,st.lon,tz,st.date,st.time);
    var q=now&&now.elevation>0?pt(now.elevation,now.azimuth):[cx,cy];
    return s+'<circle cx="'+bimSunF(q[0])+'" cy="'+bimSunF(q[1])+'" r="5" fill="'+BIM_SUN_RED+'" stroke="var(--surf)" stroke-width="1.5" data-sunnow="polar"'+(now&&now.elevation>0?'':' visibility="hidden"')+'/></svg>';
  }
  /* the sun's height through the day: the clock across, the altitude up */
  function bimSunHeightSvg(st){
    var W=300,H=170,L=34,Rr=W-8,T=10,B=H-24,s,tz,now,mn,x=bimSunHX,yy=bimSunHY;
    s='<svg viewBox="0 0 '+W+' '+H+'" role="img" aria-label="The sun\'s height through the day" data-sunheight="1">';
    [0,30,60,90].forEach(function(a){s+='<line class="'+(a?'gd':'bs')+'" x1="'+L+'" x2="'+Rr+'" y1="'+bimSunF(yy(a))+'" y2="'+bimSunF(yy(a))+'"/><text class="tk" x="'+(L-5)+'" y="'+bimSunF(yy(a)+3.5)+'" text-anchor="end">'+a+'\u00b0</text>';});
    [0,6,12,18,24].forEach(function(hh){s+='<line class="gd" x1="'+bimSunF(x(hh*60))+'" x2="'+bimSunF(x(hh*60))+'" y1="'+T+'" y2="'+B+'"/><text class="tk" x="'+bimSunF(x(hh*60))+'" y="'+(H-8)+'" text-anchor="middle">'+hh+'h</text>';});
    bimSunChartDays(st).forEach(function(D){
      var tzd=bimSunTzAt(st,D.d,'12:00'),P=[],m,r;
      for(m=0;m<=1440;m+=10){r=bimSunCalc(st.lat,st.lon,tzd,D.d,bimPad2(Math.floor(m/60))+':'+bimPad2(m%60));if(r&&r.elevation>0)P.push([x(m),yy(r.elevation)]);
        else if(P.length>1){s+=bimSunPoly(P,D);P=[];}else P=[];}
      if(P.length>1)s+=bimSunPoly(P,D);
    });
    tz=bimSunTzAt(st,st.date,st.time);now=bimSunCalc(st.lat,st.lon,tz,st.date,st.time);mn=bimSunMin(st.time);
    return s+'<circle cx="'+bimSunF(x(mn))+'" cy="'+bimSunF(yy(now?now.elevation:0))+'" r="4.5" fill="'+BIM_SUN_RED+'" stroke="var(--surf)" stroke-width="1.5" data-sunnow="height"'+(now&&now.elevation>0?'':' visibility="hidden"')+'/></svg>';
  }
  function bimSunPoly(P,D){return '<polyline points="'+P.map(function(q){return bimSunF(q[0])+','+bimSunF(q[1]);}).join(' ')+'" fill="none" stroke="'+D.c+'" stroke-width="2"'+(D.t?' stroke-dasharray="3 3"':'')+'/>';}
  function bimSunHeatKeyHtml(st){
    var C=A3D.site&&A3D.site.climate,Hh=C&&C.hourly,h=bimAwSec('Temperature on the dome');
    if(st.trial)return h+'<p class="a3d-awp-note">The climate is the site\'s: back to the site\'s place to see it on the dome.</p>';
    if(!Hh||!Hh.heat)return h+'<p class="a3d-awp-note">No year of hours yet: Analyze site gets it with the climate.</p>';
    return h+'<p class="a3d-awp-note">'+bimEsc(bimSunHalfText(bimSunHalf(st.date)))+': each cell the mean temperature at its hour over its month, at the sun\'s place then; '+Hh.year+', ERA5 via Open-Meteo.</p>'+
      '<div class="a3d-awp-key a3d-sun-heat">'+BIM_HEAT_SHORT.map(function(n,j){var c=BIM_HEAT_COL[j];return '<span class="a3d-awp-keyi"><i class="k-fill" style="background:'+(c.indexOf('var(')===0?'#c2c0b8':c)+'"></i>'+bimEsc(n)+' \u00b0C</span>';}).join('')+'</div>';
  }
  /* the panel's numbers, the sliders and the diagrams' sun, as the clock or a slider moves */
  function bimSunPanelLive(){
    var P=el.propsbody&&el.propsbody.querySelector('[data-sunpanel]'),st,key,dkey,v,a=document.activeElement,C,k,e,now,tz;
    if(!P)return false;
    st=bimSunStudy();
    key=[st.lat,st.lon,st.date,st.time,st.trial?1:0,bimSunZone().dst?1:0].join('|');
    if(key===A3D_SUNP.key)return false;
    A3D_SUNP.key=key;
    v=bimSunNowVals();
    ['place','day','time','alt','az','xyz','dayf','heat'].forEach(function(k){var e=P.querySelector('[data-sunv="'+k+'"]');if(e&&e.textContent!==v[k])e.textContent=v[k];});
    C={lat:[st.lat,bimSunLatText(st.lat)],lon:[st.lon,bimSunLonText(st.lon)],date:[bimSunDoy(st.date),bimSunDayText(st.date)],time:[bimSunMin(st.time),st.time]};
    for(k in C)if(C.hasOwnProperty(k)){
      e=P.querySelector('[data-sunout="'+k+'"]');if(e&&e.textContent!==C[k][1])e.textContent=C[k][1];
      e=P.querySelector('[data-sunsl="'+k+'"]');if(e&&e!==a&&String(e.value)!==String(C[k][0]))e.value=C[k][0];
    }
    dkey=[st.lat,st.lon,st.date].join('|');
    if(dkey!==A3D_SUNP.dkey){   /* another day or place: the turning points, the diagrams and the temperature's half-year drawn again */
      A3D_SUNP.dkey=dkey;
      e=el.propsbody.querySelector('[data-sunpanel2]');if(e)e.outerHTML=bimSunChartsHtml();
    }else{   /* the same day: the sun moved along it */
      tz=bimSunTzAt(st,st.date,st.time);now=bimSunCalc(st.lat,st.lon,tz,st.date,st.time);
      var up=!!(now&&now.elevation>0),q=up?bimSunPolarPt(now.elevation,now.azimuth):[150,150];
      e=el.propsbody.querySelector('[data-sunnow="polar"]');
      if(e){e.setAttribute('cx',bimSunF(q[0]));e.setAttribute('cy',bimSunF(q[1]));bimSunVis(e,up);}
      e=el.propsbody.querySelector('[data-sunnow="height"]');
      if(e){e.setAttribute('cx',bimSunF(bimSunHX(bimSunMin(st.time))));e.setAttribute('cy',bimSunF(bimSunHY(now?now.elevation:0)));bimSunVis(e,up);}
    }
    return true;
  }
  /* ---- what the panel's controls do ---- */
  function bimSunTry(lat,lon){
    if(lat===null||lon===null||lat===undefined||lon===undefined){A3D_SUNX.lat=null;A3D_SUNX.lon=null;}
    else{lat=+lat;lon=+lon;if(!isFinite(lat)||!isFinite(lon)||lat<-90||lat>90||lon<-180||lon>180)return false;A3D_SUNX.lat=lat;A3D_SUNX.lon=lon;}
    paint();if(A3D_AW.on)bimAwRefresh();
    return true;
  }
  function bimSunBack(){A3D_SUNX.lat=null;A3D_SUNX.lon=null;A3D_SUNX.date=null;A3D_SUNX.time=null;paint();if(A3D_AW.on)bimAwRefresh();return true;}
  /* a slider moved (commit: let go): the clock stops, the moment is the slider's */
  function bimSunSlide(k,val,commit){
    var n=parseFloat(val),cur,y,d;
    if(!isFinite(n))return false;
    if(A3D_ANIM.on||A3D_ANIM.paused)bimAnimStop();
    if(k==='lat'||k==='lon'){
      cur=bimSunStudy(true);
      if(!bimSunNum(cur.lat)||!bimSunNum(cur.lon))return false;
      A3D_SUNX.lat=Math.max(-89.9,Math.min(89.9,k==='lat'?n:cur.lat));A3D_SUNX.lon=Math.max(-180,Math.min(180,k==='lon'?n:cur.lon));
      paint();
      if(commit&&A3D_AW.on)bimAwRefresh();else bimSunPanelLive();
      return true;
    }
    if(k==='date'){
      y=+String(bimSunStudy(true).date).slice(0,4)||new Date().getFullYear();
      A3D_SUNX.date=bimSunDateOf(y,Math.max(1,Math.min(bimSunYearDays(y),Math.round(n))));
      if(commit){d=A3D_SUNX.date;A3D_SUNX.date=null;return bimSetSun('date',d);}
    }else if(k==='time'){
      n=Math.max(0,Math.min(1439,Math.round(n)));A3D_SUNX.time=bimPad2(n/60)+':'+bimPad2(n%60);
      if(commit){d=A3D_SUNX.time;A3D_SUNX.time=null;return bimSetSun('time',d);}
    }else return false;
    paint();bimSunPanelLive();
    return true;
  }
  /* Play's two ways: through the day (V170's) or through the year */
  function bimSunMode(m){
    if(m!=='day'&&m!=='year')return false;
    A3D_ANIM.sunMode=m;
    if(A3D_ANIM.on||A3D_ANIM.paused){A3D_ANIM.sunTime=bimAnimSunTime();A3D_ANIM.sunDate=bimAnimSunDate();}
    paint();if(A3D_AW.on)bimAwRefresh();
    return true;
  }
  function bimSunModeHtml(){
    var y=A3D_ANIM.sunMode==='year';
    return '<div class="a3d-awp-acts a3d-sun-mode" role="group" aria-label="Play the sun">'+
      '<button type="button" class="a3d-anzbtn'+(y?'':' on')+'" data-awact="sun:mode:day" aria-pressed="'+(!y)+'">Through the day</button>'+
      '<button type="button" class="a3d-anzbtn'+(y?' on':'')+'" data-awact="sun:mode:year" aria-pressed="'+y+'">Through the year</button></div>';
  }
  function bimSunAct(a){
    var z;
    if(a==='back')return bimSunBack();
    if(a==='mode:day'||a==='mode:year')return bimSunMode(a.slice(5));
    if(a==='dst'){z=bimSunZone();return bimSetSun('dst',z.dst?'':'auto');}
    return false;
  }
