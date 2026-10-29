module top_rtl(input a0, input a1, input a2, input a3,
           input b0, input b1, input b2, input b3,
           input cin,
           output s0, output s1, output s2, output s3, output cout);
  wire p0, p1, p2, p3, c1, c2, c3;

  assign p0 = a0 ^ b0;
  assign p1 = a1 ^ b1;
  assign p2 = a2 ^ b2;
  assign p3 = a3 ^ b3;

  assign s0 = p0 ^ cin;
  assign c1 = (a0 & b0) | (cin & p0);
  assign s1 = p1 ^ c1;
  assign c2 = (a1 & b1) | (c1 & p1);
  assign s2 = p2 ^ c2;
  assign c3 = (a2 & b2) | (c2 & p2);
  assign s3 = p3 ^ c3;
  assign cout = (a3 & b3) | (c3 & p3);
endmodule
