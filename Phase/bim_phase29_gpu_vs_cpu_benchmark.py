from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(args=['--use-gl=swiftshader','--enable-unsafe-swiftshader'])
    pg=b.new_page(viewport={'width':1600,'height':1000})
    pg.goto('file:///home/claude/canvas_v10.html'); pg.wait_for_timeout(1500)
    pg.evaluate("window.__a3dEnter()"); pg.wait_for_timeout(1000)
    res=pg.evaluate("""(()=>{
      function grid(n){
        var v=[],f=[];
        for(var i=0;i<=n;i++)for(var j=0;j<=n;j++)v.push([-3+i*6/n,((i+j)%2)*0.3,-3+j*6/n]);
        for(var i=0;i<n;i++)for(var j=0;j<n;j++){
          var a=i*(n+1)+j,b2=a+1,c=(i+1)*(n+1)+j,d=c+1;
          f.push([a,b2,d,c]);
        }
        return {v:v,f:f};
      }
      function measure(reps){
        var t0=performance.now();
        for(var r=0;r<reps;r++){window.__a3dTestRotate(0.01);window.__a3dTestPaint();}
        return (performance.now()-t0)/reps;
      }
      var out=[]; var sizes=[40,80,150,300];
      for(var s=0;s<sizes.length;s++){
        var n=sizes[s], m=grid(n), faces=m.f.length;
        // ---- GPU path ----
        window.__a3dTestForceCpu(false);
        window.__a3dTestSetObjs([{id:'perf',t:'solid',name:'Perf',pos:[0,0,0],mesh:m,col:'#7f9db8'}]);
        window.__a3dTestPaint();
        var gpuMs=measure(6);
        // ---- CPU path (old renderer) ----
        window.__a3dTestForceCpu(true);
        window.__a3dTestSetObjs([{id:'perf2',t:'solid',name:'Perf2',pos:[0,0,0],mesh:m,col:'#7f9db8'}]);
        window.__a3dTestPaint();
        var cpuMs=measure(6);
        out.push({faces:faces, gpu:Math.round(gpuMs*10)/10, cpu:Math.round(cpuMs*10)/10,
                  speedup:Math.round(cpuMs/Math.max(gpuMs,0.001)*10)/10});
      }
      return out;
    })()""")
    print("MAIN-THREAD JS COST PER FRAME (the metric that transfers to real hardware)")
    print(f"{'faces':>8} {'old CPU':>10} {'new GPU':>10} {'speedup':>9}")
    for r in res:
        print(f"{r['faces']:>8} {r['cpu']:>8} ms {r['gpu']:>8} ms {r['speedup']:>8}x")
    b.close()
