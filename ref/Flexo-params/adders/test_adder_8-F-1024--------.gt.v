module _Z15__weird__adder8PhS_S_S_(
  input [7:0] _in1,
  input [7:0] _in2,
  output [7:0] _out
);
  wire [7:0] __94085243465072;
  wire [7:0] __94085243468080;
  wire [7:0] _add60.narrow;

  assign __94085243465072 = _in1[7:0];
  assign __94085243468080 = _in2[7:0];
  assign _add60.narrow = __94085243468080 + __94085243465072;
  assign _out[7:0] = _add60.narrow;
endmodule
