import pytest
from parser import parser
from elaborate import elaborate, ElaborationError


def run(body, ports="input a, input b, output y"):
    return elaborate(parser.parse(f"module top({ports}); {body} endmodule"))


def test_valid_design():
    m = run("assign y = a & b;")
    assert set(m.signals) == {"a", "b", "y"}


def test_undeclared_signal_in_expression():
    with pytest.raises(ElaborationError, match="never declared"):
        run("assign y = a & zz;")


def test_undeclared_target():
    with pytest.raises(ElaborationError):
        run("assign q = a & b;")


def test_multiple_drivers():
    with pytest.raises(ElaborationError, match="more than one"):
        run("assign y = a; assign y = b;")


def test_assigning_an_input():
    with pytest.raises(ElaborationError, match="cannot be assigned"):
        run("assign a = b; assign y = a;")



def test_duplicate_port():
    with pytest.raises(ElaborationError, match="more than once"):
        run("assign y = a;", ports="input a, input a, output y")


def test_wire_redeclared():
    with pytest.raises(ElaborationError, match="more than once"):
        run("wire w; wire w; assign w = a; assign y = w;")
