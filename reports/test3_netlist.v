module top(x, y, a, f, g, h, k);
  input x;
  input y;
  input a;
  output f;
  output g;
  output h;
  output k;

  sky130_fd_sc_hd__conb_1 u0 (.LO(h));
  sky130_fd_sc_hd__buf_1 u1 (.A(x), .X(f));
  sky130_fd_sc_hd__buf_1 u2 (.A(x), .X(g));
  sky130_fd_sc_hd__inv_1 u3 (.A(y), .Y(k));
endmodule
