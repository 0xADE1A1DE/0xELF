module _Z12__weird__notbRb(
  input _in1,
  output [7:0] _out
);
  wire _lnot;
  wire [7:0] _frombool1;

  assign _lnot = _in1 ^ 1;
  assign _frombool1[0] = _lnot;
  assign _frombool1[7:1] = 0;
  assign _out[7:0] = _frombool1;
endmodule
