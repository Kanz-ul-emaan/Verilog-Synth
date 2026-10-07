module top(input a, input b, input c, output f1, output f2);
  assign f1 = a & b;
  assign f2 = (a & b) | c;
endmodule
