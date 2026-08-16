module _Z15__weird__adder8PhS_S_S_(
  input [7:0] _in1,
  input [7:0] _in2,
  output [7:0] _out
);
  wire [7:0] __94572783803760;
  wire [7:0] __94572783806768;
  wire [7:0] _add60.narrow;

  assign __94572783803760 = _in1[7:0];
  assign __94572783806768 = _in2[7:0];
  assign _add60.narrow = __94572783806768 + __94572783803760;
  assign _out[7:0] = _add60.narrow;
endmodule
