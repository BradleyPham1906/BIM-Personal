#!/usr/bin/env python3
"""V171c: what the first runs showed, in the files V171 did not write. The app's traffic settings gain how far ahead a
car sees the next link's stop line (a short link before a signal is no surprise to it), and what a crossing costs a
walker choosing its way: a signal's wait, and each lane crossed where nothing signals it; and the turn that is a left
turn, which waits for the oncoming.

Run from the repository root: python3 Phase/patch_phase171c.py
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from p171 import begin, rep, done   # noqa: E402

begin('6f0acd3e02810f2d6d07f7e0aba36f97af0b4c222ef3fe7e26efb452e1ef3fb4')   # after 171b and the simulation's own fixes

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
done()
