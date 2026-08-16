module _Z15__weird__adder8PhS_S_S_(
  input [7:0] _in1,
  input [7:0] _in2,
  output [7:0] _out
);
  wire [7:0] __93933722508640;
  wire [7:0] __93933722511648;
  wire [7:0] _add60.narrow;

  assign __93933722508640 = _in1[7:0];
  assign __93933722511648 = _in2[7:0];
  assign _add60.narrow = __93933722511648 + __93933722508640;
  assign _out[7:0] = _add60.narrow;
endmodule
