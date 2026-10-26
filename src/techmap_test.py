import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parser import parser
from elaborate import elaborate, ElaborationError
from ir import build_netlist, IRBuildError
from optimize import optimize
from techmap import map_to_sky130, TechMapError

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_FILE = os.path.join(PROJECT_ROOT, "examples", "test2.v")

with open(TEST_FILE) as f:
    source = f.read()

tree = parser.parse(source)

try:
    mod = elaborate(tree)
except ElaborationError as e:
    print(f"ELABORATION ERROR: {e}")
    exit(1)

try:
    netlist = build_netlist(mod)
except IRBuildError as e:
    print(f"IR BUILD ERROR: {e}")
    exit(1)

optimized = optimize(netlist)


try:
    mapped_cells, total_area = map_to_sky130(optimized)
except TechMapError as e:
    print(f"TECH MAP ERROR: {e}")
    exit(1)

print(f"Mapped netlist for module: {optimized.name}\n")
for mc in mapped_cells:
    conns = ", ".join(f".{pin}({wire})" for pin, wire in mc.connections.items())
    print(f"  {mc.lib_cell} ( {conns} )   // area = {mc.area}")

print(f"\nTotal cells: {len(mapped_cells)}")
print(f"Total area: {total_area:.3f} um^2")
