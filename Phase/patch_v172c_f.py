#!/usr/bin/env python3
"""V172c, patch f: what a Ladybug study depends on, exactly.
- A study kept the whole stamp (bimSimStamp), which holds the site's date and time: a new date marked radiation out of
  date, which does not read it. A study now keeps the stamp as V148's sun hours keep theirs (bimResKeyFrom: the model,
  its north, the site's place, not the date), and direct sun on the day studied says so when that day changes.
Run from the repository root: python3 Phase/patch_v172c_f.py
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from p171 import begin, rep, done   # noqa: E402

begin('953f222b82173be447a0880bf4f29b34c5cfc9d78528cbc3da9e45c21b0e0f00')   # patch e
S = 'js/engine/ladybug/studies.js'
rep(S, "    if(R.stamp!==bimSimStamp())why.push('the model, its north or the site\\'s place has changed');\n",
    "    if(R.stamp!==bimResKeyFrom(bimSimStamp(),'sunhours'))why.push('the model, its north or the site\\'s place has changed');\n"
    "    if(k==='sun'&&R.params&&R.params.span!=='year'&&R.params.date!==bimSunSettings().date)why.push('the day studied has changed');\n")
rep(S, "    var stamp=bimSimStamp(),t0=Date.now(),", "    var stamp=bimResKeyFrom(bimSimStamp(),'sunhours'),t0=Date.now(),")
done()
