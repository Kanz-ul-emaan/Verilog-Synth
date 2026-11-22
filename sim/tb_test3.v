`timescale 1ns/1ps
module tb;
  reg x, y, a;
  wire f_r, g_r, h_r, k_r, f_n, g_n, h_n, k_n;
  integer i, errors;

  top_rtl rtl (.x(x), .y(y), .a(a), .f(f_r), .g(g_r), .h(h_r), .k(k_r));
  top     net (.x(x), .y(y), .a(a), .f(f_n), .g(g_n), .h(h_n), .k(k_n));

  initial begin
    errors = 0;
    for (i = 0; i < 8; i = i + 1) begin
      {x, y, a} = i[2:0];
      #1;
      if ({f_r,g_r,h_r,k_r} !== {f_n,g_n,h_n,k_n} ||
          f_n !== x || g_n !== x || h_n !== 1'b0 || k_n !== ~y) begin
        $display("MISMATCH x=%b y=%b a=%b: rtl=%b%b%b%b net=%b%b%b%b",
                 x, y, a, f_r, g_r, h_r, k_r, f_n, g_n, h_n, k_n);
        errors = errors + 1;
      end
    end
    if (errors == 0) $display("PASS: all 8 input combinations match");
    else             $display("FAIL: %0d mismatches", errors);
    $finish;
  end
endmodule
