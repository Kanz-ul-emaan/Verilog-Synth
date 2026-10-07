from dataclasses import dataclass, field


@dataclass
class Cell:
    type: str      # "AND", "OR", "XOR", "NOT"
    inputs: list    # list[str] wire names
    output: str      # str wire name


@dataclass
class Netlist:
    name: str
    signals: dict   # name -> Signal (from elaborate.py)
    cells: list      # list[Cell]


class IRBuildError(Exception):
    pass


# Maps Lark rule names to our cell type names
OP_MAP = {
    "and_op": "AND",
    "or_op": "OR",
    "xor_op": "XOR",
    "not_op": "NOT",
}


def build_netlist(elaborated_module):
    """

    Takes an ElaboratedModule (from elaborate.py) and flattens every
    assign statement's expression tree into a list of Cells.
    """
    cells = []
    wire_counter = [0]  # mutable counter, wrapped in a list so nested
                         # functions can modify it (see note below)

    def fresh_wire_name():
        wire_counter[0] += 1
        return f"n{wire_counter[0]}"

    def convert(tree_node, forced_name=None):
        """
        Recursively converts a Lark expression subtree into cells.
        Returns the wire name that holds this subtree's result.
        If forced_name is given, the FINAL cell created here will use
        that name as its output instead of an auto-generated one.
        """
        if tree_node.data == "signal_ref":
            # A leaf: just a reference to an existing signal, no new cell
            return str(tree_node.children[0])

        elif tree_node.data == "not_op":
            # Unary operator: one child
            input_wire = convert(tree_node.children[0])
            out_name = forced_name if forced_name else fresh_wire_name()
            cells.append(Cell(type="NOT", inputs=[input_wire], output=out_name))
            return out_name

        elif tree_node.data in ("and_op", "or_op", "xor_op"):
            # Binary operator: two children
            left_wire = convert(tree_node.children[0])

            right_wire = convert(tree_node.children[1])
            out_name = forced_name if forced_name else fresh_wire_name()
            cell_type = OP_MAP[tree_node.data]
            cells.append(Cell(type=cell_type, inputs=[left_wire, right_wire], output=out_name))
            return out_name

        else:
            raise IRBuildError(f"Unknown expression node type: {tree_node.data}")

    for assign in elaborated_module.assigns:
        convert(assign.expr, forced_name=assign.target)

    return Netlist(
        name=elaborated_module.name,
        signals=elaborated_module.signals,
        cells=cells,
    )
