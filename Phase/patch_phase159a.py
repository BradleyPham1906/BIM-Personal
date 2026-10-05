"""patch_phase159a.py -- V159: Site analysis SA2, climate and risk: the data and the findings.

From free sources, no keys, open to browsers (reference/research-climate-risk-presentation.md):
- Open-Meteo's historical weather (ERA5): the ten full years before this one, day by day, and the
  last full year hour by hour;
- Open-Meteo's air quality (CAMS): PM2.5 hour by hour over the last 92 days;
- the USGS earthquake catalogue: magnitude 4.5 and more within 100 km since 1976.

What is kept with the project is what was worked out, not the raw series:
- the twelve months' normals: the mean daily high and low, their 90th and 10th percentiles, the
  mean, rainfall, wet days, solar energy, and heating and cooling degree days on base 18 C;
- the Koppen-Geiger zone, by Beck et al. 2018's rules;
- the year's hourly temperatures, in whole degrees, for the heat map;
- the wind rose: 16 sectors, 5 speed bands, calm, for the year, winter and summer;
- the psychrometric density and the share of hours in the comfort zone;
- the daily PM2.5 means against the WHO guideline;
- the earthquakes, by distance and direction.

Each becomes a finding in the Site analysis (V158), under Climate or Environmental risk, with its
source and date. A source that fails is named, and what did come is kept. All of it is one undo step."""
NAME = 'patch_phase159a.py'
BASE = '3156aeb6f6e0beba05dbb6ed88630744288284ef1472c064a87c04c3ea44860b'
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def rep(old, new, n=1):
    global t
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: anchor count %d (want %d): %r' % (c, n, old[:80]))
    t = t.replace(old, new)


# ---- the Site analysis takes the climate's and the risks' findings ----
rep("""    if(lw.length)A.push({auto:'people.landuse',cat:'people',title:'Land use around',value:lw.join(', ')+rr,source:osm,date:od});
    return A;
  }""", """    if(lw.length)A.push({auto:'people.landuse',cat:'people',title:'Land use around',value:lw.join(', ')+rr,source:osm,date:od});
    return A.concat(bimClimAuto());   /* __acad3dV159: climate and risk */
  }""")
rep("""  function bimSaFill(){""", """  function bimSaFill(quiet){   /* __acad3dV159: quiet when the climate fetch fills it */""")
rep("""    a3dToast('Site analysis: '+(A.length?bimSaN(add,'finding')+' added, '+upd+' updated'+(del?', '+del+' gone':'')+' from the model':'nothing known yet: place the site and get its context first'));""",
    """    if(!quiet)a3dToast('Site analysis: '+(A.length?bimSaN(add,'finding')+' added, '+upd+' updated'+(del?', '+del+' gone':'')+' from the model':'nothing known yet: place the site and get its context first'));""")

