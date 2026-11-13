// Isolated reproduction of the formatting branch in io/ifc-full.js; not an app integration test.
const values=[0.123456789,1234567.89,0.0000123456789,100.000041,100.000049];
function val(v){return String(Math.abs(v)>=1e-4||v===0?+v.toPrecision(6):v)}
const cases=values.map(input=>({input,display:val(input),numericError:Number(val(input))-input}));
const text='x'.repeat(205); const record={case:'ifc-format-limits',cases,distinctValuesCollapse:val(100.000041)===val(100.000049),textInputLength:text.length,textOutputLength:text.replace(/\s+/g,' ').slice(0,200).length,model:'isolated copy of format rule; not the importer'};
require('fs').writeFileSync(__dirname+'/results.json',JSON.stringify(record,null,2)); console.log(JSON.stringify(record));
