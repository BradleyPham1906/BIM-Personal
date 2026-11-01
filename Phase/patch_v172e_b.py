#!/usr/bin/env python3
"""V172e, patch b: found by the suite's refused template. A database that refuses at once -- open throwing, or a
transaction refused before it starts -- answered its callback synchronously, inside the call; a template's entry,
pushed after the call, was then never taken back out. Every answer of bimIdbTx now comes after the call returns, as
an IndexedDB request's always does, so a caller's code after the call has run before its callback.

Run from the repository root: python3 Phase/patch_v172e_b.py
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from p171 import begin, rep, done   # noqa: E402

begin('fc24c010c0bc517b1e1ef90efe4cc00c1eea298beebeed4944e050c348a7cc54')   # patch a

rep('js/engine/core/idb-store.js',
    "  /* one transaction on the projects store; done(err, value) once it has committed or failed */\n"
    "  function bimIdbTx(mode,work,done,again){\n"
    "    bimIdbOpen(function(err,db){\n"
    "      if(err){done(err);return;}\n"
    "      var tx,out={},ended=false;\n"
    "      function end(e,v){if(ended)return;ended=true;done(e,v);}\n",
    "  /* one transaction on the projects store; done(err, value) once it has committed or failed -- always after the\n"
    "     call has returned (__acad3dV172e: a refusal at once answered inside the call) */\n"
    "  function bimIdbTx(mode,work,done,again){\n"
    "    bimIdbOpen(function(err,db){\n"
    "      if(err){setTimeout(function(){done(err);},0);return;}\n"
    "      var tx,out={},ended=false;\n"
    "      function end(e,v){if(ended)return;ended=true;setTimeout(function(){done(e,v);},0);}\n")
done()
