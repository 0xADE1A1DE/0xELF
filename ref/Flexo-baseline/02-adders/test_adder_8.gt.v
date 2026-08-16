module _Z15__weird__adder8PhS_S_S_(
  input [7:0] _in1,
  input [7:0] _in2,
  output [7:0] _out
);
  wire [7:0] __93887128354144;
  wire [7:0] __93887128357152;
  wire [7:0] _add60.narrow;

  assign __93887128354144 = _in1[7:0];
  assign __93887128357152 = _in2[7:0];
  assign _add60.narrow = __93887128357152 + __93887128354144;
  assign _out[7:0] = _add60.narrow;
endmodule
