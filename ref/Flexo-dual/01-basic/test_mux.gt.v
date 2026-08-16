module _Z12__weird__muxbbbRb(
  input _in1,
  input _in2,
  input _in3,
  output [7:0] _out
);
  wire _or17;
  wire [7:0] _frombool11;

  assign _or17 = _in3 ? _in2 : _in1;
  assign _frombool11[0] = _or17;
  assign _frombool11[7:1] = 0;
  assign _out[7:0] = _frombool11;
endmodule
