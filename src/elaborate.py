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
    # parse_tree is the 'start' node from Lark; drill down to 'module'
    module_node = parse_tree.children[0]
    assert module_node.data == "module"

    mod_name = str(module_node.children[0])
    port_list_node = module_node.children[1]
    stmt_nodes = module_node.children[2:]

    # --- Step 1: build the signals dictionary from the port list ---
    signals = {}
    for port_node in port_list_node.children:
        direction_node, name_token = port_node.children
        kind = "input" if direction_node.data == "input_dir" else "output"
        name = str(name_token)
        if name in signals:
            raise ElaborationError(f"Signal '{name}' declared more than once")
        signals[name] = Signal(name=name, width=1, kind=kind)  # width=1 for now

    # --- Step 2: process each assign statement ---

    assigns = []
    driven_signals = set()

    for stmt_node in stmt_nodes:
        assign_node = stmt_node.children[0]  # stmt -> assign_stmt
        assert assign_node.data == "assign_stmt"

        target_name = str(assign_node.children[0])
        expr_tree = assign_node.children[1]

        # Check: target must be a declared signal
        if target_name not in signals:
            raise ElaborationError(
                f"Signal '{target_name}' is assigned but was never declared as a port"
            )

        # Check: no multiple drivers
        if target_name in driven_signals:
            raise ElaborationError(
                f"Signal '{target_name}' is driven by more than one assign statement"
            )
        driven_signals.add(target_name)

        # Check: every signal referenced on the RHS must be declared
        used_names = collect_signal_refs(expr_tree)
        for name in used_names:
            if name not in signals:
                raise ElaborationError(
                    f"Signal '{name}' is used in an expression but was never declared"
                )

        assigns.append(Assign(target=target_name, expr=expr_tree))


    return ElaboratedModule(name=mod_name, signals=signals, assigns=assigns)
