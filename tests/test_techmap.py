import itertools
from helpers import synth
from techmap2 import selfcheck, tree_map, LIB


def test_library_patterns_match_cell_functions():
    selfcheck()


def test_and_or_chain_uses_two_cells():
    _, opt = synth("module top(input a, input b, input c, output f1, output f2);"
                   " assign f1 = a & b; assign f2 = f1 | c; endmodule")
    cells, area = tree_map(opt)
    assert len(cells) == 2 and abs(area - 12.512) < 1e-6


def test_carry_collapses_to_a22o():
    _, opt = synth("module top(input a, input b, input c, input p, output y);"
                   " assign y = (a & b) | (c & p); endmodule")
    cells, _ = tree_map(opt)
    assert [c.lib_cell for c in cells] == ["sky130_fd_sc_hd__a22o_1"]


def test_tree_never_costs_more_than_direct():
    from techmap import map_to_sky130
    for src in ["module top(input a, input b, input c, output y); assign y = (a ^ b) & ~c; endmodule",
                "module top(input a, input b, input c, output y); assign y = ~((a | b) & c); endmodule"]:
        _, opt = synth(src)
        assert tree_map(opt)[1] <= map_to_sky130(opt)[1] + 1e-9
