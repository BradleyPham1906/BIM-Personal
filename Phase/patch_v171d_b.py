#!/usr/bin/env python3
"""V171d, patch b: the sun's elements follow the clock. reference/research-sun-path.md (2 to 4, 6).

A new file, site-analysis/sun-path.js: the paths of the solstices and the equinoxes with their hours, the clock's own
day, the sun now with its angles drawn, the analemma at the clock's time, and the temperature on the band of the sky
the sun crosses, kept as a run would draw them whenever the place, the zone or the clock changes, with no undo step.
The sun moving no longer needs a drawing of its own (bimAnimDrawSun): the sun now is the clock's. The words: no word
over a labelled dot; an hour's beside its dot or left out; a path's name along the path between two hours, the nearest
noon first. Hooks for the suite: testing/hooks-sun.js.

Run from the repository root: python3 Phase/patch_v171d_b.py
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from p171 import begin, rep, write, done, SRC, ROOT   # noqa: E402

begin('caa26bdf3985bc5b272ca919374aa2543387b04da756e8bcecdd0efcd5baded0')   # after patch a

SUN_PATH = r'''  /* ================= __acad3dV171d: the sun path, one clock =================
     reference/research-sun-path.md. The sun's elements follow what they are drawn from -- the place, the zone, the
     year and the moment -- as a run would draw them: the paths of the solstices and the equinoxes with their hours,
     the clock's own day, the sun now with its angles, the sun at the clock's time all year (the analemma), and the
     temperature on the band of the sky the sun crosses. A point on the dome about the site's centre is
     X = R cos(alt) sin(az), Y = R sin(alt), Z = -R cos(alt) cos(az), the azimuth turned by true north (bimDgDome). */
  var BIM_SUN_DAYC='#ff8a8f',BIM_SUN_RED='#e5484d',BIM_SUN_ALLYR='#ffd23f';
  var BIM_SUN_ROWS={dj:['12-21','01-21','02-21','03-21','04-21','05-21','06-21'],jd:['06-21','07-21','08-21','09-21','10-21','11-21','12-21']};
  var BIM_SUN_MOMENT=['today','now','angles','analemma'];   /* what moves with the clock; the rest with the place */
  var A3D_SUNSYNC={place:'',moment:''};
  /* the half-year holding a date: 21 December to 21 June, the days lengthening, or 21 June to 21 December */
  function bimSunHalf(d){var md=String(d||'').slice(5);return md>='06-21'&&md<'12-21'?'jd':'dj';}
  function bimSunHalfText(h){return h==='jd'?'21 June to 21 December, the days shortening':'21 December to 21 June, the days lengthening';}
  function bimSunMd(md){return bimSunDayText('2000-'+md).replace(/ 2000$/,'');}
  /* a day's path on the dome: every 10 minutes the sun is up, a mark on each hour, the highest point */
  function bimSunDayPath(S,R,st,dd){
    var tz=bimSunTzAt(st,dd,'12:00'),pts=[],marks=[],mi=[],noon=null,m,sp,p;
    if(!bimSunNum(tz))return null;
    for(m=0;m<1440;m+=10){
      sp=bimSunCalc(st.lat,st.lon,tz,dd,bimPad2(m/60)+':'+bimPad2(m%60));
      if(!sp||!(sp.elevation>0))continue;
      p=bimDgDome(S,R,sp);pts.push(p);
      if(m%60===0){marks.push({p:p,t:(m/60)+'h'});mi.push(pts.length-1);}
      if(!noon||sp.elevation>noon.e)noon={e:sp.elevation,az:sp.azimuth,i:pts.length-1};
    }
    return {pts:pts,marks:marks,mi:mi,noon:noon,tz:tz};
  }
  /* where a path's name may go: along it, half way between two hours, the nearest noon first */
  function bimSunAlong(D){
    var c=[],k;
    if(!D||!D.pts.length)return [];
    for(k=0;k+1<D.mi.length;k++)c.push(Math.round((D.mi[k]+D.mi[k+1])/2));
    if(!c.length)c.push(D.noon.i);
    c.sort(function(a,b){return Math.abs(a-D.noon.i)-Math.abs(b-D.noon.i);});
    return c.map(function(i){return D.pts[i];});
  }
  /* a day's numbers: sunrise and sunset with their bearings, the noon altitude, the day's length */
  function bimSunDayFacts(st,dd){
    var tz=bimSunTzAt(st,dd,'12:00'),r=bimSunCalc(st.lat,st.lon,tz,dd,'12:00'),hi,f={};
    if(!r)return null;
    hi=bimSunCalc(st.lat,st.lon,tz,dd,bimHHMM(r.noon));   /* solar noon, the day's highest */
    f.tz=tz;f.polar=r.polar;f.noonAlt=hi?hi.elevation:null;f.noonAz=hi?hi.azimuth:null;f.noonAt=r.noon;
    if(r.sunrise!==null&&r.sunset!==null){
      f.rise=r.sunrise;f.set=r.sunset;f.len=r.sunset-r.sunrise;
      f.riseAz=bimSunCalc(st.lat,st.lon,tz,dd,bimHHMM(r.sunrise)).azimuth;f.setAz=bimSunCalc(st.lat,st.lon,tz,dd,bimHHMM(r.sunset)).azimuth;
    }else f.len=r.polar==='day'?1440:0;
    return f;
  }
  function bimSunLen(m){m=Math.round(m);return Math.floor(m/60)+' h '+bimPad2(m%60)+' min';}
  /* the paths, the day studied, the sun now and its angles, the analemma, the temperature: E as bimDgPlace takes it;
     only 'moment', the four that move with the clock */
  function bimDgSunRun(S,only){
    var st=bimSunStudy(),E=[],R=S.Rc,k,yr,mom=only==='moment';
    if(!bimSunNum(st.lat)||!bimSunNum(st.lon)||!bimSunNum(st.tz))return {E:[],run:{note:'The site\'s latitude, longitude and UTC offset are needed: Analyze site gets the offset with the climate'}};
    yr=String(st.date).slice(0,4);
    if(!mom)for(k=0;k<BIM_DG_SUNDAYS.length;k++){
      var B=BIM_DG_SUNDAYS[k],dd=yr+'-'+B[0],D=bimSunDayPath(S,R,st,dd),f=bimSunDayFacts(st,dd),al=bimSunAlong(D);
      E.push({k:'path:'+B[0],name:'Sun path, '+B[1],g:{kind:'marks',pts:D?D.pts:[],marks:D?D.marks:[]},
        s:{stroke:B[2],w:1.6,dash:[6,4],mark:'#ffd23f'},
        lb:al.length?[{t:B[3],p:al[0],alt:al.slice(1,8),col:B[2]}]:[],
        info:{title:'The sun on '+B[1],rows:bimSunFactRows(f,st,dd),
          method:'NOAA\'s solar position equations every 10 minutes, on a dome '+R+' m from the site\'s centre: X = R cos(altitude) sin(azimuth), Y = R sin(altitude), Z = R cos(altitude) cos(azimuth) to the north; a dot an hour, by the clock',
          source:'Sun position (NOAA)',date:dd}});
    }
    var td=st.date,same=BIM_DG_SUNDAYS.some(function(B){return B[0]===String(td).slice(5);}),Dt=same?null:bimSunDayPath(S,R,st,td),ft=bimSunDayFacts(st,td),at=bimSunAlong(Dt);
    E.push({k:'today',name:'Sun path, the day studied',g:{kind:'marks',pts:Dt?Dt.pts:[],marks:Dt?Dt.marks:[]},
      s:{stroke:BIM_SUN_DAYC,w:1.8,dash:[2,4],mark:BIM_SUN_DAYC},
      lb:at.length?[{t:bimSunMd(String(td).slice(5)),p:at[0],alt:at.slice(1,8),col:BIM_SUN_DAYC}]:[],
      info:{title:'The sun on '+bimSunDayText(td)+(same?', drawn with the solstices and equinoxes':''),rows:bimSunFactRows(ft,st,td),
        method:'The day the clock is on: the study\'s date, or the year\'s while it plays through the year',source:'Sun position (NOAA)',date:td}});
    var tz=bimSunTzAt(st,td,st.time),now=bimSunCalc(st.lat,st.lon,tz,td,st.time),up=!!(now&&now.elevation>0),q=up?bimDgDome(S,R,now):null,c0=[S.c[0],S.y,S.c[1]];
    E.push({k:'now',name:'The sun now',g:{kind:'line',pts:up?[c0,q]:[]},s:{stroke:BIM_SUN_RED,w:1.4},sym:up?{type:'dot',p:q,r:6,col:BIM_SUN_RED}:null,
      lb:up?[{t:st.time,p:q,near:1,col:'#ff8a8f',pri:1}]:[],
      info:{title:'The sun at '+st.time+' on '+bimSunDayText(td),rows:up?bimSunNowRows(now,st,td,R):[['The sun','below the horizon']],
        method:'NOAA\'s solar position equations at the clock\'s moment; its ray from the centre of the site',source:'Sun position (NOAA)',date:td}});
    var AN=up?bimSunAngles(S,R,now):null;
    E.push({k:'angles',name:'The sun now, its angles',g:{kind:'lines',lines:AN?AN.lines:[]},s:{stroke:'#ff8a8f',w:1.1,dash:[4,3]},lb:AN?AN.lb:[],
      info:{title:'The sun\'s altitude and azimuth at '+st.time,rows:up?[['Altitude',bimDispNum(now.elevation,1)+'\u00b0, from the ground up to the sun'],['Azimuth',bimDispNum(now.azimuth,1)+'\u00b0, clockwise from true north']]:[['The sun','below the horizon']],
        method:'The altitude in the sun\'s vertical plane, from the ground up; the azimuth on the ground, clockwise from true north'}});
    var Al=bimSunAnalemma(S,R,st);
    E.push({k:'analemma',name:'The sun at '+st.time+' all year',g:{kind:'lines',lines:Al.lines},s:{stroke:BIM_SUN_ALLYR,w:1,dash:[1,3],op:0.85},
      lb:Al.top?[{t:st.time+' all year',p:Al.top,near:1,col:BIM_SUN_ALLYR,pri:5}]:[],
      info:{title:'The sun at '+st.time+' through '+yr,rows:[['Points','every second day, '+Al.n+' above the horizon'],['Clock',bimSunClockText(st,td,st.time)]],
        method:'The figure of eight the sun traces at one time of day through the year (the analemma): the declination and the equation of time',source:'Sun position (NOAA)'}});
    if(!mom){
      var M=bimSunHeatMesh(S,R,st);
      E.push({k:'heat',name:'Temperature where the sun is',g:{kind:'mesh',quads:M.quads},s:{fop:0.55},
        info:{title:'The temperature on the sun\'s band of the sky, '+bimSunHalfText(M.half),rows:M.rows,
          method:'The band between the winter and the summer path, by the hour and by the 21st of each month; each cell the mean temperature at its hour over its days, at the sun\'s place then, in the climate board\'s eleven bands',
          source:M.src}});
    }
    return {E:E,run:{legend:[{name:'21 June',short:'June',col:'#ffb347',kind:'dash'},{name:'20 March, 22 September',short:'March, September',col:'#e8d36a',kind:'dash'},{name:'21 December',short:'December',col:'#8ab4f8',kind:'dash'},
      {name:'The day studied',short:'day',col:BIM_SUN_DAYC,kind:'dash'},{name:'An hour',short:'hour',col:'#ffd23f',kind:'dot'},{name:'The sun now, its angles',short:'now',col:BIM_SUN_RED,kind:'dot'},
      {name:'The sun at this time all year',short:'all year',col:BIM_SUN_ALLYR,kind:'dash'},{name:'Temperature where the sun is',short:'temperature',col:'#ec8f86',kind:'fill'}],
      source:'NOAA solar position equations',dome:{c:S.c,y:S.y,R:R}}};   /* __acad3dV170: the dome */
  }
  function bimSunFactRows(f,st,dd){
    if(!f)return [];
    var L=[['Highest',f.noonAlt!==null?bimDispNum(f.noonAlt,1)+'\u00b0 up, at '+bimDispNum(f.noonAz,0)+'\u00b0 from north, '+bimHHMM(f.noonAt):'-']];
    if(f.rise!==undefined){L.push(['Sunrise',bimHHMM(f.rise)+', at '+bimDispNum(f.riseAz,0)+'\u00b0']);L.push(['Sunset',bimHHMM(f.set)+', at '+bimDispNum(f.setAz,0)+'\u00b0']);}
    L.push(['Daylight',f.rise!==undefined?bimSunLen(f.len):(f.polar==='day'?'the sun does not set':'the sun does not rise')]);
    L.push(['Clock',bimSunClockText(st,dd,'12:00')]);
    return L;
  }
  /* the sun's point on the dome, in the app's axes and in the owner's (Y up, Z to the north) */
  function bimSunXyz(sp,R){
    var a=sp.azimuth*Math.PI/180,e=sp.elevation*Math.PI/180;
    return [R*Math.cos(e)*Math.sin(a),R*Math.sin(e),R*Math.cos(e)*Math.cos(a)];
  }
  function bimSunNowRows(now,st,td,R){
    var X=bimSunXyz(now,R);
    return [['Altitude',bimDispNum(now.elevation,2)+'\u00b0'],['Azimuth',bimDispNum(now.azimuth,2)+'\u00b0 from true north'],
      ['On the dome','X '+bimDispNum(X[0],2)+', Y '+bimDispNum(X[1],2)+', Z '+bimDispNum(X[2],2)+' m (R '+R+' m)'],['Clock',bimSunClockText(st,td,st.time)]];
  }
  /* the sun now's construction: true north, the bearing to its foot, the drop from the sun, the azimuth's arc on the
     ground, the altitude's arc in its vertical plane */
  function bimSunAngles(S,R,now){
    var ra=R*0.3,c0=[S.c[0],S.y,S.c[1]],q=bimDgDome(S,R,now),foot=[q[0],S.y,q[2]],az=[],alt=[],n,i;
    n=Math.max(2,Math.ceil(now.azimuth/5));
    for(i=0;i<=n;i++)az.push(bimDgAt(S,now.azimuth*i/n,ra,S.y+0.02));
    n=Math.max(2,Math.ceil(now.elevation/5));
    for(i=0;i<=n;i++)alt.push(bimDgDome(S,ra*1.15,{azimuth:now.azimuth,elevation:now.elevation*i/n}));
    return {lines:[[c0,bimDgAt(S,0,ra*1.3,S.y+0.02)],[c0,foot],[q,foot],az,alt],
      lb:[{t:'A '+bimDispNum(now.azimuth,1)+'\u00b0',p:az[Math.floor(az.length/2)],near:1,col:'#ff8a8f',pri:2},
        {t:'\u03b1 '+bimDispNum(now.elevation,1)+'\u00b0',p:alt[Math.floor(alt.length/2)],near:1,col:'#ff8a8f',pri:2}]};
  }
  /* the sun at the study's time every second day of the year: a line broken below the horizon and where the clock
     changes (daylight saving Auto) */
  function bimSunAnalemma(S,R,st){
    var yr=+String(st.date).slice(0,4),L=[],cur=null,ltz=null,top=null,n=0,d,D,dd,tz,sp,p;
    for(d=0;d<366;d+=2){
      D=new Date(Date.UTC(yr,0,1)+d*864e5);
      if(D.getUTCFullYear()!==yr)break;
      dd=yr+'-'+bimPad2(D.getUTCMonth()+1)+'-'+bimPad2(D.getUTCDate());
      tz=bimSunTzAt(st,dd,st.time);sp=bimSunCalc(st.lat,st.lon,tz,dd,st.time);
      if(!sp||!(sp.elevation>0)||tz!==ltz){if(cur&&cur.length>1)L.push(cur);cur=null;}
      ltz=tz;
      if(!sp||!(sp.elevation>0))continue;
      p=bimDgDome(S,R,sp);n++;
      if(!cur)cur=[];
      cur.push(p);
      if(!top||p[1]>top[1])top=p;
    }
    if(cur&&cur.length>1)L.push(cur);
    return {lines:L,top:top,n:n};
  }
  /* ---- the temperature on the dome ---- */
  function bimSunHeatCol(v){var c=BIM_HEAT_COL[bimClbHeatClass(v)];return c.indexOf('var(')===0?'#c2c0b8':c;}
  function bimSunR3(p){return [Math.round(p[0]*1000)/1000,Math.round(p[1]*1000)/1000,Math.round(p[2]*1000)/1000];}
  /* the climate's year of hours by the half-year's bands: the mean at each of its hours over each band's days */
  function bimSunHeatBands(Hh,rows){
    var Y=+String(Hh.start).slice(0,4),n=Math.floor(Hh.heat.length/24),out=[],j,h,d;
    function dayOf(md){return Math.round((Date.UTC(Y,+md.slice(0,2)-1,+md.slice(3,5))-Date.UTC(Y,0,1))/864e5);}
    for(j=0;j+1<rows.length;j++){
      var a=dayOf(rows[j]),b=dayOf(rows[j+1]),days=[],mean=[];
      if(b>a){for(d=a;d<b&&d<n;d++)days.push(d);}else{for(d=a;d<n;d++)days.push(d);for(d=0;d<b&&d<n;d++)days.push(d);}
      for(h=0;h<24;h++){var s=0,c=0;days.forEach(function(x){var v=Hh.heat[x*24+h];if(typeof v==='number'&&isFinite(v)){s+=v;c++;}});mean.push(c?s/c:null);}
      out.push(mean);
    }
    return out;
  }
  function bimSunHeatMesh(S,R,st){
    var C=A3D.site&&A3D.site.climate,Hh=C&&C.hourly,half=bimSunHalf(st.date),rows=BIM_SUN_ROWS[half],yr=String(st.date).slice(0,4),Q=[],V=[],band,j,c,m,sp;
    if(st.trial)return {quads:[],half:half,rows:[['Not drawn','the climate is the site\'s: back to the site\'s place to see it']],src:''};
    if(!Hh||!Hh.heat||Hh.heat.length<24*28||!Hh.start||!bimSunNum(C.tz))return {quads:[],half:half,rows:[['Not drawn','no year of hours yet: Analyze site gets it with the climate']],src:''};
    band=bimSunHeatBands(Hh,rows);
    for(j=0;j<rows.length;j++){
      V.push([]);
      for(c=0;c<=72;c++){   /* every 20 minutes of the climate's own clock, the offset its hours came in */
        m=c*20;sp=bimSunCalc(st.lat,st.lon,C.tz,yr+'-'+rows[j],bimPad2(Math.floor(m/60))+':'+bimPad2(m%60));
        V[j].push(sp&&sp.elevation>0?bimSunR3(bimDgDome(S,R,sp)):null);
      }
    }
    for(j=0;j+1<rows.length;j++)for(c=0;c<72;c++){
      var v=band[j][Math.floor(c/3)];
      if(!V[j][c]||!V[j][c+1]||!V[j+1][c+1]||!V[j+1][c]||v===null)continue;
      Q.push({p:[V[j][c],V[j][c+1],V[j+1][c+1],V[j+1][c]],c:bimSunHeatCol(v),v:Math.round(v*10)/10,r:j,h:Math.floor(c/3),k:c%3});
    }
    var lo=null,hi=null;Q.forEach(function(x){if(lo===null||x.v<lo)lo=x.v;if(hi===null||x.v>hi)hi=x.v;});
    return {quads:Q,half:half,src:'ERA5 reanalysis (ECMWF), via Open-Meteo',
      rows:[['Half-year',bimSunHalfText(half)],['Cells',Q.length+' of 20 minutes by a month, the sun up'],['Coolest, warmest',lo===null?'-':bimDispNum(lo,1)+' to '+bimDispNum(hi,1)+' \u00b0C'],
        ['Data','temperature at 2 m, '+Hh.year+', hour by hour'],['Hours','the climate\'s own, UTC'+bimSunOffText(C.tz)]]};
  }
  /* the typical temperature where the sun is at a moment: its band's mean at that hour of the climate's clock */
  function bimSunHeatAt(st,dd,tm){
    var C=A3D.site&&A3D.site.climate,Hh=C&&C.hourly,half=bimSunHalf(dd),rows=BIM_SUN_ROWS[half],md=String(dd).slice(5),j,band,tz,u,h,k;
    if(st.trial||!Hh||!Hh.heat||!Hh.start||!bimSunNum(C.tz))return null;
    j=-1;
    for(k=0;k+1<rows.length;k++){var a=rows[k],b=rows[k+1];if(a<b?(md>=a&&md<b):(md>=a||md<b)){j=k;break;}}
    if(md===rows[rows.length-1])j=rows.length-2;
    if(j<0)return null;
    tz=bimSunTzAt(st,dd,tm);
    var dm=/^(\d{4})-(\d{2})-(\d{2})$/.exec(String(dd)),tt=/^(\d{1,2}):(\d{2})/.exec(String(tm));
    if(!dm||!tt)return null;
    u=Date.UTC(+dm[1],+dm[2]-1,+dm[3],+tt[1],+tt[2])-tz*3600000+C.tz*3600000;
    h=new Date(u).getUTCHours();
    band=bimSunHeatBands(Hh,rows)[j];
    return band[h]===null?null:{v:band[h],h:h,from:rows[j],to:rows[j+1],half:half};
  }
  /* drawn under the model's words: far cells first, each a quad of its band's colour, the hours and the months
     drawn over them, laid on the view at one opacity */
  function bimSunDrawMesh(ctx,V,W,H,o,a){
    var Q=o.dg.g.quads||[],s=o.dg.s||{},T=[],i,j,P,z,sp,c2;
    for(i=0;i<Q.length;i++){
      P=[];z=0;
      for(j=0;j<4;j++){sp=toScreen(bimDgW(o,Q[i].p[j]),V,W,H);if(sp[2]<=0.5){P=null;break;}P.push(sp);z+=sp[2];}
      if(P)T.push({P:P,z:z,q:Q[i]});
    }
    if(!T.length)return;
    T.sort(function(x,y){return y.z-x.z;});
    c2=bimDgOff(ctx,'meshCv');
    c2.lineJoin='round';
    for(i=0;i<T.length;i++){
      P=T[i].P;
      c2.beginPath();c2.moveTo(P[0][0],P[0][1]);c2.lineTo(P[1][0],P[1][1]);c2.lineTo(P[2][0],P[2][1]);c2.lineTo(P[3][0],P[3][1]);c2.closePath();
      c2.fillStyle=T[i].q.c;c2.fill();c2.strokeStyle=T[i].q.c;c2.lineWidth=0.8;c2.stroke();
      c2.beginPath();c2.moveTo(P[3][0],P[3][1]);c2.lineTo(P[2][0],P[2][1]);   /* the month's edge */
      if(T[i].q.k===0){c2.moveTo(P[0][0],P[0][1]);c2.lineTo(P[3][0],P[3][1]);}   /* the hour's */
      c2.strokeStyle='rgba(255,255,255,0.45)';c2.lineWidth=0.7;c2.stroke();
    }
    bimDgBlit(ctx,c2,a*(s.fop===undefined?0.55:s.fop));
  }
  /* ---- the sun's elements, following what they are drawn from ---- */
  function bimSunDomeOf(R){
    var dm=R&&R.dome,S0;
    if(dm&&dm.c&&dm.R>0)return {c:dm.c,y:dm.y||0,Rc:dm.R};
    S0=bimDgSite();return {c:S0.c,y:S0.y,Rc:S0.Rc};
  }
  function bimSunSyncKeys(st){
    var z=bimSunZone(),C=A3D.site&&A3D.site.climate,Hh=C&&C.hourly,
      place=[st.lat,st.lon,st.tz,st.trial?1:0,z.zone,z.dst?1:0,bimTrueNorthDeg(),String(st.date).slice(0,4),bimSunHalf(st.date),
        Hh?(Hh.year+':'+Hh.start+':'+(Hh.heat||[]).length):'',C?C.tz:''].join('|');
    return {place:place,moment:place+'|'+st.date+'|'+st.time};
  }
  /* as a run would draw them, no undo step: a cache of what the place and the clock give. An element moved, or
     whose shape the owner changed, is theirs (marked newer, as a run marks it); a colour changed keeps its colour
     and follows the sun */
  function bimDgSunSync(force){
    var D=bimDgState(),R=D.runs.sun,L,st,K,grp,E,by={},n=0;
    if(!R)return 0;
    L=bimDgDiags('sun');
    if(!L.length||(!force&&!L.some(bimLayerShown)))return 0;
    st=bimSunStudy();
    if(!bimSunNum(st.lat)||!bimSunNum(st.lon)||!bimSunNum(st.tz))return 0;
    K=bimSunSyncKeys(st);
    grp=K.place!==A3D_SUNSYNC.place?'all':(K.moment!==A3D_SUNSYNC.moment?'moment':null);
    if(!grp)return 0;
    A3D_SUNSYNC.place=K.place;A3D_SUNSYNC.moment=K.moment;
    E=bimDgSunRun(bimSunDomeOf(R),grp==='all'?null:'moment').E;
    E.forEach(function(e){by[e.k]=e;});
    L.forEach(function(x){
      var e=by[x.dg.k],old=null,q=x.pos||[0,0,0],gen;
      if(!e)return;
      gen=bimDgCore({g:e.g,s:e.s||{},lb:e.lb||[],sym:e.sym||null});
      try{old=JSON.parse(x.dg.gen||'null');}catch(eG){old=null;}
      if(!(q[0]||q[1]||q[2])&&old&&JSON.stringify([old.g,old.lb,old.sym])===JSON.stringify([x.dg.g,x.dg.lb||[],x.dg.sym||null])){
        if(JSON.stringify(old.s)===JSON.stringify(x.dg.s||{}))x.dg.s=e.s||{};
        x.dg.g=e.g;x.dg.lb=e.lb||[];x.dg.sym=e.sym||null;x.name=String(e.name||x.name).slice(0,80);n++;
      }else if(x.dg.gen!==gen)x.dg.newer=true;
      x.dg.gen=gen;x.dg.info=e.info||{};
    });
    return n;
  }
'''

HOOKS_SUN = r'''  /* __acad3dV171d: the sun path, one clock, for the suite */
  window.__acad3dV171d='spa,dome,zone,dst,standard,trial,preview,study,yearplay,sync,today,angles,analemma,heat,labels,panel,sliders,turning,charts';
  window.__a3dSunZoneOff=function(z,d,t){return bimSunZoneOff(z,d,t);};
  window.__a3dSunZoneStd=function(z,y){return bimSunZoneStd(z,y);};
  window.__a3dSunZone=function(){return bimSunZone();};
  window.__a3dSunTzAt=function(d,t){return bimSunTzAt(bimSunSettings(),d,t);};
  window.__a3dSunStudy=function(noClock){return bimSunStudy(!!noClock);};
  window.__a3dSunMode=function(m){if(m==='year'||m==='day')A3D_ANIM.sunMode=m;return A3D_ANIM.sunMode;};
  window.__a3dAnimSunDate=function(t){var k=A3D_ANIM.t;A3D_ANIM.t=+t||0;var r=bimAnimSunDate();A3D_ANIM.t=k;return r;};
  window.__a3dSunSync=function(force){return bimDgSunSync(!!force);};
  window.__a3dSunHeatAt=function(d,t){var st=bimSunStudy();return bimSunHeatAt(st,d||st.date,t||st.time);};
  window.__a3dSunLabels=function(){return JSON.parse(JSON.stringify({boxes:A3D_DG.labelBoxes||[],dots:A3D_DG.dotKeep||[]}));};
'''

MA = 'js/engine/site-analysis/model-analyses.js'
src_ma = (SRC / MA).read_text(encoding='utf-8')
a = src_ma.index("  /* the sun's paths for the solstices and the equinoxes, on a dome over the site, with their hours */")
b = src_ma.index("  /* the model's shadows at 9, 12 and 15 on the equinox and both solstices: drawn from the model each")
old_sun = src_ma[a:b]
assert old_sun.count('function bimDgSunRun(S){') == 1 and old_sun.count('function bimDgDome(S,R,sp){') == 1
rep(MA, old_sun, r"""  /* the sun's paths for the solstices and the equinoxes, on a dome over the site, with their hours;
     __acad3dV171d: each with its name as the view writes it, and drawn by sun-path.js */
  var BIM_DG_SUNDAYS=[['06-21','21 June','#ffb347','21 June'],['03-20','20 March and 22 September','#e8d36a','20 Mar, 22 Sep'],['12-21','21 December','#8ab4f8','21 December']];
  function bimDgDome(S,R,sp){
    var a=(sp.azimuth+bimTrueNorthDeg())*Math.PI/180,e=sp.elevation*Math.PI/180;
    return [S.c[0]+R*Math.cos(e)*Math.sin(a),S.y+R*Math.sin(e),S.c[1]-R*Math.cos(e)*Math.cos(a)];
  }
