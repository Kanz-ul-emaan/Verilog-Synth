import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parser import parser
from elaborate import elaborate, ElaborationError
from ir import build_netlist, IRBuildError
from optimize import optimize

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_FILE = os.path.join(PROJECT_ROOT, "examples", "test2.v")


def print_netlist(netlist, label):
    print(f"--- {label} ---")
    for cell in netlist.cells:
        inputs_str = ", ".join(cell.inputs)
        print(f"  {cell.output} = {cell.type}({inputs_str})")
    print(f"  Total cells: {len(netlist.cells)}\n")


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

print_netlist(netlist, "BEFORE optimization")

optimized = optimize(netlist)

print_netlist(optimized, "AFTER optimization")