ENGINE = r"""
  /* ================= __acad3dV159: Site analysis SA2, climate and risk: the data =================
     reference/research-climate-risk-presentation.md. Fetched only when asked; what is worked out
     is kept with the project (A3D.site.climate, A3D.site.risk), so the board opens offline. */
  var BIM_CLIM_ARCHIVE='https://archive-api.open-meteo.com/v1/archive';
  var BIM_CLIM_AQ='https://air-quality-api.open-meteo.com/v1/air-quality';
  var BIM_CLIM_EQ='https://earthquake.usgs.gov/fdsnws/event/1/query';
  var BIM_CLIM_YEARS=10,BIM_CLIM_BASE=18,BIM_CLIM_CALM=0.5,BIM_CLIM_WIND_BINS=[0.5,2,4,6,8];
  var BIM_CLIM_EQ_KM=100,BIM_CLIM_EQ_MIN=4.5,BIM_CLIM_EQ_SINCE='1976-01-01';
  var BIM_CLIM_WHO24=15,BIM_CLIM_WHO_YEAR=5,BIM_CLIM_COMFORT={t0:20,t1:27,rh0:20,rh1:80};
  var BIM_CLIM_DIRS=['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW'];
  var BIM_CLIM_MONTHS=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  var BIM_CLIM_MONTH_NAMES=['January','February','March','April','May','June','July','August','September','October','November','December'];
  var A3D_CLIM={busy:false};
  /* the Koppen-Geiger zones in words */
  var BIM_KOPPEN={Af:'Tropical rainforest',Am:'Tropical monsoon',Aw:'Tropical savanna, dry winter',As:'Tropical savanna, dry summer',
    BWh:'Hot desert',BWk:'Cold desert',BSh:'Hot semi-arid steppe',BSk:'Cold semi-arid steppe',
    Csa:'Hot-summer Mediterranean',Csb:'Warm-summer Mediterranean',Csc:'Cold-summer Mediterranean',
    Cwa:'Monsoon-influenced humid subtropical',Cwb:'Subtropical highland, dry winter',Cwc:'Cold subtropical highland, dry winter',
    Cfa:'Humid subtropical',Cfb:'Temperate oceanic',Cfc:'Subpolar oceanic',
    Dsa:'Hot-summer continental, dry summer',Dsb:'Warm-summer continental, dry summer',Dsc:'Subarctic, dry summer',Dsd:'Extremely cold subarctic, dry summer',
    Dwa:'Hot-summer continental, dry winter',Dwb:'Warm-summer continental, dry winter',Dwc:'Subarctic, dry winter',Dwd:'Extremely cold subarctic, dry winter',
    Dfa:'Hot-summer humid continental',Dfb:'Warm-summer humid continental',Dfc:'Subarctic',Dfd:'Extremely cold subarctic',
    ET:'Tundra',EF:'Ice cap'};
  function bimClimYears(){var y1=new Date().getFullYear()-1;return [y1-BIM_CLIM_YEARS+1,y1];}
  function bimClimQs(o){var k,s=[];for(k in o)if(o.hasOwnProperty(k))s.push(k+'='+encodeURIComponent(o[k]));return s.join('&');}
  function bimClimUrls(lat,lon){
    var y=bimClimYears(),ll={latitude:lat.toFixed(4),longitude:lon.toFixed(4)},o,k;
    function w(extra){o={};for(k in ll)o[k]=ll[k];for(k in extra)if(extra.hasOwnProperty(k))o[k]=extra[k];return o;}
    return {
      daily:BIM_CLIM_ARCHIVE+'?'+bimClimQs(w({start_date:y[0]+'-01-01',end_date:y[1]+'-12-31',
        daily:'temperature_2m_max,temperature_2m_min,temperature_2m_mean,precipitation_sum,shortwave_radiation_sum',timezone:'auto'})),
      hourly:BIM_CLIM_ARCHIVE+'?'+bimClimQs(w({start_date:y[1]+'-01-01',end_date:y[1]+'-12-31',
        hourly:'temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m',wind_speed_unit:'ms',timezone:'auto'})),
      aq:BIM_CLIM_AQ+'?'+bimClimQs(w({hourly:'pm2_5',past_days:92,forecast_days:0,timezone:'auto'})),
      eq:BIM_CLIM_EQ+'?'+bimClimQs({format:'geojson',latitude:lat.toFixed(4),longitude:lon.toFixed(4),maxradiuskm:BIM_CLIM_EQ_KM,
        minmagnitude:BIM_CLIM_EQ_MIN,starttime:BIM_CLIM_EQ_SINCE,orderby:'magnitude',limit:300})
    };
  }
  /* one source: its JSON, or why not, by its host's name */
  function bimClimGet(url){
    return fetch(url).then(function(r){if(!r.ok)throw {http:r.status};return r.text();}).then(function(tx){
      var js;try{js=JSON.parse(tx);}catch(eJ){throw {bad:true};}
      if(!js||typeof js!=='object'||js.error)throw {bad:true};
      return {ok:true,js:js};
    }).then(null,function(e){return {ok:false,err:bimCtxErr(bimMapHost(url),e)};});
  }
  function bimClimNum(v){return typeof v==='number'&&isFinite(v);}
  function bimClimPct(a,p){   /* the p-th percentile, linear between ranks */
    if(!a.length)return null;
    var s=a.slice().sort(function(x,y){return x-y;}),r=(s.length-1)*p,lo=Math.floor(r),hi=Math.ceil(r);
    return s[lo]+(s[hi]-s[lo])*(r-lo);
  }
  function bimClimR(v,d){var k=Math.pow(10,d||1);return Math.round(v*k)/k;}
  /* ten years of days, to the twelve months' normals */
  function bimClimDaily(js){
    var d=js&&js.daily;
    if(!d||!Array.isArray(d.time)||!d.time.length)return null;
    var M=[],i,m,y,yrs={},ny=0,tx,tn,tm,p,sw,days={},tmaxA=null,tminA=null;
    for(m=0;m<12;m++)M.push({tx:[],tn:[],tm:[],ptot:{},pwet:{},sw:[],hdd:{},cdd:{}});
    for(i=0;i<d.time.length;i++){
      var dm=/^(\d{4})-(\d{2})-(\d{2})/.exec(String(d.time[i]));if(!dm)continue;
      y=+dm[1];m=+dm[2]-1;
      tx=(d.temperature_2m_max||[])[i];tn=(d.temperature_2m_min||[])[i];tm=(d.temperature_2m_mean||[])[i];
      p=(d.precipitation_sum||[])[i];sw=(d.shortwave_radiation_sum||[])[i];
      if(!yrs[y]){yrs[y]=1;ny++;}
      var K=M[m];
      if(bimClimNum(tx)){K.tx.push(tx);if(tmaxA===null||tx>tmaxA.v)tmaxA={v:tx,d:d.time[i]};}
      if(bimClimNum(tn)){K.tn.push(tn);if(tminA===null||tn<tminA.v)tminA={v:tn,d:d.time[i]};}
      if(!bimClimNum(tm)&&bimClimNum(tx)&&bimClimNum(tn))tm=(tx+tn)/2;
      if(bimClimNum(tm))K.tm.push(tm);
      if(bimClimNum(p)){K.ptot[y]=(K.ptot[y]||0)+p;if(p>=1)K.pwet[y]=(K.pwet[y]||0)+1;else if(K.pwet[y]===undefined)K.pwet[y]=0;}
      if(bimClimNum(sw))K.sw.push(sw/3.6);   /* MJ/m2 to kWh/m2 */
      if(bimClimNum(tx)&&bimClimNum(tn)){var dmn=(tx+tn)/2;   /* the degree-day mean, (max + min) / 2 */
        K.hdd[y]=(K.hdd[y]||0)+Math.max(0,BIM_CLIM_BASE-dmn);K.cdd[y]=(K.cdd[y]||0)+Math.max(0,dmn-BIM_CLIM_BASE);}
    }
    function mean(a){var s=0,k;for(k=0;k<a.length;k++)s+=a[k];return a.length?s/a.length:null;}
    function ymean(o){var s=0,n=0,k;for(k in o)if(o.hasOwnProperty(k)){s+=o[k];n++;}return n?s/n:null;}
    var out=[],A={t:0,p:0,hdd:0,cdd:0,sw:0,wet:0},DIM=[31,28.25,31,30,31,30,31,31,30,31,30,31],ok=true;
    for(m=0;m<12;m++){
      var K2=M[m],r={tx:mean(K2.tx),tn:mean(K2.tn),tm:mean(K2.tm),tx90:bimClimPct(K2.tx,0.9),tn10:bimClimPct(K2.tn,0.1),
        p:ymean(K2.ptot),wet:ymean(K2.pwet),sw:mean(K2.sw),hdd:ymean(K2.hdd),cdd:ymean(K2.cdd)},k2;
      for(k2 in r)if(r.hasOwnProperty(k2)&&r[k2]!==null)r[k2]=bimClimR(r[k2],k2==='sw'?2:1);
      if(r.tm===null||r.p===null)ok=false;
      out.push(r);
      A.t+=r.tm||0;A.p+=r.p||0;A.hdd+=r.hdd||0;A.cdd+=r.cdd||0;A.sw+=(r.sw||0)*DIM[m];A.wet+=r.wet||0;
    }
    if(!ok)return null;
    A.t=bimClimR(A.t/12,1);A.p=Math.round(A.p);A.hdd=Math.round(A.hdd);A.cdd=Math.round(A.cdd);A.sw=Math.round(A.sw);A.wet=Math.round(A.wet);
    A.tmax=tmaxA;A.tmin=tminA;
    return {months:out,annual:A,years:ny};
  }
  /* Koppen-Geiger from the monthly means and totals (Beck et al. 2018, after Peel et al. 2007) */
  function bimKoppen(T,P,lat){
    var i,MAT=0,MAP=0,Tc=1e9,Th=-1e9,n10=0;
    for(i=0;i<12;i++){MAT+=T[i]/12;MAP+=P[i];if(T[i]<Tc)Tc=T[i];if(T[i]>Th)Th=T[i];if(T[i]>=10)n10++;}
    var sum=lat>=0?[3,4,5,6,7,8]:[9,10,11,0,1,2],win=lat>=0?[9,10,11,0,1,2]:[3,4,5,6,7,8];
    function pick(L,f){var v=f==='min'?1e9:-1e9;L.forEach(function(j){v=f==='min'?Math.min(v,P[j]):Math.max(v,P[j]);});return v;}
    var Ps=0,Pw=0;sum.forEach(function(j){Ps+=P[j];});win.forEach(function(j){Pw+=P[j];});
    var Psdry=pick(sum,'min'),Pswet=pick(sum,'max'),Pwdry=pick(win,'min'),Pwwet=pick(win,'max'),Pdry=Math.min.apply(null,P);
    var Pth=Pw>=0.7*MAP?2*MAT:(Ps>=0.7*MAP?2*MAT+28:2*MAT+14);
    var c;
    if(Th<=10)c=Th>0?'ET':'EF';   /* polar first: a cold ice cap is not a desert */
    else if(MAP<10*Pth)c='B'+(MAP<5*Pth?'W':'S')+(MAT>=18?'h':'k');
    else if(Tc>=18)c=Pdry>=60?'Af':(Pdry>=100-MAP/25?'Am':(Psdry<Pwdry?'As':'Aw'));
    else{
      var g=Tc>0?'C':'D',s2=(Psdry<40&&Psdry<Pwwet/3)?'s':(Pwdry<Pswet/10?'w':'f');
      var t3=Th>=22?'a':(n10>=4?'b':((g==='D'&&Tc<-38)?'d':'c'));
      c=g+s2+t3;
    }
    return {code:c,name:BIM_KOPPEN[c]||c,mat:bimClimR(MAT,1),map:Math.round(MAP),pth:bimClimR(Pth,1)};
  }
  /* the saturation pressure (Pa) and the humidity ratio (g/kg), at sea-level pressure */
  function bimPsat(T){return 610.94*Math.exp(17.625*T/(T+243.04));}
  function bimHumRatio(T,RH){var pv=RH/100*bimPsat(T);return 1000*0.622*pv/(101325-pv);}
  /* a year of hours: the heat map, the wind roses, the psychrometric density, comfort */
  function bimClimHourly(js,lat){
    var h=js&&js.hourly;
    if(!h||!Array.isArray(h.time)||h.time.length<24*28)return null;
    var n=h.time.length,i,T=h.temperature_2m||[],RH=h.relative_humidity_2m||[],WS=h.wind_speed_10m||[],WD=h.wind_direction_10m||[];
    var heat=[],year=+String(h.time[0]).slice(0,4),nb=BIM_CLIM_WIND_BINS.length;
    function rose(){var R=[],k;for(k=0;k<16;k++)R.push([0,0,0,0,0].slice(0,nb));return {c:R,calm:0,n:0,ws:0};}
    var RS={year:rose(),winter:rose(),summer:rose()},rhm=[],rhn=[],psy={},inC=0,nC=0,cold=0,hot=0,m;
    for(m=0;m<12;m++){rhm.push(0);rhn.push(0);}
    var win=lat>=0?[11,0,1]:[5,6,7],sum=lat>=0?[5,6,7]:[11,0,1];
    for(i=0;i<n;i++){
      var mm=+String(h.time[i]).slice(5,7)-1,t=T[i],rh=RH[i],ws=WS[i],wd=WD[i];
      heat.push(bimClimNum(t)?Math.round(t):null);
      if(bimClimNum(rh)&&mm>=0&&mm<12){rhm[mm]+=rh;rhn[mm]++;}
      if(bimClimNum(ws)&&bimClimNum(wd)){
        var L=[RS.year];if(win.indexOf(mm)>=0)L.push(RS.winter);if(sum.indexOf(mm)>=0)L.push(RS.summer);
        var sec=Math.round(((wd%360)+360)%360/22.5)%16,b=-1,k;
        if(ws>=BIM_CLIM_CALM)for(k=nb-1;k>=0;k--)if(ws>=BIM_CLIM_WIND_BINS[k]){b=k;break;}
        L.forEach(function(R){R.n++;R.ws+=ws;if(b<0)R.calm++;else R.c[sec][b]++;});
      }
      if(bimClimNum(t)&&bimClimNum(rh)){
        var w=bimHumRatio(t,rh),key=Math.floor(t)+'|'+Math.floor(w);
        psy[key]=(psy[key]||0)+1;nC++;
        if(t>=BIM_CLIM_COMFORT.t0&&t<=BIM_CLIM_COMFORT.t1&&rh>=BIM_CLIM_COMFORT.rh0&&rh<=BIM_CLIM_COMFORT.rh1)inC++;
        else if(t<BIM_CLIM_COMFORT.t0)cold++;else hot++;
      }
    }
    function fin(R){
      var o={pct:[],calm:R.n?bimClimR(100*R.calm/R.n,1):0,n:R.n,mean:R.n?bimClimR(R.ws/R.n,1):null,prev:null,prevPct:0},k,j,tot;
      for(k=0;k<16;k++){o.pct.push(R.c[k].map(function(v){return R.n?bimClimR(100*v/R.n,2):0;}));
        tot=0;for(j=0;j<nb;j++)tot+=R.c[k][j];tot=R.n?100*tot/R.n:0;if(tot>o.prevPct){o.prevPct=bimClimR(tot,1);o.prev=k;}}
      /* the strongest: the sector with the largest share of the two top bands */
      var best=-1,bv=0;for(k=0;k<16;k++){var sv=R.c[k][nb-1]+R.c[k][nb-2];if(sv>bv){bv=sv;best=k;}}
      o.strong=best;return o;
    }
    return {year:year,heat:heat,start:String(h.time[0]).slice(0,10),
      wind:{bins:BIM_CLIM_WIND_BINS.slice(),year:fin(RS.year),winter:fin(RS.winter),summer:fin(RS.summer)},
      rh:rhm.map(function(v,j){return rhn[j]?Math.round(v/rhn[j]):null;}),
      psy:psy,comfort:nC?{inside:bimClimR(100*inC/nC,1),cold:bimClimR(100*cold/nC,1),hot:bimClimR(100*hot/nC,1),hours:nC}:null};
  }
  /* 92 days of hours, to daily means against the WHO 24-hour guideline */
  function bimClimAq(js){
    var h=js&&js.hourly;
    if(!h||!Array.isArray(h.time)||!h.pm2_5)return null;
    var by={},order=[],i;
    for(i=0;i<h.time.length;i++){
      var v=h.pm2_5[i],d=String(h.time[i]).slice(0,10);
      if(!bimClimNum(v))continue;
      if(!by[d]){by[d]={s:0,n:0};order.push(d);}
      by[d].s+=v;by[d].n++;
    }
    var days=[],s=0,mx=null,over=0;
    order.forEach(function(d){if(by[d].n<12)return;var v=bimClimR(by[d].s/by[d].n,1);days.push({d:d,v:v});s+=v;if(mx===null||v>mx.v)mx={d:d,v:v};if(v>BIM_CLIM_WHO24)over++;});
    if(!days.length)return null;
    var mean=bimClimR(s/days.length,1),st;
    if(mean>35)st='critical';else if(mean>BIM_CLIM_WHO24||over/days.length>0.3)st='serious';else if(mean>BIM_CLIM_WHO_YEAR||over>0)st='warning';else st='good';
    return {days:days,mean:mean,max:mx,over:over,status:st,from:days[0].d,to:days[days.length-1].d};
  }
  function bimClimKm(lat1,lon1,lat2,lon2){
    var r=Math.PI/180,dl=(lat2-lat1)*r,dn=(lon2-lon1)*r,a=Math.sin(dl/2)*Math.sin(dl/2)+Math.cos(lat1*r)*Math.cos(lat2*r)*Math.sin(dn/2)*Math.sin(dn/2);
    return 6371.0088*2*Math.atan2(Math.sqrt(a),Math.sqrt(1-a));
  }
  function bimClimAz(lat1,lon1,lat2,lon2){
    var r=Math.PI/180,y=Math.sin((lon2-lon1)*r)*Math.cos(lat2*r),x=Math.cos(lat1*r)*Math.sin(lat2*r)-Math.sin(lat1*r)*Math.cos(lat2*r)*Math.cos((lon2-lon1)*r);
    return ((Math.atan2(y,x)/r)+360)%360;
  }
  function bimClimDir(az){return BIM_CLIM_DIRS[Math.round(((az%360)+360)%360/22.5)%16];}
  function bimClimEq(js,lat,lon){
    if(!js||!Array.isArray(js.features))return null;
    var E=[];
    js.features.forEach(function(f){
      var p=f&&f.properties||{},g=f&&f.geometry&&f.geometry.coordinates;
      if(!g||!bimClimNum(p.mag)||!bimClimNum(g[0])||!bimClimNum(g[1]))return;
      var km=bimClimKm(lat,lon,g[1],g[0]);
      if(km>BIM_CLIM_EQ_KM+0.5)return;
      E.push({m:bimClimR(p.mag,1),t:bimClimNum(p.time)?new Date(p.time).toISOString().slice(0,10):'',km:bimClimR(km,1),
        az:Math.round(bimClimAz(lat,lon,g[1],g[0])),depth:bimClimNum(g[2])?bimClimR(g[2],1):null,place:String(p.place||'').slice(0,120)});
    });
    E.sort(function(a,b){return b.m-a.m||a.km-b.km;});
    var st='good',big=E[0]||null;
    E.forEach(function(e){
      var s=(e.m>=6&&e.km<=50)?3:((e.m>=6)||(e.m>=5&&e.km<=50))?2:1;
      var cur={good:0,warning:1,serious:2,critical:3}[st];
      if(s>cur)st=['good','warning','serious','critical'][s];
    });
    return {events:E.slice(0,150),count:E.length,max:big,status:st,radius:BIM_CLIM_EQ_KM,minmag:BIM_CLIM_EQ_MIN,since:BIM_CLIM_EQ_SINCE};
  }
  /* CLIMATEGET: the four sources at once; what comes is placed in one undo step */
  function bimClimFetch(){
    if(A3D_CLIM.busy){a3dToast('The climate and risk data are already on their way');return null;}
    var st=bimSunSettings();
    if(!bimSunNum(st.lat)||!bimSunNum(st.lon)){a3dToast('Set the site latitude and longitude first (Properties, Site, Location): the climate is the site\'s');return null;}
    if(typeof fetch!=='function'){a3dToast('This browser cannot fetch the climate');return null;}
    var U=bimClimUrls(st.lat,st.lon),y=bimClimYears();
    A3D_CLIM.busy=true;
    a3dToast('Getting the climate ('+y[0]+' to '+y[1]+'), air quality and earthquakes for the site ...');
    return Promise.all([bimClimGet(U.daily),bimClimGet(U.hourly),bimClimGet(U.aq),bimClimGet(U.eq)]).then(function(R){
      A3D_CLIM.busy=false;
      try{return bimClimApply(st.lat,st.lon,R);}
      catch(eA){console.warn('[BIM] climate',eA);a3dToast('The climate could not be worked out - see the console');return {error:String(eA)};}
    },function(e){A3D_CLIM.busy=false;return {error:String(e)};});
  }
  function bimClimApply(lat,lon,R){
    var today=bimSaToday(),bad=[],D=null,Hh=null,Q=null,E=null,y=bimClimYears();
    if(R[0].ok)D=bimClimDaily(R[0].js);else bad.push(R[0].err);
    if(R[0].ok&&!D)bad.push('the daily climate came back empty');
    if(R[1].ok)Hh=bimClimHourly(R[1].js,lat);else bad.push(R[1].err);
    if(R[2].ok)Q=bimClimAq(R[2].js);else bad.push(R[2].err);
    if(R[3].ok)E=bimClimEq(R[3].js,lat,lon);else bad.push(R[3].err);
    if(!D&&!Hh&&!Q&&!E){a3dToast('No climate or risk data: '+bad.join('; '));return {error:bad.join('; ')};}
    pushUndo();
    undoSuspend=true;
    try{
      A3D.site=A3D.site||{};
      var C=A3D.site.climate&&A3D.site.climate.lat===lat&&A3D.site.climate.lon===lon?A3D.site.climate:{};
      C.lat=lat;C.lon=lon;C.fetched=today;C.errors=bad.slice();
      if(D){C.normals=D;C.period=[y[0],y[1]];C.koppen=bimKoppen(D.months.map(function(m){return m.tm;}),D.months.map(function(m){return m.p;}),lat);
        C.src='ERA5 reanalysis (ECMWF), via Open-Meteo';}
      if(Hh)C.hourly=Hh;
      A3D.site.climate=C;
      var K=A3D.site.risk&&A3D.site.risk.lat===lat&&A3D.site.risk.lon===lon?A3D.site.risk:{};
      K.lat=lat;K.lon=lon;K.fetched=today;
      if(Q){K.air=Q;K.airSrc='CAMS (Copernicus), via Open-Meteo';}
      if(E){K.quakes=E;K.quakeSrc='USGS earthquake catalogue';}
      A3D.site.risk=K;
      bimSaFill(true);
    }finally{undoSuspend=false;}
    refreshProps();paint();saveSoon();
    if(typeof bimSaRefresh==='function')bimSaRefresh(true);
    if(typeof bimClbRefresh==='function')bimClbRefresh();
    var got=[];if(D)got.push('the climate');if(Hh)got.push('a year of hours');if(Q)got.push('air quality');if(E)got.push(E.count+' earthquake'+(E.count===1?'':'s'));
    a3dToast('Climate and risk: '+got.join(', ')+(bad.length?'. Not available: '+bad.join('; '):''));
    return {climate:!!D,hourly:!!Hh,air:!!Q,quakes:E?E.count:null,errors:bad};
  }
  /* ---- the findings, for the Site analysis ---- */
  function bimClimFmt(v,d){return (v<0?'−':'')+Math.abs(v).toFixed(d===undefined?1:d);}
  function bimClimInt(v){return String(Math.round(v)).replace(/\B(?=(\d{3})+(?!\d))/g,',');}
  function bimClimAuto(){
    var A=[],C=A3D.site&&A3D.site.climate,K=A3D.site&&A3D.site.risk,N=C&&C.normals,src,dt;
    if(N){
      var M=N.months,a=N.annual,iw=0,ic=0,ip=0,j;
      for(j=1;j<12;j++){if(M[j].tx>M[iw].tx)iw=j;if(M[j].tn<M[ic].tn)ic=j;if(M[j].p>M[ip].p)ip=j;}
      src=C.src+', '+C.period[0]+'–'+C.period[1];dt=C.fetched;
      if(C.koppen)A.push({auto:'climate.koppen',cat:'climate',title:'Climate zone',value:C.koppen.code+': '+C.koppen.name+' (Köppen–Geiger)',source:'Köppen–Geiger (Beck et al. 2018 rules) from '+src,date:dt});
      A.push({auto:'climate.temp',cat:'climate',title:'Temperature',value:'Annual mean '+bimClimFmt(a.t)+' °C. '+BIM_CLIM_MONTH_NAMES[iw]+' is warmest (mean high '+bimClimFmt(M[iw].tx)+' °C), '+
        BIM_CLIM_MONTH_NAMES[ic]+' coldest (mean low '+bimClimFmt(M[ic].tn)+' °C); extremes '+bimClimFmt(a.tmax.v)+' and '+bimClimFmt(a.tmin.v)+' °C.',
        cls:(M[iw].tx>=32||M[ic].tn<=-10)?'constraint':'neutral',sev:(M[iw].tx>=35||M[ic].tn<=-20)?2:1,source:src,date:dt});
      A.push({auto:'climate.rain',cat:'climate',title:'Rainfall',value:bimClimInt(a.p)+' mm a year on '+a.wet+' wet days (1 mm or more); '+BIM_CLIM_MONTH_NAMES[ip]+' is wettest ('+Math.round(M[ip].p)+' mm).',
        cls:M[ip].p>=250?'constraint':'neutral',sev:1,source:src,date:dt});
      A.push({auto:'climate.degreedays',cat:'climate',title:'Heating and cooling',value:bimClimInt(a.hdd)+' heating and '+bimClimInt(a.cdd)+' cooling degree days a year (base '+BIM_CLIM_BASE+' °C): '+
        (a.hdd>2*a.cdd?'heating dominates':(a.cdd>2*a.hdd?'cooling dominates':'both matter')),source:src,date:dt});
      A.push({auto:'climate.solar',cat:'climate',title:'Solar energy',value:bimClimInt(a.sw)+' kWh/m² a year on the horizontal, '+bimClimFmt(Math.max.apply(null,M.map(function(m){return m.sw;})),1)+' kWh/m² a day at its most',
        cls:a.sw>=1400?'opportunity':'neutral',source:src,date:dt});
    }
    var Hh=C&&C.hourly;
    if(Hh&&Hh.wind&&Hh.wind.year.prev!==null){
      var W=Hh.wind.year;
      A.push({auto:'climate.wind',cat:'climate',title:'Wind',value:'Prevailing from the '+BIM_CLIM_DIRS[W.prev]+' ('+bimClimFmt(W.prevPct,0)+'% of hours), mean '+bimClimFmt(W.mean)+' m/s; the strongest from the '+
        BIM_CLIM_DIRS[W.strong>=0?W.strong:W.prev]+'; calm '+bimClimFmt(W.calm,0)+'% of hours ('+Hh.year+')',source:C.src+', '+Hh.year+' hourly',date:C.fetched});
    }
    if(Hh&&Hh.comfort){
      var cf=Hh.comfort;
      A.push({auto:'climate.comfort',cat:'climate',title:'Outdoor comfort',value:bimClimFmt(cf.inside,0)+'% of the year\'s hours in the comfort zone ('+BIM_CLIM_COMFORT.t0+'–'+BIM_CLIM_COMFORT.t1+' °C, '+
        BIM_CLIM_COMFORT.rh0+'–'+BIM_CLIM_COMFORT.rh1+'% RH); '+bimClimFmt(cf.cold,0)+'% too cool, '+bimClimFmt(cf.hot,0)+'% too hot or humid',
        cls:cf.inside<15?'constraint':(cf.inside>=40?'opportunity':'neutral'),sev:1,source:C.src+', '+Hh.year+' hourly',date:C.fetched});
    }
    var STC={good:['neutral',1],warning:['constraint',1],serious:['constraint',2],critical:['redflag',3]};
    if(K&&K.air){
      var Q=K.air,s1=STC[Q.status];
      A.push({auto:'risk.air',cat:'risk',title:'Air quality (PM2.5)',value:'Mean '+bimClimFmt(Q.mean)+' µg/m³ over '+Q.days.length+' days to '+Q.to+'; '+Q.over+' day'+(Q.over===1?'':'s')+' above the WHO 24-hour guideline ('+BIM_CLIM_WHO24+' µg/m³)',
        cls:s1[0],sev:s1[1],source:K.airSrc+', '+Q.from+' to '+Q.to,date:K.fetched});
    }
    if(K&&K.quakes){
      var E=K.quakes,s2=STC[E.status],b=E.max;
      A.push({auto:'risk.seismic',cat:'risk',title:'Earthquakes',value:E.count?(E.count+' earthquake'+(E.count===1?'':'s')+' of M'+E.minmag+' or more within '+E.radius+' km since '+E.since.slice(0,4)+'; the largest M'+b.m.toFixed(1)+' ('+b.t.slice(0,4)+'), '+Math.round(b.km)+' km '+bimClimDir(b.az)):
        'No earthquake of M'+E.minmag+' or more within '+E.radius+' km since '+E.since.slice(0,4),
        cls:s2[0],sev:s2[1],source:K.quakeSrc,date:K.fetched});
    }
    return A;
  }"""

