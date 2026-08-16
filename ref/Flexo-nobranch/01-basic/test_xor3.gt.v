module _Z13__weird__xor3bbbRb(
  input _in1,
  input _in2,
  input _in3,
  output [7:0] _out
);
  wire _xor12;
  wire _xor713;
  wire [7:0] _frombool9;

  assign _xor12 = _in1 ^ _in2;
  assign _xor713 = _xor12 ^ _in3;
  assign _frombool9[0] = _xor713;
  assign _frombool9[7:1] = 0;
  assign _out[7:0] = _frombool9;
endmodule
