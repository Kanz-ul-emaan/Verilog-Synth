module top(input x, input y, input a,
           output f, output g, output h, output k);
  assign f = x | (x & y);
  assign g = x & (x | y);
  assign h = a & ~a;
  assign k = (a | ~a) ^ y;
endmodule
