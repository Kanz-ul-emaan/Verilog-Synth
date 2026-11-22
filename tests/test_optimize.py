from helpers import synth, equivalent


def opt_cells(body, ports="input x, input y, input a, output f"):
    raw, opt = synth(f"module top({ports}); {body} endmodule")
    return raw, opt


def types(n):
    return [c.type for c in n.cells]


def test_cse_merges_duplicates():
    raw, opt = opt_cells("assign f = (x & y) | (x & y);", "input x, input y, output f")
    assert len(opt.cells) < len(raw.cells)


def test_double_negation():
    raw, opt = opt_cells("assign f = ~~x;", "input x, output f")
    assert "NOT" not in types(opt)


def test_idempotence():
    raw, opt = opt_cells("assign f = x & x;", "input x, output f")
    assert types(opt) == ["BUF"]


def test_absorption_or():
    raw, opt = opt_cells("assign f = x | (x & y);", "input x, input y, output f")
    assert types(opt) == ["BUF"]



def test_absorption_and():
    raw, opt = opt_cells("assign f = x & (x | y);", "input x, input y, output f")
    assert types(opt) == ["BUF"]


def test_complement_and_is_zero():
    raw, opt = opt_cells("assign f = a & ~a;", "input a, output f")
    assert types(opt) == ["TIE0"]


def test_complement_or_is_one():
    raw, opt = opt_cells("assign f = a | ~a;", "input a, output f")
    assert types(opt) == ["TIE1"]


def test_constant_xor_becomes_not():
    raw, opt = opt_cells("assign f = (a | ~a) ^ y;", "input a, input y, output f")
    assert types(opt) == ["NOT"]


def test_dead_gates_removed():
    raw, opt = opt_cells("wire w; assign w = x & y; assign f = x;", "input x, input y, output f")
    assert "AND" not in types(opt)


def test_optimizer_preserves_function():
    for body in ["assign f = (x & y) | (x & ~y);",
                 "assign f = x ^ y ^ x;",
                 "assign f = ~(x & y) | (x ^ y);"]:
        raw, opt = opt_cells(body, "input x, input y, output f")
        assert equivalent(raw, opt)
