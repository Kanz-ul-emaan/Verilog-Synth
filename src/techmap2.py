import sys
from itertools import product

from techmap import MappedCell, TechMapError

sys.setrecursionlimit(10000)

P = "sky130_fd_sc_hd__"

# pattern: ("N",x,y)=NAND2  ("I",x)=INV  ("B",x)=BUF  "name"=leaf
# pins: library pin -> pattern leaf name.   Areas verified from the .lib (um^2)
_XOR = ("N", ("N", "a", ("I", "b")), ("N", ("I", "a"), "b"))
_A21O = ("N", ("N", "a", "b"), ("I", "c"))
_A22O = ("N", ("N", "a", "b"), ("N", "c", "d"))
_O21AI = ("N", ("N", ("I", "a"), ("I", "b")), "c")

LIB = [
    {"cell": P+"inv_1",   "area": 3.7536, "pat": ("I", "a"), "pins": {"A": "a"}, "out": "Y",
     "func": lambda v: 1 - v["a"]},
    {"cell": P+"buf_1",   "area": 3.7536, "pat": ("B", "a"), "pins": {"A": "a"}, "out": "X",
     "func": lambda v: v["a"]},
    {"cell": P+"nand2_1", "area": 3.7536, "pat": ("N", "a", "b"), "pins": {"A": "a", "B": "b"}, "out": "Y",
     "func": lambda v: 1 - (v["a"] & v["b"])},
    {"cell": P+"nor2_1",  "area": 3.7536, "pat": ("I", ("N", ("I", "a"), ("I", "b"))),
     "pins": {"A": "a", "B": "b"}, "out": "Y",
     "func": lambda v: 1 - (v["a"] | v["b"])},
    {"cell": P+"and2_1",  "area": 6.256,  "pat": ("I", ("N", "a", "b")), "pins": {"A": "a", "B": "b"}, "out": "X",
     "func": lambda v: v["a"] & v["b"]},
    {"cell": P+"or2_1",   "area": 6.256,  "pat": ("N", ("I", "a"), ("I", "b")), "pins": {"A": "a", "B": "b"}, "out": "X",
     "func": lambda v: v["a"] | v["b"]},
    {"cell": P+"xor2_1",  "area": 8.7584, "pat": _XOR, "pins": {"A": "a", "B": "b"}, "out": "X",
     "func": lambda v: v["a"] ^ v["b"]},

    {"cell": P+"xnor2_1", "area": 8.7584, "pat": ("I", _XOR), "pins": {"A": "a", "B": "b"}, "out": "Y",
     "func": lambda v: 1 - (v["a"] ^ v["b"])},
    {"cell": P+"nand3_1", "area": 5.0048, "pat": ("N", ("I", ("N", "a", "b")), "c"),
     "pins": {"A": "a", "B": "b", "C": "c"}, "out": "Y",
     "func": lambda v: 1 - (v["a"] & v["b"] & v["c"])},
    {"cell": P+"a21o_1",  "area": 7.5072, "pat": _A21O, "pins": {"A1": "a", "A2": "b", "B1": "c"}, "out": "X",
     "func": lambda v: (v["a"] & v["b"]) | v["c"]},
    {"cell": P+"a21oi_1", "area": 5.0048, "pat": ("I", _A21O), "pins": {"A1": "a", "A2": "b", "B1": "c"}, "out": "Y",
     "func": lambda v: 1 - ((v["a"] & v["b"]) | v["c"])},
    {"cell": P+"a22o_1",  "area": 8.7584, "pat": _A22O,
     "pins": {"A1": "a", "A2": "b", "B1": "c", "B2": "d"}, "out": "X",
     "func": lambda v: (v["a"] & v["b"]) | (v["c"] & v["d"])},
    {"cell": P+"a22oi_1", "area": 7.5072, "pat": ("I", _A22O),
     "pins": {"A1": "a", "A2": "b", "B1": "c", "B2": "d"}, "out": "Y",
     "func": lambda v: 1 - ((v["a"] & v["b"]) | (v["c"] & v["d"]))},
    {"cell": P+"o21a_1",  "area": 7.5072, "pat": ("I", _O21AI), "pins": {"A1": "a", "A2": "b", "B1": "c"}, "out": "X",
     "func": lambda v: (v["a"] | v["b"]) & v["c"]},
    {"cell": P+"o21ai_1", "area": 5.0048, "pat": _O21AI, "pins": {"A1": "a", "A2": "b", "B1": "c"}, "out": "Y",
     "func": lambda v: 1 - ((v["a"] | v["b"]) & v["c"])},
]


def _eval_pat(pat, env):
    if isinstance(pat, str):
        return env[pat]
    if pat[0] == "I":
        return 1 - _eval_pat(pat[1], env)
    if pat[0] == "B":
        return _eval_pat(pat[1], env)
    return 1 - (_eval_pat(pat[1], env) & _eval_pat(pat[2], env))



def selfcheck():
    """Every pattern must compute exactly the function of its library cell."""
    for e in LIB:
        names = sorted(set(e["pins"].values()))
        for vals in product([0, 1], repeat=len(names)):
            env = dict(zip(names, vals))
            if _eval_pat(e["pat"], env) != e["func"](env):
                raise AssertionError(f"Pattern mismatch for {e['cell']} at {env}")


