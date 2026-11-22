`timescale 1ns/1ps
module tb;
  reg [3:0] a, b;
  wire eq_r, gt_r, lt_r;
  wire eq_n, gt_n, lt_n;
  integer i, errors;

  top_rtl rtl (.a0(a[0]), .a1(a[1]), .a2(a[2]), .a3(a[3]),
               .b0(b[0]), .b1(b[1]), .b2(b[2]), .b3(b[3]),
               .eq(eq_r), .gt(gt_r), .lt(lt_r));
  top     net (.a0(a[0]), .a1(a[1]), .a2(a[2]), .a3(a[3]),
               .b0(b[0]), .b1(b[1]), .b2(b[2]), .b3(b[3]),
               .eq(eq_n), .gt(gt_n), .lt(lt_n));

  initial begin
    errors = 0;
    for (i = 0; i < 256; i = i + 1) begin
      {a, b} = i[7:0];
      #1;
      if ({eq_r, gt_r, lt_r} !== {eq_n, gt_n, lt_n} ||
          eq_n !== (a == b) || gt_n !== (a > b) || lt_n !== (a < b)) begin
        $display("MISMATCH a=%d b=%d: rtl=%b%b%b net=%b%b%b",
                 a, b, eq_r, gt_r, lt_r, eq_n, gt_n, lt_n);
        errors = errors + 1;
      end
    end
    if (errors == 0) $display("PASS: all 256 input combinations match");
    else             $display("FAIL: %0d mismatches", errors);
    $finish;
  end
endmodule
