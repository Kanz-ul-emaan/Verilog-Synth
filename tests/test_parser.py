import pytest
from lark.exceptions import UnexpectedCharacters, UnexpectedToken
from parser import parser


def expr_tree(expr):
    src = f"module top(input a, input b, input c, output y); assign y = {expr}; endmodule"
    return parser.parse(src).children[0].children[2].children[0].children[1]


def test_and_binds_tighter_than_or():
    assert expr_tree("a | b & c").data == "or_op"


def test_parentheses_override_precedence():
    assert expr_tree("(a | b) & c").data == "and_op"


def test_xor_between_and_and_or():
    assert expr_tree("a | b ^ c").data == "or_op"
    assert expr_tree("a ^ b & c").data == "xor_op"


def test_not_binds_tightest():
    t = expr_tree("~a & b")
    assert t.data == "and_op" and t.children[0].data == "not_op"


def test_wire_declaration_parses():
    parser.parse("module top(input a, output y); wire w; assign w = a; assign y = w; endmodule")



@pytest.mark.parametrize("op", ["&&", "||"])
def test_logical_operators_rejected(op):
    src = f"module top(input a, input b, output y); assign y = a {op} b; endmodule"
    with pytest.raises((UnexpectedCharacters, UnexpectedToken)):
        parser.parse(src)
