#!/bin/bash
# Synthesize each benchmark, simulate it, and report PASS/FAIL.
set -e
for b in test2 test3 adder4 cmp4; do
  echo "=== $b ==="
  python3 src/synth.py examples/$b.v reports/${b}_netlist.v | grep -E "Cells|Direct|Tree"
  sed "s/module top/module top_rtl/" examples/$b.v > sim/${b}_rtl.v
  verilator --binary --timing -Wno-fatal -DFUNCTIONAL -DUNIT_DELAY=#0 --top-module tb \
    -Mdir sim/obj_$b sim/tb_$b.v sim/${b}_rtl.v reports/${b}_netlist.v \
    $VDIR/primitives.v $VDIR/sky130_fd_sc_hd.v > /dev/null 2>&1
  ./sim/obj_$b/Vtb | grep -E "PASS|FAIL|MISMATCH"
done
