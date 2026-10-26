#!/usr/bin/env python3
"""V171d, patch d: what the first looks at the built panel and dome showed.

- The day studied within three days of a solstice or an equinox lies on that day's path: its own path and hours are
  not drawn again over it (on the dome and in the diagrams); through the year the sun rides the drawn path there.
- The panel's lower part -- the turning points, the diagrams, the temperature's half-year -- follows the date and the
  place as the clock or a slider moves them, drawn again when either changes.
- The diagram of the sky is the dome seen in plan (north up, east right), not looking up: its caption says so.
- Play's chosen way is marked.

Run from the repository root: python3 Phase/patch_v171d_d.py
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from p171 import begin, rep, done   # noqa: E402

begin('ca603b98753617747e7a527b848fd16c86da9e007a0ec4a0f1357d98a07e6fb4')   # after patch c

SPF = 'js/engine/site-analysis/sun-path.js'
rep(SPF, "  function bimSunMd(md){return bimSunDayText('2000-'+md).replace(/ 2000$/,'');}",
    r"""  function bimSunMd(md){return bimSunDayText('2000-'+md).replace(/ 2000$/,'');}
  /* a day within three days of a solstice or an equinox lies on its path: the drawn one stands for it */
  function bimSunNearDrawn(d){
    var m=/^(\d{4})-(\d{2})-(\d{2})$/.exec(String(d||'')),t,k,u;
    if(!m)return false;
    t=Date.UTC(+m[1],+m[2]-1,+m[3]);
    for(k=0;k<BIM_DG_SUNDAYS.length;k++){u=Date.UTC(+m[1],+BIM_DG_SUNDAYS[k][0].slice(0,2)-1,+BIM_DG_SUNDAYS[k][0].slice(3,5));if(Math.abs(t-u)<=3*864e5)return true;}
    return false;
  }""")
rep(SPF, "    var td=st.date,same=BIM_DG_SUNDAYS.some(function(B){return B[0]===String(td).slice(5);}),",
    "    var td=st.date,same=bimSunNearDrawn(td),")

SPN = 'js/engine/site-analysis/sun-panel.js'
rep(SPN, "    if(!BIM_DG_SUNDAYS.some(function(B){return B[0]===String(st.date).slice(5);}))D.push({d:st.date,c:BIM_SUN_DAYC,t:1});",
    "    if(!bimSunNearDrawn(st.date))D.push({d:st.date,c:BIM_SUN_DAYC,t:1});")
rep(SPN, "'</div><div class=\"a3d-awp-cap\">Looking up: the centre overhead, the rim the horizon; the solstices, the equinoxes, the day studied and the sun now</div>'",
    "'</div><div class=\"a3d-awp-cap\">The sky dome in plan, north up: the centre overhead, the rim the horizon; the solstices, the equinoxes, the day studied and the sun now</div>'")
rep(SPN, "    s='<svg viewBox=\"0 0 '+S+' '+S+'\" role=\"img\" aria-label=\"The sun\\'s paths, looking up\" data-sunpolar=\"1\">';",
    "    s='<svg viewBox=\"0 0 '+S+' '+S+'\" role=\"img\" aria-label=\"The sun\\'s paths on the sky dome, in plan\" data-sunpolar=\"1\">';")
rep(SPN, """    if(dkey!==A3D_SUNP.dkey){   /* another day or place: the diagrams drawn again */
      A3D_SUNP.dkey=dkey;
      e=el.propsbody.querySelector('[data-sunchart="polar"]');if(e)e.innerHTML=bimSunPolarSvg(st);
      e=el.propsbody.querySelector('[data-sunchart="height"]');if(e)e.innerHTML=bimSunHeightSvg(st);
    }else{""", """    if(dkey!==A3D_SUNP.dkey){   /* another day or place: the turning points, the diagrams and the temperature's half-year drawn again */
      A3D_SUNP.dkey=dkey;
      e=el.propsbody.querySelector('[data-sunpanel2]');if(e)e.outerHTML=bimSunChartsHtml();
    }else{""")

CSS = 'css/site-analysis/workspace.css'
rep(CSS, ".a3d-sun-mode .a3d-anzbtn.on{border-color:#ff8a8f;color:#ffd0d2}",
    ".a3d-awp .a3d-sun-mode .a3d-anzbtn.on{border-color:#ff8a8f;color:#ffd0d2;background:rgba(255,138,143,.12)}")
rep(CSS, "body.light-theme .a3d-sun-mode .a3d-anzbtn.on{border-color:#d63b41;color:#9f1d22}",
    "body.light-theme .a3d-awp .a3d-sun-mode .a3d-anzbtn.on{border-color:#d63b41;color:#9f1d22;background:rgba(214,59,65,.08)}")

done()
