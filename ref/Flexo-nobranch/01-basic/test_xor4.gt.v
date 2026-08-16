module _Z13__weird__xor4bbbbRb(
  input _in1,
  input _in2,
  input _in3,
  input _in4,
  output [7:0] _out
);
  wire _xor16;
  wire _xor817;
  wire _xor1118;
  wire [7:0] _frombool13;

  assign _xor16 = _in1 ^ _in2;
  assign _xor817 = _xor16 ^ _in3;
  assign _xor1118 = _xor817 ^ _in4;
  assign _frombool13[0] = _xor1118;
  assign _frombool13[7:1] = 0;
  assign _out[7:0] = _frombool13;
endmodule
