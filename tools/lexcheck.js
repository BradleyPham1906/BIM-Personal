// lexcheck.js FILE.html -> JSON list of [abs_start, abs_end, kind, value] for every string,
// template, regex literal and comment acorn finds, for comparison with jslex.py
var fs=require('fs'),acorn=require('acorn');
var t=fs.readFileSync(process.argv[2],'utf8'),low=t.toLowerCase();
var re=/<!--|<(script|style)\b([^>]*)>/ig,m,i=0,out=[];
for(;;){re.lastIndex=i;m=re.exec(t);if(!m)break;
  if(m[0]==='<!--'){i=t.indexOf('-->',re.lastIndex)+3;continue;}
  var tag=m[1].toLowerCase(),e=low.indexOf('</'+tag+'>',re.lastIndex);
  if(tag==='script'){var s=re.lastIndex,code=t.slice(s,e),tk=[],cm=[];
    acorn.parse(code,{ecmaVersion:'latest',allowReturnOutsideFunction:true,onToken:tk,onComment:cm});
    tk.forEach(function(x){var k=x.type.label;
      if(k==='string')out.push([s+x.start,s+x.end,'string',x.value]);
      else if(k==='template')out.push([s+x.start,s+x.end,'template',x.value]);
      else if(k==='regexp')out.push([s+x.start,s+x.end,'regex',code.slice(x.start,x.end)]);});
    cm.forEach(function(c){out.push([s+c.start,s+c.end,'comment','']);});
  }
  i=e+tag.length+3;}
process.stdout.write(JSON.stringify(out));
