"""falsify_phase171.py -- break the V171 build one way at a time, keeping the marker.
Variant names are lower case: the runner reads no other (V126). Each names, in its comment, the check
of tests/bim_phase171_traffic_browser_tests.py that should catch it."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # ---- 1. the records ----
    'marker_lost': [("trafficrecords,network,lanes,widthkept,junctions,priority,stops,signals,webster,kellfullerton,", "trafficrecords,network,lanes,widthkept,junctions,priority,stops,signals,webster,")],   # the V171 marker
    'version_old': [("var BIM_APP_VERSION={v:'V171',", "var BIM_APP_VERSION={v:'V170',")],   # V171 or later
    'idm_t': [("{n:'T',v:1.5,u:'s',", "{n:'T',v:1.4,u:'s',")],   # the IDM's car is the authors'
    'mobil_thr': [("{n:'thr',v:0.1,", "{n:'thr',v:0.2,")],   # MOBIL's threshold
    'sat_flow': [("{n:'sat',v:1900,", "{n:'sat',v:1800,")],   # the timing manual's saturation flow
    'kf_decel': [("{n:'kf_a',v:3.048,", "{n:'kf_a',v:3,")],   # Kell and Fullerton
    'walk_short': [("{n:'walk',v:7,", "{n:'walk',v:4,")],   # the MUTCD's WALK
    'k_ten': [("{n:'k',v:9,", "{n:'k',v:10,")],   # Florida's K of 9%
    'retail_rate': [("rate:40,per:'ksf'", "rate:42,per:'ksf'")],   # San Diego's rates
    'walk_spread': [("{n:'sd',v:0.26,", "{n:'sd',v:0.25,")],   # Helbing and Molnar's walking speeds
    'alias_lost': [("'SIMULATETRAFFIC','PEDESTRIANS','TRAFFICON'", "'SIMULATETRAFFIC','TRAFFICON'")],   # searching 'pedestrians' finds TRAFFIC
    'group_model': [("BIM_ANZ_GROUP_OF.dgtraffic='access';", "BIM_ANZ_GROUP_OF.dgtraffic='model';")],   # an analysis of Access
    # ---- 2. the car, the plan, the turns, the trips ----
    'idm_not_squared': [("-(ss/s)*(ss/s));", "-(ss/s));")],   # the IDM's acceleration
    'idm_no_approach': [("v*P.T+v*dv/(2*Math.sqrt(P.a*P.b))", "v*P.T")],   # the IDM's acceleration; the steady gap
    'webster_no_five': [("(wb[0]*L+wb[1])", "(wb[0]*L)")],   # busy: Webster's cycle
    'cycle_no_least': [("C=Math.min(cmax,Math.max(cmin,C0))", "C=Math.min(cmax,C0)")],   # light traffic: the least cycle
    'yellow_unfloored': [("o.Y=Math.min(y1,Math.max(y0,", "o.Y=Math.min(y1,Math.max(0,")],   # the yellows
    'allred_own_width': [("o.AR=Math.min(rmax,(wOf(1-k)+klv)", "o.AR=Math.min(rmax,(wOf(k)+klv)")],   # the all-reds
    'walk_own_street': [("o.gped=walk+wOf(1-k)/clr;", "o.gped=walk+wOf(k)/clr;")],   # a wide road: the walkers' least green
    'greens_unheld': [("if(P[k].G<P[k].gmin-1e-9)", "if(false)")],   # a wide road: the cycle grown
    'furness_once': [("if(ti>0&&to>0)for(r=0;r<n;r++){", "if(ti>0&&to>0)for(r=0;r<1;r++){")],   # NCHRP 255's balancing
    'furness_no_rows': [("      for(i=0;i<I;i++){var rs=0;for(j=0;j<Jn;j++)rs+=T[i][j];if(rs>0)for(j=0;j<Jn;j++)T[i][j]*=qi[i]/rs;}\n", "")],   # NCHRP 255's balancing
    'dense_doubled': [("du/acres>dense", "du/acres>dense*3")],   # San Diego's trips: over 20 an acre
    'office_linear': [("if(R.ln)day=Math.exp(R.ln[0]*Math.log(r.n)+R.ln[1]);", "if(R.ln)day=Math.exp(R.ln[1])*r.n/10;")],   # San Diego's trips: the office
    # ---- 3. the network ----
    'reach_wider': [("R=bimStd('app.traffic','radius')", "R=bimStd('app.traffic','radius')*1.1")],   # every street cut at the reach
    'width_ignored': [("    if(wm.src==='mapped'){\n", "    if(false){\n")],   # Avenue 14's six lanes, under its mapped width, three
    'signal_far': [("if(!best||bd>sr||best.kind==='pass')", "if(!best||bd>sr*20||best.kind==='pass')")],   # the two signals near the lot; V166's beyond the reach
    'allstop_lost': [("if(best.kind!=='signal')best.kind='allstop';", "if(best.kind==='pass')best.kind='allstop';")],   # the all-way stop
    'stop_every_way': [("if(ba)best.stop[ba.lin]=1;", "if(ba)best.ins.forEach(function(li){best.stop[li]=1;});")],   # the stop stops that approach only
    'major_one_way': [("j.major[T[k].i]=1;", "j.tie=j.tie;")],   # Market Street's two ways in have the way
    'ramp_has_way': [("if(dd<=bd)", "if(dd<=180)")],   # where the ramp merges, the ramp gives way
    'uturn_anywhere': [("if(!T.length&&Lk.rev>=0&&!j.bnd&&!j.lot)", "if(Lk.rev>=0&&!j.bnd&&!j.lot)")],   # a car turns back only at a dead end
    'driveway_missed': [("if(d<=3&&d<bd)", "if(d<=0.5&&d<bd)")],   # a driveway stopping 2 m short of the lot line is still the lot's entry
    'doors_unnamed': [("name:(d[3]||'')||('Entrance'+(d[2]&&d[2]!=='yes'?' ('+d[2]+')':''))", "name:'Entrance'")],   # the lot's two mapped doors
    # ---- 4. the demand ----
    'volume_both_ways': [("return rc.u*bimStd('fdot.k','k')/100*0.5;", "return rc.u*bimStd('fdot.k','k')/100;")],   # each street's traffic, half each way
    'ramp_mainline': [("Lk.q=ramp.test(Lk.hw)?-1:bimTrLinkVolume(Lk);", "Lk.q=bimTrLinkVolume(Lk);")],   # the ramp carries its quieter end's
    'exit_uncapped': [("Math.min(N.links[lo].q,qmax)", "N.links[lo].q")],   # no exit drawing more than its busiest way in brings
    # ---- 5. the run ----
    'red_runs': [("if(BIM_TR_SIG.s==='r')return Math.min(h,d);", "if(false)return Math.min(h,d);")],   # no car crossed its stop line on a red
    'amber_always': [("if(far)return Math.min(h,d);", "if(false)return Math.min(h,d);")],   # no car crossed its stop line on a red
    'walk_any_time': [("return BIM_TR_SIGW.s==='g'&&", "return true||")],   # no walker started across without its green's time
    'walk_late': [("BIM_TR_SIGW.left>=cr.len/bimStd('mutcd.walk','clear')", "BIM_TR_SIGW.left>=0")],   # no walker started across without its green's time
    'merge_unchecked': [("  function bimTrClaimed(RUN,c,l,nx){\n", "  function bimTrClaimed(RUN,c,l,nx){return false;\n"),
                        ("  function bimTrRoomAt(RUN,Ln,ln,s){", "  function bimTrRoomAt(RUN,Ln,ln,s){return true;")],   # no two cars in one place
    'spawn_unchecked': [("if(room<P.s0)return -1;", "if(room<-100)return -1;")],   # no two cars in one place
    'lot_uncounted': [("        RUN.res.lotIn++;\n", "")],   # every car accounted for
    'lot_no_trips': [("    if(!RUN.lotOk)return;\n    var TR=RUN.trips", "    return;\n    var TR=RUN.trips")],   # the lot's own cars came in and went out
    'pools_twice': [("    R.warmMs=performance.now()-t0;R.warm=true;\n    bimTrResetTallies(R);", "    R.warmMs=performance.now()-t0;R.warm=true;\n    bimTrAlloc(R);")],   # the pools allocated once
    'tallies_grow': [("    Q.n++;Q.out+=out;", "    (RUN.hist||(RUN.hist=[])).push(new Float64Array(20000));Q.n++;Q.out+=out;")],   # the memory settles
    'walkers_uncapped': [("W.v0[i]=Math.max(0.5,Math.min(sp,bimStd('hm.walk','mean')*k));", "W.v0[i]=Math.max(0.5,sp);")],   # capped at 1.3 times the mean
    # ---- 6. on the clock ----
    'clock_ignored': [("A3D_ANIM.t+=dtc;bimTrAdvance(dtc);", "A3D_ANIM.t+=dtc;")],   # it runs with the clock
    'speed_ignored': [("R.acc+=sec*R.set.speed;", "R.acc+=sec;")],   # at 16 times the clock
    'stop_keeps_run': [("A3D_TR.last=bimTrResults(A3D_TR.run);}A3D_TR.run=null;}", "A3D_TR.last=bimTrResults(A3D_TR.run);}}")],   # Stop gives the run up
    'settings_no_undo': [("    if(o[k]===v)return false;\n    pushUndo();\n", "    if(o[k]===v)return false;\n")],   # turning it on is one undo step; undone
    'quality_fixed': [("function bimTrQuality(){var s=bimTrSettings();return s.q==='auto'?bimTrDeviceQ():s.q;}", "function bimTrQuality(){return 'normal';}")],   # Light chosen by hand
    # ---- 7. drawn ----
    'plan_unfilled': [("ctx.closePath();ctx.fill();ctx.stroke();dw.cars++;", "ctx.closePath();dw.cars++;")],   # ink where the cars are
    'layer_ignored': [("  function bimTrShown(){\n", "  function bimTrShown(){return true;\n")],   # with its layer off, none drawn
    'stoplines_off': [("      bimTrDrawSignals(ctx,V,W,H,R,y);\n", "")],   # the eight signalled approaches' stop lines
    'faces_unfilled': [("ctx.fillStyle=shade(col,0.45+0.55*Math.abs(vdot(o.n,LIGHT)));ctx.fill();ctx.stroke();dw.faces++;", "dw.faces+=0;")],   # in 3D the cars face by face
    # ---- 8. the results as layers ----
    'run_no_signals': [("      E.push({k:'sig:'+j.n,", "      if(0)E.push({k:'sig:'+j.n,")],   # Run lays each signal's plan
    'row_no_peak': [("    h+=bimTrSegBtns('Peak hour','peak',[['am','AM'],['pm','PM']],s.peak);\n", "")],   # its row: the peak hour
    # ---- 9. without a driveway ----
    'prov_not_alley': [("if(!g.car||g.lot)continue;", "if(!g.car||g.lot||bimTrHw(g.t)==='service')continue;")],   # a provisional entry from the alley, as V166 marks it
    # ---- 10. a phone, a tablet ----
    'quality_cores': [("if((m&&m<=2)||(c&&c<=2))return 'light';", "if(m&&m<=2)return 'light';")],   # 4 GB and 2 cores: light
    'thumb_small': [(".a3d-anzbtn{min-height:34px;padding:0 12px;font-size:12.5px}", ".a3d-anzbtn{min-height:24px;padding:0 12px;font-size:12.5px}")],   # a phone's row buttons a thumb's height
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV171' in txt
out.write_text(txt, encoding='utf-8')