""")

ML = 'js/engine/site-analysis/model-layers.js'
rep(ML, """    if(g.kind==='live'){bimDgDrawShadow(ctx,V,W,H,o,a,mo==='sun');return;}
    if(g.kind==='segs'||!g.pts||g.pts.length<3||!s.fill||!g.closed)return;""",
    """    if(g.kind==='live'){bimDgDrawShadow(ctx,V,W,H,o,a,mo==='sun');return;}
    if(g.kind==='mesh'){bimSunDrawMesh(ctx,V,W,H,o,a);return;}   /* __acad3dV171d: the temperature on the dome */
    if(g.kind==='segs'||!g.pts||g.pts.length<3||!s.fill||!g.closed)return;""")
rep(ML, "    if(!(a>0)||(mo==='sun'&&A3D_ANIM.sunTime&&bimAnimFrame().sun))return hit;",
    "    if(!(a>0))return hit;   /* __acad3dV171d: the sun now is the clock's own, moving or still */")
rep(ML, """      hit.dots.push([sp[0],sp[1]]);
      if(g.marks[i].t&&lbOk)Q.push({hit:hit,t:g.marks[i].t,x:sp[0]+8,y:sp[1],col:s.markText||'#f4f1e3',sz:10,al:'left',pri:sel?0:4,a:a,sel:sel,cap:cap});
    }""", """      hit.dots.push([sp[0],sp[1]]);
      if(g.marks[i].t){   /* __acad3dV171d: a labelled dot no word covers; its word beside it or left out */
        A3D_DG.dotKeep.push([sp[0]-5,sp[1]-5,10,10]);
        if(lbOk)Q.push({hit:hit,t:g.marks[i].t,x:sp[0]+8,y:sp[1],col:s.markText||'#f4f1e3',sz:10,al:'left',pri:sel?0:4,a:a,sel:sel,cap:cap,cands:bimDgBeside(sp)});
      }
    }""")
rep(ML, """        hit.boxes.push([sp[0]-rr,sp[1]-rr,2*rr,2*rr]);
      }
    }""", """        hit.boxes.push([sp[0]-rr,sp[1]-rr,2*rr,2*rr]);
        if(dg.a==='sun'){A3D_DG.dotKeep.push([sp[0]-rr,sp[1]-rr,2*rr,2*rr]);if(dg.k==='now'&&bimAnimLive())bimAnimFrame().sunAt=[sp[0],sp[1]];}   /* __acad3dV171d: the sun, kept clear; where it is while it plays */
      }
    }""")
rep(ML, """      sp=toScreen(bimDgW(o,L.p),V,W,H);if(sp[2]<=0.5)continue;
      Q.push({hit:hit,t:L.t,x:sp[0]+(L.al==='left'?14:0),y:sp[1],col:L.col||s.stroke,sz:L.sz||11,al:L.al||'center',pri:sel?0:(L.pri||2),a:a,sel:sel,cap:cap});""",
    """      sp=toScreen(bimDgW(o,L.p),V,W,H);if(sp[2]<=0.5)continue;
      Q.push({hit:hit,t:L.t,x:sp[0]+(L.al==='left'?14:0),y:sp[1],col:L.col||s.stroke,sz:L.sz||11,al:L.al||'center',pri:sel?0:(L.pri||2),a:a,sel:sel,cap:cap,
        cands:L.near?bimDgBeside(sp):(L.alt?bimDgAlong(o,L,sp,V,W,H):null)});   /* __acad3dV171d: beside its point, or along its path */""")
rep(ML, """  function bimDgPlaceLabels(ctx,Q,keep){""", """  /* __acad3dV171d: the places a word may take: beside its dot (right, left, above, below), or along its path at
     each point given, the first the nearest noon */
  function bimDgBeside(sp){return [[sp[0]+8,sp[1],'left'],[sp[0]-8,sp[1],'right'],[sp[0],sp[1]-13,'center'],[sp[0],sp[1]+13,'center']];}
  function bimDgAlong(o,L,sp,V,W,H){
    var C=[[sp[0],sp[1],'center']],i,q;
    for(i=0;i<L.alt.length;i++){q=toScreen(bimDgW(o,L.alt[i]),V,W,H);if(q[2]>0.5)C.push([q[0],q[1],'center']);}
    return C;
  }
  function bimDgPlaceLabels(ctx,Q,keep){""")
rep(ML, """      x0=q.al==='left'?q.x:(q.al==='right'?q.x-w:q.x-w/2);
      for(k=0;k<tries.length;k++)if(q.pri===0||free([x0-2,q.y-h/2+tries[k],w+4,h])){dy=tries[k];break;}""",
    """      x0=q.al==='left'?q.x:(q.al==='right'?q.x-w:q.x-w/2);
      if(q.cands){   /* __acad3dV171d: at one of its own places, never a line away */
        for(k=0;k<q.cands.length;k++){
          var cq=q.cands[k],cx0=cq[2]==='left'?cq[0]:(cq[2]==='right'?cq[0]-w:cq[0]-w/2);
          if(q.pri===0||free([cx0-2,cq[1]-h/2,w+4,h])){q.x=cq[0];q.y=cq[1];q.al=cq[2];x0=cx0;dy=0;break;}
        }
      }else for(k=0;k<tries.length;k++)if(q.pri===0||free([x0-2,q.y-h/2+tries[k],w+4,h])){dy=tries[k];break;}""")
rep(ML, """    if(over)A3D_DG.hits=[];
    if(!L.length)return;""", """    if(over){A3D_DG.hits=[];A3D_DG.dotKeep=[];}
    if(!L.length)return;
    if(!over){try{bimDgSunSync();}catch(eS){console.warn('[BIM] The sun\\'s elements could not follow the clock',eS);}}   /* __acad3dV171d */""")
rep(ML, "      if(over&&bimAnimLive())bimAnimDrawSun(ctx,V,W,H,Q);   /* __acad3dV170 */\n", "")
rep(ML, "      if(Q.length)bimDgPlaceLabels(ctx,Q,bimDgKeepClear(W,H));",
    "      if(Q.length)bimDgPlaceLabels(ctx,Q,bimDgKeepClear(W,H).concat(A3D_DG.dotKeep||[]));   /* __acad3dV171d: the labelled dots kept clear */")

MO = 'js/engine/site-analysis/motion.js'
src_mo = (SRC / MO).read_text(encoding='utf-8')
a = src_mo.index("  /* the sun moving along its path on the sun paths' dome, with its time; it stands in for \"the sun now\" */")
b = src_mo.index("  /* Play from still starts the clock at nothing, the layers coming in one after another; Play after Pause goes on")
assert src_mo[a:b].count('function bimAnimDrawSun(') == 1
rep(MO, src_mo[a:b], "")
rep(MO, "    lb.forEach(function(L){if(L.p)L.p=P(L.p);});",
    "    lb.forEach(function(L){if(L.p)L.p=P(L.p);if(L.alt)L.alt=L.alt.map(P);});   /* __acad3dV171d: a word's places along its path */")
rep(MO, "    (g.lines||[]).forEach(function(Ln){Ln.forEach(function(p){P.push(p);});});\n    (o.dg.lb||[])",
    "    (g.lines||[]).forEach(function(Ln){Ln.forEach(function(p){P.push(p);});});\n    (g.quads||[]).forEach(function(q){q.p.forEach(function(p){P.push(p);});});   /* __acad3dV171d: the temperature on the dome */\n    (o.dg.lb||[])")

rep('js/engine/editing/precision-editing.js',
    "      if(o.dg.g.kind==='live')return {error:'A live shadow follows the sun and the model: it cannot be turned, mirrored or scaled'};",
    "      if(o.dg.g.kind==='live')return {error:'A live shadow follows the sun and the model: it cannot be turned, mirrored or scaled'};\n"
    "      if(o.dg.g.kind==='mesh')return {error:'The temperature on the dome follows the sun: it cannot be turned, mirrored or scaled'};   /* __acad3dV171d */")

write('js/engine/site-analysis/sun-path.js', SUN_PATH)
write('js/engine/testing/hooks-sun.js', HOOKS_SUN)
rep('index.html', '<!-- @include js/engine/site-analysis/model-analyses.js -->\n',
    '<!-- @include js/engine/site-analysis/model-analyses.js -->\n<!-- @include js/engine/site-analysis/sun-path.js -->\n')
rep('index.html', '<!-- @include js/engine/testing/hooks-workspace.js -->\n',
    '<!-- @include js/engine/testing/hooks-workspace.js -->\n<!-- @include js/engine/testing/hooks-sun.js -->\n')
LAY = ROOT / 'tools' / 'app_layout.py'
lay = LAY.read_text(encoding='utf-8')
r1 = "    ('site-analysis/model-analyses.js', '  /* ---- the legend, on the view: each analysis shown, its key and its source ----'),\n"
r2 = "    ('testing/hooks-workspace.js', '  /* __acad3dV171b: the analysis workspace, for the suite */'),\n"
assert lay.count(r1) == 1 and lay.count(r2) == 1
lay = lay.replace(r1, r1 + "    ('site-analysis/sun-path.js', '  /* ================= __acad3dV171d: the sun path, one clock ================='),\n")
lay = lay.replace(r2, r2 + "    ('testing/hooks-sun.js', '  /* __acad3dV171d: the sun path, one clock, for the suite */'),\n")
LAY.write_text(lay, encoding='utf-8')

done()
