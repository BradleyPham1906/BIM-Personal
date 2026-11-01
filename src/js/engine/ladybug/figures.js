  /* ================= __acad3dV172b: the Ladybug analyses as board figures =================
     reference/research-ladybug-weather-comfort.md, 9. Each figure draws a kept result in the board's own style
     (bimClbCard, its colours and ticks), names Ladybug and its version as the method and the weather it read, and says
     what it means in its title. Nothing is computed here that Ladybug did not give. */
  var BIM_UTCI_NAMES=['Extreme cold stress','Very strong cold stress','Strong cold stress','Moderate cold stress','Slight cold stress',
    'No thermal stress','Moderate heat stress','Strong heat stress','Very strong heat stress','Extreme heat stress'];
  var BIM_UTCI_RANGE=['below −40 °C','−40 to −27 °C','−27 to −13 °C','−13 to 0 °C','0 to 9 °C','9 to 26 °C','26 to 32 °C','32 to 38 °C','38 to 46 °C','above 46 °C'];
  var BIM_UTCI_COL=['#104281','#1c5cab','#2a78d6','#6da7ec','#b7d3f6','var(--hn)','#ec8f86','#e34948','#b8302f','#7d1f1f'];
  var BIM_LB_COND={sun_wind:'In the sun, in the wind',shade_wind:'In the shade, in the wind',sun_still:'In the sun, in still air',shade_still:'In the shade, in still air'};
  var BIM_LB_STRAT_COL=['var(--s2)','#8e6bbf','#2f9e8f','#d08a1c','#c2463c'];
  /* the method line under every Ladybug figure */
  function bimLbSrcLine(R){
    var v=(R&&R.v&&R.v.ladybug)||{},s=bimLbSrcKept();
    return 'Ladybug Tools (ladybug-core '+(v['ladybug-core']||'?')+', ladybug-comfort '+(v['ladybug-comfort']||'?')+', in Pyodide '+((R&&R.v&&R.v.pyodide)||'?')+'), on '+bimLbSrcWords(s)+
      (R&&R.stale?'; the weather has changed since: run it again':'');
  }
  /* runs of classes back to the hours */
  function bimLbUnRle(t){
    var out=[],parts=String(t||'').split(','),i,k,n,j;
    for(i=0;i<parts.length;i++){
      var p=parts[i].split(':');k=+p[0];n=+p[1];
      if(!(k>=0&&k<=9)||!(n>0))return null;
      for(j=0;j<n;j++)out.push(k);
    }
    return out;
  }
  /* the year of hours, the day across and the hour down, in UTCI's classes */
  function bimLbUtciHeatSvg(cls,leap){
    var days=Math.floor(cls.length/24),W=1200,H=268,L=46,R=W-10,T0=8,B=H-24,cw=(R-L)/days,ch=(B-T0)/24,s,h,d,run,k0,k;
    s='<svg viewBox="0 0 '+W+' '+H+'" role="img" aria-label="UTCI stress over the year, hour by hour">';
    for(h=0;h<24;h++){
      run=0;k0=null;
      for(d=0;d<=days;d++){
        k=d<days?cls[d*24+h]:-1;
        if(d<days&&k===k0){run++;continue;}
        if(k0!==null&&k0>=0&&run>0)s+='<rect x="'+bimClbF(L+(d-run)*cw)+'" y="'+bimClbF(T0+h*ch)+'" width="'+bimClbF(run*cw+0.35)+'" height="'+bimClbF(ch+0.35)+'" fill="'+BIM_UTCI_COL[k0]+'"/>';
        k0=k;run=1;
      }
    }
    [0,6,12,18].forEach(function(hh){s+='<text class="tk" x="'+(L-6)+'" y="'+bimClbF(T0+hh*ch+ch/2+3.5)+'" text-anchor="end">'+(hh<10?'0':'')+hh+':00</text>';});
    var cum=0,DM=[31,leap?29:28,31,30,31,30,31,31,30,31,30,31];
    BIM_CLIM_MONTHS.forEach(function(m,i){
      s+='<line class="bs" x1="'+bimClbF(L+cum*cw)+'" x2="'+bimClbF(L+cum*cw)+'" y1="'+B+'" y2="'+(B+4)+'"/><text class="tk" x="'+bimClbF(L+(cum+DM[i]/2)*cw)+'" y="'+(H-6)+'" text-anchor="middle">'+m+'</text>';
      cum+=DM[i];
    });
    return s+'</svg>';
  }
  /* each month's hours as a band of the ten classes, archiMap's way */
  function bimLbUtciMonthSvg(M){
    var W=A3D_CLB.narrow?360:640,rowH=17,T0=6,L=40,R=W-8,H=T0+12*rowH+8,s,m,k,x,tot,w;
    s='<svg viewBox="0 0 '+W+' '+H+'" role="img" aria-label="UTCI stress by month">';
    for(m=0;m<12;m++){
      tot=0;for(k=0;k<10;k++)tot+=M[m][k];
      x=L;
      s+='<text class="tk" x="'+(L-6)+'" y="'+bimClbF(T0+m*rowH+rowH/2+3.5)+'" text-anchor="end">'+BIM_CLIM_MONTHS[m]+'</text>';
      for(k=0;k<10;k++){
        if(!M[m][k]||!tot)continue;
        w=(R-L)*M[m][k]/tot;
        s+='<rect class="mk" x="'+bimClbF(x)+'" y="'+bimClbF(T0+m*rowH+1)+'" width="'+bimClbF(w)+'" height="'+(rowH-3)+'" fill="'+BIM_UTCI_COL[k]+'"'+
          bimClbTip(BIM_CLIM_MONTH_NAMES[m]+'|'+BIM_UTCI_NAMES[k]+'|'+M[m][k]+' hours, '+bimClbNum(100*M[m][k]/tot,0)+'%')+'/>';
        if(w>26)s+='<text class="tk" x="'+bimClbF(x+w/2)+'" y="'+bimClbF(T0+m*rowH+rowH/2+3.5)+'" text-anchor="middle"'+(k===5||k===4||k===6?'':' fill="#fff"')+'>'+Math.round(100*M[m][k]/tot)+'</text>';
        x+=w;
      }
    }
    return s+'</svg>';
  }
  function bimLbUtciCard(opt,no){
    var R=bimLbResult('utci');if(!R)return null;
    var C=R.r.conditions||{},cond=(opt&&BIM_LB_COND[opt.cond])?opt.cond:'sun_wind',U=C[cond];
    if(!U)return null;
    var cls=bimLbUnRle(U.classes),src=bimLbSrcKept(),best=null,bestM=-1,m,keys=['sun_wind','shade_wind','sun_still','shade_still'];
    for(m=0;m<12;m++){var tm=0,km;for(km=0;km<10;km++)tm+=U.monthly[m][km];if(tm&&U.monthly[m][5]/tm>bestM){bestM=U.monthly[m][5]/tm;best=m;}}
    var title=bimClbNum(U.comfort,0)+'% of the year\'s hours bring no thermal stress '+BIM_LB_COND[cond].toLowerCase()+
      '; '+keys.filter(function(c){return C[c]&&c!==cond;}).map(function(c){return bimClbNum(C[c].comfort,0)+'% '+BIM_LB_COND[c].toLowerCase();}).join(', ');
    var dek='UTCI, the temperature that feels the same to a person walking, '+BIM_LB_COND[cond].toLowerCase()+': every hour of the year in its stress class, and each month\'s share.'+
      (best!==null?' The most comfortable month is '+BIM_CLIM_MONTH_NAMES[best]+' ('+bimClbNum(100*bestM,0)+'%).':'')+
      (U.outside?' '+U.outside+' hours lie outside the formula\'s range and are its extrapolation.':'');
    var body=(cls?'<div class="a3d-clb-chart a3d-clb-heat">'+bimLbUtciHeatSvg(cls,!!(src&&src.leap))+'</div>':'')+
      '<div class="a3d-clb-chart" style="margin-top:6px">'+bimLbUtciMonthSvg(U.monthly)+'</div>'+
      bimClbLeg(BIM_UTCI_NAMES.map(function(n,k){return [BIM_UTCI_COL[k],n+' ('+BIM_UTCI_RANGE[k]+')'];}))+
      bimClbTable(['Condition','No stress %','Heat stress %','Cold stress %','Lowest °C','Highest °C'],keys.filter(function(c){return C[c];}).map(function(c){
        return [BIM_LB_COND[c],bimClbNum(C[c].comfort),bimClbNum(C[c].heat),bimClbNum(C[c].cold),bimClbNum(C[c].min),bimClbNum(C[c].max)];}));
    return bimClbCard(['s12','wide'],no,title,dek,body,bimLbSrcLine(R)+'; UTCI by Bröde et al. (UTCI_a002, 2009); the sun by SolarCal (ASHRAE 55); still air is UTCI\'s 0.5 m/s');
  }
  /* the psychrometric chart, drawn from Ladybug's own geometry */
  function bimLbPsySvg(P){
    var c=P.chart,W=A3D_CLB.narrow?380:620,H=A3D_CLB.narrow?340:380,L=40,R=W-(A3D_CLB.narrow?40:56),T0=10,B=H-30,s,i;
    var x0=0,x1=(c.max_t-c.min_t)*c.x_dim,y1=c.max_hr*c.y_dim;
    function X(x){return bimClbF(L+(x-x0)/(x1-x0)*(R-L));}
    function Y(y){return bimClbF(B-y/y1*(B-T0));}
    function pl(pts){return pts.map(function(p){return X(p[0])+','+Y(p[1]);}).join(' ');}
    function bin(n){return n>=100?5:n>=40?4:n>=15?3:n>=5?2:1;}
    s='<svg viewBox="0 0 '+W+' '+H+'" role="img" aria-label="Psychrometric chart with comfort polygons">';
    for(i=0;i<c.mesh_faces.length;i++){
      var f=c.mesh_faces[i],n=c.mesh_hours[i];
      s+='<polygon class="mk" points="'+pl(f.map(function(v){return c.mesh_vertices[v];}))+'" fill="var(--w'+bin(n)+')"'+bimClbTip(n+' hour'+(n===1?'':'s'))+'/>';
    }
    c.rh.forEach(function(l,k){s+='<polyline points="'+pl(l)+'" fill="none" stroke="var(--grid)" stroke-width="1"/>';});
    s+='<polyline points="'+pl(c.saturation)+'" fill="none" stroke="var(--ink2)" stroke-width="1.6"/>';
    c.t_label_points.forEach(function(p,k){if(k%2===0)s+='<text class="tk" x="'+X(p[0])+'" y="'+(B+14)+'" text-anchor="middle">'+c.t_labels[k]+'</text>';});
    c.hr_label_points.forEach(function(p,k){s+='<text class="tk" x="'+bimClbF(R+4)+'" y="'+bimClbF(+Y(p[1])+3.5)+'">'+c.hr_labels[k]+'</text>';});
    s+='<text class="tl2" x="'+((L+R)/2)+'" y="'+(H-2)+'" text-anchor="middle">Dry-bulb temperature (°C)</text>';
    P.polygons.forEach(function(pg,k){
      var col=k===0?'var(--ink)':BIM_LB_STRAT_COL[(k-1)%BIM_LB_STRAT_COL.length];
      s+='<polygon points="'+pl(pg)+'" fill="'+(k===0?'var(--s1)':'none')+'" fill-opacity="'+(k===0?0.18:0)+'" stroke="'+col+'" stroke-width="'+(k===0?2:1.5)+'"'+(k?' stroke-dasharray="5 3"':'')+
        bimClbTip(P.names[k]+'|'+bimClbNum(P.pct[k])+'% of hours')+'/>';
    });
    return s+'</svg>';
  }
  function bimLbPsyCard(opt,no){
    var R=bimLbResult('psych');if(!R)return null;
    var P=R.r,i,strat=[];
    for(i=1;i<P.names.length;i++)strat.push(P.names[i]+' '+bimClbNum(P.pct[i],0)+'%');
    var title=bimClbNum(P.pct[0],0)+'% of hours are comfortable indoors as the weather is; '+bimClbNum(P.total,0)+'% with the '+(P.names.length-1)+' passive strategies';
    var dek='Every hour of the year on the psychrometric chart, darker where more fall; the PMV comfort zone for '+P.clo.join(' and ')+' clo at '+P.met[0]+' met (PPD 10% or less), and the zones each strategy adds: '+strat.join(', ')+'.'+
      (P.missing&&P.missing.length?' Not drawn, off the chart: '+P.missing.join(', ')+'.':'');
    var body='<div class="a3d-clb-chart">'+bimLbPsySvg(P)+'</div>'+
      bimClbLeg([['var(--w1)','1–4 hours'],['var(--w2)','5–14'],['var(--w3)','15–39'],['var(--w4)','40–99'],['var(--w5)','100 or more']].concat(
        P.names.map(function(n,k){return [k===0?'var(--ink)':BIM_LB_STRAT_COL[(k-1)%BIM_LB_STRAT_COL.length],n+': '+bimClbNum(P.pct[k])+'%','ln'];})))+
      bimClbTable(['Zone','Hours %'],P.names.map(function(n,k){return [n,bimClbNum(P.pct[k])];}).concat([['Comfortable or made comfortable',bimClbNum(P.total)]]));
    return bimClbCard('s7',no,title,dek,body,bimLbSrcLine(R)+'; PMV by Fanger (ASHRAE 55), the strategies as Ladybug\'s PMV Polygon draws them, its defaults; passive solar on a '+(P.window===180?'south':'north')+'-facing window; mean station pressure '+bimClimInt(P.press)+' Pa');
  }
  function bimLbWindCard(opt,no){
    var R=bimLbResult('wind');if(!R)return null;
    var Wr=R.r,n=Wr.hours||1,k,j,pct=[],prev=0,pv=-1;
    for(k=0;k<16;k++){
      var row=[],tt=0;
      for(j=0;j<Wr.bins.length;j++){var v=100*((Wr.sectors[k]||[])[j]||0)/n;row.push(v);tt+=v;}
      pct.push(row);if(tt>pv){pv=tt;prev=k;}
    }
    var Wd={pct:pct,calm:Wr.calm_pct,n:n,mean:Wr.mean,prev:prev};
    var title='Prevailing wind from the '+BIM_CLIM_DIRS[prev]+', '+bimClbNum(Wr.mean)+' m/s on average; calm '+bimClbNum(Wr.calm_pct,0)+'% of hours';
    var body='<div class="a3d-clb-chart">'+bimClbRoseSvg(Wd,false,'Wind rose (Ladybug)')+'</div>'+
      bimClbLeg(Wr.bins.map(function(b,j){return ['var(--w'+(j+1)+')',j<Wr.bins.length-1?b+'–'+Wr.bins[j+1]+' m/s':'≥ '+b+' m/s'];}))+
      bimClbTable(['From'].concat(Wr.bins.map(function(b,j){return j<Wr.bins.length-1?b+'–'+Wr.bins[j+1]+' m/s':'≥ '+b+' m/s';})),pct.map(function(r,k){return [BIM_CLIM_DIRS[k]].concat(r.map(function(v){return bimClbNum(v);}));}));
    return bimClbCard('s5',no,title,'Share of the hours from each direction, by speed at 10 m; calm is a speed of 0, as weather files record it, shown at the centre.',body,bimLbSrcLine(R));
  }
  /* the design days: their numbers, and the day's temperature hour by hour */
  function bimLbDdSvg(D){
    var W=A3D_CLB.narrow?360:560,H=200,L=40,R=W-10,T0=10,B=H-24,lo=1e9,hi=-1e9,s,k,ser=[['heating','var(--s1)'],['cooling','var(--s2)']];
    ser.forEach(function(q){var d=D[q[0]];if(d&&d.hourly)d.hourly.forEach(function(v){if(v<lo)lo=v;if(v>hi)hi=v;});});
    if(lo>hi)return '';
    var T=bimClbTicks(lo,hi,5),y0=T[0],y1=T[T.length-1];
    function x(h){return bimClbF(L+h/23*(R-L));}function y(v){return bimClbF(B-(v-y0)/(y1-y0)*(B-T0));}
    s='<svg viewBox="0 0 '+W+' '+H+'" role="img" aria-label="Design days, hour by hour">'+bimClbAxisY(T,function(v){return +y(v);},L,R);
    [0,6,12,18,23].forEach(function(h){s+='<text class="tk" x="'+x(h)+'" y="'+(B+14)+'" text-anchor="middle">'+(h<10?'0':'')+h+':00</text>';});
    ser.forEach(function(q){var d=D[q[0]];if(!d||!d.hourly)return;
      s+='<polyline points="'+d.hourly.map(function(v,h){return x(h)+','+y(v);}).join(' ')+'" fill="none" stroke="'+q[1]+'" stroke-width="2"/>';});
    return s+'</svg>';
  }
  function bimLbDdCard(opt,no){
    var R=bimLbResult('dd');if(!R)return null;
    var D=R.r,h=D.heating,c=D.cooling;if(!h||!c)return null;
    var how={ddy:'the station\'s DDY (ASHRAE)',epw:'the EPW\'s design conditions (ASHRAE)',approx:'this one year, approximated (less accurate than ASHRAE\'s multi-year values)'};
    var title='Design days: '+bimClbNum(h.db)+' °C for heating (99.6%), '+bimClbNum(c.db)+' °C for cooling (0.4%) with '+bimClbNum(c.hum)+' °C '+(c.hum_type==='Wetbulb'?'wet bulb':c.hum_type.toLowerCase());
    var rows=['heating','heating99','cooling','cooling1','cooling2'].filter(function(k){return D[k];}).map(function(k){var d=D[k];
      return [d.name,bimClbNum(d.db),bimClbNum(d.range),d.hum_type+' '+bimClbNum(d.hum),bimClbNum(d.wind),BIM_CLIM_MONTHS[(d.month||1)-1]+' '+d.day,how[d.how]||d.how];});
    var body='<div class="a3d-clb-chart">'+bimLbDdSvg(D)+'</div>'+bimClbLeg([['var(--s1)','Heating 99.6%','ln'],['var(--s2)','Cooling 0.4%','ln']])+
      '<table class="a3d-clb-eqt"><thead><tr><th style="text-align:left">Design day</th><th>°C</th><th>Range</th><th>Humidity</th><th>m/s</th></tr></thead><tbody>'+
      rows.map(function(r){return '<tr><td class="pl">'+bimClbE(r[0])+'</td><td>'+r[1]+'</td><td>'+r[2]+'</td><td>'+bimClbE(r[3])+'</td><td>'+r[4]+'</td></tr>';}).join('')+'</tbody></table>';
    return bimClbCard('s5',no,title,'The conditions a building\'s heating and cooling are sized for, from '+(how[h.how]||h.how)+'; the design day\'s temperature hour by hour.',body,
      bimLbSrcLine(R)+'; ASHRAE Handbook, Fundamentals, chapter 14 (climatic design information)');
  }
  /* the four, in the climate board's order */
  var BIM_LB_FIGS=[['lb.utci',bimLbUtciCard],['lb.psych',bimLbPsyCard],['lb.wind',bimLbWindCard],['lb.dd',bimLbDdCard]];
  /* the figures on a board that has no Open-Meteo climate yet (an EPW opened, say): after its empty message */
  function bimLbOnlyFigs(){
    var cards=[],fig=0;
    BIM_LB_FIGS.forEach(function(F){var c=null;try{c=F[1](null,fig+1);}catch(eLb){console.warn('[BIM] Ladybug figure '+F[0],eLb);}
      if(c){fig++;cards.push(c.replace('<figure class="a3d-clb-card','<figure data-figid="'+F[0]+'" class="a3d-clb-card'));}});
    return cards.length?'<section class="a3d-clb-grid" style="margin-top:14px">'+cards.join('')+'</section>':'';
  }
