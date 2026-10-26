  /* ================= __acad3dV107: sun position =================
     The NOAA Solar Calculator equations (after Meeus, Astronomical Algorithms) as NOAA's
     spreadsheet gives them, its refraction approximation included. Checked against NREL's SPA
     (pvlib) at six places and dates: elevation within 0.01 deg, azimuth within 0.01 deg away from
     the zenith, sunrise, sunset and solar noon within half a minute. Time is local clock time with
     the UTC offset in force on that date (-5 EST, -4 EDT); noon, sunrise and sunset are minutes
     from local midnight; azimuth is degrees clockwise from TRUE north. */
  function bimSunCalc(lat,lon,tz,dateStr,timeStr){
    var dm=/^(\d{4})-(\d{2})-(\d{2})$/.exec(String(dateStr||'')),tm=/^(\d{1,2}):(\d{2})$/.exec(String(timeStr||''));
    if(!dm||!tm||!isFinite(lat)||!isFinite(lon)||!isFinite(tz))return null;
    var rad=Math.PI/180,deg=180/Math.PI;
    var mins=(+tm[1])*60+(+tm[2]);
    var jd=Date.UTC(+dm[1],+dm[2]-1,+dm[3],0,0,0)/86400000+2440587.5+mins/1440-tz/24;
    var G=(jd-2451545)/36525;
    var I=((280.46646+G*(36000.76983+G*0.0003032))%360+360)%360;
    var J=357.52911+G*(35999.05029-0.0001537*G);
    var K=0.016708634-G*(0.000042037+0.0000001267*G);
    var L=Math.sin(J*rad)*(1.914602-G*(0.004817+0.000014*G))+Math.sin(2*J*rad)*(0.019993-0.000101*G)+Math.sin(3*J*rad)*0.000289;
    var M=I+L;
    var P=M-0.00569-0.00478*Math.sin((125.04-1934.136*G)*rad);
    var Q=23+(26+((21.448-G*(46.815+G*(0.00059-G*0.001813))))/60)/60;
    var R=Q+0.00256*Math.cos((125.04-1934.136*G)*rad);
    var T=Math.asin(Math.sin(R*rad)*Math.sin(P*rad))*deg;
    var U=Math.tan(R*rad/2)*Math.tan(R*rad/2);
    var V=4*deg*(U*Math.sin(2*I*rad)-2*K*Math.sin(J*rad)+4*K*U*Math.sin(J*rad)*Math.cos(2*I*rad)-0.5*U*U*Math.sin(4*I*rad)-1.25*K*K*Math.sin(2*J*rad));
    var hc=Math.cos(90.833*rad)/(Math.cos(lat*rad)*Math.cos(T*rad))-Math.tan(lat*rad)*Math.tan(T*rad);
    var W=(hc>=-1&&hc<=1)?Math.acos(hc)*deg:null;
    var noon=720-4*lon-V+tz*60;
    var AB=(((mins+V+4*lon-60*tz)%1440)+1440)%1440;
    var AC=AB/4<0?AB/4+180:AB/4-180;
    var cz=Math.sin(lat*rad)*Math.sin(T*rad)+Math.cos(lat*rad)*Math.cos(T*rad)*Math.cos(AC*rad);
    var AD=Math.acos(Math.max(-1,Math.min(1,cz)))*deg;
    var AE=90-AD,te=Math.tan(AE*rad);
    var AF=(AE>85?0:(AE>5?58.1/te-0.07/Math.pow(te,3)+0.000086/Math.pow(te,5):(AE>-0.575?1735+AE*(-518.2+AE*(103.4+AE*(-12.79+AE*0.711))):-20.772/te)))/3600;
    var ca=(Math.sin(lat*rad)*Math.cos(AD*rad)-Math.sin(T*rad))/(Math.cos(lat*rad)*Math.sin(AD*rad));
    var ac=Math.acos(Math.max(-1,Math.min(1,ca)))*deg;
    var AH=AC>0?((ac+180)%360):(((540-ac)%360)+360)%360;
    return {elevation:AE+AF,geomElevation:AE,azimuth:AH,declination:T,eqTime:V,hourAngle:AC,
      noon:noon,sunrise:W===null?null:noon-4*W,sunset:W===null?null:noon+4*W,
      polar:W!==null?'':(hc>1?'night':'day')};
  }
  /* ================= __acad3dV171d: the sun's clock =================
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
  /* __acad3dV107: the site's place on the earth and the moment studied. No invented location: the
     latitude, longitude and UTC offset stay unset until the owner gives them, and everything that
     needs them says so. Date and time default to noon on June 21 of this year. */
  function bimSunNum(v){return typeof v==='number'&&isFinite(v);}
  function bimPad2(n){n=Math.floor(n);return (n<10?'0':'')+n;}
  function bimHHMM(m){m=((Math.round(m)%1440)+1440)%1440;return bimPad2(m/60)+':'+bimPad2(m%60);}
  /* __acad3dV171d: a date in words, 21 June 2026 (short: 21 Jun) */
  var BIM_SUN_MON=['January','February','March','April','May','June','July','August','September','October','November','December'];
  function bimSunDayText(d,short){
    var m=/^(\d{4})-(\d{2})-(\d{2})$/.exec(String(d||''));
    if(!m)return String(d||'');
    return (+m[3])+' '+(short?BIM_SUN_MON[+m[2]-1].slice(0,3):BIM_SUN_MON[+m[2]-1]+' '+m[1]);
  }
  function bimSunSettings(){
    var s=(A3D.site&&A3D.site.sun)||{};
    return {lat:s.lat,lon:s.lon,tz:s.tz,date:s.date||(new Date().getFullYear()+'-06-21'),time:s.time||'12:00'};
  }
  function bimSunNow(saved){
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
  }
  function bimSunText(sun){
    if(!sun)return '-';
    if(sun.missing)return 'set the '+sun.missing.join(', ');
    var t=sun.elevation>0?('altitude '+sun.elevation.toFixed(1)+', azimuth '+sun.azimuth.toFixed(1)+' deg'):'below the horizon';
    if(sun.polar==='day')t+='; no sunset (midnight sun)';
    else if(sun.polar==='night')t+='; no sunrise (polar night)';
    else t+='; rises '+bimHHMM(sun.sunrise)+', sets '+bimHHMM(sun.sunset);
    return t;
  }
  function bimSetSun(field,val){
    var v=String(val==null?'':val).replace(/^\s+|\s+$/g,''),n=parseFloat(v),nv=null,lim,m,nm,cur;
    if(!A3D.site||typeof A3D.site!=='object')A3D.site={name:'Site'};
    if(field==='lat'||field==='lon'||field==='tz'){
      lim=field==='lat'?[-90,90]:(field==='lon'?[-180,180]:[-12,14]);
      nm=field==='lat'?'Latitude':(field==='lon'?'Longitude':'UTC offset');
      if(v!==''&&(!isFinite(n)||n<lim[0]||n>lim[1])){a3dToast(nm+' must be a number from '+lim[0]+' to '+lim[1]);refreshProps();return false;}
      nv=v===''?null:n;
    }else if(field==='date'){
      m=/^(\d{4})-(\d{2})-(\d{2})$/.exec(v);
      if(v!==''&&(!m||+m[2]<1||+m[2]>12||new Date(Date.UTC(+m[1],+m[2]-1,+m[3])).getUTCDate()!==+m[3])){a3dToast('The sun date must be a real date, YYYY-MM-DD');refreshProps();return false;}
      nv=v===''?null:v;
    }else if(field==='time'){
      m=/^(\d{1,2}):(\d{2})(?::\d{2})?$/.exec(v);
      if(v!==''&&(!m||+m[1]>23||+m[2]>59)){a3dToast('The sun time must be HH:MM, from 00:00 to 23:59');refreshProps();return false;}
      nv=v===''?null:(bimPad2(+m[1])+':'+m[2]);
    }else if(field==='dst'){   /* __acad3dV171d: daylight saving, Off or Auto */
      nv=v==='auto'?'auto':null;
      if(nv&&!bimSunZone().zone){a3dToast('Daylight saving needs the site\'s time zone: Analyze site gets it with the climate');refreshProps();return false;}
    }else return false;
    cur=A3D.site.sun||{};
    if((cur[field]==null?null:cur[field])===nv)return true;
    pushUndo();
    A3D.site.sun=A3D.site.sun||{};
    if(nv===null)delete A3D.site.sun[field];else A3D.site.sun[field]=nv;
    if(field==='tz')delete A3D.site.sun.tzAuto;   /* __acad3dV171d: the owner's own offset, which the climate keeps */
    refreshProps();paint();saveSoon();
    a3dToast('Sun: '+bimSunText(bimSunNow(true)));
    return true;
  }
