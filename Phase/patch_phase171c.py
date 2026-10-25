#!/usr/bin/env python3
"""V171c: what the first runs showed, in the files V171 did not write. The app's traffic settings gain how far ahead a
car sees the next link's stop line (a short link before a signal is no surprise to it), and what a crossing costs a
walker choosing its way: a signal's wait, and each lane crossed where nothing signals it; and the turn that is a left
turn, which waits for the oncoming. Traffic and people's layer starts hidden, as a coverage's does: before a
run it has only the signals' plans and the doors to show, and Simulate shows it. SUMO's record says right of way as it is built: from the ways in, the
two sharing the highest class, or the one alone with the way in most nearly opposite it.

Run from the repository root: python3 Phase/patch_phase171c.py
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from p171 import begin, rep, done   # noqa: E402

begin('3308d93f4fc8e843433aee86c38628c8ecc0fb771bfaa77dc80ea46e681835bd')   # after 171b and the simulation's own fixes

rep('js/engine/standards/registry.js',
    "{n:'queue_v',v:2,u:'m/s',say:'a car slower than this is standing in a queue'},",
    "{n:'look',v:100,u:'m',say:'how far ahead a car sees the next street\\'s stop line'},\n"
    "          {n:'x_sig',v:30,u:'s',say:'a signalled crossing\\'s wait, as a walker weighs it choosing a way: half the shortest cycle'},\n"
    "          {n:'x_lane',v:10,u:'s',say:'each lane crossed where nothing signals it, as a walker weighs it choosing a way'},\n"
    "          {n:'left',v:30,u:'deg',say:'a turn this sharp to the left or sharper waits for the oncoming'},\n"
    "          {n:'queue_v',v:2,u:'m/s',say:'a car slower than this is standing in a queue'},")
rep('js/engine/standards/registry.js',
    "the step, the warm-up and the tallies,",
    "the step, the warm-up and the tallies, how far ahead a car sees, what a crossing costs a walker choosing a way, a left turn,")
rep('js/engine/standards/registry.js',
    "'du/acre':[' an acre',' an acre']};   /* __acad3dV171 */",
    "'du/acre':[' an acre',' an acre'],deg:['\\u00b0','\\u00b0']};   /* __acad3dV171 */")
rep('js/engine/standards/registry.js',
    "right of way to the two approaches ranked highest by priority, speed and lanes;",
    "right of way from the ways in: the two sharing the highest priority (then speed and lanes), or the one alone with the way in most nearly opposite it;")
rep('js/engine/standards/registry.js',
    "{id:'traffic',name:'Traffic and people',col:'#ffb454'},",
    "{id:'traffic',name:'Traffic and people',col:'#ffb454',hidden:true},")
done()
