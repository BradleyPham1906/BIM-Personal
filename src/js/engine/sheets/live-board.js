

  /* ================= __acad3dV175b: board objects drawn from the model, the pure part =================
     docs/research/research-presentation-live.md (D1, D13: schedules, single KPI cards and a result layer's chart
     as board objects) and docs/work-orders/v175/SPEC-v175b.md. This file holds the functions that need nothing
     of the page or the model: a result layer's histogram, sorting and totalling a schedule's rows, finding one
     indicator among a board's cards, and the markup of a table and a chart. Each is a work order in
     docs/work-orders/v175/TASKS-v175b.md, added below as it is built. */

  /* a histogram of digit cells: m bins; each digit d < m adds one at index d */
  function bimLbHist(cells, m){
    var counts = [], i, c, d;
    if(typeof cells !== 'string'){for(i = 0; i < m; i += 1)counts[i] = 0;return counts;}
    for(i = 0; i < m; i += 1)counts[i] = 0;
    for(i = 0; i < cells.length; i += 1){
      c = cells.charAt(i);
      if(c >= '0' && c <= '9'){d = +c; if(d < m)counts[d] += 1;}
    }
    return counts;
  }
