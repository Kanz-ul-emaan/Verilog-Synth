from dataclasses import dataclass, field


@dataclass
class Signal:
    name: str
    width: int
    kind: str  # "input" or "output"


@dataclass
class Assign:
    target: str
    expr: object  # the Lark tree for the RHS expression, for now


@dataclass
class ElaboratedModule:
    name: str
    signals: dict  # name -> Signal
    assigns: list  # list[Assign]


class ElaborationError(Exception):
    pass


def collect_signal_refs(expr_tree):
    """
    Walk an expression subtree and return the set of all signal names
    referenced anywhere inside it (signal_ref leaves).
    """

    names = set()
    # Lark trees have .data (the rule name) and .children
    # A signal_ref node's single child is a Token holding the name.
    if hasattr(expr_tree, "data"):
        if expr_tree.data == "signal_ref":
            names.add(str(expr_tree.children[0]))
        else:
            for child in expr_tree.children:
                names |= collect_signal_refs(child)
    return names


def elaborate(parse_tree):
    module_node = parse_tree.children[0]
    assert module_node.data == "module"

    mod_name = str(module_node.children[0])
    port_list_node = module_node.children[1]
    stmt_nodes = module_node.children[2:]

    # --- Step 1: ports ---
    signals = {}
    for port_node in port_list_node.children:
        direction_node, name_token = port_node.children
        kind = "input" if direction_node.data == "input_dir" else "output"
        name = str(name_token)
        if name in signals:
            raise ElaborationError(f"Signal '{name}' declared more than once")
        signals[name] = Signal(name=name, width=1, kind=kind)

    # --- Step 2: wires and assign statements ---
    wires = set()
    assign_nodes = []
    for stmt_node in stmt_nodes:
        inner = stmt_node.children[0]
        if inner.data == "wire_decl":
            for tok in inner.children:
                n = str(tok)
                if n in signals or n in wires:
                    raise ElaborationError(f"Signal '{n}' declared more than once")
                wires.add(n)
        else:
            assign_nodes.append(inner)


    # --- Step 3: check and collect assigns ---
    assigns = []
    driven_signals = set()
    for assign_node in assign_nodes:
        target_name = str(assign_node.children[0])
        expr_tree = assign_node.children[1]

        if target_name not in signals and target_name not in wires:
            raise ElaborationError(
                f"Signal '{target_name}' is assigned but was never declared"
            )
        if target_name in signals and signals[target_name].kind == "input":
            raise ElaborationError(f"Input '{target_name}' cannot be assigned")
        if target_name in driven_signals:
            raise ElaborationError(
                f"Signal '{target_name}' is driven by more than one assign statement"
            )
        driven_signals.add(target_name)

        for name in collect_signal_refs(expr_tree):
            if name not in signals and name not in wires:
                raise ElaborationError(
                    f"Signal '{name}' is used in an expression but was never declared"
                )

        assigns.append(Assign(target=target_name, expr=expr_tree))

    return ElaboratedModule(name=mod_name, signals=signals, assigns=assigns)
