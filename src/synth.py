import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parser import parser
from elaborate import elaborate, ElaborationError
from ir import build_netlist
from optimize import optimize
from techmap import map_to_sky130
from techmap2 import tree_map, selfcheck
from backend import write_netlist

if len(sys.argv) not in (3, 4):
    print("Usage: python3 src/synth.py input.v output.v [tree|direct]")
    sys.exit(1)

in_path, out_path = sys.argv[1], sys.argv[2]
mode = sys.argv[3] if len(sys.argv) == 4 else "tree"

selfcheck()

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

direct_cells, direct_area = map_to_sky130(optimized)
tree_cells, tree_area = tree_map(optimized)

mapped, area = (tree_cells, tree_area) if mode == "tree" else (direct_cells, direct_area)
write_netlist(optimized, mapped, out_path)

print(f"Cells before logic optimization: {len(netlist.cells)}")
print(f"Cells after logic optimization:  {len(optimized.cells)}")
print(f"Direct mapping : {len(direct_cells):3d} cells, {direct_area:.4f} um^2")
print(f"Tree covering  : {len(tree_cells):3d} cells, {tree_area:.4f} um^2")
if direct_area > 0:
    print(f"Area saved by tree covering: {100 * (direct_area - tree_area) / direct_area:.1f}%")
print(f"Wrote {out_path} (mode = {mode})")
print("Cell usage:")
for name, n in sorted(Counter(c.lib_cell.replace('sky130_fd_sc_hd__', '') for c in mapped).items()):
    print(f"  {name}: {n}")
