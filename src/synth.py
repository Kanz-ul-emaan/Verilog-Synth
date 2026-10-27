import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parser import parser
from elaborate import elaborate, ElaborationError
from ir import build_netlist
from optimize import optimize
from techmap import map_to_sky130
from backend import write_netlist

if len(sys.argv) != 3:
    print("Usage: python3 src/synth.py input.v output.v")
    sys.exit(1)

in_path, out_path = sys.argv[1], sys.argv[2]

with open(in_path) as f:
    source = f.read()

tree = parser.parse(source)

try:
    mod = elaborate(tree)
except ElaborationError as e:
    print(f"ELABORATION ERROR: {e}")
    sys.exit(1)

netlist = build_netlist(mod)
optimized = optimize(netlist)
mapped, area = map_to_sky130(optimized)

write_netlist(optimized, mapped, out_path)

print(f"Cells before optimization: {len(netlist.cells)}")
print(f"Cells after optimization:  {len(optimized.cells)}")
print(f"Total area: {area:.4f} um^2")
print(f"Wrote {out_path}")
