def write_netlist(netlist, mapped_cells, path):
    """
    Writes a structural Verilog file using Sky130 cell instances.
    netlist: the optimized Netlist (for module name and ports)
    mapped_cells: list[MappedCell] from techmap.py
    """
    ports = list(netlist.signals.values())
    port_names = ", ".join(p.name for p in ports)

    # Internal wires = every wire used by a cell that is not a primary port
    port_set = set(netlist.signals.keys())
    internal = []
    for mc in mapped_cells:
        for pin, wire in mc.connections.items():
            if wire not in port_set and wire not in internal:
                internal.append(wire)

    lines = []
    lines.append(f"module {netlist.name}({port_names});")
    for p in ports:
        lines.append(f"  {p.kind} {p.name};")
    for w in internal:
        lines.append(f"  wire {w};")
    lines.append("")

    for i, mc in enumerate(mapped_cells):
        conns = ", ".join(f".{pin}({wire})" for pin, wire in mc.connections.items())
        lines.append(f"  {mc.lib_cell} u{i} ({conns});")

    lines.append("endmodule")

    with open(path, "w") as f:

        f.write("\n".join(lines) + "\n")
