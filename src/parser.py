# SCOPE NOTE:
# This synthesizer supports only the bitwise operator family used in
# structural combinational RTL: & (AND), | (OR), ^ (XOR), ~ (NOT).
# Logical operators (&&, ||, !) are intentionally NOT supported, since
# they require boolean reduction semantics rather than direct, bit-per-bit
# gate mapping, and are not used in synthesizable structural logic.

from lark import Lark

# A minimal grammar that understands JUST enough Verilog
# to parse: module top(input a, input b, output y);
#             assign y = a & b;
#           endmodule
grammar = r"""
    start: module

    module: "module" NAME "(" port_list ")" ";" stmt* "endmodule"

    port_list: port ("," port)*
    port: direction NAME
    direction: "input" -> input_dir
             | "output" -> output_dir

    stmt: assign_stmt
    assign_stmt: "assign" NAME "=" or_expr ";"

    ?or_expr: or_expr "|" xor_expr    -> or_op
            | xor_expr

    ?xor_expr: xor_expr "^" and_expr  -> xor_op
             | and_expr

    ?and_expr: and_expr "&" unary_expr -> and_op
             | unary_expr

    ?unary_expr: "~" unary_expr  -> not_op
               | atom

    ?atom: NAME        -> signal_ref
         | "(" or_expr ")"

    NAME: /[a-zA-Z_][a-zA-Z0-9_]*/

    %import common.WS
    %ignore WS
"""

parser = Lark(grammar)

with open("examples/test1.v") as f:

    source = f.read()
from lark.exceptions import UnexpectedCharacters, UnexpectedToken

try:
    tree = parser.parse(source)
except (UnexpectedCharacters, UnexpectedToken) as e:
    print("ERROR: Could not parse this Verilog file.")
    print("This synthesizer supports only bitwise operators (&, |, ^, ~).")
    print(f"Parser details: {e}")
    exit(1)

print(tree.pretty())
