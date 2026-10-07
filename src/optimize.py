from ir import Cell, Netlist

COMMUTATIVE = {"AND", "OR", "XOR"}


def optimize(netlist):
    """
    Takes a Netlist and returns a new, optimized Netlist with:
      - Common subexpression elimination (duplicate cells merged)
      - Idempotence simplification: AND(x,x)=x, OR(x,x)=x
      - Double negation elimination: NOT(NOT(x))=x
    """
    renames = {}     # old wire name -> canonical wire name
    seen = {}         # (type, inputs-key) -> canonical wire name
    producer = {}      # wire name -> the Cell (in new_cells) that drives it
    new_cells = []

    def resolve(wire):
        # Follow the rename chain until we reach a wire that's not renamed
        while wire in renames:
            wire = renames[wire]
        return wire

    def keep_as_alias(original_output, canonical_wire):
        """
        Decide how to eliminate a redundant cell's output:
        - if the name is a real primary port (must be preserved exactly),
          emit a BUF cell so that name still exists in the netlist
        - otherwise, just record a rename so later cells use the
          canonical wire directly
        """
        if original_output in netlist.signals:

            buf = Cell(type="BUF", inputs=[canonical_wire], output=original_output)
            new_cells.append(buf)
            producer[original_output] = buf
        else:
            renames[original_output] = canonical_wire

    for cell in netlist.cells:
        inputs = [resolve(w) for w in cell.inputs]

        # --- Double negation: NOT(NOT(x)) = x ---
        if cell.type == "NOT":
            src = inputs[0]
            if src in producer and producer[src].type == "NOT":
                original_x = producer[src].inputs[0]
                keep_as_alias(cell.output, original_x)
                continue

        # --- Idempotence: AND(x,x)=x , OR(x,x)=x ---
        if cell.type in ("AND", "OR") and len(inputs) == 2 and inputs[0] == inputs[1]:
            keep_as_alias(cell.output, inputs[0])
            continue

        # --- Common subexpression elimination ---
        if cell.type in COMMUTATIVE:
            key = (cell.type, tuple(sorted(inputs)))
        else:
            key = (cell.type, tuple(inputs))

        if key in seen:
            canonical = seen[key]
            keep_as_alias(cell.output, canonical)
            continue


        # Genuinely new cell: keep it
        new_cell = Cell(type=cell.type, inputs=inputs, output=cell.output)
        new_cells.append(new_cell)
        seen[key] = cell.output
        producer[cell.output] = new_cell

    return Netlist(name=netlist.name, signals=netlist.signals, cells=new_cells)
