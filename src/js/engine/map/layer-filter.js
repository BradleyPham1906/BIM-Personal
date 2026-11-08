
  /* ================= __acad3dV173b: a layer's filter (definition query) =================
     A subset of OGC CQL2 Text (21-065r2, 1.0.0): Basic CQL2 (= <> < <= > >=, AND OR NOT, IS [NOT]
     NULL, TRUE, FALSE), Advanced Comparison ([NOT] LIKE, [NOT] BETWEEN, [NOT] IN) and CASEI, as
     docs/research/research-contents-pane/filter-and-labels.md reads them, ported from its experiment
     (docs/research/experiments/v173-filter/cql2-subset.js, 73 of 73 cases). The text is kept in the
     project and read by this parser into a tree of known nodes: never eval, never new Function, never
     a RegExp made from the user's text. The owner's choices (2026-11-08): D9 two values that both read
     as numbers compare as numbers; D10 != , ILIKE, UPPER() and LOWER() accepted and written back as
     <> and CASEI; D11 a backslash in a LIKE pattern makes the next character plain. Three-valued:
     a missing field is NULL, a comparison with NULL is unknown, a feature is kept only when TRUE. */
  var BIM_FLT_KW={AND:1,OR:1,NOT:1,IS:1,NULL:1,LIKE:1,ILIKE:1,BETWEEN:1,IN:1,TRUE:1,FALSE:1,CASEI:1,UPPER:1,LOWER:1};
  var BIM_FLT_MAXLEN=4000,BIM_FLT_MAXDEPTH=64;
  var BIM_FLT_NUM=/^\s*[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?\s*$/;
  var BIM_FLT_ID=/^[A-Za-z_:][A-Za-z0-9_:.]*$/;
  function BimFltError(msg,pos){this.message=msg+(pos>=0?' (at character '+(pos+1)+')':'');this.pos=pos;}
  BimFltError.prototype=new Error();
  function bimFltIdStart(c){return /[A-Za-z_:\u00c0-\u024f\u0370-\u03ff\u0400-\u04ff]/.test(c);}
  function bimFltIdPart(c){return bimFltIdStart(c)||/[0-9.]/.test(c);}
  function bimFltTokens(src){
    var t=[],i=0,n=src.length,c,s,j,buf;
    if(n>BIM_FLT_MAXLEN)throw new BimFltError('The filter is longer than '+BIM_FLT_MAXLEN+' characters',-1);
    while(i<n){
      c=src.charAt(i);
      if(/\s/.test(c)){i++;continue;}
      s=i;
      if(c==="'"){   /* text: '' or \' is a quote; \% and \_ kept whole for LIKE (D11) */
        buf='';i++;
        for(;;){
          if(i>=n)throw new BimFltError('A text value is not closed with a quote',s);
          c=src.charAt(i);
          if(c==="'"&&src.charAt(i+1)==="'"){buf+="'";i+=2;continue;}
          if(c==='\\'&&i+1<n){j=src.charAt(i+1);buf+=j==='n'?'\n':j==='t'?'\t':j==='r'?'\r':(j==='%'||j==='_')?'\\'+j:j;i+=2;continue;}
          if(c==="'"){i++;break;}
          buf+=c;i++;
        }
        t.push({k:'str',v:buf,p:s});continue;
      }
      if(c==='"'){   /* a field name in double quotes: spaces allowed, "" is a quote */
        buf='';i++;
        for(;;){
          if(i>=n)throw new BimFltError('A field name is not closed with a double quote',s);
          c=src.charAt(i);
          if(c==='"'&&src.charAt(i+1)==='"'){buf+='"';i+=2;continue;}
          if(c==='"'){i++;break;}
          buf+=c;i++;
        }
        if(!buf)throw new BimFltError('An empty field name',s);
        t.push({k:'id',v:buf,p:s});continue;
      }
      if(/[0-9]/.test(c)||((c==='-'||c==='+'||c==='.')&&/[0-9.]/.test(src.charAt(i+1)))){
        j=/^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?/.exec(src.slice(i));
        if(!j)throw new BimFltError('A number is not written correctly',s);
        i+=j[0].length;
        if(i<n&&bimFltIdPart(src.charAt(i)))throw new BimFltError('A number runs into a name',s);
        t.push({k:'num',v:parseFloat(j[0]),p:s});continue;
      }
      if(bimFltIdStart(c)){
        j=i;while(j<n&&bimFltIdPart(src.charAt(j)))j++;
        buf=src.slice(i,j);i=j;
        if(BIM_FLT_KW.hasOwnProperty(buf.toUpperCase()))t.push({k:'kw',v:buf.toUpperCase(),p:s});
        else t.push({k:'id',v:buf,p:s});
        continue;
      }
      j=src.substr(i,2);
      if(j==='<>'||j==='<='||j==='>='||j==='!='){t.push({k:'op',v:j==='!='?'<>':j,p:s});i+=2;continue;}   /* D10 */
      if('=<>(),'.indexOf(c)>=0){t.push({k:c==='('||c===')'||c===','?c:'op',v:c,p:s});i++;continue;}
      throw new BimFltError('Unexpected character '+JSON.stringify(c),s);
    }
    t.push({k:'end',p:n});
    return t;
  }
  /* OR < AND < NOT < a comparison, as CQL2's booleanExpression */
  function bimFltParseTree(src){
    var toks=bimFltTokens(String(src)),i=0,depth=0;
    function peek(){return toks[i];}
    function isKw(v){return toks[i].k==='kw'&&toks[i].v===v;}
    function say(x){return x.k==='end'?'the end':x.k==='str'?"'"+x.v+"'":String(x.v===undefined?x.k:x.v);}
    function eat(k,v){var x=toks[i];if(x.k!==k||(v!==undefined&&x.v!==v))throw new BimFltError('Expected '+(v||k)+' but found '+say(x),x.p);i++;return x;}
    function enter(){if(++depth>BIM_FLT_MAXDEPTH)throw new BimFltError('The filter nests more than '+BIM_FLT_MAXDEPTH+' levels',toks[i].p);}
    function orX(){enter();var a=[andX()];while(isKw('OR')){i++;a.push(andX());}depth--;return a.length===1?a[0]:{op:'or',args:a};}
    function andX(){var a=[notX()];while(isKw('AND')){i++;a.push(notX());}return a.length===1?a[0]:{op:'and',args:a};}
    function notX(){if(isKw('NOT')){i++;enter();var x=notX();depth--;return {op:'not',args:[x]};}return primary();}
    function primary(){
      var x=peek(),nx;
      if(x.k==='('){i++;var e=orX();eat(')');return e;}
      if(isKw('TRUE')||isKw('FALSE')){
        nx=toks[i+1];
        if(!(nx.k==='op'||(nx.k==='kw'&&/^(IS|LIKE|ILIKE|BETWEEN|IN|NOT)$/.test(nx.v)))){i++;return {lit:x.v==='TRUE'};}
      }
      return pred();
    }
    function operand(){
      var x=peek(),a;
      if(x.k==='id'){i++;return {prop:x.v};}
      if(x.k==='str'||x.k==='num'){i++;return {lit:x.v};}
      if(isKw('TRUE')||isKw('FALSE')){i++;return {lit:x.v==='TRUE'};}
      if(isKw('NULL')){i++;return {lit:null};}
      if(isKw('CASEI')||isKw('UPPER')||isKw('LOWER')){i++;eat('(');a=operand();eat(')');return {op:'casei',args:[a]};}   /* D10 */
      throw new BimFltError('Expected a field, a value or CASEI(...) but found '+say(x),x.p);
    }
    function fold(a){return a.op==='casei'?a:{op:'casei',args:[a]};}
    function pred(){
      var l=operand(),neg=false,x,lo,hi,list;
      x=peek();
      if(x.k==='op'){i++;return {op:x.v,args:[l,operand()]};}
      if(isKw('IS')){i++;if(isKw('NOT')){i++;neg=true;}eat('kw','NULL');x={op:'isNull',args:[l]};return neg?{op:'not',args:[x]}:x;}
      if(isKw('NOT')){i++;neg=true;}
      if(isKw('LIKE')){i++;x={op:'like',args:[l,operand()]};}
      else if(isKw('ILIKE')){i++;x={op:'like',args:[fold(l),fold(operand())]};}   /* D10: written back as CASEI */
      else if(isKw('BETWEEN')){i++;lo=operand();eat('kw','AND');hi=operand();x={op:'between',args:[l,lo,hi]};}
      else if(isKw('IN')){i++;eat('(');list=[operand()];while(peek().k===','){i++;list.push(operand());}eat(')');x={op:'in',args:[l,list]};}
      else throw new BimFltError('Expected a comparison (=, <>, <, >, LIKE, BETWEEN, IN, IS NULL) after '+say(toks[i-1]),peek().p);
      return neg?{op:'not',args:[x]}:x;
    }
    var tree=orX();
    if(peek().k!=='end')throw new BimFltError('Unexpected '+say(peek()),peek().p);
    return tree;
  }
  /* the text read: {tree, text (written back as CQL2), fields, warn} or {error, pos} */
  function bimFltParse(src){
    var tree,fields=[],warn='';
    function walk(n){
      var k;
      if(!n||typeof n!=='object')return;
      if(n.hasOwnProperty('prop')&&fields.indexOf(n.prop)<0)fields.push(n.prop);
      if(n.op==='in')for(k=0;k<n.args[1].length;k++)if(n.args[1][k].hasOwnProperty('lit')&&n.args[1][k].lit===null)warn='A NULL in a list makes NOT IN keep nothing, as in SQL';
      if(n.args)for(k=0;k<n.args.length;k++){if(Array.isArray(n.args[k]))n.args[k].forEach(walk);else walk(n.args[k]);}
    }
    try{tree=bimFltParseTree(src);}
    catch(e){if(e instanceof BimFltError)return {error:e.message,pos:e.pos};console.warn('[BIM] filter',e);return {error:'The filter could not be read'};}
    walk(tree);
    return {tree:tree,text:bimFltPrint(tree),fields:fields,warn:warn};
  }
  /* a value of a feature: a missing or inherited field is NULL (properties are read as own only) */
  function bimFltValue(n,props){
    var v;
    if(n.hasOwnProperty('lit'))return n.lit;
    if(n.hasOwnProperty('prop')){
      if(!props||!Object.prototype.hasOwnProperty.call(props,n.prop))return null;
      v=props[n.prop];
      return v===undefined?null:v;
    }
    if(n.op==='casei'){v=bimFltValue(n.args[0],props);return v===null?null:String(v).toLowerCase();}
    return bimFltTruth(n,props);
  }
  function bimFltNum(v){return typeof v==='number'?v:(typeof v==='string'&&BIM_FLT_NUM.test(v)?parseFloat(v):null);}
  /* D9: two values that both read as numbers compare as numbers, else as text when both are text */
  function bimFltCmp(op,a,b){
    var x,y;
    if(a===null||b===null)return null;
    x=bimFltNum(a);y=bimFltNum(b);
    if(x!==null&&y!==null){a=x;b=y;if(isNaN(a)||isNaN(b))return null;}
    else if(typeof a!==typeof b)return op==='<>'?true:(op==='='?false:null);
    if(op==='=')return a===b;
    if(op==='<>')return a!==b;
    if(op==='<')return a<b;
    if(op==='<=')return a<=b;
    if(op==='>')return a>b;
    if(op==='>=')return a>=b;
    return null;
  }
  /* LIKE without a RegExp: % any run, _ one character, \ makes the next plain (D11); O(n m) at worst */
  function bimFltLike(s,pat){
    var P=[],k,c,si=0,pi=0,starP=-1,starS=0,lit;
    for(k=0;k<pat.length;k++){
      c=pat.charAt(k);
      if(c==='\\'&&k+1<pat.length)P.push({c:pat.charAt(++k)});
      else if(c==='%'){if(!(P.length&&P[P.length-1].w==='%'))P.push({w:'%'});}
      else if(c==='_')P.push({w:'_'});
      else P.push({c:c});
    }
    while(si<s.length){
      lit=P[pi];
      if(lit&&(lit.w==='_'||(lit.c!==undefined&&lit.c===s.charAt(si)))){si++;pi++;}
      else if(lit&&lit.w==='%'){starP=pi++;starS=si;}
      else if(starP>=0){pi=starP+1;si=++starS;}
      else return false;
    }
    while(pi<P.length&&P[pi].w==='%')pi++;
    return pi===P.length;
  }
  function bimFltTruth(n,props){
    var a,b,i,r,anyNull;
    if(n.hasOwnProperty('lit'))return n.lit===null?null:!!n.lit;
    switch(n.op){
      case 'and':anyNull=false;for(i=0;i<n.args.length;i++){r=bimFltTruth(n.args[i],props);if(r===false)return false;if(r===null)anyNull=true;}return anyNull?null:true;
      case 'or':anyNull=false;for(i=0;i<n.args.length;i++){r=bimFltTruth(n.args[i],props);if(r===true)return true;if(r===null)anyNull=true;}return anyNull?null:false;
      case 'not':r=bimFltTruth(n.args[0],props);return r===null?null:!r;
      case 'isNull':return bimFltValue(n.args[0],props)===null;
      case 'like':a=bimFltValue(n.args[0],props);b=bimFltValue(n.args[1],props);if(a===null||b===null)return null;return bimFltLike(String(a),String(b));
      case 'between':
        a=bimFltValue(n.args[0],props);
        r=bimFltCmp('>=',a,bimFltValue(n.args[1],props));b=bimFltCmp('<=',a,bimFltValue(n.args[2],props));
        if(r===false||b===false)return false;
        return r===null||b===null?null:true;
      case 'in':
        a=bimFltValue(n.args[0],props);if(a===null)return null;anyNull=false;
        for(i=0;i<n.args[1].length;i++){r=bimFltCmp('=',a,bimFltValue(n.args[1][i],props));if(r===true)return true;if(r===null)anyNull=true;}
        return anyNull?null:false;
      case '=':case '<>':case '<':case '<=':case '>':case '>=':
        return bimFltCmp(n.op,bimFltValue(n.args[0],props),bimFltValue(n.args[1],props));
    }
    return null;   /* CASEI as a whole condition: unknown */
  }
  /* a feature passes only when the filter is TRUE (CQL2: FALSE or NULL leaves it out) */
  function bimFltTest(tree,props){return bimFltTruth(tree,props)===true;}
  /* the tree written back as CQL2 text */
  function bimFltOperand(n){
    if(n.hasOwnProperty('prop'))return BIM_FLT_ID.test(n.prop)&&!BIM_FLT_KW.hasOwnProperty(n.prop.toUpperCase())?n.prop:'"'+n.prop.replace(/"/g,'""')+'"';
    if(n.hasOwnProperty('lit')){
      if(n.lit===null)return 'NULL';
      if(typeof n.lit==='string')return "'"+n.lit.replace(/'/g,"''")+"'";
      if(typeof n.lit==='boolean')return n.lit?'TRUE':'FALSE';
      return String(n.lit);
    }
    if(n.op==='casei')return 'CASEI('+bimFltOperand(n.args[0])+')';
    return '('+bimFltPrint(n)+')';
  }
  function bimFltPrint(n,parent){
    var lv={or:1,and:2,not:3}[n.op]||4,s,x;
    if(n.hasOwnProperty('lit'))return n.lit?'TRUE':'FALSE';
    function list(a){return a.map(bimFltOperand).join(', ');}
    if(n.op==='or'||n.op==='and')s=n.args.map(function(a){return bimFltPrint(a,lv);}).join(' '+n.op.toUpperCase()+' ');
    else if(n.op==='not'){
      x=n.args[0];
      if(x.op==='isNull')s=bimFltOperand(x.args[0])+' IS NOT NULL';
      else if(x.op==='like')s=bimFltOperand(x.args[0])+' NOT LIKE '+bimFltOperand(x.args[1]);
      else if(x.op==='in')s=bimFltOperand(x.args[0])+' NOT IN ('+list(x.args[1])+')';
      else if(x.op==='between')s=bimFltOperand(x.args[0])+' NOT BETWEEN '+bimFltOperand(x.args[1])+' AND '+bimFltOperand(x.args[2]);
      else s='NOT '+bimFltPrint(x,3);
    }
    else if(n.op==='isNull')s=bimFltOperand(n.args[0])+' IS NULL';
    else if(n.op==='like')s=bimFltOperand(n.args[0])+' LIKE '+bimFltOperand(n.args[1]);
    else if(n.op==='in')s=bimFltOperand(n.args[0])+' IN ('+list(n.args[1])+')';
    else if(n.op==='between')s=bimFltOperand(n.args[0])+' BETWEEN '+bimFltOperand(n.args[1])+' AND '+bimFltOperand(n.args[2]);
    else s=bimFltOperand(n.args[0])+' '+n.op+' '+bimFltOperand(n.args[1]);
    return parent&&lv<parent?'('+s+')':s;
  }
  /* one clause from the builder (field, operator, value), as CQL2 text: a number stays a number */
  function bimFltClause(field,op,val){
    var f={prop:String(field||'')},v=String(val==null?'':val),lit,parts,i;
    function L(s){s=String(s).replace(/^\s+|\s+$/g,'');return BIM_FLT_NUM.test(s)?{lit:parseFloat(s)}:{lit:s};}
    if(!f.prop)return '';
    if(op==='null')return bimFltPrint({op:'isNull',args:[f]});
    if(op==='notnull')return bimFltPrint({op:'not',args:[{op:'isNull',args:[f]}]});
    if(op==='in'){parts=v.split(',');lit=[];for(i=0;i<parts.length;i++)if(parts[i].replace(/\s/g,''))lit.push(L(parts[i]));return lit.length?bimFltPrint({op:'in',args:[f,lit]}):'';}
    if(op==='like')return bimFltPrint({op:'like',args:[f,{lit:v}]});
    if(op==='contains')return bimFltPrint({op:'like',args:[{op:'casei',args:[f]},{op:'casei',args:[{lit:'%'+v.replace(/[%_]/g,'\\$&')+'%'}]}]});
    if(['=','<>','<','<=','>','>='].indexOf(op)<0)return '';
    return bimFltPrint({op:op,args:[f,L(v)]});
  }
export { bimFltClause, bimFltParse, bimFltTest };
