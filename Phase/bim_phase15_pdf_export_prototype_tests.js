function buildSimplePdf(width, height, rgbBytes) {
  // rgbBytes: Buffer/array of length width*height*3, top-to-bottom row order (matches how we'll
  // extract it from canvas ImageData, which is also top-to-bottom).
  var chunks = [];
  var offsets = [];
  var pos = 0;
  function push(str_or_buf) {
    var buf = Buffer.isBuffer(str_or_buf) ? str_or_buf : Buffer.from(str_or_buf, 'latin1');
    chunks.push(buf);
    pos += buf.length;
  }
  function beginObj(n) {
    offsets[n] = pos;
    push(n + ' 0 obj\n');
  }

  push('%PDF-1.4\n%\xE2\xE3\xCF\xD3\n');

  beginObj(1);
  push('<< /Type /Catalog /Pages 2 0 R >>\nendobj\n');

  beginObj(2);
  push('<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n');

  beginObj(3);
  push('<< /Type /Page /Parent 2 0 R /Resources << /XObject << /Im0 5 0 R >> >> ' +
       '/MediaBox [0 0 ' + width + ' ' + height + '] /Contents 4 0 R >>\nendobj\n');

  var content = 'q\n' + width + ' 0 0 ' + height + ' 0 0 cm\n/Im0 Do\nQ\n';
  var contentBuf = Buffer.from(content, 'latin1');
  beginObj(4);
  push('<< /Length ' + contentBuf.length + ' >>\nstream\n');
  push(contentBuf);
  push('\nendstream\nendobj\n');

  beginObj(5);
  var imgHeader = '<< /Type /XObject /Subtype /Image /Width ' + width + ' /Height ' + height +
    ' /ColorSpace /DeviceRGB /BitsPerComponent 8 /Length ' + rgbBytes.length + ' >>\nstream\n';
  push(imgHeader);
  push(rgbBytes);
  push('\nendstream\nendobj\n');

  var xrefStart = pos;
  var xref = 'xref\n0 6\n0000000000 65535 f \n';
  for (var i = 1; i <= 5; i++) {
    xref += String(offsets[i]).padStart(10, '0') + ' 00000 n \n';
  }
  push(xref);
  push('trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n' + xrefStart + '\n%%EOF');

  return Buffer.concat(chunks);
}

// build a small 8x6 test image: a red-to-blue gradient, easy to sanity-check pixel values
var W = 8, H = 6;
var px = Buffer.alloc(W * H * 3);
for (var y = 0; y < H; y++) {
  for (var x = 0; x < W; x++) {
    var idx = (y * W + x) * 3;
    px[idx] = Math.round(255 * x / (W - 1));   // R ramps left->right
    px[idx + 1] = 0;
    px[idx + 2] = Math.round(255 * y / (H - 1)); // B ramps top->bottom
  }
}

var pdfBuf = buildSimplePdf(W, H, px);
require('fs').writeFileSync('/tmp/test_export.pdf', pdfBuf);
console.log('PDF written, size:', pdfBuf.length, 'bytes');
