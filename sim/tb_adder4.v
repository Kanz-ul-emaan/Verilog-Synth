`timescale 1ns/1ps
module tb;
  reg [3:0] a, b;
  reg cin;
  wire [3:0] s_r, s_n;
  wire co_r, co_n;
  reg [4:0] expected;
  integer i, errors;

  top_rtl rtl (.a0(a[0]), .a1(a[1]), .a2(a[2]), .a3(a[3]),
               .b0(b[0]), .b1(b[1]), .b2(b[2]), .b3(b[3]), .cin(cin),
               .s0(s_r[0]), .s1(s_r[1]), .s2(s_r[2]), .s3(s_r[3]), .cout(co_r));
  top     net (.a0(a[0]), .a1(a[1]), .a2(a[2]), .a3(a[3]),
               .b0(b[0]), .b1(b[1]), .b2(b[2]), .b3(b[3]), .cin(cin),
               .s0(s_n[0]), .s1(s_n[1]), .s2(s_n[2]), .s3(s_n[3]), .cout(co_n));

  initial begin
    errors = 0;
    for (i = 0; i < 512; i = i + 1) begin
      {cin, a, b} = i[8:0];
      expected = a + b + cin;
      #1;
      if ({co_r, s_r} !== {co_n, s_n} || {co_n, s_n} !== expected) begin
        $display("MISMATCH a=%d b=%d cin=%b: rtl=%b net=%b expected=%b",
                 a, b, cin, {co_r, s_r}, {co_n, s_n}, expected);
        errors = errors + 1;
      end
    end
    if (errors == 0) $display("PASS: all 512 input combinations match");
    else             $display("FAIL: %0d mismatches", errors);
    $finish;
  end

endmodule