rep("""  /* ---- edits: each one undo step ---- */
  function bimSaAdd(cat,f){""", ENGINE + """
  /* ---- edits: each one undo step ---- */
  function bimSaAdd(cat,f){""")

# ---- commands ----
rep("""    ['SAFILL',['SITEANALYSISFILL','SAFROMMODEL'],'safill',""",
    """    ['CLIMATEGET',['GETCLIMATE','WEATHERDATA','CLIMATEDATA'],'climateget','Get the site\\'s climate (ten years of ERA5), air quality (PM2.5) and earthquakes within 100 km, from free open sources'],   /* __acad3dV159 */
    ['SAFILL',['SITEANALYSISFILL','SAFROMMODEL'],'safill',""")
rep("""    safill:function(){bimShellSetTab('site');bimSaFill();},""",
    """    safill:function(){bimShellSetTab('site');bimSaFill();},
    climateget:function(){bimClimFetch();},                      /* __acad3dV159 */""")

# ---- hooks, marker, version ----
rep("""  window.__acad3dV158='layergroups,""", """  window.__acad3dV159='climatefetch,normals,koppen,degreedays,hourly,windrose,psychrometric,comfort,airquality,earthquakes,climatefindings,board,figures,kpis,tables,print';
  window.__a3dClimUrls=function(lat,lon){return bimClimUrls(lat,lon);};
  window.__a3dClimFetch=function(){return bimClimFetch();};
  window.__a3dClimBusy=function(){return !!A3D_CLIM.busy;};
  window.__a3dClim=function(){return JSON.parse(JSON.stringify({climate:(A3D.site&&A3D.site.climate)||null,risk:(A3D.site&&A3D.site.risk)||null}));};
  window.__a3dKoppen=function(T,P,lat){return bimKoppen(T,P,lat);};
  window.__a3dHumRatio=function(T,RH){return bimHumRatio(T,RH);};
  window.__a3dClimAuto=function(){return bimClimAuto();};
  window.__acad3dV158='layergroups,""")
rep("""  var BIM_APP_VERSION={v:'V158',date:'2026-10-04'};   /* __acad3dV158 */""",
    """  var BIM_APP_VERSION={v:'V159',date:'2026-10-05'};   /* __acad3dV159 */""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
