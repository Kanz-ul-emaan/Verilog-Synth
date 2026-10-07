import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parser import parser
from elaborate import elaborate, ElaborationError
from ir import build_netlist, IRBuildError

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_FILE = os.path.join(PROJECT_ROOT, "examples", "test1.v")

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

print(f"Netlist for module: {netlist.name}")
print("\nPrimary signals:")
for name, sig in netlist.signals.items():

    print(f"  {sig.kind:6s} {name} (width={sig.width})")

print("\nCells (in dependency order):")
for cell in netlist.cells:
    inputs_str = ", ".join(cell.inputs)
    print(f"  {cell.output} = {cell.type}({inputs_str})")
