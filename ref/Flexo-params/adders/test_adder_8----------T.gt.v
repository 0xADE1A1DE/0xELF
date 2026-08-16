module _Z15__weird__adder8PhS_S_S_(
  input [7:0] _in1,
  input [7:0] _in2,
  output [7:0] _out
);
  wire [7:0] __94750340644208;
  wire [7:0] __94750340647216;
  wire [7:0] _add60.narrow;

  assign __94750340644208 = _in1[7:0];
  assign __94750340647216 = _in2[7:0];
  assign _add60.narrow = __94750340647216 + __94750340644208;
  assign _out[7:0] = _add60.narrow;
endmodule
