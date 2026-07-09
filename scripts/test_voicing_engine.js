#!/usr/bin/env python3
"""Smoke test do motor de voicings (Node necessário)."""

import json
import subprocess
import sys

JS = r"""
var CD = {};
(function(){
  %s
})();
(function(){
  %s
})();
(function(){
  %s
})();
var tuning = ['E','A','D','G','B','E'];
var notes = ['A','C','E','G'];
var v = CD.discoverVoicings(tuning, notes, 3);
if (!v.length) { console.error('no voicings'); process.exit(1); }
var f = CD.assignAutoFingers(v[0].frets);
console.log(JSON.stringify({ count: v.length, first: v[0].frets, fingers: f }));
""" % (
    open('/root/Uníssono/static/js/chord-diagram/constants.js').read().replace('UníssonoChordDiagram', 'CD'),
    open('/root/Uníssono/static/js/chord-diagram/theory.js').read().split('COMMON_SHAPES')[0] + 'CD.COMMON_SHAPES={};' + open('/root/Uníssono/static/js/chord-diagram/theory.js').read().split('COMMON_SHAPES',1)[1] if False else '',
    '',
)

# Simpler inline test
TEST = """
const fs = require('fs');
const vm = require('vm');
const ctx = { window: {}, globalThis: {} };
ctx.window = ctx;
ctx.globalThis = ctx;
function load(p) { vm.runInNewContext(fs.readFileSync(p,'utf8'), ctx); }
load('/root/Uníssono/static/js/chord-diagram/constants.js');
load('/root/Uníssono/static/js/chord-diagram/theory.js');
load('/root/Uníssono/static/js/chord-diagram/voicing-engine.js');
load('/root/Uníssono/static/js/chord-diagram/auto-finger.js');
const CD = ctx.UníssonoChordDiagram;
const v = CD.discoverVoicings(CD.TUNINGS.violao, ['A','C','E','G'], 3);
if (!v.length) { console.error('fail'); process.exit(1); }
console.log('ok', v.length, JSON.stringify(v[0].frets));
"""

if __name__ == '__main__':
    r = subprocess.run(['node', '-e', TEST], capture_output=True, text=True)
    print(r.stdout or r.stderr)
    sys.exit(r.returncode)
