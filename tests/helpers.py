import itertools
from parser import parser
from elaborate import elaborate
from ir import build_netlist
from optimize import optimize
from techmap import map_to_sky130
from techmap2 import tree_map


def synth(source):
    """Run text through every stage. Returns (raw, optimized) netlists."""
    mod = elaborate(parser.parse(source))
    raw = build_netlist(mod)
    return raw, optimize(raw)


def simulate(netlist, inputs):
    """Evaluate an abstract netlist for a dict {input: 0/1}. Returns {output: 0/1}."""
    val = dict(inputs)
    val["1'b0"], val["1'b1"] = 0, 1
    for c in netlist.cells:
        i = [val[w] for w in c.inputs]
        t = c.type
        if t == "AND": v = i[0] & i[1]
        elif t == "OR": v = i[0] | i[1]
        elif t == "XOR": v = i[0] ^ i[1]
        elif t == "NOT": v = 1 - i[0]
        elif t == "BUF": v = i[0]
        elif t == "TIE0": v = 0
        elif t == "TIE1": v = 1
        else: raise ValueError(t)
        val[c.output] = v

    return {p: val[p] for p, s in netlist.signals.items() if s.kind == "output"}


def input_names(netlist):
    return [p for p, s in netlist.signals.items() if s.kind == "input"]


def all_inputs(netlist):
    names = input_names(netlist)
    for bits in itertools.product([0, 1], repeat=len(names)):
        yield dict(zip(names, bits))


def equivalent(a, b):
    """Exhaustive equivalence of two netlists with the same ports."""
    return all(simulate(a, v) == simulate(b, v) for v in all_inputs(a))
