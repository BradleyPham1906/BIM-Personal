#!/usr/bin/env python3
"""V171d, patch a: the sun's clock. reference/research-sun-path.md (5).

The site's time zone (a name from the time zone database, kept from the climate) and daylight saving: Off, the UTC
offset all year, the zone's standard time; Auto, each date's own offset from the browser's time zone database. The
offset the climate brings is the one in force on the day it was asked (Open-Meteo), so the zone's standard time is
worked out here instead. A place tried and a moment previewed from the sun's panel stand in for the site's, never
saved; the clock's moment while it plays, its date too when it plays through the year.

Run from the repository root: python3 Phase/patch_v171d_a.py
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from p171 import begin, rep, done   # noqa: E402

begin('4ac4e715e6b200b684d7dffc5659b0d8a77e0286a17ec8d24596235bfb73be98')   # V171c

SP = 'js/engine/site/sun-position.js'

# ---- the zone, daylight saving, the study ----
rep(SP, "  /* __acad3dV107: the site's place on the earth and the moment studied.",
    r"""  /* ================= __acad3dV171d: the sun's clock =================
     reference/research-sun-path.md (5). The site's time zone, a name from the time zone database the climate brings
     (Open-Meteo's timezone=auto), and daylight saving: Off, the UTC offset all year, the zone's standard time; Auto,
     each date's own offset, from the browser's time zone database. Open-Meteo's offset is the one in force on the day
     it was asked, so the zone's standard time is worked out here: the lower of mid-January's and mid-July's. */
  var BIM_SUN_FMT={},BIM_SUN_MEMO={},BIM_SUN_MEMON=0;
  function bimSunZoneOff(zone,dateStr,timeStr){
    var dm=/^(\d{4})-(\d{2})-(\d{2})$/.exec(String(dateStr||'')),tm=/^(\d{1,2}):(\d{2})/.exec(String(timeStr||'12:00')),key,f,t0,o=0,k,P,t;
    if(!zone||!dm||!tm)return null;
    key=zone+'|'+dm[0]+'|'+tm[0];
    if(BIM_SUN_MEMO.hasOwnProperty(key))return BIM_SUN_MEMO[key];
    f=BIM_SUN_FMT[zone];
    if(f===false)return null;
    try{
      if(!f)f=BIM_SUN_FMT[zone]=new Intl.DateTimeFormat('en-US',{timeZone:zone,hour12:false,year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',second:'2-digit'});
      t0=Date.UTC(+dm[1],+dm[2]-1,+dm[3],+tm[1],+tm[2]);
      for(k=0;k<3;k++){   /* the instant whose local time it is: three rounds settle it, a change of the clock included */
        t=t0-o*60000;P={};
        f.formatToParts(new Date(t)).forEach(function(x){P[x.type]=+x.value;});
        o=Math.round((Date.UTC(P.year,P.month-1,P.day,P.hour%24,P.minute,P.second||0)-t)/60000);
      }
      o=isFinite(o)?o/60:null;
    }catch(eZ){if(!f)BIM_SUN_FMT[zone]=false;return null;}
    if(++BIM_SUN_MEMON>4000){BIM_SUN_MEMO={};BIM_SUN_MEMON=0;}
    BIM_SUN_MEMO[key]=o;
    return o;
  }
  function bimSunZoneStd(zone,yr){
    var a=bimSunZoneOff(zone,yr+'-01-15','12:00'),b=bimSunZoneOff(zone,yr+'-07-15','12:00');
    return a===null||b===null?null:Math.min(a,b);
  }
  /* the site's zone, where the browser knows it, and whether daylight saving follows it */
  function bimSunZone(){
    var s=(A3D.site&&A3D.site.sun)||{},C=A3D.site&&A3D.site.climate,z=s.zone||(C&&C.tzName)||null;
    if(z&&bimSunZoneOff(z,new Date().getFullYear()+'-01-15','12:00')===null)z=null;
    return {zone:z,dst:s.dst==='auto'&&!!z};
  }
  /* the UTC offset on a date: the zone's own with daylight saving Auto, else the site's; a place tried has its own */
  function bimSunTzAt(st,dateStr,timeStr){
    var z,o;
    if(!st||st.trial)return st?st.tz:null;
    z=bimSunZone();
    if(z.dst){o=bimSunZoneOff(z.zone,dateStr,timeStr||'12:00');if(o!==null)return o;}
    return st.tz;
  }
  function bimSunOffText(h){var m=Math.round(Math.abs(h)*60);return (h<0?'\u2212':'+')+Math.floor(m/60)+(m%60?':'+bimPad2(m%60):'');}
  /* the clock in words: UTC-5, and the zone, and whether it is daylight saving time */
  function bimSunClockText(st,dateStr,timeStr){
    var tz=bimSunTzAt(st,dateStr,timeStr),z=bimSunZone(),std;
    if(!bimSunNum(tz))return 'no UTC offset';
    if(st.trial)return 'UTC'+bimSunOffText(tz)+', by the longitude';
    if(!z.zone)return 'UTC'+bimSunOffText(tz);
    std=bimSunZoneStd(z.zone,String(dateStr).slice(0,4));
    return 'UTC'+bimSunOffText(tz)+', '+z.zone+(z.dst?(std!==null&&tz>std?', daylight saving time':', standard time'):'');
  }
  /* Properties > Site > Location: the zone, and daylight saving */
  function bimSunZoneRows(){
    var z=bimSunZone();
    if(!z.zone)return '';
    return bimPropText('Time Zone',z.zone)+
      bimPropRow('Daylight Saving','<select data-propmodel="sundst" title="Off: the UTC offset all year, standard time. Auto: each date\'s own offset, by the time zone">'+
        '<option value=""'+(z.dst?'':' selected')+'>Off: standard time all year</option><option value="auto"'+(z.dst?' selected':'')+'>Auto: by the time zone</option></select>');
  }
  /* a place tried and a moment previewed from the sun's panel: never saved, never undone */
  var A3D_SUNX={lat:null,lon:null,date:null,time:null};
  function bimSunTrying(){return bimSunNum(A3D_SUNX.lat)&&bimSunNum(A3D_SUNX.lon);}
  /* the sun studied: the site's settings, a place tried (its offset by the longitude), a moment previewed, and the
     clock's moment while it plays (noClock: without it) */
  function bimSunStudy(noClock){
    var st=bimSunSettings();
    if(bimSunTrying()){st.lat=A3D_SUNX.lat;st.lon=A3D_SUNX.lon;st.tz=Math.round(A3D_SUNX.lon/15);st.trial=true;}
    if(A3D_SUNX.date)st.date=A3D_SUNX.date;
    if(A3D_SUNX.time)st.time=A3D_SUNX.time;
    if(!noClock&&bimAnimLive()){if(A3D_ANIM.sunDate)st.date=A3D_ANIM.sunDate;if(A3D_ANIM.sunTime)st.time=A3D_ANIM.sunTime;}
    return st;
  }
  /* __acad3dV107: the site's place on the earth and the moment studied.""")

rep(SP, """  function bimSunNow(saved){
    var st=bimSunSettings(),miss=[],r;
    if(!saved&&A3D_ANIM.sunTime&&bimAnimLive())st.time=A3D_ANIM.sunTime;   /* __acad3dV170: the sun while it plays; the project's time stays */
    if(!bimSunNum(st.lat))miss.push('latitude');
    if(!bimSunNum(st.lon))miss.push('longitude');
    if(!bimSunNum(st.tz))miss.push('UTC offset');
    if(miss.length)return {missing:miss,settings:st};
    r=bimSunCalc(st.lat,st.lon,st.tz,st.date,st.time);
    if(!r)return {missing:['a valid date and time'],settings:st};
    r.settings=st;
    return r;
  }""", """  function bimSunNow(saved){
    var st=saved?bimSunSettings():bimSunStudy(),miss=[],r,tz;   /* __acad3dV170: the sun while it plays; __acad3dV171d: a place tried, a moment previewed */
    if(!bimSunNum(st.lat))miss.push('latitude');
    if(!bimSunNum(st.lon))miss.push('longitude');
    if(!bimSunNum(st.tz))miss.push('UTC offset');
    if(miss.length)return {missing:miss,settings:st};
    tz=bimSunTzAt(st,st.date,st.time);   /* __acad3dV171d: the zone's own offset on the date, with daylight saving Auto */
    r=bimSunCalc(st.lat,st.lon,tz,st.date,st.time);
    if(!r)return {missing:['a valid date and time'],settings:st};
    r.settings=st;r.tzUsed=tz;
    return r;
  }""")

rep(SP, """      nv=v===''?null:(bimPad2(+m[1])+':'+m[2]);
    }else return false;""", """      nv=v===''?null:(bimPad2(+m[1])+':'+m[2]);
    }else if(field==='dst'){   /* __acad3dV171d: daylight saving, Off or Auto */
      nv=v==='auto'?'auto':null;
      if(nv&&!bimSunZone().zone){a3dToast('Daylight saving needs the site\\'s time zone: Analyze site gets it with the climate');refreshProps();return false;}
    }else return false;""")
rep(SP, """    if(nv===null)delete A3D.site.sun[field];else A3D.site.sun[field]=nv;
    refreshProps();paint();saveSoon();""", """    if(nv===null)delete A3D.site.sun[field];else A3D.site.sun[field]=nv;
    if(field==='tz')delete A3D.site.sun.tzAuto;   /* __acad3dV171d: the owner's own offset, which the climate keeps */
    refreshProps();paint();saveSoon();""")

# ---- the climate: the zone kept, its standard time ----
rep('js/engine/site-analysis/climate-data.js', """        C.tz=Math.round(tzs/36)/100;C.tzName=tzn;
        A3D.site.sun=A3D.site.sun||{};
        if(!bimSunNum(A3D.site.sun.tz)){A3D.site.sun.tz=C.tz;tzSet=true;}""", """        C.tz=Math.round(tzs/36)/100;C.tzName=tzn;
        A3D.site.sun=A3D.site.sun||{};
        /* __acad3dV171d: the zone kept with the site, and its standard time, not the offset of the day it was asked;
           an offset the owner typed is theirs */
        var zstd=tzn?bimSunZoneStd(tzn,new Date().getFullYear()):null;
        if(tzn)A3D.site.sun.zone=tzn;
        if(!bimSunNum(A3D.site.sun.tz)||(A3D.site.sun.tzAuto&&zstd!==null&&A3D.site.sun.tz!==zstd)){A3D.site.sun.tz=zstd!==null?zstd:C.tz;A3D.site.sun.tzAuto=true;tzSet=true;}""")

# ---- Properties > Site > Location ----
rep('js/engine/site-analysis/panel.js', """placeholder="not set" title="Hours from UTC in force on the date: -5 EST, -4 EDT">');""",
    """placeholder="not set" title="Standard time\\'s hours from UTC: -5 for New York">');
    loc+=bimSunZoneRows();   /* __acad3dV171d: the zone, and daylight saving */""")
rep('js/engine/ui/build-ui.js', "if(mk==='sunlat'||mk==='sunlon'||mk==='suntz'||mk==='sundate'||mk==='suntime'){bimSetSun(mk.slice(3),mv);return;}   /* __acad3dV107 */",
    "if(mk==='sunlat'||mk==='sunlon'||mk==='suntz'||mk==='sundate'||mk==='suntime'||mk==='sundst'){bimSetSun(mk.slice(3),mv);return;}   /* __acad3dV107; __acad3dV171d: sundst */")

# ---- the sun study in plan: the place tried, each date's offset ----
SH = 'js/engine/site/shadows.js'
rep(SH, """    if(!A3D.showSun||!bimCameraIsPlan()||A3D.sheetCapture)return;   /* __acad3dV119 */
    var st=bimSunSettings();""", """    if(!A3D.showSun||!bimCameraIsPlan()||A3D.sheetCapture)return;   /* __acad3dV119 */
    var st=bimSunStudy();   /* __acad3dV171d: a place tried; each date's own offset below */""")
rep(SH, "          sp=bimSunCalc(st.lat,st.lon,st.tz,days[k][0],bimPad2(i/60)+':'+bimPad2(i%60));",
    "          sp=bimSunCalc(st.lat,st.lon,bimSunTzAt(st,days[k][0],'12:00'),days[k][0],bimPad2(i/60)+':'+bimPad2(i%60));")
rep(SH, "          sp=bimSunCalc(st.lat,st.lon,st.tz,days[k][0],bimPad2(i/60)+':00');",
    "          sp=bimSunCalc(st.lat,st.lon,bimSunTzAt(st,days[k][0],'12:00'),days[k][0],bimPad2(i/60)+':00');")
rep(SH, "      if(bimAnimLive()&&A3D_ANIM.sunTime&&sunPt){ctx.textAlign='left';ctx.fillStyle='#ffe066';ctx.fillText(A3D_ANIM.sunTime,box[0]+6,box[1]+box[3]-9);}   /* __acad3dV170: the time, while it plays */",
    "      if(bimAnimLive()&&A3D_ANIM.sunTime&&sunPt){ctx.textAlign='left';ctx.fillStyle='#ffe066';ctx.fillText((A3D_ANIM.sunDate?bimSunDayText(A3D_ANIM.sunDate,true)+' ':'')+A3D_ANIM.sunTime,box[0]+6,box[1]+box[3]-9);}   /* __acad3dV170: the time, while it plays; __acad3dV171d: the date through the year */")

# ---- the diagrams' shadows: the place tried, the clock's date ----
ML = 'js/engine/site-analysis/model-layers.js'
rep(ML, """  function bimDgSun(date,time){
    var st=bimSunSettings();
    if(!bimSunNum(st.lat)||!bimSunNum(st.lon)||!bimSunNum(st.tz))return null;
    var r=bimSunCalc(st.lat,st.lon,st.tz,date,time);""", """  function bimDgSun(date,time){
    var st=bimSunStudy();   /* __acad3dV171d: a place tried; the zone's offset on the date */
    if(!bimSunNum(st.lat)||!bimSunNum(st.lon)||!bimSunNum(st.tz))return null;
    var r=bimSunCalc(st.lat,st.lon,bimSunTzAt(st,date,time),date,time);""")
rep(ML, "    var L=o.dg.g.live,mv=!!(day&&L&&A3D_ANIM.sunTime),dt=mv?bimSunSettings().date:(L&&L.date),sun;",
    "    var L=o.dg.g.live,mv=!!(day&&L&&A3D_ANIM.sunTime),dt=mv?bimSunStudy().date:(L&&L.date),sun;   /* __acad3dV171d: the clock's date through the year */")

# ---- the clock: through the day, or through the year ----
MO = 'js/engine/site-analysis/motion.js'
rep(MO, "  var A3D_ANIM={on:false,paused:false,t:0,last:0,painted:0,raf:0,playAt:0,sunTime:null,fr:null,can:false,c:null,dome:null,wired:false,key:'',frames:0};",
    """  var A3D_ANIM={on:false,paused:false,t:0,last:0,painted:0,raf:0,playAt:0,sunTime:null,fr:null,can:false,c:null,dome:null,wired:false,key:'',frames:0,
    sunMode:'day',sunDate:null};   /* __acad3dV171d: the sun through the day or through the year, and the year's date */
  var BIM_ANIM_YEAR={secs:36,hold:1.2};   /* __acad3dV171d: 1 January to 31 December, a day a step, held at the end */""")
rep(MO, """  function bimAnimSunTime(){
    var st=bimSunSettings(),B=BIM_ANIM.sun,r,a,b,p;
    if(!bimAnimSunOk())return null;
    r=bimSunCalc(st.lat,st.lon,st.tz,st.date,'12:00');""", """  function bimAnimSunTime(){
    var st=bimSunStudy(true),B=BIM_ANIM.sun,r,a,b,p;   /* __acad3dV171d: a place tried, a moment previewed */
    if(!bimAnimSunOk())return null;
    if(A3D_ANIM.sunMode==='year')return st.time;   /* __acad3dV171d: through the year, at the study's time */
    r=bimSunCalc(st.lat,st.lon,bimSunTzAt(st,st.date,'12:00'),st.date,'12:00');""")
rep(MO, """  /* the sun moving along its path on the sun paths' dome, with its time; it stands in for "the sun now" */""",
    """  /* __acad3dV171d: through the year: the date a day a step from 1 January, at the study's time, held at 31 December */
  function bimAnimSunDate(){
    var st,y,n,p,d,D;
    if(A3D_ANIM.sunMode!=='year'||!bimAnimSunOk())return null;
    st=bimSunStudy(true);y=+String(st.date).slice(0,4)||new Date().getFullYear();
    n=((y%4===0&&y%100!==0)||y%400===0)?366:365;
    p=bimAnimMod(A3D_ANIM.t,BIM_ANIM_YEAR.secs+BIM_ANIM_YEAR.hold);
    d=Math.min(n-1,Math.floor(n*Math.min(1,p/BIM_ANIM_YEAR.secs)));
    D=new Date(Date.UTC(y,0,1)+d*864e5);
    return D.getUTCFullYear()+'-'+bimPad2(D.getUTCMonth()+1)+'-'+bimPad2(D.getUTCDate());
  }
  /* the sun moving along its path on the sun paths' dome, with its time; it stands in for "the sun now" */""")
rep(MO, "      A3D_ANIM.paused=false;A3D_ANIM.c=null;A3D_ANIM.dome=null;A3D_ANIM.sunTime=bimAnimSunTime();",
    "      A3D_ANIM.paused=false;A3D_ANIM.c=null;A3D_ANIM.dome=null;A3D_ANIM.sunTime=bimAnimSunTime();A3D_ANIM.sunDate=bimAnimSunDate();")
rep(MO, "    A3D_ANIM.on=false;A3D_ANIM.paused=false;A3D_ANIM.t=0;A3D_ANIM.playAt=0;A3D_ANIM.sunTime=null;\n    bimAnimHalt();",
    "    A3D_ANIM.on=false;A3D_ANIM.paused=false;A3D_ANIM.t=0;A3D_ANIM.playAt=0;A3D_ANIM.sunTime=null;A3D_ANIM.sunDate=null;\n    bimAnimHalt();")
rep(MO, "      A3D_ANIM.painted=ts;A3D_ANIM.sunTime=bimAnimSunTime();",
    "      A3D_ANIM.painted=ts;A3D_ANIM.sunTime=bimAnimSunTime();A3D_ANIM.sunDate=bimAnimSunDate();")
rep(MO, "    if(!can&&moving){A3D_ANIM.on=false;A3D_ANIM.paused=false;A3D_ANIM.t=0;A3D_ANIM.playAt=0;A3D_ANIM.sunTime=null;bimAnimHalt();",
    "    if(!can&&moving){A3D_ANIM.on=false;A3D_ANIM.paused=false;A3D_ANIM.t=0;A3D_ANIM.playAt=0;A3D_ANIM.sunTime=null;A3D_ANIM.sunDate=null;bimAnimHalt();")
rep(MO, "    var tt=A3D_ANIM.on?'Pause, keeping this moment'+(A3D_ANIM.sunTime?' (the sun at '+A3D_ANIM.sunTime+')':''):",
    "    var tt=A3D_ANIM.on?'Pause, keeping this moment'+(A3D_ANIM.sunTime?' (the sun at '+A3D_ANIM.sunTime+(A3D_ANIM.sunDate?' on '+bimSunDayText(A3D_ANIM.sunDate):'')+')':''):")

# ---- the hooks' clock ----
rep('js/engine/testing/hooks-commands-site.js', "A3D_ANIM.c=null;A3D_ANIM.dome=null;A3D_ANIM.sunTime=bimAnimSunTime();paint();return window.__a3dAnim();};",
    "A3D_ANIM.c=null;A3D_ANIM.dome=null;A3D_ANIM.sunTime=bimAnimSunTime();A3D_ANIM.sunDate=bimAnimSunDate();paint();return window.__a3dAnim();};")

# ---- the climate board's sun chart: each date's offset ----
CB = 'js/engine/site-analysis/climate-board.js'
rep(CB, """    var S=380,cx=190,cy=190,R=150,y=new Date().getFullYear(),s,k;""",
    """    var S=380,cx=190,cy=190,R=150,y=new Date().getFullYear(),s,k,tzf=typeof tz==='function'?tz:function(){return tz;};   /* __acad3dV171d: an offset for each date */""")
rep(CB, "      for(m=0;m<=1440;m+=6){r=bimSunCalc(lat,lon,tz,y+'-'+dd[0],bimHHMM(m));",
    "      for(m=0;m<=1440;m+=6){r=bimSunCalc(lat,lon,tzf(y+'-'+dd[0]),y+'-'+dd[0],bimHHMM(m));")
rep(CB, "      for(m=0;m<1440;m+=60){r=bimSunCalc(lat,lon,tz,y+'-'+dd[0],bimHHMM(m));",
    "      for(m=0;m<1440;m+=60){r=bimSunCalc(lat,lon,tzf(y+'-'+dd[0]),y+'-'+dd[0],bimHHMM(m));")
rep(CB, "      var r0=bimSunCalc(lat,lon,tz,y+'-'+dd[0],'12:00'),",
    "      var r0=bimSunCalc(lat,lon,tzf(y+'-'+dd[0]),y+'-'+dd[0],'12:00'),")
rep(CB, "    var sun=bimClbSunSvg(lat,lon,bimSunNum(st.tz)?st.tz:Math.round(lon/15));",
    "    var sun=bimClbSunSvg(lat,lon,bimSunNum(st.tz)?function(d){return bimSunTzAt(st,d,'12:00');}:Math.round(lon/15));")

# ---- the date in words ----
rep(SP, "  function bimHHMM(m){m=((Math.round(m)%1440)+1440)%1440;return bimPad2(m/60)+':'+bimPad2(m%60);}",
    """  function bimHHMM(m){m=((Math.round(m)%1440)+1440)%1440;return bimPad2(m/60)+':'+bimPad2(m%60);}
  /* __acad3dV171d: a date in words, 21 June 2026 (short: 21 Jun) */
  var BIM_SUN_MON=['January','February','March','April','May','June','July','August','September','October','November','December'];
  function bimSunDayText(d,short){
    var m=/^(\\d{4})-(\\d{2})-(\\d{2})$/.exec(String(d||''));
    if(!m)return String(d||'');
    return (+m[3])+' '+(short?BIM_SUN_MON[+m[2]-1].slice(0,3):BIM_SUN_MON[+m[2]-1]+' '+m[1]);
  }""")

done()
