`timescale 1ns/1ps
module tb;
  reg a, b, c;
  wire f1_r, f2_r;
  wire f1_n, f2_n;
  integer i, errors;

  top_rtl rtl (.a(a), .b(b), .c(c), .f1(f1_r), .f2(f2_r));
  top     net (.a(a), .b(b), .c(c), .f1(f1_n), .f2(f2_n));

  initial begin
    errors = 0;
    for (i = 0; i < 8; i = i + 1) begin
      {a, b, c} = i[2:0];
      #1;
      if (f1_r !== f1_n || f2_r !== f2_n) begin
        $display("MISMATCH at abc=%b: rtl=%b%b net=%b%b",
                 {a,b,c}, f1_r, f2_r, f1_n, f2_n);
        errors = errors + 1;
      end
    end
    if (errors == 0) $display("PASS: all 8 input combinations match");
    else             $display("FAIL: %0d mismatches", errors);
    $finish;
  end
endmodule
