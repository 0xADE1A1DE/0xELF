module _Z15__weird__adder8PhS_S_S_(
  input [7:0] _in1,
  input [7:0] _in2,
  output [7:0] _out
);
  wire [7:0] __93913430867312;
  wire [7:0] __93913430870320;
  wire [7:0] _add60.narrow;

  assign __93913430867312 = _in1[7:0];
  assign __93913430870320 = _in2[7:0];
  assign _add60.narrow = __93913430870320 + __93913430867312;
  assign _out[7:0] = _add60.narrow;
endmodule
