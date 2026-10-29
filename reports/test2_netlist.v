module top(a, b, c, f1, f2);
  input a;
  input b;
  input c;
  output f1;
  output f2;

  sky130_fd_sc_hd__and2_1 u0 (.A(a), .B(b), .X(f1));
  sky130_fd_sc_hd__or2_1 u1 (.A(f1), .B(c), .X(f2));
endmodule
