module _Z12__weird__xorbbRb(
  input _in1,
  input _in2,
  output [7:0] _out
);
  wire _xor8;
  wire [7:0] _frombool5;

  assign _xor8 = _in1 ^ _in2;
  assign _frombool5[0] = _xor8;
  assign _frombool5[7:1] = 0;
  assign _out[7:0] = _frombool5;
endmodule
