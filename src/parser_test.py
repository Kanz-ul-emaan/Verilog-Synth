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
    assign_stmt: "assign" NAME "=" expr ";"

    ?expr: expr "&" term   -> and_expr
         | term
    ?term: NAME            -> signal_ref

    NAME: /[a-zA-Z_][a-zA-Z0-9_]*/

    %import common.WS
    %ignore WS
"""

parser = Lark(grammar)

with open("examples/test1.v") as f:

    source = f.read()

tree = parser.parse(source)

print(tree.pretty())
