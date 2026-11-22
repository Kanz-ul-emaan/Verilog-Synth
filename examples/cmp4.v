module top(input a0, input a1, input a2, input a3,
           input b0, input b1, input b2, input b3,
           output eq, output gt, output lt);

  assign eq = ~(a3 ^ b3) & ~(a2 ^ b2) & ~(a1 ^ b1) & ~(a0 ^ b0);

  assign gt = (a3 & ~b3)
            | (~(a3 ^ b3) & a2 & ~b2)
            | (~(a3 ^ b3) & ~(a2 ^ b2) & a1 & ~b1)
            | (~(a3 ^ b3) & ~(a2 ^ b2) & ~(a1 ^ b1) & a0 & ~b0);

  assign lt = ~(gt | eq);
endmodule
