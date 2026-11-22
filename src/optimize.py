from ir import Cell, Netlist

COMMUTATIVE = {"AND", "OR", "XOR"}
ZERO = "1'b0"
ONE = "1'b1"
CONSTS = (ZERO, ONE)


def optimize(netlist):
    """
    Structural + Boolean-identity optimization:
      - common-subexpression elimination
      - idempotence, double negation
      - complement rules (a&~a=0, a|~a=1, a^~a=1, a^a=0)
      - absorption (x|(x&y)=x, x&(x|y)=x)
      - constant propagation
      - dead-gate removal
    """
    renames = {}      # old wire -> replacement wire (or constant)
    seen = {}         # (type, inputs) -> wire already computing it
    producer = {}     # wire -> Cell that drives it
    new_cells = []

    def resolve(w):
        while w in renames:
            w = renames[w]
        return w

    def emit(ctype, inputs, output):
        c = Cell(type=ctype, inputs=inputs, output=output)
        new_cells.append(c)
        producer[output] = c


    def alias(out, target):
        """Make 'out' equal to 'target'. Port names must keep existing."""
        if out in netlist.signals:
            if target in CONSTS:
                emit("TIE1" if target == ONE else "TIE0", [], out)
            else:
                emit("BUF", [target], out)
        else:
            renames[out] = target

    def is_not_of(a, b):
        p = producer.get(a)
        return p is not None and p.type == "NOT" and p.inputs[0] == b

    def complementary(a, b):
        return is_not_of(a, b) or is_not_of(b, a)

    def contains(w, ctype, x):
        p = producer.get(w)
        return p is not None and p.type == ctype and x in p.inputs

    def simplify(t, ins):
        """Return a wire/constant name, ('NOT',[w]) to rewrite, or None."""
        if t == "BUF":
            return ins[0]
        if t == "NOT":
            x = ins[0]
            if x == ZERO:
                return ONE
            if x == ONE:
                return ZERO

            p = producer.get(x)
            if p is not None and p.type == "NOT":
                return p.inputs[0]
            return None

        x, y = ins
        if t == "AND":
            if x == ZERO or y == ZERO:
                return ZERO
            if x == ONE:
                return y
            if y == ONE:
                return x
            if x == y:
                return x
            if complementary(x, y):
                return ZERO
            if contains(y, "OR", x):
                return x
            if contains(x, "OR", y):
                return y
        elif t == "OR":
            if x == ONE or y == ONE:
                return ONE
            if x == ZERO:
                return y
            if y == ZERO:
                return x
            if x == y:
                return x
            if complementary(x, y):
                return ONE

            if contains(y, "AND", x):
                return x
            if contains(x, "AND", y):
                return y
        elif t == "XOR":
            if x == ZERO:
                return y
            if y == ZERO:
                return x
            if x == ONE:
                return ("NOT", [y])
            if y == ONE:
                return ("NOT", [x])
            if x == y:
                return ZERO
            if complementary(x, y):
                return ONE
        return None

    for cell in netlist.cells:
        t = cell.type
        ins = [resolve(w) for w in cell.inputs]

        while True:
            r = simplify(t, ins)
            if isinstance(r, tuple):
                t, ins = r
                continue
            break

        if r is not None:
            alias(cell.output, r)

            continue

        key = (t, tuple(sorted(ins))) if t in COMMUTATIVE else (t, tuple(ins))
        if key in seen:
            alias(cell.output, seen[key])
            continue

        emit(t, ins, cell.output)
        seen[key] = cell.output

    # ---- dead-gate removal: keep only logic that feeds an output ----
    live = {p for p, s in netlist.signals.items() if s.kind == "output"}
    kept = []
    for c in reversed(new_cells):
        if c.output in live:
            kept.append(c)
            live.update(c.inputs)
    kept.reverse()

    return Netlist(name=netlist.name, signals=netlist.signals, cells=kept)