class Node:
    def __init__(self, kind, a=None, b=None, name=None):
        self.kind = kind      # "IN", "INV", "NAND", "BUF"
        self.a = a
        self.b = b
        self.name = name
        self.is_root = False  # tree boundary (shared signal or output port)


_KIND = {"N": "NAND", "I": "INV", "B": "BUF"}


def _match(pat, node, bind, top=False):
    """Yield every way pattern 'pat' fits the subject tree rooted at 'node'."""
    if isinstance(pat, str):
        if pat in bind:
            if bind[pat] is node:
                yield bind
        else:
            nb = dict(bind)
            nb[pat] = node
            yield nb

        return
    if node.kind != _KIND[pat[0]]:
        return
    if node.is_root and not top:
        return                      # interior pattern node can't be a shared signal
    if pat[0] in ("I", "B"):
        yield from _match(pat[1], node.a, bind)
    else:
        for l, r in ((node.a, node.b), (node.b, node.a)):   # NAND is commutative
            for b1 in _match(pat[1], l, bind):
                yield from _match(pat[2], r, b1)


def tree_map(netlist):
    """Returns (list[MappedCell], total_area)."""
    # ---------- Step 1: subject graph (NAND2 / INV only) ----------
    sig = {}
    for name, s in netlist.signals.items():
        if s.kind == "input":
            sig[name] = Node("IN", name=name)

    inv = lambda x: Node("INV", x)
    nand = lambda x, y: Node("NAND", x, y)
    ties = []
    tie_names = set()

    for c in netlist.cells:
        if c.type in ("TIE0", "TIE1"):
            pin = "HI" if c.type == "TIE1" else "LO"
            ties.append(MappedCell(lib_cell=P + "conb_1", connections={pin: c.output}, area=3.7536))
            tie_names.add(c.output)
            sig[c.output] = Node("IN", name=c.output)
            continue
        try:
            ins = [sig[w] for w in c.inputs]
        except KeyError as e:
            raise TechMapError(f"Signal {e} is used before it is driven")
        if c.type == "AND":
            out = inv(nand(ins[0], ins[1]))
        elif c.type == "OR":

            out = nand(inv(ins[0]), inv(ins[1]))
        elif c.type == "XOR":
            x, y = ins
            out = nand(nand(x, inv(y)), nand(inv(x), y))
        elif c.type == "NOT":
            out = inv(ins[0])
        elif c.type == "BUF":
            out = Node("BUF", ins[0])
        else:
            raise TechMapError(f"Unsupported cell type {c.type}")
        out.name = c.output
        sig[c.output] = out

    outs = []
    for p, s in netlist.signals.items():
        if s.kind == "output" and p not in tie_names:
            if p not in sig or sig[p].kind == "IN":
                raise TechMapError(f"Output '{p}' is not driven by any gate")
            outs.append((p, sig[p]))

    def analyze():
        order, seen, fan = [], set(), {}

        def visit(n):
            if id(n) in seen:
                return
            seen.add(id(n))
            order.append(n)
            for ch in (n.a, n.b):
                if ch is not None:
                    fan[id(ch)] = fan.get(id(ch), 0) + 1
                    visit(ch)


        for _, n in outs:
            fan[id(n)] = fan.get(id(n), 0) + 1   # an output port counts as a user
            visit(n)
        return order, fan

    # Collapse INV(INV(x)) where the inner inverter has no other user
    order, fan = analyze()
    for n in order:
        for attr in ("a", "b"):
            c = getattr(n, attr)
            while c is not None and c.kind == "INV" and c.a.kind == "INV" and fan[id(c.a)] == 1:
                c = c.a.a
            setattr(n, attr, c)

    # ---------- Step 2: tree boundaries ----------
    order, fan = analyze()
    for n in order:
        n.is_root = n.kind != "IN" and fan[id(n)] > 1
    for _, n in outs:
        n.is_root = True

    counter = [0]

    def fresh():
        counter[0] += 1
        return f"_m{counter[0]}"

    for n in order:
        if n.is_root and n.name is None:
            n.name = fresh()


    # ---------- Step 3: minimum-cost cover ----------
    memo = {}

    def best(node):
        key = id(node)
        if key in memo:
            return memo[key]
        best_cost, best_choice = None, None
        for entry in LIB:
            for bind in _match(entry["pat"], node, {}, top=True):
                cost = entry["area"]
                for leaf in {id(l): l for l in bind.values()}.values():
                    if leaf.kind != "IN" and not leaf.is_root:
                        cost += best(leaf)[0]
                if best_cost is None or cost < best_cost - 1e-9:
                    best_cost, best_choice = cost, (entry, bind)
        if best_cost is None:
            raise TechMapError("No library pattern matches a node (INV and NAND2 must exist)")
        memo[key] = (best_cost, best_choice)
        return memo[key]

    cells = list(ties)

    def cover(node, out_wire):
        entry, bind = best(node)[1]
        conns = {}
        for pin, var in entry["pins"].items():
            leaf = bind[var]
            if leaf.kind == "IN" or leaf.is_root:
                conns[pin] = leaf.name
            else:
                w = fresh()

                cover(leaf, w)
                conns[pin] = w
        conns[entry["out"]] = out_wire
        cells.append(MappedCell(lib_cell=entry["cell"], connections=conns, area=entry["area"]))

    for n in order:
        if n.is_root and n.kind != "IN":
            cover(n, n.name)

    return cells, sum(c.area for c in cells)
