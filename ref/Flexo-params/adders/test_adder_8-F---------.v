module _Z15__weird__adder8PhS_S_S_(
  input [7:0] _in1,
  input [7:0] _in2,
  output [7:0] _out
);
  wire [7:0] __94301331357040;
  wire [7:0] __94301331360048;
  wire [7:0] _add60.narrow;

  assign __94301331357040 = _in1[7:0];
  assign __94301331360048 = _in2[7:0];
  assign _add60.narrow = __94301331360048 + __94301331357040;
  assign _out[7:0] = _add60.narrow;
endmodule
