

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

  /* a share as a percentage to one decimal; null when not finite numbers or total <= 0 */
  function bimLbPct(n, total){
    if(typeof n !== 'number' || !isFinite(n) || typeof total !== 'number' || !isFinite(total) || total <= 0)return null;
    return Math.round(n / total * 1000) / 10;
  }
  /* bars of a histogram: equal widths, the tallest fills the height */
  function bimLbBars(counts, W, H, gap){
    var result = [], n, w, max, i, x, h, y;
    if(!(counts instanceof Array) || counts.length === 0)return [];
    n = counts.length;
    w = (W - gap * (n - 1)) / n;
    max = 0;
    for(i = 0; i < n; i += 1){
      if(typeof counts[i] === 'number' && isFinite(counts[i]) && counts[i] > max)max = counts[i];
    }
    for(i = 0; i < n; i += 1){
      x = Math.round(i * (w + gap) * 100) / 100;
      if(max === 0)h = 0;
      else h = Math.round(counts[i] / max * H * 100) / 100;
      y = Math.round((H - h) * 100) / 100;
      result.push({x: x, y: y, w: Math.round(w * 100) / 100, h: h});
    }
    return result;
  }
  /* a new stably sorted array of rows; empty values always last */
  function bimLbSort(rows, key, desc){
    var marked = [], i, r, v, len, out, ea, eb, c;
    len = rows.length;
    for(i = 0; i < len; i += 1){
      r = rows[i];
      v = r[key];
      marked.push({row: r, v: v, p: i});
    }
    marked.sort(function(a, b){
      ea = (a.v === '' || a.v === null || a.v === undefined);
      eb = (b.v === '' || b.v === null || b.v === undefined);
      if(ea && eb)return a.p - b.p;
      if(ea)return 1;
      if(eb)return -1;
      if(typeof a.v === 'number' && typeof b.v === 'number')c = a.v - b.v;
      else c = String(a.v).toLowerCase() < String(b.v).toLowerCase() ? -1 : (String(a.v).toLowerCase() > String(b.v).toLowerCase() ? 1 : 0);
      if(desc)c = -c;
      if(c === 0)return a.p - b.p;
      return c;
    });
    out = [];
    for(i = 0; i < len; i += 1)out.push(marked[i].row);
    return out;
  }
  /* one total per column: sum of finite numbers for area/count, else empty */
  function bimLbTotals(rows, cols){
    var result = [], i, j, col, v, sum, have;
    for(i = 0; i < cols.length; i += 1){
      col = cols[i];
      if(col.kind !== 'area' && col.kind !== 'count'){result.push('');continue;}
      sum = 0; have = false;
      for(j = 0; j < rows.length; j += 1){
        v = rows[j][col.k];
        if(typeof v === 'number' && isFinite(v)){sum += v; have = true;}
      }
      result.push(have ? sum : '');
    }
    return result;
  }
  /* read back HTML entities; &amp; last so '&amp;lt;' stays '&lt;' */
  function bimLbUnesc(s){
    if(typeof s !== 'string')return '';
    return s.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&amp;/g, '&');
  }
  /* the labels of the KPI cards, read back, skipping cards without one */
  function bimLbKpiLabels(list){
    var result = [], i, s, m;
    if(!(list instanceof Array))return result;
    for(i = 0; i < list.length; i += 1){
      s = list[i];
      if(typeof s !== 'string')continue;
      m = /data-kpi="([^"]*)"/.exec(s);
      if(m)result.push(bimLbUnesc(m[1]));
    }
    return result;
  }
  /* the index of the first KPI card whose label matches exactly */
  function bimLbKpiFind(list, label){
    var i, s, m;
    if(!(list instanceof Array))return -1;
    for(i = 0; i < list.length; i += 1){
      s = list[i];
      if(typeof s !== 'string')continue;
      m = /data-kpi="([^"]*)"/.exec(s);
      if(m && bimLbUnesc(m[1]) === label)return i;
    }
    return -1;
  }
  /* the exact markup of a schedule table */
  function bimLbTableHtml(head, rows, foot, esc){
    var n, i, j, row, out;
    n = head.length;
    out = [];
    out.push('<table class="a3d-clb-dtab"><thead><tr>');
    for(i = 0; i < n; i += 1)out.push('<th>' + esc(head[i]) + '</th>');
    out.push('</tr></thead><tbody>');
    if(rows.length === 0){
      out.push('<tr><td colspan="' + n + '" class="none">No rows</td></tr>');
    } else {
      for(i = 0; i < rows.length; i += 1){
        row = rows[i];
        out.push('<tr>');
        for(j = 0; j < n; j += 1){
          if(j < row.length)out.push('<td>' + esc(row[j]) + '</td>');
          else out.push('<td></td>');
        }
        out.push('</tr>');
      }
    }
    out.push('</tbody>');
    if(foot !== null){
      out.push('<tfoot><tr>');
      for(i = 0; i < foot.length; i += 1)out.push('<td>' + esc(foot[i]) + '</td>');
      out.push('</tr></tfoot>');
    }
    out.push('</table>');
    return out.join('');
  }
  /* the exact markup of a histogram svg */
  function bimLbHistSvg(bars, cols, W, H){
    var out = [], i, bar, c;
    out.push('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ' + W + ' ' + H + '" width="' + W + '" height="' + H + '" preserveAspectRatio="none">');
    for(i = 0; i < bars.length; i += 1){
      bar = bars[i];
      if(bar.h <= 0)continue;
      c = cols.length > 0 ? cols[i % cols.length] : '#888888';
      out.push('<rect x="' + bar.x + '" y="' + bar.y + '" width="' + bar.w + '" height="' + bar.h + '" fill="' + c + '"/>');
    }
    out.push('</svg>');
    return out.join('');
  }
export {
  bimLbBars, bimLbHist, bimLbHistSvg, bimLbKpiFind, bimLbKpiLabels, bimLbSort, bimLbTableHtml, bimLbTotals
};
