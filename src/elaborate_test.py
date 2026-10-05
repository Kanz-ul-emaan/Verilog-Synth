import os
import sys

# Make sure we can import parser.py regardless of current directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parser import parser
from elaborate import elaborate, ElaborationError

# Project root = one directory above this file's location (src/..)
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

print(f"Module: {mod.name}")
print("Signals:")
for name, sig in mod.signals.items():
    print(f"  {name}: width={sig.width}, kind={sig.kind}")
print("Assigns:")
for a in mod.assigns:
    print(f"  {a.target} = <expr tree>")
