  /* ================= __acad3dV269: the spreadsheet's formulas =================
     FreeCAD's Spreadsheet workbench: cells of numbers, text and formulas, a cell named by an alias, and expressions that
     read the model and drive it. This file is the formula language, pure, tested without a page:
       a cell's content: "=formula", or a number, or text;
       formula: + - * / ^, brackets, numbers, cells (A1, $B$2), aliases (width), ranges in functions (A1:B4), pi;
       functions: sum, min, max, average, count, abs, sqrt, round(x[, places]), floor, ceil, mod(a, b), sin, cos, tan,
       asin, acos, atan in degrees (as QUICKCALC's), if(test, then, else), and obj("name", "property"), which reads an
       object of the model (spreadsheet.js says which properties).
     A reference to an empty cell is 0; a cycle, an unknown name or a bad formula is that cell's error, and so is any
     cell that reads it. */
  var BIM_SHEET_COLS=12,BIM_SHEET_ROWS=40;
  function bimSheetColName(c){return String.fromCharCode(65+c);}
  /* "B3" to [1, 2] (column, row from 0), or null */
  function bimSheetParseRef(s){
    var m=/^\$?([A-Za-z])\$?(\d{1,3})$/.exec(String(s||''));
    if(!m)return null;
    var c=m[1].toUpperCase().charCodeAt(0)-65,r=parseInt(m[2],10)-1;
    return (c>=0&&c<BIM_SHEET_COLS&&r>=0&&r<BIM_SHEET_ROWS)?[c,r]:null;
  }
  function bimSheetRefName(c,r){return bimSheetColName(c)+(r+1);}
  function bimSheetRangeCells(a,b){
    var A=bimSheetParseRef(a),B=bimSheetParseRef(b),out=[],c,r;
    if(!A||!B)return null;
    for(r=Math.min(A[1],B[1]);r<=Math.max(A[1],B[1]);r++)for(c=Math.min(A[0],B[0]);c<=Math.max(A[0],B[0]);c++)out.push(bimSheetRefName(c,r));
    return out;
  }
  var BIM_SHEET_D2R=Math.PI/180;
  var BIM_SHEET_FN={
    sum:function(a){return a.reduce(function(s,x){return s+x;},0);},
    min:function(a){return Math.min.apply(null,a);},max:function(a){return Math.max.apply(null,a);},
    average:function(a){return a.reduce(function(s,x){return s+x;},0)/a.length;},
    count:function(a){return a.length;},
    abs:function(a){return Math.abs(a[0]);},sqrt:function(a){if(a[0]<0)throw new Error('sqrt of a negative number');return Math.sqrt(a[0]);},
    round:function(a){var k=Math.pow(10,a.length>1?Math.round(a[1]):0);return Math.round(a[0]*k)/k;},
    floor:function(a){return Math.floor(a[0]);},ceil:function(a){return Math.ceil(a[0]);},
    mod:function(a){if(!a[1])throw new Error('mod by zero');return a[0]-a[1]*Math.floor(a[0]/a[1]);},
    sin:function(a){return Math.sin(a[0]*BIM_SHEET_D2R);},cos:function(a){return Math.cos(a[0]*BIM_SHEET_D2R);},tan:function(a){return Math.tan(a[0]*BIM_SHEET_D2R);},
    asin:function(a){return Math.asin(a[0])/BIM_SHEET_D2R;},acos:function(a){return Math.acos(a[0])/BIM_SHEET_D2R;},atan:function(a){return Math.atan(a[0])/BIM_SHEET_D2R;},
    if:function(a){return a[0]?a[1]:a[2];}
  };
  var BIM_SHEET_NARGS={average:-1,sum:-1,min:-1,max:-1,count:-1,round:-2,mod:2,if:3};
  /* Every cell's value. cells: {A1: "=B1*2", ...}; aliases: {A1: "width"}; readObj(name, prop) gives a number or throws.
     Returns {A1: number | text} with an error as {error}. Pure on its inputs. */
  function bimSheetEvaluate(cells,aliases,readObj){
    var out={},state={},byAlias={},k;
    for(k in (aliases||{}))if(aliases[k])byAlias[String(aliases[k]).toLowerCase()]=k;
    function cellValue(ref){
      if(state[ref]===2)return out[ref];
      if(state[ref]===1)throw new Error('A cycle through '+ref);
      state[ref]=1;
      var v;
      try{v=cellOf(cells[ref]);}catch(e){v={error:e.message};}
      out[ref]=v;state[ref]=2;
      return v;
    }
    function cellOf(raw){
      var s=raw==null?'':String(raw);
      if(s.charAt(0)==='=')return formula(s.slice(1));
      if(/^\s*$/.test(s))return '';
      var n=Number(s);
      return (isFinite(n)&&/^\s*[-+]?(\d+\.?\d*|\.\d+)([eE][-+]?\d+)?\s*$/.test(s))?n:s;
    }
    function num(ref){
      var v=cellValue(ref);
      if(v&&typeof v==='object')throw new Error(ref+' has an error');
      if(v==='')return 0;
      if(typeof v!=='number')throw new Error(ref+' is text, not a number');
      return v;
    }
    function formula(src){
      var s=src,i=0;
      function ws(){while(i<s.length&&/\s/.test(s[i]))i++;}
      function fail(m){throw new Error(m);}
      function cmp(){var v=expr();ws();var m=/^(<=|>=|<>|=|<|>)/.exec(s.slice(i));
        if(m){i+=m[1].length;var r=expr();var o=m[1];return (o==='<'?v<r:o==='>'?v>r:o==='<='?v<=r:o==='>='?v>=r:o==='<>'?v!==r:v===r)?1:0;}return v;}
      function expr(){var v=term();ws();while(s[i]==='+'||s[i]==='-'){var op=s[i++];var r=term();v=op==='+'?v+r:v-r;ws();}return v;}
      function term(){var v=unary();ws();while(s[i]==='*'||s[i]==='/'){var op=s[i++];var r=unary();if(op==='/'&&r===0)fail('Division by zero');v=op==='*'?v*r:v/r;ws();}return v;}
      function unary(){ws();if(s[i]==='-'){i++;return -unary();}if(s[i]==='+'){i++;return unary();}return power();}
      function power(){var b=atom();ws();if(s[i]==='^'){i++;return Math.pow(b,unary());}return b;}
      function str(){var q=s[i++],j=i;while(i<s.length&&s[i]!==q)i++;if(i>=s.length)fail('A quote is not closed');return s.slice(j,i++);}
      /* a function's arguments: numbers, ranges spread into them, strings kept for obj() */
      function args(){
        var a=[];ws();
        if(s[i]===')'){i++;return a;}
        for(;;){
          ws();
          var rm=/^(\$?[A-Za-z]\$?\d{1,3}):(\$?[A-Za-z]\$?\d{1,3})/.exec(s.slice(i));
          if(rm){var R=bimSheetRangeCells(rm[1].replace(/\$/g,''),rm[2].replace(/\$/g,''));if(!R)fail('A range is outside the sheet');i+=rm[0].length;
            R.forEach(function(ref){var v=cellValue(ref);if(typeof v==='number')a.push(v);else if(v&&typeof v==='object')fail(ref+' has an error');});}
          else if(s[i]==='"'||s[i]==='\'')a.push(str());
          else a.push(cmp());
          ws();
          if(s[i]===','||s[i]===';'){i++;continue;}
          if(s[i]===')'){i++;return a;}
          fail('A function’s brackets are not closed');
        }
      }
      function atom(){
        ws();
        if(s[i]==='('){i++;var v=cmp();ws();if(s[i]!==')')fail('A bracket is not closed');i++;return v;}
        var m=/^(\d+\.?\d*(?:[eE][+-]?\d+)?|\.\d+(?:[eE][+-]?\d+)?)/.exec(s.slice(i));
        if(m){i+=m[1].length;return parseFloat(m[1]);}
        var w=/^\$?[A-Za-z_][A-Za-z0-9_]*(\$?\d+)?/.exec(s.slice(i));
        if(w){
          var word=w[0];i+=word.length;ws();
          var name=word.toLowerCase();
          if(s[i]==='('){
            i++;var a=args();
            if(name==='obj'){if(a.length!==2||typeof a[0]!=='string'||typeof a[1]!=='string')fail('obj needs a name and a property: obj("Wall_1", "height")');
              var ov=readObj?readObj(a[0],a[1]):null;if(typeof ov!=='number'||!isFinite(ov))fail('obj("'+a[0]+'", "'+a[1]+'") has no number');return ov;}
            if(!BIM_SHEET_FN.hasOwnProperty(name))fail('Unknown function: '+word);
            var need=BIM_SHEET_NARGS[name];
            if(a.some(function(x){return typeof x!=='number';}))fail(word+' takes numbers');
            if(need===undefined&&a.length!==1)fail(word+' takes one number');
            if(need>0&&a.length!==need)fail(word+' takes '+need+' numbers');
            if(need===-1&&!a.length)fail(word+' needs numbers');
            if(need===-2&&(a.length<1||a.length>2))fail(word+' takes one or two numbers');
            return BIM_SHEET_FN[name](a);
          }
          if(name==='pi')return Math.PI;
          var ref=bimSheetParseRef(word);
          if(ref)return num(bimSheetRefName(ref[0],ref[1]));
          if(byAlias[name])return num(byAlias[name]);
          fail('Unknown name: '+word);
        }
        fail(i<s.length?'Unexpected "'+s[i]+'"':'The formula ends too soon');
      }
      var v=cmp();ws();
      if(i<s.length)fail('Unexpected "'+s[i]+'"');
      if(typeof v!=='number'||!isFinite(v))fail('The result is not a finite number');
      return v;
    }
    for(k in (cells||{}))cellValue(k);
    return out;
  }
export {
  BIM_SHEET_COLS, BIM_SHEET_FN, BIM_SHEET_ROWS, bimSheetColName, bimSheetEvaluate, bimSheetParseRef,
  bimSheetRefName
};
