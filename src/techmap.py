
from dataclasses import dataclass

# Areas read directly from sky130_fd_sc_hd__tt_025C_1v80.lib (um^2)
SKY130_CELL_MAP = {
    "AND":  {"cell": "sky130_fd_sc_hd__and2_1",  "area": 6.256,  "pins": ["A", "B"], "out_pin": "X"},
    "OR":   {"cell": "sky130_fd_sc_hd__or2_1",   "area": 6.256,  "pins": ["A", "B"], "out_pin": "X"},
    "XOR":  {"cell": "sky130_fd_sc_hd__xor2_1",  "area": 8.7584, "pins": ["A", "B"], "out_pin": "X"},
    "NOT":  {"cell": "sky130_fd_sc_hd__inv_1",   "area": 3.7536, "pins": ["A"],      "out_pin": "Y"},
    "BUF":  {"cell": "sky130_fd_sc_hd__buf_1",   "area": 3.7536, "pins": ["A"],      "out_pin": "X"},
    "TIE0": {"cell": "sky130_fd_sc_hd__conb_1", "area": 3.7536, "pins": [], "out_pin": "LO"},
    "TIE1": {"cell": "sky130_fd_sc_hd__conb_1", "area": 3.7536, "pins": [], "out_pin": "HI"},
}

@dataclass
class MappedCell:
    lib_cell: str
    connections: dict   # pin name -> wire name
    area: float


class TechMapError(Exception):
    pass


def map_to_sky130(netlist):
    mapped_cells = []
    total_area = 0.0

    for cell in netlist.cells:
        if cell.type not in SKY130_CELL_MAP:
            raise TechMapError(f"No Sky130 mapping defined for cell type '{cell.type}'")

        info = SKY130_CELL_MAP[cell.type]

        if len(cell.inputs) != len(info["pins"]):
            raise TechMapError(
                f"Cell '{cell.type}' expects {len(info['pins'])} input(s), "
                f"got {len(cell.inputs)}"
            )

        connections = {}
        for pin_name, wire_name in zip(info["pins"], cell.inputs):
            connections[pin_name] = wire_name
        connections[info["out_pin"]] = cell.output

        mapped_cells.append(
            MappedCell(lib_cell=info["cell"], connections=connections, area=info["area"])
        )
        total_area += info["area"]

    return mapped_cells, total_area
