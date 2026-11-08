/* V174 research experiment: where Chromium puts items that overflow a space-around / space-evenly /
   space-between / center line (css-flexbox-1 says space-around and space-evenly fall back to safe center). */
var chromium = require('playwright').chromium;
chromium.launch().then(function (b) {
  return b.newPage().then(function (p) {
    var jcs = ['space-between', 'space-around', 'space-evenly', 'center', 'safe center'];
    var html = jcs.map(function (j, i) {
      return '<div id="c' + i + '" style="display:flex;width:150px;height:30px;justify-content:' + j + '">' +
        '<div style="flex:0 0 60px"></div><div style="flex:0 0 60px"></div><div style="flex:0 0 60px"></div></div>';
    }).join('');
    return p.setContent('<body style="margin:0">' + html + '</body>').then(function () {
      return p.evaluate(function (n) {
        var r = [];
        for (var i = 0; i < n; i++) {
          var c = document.getElementById('c' + i), cr = c.getBoundingClientRect();
          r.push(c.style.justifyContent + ': first item x = ' + (c.firstChild.getBoundingClientRect().left - cr.left));
        }
        return r;
      }, jcs.length);
    }).then(function (r) { console.log('Chromium ' + b.version()); r.forEach(function (l) { console.log(l); }); return b.close(); });
  });
});
